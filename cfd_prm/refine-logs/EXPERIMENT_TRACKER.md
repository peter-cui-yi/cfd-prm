# EXPERIMENT TRACKER

## CG-PRM: First-Divergence Iso-Answer Supervision

**Status**: NOT STARTED
**Last Updated**: 2026-03-30

---

## Progress Overview

| Phase | Status | Progress |
|-------|--------|----------|
| Data Construction | NOT STARTED | 0% |
| Training | NOT STARTED | 0% |
| E1: Alignment | NOT STARTED | 0% |
| E2: Schema | NOT STARTED | 0% |
| E3: Artifact Control | NOT STARTED | 0% |
| Ablations | NOT STARTED | 0% |
| Paper Writing | NOT STARTED | 0% |

---

## Phase 1: Data Construction

### 1.1 Clean Trace Generation

| Benchmark | Target | Generated | Verified | Status |
|-----------|--------|-----------|----------|--------|
| CLEVR | 10K | 0 | 0 | ⬜ NOT STARTED |
| DocVQA | 15K | 0 | 0 | ⬜ NOT STARTED |

### 1.2 Counterfactual Generation

| Family | CLEVR | DocVQA | Status |
|--------|-------|--------|--------|
| F1: Wrong region | 0 | 0 | ⬜ NOT STARTED |
| F2: Wrong value | 0 | 0 | ⬜ NOT STARTED |
| F3: Wrong relation | 0 | 0 | ⬜ NOT STARTED |
| F4: Irrelevant | 0 | 0 | ⬜ NOT STARTED |
| F5: Correct answer wrong evidence | 0 | 0 | ⬜ NOT STARTED |

### 1.3 Iso-Answer Pair Construction

| Benchmark | Target Pairs | Constructed | Coverage Rate | Status |
|-----------|--------------|-------------|---------------|--------|
| CLEVR | 5K | 0 | - | ⬜ NOT STARTED |
| DocVQA | 8K | 0 | - | ⬜ NOT STARTED |

### 1.4 Human Challenge Set

| Benchmark | Target | Annotated | Status |
|-----------|--------|-----------|--------|
| CLEVR | 100 pairs | 0 | ⬜ NOT STARTED |
| DocVQA | 100 pairs | 0 | ⬜ NOT STARTED |

---

## Phase 2: Training

### 2.1 CG-PRM (First-Divergence)

| Run | Seed | Checkpoint | Step AUROC | Status |
|-----|------|------------|------------|--------|
| v1 | 42 | - | - | ⬜ NOT STARTED |

### 2.2 Baselines

| Model | Training | Checkpoint | Status |
|-------|----------|------------|--------|
| Pointwise | Binary CE | - | ⬜ NOT STARTED |
| Post-hoc extraction | - | - | ⬜ NOT STARTED |
| Mixed (iso + wrong-answer) | - | - | ⬜ NOT STARTED |

---

## Phase 3: Core Experiments

### E1: First-Divergence vs Pointwise

| Metric | CG-PRM | Pointwise | Delta | CI | Status |
|--------|--------|-----------|-------|-----|--------|
| Step AUROC (t*) | - | - | - | - | ⬜ NOT STARTED |

**Success Criterion**: CG-PRM > Pointwise + 0.05, CI non-overlapping

### E2: Schema-Constrained vs Post-hoc

| Metric | Schema | Post-hoc | Delta | Status |
|--------|--------|----------|-------|--------|
| t* accuracy | - | - | - | ⬜ NOT STARTED |
| Leave-one-out AUROC | - | - | - | ⬜ NOT STARTED |

**Success Criterion**: Schema > Post-hoc + 0.10 (t* accuracy)

### E3a: Leave-One-Family-Out

| Held-out Family | AUROC | Full-family AUROC | Drop | Status |
|-----------------|-------|-------------------|------|--------|
| F1 | - | - | - | ⬜ NOT STARTED |
| F2 | - | - | - | ⬜ NOT STARTED |
| F3 | - | - | - | ⬜ NOT STARTED |
| F4 | - | - | - | ⬜ NOT STARTED |
| F5 | - | - | - | ⬜ NOT STARTED |
| **Mean** | - | - | - | - |

**Success Criterion**: Mean AUROC ≥ 0.65, Drop < 0.10

### E3b: Human-Authored Failures

| Benchmark | Detection Rate | CI | Status |
|-----------|----------------|-----|--------|
| CLEVR | - | - | ⬜ NOT STARTED |
| DocVQA | - | - | ⬜ NOT STARTED |

**Success Criterion**: Detection rate ≥ 0.70

---

## Phase 4: Ablations

### A1: First-Divergence vs Pointwise
(Same as E1)

### A2: Schema-Constrained vs Post-hoc
(Same as E2)

### A3: Iso-Answer Only vs Mixed

| Metric | Iso-Answer | Mixed | Delta | Status |
|--------|------------|-------|-------|--------|
| Step AUROC (t*) | - | - | - | ⬜ NOT STARTED |

**Success Criterion**: Iso-Answer > Mixed (shows shortcut leakage)

---

## Phase 5: Secondary Analysis

### Interventional Grounding Gap

| Model | Gap | Status |
|-------|-----|--------|
| CG-PRM | - | ⬜ NOT STARTED |
| Pointwise | - | ⬜ NOT STARTED |

---

## Resource Usage

| Resource | Used | Budget | Remaining |
|----------|------|--------|-----------|
| GPU-hours | 0 | 82 | 82 |
| Days | 0 | 40 | 40 |

---

## Notes

| Date | Note |
|------|------|
| 2026-03-30 | Experiment plan created |

---

## Quick Commands

```bash
# Check data status
python scripts/check_data_status.py

# Run next experiment
python scripts/run_next.py

# Update tracker
python scripts/update_tracker.py --phase data --status complete
```

---

**Legend**:
- ⬜ NOT STARTED
- 🔄 IN PROGRESS
- ✅ COMPLETE
- ❌ FAILED