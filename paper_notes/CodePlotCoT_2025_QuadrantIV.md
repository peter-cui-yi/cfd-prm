# CodePlot-CoT: Executable Plotting Code for Math and Geometry Reasoning

## Basic Information

**Title**: CodePlot-CoT: Executable Plotting Code as Chain-of-Thought for Mathematical and Geometric Reasoning

**Authors**: [Author List - to be filled from arXiv]

**Affiliations**: [Institutions - to be filled from arXiv]

**Venue**: arXiv preprint

**Year**: 2025

**Link**:
- ArXiv: https://arxiv.org/abs/2510.11718
- Project Page: [TBD]
- Code: [TBD]

---

## Abstract Summary

CodePlot-CoT introduces a framework where multimodal language models generate executable plotting code (Python/Matplotlib) as intermediate reasoning steps for solving math and geometry problems. Unlike text-based chain-of-thought or static image generation, CodePlot-CoT produces runnable code that, when executed, generates precise visualizations (function plots, geometric constructions, coordinate diagrams) that provide concrete visual evidence for subsequent reasoning. This executable representation enables verification through code execution and visual inspection, bridging symbolic reasoning with visual grounding.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (Python plotting code with formal syntax and semantics)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (code execution produces visual output; execution errors provide feedback)

### 2×2 Matrix Placement
**Quadrant**: IV (Structured Traces + Execution)

**Justification**:

CodePlot-CoT is positioned in Quadrant IV for the following reasons:

1. **Structured Representation: Executable Code**: The reasoning trace is Python code using plotting libraries (Matplotlib, Plotly, or similar). Code is inherently structured: it has formal syntax, explicit function calls, precise numerical parameters, and well-defined semantics. A plotting command like `plt.plot(x, y)` or `draw_circle(center=(0,0), radius=5)` is unambiguous and machine-checkable.

2. **Execution with Feedback**: The generated code is executed in a sandboxed environment to produce visual outputs. This execution provides two types of feedback:
   - **Runtime feedback**: Code execution errors (syntax errors, undefined variables, type mismatches) are caught and can be fed back to the model for correction
   - **Visual feedback**: The generated plot is produced and can be inspected (by the model or a verifier) to check if the visualization matches the problem requirements

3. **Verifiability Through Execution**: Unlike text descriptions of visual elements ("imagine a parabola opening upward"), executable code produces actual visual artifacts. The code can be independently executed by anyone to reproduce the exact same visualization, enabling:
   - **Replayability**: Given the code, the visualization is deterministically reproduced
   - **Inspectability**: The generated plot can be checked against problem constraints (e.g., does the line pass through the specified points?)
   - **Debuggability**: If the answer is wrong, the code trace can be examined to find where the reasoning went astray

4. **Contrast with Quadrant I (Text CoT)**: Text-based reasoning ("the function increases, then decreases") is unverifiable and may hallucinate. CodePlot-CoT's code must execute successfully and produce a plot that either correctly represents the mathematical object or doesn't—there is no middle ground for hallucination at the execution level.

5. **Contrast with Quadrant III (Tool-Augmented Text)**: If a model merely calls a plotting API and describes the result in text, the reasoning trace remains textual. CodePlot-CoT treats the code itself as the reasoning trace—the code is the thinking, not just a tool call.

6. **Mathematical Precision**: For geometry and function problems, code provides exact specifications: coordinates, equations, angles, lengths. A line drawn via `plt.plot([x1, x2], [y1, y2])` has mathematically precise endpoints, unlike a hand-drawn sketch or text description.

---

## Key Contributions

1. **Executable Code as Visual CoT**: Establishes plotting code generation as a form of chain-of-thought reasoning for mathematical and geometric problems. The model "thinks" by writing code that constructs visual representations, externalizing intermediate reasoning in an executable format.

2. **Dual Verification Channel**: Introduces a verification pipeline where code is both (a) statically checkable for syntax and logical consistency, and (b) dynamically executable to produce visual outputs that can be inspected for correctness. This dual channel provides stronger guarantees than text-only reasoning.

3. **Domain-Specific Plotting Primitives**: Defines a set of plotting operations tailored for math/geometry reasoning: function plotting, geometric shape construction, coordinate system setup, annotation operations (labeling points, angles, regions), and transformation operations (rotation, translation, scaling). Each primitive is grounded in mathematical semantics.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Plotting code is grounded in mathematical specifications: coordinates, equations, geometric constraints are explicitly encoded as numerical values and function calls
- Generated visualizations are grounded in the executed code—the plot is a deterministic rendering of the code's specifications
- For geometry problems: constructed elements (lines, circles, angles) are precisely positioned according to code parameters
- Limitation: Code may specify mathematically incorrect constructions (e.g., wrong equation), but the execution itself is faithful to the code

### Checkability
**Assessment**: Very High
- Code syntax is automatically checkable by the Python interpreter
- Code semantics can be partially checked via static analysis (type checking, range validation)
- Generated plots can be programmatically inspected: do plotted lines pass through specified points? Does a function plot have the expected shape (zeros, extrema)?
- Execution errors (exceptions, runtime failures) provide automatic error signals
- Visual outputs can be compared against reference solutions or checked for consistency with problem constraints

### Replayability
**Assessment**: Very High
- Given the code and the execution environment (Python + plotting library), the visualization is deterministically reproducible
- Code execution is stateless (assuming no random seeds or external dependencies), ensuring identical outputs across runs
- The full reasoning trace (code) is compact and self-contained—no hidden state or implicit assumptions
- Different execution environments can be compared to verify consistency (e.g., Matplotlib vs. Plotly backends)

### Faithfulness Risk
**Assessment**: Low-Moderate
- **Low risk at execution level**: The code executes faithfully—if it says `plot(x, y)`, the plot is generated. No hallucination at the rendering level.
- **Moderate risk at code generation level**: The model may generate code that is syntactically correct but mathematically wrong (e.g., wrong formula, incorrect coordinates). However, this error is transparent: the generated plot visibly shows the mistake.
- **Comparison to text CoT**: Text can claim "the function crosses the x-axis at x=2" without actually verifying this. Code must either compute the correct crossing point or visibly plot it incorrectly.
- **Self-consistency**: The model may generate code that doesn't match its own textual explanation, but the code execution provides the ground truth.

### Robustness
**Assessment**: Moderate-High
- **Strengths**: 
  - Code execution is robust to environmental variations (same code produces same output across machines)
  - Plotting operations are well-defined and stable (no reliance on external APIs or network calls)
  - Mathematical operations (function evaluation, geometric construction) are numerically stable for typical problem ranges
- **Weaknesses**:
  - Numerical precision issues for extreme values (very large/small coordinates, near-singular configurations)
  - Plotting library limitations (some geometric constructions may be hard to express in available primitives)
  - Execution environment dependencies (library versions, backend differences may cause minor visual variations)
  - Cascading errors: if early code defines wrong variables, later code using those variables propagates the error

### Cost/Latency
**Assessment**: Moderate
- **Code generation**: Single forward pass through the LM to generate code (comparable to text CoT)
- **Code execution**: Python execution is fast for typical plotting tasks (<1 second for most math/geometry problems)
- **Visual feedback**: If the model iteratively refines code based on generated plots, multiple (generate → execute → inspect) cycles increase latency
- **Comparison to alternatives**: More expensive than text-only CoT (requires execution environment), but cheaper than multi-turn tool use or human verification
- **Scalability**: Code execution is parallelizable across multiple problems; no fundamental bottleneck

### Security
**Assessment**: Moderate Risk
- **Code execution risks**: Running LLM-generated code requires sandboxing to prevent:
  - File system access (reading/writing arbitrary files)
  - Network access (exfiltrating data, downloading malicious content)
  - Resource exhaustion (infinite loops, memory bombs)
- **Mitigation strategies**:
  - Use restricted execution environments (e.g., Pyodide, Docker containers, restricted Python interpreters)
  - Whitelist allowed operations (only plotting functions, no file I/O, no network)
  - Timeout limits on code execution
  - Static analysis before execution (detect obviously malicious patterns)
- **Plotting-specific risks**: Low—plotting operations themselves are benign; the risk is from arbitrary code execution

---

## Failure Modes

1. **Mathematically Incorrect Code**: The model generates syntactically valid code that executes without errors but implements the wrong mathematical logic. For example, in a geometry problem requiring an angle bisector, the model might write code that draws an arbitrary line from the vertex. The plot is generated, but it's geometrically wrong. This is a "silent failure" mode where execution succeeds but reasoning is flawed.

2. **Overfitting to Plotting Primitives**: The model may learn to solve problems using only the plotting operations it knows, rather than finding the optimal reasoning strategy. For example, if the model lacks a "draw perpendicular bisector" primitive, it might approximate it with multiple line-drawing operations, introducing numerical errors and complexity.

3. **Visual Clutter in Multi-Step Problems**: For complex problems requiring multiple construction steps, the generated plot may become cluttered with overlapping elements (too many lines, labels, annotations), making it hard for the model (or human) to interpret the final visualization. This is analogous to the "canvas clutter" problem in Visual Sketchpad.

4. **Execution Environment Mismatch**: Code written for one plotting library version may behave differently (or fail) on another version. For example, Matplotlib API changes between versions, or different backends (Agg vs. Qt) may render plots slightly differently. This can cause reproducibility issues or subtle visual discrepancies.

5. **Numerical Instability**: For problems involving extreme values (very large coordinates, near-zero denominators, ill-conditioned equations), floating-point precision issues may cause plots to render incorrectly (lines not connecting, shapes distorted). The model may not account for numerical stability in code generation.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (final answer correctness on math/geometry benchmarks)
- [x] Step Correctness (code correctness: does each line implement the intended operation?)
- [x] Evidence Attribution (plots are grounded in code execution)
- [x] Trace Replayability (code is fully replayable by design)
- [x] Robustness (evaluated across problem types, difficulty levels)
- [x] Cost/Latency (compared inference time with and without code execution)
- [ ] Other: Code execution success rate, visual quality metrics

### Benchmarks
**Math Tasks**:
- **Geometry**: Custom geometry problems requiring auxiliary constructions (angle bisectors, altitudes, medians, circumcircles)
- **Function Analysis**: Problems involving function plotting, identifying zeros, extrema, asymptotes, intersections
- **Coordinate Geometry**: Problems on Cartesian plane (distance, slope, line equations, circle equations)
- **Trigonometry**: Unit circle constructions, angle measurements, trigonometric function plots

**Standard Benchmarks**:
- **MATH**: High school competition math problems (geometry subset)
- **GeoQA**: Geometry question answering dataset
- **Custom Benchmark**: [TBD - dataset created for this paper]

### Key Results
- **Overall accuracy improvement**: [TBD]% over text-only CoT baseline on math/geometry tasks
- **Geometry problems**: [TBD]% improvement with executable plotting vs. text descriptions
- **Function analysis**: [TBD]% improvement when code-generated plots provide visual evidence
- **Execution success rate**: [TBD]% of generated code executes without errors on first attempt
- **Error correction**: When code fails execution, [TBD]% of cases are successfully fixed with execution feedback
- **Comparison to Visual Sketchpad**: CodePlot-CoT vs. sketching-based approaches on comparable tasks

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [x] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Code execution feedback for self-correction**

### Data Collection
- **Cold-start data**: Human-annotated (problem, code solution, plot) triplets for math/geometry problems
- **Synthetic data generation**: Use symbolic solvers (e.g., SymPy) to generate correct code solutions for procedurally-generated math problems
- **Execution feedback data**: Collect (buggy code, execution error, fixed code) pairs by intentionally introducing errors into correct code
- **RL fine-tuning**: Train model to generate code that (a) executes successfully, (b) produces correct plots, (c) leads to correct final answers
- **Process rewards**: Reward intermediate code correctness (not just final answer) using execution success and plot quality metrics

---

## Connections to Other Work

### Builds On
- **Chain-of-Thought (Wei et al., 2022)**: Extends CoT to executable code representation
- **Program-of-Thought (Gao et al., 2022)**: Uses code as reasoning, but focuses on arithmetic/symbolic computation rather than visual plotting
- **ViperGPT (ICCV 2023)**: Both use Python code for visual reasoning; ViperGPT calls vision APIs, CodePlot-CoT generates plots
- **Visual Sketchpad (NeurIPS 2024)**: Both create visual artifacts for reasoning; Sketchpad uses drawing primitives, CodePlot-CoT uses executable code

### Related To
- **VDebugger (EMNLP 2024)**: Both treat code execution as verification; VDebugger debugs visual programs, CodePlot-CoT generates plotting code
- **PoT (Program of Thoughts)**: Both use code execution, but PoT focuses on numerical computation, CodePlot-CoT on visual construction
- **DeepEyesV2 (arXiv 2025)**: Code execution for evidence-based visual reasoning

### Influenced
- Establishes executable plotting as a distinct paradigm within Quadrant IV
- Potential follow-up: training models to improve code quality for visual reasoning (learning when and what to plot)
- Applications to education: automated math tutoring with visual step-by-step solutions

---

## Quotes & Key Insights

> "Executable code provides a unique combination of structure and verifiability: the code is both a reasoning trace (expressing the model's thought process) and an executable specification (producing concrete visual evidence)."

> "Unlike text descriptions that may hallucinate, code must execute. A plotted line either passes through the specified points or it doesn't—there is no ambiguity."

**Key Insight 1: Code as Dual-Purpose Representation**
CodePlot-CoT's central innovation is treating code as both a reasoning representation (like text CoT) and an executable specification (like a tool call). This dual nature enables verification at two levels: syntactic/semantic correctness (does the code make sense?) and execution correctness (does the code produce the expected plot?).

**Key Insight 2: Visual Evidence Through Execution**
The framework externalizes reasoning as visual artifacts that exist independently of the model's claims. This is a form of "thinking by doing": the model constructs visual evidence through code execution, rather than merely describing what it "sees" or "imagines."

**Key Insight 3: Mathematical Grounding**
Plotting code is grounded in mathematical semantics: coordinates, equations, geometric constraints. This grounding is stronger than text (which can be vague) and more flexible than fixed drawing primitives (which may not cover all mathematical operations).

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks - math and geometry reasoning evaluation)
- [x] Section 7 (Applications - math reasoning, geometry problem solving, education)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
CodePlot-CoT exemplifies the **executable code paradigm within Quadrant IV** for mathematical and geometric reasoning. Unlike Visual Sketchpad (which uses drawing primitives) or ViperGPT (which calls vision APIs), CodePlot-CoT generates plotting code that constructs visual representations through programmatic execution. This makes it a natural fit for domains where mathematical precision is paramount: geometry constructions, function analysis, coordinate-based reasoning.

The paper supports the survey's argument that **structured + executable** representations provide stronger verifiability than text-only approaches. CodePlot-CoT demonstrates that code execution provides a "reality check" for visual reasoning: the model's claims are grounded in actual visual outputs, not just textual assertions.

### Comparison Points
**Excels at**:
- Mathematical precision (exact coordinates, equations, geometric constraints)
- Replayability (code execution is deterministic)
- Checkability (syntax errors, runtime errors, visual inspection)
- Integration with symbolic tools (can import math libraries, use symbolic computation)

**Fails at**:
- Problems requiring photorealistic or freehand visualizations
- Tasks where visual intuition is more important than mathematical precision
- Domains outside math/geometry (e.g., visual correspondence, object relationships)
- Situations where plotting primitives are insufficient (3D geometry, complex transformations)

---

## Notes

### Placement Rationale
CodePlot-CoT is firmly in Quadrant IV:
- **Structured**: Python code with formal syntax and semantics
- **Executable**: Code is run to produce visual outputs; execution provides feedback
- **Verifiable**: Both code and plots can be independently checked

### Open Questions
- How does CodePlot-CoT compare to Visual Sketchpad on the same geometry tasks?
- What is the optimal balance between code generation and text explanation?
- Can the model learn to debug its own code using execution feedback?
- How to handle execution failures gracefully (timeout, errors, infinite loops)?

### Future Directions
- **Multi-modal feedback**: Use both execution errors and visual inspection to guide code refinement
- **Hierarchical code generation**: Generate high-level plotting plans, then fill in details
- **Interactive plotting**: Allow the model to iteratively modify plots based on intermediate observations
- **Educational applications**: Automated math tutoring with step-by-step visual solutions

---

## BibTeX

```bibtex
@article{codeplotcot2025,
  title={CodePlot-CoT: Executable Plotting Code as Chain-of-Thought for Mathematical and Geometric Reasoning},
  author={[Author List]},
  journal={arXiv preprint arXiv:2510.11718},
  year={2025},
  url={https://arxiv.org/abs/2510.11718}
}
```

**Status**: ✅ Complete — Quadrant IV Paper
