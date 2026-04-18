# FINAL PROPOSAL: CG-PRM (Lean Version)

## First-Divergence Iso-Answer Supervision for Multimodal Process Reward Models

**Version**: Refined v3.0-Lite (Model-Centered + ACED-Lite Shield)
**Target Venue**: NeurIPS/ICLR
**Status**: Ready for implementation

---

## Problem Anchor

### Bottom-line Problem
Current multimodal PRMs fail to detect **answer-correct but evidence-wrong** reasoning traces because their supervision conflates answer correctness with grounding quality.

### Must-solve Bottleneck
VisualPRM and VRPRM use step-correctness supervision correlated with final answers. When a trace reaches the right answer but uses wrong evidence at an intermediate step, these PRMs cannot distinguish it from genuinely grounded traces.

### Non-goals
- Building full benchmark (ACED-Lite is evaluation, not contribution)
- Retraining base VLM reasoning policies
- General grounding detector
- Best-of-N reranking as method contribution

### Constraints
- Compute: 4xA800 GPUs, 40 days
- Backbone: 3B LoRA step scorer (Qwen2.5-VL-3B)
- Venue: NeurIPS/ICLR

### Success Condition
1. **Method**: CG-PRM improves over baselines on synthetic + human-audited evaluation
2. **Transfer**: Train-on-synthetic → test-on-human shows real grounding (not artifact)
3. **Generalization**: Leave-one-family-out shows no collapse to corruption patterns

---

## Contribution (Method-Centered)

### Primary: CG-PRM Method

**One-sentence**: We train a step-level PRM on first-divergence points of schema-constrained iso-answer trace pairs.

**Why smallest adequate intervention**:
- Supervising only divergence point is minimal signal for grounding discrimination
- No full-trace ranking complexity, no wrong-answer shortcut leakage

### Secondary: ACED-Lite Evaluation

**Purpose**: Defang "synthetic artifact" objection, not standalone contribution.

**Contents**:
- 3 corruption families (Object Swap, Spatial Shift, Hallucinated Evidence)
- ~100 human-audited examples (not 300)
- Train-on-synthetic → test-on-human transfer result

**What it's NOT**:
- Not a separate benchmark paper
- Not full taxonomy/community release
- Not the main contribution

---

## Method: CG-PRM

### Core Mechanism

**Data Interface**: Schema-constrained trace generation
- Teacher (Qwen2.5-VL-7B) outputs structured traces with explicit `grounding_ref` fields
- Uniform canonical format across CLEVR and DocVQA
- Automatic verification against ground truth (CLEVR) or OCR (DocVQA)

**Canonical Structured Trace Format**:
```json
{
  "steps": [
    {
      "step_id": 1,
      "step_type": "locate|read|relate|compute|answer",
      "step_text": "<natural language>",
      "grounding_ref": {
        "type": "object|span|box|region",
        "reference": "<explicit evidence pointer>",
        "value": "<extracted value>"
      },
      "is_grounded": true|false
    }
  ],
  "t_star": <divergence_step_id>
}
```

**Training**: First-divergence loss only
```
L = -log σ(r_{t*}^+ - r_{t*}^-)
```
- t*: first step where grounding differs between paired traces
- No downstream-step extension in core training (moved to ablation)

**Inference**: softmin aggregation
```
s_trace = -softmin_τ(r_t)
```

---

## ACED-Lite Evaluation

### Corruption Families (3 of 5)

| Family | Description | Example |
|--------|-------------|---------|
| **Object Swap** | Replace referenced object | "red circle" → "blue circle" (same answer) |
| **Spatial Shift** | Perturb location | "top-left" → "top-right" |
| **Hallucinated Evidence** | Reference non-existent object | "the clock shows 3pm" (no clock visible) |

### Human-Audited Subset (~100 samples)

**Purpose**: Validate synthetic → real transfer.

**Construction**:
1. Collect traces from running VLMs (Qwen2.5-VL-7B, LLaVA-1.6) on CLEVR/DocVQA
2. Manually identify "answer-correct but evidence-wrong" cases
3. Annotate first divergence point
4. Use as held-out test set (never in training)

**Size**: ~100 samples (feasible with 1-2 annotators in 3-4 days)

### Evaluation Protocol

| Experiment | Purpose |
|------------|---------|
| Step-level AUROC at t* | Primary: discrimination at divergence |
| Train-synthetic → test-human | Transfer: not just artifact |
| Leave-one-family-out | Generalization: not corruption-specific |
| Baselines (VisualPRM, VRPRM, text-only) | Comparison: improvement over SOTA |

---

## Validation Plan (4 Core Experiments)

### Experiment 1: CG-PRM vs. Baselines (Main Result)

**Purpose**: Show first-divergence supervision improves grounding discrimination.

**Setup**:
- Train CG-PRM on synthetic iso-answer pairs
- Evaluate on ACED-Lite (synthetic + human subsets)
- Baselines: VisualPRM, VRPRM, text-only PRM

**Metric**: Step-level AUROC at t*

**Expected**: +15-20% over baselines

---

### Experiment 2: Transfer (Synthetic → Human)

**Purpose**: Defang "synthetic artifact" objection.

**Setup**:
- Train on synthetic corruptions only
- Test on human-audited subset (no corruption exposure)

**Metric**: Human detection rate, AUROC drop

**Expected**: <10% AUROC drop, >55% human detection

---

### Experiment 3: Leave-One-Family-Out

**Purpose**: Show CG-PRM learns generalizable grounding.

**Setup**:
- Train on 2 families, test on 3rd

**Metric**: AUROC drop vs. in-family

**Expected**: <5% drop

---

### Experiment 4: First-Divergence vs. Pointwise (Ablation)

**Purpose**: Show divergence alignment is necessary.

**Setup**:
- Same data, different loss (first-divergence vs. pointwise)

**Metric**: AUROC at t*

**Expected**: +10% from alignment alone

---

## Compute Budget

| Phase | Days | GPU-hours |
|-------|------|-----------|
| Synthetic data generation (3 families) | 1-5 | 8 |
| Human audit (annotation) | 6-8 | 0 (manual) |
| CG-PRM training | 9-18 | 24 |
| Transfer + leave-one-out | 19-25 | 16 |
| Ablation + baselines | 26-32 | 12 |
| Paper writing | 33-40 | 0 |

**Total**: ~60 GPU-hours

---

## Timeline (40 Days)

| Days | Task | Deliverable |
|------|------|-------------|
| 1-5 | Synthetic corruption generation | 3 families |
| 6-8 | Human audit (100 samples) | Held-out test set |
| 9-18 | CG-PRM training | Checkpoint |
| 19-22 | Baseline evaluation (VisualPRM, VRPRM) | Comparison tables |
| 23-25 | Transfer experiment | Synthetic → human result |
| 26-28 | Leave-one-family-out | Generalization result |
| 29-32 | Ablations | First-divergence necessity |
| 33-40 | Paper writing | Final draft |

---

## Files to Create

### Method
- `cg_prm/losses/first_divergence_loss.py` — Core loss
- `cg_prm/data/schema_generator.py` — Trace generation
- `cg_prm/models/step_scorer.py` — 3B LoRA PRM

### Evaluation (ACED-Lite)
- `cg_prm/eval/construct_synthetic.py` — 3 corruption families
- `cg_prm/eval/human_audit.py` — Annotation interface
- `cg_prm/eval/aced_lite_metrics.py` — AUROC, transfer metrics

---

## Paper Title Options

| Title | Framing |
|-------|---------|
| "First-Divergence Iso-Answer Supervision for Multimodal PRMs" | Method-centered (recommended) |
| "Detecting Answer-Equivalent Grounding Failures in Multimodal PRMs" | Problem-centered |
| "ACED: A Benchmark for Answer-Controlled Evidence Divergence" | Benchmark-centered (NOT recommended for lean version) |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Human audit takes too long | MEDIUM | Limit to 100 samples, use undergrad annotators |
| Transfer result weak | HIGH | Use 2+ source model families to avoid generator-specific patterns |
| Baselines too strong | MEDIUM | Include text-only baseline as lower bound |
| First-divergence loss unstable | MEDIUM | Gradient clipping, warmup lambda |

---

## Why This Is the Right Scope

1. **Finishable in 40 days** — No full benchmark overhead
2. **Defends against "synthetic artifact"** — Human transfer + leave-one-out
3. **Method stays the story** — Benchmark is shield, not the paper
4. **Reusable artifact** — ACED-Lite can grow into full benchmark later
5. **Lower risk** — If transfer fails, still have method contribution

---

## Next Steps

1. **[ ] Construct synthetic corruptions** (3 families)
2. **[ ] Run human audit** (100 samples, 3-4 days)
3. **[ ] Implement first-divergence loss**
4. **[ ] Train CG-PRM + evaluate**

---

**Generated by**: research-refine pipeline (lean scoping)
**Codex review**: "Option B, but upgraded — model-centered with ACED-Lite shield"
**Verdict**: READY for implementation
