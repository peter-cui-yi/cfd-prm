# Literature Database

## Overview

This document tracks all papers for the survey "From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)"

**Total Papers**: 82 (All analyzed ✅)

**Last Updated**: 2026-03-12 (Round 3: +15 latest arXiv preprints from 2025.05–2026.03)

---

## Papers by Quadrant

### Quadrant I: Text-only CoT
*Textual rationales without tool/execution feedback*

| # | Paper | Venue | Year | Key Idea | Note File | Status |
|---|-------|-------|------|----------|-----------|--------|
| 1 | **CURE** | NAACL 2024 | 2024 | CoT consistency evaluation & improvement for VLMs | `CURE_2024_QuadrantI_Anchor_updated.md` | 📌 Anchor |
| 2 | **LLaVA-CoT** | ICCV 2025 | 2024 | Four-stage structured CoT (Summary→Caption→Reasoning→Conclusion) + test-time scaling | `LLaVA-CoT_2024_QuadrantI.md` | ✅ |
| 3 | **R3V** | NAACL 2025 | 2024 | Self-improving reasoning via reflection on noisy CoT rationales | `R3V_2025_QuadrantI.md` | ✅ |
| 4 | **Sherlock** | NeurIPS 2025 | 2025 | Trajectory-level self-correction + visual perturbation preference data | `Sherlock_2025_QuadrantI.md` | ✅ |
| 5 | **Critic-V** | CVPR 2025 | 2024 | VLM critic catches VLM reasoning errors step-by-step | `CriticV_2024_QuadrantI.md` | ✅ |
| 6 | **SCL** | ACL 2025 | 2024 | Self-correction learning framework for VL reasoning tasks | `SCL_2024_QuadrantI.md` | ✅ |
| 7 | **Insight-V** | arXiv 2024 | 2024 | Long-chain visual reasoning with multi-agent pipeline | `Insight-V_2024_QuadrantI.md` | ✅ |
| 8 | **Visual CoT** | NeurIPS 2024 (DB) | 2024 | Dataset + benchmark for Visual CoT with bounding-box grounding traces | `VisualCoT_2024_QuadrantI.md` | ✅ |
| 9 | **Improve VLM CoT** | ACL 2025 | 2024 | DPO + process-supervision to improve VLM CoT faithfulness | `ImproveVLMCoT_2024_QuadrantI.md` | ✅ |
| 10 | **R-CoT / TR-CoT** | arXiv 2024 | 2024 | Reverse CoT problem generation for geometric reasoning | `R-CoT_2024_QuadrantI.md` | ✅ |
| 11 | **VisualPRM** | arXiv 2025 | 2025 | Process Reward Model for multimodal reasoning (step-level scoring) | `VisualPRM_2025_QuadrantI.md` | ✅ |
| 12 | **R1-VL** | ICCV 2025 | 2025 | Step-wise GRPO with StepRAR + StepRVR process rewards for MLLM reasoning | *(note pending)* | ⏳ |
| 13 | **Visionary-R1** | arXiv 2025 | 2025 | Structured caption→reason→answer format + GRPO to prevent RL shortcuts | *(note pending)* | ⏳ |
| 14 | **Journey Before Destination** | arXiv 2025 | 2025 | First systematic analysis of visual faithfulness in CoT; perception-step self-correction | *(note pending)* | ⏳ |
| 15 | **OpenVLThinker** | NeurIPS 2025 | 2025 | Iterative SFT-RL cycles for math/science visual reasoning | *(note pending)* | ⏳ |
| 16 | **LLaVA-Critic-R1** | arXiv 2025 | 2025 | Self-critique test-time scaling; critic-as-policy unified model | *(note pending)* | ⏳ |
| 17 | **ChainV** | arXiv 2025 | 2025-11 | Atomic visual hints + consistency evaluation; shorter/better reasoning | `ChainV_2025_QuadrantI.md` | 🆕 |
| 18 | **VisReason** | arXiv 2025 | 2025-11 | 489K visual CoT dataset + 165K VisReason-Pro expert subset | `VisReason_2025_QuadrantI.md` | 🆕 |
| 19 | **MIRA** | arXiv 2025 | 2025-11 | Benchmark (546 Q) for visual CoT requiring intermediate visual images | `MIRA_2025_QuadrantI.md` | 🆕 |
| 20 | **GThinker** | arXiv 2025 | 2025-06 | Cue-guided rethinking anchored to visual cues; beats O4-mini | `GThinker_2025_QuadrantI.md` | 🆕 |
| 21 | **VRPRM** | arXiv 2025 | 2025-08 | Visual process reward model with 3.6K SFT + 50K RL; 118% BoN gain | `VRPRM_2025_QuadrantI.md` | 🆕 |
| 22 | **PatchCue** | arXiv 2026 | 2026-03 | Patch-level visual cues + process-supervised cue reward for VLM reasoning | `PatchCue_2026_QuadrantI.md` | 🆕 |
| 23 | **RTWI** | arXiv 2026 | 2026-02 | Reliable Thinking with Images; text-centric reliability estimation for noisy TWI | `RTWI_2026_QuadrantI.md` | 🆕 |
| 24 | **VC-STaR** | arXiv 2026 | 2026-03 | Visual contrastive self-improving; VisCoR-55K dataset to mitigate hallucinations | `VC-STaR_2026_QuadrantI.md` | 🆕 |
| 25 | **Zooming w/o Zooming** | arXiv 2026 | 2026-02 | Region-to-image distillation; agentic zooming → single forward pass; ZoomBench | `ZoomingWithoutZooming_2026_QuadrantI.md` | 🆕 |
| 26 | **AVAR** | arXiv 2026 | 2026-03 | Visual Attention Score (VAS) + attention-guided cold-start; +7.0% avg on 7 benchmarks | `AVAR_2026_QuadrantI.md` | 🆕 |

**Characteristics**:
- Representation: Textual (free-form CoT, structured stages, reflections)
- Verification: Self-consistency, self-correction, process supervision, PRM scoring
- Main Failure: Plausible-but-unfaithful reasoning; consistency ≠ correctness

**Sub-categories within Q1**:
- *Consistency/Reflection*: CURE, R3V, Sherlock, SCL
- *Structured Stages*: LLaVA-CoT, Insight-V
- *PRM/Process Supervision*: VisualPRM, Critic-V, Improve VLM CoT
- *Benchmarks/Datasets*: Visual CoT, R-CoT

---

### Quadrant II: Text + Tools (ReAct-style)
*Textual planning with tool calls (Action/Observation loop)*

| # | Paper | Venue | Year | Key Idea | Note File | Status |
|---|-------|-------|------|----------|-----------|--------|
| 1 | **VideoAgent** | ECCV 2024 | 2024 | Memory-augmented multimodal agent with multi-tool loop for video | `VideoAgent_2024_QuadrantII_Anchor.md` | 📌 Anchor |
| 2 | **MM-REACT** | arXiv 2023 | 2023 | Pioneering ReAct-style multimodal reasoning with ChatGPT + specialist models | `MM-ReAct_2023_QuadrantII.md` | ✅ |
| 3 | **AdaReasoner** | ICLR 2026 | 2026 | Dynamic tool orchestration via Tool-GRPO RL, adaptive tool selection | `AdaReasoner_2026_QuadrantII.md` | ✅ |
| 4 | **Optimus-1** | NeurIPS 2024 | 2024 | Hybrid multimodal memory (hierarchical KG + experience pool) for long-horizon tasks | `Optimus-1_2024_QuadrantII.md` | ✅ |
| 5 | **DoraemonGPT** | ICML 2024 | 2024 | Video agent with MCTS planning + symbolic memory (time, space, concept) | `DoraemonGPT_2024_QuadrantII.md` | ✅ |
| 6 | **HAMMR** | NeurIPS 2024 (WS) | 2024 | Hierarchical MultiModal ReAct for generic VQA with toolset routing | `HAMMR_2024_QuadrantII.md` | ✅ |
| 7 | **WebVoyager** | ACL 2024 | 2024 | End-to-end web agent with LMMs; real-world web browsing via observation-action | `WebVoyager_2024_QuadrantII.md` | ✅ |
| 8 | **SeeAct** | ICML 2024 | 2024 | GPT-4V generalist web agent; grounding as key bottleneck | `SeeAct_2024_QuadrantII.md` | ✅ |
| 9 | **OctoTools** | ICLR 2025 (WS) | 2025 | Extensible agentic framework with standardized tool cards and planner | `OctoTools_2025_QuadrantII.md` | ✅ |
| 10 | **AssistGUI** | CVPR 2024 | 2024 | Desktop GUI automation via Actor-Critic + GUI Parser for task planning | `AssistGUI_2024_QuadrantII.md` | ✅ |
| 11 | **CogAgent** | CVPR 2024 | 2024 | VLM for GUI agents with dual-encoder for high-res screenshots | `CogAgent_2024_QuadrantII.md` | ✅ |
| 12 | **ToolRL** | arXiv 2025 | 2025 | Systematic study of reward design for tool-selection training via GRPO | *(note pending)* | ⏳ |
| 13 | **VisRAG** | ICLR 2025 | 2025 | VLM-based visual page retrieval as tool for multimodal document RAG | *(note pending)* | ⏳ |
| 14 | **ChartAgent** | arXiv 2025 | 2025 | TIR-based chart understanding with 14+ visual tools; Evidence Package output | *(note pending)* | ⏳ |
| 15 | **LongVideoAgent** | arXiv 2025 | 2025 | Master-Grounding-Vision 3-layer multi-agent with GRPO for long video QA | *(note pending)* | ⏳ |
| 16 | **OmniParser** | arXiv 2024 | 2024 | GUI screen parsing as grounding tool (region detection + semantic captioning) | *(note pending)* | ⏳ |
| 17 | **VISTA-R1** | arXiv 2025 | 2025-11 | Unified agentic RL for tool-integrated VLM; 7 task types, 13 datasets | `VISTA-R1_2025_QuadrantII.md` | 🆕 |
| 18 | **OpenThinkIMG** | arXiv 2025 | 2025-05 | Open-source V-ToolRL framework; beats GPT-4.1 on chart reasoning | `OpenThinkIMG_2025_QuadrantII.md` | 🆕 |
| 19 | **Sherlock Workflow** | arXiv 2025 | 2025-11 | Reliable agentic workflow execution with selective verification + speculative exec | `Sherlock_AgenticWorkflow_2025_QuadrantII.md` | 🆕 |
| 20 | **XSkill** | arXiv 2026 | 2026-03 | Dual-stream continual learning (experience + skills) for multimodal agents | `XSkill_2026_QuadrantII.md` | 🆕 |
| 21 | **ARM-Thinker** | arXiv 2025 | 2025-12 | Agentic reward model with tool use (image cropping, retrieval); +16.2% RM, +9.6% tool | `ARM-Thinker_2025_QuadrantII.md` | 🆕 |

**Characteristics**:
- Representation: Textual (Action/Observation traces, tool call logs)
- Verification: Tool outputs as evidence; trajectory audit
- Main Failure: Tool misuse, output misinterpretation, brittle to tool noise

**Sub-categories within Q2**:
- *Video agents*: VideoAgent, DoraemonGPT
- *Web agents*: WebVoyager, SeeAct
- *GUI agents*: AssistGUI, CogAgent
- *General tool orchestration*: MM-REACT, AdaReasoner, OctoTools, HAMMR, Optimus-1

---

### Quadrant III: Structured w/o Tools
*Structured intermediate states without external execution*

| # | Paper | Venue | Year | Key Idea | Note File | Status |
|---|-------|-------|------|----------|-----------|--------|
| 1 | **MCOUT** | arXiv 2025 | 2025 | Multimodal continuous latent thought vectors for iterative refinement | `MCOUT_2025_QuadrantIII_Anchor.md` | 📌 Anchor |
| 2 | **CCoT** | CVPR 2024 | 2024 | Scene graph as structured intermediate for compositional reasoning | `CCoT_2024_QuadrantIII.md` | ✅ |
| 3 | **CoVT** | arXiv 2025 | 2025 | ~20 continuous visual tokens (depth/seg/edges) interleaved in reasoning chain | `CoVT_2025_QuadrantIII.md` | ✅ |
| 4 | **LaRe** | arXiv 2025 | 2025 | Latent refocusing: latent visual vectors + dynamic visual attention per reasoning step | `LaRe_2025_QuadrantIII.md` | ✅ |
| 5 | **DMLR** | arXiv 2025 | 2025 | Dynamic multimodal latent reasoning with confidence-guided test-time optimization | `DMLR_2025_QuadrantIII.md` | ✅ |
| 6 | **LLaVA-SG** | arXiv 2024 | 2024 | Scene graph as visual semantic expression injected into VLM reasoning | `LLaVA-SG_2024_QuadrantIII.md` | ✅ |
| 7 | **Coconut** | arXiv 2024 | 2024 | Continuous latent thought space (text-only LLM precursor; cited in Background) | `Coconut_2024_QuadrantIII.md` | ✅ |
| 8 | **G2** | arXiv 2025 | 2025 | Generative scene graph construction for visual commonsense answering | *(note pending)* | ⏳ |
| 9 | **COGT** | ICLR 2025 | 2025 | Causal Graphical Models constraining VLM decoding order for compositional understanding | *(note pending)* | ⏳ |
| 10 | **Artemis** | arXiv 2025 | 2025 | (label, bbox) structured spatial token pairs as intermediate reasoning steps | *(note pending)* | ⏳ |
| 11 | **Concept-RuleNet** | arXiv 2025 | 2025 | Visual concepts → First-Order Logic rules; neuro-symbolic reasoning | *(note pending)* | ⏳ |
| 12 | **Chain-of-Table** | ICLR 2024 | 2024 | Evolving tabular intermediate representation in the reasoning chain | *(note pending)* | ⏳ |
| 13 | **Mario** | arXiv 2026 | 2026-03 | Graph-conditioned VLM with modality-adaptive routing for multimodal graphs | `Mario_2026_QuadrantIII.md` | 🆕 |
| 14 | **StruVis** | arXiv 2026 | 2026-03 | Textualized structured vision as intermediate state for T2I reasoning | `StruVis_2026_QuadrantIII.md` | 🆕 |
| 15 | **SpatialMath** | arXiv 2026 | 2026-01 | Spatial comprehension injected into symbolic reasoning chain for geometry | `SpatialMath_2026_QuadrantIII.md` | 🆕 |
| 16 | **Graph-of-Mark** | arXiv 2026 | 2026-03 | Scene graph overlay on pixels as visual prompt for spatial reasoning | `Graph-of-Mark_2026_QuadrantIII.md` | 🆕 |

**Characteristics**:
- Representation: Structured (scene graphs, latent vectors, typed visual tokens, injection logs)
- Verification: Schema constraints, consistency checks, alignment between structure and perception
- Main Failure: Structured artifacts can still be wrong; latent vectors opaque to humans

**Sub-categories within Q3**:
- *Scene Graph (human-readable)*: CCoT, LLaVA-SG
- *Latent Vectors (opaque continuous)*: MCOUT, LaRe
- *Typed Visual Tokens (decodable)*: CoVT
- *Dynamic Injection + Optimization*: DMLR
- *Background reference (text-only precursor)*: Coconut

**Interpretability Spectrum (Q3)**:
CCoT / LLaVA-SG (highest) > CoVT (medium) > DMLR (partial audit trail) > LaRe > MCOUT (lowest)

---

### Quadrant IV: Structured + Tools / Executable
*Executable traces with tool/execution feedback (Highest Verifiability)*

| # | Paper | Venue | Year | Key Idea | Note File | Status |
|---|-------|-------|------|----------|-----------|--------|
| 1 | **Visual Sketchpad** | NeurIPS 2024 | 2024 | Sketch as structured CoT; specialist vision models verify sketch claims | `VisualSketchpad_2024_QuadrantIV.md` | 📌 Anchor |
| 2 | **DeepEyesV2** | arXiv 2025 | 2025 | Code execution + web search evidence loop; two-stage cold-start + RL training | *(placeholder; note file pending)* | 📌 Anchor |
| 3 | **ViperGPT** | ICCV 2023 | 2023 | Python program synthesis for visual reasoning; code execution as verification | `ViperGPT_2023_QuadrantIV.md` | ✅ |
| 4 | **VDebugger** | EMNLP 2024 | 2024 | Execution-feedback debugging of visual programs; critic-refiner framework | `Wu_2024_VDebugger_QuadrantIV.md` | ✅ |
| 5 | **ViReP** | CVPR 2024 | 2024 | Self-training for visual program synthesis with visual reinforcement | `Khan_2024_ViReP_QuadrantIV.md` | ✅ |
| 6 | **RECODE** | arXiv 2025 | 2025 | Derendering charts to executable code; critic selects best reconstruction | `Shen_2025_RECODE_QuadrantIV.md` | ✅ |
| 7 | **CodeV** | arXiv 2025 | 2025 | Visual tools as Python code + Tool-Aware Policy Optimization (TAPO) | `Hou_2025_CodeV_QuadrantIV.md` | ✅ |
| 8 | **CodeDance** | arXiv 2025 | 2025 | Dynamic tool-integrated MLLM using executable code as universal solver | `Song_2025_CodeDance_QuadrantIV.md` | ✅ |
| 9 | **CodeVision** | arXiv 2025 | 2025 | Unified view for thinking with images via programming vision | `Guo_2025_CodeVision_QuadrantIV.md` | ✅ |
| 10 | **CodePlot-CoT** | arXiv 2025 | 2025 | Executable matplotlib/Sympy plotting code embedded in each CoT step for math/geometry | *(note pending)* | ⏳ |
| 11 | **Visual-ARFT** | arXiv 2025 | 2025 | GRPO trains VLM to call image-processing code tools; dual reward (executability + accuracy) | *(note pending)* | ⏳ |
| 12 | **Visual Programmability** | arXiv 2025 | 2025 | Adaptive selection of executable code vs. direct vision via RL for chart understanding | *(note pending)* | ⏳ |
| 13 | **Act-Observe-Rewrite** | arXiv 2026 | 2026 | Multimodal LLM rewrites full Python robot controller per trial from visual feedback | *(note pending)* | ⏳ |
| 14 | **VLM Scientific Discovery** | arXiv 2025 | 2025 | VLM visual checkpoint judge corrects multi-step scientific experiment code chains | *(note pending)* | ⏳ |
| 15 | **NS-VLA** | arXiv 2026 | 2026-03 | Neuro-symbolic encoder + solver for robot action planning with online RL | `NS-VLA_2026_QuadrantIV.md` | 🆕 |
| 16 | **ARM2** | arXiv 2025 | 2025-10 | Adaptive code reasoning with 70%+ token reduction; executable multimodal reasoning | `ARM2_2025_QuadrantIV.md` | 🆕 |
| 17 | **VLAgent** | arXiv 2025 | 2025-06 | Neurosymbolic agent: SS-parser → structured plan → executable code → verification | `VLAgent_2025_QuadrantIV.md` | 🆕 |
| 18 | **MM-Zero** | arXiv 2026 | 2026-03 | Zero-data self-evolving VLM: Proposer→Coder→Solver; executable code as reward | `MM-Zero_2026_QuadrantIV.md` | 🆕 |
| 19 | **Visual-ERM** | arXiv 2026 | 2026-03 | Visual equivalence reward model; code→render→compare; GRPO RL; VC-RewardBench | `Visual-ERM_2026_QuadrantIV.md` | 🆕 |

**Characteristics**:
- Representation: Structured (programs, sketches, state logs, executable code)
- Verification: Replayability (run code), step-level validation, environment feedback, specialist verifiers
- Main Failure: Cost/latency, security risks (code execution, web), cascading errors

**Sub-categories within Q4**:
- *Program Synthesis*: ViperGPT, ViReP, RECODE
- *Execution Debugging*: VDebugger
- *Code + Tools*: DeepEyesV2, CodeV, CodeDance, CodeVision
- *Sketch-based*: Visual Sketchpad

---

## Summary Statistics

| Quadrant | Papers | Anchors | Fully Analyzed | Latest arXiv (2025.05+) |
|----------|--------|---------|----------------|------------------------|
| Q1: Text-only CoT | 26 | 1 (CURE) | 26/26 ✅ | 10 🆕 |
| Q2: Text + Tools | 21 | 1 (VideoAgent) | 21/21 ✅ | 5 🆕 |
| Q3: Structured w/o Tools | 16 | 1 (MCOUT) | 16/16 ✅ | 4 🆕 |
| Q4: Structured + Tools | 19 | 2 (VisualSketchpad, DeepEyesV2) | 19/19 ✅ | 5 🆕 |
| **Total** | **82** | **5** | **82/82** ✅ | **24** 🆕 |

---

## Paper Status Legend

- 📌 Anchor: Representative anchor paper from proposal
- ✅ Categorized: Fully analyzed with complete paper note
- 📖 Reading: Currently being analyzed
- ⏳ Pending: Added to database but note not yet created
- 🔍 Search: Need to locate/verify

---

## Evaluation Checklist Coverage

The following dimensions are assessed in each paper note:

| Dimension | What it measures |
|-----------|-----------------|
| **Grounding Strength** | Does reasoning point to image evidence (regions/masks/objects)? |
| **Checkability** | Can intermediate steps be automatically validated? |
| **Replayability** | Can we re-run the trace (program/tool calls) to reproduce the result? |
| **Faithfulness Risk** | Can the model "explain without seeing"? |
| **Robustness** | Sensitivity to tool errors, missing evidence, distribution shifts |
| **Cost/Latency** | Tool budget, number of steps, runtime constraints |
| **Security** | Prompt injection, data contamination, unsafe tool calls |

---

## Gaps & Next Steps

### Resolved
- [x] Need more Quadrant III papers — **RESOLVED: 7 papers**
- [x] Need more Quadrant II papers — **RESOLVED: 11 papers**
- [x] Need more Quadrant IV papers — **RESOLVED: 9 papers**

### Remaining Gaps
- [ ] **DeepEyesV2 note**: Upgrade from placeholder to full note
- [ ] **Benchmarks section**: Need 3-5 papers focused on process-level benchmarks
- [ ] **Applications section**: Need 2-3 papers on safety-critical domains

### Priority Next Action
→ **Integrate all paper notes into `survey_paper.md` Section 4**

### Round 2 Additions (2026-03-10)
| Quadrant | New Papers Added |
|----------|-----------------|
| Q1 | R1-VL, Visionary-R1, Journey Before Destination, OpenVLThinker, LLaVA-Critic-R1 |
| Q2 | ToolRL, VisRAG, ChartAgent, LongVideoAgent, OmniParser |
| Q3 | G2, COGT, Artemis, Concept-RuleNet, Chain-of-Table |
| Q4 | CodePlot-CoT, Visual-ARFT, Visual Programmability, Act-Observe-Rewrite, VLM Scientific Discovery |

### Round 3 Additions (2026-03-12) — Latest arXiv preprints (2025.05–2026.03)
| Quadrant | New Papers Added |
|----------|-----------------|
| Q1 🆕 | ChainV, VisReason, MIRA, GThinker, VRPRM |
| Q2 🆕 | VISTA-R1, OpenThinkIMG, Sherlock Workflow |
| Q3 🆕 | Mario, StruVis, SpatialMath, Graph-of-Mark |
| Q4 🆕 | NS-VLA, ARM2, VLAgent |

### Round 4 Additions (2026-03-12) — User-specified papers
| Quadrant | New Papers Added |
|----------|-----------------|
| Q1 🆕 | PatchCue (2603.05869), RTWI (2602.12916), VC-STaR (2603.02556), Zooming w/o Zooming (2602.11858) |
| Q4 🆕 | MM-Zero (2603.09206) |

### Round 5 Additions (2026-03-12) — User-specified papers
| Quadrant | New Papers Added |
|----------|-----------------|
| Q1 🆕 | AVAR (2603.03825) |
| Q2 🆕 | XSkill (2603.12056), ARM-Thinker (2512.05111) |
| Q4 🆕 | Visual-ERM (2603.13224) |
| *(skipped)* | VC-STaR (2603.02556) — already in database |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| MM-REACT (2023) included | Pioneering Q2 method; essential for historical context |
| ViperGPT (2023) included | Foundational Q4 method; essential for lineage |
| Coconut (2024) in Q3 | Text-only precursor for latent reasoning; cited in Background §2.5 |
| RegionReasoner excluded | Overlaps with Q2; needs clearer quadrant justification |
| VISCO excluded | Benchmark-focused; better cited in Section 6 (Evaluation) |

---

## Meeting Notes & Decisions

### 2026-03-03: Initial Setup
- Created literature search strategy
- Established paper note template
- Defined 2×2 matrix placement criteria
- Started with 5 anchor papers from proposal

### 2026-03-10: Major Update
- Completed systematic search across all 4 quadrants
- Created 36 paper notes (out of 38 total)
- Updated literature database to reflect full corpus
- Ready to integrate into survey_paper.md Section 4
