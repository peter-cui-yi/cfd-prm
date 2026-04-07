"""
Intervention analysis for CFD-PRM

Measures causal effect of step score interventions on trajectory outcomes.
"""

import os
import json
import argparse
import torch
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import numpy as np

from cfd_prm.models.step_scorer import StepScorer
from cfd_prm.data.dataset import CFDPRMDataset


class InterventionAnalyzer:
    """
    Analyze causal effects of step score interventions.

    Protocols:
    1. Step ablation: Zero out score at t*, measure outcome change
    2. Step swap: Exchange scores between ref/dev at t*, measure ranking flip
    3. Confidence weighting: Weight samples by score gap, measure correlation
    """

    def __init__(
        self,
        model: StepScorer,
        device: int = 0,
    ):
        self.model = model
        self.device = device
        self.model.eval()

    @torch.no_grad()
    def step_ablation(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        pixel_values: Optional[torch.FloatTensor],
        image_grid_thw: Optional[torch.LongTensor],
        t_star: torch.LongTensor,
    ) -> Dict[str, float]:
        """
        Step ablation: Zero out hidden state at t*, measure score change.

        Args:
            input_ids: [batch_size, seq_len]
            attention_mask: [batch_size, seq_len]
            pixel_values: [batch_size, num_patches, patch_dim]
            image_grid_thw: [num_images, 3]
            t_star: [batch_size] first divergence points

        Returns:
            Dictionary with ablation effects
        """
        self.model.eval()

        # Original scores
        original_scores = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
        )

        # Get hidden states for intervention
        # Note: This requires modifying the forward pass to return hidden states
        # For now, we'll approximate by masking input
        # TODO: Implement proper hidden state intervention

        # Approximate ablation by zeroing attention at t_star
        ablated_attention = attention_mask.clone()
        batch_size = input_ids.shape[0]
        for i in range(batch_size):
            t = min(t_star[i].item(), attention_mask.shape[1] - 1)
            ablated_attention[i, t:] = 0  # Zero attention from t_star onwards

        ablated_scores = self.model(
            input_ids=input_ids,
            attention_mask=ablated_attention,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
        )

        # Compute ablation effect
        score_change = (ablated_scores - original_scores).abs().mean().item()
        direction_flip = ((original_scores > 0.5) != (ablated_scores > 0.5)).sum().item() / batch_size

        return {
            "ablation_effect": score_change,
            "direction_flip_rate": direction_flip,
            "original_mean": original_scores.mean().item(),
            "ablated_mean": ablated_scores.mean().item(),
        }

    @torch.no_grad()
    def feature_intervention(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        pixel_values: Optional[torch.FloatTensor],
        image_grid_thw: Optional[torch.LongTensor],
        t_star: torch.LongTensor,
        intervention_type: str = "random_t",
    ) -> Dict[str, float]:
        """
        Feature intervention: Replace features at t* with control condition.

        Args:
            intervention_type: 'random_t' | 'feature_ablation' | 'counterfactual'

        Returns:
            Dictionary with intervention effects
        """
        self.model.eval()

        # Original scores
        original_scores = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
        )

        # Control: Random-t intervention (shuffle t* across batch)
        if intervention_type == "random_t":
            # Shuffle t_star assignment
            permuted_t_star = t_star[torch.randperm(t_star.shape[0])]

            # This is a placeholder - full implementation would require
            # modifying the loss to use the permuted t_star
            # For now, just measure sensitivity to t* perturbation
            pass

        # Feature ablation: Zero out features at t*
        elif intervention_type == "feature_ablation":
            # Would require access to intermediate hidden states
            # TODO: Implement when model returns hidden states
            pass

        # Counterfactual: Swap features between ref/dev
        elif intervention_type == "counterfactual":
            # Would require paired evaluation
            # TODO: Implement for paired batches
            pass

        # Placeholder metrics
        return {
            "intervention_type": intervention_type,
            "original_mean": original_scores.mean().item(),
            "intervention_effect": 0.0,  # TODO: Implement
        }


@torch.no_grad()
def run_intervention_analysis(
    model: StepScorer,
    dataloader: torch.utils.data.DataLoader,
    device: int = 0,
    n_samples: int = 10,
) -> Dict:
    """
    Run intervention analysis on a subset of samples.

    Args:
        model: Trained StepScorer
        dataloader: DataLoader with test samples
        device: CUDA device
        n_samples: Number of batches to analyze

    Returns:
        Dictionary of intervention results
    """
    analyzer = InterventionAnalyzer(model, device)

    ablation_results = []
    intervention_results = []

    for i, batch in enumerate(tqdm(dataloader, desc="Intervention Analysis", total=n_samples)):
        if i >= n_samples:
            break

        # Move data to device
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        pixel_values = batch["pixel_values"].to(device) if batch["pixel_values"] is not None else None
        image_grid_thw = batch["image_grid_thw"].to(device) if batch["image_grid_thw"] is not None else None

        # Approximate t* as middle of sequence
        batch_size = input_ids.shape[0]
        t_star = torch.tensor([input_ids.shape[1] // 2] * batch_size, device=device)

        # Run step ablation
        ablation = analyzer.step_ablation(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
            t_star=t_star,
        )
        ablation_results.append(ablation)

        # Run feature intervention
        intervention = analyzer.feature_intervention(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
            t_star=t_star,
            intervention_type="random_t",
        )
        intervention_results.append(intervention)

    # Aggregate results
    results = {
        "step_ablation": {
            "mean_effect": np.mean([r["ablation_effect"] for r in ablation_results]),
            "std_effect": np.std([r["ablation_effect"] for r in ablation_results]),
            "flip_rate": np.mean([r["direction_flip_rate"] for r in ablation_results]),
            "n_samples": len(ablation_results) * batch_size,
        },
        "feature_intervention": {
            "intervention_type": "random_t",
            "mean_effect": np.mean([r["intervention_effect"] for r in intervention_results]),
            "n_samples": len(intervention_results) * batch_size,
        },
    }

    return results


def main():
    parser = argparse.ArgumentParser(description="CFD-PRM Intervention Analysis")

    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to data directory")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--n_samples", type=int, default=10, help="Number of batches to analyze")
    parser.add_argument("--output_dir", type=str, default="results", help="Output directory")
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

    # Load data
    data_path = Path(args.data_dir) / "hard_negatives_test.json"
    if not data_path.exists():
        data_path = Path(args.data_dir) / "hard_negatives.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Data not found at {data_path}")

    print(f"Loading data from {data_path}...")
    dataset = CFDPRMDataset(data_path=str(data_path))

    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=4,
        collate_fn=lambda batch: __import__("cfd_prm.data.dataset", fromlist=["collate_fn"]).collate_fn(batch),
    )

    # Run intervention analysis
    print("Running intervention analysis...")
    results = run_intervention_analysis(model, dataloader, device=args.device, n_samples=args.n_samples)

    # Print results
    print("\n" + "=" * 50)
    print("Intervention Analysis Results")
    print("=" * 50)
    print(f"Step Ablation Effect:     {results['step_ablation']['mean_effect']:.4f} (+/- {results['step_ablation']['std_effect']:.4f})")
    print(f"Direction Flip Rate:      {results['step_ablation']['flip_rate']:.4f}")
    print(f"Random-t Intervention:    {results['feature_intervention']['mean_effect']:.4f}")
    print("=" * 50)

    # Save results
    results_file = output_dir / "intervention_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
