# Literature Search Strategy

## Search Keywords

### Primary Keywords
- `visual chain-of-thought`
- `multimodal reasoning`
- `visual agent`
- `verifiable reasoning`
- `grounded reasoning`
- `multimodal chain-of-thought`
- `visual reasoning agent`

### Secondary Keywords
- `faithfulness in VLM`
- `multimodal ReAct`
- `tool-augmented multimodal`
- `executable reasoning`
- `structured reasoning trace`
- `process supervision VLM`
- `multimodal planning`

## Target Venues (2024-Present)

### Top-tier Conferences
- **NeurIPS**: 2024, 2025
- **ICLR**: 2024, 2025
- **CVPR**: 2024, 2025
- **ECCV**: 2024
- **ACL**: 2024, 2025
- **EMNLP**: 2024, 2025
- **ICML**: 2024, 2025

### Preprint Servers
- arXiv (cs.CV, cs.CL, cs.AI, cs.LG)
- Google AI Blog
- OpenAI Blog
- Anthropic Research

## Search Databases

1. **Google Scholar**: Primary search engine
2. **arXiv**: Latest preprints
3. **Semantic Scholar**: Citation tracking
4. **Papers With Code**: Implementation availability
5. **ACL Anthology**: NLP-focused papers
6. **OpenReview**: Conference submissions

## Inclusion Criteria

- Published or preprinted between January 2024 - Present
- Focus on multimodal (visual + language) reasoning
- Contains multi-step reasoning process (CoT, plans, traces)
- Addresses faithfulness/grounding/verifiability
- Proposes benchmarks or metrics for process evaluation

## Exclusion Criteria

- Single-step visual question answering
- Purely text-based reasoning
- Methods without intermediate reasoning artifacts
- Papers focused only on answer accuracy without process analysis

## Paper Tracking Fields

For each paper, record:
1. **BibTeX**: Full citation
2. **2×2 Cell**: Quadrant placement (I/II/III/IV)
3. **Representation**: Text / Structured
4. **Verification**: None / Tools / Execution
5. **Key Contributions**: 2-3 bullet points
6. **Failure Modes**: Identified limitations
7. **Evaluation Metrics**: Process-level metrics used
8. **Connections**: Links to other papers/paradigms

## Search Workflow

1. **Initial Search** (Week 1)
   - Run keyword searches across databases
   - Screen titles and abstracts
   - Create initial bibliography (~50-100 papers)

2. **Snowballing** (Week 1-2)
   - Check citations of anchor papers
   - Review related work sections
   - Identify seminal works

3. **Categorization** (Week 2-3)
   - Read full papers
   - Fill standardized notes
   - Assign to 2×2 quadrants

4. **Gap Analysis** (Week 3)
   - Identify underrepresented quadrants
   - Targeted search for missing areas
   - Ensure balanced coverage

## Anchor Papers (from Proposal)

### Quadrant I: Text-only CoT
- CURE (NAACL 2024) - CoT consistency evaluation

### Quadrant II: Text + Tools
- VideoAgent (ECCV 2024) - Multimodal agent with memory + multi-tool loop

### Quadrant III: Structured w/o Tools
- MCOUT-style (arXiv 2025) - Continuous/latent thought state reasoning

### Quadrant IV: Structured + Tools
- Visual Sketchpad (NeurIPS 2024) - Sketch as structured CoT
- DeepEyesV2 (arXiv 2025) - Code execution + web search evidence loop

## Notes

- Prioritize papers with code implementations
- Track both positive and negative results
- Note industry vs. academic work differences
- Document evaluation protocols carefully
