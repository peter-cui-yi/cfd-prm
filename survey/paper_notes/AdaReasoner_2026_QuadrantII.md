# Paper Note: AdaReasoner

## Basic Information

**Title**: AdaReasoner: Dynamic Tool Orchestration for Iterative Visual Reasoning

**Authors**: Mingyang Song, Haoyu Sun, Jiawei Gu, Linjie Li, Luxin Xu, Ranjay Krishna, and Yu Cheng

**Venue**: International Conference on Learning Representations (ICLR) 2026

**Year**: 2026

**Link**: 
- ArXiv: https://arxiv.org/abs/2601.18631
- Homepage: https://adareasoner.github.io
- Code: https://github.com/ssmisya/AdaReasoner
- Models and Data: https://huggingface.co/AdaReasoner

---

## Abstract Summary

AdaReasoner proposes a family of multimodal models that learn tool use as a general reasoning skill through (i) a scalable data curation pipeline for long-horizon, multi-step tool interactions; (ii) Tool-GRPO, a reinforcement learning algorithm optimizing tool selection and sequencing based on end-task success; and (iii) an adaptive learning mechanism that dynamically regulates tool usage. The model exhibits strong tool-adaptive behaviors: autonomously adopting beneficial tools, suppressing irrelevant ones, and adjusting tool usage frequency based on task demands, achieving state-of-the-art performance across challenging benchmarks (+24.9% average improvement on 7B base model, surpassing GPT-5 on VSP and Jigsaw tasks).

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

AdaReasoner clearly belongs to Quadrant II for the following reasons:

1. **Structured Representation (not pure text)**: 
   - Tool-augmented reasoning trajectories are structured as sequences of state-action-observation tuples: τ = {(s₀, a₀, o₀), (s₁, a₁, o₁), ..., (s_T, a_T, o_T)}
   - Each tool call has defined structure: tool name, parameters (with specific types), and output format (e.g., POINT returns coordinates, OCR returns text with bounding boxes)
   - Multi-turn reasoning follows structured format with special tokens delimiting tool calls
   - This is fundamentally different from free-form CoT - the trajectory provides explicit, verifiable tool call logs

2. **Tool-Augmented with Execution Feedback**:
   - Seven core visual tools: POINT (object localization), DRAW2DPATH (path visualization), ASTAR (pathfinding), DETECTBLACKAREA (black region detection), INSERTIMAGE (image composition), CROP (region extraction), OCR (text extraction)
   - Tools provide executable feedback: tool outputs are concrete and verifiable (e.g., coordinates, cropped images, detected text)
   - Tool execution results are fed back into the reasoning loop as observations
   - RL training uses tool execution success rate as part of reward signal

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, AdaReasoner's reasoning trace includes:
   - Concrete tool calls with structured arguments (e.g., `{"name": "Point", "parameters": {"image": "img_1", "description": "Elf"}}`)
   - Tool execution results (e.g., `{"points": [{"x": 352.0, "y": 160.0}], "image_dimensions_pixels": {"width": 512, "height": 512}}`)
   - Multi-turn trajectory state that persists across tool calls

4. **Key Distinction from Quadrant IV**: While structured, the representation is not a fully executable program like ViperGPT (which generates Python code). The MLLM produces natural language reasoning + structured tool calls, not a complete program trace.

---

## Key Contributions

1. **Scalable Data Curation Pipeline for Multi-Turn Tool Planning**: Automatically synthesizes high-quality, multi-turn trajectories with reflection/backtracking scenarios and explicit tool failure cases, teaching models not just what tools to call but why and how to reason between them

2. **Tool-GRPO (Multi-Turn Tool Group Relative Policy Optimization)**: Extends GRPO framework with multi-turn reward accumulation (format reward × (tool reward + accuracy reward)) and adaptive tool reward that encourages reliable tool usage under uncertainty

3. **Adaptive Learning for Improved Generalization**: Randomizes tool names and parameter names at token level, and paraphrases tool descriptions at semantic level, preventing overfitting to fixed identifiers and enabling zero-shot generalization to unseen tool definitions

4. **State-of-the-Art Performance with Tool-Adaptive Behaviors**: 7B model achieves +24.9% average improvement, outperforming GPT-5 and Claude Sonnet 4 on structured reasoning tasks (VSP: 96.60% vs 80.10%, Jigsaw: 88.60% vs 84.50%), while exhibiting emergent behaviors like adopting beneficial tools, discarding irrelevant ones, and modulating tool-use frequency

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Reasoning steps explicitly reference visual evidence through tool calls
- POINT tool grounds queries to specific pixel coordinates (x, y)
- Tool outputs are grounded in concrete visual operations (e.g., CROP returns cropped image, OCR returns detected text with bounding boxes)
- Multi-turn trajectories maintain grounding through accumulated observations
- However, MLLM can still misinterpret tool outputs (acknowledged in paper - model may incorrectly aggregate tool results)

### Checkability
**Assessment**: High
- Tool calls and their arguments are explicitly logged in structured JSON format
- Tool outputs can be validated: coordinate accuracy, image manipulation success, OCR correctness
- Tool execution success rate is tracked as explicit metric (Table 6: 98.50% success on Jigsaw, 90.04% on VStar)
- Trajectory format is enforced by format reward in RL training
- Limitation: Cannot automatically verify if MLLM's tool selection logic is optimal (e.g., why choose POINT over DETECTBLACKAREA)

### Replayability
**Assessment**: High
- Complete inference trace is recorded: trajectory τ contains [(state, action, observation)] tuples
- Given same tool implementations and initial state, the trace can be re-executed deterministically
- Paper provides full training algorithm (Tool Cold Start + Tool GRPO) with detailed reward design
- Tool definitions are explicitly specified (Table 1 + Appendix A.1)
- Code and models available at https://adareasoner.github.io

### Faithfulness Risk
**Assessment**: Moderate
- **Strength**: Tool outputs force grounding - MLLM cannot answer without executing tools first
- **Strength**: Explicit tool failure cases in training data teach model to fall back on intrinsic capabilities
- **Risk**: MLLM can still misinterpret tool outputs (e.g., correctly calling tools but drawing wrong conclusion from results)
- **Risk**: Tool quality affects reasoning - poor tool execution (e.g., failed object detection) propagates errors
- **Mitigation**: Adaptive reward design treats tools as fallback under uncertainty rather than mandatory step
- **Mitigation**: Reflection/backtracking data in training teaches model to validate hypotheses and learn from intermediate failures
- Compared to Quadrant I: Much lower faithfulness risk due to explicit tool grounding

### Robustness
**Assessment**: High
- **Tool Generalization**: Model demonstrates zero-shot adaptation to unseen tools (e.g., A* tool introduced only at inference time achieves 94.5% invocation success rate)
- **Task Generalization**: Tool-planning skills learned from Jigsaw transfer to unseen VSP and WebQA tasks (Table 4: Rnd TC + Rnd TG achieves 78.91 on unseen VSP vs 28.09 baseline)
- **Tool Definition Robustness**: Model maintains performance under randomized tool names and descriptions (Table 6: 98.50% tool success rate under new tool definitions)
- **Strength**: Adaptive learning mechanism (token-level randomization + semantic paraphrasing) prevents overfitting to specific tool interfaces
- **Strength**: Modular tool design allows swapping individual components without retraining entire system

### Cost/Latency
**Assessment**: Moderate-High
- **Tool Budget**: Multiple tool calls per sample (Table 6: 3.54 calls/sample on Jigsaw, 2.35 on VStar for AdaReasoner 7B)
- **Training Cost**: Two-stage training (Tool Cold Start SFT + Tool GRPO RL) with multi-turn trajectory generation
- **Inference Cost**: MLLM calls for each tool decision + tool execution time (some tools like ASTAR require computation)
- **Tool Types**: Mix of lightweight offline tools (POINT, CROP) and computationally intensive expert-model tools (OCR, ASTAR pathfinding)
- **Comparison**: More expensive than single-pass VLM inference, but cheaper than end-to-end training of large models

### Security
**Assessment**: Low Risk
- **No Web Access**: Tools operate on local images and predefined functions only
- **Tool Sandboxing**: Tool calls are structured and validated by format reward
- **Prompt Injection**: RL training with format enforcement reduces risk of malformed tool calls
- **Data Contamination**: Tool outputs are task-specific, reducing cross-task contamination
- **API Dependencies**: No external API calls mentioned - all tools appear to be self-contained

---

## Failure Modes

1. **Tool Output Misinterpretation**: MLLM may incorrectly interpret or aggregate tool results. Example: Model correctly calls tools but draws wrong conclusion from coordinate outputs or visual comparisons.

2. **Cascading Tool Selection Errors**: Early incorrect tool choices can lead reasoning down unproductive paths. If initial POINT call misses target object, subsequent tool calls will gather misleading information. Paper addresses this via reflection/backtracking training data.

3. **Tool Failure Propagation**: When tools fail or return erroneous results (explicitly included in training), model must fall back on intrinsic capabilities. Without proper fallback training, failures would cascade.

4. **Over-Reliance on Tools**: Model might invoke tools even when unnecessary (e.g., calling ASTAR for verification task where it's irrelevant). Figure 3a shows model initially explores A* for verification but learns to suppress usage through RL.

5. **Generalization to Complex Tool Interactions**: While model generalizes to unseen tools, performance on tasks requiring complex tool coordination (e.g., multi-step image manipulation + reasoning) may degrade if training data lacks sufficient examples.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across all benchmarks)
- [x] Tool Execution Success Rate (Succ. % in Table 3, 6)
- [x] Tool Usage Frequency (CPS - calls per sample in Table 3, 6)
- [x] Step Correctness (implicitly via tool reward in RL training)
- [x] Evidence Attribution (tool outputs serve as explicit evidence)
- [x] Trace Replayability (demonstrated via trajectory examples in Appendix)
- [x] Robustness (tested via tool ablation, randomization, cross-task transfer)
- [x] Cost/Latency (discussed via CPS and turn counts)

### Benchmarks
- **VSP (Visual Spatial Planning)**: Navigation and verification tasks on grid maps with obstacles (custom VSPO + standard VSP benchmarks)
- **Jigsaw**: Visual compositionality tasks on COCO images (Jigsaw-COCO + BLINK-J subset)
- **GUIQA**: Fine-grained GUI understanding (GUIChat + WebMMU Agentic Action subset)
- **VStar**: General visual search benchmark for out-of-domain evaluation
- **HRBench**: High-resolution perception benchmark

### Key Results
- **VSP**: 97.64% (7B model) - outperforms GPT-5 (80.10%) and Claude Sonnet 4 (56.27%)
- **Jigsaw**: 88.60% (7B model) - outperforms GPT-5 + Tools (84.50%) and Qwen2.5-VL 72B + Tools (61.50%)
- **GUIQA (GUIChat)**: 73.91% - competitive with Gemini 2.5 flash (83.05%) given smaller model size
- **WebMMU (Agentic Action)**: 72.15% - outperforms GPT-5 (80.49%) on some subsets
- **VStar**: 70.68% - best among Qwen-based models without dedicated visual-search module
- **Average Improvement**: +24.9% over base Qwen2.5-VL 7B across all benchmarks
- **Tool Adaptation**: A* tool introduced at inference achieves 94.5% invocation success rate (Table 3)
- **Cross-Task Generalization**: Model trained on Jigsaw + Rnd TC/TG transfers to unseen VSP (78.91 vs 28.09 baseline)

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Tool Cold Start stage with multi-turn trajectories)
- [x] Process Supervision (Tool-GRPO with multi-turn reward accumulation)
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (Tool-GRPO - Group Relative Policy Optimization for tool use)
- [ ] Cold-start + RL for tool-use (exactly this: TC + TG pipeline)
- [ ] Verifier-guided Training
- [ ] Other: **Adaptive Learning with Tool Randomization**

### Data Collection
- **Tool Cold Start Trajectory Data**: Automatically synthesized multi-turn trajectories with:
  - Abstract trajectory design (perception-planning-verification logic for VSP, trial-and-error for Jigsaw, focus-then-extract for GUIQA)
  - Reflection and backtracking scenarios (explicit self-correction steps)
  - Tool failure cases (tools return erroneous results, teaching fallback strategies)
  - Programmatic tool execution to populate concrete inputs/outputs
  - LLM-generated CoT reasoning connecting steps
- **Tool-GRPO Data**: Multi-turn rollouts with group-relative advantage estimation
- **Adaptive Learning Data**: Token-level randomization (tool/parameter names → random strings like Func_X7a2) + semantic paraphrasing (tool descriptions rephrased by Gemini 2.5 Flash)
- **Base Models**: Qwen2.5-VL-3B-Instruct and Qwen2.5-VL-7B-Instruct

---

## Connections to Other Work

### Builds On
- **GRPO (Group Relative Policy Optimization)**: DeepSeek-R1 style rule-based RL for reasoning
- **Visual Tool-Use Agents**: VisProg (visual programming), ViperGPT (code generation), LLaVA-Plus (tool server)
- **Multimodal Reasoning with RL**: Vision-R1, Video-R1, Pixel-Reasoner, DeepEyes
- **Tool-Augmented MLLMs**: CogCoM (chain-of-manipulation), TACO (tool-action-object dataset)

### Related To
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), DoraemonGPT (MCTS + structured memory)
- **Single-Tool RL Methods**: DeepEyes (crop-based search), Pixel-Reasoner (curiosity-driven pixel reasoning) - AdaReasoner extends to multi-tool coordination
- **Code-Based Tool Use**: Thyme, PyVision - AdaReasoner uses simpler atomic tools instead of code generation
- **End-to-End VLMs**: Qwen2.5-VL, InternVL3 (contrasted as training-heavy alternatives without explicit tool use)

### Influenced
- **Need to check citations** (paper from ICLR 2026, Jan 2026 submission): Potential follow-ups in adaptive tool planning, RL for tool coordination, zero-shot tool generalization

---

## Quotes & Key Insights

> "Effective reasoning, therefore, hinges on knowing which tools to use, when to invoke them, and how to compose them over multiple steps, even when faced with new tools or new tasks."

> "AdaReasoner exhibits strong tool-adaptive and generalization behaviors: it autonomously adopts beneficial tools, suppresses irrelevant ones, and adjusts tool usage frequency based on task demands, despite never being explicitly trained to do so."

> "Our empirical analysis reveals that the effectiveness of visual tools stems from their complementary roles in enhancing perception, verification, and planning... This shifts the bottleneck from internal reasoning accuracy to effective tool planning."

**Key Insight**: AdaReasoner demonstrates that **RL-guided tool orchestration** can transform small MLLMs (7B) into state-of-the-art reasoners that outperform much larger proprietary models (GPT-5, Claude Sonnet 4) on structured visual tasks. The key is treating tool use as a **learnable reasoning skill** rather than tool-specific behavior.

**Critical Observation**: The adaptive learning mechanism (randomizing tool names + paraphrasing descriptions) is crucial for generalization. Table 4 shows Rnd TC + Rnd TG achieves 78.91 on unseen VSP vs 28.00 for non-randomized TC + TG, proving that decoupling tool-use logic from specific identifiers enables true zero-shot adaptation.

**Emergent Tool-Use Behaviors** (Figure 3):
1. **Learning to Adopt Beneficial Tools**: ASTAR usage increases to >1.0 call/sample for navigation task
2. **Learning to Discard Irrelevant Tools**: ASTAR usage decays to ~0 for verification task where it's distractor
3. **Learning to Modulate Frequency**: POINT tool maintained at ~3.2 calls/sample for navigation vs ~1.0 for verification

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [x] Section 5 (Learning & Alignment) - as example of RL for tool-use training
- [x] Section 6 (Evaluation & Benchmarks) - as example of comprehensive tool-use evaluation
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future) - as example of adaptive tool generalization

### Narrative Role

AdaReasoner serves as a **representative example** of Quadrant II with RL-guided tool orchestration, demonstrating:

1. **Structured Tool-Use Trajectories as Verifiable Representation**: Unlike free-form CoT (Quadrant I), the tool-augmented trajectory provides explicit, executable tool call logs that can be replayed and checked

2. **RL Optimization for Multi-Turn Tool Planning**: Tool-GRPO extends beyond SFT-based tool use (Quadrant I/II boundary) by optimizing tool selection and sequencing based on end-task success with multi-turn reward accumulation

3. **Adaptive Tool Generalization**: The adaptive learning mechanism (token randomization + semantic paraphrasing) enables zero-shot transfer to unseen tool definitions and tasks - a key advancement over fixed tool-use policies

4. **Trade-offs in Quadrant II Design**:
   - **Pros**: High grounding strength (explicit tool outputs), replayability (complete trajectory logs), robustness to hallucination (tool execution constrains reasoning), zero-shot tool adaptation
   - **Cons**: Higher cost (multiple tool calls per sample), dependency on tool quality, training complexity (two-stage TC + TG pipeline)

5. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (tool execution) but more complex (tool coordination)
   - vs Quadrant III (Text + Execution): More structured (explicit tool APIs) but less formal (natural language reasoning)
   - vs Quadrant IV (Structured + Execution): More flexible (natural language + tools) but less rigorous than full program synthesis

### Comparison Points

**Excels at**:
- Grounding strength (explicit tool outputs with coordinates, images, text)
- Replayability (complete tool call logs with structured arguments/results)
- Tool adaptation (zero-shot generalization to unseen tools/tasks)
- Sample efficiency (7B model outperforms 72B+ models with tools)

**Fails at**:
- Full automation of verification (MLM tool selection logic still opaque)
- Cost efficiency (3.54 calls/sample on Jigsaw)
- Open-ended tasks (tool gains smaller on general VQA vs structured reasoning)

---

## Notes

### Follow-up Items
- [ ] Verify exact ICLR 2026 acceptance status (paper dated Jan 2026, may be under review)
- [ ] Check if code repository is public (project page mentions code available)
- [ ] Review citations for follow-up work on adaptive tool planning
- [ ] Compare with other Quadrant II candidates (VideoAgent, DoraemonGPT) to confirm relative strengths

### Questions
- What is the exact training data size for Tool Cold Start stage?
- How does Tool-GRPO sample multi-turn trajectories (batch size, rollout count)?
- What are the compute requirements for training AdaReasoner (GPU hours)?
- How does the model handle conflicting tool outputs (e.g., POINT vs OCR disagree)?
- Can the adaptive learning mechanism generalize to entirely new tool categories (e.g., adding video analysis tools)?

### Clarification on Quadrant Placement
The placement in Quadrant II (not IV) is because:
- Representation is structured (tool call trajectories with defined I/O) but **reasoning trace is natural language** (CoT + tool calls)
- Tools are invoked via structured JSON commands, not programmatic code generation
- No complete program synthesis like ViperGPT (Quadrant IV)
- Best characterized as "Structured Traces (tool call logs) + Tool-Augmented Reasoning (natural language + RL optimization)"

---

## BibTeX

```bibtex
@inproceedings{song2026adareasoner,
  title={AdaReasoner: Dynamic Tool Orchestration for Iterative Visual Reasoning},
  author={Song, Mingyang and Sun, Haoyu and Gu, Jiawei and Li, Linjie and Xu, Luxin and Krishna, Ranjay and Cheng, Yu},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2026},
  url={https://arxiv.org/abs/2601.18631}
}
```

**Status**: ✅ Complete - Quadrant II Paper (RL-Guided Tool Orchestration)
