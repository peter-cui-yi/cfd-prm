#!/bin/bash
# Setup VisualWebArena dataset and convert to CFD-PRM format

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== VisualWebArena Dataset Setup ==="

# Clone VisualWebArena if not already done
if [ ! -d "data/visualwebarena_repo" ]; then
    echo "Cloning VisualWebArena repository..."
    git clone https://github.com/web-arena-x/visualwebarena.git data/visualwebarena_repo
else
    echo "VisualWebArena repository already exists"
    cd data/visualwebarena_repo && git pull && cd ../..
fi

# Install VWA dependencies (if needed)
echo "Installing VisualWebArena dependencies..."
cd data/visualwebarena_repo
pip install -e . 2>/dev/null || echo "Note: VWA setup may require manual steps"
cd ../..

# Run conversion
echo "Converting VisualWebArena to CFD-PRM format..."
python -m cfd_prm.data.visualwebarena_adapter \
    --vwa_dir data/visualwebarena_repo \
    --output_dir data/visualwebarena \
    --min_steps 3 \
    --max_steps 50

# Run hard negative mining on converted data
echo ""
echo "Running hard negative mining..."
python -m cfd_prm.data.hard_negative_miner \
    --input_dir data/visualwebarena \
    --output_dir data/hard_negatives \
    --audit_size 100

echo ""
echo "=== Setup Complete ==="
echo "Hard negative pairs saved to: data/hard_negatives/hard_negatives.json"
echo ""
echo "Next step: Run training"
echo "  ./cfd_prm/scripts/train.sh"
