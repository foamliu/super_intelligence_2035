# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake284（2026-11-12 v11-v36 SFT训练COMPLETE step70/70 loss0.618 val0.673+SFT ckpt served GPU6:8096 minicpm5-sft smoke test PASS+GPU5/6/7全占位+serve脚本修复+sandbox 89th wake CLOSED+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280(EXPERIMENTS归档)；wake281 R281(全链路就绪审计20项)；wake282 R282(v11-v36 SFT重训启动+NCCL P2P fix)；wake283 R283(SFT训练监控+ckpt验证+serve dry-run)；wake284 R284(SFT训练COMPLETE+训练动力学分析+serve脚本修复+SFT ckpt served+smoke test PASS)
- 当前动作: wake284 ①v11-v36 SFT训练COMPLETE 70/70(train loss 0.618/val loss 0.673/rc=0/01:11:28) ②global_step_70 ckpt 715MB HF safetensors完整 ③SFT ckpt SERVED on GPU6:8096(minicpm5-sft,vLLM 37.8GB,smoke test PASS:dbCreateCell回答正确) ④GPU7 serve base MiniCPM5-2B on 8095(37.8GB) ⑤GPU5/6/7全占位(17:10令满足) ⑥训练动力学分析:E1→E4 -51.7%,loss floor~0.6 ⑦serve脚本修复3处(SFT_RUNS_DIR v2_v11v36+--run-name+--ckpt裸名解析) ⑧sandbox 89th wake CLOSED ⑨git synced
- 下一步: ①post-SFT EDA-Eval评测(待沙盒ACL恢复→watcher auto-launch) ②Phase3 RL待沙盒+GPU(SFT ckpt已就绪=minicpm5-sft:8096) ③Phase1基线评测待沙盒 ④P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(89th wake,ICMP OK ALL TCP filtered,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;P3等pretrain ckpt
- 本轮新增产出: R284✅(SFT训练COMPLETE[70/70 loss 2.12→0.618 val 0.673 rc=0]+训练动力学分析[per-epoch mean E1=1.354/E2=0.836/E3=0.692/E4=0.654 -51.7% loss floor~0.6]+serve脚本修复[3处]+SFT ckpt served[GPU6:8096 minicpm5-sft smoke test PASS]+GPU5/6/7全占位+4 ckpt落盘[step20/40/60/70])
- 未完成指令: 🔴用户令17:10(serve占位)GPU5✅/GPU6✅(SFT serve)/GPU7✅(base serve)全占位;🔴用户令13:40(三阶段替身计划)Phase2 SFT COMPLETE✅+ckpt served✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake284 本轮提交R284(SFT训练COMPLETE+训练动力学分析+serve脚本修复+SFT ckpt served+smoke test+EXPERIMENTS §R284+MEMORY heartbeat+daily-memories)



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
[wake281 00:15] R281 全链路就绪审计20项(A1-A20)+本地沙盒排除(pyAether未装.17)+沙盒86th wake CLOSED+serve 5端点OK+git synced: 体积自检(MEMORY≈21KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang~45GB/4-7 vLLM~38GB各,全0%util)→serve健康5端点✅(8095-8099)→serve sentinel --check-once✅(All 5 UP action=none)→沙盒86th wake仍CLOSED(5 ports 8664/8665/8653/8669/8667全TCP timeout,poll#570)→sandbox watcher运行中(PID 4109314 --watch --auto-eval,log /tmp/posttrain_sandbox_watcher.log)→①R281 全链路就绪审计20项✅:A1 serve5端点curl全UP/A2 sentinel check-once All 5 UP/A3 sandbox 5 ports全CLOSED/A4 watcher PID 4109314 poll#570/A5 sentinel flag不存在(正确)/A6 dataset 689461B/A7 driver 29415B/A8 scorer 39781B/A9 eval --dry-run exit0/A10 phase1 --dry-run preflight全OK除sandbox BLOCKED/A11 SFT ckpt global_step_72 715MB safetensors✅/A12 v11-v36 parquet 270727B 1029rows✅/A13 pipeline --status Phase1+2 report✅ Phase3 SFT ckpt ready Gate sandbox FAIL/A14 cline ~/.bun/bin/cline✅/A15 MCP localhost:18888 SSE响应✅/A16 pyAether import→ModuleNotFoundError❌/A17 .env SANDBOX_HOST=10.129.32.75 SANDBOX_ENDPOINTS=8664/8665/8653/8669/A18 vLLM venv transformers 4.49.0✅/A19 GPU 0-3 root~45GB 4-7 vLLM~38GB/A20 Nov10 eval traces 12dirs 1task failed 无final_report ②本地沙盒排除✅:Phase1 dry-run提示unlock-B(any host H with pyAether)→.venv/bin/python -c 'import pyAether'→ModuleNotFoundError→pyAether是华大九天商业EDA Python+SWIG绑定未装.17→本地起沙盒不可行→唯一解锁=网络团队开10.129.32.75 ACL ③Nov10 eval traces不足:~/eda_code_eval/2026_1110_*/12 dirs全部1 task failed(sandbox down 16s exit1)无final_report.json api_conversation_history仅有task-001初始对话→不足D1-D6实测分析 ④归档wake279 heartbeat→daily-memories-posttrain/2026-11-12.md 📦 MEMORY≈20KB。本轮新增产出：R281✅(全链路就绪审计20项[A1-A20 serve/eval/dry-run/SFT ckpt/parquet/pipeline/cline/MCP全✅]+本地沙盒排除[pyAether ModuleNotFoundError→.17无商业EDA→唯一解锁=网络ACL]+Nov10 traces不足判定+EXPERIMENTS §R281)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake282 00:40] R282 v11-v36 SFT重训启动GPU6/7+NCCL_P2P_DISABLE修复FSDP2挂起+sandbox 87th wake CLOSED+git synced: 体积自检(MEMORY≈21KB合规)→git:pull --rebase✅up to date→GPU:0-3 root SGLang~45GB/4 vLLM~38GB/5 vLLM~38GB/6-7空闲→①teardown GPU6/7 serve✅:kill vLLM port8096/8095→GPU6/7 freed(3MiB each)→GPU5 serve(8097)保留占位 ②首次SFT launch挂起:NCCL_P2P_DISABLE未设→FSDP2挂step0/14>6min→GPU6 idle(0%)/GPU7 100%→非对称NCCL P2P死锁(prior vLLM serve残留CUDA context) ③NCCL P2P fix✅:NCCL_P2P_DISABLE=1→smoke test step1 loss=2.123@23.63s/it→两卡均100% util(GPU6=23977MB/GPU7=23626MB)→kill smoke→relaunch full ④v11-v36 SFT重训RUNNING:verl FSDP2 GPU6/7/70steps(14/epoch×5)/lr1e-5 cosine/ft_mode full/batch64/step2 loss=2.143@22.67s/it/ETA~28min/log /tmp/baize_posttrain_sft_v11v36_full.log/输出 sft_surrogate_runs/minicpm5_pyaether_v2_v11v36/ ⑤sandbox 87th wake仍CLOSED(poll#580,ICMP ping 0.4ms OK但22/80/443/8653/8664-8670全TCP filtered→子网ACL) 📦 MEMORY≈23KB。本轮新增产出：R282✅(v11-v36 SFT重训启动[teardown serve→NCCL_P2P_DISABLE=1 fix→smoke验证→full launch]+NCCL P2P诊断[GPU6 idle/GPU7 100%=P2P stale→NCCL_P2P_DISABLE=1]+sandbox ICMP-vs-TCP确认+EXPERIMENTS §R282)。未完成指令：🔴17:10 GPU5占位✅/GPU6-7转训练(更优);🔴13:40 Phase2 v11-v36重训RUNNING/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。
[wake283 00:51] R283 SFT训练监控step27/70+ckpt global_step_20 validated+post-SFT serve dry-run确认+sandbox 88th wake CLOSED+git synced: 体积自检(MEMORY≈32KB→归档wake280 heartbeat腾位)→git:pull --rebase✅up to date→GPU:0-3 root SGLang~45GB/4 vLLM~38GB/5 vLLM~38GB/6-7 SFT训练(99/96% util,28.7/28.4GB)→①SFT训练监控✅:step27/70(Epoch2/5 step13/14),loss轨迹2.123→1.671→1.157→0.938(E1)→0.819→0.728(E2),健康下降,@~22s/it,ETA~01:09,ckpt save_freq=20(global_step_20已存) ②global_step_20 ckpt完整性✅:715MB,2×safetensors(4.5G+0.53G)+config.json+generation_config+tokenizer_config+tokenizer.json+special_tokens_map+model.safetensors.index.json全齐→HF格式可直接vLLM serve ③post-SFT serve dry-run确认✅:baize_posttrain_sft_surrogate_serve.sh --dry-run --ckpt .../global_step_20 --gpu6 --port8096→recipe打印(ckpt4.7G/GPU6/8096/minicpm5-sft/mem0.85/maxlen32768/vLLM venv/transformers4.49.0)→script正确检测GPU6训练进程PID 341824/341825并warn"wait for it to finish"→eval下一步提示sandbox BLOCKED→替身预演声明 ④sandbox 88th wake仍CLOSED(poll#590,ICMP 0.28ms OK但8653/8664/8665/8669/8667/22/80/443全TCP filtered) ⑤serve健康3端点✅(8097/8098/8099 UP,8095/8096 down=GPU6/7训练中,正确) 📦 MEMORY≈30KB(归档wake280后)。本轮新增产出：R283✅(SFT训练监控[step27/70 loss 2.12→0.73]+ckpt完整性验证[global_step_20 715MB HF格式完整]+post-SFT serve dry-run确认[recipe valid+训练进程检测正确]+EXPERIMENTS §R283)。未完成指令：🔴17:10 GPU5占位✅/GPU6-7训练中;🔴13:40 Phase2 v11-v36重训RUNNING/Phase1待沙盒ACL/Phase3 RL待沙盒+GPU ⇒ WAITING=0。

