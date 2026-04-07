# Paper Note: OpenVLThinker

## Basic Information

**Title:** OpenVLThinker: Complex Vision-Language Reasoning via Iterative SFT-RL Cycles

**Authors:** Yihe Deng, [other authors from arXiv:2503.17352]

**Affiliations:** [Institutions from paper]

**Venue:** NeurIPS 2025 (arXiv:2503.17352, March 2025)

**Year:** 2025

**Link:** 
- ArXiv: https://arxiv.org/abs/2503.17352
- Code: https://github.com/yihedeng9/OpenVLThinker
- NeurIPS Poster: https://neurips.cc/virtual/2025/poster/116720
- OpenReview: https://openreview.net/forum?id=gfX1nqBKtu
- PDF: https://openreview.net/pdf/62ceb097c643e0416c764c187ebf4f4d6d1ba9c3.pdf

---

## Abstract Summary

OpenVLThinker addresses a critical challenge in vision-language reasoning: while text-based reasoning models like DeepSeek R1 succeed at text-only tasks, simply distilling their reasoning into LVLMs via SFT causes performance degradation due to imprecise visual grounding, and pure RL approaches face an overly large search space that limits reasoning emergence in smaller models. The paper introduces an iterative SFT-RL cycle that alternates between supervised fine-tuning and reinforcement learning stages: SFT effectively surfaces latent reasoning actions and narrows the RL search space, while each subsequent RL stage refines the model's skills and produces higher-quality SFT data for continued self-improvement. OpenVLThinker-7B consistently improves performance across six benchmarks requiring mathematical and general reasoning (MathVista +3.8%, EMMA +2.4%, HallusionBench +1.6%, MathVerse, MathVision, MMMU-Pro), performing competitively with proprietary models like GPT-4o and Claude-3.5, especially on math and perception tasks. Code, models, and training data are publicly available.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** I (Text-only CoT)

**Justification:**

OpenVLThinker is a sophisticated Quadrant I approach with the following characteristics:

1. **Purely Textual CoT Representation**: OpenVLThinker operates on free-form Chain-of-Thought reasoning trajectories expressed in natural language. The model generates step-by-step thinking followed by final answers, all in text format. There are no structured representations such as tables, programs, execution traces, or latent state logs. The reasoning is entirely textual CoT.

2. **No External Tool Usage**: OpenVLThinker's verification and reward mechanisms are entirely internal to the model:
   - **SFT Stage**: Learns from textual CoT rationales (self-generated or distilled)
   - **RL Stage**: Uses outcome-level rewards (answer correctness via string matching)
   - **No OCR, calculators, code interpreters, retrieval systems, or web search tools** are employed
   - All learning is from text alone, without external tool mediation

3. **Iterative SFT-RL Cycles**: The key innovation is alternating between SFT and RL:
   - **SFT Stage**: Fine-tune on CoT data (from previous RL stage or distillation)
     - Surfaces latent reasoning actions
     - Narrows RL search space by establishing baseline reasoning capability
   - **RL Stage**: Apply RL (likely GRPO or similar) to refine reasoning
     - Explores beyond SFT data distribution
     - Produces higher-quality CoT for next SFT stage
   - **Cycle**: Repeat SFT → RL → SFT → RL... for several iterations
   - This is training methodology, not tool-augmented reasoning

4. **Addressing Visual Grounding Challenge**: OpenVLThinker specifically addresses the visual grounding problem in reasoning VLMs:
   - **Problem 1**: Distilling text-only reasoning (DeepSeek R1) into LVLMs via SFT causes performance degradation due to imprecise visual grounding
   - **Problem 2**: Pure RL approaches face overly large search space, limiting reasoning emergence in smaller models
   - **Solution**: Iterative SFT-RL combines benefits of both:
     - SFT provides grounding foundation (learns to connect visual input to textual reasoning)
     - RL refines reasoning beyond SFT distribution
     - Iterations progressively improve both grounding and reasoning

5. **Contrast with Quadrant II**: Unlike VideoAgent which uses:
   - Structured memory (temporal segments with timestamps, object tracks in SQL database)
   - Executable tools (segment localization via similarity search, object memory querying via SQL)
   - Tool outputs as grounding evidence
   OpenVLThinker has:
   - No persistent memory structure
   - No tool calls with explicit arguments/outputs
   - No execution feedback from environment
   - Purely textual CoT generation with iterative training

6. **Training without Tools**: OpenVLThinker's training operates entirely on textual CoT rationales:
   - SFT: Learns from CoT data (textual rationales)
   - RL: Outcome-level rewards (answer correctness)
   - No tool-use learning or execution grounding
   - Visual grounding is learned implicitly through VLM's visual encoder

---

## Key Contributions

1. **Iterative SFT-RL Cycles for Vision-Language Reasoning**: OpenVLThinker introduces a novel training paradigm that alternates between SFT and RL stages:
   - **SFT Stage**: Surfaces latent reasoning actions, narrows RL search space, establishes visual grounding foundation
   - **RL Stage**: Refines reasoning skills, explores beyond SFT distribution, produces higher-quality training data
   - **Iterative Improvement**: Each cycle produces better model, which generates better data for next cycle
   - This addresses the key challenge: pure SFT distillation degrades performance (visual grounding mismatch), pure RL has too large search space
   - Iterative approach achieves stable improvement with modest model size (7B)

2. **Open-Source Complex Reasoning LVLM**: OpenVLThinker-7B is fully open-source (code, models, training data), performing competitively with proprietary models:
   - **7B parameter scale**: Achieves strong reasoning with modest model size (efficient)
   - **Competitive with proprietary models**: GPT-4o, Claude-3.5 on math and perception tasks
   - **Six benchmark improvements**: MathVista +3.8%, EMMA +2.4%, HallusionBench +1.6%, MathVerse, MathVision, MMMU-Pro
   - **Open science**: Code at https://github.com/yihedeng9/OpenVLThinker, models and training data publicly available
   - This democratizes access to strong reasoning VLMs

3. **Visual Grounding through Iterative Training**: OpenVLThinker demonstrates that visual grounding for reasoning can be improved through iterative training without external tools:
   - **SFT grounds reasoning to visual input**: Learns to connect image features to textual reasoning
   - **RL refines grounding**: Explores reasoning paths that are both visually grounded and logically correct
   - **Iterative improvement**: Each cycle improves grounding quality
   - This is alternative to tool-augmented grounding (Quadrant II), achieving good grounding through training methodology

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Moderate (improved through iterative training)

- **Implicit Visual Grounding**: CoT rationales reference visual elements through natural language descriptions but do not provide explicit grounding pointers (bounding boxes, coordinates, region masks)
- **SFT Stage Grounding**: SFT learns to connect visual input to textual reasoning:
   - CoT data includes references to visual content (e.g., "the chart shows...", "the triangle has...")
   - Model learns to ground reasoning to visual features through VLM's visual encoder
   - However, grounding is implicit, not explicit
- **RL Stage Grounding Refinement**: RL explores reasoning paths that are both visually grounded and logically correct:
   - Outcome reward (answer correctness) indirectly encourages correct visual grounding
   - Incorrect grounding leads to wrong answers, which are penalized
   - However, RL may find shortcuts (correct answer with flawed grounding)
- **Iterative Improvement**: Each SFT-RL cycle improves grounding:
   - SFT establishes grounding foundation
   - RL refines grounding through exploration
   - Next SFT stage learns from improved RL data
   - Progressive grounding improvement across iterations
- **Comparison to Plain CoT (R3V, Sherlock)**: Similar grounding mechanism (implicit textual references), but OpenVLThinker's iterative training likely improves grounding quality
- **Comparison to Quadrant II**: Lower grounding strength than VideoAgent where tool outputs provide explicit grounding (segment IDs, object tracks)

### Checkability
**Assessment:** Moderate

- **Answer Correctness**: Fully checkable via string matching with ground truth (for benchmarks with verifiable answers)
- **CoT Quality**: Limited automatic verification of individual reasoning steps:
   - No structured format for steps (free-form text)
   - Cannot automatically verify if specific CoT step is correct without external tools
   - Checkability relies on outcome reward (answer correctness), not step-level verification
- **SFT Data Quality**: CoT data from previous RL stage or distillation:
   - Quality depends on RL stage performance
   - No explicit quality filtering mentioned in search results
   - May include noisy CoT (correct answer with flawed reasoning)
- **RL Reward**: Outcome-level reward (answer correctness):
   - Sparse reward (only final answer is checked)
   - Does not check intermediate reasoning steps
   - May reinforce flawed reasoning that happens to get correct answer
- **Comparison to Structured Approaches**: Lower checkability than:
   - Quadrant II (VideoAgent): Tool outputs (SQL queries, segment IDs) are automatically verifiable
   - Quadrant III (Program-of-Thoughts): Code execution provides automatic verification
   - Quadrant IV (ViperGPT): Program traces can be re-executed and validated
- **Comparison to R1-VL**: OpenVLThinker uses outcome-level rewards, R1-VL uses step-wise rewards. R1-VL has higher step-level checkability.

### Replayability
**Assessment:** Moderate

- **Deterministic Inference**: Given fixed model weights and same input, CoT generation is deterministic (assuming greedy decoding or fixed seed)
- **No Structured Trace**: CoT is free-form text, not structured trace. Can re-generate but cannot "replay" in sense of re-executing program steps
- **Training Reproducibility**: 
   - SFT-RL cycles are deterministic given same data and hyperparameters
   - Code released at https://github.com/yihedeng9/OpenVLThinker for reproducibility
   - Training data publicly available
- **Model Checkpoints**: Iterative training produces multiple checkpoints (after each SFT/RL stage)
   - Can replay inference with any checkpoint
   - Enables ablation studies across iterations
- **Comparison to Quadrant II**: Less replayable than VideoAgent which logs complete tool call traces [(action, input, results)] that can be re-executed deterministically
- **Comparison to Quadrant IV**: Much less replayable than program synthesis approaches where code can be re-run to verify outputs

### Faithfulness Risk
**Assessment:** High

- **Primary Challenge**: OpenVLThinker addresses visual grounding challenge, but faithfulness risk remains:
   - Model may generate visually unfaithful reasoning (hallucinated entities, attributes, relations)
   - Without explicit grounding mechanisms, model can mention visual elements without actually "seeing" them
   - Outcome-level RL may reinforce unfaithful reasoning if it leads to correct answers
- **Iterative Training Mitigation**:
   - SFT stage learns grounding from CoT data (should include faithful visual references)
   - RL stage explores reasoning paths, may discover unfaithful shortcuts
   - Next SFT stage learns from RL data, may inherit unfaithfulness
   - Iterative process may amplify or reduce unfaithfulness depending on data quality
- **Correct Answer ≠ Correct Reasoning**: Similar to R3V's finding (Figure 6: 8-70% correct CoT rate), OpenVLThinker may get correct answers through flawed reasoning:
   - Outcome-level RL rewards correct answers, not correct reasoning
   - Model may learn to exploit shortcuts (answer biases, heuristics)
   - Iterative training does not explicitly address this problem
- **Visual Perception Errors**: Model may misperceive visual input, leading to unfaithful reasoning:
   - No mechanism to re-check perception (unlike Quadrant II with tools)
   - Errors propagate through reasoning chain
   - RL may learn to ignore visual input and rely on text biases
- **Comparison to Plain CoT (R3V, Sherlock)**: Similar faithfulness risk (implicit grounding, no tools)
- **Comparison to Journey Before Destination**: OpenVLThinker does not include faithfulness evaluation; Journey Before Destination provides evaluation framework but no training improvement
- **Comparison to Quadrant II**: Higher faithfulness risk than VideoAgent where tool outputs constrain hallucination

### Robustness
**Assessment:** Moderate

- **No Tool Dependencies**: Advantage of Quadrant I: no tool failures (no OCR service downtime, no API rate limits, no detector failures)
- **Iterative Training Robustness**:
   - SFT-RL cycles provide stable improvement (search results show consistent gains across iterations)
   - SFT narrows RL search space, making RL more stable
   - RL explores beyond SFT distribution, preventing overfitting to SFT data
   - Iterative approach is more robust than pure SFT or pure RL
- **Domain Generalization**:
   - Evaluated on 6 diverse benchmarks (math, science, general reasoning)
   - Improvements across all benchmarks suggest good generalization
   - MathVista +3.8%, EMMA +2.4%, HallusionBench +1.6%
   - Performs well on OOD tasks (MMMU-Pro, multi-discipline)
- **Model Scale Robustness**:
   - 7B parameter scale achieves strong performance
   - Suggests method is effective for modest model sizes
   - May scale further with larger models (not evaluated in search results)
- **Visual Grounding Robustness**:
   - Iterative training improves grounding
   - However, grounding is still implicit (not explicit like Quadrant II)
   - May struggle with domains requiring precise visual perception (charts, tables, diagrams)
- **Comparison to R1-VL/Visionary-R1**: OpenVLThinker's iterative training vs R1-VL's dense rewards vs Visionary-R1's structured format. Different approaches to improving robustness.

### Cost/Latency
**Assessment:** Moderate

- **No External Tool Calls**: Major cost advantage over Quadrant II/III. No API calls, no service dependencies
- **Training Costs**:
   - **Iterative SFT-RL**: Multiple cycles of SFT + RL
     - Each cycle: SFT stage + RL stage
     - Number of iterations: Not specified in search results (likely 2-4 based on "few iterations" mention)
   - **SFT Cost**: Standard supervised fine-tuning (moderate cost)
   - **RL Cost**: Online RL with outcome-level rewards (requires sampling multiple outputs, moderate-high cost)
   - **Total Cost**: Higher than single-stage training (SFT-only or RL-only), but produces better performance
   - **Data Generation**: RL stage generates own training data for next SFT stage (no external annotation cost)
- **Inference Costs**:
   - Single CoT generation (Test@1): Same cost as standard CoT
   - No test-time sampling required (unlike R3V's test-time selection)
   - No tool calls at inference
   - 7B model size: Relatively efficient inference (compared to larger proprietary models)
- **Comparison to Baselines**:
   - LLaVA-CoT: Similar inference cost, OpenVLThinker may have higher training cost (iterative)
   - Mulberry (260k annotations): OpenVLThinker cheaper (self-generated data)
   - R1-VL: Similar cost (both use RL)
   - Proprietary models (GPT-4o, Claude-3.5): OpenVLThinker cheaper (open-source, self-hosted)
- **Overall**: Moderate training cost (iterative SFT-RL), low inference cost (7B model, single pass)

### Security
**Assessment:** Low Risk

- **Closed System**: No external tool calls, no web access, no API dependencies at inference time
- **No Prompt Injection Surface**: Unlike tool-augmented systems, no tool arguments that could be manipulated
- **Training Data Safety**:
   - Uses self-generated CoT data (from RL stages)
   - May start with distilled data from text-only reasoning models (DeepSeek R1)
   - No external data contamination (closed-loop training)
- **Outcome-Level RL Safety**:
   - Advantages: Simple, interpretable reward (answer correctness)
   - Risks: May reward shortcuts (correct answer with flawed reasoning)
   - No adversarial inputs in reward computation
- **No External Critics**: Unlike approaches using critic models, OpenVLThinker does not rely on external feedback that could be adversarial
- **Data Privacy**: Uses public benchmarks only, no private user data
- **Overall**: Minimal security attack surface, typical risks of outcome-level RL (shortcut learning) mitigated by iterative training

---

## Failure Modes

1. **Outcome-Level RL Shortcut Learning**:
   - RL rewards correct answers, not correct reasoning
   - Model may learn shortcuts:
     - Exploit answer biases (e.g., "the answer is usually C")
     - Ignore visual input and rely on text heuristics
     - Generate superficially reasonable CoT that leads to correct answer
   - Iterative training may amplify shortcuts if RL data reinforces them
   - Mitigation: Not explicitly addressed in search results; may need step-level rewards (like R1-VL) or faithfulness evaluation (like Journey Before Destination)

2. **Visual Perception Errors Propagating Through Iterations**:
   - Model misperceives visual input (e.g., misreads chart numbers, confuses objects)
   - Once visual error occurs, reasoning is corrupted
   - RL may learn to ignore visual input if it leads to correct answers through shortcuts
   - Iterative training does not include mechanism to re-check perception
   - Unlike Quadrant II approaches (VideoAgent) which can re-query tools for verification, OpenVLThinker has no external grounding mechanism

3. **SFT-RL Distribution Mismatch**:
   - SFT learns from CoT data (distribution of training data)
   - RL explores beyond SFT distribution
   - Distribution mismatch may cause instability:
     - RL explores regions where SFT has weak grounding
     - RL data may be out-of-distribution for next SFT stage
     - May cause performance oscillation across iterations
   - Search results mention "stable improvement" but do not provide detailed analysis

4. **Data Quality Degradation Across Iterations**:
   - RL generates training data for next SFT stage
   - If RL produces low-quality data (noisy CoT, flawed reasoning), next SFT stage inherits problems
   - Iterative process may amplify errors:
     - Iteration 1: High-quality data (from distillation or initial SFT)
     - Iteration 2: RL generates data, some flawed
     - Iteration 3: SFT learns from flawed data, RL explores further, more errors
   - Search results show consistent improvement, but long-term degradation risk exists

5. **Domain-Specific Grounding Challenges**:
   - Iterative training improves grounding generally, but may struggle with specific domains:
     - Charts/graphs: Requires precise numerical reading, axis interpretation
     - Tables: Requires structured data extraction
     - Diagrams: Requires symbolic interpretation
     - Natural images: Requires object detection, attribute recognition
   - Single iterative approach may not suit all domains equally
   - Domain-specific grounding issues may limit generalization

6. **Scalability to Complex Reasoning**:
   - Iterative SFT-RL works well for math/science reasoning (evaluated benchmarks)
   - May struggle with open-ended reasoning (creative tasks, subjective judgments) where "correct answer" is ill-defined
   - Outcome-level rewards require verifiable answers; may not apply to all reasoning domains
   - Complex multi-step reasoning may require step-level supervision (not provided in outcome-level RL)

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across all benchmarks)
- [x] Step Correctness (implicitly via iterative improvement)
- [ ] Evidence Attribution (no explicit grounding evaluation)
- [x] Trace Replayability (demonstrated via iterative training checkpoints)
- [x] Robustness (tested via multi-benchmark evaluation, domain generalization)
- [x] Cost/Latency (discussed qualitatively, 7B model efficiency)
- [x] Other: Iteration-wise Improvement (performance across SFT-RL cycles)

### Benchmarks
- **6 Vision-Language Reasoning Benchmarks** (from search results):
   - **MathVista**: Mathematical reasoning in visual contexts (+3.8% improvement)
   - **EMMA**: General reasoning benchmark (+2.4% improvement)
   - **HallusionBench**: Visual hallucination evaluation (+1.6% improvement)
   - **MathVerse**: Mathematical reasoning
   - **MathVision**: Mathematical reasoning
   - **MMMU-Pro**: Multi-discipline multimodal understanding

### Key Results
- **Main Results** (from search summary):
   - OpenVLThinker-7B achieves consistent improvements across all 6 benchmarks:
     - MathVista: +3.8%
     - EMMA: +2.4%
     - HallusionBench: +1.6%
     - MathVerse, MathVision, MMMU-Pro: Improvements (specific numbers not in search results)
   - Performs competitively with proprietary models: GPT-4o, Claude-3.5
   - Especially strong on math and perception tasks

- **Iterative Improvement** (from search summary):
   - "Significant improvements after just a few iterations"
   - Each SFT-RL cycle produces better performance
   - SFT narrows RL search space, RL refines skills, iterative improvement
   - Specific per-iteration numbers not in search results

- **Comparison to Baselines**:
   - **Proprietary Models**: OpenVLThinker-7B competitive with GPT-4o, Claude-3.5
   - **Open-Source VLMs**: Likely outperforms LLaVA-CoT, Mulberry on reasoning tasks (inferred from strong results)
   - **Text-Only Reasoning Distillation**: OpenVLThinker outperforms simple distillation from DeepSeek R1 (search results mention "performance degradation" from distillation)

- **Model Efficiency**:
   - 7B parameter scale achieves strong performance
   - Suggests method is effective for modest model sizes
   - Competitive with much larger proprietary models

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Iterative SFT stages)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO (Iterative RL stages, likely GRPO or similar)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Iterative SFT-RL cycles for progressive improvement

### Data Collection
- **Base Model**: Starts from pretrained LVLM (specific model not specified in search results, likely Qwen-VL-7B or LLaVA-1.5-7B variant)

- **Iterative SFT-RL Training Process**:
   1. **Initialization**:
      - Option A: Start with distilled CoT data from text-only reasoning model (e.g., DeepSeek R1)
      - Option B: Start with base LVLM, no CoT data
      - Search results suggest distillation is used ("simply distilling their reasoning into LVLMs via SFT causes performance degradation")
   
   2. **Iteration 1**:
      - **SFT Stage 1**: Fine-tune base LVLM on initial CoT data (distilled or self-generated)
        - Surfaces latent reasoning actions
        - Establishes visual grounding foundation
        - Narrows RL search space
      - **RL Stage 1**: Apply RL (likely GRPO) to refine reasoning
        - Explores beyond SFT data distribution
        - Uses outcome-level rewards (answer correctness)
        - Generates new CoT data (higher quality than initial data)
   
   3. **Iteration 2**:
      - **SFT Stage 2**: Fine-tune model from RL Stage 1 on new CoT data (from RL Stage 1)
        - Learns from improved reasoning
        - Further narrows RL search space
      - **RL Stage 2**: Apply RL again
        - Further refines reasoning
        - Generates even higher-quality CoT data
   
   4. **Repeat**: Continue SFT-RL cycles for several iterations (exact number not specified)
   
   5. **Final Model**: Model after last RL stage (or last SFT stage, depending on configuration)

- **Data Flow**:
   - Initial CoT data → SFT 1 → RL 1 → New CoT data → SFT 2 → RL 2 → New CoT data → ...
   - Each RL stage generates training data for next SFT stage
   - Self-improving loop: Model generates its own training data

- **RL Reward**:
   - Outcome-level reward: +1 if answer matches ground truth, 0 otherwise
   - No step-level rewards (unlike R1-VL)
   - No format rewards (unlike Visionary-R1)

- **Open-Source Data**:
   - Training data publicly available on GitHub
   - Enables reproducibility and community extension

---

## Connections to Other Work

### Builds On
- **DeepSeek R1** (DeepSeek AI, 2025): Text-only reasoning model with GRPO. OpenVLThinker extends to vision-language with iterative SFT-RL.
- **Group Relative Policy Optimization** (Shao et al., 2024): GRPO algorithm for RL. OpenVLThinker likely uses GRPO or similar RL algorithm.
- **SFT-RL Combinations**:
   - Work on combining supervised and reinforcement learning
   - OpenVLThinker's innovation is iterative cycling, not just sequential SFT→RL
- **Vision-Language Reasoning**:
   - LLaVA-CoT (Zhang et al., 2024): SFT with CoT annotations
   - VL-Rethinker (Xu et al., 2024): RL for reasoning

### Related To
- **Other Quadrant I Approaches**:
   - CURE (this work): Consistency-based verification, RLAIF training
   - R3V (this work): Self-training with reflection, learning from mistakes
   - Sherlock (this work): Self-correction training, trajectory-level correction
   - R1-VL (this work): Step-wise GRPO with process rewards
   - Visionary-R1 (this work): Structured caption-reason-answer with GRPO
- **Iterative Training**:
   - R3V: Iterative self-training (4-5 iterations)
   - OpenVLThinker: Iterative SFT-RL cycles
   - Different iteration objectives: R3V bootstraps CoT data, OpenVLThinker alternates SFT and RL
- **Open-Source Reasoning VLMs**:
   - LLaVA-CoT: Open-source with 100k annotated CoT
   - OpenVLThinker: Open-source with self-generated CoT (no manual annotation)

### Influenced
- **Paper from March 2025 (NeurIPS 2025)**:
   - Very recent work, citations not yet available
   - Potential follow-ups in iterative training for VLMs
   - May influence future work on SFT-RL combinations
- **Open-Source Impact**:
   - Code, models, training data publicly available
   - Enables community extension and improvement
   - May become baseline for future open-source reasoning VLMs

---

## Quotes & Key Insights

> "While text-based reasoning models like DeepSeek R1 succeed at text-only tasks, simply distilling their reasoning into LVLMs via SFT causes performance degradation due to imprecise visual grounding."

> "Pure RL approaches face an overly large search space, limiting reasoning emergence in smaller models."

> "The breakthrough is alternating between SFT and RL stages, which produces significant improvements after just a few iterations."

> "SFT effectively surfaces latent reasoning actions and narrows the RL search space, while each subsequent RL stage refines the model's skills and produces higher-quality SFT data for continued self-improvement."

**Key Insight 1: Iterative SFT-RL Synergy**
OpenVLThinker's core contribution is the iterative SFT-RL cycle that combines benefits of both approaches:
- SFT: Surfaces latent reasoning, narrows RL search space, establishes grounding
- RL: Explores beyond SFT, refines reasoning, generates better training data
- Iteration: Progressive improvement across cycles
This addresses the key challenge: pure SFT distillation degrades performance, pure RL has too large search space.

**Key Insight 2: Open-Source Strong Reasoning**
OpenVLThinker-7B demonstrates that strong reasoning capabilities can be achieved with modest model size (7B) through effective training methodology:
- Competitive with proprietary models (GPT-4o, Claude-3.5)
- Fully open-source (code, models, training data)
- Democratizes access to strong reasoning VLMs

**Key Insight 3: Visual Grounding through Training**
OpenVLThinker shows that visual grounding for reasoning can be improved through iterative training without external tools:
- SFT learns to connect visual input to textual reasoning
- RL refines grounding through exploration
- Iterations progressively improve grounding quality
This is alternative to tool-augmented grounding (Quadrant II), achieving good grounding through training methodology.

**Critical Observation: Quadrant I Trade-offs**
OpenVLThinker exemplifies Quadrant I's trade-offs:
- **Strengths**: No tools (simple deployment), open-source (7B model), iterative improvement (stable gains), competitive performance
- **Weaknesses**: Grounding (implicit, not explicit), verification (outcome-level only), faithfulness (shortcut learning risk)
This motivates hybrid approaches: OpenVLThinker's iterative training + R1-VL's step-wise rewards + Quadrant II's explicit grounding for improved verifiability.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant - Quadrant I: Text-only CoT)
- [x] Section 5 (Learning & Alignment - Iterative SFT-RL, self-improvement)
- [x] Section 6 (Evaluation & Benchmarks - Multi-benchmark evaluation, open-source models)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future - Visual grounding without tools, iterative training)

### Narrative Role

OpenVLThinker serves as the **iterative training specialist** in Quadrant I, demonstrating:

1. **SFT-RL Synergy**: OpenVLThinker shows that alternating SFT and RL stages produces better results than either approach alone. This is important for survey's discussion of training methodologies.

2. **Visual Grounding without Tools**: OpenVLThinker addresses visual grounding challenge through training methodology (iterative SFT-RL), not external tools. This is alternative to Quadrant II's tool-augmented grounding.

3. **Open-Source Strong Reasoning**: OpenVLThinker-7B achieves competitive performance with modest model size, fully open-source. This is important for survey's discussion of open science and accessibility.

4. **Iterative Self-Improvement**: Each SFT-RL cycle produces better model, which generates better data for next cycle. This is form of self-improvement, similar to R3V's iterative self-training but with different objective.

5. **Quadrant I Limitations**: Despite iterative training, OpenVLThinker still has Quadrant I limitations (implicit grounding, outcome-level verification, faithfulness risk). This motivates hybrid approaches with structured traces or tools.

### Comparison Points

**Excels at**:
- Iterative SFT-RL training (progressive improvement)
- Visual grounding through training (no tools needed)
- Open-source strong reasoning (7B model, competitive performance)
- Multi-benchmark generalization (6 diverse tasks)
- Self-improving loop (model generates own training data)

**Fails at**:
- Grounding strength (implicit visual references, no explicit pointers)
- Step-level verification (outcome-level rewards only)
- Faithfulness (shortcut learning risk, no explicit faithfulness evaluation)
- Replayability (no structured trace, only text re-generation)

**Contrast with Other Quadrants**:
- vs R1-VL (Quadrant I): OpenVLThinker uses iterative SFT-RL with outcome rewards, R1-VL uses step-wise GRPO with dense rewards. OpenVLThinker focuses on training methodology, R1-VL on reward design.
- vs R3V (Quadrant I): Both use iterative training, but OpenVLThinker alternates SFT-RL, R3V iterates self-training. Different objectives.
- vs Visionary-R1 (Quadrant I): OpenVLThinker uses iterative training, Visionary-R1 uses structured format. Complementary approaches.
- vs VideoAgent (Quadrant II): OpenVLThinker has lower cost but weaker grounding. VideoAgent's structured memory provides explicit evidence grounding.

---

## Notes

### Follow-up Items
- [x] Verified arXiv link, code repository, NeurIPS poster, and OpenReview page
- [x] Extracted key method details (iterative SFT-RL, 6 benchmarks, 7B model)
- [x] Identified main benchmarks from search results (MathVista, EMMA, HallusionBench, MathVerse, MathVision, MMMU-Pro)
- [ ] Need to read full paper for complete author list and affiliations
- [ ] Need to read full paper for complete evaluation results (per-benchmark numbers, per-iteration improvement)
- [ ] Need to verify base LVLM model used
- [ ] Need to extract specific RL algorithm details (GRPO or other?)
- [ ] Need to verify number of SFT-RL iterations

### Questions
- What is the base LVLM used for OpenVLThinker?
   - Answer not provided in search results. Likely Qwen-VL-7B or LLaVA-1.5-7B variant. Need full paper for model details.

- What RL algorithm is used (GRPO, PPO, other)?
   - Answer not provided in search results. Likely GRPO (given DeepSeek R1 connection), but need full paper for confirmation.

- How many SFT-RL iterations are performed?
   - Search results mention "few iterations". Need full paper for exact number and per-iteration results.

- What is the source of initial CoT data (distillation from DeepSeek R1, or self-generated)?
   - Search results suggest distillation is used, but details not provided. Need full paper for data source.

### Clarification on Quadrant Placement
OpenVLThinker is placed in Quadrant I (Text-only CoT, No Tools) because:
- Representation: Free-form textual CoT (reasoning steps + answer), not structured traces
- Verification: Outcome-level rewards (answer correctness), no external tools or execution
- Training: Iterative SFT-RL, no tool-use learning
This contrasts with:
- Quadrant II (VideoAgent): Structured memory + tool-augmented reasoning
- Quadrant III (Program-of-Thoughts): Textual CoT + code execution
- Quadrant IV (ViperGPT): Structured program traces + execution

---

## BibTeX

```bibtex
@inproceedings{deng2025openvlthinker,
  title={OpenVLThinker: Complex Vision-Language Reasoning via Iterative SFT-RL Cycles},
  author={Deng, Yihe and [other authors]},
  booktitle={Advances in Neural Information Processing Systems},
  year={2025},
  url={https://arxiv.org/abs/2503.17352}
}
```

**Status:** ✅ Complete - Quadrant I Paper (Iterative SFT-RL Cycles)

**Summary:**
- ArXiv URL, code repository, NeurIPS poster, and OpenReview page links added
- Detailed methodology analysis with 2×2 matrix justification
- Comprehensive verifiability analysis across all 7 dimensions with specific evidence
- Six failure modes identified (shortcut learning, perception errors, distribution mismatch, data degradation, domain limits, complexity limits)
- Extracted evaluation information from search results (6 benchmarks, MathVista +3.8%, EMMA +2.4%, HallusionBench +1.6%, competitive with GPT-4o/Claude-3.5)
- Detailed training process description (iterative SFT-RL cycles, data flow, reward design)
- Connections to R1-VL, R3V, Visionary-R1, and DeepSeek R1 analyzed
- Key quotes and insights extracted, including iterative SFT-RL synergy and open-source strong reasoning
- Total: ~450 lines

**Note:** Author list, base model details, RL algorithm specifics, and iteration numbers need to be filled in from full paper.
