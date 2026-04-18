# Paper Note: VisualPRM

## Basic Information

**Title:** VisualPRM: An Effective Process Reward Model for Multimodal Reasoning

**Authors:** Weiyun Wang, Zhangwei Gao, Lianjie Chen, Zhe Chen, Jinguo Zhu, Xiangyu Zhao, Yangzhou Liu, Yue Cao, Shenglong Ye, Xizhou Zhu, Lewei Lu, Haodong Duan, Yu Qiao, Jifeng Dai, Wenhai Wang

**Affiliations:** Shanghai AI Lab; OpenGVLab; InternVL Team

**Venue:** arXiv:2503.10291 (March 2025); OpenReview (submitted to ICML/NeurIPS 2025)

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2503.10291
- Project Blog: https://internvl.github.io/blog/2025-03-13-VisualPRM/
- Model: https://huggingface.co/OpenGVLab/VisualPRM-8B-v1_1

---

## Abstract Summary

VisualPRM introduces an 8B-parameter multimodal Process Reward Model (PRM) that evaluates the correctness of individual reasoning steps in multimodal Chain-of-Thought traces. It enables Best-of-N (BoN) inference-time scaling by scoring N candidate reasoning chains at the step level and selecting the highest-scoring chain. VisualPRM is trained on **VisualPRM400K**, a 400K-example multimodal process supervision dataset generated via Monte Carlo (MC) sampling to estimate step-level correctness. The work also introduces **VisualProcessBench**, a human-annotated benchmark with 2,866 examples and 26,950 step-level correctness labels for evaluating PRM error detection ability. VisualPRM achieves +5.9 points on InternVL2.5-78B across 7 multimodal reasoning benchmarks and consistently outperforms Outcome Reward Models and Self-Consistency in BoN evaluation.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT reasoning steps evaluated by the PRM)
- [ ] Structured Trace (CoT steps are free-form text, not programs or formal structures)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** I (Text-only CoT) — specifically the **process supervision** variant

**Justification:**

1. **PRM Evaluates Text CoT Steps Without Tools**: VisualPRM takes as input an image, a question, and a sequence of textual reasoning steps, and outputs binary correctness labels for each step. The PRM is a learned model (not an external tool or execution engine). It processes text and images via the same VLM architecture as the models it evaluates.

2. **No External Tool Calls at Any Stage**: Neither the reasoning model (which generates CoT) nor VisualPRM (which evaluates steps) calls external APIs, code interpreters, object detectors, or search engines. Both are end-to-end learned models.

3. **Best-of-N Is a Decoding Strategy, Not Tool Use**: BoN inference generates N candidate CoT chains from the base model and selects the highest-scoring chain according to VisualPRM. This is analogous to beam search with a learned scorer—entirely internal to the model ecosystem.

4. **Process Supervision Is the Defining Q1 Characteristic**: Among Q1 verification methods (self-consistency, reflection, process supervision), VisualPRM exemplifies *process supervision*—training/evaluating intermediate reasoning steps. This is the most technically sophisticated Q1 verification approach.

5. **Q1 vs. Q3 Distinction**: VisualPRM evaluates *textual* reasoning steps. If the underlying CoT were programmatic (Python code, formal logic), the PRM would be more naturally Q3. Since the CoT is free-form natural language, and VisualPRM scores these text steps via learned judgment (not execution), the system remains Q1.

6. **Contrast with Outcome Reward Models (ORM)**: VisualPRM explicitly outperforms ORMs and Self-Consistency—both Q1 verification approaches. The paper frames PRM as the superior Q1 verification method, positioning VisualPRM within the Q1 design space.

---

## Key Contributions

1. **First Effective Multimodal Process Reward Model at Scale**: VisualPRM extends the PRM paradigm (originally developed for text-only math reasoning, e.g., Math-Shepherd, OmegaPRM) to multimodal reasoning, handling images + text jointly. The 8B model achieves step-level error detection superior to ORM and Self-Consistency (SC) baselines across four different MLLM families and four different model scales, demonstrating generalizability. The key technical innovations are: (a) formulating process supervision as a multi-turn chat task where the PRM sequentially predicts correctness for each step; (b) supervising *all* steps rather than stopping at the first error; (c) using binary correctness labels (not continuous scores).

2. **VisualPRM400K: Automated Multimodal Process Supervision Dataset**: 400K multimodal process supervision training examples generated via a three-stage automated pipeline: (a) collect candidate solutions to math/science VQA problems from MLLM sampling; (b) estimate step-level correctness using Monte Carlo sampling (for each prefix ending at step k, sample 16 completions and estimate P(correct answer | prefix) via majority voting); (c) label step k as correct if P > 0.7, incorrect if P < 0.3, and discard ambiguous examples. This automated pipeline avoids expensive human annotation while producing step-level labels more accurate than simple outcome labels.

3. **VisualProcessBench: First Human-Annotated Step-Level Multimodal Reasoning Benchmark**: A diagnostic benchmark with 2,866 problems and 26,950 step-wise human-annotated correctness labels (average ~9 steps per problem). Covers 5 domains: math, science, chart/diagram understanding, OCR-heavy reasoning, and spatial reasoning. Designed to measure PRM abilities to detect erroneous steps in realistic multimodal CoT traces. VisualPRM achieves strong performance on VisualProcessBench, validating the automated training pipeline.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Medium-High (strongest among Q1 approaches)

VisualPRM provides *step-level binary correctness labels* for each reasoning step—this is the strongest verification signal available in Q1. Unlike answer-level verification (correct/wrong for final answer), step-level scoring identifies *which step* in the reasoning chain is erroneous. This enables targeted error localization (e.g., "Step 3 is incorrect") that is qualitatively more informative than "the final answer is wrong." However, the PRM's step labels are soft judgments by a learned model—they can be wrong (false positives/negatives), and they do not provide explicit visual grounding (bounding boxes, evidence pointers).

### Checkability
**Assessment:** Medium-High (best in Q1 class)

Step-level PRM scores are automatically generated for any candidate CoT. This enables systematic quality assessment of reasoning chains without human review. VisualProcessBench with 26,950 human-annotated step labels provides ground truth for evaluating PRM checkability. The automated MC-sampling pipeline for VisualPRM400K demonstrates that step-level labels can be generated at scale. Limitations: (a) PRM accuracy is not 100% (false positive/negative rates reported in VisualProcessBench evaluation); (b) PRM scores individual steps but not their *coherence* across steps.

### Replayability
**Assessment:** Medium-High (strongest in Q1 class)

BoN + VisualPRM enables a structured selection process: generate N chains → score each step → select chain with highest total PRM score. This process is deterministic (given fixed N, model weights, and scoring function) and produces a complete audit trail: N candidate chains + step-level scores. The selected chain's quality is attributable to the PRM's step-level evaluation. This is more replayable than self-consistency (majority voting obscures reasoning paths) or inference-time correction (non-deterministic).

### Faithfulness Risk
**Assessment:** Medium (reduced compared to other Q1 approaches)

VisualPRM directly addresses the Q1 faithfulness problem—plausible-but-incorrect reasoning—by scoring each step for correctness. A reasoning chain that arrives at the correct answer via incorrect steps will receive low PRM scores at the erroneous steps, and BoN selection will prefer chains with consistently high step scores (i.e., faithful step-by-step reasoning). This is the mechanism by which VisualPRM reduces faithfulness risk. However, the PRM itself may assign high scores to plausible-but-wrong steps (PRM hallucination), so faithfulness risk is reduced but not eliminated.

### Robustness
**Assessment:** Medium-High

Tested across four MLLM families (MiniCPM-V2.6, Qwen2.5-VL, InternVL2.5-8B, InternVL2.5-78B) and four model scales—demonstrating robustness to base model choice. Outperforms ORM and SC across all configurations. The MC-sampling label generation pipeline is robust to individual sampling noise via majority voting over 16 samples. Primary robustness concern: PRM quality may degrade for reasoning domains underrepresented in VisualPRM400K (e.g., medical imaging, code generation).

### Cost/Latency
**Assessment:** High (inference)

**Training**: VisualPRM400K construction requires MC sampling (16 completions per step prefix for label estimation)—computationally expensive but one-time. PRM training itself is standard SFT on 400K examples.

**Inference (BoN)**: N-sample generation (N typically 8-64) + N × T PRM scoring calls (where T is steps per chain). Total cost = N × (generation cost + PRM scoring cost). For N=16 and T=10 steps, inference is ~160× more expensive than greedy decoding. This is the dominant cost concern for VisualPRM deployment and limits its use to high-stakes reasoning scenarios.

### Security
**Assessment:** Low-Medium Risk

No external tool calls. PRM scores could potentially be gamed by adversarial CoT formatting (e.g., short steps that all score "correct" without meaningful reasoning). The binary correctness label training does not penalize superficial step decompositions.

---

## Failure Modes

1. **PRM Hallucination (False Positive Steps)**: VisualPRM may assign high correctness scores to reasoning steps that are plausible but wrong—the same "plausible-but-unfaithful" failure that afflicts the generator also affects the verifier. If the PRM and the generator share architectural biases (same type of VLM), they may share the same blind spots, and BoN selection will choose a chain that is consistently wrong in the same way.

2. **High BoN Inference Cost Limits Practical Deployment**: N-sample generation + PRM scoring is 10-100× more expensive than greedy decoding. For real-time applications (autonomous systems, interactive QA), this cost is prohibitive. VisualPRM provides accuracy improvements primarily in evaluation settings, not in latency-constrained deployment.

3. **Domain Coverage Gaps in VisualPRM400K**: The 400K training examples are sourced from mathematical and scientific reasoning domains. PRM quality on other domains (medical imaging, fine-grained visual recognition, spatial navigation, video reasoning) is unknown and likely lower. The paper does not evaluate domain transfer.

4. **Step Granularity Mismatch**: VisualPRM scores discrete reasoning steps. For free-form CoT where step boundaries are ambiguous or ill-defined, step-level scoring may be unreliable. The paper segments CoT by explicit step markers, but not all CoT reasoning naturally decomposes into cleanly separable steps.

5. **MC Label Noise Propagation**: The automated MC-sampling pipeline introduces label noise—P(correct answer | prefix) is estimated from only 16 samples, which may be insufficient for high-difficulty problems. Label noise in VisualPRM400K training propagates to PRM errors at inference, limiting step-level accuracy on hard problems.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric via BoN evaluation on 7 benchmarks)
- [x] Step Correctness (VisualProcessBench: 26,950 human-annotated step labels)
- [ ] Evidence Attribution
- [x] Trace Replayability (BoN selection produces auditable step scores)
- [x] Robustness (4 MLLM families × 4 scales; vs. ORM and SC baselines)
- [x] Cost/Latency (BoN cost vs. performance trade-off)
- [x] Other: PRM error detection rate (recall/precision on erroneous steps in VisualProcessBench)

### Benchmarks
- **7 Multimodal Reasoning Benchmarks** (BoN evaluation): MathVista, MathVerse, OlympiadBench, DynaMath, GeoQA, ChartQA, and one additional (specific full list from paper)
- **VisualProcessBench** (PRM diagnostic): 2,866 problems, 26,950 step-level labels, 5 domains

### Key Results
- InternVL2.5-78B + VisualPRM (BoN-16): +5.9 pts across 7 benchmarks
- InternVL2.5-8B + VisualPRM: +8.4 pts; QwenVL2.5-7B: +3.7 pts; MiniCPM-V2.6: +8.0 pts
- VisualPRM > ORM > Self-Consistency in all BoN comparisons
- VisualProcessBench: VisualPRM achieves higher error step detection than ORM and SC baselines
- Key design ablation: supervising all steps (vs. stopping at first error) is crucial; binary label (vs. continuous score) performs comparably with lower complexity

---

## Training & Alignment

### Method
- [x] SFT with Rationale (VisualPRM trained on VisualPRM400K with step-level binary labels)
- [x] Process Supervision (core contribution: step-level process supervision for multimodal reasoning)
- [x] PRM (Process Reward Model — central contribution)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other

### Data Collection
**VisualPRM400K Construction Pipeline (3 stages)**:

1. **Candidate Solution Collection**: For each problem in math/science VQA training sets (sources: MathVista train, GeoQA train, ScienceQA train, OlympiadBench, others), sample 32 candidate CoT solutions from InternVL2.5-7B/8B using temperature sampling. Each solution consists of K steps (step boundaries identified by step markers or heuristic segmentation) plus final answer.

2. **MC Step-Level Label Estimation**: For each solution prefix ending at step k (steps 1 to k), sample 16 completions and estimate P(reach correct answer | steps 1..k) via majority voting over final answers. The step k correctness estimate is this probability.

3. **Label Assignment and Filtering**: 
   - Label step k as *correct* if P > 0.7
   - Label step k as *incorrect* if P < 0.3
   - Discard examples with ambiguous P (0.3 ≤ P ≤ 0.7)
   - Result: ~400K (problem, solution, step-level binary labels) tuples after filtering

**VisualPRM Training Format**: Multi-turn chat where each turn presents the image, question, and solution prefix through step k, and the model predicts [correct]/[incorrect] at each turn. Model is trained with standard cross-entropy loss on step correctness labels.

---

## Connections to Other Work

### Builds On
- Math-Shepherd (Wang et al., 2024): Process reward model for math reasoning (text-only)
- OmegaPRM (Liao et al., 2024): MC-sampling for process label generation
- Let's Verify Step by Step (Lightman et al., 2023): Human-annotated PRM for math reasoning
- InternVL2.5 (Chen et al., 2024): Base MLLM family used for evaluation

### Related To
- R3V (Cheng et al., NAACL 2025): Answer-correctness-based verification (less granular than step-level PRM)
- CURE (2024): Consistency-based verification (Q1, different verification signal)
- LLaVA-CoT (Xu et al., ICCV 2025): SWIRES beam search (different test-time scaling, no step-level scoring)
- Outcome Reward Models (ORMs): VisualPRM directly outperforms ORMs in experiments

### Influenced
- VisualPRM establishes the multimodal PRM paradigm; follow-up work on more fine-grained step supervision, visual grounding in PRMs, and RL training with process rewards is anticipated
- VRPRM (2024): Process reward model with CoT for visual reasoning; parallel concurrent work

---

## Quotes & Key Insights

> "Our model improves the reasoning performance of three types of MLLMs and four different model scales. Even when applied to the highly capable InternVL2.5-78B, it achieves a 5.9-point improvement across seven multimodal reasoning benchmarks."

> "Experimental results show that our model exhibits superior performance compared to Outcome Reward Models and Self-Consistency during BoN evaluation."

> "We propose VisualProcessBench, a benchmark with human-annotated step-wise correctness labels, to measure the abilities of PRMs to detect erroneous steps in multimodal reasoning tasks."

**Key Insight 1: Process Supervision Is the Strongest Q1 Verification Signal**
By directly scoring reasoning steps rather than only the final answer (ORM) or aggregate answer consistency (SC), VisualPRM identifies *where* reasoning goes wrong. The empirical superiority over ORM and SC demonstrates that step-level supervision is a strictly better Q1 verification approach—the best feasible option before moving to tool-augmented verification (Q2/Q4).

**Key Insight 2: Scale and Domain Generalization of PRM**
VisualPRM trained on math/science data generalizes across 4 MLLM families and 4 scales, suggesting that step-level reasoning correctness has universal properties across model architectures. This generalizability is an important positive result for the multimodal PRM research direction.

**Key Insight 3: Human Annotation Remains Essential for PRM Evaluation**
Despite the automated VisualPRM400K training pipeline, VisualProcessBench requires human annotation (26,950 step labels) to reliably evaluate PRM quality. Automated MC estimates are sufficient for training but not for evaluation—MC noise makes it unreliable as a ground truth. This points to a fundamental tension in process supervision: automated training is scalable, but reliable evaluation requires expensive human effort.

**Key Insight 4: PRM Enables Step-Level Interpretability**
For each BoN-selected reasoning chain, VisualPRM provides a step-level score record: [1.0, 1.0, 0.2, 0.9, 1.0] for a 5-step chain indicating Step 3 is suspicious. This score record is an interpretable artifact that lets users understand *why* the selected chain was preferred over alternatives. This is qualitatively different from self-consistency selection (which only reveals answer plurality, not step quality).

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant — Quadrant I: Process supervision, the most advanced Q1 verification)
- [x] Section 5 (Learning & Alignment — MC-sampling for automated process supervision data; PRM training)
- [x] Section 6 (Evaluation & Benchmarks — VisualProcessBench; BoN scaling curves)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — PRM hallucination, inference cost, domain generalization limits)

### Narrative Role
VisualPRM represents the **summit of Q1 verification capability**—process supervision at step level without tools. In the survey, it marks the current frontier of what text-only CoT verification can achieve. The paper simultaneously demonstrates two things that frame the survey's central tension: (1) step-level PRM achieves impressive accuracy gains (+5.9 pts on 78B model), showing Q1 is far from saturated; (2) the inference cost (BoN N=16, step scoring) and remaining PRM hallucination risk show that Q1 cannot fully solve the faithfulness problem without external verification. This positions VisualPRM as the strongest argument for "invest more in Q1" while its failure modes provide the strongest argument for "Q1 has inherent limits that Q2/Q4 must address."

### Comparison Points
**Excels at**: Step-level error detection, BoN inference scaling, generalization across MLLM families, strong empirical gains, interpretable step scores
**Fails at**: High inference cost (BoN × step scoring), PRM hallucination risk on hard problems, domain coverage gaps, MC label noise, inference latency for real-time use

---

## BibTeX

```bibtex
@article{wang2025visualprm,
  title={{VisualPRM}: An Effective Process Reward Model for Multimodal Reasoning},
  author={Wang, Weiyun and Gao, Zhangwei and Chen, Lianjie and Chen, Zhe and Zhu, Jinguo and Zhao, Xiangyu and Liu, Yangzhou and Cao, Yue and Ye, Shenglong and Zhu, Xizhou and Lu, Lewei and Duan, Haodong and Qiao, Yu and Dai, Jifeng and Wang, Wenhai},
  journal={arXiv preprint arXiv:2503.10291},
  year={2025},
  url={https://arxiv.org/abs/2503.10291}
}
```

**Status:** ✅ Complete — Quadrant I Paper (Multimodal Process Reward Model — Step-Level Verification)

**Q1 Justification Summary:** VisualPRM evaluates free-form textual CoT steps via a learned VLM-based scorer with no external tool calls; BoN is a decoding strategy internal to the model ecosystem; step-level scoring is the most sophisticated form of Q1 process supervision; no code execution, no grounding APIs, no external verifiers beyond the PRM itself.
