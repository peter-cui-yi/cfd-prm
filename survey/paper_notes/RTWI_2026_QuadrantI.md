# Paper Note: RTWI

## Basic Information

**Title:** Reliable Thinking with Images

**Authors:** Haobin Li, Yutong Yang, Yijie Lin, Xiang Dai, Mouxing Yang, Xi Peng

**Venue:** arXiv preprint

**Year:** 2026

**Link:**
- arXiv: https://arxiv.org/abs/2602.12916
- Date: February 13, 2026

---

## Abstract Summary

RTWI addresses the Noisy Thinking problem in Thinking-with-Images (TWI): imperfect visual cues and reasoning steps lead to error accumulation, degrading final answers. RTWI proposes a text-centric approach to estimate the reliability of visual cues and chain-of-thought reasoning. It uses robust filtering and voting to prevent noise from contaminating the final answer, improving verifiability without external tools.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (CoT reasoning with visual cues; reliability estimation is text-centric, operating on the model's internal representations)
- [ ] Structured Trace (reliability scores and filtering/voting are applied to text reasoning, not programs or formal structures)

### Verification Channel
- [x] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant:** I (Text-Centric Reliability Estimation — No External Tools)

**Justification:**

1. **Text-Centric Reliability Estimation**: RTWI estimates the reliability of visual cues and CoT steps using a purely text-centric approach—no external tools, detectors, or execution. The model (or an auxiliary model) evaluates cue and step quality from the reasoning trace itself.

2. **Robust Filtering and Voting**: Filtering removes low-reliability cues/steps; voting aggregates over multiple reasoning paths to reduce noise. Both operations are internal—no tool calls, no code execution, no external verifiers.

3. **Addresses Noisy Thinking**: TWI suffers when visual cues are wrong or reasoning steps are flawed—errors compound. RTWI mitigates this by estimating reliability and filtering/voting, improving verifiability through internal mechanisms.

4. **No External Verification**: All reliability estimation, filtering, and voting occur within the model ecosystem. The approach is fully Q1—textual reasoning with internal quality control.

---

## Key Contributions

1. **Noisy Thinking Formulation**: Identifies and formalizes the Noisy Thinking problem in Thinking-with-Images—imperfect visual cues and reasoning steps cause error accumulation. Provides a clear failure mode for TWI systems.

2. **Text-Centric Reliability Estimation**: Proposes a method to estimate the reliability of visual cues and CoT steps without external tools. The model learns to assess its own (or a candidate's) reasoning quality from the trace alone.

3. **Robust Filtering and Voting**: Uses filtering to remove low-reliability components and voting to aggregate over multiple reasoning paths. This prevents noise from contaminating the final answer and improves verifiability.

---

## Verifiability Analysis

### Grounding Strength
**Assessment:** Medium-High

Reliability estimation encourages the model to downweight or filter unreliable visual cues and reasoning steps. This implicitly strengthens grounding—low-reliability cues (likely wrong) are filtered, reducing "explain without seeing" risk. However, reliability is estimated internally; there is no external ground truth for cue correctness.

### Checkability
**Assessment:** Medium

Answer correctness is checkable. Reliability scores can be inspected—high vs. low reliability steps are identifiable. However, there is no automatic validator for whether reliability estimates are correct; the reliability estimator itself may have blind spots.

### Replayability
**Assessment:** Medium-High

Reasoning traces with reliability scores, filtering decisions, and voting outcomes can be logged. Given fixed model and input, outputs are reproducible with deterministic decoding. The filtering/voting process provides an auditable trail.

### Faithfulness Risk
**Assessment:** Medium (reduced vs. standard TWI)

Filtering and voting reduce faithfulness risk by removing low-reliability steps and aggregating over multiple paths. The model is less likely to commit to a single erroneous chain. However, if the reliability estimator is biased, it may filter correct steps or retain wrong ones.

### Robustness
**Assessment:** Medium-High

Filtering and voting are designed for robustness to noise. Multiple reasoning paths and aggregation reduce sensitivity to individual errors. Performance under distribution shift depends on reliability estimator generalization.

### Cost/Latency
**Assessment:** Medium

Filtering and voting add computation—reliability estimation for each step/cue, multiple reasoning paths for voting. Latency increases with the number of paths and the complexity of reliability estimation. No external tool calls.

### Security
**Assessment:** Low Risk

No external tool calls. Standard VLM risks apply. Reliability estimation could be gamed if adversarial inputs fool the estimator into trusting wrong steps.

---

## Failure Modes

1. **Reliability Estimator Errors**: The text-centric reliability estimator may misclassify—assigning high reliability to wrong steps or low reliability to correct ones. If the estimator shares biases with the reasoning model, it may fail to catch systematic errors.

2. **Over-Filtering**: Aggressive filtering may remove correct but low-confidence steps, degrading performance. The threshold for "reliable enough" is critical and may not generalize across tasks.

3. **Voting Collapse**: If multiple reasoning paths are correlated (e.g., same wrong cue), voting may reinforce the error rather than correct it. Diversity of paths is essential.

4. **Noisy Cue Propagation**: If the reliability estimator fails to identify a bad visual cue early, it may propagate through the chain. Late-stage filtering may be insufficient to recover.

5. **Task-Dependent Reliability**: Reliability estimation may be calibrated for certain task types. On out-of-distribution tasks (e.g., fine-grained perception, document understanding), reliability scores may be unreliable.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (with/without RTWI)
- [ ] Step Correctness
- [ ] Evidence Attribution
- [x] Trace Replayability (filtering/voting trace)
- [x] Robustness (noise robustness)
- [ ] Cost/Latency
- [ ] Other

### Benchmarks
- Thinking-with-Images benchmarks
- Noisy thinking / error accumulation evaluation
- Comparison: baseline TWI without reliability estimation

### Key Results
- RTWI reduces error accumulation from noisy visual cues and reasoning
- Filtering and voting improve final answer accuracy
- Text-centric approach achieves gains without external tools

---

## Training & Alignment

### Method
- [x] SFT with Rationale (if reliability estimator is trained)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Reliability estimation, filtering, voting**

### Data Collection
- Training data for reliability estimator (if learned)
- TWI reasoning traces with ground truth reliability (if supervised)
- Possibly self-generated or human-annotated traces with correctness labels

---

## Connections to Other Work

### Builds On
- Thinking-with-Images (TWI)
- Chain-of-Thought, Multimodal-CoT
- Self-consistency, voting over multiple paths
- Process reward models (reliability as step-level quality)

### Related To
- GThinker (cue-guided rethinking, consistency)
- VRPRM, VisualPRM (step-level evaluation)
- PatchCue (visual cue quality)

### Influenced
- Noisy thinking mitigation in VLMs
- Text-centric reliability estimation
- Filtering and voting for multimodal reasoning

---

## Quotes & Key Insights

> "RTWI addresses the Noisy Thinking problem in Thinking-with-Images through text-centric reliability estimation and robust filtering and voting."

**Key Insight:** Noisy Thinking is a fundamental failure mode—visual cues and reasoning steps are imperfect, and errors compound. RTWI shows that internal reliability estimation (no tools) combined with filtering and voting can mitigate this, improving verifiability within the Q1 paradigm.

---

## Survey Placement

### Section Placement
- [x] Section 4.1 (Methods by Quadrant — Quadrant I: Reliability Estimation, Filtering, Voting)
- [x] Section 5 (Learning & Alignment — reliability estimation training if applicable)
- [x] Section 6 (Evaluation & Benchmarks — noisy thinking, robustness)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges — reliability estimator errors, over-filtering)

### Narrative Role
RTWI represents **Q1 noise mitigation**—addressing Noisy Thinking through text-centric reliability estimation and filtering/voting, without external tools. It demonstrates that verifiability can be improved by internal quality control over reasoning traces.

### Comparison Points
**Excels at:** Noisy thinking mitigation, verifiability through filtering/voting, no external tools
**Fails at:** Reliability estimator accuracy, over-filtering risk, voting diversity requirements

---

## Notes

RTWI's text-centric approach is a key design choice—it keeps the method in Q1 while addressing a real failure mode. The relationship between reliability estimation and process reward models (PRMs) is worth exploring—both evaluate step quality, but RTWI focuses on filtering/voting rather than RL.

---

## BibTeX

```bibtex
@article{li2026rtwi,
  title={Reliable Thinking with Images},
  author={Li, Haobin and Yang, Yutong and Lin, Yijie and Dai, Xiang and Yang, Mouxing and Peng, Xi},
  journal={arXiv preprint arXiv:2602.12916},
  year={2026},
  url={https://arxiv.org/abs/2602.12916}
}
```

**Status:** ✅ Complete — Quadrant I Paper (Text-Centric Reliability Estimation for TWI)
