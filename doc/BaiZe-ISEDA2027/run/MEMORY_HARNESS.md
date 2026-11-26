# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **用户令 · 2026-11-26 (F) — 本地 build 升级 7-harness + cline 降本组合 + SWE-bench Verified doubao-pro 7-way 重做**
>
> **用户原话**：「安排 Harness 本地 build 升级 7-harness（没有开源的就直接装最新版），对于 cline 则采用"关掉 checkpoint、思维链等级设为 low、压缩机制设为 basic"这个降本组合，用 SWE-bench Verified + doubao-pro 重做 7-way 评测」
>
> **7 个 harness 升级清单**（源码已在 `/nas_train/app.e0031982/harness/` 下，已 git pull 到最新）：
>
> | Harness | 源码路径 | 当前版本 | 升级后版本 | 升级方式 |
> |:--|:--|:--|:--|:--|
> | cline | `/nas_train/app.e0031982/harness/cline` | 3.0.51 | 3.0.76 | `bun install && bun -F @cline/cli build`，然后 `bun link`（apps/cli） |
> | codex | `/nas_train/app.e0031982/harness/codex` | 0.94.0 | 0.172.0 | `npm install -g @openai/codex@0.172.0`（⚠️ 0.95+ 改用 Responses API，需测 gw_proxy 兼容性） |
> | opencode | `/nas_train/app.e0031982/harness/opencode` | 1.18.27 | 2.4.1 | 源码 build：`bun install && bun run build`，更新全局链接 |
> | claude-code | `/nas_train/app.e0031982/harness/claude-code` | 2.1.197 | 2.1.332 | `npm install -g @anthropic-ai/claude-code@2.1.332` |
> | hermes | `/nas_train/app.e0031982/harness/hermes-agent` | git.0e21933 | git.e0dcc39 | 源码已 pull，重新安装（`pip install -e .` 或按项目方式 rebuild） |
> | pi | `/nas_train/app.e0031982/harness/pi` | 0.2.15 | 1.6.1 | 源码 build：`bun install && bun run build`，更新全局链接 |
> | deepseek-harness | `/nas_train/app.e0031982/harness/deepseek-harness` | 0.1.5rc1 | 0.2.2rc2 | `pip install --target /nas_train/app.e0031982/harness_work/dsh_sdk deepseek-harness-sdk`（阿里镜像有 0.2.2rc2） |
>
> **cline 降本组合**（已在 `run_single.py` + `run_harness.py` 改好）：
> - `--compaction basic`
> - `--thinking low`
> - checkpoint 已在源码 `defaults.ts:25` 关闭（`enabled: false`）
>
> **执行步骤**：
> 1. 按上表逐个升级 7 个 harness，每个升级后验证 `--version` 或 `--help` 能跑
> 2. 升级完成后，用 `launch_doubao_7way.sh` 启动 SWE-bench Verified 500 题 × 7 路 × doubao-pro 评测
> 3. **删除旧 doubao-pro predictions**（`predictions_doubao_pro/` 下的所有文件），全新开始
> 4. predict 完成后 eval + 生成报告（`gen_report_doubao_pro_7way.py`）
> 5. 报告中包含各 harness **升级后的版本号**
>
> **纪律**：
> - 一次只做一个任务：先升级，再评测
> - 升级时如果某个 harness build 失败，记录错误，跳过该 harness 继续下一个，不要卡住
> - codex 0.95+ 的 Responses API 变化：如果 codex 升级后与 gw_proxy 不兼容，先记录问题，降回 0.94.0 继续评测
> - 不碰 MM、不碰其他线

> ✅ **用户令 · 2026-11-26 (E) — 停止 cline 重跑，停下待命** · ✅ 已闭环
>
> **用户原话**：「先不开 TB，让 harness 看到令就杀掉 cline 重跑，停下待命」
>
> **执行**：cline-patched predict PID 1755547 已 kill✅·0 eval/predict 进程·不启动 TB-2.1·待命

> 🆕 **用户令 · 2026-11-25 (D) — 停止 SWE-bench MM，专心做 SWE-bench Verified，一次只做一个任务**
>
> **用户原话**：「把 SWE-bench MM 的评测停下来吧，专心把 SWE-bench Verified 做好，一次只有一个任务，不要再出错了。」
>
> **背景**：harness agent 违反了「🚫 不碰 MM」的纪律，在 MM prediction 文件因灾误删丢失后自作主张全量重跑 MM，浪费了资源。用户决定砍掉 MM，集中精力。
>
> **执行**：cline-patched predict PID 1755547 已 kill✅·0 eval/predict 进程·不启动 TB-2.1·待命
> 3. **只盯 SWE-bench Verified doubao-pro 7-way predict**，等它跑完后 eval + 报告
> 4. **以后一次只做一个任务**，不要并行多个 benchmark

> 🆕 **用户令 · 2026-11-25 (C) — deepseek-harness SDK 已恢复，重新 predict deepseek-harness 路**
>
> **背景**：doubao-pro 7-way 启动后 deepseek-harness 跑完 500 题全 0 patch，根因 = `/tmp/dsh_sdk/` 被清空（机器重启或 /tmp 清理）→ `available()` 返回 False → 每题秒退 rc=2。
>
> **已修复**：运维已重新 `pip install --target /tmp/dsh_sdk deepseek-harness-sdk`，`available()` 已恢复 True。
>
> **你接手后**：
> 1. 先验证：`python3 -c "import sys; sys.path.insert(0,'/tmp/dsh_sdk'); from run_harness import DRIVERS; print(DRIVERS['deepseek-harness'].available())"` 应输出 `True`
> 2. **删除 deepseek-harness 的旧空 predictions**：`rm -f swebench_verified_full/predictions_doubao_pro/deepseek-harness__*.json`
> 3. **删除旧 progress 文件**：`rm -f swebench_verified_full/reports/progress_doubao_pro_deepseek-harness.json`
> 4. **重新 predict**（与其他 6 路并行，不影响它们）：
>    ```bash
>    cd swebench_verified_full
>    HARNESS_MODEL=doubao-seed-2.0-pro-cloud \
>    MODEL_SUFFIX=doubao-seed-2.0-pro-cloud \
>    PRED_SUBDIR=predictions_doubao_pro \
>    WORKDIR_TAG=_doubao_pro \
>    EVAL_TAG=doubao_pro_ \
>    GW_USAGE_LOG=/tmp/gw_proxy_usage.jsonl \
>    no_proxy="127.0.0.1,localhost,agi-gateway.cxmt.com" \
>    PATH="$HOME/.bun/bin:$PATH" \
>    nice -n 10 nohup python3 run_verified_full.py predict \
>      --harness deepseek-harness --workers 1 \
>      > ../logs_doubao_pro/deepseek-harness_doubao_pro_rerun.log 2>&1 &
>    ```
> 5. 确保 gw_proxy_dsh（端口 9091）在运行（doubao key + /cloud upstream）；如果不在，用 `launch_doubao_7way.sh` 的逻辑重启它
> 6. **持久化修复**：把 SDK 从 `/tmp/dsh_sdk` 搬到 NFS 持久路径：
>    ```bash
>    cp -a /tmp/dsh_sdk /nas_train/app.e0031982/harness_work/dsh_sdk
>    ```
>    然后在 `run_harness.py` 的 `DeepseekHarnessDriver._SDK_PATH` 改为 `/nas_train/app.e0031982/harness_work/dsh_sdk`（同步改 agent-arena 仓库的副本）。这样机器重启后不再丢失。
> 7. predict 完成后跑 eval + 合并结果（与其他 6 路一起 eval 也可以）
>
> **纪律**：不碰其他 6 路正在运行的 predict 进程；不碰 MM。

> 🆕 **用户令 · 2026-11-25 (B) — 评测脚本签入 agent-arena 仓库，交由 harness 维护**
>
> **用户原话**：「安排 harness 把它的评测脚本签入这个仓库：/nas_train/app.e0031982/code/agent-arena，写好 README，以后这个仓库交由 harness 维护」
>
> **已执行**：
> 1. 33 个核心脚本已签入 `/nas_train/app.e0031982/code/agent-arena`（commit `a431e3c`，已 push）
> 2. 目录结构：`proxy/` + `swebench_verified/` + `swebench_mm/` + `terminalbench/` + `reports/`
> 3. README.md 已写好（概述 / 运行条件 / 运行说明 / 架构图 / 数据流 / 评测纪律）
> 4. .gitignore 已配置（排除运行时产物、API Key、临时文件）
> 5. 排除了数百个一次性脚本（`incr_eval_R*.py` / `cleanup_empty_patches_R*.py` 等），只签入可复用核心
>
> **以后维护规则**：
> - 评测脚本的更新和新增一律在 `agent-arena` 仓库进行
> - `super_intelligence_2035` 仓库的 `harness/` 目录保持运行时副本（loop 读写），但**不再作为脚本权威源**
> - harness agent 每次 pull `agent-arena` 获取最新脚本，push 改动到 `agent-arena`
> - API Key / 凭证永不入库（.gitignore 已覆盖）

> 🆕 **用户令 · 2026-11-25 (A) — 停止当前 SWE-bench Verified 评测，改用 doubao-pro 重测全量 500×7 + 记录 token**
>
> **用户原话**：「安排 harness 停止手头的评测，重新开始：使用 doubao-pro 模型，从 SWE-bench Verified 开始重测，记录 token 数，7-way 并发（豆包白天用户量很小）。已经基本 predict 完成的 SWE-bench MM 不受影响，继续做完。」
>
> **执行**：cline-patched predict PID 1755547 已 kill✅·0 eval/predict 进程·不启动 TB-2.1·待命
>
> **第一步 — 停止当前 SWE-bench Verified 工作（不动 MM）**：
> 1. `kill` nightly_rerun_watcher（PID 2791637，sleeping until 21:00）—— 直接 kill，不触发 21:00 窗口
> 2. `kill` 任何正在运行的 `run_verified_full.py predict` / `rerun_infra_verified.py` / `incremental_eval_merge.py` 进程
> 3. `kill` 旧的 gw_proxy 进程（9090/9091/9092）—— 它们配的是 glm-5.3-flash key
> 4. 🚫 **不碰** MM 相关进程（端口 9095+ 的 mm_proxy、`run_mm_2x3.py predict`）
>
> **第二步 — 启动 doubao-pro 7-way**：
> 1. 已创建启动脚本：`harness/launch_doubao_7way.sh`
> 2. 直接运行：`bash harness/launch_doubao_7way.sh`
> 3. 脚本自动完成：API probe → 重启 3 个 gw_proxy（doubao key + /cloud upstream）→ 更新 5 个 harness config → 截断 usage sidecar → 7 路并行 predict
> 4. 模型 = `doubao-seed-2.0-pro-cloud`，upstream = `http://agi-gateway.cxmt.com/cloud`
> 5. 预测目录 = `predictions_doubao_pro/`，eval tag = `doubao_pro_`，workdir tag = `_doubao_pro`
> 6. **白天运行**（doubao 白天用户量小，无需夜间窗口）
> 7. **token 记录已部署**：gw_proxy.py / gw_proxy_dsh.py / run_single.py / incremental_eval_merge.py 已改造完成，每题 predictions JSON 带 `usage: {input_tokens, output_tokens, total_tokens, n_api_calls}`
>
> **第三步 — MM 2×3 继续**：
> 1. MM 的 cline/opencode × kimi 两路 retry 进程已消失（R3009 记录），需重启
> 2. 用 `bash harness/swebench_mm/launch_mm_2x3_full.sh` 重启剩余路由（会跳过已完成的）
> 3. MM 使用独立端口 9095+，不受 doubao gw_proxy 重配影响
>
> **第四步 — 监控**：
> - `bash harness/launch_doubao_7way.sh status` 查 7 路进度 + token 统计
> - 每路 500 题 × 7 = 3500 predict；doubao-pro 预计比 glm53 快（白天无 429）
> - predict 全部完成后，跑 eval + 生成报告
>
> **纪律**：
> - 硬护栏不变（guard PID931671 常开、nice19/ionice3/OMP8、docker eval mem128g/cpu16）
> - 不碰 pretrain/data/vision/zhulong
> - 🚫 不碰 MM 进程和 MM 预测文件
> - glm-5.3-flash 的旧 predictions（`predictions_glm53/`）和 eval 结果保留不删，作为对照

## 📊 进度快照

PHASE:        11-26令(E)执行完毕·cline predict已kill·停下待命·等后续指令
已完成:       H-B OK·Gate7/7·TB-2.1 7路 COMPLETE·SWE-bench Verified glm53+doubao-pro 7路 predict+eval·token 记录改造✅·launch_doubao_7way.sh✅·doubao-pro 7way predict 7/7 COMPLETE✅·eval 7/7 COMPLETE✅·报告✅·dsh SDK修复✅·MM已KILL✅·agent-arena repo✅·**令E✅**(cline predict killed·停下待命)
当前动作:     idle·停下待命·0 eval/predict进程·guard PID931671 LIVE(501583s≈5.8d)·gw_proxy 3进程LIVE(9090/9091/9092·PID 623606/623610/623695·~90201s≈25.1h)·资源OK(load26.42/224=11.8%·mem686G/2TB avail1095G)
下一步:     待运维新指令（所有 11-25 令 A/B/C/D + 11-26 令 E 已全部闭环）
阻塞:         无（git merge origin/main 被 1804 个 ZhuLong untracked 文件阻挡·origin/main 无 harness 变更·不影响本线）
ERROR_COUNT:  0
 体积: TASK~26.4KB / MEMORY≈25.0KB（归档H-009~H-017后·均<32KB✅）

  SWE-bench Verified Pass% (glm53 口径, 保留对照): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
  SWE-bench Verified Pass% (doubao-pro 口径): opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%
  SWE-bench Verified doubao-pro predict: 7/7路COMPLETE(cline494/opencode498/hermes498/pi494/cc500/dsh499/codex500·3500/3500=100%)
  SWE-bench Verified doubao-pro eval: 7/7路COMPLETE✅(opencode323/495·cline321/491·hermes302/489·cc297/493·pi270/483·codex218/464·dsh130/299)
  SWE-bench Multimodal: **已停(令D 2026-11-25)**·MM数据保留不删
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%

## 流水

> 📦 #H-001~#H-003 已归档 → daily-memories-harness/2026-11-25.md「归档」节（2026-11-26 07:55 滚出）


> 📦 #H-004~#H-008 已归档 → daily-memories-harness/2026-11-26.md「归档 2026-11-26 09:20」节（2026-11-26 09:20 滚出）

> 📦 #H-009~#H-017 已归档 → daily-memories-harness/2026-11-26.md「归档 #H-009~#H-017」节（2026-11-26 10:36 滚出）
> #H-019（2026-11-26 05:58, 监控巡检+**hermes+cline-patched eval COMPLETE✅→4 eval✅+2 eval LIVE**·doubao-pro 7way predict 1路active(codex491/500 PID820223 recovering from quota-block)+6路COMPLETE·**4 eval✅**(opencode 323/495=64.6% at 05:42·cline-patched 321/491=65.4% at 05:56·hermes 302/489=61.8% at 05:56·dsh 130/299=43.5%)+**2 eval LIVE**(CC PID2879750 407/493 report.json ~43min·pi PID2879751 293/483 report.json ~43min·nice19·mem128g/cpu16·9 Docker containers)·**duplicate cleanup** at 05:50: CC eval 3→1(pi 2→1) killed 2995426+3092926(cc)+3092927(pi)+2 screen sessions→load 103→53·codex quota-blocked at 05:51 recovered at 05:57(no-patch 376.6s)·token sidecar ~53k lines·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE·资源OK(load62/224=27.7%·mem681G/2015G avail1100G·0 high-CPU·pretrain step7.39s≤7.4s✅)·MM已停(令D)·下一步:①CC eval完成(ETA~06:10-06:15·86rem) ②pi eval完成(ETA~06:30-06:40·190rem) ③codex predict完成(9rem·ETA~06:15-06:45)→setsid启动codex eval ④7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-020（2026-11-26 06:20, 监控巡检+**codex predict COMPLETE✅(500/500)→codex eval STARTED**·doubao-pro 7way predict 7/7路COMPLETE(cline494/opencode498/hermes498/pi494/cc500/dsh499/codex500·3500/3500=100%)·**4 eval✅**(opencode 323/500=64.6%·cline-patched 321/500=64.2%·hermes 302/500=60.4%·dsh 130/500=26.0%)+**3 eval LIVE**(CC PID2879750 485/493 report.json sphinx-7985 stuck@23min~timeout·pi PID2879751 440/483·codex PID3809606 10/464 just-started·nice19·mem128g/cpu16·~13 Docker containers)·codex predict COMPLETE at 06:16(500/500·merged 464/500 non-empty·4 quota-block)·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·token sidecar ~53k lines·资源OK(load~60/224=27%·mem681G/2015G avail1100G·0 high-CPU·pretrain step7.39s≤7.4s✅)·MM已停(令D)·下一步:①CC eval完成(sphinx-7985 timeout~7min)→检查eval JSON ②pi eval完成(ETA~06:40-06:50) ③codex eval完成(ETA~07:50-08:30·464 patches) ④7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-021（2026-11-26 07:17, **doubao-pro 7way eval 7/7 COMPLETE✅ + 报告已生成✅**·CC eval JSON 06:27(297/493=59.4%)·pi eval JSON 06:37(270/483=54.0%)·codex eval JSON 07:06(218/464=43.6%)·lingering codex Docker container killed·**7路最终Pass%**: opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%·报告`report_harness_doubao_pro_7way_swebench_tb_zh.html`已生成(7083B·0script/0外链✅)·token统计:7路合计~355k calls/~5.17B input/~99M output·guard PID931671 LIVE·gw_proxy 3进程LIVE·资源OK(load~42/224=19%·0 Docker·0 eval/predict进程)·所有11-25令A/B/C/D全部闭环·WAITING→0·下一步:待运维新指令）

> #H-022（2026-11-26 07:25, 例行巡检·**全部完成·idle**·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load24/224=11%·mem680G/2015G avail1101G·pretrain step7.39s≤7.4s✅)·git已pull up-to-date·**任务书归档**:11-24令+11-23令+11-19MM令→ARCHIVE(归档2026-11-26节)·TASK 32432B→16994B✅·新增11-25令A/B/C/D摘要·MEMORY 30.6KB(OK)·token sidecar 52884 lines·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-023（2026-11-26 07:40, 例行巡检·**idle·健康**·git pull up-to-date(无新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load26.64/224=12%·mem680G/2015G avail1102G·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·agent-arena repo 3 commits(a1fc485/a431e3c/a50291c)·TASK 27.0KB/MEMORY 31.1KB(均<32KB✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-024（2026-11-26 07:55, 例行巡检·**idle·健康**·git merge origin/main fast-forward(仅posttrain变更·无harness新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE(492019s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load25/224=11%·mem680G/2TB avail1.1T·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅(/nas_train/app.e0031982/harness_work/dsh_sdk)·agent-arena repo✅·TASK 27.0KB/MEMORY~28.5KB(归档H-001~H-003后·<32KB✅)·research日报2026-11-26已查(ShellBench:模型>harness影响·建议harness-only消融+报token成本·我们已报token✅·AIChipBench:held-out测试条件·非直接可执行)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-025（2026-11-26 08:05, 例行巡检·**idle·健康**·git fetch+merge origin/main: Already up to date(无新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE(492601s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~81220s≈22.6h)·资源OK(load23.87/224=11%·mem680G/2TB avail1.1T·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·TASK 27.0KB/MEMORY~29.8KB(均<32KB✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）
> #H-026（2026-11-26 08:15, 例行巡检·**idle·健康**·git fetch: Already up to date(无新指令)·自检(内存10-30令):0 harness eval/predict进程·gw_proxy 3进程RSS=25-44MB(远<50GB阈值✅)·guard 3.5MB✅·自检(CPU 11-02令):load26.70/224=12%(远<80%阈值✅)·0 harness进程>8000%CPU✅·guard PID931671 LIVE(493116s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~81736s≈22.7h)·0 Docker·mem681G/2TB avail1.1T·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·TASK 27.0KB/MEMORY~30.0KB(均<32KB✅)·research日报2026-11-26已查(无新可执行建议·ShellBench token成本建议已落地✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-027（2026-11-26 09:20, **令E执行完毕**·**cline-patched predict PID 1755547 已 kill✅**·0 eval/predict 进程确认·不启动 TB-2.1·停下待命·自检(内存10-30令):0 harness eval/predict进程✅·自检(CPU 11-02令):load~24/224=11%(远<80%✅)·gw_proxy 3进程LIVE(9090/9091/9092·PID 623606/623610/623695)·guard PID931671 LIVE·0 Docker·mem680G/2TB avail1.1T·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·体积维护:H-004~H-008归档·TASK~27.0KB/MEMORY~27.5KB(均<32KB✅)·所有11-25令A/B/C/D+11-26令E已闭环·WAITING:1·下一步:待运维新指令）

> #H-028（2026-11-26 10:12, 例行巡检·**idle·健康**·git fetch origin OK·merge origin/main 被 1804 个 ZhuLong trace_deepreads untracked 文件阻挡(origin/main 6 commits 无 harness 变更·不影响本线·ZhuLong agents 会处理自己的 merge)·自检(内存10-30令):0 harness eval/predict进程·gw_proxy 3进程RSS=23-44MB(远<50GB阈值✅)·guard 3.5MB✅·自检(CPU 11-02令):load24.56/224=11%(远<80%阈值✅)·0 harness进程>8000%CPU✅·guard PID931671 LIVE(500100s≈5.8d)·gw_proxy 3进程LIVE(9090/9091/9092·PID 623606/623610/623695·~88707s≈24.6h)·0 Docker·mem682G/2TB avail1098G·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7152B✅·token sidecar 53306 lines·dsh_sdk持久化✅(/nas_train/app.e0031982/harness_work/dsh_sdk)·agent-arena repo✅·TASK 26.4KB/MEMORY 27.6KB(均<32KB✅)·dedup修复(重复归档指针删除)·research日报2026-11-26已查(无新可执行建议)·所有11-25令A/B/C/D+11-26令E已闭环·WAITING:1·下一步:待运维新指令）

> #H-029（2026-11-26 10:36, 例行巡检·**idle·健康**·git fetch origin OK·origin/main 5 commits ahead(全designflow·无harness变更)·merge被ZhuLong untracked文件阻挡(不影响本线)·自检(内存10-30令):0 harness eval/predict进程·gw_proxy 3进程RSS=23-44MB(远<50GB阈值✅)·guard 3.5MB✅·自检(CPU 11-02令):load26.42/224=11.8%(远<80%阈值✅)·0 harness进程>8000%CPU✅·guard PID931671 LIVE(501583s≈5.8d)·gw_proxy 3进程LIVE(9090/9091/9092·PID 623606/623610/623695·~90201s≈25.1h)·0 Docker·mem686G/2TB avail1095G·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7152B✅·token sidecar 53306 lines·dsh_sdk持久化✅(/nas_train/app.e0031982/harness_work/dsh_sdk)·agent-arena repo✅·体积维护:H-009~H-017归档·TASK 26.4KB/MEMORY~25.0KB(均<32KB✅)·research日报2026-11-26已查(无新可执行建议·ShellBench token成本建议已落地✅)·所有11-25令A/B/C/D+11-26令E已闭环·WAITING:1·下一步:待运维新指令）

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（同一 NFS · git pull 后各线共享）
- **doubao-pro 启动脚本**：`run/harness/launch_doubao_7way.sh`
- **doubao-pro 预测目录**：`run/harness/swebench_verified_full/predictions_doubao_pro/`
- **doubao-pro 评测目录**：`run/harness/swebench_verified_full/reports/eval_doubao_pro_*.json`
- **glm53 旧预测（对照）**：`run/harness/swebench_verified_full/predictions_glm53/`
- **token sidecar**：`/tmp/gw_proxy_usage.jsonl`
- **报告生成器**：`run/harness/gen_report_glm53_7way.py` + `run/harness/gen_cline_special.py`
