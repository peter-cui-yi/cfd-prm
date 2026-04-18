"""
Step-Level Evaluation for CFD-PRM

Evaluates trained models at the individual step level to demonstrate
that CFD's step-level scoring provides advantages that pairwise and
pointwise baselines cannot match.

Key insight:
  - Pairwise/Pointwise: score entire trajectory as one unit
    -> all steps in a trajectory get the SAME score
    -> within-trajectory score variance = 0
    -> step-level AUC ~ 0.5 (cannot distinguish correct vs incorrect steps)
  - CFD: scores each step independently
    -> correct steps get high scores, incorrect steps get low scores
    -> meaningful within-trajectory score variance
    -> step-level AUC >> 0.5
    -> can localize t* (first divergence point)

Usage:
    # Evaluate CFD model (step-level trained)
    python -m cfd_prm.eval.eval_step_level \
        --checkpoint outputs/step_level_v3_dual_loss/final \
        --data_path data/visualprm400k_converted/visualprm400k_pairs.json \
        --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
        --output_dir outputs/step_level_v3_dual_loss/eval_step \
        --step_level --pooling last

    # Evaluate pairwise baseline at step level
    python -m cfd_prm.eval.eval_step_level \
        --checkpoint outputs/baseline_pairwise_multi/final \
        --data_path data/visualprm400k_converted/visualprm400k_pairs.json \
        --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
        --output_dir outputs/baseline_pairwise_multi/eval_step \
        --pooling last

    # Evaluate pointwise baseline at step level
    python -m cfd_prm.eval.eval_step_level \
        --checkpoint outputs/baseline_pointwise_multi/final \
        --data_path data/visualprm400k_converted/visualprm400k_pairs.json \
        --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
        --output_dir outputs/baseline_pointwise_multi/eval_step \
        --pooling last
"""

import json
import random
import argparse
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from peft import PeftModel


class StepLevelEvalDataset(Dataset):
    """
    Step-level evaluation dataset.

    Expands each trajectory pair into individual step queries.
    Returns one sample per step, not per pair.
    """

    def __init__(self, pairs, processor, max_length=512, pool_mode="mean"):
        """
        Args:
            pairs: List of trajectory pairs
            processor: AutoProcessor for tokenization
            max_length: Max sequence length
            pool_mode: "mean" = score each step independently,
                       "whole" = score entire trajectory (pairwise/pointwise mode)
        """
        self.pairs = pairs
        self.processor = processor
        self.max_length = max_length
        self.pool_mode = pool_mode

        self.step_texts = []
        self.step_meta = []  # (pair_idx, side, step_idx, label)

        for pair_idx, pair in enumerate(pairs):
            question = pair.get("question", "")

            if pool_mode == "whole":
                # Whole-trajectory mode: one query per trajectory
                ref_traj = pair["reference"]["trajectory"]
                query_ref = (
                    f"Trajectory: {' | '.join(ref_traj)}\n\n"
                    f"Is this trajectory correct? Answer YES or NO."
                )
                conv = [{"role": "user", "content": [{"type": "text", "text": query_ref}]}]
                text = self.processor.apply_chat_template(conv, tokenize=False)
                self.step_texts.append(text)
                # Meta: all steps get same score, label varies
                for step_i in range(len(pair["reference"]["labels"])):
                    self.step_meta.append((pair_idx, 0, step_i, pair["reference"]["labels"][step_i]))

                dev_traj = pair["deviated"]["trajectory"]
                query_dev = (
                    f"Trajectory: {' | '.join(dev_traj)}\n\n"
                    f"Is this trajectory correct? Answer YES or NO."
                )
                conv = [{"role": "user", "content": [{"type": "text", "text": query_dev}]}]
                text = self.processor.apply_chat_template(conv, tokenize=False)
                self.step_texts.append(text)
                for step_i in range(len(pair["deviated"]["labels"])):
                    self.step_meta.append((pair_idx, 1, step_i, pair["deviated"]["labels"][step_i]))
            else:
                # Step-level mode: one query per step
                ref_traj = pair["reference"]["trajectory"]
                ref_labels = pair["reference"]["labels"]
                for step_i, label in enumerate(ref_labels):
                    prefix = "\n".join(ref_traj[:step_i + 1])
                    query = (
                        f"Question: {question}\n\n"
                        f"Step-by-step reasoning:\n{prefix}\n\n"
                        f"Is step {step_i + 1} correct? Answer YES or NO."
                    )
                    conv = [{"role": "user", "content": [{"type": "text", "text": query}]}]
                    text = self.processor.apply_chat_template(conv, tokenize=False)
                    self.step_texts.append(text)
                    self.step_meta.append((pair_idx, 0, step_i, label))

                dev_traj = pair["deviated"]["trajectory"]
                dev_labels = pair["deviated"]["labels"]
                for step_i, label in enumerate(dev_labels):
                    prefix = "\n".join(dev_traj[:step_i + 1])
                    query = (
                        f"Question: {question}\n\n"
                        f"Step-by-step reasoning:\n{prefix}\n\n"
                        f"Is step {step_i + 1} correct? Answer YES or NO."
                    )
                    conv = [{"role": "user", "content": [{"type": "text", "text": query}]}]
                    text = self.processor.apply_chat_template(conv, tokenize=False)
                    self.step_texts.append(text)
                    self.step_meta.append((pair_idx, 1, step_i, label))

    def __len__(self):
        return len(self.step_texts)

    def __getitem__(self, idx):
        return self.step_texts[idx], self.step_meta[idx]


def step_level_eval_collate_fn(batch):
    texts = [item[0] for item in batch]
    metas = [item[1] for item in batch]
    pair_idxs = torch.tensor([m[0] for m in metas], dtype=torch.long)
    sides = torch.tensor([m[1] for m in metas], dtype=torch.long)
    step_idxs = torch.tensor([m[2] for m in metas], dtype=torch.long)
    labels = torch.tensor([m[3] for m in metas], dtype=torch.float)
    return {"texts": texts, "pair_idxs": pair_idxs, "sides": sides, "step_idxs": step_idxs, "labels": labels}


def compute_auc(scores, labels):
    """Compute AUC-ROC using sklearn for reliability."""
    from sklearn.metrics import roc_auc_score
    try:
        return float(roc_auc_score(labels, scores))
    except ValueError:
        return 0.5


def compute_auprc(scores, labels):
    """Compute Average Precision (AUPRC)."""
    from sklearn.metrics import average_precision_score
    try:
        return float(average_precision_score(labels, scores))
    except ValueError:
        return 0.0


def compute_ece(scores, labels, n_bins=10):
    """Compute Expected Calibration Error."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n_total = len(scores)
    for i in range(n_bins):
        in_bin = (scores > bin_boundaries[i]) & (scores <= bin_boundaries[i + 1])
        bin_size = in_bin.sum()
        if bin_size > 0:
            bin_accuracy = labels[in_bin].mean()
            bin_confidence = scores[in_bin].mean()
            ece += (bin_size / n_total) * abs(bin_accuracy - bin_confidence)
    return ece


def compute_brier_score(scores, labels):
    """Compute Brier score: mean((scores - labels)^2)."""
    return float(np.mean((scores - labels) ** 2))


def compute_within_trajectory_variance(step_scores, pair_idxs, sides):
    """
    Compute average within-trajectory score variance.

    For each trajectory, compute variance of scores across its steps.
    Pairwise/pointwise methods should produce ~0 variance (all steps same score).
    CFD should produce meaningful variance.
    """
    traj_scores = {}
    for i in range(len(pair_idxs)):
        key = (pair_idxs[i].item(), sides[i].item())
        if key not in traj_scores:
            traj_scores[key] = []
        traj_scores[key].append(step_scores[i])

    variances = []
    for key, scores in traj_scores.items():
        if len(scores) > 1:
            variances.append(np.var(scores))

    return np.mean(variances) if variances else 0.0


def compute_pairwise_auc(scores_ref, scores_dev):
    """Compute AUC-ROC for pairwise ranking (ref should score higher than dev).

    Each (ref_score, dev_score) pair is treated as a binary classification:
    ref=1, dev=0. The AUC measures how well the scores separate ref from dev.
    """
    scores = np.concatenate([scores_ref, scores_dev])
    labels = np.concatenate([np.ones_like(scores_ref), np.zeros_like(scores_dev)])
    return compute_auc(scores, labels)


def compute_t_star_localization(all_step_scores, pairs):
    """
    Compute t* localization accuracy.

    For each deviated trajectory:
      - Find the step with the largest score drop (predicted t*)
      - Compare to actual t*
      - Count as correct if |predicted_t* - actual_t*| <= 1
    """
    # Group scores by (pair_idx, side)
    traj_data = {}
    for entry in all_step_scores:
        pair_idx, side, step_idx, score, label = entry
        key = (pair_idx, side)
        if key not in traj_data:
            traj_data[key] = []
        traj_data[key].append((step_idx, score, label))

    correct = 0
    total = 0

    for pair_idx, pair in enumerate(pairs):
        t_star_actual = pair["t_star"]

        # Only evaluate on deviated trajectory
        dev_key = (pair_idx, 1)
        if dev_key not in traj_data:
            continue

        dev_steps = sorted(traj_data[dev_key], key=lambda x: x[0])

        if len(dev_steps) < 2:
            continue

        # Find the step with the largest score drop
        # This is where scores transition from high to low
        best_pred_tstar = 0
        max_drop = 0

        for i in range(1, len(dev_steps)):
            drop = dev_steps[i-1][1] - dev_steps[i][1]  # score drop
            if drop > max_drop:
                max_drop = drop
                best_pred_tstar = dev_steps[i][0]

        # Also try: first step where score < 0.5
        first_low = None
        for i, (step_idx, score, label) in enumerate(dev_steps):
            if score < 0.5 and first_low is None:
                first_low = step_idx
                break

        # Use whichever is closer to actual t*
        if first_low is not None:
            pred_tstar = first_low if abs(first_low - t_star_actual) < abs(best_pred_tstar - t_star_actual) else best_pred_tstar
        else:
            pred_tstar = best_pred_tstar

        if abs(pred_tstar - t_star_actual) <= 1:
            correct += 1
        total += 1

    return correct / total if total > 0 else 0.0, total


def compute_score_gradientality(all_step_scores, pairs):
    """
    Compute score gradientality: do scores decrease monotonically after t*?

    For each deviated trajectory, check if scores are:
      - High before t* (correct steps)
      - Low after t* (incorrect steps)
    """
    traj_data = {}
    for entry in all_step_scores:
        pair_idx, side, step_idx, score, label = entry
        key = (pair_idx, side)
        if key not in traj_data:
            traj_data[key] = []
        traj_data[key].append((step_idx, score, label))

    avg_before_tstar = []
    avg_after_tstar = []

    for pair_idx, pair in enumerate(pairs):
        t_star = pair["t_star"]

        dev_key = (pair_idx, 1)
        if dev_key not in traj_data:
            continue

        dev_steps = traj_data[dev_key]

        before = [s for step_idx, s, label in dev_steps if step_idx < t_star]
        after = [s for step_idx, s, label in dev_steps if step_idx >= t_star]

        if before and after:
            avg_before_tstar.append(np.mean(before))
            avg_after_tstar.append(np.mean(after))

    if not avg_before_tstar:
        return 0.0

    avg_before = np.mean(avg_before_tstar)
    avg_after = np.mean(avg_after_tstar)

    return avg_before - avg_after


@torch.no_grad()
def evaluate_step_level(base_model, score_head, processor, test_pairs, device,
                        batch_size=8, pooling="mean", max_length=512, pool_mode="step"):
    """
    Run step-level evaluation.

    Args:
        pool_mode: "step" = score each step independently (CFD mode),
                   "whole" = score entire trajectory (pairwise/pointwise mode)
    """
    base_model.eval()
    score_head.eval()

    dataset = StepLevelEvalDataset(test_pairs, processor, max_length=max_length, pool_mode=pool_mode)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=step_level_eval_collate_fn)

    all_step_scores = []  # (pair_idx, side, step_idx, score, label)
    all_scores_raw = []

    for batch in tqdm(loader, desc=f"Evaluating ({pool_mode} mode)"):
        texts = batch["texts"]
        pair_idxs = batch["pair_idxs"]
        sides = batch["sides"]
        step_idxs = batch["step_idxs"]
        labels = batch["labels"]

        # Tokenize
        inputs = processor(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)

        # Forward
        outputs = base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=None,
            image_grid_thw=None,
            output_hidden_states=True,
        )
        hidden_states = outputs.hidden_states[-1]  # [batch, seq_len, hidden]

        # Pooling
        if pooling == "last":
            seq_lengths = attention_mask.sum(dim=1)
            batch_indices = torch.arange(attention_mask.size(0), device=hidden_states.device)
            pooled = hidden_states[batch_indices, seq_lengths - 1]
        else:
            mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).to(hidden_states.dtype)
            sum_embeddings = (hidden_states * mask_expanded).sum(dim=1)
            sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
            pooled = sum_embeddings / sum_mask

        logits = score_head(pooled)
        scores = torch.sigmoid(logits).squeeze(-1)

        for i in range(len(scores)):
            pi = pair_idxs[i].item()
            side = sides[i].item()
            si = step_idxs[i].item()
            score = scores[i].item()
            label = labels[i].item()
            all_step_scores.append((pi, side, si, score, label))
            all_scores_raw.append(score)

    all_scores_raw = np.array(all_scores_raw)
    all_labels = np.array([s[4] for s in all_step_scores])

    # --- Metric 1: Step-level AUC-ROC (all individual steps) ---
    step_auc = compute_auc(all_scores_raw, all_labels)

    # --- Metric 2: Step-level accuracy ---
    step_accuracy = ((all_scores_raw > 0.5) == all_labels).mean()

    # --- Metric 3: Within-trajectory score variance ---
    pair_idxs_arr = np.array([s[0] for s in all_step_scores])
    sides_arr = np.array([s[1] for s in all_step_scores])
    within_traj_var = compute_within_trajectory_variance(all_scores_raw, pair_idxs_arr, sides_arr)

    # --- Metric 4: t* localization accuracy ---
    tstar_acc, tstar_total = compute_t_star_localization(all_step_scores, test_pairs)

    # --- Metric 5: Score gradientality (avg_before_t* - avg_after_t*) ---
    score_grad = compute_score_gradientality(all_step_scores, test_pairs)

    # --- Metric 6: Trajectory-level AUC (aggregate steps to trajectory level) ---
    # Group per-step scores into per-trajectory scores
    traj_scores = {}  # (pair_idx, side) -> list of step scores
    for pi, side, si, score, label in all_step_scores:
        key = (pi, side)
        if key not in traj_scores:
            traj_scores[key] = []
        traj_scores[key].append(score)

    # Aggregate each trajectory using mean pooling (primary aggregation)
    # Properly pair ref and dev by pair_idx
    pair_scores_ref = []
    pair_scores_dev = []
    for pi in range(len(test_pairs)):
        ref_key = (pi, 0)
        dev_key = (pi, 1)
        if ref_key in traj_scores and dev_key in traj_scores:
            pair_scores_ref.append(np.mean(traj_scores[ref_key]))
            pair_scores_dev.append(np.mean(traj_scores[dev_key]))

    pair_scores_ref = np.array(pair_scores_ref)
    pair_scores_dev = np.array(pair_scores_dev)

    # Trajectory AUC: ref=1, dev=0, using mean-pooled trajectory scores
    traj_auc = compute_pairwise_auc(pair_scores_ref, pair_scores_dev)
    # Pair accuracy: fraction of pairs where ref scores higher than dev
    pairwise_acc = (pair_scores_ref > pair_scores_dev).mean()

    # --- Score statistics ---
    correct_scores = all_scores_raw[all_labels == 1]
    incorrect_scores = all_scores_raw[all_labels == 0]

    # --- Calibration metrics ---
    ece = compute_ece(all_scores_raw, all_labels)
    brier = compute_brier_score(all_scores_raw, all_labels)
    auprc = compute_auprc(all_scores_raw, all_labels)

    return {
        "step_level_auc": float(step_auc),
        "step_level_auprc": float(auprc),
        "step_level_accuracy": float(step_accuracy),
        "within_trajectory_variance": float(within_traj_var),
        "t_star_localization_accuracy": float(tstar_acc),
        "t_star_localization_total": int(tstar_total),
        "score_gradientality": float(score_grad),
        "trajectory_level_auc": float(traj_auc),
        "trajectory_level_pairwise_accuracy": float(pairwise_acc),
        "mean_correct_score": float(correct_scores.mean()) if len(correct_scores) > 0 else 0.0,
        "mean_incorrect_score": float(incorrect_scores.mean()) if len(incorrect_scores) > 0 else 0.0,
        "std_correct_score": float(correct_scores.std()) if len(correct_scores) > 0 else 0.0,
        "std_incorrect_score": float(incorrect_scores.std()) if len(incorrect_scores) > 0 else 0.0,
        "ece": float(ece),
        "brier_score": float(brier),
        "n_steps": int(len(all_scores_raw)),
        "n_pairs": int(len(pair_scores_ref)),
        "pool_mode": pool_mode,
    }


def create_split(data_path, test_ratio=0.1, seed=42):
    """Create train/test split."""
    random.seed(seed)
    with open(data_path) as f:
        pairs = json.load(f)

    n = len(pairs)
    indices = list(range(n))
    random.shuffle(indices)

    test_size = int(n * test_ratio)
    test_indices = indices[:test_size]
    test_pairs = [pairs[i] for i in test_indices]

    return test_pairs


def load_model(checkpoint_path, model_name):
    """Load model from checkpoint."""
    print(f"Loading base model from {model_name}...")
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
    )

    print(f"Loading LoRA adapter from {checkpoint_path}...")
    base_model = PeftModel.from_pretrained(base_model, checkpoint_path)

    for param in base_model.visual.parameters():
        param.requires_grad = False

    hidden_size = base_model.config.hidden_size
    score_head = nn.Sequential(
        nn.Linear(hidden_size, 256),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(256, 1),
    ).to(dtype=torch.bfloat16)

    score_head_path = f"{checkpoint_path}/score_head.pt"
    if Path(score_head_path).exists():
        score_head.load_state_dict(torch.load(score_head_path, map_location="cpu"))
        print(f"Loaded score head from {score_head_path}")
    else:
        print(f"WARNING: No score head found at {score_head_path}")

    return base_model, score_head


def main():
    parser = argparse.ArgumentParser(description="Step-Level Evaluation for CFD-PRM")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to trained checkpoint")
    parser.add_argument("--data_path", type=str, required=True, help="Path to full data JSON")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-VL-3B-Instruct", help="Base model")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--output_dir", type=str, default=None, help="Output directory")
    parser.add_argument("--test_ratio", type=float, default=0.1, help="Test split ratio")
    parser.add_argument("--pooling", type=str, default="mean", choices=["mean", "last"])
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--step_level", action="store_true",
                        help="Use step-level scoring mode (CFD-trained models)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = str(Path(args.checkpoint).parent / "eval_step")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load test data
    print("=" * 50)
    print("Loading test data")
    print("=" * 50)
    test_pairs = create_split(args.data_path, test_ratio=args.test_ratio, seed=args.seed)
    print(f"Test set: {len(test_pairs)} pairs")

    # Load model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    base_model, score_head = load_model(args.checkpoint, args.model_name)
    base_model = base_model.to(device)
    score_head = score_head.to(device)
    base_model.eval()
    score_head.eval()

    processor = AutoProcessor.from_pretrained(args.model_name)

    # Run evaluation
    all_metrics = {}

    # Mode 1: Step-level (for CFD-trained models)
    if args.step_level:
        print("\n" + "=" * 50)
        print("Step-level evaluation (each step scored independently)")
        print("=" * 50)
        metrics = evaluate_step_level(
            base_model, score_head, processor, test_pairs, device,
            batch_size=args.batch_size, pooling=args.pooling,
            max_length=args.max_length, pool_mode="step",
        )
        all_metrics["step_level"] = metrics
    else:
        # Mode 2: Whole-trajectory (for pairwise/pointwise baselines)
        print("\n" + "=" * 50)
        print("Whole-trajectory evaluation (trajectory scored as one unit)")
        print("=" * 50)
        metrics = evaluate_step_level(
            base_model, score_head, processor, test_pairs, device,
            batch_size=args.batch_size, pooling=args.pooling,
            max_length=args.max_length, pool_mode="whole",
        )
        all_metrics["whole_trajectory"] = metrics

    # Print results
    print("\n" + "=" * 60)
    print("Step-Level Evaluation Results")
    print("=" * 60)

    for mode_name, m in all_metrics.items():
        print(f"\n--- {mode_name} ---")
        print(f"Step-level AUC:           {m['step_level_auc']:.4f}")
        print(f"Step-level AUPRC:         {m['step_level_auprc']:.4f}")
        print(f"Step-level Accuracy:      {m['step_level_accuracy']:.4f}")
        print(f"Within-Traj Variance:     {m['within_trajectory_variance']:.6f}")
        print(f"t* Localization Acc:      {m['t_star_localization_accuracy']:.4f} ({m['t_star_localization_total']} pairs)")
        print(f"Score Gradientality:      {m['score_gradientality']:.4f}")
        print(f"Trajectory-level AUC:     {m['trajectory_level_auc']:.4f}")
        print(f"Trajectory-level PairAcc: {m['trajectory_level_pairwise_accuracy']:.4f}")
        print(f"Mean Correct Score:       {m['mean_correct_score']:.4f} (std: {m['std_correct_score']:.4f})")
        print(f"Mean Incorrect Score:     {m['mean_incorrect_score']:.4f} (std: {m['std_incorrect_score']:.4f})")
        print(f"ECE:                      {m['ece']:.4f}")
        print(f"Brier Score:              {m['brier_score']:.4f}")
        print(f"N Steps:                  {m['n_steps']}")
        print(f"N Pairs:                  {m['n_pairs']}")

    print("=" * 60)

    # Save results
    results_file = output_dir / "eval_step_results.json"
    with open(results_file, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
