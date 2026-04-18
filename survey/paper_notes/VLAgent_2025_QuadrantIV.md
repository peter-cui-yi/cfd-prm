# Paper Note: VLAgent

## Basic Information

**Title:** A Neurosymbolic Agent System for Compositional Visual Reasoning

**Authors:** Yichang Xu, Gaowen Liu, Ramana Rao Kompella, Sihao Hu, Fatih Ilhan, Selim Furkan Tekin, Zachary Yahn, Ling Liu

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2506.07778
- Date: June 2025 (revised October 2025)

---

## Abstract Summary

VLAgent is a neuro-symbolic approach for compositional visual reasoning. It uses a two-stage system: (1) a front-end engine that generates a structured visual reasoning plan (symbolic program script) via LLM with few-shot chain-of-thought in-context learning; (2) a back-end engine that transforms the plan into executable code and performs a sequence of actions using neural models and symbolic functions. VLAgent introduces SS-parser to validate and repair syntax/semantic errors in the LLM-generated plan before execution, and an execution verifier for stepwise validation. VLAgent outperforms existing approaches on six visual benchmarks compared to a dozen SoTA visual reasoning models.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT—used for planning, but output is symbolic program)
- [x] Structured Trace (symbolic program script, executable code; structured plan and execution)

### Verification Channel
- [ ] No Tools / No Execution (for planning only)
- [x] Tool-Augmented (neural models, symbolic functions as tools)
- [x] Execution Feedback (code is executed; execution verifier validates stepwise results)

### 2×2 Matrix Placement
**Quadrant:** IV (Structured Trace + Execution)

**Justification:**

1. **Structured Symbolic Program**: VLAgent generates a "structured visual reasoning plan (symbolic program script)"—a formal, executable representation. The back-end transforms this into executable code. This is structured trace, not free-form text.

2. **Execution Feedback**: The back-end executes the plan—running neural models and symbolic functions. The execution verifier validates stepwise results (e.g., ensemble methods for critical reasoning, caption analysis for low-confidence cases). Execution produces concrete outputs; verification provides feedback.

3. **Q4 vs. Q2**: VLAgent produces executable programs—not natural language tool instructions. The symbolic program is a formal specification that is transformed and executed. This is program synthesis + execution, analogous to ViperGPT.

4. **Q4 vs. Q3**: The plan is executed. Neural models and symbolic functions are invoked; results are verifiable. The execution verifier provides stepwise validation—this is execution feedback, not just structured internal representation.

5. **SS-parser as Verification**: The SS-parser validates and repairs the plan before execution—adding a verification layer. The execution verifier validates during/after execution. Both contribute to Q4's execution-based verification.

---

## Key Contributions

1. **Two-Stage Neurosymbolic Reasoning System**: Front-end generates structured symbolic program script via LLM; back-end transforms to executable code and runs neural models + symbolic functions. Interpretable, visualization-enhanced pipeline for compositional visual reasoning.

2. **SS-parser: Syntax and Semantic Validation**: Examines and repairs the LLM-generated plan before execution—detecting and fixing logic errors. Ensures mapping from logic plan to executable instructions is correct, reducing execution failures from plan errors.

3. **Execution Verifier for Stepwise Validation**: Validates and refines compositional reasoning results at critical steps—e.g., ensemble methods for critical visual reasoning, caption analysis for low-confidence cases. Enables stepwise correction and refinement.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Very High

Symbolic program specifies concrete operations; execution produces verifiable outputs. Neural model outputs (e.g., detections, captions) are grounded. Execution verifier provides stepwise validation. Each step is traceable to execution.

### Checkability
**Assessment:** Very High

SS-parser checks syntax and semantics. Execution produces concrete results. Execution verifier validates stepwise. Full pipeline (plan → parse → execute → verify) is auditable. Code can be inspected and re-run.

### Replayability
**Assessment:** Very High

Symbolic program and execution trace are fully replayable. Given same image/video and plan, execution is deterministic. Full pipeline can be logged and reproduced.

### Faithfulness Risk
**Assessment:** Low

Execution provides objective grounding. The model cannot fabricate execution results. SS-parser and execution verifier catch plan and execution errors. Stepwise validation reduces unfaithful reasoning.

### Robustness
**Assessment:** Medium-High

SS-parser repairs plan errors—improving robustness to LLM mistakes. Execution verifier handles low-confidence cases. Tested on six benchmarks. Sensitivity to novel compositional structures or out-of-distribution inputs is uncertain.

### Cost/Latency
**Assessment:** High

Two-stage pipeline: LLM planning + execution. Execution can involve multiple neural model calls. Execution verifier adds overhead for critical steps. Trade-off: higher cost for higher accuracy and verifiability.

### Security
**Assessment:** Medium Risk

Executable code introduces security risks. Generated programs could be malicious if prompt is manipulated. Sandboxing for execution is essential. Standard code execution security concerns apply.

---

## Failure Modes

1. **SS-parser Repair Failures**: The SS-parser may fail to detect or correctly repair semantic errors—e.g., subtle logic bugs that pass syntax check. Incorrect repairs could introduce new errors.

2. **Execution Verifier False Positives/Negatives**: The verifier may incorrectly validate wrong results or reject correct ones—especially for edge cases. Ensemble and caption analysis have limits.

3. **LLM Plan Quality**: The front-end LLM may generate plans that are conceptually wrong or incomplete—e.g., missing steps for complex compositional tasks. SS-parser can fix syntax but not logic design.

4. **Neural Model Errors**: Back-end neural models (detection, caption, etc.) may produce wrong outputs. Errors propagate through execution. Execution verifier may not catch all neural model failures.

5. **Compositional Complexity**: For highly compositional tasks (many objects, relations, steps), the plan may become too complex—increasing SS-parser and execution failure risk.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (six benchmarks)
- [ ] Step Correctness (implicit via execution verifier)
- [ ] Evidence Attribution
- [x] Trace Replayability (executable pipeline)
- [ ] Robustness
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- Six visual benchmarks
- Comparison: dozen SoTA visual reasoning models

### Key Results
- Outperforms existing representative approaches to compositional visual reasoning
- SS-parser and execution verifier contribute to reliability

---

## Training & Alignment

### Method
- [ ] SFT with Rationale (LLM uses few-shot CoT for planning)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [x] Verifier-guided Training (execution verifier, SS-parser)
- [ ] Other: In-context learning for planning

### Data Collection
- Few-shot examples for LLM planning
- Neural models (pre-trained)
- Symbolic functions (hand-crafted or learned)

---

## Connections to Other Work

### Builds On
- ViperGPT (code generation for visual reasoning)
- Neurosymbolic AI
- Compositional visual reasoning

### Related To
- NS-VLA (neurosymbolic for robotics)
- VLAgent focuses on compositional visual reasoning; NS-VLA on robot manipulation

### Influenced
- Future neurosymbolic agent systems
- SS-parser and execution verifier as design patterns

---

## Quotes & Key Insights

> "VLAgent develops an interpretable visualization-enhanced two-stage neuro-symbolic reasoning system."

> "VLAgent introduces the SS-parser, which examines the syntax and semantic correctness of the planning script, detects and repairs the logic errors found in the LLM-generated logic plan before generating the executable program."

**Key Insight:** **Verification at multiple stages**—SS-parser validates before execution; execution verifier validates during/after. This multi-layer verification reduces failures from both plan errors and execution errors, exemplifying Q4's strength in verifiable reasoning.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant — Quadrant IV: Neurosymbolic Agent, Executable Code)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks — six benchmarks)
- [ ] Section 7 (Applications — compositional visual reasoning)
- [x] Section 8 (Challenges — SS-parser limits, execution verifier)

### Narrative Role
VLAgent exemplifies **Q4 neurosymbolic agent**—structured program (symbolic plan) + execution + multi-stage verification (SS-parser, execution verifier). It demonstrates that compositional visual reasoning benefits from program synthesis and execution, with verification layers to catch errors.

### Comparison Points
**Excels at:** Verifiability, compositional reasoning, SS-parser, execution verifier
**Fails at:** Cost, security (code execution), SS-parser/verifier limits

---

## Notes

VLAgent's SS-parser is a novel contribution—bridging LLM output and executable code with validation and repair. The execution verifier's stepwise validation (ensemble, caption analysis) provides a practical approach to catching execution errors.

---

## BibTeX

```bibtex
@article{xu2025vlagent,
  title={A Neurosymbolic Agent System for Compositional Visual Reasoning},
  author={Xu, Yichang and Liu, Gaowen and Kompella, Ramana Rao and Hu, Sihao and Ilhan, Fatih and Tekin, Selim Furkan and Yahn, Zachary and Liu, Ling},
  journal={arXiv preprint arXiv:2506.07778},
  year={2025},
  url={https://arxiv.org/abs/2506.07778}
}
```

**Status:** ✅ Complete — Quadrant IV Paper (Neurosymbolic Agent for Compositional Visual Reasoning)
