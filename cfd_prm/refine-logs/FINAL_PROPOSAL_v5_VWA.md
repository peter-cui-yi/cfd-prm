# CFD-PRM Proposal v5.0 (VisualWebArena Scope)

## Checkpoint-First-Divergence Process Reward Model for Web/GUI Agents

**Target**: NeurIPS/ICLR 2026 Main Track  
**Compute**: 4xA800, ~40 GPU-hours, 40 days  
**Data**: VisualWebArena (public) + Mind2Web (OOD validation)

---

## Problem Statement

**Scoped Claim**: Web/GUI agent process reward modeling (NOT "general visual agent")

CFD-PRM detects process flaws in web navigation trajectories:
- Success/failure classification at step level
- First-divergence supervision (t* = first step where trajectory diverges from successful path)
- Sample efficiency: O(1/ε²) vs O(T/ε²) for uniform step supervision

**Why VisualWebArena**:
- Largest public multimodal web agent dataset (3,894 tasks, screenshots + trajectories)
- Natural hard negatives: failed navigation attempts are common
- Publicly available (unlike Agentic-MME)

**Framing Adjustment**:
- Method is domain-agnostic (theory applies to any step-level trajectory)
- Empirical validation: VisualWebArena (primary) + Mind2Web (OOD transfer)
- Explicit limitation: "Future work: broader visual domains beyond GUI"

---

## Contributions

| # | Contribution | Status |
|---|-------------|--------|
| 1 | Checkpoint-First-Divergence Loss (theory + implementation) | Complete |
| 2 | Hard Negative Mining from VisualWebArena | Adapter ready |
| 3 | Calibration Loss for cross-trajectory score comparability | Complete |
| 4 | Theoretical analysis (Prop 1-3) + controlled experiments | Planned |
| 5 | OOD validation (Mind2Web transfer) | Planned |

---

## Method Summary

```
Input: (screenshot, trajectory prefix) at each step
Backbone: Qwen2.5-VL-7B + LoRA (r=64, alpha=128)
Output: Step-level score r_t ∈ [0, 1]

Loss: L = L CFD (first-divergence) + 0.1 × L calibration

L CFD = -log σ(r(τ⁺) - r(τ⁻))  at t* only
L calib = -log σ(s_ref - s_dev)  softmin aggregation
```

**t* Definition (Semantic)**:
- NOT "first action token differs"
- IS "first step leading to failure state" (URL wrong, field empty, cart wrong)

---

## Evaluation Plan

### Primary: Discriminative Metrics
| Dataset | Metric | Target |
|---------|--------|--------|
| VisualWebArena test | AUROC@t* | >0.75 |
| VisualWebArena OOD (new domains) | AUROC@t* | >0.70 |
| Mind2Web (transfer) | AUROC | >0.65 |

### Secondary: Intervention
| Method | Metric | Target |
|--------|--------|--------|
| Best-of-N reranking | Success rate | +10% over random |
| Rejection sampling | Coverage vs correctness | Pareto improvement |

### Theory Validation
| Proposition | Experiment | Prediction |
|-------------|------------|------------|
| Prop 1: SNR dilution | Padding (T=10 vs T=15) | FD stable, All-Steps↓ |
| Prop 2: Feature forcing | Answer-only vs Evidence-only | Hard NE → evidence |
| Prop 3: t* robustness | δ ∈ {-3..3} perturbation | σ large → robust |

---

## Compute Budget (Updated)

| Phase | GPU-hours | Notes |
|-------|-----------|-------|
| VisualWebArena setup + hard negative mining | 2 | CLIP visual filter, NLI |
| CFD-PRM Training (5 epochs) | 32 | 4xA800, LoRA |
| Discriminative Evaluation | 4 | VisualWebArena + Mind2Web |
| Intervention Experiments | 8 | Best-of-N, rejection |
| Theory Validation (Prop 1-3) | 6 | Controlled experiments |
| OOD Transfer (Mind2Web) | 4 | Light validation |
| **Total** | **~56** | Under 115 budget |

---

## Timeline (40 Days)

| Days | Task | Deliverable |
|------|------|-------------|
| 1-3 | VisualWebArena setup | Data converted, pairs mined |
| 4-10 | CFD-PRM Training | Checkpoints saved |
| 11-15 | Discriminative Eval | AUROC tables |
| 16-22 | Intervention | Reranking results |
| 23-28 | Theory Validation | Prop 1-3 experiments |
| 29-34 | OOD Transfer | Mind2Web results |
| 35-40 | Paper Writing | Draft complete |

---

## Reviewer Risk Mitigation

| Risk | Mitigation |
|------|------------|
| "This is just GUI agent paper" | Explicit scope claim; method framed as domain-agnostic |
| "t* definition unclear (multi-path web)" | Semantic divergence (state-based), not action-based |
| "Not enough failure trajectories" | Active rollouts + temperature sampling to generate failures |
| "No generalization evidence" | Mind2Web OOD transfer experiment |
| "VWA format incompatibility" | Adapter handles screenshot + action serialization |

---

## Files Ready

**Implementation** (complete):
- `cfd_prm/models/step_scorer.py`
- `cfd_prm/losses/checkpoint_first_divergence.py`
- `cfd_prm/losses/calibration_loss.py`
- `cfd_prm/data/visualwebarena_adapter.py`
- `cfd_prm/data/hard_negative_miner.py`
- `cfd_prm/train.py`
- `cfd_prm/eval/discriminative_metrics.py`
- `cfd_prm/eval/intervention.py`

**Pending**:
- `cfd_prm/experiments/` (theory validation scripts)
- Mind2Web adapter

---

## Next Steps

1. Run `./cfd_prm/scripts/setup_visualwebarena.sh` (from repository root)
2. Verify data format + screenshot extraction
3. Launch pilot training (Exp 1.1)
4. Validate t* definition on VWA trajectories
5. Implement Mind2Web OOD evaluation

---

**Status**: READY for implementation  
**Venue Fit**: NeurIPS/ICLR (method + theory + empirical on established benchmark)  
**Scope**: Web/GUI agent PRM (honest framing, defensible claims)
