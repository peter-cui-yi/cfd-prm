# Experiment Plan: CFD-PRM (VisualWebArena Version)

## Claim-Driven Experiment Roadmap

**Version**: v3.0 (VisualWebArena Scope)  
**Linked to**: FINAL_PROPOSAL_v5_VWA.md  
**Compute Budget**: ~56 GPU-hours (reduced from 115)  
**Timeline**: 40 days  
**Data**: VisualWebArena (primary) + Mind2Web (OOD)

---

## Key Claims & Corresponding Experiments

### Claim 1: CFD-PRM improves discrimination at divergence point

**Experiment 1.1: Main Results (VisualWebArena)**
- **Dataset**: VisualWebArena test split (20% of 3,894 tasks ≈ 780 tasks)
- **Metric**: AUROC@t* (step-level discrimination at first divergence)
- **Baselines**: Outcome RM, Random, VisualPRM (if applicable)
- **GPU-hours**: 4

**Experiment 1.2: OOD Generalization**
- **OOD-Domain**: VisualWebArena tasks from unseen website categories
- **OOD-Benchmark**: Mind2Web (text-only transfer validation)
- **Metric**: AUROC drop vs IID
- **Target**: <10% drop for VWA-OOD, <15% for Mind2Web
- **GPU-hours**: 4

---

### Claim 2: CFD-PRM improves web navigation success via intervention

**Experiment 2.1: Reranking**
- **Method**: Sample N=10 trajectories per task, select highest PRM score
- **Metrics**:
  - Success Rate (task completion)
  - Process-Sound Rate (human-verified subset)
- **Baseline**: Random selection, Outcome RM
- **Target**: Success rate +10% over random
- **GPU-hours**: 10

**Experiment 2.2: Rejection Sampling**
- **Method**: PRM score < threshold → resample (max 3 attempts)
- **Metrics**: Coverage vs Correctness curve
- **GPU-hours**: 8

---

### Claim 3: Hard negatives prevent shortcut learning

**Experiment 3.1: Feature Ablation**
- **Input Variants**:
  - Answer-Only: Hide trajectory, show only final outcome
  - Evidence-Only: Hide outcome, show only trajectory
  - Full: Outcome + Trajectory
- **Prediction**:
  - Random Negative: Answer-Only ≈ Full (learns shortcut)
  - Hard Negative: Evidence-Only > Answer-Only (learns process)
- **GPU-hours**: 4

**Experiment 3.2: Noise Audit**
- **Sample**: 100 hard negative pairs
- **Human Verification**: Precision check
- **Target**: Precision ≥ 85%
- **GPU-hours**: 0 (manual)

**Experiment 3.3: Visual Similarity Filter**
- **Setup**: CLIP ViT-B/32 features, cosine similarity
- **Threshold Sweep**: sim ∈ {0.5, 0.6, 0.7}
- **Metric**: AUROC@t* vs threshold
- **Target**: sim < 0.6 optimal
- **GPU-hours**: 2

---

### Claim 4: First-divergence is more sample-efficient (Prop 1)

**Experiment 4.1: Padding Control**
- **Setup**: Same trajectories, insert 5 no-op steps
- **Variants**: T=10 vs T=15
- **Prediction**:
  - All-Steps: AUROC drops
  - First-Divergence: AUROC stable
- **GPU-hours**: 3

---

### Claim 5: Adaptive-window is robust to t* error (Prop 3)

**Experiment 5.1: t* Perturbation**
- **Setup**: Artificially shift t* by δ ∈ {-3, -2, -1, 0, 1, 2, 3}
- **Metric**: AUROC@t* vs δ
- **GPU-hours**: 3

---

### Claim 6: Checkpoint t* has information

**Experiment 6.1: Random-t* Control**
- **Setup**: Train with random t instead of true t*
- **Prediction**: True t* >> Random-t*
- **GPU-hours**: 2

**Experiment 6.2: First-Step / Last-Step Controls**
- **Setup**: Supervise only first step or last step
- **Prediction**: True t* > First ≈ Last
- **GPU-hours**: 2

---

## Compute Budget Summary

| Phase | GPU-hours | Notes |
|-------|-----------|-------|
| VWA Setup + Hard Negative Mining | 2 | CLIP filter, NLI |
| CFD-PRM Training (5 epochs) | 32 | 4xA800, LoRA |
| Discriminative Eval (1.1-1.2) | 8 | VWA + Mind2Web |
| Intervention (2.1-2.2) | 18 | Reranking, rejection |
| Hard Negative Analysis (3.x) | 6 | Feature ablation, visual filter |
| Theory Validation (4.x-6.x) | 10 | Padding, t*, controls |
| **Total** | **~76** | Under 115 budget |

**Contingency**: +20 GPU-hours for re-runs → **96 total**

---

## Experiment Priority

### Priority 1: Core Claims (Must Run)
| Exp | Description | GPU-hrs |
|-----|-------------|---------|
| 1.1 | Main results (VWA test) | 4 |
| 2.1 | Reranking | 10 |
| 3.1 | Feature ablation | 4 |
| 4.1 | Padding control | 3 |
| 6.1 | Random-t* control | 2 |
| **Subtotal** | | **23** |

### Priority 2: OOD + Robustness (Should Run)
| Exp | Description | GPU-hrs |
|-----|-------------|---------|
| 1.2 | OOD generalization | 4 |
| 3.3 | Visual filter ablation | 2 |
| 5.1 | t* perturbation | 3 |
| **Subtotal** | | **9** |

### Priority 3: Extended Validation (Nice to Have)
| Exp | Description | GPU-hrs |
|-----|-------------|---------|
| 2.2 | Rejection sampling | 8 |
| 3.2 | Noise audit | 0 |
| 4.2 | Gradient SNR | 2 |
| 6.2 | First/Last step | 2 |
| **Subtotal** | | **12** |

---

## Decision Points

| After Exp | Decision Criterion | Action |
|-----------|-------------------|--------|
| 1.1 | AUROC < 0.6 | Debug hard negatives, check t* definition |
| 2.1 | Reranking gain < 5% | Check score distribution, calibration |
| 4.1 | Padding effect not observed | Revisit theory assumptions |
| 6.1 | Random-t* ≈ True t* | t* supervision not working |

---

## Files to Create

```
cfd_prm/experiments/
├── main_results.py        # Exp 1.1
├── ood_eval.py           # Exp 1.2
├── reranking.py          # Exp 2.1
├── rejection_sampling.py # Exp 2.2
├── feature_ablation.py   # Exp 3.1
├── visual_filter_ablation.py  # Exp 3.3
├── padding_control.py    # Exp 4.1
├── gradient_snr.py       # Exp 4.2
├── tstar_perturbation.py # Exp 5.1
├── random_tstar_control.py # Exp 6.1
└── first_last_step.py    # Exp 6.2
```

---

## Success Criteria

| Metric | Target | Venue Impact |
|--------|--------|--------------|
| AUROC@t* (VWA test) | >0.75 | Strong |
| AUROC (Mind2Web OOD) | >0.65 | Moderate |
| Reranking gain | +10% | Strong |
| t* > Random-t* | p < 0.01 | Required |
| Hard negative precision | >85% | Required |

---

**Status**: READY  
**First Experiments to Launch**: 1.1 (main results) + 3.1 (feature ablation)
