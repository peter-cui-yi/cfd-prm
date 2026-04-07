# Paper Note: Optimus-1

## Basic Information

**Title**: Optimus-1: Hybrid Multimodal Memory Empowered Agents Excel in Long-Horizon Tasks

**Authors**: Zaijing Li, Yuquan Xie, Rui Shao, Gongwei Chen, Dongmei Jiang, Liqiang Nie

**Venue**: Conference on Neural Information Processing Systems (NeurIPS) 2024

**Year**: 2024

**Link**: 
- ArXiv: https://arxiv.org/abs/2408.03615
- Project Page: https://cybertronagent.github.io/Optimus-1.github.io/

---

## Abstract Summary

Optimus-1 proposes a Hybrid Multimodal Memory module to address challenges in long-horizon task completion in open worlds. The memory consists of (1) Hierarchical Directed Knowledge Graph (HDKG) that transforms world knowledge into explicit graph structures for efficient retrieval, and (2) Abstracted Multimodal Experience Pool (AMEP) that summarizes historical task execution information (environment, agent state, video frames, plans) for in-context learning. Built on top of this memory, Optimus-1 agent features Knowledge-Guided Planner (incorporates HDKG for planning), Experience-Driven Reflector (retrieves AMEP for reflection), and Action Controller (executes low-level actions). In Minecraft long-horizon tasks, Optimus-1 significantly outperforms existing agents (up to 30% improvement), exhibits near human-level performance on many tasks, and demonstrates strong generalization across MLLM backbones (2-6× improvement with memory).

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Structured Traces + Tools)

**Justification**: 

Optimus-1 clearly belongs to Quadrant II for the following reasons:

1. **Structured Representation (not pure text)**: 
   - **HDKG (Hierarchical Directed Knowledge Graph)**: Explicit graph structure D(V, E) where nodes V represent objects and directed edges E point to craftable materials. For object x, retrieves sub-graph Dj containing all required materials and relationships via topological sorting
   - **AMEP (Abstracted Multimodal Experience Pool)**: Structured storage with video buffer (1 fps filtering) + image buffer (window size 16, adaptive similarity-based updates) + MineCLIP features (video-text alignment) + textual sub-goals + environment info + agent state
   - This is fundamentally different from free-form CoT - the memory provides explicit, queryable structure for knowledge and experience

2. **Tool-Augmented with Execution Feedback**:
   - **Knowledge-Guided Planner**: Retrieves knowledge from HDKG (tool-like retrieval operation), generates sub-goal sequences g₁, g₂, ..., gₙ = pθ(o, t, pη(t)) where pη is retrieved sub-graph
   - **Experience-Driven Reflector**: Retrieves multimodal experience from AMEP (tool-like retrieval), categorizes reflection as COMPLETE/CONTINUE/REPLAN based on current state vs historical cases
   - **Action Controller (STEVE-1)**: Executes low-level mouse/keyboard actions ak = pπ(o, gi), interacts with Minecraft environment, provides execution feedback (success/failure, state updates)
   - Environment provides concrete feedback: task success rate, inventory changes, health/food status

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, Optimus-1's reasoning includes:
   - Explicit knowledge retrieval from HDKG (graph queries for crafting recipes)
   - Structured experience retrieval from AMEP (similarity-based case retrieval with MineCLIP features)
   - Environment feedback (Minecraft game state updates after actions)
   - Reflection outcomes (COMPLETE/CONTINUE/REPLAN decisions based on retrieved experiences)

4. **Key Distinction from Quadrant IV**: While structured, the representation is not a fully executable program. The MLLM (GPT-4V or alternatives) produces natural language planning and reflection, not code synthesis.

---

## Key Contributions

1. **Hybrid Multimodal Memory Module**: Proposes dual-component memory - HDKG for structured world knowledge (crafting recipes, object relationships) and AMEP for summarized multimodal experience (video frames, environment state, plans, success/failure cases)

2. **Knowledge-Guided Planner + Experience-Driven Reflector Architecture**: Planner incorporates HDKG knowledge for one-step complete planning (not iterative refinement), Reflector retrieves AMEP experiences for periodic reflection and error correction (COMPLETE/CONTINUE/REPLAN)

3. **Non-Parametric Learning via "Free Exploration-Teacher Guidance"**: Memory expands incrementally without parameter updates - agents explore randomly to fill HDKG/AMEP, then learn from teacher-provided knowledge for long-horizon tasks, enabling self-evolution across epochs

4. **Near Human-Level Performance on Minecraft Long-Horizon Tasks**: Outperforms all existing agents (GPT-3.5, GPT-4V, DEPS, Jarvis-1) by up to 30%, achieves 98.60% on Wood tasks (human: 100%), 46.69% on Iron tasks (human: 86.00%), demonstrates 2-6× improvement across MLLM backbones (Deepseek-VL, InternLM-XComposer2-VL)

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Moderate-High
- Planning is grounded in retrieved knowledge from HDKG (explicit crafting recipes, material requirements)
- Reflection is grounded in retrieved experiences from AMEP (historical cases with visual frames + state + outcomes)
- Action execution is grounded in environment feedback (Minecraft game state updates)
- Visual observation is directly used as condition in planning (not just textual description like Jarvis-1)
- However, MLLM can still hallucinate in planning/reflection phases (knowledge/experience retrieval is verifiable, but reasoning over them is not fully constrained)

### Checkability
**Assessment**: Moderate-High
- Knowledge retrieval from HDKG is checkable: retrieved sub-graph can be validated against crafting requirements
- Experience retrieval from AMEP is checkable: similarity scores (MineCLIP features) determine which cases are retrieved
- Reflection outcomes are explicitly categorized (COMPLETE/CONTINUE/REPLAN) and logged
- Action execution outcomes are verifiable via environment feedback (task success/failure, inventory changes)
- Limitation: Cannot automatically verify if MLLM's planning logic correctly uses retrieved knowledge/experience

### Replayability
**Assessment**: High
- Complete task execution trace is logged: sub-goal sequences, reflection decisions, action sequences, environment states
- Memory construction is deterministic given same exploration data (HDKG built from crafting knowledge, AMEP built from video summarization pipeline)
- Given same memory state and initial conditions, the agent behavior can be re-executed
- Paper provides detailed framework description (Section 2) with formulas for planning, reflection, action generation
- Code available at project page (https://cybertronagent.github.io/Optimus-1.github.io/)

### Faithfulness Risk
**Assessment**: Moderate
- **Strength**: Memory retrieval forces grounding - planner cannot plan without HDKG knowledge, reflector cannot reflect without AMEP experience
- **Strength**: Both successful and failed cases are stored in AMEP, providing balanced references (not just cherry-picked successes)
- **Risk**: MLLM can still misinterpret retrieved knowledge/experience (e.g., correctly retrieving recipe but planning wrong order)
- **Risk**: Experience retrieval relies on similarity scores - may retrieve irrelevant cases if MineCLIP features are not discriminative
- **Mitigation**: Periodic reflection catches errors early (not just at task completion)
- **Mitigation**: Reflection considers three scenarios (COMPLETE/CONTINUE/REPLAN) with explicit criteria
- Compared to Quadrant I: Lower faithfulness risk due to explicit memory grounding and environment feedback

### Robustness
**Assessment**: Moderate-High
- **MLLM Generalization**: Works across different MLLM backbones (GPT-4V, Deepseek-VL 7B, InternLM-XComposer2-VL) with 2-6× improvement (Figure 5a)
- **Memory Incremental Expansion**: Self-evolution through "free exploration-teacher guidance" shows consistent improvement across 4 epochs (Figure 5b)
- **Task Generalization**: Memory is task-agnostic - same HDKG/AMEP used across Wood/Stone/Iron/Gold/Diamond/Redstone/Armor task groups
- **Strength**: Plug-and-play memory module - can be added to any MLLM without parameter updates
- **Strength**: Both success and failure cases in AMEP improve robustness to distribution shift
- **Limitation**: Performance drops significantly on harder tasks (Diamond: 11.61%, Gold: 8.51%) - memory may not scale well to very long-horizon tasks

### Cost/Latency
**Assessment**: High
- **Memory Construction Cost**: 
  - HDKG: Requires knowledge extraction (crafting recipes) and graph construction
  - AMEP: Video buffering (1 fps) + image buffering (similarity computation with window 16) + MineCLIP feature extraction for all frames
- **Inference Cost**:
  - MLLM calls for planning (GPT-4V or alternatives) + reflection (periodic activation)
  - Experience retrieval: similarity search in AMEP pool
  - Knowledge retrieval: graph traversal in HDKG
  - Action execution: STEVE-1 low-level control (20 fps interaction)
- **Task Duration**: Average time varies by task group (Wood: 47.09s, Diamond: 1150.98s, Table 1)
- **Comparison**: More expensive than single-pass VLM, but justified by 30% improvement in success rate

### Security
**Assessment**: Low Risk
- **No Web Access**: Agent operates in closed Minecraft environment only
- **Tool Sandboxing**: Memory retrieval is read-only operation, action execution is constrained by game mechanics
- **Prompt Injection**: Not applicable in this domain (Minecraft environment, not open-ended interaction)
- **Data Contamination**: Memory is task-specific, experiences from different tasks are separated by similarity retrieval
- **API Dependencies**: Relies on MineCLIP for feature extraction, STEVE-1 for action execution - both are local models

---

## Failure Modes

1. **Knowledge Retrieval Failures**: If HDKG is incomplete or incorrectly constructed, planner will generate invalid plans. Example: missing recipe for diamond pickaxe leads to failed Diamond tasks.

2. **Experience Retrieval Mismatch**: AMEP retrieval relies on MineCLIP similarity - may retrieve irrelevant experiences if current situation doesn't match stored cases well. This can misguide reflection (e.g., retrieving success case when current situation is actually failing).

3. **Action Controller Limitations**: STEVE-1 (action controller) has limited instruction-following capability - paper notes weakness in complex tasks like "beat ender dragon" or "build a house". Low-level action failures propagate upward, causing sub-goal failures.

4. **Reflection Timing Sensitivity**: Reflector is "periodically activated" - if activation frequency is too low, errors may not be caught early enough; if too high, excessive overhead. Paper doesn't specify optimal timing.

5. **Memory Scalability**: As AMEP grows with more experiences, retrieval efficiency may degrade. Image buffer uses window size 16 and similarity-based filtering, but may still become bottleneck for very long task histories.

6. **Cascading Sub-Goal Failures**: Sub-goals are interdependent - failure in early sub-goal (e.g., mine cobblestone) halts execution of subsequent ones (e.g., craft stone pickaxe). Reflection can replan, but may not recover if root cause is action-level failure.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (task success rate - primary metric)
- [x] Step Correctness (implicitly via reflection COMPLETE/CONTINUE/REPLAN)
- [ ] Evidence Attribution (not explicitly measured)
- [x] Trace Replayability (demonstrated via case studies in Figure 4)
- [x] Robustness (tested via MLLM backbone ablation, memory ablation)
- [x] Cost/Latency (average steps and average time reported in Table 1)
- [ ] Other: Average Steps (AS), Average Time (AT)

### Benchmarks
- **Minecraft Long-Horizon Tasks**: 67 tasks across 7 groups (Wood, Stone, Iron, Gold, Diamond, Redstone, Armor)
  - Wood Group: Basic tools (wooden pickaxe, planks, etc.)
  - Stone Group: Stone tools (stone pickaxe, furnace, etc.)
  - Iron Group: Iron tools and armor (requires mining iron, smelting)
  - Gold Group: Gold tools (rare materials, complex crafting)
  - Diamond Group: Diamond tools (very rare, requires iron pickaxe)
  - Redstone Group: Redstone components (complex crafting chains)
  - Armor Group: Full armor sets (multiple crafting steps)
- **Human-Level Baseline**: 10 volunteers performing same tasks, average performance as reference

### Key Results
- **Wood Tasks**: 98.60% success rate (human: 100%), 47.09s average time (human: 31.08s), 841.94 steps (human: 621.59)
- **Stone Tasks**: 92.35% (human: 100%), 129.94s (human: 80.85s), 2518.88 steps (human: 1617.00)
- **Iron Tasks**: 46.69% (human: 86.00%), 651.33s (human: 434.38s), 6017.85 steps (human: 5687.60) - **outperforms human on efficiency**
- **Diamond Tasks**: 11.61% (human: 16.98%), 1150.98s (human: 744.82s) - **near human-level on hardest tasks**
- **Overall Average**: 22.26% across Iron/Gold/Diamond/Redstone/Armor (human: 36.41%) - closes gap significantly
- **vs Baselines**: Outperforms Jarvis-1 (16.89%) by 5.37%, DEPS (5.39%) by 16.87%, GPT-4V (0.00%) by 22.26%
- **MLLM Generalization**: Deepseek-VL + Memory: 73.0% Wood, 43.8% Stone (2-6× improvement over no memory)
- **Self-Evolution**: Performance improves across 4 epochs (Wood: 92.50% → 97.5%, Diamond: 4.66% → 9.6%)

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Non-Parametric Memory Learning + In-Context Learning with MLLMs**

### Data Collection
- **Free Exploration Phase**: Multiple Optimus-1 agents randomly initialized, explore random environments, acquire world knowledge through environmental feedback
  - Learn crafting recipes (e.g., "stone sword = wooden stick + 2 cobblestones") → stored in HDKG
  - Store successful and failed cases in AMEP (video frames, state, plans, outcomes)
  - Shared memory across agents for efficient filling
- **Teacher Guidance Phase**: Learn long-horizon tasks from teacher-provided knowledge
  - Example: "diamond sword = stick + 2 diamonds" added to HDKG
  - Perform complete long-horizon tasks, store experiences in AMEP
- **Memory Construction**:
  - HDKG: Graph construction from crafting knowledge (nodes = objects, edges = craftable materials)
  - AMEP: Video stream → video buffer (1 fps) → image buffer (window 16, similarity-based) → MineCLIP feature extraction → store with textual sub-goals, environment info, agent state
- **No Parameter Updates**: MLLM backbones (GPT-4V, Deepseek-VL, etc.) used as-is, memory is plug-and-play

---

## Connections to Other Work

### Builds On
- **Minecraft Agents**: MineCLIP (video-text alignment), STEVE-1 (low-level action controller), VPT (video pretraining)
- **LLM-Based Agents**: Voyager (skill library), DEPS (planning with feedback), Jarvis-1 (multimodal memory)
- **Memory-Augmented LLMs**: Textual memory (conversation history), parametric memory (fine-tuning)
- **Multimodal Large Language Models**: GPT-4V, Deepseek-VL, InternLM-XComposer2-VL

### Related To
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), AdaReasoner (tool orchestration with RL)
- **Voyager**: Also uses memory (skill library) in Minecraft, but Optimus-1 uses multimodal experience + knowledge graph vs Voyager's code-based skills
- **Jarvis-1**: Closest baseline - also uses multimodal memory in Minecraft, but Optimus-1 improves via structured HDKG + summarized AMEP (vs Jarvis-1's unsummarized storage)
- **DEPS**: Uses planning + reflection, but without multimodal memory - Optimus-1 adds visual experience retrieval

### Influenced
- **Need to check citations** (paper from NeurIPS 2024, Oct 2024): Potential follow-ups in memory-augmented agents, Minecraft agent research, multimodal experience replay

---

## Quotes & Key Insights

> "Building a general-purpose agent is a long-standing vision in the field of artificial intelligence. Existing agents have made remarkable progress in many domains, yet they still struggle to complete long-horizon tasks in an open world."

> "We attribute this to the lack of necessary world knowledge and multimodal experience that can guide agents through a variety of long-horizon tasks."

> "Different from the method of directly storing successful cases as experience, AMEP considers both successful and failed cases as references. This innovative approach of incorporating failure cases into in-context learning significantly enhances the performance of the agent."

**Key Insight**: Optimus-1 demonstrates that **structured hybrid memory (knowledge graph + multimodal experience pool)** can enable general-purpose MLLMs to perform complex long-horizon tasks in open worlds without parameter updates. The key is explicit knowledge representation (HDKG) for planning and rich experience retrieval (AMEP) for reflection.

**Critical Observation**: The ablation study (Table 2) reveals that **both knowledge and experience are crucial**: removing HDKG drops performance by 20% on average, removing AMEP drops by 12%, and removing both drops by ~80%. This shows that knowledge guides planning while experience enables error correction - they are complementary.

**Failure Case Analysis** (Figure 4): Without reflection, STEVE-1 gets stuck in loops (e.g., "fall into water", "drop in cave") with no recovery mechanism. With Experience-Driven Reflector retrieving AMEP cases, Optimus-1 recognizes failure patterns and replans, significantly improving success rate on long-horizon tasks.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [ ] Section 5 (Learning & Alignment) - as example of non-parametric memory learning
- [x] Section 6 (Evaluation & Benchmarks) - as example of embodied agent evaluation in Minecraft
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future) - as example of long-horizon task completion in open worlds

### Narrative Role

Optimus-1 serves as a **representative example** of Quadrant II with memory-augmented tool use in embodied agents, demonstrating:

1. **Structured Memory as Verifiable Representation**: Unlike free-form CoT (Quadrant I), the hybrid memory (HDKG + AMEP) provides explicit, queryable structure for both world knowledge and multimodal experience

2. **Tool-Augmented Reasoning with Environment Feedback**: Knowledge retrieval (HDKG queries) and experience retrieval (AMEP similarity search) act as tools, while Minecraft environment provides concrete execution feedback (success/failure, state updates)

3. **Memory Design for Long-Horizon Tasks**:
   - **HDKG**: Efficient knowledge representation via directed graph (crafting recipes as edges)
   - **AMEP**: Summarized experience storage (video buffering + similarity filtering + MineCLIP features)
   - **Non-Parametric Learning**: Memory expands without fine-tuning, enabling plug-and-play deployment

4. **Trade-offs in Quadrant II Design**:
   - **Pros**: High grounding strength (knowledge + experience retrieval), replayability (complete task logs), robustness to hallucination (memory constrains planning/reflection), generalization across MLLMs
   - **Cons**: High cost (memory construction + MLLM calls + environment interaction), dependency on memory quality (incomplete HDKG → invalid plans), scalability challenges (AMEP retrieval efficiency)

5. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (memory retrieval + environment feedback) but more complex (memory construction overhead)
   - vs Quadrant III (Text + Execution): More structured (explicit memory representations) but less formal (natural language planning)
   - vs Quadrant IV (Structured + Execution): More flexible (MLLM-based reasoning) but less rigorous than program synthesis

### Comparison Points

**Excels at**:
- Grounding strength (explicit knowledge/experience retrieval)
- Long-horizon task completion (30% improvement over baselines)
- MLLM generalization (2-6× improvement across backbones)
- Near human-level performance on many tasks

**Fails at**:
- Very hard tasks (Diamond: 11.61% vs human 16.98%) - memory may not scale to extremely long horizons
- Action-level failures (STEVE-1 limitations) - memory can't compensate for poor low-level control
- Cost efficiency (high memory construction + inference overhead)

---

## Notes

### Follow-up Items
- [ ] Verify exact NeurIPS 2024 camera-ready status
- [ ] Check if code repository is public (project page may have code)
- [ ] Review citations for follow-up work on memory-augmented agents
- [ ] Compare with Voyager (also Minecraft agent with memory) to understand relative strengths

### Questions
- What is the exact reflection activation frequency (how often is Experience-Driven Reflector triggered)?
- How does AMEP retrieval scale with memory size (thousands of experiences)?
- What similarity threshold is used for MineCLIP feature matching in AMEP?
- How is the graph traversal performed in HDKG (BFS, DFS, topological sort)?
- Can the memory generalize to entirely new Minecraft tasks not seen in exploration/teacher phases?

### Clarification on Quadrant Placement
The placement in Quadrant II (not IV) is because:
- Representation is structured (knowledge graph + experience pool) but **planning and reflection are natural language** (MLLM-generated)
- Memory retrieval is tool-like (graph queries, similarity search) but not programmatic code execution
- No complete program synthesis - agent produces natural language sub-goals and reflection decisions
- Best characterized as "Structured Traces (memory state) + Tool-Augmented Reasoning (knowledge/experience retrieval + environment interaction)"

---

## BibTeX

```bibtex
@inproceedings{li2024optimus1,
  title={Optimus-1: Hybrid Multimodal Memory Empowered Agents Excel in Long-Horizon Tasks},
  author={Li, Zaijing and Xie, Yuquan and Shao, Rui and Chen, Gongwei and Jiang, Dongmei and Nie, Liqiang},
  booktitle={Conference on Neural Information Processing Systems (NeurIPS)},
  year={2024},
  url={https://arxiv.org/abs/2408.03615}
}
```

**Status**: ✅ Complete - Quadrant II Paper (Memory-Augmented Embodied Agent)
