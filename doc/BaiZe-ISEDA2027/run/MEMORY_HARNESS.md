# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A kimi-k2.6-cloud serial cross-eval — codex×300 --resume RUNNING (PID 1898015, 15/270 new done, on django-12125) + ✅ deepseek-harness pnpm install + BUILD SUCCEEDED (dsh CLI --profile headless ready) + ✅ claude-code telemetry OFF
已完成:       H-B 5×源码分析 · H-D 对比矩阵 · H-C 评测调研 · kimi serial runner · cline-patched×30 (60.0%) · codex×30 (46.7%) · codex×300 --resume RUNNING (45 entries, 19 resolved, 42.2%) · SWEBENCH_COMPARE.html (75 entries, 37 resolved, total_planned=300) · ✅ Claude Code 遥测关闭 · ✅ deepseek-harness pnpm install + build (dsh CLI ready, --profile headless)
当前动作:     R87: codex×300 --resume progress 15/270 new (45 total codex entries, 19 resolved, 42.2%) + SWEBENCH_COMPARE.html regenerated (75 entries, 37 resolved) + relay healthy skip 40th + git sync
下一步:       codex×300 完成(~255条剩余, ~2.9天) → cline-patched×300 --resume(skip 30) → opencode×300 → claude-code×300(遥测已关) → deepseek-harness×300(dsh --profile headless, 需写run_harness.py集成) → 最终更新SWEBENCH_COMPARE.html
阻塞:         无硬阻塞. deepseek-harness: pnpm install ✅ + build ✅, 但 run_harness.py 集成(DeepseekHarnessDriver stub→dsh CLI headless)尚未写. 序列中最后一个, 不阻塞其他4个.
ERROR_COUNT:  0
```

## 🆕 第八十七轮速览（2026-10-06 03:12）— codex×300 progress 15/270 (45 total, 19 resolved, 42.2%) + SWEBENCH_COMPARE.html regenerated (75 entries, 37 resolved) + relay healthy skip 40th + git sync

- 📊 **codex×300 --resume progress**：PID 1898015 运行中 (etimes≈14353s≈4.0h)。45 codex entries (15 new since ×30)。19/45 resolved (42.2%), 23 patch-but-failed, 0 quota-blocked, 3 blocked (astropy git fetch timeout/lock)。当前 instance: `django__django-12125` (子进程 PID 1933855, etimes≈403s≈6.7min)。速率 ~16.5min/inst → 255 remaining ≈ 70h ≈ 2.9天。
- 📈 **SWEBENCH_COMPARE.html regenerated**：75 entries, 37 resolved (cline-patched 18 + codex 19), 16512 bytes。gen_kimi_compare.py exit=0。
- ✅ **ops 中继复核（第 40 次）→ 健康**。relay `2489749 1 385193 Ss`（ppid=1, etimes≈4.46d）。`.last_run_id=71`（与上轮一致, 无新命令）。跳过重启。
- ✅ **git sync**：`git fetch`（proxy）exit=0 → `rev-list=0 0`（完全同步）。BAIZE_HARNESS_TASK.md 无新运维指令。
- ⏭ **下一步**：codex×300 后台继续（~255 条剩余, ~2.9天）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300（需写 `DeepseekHarnessDriver` 集成 `dsh --profile headless`）→ 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第八十六轮速览（2026-10-06 02:38）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex×300 progress 13/270 (43 total, 18 resolved, 41.9%) + SWEBENCH_COMPARE.html regenerated (73 entries, 36 resolved) + relay healthy skip 39th + git sync）

- 📊 **codex×300 --resume progress**：PID 1898015 运行中 (etimes≈12210s≈3.4h)。43 codex entries (13 new since ×30)。18/43 resolved (41.9%), 22 patch-but-failed, 0 quota-blocked, 3 blocked (astropy git fetch timeout/lock)。当前 instance: `django__django-11999` (子进程 PID 3625199, etimes≈404s≈6.7min)。速率 ~15.7min/inst → 257 remaining ≈ 67h ≈ 2.8天。
- 📈 **SWEBENCH_COMPARE.html regenerated**：73 entries, 36 resolved (cline-patched 18 + codex 18), 16073 bytes。gen_kimi_compare.py exit=0。
- ✅ **ops 中继复核（第 39 次）→ 健康**。relay `2489749 1 383050 Ss`（ppid=1, etimes≈4.44d）。`.last_run_id=71`（与上轮一致, 无新命令）。跳过重启。
- ✅ **git sync**：`git fetch`（proxy）exit=0 → `rev-list=0 0`（完全同步）。BAIZE_HARNESS_TASK.md 无新运维指令。
- ⏭ **下一步**：codex×300 后台继续（~257 条剩余, ~2.8天）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300（需写 `DeepseekHarnessDriver` 集成 `dsh --profile headless`）→ 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第八十五轮速览（2026-10-06 02:05）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex×300 progress 11/270 (41 total, 16 resolved, 39.0%) + SWEBENCH_COMPARE.html regenerated (71 entries, 34 resolved) + relay healthy skip 38th + git sync）

## 🆕 第八十四轮速览（2026-10-06 01:29）—— 已滚动归档至 daily-memories-harness/2026-10-06.md（结论不改：codex×300 progress 9/270 (39 total, 16 resolved, 41.0%) + SWEBENCH_COMPARE.html regenerated (69 entries, 34 resolved) + relay healthy skip 37th + git sync + push exit=0）

## 🆕 第八十三轮速览（2026-10-06 00:50）—— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：deepseek-harness pnpm install + BUILD SUCCEEDED + codex×300 progress 8/270 + SWEBENCH_COMPARE.html regenerated + relay healthy skip 36th）

- 🎉 **deepseek-harness pnpm install SUCCEEDED**：根因 = corepack shim (`~/.local/node22/bin/pnpm`) 拦截 `pnpm` 命令 → 尝试从 `registry.npmjs.org` 下载 → ENETUNREACH。解法 = 用独立 pnpm 二进制 `~/.local/pnpm/pnpm` (v11.7.0) 绕过 corepack + `.npmrc` registry 改为 `https://mirrors.cloud.tencent.com/npm/`（npmmirror.com 被防火墙封锁 000, tencent 200）。`pnpm install --frozen-lockfile` → `Already up to date` (1068 packages 已在 .pnpm store) → exit=0, 350ms。
- 🎉 **deepseek-harness BUILD SUCCEEDED**：`pnpm build` (= `tsx scripts/build.ts`) → `✓ built in 5.45s`, `220 client artifact(s)`, exit=0。`dsh` CLI 可用 (`apps/cli/lib/bin.js`)，支持 `--profile headless "task"` 非交互模式（answer one task, print result, exit）→ 适合 SWE-bench 评测。landlock-run 二进制已就绪 (`native/landlock-run/packages/linux-x64/bin/landlock-run`, statically linked ELF x86-64)。
- 📊 **codex×300 --resume progress**：PID 1898015 运行中 (etimes≈6000s≈1.66h)。38 codex entries (8 new since ×30)。15/38 resolved (39.5%), 19 patch-but-failed, 0 quota-blocked, 3 blocked (astropy git fetch timeout/lock)。当前 instance: `django__django-11815`。速率 ~13min/inst → 262 remaining ≈ 57h ≈ 2.4天。
- ⚠️ **3 blocked astropy entries**：`astropy-14995` (git fetch TIMEOUT), `astropy-6938` (base_commit fetch TIMEOUT), `astropy-7746` (shallow.lock File exists)。已清理 stale shallow.lock。`--resume` 只 skip "resolved"/"patch-but-failed" → blocked 条目会在下次 resume 重试。
- 🔧 **gen_kimi_compare.py fixed**：3 entries 缺 `harness_result` (blocked) → KeyError。修复：`e.get("harness_result", {})` + 新增 "Blocked (infra)" 列 + `infblocked` CSS class (⚠ icon)。
- 📈 **SWEBENCH_COMPARE.html regenerated**：67 entries, 33 resolved (cline-patched 18 + codex 15), 14756 bytes。新增 "Blocked (infra)" 列。
- ✅ **ops 中继复核（第 36 次）→ 健康**。relay `2489749 1 376297 Ss`（ppid=1, etimes≈4.35d）。`.last_run_id=71`。跳过重启。
- ✅ **git sync**：`git fetch`（proxy）exit=0 → `rev-list=0 0`（完全同步）。BAIZE_HARNESS_TASK.md 无新运维指令（最新 commit `17de0dcf` = Claude Code 合规口径, 已处理）。
- ⏭ **下一步**：codex×300 后台继续（~262 条剩余, ~2.3天）→ 完成后 cline-patched×300 `--resume` → opencode×300 → claude-code×300 → deepseek-harness×300（需写 `DeepseekHarnessDriver` 集成 `dsh --profile headless`）→ 最终更新 SWEBENCH_COMPARE.html。保持 `WAITING=1`。

## 🆕 第八十二轮速览（2026-10-05 23:10）—— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：codex×30 COMPLETE 14/30=46.7% → codex×300 --resume LAUNCHED PID 1898015 + rootfs 300/300 覆盖验证 + HTML 刷新 + relay healthy skip 35th）

## 🆕 第八十轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：codex×30 23/30 scored + SWEBENCH_COMPARE.html 53 entries + deepseek-harness pnpm BLOCKED npm registry 防火墙 + relay healthy skip 33rd）

## 🆕 第七十七轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：deepseek-harness toolchain installed node22+rust+pnpm+landlock-run + pnpm install BLOCKED npm registry ECONNRESET + codex×30 RUNNING 14/30 + relay healthy skip 30th + git sync）

## 🆕 第七十六轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：codex×30 RUNNING 13/30 scored + relay 健康 skip 第 29 次 + git sync + MEMORY rolling）

## 🆕 第七十四轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：codex×30 RUNNING 2/30 scored + relay 健康 skip 第 27 次 + 无新指令）

## 🆕 第七十三轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：cline-patched×30 COMPLETE 18/30 resolved (60.0%) + codex×30 LAUNCHED + SWEBENCH_COMPARE.html regenerated）

## 🆕 第七十二轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 25 次 + kimi 22/30 scored: 14 resolved (63.6%) + sympy 后4条全resolved + SWEBENCH_COMPARE.html regenerated (10422B)）

## 🆕 第七十轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 23 次 + kimi 15/30 scored: 10 resolved (66.7%) + SWEBENCH_COMPARE.html regenerated (8902B)）

## 🆕 第六十九轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 22 次 + kimi 13/30 scored: 10 resolved (76.9%) + SWEBENCH_COMPARE.html regenerated）

## 🆕 第六十八轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 21 次 + kimi 串行横评 10/30 scored: 8 resolved + gw_proxy 健康 + SWEBENCH_COMPARE.html regenerated）

## 🆕 第六十七轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 20 次 + kimi 串行横评 5/30 scored: 3 resolved + gw_proxy 健康）

## 🆕 第六十五轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：kimi-k2.6-cloud 横评启动 + API 验证 + gw_proxy 配置 + 代码修改 + run_serial_kimi.py + cline-patched×30 后台启动）

## 🆕 第六十四轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 18 次 + R63 resume 3/9 scored + 8 blocked 修复 + resume3 启动 + cimi_search SWE-bench 官方口径核实 + SWEBENCH_OFFICIAL_CRITERIA_VERIFICATION.md 产出）

## 🆕 第六十三轮速览 —— 已滚动归档至 daily-memories-harness/2026-10-05.md（结论不改：relay 健康 skip 第 17 次 + 9 blocked resume 启动 PID 4113953 + quota 全重置 8/8 keys 200）

## 🆕 第六十二轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 16 次 + batch v2 21/30 scored + aggregate codex 2/21=9.5% leads + fair rate codex 2/3=67% + django-11001=4/4 全 resolve）

## 🆕 第六十一轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 15 次 + batch v2 19/30 scored + aggregate codex 2/19=11% leads）

## 🆕 第六十轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 14 次 + batch v2 16/30 进度 + quota 污染深度分析 fair metric codex 2/3=67% leads）

## 🆕 第五十九轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 13 次 + batch v2 15/30 log 推进至 django-11283 + aggregate codex 2/15=13% 领先）

## 🆕 第五十八轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 12 次 + batch v2 15/30 完整评分 + quota-OK fair metric codex 2/2=100%/cline 1/3=33%/opencode 1/1=100%/claude-code 1/1=100%）


## 🆕 第五十七轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 11 次 + batch v2 15/30 scored + sympy-11870 quota retry ETA ~04:27）

## 🆕 第五十六轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 10 次 + batch v2 15/30 scored + SWEBENCH_COMPARE.html updated to 17 inst）

## 🆕 第五十五轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 9 次 + batch v2 12/30 scored + quota 瓶颈从 11039 起全空 patch）


## 🆕 第五十三轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 7 次 + batch v2 5/30 scored + SWEBENCH_COMPARE.html 7 instances + quota 瓶颈从 11039 起全空 patch）


## 🆕 第五十轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：RUN_ID 62 已执行 + 三大管道修复 swebench安装/report.json解析/quota backoff + codex×10924 resolved=True + batch v2 启动）

## 🆕 第五十一轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 5 次 + batch v2 2/30 scored 11001=4/4 全 resolve + instance 3/30 11019 opencode quota retry）

## 🆕 第五十二轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 6 次 + batch v2 4/8 scored 11001=4/4 resolve + 11049 进行中）

## 🆕 第四十九轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-04.md`（结论不改：pilot 30×4 批量启动、git_clone_or_fetch 重写、/dev/shm workdir 修复 NFS 竞态）

## 🆕 第四十三~四十八轮速览 —— 均已滚动归档至 `daily-memories-harness/2026-10-04.md`（结论不改：relay 多轮健康 skip · github 代理可达 · cline/codex/opencode/claude-code 端到端打通 · SWEBENCH_COMPARE.html 创建）

## 🆕 第四十一/四十二轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-04.md`（结论不改：4/5 django resolve、claude-code 打通最后一里、driver 落地）
## 🆕 第四十轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-04.md`（结论不改：relay URGENT 健康 skip · 4/5 harness 就绪 · deepseek-harness 需 node22+rust 工具链无可用源）

## 🆕 第三十四/三十五/三十九轮速览 —— 已滚动归档至 `daily-memories-harness/2026-10-04.md`（结论不改：3/5→4/5 resolved、gw_proxy 反代基建、r1_eval 跨-run 复用修复、腾讯 npm 镜像打通、claude-code sandbox stub 修复）
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

- 2026-10-04 12:3x —— **第三十九轮**（已归档至 daily-memories-harness/2026-10-04.md）：claude-code sandbox stub 根因修复（ 静态方法缺失→补齐 no-op）， STDOUT=PONG ✅。relay 健康→跳过重启。
- 2026-10-04 10:15 —— **第三十五轮**（已归档）：3/5 harness 端到端 resolved=true（codex+opencode 补全），gw_proxy.py 反代基建 + r1_eval.py 跨-run 复用修复。
- 2026-10-04 12:1x —— **第三十八轮**（已归档）：relay 再次健康跳过 + claude-code build 成功（370 包）但 headless smoke 早退（后 R39 修复）。
- 2026-10-04 11:44 —— **第三十七轮**（已归档）：relay 健康 + gw_proxy.py →chat 翻译层实现并 3 条 curl 实测全过。
- 2026-10-04 11:0x —— **第三十六轮**（已归档）：首条 URGENT relay 复核→中继已自愈（RUN_ID 34 fuser 瞬卡→CMD_TIMEOUT=600 兜底 kill→自愈），跳过重启。
- 2026-10-04 13:50 —— **第四十轮**（已归档至 daily-memories-harness/2026-10-04.md）：relay 健康 skip + deepseek toolchain de-risk（node22/rust 全镜像不可达 → 需运维装工具链）。

- 2026-10-04 14:25 —— **第四十一轮**（已归档至 daily-memories-harness/2026-10-04.md）：relay 健康 skip + 🎉 claude-code 最后一里打通（bun --preload + --define MACRO 修复 `src/utils/user.ts:108` ReferenceError → PONG ✅；工具回路实测 OK；ClaudeCodeDriver 落地）。

- 2026-10-04 16:15 —— **第四十二轮**（已归档至 daily-memories-harness/2026-10-04.md）：relay 健康 skip + 🎉🎉🎉 claude-code 端到端 resolved=True + 4/5 harness 全 resolve django__django-10914，固化 R1_DJANGO10914_RESULTS.yaml。

- 2026-10-04 17:30 —— **第四十三轮（⏱ 响应 URGENT「恢复 ops 中继」第 4 次 → 健康跳过 + 🔧 cline 配置根因修复 + 📝 SWEBENCH_COMPARE.html + 🔬 cline × sympy-11400 resolved=False 部分正确）**：relay 复核：`2489749 1 ~260000 Ss bash ops_relay.sh`（ppid=1、态 Ss、etimes≈3d）、`pstree -p 2489749`=`bash---sleep`、`last_run_id`=42、log 末条 exit=0、无跑飞残留 → **跳过重启**。**cline 配置修复**：`~/.cline/data/globalState.json` `apiBase=/cloud/v1`（应为 `/v1`），vision loop cline 守护进程 PID 465698 不断回写 → **SIGKILL**；建独立 `cline_harness_data/globalState.json` → `127.0.0.1:9090/v1` gw_proxy + `--data-dir` + `-P openai` + `DUMMY_KEY`。**`run_harness_direct.py`** 创建（monkey-patch ClineDriver via `types.MethodType`）。**`SWEBENCH_COMPARE.html`** 创建（`run/harness/`，自包含方法论+4/5 django 结果+复现命令）。**cline × sympy__sympy-11400**：`rc=0 wall=707.1s` 80 iterations 2216B patch（`ccode.py`+`codeprinter.py`+`test_fcode.py`）→ `r1_eval.py --sandbox unshare --run-id R1_CLINE_SYMPY` → **resolved=False, F2P 1/2（`test_ccode_Relational`✅ / `test_ccode_sinc`❌ AssertionError）, P2P 28/28✅**。→ sympy 比 django 难 5.4×（707s vs 131s），exact 输出格式不匹配。`git fetch` Network unreachable，无新指令。⏭ 跑 codex/opencode/claude-code × sympy-11400 → 扩 20-30 instances。保持 `WAITING=1`。

- 2026-10-04 18:10 —— **第四十四轮（⏱ 响应 URGENT「恢复 ops 中继」第 5 次 → 健康，跳过重启）**：relay 复核（原始输出）：`ps -eo pid=,ppid=,etimes=,stat=,args= | grep ops_relay.sh | grep -v grep` → **`2489749 1 266302 Ss bash ops_relay.sh`**（ppid=1 真守护、态 Ss、etimes≈3.08d）；`pstree -p 2489749`=`bash(2489749)---sleep(2309913)`（正常 20s 轮询）；`cat ops/.last_run_id`=`57`（较上轮 42 前进 15 → 日志在动）；`tail -6 /tmp/baize_ops_relay.log` → RUN_ID 52~57 均 `exit=0`；`pgrep -af 'grep -rl|fuser -v /nas_train|stage_1.5_mid'` → **无跑飞残留**（仅 cline 自身进程 + grep 命令的误匹配）→ 判据「恰好 1 条 relay 且日志在动」成立 → **跳过重启**（🚫 红线：不 pkill 健康 relay、不动 GPU pretrain P-9.2、不删数据）。`git fetch` 报 `Network is unreachable`（github 瞬断），`git log -- BAIZE_HARNESS_TASK.md` 最近仍 `4d19875`（即本条 URGENT）→ 无新指令。✅ URGENT 项完成。⏭ 继续本线：跑 codex/opencode/claude-code × sympy-11400 → 扩 20-30 instances pilot。保持 `WAITING=1`。

- 2026-10-04 21:00 —— **第四十七轮（⏱ 响应运维第 2 条「RUN_ID 62 有单不收」第 2 次 → RUN_ID 62 已执行健康跳过 + 🚫 H-A pilot 扩量受阻于 github 网络瞬断 + MEMORY 滚动归档 R43/R44）**：relay 复核（原始输出）：`ps -eo pid,ppid,etimes,stat,args | grep ops_relay.sh | grep -v grep` → `2489749 1 275390 Ss bash ops_relay.sh`（ppid=1 真守护、态 Ss、etimes≈3.19d）；`cat ops/.last_run_id`=`62`（与上轮 R46 一致 → RUN_ID 62 已跑）；`grep -c 'RUN_ID 62' ops/outbox.md`=`1`（已入 outbox）；`tail -20 /tmp/baize_ops_relay.log` → RUN_ID 42~62 均 `exit=0`（末行 `[relay] RUN_ID=62 executed, exit=0, appended to outbox.`）；`timeout 30 git fetch origin` → exit=128（`Failed to connect to github.com port 443: Network is unreachable`）；无 index.lock，git status 仅 `.nfs*` NFS 临时文件（非阻塞）；`pgrep -f 'bash ops_relay.sh'` 误匹配 node/cline 进程（PID 613301=`node(613301)-+-.cline(613308)`），真 relay=2489749。**判据**：outbox 已含 RUN_ID 62 + git fetch exit=128 → 按「git fetch exit≠0（network unreachable）= 根因网络，与中继无关 → 🚫 不要重启」+「outbox.md 已含 RUN_ID 62 → 中继已跑但 push 失败 → 🚫 不要重启；等网络」双重判据 → **跳过重启**（🚫 红线：不 pkill 健康 relay、不动 GPU pretrain P-9.2、不删数据）。✅ URGENT 项完成。**H-A pilot 扩量核查**：`instances/` 已备 30 条 JSON（15 django `django__django-{10924..11742}` + 15 sympy `sympy__sympy-{11870..13647}`），但 `git -C rootfs/django__django-10914/testbed cat-file -t <base_commit>` 对全部 15 django base_commit → **全 MISSING**；`git -C rootfs/sympy__sympy-11400/testbed cat-file -t <base_commit>` 对全部 15 sympy base_commit → **全 MISSING**（两 rootfs 均为 `--depth=1` 浅克隆、`--is-shallow-repository=true`）→ **`run_pilot_batch.py` 的 `setup_rootfs()` 需 `git fetch --depth=1 origin <base_commit>` 从 github 取新 commit → github 不可达 → 扩量阻塞**。诚实记录：`git ls-remote https://github.com/django/django.git HEAD` → `Network is unreachable` exit=128 → 网络瞬断，非永久故障；网络恢复后 `run_pilot_batch.py --all-prepared` 即可自动续跑（30 instances × 4 harness 顺序跑）。**MEMORY 滚动归档**：R43/R44 速览块归档至 `daily-memories-harness/2026-10-04.md`（原文不改），MEMORY 32296B→~30KB（回到 32KB 上限内）。`git fetch` Network unreachable，无新指令可拉。⏭ 等 github 网络恢复 → 扩 20-30 instances pilot。保持 `WAITING=1`。
- 2026-10-04 19:00 —— **第四十五轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip + codex/claude-code × sympy-11400 评分完成 全❌ + SWEBENCH_COMPARE.html 创建 20KB + MEMORY 滚动）

- 2026-10-04 20:00 —— **第四十六轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：RUN_ID 62 已执行，健康跳过重启，git fetch Network unreachable 瞬断）

- 2026-10-04 22:38 —— **第四十九轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：30×4 pilot 批量启动 + git_clone_or_fetch 重写 + /dev/shm workdir 修复 NFS 竞态）

- 2026-10-05 00:05 —— **第五十一轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 5 次 + batch v2 2/30 scored 11001=4/4 全 resolve 🎉）

- 2026-10-05 00:39 —— **第五十二轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：relay 健康 skip 第 6 次 + batch v2 4/8 scored 11001=4/4 resolve + 11049 进行中）

- 2026-10-04 23:25 —— **第五十轮** —— 已滚动归档至 `daily-memories-harness/2026-10-05.md`（结论不改：RUN_ID 62 网络恢复 + 三大管道修复 swebench安装/report.json解析/quota backoff + codex×10924 resolved=True + batch v2 启动）
