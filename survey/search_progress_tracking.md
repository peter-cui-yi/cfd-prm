# Search Progress Tracking

**Last refreshed**: 2026-04-15

This file no longer serves as an empty search template. It records the **actual state of literature collection** after multiple rounds of keyword search, venue search, snowballing, and paper-note writing.

---

## Search Outcome Snapshot

| Quadrant | Database Count | Note Coverage | Search Status |
|----------|----------------|---------------|---------------|
| Q1: Text-only CoT | 27 | 27/27 | ✅ Well covered |
| Q2: Text + Tools | 21 | 21/21 | ✅ Well covered |
| Q3: Structured w/o Tools | 20 | 20/20 | ✅ Well covered |
| Q4: Structured + Tools | 21 | 21/21 | ✅ Well covered |
| **Total** | **89** | **89/89** | ✅ Collection complete for current scope |

## Search Waves Completed

### Wave 1: Anchor seeding

Seed papers were used to establish the four quadrants:

- CURE
- VideoAgent
- MCOUT-style / structured-trace anchor
- Visual Sketchpad
- DeepEyesV2

### Wave 2: Venue and keyword expansion

The project has clearly moved beyond the initial keyword list. The current note set shows that searches were successfully expanded along at least these threads:

- visual chain-of-thought / visual CoT
- multimodal reasoning
- multimodal agents / web agents / GUI agents
- process supervision / PRM / RLVR
- structured traces, scene graphs, latent reasoning, neuro-symbolic planning
- executable visual reasoning via code, sketches, and tool calls

### Wave 3: Snowballing and follow-on passes

The current corpus indicates successful snowballing from anchor papers into:

- self-correction and critic-style VLMs
- agentic tool orchestration
- structured reasoning representations
- code-based and executable multimodal reasoning
- RL-based visual reasoning and verifier-guided training

### Wave 4: Targeted world-model pass (2026-04-15)

A focused pass was added specifically for **world-model-based visual agents**, motivated by the observation that the draft currently emphasizes LLM-based reactive agents more than predictive/model-based ones.

This pass directly integrated four papers into the note corpus:

- `MobileWorldBench` (semantic mobile world model; Q1)
- `ViMo` (visual GUI world model; Q3)
- `MobileDreamer` (sketch world model + imagination; Q3)
- `gWorld / Generative Visual Code Mobile World Models` (executable code world model; Q4)

A follow-on pass then extended the branch with three neighboring papers:

- `Code2World` (renderable-code GUI world model; Q4)
- `WebDreamer` (model-based planning for web agents; Q3)
- `Computer-Using World Model` (desktop UI world model; Q3)

It also surfaced a follow-on shortlist for possible citation expansion:

- `Code2World` (mobile GUI; renderable-code world model)
- `World Models for Web Agents` (web; early direct world-model integration)
- `WebDreamer` (web; model-based planning)
- `WebEvolver` (web; coevolving world model)
- `R-WoM` (computer-use; retrieval-augmented world model)
- `Computer-Using World Model` (desktop/computer-use; UI-state prediction + action search)

---

## What The Search Has Already Achieved

- Coverage now spans **all four quadrants** rather than only anchor examples.
- The corpus includes both **conference papers** and **arXiv preprints** from 2024-present.
- The search successfully surfaced both **method papers** and **training/alignment papers**.
- A previously underrepresented **world-model branch** is now explicitly tracked across Q1/Q3/Q4 rather than being absent from the corpus.
- The paper-note layer is now strong enough that the bottleneck has shifted from retrieval to synthesis.

---

## Remaining Search Gaps

1. **Benchmark-centric papers** for process-level evaluation are still a targeted gap.
2. **Safety-critical application papers** remain thinner than the core methods sections.
3. If the final venue requires tighter historical framing, a small number of pre-2024 precursors may still need to be cited as background only.
4. A small number of **web/computer-use world-model** papers may still be worth adding if the survey wants broader predictive-agent coverage beyond mobile GUI.

---

## Practical Interpretation

The literature search should now be treated as **mostly complete for drafting purposes**. Additional search should be **surgical**, not open-ended.

Good next search actions:

- selectively add 1-2 stronger world-model neighbors (`World Models for Web Agents`, `WebEvolver`, `R-WoM`) if Section 4/7 benefits from them
- add 3-5 benchmark/evaluation papers if Section 6 still feels under-supported
- add 2-3 application papers if Section 7 needs stronger evidence

Bad next search actions:

- restarting broad keyword search from scratch
- adding large numbers of loosely related multimodal papers
- expanding the scope beyond the verifiability lens

---

## Next Search Session Plan

**Goal**: close only the remaining evidence gaps

1. Expand citations around the new world-model subsection that has now been inserted into `survey_paper.md`.
2. If needed, add 1-2 more world-model neighbors from web/computer-use.
3. Search specifically for process-level benchmark papers.
4. Search specifically for medical/scientific/safety-critical reasoning applications.
5. Stop once those targeted gaps are closed and return to writing/citation integration.
