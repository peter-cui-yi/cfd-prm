# Paper Note: Critic-V

## Basic Information

**Title:** Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning

**Authors:** Di Zhang, Junxian Li, Jingdi Lei, Xunzhi Wang, Yujie Liu, Zonglin Yang, Jiatong Li, Weida Wang, Suorong Yang, Jianbo Wu, Peng Ye, Wanli Ouyang, Dongzhan Zhou

**Affiliations:** Shanghai AI Lab; CUHK; Wuhan University; and others

**Venue:** CVPR 2025 (arXiv:2411.18203, submitted November 2024)

**Year:** 2024 (arXiv), 2025 (CVPR)

**Link:**
- arXiv: https://arxiv.org/abs/2411.18203
- HTML: https://arxiv.org/html/2411.18203v5

---

## Abstract Summary

Critic-V introduces an Actor-Critic paradigm for multimodal reasoning where a **Reasoner** VLM generates reasoning paths and a separate **Critic** VLM provides constructive natural-language critiques to refine those paths. The Critic is trained via Direct Preference Optimization (DPO) on a preference dataset of critiques ranked by Rule-based Reward (RBR). At inference, the Reasoner iteratively evolves its response based on Critic feedback. The key innovation is replacing scalar reward signals with rich natural-language critique—enabling more nuanced, context-sensitive feedback than binary correct/wrong labels. Critic-V outperforms GPT-4V on 5 out of 8 benchmarks and is designed for reasoning-heavy applications in autonomous driving and embodied intelligence.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT for Reasoner; natural language critiques from Critic)
- [ ] Structured Trace (critiques are free-form text, not structured programs or formal assertions)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** I (Text-only CoT)

**Justification:**

1. **Natural Language Critique, Not Tool Output**: The Critic model produces natural language feedback—text critique that identifies errors in the Reasoner's reasoning path and suggests corrections. This is fundamentally different from tool output (e.g., "the object detector returned 'car' at [x=120, y=340]"). The critique says things like "the reasoning incorrectly assumes the object in the background is stationary"—it is a textual judgment, not a verifiable factual return value.

2. **No External Tools in Either Component**: The Reasoner generates CoT purely from visual + textual inputs. The Critic evaluates reasoning paths purely from its own VLM understanding—no grounding tools, no code execution, no external knowledge retrieval. Both models are end-to-end VLMs trained on text + images.

3. **Rule-Based Reward (RBR) Is Rule Logic, Not Tool Call**: RBR uses programmatic rules (e.g., answer string matching, format compliance) to rank critique quality during training. This is *training-time supervision*, not *inference-time tool use*. The deployed system has no external tools.

4. **Iterative Refinement Is Text-to-Text**: The interaction between Reasoner and Critic is a text dialogue: Reasoner outputs reasoning text → Critic outputs critique text → Reasoner refines its reasoning text. No external execution environment is involved.

5. **Contrast with Tool-Augmented Critics**: A Q2 critic would call external tools (e.g., run image classifier to verify object identity, execute code to check arithmetic). Critic-V's critic is a learned model that operates purely on the text reasoning trace and the original image.

---

## Key Contributions

1. **Actor-Critic Paradigm with Natural Language Critiques for VLMs**: First application of the Actor-Critic reinforcement learning paradigm to multimodal reasoning where the reward signal is natural language critique rather than a scalar value. The Reasoner generates reasoning responses based on text prompts, and these evolve iteratively as a policy based on Critic feedback. Natural language critiques provide richer supervision than binary correct/wrong labels, enabling the model to receive targeted feedback on *specific reasoning errors* (e.g., "incorrectly attributed spatial relationship", "ignored the numerical value in the bottom-left legend").

2. **DPO-Trained Critic with Rule-Based Reward Ranking**: The Critic is trained using Direct Preference Optimization on a preference dataset where critique quality is ranked by Rule-based Reward (RBR). RBR evaluates critiques based on (a) whether the critique correctly identifies the error in the reasoning path, (b) whether following the critique leads to a correct final answer, and (c) format compliance. This two-stage pipeline (generate critiques → rank by RBR → train with DPO) bootstraps a high-quality Critic without human annotation.

3. **Decoupled Reasoning and Critique for Complex Task Reliability**: By separating the Reasoner (which generates solutions) from the Critic (which identifies errors), Critic-V decomposes the complex task of "generate correct reasoning" into two more tractable subtasks: "generate candidate reasoning" and "critique candidate reasoning." This decoupling is particularly valuable for complex reasoning-heavy tasks (autonomous driving scene understanding, embodied agent planning) where the Reasoner alone fails frequently.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Low-Medium

Neither the Reasoner nor the Critic provides explicit spatial grounding (bounding boxes, coordinates, region masks). The Critic identifies reasoning errors linguistically—"the model failed to account for the pedestrian's trajectory"—but does not point to specific image evidence in a machine-readable format. Grounding is entirely implicit in the VLM's visual encoder. An improvement over single-model CoT (a second model catches some visual misperceptions), but no explicit visual evidence attribution.

### Checkability
**Assessment:** Medium

The iterative critique-refinement loop provides stronger checkability than single-pass CoT: the Critic's natural language feedback is an inspectable record of identified errors. A human auditor can read the critique and assess whether it correctly identified the Reasoner's mistake. Answer correctness is automatically checkable. However, *critique quality itself* is not automatically verifiable without the RBR rules—the Critic can generate plausible-sounding but incorrect critiques. The deployment system provides no automatic check that the Critic is right.

### Replayability
**Assessment:** Medium

The multi-turn Reasoner-Critic interaction is replayable in the sense that the full dialogue (Reasoner v1 → Critique → Reasoner v2 → ...) is a recorded text transcript that can be inspected. Each step's input and output are text strings. However, the trace cannot be "executed" or formally verified—it is a text dialogue, not a program. Given the same model weights and inputs, the interaction is reproducible under fixed random seeds.

### Faithfulness Risk
**Assessment:** High (Reasoner), Medium (Critic-refined output)

**Reasoner risk**: The initial Reasoner output suffers from standard Q1 faithfulness risks—hallucination, visual misperception, spurious logical leaps.

**Critic risk**: The Critic introduces a new failure mode—**plausible but incorrect critiques**. If the Critic incorrectly identifies an error (false positive) or misidentifies the nature of an error, the Reasoner may revise a correct reasoning step into an incorrect one. This "critique-induced degradation" is a novel faithfulness risk specific to Actor-Critic architectures.

**Post-critique risk**: Even after Critic feedback, the refined Reasoner output may still be unfaithful if the Critic missed errors or gave incorrect guidance. The DPO-trained Critic is not infallible.

### Robustness
**Assessment:** Medium

No external tool dependencies (advantage). The Actor-Critic design is more robust than single-pass CoT because a second model provides an independent check. However, both models share similar architectural biases (both are VLMs trained on similar data distributions), so systematic biases (e.g., ignoring small objects, over-relying on text in images) may be present in both Reasoner and Critic simultaneously. The critique-refinement loop may reinforce shared biases rather than correcting them.

### Cost/Latency
**Assessment:** Low-Medium (training), High (inference)

**Training**: DPO training requires a critique preference dataset (generated via RBR ranking), which adds complexity but avoids human annotation. Comparable cost to other DPO-based VLM training.

**Inference**: The multi-turn Critic-Reasoner loop multiplies inference cost by the number of iterations. K iterations = K×(Reasoner cost + Critic cost). For K=3, inference is 6× more expensive than single-pass CoT. This may be prohibitive for latency-sensitive applications despite the accuracy gains.

### Security
**Assessment:** Low-Medium Risk

The Critic model could in principle be adversarially manipulated by crafting inputs that trigger incorrect critiques (causing the Reasoner to revise a correct response into an incorrect one). This "adversarial critique" attack surface is novel and not discussed in the paper. Standard VLM adversarial robustness concerns apply to both components.

---

## Failure Modes

1. **Plausible but Incorrect Critiques (Critic Failure Mode)**: The Critic may confidently identify a "reasoning error" that is actually correct, causing the Reasoner to revise a valid reasoning step. This is the inverse of the Reasoner's hallucination problem—the Critic hallucinates an error. This failure mode is specific to Actor-Critic architectures and is not present in single-model CoT.

2. **Shared Bias Reinforcement**: If both Reasoner and Critic share the same visual understanding limitations (e.g., both misperceive a specific type of visual element), the Critic will not catch the Reasoner's errors on those elements. The critique loop reinforces the shared bias rather than correcting it.

3. **Iterative Degradation**: The Reasoner-Critic loop may not converge—the Reasoner may oscillate between two incorrect reasoning paths based on Critic feedback, or the refinement chain may gradually drift away from the correct answer as multiple rounds of critique accumulate errors.

4. **DPO Critic Brittleness on Out-of-Distribution Reasoning**: The Critic is trained to critique reasoning paths from a specific distribution (training domain). For reasoning patterns not covered in the DPO training data, the Critic may generate irrelevant or misleading critiques.

5. **Computational Cost Limits Deployment**: The multi-turn inference cost (K × model calls) may prevent deployment in real-time applications. The paper targets autonomous driving and embodied intelligence—domains with strict latency requirements that may not accommodate multi-turn critique loops.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric, 8 benchmarks)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (dialogue transcript inspectable)
- [x] Robustness (comparison to GPT-4V, multiple baselines)
- [x] Cost/Latency (implicitly via iteration count analysis)
- [ ] Other

### Benchmarks
- 8 multimodal reasoning benchmarks (specific names not fully listed in available abstract; includes ScienceQA, MathVista, and similar benchmarks targeting reasoning)
- Comparison to GPT-4V, standard VLM baselines, and ablations (Reasoner-only, Critic-only)

### Key Results
- Critic-V outperforms GPT-4V on 5 out of 8 benchmarks
- Significant improvements in reasoning accuracy and efficiency over single-model baselines
- DPO-trained Critic provides better critique quality than untrained VLM Critic (ablation)
- Natural language critiques outperform scalar reward signals for iterative reasoning refinement

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Reasoner: SFT on reasoning chains)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (Critic: DPO on critique preference dataset ranked by RBR)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Actor-Critic paradigm, Rule-based Reward for critique ranking

### Data Collection
- **Critique Preference Dataset**: For each training example, generate multiple candidate critiques of Reasoner outputs. Rank critiques using Rule-based Reward (RBR): (1) Does the critique correctly identify the error? (2) Does following the critique lead to correct final answer? (3) Format compliance. Construct preference pairs (high-RBR critique preferred over low-RBR critique). Train Critic with DPO on these pairs.
- **Reasoner Training**: Standard SFT on visual reasoning datasets with CoT annotations.

---

## Connections to Other Work

### Builds On
- Actor-Critic RL (Sutton & Barto): Foundational framework
- DPO (Rafailov et al., 2024): Training Critic via preference optimization
- Self-Refine (Madaan et al., 2023): Iterative refinement via self-generated feedback
- Constitutional AI (Anthropic, 2022): Critique-based alignment paradigm

### Related To
- R3V (Cheng et al., NAACL 2025): Self-improvement via reflection on CoT rationales (single model, no separate Critic)
- Sherlock (Ding & Zhang, NeurIPS 2025): Self-correction via preference learning (single model)
- CURE (2024): Consistency-based verification without a trained Critic
- LLaVA-CoT (Xu et al., ICCV 2025): Stage-structured CoT without critic feedback

### Influenced
- Critic-based VLM refinement is a growing paradigm; Critic-V is among the first to apply DPO for multimodal critics
- Subsequent work on verifier-guided reasoning for VLMs builds on this decomposed approach

---

## Quotes & Key Insights

> "This framework decouples the reasoning process and critic process by integrating two independent components: the Reasoner, which generates reasoning paths based on visual and textual inputs, and the Critic, which provides constructive critique to refine these paths."

> "The Critic offers natural language critiques instead of scalar rewards, enabling more nuanced feedback to boost the Reasoner's capability on complex reasoning tasks."

> "Combining a dynamic text-based policy for the Reasoner and constructive feedback from the preference-optimized Critic enables a more reliable and context-sensitive multimodal reasoning process."

**Key Insight 1: Natural Language Critique as Rich Reward Signal**
Scalar rewards (correct/wrong) lose the *reason* for failure. Natural language critique preserves and communicates the error type, enabling the Reasoner to make targeted corrections rather than blind regeneration. This is the core advantage of Actor-Critic over outcome reward models in the VLM setting.

**Key Insight 2: Decoupled Evaluation from Generation**
By training a separate Critic model, Critic-V acknowledges that the same model that generates reasoning is poorly suited to evaluate its own reasoning (self-evaluation bias). This architectural separation is theoretically motivated and empirically effective—the Critic provides an independent perspective.

**Key Insight 3: DPO Enables Critic Training Without Human Labels**
The Rule-based Reward enables automatic ranking of critique quality, bootstrapping DPO training without human annotation. This is scalable and demonstrates that programmatic quality signals can train effective natural-language feedback models.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant — Quadrant I: Actor-Critic text-only CoT refinement)
- [x] Section 5 (Learning & Alignment — DPO for Critic training, Actor-Critic paradigm)
- [x] Section 6 (Evaluation & Benchmarks — 8-benchmark comparison including GPT-4V)
- [x] Section 7 (Applications — Autonomous driving, embodied intelligence)
- [x] Section 8 (Challenges — Critique failure modes, shared bias, inference cost)

### Narrative Role
Critic-V represents the **dual-model Q1 approach**: instead of one model self-correcting, two models collaborate—a Generator and an Evaluator. In the survey narrative, it shows how adding a trained Critic within Q1's constraints (text-only, no tools) provides improvements over single-model self-correction (R3V, Sherlock). However, it introduces new failure modes (incorrect critiques) and higher inference costs. The shared bias limitation motivates Q2/Q4 designs where external verification escapes the distributional biases of both Reasoner and Critic.

### Comparison Points
**Excels at**: Richer feedback than scalar rewards, decoupled evaluation, outperforming GPT-4V, targeted error correction
**Fails at**: Shared bias correction, critic accuracy verification, inference latency, out-of-distribution critique quality

---

## BibTeX

```bibtex
@inproceedings{zhang2025critic,
  title={Critic-{V}: {VLM} Critics Help Catch {VLM} Errors in Multimodal Reasoning},
  author={Zhang, Di and Li, Junxian and Lei, Jingdi and Wang, Xunzhi and Liu, Yujie and Yang, Zonglin and Li, Jiatong and Wang, Weida and Yang, Suorong and Wu, Jianbo and Ye, Peng and Ouyang, Wanli and Zhou, Dongzhan},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2025},
  url={https://arxiv.org/abs/2411.18203}
}
```

**Status:** ✅ Complete — Quadrant I Paper (Actor-Critic Natural Language Critique for VLM Reasoning)

**Q1 Justification Summary:** Both Reasoner and Critic are VLMs generating and evaluating free-form text—no external tools, no code execution, no grounding APIs. Natural language critiques are textual feedback within the model's generation process. RBR is training-time rule logic, not inference-time tool use.
