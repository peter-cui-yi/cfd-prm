# CFD-PRM Proposal v6.0 (VisualPRM400K)

## First-Divergence Supervision for Sample-Efficient Process Reward Models

**Target**: NeurIPS/ICLR 2026 Main Track  
**Compute**: 4xA800, ~60 GPU-hours, 40 days  
**Data**: VisualPRM400K (primary) + PRM800K (OOD validation)

---

## Problem Statement

**Core Claim**: First-divergence supervision achieves **O(1/ε²) sample complexity** vs O(T/ε²) for uniform step supervision.

CFD-PRM trains process reward models more efficiently by:
- Supervising **only at t*** (first step where trajectory diverges from correct reasoning)
- Gradient SNR focusing on information-maximal step
- Domain-agnostic method (validated on multimodal + text)

**Why VisualPRM400K**:
- 400K step-level correctness labels (image + text reasoning)
- Publicly available (HuggingFace: OpenGVLab/VisualPRM400K)
- Paired structure: all-correct vs has-error trajectories per question
- **Key advantage over VWA**: Has STEP-LEVEL labels (not just trajectory-level)

**Framing**:
- Method: Domain-agnostic PRM training algorithm
- Empirical: VisualPRM400K (multimodal) + PRM800K (text math)
- Core metric: **Label efficiency** (performance vs # labeled steps)

---

## Contributions

| # | Contribution | Status |
|---|-------------|--------|
| 1 | First-Divergence Supervision (theory: O(1/ε²) sample complexity) | Complete |
| 2 | Gradient SNR Analysis (why t* is information-maximal) | Complete |
| 3 | VisualPRM400K Adapter (paired trajectory extraction) | Complete |
| 4 | PRM800K OOD Validation (domain-agnostic claim) | Planned |
| 5 | Efficiency Curves (labeled steps vs accuracy) | Planned |

---

## Method Summary

```
Input: (image, step_text) at each reasoning step
Backbone: Qwen2.5-VL-7B + LoRA (r=64, alpha=128)
Output: Step-level score r_t ∈ [0, 1]

Loss: L = L CFD (first-divergence) + λ_calib · L calibration

L CFD = -log σ(r(τ⁺_t*) - r(τ⁻_t*))  at t* only
L calib = -log σ(softmin(τ⁺) - softmin(τ⁻))
```

**Key Difference from VisualPRM**:
| Method | Supervision | Sample Complexity |
|--------|-------------|-------------------|
| VisualPRM | All steps | O(T/ε²) |
| CFD-PRM | Only t* | O(1/ε²) |

---

## Evaluation Plan

### Primary: Efficiency Curves
| Dataset | Metric | Target |
|---------|--------|--------|
| VisualPRM400K | Accuracy vs # labeled steps | CFD-PRM 10x more efficient |
| VisualPRM400K | Accuracy vs training FLOPs | CFD-PRM 5x fewer FLOPs |
| PRM800K | Accuracy vs # labeled steps | Cross-domain consistency |

### Secondary: Final Performance
| Dataset | Metric | Target |
|---------|--------|--------|
| VisualPRM400K test | Best-of-N success | +5% over VisualPRM |
| PRM800K test | Step prediction AUROC | >0.75 |

### Theory Validation
| Proposition | Experiment | Prediction |
|-------------|------------|------------|
| Prop 1: Sample complexity | Label efficiency curve | O(1/ε²) vs O(T/ε²) |
| Prop 2: Gradient SNR | Gradient variance measurement | SNR_fd > SNR_all as T increases |
| Prop 3: t* information | Random-t* control | True t* >> Random |

---

## Compute Budget (Updated)

| Phase | GPU-hours | Notes |
|-------|-----------|-------|
| VisualPRM400K setup | 1 | HuggingFace download |
| CFD-PRM Training (5 epochs) | 32 | 4xA800, LoRA |
| PRM800K OOD Training | 8 | Domain-agnostic validation |
| Efficiency Curves (subsampled) | 12 | Multiple label budgets |
| Theory Validation | 8 | Gradient SNR, controls |
| **Total** | **~61** | Under 115 budget |

---

## Timeline (40 Days)

| Days | Task | Deliverable |
|------|------|-------------|
| 1-3 | VisualPRM400K setup | Data converted, pairs verified |
| 4-12 | CFD-PRM Training | Checkpoints + efficiency data |
| 13-18 | PRM800K OOD | Cross-domain results |
| 19-28 | Efficiency Curves | Label budget ablation |
| 29-34 | Theory Validation | Gradient SNR, controls |
| 35-40 | Paper Writing | Draft complete |

---

## Reviewer Risk Mitigation

| Risk | Mitigation |
|------|------------|
| "Just loss weighting" | Theory: sample complexity derivation + efficiency curves |
| "First-error supervision not new" | Cite Let's Verify Step by Step; emphasize O(1/ε²) result |
| "VisualPRM already did this" | Different formulation: they supervise all steps, we supervise t* only |
| "No reflection handling" | Acknowledge limitation; show recovery rate < 5% on VisualPRM400K |
| "Domain bias" | PRM800K OOD validation (text math) |

---

## Files Ready

**Implementation** (complete):
- `cfd_prm/models/step_scorer.py`
- `cfd_prm/losses/checkpoint_first_divergence.py`
- `cfd_prm/losses/calibration_loss.py`
- `cfd_prm/data/visualprm400k_adapter.py` ← New
- `cfd_prm/train.py`
- `cfd_prm/eval/discriminative_metrics.py`
- `cfd_prm/eval/intervention.py`

**Pending**:
- PRM800K adapter (similar structure, text-only)
- Efficiency curve experiments

---

## Next Steps

1. Run `./cfd_prm/scripts/setup_visualprm400k.sh` (from repository root)
2. Verify paired structure (ref vs dev per question)
3. Launch pilot training (Exp 1.1)
4. Add PRM800K for OOD validation

---

**Status**: READY for implementation  
**Venue Fit**: NeurIPS/ICLR (method + theory + cross-domain empirical)  
**Novelty**: First-divergence supervision with sample complexity guarantee
