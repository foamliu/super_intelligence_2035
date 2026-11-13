# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake412（2026-11-13 R412: **RL 框架切换成功——自写单进程 GRPO loop 起跑**；verl 0.4.0 GRPO 结论性 BLOCKED[wake409/410/411 list_named_actors 命名 actor 死锁]→换框架=自写 rollout-loop[纯 HF+torch 单进程单 GPU,无 Ray/verl/torchrun]；smoke 3 步 PASS[ratio=1.000 GRPO 正确,ckpt 保存,cheat=0/24]；reward check_format bug 修复；L4 eval 后台 step105 run5 在跑）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-410✅;R411✅(2-GPU 复现+torchrun 单驱动修复+NCCL 修复无效+源码审计根因+EXPERIMENTS §R411)
- 当前动作: wake412 R412:①**RL 框架切换成功**(verl 0.4.0 死锁→自写单进程 GRPO loop)：新写 `baize_posttrain_rl_grpo_loop.py`(502行,纯 HF+torch,policy+ref bf16→generate G rollouts→compute_score R0→分组优势→PPO-clipped+KL→AdamW→ckpt)+`baize_posttrain_rl_grpo_loop.sh`(GPU7+cu124 venv+NCCL加固)，取代 verl surrogate.sh ②**reward check_format bug 修复**：`baize_posttrain_reward_functions.py` 的 `check_format` def 头丢失→reward_r0_skeleton L693 raise NameError(verl 死锁在前从未暴露)→补回 ③**验证全 PASS**：--dry-run(3347 prompts+reward import OK)；--contam-check `0/3347 overlap 158 eval`(红线§5.1)；--smoke GPU7 R0 G=4 B=2 3步 ratio=1.000 gn=3-5 reward=0.32-0.46 18s/step + ckpt global_step_3 + metrics.jsonl + cheat_rate.json(0/24,红线§5.2) ④**关键 bug 修复**：首次 smoke ratio=35791→根因 attn_mask 把 prompt 置 0→修复=分离 attn_mask(真实token,传model)与 loss_mask(仅response,选loss)三处统一→ratio=1.000 ⑤未碰 GPU0-3/4/5/6；eval_chain/autocomplete/step105-run5 全程存活；smoke 完 GPU7 释放
- 下一步: ①**全量 200 步主训**(R0,G=8,B=4,ctx512/384,kl_coef=0.02,save_freq=50,~2h,GPU7 单卡)：`GPUS=7 bash baize_posttrain_rl_grpo_loop.sh --reward-arm R0 --total-steps 200 --group-size 8 --batch-prompts 4` ②**R1-R4 接沙盒**：沙盒隧道已通(wake327)，rollout 后注入 exec_success/assert_results 到 extra_info→compute_score 切到 R2-R4 ③**RL ckpt→158题 5-run mean±std**：与 SFT step105 基线配对检验(McNemar/bootstrap)；无提升/退化如实记录(vision v10 教训) ④L4 eval：step105 run5 在跑→eval_chain 自动 step60(GPU5)+base(GPU4)
- 阻塞: ✅ **RL 起跑已解除**(wake412 自写 GRPO loop 脱离 verl/Ray 死锁)。GPU7 可用(G=8 主训峰值预估 ~40GB)；GPU4/5/6=L4 eval serve(在跑)。RL 基座=MiniCPM5-2B/SFT step105(用户令解除 BaiZe 基模依赖)。verl 路径保留 BLOCKED 记录但不再尝试。
- 本轮新增产出: R412✅(RL 框架切换成功[自写单进程 GRPO loop,脱离 verl/Ray 死锁]+`baize_posttrain_rl_grpo_loop.py`502行+`baize_posttrain_rl_grpo_loop.sh`+reward check_format bug 修复+attn_mask/loss_mask bug 修复+smoke 3步 PASS[ratio=1.000,ckpt,cheat=0/24]+EXPERIMENTS §R412+MEMORY+daily)
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ smoke 起跑 PASS(wake412)，下一动作=全量 200 步主训(GPU7)+R1-R4 接沙盒+RL ckpt→158题5-run mean±std；L4 2026-11-12(zhulong step105 run5 在跑,base 待 chain;designflow base 5/5 DONE=0% delivered)；13:40 SFT v39 eval→5-run eval IN PROGRESS
- git: super_intelligence_2035(wake411 已由前轮 push);本轮将交付(wake412: grpo_loop.py+sh+reward fix+EXPERIMENTS §R412+MEMORY+daily)
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;venv 重建后需重打此patch
- 🔧 **verl 0.4.0 GRPO 结论性 BLOCKED(wake411)→ ✅ wake412 换框架解除**:verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→init 握手死锁;1-GPU/2-GPU/NCCL 修复均复现;根因=verl 0.4.0+本机 Ray 命名 actor 可见性不兼容。**wake412 解除**：弃用 verl 路径，新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch，无 Ray/verl/torchrun），smoke 3 步 PASS(ratio=1.000)。verl surrogate 脚本保留但不再尝试。详见 EXPERIMENTS §R411/§R412
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

- Q: post-train 现在能起训练吗？→ A: **✅ 能。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令解除 pretrain 依赖）。**wake412 RL 起跑成功**：弃用 verl 0.4.0（结论性 BLOCKED：`list_named_actors()` 命名 actor 死锁，1/2-GPU/NCCL 三路复现，详见 EXPERIMENTS §R410/§R411），新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch，单 GPU，无 Ray/verl/torchrun）。smoke 3 步 PASS（ratio=1.000 GRPO 正确，ckpt 保存，cheat=0/24 红线§5.2，contam gate 0/3347 红线§5.1）。**下一动作=全量 200 步主训**（`GPUS=7 bash baize_posttrain_rl_grpo_loop.sh --reward-arm R0 --total-steps 200 --group-size 8 --batch-prompts 4`，~2h）→ R1-R4 接沙盒 → RL ckpt 跑 158 题 5-run mean±std 配对检验。GPU7 可用；GPU4/5/6=L4 eval serve(在跑)。SFT（替身 v39）已完成；L4 eval 在跑（step105 run5 + step60/base 待 chain）。
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
[wake407 13:0x] R407 → 原文已归档 daily-memories-posttrain/2026-11-13.md（run3 codegen 155/158 resolved NO stuck worker 4th consecutive + pipeline fully autonomous）

[wake408 13:3x] R408 **5run_eval.sh 3-bug fix + run3 eval recovered (Pass@1=2.53%) + run4 background recover** → 原文已归档 daily-memories-posttrain/2026-11-13.md（5run_eval grep-a/$VENV_PYTHON/.env-EVAL_FW_DIR 三 bug 修复；run3 eval Pass@1=2.53%(4/158)；step105 3/5 mean±std=0.0274±0.0097）

[wake409 15:xx] R409 → 原文已归档 daily-memories-posttrain/2026-11-13.md（RL smoke 8 次全失败→根因 verl 0.4.0 1-GPU hybrid colocated-worker init 挂死，诚实负结果；详见 EXPERIMENTS §R409）

[wake412 18:1x] R412 **RL 框架切换成功——自写单进程 GRPO loop smoke 3 步 PASS（脱离 verl/Ray 死锁）+ reward check_format bug 修复**：①用户令 13:3x RL 直接 MiniCPM5-2B(+SFT step105)，wake411 verl 结论性 BLOCKED→本轮换框架 ②决策=自写 rollout-loop（非 trl）：纯 HF+torch 单进程单 GPU，无 Ray/verl/torchrun；复用 compute_score(R0)+parquet(3347)+SFT step105 ③产物 `baize_posttrain_rl_grpo_loop.py`(502行)+`.sh`(GPU7+cu124 venv)，取代 verl surrogate.sh ④reward `check_format` def 头丢失→reward_r0_skeleton raise NameError(verl 死锁在前未暴露)→补回 ⑤验证全 PASS：dry-run OK；contam-check `0/3347 overlap 158`(红线§5.1)；smoke GPU7 R0 G=4 3步 ratio=1.000 gn=3-5 18s/step+ckpt+cheat=0/24(红线§5.2) ⑥ratio=1.000 证实 GRPO 重要性采样正确 ⑦关键 bug：首次 ratio=35791→attn_mask 把 prompt 置 0→分离 attn_mask/loss_mask→ratio=1.000 ⑧GPU7 峰值 36GB 未 OOM；未碰 GPU0-3/4/5/6；eval 全程存活；smoke 完 GPU7 释放。详见 EXPERIMENTS §R412。 Next:全量 200 步主训(G=8 ~2h GPU7)+R1-R4 接沙盒+RL ckpt→158题5-run。 WAITING=0.




