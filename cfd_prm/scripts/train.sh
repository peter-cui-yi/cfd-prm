#!/bin/bash
# Quick start script for CFD-PRM training

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== CFD-PRM Quick Start ==="

# Check dependencies
echo "Checking dependencies..."
python -c "import torch; import transformers; import peft" || {
    echo "Error: Missing dependencies. Run: pip install -r cfd_prm/requirements.txt"
    exit 1
}

# Check data
if [ ! -f "data/hard_negatives/hard_negatives.json" ]; then
    echo "Error: Hard negative data not found."
    echo "Run hard negative mining first:"
    echo "  python -m cfd_prm.data.hard_negative_miner --input_dir data/agentic_mme --output_dir data/hard_negatives"
    exit 1
fi

# Multi-GPU support
NPROC_PER_NODE=${NPROC_PER_NODE:-1}

if [ "$NPROC_PER_NODE" -gt 1 ]; then
    echo "Launching multi-GPU training on $NPROC_PER_NODE GPUs"
    torchrun --nproc_per_node=$NPROC_PER_NODE --nnodes=1 --node_rank=0 \
        -m cfd_prm.train \
        --data_dir data/hard_negatives \
        --output_dir outputs/cfd_prm \
        --lambda_calib 0.1 \
        --epochs 5 \
        --batch_size 32 \
        --learning_rate 2e-5
else
    # Start training
    echo "Starting single-GPU training..."
    python -m cfd_prm.train \
        --data_dir data/hard_negatives \
        --output_dir outputs/cfd_prm \
        --lambda_calib 0.1 \
        --epochs 5 \
        --batch_size 32 \
        --learning_rate 2e-5
fi

echo "Training complete!"
echo "Check outputs/cfd_prm/ for checkpoints and logs"
