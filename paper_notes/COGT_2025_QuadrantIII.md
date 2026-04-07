# Paper Note: COGT (Q3 - Causal Graphical Models)

## Basic Information

**Title**: Causal Graphical Models for Vision-Language Compositional Understanding

**Authors**: Fiorenzo Parascandolo, Nicholas Moratelli, Enver Sangineto, Lorenzo Baraldi, Rita Cucchiara

**Venue**: ICLR 2025

**Year**: 2025

**arXiv**: https://arxiv.org/abs/2412.09353

**Code**: https://github.com/aimagelab/COGT

**Project Page**: https://aimagelab.github.io/COGT/

---

## Abstract Summary

COGT addresses Vision-Language Models' inability to understand compositional language properties by modeling dependency relations among textual and visual tokens using Causal Graphical Models (CGMs) built from dependency parsers. The decoder's generative process follows a partially-ordered structure based on the CGM, encouraging the model to learn main causal dependencies while discarding spurious correlations, significantly outperforming state-of-the-art compositional approaches on five benchmarks.

---

## Methodology Analysis

### Representation Type
- [x] **Structured Trace** — causal graphical models representing dependency relations among tokens. The reasoning state is a partially-ordered graph structure derived from syntactic dependency parsing, not free-form text sequences.

### Verification Channel
- [x] **No Tools / No Execution** — reasoning is self-contained within the model's forward passes. The dependency parser is used during training to construct the CGM structure, but no external tools are called during inference.

### 2×2 Matrix Placement
**Quadrant**: **III (Structured w/o Tools)**

**Justification**:
- **Structured**: Intermediate reasoning follows a causal graphical model structure — a partially-ordered graph representing syntactic and semantic dependencies. This is fundamentally different from free-form text generation, as the generation order is constrained by the graph topology.
- **No Tools**: All reasoning occurs within the model. The CGM structure is pre-computed from dependency parsing and used to guide the decoder's attention mechanism, but no external API or execution environment is invoked during reasoning.

---

## Key Contributions

1. **Causal Graphical Models for VLMs**: First work to model vision-language compositional understanding using CGMs, capturing dependency relations between textual and visual tokens through graph-based structural constraints.

2. **Dependency Guided Attention**: Introduces an attention mechanism that controls which embeddings can attend to each other based on the CGM structure, enforcing the causal dependencies learned from syntactic parsing.

3. **Partially-ordered generative process**: Unlike standard autoregressive (sequential) or parallel prediction, COGT's decoder follows a partially-ordered generation schedule derived from the CGM, enabling more flexible yet structured reasoning.

4. **Strong empirical results**: Significantly outperforms all state-of-the-art compositional approaches on five benchmarks (ARO, SugarCrepe, VL-CheckList, ColorSwap, FG-OVD) even compared to methods trained on larger datasets.

---

## Verifiability Analysis

| Dimension | Rating | Reasoning |
|-----------|--------|-----------|
| **Grounding** | **Medium** | CGM structure is derived from linguistic dependency parsing, providing structural grounding to language. Visual tokens are integrated into the graph, but visual grounding strength depends on the quality of vision-language alignment. |
| **Checkability** | **Medium-High** | Graph structure can be checked for validity (e.g., no cycles in dependency tree, proper parent-child relationships). The partially-ordered generation can be verified against the CGM topology. |
| **Replayability** | **High** | Given same model weights, same input, and same CGM structure, the generation process is deterministic. The CGM provides a fixed structural constraint that ensures reproducible reasoning paths. |
| **Faithfulness Risk** | **Medium** | The CGM structure is externally derived from dependency parsing, reducing the risk of the model inventing spurious dependencies. However, the model might still learn shortcuts that satisfy the graph structure without true compositional understanding. |
| **Robustness** | **Medium-High** | CGM structure provides robustness against spurious correlations by explicitly modeling causal dependencies. However, parsing errors in CGM construction could propagate through the reasoning process. |
| **Cost/Latency** | **Medium** | CGM construction requires dependency parsing (one-time cost per caption). The partially-ordered generation may have different latency characteristics compared to standard autoregressive decoding. |
| **Security** | **Low-Medium** | No external tool calls during inference reduce attack surface. Dependency parsing is performed offline during training/data preparation. |

**Q3 vs Q1**: Q1 methods express reasoning as free-form text tokens (CoT). COGT's causal graphs provide structured constraints on the generation process — the reasoning follows a graph-determined partial order rather than linear sequence, capturing compositional structure more explicitly.

**Q3 vs Q4**: Q4 methods produce executable artifacts (code, programs). COGT's CGM is not executable but provides structural constraints on generation. The graph serves as a "blueprint" for reasoning rather than an executable program.

---

## Failure Modes

1. **Dependency parsing errors**: Incorrect CGM construction from faulty dependency parsing leads to wrong structural constraints, causing the model to learn incorrect causal relationships.

2. **Vision-language misalignment**: The CGM may fail to properly integrate visual tokens with textual dependencies, especially for complex scenes where visual relationships don't map cleanly to linguistic structure.

3. **Over-constrained generation**: The partially-ordered structure might be too restrictive for certain compositional tasks that require more flexible reasoning patterns not captured by the CGM.

4. **Spurious correlation learning**: Despite the CGM structure, the model might still learn to exploit dataset biases that happen to align with the graph topology without true compositional understanding.

5. **Generalization to novel structures**: Performance may degrade on sentences with dependency structures significantly different from those seen during training, as the CGM-based constraints are learned from specific syntactic patterns.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy
- [x] Compositional Understanding Metrics
- [x] Step Correctness (structural validity)
- [ ] Evidence Attribution
- [x] Trace Replayability
- [x] Robustness
- [ ] Cost/Latency
- [ ] Security

### Benchmarks
- **ARO** (Attribution, Relation, Order)
- **SugarCrepe**
- **VL-CheckList**
- **ColorSwap**
- **FG-OVD** (Fine-Grained Open-Vocabulary Detection, proposed benchmark)

### Key Results
- Significantly outperforms all state-of-the-art compositional approaches by a large margin on all five benchmarks
- Improves over methods trained using much larger datasets
- Particularly strong gains on tasks requiring fine-grained compositional understanding (subject-verb-object relationships)
- Demonstrates effectiveness of causal graphical modeling for vision-language compositional tasks

---

## Training & Alignment

### Method
- [x] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [x] Structure-Guided Training
- [ ] Other: CGM-constrained decoding

### Data Collection
Training data consists of image-caption pairs where captions are parsed using dependency parsers to construct CGMs. The CGM structure is used to guide the decoder's attention mechanism during training, encouraging the model to learn causal dependencies aligned with the graph topology.

**Key Design**: The decoder is conditioned by the VLM visual encoder, and the generative process follows the partial order defined by the CGM. This structure encourages learning main causal dependencies while discarding spurious correlations.

---

## Connections to Other Work

### Builds On
- Causal graphical models literature (Pearl's causal inference, structural causal models)
- Dependency parsing and syntactic tree representations
- Vision-language compositional understanding benchmarks and methods
- Structured attention mechanisms in transformers

### Related To
- **G2**: Both use graph structures (causal graphs vs scene graphs) for structured reasoning in Q3
- **MCOUT**: Both are Q3 methods but COGT uses explicit causal graphs vs MCOUT's latent vectors
- **Chain-of-Table**: Both use structured representations (graphs vs tables) to guide reasoning, but COGT focuses on compositional understanding while Chain-of-Table targets table-based reasoning

### Influenced
- Potential influence on subsequent work using causal structures for VLM reasoning
- May inspire graph-constrained decoding approaches for other vision-language tasks
- Could influence compositional benchmark design and evaluation methodologies

---

## Quotes & Key Insights

> "Vision-Language Models typically treat image captions as 'bags of words,' struggling to recognize relationships between entities (e.g., confusing 'the horse is eating the grass' with 'the grass is eating the horse')."

> "Our decoder's generative process is partially-ordered following the CGM structure. This structure encourages the decoder to learn only the main causal dependencies in a sentence discarding spurious correlations."

**Key Insight**: COGT addresses a fundamental limitation in VLMs — the failure to capture compositional structure in language. By using causal graphical models derived from dependency parsing, the method enforces structural constraints that prevent the model from treating captions as unordered word collections.

**Design Trade-off**: The partially-ordered generation sacrifices some flexibility (compared to free-form text generation) for improved compositional understanding. This trade-off is justified by the significant empirical gains on compositional benchmarks.

**Theoretical Foundation**: The use of causal graphical models provides a principled framework for distinguishing true causal dependencies from spurious correlations — a key challenge in compositional reasoning.

---

## Survey Placement

### Section Placement
- [x] Section 4.X (Methods by Quadrant) — **Quadrant III: Structured Representations without Tools**
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks) — Compositional understanding benchmarks
- [ ] Section 7 (Applications)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
COGT serves as a representative example of **causal graph-based reasoning** in Quadrant III. It demonstrates how structural constraints derived from linguistic theory (dependency parsing, causal models) can improve VLM reasoning without external tools. The paper supports the survey's argument about the diversity of structured representations in Q3 and their effectiveness for specific reasoning tasks (compositionality).

### Comparison Points
- **Excels at**: Capturing compositional structure, discarding spurious correlations, interpretable graph constraints, strong empirical performance
- **Fails at**: Handling parsing errors, generalizing to novel syntactic structures, potential over-constraint for flexible reasoning
- **Contrast with G2**: COGT's causal graphs represent linguistic dependencies vs G2's scene graphs representing visual object relationships
- **Contrast with MCOUT**: COGT uses human-readable graph structures vs MCOUT's opaque latent vectors — more interpretable but potentially less expressive for complex reasoning

---

## Notes

- This paper represents the "causal graphs" sub-category of Q3 structured representations, complementing G2's "scene graphs" and MCOUT's "latent vectors".
- The use of dependency parsing to construct CGMs is an interesting bridge between linguistic theory and deep learning — leverages decades of NLP research on syntactic structure.
- The partially-ordered generation is a key innovation — more flexible than strict sequential generation but more structured than parallel prediction.
- Strong empirical results (outperforming methods with larger datasets) suggest that structural inductive biases are highly valuable for compositional reasoning.
- The FG-OVD benchmark proposed in this paper could be useful for evaluating future compositional VLM methods.
- Should be cited alongside G2 and MCOUT as representative Q3 methods with different structured representation choices.

---

## BibTeX

```bibtex
@inproceedings{parascandolo2025cogt,
  title     = {Causal Graphical Models for Vision-Language Compositional Understanding},
  author    = {Parascandolo, Fiorenzo and Moratelli, Nicholas and Sangineto, Enver and Baraldi, Lorenzo and Cucchiara, Rita},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2025},
  url       = {https://arxiv.org/abs/2412.09353},
  doi       = {10.48550/arXiv.2412.09353}
}
```
