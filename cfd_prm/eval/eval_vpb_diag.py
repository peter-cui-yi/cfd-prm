"""
VPB Deep Diagnostic: score direction, position bias, filtered subsets.
Checks 4 competing explanations for VPB AUC < 0.5.
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


class VPBDiagDataset(Dataset):
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


def diag_collate_fn(batch, processor=None):
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
def run_diag(checkpoint_path, model_name, data_path, device, batch_size=8):
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
    dataset = VPBDiagDataset(data_path, processor)
    print(f"  {len(dataset)} steps")

    from functools import partial
    loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=False,
        collate_fn=partial(diag_collate_fn, processor=processor),
    )

    all_scores = []
    all_labels = []
    all_step_idxs = []
    all_item_idxs = []

    for batch in tqdm(loader, desc="Evaluating"):
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
                print(f"\n  WARNING: OOM at batch, skipping. Seq lengths: {mask.sum(dim=1).tolist()}")
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
        all_item_idxs.extend(batch["item_idxs"].numpy().tolist())

    return np.array(all_scores), np.array(all_labels), np.array(all_step_idxs), np.array(all_item_idxs)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data_path", required=True)
    parser.add_argument("--model_name", default="/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    device = "cuda"
    scores, labels, step_idxs, item_idxs = run_diag(
        args.checkpoint, args.model_name, args.data_path, device, args.batch_size,
    )

    # ====== Check 1: Score direction sanity ======
    print("\n" + "=" * 60)
    print("CHECK 1: Score Direction Sanity")
    print("=" * 60)
    auc_normal = roc_auc_score(labels, scores)
    auc_flipped = roc_auc_score(labels, 1 - scores)
    auprc_correct = average_precision_score(labels, scores)
    auprc_incorrect = average_precision_score(1 - labels, scores)
    mu_correct = scores[labels == 1].mean()
    mu_incorrect = scores[labels == 0].mean()

    print(f"  AUC(score):            {auc_normal:.4f}")
    print(f"  AUC(1-score):          {auc_flipped:.4f}")
    print(f"  AUPRC(pos=correct):    {auprc_correct:.4f}")
    print(f"  AUPRC(pos=incorrect):  {auprc_incorrect:.4f}")
    print(f"  μ(correct):            {mu_correct:.4f}")
    print(f"  μ(incorrect):          {mu_incorrect:.4f}")
    print(f"  Δ(correct-incorrect):  {mu_correct - mu_incorrect:.4f}")

    if auc_flipped > 0.5 and auc_normal < 0.5:
        print("  >> Systematic REVERSAL detected: 1-score performs much better")

    # ====== Check 2: Position-only baseline ======
    print("\n" + "=" * 60)
    print("CHECK 2: Position-Only Baseline")
    print("=" * 60)
    neg_step_index = -step_idxs.astype(float)
    neg_step_norm = (neg_step_index - neg_step_index.min()) / (neg_step_index.max() - neg_step_index.min() + 1e-9)
    auc_pos = roc_auc_score(labels, neg_step_norm)
    print(f"  AUC(-step_index): {auc_pos:.4f}")

    lr = LogisticRegression()
    lr.fit(step_idxs.reshape(-1, 1), labels)
    lr_probs = lr.predict_proba(step_idxs.reshape(-1, 1))[:, 1]
    auc_lr = roc_auc_score(labels, lr_probs)
    print(f"  AUC(LogReg step_index): {auc_lr:.4f}")
    print(f"  LogReg coefficient: {lr.coef_[0][0]:.4f}")
    print(f"  LogReg intercept: {lr.intercept_[0]:.4f}")

    # ====== Check 3: Position-stratified analysis ======
    print("\n" + "=" * 60)
    print("CHECK 3: Position-Stratified Analysis")
    print("=" * 60)
    for pos_range, pos_mask in [
        ("step 0", step_idxs == 0),
        ("step 1", step_idxs == 1),
        ("step 2-3", (step_idxs >= 2) & (step_idxs <= 3)),
        ("step 4+", step_idxs >= 4),
    ]:
        n_total = pos_mask.sum()
        n_correct = labels[pos_mask].sum()
        n_incorrect = n_total - n_correct
        if n_correct == 0 or n_incorrect == 0:
            print(f"  {pos_range}: n={n_total}, correct={n_correct}, incorrect={n_incorrect} (skip AUC)")
            continue
        mu_c = scores[pos_mask][labels[pos_mask] == 1].mean()
        mu_i = scores[pos_mask][labels[pos_mask] == 0].mean()
        auc_p = roc_auc_score(labels[pos_mask], scores[pos_mask])
        auprc_p = average_precision_score(labels[pos_mask], scores[pos_mask])
        print(f"  {pos_range}: n={n_total}, correct={n_correct}, incorrect={n_incorrect}, "
              f"AUC={auc_p:.4f}, AUPRC={auprc_p:.4f}, μ(c)={mu_c:.4f}, μ(i)={mu_i:.4f}")

    # ====== Check 4: Filtered subset analysis ======
    print("\n" + "=" * 60)
    print("CHECK 4: Filtered Subset Analysis")
    print("=" * 60)

    # Build per-item first_incorrect position
    unique_items = np.unique(item_idxs)
    first_incorrect = {}
    for ui in unique_items:
        mask = item_idxs == ui
        item_labels = labels[mask]
        item_step_idxs = step_idxs[mask]
        for s, l in zip(item_step_idxs, item_labels):
            if l == 0:
                first_incorrect[ui] = s
                break
        if ui not in first_incorrect:
            first_incorrect[ui] = -1  # all correct

    # Check recovery patterns (1->0->1)
    recovery_count = 0
    monotonic_count = 0
    non_mono_count = 0
    for ui in unique_items:
        mask = item_idxs == ui
        item_labels = labels[mask]
        item_step_idxs = step_idxs[mask]
        sorted_order = np.argsort(item_step_idxs)
        sorted_labels = item_labels[sorted_order]
        found_error = False
        recovered = False
        for l in sorted_labels:
            if l == 0:
                found_error = True
            elif found_error and l == 1:
                recovered = True
                break
        if recovered:
            recovery_count += 1
            non_mono_count += 1
        elif found_error:
            monotonic_count += 1
        # all correct -> neither

    print(f"  Total items: {len(unique_items)}")
    print(f"  All correct: {len(unique_items) - len([k for k, v in first_incorrect.items() if v >= 0])}")
    print(f"  With errors (monotonic): {monotonic_count}")
    print(f"  With errors (non-monotonic / recovery): {recovery_count}")

    # Subset A: first_incorrect > 0
    mask_a = np.array([first_incorrect.get(ii, -1) > 0 for ii in item_idxs])
    # Subset B: items where error pattern is monotonic (no recovery)
    mono_items = set()
    for ui in unique_items:
        if first_incorrect.get(ui, -1) < 0:
            continue  # all correct, skip
        mask = item_idxs == ui
        item_labels = labels[mask]
        item_step_idxs = step_idxs[mask]
        sorted_order = np.argsort(item_step_idxs)
        sorted_labels = item_labels[sorted_order]
        found_error = False
        recovered = False
        for l in sorted_labels:
            if l == 0:
                found_error = True
            elif found_error and l == 1:
                recovered = True
                break
        if not recovered:
            mono_items.add(ui)
    mask_b = np.array([ii in mono_items for ii in item_idxs])

    # Subset C: A ∩ B
    mask_c = mask_a & mask_b

    for name, mask in [
        ("Full VPB", np.ones(len(labels), dtype=bool)),
        ("Subset A: first_incorrect > 0", mask_a),
        ("Subset B: monotonic error", mask_b),
        ("Subset C: A ∩ B (matched)", mask_c),
        ("Step 0 excluded", step_idxs > 0),
    ]:
        n = mask.sum()
        n_c = labels[mask].sum()
        n_i = n - n_c
        if n_c == 0 or n_i == 0:
            print(f"  {name}: n={n} (skip)")
            continue
        auc_s = roc_auc_score(labels[mask], scores[mask])
        auprc_s = average_precision_score(labels[mask], scores[mask])
        mu_cs = scores[mask][labels[mask] == 1].mean()
        mu_is = scores[mask][labels[mask] == 0].mean()
        print(f"  {name}: n={n}, c={n_c}, i={n_i}, AUC={auc_s:.4f}, AUPRC={auprc_s:.4f}, "
              f"μ(c)={mu_cs:.4f}, μ(i)={mu_is:.4f}, Δ={mu_cs - mu_is:.4f}")

    # Save everything
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    diag = {
        "check1_direction": {
            "auc_score": float(auc_normal),
            "auc_1_minus_score": float(auc_flipped),
            "auprc_correct": float(auprc_correct),
            "auprc_incorrect": float(auprc_incorrect),
            "mean_correct": float(mu_correct),
            "mean_incorrect": float(mu_incorrect),
        },
        "check2_position_baseline": {
            "auc_neg_step_index": float(auc_pos),
            "auc_logreg_step_index": float(auc_lr),
            "logreg_coef": float(lr.coef_[0][0]),
        },
        "n_steps": int(len(scores)),
        "n_items": int(len(unique_items)),
        "monotonic_items": monotonic_count,
        "recovery_items": recovery_count,
    }
    with open(output_dir / "vpb_diag.json", "w") as f:
        json.dump(diag, f, indent=2)
    print(f"\nResults saved to {output_dir / 'vpb_diag.json'}")


if __name__ == "__main__":
    main()
