# Paper Note: VRPRM

## Basic Information

**Title:** VRPRM: Process Reward Modeling via Visual Reasoning

**Authors:** Xinquan Chen, Bangwei Liu, Xuhong Wang, Yingchun Wang, Chaochao Lu

**Venue:** arXiv preprint

**Year:** 2025

**Link:**
- arXiv: https://arxiv.org/abs/2508.03556
- Date: August 2025

---

## Abstract Summary

VRPRM extends Process Reward Models (PRMs) to multimodal reasoning by introducing visual reasoning capability into PRM training. It addresses the limitations of existing PRMs (lack of long-term reasoning, expensive CoT-PRM annotation) with an efficient two-stage training strategy: 3.6K CoT-PRM SFT data and 50K non-CoT PRM RL training data. VRPRM surpasses a non-thinking PRM trained on 400K data and achieves up to 118% relative performance improvement over the base model in Best-of-N experiments, demonstrating higher quality reasoning at lower annotation cost.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (CoT reasoning steps evaluated by the PRM; steps are free-form text)
- [ ] Structured Trace (PRM evaluates text steps, not programs or formal structures)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** I (Visual Process Reward Model — Step-Level Verification)

**Justification:**

1. **PRM Evaluates Text CoT Steps**: VRPRM is a Process Reward Model that scores individual reasoning steps in multimodal CoT traces. The PRM takes image + question + reasoning steps as input and outputs step-level correctness/reward signals. The PRM is a learned model, not an external tool.

2. **No External Tool Calls**: Neither the reasoning model (generating CoT) nor VRPRM (evaluating steps) invokes external APIs, code interpreters, object detectors, or grounding tools. Both are end-to-end learned models processing image and text.

3. **Best-of-N Is Inference-Time Scaling**: BoN generates N candidate CoT chains and selects the highest-scoring one according to VRPRM. This is analogous to beam search with a learned scorer—entirely internal to the model ecosystem.

4. **Process Supervision for Multimodal Reasoning**: VRPRM extends the PRM paradigm (Math-Shepherd, OmegaPRM, VisualPRM) to visual reasoning with a data-efficient training strategy. It exemplifies Q1 process supervision—step-level evaluation without tools.

---

## Key Contributions

1. **VRPRM: Data-Efficient Visual Process Reward Model**: Achieves superior reasoning quality with only 3.6K CoT-PRM SFT data and 50K non-CoT PRM RL data, surpassing a non-thinking PRM trained on 400K data. Demonstrates that introducing CoT capability into PRM training enables higher quality at lower annotation cost.

2. **Two-Stage Training Strategy**: (1) SFT on 3.6K CoT-PRM examples to instill step-level evaluation with visual reasoning; (2) RL on 50K non-CoT PRM data to scale up without expensive CoT annotation. The combination achieves stable performance across tasks.

3. **118% Relative Improvement in BoN**: VRPRM achieves up to 118% relative performance improvement over the base model in Best-of-N experiments, validating the combined training strategy as a new paradigm for PRM training with efficient data utilization.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Medium-High

VRPRM provides step-level correctness/reward signals—stronger than answer-level verification. The PRM is trained to evaluate reasoning steps in the context of the image, providing implicit visual grounding. However, the PRM's judgments are learned, not verified by external tools.

### Checkability
**Assessment:** Medium-High

Step-level PRM scores are automatically generated for any candidate CoT. This enables systematic quality assessment without human review. The 3.6K CoT-PRM data provides supervision for step-level evaluation. Limitations: PRM accuracy is not 100%; false positives/negatives possible.

### Replayability
**Assessment:** Medium-High

BoN + VRPRM produces an auditable trace: N candidate chains + step-level scores. The selection process is deterministic given fixed N, model weights, and scoring function. More replayable than self-consistency (which obscures reasoning paths).

### Faithfulness Risk
**Assessment:** Medium (reduced vs. outcome-only)

Step-level PRM scoring identifies erroneous steps; BoN selection prefers chains with consistently correct steps. This reduces faithfulness risk compared to outcome-only reward models. However, the PRM itself may have blind spots (PRM hallucination).

### Robustness
**Assessment:** Medium

Trained on limited data (3.6K + 50K); generalization to unseen domains (e.g., medical imaging, fine-grained recognition) is uncertain. The two-stage strategy may be sensitive to the quality of the 3.6K CoT-PRM seed data.

### Cost/Latency
**Assessment:** High (inference), Low (training data)

**Training**: 3.6K + 50K is far less than VisualPRM's 400K—significant data efficiency. **Inference**: BoN requires N × (generation + PRM scoring), similar to VisualPRM. Cost scales with N.

### Security
**Assessment:** Low-Medium Risk

No external tool calls. PRM scores could be gamed by adversarial CoT formatting. The non-CoT RL data may not penalize superficial step decompositions.

---

## Failure Modes

1. **PRM Hallucination**: VRPRM may assign high scores to plausible-but-wrong steps—the same faithfulness problem that afflicts the generator. If the PRM and generator share architectural biases, they may share blind spots.

2. **3.6K CoT-PRM Seed Quality**: The small CoT-PRM dataset is critical for cold start. Noisy or biased annotations could propagate to the PRM and limit BoN quality. Domain coverage may be limited.

3. **Non-CoT RL Data Mismatch**: The 50K non-CoT PRM data may not fully align with CoT evaluation—the PRM may learn to score non-CoT traces well but struggle with CoT-specific step structure.

4. **BoN Inference Cost**: N-sample generation + PRM scoring remains expensive. For real-time applications, VRPRM may be impractical despite training efficiency.

5. **Domain Generalization**: Performance on tasks outside the training distribution (e.g., chart reasoning, OCR, spatial navigation) is unknown. The 118% improvement is reported on specific benchmarks.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (BoN evaluation)
- [x] Step Correctness (implicit via PRM)
- [ ] Evidence Attribution
- [x] Trace Replayability (BoN audit trail)
- [ ] Robustness
- [x] Cost/Latency (training data efficiency)
- [ ] Other

### Benchmarks
- Multimodal reasoning benchmarks (specific benchmarks from paper)
- Comparison: non-thinking PRM (400K), base model

### Key Results
- Surpasses non-thinking PRM trained on 400K data
- Up to 118% relative improvement over base model in BoN
- 3.6K CoT-PRM + 50K non-CoT RL achieves higher quality than 400K non-thinking data

---

## Training & Alignment

### Method
- [x] SFT with Rationale (3.6K CoT-PRM SFT)
- [x] Process Supervision (step-level evaluation)
- [x] PRM (Process Reward Model — central contribution)
- [x] RL / DPO (50K non-CoT PRM RL)
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other

### Data Collection
- **3.6K CoT-PRM SFT**: CoT reasoning traces with step-level correctness labels
- **50K non-CoT PRM RL**: Non-CoT reasoning traces for RL training (outcome or process rewards)
- Combined strategy avoids expensive full CoT annotation at scale

---

## Connections to Other Work

### Builds On
- Math-Shepherd, OmegaPRM (text PRMs)
- VisualPRM (multimodal PRM, 400K data)
- Let's Verify Step by Step (Lightman et al.)

### Related To
- VisualPRM (parallel work on multimodal PRM; VRPRM achieves similar goals with far less data)
- VRPRM emphasizes data efficiency

### Influenced
- Future work on data-efficient PRM training
- Combined CoT + non-CoT PRM training paradigms

---

## Quotes & Key Insights

> "Using only 3.6K CoT-PRM SFT data and 50K non-CoT PRM RL training data, VRPRM can surpass the non-thinking PRM with a total data volume of 400K."

> "This result confirms that the proposed combined training strategy can achieve higher quality reasoning capabilities at a lower data annotation cost."

**Key Insight:** **Data efficiency in PRM training**—VRPRM demonstrates that a small CoT-PRM seed (3.6K) combined with scalable non-CoT RL (50K) can outperform large-scale non-thinking PRMs. This reduces the barrier to deploying process supervision for multimodal reasoning.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant — Quadrant I: Process supervision, data-efficient PRM)
- [x] Section 5 (Learning & Alignment — two-stage PRM training)
- [x] Section 6 (Evaluation & Benchmarks — BoN, data efficiency)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — PRM hallucination, seed data quality)

### Narrative Role
VRPRM represents **Q1 process supervision with data efficiency**—achieving VisualPRM-level gains with ~10× less CoT annotation. It positions process supervision as more accessible and provides a new paradigm for PRM training that balances quality and cost.

### Comparison Points
**Excels at:** Data efficiency, BoN performance, two-stage training paradigm
**Fails at:** PRM hallucination, BoN inference cost, domain generalization

---

## Notes

VRPRM's 3.6K + 50K strategy is a significant practical advance—reducing the annotation burden for multimodal PRMs. The trade-off between CoT-PRM quality (small seed) and non-CoT RL scale warrants further study.

---

## BibTeX

```bibtex
@article{chen2025vrprm,
  title={{VRPRM}: Process Reward Modeling via Visual Reasoning},
  author={Chen, Xinquan and Liu, Bangwei and Wang, Xuhong and Wang, Yingchun and Lu, Chaochao},
  journal={arXiv preprint arXiv:2508.03556},
  year={2025},
  url={https://arxiv.org/abs/2508.03556}
}
```

**Status:** ✅ Complete — Quadrant I Paper (Visual Process Reward Model)
