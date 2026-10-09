# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A ROUND-2 7×100 BLOCKED RE-RUN (Phase 1 non-sympy: pi [4/19] RUNNING; Phase 3 sympy=44 pending after pi)
已完成:       R216 SWEBENCH_COMPARE refreshed (57995B, 700/700, 218 resolved) · hermes 100/100 DONE ✅ · opencode 100/100 DONE ✅ · dsh Phase 1 DONE · cline Phase 1 DONE · claude-code Phase 1 DONE · 口径与并发 section ✅ · trace report in doc root ✅ · H-B 7-way/3-way · 7×30 R1 COMPLETE
当前动作:     R216: Phase 1 non-sympy re-run — pi on [4/19] django-11964 (PID 1370421, running, etimes~1884s). Hermes FINISHED (100/100, 36 resolved, sympy-15346 resolved). DSH Phase 1 DONE (25/94=26.6%, 6 sympy blocked remain). 61 blocked remaining (down from 64). SWEBENCH_COMPARE.html refreshed (57995B, 700/700, 218 resolved). In-scope scored rates: pi 39.4%(71) > codex 37.4%(91) > hermes 36.0%(100) > opencode 35.0%(100) > cline 33.7%(95) > claude-code 30.7%(88) > dsh 26.6%(94).
下一步:       ① pi Phase 1 finishes (~15 rem non-sympy, ~2.5h) → Phase 2 (hermes done, instant) → Phase 3 sympy=44 serial (claude-code 12 + cline 5 + codex 9 + dsh 6 + pi 12) → ~7.3h → final ~00:00 Oct 10. ② After all 61 re-run: refresh SWEBENCH_COMPARE.html → final 7×100 table. ③ Final report with complete data.
阻塞:         <无>
ERROR_COUNT:  0
```

## ⚠️ 口径与并发 (Caliber & Concurrency Disclosure) — 2026-10-08⑦ 要求

> **运维指令 2026-10-08⑦ 追认了并发变更（serial=1→7路并行），但要求显式披露口径。**

| 维度 | Round-1 (30 条) | Round-2 (70 条新题) |
|:--|:--|:--|
| **并发** | **串行 (concurrency=1)** | **7 harness 全并行**（每个内部串行，7 个同时跑） |
| **运行条件** | 无网关争用 | 7 harness 同时竞争网关配额/沙箱/I/O |
| **--resume** | R2 复用 R1 的 30 条串行结果（不重跑） | 仅 70 条新题在 R2 并行条件下评测 |
| **可比性** | ⚠️ **跨轮不可严格比**：同一张 7×100 表混了两种运行条件 | |

**关键事实**：
1. **30 条 R1 实例 = `--resume` 复用的首轮串行结果**；**70 条新题 = 本轮并行结果** → SWEBENCH_COMPARE.html 每行标注 `R1复用` / `R2新跑`。
2. **codex 特例**：codex 在 R1 跑了 300 条超集（串行），其中 70 条与本轮 100-set 重叠 → codex 的 70 条"新跑"实际来自 **300 串行超集**，**非 R2 并行**。codex 全部 100 条均为串行。
3. **监控指标**（本轮必须对比 R1 同 30 条）：`quota-blocked` / `timeout` / `no-patch` 率 → 若 R2 显著上升 ⇒ 判"并行污染" → 结论打折。SWEBENCH_COMPARE.html §2 监控表已生成。

**R2 监控快照**（2026-10-09 14:05，R216 更新）：

| 指标 | R1 (30 serial) | R2 (70 parallel, near done) | 判定 |
|:--|:--|:--|:--|
| **quota_blocked** | 0/210 (0%) | 0/699 (0%) | ✅ **NO gateway pollution** |
| **timeout** | 0 (codex 2) | minimal (codex 3, claude-code 1 astropy) | ✅ 正常 |
| **workdir_blocked** ⚠️NEW | **0/210 (0%)** | **61/699 (8.7%)** ↓ from 64(R215)↓ from 88(R207) | ⚠️ **PARALLEL POLLUTION (workdir)** — **FIX IN PROGRESS (rerun_blocked_optimized.sh: Phase 1 non-sympy — claude-code DONE, cline-patched DONE, dsh DONE, pi [4/19] running; Phase 3 sympy=44 after pi)** |
| **no-patch (patch_applied=False)** | **0/210 (0%)** | **较高** (non-django/sympy repos) | ⚠️ eval env limitation |

**⚠️ 新发现：workdir git-checkout 冲突 = 并行污染（R207 首次披露）**：
1. **88 个 workdir-blocked 实例**（全部 R2/并行，0 个 R1/串行）→ 确认是**并行执行**导致的。
2. **根因**：7 个 harness 共享同一 repo workdir（如 `/dev/shm/harness_work/workdirs/django_django`），当 harness A 修改文件后 harness B 尝试 `git checkout` 到不同 commit 时失败（"Your local changes would be overwritten"）。
3. **影响**：pi 受影响最大（31 blocked，仅 69/100 实际运行），claude-code 次之（24 blocked，76/100）。opencode 未受影响（0 blocked，100/100）。
4. **对 resolve rate 的影响**：blocked 实例不计入 scored 分母，所以 rate 不被拉低；但**覆盖率降低**意味着 rate 基于更小样本。
5. **修复计划（R210 优化版）**：hermes 的 12 个剩余实例全是 sympy → **44 个非 sympy blocked 可立即与 hermes 并行重跑**（不同 workdir 无冲突），**44 个 sympy blocked 等 hermes 完成后串行重跑**。R210 已 kill 旧 `rerun_blocked_serial.sh` → 启动 `rerun_blocked_optimized.sh`（PID 260306, ppid=1）：Phase 1 非 sympy=44 正在跑（claude-code 12 django 优先），Phase 3 sympy=44 等 hermes。预计总时长 ~16h（vs 旧方案 18h，省 ~2h hermes 等待时间）。`git_clone_or_fetch` 已含 `git reset --hard HEAD` + `git clean -fd`（逐实例清理，防止 checkout 冲突）。

**🔬 关键发现：R2 resolve-rate 下降 = 实例集组成偏差，NOT 并行污染**：
1. **R1 = 仅 django(15) + sympy(15)** → 两个最易 repo（codex 300-full: django 29%, sympy 8%）
2. **R2 = 26 django + 15 sympy + 44 难题 repo**（matplotlib 0%, sklearn 4%, pytest 0%, sphinx 0%, astropy 0%）
3. **eval 环境问题**：非 django/sympy repo 的 patch 已生成（model_patch present）但 `patch_applied=False`（eval 无法在无 Docker 环境下 apply）→ 这些条目分类为 `blocked`，非 harness 失败
4. **结论**：R1→R2 resolve-rate 下降（60%→6% on completed R2）是**实例难度差异** + **eval 环境限制**，**非并发争用**。quota_blocked=0 证实无网关限流污染。
5. **⚠️ 报告含义**：R2 7×100 表中，非 django/sympy 行的 resolve=0 可能**不代表 harness 真实能力**，而是 eval 环境限制。最终报告需标注此限制。

## 🗣️ 运维问答 · 2026-10-08④（下一步工作建议）

> 数据源：`kimi_pilot_results.json`（480 entries = 30×7=210 in-scope + codex×300 superset），全 kimi-k2.6-cloud backbone。

### Q1. 横评数据的深度挖掘

现有报告已覆盖 per-harness resolve rate、per-repo breakdown、failure mode、cost、difficulty。以下 4 角度**尚未覆盖**：

**① Codex 300-instance 全量暴露的子集偏差（最高价值）**：codex 30-subset 46.7% vs 300-full **14.3%**——**3.3 倍偏差**。12 repo 中 7 个 0%（astropy/matplotlib/sklearn/sphinx/pytest/flask/requests），仅 django 28.9%、sympy 7.8% 非零。产出：对比柱状图（30-subset vs 300-full per-repo）。依据：`kimi_pilot_results.json` codex=300 entries。

**② "Nobody solved" 12 条根因深挖**：报告 §4.4 列出 12 条 ALL-fail（40%）但未做根因。逐条检查 `harness_result.stdout_tail`，分类：跨文件修改 / 测试歧义 / 领域知识缺失。依据：12×7=84 entries 的 `stdout_tail`。

**③ Patch 重叠度分析**：18 条 instance 有 2+ harness resolved（ALL=8+SOME=10），提取 `model_patch` 做 diff：convergent（同文件同行）vs divergent（不同方法）。限制：原始 patch 在 `/dev/shm/` 已过期，需重跑或从 git 恢复。

**④ Wall time vs Resolution**：Pi avg 275s 但 60.0%，codex avg 843s 但 46.7%——速度与正确率**负相关**。分析 resolved vs failed 的 wall time 分布。

### Q2. BaiZe backbone 接入评测的前置准备

**P0（立即做）**：① Harness 冻结配置文档化（`harness_frozen_config.yaml` + `harness_adapter_spec.md`，从现有 `run_harness.py`/`run_serial_kimi.py`/`r1_eval.py` 抽取，半天）；② Endpoint 健康检查脚本（`endpoint_health_check.py`，测 `/v1/models` + `/v1/chat/completions` + 延迟，2h）。

**P1（训练前做框架）**：③ 5-run 自动化（扩展 `run_serial_kimi.py` → `run_serial_multi.py --runs N`，聚合 mean±std，1 天）；④ 配对检验（`paired_stats.py`：McNemar + paired bootstrap CI，半天）；⑤ 诊断 D1–D6（从 `r1_eval.py` 抽取为 `diagnostic.py`，半天）。

### Q3. 评测规模扩展的建议

**强烈建议扩到 100–300 条**。依据：codex 30-subset 46.7% vs 300-full 14.3% = 3.3 倍偏差。30 条仅 django+sympy。

**扩优先序**：① django（114/300，补 35–85 条）→ ② sympy（77/300，补 25–35 条）→ ③ sklearn+matplotlib（各 23/300，codex 300 上 0%，测试「完全失败 repo」）→ ④ 不急 sphinx/pytest（与 EDA 相关性低）。

**EDA-Eval-PyAether 管线**：可提前搭建。现有 `run_harness.py`+`r1_eval.py` unshare 沙箱已验证。158 任务若也是「产 patch→跑 test→判 resolved」，管线可直接复用，只需替换数据集+评测脚本+沙箱环境。建议先 kimi 跑 5–10 条 smoke test。**缺什么**：EDA-Eval 158 任务定义文件+评测脚本（需确认是否已有）。



### Q4. 多 backbone 对比的前置

**现在可跑 pilot 版**，但有条件。**可行**：kimi × 7 harness × 30 条已完成，再跑 kimi × 2 harness × 20 新 instance 验证管线稳定性。**缺什么**：① MiniCPM5-2B endpoint——需 vLLM server，GPU 被训练占满，需等空窗；② DeepSeek-V4-Pro——需运维提供 API key；③ BaiZe base/SFT/RL——训练未完成。**3 阶段建议**：Phase 1（立即可做）kimi × 新 20 条 → Phase 2（等 GPU 空窗）MiniCPM5-2B × 2 harness × 20 条 → Phase 3（BaiZe 完成后）BaiZe-base/SFT/RL × 7 harness × 30+ 条。

### Q5. 对论文的补充建议

**① Harness 方差效应（核心）**：同一 backbone、同一 30 条，7 个 harness resolve rate 从 40.0% 到 60.0%——**20pp 方差完全由 harness 架构差异造成**。报告 BaiZe 成绩必须同时报告所用 harness。依据：210 entries per-harness 40.0%–60.0%。
**② 子集偏差警告**：codex 30-subset 46.7% vs 300-full 14.3% = 3.3 倍偏差。论文应标注子集选择影响。依据：codex=300 entries。
**③ 失败模式对训练的启示**：主要失败模式 f2p-fail（90%+），即「知道改哪里但改不对」。对 BaiZe RL——reward signal 应关注「patch 通过 f2p test」而非仅「patch apply」。依据：failure detail 分析。
**④ 成本-性能 Pareto**：Pi（60.0%, 275s）vs deepseek-harness（40.0%, 293s）wall time 接近但差 20pp。依据：per-harness avg_wall_s + resolve rate。
**⑤ "Nobody solved" 12 条作为难度基准**：12/30=40% 实例 7 个 harness 全失败，定义为「hard」实例。依据：instance-level ALL/NONE/SOME = 8/12/10。

> 📦 R196（2026-10-09 01:35）已归档 → daily-memories-harness/2026-10-09.md。结论：SWEBENCH_COMPARE 53167B/520entries/156resolved，quota_blocked=0。需要时再读。

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
- 2026-10-09 01:00 —— **第一百九十五轮** —— 🔄 Round-2 progress monitor + SWEBENCH_COMPARE.html refreshed (52716B, 504 entries, 152 resolved)：in-scope progress codex 100/100✅(res=33,33.0%), hermes 49/100(res=20,40.8% 领先), pi 71/100(res=26,36.6%), cline 72/100(res=21,29.2%), opencode 72/100(res=21,29.2%), dsh 68/100(res=17,25.0%), claude-code 72/100(res=14,19.4%). 7 serial processes running (etimes~19970s≈5.5h). R2 progress since R194: cline+4, opencode+4, claude-code+4, dsh+5, pi+7, hermes+2. quota_blocked=0 ALL → NO parallel pollution ✅. ETA: bottleneck hermes 51 remaining→~15:00 Oct9, dsh 32→~05:00, cline/opencode/claude-code 28→~05:00, pi 29→~03:30. ⑦ deliverables verified: 口径与并发 section ✅ / trace report in doc root (38307B) ✅ / 复用-新跑 markers (104) ✅ / monitoring table ✅. → commit+push. 📦 体积：TASK=32870B(32.1KB ✓) / MEMORY=~32KB(31.2KB ✓)（归档 0KB）。
- 2026-10-09 02:10 —— **第一百九十七轮** —— 🔄 Round-2 progress monitor + SWEBENCH_COMPARE.html refreshed (54030B, 551 in-scope entries, 162 resolved): codex 100/100✅(res=34,39.1%), hermes 58/100(res=27,47.4% 领先), pi 81/100(res=27,42.2%), cline 77/100(res=22,40.0%), opencode 77/100(res=21,32.8%), dsh 78/100(res=18,27.3%), claude-code 81/100(res=14,24.6%). 6 serial processes running (etimes~24200s≈6.7h). R2 progress since R195: cline+5, opencode+5, claude-code+9, dsh+10, pi+10, hermes+9. quota_blocked=0 ALL → NO parallel pollution ✅. ⑦ deliverables verified: 口径与并发 section ✅ / trace report in doc root (38307B) ✅ / 复用-新跑 markers ✅ / monitoring table ✅. ETA: bottleneck hermes 42 remaining→~10:20 Oct9, cline/opencode 23→~05:20, dsh 22→~05:10, pi/claude-code 19→~04:50. → commit+push. 📦 体积：TASK=32870B(32.1KB, marginal) / MEMORY=~31.5KB(30.8KB ✓)（归档 0KB）。
- 2026-10-09 02:47 —— **第一百九十八轮** —— 🔄 Round-2 progress monitor + SWEBENCH_COMPARE.html refreshed (55001B, 586 in-scope entries, 164 resolved): codex 100/100✅(res=34,38.2%), hermes 61/100(res=27,45.0% 领先), pi 87/100(res=27,40.3%), cline 84/100(res=22,36.7%), opencode 84/100(res=22,32.8%), dsh 86/100(res=18,26.1%), claude-code 84/100(res=14,23.3%). 6 serial processes running (etimes~26375s≈7.3h). R2 progress since R197: cline+7, opencode+7, claude-code+3, dsh+8, pi+6, hermes+3. quota_blocked=0 ALL → NO parallel pollution ✅. ⑦ deliverables verified: 口径与并发 section ✅ / trace report in doc root (38307B) ✅ / 复用-新跑 markers ✅ / monitoring table ✅. ETA: bottleneck hermes 39 remaining→~10:00 Oct9, cline/claude-code 16→~05:15, opencode 16→~04:45, dsh 14→~04:30, pi 13→~04:15. → commit+push. 📦 体积：TASK=32870B(32.1KB ✓) / MEMORY=~31KB(30.4KB ✓)（归档 R191/R188 ~1.7KB → daily-memories）。
- 2026-10-09 03:30 —— **第一百九十九轮** —— 🔄 Round-2 RESTARTED: Found all 6 old processes dead (ppid=1, ~8h old but only +4-13 instances each → stuck/slow). Killed old PIDs + restarted 5 incomplete harnesses with setsid+nohup (restart_round2.sh, properly detached). SWEBENCH_COMPARE.html refreshed (55973B, 621/700 in-scope, 164 resolved): codex 100/100✅(37.4%), pi 100/100✅(39.1%), hermes 64/100(42.9% 领先), cline 88/100(35.5%), opencode 88/100(31.9%), dsh 93/100(25.4%), claude-code 88/100(22.6%). 5 new serial processes running (ppid=1, setsid detached, etimes~60s). quota_blocked=0 ALL → NO parallel pollution ✅. ⑦ deliverables verified: 口径与并发 section ✅ / trace report in doc root (38307B) ✅ / 复用-新跑 markers ✅ / monitoring table ✅. ETA: bottleneck hermes 36 rem→~10:00 Oct9, cline/claude-code 12→~05:15, opencode 12→~04:55, dsh 7→~04:15. → commit+push. 📦 体积：TASK=32870B(32.1KB ✓) / MEMORY=28265B(27.6KB ✓)（归档 R185-R192 ~4.6KB → daily-memories-harness/2026-10-08.md）。

- 2026-10-09 05:55 —— **第二百零三轮** —— 已归档（同下）→ daily-memories-harness/2026-10-09.md。
- 2026-10-09 06:30 —— **第二百零四轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 07:05 —— **第二百零五轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 07:39 —— **第二百零六轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 08:13 —— **第二百零七轮** —— 已归档 → daily-memories-harness/2026-10-09.md（⚠️ WORKDIR-BLOCKED DISCOVERY: 88 blocked, all R2 parallel, git checkout conflicts from shared workdirs. opencode DONE 100/100 35.0%. Plan: hermes done → serial re-run blocked → final 7×100）。需要时再读。
- 2026-10-09 09:04 —— **第二百零八轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 09:40 —— **第二百零九轮** —— 已归档 → daily-memories-harness/2026-10-09.md。
- 2026-10-09 10:22 —— **第二百一十轮** —— 已归档 → daily-memories-harness/2026-10-09.md（🚀 OPTIMIZED BLOCKED RE-RUN: killed old serial script → launched rerun_blocked_optimized.sh. Phase 1 non-sympy=44 parallel with hermes, Phase 3 sympy=44 after. Hermes 88/100, 12 rem. SWEBENCH_COMPARE 57686B 688/700 193 resolved）。需要时再读。
- 2026-10-09 11:01 —— **第二百一十一轮** —— 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
- 2026-10-09 11:37 —— **第二百一十二轮** —— 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
- 2026-10-09 12:17 —— **第二百一十三轮** —— 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
- 2026-10-09 12:53 —— **第二百一十四轮** —— 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
- 2026-10-09 13:28 —— **第二百一十五轮** —— 已归档 → daily-memories-harness/2026-10-09.md。需要时再读。
- 2026-10-09 14:05 —— **第二百一十六轮** —— 🔄 Blocked re-run monitor: Hermes FINISHED (100/100, 36 resolved, sympy-15346 resolved — PID 4039300 gone). DSH Phase 1 DONE (5/5 non-sympy, 25/94=26.6%, 6 sympy blocked remain). Cline Phase 1 DONE (8/8, 32/95=33.7%, 5 sympy blocked). Claude-code Phase 1 DONE (12/12, 27/88=30.7%, 12 sympy blocked). Pi Phase 1 RUNNING [4/19] django-11964 (PID 1370421, ppid=260306, etimes~1884s). 61 blocked remaining (down from 64). SWEBENCH_COMPARE.html refreshed (57995B, 700/700, 218 resolved). In-scope scored rates: pi 39.4%(71) > codex 37.4%(91) > hermes 36.0%(100) > opencode 35.0%(100) > cline 33.7%(95) > claude-code 30.7%(88) > dsh 26.6%(94). quota_blocked=0 → NO gateway pollution ✅. ⑦ deliverables verified: 口径与并发 ✅ / trace report in doc root (38307B) ✅ / 复用-新跑 markers ✅ / monitoring table ✅. Process: rerun_blocked_optimized.sh (PID 260306, ppid=1) alive. Next: pi Phase 1 finishes (~2.5h) → Phase 3 sympy=44 serial (~7.3h) → final ~00:00 Oct 10. → commit+push. 📦 体积：TASK=32870B(32.1KB ⚠️) / MEMORY=~30KB(29.3KB ✓)。
