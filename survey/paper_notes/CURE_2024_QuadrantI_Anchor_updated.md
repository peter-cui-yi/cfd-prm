# Paper Note: CURE (Updated)

## Basic Information

**Title:** Measuring and Improving Chain-of-Thought Reasoning in Vision-Language Models

**Authors:** Yangyi Chen, Karan Sikka, Michael Cogswell, Heng Ji, Ajay Divakaran

**Affiliations:** SRI International, University of Illinois Urbana-Champaign

**Venue:** NAACL 2024 (arXiv v2: March 2024)

**Year:** 2024

**Link:** 
- ArXiv: https://arxiv.org/abs/2309.04461
- Code: https://github.com/Yangyi-Chen/CoTConsistency

---

## Abstract Summary

CURE addresses the critical concern of reasoning consistency in Vision-Language Models (VLMs) by proposing a Chain-of-Thought (CoT) based consistency measure and benchmark. The authors introduce an LLM-Human-in-the-Loop pipeline to efficiently construct the CURE benchmark (1,622 samples) with high-level visual inference and fine-grained CoT reasoning chains. Their evaluation reveals that even state-of-the-art VLMs (e.g., BLIP-2) fall short in reasoning performance and consistency compared to humans. As a solution, they propose a two-stage training framework (SFT + RLAIF) that improves both reasoning performance and consistency by approximately 4% relative improvement without requiring human annotations.

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

CURE is a quintessential Quadrant I approach for the following reasons:

1. **Purely Textual CoT Representation**: The reasoning chains in CURE consist of free-form natural language subquestions and answers (e.g., "Q1: What is on the cake? A1: Candles", "Q2: What does each candle represent? A2: Age"). There is no structured representation such as tables, programs, or executable traces. The CoT rationale is entirely textual and follows a "from recognition to cognition" progression.

2. **No External Tool Usage**: CURE's verification mechanism relies entirely on internal consistency checks rather than external tools. The consistency metrics (forward consistency Cf and backward consistency Cb) measure whether the model can correctly answer the high-level inference given correct CoT steps, and vice versa. There is no tool augmentation (OCR, detectors, retrieval) or execution feedback involved.

3. **Consistency as Self-Verification**: The core innovation is using consistency between CoT steps and final answers as a verification signal. This is purely internal to the model's reasoning process:
   - Forward Consistency (Cf): Given all subquestions answered correctly, can the model derive the correct high-level inference?
   - Backward Consistency (Cb): Given the correct high-level inference, can the model answer all subquestions correctly?
   
4. **Contrast with Quadrant II**: Unlike VideoAgent (Quadrant II) which uses structured memory (temporal segments, object tracks) and executable tools (segment localization, VQA), CURE operates entirely in the textual CoT space with no external grounding mechanisms beyond the VLM's internal visual understanding.

5. **Training without Tools**: The two-stage training framework (SFT + RLAIF) uses LLM feedback (GPT-3.5-Turbo) to evaluate reasoning chains on three criteria (Sophistication, Consistency, Groundedness), but this feedback is still text-based and does not involve tool execution or environment interaction.

---

## Key Contributions

1. **CURE Benchmark**: First benchmark to measure both reasoning performance AND consistency in VLMs using fine-grained CoT reasoning chains. Contains 1,622 human-verified samples with high-level visual inference and 2-4 progressive subquestions per sample (from recognition to cognition), constructed via a novel LLM-Human-in-the-Loop pipeline that reduces annotation cost by 50%.

2. **Consistency Metrics**: Proposes novel metrics for measuring reasoning consistency:
   - Forward Consistency (Cf): Measures if correct CoT steps lead to correct final inference
   - Backward Consistency (Cb): Measures if correct final inference implies correct CoT steps
   - Overall metrics (Ro, Rh, Rcot) for comprehensive evaluation
   Key finding: Even SOTA models show poor consistency (e.g., BLIP-2-T5: Cf=83.1%, Cb=71.03% vs Human: Cf=95.51%, Cb=91.4%)

3. **Two-Stage Training Framework (CoTBLIP)**: Proposes SFT + RLAIF training without human annotations:
   - Stage 1 (SFT): Fine-tune on LLaVA reasoning samples with LLM-generated CoT chains
   - Stage 2 (RLAIF): Use LLM feedback (GPT-3.5-Turbo) to rank reasoning chains on Sophistication, Consistency, Groundedness; train with conditional RL using control tokens
   Result: 4% relative improvement in reasoning performance (Ro: 54.93→56.91) and forward consistency (Cf: 83.66→86.67)

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Moderate-Low

- **Implicit Grounding**: CoT steps reference visual elements implicitly through natural language (e.g., "patches of snow on grass") but do not provide explicit grounding pointers such as bounding boxes, segmentation masks, or region coordinates
- **No Region Specification**: While the original Sherlock dataset includes bounding boxes for visual clues, CURE's CoT reasoning chains do not explicitly ground subquestions to specific image regions
- **Dependent on VLM Visual Encoder**: Grounding quality entirely depends on the VLM's internal visual representation (BLIP-2's frozen image encoder). No mechanism to verify if the model actually "saw" the visual evidence it claims in the CoT
- **Hallucination Risk**: Paper explicitly acknowledges hallucination as a key failure mode in Stage 1 SFT: "VLMs may produce inaccurate high-level inferences due to inconsistencies or hallucination in the rationales"
- **Partial Mitigation**: RLAIF stage includes "Groundedness" as one of three feedback criteria, asking LLM to check if "visual details in reasoning chains should be fully grounded in images, instead of hallucination"

### Checkability
**Assessment:** Moderate

- **Consistency Checking**: Primary verification mechanism is consistency between CoT steps and final answers:
  - Can automatically check if model answers all subquestions correctly (Rcot metric)
  - Can check if correct CoT leads to correct final answer (Cf metric)
  - Can check if correct final answer implies correct CoT (Cb metric)
- **Limitations of Consistency**: 
  - Consistency ≠ Correctness: Model can be consistently wrong across multiple runs
  - No automatic verification of individual CoT step quality beyond answer matching
  - LLM feedback in RLAIF provides soft supervision but is not automatically verifiable
- **Multiple Choice Format**: CURE formulates evaluation as 6-way multiple choice for easy automatic evaluation, but this limits checkability to answer selection rather than open-ended reasoning validation
- **No Execution**: Unlike Quadrant II/IV approaches, there is no executable trace to replay or verify

### Replayability
**Assessment:** Moderate

- **Deterministic Inference**: Given fixed model weights and same input, CoT generation is deterministic (assuming greedy decoding or fixed seed)
- **No Structured Trace**: CoT is free-form text, not structured trace. Can re-generate but cannot "replay" in the sense of re-executing program steps
- **Multiple Sampling for Consistency**: Paper mentions generating multiple CoT chains (3 samples in RLAIF stage) for consistency checking, but this is for training data construction, not inference-time replay
- **Reproducibility**: Code released at https://github.com/Yangyi-Chen/CoTConsistency, but replay requires same model and decoding settings
- **Comparison to Quadrant II**: Less replayable than VideoAgent which logs complete tool call traces [(action, input, results)] that can be re-executed

### Faithfulness Risk
**Assessment:** High

- **Primary Problem Addressed**: Faithfulness is the central challenge CURE attempts to address. Paper states: "VLMs are not always consistent in their reasoning" and "reliability of intermediate reasoning steps cannot be assured, irrespective of the accuracy of the final inference (and vice versa)"
- **Key Findings on Faithfulness**:
  - Even best model (BLIP-2-T5) shows significant gap vs human on consistency (Cb: 71.03% vs 91.4%)
  - Chat-based VLMs (LLaVA, miniGPT-4) show extremely poor faithfulness (LLaVA: Cb=17.65%, Cf=14.29%)
  - Model can get correct final answer while failing on CoT steps, or vice versa
- **Hallucination in CoT**: Stage 1 SFT produces rationales that "might contain inconsistent reasoning chains or contents that are not grounded in images (hallucination)"
- **Consistency ≠ Faithfulness**: CURE's consistency metrics measure internal coherence, not true faithfulness to visual evidence. Model can generate consistent but hallucinated reasoning chains
- **RLAIF Mitigation**: Stage 2 uses LLM feedback to check "Groundedness" but this is still text-based evaluation, not true visual grounding verification
- **Comparison to Quadrant II**: Much higher faithfulness risk than VideoAgent which forces grounding through memory queries and tool outputs

### Robustness
**Assessment:** Moderate

- **No Tool Dependencies**: Advantage of Quadrant I approach: no tool failures to worry about (no OCR errors, no detector failures, no API downtime)
- **Domain Shift Sensitivity**: Paper evaluates on CURE benchmark derived from Sherlock dataset (abductive reasoning about everyday scenes). Performance on out-of-distribution visual domains (medical images, diagrams, charts) is unknown
- **Caption/Description Dependency**: RLAIF stage uses image captions from SBU Captions dataset. Quality of captions affects feedback quality: "scalability of RLAIF stage...attributing to...web-scale image-captions data"
- **Model Component Dependencies**: Performance depends on three factors identified in paper:
  1. LLM component quality (text-only GPT-3.5-Turbo: Ro=15.97%)
  2. Visual input quality (OFA-Large without LLM: Ro=0.12%)
  3. Instruction fine-tuning (BLIP-2-OPT without instruction tuning: Ro=0.06%)
- **Ablation Results**: Both SFT and RLAIF stages contribute to robustness (Table 3):
  - Full CoTBLIP: Ro=56.91, Cf=86.67
  - w/o RLAIF: Ro=55.06, Cf=83.85
  - w/o SFT: Ro=54.75, Cf=83.38
- **Scalability**: Figure 4 shows increasing RLAIF training data (from 20% to 100%) consistently improves performance, suggesting good scalability

### Cost/Latency
**Assessment:** Low-Moderate

- **No External Tool Calls**: Major cost advantage over Quadrant II/III approaches. No API calls to OCR services, no detector inference, no database queries
- **Training Costs**:
  - Stage 1 (SFT): Uses 77K samples from LLaVA dataset with LLM-generated CoT (one-time GPT-4 cost)
  - Stage 2 (RLAIF): Generates 27K preference samples from SBU Captions using GPT-3.5-Turbo for feedback
  - Total LLM API cost: Moderate (GPT-4 for 77K CoT generation + GPT-3.5-Turbo for 27K feedback)
- **Inference Costs**:
  - CoTBLIP generates CoT rationale first, then passes to frozen BLIP-2-T5xl for answer prediction
  - Two-stage inference adds latency compared to direct answer prediction
  - No multiple sampling at inference time (unlike R3V which samples 3 solutions)
- **Comparison**: Lower cost than VideoAgent (which requires memory construction + multiple tool calls per query) and R3V (which samples multiple CoT solutions)

### Security
**Assessment:** Low Risk

- **Closed System**: No external tool calls, no web access, no API dependencies at inference time
- **No Prompt Injection Surface**: Unlike tool-augmented systems, there are no tool arguments that could be manipulated for injection attacks
- **Training Data Safety**: Uses publicly available datasets (LLaVA, SBU Captions) with LLM filtering. Human verification step catches problematic samples
- **LLM Feedback Risk**: RLAIF stage relies on GPT-3.5-Turbo for feedback. Potential concerns:
  - Feedback bias from LLM
  - No explicit protection against adversarial prompts in feedback generation
  - However, feedback is used only for training, not inference
- **Data Privacy**: SBU Captions contains web-scraped images with captions. No explicit mention of privacy filtering
- **Overall**: Quadrant I approach has minimal security attack surface compared to tool-augmented systems

---

## Failure Modes

1. **Consistency-Correctness Gap (Fundamental Limitation)**: 
   - Model can generate multiple consistent but incorrect reasoning chains
   - Consistency metrics (Cf, Cb) measure internal coherence, not truthfulness to visual evidence
   - Example from paper: Model may consistently reason about wrong visual details due to hallucination
   - Even after training, CoTBLIP shows significant gap vs human (Ro: 56.91% vs 85.0%; Cf: 86.67% vs 95.51%)
   - This is an inherent limitation of Quadrant I approaches: without external grounding, consistency cannot guarantee correctness

2. **Hallucination in CoT Generation**:
   - Stage 1 SFT produces rationales with hallucinated visual details not present in images
   - Paper explicitly states: "VLMs may produce inaccurate high-level inferences due to...hallucination in the rationales"
   - RLAIF stage attempts to filter via "Groundedness" criterion but LLM feedback cannot truly verify visual grounding (only text-based evaluation)
   - Failure case: Model generates CoT "There are 3 candles on the cake" when image shows 2 candles, but reasoning chain is internally consistent
   - This differs from Quadrant II where tool outputs (e.g., object detection) would catch such errors

3. **Error Propagation in CoT Steps**:
   - Figure 5 analysis shows VLMs struggle with initial visual perceptual problems (first subquestion)
   - Early mistakes in CoT cascade through subsequent reasoning steps
   - Backward Consistency (Cb) is lower than Forward Consistency (Cf) across all models, indicating models cannot reliably recover correct CoT even when given correct final answer
   - Example: If model fails to recognize "candles" in first step, subsequent reasoning about "number of candles representing age" will be wrong
   - Unlike self-correction approaches (R3V, Sherlock), CURE has no mechanism to revise erroneous CoT steps

4. **Limited Generalization Beyond Training Distribution**:
   - CURE benchmark derived from Sherlock dataset (everyday scenes with human-oriented concepts)
   - Word cloud analysis (Figure 6) shows concentration on human activities, objects, events
   - Question type distribution (Figure 7) dominated by "What" questions (86.1%), limited diversity
   - Performance on out-of-distribution domains (diagrams, charts, medical images, scientific figures) is unknown
   - RLAIF stage uses SBU Captions (general web images), but feedback quality depends on caption relevance
   - Paper acknowledges limitation: "CoTBLIP currently can only generate general visual inference about given images, without considering instructions"

5. **LLM Feedback Limitations in RLAIF**:
   - Stage 2 relies on GPT-3.5-Turbo to evaluate "Sophistication, Consistency, Groundedness"
   - LLM cannot truly verify visual groundedness (only evaluates text coherence)
   - Paper notes: "LLMs exhibit conflicting rankings" requiring consistency check to filter instances
   - Feedback quality bottleneck: If LLM provides noisy feedback, RL training may learn incorrect preferences
   - Comparison to R3V: R3V uses answer correctness (verifiable) to bootstrap positive/negative samples, while CURE uses LLM judgment (soft supervision)

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (Rh: high-level inference, Rcot: CoT steps, Ro: overall)
- [x] Step Correctness (via consistency metrics Cf, Cb)
- [ ] Evidence Attribution (no explicit grounding evaluation)
- [ ] Trace Replayability (no structured trace)
- [x] Robustness (ablation studies, data scaling analysis)
- [x] Cost/Latency (discussed qualitatively)
- [x] Other: Forward Consistency (Cf), Backward Consistency (Cb)

### Benchmarks
- **CURE**: 1,622 evaluative instances, each with:
  - High-level question with 6 candidate inferences
  - 2-4 CoT subquestions (average 2.91), each with 6 candidate answers
  - Derived from Sherlock dataset with LLM-Human-in-the-Loop construction
  - Human verification: 97% valid samples, only 3% with issues
- **Human Evaluation**: 200 samples evaluated by 3 annotators
  - Human performance: Ro=85.0%, Rh=93.0%, Rcot=89.0%, Cb=91.4%, Cf=95.5%

### Key Results
- **SOTA Model Performance (BLIP-2-T5xl)**:
  - Ro=54.56%, Rh=76.82%, Rcot=65.66%, Cb=71.03%, Cf=83.10%
  - Significant gap vs human (e.g., Ro: 54.56% vs 85.0%)
- **Chat-based VLMs Fail on Reasoning**:
  - LLaVA-13b: Ro=0.12%, Rh=14.67%, Rcot=17.82%, Cb=17.65%, Cf=14.29%
  - miniGPT-4-13b: Ro=2.10%, Rh=23.12%, Rcot=38.75%, Cb=41.80%, Cf=28.81%
  - Informal chat-style training data lacks reasoning supervision
- **CoTBLIP Improvements**:
  - Ro: 54.93 → 56.91 (+3.6% relative)
  - Rh: 77.68 → 80.05 (+3.0% relative)
  - Cf: 83.66 → 86.67 (+3.6% relative)
  - Cb: 70.71 → 71.09 (marginal)
- **Ablation Study (Table 3)**:
  - Both SFT and RLAIF stages contribute
  - SFT necessary for initialization (w/o SFT fails)
  - RLAIF provides calibration for better consistency
- **Data Scaling (Figure 4)**:
  - Increasing RLAIF training samples consistently improves performance
  - Suggests potential for web-scale image-caption data

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Stage 1)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: RLAIF (Reinforcement Learning from AI Feedback) with control tokens

### Data Collection
- **Stage 1 (SFT)**:
  - Source: LLaVA dataset (77K complex reasoning samples)
  - Original data: GPT-4 generated visual inference from 5 human-annotated COCO captions + bounding boxes
  - Post-processing: Prompt GPT-4 to convert to CoT reasoning chains (2-4 steps, logical, consistent, succinct)
  - Final: 77K CoT-augmented samples for SFT
- **Stage 2 (RLAIF)**:
  - Source: SBU Captions (web-scraped image-caption pairs)
  - Process:
    1. CoTBLIP generates 3 CoT reasoning chains per image
    2. GPT-3.5-Turbo evaluates each chain on: Sophistication, Consistency, Groundedness
    3. Pairwise comparison to rank 3 chains
    4. Consistency check to filter conflicting rankings
  - Final: 27K LLM preference samples
  - Scalability: Figure 4 shows increasing samples improves performance
- **Control Tokens**:
  - Two tokens: `<good>` and `<bad>`
  - Add `<good>` to highest-ranked chain, `<bad>` to others
  - Train CoTBLIP to maximize likelihood conditioned on control token
  - No separate reward model needed (LLM serves as reward model)

---

## Connections to Other Work

### Builds On
- **Visual Chain-of-Thought Reasoning**: Extends CoT paradigm (Wei et al., 2022) to vision-language domain
- **Self-Consistency in LLMs**: Builds on Wang et al. (2022d) "Self-Consistency Improves Chain of Thought Reasoning" but applies to VLMs with visual grounding challenge
- **Faithfulness in XAI**: Related to Lanham et al. (2023) "Measuring Faithfulness in Chain-of-Thought Reasoning" but focuses on multimodal faithfulness
- **LLM-in-the-Loop Data Generation**: Follows approach of using LLMs for dataset construction (Self-Instruct, Wang et al. 2022e)
- **RLAIF**: Extends RLHF paradigm (Ouyang et al., 2022) using AI feedback instead of human feedback

### Related To
- **Other Quadrant I Approaches**:
  - R3V (this work): Also uses CoT reflection but adds self-training with positive/negative sampling
  - Sherlock (this work): Focuses on self-correction within CoT trajectories
- **Process Supervision Methods**: Related to Section 5 of survey (learning from process feedback rather than outcome)
- **Visual Reasoning Benchmarks**:
  - Sherlock (Hessel et al., 2022): Base dataset for CURE
  - VCR (Zellers et al., 2019): Coarse-grained rationale evaluation
  - ScienceQA (Lu et al., 2022a): Human evaluation of rationales
- **VLM Training Frameworks**:
  - LLaVA (Liu et al., 2023c): Instruction tuning for VLMs
  - InstructBLIP (Dai et al., 2023): General-purpose VLM with instruction tuning
  - BLIP-2 (Li et al., 2023a): Frozen image encoder + LLM architecture

### Influenced
- **Need to check citations** (paper from NAACL 2024, arXiv v2 March 2024):
  - Potential follow-ups in VLM reasoning consistency evaluation
  - RLAIF for VLM alignment
  - CoT-based VLM training frameworks
- **Connection to R3V and Sherlock**:
  - R3V (Oct 2024) cites CURE and extends self-training to multimodal reasoning
  - Sherlock (May 2025) addresses self-correction limitation identified in CURE

---

## Quotes & Key Insights

> "The reliability of intermediate reasoning steps cannot be assured, irrespective of the accuracy of the final inference (and vice versa). This suggests VLMs are not always consistent in their reasoning."

> "Even the SOTA VLM (BLIP-2) falls short in comparison to human performance regarding overall visual reasoning performance...significant effort is needed to facilitate VLMs in achieving a level of visual reasoning comparable to that of humans in a systematic and consistent manner."

> "VLMs may produce inaccurate high-level inferences due to inconsistencies or hallucination in the rationales after this stage [SFT]."

> "The presence of the SFT stage enables VLMs to generate reasonable rationales. In its absence, CoTBLIP is restricted to producing only image captions or trivial rationales that do not contribute significantly to high-level inference."

**Key Insight 1: Consistency as Proxy for Verifiability**
CURE demonstrates that consistency between CoT steps and final answers can serve as a proxy for verifiability in the absence of external tools. However, this approach hits a fundamental ceiling: consistency measures internal coherence, not truthfulness to visual evidence. The model can be consistently wrong.

**Key Insight 2: SFT + RLAIF Necessity**
The ablation study reveals critical dependency: SFT is necessary to teach VLMs to generate reasonable CoT rationales, but insufficient for high-quality reasoning. RLAIF provides the calibration needed for better consistency and groundedness. Without SFT initialization, RLAIF fails (model produces trivial captions).

**Key Insight 3: Faithfulness Gap**
The large gap between model and human consistency (Cf: 83.1% vs 95.5%; Cb: 71.0% vs 91.4%) reveals that current VLMs lack systematic, consistent visual reasoning capabilities. This motivates the need for approaches like R3V and Sherlock that explicitly address self-improvement and self-correction.

**Critical Observation: Quadrant I Limitation**
CURE exemplifies the fundamental limitation of Quadrant I approaches: without external grounding mechanisms (tools, structured traces), verifiability relies entirely on internal consistency. This is low-cost and secure but cannot guarantee faithfulness to visual evidence. This limitation motivates moving toward Quadrant II (structured traces + tools) for higher verifiability.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant - Quadrant I: Text-only CoT)
- [x] Section 5 (Learning & Alignment - RLAIF for VLM alignment)
- [x] Section 6 (Evaluation & Benchmarks - CURE benchmark for consistency evaluation)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future - Limitations of consistency-based verification)

### Narrative Role

CURE serves as the **foundational anchor** for Quadrant I, demonstrating:

1. **Baseline Approach to Verifiability without Tools**: CURE establishes the paradigm of using internal consistency as verification signal. This is the simplest, lowest-cost approach to improving verifiability in VLM reasoning.

2. **Fundamental Limitations of Consistency-Based Verification**: 
   - Consistency ≠ Correctness: Model can generate multiple consistent but wrong reasoning chains
   - Consistency ≠ Faithfulness: CoT can be internally coherent but hallucinated
   - Human gap: Even best model (BLIP-2) shows 30% gap vs human on overall reasoning
   These limitations motivate the need for structured traces (Quadrant II/IV) and external verification (Quadrant II/III).

3. **Motivation for Self-Improvement Approaches**: CURE's RLAIF stage uses LLM feedback but cannot truly verify visual groundedness. This limitation motivates:
   - R3V: Uses answer correctness (verifiable signal) to bootstrap positive/negative samples
   - Sherlock: Uses trajectory-level self-correction with visual perturbation for preference construction

4. **Training without Human Annotations**: CURE demonstrates feasibility of training VLM reasoning capabilities using only LLM-generated data (LLaVA CoT + SBU captions with LLM feedback). This is an important precursor to R3V's self-training paradigm.

### Comparison Points

**Excels at**:
- Low cost/latency (no external tools, only LLM API calls for training)
- Security (closed system, no injection surface)
- Simplicity (purely textual CoT, easy to implement)
- Scalability (RLAIF can use web-scale image-caption data)

**Fails at**:
- True grounding (no explicit visual evidence pointers)
- Automatic verification (consistency checking cannot guarantee correctness)
- Replayability (no structured trace to re-execute)
- Faithfulness (hallucination risk in CoT generation)
- Generalization (limited to everyday scenes similar to training distribution)

**Contrast with Other Quadrants**:
- vs Quadrant II (VideoAgent): CURE has lower cost but much weaker grounding and checkability
- vs Quadrant III (text + execution): CURE has no execution feedback for verification
- vs Quadrant IV (structured + execution): CURE lacks formal rigor of program traces

---

## Notes

### Follow-up Items
- [x] Verified full author list and affiliations
- [x] Added arXiv link and code repository
- [x] Extracted specific benchmark results from Tables 2, 3 and Figures 4, 5
- [x] Reviewed connections to R3V and Sherlock
- [ ] Consider running additional analysis on CURE benchmark statistics (question type distribution, visual clue patterns)

### Questions
- How does CURE's consistency checking compare to standard self-consistency (Wang et al., 2022d) in LLMs? 
  - Answer: CURE extends self-consistency to multimodal setting with visual grounding concern. Standard self-consistency samples multiple solutions and takes majority vote. CURE measures bidirectional consistency (forward/backward) between CoT steps and final answer.
  
- What is the actual improvement in faithfulness metrics?
  - Answer: Paper does not report explicit faithfulness metrics. Reports consistency metrics (Cf, Cb) as proxy. CoTBLIP improves Cf from 83.66% to 86.67% (+3%), Cb from 70.71% to 71.09% (marginal). True faithfulness (grounding accuracy) not measured.
  
- Are there failure cases where consistency misled the evaluation?
  - Answer: Paper acknowledges this limitation but does not provide specific failure cases. States "reliability of intermediate reasoning steps cannot be assured" and hallucination is a failure mode. This is a known limitation of consistency-based approaches.

### Clarification on Quadrant Placement
CURE is placed in Quadrant I (Text-only CoT, No Tools) because:
- Representation: Free-form textual CoT (subquestions + answers), not structured traces
- Verification: Internal consistency checking, no external tools or execution
- Training: SFT + RLAIF with LLM feedback, no tool-use learning
This contrasts with:
- Quadrant II (VideoAgent): Structured memory + tool-augmented reasoning
- Quadrant III: Textual CoT + tool execution feedback
- Quadrant IV: Structured program traces + execution

---

## BibTeX

```bibtex
@inproceedings{chen2024measuring,
  title={Measuring and Improving Chain-of-Thought Reasoning in Vision-Language Models},
  author={Chen, Yangyi and Sikka, Karan and Cogswell, Michael and Ji, Heng and Divakaran, Ajay},
  booktitle={Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics},
  year={2024},
  url={https://arxiv.org/abs/2309.04461}
}
```

**Status:** ✅ Complete - Quadrant I Anchor Paper (Updated)

**Update Summary:**
- Added complete author list and affiliations
- Added arXiv URL and code repository link
- Filled in detailed methodology analysis with 2×2 matrix justification
- Expanded verifiability analysis across all 7 dimensions with specific evidence from paper
- Added comprehensive failure modes (5 modes with examples)
- Extracted specific evaluation results from tables and figures
- Detailed training data collection process for SFT and RLAIF stages
- Added connections to R3V and Sherlock papers
- Extracted key quotes and insights
- Completed BibTeX entry
- Total: ~280 lines
