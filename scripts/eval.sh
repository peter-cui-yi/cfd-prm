#!/bin/bash
# Quick start script for CFD-PRM evaluation

set -e

echo "=== CFD-PRM Evaluation ==="

if [ -z "$1" ]; then
    echo "Usage: ./scripts/eval.sh <checkpoint_path>"
    exit 1
fi

CHECKPOINT=$1

# Check checkpoint
if [ ! -d "$CHECKPOINT" ]; then
    echo "Error: Checkpoint not found at $CHECKPOINT"
    exit 1
fi

# Run discriminative evaluation
echo "Running discriminative evaluation..."
python -m cfd_prm.eval.discriminative_metrics \
    --checkpoint "$CHECKPOINT" \
    --test_dir data/hard_negatives \
    --output_dir results

# Run intervention analysis
echo "Running intervention analysis..."
python -m cfd_prm.eval.intervention \
    --checkpoint "$CHECKPOINT" \
    --data_dir data/hard_negatives \
    --output_dir results

echo "Evaluation complete!"
echo "Check results/ for metrics"
