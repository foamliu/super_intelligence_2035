# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake377（2026-11-13 R377: **5-run eval LAUNCHED** — dual Pass@1 results recorded in EXPERIMENTS; 5-run eval script created (baize_posttrain_5run_eval.sh); run 2 of 5 kicked off in background (PID1109190, code-gen running via vLLM :8096 step_105); run 1 results saved; PYTHON env var fix applied to script）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-376✅;R376✅;R376b✅;R376c✅(DUAL Pass@1=3.8%vs1.3%);R377✅(5run eval script+run2 launched)
- 当前动作: wake377 R377:①dual Pass@1 FINAL results recorded in EXPERIMENTS §L4-zhulong wake376c FINAL(step_105=6/158=3.8% vs step_60=2/158=1.3%,passed tasks:003,046,067,096,127,153,exec-fail breakdown,reproduce commands,5run eval plan) ②5-run eval automation script created `baize_posttrain_5run_eval.sh`(bash -n✅,dry-run✅,saves/restores providers.json,sets PYTHON env var,kicks off code-gen+eval,computes mean±std) ③run 1 results saved to /tmp/posttrain_5run_eval/step105/run1/(JSONL+summary) ④run 2 of 5 KICKED OFF in background(PID1109190,code-gen running,vLLM :8096,providers.json→local,PYTHON=venv python) ⑤first attempt failed(python not found)→fixed by adding PYTHON env var to script
- 下一步: ①wait for run 2 code-gen(~3h)+sandbox eval(~30min) to complete ②kick off runs 3-5 in subsequent wakes ③compute 5-run mean±std after all 5 complete ④McNemar/paired bootstrap vs baseline ⑤Phase3 RL launch-ready待SFT配方最终判定
- 阻塞: BaiZe ckpt inaccessible(/nas_train not mounted);P3等pretrain ckpt;5-run eval IN PROGRESS(run 2 of 5 running)
- 本轮新增产出: R377✅(5run eval script baize_posttrain_5run_eval.sh;EXPERIMENTS §L4-zhulong wake376c FINAL section with full dual Pass@1 results+reproduce commands;run 2 of 5 launched in background;run 1 results saved)
- 未完成指令: L4 2026-11-12(zhulong eval 1/5 runs done,designflow 0%);13:40 SFT v39 eval→5-run eval IN PROGRESS(run 2 of 5 running)
- git: super_intelligence_2035(commit 699cfa5a3 wake376c);本轮 commit pending(wake377)
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;root cause:flash_attn crashes on CPU meta tensor during FSDP2 init→RANK0 segfault→RANK1 NCCL deadlock;backup `.bak.flash_attn`;venv重建后需重打此patch



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4） | 39.1GB | ✅ wake334 restarted(PID553793 was dead→new PID799523,+no_proxy env) |
| 5 | 8097 | minicpm5-2b-sft-v39 | **vLLM SFT v39 ckpt serve**(wake360,global_step_60,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4) | 39.1GB | ✅ wake360 UP(v39 post-SFT eval用,format collapse FIXED) |
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
- 🔴 **L4 领域评测命令链（wake339 建立，wake349 更新）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配），已在 .17 跑 post-SFT eval（PID789217）；② **designflow**=EDA-Flow-Bench（36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，1165 tasks 4 shards，`eval/run_batch.sh --model minicpm5-2b --workers 4 --limit 5 --timeout 2400 --status eval/status_minicpm5_clean5.jsonl`，cline-based harness，PreToolUse hook anti-cheat）；③ **反向隧道**：36.15 `ssh -4 -p 2222 -L 127.0.0.1:8098:127.0.0.1:8098 app.e0031982@localhost` → 转发到 .17 GPU4 vLLM :8098（PID3716672 alive）；④ **cline auth on 36.15**：providers.json→`baseUrl http://127.0.0.1:8098/v1 model minicpm5-2b apiKey dummy-key`；⑤ **infra FIX（wake348+349）**：assets目录138个symlink + reference目录1个symlink(AutoPR-001)全部创建，remaining missing=0；⑥ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，BaiZe ckpts 在 .29 `/nas_train/.../hf_iter_*/`，36.15 无 GPU → 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: 不能。等 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。现在做 P0/P1/P2/P3预备（零 GPU）。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`。P0/P1/P2/P3预备 纯 CPU/IO 在本机 `.17` 跑；正式训练的 GPU 待 pretrain 完成或运维协调分卡。
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
[wake357 01:30] R357 SFT配方诊断完成 — 36%→0%回归三大根因确诊(格式崩溃+工具协议遗忘+长上下文退化) → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake358 01:00] R358 agentic SFT语料重构+训练启动(v39,2548条,52.7%PyAether+15.7%agentic+31.6%general) → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake359 01:29] R359 SFT FSDP2 GPU不均衡根因确诊(pretokenize修复,2GPU均衡100%,loss 2.41→2.17) → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake360 02:14] R360 v39 SFT smoke test+full eval launched — 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake361 02:41] R361 parallel step_105 eval launched — 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake362 02:53] R362 双eval监控+生成质量验证 — 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake363 03:09] R363 双eval进度+代码质量对比+designflow bench定位 → 原文已归档 daily-memories-posttrain/2026-11-13.md
[wake364 03:17] R364 L4 designflow eval launched via SSH reverse tunnel → 原文已归档 daily-memories-posttrain/2026-11-13.md
> 📦 wake365–wake368 流水已归档 → daily-memories-posttrain/2026-11-13.md（R365 designflow 0/5 FINAL / R366-367 dual eval monitoring+code quality / R368 dual eval monitoring+stats analysis）

[wake369 04:08] R369 zhulong dual eval monitoring+full syntax scan → 原文已归档 daily-memories-posttrain/2026-11-13.md

[wake370 04:14] R370 **zhulong dual eval monitoring+stuck worker diagnosis** → 原文已归档 daily-memories-posttrain/2026-11-13.md

> 📦 wake369–wake371 流水已归档 → daily-memories-posttrain/2026-11-13.md（R369 dual eval monitoring+full syntax scan / R370 stuck worker diagnosis / R371 live stats counters+syntax scan）

> 📦 wake372 流水已归档 → daily-memories-posttrain/2026-11-13.md（R372 dual eval monitoring+stuck worker kill）
> 📦 wake374 流水已归档 → daily-memories-posttrain/2026-11-13.md（R374 wake373 premature FINAL correction+step_105>step_60+"pass" root cause+SFT data 0 pass+5 stuck workers killed）

> 📦 wake375 流水已归档 → daily-memories-posttrain/2026-11-13.md（R375 dual eval code-gen 97pct+step_105>step_60 all metrics+5 stuck workers killed）

> 📦 wake376 流水已归档 → daily-memories-posttrain/2026-11-13.md（R376 dual eval code-gen 98%+syntax scan+empty-dir analysis:step_105>>step_60 all metrics）

[wake377 06:27] R377 **5-run eval LAUNCHED+EXPERIMENTS updated**:①dual Pass@1 FINAL results recorded in EXPERIMENTS §L4-zhulong wake376c FINAL(step_105=6/158=3.8% vs step_60=2/158=1.3%,passed:003,046,067,096,127,153,exec-fail:SyntaxErr17+AttrErr15+TypeErr13,reproduce commands,5run eval plan) ②5-run eval automation script `baize_posttrain_5run_eval.sh` created(bash -n✅,dry-run✅,saves/restores providers.json,PYTHON env var,code-gen+eval,mean±std computation) ③run 1 results saved to /tmp/posttrain_5run_eval/step105/run1/(JSONL+summary.json) ④run 2 of 5 KICKED OFF in background(PID1109190,code-gen running,vLLM :8096 step_105,providers.json→local,PYTHON=venv python) ⑤first attempt failed(`python` not found)→fixed by adding `PYTHON=$VENV_PYTHON`+`PATH=$HOME/.bun/bin:$PATH` to script ⑥tunnel UP(ports 8664/8665/8653/8669 listening,PID618469) ⑦3 serves UP(GPU4:8098+GPU5:8097+GPU6:8096 all healthy,curl /v1/models OK) ⑧git clean(commit 699cfa5a3 wake376c). R377✅.WAITING=0。


