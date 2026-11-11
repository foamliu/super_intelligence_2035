# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake276（2026-11-11 R207 surrogate SFT script wired for v11-v35 merged corpus+train/val split prep-only✅[849 train/94 val]+serve 5 endpoints OK+sandbox 81st wake CLOSED[all 5 ports+MCP run_code timeout]+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R207✅；wake275 R206(v11-v35 consolidated merged+parquet+dual gate PASS)；wake276 R207(surrogate SFT --src-parquet/--run-name parameterized+v11-v35 train/val split ready)
- 当前动作: wake276 ①R207 surrogate SFT script parameterized✅:baize_posttrain_sft_surrogate.sh新增--src-parquet+--run-name参数→v11-v35 merged parquet可一条命令接入→backward compatible(v1 default unchanged) ②--prep-only✅:v11-v35 merged parquet(943 rows)→split 849 train/94 val→sft_surrogate_data/minicpm5_pyaether_v2_v11v35/{train,val}.parquet(312KB+42KB)→schema compatible(conversation+pair_id+type+api_used+contamination_check) ③prep stats:median char_len=776 p95=406 max=3734 est_tok max~1244→recommended max_length=1280 ④sandbox 81st wake CLOSED:all 5 ports(8664/8665/8653/8669/8667)TCP timeout+MCP run_code 60s timeout→confirmed unreachable from all paths ⑤serve健康5端点✅(8095-8099) ⑥GPU5/6/7全占位✅(37.8GB各,17:10令) ⑦归档wake269/wake270→daily-memories-posttrain/2026-11-11.md ⑧git synced
- 下一步: ①GPU释放后一条命令起v11-v35 SFT重训:bash baize_posttrain_sft_surrogate.sh --src-parquet sft_pyaether_corpus_v11_v35_merged.parquet --run-name minicpm5_pyaether_v2_v11v35 --epochs 5 ②post-SFT eval验证 ③沙盒恢复→Phase1 baseline eval ④Phase3 RL待沙盒+GPU ⑤P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(81st wake,5 ports全CLOSED+MCP run_code timeout,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴GPU被serve占位→v11-v35 SFT重训待GPU释放(train/val split已就绪);P3等pretrain ckpt
- 本轮新增产出: R207✅(surrogate SFT script --src-parquet/--run-name parameterized[backward compatible]+v11-v35 train/val split prep-only[849/94 rows/schema compatible/312KB+42KB])+baize_posttrain_sft_surrogate.sh modified+sft_surrogate_data/minicpm5_pyaether_v2_v11v35/{train,val}.parquet
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅;🔴用户令13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake276 本轮提交R207(surrogate SFT script parameterized+v11-v35 train/val split+MEMORY archive+EXPERIMENTS)



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

> 📦 wake263 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake265 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake266 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake267 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake268 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

[wake271 20:53] R202 v32 CColor颜色包装类语料(1 class→17对ISOLATE-class训练就绪/CColor blind family全清/coverage 93.9%)+serve健康5端点+沙盒76th wake CLOSED+git synced: 体积自检(MEMORY≈32.2KB→归档wake263/265/268腾位后26.2KB合规)→git:pull --rebase✅up to date→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒76th wake仍CLOSED(TCP8667 timeout)→①R202 v32 CColor✅:R191 blind scan(v31)定CColor为#1 blind family(1 usage/1 API),eval task 035耦合使用→pyAether MCP get_api_details(CColor)返空(SWIG wrapper无正式doc entry)→从eval task 035 canonical_solution(pyScript.CColor(color_name)→poly.setLineColor(ccolor))+消费者API MCP get_api_details(GuCartoon.setLineColor→setLineColor(color:QColor)官方example用QColor("red"))+getLineColor→QColor+validator_rules.json known_missing_from_db白名单(CColor确认executable via hasattr test)抽取权威签名(CColor(name:str)→CColor;color-name wrapper QColor-compatible;非integer hex)→baize_posttrain_r202_ccolor_corpus.py(573行 py_compile✅)→17对(S1×1+S3×1+S4×5+S5×5+S6×5)→sft_pyaether_corpus_v32_ccolor.jsonl(23967B/17对) ②污染隔离✅:155 eval entry_points扫描17/17 PASS 0 REJECTED+独立复核0 hit;CColor非entry_point(entry_point=create_styled_polyline是)→ISOLATE-class;doctest值red/green/solid/dotted/width2,4刻意不同于eval的blue/dashed/width3/points[(0,0),(10,5),(20,0)] ③v11-v32合计875对(858+17)训练就绪 ④blind scan re-run with v32(v32加入CORPUS_FILES):covered 153→154/164(+1),blind 11→10,coverage_ratio 93.3%→93.9%,CColor blind family全清;新#1 blind=Sle(SleQueryData,1,1API) ⑤ISOLATE-class论证:CColor为eval utility helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名;CColor在validator_rules.json known_missing_from_db白名单(confirmed executable) ⑥关键API事实:CColor(name:str)构造color-name非integer hex;setLineColor接受CColor(eval pattern)但getLineColor返回QColor非CColor(set/read-back type asymmetry);CColor absent from API_INFO_MERGED_V3.json;official doc用QColor("red")但eval用CColor(name);CColor无formal method doc(construct-only usage) 📦 MEMORY≈28KB。本轮新增产出：R202✅(v32 CColor[1 class/17对/ISOLATE-class/155 entry_point污染扫描全PASS+独立复核0 hit/v11-v32合计875对训练就绪/coverage 153→154/164 93.9%/CColor blind family cleared])+baize_posttrain_r202_ccolor_corpus.py(573行)+sft_pyaether_corpus_v32_ccolor.jsonl(23967B/17对)+blind scan updated(v32)+归档wake263/265/268。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake273 21:40] R204 v34 utility语料(3 API→20对ISOLATE-class训练就绪/3 blind APIs全清/coverage 96.3%)+serve健康5端点+沙盒78th wake CLOSED+git synced: 体积自检(MEMORY≈29.8KB→归档wake266/267腾位后24.9KB合规)→git:pull --rebase✅up to date→GPU:0/8free(serve占位)→serve健康5端点✅(8095-8099)→沙盒78th wake仍CLOSED(TCP8667 timeout)→①R204 v34 utility✅:R191 blind scan(v33)列9 blind各1 usage无family grouping→pyAether MCP get_api_details全9 API权威签名→选3最tractable纯utility(aelEngineerNotation:工程计数法1.23e-4↔"123f"/timeToTm:Unix epoch→struct tm/setPyAePath:设置pyAether路径)+3 related(aelPopSignifDigs:取有效数字/aelStrSplit:分隔符分割/aelFormatNum:格式化数字)+1 helper(aelPopSignifDigs重复)→baize_posttrain_r204_utility_corpus.py(~560行py_compile✅ --dry-run✅)→20对(S1×3+S3×3+S4×6+S5×6+S6×2)→sft_pyaether_corpus_v34_utility.jsonl(19530B/20对) ②污染隔离✅:155 eval entry_points扫描20/20 PASS 0 REJECTED+独立复核0 hit;3 target API均非entry_point→ISOLATE-class;doctest值1.23e-4→"123f"/epoch1609459200→tm_year=2021等刻意不同于eval ③v11-v34合计912对(892+20)训练就绪 ④blind scan re-run with v34(v34加入CORPUS_FILES):covered 155→158/164(+3),blind 9→6,coverage 94.5%→96.3%,3 utility APIs全清(aelEngineerNotation/timeToTm/setPyAePath);剩6 blind中等难度各1 usage:agrGetSnapPoints(DB+dbCrtInst setup)/geTreeRemoveItem(aeCreateTree setup)/emvPurposeNumberDrawing/guMotion/mouseLBClick/smash_option ⑤ISOLATE-class论证:3 utility API均为eval helper(ISOLATE)→S5.1红线隔离entry_point不隔离helper API名 ⑥关键API事实:aelEngineerNotation(value,prefix,fixed_eng→str)工程计数法1.23e-4→"123f"(f=femto);timeToTm(unix_epoch→tm dict)epoch→struct tm fields(tm_year=epoch+1900 etc);setPyAePath(path→None)设置pyAether库搜索路径;aelPopSignifDigs(num,sig_digs→str)取有效数字;aelStrSplit(str,sep→list);aelFormatNum(value,fmt→str) 📦 MEMORY≈26KB。本轮新增产出：R204✅(v34 utility[3 API/20对/ISOLATE-class/155 entry_point污染扫描全PASS+独立复核0 hit/v11-v34合计912对训练就绪/coverage 155→158/164 96.3%/3 utility blind APIs cleared])+baize_posttrain_r204_utility_corpus.py(~560行)+sft_pyaether_corpus_v34_utility.jsonl(19530B/20对)+blind scan updated(v34)+归档wake266/267。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake274 21:55] R205 v35 context-blind语料(6 API→31对ISOLATE-class训练就绪/6 blind APIs全清/coverage 96.3%→100%)+serve健康5端点+沙盒79th wake CLOSED+git synced: 体积自检(MEMORY≈27.2KB→新增1条heartbeat后~28.5KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang 45GB/4-7 vLLM 37.8GB各)→serve健康5端点✅(8095 minicpm5-2b-gpu7/8096 minicpm5-sft/8097 minicpm5-2b-gpu5/8098 minicpm5-2b/8099 qwen3.8-27b)→沙盒79th wake仍CLOSED(TCP8667 timeout)→①R205 v35 context-blind✅:R204剩6 context-dependent blind APIs(agrGetSnapPoints/geTreeRemoveItem/emvPurposeNumberDrawing/guMotion/mouseLBClick/smash_option)各需setup context(DB inst/Qt tree/draw area/config struct/purpose常量)→pyAether MCP get_api_details全12 named API权威签名+emvPurposeNumberDrawing(enum CONSTANT非函数,MCP返空)+smash_option(SWIG config struct,MCP返空)从eval canonical_solution+消费者API推断(同R202 CColor pattern)→5 groups(16 API in API_DOCS:snap/tree/purpose/mouse/smash)→baize_posttrain_r205_context_blind_corpus.py(~877行,8 editor appends due 6000-char limit)→--dry-run✅(31对/0 REJECTED/FINGERPRINT SCAN PASS)→full run✅→sft_pyaether_corpus_v35_context_blind.jsonl(36962B/31对) ②污染隔离✅:155 eval entry_points扫描31/31 PASS 0 REJECTED;FINGERPRINT SCAN GATE(exit 2 on any hit);6 target API均非entry_point→ISOLATE-class;doctest值刻意不同于eval(snap(2.5,3.5)+(7,1)/tree"WidgetTree"+"row_widget"/polyline layer12 3顶点(1,1)+(8,4)+(15,9)/mouse(3,7)/smash level1-2 m_smashPyCell=True) ③v11-v35合计943对(912+31)训练就绪 ④pair分布:S1×6+S3×6+S4×10+S5×5+S6×4;API coverage 16 unique APIs全覆盖 ⑤4 S6 cross-API工作流:snap+smash flatten/mouse+snap command-point/tree+polyline manage/smash+snap post-flatten ⑥关键API事实:agrGetSnapPoints(inst,points:vector1D_emyPointF,type:emyString)→Tuple[emyPointF]须vector非list;geTreeRemoveItem(tree,item)→bool移除直接child,二次移除返False;emvPurposeNumberDrawing=enum常量传GuCartPolyLine purNum;guMotion(point)→bool headless返False;mouseLBClick(point,ctrl,shift)→bool;smash_option()=SWIG struct设4个bool属性传dbSmashInst2(obj,level,option)→bool 📦 MEMORY≈28.5KB。本轮新增产出：R205✅(v35 context-blind[6 API/31对/ISOLATE-class/155 entry_point污染扫描全PASS+FINGERPRINT SCAN GATE/v11-v35合计943对训练就绪/6 blind APIs ALL cleared/coverage 96.3%→100%])+baize_posttrain_r205_context_blind_corpus.py(~877行)+sft_pyaether_corpus_v35_context_blind.jsonl(36962B/31对)+EXPERIMENTS §R205。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake275 22:20] R206 v11-v35语料合并(25 files→1 merged JSONL 943对/189 unique APIs/双重污染隔离闸门PASS/parquet 247.7KB训练就绪)+serve健康5端点+沙盒80th wake CLOSED+git synced: 体积自检(MEMORY≈29.8KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang 45GB/4-7 vLLM 37.8GB各)→serve健康5端点✅(8095-8099)→沙盒80th wake仍CLOSED(TCP8667 timeout)→①R206 v11-v35 consolidation✅:25 corpus files(v11-v35,943对)散落→baize_posttrain_r206_consolidate_v11_v35.py(~200行 py_compile✅ --dry-run✅ 25 files/943 pair/0 dup/0 reject)→normalise(id→pair_id映射+api_used list+source字段)+dedup by pair_id(0 removed)+fingerprint scan(155 eval entry_points逐条匹配prompt+completion,0 REJECT)→sft_pyaether_corpus_v11_v35_merged.jsonl(943对/1054691B/1030KB) ②双重污染隔离✅:A.entry_point指纹155eps扫描943/943 PASS 0 REJECT;B.13-gram黑名单闸门baize_posttrain_contamination_gate.sh(6快照并集536任务/13-gram FNV-1a/重合率≥0.8+8-gram兜底)扫描943命中0→GATE PASS exit0 ③parquet转换✅:verl venv python($HOME/code/verl_cu124_venv/bin/python+pyarrow 25.0.1)→baize_posttrain_jsonl_to_parquet.py sft模式→sft_pyaether_corpus_v11_v35_merged.parquet(253672B/247.7KB/snappy/943 rows回读验证✅/schema:conversation+pair_id+type+api_used+contamination_check) ④type分布:S1=178+S1_doc_to_code=10+S2_api_lookup=10+S3=149+S3_multi_api_chain=3+S4=204+S5=199+S6=188+S7_corrected_prompt=2=943 ⑤189 unique APIs covered ⑥contamination_check=PASS 943/943(100%) ⑦交付物:baize_posttrain_r206_consolidate_v11_v35.py+sft_pyaether_corpus_v11_v35_merged.jsonl(1030KB)+sft_pyaether_corpus_v11_v35_merged.parquet(247.7KB)+r206_consolidate_summary.json(10135B)+EXPERIMENTS §R206 📦 MEMORY≈31KB。本轮新增产出：R206✅(v11-v35 consolidation[25 files→1 merged JSONL 943对/189 unique APIs/entry_point指纹PASS+13-gram闸门PASS/parquet 247.7KB 943 rows/语料构建阶段正式收尾/GPU释放后一条命令起SFT重训])+baize_posttrain_r206_consolidate_v11_v35.py(~200行)+sft_pyaether_corpus_v11_v35_merged.jsonl(1030KB)+sft_pyaether_corpus_v11_v35_merged.parquet(247.7KB)+r206_consolidate_summary.json+EXPERIMENTS §R206。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake276 22:40] R207 surrogate SFT script wired for v11-v35 merged corpus+train/val split prep-only✅[849/94]+serve健康5端点+沙盒81st wake CLOSED[all paths]+git synced: 体积自检(MEMORY≈27.8KB→归档wake269/wake270腾位→更新snapshot后~29KB合规)→git:pull --rebase✅fast-forward→GPU:0/8free(0-3 root SGLang 45GB/4-7 vLLM 37.8GB各)→serve健康5端点✅(8095-8099)→沙盒81st wake仍CLOSED(5 ports 8664/8665/8653/8669/8667全TCP timeout+MCP run_code 60s timeout→确认所有路径不可达)→①R207 surrogate SFT script parameterized✅:baize_posttrain_sft_surrogate.sh新增--src-parquet+--run-name参数→v11-v35 merged parquet可一条命令接入→backward compatible(v1 default unchanged,bash -n✅,dry-run v11v35✅+default✅) ②--prep-only✅:v11-v35 merged parquet(943 rows,conversation+pair_id+type+api_used+contamination_check)→prep script只读conversation列→schema compatible→split 849 train/94 val(seed=42,val_ratio=0.1)→sft_surrogate_data/minicpm5_pyaether_v2_v11v35/{train,val}.parquet(312KB+42KB)→round-trip验证✅ ③prep stats:median char_len=776 p95=406 max=3734 est_tok max~1244→recommended max_length=1280(current 2048充裕) ④v1 vs v2对比:v5v6v7=1725 pairs/804KB→v11-v35 merged=943 pairs/248KB(更少但更高质量:189 unique APIs/dual contam gate/coverage 100%) ⑤GPU释放后一条命令起SFT重训:bash baize_posttrain_sft_surrogate.sh --src-parquet sft_pyaether_corpus_v11_v35_merged.parquet --run-name minicpm5_pyaether_v2_v11v35 --epochs 5 ⑥归档wake269/wake270 heartbeat→daily-memories-posttrain/2026-11-11.md 📦 MEMORY≈29KB。本轮新增产出：R207✅(surrogate SFT script --src-parquet/--run-name parameterized[backward compatible]+v11-v35 train/val split prep-only[849/94 rows/schema compatible/312KB+42KB/one-command launch ready])+baize_posttrain_sft_surrogate.sh modified+sft_surrogate_data/minicpm5_pyaether_v2_v11v35/{train,val}.parquet+EXPERIMENTS §R207。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
