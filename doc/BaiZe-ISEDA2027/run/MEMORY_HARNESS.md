# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

> 🔧 **运维指令（2026-10-14 · 最高优先 · 每轮唤醒必读）**：
> **🆕 2026-10-14→15 glm53 7×300 任务**：**✅ codex+deepseek DONE(300/300 each) + 5 路运行中（~9h elapsed, 无 403/无崩溃）**。Base URL 全部 `/v1`（非 `/cloud/v1`）✅。curl /v1 → 200 ✅（02:17 复验, 0.25s）。
> **P1-2 rerun** ✅ DONE：rerun_blocked.py 54/54 完成（4 resolved, 42 pbf, 8 blocked）。累计 kimi 574→621 resolved (29.6%)。
> **glm53 7×300** 🔄：codex 300/300 DONE(81,27.0%) + deepseek 300/300 DONE(71,23.7%) + 5 路运行中。**908/2100 entries (43.2%), 281 resolved (30.9%), 624 pbf, 4 quota-blocked**。Per-harness: codex 300(81,27.0% DONE), deepseek 300(71,23.7% DONE), hermes 73(29,39.7%), opencode 73(28,38.4%), claude-code 58(25,43.1%), cline-patched 57(23,40.4%), pi 47(24,51.1%)。**🔑 关键发现（interim n=908）：glm53 30.9% ≈ kimi 30.9%，McNemar b=0/c=1, chi2=1.0 (p>>0.05) → 两模型在相同实例上几乎完全一致（907/908=99.9% 一致）**。Pending: 1192/2100。ETA ~33h（5 路并行 ~36/h）。load 25.5, RAM 1.9T, /dev/shm 986G。

> 📦 §P1 PLAN（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：P1-2 rerun ✅ DONE (54/54, 4 resolved)，kimi 574→621 resolved (29.6%)。fix3 ✅ (0 flipped)。剩余 P1-1(astropy) 待批。需要时再读。
> 📦 §FIX2 RESULTS（2026-10-13）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：fix2 32 条重评完成，9 FLIPPED (pytest)，0 FLIPPED (flask)，累计 574→617 (29.4%)。需要时再读。

## 📊 进度快照

```
PHASE:        glm53 7x300 RUNNING (908/2100, 281 resolved, codex+deepseek DONE) + P1-2 rerun DONE (54/54)
已完成:       ① 7x300 kimi COMPLETE (2100/2100, 574→621 resolved) · ② eval rootcause ✅ · ③ EDA ✅ · ④ P0 fixes ✅ · ⑤ fix1 ✅ (34 flipped) · ⑥ fix2 ✅ (9 flipped) · ⑦ fix3 ✅ (0 flipped) · ⑧ fix4 ✅ (0 flipped) · ⑨ why-low-passrate ✅ · ⑩ glm53 403 fix ✅ + 7x300 RUNNING ✅ + run_harness.py /v1 fix ✅ · ⑪ P1-2 rerun ✅ (54/54, 4 resolved) · ⑫ interim glm53 vs kimi comparison ✅ (908 overlap, McNemar b=0/c=1, chi2=1.0, 907/908=99.9% agreement)
当前动作:     glm53 7x300 RUNNING (5 harness active + codex DONE + deepseek DONE, ~9h elapsed) — 908/2100 entries (43.2%), 281 resolved (30.9%), 624 pbf, 4 quota-blocked. Per-harness: codex 300(81,27.0% DONE), deepseek 300(71,23.7% DONE), hermes 73(29,39.7%), opencode 73(28,38.4%), claude-code 58(25,43.1%), cline-patched 57(23,40.4%), pi 47(24,51.1%). curl /v1 → 200 ✅ (02:17, 0.25s). 5 PIDs alive (etimes ~32400s ~9h, ppid=1, stat=SNs). Interim (n=908 overlap): glm53 281(30.9%) vs kimi 281(30.9%), both=281, b=0, c=1 → McNemar chi2=1.0, p>>0.05, 907/908=99.9% agreement. Only diff: 1 kimi-only instance.
下一步:       ① Continue monitoring glm53 7x300 (ETA ~33h, 1192 remaining at ~36/h) ② When glm53 done: generate report_harness_glm53_vs_kimi_7x300.html (full comparison) ③ Restore kimi configs after glm53 run
阻塞:         <无> — base URL 全部 /v1, curl 200 OK, 5 路正常运行 + codex+deepseek done, 4 quota-blocked
ERROR_COUNT:  0
```

**本唤醒流水**：
> 📦 R366-R385 (2026-10-14, ~20 rounds of glm53 monitoring 23→872 + rerun + fixes) 已归档 → daily-memories-harness/2026-10-14.md + 2026-10-15.md。需要时再读。
> 📦 R386 (2026-10-15 01:08, glm53 monitoring 872/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
> 📦 R387 (2026-10-15 01:42, glm53 monitoring 887/2100) 已归档 → daily-memories-harness/2026-10-15.md。需要时再读。
- [02:17] R388: glm53 7×300 monitoring — **908/2100 (43.2%), 281 resolved (30.9%), 624 pbf, 4 qb**. codex 300/300 DONE(81,27.0%), deepseek 300/300 DONE(71,23.7%). 5 harnesses active (PIDs 3023384/3032805/3033846/3033868/3034548, etimes ~32400s ~9h, ppid=1, stat=SNs). **🔑 Interim (n=908 overlap)**: glm53 281(30.9%) vs kimi 281(30.9%), both=281, b=0(glm53-only), c=1(kimi-only) → McNemar chi2=1.0, p>>0.05, **907/908=99.9% agreement** — models nearly identical. Only diff: 1 kimi-only instance (was pi glm53 21 vs kimi 22 at R387, now glm53 24 vs kimi 25 for pi → the 1 discordant pair shifted). Per-harness: pi 51.1%, claude-code 43.1%, cline-patched 40.4%, hermes 39.7%, opencode 38.4%, codex 27.0%, deepseek 23.7%. curl /v1→200 ✅ (02:17, 0.25s). +21 entries since R387 (01:42). Remaining 1192, ETA ~33h (~36/h). load 25.5, RAM 1.9T. 📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈28.1KB(27.4KB ✓) / 归档 0B.
> 📦 R352-R385 (2026-10-13~14, 34 rounds of monitoring/fixes/reports) 已归档 → daily-memories-harness/2026-10-13.md + 2026-10-14.md + 2026-10-15.md。需要时再读。

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
- 2026-10-14 17:17 —— **glm53 7×300 CRASH RECOVERY + RESTART** —— 17:11 发现所有 7 路 harness 进程 + glm53 proxies (9092/9093) 全部死亡（dmesg 无 OOM，log 无 error msg，results file 最后修改 16:47→进程 ~16:47-17:11 间崩溃）。curl /v1 → 200 ✅（API 仍可用）。**修复**：① 重启 gw_proxy 9092 (PID 2941134) + gw_proxy_dsh 9093 (PID 2941137)，均 → `http://agi-gateway.cxmt.com/v1`；② 写 `restart_glm53_harnesses.sh`（`setsid nice -n 10` + `--resume`）；③ 重启 7 路（PIDs 3023384~3034548，ppid=1，stat=SNs）。Resume 验证：cline-patched skip 7, codex skip 116, deepseek skip 153, hermes skip 17, opencode skip 15, claude-code skip 22, pi skip 13 = 343 skip total。**344/2100 (16.4%), 86 resolved (25.0%), 257 pbf, 1 qb**。所有 log 显示 [RUN] 正常，无 403 ✅。codex+deepseek 仍遇 django-16873 quota-blocked（已知问题）。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY=30852B(30.1KB ✓) / 归档 0B。
- 2026-10-14 18:30 —— **glm53 7×300 monitoring R376** —— ALL 7 alive (etimes ~4280s = ~71min since 17:17 restart, ppid=1, stat=SNs)。curl /v1 → 200 ✅。**430/2100 (20.5%), 105 resolved (24.4%), 323 pbf, 2 qb**。Per-harness: deepseek 192(31,16.1%,1qb) / codex 141(33,23.4%,1qb) / claude-code 25(10,40.0%) / hermes 21(9,42.9%) / opencode 20(8,40.0%) / pi 15(7,46.7%) / cline-patched 16(7,43.8%)。全 7 路 log 活跃（proc fd 确认 [RUN]/[EVAL] 正常），无 403 ✅。gw_proxy_glm53.log 有 ConnectionResetError（客户端断连，proxy 仍存活 PID 2941134/2941137）。**glm53 24.4% vs kimi 27.3%**（原口径 574/2100）→ 略低，但 codex/deepseek 已跑较多且 passrate 偏低（16-23%），小样本 harness（pi/hermes/claude-code/cline-patched）passrate 偏高（40-47%），需等更多样本收敛。+87 entries in 73min = ~1.2/min, ETA ~23h。load 30.2, RAM 1874G, /dev/shm 984G。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈32700B(31.9KB ✓) / 归档 0B。
- 2026-10-14 19:03 —— **glm53 7×300 monitoring R377 + archival** —— ALL 7 alive (etimes ~6360s = ~106min since 17:17 restart, ppid=1, stat=SNs)。curl /v1 → 200 ✅ (19:03 re-verified)。**466/2100 (22.2%), 117 resolved (25.1%), 347 pbf, 2 qb**。Per-harness: deepseek 206(38,18.4%,1qb) / codex 151(34,22.5%,1qb) / claude-code 26(10,38.5%) / hermes 23(9,39.1%) / opencode 22(8,36.4%) / pi 19(9,47.4%) / cline-patched 19(9,47.4%)。无 403 ✅。**glm53 25.1% vs kimi 27.3%**（原口径 574/2100）→ 略低，但 codex/deepseek 已跑 151+206 条且 passrate 偏低(18-23%)拉低整体，小样本 harness（pi/hermes/claude-code/cline-patched ~19-26 条）passrate 偏高(38-47%)，需等更多样本收敛。+36 entries in 33min = ~1.1/min, ETA ~25h。load 30.0, RAM 1871G, /dev/shm 984G。**本轮归档**：§P1 PLAN + §FIX2 RESULTS → ARCHIVE_OPERATOR_HARNESS.md；R373-R375 + R357 → daily-memories-harness/2026-10-14.md。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈27123B(26.5KB ✓) / 归档 ~6557B → ARCHIVE_OPERATOR_HARNESS.md。
- 2026-10-14 19:43 —— **glm53 7×300 monitoring R378** —— ALL 7 alive (etimes ~8730s = ~2.4h since 17:17 restart, ppid=1)。curl /v1 → 200 ✅ (19:43 re-verified)。**526/2100 (25.0%), 128 resolved (24.3%), 396 pbf, 2 qb**。Per-harness: deepseek 232(42,18.1%,1qb) / codex 168(39,23.2%,1qb) / claude-code 30(10,33.3%) / hermes 28(9,32.1%) / opencode 26(8,30.8%) / pi 21(10,47.6%) / cline-patched 21(10,47.6%)。无 403 ✅。+60 entries since 19:03 (~1.5/min)。**glm53 24.3% vs kimi 27.3%**（原口径 574/2100）→ 略低，codex/deepseek 已跑 168+232 条且 passrate 偏低(18-23%)拉低整体，小样本 harness passrate 偏高(33-48%)，需等更多样本收敛。deepseek ETA ~2h, codex ~6h, 慢 harness (cline-patched/pi) ~48h → 整体 ETA ~30h。load 31.6, RAM 1.8T, /dev/shm 984G。📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈28200B(27.5KB ✓) / 归档 0B。
