# Paper Note: OpenThinkIMG

## Basic Information

**Title:** OpenThinkIMG: Learning to Think with Images via Visual Tool Reinforcement Learning

**Authors:** Zhaochen Su, Linjie Li, Mingyang Song, Yunzhuo Hao, Zhengyuan Yang, Jun Zhang, Guanjie Chen, Jiawei Gu, Juntao Li, Xiaoye Qu, Yu Cheng

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2505.08617
- Date: May 2025 (revised July 2025)

---

## Abstract Summary

OpenThinkIMG is the first open-source, comprehensive end-to-end framework for tool-augmented LVLMs. It features standardized vision tool interfaces, scalable trajectory generation for policy initialization, and a flexible training environment. The paper proposes V-ToolRL, a reinforcement learning framework that trains LVLMs to learn adaptive policies for invoking external vision tools—enabling autonomous discovery of optimal tool-usage strategies via feedback from tool interactions. On chart reasoning tasks, the RL-trained agent (Qwen2-VL-2B) outperforms its SFT-initialized counterpart by +28.83 points, surpasses Taco and CogCom by +12.7 on average, and exceeds GPT-4.1 by +8.68 accuracy points.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form reasoning with tool invocation; ReAct-style or similar)
- [ ] Structured Trace (tool calls are API invocations, not formal programs)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (vision tools: chart parsing, OCR, etc.)
- [x] Execution Feedback (tool interaction feedback for RL)

### 2×2 Matrix Placement
**Quadrant:** II (Text + Tool-Augmented, Visual Tool RL)

**Justification:**

1. **Textual Reasoning with Tool Interleaving**: OpenThinkIMG trains LVLMs to generate reasoning interleaved with tool calls. The model produces natural language reasoning and invokes vision tools (e.g., chart parser, OCR). Tool calls are high-level API invocations, not Python programs.

2. **Tool-Augmented Verification**: External vision tools provide verifiable outputs. The model receives feedback from tool execution—e.g., parsed chart data, extracted text—which grounds subsequent reasoning. This is tool-augmented verification.

3. **Execution Feedback for RL**: V-ToolRL optimizes for task success using feedback from tool interactions. The reward signal comes from whether tool-augmented reasoning leads to correct answers—direct execution feedback.

4. **Q2 vs. Q4**: OpenThinkIMG does not generate executable code. Tool invocation is through standardized interfaces (API calls), not program synthesis. The pipeline is agentic tool-use, not ViperGPT-style code generation.

---

## Key Contributions

1. **OpenThinkIMG: First Open-Source Tool-Augmented LVLM Framework**: Comprehensive end-to-end framework with standardized vision tool interfaces, scalable trajectory generation for policy initialization, and flexible training environment. Enables the community to develop AI agents that "think with images" via tools.

2. **V-ToolRL: RL for Adaptive Tool Invocation**: Proposes reinforcement learning to train LVLMs to learn adaptive policies for invoking external vision tools. SFT on static demonstrations offers limited generalization; V-ToolRL enables autonomous discovery of optimal tool-usage strategies via task success feedback.

3. **Empirical Validation on Chart Reasoning**: RL-trained agent (Qwen2-VL-2B) outperforms SFT-initialized counterpart by +28.83 points, Taco and CogCom by +12.7 on average, and GPT-4.1 by +8.68. Validates RL as superior to SFT for dynamic tool invocation.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** High

Tool outputs (parsed charts, OCR results) provide explicit visual evidence. Each tool call returns concrete, verifiable data. Reasoning is grounded in tool outputs rather than model assumptions.

### Checkability
**Assessment:** High

Tool calls and outputs are logged. Each invocation can be checked for correctness (did the tool return valid data?). The trajectory is auditable.

### Replayability
**Assessment:** High

Trajectories (reasoning + tool calls + observations) can be logged and replayed. Given same input and tools, the interaction is reproducible.

### Faithfulness Risk
**Assessment:** Low-Medium (reduced vs. Q1)

Tool outputs provide objective grounding. The model cannot fabricate tool results. However, it may misinterpret tool outputs or invoke the wrong tool, leading to errors.

### Robustness
**Assessment:** Medium

Chart reasoning is the primary evaluation domain. Generalization to other visual reasoning tasks (e.g., spatial, OCR-heavy, scientific diagrams) is uncertain. Tool errors (e.g., parsing failure) can propagate.

### Cost/Latency
**Assessment:** High

Tool invocation adds latency. RL training requires extensive interaction. Trade-off: higher cost for higher accuracy and adaptability.

### Security
**Assessment:** Medium Risk

Tool calls can be exploited. Adversarial inputs may trigger unsafe tool behavior. Standard agent security concerns apply.

---

## Failure Modes

1. **Over-Invocation of Tools**: The model may call tools unnecessarily for simple questions, increasing latency. RL reward design must balance accuracy and efficiency.

2. **Tool Output Misinterpretation**: Correct tool outputs may be misread—e.g., misinterpreting chart axes or OCR text—leading to wrong conclusions despite correct tool results.

3. **SFT Initialization Quality**: Policy initialization via trajectory generation affects RL convergence. Poor initial trajectories may lead to suboptimal policies or slow learning.

4. **Domain Limitation**: Evaluated primarily on chart reasoning. Performance on other visual reasoning domains (e.g., natural images, diagrams, video) may not generalize.

5. **Tool Interface Standardization**: Standardized interfaces may not cover all tool capabilities. Novel tools may require framework extension.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (chart reasoning)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [ ] Trace Replayability
- [ ] Robustness
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- Chart reasoning tasks
- Baselines: SFT-initialized, Taco, CogCom, GPT-4.1

### Key Results
- +28.83 vs. SFT-initialized counterpart
- +12.7 vs. Taco, CogCom (average)
- +8.68 vs. GPT-4.1

---

## Training & Alignment

### Method
- [x] SFT with Rationale (policy initialization via trajectory generation)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (V-ToolRL)
- [x] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other

### Data Collection
- Scalable trajectory generation for policy initialization
- RL training with feedback from tool interactions
- Chart reasoning task data

---

## Connections to Other Work

### Builds On
- ReAct, MM-ReAct
- Taco, CogCom (supervised tool-learning)
- Tool-augmented VLMs

### Related To
- VISTA-R1 (agentic RL for tool-integrated reasoning)
- OpenThinkIMG provides open-source framework; VISTA-R1 provides scaled training

### Influenced
- Community adoption of OpenThinkIMG for tool-augmented visual reasoning
- V-ToolRL as paradigm for dynamic tool invocation

---

## Quotes & Key Insights

> "Considering supervised fine-tuning (SFT) on static demonstrations offers limited policy generalization for dynamic tool invocation, we propose a novel reinforcement learning (RL) framework V-ToolRL."

> "We hope OpenThinkIMG can serve as a foundational framework for advancing dynamic, tool-augmented visual reasoning."

**Key Insight:** **RL outperforms SFT for tool-use**—static demonstrations do not teach models when and how to invoke tools adaptively. V-ToolRL's task success feedback enables autonomous discovery of tool-usage strategies, yielding large gains (+28.83 vs. SFT).

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II: Tool-Augmented, Visual Tool RL)
- [x] Section 5 (Learning & Alignment — V-ToolRL, policy initialization)
- [x] Section 6 (Evaluation & Benchmarks — chart reasoning)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — tool over-invocation, domain generalization)

### Narrative Role
OpenThinkIMG exemplifies **Q2 open-source tool-augmented framework**—providing infrastructure for the community to train LVLMs with visual tools. V-ToolRL demonstrates that RL is essential for adaptive tool invocation, surpassing SFT and closed-source baselines.

### Comparison Points
**Excels at:** Open-source framework, RL for tool-use, chart reasoning, surpassing GPT-4.1
**Fails at:** Domain generalization, cost/latency, tool over-invocation risk

---

## Notes

OpenThinkIMG's open-source nature is a significant contribution—enabling reproducible research on tool-augmented visual reasoning. The +28.83 vs. SFT gap strongly supports RL for tool-use.

---

## BibTeX

```bibtex
@article{su2025openthinkimg,
  title={{OpenThinkIMG}: Learning to Think with Images via Visual Tool Reinforcement Learning},
  author={Su, Zhaochen and Li, Linjie and Song, Mingyang and Hao, Yunzhuo and Yang, Zhengyuan and Zhang, Jun and Chen, Guanjie and Gu, Jiawei and Li, Juntao and Qu, Xiaoye and Cheng, Yu},
  journal={arXiv preprint arXiv:2505.08617},
  year={2025},
  url={https://arxiv.org/abs/2505.08617}
}
```

**Status:** ✅ Complete — Quadrant II Paper (Open-Source Visual Tool RL Framework)
