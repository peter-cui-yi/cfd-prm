# Server Setup Guide for CFD-PRM Training

This guide walks you through setting up the training environment on a remote server.

---

## Prerequisites

- Remote server with GPU (recommended: 4xA800 or equivalent)
- SSH access configured
- CUDA 11.8+ installed
- Python 3.10+ installed

---

## Step 1: Clone Repository

```bash
# SSH into your server
ssh your_username@your_server

# Clone the repository
cd /path/to/your/workspace
git clone https://github.com/peter-cui-yi/cfd-prm.git
cd cfd-prm
```

---

## Step 2: Create Virtual Environment

```bash
# Create venv
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Verify installation
python -c "import torch; import transformers; print('OK')"
```

---

## Step 4: Download Agentic-MME Data

```bash
# Create data directory
mkdir -p data

# Download Agentic-MME dataset (if available)
# TODO: Add actual download link when available
wget -O data/agentic_mme.tar.gz [AGENTIC_MME_DOWNLOAD_URL]
tar -xzf data/agentic_mme.tar.gz -C data/
```

---

## Step 5: Prepare Hard Negative Pairs

```bash
# Run hard negative mining
python cfd_prm/data/hard_negative_miner.py \
    --input_dir data/agentic_mme \
    --output_dir data/hard_negatives \
    --audit_size 500
```

---

## Step 6: Start Training

```bash
# Single GPU training
python -m cfd_prm.train \
    --data_dir data/hard_negatives \
    --output_dir outputs/cfd_prm \
    --lambda_calib 0.1 \
    --epochs 5 \
    --batch_size 32 \
    --learning_rate 2e-5

# Multi-GPU training (4 GPUs)
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --data_dir data/hard_negatives \
    --output_dir outputs/cfd_prm \
    --lambda_calib 0.1 \
    --epochs 5
```

---

## Step 7: Monitor Training

```bash
# If using wandb
# Visit: https://wandb.ai/your_entity/cfd-prm

# Check logs
tail -f outputs/cfd_prm/training.log
```

---

## Step 8: Run Evaluation

```bash
# Discriminative evaluation
python cfd_prm/eval/discriminative_metrics.py \
    --checkpoint outputs/cfd_prm/best.pt \
    --test_dir data/agentic_mme/test

# Intervention evaluation
python cfd_prm/eval/intervention.py \
    --checkpoint outputs/cfd_prm/best.pt \
    --n_samples 10
```

---

## Syncing with GitHub

### Push changes from local to GitHub:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### Pull latest changes on server:
```bash
git pull origin main
```

---

## Troubleshooting

### CUDA out of memory:
```bash
# Reduce batch size
--batch_size 16  # or 8
```

### Import errors:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Slow data loading:
```bash
# Use local SSD for data
--data_dir /tmp/cfd_prm_data
```

---

## GPU Hours Tracking

Track your GPU usage against the budget (115 GPU-hours):

```bash
# Log GPU hours
echo "Date: $(date), GPU: 4, Hours: 2, Experiment: training_stage1" >> gpu_hours.log
```

See `EXPERIMENT_TRACKER_CFD-PRM.md` for the full budget breakdown.

---

## Contact

For issues or questions, open a GitHub issue or contact the maintainers.
