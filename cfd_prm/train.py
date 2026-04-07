"""
Training script for CFD-PRM

Supports single-GPU and multi-GPU training with checkpointing.
"""

import os
import sys
import json
import math
import time
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("Warning: wandb not installed. Logging to file only.")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cfd_prm.models.step_scorer import StepScorer
from cfd_prm.data.dataset import create_dataloader
from cfd_prm.losses.checkpoint_first_divergence import CheckpointFirstDivergenceLoss
from cfd_prm.losses.calibration_loss import CalibrationLoss


def setup_logging(output_dir: str, rank: int = 0) -> logging.Logger:
    """Setup logging for training."""
    log_file = Path(output_dir) / f"training_rank{rank}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s [Rank {rank}] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_config(args) -> Dict:
    """Load or create training config."""
    config = {
        "model_name": "Qwen/Qwen2.5-VL-7B-Instruct",
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "freeze_vision": args.freeze_vision,
        "data_dir": args.data_dir,
        "output_dir": args.output_dir,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "lambda_calib": args.lambda_calib,
        "lambda_cfd": args.lambda_cfd,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "max_grad_norm": args.max_grad_norm,
        "checkpoint_every": args.checkpoint_every,
        "eval_every": args.eval_every,
        "seed": args.seed,
    }
    return config


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    epoch: int,
    step: int,
    output_dir: str,
    is_best: bool = False,
):
    """Save training checkpoint."""
    checkpoint_dir = Path(output_dir) / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    checkpoint_path = checkpoint_dir / f"checkpoint_epoch{epoch}_step{step}"
    model.save_pretrained(str(checkpoint_path))

    # Save optimizer and scheduler
    torch.save(
        {
            "epoch": epoch,
            "step": step,
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
        },
        checkpoint_path / "training_state.pt",
    )

    # Save as best if needed
    if is_best:
        best_path = checkpoint_dir / "best"
        best_path.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(str(best_path))
        torch.save(
            {
                "epoch": epoch,
                "step": step,
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
            },
            best_path / "training_state.pt",
        )


def load_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    checkpoint_path: str,
) -> Tuple[int, int]:
    """Load training checkpoint."""
    # Load model weights
    model.load_pretrained(checkpoint_path)

    # Load training state
    training_state = torch.load(Path(checkpoint_path) / "training_state.pt")
    optimizer.load_state_dict(training_state["optimizer_state_dict"])
    scheduler.load_state_dict(training_state["scheduler_state_dict"])

    return training_state["epoch"], training_state["step"]


def train_epoch(
    model: StepScorer,
    dataloader: DataLoader,
    optimizer: AdamW,
    scheduler: CosineAnnealingLR,
    cfd_loss: CheckpointFirstDivergenceLoss,
    calib_loss: CalibrationLoss,
    epoch: int,
    config: Dict,
    logger: logging.Logger,
    writer=None,
    rank: int = 0,
    gradient_scaler: Optional[torch.cuda.amp.GradScaler] = None,
) -> Dict:
    """Train for one epoch."""
    model.train()

    total_loss = 0.0
    total_cfd_loss = 0.0
    total_calib_loss = 0.0
    num_batches = len(dataloader)

    use_amp = gradient_scaler is not None
    accumulation_steps = config["gradient_accumulation_steps"]

    optimizer.zero_grad()

    for batch_idx, batch in enumerate(dataloader):
        # Move data to device
        input_ids = batch["input_ids"].to(rank)
        attention_mask = batch["attention_mask"].to(rank)
        pixel_values = batch["pixel_values"].to(rank) if batch["pixel_values"] is not None else None
        image_grid_thw = batch["image_grid_thw"].to(rank) if batch["image_grid_thw"] is not None else None
        labels = batch["labels"].to(rank)

        # Forward pass
        if use_amp:
            with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                scores = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    pixel_values=pixel_values,
                    image_grid_thw=image_grid_thw,
                )

                # Compute losses
                # Reshape scores to [batch_size//2, 2, ...] for pairwise loss
                batch_size = scores.shape[0]
                scores_pairwise = scores.view(batch_size // 2, 2)
                labels_pairwise = labels.view(batch_size // 2, 2)

                # Extract t* (first divergence point) - simplified: assume middle of trajectory
                t_star = torch.tensor([scores_pairwise.shape[1] // 2] * (batch_size // 2), device=rank)

                loss_cfd = cfd_loss(scores_pairwise, t_star, labels_pairwise)
                loss_calib = calib_loss(scores, labels)

                loss = config["lambda_cfd"] * loss_cfd + config["lambda_calib"] * loss_calib
                loss = loss / accumulation_steps

            # Backward pass with gradient scaling
            gradient_scaler.scale(loss).backward()

            # Optimizer step
            if (batch_idx + 1) % accumulation_steps == 0:
                gradient_scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"])
                gradient_scaler.step(optimizer)
                gradient_scaler.update()
                scheduler.step()
                optimizer.zero_grad()
        else:
            scores = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                pixel_values=pixel_values,
                image_grid_thw=image_grid_thw,
            )

            # Compute losses
            batch_size = scores.shape[0]
            scores_pairwise = scores.view(batch_size // 2, 2)
            labels_pairwise = labels.view(batch_size // 2, 2)

            t_star = torch.tensor([scores_pairwise.shape[1] // 2] * (batch_size // 2), device=rank)

            loss_cfd = cfd_loss(scores_pairwise, t_star, labels_pairwise)
            loss_calib = calib_loss(scores, labels)

            loss = config["lambda_cfd"] * loss_cfd + config["lambda_calib"] * loss_calib
            loss = loss / accumulation_steps

            loss.backward()

            if (batch_idx + 1) % accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"])
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        # Accumulate metrics
        total_loss += loss.item() * accumulation_steps
        total_cfd_loss += loss_cfd.item()
        total_calib_loss += loss_calib.item()

        # Log progress
        if (batch_idx + 1) % config["checkpoint_every"] == 0:
            avg_loss = total_loss / (batch_idx + 1)
            avg_cfd_loss = total_cfd_loss / (batch_idx + 1)
            avg_calib_loss = total_calib_loss / (batch_idx + 1)
            current_lr = scheduler.get_last_lr()[0]

            logger.info(
                f"Epoch {epoch} | Batch {batch_idx + 1}/{num_batches} | "
                f"Loss: {avg_loss:.4f} | CFD: {avg_cfd_loss:.4f} | Calib: {avg_calib_loss:.4f} | "
                f"LR: {current_lr:.6f}"
            )

            if WANDB_AVAILABLE and writer is not None and rank == 0:
                writer.log(
                    {
                        "train/loss": avg_loss,
                        "train/cfd_loss": avg_cfd_loss,
                        "train/calib_loss": avg_calib_loss,
                        "train/lr": current_lr,
                    },
                    step=epoch * num_batches + batch_idx,
                )

    # End of epoch metrics
    metrics = {
        "epoch_loss": total_loss / num_batches,
        "epoch_cfd_loss": total_cfd_loss / num_batches,
        "epoch_calib_loss": total_calib_loss / num_batches,
    }

    return metrics


def train(
    config: Dict,
    local_rank: int = 0,
    world_size: int = 1,
):
    """Main training loop."""
    # Setup
    set_seed(config["seed"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(str(output_dir), rank=local_rank)
    logger.info(f"Starting CFD-PRM training")
    logger.info(f"Config: {json.dumps(config, indent=2)}")

    # Initialize wandb
    writer = None
    if WANDB_AVAILABLE and local_rank == 0:
        try:
            writer = wandb.init(
                project="cfd-prm",
                config=config,
                name=f"cfd-prm-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            )
            logger.info("Initialized wandb")
        except Exception as e:
            logger.warning(f"Failed to initialize wandb: {e}")

    # Check for distributed training
    is_distributed = world_size > 1
    if is_distributed:
        torch.distributed.init_process_group(backend="nccl")
        local_rank = int(os.environ.get("LOCAL_RANK", 0))
        torch.cuda.set_device(local_rank)
        logger.info(f"Distributed training: {world_size} GPUs")

    # Create model
    logger.info("Creating StepScorer model...")
    model = StepScorer(
        model_name=config["model_name"],
        lora_r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        freeze_vision=config["freeze_vision"],
    )

    # Move model to device
    if is_distributed:
        model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[local_rank],
            find_unused_parameters=True,
        )
    else:
        model = model.to(local_rank)

    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Create dataloader
    data_path = Path(config["data_dir"]) / "hard_negatives.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Data not found at {data_path}")

    logger.info("Creating DataLoader...")
    dataloader = create_dataloader(
        data_path=str(data_path),
        batch_size=config["batch_size"],
        shuffle=True,
        num_workers=4,
        model_name=config["model_name"],
    )

    logger.info(f"Dataset size: {len(dataloader.dataset)} pairs")
    logger.info(f"Batch size: {config['batch_size']}")

    # Create losses
    cfd_loss = CheckpointFirstDivergenceLoss(margin=0.5).to(local_rank)
    calib_loss = CalibrationLoss(margin=0.1, tau=0.5).to(local_rank)

    # Create optimizer and scheduler
    optimizer = AdamW(
        model.parameters(),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"],
        betas=(0.9, 0.95),
    )

    num_training_steps = len(dataloader) * config["epochs"]
    warmup_steps = int(num_training_steps * config["warmup_ratio"])

    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=num_training_steps - warmup_steps,
        eta_min=config["learning_rate"] * 0.1,
    )

    # Gradient scaler for AMP
    gradient_scaler = torch.cuda.amp.GradScaler()

    # Optional: resume from checkpoint
    start_epoch = 0
    start_step = 0
    checkpoint_dir = output_dir / "checkpoints"
    # TODO: Add checkpoint resumption logic

    # Training loop
    logger.info("Starting training loop...")
    best_loss = float("inf")

    for epoch in range(start_epoch, config["epochs"]):
        logger.info(f"Epoch {epoch + 1}/{config['epochs']}")
        start_time = time.time()

        metrics = train_epoch(
            model=model,
            dataloader=dataloader,
            optimizer=optimizer,
            scheduler=scheduler,
            cfd_loss=cfd_loss,
            calib_loss=calib_loss,
            epoch=epoch,
            config=config,
            logger=logger,
            writer=writer,
            rank=local_rank,
            gradient_scaler=gradient_scaler,
        )

        epoch_time = time.time() - start_time
        logger.info(
            f"Epoch {epoch + 1} complete | "
            f"Loss: {metrics['epoch_loss']:.4f} | "
            f"CFD: {metrics['epoch_cfd_loss']:.4f} | "
            f"Calib: {metrics['epoch_calib_loss']:.4f} | "
            f"Time: {epoch_time:.1f}s"
        )

        if WANDB_AVAILABLE and writer is not None and local_rank == 0:
            writer.log(
                {
                    "epoch/loss": metrics["epoch_loss"],
                    "epoch/cfd_loss": metrics["epoch_cfd_loss"],
                    "epoch/calib_loss": metrics["epoch_calib_loss"],
                    "epoch/time": epoch_time,
                },
                step=(epoch + 1) * len(dataloader),
            )

        # Save checkpoint
        is_best = metrics["epoch_loss"] < best_loss
        if is_best:
            best_loss = metrics["epoch_loss"]

        if (epoch + 1) % config["checkpoint_every"] == 0 or is_best:
            save_checkpoint(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                step=0,
                output_dir=str(output_dir),
                is_best=is_best,
            )
            logger.info(f"Saved checkpoint (best: {is_best})")

    # End of training
    logger.info("Training complete!")
    logger.info(f"Best loss: {best_loss:.4f}")

    # Save final model
    final_dir = output_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    model.module.save_pretrained(str(final_dir)) if is_distributed else model.save_pretrained(str(final_dir))
    logger.info(f"Saved final model to {final_dir}")

    if WANDB_AVAILABLE and writer is not None:
        writer.finish()


def main():
    parser = argparse.ArgumentParser(description="Train CFD-PRM")

    # Model config
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-VL-7B-Instruct")
    parser.add_argument("--lora_r", type=int, default=64)
    parser.add_argument("--lora_alpha", type=float, default=128)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    parser.add_argument("--freeze_vision", action="store_true")

    # Data
    parser.add_argument("--data_dir", type=str, required=True)

    # Output
    parser.add_argument("--output_dir", type=str, required=True)

    # Training hyperparameters
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--lambda_calib", type=float, default=0.1)
    parser.add_argument("--lambda_cfd", type=float, default=1.0)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1)
    parser.add_argument("--max_grad_norm", type=float, default=1.0)

    # Checkpointing
    parser.add_argument("--checkpoint_every", type=int, default=1)
    parser.add_argument("--eval_every", type=int, default=1)

    # Misc
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--local_rank", type=int, default=-1)

    args = parser.parse_args()

    # Check for distributed training
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = args.local_rank if args.local_rank >= 0 else 0

    if world_size > 1:
        local_rank = int(os.environ.get("LOCAL_RANK", 0))

    # Load config
    config = load_config(args)

    # Start training
    train(config, local_rank=local_rank, world_size=world_size)


if __name__ == "__main__":
    main()
