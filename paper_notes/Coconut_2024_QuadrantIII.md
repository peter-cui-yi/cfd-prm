# Paper Note: Coconut (Chain of Continuous Thought)

## Basic Information

**Title**: Training Large Language Models to Reason in a Continuous Latent Space

**Authors**: Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li, Zhiting Hu, Jason Weston, Yuandong Tian

**Affiliations**: Meta AI Research; UC San Diego

**Venue**: arXiv 2024 (December 2024)

**Year**: 2024

**Link**:
- ArXiv: https://arxiv.org/abs/2412.06769

---

## Abstract Summary

Coconut (Chain of Continuous Thought) introduces a new reasoning paradigm where LLMs reason in a continuous latent space rather than in discrete language tokens. Instead of decoding intermediate reasoning steps into words, the model uses its last hidden state as a "continuous thought" that is fed back as the next input embedding directly. This enables the model to encode multiple alternative reasoning paths (breadth-first search) rather than committing to one deterministic path (depth-first, as in chain-of-thought). Coconut outperforms CoT on logical reasoning tasks requiring substantial planning search.

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

Coconut belongs to Quadrant III for the following reasons:

1. **Structured Non-Textual Representation**: Coconut's "continuous thoughts" are high-dimensional latent vectors (the model's last hidden states), not natural language text. This is a genuinely structured, non-textual intermediate representation — a latent state that encodes the model's reasoning progress in the continuous embedding space.

2. **No External Tool Usage**: All reasoning occurs within the model's forward passes. There are no external tool calls, API invocations, or execution feedback loops. The "verification" of intermediate states happens through the model's internal attention mechanisms applied to the continuous thought vectors.

3. **Structural Properties Enabling Novel Reasoning**: The continuous thought representation enables BFS-style reasoning (encoding multiple hypotheses simultaneously) that is structurally impossible with discrete text tokens. This is not just a formatting difference from text CoT — it enables qualitatively different computational behavior (parallel hypothesis encoding).

4. **Contrast with Quadrant I**: Unlike LLaVA-CoT or Insight-V which produce intermediate reasoning as natural language text (verifiable, readable, but limited to serial reasoning), Coconut's intermediate states are not interpretable as language and do not constitute a "textual rationale."

5. **Contrast with Quadrant IV**: While Coconut produces structured intermediate states, these states are not executable programs or replayable action sequences — they are ephemeral hidden state vectors that exist only during the model's forward pass and cannot be independently replayed or verified by running them again (they don't persist as artifacts).

---

## Key Contributions

1. **Continuous Thought as Reasoning Medium**: The core innovation is using the model's last hidden state (a continuous vector in the embedding space) as an intermediate reasoning token, instead of decoding it to a word and re-encoding the word. This "skips" the bottleneck of discretization and allows the hidden state to carry richer information than any single token could express.

2. **BFS-Style Planning via Continuous Encoding**: Demonstrates empirically that continuous thoughts can simultaneously encode multiple plausible next reasoning steps (analogous to BFS exploration). This is because the continuous space is not constrained to one discrete token — the hidden state can represent a superposition of multiple directions. The model can hold uncertainty about which reasoning path to follow, rather than committing prematurely.

3. **Curriculum Training Strategy**: Training Coconut requires a careful curriculum since the model must learn to produce useful continuous thoughts (training signal only comes from final answer correctness). The proposed curriculum gradually shifts from text CoT to continuous thoughts, starting with full CoT supervision and progressively replacing more text tokens with continuous thought passes.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Low
- Continuous thought vectors are not interpretable by humans — they cannot be inspected to verify whether they are "grounded" in the input
- No explicit grounding mechanism: the model's internal representations are opaque
- Post-hoc probing can reveal some information encoded in continuous thoughts (e.g., which tokens/concepts are being attended to), but this requires additional analysis and is not part of the standard inference procedure
- Significantly lower grounding strength than text CoT, which at least allows tracing which words the model used

### Checkability
**Assessment**: Low
- Intermediate continuous thoughts cannot be checked for correctness — there is no standard by which to evaluate whether a hidden state vector is "correct" at a given reasoning step
- Only the final text output (the answer) is checkable
- The curriculum training process checks outcome accuracy but provides no step-level feedback for continuous thought correctness
- Unlike text CoT where each step can be validated for logical consistency, continuous thoughts are a black box

### Replayability
**Assessment**: Low
- Continuous thoughts do not persist as artifacts — they are computed as part of the model's forward pass and are not stored separately
- To "replay" a Coconut reasoning trace, one must re-run the entire forward pass with identical inputs, which is essentially just re-running inference rather than replaying a meaningful trace
- No external state logging mechanism is described that would allow replaying the sequence of continuous thoughts
- Significantly less replayable than any text-producing system (Quadrant I/II/IV), where at minimum the final text output can be re-read

### Faithfulness Risk
**Assessment**: Very High
- Continuous thoughts are completely opaque — there is no way to verify whether the model's reasoning is faithful to the input
- The model cannot be interrogated about "why" it produced a particular continuous thought, making post-hoc faithfulness evaluation impossible
- Any failure to faithfully reason from the input is completely invisible until the final answer is wrong
- Unlike text CoT where hallucinations leave a textual trail, Coconut hallucinations are invisible
- This represents the maximum faithfulness risk in the 2×2 matrix: no visibility into any intermediate representation

### Robustness
**Assessment**: Moderate
- No tool dependencies — no external failure modes
- Sensitive to training distribution: continuous thoughts are useful only for reasoning types represented in training
- The curriculum training strategy may be sensitive to the schedule of gradually replacing text with continuous thoughts
- BFS-style reasoning should improve robustness for planning-heavy tasks by not committing prematurely to one path
- May struggle on tasks where intermediate steps need to be visible to catch perceptual errors (no corrective feedback)

### Cost/Latency
**Assessment**: Low-Moderate
- Each "continuous thought" step is computationally equivalent to one forward pass (vs. generating and re-encoding a text token)
- Eliminates tokenization/embedding overhead of discrete text CoT
- Number of continuous thought steps is configurable — can be set based on task complexity
- Generally more efficient than text CoT for equivalent reasoning depth, since continuous thoughts carry more information per step
- No external API calls or tool overhead

### Security
**Assessment**: Low Risk
- Entirely internal reasoning — no external communication or data access
- No prompt injection surface beyond input text
- Opaque reasoning makes it harder to audit for potential misuse, but also harder to inject adversarial content into the reasoning process
- As a text-in, text-out system (only the final answer is text), the attack surface is limited

---

## Failure Modes

1. **Complete Opacity of Reasoning Process**: Coconut's fundamental limitation is that its reasoning process is entirely invisible. When the model produces a wrong answer, there is no way to diagnose whether the error came from early wrong hypotheses (wrong BFS exploration), incorrect inference within a hypothesis, or failure to encode the right information in the continuous thoughts. This opacity makes debugging, improving, and auditing the system extremely difficult.

2. **Training Signal Sparsity for Long-Horizon Reasoning**: The model only receives feedback (whether the final answer is correct) at the end of the reasoning chain. For multi-step problems requiring 10+ continuous thoughts, the gradient signal must propagate through all thought steps, making training extremely challenging and likely causing the model to revert to suboptimal reasoning patterns for very long chains.

3. **Generalization to New Reasoning Domains**: Continuous thoughts are useful representations for reasoning types the model has trained on. For novel reasoning domains (e.g., a model trained on logical reasoning applied to geometric reasoning), the continuous thought vectors may not encode the right inductive biases, leading to worse performance than explicit text CoT where domain knowledge can be expressed linguistically.

4. **Incompatibility with Human Oversight and Correction**: Text CoT allows humans to identify and correct wrong intermediate reasoning steps. Coconut's continuous thoughts make human oversight impossible — if a continuous thought encodes a wrong intermediate conclusion, neither the user nor the developer can detect or correct this without intercepting the model's hidden states (which requires special tools and technical expertise).

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (primary metric — final answer correctness)
- [ ] Step Correctness (not directly evaluable)
- [ ] Evidence Attribution (not applicable)
- [ ] Trace Replayability (not applicable)
- [x] Robustness (evaluated across multiple reasoning datasets)
- [x] Cost/Latency (efficiency comparisons — latent thoughts vs. text tokens)
- [ ] Other

### Benchmarks
- **ProntoQA**: Propositional logic deduction chains
- **ProsQA**: Procedural reasoning requiring sequential planning
- **StrategyQA**: Multi-step commonsense reasoning
- Comparison baseline: Standard chain-of-thought (text CoT)

### Key Results
- **vs. CoT on logical/planning tasks**: Coconut outperforms text CoT on tasks requiring substantial search/backtracking
- **BFS evidence**: Probing experiments show continuous thoughts encode higher entropy (multiple hypotheses) than discrete text tokens
- **Efficiency**: Coconut achieves similar accuracy with fewer "thought tokens" than text CoT
- **Key finding**: Coconut's advantage is largest on tasks requiring search over multiple reasoning paths; standard CoT is competitive on tasks with straightforward reasoning chains

---

## Training & Alignment

### Method
- [x] SFT with Rationale (curriculum training starting from text CoT)
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Curriculum learning** — gradually replace text tokens with continuous thought passes

### Data Collection
- **Curriculum stages**: 
  1. Full text CoT (standard SFT on reasoning datasets)
  2. Replace last N text tokens with continuous thoughts (curriculum parameter N increases per stage)
  3. Final: all intermediate steps are continuous thoughts, only input and output in text
- **Training data**: Logical reasoning datasets (ProntoQA, ProsQA, etc.) with annotated reasoning chains used as curriculum targets
- **Key challenge**: No direct supervision for individual continuous thought steps — only final answer labels are available

---

## Connections to Other Work

### Builds On
- **Chain-of-Thought (Wei et al., 2022)**: Coconut reimagines the CoT paradigm by moving from discrete text to continuous latent representations
- **Internalize CoT (Deng et al., 2023)**: Prior work showing CoT can be partially internalized; Coconut radicalizes this by moving entirely to latent space
- **Implicit Reasoning in LLMs**: Research showing LLMs can represent multi-step reasoning in hidden states

### Related To
- **Process Reward Models (PRMs)**: Both address the challenge of step-level reasoning quality, but from different angles (PRMs verify text steps, Coconut replaces text steps with latent states)
- **Quiet-STaR**: Another approach to latent reasoning that trains models to think before speaking (but still produces text thoughts)
- **Scratchpad methods**: Explicit text scratchpad reasoning — direct contrast to Coconut's latent approach

### Influenced
- Potentially influences: latent reasoning approaches for multimodal models
- Opens research questions: Can continuous visual thoughts (analogous to text Coconut) improve VLM reasoning?

---

## Quotes & Key Insights

> "The language space may not always be optimal for reasoning. Most word tokens primarily ensure textual coherence and are not essential for reasoning, while some critical tokens require complex planning and pose challenges to LLMs."

> "Continuous thoughts can encode multiple alternative next steps, allowing the model to perform a breadth-first search (BFS) rather than committing prematurely to a single deterministic path as in CoT."

**Key Insight 1: Discrete Tokens Are a Bottleneck for Reasoning**
Coconut's central insight is that forcing all intermediate reasoning through the discrete token bottleneck is suboptimal. Many reasoning steps require representing uncertainty or exploring multiple hypotheses simultaneously — capabilities that continuous vectors support naturally but discrete tokens cannot. This motivates exploring reasoning representations beyond natural language.

**Key Insight 2: The BFS vs. DFS Analogy**
Standard text CoT is DFS — it commits to one path and follows it to completion. Coconut enables BFS — it can maintain multiple hypotheses in superposition. This is a fundamental algorithmic difference, and for problems where DFS leads to commitment errors (e.g., early wrong assumptions that are hard to reverse), BFS provides a structural advantage.

---

## Survey Placement

### Section Placement
- [x] Section 4.3 (Methods by Quadrant - Quadrant III: Structured w/o Tools)
- [ ] Section 5 (Learning & Alignment)
- [ ] Section 6 (Evaluation & Benchmarks)
- [ ] Section 7 (Applications)
- [x] Section 8 (Challenges & Future - latent reasoning as frontier direction)

### Narrative Role
Coconut is the **defining example of Quadrant III** — structured intermediate representation (continuous latent states) without tool use. It represents the most radical departure from human-readable reasoning, trading interpretability for reasoning power. In the survey, Coconut anchors the discussion of structured-but-opaque reasoning approaches, illustrating the fundamental tension between verifiability (which requires readable, checkable intermediate states) and reasoning efficiency (which may benefit from latent representations).

### Comparison Points
**Excels at**:
- Reasoning on planning-heavy tasks requiring backtracking
- Efficiency (fewer thought tokens per reasoning step)
- No tool overhead

**Fails at**:
- Human interpretability (opaque latent states)
- Verifiability (cannot check intermediate steps)
- Grounding (no way to verify latent thoughts reference input correctly)

---

## Notes

### Quadrant III Note
Coconut is placed in Quadrant III (Structured, No Tools) rather than Quadrant I because its intermediate representations are genuinely non-textual — they are high-dimensional vectors in the model's latent space. This is a fundamentally different representation type from natural language CoT. However, it shares with Quadrant I the property of having no external verification mechanism (no tool use), making the internal representation opaque and unverifiable.

### Multimodal Extension Note
The original Coconut paper focuses on text-only reasoning (LLMs). An open research question — and a natural survey gap — is whether continuous visual thoughts can similarly improve VLM reasoning. This could represent a future direction bridging Coconut's latent reasoning with visual modalities.

---

## BibTeX

```bibtex
@article{hao2024coconut,
  title={Training Large Language Models to Reason in a Continuous Latent Space},
  author={Hao, Shibo and Sukhbaatar, Sainbayar and Su, DiJia and Li, Xian and Hu, Zhiting and Weston, Jason and Tian, Yuandong},
  journal={arXiv preprint arXiv:2412.06769},
  year={2024},
  url={https://arxiv.org/abs/2412.06769}
}
```

**Status**: ✅ Complete — Quadrant III Paper
