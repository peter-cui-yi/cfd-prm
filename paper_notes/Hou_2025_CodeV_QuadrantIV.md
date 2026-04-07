# CodeV: Code with Images for Faithful Visual Reasoning via Tool-Aware Policy Optimization

## Basic Information

**Title**: CodeV: Code with Images for Faithful Visual Reasoning via Tool-Aware Policy Optimization

**Authors**: Xinhai Hou, Shaoyuan Xu, Manan Biyani, Moyan Li, Jia Liu, Todd C. Hollon, Bryan Wang

**Venue**: arXiv (November 2024, v2 March 2026)

**Year**: 2025

**Link**: https://arxiv.org/abs/2511.19661

---

## Abstract Summary

CodeV addresses a critical but overlooked failure mode in visual agents: high final-answer accuracy can coexist with *unfaithful* tool use, where models invoke tools on irrelevant regions or ignore tool outputs entirely but still guess correctly. CodeV introduces (1) a faithfulness evaluation protocol that measures whether tool outputs actually contain queried evidence, and (2) TAPO (Tool-Aware Policy Optimization), a process-level RL framework that augments GRPO with dense rewards defined directly on visual tool inputs and outputs (not chain-of-thought tokens). CodeV represents tools as Python code, enabling step-wise verification of tool behavior.

---

## Methodology Analysis

### Representation Type
- [x] Structured Trace (Python code for tool calls: `crop(image, bbox)`, `zoom_in()`, `detect()` with typed inputs/outputs)

### Verification Channel
- [x] Execution Feedback (tools are actually executed; TAPO assigns step-wise rewards based on actual tool I/O, not LLM's description of tool use)

### 2×2 Matrix Placement
**Quadrant**: IV

**Justification**:
- **Structured**: Tool calls are represented as executable Python code with explicit function signatures, not natural language descriptions ("I should look at the top-left region"). Each tool call has verifiable input parameters (bounding box coordinates) and output types (cropped image, detection results). The code representation makes intermediate reasoning steps machine-parseable.
- **Tool/Execution**: Tools are actually executed (real crops, real detections). More importantly, TAPO's training reward is defined *on the execution outputs* (does the crop contain relevant evidence?), making execution the ground truth for training signal, not LLM assessment.
- **Replayability**: High — tool call sequence + execution outputs (image crops, detection results) form a fully replayable trace. The faithfulness evaluation protocol itself *is* a replayability check: re-run the tool calls and verify they produced evidence-containing outputs.

---

## Key Contributions

1. First systematic empirical study revealing the accuracy-faithfulness decoupling: high VQA accuracy can coexist with low rates of faithful (evidence-relevant) tool use
2. Faithfulness evaluation protocol: explicit metric measuring whether intermediate visual tool outputs contain queried evidence (not just whether the final answer is correct)
3. TAPO: process-level RL that assigns dense step-wise rewards on actual tool I/O, making tool faithfulness a first-class training objective; substantially reduces reward hacking vs. outcome-only reward

---

## Verifiability Analysis

### Grounding Strength
Strong — tool inputs (bounding boxes for crop/zoom) explicitly specify which image regions are being examined. TAPO's reward directly evaluates whether those regions contain the relevant evidence, creating a closed verification loop.

### Checkability
High — each tool call is checkable: (1) Was the tool input region plausible? (2) Does the tool output contain evidence relevant to the question? TAPO's reward signal is exactly this check, made automatic.

### Replayability
High — tool calls + execution outputs (crops, detections) form a deterministic replay-able trace. The faithfulness protocol provides a standardized way to re-evaluate any trace.

### Faithfulness Risk
Explicitly addressed — the entire paper is about detecting and eliminating unfaithful tool use. TAPO's dense rewards penalize tool calls that don't produce evidence-relevant outputs, directly training away the most common faithfulness failure mode.

### Robustness
Medium-High — explicit supervision on intermediate tool behavior reduces the risk of spurious correlations driving tool selection. However, performance still depends on underlying vision tool quality (detection, OCR, etc.).

### Cost/Latency
Medium — two-stage SFT+RL training increases training cost. Inference requires executing multiple tool calls (Python + visual processing), but this is bounded by a fixed maximum number of tool invocations.

### Security
Medium — executable Python tool calls with image coordinate inputs could be manipulated by adversarial images to trigger tool calls on sensitive regions. Dense reward on tool I/O requires the reward model itself to be secure.

---

## Failure Modes

1. **Reward model faithfulness**: TAPO's step-wise reward (does tool output contain relevant evidence?) is computed by another model. If the reward model incorrectly assesses relevance, TAPO may train toward wrong tool behavior
2. **Early-step errors**: If the first tool call crops the wrong region, all subsequent reasoning is based on the wrong visual evidence. TAPO penalizes this but cannot prevent the initial crop error when the correct region is ambiguous
3. **Reward hacking at step level**: Models may learn to invoke tools on "visually complex" regions that tend to produce high relevance scores regardless of actual question relevance

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy
- [x] Evidence Attribution (faithfulness protocol: does tool output contain queried evidence)
- [x] Step Correctness (implicit in TAPO reward)

### Benchmarks
- Visual search benchmarks (primary faithfulness evaluation)
- Multimodal reasoning benchmarks (general capability)
- Math benchmarks (transfer to non-visual-search tasks)

### Key Results
- Recent visual agents achieve high accuracy but exhibit *low* faithful tool-use rates — confirming the accuracy-faithfulness decoupling hypothesis
- CodeV: competitive or superior accuracy WHILE substantially increasing faithful tool-use rates
- Strong performance on multimodal reasoning and math benchmarks (not just visual search), showing faithfulness training generalizes

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Stage 1: SFT on tool-augmented visual reasoning traces)
- [x] RL / DPO (Stage 2: TAPO = GRPO + dense step-wise rewards on tool I/O)

### Data Collection
Two-stage:
1. SFT: curated tool-augmented visual reasoning traces with correct tool uses
2. RL: online RL with TAPO rewards computed by evaluating whether each tool call's output contains question-relevant evidence (uses an evaluator model)

---

## Connections to Other Work

### Builds On
- ViReP (CVPR 2024) — execution-based RL for visual program synthesis; CodeV adds dense process-level rewards
- GRPO (process reward optimization) — extended by TAPO to apply at tool I/O level
- Visual Sketchpad (NeurIPS 2024) — tool use for structured visual reasoning

### Related To
- CodeDance (arXiv 2025) — also uses RL for executable visual reasoning; CodeDance focuses on dynamic tool composition, CodeV focuses on faithful intermediate tool use
- DeepEyesV2 (arXiv 2025) — code execution for evidence-based visual reasoning

### Influenced
Future work on process-level faithfulness verification for agentic reasoning

---

## Quotes & Key Insights

> "High final-answer accuracy often hides unfaithful visual reasoning: models may invoke tools on irrelevant regions or ignore tool outputs entirely, yet still guess the correct answer."

Key insight: **accuracy is a poor proxy for faithfulness in tool-augmented reasoning**. This is the clearest empirical demonstration of the Unfaithful Plausibility failure mode (Section 2.1 of the survey) in Q4 systems. A Q4 system's high verifiability can be *illusory* if the tools are invoked but not genuinely consulted.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Quadrant IV — faithfulness failure in Q4 systems)
- [x] Section 2.1 (Faithfulness vs. Plausibility — empirical evidence for decoupling)
- [x] Section 5 (Training — TAPO as process-level RL for tool faithfulness)
- [x] Section 8 (Challenges — accuracy-faithfulness gap)

### Narrative Role
CodeV provides the **empirical evidence that Q4 verifiability can be illusory**: even systems using real tool execution can be unfaithful if tools are invoked on irrelevant regions. It represents the maturation of Q4 from "does the system use tools?" to "does the system use tools *faithfully*?"

### Comparison Points
- Excels at: faithfulness evaluation, process-level training supervision
- Key contribution: resolving the accuracy-faithfulness decoupling that naive Q4 systems exhibit

---

## Notes

- v2 (March 2026) is the most recent version — paper is actively maintained
- The faithfulness evaluation protocol is independently valuable for the survey's Section 6 (Evaluation Protocols): it provides a concrete metric beyond answer accuracy that measures intermediate tool behavior
- TAPO is a clean technical contribution that generalizes beyond visual reasoning to any tool-augmented RL setting

---

## BibTeX

```bibtex
@article{hou2025codev,
  title={{CodeV}: Code with Images for Faithful Visual Reasoning via Tool-Aware Policy Optimization},
  author={Xinhai Hou and Shaoyuan Xu and Manan Biyani and Moyan Li and Jia Liu and Todd C. Hollon and Bryan Wang},
  journal={arXiv preprint arXiv:2511.19661},
  year={2025},
  url={https://arxiv.org/abs/2511.19661}
}
```
