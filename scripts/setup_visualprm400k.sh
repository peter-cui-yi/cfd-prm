#!/bin/bash
# Setup VisualPRM400K dataset and convert to CFD-PRM format

set -e

echo "=== VisualPRM400K Dataset Setup ==="

# Create data directory
mkdir -p data/visualprm400k

# Check if HuggingFace datasets is installed
python -c "from datasets import load_dataset" || {
    echo "Installing datasets library..."
    pip install datasets
}

# Download and convert VisualPRM400K
echo ""
echo "Loading VisualPRM400K from HuggingFace..."
python -m cfd_prm.data.visualprm400k_adapter \
    --data_dir data/visualprm400k \
    --output_dir data/visualprm400k \
    --min_steps 3 \
    --max_steps 20 \
    --max_pairs 50000

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Converted data saved to: data/visualprm400k/"
echo "  - visualprm400k_pairs.json: Paired trajectories (reference vs deviated)"
echo "  - images/: Extracted screenshots"
echo "  - conversion_stats.json: Statistics"
echo ""
echo "Next steps:"
echo "  1. Verify pairs: cat data/visualprm400k/conversion_stats.json"
echo "  2. Run training: python -m cfd_prm.train --data_dir data/visualprm400k --output_dir outputs/cfd_prm"
