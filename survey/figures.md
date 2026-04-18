# Figures for Survey

## Figure 1: 2×2 Verifiability Matrix

```mermaid
flowchart TD
    subgraph Matrix["2×2 Verifiability Matrix"]
        direction TB
        
        subgraph Row1[" "]
            direction LR
            Q1["<b>Quadrant I</b><br/>Text-only CoT<br/><br/>• CURE<br/>• Self-Consistency<br/><br/>Verifiability: ★☆☆☆☆"]
            Q2["<b>Quadrant II</b><br/>Text + Tools<br/><br/>• VideoAgent<br/>• Multimodal ReAct<br/><br/>Verifiability: ★★☆☆☆"]
        end
        
        subgraph Row2[" "]
            direction LR
            Q3["<b>Quadrant III</b><br/>Structured w/o Tools<br/><br/>• MCOUT-style<br/>• Graph-based<br/><br/>Verifiability: ★★☆☆☆"]
            Q4["<b>Quadrant IV</b><br/>Structured + Tools<br/><br/>• Visual Sketchpad<br/>• DeepEyesV2<br/><br/>Verifiability: ★★★★☆"]
        end
    end
    
    subgraph AxisY["Axis A: Representation"]
        direction TB
        Textual["Textual<br/>Rationales"]
        Structured["Structured<br/>Traces"]
    end
    
    subgraph AxisX["Axis B: Verification Channel"]
        direction LR
        NoTools["No Tools"]
        Tools["Tool-/Execution-<br/>Augmented"]
    end
```

**Caption**: Figure 1: The 2×2 Verifiability Matrix organizes multimodal reasoning methods by intermediate representation (textual vs. structured) and verification channel (no tools vs. tool-augmented). Moving from Q1 → Q4 generally increases verifiability at the cost of complexity and latency.

---

## Figure 2: Verifiability Spectrum

```mermaid
flowchart LR
    subgraph Spectrum["Verifiability Spectrum"]
        direction LR
        Q1["Quadrant I<br/>Text-only"]
        Q2["Quadrant II<br/>Text + Tools"]
        Q3["Quadrant III<br/>Structured"]
        Q4["Quadrant IV<br/>Executable + Tools"]
    end
    
    Q1 -->|"Grounding ↑"| Q2
    Q2 -->|"Checkability ↑"| Q3
    Q3 -->|"External Validation ↑"| Q4
    
    subgraph Benefits["Benefits →"]
        direction LR
        B1["Human-readable"]
        B2["External evidence"]
        B3["Automatic checks"]
        B4["Full auditability"]
    end
    
    subgraph Costs["Costs →"]
        direction LR
        C1["Low latency"]
        C2["Moderate cost"]
        C3["Tool integration"]
        C4["High complexity"]
    end
```

**Caption**: Figure 2: Verifiability exists on a spectrum. Moving rightward increases verification capabilities but also increases cost, latency, and complexity. The optimal position depends on application requirements.

---

## Figure 3: Agent Loop Architecture

```mermaid
flowchart TD
    subgraph Loop["Agentic Reasoning Loop"]
        direction TB
        Observe["1. OBSERVE<br/>• Encode image/features<br/>• Retrieve from memory"]
        Plan["2. PLAN<br/>• Generate sub-goal<br/>• Select tool/operation"]
        Act["3. ACT<br/>• Call tool<br/>• Run code<br/>• Query external source"]
        Verify["4. VERIFY<br/>• Check constraints<br/>• Validate tool output<br/>• Continue or revise"]
    end
    
    Observe --> Plan
    Plan --> Act
    Act --> Verify
    Verify --> Answer{Answer<br/>ready?}
    Answer -->|No| Observe
    Answer -->|Yes| Output["OUTPUT<br/>Final answer + trace"]
    
    subgraph Memory["Memory"]
        M1["Episodic: Past observations"]
        M2["Semantic: World knowledge"]
        M3["Working: Current context"]
    end
    
    Memory -.-> Observe
    Memory -.-> Plan
    Verify -.-> Memory
```

**Caption**: Figure 3: The agentic reasoning loop interleaves perception, planning, action, and verification. Memory maintains context across iterations. The loop continues until the agent can produce a verified answer.

---

## Figure 4: Training Progression

```mermaid
flowchart LR
    subgraph Training["Training Progression for Verifiability"]
        direction LR
        SFT["SFT with<br/>Rationale<br/><br/>• Learn format<br/>• Basic CoT"]
        PS["Process<br/>Supervision<br/><br/>• Step-level feedback<br/>• Catch errors early"]
        PRM["PRM<br/><br/>• Score steps<br/>• Guide search"]
        RL["RL / DPO<br/><br/>• Optimize policy<br/>• Multi-objective"]
    end
    
    SFT --> PS
    PS --> PRM
    PRM --> RL
    
    subgraph Feedback["Feedback Source"]
        direction TB
        F1["Human annotations"]
        F2["Tool validation"]
        F3["Execution success"]
        F4["Environment rewards"]
    end
    
    subgraph Cost["Training Cost →"]
        direction LR
        C1["Low"]
        C2["Moderate"]
        C3["High"]
        C4["Very High"]
    end
```

**Caption**: Figure 4: Training methods progress from simple imitation (SFT) to process-guided optimization (RL). Each stage adds more explicit verifiability signals but increases training complexity.

---

## Figure 5: Quadrant Migration

```mermaid
flowchart TD
    subgraph Migration["Quadrant Migration Patterns"]
        direction TB
        Q1["Q1: Text-only"]
        Q2["Q2: Text + Tools"]
        Q3["Q3: Structured"]
        Q4["Q4: Structured + Tools"]
    end
    
    Q1 -->|"Add Tools"| Q2
    Q1 -->|"Add Structure"| Q3
    Q2 -->|"Structure Tool Use"| Q4
    Q3 -->|"Add Execution"| Q4
    
    subgraph Drivers["Migration Drivers"]
        D1["Failure analysis"]
        D2["Higher verifiability needs"]
        D3["Tool availability"]
        D4["Compliance requirements"]
    end
    
    subgraph Costs["Migration Costs"]
        direction LR
        MC1["Engineering effort"]
        MC2["Latency increase"]
        MC3["New failure modes"]
        MC4["Security considerations"]
    end
```

**Caption**: Figure 5: Methods can migrate between quadrants during design or deployment. Migration is driven by failure analysis, application requirements, or tool availability, but incurs engineering and operational costs.

---

## Figure 6: Evaluation Metrics Hierarchy

```mermaid
flowchart TD
    subgraph Evaluation["Process-level Evaluation Metrics"]
        direction TB
        Answer["Answer Accuracy<br/>(Traditional)"]
        
        subgraph Process["Process Metrics (Proposed)"]
            direction TB
            Step["Step Correctness<br/>• Accuracy per step<br/>• Error detection"]
            Evidence["Evidence Attribution<br/>• Grounding precision<br/>• Citation accuracy"]
            Replay["Trace Replayability<br/>• Execution success<br/>• Output consistency"]
            Robust["Robustness<br/>• Perturbation resistance<br/>• OOD generalization"]
            Cost["Cost/Latency<br/>• Wall-clock time<br/>• Tool call count"]
        end
    end
    
    Answer -.->|"Insufficient"| Process
    Step --> Evidence
    Evidence --> Replay
    Replay --> Robust
    Robust --> Cost
```

**Caption**: Figure 6: Process-level metrics complement traditional answer accuracy. These five categories (Step Correctness, Evidence Attribution, Trace Replayability, Robustness, Cost/Latency) provide a comprehensive evaluation framework.

---

## Notes for Figure Creation

### Tools for Creating Final Figures

1. **Mermaid.js**: For flowcharts and diagrams (used above)
2. **TikZ/LaTeX**: For publication-quality vector graphics
3. **Python (matplotlib/seaborn)**: For data visualizations
4. **Figma/Illustrator**: For manual design and polish

### Color Scheme Recommendations

- **Quadrant I**: Blue (calm, simple)
- **Quadrant II**: Green (growth, tools)
- **Quadrant III**: Orange (structure, intermediate)
- **Quadrant IV**: Red (power, complexity)

### Layout Guidelines

- Use consistent iconography across figures
- Ensure figures are readable in grayscale
- Include clear captions with key insights
- Reference figures in text (e.g., "As shown in Figure 1...")
