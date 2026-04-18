# ViReP: Self-Training Large Language Models for Improved Visual Program Synthesis With Visual Reinforcement

## Basic Information

**Title**: Self-Training Large Language Models for Improved Visual Program Synthesis With Visual Reinforcement

**Authors**: Zaid Khan, Vijay Kumar BG, Samuel Schulter, Yun Fu, Manmohan Chandraker

**Venue**: CVPR 2024 (pp. 14344–14353)

**Year**: 2024

**Link**: https://arxiv.org/abs/2404.04627 | https://zaidkhan.me/ViReP

---

## Abstract Summary

ViReP addresses the fundamental training problem for visual program synthesis: no dataset of visual programs exists, and crowdsourcing is impractical due to the need for expert annotators. The solution is reinforced self-training — treating the LLM as a policy, using existing vision-language annotations to construct coarse execution-based reward signals (program output correct/incorrect), and applying REINFORCE-style policy gradient to iteratively improve program synthesis. A small number of human corrections (<50) enables continued training beyond the 1-3 iteration saturation point.

---

## Methodology Analysis

### Representation Type
- [x] Structured Trace (Python programs calling vision APIs: object detector, CLIP, VQA model, etc.)

### Verification Channel
- [x] Tool-Augmented (vision models are real tools being called)
- [x] Execution Feedback (program execution output against existing task annotations provides reward signal for RL)

### 2×2 Matrix Placement
**Quadrant**: IV

**Justification**:
- **Structured**: LLM generates Python programs as reasoning traces — not natural language. Each inference step corresponds to a typed function call with explicit arguments and return values. The program structure makes reasoning machine-checkable.
- **Tool/Execution**: At inference, programs are actually executed (calling object detectors, CLIP, VQA models). At training, execution results are compared against existing annotations to produce reward signal. This is execution-as-verification at its most direct form.
- **Replayability**: High — programs are deterministic given fixed API implementations. Any query's reasoning can be fully replayed. The RL training is itself a form of large-scale replayability verification (running millions of program executions to compute rewards).

---

## Key Contributions

1. First application of reinforced self-training (execution-based RL) to visual program synthesis, eliminating the need for human program annotations
2. Demonstrates that small self-trained LLMs (via execution RL) match or outperform frozen LLMs 10× larger on compositional visual reasoning
3. Shows that execution feedback is a viable training signal for structured visual reasoning — establishing the training paradigm that later papers (CodeV, CodeDance) extend

---

## Verifiability Analysis

### Grounding Strength
Strong — programs explicitly call specialized vision models (object detector, depth estimator, CLIP) with specific image inputs. Grounding is structurally enforced by the API, not asserted in text.

### Checkability
High at inference — each program step produces a typed value (list of bounding boxes, similarity score, boolean). Training reward is binary (correct/incorrect final answer), which is coarse but definitive.

### Replayability
High — programs are self-documenting; any query's full reasoning chain (program + API call results) is replayable. RL training logs are themselves replayable execution traces.

### Faithfulness Risk
Low — the program IS the reasoning. Unlike text CoT, there is no possibility of the model generating a "plausible but unfaithful" explanation because the program is executed and the result is checked. Reward hacking is possible (see failure modes) but different from unfaithful explanation.

### Robustness
Medium — saturation at 1-3 iterations without human corrections suggests reward hacking. The coarse binary reward (final answer correct/incorrect) does not penalize programs that reach correct answers via wrong intermediate steps.

### Cost/Latency
Medium — inference requires executing a Python program with multiple API calls. Training requires large-scale program execution (reward signal computation for entire training set × number of RL iterations).

### Security
Medium — executing LLM-generated Python code requires sandboxing. RL training could incentivize programs that exploit API implementation artifacts (reward hacking via boundary conditions).

---

## Failure Modes

1. **Reward hacking**: Binary outcome reward cannot penalize programs that get the right answer via wrong intermediate steps. RL may learn "lucky" programs that exploit dataset-specific artifacts rather than genuine visual understanding
2. **Training saturation**: Without human corrections, training saturates after 1-3 iterations — the model collapses to a set of reward-maximizing programs that are narrow and non-generalizing
3. **API coverage gap**: Programs can only invoke available APIs; queries requiring capabilities not in the tool registry (e.g., OCR, spatial reasoning beyond detection) are handled by fallback text reasoning, reducing verifiability

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across all tasks)

### Benchmarks
- Object detection: COCO
- Compositional VQA: GQA
- Image-text retrieval (unspecified)

### Key Results
- Self-trained LLM (ViReP) outperforms or matches frozen few-shot LLMs 10× larger (e.g., GPT-4 few-shot) across all three task types
- Training with <50 human corrections extends iteration from 3 to 10+ before saturation

---

## Training & Alignment

### Method
- [x] RL / DPO (REINFORCE-style policy gradient with execution-based reward)
- [x] Cold-start + RL for tool-use (few-shot prompting for warm start, then RL fine-tuning)

### Data Collection
No human program annotations required. Reward signal derived from existing vision-language task annotations (e.g., VQA answer labels): if program execution produces the annotated answer → reward=1, else → reward=0.

---

## Connections to Other Work

### Builds On
- VisProg (CVPR 2023) — visual program paradigm (tool registry, compositional reasoning)
- ViperGPT (ICCV 2023) — Python execution for visual reasoning
- REINFORCE (Williams 1992) — policy gradient applied to program synthesis

### Related To
- VDebugger (EMNLP 2024) — execution feedback for debugging (complementary: VDebugger fixes programs, ViReP learns to write better ones)
- Visual Program Distillation (CVPR 2024) — also trains a model using program execution results, but distills into a VLM (inference becomes Q1/Q3), whereas ViReP maintains Q4 at inference

### Influenced
- CodeV (arXiv 2025) — extends execution-based RL with dense step-wise process rewards
- CodeDance (arXiv 2025) — extends execution RL with balanced adaptive tool-call rewards

---

## Quotes & Key Insights

> "No dataset of visual programs for training exists, and acquisition of a visual program dataset cannot be easily crowdsourced due to the need for expert annotators."

Key insight: **execution-based reward is a scalable supervision signal** for structured visual reasoning that requires zero human program annotations. This is the founding observation for a whole line of work (CodeV, CodeDance, RECODE).

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Quadrant IV)
- [x] Section 5 (Training & Alignment — execution RL as training paradigm)

### Narrative Role
ViReP represents the **"how to train Q4 systems without program annotations"** solution. It is the CVPR 2024 anchor for execution-RL training of visual program synthesis. Pairs naturally with VDebugger (2024, inference-time debugging) and foreshadows CodeV/CodeDance (2025, denser process rewards).

### Comparison Points
- Excels at: eliminating need for program annotations; training paradigm scalability
- Weaker at: process-level faithfulness (coarse binary reward cannot penalize intermediate errors); addressed by later CodeV (TAPO)

---

## Notes

- The paper is at CVPR 2024, making it a top-venue 2024 anchor for Q4 training
- Interesting contrast with VPD (CVPR 2024): VPD distills programs into a VLM (Q4 training → Q1/Q3 inference), ViReP maintains Q4 at inference (LLM generates programs that get executed). These represent two different choices for the "training vs. inference cost" trade-off.
- The saturation problem without human corrections is an early signal of the reward hacking issue that CodeV (TAPO) specifically targets

---

## BibTeX

```bibtex
@inproceedings{khan2024virep,
  title={Self-Training Large Language Models for Improved Visual Program Synthesis With Visual Reinforcement},
  author={Zaid Khan and Vijay Kumar BG and Samuel Schulter and Yun Fu and Manmohan Chandraker},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages={14344--14353},
  year={2024},
  url={https://arxiv.org/abs/2404.04627}
}
```
