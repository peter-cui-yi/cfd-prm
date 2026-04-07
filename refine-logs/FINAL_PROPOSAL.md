# FINAL PROPOSAL: CG-PRM

## First-Divergence Iso-Answer Supervision for Multimodal Process Reward Models

**Version**: Refined v2.0 (READY state)
**Target Venue**: NeurIPS/ICLR
**Score**: 9.1/10 (GPT-5.4 review)
**Status**: Ready for implementation

---

## Problem Anchor

### Bottom-line Problem
Current multimodal PRMs fail to detect **answer-correct but evidence-wrong** reasoning traces because their supervision conflates answer correctness with grounding quality.

### Must-solve Bottleneck
VisualPRM and VRPRM use step-correctness supervision correlated with final answers. When a trace reaches the right answer but uses wrong evidence at an intermediate step, these PRMs cannot distinguish it from genuinely grounded traces.

### Non-goals
- Retraining base VLM reasoning policies
- Creating new benchmarks beyond DocVQA/CLEVR
- General grounding detector
- "Evidence necessity learning" claim
- Best-of-N reranking as method contribution

### Constraints
- Compute: 4xA800 GPUs, 40 days
- Backbone: 3B LoRA step scorer (Qwen2.5-VL-3B)
- Venue: NeurIPS/ICLR

### Success Condition
Leave-one-family-out generalization + human-authored failure detection showing step-level discrimination on answer-correct but evidence-wrong traces.

---

## Method Thesis

**One-sentence**: We train a step-level PRM on first-divergence points of schema-constrained iso-answer trace pairs.

**Why this is the smallest adequate intervention**: Supervising only the divergence point is the minimal signal that directly addresses the bottleneck. No full-trace ranking complexity, no wrong-answer shortcut leakage.

**Why timely**: Current PRM literature (VisualPRM 2025, VRPRM 2025) uses step-correctness supervision. First-divergence aligned supervision for multimodal PRMs is novel.

---

## Contribution Focus

### Dominant Contribution
**First-divergence aligned iso-answer pairwise supervision with schema-constrained traces for multimodal PRMs**

### Supporting Contribution
Interventional grounding gap metric (evaluation probe)

### Non-contributions (Sanity Checks / Appendix)
- Multi-detector hardness filter (dataset construction detail)
- VLM-generated free-form counterfactuals (robustness appendix)
- BoN reranking (application, not method)

---

## Proposed Method

### Core Mechanism

**Data Interface**: Schema-constrained trace generation
- Teacher (Qwen2.5-VL-7B) outputs structured traces with explicit `grounding_ref` fields
- Uniform canonical format across CLEVR and DocVQA
- Automatic verification against ground truth metadata (CLEVR) or OCR output (DocVQA)

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
- min aggregator as sensitivity analysis (appendix)

### Sanity Checks (Not Method Claims)

**Hardness filter**: Multi-detector ensemble
- Lexical overlap (TF-IDF), syntax diversity, step-type balance
- Text-only PRM baseline (prevent trivial negatives)

**VLM-generated negatives**: 10-20% mix (appendix robustness)

---

## Validation (Three Core Experiments)

### Experiment 1: First-divergence vs Pointwise
- Train CG-PRM (first-divergence) vs pointwise baseline
- Matched data, matched compute budget
- **Metric**: Step-level AUROC at t* on answer-correct/evidence-wrong traces

### Experiment 2: Schema-constrained vs Post-hoc
- Compare schema generation vs extraction baseline
- **Metric**: t* identification accuracy, leave-one-family-out AUROC

### Experiment 3: Leave-one-family-out + Human-authored
- Train on 4 corruption families, test on 5th (artifact control)
- Test on human-written grounding failures (natural error generalization)
- **Metric**: AUROC drop, human failure detection rate

---

## Core Ablations (Three Only)

| Ablation | Question |
|----------|----------|
| First-divergence vs pointwise | Is alignment necessary? |
| Schema-constrained vs post-hoc | Is structured generation necessary? |
| Iso-answer only vs shortcut-leaking | Does answer-mixing reintroduce shortcut? |

---

## Compute Budget

| Phase | Days | GPU-hours |
|-------|------|-----------|
| Schema-constrained generation | 1-5 | 8 |
| First-divergence training | 6-10 | 24 |
| Leave-one-out (5 runs) | 11-15 | 16 |
| Core ablations (3) | 16-20 | 12 |
| Human challenge set evaluation | 21-25 | 4 |
| Paper writing | 26-40 | 0 |

**Total**: ~64 GPU-hours (within budget)

---

## Paper Positioning

**Title**: First-Divergence Iso-Answer Supervision for Multimodal Process Reward Models

**Abstract Structure**:
1. Problem: answer-correct but evidence-wrong traces evade current PRMs
2. Gap: supervision conflates answer correctness with grounding quality
3. Method: schema-constrained traces, first-divergence pairs, ranking loss
4. Evidence: leave-one-family-out generalization, human-authored failures detected

**One-line Pitch**:
> We force a multimodal PRM to learn grounding discrimination by supervising only the divergence point of answer-controlled trace pairs.

---

## Novelty Positioning

| Claim | Novelty | Closest Prior | Delta |
|-------|---------|---------------|-------|
| First-divergence iso-answer supervision | HIGH | VisualPRM (step-correctness), PPRM (text pairwise) | First multimodal PRM with divergence-aligned + answer-controlled supervision |
| Schema-constrained generation | MEDIUM | Existing trace schemas | Explicit grounding_ref for verification |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Data yield low | MEDIUM | Increase teacher sampling, report coverage |
| Verification noise | MEDIUM | Human audit for threshold calibration |
| Artifact detection | LOW | Leave-one-out, human-authored failures, multi-detector filter |

---

## Generated by

- Pipeline: research-lit → idea-creator → novelty-check → research-review → research-refine
- Model: GPT-5.4 xhigh via Codex MCP
- Rounds: 4 (7.3 → 8.5 → 8.8 → 9.1)
- Verdict: READY