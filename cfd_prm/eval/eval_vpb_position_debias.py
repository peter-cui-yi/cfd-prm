"""
Position-Debiased VPB Inference Check

Re-score VPB data with CFD+BCE model, then apply post-hoc position debiasing
to remove the learned position prior. Compare AUC before vs after.

Methods:
  1. Simple mean subtraction: score' = score - mean_score(position) + global_mean
  2. LogReg residual: train logistic regression on (step_index, score) -> label,
     use score as primary feature and check coefficient of score vs step_index
  3. Rank-based: within each position, convert scores to percentile ranks

Usage:
    python -m cfd_prm.eval.eval_vpb_position_debias \
        --checkpoint outputs/step_level_v3_dual_loss/checkpoints/best \
        --data_path /hpc2hdd/home/ycui785/github_clone/VisualProcessBench/test.jsonl \
        --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
        --output_dir outputs/step_level_v3_dual_loss/eval_vpb_position_debias \
        --batch_size 4
"""

import json
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from peft import PeftModel
from PIL import Image
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.linear_model import LogisticRegression


class VPBDataset(Dataset):
    def __init__(self, data_path, processor):
        self.processor = processor
        self.items = []
        with open(data_path) as f:
            for item_idx, line in enumerate(f):
                item = json.loads(line)
                question = item["question"]
                steps = item["response"]["steps"]
                correctness = item["response"]["process_correctness"]
                image_paths_raw = item.get("image", [])
                images = []
                for img_path in image_paths_raw:
                    full_path = Path(data_path).parent / img_path
                    if full_path.exists():
                        try:
                            images.append(Image.open(full_path).convert("RGB"))
                        except Exception:
                            pass
                for step_i in range(len(steps)):
                    if step_i >= len(correctness):
                        continue
                    label = correctness[step_i]
                    if label == -1:
                        continue
                    prefix = "\n".join(steps[:step_i + 1])
                    query = (
                        f"Question: {question}\n\n"
                        f"Step-by-step reasoning:\n{prefix}\n\n"
                        f"Is this step correct? Answer YES or NO."
                    )
                    content = []
                    for _img in images:
                        content.append({"type": "image"})
                    content.append({"type": "text", "text": query})
                    conv = [{"role": "user", "content": content}]
                    text = processor.apply_chat_template(conv, tokenize=False)
                    self.items.append({
                        "text": text,
                        "images": images,
                        "label": label,
                        "step_idx": step_i,
                        "item_idx": item_idx,
                    })

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]


def collate_fn(batch, processor=None):
    texts = [item["text"] for item in batch]
    labels = [item["label"] for item in batch]
    step_idxs = [item["step_idx"] for item in batch]
    item_idxs = [item["item_idx"] for item in batch]
    all_images = []
    for item in batch:
        all_images.extend(item["images"])
    if all_images and len(all_images) == len(texts):
        inputs = processor(text=texts, images=all_images, return_tensors="pt", padding=True)
    else:
        inputs = processor(text=texts, return_tensors="pt", padding=True)
    return {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "pixel_values": inputs.get("pixel_values"),
        "image_grid_thw": inputs.get("image_grid_thw"),
        "labels": torch.tensor(labels, dtype=torch.float),
        "step_idxs": torch.tensor(step_idxs, dtype=torch.long),
        "item_idxs": torch.tensor(item_idxs, dtype=torch.long),
    }


@torch.no_grad()
def run_inference(checkpoint_path, model_name, data_path, device, batch_size=4):
    print("Loading model...")
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name, torch_dtype=torch.bfloat16,
    )
    base_model = PeftModel.from_pretrained(base_model, checkpoint_path)
    base_model.eval().to(device)

    score_head = nn.Sequential(
        nn.Linear(base_model.config.hidden_size, 256),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(256, 1),
    ).to(dtype=torch.bfloat16)
    sh_path = f"{checkpoint_path}/score_head.pt"
    score_head.load_state_dict(torch.load(sh_path, map_location="cpu"))
    score_head.eval().to(device)

    processor = AutoProcessor.from_pretrained(model_name)

    print("Loading VPB data...")
    dataset = VPBDataset(data_path, processor)
    print(f"  {len(dataset)} steps")

    from functools import partial
    loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=False,
        collate_fn=partial(collate_fn, processor=processor),
    )

    all_scores = []
    all_labels = []
    all_step_idxs = []

    for batch in tqdm(loader, desc="Scoring VPB"):
        ids = batch["input_ids"].to(device)
        mask = batch["attention_mask"].to(device)
        labels = batch["labels"]
        pvals = batch.get("pixel_values")
        grid = batch.get("image_grid_thw")
        if pvals is not None:
            pvals = pvals.to(device)
        if grid is not None:
            grid = grid.to(device)

        try:
            outs = base_model(
                input_ids=ids, attention_mask=mask,
                pixel_values=pvals, image_grid_thw=grid,
                output_hidden_states=True,
            )
            hidden = outs.hidden_states[-1]
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"\n  WARNING: OOM, skipping batch. Seq lengths: {mask.sum(dim=1).tolist()}")
                torch.cuda.empty_cache()
                continue
            raise

        seq_lens = mask.sum(dim=1)
        bi = torch.arange(mask.size(0), device=hidden.device)
        pooled = hidden[bi, seq_lens - 1]
        logits = score_head(pooled)
        scores = torch.sigmoid(logits).squeeze(-1)

        all_scores.extend(scores.cpu().float().numpy().tolist())
        all_labels.extend(labels.numpy().tolist())
        all_step_idxs.extend(batch["step_idxs"].numpy().tolist())

    return np.array(all_scores), np.array(all_labels), np.array(all_step_idxs)


def position_debias_mean_subtract(scores, step_idxs):
    """
    Method 1: Subtract per-position mean, add global mean.
    score' = score - mean_score(step_idx) + global_mean
    """
    global_mean = scores.mean()
    pos_means = {}
    for s, idx in zip(scores, step_idxs):
        if idx not in pos_means:
            pos_means[idx] = []
        pos_means[idx].append(s)

    for k in pos_means:
        pos_means[k] = np.mean(pos_means[k])

    debiased = np.zeros_like(scores)
    for i, (s, idx) in enumerate(zip(scores, step_idxs)):
        debiased[i] = s - pos_means[idx] + global_mean

    return debiased, pos_means


def position_debias_percentile(scores, step_idxs):
    """
    Method 2: Within each position, convert scores to percentile ranks.
    This is fully position-invariant.
    """
    debiased = np.zeros_like(scores)
    unique_positions = np.unique(step_idxs)
    for pos in unique_positions:
        mask = step_idxs == pos
        pos_scores = scores[mask]
        # Percentile rank: (rank - 0.5) / n
        ranks = np.argsort(np.argsort(pos_scores))
        n = len(pos_scores)
        percentiles = (ranks + 0.5) / n
        debiased[mask] = percentiles
    return debiased


def position_debias_logreg(scores, step_idxs, labels):
    """
    Method 3: Train LogReg on (score, step_index) -> label.
    Then use only the score component for prediction:
    P(label=1) ~ sigmoid(w_score * score + intercept)
    This isolates the score's contribution from position.

    Alternatively: compute residuals = score - predicted_score_from_position
    Then evaluate residuals as predictors.
    """
    # Fit position -> score relationship
    from sklearn.ensemble import RandomForestRegressor
    pos_features = step_idxs.reshape(-1, 1)
    rf = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    rf.fit(pos_features, scores)
    predicted_scores = rf.predict(pos_features)

    # Residual: score - expected_score_at_position
    residuals = scores - predicted_scores

    # Also try: LogReg with both features, then use only score's contribution
    lr = LogisticRegression()
    features = np.column_stack([scores, step_idxs])
    lr.fit(features, labels)

    return residuals, lr, rf


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data_path", required=True)
    parser.add_argument("--model_name", default="/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    device = "cuda"
    scores, labels, step_idxs = run_inference(
        args.checkpoint, args.model_name, args.data_path, device, args.batch_size,
    )

    # ====== Baseline metrics ======
    print("\n" + "=" * 60)
    print("BASELINE: Raw scores (no debiasing)")
    print("=" * 60)
    auc_raw = roc_auc_score(labels, scores)
    auprc_raw = average_precision_score(labels, scores)
    mu_c = scores[labels == 1].mean()
    mu_i = scores[labels == 0].mean()
    print(f"  AUC:       {auc_raw:.4f}")
    print(f"  AUPRC:     {auprc_raw:.4f}")
    print(f"  μ(correct):   {mu_c:.4f}")
    print(f"  μ(incorrect): {mu_i:.4f}")
    print(f"  Δ(c-i):    {mu_c - mu_i:.4f}")

    # ====== Method 1: Mean subtract ======
    print("\n" + "=" * 60)
    print("METHOD 1: Per-position mean subtraction")
    print("=" * 60)
    debiased_1, pos_means = position_debias_mean_subtract(scores, step_idxs)
    auc_1 = roc_auc_score(labels, debiased_1)
    auprc_1 = average_precision_score(labels, debiased_1)
    mu_c1 = debiased_1[labels == 1].mean()
    mu_i1 = debiased_1[labels == 0].mean()
    print(f"  AUC:       {auc_1:.4f}  (baseline: {auc_raw:.4f})")
    print(f"  AUPRC:     {auprc_1:.4f}  (baseline: {auprc_raw:.4f})")
    print(f"  μ(correct):   {mu_c1:.4f}")
    print(f"  μ(incorrect): {mu_i1:.4f}")
    print(f"  Δ(c-i):    {mu_c1 - mu_i1:.4f}  (baseline: {mu_c - mu_i:.4f})")

    # ====== Method 2: Percentile rank ======
    print("\n" + "=" * 60)
    print("METHOD 2: Within-position percentile ranks")
    print("=" * 60)
    debiased_2 = position_debias_percentile(scores, step_idxs)
    auc_2 = roc_auc_score(labels, debiased_2)
    auprc_2 = average_precision_score(labels, debiased_2)
    mu_c2 = debiased_2[labels == 1].mean()
    mu_i2 = debiased_2[labels == 0].mean()
    print(f"  AUC:       {auc_2:.4f}  (baseline: {auc_raw:.4f})")
    print(f"  AUPRC:     {auprc_2:.4f}  (baseline: {auprc_raw:.4f})")
    print(f"  μ(correct):   {mu_c2:.4f}")
    print(f"  μ(incorrect): {mu_i2:.4f}")
    print(f"  Δ(c-i):    {mu_c2 - mu_i2:.4f}  (baseline: {mu_c - mu_i:.4f})")

    # ====== Method 3: Residual ======
    print("\n" + "=" * 60)
    print("METHOD 3: Position-predicted score residuals")
    print("=" * 60)
    residuals, lr_model, rf_model = position_debias_logreg(scores, step_idxs, labels)
    auc_3 = roc_auc_score(labels, residuals)
    auprc_3 = average_precision_score(labels, residuals)
    mu_c3 = residuals[labels == 1].mean()
    mu_i3 = residuals[labels == 0].mean()
    print(f"  AUC:       {auc_3:.4f}  (baseline: {auc_raw:.4f})")
    print(f"  AUPRC:     {auprc_3:.4f}  (baseline: {auprc_raw:.4f})")
    print(f"  μ(correct):   {mu_c3:.4f}")
    print(f"  μ(incorrect): {mu_i3:.4f}")
    print(f"  Δ(c-i):    {mu_c3 - mu_i3:.4f}  (baseline: {mu_c - mu_i:.4f})")

    # LogReg coefficients
    print(f"  LogReg w_score:   {lr_model.coef_[0][0]:.4f}")
    print(f"  LogReg w_position: {lr_model.coef_[0][1]:.4f}")
    print(f"  LogReg intercept:  {lr_model.intercept_[0]:.4f}")

    # Also try LogReg with score only (no position)
    lr_score_only = LogisticRegression()
    lr_score_only.fit(scores.reshape(-1, 1), labels)
    probs_score_only = lr_score_only.predict_proba(scores.reshape(-1, 1))[:, 1]
    auc_score_only = roc_auc_score(labels, probs_score_only)
    print(f"  LogReg(score only) AUC: {auc_score_only:.4f}")

    # LogReg with position only
    lr_pos_only = LogisticRegression()
    lr_pos_only.fit(step_idxs.reshape(-1, 1), labels)
    probs_pos_only = lr_pos_only.predict_proba(step_idxs.reshape(-1, 1))[:, 1]
    auc_pos_only = roc_auc_score(labels, probs_pos_only)
    print(f"  LogReg(position only) AUC: {auc_pos_only:.4f}")

    # LogReg with both
    lr_both = LogisticRegression()
    lr_both.fit(np.column_stack([scores, step_idxs]), labels)
    probs_both = lr_both.predict_proba(np.column_stack([scores, step_idxs]))[:, 1]
    auc_both = roc_auc_score(labels, probs_both)
    print(f"  LogReg(score+position) AUC: {auc_both:.4f}")

    # ====== Per-position AUC comparison ======
    print("\n" + "=" * 60)
    print("PER-POSITION AUC: raw vs debiased (Method 1)")
    print("=" * 60)
    for pos in sorted(pos_means.keys()):
        mask = step_idxs == pos
        n = mask.sum()
        n_c = labels[mask].sum()
        n_i = n - n_c
        if n_c == 0 or n_i == 0:
            print(f"  step {pos}: n={n}, c={n_c}, i={n_i} (skip)")
            continue
        auc_p_raw = roc_auc_score(labels[mask], scores[mask])
        auc_p_deb = roc_auc_score(labels[mask], debiased_1[mask])
        print(f"  step {pos}: n={n}, c={n_c}, i={n_i}, AUC_raw={auc_p_raw:.4f}, AUC_deb={auc_p_deb:.4f}")

    # ====== Save results ======
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "baseline": {
            "auc": float(auc_raw),
            "auprc": float(auprc_raw),
            "mean_correct": float(mu_c),
            "mean_incorrect": float(mu_i),
            "delta": float(mu_c - mu_i),
        },
        "method1_mean_subtract": {
            "auc": float(auc_1),
            "auprc": float(auprc_1),
            "mean_correct": float(mu_c1),
            "mean_incorrect": float(mu_i1),
            "delta": float(mu_c1 - mu_i1),
            "position_means": {str(k): float(v) for k, v in pos_means.items()},
        },
        "method2_percentile": {
            "auc": float(auc_2),
            "auprc": float(auprc_2),
            "mean_correct": float(mu_c2),
            "mean_incorrect": float(mu_i2),
            "delta": float(mu_c2 - mu_i2),
        },
        "method3_residual": {
            "auc": float(auc_3),
            "auprc": float(auprc_3),
            "mean_correct": float(mu_c3),
            "mean_incorrect": float(mu_i3),
            "delta": float(mu_c3 - mu_i3),
            "logreg_w_score": float(lr_model.coef_[0][0]),
            "logreg_w_position": float(lr_model.coef_[0][1]),
        },
        "logreg_comparison": {
            "score_only_auc": float(auc_score_only),
            "position_only_auc": float(auc_pos_only),
            "score_plus_position_auc": float(auc_both),
        },
        "n_steps": int(len(scores)),
    }

    with open(output_dir / "vpb_position_debias.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_dir / 'vpb_position_debias.json'}")


if __name__ == "__main__":
    main()
