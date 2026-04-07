# Paper Note: XSkill

## Basic Information

**Title**: XSkill: Continual Learning from Experience and Skills in Multimodal Agents

**Authors**: Guanyu Jiang, Zhaochen Su, Xiaoye Qu, Yi R. Fung

**Venue**: arXiv preprint

**Year**: 2026

**Link**:
- arXiv: https://arxiv.org/abs/2603.12056
- Date: March 12, 2026

---

## Abstract Summary

XSkill proposes a **dual-stream** framework that distills **experiences** (action-level) and **skills** (task-level) from past multimodal agent trajectories. It uses **visually grounded summarization** and **cross-rollout critique** to compress and refine memory, enabling **continual learning** without catastrophic forgetting. Across five benchmarks, XSkill consistently outperforms tool-only and learning-based baselines.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Structured Traces + Tool-Augmented)

**Justification**:

1. **Multimodal agent with tool use**: The agent operates in environments where actions include tool calls; trajectories encode structured state–action–observation sequences rather than pure free-form text alone.

2. **Dual memory as retrievable structure**: Experiences (fine-grained, action-level) and skills (task-level abstractions) are explicit, reusable representations—closer to structured memory than a single unstructured CoT string.

3. **Cross-rollout critique and grounding**: Critique compares rollouts and ties summaries to visual/contextual evidence, using external interaction traces (tools + environment) as the verification substrate—not a closed “text-only” verifier.

4. **Contrast with QIV**: The paper’s emphasis is on **retrieval-augmented continual learning** from agent experience, not on generating executable programs whose primary reward comes from deterministic code execution (e.g., render-then-compare pipelines).

5. **Contrast with QI**: Verification is not purely internal attention or self-consistency; it leans on **multi-trajectory comparison**, tool-grounded interaction, and structured skill/experience banks.

---

## Key Contributions

1. **Dual-stream memory (experiences + skills)**: Separates action-level episodic detail from task-level reusable skills, supporting scalable continual learning for multimodal agents.

2. **Visually grounded summarization + cross-rollout critique**: Compresses trajectories into grounded summaries and uses critique across rollouts to improve memory quality and reduce noise.

3. **Strong empirical gains**: Consistent improvements over tool-only and other learning-based baselines on five benchmarks, demonstrating the value of structured experience/skill retrieval in agent loops.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Moderate to High

Summarization is **visually grounded**, so memory entries are intended to tie back to observations and actions in trajectories. Retrieval still depends on embedding quality and summarization fidelity; errors in compression can drop visual detail.

### Checkability
**Assessment**: Moderate

Tool calls and environment steps in stored trajectories can be audited **post hoc**, but the distilled experience/skill text is not automatically executable—consistency is checked via downstream task success and critique, not syntax-level verification.

### Replayability
**Assessment**: Moderate

Original rollouts may be replayable if full logs are kept; **summarized** memory is a lossy abstraction, so replay of the *compressed* representation alone does not reproduce exact past actions.

### Faithfulness Risk
**Assessment**: Moderate

The model could **mis-summarize** successful trajectories or retrieve irrelevant skills while sounding plausible. Cross-rollout critique mitigates but does not eliminate narrative drift or over-generalization from sparse successes.

### Robustness
**Assessment**: Moderate

Sensitive to **distribution shift** in tasks and UI/tools, **noisy trajectories**, and **imbalanced** success/failure logs. Continual learning can still suffer if critique or summarization systematically favors short-horizon wins.

### Cost/Latency
**Assessment**: Moderate to High

Maintaining dual streams, summarization, critique, and retrieval adds **compute and memory** versus a single tool-only policy; tradeoffs depend on bank size and update frequency.

### Security
**Assessment**: Moderate Risk

Agent trajectories may contain **PII or sensitive screenshots**; memory banks amplify **data retention** risks. Untrusted environments raise **prompt/tool injection** concerns when past trajectories are reused as context.

---

## Failure Modes

1. **Summarization information loss**: Visually grounded summaries may drop critical spatial or temporal cues, causing retrieval of plausible-but-wrong skills for new tasks.

2. **Critique bias or collapse**: Cross-rollout critique may overfit to superficial patterns (e.g., length, format) or dominant task types, weakening discrimination between genuinely useful trajectories.

3. **Negative transfer in continual learning**: New skills or experiences can interfere with old behaviors if the memory update rule does not isolate conflicting task regimes.

4. **Tool/environment drift**: When tools or APIs change, stored experiences become stale; without explicit versioning or invalidation, retrieval hurts performance.

5. **Sparse failure coverage**: If successful rollouts dominate the bank, the agent may lack structured memory for recovery strategies and repeat the same errors.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (partial—full trajectories if logged)
- [ ] Robustness
- [x] Cost/Latency (implicit in agent setting)
- [x] Other: continual learning / retention vs. fine-tuning baselines

### Benchmarks
- Five multimodal agent benchmarks (exact names per paper; reported consistent gains vs. tool-only and learning-based baselines)

### Key Results
- Consistent improvements across five benchmarks over tool-only and learning-based baselines, supporting dual-stream memory + continual learning.

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [x] Process Supervision (critique across rollouts shapes memory quality)
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (continual / learning-from-experience framing; details per paper)
- [x] Cold-start + RL for tool-use (multimodal agent + tools)
- [ ] Verifier-guided Training
- [x] Other: **experience/skill distillation, retrieval-augmented policy**

### Data Collection
- **Past trajectories** from multimodal agent rollouts (success/failure mixes)
- **Synthetic or augmented** summaries via visually grounded summarization
- **Critique signals** from cross-rollout comparison

---

## Connections to Other Work

### Builds On
- Multimodal agents with tool use (WebVoyager, SeeAct, MM-ReAct)
- Continual / lifelong learning for LLMs and agents
- Episodic memory and skill libraries in RL and agents

### Related To
- Retrieval-augmented agents, reflexion-style critique, experience replay
- Process supervision without full program execution (contrast with Quadrant IV code-reward pipelines)

### Influenced
- Benchmarks and methods that unify **memory design** and **multimodal tool agents**

---

## Quotes & Key Insights

> (Paraphrase from framing) Multimodal agents generate rich trajectories; structuring them into **experiences** and **skills** enables scalable continual improvement beyond single-session tool use.

**Key Insight:** Quadrant II here is driven by **structured memory of interaction** (not executable programs): verification comes from **multi-rollout critique** and task-level feedback grounded in agent observations, aligning the survey’s “structured trace + tools” axis with continual agent learning.

---

## Survey Placement

### Section Placement
- [x] Section 4 (Methods by Quadrant — **Quadrant II**: structured agent traces + tools)
- [x] Section 5 (Learning & Alignment — continual learning, memory, critique)
- [x] Section 6 (Evaluation & Benchmarks — five agent benchmarks)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — forgetting, memory staleness, summarization fidelity)

### Narrative Role
XSkill is a **canonical Quadrant II** entry for **multimodal agents**: textual reasoning plus tool use, with **explicit experience/skill retrieval** and **cross-rollout critique** as the verification loop for continual learning—contrasting with QI (internal attention only) and QIV (executable code as primary artifact).

### Comparison Points
**Excels at:** Unifying tool use with structured memory, continual learning from trajectories, visually grounded summarization  
**Weaker on:** Deterministic step verification (vs. QIV), closed-form executability of distilled memory, low-latency minimal-memory agents

---

## Notes

Verify exact benchmark names, training objectives (SFT vs. RL fractions), and whether full trajectory logs are retained at inference. If the paper releases code, add repository link.

---

## BibTeX

```bibtex
@article{jiang2026xskill,
  title={{XSkill}: Continual Learning from Experience and Skills in Multimodal Agents},
  author={Jiang, Guanyu and Su, Zhaochen and Qu, Xiaoye and Fung, Yi R.},
  journal={arXiv preprint arXiv:2603.12056},
  year={2026},
  url={https://arxiv.org/abs/2603.12056}
}
```

**Status**: Draft — Quadrant II (Multimodal agent + structured experience/skill memory + tools)
