# Experiment Tracker: CFD-PRM

**Project**: Checkpoint-First-Divergence Process Reward Model
**Budget**: 115 GPU-hours
**Start Date**: 2026-04-07
**Target**: NeurIPS/ICLR 2026

---

## GPU Hours Tracking

| Category | Budget | Used | Remaining |
|----------|--------|------|-----------|
| Hard Negative Construction | 12 | 0 | 12 |
| Training (+ calibration ablation) | 26 | 0 | 26 |
| Discriminative Eval (+ calibration) | 18 | 0 | 18 |
| Intervention | 35 | 0 | 35 |
| Controlled Experiments | 16 | 0 | 16 |
| AC Concerns (Random-t*, visual, leakage, domain) | 8 | 0 | 8 |
| Baseline Reproduction | 8 | 0 | 8 |
| **Total** | **123** | **0** | **123** |

*Note: 123 vs 115 budget = 8 GPU-hours buffer included*

---

## Experiment Status Summary

| Priority | Experiment | Claim | Status | Result |
|----------|------------|-------|--------|--------|
| P1 | Exp 1.1 (Main IID) | Discrimination | ⏳ Pending | - |
| P1 | Exp 2.1 (Reranking) | Intervention | ⏳ Pending | - |
| P1 | Exp 3.1 (Feature Ablation) | Hard Negative | ⏳ Pending | - |
| P1 | Exp 1.4 (Calibration) | Score Calibration | ⏳ Pending | - |
| P1 | Exp 1.2 (OOD) | Generalization | ⏳ Pending | - |
| P1 | Exp 1.3 (Human) | Human Alignment | ⏳ Pending | - |
| P2 | Exp 6.1 (Random-t*) | Checkpoint Info | ⏳ Pending | - |
| P2 | Exp 3.3 (Visual Filter) | Multimodal Check | ⏳ Pending | - |
| P2 | Exp 3.5 (Leakage Audit) | Train/Test Isolation | ⏳ Pending | - |
| P2 | Exp 3.4 (Domain Breakdown) | Bias Check | ⏳ Pending | - |
| P3 | Exp 4.1 (Padding) | Prop 1 | ⏳ Pending | - |
| P3 | Exp 5.1 (t* Perturbation) | Prop 3 | ⏳ Pending | - |
| P3 | Exp 4.2 (Gradient SNR) | Prop 1 | ⏳ Pending | - |
| P3 | Exp 6.2 (Checkpoint Density) | Robustness | ⏳ Pending | - |
| P4 | Exp 2.2 (Rejection) | Intervention | ⏳ Pending | - |
| P4 | Exp 2.3 (Pruning) | Intervention | ⏳ Pending | - |
| P4 | Exp 5.2 (Label Flip) | Prop 3 | ⏳ Pending | - |
| P4 | Exp 3.2 (Noise Audit) | Hard Negative | ⏳ Pending | - |
| P4 | Baseline Reproduction | Comparison | ⏳ Pending | - |

---

## Detailed Run Logs

### Run 1: Exp 1.1 (Main IID Results)

**Claim**: CFD-PRM improves discrimination at divergence point

**Setup**:
- Dataset: Agentic-MME test split (334 tasks)
- Metric: AUROC@t*

**Status**: ⏳ Pending

**Result**:
```
| Model | AUROC@t* | Δ vs Random |
|-------|----------|-------------|
| Random | 0.50 | - |
| Outcome RM | - | - |
| VisualPRM | - | - |
| VRPRM | - | - |
| CG-PRM | - | - |
| CFD-PRM (t* only) | - | - |
| CFD-PRM (adaptive-window) | - | - |
| CFD-PRM (+calibration) | - | - |
```

**Observation**: -

**Follow-up**: -

---

### Run 2: Exp 2.1 (Reranking)

**Claim**: CFD-PRM reduces Wrong-Evidence Success

**Setup**:
- Sample N=10 trajectories per task
- Select highest PRM score

**Status**: ⏳ Pending

**Result**:
```
| Model | Success | Process-Sound | Wrong-Evidence Success ↓ |
|-------|---------|---------------|--------------------------|
| Random | - | - | 15% |
| Outcome RM | - | - | - |
| VisualPRM | - | - | - |
| CFD-PRM | - | - | 5% (target) |
```

**Observation**: -

**Follow-up**: -

---

### Run 3: Exp 3.1 (Feature Ablation)

**Claim**: Hard negatives prevent shortcut learning

**Setup**:
- Answer-Only vs Evidence-Only vs Full input

**Status**: ⏳ Pending

**Result**:
```
| Model | Answer-Only | Evidence-Only | Full |
|-------|-------------|---------------|------|
| Random Negative | - | - | - |
| Hard Negative | - | - | - |
```

**Prediction**: Random: Answer-Only ≈ Full; Hard: Evidence-Only > Answer-Only

**Observation**: -

**Follow-up**: -

---

### Run 4: Exp 1.4 (Calibration Quality)

**Claim**: Calibration loss stabilizes cross-trajectory scores

**Setup**:
- λ_calib ∈ {0, 0.05, 0.1, 0.2}
- Metric: Calibration Error, Reliability Diagram

**Status**: ⏳ Pending

**Result**:
```
| λ | Calibration Error | Reranking Gain |
|---|-------------------|----------------|
| 0 (no calibration) | - | - |
| 0.05 | - | - |
| 0.1 | - | - |
| 0.2 | - | - |
```

**Prediction**: λ=0.1 optimal balance

**Observation**: -

**Follow-up**: -

---

### Run 5: Exp 6.1 (Random-t* Control)

**Claim**: Checkpoint t* is informative (not random)

**Setup**:
- CFD-PRM (checkpoint t*) vs Random-t* vs First-Step vs Last-Step

**Status**: ⏳ Pending

**Result**:
```
| Model | AUROC@t* | Δ vs Random |
|-------|----------|-------------|
| CFD-PRM | - | - |
| Random-t* | - | baseline |
| First-Step | - | - |
| Last-Step | - | - |
```

**Prediction**: CFD-PRM >> Random-t* ≈ First-Step ≈ Last-Step

**Observation**: -

**Follow-up**: -

---

### Run 6: Exp 3.3 (Visual Filter Ablation)

**Claim**: Visual similarity filter improves hard negative quality

**Setup**:
- CLIP ViT-B/32 features
- Threshold: sim ∈ {0.5, 0.6, 0.7}

**Status**: ⏳ Pending

**Result**:
```
| Threshold | Precision | Recall | AUROC@t* |
|-----------|-----------|--------|----------|
| No filter | - | - | - |
| sim < 0.5 | - | - | - |
| sim < 0.6 | - | - | - |
| sim < 0.7 | - | - | - |
```

**Prediction**: sim < 0.6 optimal

**Observation**: -

**Follow-up**: -

---

### Run 7: Exp 3.5 (Leakage Audit)

**Claim**: Train/test isolation is maintained

**Setup**:
- Sample 100 test hard negative pairs
- Check: answer + template + observation overlap with train

**Status**: ⏳ Pending

**Result**:
```
| Check Type | Overlap Count | Leakage Rate |
|------------|---------------|--------------|
| Answer string | - / 100 | -% |
| Question template | - / 100 | -% |
| Observation feature | - / 100 | -% |
| **Total** | **- / 100** | **-%** |
```

**Target**: leakage rate = 0%

**Observation**: -

**Follow-up**: -

---

### Run 8: Exp 3.4 (Domain/A answer-Type Breakdown)

**Claim**: No severe domain bias in hard negatives

**Setup**:
- Stratify by domain (CLEVR/DocVQA/COCO/GQA)
- Stratify by answer type (number/entity/date/color/bool)

**Status**: ⏳ Pending

**Result**:
```
Domain Breakdown:
| Domain | N Pairs | AUROC@t* | 95% CI |
|--------|---------|----------|--------|
| CLEVR (count) | - | - | - |
| CLEVR (attribute) | - | - | - |
| DocVQA (text) | - | - | - |
| COCO (object) | - | - | - |
| GQA (relation) | - | - | - |
```

**Observation**: -

**Follow-up**: -

---

### Run 9: Exp 4.1 (Padding Control)

**Claim**: First-divergence is more sample-efficient (Prop 1)

**Setup**:
- T=10 (original) vs T=15 (padded with no-ops)

**Status**: ⏳ Pending

**Result**:
```
| Model | T=10 | T=15 | Δ |
|-------|------|------|---|
| All-Steps | - | - | ↓ |
| First-Divergence | - | - | stable |
```

**Observation**: -

**Follow-up**: -

---

### Run 10: Exp 5.1 (t* Perturbation)

**Claim**: Adaptive-window is robust to t* error (Prop 3)

**Setup**:
- δ ∈ {-3, -2, -1, 0, 1, 2, 3}
- σ ∈ {0.5, 1.0, 2.0}

**Status**: ⏳ Pending

**Result**:
```
| σ | δ=-3 | δ=-2 | δ=-1 | δ=0 | δ=1 | δ=2 | δ=3 |
|---|------|------|------|-----|-----|-----|-----|
| 0.5 | - | - | - | - | - | - | - |
| 1.0 | - | - | - | - | - | - | - |
| 2.0 | - | - | - | - | - | - | - |
```

**Observation**: -

**Follow-up**: -

---

## Decision Points

### DP1: After Run 1 + Run 2 (Day 18)

**Criteria**:
- ✅ Run 1: CFD-PRM AUROC@t* > 0.65 (or > VisualPRM by +10%)
- ✅ Run 2: Wrong-Evidence Success < 10%

**If both pass**: Continue to Priority 2 experiments

**If either fails**: Debug (check training convergence, hard negative quality, t* localization)

---

### DP2: After Run 5 (Random-t*) (Day 22)

**Criteria**:
- ✅ CFD-PRM AUROC@t* > Random-t* by +15%

**If pass**: Checkpoint annotation is informative

**If fails**: Major issue — checkpoint t* may not be meaningful

---

### DP3: After Run 6 + Run 7 + Run 8 (Day 26)

**Criteria**:
- ✅ Visual filter improves precision (sim < 0.6 optimal)
- ✅ Leakage rate = 0%
- ✅ No severe domain bias detected

**If all pass**: AC concerns addressed

**If any fails**: Targeted fix (tighten filter / exclude overlapping pairs / reweighting)

---

### DP4: After Run 9 + Run 10 (Day 34)

**Criteria**:
- ✅ Exp 4.1: Padding affects All-Steps, not FD
- ✅ Exp 5.1: σ large → robust to t* perturbation

**If both pass**: Theory-experiment loop closed

**If either fails**: Frame as empirical findings, soften theory claims

---

## Blockers & Notes

| Date | Blocker | Resolution |
|------|---------|------------|
| - | - | - |

---

## Weekly Checkpoints

| Week | Target | Status |
|------|--------|--------|
| Week 1 (Day 1-7) | Hard negative construction (+visual +leakage check) | ⏳ |
| Week 2 (Day 8-14) | CFD-PRM training complete (+calibration ablation) | ⏳ |
| Week 3 (Day 15-21) | Exp 1.1, 2.1, 3.1, 1.4 complete | ⏳ |
| Week 4 (Day 22-28) | Exp 6.1, 3.3, 3.5, 3.4, 1.2, 1.3 complete | ⏳ |
| Week 5 (Day 29-35) | Exp 4.1, 5.1, 4.2, 6.2, 2.2, 2.3 complete | ⏳ |
| Week 6 (Day 36-40) | Exp 5.2, 3.2, Baseline + Paper writing | ⏳ |

---

**Last Updated**: 2026-04-07

**Revision History**:
- v1.0: Initial tracker (91 GPU-hours)
- v2.0 (AC Revision): Added calibration, visual filter, leakage audit, domain breakdown, Random-t* control (123 GPU-hours with buffer)
