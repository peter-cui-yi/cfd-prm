# CFD-PRM 完整实验计划

**Version**: 1.0 (Codex-Reviewed)  
**Last Updated**: 2026-04-10  
**Status**: Ready for Pre-Validation

---

## 项目概览

### 方法
- **CFD-PRM**: Checkpoint-First-Divergence Process Reward Model
- **核心创新**: 只在 t* (第一个分歧点) 进行 supervision
- **理论贡献**: O(1/ε²) sample complexity vs O(T/ε²)

### 数据
- **Primary**: VisualPRM400K (400K step-level labels, multimodal)
- **OOD**: PRM800K (text-only math)

### 评估协议
- **Track 1**: First-Error Detection (CFD-PRM 主场)
- **Track 2**: All-Error Detection (VisualPRM 主场)

---

## 当前进度

### ✅ 已完成

| 组件 | 状态 | 文件路径 |
|------|------|----------|
| Proposal v6.0 | ✅ | `refine-logs/FINAL_PROPOSAL_v6_VisualPRM.md` |
| Model (Qwen2.5-VL + LoRA) | ✅ | `cfd_prm/models/step_scorer.py` |
| Loss (CFD + Calibration) | ✅ | `cfd_prm/losses/checkpoint_first_divergence.py` |
| Data Adapter | ✅ | `cfd_prm/data/visualprm400k_adapter.py` |
| Training Script | ✅ | `cfd_prm/train.py` |
| Evaluation Protocol | ✅ | `cfd_prm/eval/EVALUATION_PROTOCOL.md` |
| README | ✅ | `cfd_prm/README.md` |
| Validity Assurance | ✅ | 包含在 README 中 |

### ⏳ 待完成

| 阶段 | 内容 | GPU-hours |
|------|------|-----------|
| **Pre-Validation** | Gate 1-5 | ~15 |
| **Full Training** | CFD-PRM + Baselines | ~40 |
| **Evaluation** | Dual-Track + OOD | ~10 |

---

## Pre-Validation Phase: 5 Gates

### Gate 1: Data Integrity (必须通过)

**目的**: 验证数据质量和分割正确性

**检查项**:
1. Prefix 完整性: `steps[0:t*]` 在 ref 和 dev 中完全相同
2. Divergence 正确性: `step[t*]` 在 ref 和 dev 中不同
3. t* 分布合理: 2 ≤ median(t*) ≤ T-2
4. 无 Leakage: Train/Test 按 `question_id` 分割，无重叠

**代码**:
```python
# 1. 下载数据
./scripts/setup_visualprm400k.sh

# 2. 完整性检查
python -c "
from cfd_prm.data.visualprm400k_adapter import VisualPRM400KAdapter

adapter = VisualPRM400KAdapter('data/visualprm400k', 'data/visualprm400k')
pairs = adapter.load_dataset()

# Prefix check
valid = 0
for p in pairs[:1000]:
    ref = p['reference']
    dev = p['deviated']
    t = p['t_star']
    if ref['solution'][:t] == dev['solution'][:t]:
        if ref['solution'][t] != dev['solution'][t]:
            valid += 1

print(f'Valid pairs: {valid}/1000 ({valid/10}%)')

# t* distribution
import numpy as np
t_stars = [p['t_star'] for p in pairs]
print(f't* distribution: min={min(t_stars)}, median={np.median(t_stars)}, max={max(t_stars)}')
"
```

**Pass 条件**:
- ≥90% pairs 满足 prefix 相同 + t* 不同
- 2 ≤ median(t*) ≤ 5
- Train/Test leakage = 0%

**用时**: 1 hour  
**失败处理**: 修复 adapter 或数据分割逻辑

---

### Gate 2: Optimization Sanity (必须通过)

**目的**: 验证代码能正常训练

**方法**: 过拟合极小数据集 (1-8 pairs)

**代码**:
```bash
# 过拟合 8 pairs
python -m cfd_prm.train \
    --data_dir data/visualprm400k \
    --output_dir outputs/pilot_overfit \
    --epochs 100 \
    --batch_size 8 \
    --max_pairs 8 \
    --learning_rate 1e-4
```

**Pass 条件**:
- Loss < 0.05 (成功过拟合)
- AUROC on these 8 pairs > 0.95

**用时**: 1 GPU-hour  
**失败处理**: 检查 loss 实现、梯度流、学习率

---

### Gate 3: Trivial-Feature Check (必须通过)

**目的**: 检测模型是否学习 shortcut

**检查项**:
1. Step-index baseline: 只用步骤位置预测
2. No-image baseline: 不用图像时的性能

**代码**:
```python
# 1. Step-index baseline
import numpy as np
from sklearn.linear_model import LogisticRegression

# Features: step index only
X_train = [[t] for sample in train_data for t in range(len(sample['solution']))]
y_train = [label for sample in train_data for label in sample['labels']]

model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate
X_test = [[t] for sample in test_data for t in range(len(sample['solution']))]
y_test = [label for sample in test_data for label in sample['labels']]
auroc_index = compute_auroc(model.predict_proba(X_test), y_test)
print(f'Step-index baseline AUROC: {auroc_index}')

# 2. No-image baseline
# (需要修改 model forward，设置 pixel_values=None)
```

**Pass 条件**:
- Step-index AUROC < 0.60 (模型不能只靠位置学习)
- No-image AUROC drop > 5% (必须依赖图像)

**用时**: 1 GPU-hour  
**失败处理**: 检查数据是否包含位置相关的噪音

---

### Gate 4: Core Signal Validation (关键决策点)

**目的**: 验证 t* 是否真的有信息量

**方法**: 小规模多 seed 实验，比较 CFD-PRM vs Random-t*

**实验配置**:
| Config | Description | Seeds |
|--------|-------------|-------|
| CFD-PRM | Supervise at true t* | 42, 123, 456 |
| Random-t* | Supervise at random step (length-matched) | 42, 123, 456 |
| Random-Step | Supervise at uniformly random step | 42, 123, 456 |
| Shifted-t* | Supervise at t*+1 | 42, 123, 456 |

**代码**:
```bash
# CFD-PRM (3 seeds)
for seed in 42 123 456; do
    python -m cfd_prm.train \
        --data_dir data/visualprm400k \
        --output_dir outputs/pilot_cfd_seed${seed} \
        --epochs 2 \
        --seed $seed \
        --max_pairs 50000
done

# Random-t* (需要修改 loss 中的 t* 选择逻辑)
for seed in 42 123 456; do
    python -m cfd_prm.train \
        --data_dir data/visualprm400k \
        --output_dir outputs/pilot_random_seed${seed} \
        --epochs 2 \
        --seed $seed \
        --max_pairs 50000 \
        --t_star_mode random
done
```

**评估**:
```python
# 评估 First-Error AUROC
for seed in [42, 123, 456]:
    model_cfd = load_model(f'outputs/pilot_cfd_seed{seed}')
    model_random = load_model(f'outputs/pilot_random_seed{seed}')
    
    auroc_cfd = evaluate_first_error(model_cfd, test_data)
    auroc_random = evaluate_first_error(model_random, test_data)
    
    print(f'Seed {seed}: CFD={auroc_cfd:.3f}, Random={auroc_random:.3f}, Δ={auroc_cfd-auroc_random:.3f}')
```

**Pass 条件**:
- CFD-PRM mean AUROC > Random-t* mean AUROC
- 统计显著性: p < 0.05 (paired t-test across seeds)
- CFD-PRM 在 All-Error 上不灾难性下降 (≤ 2 points)

**用时**: 8 GPU-hours  
**决策**: 
- ✅ Pass → 继续 Full Training
- ❌ Fail → **Pivot**: 考虑 Hybrid Loss 或修改方法

---

### Gate 5: Label-Budget-Matched Comparison

**目的**: 公平比较 label efficiency

**方法**: 保持相同 label budget，比较 CFD-PRM vs All-Steps

**代码**:
```python
# CFD-PRM: 每个 trajectory 监督 1 个 step
n_labels_cfd = len(train_pairs) * 1

# All-Steps-Matched: 每个 trajectory 随机选 1 个 step
# (需要实现 sub-sampled all-steps training)

model_matched = train_all_steps_matched(
    train_pairs,
    steps_per_trajectory=1,
    total_labels=n_labels_cfd
)

# 比较
auroc_cfd = evaluate_first_error(model_cfd, test_data)
auroc_matched = evaluate_first_error(model_matched, test_data)
print(f'CFD: {auroc_cfd:.3f}, Matched: {auroc_matched:.3f}')
```

**Pass 条件**:
- CFD-PRM > All-Steps-Matched (证明 first-divergence 的特殊价值)

**用时**: 4 GPU-hours

---

## Baseline Experiments

### 必须实现

| Baseline | 描述 | 用途 |
|----------|------|------|
| **All-Steps PRM** | 监督所有 T 个步骤 | VisualPRM 的做法 |
| **Label-Budget-Matched All-Steps** | 相同 label budget | 公平效率比较 |
| **Random-t*** | 随机选择 step 监督 | 证明 t* 有信息 |
| **Random-Step** | 均匀随机 step | 排除 "any single step works" |
| **Outcome RM** | 只看最终答案 | 下界 |

### 建议实现

| Baseline | 描述 | 用途 |
|----------|------|------|
| **Shifted-t* (t*±1)** | 监督 t*+1 或 t*-1 | 证明 "firstness" 重要 |
| **Early-Stop Prefix** | 监督前 t* 步 | Let's Verify 的做法 |
| **Two-Point Supervision** | t* 和 t*+k | Hybrid 方法 |

---

## Evaluation Protocol

### Track 1: First-Error Detection (CFD-PRM Primary)

| Metric | 定义 | Target |
|--------|------|--------|
| First-Error AUROC | 识别 t* 的能力 | > 0.75 |
| t* Accuracy@±1 | 定位精度 | > 70% |
| Label Efficiency | 达到 AUROC=0.7 的样本数 | 10x 优于 baseline |

### Track 2: All-Error Detection (Secondary)

| Metric | 定义 |
|--------|------|
| Per-Step AUROC | 所有步骤平均 AUROC |
| All-Error F1 | 检测所有错误的 F1 |

**Note**: VisualPRM 在 Track 2 上更好，CFD-PRM 在 Track 1 上更好。分开报告。

---

## Full Training Phase

### Experiment 1: CFD-PRM Full Training
- Data: 50K-100K pairs
- Epochs: 5
- Seeds: 3
- GPU-hours: ~32

### Experiment 2: Label Efficiency Curves
- Budgets: [1K, 5K, 10K, 25K, 50K, 100K]
- Match both total labels AND optimizer steps
- GPU-hours: ~12

### Experiment 3: Downstream Evaluation
- Best-of-N Reranking (N=10)
- GPU-hours: ~4

### Experiment 4: OOD Validation
- PRM800K (text-only math)
- GPU-hours: ~8

---

## Decision Points

| Gate | 决策 |
|------|------|
| Gate 1 Fail | 修复数据或 adapter |
| Gate 2 Fail | Debug 训练代码 |
| Gate 3 Fail | 检查数据 shortcut，考虑重新设计特征 |
| **Gate 4 Fail** | **核心假设错误，考虑 pivot** |
| Gate 5 Fail | 效率优势不成立，弱化 claim |

---

## Compute Budget Summary

| Phase | GPU-hours | 累计 |
|-------|-----------|------|
| Gate 1-3 (Sanity) | 3 | 3 |
| Gate 4-5 (Validation) | 12 | 15 |
| Full Training | 40 | 55 |
| Evaluation | 10 | 65 |

**总计**: ~65 GPU-hours (在 115 预算内)

---

## Timeline (40 Days)

| Days | 任务 | Gate |
|------|------|------|
| 1-2 | Data Setup + Integrity | Gate 1 |
| 3-4 | Overfit + Trivial-Feature | Gate 2-3 |
| 5-8 | Core Signal Validation | Gate 4 |
| 9-10 | Label-Budget Comparison | Gate 5 |
| 11-20 | Full Training | - |
| 21-28 | Baselines + Efficiency Curves | - |
| 29-34 | Downstream + OOD | - |
| 35-40 | Paper Writing | - |

---

## Quick Start Commands

```bash
# 1. Setup
./scripts/setup_visualprm400k.sh

# 2. Gate 1: Data Integrity
python -c "from cfd_prm.data.visualprm400k_adapter import *; check_integrity()"

# 3. Gate 2: Overfit Tiny Set
python -m cfd_prm.train --data_dir data/visualprm400k --output_dir outputs/gate2 --epochs 100 --max_pairs 8

# 4. Gate 4: Core Signal (3 seeds)
for seed in 42 123 456; do
    python -m cfd_prm.train --data_dir data/visualprm400k --output_dir outputs/gate4_seed${seed} --epochs 2 --seed $seed --max_pairs 50000
done

# 5. Evaluate
python -m cfd_prm.eval.discriminative_metrics --checkpoint outputs/gate4_seed42 --test_dir data/visualprm400k
```

---

## Files Reference

| 文件 | 用途 |
|------|------|
| `refine-logs/FINAL_PROPOSAL_v6_VisualPRM.md` | 完整 proposal |
| `cfd_prm/README.md` | 项目 README + Validity Assurance |
| `cfd_prm/eval/EVALUATION_PROTOCOL.md` | Dual-Track 评估协议 |
| `EXPERIMENT_PLAN_VALIDATION.md` | 本文件 |

---

**Status**: Ready to start Gate 1  
**Next Action**: Run `./scripts/setup_visualprm400k.sh` and validate data integrity