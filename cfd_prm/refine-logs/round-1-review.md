# Round 1 Review (GPT-5.4 xhigh)

**ThreadId**: `019d3d7f-cc40-7332-bd1c-0812213e07fa`
**Overall Score**: 7.3/10
**Verdict**: REVISE

---

## Scores by Dimension

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Fidelity | 8/10 | Iso-answer constraint directly attacks shortcut; mixing wrong-answer negatives reintroduces shortcut |
| Method Specificity | 6/10 | Step vs trace supervision unclear; pair alignment not crisp |
| Contribution Quality | 8/10 | One real mechanism-level contribution: iso-answer pairwise supervision |
| Frontier Leverage | 8/10 | Right modern primitives: frozen VLM, LoRA, synthetic counterfactuals |
| Feasibility | 6/10 | Data pipeline risk: grounded positives and same-answer negatives |
| Validation Focus | 8/10 | Mostly disciplined; core set sufficient |
| Venue Readiness | 7/10 | Potentially top-venue worthy if executed tightly |

---

## Critical Fixes

### Method Specificity (CRITICAL)

**Weakness**: The anchored failure is step-local, but proposal reads as trace-level ranking with unclear per-step supervision.

**Fix**: Make training example explicitly **first-divergence aligned**:
- For each pair, keep shared prefix fixed
- Identify first corrupted step `t*`
- Emit scalar step reward `r_t`
- Train `-log σ(r_t*^+ - r_t*^-)`
- Optionally apply same loss on all downstream steps
- Use single step scorer; define trace score at inference via `softmin` or `min` over step rewards

### Feasibility (CRITICAL)

**Weakness**: "Automatic verification → clean trace bank" is hardest part. If positives are noisy, ranking signal weakens. "Add unconstrained pairs if coverage is low" dilutes core claim.

**Fix**:
- Do NOT mix unconstrained negatives into main objective
- Use rejection sampling for same-answer negatives only
- Restrict positives to externally checkable evidence: CLEVR objects/attributes, DocVQA OCR spans/boxes
- Use human audits to calibrate acceptance thresholds, not just reporting

---

## Simplification Opportunities

1. **Delete wrong-answer negatives from core training** - keep only for auxiliary analysis
2. **Remove BoN reranking from method contribution narrative** - it's an application, not contribution
3. **Demote interventional calibration to secondary evaluation probe** - rename to `interventional grounding gap`

---

## Modernization Opportunities

- If 5 corruption families look too templated, replace part with VLM-generated free-form counterfactuals under constraints: same answer, wrong evidence, natural style

---

## Drift Warning

**NONE** - Proposal still attacks anchored problem. Risk is shortcut leakage, not drift.

---

## Raw Response

<details>
<summary>Full GPT-5.4 response</summary>

Promising direction. The proposal stays close to the anchored bottleneck, and the main idea is appropriately small. The main weakness is not ambition; it is interface clarity. Right now the paper idea is sharper than the training specification.

**Scores**
- `Problem Fidelity`: `8/10`
  The iso-answer constraint directly attacks the stated shortcut. The main fidelity leak is that mixing wrong-answer negatives back into the main loss partly reintroduces answer-correctness as a shortcut.
- `Method Specificity`: `6/10`
  The proposal is still under-specified at the exact training interface: step vs trace supervision, positive-trace verification, pair alignment, and score aggregation are not crisp enough yet.
- `Contribution Quality`: `8/10`
  There is one real mechanism-level contribution: iso-answer pairwise supervision for multimodal PRMs. That is a clean paper if you keep the metric and reranking clearly secondary.
- `Frontier Leverage`: `8/10`
  This uses the right modern primitives: frozen VLM backbone, LoRA, synthetic counterfactuals, pairwise ranking. No obvious old-school module stacking.
- `Feasibility`: `6/10`
  Model training is feasible. The risk is the data pipeline: obtaining genuinely grounded positives and enough same-answer negatives without collapsing into artifacts or low coverage.
- `Validation Focus`: `8/10`
  Mostly disciplined. The core set is sufficient: pairwise vs pointwise, leave-one-family-out, and a small human-authored challenge set.
- `Venue Readiness`: `7/10`
  Potentially top-venue worthy if executed tightly, but reviewers will immediately ask whether this is "just pairwise loss on synthetic negatives" unless the supervision interface is much sharper.

**OVERALL SCORE**: `7.3/10`

**Low-Score Fixes**
- `Method Specificity`
  Specific weakness: the anchored failure is step-local, but the proposal currently reads as trace-level ranking with unclear per-step supervision.
  Concrete fix: make the training example explicitly first-divergence aligned. For each pair, keep the shared prefix fixed, identify the first corrupted step `t*`, emit a scalar step reward `r_t`, and train `-log σ(r_t*^+ - r_t*^-)`, optionally plus the same loss on all downstream steps. Use a single step scorer and define trace score only at inference via `softmin` or `min` over step rewards.
  Priority: `CRITICAL`
- `Feasibility`
  Specific weakness: "automatic verification → clean trace bank" is the hardest part, and if positives are noisy the whole ranking signal weakens. Also, "add unconstrained pairs if coverage is low" dilutes the core claim.
  Concrete fix: do not mix unconstrained negatives into the main objective. Use rejection sampling to generate same-answer negatives only. Restrict positives to traces with externally checkable evidence references: CLEVR objects/attributes, DocVQA OCR spans or boxes. Use the 100-200 human audits to calibrate acceptance thresholds for positives and negatives, not just as a reporting set.
  Priority: `CRITICAL`

**Simplification Opportunities**
- Delete wrong-answer negatives from core training. Keep them only for auxiliary analysis or downstream robustness checks.
- Remove `best-of-N reranking` from the method contribution narrative. It is an application, not the contribution.
- Demote "interventional calibration" to a secondary evaluation probe, and rename it to something less overloaded like `interventional grounding gap`.

**Modernization Opportunities**
- If the 5 corruption families are templated enough to look synthetic, replace part of the negative generation with VLM-generated free-form counterfactual traces under explicit constraints: same final answer, wrong cited evidence, natural style.

**Drift Warning**
- `NONE`
  The proposal still attacks the anchored problem. The risk is shortcut leakage, not problem drift.

**Verdict**
- `REVISE`

The paper has a good core. To clear the top-venue bar, sharpen the step-level training interface and make the positive/negative construction story much harder to attack.

</details>