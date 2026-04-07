"""
Discriminative evaluation metrics for CFD-PRM

Evaluates step-level scoring on hard negative test pairs.
"""

import os
import json
import argparse
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, List, Tuple
from tqdm import tqdm
import numpy as np

from cfd_prm.models.step_scorer import StepScorer
from cfd_prm.data.dataset import CFDPRMDataset


def compute_pairwise_accuracy(scores_ref: torch.Tensor, scores_dev: torch.Tensor) -> float:
    """
    Compute pairwise ranking accuracy.

    Reference should score higher than deviated.
    """
    correct = (scores_ref > scores_dev).sum().item()
    total = scores_ref.shape[0]
    return correct / total


def compute_auc(scores_ref: torch.Tensor, scores_dev: torch.Tensor) -> float:
    """
    Compute AUC-ROC for pairwise ranking.
    """
    # Concatenate scores and labels
    scores = torch.cat([scores_ref, scores_dev]).cpu().numpy()
    labels = np.concatenate([np.ones_like(scores_ref.cpu().numpy()), np.zeros_like(scores_dev.cpu().numpy())])

    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]
    sorted_labels = labels[sorted_indices]

    # Compute AUC using trapezoidal rule
    n_pos = sorted_labels.sum()
    n_neg = len(sorted_labels) - n_pos

    tpr_prev = 0.0
    fpr_prev = 0.0
    auc = 0.0

    n_pos_cum = 0
    n_neg_cum = 0

    for label in sorted_labels:
        if label == 1:
            n_pos_cum += 1
        else:
            n_neg_cum += 1

        tpr = n_pos_cum / n_pos
        fpr = n_neg_cum / n_neg

        # Trapezoidal rule
        auc += (fpr - fpr_prev) * (tpr + tpr_prev) / 2

        tpr_prev = tpr
        fpr_prev = fpr

    return auc


def compute_kendall_tau(scores_ref: torch.Tensor, scores_dev: torch.Tensor) -> float:
    """
    Compute Kendall's tau for ranking correlation.
    """
    # For pairwise comparison, tau is simply: (concordant - discordant) / total
    n_pairs = min(scores_ref.shape[0], scores_dev.shape[0])
    concordant = (scores_ref > scores_dev).sum().item()
    discordant = (scores_ref < scores_dev).sum().item()

    if n_pairs == 0:
        return 0.0

    return (concordant - discordant) / n_pairs


def compute_metrics_by_difficulty(
    scores_ref: torch.Tensor,
    scores_dev: torch.Tensor,
    difficulties: List[str],
) -> Dict[str, Dict[str, float]]:
    """
    Compute metrics stratified by difficulty level.
    """
    difficulty_levels = np.unique(difficulties)
    metrics_by_level = {}

    for level in difficulty_levels:
        mask = np.array(difficulties) == level
        ref_subset = scores_ref[mask]
        dev_subset = scores_dev[mask]

        if len(ref_subset) == 0:
            continue

        metrics_by_level[level] = {
            "accuracy": compute_pairwise_accuracy(ref_subset, dev_subset),
            "auc": compute_auc(ref_subset, dev_subset),
            "kendall_tau": compute_kendall_tau(ref_subset, dev_subset),
            "n_samples": len(ref_subset),
        }

    return metrics_by_level


@torch.no_grad()
def evaluate(
    model: StepScorer,
    dataloader: torch.utils.data.DataLoader,
    device: int = 0,
) -> Dict:
    """
    Run full evaluation.

    Returns:
        Dictionary of metrics
    """
    model.eval()

    all_scores_ref = []
    all_scores_dev = []
    all_pair_ids = []
    all_task_ids = []
    all_difficulties = []

    for batch in tqdm(dataloader, desc="Evaluating"):
        # Move data to device
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        pixel_values = batch["pixel_values"].to(device) if batch["pixel_values"] is not None else None
        image_grid_thw = batch["image_grid_thw"].to(device) if batch["image_grid_thw"] is not None else None

        # Forward pass
        scores = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
        )

        # Split reference and deviated
        batch_size = scores.shape[0]
        scores_ref = scores[0::2]  # Even indices: reference
        scores_dev = scores[1::2]  # Odd indices: deviated

        all_scores_ref.append(scores_ref.cpu())
        all_scores_dev.append(scores_dev.cpu())
        all_pair_ids.extend(batch["pair_ids"][::2])
        all_task_ids.extend(batch["task_ids"][::2])

    # Concatenate all results
    scores_ref = torch.cat(all_scores_ref, dim=0)
    scores_dev = torch.cat(all_scores_dev, dim=0)

    # Compute overall metrics
    metrics = {
        "pairwise_accuracy": compute_pairwise_accuracy(scores_ref, scores_dev),
        "auc_roc": compute_auc(scores_ref, scores_dev),
        "kendall_tau": compute_kendall_tau(scores_ref, scores_dev),
        "n_pairs": len(scores_ref),
        "mean_score_ref": scores_ref.mean().item(),
        "mean_score_dev": scores_dev.mean().item(),
        "score_gap": (scores_ref - scores_dev).mean().item(),
    }

    # Metrics by difficulty (if available)
    if all_difficulties:
        metrics_by_difficulty = compute_metrics_by_difficulty(
            scores_ref, scores_dev, all_difficulties
        )
        metrics["by_difficulty"] = metrics_by_difficulty

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate CFD-PRM")

    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to test data directory")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for evaluation")
    parser.add_argument("--output_dir", type=str, default="results", help="Output directory for results")
    parser.add_argument("--device", type=int, default=0, help="CUDA device")

    args = parser.parse_args()

    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    print(f"Loading model from {args.checkpoint}...")
    model = StepScorer()
    model.load_pretrained(args.checkpoint)
    model = model.to(args.device)
    model.eval()

    print(f"Model loaded: {sum(p.numel() for p in model.parameters()):,} parameters")

    # Load test data
    test_data_path = Path(args.test_dir) / "hard_negatives_test.json"
    if not test_data_path.exists():
        # Fall back to single file split
        test_data_path = Path(args.test_dir) / "hard_negatives.json"

    if not test_data_path.exists():
        raise FileNotFoundError(f"Test data not found at {test_data_path}")

    print(f"Loading test data from {test_data_path}...")
    test_dataset = CFDPRMDataset(
        data_path=str(test_data_path),
        max_length=512,
    )

    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        collate_fn=lambda batch: __import__("cfd_prm.data.dataset", fromlist=["collate_fn"]).collate_fn(batch),
    )

    print(f"Test set size: {len(test_dataset)} pairs")

    # Run evaluation
    print("Running evaluation...")
    metrics = evaluate(model, test_loader, device=args.device)

    # Print results
    print("\n" + "=" * 50)
    print("CFD-PRM Evaluation Results")
    print("=" * 50)
    print(f"Pairwise Accuracy: {metrics['pairwise_accuracy']:.4f}")
    print(f"AUC-ROC:           {metrics['auc_roc']:.4f}")
    print(f"Kendall's Tau:     {metrics['kendall_tau']:.4f}")
    print(f"Score Gap:         {metrics['score_gap']:.4f}")
    print(f"N Pairs:           {metrics['n_pairs']}")
    print("=" * 50)

    # Save results
    results_file = output_dir / "eval_results.json"
    with open(results_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
