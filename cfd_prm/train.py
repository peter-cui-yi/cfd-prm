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
from torch.amp import GradScaler, autocast

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cfd_prm.models.step_scorer import StepScorer
from cfd_prm.data.dataset import create_dataloader, StepLevelCFDPRMDataset, step_level_collate_fn
from cfd_prm.losses.checkpoint_first_divergence import CheckpointFirstDivergenceLoss
from cfd_prm.losses.calibration_loss import CalibrationLoss
from transformers import AutoProcessor


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
        "model_name": args.model_name,
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "freeze_vision": args.freeze_vision,
        "data_dir": args.data_dir,
        "max_pairs": args.max_pairs,
        "t_star_mode": args.t_star_mode,
        "output_dir": args.output_dir,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "lambda_calib": args.lambda_calib,
        "lambda_cfd": args.lambda_cfd,
        "lambda_step_bce": args.lambda_step_bce,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "max_grad_norm": args.max_grad_norm,
        "cfd_margin": args.cfd_margin,
        "loss_type": args.loss_type,
        "pairwise_margin": args.pairwise_margin,
        "boundary_weight": args.boundary_weight,
        "checkpoint_every": args.checkpoint_every,
        "eval_every": args.eval_every,
        "seed": args.seed,
        "step_level": args.step_level,
        "pooling": args.pooling,
        "max_length": args.max_length,
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

    # Save model - unwrap from DDP if needed
    model_to_save = model.module if hasattr(model, 'module') else model
    
    # Save StepScorer's components directly
    checkpoint_path = checkpoint_dir / f"checkpoint_epoch{epoch}_step{step}"
    checkpoint_path.mkdir(parents=True, exist_ok=True)
    
    # Save PEFT adapter from base_model
    if hasattr(model_to_save, 'base_model'):
        model_to_save.base_model.save_pretrained(str(checkpoint_path))
    
    # Save score_head separately
    if hasattr(model_to_save, 'score_head'):
        torch.save(model_to_save.score_head.state_dict(), checkpoint_path / "score_head.pt")

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
        model_to_save.base_model.save_pretrained(str(best_path))
        if hasattr(model_to_save, 'score_head'):
            torch.save(model_to_save.score_head.state_dict(), best_path / "score_head.pt")
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


def compute_t_star(
    scores_pairwise: torch.FloatTensor,  # [n_pairs, 2]
    t_star_mode: str = "true",
    device: int = 0,
) -> torch.LongTensor:
    """
    Compute t_star indices based on mode.

    For the pairwise setup ([n_pairs, 2] where col 0 = ref, col 1 = dev):
      - "true":   t*=0 — correct supervision, compare ref vs dev
      - "random":  random t* per pair — noisy supervision
      - "shifted": t*=1 — wrong position, score at dev instead of ref
      - "last":    t*=1 — same as shifted (only 2 positions)
    """
    n_pairs = scores_pairwise.shape[0]
    if t_star_mode == "true":
        return torch.zeros(n_pairs, dtype=torch.long, device=device)
    elif t_star_mode == "random":
        return torch.randint(0, 2, (n_pairs,), dtype=torch.long, device=device)
    elif t_star_mode == "shifted":
        return torch.ones(n_pairs, dtype=torch.long, device=device)
    elif t_star_mode == "last":
        return torch.ones(n_pairs, dtype=torch.long, device=device)
    else:
        return torch.zeros(n_pairs, dtype=torch.long, device=device)


def train_epoch_step_level(
    model: StepScorer,
    dataloader: DataLoader,
    optimizer: AdamW,
    scheduler: CosineAnnealingLR,
    cfd_loss,
    calib_loss,
    epoch: int,
    config: Dict,
    logger: logging.Logger,
    writer=None,
    rank: int = 0,
    gradient_scaler: Optional[GradScaler] = None,
    is_distributed: bool = False,
) -> Dict:
    """Train for one epoch in step-level mode."""
    model.train()

    total_loss = 0.0
    total_cfd_loss = 0.0
    total_step_bce_loss = 0.0
    total_calib_loss = 0.0
    num_batches = len(dataloader)

    use_amp = gradient_scaler is not None
    accumulation_steps = config["gradient_accumulation_steps"]
    loss_type = config.get("loss_type", "cfd")

    optimizer.zero_grad()

    log_interval = max(1, num_batches // 100)

    for batch_idx, batch in enumerate(dataloader):
        input_ids = batch["input_ids"].to(rank)
        attention_mask = batch["attention_mask"].to(rank)
        metadata = batch["metadata"]
        # Move metadata tensors to device
        metadata = {k: v.to(rank) for k, v in metadata.items()}

        # Use no_sync during gradient accumulation to avoid premature DDP all-reduce
        should_sync = (batch_idx + 1) % accumulation_steps == 0
        if is_distributed and not should_sync:
            context = model.no_sync
        else:
            from contextlib import nullcontext
            context = nullcontext

        with context():
            if use_amp:
                with autocast('cuda', dtype=torch.bfloat16):
                    scores = model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                    )

                    if batch_idx == 0 and epoch == 0:
                        logger.info(f"DEBUG: scores min={scores.min().item():.4f}, max={scores.max().item():.4f}, std={scores.std().item():.4f}, n_steps={scores.shape[0]}")

                    # Debug score distribution
                    if batch_idx % log_interval == 0:
                        logger.info(
                            f"DEBUG batch {batch_idx}: "
                            f"score_mean={scores.mean().item():.4f} score_std={scores.std().item():.4f}"
                        )

                    if loss_type == "cfd":
                        loss_cfd, loss_step_bce = cfd_loss.forward_step_level(
                            scores, metadata, loss_type="cfd"
                        )
                        loss_calib = torch.tensor(0.0, device=rank)
                    elif loss_type == "all_wrong_ranking":
                        loss_cfd, loss_step_bce = cfd_loss.forward_step_level(
                            scores, metadata, loss_type="all_wrong_ranking"
                        )
                        loss_calib = torch.tensor(0.0, device=rank)
                    elif loss_type == "boundary_bce":
                        boundary_weight = config.get("boundary_weight", 5.0)
                        t_star = metadata["t_star"]
                        step_idx = metadata["step_idx"]
                        weights = torch.ones_like(scores)
                        near_boundary = (step_idx - t_star).abs() <= 1
                        weights[near_boundary] = boundary_weight
                        bce_per_step = F.binary_cross_entropy(scores.float(), metadata["labels"].float(), reduction="none")
                        loss_cfd = (weights * bce_per_step).sum() / weights.sum()
                        loss_calib = torch.tensor(0.0, device=rank)
                        loss_step_bce = loss_cfd
                    elif loss_type == "pairwise":
                        ref_mask = metadata["labels"] == 1
                        dev_mask = metadata["labels"] == 0
                        if ref_mask.any() and dev_mask.any():
                            ref_s = scores[ref_mask].mean()
                            dev_s = scores[dev_mask].mean()
                            target = torch.ones(1, device=rank)
                            loss_cfd = nn.functional.margin_ranking_loss(ref_s.unsqueeze(0), dev_s.unsqueeze(0), target, margin=config.get("pairwise_margin", 0.5))
                        else:
                            loss_cfd = torch.tensor(0.0, device=rank)
                        loss_calib = torch.tensor(0.0, device=rank)
                    elif loss_type == "pointwise":
                        loss_cfd = F.binary_cross_entropy(scores.float(), metadata["labels"].float())
                        loss_calib = torch.tensor(0.0, device=rank)
                        loss_step_bce = torch.tensor(0.0, device=rank)

                loss = loss_cfd + config.get("lambda_step_bce", 1.0) * loss_step_bce + config.get("lambda_calib", 0.0) * loss_calib
                loss = loss / accumulation_steps
                gradient_scaler.scale(loss).backward()

                if should_sync:
                    gradient_scaler.unscale_(optimizer)
                    if batch_idx % log_interval == 0:
                        total_norm = 0.0
                        for p in model.parameters():
                            if p.grad is not None:
                                total_norm += p.grad.data.norm(2).item() ** 2
                        total_norm = total_norm ** 0.5
                        logger.info(f"DEBUG: grad_norm={total_norm:.4f}, max_grad_norm={config['max_grad_norm']}")
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"])
                    gradient_scaler.step(optimizer)
                    gradient_scaler.update()
                    scheduler.step()
                    optimizer.zero_grad()
            else:
                scores = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )

                if loss_type == "cfd":
                    t_star_mode = config.get("t_star_mode", "true")
                    loss_metadata = metadata
                    if t_star_mode != "true":
                        loss_metadata = dict(metadata)
                        n_pairs = int(metadata["global_pair_idx"].max().item()) + 1
                        if t_star_mode == "random":
                            # Random t* per pair: uniform in [0, 20), representative of trajectory length
                            random_t_star = torch.randint(0, 20, (n_pairs,), device=rank)
                            # Expand to per-step shape
                            loss_metadata["t_star"] = random_t_star[metadata["global_pair_idx"]]
                        elif t_star_mode == "shifted":
                            loss_metadata["t_star"] = metadata["t_star"] + 2
                    loss_cfd, loss_step_bce = cfd_loss.forward_step_level(
                        scores, loss_metadata, loss_type="cfd"
                    )
                    loss_calib = torch.tensor(0.0, device=rank)
                elif loss_type == "all_wrong_ranking":
                    loss_cfd, loss_step_bce = cfd_loss.forward_step_level(
                        scores, metadata, loss_type="all_wrong_ranking"
                    )
                    loss_calib = torch.tensor(0.0, device=rank)
                elif loss_type == "boundary_bce":
                    # BCE with upweighted loss for steps near t* (boundary)
                    boundary_weight = config.get("boundary_weight", 5.0)
                    t_star = metadata["t_star"]
                    step_idx = metadata["step_idx"]
                    # Weight = boundary_weight if |step_idx - t_star| <= 1, else 1.0
                    weights = torch.ones_like(scores)
                    near_boundary = (step_idx - t_star).abs() <= 1
                    weights[near_boundary] = boundary_weight
                    # Weighted BCE
                    bce_per_step = F.binary_cross_entropy(scores.float(), metadata["labels"].float(), reduction="none")
                    loss_cfd = (weights * bce_per_step).sum() / weights.sum()
                    loss_calib = torch.tensor(0.0, device=rank)
                    loss_step_bce = loss_cfd  # reuse for logging
                elif loss_type == "pairwise":
                    ref_mask = metadata["labels"] == 1
                    dev_mask = metadata["labels"] == 0
                    if ref_mask.any() and dev_mask.any():
                        ref_s = scores[ref_mask].mean()
                        dev_s = scores[dev_mask].mean()
                        target = torch.ones(1, device=rank)
                        loss_cfd = nn.functional.margin_ranking_loss(ref_s.unsqueeze(0), dev_s.unsqueeze(0), target, margin=config.get("pairwise_margin", 0.5))
                    else:
                        loss_cfd = torch.tensor(0.0, device=rank)
                    loss_calib = torch.tensor(0.0, device=rank)
                elif loss_type == "pointwise":
                    loss_cfd = F.binary_cross_entropy(scores.float(), metadata["labels"].float())
                    loss_calib = torch.tensor(0.0, device=rank)
                    loss_step_bce = torch.tensor(0.0, device=rank)

                loss = loss_cfd + config.get("lambda_step_bce", 1.0) * loss_step_bce + config.get("lambda_calib", 0.0) * loss_calib
                loss = loss / accumulation_steps
                loss.backward()

                if should_sync:
                    if batch_idx % log_interval == 0:
                        total_norm = 0.0
                        for p in model.parameters():
                            if p.grad is not None:
                                total_norm += p.grad.data.norm(2).item() ** 2
                        total_norm = total_norm ** 0.5
                        logger.info(f"DEBUG: grad_norm={total_norm:.4f}, max_grad_norm={config['max_grad_norm']}")
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"])
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

        total_loss += loss.item() * accumulation_steps
        total_cfd_loss += loss_cfd.item()
        total_step_bce_loss += loss_step_bce.item()
        total_calib_loss += loss_calib.item()

        if (batch_idx + 1) % log_interval == 0 or (batch_idx + 1) == num_batches:
            avg_loss = total_loss / (batch_idx + 1)
            avg_cfd_loss = total_cfd_loss / (batch_idx + 1)
            avg_step_bce = total_step_bce_loss / (batch_idx + 1)
            avg_calib_loss = total_calib_loss / (batch_idx + 1)
            current_lr = scheduler.get_last_lr()[0]

            logger.info(
                f"Epoch {epoch} | Batch {batch_idx + 1}/{num_batches} | "
                f"Loss: {avg_loss:.4f} | CFD: {avg_cfd_loss:.4f} | BCE: {avg_step_bce:.4f} | Calib: {avg_calib_loss:.4f} | "
                f"LR: {current_lr:.6f}"
            )

            if WANDB_AVAILABLE and writer is not None and rank == 0:
                writer.log(
                    {
                        "train/loss": avg_loss,
                        "train/cfd_loss": avg_cfd_loss,
                        "train/step_bce": avg_step_bce,
                        "train/calib_loss": avg_calib_loss,
                        "train/lr": current_lr,
                    },
                    step=epoch * num_batches + batch_idx,
                )

    metrics = {
        "epoch_loss": total_loss / num_batches,
        "epoch_cfd_loss": total_cfd_loss / num_batches,
        "epoch_step_bce": total_step_bce_loss / num_batches,
        "epoch_calib_loss": total_calib_loss / num_batches,
    }

    return metrics


def train_epoch(
    model: StepScorer,
    dataloader: DataLoader,
    optimizer: AdamW,
    scheduler: CosineAnnealingLR,
    cfd_loss,  # Can be CFD loss, MarginRankingLoss, or None
    calib_loss,  # Can be CalibrationLoss or None
    epoch: int,
    config: Dict,
    logger: logging.Logger,
    writer=None,
    rank: int = 0,
    gradient_scaler: Optional[GradScaler] = None,
    is_distributed: bool = False,
) -> Dict:
    """Train for one epoch."""
    model.train()

    total_loss = 0.0
    total_cfd_loss = 0.0
    total_calib_loss = 0.0
    num_batches = len(dataloader)

    use_amp = gradient_scaler is not None
    accumulation_steps = config["gradient_accumulation_steps"]
    loss_type = config.get("loss_type", "cfd")

    optimizer.zero_grad()

    log_interval = max(1, num_batches // 100)  # Log every 1% of batches

    for batch_idx, batch in enumerate(dataloader):
        # Move data to device
        input_ids = batch["input_ids"].to(rank)
        attention_mask = batch["attention_mask"].to(rank)
        pixel_values = batch["pixel_values"].to(rank) if batch["pixel_values"] is not None else None
        image_grid_thw = batch["image_grid_thw"].to(rank) if batch["image_grid_thw"] is not None else None
        labels = batch["labels"].to(rank)

        # Use no_sync during gradient accumulation to avoid premature DDP all-reduce
        should_sync = (batch_idx + 1) % accumulation_steps == 0
        if is_distributed and not should_sync:
            context = model.no_sync
        else:
            from contextlib import nullcontext
            context = nullcontext

        with context():
            if batch_idx == 0 and epoch == 0:
                logger.info(f"DEBUG: pixel_values is None: {pixel_values is None}, input_ids shape: {input_ids.shape}, unique tokens: {input_ids[0, :10].tolist()}")

            # Forward pass
            if use_amp:
                with autocast('cuda', dtype=torch.bfloat16):
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

                    if batch_idx == 0 and epoch == 0:
                        logger.info(f"DEBUG: scores min={scores.min().item():.4f}, max={scores.max().item():.4f}, std={scores.std().item():.4f}")

                    # Debug: log score distribution
                    if batch_idx % log_interval == 0:
                        ref_scores_d = scores_pairwise[:, 0]
                        dev_scores_d = scores_pairwise[:, 1]
                        diff_d = ref_scores_d - dev_scores_d
                        logger.info(
                            f"DEBUG batch {batch_idx}: "
                            f"ref_mean={ref_scores_d.mean().item():.4f} ref_std={ref_scores_d.std().item():.4f} "
                            f"dev_mean={dev_scores_d.mean().item():.4f} dev_std={dev_scores_d.std().item():.4f} "
                            f"diff_mean={diff_d.mean().item():.4f} diff_std={diff_d.std().item():.4f}"
                        )

                    if loss_type == "cfd":
                        # CFD loss
                        t_star_mode = config.get("t_star_mode", "true")
                        scores_for_loss = scores_pairwise
                        if t_star_mode == "random":
                            flip_mask = torch.rand(scores_pairwise.shape[0], device=rank) > 0.5
                            scores_for_loss = scores_pairwise.clone()
                            scores_for_loss[flip_mask] = scores_pairwise[flip_mask].flip(dims=[-1])
                        elif t_star_mode in ("shifted", "last"):
                            scores_for_loss = scores_pairwise.flip(dims=[-1])
                        loss_cfd = cfd_loss(scores_for_loss, torch.zeros(scores_pairwise.shape[0], dtype=torch.long, device=rank), labels_pairwise)
                        loss_calib = calib_loss(scores, labels) if calib_loss is not None else torch.tensor(0.0, device=rank)
                    elif loss_type == "pairwise":
                        # MarginRankingLoss: ref should score higher than dev
                        ref_scores = scores_pairwise[:, 0]
                        dev_scores = scores_pairwise[:, 1]
                        target = torch.ones_like(ref_scores, device=rank)  # +1 means ref > dev
                        loss_cfd = cfd_loss(ref_scores, dev_scores, target)
                        loss_calib = torch.tensor(0.0, device=rank)
                    elif loss_type == "pointwise":
                        # BCELoss: ref -> 1.0, dev -> 0.0
                        # NOTE: BCE is not autocast-safe so we compute it outside this block
                        loss_cfd = None
                        loss_calib = torch.tensor(0.0, device=rank)

                # For pointwise, compute BCE outside autocast context
                if loss_type == "pointwise":
                    loss_cfd = F.binary_cross_entropy(scores_pairwise.float(), labels_pairwise.float())

                loss = loss_cfd + config.get("lambda_calib", 0.0) * loss_calib
                loss = loss / accumulation_steps

                # Backward pass with gradient scaling
                gradient_scaler.scale(loss).backward()

                # Optimizer step
                if should_sync:
                    gradient_scaler.unscale_(optimizer)
                    # Log gradient norm before clipping
                    if batch_idx % log_interval == 0:
                        total_norm = 0.0
                        for p in model.parameters():
                            if p.grad is not None:
                                total_norm += p.grad.data.norm(2).item() ** 2
                        total_norm = total_norm ** 0.5
                        logger.info(f"DEBUG: grad_norm={total_norm:.4f}, max_grad_norm={config['max_grad_norm']}")
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

                if loss_type == "cfd":
                    t_star = compute_t_star(scores_pairwise, t_star_mode=config.get("t_star_mode", "true"), device=rank)
                    loss_cfd = cfd_loss(scores_pairwise, t_star, labels_pairwise)
                    loss_calib = calib_loss(scores, labels) if calib_loss is not None else torch.tensor(0.0, device=rank)
                elif loss_type == "pairwise":
                    ref_scores = scores_pairwise[:, 0]
                    dev_scores = scores_pairwise[:, 1]
                    target = torch.ones_like(ref_scores, device=rank)
                    loss_cfd = cfd_loss(ref_scores, dev_scores, target)
                    loss_calib = torch.tensor(0.0, device=rank)
                elif loss_type == "pointwise":
                    targets = labels_pairwise
                    loss_cfd = F.binary_cross_entropy(scores_pairwise.float(), targets.float())
                    loss_calib = torch.tensor(0.0, device=rank)

                loss = loss_cfd + config.get("lambda_calib", 0.0) * loss_calib
                loss = loss / accumulation_steps

                loss.backward()

                if should_sync:
                    # Log gradient norm before clipping
                    if batch_idx % log_interval == 0:
                        total_norm = 0.0
                        for p in model.parameters():
                            if p.grad is not None:
                                total_norm += p.grad.data.norm(2).item() ** 2
                        total_norm = total_norm ** 0.5
                        logger.info(f"DEBUG: grad_norm={total_norm:.4f}, max_grad_norm={config['max_grad_norm']}")
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config["max_grad_norm"])
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

        # Accumulate metrics
        total_loss += loss.item() * accumulation_steps
        total_cfd_loss += loss_cfd.item()
        total_calib_loss += loss_calib.item()

        # Log progress at intervals
        if (batch_idx + 1) % log_interval == 0 or (batch_idx + 1) == num_batches:
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
    logger.info(f"Loss type: {config.get('loss_type', 'cfd')}")
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
        pooling=config.get("pooling", "mean"),
        device_map=f"cuda:{local_rank}" if is_distributed else "cuda:0",
    )

    # Move model to device (already on device from device_map)
    if is_distributed:
        model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[local_rank],
            find_unused_parameters=True,
            output_device=local_rank,
            gradient_as_bucket_view=True,
        )

    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Create dataloader — auto-detect data file in directory
    data_dir = Path(config["data_dir"])
    # Try common data filenames
    candidate_files = [
        "hard_negatives.json",
        "visualprm400k_pairs.json",
        "hard_negatives_synthetic.json",
    ]
    data_path = None
    for fname in candidate_files:
        p = data_dir / fname
        if p.exists():
            data_path = p
            break
    if data_path is None:
        # Fall back to first .json file in directory
        json_files = list(data_dir.glob("*.json"))
        if json_files:
            data_path = json_files[0]
        else:
            raise FileNotFoundError(f"No data JSON found in {data_dir}")

    if not data_path.exists():
        raise FileNotFoundError(f"Data not found at {data_path}")

    logger.info("Creating DataLoader...")

    step_level = config.get("step_level", False)

    if step_level:
        # Step-level mode: dataset returns raw pairs, collate expands to steps
        from torch.utils.data import DataLoader, DistributedSampler
        dataset = StepLevelCFDPRMDataset(
            data_path=str(data_path),
            max_pairs=config.get("max_pairs"),
        )

        # Create processor for collate function
        processor = AutoProcessor.from_pretrained(config["model_name"])

        if is_distributed:
            sampler = DistributedSampler(
                dataset, num_replicas=world_size, rank=local_rank, shuffle=True, seed=config.get("seed", 42)
            )
            dataloader = DataLoader(
                dataset,
                batch_size=config["batch_size"],
                shuffle=False,
                num_workers=4,
                collate_fn=lambda batch: step_level_collate_fn(batch, processor, config.get("max_length", 512)),
                pin_memory=True,
                sampler=sampler,
            )
        else:
            dataloader = DataLoader(
                dataset,
                batch_size=config["batch_size"],
                shuffle=True,
                num_workers=4,
                collate_fn=lambda batch: step_level_collate_fn(batch, processor, config.get("max_length", 512)),
                pin_memory=True,
            )
    else:
        dataloader = create_dataloader(
            data_path=str(data_path),
            batch_size=config["batch_size"],
            shuffle=True,
            num_workers=4,
            model_name=config["model_name"],
            max_pairs=config.get("max_pairs"),
            distributed=is_distributed,
            world_size=world_size,
            rank=local_rank,
            seed=config.get("seed", 42),
        )

    logger.info(f"Dataset size: {len(dataloader.dataset)} pairs")
    logger.info(f"Batch size: {config['batch_size']}")

    # Create losses
    loss_type = config.get("loss_type", "cfd")
    if loss_type == "cfd":
        cfd_loss = CheckpointFirstDivergenceLoss(margin=config.get("cfd_margin", 0.0)).to(local_rank)
        calib_loss = CalibrationLoss(margin=0.1, tau=0.5).to(local_rank)
    elif loss_type == "all_wrong_ranking":
        cfd_loss = CheckpointFirstDivergenceLoss(margin=config.get("cfd_margin", 0.0)).to(local_rank)
        calib_loss = None
    elif loss_type == "boundary_bce":
        cfd_loss = CheckpointFirstDivergenceLoss(margin=config.get("cfd_margin", 0.0)).to(local_rank)
        calib_loss = None
    elif loss_type == "pairwise":
        cfd_loss = nn.MarginRankingLoss(margin=config.get("pairwise_margin", 0.5), reduction="mean").to(local_rank)
        calib_loss = None
    elif loss_type == "pointwise":
        cfd_loss = None  # BCE will be computed directly in train_epoch
        calib_loss = None

    logger.info(f"Loss type: {loss_type}")

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

    # Gradient scaler for AMP - not needed for bfloat16 (same dynamic range as float32)
    # Only use GradScaler for float16 mixed precision
    gradient_scaler = None

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

        # Set epoch for distributed sampler
        if is_distributed:
            dataloader.sampler.set_epoch(epoch)

        start_time = time.time()

        if step_level:
            metrics = train_epoch_step_level(
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
                is_distributed=is_distributed,
            )
        else:
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
                is_distributed=is_distributed,
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
    parser.add_argument("--max_pairs", type=int, default=None, help="Limit number of data pairs to load")
    parser.add_argument("--t_star_mode", type=str, default="true", choices=["true", "random", "shifted", "last"],
                        help="t* mode: true=read from data, random=random step, shifted=t*+1, last=last step")
    parser.add_argument("--step_level", action="store_true",
                        help="Use step-level scoring (model outputs one score per step)")
    parser.add_argument("--pooling", type=str, default="mean", choices=["mean", "last"],
                        help="Pooling strategy for StepScorer")
    parser.add_argument("--max_length", type=int, default=512, help="Max sequence length for tokenization")

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
    parser.add_argument("--lambda_step_bce", type=float, default=1.0,
                        help="Weight for step-level BCE auxiliary loss")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1)
    parser.add_argument("--max_grad_norm", type=float, default=10.0)
    parser.add_argument("--cfd_margin", type=float, default=0.0, help="Margin for CFD loss")
    parser.add_argument("--loss_type", type=str, default="cfd", choices=["cfd", "pairwise", "pointwise", "all_wrong_ranking", "boundary_bce"],
                        help="Loss type: cfd=CFD-PRM (t* only), all_wrong_ranking=all error steps, boundary_bce=upweighted BCE near t*, pairwise=MarginRankingLoss, pointwise=BCELoss")
    parser.add_argument("--pairwise_margin", type=float, default=0.5, help="Margin for pairwise ranking loss")
    parser.add_argument("--boundary_weight", type=float, default=5.0, help="Weight multiplier for BCE loss near t* boundary")

    # Checkpointing
    parser.add_argument("--checkpoint_every", type=int, default=1)
    parser.add_argument("--eval_every", type=int, default=1)

    # Misc
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--local_rank", type=int, default=-1)

    args = parser.parse_args()

    # Check for distributed training
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0)) if world_size > 1 else 0

    if world_size > 1:
        torch.cuda.set_device(local_rank)

    # Load config
    config = load_config(args)

    # Start training
    train(config, local_rank=local_rank, world_size=world_size)


if __name__ == "__main__":
    main()
