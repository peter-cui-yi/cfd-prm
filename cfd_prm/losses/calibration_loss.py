"""
Calibration Loss for CFD-PRM

Ensures cross-trajectory score comparability:
  L_calib = -log σ(s_reference - s_deviated)

where:
  s_reference = -softmin(mean_t r_t(τ⁺))
  s_deviated = -softmin(min_t r_t(τ⁻))
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class CalibrationLoss(nn.Module):
    """
    Cross-trajectory calibration loss.

    Anchors reference (all-PASS) trajectories to have systematically
    higher scores than deviated trajectories, preventing score drift.
    """

    def __init__(
        self,
        tau: float = 1.0,
        margin: float = 0.0,
        reduction: str = 'mean'
    ):
        """
        Args:
            tau: Temperature for softmin aggregation
            margin: Minimum score difference
            reduction: 'mean' or 'sum'
        """
        super().__init__()
        self.tau = tau
        self.margin = margin
        self.reduction = reduction

    def softmin_aggregate(self, scores: torch.FloatTensor) -> torch.FloatTensor:
        """
        Aggregate step scores via softmin.

        Args:
            scores: [batch_size, seq_len] step scores

        Returns:
            trace_scores: [batch_size] aggregated trace scores
        """
        # softmin: -softmin_τ(r_t) = -(-Σ r_t * exp(-r_t/τ) / Σ exp(-r_t/τ))
        # = Σ r_t * exp(-r_t/τ) / Σ exp(-r_t/τ)
        weights = F.softmax(-scores / self.tau, dim=-1)
        trace_scores = (scores * weights).sum(dim=-1)
        return trace_scores

    def forward(
        self,
        scores: torch.FloatTensor,  # [batch_size, seq_len] or [batch_size]
        labels: torch.FloatTensor,  # [batch_size] or [batch_size, seq_len], 1=reference, 0=deviated
    ) -> torch.FloatTensor:
        """
        Compute calibration loss.

        Args:
            scores: Step-level scores from PRM [batch_size, seq_len] or aggregated [batch_size]
            labels: 1 for reference trajectory, 0 for deviated [batch_size]

        Returns:
            loss: Scalar calibration loss
        """
        # Handle 2D scores -> aggregate to 1D
        if scores.dim() == 2:
            trace_scores = self.softmin_aggregate(scores)  # [batch_size]
        else:
            trace_scores = scores  # Already aggregated [batch_size]
        
        # Handle labels (may be 1D or 2D)
        if labels.dim() == 2:
            labels = labels[:, 0]  # Take first step label [batch_size]

        # Separate reference and deviated scores
        ref_mask = (labels == 1)
        dev_mask = (labels == 0)

        ref_scores = trace_scores[ref_mask]
        dev_scores = trace_scores[dev_mask]

        if ref_scores.numel() == 0 or dev_scores.numel() == 0:
            return torch.tensor(0.0, device=scores.device)

        # Pairwise calibration: ref should score higher than dev
        # Assuming paired batches: [ref_1, dev_1, ref_2, dev_2, ...]
        if ref_scores.shape == dev_scores.shape:
            calib_loss = -F.logsigmoid(ref_scores - dev_scores + self.margin)
        else:
            # Use all pairs if shapes don't match
            diff = ref_scores.unsqueeze(1) - dev_scores.unsqueeze(0)  # [n_ref, n_dev]
            calib_loss = -F.logsigmoid(diff + self.margin)

        if self.reduction == 'mean':
            return calib_loss.mean()
        elif self.reduction == 'sum':
            return calib_loss.sum()
        else:
            return calib_loss


class CombinedLoss(nn.Module):
    """
    Combined loss: L = L_fd + λ_calib * L_calib
    """

    def __init__(
        self,
        fd_margin: float = 0.0,
        calib_tau: float = 1.0,
        calib_margin: float = 0.0,
        lambda_calib: float = 0.1,
        reduction: str = 'mean'
    ):
        """
        Args:
            fd_margin: Margin for first-divergence loss
            calib_tau: Temperature for calibration loss
            calib_margin: Margin for calibration loss
            lambda_calib: Weight for calibration loss
            reduction: 'mean' or 'sum'
        """
        super().__init__()
        self.lambda_calib = lambda_calib

        self.fd_loss = CheckpointFirstDivergenceLoss(
            margin=fd_margin,
            reduction=reduction
        )
        self.calib_loss = CalibrationLoss(
            tau=calib_tau,
            margin=calib_margin,
            reduction=reduction
        )

    def forward(
        self,
        scores: torch.FloatTensor,
        t_star: torch.LongTensor,
        labels: torch.FloatTensor,
    ) -> torch.FloatTensor:
        """
        Compute combined loss.

        Args:
            scores: Step-level scores
            t_star: First checkpoint-failure step
            labels: 1 for reference, 0 for deviated

        Returns:
            loss: Combined loss value
        """
        fd_loss = self.fd_loss(scores, t_star, labels)
        calib_loss = self.calib_loss(scores, labels)

        return fd_loss + self.lambda_calib * calib_loss


# Import from checkpoint_first_divergence
from .checkpoint_first_divergence import CheckpointFirstDivergenceLoss, AdaptiveWindowLoss
