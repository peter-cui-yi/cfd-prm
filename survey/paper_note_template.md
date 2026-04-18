# Paper Note Template

## Basic Information

**Title**: [Paper Title]

**Authors**: [Author List]

**Venue**: [Conference/Journal/arXiv]

**Year**: [Publication Year]

**Link**: [PDF/Code URL]

---

## Abstract Summary

[2-3 sentences summarizing the core contribution]

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: [I / II / III / IV]

**Justification**: [Why this placement?]

---

## Key Contributions

1. [Contribution 1]
2. [Contribution 2]
3. [Contribution 3]

---

## Verifiability Analysis

### Grounding Strength
[Does reasoning point to image evidence? regions/masks/objects?]

### Checkability
[Can intermediate steps be automatically validated?]

### Replayability
[Can we re-run the trace to reproduce results?]

### Faithfulness Risk
[Can the model "explain without seeing"?]

### Robustness
[Sensitivity to tool errors, missing evidence, distribution shifts]

### Cost/Latency
[Tool budget, number of steps, runtime constraints]

### Security
[Prompt injection, data contamination, unsafe tool calls]

---

## Failure Modes

1. [Failure mode 1]
2. [Failure mode 2]
3. [Failure mode 3]

---

## Evaluation

### Metrics Used
- [ ] Answer Accuracy
- [ ] Step Correctness
- [ ] Evidence Attribution
- [ ] Trace Replayability
- [ ] Robustness
- [ ] Cost/Latency
- [ ] Other: [specify]

### Benchmarks
[List datasets/benchmarks used]

### Key Results
[Summarize main experimental findings]

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [ ] Other: [specify]

### Data Collection
[How was training data collected?]

---

## Connections to Other Work

### Builds On
[Papers/paradigms this work extends]

### Related To
[Contemporary or parallel work]

### Influenced
[Later work building on this]

---

## Quotes & Key Insights

> [Important quote from paper]

[Key insight not captured elsewhere]

---

## Survey Placement

### Section Placement
- [ ] Section 4.X (Methods by Quadrant)
- [ ] Section 5 (Learning & Alignment)
- [ ] Section 6 (Evaluation & Benchmarks)
- [ ] Section 7 (Applications)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
[How does this paper support the survey's main argument?]

### Comparison Points
[Which evaluation checklist dimensions does this paper excel/fail at?]

---

## Notes

[Any additional observations, questions, or follow-up items]

---

## BibTeX

```bibtex
[Full BibTeX entry]
```
