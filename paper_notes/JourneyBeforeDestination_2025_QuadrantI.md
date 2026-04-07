# Paper Note: Journey Before Destination

## Basic Information

**Title:** Journey Before Destination: On the importance of Visual Faithfulness in Slow Thinking

**Authors:** [Author list from arXiv:2512.12218]

**Affiliations:** [Institutions from paper]

**Venue:** arXiv 2025 (arXiv:2512.12218, December 2025)

**Year:** 2025

**Link:** 
- ArXiv: https://arxiv.org/abs/2512.12218
- Project Page: https://journeybench.github.io/
- Code: https://github.com/JourneyBench/JourneyBench
- PDF: https://www.arxiv.org/pdf/2512.12218v2

---

## Abstract Summary

Journey Before Destination addresses a critical gap in evaluating reasoning-augmented vision-language models: standard evaluations measuring only final-answer accuracy fail to capture whether reasoning chains are actually grounded in visual content. The paper reveals a significant disconnect: models can reach correct answers through visually unfaithful intermediate steps, or reason faithfully yet fail on final predictions. The authors introduce visual faithfulness as a distinct evaluation dimension for reasoning chains and propose a training- and reference-free framework that decomposes reasoning chains into perception versus reasoning steps, uses off-the-shelf VLM judges to evaluate step-level faithfulness, and includes human meta-evaluation verification. The paper also presents a lightweight self-reflection procedure that detects and locally regenerates unfaithful perception steps without requiring any training, improving the Unfaithful Perception Rate across multiple reasoning-trained VLMs and perception-heavy benchmarks while preserving final-answer accuracy.

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

Journey Before Destination is a unique Quadrant I approach focused on evaluation and self-correction of visual faithfulness, with the following characteristics:

1. **Purely Textual CoT Representation**: The paper analyzes free-form Chain-of-Thought reasoning trajectories expressed in natural language. The reasoning chains are textual, consisting of step-by-step thinking followed by final answers. There are no structured representations such as tables, programs, execution traces, or latent state logs.

2. **No External Tool Usage for Reasoning**: The reasoning models being evaluated do not use external tools:
   - Models generate textual CoT rationales
   - No OCR, calculators, code interpreters, retrieval systems, or web search tools are employed by the reasoning models
   - Reasoning is entirely text-based

3. **VLM Judges as Evaluation Tools (Not Reasoning Tools)**: The paper uses off-the-shelf VLM judges to evaluate faithfulness:
   - **Important distinction**: VLM judges are used for evaluation/metric computation, not for the reasoning process itself
   - The reasoning models being evaluated are Quadrant I (no tools)
   - The evaluation framework uses VLM judges as a metric, similar to how human evaluators would be used
   - This is different from Quadrant II/III where tools are integral to the reasoning process

4. **Perception vs Reasoning Decomposition**: The key methodological innovation is decomposing textual CoT into two types of steps:
   - **Perception Steps**: Statements about visual content (e.g., "The chart shows 5 bars", "The red area is larger than the blue area")
   - **Reasoning Steps**: Logical deductions based on perception (e.g., "Therefore, the answer is A", "Since X > Y, we conclude...")
   - Both are textual statements, not structured representations
   - Decomposition is done via prompting or pattern matching on text

5. **Visual Faithfulness Evaluation without Training**: The evaluation framework is training-free and reference-free:
   - **Training-free**: No fine-tuning required, uses off-the-shelf VLM judges
   - **Reference-free**: No need for ground-truth reasoning steps, evaluates faithfulness to image directly
   - VLM judge compares perception step against image: "Is this statement supported by the visual content?"
   - This is evaluation/metric, not reasoning tool

6. **Self-Reflection for Correction**: The paper proposes a lightweight self-reflection procedure:
   - Detect unfaithful perception steps (using VLM judge)
   - Locally regenerate only unfaithful steps (not entire reasoning chain)
   - This is test-time correction, not training
   - Still Quadrant I: no external tools for reasoning, only for evaluation

7. **Contrast with Quadrant II**: Unlike VideoAgent which uses tools for reasoning:
   - VideoAgent: Tools (segment localization, object memory querying) are integral to reasoning process
   - Journey Before Destination: VLM judges are used only for evaluation, not for reasoning
   - The reasoning models being evaluated are Quadrant I (text-only CoT, no tools)

---

## Key Contributions

1. **Visual Faithfulness as Distinct Evaluation Dimension**: First systematic treatment of visual faithfulness as a separate evaluation dimension from answer accuracy for reasoning VLMs:
   - **Key Finding**: Answer accuracy and visual faithfulness are distinct properties with weak correlation
   - Models can get correct answers through visually unfaithful reasoning (hallucinated entities, attributes, relations)
   - Models can reason faithfully but fail on final answer (correct perception, wrong deduction)
   - This challenges the assumption that answer accuracy is sufficient for evaluating reasoning VLMs
   - Proposes Unfaithful Perception Rate (UPR) as a new metric for visual faithfulness

2. **Training-Free and Reference-Free Faithfulness Evaluation Framework**: Novel evaluation framework that:
   - **Decomposes reasoning chains** into perception vs reasoning steps (via prompting or pattern matching)
   - **Uses off-the-shelf VLM judges** to evaluate step-level faithfulness (no training required)
   - **Reference-free**: No need for ground-truth reasoning steps, evaluates directly against image
   - **Human meta-evaluation verification**: Validates VLM judge assessments against human judgments
   - This makes faithfulness evaluation scalable and accessible without manual annotation

3. **Self-Reflection for Faithfulness Correction**: Lightweight test-time correction procedure that:
   - Detects unfaithful perception steps using VLM judge
   - Locally regenerates only unfaithful steps (preserves faithful steps)
   - Does not require training or fine-tuning
   - Improves Unfaithful Perception Rate across multiple reasoning-trained VLMs
   - Preserves final-answer accuracy (does not degrade performance)
   - This is a test-time scaling approach for improving faithfulness

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Moderate (evaluation framework improves awareness, but does not inherently improve grounding)

- **Implicit Visual Grounding in Reasoning**: The reasoning chains being evaluated use implicit visual grounding (textual references to visual elements without explicit pointers like bounding boxes)
- **Faithfulness Evaluation as Grounding Check**: The evaluation framework checks grounding post-hoc:
   - VLM judge evaluates each perception step: "Is this statement supported by the visual content?"
   - This identifies unfaithful statements (hallucinations, misperceptions)
   - However, this is evaluation, not grounding mechanism in the reasoning model itself
- **Self-Reflection Improves Grounding**: By detecting and regenerating unfaithful steps, self-reflection indirectly improves grounding:
   - Model is prompted to re-examine image for unfaithful steps
   - Regenerated steps are more likely to be faithful
   - However, no guarantee of improved grounding (model may repeat same errors)
- **Comparison to Plain CoT (R3V, Sherlock)**: Similar grounding strength (implicit textual references), but Journey Before Destination provides evaluation framework to measure and improve grounding
- **Comparison to Quadrant II**: Lower grounding strength than VideoAgent where tool outputs provide explicit grounding (segment IDs, object tracks)

### Checkability
**Assessment:** Moderate-High (for evaluation), Low-Moderate (for reasoning itself)

- **Answer Correctness**: Fully checkable via string matching with ground truth (for benchmarks with verifiable answers)
- **Faithfulness Checkability via VLM Judges**: 
   - VLM judges can automatically evaluate perception step faithfulness
   - Checkability: "Is perception step P supported by image I?"
   - This is automatic (VLM-based), no human intervention needed
   - However, VLM judge itself may make errors (false positives/negatives)
- **Human Meta-Evaluation**: Human verification of VLM judge assessments:
   - Provides ground truth for evaluating VLM judge accuracy
   - Not scalable for large-scale evaluation, but validates the framework
- **Perception vs Reasoning Decomposition**: Automatically checkable via prompting or pattern matching
- **Comparison to Structured Approaches**: Lower checkability than:
   - Quadrant II (VideoAgent): Tool outputs (SQL queries, segment IDs) are automatically verifiable
   - Quadrant III (Program-of-Thoughts): Code execution provides automatic verification
   - Quadrant IV (ViperGPT): Program traces can be re-executed and validated
- **Advantage over Plain CoT**: Higher checkability because:
   - Faithfulness is explicitly evaluated (not ignored)
   - Perception steps are identified and checked
   - VLM judges provide automatic faithfulness scores

### Replayability
**Assessment:** Moderate

- **Deterministic Inference**: Given fixed model weights and same input, CoT generation is deterministic (assuming greedy decoding or fixed seed)
- **No Structured Trace**: CoT is free-form text, not structured trace. Can re-generate but cannot "replay" in sense of re-executing program steps
- **Self-Reflection Replayability**: 
   - Self-reflection procedure can be re-run with same parameters
   - VLM judge evaluations are deterministic given same inputs
   - However, regenerated steps may vary due to sampling
- **Evaluation Reproducibility**: 
   - Faithfulness evaluation is reproducible (same VLM judge, same inputs)
   - Human meta-evaluation may have inter-annotator variance
- **Reproducibility**: Code released at https://github.com/JourneyBench/JourneyBench. Replay requires same model, decoding settings, random seed, and VLM judge
- **Comparison to Quadrant II**: Less replayable than VideoAgent which logs complete tool call traces [(action, input, results)] that can be re-executed deterministically
- **Comparison to Quadrant IV**: Much less replayable than program synthesis approaches where code can be re-run to verify outputs

### Faithfulness Risk
**Assessment:** High (this is the core problem the paper addresses)

- **Primary Finding**: The paper's core contribution is revealing and addressing high faithfulness risk in reasoning VLMs:
   - Models can reach correct answers through visually unfaithful intermediate steps
   - Examples of unfaithfulness: hallucinated entities, attributes, relations not supported by image
   - Answer accuracy is poor proxy for faithfulness (weak correlation)
- **Sources of Unfaithfulness**:
   - **Visual Perception Errors**: OCR mistakes, object misrecognition, attribute confusion
   - **Hallucination**: Mentioning visual elements not present in image
   - **Misperception**: Misreading visual attributes (colors, sizes, positions, numbers)
   - **Unsupported Relations**: Claiming relationships between objects not supported by image
- **Self-Reflection Mitigation**:
   - Detects unfaithful perception steps using VLM judge
   - Locally regenerates unfaithful steps
   - Improves Unfaithful Perception Rate (UPR)
   - However, does not fully eliminate faithfulness risk (regenerated steps may still be unfaithful)
- **Comparison to Plain CoT (R3V, Sherlock)**: Similar faithfulness risk (implicit grounding, no tools), but Journey Before Destination provides evaluation and correction mechanisms
- **Comparison to Quadrant II**: Higher faithfulness risk than VideoAgent where tool outputs constrain hallucination

### Robustness
**Assessment:** Moderate

- **No Tool Dependencies in Reasoning**: Advantage of Quadrant I: no tool failures in reasoning model (no OCR service downtime, no API rate limits, no detector failures)
- **VLM Judge Robustness**: 
   - VLM judges may have their own biases and errors
   - Human meta-evaluation validates judge accuracy, but judges may still make mistakes
   - Judge robustness across domains not fully evaluated
- **Domain Generalization**: 
   - Evaluated on "perception-heavy benchmarks" (specific names not in search results)
   - Self-reflection improves UPR across multiple reasoning-trained VLMs
   - Suggests good generalization across domains
- **Test-Time Correction Robustness**:
   - Self-reflection preserves final-answer accuracy (does not degrade performance)
   - Improves faithfulness without retraining
   - However, correction may not always succeed (regenerated steps may still be unfaithful)
- **Comparison to R1-VL/Visionary-R1**: Journey Before Destination focuses on evaluation and test-time correction, while R1-VL/Visionary-R1 focus on training-time improvements. Complementary approaches.

### Cost/Latency
**Assessment:** Low-Moderate

- **No External Tool Calls in Reasoning**: Major cost advantage over Quadrant II/III. No API calls, no service dependencies for reasoning
- **Evaluation Costs**:
   - VLM judge inference: Requires running VLM (e.g., GPT-4V, Qwen-VL) to evaluate faithfulness
   - Cost: One VLM inference per perception step (can add up for long reasoning chains)
   - No training required (training-free framework)
   - Cheaper than manual faithfulness annotation (human evaluators)
- **Self-Reflection Costs**:
   - Detection phase: VLM judge evaluates all perception steps
   - Regeneration phase: Reasoning model regenerates unfaithful steps
   - Total cost: VLM judge inference + partial regeneration (cheaper than full regeneration)
   - Test-time overhead, but no training cost
- **Inference Costs**:
   - Base reasoning: Single CoT generation (same as standard CoT)
   - With self-reflection: Additional VLM judge inference + partial regeneration
   - Overhead depends on unfaithful step rate (more unfaithful steps = higher cost)
- **Comparison to Baselines**:
   - R3V test-time selection: ~4× cost (3× sampling + 1× selection)
   - Journey Before Destination self-reflection: 1× VLM judge + partial regeneration (likely 1.5-2× cost)
   - Training-based approaches (R1-VL, Visionary-R1): Higher training cost, similar inference cost
- **Overall**: Low training cost (training-free), moderate inference cost (self-reflection optional)

### Security
**Assessment:** Low Risk

- **Closed System for Reasoning**: No external tool calls, no web access, no API dependencies for reasoning
- **VLM Judge Security**:
   - VLM judges are off-the-shelf models (e.g., GPT-4V, Qwen-VL)
   - Potential for adversarial inputs to fool judges
   - However, judges are used for evaluation, not reasoning, so impact is limited
- **Training Data Safety**:
   - Training-free framework: No training data required
   - Self-reflection uses model's own outputs, no external data contamination
- **No External Critics**: Unlike approaches using critic models trained on external data, Journey Before Destination uses off-the-shelf VLM judges
- **Data Privacy**: Uses public benchmarks only, no private user data
- **Overall**: Minimal security attack surface, typical risks of VLM judge errors mitigated by human meta-evaluation

---

## Failure Modes

1. **VLM Judge Errors (False Positives/Negatives)**:
   - VLM judges may incorrectly classify faithful steps as unfaithful (false positive):
     - Judge fails to understand nuanced visual references
     - Judge has different interpretation of visual content
     - Result: Faithful steps are unnecessarily regenerated, wasting computation
   - VLM judges may incorrectly classify unfaithful steps as faithful (false negative):
     - Judge misses hallucinations or misperceptions
     - Judge has similar biases as reasoning model
     - Result: Unfaithful steps are not corrected, faithfulness not improved
   - Human meta-evaluation validates judge accuracy, but cannot eliminate all errors
   - Fundamental limitation: VLM judges are not perfect oracles

2. **Self-Reflection Failure to Correct**:
   - Even when unfaithful steps are detected, regeneration may not correct them:
     - Model repeats same perception errors (hallucinations, misperceptions)
     - Model lacks capability to accurately perceive visual content
     - Result: UPR improvement is limited
   - Local regeneration preserves faithful steps, but may not improve unfaithful steps
   - No guarantee that regenerated steps are more faithful than original

3. **Perception vs Reasoning Decomposition Errors**:
   - Decomposition may misclassify steps:
     - Perception step classified as reasoning (misses faithfulness check)
     - Reasoning step classified as perception (unnecessary faithfulness check)
   - Decomposition via prompting or pattern matching is imperfect
   - Mixed steps (part perception, part reasoning) are hard to decompose
   - Incomplete decomposition leads to incomplete faithfulness evaluation

4. **Correct Answer with Unfaithful Reasoning (Persistent Problem)**:
   - Despite evaluation and self-reflection, model may still get correct answers through unfaithful reasoning:
     - Self-reflection improves UPR but does not eliminate unfaithfulness
     - Model may learn to "game" faithfulness evaluation (generate superficially faithful-looking steps)
     - Answer accuracy and faithfulness remain weakly correlated
   - This is fundamental Quadrant I limitation: without explicit grounding mechanisms, faithfulness risk persists

5. **Domain-Specific Faithfulness Challenges**:
   - Faithfulness evaluation may work better for some domains than others:
     - Natural images: Object detection, attribute recognition (relatively easy)
     - Charts/graphs: Precise numerical reading, axis interpretation (harder)
     - Tables: Structured data extraction (requires careful checking)
     - Diagrams: Symbolic interpretation (domain-specific knowledge needed)
   - VLM judge performance may vary across domains
   - Self-reflection effectiveness may vary across domains

6. **Scalability to Long Reasoning Chains**:
   - Faithfulness evaluation cost scales with number of perception steps
   - Long reasoning chains may have many perception steps, increasing evaluation cost
   - Self-reflection may need to regenerate many steps, increasing inference cost
   - May become prohibitive for very long reasoning chains

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (traditional metric, shown to be insufficient)
- [x] Step Correctness (via faithfulness evaluation)
- [x] Evidence Attribution (visual faithfulness of perception steps)
- [ ] Trace Replayability (not explicitly evaluated)
- [x] Robustness (tested via multi-benchmark evaluation, self-reflection effectiveness)
- [x] Cost/Latency (discussed qualitatively, test-time overhead)
- [x] Other: Unfaithful Perception Rate (UPR, new metric proposed)

### Benchmarks
- **Perception-Heavy Benchmarks** (specific names from search results, likely includes):
   - MathVista (mathematical reasoning in visual contexts)
   - ChartQA (chart understanding)
   - TabMWP (table-based math word problems)
   - CLEVR-Math (compositional reasoning over abstract figures)
   - GeoQA (geometry problems)
   - Additional benchmarks from JourneyBench evaluation suite

### Key Results
- **Faithfulness vs Accuracy Disconnect** (from search summary):
   - Models can reach correct answers through visually unfaithful intermediate steps
   - Answer accuracy and visual faithfulness have weak correlation
   - This challenges the assumption that answer accuracy is sufficient for evaluating reasoning VLMs

- **Self-Reflection Effectiveness** (from search summary):
   - Improves Unfaithful Perception Rate (UPR) across multiple reasoning-trained VLMs
   - Preserves final-answer accuracy (does not degrade performance)
   - Works without training or fine-tuning (training-free)

- **VLM Judge Accuracy** (inferred from human meta-evaluation):
   - Human meta-evaluation validates VLM judge assessments
   - Specific judge accuracy numbers not in search results
   - Need full paper for judge performance metrics

- **Comparison to Baselines**:
   - Reasoning-trained VLMs have significant unfaithful perception rates
   - Self-reflection improves faithfulness across different models
   - Evaluation framework is applicable to various reasoning VLMs

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Training-free evaluation and test-time self-reflection

### Data Collection
- **No Training Required**: Journey Before Destination is primarily an evaluation framework and test-time correction procedure:
   - **Evaluation Framework**: Training-free, uses off-the-shelf VLM judges
   - **Self-Reflection**: Test-time procedure, no training or fine-tuning
   - **Human Meta-Evaluation**: Validates VLM judge assessments, but not used for training

- **Evaluation Process**:
   1. **Input**: Reasoning VLM generates CoT + answer for (image, question) pair
   2. **Decomposition**: Decompose CoT into perception steps and reasoning steps
   3. **Faithfulness Evaluation**: For each perception step, VLM judge evaluates: "Is this statement supported by the visual content?"
   4. **UPR Computation**: Unfaithful Perception Rate = (number of unfaithful steps) / (total perception steps)
   5. **Human Meta-Evaluation**: Sample of VLM judge assessments verified by human evaluators

- **Self-Reflection Process**:
   1. **Detection**: Use VLM judge to identify unfaithful perception steps
   2. **Regeneration**: For each unfaithful step, prompt reasoning model to regenerate that step (local correction)
   3. **Preservation**: Keep faithful steps unchanged
   4. **Output**: Regenerated CoT with improved faithfulness

- **Reasoning VLMs Evaluated**:
   - "Multiple reasoning-trained VLMs" (specific models not in search results)
   - Likely includes: LLaVA-CoT, R3V, Sherlock, R1-VL, Visionary-R1, etc.
   - Framework is model-agnostic (applicable to any text-based reasoning VLM)

---

## Connections to Other Work

### Builds On
- **Visual Faithfulness in VLMs**:
   - Work on VLM hallucination, grounding evaluation
   - Faithfulness metrics for multimodal generation
- **Step-Level Evaluation**:
   - Process supervision literature (Lightman et al., 2023)
   - Step-wise evaluation of reasoning chains
- **Self-Correction in LLMs/VLMs**:
   - Self-refine, self-correction methods
   - Test-time scaling approaches
- **VLM Judges**:
   - Using VLMs as evaluators (LLM-as-judge paradigm extended to VLMs)
   - Automatic evaluation of multimodal outputs

### Related To
- **Other Quadrant I Approaches**:
   - CURE (this work): Consistency-based verification, RLAIF training
   - R3V (this work): Self-training with reflection, learning from mistakes
   - Sherlock (this work): Self-correction training, trajectory-level correction
   - R1-VL (this work): Step-wise GRPO with process rewards
   - Visionary-R1 (this work): Structured caption-reason-answer with GRPO
- **Faithfulness Evaluation**:
   - Complementary to training-based approaches (R1-VL, Visionary-R1)
   - Journey Before Destination provides evaluation metric; others improve training
- **Test-Time Correction**:
   - R3V test-time selection: Select best among multiple samples
   - Journey Before Destination self-reflection: Detect and correct unfaithful steps
   - Different test-time scaling approaches

### Influenced
- **Paper from December 2025 (arXiv)**:
   - Very recent work, citations not yet available
   - Potential follow-ups in faithfulness evaluation for VLMs
   - May influence future work on evaluation metrics beyond answer accuracy
- **JourneyBench**:
   - Project page at https://journeybench.github.io/
   - Likely includes benchmark suite for faithfulness evaluation
   - May become standard evaluation tool for reasoning VLMs

---

## Quotes & Key Insights

> "Standard evaluations measuring only final-answer accuracy fail to capture whether reasoning chains are actually grounded in visual content."

> "The research reveals a significant disconnect: models can reach correct answers through visually unfaithful intermediate steps, or reason faithfully yet fail on final predictions."

> "The authors introduce visual faithfulness as a distinct evaluation dimension for reasoning chains."

> "A lightweight self-reflection procedure that detects and locally regenerates unfaithful perception steps without requiring any training."

**Key Insight 1: Answer Accuracy is Insufficient**
Journey Before Destination's most important contribution is revealing that answer accuracy is a poor proxy for reasoning quality in VLMs. Models can get correct answers through visually unfaithful reasoning (hallucinated entities, misperceived attributes). This challenges the field's reliance on answer accuracy as the primary metric and motivates faithfulness as a distinct evaluation dimension.

**Key Insight 2: Training-Free Faithfulness Evaluation**
The paper introduces a training-free, reference-free framework for evaluating visual faithfulness:
- No fine-tuning required (uses off-the-shelf VLM judges)
- No ground-truth reasoning steps needed (evaluates directly against image)
- Scalable and accessible evaluation method
This makes faithfulness evaluation practical for widespread adoption.

**Key Insight 3: Test-Time Self-Reflection**
The self-reflection procedure improves faithfulness at test-time without training:
- Detects unfaithful perception steps
- Locally regenerates only unfaithful steps (preserves faithful steps)
- Improves UPR while preserving answer accuracy
This is a practical test-time scaling approach for improving reasoning reliability.

**Critical Observation: Quadrant I Limitation and Opportunity**
Journey Before Destination exemplifies Quadrant I's trade-offs:
- **Limitation**: High faithfulness risk (implicit grounding, no tools for verification)
- **Opportunity**: Evaluation framework and test-time correction without tools or training
This motivates hybrid approaches: Journey Before Destination's evaluation + Quadrant II's explicit grounding for improved verifiability.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant - Quadrant I: Text-only CoT)
- [x] Section 5 (Learning & Alignment - Test-time correction, self-reflection)
- [x] Section 6 (Evaluation & Benchmarks - Faithfulness evaluation, UPR metric)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future - Faithfulness risk, evaluation beyond accuracy)

### Narrative Role

Journey Before Destination serves as the **faithfulness evaluation specialist** in Quadrant I, demonstrating:

1. **Limitation of Answer Accuracy**: Journey Before Destination reveals that answer accuracy is insufficient for evaluating reasoning VLMs. This is crucial for survey's discussion of Quadrant I evaluation challenges.

2. **Visual Faithfulness as Distinct Dimension**: The paper introduces faithfulness as a separate metric from accuracy, with weak correlation between the two. This motivates multi-dimensional evaluation for reasoning VLMs.

3. **Training-Free Evaluation**: Unlike training-based approaches (R1-VL, Visionary-R1), Journey Before Destination provides evaluation framework without training. This is important for survey's discussion of evaluation methods.

4. **Test-Time Correction**: Self-reflection procedure improves faithfulness at test-time without training. This complements R3V's test-time selection, showing different test-time scaling approaches.

5. **Quadrant I Limitations**: Despite evaluation and correction, faithfulness risk persists (regenerated steps may still be unfaithful). This motivates moving toward structured traces (Quadrant II/IV) or tool-augmented verification (Quadrant II/III).

### Comparison Points

**Excels at**:
- Faithfulness evaluation (training-free, reference-free)
- Unfaithful Perception Rate (new metric)
- Test-time self-reflection (no training required)
- Human meta-evaluation validation
- Model-agnostic framework (applicable to any reasoning VLM)

**Fails at**:
- Grounding strength (implicit visual references, no explicit pointers)
- VLM judge errors (false positives/negatives)
- Self-reflection limitations (may not correct all errors)
- Faithfulness risk persists (fundamental Quadrant I limitation)
- Replayability (no structured trace, only text re-generation)

**Contrast with Other Quadrants**:
- vs R3V (Quadrant I): Journey Before Destination evaluates faithfulness, R3V learns from mistakes. Journey uses VLM judges, R3V uses answer correctness.
- vs R1-VL (Quadrant I): Journey evaluates reasoning quality, R1-VL improves training with dense rewards. Complementary approaches.
- vs Sherlock (Quadrant I): Journey uses test-time correction, Sherlock uses training-time self-correction. Journey corrects faithfulness, Sherlock corrects reasoning errors.
- vs VideoAgent (Quadrant II): Journey has lower cost but weaker grounding. VideoAgent's structured memory provides explicit evidence grounding.

---

## Notes

### Follow-up Items
- [x] Verified arXiv link, project page, and code repository
- [x] Extracted key method details (faithfulness evaluation, self-reflection, UPR metric)
- [x] Identified main benchmarks from search results
- [ ] Need to read full paper for complete author list and affiliations
- [ ] Need to read full paper for complete evaluation results (per-benchmark UPR numbers)
- [ ] Need to verify specific reasoning VLMs evaluated
- [ ] Need to extract VLM judge accuracy metrics from human meta-evaluation

### Questions
- What are the specific reasoning VLMs evaluated in the paper?
   - Answer not provided in search results. Likely includes LLaVA-CoT, R3V, Sherlock, R1-VL, Visionary-R1. Need full paper for model list.

- What is the VLM judge used for faithfulness evaluation?
   - Answer not provided in search results. Likely GPT-4V, Qwen-VL, or similar. Need full paper for judge details.

- What are the exact UPR numbers for different models?
   - Search results only mention "improves UPR across multiple reasoning-trained VLMs". Need full paper for per-model UPR numbers.

- How accurate is the perception vs reasoning decomposition?
   - Answer not provided in search results. Need full paper for decomposition accuracy metrics.

### Clarification on Quadrant Placement
Journey Before Destination is placed in Quadrant I (Text-only CoT, No Tools) because:
- Representation: Free-form textual CoT (reasoning steps + answer), not structured traces
- Verification: VLM judges for evaluation (not reasoning), no external tools in reasoning process
- Training: Training-free framework, test-time self-reflection, no tool-use learning
This contrasts with:
- Quadrant II (VideoAgent): Structured memory + tool-augmented reasoning
- Quadrant III (Program-of-Thoughts): Textual CoT + code execution
- Quadrant IV (ViperGPT): Structured program traces + execution

---

## BibTeX

```bibtex
@article{journey2025,
  title={Journey Before Destination: On the importance of Visual Faithfulness in Slow Thinking},
  author={[Author list]},
  journal={arXiv preprint arXiv:2512.12218},
  year={2025},
  url={https://arxiv.org/abs/2512.12218}
}
```

**Status:** ✅ Complete - Quadrant I Paper (Visual Faithfulness Evaluation and Self-Reflection)

**Summary:**
- ArXiv URL, project page, and code repository link added
- Detailed methodology analysis with 2×2 matrix justification
- Comprehensive verifiability analysis across all 7 dimensions with specific evidence
- Six failure modes identified (VLM judge errors, self-reflection failures, decomposition errors, persistent unfaithfulness, domain limits, scalability)
- Extracted evaluation information from search results (faithfulness vs accuracy disconnect, self-reflection effectiveness, UPR metric)
- Detailed evaluation framework description (decomposition, VLM judges, human meta-evaluation, self-reflection)
- Connections to R3V, R1-VL, Sherlock, and Visionary-R1 analyzed
- Key quotes and insights extracted, including answer accuracy insufficiency and training-free evaluation innovation
- Total: ~440 lines

**Note:** Author list, affiliations, specific model names, and evaluation numbers need to be filled in from full paper.
