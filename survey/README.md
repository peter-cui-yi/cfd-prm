# From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought

## Project Overview

This directory (`survey/`) holds the draft and supporting materials for the survey paper **"From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)"**. The repository root `README.md` describes how this folder relates to the CFD-PRM research code under `cfd_prm/`.

## Core Idea

This survey re-frames **Visual Chain-of-Thought (Visual CoT)** as an interface for **verifiable reasoning** rather than narrative explanation. We introduce a **2×2 Verifiability Matrix** that organizes recent (2024–present) multimodal reasoning work along two axes:

1. **Intermediate Representation**: Textual rationales ↔ Structured traces
2. **Verification Channel**: No tools ↔ Tool-/execution-augmented

## Directory layout (this folder)

```
survey/
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
├── project_status.md            # Writing progress tracker
├── section_4_1_rewrite.md
├── cg_prm_proposal.md           # Earlier proposal notes (context)
└── paper_notes/
    ├── README.md                # Guide to paper notes directory
    └── CURE_2024_QuadrantI_Anchor.md  # Example paper analysis
```

## Current Snapshot

- `survey_paper.md` already contains a full structured draft spanning Abstract and Sections 1-10.
- `literature_database.md` currently tracks **89 curated papers** across the 2×2 matrix:
  - Q1: 27
  - Q2: 21
  - Q3: 20
  - Q4: 21
- `paper_notes/` currently contains **90 note files**. One file (`CURE_2024_QuadrantI_Anchor_updated.md`) is an updated duplicate of the same paper, so effective tracked-note coverage against the database is **89/89**.
- Targeted April 15 passes added a missing **world-model-based visual agent** branch: `MobileWorldBench`, `ViMo`, `MobileDreamer`, `gWorld`, `Code2World`, `WebDreamer`, and `Computer-Using World Model`.
- `references.bib` currently contains **49 BibTeX entries**, with **3 entries still carrying `TBD` author placeholders**.
- The folder itself has already been consolidated under `survey/`; the main remaining work is no longer file placement, but **synthesis, citation completion, figure polish, and submission formatting**.

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

- [ ] **Evidence integration**: Reconcile the latest paper notes with `survey_paper.md`, especially Sections 4-6
- [ ] **Final literature gaps**: Add citations around the new world-model subsection, and add benchmark/application-focused papers where the survey is still thin
- [ ] **References**: Expand `references.bib` beyond the current 49 entries and remove the remaining placeholder fields
- [ ] **Figure polish**: Create publication-quality versions of Mermaid diagrams
- [ ] **Formatting**: Convert to LaTeX/ACL format for submission
- [ ] **Review**: Get feedback from co-authors and domain experts

## Next Steps

### Immediate
1. Expand citation support for the new world-model subsection.
2. Fold the completed note set back into `survey_paper.md` so the prose matches the current database coverage.
3. Expand and clean `references.bib`, prioritizing the papers already cited in the draft.

### Short-term
1. Replace Mermaid-only figures with publication-quality vector versions.
2. Resolve duplicated or stale status statements across docs as the paper text is updated.
3. Start a LaTeX conversion pass once citations and figures stabilize.

### Submission Prep
1. Convert the markdown draft to venue-specific LaTeX.
2. Run internal review and co-author feedback.
3. Prepare a submission-ready version for ACL/NeurIPS/TPAMI-style venues.

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

## Current Milestones

| Milestone | Status |
|-----------|--------|
| Folder consolidation into `survey/` | ✅ Complete |
| Full markdown draft | ✅ Complete |
| Large-scale literature note collection | ✅ Largely complete |
| Prose-note reconciliation | 🔄 In progress |
| BibTeX completion | ⚠️ Pending |
| Figure polish + LaTeX conversion | ⚠️ Pending |

## Contact

- **Project Lead**: [Your name]
- **Institution**: [Your institution]
- **Email**: [Your email]

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

---

**Last Updated**: 2026-04-15

**Status**: Draft reorganized; literature coverage largely collected, synthesis and citation completion pending
