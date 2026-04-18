我先给审稿结论：这篇工作**有主会潜力，但现在还不是“大概率接收”**。按我自己的主观口径，我会给它一个 **Borderline Reject / Weak Reject**：novelty 大概 7/10，technical quality 6/10，empirical validation 4.5/10，paper story 6/10。问题不在于 idea 不好，而在于**证据链还没有对齐这条方向近两年的主战场**：近期多模态 PRM 工作通常既要证明 step-level error localization，也要证明它对 BoN / test-time scaling 的真实推理效果有帮助；同时，近期文本 PRM 工作也明确强调，BoN 之外必须看 earliest-error localization，而 newer VL-PRM work 还显示 offline step metrics 与 test-time scaling 的最优用法并不总是一致。([arXiv][1])

但你这份计划里已经有一个**真正能打的核心结果**：CFD+BCE 相比强基线 BCE-only，不只是“略好一点”，而是把 step AUC 从 0.9541 提到 0.9888，把 t* localization 从 72.8% 提到 80.6%，把 gradientality 从 0.4157 拉到 0.7590。这个增益说明你的方法并不是只靠打 pairwise/pointwise 这种不完全对口的 baseline 才成立；它在**真正相关的强基线**上也有效。这个点是能写成主会论文的。

我会建议你把整篇论文的定位收缩成一句话：

**这不是一篇“更大的 multimodal PRM”论文，而是一篇“为 step-level multimodal PRM 设计更好的 credit assignment objective”的论文。**

这个 framing 会稳很多。

---

## 可直接用的英文摘要（保守版）

**CFD-PRM: Localizing the First Divergence for Multimodal Process Reward Modeling**

Process reward models (PRMs) for multimodal reasoning require accurate step-level supervision, yet existing objectives either score whole trajectories or apply dense per-step classification uniformly across all reasoning steps. Such supervision can dilute learning around the earliest causal error boundary—the first step where an otherwise correct reasoning trajectory diverges into an incorrect one. We propose **Checkpoint-First-Divergence Process Reward Modeling (CFD-PRM)**, a hybrid training objective that combines a dense step-wise BCE loss with a sparse ranking loss applied only at the first divergence step (t^*). The BCE term ensures globally meaningful step scores, while the CFD term sharpens discrimination at the critical transition from correct to incorrect reasoning. On VisualPRM-400K paired trajectories, CFD-PRM substantially improves step-level evaluation over strong baselines, raising Step AUC from 0.9541 to 0.9888 relative to a BCE-only step-level model and markedly improving first-divergence localization and score gradientality. We further show that trajectory-level pairwise and pointwise reward models can achieve competitive trajectory ranking while failing to discriminate erroneous steps, highlighting a mismatch between trajectory-level preference modeling and step-level process verification. Ablations show that dense BCE supervision is necessary for stable learning, while accurate (t^*) supervision is crucial for the full gain of CFD. These results suggest that explicitly supervising the earliest divergence point is a simple and effective way to improve credit assignment in multimodal PRMs. 

这版摘要是**能发但不乱吹**的版本。它没有提前承诺你还没跑出来的 BoN/TTS 提升，也没有把 label-efficiency 当成既成事实。

---

## 建议你在论文里保留的 contribution

1. **提出 CFD loss**：把 ranking supervision 集中在 first-divergence step (t^*)，从而把 PRM 的学习重点从“平均所有步骤”转向“最关键的错误边界”。

2. **提出 sparse+dense 的 dual-loss recipe**：CFD-only 不足以学习稳定 step scores，而 CFD+BCE 能同时得到全局可读分数和局部边界判别力。这个点很重要，因为它把你的方法从一个“直觉上的 trick”变成了一个更完整的训练原理。

3. **揭示 trajectory ranking 与 step diagnosis 的能力鸿沟**：trajectory-level pairwise/pointwise 可以有不错的 trajectory AUC，但 step-level discrimination 接近随机；这说明“会选整条轨迹”不等于“会定位哪一步错了”。这其实是很好的 scientific insight。

4. **通过 ablation 说明 true (t^*) 不是任意 hard-negative weighting 的替代品**：random/shifted (t^*) 明显不如 true (t^*)，说明 gain 的来源确实和 first-divergence structure 有关。

有一个 contribution **现在不要写进主列表**：
**“O(1) annotation cost / t*-only label efficiency”**。这个方向非常有潜力，但你自己也写了 *not started*；而且近年的 PAV / ThinkPRM 一类工作已经把“少量 process labels 也能训练强 PRM”做成公开 claim 了，所以你必须拿真实实验说话，否则这一点反而会被 reviewer 质疑成 overclaim。([OpenReview][2])

---

## 这篇 paper 现在最强的地方

**第一，idea 清楚，而且 reviewer 一眼能懂。**
“最有信息量的监督，不在所有错误步骤的平均上，而在第一次偏离正确轨迹的位置。” 这是一个很强的直觉，而且容易画图、容易讲故事、容易形成记忆点。

**第二，你已经有了真正 relevant 的强 baseline。**
很多稿子会死在“只赢了弱 baseline”。你这边幸运的是，BCE-only 很强，0.9541 并不低，所以 CFD+BCE 还能继续拉开 gap，这个结果是有含金量的。

**第三，ablation 设计是对的。**
CFD-only、BCE-only、random (t^*)、shifted (t^*) 这几组 ablation 非常有价值，说明你不是只做了一个 loss 然后报个数字，而是在拆机制。这个审稿人会喜欢。

**第四，这个方向和领域脉络是对齐的。**
VisualPRM 已经把多模态 PRM 的问题空间打开了，并提出了 VisualPRM400K 和带人工 step 标签的 VisualProcessBench；ProcessBench 和后续 lessons paper 也都在强调 earliest-error detection 与 step-level evaluation 的重要性。你的工作不是偏题，而是正好踩在这条线上。([arXiv][1])

---

## 现在最危险的风险点，以及怎么补

### 1) 你真正的对手是 BCE-only，不是 pairwise/pointwise

这是你现在最需要认清的一点。

pairwise/pointwise 在 step-level 上接近随机，这个现象很醒目，但 reviewer 很容易说：
“那是因为你拿 trajectory-level 模型去做 step-level 诊断，当然不行。”

所以你主文的叙事顺序应该是：

* 先打 **BCE-only**；
* 再把 pairwise/pointwise 当作“为什么 trajectory-level RM 不足以替代 PRM”的 supporting observation。

另外，建议再补一个更像“hard example reweighting”的 baseline，例如：

* BCE + focal weighting around error steps
* BCE + boundary-step upweighting
* BCE + all-wrong-step ranking
* 或者一个 PQM 风格的 comparative loss baseline

因为 PQM 这类工作已经明确在批评“独立的 per-step classification 忽略 step interdependencies”。如果你不补这类 baseline，reviewer 会问：
“你这个 gain 到底来自 first divergence，还是来自任何一种 comparative signal 都行？” ([arXiv][3])

### 2) 缺少独立 benchmark 和下游 utility，是当前最大硬伤

如果你今天就投，我最可能据此给低分。

原因很简单：VisualPRM 这条线已经把标准立起来了——它不只看训练数据上的 step score，还看 **BoN 下的真实推理提升**，并引入 **VisualProcessBench** 这种人工标注的 step benchmark；后来的 VL-PRM 论文也把 **test-time scaling strategy** 当成主战场来分析。只在 VisualPRM-400K 配对数据上做 offline eval，证据还不够闭环。([arXiv][1])

我会把你当前实验优先级**强行改掉**：

* **先跑 VisualProcessBench**
* **再跑 BoN / TTS downstream**
* 20% / 50% learning curve 先往后放

因为从“提高录用率”的角度看，
**P2 test-time scaling analysis 的收益远高于继续补 20%/50% label curve。**

### 3) first-divergence 假设会被 reviewer 用 “self-correction” 攻击

这几乎是必来的问题。

因为已经有工作明确指出：在 long CoT / reflective reasoning 里，“first error 之后全错”并不总成立，后续可能出现 self-correction，正确和错误步骤会交替。([arXiv][4])

你必须主动做两件事：

第一，**量化你的数据分布到底是不是 monotonic deviation regime**。
比如统计：

* dev trajectory 在第一次错误后，后续又变回正确的比例；
* correctness label 在一条轨迹里发生多次 1↔0 翻转的比例；
* 多模态 reasoning 中 visual grounding error 后是否常出现 textual self-repair。

如果这个比例很低，你就能反打 reviewer：
“在 VisualPRM-400K 这类 paired deviation 数据里，CFD 的单一 (t^*) 假设是经验上成立的。”

如果这个比例不低，那你就要：

* 缩小 claim scope，明确说 CFD 适用于 monotonic deviation pairs；
* 或者扩展成 **multi-checkpoint CFD**。

### 4) 你的 metric 定义现在有明显红旗

这是一个非常现实的问题：**reviewer 会抓你表里的不一致**。

最明显的就是：

* 你前面说 CFD+BCE trajectory-level AUC 约 0.9823（还是从 pair accuracy 代换来的）；
* 后面 ablation / label-efficiency 表里又出现 **Traj AUC = 0.0017** 这种明显不合理的数字。

这会直接破坏可信度。

我的建议非常明确：

* **不要再写 “AUC computed from pairwise accuracy”**。AUC 不是 accuracy，别这样代。
* 对 step-level 模型，trajectory-level 统一报：

  * pair accuracy
  * BoN accuracy / prm@N
  * pass@N / search success
  * aggregation rule（mean/min/max/last/product）
* 自定义的 Score Gradientality、Within-Traj Var 可以留，但只能做辅助诊断，不要做 headline metric。主指标必须是更标准的：

  * Step AUC / F1
  * earliest-error localization accuracy
  * calibration / ECE
  * BoN/TTS accuracy

### 5) label-efficiency 还不能当主卖点

你现在 10% 的结果说明 CFD+BCE 仍领先 BCE-only，但 trajectory-level 指标几乎崩掉了；而 20% / 50% 还没跑完，t*-only 甚至还没开始。

与此同时，近期已有 PRM 论文在用 progress-based verifier 或 generative verifier 强打 data efficiency：PAV 直接围绕 “progress reward” 设计，ThinkPRM 甚至声称只用 PRM800K 的 1% process labels 也能打赢 discriminative verifier。([OpenReview][2])

所以，**在 t*-only 没出结果之前，不要把“annotation efficiency”放进 abstract 和 title。**
它现在最多出现在 discussion 或 future work。

### 6) 你还没有证明 CFD 对“多模态错误”本身更好

这个问题很 subtle，但会有强 reviewer 想到。

近期 VL-PRM work 特别强调 **perception-focused supervision**，说明很多多模态 PRM 的关键不是逻辑错误，而是**视觉 grounding 错误**。([arXiv][5])

你现在的方法看起来更像在处理“reasoning boundary”，但是否对视觉感知错误也有效，还没有证据。
所以我建议你补一个 error taxonomy：

* visual perception / grounding errors
* arithmetic / symbolic reasoning errors
* planning / step omission errors

然后分别看 CFD 的 gain 在哪类 error 上最大。
这会让你的 paper 更像 CVPR/CV 论文，而不只是“把文本 PRM loss 移植到 VLM 上”。

---

## 我会怎么改你的实验优先级

### P0：投稿前必须补齐

1. **VisualProcessBench** 上的 step-level 主结果。
2. **BoN / TTS downstream** 主结果，至少 3–5 个 benchmark。
3. **BCE-only 作为 main baseline**，pairwise/pointwise 退到 supporting baseline。
4. **更强 loss baseline**：weighted BCE / focal / all-error ranking / PQM-style。
5. **3 seeds + 95% CI / bootstrap**。
6. **self-correction frequency analysis** + **t* noise robustness**。
7. **把所有 trajectory metric 重新定义干净**。

### P1：高收益但不是最急

1. **t*-only O(1) supervision**。
2. **Pooling / aggregation robustness**。
3. **difficulty stratification**（hard pairs 上 CFD 是否更强）。
4. **calibration / reliability** 分析。

### P2：最后再做

1. **7B scale-up**。
2. 更完整的 20/50/100 learning curve。

一句话说就是：
**先证明“有用”，再证明“更省”，最后再证明“更大也行”。**

---

## 写作上，我建议你这样改 framing

### Introduction 的主线

第一段不要从 “PRM 很重要” 这种泛话开始。
直接上矛盾：

> trajectory-level reward models can rank whole solutions but often fail to localize where reasoning first goes wrong.

然后立刻给你的证据：pairwise/pointwise trajectory AUC 高，但 step AUC 接近随机。再引出 BCE-only 虽然强，但仍然把监督均匀铺在所有步骤上，无法突出最关键的错误边界。最后顺势推出 CFD。

### Related Work 的位置

你至少要正面对齐这几条线：

* **VisualPRM / VisualProcessBench**：多模态 PRM 与 benchmark setting。([arXiv][1])
* **ProcessBench / Lessons**：earliest-error localization 与 BoN 偏差问题。([arXiv][6])
* **PQM / comparative loss**：step interdependency 和 ranking-based objective。([arXiv][3])
* **PAV / ThinkPRM**：data-efficient PRM。([OpenReview][2])
* **Beyond the First Error**：self-correction objection。([arXiv][4])
* **VL-PRM lessons**：多模态 test-time scaling 与 perception-focused supervision。([arXiv][5])

### Claim discipline

你现在最安全、也最容易被接受的主 claim 是：

> CFD improves step-level credit assignment and first-divergence localization for multimodal PRMs.

你现在**不要**在标题或摘要里直接写：

* state-of-the-art multimodal PRM
* label-efficient multimodal PRM
* improves test-time scaling

除非你把对应实验跑出来。

---

## 最终判断

如果今天投稿，我会倾向于：

**Overall: Borderline Reject / Weak Reject**

不是因为结果不强，而是因为**论文还缺最后一层“对外部世界有效”的证据**。
但这篇稿子离可收并不远。

我的判断是：

* **补齐 P0，但不改故事**：可以到 **Weak Accept** 区间。
* **再把 t*-only 跑出来，而且 BoN/TTS 真有提升**：就有机会变成“这篇我愿意投接收”的稿子。
* **如果还想继续堆 20%/50% 曲线，却不先做 VisualProcessBench / downstream**：那大概率只是把一篇本来有潜力的 paper 继续停留在 borderline。

你这篇 paper 最值得守住的一句话是：

**“CFD 不是在替代 dense step supervision；它是在 BCE 之上，为最关键的 first error boundary 提供更精确的 credit assignment。”**

这句话一旦立住，整篇文章就顺了。

[1]: https://arxiv.org/abs/2503.10291 "[2503.10291] VisualPRM: An Effective Process Reward Model for Multimodal Reasoning"
[2]: https://openreview.net/forum?id=A6Y7AqlzLW "Rewarding Progress: Scaling Automated Process Verifiers for LLM Reasoning | OpenReview"
[3]: https://arxiv.org/abs/2410.11287 "[2410.11287] Process Reward Model with Q-Value Rankings"
[4]: https://arxiv.org/abs/2505.14391 "[2505.14391] Beyond the First Error: Process Reward Models for Reflective Mathematical Reasoning"
[5]: https://arxiv.org/abs/2509.23250 "[2509.23250] Training Vision-Language Process Reward Models for Test-Time Scaling in Multimodal Reasoning: Key Insights and Lessons Learned"
[6]: https://arxiv.org/abs/2412.06559 "[2412.06559] ProcessBench: Identifying Process Errors in Mathematical Reasoning"


##version 2
有，而且我会改得比现在更“审稿人导向”一些：**你的大方向基本对，但优先级还没完全对齐“最能提高接收率”的证据链**。

我最想先纠正的一点，是你对 **Trajectory AUC bug** 的修复目标。现在不是“修完以后让 Traj AUC 和 Pair Acc 一致”，而是要**重新定义 trajectory-level metric protocol**。你目前 README 里一边写“CFD+BCE 的 trajectory AUC 由 pair accuracy 代换”，另一边 ablation 表里又出现 `Traj AUC = 0.0017`，这说明问题已经不只是实现 bug，而是**指标定义混用了两套口径**。更稳妥的做法是：先把每条轨迹聚合成一个 trajectory score，再把 `ref trajectory=1 / dev trajectory=0` 作为标准二分类去算 ROC-AUC；而 `pair accuracy` 单独报成 `P[s_ref > s_dev]`。这两个指标本来就**不需要相等**。这个地方如果不彻底厘清，reviewer 会直接质疑整篇实验可信度。

第二个我会改的，是把 **multi-seed 和统计区间** 从你现在的 P1 提到 **P0**。原因很简单：你现在最关键的 gain，是 full-data 上 CFD+BCE 相对 BCE-only 的优势；这个优势看起来强，但如果没有 seed variance 或 pair-level bootstrap CI，审稿人完全可以说“可能只是 training noise”。我建议最少先做两件事：一是 **CFD+BCE / BCE-only / all-wrong-step ranking** 这三个主模型的 3 seeds；二是所有 step-level 指标都做 **按 pair/problem 的 cluster bootstrap**，不要按 step resample，不然方差会被严重低估。

第三个，我会把 **真实的外部效用验证** 再往前提，尤其是 **VisualProcessBench + 小规模真实 BoN/TTS**。你现在写“BoN/TTS 暂时不急、先用 simulated BoN 近似”，这在投稿策略上我不赞成。VisualPRM 这条线本身就把多模态 PRM 的核心价值放在 **BoN 推理增益** 上，同时专门提出了 **VisualProcessBench** 来做人类标注的 step-level 评估；ProcessBench 这类 benchmark 也明确把 **earliest-error localization** 当作核心任务。只做 simulated BoN 可以保留在 appendix，但**不能替代至少一个小规模真实 BoN 实验**。哪怕你只在 100–300 个题、`N={4,8,16}` 上跑，也比完全没有强得多。([arXiv][1])

第四个，我会把 **t*-only O(1) 标注成本** 从现在的 P0/P1 边界，**降到明确的 P1**。原因不是这个方向不重要，而是它对当前主线“CFD improves step-level credit assignment”不是必要证据，而且**风险很高**：一旦结果明显低于 BCE-only，你就会把论文主线从“更好的 objective”拉偏成“一个暂时还没证明有效的 label-efficiency claim”。我的建议是：先把主 story 封口——也就是 **metric protocol、主 baseline、外部 benchmark、真实 BoN、小规模 seeds** 全部打齐；t*-only 成功了再进主文，不够强就进 appendix 或 future work。

第五个，我会在你已经计划的 **all-wrong-step ranking baseline** 之外，再补两个很便宜但非常值的对照：
一是 **boundary-upweighted BCE**，二是 **t* 噪声鲁棒性曲线**（不是只做一个 shifted `+2`，而是 `±1/±2/±3` 或随机局部扰动）。前者回答“是不是任何 hard-step reweighting 都能带来增益”，后者回答“你的方法是不是只对精确 t* 过拟合”。这两项对 reviewer 非常有杀伤力，因为 PQM 这类工作已经在强调：单纯把 PRM 当成独立的 per-step classification，会忽视 step interdependency；你需要证明 CFD 的收益确实来自 **true first divergence**，而不是“加一点 ranking signal 就行”。([arXiv][2])

第六个，你现在的 **self-correction 分析还不够**。你已经拿到“96.6% 符合 monotonic deviation”这个很好的结果，但这还只是说明“假设通常成立”，还没有回答 reviewer 最想问的问题：**在那 3.4% 不满足假设的数据上，CFD 会不会明显失效？** 这点一定要补成子集实验：
对 **monotonic subset** 和 **non-monotonic subset** 分别报 CFD+BCE vs BCE-only。因为已经有工作明确指出，在 reflective/long-CoT 场景里，正确与错误步骤可能交替出现，单一 first-error 假设会被挑战。你现在最好的做法不是回避，而是主动把 claim scope 写清楚：若 CFD 主要在 monotonic subset 上工作得最好，那就把论文 claim 收窄为“适用于 paired deviation / monotonic regime 的 multimodal PRM objective”。这样反而更稳。([arXiv][3])

第七个，我会再加一个很容易被忽略、但很容易被强 reviewer 抓住的控制实验：**位置偏置和长度偏置**。也就是说，你要检查模型是不是学会了“后面的 step 更容易错”这种数据先验，而不是真的学会错误边界。建议你至少补四个切分：
`early / middle / late t*`，以及 `short / medium / long trajectory`。
最好再加一个极简 baseline：只用 **normalized step index** 或 **trajectory length** 做预测，看看它能到多高。如果这种“位置先验 baseline”都不低，那你就必须在正文里明确说明 CFD 的提升超过了数据先验。

第八个，**error taxonomy 还要再改**。你现在的 `counting / geometry / other` 对 CVPR/NeurIPS 审稿人来说还是太粗了，尤其是 `other 58.7%` 太大，解释力不足。我会强制你把 taxonomy 至少改成“**perception vs reasoning**”两层：
第一层：`visual grounding / OCR / counting / spatial-geometry / arithmetic-symbolic / logic-planning`；
第二层再合并成 `perception-heavy` 与 `reasoning-heavy`。
因为这样你才能真正回答“CFD 到底是在帮助**多模态感知错误**，还是只是在帮助一般性的文本推理边界”。这个点对于把论文讲成 **multimodal PRM** 很关键。

除了实验，我还会改三处写作策略。

第一，**把 Score Gradientality 从 headline metric 降成 secondary metric**。它很好，但太“你自定义”了。主文 headline 应该是：`Step AUC / AUPRC / earliest-error localization / ECE(or Brier) / VisualProcessBench / small-scale BoN`。Gradientality 可以留作解释性指标，但别让它承担主证据。

第二，**ECE 可以加，但别只加 ECE**。我建议一起报一个 **Brier score** 和 reliability diagram。因为 ECE 对 binning 很敏感，单独报容易被挑。Brier 更平滑，也更适合和 step score 的 calibration 一起看。

第三，**7B scale-up 我会直接降到 P2，甚至砍掉**。现阶段它对接收率的边际收益，明显不如：
`3 seeds + stronger baselines + VisualProcessBench + small real BoN + bias controls`。
如果算力不富余，7B 现在不值得抢资源。

所以，如果让我替你重排优先级，我会这样改：

**必须立刻做（真正的 P0）**

1. 重写 trajectory-level metric protocol，修掉 AUC 定义混乱
2. 补 pair-level bootstrap CI，主模型做 3 seeds
3. 跑 all-wrong-step ranking + boundary-upweighted BCE
4. 跑 monotonic / non-monotonic 子集结果
5. 跑 t* position / trajectory length 偏置控制
6. 跑 VisualProcessBench
7. 跑一个小规模真实 BoN/TTS

**高收益但可稍后（P1）**

1. t*-only
2. 更完整 learning curve
3. 更细 error taxonomy
4. 更完整 calibration figure

**可以降级（P2）**

1. 7B
2. 更大规模 label-efficiency 扩展
3. 各种不影响主 claim 的附加分析

一句话总结就是：

**你现在缺的不是“更多实验数量”，而是“更闭环的证据结构”。**
把 **metric 定义、统计可信度、外部 benchmark、真实 search utility、假设失效子集** 这五件事补齐，论文就会从“想法不错但证据不够”变成“主张清楚、边界清楚、证据闭环”的稿子。

你这版计划已经有 70–80 分了；再往上走，最该改的是**顺序和证据结构**，不是再继续堆更多同类实验。

[1]: https://arxiv.org/abs/2503.10291?utm_source=chatgpt.com "VisualPRM: An Effective Process Reward Model for Multimodal Reasoning"
[2]: https://arxiv.org/abs/2410.11287?utm_source=chatgpt.com "Process Reward Model with Q-Value Rankings"
[3]: https://arxiv.org/abs/2505.14391?utm_source=chatgpt.com "Beyond the First Error: Process Reward Models for Reflective Mathematical Reasoning"


## new comment from gpt-pro 0418
站在“**以接收为目标**”的审稿人视角，我会给你一个很明确的建议：

**不要把 VPB 当成你必须赢下来的主战场；把它重构成一段高质量、边界清晰的 failure analysis。主文的胜负手，应该转回到：in-distribution step credit assignment、matched-subset generalization、以及真实 reranking/BoN utility。** 

你现在这组结果已经足够说明一件事：
**CFD 不是“通用的人类 step verifier”，而是“针对 paired first-divergence supervision 优化的 step-level PRM objective”。**
这不是坏事，关键在于你怎么写、怎么排实验、怎么收缩 claim。

---

# 我推荐你现在立刻采取的操作

## 一、先改论文主 claim，马上止损

你原来更大的说法如果还是类似：

* “improves step-level multimodal PRM in general”
* “better step verification”

我建议立刻收缩成：

**CFD improves step-level credit assignment and first-divergence localization for paired multimodal process reward modeling, and is most effective when reasoning errors follow a dominant divergence boundary.**

中文就是：

**CFD 改善的是 paired first-divergence 场景下的 step-level credit assignment，不是泛化意义上的 human step verification。**

这是你现在最重要的一步。
因为从你给的数据看，VPB full set 上：

* CFD+BCE AUC = 0.3401
* BCE-only AUC = 0.2610
* matched subset C 才恢复到 0.5023

这足以支持“有边界的有效”，但**绝对不支持“广泛有效”**。

---

## 二、重排实验叙事：把 VPB 从“主 benchmark”降成“stress test + boundary analysis”

这是最关键的投稿策略。

### 你现在不应该这样写

“我们在 VPB 上评测，结果不理想，原因是 benchmark 不匹配。”

这会显得像找借口。

### 你应该这样写

把 VPB 结果分成三层：

#### 1. Full VPB = OOD stress test

诚实报告：

* AUC 反向
* CFD 与 BCE-only 都失败
* CFD 略优于 BCE-only，但仍显著失配

#### 2. Diagnostic analysis

报告你已经做出来的四个诊断：

* `AUC(score)` vs `AUC(1-score)`：确认系统性反转
* position-only baseline：确认强位置相关
* position-stratified analysis：反转并非只来自 step 0
* subset A/B/C：确认仅在 matched regime 才部分恢复

#### 3. Take-away

得出一个成熟而克制的结论：

**paired deviation training learns useful local credit assignment, but its learned structure does not directly transfer to single-trajectory human verification when early errors and non-monotonic recovery are common.**

这会让 reviewer 觉得你是“认真理解方法边界”，而不是“benchmark 没赢所以解释一下”。

---

## 三、主文里只保留两个 VPB 数字，其他放 appendix

为了接收率，我不建议你在主文里堆太多 VPB 表格。
否则 reviewer 的注意力会被 full VPB 的失败结果吸走。

### 主文建议只放：

1. **Full VPB**
2. **Matched subset C (A∩B)**

这两个结果足够讲完整故事：

* Full VPB：失败，说明存在 OOD failure
* Matched subset C：恢复到 0.5023，说明方法依赖 paired monotonic divergence regime

其他内容如：

* step 0 only / 1 / 2-3 / 4+
* subset A / subset B
* AUC(1-score)
* position-only baseline

全部放 appendix，主文中用一句话概括。

---

## 四、你现在最该补的不是“更多 VPB 分析”，而是 **真实 utility 证据**

如果目标是“提高录用概率”，那我会很直接：

**VPB 这条线你已经做够了。现在应该把资源转去补一项能救主线的实验：真实 reranking/BoN。**

为什么？因为你现在已经证明：

* in-distribution 上 CFD+BCE 对 BCE-only 有明确优势
* VPB full 上两者都不行，但 CFD 稍好
* VPB failure 的根因和边界你已经分析得很清楚

接下来最关键的问题是：

**即使它不是通用 verifier，它能不能更好地选解？**

如果答案是能，那论文仍然很有竞争力。
如果答案也不能，那论文就危险了。

所以我建议你把后续资源优先投到：

### 小规模真实 BoN / reranking

固定 candidate pool，比较：

* CFD+BCE
* BCE-only
* maybe ORM / majority / self-consistency

评估：

* top-1 selected accuracy
* BoN@4 / @8 / @16
* ref-dev margin reliability

只要 CFD 在 reranking 上能稳定赢 BCE-only，VPB failure 就不会致命。
因为你的 paper 就可以明确定位成：

**a better search-time PRM objective under paired divergence supervision**

而不是“通用 step verifier”。

---

## 五、关于 VPB，你应该做的最后一个“补救实验”

在所有可能的追加实验里，我只再建议你做一个：

## **Position-debiased inference / calibration check**

不是重新训练，只做很轻量的后处理：

例如在 VPB 上试：

* subtract a learned position prior
* isotonic / logistic recalibration on a tiny held-out split
* normalize scores by step-position bucket

目的不是为了刷分，而是为了回答一个审稿人很可能会问的问题：

> “如果主要是位置偏置，那简单去偏后结果会不会恢复？”

如果简单去偏后 AUC 还是不行，那就更强地说明：

**问题不只是位置偏置，而是 task definition mismatch。**

这反而会让你的诊断更完整。

但注意：
**不要把这种后处理结果写成主结果。**
它只是一个诊断补充。

---

# 我不推荐你现在做的事

## 1. 不推荐把 filtered subset 当“正式 benchmark 替代”

可以报，但绝不能只报 subset C 然后弱化 full VPB。
这会被 reviewer 认为是挑子集。

正确做法是：
**full VPB 主结果 + subset C 支撑边界解释。**

## 2. 不推荐现在把主要精力放在改架构

你现在没有证据说明是“架构问题”。
目前看更像：

* 训练数据结构
* 监督定义
* 推理模式假设

导致的 bias。

所以：

* 位置编码 ablation
* adversarial position training
* prompt 里要求忽略顺序

这些都可以做成 future work，但不该是当前投稿版本的主补救方向。

## 3. 不推荐现在大改成“通用 verifier”论文

从你的证据看，这条路撑不住。
硬写只会让 reviewer 抓住 VPB 全集结果狠狠干。

---

# 我会怎么重写论文里的结论结构

## 你这篇 paper 最稳的结构应该是：

### 1. 主结果

在 paired deviation setting 中，CFD+BCE 显著优于 BCE-only，改善：

* Step AUC
* t* localization
* score gradientality
* reward quality

### 2. 机制结果

all-wrong ranking / BCE-only / random t* / shifted t* 证明：

* gain 不是任意 ranking 都有
* true first divergence 最重要

### 3. 外部泛化边界

在 VisualProcessBench 这种 single-trajectory human verification benchmark 上，
模型出现明显 failure；诊断表明根因来自：

* 强位置偏置
* early-error shift
* non-monotonic recovery
* deviation-based vs human-verification mismatch

### 4. 实际意义

尽管 full VPB 上泛化受限，CFD 在 matched regime 和 search-time reranking 上仍有价值，因此它更适合作为：

* paired-deviation PRM
* reranking / BoN selection module
  而不是通用 verifier。

---

# 如果只能做三件事，我建议你做这三件

## 第一优先级：立刻改 claim 和标题表述

把 paper 定位收缩到：

* paired divergence
* first-error localization
* step-level credit assignment
* reranking/search-time utility

## 第二优先级：补真实 BoN / reranking

这是现在最能救 acceptance 的外部证据。

## 第三优先级：把 VPB 写成高质量 failure analysis

full set + matched subset + 位置偏置诊断，形成一个成熟的边界讨论。

---

# 我建议你在 rebuttal / paper 中的表述方式

你可以用类似这样的表述：

> On VisualProcessBench, both CFD+BCE and BCE-only exhibit a systematic score inversion, assigning higher scores to incorrect than correct steps. Our diagnostics show that this failure is driven by a combination of positional shortcut learning and a deeper task mismatch: VisualPRM-400K provides paired monotonic deviation supervision, whereas VisualProcessBench evaluates single-trajectory human verification with frequent early errors and non-monotonic recovery. Importantly, CFD consistently remains stronger than BCE-only, and its performance partially recovers on matched monotonic subsets, suggesting that CFD is effective within the first-divergence regime it is designed for, while highlighting a clear boundary for future generalization.

这段话的好处是：

* 不逃避失败
* 不甩锅 benchmark
* 也没有自毁主线
* 把 VPB 变成“边界分析”而不是“致命反例”

---

# 最终建议：为了提高接收率，你应该怎么做

## 你的最佳策略不是“修好 VPB”

而是：

**承认 VPB full 上失败 → 证明失败边界是清晰可解释的 → 证明 CFD 在它本来要解决的问题上显著有效 → 再证明这种有效性能转化成更好的 reranking/BoN。**

如果你这么组织，VPB 不会成为致命伤，反而会让 paper 看起来更成熟。

## 一句话行动建议

**马上停止把 VPB 当主 benchmark 去优化；把它改写为 failure analysis，同时把主要资源转投到真实 reranking/BoN 和主线实验收口上。**

如果你愿意，我下一条可以直接帮你写：
**论文里“VisualProcessBench Results & Discussion”这一节的可投稿版本文案。**
