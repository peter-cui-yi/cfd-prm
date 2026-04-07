# Research Proposal: CG-PRM (Round 2 Revision)

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
- Backbone: 3B LoRA step scorer
- Data: Schema-constrained teacher generation, rejection sampling
- Human audit: Threshold calibration
- Venue: NeurIPS/ICLR

### Success Condition
Leave-one-family-out generalization + interventional grounding gap showing step-level discrimination.

---

## Technical Gap

### Where Baseline Breaks
VisualPRM/VRPRM use step-correctness from final answer checking. No supervision for answer-correct but evidence-wrong traces.

### Why Naive Fixes Fail
- More data, stronger models, prompting: don't create contrastive signal
- Wrong-answer negatives: reintroduce answer as shortcut

### Smallest Adequate Intervention
**First-divergence aligned step supervision** with schema-constrained traces.

---

## Contribution Focus

### Dominant Contribution
**First-divergence aligned iso-answer pairwise supervision with schema-constrained traces**

### Supporting Contributions
1. Interventional grounding gap metric (secondary probe)
2. Rejection sampling protocol with hardness filter diversity

### Explicit Non-contributions
- BoN reranking (application)
- General grounding detector
- Benchmark creation

---

## Proposed Method

### Complexity Budget

| Component | Status | Notes |
|-----------|--------|-------|
| Backbone: Qwen2.5-VL-3B | Frozen | LoRA step scorer |
| Schema-constrained teacher | **NEW** | Explicit grounding_ref fields |
| Training objective | L_fd only | Downstream extension moved to ablation |
| Inference aggregator | softmin | min as sensitivity analysis |
| Hardness filter | Multi-detector | Not tied to single classifier |

---

## Core Mechanism: Schema-Constrained First-Divergence Supervision

### Canonical Structured Trace Format

**Uniform across CLEVR and DocVQA**:

```json
{
  "image": "<image_input>",
  "question": "<task>",
  "steps": [
    {
      "step_id": 1,
      "step_type": "locate|read|relate|compute|answer",
      "step_text": "<natural language description>",
      "grounding_ref": {
        "type": "object|span|box|region",
        "reference": "<explicit evidence pointer>",
        "value": "<extracted value>"
      },
      "is_grounded": true|false,
      "error_type": "none|wrong_region|wrong_value|wrong_relation|irrelevant|correct_answer_wrong_evidence"
    }
  ],
  "final_answer": "<answer>",
  "t_star": null|<divergence_step_id>
}
```

### Schema-Constrained Teacher Generation

Instead of post-hoc extraction, **teacher outputs structured traces directly**:

1. Prompt template requests explicit `grounding_ref` fields
2. Teacher generates trace with schema slots filled
3. Automatic verification cross-checks `grounding_ref.reference` against:
   - CLEVR: scene metadata (objects, attributes, relations)
   - DocVQA: OCR output (spans, boxes)

**t* Identification** (unambiguous):
- First step where `is_grounded` differs between paired traces
- Schema field directly marks divergence point
- No parsing ambiguity

### Training Loss: L_fd Only

**Core loss** (first-divergence step):
```
L = -log σ(r_{t*}^+ - r_{t*}^-)
```

**Downstream-step extension** moved to ablation only:
```
L_downstream = λ Σ_{t>t*} -log σ(r_t^+ - r_t^-)  [ABLATION]
```

### Inference Aggregator: softmin Default

**Trace score**:
```
s_trace = -softmin_τ(r_t)  where τ is temperature
```

- Emphasizes worst step (grounding-critical)
- **min aggregator** treated as sensitivity analysis, not co-equal design

### Hardness Filter: Multi-Detector Diversity

**Problem**: Single detector filter creates selection bias toward negatives that beat that detector.

**Solution**: Use **ensemble of hardness checks**:

1. **Lexical overlap**: TF-IDF similarity with clean traces ≥ threshold
2. **Syntax diversity**: Parse tree depth distribution similar
3. **Step-type balance**: Each corruption family has balanced step-type coverage
4. **Text-only PRM baseline**: Cannot achieve > 75% AUROC (not 90% - less aggressive)

This prevents filter from selecting negatives tailored to one detector's weakness.

---

## VLM-Generated Free-Form Counterfactuals (Optional Extension)

For **10-20% of negatives**, use VLM-generated counterfactuals under constraints:

1. Prompt VLM: "Generate reasoning trace with same answer, different evidence grounding"
2. Schema extraction from free-form output
3. Reject if answer differs or grounding_ref missing

This adds natural-style negatives to templated families.

---

## Claim-Driven Validation Sketch

### Claim 1: Schema-constrained first-divergence improves step detection

**Experiment**: CG-PRM vs pointwise vs post-hoc extraction baseline

**Metric**: Step AUROC at t*

### Claim 2: Leave-one-family-out generalization

**Experiment**: Train 4 families, test 5th

**Metric**: AUROC drop

### Claim 3: Multi-detector filter reduces bias

**Experiment**: Compare single-detector vs multi-detector filtered negatives

**Metric**: Cross-corruptor AUROC, human-authored failure detection

---

## Must-run Ablations

1. L_fd only vs L_fd + downstream (training loss)
2. Schema-constrained vs post-hoc extraction (data construction)
3. softmin vs min (inference aggregator)
4. Single-detector vs multi-detector filter (hardness bias)
5. Each corruption family independently
6. Templatd-only vs VLM-generated mix (naturalness)

---

## Compute Estimate

| Phase | GPU-hours |
|-------|-----------|
| Schema-constrained generation | 8 |
| L_fd training | 24 |
| Leave-one-out (5 runs) | 16 |
| Ablations | 12 |
| Secondary probes | 8 |

**Total**: ~68 GPU-hours