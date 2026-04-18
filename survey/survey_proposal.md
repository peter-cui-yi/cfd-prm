# Survey Proposal (README)
## Title
**From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)**

## TL;DR
This survey re-frames **Visual Chain-of-Thought (Visual CoT)** as an **interface for verifiable reasoning** rather than a narrative explanation. We organize recent (2024–present) multimodal reasoning and visual agents through a **2×2 Verifiability Matrix** that separates:
1) **what** intermediate reasoning looks like (text vs. structured traces), and  
2) **how** it can be verified (no tools vs. tool/execution feedback).

---

## Motivation
Recent MLLMs can “explain” answers with fluent multi-step rationales, yet these rationales are often:
- **not grounded** in the actual visual evidence (faithfulness issue),
- **hard to audit** step-by-step,
- **fragile** under distribution shifts and open-world conditions,
- **prone to hallucination** despite plausible CoT.

**Key premise:** reasoning becomes more trustworthy when intermediate steps are **machine-checkable** and/or **externally verifiable**.

---

## Scope (2024–Present)
We focus on methods and systems that:
- produce **multi-step visual reasoning** (CoT, plans, traces),
- improve **faithfulness / grounding / verifiability**,
- enable **agentic loops** (observe → plan → act/tool → verify → answer),
- propose **benchmarks/metrics** for process-level evaluation.

---

## Core Thesis
> **Verifiability increases when**  
> (a) intermediate reasoning artifacts become **machine-checkable** (structured traces), and/or  
> (b) reasoning is grounded to **externally verifiable channels** (tools/execution/feedback).

---

## Main Taxonomy: 2×2 Verifiability Matrix
### Axis A — Intermediate Representation
- **Textual rationales:** free-form CoT / plan / reflection (human-readable, but not inherently checkable)
- **Structured traces:** machine-checkable intermediate artifacts (tables, graphs, programs, state logs, continuous latent states)

### Axis B — Verification Channel
- **No tools / no execution:** no external execution feedback; verification mainly via consistency/constraints/process supervision
- **Tool-/execution-augmented:** uses tools (detectors, OCR, retrieval, code execution, web) or executable programs; allows replay & verification

### 2×2 Quadrants
| | **No tools / no execution** | **Tool-/execution-augmented** |
|---|---|---|
| **Textual rationale** | (I) **Text-only CoT** | (II) **Text + Tools (ReAct-style)** |
| **Structured trace** | (III) **Structured w/o Tools** | (IV) **Structured + Tools / Executable** |

---

## Quadrant Definitions + What to Discuss
### (I) Text-only CoT
**What it is:** free-form step-by-step natural language reasoning, without external tool feedback.  
**Verification levers:** self-consistency, reflection/critique, process supervision, rationale evaluation.  
**Typical failure:** plausible-but-unfaithful reasoning; “looks right” but not evidence-based.

**Representative anchor (2024–present):**
- CURE / CoT consistency–style evaluation & improvement for VLM reasoning (NAACL 2024)

---

### (II) Text + Tools (ReAct-style)
**What it is:** textual planning + tool calls (Action/Observation loop). Tools provide reproducible evidence.  
**Verification levers:** tool outputs as evidence; trajectory audit (actions + observations).  
**Typical failure:** tool misuse, tool-output misinterpretation, brittle to tool noise, prompt injection (web).

**Representative anchor (2024–present):**
- VideoAgent-style multimodal agent with memory + multi-tool loop (ECCV 2024)

---

### (III) Structured w/o Tools
**What it is:** intermediate states are structured (schema/graph/latent vectors), but not externally executed.  
**Verification levers:** schema constraints, consistency checks, alignment between structured state and perception.  
**Typical failure:** structured artifacts can still be wrong; need principled step correctness metrics.

**Representative anchor (2024–present):**
- Continuous/latent “thought state” reasoning (MCOUT-style, arXiv 2025)

---

### (IV) Structured + Tools / Executable (Highest Verifiability)
**What it is:** intermediate traces are executable or operationally grounded (programs, sketches, state logs) + tool/execution feedback.  
**Verification levers:** replayability (run code), step-level validation, environment feedback, specialist verifiers.  
**Typical failure:** cost/latency; security risks (web); cascading errors; tool interface mismatch.

**Representative anchors (2024–present):**
- Visual Sketchpad-style “sketch as structured CoT” (NeurIPS 2024)
- DeepEyesV2-style “code execution + web search” evidence loop (arXiv 2025)

---

## What This Survey Contributes
1. **A verifiability-centric taxonomy** that cleanly separates *representation* vs. *verification channel*.
2. **A design space** for verifiable multimodal reasoning: grounding, trace formats, replay, tool reliability, memory/state.
3. **Process-level evaluation synthesis:** beyond answer accuracy → step correctness, evidence attribution, trace replayability, robustness, cost.
4. **Training & alignment map:** SFT rationale → process supervision → PRM/RL/DPO; cold-start + RL for tool-use as a recurring pattern.
5. **Open problems & recommendations:** security, standardized trace formats, faithful tool-use, budget-aware verification, benchmarks for real-world integration.

---

## Proposed Paper Structure (Outline)
1. **Introduction:** From explanations → evidence (why verifiability is the missing piece)
2. **Background:** faithfulness vs. plausibility; grounding; agent loop; what “verification” means in multimodal settings
3. **Taxonomy (2×2 Matrix):** definitions, examples, and key trade-offs
4. **Methods by Quadrant:**
   - I: consistency, reflection, rationale supervision
   - II: ReAct-style tool loops, memory, tool orchestration
   - III: structured/latent traces, schema constraints
   - IV: executable traces, program/sketch/state logs + external verification
5. **Learning & Alignment for Verifiability:** process supervision, PRM/RL/DPO, cold-start, verifier-guided training data
6. **Evaluation Protocols & Benchmarks:** process metrics + integrated capability benchmarks (perception/search/reasoning)
7. **Applications (optional but strong):** safety-critical / vertical domains requiring auditability
8. **Challenges & Future Directions:** robust tool-use, adversarial web, cost budgets, standard traces, reliable step rewards

---

## Evaluation Checklist (What we’ll compare across papers)
- **Grounding strength:** does the reasoning point to image evidence (regions/masks/objects)?
- **Checkability:** can intermediate steps be automatically validated?
- **Replayability:** can we re-run the trace (program/tool calls) to reproduce the result?
- **Faithfulness risk:** can the model “explain without seeing”?
- **Robustness:** sensitivity to tool errors, missing evidence, distribution shifts
- **Cost/latency:** tool budget, number of steps, runtime constraints
- **Security:** prompt injection, data contamination, unsafe tool calls (especially web)

---

## Working Protocol (How we add papers)
For each candidate paper/system (2024–present), we will record:
1) **2×2 cell placement** (dominant aspect),  
2) representation type (text / structured),  
3) verification channel (none / tools / execution),  
4) failure modes + evaluation signals,  
5) how it connects to prior paradigms (ReAct/ToT/verification, etc.).

### Note Template (for each paper)
Use the existing Markdown template in our workflow:
- Abstract Summary
- Methodology Analysis (explicitly: representation + verification channel)
- Pros & Cons (verifiability-focused)
- Survey Placement (must include 2×2 cell + linkage)

---

## Deliverables (for the final survey)
- 1–2 figures: **2×2 matrix** + “verifiability spectrum”
- 2–3 tables:
  - method comparison by quadrant (representation/verification/training/eval)
  - benchmark & metric mapping (answer vs. process)
  - tool-use reliability & security considerations
- A “best practices” section for designing verifiable Visual CoT agents

---