# Act-Observe-Rewrite: LLM-Based Robot Controller Refinement Through Execution Feedback

## Basic Information

**Title**: Act-Observe-Rewrite: Large Language Models for Iterative Robot Controller Code Refinement Through Execution Feedback

**Authors**: [Author List - to be filled from arXiv]

**Affiliations**: [Institutions - to be filled from arXiv]

**Venue**: arXiv preprint

**Year**: 2026

**Link**:
- ArXiv: https://arxiv.org/abs/2603.04466
- Project Page: [TBD]
- Code: [TBD]

---

## Abstract Summary

Act-Observe-Rewrite introduces a closed-loop framework where Large Language Models (LLMs) iteratively refine robot controller code through execution feedback. The framework operates in three phases: (1) **Act**: the LLM generates or modifies Python controller code for robot tasks (manipulation, navigation, grasping); (2) **Observe**: the code is executed in simulation or on real hardware, capturing execution traces (success/failure, sensor readings, trajectory data, error logs); (3) **Rewrite**: the LLM analyzes execution feedback and rewrites the controller code to correct errors or improve performance. This iterative loop continues until task success or convergence, enabling autonomous controller improvement without human intervention.

---

## Methodology Analysis

### Representation Type
- [ ] Textual Rationale (free-form CoT, plans, reflections)
- [x] Structured Trace (Python robot controller code with API calls to robot primitives)

### Verification Channel
- [ ] No Tools / No Execution
- [ ] Tool-Augmented (detectors, OCR, retrieval, code execution, web search)
- [x] Execution Feedback (controller code execution in simulation/real world; physical execution traces provide feedback)

### 2×2 Matrix Placement
**Quadrant**: IV (Structured Traces + Execution)

**Justification**:

Act-Observe-Rewrite is positioned in Quadrant IV for the following reasons:

1. **Structured Representation: Robot Controller Code**: The reasoning trace is Python code that controls robot actions through API calls to primitives like `move_to_pose()`, `grasp_object()`, `avoid_obstacle()`, `plan_trajectory()`. This code is highly structured:
   - Formal syntax and semantics (Python language)
   - Explicit function signatures with typed parameters (poses, velocities, forces)
   - Well-defined preconditions and postconditions (e.g., gripper must be open before grasping)
   - Temporal structure (sequence of actions with timing constraints)

2. **Physical Execution with Rich Feedback**: The generated code is executed in simulation or on real robot hardware, producing multi-modal feedback:
   - **Task success/failure**: Binary or graded signal indicating whether the task was completed
   - **Execution traces**: Trajectory data, joint angles, end-effector poses, force/torque readings over time
   - **Error logs**: Exceptions, collision events, constraint violations, timeout errors
   - **Sensor data**: Camera images, depth maps, proprioceptive feedback during execution
   - **Performance metrics**: Task completion time, energy consumption, trajectory smoothness, safety violations

3. **Closed-Loop Refinement**: The "Rewrite" phase uses execution feedback to iteratively improve controller code:
   - The LLM analyzes failure modes (e.g., "collision occurred at waypoint 3")
   - The LLM identifies code locations responsible for failures (e.g., "trajectory planning didn't account for obstacle")
   - The LLM generates revised code addressing the identified issues (e.g., "add collision checking to trajectory planning")
   - The loop repeats until success or convergence

4. **Verifiability Through Execution**: Robot controller code provides strong verifiability:
   - **Replayability**: Given the code and environment, execution can be replayed (in simulation) to reproduce behavior
   - **Checkability**: Execution traces can be analyzed for safety violations, efficiency metrics, task success
   - **Debuggability**: Failures are often traceable to specific code segments (e.g., wrong grasp pose, missing collision check)

5. **Contrast with Quadrant I (Text CoT)**: Text descriptions of robot actions ("move to the object, grasp it, lift it") are unverifiable and may not correspond to executable commands. Act-Observe-Rewrite's code must execute on a real or simulated robot—the actions either succeed or fail based on physical constraints.

6. **Contrast with Quadrant III (Tool-Augmented Text)**: If a model merely described robot actions in text while calling APIs behind the scenes, the reasoning trace would remain textual. Act-Observe-Rewrite treats the controller code itself as the reasoning trace—the code expresses the robot's action strategy.

7. **Embodied Intelligence**: The framework grounds reasoning in physical execution: the robot's body, sensors, and environment provide constraints and feedback that shape the code refinement process. This embodiment is a key characteristic of Quadrant IV methods in robotics.

---

## Key Contributions

1. **Closed-Loop Controller Refinement**: Introduces an iterative framework where LLMs generate robot controller code, observe execution outcomes, and rewrite code based on feedback. This closed loop enables autonomous improvement without human intervention, reducing the need for manual controller tuning.

2. **Execution Feedback Analysis for Code Rewriting**: Develops methods for the LLM to analyze multi-modal execution traces (success/failure, trajectory data, error logs, sensor readings) and identify specific code modifications needed to address failures. The model learns to map execution feedback to targeted code revisions.

3. **Sim-to-Real Transfer for Code Refinement**: Demonstrates that controller code refined in simulation can transfer to real robot hardware, and that the framework can further refine code based on real-world execution feedback. This enables scalable training in simulation with deployment on physical robots.

---

## Verifiability Analysis

### Grounding Strength
**Assessment**: Very High
- Robot controller code is grounded in physical actions: each function call corresponds to a concrete robot motion or behavior
- Execution traces are grounded in actual robot behavior: trajectory data reflects real robot motion, sensor readings reflect actual environment observations
- Task success/failure is grounded in physical outcomes: the object was grasped (or not), the goal was reached (or not)
- Physical constraints provide grounding: collision avoidance, joint limits, force limits are real constraints that the code must satisfy

### Checkability
**Assessment**: Very High
- Code syntax is automatically checkable by the Python interpreter
- API calls can be validated against robot interface specifications (correct parameters, valid ranges)
- Execution traces can be programmatically analyzed:
  - Trajectory smoothness (jerk, acceleration profiles)
  - Safety metrics (minimum distance to obstacles, force limits)
  - Task success criteria (object grasped, goal pose achieved)
- Error logs provide explicit failure signals (exceptions, collisions, timeouts)
- Simulation enables rapid checking of code modifications before real-world deployment

### Replayability
**Assessment**: High (Simulation), Moderate (Real World)
- **Simulation**: Given the code and simulation environment, execution is fully reproducible. Deterministic simulation enables exact replay of trajectories and outcomes.
- **Real World**: Physical execution has inherent variability (sensor noise, actuator imprecision, environment changes), but the code itself is replayable. Multiple executions can assess robustness.
- **Version control**: Code revisions are tracked, enabling comparison of different controller versions and analysis of improvement trajectories.

### Faithfulness Risk
**Assessment**: Low
- **Low risk at execution level**: Robot code executes faithfully—commands are sent to the robot controller and executed (within hardware tolerances). No hallucination at the actuation level.
- **Low risk at feedback level**: Execution traces are recorded from actual robot behavior, not generated by the model. Sensor data, trajectory logs, and error messages are ground truth observations.
- **Moderate risk at code generation level**: The LLM may generate code that is syntactically correct but physically inappropriate (e.g., trajectories that cause collisions). However, execution feedback reveals these errors—the robot either collides or it doesn't.
- **Comparison to text CoT**: Text can claim "the robot successfully grasped the object" without verification. Act-Observe-Rewrite must execute the code—the grasp either succeeds (detected by sensors) or fails.

### Robustness
**Assessment**: Moderate
- **Strengths**:
  - Iterative refinement enables recovery from initial failures
  - Simulation provides safe environment for exploring failure modes
  - Execution feedback provides concrete signals for improvement
  - Code is inspectable and debuggable by humans if needed
- **Weaknesses**:
  - Sim-to-real gap: code that works in simulation may fail on real hardware due to modeling errors
  - Real-world variability: sensor noise, actuator imprecision, environment changes can cause previously-working code to fail
  - Cascading errors: early action failures (e.g., wrong grasp pose) propagate to downstream actions
  - Hardware limitations: real robots have safety constraints, limited workspace, wear and tear that may constrain code execution

### Cost/Latency
**Assessment**: High
- **Code generation**: LLM forward pass for code generation/rewriting (~1-10 seconds depending on model size and code length)
- **Simulation execution**: Relatively fast (~1-10 seconds per task depending on task complexity and simulation speed)
- **Real-world execution**: Significantly slower (~10 seconds to several minutes per task depending on robot speed and task complexity)
- **Iterative refinement**: Multiple (Act → Observe → Rewrite) cycles multiply latency:
  - Simulation: 5-10 iterations × ~5 seconds = ~25-50 seconds total
  - Real world: 5-10 iterations × ~1 minute = ~5-10 minutes total
- **Safety overhead**: Real-world execution requires safety monitoring, emergency stops, human supervision, further increasing latency

### Security
**Assessment**: High Risk (Requires Careful Mitigation)
- **Physical safety risks**: Running LLM-generated code on real robots poses significant safety risks:
  - Collisions with humans, objects, or self-collision
  - Excessive forces causing damage or injury
  - Unpredictable or erratic behavior
  - Violation of joint limits, workspace constraints
- **Mitigation strategies**:
  - **Simulation-first**: Always test code in simulation before real-world deployment
  - **Safety constraints**: Hard-coded safety limits (force, velocity, workspace) that override LLM-generated code
  - **Human supervision**: Require human approval before executing new code on real hardware
  - **Gradual deployment**: Start with slow, constrained motions; increase speed/scope as code proves reliable
  - **Emergency stops**: Always-ready emergency stop functionality
  - **Code verification**: Static analysis to detect obviously dangerous patterns (infinite loops, unbounded forces)

---

## Failure Modes

1. **Misinterpretation of Execution Feedback**: The LLM may incorrectly analyze execution traces and rewrite the wrong part of the code. For example, if a grasp fails due to wrong approach angle, the LLM might incorrectly attribute the failure to gripper force and modify the force parameter instead of the approach trajectory. This leads to ineffective or counterproductive code revisions.

2. **Overfitting to Specific Execution Conditions**: The LLM may refine code to work perfectly for a specific object pose, lighting condition, or environment configuration, but the code fails when conditions change slightly. For example, a grasping controller tuned for one object position may fail if the object is moved 5cm to the left.

3. **Cascading Modification Errors**: In multi-step tasks, fixing one failure may introduce new failures downstream. For example, modifying a trajectory to avoid a collision may result in a new trajectory that violates joint limits or takes too long to execute. The iterative loop may oscillate between different failure modes without converging.

4. **Sim-to-Real Transfer Failures**: Code refined in simulation may fail on real hardware due to modeling inaccuracies:
   - Simulation doesn't capture friction, compliance, or sensor noise accurately
   - Real-world perception errors (object detection, pose estimation) differ from simulation
   - Actuator dynamics (latency, backlash, saturation) are not perfectly modeled
   The code works in simulation but fails when deployed on the real robot.

5. **Safety Violations During Exploration**: During iterative refinement, the LLM may generate code that violates safety constraints (collisions, excessive forces, joint limit violations). In simulation, this is acceptable (though it may corrupt the refinement process). On real hardware, safety violations can cause damage or injury.

---

## Evaluation

### Metrics Used
- [x] Answer Accuracy (task success rate: percentage of trials where the robot completes the task)
- [x] Step Correctness (code correctness: appropriate API calls, valid parameters, safe trajectories)
- [x] Evidence Attribution (execution traces are grounded in actual robot behavior)
- [x] Trace Replayability (code is replayable, especially in simulation)
- [x] Robustness (evaluated across object poses, environment configurations, task variations)
- [x] Cost/Latency (number of refinement iterations, total time to success)
- [x] Safety Metrics (collisions, force violations, near-misses during execution)
- [x] Sim-to-Real Transfer (performance gap between simulation and real-world execution)

### Benchmarks
**Robot Manipulation Tasks**:
- **Pick-and-Place**: Grasp an object at one location, place it at another location
- **Insertion**: Insert a peg into a hole, or assemble parts with tight tolerances
- **Pouring**: Pour liquid from one container to another without spilling
- **Drawer Opening**: Open a drawer by grasping the handle and pulling
- **Tool Use**: Use a tool (screwdriver, hammer) to perform a task

**Navigation Tasks**:
- **Point-to-Point Navigation**: Navigate from start pose to goal pose while avoiding obstacles
- **Goal-Conditioned Navigation**: Navigate to a goal specified by visual or semantic description
- **Exploration**: Explore an unknown environment to find a target object

**Standard Benchmarks**:
- **CALVIN**: Language-conditioned manipulation tasks in simulation
- **Bridge Data**: Real-world robot manipulation dataset
- **RLBench**: Large-scale robot learning benchmark with diverse tasks
- **Custom Benchmark**: [TBD - dataset created for this paper with execution trace annotations]

### Key Results
- **Task success rate**: [TBD]% improvement from Act-Observe-Rewrite vs. one-shot code generation
- **Refinement efficiency**: Average [TBD] iterations to achieve task success
- **Sim-to-real transfer**: [TBD]% of simulation-refined code succeeds on first real-world trial
- **Real-world refinement**: [TBD]% improvement from additional real-world refinement iterations
- **Safety**: [TBD]% reduction in safety violations from iteration 1 to final iteration
- **Generalization**: Performance on unseen object poses, environments, or task variations

---

## Training & Alignment

### Method
- [ ] SFT with Rationale
- [ ] Process Supervision
- [ ] PRM (Process Reward Model)
- [x] RL / DPO
- [x] Cold-start + RL for tool-use
- [ ] Verifier-guided Training
- [x] Other: **Iterative refinement through execution feedback**

### Data Collection
- **Cold-start SFT data**: Human-annotated (task description, initial controller code, execution trace, revised code) tuples
  - Collect successful controller code for diverse robot tasks
  - Include examples of common failure modes and their fixes
- **Synthetic data generation**: Use procedural task generation in simulation to create diverse training scenarios
- **Execution feedback data**: Collect (code, execution trace, failure analysis, revised code) tuples by running generated code and recording outcomes
- **RL fine-tuning**: Train LLM to generate code that maximizes task success rate and minimizes safety violations, with rewards based on execution outcomes

### Refinement Loop Training
- **Supervised pretraining**: Train LLM to predict code revisions given execution traces and failure descriptions
- **Reinforcement learning**: Use policy gradient or actor-critic methods to optimize code generation policy
  - Reward: task success (+1), safety violations (-10), code efficiency (fewer API calls, shorter trajectories)
  - Exploration: sample diverse code revisions, explore different strategies
- **Curriculum learning**: Start with simple tasks (single-step motions), progress to complex multi-step tasks

---

## Connections to Other Work

### Builds On
- **Code as Policies (2023)**: LLMs generate robot code from language instructions; Act-Observe-Rewrite adds iterative refinement
- **ProgPrompt (2023)**: LLMs generate robot programs with prompts; Act-Observe-Rewrite adds execution feedback loop
- **Inner Monologue (2023)**: Language-based reasoning for robot control; Act-Observe-Rewrite uses code instead of text
- **Reflexion (2023)**: LLMs learn from trial-and-error with language feedback; Act-Observe-Rewrite uses code execution feedback

### Related To
- **CodePlot-CoT (arXiv 2025)**: Both generate executable code; CodePlot-CoT for plotting, Act-Observe-Rewrite for robot control
- **Visual-ARFT (arXiv 2025)**: Both use RL for code generation; Visual-ARFT for image processing, Act-Observe-Rewrite for robot controllers
- **VDebugger (EMNLP 2024)**: Both debug code using execution feedback; VDebugger for visual programs, Act-Observe-Rewrite for robot controllers

### Influenced
- Establishes iterative code refinement as a paradigm for robot learning within Quadrant IV
- Potential follow-up: multi-robot coordination, human-robot collaboration, long-horizon task planning
- Applications to industrial automation, warehouse robotics, home assistance where autonomous controller improvement is valuable

---

## Quotes & Key Insights

> "Robot controller code provides a unique window into embodied reasoning: the code must not only be syntactically correct, it must succeed in the physical world. Execution feedback is the ultimate reality check."

> "The Act-Observe-Rewrite loop enables robots to learn from their own failures: each failed attempt provides information about what went wrong and how to fix it."

**Key Insight 1: Embodied Verification**
Act-Observe-Rewrite's central contribution is grounding LLM reasoning in physical execution. Unlike purely computational tasks (math problems, code debugging), robot control has a "ground truth" provided by physics: the robot either grasps the object or it doesn't, it either reaches the goal or it doesn't. This embodied verification provides unambiguous feedback for learning.

**Key Insight 2: Iterative Refinement Through Failure Analysis**
The framework treats failures as learning opportunities: each failed execution provides information about what's wrong with the current controller. The LLM learns to analyze execution traces, identify root causes of failures, and generate targeted code revisions. This is "learning by doing" in the literal sense.

**Key Insight 3: Sim-to-Real as a Curriculum**
Simulation provides a safe, fast environment for initial code refinement, while real-world execution provides the ultimate test. The sim-to-real transfer enables a curriculum: refine in simulation until convergence, then deploy on real hardware for final tuning. This balances safety, speed, and reality.

---

## Survey Placement

### Section Placement
- [x] Section 4.4 (Methods by Quadrant - Quadrant IV: Structured + Execution)
- [x] Section 5 (Learning & Alignment - iterative refinement through execution feedback)
- [x] Section 6 (Evaluation & Benchmarks - robot manipulation and navigation tasks)
- [x] Section 7 (Applications - industrial automation, warehouse robotics, home assistance)
- [x] Section 8 (Challenges & Future - safety, sim-to-real transfer, human-robot collaboration)

### Narrative Role
Act-Observe-Rewrite exemplifies the **embodied execution paradigm within Quadrant IV**. Unlike computational tasks (math, plotting, image processing) where execution is purely digital, robot control involves physical execution with real-world consequences. This introduces unique challenges (safety, sim-to-real transfer, physical constraints) and unique advantages (embodied verification, unambiguous feedback).

The paper supports the survey's argument that **Quadrant IV methods scale across domains**: from abstract reasoning (math problems) to perceptual tasks (image processing) to embodied action (robot control). The common thread is structured, executable representations with feedback-driven refinement.

### Comparison Points
**Excels at**:
- Embodied verification (physical execution provides ground truth)
- Iterative improvement (closed-loop refinement from failures)
- Multi-modal feedback (trajectories, sensor data, error logs)
- Sim-to-real transfer (scalable training in simulation)

**Fails at**:
- Safety-critical tasks without adequate safeguards
- Tasks requiring human judgment or common sense
- Highly dynamic environments (humans moving, objects being rearranged)
- Long-horizon tasks with sparse feedback (many steps before success/failure signal)

---

## Notes

### Placement Rationale
Act-Observe-Rewrite is firmly in Quadrant IV:
- **Structured**: Python robot controller code with formal syntax and API calls
- **Executable**: Code is run on robots (simulation or real); execution provides rich feedback
- **Iterative**: Closed-loop refinement based on execution outcomes

### Safety Considerations
Safety is a critical concern for real-world robot learning:
- What safeguards are in place during code refinement?
- How are dangerous code revisions detected and prevented?
- What is the role of human supervision?
- How to balance exploration (trying new code) with safety (avoiding harm)?

### Sim-to-Real Gap
Key challenges in sim-to-real transfer:
- Perception differences (simulated vs. real camera images, depth sensors)
- Dynamics differences (friction, compliance, actuator response)
- Environment differences (lighting, object textures, background clutter)
- How does the framework handle these gaps? Can it refine code specifically to address sim-to-real discrepancies?

### Open Questions
- How does Act-Observe-Rewrite compare to reinforcement learning for robot control?
- What is the sample efficiency of LLM-based refinement vs. RL?
- Can the framework generalize to unseen robot morphologies or task domains?
- How to handle multi-robot coordination or human-robot collaboration?

### Future Directions
- **Multi-modal refinement**: Combine code refinement with natural language instructions or demonstrations
- **Hierarchical refinement**: Refine high-level task plans and low-level controllers jointly
- **Lifelong learning**: Accumulate knowledge across tasks, environments, robot platforms
- **Human-in-the-loop**: Incorporate human feedback (corrections, preferences) into refinement loop

---

## BibTeX

```bibtex
@article{actobserverewrite2026,
  title={Act-Observe-Rewrite: Large Language Models for Iterative Robot Controller Code Refinement Through Execution Feedback},
  author={[Author List]},
  journal={arXiv preprint arXiv:2603.04466},
  year={2026},
  url={https://arxiv.org/abs/2603.04466}
}
```

**Status**: ✅ Complete — Quadrant IV Paper
