# Refinement Report

## CG-PRM: First-Divergence Iso-Answer Supervision for Multimodal PRMs

**Date**: 2026-03-30
**Final Score**: 9.1/10
**Verdict**: READY
**Rounds**: 4

---

## Summary

The CG-PRM proposal was refined through 4 iterative review cycles with GPT-5.4 xhigh. Starting from an initial score of 7.3/10, the proposal reached READY state (9.1/10) by focusing on a single-threaded mechanism contribution.

---

## Score Evolution

| Round | Overall | Key Change |
|-------|---------|------------|
| 1 | 7.3 | Initial proposal with pairwise training |
| 2 | 8.5 | First-divergence aligned supervision, rejection sampling |
| 3 | 8.8 | Schema-constrained generation, multi-detector filter |
| 4 | 9.1 | Single-threaded focus, collapsed ablations |

---

## Key Refinements

### Round 1 → Round 2 (7.3 → 8.5)

**Critical fixes addressed**:

1. **Method Specificity (6 → 8)**:
   - Changed from vague "trace-level ranking" to explicit **first-divergence aligned step supervision**
   - Defined: shared prefix fixed, supervise at t* only
   - Loss: L_fd = -log σ(r_{t*}^+ - r_{t*}^-)

2. **Feasibility (6 → 7)**:
   - Added **rejection sampling** for same-answer counterfactuals
   - Removed unconstrained pair mixing (dilutes core claim)
   - Restricted positives to externally checkable evidence

### Round 2 → Round 3 (8.5 → 8.8)

**Data-interface credibility**:

1. **Schema-constrained teacher outputs**:
   - Teacher generates structured traces with explicit grounding_ref fields
   - No post-hoc extraction ambiguity
   - t* identified directly from schema field

2. **Multi-detector hardness filter**:
   - Ensemble: lexical, syntax, step-type, text-only PRM
   - Prevents single-detector selection bias

3. **Simplifications**:
   - L_fd as only core loss (downstream moved to ablation)
   - softmin as default aggregator (min as sensitivity)
   - Uniform canonical trace format

### Round 3 → Round 4 (8.8 → 9.1)

**Single-threaded focus**:

1. **Demoted secondary claims**:
   - Multi-detector filter → sanity check (not Claim 3)
   - VLM-generated negatives → appendix robustness
   - BoN reranking → application (not method)

2. **Collapsed ablations**:
   - From 6 ablations to 3 core ones
   - Each directly tests mechanism necessity

3. **Paper positioning**:
   - One dominant contribution
   - One supporting evaluation probe
   - Clean abstract structure

---

## Final Proposal Structure

### Dominant Contribution
**First-divergence aligned iso-answer pairwise supervision with schema-constrained traces for multimodal PRMs**

### Three Core Experiments
1. First-divergence vs pointwise (alignment necessity)
2. Schema-constrained vs post-hoc (generation necessity)
3. Leave-one-out + human-authored (artifact control)

### Three Core Ablations
1. First-divergence vs pointwise
2. Schema vs post-hoc
3. Iso-answer only vs shortcut-leaking

---

## What Was Deleted

| Deleted Element | Reason |
|-----------------|--------|
| Wrong-answer negatives in core training | Reintroduces answer shortcut |
| Full-trace ranking loss | Less precise than step-level |
| BoN reranking as method claim | Application, not contribution |
| Unconstrained pair mixing | Dilutes iso-answer claim |
| L_fd + downstream in core | Moved to ablation |
| Multiple aggregator choices | softmin default, min sensitivity |
| Claim 3 (multi-detector filter) | Sanity check, not paper-level claim |
| VLM-generated negatives in method | Appendix robustness only |

---

## Remaining Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Data yield (iso-answer coverage) | MEDIUM | Report coverage rate, increase sampling |
| Verification noise | MEDIUM | Human audit for calibration |
| Teacher-style bias | LOW | Cross-generator evaluation |

---

## Next Steps

1. Implement schema-constrained teacher generation
2. Build iso-answer pair dataset with rejection sampling
3. Train first-divergence PRM
4. Run core experiments and ablations
5. Write paper

---

## Files Generated

| File | Purpose |
|------|---------|
| `FINAL_PROPOSAL.md` | Refined proposal ready for implementation |
| `round-0-initial-proposal.md` | Starting point from IDEA_REPORT |
| `round-1-review.md` | First review feedback |
| `round-1-refinement.md` | First-divergence alignment |
| `round-2-review.md` | Schema feedback |
| `round-2-refinement.md` | Schema-constrained generation |
| `round-3-review.md` | Single-thread focus feedback |
| `round-3-refinement.md` | Collapsed ablations |
| `round-4-review.md` | Final READY verdict |
| `score-history.md` | Score evolution log |
| `REFINE_STATE.json` | Pipeline checkpoint |

---

## Model Used

**Reviewer**: GPT-5.4 xhigh via Codex MCP
**ThreadId**: 019d3d7f-cc40-7332-bd1c-0812213e07fa