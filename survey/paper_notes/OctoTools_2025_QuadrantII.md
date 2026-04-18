# Paper Note: OctoTools

## Basic Information

**Title**: OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning

**Authors**: Pan Lu, Bowen Chen, Sheng Liu, Rahul Chalamala, Caiming Xiong, Chetan Bansal, Kai-Wei Chang, Hao Cheng, Yejin Choi, Hannaneh Hajishirzi, Subbarao Kambhampati, Percy Liang, Tao Lei, Yizhou Sun, Xiang Ren

**Venue**: ICLR 2025 Workshop (Foundation Models in the Wild, FM-Wild)

**Year**: 2025

**Link**:
- arXiv: https://arxiv.org/abs/2502.11271
- Project: https://octotools.github.io/
- ICLR Virtual: https://iclr.cc/virtual/2025/32740
- OpenReview: https://openreview.net/forum?id=MwPOhwY3sl

---

## Abstract Summary

OctoTools is a training-free, extensible agentic framework for complex reasoning across diverse domains (visual understanding, mathematics, medicine, science, etc.). It introduces three key components: (1) standardized **tool cards** that encapsulate tool functionality and context, enabling zero-shot integration of new tools; (2) a **planner** that governs high-level (task decomposition) and low-level (step-by-step execution) planning; (3) an **executor** that instantiates tool calls and saves structured intermediate results. OctoTools achieves 9.3% average accuracy gains over GPT-4o across 16 diverse benchmarks and outperforms AutoGen, GPT-Functions, and LangChain when given equivalent tools.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Text + Tools, ReAct-style)

**Justification**:

1. **Textual Planning (High-level + Low-level)**: The planner first generates a high-level task decomposition ("First, extract the text from the image using OCR, then check for mathematical expressions, then compute") and then low-level action plans at each step. Both are natural language.

2. **Tool Cards as Formal Tool Registry**: Tool cards are structured metadata (tool name, description, input/output format, usage examples) that allow the planner to select appropriate tools. While structured as metadata, tool cards are not the reasoning trace — they are used by the planner to reason about which tool to call. The planning and observation remain textual.

3. **Executor with Structured Intermediate Results**: The executor saves tool outputs as structured intermediate data (JSON-like records). However, these are stored for context, not as the primary reasoning trace — the planner still reasons in natural language about what these results mean.

4. **Why not Q4?**: OctoTools does not generate executable code as its primary reasoning format. The planner outputs natural language plans; the executor translates these to tool API calls. Unlike code-generation frameworks (e.g., VisProg, ViperGPT), the LLM's interface is natural language, not Python.

5. **Why not Q3?**: While executor results are stored in structured format, the planner's reasoning about those results is natural language. The structured intermediate results are a means to ground subsequent reasoning, not the primary representation.

---

## Key Contributions

1. **Tool Card Abstraction**: Introduces standardized "tool cards" (metadata descriptions of tools including name, description, use cases, I/O format, examples) that enable training-free integration of any new tool. This separation of tool description from tool implementation allows the framework to be extended without modifying the planner.

2. **Hierarchical Planning Architecture**: Distinguishes high-level planning (task decomposition into sub-goals) from low-level planning (selecting specific tools for each sub-goal), providing clearer verification of reasoning quality at each level.

3. **Comprehensive Multi-Domain Evaluation**: Evaluates on 16 diverse benchmarks spanning math (MathVista, MMMU-Pro), medicine (MedQA), science (ScienceQA), general (GAIA), and specialized domains, demonstrating broad applicability and establishing a reference point for agentic multimodal reasoning systems.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Tool cards explicitly describe what each tool does and what evidence it produces — planner can reason about expected vs. actual tool outputs
- Executor saves structured intermediate results: each tool output is stored with tool name, inputs, outputs — creating an auditable evidence chain
- Tool outputs for visual tasks (OCR text, detected objects, computed answers) are concretely grounded in input data
- "Generalist Solutioner" fallback for questions without specialized tools reduces but doesn't eliminate hallucination risk

### Checkability
**Assessment**: High
- Structured intermediate results (executor saves all tool I/O) provide complete checkability
- Each reasoning step references a specific tool call with specific inputs and outputs
- High-level plan vs. low-level execution can be independently validated
- Cross-tool consistency can be checked: if OCR tool and image captioning tool produce conflicting information, this is detectable

### Replayability
**Assessment**: High
- Given same tool implementations and LLM, complete traces are reproducible
- Structured intermediate results enable partial replay (can re-run from any point in the plan)
- Paper notes that tool cards provide complete documentation for reproducing tool behavior

### Faithfulness Risk
**Assessment**: Low
- Tool-mediated reasoning prevents pure LLM hallucination on factual/perceptual claims
- Planner must select a tool and interpret its output — cannot fabricate observations
- Risk: "Generalist Solutioner" tool falls back to LLM reasoning for tasks without specialized tools, reintroducing hallucination risk
- Mitigation: High-level plan commits to tool sequence before execution, reducing opportunistic reasoning

### Robustness
**Assessment**: Moderate-High
- Extensible tool design: when one tool fails, planner can route to alternative
- 16-benchmark evaluation demonstrates robustness across domains
- Limitation: Training-free approach means no adaptation to distribution shift
- Limitation: Tool card quality determines planning quality — poorly specified cards → poor tool selection

### Cost/Latency
**Assessment**: Moderate
- Two-level planning adds overhead vs. single-step inference
- Tool card lookup and selection require additional LLM calls
- Executor I/O storage adds memory overhead
- Significantly cheaper than MCTS approaches (DoraemonGPT) since planning is sequential, not exhaustive search
- Paper reports competitive runtime on 16 benchmarks

### Security
**Assessment**: Moderate Risk
- Training-free design means no safety-specific training
- Web search tools could be exploited via prompt injection in search results
- Code execution tools (if included) introduce sandbox escape risks
- Tool card abstraction provides some protection: tools have defined I/O contracts that malicious content must fit

---

## Failure Modes

1. **Tool Card Mismatch**: When the planner's understanding of a tool (from its card) doesn't match the tool's actual behavior, reasoning proceeds on wrong assumptions. Example: Tool card says "OCR extracts all text" but the actual tool only extracts machine-printed text, missing handwriting. The planner may assume results are complete when they aren't.

2. **Planner Over-reliance on Generalist Solutioner**: For tasks without obvious specialized tools, the planner defaults to the "Generalist Solutioner" (direct LLM reasoning). This reintroduces Q1-style hallucination into an otherwise Q2 system. The system appears to use tools but actually performs direct reasoning for hard cases.

3. **High-Level Plan Commits Too Early**: The hierarchical design commits to a high-level plan before any tool is executed. If the initial high-level decomposition is wrong (e.g., misidentifying the task type), the subsequent low-level steps are all incorrect. Unlike MCTS-based approaches, there is no built-in backtracking.

4. **Cross-Tool Output Inconsistency with No Arbitration**: When multiple tools produce conflicting evidence (e.g., OCR returns "42" but calculator returns "41" for the same computation), the planner must decide which to trust. With no explicit arbitration mechanism, the LLM's biases determine the resolution.

5. **Tool Availability Mismatch with Task Complexity**: On highly specialized tasks (medical imaging, legal document analysis), available tools in the framework may not cover all necessary operations, leading to degraded performance despite the extensibility claim.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across 16 benchmarks)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (structured intermediate results)
- [x] Robustness (16 diverse benchmarks across domains)
- [ ] Cost/Latency
- [x] Other: Tool usage frequency analysis, ablation on planning levels

### Benchmarks
- **Visual**: MathVista, ChartQA, DocVQA, MMBench, MMMU-Pro
- **Medical**: MedQA, MedMCQA
- **Science**: ScienceQA, MMLU-Pro
- **General**: GAIA, HotpotQA
- **Mathematics**: MATH, AMC
- Total: 16 benchmarks, 9.3% average improvement over GPT-4o

### Key Results
- 9.3% average accuracy gain over GPT-4o (no tools)
- Up to 10.6% improvement over AutoGen, GPT-Functions, LangChain (same tools)
- Particularly strong on multimodal + computation tasks (MathVista: +12.4%, ChartQA: +8.7%)
- Tool usage analysis shows high-level planner successfully routes to specialized tools

---

## Training & Alignment

### Method
- [x] Other: **Training-free with prompt engineering** (no gradient-based training)

### Data Collection
- No training — leverages GPT-4o as base LLM
- Tool cards manually authored by researchers (describes tool purpose, I/O, examples)
- Evaluation data from existing benchmarks

---

## Connections to Other Work

### Builds On
- **ReAct** (Yao et al., 2022): Core agent loop
- **Toolformer** (Schick et al., 2023): Tool use learning
- **LangChain**: Agent framework (OctoTools compared against)
- **AutoGen** (Wu et al., 2023): Multi-agent framework (compared against)
- **HuggingGPT / TaskMatrix**: Tool-augmented reasoning

### Related To
- **HAMMR** (NeurIPS 2024): Hierarchical tool composition for VQA
- **VideoAgent** (ECCV 2024): Q2 tool-augmented reasoning
- **DoraemonGPT** (ICML 2024): Extensible video agent tools
- **Chameleon** (NeurIPS 2023): Plug-and-play compositional reasoning (earlier work)

### Influenced
- Future extensible agentic framework designs
- Tool card standardization as an emerging design pattern

---

## Quotes & Key Insights

> "OctoTools introduces standardized tool cards to encapsulate functionality, a planner for high-level and low-level planning, and an executor for tool usage."

> "OctoTools achieves 9.3% average accuracy gains over GPT-4o across 16 diverse tasks, outperforming existing frameworks when given the same tools."

**Key Insight**: OctoTools demonstrates that **framework design matters as much as tool selection**. Given identical tools, OctoTools outperforms AutoGen, GPT-Functions, and LangChain by up to 10.6% — suggesting that the hierarchical planning architecture and tool card abstraction provide genuine benefits beyond just "having tools available."

**Design Philosophy**: The tool card abstraction is a key Q2 innovation — it makes the tool registry explicit and machine-readable, allowing the LLM planner to reason about tool selection systematically rather than from vague descriptions in the system prompt. This reduces tool misuse (a key Q2 failure mode) by giving the planner clear context about each tool's capabilities.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II)
- [x] Section 4.2.7 (Tool Orchestration — tool card pattern as design principle)
- [x] Section 9 (Best Practices — tool card abstraction as recommendation)

### Narrative Role

OctoTools provides a **framework-level perspective** on Q2 design:

1. **Tool registration as a design problem**: Unlike papers that use ad-hoc tool descriptions, OctoTools formalizes tool metadata, reducing miscommunication between planner and executor.
2. **Hierarchical planning → better verifiability**: High-level plans can be audited separately from low-level execution, enabling finer-grained verification.
3. **Contrast with flat Q2 agents**: Compared to VideoAgent (no explicit tool registry) and HAMMR (hierarchical agents), OctoTools occupies a middle ground with structured tool descriptions but flexible natural language planning.

### Comparison Points

**Excels at**:
- Extensibility (tool cards enable easy addition of new tools)
- Planning clarity (two-level hierarchy)
- Broad benchmark coverage (16 tasks)

**Fails at**:
- Planner adaptability (no backtracking, rigid high-level plan)
- Specialized domain coverage (tools must be pre-defined)
- Real-time use (multiple planning levels add latency)

---

## BibTeX

```bibtex
@article{lu2025octotools,
  title={OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning},
  author={Lu, Pan and Chen, Bowen and Liu, Sheng and Chalamala, Rahul and Xiong, Caiming and Bansal, Chetan and Chang, Kai-Wei and Cheng, Hao and Choi, Yejin and Hajishirzi, Hannaneh and Kambhampati, Subbarao and Liang, Percy and Lei, Tao and Sun, Yizhou and Ren, Xiang},
  journal={arXiv preprint arXiv:2502.11271},
  year={2025},
  url={https://arxiv.org/abs/2502.11271}
}
```

**Status**: ✅ Complete — Quadrant II Paper
