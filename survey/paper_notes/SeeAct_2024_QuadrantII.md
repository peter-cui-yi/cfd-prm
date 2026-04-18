# Paper Note: SeeAct

## Basic Information

**Title**: GPT-4V(ision) is a Generalist Web Agent, if Grounded

**Authors**: Boyuan Zheng, Boyu Gou, Jihyung Kil, Huan Sun, Yu Su

**Venue**: ICML 2024

**Year**: 2024

**Link**:
- arXiv: https://arxiv.org/abs/2401.01614
- Project: https://osu-nlp-group.github.io/SeeAct/
- GitHub: https://github.com/OSU-NLP-Group/SeeAct
- ICLR Workshop 2024: https://openreview.net/forum?id=piecKJ2DlB

---

## Abstract Summary

SeeAct (See-then-Act) is a two-stage generalist web agent based on GPT-4V: (1) the model visually perceives a webpage screenshot and generates a textual description of the needed action; (2) a grounding module maps that description to a concrete HTML element and action. SeeAct achieves 51.1% task success on live websites when grounding is performed manually (oracle), demonstrating strong visual understanding but revealing grounding as the bottleneck. The paper systematically evaluates three grounding strategies and finds that combining HTML structure with visual context provides the best automatic grounding, though a substantial gap to oracle remains.

---

## Methodology Analysis

### Representation Type
- [x] Textual Rationale (free-form CoT, plans, reflections)
- [ ] Structured Trace (tables, graphs, programs, state logs, latent states)

### Verification Channel
- [ ] No Tools / No Execution
- [x] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (replayable, environment feedback)

### 2×2 Matrix Placement
**Quadrant**: II (Text + Tools, ReAct-style)

**Justification**:

1. **Textual Representation**: SeeAct generates textual action descriptions in the "See" phase ("I need to click on the 'Add to Cart' button for the first product"). These descriptions are free-form natural language, not structured programs or formal specifications.

2. **Tool-Augmented Grounding**: The "Act" phase uses grounding tools — HTML parser + visual annotation (Set-of-Mark style bounding boxes + numeric labels) — to map textual descriptions to executable browser actions. These tools (HTML parser, element extractor, visual annotator) are externally called and produce verifiable outputs (element IDs, coordinates).

3. **Execution Feedback**: Browser executes actions and returns new webpage state as observation — direct feedback from the environment.

4. **Why not Q4?**: Unlike code-generation web agents (e.g., mind2web fine-tuned models), SeeAct does not synthesize executable programs. The pipeline is: screenshot → natural language description → grounding → discrete action. No Python/JavaScript generation.

5. **The Grounding Gap**: SeeAct's core scientific contribution is identifying and measuring the grounding problem: even if the textual reasoning is correct (51.1% with oracle grounding), automatic grounding only achieves ~30% (dropping ~21 points). This gap is a Q2 failure mode: textual descriptions are correct but cannot be automatically converted to executable actions.

---

## Key Contributions

1. **Systematic Grounding Evaluation**: Identifies three grounding strategies (Element Attributes, Image Annotation, Textual Choices) and comprehensively evaluates their effectiveness — finding that none approach oracle grounding, exposing a fundamental Q2 limitation.

2. **Online Evaluation Protocol**: Extends Mind2Web (offline/cached) to live websites, enabling more realistic evaluation of web agents in dynamic environments.

3. **Grounding as Bottleneck Insight**: Demonstrates empirically that visual understanding (GPT-4V "seeing" the webpage) is not the limiting factor — grounding text→element is the key challenge, establishing a research agenda for improving web agents.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Moderate (depends on grounding quality)
- "See" phase: High grounding — model explicitly describes what it sees and what action it intends, which can be audited against the screenshot
- "Act" phase: Grounding quality varies by strategy:
  - Element Attributes: Moderate (text-based matching, may be ambiguous)
  - Image Annotation: Higher (element IDs on annotated screenshot provide visual evidence)
  - Textual Choices: Highest (explicit candidate list, selection is auditable)

### Checkability
**Assessment**: Moderate-High
- Two-stage pipeline makes each stage checkable separately:
  - Stage 1: Is the generated action description reasonable given the screenshot? (human/LLM-checkable)
  - Stage 2: Did the grounding correctly map description to element? (auditable via HTML comparison)
- Full trajectory (screenshot, description, element selection, action, new screenshot) is logged

### Replayability
**Assessment**: Moderate
- Offline evaluation on Mind2Web (cached websites): High replayability
- Online evaluation on live websites: Moderate (websites change over time)
- The two-stage decomposition enables partial replayability: can re-run grounding on cached screenshots

### Faithfulness Risk
**Assessment**: Low-Moderate
- Stage 1 reasoning is explicitly tied to what's visible in the screenshot — model must describe visible elements
- Risk: Model may "see" what it expects to see (hallucinate UI elements that aren't present)
- Paper's offline evaluation can detect such hallucinations by comparing described elements to actual DOM

### Robustness
**Assessment**: Moderate
- Tested on diverse website types (search, shopping, travel, information)
- Failure modes: Dynamic content, paginated results, complex multi-frame layouts
- Grounding robustness varies by page complexity — simple, well-structured pages → high accuracy; complex, dynamic pages → low accuracy

### Cost/Latency
**Assessment**: Moderate-High
- Two GPT-4V calls per step: one for action generation, one for element selection
- Additional cost for image annotation (creating Set-of-Mark overlays)
- Each step processes full webpage screenshot
- Multi-step tasks compound cost

### Security
**Assessment**: Moderate Risk
- Prompt injection via malicious webpage content is a documented risk
- Stage 1 (action generation) is most vulnerable: malicious text on page could be interpreted as instructions
- Stage 2 (grounding to elements) provides some protection: even if Stage 1 is manipulated, grounding must still find a real DOM element

---

## Failure Modes

1. **Grounding Gap**: The most critical failure mode — even when the model correctly identifies what to do ("click the Add to Cart button"), the automatic grounding may select the wrong element or fail to ground at all. This creates a disconnect between correct visual reasoning and incorrect execution. Best automatic grounding (Element Attributes+) achieves ~30% vs 51.1% with oracle.

2. **Set-of-Mark Ineffectiveness for Web**: Image annotation with bounding boxes and numeric labels (Set-of-Mark prompting) works well for natural images but fails for dense, information-rich web pages — elements overlap, text is tiny, layout is complex. The paper shows SoM is actually less effective than text-based grounding for web agents.

3. **Cross-Page State Loss**: In multi-page tasks, the model must maintain intent across page transitions. If a page load fails or presents unexpected content, the model may lose track of the original task goal.

4. **Template-Following Brittleness**: When webpages deviate from common patterns (e.g., non-standard checkout flow), the model's training distribution expectations cause systematic errors.

5. **Action Loop**: Model may take the same action repeatedly when the page doesn't change as expected (e.g., clicking a disabled button), not recognizing the action failed.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (task success rate)
- [ ] Step Correctness
- [x] Evidence Attribution (grounding accuracy as explicit metric)
- [ ] Trace Replayability
- [x] Robustness (multiple grounding strategies compared)
- [ ] Cost/Latency
- [x] Other: Element-level grounding accuracy, step-level action accuracy

### Benchmarks
- **Mind2Web**: 177 test tasks, 3 domains (cross-task, cross-website, cross-domain splits)
- **Live Website Evaluation**: 100+ tasks on real live websites
- Custom grounding evaluation: 3 strategies × different models

### Key Results
- Oracle grounding (manual): 51.1% task success
- Best automatic grounding (Element Attributes+): ~30% task success
- Grounding gap: ~21% points between oracle and best automatic
- Text-only GPT-4 (with HTML): ~35% on Mind2Web
- GPT-4V + Image Annotation grounding: competitive with text-only in some settings

---

## Training & Alignment

### Method
- [x] Other: **Zero-shot prompting with GPT-4V** (no task-specific training)

### Data Collection
- Uses pre-trained GPT-4V — no SeeAct-specific training
- Mind2Web dataset for evaluation (not for training)
- Prompt engineering: system prompt defining web agent role, output format for action descriptions, element selection format

---

## Connections to Other Work

### Builds On
- **Mind2Web** (Deng et al., 2023): Web agent benchmark and dataset
- **GPT-4V** (OpenAI): Visual understanding backbone
- **ReAct** (Yao et al., 2022): Thought/Action paradigm
- **Set-of-Mark Prompting** (Yang et al., 2023): Visual grounding technique (which SeeAct shows doesn't work for web)

### Related To
- **WebVoyager** (He et al., ACL 2024): Concurrent Q2 web agent, takes end-to-end approach
- **VideoAgent** (ECCV 2024): Q2 anchor, same ReAct paradigm in video domain
- **CogAgent** (CVPR 2024): Fine-tuned GUI agent (contrasted as training-based approach)

### Influenced
- **SeeClick** (2024): Learns efficient grounding for web agents
- Grounding research for web/GUI agents throughout 2024-2025

---

## Quotes & Key Insights

> "GPT-4V presents a great potential for web agents — it can successfully complete 51.1% of the tasks on live websites if we manually ground its textual plans into actions."

> "Existing LMM grounding strategies like set-of-mark prompting turns out to be not effective for web agents."

**Key Insight**: SeeAct's most important finding is a **grounding-understanding asymmetry**: GPT-4V can correctly reason about what to do (high-quality textual plans) but cannot reliably translate those plans into executable actions (poor automatic grounding). This creates a unique Q2 failure mode: the textual reasoning (Thought) is verifiably correct, but the Action execution is unreliable.

**Methodological Contribution**: By isolating Stage 1 (understanding) from Stage 2 (grounding) and measuring each separately, SeeAct provides a diagnostic framework for web agents — enabling researchers to identify whether failures come from visual understanding or grounding.

---

## Survey Placement

### Section Placement
- [x] Section 4.2 (Methods by Quadrant — Quadrant II)
- [x] Section 4.2.5 (Failure Modes — grounding gap as Q2-specific failure)
- [x] Section 8 (Challenges — tool output → executable action translation as open problem)

### Narrative Role

SeeAct uniquely demonstrates the **grounding-as-tool problem** in Q2:

1. **Tool calls are not always self-grounding**: WebVoyager's browser tool returns a new screenshot (clear feedback); SeeAct's grounding tool must first find the right element (ambiguous mapping).
2. **Identifying the Q2 bottleneck**: For web agents, grounding from textual description to DOM element is as hard as the visual understanding task itself.
3. **Contrast with VideoAgent**: VideoAgent's tool calls have clear outputs (segment IDs, SQL results); SeeAct's grounding has ambiguous outputs (which of many elements?).

### Comparison Points

**Excels at**:
- Diagnostic clarity (isolating understanding from grounding)
- Principled comparison of grounding strategies
- Strong oracle performance (51.1%)

**Fails at**:
- Automatic grounding (large oracle vs. automatic gap)
- Dense web page understanding
- Set-of-Mark style visual annotation for complex layouts

---

## Notes

### Questions
- What is the exact ICML 2024 paper ID?
- Was the ICLR 2024 Workshop version substantially different from the ICML version?
- How does SeeAct's approach compare to later work (e.g., SeeClick) that addresses the grounding gap?

---

## BibTeX

```bibtex
@inproceedings{zheng2024seeact,
  title={{GPT-4V(ision) is a Generalist Web Agent, if Grounded}},
  author={Zheng, Boyuan and Gou, Boyu and Kil, Jihyung and Sun, Huan and Su, Yu},
  booktitle={Proceedings of the 41st International Conference on Machine Learning (ICML)},
  year={2024},
  url={https://arxiv.org/abs/2401.01614}
}
```

**Status**: ✅ Complete — Quadrant II Paper
