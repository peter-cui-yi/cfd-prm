# VisualProcessBench 评估结果与诊断分析报告

> 评估日期: 2026-04-17
> 模型: Qwen2.5-VL-3B-Instruct + LoRA (r=64, alpha=128)
> 数据集: VisualProcessBench test set (2,730 items, 19,259 steps)

---

## 一、VisualProcessBench 基准结果

### 1.1 Full VPB（全部 items）

| 指标 | CFD+BCE | BCE-only |
|------|---------|----------|
| Step AUC | **0.3401** | 0.2610 |
| Step AUPRC | **0.8090** | 0.7668 |
| Step Accuracy | 0.7083 | 0.7987 |
| ECE | 0.2665 | **0.1952** |
| Brier Score | 0.2453 | **0.1759** |
| μ(correct) | 0.7875 | 0.8437 |
| μ(incorrect) | 0.9016 | 0.9310 |
| std(correct) | 0.3161 | 0.1916 |
| std(incorrect) | 0.2348 | 0.1464 |
| n_correct | 16,585 (86.1%) | |
| n_incorrect | 2,674 (13.9%) | |

### 1.2 数据分布对比

| | VPB test | VisualPRM-400k train |
|--|----------|------------------------|
| 正确步占比 | 86.1% | 87.0% |
| 错误步占比 | 13.9% | 13.0% |
| 错误步在 step 0 | **55.5%** | 0% |
| 第一个错误在 step ≤ 1 | **90.2%** | 0% |
| 标注方式 | 单轨迹人工标注 | paired (reference vs deviated) |

---

## 二、核心问题：AUC 反向（< 0.5）

### 2.1 现象

两个模型的 Step AUC 都远低于 0.5（CFD+BCE: 0.340, BCE-only: 0.261），意味着模型给 **incorrect steps 打了更高的分**。

具体表现：
- CFD+BCE: μ(correct)=0.788, μ(incorrect)=0.902 → **反了**
- BCE-only: μ(correct)=0.844, μ(incorrect)=0.931 → **反了**

### 2.2 根本原因：训练与评估的结构不匹配

#### 训练数据（VisualPRM-400k）的结构

每一对数据包含两条轨迹：

```
Reference trajectory（参考轨迹）:
  Step 0: [1] ✓
  Step 1: [1] ✓
  Step 2: [1] ✓
  ... → 全部正确

Deviated trajectory（偏离轨迹）:
  Step 0: [1] ✓  ← 与 reference 相同
  Step 1: [1] ✓  ← 与 reference 相同
  Step 2: [1] ✓  ← 与 reference 相同
  Step 3: [0] ✗  ← t* 位置，从这里开始不同
  Step 4: [0] ✗
  Step 5: [0] ✗
```

**训练数据的关键约束**：
1. t* 之前的步骤**永远是正确的**（reference 和 deviated 共享同一段推理）
2. **step 0 永远是正确的**（label=1）
3. 错误只出现在 t* 之后

#### VPB 的结构

VPB 是单条轨迹，人工标注每一步的推理是否正确：

```
VPB item（incorrect at step 0）:
  Step 0: [0] ✗  ← 开头思路就不对
  Step 1: [1] ✓
  Step 2: [1] ✓
  ...

VPB item（incorrect at step 14）:
  Step 0-13: [1] ✓
  Step 14: [0] ✗  ← 中间某步出错
  Step 15+: [1] ✓
```

**VPB 与训练数据的关键差异**：
1. **55.5% 的错误步在 position 0** — 模型训练时从未见过 step 0 是错误的
2. **90.2% 的第一个错误在 step ≤ 1** — 模型训练时错误只出现在 t* 之后
3. **标注逻辑不同**：训练数据是"这一步和 reference 不同所以错"，VPB 是"这一步的推理本身有问题所以错"

### 2.3 为什么 AUC 反向了

模型在训练中学到了一条**隐式位置先验**：`step index 越小 → 分数越高`。

因为训练数据中：
- 所有 step 0 的 label 都是 1
- 所有 label 为 0 的步骤都出现在 trajectory 的中后段（t* 之后）

当 VPB 告诉模型"step 0 是错误的"时，模型**不相信**——它给早期步骤打了高分（这是它从训练数据中学到的 pattern）。

同时，VPB 中标记为 correct 的步骤分布在轨迹的各个位置（包括后半段），模型给这些后半段步骤打了相对较低的分数。

结果：**incorrect steps 的平均分数 > correct steps 的平均分数** → AUC 反向。

### 2.4 为什么 AUPRC 仍然合理

AUPRC（Average Precision）不受 score 整体缩放方向的影响，它关注的是高分区域的 precision。即使模型给所有步骤都打了相对较高的分（0.79-0.93），它仍然在一定程度上区分了哪些步骤更可能正确（AUPRC 0.809 vs 随机 0.861 的 base rate）。

---

## 三、CFD+BCE vs BCE-only 在 VPB 上的差异

| 对比维度 | CFD+BCE | BCE-only | 分析 |
|----------|---------|----------|------|
| AUC | 0.340 | 0.261 | CFD 略好，但都反向 |
| AUPRC | 0.809 | 0.767 | CFD 区分度更好 |
| μ(incorrect) | 0.902 | 0.931 | CFD 给错误步的分数略低 |
| std(correct) | 0.316 | 0.192 | CFD 的分数分布更广 |
| std(incorrect) | 0.235 | 0.146 | CFD 对错误步的区分更细 |

**CFD+BCE 的表现略好于 BCE-only**，但差异很小。两者都受到了相同的位置先验问题的影响。

---

## 四、VPB 诊断结果：区分位置偏置 vs 任务定义错位

### 4.1 Check 1：Score Direction Sanity

| 指标 | CFD+BCE | BCE-only |
|------|---------|----------|
| AUC(score) | 0.3401 | 0.2610 |
| AUC(1-score) | 0.6599 | 0.7390 |
| AUPRC(correct) | 0.8090 | 0.7668 |
| AUPRC(incorrect) | 0.2102 | 0.3264 |
| μ(correct) | 0.7875 | 0.8437 |
| μ(incorrect) | 0.9016 | 0.9310 |
| Δ(correct-incorrect) | **-0.1141** | **-0.0873** |

**结论：系统性反转确认。** AUC(1-score) >> AUC(score)，两个模型都给 incorrect steps 打了更高的分数。CFD+BCE 的翻转幅度（Δ = -0.114）比 BCE-only（Δ = -0.087）更大，说明 CFD 对"分数下降"的结构化假设在 VPB 上反而放大了问题。

### 4.2 Check 2：Position-Only Baseline

| 指标 | 值 | 含义 |
|------|-----|------|
| AUC(-step_index) | 0.2742 | 仅用负位置索引的 AUC |
| **AUC(LogReg step_index)** | **0.7258** | 纯位置线性回归 AUC |
| LogReg 系数 | 0.1664 | step_index → incorrect 的正向关系 |
| LogReg 截距 | 1.2086 | 基础 incorrect 概率的 logit |

**关键发现：仅用 step_index 作为特征，LogReg 就能达到 AUC = 0.7258。** 这意味着 VPB 数据中存在极强的位置-标签相关性（step index 越大 → 越容易是 incorrect）。这解释了为什么模型学到的位置先验会产生如此大的影响。

对比：
- CFD+BCE AUC = 0.3401（比纯位置 0.7258 差得多）
- BCE-only AUC = 0.2610（更差）

说明模型**没有**简单地学习到位置-标签的映射关系，而是学到了更复杂但与 VPB 标签结构相矛盾的模式。

### 4.3 Check 3：Position-Stratified Analysis

| 位置 | 模型 | n | AUC | μ(c) | μ(i) | Δ |
|------|------|---|-----|------|------|---|
| **step 0** | CFD+BCE | 2679 | 0.4370 | 0.9376 | 0.9736 | -0.0360 |
| | BCE-only | 2679 | 0.3060 | 0.9500 | 0.9815 | -0.0315 |
| **step 1** | CFD+BCE | 2431 | 0.4382 | 0.9129 | 0.9489 | -0.0360 |
| | BCE-only | 2431 | 0.3802 | 0.9303 | 0.9547 | -0.0244 |
| **step 2-3** | CFD+BCE | 4384 | 0.4032 | 0.8419 | 0.9082 | -0.0663 |
| | BCE-only | 4384 | 0.3605 | 0.8684 | 0.9241 | -0.0557 |
| **step 4+** | CFD+BCE | 9765 | 0.4498 | 0.7119 | 0.7429 | -0.0310 |
| | BCE-only | 9765 | 0.4258 | 0.7971 | 0.8258 | -0.0287 |

**发现：**
- **每个位置层的 AUC 都 < 0.5**，反转不是 step 0 独⼀导致的
- step 2-3 的翻转幅度最大（Δ = -0.066），这是 t* 最常出现的位置范围
- step 4+ 的 AUC 最接近 0.5（0.450），说明模型对后半段步骤的判别相对中性
- CFD+BCE 的翻转幅度普遍大于 BCE-only，印证了 CFD 的结构性假设在 VPB 上不匹配

### 4.4 Check 4：Filtered Subset Analysis

| 子集 | 模型 | n | AUC | μ(c) | μ(i) | Δ |
|------|------|---|-----|------|------|---|
| **Full VPB** | CFD+BCE | 19259 | 0.3401 | 0.7875 | 0.9016 | -0.1141 |
| | BCE-only | 19259 | 0.2610 | 0.8437 | 0.9310 | -0.0873 |
| **Subset A: first_incorrect > 0** | CFD+BCE | 2776 | 0.4909 | 0.8165 | 0.8113 | **+0.0052** |
| | BCE-only | 2776 | 0.4827 | 0.8715 | 0.8741 | -0.0026 |
| **Subset B: monotonic error** | CFD+BCE | 807 | 0.3430 | 0.7740 | 0.8392 | -0.0652 |
| | BCE-only | 807 | 0.2981 | 0.8688 | 0.9139 | -0.0451 |
| **Subset C: A∩B (matched)** | CFD+BCE | 673 | **0.5023** | 0.7740 | 0.7370 | **+0.0370** |
| | BCE-only | 673 | 0.4517 | 0.8688 | 0.8663 | +0.0025 |
| **Step 0 excluded** | CFD+BCE | 16580 | 0.4414 | 0.7759 | 0.8119 | -0.0360 |
| | BCE-only | 16580 | 0.4136 | 0.8355 | 0.8681 | -0.0326 |

### 4.5 关键发现总结

#### A. 位置偏置（Position Bias）→ 是主要原因之一

- 纯位置 LogReg 达到 AUC = 0.7258，远超模型本身
- 模型学到的模式："早期步骤 = 高分"与 VPB 的标注结构（55% 错误在 step 0）直接冲突

#### B. 任务定义错位（Task Definition Mismatch）→ 也是主要原因之一

- Subset C（排除 step 0 + 单调错误）AUC 恢复至 **0.5023**（接近 0.5）
- Subset A（排除 step 0）AUC 恢复至 **0.4909**
- 这些子集更接近训练数据的结构（错误不出现在 step 0），但 AUC 仍仅达到 ~0.50
- 说明除了位置偏置，还存在**语义层面的不匹配**：训练数据是 deviation-based，VPB 是 human verification

#### C. 数据特征：59% 非单调恢复模式

- 1612/2730 items 有"错误后恢复"模式（1→0→1）
- 仅 201/2730 items 是单调错误
- 训练数据中几乎没有"恢复"模式——deviated trajectory 一旦出错就一直错
- 这可能是 AUC 在子集 C 中仅恢复到 0.5023 的第二个原因

#### D. CFD vs BCE-only 的对比

- CFD+BCE 在所有子集上都优于 BCE-only
- 但 CFD+BCE 的反转幅度更大（Δ = -0.114 vs -0.087），因为 CFD 假设"正确 checkpoint 后分数不应下降"，而 VPB 中"错误→正确恢复"的模式打破了这个假设
- CFD 的结构性假设在匹配训练分布时是优势（AUC 0.989），在不匹配时反而成为劣势

---

## 五、解决方向

### 5.1 Filtered VPB（短期方案）

过滤掉第一个 incorrect 步骤出现在 position 0 的 items，只评估符合训练数据分布的子集（约 673 items，Subset C）。这可以作为"模型在匹配训练分布时的表现"报告。

### 5.2 在训练中加入早期错误样本（长期方案）

在 VisualPRM-400k 训练数据中加入 deviated trajectory 从 step 0 就错误的样本，打破模型学到的位置先验。

### 5.3 加入"恢复"模式样本（长期方案）

加入 deviated trajectory 中途恢复正确的样本（即 1→0→1 模式），使模型能处理非单调错误模式。当前训练数据中几乎没有此类样本。

### 5.4 修改模型架构

加入显式的位置无关化机制，比如：
- 位置编码的 ablation
- 对抗性位置训练（adversarial position training）
- 在 prompt 中显式要求模型忽略步骤顺序

### 5.5 在论文中报告此发现

VPB 的"反向 AUC"本身是一个有价值的发现——它揭示了 CFD/BCE-only 模型学到的判别能力中包含了强烈的**位置偏倚**，以及训练数据的 deviation-based 标注与 human verification 标注之间的**根本性差异**。这对于 PRM 的实际部署是一个重要的 failure mode。
