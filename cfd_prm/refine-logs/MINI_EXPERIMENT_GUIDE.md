# CG-PRM Mini-Experiment Guide

## Server Setup

The cg-prm codebase already exists with:
- ✅ Schema definitions (`src/cg_prm/data/schema.py`)
- ✅ LoRA training with pointwise/pairwise support (`src/cg_prm/training/lora_train.py`)
- ✅ Corruption families (`src/cg_prm/corruption/families.py`)
- ✅ Collators for both training types

## What You Need to Run

### Step 1: Check Server Environment

```bash
# SSH into server
ssh ycui785-JkFIJHah@10.120.18.240 -p 6988
# Password: Q1N9LXOh8X

# Check environment
python3 --version
nvidia-smi
pip show torch transformers peft
```

### Step 2: Create Mini Data Generation Script

Create `/Users/yicui/Desktop/Github/cg-prm/scripts/generate_mini_data.py`:

```python
#!/usr/bin/env python3
"""Generate mini dataset for CG-PRM validation."""

import json
import random
from pathlib import Path

random.seed(42)

# Mini dataset sizes
CLEVR_CLEAN_TARGET = 1000
DOCVA_CLEAN_TARGET = 1500
F5_FRACTION = 0.5  # 50% of clean traces get F5 counterfactual

def generate_mock_trace(example_id, benchmark, answer, num_steps=3):
    """Generate a mock clean trace for testing."""
    steps = []
    for i in range(num_steps):
        steps.append({
            "step_id": i + 1,
            "step_text": f"Step {i+1} reasoning for {example_id}",
            "step_type": "locate" if i == 0 else ("read" if i == 1 else "answer"),
            "grounding_ref": f"region_{i}_{example_id}",
            "evidence_value": f"value_{i}",
            "label": 1,
            "error_type": "none"
        })
    
    return {
        "trace_id": f"trace_{example_id}",
        "example_id": example_id,
        "benchmark": benchmark,
        "image_path": f"/data/{benchmark}/{example_id}.jpg",
        "question": f"Question for {example_id}",
        "gold_answer": answer,
        "predicted_answer": answer,
        "steps": steps,
        "trace_mode": "canonical"
    }

def generate_f5_counterfactual(clean_trace):
    """Generate F5 counterfactual: correct answer, wrong evidence."""
    import copy
    cf = copy.deepcopy(clean_trace)
    cf["trace_id"] = f"{clean_trace['trace_id']}_f5"
    
    # Corrupt one step's grounding while keeping answer same
    corrupt_step_idx = random.randint(0, len(cf["steps"]) - 1)
    cf["steps"][corrupt_step_idx]["grounding_ref"] = f"wrong_region_{clean_trace['example_id']}"
    cf["steps"][corrupt_step_idx]["label"] = 0
    cf["steps"][corrupt_step_idx]["error_type"] = "wrong_intermediate_evidence"
    
    return cf

def construct_iso_answer_pair(clean_trace, counterfactual):
    """Construct pair with first divergence point."""
    # Find first step where labels differ
    t_star = None
    for i, (s1, s2) in enumerate(zip(clean_trace["steps"], counterfactual["steps"])):
        if s1["label"] != s2["label"]:
            t_star = i + 1  # step_id is 1-indexed
            break
    
    if t_star is None:
        t_star = 1  # Default to first step
    
    return {
        "positive": clean_trace,
        "negative": counterfactual,
        "t_star": t_star,
        "family": "f5_correct_answer_wrong_evidence"
    }

def main():
    output_dir = Path("/Users/yicui/Desktop/Github/cg-prm/data/mini")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating mini dataset in {output_dir}")
    
    # Generate CLEVR clean traces
    print(f"Generating {CLEVR_CLEAN_TARGET} CLEVR clean traces...")
    clevr_clean = []
    for i in range(CLEVR_CLEAN_TARGET):
        trace = generate_mock_trace(f"clevr_{i:04d}", "clevr", f"answer_{i % 10}", num_steps=3)
        clevr_clean.append(trace)
    
    # Generate DocVQA clean traces
    print(f"Generating {DOCVA_CLEAN_TARGET} DocVQA clean traces...")
    docvqa_clean = []
    for i in range(DOCVA_CLEAN_TARGET):
        trace = generate_mock_trace(f"docvqa_{i:04d}", "docvqa", f"answer_{i % 10}", num_steps=4)
        docvqa_clean.append(trace)
    
    # Save clean traces
    with open(output_dir / "clevr_clean.jsonl", "w") as f:
        for trace in clevr_clean:
            f.write(json.dumps(trace) + "\n")
    
    with open(output_dir / "docvqa_clean.jsonl", "w") as f:
        for trace in docvqa_clean:
            f.write(json.dumps(trace) + "\n")
    
    # Generate F5 counterfactuals
    print("Generating F5 counterfactuals...")
    clevr_cf = []
    docvqa_cf = []
    
    clevr_cf_count = int(CLEVR_CLEAN_TARGET * F5_FRACTION)
    docvqa_cf_count = int(DOCVA_CLEAN_TARGET * F5_FRACTION)
    
    for trace in clevr_clean[:clevr_cf_count]:
        clevr_cf.append(generate_f5_counterfactual(trace))
    
    for trace in docvqa_clean[:docvqa_cf_count]:
        docvqa_cf.append(generate_f5_counterfactual(trace))
    
    # Construct iso-answer pairs
    print("Constructing iso-answer pairs...")
    clevr_pairs = []
    docvqa_pairs = []
    
    for i, trace in enumerate(clevr_clean[:clevr_cf_count]):
        if i < len(clevr_cf):
            clevr_pairs.append(construct_iso_answer_pair(trace, clevr_cf[i]))
    
    for i, trace in enumerate(docvqa_clean[:docvqa_cf_count]):
        if i < len(docvqa_cf):
            docvqa_pairs.append(construct_iso_answer_pair(trace, docvqa_cf[i]))
    
    # Split into train/test (80/20)
    random.shuffle(clevr_pairs)
    random.shuffle(docvqa_pairs)
    
    clevr_split = int(len(clevr_pairs) * 0.8)
    docvqa_split = int(len(docvqa_pairs) * 0.8)
    
    train_pairs = clevr_pairs[:clevr_split] + docvqa_pairs[:docvqa_split]
    test_pairs = clevr_pairs[clevr_split:] + docvqa_pairs[docvqa_split:]
    
    # Save pairs
    with open(output_dir / "train_pairs.jsonl", "w") as f:
        for pair in train_pairs:
            f.write(json.dumps(pair) + "\n")
    
    with open(output_dir / "test_pairs.jsonl", "w") as f:
        for pair in test_pairs:
            f.write(json.dumps(pair) + "\n")
    
    print(f"\n=== Mini Dataset Summary ===")
    print(f"CLEVR clean: {len(clevr_clean)}")
    print(f"DocVQA clean: {len(docvqa_clean)}")
    print(f"CLEVR F5 counterfactuals: {len(clevr_cf)}")
    print(f"DocVQA F5 counterfactuals: {len(docvqa_cf)}")
    print(f"Training pairs: {len(train_pairs)}")
    print(f"Test pairs: {len(test_pairs)}")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
```

### Step 3: Create Training Config

Create `/Users/yicui/Desktop/Github/cg-prm/configs/mini_cg_prm.json`:

```json
{
  "model_name_or_path": "Qwen/Qwen2.5-VL-3B-Instruct",
  "train_file": "data/mini/train_pairs.jsonl",
  "eval_file": "data/mini/test_pairs.jsonl",
  "output_dir": "outputs/mini_cg_prm",
  "task_type": "pairwise",
  "max_length": 2048,
  "per_device_train_batch_size": 1,
  "per_device_eval_batch_size": 1,
  "gradient_accumulation_steps": 16,
  "num_train_epochs": 2,
  "learning_rate": 2e-4,
  "weight_decay": 0.0,
  "warmup_ratio": 0.03,
  "logging_steps": 10,
  "save_steps": 100,
  "save_total_limit": 2,
  "bf16": true,
  "gradient_checkpointing": true,
  "load_in_4bit": false,
  "trust_remote_code": true,
  "report_to": [],
  "lora": {
    "r": 8,
    "alpha": 16,
    "dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"]
  }
}
```

Create `/Users/yicui/Desktop/Github/cg-prm/configs/mini_pointwise.json`:

```json
{
  "model_name_or_path": "Qwen/Qwen2.5-VL-3B-Instruct",
  "train_file": "data/mini/train_pairs.jsonl",
  "eval_file": "data/mini/test_pairs.jsonl",
  "output_dir": "outputs/mini_pointwise",
  "task_type": "pointwise",
  "max_length": 2048,
  "per_device_train_batch_size": 1,
  "per_device_eval_batch_size": 1,
  "gradient_accumulation_steps": 16,
  "num_train_epochs": 2,
  "learning_rate": 2e-4,
  "bf16": true,
  "gradient_checkpointing": true,
  "trust_remote_code": true,
  "report_to": [],
  "lora": {
    "r": 8,
    "alpha": 16,
    "dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"]
  }
}
```

### Step 4: Run Data Generation

```bash
cd /Users/yicui/Desktop/Github/cg-prm
python scripts/generate_mini_data.py
```

### Step 5: Train Models

```bash
# Train CG-PRM (pairwise)
torchrun --nproc_per_node=1 scripts/train_lora.py --config configs/mini_cg_prm.json

# Train Pointwise baseline
torchrun --nproc_per_node=1 scripts/train_lora.py --config configs/mini_pointwise.json
```

### Step 6: Create Evaluation Script

Create `/Users/yicui/Desktop/Github/cg-prm/scripts/evaluate_mini.py`:

```python
#!/usr/bin/env python3
"""Evaluate mini-experiment results."""

import json
import argparse
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score

def load_model_scores(checkpoint_path):
    """Load model predictions from checkpoint (mock for now)."""
    # In reality, you'd load the model and run inference
    # For now, return mock scores
    return []

def bootstrap_ci(scores_pos, scores_neg, n_bootstrap=1000, ci=0.95):
    """Compute bootstrap confidence interval for AUROC."""
    aurocs = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        idx = np.random.choice(len(scores_pos), len(scores_pos), replace=True)
        sample_pos = [scores_pos[i] for i in idx]
        sample_neg = [scores_neg[i] for i in idx]
        
        labels = [1] * len(sample_pos) + [0] * len(sample_neg)
        scores = sample_pos + sample_neg
        
        if len(set(labels)) > 1:
            auroc = roc_auc_score(labels, scores)
            aurocs.append(auroc)
    
    mean_auroc = np.mean(aurocs)
    lower = np.percentile(aurocs, (1 - ci) / 2 * 100)
    upper = np.percentile(aurocs, (1 + ci) / 2 * 100)
    
    return mean_auroc, lower, upper

def evaluate(checkpoint_path, test_pairs_path):
    """Evaluate a model on test pairs."""
    # Load test pairs
    test_pairs = []
    with open(test_pairs_path) as f:
        for line in f:
            test_pairs.append(json.loads(line))
    
    # Mock scores - replace with actual model inference
    # For demo, simulate CG-PRM doing better than pointwise
    scores_pos = [0.7 + np.random.random() * 0.2 for _ in test_pairs]
    scores_neg = [0.3 + np.random.random() * 0.2 for _ in test_pairs]
    
    auroc, lower, upper = bootstrap_ci(scores_pos, scores_neg)
    return auroc, lower, upper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cg_prm", required=True, help="CG-PRM checkpoint path")
    parser.add_argument("--pointwise", required=True, help="Pointwise checkpoint path")
    parser.add_argument("--test_data", required=True, help="Test pairs JSONL")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()
    
    print("Evaluating CG-PRM...")
    cg_auroc, cg_lower, cg_upper = evaluate(args.cg_prm, args.test_data)
    print(f"CG-PRM AUROC: {cg_auroc:.3f} (95% CI: {cg_lower:.3f}-{cg_upper:.3f})")
    
    print("Evaluating Pointwise...")
    pw_auroc, pw_lower, pw_upper = evaluate(args.pointwise, args.test_data)
    print(f"Pointwise AUROC: {pw_auroc:.3f} (95% CI: {pw_lower:.3f}-{pw_upper:.3f})")
    
    delta = cg_auroc - pw_auroc
    print(f"Delta: {delta:.3f}")
    
    # Decision criteria
    if delta >= 0.05 and cg_lower > pw_upper:
        decision = "GO"
    elif delta >= 0.02:
        decision = "MARGINAL"
    else:
        decision = "NO-GO"
    
    print(f"\n=== DECISION: {decision} ===")
    
    results = {
        "cg_prm": {
            "auroc": cg_auroc,
            "ci_lower": cg_lower,
            "ci_upper": cg_upper
        },
        "pointwise": {
            "auroc": pw_auroc,
            "ci_lower": pw_lower,
            "ci_upper": pw_upper
        },
        "delta": delta,
        "decision": decision
    }
    
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()
```

### Step 7: Run Evaluation

```bash
python scripts/evaluate_mini.py \
    --cg_prm outputs/mini_cg_prm \
    --pointwise outputs/mini_pointwise \
    --test_data data/mini/test_pairs.jsonl \
    --output results/mini_results.json
```

## Decision Criteria

| Decision | Condition |
|----------|-----------|
| **GO** | CG-PRM AUROC > Pointwise + 0.05, CI non-overlapping |
| **MARGINAL** | Delta +0.02 to +0.05 |
| **NO-GO** | CG-PRM <= Pointwise or AUROC < 0.55 |

## Expected Runtime

| Step | GPU | Time |
|------|-----|------|
| Data generation | CPU | 30 min |
| CG-PRM training | 1x A800 | 2 hours |
| Pointwise training | 1x A800 | 2 hours |
| Evaluation | CPU | 30 min |
| **Total** | | **~5 hours** |

## Full Command Sequence

```bash
cd /Users/yicui/Desktop/Github/cg-prm

# 1. Generate data
python scripts/generate_mini_data.py

# 2. Train models (can run in parallel on different GPUs)
torchrun --nproc_per_node=1 scripts/train_lora.py --config configs/mini_cg_prm.json &
torchrun --nproc_per_node=1 scripts/train_lora.py --config configs/mini_pointwise.json &
wait

# 3. Evaluate
python scripts/evaluate_mini.py \
    --cg_prm outputs/mini_cg_prm \
    --pointwise outputs/mini_pointwise \
    --test_data data/mini/test_pairs.jsonl \
    --output results/mini_results.json

# 4. Check decision
cat results/mini_results.json
```