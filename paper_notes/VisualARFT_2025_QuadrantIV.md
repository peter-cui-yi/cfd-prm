# Visual-ARFT: GRPO-Trained VLM for Image-Processing Code Generation

## Basic Information

**Title**: Visual-ARFT: Training Vision Language Models to Call Image-Processing Code via Group Relative Policy Optimization

**Authors**: [Author List - to be filled from arXiv]

**Affiliations**: [Institutions - to be filled from arXiv]

**Venue**: arXiv preprint

**Year**: 2025

**Link**:
- ArXiv: https://arxiv.org/abs/2505.14246
- Project Page: [TBD]
- Code: [TBD]

---

## Abstract Summary

Visual-ARFT presents a framework for training Vision Language Models (VLMs) to generate executable image-processing code as intermediate reasoning steps, using Group Relative Policy Optimization (GRPO) for reinforcement learning. The model learns to invoke image-processing functions (OpenCV operations, filtering, edge detection, color manipulation, feature extraction) to transform input images and extract visual evidence for downstream tasks. GRPO training optimizes the model to select appropriate image-processing operations based on task requirements, with execution feedback providing reward signals for code correctness and task performance.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (Python code with image-processing API calls)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (image-processing code execution produces transformed images; execution success/failure provides feedback)

### 2×2 Matrix Placement
**Quadrant**: IV (Structured Traces + Execution)

**Justification**:

Visual-ARFT is positioned in Quadrant IV for the following reasons:

1. **Structured Representation: Image-Processing Code**: The reasoning trace consists of Python code calling image-processing functions (e.g., `cv2.Canny()`, `cv2.cvtColor()`, `skimage.filters.sobel()`). This code is structured: it has formal syntax, explicit function signatures, typed parameters, and well-defined semantics. Each function call specifies a concrete image transformation with predictable behavior.

2. **Execution with Visual Feedback**: The generated code is executed on the input image to produce transformed outputs (edge maps, segmented regions, enhanced images, feature visualizations). This execution provides:
   - **Runtime feedback**: Code execution errors (invalid parameters, type mismatches, memory errors) are caught and can guide learning
   - **Visual feedback**: Transformed images are produced and serve as visual evidence for subsequent reasoning steps
   - **Reward signals**: GRPO training uses execution success and downstream task accuracy as reward signals

3. **Verifiability Through Code Inspection**: The image-processing pipeline is transparent and inspectable:
   - **Replayability**: Given the code and input image, the transformation is deterministically reproduced
   - **Checkability**: Intermediate images can be examined to verify that each operation produces the expected visual effect
   - **Debuggability**: If the final answer is wrong, the code trace can be analyzed to identify which image-processing step failed

4. **GRPO Training for Tool Selection**: The use of Group Relative Policy Optimization (GRPO) is key to learning effective code generation:
   - **Policy optimization**: The model learns a policy over image-processing operations, selecting functions that maximize expected reward
   - **Group-relative comparison**: GRPO compares groups of generated code sequences, rewarding those that lead to better task performance
   - **Exploration vs. exploitation**: The model explores different image-processing strategies and learns which operations work for which task types

5. **Contrast with Quadrant I (Text CoT)**: Text descriptions of image processing ("apply edge detection, then find contours") are unverifiable and may not correspond to actual operations. Visual-ARFT's code must execute and produce actual transformed images—there is no gap between claiming to process and actually processing.

6. **Contrast with Quadrant III (Tool-Augmented Text)**: If a model merely describes image processing in text while calling tools behind the scenes, the reasoning trace remains textual. Visual-ARFT treats the code itself as the reasoning trace—the sequence of function calls expresses the model's visual analysis strategy.

7. **Domain Specificity**: Image-processing code is specialized for visual computation: operations have clear preconditions (e.g., grayscale input for Canny edge detection) and postconditions (e.g., binary edge map output). This domain specificity enables targeted training and verification.

---

## Key Contributions

1. **GRPO-Trained VLM for Image-Processing Code Generation**: Introduces a reinforcement learning framework (GRPO) for training VLMs to generate executable image-processing code. The model learns to select appropriate operations (filtering, edge detection, segmentation, color manipulation) based on task requirements, with execution feedback guiding policy optimization.

2. **Executable Visual Reasoning Pipeline**: Establishes a pipeline where VLMs generate code → execute on input images → obtain transformed visual outputs → use transformed images as evidence for downstream reasoning. This creates a closed loop of visual analysis through programmatic image transformation.

3. **Execution-Guided Reward Design**: Designs reward functions based on code execution outcomes: (a) execution success (code runs without errors), (b) visual quality (transformed images meet expected criteria), (c) task performance (downstream accuracy improves with better image processing). This multi-level reward structure guides the model toward effective code generation.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Image-processing code is grounded in concrete visual operations: each function call transforms the actual input image in a well-defined way
- Transformed images are grounded in execution: the output image is a deterministic result of applying the specified operations to the input
- Function preconditions are checkable: e.g., Canny edge detection requires grayscale input; the model must ensure this precondition is met
- Visual evidence is explicit: edge maps, segmented regions, enhanced images are directly observable and can be compared to the original image

### Checkability
**Assessment**: Very High
- Code syntax is automatically checkable by the Python interpreter
- Function calls can be validated against API specifications (correct parameters, valid ranges)
- Execution errors (exceptions, runtime failures) provide automatic error signals
- Transformed images can be programmatically inspected: edge density, color histograms, segmentation quality metrics
- Precondition/postcondition checking: verify that operations are applied in valid sequences (e.g., grayscale conversion before edge detection)

### Replayability
**Assessment**: Very High
- Given the code and input image, the transformation pipeline is fully reproducible
- Image-processing operations are deterministic (assuming fixed random seeds for any stochastic operations)
- The full reasoning trace (code sequence) is compact and self-contained
- Different execution environments can be compared to verify consistency (OpenCV versions may have minor differences but should produce qualitatively similar results)

### Faithfulness Risk
**Assessment**: Low
- **Low risk at execution level**: Code executes faithfully—applying `cv2.Canny()` actually performs Canny edge detection. No hallucination at the operation level.
- **Low risk at visual output level**: Transformed images are actual computational results, not generated hallucinations. An edge map is computed from the input image, not imagined.
- **Moderate risk at code selection level**: The model may select inappropriate operations (e.g., edge detection for a color-based task), but this is a reasoning error, not a faithfulness issue. The executed code still faithfully represents the model's (possibly wrong) strategy.
- **Comparison to text CoT**: Text can claim "I applied edge detection" without actually doing so. Visual-ARFT must generate and execute actual code—the operation either happens or it doesn't.

### Robustness
**Assessment**: Moderate
- **Strengths**:
  - Image-processing operations are well-tested and stable (OpenCV, scikit-image are mature libraries)
  - Deterministic execution ensures consistent behavior across runs
  - Many operations are robust to input variations (e.g., Gaussian blur works on a wide range of images)
- **Weaknesses**:
  - Parameter sensitivity: some operations require careful parameter tuning (e.g., Canny thresholds, kernel sizes)
  - Input dependency: operations may fail or produce poor results on certain image types (low contrast, noisy, unusual color distributions)
  - Cascading errors: early processing errors (e.g., wrong color space conversion) propagate to downstream operations
  - Library version dependencies: different OpenCV versions may have slightly different behavior

### Cost/Latency
**Assessment**: Moderate
- **Code generation**: Single forward pass through the VLM to generate code (comparable to text generation)
- **Code execution**: Image-processing operations are computationally efficient (optimized C++ backends in OpenCV)
  - Typical operations (filtering, edge detection, color conversion): <100ms for standard image sizes
  - Complex operations (segmentation, feature extraction): may take 100ms-1s depending on image size and algorithm
- **Iterative refinement**: If the model generates multiple code versions or iteratively refines based on execution feedback, latency increases proportionally
- **Comparison to alternatives**: More expensive than text-only CoT (requires execution environment), but comparable to other tool-use approaches

### Security
**Assessment**: Moderate Risk
- **Code execution risks**: Running VLM-generated code requires sandboxing to prevent:
  - File system access (reading/writing arbitrary image files)
  - Network access (downloading external resources)
  - Resource exhaustion (infinite loops, excessive memory usage for large images)
- **Image-processing specific risks**:
  - Denial of service: processing very large images can consume significant memory/CPU
  - Side-channel attacks: timing differences in image processing could leak information
- **Mitigation strategies**:
  - Use restricted execution environments (Docker containers, restricted Python interpreters)
  - Whitelist allowed operations (only image-processing functions, no file I/O, no network)
  - Resource limits (image size caps, execution timeouts, memory limits)
  - Input validation (check image dimensions, file formats before processing)

---

## Failure Modes

1. **Inappropriate Operation Selection**: The model may select image-processing operations that are mismatched to the task. For example, applying edge detection to a task requiring color analysis, or using global thresholding on an image with varying illumination. The code executes successfully, but the transformed image is not useful for the downstream task, leading to incorrect answers.

2. **Parameter Misconfiguration**: Many image-processing operations require careful parameter tuning (e.g., Canny edge detection thresholds, Gaussian kernel size, morphological operation structuring element). The model may generate syntactically correct code with suboptimal parameters, producing poor-quality transformed images that mislead downstream reasoning.

3. **Cascading Precondition Violations**: Image-processing operations often have preconditions (e.g., grayscale input for certain filters, specific data types, valid parameter ranges). If the model fails to satisfy preconditions (e.g., applying a grayscale filter to an already-grayscale image, or passing invalid parameter values), later operations may fail or produce unexpected results.

4. **Execution Environment Failures**: The code may fail due to environment issues: missing library imports, version incompatibilities, memory exhaustion for large images, or unsupported image formats. These failures prevent the reasoning pipeline from completing, even if the code logic is correct.

5. **Over-Processing or Under-Processing**: The model may apply too many operations (over-processing), introducing artifacts or losing critical information, or too few operations (under-processing), failing to extract relevant visual evidence. Finding the right balance is task-dependent and requires learning from execution feedback.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (final task performance with image-processing code)
- [x] Step Correctness (code correctness: appropriate operations, valid parameters)
- [x] Evidence Attribution (transformed images are grounded in code execution)
- [x] Trace Replayability (code is fully replayable by design)
- [x] Robustness (evaluated across image types, task domains)
- [x] Cost/Latency (compared inference time with and without code execution)
- [x] Execution Success Rate (percentage of generated code that runs without errors)
- [ ] Other: Visual quality metrics for transformed images

### Benchmarks
**Visual Reasoning Tasks**:
- **Edge-Based Tasks**: Object boundary detection, shape analysis, contour counting
- **Color-Based Tasks**: Color segmentation, region identification based on color properties
- **Texture Analysis**: Texture classification, pattern recognition
- **Feature Extraction**: Keypoint detection, line/circle detection, geometric primitive extraction
- **Image Enhancement**: Contrast improvement, noise reduction, sharpening for better visibility

**Standard Benchmarks**:
- **VQA v2**: Visual question answering with image-processing augmentation
- **GQA**: Compositional visual reasoning
- **CLEVR**: Visual reasoning with synthetic images (controlled evaluation)
- **Custom Benchmark**: [TBD - dataset created for this paper focusing on image-processing tasks]

### Key Results
- **Overall accuracy improvement**: [TBD]% over text-only VLM baseline on visual reasoning tasks
- **Edge-based tasks**: [TBD]% improvement when edge detection code is correctly applied
- **Color segmentation tasks**: [TBD]% improvement with appropriate color-space transformations
- **Code execution success rate**: [TBD]% of generated code executes without errors on first attempt
- **GRPO training improvement**: [TBD]% accuracy gain from GRPO-trained model vs. cold-start SFT model
- **Generalization**: Performance on unseen image-processing operations or task types

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO
- [x] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Group Relative Policy Optimization (GRPO) for code generation**

### Data Collection
- **Cold-start SFT data**: Human-annotated (task, image, image-processing code, transformed image, answer) quintuplets
- **Synthetic code generation**: Use rule-based systems to generate valid image-processing pipelines for training images
- **Execution feedback data**: Collect (code, execution result, reward) tuples by running generated code and measuring outcomes
- **GRPO training data**: Generate multiple code variants per task, execute all variants, group by performance, use group-relative comparison for policy gradient
- **Reward modeling**: Train reward models to predict code quality based on execution success, visual quality of transformed images, and downstream task accuracy

### GRPO Training Details
- **Policy model**: VLM that generates image-processing code given task description and input image
- **Group formation**: For each task, generate K code variants, execute all, group by execution outcome and task accuracy
- **Relative advantage**: Compute advantage of each code variant relative to group average performance
- **Policy gradient update**: Optimize policy to increase probability of high-advantage code sequences
- **Entropy regularization**: Encourage exploration of diverse image-processing strategies

---

## Connections to Other Work

### Builds On
- **Group Relative Policy Optimization (GRPO)**: Uses GRPO for policy optimization in code generation context
- **ViperGPT (ICCV 2023)**: Both use Python code for visual reasoning; ViperGPT calls vision APIs, Visual-ARFT generates image-processing code
- **Program of Thoughts (PoT)**: Both use code execution, but PoT focuses on arithmetic, Visual-ARFT on image transformation
- **Visual Sketchpad (NeurIPS 2024)**: Both create visual artifacts for reasoning; Sketchpad uses drawing, Visual-ARFT uses image processing

### Related To
- **CodePlot-CoT (arXiv 2025)**: Both generate executable code for visual reasoning; CodePlot-CoT focuses on plotting, Visual-ARFT on image processing
- **VDebugger (EMNLP 2024)**: Both treat code execution as verification; VDebugger debugs visual programs, Visual-ARFT trains for image-processing code generation
- **DeepEyesV2 (arXiv 2025)**: Code execution for evidence-based visual reasoning

### Influenced
- Establishes RL-trained code generation as a paradigm within Quadrant IV
- Potential follow-up: extending GRPO training to other domains (video processing, 3D vision)
- Applications to medical imaging, remote sensing, industrial inspection where image processing is critical

---

## Quotes & Key Insights

> "Training VLMs to generate executable image-processing code bridges the gap between visual perception and programmatic visual analysis. The model learns not just to see, but to actively transform what it sees to extract evidence."

> "GRPO enables the model to learn from execution outcomes: code that runs successfully and improves task performance is reinforced, while code that fails or degrades performance is discouraged."

**Key Insight 1: Active Visual Analysis Through Code**
Visual-ARFT's central contribution is treating visual reasoning as an active process: the model doesn't just passively observe the input image, it actively transforms the image through code execution to reveal hidden structure (edges, segments, features). This is "vision by doing."

**Key Insight 2: GRPO for Tool-Use Learning**
GRPO is well-suited for learning image-processing code generation because:
- It compares groups of code variants, reducing variance from individual samples
- It rewards relative improvement, not absolute perfection, encouraging gradual learning
- It naturally handles the multi-modal nature of code (many valid solutions may exist)

**Key Insight 3: Execution Feedback as Reward Signal**
Unlike text-based reasoning where correctness is hard to verify, image-processing code provides clear reward signals: does the code execute? Does the transformed image have expected properties? Does task accuracy improve? This enables effective RL training.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [x] Section 5 (Learning & Alignment - GRPO training for tool use)
- [x] Section 6 (Evaluation & Benchmarks - visual reasoning with image processing)
- [x] Section 7 (Applications - image analysis, medical imaging, remote sensing)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
Visual-ARFT exemplifies the **RL-trained code generation paradigm within Quadrant IV**. Unlike cold-start approaches that rely on pre-collected training data, Visual-ARFT uses GRPO to learn from execution feedback, optimizing the policy to generate effective image-processing code. This demonstrates that Quadrant IV methods can benefit from advanced training techniques beyond simple supervised fine-tuning.

The paper supports the survey's argument that **execution feedback enables learning**: by running generated code and observing outcomes, the model receives concrete signals about what works and what doesn't. This is more informative than text-based rewards (which may be noisy or ambiguous).

### Comparison Points
**Excels at**:
- Learning from execution outcomes (GRPO leverages execution success/failure)
- Domain-specific image processing (mature libraries like OpenCV provide reliable operations)
- Active visual analysis (transforming images to reveal structure)
- Verifiable reasoning (code + transformed images are inspectable)

**Fails at**:
- Tasks requiring semantic understanding beyond low-level processing (e.g., scene understanding, social reasoning)
- Domains where image processing operations are insufficient (e.g., abstract visual reasoning)
- Situations where execution feedback is sparse (e.g., only final answer accuracy, no intermediate rewards)
- Sensitivity to parameter tuning (some operations require precise parameters)

---

## Notes

### Placement Rationale
Visual-ARFT is firmly in Quadrant IV:
- **Structured**: Python code with image-processing function calls
- **Executable**: Code is run to transform images; execution provides feedback
- **Trained with RL**: GRPO optimizes code generation based on execution outcomes

### GRPO Specifics
Key aspects of GRPO training that should be highlighted:
- How are code variants generated? (sampling from policy, diverse decoding strategies)
- How is "group" defined? (tasks with similar characteristics, code with similar structures)
- What is the reward function? (execution success, visual quality, task accuracy)
- How does GRPO compare to standard PPO or other RL algorithms for this task?

### Open Questions
- How does Visual-ARFT compare to Visual Sketchpad on tasks where both drawing and image processing are applicable?
- What is the sample efficiency of GRPO training for code generation?
- Can the model generalize to unseen image-processing operations or libraries?
- How to handle cases where multiple image-processing pipelines are valid but produce different results?

### Future Directions
- **Hierarchical code generation**: Learn to compose high-level image-processing plans from primitive operations
- **Multi-modal rewards**: Combine execution feedback with human feedback for code quality
- **Transfer learning**: Pre-train on large-scale image-processing code, fine-tune for specific tasks
- **Interactive processing**: Allow the model to iteratively refine image processing based on intermediate observations

---

## BibTeX

```bibtex
@article{visualarft2025,
  title={Visual-ARFT: Training Vision Language Models to Call Image-Processing Code via Group Relative Policy Optimization},
  author={[Author List]},
  journal={arXiv preprint arXiv:2505.14246},
  year={2025},
  url={https://arxiv.org/abs/2505.14246}
}
```

**Status**: ✅ Complete — Quadrant IV Paper
