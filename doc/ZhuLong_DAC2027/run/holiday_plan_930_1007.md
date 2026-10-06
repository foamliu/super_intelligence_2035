# 🎯 十一假期执行计划 2026-09-30 → 2026-10-07

> 本计划基于已完成探路制定。**探路成绩（1-shot）：**  
> ✅ 组件消融（pure_llm 11.4% / rag 70.3% / wo_retrieval 81.6%）  
> ✅ S2 Φ 轴（k10 75.3% / k3 69.0% / k1 60.8% / lagged 84.2%）  
> ✅ S2 lagged trace_key 已修复，r2 已出分（84.2% / 98.1%）  
> **假期 = 全部×5 轮完整版，单机串行。**


---

## 单机串行执行顺序

**总顺序**（按 README §8）：S1 保真度 → 组件消融 → S2 Φ 轴 → 模型消融

```
Phase 1: 流 A — S1 保真度消融（omega_low ×5 → readback_binary ×5 → readback_none ×5）
    ↓  loop 退出自动衔接
Phase 2: 流 C Phase1 — 组件消融（pure_llm ×5 → rag ×5 → wo_retrieval ×5 → full ×5）
    ↓  loop 内自动过渡
Phase 3: 流 C Phase2 — S2 Φ 轴（phi_k10 ×5 → phi_k3 ×5 → phi_k1 ×5 → phi_lagged(fixed) ×5）
    ↓  loop 退出自动衔接
Phase 4: 流 B — 模型消融（glm-5.2 ×5 → ds-v4-flash ×5 → kimi ×5 → doubao ×5）
```

**conductor 脚本:** `ablation_run_conductor_serial.sh` → 一键启动全流程

---

## 完工标准

论文 6 张表中所有 `[TBD]` 替换为 `mean ± std`（按 README §4.1 口径）：

| 表 | 占位 | 对应配置 | 负责流 |
|:---|:---:|:---|---:|
| `tab:omega` (6_exp.tex) | 6 | omega_low / omega_high / (H+E) | **流 A** |
| `tab:ablation-harness` (6_exp.tex) | 9 | readback_binary / readback_none / full | **流 A** |
| `tab:main-ablation` (6_exp.tex) | 7 | pure_llm / rag / wo_retrieval / wo_sandbox / wo_selfexpl / full | **流 C** |
| `tab:phi-bound` (6_exp.tex) | 14 | k=10 / k=3 / k=1 / lagged / unbounded | **流 C** |
| `tab:llm-comparison` (6_exp.tex) | 14 | glm5.2 / ds-v4-flash / kimi / doubao | **流 B** |

---

## Phase 1 — S1 保真度消融（流 A）

**task book:** `ablation_run_task_s1_full.md`  
**loop:** `ablation_run_loop_s1_full.sh`  
**MEMORY:** `MEMORY_s1_full.md`  
**基座:** `deepseek-v4-pro-fp4`（不变）

### 执行顺序
```
omega_low (L) × 5 轮  →  readback_binary (B) × 5 轮  →  readback_none (N) × 5 轮
```

### 关键变化（vs 1-shot 探路版）
| 项目 | 1-shot | 完整版 |
|:---|---:|---:|
| 每臂轮数 | 1 | **5** |
| 成绩口径 | 单次 Pass@1 | **mean ± std**（5 轮） |
| 推进逻辑 | 1 轮结束→切下一臂 | **5 轮结束**→算 mean±std→切下一臂 |

### 配套改动
S1 代码依赖（`query_knowledge.py` 的 `EDA_OMEGA_FIDELITY=low`、`run_code.py` 的 `EDA_RUNCODE_READBACK=binary|none`、`set_s1_fidelity.py`）若尚不存在，首周期 agent 自建。

---

## Phase 2+3 — 组件消融 + S2 Φ 轴（流 C）

**task book:** `ablation_run_task_component_s2_full.md`  
**loop:** `ablation_run_loop_component_s2_full.sh`  
**MEMORY:** `MEMORY_component_full.md`  
**基座:** `deepseek-v4-pro-fp4`（不变）

### Phase 2: 组件消融
```
pure_llm × 5 轮  →  rag × 5 轮  →  wo_retrieval × 5 轮  →  full × 5 轮
```

### Phase 3: S2 Φ 轴（trace_key 已修复）
```
phi_k10 × 5 轮  →  phi_k3 × 5 轮  →  phi_k1 × 5 轮  →  phi_lagged × 5 轮
```

> S2 探路已完成：k10/k3/k1 均 ✅，lagged 探路 r1 因 trace_key 缺陷作废 → r2 已修复重跑出分（84.2% / 98.1%）。  
> 流 C 的 S2 完整版在探路基础上铺开 5 轮。lagged trace_key 已在 `main.py` 完成修复（SSE session 对象身份作 dict 键），详见 `MEMORY_s2_1shot.md` ✅ 关键缺陷已修复 #2。

---

## Phase 4 — 模型消融（流 B）

**task book:** `ablation_run_task_model_full.md`  
**loop:** `ablation_run_loop_model_full.sh`  
**MEMORY:** `MEMORY_model_full.md`  
**基座:** 切 4 次

### 执行顺序
```
glm-5.2 × 5 轮  →  deepseek-v4-flash × 5 轮  →  kimi-k2.6-cloud × 5 轮  →  doubao-seed × 5 轮
```

### 注意事项
- 每次切模型前执行 `cline auth` 切换 API key/base_url/model
- `full` 配置（检索开 + sandbox 开，默认，不切 `set_ablation`）
- 主基座 `deepseek-v4-pro-fp4` 已有数据（~84.8%），不重跑

---

## 启动方式

### 一键启动（推荐）
```bash
# 登入 10.251.36.15，终端执行
cd /nasdata/app.e0031982/code/ZhuLong_DAC2027/run
setsid bash ablation_run_conductor_serial.sh > /tmp/ablation_conductor.log 2>&1 < /dev/null &
```

### 查看进度
```bash
# 看总的 conductor 日志
tail -f /tmp/ablation_conductor.log

# 看当前阶段 loop 日志
tail -f /tmp/ablation_loop_s1_full.log          # Phase 1
tail -f /tmp/ablation_loop_component_s2_full.log  # Phase 2+3
tail -f /tmp/ablation_loop_model_full.log         # Phase 4

# 看每日操作流水
cat /nasdata/app.e0031982/code/ZhuLong_DAC2027/run/daily-memories/$(date +%F).md
```

---

## 时间估算

| 阶段 | 内容 | 轮数 | 单轮 ~时间 | 总 ~时间 |
|:---|---:|---:|---:|---:|
| Phase 1 | S1 保真度 | 15 | 3h | ~45h（2 天） |
| Phase 2 | 组件消融(含 full 锚点) | 20 | 3h | ~60h（2 天） |
| Phase 3 | S2 Φ 轴 | 20 | 3h | ~60h（2.5 天） |
| Phase 4 | 模型消融 | 20 | 3h | ~60h（2.5 天） |
| **合计** | **15 配置** | **75** | 3h | **~262h（~10-11 天，含 30min 轮询粒度）** |

> 假期 9/30–10/7 = 8 天，时间刚好覆盖。若任一阶段超预期，模型消融（Phase 4）可以节后补跑。

---

## 交付物清单

假期结束时，`run/` 目录下新增：

| 文件 | 内容 |
|:---|---:|
| `MEMORY_s1_full.md` | S1 保真度 5-run 成绩（mean±std） |
| `MEMORY_component_full.md` | 组件消融 + S2 Φ 成绩（含 mean±std、Converged、Mean read-backs） |
| `MEMORY_model_full.md` | 模型消融 5-run 成绩（mean±std） |
| `daily-memories/2026-09-30.md` … `2026-10-07.md` | 每日操作流水 |

---

## 风险与应对

| 风险 | 概率 | 应对 |
|:---|---:|:---|
| 沙箱阻断（run_commands 被禁）不需要处理 | 🟢 低 | **这是预期行为** — eval cline 活跃期间反作弊 hook 拦截 run_commands，eval 结束后自动恢复。loop 的 30min 间隔就是等 eval 完成的自然机制。无需人工介入 |
| lagged trace_key 修复不彻底 | 🟢 低 | 探路已完成修复+canary 通过（MEMORY_s2_1shot.md ✅ 关键缺陷已修复 #2），r2 正在跑。满分后再审计确认 |
| 模型 API quota 超限 | 🟡 中 | 每模型 5 轮 ≈ 158×5=790 trace，确认各 API key 限额 |
| 假期中断（断电/进程被杀） | 🟡 中 | loop 醒来发现 MEMORY 还在 ⇒ 按 PHASE 续跑，不丢状态 |
| 8 天不够跑完全部 | 🟢 低 | Phase 4（模型消融）可节后用 conductor 续跑 |

---

*生成日期 2026-09-29 · 探路结果驱动 · README §8 推荐顺序 · 单机串行脚本 `ablation_run_conductor_serial.sh`*
