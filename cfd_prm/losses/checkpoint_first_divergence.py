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

    def forward_step_level(
        self,
        scores: torch.FloatTensor,  # [n_total_steps] — one score per step
        metadata: Dict,
        labels: torch.FloatTensor = None,  # [n_total_steps] per-step labels
        loss_type: str = "cfd",  # "cfd" or "all_wrong_ranking"
    ) -> torch.FloatTensor:
        """
        Compute first-divergence loss for step-level scoring.

        Two components:
        1. Ranking loss: depends on loss_type
           - "cfd": ref_score(t*) > dev_score(t*) — only at t*
           - "all_wrong_ranking": ref_score(t) > dev_score(t) for ALL t >= t*
        2. Step-level BCE loss: all steps supervised with their labels

        Args:
            scores: [n_total_steps] flat scores for all steps across all pairs
            metadata: Dict with global_pair_idx, side, step_idx, t_star, labels
            labels: [n_total_steps] per-step labels (1=correct, 0=incorrect).
                    If None, falls back to labels in metadata.
            loss_type: "cfd" for first-divergence only, "all_wrong_ranking" for all error steps

        Returns:
            cfd_loss, bce_loss
        """
        pair_idx = metadata["global_pair_idx"]  # [n_total_steps]
        side = metadata["side"]                  # [n_total_steps], 0=ref, 1=dev
        step_idx = metadata["step_idx"]          # [n_total_steps]
        t_star = metadata["t_star"]              # [n_total_steps]

        step_labels = labels if labels is not None else metadata["labels"]

        n_pairs = int(pair_idx.max().item()) + 1

        # --- Component 1: Ranking loss ---
        if loss_type == "all_wrong_ranking":
            # For each pair, rank ref score vs dev score at EVERY step >= t*
            all_ranking_losses = []
            for p in range(n_pairs):
                mask = pair_idx == p
                p_t_star = int(t_star[mask][0].item())

                # Get dev steps that are >= t* (error steps)
                dev_mask = mask & (side == 1)
                dev_steps = step_idx[dev_mask]
                dev_scores = scores[dev_mask]

                # Get ref score at t* (or closest step)
                ref_mask = mask & (side == 0)
                ref_steps = step_idx[ref_mask]
                ref_scores_all = scores[ref_mask]

                # For each dev error step, compare with ref score at same step index
                for i, (ds, dscore) in enumerate(zip(dev_steps.tolist(), dev_scores.tolist())):
                    if ds >= p_t_star:
                        # Find ref score at same step index (or closest)
                        ref_at_same_step = ref_steps == ds
                        if ref_at_same_step.any():
                            ref_score = ref_scores_all[ref_at_same_step.nonzero(as_tuple=True)[0][0]]
                        else:
                            # Use ref score at t* as proxy
                            ref_at_tstar = ref_steps == p_t_star
                            if ref_at_tstar.any():
                                ref_score = ref_scores_all[ref_at_tstar.nonzero(as_tuple=True)[0][0]]
                            else:
                                ref_score = ref_scores_all[-1]
                        ranking = -F.logsigmoid(ref_score - dscore + self.margin)
                        all_ranking_losses.append(ranking)

            if all_ranking_losses:
                ranking_loss = torch.stack(all_ranking_losses).mean()
            else:
                ranking_loss = torch.tensor(0.0, device=scores.device)
        else:
            # Original CFD: ranking only at t*
            ref_scores_at_tstar = torch.zeros(n_pairs, device=scores.device)
            dev_scores_at_tstar = torch.zeros(n_pairs, device=scores.device)
            valid_pairs = torch.zeros(n_pairs, dtype=torch.bool, device=scores.device)

            for p in range(n_pairs):
                mask = pair_idx == p
                p_t_star = t_star[mask][0].item()

                # Reference score at t*
                ref_mask = mask & (side == 0)
                ref_steps = step_idx[ref_mask]
                ref_scores = scores[ref_mask]
                if (ref_steps == p_t_star).any():
                    idx = (ref_steps == p_t_star).nonzero(as_tuple=True)[0][0]
                    ref_scores_at_tstar[p] = ref_scores[idx]
                else:
                    ref_scores_at_tstar[p] = ref_scores[-1]

                # Deviated score at t*
                dev_mask = mask & (side == 1)
                dev_steps = step_idx[dev_mask]
                dev_scores = scores[dev_mask]
                if (dev_steps == p_t_star).any():
                    idx = (dev_steps == p_t_star).nonzero(as_tuple=True)[0][0]
                    dev_scores_at_tstar[p] = dev_scores[idx]
                else:
                    dev_scores_at_tstar[p] = dev_scores[-1]

                valid_pairs[p] = True

            # Ranking loss: -log σ(ref_score(t*) - dev_score(t*) + margin)
            if valid_pairs.any():
                ranking_loss = -F.logsigmoid(
                    ref_scores_at_tstar[valid_pairs] - dev_scores_at_tstar[valid_pairs] + self.margin
                )
                ranking_loss = ranking_loss.mean()
            else:
                ranking_loss = torch.tensor(0.0, device=scores.device)

        # --- Component 2: Step-level BCE (supervises ALL steps) ---
        bce_loss = F.binary_cross_entropy(scores.float(), step_labels.float())

        return ranking_loss, bce_loss

    def forward(
        self,
        scores: torch.FloatTensor,  # [batch_size, seq_len] or [n_pairs, 2]
        t_star: torch.LongTensor,   # [batch_size] or [n_pairs]
        labels: Optional[torch.FloatTensor] = None,  # [batch_size, seq_len] or [n_pairs, 2], unused
    ) -> torch.FloatTensor:
        """
        Compute first-divergence loss.

        Args:
            scores: Step-level scores [batch_size, seq_len] or pairwise scores [n_pairs, 2]
            t_star: First checkpoint-failure step for each sample
            labels: (unused, kept for compatibility)

        Returns:
            loss: Scalar loss value
        """
        batch_size, seq_len = scores.shape

        # Handle pairwise mode: [n_pairs, 2] where col 0 = ref, col 1 = dev
        # In this case, t_star selects which column to use, but the ranking
        # is directly between the two columns (not even/odd rows).
        if seq_len == 2:
            ref_scores = scores[:, 0]  # [n_pairs]
            dev_scores = scores[:, 1]  # [n_pairs]
            ranking_loss = -F.logsigmoid(ref_scores - dev_scores + self.margin)
            if self.reduction == 'mean':
                return ranking_loss.mean()
            elif self.reduction == 'sum':
                return ranking_loss.sum()
            else:
                return ranking_loss

        # Step-level mode: gather scores at t* for each sample
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
        labels: torch.FloatTensor = None,  # [batch_size, seq_len]
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
