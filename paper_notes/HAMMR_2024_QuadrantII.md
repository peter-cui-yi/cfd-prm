# Paper Note: HAMMR

## Basic Information

**Title**: HAMMR: HierArchical MultiModal React agents for generic VQA

**Authors**: Lluis Castrejon, Thomas Mensink, Howard Zhou, Vittorio Ferrari, Andre Araujo, Jasper Uijlings

**Venue**: NeurIPS 2024 Workshops (Multimodal Algorithmic Reasoning; Compositional Learning)

**Year**: 2024

**Link**:
- arXiv: https://arxiv.org/abs/2404.05465
- OpenReview: https://openreview.net/forum?id=AAH9wsYzvb
- NeurIPS Virtual: https://neurips.cc/virtual/2024/106670

---

## Abstract Summary

HAMMR proposes a hierarchical extension of multimodal ReAct agents for generic VQA, where top-level LLM+tools agents can call upon specialized sub-agents (counting agent, OCR agent, spatial reasoning agent, external knowledge agent, etc.). The key insight is that naively combining all tools for a single generic VQA system performs poorly; hierarchical compositionality is essential. HAMMR outperforms naive LLM+tools by 19.5% and surpasses the standalone PaLI-X VQA model by 5.0% on a diverse VQA suite.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Text + Tools, ReAct-style)

**Justification**:

HAMMR is a direct instantiation of the ReAct paradigm in the multimodal domain:

1. **Textual Representation**: The top-level agent produces natural language Thought/Action/Observation traces. Sub-agents also communicate via natural language. No program synthesis or structured DSL involved — the "hierarchy" is implemented through natural language tool calls where one agent calls another.

2. **Tool-Augmented Verification**: Each sub-agent calls external tools (Google Lens for visual search, OCR API, object detector + counter, spatial relationship classifier, web search for external knowledge). Tool outputs feed back as natural language Observations.

3. **Why not Q4?**: Unlike ViperGPT or Visual Sketchpad, HAMMR does not generate executable programs. The orchestration is through natural language prompt calls, not code execution.

4. **Why not Q3?**: No structured intermediate representations (graphs, scene graphs, schemas). The intermediate states are plain text.

---

## Key Contributions

1. **Hierarchical Compositionality**: Demonstrates that agents calling specialized sub-agents (rather than having a single agent with all tools) is critical for generic VQA performance — 19.5% improvement over naive LLM+all-tools.

2. **Generic VQA Benchmark Suite**: Evaluates across diverse VQA categories — counting, spatial reasoning, OCR, visual pointing, external knowledge — as a unified challenge, contrasting with per-benchmark optimization.

3. **Agent Specialization Principle**: Shows empirically that task-specific sub-agents (each with curated tool subsets) dramatically outperform a monolithic agent with all tools; provides design guidance for multi-tool VQA systems.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Moderate-High
- Sub-agents ground reasoning to specific visual operations (OCR extracts text regions, counter grounds object counts, spatial agent grounds relative positions)
- Top-level agent reasoning is grounded via sub-agent outputs (text observations from concrete tool results)
- Limitation: Sub-agent outputs are returned as text, so the top-level agent receives evidence but may misinterpret it

### Checkability
**Assessment**: Moderate
- Tool calls at both levels are explicitly logged (which sub-agent was called, with what query, what output was returned)
- Sub-agent internal tool calls (OCR API results, detection outputs) can be audited
- Limitation: The top-level reasoning connecting sub-agent outputs is natural language — cannot auto-validate

### Replayability
**Assessment**: Moderate
- Given the same VQA model backbone and tool APIs (same versions), traces can be reproduced
- Hierarchical call graph (which top-level agent called which sub-agent with what query) is recorded
- Limitation: Non-deterministic LLM outputs may produce different traces across runs

### Faithfulness Risk
**Assessment**: Moderate
- Tool calls force grounding: agent cannot answer counting questions without calling the counter tool
- Risk: Top-level agent may selectively weight sub-agent outputs, potentially ignoring valid evidence
- Example failure: Spatial sub-agent returns "left" but top-level agent combines with visual cue and says "right"

### Robustness
**Assessment**: Moderate
- Hierarchical design provides some redundancy (if one sub-agent fails, top-level agent can try another)
- Each sub-agent is specialized, reducing the chance of complete failure on any category
- Limitation: If a category is not covered by any sub-agent, performance degrades to the naive approach

### Cost/Latency
**Assessment**: High Cost
- Hierarchical calls: top-level agent call + sub-agent call(s) + tool API calls per question
- Each level introduces LLM inference latency
- Paper does not quantify cost but notes this as a limitation of the ReAct approach

### Security
**Assessment**: Low Risk
- Tools are perception/retrieval APIs (no code execution, no user-provided web content)
- External knowledge search could introduce adversarial content
- No explicit injection protections mentioned

---

## Failure Modes

1. **Sub-agent Selection Error**: Top-level agent incorrectly routes to a sub-agent not suited for the task. Example: routing a counting question to the visual-pointing sub-agent when it should go to the counting sub-agent. Since sub-agents have curated tool subsets, wrong routing produces irrelevant tool outputs.

2. **Inter-level Output Misinterpretation**: Sub-agent correctly identifies evidence (e.g., OCR returns "EXIT" sign), but top-level agent draws wrong conclusion (e.g., misattributes direction from sign text). The textual interface between levels creates a semantic gap.

3. **Coverage Gaps for Novel Tasks**: Generic VQA may encounter question types not covered by any specialized sub-agent. Top-level agent falls back to naive LLM+all-tools, performing poorly.

4. **Cascading Failures in Multi-hop Questions**: Multi-hop questions require chaining sub-agent calls; an error in the first sub-agent call pollutes context for subsequent calls with no recovery mechanism.

5. **Tool API Brittleness**: OCR, visual search, and counting tools have failure modes (low-resolution text, occluded objects, cluttered scenes). Sub-agents have no fallback when primary tool fails.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [ ] Trace Replayability
- [x] Robustness (implicit: tested across diverse question types)
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- **Generic VQA Suite** (custom, authors assembled): Counting, spatial reasoning, OCR-based, visual pointing, external knowledge, standard VQA
- Implicit comparison against NaturalBench, TextVQA, COCO counting, etc.

### Key Results
- HAMMR vs naive LLM+tools: +19.5% on generic VQA suite
- HAMMR vs PaLI-X (standalone VQA): +5.0%
- Hierarchical agent design critical: removing hierarchy → performance collapses to naive baseline

---

## Training & Alignment

### Method
- [x] Other: **Zero-shot / few-shot prompt engineering** (no finetuning of agent or sub-agents)

### Data Collection
- No training data for agent — uses pre-trained LMM (Gemini-based or GPT-4V) with prompt engineering
- Sub-agents also prompt-based, with curated system prompts for each specialization
- Tool APIs (OCR, counter, search) are off-the-shelf, no additional training

---

## Connections to Other Work

### Builds On
- **ReAct** (Yao et al., 2022): Core Thought/Action/Observation loop
- **MM-ReAct** (Yang et al., 2023): Early multimodal ReAct application
- **Toolformer** (Schick et al., 2023): Self-supervised tool-use learning
- **HuggingGPT / Jarvis**: Hierarchical task planning with specialized models

### Related To
- **VideoAgent** (ECCV 2024): Memory-augmented tool-use for video, same Q2 quadrant
- **OctoTools** (ICLR 2025): Extensible tool framework, shares "multiple specialist tools" philosophy
- **Chameleon** (NeurIPS 2023): Plug-and-play compositional reasoning (predecessor)

### Influenced
- Work on multi-agent VQA systems
- Hierarchical agent architectures for complex reasoning

---

## Quotes & Key Insights

> "Naively applying the LLM+tools approach using the combined set of all tools leads to poor results. This motivates us to introduce HAMMR: HierArchical MultiModal React."

> "We start from a multimodal ReAct-based system and make it hierarchical by enabling our HAMMR agents to call upon other specialized agents."

**Key Insight**: The **compositionality failure** of flat multi-tool agents is the primary motivation for HAMMR. When a single agent must choose from counting tools, OCR tools, spatial tools, and knowledge tools simultaneously, tool selection becomes unreliable. Hierarchical routing — where the top-level agent only decides "which type of problem is this?" — dramatically simplifies the decision space and improves accuracy.

**Critical Design Principle**: Specialization ≠ Restriction. Each sub-agent is specialized (limited tool set), but the top-level agent can combine multiple sub-agents for multi-step problems. This creates a flexible, composable architecture without the complexity of a flat "all tools available" design.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II: Text + Tools)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 8 (Challenges & Future — agent compositionality as open problem)

### Narrative Role

HAMMR provides a **pure-play ReAct baseline** for Q2, demonstrating:

1. **Why flat multi-tool agents fail on generic VQA**: The tool selection problem is exponentially hard as tool count grows.
2. **Hierarchical compositionality as the Q2 design principle**: Sub-agents provide specialized verification channels, top-level agent provides orchestration.
3. **Contrast with VideoAgent**: Both are Q2, but VideoAgent uses structured memory while HAMMR uses hierarchical agent architecture — two different solutions to the same "tool misuse" problem.

### Comparison Points

**Excels at**:
- Generic VQA coverage (multiple task types)
- Hierarchical agent design principles
- Direct ReAct paradigm instantiation

**Fails at**:
- Cost efficiency (multi-level LLM calls)
- Persistent memory (no cross-question memory)
- Formal verifiability (textual inter-agent communication)

---

## Notes

### Follow-up Items
- [ ] Verify if HAMMR has a published extended version beyond the NeurIPS 2024 workshops
- [ ] Check which backbone LMM was used (search results suggest Gemini-based)
- [ ] Confirm exact tool set for each sub-agent
- [ ] Compare failure modes with VideoAgent (both Q2, different architectures)

---

## BibTeX

```bibtex
@inproceedings{castrejon2024hammr,
  title={HAMMR: HierArchical MultiModal React agents for generic VQA},
  author={Castrejon, Lluis and Mensink, Thomas and Zhou, Howard and Ferrari, Vittorio and Araujo, Andre and Uijlings, Jasper},
  booktitle={NeurIPS 2024 Workshops (Multimodal Algorithmic Reasoning; Compositional Learning)},
  year={2024},
  url={https://arxiv.org/abs/2404.05465}
}
```

**Status**: ✅ Complete — Quadrant II Paper
