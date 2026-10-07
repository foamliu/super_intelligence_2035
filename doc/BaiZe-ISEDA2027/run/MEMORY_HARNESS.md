# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A 30×5 harness cross-eval (kimi-k2.6-cloud, serial=1) — cline-patched×30 ✅ 60.0% · codex×30 ✅ 46.7% · opencode×30 ✅ 50.0% · claude-code×30 ✅ 44.8% · deepseek-harness×30 🔄 RUNNING (9/30, 7 resolved = 77.8%, chain PID 1292346 → run_serial PID 3587539). gw_proxy healthy (PID 3175038, port 9090) + gw_proxy_dsh healthy (PID 1307655, port 9091).
已完成:       H-B 5×源码分析 · H-D 对比矩阵 · H-C 评测调研 · kimi serial runner · cline-patched×30 (60.0%) · codex×300 stopped (43/108/149) · opencode×30 (50.0%) · claude-code×30 (44.8%) · deepseek-harness×9/30 (7 res/2 pbf = 77.8%, RUNNING) · SWEBENCH_COMPARE.html (30×5, 129 entries, 67 resolved)
当前动作:     R153: deepseek-harness×30 progress check (9/30 done, 7 resolved/2 pbf = 77.8%) → SWEBENCH_COMPARE.html regenerated (15608B, 129 entries, 67 resolved) → commit+push
下一步:       [AUTO] deepseek-harness×21 remaining (~90min at ~4min/inst) → chain auto-regen final HTML (5 rows complete) → [next wake] verify final results → final commit+push
阻塞:         无硬阻塞. deepseek-harness toolchain working, 7/9 resolved so far.
ERROR_COUNT:  0
```

## 🆕 第一百五十三轮速览（2026-10-07 19:59）— deepseek-harness×30 progress 9/30 (7 res/2 pbf = 77.8%) + SWEBENCH_COMPARE.html regenerated (15608B, 129 entries, 67 resolved)

- 🔄 **deepseek-harness×30 progress**：chain script (PID 1292346) running, 9/30 done, **7 resolved / 2 patch-but-failed = 77.8%** (so far, on 30-set)。
  - Instances 1–9: django__django-10924(res) → 11001(res) → 11019(res) → 11039(res) → 11049(pbf) → 11099(res) → 11133(res) → 11179(pbf) → 11283(running)。
  - Current instance: django__django-11283 (inst 9, started ~40min ago, etimes ~24s for run_single)。
  - **Pace**: ~4 min/inst → 21 remaining ≈ **~84 min** to completion。
- 📈 **SWEBENCH_COMPARE.html regenerated**：15608 bytes, 30 instances, 129 entries (cline 30 + codex 30 + opencode 30 + claude-code 30 + deepseek 9), 67 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 30/30 | 13 | 16 | 1 | 44.8% |
  | deepseek-harness | 9/30 | 7 | 2 | 0 | 77.8% (so far) |
- ✅ **gw_proxy 健康**：PID 3175038 (port 9090) + gw_proxy_dsh PID 1307655 (port 9091)。
- ✅ **chain script 健康**：PID 1292346 (etimes ~27000 = ~7.5h)，正在跑 deepseek-harness×30。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~27.2KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=27.2KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动跑 deepseek-harness×21 remaining (~84min) → final regen HTML (5 rows complete) → [next wake] verify final results → final commit+push。保持 `WAITING=1`。


## 🆕 第一百五十二轮速览（2026-10-07 19:25）— ✅ claude-code×30 COMPLETE (44.8%) + deepseek-harness×30 RUNNING (1/30 resolved ✅, toolchain confirmed) + SWEBENCH_COMPARE.html (15409B, 121 entries, 61 resolved)

- ✅ **claude-code×30 COMPLETE**：30/30 done → 13 resolved, 16 patch-but-failed, 1 blocked = **44.8%** (13/29 scored)。chain script (PID 1292346) finished claude-code at 19:18:47。
  - 最后 3 个 instance 均 resolved (sympy__sympy-13471, 13480, 13647)。
- ✅ **deepseek-harness×30 STARTED + toolchain CONFIRMED**：chain script auto-started deepseek-harness×30 at 19:18:47 (PID 3587539)。
  - **Instance 1/30**: django__django-10924 → **resolved** ✅ (patch applied, FAIL_TO_PASS test_callable_path passed, PASS_TO_PASS test_path passed)。
  - **gw_proxy_dsh.py (port 9091) confirmed working** in production：SDK 通过 proxy 调用 kimi-k2.6-cloud 成功生成 patch + eval passed。
  - eval log: `eval_R1_KIMI_DEEPSEEK_HARNESS_django__django_10924.log` → resolved=true。
  - proxy log shows ConnectionResetError (normal client disconnect, not errors)。
- 📈 **SWEBENCH_COMPARE.html regenerated**：15409 bytes, 30 instances, 121 entries (cline 30 + codex 30 + opencode 30 + claude-code 30 + deepseek 1), 61 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 30/30 | 13 | 16 | 1 | 44.8% |
  | deepseek-harness | 1/30 | 1 | 0 | 0 | 100.0% (so far) |
- ✅ **gw_proxy 健康**：PID 3175038 (port 9090) + gw_proxy_dsh PID 1307655 (port 9091)。
- ✅ **chain script 健康**：PID 1292346 (etimes ~26583 = ~7.4h)，正在跑 deepseek-harness×30。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~24.6KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=24.6KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动跑 deepseek-harness×29 remaining (~2h at ~5min/inst) → final regen HTML (5 rows complete) → [next wake] verify final results → final commit+push。保持 `WAITING=1`。


## 🆕 第一百五十一轮速览（2026-10-07 18:48）— 🔧 deepseek-harness toolchain FIXED (gw_proxy_dsh.py port 9091) + claude-code×26/30 + SWEBENCH_COMPARE.html regenerated (15267B, 116 entries, 57 resolved)

- 🔧 **deepseek-harness 工具链修复（本轮核心成果）**：诊断发现 deepseek-harness SDK 通过 gw_proxy (port 9090) 调用 kimi-k2.6-cloud 时收到 **HTTP 400 INVALID_REQUEST**（`finish_reason: error`），原因 = SDK 发送 DeepSeek 特有参数（`reasoning_effort: high`、`thinking: {type: enabled}`、`dsh_plugin_packages`、`stream_options`、`max_tokens: 256000`）被 vLLM 网关拒绝。
  - **修法**：创建 `/nas_train/app.e0031982/harness_work/gw_proxy_dsh.py`（port 9091），在 `rewrite_dsh_body()` 中剥离这些参数 + 封顶 `max_tokens=8192` + 剥离 auth 头后注入真 API key。
  - **验证**：SDK 测试通过 → `finish_reason: completed`、`final_response: 'Done! I've created a file called hello.txt...'`、wall=9.2s（vs 之前 2.7s with error）。
  - **更新**：`run_harness.py:356` 改为 `base_url=http://127.0.0.1:9091/v1`。
  - **清理**：删除 2 条 broken deepseek-harness entries（HTTP 400 产生的空 patch），--resume 将跑全部 30 条。
  - gw_proxy_dsh PID 运行在 port 9091，与主 gw_proxy (port 9090) 互不干扰。
- 🔄 **claude-code×30 进展**：26/30 done → 10 resolved, 15 patch-but-failed, 1 blocked = **40.0%** (10/25 scored)。chain script (PID 1292346) 仍在跑，4 remaining。
- 📈 **SWEBENCH_COMPARE.html regenerated**：15267 bytes, 30 instances, 116 entries (cline 30 + codex 30 + opencode 30 + claude-code 26 + deepseek 0), 57 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 26/30 | 10 | 15 | 1 | 40.0% (so far) |
  | deepseek-harness | 0/30 | 0 | 0 | 0 | N/A (fixed, pending) |
- ✅ **gw_proxy 健康**：PID 3175038, port 9090 + gw_proxy_dsh PID on port 9091。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~21.8KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=21.8KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动执行 claude-code 剩 4 inst → deepseek-harness×30（fixed proxy 9091）→ final regen HTML。下次唤醒检查结果 → 最终 SWEBENCH_COMPARE.html (5 rows) → commit+push。保持 `WAITING=1`。


## 🆕 第一百五十轮速览（2026-10-07 18:03）— claude-code×30 progress (21/30, 9 res/11 pbf/1 blk = 45.0%) + SWEBENCH_COMPARE.html regenerated (15193B, 113 entries, 56 resolved) + chain script healthy + relay skip 102nd

- 🔄 **claude-code×30 进展**：21/30 done → 9 resolved, 11 patch-but-failed, 1 blocked = **45.0%** (9/20 scored) so far。PID 3273581 (ppid=1292346, etimes≈13173s≈219min)，当前处理 instance 22/30 `sympy__sympy-12481`（run_single.py 子进程 PID 1808479, etimes≈411s≈6.8min, timeout=1800s）。avg≈10min/inst, 8 remaining, ETA ~19:20。自 R149 新增 3 entries（sympy-12236 pbf, sympy-12419 pbf, sympy-12454 pbf），resolved 不变（仍 9）。
- 📈 **SWEBENCH_COMPARE.html regenerated**：gen_kimi_compare.py exit=0, 15193 bytes, 30 instances, 113 entries (cline 30 + codex 30 + opencode 30 + claude-code 21 + deepseek 2), 56 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 21/30 | 9 | 11 | 1 | 45.0% (so far) |
  | deepseek-harness | 2/30 | 0 | 2 | 0 | 0.0% |
- 🚀 **chain script 健康**：PID 1292346 (ppid=1, etimes≈21814s≈6.1h) → claude-code×30 running → 完成后 auto-start deepseek-harness×30 → final regen HTML。日志 `/tmp/chain_harnesses.log` 正常（claude-code phase, instance 22/30 in progress）。
- ✅ **gw_proxy 健康**：PID 3175038, port 9090, etimes≈202241s≈2.3d。
- ✅ **ops 中继复核（第 102 次）→ 健康**。relay `2489749 1 525098 bash ops_relay.sh`（ppid=1, etimes≈6.1d）。跳过重启。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~19.7KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=~19.7KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动执行 claude-code→deepseek-harness→regen HTML。下次唤醒检查 chain script 日志 + claude-code/deepseek-harness 进度 → 最终 SWEBENCH_COMPARE.html (5 rows) → commit+push。保持 `WAITING=1`。

## 🆕 第一百四十九轮速览（2026-10-07 17:26）— claude-code×30 progress (18/30, 8 res/9 pbf/1 blk = 47.1%) + SWEBENCH_COMPARE.html regenerated (15108B, 110 entries, 55 resolved) + chain script healthy + relay skip 101st

- 🔄 **claude-code×30 进展**：18/30 done → 8 resolved, 9 patch-but-failed, 1 blocked = **47.1%** (8/17 scored) so far。PID 3273581 (ppid=1292346, etimes≈11010s≈183min)，当前处理 instance 19/30 `sympy__sympy-12236`（run_single.py 子进程 PID 3628156, etimes≈224s≈3.7min, timeout=1800s）。avg≈9.3min/inst, 12 remaining, ETA ~19:20。自 R148 新增 3 entries（全部 pbf: sympy-11870, sympy-11897, sympy-12171），resolved 不变。
- 📈 **SWEBENCH_COMPARE.html regenerated**：gen_kimi_compare.py exit=0, 15108 bytes, 30 instances, 110 entries (cline 30 + codex 30 + opencode 30 + claude-code 18 + deepseek 2), 55 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 18/30 | 8 | 9 | 1 | 47.1% (so far) |
  | deepseek-harness | 2/30 | 0 | 2 | 0 | 0.0% |
- 🚀 **chain script 健康**：PID 1292346 (ppid=1, etimes≈19651s≈5.5h) → claude-code×30 running → 完成后 auto-start deepseek-harness×30 → final regen HTML。日志 `/tmp/chain_harnesses.log` 正常（claude-code phase since 14:22:59）。
- ✅ **gw_proxy 健康**：PID 3175038, port 9090, etimes≈200026s≈2.3d。
- ✅ **ops 中继复核（第 101 次）→ 健康**。relay `2489749 1 522883 bash ops_relay.sh`（ppid=1, etimes≈6.0d）。跳过重启。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~17.5KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=~17.5KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动执行 claude-code→deepseek-harness→regen HTML。下次唤醒检查 chain script 日志 + claude-code/deepseek-harness 进度 → 最终 SWEBENCH_COMPARE.html (5 rows) → commit+push。保持 `WAITING=1`。

## 🆕 第一百四十八轮速览（2026-10-07 16:53）— claude-code×30 progress (15/30, 8 res/6 pbf/1 blk = 57.1%) + SWEBENCH_COMPARE.html regenerated (15027B, 107 entries, 55 resolved) + chain script healthy + relay skip 100th

- 🔄 **claude-code×30 进展**：15/30 done → 8 resolved, 6 patch-but-failed, 1 blocked = **57.1%** (8/14 scored) so far。PID 3273581 (ppid=1292346, etimes≈8975s≈150min)，当前处理 instance 16/30 `sympy__sympy-11870`（run_single.py 子进程 PID 984533, etimes≈387s≈6.5min, timeout=1800s）。avg≈9.3min/inst, 15 remaining, ETA ~19:10。
- 📈 **SWEBENCH_COMPARE.html regenerated**：gen_kimi_compare.py exit=0, 15027 bytes, 30 instances, 107 entries (cline 30 + codex 30 + opencode 30 + claude-code 15 + deepseek 2), 55 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 15/30 | 8 | 6 | 1 | 57.1% (so far) |
  | deepseek-harness | 2/30 | 0 | 2 | 0 | 0.0% |
- 🚀 **chain script 健康**：PID 1292346 (ppid=1, etimes≈17616s≈4.9h) → claude-code×30 running → 完成后 auto-start deepseek-harness×30 → final regen HTML。日志 `/tmp/chain_harnesses.log` 正常。
- ✅ **gw_proxy 健康**：PID 3175038, port 9090, etimes≈198067s≈2.3d。
- ✅ **ops 中继复核（第 100 次）→ 健康**。relay `2489749 1 520924 bash ops_relay.sh`（ppid=1, etimes≈6.0d）。跳过重启。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~14.5KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=~14.5KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动执行 claude-code→deepseek-harness→regen HTML。下次唤醒检查 chain script 日志 + claude-code/deepseek-harness 进度 → 最终 SWEBENCH_COMPARE.html (5 rows) → commit+push。保持 `WAITING=1`。

## 🆕 第一百四十七轮速览（2026-10-07 16:16）— claude-code×30 progress (12/30, 7 res/4 pbf/1 blk = 63.6%) + SWEBENCH_COMPARE.html regenerated (14943B, 104 entries, 54 resolved) + data integrity verified + chain script healthy + relay skip 99th

- 🔄 **claude-code×30 进展**：12/30 done → 7 resolved, 4 patch-but-failed, 1 blocked = **63.6%** (7/11 scored) so far。PID 3273581 (ppid=1292346, etimes≈6701s≈112min)，当前处理 instance 13/30 `django__django-11620`（run_single.py 子进程 PID 1806071, etimes≈1039s≈17min, timeout=1800s）。avg≈9.3min/inst, 18 remaining, ETA ~19:00。
- 📈 **SWEBENCH_COMPARE.html regenerated**：gen_kimi_compare.py exit=0, 14943 bytes, 30 instances, 104 entries (cline 30 + codex 30 + opencode 30 + claude-code 12 + deepseek 2), 54 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 12/30 | 7 | 4 | 1 | 63.6% (so far) |
  | deepseek-harness | 2/30 | 0 | 2 | 0 | 0.0% |
- 🔍 **claude-code “blocked” 1 件**：`django__django-11001` classification=blocked（非 quota-blocked，harness 执行层面 blocked；eval.resolved 未测）。
- 🚀 **chain script 健康**：PID 1292346 (ppid=1, etimes≈15342s≈4.3h) → claude-code×30 running → 完成后 auto-start deepseek-harness×30 → final regen HTML。日志 `/tmp/chain_harnesses.log` 8 行正常。
- ✅ **gw_proxy 健康**：PID 3175038, port 9090, etimes≈195829s≈2.3d。
- ✅ **ops 中继复核（第 99 次）→ 健康**。relay `2489749 1 518704 bash ops_relay.sh`（ppid=1, etimes≈6.0d）。跳过重启。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~14KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=~14.0KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动执行 claude-code→deepseek-harness→regen HTML。下次唤醒检查 chain script 日志 + claude-code/deepseek-harness 进度 → 最终 SWEBENCH_COMPARE.html (5 rows) → commit+push。保持 `WAITING=1`。

> 📦 R131~R145（2026-10-07 05:24~15:02，codex --resume 巡检 + opencode×30 全程 + chain script 启动 + 竞态修复 + claude-code×30 启动）已滚动归档至 `daily-memories-harness/2026-10-07.md`「从 MEMORY_HARNESS.md 滚动归档」节（原文不改）。结论：codex×300 stopped at 43/108/149，opencode×30 COMPLETE 50.0%，chain script launched，claude-code×30 running 60.0%。

> 📦 R113及更早（R34~R114）均已滚动归档至 `daily-memories-harness/2026-10-04.md` ~ `2026-10-06.md`（结论不改）。

## 🔴 运维必读（2026-10-04 更新：✅✅✅ **🚀🚀 步3+步4 完整 pipeline 打通〔第三十三轮〕：`cline` harness（头less CLI + `deepseek-v4-flash`）在真实 instance `django__django-10914` 上自动产 model_patch → `r1_eval.py`（R1 unshare 沙箱）官方评分 → `resolved: true`**（patch 2576B/4 文件、墙钟 131.2s、FAIL_TO_PASS `test_override_file_upload_permissions` PASS、PASS_TO_PASS 111 全绿）。**「生成侧 + 评分侧」正式串通**，步4「顺序跑 300×5」的 cline 单桩已就绪；另 4 harness（codex/opencode/claude-code/deepseek）仍需先 build。⚠️ 同时确认：**运维已于 07:15–07:29 修复「9h 静默停摆」**——`.29` 的 cline 凭据 10-03 22:12 后被轮换/吊销（只更新了 `.12`），导致本线与 pretrain 两条 loop 每轮 `Forbidden` 但 `exit 0` → 静默空转；修复=把 `.12` key 写入 `.29` secrets.json + loop 加 `env -u OPENAI_API_KEY -u *_PROXY`。🔑 **纠正第三十二轮的「stale key」误判**：网关是**按模型授权**——env key `01_549…`→ `deepseek-v4-flash`=200（pro-fp4=403）；secrets key `02_088…`→ `deepseek-v4-pro-fp4`=200（flash=403）。故 flash 用 env key、pro-fp4 用 secrets key。 🔑 **HF 离线加载**：`HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1` + 缓存 `/nas_train/app.e0031982/hf_cache/SWE-bench___swe-bench_lite`（否则 `load_dataset` 因直连 hf=000 而挂起）。）

> 🆕 **batch-5（运维「放行」）已收到**：全量 SWE-bench-Lite 300 × 5 harness（cline/opencode/deepseek-harness/codex/claude-code）**按序跑，不要缩水**；**L0（dockerd 配代理）已取消**；**R1（`unshare` 用户命名空间沙箱 + 每实例 rootfs 落 `/nas_train`）为首选**；docker 系（L1 skopeo / L2 build）降为末选。
> ✅ **batch-5 步1 硬闸已核验通过**（本轮回贴原始输出）：`unshare --user --map-root-user --mount --pid --fork` 三件套 **OK**、user ns 内 `mount -t tmpfs` **OK**、`unprivileged_userns_clone=1`、`/nas_train` 剩 **32T** → **R1 完全可行，不碰 docker/daemon**。
> ⏭ **下一步**：步2（用 1 个 repo=django 端到端跑通 R1 沙箱）→ 步3（写适配层：`benchmark.py` 只驱动 aider，另 5 者需适配；先跑通 codex/opencode 再复制，复用官方 `run_evaluation` 口径）→ 步4（顺序跑 300×5，受 5h 滑动窗口 key 约束 → 低并发 ≤4 + 跨 harness 串行 + 每 harness 跑完即固化）。
> ⚠️ **重 I/O 避让训练**：.29 是 pretrain R2 训练机，实跑 300×5 只在低负载窗口；步3 适配层（纯 CPU）可先行。

> 🆕 **已交付 batch-4**：`harness/SWEBENCH_LITE_FEASIBILITY.md`（只读评估 §1–8）+ `harness/CODE_AGENT_BENCHMARKS_SURVEY.md` 升 v2（更正 Aider「无 docker 可立即开跑」→「沙箱前提未满足」+ 两条 root 解法）。
> 🔑 batch-4 关键数据（仍为 R1 硬闸与镜像决策依据）：① 磁盘不约束（`/data/docker` 本地 6.5T 可用，非 NFS）；② 镜像 nominal ≈420–430GB、**层去重后 ~50–100GB**（32 张深清单实测 15.4% 共享率）；③ ⚠️ **Docker Hub 匿名拉取限流 100 次/h**（共用代理出口 IP）；④ 本机 11 镜像无一 SWE-bench；⑤ 重启风险低（0 running 容器）。

> （旧）第十七轮执行**第 3 批**（`7e0b168`）：`harness/CLINE_IMPROVEMENTS_TOP5.html` 已交付（P0 O5/O4、P1 O3、P2 O1/O2，四段式 + 诚实条款）。
> - ⏸ **H-A′ 仍未实跑**（见「待运维拍板」）；H-B 5/5、H-D 均已交付。

### 📦 早期「已办」状态段（round 15–18 期）已滚动归档
> 2026-10-04 第三十四轮：以下 4 段（Docker 解锁 / docker pull 失败根因 / H-C Aider Polyglot 核查 / H-A′ 前置核查 + 可行性结论表 + Lite repo 分布）的**原文**已滚动至 `daily-memories-harness/2026-10-04.md`「从 MEMORY_HARNESS.md 滚动归档」节（结论不改）。要点速记：
- **连通性（2026-10-04 实测）**：GitHub git ✅（走代理）；pypi 官方 000、✅ aliyun `mirrors.aliyun.com/pypi`=200；**npm 官方/npmmirror/npm.aliyun 全 000，唯一可达 = 腾讯镜像 `https://mirrors.cloud.tencent.com/npm/`（走代理；`bun add is-number` 696ms 成功）**；conda 用 tsinghua 镜像；Docker socket 已解锁但 pull 被 dockerd 无代理阻断（L0 已取消）。
- **沙箱**：bwrap/nsjail/firejail/podman 全 absent，仅 `unshare --user --map-root-user` 可用 → R1 走 unshare user-ns 沙箱（步1 已核验 --user --map-root-user --mount --pid 三件套 OK）。
- **工具链**：python/node/bun/javac/g++ 在；`go/rustc/cargo` 全 absent（codex=rust 需先装工具链）。
- **模型/数据**：网关 `http://agi-gateway.cxmt.com/v1` + `deepseek-v4-flash`=200（按模型授权：env key→flash、secrets key→pro-fp4）；SWE-bench_Lite/test=300 已拉 HF 缓存。
- **Lite repo 分布**：django 114(38%) · sympy 77(26%) · matplotlib 23 · scikit-learn 23 · pytest 17 · sphinx 16 · 其余 <7。


## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 2026-10-02 的 7 条流水条目（H-B 5 份源码分析 + H-A §1.1 可行性核查的关键证据路径 `文件:行号`）已于第二十一轮滚动归档至 `daily-memories-harness/2026-10-02.md`「从 MEMORY_HARNESS.md 滚动归档」节（原文不改）。

> 📦 R35~R52 的流水条目（claude-code 打通 · gw_proxy 基建 · 30×4 pilot · batch v2 · relay 多轮健康 skip · MEMORY 滚动）均已滚动归档至 `daily-memories-harness/2026-10-04.md` ~ `daily-memories-harness/2026-10-05.md`（原文不改）。需要时再读。

- 2026-10-04 23:25 —— **第五十轮** —— 已归档（同上）
- 2026-10-07 07:47 —— **第一百三十五轮** —— 📊 昨夜工作汇报 HTML 交付 `report_10_07_harness_overnight.html`（27187B，自包含，内联SVG，8章节）。窗口 R118→R134，codex 43/96/161，总 resolved 61。📦 体积：TASK=35729B(>32KB待归档) / MEMORY=19345B(≤32KB ✓)（归档 0KB）。
- 2026-10-07 08:37 —— **第一百三十六轮** —— TASK.md归档（10-07报告块→ARCHIVE, 37158B→30050B）+ SWEBENCH_COMPARE.html regenerated（72925B, 61 resolved, codex 43/101/156）+ relay skip 88th + git sync 0/0。📦 体积：TASK=30050B(≤32KB ✓) / MEMORY=21120B(≤32KB ✓)（归档 7108B → ARCHIVE_OPERATOR_HARNESS.md）。
- 2026-10-07 09:14 —— **第一百三十七轮** —— codex --resume 进展(+2 pbf, -2 blocked: 43/103/154) + SWEBENCH_COMPARE.html regenerated（72925B, 61 resolved）+ relay skip 89th + push auto-commit(c225e0b5) + git sync 0/0。📦 体积：TASK=29.3KB / MEMORY=22.4KB（归档 0KB）。
- 2026-10-07 09:48 —— **第一百三十八轮** —— codex --resume 进展(+3 pbf, -3 blocked: 43/106/151, [41/197] django__django-15781) + SWEBENCH_COMPARE.html regenerated（72921B, 61 resolved）+ relay skip 90th + git sync 0/0。📦 体积：TASK=29.3KB / MEMORY=24.1KB（归档 0KB）。
- 2026-10-07 13:45 —— **第一百四十三轮** —— opencode×30 progressed to 22/30 (12 res/10 pbf = 54.5%, PID 87730, running inst 23) → SWEBENCH_COMPARE.html regenerated（14377B, 84 entries, 44 resolved）+ relay skip 95th + commit+push。📦 体积：TASK=30.7KB / MEMORY=27.9KB（归档 0KB）。
- 2026-10-07 14:20 —— **第一百四十四轮** —— opencode×30 at 29/30 (14 res/15 pbf = 48.3%, last inst sympy__sympy-13647 running) → SWEBENCH_COMPARE.html regenerated（14568B, 91 entries, 46 resolved）+ all 5 harnesses verified available + gw_proxy healthy + relay skip 96th + R142 archived → commit+push。📦 体积：TASK=30.7KB / MEMORY=31.0KB（归档 ~1.7KB → daily-memories-harness/2026-10-07.md）。
- 2026-10-07 15:02 —— **第一百四十五轮** —— claude-code×30 progress (7/30, 4 res/2 pbf/1 blk = 57.1%, inst 8/30 django__django-11179) → SWEBENCH_COMPARE.html regenerated（14796B, 99 entries, 51 resolved）+ chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 97th + R131~R144 archived to daily → commit+push。📦 体积：TASK=30.7KB / MEMORY=12.8KB（归档 ~13.4KB → daily-memories-harness/2026-10-07.md）。
- 2026-10-07 15:55 —— **第一百四十六轮** —— claude-code×30 progress (10/30, 6 res/3 pbf/1 blk = 60.0%, inst 11/30 django__django-11564) → SWEBENCH_COMPARE.html regenerated（14885B, 102 entries, 53 resolved）+ chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 98th → commit+push。📦 体积：TASK=30.7KB / MEMORY=~14.0KB（归档 0KB）。
- 2026-10-07 16:16 —— **第一百四十七轮** —— claude-code×30 progress (12/30, 7 res/4 pbf/1 blk = 63.6%, inst 13/30 django__django-11620) → SWEBENCH_COMPARE.html regenerated（14943B, 104 entries, 54 resolved）+ data integrity verified (no dupes on 30-set) + chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 99th → commit+push。📦 体积：TASK=30.7KB / MEMORY=~14.0KB（归档 0KB）。
- 2026-10-07 16:53 —— **第一百四十八轮** —— claude-code×30 progress (15/30, 8 res/6 pbf/1 blk = 57.1%, inst 16/30 sympy__sympy-11870) → SWEBENCH_COMPARE.html regenerated（15027B, 107 entries, 55 resolved）+ chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 100th → commit+push。📦 体积：TASK=30.7KB / MEMORY=~14.5KB（归档 0KB）。
- 2026-10-07 17:26 —— **第一百四十九轮** —— claude-code×30 progress (18/30, 8 res/9 pbf/1 blk = 47.1%, inst 19/30 sympy__sympy-12236, +3 pbf since R148) → SWEBENCH_COMPARE.html regenerated（15108B, 110 entries, 55 resolved）+ chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 101st → commit+push。📦 体积：TASK=30.7KB / MEMORY=~17.5KB（归档 0KB）。
- 2026-10-07 18:03 —— **第一百五十轮** —— claude-code×30 progress (21/30, 9 res/11 pbf/1 blk = 45.0%, inst 22/30 sympy__sympy-12481, +3 pbf since R149) → SWEBENCH_COMPARE.html regenerated（15193B, 113 entries, 56 resolved）+ chain script healthy (PID 1292346) + gw_proxy healthy + relay skip 102nd → commit+push。📦 体积：TASK=30.7KB / MEMORY=~19.7KB（归档 0KB）。
- 2026-10-07 19:25 —— **第一百五十二轮** —— ✅ claude-code×30 COMPLETE (13 res/16 pbf/1 blk = 44.8%) → deepseek-harness×30 RUNNING (1/30, django__django-10924 → resolved ✅, toolchain fix confirmed working in production) → SWEBENCH_COMPARE.html regenerated（15409B, 121 entries, 61 resolved）+ chain script healthy (PID 1292346) + gw_proxy + gw_proxy_dsh healthy → commit+push。📦 体积：TASK=30.7KB / MEMORY=~25.5KB（归档 0KB）。
