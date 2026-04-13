# CFD-PRM + On-Policy Distillation 结合探索

## 背景

### CFD-PRM 当前方法
- **数据**: Offline fixed pairs (VisualPRM400K)
- **t*: 从 human labels 预计算
- **训练**: 一次训练，无 policy 交互

### On-Policy Distillation 核心思想
- **数据分布**: 与 student policy 匹配
- **动态收集**: 训练过程中生成数据
- **迭代优化**: 根据 student 错误模式调整

---

## 结合方向分析

### Idea 1: On-Policy Pair Generation

**What**: 用 student policy 生成轨迹，动态构建 pairs

```python
# 传统 CFD-PRM (offline)
pairs = load_visualprm400k()  # 固定数据
train(pairs)

# On-Policy CFD-PRM
for iteration in range(N):
    # Student policy 生成轨迹
    trajectories = student_policy.generate(task)
    
    # Teacher 识别成功/失败
    ref = teacher.select_best(trajectories)
    dev = teacher.select_failed(trajectories)
    
    # 自动计算 t*
    t_star = find_first_divergence(ref, dev)
    
    # 构建 pairs 并训练
    pairs = build_pairs(ref, dev, t_star)
    student.update(pairs)
```

**Why**: 
- 数据分布与 student policy 匹配
- t* 基于 student 实际错误模式

**Novelty**: First on-policy PRM training with first-divergence supervision

**Feasibility**: 
- 需要 teacher model (可用 GPT-4 或大 PRM)
- Compute: ~100 GPU-hours (更多迭代)

**Risk**:
- Teacher 质量依赖大模型
- 可能收敛到 student 的局部最优

---

### Idea 2: Progressive t* Refinement

**What**: 迭代更新 t* 定义和 PRM

```python
# Phase 1: Offline CFD-PRM (当前方法)
prm_v1 = train_cfd_prm(visualprm400k)

# Phase 2: Policy-guided refinement
for iter in range(K):
    # 用当前 PRM 训练 policy
    policy = train_policy_with_prm(prm_v1)
    
    # 收集 policy 的新错误
    new_failures = collect_policy_errors(policy)
    
    # 分析 t* 分布变化
    t_star_v2 = analyze_policy_failure_patterns(new_failures)
    
    # Retrain PRM with refined t*
    prm_v2 = train_cfd_prm(new_failures, t_star_definition=t_star_v2)
```

**Why**: 
- t* 定义不是静态的，应根据 policy 进化
- 可能发现更有意义的 divergence patterns

**Novelty**: Dynamic t* definition that adapts to policy

**Feasibility**: 
- 两阶段，先 offline 再 online
- Compute: ~80 GPU-hours

**Risk**:
- t* 定义不稳定可能导致训练发散
- 需要更多理论分析

---

### Idea 3: Teacher-Student PRM Distillation

**What**: 大 teacher PRM → 小 student PRM (with CFD)

```python
# Teacher: 大模型 all-steps PRM (70B)
teacher = AllStepsPRM_70B()

# Student: 小模型 CFD-PRM (7B)
student = CFDPRM_7B()

# On-policy distillation loop
for batch in student_policy_data:
    # Teacher 对所有 steps 打分
    teacher_scores = teacher.score_all_steps(batch)
    
    # Student 只学 t*
    t_star = find_lowest_score_position(teacher_scores)  # teacher 指示 t*
    student_loss = student.train_at_t_star(batch, t_star)
```

**Why**: 
- Teacher 提供准确的 t* 定位（比 human labels 更可靠）
- Student 学习效率高（CFD 的优势）

**Novelty**: PRM distillation with first-divergence transfer

**Feasibility**: 
- 需要 70B teacher (可用现成的 VisualPRM-8B 作为 proxy)
- Compute: ~50 GPU-hours

**Risk**:
- Teacher 的 t* 定义可能与 student policy 不匹配
- 需要验证 teacher 是否真的能识别 t*

---

### Idea 4: Policy-aware t* Definition

**What**: 根据 policy 的错误模式重新定义 t*

```python
# 传统 t*: 第一个 human label=0 的步骤
t_star_human = first_label_zero(labels)

# Policy-aware t*: 导致 policy 最终失败的第一个步骤
def find_policy_t_star(policy, task):
    trajectories = policy.generate(task, N=10)
    
    # 分析哪个 step 导致失败
    for t in range(len(trajectory)):
        # Intervention experiment
        modified = intervene_at_step(trajectory, t)
        if is_failure(modified) and is_success(trajectory):
            return t  # t 是关键 divergence point
    
    return None

# 用 policy-aware t* 训练
prm = train_cfd_prm(pairs, t_star_fn=find_policy_t_star)
```

**Why**: 
- Human labels 可能不反映 policy 的真实失败模式
- 更准确的 t* 定义可能带来更好的 supervision

**Novelty**: Intervention-based t* definition (causal)

**Feasibility**: 
- Intervention experiments expensive
- Compute: ~200 GPU-hours (可能超出预算)

**Risk**:
- Intervention 定义可能与 human intuition 不一致
- 解释性变差

---

### Idea 5: RL Loop with CFD-PRM Reward

**What**: 完整 RL 循环，CFD-PRM 作为 reward

```python
# CFD-PRM 作为 reward model
prm = CFDPRM()

# RL 训练
for iteration in range(N):
    # Policy 生成轨迹
    trajectories = policy.generate()
    
    # CFD-PRM 评分
    rewards = prm.score_at_t_star(trajectories)
    
    # Policy 更新 (PPO-style)
    policy.update(trajectories, rewards)
    
    # 定期更新 PRM (on-policy)
    if iteration % K == 0:
        new_pairs = collect_recent_pairs(policy)
        prm.update(new_pairs)
```

**Why**: 
- 完整闭环：PRM 改进 policy，policy 改进 PRM
- 可能达到更高的最终性能

**Novelty**: Online PRM learning during RL

**Feasibility**: 
- Compute: ~150 GPU-hours (超出预算)
- 需要完整 RL pipeline

**Risk**:
- RL 训练不稳定
- PRM 可能 drift

---

## 推荐方案

### 最可行: Idea 3 (Teacher-Student Distillation)

| 维度 | 评估 |
|------|------|
| **Compute** | ~50 GPU-hours (可接受) |
| **Novelty** | High (PRM distillation + CFD) |
| **Feasibility** | Teacher 可用现成 VisualPRM |
| **Risk** | Medium (teacher-student mismatch) |

### 实现方案

```python
# Stage 1: Offline CFD-PRM (baseline)
prm_cfd = train_cfd_prm(visualprm400k)

# Stage 2: Distillation refinement
teacher = VisualPRM_8B()  # 现成模型

student = CFDPRM_7B()
for batch in on_policy_data:
    teacher_scores = teacher.score(batch)
    t_star_teacher = argmin(teacher_scores)
    
    # Student 只学 teacher 指示的 t*
    student.train_at_t_star(batch, t_star_teacher)

# Stage 3: Compare
auroc_cfd = evaluate(prm_cfd)
auroc_distilled = evaluate(student)
```

---

## 与当前 Proposal 的关系

| Option | 与 CFD-PRM 的关系 |
|--------|-------------------|
| **继续原计划** | 保持 offline CFD-PRM，不加 distillation |
| **Idea 3** | 作为扩展：先用 CFD-PRM，再 distillation refinement |
| **Idea 1/2/5** | 需要重新设计 pipeline，偏离原计划 |

---

## 下一步决策

1. **Option A**: 继续原 CFD-PRM proposal，不加 on-policy distillation
2. **Option B**: 添加 Idea 3 (Teacher-Student) 作为第二阶段
3. **Option C**: 完全转向 on-policy 方向

**建议**: Option B - Idea 3 作为 optional extension，不影响核心 proposal