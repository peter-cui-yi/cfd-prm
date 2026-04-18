# Visual PRM Related Work

## 1. VisualPRM: An Effective Process Reward Model for Multimodal Reasoning

- **arXiv:** [2503.10291](https://arxiv.org/abs/2503.10291) (March 2025)
- **Method:** 8B-parameter multimodal PRM trained with per-step binary classification (BCE). Each reasoning step is independently scored as correct/incorrect. Uses VisualPRM-400K dataset for training.
- **Key results:** Demonstrates that per-step supervision improves multimodal reasoning over outcome-level rewards.
- **Relation to our work:** VisualPRM's per-step BCE training is our **BCE-only baseline**. We use the same dataset (VisualPRM-400K) and architecture family (Qwen2.5-VL). Our contribution is the CFD loss that adds ranking supervision at the first divergence point.

## 2. VRPRM: Process Reward Modeling via Visual Reasoning

- **arXiv:** [2508.03556](https://arxiv.org/abs/2508.03556) (August 2025)
- **Authors:** Xinquan Chen, Bangwei Liu, Xuhong Wang, Yingchun Wang, Chaochao Lu
- **Method:** Generative PRM that produces reasoning-based reward judgments rather than scalar scores. Uses a two-stage training strategy: (1) SFT with 3.6K CoT-PRM data; (2) RL with 50K non-CoT PRM data. Introduces Self-Routing, a parameter-free routing mechanism for visual reasoning.
- **Key results:** Surpasses traditional non-thinking PRMs trained on 400K data while using <1/8 of the training data. 118% improvement over base model in Best-of-N experiments.
- **Relation to our work:** VRPRM focuses on **generative** reward judgment and data efficiency through CoT reasoning. Our work focuses on **discriminative** reward scoring with targeted supervision at t*. The two approaches are complementary.

## 3. VL-PRM: Training Vision-Language Process Reward Models for Test-Time Scaling

- **arXiv:** [2509.23250](https://arxiv.org/abs/2509.23250) (September 2025)
- **Authors:** Theog Brand et al.
- **Method:** Explores the design space of VL-PRMs for multimodal reasoning. Uses a hybrid data synthesis framework combining MCTS with strong VLM judgments. Introduces perception-focused supervision to capture visual grounding errors. Evaluates three test-time scaling strategies: greedy selection, VL-PRM-guided path selection, and others.
- **Key results:** Smaller VL-PRMs can be effective under test-time scaling. Hybrid data synthesis produces cleaner step-level labels than MCTS alone.
- **Relation to our work:** VL-PRM studies the **data construction and test-time scaling** design space. Our work studies the **loss function design** within a fixed data pipeline. Both contribute to making visual PRMs more effective.

## 4. URSA: Understanding and Verifying Chain-of-thought Reasoning in Multimodal Mathematics

- **arXiv:** [2501.04686](https://arxiv.org/abs/2501.04686) (NeurIPS 2025)
- **Authors:** Ruilin Luo, Zhuofan Zheng, Lei Wang, et al.
- **Method:** Three-stage "Unfolding multimodal pRocess-Supervision Aided" framework: (1) Vision-language alignment; (2) Math-domain SFT on MMathCoT-1M dataset; (3) PRM training (URSA-RM-8B) with dual-view process reward data and PS-GRPO for RL.
- **Key results:** SOTA among similarly sized multimodal LLMs on mathematical reasoning benchmarks.
- **Relation to our work:** URSA applies PRM to **mathematical reasoning** specifically, with a focus on the full training pipeline. Our work is **domain-agnostic** (VisualPRM-400K covers multiple domains) and focuses on the loss function level.

## 5. ViLBench: A Suite for Vision-Language Process Reward Modeling

- **arXiv:** [2503.20271](https://arxiv.org/abs/2503.20271) (EMNLP 2025)
- **Authors:** Haoqin Tu, Weitao Feng, Hardy Chen, Hui Liu, Xianfeng Tang, Cihang Xie
- **Method:** Introduces a benchmark suite for VL-PRM evaluation. Collects 73.6K vision-language process reward data using an enhanced tree-search algorithm. Trains a 3B model as a PRM.
- **Key results:** GPT-4o with CoT achieves only 27.3% accuracy on ViLBench, showing the benchmark's difficulty. Their 3B PRM achieves 3.3% improvement over standard CoT and 2.5% over untrained counterpart.
- **Relation to our work:** ViLBench provides a **benchmark** for VL-PRM evaluation. Our method (CFD-PRM) could be evaluated on ViLBench to demonstrate cross-dataset generalization.

## 6. Benchmarking Multimodal CoT Reward Model Stepwise by Visual Program

- **ICCV 2025:** [Gao et al.](https://openaccess.thecvf.com/content/ICCV2025/papers/Gao_Benchmarking_Multimodal_CoT_Reward_Model_Stepwise_by_Visual_Program_ICCV_2025_paper.pdf)
- **Method:** Uses visual programs to benchmark multimodal CoT reward models stepwise. Trains models for step-by-step reasoning to focus on critical visual regions.
- **Relation to our work:** Complementary evaluation methodology. ViLBench-like approach to stepwise assessment of multimodal reasoning quality.

## 7. TIM-PRM: Verifying Multimodal Reasoning with Tool-Integrated PRM

- **arXiv:** [2511.22998](https://arxiv.org/abs/2511.22998) (November 2025)
- **Method:** Tool-integrated PRM for multimodal reasoning verification. Combines external tools with process supervision.
- **Relation to our work:** TIM-PRM extends PRM with **tool usage**. Our work focuses on the **supervision signal design** without tools.

## Summary Table

| Paper | Venue | Method | Scale | Key Focus |
|---|---|---|---|---|
| VisualPRM | arXiv 2025 | Per-step BCE | 8B | First VL-PRM |
| VRPRM | arXiv 2025 | Generative + CoT | - | Data efficiency |
| VL-PRM | arXiv 2025 | Hybrid MCTS + VLM | - | Design space |
| URSA | NeurIPS 2025 | 3-stage PRM + GRPO | 8B | Math reasoning |
| ViLBench | EMNLP 2025 | Benchmark suite | 3B | Evaluation |
| Gao et al. | ICCV 2025 | Visual program benchmark | - | Stepwise evaluation |
| TIM-PRM | arXiv 2025 | Tool-integrated PRM | - | Tool usage |
| **CFD-PRM (ours)** | - | CFD(t*) + BCE | 3B | First-divergence supervision |
