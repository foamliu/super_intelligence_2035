# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

> 🆕 **R435 (2026-10-18 16:57) — 7×5 PILOT COMPLETE: 1/7 passed (cline-patched 0.8), 6/7 infra-failed → 3 root causes FOUND & FIXED, awaiting re-run**：
> **Pilot 结果**（7 harness × 5 task = 35 trial, .29 PID 2731368, oracle 5/5 ✅ reward=1.0）：
> - **cline-patched** 5/5 mean=**0.800** ✅（4/5 resolved: bn-fit/break-filter/fix-git/log-summary, chess-best-move failed）
> - **codex** 0/5 mean=0.0 — 5×NonZeroAgentExitCodeError（`npm install -g @openai/codex` exit 254）
> - **hermes** 0/5 mean=0.0 — 5×（2 NonZero + 3 AttributeError）（`pip install hermes-agent` PEP 668）
> - **opencode** 0/5 mean=0.0 — 4×NonZeroAgentExitCodeError（`curl|bash` GitHub releases DL exit 56）
> - **claude-code** 0/5 mean=0.0 — 5×NonZeroAgentExitCodeError（`npm install -g @anthropic-ai/claude-code` exit 254）
> - **deepseek-harness** 0/5 mean=0.0 — 5×（2 NonZero + 3 AttributeError）（`pip install deepseek-harness-sdk` PEP 668）
> - **pi** 0/5 mean=0.0 — 5×NonZeroAgentExitCodeError（`npm install -g @fleetagent/pi-coding-agent` exit 254）
> **🔴 Pilot gate: 6/7 = 85.7% infra failure → BLOCKER**（>50% & ≥3 路全挂）。但全为 infra/install 问题，非模型能力。
> **根因 3 类 + Fix**：
> ① **npm RO mount**（codex/claude-code/pi）：`/opt/node` 挂 `:ro` → `npm install -g` 写 `/opt/node/lib/node_modules` → `ENOENT no such file or directory, mkdir '/opt/node/lib/node_modules/@openai'`。**Fix**：`_base.py:_install_node` fast path 加 `mkdir -p /usr/local/lib/node_modules && npm config set prefix /usr/local`。**验证 ✅**：容器内 `npm install -g @openai/codex@0.94.0` → `codex-cli 0.94.0` exit 0（3min, bn-fit-modify image）。
> ② **pip PEP 668**（hermes/deepseek-harness）：容器 Python 3.12 `externally-managed-environment` → pip 拒绝系统级安装。**Fix**：加 `--break-system-packages` flag。
> ③ **opencode GitHub DL**（opencode）：`curl -fsSL https://opencode.ai/install | bash` → 脚本从 `github.com/anomalyco/opencode/releases` 下载二进制 → proxy exit 56（NetworkConnectionError）。**Fix**：改用 `npm install -g opencode-ai`（install script 的 npm fallback 路径），复用 ① 的 prefix fix。
> **修复文件**：`agents/_base.py`（npm prefix）、`agents/hermes.py`（--break-system-packages）、`agents/deepseek_harness.py`（--break-system-packages）、`agents/opencode.py`（npm install 替代 curl|bash）。py_compile ✅ 7/7，28/28 mock 单测 ✅。
> **Next**：① git push（adapter 修复在 NFS 共享，.29 立即可见）② .29 重跑 `launch_tb_7way.sh --pilot` ③ gate（infra ≤20%, ≥6/7 runnable）→ ④ full 7×89 ⑤ gen_report。📦 体积：TASK≈30KB / MEMORY≈27KB（归档 R432+旧指令 ~7KB → ARCHIVE）。

> 🟢 **R433 (2026-10-18 15:03) — SMOKE PASSED reward=1.0 ✅ + 7×5 pilot launched（crashed → R434 修复重跑）**：
> **solo smoke R433b (cline-patched × fix-git) ✅ reward 1.0**（`n_completed:1, n_errored:0, mean:1.0`，14:43→14:50）。verifier 流程：`apt install curl`→`curl -LsSf astral.sh/uv/0.9.5/install.sh`（SSL timeout rc=28 ~5min）→`source /root/.local/bin/env`→`uvx -p3.13 pytest`→**2 passed**（test_about_file/test_layout_file）→reward.txt=1。**根因修复确认**：overlay `client:`→`main:` + `network_mode:host` + 挂 `/root/.local/bin/env`（verifier `source env` 找到 mounted uvx）。cline agent 跑了 13 轮 API（run_commands×3+/editor×1+，exit_code:0）真实解题，非 infra 噪声。
> **overlay 再优化（commit 27758bad）**：`no_proxy`/`NO_PROXY` 加 `astral.sh` —— .29 对 astral.sh **直连 Network unreachable**（无互联网路由），绕过代理后 curl rc=7 **~3s 快失败** vs 经代理 CDN TLS 挂 ~5min → 每 verifier 省 ~5min（full 623 trial 省 ~52h）。`/etc/hosts` 挂载 + `--add-host` 在 `network_mode:host` 下**均失效**（getent 仍返真实 Cloudflare IP），故用 no_proxy 方案。YAML ✅，容器内实测 curl 3s 快失败 + 流程续到 uvx。
> **7×5 PILOT 已启动**（.29 PID 1331208，15:03:31，wrapper `/nas_train/app.e0031982/download/tb-overlay/tb_pilot_7way.sh`）：oracle check(5 task, n-concurrent 4)→7 harness×5 task=35 trial。pilot task 改用**本地有镜像**的 5 个 `break-filter-js-from-html / bn-fit-modify / log-summary-date-ranges / chess-best-move / fix-git`——原 `regex-log`/`sqlite-db-truncate` **无本地镜像**且 Docker Hub pull 被代理阻断（registry-1.docker.io timeout）→已替换（launch_tb_7way.sh 已改）。wrapper 注入 PATH(~/.local/bin harbor)+proxy+TB_API_KEY，避 §3(4)「非登录 shell 无 cline/harbor」坑。启动验证：harbor 0.24.0 ✅、key len 72 ✅、overlay astral.sh 7 行 ✅、oracle 容器 fix-git Up ✅。
> **🔴 FULL-EVAL 镜像阻塞预警**：89 task 仅 **~15 本地镜像**（alexgshaw/*:20251031）；Docker Hub pull 被 MITM 代理阻断（registry-1.docker.io `Client.Timeout exceeded`）→ full 7×89 暂只能跑本地镜像 task。需解决镜像拉取（Docker Hub mirror / 批量预拉 / 本地 build）才能跑满 89。
> **Next**：① poll oracle check（5 task reward 应=1.0，验证 overlay 对多 task 有效 + curl 快失败）② oracle ✅ → 监控 7 harness 35 trial（gate: infra≤20%, ≥6/7 runnable）③ 解决 full-eval 镜像拉取 ④ full 7×89 ⑤ gen_7way_report。
> 🆕 **R434 (2026-10-18 15:22) — `-p` 单值 BUG 修复 → oracle 5/5 ✅ → PILOT RE-LAUNCH (PID 2731368)**：
> **R433 pilot 崩溃双因**：① `harbor run -p/--path` 是**单值**（`Path|None` last-wins，非 `list[Path]`，源码 harbor/cli/jobs.py 确认）→ 多个 `-p` 只留最后一个 → oracle 实跑 1 task(fix-git reward=1, 1m48s, astral.sh 快失败 ✅)。② **运行中编辑 NFS 上的 launch_tb_7way.sh** → bash 增量读遇 `Stale file handle` → 脚本 oracle 后崩溃，7 harness 未跑。
> **修复(commit 6ebf67f7)**：pilot=`mktemp -d`+5 symlink→单 `-p <dataset-dir>`；full=`-p ${TB_TASKS_DIR}`。bash -n ✅。**oracle_val5 独立验证 5/5 reward=1** ✅（break-filter/log-summary 慢：verifier test.sh 内 apt-get 经代理每次重跑，非镜像层缓存）。
> **PILOT RE-LAUNCHED**(.29 PID 2731368, setsid 后台, `/tmp/launch_pilot.sh` 注 PATH+proxy+TB_API_KEY)：oracle 4/5 reward=1(break-filter apt-get 中)→将跑 7 harness×5=35 trial。**🔒铁律：pilot 运行期间禁编辑 NFS 上 launch_tb_7way.sh**。
> **Next**：① oracle 5/5→② 首个 harness(cline-patched)确认 kimi API 调通→③ 35-trial gate(infra≤20%,≥6/7)→④ full-eval 镜像方案→⑤ full 7×89。📦MEMORY~32.4KB,R432 待归档。


> 📦 R432 (2026-10-18 13:50, 4 bugs fixed + gateway ✅ + docker blocker → resolved) 已归档 → daily-memories-harness/2026-10-18.md。结论：PYTHONPATH/key/overlay 3 bugs 修复，docker 权限已由运维恢复，smoke+ pilot 已跑。需要时再读。

> 📦 R431 (2026-10-18 12:30) — archived → `daily-memories-harness/2026-10-18.md`。结论：relay fixed（inbox RUN_ID 标记问题），smoke failed at cline install（npm fallback 装错包），3 bugs found（A:PYTHONPATH / B:key提取 / C:Docker Hub不可达）——**全部在 R432 修复**（C 改用 overlay 挂 host cline 二进制，绕过 npm）。
> 📦 §运维指令(2026-10-16) + DATA-LOSS BUG#2 + glm53 7×300 COMPLETE + TB 2.0 R426 progress + Proxy notes 已归档 → daily-memories-harness/2026-10-18.md。结论：glm53 2100/2100 DONE(577 resolved)，data-loss bug 修复，TB Docker/networking/oracle 全打通。需要时再读。

> 📦 §P1 PLAN（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：P1-2 rerun ✅ DONE (54/54, 4 resolved)，kimi 574→621 resolved (29.6%)。fix3 ✅ (0 flipped)。剩余 P1-1(astropy) 待批。需要时再读。
> 📦 §FIX2 RESULTS（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：fix2 32 条重评完成，9 FLIPPED (pytest)，0 FLIPPED (flask)，累计 574→617 (29.4%)。需要时再读。

## 📊 进度快照

```
PHASE:        TB T2 7×5 PILOT v2 — 6/7 infra-fail FIXED (npm prefix + pip --break-system-packages + opencode via npm), awaiting re-run
已完成:       ①-㉘ same · ㉙ Oracle 5/5 ✅ · ㉛ 7 adapters + mock 28/28 · ㉜ launch script · ㉝ smoke ✅ reward 1.0 · ㉞ 7×5 pilot v1 COMPLETE (cline-patched 0.8, 6/7 infra-fail) · ㉟ 3 root causes found + FIXED (R435)
当前动作:     R435 (16:57): pilot v1 结果分析 + 3 类 infra bug 修复（npm RO mount / pip PEP668 / opencode GitHub DL）。4 adapter 文件已改，py_compile + 28/28 mock ✅，npm prefix fix 容器实测 ✅ codex-cli 0.94.0。待 git push + .29 重跑 pilot。
下一步:       ① git push ② .29 重跑 `launch_tb_7way.sh --pilot` ③ pilot gate（infra ≤20%, ≥6/7 runnable）→ ④ full 7×89 ⑤ gen_report
阻塞:         无（infra bugs 已修，待验证）。🔴 full-eval 镜像阻塞预警：89 task 仅 ~15 本地镜像，Docker Hub pull 被代理阻断。
ERROR_COUNT:  0
```

**本唤醒流水**：
- 2026-10-18 16:57 —— R435: 7×5 pilot v1 COMPLETE（.29, 35 trial）。oracle 5/5 ✅。cline-patched 4/5 (0.8) ✅。6/7 harness 全 infra-fail（codex/claude-code/pi: npm ENOENT on RO /opt/node; hermes/deepseek: pip PEP668; opencode: GitHub DL exit 56）。3 类根因全 FIXED: _base.py npm prefix /usr/local + hermes/deepseek --break-system-packages + opencode npm install。容器实测 codex-cli 0.94.0 ✅。28/28 mock ✅。待 push + .29 重跑 pilot。
- 2026-10-18 12:30 —— R431: ① ops relay 修复——RUN_ID 123 不执行真因=inbox.md 触发标记 122 未更到 123（relay 未冻结），已 122→123(commit eb204521)+push，123 在 .29 执行成功；kill .12 stray relay(pid 1048010)，.29 single relay(pid 1972249,ppid=1)；123 probe 训练全健康。② TB solo smoke 跑起 on .29：cline-patched × fix-git(cached image)，跑 2m24s → FAILED at cline install(npm install -g cline exit 1；根因=cline 是 bun 源码构建非 npm 包，fast-path 嵌入式 bun 二进制不存在)。③ 发现 3 bug：launch_tb_7way.sh 未设 PYTHONPATH(自定义 adapter 导入失败)/key 提取破损(全角冒号+-A1,取空→401)/Docker Hub 不可达 via proxy(仅 cached image 能跑,regex-log 未缓存致首试 16s 失败)。改 fix-git(cache)后容器 Up，但 cline install fail。WAITING=0 待修 cline install 路径。
- 2026-10-18 07:20 —— R430: MEMORY archived 33.5KB→23.6KB · _base.py _install_node fixed (NVM+aliyun mirror replaces blocked nodesource.com) · launch_tb_7way.sh fixed (local -p paths + minimal2 overlay, 5 pilot tasks) · 28/28 adapter tests OK · Docker on .29 ✅ (not .12) · Next: smoke test 1 adapter on .29
- 2026-10-18 06:06 —— R429: Oracle 5/5 ✅ ALL PASS (BCE fix8: numpy 2.x alias + planarity 1.0.0 key remap). Details → daily-memories-harness/2026-10-18.md
- 2026-10-18 03:55 —— R427: Oracle 4/5 (build-pmars ✅ fix125 snapshot, BCE ❌ numpy 2.x). Details → daily-memories-harness/2026-10-18.md
- 2026-10-18 04:25 —— R428: ARS ✅ restored via minimal2 overlay (bookworm only, no Rprofile). Dual-overlay strategy. Details → daily-memories-harness/2026-10-18.md
- 2026-10-17 21:12 —— R426: Codex pilot API SOLVED (wire_api=chat), task timeout on R install. Details → daily-memories-harness/2026-10-17.md
- 2026-10-17 17:57 —— **R425: TB 2.0 Docker networking SOLVED + Oracle 1-task ✅ reward 1.0** —— 运维直连 .29 解决全部 TB T2 blocker：① **Docker ✅**：用户已在 docker 组, `docker ps` + `docker pull` 正常。② **Dataset ✅**：`terminal-bench@2.0` 89 tasks 已下载到 `~/terminal-bench/`, registry at `/tmp/tb_registry_full.json`。③ **/tmp cleanup**：释放 2.7G (17G→15G, 79G available)。④ **Docker networking fix**（核心突破）：proxy (172.19.92.25:13128) 是 MITM — HTTP block archive.ubuntu.com/deb.debian.org (302→disable.htm), HTTPS pypi.org → tls eof。**但** mirrors.aliyun.com HTTP (apt) + HTTPS (pip/uv) 均可用。解决方案：`network_mode: host` + aliyun apt mirror (HTTP) + uv/uvx 从 host mount + Python 3.13 从 host uv data mount + `UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/`。Overlay at `/tmp/network-host-overlay.yml`。⑤ **Oracle 1-task ✅ reward 1.0** (adaptive-rejection-sampler, 1m55s, 9/9 pytest passed)。⑥ **Oracle -k 5 validation running** (PID 1680140, 5 tasks, -n 1)。Docker daemon proxy 在 `/etc/docker/daemon.json` ✅, image pull 正常 ✅。📦 体积：TASK ~31KB / MEMORY 待测。
> 📦 R424 (2026-10-17 16:02, TB T2 blocker 深查 — Docker blocked + dataset 名 + OAuth URL) 已归档 → daily-memories-harness/2026-10-17.md。结论：Docker permission denied, 数据集实际名 terminal-bench-core@0.1.1, 需 Harbor Hub auth。**全部已由 R425 运维直连解决**。需要时再读。
> 📦 R421-R423 (2026-10-17 11:42~14:45) 已归档 → daily-memories-harness/2026-10-17.md。需要时再读。
> 📦 R414-R420 (2026-10-17 02:59~10:28) 已归档 → daily-memories-harness/2026-10-17.md。需要时再读。
> 📦 R411 (2026-10-16 23:05, 重启 4 路补跑 glm53 7×300) 已归档 → daily-memories-harness/2026-10-16.md；结论：1960/2100(140pending)，退出根因=API 429 并发限流，写 restart_glm53_4routes.sh 启动 4 路(codex/deepseek/hermes 已 DONE 不重启)。需要时再读。
> 📦 R416-R425 (2026-10-16~17, glm53 7×300 报告 + Codex pilot + Docker networking) 已归档 → daily-memories-harness/2026-10-16.md + 2026-10-17.md。需要时再读。
> 📦 R366-R385 (2026-10-14, ~20 rounds of glm53 monitoring 23→872 + rerun + fixes) 已归档 → daily-memories-harness/2026-10-14.md + 2026-10-15.md。需要时再读。
> 📦 R386 (2026-10-15 01:08, glm53 monitoring 872/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R387 (2026-10-15 01:42, glm53 monitoring 887/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R388 (2026-10-15 02:17, glm53 monitoring 908/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R389 (2026-10-15 02:52, glm53 monitoring 933/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R390 (2026-10-15 03:26, glm53 monitoring 959/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R391 (2026-10-15 04:02, glm53 monitoring 980/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R392 (2026-10-15 04:38, glm53 monitoring 1012/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R393 (2026-10-15 05:14, glm53 monitoring 1044/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R394 (2026-10-15 05:48, glm53 monitoring 1068/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R395 (2026-10-15 06:23, glm53 monitoring 1089/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R397 (2026-10-15 07:31, glm53 monitoring 1137/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R398-R400 (2026-10-15, glm53 monitoring 1154→1177) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R401-R405 (2026-10-15 10:03~12:37, DATA-LOSS BUG FIX + glm53 monitoring 1186→1226) 已归档 → daily-memories-harness/2026-10-15.md。结论：save_results bug 修复（atomic write + skip-on-parse-error），1186→1306 entries 持续增长。需要时再读。
> 📦 R352-R406 (2026-10-13~15, 44+ rounds of monitoring/fixes/reports) 已归档 → daily-memories-harness/2026-10-13.md + 2026-10-14.md + 2026-10-15.md。需要时再读。

> 📦 §口径与并发 (2026-10-08⑦) 已归档 → daily-memories-harness/2026-10-08.md。**结论**：R1串行 vs R2并行已披露，workdir隔离修复holding，R2 resolve-rate下降=实例难度差异非并发污染。需要时再读。

## 🗣️ 运维问答

> 📦 §运维问答·2026-10-08ⓔ（Q1-Q5 下一步工作建议）已归档 → daily-memories-harness/2026-10-08.md。**结论**：Q1-Q5 已回答（codex 300 偏差 3.3×、nobody-solved 12 条、patch 重叠度、wall time vs resolution、多 backbone 3 阶段建议），均已写入报告。需要时再读。
> **当前无待答运维问题**。

> 📦 R196-R202 (2026-10-09, SWEBENCH_COMPARE monitoring) 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。

> 📦 R198（2026-10-09 02:47）已归档 → daily-memories-harness/2026-10-09.md。结论：SWEBENCH_COMPARE 55001B/586entries/164resolved，quota_blocked=0。需要时再读。

> 📦 R200（2026-10-09 04:10）已归档 → daily-memories-harness/2026-10-09.md。结论：SWEBENCH_COMPARE 55942B/621entries/166resolved，5 procs alive，quota_blocked=0。需要时再读。

> 📦 R202（2026-10-09 05:19）已归档 → daily-memories-harness/2026-10-09.md。结论：SWEBENCH_COMPARE 56175B/631entries/177resolved，5 procs alive，quota_blocked=0。需要时再读。

> 📦 R201（2026-10-09 04:43）已归档 → daily-memories-harness/2026-10-09.md。结论：SWEBENCH_COMPARE 56090B/627entries/172resolved，5 procs alive，quota_blocked=0。需要时再读。

> 📦 R183/R186（2026-10-08 16:38~17:30，health-check + Q&A delivered）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：5 questions answered (Q1-Q5)，all deliverables verified intact。需要时再读。

> 📦 R191（2026-10-08 22:39，Round-2 progress monitor）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：quota_blocked=0，NO parallel pollution，R2 resolve-rate 下降=实例集组成偏差。需要时再读。

> 📦 R188（2026-10-08 20:40，⑦ 口径披露 + 轨迹报告补落根目录 + SWEBENCH_COMPARE 升级 7×100）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：口径与并发 section ✅，trace report in doc root ✅，gen_round2_compare.py ✅。需要时再读。


> 📦 R186/R184/R183（2026-10-08 16:38~18:30，health-check + Q&A delivered）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：5 questions answered (Q1-Q5)，all deliverables verified intact。需要时再读。

> 📦 R169-R182（2026-10-08 07:15~16:03，14 轮：Hermes×30 COMPLETE→7-way ALL DONE→report 交付→3-way/7-way HTML→§4.5→health-check）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：7-way 横评全完成（40%–60%），report + 3-way/7-way HTML 均已交付。

> 📦 R166-R168（2026-10-08 05:00~06:07，Hermes×30 progress 19→22/30）已滚动归档至 `daily-memories-harness/2026-10-08.md`。结论：Hermes 推进 19→22/30，最终 16/30=53.3%。


> 📦 R159-R165（2026-10-07 23:53 ~ 2026-10-08 04:26，Pi×30 progress + Hermes×30 启动/progress 3/30→16/30 + 版本复核 + HTML version table）已滚动归档至 daily-memories-harness/2026-10-08.md。结论：Hermes×30 从 3/30 推进到 16/30 (50.0%)，版本/commit 已验证并写入 HTML version table。


> 📦 R154-R158（2026-10-07 20:34~23:18，deepseek-harness×30 progress + COMPLETE + Pi smoke-test + Hermes unavailable 误判 + gen_kimi_compare.py 7-way 升级）已滚动归档至 `daily-memories-harness/2026-10-07.md`「从 MEMORY_HARNESS.md 滚动归档」节。结论：deepseek-harness×30 COMPLETE 40.0%，Pi smoke-test PASSED，Hermes toolchain 误判后纠正。

> 📦 R147-R153（2026-10-07 16:16~19:59，claude-code×30 全程 + deepseek-harness×30 启动 + toolchain 修复 + 早期 progress）已滚动归档至 `daily-memories-harness/2026-10-07.md`「从 MEMORY_HARNESS.md 滚动归档」节。结论：claude-code×30 COMPLETE 44.8%，deepseek-harness×30 RUNNING (toolchain fixed via gw_proxy_dsh.py port 9091)。
> 📦 R131~R145 已归档至同文件。R113及更早已归档至 `daily-memories-harness/2026-10-04.md` ~ `2026-10-06.md`。

> 📦 §运维必读(2026-10-04) + batch-5/batch-4 + early rounds 已归档 → daily-memories-harness/2026-10-18.md「ARCHIVED from MEMORY」节。结论：SWE-bench 7×300 pipeline 打通(cline→r1_eval→resolved)，R1 unshare 沙箱可行，连通性/npm/docker 均已查明。需要时再读。

## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（详见上方 `## 🗣️ 运维问答 · 2026-10-08④（下一步工作建议）` 小节，2026-10-08 17:30 已回答 5 个问题。）

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
> 📦 R135~R159 的流水条目（Oct-7: report HTML · TASK归档 · codex --resume · opencode×30 · claude-code×30 · deepseek-harness×30 · Pi×30 progress）已滚动归档至 `daily-memories-harness/2026-10-07.md`「从 MEMORY_HARNESS.md 滚动归档 R135~R159」节（原文不改）。需要时再读。
- 2026-10-08 09:46 —— **第一百七十二~七十六轮** —— 📄 report_harness_swebench_analysis.html 交付（64201B, 9 sections, deep analysis with failure modes, cost analysis, BaiZe implications）→ HARNESS_3WAY_COMPARISON.html 交付（59268B, 14 sections, cline/Pi/Hermes deep comparison）→ HARNESS_7WAY_COMPARISON.html 交付（56352B, 10 sections, 5 inline SVG, superset analysis finding）→ all verified at both locations → commit+push。📦 体积：TASK=31.5KB / MEMORY=~29KB（归档 0KB）。
- 2026-10-08 13:00 —— **第一百七十八轮** —— 💓 Health-check heartbeat：all deliverables verified intact, no new instructions, no running chains → commit+push。📦 体积：TASK=32277B(31.5KB ✓) / MEMORY=~29KB(28.3KB ✓)（归档 0KB）。
- 2026-10-08 13:38 —— **第一百七十九轮** —— 💓 Health-check heartbeat：all deliverables verified intact (SWEBENCH_COMPARE 21976B, report_harness_swebench_analysis 64201B, HARNESS_7WAY_COMPARISON 56352B, HARNESS_3WAY_COMPARISON 59268B, kimi_pilot_results.json 532623B)，no new instructions (git fetch=up to date)，no running chains → commit+push。📦 体积：TASK=32277B(31.5KB ✓) / MEMORY=~29.6KB(28.9KB ✓)（归档 0KB）。
- 2026-10-08 14:11 —— **第一百八十轮** —— 💓 Health-check heartbeat：all deliverables verified intact, no new instructions, no running chains → commit+push。📦 体积：TASK=32277B(31.5KB ✓) / MEMORY=~31KB(30.4KB ✓)（归档 0KB）。
- 2026-10-08 15:19 —— **第一百八十一轮** —— 💓 Health-check heartbeat：report_harness_swebench_analysis.html re-verified (9 sections, 64201B, all requirements met: TL;DR/eval design/results/failure modes SVG/cost SVG/architecture/BaiZe implications/limitations/next steps), no new instructions, no running chains, R160-R171 archived to daily → commit+push。📦 体积：TASK=32277B(31.5KB ✓) / MEMORY=~30KB(29.3KB ✓)（归档 ~4KB → daily-memories-harness/2026-10-08.md）。
> 📦 R185-R192 (2026-10-08 17:58~23:17) 已归档 → daily-memories-harness/2026-10-08.md（原文保留）。需要时再读。
> 📦 R193-R194 (2026-10-08 23:50~10-09 00:25) 已归档 → daily-memories-harness/2026-10-09.md（原文保留）。需要时再读。
> 📦 R195-R199 (2026-10-09 01:00~03:30) 已归档 → daily-memories-harness/2026-10-09.md（原文保留）。需要时再读。

- 2026-10-09 05:55 —— **第二百零三轮** —— 已归档（同下）→ daily-memories-harness/2026-10-09.md。
- 2026-10-09 06:30 —— **第二百零四轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 07:05 —— **第二百零五轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 07:39 —— **第二百零六轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 08:13 —— **第二百零七轮** —— 已归档 → daily-memories-harness/2026-10-09.md（⚠️ WORKDIR-BLOCKED DISCOVERY: 88 blocked, all R2 parallel, git checkout conflicts from shared workdirs. opencode DONE 100/100 35.0%. Plan: hermes done → serial re-run blocked → final 7×100）。需要时再读。
> 📦 R208-R229 (2026-10-09 09:04~23:20, 7×100 第二轮 + blocked re-run + SWEBENCH_COMPARE) 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
> 📦 R230-R258 (2026-10-10 00:14~17:37, smoke test + 7×300 launch + monitoring 62%→71%) 已归档 → daily-memories-harness/2026-10-10.md。结论：7×300 launched 00:14, ALL 7 alive, workdir block=0 holding (R231→R258), progress 0→71.1% (1494/2100). 需要时再读。
> 📦 R259-R268 (2026-10-10 18:13~23:29, 7×300 monitoring 72.0%→78.2%) 已归档 → daily-memories-harness/2026-10-10.md。结论：1528→1642/2100, 334→362 resolved, workdir block=0 (30→38 rounds), hermes ETA 26→23.7h。需要时再读。
> 📦 R269-R276 (2026-10-11 00:05~04:18, 7×300 monitoring 78.7%→83.4%) 已归档 → daily-memories-harness/2026-10-11.md。结论：1670→1751/2100, 369→393 resolved, workdir block=0 (40→46 rounds), hermes ETA 23→22h。需要时再读。
> 📦 R277-R281 (2026-10-11 04:54~07:18, 7×300 monitoring 83.9%→85.7%) 已归档 → daily-memories-harness/2026-10-11.md。结论：1762→1800/2100, 398→413 resolved, workdir block=0 (47→51 rounds), blocked 90→83 trend, hermes ETA 18h。需要时再读。
- 2026-10-11 13:51 —— **第二百九十二轮** —— 7×300 monitoring at 13:51 (2257 min since 00:14 launch, 37.6h). ALL 7 alive (etimes ~135417s, stat=S). 1927/2100 (91.8%), +14 since R291 (36 min). 487 resolved (+6) / 1355 pbf / 74 blocked (11 checkout + 61 git_fetch_503 + 1 timeout + 1 other) + 7 qb (ALL django__django-16873 API quota) + 4 np (all deepseek). Workdir fix holding ✅ (62nd round, 0 new checkout/overwrite). Code fix applied: git checkout -f (4 places in git_clone_or_fetch, lines 110/114/124/128) to force-clear 11 legacy checkout blocks on next process restart. Per-harness: cline 287(78,rem13) / codex 300(72,rem0,21 blk) / claude 264(61,rem36) / opencode 293(83,rem7) / deepseek 278(57,rem22) / hermes 235(58,rem65←BOTTLENECK,ETA~19.5h→~Oct 12 09:20) / pi 270(78,rem30). Blocked trend: 72→74 (+2: new git_fetch_503). Resources: load 16.95/16.34/13.50, 1821G avail RAM, /dev/shm 17G/992G(2%), GPU 100% (pretrain R2 active). 📦 体积：TASK=32106B(31.4KB ✓) / MEMORY≈32400B(31.6KB ✓)。
- 2026-10-14 11:10 —— **glm53 7×300 LAUNCHED** —— 403 RESOLVED: glm53 key works on `/v1` (HTTP 200) NOT `/cloud/v1` (HTTP 403). Fixed `launch_glm53_7x300.sh`: GLM53_BASE + GW_UPSTREAM → `/v1`; cline globalState.json openAiBaseUrl → `/v1` (backed up). 7 harnesses launched (PIDs 1262875~1278074), gw_proxy 9092/9093 → `/v1`. cline-patched first instance (astropy-12907) already in EVAL phase ✅. P1-2 rerun ~20/54 still running. 📦 体积：TASK=27362B(26.7KB ✓) / MEMORY≈31100B(30.4KB ✓) / 归档 0B。
- 2026-10-14 13:50 —— **cline-patched 403 真正修复** —— 发现上一轮 403 修复不完整：`launch_glm53_7x300.sh` 更新了 `~/.cline/data/globalState.json`（默认 cline 数据目录），但 cline-patched 用独立 data dir `/nas_train/app.e0031982/harness_work/cline_harness_data/`（`run_single.py:28` `--data-dir`），其 `globalState.json` 仍指向 `http://127.0.0.1:9090/v1`（kimi proxy 9090 → kimi key → `/cloud` → 403）。全部 61 条 cline-patched 条目均有 Forbidden（rc=1, wall~3s, empty patch）。**修复**：① harness data dir `globalState.json` `openAiBaseUrl` 9090→9092, model→glm-5.3-flash；② 删除 61 条无效条目（flock）；③ `setsid` 重启 cline-patched（PID 314979）；④ 验证：首条 astropy-12907 `[RUN]`→`[EVAL]` 无 Forbidden ✅。7 路全部存活。172 entries, 63 resolved (36.6%), 109 pbf。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈31.5KB(✓) / 归档 0B。
- 2026-10-14 14:36 —— **glm53 monitoring + P1-2 rerun DONE** —— curl /v1 → 200 ✅。所有脚本 base URL 确认 `/v1`（launch_glm53_7x300.sh / run_harness.py / run_serial_kimi.py 均 ✅）。P1-2 rerun 54/54 完成（4 resolved, 42 pbf, 8 blocked），rerun_blocked 进程已退出。glm53 7×300: 244/2100 (11.6%), 72 resolved (29.6%), 171 pbf, 0 blocked/no-patch。Per-harness: codex 84(33, 39.3%), deepseek 110(25, 22.7%), claude-code 15(6, 40.0%), hermes 11(3, 27.3%), opencode 11(2, 18.2%), pi 11(3, 27.3%), cline-patched 2(0, 0.0%, 无 403 ✅)。glm53 29.6% vs kimi 29.6%（621/2100）持平。ETA ~18h。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY=30041B(29.3KB ✓) / 归档 0B。
- 2026-10-14 15:12 —— **glm53 7×300 monitoring** —— ALL 7 alive (cline-patched etimes=4284s~71min, 其余 6 路 ~14490s~4h)。**298/2100 (14.2%), 77 resolved (25.8%), 220 pbf, 1 quota-blocked (deepseek django-16873)**。Per-harness: codex 108(33,30.6%) / deepseek 132(25,18.9%,1qb) / claude-code 16(6,37.5%) / hermes 14(6,42.9%) / opencode 12(3,25.0%) / pi 12(4,33.3%) / cline-patched 4(0,0.0%,刚重启)。无 403/Forbidden ✅。**glm53 25.8% vs kimi 27.3%（原口径 574/2100）** → 略低，298 条样本尚小。eta ~16h。load 30.1, RAM 1883G, /dev/shm 985G。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY=30226B(29.5KB ✓) / 归档 0B。
> 📦 2026-10-14 17:17~19:43 (R375-R378, glm53 CRASH RECOVERY + monitoring 344→526/2100) 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
