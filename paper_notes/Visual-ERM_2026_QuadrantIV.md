# Paper Note: Visual-ERM

## Basic Information

**Title**: Visual-ERM: Reward Modeling for Visual Equivalence

**Authors**: Ziyu Liu, Shengyuan Ding, Xinyu Fang, et al. (Shanghai AI Lab)

**Venue**: arXiv preprint

**Year**: 2026

**Link**:
- arXiv: https://arxiv.org/abs/2603.13224
- Date: March 13, 2026
- Code: https://github.com/InternLM/Visual-ERM

---

## Abstract Summary

Visual-ERM introduces the **Visual Equivalence Reward Model (VERM)**: candidate outputs (e.g., code) are **rendered to images** and compared to **ground-truth images**, yielding **fine-grained, interpretable, task-agnostic** reward signals. Integrated into **GRPO** RL, it improves **chart-to-code** (+8.4), **table-to-markdown** (+2.7), and **SVG-to-code** (+4.1). The work also releases **VC-RewardBench** (1335 instances) for visual-equivalence reward evaluation.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: IV (Structured Traces + Execution Feedback)

**Justification**:

1. **Code → render → image comparison**: The core artifact is **executable or renderable output** whose correctness is judged by **running a rendering pipeline** and comparing pixels (or rendered structure) to a reference—classic **execution-grounded** verification.

2. **Reward from visual equivalence**: GRPO uses **visual comparison** as the reward signal, not merely tool-augmented side information. The environment feedback is the **rendered image** (and structured error annotations such as JSON, per framing).

3. **Task-agnostic mechanism**: The same render-and-compare loop applies across chart, table, and SVG domains—verification is tied to **reproducible rendering**, not a single textual rubric.

4. **Contrast with QII**: Tools may be used to render, but the **primary epistemic guarantee** is execution output (images), not retrieval/critique over agent trajectories alone.

5. **Contrast with QI**: No reliance on purely internal attention or self-consistency; **external rendering** is the bridge to ground truth.

---

## Key Contributions

1. **Visual Equivalence Reward Model (VERM)**: Defines rewards via rendered visual comparison against GT images—interpretable and fine-grained across visual output tasks.

2. **GRPO integration with execution feedback**: Shows consistent RL gains on chart-to-code (+8.4), table-to-markdown (+2.7), and SVG-to-code (+4.1), demonstrating scalable use of visual rewards.

3. **VC-RewardBench (1335 instances)**: Provides a dedicated benchmark for visual-equivalence reward modeling, supporting reproducible comparison of reward models in this regime.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High (within renderable tasks)

Rewards are tied to **actual rendered images** versus references; grounding is literal pixel/layout-level for tasks where rendering is faithful to semantics.

### Checkability
**Assessment**: Very High

Rendering success/failure, image diff metrics, and **structured annotations** (e.g., JSON error flags) are machine-checkable given GT images and a fixed renderer.

### Replayability
**Assessment**: Very High

Given candidate code/markdown, renderer version, and GT assets, visual comparison is **reproducible** modulo nondeterministic rendering (if any—usually controllable).

### Faithfulness Risk
**Assessment**: Low to Moderate

**Low** for “does it look like GT” objectives. **Moderate** risk of **visual equivalence ≠ semantic equivalence** (different code, same image; or visually similar but wrong data labels). Task design and GT curation matter.

### Robustness
**Assessment**: Moderate

Sensitive to **renderer changes**, **anti-aliasing/fonts**, **chart style drift**, and **acceptable visual diversity** (multiple valid renders). May over-penalize stylistic variance that humans accept.

### Cost/Latency
**Assessment**: High

Per-candidate **rendering + image comparison** in RL rollouts multiplies compute vs. scalar RM scoring; batching and caching help but do not remove overhead.

### Security
**Assessment**: High Risk (execution)

Rendering pipelines may execute **user- or model-generated code**; sandboxing, timeouts, and resource limits are required. **Data leakage** via malicious code in training/inference must be mitigated.

---

## Failure Modes

1. **Renderer brittleness**: Minor code or environment differences produce large visual diffs despite acceptable outputs, destabilizing reward and RL.

2. **Semantic errors with visual match**: Outputs can be wrong on underlying data while appearing visually similar (or vice versa), misaligning reward with task intent.

3. **GT coverage gaps**: VC-RewardBench and training GTs may underrepresent layout edge cases, causing reward hacking toward benchmark-specific render quirks.

4. **Reward hacking via trivial renders**: Models may exploit degenerate solutions that score well on pixels but fail downstream use (e.g., empty or overly simplified figures).

5. **Structured annotation mismatch**: If JSON error annotations are mis-calibrated, process-level feedback can reinforce incorrect error types.

6. **Distribution shift across domains**: Chart vs. table vs. SVG each stress different failure modes; a single visual metric may not transfer without calibration.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (downstream code/table/SVG quality)
- [x] Step Correctness (render success, annotation alignment)
- [x] Evidence Attribution (visual diff as evidence)
- [x] Trace Replayability (code + render logs)
- [x] Robustness (renderer/stylistic sensitivity—discussed as limitation)
- [x] Cost/Latency (rendering in RL)
- [x] Other: reward model accuracy on VC-RewardBench

### Benchmarks
- **VC-RewardBench** (1335 instances)
- Chart-to-code, table-to-markdown, SVG-to-code (main reported lifts: +8.4, +2.7, +4.1)

### Key Results
- GRPO with VERM yields consistent gains across three structured visual generation tasks; VC-RewardBench supports dedicated reward-model evaluation.

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [x] PRM (Process Reward Model) — visual equivalence RM
- [x] RL / DPO — **GRPO** with visual rewards
- [ ] Cold-start + RL for tool-use
- [x] Verifier-guided Training — **execution/visual verifier** as reward source
- [x] Other: **structured output** (e.g., JSON error annotations) for interpretable rewards

### Data Collection
- Tasks with **paired GT images** and target outputs (code/markdown/SVG)
- VC-RewardBench curation for reward evaluation
- Synthetic or human-annotated visual equivalence labels (per paper details)

---

## Connections to Other Work

### Builds On
- GRPO / group-relative RL for LLMs
- Code-to-visual execution (plotting, SVG, table rendering)
- Reward modeling and process supervision for code generation

### Related To
- MM-Zero, CodePlot-CoT, Visual-ARFT (execution + visual feedback)
- Chart/table agents (Quadrant II) that use tools—here the **verifier** is execution-render, not only retrieval

### Influenced
- **Visual reward models** as a standard component for code/structured output RL when GT images exist

---

## Quotes & Key Insights

> (Paraphrase) **Visual equivalence** turns ambiguous textual targets into concrete, inspectable **images**, yielding rewards that are fine-grained and interpretable.

**Key Insight:** This is a textbook **Quadrant IV** pattern: **structured output + deterministic rendering + visual comparison** closes the verification loop for RL—stronger objectivity than text-only RMs when the task is inherently visual.

---

## Survey Placement

### Section Placement
- [x] Section 4 (Methods by Quadrant — **Quadrant IV**)
- [x] Section 5 (Learning & Alignment — GRPO + visual RM)
- [x] Section 6 (Evaluation & Benchmarks — VC-RewardBench + task suites)
- [x] Section 7 (Applications — charts, tables, SVG)
- [x] Section 8 (Challenges — renderer fragility, semantic-visual gap, compute)

### Narrative Role
Visual-ERM anchors the survey’s story that **execution feedback** can be **visual** and **task-agnostic**, enabling scalable RL for structured generation when GT imagery is available—complementary to agentic tool use (QII) and internal attention training (QI).

### Comparison Points
**Excels at:** Interpretable rewards, reproducible verification, multi-domain visual equivalence  
**Weaker on:** Tasks without faithful renders, semantic errors invisible to pixels, runtime cost

---

## Notes

Confirm exact VERM architecture (separate vision encoder vs. end-to-end), JSON annotation schema, and renderer stack in the released GitHub repo. Add citation to Shanghai AI Lab technical reports if applicable.

---

## BibTeX

```bibtex
@article{liu2026visualerm,
  title={{Visual-ERM}: Reward Modeling for Visual Equivalence},
  author={Liu, Ziyu and Ding, Shengyuan and Fang, Xinyu and others},
  journal={arXiv preprint arXiv:2603.13224},
  year={2026},
  url={https://arxiv.org/abs/2603.13224},
  note={Code: https://github.com/InternLM/Visual-ERM}
}
```

**Status**: Draft — Quadrant IV (Render-and-compare visual reward + GRPO)
