# FINAL PROPOSAL: CG-PRM (Benchmark-Centered)

## ACED: A Benchmark for Answer-Controlled Evidence Divergence in Multimodal Process Reward Models

**Version**: Refined v3.0 (Benchmark-Centered)
**Target Venue**: NeurIPS/ICLR
**Score**: 9.1/10 (GPT-5.4 review) → Pending re-review with benchmark focus
**Status**: Ready for implementation

---

## Problem Anchor

### Bottom-line Problem
**Current multimodal PRMs cannot distinguish answer-equivalent but evidence-divergent traces.** When a model reaches the right answer but uses wrong visual grounding at intermediate steps, existing PRMs (VisualPRM, VRPRM) assign similar scores to both correct and flawed reasoning.

### Must-solve Bottleneck
1. **Supervision conflation**: Step-correctness labels are correlated with final answers, not grounding fidelity
2. **No diagnostic benchmark**: Existing evaluation (BoN accuracy, step AUROC) doesn't isolate this failure mode
3. **Synthetic artifact risk**: VLM-generated corruptions may teach PRMs to detect generation patterns, not grounding failures

### Non-goals
- Retraining base VLM reasoning policies
- General vision-language grounding detector
- Best-of-N reranking as main contribution
- "Solving faithfulness" — own the specific failure mode

### Constraints
- Compute: 4xA800 GPUs, 40 days
- Backbone: 3B LoRA step scorer (Qwen2.5-VL-3B)
- Venue: NeurIPS/ICLR

### Success Condition
1. **Benchmark**: ACED shows existing PRMs fail on answer-controlled evidence divergence (AUROC near random)
2. **Method**: CG-PRM achieves significant improvement on ACED while maintaining generalization
3. **Human validation**: Human-audited subset confirms synthetic corruptions reflect real failures

---

## Core Contribution: Benchmark + Method

### Primary Contribution: ACED Benchmark

**ACED** (Answer-Controlled Evidence Divergence) is the first benchmark specifically designed to evaluate whether PRMs can detect grounding failures when answers are identical.

**Construction**:
- **Synthetic corruptions** (5 families): Systematic grounding perturbations with answer preserved
- **Human-audited set** (200-300 samples): Manually verified answer-equivalent, evidence-divergent pairs
- **First-divergence annotation**: For each pair, the exact step where grounding diverges is labeled

**Evaluation Protocol**:
- Step-level AUROC at t* (first divergence point)
- Leave-one-family-out generalization (train on 4, test on 5th)
- Human failure detection rate (corruption-free, natural errors)

**Why this is the center**:
- Existing PRM evaluation (BoN accuracy, Math-500, etc.) conflates answer correctness with process quality
- ACED isolates the grounding discrimination capability
- Provides diagnostic value beyond "our PRM wins"

### Secondary Contribution: CG-PRM Method

**One-sentence**: We train a step-level PRM on first-divergence points of schema-constrained iso-answer trace pairs.

**Why it fits the benchmark**:
- First-divergence loss directly targets ACED's evaluation metric
- Iso-answer pairing removes answer correctness as a shortcut
- Schema-constrained traces enable automatic divergence point identification

---

## Method: CG-PRM

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

---

## ACED Benchmark Construction

### Corruption Families (5 Total)

| Family | Description | Example |
|--------|-------------|---------|
| **Object Swap** | Replace referenced object with different one | "red circle" → "blue circle" (same answer via different reasoning) |
| **Spatial Shift** | Perturb location references | "top-left" → "top-right" |
| **Attribute Corruption** | Wrong color/size/material attribute | "3 apples" with reasoning counting oranges |
| **Hallucinated Evidence** | Reference non-existent object | "the clock shows 3pm" when no clock visible |
| **Shortcut Reasoning** | Correct answer via irrelevant path | Answer from question text, not image |

### Human-Audited Subset

**Purpose**: Validate that synthetic corruptions reflect real failure modes, not generation artifacts.

**Construction**:
1. Collect traces from running VLMs (Qwen2.5-VL, LLaVA) on CLEVR/DocVQA
2. Manually identify "answer-correct but evidence-wrong" cases
3. Annotate first divergence point
4. Release as held-out evaluation set (not used in training)

**Size**: 200-300 samples (feasible with undergraduate annotators)

### Evaluation Metrics

| Metric | Purpose |
|--------|---------|
| **Step-level AUROC at t*** | Primary: can PRM discriminate at divergence point? |
| **Leave-one-family-out AUROC** | Generalization: does PRM learn corruption artifacts? |
| **Human failure detection** | Real-world: does synthetic → real transfer? |
| **Calibration error** | Reliability: do scores reflect actual grounding quality? |

---

## Validation Plan

### Experiment 1: ACED Baseline (Diagnostic)

**Purpose**: Show existing PRMs fail on answer-controlled evidence divergence.

**Setup**:
- Evaluate VisualPRM, VRPRM on ACED (synthetic + human subsets)
- Compare to random, text-only baseline

**Expected**: AUROC near 0.5-0.6 (little discrimination)

**Claim**: "Current PRMs cannot distinguish answer-equivalent but evidence-divergent traces"

---

### Experiment 2: CG-PRM vs. Pointwise (Main Result)

**Purpose**: Show first-divergence supervision improves grounding discrimination.

**Setup**:
- Train CG-PRM (first-divergence) vs. pointwise baseline (same data, different loss)
- Matched compute budget, same backbone

**Metric**: Step-level AUROC at t* on ACED

**Expected**: +15-20% AUROC improvement

---

### Experiment 3: Leave-One-Family-Out + Human Transfer

**Purpose**: Show CG-PRM learns generalizable grounding, not corruption artifacts.

**Setup**:
- Train on 4 corruption families, test on 5th
- Test on human-audited subset (no corruption exposure)

**Metric**: AUROC drop, human failure detection rate

**Expected**: <5% AUROC drop, >60% human detection

---

### Experiment 4: Downstream Value (Application)

**Purpose**: Show ACED discrimination translates to real improvements.

**Setup**:
- Best-of-N reranking with CG-PRM vs. VisualPRM
- Standard benchmarks (MathVista, MathVision)

**Expected**: Modest gains (2-5%), confirming ACED is complementary to existing evals

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
| ACED synthetic construction | 1-5 | 8 |
| Human audit (MTurk/undergrad) | 6-10 | 0 (manual) |
| CG-PRM training | 11-15 | 24 |
| Leave-one-out (5 runs) | 16-20 | 16 |
| Core ablations (3) | 21-25 | 12 |
| Downstream evaluation | 26-30 | 4 |
| Paper writing | 31-40 | 0 |

**Total**: ~64 GPU-hours (within budget)

---

## Paper Positioning

**Title**: ACED: A Benchmark for Answer-Controlled Evidence Divergence in Multimodal Process Reward Models

**Alternative**: "Current Multimodal PRMs Cannot Detect Answer-Equivalent Grounding Failures"

**Abstract Structure**:
1. **Problem**: Answer-correct but evidence-wrong traces evade detection
2. **Gap**: No benchmark isolates this; existing PRMs conflate answer + process
3. **Contribution 1**: ACED benchmark (synthetic + human-verified)
4. **Contribution 2**: CG-PRM method (first-divergence supervision)
5. **Evidence**: Existing PRMs fail on ACED; CG-PRM improves + generalizes

**One-line Pitch**:
> We introduce ACED, the first benchmark to isolate grounding discrimination from answer correctness, and show current PRMs fail while our first-divergence method succeeds.

**Narrative Shift**:
- **Before**: "We propose a better PRM objective"
- **After**: "We expose a failure mode, build a benchmark for it, and show how to fix it"

---

## Novelty Positioning

| Claim | Novelty | Closest Prior | Delta |
|-------|---------|---------------|-------|
| ACED benchmark (answer-controlled evidence divergence) | HIGH | MagiC (separates answer/reasoning/grounding) | First to isolate answer-equivalent grounding failures with first-divergence annotation |
| First-divergence iso-answer supervision | HIGH | VisualPRM (step-correctness), PPRM (text pairwise) | First multimodal PRM with divergence-aligned + answer-controlled supervision |
| Schema-constrained trace generation | MEDIUM | Existing trace schemas | Explicit grounding_ref for verification |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Synthetic corruption artifacts | HIGH | Human-audited subset; show transfer |
| Data yield low | MEDIUM | Increase teacher sampling, report coverage |
| Downstream gains minimal | LOW | Frame ACED as diagnostic, not replacement |
| Concurrent benchmark release | MEDIUM | Emphasize first-divergence annotation + method |

---

## Related Work (Key Differentiators)

| Work | Approach | Limitation (for our purpose) |
|------|----------|------------------------------|
| VisualPRM (2025) | Step-correctness supervision | Conflates answer + grounding |
| VRPRM (2025) | Data-efficient PRM | Same supervision issue |
| PPRM (ICLR 2026) | Pairwise PRM (text-only) | Not multimodal, no divergence alignment |
| MagiC (OpenReview) | Separates answer/reasoning/grounding | No process reward, no first-divergence |
| Difference Feedback (2026) | Contrastive feedback | Not answer-controlled, no grounding focus |

---

## Timeline

| Days | Task | Deliverable |
|------|------|-------------|
| 1-5 | ACED synthetic construction (5 families) | Corruption dataset |
| 6-10 | Human audit (MTurk/undergrad) | Held-out evaluation set |
| 11-15 | CG-PRM training | First checkpoint |
| 16-20 | Leave-one-family-out experiments | Generalization results |
| 21-25 | Core ablations + baselines | Main result tables |
| 26-30 | Downstream evaluation (BoN) | Application results |
| 31-40 | Paper writing | Final paper |

---

## Files to Create/Modify

### Benchmark Construction
- `aced/benchmark/construct_synthetic.py` — Generate 5 corruption families
- `aced/benchmark/human_audit.py` — Annotation interface + quality control
- `aced/benchmark/evaluate.py` — ACED evaluation protocol

### Method
- `cg_prm/trainer/first_divergence_loss.py` — Core loss implementation
- `cg_prm/data/schema_generator.py` — Schema-constrained trace generation
- `cg_prm/models/step_scorer.py` — 3B LoRA PRM

### Evaluation
- `cg_prm/eval/aced_metrics.py` — Step-level AUROC, calibration
- `cg_prm/eval/leave_one_out.py` — Family generalization test

---

## Generated by

- Pipeline: research-lit → idea-creator → novelty-check → research-review → research-refine
- Model: GPT-5.4 xhigh via Codex MCP
- Rounds: 4 (7.3 → 8.5 → 8.8 → 9.1)
- **Codex review**: "Make the benchmark the center of the paper"
- **Verdict**: READY (v3.0 with benchmark-centered framing)
