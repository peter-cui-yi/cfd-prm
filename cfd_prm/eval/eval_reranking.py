"""
Reranking / Best-of-N Evaluation for CFD-PRM

Evaluates whether CFD-trained PRM can better select the correct answer
from a pool of candidates, compared to BCE-only and other baselines.

For each question, we have:
  - 1 reference trajectory (correct answer)
  - N deviated trajectories (varied answers, some correct, some wrong)

Metrics:
  - Pairwise ranking accuracy: ref scored higher than dev?
  - Top-1 selection accuracy: is reference ranked #1?
  - BoN@k accuracy: best of k candidates gives correct answer?
  - Score margin reliability: ref_score - dev_score correlation with answer quality

Usage:
    python -m cfd_prm.eval.eval_reranking \
        --checkpoint outputs/step_level_v3_dual_loss/checkpoints/best \
        --data_path data/visualprm400k_converted/visualprm400k_pairs.json \
        --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
        --output_dir outputs/step_level_v3_dual_loss/eval_reranking \
        --pooling last --batch_size 8
"""

import json
import argparse
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from sklearn.metrics import roc_auc_score
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from peft import PeftModel


class RerankTrajectory:
    """Single candidate trajectory for reranking."""
    def __init__(self, traj_id, trajectory, image_path, labels, is_reference, final_answer, question_text):
        self.traj_id = traj_id
        self.trajectory = trajectory
        self.image_path = image_path
        self.labels = labels
        self.is_reference = is_reference
        self.final_answer = final_answer
        self.question_text = question_text
        self.score = None  # PRM score (to be filled)


def build_rerank_groups(pairs):
    """
    Group pairs by question to form reranking candidate pools.
    Each group has 1 reference + N deviated trajectories.
    """
    groups = {}
    for pair in pairs:
        question = pair["question"]
        if question not in groups:
            groups[question] = {
                "question": question,
                "reference": pair["reference"],
                "deviateds": [],
            }
        groups[question]["deviateds"].append({
            "trajectory": pair["deviated"]["trajectory"],
            "image_path": pair["deviated"]["image_path"],
            "labels": pair["deviated"]["labels"],
            "t_star": pair["t_star"],
        })
    return list(groups.values())


def build_score_queries(trajectories, max_length=512):
    """
    Build queries for scoring each step in each trajectory.
    Returns list of (traj_id, step_idx, text, image_path, label)
    """
    queries = []
    for traj in trajectories:
        steps = traj.trajectory
        for step_i in range(len(steps)):
            prefix = "\n".join(steps[:step_i + 1])
            query = (
                f"Question: {traj.question_text}\n\n"
                f"Step-by-step reasoning:\n{prefix}\n\n"
                f"Is this step correct? Answer YES or NO."
            )
            queries.append((traj.traj_id, step_i, query, traj.image_path, traj.labels[step_i] if step_i < len(traj.labels) else 1))
    return queries


def compute_trajectory_score(traj, step_scores):
    """
    Compute trajectory-level score from step scores.
    Options: mean, min, last, product
    We use mean as default.
    """
    if not step_scores:
        return 0.0
    return np.mean(step_scores)


@torch.no_grad()
def score_trajectories(model, score_head, processor, trajectories, device, batch_size=8, max_length=512, pooling="last", whole_trajectory=False):
    """
    Score all trajectories.

    If whole_trajectory=True: score entire trajectory as one unit (faster, ~7x fewer queries)
    If whole_trajectory=False: score each step independently and average (more accurate for CFD model)
    """
    model.eval()
    score_head.eval()

    queries = []
    for traj in trajectories:
        if whole_trajectory:
            # Whole trajectory query
            traj_text = " | ".join(traj.trajectory)
            query = (
                f"Trajectory: {traj_text}\n\n"
                f"Is this trajectory correct? Answer YES or NO."
            )
            queries.append((traj.traj_id, query, traj.image_path))
        else:
            # Step-level queries
            steps = traj.trajectory
            for step_i in range(len(steps)):
                prefix = "\n".join(steps[:step_i + 1])
                query = (
                    f"Question: {traj.question_text}\n\n"
                    f"Step-by-step reasoning:\n{prefix}\n\n"
                    f"Is this step correct? Answer YES or NO."
                )
                queries.append((traj.traj_id, step_i, query, traj.image_path))

    # Group by image path for efficient batching
    image_groups = defaultdict(list)
    for q_idx, q in enumerate(queries):
        if whole_trajectory:
            traj_id, text, image_path = q
            image_groups[image_path].append((q_idx, traj_id, None, text))
        else:
            traj_id, step_idx, text, image_path = q
            image_groups[image_path].append((q_idx, traj_id, step_idx, text))

    # Score in batches
    all_scores = {}  # q_idx -> score

    for image_path, batch_queries in tqdm(image_groups.items(), desc="Scoring trajectories"):
        q_idxs = [q[0] for q in batch_queries]
        texts = [q[3] for q in batch_queries]

        inputs = processor(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
        )
        hidden_states = outputs.hidden_states[-1]

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
        scores = torch.sigmoid(logits).squeeze(-1).cpu().float().numpy()

        for i, q_idx in enumerate(q_idxs):
            all_scores[q_idx] = scores[i]

    # Aggregate scores into trajectory scores
    if whole_trajectory:
        for i, (traj_id, _, _) in enumerate(queries):
            for traj in trajectories:
                if traj.traj_id == traj_id:
                    traj.score = all_scores[i]
                    break
    else:
        traj_step_scores = defaultdict(list)
        query_idx = 0
        for image_path, batch_queries in image_groups.items():
            for local_i, (q_idx, traj_id, step_idx, text) in enumerate(batch_queries):
                traj_step_scores[traj_id].append(all_scores[q_idx])

        for traj in trajectories:
            scores = traj_step_scores.get(traj.traj_id, [])
            traj.score = np.mean(scores) if scores else 0.0

    return trajectories


def evaluate_reranking(groups, score_method, device, batch_size=8, max_length=512, pooling="last", model=None, score_head=None, processor=None):
    """
    Evaluate reranking performance.
    """
    results = {
        "pairwise_accuracy": [],
        "top1_accuracy": [],
        "bon_accuracies": {},  # bon@k -> accuracy
        "score_margins": [],
        "n_groups": len(groups),
        "n_pairs": 0,
    }

    for group in tqdm(groups, desc="Evaluating reranking"):
        question = group["question"]
        reference = group["reference"]
        deviateds = group["deviateds"]

        ref_answer = reference["trajectory"][-1]

        # Build all trajectories
        trajectories = []
        trajectories.append(RerankTrajectory(
            traj_id="ref",
            trajectory=reference["trajectory"],
            image_path=reference["image_path"],
            labels=reference["labels"],
            is_reference=True,
            final_answer=ref_answer,
            question_text=question,
        ))
        for di, dev in enumerate(deviateds):
            dev_answer = dev["trajectory"][-1]
            trajectories.append(RerankTrajectory(
                traj_id=f"dev_{di}",
                trajectory=dev["trajectory"],
                image_path=dev["image_path"],
                labels=dev["labels"],
                is_reference=False,
                final_answer=dev_answer,
                question_text=question,
            ))

        # Score all trajectories
        trajectories = score_method(trajectories)

        # Get scores
        ref_score = trajectories[0].score
        dev_scores = [t.score for t in trajectories[1:]]
        dev_answers = [t.final_answer for t in trajectories[1:]]

        results["n_pairs"] += len(deviateds)

        # Pairwise accuracy: ref scored higher than each dev?
        for ds in dev_scores:
            results["pairwise_accuracy"].append(1 if ref_score > ds else 0)

        # Score margin
        results["score_margins"].append({
            "ref_score": ref_score,
            "dev_scores": dev_scores,
            "ref_is_correct": True,
        })

        # Top-1 selection: is reference ranked #1?
        all_scores = [ref_score] + dev_scores
        max_score = max(all_scores)
        top1_is_ref = (ref_score == max_score)
        results["top1_accuracy"].append(1 if top1_is_ref else 0)

        # BoN@k: for k in [2, 4, 8], select best of k random candidates + ref
        for k in [2, 3, 4, 5]:
            if k - 1 > len(deviateds):
                continue
            if f"bon@{k}" not in results["bon_accuracies"]:
                results["bon_accuracies"][f"bon@{k}"] = []

            # Try all combinations of k-1 devs + ref
            from itertools import combinations
            bon_correct = 0
            bon_total = 0
            for dev_subset in combinations(range(len(deviateds)), min(k - 1, len(deviateds))):
                candidate_scores = [ref_score] + [dev_scores[i] for i in dev_subset]
                candidate_answers = [ref_answer] + [dev_answers[i] for i in dev_subset]

                # Select best by score
                best_idx = np.argmax(candidate_scores)
                best_answer = candidate_answers[best_idx]

                # Check if best answer matches reference (correct) answer
                bon_correct += (1 if best_answer == ref_answer else 0)
                bon_total += 1

            if bon_total > 0:
                results["bon_accuracies"][f"bon@{k}"].append(bon_correct / bon_total)

    # Aggregate
    results["pairwise_accuracy"] = np.mean(results["pairwise_accuracy"]) if results["pairwise_accuracy"] else 0
    results["top1_accuracy"] = np.mean(results["top1_accuracy"]) if results["top1_accuracy"] else 0

    for k in results["bon_accuracies"]:
        results["bon_accuracies"][k] = np.mean(results["bon_accuracies"][k]) if results["bon_accuracies"][k] else 0

    # Average margin
    margins = []
    for m in results["score_margins"]:
        for ds in m["dev_scores"]:
            margins.append(m["ref_score"] - ds)
    results["avg_margin"] = np.mean(margins) if margins else 0
    results["margin_std"] = np.std(margins) if margins else 0

    # Remove per-group details
    results["score_margins"] = []

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data_path", required=True)
    parser.add_argument("--model_name", default="/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b")
    parser.add_argument("--pooling", default="last")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--subset", type=int, default=None, help="Evaluate only first N questions for testing")
    parser.add_argument("--whole_trajectory", action="store_true", help="Score whole trajectory instead of per-step")
    args = parser.parse_args()

    device = "cuda"

    # Load model
    print("Loading model...")
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model_name, torch_dtype=torch.bfloat16,
    )
    base_model = PeftModel.from_pretrained(base_model, args.checkpoint)
    base_model.eval().to(device)

    score_head = nn.Sequential(
        nn.Linear(base_model.config.hidden_size, 256),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(256, 1),
    ).to(dtype=torch.bfloat16)
    sh_path = f"{args.checkpoint}/score_head.pt"
    score_head.load_state_dict(torch.load(sh_path, map_location="cpu"))
    score_head.eval().to(device)

    processor = AutoProcessor.from_pretrained(args.model_name)

    # Load data
    print("Loading data...")
    with open(args.data_path) as f:
        pairs = json.load(f)

    groups = build_rerank_groups(pairs)
    print(f"  {len(groups)} unique questions")
    print(f"  Avg candidates per question: {np.mean([len(g['deviateds']) + 1 for g in groups]):.1f}")

    if args.subset:
        groups = groups[:args.subset]
        print(f"  Using subset: {len(groups)} questions")

    # Build score function with closures
    def score_trajectories_closure(trajectories):
        return score_trajectories(
            base_model, score_head, processor, trajectories,
            device, args.batch_size, args.max_length, args.pooling,
            whole_trajectory=args.whole_trajectory,
        )

    # Run evaluation
    print("\nRunning reranking evaluation...")
    results = evaluate_reranking(
        groups, score_trajectories_closure, device,
        args.batch_size, args.max_length, args.pooling,
    )

    # Print results
    print("\n" + "=" * 60)
    print("RERANKING RESULTS")
    print("=" * 60)
    print(f"  Questions: {results['n_groups']}")
    print(f"  Pairs evaluated: {results['n_pairs']}")
    print(f"  Pairwise accuracy: {results['pairwise_accuracy']:.4f}")
    print(f"  Top-1 selection accuracy: {results['top1_accuracy']:.4f}")
    print(f"  Avg score margin (ref-dev): {results['avg_margin']:.4f} (+/- {results['margin_std']:.4f})")
    for k, acc in sorted(results["bon_accuracies"].items()):
        print(f"  BoN@{k} accuracy: {acc:.4f}")

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert numpy types to Python types for JSON serialization
    json_results = {}
    for k, v in results.items():
        if isinstance(v, dict):
            json_results[k] = {kk: float(vv) for kk, vv in v.items()}
        elif hasattr(v, 'item'):
            json_results[k] = v.item()
        else:
            json_results[k] = v
    json_results["bon_accuracies"] = {k: float(v) for k, v in results.get("bon_accuracies", {}).items()}

    with open(output_dir / "reranking_results.json", "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"\nResults saved to {output_dir / 'reranking_results.json'}")


if __name__ == "__main__":
    main()
