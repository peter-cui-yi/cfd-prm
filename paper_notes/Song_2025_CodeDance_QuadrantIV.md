# CodeDance: A Dynamic Tool-integrated MLLM for Executable Visual Reasoning

## Basic Information

**Title**: CodeDance: A Dynamic Tool-integrated MLLM for Executable Visual Reasoning

**Authors**: Qi Song, Honglin Li, Yingchen Yu, Haoyi Zhou, Lin Yang, Song Bai, Qi She, Zilong Huang, Yunqing Zhao

**Venue**: arXiv (December 2025)

**Year**: 2025

**Link**: https://arxiv.org/abs/2512.17312

---

## Abstract Summary

CodeDance challenges the limitations of current open-source multimodal reasoning approaches—text-only chains, rigid visual schemas, and single-step pipelines—by introducing executable code as a general solver for visual reasoning. Unlike fixed-schema calls (e.g., predicting only bounding-box coordinates), CodeDance dynamically defines, composes, and executes code to orchestrate multiple tools, compute intermediate results, and render visual artifacts (boxes, lines, plots) for transparent, self-checkable reasoning. A balanced adaptive tool-call reward guides RL training, and novel emergent behaviors (unseen tool invocations, cross-task transfer) arise without task-specific fine-tuning.

---

## Methodology Analysis

### Representation Type
- [x] Structured Trace (Python programs that dynamically compose multiple tools, compute intermediate results, and generate visual artifacts)

### Verification Channel
- [x] Tool-Augmented (multiple specialized vision tools are actually called via Python)
- [x] Execution Feedback (rendered visual artifacts — bounding boxes, plots — serve as self-checkable intermediate outputs; RL reward from balanced adaptive tool-call criterion)

### 2×2 Matrix Placement
**Quadrant**: IV

**Justification**:
- **Structured**: Unlike Q2 approaches (which use text-format tool plans with API strings), CodeDance generates full Python programs as reasoning traces. These programs can define new helper functions, use conditionals and loops, and compose multiple tool calls in complex patterns. The program structure is machine-parseable, auditable, and replayable.
- **Tool/Execution**: Programs are executed in a Python interpreter (not simulated). Execution renders visual artifacts (bounding boxes drawn on images, line plots, charts) that are explicitly self-checkable — the agent can observe the rendered output and verify its intermediate reasoning steps visually.
- **Replayability**: High — the program code is the exact artifact that can be re-run. RL-trained emergent behaviors (novel tool compositions) can be precisely replicated by running the same code. Visual artifact rendering creates an interpretable audit trail.

---

## Key Contributions

1. First open-source system achieving o3-style "thinking with images" via executable code on full multimodal reasoning benchmarks, outperforming GPT-4o
2. Balanced adaptive tool-call reward: RL objective that simultaneously penalizes tool overuse (efficiency) and under-use (exploration), addressing a key training instability in executable reasoning
3. Empirical discovery of emergent behaviors in RL training: novel tool compositions and cross-task transfer that arise without explicit supervision — suggesting general mechanisms of executable visual reasoning

---

## Verifiability Analysis

### Grounding Strength
Strong — visual artifacts (bounding boxes, annotations rendered on images) explicitly ground intermediate reasoning in image evidence. Unlike text descriptions of regions ("the upper left corner"), rendered boxes are visually verifiable.

### Checkability
High — program outputs are deterministic given the code; rendered visual artifacts can be checked by humans or automated systems. The code itself is an auditable specification of what tools were invoked with what arguments.

### Replayability
High — programs can be re-run exactly. RL training logs (program + execution output pairs) are replayable. The emergent behaviors reported in the paper can be reproduced by running the discovered programs.

### Faithfulness Risk
Low for tool invocations (actual execution grounds reasoning), but potentially medium for how the agent *interprets* execution results in text before generating the next code step. If the LLM "narrates" the execution output incorrectly in its reasoning, subsequent code may be based on misinterpretation despite correct execution.

### Robustness
High — dynamic code composition (vs. rigid schema) allows the system to handle unexpected visual structures by composing new tool combinations. Error recovery through code refinement (if execution fails with an exception, the model can catch and retry).

### Cost/Latency
High — executing Python with multiple tool calls (each involving a vision model forward pass), plus rendering visual artifacts, is significantly more expensive than text-only reasoning. The balanced tool-call reward helps mitigate unnecessary calls but does not eliminate the cost.

### Security
High risk — the flexibility of full Python execution (vs. fixed tool schemas) creates the largest attack surface among Q4 approaches. Dynamically defined helper functions could call arbitrary Python libraries. Sandboxing requirements are strict and complex.

---

## Failure Modes

1. **Security: unrestricted code execution**: Dynamic code generation without a fixed tool registry can call arbitrary Python libraries (file I/O, network, system calls). Sandboxing requires careful whitelist design and may still have escape paths.
2. **Cost: execution overhead**: Multi-tool orchestration with visual artifact rendering at each step creates significant latency (seconds per query). Not suitable for real-time applications.
3. **Cascading errors: implicit state**: Python variables passing state between code blocks can create silent dependency failures. If `detections = detect(image)` returns an empty list and later code expects non-empty, the program may produce silently wrong answers rather than an exception.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric)
- [x] Trace Replayability (implicit — code is replayable by construction)

### Benchmarks
- Visual search benchmarks
- Math reasoning benchmarks
- Chart QA benchmarks

### Key Results
- Consistently outperforms schema-driven baselines (text-only chains, bounding-box-only schemas)
- Surpasses GPT-4o and larger open-source models on all benchmarks
- Key finding: emergent cross-task transfer without task-specific fine-tuning — models learn generalizable executable reasoning patterns

---

## Training & Alignment

### Method
- [x] RL / DPO (RL with balanced adaptive tool-call reward)
- [x] Cold-start + RL for tool-use (SFT warm-start on atomic tool-use examples, then RL for composition and generalization)

### Data Collection
- SFT: atomic task-specific supervision (individual tool calls with correct outcomes)
- RL: online RL with balanced adaptive tool-call reward (penalizes both tool overuse and underuse; reward from final answer correctness + tool usage efficiency)

---

## Connections to Other Work

### Builds On
- Visual Sketchpad (NeurIPS 2024) — structured visual trace; CodeDance extends from sketch generation to arbitrary tool orchestration
- ViReP (CVPR 2024) — execution-based RL for visual programs; CodeDance uses richer reward signal
- o3 (OpenAI) — inspiration for "thinking with images" at scale

### Related To
- CodeV (arXiv 2025) — both use RL for executable visual reasoning; CodeV focuses on faithful tool use (dense step-wise reward), CodeDance focuses on dynamic tool composition (balanced adaptive reward)
- CodeVision (arXiv 2025) — also code-as-tool framework; CodeVision uses code as interface to arbitrary image operations, CodeDance uses code as general solver with explicit visual artifact rendering

### Influenced
Future work on emergent executable reasoning in multimodal systems

---

## Quotes & Key Insights

> "Recent releases such as o3 highlight human-like 'thinking with images' reasoning that combines structured tool use with stepwise verification, yet most open-source approaches still rely on text-only chains, rigid visual schemas, or single-step pipelines."

> "Beyond the expected capabilities taught by atomic supervision, we empirically observe novel emergent behaviors during RL training."

Key insight: **emergent composition in executable reasoning** — when an LLM is trained to use individual tools via RL, it can spontaneously learn to compose them in novel ways not present in training data. This is Q4-specific: you can't observe emergent *execution* patterns in Q2 (text-plan + tools) because the verification signal is weaker.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Quadrant IV — dynamic executable code as reasoning trace)
- [x] Section 5 (Training — balanced adaptive tool-call RL reward)
- [x] Section 8 (Challenges — security implications of unrestricted code execution; emergent behaviors as open research question)

### Narrative Role
CodeDance represents the **"maximum flexibility" extreme of Q4**: executable programs that can dynamically define new tools and compose arbitrary operations. It bridges from Q4 in research settings to o3-style reasoning at commercial scale. The emergent behaviors finding is particularly important for the survey's discussion of what training approaches unlock in Q4.

### Comparison Points
- Excels at: flexibility, generalization, emergent capabilities, surpassing GPT-4o
- Weaker at: security (unrestricted execution), cost (visual artifact rendering), interpretability (complex program traces are harder to audit than simple tool sequences)

---

## Notes

- Song Bai is from ByteDance/BAAI — strong industry-research pedigree
- The o3 connection is important for the survey narrative: CodeDance is the open-source research answer to proprietary systems' "thinking with images"
- Emergent behavior section is uniquely valuable for Section 8 (Future Directions) — suggests RL on executable reasoning may unlock capabilities beyond what was explicitly trained

---

## BibTeX

```bibtex
@article{song2025codedance,
  title={{CodeDance}: A Dynamic Tool-integrated {MLLM} for Executable Visual Reasoning},
  author={Qi Song and Honglin Li and Yingchen Yu and Haoyi Zhou and Lin Yang and Song Bai and Qi She and Zilong Huang and Yunqing Zhao},
  journal={arXiv preprint arXiv:2512.17312},
  year={2025},
  url={https://arxiv.org/abs/2512.17312}
}
```
