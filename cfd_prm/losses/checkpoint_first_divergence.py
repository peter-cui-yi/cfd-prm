"""
Checkpoint-First-Divergence Loss for CFD-PRM

Implements the core loss function:
  L_fd = -log σ(r_θ(τ⁺) - r_θ(τ⁻))  at t* only

With adaptive-window extension:
  L_aw = (1/|W|) Σ_{t∈W} w_t · ℓ_t
  where W = {t*-k, ..., t*+k}, w_t = exp(-|t-t*|/σ)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional


class CheckpointFirstDivergenceLoss(nn.Module):
    """
    Checkpoint-First-Divergence Loss.

    Focuses supervision on the first checkpoint-failure step (t*) only,
    avoiding gradient dilution across all steps.
    """

    def __init__(self, margin: float = 0.0, reduction: str = 'mean'):
        """
        Args:
            margin: Minimum score difference between positive and negative
            reduction: 'mean' or 'sum'
        """
        super().__init__()
        self.margin = margin
        self.reduction = reduction

    def forward(
        self,
        scores: torch.FloatTensor,  # [batch_size, seq_len]
        t_star: torch.LongTensor,   # [batch_size]
        labels: torch.FloatTensor,  # [batch_size, seq_len], 1=reference, 0=deviated
    ) -> torch.FloatTensor:
        """
        Compute first-divergence loss.

        Args:
            scores: Step-level scores from PRM
            t_star: First checkpoint-failure step for each sample
            labels: 1 for reference trajectory, 0 for deviated

        Returns:
            loss: Scalar loss value
        """
        batch_size, seq_len = scores.shape

        # Gather scores at t* for each sample
        t_star_expanded = t_star.unsqueeze(-1)  # [batch_size, 1]
        scores_at_tstar = torch.gather(scores, 1, t_star_expanded).squeeze(-1)  # [batch_size]

        # Pairwise ranking: reference should score higher than deviated at t*
        # Assuming batch is paired: [ref_1, dev_1, ref_2, dev_2, ...]
        ref_scores = scores_at_tstar[0::2]   # Even indices
        dev_scores = scores_at_tstar[1::2]   # Odd indices

        # Ranking loss: -log σ(ref - dev)
        ranking_loss = -F.logsigmoid(ref_scores - dev_scores + self.margin)

        if self.reduction == 'mean':
            return ranking_loss.mean()
        elif self.reduction == 'sum':
            return ranking_loss.sum()
        else:
            return ranking_loss


class AdaptiveWindowLoss(nn.Module):
    """
    Adaptive-Window Extension of First-Divergence Loss.

    Applies supervised loss to a window around t* for robustness:
      L_aw = (1/|W|) Σ_{t∈W} w_t · ℓ_t
      where W = {t*-k, ..., t*+k}, w_t = exp(-|t-t*|/σ)
    """

    def __init__(
        self,
        sigma: float = 1.0,
        k_factor: float = 1.0,
        margin: float = 0.0,
        reduction: str = 'mean'
    ):
        """
        Args:
            sigma: Bandwidth for exponential weighting
            k_factor: Window size factor (k = k_factor * checkpoint_density)
            margin: Minimum score difference
            reduction: 'mean' or 'sum'
        """
        super().__init__()
        self.sigma = sigma
        self.k_factor = k_factor
        self.margin = margin
        self.reduction = reduction

    def forward(
        self,
        scores: torch.FloatTensor,  # [batch_size, seq_len]
        t_star: torch.LongTensor,   # [batch_size]
        checkpoint_density: Optional[torch.FloatTensor] = None,  # [batch_size]
        labels: torch.FloatTensor,  # [batch_size, seq_len]
    ) -> torch.FloatTensor:
        """
        Compute adaptive-window loss.

        Args:
            scores: Step-level scores from PRM
            t_star: First checkpoint-failure step
            checkpoint_density: Checkpoints per task (for adaptive k)
            labels: 1 for reference trajectory, 0 for deviated

        Returns:
            loss: Scalar loss value
        """
        batch_size, seq_len = scores.shape

        # Adaptive window size based on checkpoint density
        if checkpoint_density is None:
            k = torch.ones(batch_size, dtype=torch.long, device=scores.device)
        else:
            k = torch.ceil(self.k_factor / checkpoint_density.clamp(min=0.1)).long()

        # Build window indices for each sample
        loss_values = []

        for i in range(batch_size):
            t_i = t_star[i].item()
            k_i = k[i].item()

            # Window: [max(0, t_i - k_i), min(seq_len, t_i + k_i + 1)]
            window_start = max(0, t_i - k_i)
            window_end = min(seq_len, t_i + k_i + 1)

            # Exponential weights
            t_indices = torch.arange(window_start, window_end, device=scores.device)
            weights = torch.exp(-torch.abs(t_indices - t_i) / self.sigma)
            weights = weights / weights.sum()  # Normalize

            # Gather scores in window
            window_scores = scores[i, window_start:window_end]
            window_labels = labels[i, window_start:window_end]

            # Weighted ranking loss
            if window_scores.numel() > 0:
                ref_mask = window_labels == 1
                dev_mask = window_labels == 0

                if ref_mask.any() and dev_mask.any():
                    ref_avg = (window_scores * weights * ref_mask).sum() / ref_mask.sum()
                    dev_avg = (window_scores * weights * dev_mask).sum() / dev_mask.sum()

                    loss_i = -F.logsigmoid(ref_avg - dev_avg + self.margin)
                    loss_values.append(loss_i)

        if len(loss_values) == 0:
            return torch.tensor(0.0, device=scores.device)

        loss = torch.stack(loss_values)

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss
