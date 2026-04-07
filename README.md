# From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought

## Project Overview

This repository contains the complete draft and supporting materials for the survey paper **"From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)"**.

## Core Idea

This survey re-frames **Visual Chain-of-Thought (Visual CoT)** as an interface for **verifiable reasoning** rather than narrative explanation. We introduce a **2×2 Verifiability Matrix** that organizes recent (2024–present) multimodal reasoning work along two axes:

1. **Intermediate Representation**: Textual rationales ↔ Structured traces
2. **Verification Channel**: No tools ↔ Tool-/execution-augmented

## Repository Structure

```
pqe survey/
├── README.md                    # This file - project overview
├── survey_proposal.md           # Original proposal
├── survey_paper.md              # Complete survey paper draft
├── figures.md                   # Mermaid diagrams for figures
├── tables.md                    # Comparison tables for paper
├── references.bib               # Bibliography (BibTeX format)
├── literature_search_strategy.md # Search methodology and keywords
├── literature_database.md       # Paper tracking by quadrant
├── search_progress_tracking.md  # Search session logs
├── paper_note_template.md       # Template for analyzing papers
└── paper_notes/
    ├── README.md                # Guide to paper notes directory
    └── CURE_2024_QuadrantI_Anchor.md  # Example paper analysis
```

## Key Contributions

1. **A Verifiability-Centric Taxonomy**: 2×2 matrix separating representation from verification channel
2. **A Design Space for Verifiable Reasoning**: Recurring patterns across quadrants
3. **Process-Level Evaluation Synthesis**: Metrics beyond answer accuracy
4. **Training & Alignment Map**: SFT → process supervision → PRM/RL/DPO progression
5. **Open Problems & Recommendations**: Challenges and best practices

## The 2×2 Verifiability Matrix

| | **No Tools** | **Tool-/Execution-Augmented** |
|---|---|---|
| **Textual Rationale** | **Quadrant I**: Text-only CoT<br/>e.g., CURE | **Quadrant II**: Text + Tools<br/>e.g., VideoAgent |
| **Structured Trace** | **Quadrant III**: Structured w/o Tools<br/>e.g., MCOUT | **Quadrant IV**: Structured + Tools<br/>e.g., Visual Sketchpad, DeepEyesV2 |

## Paper Status

### Completed Sections

- ✅ Abstract
- ✅ Section 1: Introduction
- ✅ Section 2: Background
- ✅ Section 3: Taxonomy (2×2 Matrix)
- ✅ Section 4: Methods by Quadrant
- ✅ Section 5: Learning & Alignment
- ✅ Section 6: Evaluation Protocols & Benchmarks
- ✅ Section 7: Applications
- ✅ Section 8: Challenges & Future Directions
- ✅ Section 9: Best Practices
- ✅ Section 10: Conclusion
- ✅ Figures (Mermaid diagrams)
- ✅ Tables (Comparison matrices)

### Pending Work

- [ ] **Systematic literature search**: Execute search strategy to populate all quadrants
- [ ] **Paper analysis**: Fill paper notes for 20-30 papers (currently only 1 anchor paper)
- [ ] **References**: Complete BibTeX entries (currently placeholders)
- [ ] **Figure polish**: Create publication-quality versions of Mermaid diagrams
- [ ] **Formatting**: Convert to LaTeX/ACL format for submission
- [ ] **Review**: Get feedback from co-authors and domain experts

## Next Steps

### Immediate (Week 1-2)
1. Execute systematic literature search per `literature_search_strategy.md`
2. Add 15-20 papers to `literature_database.md`
3. Create paper notes for each added paper

### Short-term (Week 3-4)
1. Integrate paper analyses into Section 4
2. Complete `references.bib` with full citations
3. Create final figure files (TikZ or vector graphics)

### Medium-term (Week 5-8)
1. Convert to LaTeX format
2. Get co-author feedback
3. Iterate based on reviews
4. Prepare for submission (target: ACL 2026, NeurIPS 2026, or TPAMI)

## How to Contribute

### Adding a New Paper

1. Create new file in `paper_notes/` using naming convention: `[FirstAuthor]_[Year]_[ShortTitle].md`
2. Use template from `paper_note_template.md`
3. Fill all sections, especially 2×2 placement justification
4. Add BibTeX to `references.bib`
5. Update `literature_database.md`

### Updating the Survey

1. Make changes to `survey_paper.md`
2. Update relevant tables in `tables.md`
3. If adding figures, update `figures.md`
4. Commit with clear message: "[Section X] Added description of [paper/method]"

## Evaluation Checklist

When analyzing papers, assess these dimensions:

1. **Grounding strength**: Does reasoning point to image evidence?
2. **Checkability**: Can steps be automatically validated?
3. **Replayability**: Can trace be re-run to reproduce results?
4. **Faithfulness risk**: Can model "explain without seeing"?
5. **Robustness**: Sensitivity to errors and distribution shifts
6. **Cost/latency**: Tool budget and runtime
7. **Security**: Injection and contamination risks

## Key Deadlines

| Milestone | Target Date |
|-----------|-------------|
| Complete literature search | 2026-03-17 |
| First full draft | 2026-03-24 |
| Co-author review | 2026-03-31 |
| Camera-ready (if accepted) | TBD |

## Contact

- **Project Lead**: [Your name]
- **Institution**: [Your institution]
- **Email**: [Your email]

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

---

**Last Updated**: 2026-03-03

**Status**: Draft v0.1 - In Progress
