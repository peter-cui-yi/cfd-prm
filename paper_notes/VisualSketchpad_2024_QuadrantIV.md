# Paper Note: Visual Sketchpad

## Basic Information

**Title**: Visual Sketchpad: Sketching as a Visual Chain of Thought for Multimodal Language Models

**Authors**: Yushi Hu, Weijia Shi, Xingyu Fu, Dan Roth, Mari Ostendorf, Luke Zettlemoyer, Noah A. Smith, Ranjay Krishna

**Affiliations**: University of Washington; University of Pennsylvania

**Venue**: NeurIPS 2024

**Year**: 2024

**Link**:
- ArXiv: https://arxiv.org/abs/2406.09403
- Project Page: https://visualsketchpad.github.io/

---

## Abstract Summary

Visual Sketchpad introduces a framework that gives multimodal language models a visual sketchpad and drawing tools, enabling them to externalize intermediate reasoning as sketches — auxiliary lines in geometry, bounding box marks for spatial reasoning, highlights for correspondence. Unlike text-based CoT or text-to-image generation, Sketchpad uses primitive drawing operations (lines, boxes, marks) combined with specialist vision models (object detection, segmentation) during sketching. This produces structured visual artifacts as intermediate reasoning steps, yielding 12.7% average improvement on math tasks and 8.6% on visual reasoning tasks over non-sketching baselines.

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
**Quadrant**: IV (Structured Traces + Execution)

**Justification**:

Visual Sketchpad is firmly in Quadrant IV for the following reasons:

1. **Structured Visual Artifacts as Reasoning Traces**: The key representation in Sketchpad is the drawn sketch — geometric line annotations, bounding box overlays, segmentation masks, highlighted correspondences. These are structured visual artifacts with spatial precision: a line has specific endpoints, a bounding box has exact coordinates, a mask has exact pixel membership. This is qualitatively different from text descriptions of visual elements.

2. **Tool Execution with Feedback**: Sketchpad uses two types of tool execution:
   - **Drawing tool execution**: The LM generates drawing commands (draw a line from (x1,y1) to (x2,y2)), which are executed on a canvas to produce a modified image
   - **Vision specialist execution**: The LM can invoke object detectors, segmentation models to draw bounding boxes or masks programmatically
   The executed sketch is then fed back to the multimodal LM as a new visual input — this constitutes genuine execution feedback where the modified image grounds subsequent reasoning

3. **Structural Properties of Sketches**: Geometric sketches have formal properties: a correctly drawn auxiliary line in a geometry problem either bisects an angle or it doesn't; a box drawn around the correct object either contains it or it doesn't. These properties are checkable against the original image and problem specification.

4. **Contrast with Quadrant I (LLaVA-CoT)**: LLaVA-CoT's Caption stage verbally describes what's in the image — this is text that may be hallucinated. Sketchpad actually draws on the image — the drawing is a physical artifact that exists and can be verified against the spatial content. You can check if a drawn line really passes through two labeled points.

5. **Contrast with Quadrant II (CogAgent)**: CogAgent produces text action specifications that get executed in a GUI environment. Sketchpad produces drawing specifications that get executed on a visual canvas. The distinction is that Sketchpad's outputs are structured visual traces that serve as evidence, while CogAgent's actions change environmental state but the reasoning trace itself remains textual.

---

## Key Contributions

1. **Visual CoT via Sketching**: Establishes sketching as a form of visual chain-of-thought that humans naturally use — drawing auxiliary lines in geometry, circling objects in visual search, highlighting corresponding regions across images. The framework systematizes this into a format multimodal LMs can use: generate drawing commands → execute on canvas → use modified image as new context.

2. **Primitive Drawing Operations**: Unlike text-to-image generation (which produces hallucinated images), Sketchpad uses geometric primitives (lines, arcs, circles, rectangles, dots, text annotations) and specialist vision models (for boxes and masks) that are precisely grounded. A drawn circle has exact center and radius; a detection box is produced by an actual detector run on the image.

3. **Multi-Domain Applicability**: Demonstrates sketch-based reasoning across: geometry problems (auxiliary lines, angle bisectors), function graphs (sketching curves for function analysis), chess positions (marking piece positions, threat lines), spatial reasoning (boxes for reference objects), and visual correspondence (matching marks across images). Each domain uses a tailored sketching strategy.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Drawn primitives are spatially grounded in the actual image: a line from point A to point B starts and ends at verifiable image coordinates
- Detection/segmentation tools produce boxes/masks from actual vision models run on the image — these are grounded in real visual evidence
- The sketched image can be compared to the original image to verify that drawn marks are positioned correctly relative to visual elements
- Each drawing operation is explicit and reviewable: "draw_line(start=[100, 200], end=[300, 400])" is unambiguous

### Checkability
**Assessment**: Very High
- Drawing commands have formal syntax and semantics — easily checkable for validity
- The resulting sketch image can be inspected to verify spatial correctness
- For geometry problems: drawn auxiliary lines can be checked to pass through the specified points
- For object detection boxes: boxes can be verified against expected object locations in the image
- The full sequence of drawing operations forms a checkable trace of the reasoning process

### Replayability
**Assessment**: Very High
- Drawing commands fully specify the reasoning trace: given the original image and the sequence of drawing commands, any step can be reproduced exactly
- The final sketch is a persistent artifact that captures the intermediate reasoning state
- Execution is deterministic: the same drawing commands on the same image always produce the same sketch
- Different implementations (rasterization engines) can be compared to verify consistency

### Faithfulness Risk
**Assessment**: Low
- Drawing execution is a deterministic process — the sketch faithfully represents the drawing commands
- For geometry: if the LM draws an auxiliary line, it actually gets drawn (not just claimed to be drawn)
- Risk: LM may draw geometrically incorrect constructions (e.g., misidentifying where to place an auxiliary line), but the error is visually transparent
- Detection-based drawings are limited by detector accuracy, but detector outputs are verifiable
- Much lower hallucination risk than text CoT: a false claim in text is invisible; a wrong drawing is visible

### Robustness
**Assessment**: Moderate-High
- Geometry domain: highly robust when the LM correctly identifies what to draw (auxiliary lines are straightforward to validate)
- Visual reasoning: robust when object detection/segmentation tools work correctly
- Sensitivity to image quality: low-resolution or visually complex images may produce imprecise drawing coordinates
- Complex multi-step sketching: later drawing steps depend on earlier ones; errors in early placement cascade
- No tool API dependency risks (drawing is local computation); vision specialists (for detection/segmentation) can fail

### Cost/Latency
**Assessment**: Moderate-High
- Each sketching step requires: LM generates drawing command → execute drawing → LM processes new sketched image → repeat
- Multi-step geometry problems may require 3-5 drawing steps per problem
- Vision specialist invocation for detection/segmentation adds extra model inference
- The modified (sketched) image is fed back as new visual input, requiring VLM processing for each drawing step
- More expensive than single-pass VLM but justified by accuracy gains on challenging reasoning tasks

### Security
**Assessment**: Low Risk
- Local drawing operations — no external API calls or web access
- Drawing commands are simple geometric specifications with no code execution risk
- Vision specialist calls are constrained to predefined detection/segmentation models
- Limited attack surface: adversarial content in images could affect detection tool outputs, but drawing commands themselves are safe

---

## Failure Modes

1. **Geometric Construction Errors**: For math tasks, the LM may correctly identify the type of auxiliary construction needed (e.g., "draw an altitude") but place it incorrectly due to misestimating coordinates from the image. Once a geometrically wrong auxiliary line is drawn, subsequent reasoning (angle calculations, triangle identification) is grounded in the wrong construction, producing systematically wrong answers.

2. **Drawing as Confirmation Bias**: The LM may draw sketches that confirm its initial hypothesis rather than genuinely exploring the visual problem. For example, if the LM initially assumes an object is at position A, it may draw a box around position A regardless of what the actual image shows, using the drawing to "commit" to a wrong answer rather than to discover the right one.

3. **Domain Limitation of Primitive Operations**: Sketchpad's drawing primitives (lines, boxes, circles, text) work well for geometry and spatial reasoning but are poorly suited for some visual tasks. For example, questions about texture, motion, emotional expression, or fine-grained color discrimination are hard to address through geometric drawing operations — the LM cannot "sketch" these properties meaningfully.

4. **Iterative Sketch Complexity Explosion**: For complex multi-step tasks requiring many drawing operations, the canvas becomes cluttered with overlapping annotations, making it harder for the VLM to interpret the latest sketched image. Unlike a clean original image, heavily annotated images may confuse the model's visual processing, reducing performance on problems that would benefit from many drawing steps.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric — task accuracy improvement with sketching)
- [ ] Step Correctness (drawing quality not directly evaluated)
- [x] Evidence Attribution (drawings grounded in image, verifiable)
- [x] Trace Replayability (drawing sequences are complete trace)
- [x] Robustness (evaluated across diverse math and vision domains)
- [x] Cost/Latency (compared inference costs with and without sketching)
- [ ] Other

### Benchmarks
**Math Tasks**:
- **Geometry** (custom, 150 problems): Plane geometry problems requiring auxiliary constructions
- **FunctionGraph**: Function analysis from graphical representations
- **BLINK Chess**: Chess position reasoning with piece relationships

**Vision Tasks**:
- **V\*Bench**: Complex visual search and spatial reasoning
- **BLINK Spatial Reasoning**: Multi-image spatial relationship understanding
- **BLINK Visual Correspondence**: Matching visual elements across images

### Key Results
- **Math tasks**: Average +12.7% improvement over non-sketching baseline (GPT-4o + Sketchpad)
- **Vision tasks**: Average +8.6% improvement over non-sketching baseline
- **V\*Bench**: 80.3% (new SOTA)
- **BLINK Spatial Reasoning**: 83.9% (new SOTA)
- **Visual Correspondence**: 80.8% (new SOTA)
- **GPT-4o baseline**: 60-65% on these tasks; Sketchpad adds ~15-20% absolute improvement

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Zero-shot prompting** of GPT-4o with drawing tool descriptions; no task-specific training

### Data Collection
- **No training required**: Sketchpad uses GPT-4o in zero-shot mode, providing it with descriptions of available drawing operations and vision tools in the system prompt
- **Task-specific prompting**: For each domain (geometry, spatial reasoning, etc.), a specialized prompt instructs the LM on which types of sketching actions are appropriate
- **Vision tools**: Pre-trained object detection (GLIP/GroundingDINO), segmentation (SAM) models for specialist operations

---

## Connections to Other Work

### Builds On
- **Chain-of-Thought (Wei et al., 2022)**: Extends CoT to the visual modality; "sketching as thinking" is the visual analog of text CoT
- **ViperGPT (2023)**: Both use executable operations as reasoning steps; Sketchpad extends to visual canvas operations
- **GPT-4V / GPT-4o**: Leverages multimodal LM's ability to both generate drawing instructions and interpret sketched images

### Related To
- **ViperGPT (ICCV 2023)**: Both are Quadrant IV approaches; ViperGPT uses Python code for vision API calls, Sketchpad uses drawing operations on a visual canvas
- **VideoAgent (ECCV 2024)**: Both use tool execution with feedback; VideoAgent uses memory queries, Sketchpad uses canvas operations
- **Human Visual Reasoning Studies**: Motivated by cognitive science showing humans draw auxiliary elements when solving visual-spatial problems

### Influenced
- Established sketching as a viable modality for multimodal reasoning
- Potential follow-up: training models to improve drawing quality for reasoning (learning when and what to sketch)

---

## Quotes & Key Insights

> "Humans draw to facilitate reasoning: we draw auxiliary lines when solving geometry problems; we mark and circle when reasoning on maps; we use sketches to amplify our ideas and relieve our limited-capacity working memory."

> "Sketchpad enables LMs to draw with lines, boxes, marks, etc., which is closer to human sketching and better facilitates reasoning. Sketchpad can also use specialist vision models during the sketching process."

**Key Insight 1: Visual Thinking as a First-Class Cognitive Modality**
Sketchpad's central observation is that human visual reasoning involves active manipulation of visual representations — not just passive observation. By giving LMs the ability to draw, the framework implements a cognitive strategy that humans find natural and effective. The +12.7% math improvement demonstrates that visual externalization provides genuine reasoning benefits.

**Key Insight 2: Primitives vs. Generation for Grounded Sketching**
Unlike text-to-image generation that produces hallucinated images, Sketchpad's drawing primitives are grounded operations on the actual image. This is crucial for verifiability: a line drawn through two specified points either passes through them or doesn't — there is no hallucination possible at the drawing execution level (though the choice of what to draw may be wrong).

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks - visual and math reasoning evaluation)
- [x] Section 7 (Applications - math reasoning, visual spatial tasks)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
Visual Sketchpad exemplifies the **full potential of Quadrant IV** — it combines the verifiability of structured geometric representations with the execution feedback of a drawing canvas. Unlike ViperGPT (which generates Python for *observing* visual data), Sketchpad *modifies* the visual data through structured drawing operations, creating new visual evidence that feeds back into the LM's reasoning. This makes it a uniquely powerful Quadrant IV approach where the structured representation is itself a visual artifact.

### Comparison Points
**Excels at**:
- Visual-spatial reasoning (native medium for geometric thinking)
- Human-interpretable reasoning traces (sketches are readable)
- Grounding without hallucination (execution is deterministic)

**Fails at**:
- Non-spatial visual tasks (texture, emotion, color nuance)
- Very complex multi-step sketching (canvas clutter)
- Tasks requiring photorealistic visual editing

---

## Notes

### Survey Placement Note (from original task)
The user initially placed Visual Sketchpad in Quadrant III but noted it actually belongs in Quadrant IV. This assessment is correct: Sketchpad involves both structured representations (geometric drawings) AND execution (drawings are executed and fed back as new visual inputs). The execution feedback loop is the key criterion for Quadrant IV placement. The note has been placed in the Quadrant IV file accordingly.

---

## BibTeX

```bibtex
@inproceedings{hu2024visualsketchpad,
  title={Visual Sketchpad: Sketching as a Visual Chain of Thought for Multimodal Language Models},
  author={Hu, Yushi and Shi, Weijia and Fu, Xingyu and Roth, Dan and Ostendorf, Mari and Zettlemoyer, Luke and Smith, Noah A and Krishna, Ranjay},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2024},
  url={https://arxiv.org/abs/2406.09403}
}
```

**Status**: ✅ Complete — Quadrant IV Paper
