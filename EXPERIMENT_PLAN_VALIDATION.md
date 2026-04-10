# CFD-PRM Experiment Plan (Codex-Reviewed)

## Pre-Validation Phase (Go/No-Go Gates)

### Gate 1: Data Integrity (必须通过)

```python
# 1. 下载数据
pairs = load_visualprm400k()

# 2. Prefix 完整性检查
for pair in pairs:
    ref = pair["reference"]
    dev = pair["deviated"]
    t_star = pair["t_star"]
    
    # 验证: steps[0:t*] 完全相同
    assert ref["solution"][:t_star] == dev["solution"][:t_star]
    
    # 验证: step[t*] 不同
    assert ref["solution"][t_star] != dev["solution"][t_star]

# 3. t* 分布检查
t_star_dist = histogram([p.t_star for p in pairs])
# 要求: t*=1 < 10%, t* > T-2 < 10%

# 4. Leakage Audit
train_ids = set(p["question_id"] for p in train_pairs)
test_ids = set(p["question_id"] for p in test_pairs)
assert len(train_ids & test_ids) == 0  # 无重叠
```

**Pass 条件**:
- ≥90% pairs 满足 prefix 相同 + t* 不同
- t* 分布合理 (2 ≤ median ≤ T-2)
- Train/Test leakage = 0%

---

### Gate 2: Optimization Sanity (必须通过)

```python
# 过拟合极小数据集 (1-8 pairs)
tiny_pairs = pairs[:8]
model = CFDPRM()

# 训练到 loss ~ 0
for epoch in range(100):
    loss = model.train_step(tiny_pairs)
    if loss < 0.01:
        break

# 验证梯度只来自 t*
gradients = model.get_gradient_activations()
assert gradients["t*_only"] > 0.9  # 90% 梯度在 t*
```

**Pass 条件**:
- Loss < 0.01 (过拟合成功)
- 梯度集中在 t* (> 90%)

---

### Gate 3: Trivial-Feature Check (必须通过)

```python
# 检测模型是否学习 shortcut

# Baseline 1: 只用 step index
features_index = [[t] for t in range(T)]
model_index = train_logreg(features_index, labels)

# Baseline 2: 只用 step length
features_length = [[len(step)] for step in solution]
model_length = train_logreg(features_length, labels)

# Baseline 3: 无图像
model_no_image = train_cfd_prm(data, use_image=False)

# 要求: 这些 baseline 都不应该太强
```

**Pass 条件**:
- Step-index baseline AUROC < 0.6
- No-image AUROC drop > 5% (证明依赖图像)

---

### Gate 4: Core Signal Validation (关键决策点)

```python
# 小规模多 seed 实验 (20K-50K pairs, 1-2 epochs, 3 seeds)

configs = [
    ("CFD-PRM", {"t_star": "true"}),
    ("Random-t*", {"t_star": "random", "length_matched": True}),
    ("Random-Step", {"supervise": "random_step"}),
    ("Shifted-t*", {"t_star": "true+1"}),  # t*+1
]

results = {}
for name, config in configs:
    aurocs = []
    for seed in [42, 123, 456]:
        model = train(pairs[:50000], config, seed=seed, epochs=2)
        auroc = evaluate_first_error(model, test_pairs)
        aurocs.append(auroc)
    results[name] = {"mean": mean(aurocs), "std": std(aurocs)}

# 关键比较
delta = results["CFD-PRM"]["mean"] - results["Random-t*"]["mean"]
```

**Go 条件**:
- CFD-PRM > Random-t* by **statistically significant margin** (p < 0.05)
- CFD-PRM > Random-Step
- CFD-PRM 在 All-Error 上 **不灾难性下降** (≤ 2 points)

---

### Gate 5: Label-Budget-Matched Comparison

```python
# 公平比较: 相同 label budget

# CFD-PRM: 每个 trajectory 监督 1 个 step (t*)
n_labels_cfd = len(pairs) * 1

# All-Steps-Matched: 每个 trajectory 随机选 1 个 step 监督
model_matched = train_all_steps(pairs, 
    steps_per_trajectory=1,  # 匹配 label budget
    total_labels=n_labels_cfd
)

# 比较
auroc_cfd = evaluate(model_cfd, test)
auroc_matched = evaluate(model_matched, test)
```

**Go 条件**:
- CFD-PRM > All-Steps-Matched (证明 first-divergence 优势)

---

## Full Training Phase (通过所有 Gates 后)

### Experiment 1: CFD-PRM Full Training
- Data: 50K-100K pairs
- Epochs: 5
- Seeds: 3
- GPU-hours: ~32

### Experiment 2: Label Efficiency Curves
- Label budgets: [1K, 5K, 10K, 25K, 50K, 100K]
- Match both **total labels** AND **optimizer steps**
- GPU-hours: ~12

### Experiment 3: Downstream Evaluation
```python
# Best-of-N Reranking
for task in test_tasks:
    candidates = generate_N_solutions(task, N=10)
    scores = [model.score(c) for c in candidates]
    best = candidates[argmax(scores)]
    success = evaluate_answer(best, ground_truth)
```

### Experiment 4: OOD Validation
- PRM800K (text-only math)
- GPU-hours: ~8

---

## Decision Summary

| Gate | Description | Decision |
|------|-------------|----------|
| Gate 1 | Data integrity | Fail → Fix data |
| Gate 2 | Optimization sanity | Fail → Debug code |
| Gate 3 | No trivial shortcuts | Fail → Redesign features |
| Gate 4 | Core signal (t* > random) | Fail → **Pivot method** |
| Gate 5 | Label-budget advantage | Fail → Weaken efficiency claim |

**通过所有 Gates → 进入 Full Training**
**Gate 4 失败 → 方法假设错误，考虑 Hybrid Loss 或 pivot**