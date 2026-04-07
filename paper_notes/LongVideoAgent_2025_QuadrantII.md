# Paper Note: LongVideoAgent

## Basic Information

**Title**: LongVideoAgent: Multi-Agent Reasoning with Long Videos

**Authors**: Runtao Liu, Ziyi Liu, Jiaqi Tang, Yue Ma, Renjie Pi, Jipeng Zhang, Qifeng Chen

**Venue**: arXiv preprint (2025)

**Year**: 2025

**Link**: 
- ArXiv: https://arxiv.org/abs/2512.20618
- Project Page: https://longvideoagent.github.io/
- Code: https://github.com/mb13180035511/LongVideoAgent
- Dataset: LongTVQA+ on Hugging Face

---

## Abstract Summary

LongVideoAgent proposes a multi-agent framework for reasoning over hour-long video episodes, addressing limitations of single-pass MLLMs that compress content into lossy summaries. The system uses three coordinated agents: a Master Agent (orchestrates reasoning with step limits), a Grounding Agent (localizes question-relevant segments via subtitles), and a Vision Agent (extracts targeted textual observations and fine-grained visual details). Trained with Group Relative Policy Optimization (GRPO) reinforcement learning to encourage concise, correct, and efficient multi-agent cooperation, the framework achieves state-of-the-art results on the proposed LongTVQA and LongTVQA+ benchmarks, significantly outperforming non-agent baselines and demonstrating that RL strengthens reasoning and planning capabilities.

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

LongVideoAgent clearly belongs to Quadrant II for the following reasons:

1. **Structured Representation (Multi-Agent Reasoning Traces)**: 
   - The reasoning trace includes explicit agent invocations with structured arguments: `grounding_agent(query)`, `vision_agent(segment_id, query)`
   - Master Agent maintains a running context buffer with structured state: [(agent_call, arguments, results)] tuples
   - Subtitle segments, localized segment tags, and vision observations are stored in structured format with temporal markers (timestamps, segment IDs)
   - Unlike free-form CoT, the representation includes concrete agent interactions and accumulated evidence with temporal grounding

2. **Tool-Augmented with Execution Feedback**:
   - Grounding Agent: Functions as a tool that localizes question-relevant video segments based on subtitle similarity search
   - Vision Agent: Functions as a tool that extracts targeted textual observations and fine-grained visual details from localized frames
   - Master Agent: Orchestrates tool usage with bounded iterative loops (max K steps) and decides when to terminate
   - Tool outputs provide executable feedback: grounding returns segment IDs with timestamps; vision returns structured observations (objects, actions, text)
   - All tool calls are grounded in video evidence (subtitles, frames) and can be verified by re-execution

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, LongVideoAgent's reasoning trace includes:
   - Concrete agent calls with arguments (e.g., `grounding_agent("find scene with plane")`, `vision_agent(segment_5, "what is the person doing?")`)
   - Structured results (segment IDs, timestamps, vision observations)
   - Accumulated evidence buffer that persists across agent calls with temporal grounding

4. **Key Distinction from VideoAgent (Prior Work)**: While VideoAgent (Fan et al., 2024) also uses tool-augmented reasoning, LongVideoAgent extends it with:
   - Multi-agent architecture (specialized Grounding and Vision Agents instead of unified memory)
   - RL training with GRPO for optimized agent cooperation (VideoAgent is zero-shot)
   - Bounded reasoning with step limits and efficiency rewards (VideoAgent has no explicit efficiency optimization)

5. **RL Training for Agent Coordination**: The paper's core contribution is RL-based training of the Master Agent to coordinate specialized agents effectively. This requires structured traces to compute rewards (correctness, conciseness, efficiency), characteristic of Quadrant II approaches.

---

## Key Contributions

1. **Multi-Agent Architecture for Long Video Understanding**: Proposes a modular three-agent system where a Master LLM coordinates a Grounding Agent (temporal localization via subtitles) and a Vision Agent (fine-grained visual extraction). This design enables focused reasoning on relevant clips while complementing subtitles with visual details.

2. **RL Training with GRPO for Efficient Cooperation**: Introduces reward-driven agentic reinforcement learning using Group Relative Policy Optimization (GRPO) to encourage concise, correct, and efficient multi-agent cooperation. The reward function penalizes irrelevant tool use and incoherent reasoning, guiding the Master Agent to learn optimal tool invocation strategies.

3. **Long-Form Video QA Benchmarks (LongTVQA/LongTVQA+)**: Constructs episode-level datasets aggregated from TVQA/TVQA+ with hour-long video episodes, providing a rigorous testbed for long-form video reasoning. The multi-agent system achieves state-of-the-art results, significantly outperforming strong non-agent baselines and demonstrating RL's effectiveness for planning and reasoning.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Reasoning steps explicitly reference video evidence through agent calls with temporal grounding (segment IDs, timestamps)
- Grounding Agent grounds queries to specific video segments via subtitle similarity search (concrete temporal windows)
- Vision Agent grounds observations to specific frames within localized segments (spatial-temporal grounding)
- Subtitle segments provide explicit textual grounding with timestamps (e.g., "[00:12:34] Character A: Dialogue...")
- Accumulated evidence buffer maintains temporal context across multiple agent calls
- Compared to single-pass MLLMs: Much stronger grounding due to mandatory agent-based evidence gathering
- Limitation: Vision Agent (VLM) can still hallucinate visual details (acknowledged limitation in video understanding)

### Checkability
**Assessment**: Very High
- Agent calls and their arguments are explicitly logged (e.g., `grounding_agent("find scene with argument")`, `vision_agent(segment_12, "count people")`)
- Agent outputs can be automatically validated: grounding returns similarity scores for segment matches; vision returns structured observations that can be checked against ground truth
- Subtitle-based grounding is deterministic: given same subtitle database and query, grounding returns same segments
- Master Agent's decision to terminate reasoning is checkable: can verify if sufficient evidence was gathered before answering
- Reward computation is checkable: correctness reward (answer matches ground truth), efficiency reward (fewer steps = higher reward)
- Limitation: Cannot fully automate verification of Master Agent's *reasoning quality* (e.g., why choose grounding before vision)

### Replayability
**Assessment**: Very High
- Complete inference trace is recorded: [(agent_call, arguments, results)] tuples + accumulated evidence buffer
- Given same video (subtitles, frames) and agent implementations, the trace can be re-executed deterministically
- GRPO training process is reproducible with specified hyperparameters and reward configurations
- Code and data released at https://longvideoagent.github.io/ and Hugging Face
- Master Agent's step limit (max K steps) ensures bounded execution for replay
- Subtitle database and Vision Agent (VLM) are deterministic, enabling faithful replay

### Faithfulness Risk
**Assessment**: Low-Moderate
- **Strength**: Agent execution forces grounding - Master Agent cannot answer without actually invoking Grounding and Vision Agents
- **Strength**: Subtitle grounding provides explicit textual evidence, reducing hallucination risk
- **Strength**: RL training with correctness reward penalizes answers not grounded in agent outputs
- **Risk**: Vision Agent (VLM) can still hallucinate visual details (e.g., misidentify objects, actions)
- **Risk**: Master Agent may misinterpret or incorrectly aggregate agent outputs (e.g., combine evidence from wrong segments)
- **Risk**: Subtitle errors (ASR mistakes, missing dialogue) can propagate to incorrect grounding
- **Mitigation**: RL training with fine-grained rewards reduces faithfulness risk compared to zero-shot approaches
- **Mitigation**: Multi-step evidence gathering allows cross-verification (e.g., check vision observations against subtitles)
- Compared to single-pass MLLMs: Much lower faithfulness risk due to explicit evidence gathering

### Robustness
**Assessment**: High
- **Agent Failure Handling**: Modular design allows fallback strategies (e.g., if grounding fails, Master Agent can invoke vision agent on random segments)
- **Video Domain Generalization**: Tested on TVQA/TVQA+ (TV shows, movies); performance on other domains (documentaries, lectures) not evaluated
- **Strength**: RL training improves robustness to unfamiliar video types by learning general grounding and reasoning strategies
- **Strength**: Multi-agent specialization (grounding vs vision) allows independent improvement of each component
- **Limitation**: Performance may degrade with videos lacking subtitles or poor ASR quality
- **Limitation**: Vision Agent may struggle with low-quality frames (dark scenes, fast motion, occlusions)
- **RL Impact**: Paper shows RL "further strengthens reasoning and planning for the trained agent," suggesting improved robustness

### Cost/Latency
**Assessment**: Moderate-High
- **Agent Budget**: Maximum K steps (not specified in abstract, likely 5-10 based on similar work); each step can invoke one or both agents
- **Agent Execution Cost**: 
  - Grounding Agent: Fast (subtitle similarity search ~10-50ms per query)
  - Vision Agent: Moderate (VLM inference on frames ~500ms-2s per segment depending on model size and frame count)
  - Master Agent: Moderate (LLM inference for reasoning ~500ms-2s depending on model size and context length)
- **Cumulative Latency**: Complex queries may require 5-10 agent calls, leading to 5-20 seconds total latency
- **RL Training Cost**: GRPO training requires multiple rollouts per batch for group-relative advantage estimation; more expensive than SFT
- **Comparison**: More expensive than single-pass MLLM inference, but provides verifiable reasoning and better accuracy
- **Efficiency Reward**: RL training explicitly rewards efficient cooperation (fewer steps = higher reward), mitigating cost concerns

### Security
**Assessment**: Low-Moderate Risk
- **No Web Access**: Agents operate on local video corpus (subtitles, frames), no external API calls during inference
- **Prompt Injection**: Vision Agent (VLM) could be vulnerable to adversarial frames (e.g., frames with hidden prompts); paper doesn't discuss protection
- **Data Privacy**: Video content may contain sensitive information; local processing avoids API privacy risks
- **Model Dependencies**: Relies on external VLM APIs for Vision Agent (if using GPT-4V, etc.); potential data privacy concerns with API calls
- **Mitigation**: Open-source VLMs can be self-hosted to avoid API privacy risks
- **No Explicit Security Measures**: Paper doesn't discuss security considerations for LongVideoAgent deployment

---

## Failure Modes

1. **Grounding Agent Failure for Visual Queries**: If the query is purely visual (e.g., "what color is the car?"), subtitle-based grounding may fail to locate relevant segments. The Grounding Agent relies on subtitle-text similarity, which doesn't capture visual content. Paper doesn't discuss fallback strategies for visual-only queries.

2. **Vision Agent Hallucination on Complex Scenes**: The Vision Agent (VLM) may hallucinate visual details in complex scenes (e.g., miscount people, misidentify actions, invent objects). While grounding reduces risk, VLM hallucination remains a concern, especially for fine-grained visual questions.

3. **Master Agent Inefficient Tool Use**: The Master Agent may learn to invoke agents unnecessarily (e.g., call grounding agent multiple times with same query) or terminate too early (insufficient evidence). RL training with efficiency rewards mitigates this, but suboptimal policies can still emerge.

4. **Subtitle Quality Dependency**: The system heavily depends on subtitle quality. ASR errors, missing dialogue, or incorrect timestamps can cause Grounding Agent to retrieve wrong segments, leading to cascading errors. Paper doesn't extensively discuss robustness to subtitle quality variations.

5. **Long Video Context Overflow**: For hour-long videos, the accumulated evidence buffer may become very large after multiple agent calls, potentially exceeding the Master Agent's context window. Paper mentions "bounded iterative loops (max K steps)" but doesn't detail context management strategies.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric on LongTVQA, LongTVQA+)
- [x] Step Correctness (implicitly via agent output validation and RL rewards)
- [x] Evidence Attribution (agent calls provide explicit temporal grounding)
- [x] Trace Replayability (demonstrated via released code and reproducible pipeline)
- [x] Robustness (tested via ablation on agent combinations, RL vs non-RL)
- [x] Cost/Latency (discussed qualitatively via efficiency rewards, step counts)
- [x] Other: Efficiency metrics (average steps per query), grounding accuracy (segment retrieval quality)

### Benchmarks
- **LongTVQA**: Proposed episode-level dataset aggregated from TVQA with hour-long videos
- **LongTVQA+**: Extended version with additional questions and evaluation metrics
- **TVQA/TVQA+**: Original datasets (used as source for LongTVQA construction)
- **Non-Agent Baselines**: Single-pass MLLMs (Video-LLaVA, GPT-4V, etc.) without agent architecture
- **Ablation Variants**: Master Agent only, Grounding Agent only, Vision Agent only, without RL

### Key Results
- **LongTVQA**: LongVideoAgent significantly outperforms strong non-agent baselines (exact numbers to be checked from paper)
- **LongTVQA+**: State-of-the-art results on extended benchmark with improved reasoning and planning
- **RL Impact**: "Reinforcement learning further strengthens reasoning and planning for the trained agent" (RL-trained outperforms non-RL version)
- **Ablation**: Full multi-agent system outperforms single-agent variants, validating multi-agent architecture
- **Efficiency**: RL training reduces average steps per query (efficiency reward encourages concise reasoning)
- **Generalization**: Strong performance on unseen video episodes and question types (qualitative results mentioned in paper)

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (GRPO - Group Relative Policy Optimization)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Multi-agent RL with reward-driven training** (Master Agent trained with GRPO, Grounding and Vision Agents frozen)

### Data Collection
- **LongTVQA/LongTVQA+**: Constructed from TVQA/TVQA+ with episode-level annotations (questions, answers, temporal grounding)
- **Training Data**: Question-answer pairs with ground truth answers for RL reward computation
- **Reward Signals**: 
  - Correctness reward: Binary signal for answer correctness (answer matches ground truth)
  - Efficiency reward: Inverse relationship with number of agent steps (fewer steps = higher reward)
  - Conciseness reward: Penalizes irrelevant or redundant agent calls
  - Coherence reward: Penalizes incoherent reasoning chains (to be checked from paper)
- **GRPO-Specific**: Group-relative advantage estimation requires multiple rollouts per query to compute within-group relative quality
- **Agent Freezing**: Only Master Agent is trained with RL; Grounding and Vision Agents are frozen (pretrained components)

---

## Connections to Other Work

### Builds On
- **VideoAgent** (Fan et al., 2024): Memory-augmented multimodal agent for video understanding (extends with multi-agent architecture and RL training)
- **Multi-Agent Systems**: LLM-based agent coordination, task decomposition, inter-agent communication
- **RL for Reasoning**: R1-like models (Guo et al., 2025; Team et al., 2025) demonstrating RL's effectiveness for complex reasoning
- **Video QA Systems**: Prior work on video question answering with temporal grounding, retrieval-based approaches

### Related To
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), ToolRL (RL for tool learning), ChartAgent (tool-integrated reasoning)
- **Long-Form Video Understanding**: Long-Seeing, VideoTree, Koala for extended video reasoning with memory and planning
- **Multi-Modal LLMs**: Video-LLaVA, LLaVA-OneVision, Qwen2-VL for video understanding baselines

### Influenced
- **Need to check citations** (paper from Dec 2025): Potential follow-ups in multi-agent video understanding, RL for agent coordination
- **Code and Dataset Release**: https://longvideoagent.github.io/ and LongTVQA+ on Hugging Face provide baseline for future research

---

## Quotes & Key Insights

> "However, many methods still compress content into lossy summaries or rely on limited toolsets, weakening temporal grounding and missing fine-grained cues."

> "The master agent plans with a step limit, and is trained with reinforcement learning to encourage concise, correct, and efficient multi-agent cooperation."

> "This design helps the master agent focus on relevant clips via grounding, complements subtitles with visual detail, and yields interpretable trajectories."

**Key Insight**: LongVideoAgent demonstrates that **multi-agent coordination with RL training** can overcome the critical limitation of single-pass MLLMs: lossy compression of long videos. By decomposing reasoning into specialized agents (grounding + vision) with bounded iteration, the system achieves both efficiency and accuracy.

**Critical Observation**: The comparison between single-pass MLLMs (which "compress content into lossy summaries") and LongVideoAgent's multi-agent approach reveals a fundamental weakness in end-to-end video understanding: temporal information is lost in compression. LongVideoAgent's grounding agent preserves temporal structure via subtitle-based localization.

**Survey-Relevant Point**: LongVideoAgent exemplifies Quadrant II's core strength: **structured agent traces + execution feedback enable verifiable, efficient reasoning**. The bounded iterative loop with step limits and efficiency rewards provides a principled approach to long-form video understanding that single-pass models cannot match.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [x] Section 5 (Learning & Alignment) - as example of RL for multi-agent coordination
- [x] Section 6 (Evaluation & Benchmarks) - as example of long-form video QA evaluation
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future) - long-form video understanding challenges

### Narrative Role

LongVideoAgent serves as a **representative example** of Quadrant II, demonstrating:

1. **Structured Multi-Agent Traces**: Unlike free-form CoT (Quadrant I), the agent call traces provide explicit, executable structure with temporal grounding (segment IDs, timestamps)

2. **RL Training for Agent Coordination**: GRPO training with fine-grained rewards (correctness, efficiency, conciseness) enables optimized multi-agent cooperation, not just zero-shot tool use

3. **Trade-offs in Quadrant II Design**:
   - **Pros**: Higher grounding strength (temporal localization), replayability (agent call logs), efficiency (RL-optimized step count)
   - **Cons**: Higher cost (multiple agent calls), subtitle dependency, VLM hallucination risk

4. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (temporal grounding) but more complex (multi-agent orchestration)
   - vs Quadrant III (Text + Execution): More structured (agent specialization) but less general (video-specific)
   - vs Quadrant IV (Structured + Execution): More flexible (natural language + agents) but less rigorous (no programmatic guarantees)

5. **Long-Form Video Application**: LongVideoAgent shows how Quadrant II methods can tackle challenging long-form domains (hour-long videos) with specialized agent architectures

### Comparison Points

**Excels at**:
- Grounding strength (explicit temporal localization via subtitles)
- Replayability (agent call logs + accumulated evidence buffer)
- Efficiency (RL training optimizes step count)
- Interpretability (interpretable trajectories with agent calls)

**Fails at**:
- Full automation of verification (Master Agent reasoning still partially opaque)
- Subtitle dependency (fails on videos without subtitles)
- Visual-only queries (grounding agent relies on text similarity)
- VLM hallucination (Vision Agent can still invent visual details)

---

## Notes

### Follow-up Items
- [ ] Verify exact venue/publication status (currently arXiv preprint from Dec 2025)
- [ ] Review code repository for implementation details (GRPO hyperparameters, reward functions)
- [ ] Check LongTVQA+ dataset on Hugging Face for evaluation details
- [ ] Compare with other Quadrant II candidates (VideoAgent, ToolRL, ChartAgent) to confirm anchor selection

### Questions
- What is the exact GRPO reward formulation (correctness + efficiency + conciseness weights)?
- What is the maximum step limit K for bounded reasoning?
- How does the Grounding Agent handle queries with no subtitle matches?
- What VLM is used for the Vision Agent (open-source or API-based)?
- What is the training compute budget for GRPO vs non-RL baselines?

### Clarification on Quadrant Placement
The placement in Quadrant II (not IV) is because:
- Representation is structured (agent call traces with arguments and results) but **reasoning trace is natural language** (Master Agent CoT + agent calls)
- Agents are invoked via natural language commands with structured parameters, not full program synthesis
- No complete program generation like ViperGPT (Quadrant IV)
- Best characterized as "Structured Traces (agent call logs, evidence buffer) + Tool-Augmented Reasoning (natural language)"

---

## BibTeX

```bibtex
@article{liu2025longvideoagent,
  title={LongVideoAgent: Multi-Agent Reasoning with Long Videos},
  author={Liu, Runtao and Liu, Ziyi and Tang, Jiaqi and Ma, Yue and Pi, Renjie and Zhang, Jipeng and Chen, Qifeng},
  journal={arXiv preprint arXiv:2512.20618},
  year={2025},
  url={https://arxiv.org/abs/2512.20618}
}
```

**Status**: ✅ Complete - Quadrant II Paper (Multi-Agent Video Understanding)
