# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **用户令 · 2026-11-25 — 停止当前 SWE-bench Verified 评测，改用 doubao-pro 重测全量 500×7 + 记录 token**
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

PHASE:        11-25令(doubao-pro 7-way 重测 SWE-bench Verified)·等执行
已完成:       H-B OK·Gate7/7·TB-2.1 7路 COMPLETE·SWE-bench Verified glm53 7路 predict+eval·token 记录改造✅(gw_proxy+run_single+incr_eval_merge)·launch_doubao_7way.sh✅
当前动作:     等执行：(1)停旧 Verified 进程 (2)run launch_doubao_7way.sh (3)重启 MM kimi retry
下一步:     doubao-pro 7-way predict → eval → 报告；MM kimi retry → MM eval
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~31.7KB / MEMORY≈6KB

 SWE-bench Verified Pass% (glm53 口径, 保留对照): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
 SWE-bench Multimodal 2×3 predict: 4路DONE·2路kimi retry需重启·has_patch=2615/2880(90.8%)
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%

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
