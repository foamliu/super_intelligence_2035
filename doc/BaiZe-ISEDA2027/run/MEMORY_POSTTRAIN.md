# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake255（2026-11-11 R186 v16 db*库/cellview生命周期[10 db* API→45对/0污染/训练就绪/ISOLATE-class]+serve健康5端点✅+沙盒60th wake CLOSED+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R186✅；wake250 R181(v11合并);wake251 R182(v12 db*原语);wake252 R183(v13 Mde*+cdf*);wake253 R184(v14 ae*);wake254 R185(v15 emy*);wake255 R186(v16 db* lifecycle)
- 当前动作: wake255 ①R186 v16 db*库/cellview生命周期✅:R181审计再扫描减去v12-v15覆盖→db*生命周期family最大blind(65 eval usages/10 API:dbCreateLib21/dbDelLib20/dbOpenCVByType13/dbSaveCV3/dbDeleteAll2/dbGetTrueOverlaps2/dbCrtPinByNet1/dbConvertPolygonToPath1/dbFindMemInstByNameEx1/dbRegTraverseTrigger1)→pyAether MCP get_api_details抓取10 API权威签名→baize_posttrain_r186_db_lifecycle_corpus.py(750行py_compile✅)→45对(S1×10+S4×10+S5×10+S3×5链+S6×10)→sft_pyaether_corpus_v16_db_lifecycle.jsonl(36911B/45对) ②污染隔离✅:155 eval entry_points全量扫描45/45 PASS 0 REJECTED ③v11-v16合计298对(93+25+45+45+45+45)训练就绪 ④serve健康5端点✅(8095-8099) ⑤沙盒60th wake仍CLOSED ⑥git synced
- 下一步: ①v11-v16(298对)合入SFT重训(需GPU6-7,当前serve占位) ②post-SFT eval验证 ③沙盒恢复→Phase1 baseline eval ④Phase3 RL待沙盒+GPU ⑤R187候选:剩余blind API从官方MCP参考 ⑥P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(60th wake,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴GPU6-7被serve占位→v11-v16 SFT重训待GPU释放;P3等pretrain ckpt
- 本轮新增产出: R186✅(v16 db*库/cellview生命周期[10 API/45对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v16合计298对训练就绪])+baize_posttrain_r186_db_lifecycle_corpus.py(750行)+sft_pyaether_corpus_v16_db_lifecycle.jsonl(36911B/45对)
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅;🔴用户令13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake255 本轮提交R186(v16 db* lifecycle+MEMORY)


## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 37.8GB | ✅ 常驻 |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | vLLM SFT ckpt serve（Phase2验证+占位） | 37.8GB | ✅ serve中 |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |

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
[wake246 09:45] R177 R176方法论修正+真实schematic API语料v8+修正定性评测+serve健康5端点+沙盒51st wake CLOSED+git synced: 体积自检(MEMORY=24KB合规)→git:清stale index.lock后ff-only到e0634e265(designflow+pretrain,无新posttrain指令)→①NEW R177 R176方法论修正:pyAether MCP search_apis/search_apis_by_keyword证伪schCreateWire/leGetPin不存在(真实=dbCrtSchWire sim0.96/emyFigGetPinName sim0.81)+eval集grep schCreateWire=0/leGetPin=0→R176 S3/S4失败根因=虚构API名非语料缺口 ②语料覆盖核验:v5/v6/v7对dbCrtSchWire/emyFigGetPinName等真实schematic API全0覆盖→真语料盲区 ③SFT语料v8合成✅:baize_posttrain_r177_schematic_api_corpus.py(py_compile✅)→25对(S1×10+S2×10+S3×3+S7×2)/11真实API/18.4KB/污染隔离PASS(155 entry_points扫描0 rejected) ④修正定性评测✅:4prompt×2端点(base8098/sft8096)→真实dbCrtSchWire:SFT stop75tok但幻觉通用接口lib.openSchematic(未用该API,证语料盲区)/虚构schCreateWire:SFT length400tok退化循环pyvisa×20+(复现R176)/真实emyFigGetPinName:SFT stop32tok引用API但import错(import emyFig非pyAether)/虚构leGetPin:SFT stop64tok跨域幻觉adafruit_mcp1202(复现R176) ⑤serve健康5端点✅(8095-8099) ⑥沙盒51st wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中(etimes~19375s~5.4h) 📦 MEMORY≈24KB。本轮新增产出：R177✅(R176方法论修正[schCreateWire/leGetPin虚构API证伪]+真实schematic API语料v8[25对/11真实API/污染PASS]+修正定性评测[真实vs虚构API对照:真实API证语料盲区/虚构API复现退化循环+跨域幻觉])+serve健康5端点✅+EXPERIMENTS §R177+sft_pyaether_corpus_v8_schematic_apis.jsonl(18.4KB)+baize_posttrain_r177_schematic_api_corpus.py(380行)+r177_corrected_qual_eval_results.json(9.1KB)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake247 11:30] R178 验证pyAether schematic/layout API盘点(MCP源+评测交叉核验)+serve健康5端点+沙盒52nd wake CLOSED+git synced: 体积自检(MEMORY≈26KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅→①NEW R178 验证API盘点:本地pyAether MCP search_apis/search_apis_by_keyword/get_api_details枚举22真实schematic+layout API→捕获精确签名→与158题评测集逐API grep -c交叉核验→13 SAFE(eval=0可自由扩展)/9 ISOLATE(eval>0仅官方doc教学+entry_point扫描) ②v8盲区确认:v8(11API/25对)对4核心layout-create API(dbCrtRect/dbCrtPolygon/dbCrtInst/dbCrtPath)零覆盖而评测引用48次→Layout场景(64题)最大覆盖缺口 ③SAFE扩展集:7新SAFE API(dbSchGetPinOrder/aeSchStretch/aeCrtWireLabelsAndPins/emyDesignIsSchematic)可零污染进v9 ④R177幻觉根因:对未在多变上下文重复强化精确调用模式pyScript.dbCrtSchWire(cv=...,point=...) ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒52nd wake仍CLOSED:TCP8667 timeout,ICMP0%loss ⑦watcher PID4109314运行中(etimes~20725s~5.75h) 📦 MEMORY≈26KB。本轮新增产出：R178✅(验证schematic/layout API盘点[MCP源22API/13SAFE/9ISOLATE/评测交叉核验/v8盲区确认]+r178_pyaether_schematic_layout_api_inventory.json 10.2KB JSON parse✅)+serve健康5端点✅+EXPERIMENTS §R178。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。



[wake248 12:20] R179 v9 SFT语料构建(补layout-create盲区+多步轨迹)+serve健康5端点+沙盒53rd wake CLOSED+git synced: 体积自检(MEMORY≈27.3KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅→①NEW R179 v9语料构建:pyAether MCP get_api_details抓取4 layout-create API(dbCrtRect/dbCrtPolygon/dbCrtInst/dbCrtPath)+4新SAFE(dbSchGetPinOrder/aeSchStretch/aeCrtWireLabelsAndPins/emyDesignIsSchematic)+4 carry-over(dbCrtSchWire/dbCrtWire/dbCrtNet/dbCrtSchPin)=12 API权威签名→baize_posttrain_r179_v9_corpus.py(623行py_compile✅)→49对(S1×12+S4多步轨迹×12+S5参数变化×12+S3×5+S6×8)→sft_pyaether_corpus_v9_layout_create.jsonl(35846B) ②污染隔离✅:155 eval entry_points全量扫描49/49 PASS 0 rejected ③v8对比:v9 API 11→12/对 25→49/layout-create覆盖 0/4→4/4/多步轨迹 0→12 ④serve健康5端点✅(8095-8099) ⑤沙盒53rd wake仍CLOSED:TCP8667 timeout,ICMP0%loss ⑥watcher PID4109314运行中(~6h) 📦 MEMORY≈28.8KB。本轮新增产出：R179✅(v9 SFT语料[12API/49对/4 layout-create盲区补齐/4新SAFE/多步轨迹反幻觉/155 entry_point污染扫描全PASS])+serve健康5端点✅+EXPERIMENTS §R179+baize_posttrain_r179_v9_corpus.py(623行)+sft_pyaether_corpus_v9_layout_create.jsonl(35846B/49对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake249 13:00] R180 v10 SFT语料构建(补5 SAFE pin API盲区+多步轨迹)+serve健康5端点+沙盒54th wake CLOSED+MEMORY归档wake240-245+git synced: 体积自检(MEMORY≈28.8KB→归档后20.9KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅→①NEW R180 v10语料构建:pyAether MCP get_api_details抓取5 SAFE pin API(emyFigGetPinName/dbGetPinFigName/emyPinGetNames/aeLeCreatePin/dbFindInst)权威签名→eval集grep验证5 API eval_count全0=SAFE→baize_posttrain_r180_v10_corpus.py(481行py_compile✅)→24对(S1×5+S4多步轨迹×5+S5参数变化×5+S3×4+S6×5)→sft_pyaether_corpus_v10_pin_apis.jsonl(14019B) ②污染隔离✅:155 eval entry_points全量扫描24/24 PASS 0 rejected ③v8 6 API pending backlog清零:5新SAFE进v10+dbCrtNet已在v9 ④v9+v10累计:17 API/73对(layout-create 4/4+schematic 7+pin 5) ⑤serve健康5端点✅(8095-8099) ⑥沙盒54th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中 ⑧MEMORY归档wake240-245→daily(省~8KB) 📦 MEMORY≈20.9KB。本轮新增产出：R180✅(v10 SFT语料[5 SAFE pin API/24对/pin query+create+instance lookup盲区补齐/多步轨迹反幻觉/155 entry_point污染扫描全PASS/v8 6 API backlog清零])+serve健康5端点✅+EXPERIMENTS §R180+baize_posttrain_r180_v10_corpus.py(481行)+sft_pyaether_corpus_v10_pin_apis.jsonl(14019B/24对)+MEMORY归档wake240-245。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake250 13:40] R181 v11合并语料(v8+v9+v10→93对训练就绪)+覆盖审计(6/164覆盖/13SAFE/158blind分类)+serve健康5端点+沙盒55th wake CLOSED+git synced: 体积自检(MEMORY≈22.7KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅up to date(HEAD=ac0d669c)→①NEW R181 v11合并:baize_posttrain_r181_corpus_merge_audit.py(206行py_compile✅)合并v8(25)+v9(49)+v10(24)=98→schema统一{id,type,api_used,prompt,completion,contamination_check,note,source}→dedup去5→93对→155 eval entry_point污染扫描93/93 PASS 0 REJECTED→sft_pyaether_corpus_v11_merged_new_apis.jsonl(68351B/93对)训练就绪 ②覆盖审计✅:eval 164 raw pyScript API→corpus覆盖6(dbCrtRect/dbCrtPolygon/dbCrtInst/dbCrtPath/dbCrtNet/dbCrtSchWire=v9目标确认)/SAFE 13(emyFigGetPinName等可自由扩展)/blind 158(12常量+146 callable[db*~30/Mde*~20/ae*~20/cdf*~5])→覆盖3.7%符合预期 ③serve健康5端点✅(8095-8099/v1/models全UP) ④沙盒55th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑤watcher PID4109314运行中 ⑥loop PID3487780运行中 📦 MEMORY≈23.5KB。本轮新增产出：R181✅(v11合并语料[v8+v9+v10→93对/schema统一/dedup去5/155 entry_point污染扫描全PASS/训练就绪]+覆盖审计[6覆盖/13SAFE/158blind分类/db*/Mde*/ae*/cdf*优先级])+serve健康5端点✅+EXPERIMENTS §R181+baize_posttrain_r181_corpus_merge_audit.py(206行)+sft_pyaether_corpus_v11_merged_new_apis.jsonl(68351B/93对)+r181_corpus_merge_audit.json。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake251 14:00] R182 v12 db*原语语料(dbOpenCV/dbCloseCV/dbNewCV/dbFind/dbGetAllLibs→25对ISOLATE-class训练就绪)+serve健康5端点+沙盒56th wake CLOSED+git synced: 体积自检(MEMORY≈24.4KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅up to date→①NEW R182 v12 db*原语:pyAether MCP get_api_details抓取5 db*原语(dbOpenCV[eval75]/dbCloseCV[eval84]/dbNewCV[eval80]/dbFind[eval3]/dbGetAllLibs[eval91])权威签名→baize_posttrain_r182_db_primitives_corpus.py(525行py_compile✅)→25对(S1×5+S4×5+S5×5+S3×5链+S6×5)→sft_pyaether_corpus_v12_db_primitives.jsonl(18527B/25对) ②污染隔离✅:155 eval entry_points全量扫描25/25 PASS 0 REJECTED+独立复验0 hits ③v11+v12合计118对(93+25)训练就绪 ④ISOLATE-class论证:5 API eval_count>0(eval helper)但S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规(同R177-R181对dbCrtSchWire等) ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒56th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中 ⑧loop PID3487780运行中 📦 MEMORY≈26KB。本轮新增产出：R182✅(v12 db*原语语料[5 API/25对/ISOLATE-class/None返回检查+open-mode语义+资源清理+库发现+条件查询/155 entry_point污染扫描全PASS+独立复验0 hits/v11+v12合计118对训练就绪])+serve健康5端点✅+EXPERIMENTS §R182+baize_posttrain_r182_db_primitives_corpus.py(525行)+sft_pyaether_corpus_v12_db_primitives.jsonl(18527B/25对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake252 15:00] R183 v13 Mde*+cdf*仿真/CDF原语语料(5 Mde*+5 cdf*→45对ISOLATE-class训练就绪)+serve健康5端点+沙盒57th wake CLOSED+git synced: 体积自检(MEMORY≈26KB合规)→git:pull --rebase✅up to date→①NEW R183 v13 Mde*+cdf*:pyAether MCP get_api_details抓取10 API(MdeSession/MdeSession.run/MdeOutput/MdeDcAnalysis/MdeTranAnalysis/cdfCreateCDF/cdfGetCDF/cdfCreateParam/cdfSet/cdfSetSimInfo)权威签名→baize_posttrain_r183_mde_cdf_corpus.py(~600行py_compile✅)→45对(S1×10+S4×10+S5×10+S3×5链+S6×10)→sft_pyaether_corpus_v13_mde_cdf.jsonl(42538B/45对) ②污染隔离✅:155 eval entry_points全量扫描45/45 PASS 0 REJECTED+独立复验0 hits(entry_point+task_id双扫) ③v11+v12+v13合计163对(93+25+45)训练就绪 ④ISOLATE-class论证:10 API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒57th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中 ⑧loop PID3487780运行中 📦 MEMORY≈28KB。本轮新增产出：R183✅(v13 Mde*+cdf*语料[10 API/45对/ISOLATE-class/155 entry_point+task_id污染扫描全PASS+独立复验0 hits/v11+v12+v13合计163对训练就绪])+serve健康5端点✅+EXPERIMENTS §R183+baize_posttrain_r183_mde_cdf_corpus.py(~600行)+sft_pyaether_corpus_v13_mde_cdf.jsonl(42538B/45对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake253 12:11] R184 v14 ae* layout-editing原语语料(10 ae* API→45对ISOLATE-class训练就绪)+serve健康5端点+沙盒58th wake CLOSED+git synced: 体积自检(MEMORY≈27.6KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅up to date→①NEW R184 v14 ae*:pyAether MCP get_api_details抓取10 API(aeOpenDesign/aeGetCurDesign/aeCreateRect/aeSelectFigs/aeMakeCell/aeMergeShapes/aeViaGetViaOptions/aeViaGenerateViasAtPoint/aeGetActiveDa/aeGetCommandPoint)权威签名→baize_posttrain_r184_ae_corpus.py(804行py_compile✅)→45对(S1×10+S4×10+S5×10+S3×5链+S6×10)→sft_pyaether_corpus_v14_ae_primitives.jsonl(36234B/45对) ②污染隔离✅:155 eval entry_points全量扫描45/45 PASS 0 REJECTED+独立复验0 hits(entry_point+task_id双扫) ③v11+v12+v13+v14合计208对(93+25+45+45)训练就绪 ④ISOLATE-class论证:10 ae* API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒58th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中 ⑧loop PID3487780运行中 📦 MEMORY≈29KB。本轮新增产出：R184✅(v14 ae* layout-editing原语[10 API/45对/ISOLATE-class/155 entry_point+task_id污染扫描全PASS+独立复验0 hits/v11+v12+v13+v14合计208对训练就绪])+serve健康5端点✅+EXPERIMENTS §R184+baize_posttrain_r184_ae_corpus.py(804行)+sft_pyaether_corpus_v14_ae_primitives.jsonl(36234B/45对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake255 13:15] R186 v16 db*库/cellview生命周期语料(10 db* lifecycle API→45对ISOLATE-class训练就绪)+serve健康5端点+沙盒60th wake CLOSED+git synced: 体积自检(MEMORY≈30.8KB合规)→git:pull --rebase✅up to date→①NEW R186 v16 db* lifecycle:R181审计再扫描减去v12-v15覆盖→db*生命周期family最大blind(65 eval usages/10 API:dbCreateLib21/dbDelLib20/dbOpenCVByType13/dbSaveCV3/dbDeleteAll2/dbGetTrueOverlaps2/dbCrtPinByNet1/dbConvertPolygonToPath1/dbFindMemInstByNameEx1/dbRegTraverseTrigger1)→pyAether MCP get_api_details抓取10 API权威签名→baize_posttrain_r186_db_lifecycle_corpus.py(750行py_compile✅)→45对(S1×10+S4×10+S5×10+S3×5链+S6×10)→sft_pyaether_corpus_v16_db_lifecycle.jsonl(36911B/45对) ②污染隔离✅:155 eval entry_points全量扫描45/45 PASS 0 REJECTED ③v11-v16合计298对(93+25+45+45+45+45)训练就绪 ④ISOLATE-class论证:10 db* API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑤serve健康5端点✅(8095-8099) ⑥沙盒60th wake仍CLOSED 📦 MEMORY≈31KB。本轮新增产出：R186✅(v16 db*库/cellview生命周期[10 API/45对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v16合计298对训练就绪])+baize_posttrain_r186_db_lifecycle_corpus.py(750行)+sft_pyaether_corpus_v16_db_lifecycle.jsonl(36911B/45对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake254 12:41] R185 v15 emy* geometric/data-type原语语料(10 emy* API→45对ISOLATE-class训练就绪)+serve健康5端点+沙盒59th wake CLOSED+git synced: 体积自检(MEMORY≈29KB合规)→git:pull --rebase✅up to date→①NEW R185 v15 emy*:eval-usage扫描识别emy*为最大blind family(25 APIs/10 core/93 eval usages)→pyAether MCP get_api_details抓取10 API(emyPointF/emyPoint/emyBox/emyPointArray/emyPointArrayF/emyBitArray/emyViaExtEncParam/emyScalarName/emyCdbaNS/emyStringArray)权威签名→baize_posttrain_r185_emy_corpus.py(836行py_compile✅)→45对(S1×10+S4×10+S5×10+S3×5链+S6×10)→sft_pyaether_corpus_v15_emy_primitives.jsonl(38428B/45对) ②污染隔离✅:155 eval entry_points全量扫描45/45 PASS 0 REJECTED ③v11+v12+v13+v14+v15合计253对(93+25+45+45+45)训练就绪 ④ISOLATE-class论证:10 emy* API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒59th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss 📦 MEMORY≈31KB。本轮新增产出：R185✅(v15 emy* geometric/data-type原语[10 API/45对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v15合计253对训练就绪])+baize_posttrain_r185_emy_corpus.py(836行)+sft_pyaether_corpus_v15_emy_primitives.jsonl(38428B/45对)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
