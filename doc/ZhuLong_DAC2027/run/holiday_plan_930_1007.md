# 🎯 十一假期执行计划 2026-09-30 → 2026-10-07

> 本计划基于 9/28–9/29 完成的 **S2 Φ 轴探路**及此前完成的**组件消融探路**，制定 5-run 完整版试验。  
> 3 条流可分布到 **3 台机器并行**，互不依赖。

---

## 完工标准

论文 6 张表中所有 `[TBD]` 替换为 `mean ± std`（按 README §4.1 口径）：

| 表 | 占位 | 对应配置 | 负责流 |
|:---|:---:|:---|---:|
| `tab:main-ablation` (6_exp.tex) | 7 | pure_llm / rag / wo_retrieval / wo_sandbox / wo_selfexpl / full | **流 C** |
| `tab:omega` (6_exp.tex) | 6 | omega_low / omega_high / (H+E) | **流 A** |
| `tab:ablation-harness` (6_exp.tex) | 9 | readback_binary / readback_none / full | **流 A** |
| `tab:phi-bound` (6_exp.tex) | 14 | k=10 / k=3 / k=1 / lagged / unbounded | **流 C**（S1 之后） |
| `tab:llm-comparison` (6_exp.tex) | 14 | glm5.2 / ds-v4-flash / kimi / doubao | **流 B** |

> 🔴 **流 A 与流 C 共用同一台机器的 MCP 环境（BASE_DIR），不可同时在同一台机器跑。**  
> 但流 B（换基座）可与其他流在同一台机器，因为 `run_cline_script.sh` 会切基座不冲突。  
> **推荐 3 台独立机器：** 流 A → 机器 1，流 B → 机器 2，流 C（S1 全部跑完后再开）→ 机器 1 或机器 3。

---

## 流 A — S1 保真度消融（Ω 文档轴 + readback 回读轴）

**task book:** `ablation_run_task_s1_full.md`  
**loop:** `ablation_run_loop_s1_full.sh`  
**MEMORY:** `MEMORY_s1_full.md`  
**基座:** `deepseek-v4-pro-fp4`（不变）

### 执行顺序

```
omega_low (L) × 5 轮  →  readback_binary (B) × 5 轮  →  readback_none (N) × 5 轮
```

### 逻辑改动（vs 1-shot 探路版）

| 项目 | 1-shot | 完整版 |
|:---|---:|---:|
| 每臂轮数 | 1 | **5** |
| 成绩口径 | 单次 Pass@1 | **mean ± std**（5 轮） |
| 推进逻辑 | 某臂 1 轮结束 → 切下一臂 | 某臂 **5 轮全结束** → 算 mean±std → 切下一臂 |
| 异常重试 | ERROR_COUNT < 3 重打分 | 同左，但只重试当前轮 |

### 配套改动

S1 代码依赖已于 1-shot 探路书中定义（`query_knowledge.py` 的 `EDA_OMEGA_FIDELITY=low`、`run_code.py` 的 `EDA_RUNCODE_READBACK=binary|none`、`set_s1_fidelity.py`）。若尚未实现，流 A 首周期需自行实现。

---

## 流 B — 模型消融（S3 backbone 比较）

**task book:** `ablation_run_task_model_full.md`  
**loop:** `ablation_run_loop_model_full.sh`  
**MEMORY:** `MEMORY_model_full.md`  
**基座:** 切 4 次

### 执行顺序

```
glm-5.2 × 5 轮  →  ds-v4-flash × 5 轮  →  kimi-k2.6-cloud × 5 轮  →  doubao × 5 轮
```

### 逻辑改动（vs 1-shot 探路版）

| 项目 | 1-shot | 完整版 |
|:---|---:|---:|
| 每模型轮数 | 1 | **5** |
| 成绩口径 | 单次 Pass@1 | **mean ± std**（5 轮） |
| 切模型条件 | 1 轮结束 | **5 轮全结束 + mean±std 记录** |
| 主基座 | deepseek-v4-pro-fp4 已有数据不重跑 | 同左 |

### 注意事项

- 每次切模型前执行 `cline auth` 切换 API key/base_url/model
- `full` 配置（检索开 + sandbox 开，默认，不切 `set_ablation`）
- 启动命令统一 `-p 8 -n`

---

## 流 C — 组件消融完整版 + S2 Φ 轴完整版（串行，先组件后 S2）

**Phase 1 task book:** `ablation_run_task_component_full.md`  
**Phase 2 task book:** `ablation_run_task_s2_full.md`  
**loop:** `ablation_run_loop_component_s2_full.sh`  
**MEMORY:** `MEMORY_component_full.md` → `MEMORY_s2_full.md`  
**基座:** `deepseek-v4-pro-fp4`（全流不变）

### Phase 1: 组件消融

```
pure_llm × 5 轮  →  rag × 5 轮  →  wo_retrieval × 5 轮
```

> `wo_sandbox` 与 `wo_selfexpl` 暂不做（按 README 探路阶段确认延缓）。

### Phase 2: S2 Φ 轴（含 lagged trace_key 修复）

```
k=10 × 5 轮  →  k=3 × 5 轮  →  k=1 × 5 轮  →  lagged(fixed) × 5 轮
```

> ⚠️ **lagged 修复点：** 探路发现 `run_code.py` 单槽缓冲按 `_trace_key_from_ctx()`（client_id / id(session)）隔离，同 worker 顺序处理多题致槽位残留泄漏（42/158 滞后量≠1）。修复方案：trace_key 改为 per-task，使用 `cline session_id`（已确认 158/158 唯一）作为 key。

### 逻辑改动（vs 1-shot）

| 项目 | 1-shot | 完整版 |
|:---|---:|---:|
| 每配置轮数 | 1 | **5** |
| 成绩口径 | 单次 Pass@1 | **mean ± std** |
| 组件完成后 | done_all（模型消融另行） | **自动切 S2 Φ 轴** |
| S2 完成后 | done_all | done_all |

---

## 时间估算

| 流 | 配置数 | 每配置轮数 | 总轮数 | 单轮 ~时间 | 总 ~时间 |
|:---|---:|---:|---:|---:|---:|
| A S1 保真度 | 3 | 5 | 15 | 3h | ~45h（< 2 天） |
| B 模型消融 | 4 | 5 | 20 | 3h | ~60h（< 3 天） |
| C Phase1 组件 | 3 | 5 | 15 | 3h | ~45h（< 2 天） |
| C Phase2 S2 Φ | 4 | 5 | 20 | 3h | ~60h（< 3 天） |
| **合计** | **14** | **5** | **70** | 3h | **~210h** |

> 3 条流在 3 台机器并行 → **总耗时约 3–5 天**，假期 8 天内轻松完成。

---

## 交付物清单

假期结束时，论文 `run/` 目录下新增以下文件：

| 文件 | 状态 |
|:---|:---:|
| `MEMORY_s1_full.md` | S1 完整 5-run 成绩 |
| `MEMORY_model_full.md` | 模型消融 5-run 成绩 |
| `MEMORY_component_full.md` | 组件消融 5-run 成绩（含探路数据） |
| `MEMORY_s2_full.md` | S2 Φ 完整 5-run 成绩 |
| `daily-memories/2026-09-30.md` 至 `2026-10-07.md` | 每日流水 |
| 论文 `*_*.tex` 中 [TBD] 减少 | 据成绩填入 |

---

## 风险与应对

| 风险 | 概率 | 应对 |
|:---|---:|:---|
| 沙箱 ACCESS RESTRICTED 间歇性阻断 | 🔴 高 | 循环脚本 30min 间隔自动重试；连续 6 周期阻断 → 人工介入 |
| lagged trace_key 修复不完全 | 🟡 中 | 流 C 首周期实现+自测 canary；若仍失败则如实报告 |
| 部分模型 API quota 超限 | 🟡 中 | 每模型 5 轮 ≈ 158×5=790 trace × 几~十几次调用，建议确认限额 |
| 假期中途需人工介入 | 🟢 低 | 每日检查 loop 日志 `/tmp/ablation_loop_*.log` 与 daily-memories |

---

*生成日期 2026-09-29 · 由探路结果驱动 · 按 README §8 建议执行顺序编排*
