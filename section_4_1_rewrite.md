### 4.1 Quadrant I: Text-only CoT

**Definition**: Methods that generate free-form textual reasoning without external tool feedback.

#### 4.1.1 Approach Overview

Quadrant I methods represent the simplest approach to Visual CoT: the model generates step-by-step natural language explanations based solely on its internal representations. Verification, when present, relies on:
- **Self-consistency**: Multiple reasoning samples should agree
- **Reflection and self-correction**: The model critiques and revises its own reasoning
- **Process supervision**: External feedback on step quality (PRMs, rule-based rewards, DPO)
- **Visual cues and structured stages**: Patch-level hints, multi-stage pipelines, or contrastive signals to improve grounding

**Why Text-only?** Despite limitations, Quadrant I approaches remain popular because:
- No tool integration complexity
- Fast inference (no external calls)
- Works with any VLM (no special capabilities required)
- Human-readable by default

Recent work (2024–2026) has expanded the design space significantly: from consistency-based verification (CURE) to process reward models (VisualPRM, VRPRM), from self-correction learning (SCL, Sherlock) to RL for visual reasoning (R1-VL, Visionary-R1, GThinker), and from structured stages (LLaVA-CoT) to visual cue augmentation (ChainV, PatchCue) and faithfulness analysis (Journey Before Destination, MIRA).

**Connections and Progression**: CURE establishes consistency as a weak verification proxy; R3V extends this with self-training and reveals the noisy CoT problem (8–70% correct CoT in correct-answer solutions). SCL and Sherlock show that self-correction requires explicit training—inference-time prompting fails. Process supervision (VisualPRM, VRPRM, R1-VL) addresses step-level quality; Critic-V and LLaVA-Critic-R1 use critic feedback. Structured formats (LLaVA-CoT, Visionary-R1) and visual cues (ChainV, PatchCue) improve grounding. Benchmarks (MIRA, Journey Before Destination, Visual CoT) diagnose gaps: text-only reasoning is insufficient for visualization-essential tasks; faithfulness and answer accuracy can diverge.

---

#### 4.1.2 Representative Works

##### Consistency & Self-Correction (6 papers)

This subcategory focuses on improving reasoning quality through consistency evaluation, reflection, self-correction training, noisy-thinking mitigation, and contrastive self-improvement—all without external tools.

**CURE** (Chen et al., NAACL 2024) introduces the first benchmark for measuring both reasoning performance and consistency in VLMs. It proposes forward consistency (Cf)—whether correct CoT steps lead to correct final inference—and backward consistency (Cb)—whether correct final inference implies correct CoT steps. A two-stage training framework (SFT + RLAIF) uses LLM feedback (GPT-3.5-Turbo) on Sophistication, Consistency, and Groundedness to rank reasoning chains. CURE achieves ~4% relative improvement (Ro: 54.93→56.91, Cf: 83.66→86.67) on the CURE benchmark (1,622 samples). A fundamental gap remains: even SOTA models (BLIP-2) show Cf=83.1% vs. human Cf=95.5%, and consistency ≠ correctness—models can be consistently wrong.

**R3V** (Cheng et al., NAACL 2025) proposes self-training via reflection on CoT rationales, requiring only QA pairs and a small GPT-distilled warmup (800–1000 samples per dataset). It bootstraps positive samples (correct answer) and negative samples (wrong answer), then introduces self-refine loss (given wrong CoT, generate corrected version) and self-select loss (compare multiple candidates, identify correct one). R3V achieves 23–60% relative improvement over GPT-distilled baselines across TabMWP, ChartQA, CLEVR-Math, MiniWob, GeoQA, M3CoT. Test-time self-selection (N=3) consistently outperforms majority voting. A critical finding: only 8–70% of correct-answer solutions have fully correct CoT (M3CoT: 8%), explaining why DPO fails (STaR+DPO ≈ STaR).

**Sherlock** (Ding & Zhang, NeurIPS 2025) addresses error propagation through trajectory-level self-correction: instead of regenerating the entire response (R3V), the model corrects only the erroneous suffix while preserving the correct prefix. Preference data is constructed via visual perturbation—applying noise to images creates controllable quality gaps between responses. Dynamic β adapts regularization to sample quality. With only 20k annotated samples (vs. 100k LLaVA-CoT, 260k Mulberry), Sherlock achieves 64.1% direct and 65.4% after self-correction. Stage III enables online self-improvement without external supervision. Analysis reveals step-wise self-correction occurs in <10% of cases without explicit training; Modify One Step causes accuracy to drop to ~25%.

**SCL** (He et al., ACL 2025) provides a key negative result: VLMs *cannot* effectively self-correct at inference time without fine-tuning—multi-turn correction prompts and external critiques fail to improve accuracy. However, DPO on self-generated two-turn correction data (SELFCORSET) significantly improves performance. SELFCORSET is constructed by prompting the model twice (initial response, then correction prompt) and labeling pairs by correctness (++, +−, −+, −−). SCL reframes self-correction as a training-time capability: the model learns to generate better first-pass responses, reducing inference cost compared to iterative refinement.

**RTWI** (Li et al., arXiv 2026) addresses the Noisy Thinking problem in Thinking-with-Images: imperfect visual cues and reasoning steps cause error accumulation, degrading final answers. RTWI proposes text-centric reliability estimation—the model (or auxiliary model) evaluates cue and step quality from the reasoning trace itself, without external tools. Robust filtering removes low-reliability components; voting aggregates over multiple reasoning paths. This prevents noise from contaminating the final answer and improves verifiability through internal quality control.

**VC-STaR** (Pan et al., arXiv 2026) leverages VLMs' intrinsic ability to compare contrastive VQA pairs (e.g., "Which image shows X?" with two similar images) to build a self-improving framework. It generates VisCoR-55K contrastive pairs and self-generated rationales, then performs SFT on these rationales. The contrastive structure provides implicit verification—the model must identify the correct image, reducing "explain without seeing" risk. Visual contrast bootstrap reduces hallucinations without external tools.

---

##### Structured Stages & Visual CoT (6 papers)

These methods introduce structured reasoning pipelines, visual grounding traces (bounding boxes, patch cues), or multi-agent architectures to improve interpretability and grounding—while remaining tool-free.

**LLaVA-CoT** (Xu et al., ICCV 2025) proposes a four-stage pipeline: Summary (problem framing), Caption (perceptual grounding in language), Reasoning (logical derivation), Conclusion (answer extraction). Trained on LLaVA-CoT-100k (GPT-4o-generated stage-wise annotations), it uses Stage-Wise Retracing Search (SWIRES) for beam search at stage boundaries rather than token level. LLaVA-CoT outperforms base model by 9.4% and surpasses Gemini-1.5-pro, GPT-4o-mini, and Llama-3.2-90B. The Caption stage forces explicit visual description before reasoning; SWIRES achieves +9.4% over greedy decoding. A failure mode: Caption-Reasoning stage-boundary drift—Reasoning may contradict or ignore Caption.

**Visual CoT** (Shao et al., NeurIPS 2024 DB) introduces a 438K dataset with intermediate bounding-box annotations (~98k with full reasoning steps) spanning five domains. A multi-turn pipeline: Turn 1 predicts the answer-critical region (model-generated bbox), Turn 2 receives the cropped region and generates reasoning + answer. The benchmark evaluates region identification (IoU) and reasoning accuracy. Key finding: MLLMs struggle when answer-critical information resides in small or high-resolution regions; CoT traces without explicit visual focus are uninterpretable.

**Insight-V** (Dong et al., arXiv 2024) addresses long-chain visual reasoning with a multi-agent pipeline: a Reasoning Agent generates extended CoT (problem decomposition, evidence gathering, logical steps) and a Summary Agent distills conclusions. This addresses "long-chain training collapse" where direct supervision with long reasoning degrades general performance. Progressive reasoning path generation and multi-granularity quality assessment (answer correctness + step coherence) produce training data; iterative DPO stabilizes the Reasoning Agent. Significant gains on challenging multimodal benchmarks requiring complex visual reasoning.

**ChainV** (Zhang et al., arXiv 2025) injects atomic visual hints (pixel coordinates + reliability via Bernoulli process) into reasoning via two-stage selection: coarse patch selection based on previous step, then attention-intensity-weighted atomic hint refinement. Consistency-based evaluation adaptively adjusts self-reflection depth—reducing over-thinking on simple steps. ChainV achieves +2.3% on MathVista within MIMO-VL-RL with 51.4% latency reduction and 24.5% shorter output tokens. Training-free; operates on top of existing models.

**PatchCue** (Qi et al., arXiv 2026) replaces pixel-level bounding boxes and point-based cues with textified patch coordinates—a balance between spatial precision and robustness. A two-stage pipeline: cold-start SFT establishes patch-cue reasoning; RL with process-supervised cue reward guides intermediate steps toward correct visual grounding. The cue reward evaluates whether patch references correctly ground reasoning. PatchCue outperforms pixel-level and point-based baselines across general VQA, complex reasoning, and document understanding.

**Zooming without Zooming** (Wei et al., arXiv 2026) distills inference-time agentic zooming (iterative region cropping and re-processing) into training-time primitives. Region-to-image distillation transfers zooming capability into model weights; at inference, a single forward pass achieves fine-grained perception without tool calls. ZoomBench (845 VQA) evaluates fine-grained multimodal perception. The approach reduces latency and tool dependency while internalizing zooming capability.

---

##### PRM & Process Supervision (4 papers)

These methods use process reward models, critic models, or DPO with process-level signals to improve step-level correctness and faithfulness.

**VisualPRM** (Wang et al., arXiv 2025) introduces an 8B multimodal Process Reward Model trained on VisualPRM400K. Labels are generated via Monte Carlo sampling: for each prefix ending at step k, sample 16 completions and estimate P(correct answer | prefix) via majority voting; label step k correct if P>0.7, incorrect if P<0.3. VisualPRM formulates process supervision as multi-turn chat (sequential step correctness prediction) and supervises all steps. Best-of-N inference scores N candidate chains; achieves +5.9 points on InternVL2.5-78B across 7 benchmarks, outperforming ORM and Self-Consistency. VisualProcessBench (2,866 problems, 26,950 step labels) provides human-annotated evaluation. Inference cost: N× generation + N×T PRM scoring.

**Critic-V** (Zhang et al., CVPR 2025) applies an Actor-Critic paradigm: a Reasoner VLM generates reasoning paths and a separate Critic VLM provides natural-language critiques (e.g., "incorrectly attributed spatial relationship"). The Critic is trained via DPO on preferences ranked by Rule-based Reward (RBR)—evaluating whether critique correctly identifies errors and whether following it leads to correct answers. At inference, the Reasoner iteratively refines based on Critic feedback. Critic-V outperforms GPT-4V on 5 of 8 benchmarks. Natural-language critique provides richer, context-sensitive feedback than binary correct/wrong. Failure mode: critique-induced degradation when Critic gives incorrect guidance.

**Improve VLM CoT** (Zhang et al., ACL 2025) diagnoses that training on short answers (even at scale) fails to generalize to CoT—e.g., 26K ChartQA short-answer training improves CoT by only 0.6 points. A two-stage pipeline: (1) Distillation—GPT-4o generates detailed CoT for 193K examples, SFT on enriched data; (2) DPO—construct positive/negative pairs by comparing model-generated CoT quality against short-answer ground truth. Achieves significant CoT improvements; notably, CoT training also improves direct-answer prediction—teaching general reasoning, not just longer outputs.

**VRPRM** (Chen et al., arXiv 2025) achieves data-efficient process supervision: only 3.6K CoT-PRM SFT + 50K non-CoT PRM RL data surpasses a non-thinking PRM trained on 400K. Stage 1 instills step-level evaluation with visual reasoning; Stage 2 scales via non-CoT RL without expensive CoT annotation. VRPRM achieves up to 118% relative improvement over base model in Best-of-N. The combined strategy demonstrates a new paradigm for PRM training with efficient data utilization. Limitation: 3.6K seed quality is critical; BoN inference cost scales with N.

---

##### RLVR: RL for Visual Reasoning (5 papers)

These methods apply reinforcement learning (GRPO, DPO, iterative SFT-RL) to improve visual reasoning, often with step-level or format rewards to prevent shortcuts.

**R1-VL** (Zhang et al., ICCV 2025) proposes Step-wise Group Relative Policy Optimization (StepGRPO) with two rule-based process rewards: StepRAR (soft key-step matching rewards intermediate reasoning accuracy) and StepRVR (logic evaluation rewards reasoning completeness and consistency). Key steps are extracted automatically from reference solutions; no manual step-level annotation or external tools required. Dense step-level rewards address sparse outcome-only GRPO—reasoning paths receive rewards for correct intermediate steps even if final answer is wrong. R1-VL achieves SOTA across 8 benchmarks (MathVista, ChartQA, TabMWP, CLEVR-Math, GeoQA, etc.) with more stable training dynamics.

**Visionary-R1** (arXiv 2025) mitigates RL shortcuts—models producing short, uninformative reasoning that works on easy training questions but fails to generalize. A structured caption→reason→answer format forces models to interpret images before reasoning, preventing reliance on spurious textual cues. Format reward encourages generating all three sections. Trained on 273K CoT-free QA pairs with GRPO only (no explicit CoT supervision), Visionary-R1 outperforms GPT-4o, Claude 3.5-Sonnet, and Gemini-1.5-Pro on visual reasoning benchmarks.

**OpenVLThinker** (Deng et al., NeurIPS 2025) introduces iterative SFT-RL cycles: SFT surfaces latent reasoning actions and narrows the RL search space; each RL stage refines skills and produces higher-quality SFT data for the next cycle. Addresses two problems: (1) distilling text-only reasoning (DeepSeek R1) into LVLMs via SFT causes visual grounding degradation; (2) pure RL faces overly large search space. OpenVLThinker-7B improves MathVista (+3.8%), EMMA (+2.4%), HallusionBench (+1.6%), and others, competing with GPT-4o and Claude-3.5 on math and perception tasks.

**LLaVA-Critic-R1** (arXiv 2025) challenges the separation between critic and policy: it reorganizes preference-labeled critic datasets into verifiable training signals and applies RL directly to a base generative model. The unified model excels at both evaluation (critic) and generation (policy). The policy achieves +5.7% over Qwen-2.5-VL-7B across 26 benchmarks; LLaVA-Critic-R1+ reaches 71.9 on MMMU at 7B scale. Best-of-128 self-critique at test time yields +13.8% on five reasoning tasks without additional training—a simple path toward scalable, self-improving multimodal systems.

**GThinker** (Zhan et al., arXiv 2025) introduces Cue-Rethinking: inferences are grounded in visual cues and iteratively reinterpreted to resolve inconsistencies. Addresses MLLMs' failure to integrate visual information effectively—over-relying on logic/knowledge-based "slow thinking." A two-stage pipeline: pattern-guided cold start (SFT on cue-rethinking examples) + incentive RL. GThinker-11K (7K iteratively-annotated paths + 4K RL samples) achieves 81.5% on M³CoT, surpassing O4-mini, with 2.1% improvement on general benchmarks while maintaining math performance.

---

##### Faithfulness Analysis & Benchmarks (4 papers)

These works analyze visual faithfulness, provide diagnostic benchmarks, or generate high-quality training data for geometric and general visual reasoning.

**Journey Before Destination** (arXiv 2025) presents the first systematic analysis of visual faithfulness in reasoning chains. Standard evaluations measuring only final-answer accuracy fail to capture whether reasoning is grounded in visual content. The framework decomposes CoT into perception steps (statements about visual content) vs. reasoning steps (logical deductions), uses off-the-shelf VLM judges to evaluate step-level faithfulness (training- and reference-free), and includes human meta-evaluation. A lightweight self-reflection procedure detects unfaithful perception steps and locally regenerates them, improving Unfaithful Perception Rate while preserving answer accuracy.

**R-CoT / TR-CoT** (Deng et al., arXiv 2024) addresses geometric reasoning data scarcity via reverse CoT: instead of question→answer, start from known geometric properties in diagram descriptions, apply theorem-based reasoning to derive measurable properties, then formulate questions targeting those properties. GeoChain (TR-Engine) synthesizes theorem-grounded diagrams with structured textual descriptions; theorem validation ensures correctness. R-CoT-8B achieves up to 16.6% improvement over prior SOTA on MathVista and outperforms GPT-4o by 13% on average. Theorem validation is used at data construction, not inference.

**VisReason** (Li et al., arXiv 2025) introduces a 489K visual CoT dataset spanning four domains with multi-round, human-like rationales. VisReason-Pro (165K) provides expert-level GPT annotations, detailed reasoning traces, and 3D spatial grounding via depth-informed annotations. The dataset addresses scarcity of stepwise visual reasoning data. Fine-tuning Qwen2.5-VL on VisReason and VisReason-Pro yields substantial improvements in step-by-step accuracy, interpretability, and cross-benchmark generalization.

**MIRA** (Zhou et al., arXiv 2025) is a 546-problem benchmark for tasks where generating intermediate visual images (sketches, structural diagrams, path drawings) is essential—mirroring human "drawing to think." Three evaluation levels: direct input (image + question only), text-only CoT (image + thinking prompts), and Visual-CoT (annotated image clues + textual thinking prompts). Key finding: existing MLLMs perform poorly with text-only prompts but improve by 33.7% on average when intermediate visual cues are provided. Pass@k and textual prompt alignment yield only limited improvements compared to Visual-CoT, underscoring the critical role of imagined visual information.

---

#### 4.1.3 Verification Strategies

| Strategy | Mechanism | Representative Works | Strength | Limitation |
|----------|-----------|---------------------|----------|------------|
| **Self-Consistency** | Multiple samples → agreement | CURE, R3V | Simple, no tools | Consistent ≠ correct |
| **Reflection / Self-Correction** | Model critiques and revises own reasoning | R3V, Sherlock, SCL | Can catch obvious errors | May not recognize subtle mistakes |
| **Process Supervision (PRM)** | Step-level scoring by learned model | VisualPRM, VRPRM | Strongest Q1 checkability | PRM may have blind spots; BoN cost |
| **Process Rewards (RL)** | StepRAR, StepRVR, format rewards | R1-VL, Visionary-R1 | Dense rewards, no annotation | Rule-based; domain-dependent |
| **Visual Cues** | Patch coordinates, atomic hints, grounding traces | ChainV, PatchCue, Visual CoT | Explicit grounding | No external verification |
| **Critic Feedback** | Natural-language critique from separate VLM | Critic-V | Richer than scalar rewards | Critic can be wrong; iteration cost |
| **DPO / Preference Learning** | Correct vs. incorrect reasoning pairs | Improve VLM CoT, SCL, GThinker | Calibrates reasoning quality | Noisy CoT degrades DPO (R3V) |
| **Reliability Filtering & Voting** | Estimate cue/step reliability; filter and vote | RTWI | Mitigates noisy thinking | Estimator errors; over-filtering |
| **Contrastive Self-Improvement** | Contrastive VQA pairs; quality via discrimination | VC-STaR | Reduces hallucination | Self-generated rationale errors |
| **Constraint Checking** | Validate against stated rules | — | Catches logical violations | Rules must be explicit |

---

#### 4.1.4 Failure Modes

1. **Plausible-but-Unfaithful Reasoning**
   - Model generates coherent explanation that doesn't reflect actual computation
   - Example: "I see a dog" when image contains a cat, but answer is still correct
   - **CURE**: Acknowledges hallucination in SFT; RLAIF's "Groundedness" criterion cannot truly verify visual grounding
   - **R3V**: Figure 6 shows only 8–70% of correct-answer solutions have fully correct CoT (M3CoT: 8%)
   - **Journey Before Destination**: Reveals disconnect between answer accuracy and step-level visual faithfulness

2. **Consistency-Correctness Gap**
   - Multiple samples agree but are all wrong
   - **CURE**: Consistency metrics (Cf, Cb) measure internal coherence, not truthfulness; even best model shows 30% gap vs. human
   - **R3V**: DPO fails (STaR+DPO ≈ STaR) because positive samples often contain flawed CoT

3. **Reflection and Self-Correction Limitations**
   - Model cannot identify its own errors without explicit training
   - **SCL**: Inference-time self-correction fails without fine-tuning; prompts and external critiques do not improve
   - **Sherlock**: Step-wise self-correction occurs in <10% of cases; even with "aha moments," only ~50% lead to correct answers; Modify One Step causes accuracy to drop to ~25% (random guess)
   - **Critic-V**: Critique-induced degradation—incorrect critiques can revise correct reasoning into wrong

4. **Error Propagation**
   - Early mistakes cascade through CoT
   - **Sherlock**: Trajectory-level correction preserves correct prefix but requires model to identify error point
   - **R3V**: Visual perception errors (e.g., OCR mistakes) propagate; self-refine corrects post-hoc but cannot prevent initial errors
   - **ChainV**: Incorrect patch selection propagates; consistency evaluation may misguide reflection depth

5. **No External Grounding**
   - Cannot verify factual claims about visual content
   - **MIRA**: Text-only CoT and prompts yield limited improvement; 33.7% gain when intermediate visual cues provided
   - **Visual CoT**: Wrong bounding box in Turn 1 silently corrupts all reasoning in Turn 2
   - **LLaVA-CoT**: Caption-Reasoning stage-boundary drift—Reasoning may contradict or ignore Caption

6. **PRM and Reliability Estimator Blind Spots**
   - **VisualPRM, VRPRM**: PRM may assign high scores to plausible-but-wrong steps (PRM hallucination)
   - **RTWI**: Reliability estimator may misclassify; over-filtering removes correct steps; voting may reinforce correlated errors
   - **VRPRM**: 3.6K CoT-PRM seed quality is critical; small dataset may limit domain coverage

7. **RL Shortcuts and Reward Hacking**
   - **Visionary-R1**: Without explicit structure, models produce short, uninformative reasoning that works on easy questions but fails to generalize
   - **R1-VL**: Outcome-only GRPO suffers sparse rewards; step-level rewards improve but rule-based matching has limitations
   - **GThinker**: RL reward design matters; outcome-only rewards may encourage shortcut strategies

8. **Data and Domain Limitations**
   - **CURE**: Limited to everyday scenes (Sherlock-derived); performance on medical, charts, scientific diagrams unknown
   - **VisReason**: 489K/165K scale; generalization to unseen domains uncertain
   - **R-CoT**: Geometric domain; theorem validation at data construction, not inference
   - **VC-STaR**: Self-generated rationales may contain errors; bootstrap instability; VisCoR-55K coverage limits

9. **Structured Output and Visual Cue Limitations**
   - **LLaVA-CoT**: Hallucinated Caption as reasoning foundation—if Caption misidentifies (e.g., wrong color, miscount), Reasoning builds on false foundation
   - **ChainV**: Incorrect patch selection may target visually salient but semantically irrelevant regions; Bernoulli stochastic process causes variance across runs
   - **PatchCue**: Process-supervised cue reward could be gamed if reward model has blind spots; patch representation may not generalize to all spatial reasoning
   - **Zooming without Zooming**: Distillation may not perfectly transfer zooming capability; without explicit region output, cannot verify which regions were attended

10. **Iterative and Multi-Turn Overhead**
    - **Critic-V**: Multi-turn Reasoner-Critic loop increases inference cost; each refinement requires full generation
    - **R3V**: Test-time self-selection (N=3) ≈ 4× cost of Test@1; plateaus at large N due to input length limits
    - **VisualPRM**: BoN with N=16 and T=10 steps ≈ 160× more expensive than greedy decoding
    - **LLaVA-Critic-R1**: Best-of-128 yields +13.8% but requires 128× generation + 128× critic scoring

---

#### 4.1.5 Design Trade-offs Across Subcategories

| Subcategory | Data Efficiency | Inference Cost | Verifiability | Key Trade-off |
|-------------|-----------------|----------------|---------------|----------------|
| **Consistency & Self-Correction** | High (R3V: QA only; Sherlock: 20k) | Low–Medium (R3V test-time selection adds cost) | Low–Medium | Consistency ≠ correctness; self-correction requires training |
| **Structured Stages & Visual CoT** | Medium (LLaVA-CoT: 100k; VisReason: 489k) | Low–Medium (SWIRES, multi-turn add cost) | Medium | Stage-boundary drift; wrong bbox corrupts reasoning |
| **PRM & Process Supervision** | Low–High (VRPRM: 3.6k+50k; VisualPRM: 400k) | High (BoN: N× generation + PRM scoring) | Medium–High | PRM blind spots; BoN cost prohibitive for real-time |
| **RLVR** | High (Visionary-R1: 273k CoT-free; GThinker: 11k) | Low (single pass) | Medium | RL shortcuts; reward design critical |
| **Faithfulness & Benchmarks** | N/A (evaluation/data) | Varies | Diagnostic | MIRA: 33.7% gap between text-only and Visual-CoT |

**Emerging Patterns**: (1) Process-level supervision (PRM, step rewards) consistently outperforms outcome-only training; (2) structured output formats (caption→reason→answer, four-stage) prevent shortcuts; (3) self-improvement and contrastive bootstrap reduce annotation cost; (4) test-time scaling (BoN, self-selection) provides accuracy/cost trade-off without retraining.

**Summary of 25 Papers by Subcategory**:

| Subcategory | Papers | Key Verification Mechanism |
|-------------|--------|---------------------------|
| Consistency & Self-Correction | CURE, R3V, Sherlock, SCL, RTWI, VC-STaR | Consistency metrics, self-refine/select, trajectory correction, reliability filtering, contrastive bootstrap |
| Structured Stages & Visual CoT | LLaVA-CoT, Visual CoT, Insight-V, ChainV, PatchCue, Zooming w/o Zooming | Four-stage pipeline, bbox grounding, multi-agent, atomic hints, patch cues, region distillation |
| PRM & Process Supervision | VisualPRM, Critic-V, Improve VLM CoT, VRPRM | Step-level PRM, natural-language critique, DPO+distillation, data-efficient PRM |
| RLVR | R1-VL, Visionary-R1, OpenVLThinker, LLaVA-Critic-R1, GThinker | StepGRPO, format reward, SFT-RL cycles, critic-as-policy, cue-rethinking |
| Faithfulness & Benchmarks | Journey Before Destination, R-CoT/TR-CoT, VisReason, MIRA | Perception/reasoning decomposition, reverse CoT, large-scale CoT data, visualization-essential benchmark |

**Key Datasets and Benchmarks Introduced**:

| Name | Size | Source | Purpose |
|------|------|--------|---------|
| CURE | 1,622 | Sherlock-derived | Consistency + reasoning evaluation |
| LLaVA-CoT-100k | 100K | Multi-source VQA | Four-stage CoT training |
| Visual CoT | 438K (98K with full CoT) | 11 source datasets | Bbox grounding + reasoning |
| VisualPRM400K | 400K | MC sampling | PRM training |
| VisualProcessBench | 2,866 problems, 26,950 steps | Human annotation | PRM evaluation |
| VisCoR-55K | 55K | Generated | Contrastive VQA self-improvement |
| VisReason | 489K (165K Pro) | Four domains | Large-scale visual CoT |
| GThinker-11K | 7K + 4K RL | Iterative annotation | Cue-rethinking |
| ZoomBench | 845 | — | Fine-grained perception |
| MIRA | 546 | — | Visualization-essential reasoning |
| JourneyBench | — | — | Visual faithfulness evaluation |

---

#### 4.1.6 When to Use Quadrant I

**Appropriate**:
- Low-stakes applications (entertainment, casual QA)
- Closed-world tasks with clear rules
- Settings where tool use is impossible or prohibited
- Rapid prototyping before adding verification
- Resource-constrained deployment (low latency, no API costs)
- When human-readable explanations are sufficient

**Not Appropriate**:
- Safety-critical domains (medical, legal)
- Open-world reasoning requiring factual verification
- Tasks demanding step-level auditability
- When intermediate visual grounding must be externally verified
- High-stakes decisions requiring reproducibility

**Selection Guidance by Subcategory**:
- **Consistency & Self-Correction**: Choose when annotation budget is limited (R3V, Sherlock) or noisy CoT is a concern (RTWI, VC-STaR). R3V for self-training from QA only; Sherlock for trajectory-level correction with minimal data.
- **Structured Stages & Visual CoT**: Choose when interpretability and grounding are priorities. LLaVA-CoT for general reasoning; ChainV or PatchCue for efficiency; Zooming w/o Zooming when fine-grained perception is needed without tools.
- **PRM & Process Supervision**: Choose when step-level quality matters and inference cost is acceptable. VRPRM for data efficiency; VisualPRM for strongest BoN gains; Critic-V when natural-language feedback is preferred.
- **RLVR**: Choose when CoT annotations are scarce (Visionary-R1: CoT-free) or iterative improvement is desired (OpenVLThinker). R1-VL for dense process rewards; GThinker for cue-grounded reasoning; LLaVA-Critic-R1 for unified critic-policy with test-time scaling.
- **Faithfulness & Benchmarks**: Use Journey Before Destination for faithfulness evaluation; MIRA for visualization-essential tasks; VisReason for large-scale CoT training; R-CoT for geometric reasoning data.

**Comparison with Other Quadrants**: Quadrant I offers the lowest deployment complexity—no tool APIs, no execution sandbox, no structured trace parsers. Moving to Quadrant II (tools) adds external grounding but tool latency and failure modes. Quadrant III (structured traces) enables automatic verification but requires schema design. Quadrant IV (executable + tools) provides highest verifiability at highest cost. For many applications, Quadrant I with process supervision (PRM, step rewards) or structured outputs (LLaVA-CoT, Visionary-R1) offers a practical middle ground.

---
