# Paper Note: VisRAG

## Basic Information

**Title**: VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents

**Authors**: Shi Yu, Chaoyue Tang, Bokai Xu, Junbo Cui, Junhao Ran, Yukun Yan, Zhenghao Liu, Shuo Wang, Xu Han, Zhiyuan Liu, Maosong Sun

**Venue**: ICLR 2025 (Conference paper)

**Year**: 2025

**Link**: 
- ArXiv: https://arxiv.org/abs/2410.10594
- Code: https://github.com/openbmb/visrag
- OpenReview: https://openreview.net/forum?id=zG459X3Xge

---

## Abstract Summary

VisRAG introduces a vision-language model (VLM)-based RAG pipeline that directly embeds documents as images for retrieval and generation, eliminating the information loss from traditional text parsing. By preserving layout, images, and visual formatting in multi-modality documents, VisRAG achieves 20-40% end-to-end performance gains over text-based RAG systems. The approach uses a VLM-based retriever (VisRAG-Ret) with dual-encoder architecture and a VLM-based generator (VisRAG-Gen) with page concatenation techniques, demonstrating strong data efficiency and generalization across text-centric and vision-centric documents.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Structured Traces + Tools)

**Justification**: 

VisRAG belongs to Quadrant II for the following reasons:

1. **Structured Representation (Visual Document Embeddings)**: 
   - Document pages are encoded as structured visual embeddings using VLM hidden states with position-weighted mean pooling
   - The embedding space preserves spatial layout, visual formatting, and image content that would be lost in text parsing
   - Unlike pure textual CoT, the representation includes concrete visual features (figure embeddings, layout structure, OCR-free text regions)
   - Retrieval units are page-level images with structured metadata (page boundaries, visual regions)

2. **Tool-Augmented (VLM as Retrieval and Generation Tools)**:
   - VisRAG-Ret: VLM-based retriever functions as a tool that maps queries and document images to embedding space for similarity search
   - VisRAG-Gen: VLM-based generator functions as a tool that processes retrieved document images to produce answers
   - The pipeline uses specialized VLM capabilities (OCR-free document understanding, multi-image reasoning, visual grounding) as tools
   - Tool outputs are concrete: retrieval returns top-k document images with similarity scores; generation produces answers grounded in visual evidence

3. **Key Distinction from Quadrant I**: Unlike CURE (Quadrant I) which uses only textual CoT with internal consistency checks, VisRAG's reasoning includes:
   - Concrete visual tool calls (embed document image, retrieve similar pages, generate from visual input)
   - Structured visual evidence (document page images with layout, figures, tables preserved)
   - Embedding-based retrieval that can be verified via similarity scores and re-execution

4. **Key Distinction from Quadrant III**: While the pipeline uses tools, it's not purely textual reasoning with execution feedback. The VLM processes visual inputs directly, making it fundamentally multimodal rather than text+execution.

5. **Pipeline Structure**: The two-stage pipeline (retrieval → generation) with explicit tool boundaries and structured visual representations aligns with Quadrant II's "Structured Traces + Tools" paradigm.

---

## Key Contributions

1. **Pure-Vision RAG Pipeline**: Proposes the first comprehensive VLM-based RAG system that bypasses text parsing entirely, using document images directly for both retrieval and generation. This eliminates information loss from layout recognition, OCR errors, and text extraction failures in traditional TextRAG pipelines.

2. **Dual VLM Architecture with Multi-Image Handling**: Designs VisRAG-Ret (dual-encoder retriever with position-weighted mean pooling) and VisRAG-Gen (generator with page concatenation and weighted selection techniques) to handle multi-page document reasoning. The architecture supports both single-image and multi-image VLMs through innovative concatenation strategies.

3. **Comprehensive Evaluation with 20-40% Gains**: Demonstrates significant improvements over TextRAG across multiple benchmarks, with 40% relative improvement using MiniCPM-V 2.6 and 20% with GPT-4o. Shows better training data efficiency, strong generalization to unseen document types, and robustness across text-centric and vision-centric documents.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Retrieval is explicitly grounded in document images: each retrieved item is a concrete page image with visual evidence
- Generation is grounded in retrieved visual content: VLM processes actual document images, not parsed text
- Visual grounding preserves layout relationships (e.g., figure-caption proximity, table structure) that text parsing would lose
- Similarity scores provide explicit grounding strength metric for retrieval quality
- Limitation: VLM can still hallucinate visual details (acknowledged in paper's discussion of VLM limitations)
- Compared to TextRAG: Much stronger grounding due to direct visual evidence, no parsing-induced distortion

### Checkability
**Assessment**: Moderate-High
- Retrieval step is checkable: similarity scores between query and document embeddings can be inspected and validated
- Generation step is partially checkable: VLM's visual attention can be analyzed (though paper doesn't include attention visualization)
- Embedding computation is deterministic: given same VLM and pooling method, embeddings are reproducible
- Limitation: Cannot automatically verify if VLM correctly interpreted visual content (e.g., read chart values accurately)
- Limitation: No explicit mechanism to check if retrieved pages are actually relevant (relies on similarity scores)
- Compared to pure text RAG: More checkable due to visual evidence, but VLM interpretation remains partially opaque

### Replayability
**Assessment**: High
- Complete pipeline is reproducible: retrieval (query embedding → ANN search → top-k pages) and generation (VLM inference on retrieved images) are deterministic
- Code and data released at https://github.com/openbmb/visrag
- VLM models are publicly available (MiniCPM-V, Qwen2-VL, GPT-4o)
- Embedding computation uses specified pooling method (position-weighted mean) with fixed VLM weights
- Limitation: Multi-image VLMs may have non-deterministic sampling (not specified in paper)

### Faithfulness Risk
**Assessment**: Moderate
- **Strength**: Visual grounding reduces hallucination risk - VLM must process actual document images, not rely on parametric knowledge
- **Strength**: Retrieval step constrains generation to retrieved evidence, reducing free-form hallucination
- **Risk**: VLM can still misinterpret visual content (e.g., misread chart values, misunderstand figure captions)
- **Risk**: Position-weighted mean pooling may lose fine-grained visual details if important tokens are early in sequence
- **Risk**: Page concatenation for multi-image VLMs may cause attention dilution (too many pages, insufficient focus)
- **Mitigation**: Paper notes VisRAG shows "strong generalization capability" and "robustness," suggesting faithfulness is manageable
- Compared to TextRAG: Lower faithfulness risk (no parsing errors), but VLM visual hallucination remains a concern

### Robustness
**Assessment**: Moderate-High
- **Document Type Robustness**: Tested on both text-centric and vision-centric documents; performs well across both (paper claims robustness)
- **VLM Robustness**: Works with multiple VLM backbones (MiniCPM-V, GPT-4o, Qwen2-VL), allowing flexibility in model selection
- **Strength**: Modular design allows swapping retriever/generator VLMs independently
- **Strength**: No dependency on external parsers (layout recognition, OCR) that can fail catastrophically
- **Limitation**: Performance may degrade with very low-quality document images (blurry scans, handwritten text)
- **Limitation**: Multi-image handling (page concatenation) may struggle with very long documents (10+ pages)
- **Training Data Efficiency**: Paper claims VisRAG is "efficient in utilizing training data," suggesting good data-to-performance ratio

### Cost/Latency
**Assessment**: Moderate-High
- **Retrieval Cost**: VLM embedding computation is more expensive than text encoder (CLIP-style vision encoder + LLM)
- **Generation Cost**: Multi-image VLM inference is significantly more expensive than text-only LLM (processes visual tokens + text tokens)
- **Memory Cost**: Storing document images requires more storage than parsed text (though compression can mitigate)
- **Comparison**: More expensive than TextRAG (single VLM pass vs. parser + text encoder + LLM), but eliminates parser costs
- **Latency**: VLM inference latency depends on image resolution and VLM size; multi-image concatenation increases latency linearly
- **Trade-off**: Higher cost is justified by 20-40% performance gains and elimination of parsing pipeline complexity

### Security
**Assessment**: Low-Moderate Risk
- **No Web Access**: VisRAG operates on local document corpus, no external API calls during inference
- **Prompt Injection**: VLM generation could be vulnerable to adversarial document images (e.g., images with hidden prompts); paper doesn't discuss protection
- **Data Privacy**: Document images may contain sensitive information; VLM processing requires careful data handling
- **Model Dependencies**: Relies on external VLM APIs (e.g., GPT-4o) for generation; potential data privacy concerns with API calls
- **Mitigation**: Open-source VLMs (MiniCPM-V, Qwen2-VL) can be self-hosted to avoid API privacy risks
- **No Explicit Security Measures**: Paper doesn't discuss security considerations for VisRAG deployment

---

## Failure Modes

1. **VLM Visual Hallucination**: Despite visual grounding, VLMs can still hallucinate visual details (e.g., misread chart values, invent text in images). Paper acknowledges VLM hallucination as a general limitation, though VisRAG's grounding reduces risk compared to pure parametric generation.

2. **Retrieval Failure for Visual Queries**: If the query is highly visual (e.g., "find the diagram showing X"), the text query embedding may not align well with document image embeddings, leading to poor retrieval. Dual-encoder training mitigates this, but cross-modal retrieval remains challenging.

3. **Multi-Image Attention Dilution**: When concatenating many pages (e.g., 10+ retrieved documents), the VLM's attention may be spread too thin, missing critical details on individual pages. Paper mentions this as a limitation and proposes weighted selection, but doesn't fully solve the problem.

4. **Low-Quality Document Images**: VisRAG assumes document images are clear and readable. Blurry scans, handwritten text, or heavily compressed images can degrade both retrieval (poor embedding quality) and generation (VLM misinterpretation).

5. **Domain Shift for Specialized Documents**: VisRAG trained on general documents may struggle with highly specialized formats (e.g., scientific papers with complex equations, legal documents with specific layout conventions). Paper shows generalization, but extreme domain shifts remain a risk.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric for end-to-end RAG performance)
- [x] Step Correctness (retrieval accuracy measured via recall metrics)
- [ ] Evidence Attribution (not explicitly measured)
- [x] Trace Replayability (demonstrated via released code and reproducible pipeline)
- [x] Robustness (tested via text-centric vs vision-centric document splits)
- [x] Cost/Latency (discussed qualitatively, not quantified)
- [x] Other: Retrieval metrics (Recall@K, MRR), generation metrics (exact match, F1)

### Benchmarks
- **Custom VQA Datasets**: Constructed from open-source visual question answering datasets
- **Synthetic PDF Queries**: Web-crawled PDFs with synthetic query-document pairs
- **Text-Centric Documents**: Documents where text dominates (e.g., articles, reports)
- **Vision-Centric Documents**: Documents where figures/tables are critical (e.g., scientific papers, manuals)
- **In-Domain vs Out-of-Domain**: Tested generalization to unseen document types and query distributions

### Key Results
- **End-to-End Accuracy**: VisRAG achieves 40% relative improvement over TextRAG with MiniCPM-V 2.6 (37.97% → 53.32%)
- **End-to-End Accuracy**: VisRAG achieves 20% relative improvement over TextRAG with GPT-4o (43.54% → 52.44%)
- **Retrieval Performance**: VisRAG-Ret outperforms state-of-the-art text-centric and vision-centric retrievers
- **Ablation**: VisRAG-Ret outperforms standalone vision encoder or language model under identical training conditions
- **Generation Performance**: VisRAG-Gen surpasses traditional text-based generators with open-source VLMs
- **Multi-Image Reasoning**: Performance increases with more retrieved documents when using multi-image VLMs
- **Data Efficiency**: VisRAG shows better training data efficiency than baseline models
- **Generalization**: Strong performance on out-of-domain documents and query types

---

## Training & Alignment

### Method
- [x] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Dual-stage supervised training** (retriever training with InfoNCE loss, generator training with standard language modeling loss)

### Data Collection
- **Open-Source VQA Datasets**: Used existing visual question answering datasets for training data
- **Synthetic Query-Document Pairs**: Generated synthetic queries from web-crawled PDFs to expand training data
- **Retriever Training**: InfoNCE loss with positive document and hard negative documents (in-batch negatives)
- **Generator Training**: Standard language modeling loss on VQA pairs (query + document images → answer)
- **No RL or Process Labels**: Training is fully supervised, no reinforcement learning or step-by-step process supervision
- **VLM Backbone**: Uses pretrained VLMs (MiniCPM-V, Qwen2-VL, GPT-4o) with fine-tuning on RAG-specific data

---

## Connections to Other Work

### Builds On
- **TextRAG**: Traditional retrieval-augmented generation with text-based retrievers (Guu et al., 2020; Lewis et al., 2020)
- **Dense Retrieval**: Dual-encoder architecture with contrastive learning (Karpukhin et al., 2020)
- **Vision-Language Models**: VLMs for document understanding (MiniCPM-V, Qwen2-VL, LLaVA family)
- **OCR-Free Document Understanding**: DocOwl series, UReader, TextMonkey for direct image-to-text document processing

### Related To
- **Multi-Modal Retrieval**: UniIR (Wei et al., 2023) for universal multi-modal retrieval tasks
- **Vision-Based Retrieval**: DSE (Ma et al., 2024) and ColPali (Faysse et al., 2024) for direct document image encoding
- **Quadrant II Approaches**: VideoAgent (memory-augmented tool use), ChartAgent (tool-integrated chart reasoning)
- **Document Understanding**: VLMs for figure captioning, table understanding, diagram interpretation

### Influenced
- **VisRAG 2.0**: Follow-up work (arXiv:2510.09733) with evidence-guided multi-image reasoning and RS-GRPO training, achieving 27% average accuracy improvement
- **Need to check citations** (paper from ICLR 2025): Potential follow-ups in vision-based RAG, multi-modal document understanding

---

## Quotes & Key Insights

> "Compared to traditional text-based RAG, VisRAG maximizes the retention and utilization of the data information in the original documents, eliminating the information loss introduced during the parsing process."

> "VisRAG is efficient in utilizing training data and demonstrates strong generalization capability, positioning it as a promising solution for RAG on multi-modality documents."

> "In real-world scenarios, knowledge is often presented in multi-modality documents such as textbooks and manuals, which may have texts and figures intersected together."

**Key Insight**: VisRAG demonstrates that **bypassing text parsing entirely** and using VLMs to process document images directly can achieve significant performance gains (20-40%) over traditional TextRAG. The key is preserving visual information (layout, figures, tables) that text parsing inevitably loses.

**Critical Observation**: The comparison between TextRAG and VisRAG (Figure 1) reveals that parsing errors and information loss in TextRAG cascade through retrieval and generation stages. VisRAG's end-to-end visual pipeline avoids this by keeping information in its original visual format throughout.

**Survey-Relevant Point**: VisRAG exemplifies Quadrant II's core strength: **structured visual representations + VLM tools enable verifiable, grounded reasoning**. Unlike Quadrant I (pure text), the visual embeddings preserve spatial and layout information. Unlike Quadrant III (text+execution), the visual processing is native to the VLM, not an external tool.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Structured Traces + Tools)
- [ ] Section 5 (Learning & Alignment)
- [x] Section 6 (Evaluation & Benchmarks) - as example of multi-modal RAG evaluation
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future) - multi-modal document understanding challenges

### Narrative Role

VisRAG serves as a **representative example** of Quadrant II, demonstrating:

1. **Structured Visual Representations**: Unlike free-form CoT (Quadrant I), the document image embeddings provide explicit, structured visual evidence that preserves layout and formatting

2. **VLM as Tool for Retrieval and Generation**: The pipeline uses VLMs as specialized tools for visual document processing, with concrete outputs (embeddings, answers) that can be verified

3. **Trade-offs in Quadrant II Design**:
   - **Pros**: Higher grounding strength (visual evidence), no parsing errors, robustness to document complexity
   - **Cons**: Higher cost (VLM inference), visual hallucination risk, multi-image attention dilution

4. **Contrast with Other Quadrants**:
   - vs Quadrant I (CURE): More verifiable (visual grounding) but more complex (VLM processing)
   - vs Quadrant III (Text + Execution): More native (visual processing) but less interpretable (VLM attention)
   - vs Quadrant IV (Structured + Execution): More flexible (natural language + vision) but less rigorous (no programmatic guarantees)

5. **Multi-Modal Extension of RAG**: VisRAG shows how Quadrant II methods can extend beyond text-only reasoning to multi-modal document understanding

### Comparison Points

**Excels at**:
- Grounding strength (direct visual evidence from document images)
- Replayability (deterministic retrieval and generation pipeline)
- Robustness (works across text-centric and vision-centric documents)
- Data efficiency (strong performance with limited training data)

**Fails at**:
- Full automation of verification (VLM visual interpretation still opaque)
- Cost efficiency (VLM inference more expensive than text encoders)
- Multi-image scalability (attention dilution with many retrieved pages)
- Low-quality image handling (performance degrades with blurry scans)

---

## Notes

### Follow-up Items
- [x] Check VisRAG 2.0 follow-up (arXiv:2510.09733) with RS-GRPO training
- [ ] Review code repository for implementation details (pooling method, concatenation strategy)
- [ ] Check citations for follow-up work on vision-based RAG (paper from ICLR 2025)
- [ ] Compare with other Quadrant II candidates (ChartAgent, VideoAgent) to confirm anchor selection

### Questions
- What is the exact position-weighted mean pooling formula for embedding computation?
- How does page concatenation handle different aspect ratios and resolutions?
- What is the maximum number of retrieved pages that can be effectively concatenated?
- How does VisRAG handle documents with mixed text-image quality (e.g., clear text but blurry figures)?
- What is the training compute budget for VisRAG-Ret and VisRAG-Gen?

### Clarification on Quadrant Placement
The placement in Quadrant II (not III) is because:
- Representation is structured (visual embeddings, document images) but **reasoning is VLM-native** (not external tool execution)
- VLM functions as both retriever and generator, not as external tool to text-based reasoning
- No explicit execution feedback loop like Quadrant III (code execution, calculator)
- Best characterized as "Structured Visual Traces (embeddings, images) + VLM Tools (retrieval, generation)"

---

## BibTeX

```bibtex
@inproceedings{yu2025visrag,
  title={VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents},
  author={Yu, Shi and Tang, Chaoyue and Xu, Bokai and Cui, Junbo and Ran, Junhao and Yan, Yukun and Liu, Zhenghao and Wang, Shuo and Han, Xu and Liu, Zhiyuan and Sun, Maosong},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025},
  url={https://arxiv.org/abs/2410.10594}
}
```

**Status**: ✅ Complete - Quadrant II Paper (Vision-Based RAG)
