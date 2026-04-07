# Paper Note: Graph-of-Mark

## Basic Information

**Title:** Graph-of-Mark: Promote Spatial Reasoning in Multimodal Language Models with Graph-Based Visual Prompting

**Authors:** Giacomo Frisoni, Lorenzo Molfetta, Mattia Buzzoni, Gianluca Moro

**Venue:** arXiv preprint

**Year:** 2026

**Link:**
- arXiv: https://arxiv.org/abs/2603.06663
- Date: March 2026

---

## Abstract Summary

Graph-of-Mark (GoM) is the first pixel-level visual prompting technique that overlays scene graphs onto the input image for spatial reasoning tasks. Unlike Set-of-Mark and similar approaches that treat marked objects as isolated entities, GoM captures relationships between objects by overlaying scene graph structure (nodes, edges) on the image. Evaluated across 3 open-source MLMs and 4 datasets, GoM consistently improves zero-shot capability in interpreting object positions and relative directions, with up to 11 percentage points improvement in visual question answering and localization.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT)
- [x] Structured Trace (scene graph overlaid on image—nodes = objects, edges = relations; graph structure is the intermediate representation)

### Verification Channel
- [x] No Tools / No Execution (scene graph is pre-computed or from a model, not from runtime tool calls—training-free prompting)
- [ ] Tool-Augmented (GoM is inference-time visual prompting; scene graph may come from a detector/parser, but the key is the prompting format)
- [ ] Execution Feedback

### 2×2 Matrix Placement
**Quadrant:** III (Structured Trace, No Tools) — with a note on scene graph source

**Justification:**

1. **Structured Scene Graph Representation**: GoM overlays a scene graph (nodes = objects, edges = relations) onto the image. The graph structure is a formal, structured representation—not free-form text. The MLM reasons over this graph-augmented image.

2. **No Runtime Tool Execution**: GoM is a visual prompting technique. The scene graph may be produced by an off-the-shelf detector/parser (pre-processing), but at inference the MLM does not call tools in a loop. The augmented image (with graph overlaid) is the input. No ReAct-style tool feedback.

3. **Q3 vs. Q1**: The scene graph provides structured intermediate representation—explicit object identities and relations. This is distinct from Q1's free-form textual CoT.

4. **Q3 vs. Q2/Q4**: If the scene graph were produced by runtime tool calls with feedback (e.g., iterative grounding), it would be Q2/Q4. GoM uses the graph as a static prompt augmentation—no execution loop. The graph is a structured input, not a tool-augmented trace.

---

## Key Contributions

1. **First Pixel-Level Scene Graph Visual Prompting**: GoM is the first technique to overlay scene graphs onto input images for spatial reasoning. Unlike Set-of-Mark (boxes + numeric IDs only), GoM captures object relationships via graph edges, enabling relational reasoning.

2. **Consistent Zero-Shot Improvement**: Evaluated across 3 open-source MLMs and 4 datasets. GoM consistently improves zero-shot capability in object positions and relative directions—up to 11 percentage points in VQA and localization.

3. **Extensive Ablations**: Ablations on drawn components (nodes, edges, etc.) and impact of auxiliary graph descriptions in the text prompt provide design guidance for graph-based visual prompting.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** High

Scene graph provides explicit grounding—each object has a mark (box/ID), and edges encode relations. The MLM reasons over this structured input. Object positions and relations are visually present on the image.

### Checkability
**Assessment:** Medium-High

Scene graph structure can be checked (do nodes/edges match the image?). Object detection and relation extraction may have errors—the graph could be wrong. But the structure is inspectable. VQA/localization answers can be validated against ground truth.

### Replayability
**Assessment:** High

Given same image and scene graph, the MLM's output is reproducible (deterministic decoding). The graph overlay is deterministic given the graph. Full pipeline (graph extraction → overlay → MLM) can be replayed.

### Faithfulness Risk
**Assessment:** Medium (reduced vs. no prompting)

Graph structure constrains reasoning—the model must reason over provided objects and relations. However, if the scene graph is wrong (detection/relation errors), the model may reason from incorrect structure. No runtime verification of graph correctness.

### Robustness
**Assessment:** Medium

Tested on 4 datasets, 3 MLMs. Performance depends on scene graph quality. Poor object detection or relation extraction would degrade GoM. Distribution shift in image types may affect graph extraction.

### Cost/Latency
**Assessment:** Low-Medium

Scene graph extraction adds pre-processing cost (one-time per image). Overlay and MLM inference are standard. No multi-turn tool loop—efficient compared to agentic approaches.

### Security
**Assessment:** Low Risk

No runtime tool calls. Scene graph could be manipulated (adversarial graph overlay), but attack surface is limited. Standard MLM risks apply.

---

## Failure Modes

1. **Scene Graph Quality**: GoM's effectiveness depends on accurate object detection and relation extraction. Noisy or incomplete graphs (missing objects, wrong relations) will mislead the MLM.

2. **Graph Complexity**: Dense scenes with many objects may produce cluttered graph overlays—reducing readability. The MLM may struggle to parse complex graphs.

3. **Auxiliary Text Prompt Sensitivity**: Ablations show impact of graph descriptions in the text prompt. Suboptimal prompt design may reduce gains.

4. **Domain Limitation**: Evaluated on spatial reasoning (positions, relative directions). Performance on other reasoning types (e.g., counting, attribute reasoning, causal reasoning) may not improve—or may not be tested.

5. **MLM Compatibility**: Different MLMs may respond differently to graph overlays. The 3 tested MLMs may not represent all architectures.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (VQA, localization)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [ ] Trace Replayability
- [x] Robustness (3 MLMs, 4 datasets)
- [ ] Cost/Latency
- [ ] Other: Ablations on components

### Benchmarks
- 4 datasets (VQA, localization)
- 3 open-source MLMs

### Key Results
- Up to 11 percentage points improvement in VQA and localization
- Consistent improvement across MLMs and datasets
- Ablations inform design of graph-based visual prompting

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Training-free visual prompting

### Data Collection
- GoM is training-free. Scene graph may come from pre-trained detectors/parsers.
- Evaluation on 4 spatial reasoning datasets

---

## Connections to Other Work

### Builds On
- Set-of-Mark (Xu et al.)—object marking with boxes/IDs
- Scene graph generation
- Visual prompting for VLMs

### Related To
- Mario (multimodal graph reasoning)—Mario reasons over MMGs; GoM overlays scene graphs on pixels
- Graph-of-Mark focuses on spatial reasoning with pixel-level overlay

### Influenced
- Future work on graph-based visual prompting
- Scene graph integration for spatial reasoning

---

## Quotes & Key Insights

> "These approaches treat marked objects as isolated entities, failing to capture the relationships between them. On these premises, we propose Graph-of-Mark (GoM), the first pixel-level visual prompting technique that overlays scene graphs onto the input image."

> "Our results demonstrate that GoM consistently improves the zero-shot capability of MLMs in interpreting object positions and relative directions."

**Key Insight:** **Relations matter for spatial reasoning**—Set-of-Mark provides object-level grounding, but GoM adds relation-level structure (edges). Capturing "left_of," "above," etc. explicitly improves spatial reasoning, validating structured visual prompting as a Q3 approach.

---

## Survey Placement

### Section Placement
- [x] Section 4.3 (Methods by Quadrant — Quadrant III: Structured Visual Prompting, Scene Graphs)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks — spatial reasoning)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — scene graph quality)

### Narrative Role
Graph-of-Mark exemplifies **Q3 training-free structured prompting**—using scene graphs as structured input to improve spatial reasoning without tools or execution. It extends Set-of-Mark by adding relational structure, demonstrating that structured intermediate representation (graph) improves over unstructured marking.

### Comparison Points
**Excels at:** Training-free, spatial reasoning, relation capture, 11pt improvement
**Fails at:** Dependency on scene graph quality, no runtime verification

---

## Notes

GoM's scene graph may come from external models (object detector, relation extractor). The boundary between "pre-processing" and "tool use" is subtle—we place GoM in Q3 because the MLM does not invoke tools at inference; the graph is a static input augmentation.

---

## BibTeX

```bibtex
@article{frisoni2026gom,
  title={{Graph-of-Mark}: Promote Spatial Reasoning in Multimodal Language Models with Graph-Based Visual Prompting},
  author={Frisoni, Giacomo and Molfetta, Lorenzo and Buzzoni, Mattia and Moro, Gianluca},
  journal={arXiv preprint arXiv:2603.06663},
  year={2026},
  url={https://arxiv.org/abs/2603.06663}
}
```

**Status:** ✅ Complete — Quadrant III Paper (Scene Graph Visual Prompting)
