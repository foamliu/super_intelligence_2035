# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake316（2026-11-12 R316 static eval FULL 113/113 COMPLETE definitive final analysis+7-point trend stability confirmed+sandbox 118th still FILTERED）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280归档；wake281-315✅；R316✅（FULL 113/113 definitive analysis[syn+38.9pp,stop+40.7pp,4.7x concise,4.0x faster]+API all-correct 0%→0%[SFT不修API知识]+per-scenario[Schematic +44pp最大]+7-point trend stability 20→113[monotonic↑]+failure mode[92.9% syn_ok_api_wrong=RL攻击面]+EXPERIMENTS §R316）
- 当前动作: wake316 ①R311 eval(PID 554362)已完成→113/113 ALL DONE ②FULL 113-task definitive analysis:syn 54.9%→93.8%(+38.9pp),stop 53.1%→93.8%(+40.7pp),trunc 46.9%→6.2%(-40.7pp,46 tasks eliminated),has_func 85.8%→100%,code 6762→1432chars(4.7x),API cov 0.141→0.166(1.17x),**All API correct 0%→0%[ZERO improvement]**,time 25.1→6.3s(4.0x faster) ③per-scenario:Schematic +44pp最大(n=41),DesignMgmt +43pp,Layout +36pp,Others +30pp(100% reached) ④7-point trend stability 20→50→70→80→90→110→113:syn delta +20/+26/+25.7/+30/+33.3/+38.2/+38.9pp monotonic↑,无下降拐点 ⑤failure mode:SFT后92.9% syn_ok_api_wrong→RL攻击面明确 ⑥D1-D6完整:D1+14.2pp/D2+0.024/D3-40.7pp/D4(syn)-38.9pp/D4(API)0pp/D5见per-scenario/D6 N/A ⑦sandbox 118th still FILTERED ⑧EXPERIMENTS §R316 updated
- 下一步: ①沙盒恢复后跑baize_posttrain_baseline_eval.sh获取真实Pass@1 5-run(static eval已全部完成) ②Phase1里程碑报告reports/report_posttrain_baseline_3model_zh.html(可基于R316完整数据撰写) ③Phase3 RL待沙盒+GPU ④P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴沙盒10.129.32.75全端口FILTERED(Pass@1需沙盒执行);P3等pretrain ckpt
- 本轮新增产出: R316✅(FULL 113/113 definitive final analysis[syn+38.9pp/stop+40.7pp/4.7x concise/4.0x faster]+API all-correct 0%→0%[SFT不修API知识→RL攻D4/D6]+per-scenario[Schematic +44pp最大]+7-point trend stability 20→113[monotonic↑无反转]+failure mode[92.9% syn_ok_api_wrong=RL攻击面]+D1-D6完整+EXPERIMENTS §R316)
- 未完成指令: 🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R316✅/Phase1 static eval COMPLETE(113/113 done)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU
- git: wake316 R316 pending commit



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

[wake313 12:05] R313 static eval 80/113 full-metric analysis[base vs SFT]+API coverage insight+per-scenario+4-point trend stability+sandbox 115th FILTERED: 体积自检(MEMORY ~29.5KB合规)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全占位→eval PID 554362仍在后台跑(etimes~42min,80/113 done)→sandbox 115th wake:22+8080全FILTERED→①full-metric analysis 80 tasks:syn 66.2%→96.2%(+30pp),stop 63.8%→95.0%(+31.2pp),length 36.2%→5.0%(-31.2pp),has_func 93.8%→100%,code 6370→1284chars(5.0x concise),time 23.5→5.3s(4.4x faster) ②API coverage 0.179→0.191(1.07x)→SFT修好格式/结构但API知识正确性改善微弱→与D4一致:SFT回收D1/D3协议问题,RL需攻D4/D6语义推理 ③per-scenario:DesignMgmt 47%→100%(+53pp最大受益),Layout 68%→95%,Others 74%→100%,Schematic 73%→91%(唯一未满分) ④4-point trend stability 20→50→70→80:syn delta +20/+26/+25.7/+30pp,conciseness 3.7/5.0/5.1/5.0x,无反转 ⑤~33 tasks待完成,预计1-2 wake内full 113完成。本轮新增产出：R313✅(80/113 full-metric analysis[syn+30pp/stop+31.2pp/5.0x concise/4.4x faster]+API cov 1.07x[SFT修格式不修API知识→RL攻D4/D6]+per-scenario[DesignMgmt +53pp最大/Schematic 91%最低]+4-point trend stability[无反转]+sandbox 115th FILTERED+EXPERIMENTS §R313)。未完成指令：🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R313✅/Phase1 static eval running(80/113 done,full in bg)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake314 12:12] R314 static eval 90/113 extended full-metric analysis[base vs SFT]+5-point trend stability confirmed+sandbox 116th FILTERED: 体积自检(MEMORY ~31.5KB合规)→GPU:0-3 root SGLang~45GB/4 vLLM~38GB base/5-7 vLLM~38GB占位→eval PID 554362仍在后台跑(etimes~47min,90/113 done)→sandbox 116th wake:22+8080全FILTERED→①extended full-metric analysis 90 tasks:syn 62.2%→95.6%(+33.3pp vs R313 +30pp↑),stop 60.0%→95.6%(+35.6pp),length 40.0%→4.4%(-35.6pp),has_func 92.2%→100%,code 6556→1255chars(5.2x vs R313 5.0x↑),API cov 0.164→0.186(1.13x vs R313 1.07x↑),time 24.0→5.2s(4.6x faster) ②per-scenario:DesignMgmt 53→95(+42pp最大),Layout 58→96(+38pp),Others 71→100(+29pp,SFT完全消除语法错),Schematic 67→92(+25pp最低) ③5-point trend stability 20→50→70→80→90:syn delta +20/+26/+25.7/+30/+33.3pp monotonic↑(无下降拐点),conciseness 3.7/5.0/5.1/5.0/5.2x稳定 ④API correct 13.1%→15.1%(+2pp微弱)→SFT修格式不修API知识结论更强 ⑤~23 tasks待完成,预计下1 wake内full 113完成。本轮新增产出：R314✅(90/113 extended full-metric analysis[syn+33.3pp/stop+35.6pp/5.2x concise/4.6x faster]+API cov 1.13x[SFT修格式不修API知识→RL攻D4/D6]+per-scenario[DesignMgmt +42pp最大/Others 100%]+5-point trend stability 20→50→70→80→90[monotonic↑无反转]+sandbox 116th FILTERED+EXPERIMENTS §R314)。未完成指令：🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R314✅/Phase1 static eval running(90/113 done,full in bg)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake315 12:25] R315 static eval 110/113 near-complete full-metric analysis[base vs SFT]+6-point trend stability+sandbox 117th FILTERED+MEMORY归档wake307-311: 体积自检(MEMORY 33KB→归档wake307-311→daily-memories→25KB合规)→GPU:0-3 root SGLang~45GB/4 vLLM~38GB base(68%util)/5-7 vLLM~38GB占位→eval PID 554362仍在后台跑(etimes~58min,110/113 done,仅~3待完成)→sandbox 117th wake:22全FILTERED→①near-complete full-metric analysis 110 tasks:syn 55.5%→93.6%(+38.2pp vs R314 +33.3pp↑),stop 53.6%→93.6%(+40.0pp),length 46.4%→6.4%(-40.0pp),has_func 86.4%→100%(+13.6pp),code 6726→1445chars(4.7x),API cov 0.143→0.168(1.17x vs R314 1.13x↑),API correct 7.5%→9.7%(+2.2pp),time 24.9→6.4s(3.9x faster) ②per-scenario:Schematic 45→88(+42pp最大,R314时最低+25pp→110-task反转为最高),DesignMgmt 55→95(+40pp),Layout 59→96(+37pp),Others 70→100(+30pp) ③6-point trend stability 20→50→70→80→90→110:syn delta +20/+26/+25.7/+30/+33.3/+38.2pp monotonic↑(无下降拐点),conciseness 3.7/5.0/5.1/5.0/5.2/4.7x稳定 ④base截断严重:46.4% finish=length vs SFT 6.4%→base长推理链频繁超max_tokens ⑤仅差3 tasks待完成,预计下1 wake内full 113完成。本轮新增产出：R315✅(110/113 near-complete full-metric analysis[syn+38.2pp/stop+40.0pp/4.7x concise/3.9x faster]+API cov 1.17x[SFT修格式不修API知识→RL攻D4/D6]+per-scenario[Schematic +42pp反转为最大/Others 100%]+6-point trend stability 20→50→70→80→90→110[monotonic↑无反转]+sandbox 117th FILTERED+MEMORY归档wake307-311→25KB+EXPERIMENTS §R315)。未完成指令：🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R315✅/Phase1 static eval running(110/113 done,仅3待完成)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake316 12:35] R316 static eval FULL 113/113 COMPLETE definitive final analysis+7-point trend stability+failure mode+sandbox 118th FILTERED: 体积自检(MEMORY ~27KB合规)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全占位→eval PID 554362已完成(不在进程列表)→113/113 ALL DONE→sandbox 118th wake:22+8080全FILTERED→①FULL 113-task definitive analysis:syn 54.9%→93.8%(+38.9pp),stop 53.1%→93.8%(+40.7pp),trunc 46.9%→6.2%(-40.7pp,46 tasks eliminated),has_func 85.8%→100%,code 6762→1432chars(4.7x),**All API correct 0%→0%[ZERO improvement]**,API cov 0.141→0.166(1.17x),time 25.1→6.3s(4.0x faster) ②per-scenario:Schematic +44pp最大(n=41),DesignMgmt +43pp(n=21),Layout +36pp(n=28),Others +30pp(n=23,100% reached) ③per-category:Geometry +53pp最大,SimConfig +29pp最低 ④7-point trend stability 20→50→70→80→90→110→113:syn delta +20/+26/+25.7/+30/+33.3/+38.2/+38.9pp monotonic↑,conciseness 3.7/5.0/5.1/5.0/5.2/4.7/4.7x稳定,无下降拐点 ⑤failure mode:base[syntax_error 45.1%/success_like 53.1%],SFT[syn_ok_api_wrong 92.9%/syntax_error 6.2%]→92.9%语法正确但API错误=RL攻击面 ⑥D1-D6完整:D1(func)+14.2pp/D2(cov)+0.024/D3(trunc)-40.7pp/D4(syn)-38.9pp/D4(API correct)0pp/D5 per-scenario见上/D6 N/A ⑦核心结论:SFT大幅回收协议问题(D1/D3)但API知识正确性零改善(D4)→RL需攻API正确性+迭代闭环 ⑧EXPERIMENTS §R316 updated。本轮新增产出：R316✅(FULL 113/113 definitive final analysis[syn+38.9pp/stop+40.7pp/4.7x concise/4.0x faster]+API all-correct 0%→0%[SFT不修API知识→RL攻D4/D6]+per-scenario[Schematic +44pp最大]+7-point trend stability 20→113[monotonic↑无反转]+failure mode[92.9% syn_ok_api_wrong=RL攻击面]+D1-D6完整+EXPERIMENTS §R316)。未完成指令：🔴17:10 GPU5/6/7全✅+GPU4 restarted✅;🔴13:40 Phase2 SFT COMPLETE✅+R300-R316✅/Phase1 static eval COMPLETE(113/113 done)/Phase3 RL脚本+奖励就绪✅待沙盒+GPU ⇒ WAITING=0。
