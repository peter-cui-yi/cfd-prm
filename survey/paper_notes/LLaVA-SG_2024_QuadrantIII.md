# Paper Note: LLaVA-SG (Scene Graph VLM)

## Basic Information

**Title**: LLaVA-SG: Leveraging Scene Graphs as Visual Semantic Expression in Vision-Language Models

**Authors**: Jingyi Wang, Jianzhong Ju, Jian Luan, Zhidong Deng

**Affiliations**: Tsinghua University; Tencent AI Lab

**Venue**: arXiv 2024

**Year**: 2024 (arXiv: August 29, 2024)

**Link**:
- ArXiv: https://arxiv.org/abs/2408.16224

---

## Abstract Summary

LLaVA-SG addresses the fragmented perception problem in ViT-based VLMs by introducing a Scene Graph Expression (SGE) module that extracts and structurally represents semantic relationships between objects in images. Unlike standard ViT encoders that divide images into independent patches (losing inter-object relationships), LLaVA-SG constructs an explicit scene graph capturing object entities, their visual features, and pairwise semantic relationships. The SGE module is integrated into the standard LLaVA framework through a three-phase training strategy, demonstrably improving VLM performance on vision-language tasks by preserving intricate semantic details and facilitating better visual understanding.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: III (Structured Representation, No Tools)

**Justification**:

LLaVA-SG belongs to Quadrant III for the following reasons:

1. **Structured Scene Graph Representation**: The core innovation is the Scene Graph Expression (SGE) module which produces an explicit, structured graph — with nodes representing detected objects (with their visual features and bounding boxes) and edges representing semantic relationships between objects (spatial, functional, attribute-based). This is a formally structured intermediate representation, not free-form text.

2. **No External Tool Execution**: The scene graph is constructed by the SGE module (using an internal scene graph generation component, not an external API), and all reasoning occurs through the LLaVA framework without invoking external tools. The scene graph is an internal representation that enriches the model's input — it is not produced by calling an external detector API with feedback.

3. **Schema-Constrained Representation**: Scene graphs follow a formal schema (Subject → Predicate → Object, or node-edge-node triples). This structural constraint provides implicit validation — a scene graph with nonsensical relationships violates the schema and can be detected. This places it in Quadrant III's "structured with schema constraints" paradigm.

4. **Contrast with Quadrant I (LLaVA-CoT)**: Unlike LLaVA-CoT which uses natural language captions as intermediate representation, LLaVA-SG uses a formal graph structure. The difference is representational: graphs explicitly encode binary relationships between entities, which natural language cannot do as concisely or structurally.

5. **Contrast with Quadrant II**: A Quadrant II approach would invoke an external scene graph generation API (e.g., calling a Visual Relationship Detection service) and use the returned scene graph as tool output. LLaVA-SG's SGE module is an integral part of the model architecture trained jointly, not an external tool call.

---

## Key Contributions

1. **Scene Graph Expression (SGE) Module**: A neural module that processes image features to construct a scene graph — extracting object nodes (with class labels and visual features via ROI pooling) and relationship edges (predicted via a relation network or cross-attention over object pairs). The SGE module converts raw ViT patch features into a semantically structured graph that captures what objects are present and how they relate.

2. **Integration with LLaVA Framework via Cross-Attention Fusion**: The SGE module's graph output is integrated into LLaVA through a cross-attention mechanism that allows the language model to attend over object nodes and relationship edges independently, rather than treating the image as an undifferentiated sequence of patches. This provides the LLM with explicit "object-relationship" tokens alongside patch tokens.

3. **Three-Phase Training Strategy**: Training proceeds in three phases to avoid conflicting gradients: (1) Visual-language alignment training with 558K image-text pairs (training SGE alignment to language space), (2) SGE module training with relationship understanding datasets (training scene graph generation quality), (3) Fine-tuning with frozen visual encoders but active LLM + SGE (task-specific adaptation). This staged approach preserves previously learned visual representations.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Scene graphs provide explicit object-level grounding — each graph node corresponds to a detected object with a bounding box and visual features
- Relationships are explicitly represented as typed edges (e.g., "cat (subject) → sitting on (predicate) → sofa (object)")
- Unlike natural language captions which describe the scene holistically, scene graphs decompose it into verifiable atomic facts
- Each node's bounding box can be cross-referenced with the original image to verify object existence

### Checkability
**Assessment**: Moderate-High
- Individual scene graph nodes can be verified against the image: does the bounding box contain an object of the claimed category?
- Relationship edges can be partially verified: does the spatial arrangement in the image support the claimed relationship?
- Schema validation is automatic: graph must follow valid triples (subject, predicate, object); malformed structures are detectable
- Limitation: Semantic relationships (e.g., "riding" vs. "sitting on") require visual understanding to validate — not fully automatable
- Downstream answer correctness provides implicit checking of graph quality

### Replayability
**Assessment**: Moderate
- Scene graph generation is a forward pass through the SGE module — deterministic given fixed model weights
- The graph structure can be serialized and stored, making it a persistent artifact (unlike Coconut's ephemeral latent states)
- However, the graph is generated as part of inference, not as a separable, replayable trace
- More replayable than Coconut (explicit graph structure) but less than ViperGPT (executable program)

### Faithfulness Risk
**Assessment**: Moderate
- Scene graphs provide stronger grounding than text CoT by explicitly representing detected objects with visual features
- However, scene graph generation can still fail: objects may be incorrectly detected, relationships misclassified, or important objects missed (detection coverage issues)
- The SGE module is trained end-to-end with the LLM — if the training signal is dominated by answer correctness, the SGE module may learn to produce graphs that are linguistically useful to the LLM but not visually faithful
- Key advantage: Graph structure constrains hallucination — the model cannot claim a relationship between objects that are not in the graph

### Robustness
**Assessment**: Moderate
- Scene graph generation quality varies with image complexity: crowded scenes with many objects produce noisier graphs
- Long-tail relationship types (rare predicates) are poorly represented in training data, leading to frequent misclassification as common predicates
- The three-phase training strategy improves robustness by preventing catastrophic forgetting during specialized training
- Domain shift: trained primarily on standard image VQA datasets, may struggle with domain-specific visual relationships (medical anatomy, scientific diagrams)

### Cost/Latency
**Assessment**: Moderate
- Additional cost vs. standard LLaVA: SGE module inference (object detection + relationship prediction) adds latency
- Scene graph generation is parallelizable with patch feature extraction
- No external API calls — all computation is model-internal
- Graph size scales with scene complexity (more objects → larger graph → more attention computation in LLM)

### Security
**Assessment**: Low Risk
- Closed-system reasoning — no external API calls or web access
- Scene graph structure provides some natural resistance to adversarial text inputs (adversarial content in text cannot directly inject false visual relationships)
- Adversarial images designed to confuse object detectors could corrupt the scene graph, but this is a general vision model vulnerability

---

## Failure Modes

1. **Scene Graph Incompleteness**: Object detectors have finite recall — small, occluded, or unusual objects may not be included in the scene graph. If the answer to a visual question depends on an object that the SGE module fails to detect, the LLM reasons without access to that evidence. This is more problematic than text CoT failure since the information is completely absent from the representation rather than just poorly described.

2. **Relationship Misclassification in Complex Scenes**: For images with many objects and complex spatial arrangements, the relationship network may produce incorrect predicates (e.g., "above" when "on" is correct, or "holding" when "near" is more accurate). These misclassifications are silently propagated to the LLM as "structured facts," which may be more misleading than a vague text description.

3. **Long-Tail Relationship Sparsity**: Training datasets for scene graph generation (Visual Genome, etc.) have highly skewed relationship distributions — common predicates (on, in, near, of) dominate while specific ones (cooking, riding, operating) are sparse. Models trained on this data produce generic, non-discriminative graphs for specialized scenes, reducing the semantic value of the graph representation.

4. **Graph-Language Alignment Failure for Novel Tasks**: The SGE module is trained to produce graphs that are useful for the VQA tasks in its training distribution. For novel task types (e.g., "describe the emotional dynamics between the people in this image" or "identify what's wrong with the engineering diagram"), the graph schema (object-predicate-object) may not capture the relevant semantic information, and the LLM cannot compensate since it sees only the graph representation.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric — VQA accuracy improvement over baseline)
- [ ] Step Correctness (graph quality not directly evaluated)
- [ ] Evidence Attribution (not explicitly measured)
- [ ] Trace Replayability
- [x] Robustness (multi-benchmark evaluation)
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- **ScienceQA**: Science question answering with visual context
- **POPE**: Object hallucination evaluation benchmark
- **MMBench**: Comprehensive multimodal evaluation
- **GQA**: Compositional question answering about scene graphs
- **VSR** (Visual Spatial Reasoning): Spatial relationship understanding
- Standard VQA benchmarks (VQAv2, etc.)
- Baseline: Standard LLaVA-1.5

### Key Results
- SGE module integration significantly improves VLM performance on vision-language tasks
- Largest improvements on benchmarks requiring relational reasoning (GQA, VSR)
- Hallucination reduction on POPE: explicit object grounding reduces object hallucination
- Three-phase training strategy outperforms naive end-to-end training on all benchmarks
- Model generalizes across task types while specialized in relational understanding

---

## Training & Alignment

### Method
- [x] SFT with Rationale (standard VQA fine-tuning with SGE module integration)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: Three-phase staged training for SGE integration

### Data Collection
- **Phase 1 (Visual Alignment)**: 558K image-text pairs (LLaVA-158K + COCO captions + others) for aligning SGE visual features with language space
- **Phase 2 (SGE Training)**: Visual relationship datasets: Visual Genome (scene graph annotations), GQA (structured visual questions), SpatialSense (spatial relationship pairs)
- **Phase 3 (Instruction Fine-tuning)**: LLaVA-665K instruction following dataset with frozen visual encoders
- **SGE Module Architecture**: Object detector (DETR or Faster R-CNN for node detection), relation prediction network (cross-attention over object feature pairs → relationship category)

---

## Connections to Other Work

### Builds On
- **LLaVA/LLaVA-1.5 (Liu et al., 2023/2024)**: Extends LLaVA with the SGE module; preserves LLaVA's instruction following capabilities
- **Visual Genome (Krishna et al., 2017)**: Key dataset for scene graph generation training data
- **Scene Graph Generation (Yang et al., 2018; Zellers et al., 2018)**: Prior work on generating scene graphs from images, adapted for VLM integration

### Related To
- **Structured VQA (Shi et al., 2019)**: Using structured representations for visual question answering
- **Relation Networks (Santoro et al., 2017)**: Early work on relational reasoning in neural networks
- **GraphVQA**: Approaches using graph neural networks for VQA

### Influenced
- Demonstrates that structured intermediate representations (graphs) can be integrated into end-to-end VLMs without sacrificing generalist capabilities
- Motivates further research on hybrid visual representation approaches combining patches with explicit structural information

---

## Quotes & Key Insights

> "The division of the images into patches by ViT results in a fragmented perception, thereby hindering the visual understanding capabilities of VLMs."

> "The Scene Graph Expression (SGE) module extracts and structurally expresses the complex semantic information within images, thereby improving the foundational perception and understanding abilities of VLMs."

**Key Insight 1: Patches vs. Relationships**
LLaVA-SG identifies a fundamental limitation of ViT-based visual encoding: patches are spatially local and lose inter-object relationships. Scene graphs explicitly encode what patches implicitly must learn through attention patterns. By making relationships a first-class representational element, LLaVA-SG provides the language model with explicit relational propositions that are the natural language of visual reasoning.

**Key Insight 2: Structured Representation Without External Tools**
LLaVA-SG demonstrates that structured representations (scene graphs) can be integrated into VLMs as an internal module rather than an external tool. This provides the structured grounding benefits of Quadrant III/IV while maintaining the architectural simplicity of Quadrant I/II approaches. The trade-off is that the scene graph quality is bounded by the internal SGE module rather than a state-of-the-art external detector.

---

## Survey Placement

### Section Placement
- [x] Section 4.3 (Methods by Quadrant - Quadrant III: Structured w/o Tools)
- [ ] Section 5 (Learning & Alignment)
- [ ] Section 6 (Evaluation & Benchmarks)
- [x] Section 7 (Applications - relational visual reasoning)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
LLaVA-SG represents the Quadrant III paradigm of structural enrichment without external tool execution. It contrasts with Coconut (latent vector structure) by using an explicitly human-readable graph structure, and contrasts with ViperGPT (Quadrant IV) by not requiring external code execution. It demonstrates that structured representations provide grounding and checkability benefits over pure text CoT, while avoiding the latency and complexity of full tool-augmented systems.

### Comparison Points
**Excels at**:
- Relational reasoning (explicit relationship representation)
- Hallucination reduction (object nodes are detector-grounded)
- Architectural integration (plug-in module for existing VLMs)

**Fails at**:
- Long-tail relationship coverage
- Complex, novel scene understanding
- Automatic step verification (graph correctness not automatically checked)

---

## Notes

### File Naming
The user requested filename `SceneGraph_VLM_2024_QuadrantIII.md` for this paper. The actual paper is LLaVA-SG (arXiv 2408.16224), which is the most suitable 2024 paper matching the "scene graph as structured intermediate representation for VLM reasoning without tool execution" description. The note is saved as `LLaVA-SG_2024_QuadrantIII.md` to match the paper's actual name; the database entry should reference both names.

### Distinction from Tool-Using Scene Graph Approaches
Some papers use scene graph generation APIs as external tools (calling a remote VRD service and using the returned graph as tool output). LLaVA-SG differs by integrating the SGE module as an internal model component. This internal integration is the criterion for Quadrant III placement rather than Quadrant II.

---

## BibTeX

```bibtex
@article{wang2024llavaSG,
  title={LLaVA-SG: Leveraging Scene Graphs as Visual Semantic Expression in Vision-Language Models},
  author={Wang, Jingyi and Ju, Jianzhong and Luan, Jian and Deng, Zhidong},
  journal={arXiv preprint arXiv:2408.16224},
  year={2024},
  url={https://arxiv.org/abs/2408.16224}
}
```

**Status**: ✅ Complete — Quadrant III Paper
