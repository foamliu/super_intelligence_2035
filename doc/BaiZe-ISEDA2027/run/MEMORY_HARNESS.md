# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        TB 7×5 pilot Gen3 DONE → GATE FAILED (85.7% err, 1/7 runnable) → 🔴 BLOCKED per 预注册门据
已完成:       oracle 5/5 ✅ · 7 adapters 骨架 ✅ · 28/28 mock ✅ · smoke ✅(R433) · pilot Gen3 ✅(35 trials ran, 08:52 exit0) · cline-patched 5/5 resolved ✅
当前动作:     R447: pilot Gen3 已完成(08:52)→解析 7 路 result.json→仅 cline-patched 5/5 resolved；其余 6 路 CLI "exited with code 1"(5 缺 auth/config 注入 + pi docker-cp 路径 bug)；按预注册门据 >50%→🔴 STOP 报 blocker，未启 7×89
下一步:       下轮修 6 适配器：codex/hermes/opencode/claude-code/deepseek-harness 注入 kimi-k2.6-cloud 的 API-key/baseURL/model 配置；pi 改为先 mkdir -p /root/.pi/agent 再 docker cp models.json → 重跑 7×5 pilot → 再判门据(infra≤20% AND ≥6/7)→放行 7×89
阻塞:         🔴 pilot gate FAIL: adapter-err 85.7%(30/35)，仅 1/7 runnable。cline-patched 5/5 证明 Docker/API/dataset/oracle/trace 全 OK → 非 env-infra，是 6 适配器 CLI 装好即 exit1(配置未注入)。每路原文见 R447。等运维裁定是否由我修适配器
ERROR_COUNT:  1
```

> 🆕 **R447 (2026-10-19 09:08) — 🔴 7×5 pilot Gen3 DONE → GATE FAILED (85.7% adapter-err, 1/7 runnable) → STOP 报 blocker，未启 7×89**：
> **① pilot Gen3 已完成**：`[pilot_gen3] END 2026-10-19 08:52:25 exit=0`，7 路 × 5 task = 35 trials 全跑完（`.29` via SSH，PID 2393345）。oracle_check ran 1m20s。Docker 3 容器 cached `alexgshaw/*:20251031` Up。聚合 `terminalbench_kimi_k2.6_results.json` **未生成**（launch 脚本只 echo 路径，未 merge；per-harness 结果在 `jobs_<name>/<ts>/result.json`）。
> **② 四分类（解析 7 路 result.json）**：
> | harness | total | resolved | failed | errored | runnable |
> |:--|--:|--:|--:|--:|:--|
> | cline-patched | 5 | **5** | 0 | 0 | ✅ YES |
> | codex | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> | hermes | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> | opencode | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> | claude-code | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> | deepseek-harness | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> | pi | 5 | 0 | 0 | 5(RuntimeError) | ❌ NO |
> TOTAL=35, resolved=5, errored=30, **infra/adapter-err rate=85.7%**, **runnable=1/7**。
> **③ 预注册门据判定**：infra≤20% AND ≥6/7 runnable → ✅放行；20–50% → ⚠️修infra不放行；**>50% 或 ≥3 路完全跑不起来 → 🔴 停报 blocker**。现 85.7%(>50%) 且 6/7 完全失败(≥3) → **🔴 STOP，未启 7×89**。
> **④ 根因（每路失败原文）**——**非 env-infra**（cline-patched 5/5 证明 Docker/API/kimi-k2.6-cloud 网关/dataset/oracle/trace 全 OK），是**适配器 CLI 装好即 exit 1**：
>   - **codex**：`npm install -g @openai/codex@0.94.0` OK → `Trial ... failed: Codex exited with code 1:`（CLI exit1，疑缺 OPENAI_API_KEY/baseURL 指向 kimi 网关的配置注入）。
>   - **hermes**：`pip install --break-system-packages hermes-agent` OK → `Hermes exited with code 1:`（同上，缺 auth/config 注入）。
>   - **opencode**：`npm install -g opencode-ai` OK → `OpenCode exited with code 1:`（同上；且 `traces/opencode_run.log`=0B）。
>   - **claude-code**：`npm install -g @anthropic-ai/claude-code` OK → `Claude-Code exited with code 1:`（同上，缺 ANTHROPIC auth/网关配置）。
>   - **deepseek-harness**：`pip install --break-system-packages deepseek-harness-sdk` OK → `DeepSeek-Harness exited with code 1:`（同上）。
>   - **pi**（**不同根因**）：`npm install -g --ignore-scripts @fleetagent/pi-coding-agent@latest` OK → `docker compose cp ... main:/root/.pi/agent/models.json` → `Error response from daemon: Could not find the file /root/.pi/agent in container`（适配器顺序 bug：目标目录 `/root/.pi/agent` 未先 mkdir 就 cp）。
>   - **cline-patched（对照，工作）**：`ln -sf /opt/cline-modules/@cline/cli-linux-x64/bin/cline /usr/local/bin/cline && cline --version` → 5/5 reward 1.0（bn-fit-modify/break-filter-js-from-html/chess-best-move/fix-git/log-summary-date-ranges 全 resolved）。
> **⑤ 提议修复（待运维裁定是否由我执行）**：(a) codex/hermes/opencode/claude-code/deepseek-harness 5 适配器：在 `step()/install()` 注入 kimi-k2.6-cloud 的 API-key + baseURL(`http://agi-gateway.cxmt.com/cloud/v1`) + model 到各 CLI 期望的 env/config 文件（参照 cline-patched R433 的做法）；(b) pi 适配器：cp 前先 `mkdir -p /root/.pi/agent`（或先跑一次 pi 让其 scaffold）。修完重跑 **同一个 7×5 pilot** 再判门据。🚫 不用假分数/跳过 trial 凑数，🚫 不把 adapter-err 算成 harness 能力失败。
> **⑥ 纪律**：commit 前缀 `harness tb:`；不占 GPU；relay `.12` PID2663131 健康(last_run_id=139)；inbox 仍 RUN_ID139(只读诊断)，无 >139 新指令。📦 体积：TASK=29962B(29.2KB✓) / MEMORY 37194B→归档 R446全文+旧快照+旧流水(R425-R441)→daily-10-19 →24886B(24.3KB✓)。WAITING=1（STOP 报 blocker 等裁定；按判死判据本轮已提交心跳）。


> 📦 R446 (2026-10-19 07:47, 🟢 Docker 在 .29 可用 + 7×5 pilot Gen3 启动) 已归档 → daily-memories-harness/2026-10-19.md。结论：纠正 R436-R445 误判（Docker 只在 .29），pilot Gen3 已启动（由 R447 承接：pilot done 08:52，gate failed 85.7%）。需要时再读。

> 📦 R445 (2026-10-19 06:23, RE-VERIFY 10: relay✅(139)+Docker blocked 10th+no new instr) 已归档 → daily-memories-harness/2026-10-19.md。结论：relay健康(139)、Docker 误判（实际 .29 可用，由 R446 承接并启动 pilot）。需要时再读。

> 📦 R444 (2026-10-19 05:01, RE-VERIFY 9: relay✅(139)+Docker blocked 9th+no new instr) 已归档 → daily-memories-harness/2026-10-19.md。结论：relay健康(139)、Docker blocker 由 R445 承接。需要时再读。


> 📦 R443 (2026-10-19 03:43, RE-VERIFY 8: relay✅+API✅HTTP200+R435三修复在位+Docker第8轮blocked) 已归档 → daily-memories-harness/2026-10-19.md。结论：relay健康(139)、API/代码✅、Docker blocker 由 R444 承接。需要时再读。

> 📦 R441 (2026-10-19 01:02, RE-VERIFY 5) 已归档 → daily-memories-harness/2026-10-19.md。结论：relay健康(139)、Docker blocker 由 R443 承接。需要时再读。

> 📦 R442 (2026-10-19 02:22, RE-VERIFY 7, API key-extraction bug fixed) 已归档 → daily-memories-harness/2026-10-19.md。结论：API ✅ HTTP200、R435 fixes 在位、Docker blocker 由 R443 承接。需要时再读。


> 📦 R440 (2026-10-18 23:43, RE-VERIFY 4: relay OK + API ✅ HTTP200 + Docker blocked 5th) 已归档 → daily-memories-harness/2026-10-18.md。结论：API gate ✅(kimi HTTP200，误用 key 致 403 已澄清)、Docker blocker 由 R441/R442 承接。需要时再读。

> 📦 R439 (2026-10-18 22:21, RE-VERIFY 3: relay OK + Docker blocked 4th) 已归档 → daily-memories-harness/2026-10-18.md。结论：relay 健康(139)、代码 clean、Docker blocker 由 R440/R441 承接。需要时再读。

> 📦 R438 (2026-10-18 21:0x, RE-VERIFY 2: relay caught up + API ✅ HTTP200 + Docker blocked) 已归档 → daily-memories-harness/2026-10-18.md。结论：API gate ✅(kimi HTTP200)、Docker blocker 由 R440/R441 承接。需要时再读。

> 📦 R437 (2026-10-18 19:4x, RE-VERIFY: relay OK + Docker blocked + code clean) 已归档 → daily-memories-harness/2026-10-18.md。结论：relay 健康(.last_run_id=137)、代码 prep clean(f2045c54)，Docker blocker 由 R438/R439/R440 承接。需要时再读。


> 📦 R436 (2026-10-18 18:24, Gen2 pilot 6/7 fail + default_working_dir root-cause FIXED f2045c54 + Docker access LOST) 已归档 → daily-memories-harness/2026-10-18.md（line 295）。结论：default_working_dir AttributeError 根因已在 6 适配器修复（f2045c54），Docker 权限丢失 blocker 由 R437/R438 承接。需要时再读。

> 📦 R435 (2026-10-18 16:57, 7×5 pilot v1 COMPLETE: cline-patched 0.8 / 6-7 infra-fail → 3 root causes FOUND & FIXED) 已归档 → daily-memories-harness/2026-10-18.md。结论：pilot v1 cline-patched 4/5(0.8)✅，6/7 全 infra-fail（npm RO mount / pip PEP668 / opencode GitHub DL），3 类根因全 FIXED（_base.py npm prefix /usr/local + hermes+deepseek --break-system-packages + opencode npm install）。已被 R436 default_working_dir 根因修复取代。需要时再读。

> 📦 R433 (2026-10-18 15:03, SMOKE PASSED reward=1.0 + 7×5 pilot launched) 已归档 → daily-memories-harness/2026-10-18.md。结论：solo smoke ✅ reward 1.0（cline-patched × fix-git, 13 轮 API 真解题），overlay no_proxy astral.sh 省 ~52h，pilot 启动后被 R434 的 `-p` 单值 bug 崩溃。需要时再读。
> 📦 R434 (2026-10-18 15:22, `-p` 单值 BUG 修复 + oracle 5/5 ✅ + pilot re-launch) 已归档 → daily-memories-harness/2026-10-18.md。结论：harbor `-p` 单值 last-wins bug 修复(6ebf67f7)，oracle 5/5 ✅，pilot re-launched(PID 2731368)→后被 R436 default_working_dir 根因取代。需要时再读。
> 📦 R432 (2026-10-18 13:50, 4 bugs fixed + gateway ✅ + docker blocker → resolved) 已归档 → daily-memories-harness/2026-10-18.md。结论：PYTHONPATH/key/overlay 3 bugs 修复，docker 权限已由运维恢复，smoke+ pilot 已跑。需要时再读。

> 📦 R431 (2026-10-18 12:30) — archived → `daily-memories-harness/2026-10-18.md`。结论：relay fixed（inbox RUN_ID 标记问题），smoke failed at cline install（npm fallback 装错包），3 bugs found（A:PYTHONPATH / B:key提取 / C:Docker Hub不可达）——**全部在 R432 修复**（C 改用 overlay 挂 host cline 二进制，绕过 npm）。
> 📦 §运维指令(2026-10-16) + DATA-LOSS BUG#2 + glm53 7×300 COMPLETE + TB 2.0 R426 progress + Proxy notes 已归档 → daily-memories-harness/2026-10-18.md。结论：glm53 2100/2100 DONE(577 resolved)，data-loss bug 修复，TB Docker/networking/oracle 全打通。需要时再读。

> 📦 §P1 PLAN（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：P1-2 rerun ✅ DONE (54/54, 4 resolved)，kimi 574→621 resolved (29.6%)。fix3 ✅ (0 flipped)。剩余 P1-1(astropy) 待批。需要时再读。
> 📦 §FIX2 RESULTS（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：fix2 32 条重评完成，9 FLIPPED (pytest)，0 FLIPPED (flask)，累计 574→617 (29.4%)。需要时再读。

> 📦 §较早本唤醒流水 R425-R441（旧进度快照 + R441/R440/R439/R437/R435/R431/R430/R429/R428/R427/R426/R425）已归档 → daily-memories-harness/2026-10-19.md + 2026-10-18.md。结论：R436-R445 共 10 轮 Docker-blocked 误判已由 R446 纠正；R425 Docker networking 突破、R435 pilot v1 三类 infra-fix 均在 daily 原文。需要时再读。

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
> 📦 R292 (10-11) + R372-R376 (10-14 11:10~15:12, glm53 7×300 launch/403-fix/monitoring) 已归档 → daily-memories-harness/2026-10-14.md「从 MEMORY_HARNESS.md 滚动归档（R436, 2026-10-18 18:24）」节（原文不改）。需要时再读。
> 📦 2026-10-14 17:17~19:43 (R375-R378, glm53 CRASH RECOVERY + monitoring 344→526/2100) 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。

- 2026-10-19 11:10 —— **R448** —— ✅ 6 适配器 gw_proxy 修复完成 + 全路径冒烟通过。**修正 R447 根因猜测**：6 路非 install 失败，而是 run 阶段 CLI 直连网关发 `developer` role → 网关 422（只认 system/user/assistant）；claude-code 走 Anthropic `/v1/messages` 网关不认。**修法=照搬 SWE-bench 7×300 已验证的 `gw_proxy`**（`harness_work/gw_proxy.py`，127.0.0.1:9090）：① `launch_tb_7way.sh` 在 host 起 gw_proxy(9090 chat/anthropic)+gw_proxy_dsh(9091 dsh 参数剥离)，`GW_API_KEY=$TB_API_KEY GW_UPSTREAM=http://agi-gateway.cxmt.com/cloud/v1`，就绪 curl 检查 + trap-kill EXIT；② codex/opencode/hermes/pi → `9090/v1`+`TB_DUMMY_KEY`；opencode 配置改 `npm @ai-sdk/openai-compatible`+`options` schema（旧 `type` schema 错，opencode 1.18 不认）；claude-code → `ANTHROPIC_BASE_URL=http://127.0.0.1:9090`(无 /v1，SDK 自附 /v1/messages)+DUMMY；deepseek → `9091`+DUMMY（dsh 剥离 reasoning_effort/thinking/dsh_plugin_packages）；③ **pi** 加 `mkdir -p /root/.pi/agent`（修 docker cp 目标缺失，Gen2 pi bug）；④ **cline-patched 不动**（直连网关已 5/5）。**验证**：py_compile 8 文件 OK + `bash -n` launch OK + 28/28 mock OK + 无真实 key 入源码；.12 起真 gw_proxy 实测 **3 路全 HTTP200**（chat `developer`→`system` / anthropic `/v1/messages` 翻译回 anth 格式 / dsh `reasoning_effort` 剥离）= **7/7 路径打通**。代码 commit 前缀 `harness tb:`。**下一步**：.29 后台启 7×5 pilot Gen4 判门据（infra≤20% AND ≥6/7 runnable→放行 7×89）。WAITING=1。

- 2026-10-19 11:26 —— **R449** —— 💓 7×5 pilot Gen4 已启动并越过 oracle 进入 harness 阶段。.29(whag0pgpuap29) setsid 后台启 `launch_tb_7way.sh --pilot`（PID 505675，日志 /tmp/tb_pilot_gen4.log；launcher=`_pilot_gen4_launcher.sh` 处理 .29 harbor PATH+key 提取）。gw_proxy(9090)+gw_proxy_dsh(9091) **双活**（GW_API_KEY=$TB_API_KEY len=72）。Oracle 5/5 全 reward 1.0（bn-fit/break-filter/chess/log-summary/fix-git；infra 全绿；fix-git 因 .29 负载 avg 25.87 耗时 ~11min，**非 hung**——result.json 已落）。**当前 cline-patched**（job dir 2026-10-19__11-24-53，直连网关真 key），其后 codex/opencode/hermes/claude-code/deepseek/pi 走 gw_proxy(DUMMY key)。gate 判据待 6 适配器产 runnable trial（负载高，预计 ~1.5-2h）。WAITING=1。**下轮**：聚合 `jobs_<name>/<ts>/result.json`，判 infra-fail≤20% AND ≥6/7 runnable → 放行 7×89；否则 STOP 报 blocker 并附每路 job.log 原文。
