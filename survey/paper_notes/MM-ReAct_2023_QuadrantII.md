# Paper Note: MM-REACT

## Basic Information

**Title**: MM-REACT: Prompting ChatGPT for Multimodal Reasoning and Action

**Authors**: Zhengyuan Yang, Linjie Li, Jianfeng Wang, Kevin Lin, Ehsan Azarnasab, Faisal Ahmed, Zicheng Liu, Ce Liu, Michael Zeng, Lijuan Wang

**Affiliations**: Microsoft Azure AI, Microsoft Research

**Venue**: arXiv 2023

**Year**: 2023

**Link**:
- ArXiv: https://arxiv.org/abs/2303.11381
- Project Page: https://multimodal-react.github.io/
- Code/Demo available at project page

---

## Abstract Summary

MM-REACT proposes a system paradigm that integrates ChatGPT with a pool of vision experts to achieve multimodal reasoning and action via the ReAct framework. The system uses a textual prompt design that serializes visual inputs (image descriptions, textualized spatial coordinates, file path references) into text that ChatGPT can process, then ChatGPT decides which vision specialist to invoke. Through zero-shot prompting, MM-REACT demonstrates capabilities in complex visual tasks that exceed single VLM abilities: celebrity recognition, optical character recognition, object detection with spatial reasoning, image editing requests, and multi-image reasoning.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [ ] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Text + Tools / ReAct-style)

**Justification**:

MM-REACT belongs to Quadrant II for the following reasons:

1. **Textual Reasoning Representation**: ChatGPT's reasoning is expressed entirely in natural language — it produces thoughts (reasoning steps), actions (tool invocation with arguments), and observations (tool outputs) as plain text following the ReAct template. The representation is not a structured program, graph, or formal trace — it is free-form natural language reasoning interspersed with tool calls.

2. **Tool-Augmented with External Vision Experts**: MM-REACT integrates a diverse pool of vision specialist tools: BLIP-2 (image captioning/VQA), Azure Computer Vision (image tagging, dense captions), Bing Image Search (web image retrieval), Azure Form Recognizer (OCR/document understanding), Azure Celebrity Recognizer, and Azure Object Detection. These tools provide externally grounded, verifiable evidence that ChatGPT cannot generate from parametric knowledge alone.

3. **Tool Outputs as Verification Evidence**: When ChatGPT invokes `[image caption tool] -> "A dog sitting on a red sofa"`, the returned caption is external evidence from a specialized model. Unlike Quadrant I (CURE, LLaVA-CoT) where all reasoning is internal to one model, MM-REACT's tool outputs can be independently verified by running the same tools on the same image.

4. **Contrast with Quadrant IV (ViperGPT)**: ViperGPT generates a complete Python program that is then executed. MM-REACT does not generate a program — ChatGPT interleaves reasoning and tool calls in natural language, making individual decisions about which tool to invoke next. This is the ReAct pattern (natural language + tool calls) rather than program synthesis.

---

## Key Contributions

1. **Textual Prompt Design for Multimodal Tool Use**: Introduces a prompt serialization strategy that converts visual information into text ChatGPT can reason about: (i) text descriptions replace image pixels, (ii) spatial coordinates are textualized (e.g., "bounding box [100, 200, 300, 400]"), (iii) file paths reference dense visual signals. This enables a text-only LLM (ChatGPT) to coordinate vision tools without direct pixel access.

2. **Comprehensive Vision Expert Pool**: Assembles a diverse set of vision specialists covering: captioning, dense captioning, tagging, OCR, celebrity/landmark recognition, object detection with spatial information, face recognition, image search, and video understanding. The modular design allows adding new experts without retraining the reasoning model.

3. **Zero-Shot Generalization to Complex Visual Tasks**: Demonstrates that ChatGPT + vision tools achieves zero-shot capabilities on tasks that dedicated VLMs struggle with: identifying who is in a photo (celebrity recognition), reading nested text in receipts (OCR + spatial reasoning), planning image editing actions, and answering questions about multiple images simultaneously.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: High
- Tool outputs provide externally grounded evidence: OCR returns actual text detected in the image; object detectors return coordinates and categories; celebrity recognition returns name + confidence
- ChatGPT's reasoning explicitly references tool outputs: "According to the OCR tool, the text says 'SALE 50% OFF'"
- Spatial coordinates from detection tools ground reasoning to specific image regions
- Unlike pure VLM reasoning, tool-returned evidence can be independently verified by running the same tools on the same image

### Checkability
**Assessment**: Moderate-High
- Complete ReAct trace logs all tool calls, arguments, and returned observations — these can be reviewed and audited
- Tool outputs are deterministic (same image → same OCR result) enabling reproducibility checking
- ChatGPT's reasoning steps can be checked for logical consistency with tool outputs
- Limitation: Cannot automatically verify whether ChatGPT correctly interprets or aggregates multiple tool outputs
- Limitation: Tool selection logic (why invoke this tool vs. another) is opaque natural language reasoning

### Replayability
**Assessment**: High
- Full ReAct trace records all tool invocations with arguments and results
- Given the same trace, any step can be independently verified by calling the same tool with the same input
- However, ChatGPT's text generation introduces non-determinism; the trace can be approximately but not exactly reproduced without fixing the random seed
- Tool outputs are deterministic and independently replayable

### Faithfulness Risk
**Assessment**: Moderate
- **Reduced compared to Q1**: Tool outputs ground reasoning in externally verified evidence rather than model's parametric memory
- **Risk**: ChatGPT may selectively ignore or misinterpret tool outputs that contradict its prior beliefs
- **Risk**: The textual serialization of images (captions, coordinates) loses information — ChatGPT reasons about a lossy text representation, not the full visual signal
- **Risk**: Multiple conflicting tool outputs (e.g., captioning says "A man" but celebrity recognizer identifies "John Smith") must be reconciled by ChatGPT, which can make reasoning errors

### Robustness
**Assessment**: Moderate
- **Tool Failure Sensitivity**: If a specialized tool (e.g., Azure Celebrity Recognizer) is unavailable or returns errors, ChatGPT must either skip or substitute, potentially degrading reasoning quality
- **Textual Serialization Loss**: Converting visual content to text descriptions loses fine-grained spatial and perceptual details — system performs worse on tasks requiring precise pixel-level reasoning
- **Prompt Injection via Tool Outputs**: Malicious content detected by OCR could potentially influence ChatGPT's reasoning (e.g., "IGNORE PREVIOUS INSTRUCTIONS" in image text)
- **Strength**: Modular design allows replacing individual tools with better versions without changing reasoning framework

### Cost/Latency
**Assessment**: Moderate-High
- Multiple tool calls per query: each tool invocation adds latency (network call to Azure services + processing time)
- ChatGPT calls for each reasoning step + tool dispatch decision
- No explicit upper bound on number of tool calls — complex queries may invoke 5-10 tools
- Compared to zero-shot VLMs, significantly higher cost; compared to fine-tuned models, no training cost but higher inference cost

### Security
**Assessment**: Moderate Risk
- **Prompt Injection via OCR**: OCR tool can return adversarial text embedded in images, which then enters ChatGPT's reasoning context as "trusted" tool output
- **Data Privacy**: Images are sent to Azure cloud services for tool processing — potential privacy concerns for sensitive images
- **No Explicit Injection Protection**: Paper does not describe mechanisms to sanitize tool outputs before passing to ChatGPT
- **API Dependency**: Relies on Azure cognitive services; service changes or access revocation would break the system

---

## Failure Modes

1. **Textual Serialization Information Loss**: The conversion of images to text representations (captions + coordinates) discards fine-grained visual details. Tasks requiring precise spatial reasoning (e.g., "Are these two objects touching?", "Is the shadow to the left or right of the object?") or subtle visual distinctions (e.g., expression analysis, material identification) may fail because the text serialization lacks the resolution needed for these judgments.

2. **Tool Output Misinterpretation by ChatGPT**: ChatGPT may incorrectly integrate tool outputs into its reasoning. For example, if the object detector returns "person [0.1, 0.2, 0.3, 0.4]: 0.92 confidence", ChatGPT must correctly interpret the coordinate format and confidence score. Misinterpretation of these structured outputs — especially for users with non-standard image formats — can lead to incorrect spatial reasoning.

3. **Cascading Errors from Early Wrong Tool Selection**: If ChatGPT initially selects the wrong tool for a task (e.g., calling image captioning when dense OCR is needed), the poor-quality output from the first tool call may anchor subsequent reasoning in an incorrect direction. Without a recovery mechanism that can backtrack to a different tool chain, early errors propagate.

4. **Complex Multi-Step Task Breakdown**: For tasks requiring more than 5-6 tool calls, the ReAct loop may produce incoherent reasoning as ChatGPT loses track of the overall goal across a long context. The system lacks explicit goal decomposition structures (unlike VideoAgent's unified memory), making long-horizon multi-step tasks fragile.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (qualitative demonstrations + some quantitative)
- [ ] Step Correctness (not systematically evaluated)
- [x] Evidence Attribution (tool outputs as explicit evidence references)
- [x] Trace Replayability (demonstrated via case studies)
- [ ] Robustness (not systematically evaluated)
- [ ] Cost/Latency (discussed qualitatively)
- [ ] Other

### Benchmarks
- **Qualitative demonstrations**: 12 categories of advanced visual tasks demonstrated
- **Celebrity/Text-In-Wild**: Identification tasks requiring external knowledge
- **Multi-image reasoning**: Comparative and relational reasoning across images
- No formal benchmark evaluation with aggregate quantitative metrics (primarily qualitative demonstration paper)

### Key Results
- Demonstrates zero-shot capabilities on celebrity recognition (impossible without retrieval tools)
- Shows OCR-grounded document understanding beyond single-model VLM capabilities
- Illustrates multi-image reasoning (e.g., "find differences between these two photos") via parallel tool invocations
- Comparison with "joint fine-tuning" approach shows trade-offs: MM-REACT has more flexible composition but higher latency

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [ ] RL / DPO
- [ ] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Zero-shot prompting** (no training — ChatGPT's existing capabilities used as-is with carefully designed prompts)

### Data Collection
- **No training data**: MM-REACT operates entirely zero-shot using ChatGPT (ChatGPT-turbo / GPT-4) with system prompts that describe available tools, their input/output formats, and example ReAct traces
- **Prompt engineering only**: System prompt includes: tool descriptions, serialization format for images, few-shot examples of tool invocation, and instructions for reasoning format (Thought/Action/Observation)
- **Tool configuration**: Azure cognitive services configured with API keys; no custom model training

---

## Connections to Other Work

### Builds On
- **ReAct (Yao et al., 2022)**: Directly implements the ReAct paradigm (Reason + Act) for multimodal settings. MM-REACT = ReAct + vision expert pool
- **Toolformer (Schick et al., 2023)**: Related paradigm of LLMs learning to use tools, but MM-REACT uses prompt engineering rather than tool-use fine-tuning
- **ChatGPT / GPT-4**: Leverages GPT's instruction following and reasoning capabilities without modification

### Related To
- **VideoAgent (ECCV 2024)**: Both are Quadrant II ReAct-style systems; VideoAgent uses structured memory and specialized memory querying tools; MM-REACT uses a broader pool of one-shot vision specialists
- **HuggingGPT / Jarvis (2023)**: Contemporary work on connecting LLMs to specialist AI models via planning
- **VisProg (2023)**: Uses LLM to generate visual programs; MM-REACT uses ReAct-style natural language rather than formal programs

### Influenced
- **VideoAgent (2024)**: Inspired by MM-REACT's tool use paradigm; refined the approach with structured memory for video understanding
- **AssistGUI (2024)**: GUI automation agents building on the LLM-as-controller paradigm
- Spawned significant follow-up work in LLM-based multimodal tool use (2023-2024)

---

## Quotes & Key Insights

> "MM-REACT introduces a textual prompt design that can represent text descriptions, textualized spatial coordinates, and aligned file names for dense visual signals such as images and videos."

> "MM-REACT's prompt design allows language models to accept, associate, and process multimodal information, thereby facilitating the synergetic combination of ChatGPT and various vision experts."

**Key Insight 1: Separation of Perception and Reasoning**
MM-REACT explicitly separates visual perception (delegated to specialized tools) from reasoning (handled by ChatGPT). This modularity allows each component to be updated independently and enables capabilities beyond what any single model can provide. However, the interface between perception and reasoning (textual serialization) introduces information loss.

**Key Insight 2: Zero-Shot Compositionality**
By prompting ChatGPT to select and compose vision tools, MM-REACT achieves zero-shot compositionality — solving novel visual tasks by combining existing tools in new ways without task-specific training. This is a fundamental advantage over fine-tuned VLMs but comes with the reliability risks of open-ended LLM tool selection.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant - Quadrant II: Text + Tools / ReAct-style)
- [ ] Section 5 (Learning & Alignment)
- [ ] Section 6 (Evaluation & Benchmarks)
- [x] Section 7 (Applications - multi-domain visual intelligence)
- [ ] Section 8 (Challenges & Future)

### Narrative Role
MM-REACT is a foundational Quadrant II work that established the paradigm of using LLMs as orchestrators for vision specialist pools. It demonstrates the core trade-off of Quadrant II: higher grounding strength and verifiability through external tool outputs, but at the cost of information loss from textual serialization and susceptibility to prompt injection. As the pioneer ReAct-for-multimodal paper (March 2023), it provides historical context for the subsequent evolution to more sophisticated systems like VideoAgent.

### Comparison Points
**Excels at**:
- Grounding strength via specialized tool outputs
- Zero-shot generalization to diverse visual tasks
- Modularity (easily extendable tool pool)

**Fails at**:
- Quantitative benchmarking (primarily qualitative paper)
- Handling tasks requiring fine-grained visual details beyond text serialization
- Security (prompt injection via OCR outputs)

---

## Notes

### Historical Significance
MM-REACT (March 2023) is one of the earliest papers to systematically apply ReAct-style tool use to multimodal scenarios. It predates the LLM agent explosion of late 2023 and can be considered a foundational work for Quadrant II approaches. Its influence is visible in VideoAgent, AssistGUI, CogAgent, and many subsequent tool-augmented VLM papers.

### Quadrant Placement vs. HuggingGPT
HuggingGPT (also 2023) follows a similar paradigm (LLM + specialist models). The distinction is that MM-REACT maintains a ReAct-style trace (Thought/Action/Observation), making the reasoning more explicit and checkable, while HuggingGPT uses a planning-then-execution structure.

---

## BibTeX

```bibtex
@article{yang2023mmreact,
  title={MM-REACT: Prompting ChatGPT for Multimodal Reasoning and Action},
  author={Yang, Zhengyuan and Li, Linjie and Wang, Jianfeng and Lin, Kevin and Azarnasab, Ehsan and Ahmed, Faisal and Liu, Zicheng and Liu, Ce and Zeng, Michael and Wang, Lijuan},
  journal={arXiv preprint arXiv:2303.11381},
  year={2023},
  url={https://arxiv.org/abs/2303.11381}
}
```

**Status**: ✅ Complete — Quadrant II Paper
