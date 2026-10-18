# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

> 🆕 **R432 (2026-10-18 13:50) — 4 BUGS FIXED + GATEWAY ✅ + 🔴 DOCKER BLOCKER (需 root)**：
> **代码修复（无需 docker，全部验证通过，bash -n + pyyaml safe_load ✅）**：
>   - **bug-A (PYTHONPATH)** ✅ FIXED：`launch_tb_7way.sh` 行 30 加 `export PYTHONPATH="${SCRIPT_DIR}/..:${PYTHONPATH:-}"`。验证：harbor venv python `import terminalbench.agents.cline_patched` → `import OK: cline-patched`。
>   - **bug-B (key 提取)** ✅ FIXED：改为 `grep -A2 'kimi-k2.6-cloud' keys.txt | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]'`。验证：72 字符 key（`02_088EE...9a9f`）。
>   - **bug-C/overlay** ✅ FIXED：新建稳定 overlay `harness/terminalbench/overlay-network-host.yml`（挂载 `/opt/node` + `/opt/cline-modules`，含 npm mirror+proxy）；launch 默认指向它（不再用 /tmp volatile `minimal2.yml`）。cline fast-path（`cline_patched.py` 行 93-115）将触发——host cline = 132MB standalone ELF（`@cline/cli-linux-x64/bin/cline`，v3.0.72），ldd 仅需 glibc，容器内可直跑，**无需 npm install**。
>   - **task dir** ✅：`~/terminal-bench` → `/tmp/terminal-bench-repo/original-tasks` symlink（226 任务目录，5 pilot 全在）。
> **网关验证** ✅ NOT blocker：`curl /v1/models` → HTTP 200；`curl /v1/chat/completions`（kimi-k2.6-cloud, max_tokens=5）→ HTTP 200，model=`kimi-k2.6`，0.75s。
> **🔴 DOCKER BLOCKER（需 root/运维）**：`docker info` → permission denied（docker socket `/var/run/docker.sock`）。根因：docker 组被重建（旧 gid 122→`_lldpd`，docker 现 gid 123，**零成员**）。`sg docker -c 'docker info'` → "Invalid password"（非成员且无密码）。无 passwordless sudo，无 setuid docker。**.29 上无任何进程有 docker 访问权**（已查 `/proc/*/status` Groups，无 gid 123）。**已试命令（全失败）**：`docker info`、`docker images`、`sg docker -c 'docker info'`、`sudo -n docker info`。**修复方案**：需 root 执行 `sudo usermod -aG docker app.e0031982`（或 `sudo gpasswd -a app.e0031982 docker`）→ `newgrp docker` 或重新登录 → 即可跑 smoke。**smoke / pilot / full 全部阻塞于此**。
> **Next（docker 恢复后）**：① solo smoke（cline-patched × fix-git）→ ② 7×5 pilot → ③ gate（infra ≤20%, ≥6 runnable）→ ④ 7×89 full（623 trials 或以实际 226 任务为准）。

> 📦 R431 (2026-10-18 12:30) — archived → `daily-memories-harness/2026-10-18.md`。结论：relay fixed（inbox RUN_ID 标记问题），smoke failed at cline install（npm fallback 装错包），3 bugs found（A:PYTHONPATH / B:key提取 / C:Docker Hub不可达）——**全部在 R432 修复**（C 改用 overlay 挂 host cline 二进制，绕过 npm）。
> 🔧 **运维指令（2026-10-16 · 最高优先 · 每轮唤醒必读）**：
> **🆕 2026-10-16 重启补完 188 条**：用 `--resume` 重启未跑完的 4 路（opencode/cline/claude/pi）。
> **🔴 DATA-LOSS BUG #2 FIXED (2026-10-17 01:30)**：`load_results()` 在 JSON parse error 时**重命名**损坏文件 → `save_results()` 读到空文件 → 仅写当前 harness → **丢失 3 个 DONE harness 数据**（codex/deepseek/hermes 共 900 条）。根因=load_results 和 save_results **双重读取**：load_results 先 rename，save_results 找不到文件→current=[]。已从 `.corrupt` 备份恢复 1994 条 + 合并当前 1110 条 = **2011 条**。修复：① `load_results` **不再 rename**（留文件在原位）② `save_results` 改为**容错解析+恢复写入**（raw_decode salvage → merge → write）。
> **glm53 7×300** ✅ **COMPLETE (R423, 14:45)**：**全部 7 路 DONE ✅ 2100/2100**（codex 80 · deepseek 71 · hermes 81 · opencode 87 · claude-code 80 · cline-patched 86 · pi 92）。**577 resolved (27.5%)** vs kimi 574/2100 (27.3%)。McNemar: 2093/2100 agree(99.7%), b=2 c=5, p=0.453 → **换 backbone 无显著提升**。报告 `report_harness_glm53_7x300_zh.html` 已出最终版（pending=0）。pi PID 1195199 已完成 300/300（django-16873 标记 quota-blocked）。
> **TB 2.0 PROGRESS（R426, 21:12 — Codex pilot ✅ API working, task timeout）**：① Docker ✅ ② Dataset ✅ (89 tasks) ③ Oracle 1-task ✅ reward 1.0 ④ Docker networking ✅ (host net + aliyun mirror + uv mount) ⑤ **Codex 1-task pilot COMPLETE** — codex 0.94.0 + `wire_api="chat"` config → **Chat Completions API works through gw_proxy!** Agent executed ~44 commands, created todo list, problem-solved R installation. **Timed out after 900s** (AgentTimeoutError, reward 0.0) because R installation was blocked by conflicting Debian/Ubuntu apt sources in container. **Key: API issue SOLVED, timeout is task-specific.** ⑥ apt .deb corruption FIXED (HTTP sources + `Verify-Peer "false"` + `Install-Recommends "false"`) ⑦ NVM mirror ✅ (aliyun), Tencent npm mirror ✅ ⑧ codex.py fully patched (NVM mirror + curl -k + npm registry/strict_ssl + ca_certificates) ⑨ eve.py patched (NVM mirror). **Next: check other 6 agents' install requirements, run 7×5 pilot.**
> **Proxy notes**: MITM proxy at 172.19.92.25:13128. HTTP **blocks** archive.ubuntu.com + deb.debian.org (302→disable.htm). HTTPS pypi.org → tls handshake eof. BUT mirrors.aliyun.com HTTP (apt) + HTTPS (pip/uv) **both work**. Docker daemon proxy in `/etc/docker/daemon.json` ✅, image pulls work ✅. Host uv 0.8.13 at `/usr/local/bin/uv`, Python 3.13.7 at `~/.local/share/uv/python/`.
> **P1-2 rerun** ✅ DONE：kimi 574→621 resolved (29.6%)。

> 📦 §P1 PLAN（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：P1-2 rerun ✅ DONE (54/54, 4 resolved)，kimi 574→621 resolved (29.6%)。fix3 ✅ (0 flipped)。剩余 P1-1(astropy) 待批。需要时再读。
> 📦 §FIX2 RESULTS（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：fix2 32 条重评完成，9 FLIPPED (pytest)，0 FLIPPED (flask)，累计 574→617 (29.4%)。需要时再读。

## 📊 进度快照

```
PHASE:        TB T2 SOLO SMOKE FAILED at cline install (smoke #3 done, 2m24s) · ops relay fixed · cline-install 路径需重做
已完成:       ①-㉘ same · ㉙ Oracle 5/5 ✅ · ㉛ 7 adapters + mock 28/28 · ㉜ launch script (local -p) · ㉝ R431: ops relay fixed (inbox marker 122→123, commit eb204521) + stray .12 relay killed + 123 ran ✅ · ㉞ TB solo smoke ran 2m24s → FAILED at cline install (npm fallback targets non-existent pkg; fast-path embedded-bun binary absent)
当前动作:     R431 (12:45): smoke 诊断完成。cline install 路径根本性破损——本机 cline=bun 源码构建(非 npm 包)，fast-path 期望的嵌入式 bun 二进制不存在 → npm fallback 装错包 fail。node fast-path/env 容器/镜像缓存均 ✅。
下一步:       ① 修 cline install：本机 bun --compile 构建独立二进制(或 dist/index.js+bun) + overlay 挂载 cline 源码/bun + 改 cline_patched fast-path 路径 ② 重跑 smoke(cline-patched × fix-git) ③ 修 launch_tb_7way.sh bug-A(PYTHONPATH)+bug-B(key) ④ 解 bug-C(未缓存镜像拉取) ⑤ smoke pass → 7×5 pilot
阻塞:         cline install 路径破损(smoke fail 根因，pilot 前必修) · bug-C Docker Hub 不可达(未缓存镜像) · bug-A/B launch script。其余无。
ERROR_COUNT:  0
```

**本唤醒流水**：
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
