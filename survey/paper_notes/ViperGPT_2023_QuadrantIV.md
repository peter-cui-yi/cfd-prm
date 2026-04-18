# Paper Note: ViperGPT

## Basic Information

**Title**: ViperGPT: Visual Inference via Python Execution for Reasoning

**Authors**: Dídac Surís, Sachit Menon, Carl Vondrick

**Affiliations**: Columbia University

**Venue**: ICCV 2023

**Year**: 2023

**Link**:
- ArXiv: https://arxiv.org/abs/2303.08128
- Project/Code: Available through authors

---

## Abstract Summary

ViperGPT introduces a framework that uses code-generation LLMs (GPT-3.5 Codex) to compose vision-and-language models into Python subroutines to produce answers for visual queries. The model is given a Python API defining available vision modules (object detection, image captioning, OCR, depth estimation, visual question answering, etc.) and generates executable Python code for each query. The generated program is then executed to produce the final answer. This approach is training-free, achieves state-of-the-art results on complex visual reasoning tasks, and provides interpretable, replayable reasoning traces as Python programs.

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
**Quadrant**: IV (Structured Traces + Execution / Highest Verifiability)

**Justification**:

ViperGPT is the paradigmatic Quadrant IV approach for the following reasons:

1. **Structured Program Representation**: ViperGPT's reasoning trace is a formal Python program — not natural language, not a casual action list. Python programs have unambiguous syntax, formal semantics, and can be analyzed by automated tools. Each line of code is a precisely specified operation on visual data.

2. **Execution Feedback as Verification**: The Python program is actually executed against real vision models and image data. Each function call (`find(image, "dog")`, `simple_query(image, "Is the cat sitting?")`) produces concrete outputs that are logged. Execution either succeeds (returning meaningful results) or fails (throwing an exception) — both providing objective feedback about the reasoning process.

3. **Full Replayability**: The Python program completely specifies the reasoning process. Given the same image and the same API, anyone can re-run the program and reproduce all intermediate results. The program serves as a complete, self-contained specification of the reasoning trace.

4. **Contrast with Quadrant II (MM-REACT)**: MM-REACT produces natural language Thought/Action/Observation traces where each action is a free-form English instruction to a tool. ViperGPT produces Python code where each operation is a precise function call with typed arguments. Python can be formally analyzed, debugged, and re-executed; natural language cannot.

---

## Key Contributions

1. **Code-as-Reasoning: Python API for Vision Modules**: Defines a comprehensive Python API exposing vision capabilities as callable functions: `find(image, query)` (object detection), `exists(image, query)` (yes/no detection), `verify_property(image, object, property)` (attribute verification), `simple_query(image, question)` (VQA), `get_bounding_box(image, query)` (spatial localization), `crop(image, bbox)` (region extraction), `compute_depth(image)`, `count(image, query)`, etc. These functions are implemented by specialist vision models.

2. **Zero-Shot Code Generation for Novel Queries**: Using GPT-3.5 Codex with a few-shot prompt showing the API, ViperGPT generates Python programs for arbitrary visual queries without task-specific training. The code generation is remarkably general — it handles questions about counting, spatial relationships, attribute verification, multi-step reasoning, and comparison across images.

3. **Interpretable, Replayable Execution Traces**: Unlike end-to-end VLMs whose reasoning is opaque, ViperGPT's Python programs provide complete transparency: every intermediate result is a named variable; the execution trace shows exactly what visual evidence was gathered and how it was combined. Programs can be inspected, debugged, and modified.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Each function call produces verifiable visual evidence: `find(image, "dog")` returns actual bounding boxes of detected dogs
- Intermediate variables store concrete results: `num_cats = count(image, "cat")` holds an actual integer from the detector
- Every reasoning step is grounded in vision model outputs, not model assumptions
- Spatial reasoning is grounded in actual coordinates: `left_of(bbox1, bbox2)` computes based on real bounding box positions
- Programs can be inspected to see exactly which visual queries were made and what was returned

### Checkability
**Assessment**: Very High
- Python programs have well-defined semantics: each statement can be checked for syntactic and semantic correctness
- Intermediate results are explicitly named variables: `dogs = find(image, "dog")` — the existence and properties of this list are checkable
- Execution produces a full trace of function calls, inputs, and outputs
- Test cases can be written for individual API functions to verify tool correctness independently
- Answer is produced by executing deterministic Python logic over vision tool outputs

### Replayability
**Assessment**: Very High
- The Python program *is* the complete reasoning trace — it specifies exactly what to do and how to combine results
- Given the same image and API implementations, the program can be executed to reproduce all intermediate results
- Programs can be archived, shared, and inspected independently of the generative model that created them
- Different API implementations can be swapped to test sensitivity to tool quality
- This is the highest replayability in the 2×2 matrix: a formal executable specification

### Faithfulness Risk
**Assessment**: Low
- Programs explicitly state every operation performed: no hidden reasoning, no implicit assumptions
- The code cannot secretly deviate from what it says: `dogs = find(image, "dog")` will call the detector on the image
- Vision tools may have errors (wrong detections), but the program itself faithfully executes whatever it says
- Key risk: the code generation step may produce syntactically correct but semantically wrong programs (e.g., counting the wrong objects), but this is detectable by code review
- Much lower faithfulness risk than text CoT where reasoning can diverge from stated steps

### Robustness
**Assessment**: Moderate-High
- **Tool error sensitivity**: If a vision API function returns incorrect results (e.g., wrong bounding box), the program propagates those errors — but the error is traceable to a specific function call
- **Code generation failures**: Codex may occasionally generate syntactically invalid or logically flawed programs; exception handling catches syntax errors
- **API coverage**: Handles well within API capabilities; questions requiring unlisted functions (e.g., emotion recognition) will fail or require workarounds
- **Strength**: Modular API allows replacing individual tools with better implementations without changing the generated code

### Cost/Latency
**Assessment**: Moderate-High
- Code generation: One Codex API call per query (fast — generates complete program)
- Execution: Multiple vision API calls per program (one per function call in the generated code)
- Complex queries may require 5-10 function calls; each call involves running a specialist model
- No fine-tuning or training required — inference-only system
- Total cost: 1 LLM call (code generation) + N specialist model calls (execution)
- More expensive than single-pass VLM but cheaper than iterative multi-LLM agent systems

### Security
**Assessment**: Moderate Risk
- Python code execution is a security concern: if the API is not properly sandboxed, malicious code could be generated
- The provided API is designed to be safe (vision-only functions with no file system or network access)
- However, Codex could potentially generate Python that bypasses the API (e.g., importing os, accessing files)
- Need for proper sandboxing (restricted execution environment, limited imports) for deployment
- Unlike text-only systems, code execution introduces a new attack surface

---

## Failure Modes

1. **Code Generation Semantic Errors**: GPT-3.5 Codex may generate programs that are syntactically correct but logically wrong. For example, using `count(image, "cat")` when the question asks about dogs, or checking the wrong spatial relationship. These errors are harder to detect than syntax errors since the program executes successfully but produces wrong answers. Code review is necessary but requires understanding the visual query.

2. **API Coverage Gaps**: ViperGPT's capabilities are bounded by its API. For queries requiring visual understanding beyond the defined functions (e.g., emotion recognition, brand identification, aesthetic judgment, OCR of handwriting), the generated code either fails to compile (using undefined functions) or produces poor approximations using inadequate existing functions.

3. **Visual Tool Quality Bottleneck**: The final answer quality is bounded by the quality of the underlying vision models (GLIP for detection, BLIP-2 for VQA, etc.). If the detector misidentifies objects at a critical program step, the downstream logic operates on wrong inputs and produces incorrect answers despite correct program logic. Unlike text CoT where the model might compensate with world knowledge, program execution has no such fallback.

4. **Complex Spatial/Relational Reasoning Limitations**: Some visual reasoning requires multi-hop spatial relationships that are hard to express as simple API calls. For example, "Is the object behind the leftmost red item to the right of the tallest blue item?" requires multiple spatial queries and complex comparison logic. While Python can express this logic, generating correct complex programs reliably is challenging for current code generation models.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary: exact match on benchmark QA pairs)
- [x] Step Correctness (programs can be reviewed for logical correctness)
- [x] Evidence Attribution (function call outputs attributed to specific visual queries)
- [x] Trace Replayability (programs are the trace — fully replayable)
- [x] Robustness (multi-benchmark evaluation + ablation on API components)
- [ ] Cost/Latency (discussed qualitatively)
- [ ] Other

### Benchmarks
- **GQA**: Compositional visual question answering (spatial, relational)
- **NExT-QA**: Video QA requiring temporal and causal reasoning
- **NLVR2**: Natural Language Visual Reasoning for Real (binary statements about image pairs)
- **AGQA**: Action-grounded question answering for video understanding

### Key Results
- **GQA**: State-of-the-art among zero-shot methods; competitive with supervised methods
- **NExT-QA**: Strong performance on temporal and causal questions
- **NLVR2**: Significant improvement over prior zero-shot baselines
- **Key finding**: ViperGPT substantially outperforms end-to-end VLMs on questions requiring multi-step compositional reasoning, counting, and spatial relationship verification
- **Ablation**: Programs are significantly better than natural language CoT for questions requiring precise compositional logic

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Zero-shot code generation via Codex few-shot prompting** — no task-specific training

### Data Collection
- **No training data**: ViperGPT operates zero-shot using GPT-3.5 Codex with a few-shot API documentation prompt
- **API documentation**: Detailed docstrings and type annotations for each API function serve as the few-shot prompt; examples of Python programs for simple visual queries
- **Vision modules**: Pre-trained SOTA models used as API implementations:
  - GLIP (object detection/grounding)
  - BLIP-2 (image captioning, VQA)
  - MiDaS (depth estimation)
  - PyTesseract (OCR)
  - CLIP (cross-modal comparison)
  - Custom implementations for spatial relationship computation

---

## Connections to Other Work

### Builds On
- **Program Synthesis for VQA (Andreas et al., 2016; Johnson et al., 2017)**: Prior work on neural module networks and program synthesis for VQA; ViperGPT replaces learned programs with Codex-generated programs
- **GPT-3 Codex (Chen et al., 2021)**: Code generation model enabling zero-shot Python generation
- **Compositional VQA**: Addresses the fundamental compositionality challenge in visual reasoning that end-to-end models struggle with

### Related To
- **Visual Programming / VisProg (Gupta & Kembhavi, 2023)**: Contemporary work using GPT to generate visual programs in a domain-specific language; ViperGPT uses Python and a broader API
- **CodeVQA**: Related approaches using code for VQA
- **MM-REACT (2023)**: Both use LLMs to compose vision tools; MM-REACT uses natural language ReAct while ViperGPT uses formal Python
- **VisualWebArena (2024)**: Extends the executable trace paradigm to web agent tasks

### Influenced
- **VideoAgent (2024)**: Inspired by ViperGPT's tool composition paradigm, extended with structured memory
- **Visual Sketchpad (2024)**: Extends executable reasoning to drawing/sketching operations
- **Code-as-policy**: ViperGPT helped establish Python as the lingua franca for robot and visual agent programming

---

## Quotes & Key Insights

> "ViperGPT utilizes a provided API to access the available modules, and composes them by generating Python code that is later executed. This simple approach requires no further training, and achieves state-of-the-art results across various complex visual tasks."

> "End-to-end models do not explicitly differentiate between the two [visual processing and reasoning], limiting interpretability and generalization."

**Key Insight 1: Python as Verifiable Reasoning Language**
ViperGPT's central insight is that Python programs are a far more verifiable reasoning medium than natural language. Python has formal semantics, can be statically analyzed, throws exceptions on errors, and produces completely replayable execution traces. Using Python as the "chain of thought" simultaneously provides interpretability and executability — properties that natural language lacks.

**Key Insight 2: Zero-Shot Compositionality via API Design**
By designing a clean API with well-documented functions, ViperGPT enables GPT-3.5 Codex to compose novel visual reasoning programs zero-shot. The quality of the API design (function naming, type hints, docstrings) directly determines what reasoning is expressible — API design is a form of "inductive bias engineering" for the program synthesis paradigm.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks - multi-benchmark compositional VQA evaluation)
- [x] Section 7 (Applications - compositional visual reasoning)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
ViperGPT is a **foundational anchor for Quadrant IV**, demonstrating that Python programs provide the highest verifiability in the 2×2 matrix. It establishes the paradigm of using executable programs (rather than natural language) as reasoning traces, with each step grounded in vision API outputs. Its influence on subsequent work (Visual Sketchpad, VideoAgent) makes it essential historical context for understanding the evolution of structured, executable multimodal reasoning.

### Comparison Points
**Excels at**:
- Replayability (programs are complete, executable specifications)
- Grounding strength (every step calls a vision API with explicit outputs)
- Checkability (programs analyzable as formal code)
- Compositional reasoning (Python naturally expresses complex logic)

**Fails at**:
- API coverage gaps (bounded by predefined function set)
- Code generation errors for complex programs
- Security (code execution requires sandboxing)

---

## Notes

### Historical Position
ViperGPT (March 2023, ICCV 2023) is one of the earliest papers to use LLM code generation for visual reasoning, alongside VisProg. These two works established the Q4 program-synthesis paradigm that was later extended by Visual Sketchpad, VideoAgent, and many other systems. ViperGPT's influence on the field makes it essential context for any survey of structured visual reasoning.

---

## BibTeX

```bibtex
@inproceedings{suris2023vipergpt,
  title={ViperGPT: Visual Inference via Python Execution for Reasoning},
  author={Sur{\'\i}s, D{\'i}dac and Menon, Sachit and Vondrick, Carl},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)},
  year={2023},
  url={https://arxiv.org/abs/2303.08128}
}
```

**Status**: ✅ Complete — Quadrant IV Foundational Paper
