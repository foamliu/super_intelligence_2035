# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake420（2026-11-13 R420: **R0 训练侧证据复核(重新计算验证 proxy-饱和) + eval serve 路径 de-risk(ckpt config valid/serve+analysis 脚本验证可跑) + 训练动力学 JSON 落盘**；R0 RL eval 仍 gated 于 step60 run2 未完，自治 eval 队列 run2→R0 5-run→residual SFT 排队运行中）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-418✅;R411✅(verl BLOCKED);R412✅(自写 GRPO loop smoke PASS);R413✅(全量主训起跑+OOM修复);R414✅(主训监控+cheat=0/800);R415✅(R1-R4 沙盒桥+主训 step165+cheat=0/2400);R416✅(R0 200步 COMPLETED+reward 动力学+eval chain 排队);R417✅(step105 5/5 0.0304±0.0083+JSONL 解析硬化);R418✅(eval 队列重排 R0 提前);R419✅(R0 proxy-饱和量化+R2 臂 venv selftest 全 PASS+py3.8 selftest 修复)
- 当前动作: wake420 R420:**零 GPU 实质产出**（R0 RL eval gated 于 step60 run2 PID1962541 19:42 起未完，GPU7 预留待 serve，本轮做"等结果前能做的实质工作"）。①**R0 训练侧证据复核**（数据源 metrics.jsonl 200 行+cheat_rate.json，重新计算验证 w419）：config=R0 arm/G8 B2/lr3e-6/kl0.02/ctx512+384/ppo1/save50，wall61.7min；reward 分段 s1-20=0.6731→s51-100=0.9201(峰)→s151-200=0.911(平台/微降)；**frac_positive_adv 0.5625→0.2637(信号衰减)**；**frac_nonzero_reward→1.0(区分度塌缩)**；**mean_ratio=1.0 恒定(policy 不动)**；KL 0.07 健康 → **reward↑=proxy 拟合/饱和非能力增长**，三条独立证据支撑，训练侧偏负（与 vision v10 同构）②**eval serve 路径 de-risk**：global_step_200/config.json valid LlamaForCausalLM(同 SFT step105 架构)→vLLM 可加载；serve 脚本接受 --ckpt/--gpu/--port/--name✅；chain 脚本逻辑(等GRPO退出→取latest ckpt→等旧chain退出→serve→5run eval→analysis)✅；5run_analysis.py 算 McNemar+paired bootstrap(满足红线§5.3)✅；chain PID2028723 ALIVE 180s 轮询，run2 ALIVE codegen 至 21:00，GPU7=3MiB → **等待数小时后 R0 eval 自动正确执行无需人工** ③**训练动力学 JSON 落盘** `rl_R0_step200_training_dynamics.json`(配置+分段+cheat+解读+eval_status=PENDING，供后续报告消费)
- 下一步: ①**等 run2(1962541)完→RL eval chain(2028723)自动 serve global_step_200 于 GPU7:8095→158题5-run**→核 /tmp/posttrain_5run_eval/5run_rl_analysis.json(grpo_R0_step200 vs step105 0.0304±0.0083) ②**R0 结论分流**：显著>0.0304→报告 `reports/report_posttrain_rl_surrogate_zh.html`(里程碑,标「替身预演」)；无提升/退化→**诚实负结果**(训练侧 A 已偏负支撑)+起 **R2+sandbox-exec**(B 已就绪,`GPUS=7 ... --reward-arm R2 --sandbox-exec`,需 GPU7 释放且沙盒不与 eval 争用) ③R0=静态字符串匹配奖励,reward 0.36→0.92 平台化=proxy 饱和,真实裁判=158题5-run
- 阻塞: ✅ **RL R0 主训 COMPLETED**(global_step_200)。RL 基座=MiniCPM5-2B/SFT step105(用户令解除 BaiZe 基模依赖)。**eval 队列**：run2(1962541,~1-1.5h 剩)→R0 RL 5-run eval(2028723,~12-20h)→residual SFT(2030315,step60-3/4/5+base-1..5)。verl 结论性 BLOCKED 不再尝试。GPU4/5/6=L4 eval serve(在跑)；GPU7=空闲(R0 eval serve 预留)。
- 本轮新增产出: R420✅(R0 训练侧证据复核重新计算验证[reward 平台+frac_positive_adv 0.56→0.26 衰减+frac_nonzero→1.0 塌缩+mean_ratio=1.0 policy 不动]+eval serve 路径 de-risk[ckpt config valid+serve/chain/analysis 脚本验证可跑+chain ALIVE]+训练动力学 JSON `rl_R0_step200_training_dynamics.json` 落盘+EXPERIMENTS §R420)
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ smoke PASS(w412)+✅ 200步主训 COMPLETED(w413-416)+✅ eval 队列重排 R0 提前(w418)+✅ R0 训练侧 proxy-饱和量化+R2 臂就绪复验(w419)+✅ R0 训练侧证据复核+eval serve 路径 de-risk+动力学 JSON 落盘(w420)；下一动作=等 run2 完→RL eval chain(2028723)自动 serve global_step_200→158题5-run mean±std 配对检验(McNemar+bootstrap)→R0 真实数字(vs step105 0.0304±0.0083)→有提升出里程碑报告/无提升诚实负结果+起 R2+sandbox-exec；L4 2026-11-12(zhulong step105 ✅5/5 0.0304±0.0083;step60 run2 中[run3-5 已 defer 到 R0 eval 后];designflow base 5/5 DONE=0%)
- git: super_intelligence_2035(behind 2,vision 在途文件不碰);本轮将交付(wake420: EXPERIMENTS §R420+MEMORY wake420+rl_R0_step200_training_dynamics.json)
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
| 7 | — | — | **空闲**(R0 RL eval serve 预留,待 run2 完后 PID2028723 serve global_step_200 于 :8095) | 3 MiB | ⬜ wake418 reserved |

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

- Q: post-train 现在能起训练吗？→ A: **✅ 能，且已跑完。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令解除 pretrain 依赖）。**wake412 RL 起跑成功**（弃用 verl 0.4.0 结论性 BLOCKED，新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`，纯 HF+torch 单 GPU 无 Ray/verl）。**wake413-416 R0 全量 200 步主训 COMPLETED**（G=8 B=2 ctx512/256 kl=0.02，wall 61.7min，global_step_200 ckpt 落盘，全程 mean_ratio=1.0 KL 0.04-0.09 健康，cheat=0/3200 红线§5.2）。reward 0.36→0.92(峰值)→0.90 平台（R0 静态字符串匹配，reward↑≠Pass@1↑）。**wake418 eval 队列重排**：原 RL eval chain(1923203)把 R0 5-run 排在 step60-run3-5+base-1-5(≈30h)之后；本轮 kill 1923203+SFT chain 父 1161064（run2 子 1962541 ppid→1 继续）→起新 RL eval chain **PID2028723** 等 run2(1962541)完→serve global_step_200 于 GPU7:8095→158题5-run mean±std 配对检验 vs step105 0.0304±0.0083→/tmp/posttrain_5run_eval/5run_rl_analysis.json→residual SFT chain **PID2030315** 跑 step60-run3-5+base-1-5。**下一动作=等 run2 完→2028723 自动出 R0 真实数字**：有提升→报告；无提升/退化→诚实负结果+起 R2+sandbox-exec（wake415 已就绪）。GPU0-3=root；GPU4/5/6=L4 eval serve；GPU7=空闲(R0 eval serve 预留)。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。GPU0-3=root SGLang(不可动)；GPU4/5/6=L4 eval serve(在跑)；GPU7=空闲(R0 eval serve 预留,待 run2 完后 2028723 serve)。
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

> 📦 wake263-wake278 已归档 → daily-memories-posttrain/2026-11-11.md / 2026-11-12.md（多次 roll 合并指针；R-content 见 EXPERIMENTS 归档：R202/R204-R210，含 v11-v35 语料合并 943 对+双重污染闸门 PASS、surrogate SFT 脚本参数化+train/val 849/94 split）。
> 📦 wake279-wake316 已归档 → daily-memories-posttrain/2026-11-12.md（R210-R316，多次 roll 合并指针；要点：R291 全量113task静态分析 SFT语法95.6%vsBase62.8%+32.7pp/截断8.6x降/P0 D1-D6终验；R294 SFT v11v36训练动力学；R297 API级Gap分析；R300 场景加权RL奖励[GRPO兼容]；R301 Phase1评测架构调查；R302-316 Phase1生成失败根因[工具名不匹配+沙盒不可达→退化循环]+自定义minicpm5 vLLM tool-call parser+上下文溢出修复[65536+enforce-eager]+R316 FULL 113/113 D1-D6 complete）。

> 📦 wake320–wake326 流水已归档 → daily-memories-posttrain/2026-11-12.md（R320 API Validator+R4 reward / R321 missing API coverage 178/166 split / R322 PoC 8→14 pairs / R323 full 166→258 pairs 100% coverage / R324 v11-v38 corpus merge 1344 pairs / R325 v38 quality+SFT dry-run PASS / R326 SSH tunnel fixed+run_code 3 root cause fix+commit fe93de4）
> 📦 wake327–wake329 流水已归档 → daily-memories-posttrain/2026-11-12.md（R327 隧道验证+拆GPU5/6/7+SFT起跑 / R328 SDPA fix+retrain / R329 gen pipeline+scoring verified）

> 📦 wake330–wake332 流水已归档 → daily-memories-posttrain/2026-11-12.md（R330 tunnel re-verify+run_code PASS+SFT final-epoch / R331 SFT v11v38 CONVERGED+serve GPU5 / R332 post-SFT eval LAUNCHED 158-task background）
> 📦 wake334–wake336 流水已归档 → daily-memories-posttrain/2026-11-12.md（R334 GPU4 serve重启+eval progress / R335 31/158+11:2x全deliverable确认 / R336 29/158+SFT code quality 5 files）
> 📦 wake337–wake356 流水已归档 → daily-memories-posttrain/2026-11-12.md / 2026-11-13.md（R337 sandbox e2e verified+RL launch-ready / R338-351 eval monitoring+designflow baseline 0/5=0% / R352-356 designflow expand30 0/30=0%+eval path-error diagnosed）
> 📦 wake357–wake397 流水已归档 → daily-memories-posttrain/2026-11-13.md（R357 SFT配方诊断 / R358 v39 SFT训练启动 / R359 FSDP2 GPU不均衡修复 / R360-364 dual eval+designflow / R365-396 eval monitoring+stuck worker kills+pipeline autonomous / R397 run2 eval done Pass@1=1.9%+JSONL bug fixed+run3 started）

> 📦 wake398 流水已归档 → daily-memories-posttrain/2026-11-13.md（R398 5run_analysis.py fixed 3 bugs+run3 codegen monitored ~37/158）

> 📦 wake399-wake401 流水已归档 → daily-memories-posttrain/2026-11-13.md（R399 codegen 53/158；R400 stuck worker kill+68/158；R401 85/158 no-stuck healthy）
> 📦 wake402-wake412 流水已归档 → daily-memories-posttrain/2026-11-13.md（R402-R407 eval pipeline fully autonomous / R408 5run_eval 3-bug fix+run3 Pass@1=2.53%+step105 3/5 mean±std=0.0274±0.0097 / R409 verl 0.4.0 RL smoke 8 次全失败诚实负结果 / R412 弃 verl→自写单进程 GRPO loop smoke 3 步 PASS[ratio 1.000,cheat=0/24]）

> 📦 wake413–414 流水已归档 → daily-memories-posttrain/2026-11-13.md（R413 全量200步主训起跑+OOM修复 / R414 step76监控+红线cheat=0/800+reward动力学+自治eval chain PID1923203落地）。
> 📦 wake415 流水已归档 → daily-memories-posttrain/2026-11-13.md（R415 R1-R4 沙盒执行客户端 `baize_posttrain_rl_sandbox_exec.py`(--selftest 真实沙盒 PASS R2部分分生效) + GRPO loop `--sandbox-exec` 集成(向后兼容) + 主训 step165/200 监控 + 红线 cheat=0/2400）。

[wake416 19:5x] R416 RL R0 主训 200 步 COMPLETED + 自治 eval chain 排队待发 → 原文已归档 daily-memories-posttrain/2026-11-13.md

[wake417 20:1x] R417 step105 基线 5-run 修复 3/5→5/5(0.0304±0.0083)+5run_eval.sh JSONL 解析硬化 → 原文已归档 daily-memories-posttrain/2026-11-13.md

[wake418 20:3x] R418 eval 队列重排——R0 RL eval 提前到 step60-run2 之后（kill 旧 chain 1923203/1161064→新 RL eval chain PID2028723 等 run2→residual SFT chain PID2030315）→ 原文已归档 daily-memories-posttrain/2026-11-13.md

[wake419 20:4x] R419 R0 训练动力学 proxy-饱和量化 + R2+sandbox-exec 臂 venv selftest 全 PASS 复验 + py3.8 selftest 健壮性修复 → 原文已归档 daily-memories-posttrain/2026-11-13.md

[wake420 21:0x] R420 **R0 训练侧证据复核 + eval serve 路径 de-risk + 训练动力学 JSON 落盘**（不空转：R0 RL eval gated 于 step60 run2 PID1962541 19:42 起未完，GPU7 预留待 serve，本轮零 GPU 实质产出）：①**R0 训练侧证据复核**（数据源 metrics.jsonl 200 行+cheat_rate.json，重新计算验证 w419）：config=R0 arm/G8 B2(3200 rollouts=200×8×2)/lr3e-6/kl0.02/clip0.2/ctx512+384/ppo1/save50，wall61.7min，grad_norm max11.31；reward 分段 s1-20=0.6731→s21-50=0.8874→s51-100=0.9201(峰)→s101-150=0.9153→s151-200=0.911(平台/微降)；**frac_positive_adv 0.5625→0.2637(信号衰减~53%)**；**frac_nonzero_reward→1.0(区分度塌缩)**；**mean_ratio=1.0 恒定(policy 对 ref 不动)**；KL 0.0149→0.0717 健康 → **reward↑=proxy 拟合/饱和非能力增长**，三条独立证据(reward 平台+信号衰减+policy 不动)支撑，训练侧偏负（与 vision v10 同构）②**eval serve 路径 de-risk**：global_step_200/config.json valid LlamaForCausalLM(hidden2048/42L/16H/2KV/vocab130560/bf16,同 SFT step105 架构)→vLLM 可加载(tokenizer 齐全)；serve 脚本 baize_posttrain_sft_surrogate_serve.sh 接受 --ckpt/--gpu/--port/--name✅；chain 脚本逻辑(等GRPO退出→取latest global_step_*→等旧chain退出防 providers.json clobber→serve→60×15s健康检查→5run eval→analysis)✅；5run_analysis.py 算 mean±std+McNemar(b/c/chi2/p)+paired bootstrap(10k 95%CI)→**满足红线§5.3 配对检验**✅；实测 chain PID2028723 ALIVE(20:31 起 180s 轮询日志 eval-chain still running)，run2 PID1962541 ALIVE(codegen.log 写至 21:00)，GPU7=3MiB 空闲 → **等待数小时后 R0 eval 自动正确执行无需人工干预** ③**训练动力学 JSON 落盘** `rl_surrogate_runs/minicpm5_grpo_loop_R0_200step/rl_R0_step200_training_dynamics.json`(完整配置+分段统计+cheat+解读+eval_status=PENDING，供后续里程碑报告 report_posttrain_rl_surrogate_zh.html 直接消费，报告待 5-run eval 出数后再建不预填假数) ④红线复核：§5.1 contam 0/3347；§5.2 cheat=0/3200；§2/§5.3 协议冻结未改 ⑤MEMORY 体积 roll wake419→daily-memories。详见 EXPERIMENTS §R420。 Next:等 chain 2028723 出 /tmp/posttrain_5run_eval/5run_rl_analysis.json(grpo_R0_step200 vs step105 0.0304±0.0083,McNemar+bootstrap)→R0 结论分流(显著提升出里程碑报告/无提升诚实负结果+起 R2+sandbox-exec)。 WAITING=0.





