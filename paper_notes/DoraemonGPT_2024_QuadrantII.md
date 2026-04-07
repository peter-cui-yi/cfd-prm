# Paper Note: DoraemonGPT

## Basic Information

**Title**: DoraemonGPT: Toward Understanding Dynamic Scenes with Large Language Models (Exemplified as A Video Agent)

**Authors**: Zongxin Yang, Guikun Chen, Xiaodi Li, Wenguan Wang, Yi Yang

**Venue**: ICML 2024

**Year**: 2024

**Link**:
- arXiv: https://arxiv.org/abs/2401.08392
- ICML 2024: https://proceedings.mlr.press/v235/yang24d.html
- Project: https://z-x-yang.github.io/doraemon-gpt/
- GitHub: https://github.com/z-x-yang/DoraemonGPT

---

## Abstract Summary

DoraemonGPT is a comprehensive LLM-driven video agent for understanding dynamic scenes. Given a video and question/task, it converts the video into symbolic memory (spatial-temporal structured stores) and employs plug-and-play sub-task tools (which can generate SQL to query the memory or access external knowledge) to gather evidence. A novel MCTS-based planner schedules tool execution, explores the planning space, and aggregates multiple solution paths into an improved final answer. DoraemonGPT is evaluated on three benchmarks (Ego4D NLQ, MSVD-QA, NExT-QA) and in-the-wild scenarios, demonstrating effectiveness on dynamic scene understanding.

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
**Quadrant**: II (Text + Tools, ReAct-style) — with borderline Q4 elements

**Justification**:

1. **Textual Reasoning as Primary Interface**: The main LLM planner produces natural language reasoning and plans. Tool selection and orchestration are driven by free-form LLM reasoning ("I need to find when the person first enters the room, so I should query the temporal memory with a spatial-location condition..."). This is Q2's Thought/Action/Observation pattern.

2. **Structured Symbolic Memory as Storage**: The video is pre-processed into symbolic memory (SQL database of instances + attributes), which is Q3/Q4 territory. However, the key distinction is that this memory is a **static pre-computed representation** used as a retrieval store — not a dynamically generated reasoning trace. The LLM's reasoning trace itself remains natural language.

3. **SQL as Tool Output, Not Primary Trace**: Sub-task tools internally generate SQL to query the symbolic memory. The SQL is an implementation detail of the tool, not the LLM's primary reasoning artifact. The LLM receives the SQL query result as natural language text (e.g., "The person enters at segment 12-15"), not the SQL itself.

4. **MCTS Planning is Textual**: The MCTS planner operates over natural language action spaces (which tool to call next), not over program syntax trees. Each MCTS node represents a natural language tool selection decision.

5. **Distinction from VideoAgent**: Similar Q2 placement. Key difference: DoraemonGPT adds MCTS-based planning (exploring multiple paths) while VideoAgent uses a simpler sequential tool loop. Both store structured memory but communicate via natural language.

6. **Why not Q4?**: Unlike ViperGPT or Visual Sketchpad where the primary reasoning artifact is executable code, DoraemonGPT's LLM outputs are natural language plans. The SQL generation happens inside sub-task tools (transparent to the main LLM), not as the main LLM's output.

---

## Key Contributions

1. **MCTS-Based Tool Planning**: Introduces LLM-driven Monte Carlo Tree Search for tool scheduling in video understanding, allowing exploration of multiple solution paths and backpropagation of rewards to select better plans — going beyond greedy sequential tool selection.

2. **Dual Symbolic Memory Architecture**: Space-dominant memory (instances/objects with attributes, queryable by SQL) + time-dominant memory (frame/clip-level temporal structure), providing comprehensive video representation for spatial and temporal reasoning.

3. **Plug-and-Play Tool Design**: External knowledge tools can be added without modifying the core architecture. The system supports specialized domain tools (e.g., chemistry analysis for lab experiment understanding), making it extensible to new domains.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Symbolic memory stores explicit, queryable evidence: object IDs, attributes, positions, timestamps
- SQL queries over symbolic memory produce concrete, grounded results (not vague descriptions)
- MCTS search logs show which paths led to the final answer, providing a verifiable decision tree
- Limitation: Symbolic memory quality depends on perception tools (detectors, captioners) that may miss details or produce errors

### Checkability
**Assessment**: Moderate-High
- MCTS tree structure provides auditable planning trace: which alternatives were considered, why current path was selected (reward values)
- SQL query results are concrete and replayable given the same symbolic memory
- Sub-task tool outputs are logged as observations in the planning tree
- Limitation: MCTS reward function relies on LLM evaluation, which may not be reliable

### Replayability
**Assessment**: High
- Symbolic memory is deterministic given fixed perception models
- MCTS exploration with same random seed produces same tree
- SQL queries over same symbolic memory produce same results
- Full planning tree can be re-explored (replay best path)

### Faithfulness Risk
**Assessment**: Low-Moderate
- Symbolic memory forces grounding: LLM cannot answer without querying actual video evidence
- MCTS explores multiple paths, reducing the chance of a single unfaithful reasoning thread dominating
- Risk: Reward model (another LLM) may prefer plausible-but-wrong paths
- Risk: Symbolic memory may miss critical video details (perception tool limitations)

### Robustness
**Assessment**: Moderate
- MCTS exploration provides robustness against greedy planning errors (can backtrack and try different tools)
- Modular tool design: individual tools can be swapped without changing architecture
- Limitation: Symbolic memory construction is expensive and sensitive to video quality
- Limitation: MCTS search budget constrains exploration depth

### Cost/Latency
**Assessment**: Very High
- Memory construction: requires running detectors, trackers, captioners on entire video
- MCTS: each node expansion requires LLM call + potential tool execution
- Many nodes explored before convergence
- Significantly more expensive than VideoAgent (which uses simpler sequential tool calls)
- Paper notes computational cost as limitation

### Security
**Assessment**: Low Risk
- Operates on local video content — no web access
- SQL queries are over internal symbolic memory — limited injection risk
- External knowledge tools could introduce adversarial content if web search is used

---

## Failure Modes

1. **Symbolic Memory Construction Errors**: If the perception tools (detectors, trackers, captioners) fail to correctly populate the symbolic memory (e.g., missed objects, incorrect attribute labels, tracking ID switches), all downstream queries will produce wrong results. The MCTS cannot recover from fundamentally incorrect memory.

2. **Reward Misestimation in MCTS**: The MCTS backpropagates rewards based on an LLM evaluating intermediate results. If the reward model incorrectly ranks a plausible-but-wrong path as high-reward, MCTS converges to the wrong solution. This is particularly risky for ambiguous questions where multiple plausible answers exist.

3. **SQL Generation Errors in Sub-tasks**: Sub-task tools rely on LLMs to generate SQL queries. Complex or ambiguous natural language questions may produce incorrect SQL (wrong table, wrong conditions, wrong aggregation), leading to empty or misleading query results.

4. **Insufficient Search Budget**: If the MCTS search budget (number of nodes) is too small, the planner may not explore enough of the planning space and miss the correct solution path. The optimal budget is task-dependent and hard to set in advance.

5. **Domain Coverage Gaps**: While the architecture supports plug-and-play tools, specialized domains (e.g., medical, legal) require domain-specific sub-task tools. Without appropriate tools, performance degrades to the fallback LLM reasoning, which may hallucinate.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (MCTS tree provides planning trace)
- [x] Robustness (tested on diverse video types and in-the-wild scenarios)
- [x] Cost/Latency (discussed qualitatively)
- [ ] Other

### Benchmarks
- **NExT-QA**: Multi-choice video QA with causal/temporal/descriptive questions
- **MSVD-QA**: Short clip QA
- **Ego4D NLQ**: Temporal grounding in egocentric videos
- **In-the-wild scenarios**: Laboratory experiment understanding, video editing assistance

### Key Results
- State-of-the-art on NExT-QA and MSVD-QA at time of publication
- Strong performance on Ego4D NLQ temporal grounding
- Ablation studies show MCTS planning critical vs. greedy scheduling
- Multi-path solution aggregation improves accuracy over single-path

---

## Training & Alignment

### Method
- [x] Other: **Zero-shot with pre-trained components** (no end-to-end training)

### Data Collection
- No training for main LLM or planner — uses GPT-4 / Gemini zero-shot
- Perception tools (detectors, trackers, captioners) are pre-trained on standard datasets
- Sub-task tools use prompt engineering to generate SQL

---

## Connections to Other Work

### Builds On
- **ReAct** (Yao et al., 2022): Thought/Action/Observation paradigm
- **MCTS** (Silver et al., 2016, AlphaGo): Planning algorithm adapted for LLM tool scheduling
- **SymbolGraph / Scene Graph** methods: Structured video representation
- **VideoAgent** (ECCV 2024): Similar Q2 video agent with structured memory

### Related To
- **VideoAgent** (ECCV 2024): Q2 anchor — both use structured memory + tool loop for video
- **OctoTools** (ICLR 2025): Extensible tool framework with similar plug-and-play philosophy
- **HAMMR** (NeurIPS 2024): Hierarchical tool composition for VQA

### Influenced
- Video understanding agent research post-2024
- MCTS planning for LLM agent systems

---

## Quotes & Key Insights

> "Considering the video modality better reflects the ever-changing nature of real-world scenarios, we exemplify DoraemonGPT as a video agent."

> "We introduce a novel LLM-driven planner based on Monte Carlo Tree Search to explore the large planning space for scheduling various tools."

**Key Insight**: DoraemonGPT addresses a fundamental limitation of sequential tool planning: the **planning space is large and greedy selection fails**. By using MCTS, the system can explore non-obvious tool orderings that yield better evidence. The backpropagation of reward through the MCTS tree allows the system to learn from intermediate results without offline training.

**Architectural Insight**: The separation of concerns in DoraemonGPT is elegant: (1) memory layer = symbolic, structured, verifiable; (2) tool layer = domain-specific, plug-and-play; (3) planning layer = LLM-driven MCTS, flexible. This three-layer design allows components to be updated independently.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II)
- [x] Section 4.2.3 (Verification Strategies — MCTS as cross-path consistency check)
- [x] Section 5 (Learning & Alignment — zero-shot with structured memory)
- [x] Section 8 (Challenges — MCTS cost, reward model reliability)

### Narrative Role

DoraemonGPT demonstrates a **more powerful but more expensive** variant of Q2:

1. **MCTS vs. sequential tool loops**: VideoAgent uses a simple ReAct loop; DoraemonGPT uses MCTS to explore plan space. Both Q2, but different reliability levels.
2. **Structured memory as pre-grounding**: The symbolic memory pre-grounds the video before any tool call, reducing hallucination risk compared to pure VQA-based approaches.
3. **Trade-off exposition**: More exploration (MCTS) = more reliable but more expensive. Sets up Section 8 discussion of cost/benefit in Q2.

### Comparison Points

**Excels at**:
- Planning robustness (MCTS explores alternatives)
- Dynamic scene understanding (temporal + spatial memory)
- Extensibility (plug-and-play tools)

**Fails at**:
- Cost efficiency (MCTS × LLM calls = very expensive)
- Memory construction errors (propagate silently)
- Real-time deployment (latency prohibitive)

---

## Notes

### Clarification on Q2 Placement vs. Q4
The symbolic memory's SQL queries are an internal tool implementation. The primary LLM's interface remains:
- **Input**: Natural language question + video
- **Output**: Natural language answer + natural language planning trace
- **Tools called**: Natural language tool names → tool executes SQL internally → returns natural language result

This is Q2 (Text + Tools), not Q4 (Structured + Executable), because the LLM's primary reasoning artifact is natural language, not SQL/code.

---

## BibTeX

```bibtex
@inproceedings{yang2024doraemongpt,
  title={DoraemonGPT: Toward Understanding Dynamic Scenes with Large Language Models (Exemplified as A Video Agent)},
  author={Yang, Zongxin and Chen, Guikun and Li, Xiaodi and Wang, Wenguan and Yang, Yi},
  booktitle={Proceedings of the 41st International Conference on Machine Learning (ICML)},
  year={2024},
  url={https://arxiv.org/abs/2401.08392}
}
```

**Status**: ✅ Complete — Quadrant II Paper
