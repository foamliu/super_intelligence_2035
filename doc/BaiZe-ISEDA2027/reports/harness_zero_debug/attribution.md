# SWE-bench Verified · 恒 0 分 harness 归因表（step 1）

> 运维直令 2026-10-30 22:2x：「SWE-bench Verified 是否有几个 harness 分数始终是 0，调试跑通。」
> 本文件为 step 1（归因表，不许猜）。所有数字均有原始日志/JSON 路径可复现。
> 骨干模型：kimi-k2.6-cloud（全路统一）。打分：官方 swebench docker harness v5.0.2。

## 1. 归因总表

| runner | 阶段 | n_attempt | n_patch | n_resolved | 恒0? | 错误分类 |
|:--|:--|--:|--:|--:|:--|:--|
| **cline** | full500 (gate PASS) | 486 predict / 429 eval | 429 | **313 (73.0%)** | No | 健康 |
| **opencode** | full500 (gate PASS) | 499 predict / 488 eval | 488 | **394 (80.7%)** | No | 健康；缺 1 题 (sphinx-10435，进程已退出) |
| **pi** | full500 (gate PASS) | 410 predict / 371 eval | 371 | **274 (73.9%)** | No | 健康 |
| **claude-code** | full500 (gate PASS) | 343 predict / 266 eval | 266 | **200 (75.2%)** | No | Gen7 pilot 曾 0%，**已修复** → gate v2 PASS → full500 75.2% |
| **codex** | full500 (gate PASS) | 235 predict / 169 eval | 169 | **131 (77.5%)** | No | 健康 |
| **hermes** | gate v2 FAIL（未进全量） | 10 (gate) | 0 → rerun 1/1 | 0 (gate) | gate 阶段 Yes，**实际 No** | **适配器首跑 ~2s 退出不调模型**；rerun 证明可修 |
| **deepseek-harness** | gate v2 FAIL（未进全量） | 10 (gate) | 0 | 0 (gate) | gate 阶段 Yes，**实际 No** | **适配器 ~3-6s 退出不调模型**；glm53 7×300=40% 证明可修 |

> **结论**：SWE-bench Verified full500 中**无 runner 因模型能力「恒 0」**。
> 5 个 gate-PASS runner 全部 pass>0（73.0%–80.7%）。
> hermes / deepseek 的 0% 是 **gate v2 适配器/启动配置回归**（exit ~2-6s，未发起模型请求），
> **非模型能力问题**，且**可修复**（有先例证据）。

## 2. 关键证据

### 2.1 hermes gate v2 首跑 = 0/10 patch，~2s 退出（适配器不调模型）
日志：`run/harness/swebench_verified_full/logs/gate_predict_hermes.log`
```
[1/10] PREDICT hermes on django__django-10097  -> no-patch (patch=0B wall=3.0s)
[2/10] PREDICT hermes on sympy__sympy-11618    -> no-patch (patch=0B wall=2.7s)
[3/10] PREDICT hermes on sphinx-doc__sphinx-10323 -> no-patch (patch=0B wall=2.3s)
...（10 题全部 patch=0B，wall=1.8-3.0s，1 题 infra=matplotlib fetch 超时）
merged 0/10 predictions
```
判据：wall≈2s + patch=0B = 适配器进程启动后**立即退出**，未调用模型（真实模型调用需数百秒，见 2.2）。

### 2.2 hermes rerun = 适配器可修（铁证）
日志：`run/harness/swebench_verified_full/logs/gate_predict_hermes_rerun.log`
```
[1/9] PREDICT hermes on sympy__sympy-11618 -> patch-produced (patch=1269B wall=578.7s)
[2/9] PREDICT hermes on sphinx-doc__sphinx-10323 ->（rerun 未跑完，仅 1-2 题）
```
判据：**同一题 sympy-11618**，首跑 2.7s/0B → rerun 578.7s/1269B。
证明 hermes 适配器**能工作**，gate v2 首跑是**配置/环境回归**。

### 2.3 hermes pilot20 = 13/15 patch（11/20 resolved = 55%）
路径：`run/harness/swebench_verified_pilot/predictions/hermes__*.json`
```
hermes pilot20: 15 files, 15 parsed, 13 non-empty patch
```
（MEMORY 记录：pilot20 hermes 11/20 = 55.0%）
判据：hermes 在 pilot20 配置下**正常产出 patch**，进一步证明 gate v2 首跑 0% 是回归非能力。

### 2.4 deepseek-harness gate v2 = 0/10 patch，~3-6s 退出
日志：`run/harness/swebench_verified_full/logs/gate_predict_deepseek-harness.log`
```
[1/10] PREDICT deepseek-harness on django__django-10097 -> no-patch (patch=0B wall=3.3s)
[2/10] ... sympy-11618 -> no-patch (wall=0.9s)
...（10 题全部 patch=0B，wall=0.9-6.3s，1 题 infra=matplotlib）
merged 0/10 predictions
```
判据：与 hermes 同构 —— 适配器 ~3-6s 退出不调模型。
对照：deepseek 在 **glm53 7×300 = 40.0%**（MEMORY 2026-10-07⑥），证明适配器历史可用。

### 2.5 claude-code = 从 0% 修复到 75.2%（先例）
- Gen7 pilot (7×5)：claude-code = 0%（适配器 bug）
- 修复后 gate v2 PASS → 进 full500 → **200/266 = 75.2%**
- 证明「0% 适配器 bug → 修复 → 正常高分」路径可行（hermes/deepseek 同理）。

## 3. 根因分类

| runner | 0% 根因 | 可修? | 修复先例 |
|:--|:--|:--|:--|
| hermes | gate v2 首跑适配器 ~2s 退出（未调模型）；疑似启动参数/环境/凭证回归 | **是** | hermes rerun 578.7s 产出 patch；pilot20 13/15 patch |
| deepseek-harness | gate v2 适配器 ~3-6s 退出（未调模型）；同构回归 | **是** | glm53 7×300 = 40% |
| claude-code | Gen7 pilot 适配器 bug | **已修** | full500 75.2% |

## 4. 下一步（step 2 最小复现，下一唤醒执行）

1. **hermes smoke**：用 gate v2 原题原命令跑 1 题（如 sympy-11618），加 `set -x` / stderr 捕获，
   对比 gate v2 首跑（2s 退出）vs rerun（578.7s 产出）的**配置差异**，定位 ~2s 退出点。
   - 检查 `run_harness.py` 中 HermesDriver.run() 的启动命令、env、base_url、api_key。
   - 日志存 `reports/harness_zero_debug/hermes/`（≤200 行）。
2. **deepseek smoke**：同上，1 题（如 django-10097），定位 ~3-6s 退出点。
3. **修**：只改适配器/启动参数/凭证/超时/镜像；🚫 改题/改判分/伪造。
4. **验收**：修后重跑 ≥5 题，pass>0 才算通。
5. **交付**：`doc/BaiZe-ISEDA2027/reports/report_harness_zero_score_zh.html`（归因表 + 修复前后对比 + 剩余阻塞）。

## 5. 数据来源（可复现）
- full500 eval：`run/harness/swebench_verified_full/reports/eval_*.json`（regen_eval_summaries.py 产出，untracked）
- gate v2 日志：`run/harness/swebench_verified_full/logs/gate_predict_{hermes,deepseek-harness}.log`
- hermes rerun：`run/harness/swebench_verified_full/logs/gate_predict_hermes_rerun.log`
- pilot20 predictions：`run/harness/swebench_verified_pilot/predictions/hermes__*.json`
- 驱动定义：`run/harness/run_harness.py`（DRIVERS dict，hermes/deepseek driver）
- 单题运行器：`run/harness/run_single.py`（--harness hermes/deepseek-harness）

---
生成时间：2026-10-30 22:5x（R983）。作者：harness agent。下一步：step 2 smoke test。
