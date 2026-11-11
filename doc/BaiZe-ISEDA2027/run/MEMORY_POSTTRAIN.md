# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake303（2026-11-12 R303 Phase1生成tool-calling实时分析+退化循环发现[514 req/9704 run_commands/退化循环40次]+生成在跑[8 workers/150 in queue/0 .py yet]）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280(EXPERIMENTS归档)；wake281-302✅；wake303 Phase1生成tool-calling实时分析✅
- 当前动作: wake303 ①Phase1生成健康验证:8 workers处理task 001-008,150/158 in queue,0 completed .py,514 HTTP 200 req,0 fail/0 timeout→生成健康 ②tool-calling分布分析(vLLM 30MB日志):run_commands 9704/search_apis 5813/run_pyAether_code_tool 2592/submit_and_exit 2343/get_api_details 908→模型确实用工具,content XML解析正常工作 ③退化循环发现:worker_1 task_002陷入pyAeur_code拼写错误循环,40次重复,系统反复提醒submit_and_exit,模型无法跳出→D1/D2协议差距直接证据 ④hermes parser复现确认:tool_calls=[]但content有<function>XML→cline从content解析 ⑤MEMORY归档wake296/297→daily腾位
- 下一步: ①等待Phase1生成完成(158 tasks×5 runs,2500s/task timeout,后台setsid,预计数小时) ②生成完成后需沙盒侧机器评分(.17缺framework+pyAether) ③沙盒恢复后--score-existing快速验证 ④Phase3 RL待沙盒+GPU ⑤P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP全端口过滤(8664/22 FILTERED)+.17缺EDA-Eval-Framework+pyAether→Phase1评分需沙盒侧机器;MCP run_code同样-32001超时;hermes parser不匹配MiniCPM5 XML(但cline从content解析已绕过);P3等pretrain ckpt
- 本轮新增产出: R303✅(Phase1生成tool-calling实时分析[514 req/9704 run_commands/search_apis 5813/退化循环pyAeur_code 40次/hermes parser复确认]+EXPERIMENTS §R303+wake296/297归档)
- 未完成指令: 🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅+v11-v37合并+parquet+SFT dry-run✅+R300场景加权RL奖励设计✅+R301 Phase1预检+架构调查✅+R302 GPU4重启+Phase1生成启动✅+R303 tool-calling实时分析✅(生成在跑)/Phase1评分需沙盒侧机器/Phase3 RL脚本+奖励就绪✅待沙盒+GPU
- git: wake303 R303待提交



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,--enable-auto-tool-choice --tool-call-parser hermes） | 39.6GB | ✅ 常驻+tool-calling |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | **vLLM SFT ckpt global_step_70**（post-SFT评测用） | 37.8GB | ✅ SFT served(wake284) |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中(wake284) |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建
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
[wake299 05:15] R299 v11-v37统一训练语料合并+parquet转换+SFT dry-run全OK+serve 5端点UP+sandbox 104th CLOSED+GPU全占位+git synced: 体积自检(MEMORY 27.3KB合规)→git synced(main=origin)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(8095-8099全UP)→sandbox 104th wake ICMP 0.6ms OK但TCP 8664 timeout(仍阻塞)→①v11-v37合并:v11-v36(1029pairs)+v37(57pairs)→1086pairs(0 dup)→sft_pyaether_corpus_v11_v37_merged.jsonl(1528KB) ②parquet转换:1086rows/0.34MB/schema[conversation,pair_id,type,api_used,contamination_check]/schema match v5✅/0 errors ③污染隔离PASS(488 eval entry_points指纹扫描) ④API家族重平衡:db*243→335(+92,+37.9%)/emy*:db*1.62→1.18/dbCloseLib 0→10/dbCloseCV 8→21/dbGetAllLibs 6→16/dbSaveCV 5→16/dbCrtInst 13→23 ⑤SFT dry-run全前置OK(torchrun✅/model✅/verl+flash_attn+peft✅/src parquet 351999bytes✅)/recipe:GPU6,7/2×A40/3epochs/lr1e-5/full FT/max_len2048/save20 ⑥EXPERIMENTS §R299新增(6节:合并/重平衡/污染/parquet/dry-run/BaiZe启示)。本轮新增产出：R299✅(v11-v37统一语料[1086pairs/parquet 0.34MB/污染PASS/db*+37.9%/emy*:db*1.18]+SFT dry-run全OK+EXPERIMENTS §R299+sft_pyaether_corpus_v11_v37_merged.jsonl+parquet+r299_v11v37_merge_summary.json+baize_posttrain_r299_v11v37_merge.py)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅+v11-v37合并+parquet+SFT dry-run✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake300 05:45] R300场景加权RL奖励设计[GRPO兼容/加性bonus方案]+serve 5端点UP+sandbox 105th CLOSED+GPU全占位+git synced: 体积自检(MEMORY 28.1KB合规)→git synced(rebase onto 3dc670125✅)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(sentinel --check-once全UP)→sandbox 105th wake ICMP 0.5ms OK但TCP 8664 FILTERED(仍阻塞)→①R300场景加权RL奖励设计:核心发现GRPO组内归一化使简单乘子失效(A=(wr-wr_bar)/(wsigma)=A)→改为加性bonus/penalty方案(保持R1-R4论文定义不变)→scene_weights数据驱动(layout 1.0/design_mgmt 0.94/others 0.856/schematic 0.786,公式1.0+max(0,-delta)*2+(1-recall)*0.5归一化)→30 both_missed API bonus(dbCreateLib等+0.03*sw/个)→50 anti-forget API penalty(base_only API丢弃-0.02*sw/个) ②reward_functions.py+3函数(_load_scene_weight_config/_infer_scenario[metadata优先db*→layout emy*→schematic]/reward_r300_scene_weighted)→py_compile✅ ③自测PASS:Layout dbCreateLib+dbNewCV bonus 0.060>Schematic emyScalarName+emyBlock.create bonus 0.047(因layout weight 1.0>schematic 0.786)→无both_missed API bonus=0 ④YAML接入(enable_scene_weighting:false+scene_weight_config:rl_scene_weight_config_r300.json,待沙盒恢复后arm=R4+enable true) ⑤EXPERIMENTS §R300新增(10节:GRPO兼容性/加性方案/权重计算/bonus set/anti-forget/场景推断/自测/配置接入/BaiZe启示/局限)。本轮新增产出：R300✅(场景加权RL奖励设计[GRPO兼容/加性bonus/layout1.0>schematic0.786/30 both_missed bonus/50 anti-forget penalty/自测PASS/YAML接入]+EXPERIMENTS §R300+rl_scene_weight_config_r300.json+r300_scene_weight_summary.json+baize_posttrain_r300_scene_weight_design.py+reward_functions.py+3函数+YAML+2kwargs)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅+v11-v37合并+parquet+SFT dry-run✅+R300场景加权RL奖励设计✅/Phase1待沙盒ACL/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake301 05:55] R301 Phase1评测架构纵深调查+预检脚本[3阻塞项发现]+serve 5端点UP+sandbox 106th CLOSED+GPU全占位+git synced: 体积自检(MEMORY 30.5KB合规,归档wake298→daily)→git synced(fast-forward to ee2f3f2b7✅)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(8095-8099全UP)→sandbox 106th wake ICMP 0.28ms OK但TCP 8664/22全FILTERED(仍阻塞)+MCP run_code同样-32001超时→①R301 Phase1评测架构纵深调查:拆解生成vs评分依赖链(run_cline_script.sh生成[.17可跑] vs run_eval.py→run_on_sandbox.py评分[需沙盒+framework])→发现评分需3件.17没有的:(a)沙盒网络可达[10.129.32.75 4端口8664/8665/8653/8669全ACL FILTERED](b)EDA-Eval-Framework absent[~/20260806/缺失,NFS无,env空,含run_on_sandbox.py/assemble/calculate](c)pyAether NOT_INSTALLED[system py3.8.10 ModuleNotFoundError]→.17只能跑生成不能跑评分→此前MEMORY"Phase1待沙盒ACL"低估阻塞 ②建baize_posttrain_phase1_launch.sh(--preflight/--generate/--score/--full/--score-existing,bash -n✅)→3模型端点注册表[minicpm5-2b:8098/qwen3.8-27b:8099/glm-5.2:cloud]→preflight实测PASS=9 FAIL=6[dataset158✅/driver✅/scorer✅/cline3.0.53✅/3端点全UP✅/sandbox4端口全FILTERED❌/framework ABSENT❌/pyAether NOT_INSTALLED❌]→JSON报告落nemo_experiments ③发现11-10有3个158-task未评分生成集(094456/094902/095714,158 completion=pass,0 status=pass,沙盒断裂前生成)→沙盒恢复后--score-existing可立即评分省重新生成 ④EXPERIMENTS §R301新增(6节:依赖链拆解/预检脚本/未评分生成集/预检实测/运维建议/局限)。本轮新增产出：R301✅(Phase1评测架构纵深调查[生成vs评分依赖链/3阻塞项:沙盒ACL+framework absent+pyAether absent/.17只能生成]+baize_posttrain_phase1_launch.sh[--preflight PASS=9 FAIL=6/--generate/--score/--full/--score-existing]+3模型端点注册表+11-10未评分生成集发现[3×158tasks]+EXPERIMENTS §R301+preflight JSON)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅+v11-v37合并+parquet+SFT dry-run✅+R300场景加权RL奖励设计✅+R301 Phase1预检+架构调查✅/Phase1评分需沙盒侧机器(非仅ACL,缺framework+pyAether)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake302 06:30] R302 GPU4 vLLM重启加tool-calling+Phase1生成已启动[150/158在队,193+req已处理]+GPU全占位+serve 5端点UP: 体积自检(MEMORY 31.7KB合规,归档wake295→daily)→①旧vLLM进程3408952/3408953/3409056顽固:kill失败需kill -9,GPU worker 3409056持38GB阻塞重启→全部清除,GPU4释放+port 8098释放 ②新vLLM serve启动(PID 425730 via setsid,nohup致CUDA graph capture时进程死亡→改setsid,--enable-auto-tool-choice --tool-call-parser hermes,GPU4:8098,39.6GB) ③tool-calling API验证:tool_choice:auto不再被拒(旧serve无tool-calling flag→400错误) ④Phase1生成启动:baize_posttrain_phase1_launch.sh --generate --model minicpm5-2b,setsid后台,log /tmp/phase1_generate.log ⑤生成在跑:8 workers,150/158 tasks in queue(8 in progress),193+ HTTP 200 req,153 submit_and_exit calls,模型发<function>XML tool calls→cline从content解析执行(多轮对话可见) ⑥关键发现:hermes parser不解析MiniCPM5 XML到tool_calls字段,但cline从content解析<function>标签→基础设施可用 ⑦GPU5/6/7占位serve仍UP(8095/8096/8097) ⑧sandbox仍不可达→评分仍需沙盒侧机器。本轮新增产出：R302✅(GPU4 vLLM重启[--enable-auto-tool-choice --tool-call-parser hermes/setsid/PID 425730/39.6GB]+Phase1生成启动[--generate --model minicpm5-2b/8 workers/150 in queue/193+ req/模型发<function> XML+cline从content解析]+wake295归档)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 ...+R302 GPU4重启+Phase1生成启动✅(生成在跑)/Phase1评分需沙盒侧机器/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake303 06:45] R303 Phase1生成tool-calling实时分析+退化循环发现[514 req/9704 run_commands/退化循环40次]+生成健康+serve 5端点UP+sandbox 107th CLOSED+GPU全占位+git synced: 体积自检(MEMORY 31.7KB→归档wake296/297→daily→27.3KB合规)→git synced(main=origin clean)→GPU:0-3 root SGLang~45GB/4 vLLM 39.6GB/5-7 vLLM各~38GB全占位→serve健康5端点✅(8095-8099全UP curl确认)→sandbox 107th wake 5 ports全FILTERED(仍阻塞)+MCP run_code同样-32001超时→①Phase1生成健康验证:PID 426644运行~16min,8 workers处理task 001-008,150/158 in queue,0 completed .py,514 HTTP 200 req,0 fail/0 timeout→生成健康运行中(run 1/5) ②tool-calling分布分析(vLLM GPU4日志30MB):grep <function name>→run_commands 9704/search_apis 5813/run_pyAether_code_tool 2592/submit_and_exit 2343/get_api_details 908/run_code 575/read_files 476/editor 124/search_apis_by_keyword 64→模型确实在使用工具,content XML解析正常工作 ③API测试:curl tool_choice=auto→content有<function>XML但tool_calls=[]→hermes parser不解析MiniCPM5 XML(R302结论复现确认),cline从content解析<function>标签→基础设施可用 ④退化循环发现:worker_1 task_002陷入pyAeur_code(缺h拼写错误)循环,grep 40次重复,系统反复提醒submit_and_exit(524次全局),模型无法跳出→D1/D2协议差距直接证据:base模型不懂得从执行反馈中学习,倾向于重复相同动作 ⑤R176对比:SFT模型15/16产出可执行代码+0/16退化循环→SFT消除退化循环 ⑥RL启示:退化循环=执行反馈未利用→R1二值reward=0即可惩罚退化 ⑦MEMORY归档wake296/297→daily腾位。本轮新增产出：R303✅(Phase1生成tool-calling实时分析[514 req/9704 run_commands/search_apis 5813/退化循环pyAeur_code 40次/D1D2协议差距直接证据/hermes parser复确认]+EXPERIMENTS §R303[7节:生成状态/tool-calling分布/退化循环/SFT对比/RL建议/局限/溯源]+wake296/297归档)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 ...+R302 GPU4重启+Phase1生成启动✅+R303 tool-calling实时分析✅(生成在跑)/Phase1评分需沙盒侧机器/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。
