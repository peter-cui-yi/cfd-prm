# Paper Note: MIRA

## Basic Information

**Title:** When Visualizing is the First Step to Reasoning: MIRA, a Benchmark for Visual Chain-of-Thought

**Authors:** Yiyang Zhou, Haoqin Tu, Zijun Wang, Zeyu Wang, Niklas Muennighoff, Fan Nie, Yejin Choi, James Zou, Chaorui Deng, Shen Yan, Haoqi Fan, Cihang Xie, Huaxiu Yao, Qinghao Ye

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2511.02779
- Date: November 2025

---

## Abstract Summary

MIRA is a benchmark designed to evaluate models in scenarios where generating intermediate visual images (sketches, structural diagrams, path drawings) is essential for successful reasoning—mirroring human "drawing to think." It includes 546 multimodal problems annotated with intermediate visual images and final answers. The benchmark evaluates models at three levels: direct input (image + question only), text-only CoT (image + thinking prompts), and Visual-CoT (annotated image clues + textual thinking prompts). Experiments show that existing MLLMs perform poorly with text-only prompts but improve by an average of 33.7% when intermediate visual cues are provided, underscoring the critical role of imagined visual information in reasoning.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (text CoT; intermediate visual images are *annotated* ground truth, not model-generated—the benchmark evaluates whether models *need* such visuals)
- [ ] Structured Trace (MIRA is a benchmark, not a method; it probes model capabilities)

### Verification Channel
- [x] No Tools / No Execution (benchmark evaluation; models are not required to use tools)
- [ ] Tool-Augmented
- [ ] Execution Feedback

### 2×2 Matrix Placement
**Quadrant:** I (Benchmark for Visual CoT—evaluates Q1-style reasoning)

**Justification:**

1. **Benchmark, Not Method**: MIRA is an evaluation benchmark. It does not prescribe a specific reasoning architecture. The three evaluation levels (direct, text-only CoT, Visual-CoT) probe how models perform with and without intermediate visual cues.

2. **No Tool Requirement**: Models are evaluated on their ability to reason about problems that *benefit from* intermediate visualizations. The benchmark does not require models to call image generation tools, grounding APIs, or execution environments. The "Visual-CoT" setting provides *annotated* intermediate images as input—it tests whether such cues help, not whether models can generate them.

3. **Q1 Focus**: MIRA evaluates reasoning quality—answer correctness—under different input conditions. The key finding is that text-only reasoning is insufficient for tasks requiring visual imagination; providing intermediate visual clues (as additional input) improves performance. This supports the Q1 design space: better visual grounding (e.g., via intermediate images) can improve reasoning without tools.

4. **Probing Upper Bound**: Pass@k and majority voting are used to probe model capacity. The benchmark reveals a gap between text-only and Visual-CoT performance—motivating future work on either generating intermediate visuals (Q2/Q4) or improving text-based reasoning to compensate (Q1).

---

## Key Contributions

1. **MIRA: 546-Problem Benchmark for Visual CoT**: The first benchmark designed for tasks where generating intermediate visual images (sketches, diagrams, path drawings) is essential for reasoning. Tasks involve complex structures, spatial relationships, or reasoning steps difficult to express through language alone, mirroring human "drawing to think."

2. **Unified Three-Level Evaluation Protocol**: Direct input (image + question only), text-only CoT (image + thinking prompts), and Visual-CoT (annotated image clues + textual thinking prompts). Enables systematic comparison of model performance across input conditions.

3. **Empirical Finding: 33.7% Gain from Visual Cues**: Existing MLLMs (including strongest private and open-weight models) perform poorly with text-only prompts but improve consistently when intermediate visual cues are provided. Pass@k and textual prompt alignment yield only limited improvements compared to Visual-CoT, underscoring the critical role of imagined visual information.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** High (in Visual-CoT setting)

When intermediate visual clues are provided, the benchmark explicitly grounds reasoning in visual evidence. The annotated images serve as ground-truth intermediate states. In text-only and direct settings, grounding is implicit and weaker.

### Checkability
**Assessment:** High (benchmark design)

Answer correctness is automatically checkable. The benchmark provides ground-truth intermediate images for 546 problems, enabling evaluation of whether model reasoning aligns with expected visual structure.

### Replayability
**Assessment:** High

Benchmark is fixed; evaluation is fully reproducible. Models can be re-run on the same 546 problems under each evaluation level.

### Faithfulness Risk
**Assessment:** Medium (evaluation concern)

The benchmark reveals that models struggle with text-only reasoning on visual-imagination tasks—suggesting high faithfulness risk when models rely on text alone. The 33.7% gain from Visual-CoT indicates that models benefit from explicit visual grounding.

### Robustness
**Assessment:** Medium (benchmark scope)

546 problems may not cover all visual reasoning scenarios. Models may overfit to MIRA's task distribution. The benchmark is designed for "visualization-essential" tasks—generalization to other reasoning types is unclear.

### Cost/Latency
**Assessment:** Low (benchmark evaluation)

Standard VQA-style evaluation. Pass@k and majority voting increase computational cost for upper-bound probing.

### Security
**Assessment:** Low Risk

Benchmark evaluation; no external tool calls or sensitive data.

---

## Failure Modes

1. **Benchmark Scale**: 546 problems may be insufficient for robust statistical conclusions or for training models. Larger-scale benchmarks may be needed for future work.

2. **Annotation Quality**: Human-annotated intermediate images and answers may contain errors or inconsistencies.

3. **Task Coverage**: MIRA focuses on "visualization-essential" tasks. Models may perform well on MIRA but fail on other visual reasoning tasks (e.g., fine-grained recognition, OCR) that do not require intermediate drawings.

4. **Evaluation Gap**: The gap between text-only and Visual-CoT performance does not prescribe a solution—models could improve by either (a) generating intermediate images (requiring tools), or (b) improving text-based reasoning to compensate (Q1). The benchmark motivates but does not resolve this design choice.

5. **Model Bias**: Strongest private models may have different training data distributions; MIRA's task design may favor or disfavor certain model families.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Pass@k, majority voting (upper-bound probing)
- [ ] Robustness
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- MIRA (546 problems, 3 evaluation levels)
- Comparison across strongest private and open-weight MLLMs

### Key Results
- 33.7% average relative gain when intermediate visual cues are provided
- Text-only CoT and textual prompt alignment yield limited improvements
- Critical role of imagined visual information in enabling successful reasoning on MIRA

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Benchmark (no training method)

### Data Collection
- 546 multimodal problems with human-annotated intermediate visual images and final answers
- Tasks designed for complex structures, spatial relationships, reasoning steps difficult to express in language

---

## Connections to Other Work

### Builds On
- Visual CoT benchmarks (MathVista, ScienceQA, etc.)
- "Drawing to think" cognitive science
- Chain-of-Thought evaluation

### Related To
- MIRA probes the need for intermediate visual generation
- StruVis (structured vision for T2I), Graph-of-Mark (scene graph prompting)
- LLaVA-CoT, VisReason (visual CoT training)

### Influenced
- Future benchmarks for visual reasoning requiring intermediate visualization
- Models that generate intermediate images (Q2/Q4) or improve text-only reasoning (Q1)

---

## Quotes & Key Insights

> "Tasks in MIRA require models to generate and utilize intermediate images - such as sketches, structural diagrams, or path drawings - to guide their reasoning process."

> "When intermediate visual cues are provided, model performance improves consistently, yielding an average relative gain of 33.7% across all models and tasks."

**Key Insight:** MIRA establishes that **visualization is often the first step to reasoning** for complex spatial and structural tasks. The 33.7% gap between text-only and Visual-CoT performance motivates either tool-augmented intermediate image generation (Q2/Q4) or improved Q1 training to bridge the gap.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant — Quadrant I: Benchmark revealing limitations)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks — MIRA benchmark)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — need for intermediate visual generation)

### Narrative Role
MIRA serves as a **diagnostic benchmark** that exposes the limits of text-only visual CoT. It provides empirical evidence that certain reasoning tasks require intermediate visual representations—supporting the survey's argument that Q1 has inherent limits and that Q2/Q4 (tool-augmented, structured) approaches may be necessary for visualization-essential tasks.

### Comparison Points
**Excels at:** Benchmark design, three-level evaluation, clear empirical finding (33.7% gain)
**Fails at:** Scale (546 problems), prescribing solutions (benchmark only motivates)

---

## Notes

MIRA is a benchmark paper; its primary contribution is evaluation infrastructure and empirical findings. The 33.7% gain from Visual-CoT is a strong signal for the importance of intermediate visual representations in reasoning.

---

## BibTeX

```bibtex
@article{zhou2025mira,
  title={When Visualizing is the First Step to Reasoning: {MIRA}, a Benchmark for Visual Chain-of-Thought},
  author={Zhou, Yiyang and Tu, Haoqin and Wang, Zijun and Wang, Zeyu and Muennighoff, Niklas and Nie, Fan and Choi, Yejin and Zou, James and Deng, Chaorui and Yan, Shen and Fan, Haoqi and Xie, Cihang and Yao, Huaxiu and Ye, Qinghao},
  journal={arXiv preprint arXiv:2511.02779},
  year={2025},
  url={https://arxiv.org/abs/2511.02779}
}
```

**Status:** ✅ Complete — Quadrant I Paper (Benchmark for Visual CoT)
