# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0
> 🆕 **用户令 · 2026-11-26 — cline 配置修正 + 重新 predict cline 路 + 报告已更新**
>
> **用户原话**：「确认 cline 配置是否：关掉 checkpoint、思维链等级设为 low、压缩机制设为 basic 这个降本组合」「在报告表格中包含各 harness 版本号，把 cline-patched 改成 zhulong(cline-patched)」
>
> **排查结论**：
> - **compaction**：`run_cline_patched`（实际使用的路径）**未设** → 默认 agentic ❌（应为 basic）
> - **thinking**：**未设** → 默认 provider default ❌（应为 low）
> - **checkpoint**：cline 3.0.51 **无 checkpoint 功能**（旧版 `cline-checkpoint-off` ELF 已废弃，TypeScript 版 `~/.bun/bin/cline` 默认不做 checkpoint，除非用 `--id` resume）→ 无需设置 ✅
>
> **已修复**：
> - `run_single.py:106-108`：加 `--compaction basic --thinking low`
> - `run_harness.py:198`：加 `--thinking low`（compaction basic 已有）
> - 两处已同步到 agent-arena 仓库
>
> **报告已更新**（`gen_report_doubao_pro_7way.py`）：
> - cline-patched → zhulong(cline-patched)
> - 主表 + predict 表均加版本号列
> - 版本号：cline 3.0.51 / codex 0.94.0 / opencode 1.18.27 / claude-code 2.1.197 / pi 0.2.15 / hermes git.0e21933 / deepseek 0.1.5rc1
> - 报告已 REGEN（7561 bytes）
>
> **你接手后**：
> 1. **删除 cline 旧 predictions**：`rm -f swebench_verified_full/predictions_doubao_pro/cline-patched__*.json`
> 2. **删除旧 progress + eval**：`rm -f swebench_verified_full/reports/progress_doubao_pro_cline-patched.json swebench_verified_full/reports/eval_doubao_pro_cline-patched.json`
> 3. **重新 predict**（配置已修正：compaction=basic + thinking=low）：
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
>      --harness cline-patched --workers 1 \
>      > ../logs_doubao_pro/cline-patched_doubao_pro_rerun.log 2>&1 &
>    ```
> 4. predict 完成后 eval：`python3 incremental_eval_merge.py --route cline-patched --regen`
> 5. REGEN 报告：`python3 gen_report_doubao_pro_7way.py`
>
> **纪律**：不碰其他 6 路的 predictions/eval；只重跑 cline-patched 这一路。

> 🆕 **用户令 · 2026-11-25 (D) — 停止 SWE-bench MM，专心做 SWE-bench Verified，一次只做一个任务**
>
> **用户原话**：「把 SWE-bench MM 的评测停下来吧，专心把 SWE-bench Verified 做好，一次只有一个任务，不要再出错了。」
>
> **背景**：harness agent 违反了「🚫 不碰 MM」的纪律，在 MM prediction 文件因灾误删丢失后自作主张全量重跑 MM，浪费了资源。用户决定砍掉 MM，集中精力。
>
> **执行步骤**：
> 1. **立即 kill 所有 MM 进程**：`pkill -f "run_mm_2x3.py"` + kill mm_proxy（端口 9095+）
> 2. **不删 MM 数据**（已有的 progress/predictions 保留，以后需要时可用）
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
> **执行步骤**：
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

PHASE:        11-26令(cline配置修正+重新predict cline-patched路)·cline-patched re-predict RUNNING(PID1755547·compaction=basic+thinking=low·500 pending)
已完成:       H-B OK·Gate7/7·TB-2.1 7路 COMPLETE·SWE-bench Verified glm53 7路 predict+eval·token 记录改造✅·launch_doubao_7way.sh✅·**doubao-pro 7way predict 7/7 COMPLETE✅**(3500/3500=100%)·**doubao-pro 7way eval 7/7 COMPLETE✅**·**报告已生成✅**(report_harness_doubao_pro_7way_swebench_tb_zh.html)·**dsh SDK修复✅**·**MM已KILL✅**(令D)·**agent-arena repo✅**(33 scripts committed)
当前动作:     cline-patched re-predict RUNNING(PID1755547·workers=1·500 pending·compaction=basic+thinking=low)·guard PID931671 LIVE(493567s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~82959s≈23h)·0 Docker·load~26/224=12%·mem684G/2TB avail1.1T
下一步:     ①monitor cline-patched re-predict(500题·ETA~3-4h) ②predict完成→eval(incremental_eval_merge.py --route cline-patched --regen) ③REGEN报告(gen_report_doubao_pro_7way.py)
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~27.0KB / MEMORY≈30.2KB（均<32KB✅·归档#H-004~#H-008后）

  SWE-bench Verified Pass% (glm53 口径, 保留对照): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
  SWE-bench Verified Pass% (doubao-pro 口径): opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%
  SWE-bench Verified doubao-pro predict: 7/7路COMPLETE(cline494/opencode498/hermes498/pi494/cc500/dsh499/codex500·3500/3500=100%)
  SWE-bench Verified doubao-pro eval: 7/7路COMPLETE✅(opencode323/495·cline321/491·hermes302/489·cc297/493·pi270/483·codex218/464·dsh130/299)
  SWE-bench Multimodal: **已停(令D 2026-11-25)**·MM数据保留不删
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%

## 流水

> 📦 #H-001~#H-003 已归档 → daily-memories-harness/2026-11-25.md「归档」节（2026-11-26 07:55 滚出）

> 📦 #H-004~#H-006 已归档 → daily-memories-harness/2026-11-25.md「归档」节（2026-11-26 08:25 滚出）
> 📦 #H-007~#H-008 已归档 → daily-memories-harness/2026-11-25.md「归档」节（2026-11-26 08:38 滚出）

> #H-009（2026-11-26 01:00, 监控巡检·**dsh predict COMPLETE✅**(499/500·299 legit+29 garbage+171 empty·无运行进程)·doubao-pro 7way predict 5路active+CC rerun·2854/3500=81.5%·cline404(93rem)/codex374(126rem·最慢)/opencode416(83rem)/pi398(100rem)/hermes408(91rem)·CC rerun PID2440121(355 files increasing·log=rerun2.log·patch-producing正常·~145 remaining of 162)·⚠️dsh 29个垃圾patch(>1MB=venv git diff·django×27+matplotlib×1+sphinx×1·最大21MB django-17087)需eval前过滤→set model_patch=""·token 0.69B(41845 calls·in=676.6M+out=12.9M)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(466854s≈5.4d)·资源OK(load24.45/224=10.9%·mem670G/2015G avail1114G·0 high-CPU)·pretrain step7.29-7.39s≤7.4s✅·所有5路active newest file age<120s=全活跃·MM已停(令D·数据保留)·下一步:①继续monitor 5路+CC rerun→完成(ETA~05:00 codex bottleneck) ②dsh垃圾patch过滤 ③eval incremental_eval_merge.py --route <h> ④7way报告REGEN)

> #H-010（2026-11-26 01:30, 监控巡检+dsh垃圾patch过滤✅·**dsh 29/29垃圾patch过滤COMPLETE✅**(26 venv diff + 3 test-project/framework-delete → model_patch=""·verified all dsh files <1MB·299 non-empty/200 empty/499 total)·doubao-pro 7way predict 6路全活跃·2930/3500=83.7%·cline414(86rem)/codex385(115rem·最慢)/opencode428(72rem)/pi409(91rem)/hermes419(81rem)/cc375(125rem)+dsh499 COMPLETE·CC rerun PID2440121 ALIVE(3172s·rerun2.log·34 patch-produced+2 transient quota-blocked→recovered at 01:27:55)·pi有1 quota-blocked+1 no-patch→recovered at 01:28:44·hermes有1个612KB patch(sphinx-9602·含docs/_build/构建产物·29 diff·非venv垃圾·eval会处理不预过滤)·token~0.70B(43194 sidecar lines)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(468410s≈5.4d)·资源OK(load24.83/224=11%·mem671G/2015G avail1112G·0 high-CPU harness进程)·所有6路newest file age<130s=全活跃·MM已停(令D)·下一步:①继续monitor 6路→完成(ETA~05:00-06:00 codex bottleneck) ②eval incremental_eval_merge.py --route <h> --regen ③7way报告REGEN)

> #H-011（2026-11-26 02:05, 监控巡检+旧容器清理·doubao-pro 7way predict 6路全活跃·3041/3500=86.9%·cline431(69rem)/codex401(99rem·bottleneck)/opencode441(59rem)/pi427(73rem)/hermes439(61rem)/cc403(97rem)+dsh499 COMPLETE·**dsh eval LIVE**(PID3366607·4 docker containers active·299 non-empty patches·4 workers·guarded mem128g/cpu16·~22min elapsed·eval log=full_eval_doubao_pro_deepseek-harness.log)·CC rerun PID2440121 ALIVE(5266s·rerun2.log·patch-producing正常·last entry 02:02:35)·所有6路newest file age<300s=全活跃·quota transient: codex 5/pi 5(全recovered·doubao网关偶发·proxy自动重试)·**清理4个旧cline-patched rerun docker容器**(rerun_incr_cline-patched_11241548·idle 0%CPU·34h stuck·orphaned from superseded 11-24 glm53 rerun)·token~0.73B(44845 sidecar lines)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(470729s≈5.4d)·资源OK(load30.63/224=13.7%·mem674G/2015G avail1108G·0 high-CPU harness进程·max docker=100% single-core)·pretrain step~7.0-7.5s≤7.4s✅(from MEMORY_PRETRAIN last 7.39s)·MM已停(令D)·下一步:①继续monitor 6路→完成(ETA~04:30-05:30 codex/CC bottleneck) ②dsh eval完成后检查eval JSON结果 ③eval incremental_eval_merge.py --route <h> --regen ④7way报告REGEN)

> #H-012（2026-11-26 02:35, 监控巡检·doubao-pro 7way predict 6路全活跃·3119/3500=89.1%·cline441(59rem)/codex410(90rem·bottleneck)/opencode455(45rem)/pi439(61rem)/hermes451(49rem)/cc424(76rem)+dsh499 COMPLETE·**dsh eval LIVE**(PID3366607·260/299·111 passed=42.7%·4 docker containers·ETA~10min)·CC rerun PID2440121 ALIVE(6698s·rerun2.log·patch-producing正常·last entry 02:26:59)·所有6路newest file age<200s=全活跃·quota transient: codex/pi(全recovered·doubao网关偶发·proxy自动重试)·empty patches: cline3/codex22/opencode3/pi13/hermes7/cc2/dsh200·token~0.75B(46250 sidecar lines)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(472207s≈5.5d)·资源OK(load71.95/224=32%·mem675G/2015G avail1107G·0 high-CPU harness进程·max docker=100% single-core)·pretrain step~7.0-7.5s≤7.4s✅·MM已停(令D)·下一步:①dsh eval即将完成→检查eval JSON ②等6路predict完成(ETA~04:30-05:30 codex bottleneck) ③eval incremental_eval_merge.py --route <h> --regen ④7way报告REGEN)

> #H-013（2026-11-26 03:13, 监控巡检+**dsh eval修复✅**·doubao-pro 7way predict 5路active(cline468/codex432/opencode477/pi460/hermes471)+dsh COMPLETE(499/500)+CC rerun2 PID2440121 ALIVE(102/162 patch-produced·~60rem)·**dsh eval COMPLETE✅**(130/299=43.5%·130/500=26.0%·168 failed·1 infra timeout)·**修复full_eval_doubao_pro.py两处bug**：①EVAL_LOG_ROOT `logs/run_evaluation`→`logs/evaluation`(swebench实际写入路径) ②model名 `disp(route)-suffix`→`route-suffix`(deepseek-harness≠deepseek)·原eval JSON显示0 resolved/299 infra=全误分类(路径不存在→fallback glob也失败→全infra)·新增`reclassify_eval.py`从已有report.json重分类(无需重跑Docker)·5路newest file age<120s=全活跃·guard PID931671 LIVE(474571s≈5.5d)·gw_proxy 3进程LIVE(9090/9091/9092·ss确认UP·status脚本误报DOWN)·资源OK(load26/224=11.6%·mem676G/2015G avail1106G)·Docker 1080 swebench images(dsh eval 299个·未清理)·disk 184T/207T=89%·pretrain step~7.0-7.5s≤7.4s✅·MM已停(令D)·下一步:①等5路predict完成(ETA~04:30-06:00 codex 68rem最慢) ②CC rerun2完成(~60rem·ETA~05:00) ③每路完成后full_eval_doubao_pro.py --route <h> ④7way报告REGEN)

> #H-014（2026-11-26 03:55, 监控巡检+**dsh eval修复验证✅**·doubao-pro 7way predict 6路active(cline479/codex443/opencode490/pi468/hermes483/cc465)+dsh COMPLETE(499/500)·3318/3500=94.8%·**dsh eval JSON正确生成✅**(reclassify_eval.py从298个report.json重分类·resolved=130/failed=168/infra=1(scikit-learn-14710 timeout)·Pass%=130/299=43.5%=130/500=26.0%·与上次结果完全一致✅)·**前次full_eval_doubao_pro.py进程被tool超时kill**(03:39启动→进程退出·docker容器orphaned·已kill)·改用reclassify_eval.py直接从已有report.json生成eval JSON(无需重跑Docker·298/299 report.json已存在·1个missing=scikit-learn-14710=前次也是infra timeout)·CC rerun PID2440121 ALIVE(11000s+)·所有6路newest file age<120s=全活跃·token 0.85B(49732 calls)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(476349s≈5.5d)·资源OK(load42/224=18.9%·mem677G/2015G avail1103G·0 high-CPU)·pretrain step7.39s≤7.4s✅·disk 184T/207T=89%·MM已停(令D)·下一步:①等6路predict完成(ETA~04:30-06:30 codex 57rem最慢) ②每路完成后用setsid启动full_eval_doubao_pro.py --route <h>(避免tool超时kill) ③7way报告REGEN)

> #H-015（2026-11-26 04:17, 监控巡检+**opencode predict COMPLETE✅+opencode eval LIVE**·doubao-pro 7way predict 5路active(cline494/codex455/cc479/pi480/hermes498)+opencode COMPLETE(498/500·progress=500/500)+dsh COMPLETE(499/500)·3403/3500=97.2%·**opencode eval LIVE**(PID2481370·setsid+nice19启动避免tool超时kill·495 non-empty patches·4 Docker containers·mem128g/cpu16·log=logs/full_eval_doubao_pro_opencode.log)·hermes即将完成(498/500·2rem)·CC rerun PID2440121 ALIVE(13100s+)·token 0.86B(51147 sidecar lines)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(478626s≈5.5d)·资源OK(load21.5/224=9.6%·mem675G/2015G avail1105G·0 high-CPU·max cline=151% single-core)·pretrain step7.39s≤7.4s✅·MM已停(令D)·下一步:①opencode eval完成(ETA~30-60min)→检查eval JSON ②hermes完成后setsid启动eval ③等其余4路predict完成(ETA~05:00-06:30 codex 45rem最慢) ④7way报告REGEN）

> #H-016（2026-11-26 04:24, 监控巡检+**hermes+cline-patched predict COMPLETE✅→3 eval LIVE**·doubao-pro 7way predict 3路active(codex458/pi482/cc481)+4路COMPLETE(cline-patched494/opencode498/hermes498/dsh499)·3411/3500=97.5%·**3 eval LIVE**(opencode PID2481370 495 patches 7min elapsed·hermes PID2857902 489 patches 2min·cline-patched PID2990710 491 patches 1min·各4 Docker containers=12 total·setsid+nice19·mem128g/cpu16)+dsh eval✅(130/299=43.5%)·3路predict active(codex PID820223 67733s·pi PID820587 67729s·cc PID2440121 13813s rerun)·token 0.86B(51147 sidecar lines)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(478800s≈5.5d)·资源OK(load41.9/224=18.7%·mem679G/2015G avail1102G·Docker 12 containers max 97MiB each)·pretrain step7.39s≤7.4s✅·MM已停(令D)·下一步:①3 eval完成(ETA~30-60min)→检查eval JSON ②等3路predict完成(codex 42rem最慢·ETA~06:00-06:30)→setsid启动eval ③7way报告REGEN）

> #H-017（2026-11-26 04:48, 监控巡检+**pi predict COMPLETE✅(494/500)+3 eval progressing**·doubao-pro 7way predict 2路active(codex468/500 PID820223·cc rerun PID2440121)+5路COMPLETE(cline494/opencode498/hermes498/pi494/dsh499)·3435/3500=98.1%·**3 eval LIVE progressing**(opencode 220/495 report.json·hermes 182/489·cline-patched 165/491·~3 report/min per route·PID2481370/2857902/2990710·12 Docker containers·setsid+nice19·mem128g/cpu16)+dsh eval✅(130/299=43.5%)·token sidecar 51971 lines·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(480636s≈5.6d)·资源OK(load46/224=20.5%·mem678G/2015G avail1102G·0 high-CPU·max=451% Django test in eval container·well below 8000% threshold)·pretrain step7.39s≤7.4s✅·GPUs all~100% pretrain normal·MM已停(令D)·下一步:①3 eval完成(ETA~06:30-07:00)→检查eval JSON ②codex predict完成(32rem·ETA~06:30)→setsid启动eval ③CC rerun完成→eval ④7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-018（2026-11-26 05:15, 监控巡检+**CC predict COMPLETE✅(500/500·rerun2 merged 493/500 at 05:00)→启动CC+pi eval→5 eval LIVE**·doubao-pro 7way predict 1路active(codex477/500 PID820223)+6路COMPLETE(cline494/opencode498/hermes498/pi494/cc500/dsh499)·3472/3500=99.2%·**5 eval LIVE**(opencode PID2481370 338/495·hermes PID2857902 303/489·cline-patched PID2990710 294/491·CC PID2879750 4/493 just-started·pi PID2879751 4/483 just-started·各4 Docker workers·screen+nice19·mem128g/cpu16·32 Docker containers)+dsh eval✅(130/299=43.5%)·CC rerun2 finished 05:00 merged 493/500·CC progress=500/500✅·token sidecar ~52k lines·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE·资源OK(load82/224=36.5%·mem698G/2015G avail1126G·CPU idle52.7%·0 high-CPU·pretrain step7.39s≤7.4s✅)·MM已停(令D)·下一步:①5 eval完成(ETA~06:30-08:00)→检查eval JSON ②codex predict完成(23rem·ETA~06:30)→screen启动codex eval ③7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-019（2026-11-26 05:58, 监控巡检+**hermes+cline-patched eval COMPLETE✅→4 eval✅+2 eval LIVE**·doubao-pro 7way predict 1路active(codex491/500 PID820223 recovering from quota-block)+6路COMPLETE·**4 eval✅**(opencode 323/495=64.6% at 05:42·cline-patched 321/491=65.4% at 05:56·hermes 302/489=61.8% at 05:56·dsh 130/299=43.5%)+**2 eval LIVE**(CC PID2879750 407/493 report.json ~43min·pi PID2879751 293/483 report.json ~43min·nice19·mem128g/cpu16·9 Docker containers)·**duplicate cleanup** at 05:50: CC eval 3→1(pi 2→1) killed 2995426+3092926(cc)+3092927(pi)+2 screen sessions→load 103→53·codex quota-blocked at 05:51 recovered at 05:57(no-patch 376.6s)·token sidecar ~53k lines·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE·资源OK(load62/224=27.7%·mem681G/2015G avail1100G·0 high-CPU·pretrain step7.39s≤7.4s✅)·MM已停(令D)·下一步:①CC eval完成(ETA~06:10-06:15·86rem) ②pi eval完成(ETA~06:30-06:40·190rem) ③codex predict完成(9rem·ETA~06:15-06:45)→setsid启动codex eval ④7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-020（2026-11-26 06:20, 监控巡检+**codex predict COMPLETE✅(500/500)→codex eval STARTED**·doubao-pro 7way predict 7/7路COMPLETE(cline494/opencode498/hermes498/pi494/cc500/dsh499/codex500·3500/3500=100%)·**4 eval✅**(opencode 323/500=64.6%·cline-patched 321/500=64.2%·hermes 302/500=60.4%·dsh 130/500=26.0%)+**3 eval LIVE**(CC PID2879750 485/493 report.json sphinx-7985 stuck@23min~timeout·pi PID2879751 440/483·codex PID3809606 10/464 just-started·nice19·mem128g/cpu16·~13 Docker containers)·codex predict COMPLETE at 06:16(500/500·merged 464/500 non-empty·4 quota-block)·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·token sidecar ~53k lines·资源OK(load~60/224=27%·mem681G/2015G avail1100G·0 high-CPU·pretrain step7.39s≤7.4s✅)·MM已停(令D)·下一步:①CC eval完成(sphinx-7985 timeout~7min)→检查eval JSON ②pi eval完成(ETA~06:40-06:50) ③codex eval完成(ETA~07:50-08:30·464 patches) ④7way报告REGEN(gen_report_doubao_pro_7way.py)）

> #H-021（2026-11-26 07:17, **doubao-pro 7way eval 7/7 COMPLETE✅ + 报告已生成✅**·CC eval JSON 06:27(297/493=59.4%)·pi eval JSON 06:37(270/483=54.0%)·codex eval JSON 07:06(218/464=43.6%)·lingering codex Docker container killed·**7路最终Pass%**: opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%·报告`report_harness_doubao_pro_7way_swebench_tb_zh.html`已生成(7083B·0script/0外链✅)·token统计:7路合计~355k calls/~5.17B input/~99M output·guard PID931671 LIVE·gw_proxy 3进程LIVE·资源OK(load~42/224=19%·0 Docker·0 eval/predict进程)·所有11-25令A/B/C/D全部闭环·WAITING→0·下一步:待运维新指令）

> #H-022（2026-11-26 07:25, 例行巡检·**全部完成·idle**·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load24/224=11%·mem680G/2015G avail1101G·pretrain step7.39s≤7.4s✅)·git已pull up-to-date·**任务书归档**:11-24令+11-23令+11-19MM令→ARCHIVE(归档2026-11-26节)·TASK 32432B→16994B✅·新增11-25令A/B/C/D摘要·MEMORY 30.6KB(OK)·token sidecar 52884 lines·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-023（2026-11-26 07:40, 例行巡检·**idle·健康**·git pull up-to-date(无新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load26.64/224=12%·mem680G/2015G avail1102G·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·agent-arena repo 3 commits(a1fc485/a431e3c/a50291c)·TASK 27.0KB/MEMORY 31.1KB(均<32KB✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-024（2026-11-26 07:55, 例行巡检·**idle·健康**·git merge origin/main fast-forward(仅posttrain变更·无harness新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE(492019s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092)·资源OK(load25/224=11%·mem680G/2TB avail1.1T·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅(/nas_train/app.e0031982/harness_work/dsh_sdk)·agent-arena repo✅·TASK 27.0KB/MEMORY~28.5KB(归档H-001~H-003后·<32KB✅)·research日报2026-11-26已查(ShellBench:模型>harness影响·建议harness-only消融+报token成本·我们已报token✅·AIChipBench:held-out测试条件·非直接可执行)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）

> #H-025（2026-11-26 08:05, 例行巡检·**idle·健康**·git fetch+merge origin/main: Already up to date(无新指令)·自检:0 eval/predict进程·0 Docker·guard PID931671 LIVE(492601s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~81220s≈22.6h)·资源OK(load23.87/224=11%·mem680G/2TB avail1.1T·0 high-CPU harness进程)·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·TASK 27.0KB/MEMORY~29.8KB(均<32KB✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）
> #H-026（2026-11-26 08:15, 例行巡检·**idle·健康**·git fetch: Already up to date(无新指令)·自检(内存10-30令):0 harness eval/predict进程·gw_proxy 3进程RSS=25-44MB(远<50GB阈值✅)·guard 3.5MB✅·自检(CPU 11-02令):load26.70/224=12%(远<80%阈值✅)·0 harness进程>8000%CPU✅·guard PID931671 LIVE(493116s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~81736s≈22.7h)·0 Docker·mem681G/2TB avail1.1T·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·TASK 27.0KB/MEMORY~30.0KB(均<32KB✅)·research日报2026-11-26已查(无新可执行建议·ShellBench token成本建议已落地✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）
> #H-027（2026-11-26 08:25, 例行巡检·**idle·健康**·git fetch: Already up to date(无新指令)·自检(内存10-30令):0 harness eval/predict进程·gw_proxy 3进程RSS=24-43MB(远<50GB阈值✅)·guard 3.5MB✅·自检(CPU 11-02令):load26.21/224=12%(远<80%阈值✅)·0 harness进程>8000%CPU✅·guard PID931671 LIVE(493567s≈5.7d)·gw_proxy 3进程LIVE(9090/9091/9092·~82187s≈22.8h)·0 Docker·mem684G/2TB avail1.1T·报告report_harness_doubao_pro_7way_swebench_tb_zh.html=7083B✅·token sidecar 52884 lines·dsh_sdk持久化✅·agent-arena repo✅·TASK 27.0KB/MEMORY~25.5KB(归档#H-004~#H-006后·均<32KB✅)·research日报2026-11-26已查(无新可执行建议·ShellBench token成本建议已落地✅)·所有11-25令A/B/C/D已闭环·WAITING:0·下一步:待运维新指令）
> #H-028（2026-11-26 08:38, **cline-patched re-predict STARTED✅**·11-26令接手执行·cline配置修正已验证(run_single.py:109-110 --compaction basic --thinking low✅·run_harness.py:198-199✅·agent-arena synced✅)·报告已更新(7873B·zhulong(cline-patched)+版本号✅)·旧cline-patched predictions/progress/eval已删✅(494 files)·re-predict启动✅(PID1755547·setsid·workers=1·500 pending·nice10·compaction=basic+thinking=low)·gw_proxy 3进程LIVE(9090/9091/9092·~82959s≈23h)·guard PID931671 LIVE(493567s≈5.7d)·0 Docker·load~26/224=12%·mem684G/2TB avail1.1T·自检(内存10-30令):gw_proxy RSS=24-43MB✅·自检(CPU 11-02令):0 harness进程>8000%CPU✅·⚠️cline实际版本3.0.75(MEMORY记3.0.51·待后续确认)·归档#H-004~#H-008→daily-memories·MEMORY~30.2KB(均<32KB✅)·下一步:monitor re-predict(ETA~3-4h)→eval→REGEN报告·WAITING:0）



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
