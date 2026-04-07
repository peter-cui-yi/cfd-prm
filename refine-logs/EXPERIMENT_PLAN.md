# EXPERIMENT PLAN: CG-PRM

## First-Divergence Iso-Answer Supervision for Multimodal PRMs

**Version**: 1.0
**Created**: 2026-03-30
**Status**: Ready for Execution
**Budget**: 4xA800 GPUs, 40 days (~80 GPU-hours total)

---

## Overview

### Dominant Contribution
First-divergence aligned iso-answer pairwise supervision with schema-constrained traces

### Three Core Experiments
1. **E1**: First-divergence vs pointwise (alignment necessity)
2. **E2**: Schema-constrained vs post-hoc (generation necessity)
3. **E3**: Leave-one-family-out + human-authored (artifact control)

### Three Core Ablations
1. **A1**: First-divergence vs pointwise
2. **A2**: Schema-constrained vs post-hoc
3. **A3**: Iso-answer only vs shortcut-leaking

---

## Part 1: Data Construction

### 1.1 Schema-Constrained Teacher Generation

**Model**: Qwen2.5-VL-7B-Instruct
**GPUs**: 1x A800
**Time**: ~8 hours

**Prompt Template** (DocVQA):
```
You are a document reasoning assistant. Analyze the document and answer the question.

Output your reasoning as a JSON trace with the following structure:
{
  "steps": [
    {
      "step_id": 1,
      "step_type": "locate|read|relate|compute|answer",
      "step_text": "Natural language description of this step",
      "grounding_ref": {
        "type": "span|box|region",
        "reference": "Exact OCR span or bounding box coordinates",
        "value": "The extracted value from evidence"
      }
    }
  ],
  "final_answer": "Your answer"
}

Question: {question}
```

**Prompt Template** (CLEVR):
```
You are a visual reasoning assistant. Analyze the image and answer the question.

Output your reasoning as a JSON trace:
{
  "steps": [
    {
      "step_id": 1,
      "step_type": "locate|identify|relate|compute|answer",
      "step_text": "Natural language description",
      "grounding_ref": {
        "type": "object|region|attribute",
        "reference": "Object ID, spatial region, or attribute name",
        "value": "Extracted value"
      }
    }
  ],
  "final_answer": "Your answer"
}

Question: {question}
```

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| Temperature | 0.7 |
| Top-p | 0.9 |
| Max tokens | 1024 |
| Samples per example | 5 (for diversity) |

**Output**:
- `data/clevr/clean_traces.json` (~10K traces)
- `data/docvqa/clean_traces.json` (~15K traces)

### 1.2 Automatic Verification

**Verification Rules** (CLEVR):
```python
def verify_clevr_step(step, scene_metadata):
    """Verify grounding_ref against CLEVR ground truth."""
    ref = step["grounding_ref"]

    if ref["type"] == "object":
        # Check object exists in scene
        obj_id = ref["reference"]
        return obj_id in scene_metadata["objects"]

    elif ref["type"] == "attribute":
        # Check attribute value matches
        obj_id, attr = parse_reference(ref["reference"])
        expected = scene_metadata["objects"][obj_id][attr]
        return ref["value"] == expected

    elif ref["type"] == "relation":
        # Check spatial relation holds
        return verify_relation(ref, scene_metadata)
```

**Verification Rules** (DocVQA):
```python
def verify_docvqa_step(step, ocr_output):
    """Verify grounding_ref against OCR."""
    ref = step["grounding_ref"]

    if ref["type"] == "span":
        # Check span exists in OCR
        span_text = ref["reference"]
        return span_text in ocr_output["text"]

    elif ref["type"] == "box":
        # Check bounding box overlaps with OCR regions
        box = parse_box(ref["reference"])
        return has_ocr_overlap(box, ocr_output["boxes"])
```

**Filtering**:
- Accept traces where ≥ 80% of steps pass verification
- Report coverage: fraction of dataset surviving filtering

### 1.3 Counterfactual Generation

**Five Corruption Families**:

| Family | ID | Description | Implementation |
|--------|-----|-------------|----------------|
| Wrong region | F1 | Reference incorrect object/span | Swap grounding_ref to wrong location |
| Wrong value | F2 | Correct location, wrong extracted value | Mutate value field |
| Wrong relation | F3 | Incorrect spatial/logical relation | Flip relation direction |
| Irrelevant evidence | F4 | Plausible but irrelevant step | Insert off-topic evidence |
| Correct answer, wrong evidence | F5 | Same answer, corrupted intermediate | Corrupt step, preserve answer |

**Rejection Sampling**:
```python
def generate_counterfactual(clean_trace, family, max_attempts=10):
    """Generate same-answer counterfactual via rejection sampling."""
    for _ in range(max_attempts):
        candidate = corrupt_trace(clean_trace, family)

        # Check 1: Answer preserved
        if candidate["final_answer"] != clean_trace["final_answer"]:
            continue

        # Check 2: Non-trivial (hardness filter)
        if is_trivial(candidate):
            continue

        return candidate

    return None  # Rejection failed
```

**Hardness Filter** (multi-detector ensemble):
```python
def is_trivial(counterfactual):
    """Check if counterfactual is trivially detectable."""

    # Check 1: Lexical similarity
    tfidf_sim = compute_tfidf_similarity(counterfactual, clean_traces)
    if tfidf_sim < 0.3:  # Too different lexically
        return True

    # Check 2: Text-only PRM baseline
    text_only_score = text_only_prm.predict(counterfactual)
    if text_only_score > 0.75:  # Text-only can detect it
        return True

    return False
```

**Output**:
- `data/clevr/counterfactuals/{family}/` (~2K per family)
- `data/docvqa/counterfactuals/{family}/` (~3K per family)

### 1.4 Iso-Answer Pair Construction

**Algorithm**:
```python
def construct_pairs(clean_traces, counterfactuals):
    """Construct first-divergence aligned iso-answer pairs."""
    pairs = []

    for clean in clean_traces:
        # Find counterfactuals with same answer
        same_answer = filter_by_answer(counterfactuals, clean["final_answer"])

        for cf in same_answer:
            # Identify first divergence point
            t_star = find_first_divergence(clean, cf)

            if t_star is not None:
                pairs.append({
                    "positive": clean,
                    "negative": cf,
                    "t_star": t_star,
                    "family": cf["error_type"]
                })

    return pairs
```

**Coverage Reporting**:
- Iso-answer survival rate: `N_pairs / N_clean_traces`
- Selection bias analysis: answer type, reasoning length, step count

**Output**:
- `data/clevr/pairs.json` (~5K pairs)
- `data/docvqa/pairs.json` (~8K pairs)

---

## Part 2: Training Configuration

### 2.1 Model Architecture

**Backbone**: Qwen2.5-VL-3B-Instruct
**LoRA Configuration**:
| Parameter | Value |
|-----------|-------|
| Rank (r) | 16 |
| Alpha | 32 |
| Dropout | 0.05 |
| Target modules | q_proj, v_proj, k_proj, o_proj |

**Step Scorer Head**:
```python
class StepScorer(nn.Module):
    def __init__(self, hidden_dim=3584):
        super().__init__()
        self.scorer = nn.Sequential(
            nn.Linear(hidden_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )

    def forward(self, hidden_states):
        return self.scorer(hidden_states)
```

### 2.2 Training Hyperparameters

**Core Training (First-Divergence Loss)**:
| Parameter | Value |
|-----------|-------|
| Loss | `-log σ(r_{t*}^+ - r_{t*}^-)` |
| Optimizer | AdamW |
| Learning rate | 1e-4 |
| LR schedule | Cosine decay |
| Warmup steps | 100 |
| Batch size | 32 pairs |
| Epochs | 3 |
| Gradient accumulation | 4 |
| Mixed precision | bf16 |

**GPU Allocation**:
- Training: 2x A800
- Time: ~6 hours per epoch, ~18 hours total

### 2.3 Training Script

```bash
# CG-PRM Training
torchrun --nproc_per_node=2 train_cg_prm.py \
    --model_name Qwen/Qwen2.5-VL-3B-Instruct \
    --data_path data/pairs.json \
    --output_dir checkpoints/cg-prm-v1 \
    --lora_r 16 \
    --lora_alpha 32 \
    --learning_rate 1e-4 \
    --num_epochs 3 \
    --batch_size 32 \
    --gradient_accumulation_steps 4 \
    --loss_type first_divergence \
    --seed 42
```

### 2.4 Checkpoints

Save checkpoints at:
- Every 1000 steps
- End of each epoch
- Final model

---

## Part 3: Core Experiments

### 3.1 E1: First-Divergence vs Pointwise

**Purpose**: Is alignment necessary?

**Models**:
| Model | Training | Data |
|-------|----------|------|
| CG-PRM | First-divergence L_fd | Iso-answer pairs |
| Baseline-Pointwise | Binary cross-entropy | Same pairs, pointwise |

**Training**:
```bash
# CG-PRM (first-divergence)
python train.py --loss_type first_divergence --output_dir cg-prm-fd

# Baseline (pointwise)
python train.py --loss_type pointwise --output_dir baseline-pointwise
```

**Evaluation**:
- Dataset: Held-out answer-correct but evidence-wrong traces
- Metric: Step-level AUROC at t*
- Bootstrap CI: 1000 samples

**Success Criterion**:
- CG-PRM AUROC > Baseline AUROC + 0.05 (5 percentage points)
- 95% CI non-overlapping

### 3.2 E2: Schema-Constrained vs Post-hoc

**Purpose**: Is structured generation necessary?

**Models**:
| Model | Data Construction |
|-------|-------------------|
| CG-PRM (schema) | Teacher outputs grounding_ref directly |
| Baseline (post-hoc) | Extract grounding_ref after generation |

**Post-hoc Extraction**:
```python
def extract_grounding_ref(trace_text):
    """Post-hoc extraction from free-form text."""
    # Use regex/heuristics to find evidence references
    patterns = [
        r"region[:\s]+([^,\.]+)",
        r"object[:\s]+([^,\.]+)",
        r"value[:\s]+([^,\.]+)"
    ]
    # ... extraction logic
```

**Evaluation**:
| Metric | Description |
|--------|-------------|
| t* identification accuracy | Correctly identifying divergence point |
| Leave-one-out AUROC | Generalization to unseen families |

**Success Criterion**:
- Schema t* accuracy > Post-hoc t* accuracy + 0.10
- Schema leave-one-out AUROC > Post-hoc + 0.03

### 3.3 E3: Leave-One-Family-Out + Human-Authored

**Purpose**: Artifact control and natural error generalization

**Experiment 3a: Leave-One-Family-Out**:
```bash
for held_out in F1 F2 F3 F4 F5; do
    # Train on 4 families
    python train.py \
        --train_families $(complement $held_out) \
        --test_families $held_out \
        --output_dir lofo-$held_out
done
```

**Metrics**:
- AUROC on held-out family
- AUROC drop from full-family training

**Success Criterion**:
- Mean leave-one-out AUROC ≥ 0.65
- AUROC drop < 0.10 from full-family

**Experiment 3b: Human-Authored Failures**:
- Dataset: 100 matched pairs per benchmark (200 total)
- Negative traces written by humans (not synthetic)
- Evaluate: paired ranking accuracy

**Success Criterion**:
- Human failure detection rate ≥ 0.70
- Significantly above random (p < 0.01)

---

## Part 4: Core Ablations

### A1: First-Divergence vs Pointwise

Same as E1 (already covered)

### A2: Schema-Constrained vs Post-hoc

Same as E2 (already covered)

### A3: Iso-Answer Only vs Shortcut-Leaking

**Purpose**: Does mixing wrong-answer negatives reintroduce shortcut?

**Models**:
| Model | Training Data |
|-------|---------------|
| CG-PRM (iso-answer) | Same-answer pairs only |
| Baseline (mixed) | Same-answer + wrong-answer pairs |

**Evaluation**:
- Metric: AUROC on answer-correct but evidence-wrong traces
- Compare: shortcut exploitation

**Success Criterion**:
- Iso-answer model AUROC > Mixed model AUROC
- Shows mixing wrong-answer pairs hurts grounding discrimination

---

## Part 5: Evaluation Protocol

### 5.1 Step-Level Evaluation

```python
def evaluate_step_auroc(model, test_pairs):
    """Compute step-level AUROC at divergence point."""
    scores_pos = []
    scores_neg = []

    for pair in test_pairs:
        # Score at t*
        score_pos = model.score_step(pair["positive"], pair["t_star"])
        score_neg = model.score_step(pair["negative"], pair["t_star"])

        scores_pos.append(score_pos)
        scores_neg.append(score_neg)

    # AUROC: can we distinguish positive from negative steps?
    labels = [1] * len(scores_pos) + [0] * len(scores_neg)
    scores = scores_pos + scores_neg

    return roc_auc_score(labels, scores)
```

### 5.2 Interventional Grounding Gap

```python
def compute_necessity_gap(model, trace, evidence_intact, evidence_perturbed):
    """Compute interventional grounding gap."""
    score_intact = model.score_trace(trace, evidence_intact)
    score_perturbed = model.score_trace(trace, evidence_perturbed)

    return score_intact - score_perturbed
```

**Protocol**:
- For each test trace, create evidence perturbation
- Compare CG-PRM gap vs baseline gap

### 5.3 Bootstrap Confidence Intervals

```python
def bootstrap_ci(metric_func, data, n_samples=1000, ci=0.95):
    """Compute bootstrap confidence interval."""
    scores = []
    for _ in range(n_samples):
        sample = resample(data, replace=True)
        scores.append(metric_func(sample))

    lower = np.percentile(scores, (1 - ci) / 2 * 100)
    upper = np.percentile(scores, (1 + ci) / 2 * 100)

    return np.mean(scores), lower, upper
```

---

## Part 6: Execution Schedule

### Week 1 (Days 1-7): Data Construction

| Day | Task | GPU | Hours |
|-----|------|-----|-------|
| 1 | Set up pipeline, prompt templates | - | 4 |
| 2-3 | CLEVR clean trace generation | 1x A800 | 8 |
| 4-5 | DocVQA clean trace generation | 1x A800 | 8 |
| 6 | Automatic verification, filtering | - | 4 |
| 7 | Counterfactual generation (F1-F3) | 1x A800 | 4 |

### Week 2 (Days 8-14): Data + Training

| Day | Task | GPU | Hours |
|-----|------|-----|-------|
| 8-9 | Counterfactual generation (F4-F5) | 1x A800 | 4 |
| 10 | Iso-answer pair construction | - | 4 |
| 11-12 | Coverage analysis, filtering | - | 4 |
| 13-14 | CG-PRM training (v1) | 2x A800 | 18 |

### Week 3 (Days 15-21): Core Experiments

| Day | Task | GPU | Hours |
|-----|------|-----|-------|
| 15-16 | E1: First-divergence vs pointwise | 2x A800 | 12 |
| 17-18 | E2: Schema vs post-hoc | 2x A800 | 8 |
| 19-21 | E3: Leave-one-family-out (5 runs) | 2x A800 | 16 |

### Week 4 (Days 22-28): Ablations + Analysis

| Day | Task | GPU | Hours |
|-----|------|-----|-------|
| 22-23 | A3: Iso-answer vs mixed | 2x A800 | 8 |
| 24-25 | Human-authored evaluation | - | 4 |
| 26-28 | Interventional grounding gap analysis | - | 4 |

### Week 5-6 (Days 29-40): Paper Writing

| Day | Task |
|-----|------|
| 29-32 | Consolidate results, figures |
| 33-36 | Write paper sections |
| 37-40 | Revision, formatting |

---

## Part 7: Success Criteria Summary

### Minimum Publishable Result (MPR)

| Criterion | Threshold |
|-----------|-----------|
| E1: First-divergence > Pointwise | AUROC +0.05, CI non-overlapping |
| E3a: Leave-one-out AUROC | ≥ 0.65 |
| E3b: Human failure detection | ≥ 0.70 |
| A3: Iso-answer > Mixed | Shows shortcut leakage |

### Stretch Goals

| Goal | Target |
|------|--------|
| Leave-one-out AUROC | ≥ 0.75 |
| Human failure detection | ≥ 0.80 |
| Cross-generator transfer | AUROC ≥ 0.70 |

### Failure Modes

| Failure | Action |
|---------|--------|
| E1 fails (no alignment benefit) | Investigate t* identification |
| E3a fails (artifact detection) | Add more paraphrase diversity |
| E3b fails (no human generalization) | Expand training, add natural negatives |

---

## Part 8: Resource Budget

| Resource | Allocation |
|----------|------------|
| GPU-hours (data) | ~16 hours |
| GPU-hours (training) | ~30 hours |
| GPU-hours (experiments) | ~36 hours |
| **Total GPU-hours** | **~82 hours** |
| Storage | ~50 GB (traces, checkpoints) |
| Human annotation | 100-200 samples (audit) |

**Budget check**: 82 hours on 4x A800 = well within 40-day, 4xA800 constraint.

---

## Appendix A: File Structure

```
cg-prm/
├── data/
│   ├── clevr/
│   │   ├── clean_traces.json
│   │   ├── counterfactuals/
│   │   │   ├── F1_wrong_region.json
│   │   │   ├── F2_wrong_value.json
│   │   │   ├── F3_wrong_relation.json
│   │   │   ├── F4_irrelevant.json
│   │   │   └── F5_correct_answer_wrong_evidence.json
│   │   └── pairs.json
│   ├── docvqa/
│   │   ├── clean_traces.json
│   │   ├── counterfactuals/
│   │   └── pairs.json
│   └── human_challenge/
│       ├── clevr_pairs.json
│       └── docvqa_pairs.json
├── checkpoints/
│   ├── cg-prm-v1/
│   ├── baseline-pointwise/
│   ├── baseline-posthoc/
│   └── lofo-{F1..F5}/
├── results/
│   ├── e1_alignment.json
│   ├── e2_schema.json
│   ├── e3_lofo.json
│   ├── e3_human.json
│   └── a3_shortcut.json
├── scripts/
│   ├── generate_traces.py
│   ├── verify_traces.py
│   ├── generate_counterfactuals.py
│   ├── construct_pairs.py
│   ├── train.py
│   └── evaluate.py
└── configs/
    ├── clevr.yaml
    └── docvqa.yaml
```

---

## Appendix B: Commands Reference

```bash
# 1. Generate clean traces
python scripts/generate_traces.py --benchmark clevr --output data/clevr/clean_traces.json
python scripts/generate_traces.py --benchmark docvqa --output data/docvqa/clean_traces.json

# 2. Verify traces
python scripts/verify_traces.py --input data/clevr/clean_traces.json --output data/clevr/clean_traces_verified.json

# 3. Generate counterfactuals
python scripts/generate_counterfactuals.py --input data/clevr/clean_traces_verified.json --output data/clevr/counterfactuals/

# 4. Construct pairs
python scripts/construct_pairs.py --clean data/clevr/clean_traces_verified.json --counterfactuals data/clevr/counterfactuals/ --output data/clevr/pairs.json

# 5. Train CG-PRM
torchrun --nproc_per_node=2 scripts/train.py --config configs/clevr.yaml --loss_type first_divergence

# 6. Evaluate
python scripts/evaluate.py --checkpoint checkpoints/cg-prm-v1 --test_data data/clevr/pairs.json

# 7. Run full experiment
bash scripts/run_e1.sh  # First-divergence vs pointwise
bash scripts/run_e2.sh  # Schema vs post-hoc
bash scripts/run_e3.sh  # Leave-one-out + human
```

---

## Appendix C: Random Seeds

For reproducibility, fix seeds:
```python
SEEDS = [42, 123, 456, 789, 1024]  # 5 seeds for robustness
```

All experiments run with seed=42 for primary results.
Use all 5 seeds for final paper tables.

---

**Plan Created**: 2026-03-30
**Ready for Execution**: ✅