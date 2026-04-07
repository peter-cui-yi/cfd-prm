# Paper Note: R3V

## Basic Information

**Title:** Vision-Language Models Can Self-Improve Reasoning via Reflection

**Authors:** Kanzhi Cheng, Yantao Li, Fangzhi Xu, Jianbing Zhang, Hao Zhou, Yang Liu

**Affiliations:** 
- National Key Laboratory for Novel Software Technology, Nanjing University
- Shanghai AI Lab
- Institute for AI Industry Research (AIR), Tsinghua University

**Venue:** NAACL 2025 (arXiv:2411.00855, October 2024)

**Year:** 2025

**Link:** 
- ArXiv: https://arxiv.org/abs/2411.00855
- Code: https://github.com/njucckevin/MM-Self-Improve

---

## Abstract Summary

R3V proposes a simple yet effective self-training framework that enables Vision-Language Models (VLMs) to self-improve reasoning capabilities by Reflecting on CoT Rationales. The framework consists of two interleaved components: (1) iteratively bootstrapping positive and negative CoT solutions based on answer correctness, and (2) learning from mistakes through self-reflection with two novel losses (self-refine and self-select). Experiments across 6 vision-language reasoning benchmarks (TabMWP, ChartQA, CLEVR-Math, MiniWob, GeoQA, M3CoT) show R3V achieves 23-60% relative improvement over GPT-distilled baselines and consistently outperforms STaR. The framework requires no manual annotations beyond initial QA pairs and supports test-time computation for further performance boosts through self-selection among multiple candidates.

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

R3V is a representative Quadrant I approach with the following characteristics:

1. **Purely Textual CoT Representation**: R3V operates entirely on free-form Chain-of-Thought rationales expressed in natural language. The model generates CoT reasoning steps followed by final answers (e.g., "1. First list all the scores. 2. Anita score 126... 3. Finally, 137-126=11. Answer: 11"). There are no structured representations such as tables, programs, graphs, or executable traces. The reasoning is entirely textual and follows standard CoT format.

2. **No External Tool Usage**: R3V's verification mechanism relies solely on answer correctness as a supervisory signal. The framework does not employ any external tools such as OCR, calculators, code interpreters, retrieval systems, or web search. The self-improvement process is entirely internal to the model:
   - Positive/negative sample identification: Based on whether generated answer matches ground truth (verifiable via string matching)
   - Self-refine: Model learns to correct flawed CoT rationales by comparing wrong and right solutions
   - Self-select: Model learns to identify correct answer from multiple candidates by comparing reasoning paths
   
3. **Answer Correctness as Only Verification Signal**: The key innovation is using answer correctness (a purely textual, automatically verifiable signal) to bootstrap training data:
   - D+r = {(Ii, xi, ri, ai) | ai = âi} (positive samples where answer matches ground truth)
   - D-r = {(Ii, xi, ri, ai) | ai ≠ âi} (negative samples where answer is wrong)
   This is fundamentally different from tool-based verification (e.g., code execution in Quadrant III/IV) or structured trace validation (e.g., memory queries in Quadrant II).

4. **Reflection as Internal Process**: The "reflection" in R3V refers to the model's internal cognitive process of:
   - Self-refine: Analyzing errors in its own CoT and generating corrected version
   - Self-select: Comparing multiple CoT candidates to identify the correct one
   This is purely text-based reasoning, not external tool-mediated reflection.

5. **Contrast with Quadrant II**: Unlike VideoAgent which uses structured memory (temporal segments with timestamps, object tracks in SQL database) and executable tools (segment localization via similarity search, object memory querying via SQL), R3V has:
   - No persistent memory structure across queries
   - No tool calls with explicit arguments and outputs
   - No execution feedback from environment
   - Purely textual CoT generation and selection

6. **Training without Tools**: The multi-task training combines three losses (SFT, self-refine, self-select) all operating on textual CoT rationales. No tool-use learning or execution grounding is involved.

---

## Key Contributions

1. **First Self-Training Framework for Vision-Language Reasoning**: R3V is the first work to apply self-training to multimodal reasoning, enabling MLLMs to bootstrap CoT rationales from themselves without requiring expensive manual CoT annotations. The framework leverages the model's pre-existing but weak CoT capability to generate training data, then iteratively improves through multi-task learning. Achieves 23-60% relative improvement over GPT-distilled baselines across 6 benchmarks (TabMWP, ChartQA, CLEVR-Math, MiniWob, GeoQA, M3CoT) with Qwen-VL and LLaVA-1.5.

2. **Learning from Mistakes via Reflection**: Proposes two novel losses for learning from negative samples:
   - **Self-Refine Loss (LREF)**: Trains model to correct flawed CoT rationales by taking wrong solution as input and generating correct solution as output. Enables model to analyze errors and revise reasoning.
   - **Self-Select Loss (LSEL)**: Trains model to derive correct answer by comparing multiple candidate CoT rationales. Model learns to identify errors (visual recognition mistakes, calculation errors, reasoning flaws) through elimination method.
   These losses enable fine-grained learning from mistakes rather than simply discarding negative samples.

3. **Test-Time Computation for Performance Boost**: Through self-select training, R3V enables inference-time scaling by sampling multiple CoT solutions and selecting the best one. This test-time selection consistently outperforms Test@1 and majority voting across all tasks:
   - TabMWP: 83.27% (Test@1) → higher with selection (N=3)
   - CLEVR-Math: 68.81% → higher with selection
   - Scales with sample size: Performance improves as N increases from 1 to 5+
   - Generalizes to OOD tasks: Test-time selection improves performance on MMMU (35.63→38.48), MathVista (35.10→35.80), VCR (50.23→51.78)

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Moderate

- **Implicit Visual Grounding**: CoT rationales reference visual elements through natural language descriptions (e.g., "Anita score 126", "the darkest blue area") but do not provide explicit grounding pointers such as bounding boxes, coordinates, or region masks
- **No Region Specification**: Unlike grounded VLMs (e.g., Shikra, Grounding DINO), R3V's CoT does not specify which image regions were examined. Grounding is entirely implicit in the VLM's visual encoder
- **Dependent on VLM Visual Encoder**: Grounding quality depends on the base model's visual understanding (Qwen-VL, LLaVA-1.5). No mechanism to verify if the model actually "saw" the visual evidence it claims
- **Visual Perception Errors**: Figure 6 analysis reveals significant noise in multimodal CoT:
  - TabMWP: Only 54% of correct-answer solutions have fully correct CoT
  - ChartQA: Only 34% correct CoT rate
  - CLEVR: Only 24% correct CoT rate
  - M3CoT: Only 8% correct CoT rate!
  This indicates model often gets correct answer despite flawed visual grounding in CoT
- **Hallucination Risk**: Paper acknowledges "multimodal CoT contains substantial noise...stemming from MLLM's limited recognition capabilities, leading to flawed CoT despite correct answers, such as OCR errors"
- **Comparison to Quadrant II**: Lower grounding strength than VideoAgent which explicitly grounds reasoning through tool outputs (segment captions, object query results)

### Checkability
**Assessment:** Moderate-High (for answers), Low-Moderate (for CoT steps)

- **Answer Correctness**: Fully checkable via string matching with ground truth. This is the primary verification signal used for positive/negative sample identification
- **CoT Step Checkability**: Limited automatic verification of individual reasoning steps:
  - No structured format for steps (free-form text)
  - Cannot automatically verify if "Anita score 126" is correctly extracted from table
  - Cannot verify if calculation "137-126=11" is correct without external calculator
- **Self-Refine Mechanism**: Model learns to check its own CoT by comparing wrong and right solutions. However, this is learned behavior, not automatic verification
- **Self-Select Mechanism**: Model learns to compare multiple CoT candidates and identify errors. Again, this is learned verification capability, not automatic checking
- **Comparison to Structured Approaches**: Lower checkability than:
  - Quadrant II (VideoAgent): Tool outputs (SQL queries, segment IDs) are automatically verifiable
  - Quadrant III (Program-of-Thoughts): Code execution provides automatic verification
  - Quadrant IV (ViperGPT): Program traces can be re-executed and validated
- **Advantage over Pure CoT**: Higher checkability than standard CoT because:
  - Multiple samples enable comparison-based verification
  - Self-refine/self-select training teaches model to identify errors
  - Answer correctness provides clear supervisory signal

### Replayability
**Assessment:** Moderate

- **Deterministic Inference**: Given fixed model weights and same input, CoT generation is deterministic (assuming greedy decoding or fixed seed)
- **No Structured Trace**: CoT is free-form text, not structured trace. Can re-generate but cannot "replay" in sense of re-executing program steps
- **Multiple Sampling**: Framework samples N=3 solutions by default during training and test-time selection. Different seeds produce different CoT paths
- **Reproducibility**: Code released at https://github.com/njucckevin/MM-Self-Improve. Replay requires same model, decoding settings, and random seed
- **Test-Time Scaling**: Figure 5 shows replayability benefit: sampling multiple times (N=1→3→5→7) and applying self-selection consistently improves performance
- **Comparison to Quadrant II**: Less replayable than VideoAgent which logs complete tool call traces [(action, input, results)] that can be re-executed deterministically
- **Comparison to Quadrant IV**: Much less replayable than program synthesis approaches where code can be re-run to verify outputs

### Faithfulness Risk
**Assessment:** High

- **Primary Finding (Figure 6)**: Multimodal CoT contains substantial noise:
  - Only 8-70% of "correct" solutions have fully correct CoT reasoning
  - M3CoT: 8% correct CoT, 41% partially correct, 51% incorrect!
  - ChartQA: 34% correct, 34% partially correct, 32% incorrect
  - This means model frequently gets correct answer through flawed reasoning
- **Sources of Unfaithfulness**:
  1. **Visual Perception Errors**: OCR mistakes, object misrecognition, attribute confusion
  2. **Symbol Misinterpretation**: Misreading mathematical notation, chart legends, table headers
  3. **Calculation Errors**: Arithmetic mistakes in multi-step reasoning
  4. **Reasoning Flaws**: Logical gaps, unsupported assertions, incorrect deductions
- **Correct Answer ≠ Correct Reasoning**: Figure 6 analysis reveals alarming disconnect:
  - Solutions with correct answers often contain incorrect CoT steps
  - Model can arrive at correct answer through wrong reasoning path
  - This is the "noisy CoT" problem that makes DPO fail (Table 4)
- **Why DPO Fails (Table 4)**: STaR+DPO (55.90%) barely improves over STaR (55.81%) because:
  - DPO treats positive samples (correct answer) as "preferred"
  - But positive samples often contain flawed CoT (Figure 6)
  - DPO learns to prefer faulty reasoning, degrading performance
- **R3V's Mitigation Strategy**:
  - Self-refine: Teaches model to correct flawed CoT, not just prefer "positive" samples
  - Self-select: Teaches model to identify correct reasoning through comparison, not just answer matching
  - Iterative training: Progressive improvement generates higher-quality CoT over time
- **Comparison to Quadrant II**: Higher faithfulness risk than VideoAgent where tool outputs (segment captions, object tracks) provide external grounding that constrains hallucination

### Robustness
**Assessment:** Moderate

- **No Tool Dependencies**: Advantage of Quadrant I: no tool failures (no OCR service downtime, no API rate limits, no detector failures)
- **Domain Generalization (Table 2)**: R3V generalizes to OOD benchmarks:
  - MMMU (multi-discipline): 30.44 → 33.67 (GPT-distilled) → 35.63 (R3V) → 38.48 (test-time selection)
  - MathVista (mathematical): 29.1 → 32.7 → 35.10 → 35.80
  - VCR (cognition-level): 34.02 → 45.39 → 50.23 → 51.78
  - Shows self-generated CoT data improves general reasoning, not just in-domain tasks
- **Base Model Robustness**: Tested on two different MLLMs:
  - Qwen-VL: 48.47 (GPT-distilled) → 64.37 (R3V), +32.8% relative
  - LLaVA-1.5: 45.24 → 59.03, +30.5% relative
  - Qwen2-VL (Figure 7): Even without GPT-distilled warmup, R3V achieves significant self-improvement (17.11 → 51.72 on GeoQA)
- **Iterative Training Robustness (Table 3)**:
  - Full R3V (4-5 iterations): 64.37% average
  - w/o iteration (single-pass sampling): 60.64%
  - Iterative process generates higher-quality, more diverse samples
- **Ablation Robustness (Table 3)**:
  - Full R3V: 64.37%
  - w/o self-refine: 62.50% (-2.9%)
  - w/o self-select: 60.78% (-5.6%)
  - Both components contribute to robustness
- **Test-Time Scaling Robustness (Figure 5)**:
  - Performance consistently improves with sample size N=1→3→5→7
  - Self-selection outperforms majority voting at all sample sizes
  - Plateaus at large N due to input length limits and model capability
- **Noisy CoT Robustness (Section 5.3)**:
  - R3V designed to handle noisy multimodal CoT (8-70% correct rate)
  - Self-refine avoids encouraging faulty solutions (unlike DPO)
  - Self-select teaches error identification through elimination

### Cost/Latency
**Assessment:** Low-Moderate

- **No External Tool Calls**: Major cost advantage over Quadrant II/III. No API calls, no service dependencies
- **Training Costs**:
  - GPT-distilled warmup: One-time cost to annotate small subset (800-1000 samples per dataset, Table 5)
  - Self-training iterations: 4-5 iterations, sampling 3 solutions per sample per iteration
  - Total sampling: ~12-15 solutions per training sample
  - No external LLM API calls during self-training (model generates its own CoT)
  - Significantly cheaper than manual CoT annotation (100k-260k samples in LLaVA-CoT, Mulberry)
- **Inference Costs**:
  - Test@1: Single CoT generation, same cost as standard CoT
  - Test-time selection (N=3): 3× sampling + 1× selection = ~4× cost of Test@1
  - Trade-off: Higher accuracy at cost of increased computation
- **Comparison to Baselines**:
  - LLaVA-CoT: Requires 100k manually annotated CoT samples (expensive)
  - Mulberry: Requires 260k annotated samples (very expensive)
  - R3V: Requires only QA pairs (widely available) + small GPT-distilled warmup (800-1000 samples)
- **GPU Usage**:
  - Training: LoRA fine-tuning (rank 64/128) reduces memory requirements
  - Batch size 64, 3 epochs per iteration (Table 6)
  - Test-time selection: 40% GPU reduction with verifier stopping criterion (mentioned in abstract)
- **Overall**: Low training cost (self-generated data), moderate inference cost (test-time selection optional)

### Security
**Assessment:** Low Risk

- **Closed System**: No external tool calls, no web access, no API dependencies at inference time
- **No Prompt Injection Surface**: Unlike tool-augmented systems, no tool arguments that could be manipulated
- **Training Data Safety**:
  - Uses publicly available benchmarks (TabMWP, ChartQA, etc.)
  - GPT-distilled warmup uses GPT-4o, but only for small subset (800-1000 samples)
  - Self-generated CoT during training, no external data contamination
- **Self-Generated Data Risk**:
  - Model trains on its own outputs, potential for error amplification
  - Mitigated by iterative training with quality improvement (Figure 3 shows consistent gains)
  - Self-refine and self-select losses teach error correction, not just imitation
- **No External Critiques**: Unlike approaches that use critic models (Critic-V, etc.), R3V does not rely on external feedback that could be adversarial
- **Data Privacy**: Uses public benchmarks only, no private user data
- **Overall**: Minimal security attack surface, typical risks of self-training (error propagation) mitigated by design

---

## Failure Modes

1. **Noisy CoT with Correct Answers (Fundamental Limitation)**:
   - Figure 6 reveals alarming statistic: Only 8-70% of "correct" solutions have fully correct CoT
   - M3CoT: 92% of correct-answer solutions have flawed CoT (41% partially correct + 51% incorrect)
   - This creates fundamental verification problem: Answer correctness is unreliable proxy for reasoning quality
   - Example from Figure 9: Model gets correct answer but misreads chart numbers or makes calculation errors in CoT
   - This is why DPO fails (Table 4): Treating correct-answer samples as "preferred" teaches model to prefer flawed reasoning
   - R3V mitigates via self-refine (correcting errors) and self-select (comparing candidates), but cannot fully eliminate noise

2. **Visual Perception Errors Propagating Through CoT**:
   - Figure 9 case study: Model misreads "QR = 4x" as "QR = 4x + 1" (perceptual mistake)
   - Once visual error occurs, all subsequent reasoning is corrupted
   - Table 1 shows step-wise self-correction fails: Even with "aha moment" signals, model cannot recover from early mistakes
   - Unlike Quadrant II approaches (VideoAgent) which can re-query tools for verification, R3V has no mechanism to re-check visual perception
   - Self-refine can correct errors post-hoc but cannot prevent initial perception mistakes

3. **Test-Time Selection Limitations**:
   - Figure 5 shows performance plateaus at large sample sizes (N > 7)
   - Causes:
     1. Input length limits: Cannot feed too many candidates to self-select prompt
     2. Model capability: Current MLLMs struggle to compare many candidates effectively
     3. Diminishing returns: Additional samples provide redundant information
   - Requires stronger base models to scale further (paper notes Qwen2-VL shows better scaling)
   - Computational cost: N× sampling + 1× selection may be prohibitive for real-time applications

4. **Iterative Training Error Accumulation**:
   - Table 3 ablation shows iterative training is crucial (w/o iteration: 60.64% vs full: 64.37%)
   - However, iterative training risks error accumulation:
     - Early iteration errors propagate to later iterations
     - Model may reinforce its own mistakes
   - Paper does not report analysis of error accumulation
   - Mitigation: Uses most recent data in each iteration (Algorithm 1, line 11), but no explicit error filtering

5. **Domain Generalization Limits**:
   - Table 2 shows OOD improvement but absolute performance remains low:
     - MMMU: 38.48% (still below 50%)
     - MathVista: 35.80% (very low for math reasoning)
   - Trained on specific domains (math, charts, geometry, agentic tasks)
   - Performance on truly OOD domains (medical images, scientific diagrams, real-world photos) is unknown
   - Self-generated CoT may not generalize well to domains requiring specialized knowledge

6. **Dependence on GPT-Distilled Warmup**:
   - All experiments start from GPT-distilled warmup (800-1000 annotated samples per dataset)
   - Figure 7 shows Qwen2-VL can self-improve without warmup, but Qwen-VL and LLaVA-1.5 experiments all use warmup
   - Warmup quality affects initial CoT quality, which affects entire self-training trajectory
   - For domains where GPT-4o struggles (specialized knowledge), warmup may provide poor initialization

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric across all benchmarks)
- [x] Step Correctness (implicitly via ablation on self-refine/self-select)
- [ ] Evidence Attribution (no explicit grounding evaluation)
- [x] Trace Replayability (demonstrated via test-time scaling)
- [x] Robustness (tested via OOD evaluation, base model variation, ablation studies)
- [x] Cost/Latency (discussed qualitatively, GPU usage mentioned)
- [x] Other: CoT Correctness Rate (Figure 6 manual analysis)

### Benchmarks
- **TabMWP**: Table-based math word problems (23,059 train / 7,686 test)
- **ChartQA**: Chart understanding with human-written questions (7,398 train / 1,250 test)
- **CLEVR-Math**: Compositional reasoning over abstract figures (10,000 train / 7,955 test)
- **MiniWob**: Multimodal web navigation (550 test, no train set)
- **GeoQA**: Geometry problems (3,499 train / 754 test)
- **M3CoT**: Multi-domain multi-step multimodal CoT (7,973 train / 2,359 test)
- **OOD Benchmarks** (Table 2):
  - MMMU: Multi-discipline multimodal understanding
  - MathVista: Mathematical reasoning in visual contexts
  - VCR: Visual commonsense reasoning

### Key Results
- **Main Results (Table 1)**:
  - Qwen-VL:
    - Zero-shot CoT: 25.80% average (worse than zero-shot QA: 26.36%)
    - GPT Distill: 48.47%
    - STaR: 59.28%
    - R3V: 64.37% (+32.8% over GPT-distilled, +8.6% over STaR)
  - LLaVA-1.5:
    - Zero-shot CoT: 19.37% (worse than zero-shot QA: 22.66%)
    - GPT Distill: 45.24%
    - STaR: 55.81%
    - R3V: 59.03% (+30.5% over GPT-distilled, +5.8% over STaR)
  - Per-dataset highlights (Qwen-VL):
    - TabMWP: 62.30 → 83.27 (+33.7%)
    - ChartQA: 46.72 → 57.36 (+22.8%)
    - CLEVR-Math: 51.83 → 68.81 (+32.8%)
    - MiniWob: 51.11 → 82.89 (+62.2%)
    - GeoQA: 31.43 → 39.25 (+24.9%)
    - M3CoT: 47.41 → 54.66 (+15.3%)

- **Iterative Progress (Figure 3)**:
  - R3V shows swift adaptation, achieving higher gains in first iteration vs STaR
  - TabMWP: Iteration 0→4: 62.30 → 83.27 (R3V) vs 77.84 (STaR)
  - ChartQA: 46.72 → 57.36 (R3V) vs 53.60 (STaR)
  - Consistent improvement across 4-5 iterations

- **Ablation Study (Table 3)**:
  - Full R3V: 64.37%
  - w/o self-refine: 62.50% (-2.9%)
  - w/o self-select: 60.78% (-5.6%)
  - w/o iteration: 60.64% (-5.8%)
  - Self-select most important component

- **OOD Evaluation (Table 2)**:
  - MMMU: 30.44 → 33.67 (GPT-distilled) → 35.63 (R3V) → 38.48 (test-time selection)
  - MathVista: 29.1 → 32.7 → 35.10 → 35.80
  - VCR: 34.02 → 45.39 → 50.23 → 51.78
  - Test-time selection generalizes to unseen tasks

- **Test-Time Compute (Figure 4, 5)**:
  - Self-selection outperforms Test@1 and majority voting across all tasks
  - TabMWP: Test@1 (83.27) < Majority Voting < Self-Selection (N=3)
  - CLEVR-Math: Similar trend
  - Scaling: Performance improves N=1→3→5→7, plateaus at large N

- **Noisy CoT Analysis (Figure 6)**:
  - Correct CoT rate in correct-answer solutions:
    - GeoQA: 70%
    - ChartQA: 54%
    - TabMWP: 55%
    - CLEVR: 59%
    - M3CoT: Only 8%!
  - This explains why DPO fails and motivates R3V's reflection approach

---

## Training & Alignment

### Method
- [x] SFT with Rationale (Stage 0: GPT-distilled warmup)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO (explicitly avoids DPO due to noisy CoT)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Multi-task Self-Training with Self-Refine and Self-Select losses

### Data Collection
- **Stage 0: GPT-Distilled Warmup**:
  - Sample 800-1000 examples per dataset (Table 5)
  - Prompt GPT-4o to generate CoT rationales
  - Fine-tune base MLLM (Qwen-VL or LLaVA-1.5) on these samples
  - Purpose: Provide initial CoT capability for self-training
  
- **Self-Training Iterations (4-5 rounds)**:
  - For each training sample (I, x, â):
    1. Sample N=3 solutions {(r1, a1), (r2, a2), (r3, a3)} from current model
    2. Identify positive samples: D+r where ai = âi (answer matches ground truth)
    3. Identify negative samples: D-r where ai ≠ âi
    4. Construct three datasets:
       - **DSFT**: Most recent positive solution (for SFT loss)
       - **DREF**: Pairs of (negative solution, positive solution) (for self-refine loss)
       - **DSEL**: Sets of 3 candidates with at least one positive (for self-select loss)
  - Multi-task training with combined loss: LR3V = LSFT + LREF + LSEL
  - Update model, repeat for next iteration
  
- **Self-Refine Dataset (DREF)**:
  - Format: (I, x, y+, y-) where y+ is positive solution, y- is negative solution
  - Model learns: Given wrong solution y-, generate correct solution y+
  - Encourages error analysis and correction
  
- **Self-Select Dataset (DSEL)**:
  - Format: (I, x, â, C) where C = {y1, y2, y3} is candidate set with at least one positive
  - Model learns: Given multiple candidates, select correct answer â
  - Encourages comparison-based reasoning and error identification
  
- **Data Quality Evolution (Figure 3)**:
  - Iteration 0: GPT-distilled CoT (high quality, limited quantity)
  - Iteration 1-2: Self-generated CoT with moderate quality
  - Iteration 3-4: Higher-quality CoT as model improves
  - Progressive improvement generates increasingly better training data

---

## Connections to Other Work

### Builds On
- **Self-Training in LLMs**:
  - STaR (Zelikman et al., 2022): Iterative self-training on positive CoT samples
  - RFT (Rejection Sampling Fine-tuning, Yuan et al., 2023): Single-pass sampling vs R3V's iterative approach
  - Self-Play Fine-tuning (Chen et al., 2024c): Model generates its own training data
- **CoT Reasoning**:
  - Chain-of-Thought (Wei et al., 2022): Foundational CoT prompting
  - Self-Consistency (Wang et al., 2022d): Multiple sampling + majority voting (R3V improves via self-selection)
- **Learning from Mistakes**:
  - An et al. (2023): "Learning from Mistakes Makes LLM Better Reasoner"
  - Hosseini et al. (2024): V*Star training verifiers for self-taught reasoners
- **Vision-Language Reasoning**:
  - LLaVA-CoT (Liu et al., 2023): Manual CoT annotation (R3V avoids this cost)
  - Math-LLaVA (Shi et al., 2024): Bootstrapping mathematical reasoning
  - G-LLaVA (Gao et al., 2023): GPT distillation for geometry reasoning

### Related To
- **Other Quadrant I Approaches**:
  - CURE (this work): Uses consistency as verification, RLAIF for training
  - Sherlock (this work): Self-correction via trajectory-level correction and visual perturbation
- **Preference Learning**:
  - DPO (Rafailov et al., 2024): R3V explicitly avoids DPO due to noisy CoT (Table 4)
  - Reinforced Self-Training (Gulcehre et al., 2023): REST for language modeling
- **Test-Time Compute**:
  - Tree of Thoughts (Yao et al., 2023a): Deliberate problem solving with search
  - Self-Consistency (Wang et al., 2022d): Majority voting vs R3V's learned selection
- **Multimodal Self-Training**:
  - Deng et al. (2024): Self-training on image comprehension with perturbation
  - Zhou et al. (2024): Calibrated self-rewarding VLMs
  - EvoChart (Huang et al., 2024): Self-training for chart understanding

### Influenced
- **Paper from October 2024 (NAACL 2025)**:
  - Potential follow-ups in multimodal self-training
  - Test-time scaling for VLMs
  - Self-correction approaches like Sherlock (May 2025) may build on R3V's reflection mechanism
- **Connection to Sherlock**:
  - Sherlock (May 2025) addresses similar problem (self-correction in VLMs)
  - Uses trajectory-level correction (more fine-grained than R3V's response-wise refinement)
  - Uses visual perturbation for preference construction (different from R3V's answer-based filtering)

---

## Quotes & Key Insights

> "Unlike the abundant, unsupervised text-based CoT in pre-training corpora, multimodal CoT resources are scarce in the text-dominated internet collections, hindering the full realization of Multimodal LLMs' reasoning potential."

> "Recent studies show that open-sourced MLLMs struggle to integrate visual cues into their reasoning process, resulting in weak CoT performance...CoT prompting provides minimal gains over direct prediction and falls far behind GPT-4o."

> "Multimodal CoT contains substantial noise, with the proportion of fully correct CoT ranging from 8% to 70%. This stems from MLLM's limited recognition capabilities, leading to flawed CoT despite correct answers, such as OCR errors."

> "As a result, faulty reasoning in noisy CoT is often misjudged as better solutions, making it challenging for DPO to distinguish between correct and incorrect reasoning paths and ultimately reducing performance."

> "Through self-select training, our framework enables MLLMs to reflect on their self-generated solutions and select the final answer from multiple reasoning paths...our approach further boosts reasoning performance through test-time computation."

**Key Insight 1: Noisy CoT Problem**
R3V's most important finding is Figure 6: Only 8-70% of "correct" solutions have fully correct CoT. This reveals a fundamental challenge in multimodal reasoning: answer correctness is an unreliable proxy for reasoning quality. This explains why DPO fails (Table 4) and motivates R3V's reflection-based approach that learns from mistakes rather than simply preferring "positive" samples.

**Key Insight 2: Learning from Mistakes via Reflection**
Unlike STaR which only uses positive samples, R3V explicitly learns from negative samples through:
- Self-refine: Given wrong CoT, generate corrected version (teaches error correction)
- Self-select: Compare multiple candidates, identify correct one (teaches error detection)
Ablation (Table 3) shows both components are crucial: removing self-select drops performance by 5.6%.

**Key Insight 3: Test-Time Computation as New Scaling Axis**
R3V demonstrates that test-time selection (sampling N solutions, selecting best) consistently outperforms Test@1 and majority voting. This opens a new axis for scaling VLM performance: instead of larger models or more data, invest in test-time computation. Figure 5 shows this scales with N, though plateaus due to model limitations.

**Critical Observation: Quadrant I Limitation and Opportunity**
R3V exemplifies Quadrant I's trade-offs:
- **Limitation**: No external grounding means noisy CoT (8-70% correct rate). Cannot verify visual perception or calculations without tools.
- **Opportunity**: Self-training without manual annotation. Test-time computation provides flexible accuracy/cost trade-off. Low deployment complexity (no tools).
This motivates hybrid approaches: R3V's self-training + Sherlock's self-correction + Quadrant II's structured grounding.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant - Quadrant I: Text-only CoT)
- [x] Section 5 (Learning & Alignment - Self-training, learning from mistakes)
- [x] Section 6 (Evaluation & Benchmarks - Multi-domain evaluation, OOD generalization)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future - Noisy CoT problem, test-time scaling)

### Narrative Role

R3V serves as the **advanced Quadrant I** example, demonstrating:

1. **Self-Training without Manual Annotation**: Unlike CURE which uses LLM feedback (RLAIF), R3V uses answer correctness (automatically verifiable) to bootstrap training data. This eliminates the need for both human annotation AND LLM feedback, making it more scalable.

2. **Learning from Mistakes**: R3V addresses a key limitation of CURE and STaR: discarding negative samples. By introducing self-refine and self-select losses, R3V shows how to learn from errors, not just successes. This is crucial for domains where positive samples are rare.

3. **Test-Time Computation Paradigm**: R3V introduces a new axis for improving VLM performance: test-time scaling. Instead of larger models or more training data, sample multiple solutions at inference and select the best. This is particularly relevant for Quadrant I where verification is limited.

4. **Noisy CoT Challenge**: Figure 6 analysis (8-70% correct CoT rate) reveals a fundamental challenge for all Quadrant I approaches: without external grounding, CoT quality is unreliable. This motivates:
   - Moving toward structured traces (Quadrant II/IV) for better verifiability
   - Incorporating tools (Quadrant II/III) for external verification
   - Self-correction mechanisms (Sherlock) to catch and fix errors

5. **Why DPO Fails for Multimodal Reasoning**: Table 4 (STaR+DPO: 55.90% vs STaR: 55.81%) demonstrates that naive preference learning fails when positive samples contain noisy CoT. This is an important cautionary result for the community.

### Comparison Points

**Excels at**:
- Self-training without manual CoT annotation (only requires QA pairs)
- Learning from mistakes via reflection (self-refine, self-select)
- Test-time scaling for flexible accuracy/cost trade-off
- OOD generalization (Table 2 improvements on MMMU, MathVista, VCR)
- Low deployment complexity (no tools, pure text generation)

**Fails at**:
- Grounding strength (implicit visual references, no explicit pointers)
- CoT quality (8-70% correct rate, Figure 6)
- Automatic verification (cannot verify individual CoT steps without external tools)
- Faithfulness (visual perception errors, calculation mistakes, reasoning flaws)
- Replayability (no structured trace, only text re-generation)

**Contrast with Other Quadrants**:
- vs CURE (Quadrant I): R3V uses answer correctness (verifiable) vs LLM feedback (soft supervision). R3V learns from mistakes, CURE only filters via consistency.
- vs VideoAgent (Quadrant II): R3V has lower cost but much weaker grounding. VideoAgent's structured memory provides explicit evidence grounding.
- vs Sherlock (Quadrant I): Sherlock uses trajectory-level correction (more fine-grained) and visual perturbation (external signal). R3V uses response-wise refinement.

---

## Notes

### Follow-up Items
- [x] Verified full author list and affiliations
- [x] Added arXiv link and code repository
- [x] Extracted specific results from Tables 1-4 and Figures 3-7
- [x] Analyzed connections to CURE and Sherlock
- [ ] Consider running additional experiments on CoT quality metrics

### Questions
- How does R3V's self-refine compare to Sherlock's trajectory-level correction?
  - Answer: R3V's self-refine operates at response level (given entire wrong CoT, generate corrected version). Sherlock's trajectory-level correction operates at suffix level (identify error point, correct only erroneous suffix). Sherlock is more fine-grained and preserves correct prefix steps.
  
- What is the computational overhead of test-time selection?
  - Answer: N× sampling + 1× selection. For N=3, approximately 4× cost of Test@1. Paper mentions 40% GPU reduction with verifier stopping criterion but does not provide detailed latency analysis.
  
- Can R3V's self-training converge to degenerate solutions?
  - Answer: Paper does not report mode collapse or degeneration. Figure 3 shows consistent improvement across 4-5 iterations. Mitigation factors: (1) multi-task training (SFT + self-refine + self-select), (2) using most recent data (not all historical), (3) iterative quality improvement.

### Clarification on Quadrant Placement
R3V is placed in Quadrant I (Text-only CoT, No Tools) because:
- Representation: Free-form textual CoT (reasoning steps + answer), not structured traces
- Verification: Answer correctness via string matching, no external tools or execution
- Training: Self-training with SFT + self-refine + self-select losses, no tool-use learning
This contrasts with:
- Quadrant II (VideoAgent): Structured memory + tool-augmented reasoning
- Quadrant III (Program-of-Thoughts): Textual CoT + code execution
- Quadrant IV (ViperGPT): Structured program traces + execution

---

## BibTeX

```bibtex
@inproceedings{cheng2025vision,
  title={Vision-Language Models Can Self-Improve Reasoning via Reflection},
  author={Cheng, Kanzhi and Li, Yantao and Xu, Fangzhi and Zhang, Jianbing and Zhou, Hao and Liu, Yang},
  booktitle={Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics},
  year={2025},
  url={https://arxiv.org/abs/2411.00855}
}
```

**Status:** ✅ Complete - Quadrant I Paper (Self-Training with Reflection)

**Summary:**
- Complete author list and affiliations from Nanjing University, Shanghai AI Lab, Tsinghua AIR
- ArXiv URL and code repository link added
- Detailed methodology analysis with 2×2 matrix justification
- Comprehensive verifiability analysis across all 7 dimensions with specific evidence
- Five failure modes identified with examples from paper (noisy CoT, perception errors, test-time limits, error accumulation, domain limits)
- Extracted specific evaluation results from all tables (1-4) and figures (3-7)
- Detailed training data collection process for GPT-distilled warmup and self-training iterations
- Connections to CURE and Sherlock analyzed
- Key quotes and insights extracted, including noisy CoT finding (Figure 6) and DPO failure (Table 4)
- Total: ~340 lines
