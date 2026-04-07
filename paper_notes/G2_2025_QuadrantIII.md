# Paper Note: G2 (Q3 - Scene Graph Representation)

## Basic Information

**Title**: Generative Visual Commonsense Answering and Explaining with Generative Scene Graph Constructing

**Authors**: Fan Yuan, Xiaoyuan Fang, Rong Quan, Jing Li, Wei Bi, Xiaogang Xu, Piji Li

**Venue**: arXiv (preprint)

**Year**: 2025 (submitted Jan 2025)

**arXiv**: https://arxiv.org/abs/2501.09041

---

## Abstract Summary

G2 proposes a scene-graph-enhanced visual commonsense reasoning framework that addresses the limitation of existing methods failing to exploit real-world object relationship information. The approach first constructs location-free scene graphs using image patches and LLMs, then performs question answering and explanation generation based on the constructed scene graph information with automatic filtering and selection strategies.

---

## Methodology Analysis

### Representation Type
- [x] **Structured Trace** — scene graphs representing object relationships in the visual scene. The reasoning state consists of graph structures with nodes (objects) and edges (relationships), not free-form text.

### Verification Channel
- [x] **No Tools / No Execution** — reasoning is self-contained within the model's forward passes. No external API, detector, code interpreter, or retrieval system is called. Scene graph construction and filtering are internal processes.

### 2×2 Matrix Placement
**Quadrant**: **III (Structured w/o Tools)**

**Justification**:
- **Structured**: Intermediate reasoning states are scene graphs — structured representations capturing objects and their relationships. The graph structure provides explicit organization of visual information beyond free-form text.
- **No Tools**: All reasoning occurs within the model. Scene graph construction uses internal image patch processing and LLM capabilities without invoking external tools or execution environments.

---

## Key Contributions

1. **Scene-graph-enhanced reasoning framework**: Integrates scene graph construction directly into visual commonsense reasoning, enabling explicit modeling of object relationships rather than relying solely on training memory knowledge.

2. **Location-free scene graph construction**: Uses image patches and LLMs to construct scene graphs without requiring explicit spatial localization, making the approach more flexible and generalizable.

3. **Automatic graph filtering and selection**: Proposes strategies to absorb valuable scene graph information during training, filtering out noisy or irrelevant graph structures to improve reasoning quality.

4. **Joint answering and explanation**: Generates both commonsense answers and explanations based on the same scene graph representation, providing interpretable reasoning pathways.

---

## Verifiability Analysis

| Dimension | Rating | Reasoning |
|-----------|--------|-----------|
| **Grounding** | **Medium** | Scene graphs explicitly represent objects and relationships from the visual scene, providing some grounding. However, location-free representation may lose spatial grounding information. |
| **Checkability** | **Medium** | Graph structures can be checked for consistency (e.g., cycle detection, node-edge validity). However, correctness of relationships is hard to automatically verify without ground truth scene graphs. |
| **Replayability** | **Medium** | Given same model weights and input, same scene graphs should be produced. However, graph construction may involve stochastic LLM sampling, affecting determinism. |
| **Faithfulness Risk** | **Medium-High** | Scene graphs could be generated based on learned priors rather than actual visual evidence. The model might "hallucinate" relationships that seem plausible but aren't present in the image. |
| **Robustness** | **Medium** | Graph filtering helps with noisy inputs, but performance may degrade on scenes with unusual object configurations not seen during training. |
| **Cost/Latency** | **Medium** | Scene graph construction adds computational overhead compared to direct answering. Graph filtering and selection also add processing steps. |
| **Security** | **Low-Medium** | No external tool calls reduce attack surface. However, scene graph construction from image patches could be vulnerable to adversarial visual inputs. |

**Q3 vs Q1**: Q1 methods express reasoning as text tokens (free-form CoT). G2's scene graphs provide structured representation of object relationships — more organized than text but less interpretable than full natural language explanations.

**Q3 vs Q4**: Q4 methods produce executable artifacts (code, programs) that can be run to verify outputs. G2's scene graphs cannot be "executed" — they serve as intermediate representations for downstream reasoning but lack executable semantics.

---

## Failure Modes

1. **Graph hallucination**: The model may generate scene graph relationships that don't exist in the actual image, especially for ambiguous or low-resolution visual inputs.

2. **Information loss in location-free representation**: By not encoding spatial positions, the scene graph may miss critical spatial relationships needed for certain commonsense reasoning tasks.

3. **Filtering errors**: Automatic graph filtering might discard valuable relationships or retain noisy ones, especially for out-of-distribution scenes where the filtering criteria don't generalize.

4. **Cascade errors**: Errors in scene graph construction propagate to downstream answering and explanation, with no mechanism for correction or refinement.

5. **Object relationship ambiguity**: For complex scenes with multiple interacting objects, the scene graph may fail to capture all relevant relationships or create spurious connections.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy
- [x] Explanation Quality
- [ ] Step Correctness
- [ ] Evidence Attribution
- [ ] Trace Replayability
- [ ] Robustness
- [ ] Cost/Latency
- [x] Scene Graph Quality (construction evaluation)

### Benchmarks
- Visual Commonsense Reasoning (VCR) dataset
- Scene graph construction benchmarks
- Visual commonsense explanation datasets

### Key Results
- Extensive experiments demonstrate effectiveness on scene graph construction and visual commonsense answering/explaining tasks
- Ablation analysis shows contribution of scene graph filtering and selection strategies
- Outperforms baselines that don't use structured scene graph representations

---

## Training & Alignment

### Method
- [x] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [x] Graph Filtering Learning
- [ ] Other: Scene graph selection strategies

### Data Collection
Training data includes scene graph annotations or uses automatic scene graph construction from images. The model learns to construct location-free scene graphs from image patches and LLM-generated descriptions, then uses these graphs for downstream reasoning tasks.

---

## Connections to Other Work

### Builds On
- Scene graph generation literature (e.g., Neural Motifs, Scene Graph Generation by Recognition)
- Visual commonsense reasoning frameworks (VCR dataset and models)
- Graph-based reasoning approaches in vision-language tasks

### Related To
- **CCoT**: Also uses scene graphs but for different reasoning tasks
- **MCOUT**: Both are Q3 methods but MCOUT uses latent vectors while G2 uses explicit graph structures
- **COGT**: Both use graph structures (causal graphs vs scene graphs) for structured reasoning

### Influenced
- Potential influence on subsequent scene-graph-enhanced VLM reasoning work
- May inspire graph filtering strategies for other structured representation methods

---

## Quotes & Key Insights

> "Existing work fails to effectively exploit the real-world object relationship information present within the scene, and instead overly relies on knowledge from training memory."

**Key Insight**: G2 addresses a fundamental limitation in visual commonsense reasoning — the over-reliance on memorized knowledge rather than scene-specific relationship information. By constructing scene graphs dynamically, the model can ground its reasoning in the actual visual content.

**Design Trade-off**: Location-free scene graphs sacrifice spatial precision for flexibility and generalizability. This design choice reflects the insight that many commonsense reasoning tasks depend more on object relationships than exact spatial positions.

---

## Survey Placement

### Section Placement
- [x] Section 4.X (Methods by Quadrant) — **Quadrant III: Structured Representations without Tools**
- [ ] Section 5 (Learning & Alignment)
- [ ] Section 6 (Evaluation & Benchmarks)
- [ ] Section 7 (Applications)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
G2 serves as a representative example of **scene graph-based reasoning** in Quadrant III. It demonstrates how structured representations (graphs) can improve visual commonsense reasoning without requiring external tools. The paper supports the survey's argument about the trade-offs between structure and interpretability in Q3 methods.

### Comparison Points
- **Excels at**: Explicit object relationship modeling, interpretable graph structures, joint answering and explanation
- **Fails at**: Spatial grounding (location-free), automatic verification of graph correctness, handling ambiguous relationships
- **Contrast with MCOUT**: G2 uses human-readable graphs vs MCOUT's latent vectors — more interpretable but potentially less expressive
- **Contrast with COGT**: G2's scene graphs represent visual objects vs COGT's causal graphs representing linguistic dependencies

---

## Notes

- This paper represents the "scene graph" sub-category of Q3 structured representations, complementing MCOUT's "latent vectors" and COGT's "causal graphs".
- The location-free design is an interesting compromise — retains graph structure but sacrifices spatial grounding for flexibility.
- Graph filtering and selection strategies are important contributions that address the noise problem in automatically constructed scene graphs.
- Should be cited alongside other scene-graph-based reasoning methods in the survey's Q3 section.
- The automatic graph filtering approach could potentially be applied to other structured representation methods beyond scene graphs.

---

## BibTeX

```bibtex
@article{yuan2025g2,
  title     = {Generative Visual Commonsense Answering and Explaining with Generative Scene Graph Constructing},
  author    = {Fan Yuan and Xiaoyuan Fang and Rong Quan and Jing Li and Wei Bi and Xiaogang Xu and Piji Li},
  journal   = {arXiv preprint arXiv:2501.09041},
  year      = {2025},
  url       = {https://arxiv.org/abs/2501.09041},
  doi       = {10.48550/arXiv.2501.09041}
}
```
