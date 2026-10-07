# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A 30×5 harness cross-eval (kimi-k2.6-cloud, serial=1) — cline-patched×30 ✅ 60.0% · codex×30 ✅ 46.7% · opencode×30 ✅ 50.0% · claude-code×30 ✅ 44.8% · deepseek-harness×15/30 🔄 RUNNING (7 res/8 pbf = 46.7%, chain PID 1292346 → run_serial PID 3587539, on inst 16 sympy__sympy-11870). gw_proxy healthy (PID 3175038, port 9090) + gw_proxy_dsh healthy (PID 1307655, port 9091).
已完成:       H-B 5×源码分析 · H-D 对比矩阵 · H-C 评测调研 · kimi serial runner · cline-patched×30 (60.0%) · codex×300 stopped (43/108/149) · opencode×30 (50.0%) · claude-code×30 (44.8%) · deepseek-harness×15/30 (7 res/8 pbf = 46.7%, RUNNING) · SWEBENCH_COMPARE.html (30×5, 135 entries, 67 resolved)
当前动作:     R155: deepseek-harness×30 progress check (15/30 done, 7 resolved/8 pbf = 46.7%) → SWEBENCH_COMPARE.html regenerated (15799B, 135 entries, 67 resolved) → R147-R153 archived → commit+push
下一步:       [AUTO] deepseek-harness×15 remaining (~75min at ~5min/inst) → chain auto-regen final HTML (5 rows complete) → [next wake] verify final results → final commit+push
阻塞:         无硬阻塞. deepseek-harness toolchain working, last 7 instances all pbf (11283-11742).
ERROR_COUNT:  0
```

## 🆕 第一百五十五轮速览（2026-10-07 21:14）— deepseek-harness×30 progress 15/30 (7 res/8 pbf = 46.7%) + SWEBENCH_COMPARE.html regenerated (15799B, 135 entries, 67 resolved) + R147-R153 archived

- 🔄 **deepseek-harness×30 progress**：chain script (PID 1292346) running, run_serial PID 3587539 (etimes ~6663s = ~111min), 15/30 done, **7 resolved / 8 patch-but-failed = 46.7%** (on 15 scored)。
  - Instances 1–15: 10924(res) → 11001(res) → 11019(pbf) → 11039(res) → 11049(res) → 11099(res) → 11133(res) → 11179(res) → 11283(pbf) → 11422(pbf) → 11564(pbf) → 11583(pbf) → 11620(pbf) → 11630(pbf) → 11742(pbf)。
  - Current instance: sympy__sympy-11870 (inst 16, first sympy instance)。
  - **Pace**: avg ~300s/inst → 15 remaining ≈ **~75 min** to completion。
  - Note: rate dropped from 77.8% (R153, 9 done) → 58.3% (R154, 12 done) → 46.7% (R155, 15 done) — last 7 instances all pbf。
- 📈 **SWEBENCH_COMPARE.html regenerated**：15799 bytes, 30 instances, 135 entries (cline 30 + codex 30 + opencode 30 + claude-code 30 + deepseek 15), 67 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 29/30 | 13 | 16 | 1 | 44.8% |
  | deepseek-harness | 15/30 | 7 | 8 | 0 | 46.7% (so far) |
- ✅ **gw_proxy 健康**：PID 3175038 (port 9090, HTTP 200) + gw_proxy_dsh PID 1307655 (port 9091, HTTP 200)。
- ✅ **chain script 健康**：PID 1292346 (etimes ~32996 = ~9.2h)，正在跑 deepseek-harness×30 (last step before final HTML regen)。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=17702B（17.3KB，≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=17.3KB（归档 ~13KB R147-R153 → daily-memories-harness/2026-10-07.md）。
- ⏭ **下一步**：chain script 自动跑 deepseek-harness×15 remaining (~75min) → final regen HTML (5 rows complete) → [next wake] verify final results → final commit+push。保持 `WAITING=1`。


## 🆕 第一百五十四轮速览（2026-10-07 20:34）— deepseek-harness×30 progress 12/30 (7 res/5 pbf = 58.3%) + SWEBENCH_COMPARE.html regenerated (15719B, 132 entries, 67 resolved)

- 🔄 **deepseek-harness×30 progress**：chain script (PID 1292346) running, run_serial PID 3587539 (etimes ~4500s = ~75min), 12/30 done, **7 resolved / 5 patch-but-failed = 58.3%** (on 12 scored)。
  - Instances 1–12: 10924(res) → 11001(res) → 11019(pbf) → 11039(res) → 11049(res) → 11099(res) → 11133(res) → 11179(res) → 11283(pbf) → 11422(pbf) → 11564(pbf) → 11583(pbf)。
  - Current instance: django__django-11620 (inst 13, run_single PID 484912, etimes ~97s)。
  - **Pace**: avg ~300s/inst → 18 remaining ≈ **~90 min** to completion。
  - Note: resolve rate dropped from 77.8% (R153, 9 done) to 58.3% (12 done) — last 4 instances all pbf。
- 📈 **SWEBENCH_COMPARE.html regenerated**：15719 bytes, 30 instances, 132 entries (cline 30 + codex 30 + opencode 30 + claude-code 30 + deepseek 12), 67 resolved。
- 📊 **当前 5-way 对比**（kimi_pilot_results.json, 同 30 instances）：
  | harness | scored | resolved | pbf | blk | rate |
  |---|---|---|---|---|---|
  | cline-patched | 30/30 | 18 | 12 | 0 | 60.0% |
  | codex (30-subset) | 30/30 | 14 | 16 | 0 | 46.7% |
  | opencode | 30/30 | 15 | 15 | 0 | 50.0% |
  | claude-code | 30/30 | 13 | 16 | 1 | 44.8% |
  | deepseek-harness | 12/30 | 7 | 5 | 0 | 58.3% (so far) |
- ✅ **gw_proxy 健康**：PID 3175038 (port 9090, HTTP 200) + gw_proxy_dsh PID 1307655 (port 9091, HTTP 200)。
- ✅ **chain script 健康**：PID 1292346 (etimes ~30885 = ~8.6h)，正在跑 deepseek-harness×30 (last step before final HTML regen)。
- 📦 **体积自检**：TASK=31476B（30.7KB，≤32KB ✓）/ MEMORY=~29.5KB（≤32KB ✓）。📦 体积：TASK=30.7KB / MEMORY=29.5KB（归档 0KB）。
- ⏭ **下一步**：chain script 自动跑 deepseek-harness×18 remaining (~90min) → final regen HTML (5 rows complete) → [next wake] verify final results → final commit+push。保持 `WAITING=1`。


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
- 2026-10-07 19:59 —— **第一百五十三轮** —— deepseek-harness×30 progress 9/30 (7 res/2 pbf = 77.8%) → SWEBENCH_COMPARE.html regenerated（15608B, 129 entries, 67 resolved）→ commit+push。📦 体积：TASK=30.7KB / MEMORY=27.2KB（归档 0KB）。
- 2026-10-07 20:34 —— **第一百五十四轮** —— deepseek-harness×30 progress 12/30 (7 res/5 pbf = 58.3%) → SWEBENCH_COMPARE.html regenerated（15719B, 132 entries, 67 resolved）→ commit+push。📦 体积：TASK=30.7KB / MEMORY=29.5KB（归档 0KB）。
- 2026-10-07 21:14 —— **第一百五十五轮** —— deepseek-harness×30 progress 15/30 (7 res/8 pbf = 46.7%) → SWEBENCH_COMPARE.html regenerated（15799B, 135 entries, 67 resolved）+ R147-R153 archived to daily → commit+push。📦 体积：TASK=30.7KB / MEMORY=17.3KB（归档 ~13KB → daily-memories-harness/2026-10-07.md）。
