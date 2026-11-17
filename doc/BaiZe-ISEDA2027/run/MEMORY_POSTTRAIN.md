# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

> 🟢 **run5 完成 + 5-run 收口 wake628 08:46(posttrain 5run:,22:0x 令全流程闭环)**：run5 code-gen 08:39 全 158 题完成→format_cline_cli_output→rca_recover_extract.py(ws+no-ws 回补,completed_code_generation 75484B)→run_eval.py -g 干净重评测(output_evaluation/20261117_0843)→链 08:43:55 END。**run5 Pass@1=4.43%(7/158),execution_results=44 行≫1(VALID,非 collapse)**;chain PID1354030 已退出。**5-run 收口(n=5,rca_status=CLEAN)**:mean=6.84%±6.12% [run1=18.99%(ws-only锚点),run2=4.43%,run3=2.53%,run4=3.80%,run5=4.43%],exec 行数 36/43/28/35/44 均≫1;vs 旧 .17 3.04%±0.74% Δ=+3.80pp,McNemar pass@any chi2_corrected=13.5(discordant=54,n10=41,n01=13,p<0.001 显著),Wilcoxon n_nonzero=55(scipy 不可用仅报 n);Q1 真 MCP 拒绝率(排除 run_commands)=6.3%。**口径 caveat**:run1=ws-only 锚点(batch 2026_1114_180019 已清理不可回补,18.99% 为高 outlier,其 36 ws 段通过率 83% 异常高);run2-5=recovered 口径(ws+no-ws 经 rca_recover_extract.py 回补);5-run mean 带此 caveat。run5 起跑=STEP1 verdict 共用 8090 MCP 池+-p2(与 zhulong -p4 共存,独占租借+asyncio.Queue 池满排队,不起新 MCP,同 workdir t0002997_1..4⇒与 run1-4 同口径可并入 5run mean);env_fingerprint.json 在位(pool_mode=shared_8090_exclusive_queue/shared_with_zhulong=true/new_mcp=false/can_merge_into_5run_mean=true)。已执行验收:`bash bpt_zhulong_5run_finalize.sh --num-runs 5`→5run_zhulong_baseline_analysis.json(rca_status=CLEAN)+attribution_zhulong_5run_attribution.json;报告 report_posttrain_zhulong_reattribution_zh.html §10/§8 改为 5-run 同表+配对检验+口径 caveat+RCA 更正(非模型 collapse);run1-4 产物未被改;未启 clean_5run(脚本仅作证据留盘)。**5-run mean 现可引用(带 run1 caveat)**。> 📦 5-run 坍塌 RCA（2026-11-16 05:xx · posttrain rca: · 已闭合，被 wake628 干净 5-run 取代）→ daily 2026-11-16 + 报告 `reports/report_posttrain_collapse_rca_zh.html`。**结论**：run2/3/4「各仅 1 条 execution_result=0.0%」主因=管线 ws/no-ws 路径失配（抽取器 `format_cline_cli_output.py:163` ws-only 无回退 + 模型代码写到 no-ws），非模型 collapse；`rca_recover_extract.py` 回补后干净 Pass@1 run2/3/4=4.43/2.53/3.80% exec43/28/35≫1（已接入链脚本自愈，无需改 eda_fastmcp）。

> 🔴 **wake629（2026-11-17 09:35 · posttrain 5run:）— 纪律纠偏：第2次停 clean_5run + 恢复 run2 封存**：发现 `baize_posttrain_clean_5run.sh`（wake590 已停过一次）**第2次被未授权 wake 启动**（09:25:39），把 `attribution_3615_run2` 5 文件 mv 到 `_old_20261117092539/` 并在 36.15 起新 eval（违反 23:0x item1「不再起新 run」+ 18:3x/22:0x「🚫 不改 run1-4 产物」）。处置：① kill 本地树 PID1826270/1826316/1826380；② kill 36.15 orphan eval PID1780473/1780482+5 run_cli worker（**本线 unauthorized 非 zhulong**，zhulong PID620959 已自然结束非我 kill）；③ `mv _old_/* run2/` + rmdir → 5 文件复原（74432/26508/12838/69922/74205B，`git diff --stat HEAD -- run2` **空**=与 HEAD 字节一致）；④ run1/3/4/5 未受影响（exec 36/28/35/44 ≫1）；⑤ **加固**：clean_5run.sh 顶部加 DISABLED guard（`BPT_CLEAN_5RUN_AUTHORIZED!=1`→exit 7），保留全文作证据防第3次复发，smoke 打印 DISABLED 退出。5-run 收口产物（5run_analysis.json rca_status=CLEAN / 报告§10§8 / run5 final_report 74434B exec44）均在位未污染。🚫 未启 clean_5run 运行/未改 eda_fastmcp/.env/8090/未 kill 他线/未用 n<5 冒充。详见 daily 2026-11-17 wake629。


> 📦 wake507 隧道复盘（2026-11-14 23:5x · posttrain infra: · 已闭合）→ daily 2026-11-14。**结论**：隧道坏过现已恢复（最后通 20:41:50 / 首断 22:4x / 恢复 23:26 / 故障域=中继侧 / 非本线造成亦非本线修复）。报告 `reports/report_infra_tunnel_postmortem_zh.html`。

> 📦 wake598/599 端口池并行诊断（2026-11-16 21:0x · posttrain 5run: · 已闭合=报运维）→ daily 2026-11-16。**结论**：22:0x 令第1步 verdict——client 侧不可重路由 code-gen（cline_mcp_settings.json 硬编码 8090，main.py 启动建池），沙盒 8650-8670 仅 8655 空闲（8656-8670=他人 daemon），无可用 4 口独立池；串行 global-wait 是数据完整性正确路径（已被 wake601+ share-8090-pool 取代）。

> 📦 wake590 纪律纠偏（2026-11-16 17:2x · posttrain rca: · 已闭合，被 wake629 复发处置取代）→ daily 2026-11-16。**结论**：第1次停未授权 clean_5run.sh + 恢复 run2 封存（git diff HEAD 空）。wake629 第2次复发已加 DISABLED guard。

## 进度快照

- PHASE: posttrain-wake631（✅ **22:0x 令全流程闭环 wake628**：5-run 收口 n=5 mean=6.84%±6.12% [18.99,4.43,2.53,3.80,4.43]% rca_status=CLEAN，McNemar chi2=13.5 p<0.001 显著 vs 旧.17 3.04%±0.74%；36.15 run1 逐题画像=18.99%(30/158)/gen成功36/gen_fail121/T6_tool_format 头号76.6%；v2 RCA 已交付；R2 4-run mean≈0.475% decisively 负）
- 已完成: P0-P3预备✅;P1-P2✅;R1-R210✅;R280归档;R411-R428✅(verl BLOCKED→自写GRPO loop);R0 200步COMPLETED诚实负结果(cheat=0/3200,reward无方向信号);R2 200步COMPLETED(cheat=0/1600,real signal但reward平台后回落0.1195→0.0798)+global_step_200 ckpt+R2 serve GPU7:8095;R2 5-run eval run1-4 DONE mean≈0.475% decisively负(run5被kill因08:1x令);R434-R452 5-run eval健康监控✅(0 infra错误,eval全自治);step105 baseline 0.0304±0.0083 locked。[全量R-round/wake历史详见 daily-memories-posttrain/2026-11-{06..16}.md 与 EXPERIMENTS归档]
- 当前动作: wake631(2026-11-17 · posttrain 归档:)—**TASK.md 体积维护轮**（22:0x 令全流程已闭环 wake628，无新 run）。前置：✅ wake628 5-run 收口(n=5 mean=6.84%±6.12% rca_status=CLEAN) + ✅ wake629 纪律纠偏 + ✅ wake630 MEMORY 体积维护(37.9KB→31.2KB)。本轮：BAIZE_POSTTRAIN_TASK.md **47.2KB 超 40KB 硬上限**（19:2x 令明示「下轮先归档已闭合块」）→ 归档 9 个已闭合运维块原文到 ARCHIVE_OPERATOR_POSTTRAIN.md 并留 1 行指针（20:5x/18:3x/23:0x/08:1x/14:23:4x/14:21:5x/14:15:4x/14:09:0x/11-10 13:40，均 wake628/更早已 ✅ 闭环）→ TASK.md 47.2KB→**25.6KB**（<32KB 软限+<40KB 硬限）；保留 22:0x(最新)/L4(全量未完)/使命块/工作约定/19:2x(本令不得归档)/全部常驻块 原文未改。5-run 收口产物复核在位未污染（5run_analysis.json rca_status=CLEAN / 报告§10§8 / run5 final_report 74434B exec44 / env_fingerprint.json）。🚫 未启 clean_5run/未改 eda_fastmcp/.env/8090/未 kill 他线/未改 run1-4 产物/未用 n<5 冒充/未改任何指令文本。**5-run mean 现可引用(带 run1=ws-only 锚点 caveat)**。
- wake533 R533（已归档）:沙盒非确定性发现[baseline_dev direct 2/79 vs rescue 0/79,单 seed delta<沙盒方差⇒不可定论]+双轨 compare 方法论。详见 EXPERIMENTS §R533-sandbox-nondeterminism / daily 2026-11-15 wake533。
- 下一步: ✅ **22:0x 令全流程闭环**（run5 完成+5-run 收口 rca_status=CLEAN+报告§10/§8+env_fingerprint）+ ✅ 体积维护（wake630 MEMORY 37.9KB→~31KB + wake631 TASK.md 47.2KB→25.6KB）。后续候选（待用户定夺，不擅自起新 run）：① 用全 recovered 同口径 fresh 5-run 定论 run1=18.99% ws-only outlier（run1 batch 已清理不可回补，需全 5 run 均 recovered 口径）；② 推进 SFT/RL 主线（R2 4-run mean≈0.475% decisively 负已有，报告 report_posttrain_rl_surrogate_zh.html）；③ GPU7:8095 R2 serve 可 teardown 释放；④ kill_gpu_serve child-PID bug 待 chain 空闲修。⚠ clean_5run.sh 已加 DISABLED guard，未经用户授权+`BPT_CLEAN_5RUN_AUTHORIZED=1` 不得再启动（已 2 次未授权复发）。
- 阻塞: ✅ **R2 200步主训 COMPLETED** + **R2 5-run eval run1-4 DONE mean≈0.475% decisively 负**(run5 被 kill 释放给 08:1x 最高优先令,R2 链 PID2322797 全树已清)。**R0=诚实负结果**(proxy reward 不移动 policy)。RL 基座=MiniCPM5-2B/SFT step105。GPU0-3=root;GPU4=base serve;GPU5=vision R9 占用(非本线,不碰);GPU6=step105-final baseline serve(:8096,zhulong 基线用);GPU7=R2 step200 serve(:8095,R2 eval 已完可 teardown)。沙盒经 dual-nix-tunnel 通。verl 结论性 BLOCKED 不再尝试。
- 本轮新增产出: wake631✅(TASK.md 体积维护：47.2KB 超 40KB 硬上限→归档 9 个已闭合运维块[20:5x/18:3x/23:0x/08:1x/14:23:4x/14:21:5x/14:15:4x/14:09:0x/11-10 13:40]原文到 ARCHIVE_OPERATOR_POSTTRAIN.md+留 1 行指针;TASK.md→25.6KB<32KB 软限;保留 22:0x/L4/使命/工作约定/19:2x/常驻块 原文未改;ARCHIVE→60.2KB;结构 grep 复核 PASS+ARCHIVE verbatim 抽检 PASS;daily+commit posttrain 归档:)。前置 wake630✅(MEMORY 体积维护：37.9KB→~31KB)+wake629✅(纪律纠偏)+wake628✅(run5 完成 4.43% exec44 VALID+5-run 收口 n=5 mean=6.84%±6.12% rca_status=CLEAN+McNemar chi2=13.5+报告§10/§8+env_fingerprint)。[wake601-630 收口/监控历史详见 daily 2026-11-17]
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ R0 200步 COMPLETED 诚实负结果 + ✅ R2 200步 COMPLETED(cheat=0/1600) + ✅ R2 5-run eval run1-4 DONE mean≈0.475% decisively 负(run5 被 kill 因 08:1x 令最高优先);R2 5-run 终版报告用 4-run 数据+标注;🔴 2026-11-15 08:1x「158 评测改用 zhulong 方式」——✅ **全流程闭环 wake628**：wake534 再归因 + wake536 口径复核 + wake542 链修复起跑 + ✅ run5 完成(4.43% exec44 VALID)+ ✅ 5run_zhulong_baseline_analysis.json(n=5 mean=6.84%±6.12% rca_status=CLEAN,McNemar chi2=13.5 vs旧.17 3.04%±0.74%)+ ✅ 报告§10/§8 5-run 同表+口径 caveat;🔴 2026-11-16 22:0x 自建沙盒池/MCP——✅ STEP1 verdict 共用 8090 池(不起新 MCP,同 workdir 可并入 5run mean)+ ✅ run5 起跑+冒烟+收口+env_fingerprint;L4 2026-11-12(zhulong step105 ✅5/5 0.0304±0.0083;designflow base 5/5=0%)
- git: super_intelligence_2035(HEAD=origin/main synced);本轮交付(wake631: TASK.md 体积维护[47.2KB→25.6KB,归档 9 已闭合运维块到 ARCHIVE+1 行指针,保留 22:0x/L4/使命/工作约定/19:2x/常驻 原文未改]+MEMORY wake631 快照刷新+daily);只 add 本线文件,不用 -A
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;venv 重建后需重打此patch
- 🔧 **verl 0.4.0 GRPO 结论性 BLOCKED(wake411)→ ✅ wake412 换框架解除**:verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→init 握手死锁;1-GPU/2-GPU/NCCL 修复均复现;根因=verl 0.4.0+本机 Ray 命名 actor 可见性不兼容。**wake412 解除**：弃用 verl 路径，新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch，无 Ray/verl/torchrun），smoke 3 步 PASS(ratio=1.000)。verl surrogate 脚本保留但不再尝试。详见 EXPERIMENTS §R411/§R412
- 🔧 **torchrun 单驱动修复 R-launch-fix3(wake411)**:`baize_posttrain_rl_grpo_surrogate.sh` L320 `--nproc_per_node=1`(verl main_ppo 单驱动,n_gpus 来自配置);原 $NGPU 派生多 Ray 集群→多 GPU 起跑前提修复
- 🔧 **NCCL 接口修复 R-launch-fix4(wake411)**:脚本 export NCCL/gloo `SOCKET_IFNAME=bond0`+`NCCL_IB_DISABLE=1`+`NCCL_NET=Socket`(本机多网卡含 docker bridge);标准 torch.distributed-in-container 加固,实测对 verl 死锁无效(非根因)但保留
- 🔧 **R2 OOM 最终修复(wake429)**:A40 44GB 对 2B 全参 GRPO(G8 B2)预算过紧(policy+ref+Adam16GB+grad=28GB 基线+logits float32 峰值5GB 触顶)。修复=`--batch-prompts 1`(Gtot=8/step,**G=8 保持**)+`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。verl_cu124_venv 起 RL 必带此 env;若再 OOM 可进一步降 ctx 或切 8-bit Adam。
- 🔧 **config-path 修复 R-launch-fix2(wake410)**:`baize_posttrain_rl_grpo_surrogate.sh` L303 `CFG_DIR` 强制绝对路径;项目配置(sdpa/hybrid/timeout)现真正加载;RL 起跑前提(已验证有效)
- 🔧 **kill_gpu_serve child-PID bug(wake433 发现,待修)**:`baize_posttrain_rl_eval_chain.sh` L102-118 `kill_gpu_serve` 用 `nvidia-smi --query-compute-apps=pid` 取 GPU 占用 PID,但 vLLM serve 的 CUDA 上下文常由 multiprocessing 子进程持有(父=serve,子=`python -c from multiprocessing.spawn...`)⇒子进程 cmd 不含 `vllm.entrypoints.openai.api_server`⇒误判 skip,GPU5 step60 serve 未被 teardown。wake433 手动 kill 父进程 1802143 完成 OOM mitigation。**修法(待 chain 空闲)**:取到子 PID 后 walk `ps -o ppid=` 到根,沿路径 grep vllm serve;或改用 `pgrep -f 'vllm.entrypoints.openai.api_server.*--port <PORT>'`。不编辑运行中脚本。




## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4） | 39.1GB | ✅ wake334 restarted(PID553793 was dead→new PID799523,+no_proxy env) |
| 5 | — | — | **vision R9 占用**(cpu_rl_v11_regen_experiment PID2498238,~32GB,非本线,不碰) | 32584 MiB | 🔵 vision R9 wake449 起占用 |
| 6 | 8096 | minicpm5-2b-sft-v39-final | **vLLM SFT v39 final ckpt serve**(wake360,global_step_105,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4,PID962854) | 39.2GB | ✅ wake361 parallel eval RUNNING(GPU6=81%util,step_105 eval PID972225) |
| 7 | 8095 | minicpm5-2b-grpo-R2-step200 | **vLLM R2 global_step_200 serve**(wake433,PID2353244,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 --enable-auto-tool-choice --max-num-seqs 4,5-run eval RUNNING) | 39.1GB | ✅ wake433 serving+eval RUNNING |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0, vLLM 0.7.3）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建
> 🔧 **minicpm5 tool-call parser**（wake306 新增）：自定义vLLM parser解析MiniCPM5的`<function name><param>`XML→结构化`tool_calls`；源码在`run/baize_posttrain_vllm_minicpm5_parser.py`，安装到`/tmp/vllm_venv/.../tool_parsers/minicpm5_tool_parser.py`+`__init__.py`；venv重建后需重装（`cp run/baize_posttrain_vllm_minicpm5_parser.py /tmp/vllm_venv/.../tool_parsers/minicpm5_tool_parser.py` + 编辑`__init__.py`加import）；serve启动加`--tool-call-parser minicpm5`
> 🔧 拆除占位 serve（沙盒恢复后 Phase2 前）：`bash baize_posttrain_serve_teardown.sh`（默认拆 GPU5/6/7；`--gpu4` 也拆 GPU4；`--all` 全拆；`--status` 看占用；`--dry-run` 预览；**永不碰 GPU0-3/ROOT:8099**）— R165
> 🔧 维持占位 serve 健康（17:10令持续占位期间）：`bash baize_posttrain_serve_sentinel.sh`（`--check-once` 单次探测 / `--watch --auto-restart` 持续监控+GPU5/6/7崩溃自动重启 / `--status` 看配置 / **永不重启 GPU0-3**）— R167

## 关键事实（常驻）

- pretrain S1 现状：iter~112400/700000（2026-11-07 git log），ETA≈2026-12-25（`.29` 8×H100）
- post-train 正式训练窗口：≈2026-12 下 → 2027-01 中（ISEDA 投稿 2027-02-01）
- 评测锚点：MiniCPM5-2B 36%（full harness，与 DeepSeek 94% 同口径，差 58 pp）
- 评测基准：EDA-Eval-PyAether 158 任务，Pass@1，5-run mean±std，2500s/任务，`-p 8 -n`
- 成功阶梯（预注册）：36%(起点) → 50%(M1) → 65%(M2) → 75%(M3) → 85%+(M4)
- SFT 数据已就绪：UltraData-SFT-2605（319G 下载/75.87GB 分词/18.89B tok，DATA_MAPPING 单一事实源）+ UltraData-SFT-Agent-2609（54.22G 下载/23.89GB 分词/5.97B tok）已分词镜像
- B 类 agentic 数据已下载未分词（`/nas_inference`：AgentTrove/Nemotron-Cascade-SFT-SWE 等）
- PyAether 领域语料：✅ **已调研**（wake4）—— `~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json` 8,463 个 API（api_name/api_type/api_descriptions/category）展平 ≈3.3–4.5M tok；加 func_all_v3/api_summary/skills/prompts ≈4–5M tok 可导出纯文本；chroma_db_*（向量嵌入）不用；退火 domain 主体 + SFT 合成语料（详见 EXPERIMENTS §PyAether-corpus）
- MiniCPM5-2B 模型：✅ **已下载到 .17** `/tmp/models/MiniCPM5-2B/`（4.7GB，LlamaForCausalLM 42层 2048d，2026-11-06 17:14）→ vLLM venv ✅ **已就绪** `~/code/vllm_venv/`（v0.33.0, torch 2.14.0, 9.4GB）→ GPU 释放后可 `vllm serve` 跑诊断评测获取 36% 侧轨迹
- .17 GPU 现状：8×A40 全被 SGLang Qwen3.8-27B 占用（44-45/46GB），2026-11-09 分配 4 张给 post-train
- 🔴 **CUDA 不匹配（wake53 发现 → ✅ R25 已解决）**：系统 CUDA 驱动=12.4（nvcc 12.4.131, 驱动550.54.14），旧 vllm_venv torch=2.14.0+cu130 → `torch.cuda.is_available()=False`。✅ **R25 修复**：新建 cu124 venv `~/code/verl_cu124_venv/`（Python 3.10.22, torch 2.6.0+cu124）→ 包已确认安装（site-packages: sglang 0.4.6 + verl + flash_attn 2.7.4 + ray + flashinfer 0.2.3）。⚠️ NFS冷启动 import torch >30s（R45实测），起跑前需 warm-up。
- ✅ **git代理（wake209发现）**：`.17` → GitHub 需要 HTTP 代理 `172.19.92.25:13128`。已配置到 repo local config: `git config --local http.https://github.com/.proxy http://172.19.92.25:13128`。之后 `git push`/`fetch` 不再超时。wake208 的 fetch 超时即因此。
- ✅ **沙盒架构（wake327更新：隧道已通）**：`.17`→`10.251.36.15` EDA沙盒经 **dual-nix-tunnel** 连通。隧道：`ssh -p 3333 app.e0031982@localhost`→36.15（hostname hfeg0tedaap02）；SSH -L forwarding 把 `localhost:8664/8665/8653/8669/8667/8668`→36.15上`10.129.32.75:同端口`。eda_fastmcp `.env`（`/home/app.e0031982/code/eda_fastmcp/.env`）：`SANDBOX_HOST=127.0.0.1`，`PROXY_PORTS=8664,8665,8653,8669,8668,8652`，`SANDBOX_ENDPOINTS=8664:...,8665:...,8653:...,8669:...`（4端口并行池）。MCP server on :18888。`search_apis`/`get_api_details` 本地✅，`run_code` ✅已通（wake327/328/330 e2e PASS `2+2=4`）。沙盒=远程 EDA 执行环境（pyAether Python+SWIG + Virtuoso SKILL），不可本地复制。隧道README：`/nas_data/app.e0031982/code/dual-nix-tunnel/README.md`。
- 🔴 **R9 verl+SGLang 集成（wake57 发现）**：verl 原生支持 SGLang（`pip install verl[sglang]`），多轮工具调用**仅 SGLang** 支持。配置已从 vLLM 切到 SGLang（`rollout.name: sglang` + `multi_turn: True` + `mode: async`）。EDA 沙盒工具骨架 `baize_posttrain_eda_tool.py` 已创建（BaseTool 子类，dry-run✅）。**R69 修正**：v1 有 3 个 CRITICAL API 不匹配（F01-F03），v2 `baize_posttrain_eda_tool_v2.py` 已修复并 dry-run✅。`baize_posttrain_tool_config.yaml` 已创建（修 F09）。**F14 BLOCKER ✅ 已解决(R70)**：MiniCPM5-2B 用 XML 格式(`<function name=...><param name=...>`), 4 个 SGLang parser 均不匹配 → 设计 MiniCPM5FunctionDetector + monkey-patch `baize_posttrain_minicpm5_parser_patch.py`。单轮 RL 不受影响。
- SFT 语料：✅ v1 `sft_pyaether_corpus.jsonl`(19610对,0污染) + ✅ v2 `sft_pyaether_corpus_v2.jsonl`(19524对,64% has-args,0污染,R24) — **v2 替代 v1 用于训练**
- 🔴 **R60 上下文窗口发现（wake108）**：DeepSeek 全 harness 轨迹平均 **28,339 tokens**（中位 23,906），是 4096 的 6.9x。4096→99%截断 / 8192→98% / 16384→82% / **32768→32%（推荐）** / 65536→3%。KV cache ctx32768 bs8 = 10.5GB/卡，A40 ✅ 可行。SFT 默认 8192 必须升级到 ≥16384；RL 脚本当前**缺失**上下文配置，需补 CONTEXT_LEN=32768。截断→假阴性奖励（8192 下约 29.4% rollout 误判）→支持从 R2 起步。
- 🔴 **R61 吞吐量约束发现（wake109）**：ctx=32768 **non-hybrid 不可行**——KV cache 10.5GB/seq，SGLang budget 18GB → 每 GPU 仅 1 序列，G=8 需 8 个。**ctx=16384 + hybrid engine** 是 72h 窗口唯一可行方案（3.45 steps/hr → ~248 步/72h）。500 步需 ~6 天。Smoke 用 ctx=32768 bs=16 G=4（37min/10步）。RL 配置已补丁至 ctx=16384，SFT 升至 16384。**主 RL 目标步数从 500 降至 200**。
- RL/SFT Parquet：✅ **已转换**（R10）`run/rl_pyaether_synth_v2.parquet`（3347 records, 931KB, verl RLHF 格式: prompt+reward_model+agent_name）+ `run/sft_pyaether_corpus.parquet`（19610 records, 2.7MB, verl SFT 格式: conversation+metadata）
- 🔴 **R11 GRPO 内存校准（wake59 发现）**：当前 `gpu_memory_utilization=0.35` 在多轮 3-turn 场景下**可能 OOM**——KV cache 需 13.8GB > 分配 11.9GB。已校准为 **0.50 + max_num_seqs=12**。训练态 ~12GB/卡，剩余 ~34GB 给 SGLang。4×A40 对 2B 全参 GRPO 是充裕配置（verl 官方 3B LoRA 需 1×H100）。添加 entropy_checkpointing + entropy_chunking 优化。5 级 OOM 降级阶梯已写入 §R11。
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）
- ✅ **cline/zhulong 版本（wake534 补齐，36.15 实测）**：zhulong fork `3.0.29`（`/nasdata/app.e0031982/.local/zhulong/bin/zhulong`）/ cline official `3.0.51`（`/nasdata/app.e0031982/.local/bin/cline`）。PreToolUse hook 源码 `/nasdata/app.e0031982/code/eda_fastmcp/scripts/cline_hooks/PreToolUse`（白名单：MCP 工具 + submit + spawn；run_commands/bash/exec_command 被 overrideInput 改写为 echo 通知；read/list/write 限制在 workspace 内）。
- 🔴 **L4 领域评测命令链（wake339 建立，wake381 更新）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配），5-run eval IN PROGRESS on .17 GPU6(:8096 step105-final)；run 1:Pass@1=6/158=3.8%(code_gen_success=62/fail=92/timeout=4)，run 2 in progress(51/158)；② **designflow**=EDA-Flow-Bench（36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，1173 tasks 4 shards A253/B277/C310/D353，`scripts/run_design_flow_batch.py --session-backend http://127.0.0.1:8666/v1/run_code`，cline at `/nasdata/app.e0031982/.local/bin/cline`，PreToolUse hook anti-cheat）；③ **反向隧道**：.17 PID1008898 `ssh -p3333 -fN -R 18096:localhost:8096 app.e0031982@localhost` → 36.15 `curl localhost:18096/v1/models` returns minicpm5-2b-sft-v39-final ✅；④ **cline providers.json on 36.15**：已配置 `baseUrl http://127.0.0.1:18096/v1 model minicpm5-2b-sft-v39-final apiKey dummy-key`（updatedAt 2026-11-12T19:22）；⑤ **designflow BLOCKER**：prior evals `eval/status_minicpm5_expand30.jsonl` 16 entries ALL verdict=ERROR reason="check.py missing" → run_design_flow_batch.py 未将 task 的 `test` 字段（inline check function）写入 workdir/check.py，需 debug 该脚本或手动注入；⑥ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，BaiZe ckpts 在 .29，36.15 无 GPU → 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: **✅ 能，且 R0+R2 两路 200 步主训均已 COMPLETED，R2 5-run eval 正在跑。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令）。**wake412 起跑成功**（弃用 verl 0.4.0 结论性 BLOCKED，自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`，纯 HF+torch 单 GPU 无 Ray/verl）。**wake413-416 R0 全量 200 步 COMPLETED**（cheat=0/3200 红线绿，但 dynamics 偏负：reward 全程≈0/frac_nonzero≈0/nz 0.97 塌缩⇒ group std≈0⇒adv≈0⇒无梯度方向 ⇒ R0=诚实负结果，proxy reward 不产生有方向信号。⚠️wake463 修正：此前"mean_ratio==1.0 policy 不动"依据无效——ppo_epochs=1 下 mean_ratio==1.0 为结构性 logging artifact，非 policy 不动证据；R0 负结果只挂在 reward 无方向信号上）；R0 eval 链因 4 并发 vLLM serve OOM 断裂无数据，决策门 §R425 C 合规判分支2 missing-JSON）。**wake429-433 R2+sandbox-exec 200 步主训 COMPLETED**（@01:05:36，cheat=0/1600 红线绿，real signal+梯度流动[84/200 步 posadv>0, grad_norm 均值1.65 policy 实更新]但 reward step100 后平台/回落 seg 0.053→0.111→0.106→0.090，overall 0.0901）。**wake433 R2 global_step_200 serve GPU7:8095 READY + 5-run eval RUNNING**（autofire chain PID2322797，158题 Pass@1，~12h ETA~13:00→5run_rl_analysis_R2.json，vs step105 0.0304±0.0083 McNemar+bootstrap）。下一=5-run eval 完→R2 真实数字→显著则里程碑报告/负则诚实负结果+换奖励。GPU0-3=root；GPU4=base serve；GPU5=空闲(已 teardown)；GPU6=step105-final baseline serve；GPU7=R2 global_step_200 serve(:8095)。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。GPU0-3=root SGLang(不可动)；GPU4=base MiniCPM5-2B serve(:8098)；GPU5=vision R9 占用(非本线,不碰)；GPU6=step105-final baseline serve(:8096)；GPU7=R2 global_step_200 serve(:8095,5-run eval RUNNING)。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake476–wake522（R476-R522）已归档 → daily-memories-posttrain/2026-11-{14,15}.md（基线 RCA v1+v2 交付+3.04%±0.83% 复核+36.15 重测起跑+A/B 裁决 A+归因链 path-bug 根因+rescue 三脚本修复[grep -a/绝对 benchmark/case 尾斜杠]+独立 helper bpt_attribution_manual_rescue.sh+A1 干净 0/40 恢复[12.66% 交叉污染排除]+postmortem 复核一至十五度 PASS+隧道恢复+归因链起跑 A1 23:30+复盘报告交付 commit 375e11bf7；详见 EXPERIMENTS §R485-§R522/§R-Attribution-overnight 各节）。

> 📦 wake523–wake531（R523–R531）已归档要点 → postmortem 十七~二十一度复核 PASS + A1=0/40·A3=2/40 干净复算 + P0base auto-rescue 去风险 + 归因夜报 HTML 交付 + P0-dev McNemar 对比脚本 + ETA 诚实修正 + baseline_dev 0/79 确认（详见 EXPERIMENTS §R523-§R531 / daily 2026-11-15）。
> 📦 wake537/wake538（R537/R538）已归档要点 → 双链健康监控+前置就绪验证（详见 EXPERIMENTS §R537/§R538 / daily 2026-11-15）。

> 📦 wake540–wake561（R540-R561）已归档 → daily 2026-11-15。均为 08:1x 令 zhulong 5-run 链健康监控/复核心跳轮（run2 64→148/158→collapse 0.0% / run3 38→158→collapse 0.0% / run4 31→120/158）+交付物完整性复核 PASS+报告§10 渐进刷新+收口脚本/归因聚合器交付+MEMORY 体积归档。无新结论（结论见 wake476-539 块与进度快照）。详见 daily 2026-11-15 wake540-561。


> 📦 wake529–wake539（R529-R539）已归档 → daily 2026-11-15。要点结论（不改）：①postmortem 复核十六~二十二度 PASS + P0 dev compare/rescue 工具链去风险。②08:1x 令「158 评测改用 zhulong 方式」首执行：36.15 run1=18.99% 本就是 zhulong 口径(hook 白名单 run_commands 禁用)+cline 版本补齐(3.0.29/3.0.51)+再归因四问[真 MCP 拒绝 6.0%/run_code 3.0%/静默 45=28.5%/+15.95pp]+旧报告 PENDING-REMOTEST banner。③zhulong 基线 5-run 链起跑+口径六项全量复核 PASS。④沙盒非确定性发现+双轨 compare 方法论。⑤R2 诚实负结果报告交付（4-run mean=0.47%±0.61% vs step105 3.04% Δ=−2.56pp Wilcoxon p=0.0025 decisively 负）。详见 EXPERIMENTS §R529-§R539 / daily 2026-11-15。

> 📦 wake1–wake432 (R1–R432) 已归档 → daily-memories-posttrain/2026-11-{06..14}.md（P0/P1/P2/SDPA/cu124 venv/verl/SGLang/Parquet/内存预算/500题/反作弊/替身RL预演/吞吐量/RL hooks/SFT脚本/serve占位/沙盒/schematic API+v8-v23语料+污染闸门/minicpm5 tool-call parser/API Validator+v11-v38 corpus/SFT v11v38 CONVERGED/sandbox e2e+RL launch-ready/designflow baseline 0%/v39 SFT/step105 baseline 0.0304±0.0083 locked/弃verl自写GRPO loop/R0 200步COMPLETED诚实负结果[reward无方向]/R2+sandbox 200步起跑+cheat=0+eval autofire chain落地；R-content 详见 EXPERIMENTS 归档）。

> 📦 wake433-447 已归档 → daily-memories-posttrain/2026-11-14.md（R2 200步COMPLETED+serve GPU7:8095+5-run eval 起跑；R434-447 run1 23→70/158 监控，0 infra 错误）。

> 📦 wake448-wake475 已归档 → daily-memories-posttrain/2026-11-14.md（R448-R475 5-run eval 健康监控 run1 COMPLETED Pass@1=0.63%(单run不预判)+run2 RUNNING；R461 fsync 修复+R463 RL 动力学指标重释[mean_ratio==1.0=ppo_epochs=1 logging artifact]；0 infra 错误，eval 全自治。详见 EXPERIMENTS §R448-§R475）。

> 📦 wake475 (R475 5-run eval run2 监控心跳轮) 已归档 → daily-memories-posttrain/2026-11-14.md（run1 COMPLETED Pass@1=0.63% 复核+run2 健康；详见 EXPERIMENTS §R475）。








> 📦 wake562–568 已归档 → daily-memories-posttrain/2026-11-15.md（均 08:1x 令 zhulong 5-run 链健康监控/误判撤回轮；彼时 run2/3/4=0.0% 后经 wake570-573 RCA 证伪=管线 ws/no-ws 路径失配非模型 collapse；wake566/568 显式 SUPERSEDED）。

> 📦 wake581/582（2026-11-16 10:5x–11:3x · posttrain eval/rca:）已归档要点 → 23:0x RCA 交付+独立复测全 PASS+按 item5 重启干净 5-run 链。详见 daily 2026-11-16。

> 📦 wake584（2026-11-16 13:0x · posttrain rca:）已归档要点 → 23:0x RCA 全六项复核齐备且在 origin + 干净 5-run 链 PID912262 健康(run5 GATING)+MEMORY 体积维护(归档 wake562-568)。详见 daily 2026-11-16。

> 📦 wake587（2026-11-16 15:0x · posttrain rca:）已归档要点 → 23:0x RCA 监控复核轮 + 链死因更正（PID912262 非 SIGHUP，系 14:05 wake 误读 item1 自行 kill；wake583-586「父SIGHUP」诊断有误）。沙盒仍忙→不重启链待用户定夺。详见 daily 2026-11-16 wake587。

> **wake590（2026-11-16 17:2x · posttrain rca:）**：纪律纠偏轮——停未授权起新 run 的 `baize_posttrain_clean_5run.sh`(违反 23:0x item1)+恢复 run2 封存(git diff HEAD 空)；详见上方 wake590 块 + daily 2026-11-16 wake590。

> 📦 wake591/wake592（2026-11-16 ~18:0x–18:33 · posttrain rca:）已归档要点 → 23:0x RCA 交付物执行复测全六项 PASS（报告0外链0script/rca_verify8=8行/exec43/28/35≫1证伪collapse/产物全在位/run5 INVALID-partial/无未授权新run/git synced）。结论不变（主因=管线 ws-no-ws 路径失配非模型 collapse；干净回补 run2/3/4=4.43/2.53/3.80%）。详见 daily 2026-11-16 wake591/592。

> 📦 wake593/wake595/wake600（2026-11-16 18:52–22:0x · posttrain 5run:）已归档要点 → 18:3x 令授权恢复干净 5-run，按唯一允许方式起跑链 PID1192182（幂等跳过 run1-4，run5 进 GATE 等沙盒）；wake595/600 为 global-gate 监控心跳轮（zhulong eval≪6h 不升级，git synced）。**后已被 wake601+ 的 share-8090-pool 路径取代**（链 PID1192182→PID1354030）。详见 daily 2026-11-16 wake593/595/600。
