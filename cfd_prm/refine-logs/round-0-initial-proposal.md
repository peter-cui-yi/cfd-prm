# Research Proposal: CG-PRM (Counterfactual Grounding Process Reward Model)

## Problem Anchor

### Bottom-line Problem
Current multimodal PRMs fail to detect **answer-correct but evidence-wrong** reasoning traces because their supervision conflates answer correctness with grounding quality.

### Must-solve Bottleneck
VisualPRM and VRPRM are trained with step-correctness supervision that correlates with final answers. When a trace reaches the right answer but uses wrong evidence at an intermediate step, these PRMs cannot distinguish it from a genuinely grounded trace. This creates a systematic false-acceptance problem.

### Non-goals
- Retraining base VLM reasoning policies
- Creating new benchmarks beyond DocVQA/CLEVR
- Building a general-purpose grounding detector (PRM is trace-level verifier)
- Proving "evidence necessity learning" (too strong, lacks causal evidence)

### Constraints
- Compute: 4xA800 GPUs, 40 days
- Backbone: 3B LoRA-trained PRM (Qwen2.5-VL-3B-Instruct)
- Data: Automated construction, minimal human annotation (100-200 audit samples)
- Venue: NeurIPS/ICLR level

### Success Condition
CG-PRM must show **leave-one-family-out generalization** (detect unseen corruption types) and **interventional calibration** (necessity gap metric) proving it distinguishes grounded from ungrounded traces even when answers match.

---

## Technical Gap

### Where Baseline Breaks
VisualPRM/VRPRM use step-correctness labels derived from final answer checking. For a trace that: (1) is fluent, (2) reaches correct answer, but (3) uses wrong evidence at step 3, the PRM has no supervision signal to reject it. The training data has zero contrastive examples holding answer fixed while varying grounding.

### Why Naive Fixes Fail
- **More data**: Adding more clean traces doesn't create answer-controlled contrast
- **Stronger models**: Larger PRMs still inherit the same supervision bias
- **Prompting**: Asking PRM to "check grounding" without training signal is unreliable
- **Outcome reward**: ORM tracks answer correctness, not process grounding

### Smallest Adequate Intervention
**Iso-answer pairwise training**: Create matched trace pairs that reach the same answer but differ in grounding quality. Train PRM with pairwise ranking loss so it must rank grounding quality rather than answer correctness.

### Frontier-native Alternative
Current approach is already frontier-native (VLM-based PRM, counterfactual negatives). The key innovation is the **pairing constraint** (iso-answer) rather than a new architecture.

### Core Technical Claim
> Iso-answer pairwise supervision with counterfactual grounding negatives forces a multimodal PRM to learn grounding discrimination by removing answer correctness as a shortcut.

### Required Evidence
1. Leave-one-family-out generalization (artifact control)
2. Human-authored grounding failure detection (natural error generalization)
3. Shallow lexical baseline fails (not detecting artifacts)
4. Interventional calibration metric shows necessity gap
5. Pointwise vs pairwise ablation (objective validation)

---

## Method Thesis

### One-sentence Thesis
We train a multimodal PRM on answer-controlled trace pairs so it must rank grounding quality rather than answer correctness.

### Why Smallest Adequate Intervention
Adding pairwise ranking loss on iso-answer pairs is the minimal change that directly addresses the bottleneck. No new architecture, no RL, no policy training.

### Why Timely
Current PRM literature (VisualPRM 2025, VRPRM 2025) uses step-correctness supervision. Pairwise ranking for PRMs exists in text domain (PPRM), but **iso-answer pairing for multimodal PRMs** is novel.

---

## Contribution Focus

### Dominant Contribution
**Iso-answer pairwise training for multimodal PRMs with counterfactual grounding negatives**

### Supporting Contribution
Interventional calibration metric (necessity gap) for evaluating PRM grounding sensitivity

### Explicit Non-contributions
- New reasoning architecture
- General grounding detector
- Benchmark creation (DocVQA/CLEVR only)
- "Evidence necessity learning" claim (too strong)

---

## Proposed Method

### Complexity Budget

| Component | Status | Notes |
|-----------|--------|-------|
| Backbone: Qwen2.5-VL-3B | Frozen | LoRA training only |
| Training objective | **NEW** | Pairwise ranking loss (replacing pointwise binary) |
| Iso-answer pair matching | **NEW** | Data construction logic |
| 5 corruption families | Reuse | Already implemented in cg-prm codebase |
| Interventional calibration | **NEW** | Evaluation metric |
| Cross-corruptor | Reuse | Already implemented |

### Tempting Additions Intentionally Not Used
- 7B PRM scale-up (deferred, not core claim)
- ChartQA extension (supplementary only)
- RL policy optimization (different paper)
- Dense evidence supervision (separate baseline)

### System Overview

```
Image + Question
    ↓
Teacher (7B) generates N candidate traces
    ↓
Automatic verification → Clean trace bank
    ↓
Counterfactual corruptor → 5 families of grounding negatives
    ↓
Iso-answer pair matching → Paired (grounded, ungrounded) traces
    ↓
CG-PRM (3B LoRA) → Pairwise ranking training
    ↓
Per-step scores + trace score → Best-of-N reranking
```

### Core Mechanism: Iso-Answer Pairwise Training

**Input**: Matched pair (trace_grounded, trace_ungrounded) where both reach same final answer

**Output**: Ranking score s(trace_grounded) > s(trace_ungrounded)

**Training Signal**:
```
L = -log(σ(s(grounded) - s(ungrounded)))
```

**Why This Is Main Novelty**:
- VisualPRM uses pointwise binary (step correct/incorrect)
- PPRM uses pairwise but without answer-controlled pairing
- CG-PRM combines: pairwise ranking + iso-answer constraint + counterfactual grounding negatives

### Pair Construction Logic

1. For each clean trace with correct answer:
2. Generate counterfactual with same answer but corrupted evidence (Family 5)
3. Also pair with wrong-answer counterfactuals as additional negatives
4. Report iso-answer coverage rate (fraction of dataset that survives matching)
5. Characterize selection bias by benchmark, answer type, reasoning length

### Interventional Calibration Metric

**Necessity Gap**: Difference in PRM score when grounding evidence is perturbed vs intact.

```
Gap = E[s(trace | evidence_intact)] - E[s(trace | evidence_perturbed)]
```

This metric tests whether PRM responds to grounding interventions, not just fluency.

### Training Plan

**Stage 1**: Build iso-answer pair dataset
- Clean traces from teacher
- Counterfactual generation (5 families)
- Pair matching with coverage analysis

**Stage 2**: Pairwise PRM training
- LoRA on 3B backbone
- Ranking loss on matched pairs
- Class balancing across corruption families

**Stage 3**: Artifact control experiments
- Leave-one-family-out training
- Human-authored grounding failures
- Shallow lexical baseline

### Failure Modes and Diagnostics

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Artifact detection | Leave-one-out fails | Use multiple paraphrase styles |
| Coverage bias | Low iso-answer survival | Report bias, add unconstrained pairs |
| Schema overfitting | Free-form evaluation drops | Tiered free-form protocol |
| Teacher-style bias | Cross-generator fails | Multiple generators in reranking |

### Novelty and Elegance Argument

**Closest Prior**: VisualPRM (step-correctness supervision), PPRM (text-only pairwise PRM)

**Exact Difference**: CG-PRM is first to use **iso-answer pairwise training with counterfactual grounding negatives** for multimodal PRMs. The pairing constraint removes answer correctness as shortcut, forcing grounding learning.

**Why Focused**: One mechanism (pairing constraint), one dominant claim, minimal architecture changes.

---

## Claim-Driven Validation Sketch

### Claim 1: Iso-answer pairwise training improves grounding detection on answer-correct but evidence-wrong traces

**Minimal Experiment**:
- Train CG-PRM (pairwise) vs VisualPRM-style baseline (pointwise)
- Evaluate on held-out traces: correct-answer + wrong-evidence

**Baselines**:
1. Pointwise PRM with same data (matched compute)
2. VisualPRM (if available checkpoint)
3. Shallow lexical detector (text-only, no image)

**Metric**: Step-level AUROC on answer-correct but evidence-wrong subset

**Expected Evidence**: CG-PRM AUROC > pointwise + shallow baseline, with bootstrap CI

### Claim 2: Leave-one-family-out generalization shows artifact control

**Minimal Experiment**:
- Train on 4 corruption families, test on 5th
- Repeat for each family (5 runs)

**Baseline**: Train on all 5 families, test on all (overfitting comparison)

**Metric**: AUROC drop from full-family to leave-one-out

**Expected Evidence**: Moderate drop (not catastrophic) indicates real grounding learning

### Claim 3: Interventional calibration metric (necessity gap) measures grounding sensitivity

**Minimal Experiment**:
- Compute necessity gap on intervention tests
- Compare CG-PRM vs pointwise baseline

**Metric**: Gap magnitude and consistency

**Expected Evidence**: CG-PRM gap > baseline gap

---

## Experiment Handoff Inputs

### Must-prove Claims
1. Iso-answer pairwise > pointwise on answer-correct/evidence-wrong
2. Leave-one-family-out generalization (artifact control)
3. Human-authored grounding failures detected (natural error generalization)

### Must-run Ablations
1. Pairwise vs pointwise (matched data, matched compute)
2. Iso-answer vs unconstrained pairs
3. Each corruption family independently
4. Mean vs min-sensitive aggregation
5. Canonical vs free-form traces

### Critical Datasets
- CLEVR (low-noise causal anchor)
- DocVQA (realistic visual-text grounding)
- Human-written grounding challenge set (200 pairs)

### Highest-risk Assumptions
1. Counterfactual negatives are genuinely hard (not trivial artifacts)
2. Iso-answer coverage is sufficient (selection bias limited)
3. Pairwise ranking converges on 3B backbone

---

## Compute & Timeline Estimate

| Phase | Days | GPU-hours | Key Deliverable |
|-------|------|-----------|-----------------|
| Pair construction | 1-5 | 8 | Iso-answer pair dataset, coverage stats |
| Pairwise training | 6-10 | 24 | CG-PRM v1 checkpoint |
| Leave-one-out exp | 11-15 | 16 | Generalization results |
| Pointwise vs pairwise | 16-20 | 12 | Objective ablation |
| Human challenge set | 21-25 | 4 | Gold evaluation set |
| Calibration metrics | 26-30 | 8 | Necessity gap analysis |
| Free-form robustness | 31-35 | 8 | Schema robustness |
| Paper writing | 36-40 | 0 | Final paper |

**Total GPU-hours**: ~80 (within 4xA800 budget)