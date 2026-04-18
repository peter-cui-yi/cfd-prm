# CodeVision: Thinking with Programming Vision — Towards a Unified View for Thinking with Images

## Basic Information

**Title**: Thinking with Programming Vision: Towards a Unified View for Thinking with Images

**Authors**: Zirun Guo, Minjie Hong, Feng Zhang, Kai Jia, Tao Jin

**Venue**: arXiv (December 2025)

**Year**: 2025

**Link**: https://arxiv.org/abs/2512.03746 | https://github.com/ByteDance-BandAI/CodeVision

---

## Abstract Summary

CodeVision reveals a critical and previously overlooked vulnerability: SOTA MLLMs degrade significantly on simple image orientation changes or natural corruptions, exposing the fragility of pixel-based perception. To address this, CodeVision proposes a "code-as-tool" framework where the model generates Python code as a universal interface for any image operation — moving beyond fixed tool registries to a fully open-ended tool space. Training uses SFT on complex multi-turn tool composition + RL with a dense process reward. On MVToolBench, CodeVision-7B achieves 60.1, nearly doubling Gemini2.5-Pro (32.6).

---

## Methodology Analysis

### Representation Type
- [x] Structured Trace (Python code defining arbitrary image operations on-the-fly; no fixed schema — code IS the tool definition)

### Verification Channel
- [x] Tool-Augmented (code is executed by Python interpreter; output is transformed image or operation result)
- [x] Execution Feedback (runtime errors trigger error recovery; dense process reward depends on execution outcome quality)

### 2×2 Matrix Placement
**Quadrant**: IV

**Justification**:
- **Structured**: Unlike Q2 (natural language plans with named tool calls like "call_search_api('cats')"), CodeVision generates Python code where the *entire tool invocation* is a code expression. Tools are not pre-named API calls but can be any Python-expressible image operation (including ad-hoc defined lambdas). This is the most flexible and structured form: the code is a formal specification that is both executable and syntactically machine-parseable.
- **Tool/Execution**: Python code is actually executed, transforming images (rotate, crop, detect, OCR, etc.). RL reward depends on actual execution outcomes. Runtime feedback (exceptions, unexpected output types) is handled by error recovery mechanisms learned during SFT.
- **Replayability**: High — the code trace is an exact, deterministic specification. Any reasoning step can be re-run with any Python environment containing the required libraries. Dense process reward logs provide step-level execution records.

---

## Key Contributions

1. Empirical discovery: SOTA MLLMs degrade on simple orientation changes and natural corruptions — a fundamental brittleness of pixel-based visual reasoning
2. "Code-as-tool" framework: generalization beyond fixed tool registries to any Python-expressible image operation, enabling flexible multi-turn tool composition
3. MVToolBench: new benchmark for evaluating robustness (orientation changes) and multi-tool reasoning, where CodeVision-7B nearly doubles Gemini2.5-Pro

---

## Verifiability Analysis

### Grounding Strength
Strong — code operations are explicitly applied to specific image regions or channels. Python operations like `rotate(image, angle=90)` or `crop(image, x1, y1, x2, y2)` have precise, verifiable semantics. No ambiguity about what "grounding" was applied.

### Checkability
High — code is deterministic (same inputs → same outputs). Intermediate results (transformed images) can be inspected at each step. Unlike text-based tool planning, code outputs are typed and machine-checkable.

### Replayability
High — the code trace is a complete specification. Given the same Python environment, every step is exactly reproducible. Error recovery actions (catching exceptions, adapting code) are themselves code and thus replayable.

### Faithfulness Risk
Low for execution — code operations are deterministic and cannot "hallucinate" their outputs. Risk remains in how the LLM *interprets* execution results in its reasoning text before generating the next code step.

### Robustness
High — the specific motivation is robustness to orientation changes and corruptions. Code operations can explicitly handle these (e.g., `np.rot90(image)`, histogram equalization) whereas pixel-based perception cannot. Error recovery from runtime feedback adds additional robustness.

### Cost/Latency
High — multi-turn tool composition with arbitrary Python operations incurs significant execution overhead. Dense process reward during training adds cost compared to outcome-only training. Inference requires Python environment with all image processing libraries.

### Security
Very high risk — "any Python-expressible image operation" means the attack surface is essentially all of Python's standard library. An adversarial prompt could trigger `os.system()` calls or network requests. This is the highest-security-risk Q4 approach. Sandboxing must be extremely strict.

---

## Failure Modes

1. **Security: open-ended code execution**: The explicit design goal (any Python operation, beyond fixed registries) creates maximum security risk. No tool whitelist means sandboxing must be comprehensive and robust to escape attempts.
2. **Cost: dense reward overhead**: RL with dense process rewards requires evaluating intermediate execution outputs at each step during training. For complex multi-turn sequences, this multiplies training compute significantly.
3. **Cascading errors: no type contracts**: Unlike fixed tool registries (which have documented I/O types), ad-hoc code-defined operations have no pre-specified types. A function returning an unexpected type silently fails downstream (`AttributeError`, `TypeError`) without triggering a meaningful execution error signal.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy
- [x] Robustness (to orientation changes and corruptions — novel evaluation dimension)
- [x] Multi-tool reasoning (MVToolBench score)

### Benchmarks
- MVToolBench (multi-tool reasoning; new benchmark introduced in this paper)
- Orientation robustness suite (evaluating MLLM fragility — new contribution)
- General multimodal benchmarks (Qwen2.5-VL and Qwen3-VL series)

### Key Results
- CodeVision-7B: 60.1 on MVToolBench vs. Gemini2.5-Pro's 32.6 (nearly 2×)
- Significant improvement on orientation robustness (baselines degrade drastically; CodeVision handles orientation changes via code rotation)
- Emergent capabilities: flexible tool composition, efficient chained execution, robust error recovery

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Stage 1: SFT on complex multi-turn tool composition dataset with error recovery)
- [x] RL / DPO (Stage 2: RL with dense process reward for strategic and efficient tool use)

### Data Collection
- SFT dataset: curated for complex multi-turn tool composition and error recovery scenarios (construction details not fully specified)
- RL dataset: online RL with dense process reward (specific design of dense reward function is a key technical contribution of the paper)

---

## Connections to Other Work

### Builds On
- Visual Sketchpad (NeurIPS 2024) — code for creating auxiliary visual artifacts; CodeVision extends to arbitrary image operations
- ViReP (CVPR 2024) — RL for visual program synthesis; CodeVision uses denser process rewards
- DeepEyesV2 (arXiv 2025) — code execution for visual reasoning; CodeVision adds open-ended tool definition

### Related To
- CodeDance (arXiv 2025) — same ByteDance ecosystem, similar code-as-tool approach; CodeDance emphasizes dynamic tool composition with visual artifact rendering, CodeVision emphasizes robustness to visual corruptions and open-ended tool space
- CodeV (arXiv 2025) — TAPO for faithful tool use; CodeVision uses dense process rewards for strategic tool use (both address process-level training but with different emphases)

### Influenced
Future work on robust multimodal reasoning via code operations

---

## Quotes & Key Insights

> "Even state-of-the-art MLLMs are surprisingly brittle, showing significant performance degradation on images with simple orientation changes or natural corruptions."

> "Code-as-tool framework where the model generates code as a universal interface to invoke any image operation, moving beyond fixed tool registries."

Key insight: **orientation change as a test of true visual understanding vs. texture-based recognition** — if a model truly understands a scene geometrically, it should handle rotations. Code operations can implement rotation explicitly, bypassing the need for pixel-level orientation invariance. This reveals a fundamental advantage of Q4 (executable operations) over Q1/Q3 (pixel-based perception).

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Quadrant IV — code-as-tool, open-ended tool space)
- [x] Section 8 (Challenges — security implications of open-ended execution; robustness to corruptions as eval dimension)

### Narrative Role
CodeVision represents the **"universal tool interface" design pattern** in Q4: code replaces a fixed tool registry with an open-ended programming interface. This achieves maximum flexibility (any Python-expressible operation) at the cost of maximum security risk. The robustness findings provide empirical motivation for why pixel-based reasoning (Q1, Q3) is insufficient for real-world deployment.

### Comparison Points
- Excels at: robustness to corruptions, multi-tool reasoning flexibility, open-ended tool composition
- Weaker at: security (open tool space), cost (dense RL training)

---

## Notes

- ByteDance BandAI affiliation — suggests close connection to production deployment needs (explains focus on robustness to image corruptions)
- Nearly 2× improvement over Gemini2.5-Pro on MVToolBench is a remarkably strong result for a 7B model
- The MVToolBench dataset introduced here could be independently useful for the survey's Section 6 (Evaluation Benchmarks)
- Orientation robustness finding is a powerful argument for Q4 in the survey — it shows pixel-based methods have a fundamental limitation that executable code methods can overcome

---

## BibTeX

```bibtex
@article{guo2025codevision,
  title={Thinking with Programming Vision: Towards a Unified View for Thinking with Images},
  author={Zirun Guo and Minjie Hong and Feng Zhang and Kai Jia and Tao Jin},
  journal={arXiv preprint arXiv:2512.03746},
  year={2025},
  url={https://arxiv.org/abs/2512.03746}
}
```
