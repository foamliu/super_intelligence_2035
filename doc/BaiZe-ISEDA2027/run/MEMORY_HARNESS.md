# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

> 🔧 **运维指令（2026-10-14 · 最高优先 · 每轮唤醒必读）**：
> **🆕 2026-10-14 glm53 7×300 任务**：**✅ RESTARTED 17:17 — 全部 7 路已重启，无 403**。发现 17:11 所有 7 路进程 + glm53 proxies (9092/9093) 均已死亡（死因不明，非 OOM，log 无 error，可能 ~16:47 后崩溃）。curl /v1 → 200 ✅。已重启 gw_proxy 9092 + gw_proxy_dsh 9093（均 → `/v1`），再 `setsid` 重启 7 路 `--resume`。Base URL 全部 `/v1`（非 `/cloud/v1`）✅。
> **P1-2 rerun** ✅ DONE：rerun_blocked.py 54/54 完成（4 resolved, 42 pbf, 8 blocked）。累计 kimi 574→621 resolved (29.6%)。
> **glm53 7×300** 🔄：7 路运行中（17:17 重启，--resume 跳过已完成）。**344/2100 entries (16.4%), 86 resolved (25.0%), 257 pbf, 1 quota-blocked**。Per-harness: codex 116(33, 28.4%), deepseek 154(26, 16.9%, 1qb), claude-code 22(9, 40.9%), hermes 17(7, 41.2%), opencode 15(6, 40.0%), pi 13(5, 38.5%), cline-patched 7(0, 0.0%)。**glm53 25.0% vs kimi 27.3%**（原口径 574/2100）→ 略低，344 条样本尚小。Pending: 1756/2100。ETA ~30h（从重启算）。load 27.3, RAM 1889G avail, /dev/shm 984G free。

## §P1 PLAN — 等运维确认（2026-10-13 06:11 报出 · 指令④要求「做法/成本/ETA/占用」）

> **数据基础**（从 `kimi_pilot_results.json` 2100 条 + `fix1.json` 376 条实测）：
> - blocked: 50（matplotlib 31, django 10, sympy 6, sklearn 2, pytest 1；claude-code 15, hermes 15, deepseek 11, pi 5, codex 4）
> - quota-blocked: 14（全 django__django-16873，API 配额问题，非 infra）
> - no-patch: 4（全 deepseek，timeout）
> - astropy patch-not-applied: 28/42（eval env 失败，未纳入 fix1 的 5 repo 范围）
> - fix1 后仍 patch-not-applied: 97（mpl 30, sklearn 27, pytest 18, flask 14, sphinx 8）
> - **97 条根因已查清（§7）**：py_version_36_needs_38=42(pytest/sklearn/sphinx) · py_version_38_needs_39=30(全 matplotlib) · werkzeug_version=14(全 flask) · other=11
> - **新增 P1-1b**：per-repo Python 版本 conda env（3.8 for pytest/sklearn/sphinx, 3.9 for matplotlib）+ werkzeug 兼容版本预装 → 可修 86/97 条

| P1 项 | 做法 | 成本 | ETA | 占用 | 预估挽回 | 风险 |
|:--|:--|:--|:--|:--|:--|:--|
| **P1-1 astropy** | 预编译 astropy wheel（`pip wheel astropy`）+ 注入 `~/.cache/pip`；或增大 eval 沙箱 memory limit（cgroup）| ~4h | 批准后 4h | CPU+磁盘（编译 ~2GB），无 GPU | ~28 patch-apply 新增（resolved 数取决于 patch 质量）| 中：astropy C 扩展编译依赖多 |
| **P1-2 网络 503** | ① git fetch 加 3 次重试+指数退避 ② 预克隆 5 高频 repo 到本地缓存（`/dev/shm/repos/`），harness 从本地 clone | ~1h | 批准后 1h | CPU+磁盘（预克隆 ~5GB），无 GPU | 50 blocked → 可重跑 | 低：改 `run_serial_kimi.py` git 逻辑 |
| **P1-3 Docker** | per-instance 预构建 Docker（官方做法）| ~2-3 天 | 2-3 天 | 重 CPU+大量磁盘+Docker | 理论上覆盖全部 env 失败 | 🔴 **不可行**：本机 `docker info`→NOT AVAILABLE，内网无法 `docker pull`。**建议暂缓** |
| **②b 重跑 agent** | blocked(50)+no-patch(4)=54 条重跑 harness（同 7 harness+kimi-k2.6-cloud）；quota-blocked(14) 不重跑 | ~1h(并行)~5.4h(串行) | P1-2 后 ~1h | CPU+API 配额，无 GPU | 50 blocked → 重跑后估 ~5-10 resolved | 低：已验证流程 |

> **建议优先级**：P1-2（~1h, 低风险）→ ②b 重跑（~1h）→ P1-1（~4h）→ P1-3 暂缓。**等运维确认后执行**。

## §FIX2 RESULTS — P1-1b fix2 重评完成（2026-10-13 13:00 · 本轮完成）

> **fix2 重评 32 条（pytest 18 + flask 14）全部完成** ✅（5.6min total）。
> **修复措施**：pytest `pip install 'setuptools<70'` + flask `pip install 'werkzeug<2.3'`（均用现有 testbed env，无需 C 重建）。
>
> **pytest (18 条)**：**9 FLIPPED to RESOLVED** ✅ · 15/18 patch-applied（从 0/18！）· 3.6min
> - pytest-5227：7/7 harness 全部 RESOLVED（codex/pi/opencode/cline-patched/deepseek/claude-code/hermes）
> - pytest-5103：2/2 RESOLVED（pi/opencode）
> - pytest-5221：6/6 patch-applied 但 f2p=0/2（全未通过 — patch 全错，agent 能力限制）
> - pytest-11143/11148：3 条 patch 仍未 apply（pi 的 patch 有兼容性问题）
>
> **flask (14 条)**：**0 FLIPPED** · 13/14 patch-applied（从 0/14！）· 2.0min
> - flask-4045：7/7 patch-applied，f2p=1/2（1/2 fail-to-pass 通过 — patch 部分正确但不完整）
> - flask-4992：6/7 patch-applied，f2p=0/1（全未通过 — patch 质量限制）
> - 1 条未 apply：opencode/flask-4992
>
> **累计（fix1+fix2）**：574→617 resolved（27.3%→29.4%, +2.1pp）· +243 patch-applied
> **剩余 65 条 not-applied**：matplotlib 30（需 qhull+freetype build deps ~2h）· sklearn 27（需 build deps ~2h）· sphinx 8（待排查）
> **r1_eval.py fix2b**：`conda activate {env}` → `export PATH={env_path}/bin:$PATH`（chroot 内 conda activate 修复，正确保留）

**下一步建议**：① matplotlib+sklearn 需额外 ~4h 安装 build deps + 重建 C 扩展（65 条中 57 条）② sphinx 8 条逐条排查 ③ **等运维确认后执行**

## 📊 进度快照

```
PHASE:        glm53 7x300 RUNNING (169/2100, 61 resolved, /v1 endpoint) + P1-2 rerun RUNNING (~34/54)
已完成:       ① 7x300 kimi COMPLETE (2100/2100, 574 resolved) · ② eval rootcause ✅ · ③ EDA ✅ · ④ P0 fixes ✅ · ⑤ fix1 ✅ (34 flipped) · ⑥ fix2 ✅ (9 flipped) · ⑦ fix3 ✅ (0 flipped) · ⑧ fix4 ✅ (0 flipped) · ⑨ why-low-passrate ✅ · ⑩ glm53 403 fix ✅ + 7x300 LAUNCHED ✅ + run_harness.py /v1 fix ✅
当前动作:     glm53 7x300 RUNNING (7 harness × 300, started 11:10 CST, ~2h elapsed) — 169/2100 entries, 61 resolved, 108 pbf, 0 blocked/no-patch. Per-harness: cline-patched 45(20, 44.4%), codex 44(21, 47.7%), deepseek 53(19, 35.8%), claude-code 8(0), hermes 7(1), opencode 7(0), pi 5(0). curl /v1 → 200 ✅ (re-verified). P1-2 rerun 34/54 (4 resolved, PID 3541239) in background.
下一步:       ① Monitor glm53 7x300 progress (ETA ~22h remaining) ② P1-2 rerun completion + merge ③ When glm53 done: generate report_harness_glm53_vs_kimi_7x300.html ④ Restore kimi configs after glm53 run
阻塞:         <无> — base URL 全部 /v1, curl 200 OK, 7 路正常运行, 无 403/quota/timeout
ERROR_COUNT:  0
```

**本唤醒流水**：
> 📦 R366 (2026-10-14 06:50, report updated + preclone killed + rerun monitoring) 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
- [08:54] R369: rerun monitoring (13/54, 1 resolved) + report update. 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
- [09:40] R370: matplotlib preclone v2 + report update (15/54). 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
> 📦 R371-R372 (2026-10-14, glm53 403 resolved + early monitoring 23/2100) 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
- [12:40] R373: **glm53 7×300 monitoring + run_harness.py /v1 fix + curl re-verify**. curl POST `http://agi-gateway.cxmt.com/v1/chat/completions` (model=glm-5.3-flash) → **200 OK** ✅ (re-verified this round). **101/2100 entries** in `glm53_pilot_results.json`: 32 resolved, 69 pbf, 0 blocked/no-patch. Per-harness: cline-patched 29(11 resolved, 37.9%), codex 27(11, 40.7%), deepseek 31(10, 32.3%), claude-code 5(0), hermes/opencode/pi 3 each(0). Early django resolve rates notably higher than kimi (cline 37.9% vs 28.7%, codex 40.7% vs 26.7%). **Fixed `run_harness.py:36`**: GATEWAY default `/cloud/v1` → `/v1` (was the last stale /cloud/v1 in active code; not used in actual driver flow but updated per directive "三文件全更新"). All `/cloud/v1` references now only in comments/migration logic. 7 `run_serial_kimi.py --resume` processes running (PIDs 1262875~1278074, etimes ~4800s/~80min). gw_proxy 9092/9093 → `/v1` upstream. P1-2 rerun: 22/54 (3 resolved, PID 3541239). 📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈32400B(31.6KB ✓) / 归档 0B。
- [13:04] R374: **glm53 7×300 monitoring + curl re-verify**. curl POST `http://agi-gateway.cxmt.com/v1/chat/completions` (model=glm-5.3-flash) → **200 OK** ✅. **169/2100 entries**: 61 resolved, 108 pbf, 0 blocked/no-patch. Per-harness: cline-patched 45(20, 44.4%), codex 44(21, 47.7%), deepseek 53(19, 35.8%), claude-code 8(0), hermes 7(1), opencode 7(0), pi 5(0). All 7 `run_serial_kimi.py --resume` alive (etimes ~6760s/~1.9h). glm53 resolve rate consistently above kimi (cline 44.4% vs 28.7%, codex 47.7% vs 26.7%). P1-2 rerun: 34/54 (4 resolved, 21 pbf, 8 blocked, PID 3541239). No 403/quota/timeout. 📦 体积：TASK=28709B(28.0KB ✓) / MEMORY≈32600B(31.8KB ✓) / 归档 0B。
> 📦 R358-R365 (2026-10-13 22:15 ~ 2026-10-14 06:15, why-low report + fix4 + preclone + rerun launch) 已归档 → daily-memories-harness/2026-10-14.md。需要时再读。
> 📦 R352 (2026-10-13 07:41, report finalized + 97 not-applied root cause) 已归档 → daily-memories-harness/2026-10-13.md。需要时再读。
> 📦 R353-R354 (2026-10-13 08:19~08:57, monitoring wakes, fix1 re-verified, waiting for P1) 已归档 → daily-memories-harness/2026-10-13.md。
> 📦 R355 (2026-10-13 12:21, fix2 feasibility test analysis) 已归档 → daily-memories-harness/2026-10-13.md。
- [14:30] R357: **fix3 launched** 🔄. Root cause: pkg-config `.pc` files in testbed_py39/testbed_py38 had full host paths (`/nas_train/.../rootfs/.../opt/miniconda3/...`) as prefix → chroot sandbox can't find qhull/freetype headers. Fix: (1) `sed` all `.pc` files to chroot-internal paths (`/opt/miniconda3/envs/testbed_py39`) (2) `r1_eval.py`: inject `CFLAGS`/`CPPFLAGS`/`LDFLAGS`/`PKG_CONFIG_PATH`/`C_INCLUDE_PATH`/`CPLUS_INCLUDE_PATH` when `env_override` set (3) add `--no-build-isolation` to `pip install -e .`. Test: matplotlib 1 entry → `patch_applied: false→true` ✅ (78s/entry). Full 64-entry run launched (PID 2127908, `--resume`). 📦 体积：TASK=34786B(34.0KB ⚠️) / MEMORY=27552B(26.9KB ✓).
> 📦 R344-R349 (2026-10-13 01:25~04:58, fix1 re-eval launch→90% monitoring, 3→30 FLIPPED, 57→188 patch-applied) 已归档 → daily-memories-harness/2026-10-13.md。需要时再读。
> 📦 R342 (2026-10-12 23:15, eval rootcause report delivery) 已归档 → daily-memories-harness/2026-10-12.md。结论：report_harness_eval_rootcause.html (45612B, 6 sections, 3 SVG) delivered ✅。需要时再读。
> 📦 R337-R341 (2026-10-12 18:18~21:08, monitoring wakes) 已归档 → daily-memories-harness/2026-10-12.md。需要时再读。
> 📦 R326-R330 (2026-10-12 10:30~13:48, Report A/B refresh + cline vs opencode EDA report delivery + re-verification) 已归档 → daily-memories-harness/2026-10-12.md。需要时再读。
> 📦 R302-R321 (2026-10-11~12, 两份报告交付 + 7×300 monitoring 97.5%→99.3%) 已归档 → daily-memories-harness/2026-10-11.md + 2026-10-12.md。需要时再读。
> 📦 R322-R325 (2026-10-12 08:00~09:45, 7×300 monitoring 99.4%→99.7%, 567→571 resolved, hermes 288→294/300, Report B 刷新 2094 entries) 已归档 → daily-memories-harness/2026-10-12.md。需要时再读。

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
