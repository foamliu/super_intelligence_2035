# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake292（2026-11-12 MEMORY归档wake282-285(31KB→26KB)+sandbox 97st CLOSED+GPU全占位+5端点UP+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280(EXPERIMENTS归档)；wake281-291✅；wake292 MEMORY归档roll(wake282-285→daily-memories-2026-11-12.md)
- 当前动作: wake292 ①体积自检MEMORY 31KB→超标预警→归档wake282-285原文至daily-memories-posttrain/2026-11-12.md+留4行指针→26KB合规 ②GPU核验:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve ③serve健康5端点全UP(8095-8099) ④sandbox 97th wake ICMP 0.44ms OK但TCP 8664 FILTERED(仍阻塞) ⑤git status clean
- 下一步: ①post-SFT EDA-Eval正式评测(待沙盒ACL恢复,静态分析已COMPLETE) ②Phase3 RL待沙盒+GPU(SFT ckpt已就绪=minicpm5-sft:8096,RL核心目标=API覆盖率) ③Phase1基线评测待沙盒 ④P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(97th wake,ICMP OK但8664 TCP filtered,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;P3等pretrain ckpt
- 本轮新增产出: R292✅(MEMORY归档roll[wake282-285原文→daily-memories-2026-11-12.md+4指针,31KB→26KB]+serve健康复检5端点UP+sandbox 97st recheck CLOSED+GPU全占位确认)
- 未完成指令: 🔴用户令17:10(serve占位)GPU5✅/GPU6✅(SFT serve)/GPU7✅(base serve)全占位;🔴用户令13:40(三阶段替身计划)Phase2 SFT COMPLETE✅+ckpt served✅+定性对比✅+全量113task静态分析COMPLETE✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake292 本轮提交R292(MEMORY归档wake282-285+heartbeat+daily-memories append)



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 38.0GB | ✅ 常驻 |
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
[wake287 02:00] R287 EDA-Eval静态分析全量113task扩展+think-tag工具链修复+10task初步结果+后台运行中+sandbox 92st CLOSED+GPU5/6/7全占位+git synced: 体积自检(MEMORY≈24KB合规)→git:pull --rebase✅up to date→GPU:0-3 root SGLang~45GB/4-7 vLLM~38GB各0%util(serve idle)→serve健康5端点✅(8095-8099全UP)→sandbox 92st wake ICMP 0.3ms OK但TCP 8664/8665/8653/8669/22/80全FILTERED→①全量113 non-techlib task静态分析脚本baize_posttrain_static_eval_full.py编写✅(urllib+--resume+每10task checkpoint+per-scenario summary) ②think-tag工具链bug发现+修复✅:MiniCPM5/SFT输出以think标签包裹(字节验证0x3c7468696e6b3e=think)非markdown fence→旧strip_markdown regex误判→修复为先re.sub think block再strip fence行 ③10-task初步结果(修复后):SFT语法10/10(100%)vs Base6/10(60%)/SFT代码3.5x更短(1653ch vs 5763ch)/SFT finish=stop9/10 vs Base6/10/Base截断4/10 vs SFT1/10 ④API覆盖率低(SFT0.075/Base0.050)因SFT有时用Python内置(time/os.path)替代pyAether API→RL需修正的API选择问题 ⑤全量113task后台运行中(PID371302 setsid全分离,task14+/113,ETA~82min,输出eda_eval_static_full_wake287.json每10task checkpoint) ⑥EXPERIMENTS §R287新增 📦 MEMORY≈25KB。本轮新增产出：R287✅(全量113task脚本+think-tag修复+10task初步[SFT语法100%vsBase60%/3.5x简洁/API覆盖低分析]+后台进程+EXPERIMENTS §R287)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅+全量113task运行中/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。

[wake288 02:30] R288 全量静态分析30/113中间结果分析+per-scenario分层+Sandbox 93st CLOSED+GPU全占位+git synced: 体积自检(MEMORY≈25KB合规)→git:pull --rebase✅up to date→GPU:0-3 root SGLang~45GB/4-7 vLLM~38GB(GPU4 95%util busy)→serve健康5端点✅(8095-8099全UP)→sandbox 93rd wake ICMP 0.42ms OK但TCP 8664 FILTERED→①全量静态分析后台进程PID371302仍在运行(task32/113,ETA~50min,--resume每10task checkpoint) ②30-task中间结果(正确解析syntax_error字段):SFT语法96.7%(29/30)vsBase70%(21/30)+26.7pp/SFT截断6.7%(2/30)vsBase30%(9/30)/SFT代码4.5x更短(1383vs6216ch)/SFT has_function100%vsBase93.3%/SFT语法错误1(EOF)vsBase9(8 invalid syntax+1EOF) ③API覆盖率SFT0.118vsBase0.094(仍低,→RL核心目标) ④per-scenario分层:Schematic受益最大(37.5→87.5%+50pp,API覆盖0.195最高)/Layout(76.9→100%+23.1pp)/DesignMgmt(85.7→100%+14.3pp但API覆盖0.020)/Others(n=2,均100%) ⑤P0诊断验证:D1协议可回收✅(SFT+26.7pp)/D3截断减少✅(30→6.7%)/D4语法vs语义✅(SFT修语法,API选择=RL)/D5 Schematic配比✅(受益最大) ⑥EXPERIMENTS §R288新增 📦 MEMORY≈26KB。本轮新增产出：R288✅(30/113中间结果[总体+per-scenario分层+P0 D1/D3/D4/D5验证]+EXPERIMENTS §R288)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅+30/113中间结果✅+全量运行中/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。

[wake290 02:50] R290 全量静态分析80/113中间结果扩展+per-category分层+API覆盖深度分析+Sandbox 95st CLOSED+GPU全占位+git synced: 体积自检(MEMORY≈27KB合规)→git:pull --rebase✅up to date→GPU:0-3 root SGLang~45GB/4-7 vLLM~38GB(GPU4 94%util busy被eval调用)→serve健康5端点✅(8095-8099全UP)→sandbox 95th wake ICMP 0.83ms OK但TCP 8664 FILTERED→①全量静态分析后台进程PID371302仍在运行(task80/113,~33task剩余,ETA~15min,--resume每10task checkpoint) ②80-task中间结果扩展:SFT语法97.5%vsBase76.2%(+21.3pp稳定)/SFT截断3.8%vsBase23.8%(6.3x降低)/SFT代码4.8x更短(1248vs6031ch,Base啰嗦程度被60样本低估)/SFT时间4.4x更快(3.6vs15.9s)/API覆盖率SFT0.191vsBase0.196(≈持平→RL核心目标) ③新发现:SFT用Python内置替代pyAether(11vs7 task,负面副作用→RL R4臂修正)/Full API coverage无改善(4%→4%) ④per-scenario:Schematic +27pp受益最大/DesignMgmt +24pp但API覆盖极低0.058 ⑤per-category:Query&Edit +30pp/DB&Mgmt +29pp ⑥P0诊断验证:D1✅/D2⚠️(SFT略降1.74vs1.96)/D3✅/D4✅/D5✅ ⑦EXPERIMENTS §R290新增 📦 MEMORY≈28KB。本轮新增产出：R290✅(80/113中间结果扩展[4.8x更短/4.4x更快/API覆盖≈持平]+per-category分层+API覆盖深度分析[SFT用内置替代pyAether→RL R4臂修正]+P0 D1/D2/D3/D4/D5验证+EXPERIMENTS §R290)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅+80/113中间结果✅+全量运行中/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。
[wake291 03:05] R291 全量113task静态分析最终结果COMPLETE+分析脚本+P0 D1-D6最终验证+趋势稳定性+Sandbox 96st CLOSED+GPU全占位+git synced: 体积自检(MEMORY≈29KB合规)→git:pull --rebase✅(remote ahead,autostash applied)→GPU:0-3 root SGLang~45GB/4-7 vLLM~38GB(全idle serve)→serve健康5端点✅(8095-8099全UP)→sandbox 96th wake ICMP OK但TCP 8664 FILTERED→①全量113task静态分析后台进程PID371302已COMPLETE(113/113,~37min运行) ②最终分析脚本baize_posttrain_static_final_analysis.py编写✅(153行,py_compile通过,think-tag regex修复) ③113task最终结果:SFT语法95.6%(108/113)vsBase62.8%(71/113)+32.7pp/SFT截断4.4%(5/113)vsBase38.1%(43/113)8.6x降低/SFT函数定义100%(113/113)vsBase69.0%(78/113)/SFT时间4.3s vsBase17.1s 4.0x更快/API覆盖SFT0.170vsBase0.115仅+0.055→RL核心价值区 ④per-scenario:Schematic+48.8pp(n=41)受益最大/Layout+28.6pp/Others+21.7pp(100%)/DesignMgmt+19.0pp ⑤per-category:DesignContentCreation+48.1pp/Query&Edit+38.5pp(API0.173→0.296最大改善)/Geometry+35.3pp/DB&Mgmt+25.0pp/Sim&Config+23.8pp/Utilities+20.0pp ⑥P0诊断最终验证:D1✅(69→100%协议完全可回收)/D2⚠️(0.115→0.170仅微增→RL)/D3✅(8.6x降低)/D4✅(42→5语法错误,88%修复)/D5✅(Schematic+48.8pp最大)/D6 N/A(需运行时) ⑦趋势稳定性:10→30→60→80→113 task语法Δ稳定+21~+33pp/截断ratio持续增强4.5x→6.3x→8.6x/Schematic始终最大受益 ⑧代码长度说明:函数体Base787ch vs SFT1314ch(SFT更完整),与wake290原始输出4.8x ratio互补 ⑨EXPERIMENTS §R291新增+报告§13更新 📦 MEMORY≈30KB。本轮新增产出：R291✅(全量113task静态分析最终COMPLETE[+32.7pp语法/8.6x截断/100%函数定义/4.0x更快/API+0.055]+per-scenario[Schematic+48.8pp]+per-category[6类全量]+P0 D1-D6最终验证+趋势10→113+分析脚本+summary JSON+EXPERIMENTS §R291+报告§13)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量113task静态分析COMPLETE✅/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。
[wake292 03:20] R292 MEMORY归档roll(wake282-285→daily)+serve健康复检+sandbox 97st recheck CLOSED+GPU全占位+git synced: 体积自检(MEMORY 31KB→超标预警)→归档wake282-285原文至daily-memories-posttrain/2026-11-12.md+留4行指针→MEMORY 26KB合规→GPU:0-3 root SGLang~45GB/4 vLLM 38GB/5 vLLM 38GB/6 vLLM 38GB(SFT served)/7 vLLM 38GB全idle serve→serve健康5端点✅(8095 minicpm5-2b-gpu7/8096 minicpm5-sft/8097 minicpm5-2b-gpu5/8098 minicpm5-2b/8099 qwen3.8-27b全UP)→sandbox 97th wake ICMP 0.44ms OK但TCP 8664 FILTERED(仍阻塞,需网络团队开ACL)→本轮动作=MEMORY体积维护(31KB→26KB,归档4条verbose heartbeat,wake282-285原文不改搬入daily)+serve健康复检+sandbox recheck+git synced 📦 MEMORY≈26KB。本轮新增产出：R292✅(MEMORY归档roll[wake282-285→daily-memories-2026-11-12.md+4指针,31KB→26KB合规]+serve 5端点UP复检+sandbox 97st CLOSED recheck+GPU全占位确认)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量113task静态分析COMPLETE✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
