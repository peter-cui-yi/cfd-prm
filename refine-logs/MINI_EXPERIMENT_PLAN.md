# MINI-EXPERIMENT PLAN: CG-PRM Validation

## Purpose
Quick validation (2-3 days, 8 GPU-hours) to test the core hypothesis before committing to full-scale experiments.

---

## Core Hypothesis
> First-divergence iso-answer supervision improves step-level grounding detection on answer-correct but evidence-wrong traces.

---

## Mini-Data Construction

### Scale: 10% of Full Plan

| Data Type | CLEVR | DocVQA | Total |
|-----------|-------|--------|-------|
| Clean traces | 1,000 | 1,500 | **2,500** |
| Counterfactuals (F5 only) | 500 | 750 | **1,250** |
| Iso-answer pairs | 500 | 750 | **1,250** |
| Held-out test pairs | 100 | 150 | **250** |

### Why F5 Only?
**F5 (Correct answer, wrong evidence)** is the hardest and most important failure mode. If we can't detect this, the idea fails.

### Data Split
```
Training:  1,000 pairs (800 CLEVR + 200 DocVQA)
Validation: 150 pairs (100 CLEVR + 50 DocVQA)
Test:      250 pairs (150 CLEVR + 100 DocVQA) - held out from training
```

---

## Mini-Training Setup

### Models to Train

| Model | Loss | Data | GPU-hours |
|-------|------|------|-----------|
| CG-PRM (first-divergence) | L_fd | Iso-answer pairs | 2h |
| Baseline (pointwise) | BCE | Same data | 2h |

### Hyperparameters (Reduced)
| Parameter | Value |
|-----------|-------|
| Backbone | Qwen2.5-VL-3B |
| LoRA rank | 8 (vs 16 full) |
| Learning rate | 2e-4 |
| Epochs | 2 (vs 3 full) |
| Batch size | 16 (vs 32 full) |
| Steps | ~125 (1K pairs ÷ 16 batch) |

### Training Command
```bash
# CG-PRM mini
torchrun --nproc_per_node=1 train.py \
    --data_path data/mini_pairs.json \
    --output_dir checkpoints/mini-cg-prm \
    --lora_r 8 \
    --learning_rate 2e-4 \
    --num_epochs 2 \
    --batch_size 16 \
    --loss_type first_divergence

# Baseline mini
torchrun --nproc_per_node=1 train.py \
    --data_path data/mini_pairs.json \
    --output_dir checkpoints/mini-pointwise \
    --loss_type pointwise
```

---

## Evaluation (Single Metric Focus)

### Primary Metric: Step AUROC at t*

**What it measures**: Can the model distinguish grounded from ungrounded steps at the divergence point?

```python
def evaluate(model, test_pairs):
    """Compute step-level AUROC at t*."""
    y_true = []
    y_score = []

    for pair in test_pairs:
        # Score positive step at t*
        pos_score = model.score_step(pair["positive"], pair["t_star"])
        # Score negative step at t*
        neg_score = model.score_step(pair["negative"], pair["t_star"])

        y_true.extend([1, 0])
        y_score.extend([pos_score, neg_score])

    return roc_auc_score(y_true, y_score)
```

### Secondary Metrics (Optional)
| Metric | Purpose |
|--------|---------|
| Pair ranking accuracy | Correct pair ordering rate |
| Score gap | E[s^+] - E[s^-] magnitude |

---

## Go/No-Go Criteria

### ✅ GO (Proceed to Full Experiment)

| Criterion | Threshold |
|-----------|-----------|
| **Primary** | CG-PRM AUROC > Pointwise AUROC + **0.05** (5pp) |
| **Confidence** | Bootstrap 95% CI non-overlapping |
| **Pair ranking** | CG-PRM accuracy > 0.55 (above random) |

### ⚠️ MARGINAL (Investigate Before Scaling)

| Criterion | Threshold |
|-----------|-----------|
| CG-PRM AUROC > Pointwise + 0.02 (2pp) | Weak signal, debug data quality |
| CI overlaps but directional trend | Increase data, check t* identification |

### ❌ NO-GO (Idea Fails)

| Criterion | Threshold |
|-----------|-----------|
| CG-PRM AUROC ≤ Pointwise | First-divergence doesn't help |
| CG-PRM AUROC < 0.55 | Not learning grounding at all |
| Pair ranking accuracy ≤ 0.50 | Random performance |

---

## Decision Tree

```
                    Mini-Experiment
                          │
                          ▼
            ┌─────────────────────────┐
            │  CG-PRM AUROC > Pointwise + 0.05?  │
            └─────────────────────────┘
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
            ┌───────────┐  ┌─────────────────┐
            │  CI non-overlap? │  │ AUROC > +0.02? │
            └───────────┘  └─────────────────┘
                │       │        │       │
               YES      NO      YES      NO
                │       │        │       │
                ▼       ▼        ▼       ▼
              GO    MARGINAL  MARGINAL  NO-GO
              │         │        │       │
              ▼         ▼        ▼       ▼
         Full       Debug    Check    Pivot or
         Scale      Data     t* ID    Abandon
```

---

## Execution Timeline

### Day 1: Data Construction (4 hours)

| Hour | Task | Output |
|------|------|--------|
| 0-1 | Generate 1K CLEVR clean traces | `data/mini_clevr_clean.json` |
| 1-2 | Generate 1.5K DocVQA clean traces | `data/mini_docvqa_clean.json` |
| 2-3 | Generate F5 counterfactuals | `data/mini_counterfactuals.json` |
| 3-4 | Construct pairs, split train/test | `data/mini_pairs.json` |

**GPU**: 1x A800 (4 hours)

### Day 2: Training (5 hours)

| Hour | Task | Output |
|------|------|--------|
| 0-2 | Train CG-PRM (first-divergence) | `checkpoints/mini-cg-prm/` |
| 2-4 | Train Pointwise baseline | `checkpoints/mini-pointwise/` |
| 4-5 | Evaluate on test set | `results/mini_results.json` |

**GPU**: 1x A800 (4 hours)

### Day 3: Decision (2 hours)

| Hour | Task |
|------|------|
| 0-1 | Bootstrap CI, compute metrics |
| 1-2 | Apply decision criteria, document findings |

---

## Resource Budget

| Resource | Mini-Experiment | Full Experiment |
|----------|-----------------|-----------------|
| GPU-hours | **8h** | 82h |
| Days | **3** | 40 |
| Data | **2.5K** traces | 25K traces |
| Pairs | **1.25K** | 13K |

**10x efficiency**: Validate idea at 10% cost before full commitment.

---

## Success Checklist

Before declaring "GO":
- [ ] CG-PRM AUROC > Pointwise + 0.05
- [ ] 95% CI non-overlapping (bootstrap N=1000)
- [ ] Pair ranking accuracy > 0.55
- [ ] Score gap E[s^+] - E[s^-] > 0.1
- [ ] Visual inspection: t* correctly identified for 5 random samples

---

## Failure Analysis Protocol

If NO-GO or MARGINAL, investigate:

### Check 1: Data Quality
```python
# Are clean traces actually grounded?
audit_clean_traces(n=20)

# Are counterfactuals non-trivial?
text_only_baseline = train_text_classifier(counterfactuals)
print(f"Text-only AUROC: {text_only_baseline.auroc}")  # Should be < 0.75
```

### Check 2: t* Identification
```python
# Is t* being identified correctly?
for pair in sample(pairs, 10):
    print(f"Expected t*: {pair.t_star}")
    print(f"Grounding diff at t*? {check_diff(pair, pair.t_star)}")
```

### Check 3: Learning Dynamics
```python
# Is loss decreasing?
plot_loss_curves(cg_prm_logs)
plot_loss_curves(pointwise_logs)

# Is score gap emerging?
plot_score_gap_over_training(cg_prm_logs)
```

---

## Commands to Run

```bash
# 1. Generate mini data
python scripts/generate_mini_data.py \
    --clevr_n 1000 --docvqa_n 1500 \
    --output data/mini/

# 2. Train models
bash scripts/run_mini_training.sh

# 3. Evaluate
python scripts/evaluate_mini.py \
    --cg_prm checkpoints/mini-cg-prm \
    --pointwise checkpoints/mini-pointwise \
    --test_data data/mini/test_pairs.json \
    --output results/mini_results.json

# 4. Decision
python scripts/decision.py --results results/mini_results.json
```

---

## Expected Outcomes

### Scenario A: GO (Idea Works)
```
CG-PRM AUROC:     0.72 ± 0.03
Pointwise AUROC:  0.65 ± 0.04
Delta:            +0.07 (GO threshold: +0.05)
Pair accuracy:    0.68

Decision: ✅ GO - Proceed to full-scale experiment
```

### Scenario B: MARGINAL (Weak Signal)
```
CG-PRM AUROC:     0.68 ± 0.05
Pointwise AUROC:  0.64 ± 0.05
Delta:            +0.04 (MARGINAL threshold: +0.02)
CI overlap:       Partial

Decision: ⚠️ MARGINAL - Debug data quality, increase sample
```

### Scenario C: NO-GO (Idea Fails)
```
CG-PRM AUROC:     0.58 ± 0.06
Pointwise AUROC:  0.59 ± 0.06
Delta:            -0.01
Pair accuracy:    0.48 (random)

Decision: ❌ NO-GO - Core hypothesis rejected
```

---

**Plan Created**: 2026-03-30
**Budget**: 8 GPU-hours, 3 days
**Purpose**: Validate hypothesis before full-scale commitment