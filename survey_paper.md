# From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)

## Abstract

Multimodal Large Language Models (MLLMs) have demonstrated remarkable capabilities in visual reasoning tasks, often producing fluent multi-step explanations for their answers. However, these explanations frequently lack **verifiability**—they may be plausible but unfaithful to actual visual evidence, difficult to audit step-by-step, and fragile under distribution shifts. This survey re-frames Visual Chain-of-Thought (Visual CoT) as an interface for **verifiable reasoning** rather than narrative explanation. We introduce a **2×2 Verifiability Matrix** that organizes recent (2024–present) work along two axes: (1) **intermediate representation** (textual rationales vs. structured traces) and (2) **verification channel** (no tools vs. tool/execution-augmented). Through this taxonomy, we analyze how different approaches trade off between human readability and machine checkability, between internal consistency and external grounding. We synthesize evaluation protocols that move beyond answer accuracy to measure process-level properties such as step correctness, evidence attribution, and trace replayability. Finally, we identify open challenges including robust tool-use, standardized trace formats, and cost-aware verification, providing design recommendations for building trustworthy multimodal reasoning systems.

**Keywords**: Visual Chain-of-Thought, Multimodal Reasoning, Verifiable AI, Faithfulness, Grounding, AI Agents

---

## 1 Introduction

### 1.1 The Verifiability Gap in Multimodal Reasoning

Recent advances in Multimodal Large Language Models (MLLMs) have enabled systems that can reason about visual content through multi-step chains of thought. These models generate explanations that appear coherent and plausible, often matching or exceeding human performance on benchmarks like VQA, ScienceQA, and chart understanding tasks. However, a critical gap has emerged: **the gap between plausible explanations and verifiable evidence**.

Consider a medical VQA system that answers "pneumonia" when shown a chest X-ray and explains: "I observe bilateral opacities in the lower lung fields, which is characteristic of pneumonia." This explanation sounds authoritative, but was it actually derived from analyzing those regions? Or did the model learn a superficial correlation and generate a post-hoc rationale? Current Visual CoT methods often cannot distinguish between these cases—their reasoning is **not machine-checkable** and **not grounded** in identifiable visual evidence.

This verifiability gap manifests in four key failure modes:

1. **Unfaithful Reasoning**: Models generate explanations that do not reflect their actual decision process (plausible but wrong).
2. **Unauditable Steps**: Intermediate reasoning cannot be inspected or validated step-by-step.
3. **Fragile Generalization**: Performance degrades under distribution shifts or open-world conditions.
4. **Hallucination Despite CoT**: Models produce confident, multi-step reasoning about visual content that does not exist.

### 1.2 From Explanations to Evidence

This survey proposes a fundamental re-framing: **Visual CoT should be evaluated not by how well it explains, but by how well it provides verifiable evidence**. An explanation is a narrative that humans can read; evidence is an artifact that can be checked, replayed, and validated.

The distinction is critical:
- **Explanation**: "The object appears red and round, so it might be an apple." (human-readable, not checkable)
- **Evidence**: "Object detection confidence: 0.92 for 'apple' at [x1, y1, x2, y2]; color histogram matches apple prototype (p=0.87)." (machine-checkable, replayable)

We argue that verifiability increases when intermediate reasoning artifacts become:
- **(a) Machine-checkable**: Structured traces (programs, graphs, state logs) rather than free-form text
- **(b) Externally grounded**: Connected to tool outputs or execution feedback rather than purely internal states

This shift from explanations to evidence requires new design patterns: executable reasoning traces, tool-augmented verification loops, standardized formats for intermediate states, and process-level evaluation metrics.

### 1.3 Survey Contributions

This survey makes five key contributions:

1. **A Verifiability-Centric Taxonomy**: We introduce a 2×2 matrix that cleanly separates *representation* (textual vs. structured) from *verification channel* (no tools vs. tool-augmented), providing a unified framework for analyzing recent work.

2. **A Design Space for Verifiable Reasoning**: We synthesize recurring patterns across quadrants: grounding mechanisms, trace formats, replay strategies, tool orchestration, and memory architectures.

3. **Process-Level Evaluation Synthesis**: We move beyond answer accuracy to compare metrics for step correctness, evidence attribution, trace replayability, robustness, and cost/latency.

4. **Training & Alignment Map**: We trace the progression from SFT with rationales → process supervision → PRM/RL/DPO, identifying cold-start + RL for tool-use as a recurring pattern.

5. **Open Problems & Recommendations**: We identify critical gaps including robust tool-use, adversarial vulnerabilities, cost budgets, standardized trace formats, and benchmarks for real-world integration.

### 1.4 Organization

The remainder of this survey is organized as follows:

- **Section 2** establishes background concepts: faithfulness vs. plausibility, grounding in multimodal settings, the agent loop, and what "verification" means.
- **Section 3** introduces our 2×2 Verifiability Matrix taxonomy with detailed quadrant definitions.
- **Section 4** surveys methods by quadrant, analyzing representative works and their trade-offs.
- **Section 5** synthesizes training and alignment approaches for verifiability.
- **Section 6** compares evaluation protocols and benchmarks.
- **Section 7** discusses applications in safety-critical domains (optional).
- **Section 8** identifies challenges and future directions.
- **Section 9** provides best practices for designing verifiable Visual CoT agents.
- **Section 10** concludes.

**Scope**: This survey focuses on methods published or preprinted between January 2024 and present that produce multi-step visual reasoning with explicit intermediate artifacts. We exclude single-step VQA methods and purely text-based reasoning.

---

## 2 Background

### 2.1 Faithfulness vs. Plausibility

A fundamental distinction in interpretable AI is between **faithfulness** and **plausibility** (Jacovi & Goldberg, 2020), which becomes critical in multimodal reasoning:

**Definition 2.1 (Plausibility)**: A reasoning trace is *plausible* if it appears coherent and reasonable to human evaluators. Plausibility is about surface-level coherence: the explanation "makes sense" given the question and answer.

**Definition 2.2 (Faithfulness)**: A reasoning trace is *faithful* if it accurately reflects the model's actual decision process. Faithfulness requires that the stated reasons causally contributed to the output.

The tension arises because these properties are independent:
- **Plausible + Faithful**: Ideal case—reasoning is both readable and accurate
- **Plausible + Unfaithful**: Dangerous case—convincing but misleading (common in current VLMs)
- **Implausible + Faithful**: Rare—correct reasoning that appears strange
- **Implausible + Unfaithful**: Obvious failure

**Example 2.1 (Unfaithful Plausibility)**: A VLM answers "2" to "2 + 2 = ?" with CoT: "Adding 2 and 2 gives 4... wait, but considering the context, the answer should be 2." The reasoning mentions "4" but outputs "2"—the CoT does not faithfully represent the computation.

In multimodal settings, unfaithfulness often manifests as **reasoning without seeing**: the model generates a detailed visual analysis without actually attending to the image. This is possible because language models learn statistical patterns in reasoning traces from training data, which can be reproduced without genuine visual grounding.

**Measurement Challenge**: Faithfulness is fundamentally unobservable—we cannot directly access the model's "true" reasoning. Instead, we rely on indirect tests:
- **Counterfactual tests**: If we modify the image, does the reasoning change appropriately?
- **Attention attribution**: Do attention weights correlate with stated reasoning?
- **Intermediate supervision**: Can we verify individual steps against ground truth?

None of these are perfect, but they provide evidence for or against faithfulness.

### 2.2 Grounding in Multimodal Settings

**Definition 2.3 (Grounding)**: A reasoning step is *grounded* if it can be linked to specific, identifiable elements in the input (image regions, objects, attributes, relationships).

Grounding exists on a spectrum:

| Level | Description | Example |
|-------|-------------|---------|
| L0: No grounding | Purely textual reasoning | "I think the answer is A" |
| L1: Implicit grounding | References visual concepts without pointers | "The object looks red" |
| L2: Weak grounding | Mentions spatial locations vaguely | "In the top-left corner" |
| L3: Strong grounding | Points to specific regions/objects | "Object at [x1,y1,x2,y2] with 0.9 confidence" |
| L4: Executable grounding | Grounding can be verified by running code | "Ran detector; found apple at [coords]" |

Most current Visual CoT methods operate at L1-L2, providing implicit or weak grounding. Higher levels (L3-L4) enable stronger verifiability but require structured representations and/or tool integration.

**Grounding Failure Modes**:
1. **Ghost References**: Mentioning objects or regions that don't exist in the image
2. **Vague Pointing**: Using ambiguous terms ("the object", "this area") that cannot be verified
3. **Mismatched Modality**: Reasoning about visual properties that cannot be determined from the image type (e.g., claiming to see color in a grayscale image)
4. **Cascading Grounding Errors**: Early grounding mistakes propagate through subsequent reasoning

### 2.3 The Agent Loop: Observe → Plan → Act → Verify

Multimodal reasoning agents extend beyond single-pass CoT by introducing an **agentic loop** that interleaves perception, reasoning, and action:

```
┌──────────────────────────────────────────┐
│  1. OBSERVE: Perceive visual input       │
│     - Encode image/features              │
│     - Retrieve from memory               │
├──────────────────────────────────────────┤
│  2. PLAN: Decide next reasoning step     │
│     - Generate sub-goal                  │
│     - Select tool/operation              │
├──────────────────────────────────────────┤
│  3. ACT: Execute selected operation      │
│     - Call tool (detector, OCR, etc.)    │
│     - Run code/program                   │
│     - Query external source              │
├──────────────────────────────────────────┤
│  4. VERIFY: Check intermediate result    │
│     - Compare against constraints        │
│     - Validate tool output               │
│     - Decide: continue or revise         │
└──────────────────────────────────────────┘
              ↓ (loop or terminate)
         ANSWER: Final output with trace
```

**Key Design Choices**:
- **Granularity**: How fine-grained are the loop iterations?
- **Memory**: What information persists across iterations?
- **Termination**: How does the agent decide when to stop?
- **Verification**: What checks are performed at each step?

Agents with longer loops and richer verification tend toward higher verifiability (Quadrants II and IV), but at increased computational cost.

### 2.4 What is Verification?

**Definition 2.4 (Verification)**: *Verification* is the process of checking whether a reasoning step or conclusion is correct, grounded, and trustworthy.

In multimodal reasoning, verification operates at multiple levels:

| Level | Target | Mechanism | Example |
|-------|--------|-----------|---------|
| Step-level | Individual reasoning step | Consistency check, tool validation | "Does this detection match the stated region?" |
| Trace-level | Full reasoning chain | Replay, constraint satisfaction | "Can we re-run the trace and get the same result?" |
| Answer-level | Final conclusion | Comparison to ground truth | "Is the answer correct?" |

**Verification Channels**:
1. **Internal Consistency**: Check if steps are logically coherent (no external tools)
2. **Tool Feedback**: Use external tools to validate claims (detectors, OCR, etc.)
3. **Execution**: Run code/programs to verify computational steps
4. **Human-in-the-loop**: Request human feedback on uncertain steps
5. **Cross-validation**: Compare multiple reasoning paths for agreement

This survey's taxonomy (Section 3) distinguishes methods by their primary verification channel: internal (no tools) vs. external (tool/execution-augmented).

**Verification ≠ Correctness**: A verified step is not necessarily correct—verification mechanisms themselves can fail. The goal is to increase *confidence* through multiple, independent checks.

### 2.5 Related Paradigms

Our work builds on several foundational paradigms:

**Chain-of-Thought (CoT)** (Wei et al., 2022): Eliciting step-by-step reasoning through prompting. Visual CoT extends this to multimodal inputs, but faces unique grounding challenges.

**ReAct** (Yao et al., 2023): Interleaving reasoning with actions (tool calls). ReAct-style loops are central to Quadrant II methods, though originally developed for text-only settings.

**Tree-of-Thought (ToT)** (Yao et al., 2023): Exploring multiple reasoning branches. ToT ideas appear in methods using self-consistency or multi-path verification.

**Process Supervision** (Lightman et al., 2023): Training models with step-level feedback rather than outcome-only rewards. Process supervision is critical for improving faithfulness across all quadrants.

**Tool-Use in LLMs**: Recent work on equipping language models with calculators, search engines, code interpreters, and APIs. Multimodal tool-use adds complexity: tools must operate on visual inputs and produce visual outputs/grounding.

**Distinction from Prior Surveys**: Existing surveys on VLMs focus on architectures, training, or benchmarks. Surveys on reasoning focus on text-only settings. This is the first survey to specifically address **verifiability** in **multimodal** reasoning through the lens of **intermediate representations** and **verification channels**.

---

## 3 Taxonomy: A 2×2 Verifiability Matrix

This survey introduces a **2×2 Verifiability Matrix** to organize recent work in multimodal reasoning. The taxonomy is defined by two orthogonal axes:

1. **Axis A (Intermediate Representation)**: What form do the reasoning intermediates take?
2. **Axis B (Verification Channel)**: How can the reasoning be verified?

This clean separation enables precise comparison: methods may differ in representation but share verification strategies, or vice versa.

### 3.1 Axis A: Intermediate Representation

The first axis captures **what** intermediate reasoning artifacts look like:

#### Textual Rationales

**Definition**: Free-form natural language descriptions of reasoning steps, plans, or reflections.

**Characteristics**:
- ✓ Human-readable without special tools
- ✓ Flexible expression of uncertainty, hypotheses, reflections
- ✗ Not inherently machine-checkable
- ✗ Ambiguous or vague references possible
- ✗ Difficult to enforce structural constraints

**Examples**:
- "First, I need to identify the objects in the image. I see a red car..."
- "Let me think step by step: the chart shows an upward trend..."
- "Wait, I should reconsider. The previous step might be wrong because..."

**Verification Strategies** (without structured representation):
- Self-consistency (multiple samples agree?)
- Reflection/critique (model checks its own reasoning)
- Process supervision (external feedback on step quality)
- Constraint checking (does text satisfy stated rules?)

#### Structured Traces

**Definition**: Machine-checkable intermediate artifacts with explicit schema or executable semantics.

**Characteristics**:
- ✓ Automatically verifiable (can run/check programmatically)
- ✓ Enforces explicit grounding (coordinates, object IDs, etc.)
- ✓ Replayable (same trace → same result)
- ✗ Requires parsers/interpreters
- ✗ Less flexible for uncertain or hypothetical reasoning
- ✗ May lose nuance in discretization

**Types of Structured Traces**:

| Type | Format | Verification | Example |
|------|--------|--------------|---------|
| **Tables** | Rows/columns with schema | Schema validation, constraint checks | Object properties table |
| **Graphs** | Nodes + edges | Graph traversal, path validation | Scene graph reasoning |
| **Programs** | Executable code | Run code, check output | Python script for counting |
| **State Logs** | Structured records | Replay, consistency | `{"step": 1, "action": "detect", "result": {...}}` |
| **Latent Vectors** | Continuous representations | Similarity checks, clustering | Thought state embeddings |
| **Sketches** | Visual diagrams | Spatial constraints, overlay | Bounding boxes, segmentation |

**Key Distinction**: Structured traces enable **automatic verification**—a computer can check whether the trace satisfies constraints, can be replayed, and produces consistent results. This is impossible with free-form text alone.

### 3.2 Axis B: Verification Channel

The second axis captures **how** reasoning can be verified:

#### No Tools / No Execution

**Definition**: Verification relies on internal consistency, logical constraints, or process supervision—without external tool feedback or execution.

**Characteristics**:
- ✓ Self-contained (no external dependencies)
- ✓ Fast (no tool call latency)
- ✓ Safe (no tool misuse risk)
- ✗ Limited to what the model can check internally
- ✗ Cannot verify factual claims about the world
- ✗ Faithfulness still unobservable

**Verification Mechanisms**:
- **Consistency**: Sample multiple times; do they agree?
- **Logical Constraints**: Does reasoning satisfy stated rules?
- **Self-Reflection**: Can the model critique and revise its own reasoning?
- **Process Supervision**: External model/human provides step-level feedback

**When Sufficient**: For closed-world tasks with clear rules (logic puzzles, constrained VQA), internal verification may suffice. For open-world reasoning, external grounding becomes critical.

#### Tool-/Execution-Augmented

**Definition**: Verification uses external tools (detectors, OCR, retrieval, code execution, web search) or executable programs that provide reproducible evidence.

**Characteristics**:
- ✓ Externally grounded (not just internal states)
- ✓ Reproducible (tool outputs can be re-checked)
- ✓ Factual verification possible (not just consistency)
- ✗ Tool call latency and cost
- ✗ Tool failure modes (errors, hallucinations, injection)
- ✗ Security risks (web access, code execution)

**Tool Categories**:

| Category | Examples | Verification Role |
|----------|----------|-------------------|
| **Perception Tools** | Object detectors, OCR, segmentation | Ground claims to visual evidence |
| **Computation Tools** | Calculators, code interpreters | Verify computational steps |
| **Retrieval Tools** | Search engines, knowledge bases | Fact-check claims |
| **Memory Tools** | Vector databases, episodic memory | Maintain context across steps |
| **Specialist Verifiers** | Domain-specific checkers | Validate domain-specific claims |

**Execution Feedback**: Beyond tool calls, some methods execute entire programs or reasoning traces, enabling end-to-end replay and step-by-step validation.

### 3.3 The Four Quadrants

Crossing the two axes yields four quadrants:

```
                    VERIFICATION CHANNEL
              ┌─────────────────┬─────────────────┐
              │  No Tools       │  Tool-/Execution│
              │                 │  -Augmented     │
  ┌───────────┼─────────────────┼─────────────────┤
  │           │                 │                 │
  │ TEXTUAL   │  Quadrant I     │  Quadrant II    │
  │           │  Text-only CoT  │  Text + Tools   │
  │           │                 │  (ReAct-style)  │
  │           │  • Consistency  │  • Tool loops   │
  R           │  • Reflection   │  • Memory       │
  │           │  • Supervision  │  • Orchestration│
  │           │                 │                 │
  ├───────────┼─────────────────┼─────────────────┤
  │           │                 │                 │
  │ STRUCTURED│  Quadrant III   │  Quadrant IV    │
  │           │  Structured     │  Structured +   │
  │           │  w/o Tools      │  Tools/         │
  │           │                 │  Executable     │
  │           │  • Schema       │  • Programs     │
  │           │  • Graphs       │  • Sketches     │
  │           │  • Latent       │  • State logs   │
  │           │                 │                 │
  └───────────┴─────────────────┴─────────────────┘
```

#### Quadrant I: Text-only CoT

**Definition**: Free-form textual reasoning without external tool feedback.

**Representative Works**: CURE (NAACL 2024), self-consistency methods

**Strengths**:
- Simple, no tool integration required
- Fast inference (no tool latency)
- Human-readable explanations

**Limitations**:
- Plausible-but-unfaithful reasoning
- Cannot verify factual claims
- Limited to model's internal knowledge

**Verifiability Level**: ★☆☆☆☆ (Low)

---

#### Quadrant II: Text + Tools (ReAct-style)

**Definition**: Textual planning with tool calls in Action/Observation loops.

**Representative Works**: VideoAgent (ECCV 2024), multimodal ReAct methods

**Strengths**:
- Tool outputs provide external evidence
- Trajectory is auditable (actions + observations)
- Flexible tool orchestration

**Limitations**:
- Tool misuse or misinterpretation
- Brittle to tool noise/failures
- Prompt injection risks (web tools)

**Verifiability Level**: ★★☆☆☆ (Moderate)

---

#### Quadrant III: Structured w/o Tools

**Definition**: Structured intermediate states without external execution.

**Representative Works**: MCOUT-style (arXiv 2025), graph-based reasoning

**Strengths**:
- Schema constraints enable automatic checks
- Consistency between structure and perception
- Replayable (same structure → same interpretation)

**Limitations**:
- Structured artifacts can still be wrong
- Requires schema design
- May lose flexibility

**Verifiability Level**: ★★☆☆☆ (Moderate)

---

#### Quadrant IV: Structured + Tools / Executable

**Definition**: Executable traces (programs, sketches, state logs) with tool/execution feedback.

**Representative Works**: ViperGPT (ICCV 2023), Visual Sketchpad (NeurIPS 2024), DeepEyesV2 (arXiv 2025), CodeV, CodeDance, RECODE, VDebugger, MM-Zero, VLAgent, and 9 others (18 total)

**Strengths**:
- Highest verifiability (replayable + externally grounded)
- Step-level validation possible
- Specialist verifiers can audit traces
- Clear failure localization

**Limitations**:
- Highest cost/latency
- Security risks (code execution, web)
- Cascading errors across steps
- Tool interface complexity

**Verifiability Level**: ★★★★☆ (High)

### 3.4 Verifiability Spectrum

While the 2×2 matrix provides discrete categories, verifiability exists on a **spectrum**. Figure 3.2 illustrates how methods can be positioned along a continuous axis from "pure explanation" to "fully verifiable evidence":

```
Low Verifiability ←————————————————————————————————→ High Verifiability

[Text-only CoT] —— [Text + Simple Tools] —— [Structured Traces] —— [Executable + Tools]
     │                    │                        │                      │
  Quadrant I           Quadrant II            Quadrant III          Quadrant IV
```

**Factors Affecting Verifiability**:

1. **Grounding Strength**: How precisely can reasoning be linked to visual evidence?
2. **Checkability**: Can steps be automatically validated?
3. **Replayability**: Can the trace be re-run to reproduce results?
4. **External Validation**: Are claims checked against external sources?
5. **Error Localization**: Can failures be pinpointed to specific steps?

**Design Implication**: Moving rightward on the spectrum generally increases verifiability but also increases cost, latency, and complexity. The optimal position depends on the application:
- **Low-stakes applications** (entertainment, casual QA): Quadrant I-II may suffice
- **High-stakes applications** (medical, legal, scientific): Quadrant III-IV preferred

### 3.5 Quadrant Migration Patterns

Methods may **migrate between quadrants** during design or deployment:

**I → II (Adding Tools)**: A text-only CoT system adds tool calls to improve grounding. Example: adding OCR to a chart reasoning system.

**I → III (Adding Structure)**: A text-only system adopts structured traces for better checkability. Example: requiring explicit object references in reasoning.

**II → IV (Structuring Tool Use)**: A ReAct-style system formalizes tool calls into executable programs. Example: converting text plans to Python code.

**III → IV (Adding Execution)**: A structured trace system adds tool feedback. Example: adding detector validation to graph-based reasoning.

**Migration Drivers**:
- Failure analysis revealing limitations of current quadrant
- Application requirements demanding higher verifiability
- Tool availability/cost changes

**Migration Costs**:
- Engineering effort for tool integration
- Latency increases
- New failure modes (tool errors, injection)

Understanding these patterns helps designers make informed trade-offs.

---

## 4 Methods by Quadrant

This section surveys recent methods (2024–present) organized by our 2×2 taxonomy. For each quadrant, we:
1. Define the approach and its characteristics
2. Analyze representative works
3. Discuss verification strategies
4. Identify failure modes
5. Compare trade-offs

---

### 4.1 Quadrant I: Text-only CoT

**Definition**: Methods that generate free-form textual reasoning without external tool feedback.

#### 4.1.1 Approach Overview

Quadrant I methods represent the simplest approach to Visual CoT: the model generates step-by-step natural language explanations based solely on its internal representations. Verification, when present, relies on:
- **Self-consistency**: Multiple reasoning samples should agree
- **Reflection and self-correction**: The model critiques and revises its own reasoning
- **Process supervision**: External feedback on step quality (PRMs, rule-based rewards, DPO)
- **Visual cues and structured stages**: Patch-level hints, multi-stage pipelines, or contrastive signals to improve grounding

**Why Text-only?** Despite limitations, Quadrant I approaches remain popular because:
- No tool integration complexity
- Fast inference (no external calls)
- Works with any VLM (no special capabilities required)
- Human-readable by default

Recent work (2024–2026) has expanded the design space significantly: from consistency-based verification (CURE) to process reward models (VisualPRM, VRPRM), from self-correction learning (SCL, Sherlock) to RL for visual reasoning (R1-VL, Visionary-R1, GThinker), and from structured stages (LLaVA-CoT) to visual cue augmentation (ChainV, PatchCue) and faithfulness analysis (Journey Before Destination, MIRA).

**Connections and Progression**: CURE establishes consistency as a weak verification proxy; R3V extends this with self-training and reveals the noisy CoT problem (8–70% correct CoT in correct-answer solutions). SCL and Sherlock show that self-correction requires explicit training—inference-time prompting fails. Process supervision (VisualPRM, VRPRM, R1-VL) addresses step-level quality; Critic-V and LLaVA-Critic-R1 use critic feedback. Structured formats (LLaVA-CoT, Visionary-R1) and visual cues (ChainV, PatchCue) improve grounding. Benchmarks (MIRA, Journey Before Destination, Visual CoT) diagnose gaps: text-only reasoning is insufficient for visualization-essential tasks; faithfulness and answer accuracy can diverge.

---

#### 4.1.2 Representative Works

##### Consistency & Self-Correction (6 papers)

This subcategory focuses on improving reasoning quality through consistency evaluation, reflection, self-correction training, noisy-thinking mitigation, and contrastive self-improvement—all without external tools.

**CURE** (Chen et al., NAACL 2024) introduces the first benchmark for measuring both reasoning performance and consistency in VLMs. It proposes forward consistency (Cf)—whether correct CoT steps lead to correct final inference—and backward consistency (Cb)—whether correct final inference implies correct CoT steps. A two-stage training framework (SFT + RLAIF) uses LLM feedback (GPT-3.5-Turbo) on Sophistication, Consistency, and Groundedness to rank reasoning chains. CURE achieves ~4% relative improvement (Ro: 54.93→56.91, Cf: 83.66→86.67) on the CURE benchmark (1,622 samples). A fundamental gap remains: even SOTA models (BLIP-2) show Cf=83.1% vs. human Cf=95.5%, and consistency ≠ correctness—models can be consistently wrong.

**R3V** (Cheng et al., NAACL 2025) proposes self-training via reflection on CoT rationales, requiring only QA pairs and a small GPT-distilled warmup (800–1000 samples per dataset). It bootstraps positive samples (correct answer) and negative samples (wrong answer), then introduces self-refine loss (given wrong CoT, generate corrected version) and self-select loss (compare multiple candidates, identify correct one). R3V achieves 23–60% relative improvement over GPT-distilled baselines across TabMWP, ChartQA, CLEVR-Math, MiniWob, GeoQA, M3CoT. Test-time self-selection (N=3) consistently outperforms majority voting. A critical finding: only 8–70% of correct-answer solutions have fully correct CoT (M3CoT: 8%), explaining why DPO fails (STaR+DPO ≈ STaR).

**Sherlock** (Ding & Zhang, NeurIPS 2025) addresses error propagation through trajectory-level self-correction: instead of regenerating the entire response (R3V), the model corrects only the erroneous suffix while preserving the correct prefix. Preference data is constructed via visual perturbation—applying noise to images creates controllable quality gaps between responses. Dynamic β adapts regularization to sample quality. With only 20k annotated samples (vs. 100k LLaVA-CoT, 260k Mulberry), Sherlock achieves 64.1% direct and 65.4% after self-correction. Stage III enables online self-improvement without external supervision. Analysis reveals step-wise self-correction occurs in <10% of cases without explicit training; Modify One Step causes accuracy to drop to ~25%.

**SCL** (He et al., ACL 2025) provides a key negative result: VLMs *cannot* effectively self-correct at inference time without fine-tuning—multi-turn correction prompts and external critiques fail to improve accuracy. However, DPO on self-generated two-turn correction data (SELFCORSET) significantly improves performance. SELFCORSET is constructed by prompting the model twice (initial response, then correction prompt) and labeling pairs by correctness (++, +−, −+, −−). SCL reframes self-correction as a training-time capability: the model learns to generate better first-pass responses, reducing inference cost compared to iterative refinement.

**RTWI** (Li et al., arXiv 2026) addresses the Noisy Thinking problem in Thinking-with-Images: imperfect visual cues and reasoning steps cause error accumulation, degrading final answers. RTWI proposes text-centric reliability estimation—the model (or auxiliary model) evaluates cue and step quality from the reasoning trace itself, without external tools. Robust filtering removes low-reliability components; voting aggregates over multiple reasoning paths. This prevents noise from contaminating the final answer and improves verifiability through internal quality control.

**VC-STaR** (Pan et al., arXiv 2026) leverages VLMs' intrinsic ability to compare contrastive VQA pairs (e.g., "Which image shows X?" with two similar images) to build a self-improving framework. It generates VisCoR-55K contrastive pairs and self-generated rationales, then performs SFT on these rationales. The contrastive structure provides implicit verification—the model must identify the correct image, reducing "explain without seeing" risk. Visual contrast bootstrap reduces hallucinations without external tools.

---

##### Structured Stages & Visual CoT (6 papers)

These methods introduce structured reasoning pipelines, visual grounding traces (bounding boxes, patch cues), or multi-agent architectures to improve interpretability and grounding—while remaining tool-free.

**LLaVA-CoT** (Xu et al., ICCV 2025) proposes a four-stage pipeline: Summary (problem framing), Caption (perceptual grounding in language), Reasoning (logical derivation), Conclusion (answer extraction). Trained on LLaVA-CoT-100k (GPT-4o-generated stage-wise annotations), it uses Stage-Wise Retracing Search (SWIRES) for beam search at stage boundaries rather than token level. LLaVA-CoT outperforms base model by 9.4% and surpasses Gemini-1.5-pro, GPT-4o-mini, and Llama-3.2-90B. The Caption stage forces explicit visual description before reasoning; SWIRES achieves +9.4% over greedy decoding. A failure mode: Caption-Reasoning stage-boundary drift—Reasoning may contradict or ignore Caption.

**Visual CoT** (Shao et al., NeurIPS 2024 DB) introduces a 438K dataset with intermediate bounding-box annotations (~98k with full reasoning steps) spanning five domains. A multi-turn pipeline: Turn 1 predicts the answer-critical region (model-generated bbox), Turn 2 receives the cropped region and generates reasoning + answer. The benchmark evaluates region identification (IoU) and reasoning accuracy. Key finding: MLLMs struggle when answer-critical information resides in small or high-resolution regions; CoT traces without explicit visual focus are uninterpretable.

**Insight-V** (Dong et al., arXiv 2024) addresses long-chain visual reasoning with a multi-agent pipeline: a Reasoning Agent generates extended CoT (problem decomposition, evidence gathering, logical steps) and a Summary Agent distills conclusions. This addresses "long-chain training collapse" where direct supervision with long reasoning degrades general performance. Progressive reasoning path generation and multi-granularity quality assessment (answer correctness + step coherence) produce training data; iterative DPO stabilizes the Reasoning Agent. Significant gains on challenging multimodal benchmarks requiring complex visual reasoning.

**ChainV** (Zhang et al., arXiv 2025) injects atomic visual hints (pixel coordinates + reliability via Bernoulli process) into reasoning via two-stage selection: coarse patch selection based on previous step, then attention-intensity-weighted atomic hint refinement. Consistency-based evaluation adaptively adjusts self-reflection depth—reducing over-thinking on simple steps. ChainV achieves +2.3% on MathVista within MIMO-VL-RL with 51.4% latency reduction and 24.5% shorter output tokens. Training-free; operates on top of existing models.

**PatchCue** (Qi et al., arXiv 2026) replaces pixel-level bounding boxes and point-based cues with textified patch coordinates—a balance between spatial precision and robustness. A two-stage pipeline: cold-start SFT establishes patch-cue reasoning; RL with process-supervised cue reward guides intermediate steps toward correct visual grounding. The cue reward evaluates whether patch references correctly ground reasoning. PatchCue outperforms pixel-level and point-based baselines across general VQA, complex reasoning, and document understanding.

**Zooming without Zooming** (Wei et al., arXiv 2026) distills inference-time agentic zooming (iterative region cropping and re-processing) into training-time primitives. Region-to-image distillation transfers zooming capability into model weights; at inference, a single forward pass achieves fine-grained perception without tool calls. ZoomBench (845 VQA) evaluates fine-grained multimodal perception. The approach reduces latency and tool dependency while internalizing zooming capability.

---

##### PRM & Process Supervision (4 papers)

These methods use process reward models, critic models, or DPO with process-level signals to improve step-level correctness and faithfulness.

**VisualPRM** (Wang et al., arXiv 2025) introduces an 8B multimodal Process Reward Model trained on VisualPRM400K. Labels are generated via Monte Carlo sampling: for each prefix ending at step k, sample 16 completions and estimate P(correct answer | prefix) via majority voting; label step k correct if P>0.7, incorrect if P<0.3. VisualPRM formulates process supervision as multi-turn chat (sequential step correctness prediction) and supervises all steps. Best-of-N inference scores N candidate chains; achieves +5.9 points on InternVL2.5-78B across 7 benchmarks, outperforming ORM and Self-Consistency. VisualProcessBench (2,866 problems, 26,950 step labels) provides human-annotated evaluation. Inference cost: N× generation + N×T PRM scoring.

**Critic-V** (Zhang et al., CVPR 2025) applies an Actor-Critic paradigm: a Reasoner VLM generates reasoning paths and a separate Critic VLM provides natural-language critiques (e.g., "incorrectly attributed spatial relationship"). The Critic is trained via DPO on preferences ranked by Rule-based Reward (RBR)—evaluating whether critique correctly identifies errors and whether following it leads to correct answers. At inference, the Reasoner iteratively refines based on Critic feedback. Critic-V outperforms GPT-4V on 5 of 8 benchmarks. Natural-language critique provides richer, context-sensitive feedback than binary correct/wrong. Failure mode: critique-induced degradation when Critic gives incorrect guidance.

**Improve VLM CoT** (Zhang et al., ACL 2025) diagnoses that training on short answers (even at scale) fails to generalize to CoT—e.g., 26K ChartQA short-answer training improves CoT by only 0.6 points. A two-stage pipeline: (1) Distillation—GPT-4o generates detailed CoT for 193K examples, SFT on enriched data; (2) DPO—construct positive/negative pairs by comparing model-generated CoT quality against short-answer ground truth. Achieves significant CoT improvements; notably, CoT training also improves direct-answer prediction—teaching general reasoning, not just longer outputs.

**VRPRM** (Chen et al., arXiv 2025) achieves data-efficient process supervision: only 3.6K CoT-PRM SFT + 50K non-CoT PRM RL data surpasses a non-thinking PRM trained on 400K. Stage 1 instills step-level evaluation with visual reasoning; Stage 2 scales via non-CoT RL without expensive CoT annotation. VRPRM achieves up to 118% relative improvement over base model in Best-of-N. The combined strategy demonstrates a new paradigm for PRM training with efficient data utilization. Limitation: 3.6K seed quality is critical; BoN inference cost scales with N.

---

##### RLVR: RL for Visual Reasoning (5 papers)

These methods apply reinforcement learning (GRPO, DPO, iterative SFT-RL) to improve visual reasoning, often with step-level or format rewards to prevent shortcuts.

**R1-VL** (Zhang et al., ICCV 2025) proposes Step-wise Group Relative Policy Optimization (StepGRPO) with two rule-based process rewards: StepRAR (soft key-step matching rewards intermediate reasoning accuracy) and StepRVR (logic evaluation rewards reasoning completeness and consistency). Key steps are extracted automatically from reference solutions; no manual step-level annotation or external tools required. Dense step-level rewards address sparse outcome-only GRPO—reasoning paths receive rewards for correct intermediate steps even if final answer is wrong. R1-VL achieves SOTA across 8 benchmarks (MathVista, ChartQA, TabMWP, CLEVR-Math, GeoQA, etc.) with more stable training dynamics.

**Visionary-R1** (arXiv 2025) mitigates RL shortcuts—models producing short, uninformative reasoning that works on easy training questions but fails to generalize. A structured caption→reason→answer format forces models to interpret images before reasoning, preventing reliance on spurious textual cues. Format reward encourages generating all three sections. Trained on 273K CoT-free QA pairs with GRPO only (no explicit CoT supervision), Visionary-R1 outperforms GPT-4o, Claude 3.5-Sonnet, and Gemini-1.5-Pro on visual reasoning benchmarks.

**OpenVLThinker** (Deng et al., NeurIPS 2025) introduces iterative SFT-RL cycles: SFT surfaces latent reasoning actions and narrows the RL search space; each RL stage refines skills and produces higher-quality SFT data for the next cycle. Addresses two problems: (1) distilling text-only reasoning (DeepSeek R1) into LVLMs via SFT causes visual grounding degradation; (2) pure RL faces overly large search space. OpenVLThinker-7B improves MathVista (+3.8%), EMMA (+2.4%), HallusionBench (+1.6%), and others, competing with GPT-4o and Claude-3.5 on math and perception tasks.

**LLaVA-Critic-R1** (arXiv 2025) challenges the separation between critic and policy: it reorganizes preference-labeled critic datasets into verifiable training signals and applies RL directly to a base generative model. The unified model excels at both evaluation (critic) and generation (policy). The policy achieves +5.7% over Qwen-2.5-VL-7B across 26 benchmarks; LLaVA-Critic-R1+ reaches 71.9 on MMMU at 7B scale. Best-of-128 self-critique at test time yields +13.8% on five reasoning tasks without additional training—a simple path toward scalable, self-improving multimodal systems.

**GThinker** (Zhan et al., arXiv 2025) introduces Cue-Rethinking: inferences are grounded in visual cues and iteratively reinterpreted to resolve inconsistencies. Addresses MLLMs' failure to integrate visual information effectively—over-relying on logic/knowledge-based "slow thinking." A two-stage pipeline: pattern-guided cold start (SFT on cue-rethinking examples) + incentive RL. GThinker-11K (7K iteratively-annotated paths + 4K RL samples) achieves 81.5% on M³CoT, surpassing O4-mini, with 2.1% improvement on general benchmarks while maintaining math performance.

---

##### Faithfulness Analysis & Benchmarks (4 papers)

These works analyze visual faithfulness, provide diagnostic benchmarks, or generate high-quality training data for geometric and general visual reasoning.

**Journey Before Destination** (arXiv 2025) presents the first systematic analysis of visual faithfulness in reasoning chains. Standard evaluations measuring only final-answer accuracy fail to capture whether reasoning is grounded in visual content. The framework decomposes CoT into perception steps (statements about visual content) vs. reasoning steps (logical deductions), uses off-the-shelf VLM judges to evaluate step-level faithfulness (training- and reference-free), and includes human meta-evaluation. A lightweight self-reflection procedure detects unfaithful perception steps and locally regenerates them, improving Unfaithful Perception Rate while preserving answer accuracy.

**R-CoT / TR-CoT** (Deng et al., arXiv 2024) addresses geometric reasoning data scarcity via reverse CoT: instead of question→answer, start from known geometric properties in diagram descriptions, apply theorem-based reasoning to derive measurable properties, then formulate questions targeting those properties. GeoChain (TR-Engine) synthesizes theorem-grounded diagrams with structured textual descriptions; theorem validation ensures correctness. R-CoT-8B achieves up to 16.6% improvement over prior SOTA on MathVista and outperforms GPT-4o by 13% on average. Theorem validation is used at data construction, not inference.

**VisReason** (Li et al., arXiv 2025) introduces a 489K visual CoT dataset spanning four domains with multi-round, human-like rationales. VisReason-Pro (165K) provides expert-level GPT annotations, detailed reasoning traces, and 3D spatial grounding via depth-informed annotations. The dataset addresses scarcity of stepwise visual reasoning data. Fine-tuning Qwen2.5-VL on VisReason and VisReason-Pro yields substantial improvements in step-by-step accuracy, interpretability, and cross-benchmark generalization.

**MIRA** (Zhou et al., arXiv 2025) is a 546-problem benchmark for tasks where generating intermediate visual images (sketches, structural diagrams, path drawings) is essential—mirroring human "drawing to think." Three evaluation levels: direct input (image + question only), text-only CoT (image + thinking prompts), and Visual-CoT (annotated image clues + textual thinking prompts). Key finding: existing MLLMs perform poorly with text-only prompts but improve by 33.7% on average when intermediate visual cues are provided. Pass@k and textual prompt alignment yield only limited improvements compared to Visual-CoT, underscoring the critical role of imagined visual information.

---

#### 4.1.3 Verification Strategies

| Strategy | Mechanism | Representative Works | Strength | Limitation |
|----------|-----------|---------------------|----------|------------|
| **Self-Consistency** | Multiple samples → agreement | CURE, R3V | Simple, no tools | Consistent ≠ correct |
| **Reflection / Self-Correction** | Model critiques and revises own reasoning | R3V, Sherlock, SCL | Can catch obvious errors | May not recognize subtle mistakes |
| **Process Supervision (PRM)** | Step-level scoring by learned model | VisualPRM, VRPRM | Strongest Q1 checkability | PRM may have blind spots; BoN cost |
| **Process Rewards (RL)** | StepRAR, StepRVR, format rewards | R1-VL, Visionary-R1 | Dense rewards, no annotation | Rule-based; domain-dependent |
| **Visual Cues** | Patch coordinates, atomic hints, grounding traces | ChainV, PatchCue, Visual CoT | Explicit grounding | No external verification |
| **Critic Feedback** | Natural-language critique from separate VLM | Critic-V | Richer than scalar rewards | Critic can be wrong; iteration cost |
| **DPO / Preference Learning** | Correct vs. incorrect reasoning pairs | Improve VLM CoT, SCL, GThinker | Calibrates reasoning quality | Noisy CoT degrades DPO (R3V) |
| **Reliability Filtering & Voting** | Estimate cue/step reliability; filter and vote | RTWI | Mitigates noisy thinking | Estimator errors; over-filtering |
| **Contrastive Self-Improvement** | Contrastive VQA pairs; quality via discrimination | VC-STaR | Reduces hallucination | Self-generated rationale errors |
| **Constraint Checking** | Validate against stated rules | — | Catches logical violations | Rules must be explicit |

---

#### 4.1.4 Failure Modes

1. **Plausible-but-Unfaithful Reasoning**
   - Model generates coherent explanation that doesn't reflect actual computation
   - Example: "I see a dog" when image contains a cat, but answer is still correct
   - **CURE**: Acknowledges hallucination in SFT; RLAIF's "Groundedness" criterion cannot truly verify visual grounding
   - **R3V**: Figure 6 shows only 8–70% of correct-answer solutions have fully correct CoT (M3CoT: 8%)
   - **Journey Before Destination**: Reveals disconnect between answer accuracy and step-level visual faithfulness

2. **Consistency-Correctness Gap**
   - Multiple samples agree but are all wrong
   - **CURE**: Consistency metrics (Cf, Cb) measure internal coherence, not truthfulness; even best model shows 30% gap vs. human
   - **R3V**: DPO fails (STaR+DPO ≈ STaR) because positive samples often contain flawed CoT

3. **Reflection and Self-Correction Limitations**
   - Model cannot identify its own errors without explicit training
   - **SCL**: Inference-time self-correction fails without fine-tuning; prompts and external critiques do not improve
   - **Sherlock**: Step-wise self-correction occurs in <10% of cases; even with "aha moments," only ~50% lead to correct answers; Modify One Step causes accuracy to drop to ~25% (random guess)
   - **Critic-V**: Critique-induced degradation—incorrect critiques can revise correct reasoning into wrong

4. **Error Propagation**
   - Early mistakes cascade through CoT
   - **Sherlock**: Trajectory-level correction preserves correct prefix but requires model to identify error point
   - **R3V**: Visual perception errors (e.g., OCR mistakes) propagate; self-refine corrects post-hoc but cannot prevent initial errors
   - **ChainV**: Incorrect patch selection propagates; consistency evaluation may misguide reflection depth

5. **No External Grounding**
   - Cannot verify factual claims about visual content
   - **MIRA**: Text-only CoT and prompts yield limited improvement; 33.7% gain when intermediate visual cues provided
   - **Visual CoT**: Wrong bounding box in Turn 1 silently corrupts all reasoning in Turn 2
   - **LLaVA-CoT**: Caption-Reasoning stage-boundary drift—Reasoning may contradict or ignore Caption

6. **PRM and Reliability Estimator Blind Spots**
   - **VisualPRM, VRPRM**: PRM may assign high scores to plausible-but-wrong steps (PRM hallucination)
   - **RTWI**: Reliability estimator may misclassify; over-filtering removes correct steps; voting may reinforce correlated errors
   - **VRPRM**: 3.6K CoT-PRM seed quality is critical; small dataset may limit domain coverage

7. **RL Shortcuts and Reward Hacking**
   - **Visionary-R1**: Without explicit structure, models produce short, uninformative reasoning that works on easy questions but fails to generalize
   - **R1-VL**: Outcome-only GRPO suffers sparse rewards; step-level rewards improve but rule-based matching has limitations
   - **GThinker**: RL reward design matters; outcome-only rewards may encourage shortcut strategies

8. **Data and Domain Limitations**
   - **CURE**: Limited to everyday scenes (Sherlock-derived); performance on medical, charts, scientific diagrams unknown
   - **VisReason**: 489K/165K scale; generalization to unseen domains uncertain
   - **R-CoT**: Geometric domain; theorem validation at data construction, not inference
   - **VC-STaR**: Self-generated rationales may contain errors; bootstrap instability; VisCoR-55K coverage limits

9. **Structured Output and Visual Cue Limitations**
   - **LLaVA-CoT**: Hallucinated Caption as reasoning foundation—if Caption misidentifies (e.g., wrong color, miscount), Reasoning builds on false foundation
   - **ChainV**: Incorrect patch selection may target visually salient but semantically irrelevant regions; Bernoulli stochastic process causes variance across runs
   - **PatchCue**: Process-supervised cue reward could be gamed if reward model has blind spots; patch representation may not generalize to all spatial reasoning
   - **Zooming without Zooming**: Distillation may not perfectly transfer zooming capability; without explicit region output, cannot verify which regions were attended

10. **Iterative and Multi-Turn Overhead**
    - **Critic-V**: Multi-turn Reasoner-Critic loop increases inference cost; each refinement requires full generation
    - **R3V**: Test-time self-selection (N=3) ≈ 4× cost of Test@1; plateaus at large N due to input length limits
    - **VisualPRM**: BoN with N=16 and T=10 steps ≈ 160× more expensive than greedy decoding
    - **LLaVA-Critic-R1**: Best-of-128 yields +13.8% but requires 128× generation + 128× critic scoring

---

#### 4.1.5 Design Trade-offs Across Subcategories

| Subcategory | Data Efficiency | Inference Cost | Verifiability | Key Trade-off |
|-------------|-----------------|----------------|---------------|----------------|
| **Consistency & Self-Correction** | High (R3V: QA only; Sherlock: 20k) | Low–Medium (R3V test-time selection adds cost) | Low–Medium | Consistency ≠ correctness; self-correction requires training |
| **Structured Stages & Visual CoT** | Medium (LLaVA-CoT: 100k; VisReason: 489k) | Low–Medium (SWIRES, multi-turn add cost) | Medium | Stage-boundary drift; wrong bbox corrupts reasoning |
| **PRM & Process Supervision** | Low–High (VRPRM: 3.6k+50k; VisualPRM: 400k) | High (BoN: N× generation + PRM scoring) | Medium–High | PRM blind spots; BoN cost prohibitive for real-time |
| **RLVR** | High (Visionary-R1: 273k CoT-free; GThinker: 11k) | Low (single pass) | Medium | RL shortcuts; reward design critical |
| **Faithfulness & Benchmarks** | N/A (evaluation/data) | Varies | Diagnostic | MIRA: 33.7% gap between text-only and Visual-CoT |

**Emerging Patterns**: (1) Process-level supervision (PRM, step rewards) consistently outperforms outcome-only training; (2) structured output formats (caption→reason→answer, four-stage) prevent shortcuts; (3) self-improvement and contrastive bootstrap reduce annotation cost; (4) test-time scaling (BoN, self-selection) provides accuracy/cost trade-off without retraining.

**Summary of 25 Papers by Subcategory**:

| Subcategory | Papers | Key Verification Mechanism |
|-------------|--------|---------------------------|
| Consistency & Self-Correction | CURE, R3V, Sherlock, SCL, RTWI, VC-STaR | Consistency metrics, self-refine/select, trajectory correction, reliability filtering, contrastive bootstrap |
| Structured Stages & Visual CoT | LLaVA-CoT, Visual CoT, Insight-V, ChainV, PatchCue, Zooming w/o Zooming | Four-stage pipeline, bbox grounding, multi-agent, atomic hints, patch cues, region distillation |
| PRM & Process Supervision | VisualPRM, Critic-V, Improve VLM CoT, VRPRM | Step-level PRM, natural-language critique, DPO+distillation, data-efficient PRM |
| RLVR | R1-VL, Visionary-R1, OpenVLThinker, LLaVA-Critic-R1, GThinker | StepGRPO, format reward, SFT-RL cycles, critic-as-policy, cue-rethinking |
| Faithfulness & Benchmarks | Journey Before Destination, R-CoT/TR-CoT, VisReason, MIRA | Perception/reasoning decomposition, reverse CoT, large-scale CoT data, visualization-essential benchmark |

**Key Datasets and Benchmarks Introduced**:

| Name | Size | Source | Purpose |
|------|------|--------|---------|
| CURE | 1,622 | Sherlock-derived | Consistency + reasoning evaluation |
| LLaVA-CoT-100k | 100K | Multi-source VQA | Four-stage CoT training |
| Visual CoT | 438K (98K with full CoT) | 11 source datasets | Bbox grounding + reasoning |
| VisualPRM400K | 400K | MC sampling | PRM training |
| VisualProcessBench | 2,866 problems, 26,950 steps | Human annotation | PRM evaluation |
| VisCoR-55K | 55K | Generated | Contrastive VQA self-improvement |
| VisReason | 489K (165K Pro) | Four domains | Large-scale visual CoT |
| GThinker-11K | 7K + 4K RL | Iterative annotation | Cue-rethinking |
| ZoomBench | 845 | — | Fine-grained perception |
| MIRA | 546 | — | Visualization-essential reasoning |
| JourneyBench | — | — | Visual faithfulness evaluation |

---

#### 4.1.6 When to Use Quadrant I

**Appropriate**:
- Low-stakes applications (entertainment, casual QA)
- Closed-world tasks with clear rules
- Settings where tool use is impossible or prohibited
- Rapid prototyping before adding verification
- Resource-constrained deployment (low latency, no API costs)
- When human-readable explanations are sufficient

**Not Appropriate**:
- Safety-critical domains (medical, legal)
- Open-world reasoning requiring factual verification
- Tasks demanding step-level auditability
- When intermediate visual grounding must be externally verified
- High-stakes decisions requiring reproducibility

**Selection Guidance by Subcategory**:
- **Consistency & Self-Correction**: Choose when annotation budget is limited (R3V, Sherlock) or noisy CoT is a concern (RTWI, VC-STaR). R3V for self-training from QA only; Sherlock for trajectory-level correction with minimal data.
- **Structured Stages & Visual CoT**: Choose when interpretability and grounding are priorities. LLaVA-CoT for general reasoning; ChainV or PatchCue for efficiency; Zooming w/o Zooming when fine-grained perception is needed without tools.
- **PRM & Process Supervision**: Choose when step-level quality matters and inference cost is acceptable. VRPRM for data efficiency; VisualPRM for strongest BoN gains; Critic-V when natural-language feedback is preferred.
- **RLVR**: Choose when CoT annotations are scarce (Visionary-R1: CoT-free) or iterative improvement is desired (OpenVLThinker). R1-VL for dense process rewards; GThinker for cue-grounded reasoning; LLaVA-Critic-R1 for unified critic-policy with test-time scaling.
- **Faithfulness & Benchmarks**: Use Journey Before Destination for faithfulness evaluation; MIRA for visualization-essential tasks; VisReason for large-scale CoT training; R-CoT for geometric reasoning data.

**Comparison with Other Quadrants**: Quadrant I offers the lowest deployment complexity—no tool APIs, no execution sandbox, no structured trace parsers. Moving to Quadrant II (tools) adds external grounding but tool latency and failure modes. Quadrant III (structured traces) enables automatic verification but requires schema design. Quadrant IV (executable + tools) provides highest verifiability at highest cost. For many applications, Quadrant I with process supervision (PRM, step rewards) or structured outputs (LLaVA-CoT, Visionary-R1) offers a practical middle ground.

---

### 4.2 Quadrant II: Text + Tools (ReAct-style)

**Definition**: Methods that combine textual planning with tool calls in Action/Observation loops.

#### 4.2.1 Approach Overview

Quadrant II methods extend text-only CoT by introducing **tools** that provide external evidence. The reasoning trace follows the ReAct pattern (Yao et al., 2023):
- **Thought**: Reasoning about what to do next
- **Action**: Tool selection and parameters
- **Observation**: Tool output (evidence)
- **Loop**: Repeat until answer can be produced

**Relation to ReAct**: ReAct was originally developed for text-only settings; Quadrant II generalizes it to multimodal inputs. MM-REACT (Yang et al., 2023) pioneered this extension by serializing visual inputs into text so a text-only LLM could coordinate vision tools. Subsequent work has explored memory-augmented loops (VideoAgent, DoraemonGPT), hierarchical orchestration (HAMMR), RL-based tool learning (AdaReasoner, ToolRL, VISTA-R1), and domain-specific tool sets (ChartAgent, VisRAG, OmniParser).

**Why Tools?** Tools address Quadrant I's key limitation—lack of external grounding. By calling detectors, OCR, search engines, GUI parsers, or other tools, the model can:
- Verify visual claims ("Is there really a dog there?")
- Access external knowledge ("What species is this?")
- Perform precise computations ("Count the objects")
- Maintain memory across steps
- Ground actions to specific screen regions (web, desktop, mobile)

#### 4.2.2 Representative Works

Representative works are organized by subcategory below.

##### Foundational ReAct-style (3 works)

**MM-REACT** (Yang et al., arXiv 2023) pioneers multimodal ReAct by integrating ChatGPT with a pool of vision specialists (BLIP-2, Azure Computer Vision, OCR, celebrity recognition, object detection). The system serializes visual inputs into text—image descriptions, textualized spatial coordinates (e.g., "bounding box [100, 200, 300, 400]"), and file path references—so a text-only LLM can coordinate vision tools without direct pixel access. MM-REACT demonstrates zero-shot capabilities on complex visual tasks that dedicated VLMs struggle with: identifying celebrities in photos, reading nested text in receipts via OCR + spatial reasoning, planning image editing actions, and answering multi-image questions. The modular design allows adding new experts without retraining the reasoning model, establishing the template for subsequent multimodal tool-augmented reasoning.

**VideoAgent** (Fan et al., ECCV 2024) introduces a memory-augmented multimodal agent for long-form video understanding. It constructs dual-component structured memory: temporal memory stores segment-level captions with ViCLIP features and caption embeddings in a searchable table; object memory maintains an SQL database with object IDs, categories, segment indices, and CLIP features for re-identification across frames. Four tools—caption retrieval, segment localization, VQA, and object memory querying—enable the LLM to interactively gather evidence. VideoAgent achieves +6.6% on NExT-QA and +26.0% on EgoSchema over baselines, demonstrating that minimal but sufficient tool design centered on memory querying outperforms larger tool collections. Limitations include tool failures (false negatives in detection) propagating to the final answer and occasional tool misuse (Fan et al., 2024).

**DoraemonGPT** (Yang et al., ICML 2024) extends video understanding with MCTS-based planning and symbolic memory. The video is pre-processed into space-dominant memory (object instances with attributes, queryable by SQL) and time-dominant memory (frame/clip-level temporal structure). Sub-task tools internally generate SQL to query this memory; the main LLM receives natural language results (e.g., "The person enters at segment 12-15") rather than raw SQL. An LLM-driven MCTS planner explores multiple solution paths, backpropagates rewards, and aggregates evidence into improved answers—going beyond greedy sequential tool selection. DoraemonGPT outperforms sequential tool loops on Ego4D NLQ, MSVD-QA, and NExT-QA, but incurs significantly higher cost from MCTS node expansion (each node requires an LLM call and potential tool execution) (Yang et al., 2024).

##### Dynamic Tool Orchestration (4 works)

**AdaReasoner** (Song et al., ICLR 2026) proposes Tool-GRPO, a reinforcement learning algorithm for adaptive tool selection across seven task types (VSP, Jigsaw, etc.). The model uses seven core visual tools—POINT (object localization), DRAW2DPATH, ASTAR (pathfinding), DETECTBLACKAREA, INSERTIMAGE, CROP, OCR—and learns to autonomously adopt beneficial tools, suppress irrelevant ones, and modulate tool-use frequency via end-task success feedback. A scalable data curation pipeline synthesizes multi-turn trajectories with reflection/backtracking and explicit tool failure cases. AdaReasoner achieves +24.9% average improvement on a 7B base model, surpassing GPT-5 on structured reasoning tasks (VSP: 96.60% vs. 80.10%, Jigsaw: 88.60% vs. 84.50%), with emergent behaviors like adopting POINT over DETECTBLACKAREA when beneficial (Song et al., 2026).

**HAMMR** (Castrejon et al., NeurIPS 2024 WS) introduces hierarchical multimodal ReAct for generic VQA. A top-level LLM+tools agent calls specialized sub-agents—counting agent (object detector + counter), OCR agent, spatial reasoning agent (relative position classifier), external knowledge agent (Google Lens, web search)—each with curated tool subsets. The key insight is that naively combining all tools for a single generic VQA system performs poorly; hierarchical compositionality is essential. HAMMR outperforms naive LLM+all-tools by 19.5% and PaLI-X by 5.0% on a diverse VQA suite spanning counting, spatial reasoning, OCR, visual pointing, and external knowledge (Castrejon et al., 2024).

**OctoTools** (Lu et al., ICLR 2025 WS) presents a training-free, extensible agentic framework with standardized **tool cards**—metadata encapsulating tool name, description, use cases, I/O format, and examples—enabling zero-shot integration of any new tool without modifying the planner. A planner governs high-level task decomposition and low-level step-by-step execution; an executor instantiates tool calls and saves structured intermediate results (JSON-like records). OctoTools achieves 9.3% average gains over GPT-4o across 16 diverse benchmarks (math, medicine, science, GAIA) and outperforms AutoGen, GPT-Functions, and LangChain when given equivalent tools (Lu et al., 2025).

**ToolRL** (Qian et al., arXiv 2025) provides the first comprehensive study of reward design for tool-selection training via GRPO. The authors systematically explore reward strategies across four dimensions: type (what to reward), scale (magnitude), granularity (detail level), and temporal dynamics. Key findings: longer reasoning traces are not inherently better; dynamic reward scaling aids learning transitions; fine-grained reward decomposition (format reward × (tool reward + accuracy reward)) leads to more stable training. ToolRL achieves +17% over base models and +15% over SFT across BFCL, Bamboogle, and API-Bank, with emergent proactiveness and metacognitive reasoning (Qian et al., 2025).

##### Web & GUI Agents (5 works)

**WebVoyager** (He et al., ACL 2024) builds an end-to-end web agent with GPT-4V, processing screenshots and web element text in a ReAct loop: observe current webpage screenshot → reason about what action to take → execute browser action (click, type, scroll, open URL) → observe new state. It introduces the first benchmark evaluating multimodal web agents on real, live websites (not cached/simulated) across 15 popular domains (Google, Amazon, GitHub, Wolfram Alpha, etc.) with 643 tasks. WebVoyager achieves 59.1% task success (vs. 27.8% text-only GPT-4), demonstrating that combining visual screenshot perception with HTML text enables significantly better web task completion. A GPT-4V-based automatic evaluator achieves 85.3% agreement with human judgment. Failure modes include layout misidentification on complex pages (dense grids, multi-column tables) and prompt injection risk from malicious content (He et al., 2024).

**SeeAct** (Zheng et al., ICML 2024) demonstrates that GPT-4V is a generalist web agent when grounded. The two-stage pipeline: (1) "See" phase—model visually perceives a webpage screenshot and generates a textual description of the needed action; (2) "Act" phase—a grounding module maps that description to a concrete HTML element and action. SeeAct achieves 51.1% task success on live websites when grounding is performed manually (oracle), demonstrating strong visual understanding. The paper systematically evaluates three grounding strategies (Element Attributes, Image Annotation, Textual Choices) and finds that combining HTML structure with visual context provides the best automatic grounding—though a substantial gap to oracle remains (~21 points). This exposes **grounding as the key bottleneck** for web agents: textual reasoning is correct but text→element mapping fails (Zheng et al., 2024).

**AssistGUI** (Gao et al., CVPR 2024) targets desktop GUI automation for complex PC software (After Effects, MS Word, Excel, PowerPoint). The benchmark contains 100 tasks across 9 Windows applications with reference video demonstrations. An Actor-Critic framework employs four components: a Planner (decomposes tasks into sub-steps), a GUI Parser (LLM-driven visual tool that converts screenshots to structural text), a Critic (assesses previous actions and guides correction), and an Actor (generates keyboard/mouse commands). The Critic provides explicit error detection and correction guidance—a primitive verification mechanism within the plan-execute loop. The best system achieves 46% success, highlighting substantial challenges in complex procedural GUI automation (Gao et al., 2024).

**CogAgent** (Hong et al., CVPR 2024) is an 18B-parameter VLM for GUI agents with a dual-resolution architecture: a low-resolution encoder (224×224) for semantic understanding and a high-resolution encoder (1120×1120) for precise GUI element recognition. This cross-attention mechanism enables recognition of tiny text and interface elements from screenshots alone. CogAgent achieves SOTA on 9 VQA benchmarks and outperforms LLM-based methods that consume HTML text on both PC (Mind2Web) and Android (AITW) GUI navigation tasks.

**OmniParser** (Lu et al., arXiv 2024) provides GUI screen parsing as a grounding tool for pure vision-based GUI agents. Two fine-tuned specialized models: a detection model (identifies interactable regions from 67k screenshots, trained on DOM-derived bounding boxes) and a caption model (extracts functional semantics from 7k icon-description pairs). OmniParser significantly improves GPT-4V's performance on ScreenSpot benchmark and outperforms GPT-4V baselines on Mind2Web and AITW using only screenshot input—without DOM trees or view hierarchies. The structured parsing with local semantics (icon descriptions + OCR text) improves bounding box ID assignment accuracy from 70.5% to 93.8%, enabling cross-platform GUI agents (web, mobile, desktop) (Lu et al., 2024).

##### Domain-Specific Agents (4 works)

**Optimus-1** (Li et al., NeurIPS 2024) addresses long-horizon tasks in open worlds (e.g., Minecraft) with hybrid multimodal memory. The memory consists of (1) Hierarchical Directed Knowledge Graph (HDKG)—transforms world knowledge (crafting recipes, object relationships) into explicit graph structures for efficient retrieval via topological sorting; (2) Abstracted Multimodal Experience Pool (AMEP)—summarizes historical task execution (video frames, environment state, plans, success/failure cases) for in-context learning. Built on this memory, agents feature a Knowledge-Guided Planner (incorporates HDKG), Experience-Driven Reflector (retrieves AMEP for COMPLETE/CONTINUE/REPLAN decisions), and Action Controller (low-level mouse/keyboard via STEVE-1). Optimus-1 achieves up to 30% improvement over existing agents and near human-level performance on many Minecraft tasks (98.60% on Wood tasks; human: 100%) (Li et al., 2024).

**VisRAG** (Yu et al., ICLR 2025) introduces VLM-based visual page retrieval for document RAG, eliminating information loss from traditional text parsing. Document pages are embedded as images using VLM hidden states with position-weighted mean pooling, preserving layout, figures, and visual formatting. VisRAG-Ret (dual-encoder retriever) and VisRAG-Gen (generator with page concatenation) handle multi-page documents. VisRAG achieves 20–40% end-to-end gains over text-based RAG, with stronger grounding from direct visual evidence and better training data efficiency (Yu et al., 2025).

**ChartAgent** (Wang et al., arXiv 2025) proposes Tool-Integrated Reasoning (TIR) for chart understanding with 14+ specialized tools (OCR, instance segmentation, key element detection, auxiliary line projection, color matching, numerical calculation, data structuring, relational reasoning). A "Think-Observe-Execute-Reflect" loop dynamically orchestrates tools based on query requirements; all intermediate outputs are consolidated into a structured Evidence Package. ChartAgent achieves SOTA on ChartBench and ChartX, outperforming prior methods by up to 17.31% on unannotated, numerically intensive queries while providing traceable and reproducible reasoning chains.

**LongVideoAgent** (Liu et al., arXiv 2025) tackles hour-long video QA with a Master-Grounding-Vision three-layer multi-agent system. The Master Agent orchestrates reasoning with bounded iterative loops (max K steps) and step limits; the Grounding Agent localizes question-relevant segments via subtitle similarity search; the Vision Agent extracts targeted textual observations and fine-grained visual details from localized frames. Trained with GRPO for correctness, conciseness, and efficiency, LongVideoAgent achieves SOTA on LongTVQA and LongTVQA+ benchmarks, significantly outperforming non-agent baselines and demonstrating that RL strengthens reasoning and planning capabilities.

##### Agentic RL & Verification (3 works)

**VISTA-R1** (Lu et al., arXiv 2025) introduces VISTA-Gym, a scalable training environment for tool-integrated visual reasoning that unifies 7 tasks from 13 datasets with standardized visual tool interfaces, executable interaction loops, verifiable feedback signals, and efficient trajectory logging. VISTA-R1 is trained via multi-turn trajectory sampling and end-to-end RL to interleave tool-use with agentic reasoning, addressing VLMs' struggle with tool selection, invocation, and coordination. VISTA-R1-8B outperforms state-of-the-art baselines of similar size by 9.51%–18.72% across 11 public reasoning-intensive VQA benchmarks.

**OpenThinkIMG** (Su et al., arXiv 2025) presents the first open-source, comprehensive end-to-end framework for tool-augmented LVLMs. It features standardized vision tool interfaces, scalable trajectory generation for policy initialization, and a flexible training environment. V-ToolRL trains LVLMs to learn adaptive policies for invoking external vision tools via RL feedback—enabling autonomous discovery of optimal tool-usage strategies. On chart reasoning tasks, the RL-trained agent (Qwen2-VL-2B) outperforms its SFT-initialized counterpart by +28.83 points, surpasses Taco and CogCom by +12.7 on average, and exceeds GPT-4.1 by +8.68 accuracy points.

**Sherlock Workflow** (Ro et al., arXiv 2025) addresses reliable agentic workflow execution with selective verification and speculative execution. Agentic workflows compose multiple LLM calls with tools, retrieval, and reasoning steps, but are inherently error-prone. Sherlock uses counterfactual fault-injection analysis to identify error-prone nodes, a learned verifier selector (GRPO on preference data) for cost-optimal placement, and speculative execution that overlaps verification with downstream computation—rolling back when verification fails. Compared to non-verifying baseline, Sherlock delivers 18.3% accuracy gain on average, reduces execution time by up to 48.7%, and lowers verification cost by 26.0% versus Monte Carlo search (Ro et al., 2025).

*Summary*: The 19 Representative Works span five subcategories: foundational ReAct (MM-REACT, VideoAgent, DoraemonGPT), dynamic tool orchestration (AdaReasoner, HAMMR, OctoTools, ToolRL), web and GUI agents (WebVoyager, SeeAct, AssistGUI, CogAgent, OmniParser), domain-specific agents (Optimus-1, VisRAG, ChartAgent, LongVideoAgent), and agentic RL & verification (VISTA-R1, OpenThinkIMG, Sherlock Workflow). Together they illustrate the evolution from zero-shot prompting (MM-REACT) through memory-augmented and hierarchical designs to RL-trained adaptive tool use and speculative verification.

#### 4.2.3 Verification Strategies

| Strategy | Mechanism | Representative Work | Strength | Limitation |
|----------|-----------|---------------------|----------|------------|
| **Tool Output Validation** | Check tool confidence/scores | VideoAgent, ChartAgent | Quantitative evidence | Tools can be overconfident |
| **Cross-Tool Consistency** | Multiple tools verify same claim | HAMMR, ChartAgent | Reduces single-tool failures | Requires tool redundancy |
| **Trajectory Audit** | Review action-observation log | VideoAgent, DoraemonGPT | Full trace is inspectable | Requires human/model reviewer |
| **Temporal Consistency** | Check observations across time | VideoAgent, LongVideoAgent | Catches transient errors | May miss systematic issues |
| **Evidence Package** | Structured consolidation of tool outputs | ChartAgent | Explicit audit trail | Domain-specific design |
| **Selective Verification** | Fault-injection + verifier placement | Sherlock Workflow | Cost-optimal accuracy | Requires onboarding data |
| **Speculative Execution** | Overlap verification with downstream | Sherlock Workflow | Masks verifier latency | Rollback overhead on failure |
| **RL Reward Design** | Format + correctness + tool rewards | AdaReasoner, ToolRL, VISTA-R1 | Learns optimal tool use | Reward design is critical |

**Discussion**: Verification in Quadrant II is inherently partial. Tool outputs provide quantitative evidence but tools can be overconfident; trajectory audit requires human or model reviewers; cross-tool consistency requires redundant tools. Recent work addresses these limits: ChartAgent's Evidence Package consolidates tool outputs into a structured audit trail; Sherlock Workflow uses fault-injection to identify error-prone nodes and selective verification to balance cost and accuracy; AdaReasoner and ToolRL show that RL reward design can learn when and how to invoke tools reliably.

#### 4.2.4 Tool Categories in Multimodal Reasoning

| Category | Tools | Use Cases | Representative Work |
|----------|-------|-----------|----------------------|
| **Perception** | Object detectors, OCR, segmentation, depth estimation | Ground claims to visual evidence | MM-REACT, VideoAgent, ChartAgent |
| **Computation** | Calculators, code interpreters | Verify numerical reasoning | OctoTools, ToolRL |
| **Retrieval** | Search engines, knowledge bases, VLM-based document retrieval | Fact-check claims, document RAG | MM-REACT, VisRAG, HAMMR |
| **Memory** | Vector databases, key-value stores, symbolic SQL memory | Maintain context across steps | VideoAgent, DoraemonGPT, Optimus-1 |
| **GUI Tools** | Screen parsers, element detection, icon captioning | Ground actions to screen regions | OmniParser, AssistGUI, CogAgent |
| **Video Grounding** | Segment localization, subtitle search, object tracking | Temporal localization in video | VideoAgent, LongVideoAgent, DoraemonGPT |
| **Specialist** | Medical analyzers, chart parsers, equation solvers | Domain-specific verification | ChartAgent, OctoTools |

**Tool Design Principles**: Several principles emerge from the Representative Works. *Minimal but sufficient*: VideoAgent demonstrates that four tools centered on memory querying outperform larger tool collections. *Standardization*: OctoTools' tool cards and AdaReasoner's tool name/parameter randomization enable zero-shot generalization to unseen tools. *Hierarchical specialization*: HAMMR shows that task-specific sub-agents with curated tool subsets outperform monolithic agents. *Structured outputs*: ChartAgent's Evidence Package and DoraemonGPT's SQL-queryable memory provide explicit audit trails for verification.

**Tool Selection and Orchestration Strategies**: The Representative Works illustrate four orchestration paradigms. (1) *Sequential ReAct*: MM-REACT, VideoAgent, WebVoyager—greedy Thought→Action→Observation loops; simple but prone to tool misuse. (2) *Hierarchical routing*: HAMMR—top-level agent delegates to specialized sub-agents; reduces tool overload but adds latency. (3) *Search-based planning*: DoraemonGPT—MCTS explores multiple paths, backpropagates rewards; higher quality but higher cost. (4) *RL-learned policies*: AdaReasoner, ToolRL, VISTA-R1, OpenThinkIMG, LongVideoAgent—end-task or process rewards train adaptive tool selection; requires training but generalizes better. The choice depends on task complexity, latency budget, and availability of training data.

#### 4.2.5 Failure Modes

Quadrant II methods introduce failure modes beyond Quadrant I's plausible-but-unfaithful reasoning. The following taxonomy, with representative paper citations, summarizes observed limitations.

1. **Tool Misuse**
   - Calling wrong tool for the task; incorrect tool parameters; using general tools when specialized ones are needed.
   - *VideoAgent*: Occasional tool misuse (calling wrong tool for task) propagated to final answer (Fan et al., 2024).
   - *HAMMR*: Top-level agent may selectively weight sub-agent outputs, ignoring valid evidence; spatial sub-agent returns "left" but top-level agent says "right" (Castrejon et al., 2024).
   - *AssistGUI*: Complex GUIs (e.g., After Effects timeline) have many overlapping elements that the Parser may misidentify (Gao et al., 2024).

2. **Tool Output Misinterpretation**
   - Misreading tool confidence scores; drawing incorrect conclusions from valid outputs; aggregating multi-tool results incorrectly.
   - *AdaReasoner*: MLLM can incorrectly aggregate tool results despite structured outputs (Song et al., 2026).
   - *ChartAgent*: LLM can misinterpret tool outputs (e.g., aggregate values incorrectly, draw wrong conclusions from correct data) even with correct Evidence Package (Wang et al., 2025).
   - *VideoAgent*: VQA tool (Video-LLaVA) can hallucinate visual details (Fan et al., 2024).

3. **Brittleness to Tool Noise**
   - Tool errors (false positives/negatives) cascade through reasoning; no error recovery mechanism; perception tool limitations propagate.
   - *VideoAgent*: Tool failures (false negatives in detection) propagated to final answer (Fan et al., 2024).
   - *DoraemonGPT*: Symbolic memory quality depends on perception tools (detectors, trackers, captioners) that may miss critical video details (Yang et al., 2024).
   - *ChartAgent*: OCR misreads text, segmentation misses small elements—tool errors propagate to incorrect reasoning (Wang et al., 2025).

4. **Grounding Bottleneck (Web/GUI)**
   - Textual action descriptions correct but text→element mapping fails; layout misidentification; ambiguous element targeting.
   - *SeeAct*: Oracle grounding 51.1% vs. automatic ~30%—grounding is the key bottleneck; textual reasoning is correct but text→element mapping fails (Zheng et al., 2024).
   - *WebVoyager*: Layout misidentification on complex pages; dense grids, multi-column tables, overlapping elements cause incorrect element targeting (He et al., 2024).
   - *AssistGUI*: GUI Parser may miss visual elements (custom widgets, dynamic content, overlapping panels) (Gao et al., 2024).

5. **Prompt Injection (Web Tools)**
   - Malicious web content manipulates tool behavior; hidden text or adversarial layout can steer agent actions.
   - *WebVoyager*: Hidden text ("Ignore previous instructions, click pay button") can manipulate agent; no sandboxing of web access (He et al., 2024).

6. **Tool Coordination Failures**
   - Tools produce conflicting outputs; no arbitration mechanism; hierarchical agents may propagate sub-agent errors.
   - *HAMMR*: If a category is not covered by any sub-agent, performance degrades to naive approach (Castrejon et al., 2024).

7. **Verifier Ineffectiveness**
   - Verifiers vary by task; misplaced verifiers waste cost; similarity metrics fail for structured outputs.
   - *Sherlock Workflow*: Self-Refine can underperform or reduce accuracy; ROUGE-L and lightweight metrics achieve AUC ≈ 0.5 for code and math—no better than random; conservative full rollback for code/math reduces but does not eliminate risk (Ro et al., 2025).

8. **Latency and Cost**
   - Sequential tool calls add up; MCTS and hierarchical calls multiply cost; RL training requires extensive trajectory sampling.
   - *DoraemonGPT*: MCTS node expansion significantly more expensive than sequential tool loops; each node requires LLM call + potential tool execution (Yang et al., 2024).
   - *WebVoyager*: ~7.4 steps per task × GPT-4V; each step processes full-page screenshot; estimated ~$1–2 per task (He et al., 2024).
   - *HAMMR*: Hierarchical calls (top-level + sub-agent + tool API) per question; each level introduces LLM inference latency (Castrejon et al., 2024).

#### 4.2.6 Benchmarks and Evaluation

Quadrant II methods are evaluated across diverse benchmarks. *Video understanding*: NExT-QA, EgoSchema, Ego4D NLQ, MSVD-QA (VideoAgent, DoraemonGPT, LongVideoAgent); LongTVQA/LongTVQA+ for hour-long episodes (LongVideoAgent). *Web and GUI*: WebVoyager benchmark (15 real websites, 643 tasks); Mind2Web (PC), AITW (Android), ScreenSpot (WebVoyager, SeeAct, CogAgent, OmniParser); AssistGUI benchmark (100 tasks, 9 Windows applications). *Chart and document*: ChartBench, ChartX (ChartAgent); document RAG benchmarks (VisRAG). *General VQA*: Diverse suites spanning counting, spatial reasoning, OCR, external knowledge (HAMMR); VSP, Jigsaw, VStar (AdaReasoner). *Tool learning*: BFCL, Bamboogle, API-Bank (ToolRL); VISTA-Gym (7 tasks, 13 datasets) (VISTA-R1). *Workflow*: CoTCollection, OMEGA, LiveCodeBench (Sherlock Workflow). Evaluation protocols vary: task success rate (WebVoyager, AssistGUI), accuracy on QA benchmarks (VideoAgent, ChartAgent), and automatic evaluators (GPT-4V-based for WebVoyager with 85.3% human agreement).

#### 4.2.7 When to Use Quadrant II

**Appropriate**:
- Tasks requiring factual verification
- Multi-hop reasoning needing information integration
- Settings where tool APIs are available and reliable
- Applications needing moderate verifiability
- Web, desktop, or mobile GUI automation
- Long-form video/document understanding

**Not Appropriate**:
- Real-time applications with strict latency requirements
- Environments where tools are unavailable or unreliable
- Security-sensitive settings (web access risks)
- When structured traces are required for compliance

**Selection Guidance by Subcategory**:
- **Foundational ReAct**: MM-REACT for zero-shot vision tool orchestration; VideoAgent for video QA with memory; DoraemonGPT when exploration over multiple paths justifies MCTS cost.
- **Dynamic Orchestration**: AdaReasoner for adaptive tool selection across task types; HAMMR for hierarchical VQA; OctoTools for extensible, training-free frameworks; ToolRL for reward design in tool learning.
- **Web & GUI**: WebVoyager for end-to-end web tasks; SeeAct when grounding bottleneck is the research focus; AssistGUI for desktop automation; CogAgent for high-res GUI understanding; OmniParser as grounding tool for any GUI agent.
- **Domain-Specific**: Optimus-1 for Minecraft-style long-horizon; VisRAG for document RAG; ChartAgent for chart reasoning with Evidence Package; LongVideoAgent for hour-long video QA.
- **Agentic RL & Verification**: VISTA-R1 and OpenThinkIMG for RL-based tool-integrated VLMs; Sherlock Workflow when selective verification and speculative execution are needed.

**Comparison with Other Quadrants**: Quadrant II adds external grounding via tools but introduces tool latency, misuse, and output misinterpretation. Quadrant III (structured traces) enables automatic verification without tool dependencies. Quadrant IV (executable + tools) provides highest verifiability at highest cost. For many applications, Quadrant II with RL-trained tool use (AdaReasoner, VISTA-R1) or selective verification (Sherlock Workflow) offers a practical balance.

**Design Trade-offs**: Several design dimensions emerge from the Representative Works. *Memory vs. computation*: VideoAgent and DoraemonGPT pre-compute structured memory (temporal + object) to reduce inference-time tool calls, at the cost of memory construction; LongVideoAgent uses on-demand grounding. *Hierarchy vs. flat*: HAMMR shows hierarchical sub-agents outperform monolithic tool access; OctoTools uses a flat tool registry with tool cards. *RL vs. zero-shot*: AdaReasoner, ToolRL, VISTA-R1, OpenThinkIMG, and LongVideoAgent demonstrate that RL-based tool learning substantially outperforms SFT or zero-shot prompting for adaptive tool selection. *Verification overhead*: Sherlock Workflow addresses the cost-accuracy trade-off via selective verification and speculative execution; ChartAgent's Evidence Package provides auditability without runtime verification.

---

### 4.3 Quadrant III: Structured w/o Tools

**Definition**: Methods that use structured intermediate representations without external tool execution.

#### 4.3.1 Approach Overview

Quadrant III methods address a key limitation of Quadrants I and II: **textual reasoning is not automatically checkable**. By using structured traces—tables, graphs, programs, state logs, or latent representations—these methods enable:
- **Schema validation**: Does the structure conform to expected format?
- **Constraint checking**: Are relationships logically consistent?
- **Alignment verification**: Does structure match the visual input?
- **Replayability**: Same structure → same interpretation

**Why Structure Without Tools?** Quadrant III occupies an interesting middle ground:
- More verifiable than text-only (Quadrant I)
- No tool dependencies or latency (unlike Quadrant II)
- Enables automatic checks while remaining self-contained
- Useful when tools are unavailable but checkability is needed

**Interpretability Spectrum**. A central design trade-off in Quadrant III is the spectrum from human-readable structure to opaque latent representations. At the **highest interpretability** end, CCoT and LLaVA-SG produce explicit scene graphs with (subject, predicate, object) triples that humans can inspect and verify. CoVT occupies the **medium** range: ~20 continuous visual tokens encoding depth, segmentation, and edges can be optionally decoded to dense predictions for partial inspection. DMLR offers **partial** interpretability via its Dynamic Visual Injection log—which image regions were attended at each step is checkable, though latent refinements remain opaque. LaRe provides **low** interpretability: visual refocusing steps indicate attended regions but latent states between steps are uninterpretable. MCOUT anchors the **lowest** end: continuous latent thought vectors are entirely opaque, with no intermediate artifact to inspect when reasoning fails. This spectrum informs method selection: high-stakes applications favor CCoT/LLaVA-SG; efficiency-critical settings may accept MCOUT's opacity for its reasoning gains.

#### 4.3.2 Representative Works by Subcategory

**Scene Graph Methods (4 papers)**. These methods use scene graphs as structured intermediate representations for visual reasoning.

**CCoT** (CVPR 2024) proposes compositional chain-of-thought prompting that generates a scene graph as an intermediate step before answering. The LMM produces (entity, attribute, relation) triples in a two-stage pipeline: first generate the scene graph, then feed it as structured context to produce the final answer. Zero-shot and training-free, CCoT improves compositional VQA across GPT-4V, LLaVA, and InstructBLIP on SeedBench, MMBench, and Winoground. **LLaVA-SG** (arXiv 2024) integrates a Scene Graph Expression (SGE) module into the LLaVA framework, converting ViT patch features into a semantically structured graph with object nodes and relationship edges. The SGE output is fused via cross-attention, allowing the LLM to attend over object-relationship tokens explicitly. **G2** (arXiv 2025) constructs location-free scene graphs from image patches and LLMs for visual commonsense answering and explanation, with automatic graph filtering and selection to absorb valuable structure while discarding noise. **Graph-of-Mark** (arXiv 2026) overlays scene graphs onto input images as pixel-level visual prompts for spatial reasoning—the first such technique to capture object relationships via graph edges rather than isolated marks, improving zero-shot VQA and localization by up to 11 percentage points.

**Latent/Continuous Reasoning (4 papers)**. These methods reason in continuous latent space rather than discrete text, trading interpretability for expressiveness.

**MCOUT** (arXiv 2025) extends Coconut to multimodal settings, producing continuous latent thought vectors iteratively refined and aligned with visual and textual embeddings. Two variants—MCOUT-Base (hidden state reuse) and MCOUT-Multi (multimodal latent attention)—achieve up to 8.23% gains on MMMU, ScienceQA, and MMStar. **Coconut** (arXiv 2024) introduces the text-only precursor: reasoning in continuous latent space by feeding the model's last hidden state back as the next input embedding, enabling BFS-style multi-path encoding rather than depth-first text CoT. **LaRe** (arXiv 2025) combines latent reasoning with dynamic visual refocusing—at each step, attention is redirected to relevant image regions, addressing the "latent drift" problem where pure latent methods lose visual grounding. LaRe achieves 9.4% accuracy gains with 16.5% fewer inference tokens. **DMLR** (arXiv 2025) proposes test-time confidence-guided latent policy gradient optimization with a Dynamic Visual Injection Strategy that retrieves the most relevant visual patches at each latent step, providing a partial audit trail of perceptual focus points.

**Structured Visual Tokens (3 papers)**. These methods use compact structured tokens—continuous or textualized—as reasoning intermediates.

**CoVT** (arXiv 2025) interleaves ~20 continuous visual tokens (encoding depth, segmentation, edges, DINO features) with text tokens in the reasoning chain. Trained via distillation from lightweight vision experts, the VLM reasons in visual token space at inference without external tools, improving perception benchmarks by 3–16%. **Artemis** (arXiv 2025) represents each reasoning step as a (label, bounding-box) pair—structured spatial tokens that enable direct supervision for proposal quality and explicit state tracking. Built on Qwen2.5-VL-3B, Artemis achieves strong performance on grounding, detection, counting, and geometric-perception tasks. **StruVis** (arXiv 2026) uses text-based structured visual representations (layout descriptions, spatial relations, object lists) as intermediate states for T2I reasoning, replacing costly intermediate image generation with efficient structured text that enables the MLLM to "perceive" visual structure, gaining 4.61% on T2I-ReasonBench.

**Neuro-symbolic Methods (3 papers)**. These methods combine neural perception with formal symbolic reasoning.

**Concept-RuleNet** (arXiv 2025) mines discriminative visual concepts from training images, composes them into first-order logic (FOL) rules via an LLM reasoner, and employs a vision verifier to quantify symbol presence—achieving 5% improvement over neurosymbolic baselines while reducing hallucinated symbols by up to 50%. **COGT** (ICLR 2025) models vision-language compositional understanding using Causal Graphical Models (CGMs) derived from dependency parsing; the decoder follows a partially-ordered generation schedule constrained by the CGM, significantly outperforming compositional baselines on ARO, SugarCrepe, and VL-CheckList. **SpatialMath** (arXiv 2026) infuses spatially-grounded representations from visual diagrams into structured symbolic reasoning chains for geometric math problems, with a specialized perception module extracting geometric structures and spatial relationships, achieving up to 10 percentage points improvement on vision-intensive MATHVERSE-PLUS.

**Graph & Table Reasoning (2 papers)**. These methods use evolving tabular or graph structures as reasoning intermediates.

**Chain-of-Table** (ICLR 2024) integrates tabular data into the reasoning chain as evolving intermediate states—the LLM iteratively generates operations (filter, aggregate, select) and updates table snapshots via in-context learning, achieving SOTA on WikiTQ, FeTaQA, and TabFact without external code execution. **Mario** (arXiv 2026) enables graph-conditioned VLM reasoning on multimodal graphs (nodes with textual and visual attributes, edges with structural cues), using fine-grained cross-modal contrastive learning and a modality-adaptive router to surface the most informative modality configuration per node, outperforming graph models on node classification and link prediction.

#### 4.3.3 Types of Structured Traces

| Type | Description | Verification Mechanism | Example Use Case |
|------|-------------|----------------------|------------------|
| **Scene Graphs** | Nodes (objects) + edges (relations) | Schema validation, path traversal | CCoT, LLaVA-SG, G2, Graph-of-Mark |
| **Tables** | Rows/columns with schema | Schema validation, constraint checks | Chain-of-Table |
| **Multimodal Graphs** | Nodes with text+visual attributes | Graph structure, modality routing | Mario |
| **Spatial Tokens** | (label, bbox) or layout descriptions | IoU, spatial consistency | Artemis, StruVis |
| **Visual Tokens** | ~20 continuous perceptual embeddings | Decode to depth/seg/edges | CoVT |
| **FOL Rules** | First-order logic with symbols | Syntactic validity, satisfiability | Concept-RuleNet |
| **Causal Graphs** | Partially-ordered dependency structure | Graph topology, generation order | COGT |
| **Latent Vectors** | Continuous thought embeddings | Similarity, alignment (opaque) | MCOUT, Coconut, LaRe, DMLR |

#### 4.3.4 Verification Strategies

| Strategy | Mechanism | Representative Methods | Strength | Limitation |
|----------|-----------|------------------------|----------|------------|
| **Schema Validation** | Check structure conforms to schema (triples, rows/columns, FOL syntax) | CCoT, LLaVA-SG, Chain-of-Table, Concept-RuleNet | Catches format errors, malformed graphs | Doesn't verify semantic correctness |
| **Constraint Checking** | Validate logical constraints (no cycles, type compatibility, rule satisfiability) | COGT, Concept-RuleNet, Artemis | Catches inconsistencies, invalid operations | Constraints must be specified; may be brittle |
| **Alignment Verification** | Compare structure to visual input (IoU, patch retrieval log, decoded dense predictions) | Artemis, DMLR, CoVT, Graph-of-Mark | Ensures grounding in visual evidence | Requires visual encoder or ground truth; partial for latent methods |
| **Consistency Checks** | Verify across reasoning steps (table evolution, graph coherence) | Chain-of-Table, LLaVA-SG | Catches contradictions, cascading errors | May miss systematic biases |
| **Similarity Metrics** | Compare latent states to visual/text embeddings | MCOUT, LaRe | Quantitative alignment measure | Interpretation unclear; no human audit trail |

#### 4.3.5 Failure Modes

1. **Structurally Valid but Wrong**
   - Trace satisfies all constraints but conclusion is incorrect. CCoT and G2 can produce plausible scene graphs with hallucinated entities or relations that cascade to wrong answers (CCoT: fabricated edges; G2: graph hallucination from learned priors). Concept-RuleNet's FOL rules may be logically valid but semantically meaningless.

2. **Schema Rigidity**
   - Structure cannot express necessary reasoning. Chain-of-Table forces reasoning into tabular operations—complex multi-step joins or nested aggregations may exceed LLM capabilities. Artemis's (label, bbox) pairs may be insufficient for attributes, relationships, or multi-object interactions beyond simple detection.

3. **Alignment Failures**
   - Structure doesn't match visual input. Artemis: localization errors (poor IoU) or label-localization mismatch. Graph-of-Mark and LLaVA-SG: scene graph extraction errors (wrong objects, misclassified relations). DMLR: visual patch myopia—Dynamic Injection may fixate on salient but reasoning-irrelevant patches.

4. **Opaque Latent Errors**
   - Latent methods (MCOUT, Coconut, LaRe) produce no inspectable intermediate artifact. When MCOUT produces a wrong answer, the error is buried in latent space. LaRe's refocusing may collapse to the same region after iterations; DMLR's confidence-guided optimization may reinforce incorrect trajectories if confidence is miscalibrated.

5. **Interpretability–Efficiency Trade-off**
   - High-interpretability methods (CCoT, LLaVA-SG) require explicit structure generation; latent methods (MCOUT) achieve efficiency gains at the cost of zero human auditability. CoVT and DMLR offer partial interpretability (decodable tokens, injection logs) as a middle ground.

#### 4.3.6 When to Use Quadrant III

**Appropriate**:
- Settings requiring automatic checkability without tool dependencies
- Tasks with clear structural constraints (spatial, logical, tabular)
- When interpretability spectrum is acceptable (choose CCoT/LLaVA-SG for high, CoVT for medium, MCOUT for efficiency)
- Environments where tools are unavailable or latency is prohibitive

**Not Appropriate**:
- Tasks requiring external knowledge or factual verification
- Open-ended reasoning without clear structure
- When human interpretability is essential and latent methods are the only option
- Applications needing real-world grounding via execution feedback

**Selection Guidance by Subcategory**:
- **Scene Graph Methods**: CCoT for zero-shot compositional VQA without fine-tuning; LLaVA-SG when integrating scene graphs into the VLM architecture is preferred; G2 for visual commonsense answering with location-free graphs; Graph-of-Mark when pixel-level spatial prompting and object-relation overlay are needed.
- **Latent/Continuous Reasoning**: MCOUT when multimodal latent reasoning with no interpretability requirement is acceptable; Coconut for text-only logical reasoning with BFS-style search; LaRe when visual refocusing per step is needed to mitigate latent drift; DMLR when test-time optimization and partial visual injection audit trail justify the compute cost.
- **Structured Visual Tokens**: CoVT when perceptual cues (depth, segmentation, edges) should be interleaved with text and optionally decoded; Artemis for perception-policy learning with (label, bbox) supervision; StruVis for T2I reasoning where structured layout/relations replace costly intermediate image generation.
- **Neuro-symbolic Methods**: Concept-RuleNet when FOL rules and hallucination reduction (up to 50%) are critical; COGT for compositional language understanding with causal dependency constraints; SpatialMath for geometric math problems requiring spatially-grounded symbolic chains.
- **Graph & Table Reasoning**: Chain-of-Table for table understanding (WikiTQ, FeTaQA, TabFact) without SQL execution; Mario for multimodal graph reasoning with node classification and link prediction.

**Design Trade-offs**: Several design dimensions emerge from the Representative Works. *Interpretability vs. efficiency*: CCoT and LLaVA-SG offer highest interpretability (explicit scene graphs) at the cost of structure generation overhead; MCOUT and Coconut achieve efficiency via opaque latent reasoning. *Training vs. test-time*: Most Q3 methods require fine-tuning (LLaVA-SG, CoVT, Artemis); DMLR is a test-time optimization method applicable to existing VLMs. *Structure source*: Scene graphs may be LMM-generated (CCoT, G2), internally extracted (LLaVA-SG), or overlaid as prompts (Graph-of-Mark). *Verification depth*: Schema validation (CCoT, Chain-of-Table) catches format errors; alignment verification (Artemis, DMLR) requires visual grounding; latent methods (MCOUT) offer only similarity metrics with no human audit trail.

**Comparison with Other Quadrants**: Quadrant III offers automatic verification via structured traces without tool dependencies—unlike Quadrant II (tools add latency and failure modes) and Quadrant IV (executable traces require execution sandbox). The interpretability spectrum within Q3 allows practitioners to tune the trade-off: CCoT/LLaVA-SG for high-stakes applications requiring human audit; MCOUT for efficiency-critical settings. Quadrant I (text-only) cannot perform schema validation or constraint checking; Q3's structured traces enable systematic verification. For many applications, Q3 with the right subcategory (scene graphs for spatial reasoning, Chain-of-Table for tabular, Concept-RuleNet for interpretable rules) offers a practical balance between verifiability and deployment simplicity.

---

### 4.4 Quadrant IV: Structured + Tools / Executable

**Definition**: Methods that combine structured traces with tool/execution feedback for maximum verifiability.

#### 4.4.1 Approach Overview

Quadrant IV represents the **highest verifiability** approach: structured traces that are **executable** and **externally grounded**. Key characteristics:
- **Executable Traces**: Programs, sketches, or state logs that can be re-run
- **Tool Feedback**: External tools validate claims at each step
- **Replayability**: Same trace + same tools → same result
- **Step-Level Validation**: Each step can be independently verified

**Why Quadrant IV?** This approach addresses fundamental limitations of all other quadrants:
- More verifiable than text-only (Quadrant I)
- More checkable than text + tools (Quadrant II)
- More grounded than structured w/o tools (Quadrant III)

The trade-off: highest cost, latency, and complexity. The following subsections organize Representative Works by subcategory: Program Synthesis Pioneers, Sketch & Visual State, Code-as-Reasoning, RL-Trained Executable Agents, Embodied & Scientific, and Neuro-symbolic Executable.

#### 4.4.2 Representative Works by Subcategory

**Program Synthesis Pioneers (3 papers)**. These works establish the foundational paradigm of executable Python programs for visual reasoning. **ViperGPT** (ICCV 2023) provides the paradigmatic foundation: LLMs compose vision-and-language models into Python subroutines with a formal API (object detection, VQA, OCR, depth estimation), generating executable code for each query. The program serves as a complete, self-contained reasoning trace—fully replayable and machine-checkable. **ViReP** (CVPR 2024) addresses the training cold-start: no dataset of visual programs exists, so it uses reinforced self-training with execution-based reward (program output correct/incorrect) and REINFORCE-style policy gradient; small human corrections (<50) extend training beyond saturation. **VDebugger** (EMNLP 2024) introduces a critic-refiner framework for debugging visual programs: it tracks execution step-by-step, uses execution feedback (return values, exceptions) to localize logic errors, and trains via mask-best decoding that auto-injects bugs into correct programs. VDebugger improves downstream accuracy by up to 3.2% with 2.3% generalization on unseen tasks.

**Sketch & Visual State (3 papers)**. These methods use sketching or executable plotting as intermediate visual reasoning—structured artifacts that can be validated and replayed. **Visual Sketchpad** (NeurIPS 2024) [ANCHOR] establishes sketching as visual CoT: the model produces drawing commands (lines, boxes, masks) executed on a canvas, with specialist vision models (detection, segmentation) for programmatic annotation. Sketches are spatially grounded, replayable, and interpretable—achieving 12.7% improvement on math and 8.6% on visual reasoning. **CodePlot-CoT** (arXiv 2025) generates executable matplotlib/SymPy plotting code as each CoT step for math and geometry: code produces precise visualizations (function plots, geometric constructions) that provide concrete visual evidence; execution errors and visual inspection enable dual verification. **CodeVision** (arXiv 2025) proposes a unified view for "thinking with images via programming vision": the model generates Python code as a universal interface for any image operation, moving beyond fixed tool registries to an open-ended tool space; SFT on multi-turn tool composition plus RL with dense process reward yields 60.1 on MVToolBench (nearly doubling Gemini2.5-Pro).

**Code-as-Reasoning (5 papers)**. These methods treat executable code as the primary reasoning trace, with tool integration and execution feedback. **DeepEyesV2** (arXiv 2025) [ANCHOR] combines code execution with web search for evidence-based visual reasoning: cold-start data collection followed by RL trains agents that generate Python programs calling perception tools and web search for factual verification; programs produce reproducible results with clear failure localization. **CodeV** (arXiv 2025) addresses fidelity failure: high accuracy can coexist with unfaithful tool use (models invoke tools on irrelevant regions). CodeV represents tools as Python code and introduces TAPO (Tool-Aware Policy Optimization), a process-level RL framework with dense rewards on actual tool I/O; it substantially improves faithful tool-use rates. **CodeDance** (arXiv 2025) is a dynamic tool-integrated MLLM that dynamically defines, composes, and executes code to orchestrate multiple tools, compute intermediate results, and render visual artifacts (boxes, plots); balanced adaptive tool-call reward guides RL, with emergent behaviors (novel tool invocations, cross-task transfer) without task-specific fine-tuning. **RECODE** (arXiv 2025) proposes "derendering": reverse-engineering charts and diagrams into executable code that reproduces them; a critic selects the most faithful reconstruction by comparing rendered output to the original image; the derendering program enables precise symbolic calculations. **ARM2** (arXiv 2025) introduces adaptive reasoning with executable code: the model chooses between code and text per step; length-aware RL achieves 70%+ token reduction while preserving performance on par with traditional reasoning models.

**RL-Trained Executable Agents (3 papers)**. These works use reinforcement learning to train VLMs for executable code generation, with execution feedback as the primary reward signal. **Visual-ARFT** (arXiv 2025) uses GRPO to train VLMs to generate image-processing code (OpenCV, filtering, edge detection); execution produces transformed images and success/failure signals; dual reward (execution success + downstream task accuracy) guides policy optimization. **Visual Programmability** (arXiv 2025) learns adaptive selection between code execution and direct vision for chart understanding: a meta-controller routes to code for precise numerical extraction and arithmetic, or to vision for qualitative pattern recognition; execution outcomes inform pathway selection. **MM-Zero** (arXiv 2026) is the first zero-data self-evolving VLM: Proposer generates concepts, Coder converts them to executable Python/SVG code and renders images, Solver reasons over generated images; GRPO with execution reward and visual verification (Solver answers vs. Proposer intent) drives autonomous improvement from scratch.

**Embodied & Scientific (2 papers)**. These methods apply executable reasoning to physical or scientific domains. **Act-Observe-Rewrite** (arXiv 2026) uses LLMs to iteratively refine robot controller code: the LLM generates Python controller code, observes execution in simulation or on hardware (trajectory data, error logs, sensor readings), and rewrites code to correct failures; the closed loop enables autonomous controller improvement without human intervention. **VLM Scientific Discovery** (arXiv 2025) positions VLMs as visual checkpoints for experimental code: scientists write code, execute to produce visual outputs (plots, microscopy, simulation); the VLM validates whether outputs match expected scientific patterns, catching errors early and guiding iterative refinement.

**Neuro-symbolic Executable (2 papers)**. These methods combine neural perception with symbolic reasoning and executable verification. **NS-VLA** (arXiv 2026) uses a neuro-symbolic encoder to extract structured primitives from vision and language, and a symbolic solver for data-efficient action sequencing; online RL with execution feedback enables expansive exploration beyond demonstrations. **VLAgent** (arXiv 2025) employs a two-stage pipeline: SS-parser validates and repairs the LLM-generated symbolic program before execution; the back-end transforms the plan to executable code and runs neural models plus symbolic functions; an execution verifier validates stepwise results (ensemble methods for critical reasoning, caption analysis for low-confidence cases).

#### 4.4.3 Highest Verifiability: Replayability, Step-Level Validation, Execution Feedback

Quadrant IV achieves the **highest verifiability** in the 2×2 matrix through three mechanisms:

1. **Replayability**: Executable traces (Python programs, drawing commands, symbolic plans) fully specify the reasoning process. Given the same inputs and environment, anyone can re-run the trace and reproduce results. ViperGPT's programs are self-documenting; Visual Sketchpad's drawing commands are deterministic; RECODE's derendering programs are complete formal specifications. This contrasts with text CoT, where "replay" is impossible—the model may produce different text for the same reasoning.

2. **Step-Level Validation**: Each step can be independently verified. VDebugger localizes bugs to specific code lines via execution feedback. CodeV's TAPO assigns step-wise rewards on actual tool I/O. VLAgent's execution verifier validates stepwise results. Code execution produces concrete outputs (lists, counts, images) at each step—checkable without LLM introspection.

3. **Execution Feedback**: External grounding via execution provides objective correctness signals. Code either runs or fails; tools return typed outputs or exceptions. ViReP and Visual-ARFT use execution feedback as RL reward. MM-Zero's Coder receives execution success/failure; the Solver's answers are verified against Proposer intent. This eliminates the faithfulness gap: the model cannot "explain without doing."

#### 4.4.4 Cost, Latency, and Security Trade-offs

Quadrant IV methods incur the highest cost, latency, and security risk in the taxonomy:

**Cost/Latency**: Code execution adds multiple API calls per step (ViperGPT, CodeDance); iterative refinement loops (VDebugger, RECODE) multiply forward passes; RL training requires large-scale execution (ViReP, Visual-ARFT, MM-Zero). ARM2 mitigates via 70% token reduction when code replaces verbose CoT. Visual Programmability and CodeVision reduce cost by selectively invoking code only when needed.

**Security**: Executing LLM-generated code requires sandboxing. CodeVision's open-ended tool space ("any Python-expressible image operation") creates maximum attack surface (CodeVision, CodeDance). ViperGPT constrains the API to vision-only functions. VDebugger's mask-best decoding may produce programs with unintended side effects. RECODE limits execution to visualization libraries. Deployment must enforce restricted interpreters, whitelisted imports, and timeout limits.

**Cascading Errors**: Early-step errors propagate (VDebugger, CodeV). If the critic mislocalizes the buggy step, the refiner patches the wrong code (VDebugger). RECODE's iterative refinement may require many cycles for complex charts without clear termination. CodeDance's implicit state between code blocks can cause silent failures.

#### 4.4.5 Verification Strategies

| Strategy | Mechanism | Representative Works | Strength | Limitation |
|----------|-----------|---------------------|----------|------------|
| **Code Execution** | Run program, check output | ViperGPT, DeepEyesV2, CodeDance | Fully reproducible; deterministic | Security risks; sandbox required |
| **Execution Feedback Debugging** | Step-by-step trace; critic-refiner | VDebugger | Localizes logic errors; mask-best training | Critic mislocalization; cascading errors |
| **Tool I/O Validation** | Dense rewards on actual tool inputs/outputs | CodeV (TAPO) | Faithfulness; prevents reward hacking | Reward model must assess relevance correctly |
| **Derendering + Critic Selection** | Render code output; compare to original | RECODE | Objective verification; no LLM needed | Fails for non-standard visuals |
| **Sketch Execution** | Drawing commands → canvas; validation | Visual Sketchpad | Spatially grounded; interpretable | Specialist vision tools required |
| **Plotting Code Execution** | Matplotlib/SymPy code → visual output | CodePlot-CoT | Dual verification (code + visual) | Domain-limited to math/geometry |
| **Visual Checkpoint** | VLM validates generated visual outputs | VLM Scientific Discovery, MM-Zero | Catches errors; guides refinement | VLM may miss subtle anomalies |
| **SS-Parser + Execution Verifier** | Syntax/semantic validation; stepwise validation | VLAgent | Catches plan errors; ensemble for critical steps | Two-stage overhead |

#### 4.4.6 Failure Modes

1. **Execution Failures** (ViperGPT, CodeDance, MM-Zero): Code crashes, timeouts, or resource exhaustion. Tool API failures (VDebugger). Syntax errors in generated code. MM-Zero's Coder may produce invalid Python/SVG; execution failures provide negative feedback but can destabilize training.

2. **Security Risks** (CodeVision, CodeDance, ViperGPT): Code injection; open-ended code execution (CodeVision's "any Python operation") creates maximum attack surface. Sandboxing must be comprehensive. VDebugger's mask-best decoding may produce programs with unintended side effects.

3. **Cascading Errors** (VDebugger, CodeV, RECODE): Early step error propagates; garbage in, garbage out. VDebugger: critic mislocalization → refiner patches wrong step. CodeV: wrong first crop → all subsequent reasoning based on wrong evidence. RECODE: color/encoding errors in derendering produce silent errors (visually similar but wrong chart).

4. **Reward Hacking** (ViReP, CodeV): ViReP's binary outcome reward cannot penalize programs that get the right answer via wrong intermediate steps; training saturates at 1–3 iterations without human corrections. CodeV: reward model may incorrectly assess tool output relevance; models may learn to invoke tools on "visually complex" regions that score high regardless of question relevance.

5. **Cost/Latency** (RECODE, Visual-ARFT, Visual Programmability): Multiple tool calls per step; iterative refinement loops; RL training with dense process rewards. RECODE's generate-execute-critique-refine loop is among the most expensive for complex charts. Not suitable for real-time use.

6. **Tool Interface Mismatch** (VDebugger, CodeDance): Generated code doesn't match tool API; type errors, parameter mismatches. CodeDance's dynamic code composition may lack type contracts—unexpected return types cause silent downstream failures.

7. **Derendering Failure** (RECODE): For highly stylized or hand-drawn visuals, no faithful derendering program may exist in the assumed grammar. Framework degrades to standard perception when derendering fails.

#### 4.4.7 When to Use Quadrant IV

**Appropriate**:
- Safety-critical applications (medical, legal, scientific)
- Tasks requiring full auditability and reproducibility
- Settings where step-level validation is essential
- High-stakes decisions needing multiple verification layers
- Domains with well-defined executable grammars (charts, geometry, robot control)

**Not Appropriate**:
- Real-time applications with strict latency requirements
- Resource-constrained environments
- Settings where code execution is prohibited
- Low-stakes applications where cost outweighs benefit
- Open-ended visuals without clear derendering grammar (RECODE)

**Comparison with Other Quadrants**: Quadrant IV provides highest verifiability at highest cost. Quadrant I offers lowest deployment complexity—no tool APIs, no execution sandbox. Quadrant II adds external grounding but tool latency and failure modes. Quadrant III enables automatic verification via structured traces without tool dependencies. For many applications, Quadrant I with process supervision or Quadrant II with RL-trained tool use offers a practical balance; Quadrant IV is reserved for settings where replayability and step-level validation justify the cost.

---

### 4.5 Quadrant Comparison Summary

The following table summarizes all 78 papers across the four quadrants, reflecting the latest design space and trade-offs:

| Aspect | Q1 (25 papers) | Q2 (19 papers) | Q3 (16 papers) | Q4 (18 papers) |
|--------|---------------|----------------|----------------|----------------|
| **Representative works** | R1-VL, LLaVA-CoT, VisualPRM, Critic-V | AdaReasoner, VISTA-R1, ChartAgent, VideoAgent | CCoT, LLaVA-SG, Chain-of-Table, MCOUT | ViperGPT, DeepEyesV2, Visual Sketchpad, CodeV |
| **Verification strategies** | Self-consistency, PRM, step rewards (StepRAR/StepRVR), critic feedback, DPO | Tool output validation, trajectory audit, RL reward design (Tool-GRPO), selective verification | Schema validation, constraint checking, alignment verification | Code execution, execution feedback debugging, tool I/O validation, derendering |
| **Grounding** | Weak (implicit L1–L2; patch cues, bbox in Visual CoT) | Strong (tool outputs, evidence packages) | Moderate (scene graphs, spatial tokens, latent alignment) | Strong (executable traces, tool I/O) |
| **Checkability** | Manual (PRM/BoN for partial automation) | Partial (tool outputs checkable; trajectory audit) | Automatic (schema, constraints, alignment) | Automatic (execution, stepwise validation) |
| **Replayability** | No | Partial (tool replay; trajectory log) | Yes (structured traces) | Yes (full; executable replay) |
| **Latency** | Low (single pass; BoN adds cost) | Moderate (sequential tool calls; MCTS/hierarchy multiply) | Low (no tools; structure overhead) | High (code execution, refinement loops) |
| **Cost** | Low (no APIs; BoN/PRM optional) | Moderate (tool APIs, RL training) | Low (no execution) | High (execution, RL, iterative refinement) |
| **Security** | Low | Moderate (web/GUI prompt injection) | Low | High (code execution, sandbox required) |
| **Best for** | Low-stakes QA, rapid prototyping, resource-constrained | Factual verification, web/GUI agents, long-form video | Automatic checkability w/o tools, spatial/logical structure | Safety-critical, full auditability, reproducible traces |
| **Key trend (2024→2026)** | RLVR (StepGRPO, GRPO, SFT-RL); PRM data efficiency; faithfulness as independent dimension | RL for tool selection (Tool-GRPO, VISTA-Gym); selective verification; hierarchical orchestration | Latent reasoning (MCOUT, LaRe); scene-graph overlay (Graph-of-Mark); neuro-symbolic (Concept-RuleNet) | Zero-data self-evolving (MM-Zero); dual reward (executability + accuracy); critic-refiner (VDebugger) |

**Design Guidance**: Choose the quadrant that matches your application's verifiability requirements, latency constraints, and risk tolerance.

---

## 5 Learning & Alignment for Verifiability

This section examines how verifiable reasoning systems are trained and aligned. We identify a recurring progression across quadrants and synthesize best practices.

### 5.1 Training Progression

Training methods for verifiable reasoning follow a common progression from simple imitation to process-guided optimization:

```
SFT with Rationale → Process Supervision → PRM → RL/DPO
```

#### 5.1.1 SFT with Rationale

**Approach**: Supervised fine-tuning on examples with annotated reasoning traces.

**Data Collection**:
- Human-annotated CoT (experts write step-by-step reasoning)
- Model-generated CoT filtered by answer correctness
- Distillation from stronger models

**Strengths**:
- Simple, follows standard SFT pipeline
- Learns reasoning format and style
- Effective for basic CoT capabilities

**Limitations**:
- Learns correlation, not causation (may produce plausible but unfaithful reasoning)
- No explicit verifiability training
- Answer-level supervision only (process may be wrong)

**Example**: Fine-tuning a VLM on VQA datasets with CoT annotations teaches the model to produce multi-step explanations, but doesn't guarantee faithfulness.

#### 5.1.2 Process Supervision

**Approach**: Provide feedback on individual reasoning steps, not just final answers.

**Data Collection**:
- Human annotators label each step as correct/incorrect
- Model-generated critiques of reasoning steps
- Step-level rewards from task structure (e.g., code execution success)

**Strengths**:
- Directly trains for faithful reasoning
- Catches errors early in the process
- Enables credit assignment (which steps deserve reward?)

**Limitations**:
- Requires step-level annotations (expensive)
- May overfit to annotation schema
- Defining step boundaries can be ambiguous

**Example**: Training a model to recognize when its detection step is wrong, even if the final answer happens to be correct.

#### 5.1.3 PRM (Process Reward Model)

**Approach**: Train a separate model to score reasoning traces at each step.

**Architecture**:
- **PRM Input**: (Question, Image, Reasoning Step _t_, Context)
- **PRM Output**: Reward score _r_t_ ∈ [0, 1]
- **Training**: Human preference data or verified step correctness

**Usage**:
- Guide search during inference (beam search with PRM scores)
- Train policy model via RL (maximize cumulative PRM score)
- Filter generated traces (discard low-scoring paths)

**Strengths**:
- Scalable (PRM can be trained once, used many times)
- Enables inference-time improvement
- Separates reasoning generation from evaluation

**Limitations**:
- PRM may have blind spots (adversarial traces fool PRM)
- Training data requirements (need step-level preferences)
- Computational overhead at inference

**Example**: A PRM trained to detect unfaithful reasoning steps can guide the policy model away from generating such traces.

#### 5.1.4 RL / DPO

**Approach**: Optimize reasoning policy using reinforcement learning or direct preference optimization.

**RL Methods**:
- **PPO**: Maximize cumulative reward (from PRM or environment)
- **Advantage**: Handles delayed rewards (early steps affect final outcome)

**DPO Methods**:
- Learn from pairwise preferences (trace A > trace B)
- Avoid explicit reward modeling
- More stable than RL

**Reward Sources**:
- **Environment feedback**: Tool outputs, execution success
- **PRM scores**: Step-level quality
- **Human preferences**: Which trace is more faithful?
- **Consistency**: Agreement across multiple samples

**Strengths**:
- Directly optimizes for verifiability metrics
- Can incorporate multiple reward sources
- Handles long-horizon reasoning (credit assignment)

**Limitations**:
- Training instability (RL)
- Reward hacking (optimize for reward, not true verifiability)
- Computational cost

**Example**: RL training where rewards come from successful code execution + correct final answer teaches the model to produce executable, verifiable reasoning.

#### 5.1.5 RLVR for Visual Reasoning

**Approach**: Reinforcement Learning for Visual Reasoning (RLVR) applies RL with process-level rewards to improve step-wise correctness and prevent shortcuts in visual CoT.

**Representative Methods**:
- **R1-VL**: StepGRPO with step-level accuracy (StepRAR) and validity (StepRVR) rewards; key steps extracted from reference solutions; no manual annotation or external tools.
- **Visionary-R1**: GRPO with structured caption→reason→answer format reward; CoT-free training (273K QA pairs) prevents reliance on spurious textual cues.
- **OpenVLThinker**: Iterative SFT-RL cycles—SFT surfaces latent reasoning, RL refines; addresses visual grounding degradation when distilling text-only reasoning into LVLMs.
- **AdaReasoner**: Tool-GRPO for adaptive tool selection across seven task types; end-task success feedback modulates tool-use frequency.
- **Visual-ARFT**: GRPO for code tool calling; dual reward (executability + downstream accuracy) guides policy optimization.
- **VISTA-R1**: Unified agentic RL across 7 task types via VISTA-Gym; standardized tool interfaces and verifiable feedback.
- **ToolRL**: Systematic reward design study—type, scale, granularity, temporal dynamics; fine-grained decomposition (format × tool × accuracy) improves stability.

**Strengths**:
- Dense step-level rewards address sparse outcome-only RL
- Format and structure rewards prevent shortcut reasoning
- Scalable to tool-use and code execution domains

**Limitations**:
- Rule-based rewards (StepRAR, StepRVR) may be domain-dependent
- Reward design is critical (ToolRL); reward hacking remains a risk

**PRM Variants for Visual Reasoning**:
- **VisualPRM**: Step-level scoring for multimodal reasoning; Monte Carlo sampling for labels; Best-of-N inference.
- **VRPRM**: Low-data PRM (3.6K SFT + 50K non-CoT RL) surpasses 400K-trained baselines; Stage 1 instills step evaluation, Stage 2 scales via non-CoT RL.
- **Critic-V**: VLM critic for step-by-step error detection; natural-language critiques; DPO on RBR-ranked preferences.

**Self-Improvement Variants**:
- **LLaVA-Critic-R1**: Critic-as-policy; preference data → verifiable RL signal; unified model for evaluation and generation; Best-of-128 self-critique at test time.
- **VC-STaR**: Visual contrastive self-improvement; contrastive VQA pairs (VisCoR-55K) provide implicit verification.
- **MM-Zero**: Zero-data self-evolving; Proposer→Coder→Solver; GRPO with execution reward and visual verification drives autonomous improvement from scratch.

### 5.2 Cold-start + RL for Tool-use

A recurring pattern across Quadrants II and IV is **cold-start + RL for tool-use**:

**Phase 1: Cold-Start SFT**
- Train on demonstrations of tool use (human or expert model)
- Learn basic tool calling format and semantics
- Establish foundation for tool interaction

**Phase 2: RL Fine-tuning**
- Interact with tools in environment
- Receive feedback (tool outputs, task success)
- Optimize tool-use policy via RL

**Why This Pattern?**
- Tool use is compositional (many possible tool combinations)
- SFT alone cannot cover all scenarios
- RL enables exploration and adaptation to tool failures

**Example Trajectory**:
1. **SFT**: Model learns to call `detector.detect(image)` from examples
2. **RL**: Model explores when to call detector, which parameters to use, how to handle failures
3. **Result**: Robust tool-use policy that adapts to diverse scenarios

**Challenges**:
- **Exploration cost**: Failed tool calls during RL training
- **Safety**: Ensuring safe exploration (especially for code execution, web access)
- **Sample efficiency**: RL requires many episodes

**Representative Works**: **DeepEyesV2** combines cold-start data collection (program candidates) with RL—programs are executed, outputs verified, and successful programs used for training. **Visual-ARFT** uses GRPO with dual reward (execution success + task accuracy) for image-processing code; cold-start SFT establishes basic code generation before RL. **OpenVLThinker** employs iterative SFT-RL cycles: SFT narrows the RL search space by surfacing latent reasoning; each RL stage refines skills and produces higher-quality SFT data for the next cycle, addressing visual grounding degradation when distilling text-only reasoning into LVLMs.

### 5.3 Verifier-guided Training Data

**Approach**: Use verifiers (tools, execution, human feedback) to collect high-quality training data.

**Pipeline**:
```
1. Generate candidate traces (model sampling)
2. Verify traces (tools, execution, humans)
3. Filter/rank by verification score
4. Train on verified traces
```

**Verifier Types**:
- **Tool-based**: Do tool outputs confirm the reasoning?
- **Execution-based**: Does code run successfully and produce correct output?
- **Human-based**: Do annotators rate the trace as faithful?
- **Consistency-based**: Do multiple samples agree?

**Advantages**:
- Scalable data collection (model generates, verifier filters)
- High-quality training signal (verified traces)
- Can target specific failure modes

**Challenges**:
- Verifier coverage (what cannot be verified?)
- Verification errors (false positives/negatives)
- Distribution shift (verified data may not match deployment)

**Representative Works**: **VisualPRM** uses Monte Carlo sampling to generate step-level labels (P(correct | prefix) via majority voting); the 8B PRM scores reasoning chains for Best-of-N inference and process supervision. **VRPRM** achieves data-efficient verifier-guided training: only 3.6K CoT-PRM SFT + 50K non-CoT PRM RL surpasses 400K-trained baselines; Stage 1 instills step-level evaluation, Stage 2 scales via non-CoT RL without expensive CoT annotation. **Critic-V** applies a VLM critic for step-by-step error detection—natural-language critiques (e.g., "incorrectly attributed spatial relationship") provide richer feedback than scalar rewards; the Critic is trained via DPO on preferences ranked by Rule-based Reward (RBR).

**Example**: DeepEyesV2 collects training data by:
1. Generating program candidates for reasoning tasks
2. Executing programs and checking outputs
3. Filtering to programs that run successfully and produce correct answers
4. Training on verified programs

### 5.4 Cross-Quadrant Training Patterns

Despite quadrant differences, common training patterns emerge:

| Pattern | Q1 | Q2 | Q3 | Q4 |
|---------|----|----|----|----|
| **SFT with CoT** | ✓ | ✓ | ✓ | ✓ |
| **Process Supervision** | ✓ | ✓ | ✓ | ✓ |
| **Tool-use SFT** | ✗ | ✓ | ✗ | ✓ |
| **Execution Feedback** | ✗ | Partial | ✗ | ✓ |
| **PRM** | ✓ | ✓ | ✓ | ✓ |
| **RL for Tool-use** | ✗ | ✓ | ✗ | ✓ |

**Key Insight**: As we move from Q1 → Q4, training increasingly relies on **external feedback** (tools, execution) rather than purely internal signals (consistency, human preferences).

**Training Recommendation**:
- **Q1**: Focus on consistency training and process supervision
- **Q2**: Combine SFT for tool-use with RL for tool orchestration
- **Q3**: Train with structural constraints and alignment losses
- **Q4**: Use execution feedback as primary training signal

---

---

## 6 Evaluation Protocols & Benchmarks

Evaluating verifiable reasoning requires moving beyond answer accuracy to measure **process-level properties**. This section synthesizes evaluation protocols across quadrants.

### 6.1 Beyond Answer Accuracy: Process-level Metrics

Traditional VQA evaluation measures only whether the final answer is correct. This is insufficient for verifiable reasoning—a correct answer with unfaithful reasoning should not receive full credit.

We propose five process-level metric categories:

#### 6.1.1 Step Correctness

**Definition**: Are individual reasoning steps correct?

**Measurement**:
- **Human annotation**: Experts label each step as correct/incorrect
- **Tool verification**: Tools validate step claims (e.g., detector confirms object presence)
- **Execution success**: Code steps run without errors
- **Constraint satisfaction**: Steps satisfy logical/structural constraints

**Metrics**:
- Step Accuracy: % of steps labeled correct
- Step F1: Precision/recall for step-level predictions
- Error Rate: % of traces with ≥1 incorrect step
- **StepRAR + StepRVR** (R1-VL): Step-level rule-based rewards—StepRAR (soft key-step matching) rewards intermediate reasoning accuracy; StepRVR (logic evaluation) rewards reasoning completeness and consistency; key steps extracted from reference solutions without manual annotation.
- **Noisy Thinking detection** (RTWI): Text-centric reliability estimation for cue and step quality; robust filtering removes low-reliability components; voting aggregates over multiple reasoning paths to prevent noise from contaminating final answers.

**Example**: For a counting task with CoT "I see 3 cars, 2 people, 1 dog":
- Step verification: Run detector, compare counts
- Score: 3/3 correct → Step Accuracy = 100%

**Challenges**:
- Step boundary definition (what counts as one step?)
- Partial credit (mostly correct steps)
- Inter-annotator agreement (for human labels)

#### 6.1.2 Evidence Attribution

**Definition**: Can reasoning steps be linked to specific visual evidence?

**Measurement**:
- **Grounding precision**: Do stated regions match actual objects?
- **Citation accuracy**: For tool-based reasoning, do tool outputs support claims?
- **Attention alignment**: Do attention weights correlate with stated reasoning?

**Metrics**:
- Grounding IoU: Intersection-over-Union between stated and actual regions
- Citation Precision: % of claims supported by cited evidence
- Attention Correlation: Correlation between attention and reasoning mentions
- **Process-supervised cue reward** (PatchCue): Evaluates whether patch references correctly ground reasoning; RL with process-supervised cue reward guides intermediate steps toward correct visual grounding; balances spatial precision and robustness vs. pixel-level bbox.
- **Visual faithfulness as independent dimension** (Journey Before Destination): Decomposes CoT into perception steps vs. reasoning steps; uses off-the-shelf VLM judges for step-level faithfulness (training- and reference-free); treats faithfulness as orthogonal to answer accuracy.
- **Unfaithful Perception Rate** (Journey Before Destination): % of perception steps that are not grounded in actual visual content; enables targeted improvement via self-reflection and local regeneration of unfaithful steps.

**Example**: For reasoning "The red car [x1,y1,x2,y2] is parked illegally":
- Verify: Is there a red car at those coordinates?
- Verify: Does the region show illegal parking (e.g., in front of fire hydrant)?

**Challenges**:
- Implicit grounding (vague references like "the object")
- Multi-modal evidence (reasoning based on combination of image + knowledge)

#### 6.1.3 Trace Replayability

**Definition**: Can the reasoning trace be re-run to reproduce the result?

**Measurement**:
- **Execution replay**: Re-run code/program, check output consistency
- **Tool replay**: Re-call tools with same parameters, compare outputs
- **Sampling replay**: Generate multiple samples, check agreement

**Metrics**:
- Replay Success Rate: % of traces that can be successfully re-run
- Output Consistency: Agreement between original and replayed outputs
- Determinism Score: Variance across multiple replays

**Example**: For a program-based reasoning trace:
```python
# Original execution
count = len(detector.detect(image))  # Returns 5

# Replay
count_replay = len(detector.detect(image))  # Should return 5
consistent = (count == count_replay)
```

**Challenges**:
- Non-deterministic tools (model outputs vary)
- Stateful environments (replay may change state)
- External dependencies (web APIs may change)

#### 6.1.4 Robustness

**Definition**: Is reasoning robust to perturbations, distribution shifts, and adversarial attacks?

**Measurement**:
- **Input perturbations**: Add noise, change lighting, crop image
- **Distribution shifts**: Test on out-of-distribution data
- **Adversarial attacks**: Targeted perturbations to fool reasoning
- **Tool failures**: Simulate tool errors, check recovery

**Metrics**:
- Robustness Score: Performance drop under perturbation (smaller = better)
- OOD Generalization: Accuracy gap between in-distribution and OOD
- Adversarial Accuracy: Accuracy under targeted attacks
- Failure Recovery: % of cases where model recovers from tool errors

**Example**: Test robustness by:
1. Add Gaussian noise to image
2. Run reasoning, compare to original
3. Measure: Does reasoning change appropriately (if content changes) or stay stable (if noise is imperceptible)?

**Challenges**:
- Defining appropriate perturbation magnitude
- Separating robustness from brittleness to meaningful changes

#### 6.1.5 Cost/Latency

**Definition**: What are the computational and time costs of the reasoning process?

**Measurement**:
- **Wall-clock time**: End-to-end inference latency
- **Tool calls**: Number of external API calls
- **Compute cost**: FLOPs, GPU hours, API costs
- **Step count**: Number of reasoning steps

**Metrics**:
- Latency (ms): Time from input to output
- Tool Call Count: Number of tool invocations
- Cost per Query: Monetary cost (for paid APIs)
- Steps per Query: Reasoning trace length

**Example**: Compare Q1 vs Q4:
- Q1 (Text-only): 100ms, 0 tool calls, $0.00
- Q4 (Structured + Tools): 2000ms, 15 tool calls, $0.05

**Trade-off**: Higher verifiability (Q4) comes at higher cost. The question is whether the verifiability gain justifies the cost for the application.

### 6.2 Benchmarks for Verifiable Reasoning

Existing benchmarks focus primarily on answer accuracy. We identify benchmarks that enable process-level evaluation:

| Benchmark | Task | Process Metrics Supported | Quadrant Coverage |
|-----------|------|--------------------------|-------------------|
| **VQA-CoT** | Visual QA with CoT | Step correctness (human annotation) | Q1 |
| **ScienceQA** | Science reasoning | Step correctness, evidence attribution | Q1, Q2 |
| **ChartQA** | Chart understanding | Evidence attribution (to chart regions) | Q1, Q2, Q4 |
| **DocVQA** | Document VQA | Evidence attribution (to text regions) | Q2, Q4 |
| **RefCOCO+** | Referring expression | Grounding precision (bounding boxes) | Q3, Q4 |
| **Visual Genome** | Scene graph generation | Structural correctness | Q3 |
| **CLEVR** | Compositional reasoning | Step correctness (program execution) | Q3, Q4 |
| **Video-MME** | Video understanding | Temporal grounding, step tracking | Q2, Q4 |
| **ToolBench-VL** | Tool use for VQA | Tool correctness, trajectory audit | Q2, Q4 |
| **ExecVQA** | Executable VQA | Code execution success, replayability | Q4 |
| **VisReason** | Visual CoT (489K + 165K Pro) | Step-by-step accuracy, 3D spatial grounding | Q1 |
| **MIRA** | Visualization-essential (546 Qs) | Intermediate visual image generation, Pass@k, textual prompt alignment | Q1 |
| **Visual CoT** (NeurIPS 2024 DB) | CoT with bbox grounding (438K, ~98K full CoT) | Region identification (IoU), reasoning accuracy | Q1 |
| **ZoomBench** | Fine-grained perception (845 VQA) | Region-to-image distillation, zooming capability | Q1 |
| **VISTA-Gym** | Agentic RL training env | 7 tasks, 13 datasets, standardized tool interfaces, verifiable feedback | Q2, Q4 |

**Benchmark Gaps**:
- No benchmark comprehensively evaluates all five process metric categories
- Limited benchmarks for Q3 (structured w/o tools)
- Few benchmarks test robustness to adversarial attacks
- No standardized cost/latency benchmarks

**Recommendation**: Use multiple benchmarks to cover different quadrants and metric categories. Report both answer accuracy and process metrics.

### 6.3 Integrated Capability Evaluation

Verifiable reasoning requires integrating multiple capabilities. We propose evaluation across four dimensions:

#### Perception

**What to measure**:
- Object detection accuracy
- Attribute recognition
- Spatial relationship understanding
- OCR / text reading

**Evaluation**:
- Standard perception benchmarks (COCO, Visual Genome)
- Perception ablation (provide ground truth perception, measure reasoning improvement)

**Insight**: Poor perception cascades to reasoning errors. Separate perception failures from reasoning failures.

#### Search

**What to measure**:
- Query formulation (can model ask the right questions?)
- Result integration (can model use search results correctly?)
- Source evaluation (does model trust reliable sources?)

**Evaluation**:
- Retrieval-augmented QA benchmarks
- Search trajectory analysis (query quality, result usage)

**Insight**: Search is only useful if model can formulate good queries and correctly interpret results.

#### Reasoning

**What to measure**:
- Multi-step inference
- Logical consistency
- Constraint satisfaction
- Counterfactual reasoning

**Evaluation**:
- Compositional reasoning benchmarks (CLEVR, gQA)
- Logic puzzle datasets
- Counterfactual VQA

**Insight**: Reasoning capability is necessary but not sufficient—reasoning must also be faithful and grounded.

#### Tool-use

**What to measure**:
- Tool selection (picking the right tool)
- Parameter formulation (calling tool correctly)
- Output interpretation (understanding tool results)
- Error handling (responding to tool failures)

**Evaluation**:
- Tool-use benchmarks (ToolBench, API-Bank)
- Tool ablation (remove specific tools, measure impact)
- Failure injection (simulate tool errors)

**Insight**: Tool-use is a means to verifiability, not an end. Evaluate tools by how much they improve verification, not just answer accuracy.

### 6.4 Evaluation Protocol Recommendations

Based on this analysis, we recommend:

**For Paper Authors**:
1. Report both answer accuracy and process metrics
2. Include failure mode analysis (not just aggregate scores)
3. Compare across quadrants (ablate tools, structure)
4. Report cost/latency (not just performance)
5. Release code and traces for reproducibility

**For Reviewers**:
1. Evaluate verifiability claims (not just answer accuracy)
2. Check that process metrics are meaningful (not just proxy metrics)
3. Verify that baselines are fair (compare within quadrant)
4. Assess practical applicability (cost, latency, safety)

**For Benchmark Creators**:
1. Include process-level annotations (step correctness, grounding)
2. Support multiple quadrants (not biased toward one approach)
3. Include robustness tests (perturbations, OOD, adversarial)
4. Provide cost tracking (tool call counting, timing)

---

---

## 7 Applications (Optional)

### 7.1 Safety-Critical Domains

Verifiable reasoning is essential in domains where errors have serious consequences:

#### Medical Imaging Reasoning

**Requirements**:
- Step-level auditability (radiologists must verify each finding)
- Evidence attribution (claims must link to image regions)
- High robustness (no tolerance for hallucination)

**Quadrant Choice**: Q4 (Structured + Tools) preferred
- Structured reports (findings linked to coordinates)
- Tool verification (CAD systems confirm detections)
- Replayability (second opinion from same trace)

**Example**: Chest X-ray interpretation with verifiable CoT:
```
Step 1: Detect opacity in right lower lobe [coords]
        → Verified by segmentation tool (IoU=0.92)
Step 2: Classify opacity as consolidation
        → Verified by radiologist review
Step 3: Infer diagnosis: pneumonia
        → Supported by clinical guidelines
```

#### Scientific Diagram Analysis

**Requirements**:
- Precise grounding (data points must map to visual elements)
- Reproducibility (same diagram → same extraction)
- Uncertainty quantification

**Quadrant Choice**: Q3-Q4 depending on verification needs

#### Legal Document Understanding

**Requirements**:
- Citation accuracy (claims must link to document text)
- Logical consistency (arguments must be sound)
- Auditability (full reasoning trace for discovery)

**Quadrant Choice**: Q3 (Structured w/o Tools) often sufficient
- Structured legal reasoning templates
- Citation graphs linking claims to text
- Logical constraint checking

### 7.2 Vertical Domains Requiring Auditability

#### Financial Analysis

- Earnings report interpretation with traceable reasoning
- Investment recommendations with auditable logic
- Regulatory compliance (reasoning must be explainable)

#### Quality Control / Manufacturing

- Defect detection with grounded explanations
- Root cause analysis with verifiable steps
- Compliance documentation

#### Education

- Grading with explainable rubrics
- Student feedback with specific evidence
- Fairness auditing (no biased reasoning)

---

## 8 Challenges & Future Directions

Despite recent progress, significant challenges remain in building truly verifiable multimodal reasoning systems.

### 8.1 Robust Tool-use

**Challenge**: Current tool-use is brittle—small perturbations or tool failures cascade into reasoning errors.

**Specific Problems**:
1. **Tool Selection Errors**: Model calls wrong tool for the task
2. **Parameter Sensitivity**: Small parameter changes cause large output variations
3. **Failure Propagation**: Tool errors are not detected or recovered from
4. **Tool Versioning**: Tool behavior changes over time (API updates)

**Research Directions**:
- **Tool Error Detection**: Train models to recognize when tools fail
- **Redundant Verification**: Multiple tools cross-validate claims
- **Graceful Degradation**: Fall back to simpler reasoning when tools unavailable
- **Tool Calibration**: Understand tool confidence and uncertainty

**Open Question**: How can models learn robust tool-use policies that generalize to unseen tool combinations?

### 8.2 Adversarial Challenges

#### Prompt Injection

**Challenge**: For Quadrant II and IV methods with web access or external APIs, malicious content can manipulate reasoning.

**Attack Vectors**:
- **Web Content Injection**: Malicious web pages contain hidden instructions
- **Tool Output Poisoning**: Compromised APIs return manipulated results
- **Context Overflow**: Overwhelm model with irrelevant information

**Defenses**:
- **Output Sanitization**: Filter tool outputs before reasoning
- **Source Trust Scoring**: Weight evidence by source reliability
- **Execution Sandboxing**: Isolate code execution from sensitive data
- **Human-in-the-Loop**: Require human approval for high-stakes decisions

**Research Direction**: Adversarial training for tool-use—expose models to injection attempts during training.

#### Data Contamination

**Challenge**: Training data may contain spurious correlations that undermine verifiability.

**Problems**:
- Models learn to produce plausible-looking traces without genuine reasoning
- Benchmark contamination (models memorize test sets)
- Annotation artifacts (human biases in reasoning traces)

**Research Directions**:
- **Contamination Detection**: Identify and filter contaminated training data
- **Robust Evaluation**: Design benchmarks resistant to contamination
- **Process-level Auditing**: Verify that reasoning generalizes beyond memorization

### 8.3 Cost Budgets

**Challenge**: High-verifiability methods (Q4) incur significant computational and monetary costs.

**Cost Components**:
- **Tool API Calls**: Paid APIs (search, specialized services)
- **Compute**: Multiple forward passes, code execution
- **Latency**: Sequential tool calls add up
- **Storage**: Maintaining traces, memory, logs

**Example Cost Breakdown** (per query):
| Component | Q1 | Q2 | Q4 |
|-----------|----|----|----|
| Model Inference | $0.001 | $0.002 | $0.005 |
| Tool Calls | $0 | $0.01 | $0.05 |
| Latency | 100ms | 1000ms | 3000ms |

**Research Directions**:
- **Budget-Aware Reasoning**: Model learns to allocate verification budget optimally
- **Early Exiting**: Stop reasoning when confidence is sufficient
- **Caching**: Reuse tool outputs for similar queries
- **Tiered Verification**: Apply expensive verification only when cheap checks fail

**Open Question**: What is the minimum verification budget needed for a given accuracy/verifiability target?

### 8.4 Standardized Trace Formats

**Challenge**: No standard format for reasoning traces makes comparison, reproduction, and tool integration difficult.

**Current State**:
- Each paper uses custom trace format
- Tools require custom integration
- Benchmarks support limited trace types
- Cross-paper comparison is difficult

**Proposal: Common Trace Schema**:
```json
{
  "step_id": 1,
  "step_type": "perception",
  "description": "Detect objects in image",
  "tool_call": {"name": "detector.detect", "params": {...}},
  "tool_output": {"objects": [...]},
  "grounding": {"type": "bbox", "coords": [x1,y1,x2,y2]},
  "confidence": 0.92,
  "verification_status": "verified"
}
```

**Benefits**:
- Interoperability (tools work with any system using the schema)
- Reproducibility (traces can be re-run)
- Benchmark support (standardized evaluation)
- Cross-paper comparison

**Research Directions**:
- Community effort to define schema (like ONNX for models)
- Tool libraries supporting standard schema
- Benchmark adoption of standard formats
- Trace compression for efficient storage

### 8.5 Reliable Step Rewards

**Challenge**: Defining reward functions that truly capture verifiability, not proxy metrics.

**Current Approaches**:
- **Answer correctness**: Insufficient (correct answer, wrong reasoning)
- **Human preferences**: Expensive, subjective
- **Tool validation**: Limited to tool coverage
- **Consistency**: May reward consistent errors

**Problems**:
- **Reward Hacking**: Model optimizes for reward, not true verifiability
- **Sparse Rewards**: Only final answer has clear reward signal
- **Credit Assignment**: Which steps deserve credit/blame?
- **Multi-objective**: Verifiability vs. accuracy vs. cost trade-offs

**Research Directions**:
- **Dense Rewards**: Step-level feedback from multiple sources
- **Adversarial Rewards**: Penalize traces that fool verifiers but are wrong
- **Human-AI Collaboration**: Combine human judgment with automated checks
- **Causal Rewards**: Reward steps that causally contribute to correct answers

**Open Question**: Can we learn reward functions that generalize to unseen reasoning scenarios?

### 8.6 Real-World Integration Benchmarks

**Challenge**: Current benchmarks are simplified and don't capture real-world complexity.

**Gap Analysis**:
| Aspect | Current Benchmarks | Real-World Needs |
|--------|-------------------|------------------|
| Task Scope | Single-domain | Multi-domain integration |
| Time Pressure | No latency constraints | Real-time requirements |
| Tool Availability | Fixed, reliable tools | Dynamic, unreliable tools |
| Stakes | Low | High (medical, legal, financial) |
| Evaluation | Answer accuracy | Process + outcome + cost |

**Proposal: Real-World Benchmark Suite**:

1. **Clinical Decision Support**
   - Task: Diagnose from medical images + patient history
   - Metrics: Diagnostic accuracy + reasoning faithfulness + time
   - Verification: Radiologist review of reasoning traces

2. **Legal Document Analysis**
   - Task: Extract legal arguments with citations
   - Metrics: Citation accuracy + logical consistency
   - Verification: Lawyer audit of reasoning

3. **Financial Report Interpretation**
   - Task: Analyze earnings reports, make recommendations
   - Metrics: Recommendation quality + traceable logic
   - Verification: Analyst review + backtesting

4. **Scientific Literature Review**
   - Task: Synthesize findings from multiple papers
   - Metrics: Claim accuracy + citation correctness
   - Verification: Domain expert evaluation

**Research Directions**:
- Long-horizon tasks (hours/days, not minutes)
- Multi-tool, multi-source integration
- Human-AI collaboration metrics
- Deployment cost tracking

### 8.7 Emerging Directions

#### Multimodal Foundation Models for Reasoning

New foundation models trained specifically for reasoning (not just QA) may change the landscape:
- Reasoning-centric pretraining objectives
- Built-in tool-use capabilities
- Native support for structured traces

#### Neuro-Symbolic Integration

Combining neural perception with symbolic reasoning:
- Neural networks for perception (flexible, robust)
- Symbolic engines for reasoning (verifiable, checkable)
- Best of both worlds?

#### Human-AI Collaborative Reasoning

Rather than full automation:
- AI proposes reasoning steps
- Humans verify critical steps
- Iterative refinement
- Shared responsibility

---

### 8.6 Real-World Integration Benchmarks

[To be written]

---

## 9 Best Practices

Based on this survey's analysis, we provide design recommendations for building verifiable Visual CoT agents.

### 9.1 Choose the Right Quadrant for Your Application

**Decision Framework**:

| Application Type | Recommended Quadrant | Rationale |
|-----------------|---------------------|-----------|
| Low-stakes QA | Q1 (Text-only) | Cost/latency priority |
| Multi-hop reasoning | Q2 (Text + Tools) | Need external knowledge |
| Spatial/structural tasks | Q3 (Structured) | Automatic checkability needed |
| Safety-critical | Q4 (Structured + Tools) | Maximum verifiability required |

**Questions to Ask**:
1. What is the cost of a reasoning error?
2. Is auditability required (regulatory, legal)?
3. What latency/cost constraints exist?
4. Are reliable tools available for the domain?

### 9.2 Design for Verifiability from the Start

**Principles**:
1. **Explicit Grounding**: Require reasoning to reference specific visual elements
   - Use bounding boxes, coordinates, object IDs
   - Avoid vague references ("the object", "this area")

2. **Structured Traces**: Use machine-checkable formats when possible
   - Programs over prose for computational reasoning
   - Graphs/tables for relational reasoning
   - Sketches for spatial reasoning

3. **Step-Level Verification**: Build verification into each step
   - Tool validation after perception steps
   - Constraint checking after reasoning steps
   - Consistency checks before finalizing answer

4. **Replayability**: Design traces that can be re-run
   - Log all tool calls with parameters
   - Use deterministic operations when possible
   - Version control for tools and models

### 9.3 Tool-Use Best Practices

**Tool Selection**:
- Choose tools with confidence scores (not binary outputs)
- Prefer tools with known failure modes over black boxes
- Use redundant tools for critical claims

**Tool Integration**:
- Wrap tools with error handling and retry logic
- Log all tool inputs and outputs
- Validate tool outputs before using in reasoning

**Tool Orchestration**:
- Parallel tool calls when possible (reduce latency)
- Early exiting (skip unnecessary tools)
- Budget tracking (stop if cost exceeds threshold)

### 9.4 Training Recommendations

**Data Collection**:
- Collect process-level annotations (not just answer labels)
- Include failure cases in training data
- Use verifier-guided filtering for quality

**Training Strategy**:
1. Start with SFT on high-quality traces
2. Add process supervision for step-level feedback
3. Fine-tune with RL for tool-use optimization
4. Use PRM for inference-time guidance

**Evaluation During Training**:
- Track both answer accuracy and process metrics
- Include robustness tests (perturbations, OOD)
- Monitor for reward hacking (RL phase)

### 9.5 Deployment Considerations

**Monitoring**:
- Log all reasoning traces for auditing
- Track tool failure rates and latency
- Alert on anomalous reasoning patterns

**Human-in-the-Loop**:
- Escalate uncertain cases to humans
- Allow human verification of critical steps
- Collect human feedback for continuous improvement

**Safety**:
- Sandbox code execution
- Filter web content (prevent injection)
- Rate limiting (prevent abuse)
- Data privacy (don't leak sensitive information in tool calls)

### 9.6 Documentation and Reporting

**For Research Papers**:
- Report all five process metric categories
- Include failure mode analysis
- Release code and example traces
- Document tool dependencies and versions

**For Production Systems**:
- Document reasoning capabilities and limitations
- Provide example traces (success and failure cases)
- Specify tool requirements and fallbacks
- Include cost/latency benchmarks

---

## 10 Conclusion

This survey has argued for a fundamental re-framing of Visual Chain-of-Thought reasoning: from **explanations** that sound plausible to **evidence** that can be verified.

### Key Takeaways

**1. Verifiability is Multi-Dimensional**

Verifiability is not a binary property but exists on a spectrum determined by:
- **Representation**: Textual rationales → Structured traces
- **Verification Channel**: Internal consistency → External tool feedback

Our 2×2 matrix provides a framework for understanding these dimensions and comparing approaches.

**2. Higher Verifiability Comes at a Cost**

Moving from Quadrant I to Quadrant IV increases verifiability but also increases:
- Computational cost and latency
- System complexity
- Security considerations

The optimal quadrant depends on the application's requirements and constraints.

**3. Process-Level Evaluation is Essential**

Answer accuracy alone is insufficient. We must evaluate:
- Step correctness
- Evidence attribution
- Trace replayability
- Robustness
- Cost/latency

Benchmarks and metrics for these properties are critical for progress.

**4. Training Must Target Verifiability**

Standard SFT produces plausible but potentially unfaithful reasoning. Better approaches include:
- Process supervision (step-level feedback)
- PRM-guided training
- RL with verifiability rewards
- Verifier-guided data collection

**5. Open Challenges Remain**

Significant problems are unsolved:
- Robust tool-use under failures and adversarial attacks
- Cost-aware verification (budget-constrained reasoning)
- Standardized trace formats for interoperability
- Reliable reward functions for training
- Real-world benchmarks capturing deployment complexity

### Call to Action

**For Researchers**:
- Design methods with verifiability as a primary objective, not an afterthought
- Develop benchmarks that reward faithful reasoning, not just correct answers
- Share traces and code to enable reproducibility

**For Practitioners**:
- Choose verification level appropriate to application stakes
- Build monitoring and auditing into deployed systems
- Collect process-level feedback for continuous improvement

**For the Community**:
- Develop standardized trace formats and evaluation protocols
- Create benchmarks for real-world, high-stakes applications
- Establish best practices for safe, verifiable deployment

### Final Thought

The goal is not to eliminate all reasoning errors—that is impossible. The goal is to build systems whose reasoning can be **inspected, validated, and trusted**. When reasoning is verifiable, errors can be caught, decisions can be audited, and users can have justified confidence in the system's outputs.

As multimodal AI systems are deployed in increasingly consequential settings, verifiability is not optional—it is essential. This survey provides the framework, tools, and recommendations for building verifiable Visual CoT systems. The path forward requires sustained effort across the community, but the destination—trustworthy, accountable AI reasoning—is worth the journey.

---

## References

[To be populated from references.bib]

---

## Appendix

### A. Complete Paper List by Quadrant

**Quadrant I: Text-only CoT**
1. CURE (NAACL 2024) - Consistency and Reflection for Visual CoT
[To be populated with systematic search results]

**Quadrant II: Text + Tools**
1. VideoAgent (ECCV 2024) - Multimodal Agent with Memory and Multi-Tool Loop
[To be populated with systematic search results]

**Quadrant III: Structured w/o Tools**
1. MCOUT-style (arXiv 2025) - Continuous Latent Thought States
[To be populated with systematic search results]

**Quadrant IV: Structured + Tools**
1. Visual Sketchpad (NeurIPS 2024) - Sketch as Structured CoT
2. DeepEyesV2 (arXiv 2025) - Code Execution + Web Search
[To be populated with systematic search results]

### B. Evaluation Checklist Details

See Section 6.1 for detailed descriptions of each metric category:
- Step Correctness
- Evidence Attribution
- Trace Replayability
- Robustness
- Cost/Latency

### C. Glossary

| Term | Definition |
|------|------------|
| **Verifiability** | The degree to which reasoning can be checked, validated, and trusted |
| **Faithfulness** | Reasoning accurately reflects the model's actual decision process |
| **Grounding** | Reasoning is linked to specific, identifiable visual elements |
| **Replayability** | Reasoning trace can be re-run to reproduce the result |
| **Process Supervision** | Training with step-level feedback (not just answer-level) |
| **PRM** | Process Reward Model—scores individual reasoning steps |

---

**Document Status**: Draft v0.1

**Last Updated**: 2026-03-03

**Authors**: [To be completed]

**Contact**: [To be completed]

[To be written]

### C. Glossary

[To be written]
