# Research Proposal: CG-PRM (Round 1 Revision)

## Problem Anchor

### Bottom-line Problem
Current multimodal PRMs fail to detect **answer-correct but evidence-wrong** reasoning traces because their supervision conflates answer correctness with grounding quality.

### Must-solve Bottleneck
VisualPRM and VRPRM use step-correctness supervision correlated with final answers. When a trace reaches the right answer but uses wrong evidence at an intermediate step, these PRMs cannot distinguish it from genuinely grounded traces.

### Non-goals
- Retraining base VLM reasoning policies
- Creating new benchmarks beyond DocVQA/CLEVR
- General grounding detector (PRM is trace-level verifier)
- "Evidence necessity learning" claim (too strong, lacks causal evidence)
- **Best-of-N reranking as method contribution** (demoted to application)

### Constraints
- Compute: 4xA800 GPUs, 40 days
- Backbone: 3B LoRA-trained step scorer (Qwen2.5-VL-3B-Instruct)
- Data: Automated construction with rejection sampling
- Human audit: 100-200 samples for threshold calibration (not just reporting)
- Venue: NeurIPS/ICLR level

### Success Condition
CG-PRM must show **leave-one-family-out generalization** and **interventional grounding gap** proving it distinguishes grounded from ungrounded traces at the step level.

---

## Technical Gap

### Where Baseline Breaks
VisualPRM/VRPRM use step-correctness labels derived from final answer checking. For a trace that reaches correct answer but uses wrong evidence at step t*, the PRM has no supervision to reject it. No contrastive examples holding answer fixed while varying grounding.

### Why Naive Fixes Fail
- **More data**: Adding clean traces doesn't create answer-controlled contrast
- **Stronger models**: Larger PRMs inherit same supervision bias
- **Prompting**: Unreliable without training signal
- **Outcome reward**: Tracks answer correctness, not process grounding
- **Wrong-answer negatives**: Reintroduces answer as shortcut

### Smallest Adequate Intervention
**First-divergence aligned step supervision**: For each iso-answer pair, identify the first step where grounding diverges (t*). Train step scorer on that specific step's reward difference, not on full-trace ranking.

### Core Technical Claim
> First-divergence aligned iso-answer pairs force a step-level PRM to learn grounding discrimination by supervising only the divergence point, removing answer correctness as a shortcut.

---

## Method Thesis

### One-sentence Thesis
We train a step-level PRM on first-divergence points of iso-answer trace pairs, where grounding quality differs but the final answer is identical.

### Why Smallest Adequate Intervention
Supervising only the divergence point is the minimal signal that directly addresses the bottleneck. No full-trace ranking complexity, no wrong-answer shortcut leakage.

### Why Timely
Current PRMs use step-correctness supervision. First-divergence aligned supervision for multimodal PRMs is novel and directly targets the answer-correct/evidence-wrong failure mode.

---

## Contribution Focus

### Dominant Contribution
**First-divergence aligned iso-answer pairwise supervision for multimodal step-level PRMs**

### Supporting Contributions
1. Interventional grounding gap metric (secondary evaluation probe)
2. Rejection sampling protocol for same-answer counterfactual negatives

### Explicit Non-contributions
- Best-of-N reranking (application, not method)
- General grounding detector
- Benchmark creation
- "Evidence necessity learning" claim

---

## Proposed Method

### Complexity Budget

| Component | Status | Notes |
|-----------|--------|-------|
| Backbone: Qwen2.5-VL-3B | Frozen | LoRA step scorer only |
| Training objective | **NEW** | First-divergence step ranking loss |
| Iso-answer pair matching | **NEW** | Rejection sampling, no unconstrained |
| 5 corruption families | Reuse | Already implemented |
| Interventional grounding gap | **NEW** | Secondary evaluation probe |
| Wrong-answer negatives | **DELETED** | Auxiliary analysis only |

### Tempting Additions Intentionally Not Used
- Wrong-answer negatives in core training (reintroduces shortcut)
- Full-trace ranking loss (less precise than step-level)
- BoN reranking as method contribution (application only)
- Unconstrained pairs when coverage low (dilutes claim)
- 7B PRM scale-up (deferred)

---

## Core Mechanism: First-Divergence Aligned Step Supervision

### Pair Construction

For each clean grounded trace with externally verified evidence:

1. **Generate same-answer counterfactual via rejection sampling**:
   - Corrupt evidence at step t
   - Verify final answer unchanged
   - Reject if answer differs or if corruption is trivially detectable

2. **Align pairs at first divergence point**:
   - Shared prefix: steps 1..t*-1 are identical
   - Divergence: step t* is grounded in positive, ungrounded in negative
   - Downstream: steps t*+1..T may differ

3. **No mixing of unconstrained pairs**:
   - Core training uses ONLY iso-answer pairs
   - Wrong-answer pairs kept for auxiliary robustness analysis (not main loss)

### Step Scorer Architecture

**Input**: `(image, question, step_prefix, step_t, step_context)`

**Output**: Scalar step reward `r_t ∈ [0, 1]`

**Training Signal** (first-divergence loss):
```
L_fd = -log σ(r_{t*}^+ - r_{t*}^-)
```

Optionally extend to downstream steps:
```
L_total = L_fd + λ Σ_{t>t*} -log σ(r_t^+ - r_t^-)
```

### Trace Score at Inference (NOT Training)

**Definition**: Trace score derived from step rewards via softmin:
```
s_trace = -softmin_t(r_t)  (emphasizes worst step)
```

Or via min:
```
s_trace = min_t(r_t)
```

This aggregation is used only for downstream applications (BoN reranking), NOT for training.

### Positive Trace Verification

Restrict positives to **externally checkable evidence references**:

| Benchmark | Checkable Evidence |
|-----------|--------------------|
| CLEVR | Object identity, attributes, spatial relations (ground truth metadata) |
| DocVQA | OCR spans, bounding boxes, key-value pairs |

**Verification protocol**:
1. Extract evidence reference from step grounding_ref field
2. Cross-check against ground truth or OCR output
3. Accept only if reference matches verified source

**Human audit role**:
- Calibrate acceptance thresholds (not just reporting)
- 100-200 samples to tune verification strictness
- Measure false-positive rate in clean trace bank

### Counterfactual Generation via Rejection Sampling

For each corruption family:

1. Generate candidate counterfactual trace
2. Check: final answer matches original
3. Check: corruption is non-trivial (passes hardness filter)
4. Accept only if both checks pass
5. Discard candidates that fail rejection criteria

**Hardness filter**:
- Text-only classifier cannot distinguish with > 90% accuracy
- Lexical statistics (length, word overlap) similar to clean traces

---

## Failure Modes and Diagnostics

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Shortcut leakage | Leave-one-out fails | Rejection sampling, no wrong-answer mix |
| Coverage too low | Report iso-answer survival rate | Increase teacher sampling, relax strictness |
| Artifact detection | Shallow baseline succeeds | Hardness filter, paraphrase diversity |
| Teacher-style bias | Cross-generator fails | Multiple generators in evaluation |

---

## Claim-Driven Validation Sketch

### Claim 1: First-divergence aligned supervision improves step-level grounding detection

**Minimal Experiment**:
- Train CG-PRM (first-divergence) vs pointwise baseline
- Evaluate on answer-correct but evidence-wrong traces

**Baselines**:
1. Pointwise step PRM (matched data, matched compute)
2. Shallow lexical detector (text-only, no image)
3. Full-trace pairwise ranking (ablation of divergence alignment)

**Metric**: Step-level AUROC at divergence point t*

### Claim 2: Leave-one-family-out generalization shows artifact control

**Minimal Experiment**:
- Train on 4 families, test on 5th
- Repeat 5 times

**Metric**: AUROC drop vs full-family training

### Claim 3: Interventional grounding gap measures sensitivity

**Secondary Probe** (not method contribution):
- Compute gap when evidence is perturbed vs intact
- Compare CG-PRM vs baseline

**Metric**: Gap magnitude

---

## Experiment Handoff Inputs

### Must-prove Claims
1. First-divergence > pointwise on answer-correct/evidence-wrong steps
2. Leave-one-family-out generalization (artifact control)
3. Human-authored grounding failures detected

### Must-run Ablations
1. First-divergence vs full-trace pairwise (alignment matters)
2. Iso-answer only vs mixed wrong-answer (shortcut leakage)
3. Rejection sampling vs naive counterfactuals
4. Each corruption family independently
5. Softmin vs min aggregation (inference)

### Critical Datasets
- CLEVR (externally verified object/attribute evidence)
- DocVQA (OCR-verified span/box evidence)
- Human-written grounding failures (200 pairs)

---

## Compute & Timeline Estimate

| Phase | Days | GPU-hours |
|-------|------|-----------|
| Positive verification + rejection sampling setup | 1-5 | 8 |
| First-divergence training | 6-10 | 24 |
| Leave-one-out experiments | 11-15 | 16 |
| Ablations (alignment, shortcut, rejection) | 16-20 | 12 |
| Human challenge set | 21-25 | 4 |
| Secondary probes | 26-30 | 8 |
| Paper writing | 31-40 | 0 |

**Total**: ~72 GPU-hours