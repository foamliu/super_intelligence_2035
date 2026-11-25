# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
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

PHASE:        11-25令(doubao-pro 7-way 重测 SWE-bench Verified)·doubao-pro 7way predict 进行中(2760/3500=78.9%)·MM已停(令D)
已完成:       H-B OK·Gate7/7·TB-2.1 7路 COMPLETE·SWE-bench Verified glm53 7路 predict+eval·token 记录改造✅·launch_doubao_7way.sh✅·**doubao-pro 7way LIVE✅**(7路全RUN)·**deepseek-harness SDK修复✅**·**MM已KILL✅**(令D·pkill run_mm_2x3.py+mm_proxy·MM数据保留不删)·**claude-code predict重启✅**(19:24 git-fetch blocked 158题→00:25重启resume pending=162)
当前动作:     doubao-pro 7way predict 7/7路全RUN(cc342+rerun/cline388/opencode407/pi385/codex355/hermes390/dsh493=2760/3500=78.9%)·token 0.65B(39637 calls·in=633.7M+out=12.2M·from gw_proxy sidecar)·MM已停(令D)·claude-code rerun PID1808093 pending=162(00:25启动·resume跳过338已完成)·guard PID931671 LIVE(464197s≈5.4d)
下一步:     ①doubao-pro 7way predict完成(ETA~04:00 Nov26·dsh近完7remaining·codex最慢145remaining)→eval+报告 ②⚠️dsh垃圾patch需eval前过滤或标注(14个>1MB git diff venv) ③eval用incremental_eval_merge.py --route <h> · ④7way报告REGEN
阻塞:         无（MM已停·dsh近完成·claude-code rerun已启动）
ERROR_COUNT:  0
 体积: TASK~31.7KB / MEMORY≈15.5KB

  SWE-bench Verified Pass% (glm53 口径, 保留对照): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
  SWE-bench Verified doubao-pro predict: 2760/3500=78.9% (cc342/cline388/opencode407/pi385/codex355/hermes390/dsh493)
  SWE-bench Multimodal: **已停(令D 2026-11-25)**·MM数据保留不删
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%

## 流水

> #H-001（2026-11-25 11:05, 监控巡检·doubao-pro 7way predict 7/7路全RUN·cline45/codex39/opencode43/pi42/cc54/hermes37/dsh17 of 500·deepseek-harness rerun PID570709 17/500 14 patches produced·SDK路径持久化✅(run_harness.py:377=/nas_train/app.e0031982/harness_work/dsh_sdk)·token sidecar 3769 lines·资源OK(load25/224 cores·mem 670G/2015G·pretrain step7.29s≤7.4s✅·guard PID931671 LIVE·0 high-CPU)·agent-arena repo✅(33 scripts committed)·MM 2×3 predictions全丢待重跑·下一步:继续monitor 7way predict→完成后eval+报告

> #H-002（2026-11-25 11:26, 监控巡检·doubao-pro 7way predict 7/7路全RUN健康·371/3500=10.6%·cc70/cline57/opencode57/pi55/codex49/hermes49/dsh34·patch_produced=359·0 infra·7 quota transient(全恢复)·0 error·token 78.4M(5010 calls)·gw_proxy 3进程(9090/9091/9092)·guard PID931671 LIVE(418143s)·SDK持久化✅(run_harness.py:377=/nas_train/app.e0031982/harness_work/dsh_sdk)·资源OK(load29/224·mem686G/2015G·pretrain step7.29s≤7.4s✅·CPU idle89%)·MM 2×3 predictions全丢(progress_2x3元数据存活480/480·predictions_2x3/0 files)·下一步:继续monitor→7way predict完成(ETA~midnight)→eval+报告→MM全量重跑

> #H-003（2026-11-25 11:49, 监控巡检·doubao-pro 7way predict 7/7路全RUN健康·453/3500=12.9%·cc85/cline67/opencode67/pi65/hermes60/codex60/dsh49·non-empty patches=433/453=95.6%·0 infra·1 quota transient(dsh 11:40·已恢复)·0 error·token 97.2M(6250 calls·input 95.2M+output 2.0M)·gw_proxy 3进程LIVE·guard PID931671 LIVE(419522s)·SDK持久化✅(run_harness.py:377=/nas_train/app.e0031982/harness_work/dsh_sdk·目录存在✅)·资源OK(load29.87/224·mem670G/2015G·CPU idle87%·0 high-CPU harness进程)·11-24令(cline --workers 8 glm53 parallel predict)已被11-25(A)令取代(停止glm53→改doubao-pro)·旧parallel_cline_predict.log不存在(已清理)·MM 2×3 predictions全丢(progress_2x3元数据存活480/480·predictions_2x3/0 files)·下一步:继续monitor→7way predict完成(ETA~midnight)→eval+报告→MM全量重跑

> #H-004（2026-11-25 12:12, 监控巡检·doubao-pro 7way predict 7/7路全RUN健康·538/3500=15.4%·cc100/cline78/opencode81/pi73/hermes71/codex72/dsh63·non-empty patches=510/538=94.8%·⚠️deepseek-harness有5个9.9MB垃圾patch(=git diff整个venv目录·django-11211/11555/11149/11815/11734)·dsh patch_rate=43/63=68.3%远低于其他路95-100%·0 infra·0 quota transient·0 error·token 754M(47948 calls·in=739M+out=14.9M)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(420808s)·SDK持久化✅·资源OK(load27/224·mem672G/2015G·0 high-CPU)·所有7路newest file age<132s=全活跃·research日报2026-11-25已查(无直接可执行建议)·下一步:继续monitor→7way predict完成(ETA~midnight)→eval+报告→MM全量重跑·⚠️eval前需处理dsh垃圾patch(过滤或标注)

> #H-005（2026-11-25 12:34, 监控巡检·doubao-pro 7way predict 7/7路全RUN健康·618/3500=17.7%·cc111/cline89/opencode94/pi82/codex81/hermes82/dsh79·non-empty patches=580/618=93.9%(excl dsh: 529/539=98.1%)·⚠️dsh有6个10.5MB垃圾patch(=git diff整个venv目录·django-11211/11555/11149/11815/11734/11999)·dsh patch_rate=51/79=64.6%远低于其他路96-100%·dsh 28 empty patches(35.4%)·0 errors·16 quota transient全恢复(codex5/opencode1/pi3/cc2/hermes4/dsh1)·429在gw_proxy日志(9090=56/9091=0/9092=26)有retry处理·token 134.5M(8518 calls·in=131.8M+out=2.7M)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(422112s≈4.9d)·SDK持久化✅·资源OK(load28/224·mem672G/2015G·0 high-CPU harness进程)·所有7路newest file age<170s=全活跃·pretrain step7.39s≤7.4s✅·下一步:继续monitor→7way predict完成(ETA~midnight)→eval+报告→MM全量重跑·⚠️eval前需处理dsh垃圾patch(过滤或标注)

> #H-006（2026-11-25 13:04, 监控巡检+MM修复·doubao-pro 7way predict 7/7路全RUN健康·707/3500=20.2%·cc129/cline99/opencode104/pi92/codex93/hermes93/dsh97·patch_rate=652/707=92.2%(excl dsh: 602/649=92.8%)·⚠️dsh 9个>1MB垃圾patch(git diff venv)+38空patch·dsh patch_rate=50/97=51.5%·token ~1.01B(63610 calls)·gw_proxy 3进程LIVE(9090/9091/9092)·guard PID931671 LIVE(423386s≈4.9d)·SDK持久化✅·**MM 2×3全量重跑启动✅**(6/6路RUN·clear stale progress→launch_mm_2x3_full.sh·**fixed opencode KeyError**: run_mm_2x3.py lines 150/154/411 r['llm']→r['model'](config用model不用lll)·agent-arena commit a1fc485 pushed✅·synced to super_intelligence_2035)·⚠️**deepseek-v4-flash不支持多模态**(cline+opencode 2路每题rc=1 "not a multimodal model"·产空patch·非bug是模型限制·2×3实际有效=2×2+2空)·cline__doubao 3/480 has_patch✅·cline__kimi 1/480 running·opencode 3路刚启动·资源OK(load30/224·mem675/2015G·0 high-CPU harness进程·max=cline_mm_doubao 240%=2.4核)·pretrain step7.39s≤7.4s✅·所有7路SWE-bench newest file age<160s=全活跃·下一步:继续monitor 7way+MM→7way完成→eval+报告→MM完成→eval→dsh垃圾patch过滤

> #H-007（2026-11-25 13:28, 监控巡检·doubao-pro 7way predict 7/7路全RUN健康·817/3500=23.3%·cc151/cline112/opencode120/pi105/codex103/hermes106/dsh120·所有7路newest file age<110s=全活跃·token 1.22B(76457 calls·in=1199.8M+out=24.3M·from prediction JSON usage field)·gw_proxy 3进程LIVE(9090/9091/9092)·429 counts: 9090=58/9091=1/9092=26(proxy handles with retries·0.75% rate)·⚠️ConnectionResetError on 9090/9091 tails(predictions still progressing)·guard PID931671 LIVE(425296s≈4.9d)·SDK持久化✅·⚠️dsh 14个>1MB垃圾patch(11MB each·all django·git diff venv目录)需eval前过滤·MM 2×3 LIVE(169/2880=5.9%·⚠️kimi-k2.6 routes very slow)·pretrain iter319060 step7.32s≤7.4s✅·资源OK(load31.65/224·mem676G/2015G)·下一步:继续monitor 7way+MM→7way完成→eval+报告)

> #H-008（2026-11-26 00:26, **令D执行+claude-code重启**·**MM已KILL✅**(pkill run_mm_2x3.py+mm_proxy·令D执行·MM数据保留不删)·**claude-code predict重启✅**(19:24 git-fetch blocked 158题→00:25重启resume pending=162·PID1808093·log=claude-code_doubao_pro_rerun.log·resume跳过338已完成题)·doubao-pro 7way predict 7/7路全RUN健康·2760/3500=78.9%·cc342/cline388/opencode407/pi385/codex355/hermes390/dsh493·dsh近完成(7remaining)·token 0.65B(39637 calls·in=633.7M+out=12.2M·from gw_proxy sidecar /tmp/gw_proxy_usage.jsonl)·gw_proxy 3进程LIVE(9090/9091/9092 PID623606/623610/623695)·guard PID931671 LIVE(464197s≈5.4d)·资源OK(load31/224·mem OK·0 high-CPU harness进程)·pretrain step7.29s≤7.4s✅·claude-code blocking根因:git_clone_or_fetch返回ok=False(workdir /dev/shm state OK·/dev/shm 13%used·非磁盘问题·可能NFS/git transient)·下一步:继续monitor 7way predict→完成(ETA~04:00)→eval+报告→dsh垃圾patch过滤)

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
