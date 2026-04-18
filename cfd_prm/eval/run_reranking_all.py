"""
Full Reranking Experiment: Run on all 3 models sequentially.

Evaluates CFD+BCE, BCE-only, and all_wrong_ranking on reranking task.
Uses text-only whole-trajectory scoring (consistent with existing eval_step_level.py).
"""
import subprocess
import json
import sys

CHECKPOINTS = {
    "cfd_bce": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/step_level_v3_dual_loss/checkpoints/best",
    "bce_only": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/step_level_bce_only/checkpoints/best",
    "all_wrong_ranking": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/all_wrong_ranking/checkpoints/best",
}

DATA_PATH = "/hpc2hdd/home/ycui785/github_clone/cfd-prm/data/visualprm400k_converted/visualprm400k_pairs.json"
MODEL_NAME = "/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b"
OUTPUT_BASE = "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs"
GPU = "2"

PYTHON = "/hpc2hdd/home/ycui785/anaconda3/envs/nips27/bin/python"

for name, ckpt in CHECKPOINTS.items():
    output_dir = f"{OUTPUT_BASE}/{name}/eval_reranking"
    print(f"\n{'='*60}")
    print(f"Running reranking for: {name}")
    print(f"{'='*60}")

    cmd = [
        PYTHON, "-m", "cfd_prm.eval.eval_reranking",
        "--checkpoint", ckpt,
        "--data_path", DATA_PATH,
        "--model_name", MODEL_NAME,
        "--output_dir", output_dir,
        "--pooling", "last",
        "--batch_size", "32",
        "--whole_trajectory",
    ]

    env = {"CUDA_VISIBLE_DEVICES": GPU}
    result = subprocess.run(cmd, capture_output=False, text=True, env={**dict(__import__('os').environ), **env})

    if result.returncode != 0:
        print(f"ERROR: {name} failed with exit code {result.returncode}")
        sys.exit(1)

    # Load and print results
    results_path = f"{output_dir}/reranking_results.json"
    with open(results_path) as f:
        results = json.load(f)
    print(f"\n  Pairwise accuracy: {results['pairwise_accuracy']:.4f}")
    print(f"  Top-1 accuracy: {results['top1_accuracy']:.4f}")
    print(f"  Avg margin: {results['avg_margin']:.4f}")
    for k, v in results.get('bon_accuracies', {}).items():
        print(f"  {k}: {v:.4f}")

print("\nAll models evaluated successfully.")
