"""
CFD-PRM: Checkpoint-First-Divergence Process Reward Model
"""

from .losses.checkpoint_first_divergence import (
    CheckpointFirstDivergenceLoss,
    AdaptiveWindowLoss,
)
from .losses.calibration_loss import (
    CalibrationLoss,
    CombinedLoss,
)

__version__ = "4.0"
__all__ = [
    "CheckpointFirstDivergenceLoss",
    "AdaptiveWindowLoss",
    "CalibrationLoss",
    "CombinedLoss",
]
