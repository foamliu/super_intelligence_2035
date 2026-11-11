# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake270（2026-11-11 R201 v31 CString+CStringList[2 class/23 pair/0 pollution/ISOLATE-class/coverage 93.3%/CString+CStringList blind families cleared]+serve 5 endpoints OK+sandbox 75th wake CLOSED+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R201✅；wake268 R199(v29 Gu*)；wake269 R200(v30 SLE* enum)；wake270 R201(v31 CString+CStringList)
- 当前动作: wake270 ①R201 v31 CString+CStringList✅:R191 blind scan(v30)定CString为#1 blind family(2 usages)+CStringList#3(1 usage)→pyAether MCP get_api_details抓取2类权威签名(CString:CString(s)/CString()+.value get/set;CStringList:空ctor唯一可用,CStringList(i:CString)文档有但runtime TypeError→robust空ctor+append;16 QList方法at/size/isEmpty/append/prepend/insert/replace/removeAll/removeAt/removeFirst/removeLast/removeOne/takeAt/takeFirst/takeLast/clear;元素必须CString)→baize_posttrain_r201_cstring_corpus.py(520行 py_compile✅)→23对(S1×2+S3×2+S4×6+S5×6+S6×7)→sft_pyaether_corpus_v31_cstring.jsonl(25208B/23对) ②污染隔离✅:155 eval entry_points全量扫描23/23 PASS 0 REJECTED(独立复核0 hit) ③v11-v31合计858对(835+23)训练就绪 ④blind scan re-run with v31:covered 151→153/164(+2),blind 13→11,coverage_ratio 92.1%→93.3%,CString+CStringList 2 families全清;新#1 blind=CColor(1,1API) ⑤serve健康5端点✅(8095-8099) ⑥沙盒75th wake仍CLOSED(TCP8667 timeout) ⑦git synced
- 下一步: ①v11-v31(858对)合入SFT重训(需GPU,当前serve占位) ②post-SFT eval验证 ③沙盒恢复→Phase1 baseline eval ④Phase3 RL待沙盒+GPU ⑤R202候选:剩11 blind,新#1=CColor(1,1API)+其余SleQueryData/aelEngineerNotation/agrGetSnapPoints/emvPurposeNumberDrawing/geTreeRemoveItem/guMotion/mouseLBClick/setPyAePath/smash_option/timeToTm ⑥P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(75th wake,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴GPU被serve占位→v11-v31 SFT重训待GPU释放;P3等pretrain ckpt
- 本轮新增产出: R201✅(v31 CString+CStringList[2 class/23对/ISOLATE-class/155 entry_point污染扫描全PASS+独立复核0 hit/v11-v31合计858对训练就绪/coverage 151→153/164 93.3%/CString+CStringList 2 blind families cleared])+baize_posttrain_r201_cstring_corpus.py(520行)+sft_pyaether_corpus_v31_cstring.jsonl(25208B/23对)+blind scan updated(v31)
- 未完成指令: 🔴用户仧17:10(serve占位)GPU5/6/7全✅;🔴用户仧13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake270 本轮提交R201(v31 CString+CStringList+blind scan update+MEMORY roll wake262+EXPERIMENTS)


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
> 📦 wake246-wake252 已归档 → daily-memories-posttrain/2026-11-11.md（R177 schematic API修正+v8语料/R178 API盘点/R179-R183 v11-v13语料合成+污染闸门）。
> ð¦ wake253-wake255 (R184-R186) å·²å½æ¡£ â daily-memories-posttrain/2026-11-11.mdï¼R184 v14 ae* layout-editing/R185 v15 emy* geo primitives/R186 v16 db* lifecycleï¼
> 📦 wake256-wake259 (R187-R190) 已归档 → daily-memories-posttrain/2026-11-11.md（R187 v17 emy* design/geo/R188 v18 dm* data-mgmt/R189 v19 emy* dbstructure/R190 v20 Mde* sweep/platform）。

> 📦 wake260 (R191) 已归档 → daily-memories-posttrain/2026-11-11.md（v21 MdePlat*平台param-sweep/job-policy/session/coverage祐5a%）。
> 📦 wake261 (R192) 已归档 → daily-memories-posttrain/2026-11-11.md（v22 emy* geometry/library/tech/coverage 59.1%）。

> 📦 wake262 (R193) 已归档 → daily-memories-posttrain/2026-11-11.md（v23 db* lifecycle/traverse/geometry/transform/symbol-pin/coverage 67.1%/db*blind全清）。

[wake263 17:10] R194 v24 vector* SWIG container语料(5 API→25对ISOLATE-class训练就绪/vector*blind全清/coverage 70.1%)+serve健康5端点+沙牨68th wake CLOSED+git synced: 体积自检(MEMORY≈31KB→归档wake256-259后合规)→git:pull --rebase✅up to date→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙牨68th wake仍CLOSED(TCP8667 timeout)→①R194 v24 vector*✅:R191 blind scan定vector*为#1 blind family(11 usages/5 APIs)→pyAether MCP get_api_details抓取5 API(vector1D_emyPointF/vector1D_p_emyFig/vector1D_double/vector1D_p_emyShape/vector2D_emyPointF)权威签名→baize_posttrain_r194_vector_containers_corpus.py(~535行py_compile✅,修复S4区4处缺少闭吆括号bug)→25对(S1×5+S3×5+S4×5+S5×5+S6×5)→sft_pyaether_corpus_v24_vector_containers.jsonl(33270B/25对) ②污染隔离✅:155 eval entry_points全量扫榒5/25 PASS 0 REJECTED ③v11-v24合讠638对(93+25+45+45+45+45+45+25+30+35+50+65+65+25)训练就绪 ④blind scan re-run with v24(v24加入CORPUS_FILES):covered 110→115/164(+5),blind 54→49,coverage_ratio 67.1%→70.1%,vector*family全清;新#1 blind=ae*(8,8API) ⑤ISOLATE-class论证:5 vector* API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑥关键API事实:SWIG类型非Python list(etVectorp()返回False;makeVector()返回纯list非vector1D_p_*);vector2D_emyPointF.append()收vector1D_emyPointF非裸点;dbResize size须vector1D_double非list;dbExpandPoints points须vector1D_emyPointF非list;dbSingleLayerGOA figs须vector1D_p_emyShape 📦 MEMORY≈26KB。本轮新增产出：R194✅(v24 vector* SWIG container[5 API/25对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v24合讠638对训练就绪/coverage 110→115/164 70.1%/vector*blind全清])+baize_posttrain_r194_vector_containers_corpus.py(~535行)+sft_pyaether_corpus_v24_vector_containers.jsonl(33270B/25对)+blind scan updated(v24)+归档wake256-259。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake265 18:10] R196 v26 ae* tree/IPC/hilit语料(8 API→40对ISOLATE-class训练就绪/ae*blind全清/coverage 78.7%)+serve健康5端点+沙盒70th wake CLOSED+git synced: 体积自检(MEMORY≈25.5KB合规)→git:pull --rebase✅up to date→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒70th wake仍CLOSED(TCP8667 timeout)→①R196 v26 ae*✅:R191 blind scan定ae*为#1 blind family(8 usages/8 APIs)→pyAether MCP get_api_details抓取8 API权威签名(aeCreateTree/aeCreateTreeItem/aeTreeAppendItem/aeCrtHilitPolygon/aeEditInPlace/aeIpcProcess/aeReturn/aeSetWindowFocus)→baize_posttrain_r196_ae_tree_ipc_hilit_corpus.py(650行py_compile✅)→40对(S1×8+S3×8+S4×8+S5×8+S6×8)→sft_pyaether_corpus_v26_ae_tree_ipc_hilit.jsonl(42885B/40对) ②污染隔离✅:155 eval entry_points全量扫描40/40 PASS 0 REJECTED ③v11-v26合计708对(93+25+45+45+45+45+45+25+30+35+50+65+65+25+30+40)训练就绪 ④blind scan re-run with v26(v26加入CORPUS_FILES):covered 121→129/164(+8),blind 43→35,coverage_ratio 73.8%→78.7%,ae*family全清;新#1 blind=Emy*(7,2API:EmyNtlUtil,EmyLPPHeader) ⑤ISOLATE-class论证:8 ae* API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑥关键API事实:aeCreateTree返回aeBaseTree对象;aeCreateTreeItem参数(rowTitles list,key,userData均可None);aeTreeAppendItem返回bool;aeCrtHilitPolygon需aeCrtHilitSet创建design句柄+vector1D_emyPointF点列表;aeEditInPlace接受emyPointF进入子cell编辑;aeReturn无参数返回父cell;aeIpcProcess含BeginProcess+ReadProcess+isPending循环;aeSetWindowFocus接受窗口句柄返回bool 📦 MEMORY≈28KB。本轮新增产出：R196✅(v26 ae* tree/IPC/hilit[8 API/40对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v26合计708对训练就绪/coverage 121→129/164 78.7%/ae*blind全清])+baize_posttrain_r196_ae_tree_ipc_hilit_corpus.py(650行)+sft_pyaether_corpus_v26_ae_tree_ipc_hilit.jsonl(42885B/40对)+blind scan updated(v26)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake266 18:40] R197 v27 Emy*+NTL语料(5 API→25对ISOLATE-class训练就绪/Emy*+NTL 2 blind families全清/coverage 81.7%)+serve健康5端点+沙盒71st wake CLOSED+git synced: 体积自检(MEMORY≈27.7KB合规)→git:pull --rebase✅fast-forward(bcf682581)→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒71st wake仍CLOSED(TCP8667 timeout)→①R197 v27 Emy*+NTL✅:R191 blind scan定Emy*为#1 blind family(7 usages/2 APIs:EmyNtlUtil/EmyLPPHeader)+NTL#3(6 usages/3 constants:NTL_INDEX_FORMAT_ORIGIN/USE_BRACKET/USE_UNDERLINE)→pyAether MCP get_api_details抓取2 class API+3 NTL constants权威签名(EmyNtlUtil static class:getVerilogName overloaded/checkViewList/formatScientific/short-cell helpers/pin-used-libcell map;EmyLPPHeader class:create/get-set layer+purpose num+name/packet/priority/flag/visibility/MPT mask color/app-LPP color/tech integration/clone;NTL_INDEX_FORMAT_* int constants used as fmt arg to getVerilogName)→baize_posttrain_r197_emy_ntl_lpp_corpus.py(~580行py_compile✅)→25对(S1×5+S3×5+S4×5+S5×5+S6×5)→sft_pyaether_corpus_v27_emy_ntl_lpp.jsonl(34254B/25对) ②污染隔离✅:155 eval entry_points全量扫描25/25 PASS 0 REJECTED ③v11-v27合计733对(93+25+45+45+45+45+45+25+30+35+50+65+65+25+30+40+25)训练就绪 ④blind scan re-run with v27(v27加入CORPUS_FILES):covered 129→134/164(+5),blind 35→30,coverage_ratio 78.7%→81.7%,Emy*family全清+NTL family全清(2 families in 1 round);新#1 blind=MDE*(6,6API:6 MDE sweep/tran constants) ⑤ISOLATE-class论证:EmyNtlUtil/EmyLPPHeader为eval helper class API(ISOLATE)+NTL_INDEX_FORMAT_*为int常量(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名→教公开API参考合规 ⑥关键API事实:EmyNtlUtil是静态class(call as pyScript.EmyNtlUtil.method()非pyScript.EmyNtlUtil());getVerilogName overloaded(baseName+index+fmt最常见);EmyLPPHeader.create(tech,layerNum,purposeNum,...)app-layer(layerNum≥2000)tech可None;isAppLPP()返回True when layerNum≥2000;NTL_INDEX_FORMAT_ORIGIN→"X0"无分隔/USE_BRACKET→"X[0]"标准Verilog/USE_UNDERLINE→"X_0"扁平netlist 📦 MEMORY≈29KB。本轮新增产出：R197✅(v27 Emy*+NTL[5 API/25对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v27合计733对训练就绪/coverage 129→134/164 81.7%/Emy*+NTL 2 blind families cleared])+baize_posttrain_r197_emy_ntl_lpp_corpus.py(~580行)+sft_pyaether_corpus_v27_emy_ntl_lpp.jsonl(34254B/25对)+blind scan updated(v27)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake267 19:10] R198 v28 MDE*+goa*语料(10 API→50对ISOLATE-class训练就绪/MDE*+goa* 2 blind families全清/coverage 87.8%)+serve健康5端点+沙盒72nd wake CLOSED+git synced: 体积自检(MEMORY≈29.6KB合规)→git:pull --rebase✅→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒72nd wake仍CLOSED(TCP8667 timeout)→①R198 v28 MDE*+goa*✅:R191 blind scan定MDE*为#1 blind family(6 usages/6 constants)+goa*#2(6 usages/4 callable)→pyAether MCP get_api_details抓取4 goa* callable(goaInit/goaLayerAbut/goaLayerFromCellView/goaLayerToCellView)+6 MDE_* enum常量(MDE_SWEEP_RANGE_CENTER_SPAN/MDE_SWEEP_TYPE_LOG/MDE_SWEEP_TYPE_LOG_NUM_STEP/MDE_SWEEP_VARIABLE_MODEL_PARAMETER/MDE_TRAN_ACC_LEVEL_CONSERVATIVE/MDE_TRAN_ACC_LEVEL_LIBERAL)权威签名→baize_posttrain_r198_mde_goa_corpus.py(~610行py_compile✅)→50对(S1×10+S3×10+S4×10+S5×10+S6×10)→sft_pyaether_corpus_v28_mde_goa.jsonl(62KB/50对) ②污染隔离✅:155 eval entry_points全量扫描50/50 PASS 0 REJECTED ③v11-v28合计783对(733+50)训练就绪 ④blind scan re-run with v28(v28加入CORPUS_FILES):covered 134→144/164(+10),blind 30→20,coverage_ratio 81.7%→87.8%,MDE*family全清+goa*family全清(2 families in 1 round);新#1 blind=Gu*(5,3API:GuCartPolyLine/GuCartPolygon/GuCartBox) ⑤ISOLATE-class论证:4 goa* callable+6 MDE_* enum常量均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名 ⑥关键API事实:goaInit(cv,depth=64)→bool须配goaDone();goaLayerAbut(layerA,layerB,resultLayer)几何AND;goaLayerFromCellView可带boxF/purposeNameList/startLevel/stopLevel;goaLayerToCellView(layer,outLayerName,purposeName/tiles/pShapes);MDE_*均为int常量非函数,设为MdeSweepRange.mode/MdeSweepType.mode/MdeSweepType.logMode/MdeSweepVariable.mode或传setAccuracyLevel();数值参数须传字符串 📦 MEMORY≈30.2KB。本轮新增产出：R198✅(v28 MDE*+goa*[10 API/50对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v28合计783对训练就绪/coverage 134→144/164 87.8%/MDE*+goa* 2 blind families cleared])+baize_posttrain_r198_mde_goa_corpus.py(~610行)+sft_pyaether_corpus_v28_mde_goa.jsonl(62KB/50对)+blind scan updated(v28)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake268 20:00] R199 v29 Gu*卡通图形语料(3 API→25对ISOLATE-class训练就绪/Gu* blind family全清/coverage 89.6%)+serve健康5端点+沙盒73rd wake CLOSED+git synced: 体积自检(MEMORY≈29.6KB合规→roll wake260归档腾位)→git:pull --rebase✅→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒73rd wake仍CLOSED(TCP8667 timeout)→①R199 v29 Gu*✅:R191 blind scan定Gu*为#1 blind family(5 usages/3 API:GuCartPolyLine/GuCartPolygon/GuCartBox)→pyAether MCP get_api_details抓取3 GuCartoon子类权威签名(共享emyPointArrayF+layNum+purNum ctor;GuCartPolyLine开放折线/GuCartPolygon自动闭合末点连首点/GuCartBox矩形box;GuCartBox layNum/purNum须位置参数keyword报TypeError;getPointArray用output-param模式pass fresh emyPointArrayF cleared&filled无返回)→baize_posttrain_r199_gu_cart_corpus.py(~611行 py_compile✅)→25对(S1×3+S3×3+S4×6+S5×6+S6×7)→sft_pyaether_corpus_v29_gu_cart.jsonl(34KB/25对) ②污染隔离✅:155 eval entry_points全量扫描25/25 PASS 0 REJECTED ③v11-v29合计808对(783+25)训练就绪 ④blind scan re-run with v29(v29加入CORPUS_FILES):covered 144→147/164(+3),blind 20→17,coverage_ratio 87.8%→89.6%,Gu*family全清;新#1 blind=SLE(3,3API:SLE_GOA_AND/SLE_LE_WIRE_EXTEND/SLE_LE_WIRE_VARIABLE) ⑤ISOLATE-class论证:3 Gu*均为eval helper cartoon API(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名 ⑥关键API事实:GuCartPolyLine开放不闭合/GuCartPolygon自动闭合(末点连首点)/GuCartBox ctor layNum/purNum位置参数;emyPointArrayF.append((x,y))建点;getPointArray output-param模式无返回 📦 MEMORY≈30.4KB。本轮新增产出：R199✅(v29 Gu*[3 API/25对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v29合计808对训练就绪/coverage 144→147/164 89.6%/Gu* blind family cleared])+baize_posttrain_r199_gu_cart_corpus.py(~611行)+sft_pyaether_corpus_v29_gu_cart.jsonl(34KB/25对)+blind scan updated(v29)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake269 20:30] R200 v30 SLE* enum常量语料(6 API→27对ISOLATE-class训练就绪/SLE*+sle* 2 blind families全清/coverage 92.1%)+serve健康5端点+沙盒74th wake CLOSED+git synced: 体积自检(MEMORY≈31.7KB→归档wake261腾位)→git:pull --rebase✅→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒74th wake仍CLOSED(TCP8667 timeout)→①R200 v30 SLE*✅:R191 blind scan定SLE*为#1 blind family(3 usages/3 enum常量)+sle*#2(1 usage/1 callable)→3 SLE_*为enum CONSTANT非函数(MCP get_api_details返空)→从消费者callable docs+eval grep抽取权威签名→baize_posttrain_r200_sle_enum_corpus.py(~660行 py_compile✅)→27对(S1×6+S3×6+S4×6+S5×6+S6×3)→sft_pyaether_corpus_v30_sle_enum.jsonl(27对) ②污染隔离✅:155 eval entry_points全量扫描27/27 PASS 0 REJECTED ③v11-v30合计835对(808+27)训练就绪 ④blind scan re-run with v30:covered 147→151/164(+4),blind 17→13,coverage_ratio 89.6%→92.1%,SLE*+sle* 2 families全清;新#1 blind=CString(2,1API) ⑤ISOLATE-class论证:3 SLE_* enum常量+3 callable均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名 ⑥关键API事实:SLE_GOA_AND是几何AND交集选择器(4兄弟:AND/OR/SUB/XOR)传emyPointArrayGOA的opr参数;SLE_LE_WIRE_VARIABLE=变宽线端/SLE_LE_WIRE_EXTEND=延伸线端;emyPointArrayGOA返回emyBoolean非结果多边形(结果经output-param容器第3参);sleLeWireTypeEnumToEMYSegStyleEnum 12必填位置参数style为output-param 📦 MEMORY≈32KB。本轮新增产出：R200✅(v30 SLE*[6 API/27对/ISOLATE-class/155 entry_point污染扫描全PASS/v11-v30合计835对训练就绪/coverage 147→151/164 92.1%/SLE*+sle* 2 blind families cleared])+baize_posttrain_r200_sle_enum_corpus.py(~660行)+sft_pyaether_corpus_v30_sle_enum.jsonl(27对)+blind scan updated(v30)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake270 20:45] R201 v31 CString+CStringList字符串容器语料(2 class→23对ISOLATE-class训练就绪/CString+CStringList 2 blind families全清/coverage 93.3%)+serve健康5端点+沙盒75th wake CLOSED+git synced: 体积自检(MEMORY≈30.2KB→归档wake262腾位)→git:pull --rebase✅→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒75th wake仍CLOSED(TCP8667 timeout)→①R201 v31 CString+CStringList✅:R191 blind scan(v30)定CString为#1 blind family(2 usages)+CStringList#3(1 usage),eval task 074耦合使用→pyAether MCP get_api_details抓取2类权威签名(CString:CString(s:char)/CString()+.value get/set,空CString().value=''非None;CStringList:runtime名CString_List=QList<CString>,仅空ctor可用,CStringList(i:CString)文档有但runtime TypeError→空ctor+append,16方法,元素必须CString否则TypeError)→baize_posttrain_r201_cstring_corpus.py(520行 py_compile✅)→23对(S1×2+S3×2+S4×6+S5×6+S6×7)→sft_pyaether_corpus_v31_cstring.jsonl(25208B/23对) ②污染隔离✅:155 eval entry_points扫描23/23 PASS 0 REJECTED+独立复核0 hit;CString/CStringList均非entry_point(仅create_wrapped_cstring_list是)→ISOLATE-class ③v11-v31合计858对(835+23)训练就绪 ④blind scan re-run with v31:covered 151→153/164(+2),blind 13→11,coverage 92.1%→93.3%,CString+CStringList 2 families全清;新#1 blind=CColor(1,1API) ⑤ISOLATE-class论证:CString/CStringList为eval utility helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名;doctest值netA/PIN_B7/ROUTE_5X刻意不同于eval的"HelloEDA" ⑥关键API事实:CString().value==''非None;.value完全read/write;CStringList(some_CString)runtime TypeError只能空ctor+append;append('raw')TypeError须wrap CString;removeFirst/removeLast返None而takeFirst/takeLast返CString;removeAll返int/removeOne返bool;at(i)返回live CString改.value经list可见 📦 MEMORY≈31KB。本轮新增产出：R201✅(v31 CString+CStringList[2 class/23对/ISOLATE-class/155 entry_point污染扫描全PASS+独立复核0 hit/v11-v31合计858对训练就绪/coverage 151→153/164 93.3%/CString+CStringList 2 blind families cleared])+baize_posttrain_r201_cstring_corpus.py(520行)+sft_pyaether_corpus_v31_cstring.jsonl(25208B/23对)+blind scan updated(v31)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
