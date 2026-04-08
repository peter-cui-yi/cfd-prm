# VisualPRM400K Setup Guide for CFD-PRM

This guide explains how to use VisualPRM400K dataset for CFD-PRM training.

## Overview

**VisualPRM400K** is a multimodal process supervision dataset with:
- **400,000 step-level correctness labels** on image + text reasoning
- Paired structure: all-correct vs has-error trajectories per question
- Publicly available on HuggingFace

**Paper:** VisualPRM (InternVL team, March 2025)  
**HuggingFace:** [OpenGVLab/VisualPRM400K](https://huggingface.co/datasets/OpenGVLab/VisualPRM400K)

---

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone CFD-PRM repo (if not already done)
git clone https://github.com/peter-cui-yi/cfd-prm.git
cd cfd-prm

# Run setup script
chmod +x scripts/setup_visualprm400k.sh
./scripts/setup_visualprm400k.sh
```

This will:
1. Download VisualPRM400K from HuggingFace
2. Extract paired trajectories (reference vs deviated)
3. Find t* (first divergence point) from step labels
4. Save images and trajectory texts

### Option 2: Manual Setup

```bash
# 1. Download from HuggingFace (requires git-lfs)
git lfs install
git clone https://huggingface.co/datasets/OpenGVLab/VisualPRM400K data/visualprm400k_raw

# 2. Convert to CFD-PRM format
python -m cfd_prm.data.visualprm400k_adapter \
    --data_dir data/visualprm400k_raw \
    --output_dir data/visualprm400k \
    --min_steps 3 \
    --max_steps 20 \
    --max_pairs 50000
```

---

## Output Format

After conversion, you'll have:

```
data/
└── visualprm400k/
    ├── visualprm400k_pairs.json    # Paired trajectories
    ├── images/                      # Extracted images
    └── conversion_stats.json        # Statistics
```

### Paired Trajectory Format

```json
{
  "pair_id": "vprm_pair_00001",
  "t_star": 3,
  "reference": {
    "image_path": "data/visualprm400k/images/vprm_pair_00001_ref_abc123.png",
    "trajectory": "Question: ...\n\nReasoning steps:\n  Step 1: ...\n  Step 2: ...\n  Step 3: ...\n  Step 4: ...",
    "answer": "42",
    "labels": [1, 1, 1, 1, 1, 1]
  },
  "deviated": {
    "image_path": "data/visualprm400k/images/vprm_pair_00001_dev_def456.png",
    "trajectory": "Question: ...\n\nReasoning steps:\n  Step 1: ...\n  Step 2: ...\n  Step 3: ...\n  Step 4: [WRONG]",
    "answer": "wrong answer",
    "labels": [1, 1, 1, 0, 0, 0]
  },
  "metadata": {
    "question": "original question text",
    "num_steps": 6,
    "t_star": 3
  }
}
```

**Key fields:**
- `t_star`: First step where deviated trajectory has label=0 (first divergence point)
- `reference.labels`: All 1s (correct trajectory)
- `deviated.labels`: Has at least one 0 (error trajectory)
- Trajectory text includes steps **up to t*** for both reference and deviated

---

## Training

After setup, train CFD-PRM:

```bash
# Single GPU
python -m cfd_prm.train \
    --data_dir data/visualprm400k \
    --output_dir outputs/cfd_prm \
    --epochs 5 \
    --batch_size 32 \
    --learning_rate 2e-5

# Multi-GPU (4x A800)
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --data_dir data/visualprm400k \
    --output_dir outputs/cfd_prm \
    --epochs 5
```

---

## Troubleshooting

### HuggingFace Download Fails

```bash
# Check git-lfs is installed
git lfs --version

# Re-install datasets library
pip install --upgrade datasets
```

### Not Enough Pairs

If `conversion_stats.json` shows too few pairs:
```bash
# Increase max_pairs limit
python -m cfd_prm.data.visualprm400k_adapter \
    --data_dir data/visualprm400k \
    --output_dir data/visualprm400k \
    --max_pairs 100000
```

### Image Extraction Fails

Some samples may not have valid images. The adapter skips these automatically. Check `conversion_stats.json` for final counts.

---

## Dataset Statistics

After conversion, check `data/visualprm400k/conversion_stats.json`:

```json
{
  "raw_samples": 400000,
  "paired_trajectories": 85000,
  "converted_pairs": 45000,
  "images_saved": 90000,
  "avg_t_star": 3.2,
  "avg_steps": 5.8
}
```

**Notes:**
- `paired_trajectories`: Number of (question, all-correct, has-error) triplets
- `converted_pairs`: Actual pairs after filtering (image extraction, length filters)
- `avg_t_star`: Average first divergence point (~step 3-4)

---

## Comparison: VisualPRM400K vs VisualWebArena

| Feature | VisualPRM400K | VisualWebArena |
|---------|---------------|----------------|
| Step-level labels | ✅ Yes (core advantage) | ❌ Trajectory-level only |
| Images | ✅ Yes | ✅ Yes |
| Paired structure | ✅ All-correct vs has-error | ⚠️ Need to generate |
| t* available | ✅ From labels | ⚠️ Need to infer |
| Size | ~400K samples | ~4K tasks |
| Domain | Multimodal math/reasoning | Web navigation |
| CFD-PRM fit | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**VisualPRM400K is recommended** because it has genuine step-level correctness labels, which is exactly what CFD-PRM needs for first-divergence supervision.

---

## Compute Budget

Estimated GPU hours for CFD-PRM training on VisualPRM400K:

| Phase | GPUs | Hours | Total GPU-hrs |
|-------|------|-------|---------------|
| Data setup | 0 | 0 | 0 |
| Pilot training | 1 | 4 | 4 |
| Full training (5 epochs) | 4 | 8 | 32 |
| PRM800K OOD validation | 4 | 2 | 8 |
| Efficiency curves (ablation) | 4 | 3 | 12 |
| Theory validation | 4 | 2 | 8 |
| **Total** | | | **~64** |

---

## References

- VisualPRM Paper: https://internvl.github.io/blog/2025-03-13-VisualPRM/
- VisualPRM400K HuggingFace: https://huggingface.co/datasets/OpenGVLab/VisualPRM400K
- CFD-PRM Proposal: `refine-logs/FINAL_PROPOSAL_v6_VisualPRM.md`
