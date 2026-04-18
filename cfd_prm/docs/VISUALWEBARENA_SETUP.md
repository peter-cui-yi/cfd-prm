# VisualWebArena Setup Guide for CFD-PRM

This guide explains how to use VisualWebArena as an alternative dataset for CFD-PRM training.

## Overview

**VisualWebArena** is a multimodal agent benchmark with:
- 3,894 web navigation tasks
- Screenshots at each step
- Action trajectories (clicks, typing, navigation)
- Success/failure labels

**Paper:** [VisualWebArena (arXiv:2401.13649)](https://arxiv.org/html/2401.13649v2)

**GitHub:** [web-arena-x/visualwebarena](https://github.com/web-arena-x/visualwebarena)

---

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# From the repository root:
git clone <your-repo-url>
cd <repo-root>

chmod +x cfd_prm/scripts/setup_visualwebarena.sh
./cfd_prm/scripts/setup_visualwebarena.sh
```

This will:
1. Clone VisualWebArena repository
2. Install dependencies
3. Convert trajectories to CFD-PRM format
4. Mine hard negative pairs

### Option 2: Manual Setup

```bash
# 1. Clone VisualWebArena
git clone https://github.com/web-arena-x/visualwebarena.git data/visualwebarena_repo
cd data/visualwebarena_repo

# 2. Follow VWA setup instructions
# (May require API keys, browser setup, etc.)

# 3. Convert to CFD-PRM format
cd ../..
python -m cfd_prm.data.visualwebarena_adapter \
    --vwa_dir data/visualwebarena_repo \
    --output_dir data/visualwebarena \
    --min_steps 3 \
    --max_steps 50

# 4. Run hard negative mining
python -m cfd_prm.data.hard_negative_miner \
    --input_dir data/visualwebarena \
    --output_dir data/hard_negatives \
    --audit_size 100
```

---

## Output Format

After conversion, you'll have:

```
data/
├── visualwebarena/
│   ├── visualwebarena_steps.json    # Step-level trajectories
│   ├── hard_negatives.json          # Hard negative pairs
│   ├── images/                       # Extracted screenshots
│   └── conversion_stats.json         # Statistics
└── hard_negatives/                   # Processed for training
    └── hard_negatives.json
```

### Hard Negative Pair Format

```json
{
  "task_id": "vwa_shopping_pair_001",
  "pair_id": "vwa_shopping_001",
  "reference": {
    "trajectory": "Task: Find and add blue shoes to cart...\nActions:\n  1. Clicked on search bar\n  2. Typed 'blue shoes'...",
    "image_path": "data/visualwebarena/images/vwa_task123_step0_abc123.png",
    "success": true
  },
  "deviated": {
    "trajectory": "Task: Find and add blue shoes to cart...\nActions:\n  1. Clicked on search bar\n  2. Typed 'red shoes'...",
    "image_path": "data/visualwebarena/images/vwa_task456_step0_def456.png",
    "success": false
  }
}
```

---

## Training

After setup, train CFD-PRM:

```bash
# Single GPU
python -m cfd_prm.train \
    --data_dir data/hard_negatives \
    --output_dir outputs/cfd_prm \
    --epochs 5 \
    --batch_size 32 \
    --learning_rate 2e-5

# Multi-GPU (4x A800)
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --data_dir data/hard_negatives \
    --output_dir outputs/cfd_prm \
    --epochs 5
```

---

## Troubleshooting

### VWA Repository Clone Fails
```bash
# Try alternative clone method
git clone --depth 1 https://github.com/web-arena-x/visualwebarena.git data/visualwebarena_repo
```

### Screenshot Extraction Fails
Some VWA trajectories may not have screenshots. Run with text-only mode:
```bash
python -m cfd_prm.data.visualwebarena_adapter \
    --vwa_dir data/visualwebarena_repo \
    --output_dir data/visualwebarena \
    --skip_screenshots
```

### Not Enough Hard Negative Pairs
Adjust the miner thresholds:
```bash
python -m cfd_prm.data.hard_negative_miner \
    --input_dir data/visualwebarena \
    --output_dir data/hard_negatives \
    --visual_threshold 0.7  # Increase from 0.6 to allow more pairs
```

---

## Dataset Statistics

After conversion, check `data/visualwebarena/conversion_stats.json`:

```json
{
  "total_trajectories": 3894,
  "total_steps": 45231,
  "total_pairs": 12500,
  "images_saved": 42000,
  "success_trajectories": 2100,
  "failure_trajectories": 1794
}
```

---

## Alternative Datasets

If VisualWebArena doesn't work for your use case, consider:

| Dataset | Multimodal | Trajectories | Download |
|---------|-----------|--------------|----------|
| **VisualWebArena** | ✅ | ✅ | GitHub |
| **Mind2Web** | ⚠️ (text-only) | ✅ | [HuggingFace](https://huggingface.co/datasets/magicgh/MT-Mind2Web) |
| **WebArena** | ⚠️ (DOM-only) | ✅ | [GitHub](https://github.com/web-arena-x/webarena) |
| **VideoWebArena** | ✅ | ✅ | [GitHub](https://github.com/ljang0/videowebarena) |

---

## Compute Budget

Estimated GPU hours for CFD-PRM training on VisualWebArena:

| Phase | GPUs | Hours | Total GPU-hrs |
|-------|------|-------|---------------|
| Hard negative mining | 1 | 2 | 2 |
| Pilot training | 1 | 4 | 4 |
| Full training (5 epochs) | 4 | 8 | 32 |
| Evaluation | 1 | 2 | 2 |
| **Total** | | | **~40** |

---

## References

- VisualWebArena Paper: https://arxiv.org/abs/2401.13649
- VisualWebArena GitHub: https://github.com/web-arena-x/visualwebarena
- CFD-PRM Proposal: `FINAL_PROPOSAL_CFD-PRM.md`
