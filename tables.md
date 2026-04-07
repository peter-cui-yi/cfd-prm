# Tables for Survey

## Table 1: Method Comparison by Quadrant

| Aspect | Quadrant I: Text-only | Quadrant II: Text + Tools | Quadrant III: Structured | Quadrant IV: Structured + Tools |
|--------|----------------------|--------------------------|-------------------------|--------------------------------|
| **Representation** | Free-form text | Text + Action/Observation | Tables, graphs, programs, latent states | Executable programs, sketches, state logs |
| **Verification** | Self-consistency, reflection | Tool outputs, trajectory audit | Schema constraints, alignment checks | Code execution, tool validation, specialist verifiers |
| **Grounding Strength** | Weak (implicit) | Moderate (tool-based) | Moderate (structural) | Strong (executable + external) |
| **Checkability** | Manual (human review) | Partial (tool outputs checkable) | Automatic (schema validation) | Automatic (execution + tools) |
| **Replayability** | No (stochastic) | Partial (tool-dependent) | Yes (deterministic structure) | Yes (full execution replay) |
| **Training** | SFT with CoT, consistency | Tool-use SFT, RL for orchestration | Constraint-based training | Execution feedback, RL for tool-use |
| **Evaluation** | Answer accuracy, step correctness | Tool accuracy, trajectory quality | Structural correctness | Execution success, end-to-end accuracy |
| **Latency** | Low (~100ms) | Moderate (~500-2000ms) | Low (~100-300ms) | High (~2000-5000ms) |
| **Cost** | Low (model inference only) | Moderate (tool API costs) | Low (compute only) | High (compute + tool costs) |
| **Security Risk** | Low | Moderate (web injection) | Low | High (code execution, web) |
| **Best For** | Low-stakes QA, prototyping | Multi-hop reasoning, fact-checking | Spatial/structural tasks | Safety-critical, high-stakes |
| **Representative Works** | CURE (NAACL 2024) | VideoAgent (ECCV 2024) | MCOUT-style (arXiv 2025) | Visual Sketchpad (NeurIPS 2024), DeepEyesV2 (arXiv 2025) |

---

## Table 2: Benchmark & Metric Mapping

| Benchmark | Task Type | Answer Metrics | Process Metrics | Quadrant Support | Limitations |
|-----------|-----------|----------------|-----------------|------------------|-------------|
| **VQA-CoT** | Visual QA + CoT | Accuracy | Step correctness (human) | Q1 | No tool evaluation |
| **ScienceQA** | Science reasoning | Accuracy | Step correctness, evidence | Q1, Q2 | Limited to science domain |
| **ChartQA** | Chart understanding | Accuracy | Evidence attribution | Q1, Q2, Q4 | No structured trace eval |
| **DocVQA** | Document VQA | ANLS | Grounding (text regions) | Q2, Q4 | Text-only grounding |
| **RefCOCO+** | Referring expression | Precision@K | Grounding IoU | Q3, Q4 | Single-step only |
| **Visual Genome** | Scene graph | Recall@K | Structural correctness | Q3 | No reasoning evaluation |
| **CLEVR** | Compositional QA | Accuracy | Program execution | Q3, Q4 | Synthetic domain |
| **Video-MME** | Video QA | Accuracy | Temporal grounding | Q2, Q4 | No step-level metrics |
| **ToolBench-VL** | Tool use | Success rate | Tool correctness | Q2, Q4 | Limited tool coverage |
| **ExecVQA** | Executable VQA | Accuracy | Code success, replay | Q4 | New benchmark (limited adoption) |

### Metric Coverage Summary

| Metric Category | Benchmarks Supporting | Gap |
|----------------|----------------------|-----|
| Step Correctness | VQA-CoT, ScienceQA, CLEVR | Limited to annotated datasets |
| Evidence Attribution | ChartQA, DocVQA, RefCOCO+ | Mostly bounding box grounding |
| Trace Replayability | CLEVR, ExecVQA | Very limited support |
| Robustness | (None explicitly) | **Major gap** |
| Cost/Latency | (None explicitly) | **Major gap** |

---

## Table 3: Tool-use Reliability & Security Considerations

| Tool Category | Reliability Concerns | Security Risks | Mitigation Strategies |
|--------------|---------------------|----------------|----------------------|
| **Object Detectors** | False positives/negatives, confidence calibration | Model poisoning (adversarial training data) | Multi-detector consensus, confidence thresholds |
| **OCR** | Accuracy on difficult text (handwriting, low-res) | Text injection (adversarial text in images) | Confidence scoring, human verification for critical text |
| **Segmentation** | Boundary accuracy, class confusion | Mask manipulation attacks | IoU validation, post-processing checks |
| **Depth Estimation** | Scale ambiguity, reflection errors | Depth spoofing | Multi-view consistency, physical constraints |
| **Search Engines** | Result quality, ranking bias | **Prompt injection**, SEO poisoning | Source trust scoring, result filtering |
| **Knowledge Bases** | Outdated information, coverage gaps | Knowledge base poisoning | Version tracking, cross-referencing |
| **Code Interpreters** | Runtime errors, incorrect outputs | **Code injection**, resource exhaustion | Sandboxing, resource limits, output validation |
| **Calculators** | Precision limits, edge cases | Minimal | Input validation, range checking |
| **Specialist Tools** (medical, legal) | Domain-specific errors, liability | Domain-specific attacks | Expert validation, regulatory compliance |
| **Memory/Database** | Retrieval accuracy, staleness | Data leakage, injection | Access control, query sanitization |

### Security Risk Levels by Quadrant

| Quadrant | Tool Exposure | Attack Surface | Risk Level |
|----------|--------------|----------------|------------|
| Q1: Text-only | None | Prompt injection only | 🟢 Low |
| Q2: Text + Tools | Web APIs, external services | Injection, poisoning, manipulation | 🟡 Moderate |
| Q3: Structured | None/Minimal | Schema exploitation | 🟢 Low |
| Q4: Structured + Tools | Code execution, web, APIs | All Q2 risks + code injection | 🔴 High |

### Recommended Security Practices

1. **Input Sanitization**: Clean all tool inputs (images, queries, parameters)
2. **Output Validation**: Verify tool outputs before using in reasoning
3. **Sandboxing**: Isolate code execution from sensitive resources
4. **Rate Limiting**: Prevent abuse and resource exhaustion
5. **Audit Logging**: Log all tool calls for forensic analysis
6. **Human Oversight**: Require human approval for high-stakes decisions
7. **Tool Versioning**: Track tool versions for reproducibility and security updates

---

## Table 4: Training Method Comparison

| Method | Data Requirements | Verifiability Signal | Scalability | Best Quadrant |
|--------|------------------|---------------------|-------------|---------------|
| **SFT with CoT** | Answer + rationale pairs | Weak (answer-level only) | High (standard pipeline) | Q1 |
| **Process Supervision** | Step-level annotations | Strong (per-step feedback) | Low (expensive annotation) | Q1, Q2, Q3, Q4 |
| **PRM** | Step preferences/scores | Strong (learned reward) | Medium (train once, use many) | Q1, Q2, Q3, Q4 |
| **RL (PPO)** | Environment interaction | Strong (execution rewards) | Low (sample inefficient) | Q2, Q4 |
| **DPO** | Pairwise preferences | Medium (relative quality) | Medium (needs preferences) | Q1, Q2, Q3, Q4 |
| **Verifier-guided** | Generated + verified traces | Strong (verification signal) | High (auto-generation) | Q2, Q4 |

---

## Table 5: Applications & Quadrant Recommendations

| Domain | Application | Verifiability Requirements | Recommended Quadrant | Rationale |
|--------|-------------|---------------------------|---------------------|-----------|
| **Medical** | Radiology diagnosis | Step audit, evidence grounding, high robustness | Q4 | Safety-critical, regulatory requirements |
| **Medical** | Triage assistant | Moderate verifiability, fast response | Q2 | Balance speed and verification |
| **Legal** | Contract analysis | Citation accuracy, logical consistency | Q3 | Structured reasoning, auditability |
| **Legal** | Case research | Fact verification, source tracking | Q2 + Q4 | Need external verification |
| **Finance** | Earnings analysis | Traceable logic, reproducibility | Q3-Q4 | Audit requirements |
| **Finance** | Trading signals | Low latency, moderate verification | Q1-Q2 | Speed priority |
| **Education** | Grading assistant | Explainable rubrics, fairness | Q3 | Structured evaluation |
| **Education** | Tutoring | Step-level feedback, patience | Q2 | Interactive, tool-supported |
| **Manufacturing** | Quality inspection | Defect grounding, compliance docs | Q4 | High stakes, traceability |
| **Consumer** | Visual search | Low latency, basic accuracy | Q1 | Cost/latency priority |
| **Research** | Literature review | Citation accuracy, synthesis quality | Q3-Q4 | Verifiable claims essential |
| **Government** | Policy analysis | Auditability, multi-source integration | Q4 | High stakes, public accountability |

---

## Table 6: Open Challenges & Research Directions

| Challenge | Current State | Desired State | Research Directions |
|-----------|--------------|---------------|---------------------|
| **Robust Tool-use** | Brittle to failures | Graceful degradation, recovery | Error detection, redundant verification |
| **Adversarial Robustness** | Vulnerable to injection | Resistant to attacks | Adversarial training, input sanitization |
| **Cost Efficiency** | High cost for Q4 | Budget-aware reasoning | Early exiting, caching, tiered verification |
| **Standardized Formats** | Custom per paper | Community standard | Schema development, tool libraries |
| **Reward Functions** | Proxy metrics, hacking | True verifiability signals | Multi-objective, adversarial rewards |
| **Benchmarks** | Answer-focused, synthetic | Real-world, process-level | Application-specific suites, human evaluation |
| **Long-horizon Reasoning** | Limited to few steps | Hours/days of reasoning | Memory architectures, human collaboration |
| **Multi-modal Integration** | Vision + text dominant | Audio, video, sensors | Unified representations, cross-modal verification |
| **Human-AI Collaboration** | Full automation or manual | Shared reasoning | Interactive verification, responsibility sharing |
| **Deployment Monitoring** | Answer tracking only | Full trace auditing | Real-time verifiability dashboards, alerting |

---

## Usage Notes

### How to Use These Tables

1. **Table 1**: Include in Section 4.5 (Quadrant Comparison Summary)
2. **Table 2**: Include in Section 6.2 (Benchmarks for Verifiable Reasoning)
3. **Table 3**: Include in Section 8.2 (Adversarial Challenges)
4. **Table 4**: Include in Section 5.1 (Training Progression)
5. **Table 5**: Include in Section 7 (Applications)
6. **Table 6**: Include in Section 8 (Challenges & Future Directions)

### Formatting for Publication

- Convert to LaTeX `table` environment for paper submission
- Ensure tables fit within column width (typically 3.5" for single column, 7" for double column)
- Use consistent font size (typically 8-9pt for tables)
- Add proper captions and source attributions
- Consider splitting large tables across multiple pages if needed

### Accessibility

- Ensure tables are readable when printed in grayscale
- Provide table descriptions for screen readers
- Include key insights in captions (not just data)
