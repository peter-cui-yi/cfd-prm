# Paper Note: ChartAgent

## Basic Information

**Title**: ChartAgent: A Chart Understanding Framework with Tool Integrated Reasoning

**Authors**: Boran Wang, Xinming Wang, Yi Chen, Xiang Li, Jian Xu, Jing Yuan, Chenglin Liu

**Venue**: arXiv preprint (2025)

**Year**: 2025

**Link**: 
- ArXiv: https://arxiv.org/abs/2512.14040
- Project Page: (to be checked from paper)

---

## Abstract Summary

ChartAgent introduces a Tool-Integrated Reasoning (TIR) framework for automated chart understanding that decomposes complex chart analysis into observable, replayable steps. The system employs an extensible tool library with 14+ specialized tools (OCR, instance segmentation, key element detection, auxiliary line projection, etc.) that the agent dynamically orchestrates through a "Think-Observe-Execute-Reflect" loop. By consolidating intermediate outputs into a structured "Evidence Package," ChartAgent achieves state-of-the-art results on ChartBench and ChartX benchmarks, outperforming prior methods by up to 17.31% on unannotated, numerically intensive queries while providing traceable and reproducible reasoning chains.

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

ChartAgent clearly belongs to Quadrant II for the following reasons:

1. **Structured Representation (Evidence Package)**: 
   - The framework consolidates all intermediate tool outputs into a structured "Evidence Package" containing visualizations, detected elements, OCR results, and computed values
   - Unlike free-form CoT, the Evidence Package provides explicit, queryable structure: detected chart type, axis labels, data points, computed statistics
   - Tool outputs are standardized and reproducible: OCR returns text with bounding boxes, segmentation returns masks, calculation returns numerical results
   - The reasoning trace includes concrete tool invocations with arguments and results, not just textual reasoning

2. **Tool-Augmented with Execution Feedback**:
   - 14+ specialized tools: OCR, classification, auxiliary line detection, instance segmentation, color matching, numerical calculation, data structuring, relational reasoning
   - Tools provide executable feedback: OCR extracts text from specific regions, segmentation isolates chart elements, calculation performs arithmetic on extracted values
   - Tool outputs are grounded in visual evidence (bounding boxes, masks, extracted text) and can be verified by re-execution
   - The agent dynamically orchestrates tools based on query requirements and intermediate results

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, ChartAgent's reasoning trace includes:
   - Concrete tool calls with arguments (e.g., `OCR(axis_region)`, `segmentation(pie_chart)`)
   - Structured results (bounding boxes, masks, extracted values, computation results)
   - Evidence Package that persists across reasoning steps and supports verification

4. **Key Distinction from Quadrant IV**: While structured, the representation is not a fully executable program like ViperGPT (which generates Python code). The LLM produces natural language reasoning + tool calls in a "Think-Observe-Execute-Reflect" loop, not a complete program trace.

5. **Human-Inspired Cognitive Process**: The framework explicitly mimics human chart analysis (identify axes → read scales → locate data markers → perform measurement → integrate information), which is structured but not fully programmatic.

---

## Key Contributions

1. **Tool-Integrated Reasoning Framework for Charts**: Proposes ChartAgent, a chart understanding agent that transforms complex chart analysis from end-to-end black-box mapping into observable, controllable reasoning chains. The "Think-Observe-Execute-Reflect" loop dynamically orchestrates specialized tools based on query requirements.

2. **Modular Tool Library with 14+ Specialized Tools**: Constructs an extensible tool library organized into visual perception tools (OCR, classification, segmentation, auxiliary line detection, color matching) and reasoning tools (numerical calculation, data structuring, relational reasoning). Tools are dynamically invoked and their outputs aggregated into standardized Evidence Packages.

3. **State-of-the-Art Performance with Verifiable Reasoning**: Achieves SOTA results on ChartBench and ChartX benchmarks, outperforming prior methods by up to 17.31% on unannotated, numerically intensive queries. The Evidence Package provides traceable support for final conclusions, substantially improving robustness under sparse annotation settings.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Reasoning steps explicitly reference visual evidence through tool calls with concrete regions (bounding boxes, masks)
- OCR tool grounds text extraction to specific chart regions (axes, labels, legends)
- Segmentation tool grounds element detection to pixel-level masks (pie slices, bar segments, line points)
- Auxiliary line tool grounds numerical estimation to Cartesian projections (x-axis, y-axis alignments)
- Evidence Package consolidates all visual grounding, providing explicit attribution for final answers
- Compared to end-to-end MLLMs: Much stronger grounding due to mandatory tool-based visual parsing
- Limitation: Tool outputs can still have errors (e.g., OCR misreads text, segmentation misses small elements)

### Checkability
**Assessment**: Very High
- Tool calls and their arguments are explicitly logged (e.g., `OCR(axis_label_region)`, `calculate_percentage(slice_angle)`)
- Tool outputs can be automatically validated: OCR text can be checked against ground truth, segmentation masks can be evaluated with IoU, calculations can be verified arithmetically
- Evidence Package provides complete audit trail: all intermediate visualizations and computations are recorded
- Tool selection logic is partially checkable: can verify if invoked tools are appropriate for query type (e.g., pie chart tools for pie chart queries)
- Limitation: Cannot fully automate verification of tool *selection strategy* (why choose tool A before tool B)

### Replayability
**Assessment**: Very High
- Complete inference trace is recorded: [(tool_call, arguments, results)] tuples + Evidence Package
- Given same chart image and tool implementations, the trace can be re-executed deterministically
- Tool implementations are modular and can be independently verified (OCR model, segmentation model, calculation functions)
- Paper provides full algorithm description with Think-Observe-Execute-Reflect loop
- Code availability: (to be checked from paper - likely will be released)
- Evidence Package standardization ensures consistent output format for replay

### Faithfulness Risk
**Assessment**: Low-Moderate
- **Strength**: Tool execution forces grounding - model cannot answer without actually invoking visual tools
- **Strength**: Evidence Package requires concrete visual evidence (bounding boxes, masks, extracted values) before final conclusion
- **Strength**: Multi-tool cross-verification (e.g., OCR + segmentation + calculation) reduces single-tool hallucination risk
- **Risk**: LLM can still misinterpret tool outputs (e.g., aggregate values incorrectly, draw wrong conclusions from correct data)
- **Risk**: Tool failures (e.g., OCR misses text, segmentation fails on complex charts) can propagate to incorrect reasoning
- **Mitigation**: Reflection step allows model to detect inconsistencies and re-invoke tools if needed
- Compared to end-to-end MLLMs: Much lower faithfulness risk due to explicit visual grounding and Evidence Package

### Robustness
**Assessment**: High
- **Tool Failure Handling**: Modular design allows fallback strategies (e.g., if OCR fails, use visual estimation via auxiliary lines)
- **Chart Type Generalization**: Tool library covers diverse chart types (bar, line, pie, radar, scatter, multi-axis) with specialized tools for each
- **Annotation Robustness**: Substantially improves performance on unannotated charts (GPT-4o drops 53.73% on unannotated vs annotated; ChartAgent mitigates this)
- **Strength**: Extensible tool library allows adding new tools for unseen chart types or reasoning tasks
- **Strength**: Multi-expert collaboration with weighted voting provides ensemble robustness
- **Limitation**: Performance may degrade with extremely low-quality images (blurry, low resolution, heavy compression)
- **Limitation**: Tool orchestration complexity increases with chart complexity (multi-panel, multi-series charts)

### Cost/Latency
**Assessment**: Moderate-High
- **Tool Budget**: Multiple tool calls per query (exact number varies by chart complexity); paper doesn't specify maximum but implies iterative loop
- **Tool Execution Cost**: 
  - OCR: Fast (modern OCR models ~100ms per region)
  - Segmentation: Moderate (instance segmentation ~200-500ms per image)
  - Calculation: Fast (arithmetic operations ~1ms)
  - LLM orchestration: Moderate (LLM inference for tool selection ~500ms-2s depending on model size)
- **Cumulative Latency**: Complex charts may require 5-10 tool calls, leading to 2-5 seconds total latency
- **Comparison**: More expensive than single-pass MLLM inference, but provides verifiable reasoning
- **Trade-off**: Higher cost is justified by 17.31% performance gain on unannotated charts and verifiability

### Security
**Assessment**: Low Risk
- **No Web Access**: Tools operate on local chart images only, no external API calls
- **No User Input Processing**: Tools process chart images, not user-generated text (reduces injection risk)
- **Tool Sandboxing**: Tool implementations are deterministic functions (OCR, segmentation, calculation) with no side effects
- **Data Privacy**: Chart images may contain sensitive data; local processing avoids API privacy risks
- **Mitigation**: Evidence Package logging provides audit trail for debugging and security analysis
- **No Explicit Security Concerns**: Paper doesn't discuss security considerations (low-risk application domain)

---

## Failure Modes

1. **Tool Output Errors Propagate to Final Answer**: If OCR misreads axis labels or segmentation fails to isolate chart elements correctly, subsequent reasoning steps will compound the error. For example, OCR reading "100" as "1000" will cause all downstream calculations to be off by 10x. Reflection step may catch some errors, but not all.

2. **Incorrect Tool Selection for Chart Type**: The agent may invoke inappropriate tools for a given chart type (e.g., use bar chart tools for radar charts). Paper mentions "tool expert manager" and "polymath weighted voting" to mitigate this, but tool selection errors remain a risk, especially for unusual or hybrid chart types.

3. **Complex Chart Overload**: For multi-panel, multi-series charts with overlapping elements, the tool orchestration may become overwhelmed. Too many tool calls can lead to context overflow, attention dilution, or inconsistent Evidence Package assembly. Paper doesn't extensively discuss scalability to very complex charts.

4. **Visual Ambiguity Resolution Failure**: Some charts have inherent visual ambiguity (e.g., overlapping data points, occluded labels, unclear axis scales). Tools may return conflicting or uncertain results, and the agent may lack robust conflict resolution strategies. Paper mentions "multi-expert collaboration" but doesn't detail conflict handling.

5. **Numerical Estimation Errors**: For charts without explicit numerical labels, tools like auxiliary line projection must estimate values visually. These estimates can have significant errors (e.g., ±5-10% for manual projection), which propagate to final answers. Paper shows improvement on unannotated charts but doesn't eliminate the challenge entirely.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric on ChartBench, ChartX, ChartQA)
- [x] Step Correctness (implicitly via tool output validation and Evidence Package verification)
- [x] Evidence Attribution (Evidence Package provides explicit visual grounding)
- [x] Trace Replayability (demonstrated via standardized tool call logs and Evidence Package)
- [x] Robustness (tested on annotated vs unannotated charts, diverse chart types)
- [x] Cost/Latency (discussed qualitatively via tool orchestration complexity)
- [x] Other: NumberQA (NQA), Value Compare, Chart-to-Table conversion metrics

### Benchmarks
- **ChartBench**: Comprehensive chart understanding benchmark with annotated and unannotated charts
- **ChartX**: Cross-chart-type benchmark testing generalization to diverse chart formats
- **ChartQA**: Chart question answering benchmark with numerical and comparative questions
- **NumberQA (NQA)**: Subset focusing on numerical value extraction and computation
- **Value Compare**: Subset focusing on comparative reasoning (greater than, less than, equal)
- **Chart-to-Table**: Task of extracting structured data tables from chart images

### Key Results
- **ChartBench Unannotated**: ChartAgent outperforms prior methods by up to 17.31% on numerically intensive queries
- **GPT-4o Baseline**: GPT-4o experiences 53.73% accuracy drop on unannotated vs annotated charts; ChartAgent substantially mitigates this
- **Qwen3-VL Baseline**: Even Qwen3-VL (least affected baseline) observes 17.56 p.p. decline; ChartAgent improves robustness
- **NumberQA**: State-of-the-art performance on numerical extraction and computation tasks
- **Value Compare**: Strong performance on comparative reasoning across chart types
- **Chart-to-Table**: High accuracy in extracting structured data from diverse chart formats
- **Ablation**: Full tool set significantly outperforms subsets, validating comprehensive tool design

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Tool orchestration with prompt engineering** (no training required for agent; tools are pretrained/fine-tuned separately)

### Data Collection
- **Tool Training**: Individual tools (OCR, segmentation, classification) are pretrained or fine-tuned on domain-specific datasets
  - OCR: Trained on chart text datasets (synthetic + real chart labels)
  - Segmentation: Trained on chart element segmentation datasets (pie slices, bar segments, line points)
  - Classification: Trained on chart type classification datasets
- **Agent Orchestration**: No explicit training; uses prompt engineering to guide Think-Observe-Execute-Reflect loop
- **Evidence Package**: Standardized format designed to capture all intermediate outputs for verification
- **No RL or Process Labels**: Agent operates zero-shot using pretrained LLM's tool-use capability
- **Multi-Expert Collaboration**: Weighted voting mechanism combines predictions from multiple tools without explicit training

---

## Connections to Other Work

### Builds On
- **Tool-Integrated Reasoning (TIR)**: Prior work on LLMs interacting with external tools in multi-step loops
- **Chart Understanding Models**: MatCha, UniChart, ChartAssistant, ChartMoE for domain-specific chart processing
- **MLLMs for Vision**: GPT-4o, Qwen3-VL, Gemini for general visual reasoning (baselines in paper)
- **Agent Frameworks**: ReAct (Yao et al., 2022) for think-act-observe loops, LangChain for tool orchestration

### Related To
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), VisRAG (vision-based RAG), ToolRL (RL for tool learning)
- **Domain-Specific Agents**: Scientific chart analysis, business analytics, data visualization interpretation
- **Verifiable Reasoning**: Work on faithful explanation, evidence attribution, reasoning trace verification

### Influenced
- **Need to check citations** (paper from Dec 2025): Potential follow-ups in chart understanding agents, TIR for visualization
- **Code Repository**: (to be checked from paper - likely will be released to facilitate future research)

---

## Quotes & Key Insights

> "Inspired by human cognition, ChartAgent decomposes complex chart analysis into a sequence of observable, replayable steps."

> "Leveraging TIR's transparency and verifiability, ChartAgent moves beyond the black-box paradigm by standardizing and consolidating intermediate outputs into a structured Evidence Package, providing traceable and reproducible support for final conclusions."

> "Experiments show that ChartAgent substantially improves robustness under sparse-annotation settings, offering a practical path toward trustworthy and extensible systems for chart understanding."

**Key Insight**: ChartAgent demonstrates that **Tool-Integrated Reasoning with structured Evidence Packages** can overcome the critical limitation of end-to-end MLLMs: over-reliance on explicit textual annotations. By decomposing chart analysis into verifiable tool steps, ChartAgent achieves robust performance even when key numerals are absent.

**Critical Observation**: The comparison between GPT-4o's 53.73% drop on unannotated charts and ChartAgent's robustness reveals a fundamental weakness in end-to-end MLLMs: they treat chart understanding as black-box pixel-to-answer mapping without structured visual parsing. ChartAgent's tool-based approach forces explicit visual evidence collection.

**Survey-Relevant Point**: ChartAgent exemplifies Quadrant II's core strength: **structured tool traces + execution feedback enable verifiable, robust reasoning**. The Evidence Package provides an audit trail that end-to-end models cannot match, making ChartAgent suitable for precision-sensitive domains (scientific research, finance).

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks) - as example of chart understanding evaluation
- [x] Section 7 (Applications) - data visualization, scientific chart analysis
- [x] Section 8 (Challenges & Future) - verifiable reasoning for domain-specific tasks

### Narrative Role

ChartAgent serves as a **representative example** of Quadrant II, demonstrating:

1. **Structured Evidence Package as Verifiable Representation**: Unlike free-form CoT (Quadrant I), the Evidence Package provides explicit, queryable structure with concrete visual grounding (bounding boxes, masks, extracted values)

2. **Tool-Augmented Reasoning with Execution Feedback**: Each tool call produces concrete, verifiable outputs (OCR text, segmentation masks, calculation results) that can be replayed and checked

3. **Trade-offs in Quadrant II Design**:
   - **Pros**: Higher grounding strength (visual evidence), robustness to missing annotations, verifiability (Evidence Package)
   - **Cons**: Higher cost (multiple tool calls), tool failure sensitivity, orchestration complexity

4. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (Evidence Package) but more complex (tool orchestration)
   - vs Quadrant III (Text + Execution): More structured (visual tools) but less general (domain-specific to charts)
   - vs Quadrant IV (Structured + Execution): More flexible (natural language + tools) but less rigorous (no programmatic guarantees)

5. **Domain-Specific Application**: ChartAgent shows how Quadrant II methods can be tailored to specific domains (chart understanding) with specialized tool libraries

### Comparison Points

**Excels at**:
- Grounding strength (explicit visual evidence via tools)
- Replayability (standardized tool call logs + Evidence Package)
- Robustness (substantial improvement on unannotated charts)
- Verifiability (complete audit trail for final conclusions)

**Fails at**:
- Full automation of verification (tool selection logic still partially opaque)
- Cost efficiency (multiple tool calls per query)
- Scalability (complex multi-panel charts may overwhelm orchestration)
- Generalization (tool library is chart-specific, not general-purpose)

---

## Notes

### Follow-up Items
- [ ] Verify exact venue/publication status (currently arXiv preprint from Dec 2025)
- [ ] Check if code repository is public (paper mentions "code will be released")
- [ ] Review citations for follow-up work on chart understanding agents
- [ ] Compare with other Quadrant II candidates (VideoAgent, VisRAG, ToolRL) to confirm anchor selection

### Questions
- What is the exact tool orchestration algorithm (Think-Observe-Execute-Reflect loop details)?
- How does the "tool expert manager" and "polymath weighted voting" work?
- What is the average number of tool calls per query across different chart types?
- How does ChartAgent handle tool execution errors (e.g., OCR failure, segmentation timeout)?
- What is the Evidence Package schema (exact format for storing intermediate results)?

### Clarification on Quadrant Placement
The placement in Quadrant II (not IV) is because:
- Representation is structured (Evidence Package with tool outputs) but **reasoning trace is natural language** (Think-Observe-Execute-Reflect loop)
- Tools are invoked via natural language commands with structured parameters, not full program synthesis
- No complete program generation like ViperGPT (Quadrant IV)
- Best characterized as "Structured Traces (Evidence Package) + Tool-Augmented Reasoning (natural language)"

---

## BibTeX

```bibtex
@article{wang2025chartagent,
  title={ChartAgent: A Chart Understanding Framework with Tool Integrated Reasoning},
  author={Wang, Boran and Wang, Xinming and Chen, Yi and Li, Xiang and Xu, Jian and Yuan, Jing and Liu, Chenglin},
  journal={arXiv preprint arXiv:2512.14040},
  year={2025},
  url={https://arxiv.org/abs/2512.14040}
}
```

**Status**: ✅ Complete - Quadrant II Paper (Chart Understanding Agent)
