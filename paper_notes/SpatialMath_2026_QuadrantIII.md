# Paper Note: SpatialMath

## Basic Information

**Title:** SpatialMath: Spatial Comprehension-Infused Symbolic Reasoning for Mathematical Problem-Solving

**Authors:** Ashutosh Bajpai, Akshat Bhandari, Akshay Nambi, Tanmoy Chakraborty

**Venue:** arXiv preprint

**Year:** 2026

**Link:**
- arXiv: https://arxiv.org/abs/2601.17489
- Date: January 2026

---

## Abstract Summary

SpatialMath addresses MSLMs' limitations in visual comprehension and mathematical reasoning for geometric problems. It proposes a Spatial Comprehension-Infused Symbolic Reasoning Framework that integrates spatially-grounded representations from visual diagrams into structured symbolic reasoning chains. A specialized perception module extracts geometric structures and spatial relationships; these are infused into symbolic reasoning chains for visual comprehension-aware reasoning. MATHVERSE-PLUS is introduced—a dataset with structured visual interpretations and step-by-step reasoning for vision-intensive math problems. SpatialMath achieves up to 10 percentage points improvement over supervised fine-tuning with data augmentation in vision-intensive settings.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT)
- [x] Structured Trace (spatially-grounded representations, symbolic reasoning chains, structured visual interpretations)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** III (Structured Trace, No Tools)

**Justification:**

1. **Structured Symbolic Reasoning**: SpatialMath uses "structured symbolic reasoning chains" with "spatially-grounded representations." The perception module extracts geometric structures and spatial relationships—structured representations, not free-form text. These are infused into reasoning chains in a methodical way.

2. **No External Tool Invocation**: The perception module is part of the model (or a learned component)—not an external detector or geometry solver. All reasoning occurs within the MSLM. No code execution, theorem provers, or grounding APIs.

3. **Q3 vs. Q1**: SpatialMath's intermediate states are structured (geometric structures, spatial relations, symbolic chains)—distinct from free-form textual CoT. The "perception-to-reasoning pipeline" is a structured pipeline.

4. **Q3 vs. Q4**: No execution of programs or external tools. Symbolic reasoning is internal to the model—not executed by a formal system (e.g., geometry theorem prover).

---

## Key Contributions

1. **Spatial Comprehension-Infused Symbolic Reasoning**: Integrates spatially-grounded representations from visual diagrams into structured symbolic reasoning chains. A specialized perception module extracts geometric structures and spatial relationships; these are methodically infused to facilitate visual comprehension-aware reasoning.

2. **MATHVERSE-PLUS Dataset**: Novel dataset with structured visual interpretations and step-by-step reasoning paths for vision-intensive mathematical problems. Supports training and evaluation of perception-to-reasoning pipelines.

3. **10 Percentage Point Improvement**: SpatialMath achieves up to 10 percentage points improvement over supervised fine-tuning with data augmentation in vision-intensive settings. Robustness analysis shows that enhanced spatial representations directly improve reasoning accuracy.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** High

Spatially-grounded representations are extracted from visual diagrams—explicit grounding in geometric structure. Each reasoning step can be traced to specific spatial/geometric elements. The perception module provides structured evidence.

### Checkability
**Assessment:** Medium-High

Geometric structures and spatial relations can be checked for consistency with the diagram. Symbolic reasoning steps can be validated against mathematical correctness. MATHVERSE-PLUS provides ground truth for evaluation.

### Replayability
**Assessment:** High

The perception-to-reasoning pipeline is deterministic (given fixed model and input). Structured representations and reasoning chains are serializable. Full trace can be logged and replayed.

### Faithfulness Risk
**Assessment:** Medium (reduced vs. Q1)

Structured perception constrains hallucination—the model must reason from extracted geometric structure. However, perception errors (wrong angle, wrong relation) can propagate to wrong conclusions. No external verifier.

### Robustness
**Assessment:** Medium-High

Robustness analysis confirms that enhanced spatial representations improve reasoning accuracy. Performance on vision-intensive problems is the focus. Sensitivity to diagram quality, occlusion, or distribution shift is uncertain.

### Cost/Latency
**Assessment:** Medium

Perception module adds compute. Structured reasoning may require multiple stages. Trade-off: higher cost for better geometric reasoning.

### Security
**Assessment:** Low Risk

No external tool calls. Standard MSLM risks. Adversarial diagrams could potentially mislead the perception module.

---

## Failure Modes

1. **Perception Module Errors**: The specialized perception module may mis-extract geometric structures or spatial relationships—e.g., wrong angle values, incorrect parallel/perpendicular relations—leading to erroneous symbolic reasoning.

2. **Symbolic Reasoning Propagation**: Errors in spatial representation propagate through symbolic chains. A single mis-extracted relation can invalidate the entire solution.

3. **Vision-Intensive Focus**: Optimized for vision-intensive geometric problems. Performance on text-heavy math or non-geometric math may not improve—or may degrade if the pipeline adds overhead.

4. **MATHVERSE-PLUS Coverage**: Dataset scope may not cover all geometric problem types. Models may overfit to MATHVERSE-PLUS distribution.

5. **Diagram Quality Sensitivity**: Hand-drawn diagrams, low resolution, or unusual notation may challenge the perception module.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (vision-intensive math)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Robustness (spatial representation ablation)
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- MATHVERSE-PLUS (vision-intensive math)
- Comparison: supervised fine-tuning with data augmentation

### Key Results
- Up to 10 percentage points improvement in vision-intensive settings
- Robustness analysis: enhanced spatial representations directly improve reasoning accuracy
- Validates structured perception-to-reasoning pipeline for MSLMs

---

## Training & Alignment

### Method
- [x] SFT with Rationale (MATHVERSE-PLUS, structured reasoning)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other: Perception module training, symbolic chain infusion

### Data Collection
- MATHVERSE-PLUS: structured visual interpretations, step-by-step reasoning for vision-intensive math
- Perception module training data

---

## Connections to Other Work

### Builds On
- MATHVERSE, geometry problem solving
- Multimodal math reasoning (MathVista, GeoQA)
- Perception-to-reasoning pipelines

### Related To
- SpatialMath focuses on geometric/spatial math
- GThinker (cue-guided rethinking for general multimodal reasoning)
- Chain-of-Table (structured reasoning for tables)

### Influenced
- Future work on spatial comprehension for math
- MATHVERSE-PLUS as benchmark for vision-intensive math

---

## Quotes & Key Insights

> "SpatialMath employs a specialized perception module to extract spatially-grounded representations from visual diagrams, capturing critical geometric structures and spatial relationships."

> "Robustness analysis reveals that enhanced spatial representations directly improve reasoning accuracy, reinforcing the need for structured perception-to-reasoning pipelines in MSLMs."

**Key Insight:** **Structured perception as prerequisite for geometric reasoning**—MSLMs struggle to connect perception with structured reasoning. SpatialMath demonstrates that explicit extraction of geometric structure (angles, relations) and infusion into symbolic chains is necessary for vision-intensive math, supporting the Q3 design space.

---

## Survey Placement

### Section Placement
- [x] Section 4.3 (Methods by Quadrant — Quadrant III: Structured Symbolic Reasoning for Math)
- [x] Section 5 (Learning & Alignment — perception module, SFT)
- [x] Section 6 (Evaluation & Benchmarks — MATHVERSE-PLUS)
- [ ] Section 7 (Applications — math education, geometry)
- [x] Section 8 (Challenges — perception errors, propagation)

### Narrative Role
SpatialMath exemplifies **Q3 structured reasoning for domain-specific tasks** (geometric math). It demonstrates that perception-to-reasoning pipelines with structured intermediate representations are necessary for vision-intensive math—a domain where Q1 text-only reasoning is insufficient.

### Comparison Points
**Excels at:** Geometric reasoning, spatial grounding, MATHVERSE-PLUS, 10pt improvement
**Fails at:** External verification of geometric correctness, robustness to diagram quality

---

## Notes

SpatialMath's focus on geometric/spatial math is a natural fit for structured representations—geometry has formal structure (angles, relations) that can be explicitly extracted and reasoned over.

---

## BibTeX

```bibtex
@article{bajpai2026spatialmath,
  title={{SpatialMath}: Spatial Comprehension-Infused Symbolic Reasoning for Mathematical Problem-Solving},
  author={Bajpai, Ashutosh and Bhandari, Akshat and Nambi, Akshay and Chakraborty, Tanmoy},
  journal={arXiv preprint arXiv:2601.17489},
  year={2026},
  url={https://arxiv.org/abs/2601.17489}
}
```

**Status:** ✅ Complete — Quadrant III Paper (Spatial Comprehension for Math)
