# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake411（2026-11-13 R411: **RL 基座=MiniCPM5-2B/SFT step105(用户令解除 BaiZe 基模依赖);verl 0.4.0 GRPO 结论性 BLOCKED——2-GPU 复现同一 init 握手死锁(≥2GPU 假设证伪)+torchrun 多驱动 bug 修复(R-launch-fix3)+NCCL 接口修复(R-launch-fix4)无效;RL 路径需换框架(trl/自写 loop)**;L4 eval 后台 step105 run5 在跑）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-410✅;R411✅(2-GPU 复现+torchrun 单驱动修复+NCCL 修复无效+源码审计根因+EXPERIMENTS §R411)
- 当前动作: wake411 R411:①**RL 基座依赖解除**(用户令 13:3x):RL 起点=MiniCPM5-2B→SFT step105(global_step_105=minicpm5-2b-sft-v39-final),不再等 BaiZe 基模 ②**2-GPU 起跑实测**:kill GPU5 step60 serve 腾卡→GPU5+GPU7;新写 `baize_posttrain_rl_smoke_sglang_2gpu.yaml`(SGLang rollout,hybrid,n_gpus=2,ctx1024,G=4,5步,no-KL,R0) ③**torchrun 多驱动 bug 修复(R-launch-fix3)**:verl main_ppo 是单驱动(自调 ray.init,n_gpus 来自配置),`--nproc_per_node` 必须=1;原 $NGPU 派生多 Ray 集群争抢 GPU→改 1 ④**2-GPU 复现同一死锁**:进展比 1-GPU 更远(Ray→TaskRunner→validate_config PASS→2 WorkerDict _0:0/_0:1+RegisterCenter),但卡 `Waiting for register center`(base.py:371 `list_named_actors()` 找不到命名 actor),2 WorkerDict RSS 恒 682MB/wchan=hrtimer_nanosleep/GPU 恒 3MiB 4.5-6.7min——与 wake410 1-GPU 签名一致→≥2GPU 不能解除 ⑤**NCCL 接口修复(R-launch-fix4)无效**:NCCL/gloo pin bond0+IB disable,重跑签名不变 ⑥**源码审计根因**:WorkerDict.__init__/_configure_with_store 均无 sleep/无 init_process_group;register_center 进程存在但 TaskRunner list_named_actors() 看不到→verl 0.4.0+本机 Ray 命名 actor 可见性不兼容;py-spy 因 ptrace_scope=1 被拒 ⑦cleanup+GPU5 重 serve step60(PID1802143,:8097 OK)恢复 eval chain
- 下一步: ①**换 RL 框架起跑**(trl GRPO 单进程/自写 rollout-loop,脱离 verl Ray colocated);trl 未装于两 venv,需安装+奖励函数适配+rollout 配置(脚手架,下一 wake 起) ②或 patch verl base.py:371 用 ray.get_actor 直取代替 list_named_actors(需确认 namespace,有风险) ③zhulong 5-run eval:等 step105 run5 跑完→eval_chain 自动 step60(GPU5 已恢复)+base(GPU4)
- 阻塞: 🔴 **RL 起跑 BLOCKED on verl 0.4.0 框架**(非基座、非 GPU 数):1-GPU(2x)+2-GPU+NCCL 修复三路均复现 WorkerDict init/register-center 握手死锁;根因=verl list_named_actors 与本机 Ray 命名 actor 可见性不兼容,需 root 才能精确定位;解法=换 trl/自写 loop。GPU 现充足(GPU5/7 可用);BaiZe 基模依赖已解除
- 本轮新增产出: R411✅(RL 基座依赖解除[用户令]+2-GPU SGLang smoke 配置+torchrun 单驱动修复 R-launch-fix3[多 GPU 起跑前提]+NCCL 接口修复 R-launch-fix4[标准加固,实测无效]+2-GPU 复现死锁[≥2GPU 假设证伪]+源码审计根因[list_named_actors 不可见]+EXPERIMENTS §R411+MEMORY+daily+GPU5 step60 重 serve 恢复 eval)
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑(BLOCKED on verl 框架死锁,下一动作=换 trl/自写 loop,见 §R411);L4 2026-11-12(zhulong 5-run eval:step105 run5 在跑,GPU5 step60 serve 已恢复,base 待 chain;designflow base 5/5 DONE=0% delivered);13:40 SFT v39 eval→5-run eval IN PROGRESS
- git: super_intelligence_2035(wake410 未提交);本轮将交付(wake411: surrogate 脚本 R-launch-fix3/fix4+smoke_sglang_2gpu.yaml+EXPERIMENTS §R411+MEMORY+daily)
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;venv 重建后需重打此patch
- 🔧 **verl 0.4.0 GRPO 结论性 BLOCKED(wake411)**:verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→TaskRunner 与 2 WorkerDict 互等→init 握手死锁;1-GPU/2-GPU/NCCL 修复均复现(RSS 恒 682MB,GPU 恒 0,wchan hrtimer_nanosleep);非 GPU 数/非 KL/非 NCCL/非调度;根因=verl 0.4.0+本机 Ray 命名 actor 可见性不兼容;解法=换 trl GRPO/自写 rollout-loop(脱离 verl Ray colocated);详见 EXPERIMENTS §R411
- 🔧 **torchrun 单驱动修复 R-launch-fix3(wake411)**:`baize_posttrain_rl_grpo_surrogate.sh` L320 `--nproc_per_node=1`(verl main_ppo 单驱动,n_gpus 来自配置);原 $NGPU 派生多 Ray 集群→多 GPU 起跑前提修复
- 🔧 **NCCL 接口修复 R-launch-fix4(wake411)**:脚本 export NCCL/gloo `SOCKET_IFNAME=bond0`+`NCCL_IB_DISABLE=1`+`NCCL_NET=Socket`(本机多网卡含 docker bridge);标准 torch.distributed-in-container 加固,实测对 verl 死锁无效(非根因)但保留
- 🔧 **config-path 修复 R-launch-fix2(wake410)**:`baize_posttrain_rl_grpo_surrogate.sh` L303 `CFG_DIR` 强制绝对路径;项目配置(sdpa/hybrid/timeout)现真正加载;RL 起跑前提(已验证有效)



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4） | 39.1GB | ✅ wake334 restarted(PID553793 was dead→new PID799523,+no_proxy env) |
| 5 | 8097 | minicpm5-2b-sft-v39 | vLLM SFT v39 step60 ckpt serve(--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 --enable-auto-tool-choice --max-num-seqs 4) | 39.1GB | ✅ wake411 re-serve(PID1802143,曾为 2-GPU RL smoke 腾卡而 kill,verl BLOCKED 后恢复 eval chain) |
| 6 | 8096 | minicpm5-2b-sft-v39-final | **vLLM SFT v39 final ckpt serve**(wake360,global_step_105,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4,PID962854) | 39.2GB | ✅ wake361 parallel eval RUNNING(GPU6=81%util,step_105 eval PID972225) |
| 7 | — | — | **空闲**(同GPU6,SFT converged) | 3 MiB | ⬜ freed(wake331) |

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

- Q: post-train 现在能起训练吗？→ A: **RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令解除 pretrain 依赖）。但 🔴 **RL 起跑 BLOCKED on verl 0.4.0 框架**（非基座、非 GPU 数）：verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→TaskRunner 与 WorkerDict 互等→init 握手死锁；**1-GPU(2x)+2-GPU+NCCL 接口修复三路均复现同一签名**（RSS 恒~682MB，GPU 显存恒 0，wchan=hrtimer_nanosleep，资源已分配→非调度死锁；详见 EXPERIMENTS §R410/§R411）。✅ 已修：config-path(R-launch-fix2)、torchrun 单驱动(R-launch-fix3)、NCCL 接口(R-launch-fix4，无效但保留)。❌ wake410「≥2 GPU 解法」已证伪（wake411 2-GPU 复现同一死锁）。**解法=换 RL 框架**（trl GRPO 单进程 / 自写 rollout-loop，脱离 verl Ray colocated；trl 未装需安装）——下一 wake 起做。GPU 现充足（GPU5/7 可用）。SFT（替身 v39）已完成；L4 eval 在跑（step105 run5 + step60/base 待 chain）。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。GPU0-3=root SGLang(不可动)；GPU4/5/6=L4 eval serve(在跑)；GPU7=空闲(本轮 RL smoke 用后已清理)。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake1–wake4 流水已归档 → daily-memories-posttrain/2026-11-06.md（P0数据源诊断/P1-e污染隔离/P2方案书/P0实测D1–D6+PyAether语料调研）。
> 📦 wake9–wake16 流水已归档 → daily-memories-posttrain/2026-11-06.md（vLLM 安装/MiniCPM5-2B 下载/诊断脚本增强/CPU 模型加载验证）。
> 📦 wake17–wake48 流水已归档 → daily-memories-posttrain/2026-11-07.md（survey/例行巡检/替身RL预演/R1+R3深度调研）。

> 📦 wake48-59 已归档到 daily-memories-posttrain/2026-11-07.md（R1-R11：EDA环境RL/GRPO奖励/失败模式/造题分层/合成题生成/RL框架/SFT方案/verl环境/SGLang集成/Parquet转换/内存预算）
> 📦 wake54-wake55 已归档到 daily-memories-posttrain/2026-11-08.md（例行巡检确认/启动配套脚本创建）


> 📦 wake56-wake74 已归档到 daily-memories-posttrain/2026-11-08.md（R8-R26：模型架构/SGLang集成/Parquet/内存预算/启动就绪/轨迹污染/SFT v2/cu124 venv/版本对齐）

> 📦 wake75–wake85 (R27–R37) 已归档 → daily-memories-posttrain/2026-11-08.md（cu124 venv依赖修复/全链路dry-run/SFT v2 parquet/奖励函数验证/cheat detection修复/preflight修复/GPU显存预算/排程优化/flash_attn编译/对抗鲁棒性/RL监控/沙盒连通性三层回退）。
> 📦 wake86–wake91 (R38–R43) 已归档 → daily-memories-posttrain/2026-11-08.md（Day-1执行手册/评测分析管线/数据质量审计/Day-0集成审计/发射前排演/smoke校准器）。


> 📦 wake92–wake105 (R44–R57) 已归档 → daily-memories-posttrain/2026-11-08.md（基线验收门/物理核验/GPU watcher/verl审计/奖励预注册/配置审计/SGLang兼容/风险登记册/调度优化/Ray patch/预发射验证/D1-D6分析/SFT混合管线/Vision GRPO教训）。

> 📦 wake106–wake115 (R58–R67) 已归档 → daily-memories-posttrain/2026-11-09.md（RL prompt预筛分/GRPO动力学/上下文窗口预算/Rollout吞吐量/Day-1诊断/Post-RL管线/72h守护/SFT动力学/72h替身RL投影/Day-0就绪审计+SGLang吞吐量）。

> 📦 wake116–wake128 (R68–R80) 已归档 → daily-memories-posttrain/2026-11-09.md（吞吐量统一模型/verl多轮审计/F14 parser/端到端仿真/统计功效/GRPO超参景观/RL课程/反作弊框架/反作弊监控/分词器覆盖/GPU-Day审计/SFT混合优化/GRPO崩溃检测）。

> 📦 wake129-wake142 (R81-R94) 已归档 → daily-memories-posttrain/2026-11-09.md（自适应训练控制器/崩溃恢复/难度分析/沙盒吞吐量/奖励臂动力学/E2E时间线/SFT ckpt选择/DeepSeek失败分析/DeepSeek成功模式/轨迹污染/GRPO HP校准/基线分析管线/SGLang替身基线）。
> 📦 [wake141] R93 已归档 → daily-memories-posttrain/2026-11-09.md；**结论**：D1-D6管线463行+smoke验证123条DeepSeek轨迹(D1=1.0/D2=22.88/D6=2.12)+模型对比框架。

> 📦 wake143-wake154 (R95-R107) 已归档 → daily-memories-posttrain/2026-11-09.md（GPU就绪修复/Launch验证/替身难度图谱/API覆盖差距/SFT增强生成/源码API提取/深度API搜索/就绪审计/可解性验证/全量500题+RL课程/启动日计划/E2E验证）。

> 📦 wake155-wake186 (R108-R139) 已归档 → daily-memories-posttrain/2026-11-09.md 及 2026-11-10.md（数据管线审计/可解性验证/奖励塑形R5/课程整合/统计框架/消融设计/反作弊/领域退火/SFT混合/显存预算/训练鹿性）。



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
> 📦 wake256-wake259 (R187-R190) 已归档 → daily-memories-posttrain/2026-11-11.md（R187 v17 emy* design/geo/R188 v18 dm* data-mgmt/R189 v19 emy* dbstructure/R190 v20 Mde* sweep/platform）。

> 📦 wake260 (R191) 已归档 → daily-memories-posttrain/2026-11-11.md（v21 MdePlat*平台param-sweep/job-policy/session/coverage祐5a%）。
> 📦 wake261 (R192) 已归档 → daily-memories-posttrain/2026-11-11.md（v22 emy* geometry/library/tech/coverage 59.1%）。

> 📦 wake262 (R193) 已归档 → daily-memories-posttrain/2026-11-11.md（v23 db* lifecycle/traverse/geometry/transform/symbol-pin/coverage 67.1%/db*blind全清）。

> 📦 wake263 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake265 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake266 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake267 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake268 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake271 (R202) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

> 📦 wake273 (R204) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

> 📦 wake274 (R205) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。

> 📦 wake275 (R206) 已归档 → daily-memories-posttrain/2026-11-11.md（v11-v35 25files→943对merged JSONL+parquet+双重污染闸门PASS）。

> 📦 wake276 (R207) 已归档 → daily-memories-posttrain/2026-11-11.md（surrogate SFT script parameterized+v11-v35 train/val split 849/94 ready）。
> 📦 wake277 (R208) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。
> 📦 wake278 (R209) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。
> 📦 wake279 (R210) 已归档 → daily-memories-posttrain/2026-11-12.md（wake281 roll）。
> 📦 wake280 (R280) 已归档 → daily-memories-posttrain/2026-11-12.md（wake283 roll）。
> 📦 wake281 (R281) 已归档 → daily-memories-posttrain/2026-11-12.md（wake285 roll）。
> 📦 wake282 (R282) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake283 (R283) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake284 (R284) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake285 (R285) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake296 (R296) 已归档 → daily-memories-posttrain/2026-11-12.md（wake303 roll）。
> 📦 wake297 (R297) 已归档 → daily-memories-posttrain/2026-11-12.md（wake303 roll）。
[wake287 02:00] R287 02:00 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake288 02:30] R288 02:30 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake290 02:50] R290 02:50 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake291 03:05] R291 全量113task静态分析最终结果COMPLETE+SFT语法95.6%vsBase62.8%+32.7pp/截断8.6x降低/函数100%/API+0.055→RL核心区/P0 D1-D6最终验证 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake292 03:20] R292 MEMORY归档roll(wake282-285→daily)+serve健康复检+sandbox 97st CLOSED+GPU全占位 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake293 03:20] R293 Live生成烟测BASE vs SFT → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake294 03:40] R294 SFT v11v36训练动力学分析+报告校正 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake295 03:40] R295 扩展BASE vs SFT 15task实时生成对比 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake296 04:10] R296 3-model对比 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake297 04:30] R297 API级Gap分析 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake299 05:15] R299 v11-v37统一语料合并+parquet+SFT dry-run → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake300 05:45] R300场景加权RL奖励设计[GRPO兼容/加性bonus] → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake301 05:55] R301 Phase1评测架构纵深调查+预检脚本 → 原文已归档 daily-memories-posttrain/2026-11-12.md
> 📦 wake302–303 流水已归档 → daily-memories-posttrain/2026-11-12.md（R302 GPU4 vLLM重启+Phase1生成启动 / R303 tool-calling分布+退化循环发现）
> 📦 wake304 流水已归档 → daily-memories-posttrain/2026-11-12.md（R304 Phase1生成100%失败根因[工具名不匹配+沙盒不可达→退化循环→max-output-token]+停止浪费运行）
[wake305 08:15] R305 no_sandbox模板运行失败根因 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake306 08:50] R306 自定义minicpm5 vLLM tool-call parser → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake307 09:15] R307 工具名对齐实证+context溢出发现 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake308 09:35] R308 上下文溢出修复[max-model-len 65536+--enforce-eager] → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake309 09:55] R309 极简no_sandbox模板+Phase1启动就绪清单 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake310 03:10] R310 vLLM parser streaming 5-bug fix+cline CLI E2E test PASS → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake311 11:24] R311 full static eval launched+GPU4 base serve restarted → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake313 12:05] R313 static eval 80/113 full-metric analysis → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake314 12:12] R314 static eval 90/113 extended analysis → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake315 12:25] R315 static eval 110/113 near-complete+MEMORY归档 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake316 12:35] R316 FULL 113/113 definitive final analysis[D1-D6 complete] → 原文已归档 daily-memories-posttrain/2026-11-12.md

> 📦 wake320–wake326 流水已归档 → daily-memories-posttrain/2026-11-12.md（R320 API Validator+R4 reward / R321 missing API coverage 178/166 split / R322 PoC 8→14 pairs / R323 full 166→258 pairs 100% coverage / R324 v11-v38 corpus merge 1344 pairs / R325 v38 quality+SFT dry-run PASS / R326 SSH tunnel fixed+run_code 3 root cause fix+commit fe93de4）
> 📦 wake327–wake329 流水已归档 → daily-memories-posttrain/2026-11-12.md（R327 隧道验证+拆GPU5/6/7+SFT起跑 / R328 SDPA fix+retrain / R329 gen pipeline+scoring verified）

> 📦 wake330–wake332 流水已归档 → daily-memories-posttrain/2026-11-12.md（R330 tunnel re-verify+run_code PASS+SFT final-epoch / R331 SFT v11v38 CONVERGED+serve GPU5 / R332 post-SFT eval LAUNCHED 158-task background）
> 📦 wake334–wake336 流水已归档 → daily-memories-posttrain/2026-11-12.md（R334 GPU4 serve重启+eval progress / R335 31/158+11:2x全deliverable确认 / R336 29/158+SFT code quality 5 files）
> 📦 wake337–wake356 流水已归档 → daily-memories-posttrain/2026-11-12.md / 2026-11-13.md（R337 sandbox e2e verified+RL launch-ready / R338-351 eval monitoring+designflow baseline 0/5=0% / R352-356 designflow expand30 0/30=0%+eval path-error diagnosed）
> 📦 wake357–wake397 流水已归档 → daily-memories-posttrain/2026-11-13.md（R357 SFT配方诊断 / R358 v39 SFT训练启动 / R359 FSDP2 GPU不均衡修复 / R360-364 dual eval+designflow / R365-396 eval monitoring+stuck worker kills+pipeline autonomous / R397 run2 eval done Pass@1=1.9%+JSONL bug fixed+run3 started）

> 📦 wake398 流水已归档 → daily-memories-posttrain/2026-11-13.md（R398 5run_analysis.py fixed 3 bugs+run3 codegen monitored ~37/158）

> 📦 wake399-wake401 流水已归档 → daily-memories-posttrain/2026-11-13.md（R399 codegen 53/158；R400 stuck worker kill+68/158；R401 85/158 no-stuck healthy）
[wake402 11:5x] R402 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake403 12:1x] R403 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake404 12:2x] R404 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake405 12:44] R405 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake406 12:5x] R406 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake407 13:0x] R407 **run3 codegen 155/158 resolved NO stuck worker 4th consecutive + pipeline fully autonomous**:①zhulong run3 codegen(batch 2026_1113_101852,step105 SFT v39 final,GPU6:8096)stats success=143/failure=6/timeout=6=155/158 resolved(98.1%),102 .py produced,3 left,1 cline worker active PID1331303 etime168s<<2500s→NO stuck worker 4th consecutive(wake405/406/407) ②progress since wake406:+9 success(134→143)+1 timeout(5→6)+10 resolved(145→155) ③failed6(024/010/017/055/046/091)+timeout6(062/098/118/119/121/126) ④pipeline autonomy 3 layers alive:autocomplete daemon PID1122770(~6.4h)+eval_chain PID1161064(~4.8h)+run3 5run_eval PID1217799(~2.8h)→run_cline_script PID1217807 ⑤3 serves UP:8098(base GPU4)+8097(SFT step60 GPU5)+8096(SFT step105 GPU6 100%util) ⑥tunnel UP(ssh -p3333 TUNNEL_OK hfeg0tedaap02)+reverse 18096+18098 ⑦GPU7=vision/wave_rl NOT posttrain not touched ⑧designflow base 5/5 FAIL=0% FINAL delivered(wake404) ⑨run2 eval pass_rate=0.0190(3/158) ⑩EXPERIMENTS §L4-zhulong wake407 updated+MEMORY rolled wake402/403→daily. Next:run3 codegen complete(~3 tasks<30min)→auto eval→runs4-5→step60→base→final 5run mean±std. WAITING=0.

[wake408 13:3x] R408 **5run_eval.sh 3-bug fix + run3 eval recovered (Pass@1=2.53%) + run4 background recover** → 原文已归档 daily-memories-posttrain/2026-11-13.md（5run_eval grep-a/$VENV_PYTHON/.env-EVAL_FW_DIR 三 bug 修复；run3 eval Pass@1=2.53%(4/158)；step105 3/5 mean±std=0.0274±0.0097）

[wake409 15:xx] R409 **RL smoke 起跑 8 次全失败→根因 verl 0.4.0 1-GPU hybrid colocated-worker init 挂死（诚实负结果）**:①**用户令 2026-11-13 13:3x**：RL 不再等 BaiZe 基模，直接在 MiniCPM5-2B(+SFT v39 step105)上跑 RL ②**8 次 smoke 全失败**（GPU7,R0,G=4,10步,ckpt=step105）：gpu7..gpu7d[sglang 早期 config 错]+gpu7e[sglang `loss_agg_mode` ConfigAttributeError→v2_merged 继承 ppo_trainer 默认修复]+gpu7f[sglang ActorUnavailableError actor 死]+gpu7g[sglang register-center 挂死]+gpu7h[vllm `No module 'msgspec'`+`No module 'vllm'`]+gpu7b[hf register-center 挂死] ③**根因=verl 0.4.0 1-GPU hybrid colocated-worker init 挂死**：sglang(gpu7g)与 hf(gpu7b)不同 rollout 引擎但同构挂死（verl `Waiting for register center actor`阶段，GPU 恒 3MiB 不分配、log 停长、进程存活、300s 超时不触发、colocated worker 无 .out、ray `CoreWorker Exit 2`、bundle 已 Commit 但 worker init 中退出）⇒阻塞在 colocated worker ray actor init（import torch/verl + NFS 加载 4.7GB ckpt + FSDP shard，与 128 prestart worker 争资源）非 rollout 引擎 ④**vLLM rollout 不可行**：verl_cu124_venv 无 vllm/msgspec（vllm 0.7.3 需 torch2.5.1 与 venv torch2.6.0+cu124 冲突；外部 /tmp/vllm_venv 是 torch2.5.1 独立 venv） ⑤**2-GPU 绕路**：SFT R170/R172 在 2 GPU FSDP2 成功⇒2 GPU 非 hybrid 可绕过；但 GPU4/5/6 在跑 L4 eval serve(eval_chain step105→step60→base)，拆即停 eval 违反 L4 指令「不得因此停 SFT eval」；GPU7 唯一空闲 ⑥**RL 全量 BLOCKED**至 1-GPU hybrid init 修复或 eval 完释放 GPU ⑦交付：smoke_hf.yaml(hf rollout,继承 ppo_trainer,prompt512/resp256/batch8,hydra compose 验证 PASS)+v2_merged L88 BLOCKED 注释+EXPERIMENTS §R409(8-attempt 时间线+根因+绕路不可行+下一步) ⑧cleanup：kill 全部 smoke+ray stop+清 /tmp/ray session，GPU7=3MiB 空，3 serves UP(8098/8097/8096)，eval pipeline 完整(autocomplete PID1122770+eval_chain PID1161064+recover_run4 PID1359141)，未碰 GPU0-3/vision/158 任务 ⑨符合用户令第 4 条「诚实负结果」。 Next:等 L4 eval 完释放 GPU→2 GPU 非 hybrid RL[最稳]，或深入 verl fsdp_workers 定位 colocated init 退出点。 WAITING=0.




