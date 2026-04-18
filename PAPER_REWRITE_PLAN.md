# CFD-PRM 论文重写计划

## 新定位

**这不是一篇"更大的 multimodal PRM"论文，而是一篇"为 step-level multimodal PRM 设计更好的 credit assignment objective"的论文。**

核心一句话贡献：**显式监督最早的分歧点（first divergence point）是改善多模态 PRM 中 credit assignment 的一个简单而有效的方法。**

---

## 论文标题

**CFD-PRM: Localizing the First Divergence for Multimodal Process Reward Modeling**

## 摘要

Process reward models (PRMs) for multimodal reasoning require accurate step-level supervision, yet existing objectives either score whole trajectories or apply dense per-step classification uniformly across all reasoning steps. Such supervision can dilute learning around the earliest causal error boundary---the first step where an otherwise correct reasoning trajectory diverges into an incorrect one. We propose **Checkpoint-First-Divergence Process Reward Modeling (CFD-PRM)**, a hybrid training objective that combines a dense step-wise BCE loss with a sparse ranking loss applied only at the first divergence step ($t^*$). The BCE term ensures globally meaningful step scores, while the CFD term sharpens discrimination at the critical transition from correct to incorrect reasoning. On VisualPRM-400K paired trajectories, CFD-PRM substantially improves step-level evaluation over strong baselines, raising Step AUC from 0.9541 to 0.9888 relative to a BCE-only step-level model and markedly improving first-divergence localization and score gradientality. We further show that trajectory-level pairwise and pointwise reward models can achieve competitive trajectory ranking while failing to discriminate erroneous steps, highlighting a mismatch between trajectory-level preference modeling and step-level process verification. Ablations show that dense BCE supervision is necessary for stable learning, while accurate ($t^*$) supervision is crucial for the full gain of CFD. These results suggest that explicitly supervising the earliest divergence point is a simple and effective way to improve credit assignment in multimodal PRMs.

---

## Contribution 列表（4 条，不多写）

1. **提出 CFD Loss**：将 ranking supervision 集中在 first-divergence step ($t^*$)，把 PRM 的学习重点从"平均所有步骤"转向"最关键的错误边界"。

2. **Sparse + Dense 的 Dual-Loss Recipe**：证明 CFD-only 不足以学习稳定的 step scores，而 CFD+BCE 能同时获得全局可读分数和局部边界判别力。这不是直觉上的 trick，而是更完整的训练原理。

3. **揭示 Trajectory Ranking 与 Step Diagnosis 的能力鸿沟**：trajectory-level pairwise/pointwise 模型可以达到 ~90% 的 trajectory AUC，但 step-level discrimination 接近随机（AUC ~0.50）。"会选整条轨迹"不等于"会定位哪一步错了"。

4. **通过 Ablation 说明 True ($t^*$) 不是任意 hard-negative weighting 的替代品**：random/shifted ($t^*$) 明显不如 true ($t^*$)，说明 gain 的来源确实和 first-divergence structure 有关。

**不写进主列表的**：
- "O(1) annotation cost / label efficiency"（需要更多实验验证，PAV/ThinkPRM 已有类似 claim）
- "better general verifier"（VPB 结果显示不是）

---

## 论文结构

### 1. Introduction
- **问题**：PRM 需要准确的 step-level supervision，但现有方法（dense per-step BCE）均匀地对待所有步骤
- **洞察**：最有信息量的监督不在所有错误步骤的平均上，而在第一次偏离正确轨迹的位置
- **方法**：CFD = dense BCE + sparse ranking at $t^*$
- **关键结果预览**：
  - Step AUC: 0.954 → 0.989（vs 强基线 BCE-only）
  - Reranking Top-1: 89.7%（step-level + image）
  - Trajectory-level models fail at step diagnosis (AUC ~0.50)
- **4 条 contribution**

### 2. Background & Related Work
- 2.1 Process Reward Models (VisualPRM, ProcessBench)
- 2.2 Step-Level Evaluation & Earliest-Error Detection
- 2.3 Test-Time Scaling & PRM-Guided Search (BoN)
- 2.4 Data-Efficient PRM Training (PAV, ThinkPRM)

### 3. Method
- 3.1 Paired Trajectory Setup & $t^*$ Definition
- 3.2 Checkpoint-First-Divergence Loss
- 3.3 Dual-Loss Architecture (CFD + BCE)
- 3.4 Why CFD-Only Fails (need dense supervision)

### 4. Experiments: In-Distribution Step Credit Assignment
- 4.1 Main Results (CFD+BCE vs all baselines)
- 4.2 Ablation Study (CFD-only, random $t^*$, shifted $t^*$)
- 4.3 Reranking / BoN Utility (search-time PRM)
- 4.4 Label Efficiency (10%, 20%, 50%)
- 4.5 Monotonicity Analysis

### 5. Experiments: Generalization Boundary (VPB)
- 5.1 Full VPB Results (honest reporting of failure)
- 5.2 Diagnostic: Position Bias & Task Mismatch
- 5.3 Matched Subset Analysis (recovers to ~0.50)
- 5.4 Take-away: CFD is effective within its designed regime

### 6. Discussion
- What CFD is good at
- What CFD is NOT good at
- Future directions

### 7. Conclusion

---

## 核心实验结果表

### 表 1: Main In-Distribution Results (VisualPRM-400K test)

| Method | Step AUC | Step Acc | t* Loc | Gradient | ECE | Brier | Traj Pair Acc |
|--------|----------|----------|--------|----------|-----|-------|---------------|
| **CFD+BCE (full)** | **0.9888** | **0.9811** | **0.8055** | **0.7590** | 0.0162 | 0.0152 | **0.9823** |
| BCE-only (full) | 0.9541 | 0.9545 | 0.7282 | 0.4157 | -- | -- | 0.8654 |
| Boundary BCE | 0.9538 | -- | 0.7743 | 0.6226 | 0.0225 | 0.0202 | 0.9661 |
| CFD-only | 0.7320 | -- | -- | -- | -- | -- | -- |
| Random $t^*$ + BCE | 0.9416 | 0.9444 | 0.7129 | 0.5015 | -- | -- | -- |
| Shifted $t^*$ (+2) + BCE | 0.9414 | 0.9444 | 0.7228 | 0.5022 | -- | -- | -- |
| Pairwise | 0.5173 | 0.5021 | 0.5685 | 0.0237 | -- | -- | -- |
| Pointwise | 0.5587 | 0.1423 | 0.4585 | -0.0218 | -- | -- | -- |

### 表 2: Reranking / Best-of-N (10,910 questions, 33,375 pairs)

#### (a) Text-Only Whole-Trajectory Scoring

| Model | Pair Acc | Top-1 | Margin | BoN@2 | BoN@3 | BoN@5 |
|-------|----------|-------|--------|-------|-------|-------|
| **CFD+BCE** | **0.8222** | **0.7140** | 0.4651 | **0.8308** | **0.7753** | **0.6583** |
| BCE-only | 0.7648 | 0.6187 | 0.1146 | 0.7613 | 0.6891 | 0.5706 |
| All Wrong Ranking | 0.8401 | 0.7352 | 0.3310 | 0.8407 | 0.7905 | 0.6985 |
| Boundary BCE | 0.7933 | 0.6605 | 0.2530 | 0.7936 | 0.7251 | 0.6089 |

#### (b) Step-Level + Image Scoring

| Model | Pair Acc | Top-1 | Margin | BoN@2 | BoN@3 | BoN@5 |
|-------|----------|-------|--------|-------|-------|-------|
| **CFD+BCE** | **0.9302** | **0.8967** | **0.2406** | **0.9476** | **0.9226** | **0.8497** |
| BCE-only | 0.7599 | 0.6329 | 0.0994 | 0.7596 | 0.6934 | 0.5626 |
| All Wrong Ranking | 0.8771 | 0.7942 | 0.1713 | 0.8844 | 0.8380 | 0.7218 |

**关键观察**：
- CFD+BCE 在 step-level + image 下达到 89.7% Top-1，BoN@5 = 85.0%
- BCE-only 在两种模式下几乎没有变化（BoN@5: 0.57 vs 0.56），没有学会利用视觉信息
- CFD 从 text-only 到 step-level 的提升最大（BoN@5: 0.66 → 0.85, +19%）

### 表 3: Label Efficiency

| Data | Method | Step AUC | t* Loc | Gradient |
|------|--------|----------|--------|----------|
| 10% | **CFD+BCE** | **0.8066** | **0.6818** | **0.3272** |
| | BCE-only | 0.7870 | 0.6224 | 0.2902 |
| 20% | **CFD+BCE** | **0.8226** | **0.6988** | **0.3143** |
| | BCE-only | 0.8186 | 0.6862 | 0.2693 |
| 50% | CFD+BCE | 0.9247 | **0.7300** | **0.4810** |
| | BCE-only | **0.9359** | 0.7207 | 0.4504 |
| Full | CFD+BCE | **0.9888** | **0.8055** | **0.7590** |
| | BCE-only | 0.9541 | 0.7282 | 0.4157 |

### 表 4: VPB Results (Failure Analysis)

| Metric | CFD+BCE | BCE-only |
|--------|---------|----------|
| Full VPB AUC | **0.3401** | 0.2610 |
| Full VPB AUPRC | **0.8090** | 0.7668 |
| Subset C (matched) AUC | **0.5023** | 0.4517 |
| Position-debiased AUC | **0.5686** | -- |
| Position-only LogReg AUC | 0.7256 | -- |

---

## 需要重写的部分

1. **Title**: 已确定
2. **Abstract**: 已确定（GPT-pro 提供）
3. **Introduction**: 全新叙事弧（contradiction → BCE-only → CFD → contributions）
4. **Related Work**: 对齐 4 条线（VisualPRM, ProcessBench, BoN/TTS, Data-efficient PRM）
5. **VPB Section**: 作为 failure analysis，不是 main benchmark

## 可以保留的部分

1. **Method Section**: CFD loss definition, dual-loss architecture
2. **Main in-distribution results**: 所有数字都强
3. **Ablation Study**: CFD-only, random $t^*$, shifted $t^*$
4. **Reranking Results**: 特别 step-level + image
5. **Monotonicity Analysis**: 支持 claim scope
6. **Label-efficiency Data**: 保留但作为 secondary

---

## 当前状态

- 所有核心实验已完成
- boundary_bce eval 完成（Step AUC = 0.9538, Traj Pair Acc = 0.9661）
- step-level reranking for boundary_bce 还在跑（~32%）
- 可以开始写论文
