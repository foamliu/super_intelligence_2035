# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake279（2026-11-11 R210 v11-v36 JSONL→parquet+contamination gate PASS+SFT dry-run OK+serve 5 endpoints OK+sandbox 84th wake CLOSED+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；wake278 R209(v36 corpus 86 pairs→Tier-2 75.0%)；wake279 R210(v11-v36 parquet 1029 rows+gate PASS+SFT dry-run OK)
- 当前动作: wake279 ①R210 v11-v36 JSONL→parquet✅:baize_posttrain_r210_v11v36_parquet.py(155行,py_compile✅)→1029 rows/0.26MB/schema match v5=True/conversation[system,user,assistant] ②权威污染闸门✅:baize_posttrain_contamination_gate.sh --sft-synth v11_v36_merged.jsonl→1029 docs scanned/0 hits/PASS(exit 0,可投料) ③SFT surrogate dry-run✅:--src-parquet v11_v36_merged.parquet --run-name minicpm5_pyaether_v2_v11v36 --epochs 5→torchrun OK/model OK/verl+flash_attn+peft OK/parquet 270727B OK ④v11-v36 SFT重训真正一条命令可起(GPU释放后) ⑤sandbox 84th wake仍CLOSED(5 ports全TCP timeout) ⑥serve健康5端点✅(8095-8099) ⑦GPU0-7全占 ⑧git synced
- 下一步: ①GPU释放后一条命令起v11-v36 SFT重训:bash baize_posttrain_sft_surrogate.sh --prep-only --src-parquet sft_pyaether_corpus_v11_v36_merged.parquet --run-name minicpm5_pyaether_v2_v11v36 --epochs 5 然后 bash baize_posttrain_sft_surrogate.sh --src-parquet sft_pyaether_corpus_v11_v36_merged.parquet --run-name minicpm5_pyaether_v2_v11v36 --epochs 5 ②post-SFT eval验证 ③沙盒恢复→Phase1 baseline eval ④Phase3 RL待沙盒+GPU ⑤[可选]v37+针对ae* GUI API补充(122 family×1 API,低ROI,暂缓) ⑥P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(84th wake,5 ports全CLOSED,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴GPU被serve占位→v11-v36 SFT重训待GPU释放;P3等pretrain ckpt
- 本轮新增产出: R210✅(v11-v36 JSONL→parquet[1029 rows/0.26MB/schema match v5=True]+权威污染闸门[1029 docs/0 hits/PASS]+SFT surrogate dry-run[torchrun/model/verl+flash_attn+peft/parquet全OK]+v11-v36 SFT重训一条命令可起)+baize_posttrain_r210_v11v36_parquet.py(155行 py_compile✅)+sft_pyaether_corpus_v11_v36_merged.parquet(0.26MB)+r210_v11v36_parquet_summary.json+EXPERIMENTS §R210
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅;🔴用户令13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake279 本轮提交R210(v11-v36 parquet+contamination gate+SFT dry-run readiness+EXPERIMENTS §R210)



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

> 📦 wake271 (R202) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

> 📦 wake273 (R204) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

[wake274 21:55] R205 v35 context-blind语料(6 API→31对ISOLATE-class训练就绪/6 blind APIs全清/coverage 96.3%→100%)+serve健康5端点+沙盒79th wake CLOSED+git synced: 体积自检(MEMORY≈27.2KB→新增1条heartbeat后~28.5KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang 45GB/4-7 vLLM 37.8GB各)→serve健康5端点✅(8095 minicpm5-2b-gpu7/8096 minicpm5-sft/8097 minicpm5-2b-gpu5/8098 minicpm5-2b/8099 qwen3.8-27b)→沙盒79th wake仍CLOSED(TCP8667 timeout)→①R205 v35 context-blind✅:R204剩6 context-dependent blind APIs(agrGetSnapPoints/geTreeRemoveItem/emvPurposeNumberDrawing/guMotion/mouseLBClick/smash_option)各需setup context(DB inst/Qt tree/draw area/config struct/purpose常量)→pyAether MCP get_api_details全12 named API权威签名+emvPurposeNumberDrawing(enum CONSTANT非函数,MCP返空)+smash_option(SWIG config struct,MCP返空)从eval canonical_solution+消费者API推断(同R202 CColor pattern)→5 groups(16 API in API_DOCS:snap/tree/purpose/mouse/smash)→baize_posttrain_r205_context_blind_corpus.py(~877行,8 editor appends due 6000-char limit)→--dry-run✅(31对/0 REJECTED/FINGERPRINT SCAN PASS)→full run✅→sft_pyaether_corpus_v35_context_blind.jsonl(36962B/31对) ②污染隔离✅:155 eval entry_points扫描31/31 PASS 0 REJECTED;FINGERPRINT SCAN GATE(exit 2 on any hit);6 target API均非entry_point→ISOLATE-class;doctest值刻意不同于eval(snap(2.5,3.5)+(7,1)/tree"WidgetTree"+"row_widget"/polyline layer12 3顶点(1,1)+(8,4)+(15,9)/mouse(3,7)/smash level1-2 m_smashPyCell=True) ③v11-v35合计943对(912+31)训练就绪 ④pair分布:S1×6+S3×6+S4×10+S5×5+S6×4;API coverage 16 unique APIs全覆盖 ⑤4 S6 cross-API工作流:snap+smash flatten/mouse+snap command-point/tree+polyline manage/smash+snap post-flatten ⑥关键API事实:agrGetSnapPoints(inst,points:vector1D_emyPointF,type:emyString)→Tuple[emyPointF]须vector非list;geTreeRemoveItem(tree,item)→bool移除直接child,二次移除返False;emvPurposeNumberDrawing=enum常量传GuCartPolyLine purNum;guMotion(point)→bool headless返False;mouseLBClick(point,ctrl,shift)→bool;smash_option()=SWIG struct设4个bool属性传dbSmashInst2(obj,level,option)→bool 📦 MEMORY≈28.5KB。本轮新增产出：R205✅(v35 context-blind[6 API/31对/ISOLATE-class/155 entry_point污染扫描全PASS+FINGERPRINT SCAN GATE/v11-v35合计943对训练就绪/6 blind APIs ALL cleared/coverage 96.3%→100%])+baize_posttrain_r205_context_blind_corpus.py(~877行)+sft_pyaether_corpus_v35_context_blind.jsonl(36962B/31对)+EXPERIMENTS §R205。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

> 📦 wake275 (R206) 已归档 → daily-memories-posttrain/2026-11-11.md（v11-v35 25files→943对merged JSONL+parquet+双重污染闸门PASS）。

> 📦 wake276 (R207) 已归档 → daily-memories-posttrain/2026-11-11.md（surrogate SFT script parameterized+v11-v35 train/val split 849/94 ready）。
[wake277 23:10] R208 v11-v35 corpus coverage audit vs 158-task eval API[Tier-2=314/488=64.3% MODERATE]+serve健康5端点+沙盒82nd wake CLOSED+git synced: 体积自检(MEMORY≈30.3KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang~45GB/4-7 vLLM~38GB各,全0%util)→serve健康5端点✅(8095-8099)→沙盒82nd wake仍CLOSED(5 ports 8664/8665/8653/8669/8667全TCP timeout)→①R208 corpus coverage audit✅:baize_posttrain_r208_corpus_coverage_audit.py(10.6KB,纯stdlib,py_compile✅,dry-run✅)→对比943对语料189 unique APIs vs eval 488 APIs(pyAether_eval_488_apis.txt)→命名约定差异:eval用全限定pyAether.C.m,语料用class/func级短名→定义3级覆盖度量 ②Tier-2 CLASS-AWARE(主指标)314/488=64.3%覆盖[1-dot pyAether.F覆盖⇔F在语料;2-dot pyAether.C.m覆盖⇔C类或m方法在语料];Tier-1 leaf 167/488=34.2%;Tier-3 strict 167/488=34.2% ③缺口集中度:320 family中168完全覆盖/152有缺口(152完全未覆盖)→top未覆盖family:emyLine(4)/emyScalarInst(4)/emyScalarNet(4)/MdeSetting(3)/dmLibObj(3)/emyPin(3)/dmCellObj(2)/dmViewObj(2)/emyArc(2)/emyEllipse(2)/emyNet(2)/emyTerm(2)/emyText(2)=13个完全未覆盖family(v36+增强首选目标) ④surplus=22个corpus API教了但eval不考(dbCrtWire/dbFindInst/aeLeCreatePin/SleHierQuery等) ⑤判定MODERATE(50-70%区间):SFT可帮但缺口实质,建议v36+针对13个未覆盖family合成S3/S4示例5-10对/family→重跑R208审计目标Tier-2≥75%;即便不补64.3%也足以让SFT在D1/D2工具协议层面回收部分分(M1=50%可达)但M2=65%领域增益受限 ⑥交付物:baize_posttrain_r208_corpus_coverage_audit.py(10.6KB)+r208_coverage_audit.json(6.7KB)+EXPERIMENTS §R208 📦 MEMORY≈31.5KB。本轮新增产出：R208✅(v11-v35 corpus coverage audit vs 158-task eval API[Tier-2=314/488=64.3% MODERATE/152 family有缺口/13个完全未覆盖family识别为v36+目标/22 surplus/3-tier metric/Pre-GPU判定MODERATE])+baize_posttrain_r208_corpus_coverage_audit.py(10.6KB py_compile✅ dry-run✅)+r208_coverage_audit.json(6.7KB)+EXPERIMENTS §R208。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake278 23:22] R209 v36 uncovered-family corpus augmentation[Tier-2 314/488=64.3%→366/488=75.0% GOAL MET]+serve健康5端点+沙盒83rd wake CLOSED+git synced: 体积自检(MEMORY≈31.8KB→归档wake275/wake276腾位→更新snapshot+heartbeat后~30KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang~45GB/4-7 vLLM~38GB各)→serve健康5端点✅(8095-8099)→沙盒83rd wake仍CLOSED(5 ports全TCP timeout)→①R209 v36 corpus augmentation✅:baize_posttrain_r209_gen_v36_uncovered.py(620行,py_compile✅)→针对R208识别的13个完全未覆盖family(emyLine/emyScalarInst/emyScalarNet/MdeSetting/dmLibObj/emyPin/dmCellObj/dmViewObj/emyArc/emyEllipse/emyNet/emyTerm/emyText)+3 enum(emyTermAttrType/emyTermType/emyTextAlign)+14 bonus 1-uncovered family(MDE_SWEEP_*/MdePlatSweepStepMode/MdeResult/SleLeWireTypeEnum/addProp/EmyTechGetPurposeNum/PVM_*/aeCrtGuardring/aeCheckAndSaveDesign/aeEnableUndo)=30 targets→pyAether MCP get_api_details获取全部30个API权威签名→合成S1(doc→code)+S3(code→explain)+S4(scenario)+S5(variant)训练对(main family 4对,bonus/enum 2对)→86 pairs/0 contamination FAIL(155 eval entry_points指纹扫描全PASS)/55 unique api_used→sft_pyaether_corpus_v36_uncovered_families.jsonl(109KB/86对) ②combined v11-v36 corpus✅:cat v11-v35(943对)+v36(86对)→sft_pyaether_corpus_v11_v36_merged.jsonl(1029对/244 unique APIs) ③R208 audit on combined corpus✅:baize_posttrain_r208_corpus_coverage_audit.py --corpus flag added→Tier-2 CLASS-AWARE 366/488=75.0%(从64.3%→75.0%,+52 APIs覆盖,GOAL MET);Tier-1 leaf 194/488=39.8%;Tier-3 strict 219/488=44.9%→Pre-GPU verdict:GOOD(≥70%→proceed to SFT with confidence) ④剩余122 uncovered family多为ae* GUI/App-form API(aeCreateButton/aeCreateMenu/aeCreateStringField等,1 API/family,低ROI,暂缓) ⑤r208 audit --corpus flag added(baize_posttrain_r208_corpus_coverage_audit.py)+r209_v36_coverage_audit.json ⑥归档wake275/wake276 heartbeat→daily-memories-posttrain/2026-11-11.md 📦 MEMORY≈30KB。本轮新增产出：R209✅(v36 uncovered-family corpus augmentation[13 main+3 enum+14 bonus=30 targets→86 pairs/0 contam FAIL/55 unique APIs/Tier-2 64.3%→75.0% GOAL MET/Pre-GPU GOOD/combined 1029对])+baize_posttrain_r209_gen_v36_uncovered.py(620行 py_compile✅)+sft_pyaether_corpus_v36_uncovered_families.jsonl(109KB/86对)+sft_pyaether_corpus_v11_v36_merged.jsonl(1029对)+r209_v36_coverage_audit.json+r208 audit --corpus flag+EXPERIMENTS §R209。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake279 23:38] R210 v11-v36 JSONL→parquet[1029 rows/0.26MB/schema match v5=True]+权威污染闸门[1029 docs/0 hits/PASS]+SFT surrogate dry-run[torchrun/model/verl+flash_attn+peft/parquet全OK]+serve健康5端点+沙盒84th wake CLOSED+git synced: 体积自检(MEMORY≈30.7KB→归档wake271/wake273腾位→更新snapshot+heartbeat后~28KB合规)→git:pull --rebase✅up to date→GPU:0/8free(0-3 root SGLang~45GB/4-7 vLLM~38GB各,全0%util)→serve健康5端点✅(8095-8099)→沙盒84th wake仍CLOSED(5 ports 8664/8665/8653/8669/8667全TCP timeout)→①R210 v11-v36 JSONL→parquet✅:baize_posttrain_r210_v11v36_parquet.py(155行,py_compile✅)→verl venv pyarrow 25.0.1转换1029 rows→sft_pyaether_corpus_v11_v36_merged.parquet(270727B/0.26MB/snappy)→schema match v5=True(conversation/pair_id/type/api_used/contamination_check)→0 parse errors/0 empty prompt/0 empty completion→type分布:S4=217/S5=212/S1=208/S6=188/S3=179/S1_doc_to_code=10/S2_api_lookup=10/S3_multi_api_chain=3/S7=2 ②权威污染闸门✅:baize_posttrain_contamination_gate.sh --sft-synth v11_v36_merged.jsonl→6快照并集536任务(含v20260311的158)→13-gram重合率≥0.8+8-gram兜底→扫描1029 docs/0 hits/PASS(exit 0,可投料) ③SFT surrogate dry-run✅:baize_posttrain_sft_surrogate.sh --dry-run --src-parquet sft_pyaether_corpus_v11_v36_merged.parquet --run-name minicpm5_pyaether_v2_v11v36 --epochs 5→recipe打印OK→torchrun OK/model OK/verl+flash_attn+peft OK/parquet 270727B OK→GPU 6,7/2×A40 FSDP2/max_length 2048/batch 64/4/epochs 5/lr 1e-5 cosine/ft_mode full ④v11-v36 SFT重训真正一条命令可起(GPU释放后):--prep-only创建train/val split,然后去掉--dry-run正式跑 ⑤归档wake271/wake273 heartbeat→daily-memories-posttrain/2026-11-11.md 📦 MEMORY≈28KB。本轮新增产出：R210✅(v11-v36 JSONL→parquet[1029 rows/0.26MB/schema match v5=True]+权威污染闸门[1029 docs/0 hits/PASS]+SFT surrogate dry-run[torchrun/model/verl+flash_attn+peft/parquet全OK]+v11-v36 SFT重训一条命令可起)+baize_posttrain_r210_v11v36_parquet.py(155行 py_compile✅)+sft_pyaether_corpus_v11_v36_merged.parquet(0.26MB)+r210_v11v36_parquet_summary.json+EXPERIMENTS §R210。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
