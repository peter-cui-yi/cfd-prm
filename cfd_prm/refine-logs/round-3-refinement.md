# Research Proposal: CG-PRM (Round 3 Final)

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
- Venue: NeurIPS/ICLR

### Success Condition
Leave-one-family-out generalization + human-authored failure detection showing step-level discrimination.

---

## Method Thesis

**One-sentence**: We train a step-level PRM on first-divergence points of schema-constrained iso-answer trace pairs.

---

## Contribution Focus

### Dominant Contribution
**First-divergence aligned iso-answer pairwise supervision with schema-constrained traces for multimodal PRMs**

### Supporting Contribution
Interventional grounding gap metric (evaluation probe)

### Non-contributions (Sanity Checks / Appendix)
- Multi-detector hardness filter (dataset construction detail)
- VLM-generated free-form counterfactuals (robustness appendix)
- BoN reranking (application)

---

## Proposed Method

### Core Mechanism (Single-threaded)

**Data Interface**: Schema-constrained trace generation
- Teacher outputs structured traces with explicit `grounding_ref` fields
- Uniform format across CLEVR/DocVQA
- Automatic verification against ground truth/OCR

**Training**: First-divergence loss only
```
L = -log σ(r_{t*}^+ - r_{t*}^-)
```
- t*: first step where grounding differs
- No downstream-step extension in core training

**Inference**: softmin aggregation
```
s_trace = -softmin_τ(r_t)
```
- min as sensitivity analysis (appendix)

### Sanitity Checks (Not Method Claims)

**Hardness filter**: Multi-detector ensemble for dataset quality
- Lexical, syntax, step-type balance, text-only PRM baseline
- Sanity check: prevents trivial negatives

**VLM-generated negatives**: 10-20% mix for naturalness
- Robustness analysis in appendix, not core method

---

## Validation (Three Core Experiments)

### Experiment 1: First-divergence vs pointwise
- Train CG-PRM vs pointwise baseline (matched data/compute)
- Metric: Step AUROC at t* on answer-correct/evidence-wrong traces

### Experiment 2: Schema-constrained vs post-hoc
- Compare schema generation vs extraction baseline
- Metric: t* identification accuracy, downstream generalization

### Experiment 3: Leave-one-family-out + human-authored
- Train on 4 corruption families, test on 5th
- Test on human-written grounding failures
- Metric: AUROC drop, human failure detection rate

---

## Core Ablations (Three Only)

1. **First-divergence vs pointwise** — is alignment necessary?
2. **Schema-constrained vs post-hoc** — is structured generation necessary?
3. **Iso-answer only vs shortcut-leaking** — does answer-mixing reintroduce shortcut?

---

## Paper Positioning

**Title**: First-Divergence Iso-Answer Supervision for Multimodal Process Reward Models

**Abstract Structure**:
1. Problem: answer-correct but evidence-wrong traces
2. Gap: current PRMs conflate answer correctness with grounding
3. Method: schema-constrained traces, first-divergence pairs, ranking loss
4. Evidence: leave-one-out generalization, human-authored failures detected

**One-line Pitch**:
> We force a multimodal PRM to learn grounding discrimination by supervising only the divergence point of answer-controlled trace pairs.