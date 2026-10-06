# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A kimi-k2.6-cloud serial cross-eval — codex --resume RUNNING (PID 2151526, ~660min): 162 blocked remaining (3 unblocked since R132: +3 pbf). 330 entries, 61 resolved.
已完成:       H-B 5×源码分析 · H-D 对比矩阵 · H-C 评测调研 · kimi serial runner · cline-patched×30 (60.0%) · codex×300 (43 resolved, 95 pbf, 162 blocked) · SWEBENCH_COMPARE.html (330 entries, 61 resolved) · ✅ git_fetch_retry (120→300s + 3 retries)
当前动作:     R133: codex --resume progress check (PID 2151526 alive, ~660min, working django__django-15388; 3 unblocked since R132: +3 pbf → 43/95/162) + SWEBENCH_COMPARE.html regenerated (72939B, 61 resolved) + relay healthy skip 86th + git sync (0/0 synced, proxy fetch) + 体积自检 (TASK=29771B/MEMORY=16204B, both ≤32KB ✓)
下一步:       codex --resume 完成(162 blocked) → cline-patched×300 --resume → opencode×300 → claude-code×300 → deepseek-harness×300 → 最终更新 SWEBENCH_COMPARE.html
阻塞:         无硬阻塞. 162 blocked remaining. git_fetch_retry fix (300s+3retry) 正在逐条解除.
ERROR_COUNT:  0
```

## 🆕 第一百三十三轮速览（2026-10-07 06:39）— codex --resume RUNNING (PID 2151526, ~660min): 3 unblocked since R132 (+3 pbf → 43/95/162) + SWEBENCH_COMPARE.html regenerated (72939B, 61 resolved) + relay healthy skip 86th + git sync (0/0 synced, proxy fetch) + 体积自检 (TASK=29771B/MEMORY=16204B, both ≤32KB ✓)

- 🔄 **codex --resume progress**：PID 2151526 (ppid=1, etimes≈39574s ≈ 660min) alive, currently running `django__django-15388` (child PID 2629619→run_single.py, etimes≈748s ≈ 12min). 3 instances unblocked since R132: +3 pbf (95 total), -3 blocked (162 total). codex 300 total: 43 resolved (14.3%), 95 pbf (31.7%), 162 blocked (54.0%). Total: 61 resolved (cline 18 + codex 43), 107 pbf, 162 blocked. git_fetch_retry fix (300s+3retry) continues unblocking.
- 📈 **SWEBENCH_COMPARE.html regenerated**：330 entries (30 cline-patched + 300 codex), 61 resolved, 72939 bytes。gen_kimi_compare.py exit=0.
- ✅ **ops 中继复核（第 86 次）→ 健康**。relay `2489749 1 484081 bash ops_relay.sh`（ppid=1, etimes≈5.6d）。跳过重启。
- ✅ **git sync**：`git fetch`（proxy=http://172.19.92.25:13128）exit=0。rev-list 0/0 (fully synced)。无新运维指令。
- 📦 **体积自检**：TASK=29771B / MEMORY=16204B → 两者均 ≤32KB ✓（无需归档）。
- ⏭ **下一步**：codex --resume 后台继续（162 blocked）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300 → 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第一百三十二轮速览（2026-10-07 06:07）— codex --resume RUNNING (PID 2151526, ~626min): 1 unblocked since R131 (+1 pbf → 43/92/165) + SWEBENCH_COMPARE.html regenerated (72939B, 61 resolved) + relay healthy skip 85th + git sync (0/0 synced) + 体积自检 (TASK=29771B/MEMORY=14661B, both ≤32KB ✓)

- 🔄 **codex --resume progress**：PID 2151526 (ppid=1, etimes≈37586s ≈ 626min) alive, currently running `django__django-15252` (child PID 4144623→run_single.py, etimes≈1004s ≈ 17min). 1 instance unblocked since R131: +1 pbf (92 total), -1 blocked (165 total). codex 300 total: 43 resolved (14.3%), 92 pbf (30.7%), 165 blocked (55.0%). Total: 61 resolved (cline 18 + codex 43), 104 pbf, 165 blocked. git_fetch_retry fix (300s+3retry) continues unblocking.
- 📈 **SWEBENCH_COMPARE.html regenerated**：330 entries (30 cline-patched + 300 codex), 61 resolved, 72939 bytes。gen_kimi_compare.py exit=0.
- ✅ **ops 中继复核（第 85 次）→ 健康**。relay `2489749 1 482093 bash ops_relay.sh`（ppid=1, etimes≈5.6d）。跳过重启。
- ✅ **git sync**：`git fetch`（proxy）exit=0。rev-list 0/0 (fully synced)。无新运维指令。
- 📦 **体积自检**：TASK=29771B / MEMORY=14661B → 两者均 ≤32KB ✓（R131 已滚动归档，本轮无需再归档）。
- ⏭ **下一步**：codex --resume 后台继续（165 blocked）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300 → 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第一百三十一轮速览（2026-10-07 05:24）— codex --resume RUNNING (PID 2151526, ~583min): 2 unblocked since R130 (+2 pbf → 43/91/166) + SWEBENCH_COMPARE.html regenerated (72943B, 61 resolved) + relay healthy skip 84th + git sync (0/0 synced) + 体积自检 + MEMORY rolling archive (R113及更早 → daily-memories)

- 🔄 **codex --resume progress**：PID 2151526 (ppid=1, etimes≈34996s ≈ 583min) alive, currently running `django__django-15213` (child PID 1788439→run_single.py, etimes≈395s ≈ 7min). 2 instances unblocked since R130: +2 pbf (91 total), -2 blocked (166 total). codex 300 total: 43 resolved (14.3%), 91 pbf (30.3%), 166 blocked (55.3%). Total: 61 resolved (cline 18 + codex 43), 103 pbf, 166 blocked. git_fetch_retry fix (300s+3retry) continues unblocking.
- 📈 **SWEBENCH_COMPARE.html regenerated**：330 entries (30 cline-patched + 300 codex), 61 resolved, 72943 bytes。gen_kimi_compare.py exit=0.
- ✅ **ops 中继复核（第 84 次）→ 健康**。relay `2489749 1 479503 bash ops_relay.sh`（ppid=1, etimes≈5.5d）。跳过重启。
- ✅ **git sync**：`git fetch`（proxy）exit=0。rev-list 0/0 (fully synced)。无新运维指令。
- 📦 **体积自检**：TASK=29771B / MEMORY=32489B → 本轮滚动归档 R113及更早至 daily-memories-harness → 归档后 MEMORY≈15KB.
- ⏭ **下一步**：codex --resume 后台继续（166 blocked）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300 → 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第一百三十轮速览（2026-10-07 04:49）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~549min, 1 unblocked since R129 (+1 pbf → 43/89/168), SWEBENCH_COMPARE.html 72943B 61 resolved, relay healthy skip 83rd, git sync 0/0, 体积自检 TASK=29771B/MEMORY=32465B）

## 🆕 第一百二十九轮速览（2026-10-07 04:13）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~514min, 1 unblocked since R128 (+1 pbf → 43/88/169), SWEBENCH_COMPARE.html 72945B 61 resolved, relay healthy skip 82nd, git sync 0/0, 体积自检 TASK=29771B/MEMORY=32450B）

## 🆕 第一百二十八轮速览（2026-10-07 03:39）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~478min, 3 unblocked since R127 (+3 pbf → 43/87/170), SWEBENCH_COMPARE.html 72945B 61 resolved, relay healthy skip 81st, git sync 0/0, 体积自检 TASK=29771B/MEMORY≈31KB）

## 🆕 第一百二十七轮速览（2026-10-07 03:05）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~445min, 2 unblocked since R126 (+2 pbf → 43/84/173), SWEBENCH_COMPARE.html 72952B 61 resolved, relay healthy skip 80th, git sync 0/0, 体积自检 TASK=29771B/MEMORY≈31KB）

## 🆕 第一百二十六轮速览（2026-10-07 02:31）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~411min, 2 unblocked since R125 (+2 pbf → 43/82/175), SWEBENCH_COMPARE.html 72956B 61 resolved, relay healthy skip 79th, git sync pulled 1 zhulong commit, 体积自检 TASK=29771B/MEMORY≈31KB）

## 🆕 第一百二十四轮速览（2026-10-07 01:24）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~344min, 2 unblocked since R123 (+1 resolved +1 pbf → 41/80/179), SWEBENCH_COMPARE.html 72960B 59 resolved, relay healthy skip 77th, R123 push confirmed succeeded, git sync）

## 🆕 第一百二十三轮速览（2026-10-07 00:51）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~309min, 2 unblocked since R122 (+2 resolved), codex 40 resolved/79 pbf/181 blocked, SWEBENCH_COMPARE.html 72960B 58 resolved, relay healthy skip 76th, R123 push 503→实际已成功, git sync）

## 🆕 第一百二十二轮速览（2026-10-07 00:17）—— 已滚动归档至 daily-memories-harness/2026-10-07.md（结论不改：codex --resume RUNNING PID 2151526 ~275min, 2 unblocked since R121 (+1 resolved), codex 38 resolved/79 pbf/183 blocked, SWEBENCH_COMPARE.html 72960B 56 resolved, relay healthy skip 75th, git sync）

## 🆕 第一百二十一轮速览（2026-10-06 23:39）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~240min, 3 unblocked since R120 (+2 resolved), codex 37 resolved/78 pbf/185 blocked, SWEBENCH_COMPARE.html 72962B 55 resolved, relay healthy skip 74th, git sync）


## 🆕 第一百一十九轮速览（2026-10-06 22:33）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~172min, 2 unblocked since R118: +1 resolved +1 pbf, codex 35 resolved/76 pbf/189 blocked, SWEBENCH_COMPARE.html 72964B 53 resolved, relay healthy skip 72nd, git sync）

## 🆕 第一百一十八轮速览（2026-10-06 21:58）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~137min, 2 unblocked since R117: +1 resolved +1 pbf, codex 34 resolved/75 pbf/191 blocked, SWEBENCH_COMPARE.html 72964B 52 resolved, relay healthy skip 71st, git sync）

## 🆕 第一百一十七轮速览（2026-10-06 21:23）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~103min, 1 unblocked→pbf since R116, codex 33 resolved/74 pbf/193 blocked, SWEBENCH_COMPARE.html 72965B 51 resolved, relay healthy skip 70th, git sync）

## 🆕 第一百一十六轮速览（2026-10-06 20:50）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~69min, 1 unblocked→pbf since R115, codex 33 resolved/73 pbf/194 blocked, SWEBENCH_COMPARE.html 72966B 51 resolved, relay healthy skip 69th, git sync）

## 🆕 第一百一十五轮速览（2026-10-06 20:15）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex --resume RUNNING PID 2151526 ~36min, 2 unblocked→pbf (astropy-14995/6938), codex 33 resolved/72 pbf/195 blocked, SWEBENCH_COMPARE.html 72972B 51 resolved, relay healthy skip 68th, git sync）

## 🆕 R113及更早（R34~R114）—— 均已滚动归档至 daily-memories-harness/2026-10-04.md ~ 2026-10-06.md（结论不改：codex×300 从 0 增长到 COMPLETE 33 resolved/70 pbf/197 blocked + git_fetch_retry fix + --resume started + cline-patched×30 COMPLETE 60.0% + 5 harness 端到端打通 + gw_proxy/r1_eval/SWEBENCH_COMPARE.html 基建 + relay 多轮健康 skip + batch-4/5 交付）

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
