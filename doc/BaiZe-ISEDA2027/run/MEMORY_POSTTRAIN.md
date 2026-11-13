# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake437（2026-11-14 R437: **5-run eval RUNNING 健康监控[run1 ~32/158 任务(success26/fail1/timeout5),8 worker,GPU7 97%util,0 真实 traceback/OOM,3 并发 serve 稳定,GPU5 空闲,自动链 PID2322797,ETA~13:00]**）；前轮 R436: run1 ~26/158；R435: run1 ~28/158；R434: run1 ~23/158；R433: R2 200步主训 COMPLETED+OOM mitigation+R2 serve GPU7:8095 READY+5-run eval 起跑；R432: R2 监控 step151+奖励平台期修正+cheat=0/1200；R431: R2 监控 step100+cheat=0/400；R430: R2 监控 step48+eval chain 落地；R429: R0 诚实负结果+决策门分支2+R2 起跑 step1
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-433✅;R411-R428✅(verl BLOCKED→自写GRPO loop/R0 200步COMPLETED+cheat=0/3200/step105 baseline 0.0304±0.0083 locked/eval 自治链路+决策门预注册+5-run并行不可行/R2 autofire chain 落地[全量详见 daily-memories 2026-11-13/14]);R431✅(R2 监控 step100+cheat=0/400+step50 ckpt)；R432✅(R2 主训监控 step151/200 健康[奖励平台期诚实修正:step100 后 mean_reward 0.113→0.105 平台/回落,纠正 wake431 单调上升]+cheat=0/1200 三次落盘+step150 ckpt+eval chain 健康等待)；R433✅(R2 200步主训 COMPLETED[cheat=0/1600 红线绿终值+global_step_200 ckpt 5.03GB+全200步奖励平台后回落 0.1195→0.0798]+GPU5 step60 serve 手动 teardown 完成 OOM mitigation[kill_gpu_serve child-PID bug 实证]+R2 serve GPU7:8095 READY[model minicpm5-2b-grpo-R2-step200]+5-run eval RUNNING 01:08:13 自动链 PID2322797 ~12h ETA~13:00)；R434✅(5-run eval 健康监控 wake:run1 ~23/158 任务,8 cline worker,GPU7 98%util,0 真实 traceback/OOM,3 并发 serve 稳定[GPU4 base/GPU6 step105-final/GPU7 R2],GPU5 空闲,autofire chain PID2322797 健康,ETA~13:00→5run_rl_analysis_R2.json,本轮无人工动作=eval 全自治)；R435✅(5-run eval 健康监控 run1 ~28/158,8 worker,GPU7 89%util,3 并发 serve 稳定,GPU5 空闲,0 traceback/OOM,本轮无人工=eval 全自治)
- 当前动作: wake437 R437:**5-run eval RUNNING 健康监控（本轮=纯监控，eval 全自治，无人工动作）**。①**eval 链健康实测**(autofire chain PID2322797 存活 etime≈5645s;R2 serve GPU7:8095 curl /v1/models 返回 minicpm5-2b-grpo-R2-step200,GPU7=39244MiB/97%util;3 并发 serve[GPU4 base:8098/GPU6 step105-final:8096/GPU7 R2:8095]全稳;GPU5 空闲 3MiB)②**run1 进度**(batch_id 2026_1114_010813,eval run1 PID2354141 etime≈3431s @01:08:13 起 ~57min,8 cline worker active,stats counters success=26/failure=1/timeout=5=32/158 已完成,`.task_queue` 158→118 行[较 wake436 的 124 行 +6],code/ 43 文件,batch_cline.log @02:03:14 持续增长[worker-1/2 任务 037/038/039/040 成功完成],0 真实 Python traceback/CUDA OOM/Killed[worker cline.log grep=0;WARNING Exit Code:1/超时 2500s=模型能力不足的 task 失败,非 infra 错误])③**前轮 R434/R435/R436 已归档**:同口径监控 wake run1 ~23/28/26/158。④本轮未编辑任何运行中脚本/未碰 GPU0-3/GPU4/GPU6 既有 serve/eval 链;kill_gpu_serve bug 待 chain 空闲时修(不编辑运行中脚本)。详见 EXPERIMENTS §R437。
- 下一步: ①**5-run eval 自动链 RUNNING**(~12h,ETA~13:00,autofire chain PID2322797 自动,无需人工)→5run_rl_analysis_R2.json 出 R2 真实数字(vs step105 baseline 0.0304±0.0083,McNemar+bootstrap) ②**R2 显著提升**(McNemar p<0.05 或 bootstrap ci_low>0)→里程碑报告 `reports/report_posttrain_rl_surrogate_zh.html`(标「替身预演」);R2 无提升/退化(**平台化使此分支概率上升**)→诚实负结果+换奖励/任务定义(§用户令#4),最终结论「MiniCPM5-2B 上 RL 能否显著提升 PyAether 脚本能力」本身就是交付物 ③R2 config vs R0 唯一差异=B(1 vs 2)+reward arm(R2 sandbox-exec vs R0 proxy),G/ctx/lr/kl 不变,论文需注明 ④kill_gpu_serve child-PID bug 待 chain 空闲时修(L102-118:walk ppid 到 vllm serve 父进程或改 pgrep -f '--port <PORT>')
- 阻塞: ✅ **R2 200步主训 COMPLETED**(PID2314192 已退出@01:05:36,cheat=0/1600,global_step_200 ckpt 已 serve)+✅ **5-run eval 自动链 RUNNING**(PID2322797,label=grpo_R2_step200,GPU7:8095,~12h ETA~13:00→5run_rl_analysis_R2.json)。**R0=诚实负结果**(proxy reward 不移动 policy,训练侧 dynamics 已证;eval 因 infra 断裂[OOM 杀 serve+链]无数据,决策门 §R425 C 合规判分支2 missing-JSON)。RL 基座=MiniCPM5-2B/SFT step105(用户令解除 BaiZe 基模依赖)。GPU0-3=root;GPU4=base serve;GPU5=空闲(step60 serve 已 teardown);GPU6=step105-final baseline serve;GPU7=R2 global_step_200 serve(:8095)。沙盒经 dual-nix-tunnel 通(TUNNEL_OK 实测)。verl 结论性 BLOCKED 不再尝试。
- 本轮新增产出: R437✅(5-run eval 健康监控 wake:eval 链 PID2322797 健康+run1 ~32/158[success26/fail1/timeout5]+8 worker+0 真实 traceback/OOM+3 并发 serve 稳定+GPU5 空闲+EXPERIMENTS §R437+daily-memories 2026-11-14 wake437+MEMORY wake437 更新）；R436✅(5-run eval 健康监控 run1 ~26/158+EXPERIMENTS §R436+MEMORY wake436 更新+体积滚动压缩[wake398-432 指针块合并]）；R435✅(5-run eval 健康监控 run1 ~28/158+EXPERIMENTS §R435+MEMORY wake435 更新+体积自检)；R434✅(5-run eval 健康监控 run1 ~23/158+EXPERIMENTS §R434+MEMORY wake434 更新+体积压缩归档)；R433✅(R2 200步主训 COMPLETED+OOM mitigation+R2 serve GPU7:8095 READY+5-run eval 起跑[全量详见 daily-memories 2026-11-14 §wake433])；R432✅(R2 监控 step151+奖励平台期修正+cheat=0/1200)；R431✅(R2 监控 step100+cheat=0/400+step50 ckpt)
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ R0 200步主训 COMPLETED+诚实负结果+✅ R2+sandbox-exec 200步主训 COMPLETED(cheat=0/1600,奖励平台后回落 0.1195→0.0798)+✅ 5-run eval RUNNING(01:08:13 自动链 PID2322797,serve R2 global_step_200 GPU7:8095→158题5-run→5run_rl_analysis_R2.json,~12h ETA~13:00)；下一动作=5-run eval 完→R2 真实数字(vs step105 0.0304±0.0083,McNemar+bootstrap)→显著则里程碑报告 report_posttrain_rl_surrogate_zh.html(标替身预演)/负则诚实负结果+换奖励(§用户令#4,平台化使负分支概率上升)；L4 2026-11-12(zhulong step105 ✅5/5 0.0304±0.0083;designflow base 5/5=0%)
- git: super_intelligence_2035(main=origin,同步,designflow/vision 在途文件不碰)；本轮交付(wake436: EXPERIMENTS §R436+MEMORY wake436 更新+体积滚动压缩+daily-memories 2026-11-14 wake435 归档)
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
| 5 | — | — | **空闲**(step60 serve 已 teardown,wake433 OOM mitigation 手动 kill) | 3 MiB | ⬜ wake433 freed |
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
- 🔴 **L4 领域评测命令链（wake339 建立，wake381 更新）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配），5-run eval IN PROGRESS on .17 GPU6(:8096 step105-final)；run 1:Pass@1=6/158=3.8%(code_gen_success=62/fail=92/timeout=4)，run 2 in progress(51/158)；② **designflow**=EDA-Flow-Bench（36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，1173 tasks 4 shards A253/B277/C310/D353，`scripts/run_design_flow_batch.py --session-backend http://127.0.0.1:8666/v1/run_code`，cline at `/nasdata/app.e0031982/.local/bin/cline`，PreToolUse hook anti-cheat）；③ **反向隧道**：.17 PID1008898 `ssh -p3333 -fN -R 18096:localhost:8096 app.e0031982@localhost` → 36.15 `curl localhost:18096/v1/models` returns minicpm5-2b-sft-v39-final ✅；④ **cline providers.json on 36.15**：已配置 `baseUrl http://127.0.0.1:18096/v1 model minicpm5-2b-sft-v39-final apiKey dummy-key`（updatedAt 2026-11-12T19:22）；⑤ **designflow BLOCKER**：prior evals `eval/status_minicpm5_expand30.jsonl` 16 entries ALL verdict=ERROR reason="check.py missing" → run_design_flow_batch.py 未将 task 的 `test` 字段（inline check function）写入 workdir/check.py，需 debug 该脚本或手动注入；⑥ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，BaiZe ckpts 在 .29，36.15 无 GPU → 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: **✅ 能，且 R0+R2 两路 200 步主训均已 COMPLETED，R2 5-run eval 正在跑。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令）。**wake412 起跑成功**（弃用 verl 0.4.0 结论性 BLOCKED，自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`，纯 HF+torch 单 GPU 无 Ray/verl）。**wake413-416 R0 全量 200 步 COMPLETED**（cheat=0/3200 红线绿，但 dynamics 偏负：reward 平台/mean_ratio==1.0 policy 不动/nz 0.97 塌缩 ⇒ R0=诚实负结果，proxy reward 不提升能力；R0 eval 链因 4 并发 vLLM serve OOM 断裂无数据，决策门 §R425 C 合规判分支2 missing-JSON）。**wake429-433 R2+sandbox-exec 200 步主训 COMPLETED**（@01:05:36，cheat=0/1600 红线绿，real signal+梯度流动[84/200 步 posadv>0]但 reward step100 后平台/回落 0.1195→0.0798，overall 0.0901）。**wake433 R2 global_step_200 serve GPU7:8095 READY + 5-run eval RUNNING**（autofire chain PID2322797，158题 Pass@1，~12h ETA~13:00→5run_rl_analysis_R2.json，vs step105 0.0304±0.0083 McNemar+bootstrap）。下一=5-run eval 完→R2 真实数字→显著则里程碑报告/负则诚实负结果+换奖励。GPU0-3=root；GPU4=base serve；GPU5=空闲(已 teardown)；GPU6=step105-final baseline serve；GPU7=R2 global_step_200 serve(:8095)。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。GPU0-3=root SGLang(不可动)；GPU4=base MiniCPM5-2B serve(:8098)；GPU5=空闲(step60 serve 已 teardown)；GPU6=step105-final baseline serve(:8096)；GPU7=R2 global_step_200 serve(:8095,5-run eval RUNNING)。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake1–wake186 (R1–R139) 已归档 → daily-memories-posttrain/2026-11-{06,07,08,09,10}.md（P0/P1/P2/SDPA/cu124 venv/verl/SGLang/Parquet/内存预算/500题/反作弊/替身RL预演/吞吐量等全量调研；R-content 详见 EXPERIMENTS 归档）。



> 📦 wake189-wake192 (R142-R145) 已归档 → daily-memories-posttrain/2026-11-10.md（RL Step Budget/verl Lifecycle Hooks/Production Hook Module/SFT-to-RL Transfer）。
> 📦 wake193-wake202 已归档 → daily-memories-posttrain/2026-11-10.md（Phase1基线评测/SFT crash诊断/GPU5-7 serve占位/沙盒阻塞确认/Phase1解锁路径穷尽/eval管线接口纠正/SFT失败根因分析/SFT脚本修复落地）。
> 📦 wake203-wake206 已归档 → daily-memories-posttrain/2026-11-10.md（Phase1启动脚本/eval管线接口纠正/SFT失败根因分析/SFT脚本修复落地/serve健康复检+体积归档wake193-202）。

> 📦 wake207-wake212 已归档 → daily-memories-posttrain/2026-11-11.md（serve chat completions实测/git代理发现/沙盒架构文档化/Phase1 dry-run preflight/SFT脚本语法验证/Phase2 SFT数据管线CPU全验证/Phase3 RL/GRPO全依赖图审计）。

> 📦 wake220-wake222 已归档 → daily-memories-posttrain/2026-11-11.md（R151 v7 generative final+unified v5v6v7 1725pairs/R152 verl SFT parquet/R153 退火源语料400docs+闸门PASS）。
> 📦 wake223-wake226 已归档 → daily-memories-posttrain/2026-11-11.md（R154替身SFT启动脚本verl FSDP/R155替身RL-GRPO脚本/R156三阶段编排器/R157沙盒看门狗）。
> 📦 wake227-wake230 已归档 → daily-memories-posttrain/2026-11-11.md（R158 EXPERIMENTS台账首次归档/R159 Phase2 SFT就绪审计/R160退火语料分词需求+脚本/R161 Phase3 RL就绪审计+污染闸门修复）。
> 📦 wake231-wake239 已归档 → daily-memories-posttrain/2026-11-11.md §Archived from MEMORY (wake244 roll)（R162 Phase1就绪审计/R163归档/R164沙盒诊断/R165 serve-teardown/R166数据可达/R167 serve-sentinel/R168 pipeline审计/R169 runbook/R170 SFT启动）。
> 📦 wake240-wake245 已归档 → daily-memories-posttrain/2026-11-11.md（R171 post-SFT serve桥接/R172 Phase2 SFT完成+ckpt serve/R173 Phase3 RL dry-run+排序bug修复/R174 SFT-MiniCPM5 vs Qwen3.8-27B/R175 扩展SFT定性8-prompt+loss曲线+归档wake231-239/R176 expanded qual eval）。
> 📦 wake246-wake252 已归档 → daily-memories-posttrain/2026-11-11.md（R177 schematic API修正+v8语料/R178 API盘点/R179-R183 v11-v13语料合成+污染闸门）。
> ð¦ wake253-wake255 (R184-R186) å·²å½æ¡£ â daily-memories-posttrain/2026-11-11.mdï¼R184 v14 ae* layout-editing/R185 v15 emy* geo primitives/R186 v16 db* lifecycleï¼
> 📦 wake253-wake262 (R184-R193) 已归档 → daily-memories-posttrain/2026-11-11.md（R184-R193 v14-v23 语料：ae* layout-editing/emy* geo/dbstructure/db* lifecycle+blind 全清/Mde* sweep-platform/coverage 59-67%）。

> 📦 wake263-wake316 已归档 → daily-memories-posttrain/2026-11-11.md / 2026-11-12.md（多次 roll 合并指针；要点：R291 全量113task静态分析 SFT语法95.6%vsBase62.8%/P0 D1-D6终验；R300 场景加权RL奖励；R302-316 Phase1生成失败根因+minicpm5 vLLM tool-call parser+上下文溢出修复；v11-v35 语料合并943对+双重污染闸门PASS+surrogate SFT脚本参数化+train/val 849/94 split；R-content 详见 EXPERIMENTS 归档）。

> 📦 wake320–wake336 流水已归档 → daily-memories-posttrain/2026-11-12.md（R320-R336：API Validator/R321-R323 API coverage 166→258/R324 v11-v38 corpus 1344 pairs/R325 SFT dry-run PASS/R326 SSH tunnel+run_code fix/R327 隧道验证+拆GPU5-7+SFT起跑/R328 SDPA fix+retrain/R329 gen pipeline+scoring/R330 tunnel re-verify+SFT final-epoch/R331 SFT v11v38 CONVERGED+serve GPU5/R332 post-SFT eval LAUNCHED/R334 GPU4 serve重启/R335 31/158/R336 29/158+SFT code quality）
> 📦 wake337–wake356 流水已归档 → daily-memories-posttrain/2026-11-12.md / 2026-11-13.md（R337 sandbox e2e verified+RL launch-ready / R338-351 eval monitoring+designflow baseline 0/5=0% / R352-356 designflow expand30 0/30=0%+eval path-error diagnosed）
> 📦 wake357–wake397 流水已归档 → daily-memories-posttrain/2026-11-13.md（R357 SFT配方诊断 / R358 v39 SFT训练启动 / R359 FSDP2 GPU不均衡修复 / R360-364 dual eval+designflow / R365-396 eval monitoring+stuck worker kills+pipeline autonomous / R397 run2 eval done Pass@1=1.9%+JSONL bug fixed+run3 started）

> 📦 wake398-wake432 流水已归档 → daily-memories-posttrain/2026-11-13.md / 2026-11-14.md（R398-R432：5run_analysis bugfix+eval pipeline fully autonomous[R402-R407] / step105 baseline 5/5=0.0304±0.0083 locked[R417] / verl 0.4.0 RL smoke 8 次全失败→弃 verl 自写单进程 GRPO loop smoke 3 步 PASS[R409/R412] / R0 200步主训COMPLETED+诚实负结果[proxy reward 不移动 policy,mean_ratio==1.0,nz 0.97 塌缩][R416/R420/R429] / R0 eval 链 OOM 断裂 5run_rl_analysis.json MISSING→决策门分支2[R429] / R2+sandbox-exec 200步主训起跑+cheat=0+eval autofire chain[OOM 修复版 PID2322797]落地[R428/R430] / R2 监控 step100/151+奖励平台期修正[R431/R432]。R-content 详见 EXPERIMENTS 归档）。

> 📦 [wake433 01:0x] R433 流水已归档 → daily-memories-posttrain/2026-11-14.md；**结论**：R2 200步主训 COMPLETED(cheat=0/1600,global_step_200 ckpt 5.03GB,奖励平台后回落 0.1195→0.0798 overall 0.0901)+OOM mitigation 手动 teardown GPU5(kill_gpu_serve child-PID bug)+R2 serve GPU7:8095 READY+5-run eval 起跑。详见 EXPERIMENTS §R433。

> 📦 [wake434 01:2x] R434 已归档 → daily-memories-posttrain/2026-11-14.md；**结论**：5-run eval 健康监控 run1 ~23/158,8 worker,GPU7 98%util,3 并发 serve 稳定,GPU5 空闲,0 traceback/OOM,eval 全自治无人工动作。详见 EXPERIMENTS §R434。
> 📦 [wake435 01:37] R435 已归档 → daily-memories-posttrain/2026-11-14.md；**结论**：5-run eval 健康监控 run1 ~28/158,8 worker,GPU7 89%util,3 并发 serve 稳定,GPU5 空闲,0 traceback/OOM,eval 全自治无人工动作。详见 EXPERIMENTS §R435。
> 📦 [wake436 01:55] R436 已归档 → daily-memories-posttrain/2026-11-14.md；**结论**：5-run eval 健康监控 run1 ~26/158,8 worker,GPU7 87%util,3 并发 serve 稳定,GPU5 空闲,0 traceback/OOM,eval 全自治无人工动作+MEMORY 体积滚动压缩。详见 EXPERIMENTS §R436。

[wake437 02:05] R437 **5-run eval RUNNING 健康监控（纯监控 wake，eval 全自治，无人工动作）**。实测：autofire chain PID2322797 存活(etime≈5645s)；R2 serve GPU7:8095 curl /v1/models 返回 minicpm5-2b-grpo-R2-step200,GPU7=39244MiB/97%util；3 并发 serve[GPU4 base:8098/GPU6 step105-final:8096/GPU7 R2:8095]全稳；GPU5 空闲 3MiB。run1 进度(batch_id 2026_1114_010813,eval run1 PID2354141 @01:08:13 起 ~57min)：8 cline worker active,stats counters success=26/failure=1/timeout=5=32/158 已完成,`.task_queue` 158→118 行(较 wake436 的 124 行 +6),code/ 43 文件,batch_cline.log @02:03:14 持续增长[worker-1/2 任务 037/038/039/040 成功完成],0 真实 Python traceback/CUDA OOM/Killed(worker cline.log grep=0;WARNING Exit Code:1/超时 2500s=模型能力不足 task 失败,非 infra 错误)。本轮未编辑运行中脚本/未碰 GPU0-3/GPU4/GPU6 既有 serve/eval 链；kill_gpu_serve bug 待 chain 空闲时修。详见 EXPERIMENTS §R437。 Next:5-run eval ~13:00 完(autofire 链自动)→5run_rl_analysis_R2.json→R2 真实数字(vs step105 0.0304±0.0083,McNemar+bootstrap)→显著则里程碑报告 report_posttrain_rl_surrogate_zh.html(标替身预演)/负则诚实负结果+换奖励(§用户令#4)。WAITING=0.







