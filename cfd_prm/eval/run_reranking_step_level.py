"""
Full Reranking (Step-Level): Run on all 3 models with image-based scoring.

Same as run_reranking_all.py but WITHOUT --whole_trajectory flag,
so it scores each step independently with images.

Models are distributed across GPU 2 and 3 for parallel execution.
"""
import subprocess
import json
import sys
import os

CHECKPOINTS = {
    "cfd_bce": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/step_level_v3_dual_loss/checkpoints/best",
    "bce_only": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/step_level_bce_only/checkpoints/best",
    "all_wrong_ranking": "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs/all_wrong_ranking/checkpoints/best",
}

DATA_PATH = "/hpc2hdd/home/ycui785/github_clone/cfd-prm/data/visualprm400k_converted/visualprm400k_pairs.json"
MODEL_NAME = "/hpc2hdd/home/ycui785/model/qwen2_5_vl_3b"
OUTPUT_BASE = "/hpc2hdd/home/ycui785/github_clone/cfd-prm/outputs"

# Distribute models across GPUs
MODEL_GPU = {
    "cfd_bce": "2",
    "bce_only": "3",
    "all_wrong_ranking": "2",  # runs after cfd_bce on same GPU
}

PYTHON = "/hpc2hdd/home/ycui785/anaconda3/envs/nips27/bin/python"

processes = {}

for name, ckpt in CHECKPOINTS.items():
    output_dir = f"{OUTPUT_BASE}/{name}/eval_reranking_step_level"
    gpu = MODEL_GPU[name]

    cmd = [
        PYTHON, "-m", "cfd_prm.eval.eval_reranking",
        "--checkpoint", ckpt,
        "--data_path", DATA_PATH,
        "--model_name", MODEL_NAME,
        "--output_dir", output_dir,
        "--pooling", "last",
        "--batch_size", "4",  # smaller due to image-based scoring
    ]
    # No --whole_trajectory flag = step-level with images

    print(f"\n{'='*60}")
    print(f"Starting step-level reranking: {name} on GPU {gpu}")
    print(f"{'='*60}")

    env = {**dict(os.environ), "CUDA_VISIBLE_DEVICES": gpu}
    log_file = f"{OUTPUT_BASE}/reranking_step_level_{name}.log"
    with open(log_file, "w") as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
        processes[name] = (p, log_file, gpu)

# Wait for all processes
for name, (p, log_file, gpu) in processes.items():
    print(f"\nWaiting for {name} (GPU {gpu})...")
    p.wait()
    if p.returncode != 0:
        print(f"ERROR: {name} failed with exit code {p.returncode}")
        print(f"See {log_file} for details")
        sys.exit(1)
    print(f"  {name} completed.")

# Load and print results
print("\n" + "=" * 60)
print("STEP-LEVEL RERANKING RESULTS")
print("=" * 60)
for name in CHECKPOINTS:
    results_path = f"{OUTPUT_BASE}/{name}/eval_reranking_step_level/reranking_results.json"
    with open(results_path) as f:
        results = json.load(f)
    print(f"\n{name}:")
    print(f"  Pairwise accuracy: {results['pairwise_accuracy']:.4f}")
    print(f"  Top-1 accuracy: {results['top1_accuracy']:.4f}")
    print(f"  Avg margin: {results['avg_margin']:.4f}")
    for k, v in results.get('bon_accuracies', {}).items():
        print(f"  {k}: {v:.4f}")

print("\nAll models evaluated successfully.")
