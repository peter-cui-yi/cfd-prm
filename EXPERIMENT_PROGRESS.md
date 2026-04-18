# CFD-PRM Experiment Progress

**Last Updated**: 2026-04-12

---

## Proposal Reference

See `refine-logs/FINAL_PROPOSAL_v6_VisualPRM.md` for full proposal.

**Core Claim**: First-Divergence Supervision achieves O(1/ε²) sample complexity vs O(T/ε²) for uniform step supervision.

---

## Contributions

| # | Contribution | Status |
|---|-------------|--------|
| 1 | First-Divergence Supervision (theory: O(1/ε²) sample complexity) | Method implemented, theory pending |
| 2 | Gradient SNR Analysis (why t* is information-maximal) | Not started |
| 3 | VisualPRM400K Adapter + Training Framework | Complete |
| 4 | PRM800K OOD Validation (domain-agnostic claim) | Not started |
| 5 | Efficiency Curves (labeled steps vs accuracy) | Not started |

---

## Experimental Results

### CFD-PRM (Main Method)

- **Training**: 3 epochs, full dataset (33,375 pairs), single GPU
- **Hyperparameters**: LR=2e-5, batch_size=2, grad_accum=4, max_grad_norm=10.0, margin=0.0, lambda_calib=0.0, warmup_ratio=0.05
- **Loss trajectory**: Epoch 1: 0.4218 → Epoch 2: 0.3990 → Epoch 3: 0.3863
- **Checkpoint**: `outputs/full_train_lr2e5/final`
- **Test Set Evaluation**:
  - AUC-ROC: **0.9392**
  - Pairwise Accuracy: **0.9149**
  - Kendall's Tau: **0.8334**
  - Score Gap (ref - dev): **0.7915**
  - Ref mean: 0.9230 (std: 0.2436)
  - Dev mean: 0.1315 (std: 0.3237)

### Baseline 1: Pairwise (MarginRankingLoss, margin=0.5)

- **Training**: Multi-GPU (4x A800), 3 epochs, full dataset
- **Hyperparameters**: Same as CFD-PRM for fair comparison
- **Loss trajectory**: Epoch 1: 0.1218 → Epoch 2: 0.0546 → Epoch 3: 0.0270
- **Checkpoint**: `outputs/baseline_pairwise_multi/final`
- **Test Set Evaluation**:
  - AUC-ROC: **0.9903**
  - Pairwise Accuracy: **0.9904**
  - Kendall's Tau: **0.9829**
  - Score Gap (ref - dev): **0.8017**
  - Ref mean: 0.8359 (std: 0.1930)
  - Dev mean: 0.0342 (std: 0.1116)

### Baseline 2: Pointwise (BCE)

- **Training**: Multi-GPU (4x A800), 3 epochs, full dataset
- **Hyperparameters**: Same as CFD-PRM for fair comparison
- **Loss trajectory**: Epoch 1: 0.2808 → Epoch 2: 0.1375 → Epoch 3: 0.0924
- **Checkpoint**: `outputs/baseline_pointwise_multi/final`
- **Test Set Evaluation**:
  - AUC-ROC: **0.9990**
  - Pairwise Accuracy: **0.9976**
  - Kendall's Tau: **0.9973**
  - Score Gap (ref - dev): **0.9648**
  - Ref mean: 0.9815 (std: 0.0630)
  - Dev mean: 0.0166 (std: 0.0810)

### Multi-GPU Training Support

- **Status**: Complete
- **Changes**: Added DistributedSampler to dataset.py, fixed DDP save_pretrained in train.py
- **Launch**: `torchrun --nproc_per_node=4`
- **Verified**: CFD-PRM test run on 2000 pairs completed successfully

---

## Comparison Summary (All models: 3 epochs, same data, same hyperparameters)

| Metric | CFD-PRM | Pairwise Baseline | Pointwise Baseline |
|--------|---------|------------------|-------------------|
| **AUC-ROC** | 0.9392 | 0.9903 | **0.9990** |
| **Pairwise Accuracy** | 0.9149 | 0.9904 | **0.9976** |
| **Kendall's Tau** | 0.8334 | 0.9829 | **0.9973** |
| **Score Gap** | 0.7915 | 0.8017 | **0.9648** |
| Ref mean (std) | 0.9230 (0.2436) | 0.8359 (0.1930) | **0.9815 (0.0630)** |
| Dev mean (std) | 0.1315 (0.3237) | 0.0342 (0.1116) | **0.0166 (0.0810)** |

**Observations**:
1. Both baselines significantly outperform CFD-PRM on all metrics
2. Pointwise BCE is the strongest: AUC 99.90% vs CFD 93.92%
3. CFD-PRM has higher variance in scores (ref_std=0.24, dev_std=0.32) vs pointwise (ref_std=0.06, dev_std=0.08)
4. CFD-PRM may need more training epochs or hyperparameter tuning to match baselines

## Pending Experiments (Per Proposal)

### Gradient SNR Analysis

- **Goal**: Measure gradient signal-to-noise ratio for CFD vs uniform step supervision
- **Prediction**: SNR_fd > SNR_all as T increases
- **Status**: Not started

### Efficiency Curves

- **Goal**: Train CFD-PRM and baselines on different data budgets (10%, 25%, 50%, 75%, 100%)
- **Target**: Show CFD-PRM 10x more efficient than VisualPRM (uniform supervision)
- **Status**: Not started

### PRM800K OOD Validation

- **Goal**: Domain-agnostic claim (text-only math reasoning)
- **Status**: Not started

### t* Information Control

- **Goal**: Compare true t* vs random t* supervision
- **Prediction**: True t* >> Random
- **Status**: Not started

---

## Infrastructure

### Data

- **VisualPRM400K**: 33,375 pairs, converted to `data/visualprm400k_converted/`
- **90/10 train/test split**: Created on-the-fly during evaluation (seed=42)

### Model

- **Base**: Qwen2.5-VL-3B (`/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b`)
- **LoRA**: r=64, alpha=128, dropout=0.05
- **Score Head**: 2-layer MLP (hidden_size → 256 → 1) with ReLU + Dropout(0.1)

### Training Code

- `cfd_prm/train.py` — supports 3 loss types: cfd, pairwise, pointwise
- `cfd_prm/models/step_scorer.py` — StepScorer model
- `cfd_prm/losses/checkpoint_first_divergence.py` — CFD loss + AdaptiveWindowLoss
- `cfd_prm/losses/calibration_loss.py` — CalibrationLoss + CombinedLoss
- `cfd_prm/data/dataset.py` — DataLoader with DistributedSampler support
- `cfd_prm/eval/eval_model.py` — Evaluation script (AUC, pairwise accuracy, Kendall's tau)

---

## Notes

- Calibration loss consistently stuck at ~0.64 with near-zero gradient contribution — effectively dead weight
- CFD-PRM has higher score variance than baselines (may indicate under-training or optimization difficulty)
- Both baselines outperform CFD-PRM on test set — CFD loss formulation may need revision
- Multi-GPU training verified working with DDP on 4x A800
