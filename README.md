# Verifiable Visual CoT: Survey + CFD-PRM

This repository hosts two parallel tracks:

1. **`survey/`** — Literature survey and paper draft: *From Explanations to Evidence: A Survey of Verifiable Visual Chain-of-Thought and Agentic Multimodal Reasoning (2024–Present)*. Start with [`survey/README.md`](survey/README.md).
2. **`cfd_prm/`** — Research code and experiments for **CFD-PRM** (Checkpoint-First-Divergence Process Reward Model): training, evaluation, setup scripts, and refinement / experiment logs. Start with [`cfd_prm/README.md`](cfd_prm/README.md).

## Layout

```
.
├── README.md                 # This file
├── survey/                   # Survey paper: draft, bib, paper notes, literature DB
└── cfd_prm/                  # CFD-PRM: Python package, scripts, configs, docs, refine-logs
```

## Quick pointers

| Track | Contents |
|--------|----------|
| Survey | `survey/survey_paper.md`, `survey/paper_notes/`, `survey/references.bib` |
| CFD-PRM | `cfd_prm/train.py`, `cfd_prm/scripts/`, `cfd_prm/docs/`, `cfd_prm/refine-logs/` |

Python training and setup commands assume the **repository root** as the current working directory (so `python -m cfd_prm.train` resolves the `cfd_prm` package). Use the scripts under `cfd_prm/scripts/`; they `cd` to the repo root automatically.
