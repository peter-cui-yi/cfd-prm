# Paper Note: Sherlock (Agentic Workflow)

## Basic Information

**Title:** Sherlock: Reliable and Efficient Agentic Workflow Execution

**Authors:** Yeonju Ro, Haoran Qiu, Íñigo Goiri, Rodrigo Fonseca, Ricardo Bianchini, Aditya Akella, Zhangyang Wang, Mattan Erez, Esha Choukse

**Affiliations:** Microsoft Azure Research, Microsoft Azure, The University of Texas at Austin

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2511.00330
- Date: November 2025

---

## Abstract Summary

Agentic workflows compose multiple LLM calls with tools, retrieval, and reasoning steps, but are inherently error-prone: incorrect output at one step propagates or amplifies through subsequent stages. Sherlock addresses three key questions: (1) which nodes deserve costly verification, (2) how to select the most appropriate verifier per node, and (3) how to use verification with minimal latency impact. Sherlock uses counterfactual fault-injection analysis to identify error-prone nodes, a learned verifier selector for cost-optimal placement, and speculative execution that overlaps verification with downstream computation—rolling back when verification fails. Compared to non-verifying baseline, Sherlock delivers 18.3% accuracy gain on average, reduces execution time by up to 48.7%, and lowers verification cost by 26.0% versus Monte Carlo search.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (LLM-generated plans, reasoning steps, tool invocations)
- [x] Structured Trace (workflow graph with nodes/edges, execution traces, verifier outputs)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (web search, retrieval, code execution—per workflow node)
- [x] Execution Feedback (verifier results, rollback on failure, speculative execution)

### 2×2 Matrix Placement
**Quadrant:** II (Text + Tools)

**Justification:**

1. **Textual Reasoning with Tool Interleaving**: Agentic workflows decompose tasks into subtasks where each node involves LLM inference optionally augmented with tool invocations (web search, retrieval, code execution). The planner generates workflows from natural language; execution is text-driven with tool calls.

2. **Tool-Augmented Verification**: Sherlock integrates verifiers (Self-Refine, Adv-Refine, Self-Consistency, LLM-as-a-Judge, Debate) that validate LLM outputs. Verification is tool-augmented in the sense that the workflow itself uses tools, and verifiers operate on tool-mediated outputs. The system observes tool/LLM outputs → plans verifier placement → acts (speculative execution + verification) → verifies (rollback if failed).

3. **Observe–Plan–Act–Verify Loop**: (a) **Observe**: Execution traces, fault-injection results, verifier accuracy/cost per task. (b) **Plan**: Topological vulnerability estimator prioritizes nodes; verifier selector chooses cost-optimal verifier. (c) **Act**: Speculative execution runs downstream nodes while verification runs in background. (d) **Verify**: If verification fails or revises output, similarity check determines rollback; system rolls back to last verified output and re-executes.

4. **Q2 vs. Q4**: Sherlock focuses on text-based agentic workflows (instruction-following, math, code, tool-use). No vision/multimodal input; workflow nodes are LLM + tools, not vision tools. Pure Q2: Text + Tools.

---

## Key Contributions

1. **Vulnerability-Guided Verifier Placement**: Counterfactual fault-injection analysis identifies error-prone nodes. Three failure modes—behavioral deviation (prompt replacement), context-loss (dropping upstream history), execution faults (output replacement)—are injected with empirically derived frequencies. Topological policy prioritizes terminal nodes, initial nodes, then intermediates by fan-in. Policy is topological (not graph-specific), enabling application to dynamically generated workflows.

2. **Cost-Optimal Verifier Selection**: Learning-based verifier selector via GRPO (Group Relative Policy Optimization) on preference data. Utility U(v, τ) = P(v, τ) − λ·C(v, τ) balances accuracy gain and cost. Task-dependent: different verifiers excel on instruction vs. code vs. math vs. tool tasks. Single global verifier is inefficient; Sherlock learns task-specific selection.

3. **Speculative Verification Runtime**: Overlaps verification with downstream computation to mask verifier latency. If verification confirms output, speculative results retained; otherwise rollback to failed node, propagate corrected output, reschedule invalidated nodes. Similarity metrics (ROUGE-L for instruction/tool; conservative rollback for code/math) determine selective rollback. Speculation depth bounded by verifier latency and cost budget.

4. **End-to-End System**: Integrates vulnerability analysis, verifier selection, and speculative execution. Delivers 18.3% accuracy gain vs. baseline, up to 48.7% execution time reduction, 26.0% cost reduction vs. Monte Carlo search.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** High

Workflow nodes receive explicit context from upstream outputs. Tool invocations (web search, retrieval, code execution) return concrete results. Verifier outputs provide additional grounding: when verification revises output, the corrected result is propagated. Execution traces (prompts, outputs per node, ground truth) enable traceability. Fault-injection analysis quantifies how each node affects final output.

### Checkability
**Assessment:** High

Per-node outputs are checkable via verifiers. Verification result (pass/fail, revised output) is explicit. Similarity metrics (ROUGE-L, etc.) provide automatic equivalence checks for selective rollback. Ground-truth final output enables end-to-end accuracy evaluation. Fault-injection experiments yield vulnerability scores per node. Verifier accuracy and cost are measurable per task.

### Replayability
**Assessment:** High

Execution traces (prompts, outputs, ground truth) are logged. Workflow structure (graph) is reproducible. Fault injection re-executes downstream with counterfactual outputs. Rollback mechanism re-executes invalidated nodes with corrected inputs. Temperature fixed to 0 during fault injection for reproducibility. Speculative execution is deterministic given verification outcomes.

### Faithfulness Risk
**Assessment:** Medium (reduced by verification)

LLM outputs can hallucinate or contain logical errors; errors propagate downstream. Sherlock mitigates via selective verification at error-prone nodes. Verifier-revised outputs may correct hallucinations. However: verifiers themselves can err; similarity-based selective rollback may retain incorrect speculative results when metrics fail (e.g., ROUGE-L collapses for code/math, AUC ≈ 0.5). Conservative full rollback for code/math reduces but does not eliminate risk.

### Robustness
**Assessment:** Medium-High

Topological policy generalizes across workflows within a domain (learned from 100+ graphs, 15K+ traces). Verifier selector adapts to task type. Speculative execution tolerates verification latency. Failure modes (behavioral deviation, context-loss, execution faults) are empirically grounded. Domain onboarding required for new domains; policy is topology-based, not workflow-specific. Benchmarks: CoTCollection, OMEGA, LiveCodeBench cover instruction, math, code, tool tasks.

### Cost/Latency
**Assessment:** Medium (optimized vs. full verification)

Verification adds up to 28.9× latency and 53.2× cost vs. baseline (single verifier). Sherlock reduces overhead via: (1) selective placement (only error-prone nodes), (2) cost-optimal verifier selection, (3) speculative execution (overlap verification with computation). Results: 48.7% execution time reduction vs. non-speculative; 26.0% cost reduction vs. Monte Carlo search. Trade-off: speculation budget and rollback aggressiveness are tunable.

### Security
**Assessment:** Medium Risk

Workflow nodes can invoke tools (web search, retrieval, code execution)—standard agent security concerns (prompt injection, unsafe tool calls). Verifiers (LLM-as-a-Judge, Debate) add external model calls. Rollback mechanism could be exploited if verification is adversarially triggered. No explicit security analysis in paper. Standard mitigations: input validation, tool sandboxing.

---

## Failure Modes

1. **Verifier Ineffectiveness**: Verifiers vary by task; some (e.g., Self-Refine) can underperform or even reduce accuracy. Misplaced verifiers waste cost. Verifier selector learns from preference data; poor training data or distribution shift can yield suboptimal selection.

2. **Similarity Metric Failure**: ROUGE-L and other lightweight metrics achieve AUC ≈ 0.5 for code and math—no better than random. Sherlock conservatively defaults to full rollback for these tasks, but semantic equivalence may be missed. Over-retention of incorrect speculative results or unnecessary rollback of correct results can occur.

3. **Fault Model Mismatch**: Injected faults (prompt replacement, context dropping, output replacement) may not cover all real failure modes. Empirical frequencies from prior work (Cemri et al., 2025) may not generalize. Unmodeled failures (e.g., tool API errors, timeout) can propagate undetected.

4. **Speculation Overhead**: When verification fails frequently, rollback incurs re-execution cost. High rollback rate can negate latency gains. Budget-constrained speculation limits depth; aggressive speculation under high failure rate wastes compute.

5. **Domain Onboarding Dependency**: Sherlock requires example workflows with execution traces and ground truth for new domains. Cold start: no learned policies. Generalization to unseen task types within a domain may degrade. Topological policy is heuristic; learned policy could overfit to onboarding data.

6. **Verifier Latency Bottleneck**: Speculation depth is bounded by verifier latency. Slow verifiers (e.g., Debate, Adv-Refine) limit how far downstream can be speculated. Verification on critical path can still stall execution if not overlapped effectively.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary; final output correctness)
- [x] Step Correctness (implicit via per-node verification)
- [ ] Evidence Attribution
- [x] Trace Replayability (execution traces, rollback)
- [x] Cost/Latency (normalized cost, execution time)
- [x] Other: Verifier utility (accuracy gain − λ·cost), match rate (verified vs. original output)

### Benchmarks
- **CoTCollection**: Instruction-following, multi-step reasoning and planning
- **OMEGA**: Math, compositional subset
- **LiveCodeBench**: Code generation, execution, test output prediction
- **Flow** (Niu et al., 2025): LLM planner for workflow generation

### Key Results
- **Accuracy**: 18.3% gain on average vs. non-verifying baseline; best-in-class vs. verifying baselines
- **Latency**: Up to 48.7% execution time reduction vs. non-speculative execution
- **Cost**: 26.0% verification cost reduction vs. Monte Carlo search-based method
- **Verifier Characterization**: Verification can add up to 28.9× latency, 53.2× cost; verifier utility is task-dependent (Figure 4)
- **Vulnerability**: Terminal nodes most vulnerable; initial nodes second; fan-in correlates with vulnerability (Figure 8)
- **Match Rate**: Verifiers often retain original output (0.6–0.8+ for instruction, code, math); lower for Tool (0.10–0.13 for some verifiers)—motivates speculative execution

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (GRPO for verifier selector)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Preference learning (utility U = P − λ·C), fault-injection-based vulnerability analysis

### Data Collection
- **Domain onboarding**: Example workflows with execution traces (prompts, outputs per node, ground truth)
- **Fault injection**: 100+ graphs, 15K+ traces; inject faults per failure mode, measure Δ(y, y′) on final output
- **Verifier characterization**: Accuracy and cost per verifier per task category (instruction, code, math, tool)
- **Preference data**: (τ, {P(vj, τ), C(vj, τ)}) for GRPO training of verifier selector

---

## Connections to Other Work

### Builds On
- **Agentic workflows**: LangGraph, Agent Framework (Microsoft), Flow (Niu et al., 2025)
- **LLM verifiers**: Self-Refine (Madaan et al., 2023), Self-Consistency (Wang et al., 2023), LLM-as-a-Judge (Zheng et al., 2023), Debate (Du et al., 2023)
- **Fault injection**: Cemri et al. (2025) failure mode frequencies
- **GRPO**: Shao et al. (2024) for preference optimization

### Related To
- **VerifiAgent** (Han et al., 2025): Unified verification agent with meta + tool-based verification; different scope (single reasoning task vs. workflow)
- **CRITIC** (Gou et al., 2024): LLM + tools for critique and revision
- **ReAct, Tool-use agents**: Yao et al. (2023); Sherlock operates at workflow level, not single-agent level

### Influenced
- Systems for reliable agentic workflow serving
- Selective verification and speculative execution for LLM pipelines

---

## Quotes & Key Insights

> "In agentic workflows, these errors are particularly problematic: mistakes made in the early nodes propagate down along the edges, amplifying as they go downstream, and contaminate the final output."

> "Verifying only the terminal node in a workflow wastes compute resources and misses opportunities to stop error propagation early in the graph, and exhaustive verification across all nodes adds a prohibitively high overhead."

> "Insight 1: Verifiers bring significant cost and latency overhead, underscoring the need for principled verifier placement strategies in an agentic workflow."
> "Insight 2: Verifiers have distinct accuracy improvements and cost behaviors, which are highly task dependent."
> "Insight 3: Revised output after verification may not necessarily change from its original output."

**Key Insight:** **Selective verification + speculative execution**—Sherlock identifies where verification matters (vulnerability analysis), selects cost-optimal verifiers per node (learning-based), and overlaps verification with computation (speculative execution with rollback). This balances reliability (18.3% accuracy gain) with efficiency (48.7% latency reduction, 26.0% cost reduction).

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II: Tool-Augmented, Agentic Workflows)
- [x] Section 5 (Learning & Alignment — GRPO for verifier selection, fault-injection analysis)
- [x] Section 6 (Evaluation & Benchmarks — CoTCollection, OMEGA, LiveCodeBench)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — verification overhead, fault model, similarity metrics)

### Narrative Role
Sherlock exemplifies **Q2 workflow-level verification**—addressing reliability of agentic workflows (LLM + tools) through principled, fault-aware verification. It demonstrates that selective verification (where to verify) + cost-optimal selection (which verifier) + speculative execution (how to minimize latency) effectively balance accuracy, cost, and latency. Complements single-task verifiers (e.g., VerifiAgent) by operating at the workflow graph level.

### Comparison Points
**Excels at:** Workflow-level verification, selective placement, cost-latency-accuracy trade-off, speculative execution, fault-injection-based vulnerability analysis
**Fails at:** Domain onboarding requirement, similarity metrics for code/math, verifier effectiveness variability

---

## Notes

- **Distinction from Sherlock (Q1)**: arXiv:2505.22651 "Sherlock: Self-Correcting Reasoning in Vision-Language Models" is a different paper (Quadrant I, VLM self-correction). This note is for arXiv:2511.00330 "Sherlock: Reliable and Efficient Agentic Workflow Execution" (Quadrant II).
- **Observe–Plan–Act–Verify**: Sherlock implements this loop at the workflow level: observe (traces, fault injection), plan (vulnerability + verifier selection), act (speculative execution), verify (rollback on failure).

---

## BibTeX

```bibtex
@article{ro2025sherlock,
  title={Sherlock: Reliable and Efficient Agentic Workflow Execution},
  author={Ro, Yeonju and Qiu, Haoran and Goiri, {\'I}{\~n}igo and Fonseca, Rodrigo and Bianchini, Ricardo and Akella, Aditya and Wang, Zhangyang and Erez, Mattan and Choukse, Esha},
  journal={arXiv preprint arXiv:2511.00330},
  year={2025},
  url={https://arxiv.org/abs/2511.00330}
}
```

**Status:** ✅ Complete — Quadrant II Paper (Agentic Workflow Verification)
