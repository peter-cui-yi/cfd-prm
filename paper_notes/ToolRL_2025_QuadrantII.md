# Paper Note: ToolRL

## Basic Information

**Title**: ToolRL: Reward is All Tool Learning Needs

**Authors**: Cheng Qian, Emre Can Acikgoz, Qi He, Hongru Wang, Xiusi Chen, Dilek Hakkani-Tür, Gokhan Tur, Heng Ji

**Venue**: arXiv preprint (NeurIPS 2025 poster)

**Year**: 2025

**Link**: 
- ArXiv: https://arxiv.org/abs/2504.13958
- Code: https://github.com/qiancheng0/ToolRL
- OpenReview: https://openreview.net/forum?id=eOLdGbXT6t

---

## Abstract Summary

ToolRL presents the first comprehensive study on reward design for tool selection and application tasks within the RL paradigm. The authors systematically explore reward strategies across types, scales, granularity, and temporal dynamics, then propose a principled reward design framework tailored for tool use tasks. Applied to train LLMs using Group Relative Policy Optimization (GRPO), the approach achieves 17% improvement over base models and 15% gain over SFT models across diverse benchmarks, demonstrating that thoughtful reward design is critical for enhancing tool use capabilities and generalization performance.

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
**Quadrant**: II (Structured Traces + Tools)

**Justification**: 

ToolRL belongs to Quadrant II for the following reasons:

1. **Structured Representation (Tool Call Traces)**: 
   - The model learns to produce structured tool invocation sequences with specific tool names and parameters
   - Training traces include explicit tool call syntax, arguments, and execution results
   - Unlike pure textual CoT, the representation includes concrete tool interactions that can be logged and replayed
   - The "deep-thinking trajectories" mentioned in the paper contain structured tool selection decisions, not just free-form reasoning

2. **Tool-Augmented with Execution Feedback**:
   - Models interact with external tools (search engines, calculators, code interpreters, APIs) in multi-step feedback-driven loops
   - Tool outputs provide concrete, verifiable feedback (e.g., search results, calculation outputs, code execution results)
   - The RL training uses tool execution outcomes to compute rewards (correctness, format adherence, efficiency)
   - Tools offer real-time access and specialized capabilities beyond the model's parametric knowledge

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, ToolRL's reasoning trace includes:
   - Explicit tool invocation decisions (which tool to call, when, and with what parameters)
   - Structured tool outputs that ground subsequent reasoning steps
   - Executable action sequences that can be replayed to verify correctness

4. **Key Distinction from Quadrant IV**: While structured, the representation is not a fully executable program like ViperGPT (which generates Python code). The LLM produces natural language reasoning + tool calls in a specific format, not a complete programmatic trace. The focus is on tool selection and parameter specification rather than full code synthesis.

5. **RL Training Emphasis**: The paper's core contribution is reward design for RL-based tool learning, which requires structured traces to compute fine-grained rewards (format reward, correctness reward, tool selection reward). This structured feedback loop is characteristic of Quadrant II approaches.

---

## Key Contributions

1. **First Systematic Study on RL for General-Purpose Tool Learning**: Presents the first comprehensive investigation into RL-based training for general-purpose tool selection and application across diverse tool sets and task types, moving beyond narrow domains like search-only or code-only tool use.

2. **Principled Reward Design Framework for TIR**: Proposes a structured reward design framework tailored for Tool-Integrated Reasoning (TIR), analyzing four key dimensions: reward type (what to reward), reward scale (magnitude), reward granularity (detail level), and reward dynamics (temporal evolution). The framework identifies that longer reasoning traces are not inherently better, dynamic reward scaling aids learning transitions, and fine-grained reward decomposition leads to more stable training.

3. **Strong Empirical Performance with GRPO**: Demonstrates that GRPO with the proposed reward design consistently outperforms both base models (+17%) and SFT models (+15%) across multiple benchmarks (BFCL, Bamboogle, API-Bank), with robust generalization to unseen scenarios and emergent behaviors like proactiveness and metacognitive reasoning.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Tool calls explicitly reference external capabilities (search APIs, calculators, code interpreters) with concrete parameters
- Tool outputs provide grounded evidence (search results, computation results, execution outputs) that anchor subsequent reasoning steps
- Structured tool invocation format ensures each step is attributable to specific tool interactions
- Limitation: The LLM can still misinterpret tool outputs or make incorrect tool selection decisions (paper notes SFT models "over-interpret" tools and fail to reject inappropriate tools)
- Compared to pure textual CoT: Much stronger grounding due to mandatory tool interaction

### Checkability
**Assessment**: High
- Tool calls and their arguments are explicitly logged in structured format
- Tool outputs can be automatically validated (e.g., check if search results are relevant, if code executes without errors, if calculation is correct)
- Format reward component ensures tool calls follow expected syntax, enabling automatic parsing and validation
- Correctness reward provides binary signal (answer matches ground truth), enabling outcome verification
- Limitation: Cannot automatically verify if LLM's tool selection *logic* is optimal (e.g., why choose tool A over tool B when both could work)

### Replayability
**Assessment**: High
- Complete inference trace is recorded: [(tool_call, arguments, results)] tuples
- Given same tool implementations and initial query, the trace can be re-executed deterministically
- Paper provides training code and scripts to reproduce results (https://github.com/qiancheng0/ToolRL)
- GRPO training process is reproducible with released hyperparameters and reward configurations
- Tool execution is deterministic (same API call → same result), enabling faithful replay

### Faithfulness Risk
**Assessment**: Moderate
- **Strength**: Tool execution forces grounding - model cannot answer without actually invoking tools and receiving outputs
- **Strength**: Reward design penalizes "fake" tool calls (format reward ensures proper syntax, correctness reward validates outcomes)
- **Risk**: Model can still learn superficial patterns (e.g., imitating "but wait" cues from SFT data without genuine reasoning, as shown in Figure 1)
- **Risk**: Model may misinterpret tool outputs or aggregate results incorrectly (paper notes SFT failures where models "fail to reject inappropriate tools")
- **Mitigation**: RL training with fine-grained rewards reduces faithfulness risk compared to SFT by rewarding actual tool effectiveness, not just imitation
- Compared to Quadrant I: Lower faithfulness risk due to mandatory tool execution and outcome-based rewards

### Robustness
**Assessment**: Moderate
- **Tool Failure Sensitivity**: System depends on tools working correctly; API failures, rate limits, or incorrect tool outputs can derail reasoning chains
- **Domain Generalization**: Tested on diverse benchmarks (BFCL, Bamboogle, API-Bank) covering different tool types and task domains; shows strong generalization (+17% over base)
- **Strength**: Modular tool design allows swapping individual tools without retraining the entire system
- **Strength**: RL training with diverse tool scenarios improves robustness to unfamiliar tool combinations (paper highlights generalization to "unseen scenarios")
- **Limitation**: Performance may degrade with tools significantly different from training distribution (e.g., tools with very different parameter schemas)
- **Reward Design Impact**: Fine-grained reward decomposition (format + correctness + efficiency) provides stable learning signal across different tool types

### Cost/Latency
**Assessment**: Moderate-High
- **Tool Budget**: Multiple tool calls per query (exact number varies by task complexity); paper doesn't specify maximum but implies multi-step reasoning
- **Training Cost**: RL training (GRPO/PPO) is more expensive than SFT; requires multiple rollouts per batch for group-relative advantage estimation
- **Inference Cost**: Each tool call incurs API latency (search, code execution, external APIs); cumulative latency for multi-step reasoning
- **Comparison**: More expensive than single-pass LLM inference, but cheaper than end-to-end training of specialized tool-use models
- **Efficiency Reward**: Paper mentions rewarding "concise, correct, and efficient" behavior, suggesting awareness of cost trade-offs

### Security
**Assessment**: Moderate Risk
- **Tool Sandboxing**: Tool execution (especially code interpreters) requires careful sandboxing to prevent malicious code execution; paper doesn't explicitly mention safeguards
- **API Authentication**: Tool calls to external APIs (search, databases) require credential management; potential for credential leakage if not handled properly
- **Prompt Injection**: Tools that accept user-generated input (e.g., web search with query parameters) could be vulnerable to injection attacks; paper doesn't discuss protection mechanisms
- **Data Privacy**: Tool calls may send user queries to external services (search engines, APIs); potential privacy concerns depending on tool implementation
- **Mitigation**: Reward design could penalize unsafe tool calls, but paper doesn't explicitly address security in reward formulation

---

## Failure Modes

1. **Superficial Tool Imitation without Genuine Reasoning**: As shown in Figure 1, SFT-trained models can learn to imitate superficial cues (e.g., "but wait", excessive tool calls) without engaging in genuine deep thinking or tool selection logic. While RL mitigates this, poorly designed rewards could still lead to "reward hacking" where models learn to maximize reward without actual tool effectiveness.

2. **Incorrect Tool Selection or Parameter Specification**: The model may select inappropriate tools for a given task or specify incorrect parameters, leading to useless or misleading tool outputs. Paper notes that SFT models "fail to reject inappropriate tools," and while RL improves this, tool selection errors remain a risk, especially for unfamiliar task types.

3. **Cascading Errors from Early Tool Failures**: Early incorrect tool calls can lead the reasoning down unproductive paths with no recovery mechanism. If the first tool call returns irrelevant results, subsequent reasoning steps may compound the error. Paper doesn't explicitly address error recovery or backtracking strategies.

4. **Over-Reliance on Coarse-Grained Rewards**: If reward design is too coarse (e.g., only answer correctness), the model may learn to produce correct answers through lucky guesses rather than robust tool-use strategies. Paper emphasizes the importance of fine-grained reward decomposition to avoid this pitfall.

5. **Tool Execution Failures and Error Handling**: Tools may fail due to API errors, timeouts, or invalid inputs. If the model lacks robust error handling strategies (e.g., retry logic, fallback tools), a single tool failure can derail the entire reasoning chain. Paper doesn't extensively discuss error handling in training data or reward design.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across all benchmarks)
- [x] Step Correctness (implicitly via tool call format reward and correctness reward)
- [ ] Evidence Attribution (not explicitly measured)
- [x] Trace Replayability (demonstrated via released code and training scripts)
- [x] Robustness (tested via generalization to unseen scenarios and task types)
- [x] Cost/Latency (discussed qualitatively via reward trends, not quantified)
- [x] Other: Format adherence (format reward), tool selection quality (implicit in correctness reward)

### Benchmarks
- **BFCL (Berkeley Function Calling Leaderboard)**: Multi-turn function calling benchmark testing tool selection and parameter specification
- **Bamboogle**: Multi-hop QA benchmark requiring search tool use and information aggregation
- **API-Bank**: Benchmark for API call correctness and task completion across diverse API types
- **ToolACE**: Tool use benchmark (mentioned in passing as part of training data)
- **Hammer**: Tool use benchmark (mentioned in passing as part of training data)
- **xLAM**: Tool use dataset (mentioned in passing as part of training data)

### Key Results
- **BFCL**: ToolRL (GRPO Cold Start) achieves 58.38% (Qwen2.5-7B), outperforming Raw (46.20%) and SFT400 (52.98%) by significant margins
- **Bamboogle**: ToolRL achieves 72.00% (Qwen2.5-7B), compared to Raw (44.00%) and SFT400 (60.00%) - a 12 point gain over SFT
- **API-Bank**: ToolRL achieves 67.00% (Qwen2.5-7B), outperforming Raw (63.15%) and SFT400 (64.66%)
- **Average Improvement**: +17% over base models, +15% over SFT models across all benchmarks
- **Reward Trends**: Format reward and correctness reward both increase rapidly during training (Figure 2, right), indicating stable learning
- **Generalization**: Strong performance on unseen scenarios and task objectives (qualitative results mentioned in paper)
- **Emergent Behaviors**: Models exhibit proactiveness and metacognitive reasoning (e.g., self-correction, tool rejection) without explicit training

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (GRPO and PPO)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Reward design study for general-purpose tool learning** (systematic exploration of reward types, scales, granularity, dynamics)

### Data Collection
- **Training Data**: Combination of ToolACE, Hammer, and xLAM datasets (mentioned in GitHub repository)
- **Cold-Start Models**: SFT400 and SFT4K variants used as initialization for RL training
- **Reward Signals**: 
  - Format reward: Binary or continuous signal for tool call syntax adherence
  - Correctness reward: Binary signal for answer correctness (answer matching)
  - Dynamic scaling: Reward magnitudes adjusted during training to facilitate learning transitions
- **No Process Labels**: Unlike process supervision approaches, ToolRL doesn't require step-by-step correctness labels; rewards are computed from final outcomes and format adherence
- **GRPO-Specific**: Group-relative advantage estimation requires multiple rollouts per query to compute within-group relative quality

---

## Connections to Other Work

### Builds On
- **RL for Reasoning**: R1-like models (Guo et al., 2025; Team et al., 2025) demonstrating RL's effectiveness for complex reasoning
- **Tool-Integrated Reasoning (TIR)**: Prior work on LLMs interacting with external tools (search engines, calculators, code interpreters) in multi-step loops
- **RL Algorithms**: Group Relative Policy Optimization (GRPO) from Shao et al. (2024) and Proximal Policy Optimization (PPO) from Schulman et al. (2017)
- **Tool-Use Training**: SFT-based approaches (Chen et al., 2023a; Zeng et al., 2024; Chen et al., 2024; Acikgoz et al., 2025) that generate tool-use trajectories offline then fine-tune

### Related To
- **Search-R1** (Jin et al., 2025): RL for search tool use in QA settings (narrower scope than ToolRL's general-purpose tool learning)
- **TORL** (Li et al., 2025b): RL for code tool use in math problem-solving (narrower scope than ToolRL)
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), DoraemonGPT (MCTS + structured memory)
- **Quadrant IV Approaches**: ViperGPT (program synthesis for vision tools), VisProg (visual programming)

### Influenced
- **Need to check citations** (paper from Apr 2025, NeurIPS 2025): Potential follow-ups in RL-based tool learning, reward design for agent training
- **Code Repository**: https://github.com/qiancheng0/ToolRL provides baseline for future research on RL for tool use

---

## Quotes & Key Insights

> "Unlike textual reasoning, which primarily involves deduction and inference from static text, TIR additionally demands the model's ability to select appropriate tools, interpret intermediate outputs, and adaptively refine its trajectory on the fly."

> "Designing effective reward signals to guide learning through this complexity remains an open and underexplored challenge."

> "Longer reasoning trace is not inherently better and length rewards can degrade performance."

> "Dynamic reward scale helps models transition smoothly from simple to complex behaviors."

> "Finegrained reward decomposition leads to more stable and effective learning."

**Key Insight**: ToolRL demonstrates that **reward design is the critical bottleneck** for RL-based tool learning, not the RL algorithm itself. The paper's systematic exploration reveals that naive reward designs (e.g., length rewards, coarse answer matching) can degrade performance, while carefully crafted fine-grained rewards (format + correctness + dynamic scaling) enable stable, effective learning.

**Critical Observation**: The comparison between SFT and RL (Figure 1) reveals a fundamental limitation of imitation-based training: SFT models learn to superficially imitate "deep thinking" cues without genuine reasoning. RL with outcome-based rewards mitigates this by directly optimizing for tool effectiveness, not just trajectory similarity.

**Survey-Relevant Point**: ToolRL exemplifies Quadrant II's core strength: **structured tool traces + execution feedback enable verifiable, generalizable tool-use capabilities**. Unlike Quadrant I (pure text), the tool execution provides concrete grounding. Unlike Quadrant IV (full program synthesis), the natural language + tool call format is more flexible and easier to train with RL.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [x] Section 5 (Learning & Alignment) - as example of RL for tool-use training
- [ ] Section 6 (Evaluation & Benchmarks)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future) - reward design challenges for tool learning

### Narrative Role

ToolRL serves as a **representative example** of Quadrant II, demonstrating:

1. **Structured Tool Traces as Verifiable Representation**: Unlike free-form CoT (Quadrant I), the tool call traces provide explicit, executable structure that can be replayed and validated

2. **RL Training with Execution Feedback**: Each tool call produces concrete outcomes that inform reward computation, enabling outcome-based optimization rather than imitation-based training

3. **Reward Design as Critical Challenge**: The paper's core contribution highlights a key Quadrant II challenge: designing fine-grained rewards that properly credit tool selection, parameter specification, and reasoning quality

4. **Trade-offs in Quadrant II Design**:
   - **Pros**: Higher grounding strength (tool execution), replayability (structured traces), generalization (RL vs SFT)
   - **Cons**: Higher cost (multiple tool calls per query), tool failure sensitivity, reward design complexity

5. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (tool execution) but more complex (tool orchestration)
   - vs Quadrant III (Text + Execution): More structured (explicit tool calls) but less formal (not full programs)
   - vs Quadrant IV (Structured + Execution): More flexible (natural language + tools) but less rigorous (no programmatic guarantees)

### Comparison Points

**Excels at**:
- Grounding strength (mandatory tool execution)
- Replayability (structured tool call logs)
- Generalization (RL training outperforms SFT by 15%)
- Reward design methodology (systematic exploration of 4 dimensions)

**Fails at**:
- Full automation of verification (tool selection logic still opaque)
- Cost efficiency (multiple tool calls per query)
- Error handling (no explicit backtracking or recovery mechanisms)
- Security (no discussion of tool sandboxing or injection protection)

---

## Notes

### Follow-up Items
- [ ] Verify exact NeurIPS 2025 paper ID and page numbers (currently arXiv preprint)
- [ ] Review code repository for implementation details (reward functions, hyperparameters)
- [ ] Check citations for follow-up work on RL for tool learning (paper from Apr 2025)
- [ ] Compare with other Quadrant II candidates (VideoAgent, DoraemonGPT) to confirm anchor selection

### Questions
- What is the exact reward formulation for format reward and correctness reward?
- How does the dynamic reward scaling schedule work (e.g., linear increase, exponential decay)?
- What is the average number of tool calls per query across different benchmarks?
- How does ToolRL handle tool execution errors (timeouts, API failures, invalid inputs)?
- What is the training compute budget for GRPO vs PPO vs SFT?

### Clarification on Quadrant Placement
The placement in Quadrant II (not IV) is because:
- Representation is structured (tool call traces with arguments and results) but **reasoning trace is natural language** (CoT + tool calls)
- Tools are invoked via natural language commands with structured parameters, not full program synthesis
- No complete program generation like ViperGPT (Quadrant IV)
- Best characterized as "Structured Traces (tool call logs) + Tool-Augmented Reasoning (natural language)"

---

## BibTeX

```bibtex
@article{qian2025toolrl,
  title={ToolRL: Reward is All Tool Learning Needs},
  author={Qian, Cheng and Acikgoz, Emre Can and He, Qi and Wang, Hongru and Chen, Xiusi and Hakkani-T{\"u}r, Dilek and Tur, Gokhan and Ji, Heng},
  journal={arXiv preprint arXiv:2504.13958},
  year={2025},
  url={https://arxiv.org/abs/2504.13958}
}
```

**Status**: ✅ Complete - Quadrant II Paper (RL for Tool Learning)
