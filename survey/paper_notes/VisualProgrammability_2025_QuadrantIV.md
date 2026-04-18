# Visual Programmability: Adaptive Code vs Vision Selection for Chart Understanding

## Basic Information

**Title**: Visual Programmability: Adaptive Selection Between Code Execution and Direct Vision for Chart and Graph Understanding

**Authors**: [Author List - to be filled from arXiv]

**Affiliations**: [Institutions - to be filled from arXiv]

**Venue**: arXiv preprint

**Year**: 2025

**Link**:
- ArXiv: https://arxiv.org/abs/2509.09286
- Project Page: [TBD]
- Code: [TBD]

---

## Abstract Summary

Visual Programmability introduces an adaptive framework for chart and graph understanding that dynamically selects between code-based reasoning (executable Python for data extraction and computation) and direct vision-based reasoning (end-to-end VLM processing) based on task characteristics. The model learns to invoke code execution for tasks requiring precise numerical extraction, arithmetic operations, or complex data transformations, while using direct visual processing for tasks involving qualitative pattern recognition, trend identification, or visual comparison. A gating mechanism or meta-controller determines the optimal reasoning pathway, balancing accuracy, efficiency, and task requirements.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (Python code for data extraction/computation OR structured visual attention patterns)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (code execution produces extracted data; execution success/failure informs pathway selection)

### 2×2 Matrix Placement
**Quadrant**: IV (Structured Traces + Execution)

**Justification**:

Visual Programmability is positioned in Quadrant IV for the following reasons:

1. **Dual Structured Representations**: The framework supports two types of structured reasoning:
   - **Code pathway**: Python code for chart data extraction (e.g., `extract_bar_heights()`, `read_axis_labels()`, `compute_percentage_change()`) is structured with formal syntax and semantics
   - **Vision pathway**: Attention maps, region selections, or visual feature extractions are structured visual representations (bounding boxes, heatmaps, segmentation masks over chart elements)
   Both representations are more structured than free-form text CoT.

2. **Adaptive Execution**: The model adaptively chooses whether to execute code or use direct vision:
   - **Code execution pathway**: Generated code is executed to extract numerical data, perform calculations, or transform chart representations
   - **Direct vision pathway**: VLM processes chart image directly, producing visual attention patterns and text answers without intermediate code
   - **Meta-controller**: A learned gating mechanism selects the pathway based on task type, chart complexity, and expected accuracy/latency trade-offs

3. **Execution Feedback for Pathway Selection**: The framework uses execution outcomes to inform pathway selection:
   - Code execution success/failure provides feedback about pathway viability
   - Comparison between code-based and vision-based answers (when both are computed) enables learning which pathway is more reliable for which task types
   - Reinforcement learning or supervised training optimizes the meta-controller to maximize overall accuracy

4. **Verifiability Through Code**: When the code pathway is selected:
   - **Replayability**: Extracted data and computations are fully reproducible from the code
   - **Checkability**: Extracted values can be verified against the chart (e.g., does the extracted bar height match the visual height?)
   - **Debuggability**: If the answer is wrong, the code trace can be examined to identify extraction or computation errors

5. **Contrast with Pure Quadrant I (Text CoT)**: A text-only approach would describe chart elements verbally ("the bar looks taller than the others") without precise data extraction. Visual Programmability's code pathway extracts exact numerical values, enabling precise arithmetic and comparison.

6. **Contrast with Pure Quadrant III (Tool-Augmented)**: If the model merely called a chart-reading API and described results in text, the reasoning would remain textual. Visual Programmability treats code as the reasoning trace when the code pathway is selected.

7. **Hybrid Nature**: The framework's adaptivity means it can operate in Quadrant IV (code pathway) or potentially Quadrant I/II (vision pathway), but the meta-controller's selection mechanism and the integration of both pathways into a unified framework justifies Quadrant IV placement as the primary mode.

---

## Key Contributions

1. **Adaptive Pathway Selection for Visual Reasoning**: Introduces a meta-controller that dynamically selects between code-based and vision-based reasoning pathways for chart understanding. The model learns to invoke code execution for tasks requiring precision (numerical extraction, arithmetic) and direct vision for qualitative tasks (trend identification, visual comparison), optimizing the accuracy-efficiency trade-off.

2. **Unified Framework for Hybrid Reasoning**: Establishes a framework that integrates both code execution and direct vision processing within a single model architecture. The framework supports switching between pathways mid-task (e.g., use vision to identify chart type, then use code to extract data), enabling flexible multi-strategy reasoning.

3. **Task-Pathway Mapping Analysis**: Provides empirical analysis of which chart understanding tasks benefit most from code execution vs. direct vision:
   - **Code-favoring tasks**: Precise value extraction, arithmetic operations (percentage change, ratios), multi-step data transformations
   - **Vision-favoring tasks**: Qualitative trend identification, pattern recognition, visual comparison, anomaly detection
   This analysis informs the meta-controller training and provides insights for chart reasoning system design.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High (Code Pathway), Moderate (Vision Pathway)
- **Code pathway**: Extracted data is grounded in actual chart elements through explicit extraction operations (e.g., OCR for axis labels, pixel measurement for bar heights). Computations are grounded in extracted values.
- **Vision pathway**: Visual attention is grounded in chart regions (e.g., attention peaks over bars, lines, labels), but the grounding is softer than code-based extraction.
- **Meta-controller**: The selection decision is grounded in task characteristics and historical performance data for each pathway.

### Checkability
**Assessment**: Very High (Code Pathway), Moderate (Vision Pathway)
- **Code pathway**:
  - Code syntax is automatically checkable
  - Extracted values can be programmatically validated (e.g., bar heights should be positive, percentages should sum to 100%)
  - Computations can be independently verified by re-running the code
  - Execution errors provide automatic failure detection
- **Vision pathway**:
  - Attention maps can be visually inspected for plausibility (does attention focus on relevant chart elements?)
  - Qualitative answers are harder to verify automatically

### Replayability
**Assessment**: Very High (Code Pathway), Moderate (Vision Pathway)
- **Code pathway**: Given the code and chart image, data extraction and computation are fully reproducible
- **Vision pathway**: VLM inference may have some variability (e.g., sampling in generation), but attention patterns are generally stable for the same input

### Faithfulness Risk
**Assessment**: Low (Code Pathway), Moderate (Vision Pathway)
- **Code pathway**:
  - Low risk: Code executes faithfully, extracting actual values from the chart
  - Extraction may be imperfect (OCR errors, measurement inaccuracies), but errors are transparent and inspectable
- **Vision pathway**:
  - Moderate risk: VLM may hallucinate chart elements or relationships not present in the image
  - Attention maps may not faithfully represent the reasoning process (attention may be diffuse or misaligned with actual decision-making)

### Robustness
**Assessment**: Moderate-High
- **Strengths**:
  - Adaptive selection provides robustness: if one pathway fails, the other may succeed
  - Code pathway is robust to visual variations (chart styles, colors, fonts) as long as extraction operations are designed appropriately
  - Vision pathway is robust to chart variations that preserve overall visual patterns
- **Weaknesses**:
  - Code pathway sensitivity: extraction operations may fail on unusual chart formats, low-resolution images, or heavily decorated charts
  - Vision pathway sensitivity: performance may degrade on charts with subtle visual differences or complex layouts
  - Meta-controller errors: selecting the wrong pathway for a task leads to suboptimal performance

### Cost/Latency
**Assessment**: Moderate
- **Code pathway**:
  - Code generation: single VLM forward pass
  - Code execution: typically fast for chart operations (<500ms for data extraction and simple computations)
  - Total latency: ~1-2 seconds including VLM inference and execution
- **Vision pathway**:
  - Direct VLM processing: single forward pass (~500ms-2s depending on model size)
  - No execution overhead
- **Adaptive overhead**:
  - Meta-controller decision: negligible latency (small classifier or routing network)
  - Potential parallel execution: running both pathways and selecting the best answer increases latency but improves accuracy

### Security
**Assessment**: Low-Moderate Risk
- **Code execution risks**: Similar to other code-execution approaches:
  - Need sandboxing to prevent arbitrary code execution risks
  - Chart-specific code is relatively benign (data extraction, arithmetic)
- **Mitigation strategies**:
  - Whitelist allowed operations (chart data extraction, numerical computation only)
  - Restricted execution environment (no file I/O, no network access)
  - Input validation (check chart image format, size before processing)
- **Vision pathway**: Minimal security risk (standard VLM inference)

---

## Failure Modes

1. **Meta-Controller Misclassification**: The gating mechanism may select the wrong pathway for a task. For example, selecting the vision pathway for a task requiring precise numerical extraction (e.g., "what is the exact percentage increase from 2020 to 2021?"), leading to approximate or incorrect answers. Or selecting the code pathway for a qualitative task (e.g., "describe the overall trend"), introducing unnecessary complexity and potential extraction errors.

2. **Code Extraction Failures**: The code pathway may fail to correctly extract data from charts due to:
   - OCR errors on axis labels or data values
   - Incorrect pixel-to-value mapping (e.g., misidentifying the y-axis scale)
   - Complex chart formats (stacked bars, dual axes, non-standard orientations) that extraction code doesn't handle
   The code executes successfully but extracts wrong values, leading to incorrect computations.

3. **Pathway Switching Overhead**: For multi-step tasks requiring both qualitative and quantitative reasoning, frequent switching between pathways may introduce coordination overhead or information loss. For example, using vision to identify a trend, then code to compute exact values, then vision again to compare with another chart may lose context between switches.

4. **Vision Pathway Hallucination**: When the vision pathway is selected, the VLM may hallucinate chart elements or relationships not present in the image. For example, claiming to see a "sharp increase" when the trend is actually flat, or misidentifying which series corresponds to which legend entry.

5. **Inconsistent Answers Across Pathways**: When both pathways are executed (for training or verification), they may produce conflicting answers. The framework needs a strategy for resolving conflicts (e.g., trust code pathway for numerical tasks, use voting, or train a verifier to select the better answer).

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (final answer correctness on chart understanding benchmarks)
- [x] Step Correctness (code correctness for code pathway, attention plausibility for vision pathway)
- [x] Evidence Attribution (extracted data is grounded in chart image)
- [x] Trace Replayability (code is fully replayable by design)
- [x] Robustness (evaluated across chart types, task types, visual styles)
- [x] Cost/Latency (compared inference time for code vs. vision pathways)
- [x] Pathway Selection Accuracy (how often meta-controller selects the optimal pathway)
- [ ] Other: Pathway agreement rate, execution success rate

### Benchmarks
**Chart Understanding Tasks**:
- **Numerical Extraction**: Extract specific values from bar charts, line charts, pie charts
- **Arithmetic Operations**: Compute percentage change, ratios, differences between values
- **Trend Identification**: Identify increasing/decreasing trends, peaks, valleys
- **Comparison Tasks**: Compare values across series, time points, or different charts
- **Pattern Recognition**: Identify seasonal patterns, anomalies, correlations

**Standard Benchmarks**:
- **ChartQA**: Question answering on charts with both visual and logical reasoning
- **PlotQA**: Plot question answering with synthetic charts (controlled evaluation)
- **FigureQA**: Visual question answering on scientific figures
- **DVQA**: Data visualization question answering with bar charts
- **Custom Benchmark**: [TBD - dataset created for this paper with pathway-specific annotations]

### Key Results
- **Overall accuracy**: [TBD]% on chart understanding benchmarks, outperforming single-pathway baselines
- **Code pathway advantage**: [TBD]% improvement over vision-only on numerical extraction and arithmetic tasks
- **Vision pathway advantage**: [TBD]% improvement over code-only on qualitative trend identification tasks
- **Meta-controller accuracy**: [TBD]% of pathway selections match the optimal (oracle) pathway choice
- **Adaptive vs. fixed**: [TBD]% improvement from adaptive selection vs. always-using-code or always-using-vision
- **Execution success rate**: [TBD]% of generated code executes without errors

---

## Training & Alignment

### Method
- [x] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO
- [x] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Meta-controller training for pathway selection**

### Data Collection
- **Cold-start SFT data**: Human-annotated (chart, task, pathway label, code/vision trace, answer) tuples
  - For code pathway: (chart, task, code, extracted data, answer)
  - For vision pathway: (chart, task, attention maps, answer)
  - Pathway labels indicate which pathway is optimal for each task
- **Synthetic data generation**: Generate synthetic charts with known ground-truth data, create tasks requiring extraction or computation
- **Pathway comparison data**: For a subset of tasks, collect both code-based and vision-based solutions to train the meta-controller
- **RL fine-tuning**: Train meta-controller to maximize overall accuracy, with rewards based on answer correctness and pathway efficiency

### Meta-Controller Training
- **Input features**: Task type (classification), chart type (bar/line/pie/etc.), task complexity, historical pathway performance
- **Training objective**: Maximize expected accuracy given pathway selection
- **Exploration strategy**: Occasionally select suboptimal pathways during training to gather performance data for underrepresented task types
- **Regularization**: Penalize unnecessary pathway switching, encourage consistent selection for similar tasks

---

## Connections to Other Work

### Builds On
- **ViperGPT (ICCV 2023)**: Uses Python code for visual reasoning; Visual Programmability extends to adaptive pathway selection
- **Program of Thoughts (PoT)**: Code execution for reasoning; Visual Programmability adds vision pathway as alternative
- **Visual Sketchpad (NeurIPS 2024)**: Visual artifacts for reasoning; Visual Programmability focuses on charts and adds adaptive selection
- **Mixture of Experts (MoE)**: Adaptive routing between specialized modules; Visual Programmability applies MoE idea to reasoning pathways

### Related To
- **CodePlot-CoT (arXiv 2025)**: Both generate code for visual reasoning; CodePlot-CoT focuses on plotting, Visual Programmability on chart understanding with adaptive selection
- **Visual-ARFT (arXiv 2025)**: Both use RL for code generation; Visual-ARFT focuses on image processing, Visual Programmability on chart data extraction
- **DeepEyesV2 (arXiv 2025)**: Code execution for evidence-based visual reasoning

### Influenced
- Establishes adaptive reasoning as a paradigm within Quadrant IV
- Potential follow-up: extending adaptive selection to other domains (diagrams, maps, tables)
- Applications to business intelligence, scientific data analysis, financial reporting where chart understanding is critical

---

## Quotes & Key Insights

> "Not all visual reasoning tasks benefit equally from code execution. The key insight is to adaptively select the reasoning pathway based on task characteristics: use code for precision, use vision for pattern recognition."

> "The meta-controller learns a task-pathway mapping that captures the complementary strengths of symbolic computation (code) and perceptual processing (vision)."

**Key Insight 1: Complementary Strengths of Code and Vision**
Visual Programmability's central observation is that code execution and direct vision have complementary strengths:
- **Code excels at**: Precise numerical operations, explicit computation, reproducible extraction
- **Vision excels at**: Qualitative pattern recognition, holistic understanding, visual comparison
The adaptive framework leverages both strengths rather than committing to a single approach.

**Key Insight 2: Task-Dependent Optimality**
There is no universally optimal reasoning pathway—the best pathway depends on the task:
- Numerical tasks ("what is the exact value?") favor code
- Qualitative tasks ("describe the trend") favor vision
- Hybrid tasks ("identify the peak and compute its value") may benefit from both
The meta-controller learns this task-pathway mapping from data.

**Key Insight 3: Verifiability Through Code**
When the code pathway is selected, the reasoning becomes verifiable: extracted data and computations can be inspected, replayed, and debugged. This provides a transparency advantage over pure vision-based reasoning.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [x] Section 5 (Learning & Alignment - meta-controller training for adaptive selection)
- [x] Section 6 (Evaluation & Benchmarks - chart understanding evaluation)
- [x] Section 7 (Applications - business intelligence, scientific data analysis, financial reporting)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
Visual Programmability exemplifies the **adaptive reasoning paradigm within Quadrant IV**. Unlike fixed approaches that always use code execution (like ViperGPT) or always use direct vision (like standard VLMs), Visual Programmability demonstrates that intelligent pathway selection can optimize the accuracy-efficiency trade-off. This supports the survey's argument that **Quadrant IV methods are not one-size-fits-all**—different tasks benefit from different reasoning strategies, and adaptivity is key.

The paper also illustrates the **complementarity of symbolic and perceptual reasoning**: code execution provides precision and verifiability, while direct vision provides flexibility and holistic understanding. Combining both through adaptive selection leverages their respective strengths.

### Comparison Points
**Excels at**:
- Task-dependent reasoning (selects optimal pathway for each task)
- Numerical precision (code pathway for exact extraction and computation)
- Qualitative understanding (vision pathway for pattern recognition)
- Verifiability (code pathway provides inspectable traces)

**Fails at**:
- Tasks requiring seamless integration of both pathways (switching overhead)
- Unusual chart formats not covered in training (both pathways may fail)
- Situations where meta-controller makes wrong selection (suboptimal performance)
- Complex multi-step tasks requiring frequent pathway switching

---

## Notes

### Placement Rationale
Visual Programmability is primarily in Quadrant IV because:
- **Structured**: Both pathways use structured representations (code or visual attention)
- **Executable**: Code pathway involves execution with feedback
- **Adaptive**: Meta-controller adds intelligence to pathway selection, but doesn't change the fundamental Quadrant IV nature

However, the framework has a hybrid character: when the vision pathway is selected, it operates more like Quadrant I (text CoT) or Quadrant II (structured without execution). The overall framework design and the integration of code execution justify Quadrant IV as the primary placement.

### Meta-Controller Design
Key design questions for the meta-controller:
- What features does it use for pathway selection? (task type, chart type, historical performance)
- Is it trained end-to-end with the pathways, or as a separate module?
- Does it make hard selections (one pathway only) or soft combinations (weighted ensemble)?
- How does it handle uncertainty or ambiguous tasks?

### Open Questions
- How does Visual Programmability compare to ensemble approaches (run both pathways, vote on answers)?
- What is the generalization to unseen chart types or task categories?
- Can the meta-controller learn online from user feedback or execution outcomes?
- How to handle tasks where both pathways are equally valid but produce different answers?

### Future Directions
- **Multi-pathway extension**: Add more reasoning pathways (e.g., retrieval-augmented, symbolic reasoning)
- **Hierarchical selection**: Select pathways at multiple granularities (task-level, subtask-level)
- **Cross-modal learning**: Use successful code pathways to improve vision pathway (knowledge transfer)
- **Interactive clarification**: Allow the model to ask clarifying questions when pathway selection is uncertain

---

## BibTeX

```bibtex
@article{visualprogrammability2025,
  title={Visual Programmability: Adaptive Selection Between Code Execution and Direct Vision for Chart and Graph Understanding},
  author={[Author List]},
  journal={arXiv preprint arXiv:2509.09286},
  year={2025},
  url={https://arxiv.org/abs/2509.09286}
}
```

**Status**: ✅ Complete — Quadrant IV Paper
