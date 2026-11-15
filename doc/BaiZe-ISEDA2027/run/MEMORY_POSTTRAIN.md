# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

> 🔧 **隧道复盘结论（wake507 · 2026-11-14 23:5x · posttrain infra:）**：隧道**坏过现已恢复**——最后通点 **20:41:50**（36.15 run1 完整 18.99% 落盘）/ 首断点 **22:4x wake505** / 恢复确认 **23:26 wake506**（中继 tunnel.ps1 重新在线）/ 故障域=**中继侧①+②** / **非本线造成亦非本线修复**。报告 `reports/report_infra_tunnel_postmortem_zh.html`。[wake复验 2026-11-15 07:43：三验证命令实测全 PASS + anchor final_report mtime=20:41:50 pass_rate=0.18987=18.99% 实测确认。postmortem 任务完成。]

## 进度快照

- PHASE: posttrain-wake500（✅ **归因前提核验PASS:5×跳升确属同模型step105不同环境比较**[curl .17:8096=id=minicpm5-2b-sft-v39-final root=global_step_105;36.15经反向隧道18096→.17:8096;final_report model_name=zhulong_deepseek_v32=config.yaml active_model陈旧标签非实际模型];**36.15 run1逐题画像[🔴wake500订正:完整run1=18.99%(30/158)/gen成功36/gen_fail121/生成后通过率83.3%;六类分型T6_tool_format_genfail121头号(76.6%);全局拒绝1304[run_commands1048/missing-field527/string-not-array321];wake499的15.82%/29/25/86.2%是20:03部分副本,已superseded]**;v2 RCA已交付[e434f6def];**双 eval 并行 RUNNING**:36.15重测 run1 DONE=18.99%(完整,wake500订正;旧15.82%为部分副本)/run2 RUNNING(PID2747266) + .17 R2 5-run chain PID2322797健康;v2 RCA核心:MCP工具6051+submit13699/91.77%报错/C5_degenerate_pass479/790=60.6%头号/检索333API仅19进代码5.7%）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-433✅;R411-R428✅(verl BLOCKED→自写GRPO loop/R0 200步COMPLETED+cheat=0/3200/step105 baseline 0.0304±0.0083 locked/eval 自治链路+决策门预注册+5-run并行不可行/R2 autofire chain 落地[全量详见 daily-memories 2026-11-13/14]);R431✅(R2 监控 step100+cheat=0/400+step50 ckpt)；R432✅(R2 主训监控 step151/200 健康[奖励平台期诚实修正:step100 后 mean_reward 0.113→0.105 平台/回落,纠正 wake431 单调上升]+cheat=0/1200 三次落盘+step150 ckpt+eval chain 健康等待)；R433✅(R2 200步主训 COMPLETED[cheat=0/1600 红线绿终值+global_step_200 ckpt 5.03GB+全200步奖励平台后回落 0.1195→0.0798]+GPU5 step60 serve 手动 teardown 完成 OOM mitigation[kill_gpu_serve child-PID bug 实证]+R2 serve GPU7:8095 READY[model minicpm5-2b-grpo-R2-step200]+5-run eval RUNNING 01:08:13 自动链 PID2322797 ~12h ETA~13:00)；R434-R452✅(5-run eval 健康监控 run1 ~23→94/158 渐进,8 worker,GPU7 87-100%util,3 并发 serve 稳定,GPU5=vision R9 占用,0 traceback/OOM/infra 错误,eval 全自治无人工动作[全量详见 daily-memories 2026-11-14])
- 当前动作: wake564 R564:**08:1x 令 zhulong 5-run 链健康复核(run4 RUNNING 101/158 codegen @20:28)**。链 PID43678 活(etimes≈19588s≈5.4h)，run4 batch 2026_1115_183438 on 36.15：run_cline_script PID1910477/1910486 活(etimes≈5563s≈1.5h)，-p 8，**70/158 code dirs @20:06**(~44%)，stats/success=63/failure=7/timeout=0 活跃写入(latest mtime 20:03:14)。**run4 codegen 健康(success=63/70≈90%，非 run2/run3 degenerate collapse)**。端点 :8096(step105)/隧道 :3333 实测 PASS。run1=18.99%+run2=0.0%+run3=0.0% 幂等跳过→run4 RUNNING(codegen ETA~21:40)→run5 待跑→全 5-run ETA~01:00+→链尾自动产 5run_zhulong_baseline_analysis.json→手动 `bash bpt_zhulong_5run_finalize.sh --num-runs 5` 出 Q1-Q4 跨5run聚合+新旧同表→回填报告§10(已刷新 run4=70/158)。interim n=3 mean=6.33%±10.96%[18.99,0,0] vs old 3.04%±0.83% Δ+3.29pp(McNemar discordant52)。九项达成延续 PASS；令明确「跑起来后正常 push 别等全跑完」⇒ 重测 RUNNING 即达标；唯一未完成=5-run 链 run4/5 自治收尾。详见 daily 2026-11-15 wake563。
- wake533 R533（已归档）:沙盒非确定性发现[baseline_dev direct 2/79 vs rescue 0/79,单 seed delta<沙盒方差⇒不可定论]+双轨 compare 方法论。详见 EXPERIMENTS §R533-sandbox-nondeterminism / daily 2026-11-15 wake533。
- 下一步: ①**zhulong 5-run 基线链 RUNNING**(PID43678,copy-path bug 已修+幂等；run1=18.99%+run2=0.0% 已幂等跳过+run3 RUNNING batch 2026_1115_144001 on 36.15[~81% 128/158],run4/5 串行 ETA~17:45/20:30/23:40)→链尾自动产 5run_zhulong_baseline_analysis.json(全5run mean±std+McNemar vs旧.17 5-run 3.04%±0.74%)→手动 bash bpt_zhulong_5run_finalize.sh --num-runs 5 出归因聚合+同表→更新报告§10+新旧基线同表并列(新基线标「zhulong 口径」,旧标「口径非zhulong·含被禁run_commands」) ②run2=0.0% 已记入 attribution_zhulong_5run_attribution.json(run2_collapse_note:非infra,系2B模型 degenerate non-generation,36→1 swing 证实高方差) ③R2 4-run mean≈0.475% decisively 负已有(报告 report_posttrain_rl_surrogate_zh.html 预生成 4/5);run5 被 kill 不补 ④GPU7:8095 R2 serve 可 teardown 释放 ⑤kill_gpu_serve child-PID bug待chain空闲修 ⑥MEMORY 体积≈32KB(达标)
- 阻塞: ✅ **R2 200步主训 COMPLETED** + **R2 5-run eval run1-4 DONE mean≈0.475% decisively 负**(run5 被 kill 释放给 08:1x 最高优先令,R2 链 PID2322797 全树已清)。**R0=诚实负结果**(proxy reward 不移动 policy)。RL 基座=MiniCPM5-2B/SFT step105。GPU0-3=root;GPU4=base serve;GPU5=vision R9 占用(非本线,不碰);GPU6=step105-final baseline serve(:8096,zhulong 基线用);GPU7=R2 step200 serve(:8095,R2 eval 已完可 teardown)。沙盒经 dual-nix-tunnel 通。verl 结论性 BLOCKED 不再尝试。
- 本轮新增产出: R559✅(08:1x 令 zhulong 5-run 链健康复核[run3 codegen COMPLETE 158/158 task dirs,stats 18:00 后活跃,MCP/RAG 回路健康,run_commands hook 拒绝确认防泄题]+九项达成核验延续 PASS[wake558 已全 PASS,重测 RUNNING 即达标]); R557✅(08:1x 令 zhulong 5-run 链健康监控[run3 ~99% codegen 157/158]+reattribution 报告§10 刷新落盘[15548B ends </html>]+端点实测 PASS); R556✅(run3 ~81% 128/158+报告§10 刷新); R549✅(run2 打分期+MEMORY 体积归档); R548✅(run2 148/158+端点 PASS); R547✅(收口脚本 arg-parse 修复); R545✅(收口脚本交付[dry-run Δ+15.95pp,McNemar discordant52]+前置就绪); R544✅(eda_fastmcp 代码只读核验+run1 真归因钉死[run_commands 80.4% 系 hook 设计非能力]); R543✅(5-run 归因聚合器); R541✅(交付链去风险); R539✅(R2 诚实负结果报告); R536✅(口径六项复核); R535✅(5-run链起跑); R534✅(再归因); R533✅(沙盒非确定性); R532/R518/R516/R504✅(已归档 daily 2026-11-14/15)
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ R0 200步 COMPLETED 诚实负结果 + ✅ R2 200步 COMPLETED(cheat=0/1600) + ✅ R2 5-run eval run1-4 DONE mean≈0.475% decisively 负(run5 被 kill 因 08:1x 令最高优先);R2 5-run 终版报告用 4-run 数据+标注;🔴 2026-11-15 08:1x「158 评测改用 zhulong 方式」——✅ wake534 再归因 + ✅ wake536 口径复核 + ✅ wake542 链修复并起跑 RUNNING(run1=18.99% 已有+run2-5 串行 on 36.15,ETA~21:00-23:00)→5run_zhulong_baseline_analysis.json→更新报告§10+新旧基线同表并列;L4 2026-11-12(zhulong step105 ✅5/5 0.0304±0.0083;designflow base 5/5=0%)
- git: super_intelligence_2035(main=origin,synced via pull --rebase --autostash);本轮交付(wake542: baize_posttrain_zhulong_baseline_5run_chain.sh 修复[gate self-match+PYTHON/EVAL_FW_DIR/bash -lc]+MEMORY wake542 心跳);只 add 本线文件,不用 -A
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

> 📦 wake540 R540 已归档要点 → 双链健康监控+08:1x 令交付物完整性核验 PASS（详见 EXPERIMENTS §R540 / daily 2026-11-15 wake540）。

> 📦 wake541 R541 已归档要点 → 08:1x 令交付链端到端去风险 PASS（R2 run5 codegen 活跃+zhulong GATE 健康+反向隧道+serve 实测 PASS+分析脚本 dry-run PASS[delta_pp=+15.95]+5 份旧报告 banner 复核无缺口；详见 daily 2026-11-15 wake541）。

> 📦 wake543 R543 已归档要点 → 08:1x 令 zhulong 口径链健康复核 + 5-run 归因聚合器 `bpt_zhulong_5run_attribution_aggregate.py` 交付（run1-only dry-run PASS：Q1 真 MCP 6.3%/Q2 run_code 2.0%/Q3 silent 45/Q4 +15.95pp）。详见 daily 2026-11-15 wake543。

> 📦 wake544 R544 已归档要点 → 08:1x 令 eda_fastmcp 代码只读核验（PreToolUse hook 白名单= MCP+submit+spawn+workspace 内 read/list/write；run_commands 不在白名单→/dev/null no-op 防泄题）+ run1 真归因钉死（rejected 1304 中 run_commands 1048=80.4% 系 hook 设计非能力；真 MCP 拒绝≈73；run_code 拒绝率 2.0%；MCP 成功调用重⇒佐证用户「归因前提站不住」）。详见 daily 2026-11-15 wake544。

> 📦 wake546 R546 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run2 110/158)+再归因报告同步 run/reports/(banner 链接缺口修复)+交付物完整性复核 PASS。详见 daily 2026-11-15 wake546。

> 📦 wake545 R545 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run2 64/158)+收口脚本 bpt_zhulong_5run_finalize.sh 交付[dry-run PASS:delta_pp=+15.95]+前置就绪验证[双脚本 py_compile/旧5run数据在位/5旧报告banner]+run1真归因钉死[真MCP6.3%/run_code2.0%/silent45/+15.95pp]。详见 daily 2026-11-15 wake545。

> 📦 wake542 R542 已归档要点 → 08:1x 令 zhulong 口径 5-run 基线链修复并起跑 RUNNING（R2 链全树 kill[4-run decisive 负]+修复 gate self-match bug[pgrep→[r]grep]+修复 36.15 远程环境三缺失[PYTHON/EVAL_FW_DIR/bash -lc]+zhulong 基线链 PID4099520 RUNNING run2 on 36.15）。详见 daily 2026-11-15 wake542。

> 📦 wake547 R547 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run2 127/158)+收口脚本 arg-parse 修复[set -u 无参崩→while/case 标准循环,验证 bash -n/--help/--dry-run/--bogus rc=2 全 PASS]。详见 daily 2026-11-15 wake547。
> 📦 wake548 R548 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run2 148/158)+依赖端点实测 PASS[:8096/18096/3333]+交付物完整性复核 PASS[reattribution 报告+四问JSON+5旧报告banner]。详见 daily 2026-11-15 wake548。
> 📦 wake549 R549 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run2 打分期)+MEMORY 体积归档(36KB→≤32KB)。详见 daily 2026-11-15 wake549。
> 📦 wake550 R550 已归档要点 → 08:1x 令 zhulong 5-run 链 copy-path bug 修复[final_report/execution_results 在 output_evaluation/ 非 batch 目录]+run2 救援=0.0%[degenerate non-generation,36→1 swing 证高方差]+幂等跳过修复+链重启 PID43678[run1=18.99%+run2=0.0% 跳过,run3 RUNNING batch 2026_1115_144001]。interim mean=9.49%±9.49% vs old 3.04% Δ+6.45pp。详见 daily 2026-11-15 wake550。
> 📦 wake551 R551 已归档要点 → 08:1x 令 zhulong 5-run 链健康监控(run3 起步 38/158)+磁盘实测足量+无沙盒争用。详见 daily 2026-11-15 wake551。
> 📦 wake552/wake553（R552/R553）已归档要点 → 08:1x 令 zhulong 5-run 链健康监控(run3 41%→53%)+PreToolUse hook 只读复核 PASS(L138 run_commands→/dev/null no-op 防泄题)+交付物完整性核验 PASS。详见 daily 2026-11-15 wake552/wake553。

> 📦 wake554 R554 已归档要点 → 08:1x 令 zhulong 5-run 链健康监控(run3 ~64%)+reattribution 报告§10/§8 刷新（**注：wake554 报告编辑未持久化落盘，wake555 已实测重做并验证 mtime/标签平衡**）。详见 daily 2026-11-15 wake554。

> 📦 wake556 R556 已归档要点 → 08:1x 令 zhulong 5-run 链健康监控(run3 ~81% 128/158)+reattribution 报告§10 run3 行刷新落盘(15548B)。详见 daily 2026-11-15 wake556。

> 📦 wake555 R555 已归档要点 → 08:1x 令 zhulong 5-run 链健康监控(run3 ~72%)+reattribution 报告§10/§8 实测刷新落盘（纠正 wake554 未持久化；§10 进度表 run1=18.99%/run2=0.0% collapse/run3 RUNNING/run4-5待跑，interim n=2 mean=9.49%±9.49% vs old 3.04% Δ+6.45pp）。详见 daily 2026-11-15 wake555。

> 📦 wake558 R558 已归档要点 → 08:1x 令 eda_fastmcp 四文件只读核验(PreToolUse 白名单=MCP+submit+spawn,run_commands→/dev/null no-op 防泄题;run_cline_script 口径钉死)+九项达成核验全 PASS。详见 daily 2026-11-15 wake558。
> 📦 wake559 R559 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run3 codegen COMPLETE 158/158)+run1 真归因复核(pass_rate=0.1899,30/158)+九项达成延续 PASS。详见 daily 2026-11-15 wake559。

> 📦 wake560 R560 已归档要点 → 08:1x 令 zhulong 5-run 链 run3=0.0% COMPLETED(第二次 degenerate collapse,gen_success=1/fail=157)+run4 RUNNING(31/158@19min)+报告§10/§8 刷新落盘(16085B)+interim n=3 mean=6.33%±10.96%[18.99,0,0] vs old 3.04% Δ+3.29pp。详见 daily 2026-11-15 wake560。

> 📦 wake561 R561 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run4 RUNNING 52/158)+交付物完整性核验 PASS(reattribution 报告+四问JSON+5旧报告banner)。interim n=3 mean=6.33%±10.96%[18.99,0,0] vs old 3.04% Δ+3.29pp。详见 daily 2026-11-15 wake561。


> 📦 wake539 R539 已归档要点 → R2 诚实负结果报告生成器 bpt_rl_surrogate_5run_report.py 交付 + 初步报告 report_posttrain_rl_surrogate_zh.html 落盘（R2 4-run mean=0.47%±0.61% vs step105 3.04%±0.83%，Δ=−2.56pp，Wilcoxon p=0.0025，decisively 负；proxy reward 与任务正确性未对齐为主因）。详见 EXPERIMENTS §R539 / daily 2026-11-15 wake539。

> 📦 wake536 R536 已归档要点 → zhulong 基线 5-run 链口径六项全量复核 PASS（CLI_AGENT=zhulong 默认+PreToolUse hook+prompt 模板+反向隧道 18096+-b flag 合法+benchmark 158 行+cline 版本）+ R2 run1-4 DONE mean≈0.475% decisively 负 + run5 RUNNING ETA~10:00-10:30 + 口径差异提醒（R2 .17 口径 vs zhulong 基线 36.15 口径不可比）（详见 EXPERIMENTS §R536 / daily 2026-11-15 wake536）。
> 📦 wake535 R535 已归档要点 → zhulong 基线 5-run 链起跑(GATE 避让 R2,照抄 zhulong 入口,run1=18.99% 已有+run2-5 待跑,ETA~11-16)+分析脚本 bpt_zhulong_baseline_5run_analysis.py 预演验证 PASS（详见 EXPERIMENTS §R535 / daily 2026-11-15 wake535）。
> 📦 wake534 R534 已归档要点 → 08:1x 用户令「158 评测改用 zhulong 方式」已执行：36.15 run1=18.99% 本就是 zhulong 口径(hook 白名单 run_commands 禁用)+cline 版本补齐(3.0.29/3.0.51)+再归因四问[真 MCP 拒绝 6.0%/run_code 3.0%/静默 45=28.5%/+15.95pp]+旧报告 4 份 PENDING-REMOTEST banner+新报告（详见 EXPERIMENTS §R534 / daily 2026-11-15 wake534）。
> wake533 R533（已归档）:沙盒非确定性发现+双轨 compare 方法论[direct-vs-direct/rescue-vs-rescue,两轨一致才采信]+报告§4 caveat+R2 4-run mean 0.475% decisively 负。详见 EXPERIMENTS §R533-sandbox-nondeterminism / daily 2026-11-15 wake533。
> 📦 wake532 R532 已归档要点 → postmortem 复验 PASS + P0 dev compare/rescue 工具链 p0_dev 路径去风险（rescue --arm-dir 口径订正 + auto-rescue dev 臂有效 + compare py_compile/help PASS + baseline_dev 复核；详见 EXPERIMENTS §R532-p0dev-derisk / daily 2026-11-15 wake532）。


> 📦 wake529 R529 已归档要点 → postmortem 二十二度复核 PASS + P0 dev 链进度精化 + 阻塞诚实标注（详见 EXPERIMENTS §R529 / daily 2026-11-15）。

> 📦 wake1–wake186 (R1–R139) 已归档 → daily-memories-posttrain/2026-11-{06,07,08,09,10}.md（P0/P1/P2/SDPA/cu124 venv/verl/SGLang/Parquet/内存预算/500题/反作弊/替身RL预演/吞吐量等全量调研；R-content 详见 EXPERIMENTS 归档）。



> 📦 wake189-wake245 (R142-R176) 已归档 → daily-memories-posttrain/2026-11-10/11.md（RL hooks/SFT脚本/Phase1就绪/serve占位/沙盒/SFT完成/RL dry-run；R-content 详见 EXPERIMENTS）。
> 📦 wake246-wake262 (R177-R193) 已归档 → daily-memories-posttrain/2026-11-11.md（R177-R183 schematic API修正+v8~v13语料+污染闸门 / R184-R193 v14-v23 语料：ae*/emy*/db* lifecycle+blind 全清/Mde* sweep-platform/coverage 59-67%）。


> 📦 wake263-wake316 已归档 → daily-memories-posttrain/2026-11-11/12.md（R291 SFT语法95.6%vsBase62.8%/P0 D1-D6终验；R302-316 minicpm5 tool-call parser+上下文溢出修复；v11-v35 语料943对；详见 EXPERIMENTS）。

> 📦 wake320–wake336 已归档 → daily-memories-posttrain/2026-11-12.md（API Validator+v11-v38 corpus 1344 pairs+SFT v11v38 CONVERGED+serve+post-SFT eval LAUNCHED；详见 EXPERIMENTS）。
> 📦 wake337–wake397 已归档 → daily-memories-posttrain/2026-11-12/13.md（sandbox e2e+RL launch-ready/designflow baseline 0%/v39 SFT训练+eval pipeline autonomous/R397 run2 Pass@1=1.9%；详见 EXPERIMENTS）。

> 📦 wake398-wake432 已归档 → daily-memories-posttrain/2026-11-13/14.md（step105 baseline 0.0304±0.0083 locked/弃verl自写GRPO loop/R0 200步COMPLETED诚实负结果[reward无方向]/R2+sandbox 200步起跑+cheat=0+eval autofire chain落地；详见 EXPERIMENTS）。

> 📦 wake433-447 已归档 → daily-memories-posttrain/2026-11-14.md（R2 200步COMPLETED+serve GPU7:8095+5-run eval 起跑；R434-447 run1 23→70/158 监控，0 infra 错误）。

> 📦 wake448-wake475 已归档 → daily-memories-posttrain/2026-11-14.md（R448-R475 5-run eval 健康监控 run1 COMPLETED Pass@1=0.63%(单run不预判)+run2 RUNNING；R461 fsync 修复+R463 RL 动力学指标重释[mean_ratio==1.0=ppo_epochs=1 logging artifact]；0 infra 错误，eval 全自治。详见 EXPERIMENTS §R448-§R475）。

> 📦 wake475 (R475 5-run eval run2 监控心跳轮) 已归档 → daily-memories-posttrain/2026-11-14.md（run1 COMPLETED Pass@1=0.63% 复核+run2 健康；详见 EXPERIMENTS §R475）。








> 📦 wake562 R562 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run4 RUNNING 65/158)+报告§10 run4 进度刷新落盘。interim n=3 mean=6.33%±10.96%[18.99,0,0] vs old 3.04% Δ+3.29pp。详见 daily 2026-11-15 wake562。

> 📦 wake563 R563 已归档要点 → 08:1x 令 zhulong 5-run 链健康复核(run4 70/158 codegen)+报告§10 刷新。详见 daily 2026-11-15 wake563。

> 🔧 **wake564 R564（2026-11-15 20:28 · posttrain eval:）**：**08:1x 令 zhulong 5-run 链健康复核(run4 RUNNING 101/158 codegen)+报告§10 run4 进度刷新**。①链健康：PID43678 活(etimes≈20904s≈5.8h)，run4 batch 2026_1115_183438 on 36.15：run_cline_script PID1910477/1910486 活(etimes≈6881s≈1.9h)，-p 8，**code/ 目录 101 子目录 @20:28**(~64%)，.task_queue 仍有 57 任务排队(099+)，l1_injection mode=no memory bank。**run4 codegen 健康（非 run2/run3 degenerate collapse）**。端点 :8096(step105)/隧道 :3333 实测 PASS。②报告§10 run4 行刷新落盘(codegen 70/158→101/158,footer wake564)。③交付物完整性延续 PASS(reattribution 报告+四问JSON attribution_zhulong_5run_attribution.json+5旧报告 PENDING-REMOTEST banner)。④interim n=3 mean=6.33%±10.96%[18.99,0,0] vs old 3.04%±0.83% Δ+3.29pp(McNemar discordant52)；run1=18.99%/run2=0.0%/run3=0.0% 实测确认。⑤九项达成延续 PASS；令明确「跑起来后正常 push 别等全跑完」⇒ 重测 RUNNING 即达标；唯一未完成=5-run 链 run4/5 自治收尾 ETA~01:30+。详见 daily 2026-11-15 wake564。
