# Paper Note: CoVT

## Basic Information

**Title**: Chain-of-Visual-Thought: Teaching VLMs to See and Think Better with Continuous Visual Tokens

**Authors**: Yiming Qin, Bomin Wei, Jiaxin Ge, Konstantinos Kallidromitis, Stephanie Fu, Trevor Darrell, XuDong Wang

**Venue**: arXiv (preprint)

**Year**: 2025 (submitted Nov 24, 2025)

**arXiv**: https://arxiv.org/abs/2511.19418

---

## Abstract Summary

CoVT introduces a reasoning framework where VLMs think not only in words but also through **continuous visual tokens** — compact latent representations (~20 tokens) that encode rich perceptual cues (2D appearance, 3D geometry, spatial layout, edge structure). During training, the VLM learns to autoregressively predict these visual tokens to reconstruct dense supervision signals (depth, segmentation, edges, DINO features) from lightweight vision experts. At inference, the model reasons directly in continuous visual token space without calling any external tools, improving performance by 3–16% across diverse perception benchmarks.

---

## Methodology Analysis

### Representation Type
- [x] **Structured Trace** — continuous visual tokens (compact latent embeddings encoding perceptual features like depth, segmentation, edge structure). These are interleaved with text tokens in the reasoning chain.

### Verification Channel
- [x] **No Tools / No Execution** — at inference time, no external models or tools are called. Vision experts (depth estimators, segmentation models) are used **only at training time** for knowledge distillation, not at inference.

### 2×2 Matrix Placement
**Quadrant**: **III (Structured w/o Tools)**

**Justification**:
- **Structured**: Intermediate visual tokens are compact continuous vectors that encode specific perceptual dimensions (depth, segmentation, spatial layout). This is a structured multi-dimensional representation, not free-form text.
- **No Tools**: At inference time, all reasoning is internal to the VLM. The visual tokens are generated within the model's forward pass — no external detector, depth estimator, or segmentation model is queried.

**Important clarification on training vs. inference**: Vision experts (depth, segmentation, DINO) are used at training time to provide supervision signals, but after training, the model has internalized these perceptual capabilities into its visual token space. This is analogous to using labeled data for training — the labeling tool is not part of inference.

---

## Key Contributions

1. **Visual token chain-of-thought**: Proposes a new type of intermediate reasoning step — continuous visual tokens that encode dense perceptual knowledge, interleaved with standard text tokens in the reasoning chain.
2. **Multi-cue perceptual encoding**: A single set of ~20 visual tokens encodes complementary perceptual signals: 2D appearance (DINO features), 3D geometry (depth), spatial layout (segmentation), and edge structure — enabling richer visual grounding than text alone.
3. **Efficient distillation**: Lightweight vision experts distill perceptual knowledge into the VLM's visual token space without catastrophic forgetting of existing capabilities.
4. **Plug-in compatibility**: Integrates into existing VLMs (Qwen2.5-VL, LLaVA) as an additional reasoning head, with optional decoding of visual tokens back to dense predictions for interpretability.
5. **Broad perception gains**: Consistent 3–16% improvement across CV-Bench, MMVP, RealWorldQA, MMStar, WorldMedQA, HRBench.

---

## Verifiability Analysis

| Dimension | Rating | Reasoning |
|-----------|--------|-----------|
| **Grounding** | **Medium-High** | Visual tokens are explicitly trained to encode spatially grounded perceptual cues (depth, segmentation) from the actual input image. Grounding is more direct than pure text CoT. |
| **Checkability** | **Medium** | Visual tokens can be optionally decoded to dense predictions (depth maps, segmentation masks), making intermediate states partially inspectable. However, tokens are not natively human-readable. |
| **Replayability** | **High** | Given same model + same input, same visual tokens are produced (deterministic). Decoded dense predictions are directly comparable across runs. |
| **Faithfulness Risk** | **Medium** | Visual tokens are trained to encode specific perceptual signals, reducing the risk of arbitrary hallucination. However, the token space may not capture complex relational reasoning or abstract concepts. |

**Q3 vs Q1 distinction**: Q1 text CoT says "the object is in the top-left quadrant." CoVT produces a spatial layout embedding that encodes actual spatial configuration as continuous vectors. The latter is more grounded (tied to image features via training supervision) and more checkable (decodable to spatial map).

**Q3 vs Q4 distinction**: Q4 would call an external segmentation API at inference time and use its output to verify reasoning (e.g., VisProg). CoVT has internalized segmentation and depth estimation into its weight space — it generates equivalent structured tokens internally, without external API calls.

---

## Failure Modes

1. **Perceptual tunnel vision**: The fixed set of perceptual cues (depth, segmentation, edges, DINO) may miss task-critical features not in the training supervision (e.g., text recognition, fine-grained attribute differences).
2. **~20 token budget**: Compressing rich spatial information into ~20 tokens may lose detail for complex scenes with many objects.
3. **Training distribution gap**: If test images differ significantly from training distribution, visual tokens may not encode the right perceptual signals.
4. **Interpretability ceiling**: Even with decoding, visual tokens are intermediate-dimensional — less interpretable than explicit scene graphs or symbolic programs.

---

## Benchmark Results

| Benchmark | Task | Improvement |
|-----------|------|-------------|
| CV-Bench | Spatial reasoning | +3–16% |
| MMVP | Visual perception | Consistent gains |
| RealWorldQA | Real-world QA | Consistent gains |
| MMStar | Multimodal star | Consistent gains |
| WorldMedQA | Medical QA | Consistent gains |
| HRBench | High-resolution | Consistent gains |

---

## Training & Alignment

**Training**: Two-stage — (1) train VLM to predict dense supervision signals (depth, segmentation, DINO) using lightweight vision expert outputs, then (2) fine-tune with CoVT interleaving visual and text tokens in the reasoning chain.

**Distillation**: Knowledge from vision experts is compressed into the VLM's visual token space. This is a form of process supervision where the intermediate "visual thought" is supervised by grounded perceptual labels.

---

## Connections

**Builds on**: Coconut (continuous thought concept), MCOUT (multimodal latent reasoning)

**Key differentiator vs. MCOUT**: CoVT's visual tokens encode *specific named perceptual dimensions* (depth, segmentation, edges) — more structured and interpretable than MCOUT's general hidden state vectors. CoVT visual tokens are a *typed* structured representation.

**Related**: DMLR (also uses visual patches dynamically), LaRe (also latent space reasoning)

---

## BibTeX

```bibtex
@article{qin2025covt,
  title     = {Chain-of-Visual-Thought: Teaching VLMs to See and Think Better with Continuous Visual Tokens},
  author    = {Qin, Yiming and Wei, Bomin and Ge, Jiaxin and Kallidromitis, Konstantinos and Fu, Stephanie and Darrell, Trevor and Wang, XuDong},
  journal   = {arXiv preprint arXiv:2511.19418},
  year      = {2025},
  url       = {https://arxiv.org/abs/2511.19418}
}
```

---

## Notes

- CoVT is the most **interpretable among latent Q3 methods** because its visual tokens encode named perceptual dimensions decodable to spatial maps.
- The training–inference distinction is critical: vision experts are *training-time* oracles, not *inference-time* tools. This cleanly places CoVT in Q3.
- Potential bridge paper: CoVT could be seen as a step toward Q4 if the decoded dense predictions were used as verification feedback. Currently they are only for interpretability, not correctness checking.
- Authors include Trevor Darrell — same group as CCoT (Mitra et al.), suggesting a Berkeley line of structured reasoning research.
