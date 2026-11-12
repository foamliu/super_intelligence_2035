# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake321（2026-11-12 R321 Missing API Coverage Analysis: 178 learning failure(51.7%)+166 true data gap(48.3%)+v11_v37补救覆盖0新API+MCP文档可合成训练对+GPU占位维持+sandbox 123rd FILTERED）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280归档；wake281-320✅；R321✅（Missing API Coverage: 344 missing APIs split into 178 learning failure + 166 true data gap, v11_v37 covers 0 new, MCP docs available for synthesis）
- 当前动作: wake321 R321 Missing API Coverage Analysis：①sentinel 5 serve全UP(17:10占位维持)②sandbox 123rd unreachable(poll#980,down 30+wakes)③contam gate PASS(0命中)④RL dry-run OK(SFT ckpt global_step_72,R0,3000 steps)⑤344 missing APIs cross-ref vs SFT corpus v11_v36: 178(51.7%)ARE in corpus=learning failure, 166(48.3%)NOT in corpus=true data gap⑥v11_v37补救语料覆盖0新API(补救方向错误)⑦MCP验证data gap API文档可用(emyLPPHeader.getLayerNum/GuCartPolyLine.getPointArray等有签名+示例代码)⑧SFT增强策略: data gap→MCP合成训练对, learning failure→频率/质量提升+RL强化
- 下一步: ①沙盒恢复→拆GPU5/6/7占位+切R1-R4+--smoke→正式起跑RL(R4 validator可import) ②沙盒恢复→baize_posttrain_baseline_eval.sh真实Pass@1 5-run ③用MCP批量获取166 data gap API文档→合成SFT训练对(下一轮可做,零GPU) ④P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴沙盒10.129.32.75全端口FILTERED(第123次,Pass@1+RL R1-R4需沙盒);P3等pretrain ckpt
- 本轮新增产出: R321✅(Missing API Coverage Analysis[344 APIs split 178 learning failure/166 data gap+v11_v37 covers 0 new+MCP docs available+SFT/RL strategy]+baize_posttrain_r321_missing_api_coverage.py+r321_missing_api_coverage.json+EXPERIMENTS §R321)
- 未完成指令: 🔴17:10 GPU5/6/7全✅占位中(17:10令持续);🔴13:40 Phase2 SFT COMPLETE✅+R300-R321✅/Phase1 static eval COMPLETE(3-model 113/113)/Phase3 RL就绪✅(R4 validator可import)待沙盒+GPU
- git: wake321 R321 pending commit



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,**--max-model-len 65536 --enforce-eager** --tool-call-parser minicpm5） | 37.9GB | ✅ wake311 restarted(serve was down,setsid PID 553793) |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | **vLLM SFT ckpt global_step_70**（post-SFT评测用,**--max-model-len 65536 --enforce-eager** --tool-call-parser minicpm5） | 38.0GB | ✅ wake308 ctx修复 |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中(wake284) |

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
- ✅ **沙盒架构（wake209文档化）**：eda_fastmcp `.env` → `SANDBOX_HOST=10.129.32.75`，`SANDBOX_ENDPOINTS=8664:/proj/.../t0002596_bak_1,8665:...,8653:...,8669:...`（4端口并行池）。沙盒是远程 EDA 执行环境（pyAether Python+SWIG + Virtuoso SKILL），不可在 .17 本地复制（需 EDA 工具安装）。`search_apis`/`get_api_details` 本地✅（向量DB本地），`run_code` 转发到远程沙盒（当前阻塞）。
- 🔴 **R9 verl+SGLang 集成（wake57 发现）**：verl 原生支持 SGLang（`pip install verl[sglang]`），多轮工具调用**仅 SGLang** 支持。配置已从 vLLM 切到 SGLang（`rollout.name: sglang` + `multi_turn: True` + `mode: async`）。EDA 沙盒工具骨架 `baize_posttrain_eda_tool.py` 已创建（BaseTool 子类，dry-run✅）。**R69 修正**：v1 有 3 个 CRITICAL API 不匹配（F01-F03），v2 `baize_posttrain_eda_tool_v2.py` 已修复并 dry-run✅。`baize_posttrain_tool_config.yaml` 已创建（修 F09）。**F14 BLOCKER ✅ 已解决(R70)**：MiniCPM5-2B 用 XML 格式(`<function name=...><param name=...>`), 4 个 SGLang parser 均不匹配 → 设计 MiniCPM5FunctionDetector + monkey-patch `baize_posttrain_minicpm5_parser_patch.py`。单轮 RL 不受影响。
- SFT 语料：✅ v1 `sft_pyaether_corpus.jsonl`(19610对,0污染) + ✅ v2 `sft_pyaether_corpus_v2.jsonl`(19524对,64% has-args,0污染,R24) — **v2 替代 v1 用于训练**
- 🔴 **R60 上下文窗口发现（wake108）**：DeepSeek 全 harness 轨迹平均 **28,339 tokens**（中位 23,906），是 4096 的 6.9x。4096→99%截断 / 8192→98% / 16384→82% / **32768→32%（推荐）** / 65536→3%。KV cache ctx32768 bs8 = 10.5GB/卡，A40 ✅ 可行。SFT 默认 8192 必须升级到 ≥16384；RL 脚本当前**缺失**上下文配置，需补 CONTEXT_LEN=32768。截断→假阴性奖励（8192 下约 29.4% rollout 误判）→支持从 R2 起步。
- 🔴 **R61 吞吐量约束发现（wake109）**：ctx=32768 **non-hybrid 不可行**——KV cache 10.5GB/seq，SGLang budget 18GB → 每 GPU 仅 1 序列，G=8 需 8 个。**ctx=16384 + hybrid engine** 是 72h 窗口唯一可行方案（3.45 steps/hr → ~248 步/72h）。500 步需 ~6 天。Smoke 用 ctx=32768 bs=16 G=4（37min/10步）。RL 配置已补丁至 ctx=16384，SFT 升至 16384。**主 RL 目标步数从 500 降至 200**。
- RL/SFT Parquet：✅ **已转换**（R10）`run/rl_pyaether_synth_v2.parquet`（3347 records, 931KB, verl RLHF 格式: prompt+reward_model+agent_name）+ `run/sft_pyaether_corpus.parquet`（19610 records, 2.7MB, verl SFT 格式: conversation+metadata）
- 🔴 **R11 GRPO 内存校准（wake59 发现）**：当前 `gpu_memory_utilization=0.35` 在多轮 3-turn 场景下**可能 OOM**——KV cache 需 13.8GB > 分配 11.9GB。已校准为 **0.50 + max_num_seqs=12**。训练态 ~12GB/卡，剩余 ~34GB 给 SGLang。4×A40 对 2B 全参 GRPO 是充裕配置（verl 官方 3B LoRA 需 1×H100）。添加 entropy_checkpointing + entropy_chunking 优化。5 级 OOM 降级阶梯已写入 §R11。
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）

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

[wake317 13:00] R317 Qwen3.8-27B static eval COMPLETE 113/113+3-model comparison[API knowledge universal bottleneck]+report updated+sandbox 119th FILTERED: Qwen3.8-27B static eval 113/113 COMPLETE(thinking disabled via enable_thinking:false,max_tokens=2048,~5.5min)→3-model comparison:三模型all_apis_correct完全相同=3/113=2.7%(相同3任务055/061/062,各仅1个expected API)→API知识是通用瓶颈,与模型规模无关(2B vs 27B差距13.5x无API知识提升)→Qwen: syn97.3%(110/113),trunc4.4%(5/113),cov0.145,all_correct2.7%(3/113),code1924chars,time2.9s→Qwen vs MC5-base: syn+42.4pp,trunc-42.5pp,3.5x concise; vs MC5-SFT: syn+3.5pp,trunc-1.8pp,但API correct相同2.7%→per-scenario all_correct:Schematic0%/Layout7.1%/DesignMgmt0%/Others4.3%(三模型完全一致)→58pp差距归因更新:不是规模问题(Qwen27B也2.7%)→是API知识+agent迭代闭环→report_posttrain_baseline_3model_zh.html updated(status→静态评测完成+§6.1 MC5 base vs SFT table+§7.1 Qwen table+§7.5 三模型对比+§11 gap decomposition更新+footer更新)→EXPERIMENTS §R317 appended→sandbox 119th still FILTERED。本轮新增产出：R317✅(Qwen3.8-27B 113/113 static eval[thinking disabled]+3-model comparison[API knowledge universal bottleneck:三模型all_apis_correct均2.7%]+Qwen syn97.3%≈MC5-SFT93.8%>>MC5-base54.9%+report updated[§6.1/§7.1/§7.5/§11/footer]+EXPERIMENTS §R317+baize_posttrain_static_eval_qwen.py+static_eval_qwen_results.json)。未完成指令：🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R317✅/Phase1 static eval COMPLETE(3-model 113/113 done)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake318 13:24] R318 Phase3 RL launch-readiness audit+GPU占位维持+sandbox 120th FILTERED: 体积自检(MEMORY ~30KB合规)→sentinel --check-once:全5 serve UP(GPU5:8097/GPU6:8096/GPU7:8095/GPU4:8098/GPU0:8099,17:10占位维持)→sandbox-check:10.129.32.75:8667 unreachable(exit=124,120th,down 29+wakes,22/8080/443/80全FILTERED,ping通0.188ms=主机级防火墙)→contam-check:PASS(0命中,黑名单6快照/536任务含158,13-gram≥0.8或8-gram兜底,§5.1红线满足)→Phase3产物全就位:reward_functions.py 42KB(11-12 05:37)/hooks.py 42KB/verl_config_v2.yaml 5.7KB(11-12)/hooks_config.yaml/rl_pyaether_synth_v2.parquet 953KB(3347 synthetic)/SFT ckpt global_step_70→默认REWARD_ARM=R0(skeleton无沙盒),G=8,3000steps,KL0.02,clip0.2,GPU-busy guard不kill serve→结论:Phase3 RL秒级启动就绪,唯一阻塞=沙盒防火墙(infra,非agent可修);沙盒一通→拆GPU5/6/7占位+切R1-R4+--smoke→正式起跑→静态评测战略结论已锁定(58pp归因=API知识+迭代闭环非规模,RL R4臂正中靶心)→EXPERIMENTS §R318 appended。本轮新增产出：R318✅(Phase3 RL launch-readiness audit[sentinel 5 serve全UP+contam gate PASS 0命中+产物清单齐+sandbox 8667 unreachable 29+wakes]+GPU占位维持+EXPERIMENTS §R318)。未完成指令：🔴17:10 GPU5/6/7全✅占位中;🔴13:40 Phase2 SFT COMPLETE✅+R300-R318✅/Phase1 static eval COMPLETE(3-model 113/113)/Phase3 RL就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake319 13:45] R319 API Misuse Taxonomy 3-model deep analysis+SFT hallucination pattern+RL R4 refinement+GPU占位维持+sandbox 121st FILTERED: 体积自检(MEMORY 31KB→归档wake313-316→daily-memories→~26KB合规)→sentinel --check-once:全5 serve UP(GPU5:8097/GPU6:8096/GPU7:8095/GPU4:8098/GPU0:8099,17:10占位维持)→sandbox-check:10.129.32.75:8667 unreachable(exit=124,121st,down 30+wakes)→R319 API Misuse Taxonomy(3-model 113/task deep analysis from static_eval_r311+qwen_results):①MC5-base wrong 51/113(45.1%),missing 110/113(97.3%),all_correct 3/113(2.7%)②MC5-SFT wrong 60/113(53.1%↑vs base 45.1%!),missing 110/113(97.3%),all_correct 3/113(2.7%)③Qwen3.8-27B wrong 42/113(37.2%),missing 110/113(97.3%),all_correct 3/113(2.7%)④SFT paradox:SFT INCREASES wrong APIs(45.1%→53.1%)—learned emy* naming convention but hallucinates specific API names(emyPoint 7x/emyPointF 4x/emyRectF 4x/emyInitAether 3x等177 distinct wrong APIs)⑤344 MISSING APIs common to ALL 3 models(dbCreateLib 20x/dbGetAllLibs 19x/dbDelLib 18x/emyString 16x/dbNewCV 16x/dbCloseCV 15x等核心API)⑥3 WRONG APIs common to all(Point/PointArray/emyDesign=generic OOP not pyAether)⑦all_correct intersection=3 tasks(055/061/062,各仅1 expected API)⑧MC5-SFT per-scenario:Schematic 0/41 all_correct+24/41 wrong(worst),DesignMgmt 0/21+16/21,Layout 2/28+12/28,Others 1/23+8/23⑨RL R4 implication:check API existence vs pyAether DB(not naming convention),penalize 177 hallucinated APIs,encourage 344 missing APIs,give partial credit for correct module prefix but verify against API DB not prefix-only⑩产物:baize_posttrain_r319_api_misuse_analysis.py+r319_api_misuse_analysis.json(367KB)。本轮新增产出：R319✅(API Misuse Taxonomy 3-model 113/task[SFT hallucinate emy* 177 wrong APIs+344 common missing APIs+RL R4 refinement]+baize_posttrain_r319_api_misuse_analysis.py+r319_api_misuse_analysis.json+EXPERIMENTS §R319)。未完成指令：🔴17:10 GPU5/6/7全✅占位中;🔴13:40 Phase2 SFT COMPLETE✅+R300-R319✅/Phase1 static eval COMPLETE(3-model 113/113)/Phase3 RL就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake320 14:30] R320 Offline PyAether API Existence Validator+R4 Reward Module+R319 Correction+GPU占位维持+sandbox 122nd FILTERED: 体积自检(MEMORY ~28KB合规)→git pull --rebase(up to date)→sentinel:全5 serve UP(GPU5:8097/GPU6:8096/GPU7:8095/GPU4:8098/GPU0:8099,17:10占位维持)→sandbox:10.129.32.75:8667+22 unreachable(exit=124,122nd,down 30+wakes)→R320 Offline API Validator(pyAether MCP search验证21 APIs):①R319 "wrong" APIs中6/9(67%)实为有效pyAether API(emyPoint/emyPointF/emyPointArrayF/emyInitAether/emyDesign/emyTermType exact match),真幻觉仅3(emyRectF/emyCreateLibrary/CellView)②R319 "missing" APIs中7/8确认为有效API(dbCreateLib/dbGetAllLibs/dbDelLib/dbCloseCV/dbNewCV/emyString/EmyLPPHeader exact match),CString unclear③R319 "SFT paradox"被推翻:SFT增加的是valid-wrong-context不是幻觉④R4 validator 3-tier分类(CORRECT/VALID_WRONG_CONTEXT/HALLUCINATION/MISSING)全量评测113tasks×3models:MC5-base mean_r4=0.093(CORRECT93/HALLUC17/HALLUC_LIKELY112),MC5-SFT mean_r4=0.109(CORRECT102↑/HALLUC10↓/HALLUC_LIKELY30↓73%),Qwen mean_r4=0.108(CORRECT102/HALLUC9)⑤SFT CORRECT 93→102(+9.7%),HALLUC 17→10(-41%),HALLUC_LIKELY 112→30(-73%),VALID_WRONG_CTX 6→29(SFT学会API词汇表)⑥missing_rate~89%三模型一致=344 common missing APIs是通用知识缺口⑦产物:baize_posttrain_r320_api_validator.py+baize_posttrain_r320_r4_validator.py(R4 reward模块可import)+r320_api_db_snapshot.json(50KB)+r320_mcp_validation.json+r320_r4_aggregate_stats.json+EXPERIMENTS §R320。本轮新增产出：R320✅(Offline API Validator 3-tier[MCP验证21 APIs+R319纠错67% wrong=valid+R4 validator模块可import+113tasks×3models全量R4评测]+5产物+EXPERIMENTS §R320)。未完成指令：🔴17:10 GPU5/6/7全✅占位中;🔴13:40 Phase2 SFT COMPLETE✅+R300-R320✅/Phase1 static eval COMPLETE(3-model 113/113)/Phase3 RL就绪✅(R4 validator可import)待沙盒+GPU ⇒ WAITING=0。
[wake321 14:35] R321 Missing API Coverage Analysis: Data Gap vs Learning Failure+MCP docs available+GPU占位维持+sandbox 123rd FILTERED: 体积自检(MEMORY ~30KB合规)→git pull --rebase(up to date)→sentinel --check-once:全5 serve UP(GPU5:8097/GPU6:8096/GPU7:8095/GPU4:8098/GPU0:8099,17:10占位维持)→sandbox:10.129.32.75:8667+22 nc timeout(poll#980,123rd,down 30+wakes)→contam gate PASS(0命中)→RL dry-run OK(SFT ckpt global_step_72,R0 arm,3000 steps,deps OK)→R321 Missing API Coverage Analysis(cross-ref 344 missing APIs vs SFT corpus v11_v36):①344 missing APIs: 178(51.7%)ARE in corpus=LEARNING FAILURE, 166(48.3%)NOT in corpus=TRUE DATA GAP②v11_v37补救语料(1086行,+57行,+317K chars)覆盖0新API→补救方向错误(增加同类示例而非覆盖缺失API)③missing API模块分布: unknown 177/EmyLPPHeader 12/emyBitArray 9/emyBoxF 9/MdePlatSession 8/GuCartPolyLine 6④MCP验证data gap API文档可用: emyLPPHeader.getLayerNum(签名+描述), GuCartPolyLine.getPointArray(签名+完整代码示例), emyLPPHeader class(8方法+13属性)⑤SFT增强策略: data gap(166)→MCP批量获取文档→合成训练对(预估500-830条,污染隔离); learning failure(178)→频率/质量提升+RL R4强化⑥RL策略: learning failure APIs是RL理想目标(模型见过但不调用→reward强化使用)⑦产物: baize_posttrain_r321_missing_api_coverage.py+r321_missing_api_coverage.json+EXPERIMENTS §R321。本轮新增产出：R321✅(Missing API Coverage Analysis[344 APIs split 178 learning failure/166 data gap+v11_v37 covers 0 new+MCP docs available+SFT/RL strategy]+3产物+EXPERIMENTS §R321)。未完成指令：🔴17:10 GPU5/6/7全✅占位中;🔴13:40 Phase2 SFT COMPLETE✅+R300-R321✅/Phase1 static eval COMPLETE(3-model 113/113)/Phase3 RL就绪✅(R4 validator可import)待沙盒+GPU ⇒ WAITING=0。
