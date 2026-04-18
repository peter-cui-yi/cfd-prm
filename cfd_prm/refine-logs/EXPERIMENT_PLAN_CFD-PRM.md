# Experiment Plan: CFD-PRM

## Claim-Driven Experiment Roadmap

**Version**: v2.0 (AC Revision-Enhanced)
**Linked to**: FINAL_PROPOSAL_CFD-PRM.md v4.0
**Compute Budget**: 115 GPU-hours
**Timeline**: 40 days

---

## Key Claims & Corresponding Experiments

### Claim 1: CFD-PRM improves discrimination at divergence point

**Experiment 1.1: Main Results (IID)**
- **Dataset**: Agentic-MME test split (80% of 418 tasks)
- **Metric**: AUROC@t* (step-level discrimination at first checkpoint failure)
- **Baselines**: VisualPRM, VRPRM, CG-PRM, Outcome RM, Random
- **GPU-hours**: 4

**Experiment 1.2: OOD Generalization**
- **OOD-Tool**: 50 tasks with unseen tool APIs
- **OOD-Domain**: 50 tasks (medical/legal/finance)
- **Metric**: AUROC@t* drop vs IID
- **Target**: <10% drop
- **GPU-hours**: 4

**Experiment 1.3: Human Alignment**
- **Dataset**: Human-Verified subset (100 samples)
- **Metrics**: 
  - Human AUROC (PRM score vs human sound/flawed label)
  - t*_match (PRM t* vs human t*_human, ±1 step tolerance)
- **GPU-hours**: 2

**Experiment 1.4: Calibration Quality (Added for AC)**
- **Dataset**: Agentic-MME test split
- **Metrics**:
  - Calibration Error = E[|s_trace - P(sound|s_trace)|]
  - Reliability Diagram (decile bins)
- **Ablation**: λ_calib ∈ {0, 0.05, 0.1, 0.2}
- **Target**: λ=0.1 optimal calibration
- **GPU-hours**: 4

---

### Claim 2: CFD-PRM reduces Wrong-Evidence Success via intervention

**Experiment 2.1: Reranking**
- **Method**: Sample N=10 trajectories per task, select highest PRM score
- **Metrics**:
  - Success Rate (answer correctness)
  - Process-Sound Rate (human-verified)
  - Wrong-Evidence Success (answer correct BUT process flawed)
- **Baseline**: Random selection, Outcome RM, VisualPRM
- **Target**: Wrong-Evidence Success 15% → 5%
- **GPU-hours**: 15

**Experiment 2.2: Rejection Sampling**
- **Method**: PRM score < threshold → resample (max 3 attempts)
- **Metrics**: Coverage vs Correctness curve
- **GPU-hours**: 10

**Experiment 2.3: Search Pruning**
- **Method**: Low-score branch pruned in MCTS/beam search
- **Metrics**: Search efficiency (node expansions), final answer quality
- **GPU-hours**: 10

---

### Claim 3: Hard negatives prevent shortcut learning

**Experiment 3.1: Feature Ablation**
- **Input Variants**:
  - Answer-Only: Hide evidence, show only answer
  - Evidence-Only: Hide answer, show only evidence
  - Full: Answer + Evidence
- **Prediction**:
  - Random Negative: Answer-Only ≈ Full (learns answer shortcut)
  - Hard Negative: Evidence-Only > Answer-Only (learns evidence)
- **GPU-hours**: 4

**Experiment 3.2: Noise Audit (Expanded)**
- **Sample**: 500 hard negative pairs (expanded from 200)
- **Human Verification**: True negative vs false negative
- **Report**: Precision, False Negative Rate, Type I-IV error breakdown
- **GPU-hours**: 0 (manual)

**Experiment 3.3: Visual Similarity Filter (Added for AC)**
- **Setup**: CLIP ViT-B/32 features, cosine similarity
- **Threshold Sweep**: sim ∈ {0.5, 0.6, 0.7}
- **Metric**: AUROC@t* vs threshold
- **Prediction**: sim < 0.6 optimal (precision-recall trade-off)
- **GPU-hours**: 2

**Experiment 3.4: Domain/Answer-Type Breakdown (Added for AC)**
- **Stratification**:
  - Domain: CLEVR / DocVQA / COCO / GQA
  - Answer Type: number / entity / date / color / bool
- **Metric**: AUROC@t* with 95% CI per stratum
- **Purpose**: Check for systematic bias in hard negatives
- **GPU-hours**: 2

**Experiment 3.5: Leakage Audit (Added for AC)**
- **Sample**: 100 test hard negative pairs
- **Check**: Train overlap (answer + template + observation features)
- **Target**: leakage rate = 0%
- **GPU-hours**: 0 (manual)

---

### Claim 4: First-divergence is more sample-efficient (Prop 1)

**Experiment 4.1: Padding Control**
- **Setup**: Same trajectories, insert 5 no-op steps
- **Variants**: T=10 (original) vs T=15 (padded)
- **Prediction**:
  - All-Steps: AUROC drops (SNR diluted)
  - First-Divergence: AUROC stable
- **GPU-hours**: 3

**Experiment 4.2: Gradient SNR Measurement**
- **Setup**: Estimate gradient variance per step during training
- **Metric**: SNR = ||mean gradient||² / variance
- **Prediction**: SNR_all ∝ 1/T, SNR_fd independent of T
- **GPU-hours**: 2

---

### Claim 5: Adaptive-window is robust to t* error (Prop 3)

**Experiment 5.1: t* Perturbation**
- **Setup**: Artificially shift t* by δ ∈ {-3, -2, -1, 0, 1, 2, 3}
- **Variants**: σ ∈ {0.5, 1.0, 2.0} (window bandwidth)
- **Metric**: AUROC@t* vs δ curves
- **Prediction**: σ large → robust, σ small → sensitive
- **GPU-hours**: 3

**Experiment 5.2: Label Flip**
- **Setup**: Randomly flip 10%, 20%, 30% checkpoint labels
- **Variants**: σ ∈ {0.5, 1.0, 2.0}
- **Metric**: AUROC drop vs η
- **Prediction**: σ large → less degradation
- **GPU-hours**: 3

---

### Claim 6: Checkpoint t* has information (Added for AC)

**Experiment 6.1: Random-t* Control**
- **Variants**:
  - CFD-PRM (checkpoint t*): Use real checkpoint标注的 t*
  - Random-t*: Randomly select a step as "pseudo-t*"
  - First-Step: Fixed t* = 1
  - Last-Step: Fixed t* = T
- **Prediction**: CFD-PRM >> Random-t* ≈ First-Step ≈ Last-Step
- **Purpose**: Validate checkpoint annotation is informative (not random)
- **GPU-hours**: 4

**Experiment 6.2: Checkpoint Density Stratification**
- **Buckets**:
  - Sparse (≤3 checkpoints per task)
  - Medium (4-6 checkpoints)
  - Dense (≥7 checkpoints)
- **Metric**: AUROC@t* per bucket
- **Prediction**: adaptive-window outperforms t*-only in sparse bucket
- **GPU-hours**: 2

---

## Experiment Run Order

### Priority 1: Core Claims (Must Run)

| Run # | Experiment | GPU-hours | Cumulative |
|-------|------------|-----------|------------|
| 1 | Exp 1.1 (Main IID) | 4 | 4 |
| 2 | Exp 2.1 (Reranking) | 15 | 19 |
| 3 | Exp 3.1 (Feature Ablation) | 4 | 23 |
| 4 | Exp 1.4 (Calibration) | 4 | 27 |
| 5 | Exp 1.2 (OOD) | 4 | 31 |
| 6 | Exp 1.3 (Human) | 2 | 33 |

**Decision Point DP1**: If Exp 1.1 + 2.1 show positive signal → continue. Else → debug.

---

### Priority 2: AC Concerns (Should Run Early)

| Run # | Experiment | GPU-hours | Cumulative |
|-------|------------|-----------|------------|
| 7 | Exp 6.1 (Random-t*) | 4 | 37 |
| 8 | Exp 3.3 (Visual Filter) | 2 | 39 |
| 9 | Exp 3.5 (Leakage Audit) | 0 | 39 |
| 10 | Exp 3.4 (Domain Breakdown) | 2 | 41 |

**Decision Point DP2**: If Exp 6.1 shows CFD-PRM >> Random-t* → checkpoint t* is informative. If not → major issue.

---

### Priority 3: Theory Validation (Should Run)

| Run # | Experiment | GPU-hours | Cumulative |
|-------|------------|-----------|------------|
| 11 | Exp 4.1 (Padding) | 3 | 44 |
| 12 | Exp 5.1 (t* Perturbation) | 3 | 47 |
| 13 | Exp 4.2 (Gradient SNR) | 2 | 49 |
| 14 | Exp 6.2 (Checkpoint Density) | 2 | 51 |

---

### Priority 4: Extended Validation (Nice to Run)

| Run # | Experiment | GPU-hours | Cumulative |
|-------|------------|-----------|------------|
| 15 | Exp 2.2 (Rejection) | 10 | 61 |
| 16 | Exp 2.3 (Pruning) | 10 | 71 |
| 17 | Exp 5.2 (Label Flip) | 3 | 74 |
| 18 | Exp 3.2 (Noise Audit) | 0 | 74 |
| 19 | Baseline Reproduction | 8 | 82 |

**Buffer**: ~33 GPU-hours for debugging/re-runs

**Total**: 82 + 33 = 115 GPU-hours

---

## Experiment Tracker

| Run # | Experiment | Status | Start Date | End Date | Result | Notes |
|-------|------------|--------|------------|----------|--------|-------|
| 1 | Exp 1.1 (Main IID) | ⏳ Pending | | | | |
| 2 | Exp 2.1 (Reranking) | ⏳ Pending | | | | |
| 3 | Exp 3.1 (Feature Ablation) | ⏳ Pending | | | | |
| 4 | Exp 1.4 (Calibration) | ⏳ Pending | | | | |
| 5 | Exp 1.2 (OOD) | ⏳ Pending | | | | |
| 6 | Exp 1.3 (Human) | ⏳ Pending | | | | |
| 7 | Exp 6.1 (Random-t*) | ⏳ Pending | | | | |
| 8 | Exp 3.3 (Visual Filter) | ⏳ Pending | | | | |
| 9 | Exp 3.5 (Leakage Audit) | ⏳ Pending | | | | |
| 10 | Exp 3.4 (Domain Breakdown) | ⏳ Pending | | | | |
| 11 | Exp 4.1 (Padding) | ⏳ Pending | | | | |
| 12 | Exp 5.1 (t* Perturbation) | ⏳ Pending | | | | |
| 13 | Exp 4.2 (Gradient SNR) | ⏳ Pending | | | | |
| 14 | Exp 6.2 (Checkpoint Density) | ⏳ Pending | | | | |
| 15 | Exp 2.2 (Rejection) | ⏳ Pending | | | | |
| 16 | Exp 2.3 (Pruning) | ⏳ Pending | | | | |
| 17 | Exp 5.2 (Label Flip) | ⏳ Pending | | | | |
| 18 | Exp 3.2 (Noise Audit) | ⏳ Pending | | | | |
| 19 | Baseline Reproduction | ⏳ Pending | | | | |

---

## Success Criteria by Milestone

### Milestone 1 (Day 12): Training Complete
- [ ] CFD-PRM 4 checkpoints saved (t*, prefix, adaptive-window, +calibration)
- [ ] Training loss curves show convergence
- [ ] λ_calib ablation shows λ=0.1 optimal

### Milestone 2 (Day 18): Discriminative Results
- [ ] Exp 1.1: CFD-PRM AUROC@t* > VisualPRM by +10%
- [ ] Exp 1.2: OOD drop < 10%
- [ ] Exp 1.3: Human AUROC > 0.70
- [ ] Exp 1.4: Calibration Error < 0.15

### Milestone 3 (Day 22): AC Concerns Addressed
- [ ] Exp 6.1: CFD-PRM >> Random-t* (checkpoint t* is informative)
- [ ] Exp 3.3: Visual filter improves precision (sim < 0.6 optimal)
- [ ] Exp 3.5: Leakage rate = 0%
- [ ] Exp 3.4: No severe domain bias detected

### Milestone 4 (Day 30): Intervention Results
- [ ] Exp 2.1: Wrong-Evidence Success 15% → 5%
- [ ] Exp 2.2: Pareto curve shows coverage/correctness trade-off
- [ ] Exp 2.3: Search pruning reduces node expansions by >20%

### Milestone 5 (Day 34): Theory Validation
- [ ] Exp 4.1: Padding causes All-Steps↓, FD stable
- [ ] Exp 5.1: σ large → robust to t* perturbation
- [ ] Exp 4.2: SNR_all ∝ 1/T confirmed
- [ ] Exp 6.2: adaptive-window helps sparse checkpoint tasks

### Milestone 6 (Day 40): Paper Submission
- [ ] All tables/figures generated
- [ ] Paper draft complete
- [ ] Supplementary material ready

---

## Result Recording Template

After each experiment, record results:

```markdown
### Run X: [Experiment Name]

**Status**: ✅ Complete / ❌ Failed / ⚠️ Partial

**Result**:
| Model | Metric 1 | Metric 2 | Metric 3 |
|-------|----------|----------|----------|
| CFD-PRM | - | - | - |
| Baseline | - | - | - |

**Observation**:
- [Key finding]

**Follow-up**:
- [Action item if needed]
```

---

## Files to Create

- `cfd_prm/experiments/run_*.py` — Individual experiment scripts
- `cfd_prm/results/` — Result JSONs
- `cfd_prm/figures/` — Paper-ready figures

**New Files (AC Revision)**:
- `cfd_prm/experiments/calibration_ablation.py` — Exp 1.4
- `cfd_prm/experiments/visual_filter_ablation.py` — Exp 3.3
- `cfd_prm/experiments/leakage_audit.py` — Exp 3.5
- `cfd_prm/experiments/domain_breakdown.py` — Exp 3.4
- `cfd_prm/experiments/random_tstar.py` — Exp 6.1
- `cfd_prm/experiments/checkpoint_density.py` — Exp 6.2

---

**Next Action**: Launch Run 1 (Exp 1.1: Main IID Results)

---

## Revision History

- v1.0: Initial experiment plan (91 GPU-hours)
- v2.0 (AC Revision): Added calibration, visual filter, leakage audit, domain breakdown, Random-t* control (115 GPU-hours)
