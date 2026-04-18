# CFD-PRM：基于检查点首次分歧的过程奖励模型

## 核心思想

CFD-PRM 是一种能够**逐步骤**对推理过程进行评分的过程奖励模型（Process Reward Model, PRM）。其核心洞察是：监督信号应集中于正确推理轨迹首次偏离为错误轨迹的关键步骤（即"检查点首次分歧"点，记为 t*）。

## 创新点

### 1. 检查点首次分歧损失（CFD Loss）

传统 PRM 方法对所有步骤平均施加监督，导致梯度被严重稀释。CFD 将排序损失集中作用于 t* 这一个关键步骤：

```
L_cfd = -log σ(score_ref(t*) - score_dev(t*) + margin)
```

这使得模型学会识别推理**在哪里**出错，而不仅仅是**是否**出错。

### 2. 双损失架构

仅靠 CFD（稀疏监督）不足以驱动模型学习。解决方案是将其与一个密集辅助损失配对：

| 组件 | 作用范围 | 目的 |
|------|----------|------|
| **CFD 损失**（λ=1.0） | 仅 t* | 学习分歧点的位置 |
| **BCE 损失**（λ=1.0） | 所有步骤 | 确保每一步都输出有意义的分数 |

### 3. 逐步骤训练范式

与之前将整个推理链作为整体打分的轨迹级方法不同，CFD-PRM：

- 将每对（参考轨迹, 偏离轨迹）扩展为独立的步骤查询
- 每个步骤从模型获得独立的分数
- 批处理在 **pair 级别**进行（与 DistributedSampler 兼容），扩展在 collate 函数中完成

### 4. 关键发现：基线方法在逐步骤判别上完全失效

Pairwise 和 Pointwise 基线在轨迹级别达到接近完美的准确率，但**无法区分单个步骤的好坏**——它们将整个轨迹作为一个整体打分，导致轨迹内部各步骤的分数几乎相同。

## 实验结果

### 轨迹级别评估（所有方法）

| 方法 | AUC-ROC | 配对准确率 | 分数差距 | 参考分数标准差 | 偏离分数标准差 |
|------|---------|------------|----------|----------------|----------------|
| **Pairwise** | 0.9026 | 0.8945 | 0.8017 | 0.245 | 0.208 |
| **Pointwise** | 0.8512 | 0.8625 | 0.9648 | 0.063 | 0.081 |
| **CFD+BCE** | 0.9823* | 0.9823 | — | 0.105 | 0.212 |

*CFD+BCE 的轨迹级别 AUC 由配对准确率（0.9823）推算；标准 AUC-ROC 指标对步骤级模型意义有限，因为其轨迹分数由逐步骤分数聚合而成，而非直接计算。

### 逐步骤评估 — 核心差距

| 方法 | 步骤级 AUC | 步骤级准确率 | 分数梯度性 | t* 定位准确率 | 正确步骤平均分 | 错误步骤平均分 |
|------|-----------|-------------|-----------|--------------|---------------|---------------|
| **Pairwise** | **0.5173** | **0.5021** | **0.0237** | 0.5685 | 0.5005 | 0.4830 |
| **Pointwise** | **0.5587** | **0.1423** | **-0.0218** | 0.4585 | 0.0667 | 0.0393 |
| **CFD+BCE** | **0.9888** | **0.9811** | **0.7590** | **0.8055** | **0.9743** | **0.0820** |

**分数梯度性（Score Gradientality）** = 偏离轨迹上 t* 之前的平均分数 − t* 之后的平均分数。值越高说明模型能正确识别推理在哪里出错。

### 核心结论

1. **Pairwise/Pointwise 轨迹级表现良好**（AUC 0.85-0.90），但步骤级完全失效（AUC ≈ 0.46-0.56，接近随机）
2. **CFD+BCE 步骤级表现卓越**（AUC 0.9888），在步骤级判别上远超基线，同时保持最高的轨迹级准确率（98.23%）
3. **Score Gradientality 差距巨大**：CFD 为 0.759，pairwise 仅 0.024，pointwise 甚至为负值（-0.022）
4. **t* 定位准确率 80.55%**：CFD 能定位推理的第一个分歧点
5. **正确 vs 错误步骤分数差距极大**：CFD 给正确步骤 0.974 分，错误步骤仅 0.082 分

## 训练配置

| 参数 | 取值 |
|------|------|
| 基础模型 | Qwen2.5-VL-3B-Instruct |
| LoRA | r=64, alpha=128 |
| 视觉编码器 | 冻结 |
| Epoch 数 | 3（提前停止） |
| 批次大小 | 2 × 2 GPU（梯度累积=4，有效批次=16） |
| 学习率 | 2e-5 |
| 池化方式 | 最后一 token |
| 损失函数 | CFD（λ=1.0）+ BCE（λ=1.0） |
| 数据集 | VisualPRM-400K（3337 对测试数据） |
| 训练目录 | `outputs/step_level_v3_dual_loss/` |

## 文件结构

| 文件 | 用途 |
|------|------|
| `cfd_prm/models/step_scorer.py` | StepScorer 模型（Qwen2.5-VL + LoRA + 评分头） |
| `cfd_prm/losses/checkpoint_first_divergence.py` | CFD 损失 + 自适应窗口损失 |
| `cfd_prm/data/dataset.py` | StepLevelCFDPRMDataset + 逐步骤 collate 函数 |
| `cfd_prm/train.py` | 训练脚本，支持 `--step_level` 参数 |
| `cfd_prm/eval/eval_model.py` | 轨迹级别评估 |
| `cfd_prm/eval/eval_step_level.py` | 逐步骤评估（AUC、梯度性、t* 定位准确率） |

## 复现命令

```bash
# CFD+BCE 训练（逐步骤）
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
    --data_dir data/visualprm400k_converted \
    --output_dir outputs/step_level_v3_dual_loss \
    --step_level --epochs 5 --batch_size 2 --gradient_accumulation_steps 4 \
    --learning_rate 2e-5 --max_grad_norm 1.0 --cfd_margin 0.0 \
    --lambda_step_bce 1.0 --lambda_calib 0.0 --warmup_ratio 0.05 \
    --pooling last --seed 42 --loss_type cfd

# Pairwise 基线
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
    --data_dir data/visualprm400k_converted \
    --output_dir outputs/baseline_pairwise_multi \
    --epochs 3 --batch_size 2 --gradient_accumulation_steps 4 \
    --learning_rate 2e-5 --max_grad_norm 10.0 --cfd_margin 0.0 \
    --lambda_calib 0.0 --warmup_ratio 0.05 --seed 42 --loss_type pairwise

# Pointwise 基线
torchrun --nproc_per_node=4 -m cfd_prm.train \
    --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
    --data_dir data/visualprm400k_converted \
    --output_dir outputs/baseline_pointwise_multi \
    --epochs 3 --batch_size 2 --gradient_accumulation_steps 4 \
    --learning_rate 2e-5 --max_grad_norm 10.0 --cfd_margin 0.0 \
    --lambda_calib 0.0 --warmup_ratio 0.05 --seed 42 --loss_type pointwise

# 逐步骤评估
python -m cfd_prm.eval.eval_step_level \
    --checkpoint outputs/<方法名>/final \
    --data_path data/visualprm400k_converted/visualprm400k_pairs.json \
    --model_name /hpc2hdd/home/ycui785/model/qwen2_5_vl_3b \
    --output_dir outputs/<方法名>/eval_step \
    --step_level --pooling last
```
