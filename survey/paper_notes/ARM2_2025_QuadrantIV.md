# Paper Note: ARM2

## Basic Information

**Title:** ARM2: Adaptive Reasoning Model with Vision Understanding and Executable Code

**Authors:** Jian Xie, Zhendong Chu, Aoxiao Zhong, Kai Zhang, Mingzhe Han, Xing Fan, Jialie Shen, Qingsong Wen

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2510.08163
- Date: October 2025

---

## Abstract Summary

ARM2 addresses the "over-thinking" problem in Large Reasoning Models by introducing a unified model that adaptively balances reasoning performance and efficiency through reinforcement learning with length-aware optimization. Beyond natural language inference, ARM2 integrates vision understanding (multimodal) and executable code into reasoning—enabling substantial token cost reduction while preserving task performance compared to long CoT. ARM2 achieves performance on par with traditional reasoning models trained with GRPO while reducing token usage by over 70% on average.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT only)
- [x] Structured Trace (executable code is a formal, structured representation—Python or similar)

### Verification Channel
- [ ] No Tools / No Execution (for text-only parts)
- [x] Tool-Augmented (code execution is a form of tool use)
- [x] Execution Feedback (code is executed; execution results provide feedback)

### 2×2 Matrix Placement
**Quadrant:** IV (Structured Trace + Execution)

**Justification:**

1. **Executable Code as Structured Representation**: ARM2 integrates "executable code" into reasoning. Code is a formal, structured representation—not free-form text. The model can choose to output code for certain steps (e.g., calculation, data processing) instead of lengthy verbal CoT.

2. **Execution Feedback**: Code is executed (e.g., Python interpreter). Execution results are returned to the model—providing verifiable feedback. This is execution feedback: the model receives concrete outputs from code execution.

3. **Q4 vs. Q2**: ARM2 generates executable code—not just natural language tool instructions. Code has formal semantics and is run by an interpreter. This is program synthesis + execution, not ReAct-style tool invocation.

4. **Q4 vs. Q3**: ARM2's code is executed. The execution environment (interpreter) runs the code and returns results. This is not just structured internal representation—it is execution with feedback.

5. **Adaptive Reasoning**: The model adaptively chooses between code and text—length-aware optimization reduces tokens by using code for steps where execution is more efficient than verbal reasoning.

---

## Key Contributions

1. **Adaptive Reasoning with Unified Format**: A unified model that adaptively balances reasoning performance and efficiency across multiple formats (text, code, vision) through RL with length-aware optimization. Addresses over-thinking without heuristic or task-specific routing.

2. **Executable Code Integration**: Integrates executable code into reasoning—enabling substantial token reduction (70%+) while preserving performance. Code execution replaces verbose verbal reasoning for calculative or data-processing steps.

3. **Multimodal Extension**: Extends beyond natural language to vision understanding—multimodal reasoning with adaptive code/text balance. Achieves performance on par with GRPO-trained reasoning models at a fraction of the token cost.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Very High (for code steps)

Code execution produces concrete, verifiable outputs. Each code step's result is grounded in execution. Vision understanding provides grounding for multimodal inputs. Text steps remain less verifiable.

### Checkability
**Assessment:** Very High (for code steps)

Code execution is checkable—run the code, compare output. Syntax and semantics can be validated. Text steps require human or learned verifier. Code steps dominate checkability.

### Replayability
**Assessment:** Very High

Code is fully replayable—execute the same code on same inputs, get same outputs. The full trace (text + code + execution results) can be logged and reproduced. Deterministic execution.

### Faithfulness Risk
**Assessment:** Low (for code steps)

Code execution cannot hallucinate—outputs are from execution. Text steps retain faithfulness risk. The model cannot "explain without executing" for code steps—execution is the source of truth.

### Robustness
**Assessment:** Medium-High

Tested across formats; length-aware optimization may improve robustness to diverse task types. Code execution can fail (e.g., runtime errors)—model must handle failures. Vision integration adds robustness considerations.

### Cost/Latency
**Assessment:** Low (primary contribution)

70% token reduction is the key benefit. Lower token cost = lower API cost, faster inference. Code execution adds small overhead but is negligible compared to token savings.

### Security
**Assessment:** Medium Risk

Code execution introduces security risks—arbitrary code execution could be exploited. Sandboxing is essential. Prompt injection could lead to malicious code generation. Standard code execution security concerns apply.

---

## Failure Modes

1. **Code Execution Errors**: Generated code may have syntax errors, runtime errors, or logical bugs—leading to wrong conclusions. The model must handle execution failures gracefully.

2. **Inappropriate Code Use**: The model may over-use code for steps that require verbal reasoning (e.g., conceptual explanation), or under-use code when it would be beneficial. Length-aware optimization may not perfectly balance.

3. **Vision-Code Integration**: For multimodal inputs, the model must correctly pass visual information (or extracted features) to code. Integration errors could cause wrong code inputs.

4. **Security Vulnerabilities**: Generated code could be malicious if prompt is manipulated. Sandboxing must be robust. Code execution attack surface is larger than text-only.

5. **Domain Limitation**: Optimized for tasks where code execution helps (math, data processing). Performance on purely conceptual reasoning may not improve—or may degrade if the model over-prefers code.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (code execution)
- [ ] Robustness
- [x] Cost/Latency (70% token reduction)
- [ ] Other

### Benchmarks
- Reasoning benchmarks (compared to GRPO-trained models)
- Multimodal benchmarks (vision understanding)

### Key Results
- Performance on par with GRPO-trained reasoning models
- Over 70% token usage reduction on average
- Validates adaptive code/text reasoning as efficiency paradigm

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (reinforcement learning with length-aware optimization)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other: Length-aware optimization

### Data Collection
- Reasoning data with code and text formats
- RL training with length-aware reward

---

## Connections to Other Work

### Builds On
- Program-aided language models (PAL, PoT)
- GRPO (Reasoning Model training)
- ViperGPT (code generation for vision)

### Related To
- ARM2 extends ViperGPT-style code execution to adaptive reasoning with length optimization
- CodePlotCoT, VisualProgrammability (code for vision)

### Influenced
- Future work on adaptive code/text reasoning
- Length-aware multimodal reasoning

---

## Quotes & Key Insights

> "ARM2 integrates executable code into reasoning, enabling substantial reductions in token cost while preserving task performance compared to long CoT."

> "Experiments demonstrate that ARM2 achieves performance on par with traditional reasoning models trained with GRPO, while reducing token usage by over 70% on average."

**Key Insight:** **Code as token-efficient reasoning**—executable code can replace verbose verbal reasoning for calculative steps, achieving 70% token reduction without accuracy loss. This positions adaptive code/text reasoning as a practical efficiency solution for deployment.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant — Quadrant IV: Executable Code + Execution)
- [x] Section 5 (Learning & Alignment — RL with length-aware optimization)
- [x] Section 6 (Evaluation & Benchmarks — token efficiency)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — code execution errors, security)

### Narrative Role
ARM2 exemplifies **Q4 adaptive reasoning**—combining executable code with text and vision for efficiency. The 70% token reduction demonstrates that structured execution (code) can dramatically reduce cost while maintaining accuracy, supporting the Q4 design space for practical deployment.

### Comparison Points
**Excels at:** Token efficiency, code execution verifiability, multimodal adaptation
**Fails at:** Code execution security, handling execution errors, domain generalization

---

## Notes

ARM2's length-aware optimization is a general framework—could apply to other format combinations (e.g., table + code, graph + code). The 70% token saving is a significant practical result.

---

## BibTeX

```bibtex
@article{xie2025arm2,
  title={{ARM2}: Adaptive Reasoning Model with Vision Understanding and Executable Code},
  author={Xie, Jian and Chu, Zhendong and Zhong, Aoxiao and Zhang, Kai and Han, Mingzhe and Fan, Xing and Shen, Jialie and Wen, Qingsong},
  journal={arXiv preprint arXiv:2510.08163},
  year={2025},
  url={https://arxiv.org/abs/2510.08163}
}
```

**Status:** ✅ Complete — Quadrant IV Paper (Adaptive Reasoning with Executable Code)
