# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-16（⚡ **ArmA 效率专项：先修分片不均与数据管线 · 🚫 不改配方**）· 用户直令 · 最高优先

> **用户令（2026-10-16）**：「vision 是否有提升效率的机会点？现在 GBS / MBS / 梯度累积分别是多少，其他超参数呢？」

> **运维实测（源：`vision/armA_openclip_train.py` + `vision/run_armA_openclip.sh`）+ 机上涨卡实测（RUN_ID 109）**：
> - **批形状**：**MBS = 256 图/卡 × 8 卡 = GBS 2048；梯度累积 = 1**（每 step 一次 fwd/bwd/opt，无 accum；`armA_openclip_train.py:178-199`）。
> - **其它超参**：LR **2e-3 → 2e-4**（cosine，warmup **8000**）、steps **154500**（≈2.7ep/118M 对）、wd **0.1**、β **(0.9, 0.98)**、eps 1e-8、grad-clip **1.0**、**bf16**、`num_workers=6`、save every 10000、log every 20、seed 1234；`ClipLoss(local_loss=False, gather_with_grad=False, cache_labels=True)`；DDP `find_unused_parameters=False`。
> - **实测瓶颈证据**：显存**仅 24.4GB / 80GB**，而 8 卡 **util = 100/100/59/0/92/2/6/26%（严重不均）** ⇒ **典型 straggler：多数卡在等数据**（不是算力不够、更不是显存不够）。

**① 最高优先 —— 修分片不均**：`parse_shards()` 用 `all_shards[rank::world_size]`（`armA_openclip_train.py:59-73`）对**排序后**的 tar 列表做轮询切分 ⇒ 各 rank 拿到的**样本数/字节数不均衡**（webdataset tar 大小不一）。改为**按文件字节数装箱均衡**分配，或改用 `--data-source wds` 的 `split_by_node/split_by_worker`。**验收：8 卡 util ≥85% 且卡间方差显著变小。**
**② 数据管线**：`num_workers` **6 → 12~16**，并加 `persistent_workers=True` + `prefetch_factor=4~8` + `pin_memory=True`（H2D 已 `non_blocking=True`）。
**③ 白送项**：`torch.backends.cudnn.benchmark=True`（输入固定 224×224）；AdamW 加 `fused=True`；`precision='bf16'`（模型转 bf16）与外层 `autocast(bf16)` **二者留一**（现在双份，冗余）。
**④ 可选**：`torch.compile(model)`（ViT-B 常 +10~25%，需验 DDP+autocast 兼容）。
**⑤ 🚫 不改配方**：**GBS=2048 / MBS=256 / 累积=1 / LR 曲线一律不动**（否则与 ArmC、④-4ep 口径不可比）。若确要提 MBS（显存有 55GB 余量），**必须同步加梯度累积以保持 GBS=2048**，且需先回报再动。
**⑥ 交付**：修前/修后 **it/s + 8 卡 util + 新 ETA** 对比表 → `MEMORY_VISION.md` + `daily-memories-vision/`；commit 前缀 `vision armA perf:`。
**⑦ ⚠️ 体积**：任务书**已超 32KB** ⇒ **本轮须把已闭合块（10-16 三个评测块）原文归档进 `ARCHIVE_OPERATOR_VISION.md` 并压回 ≤32KB**。


### 🆕 运维指令 · 2026-10-16（📄 写 Stage(iv) 训练+12集评测报告 → 🚀 启动 ArmA open_clip 从头训 encoder）· 用户直令 · 最高优先

> **用户令（2026-10-16）**：「vision：把上一件工作，包括训练、12 集 lmms-eval 评测，写成中文 html 报告；然后启动 vision ArmA（open_clip 从头训 encoder）。」

**① 写报告（先做，纯写作零 GPU）**：
- 覆盖 Stage(iv) MLLM 全链路：Stage-1/1.5/2 训练（loss / 步数 / ckpt）+ Part A/B 验收（open_clip 协议 + LLaVA-OV 兼容导出）+ **12 集 lmms-eval 评测结果**（ai2d 60.04% · realworldqa 43.01% · mmmu 42.89% · blink 38.52% · mmstar 26.81% · mmmu_pro 23.12% · infovqa 16.58% · chartqa 12.24% · countbench 10.79% · docvqa 7.41% · ocrbench 1.1% · mme 596.7+250.7，来源 `consolidated_12benchmarks.json`）。
- 中文自包含 HTML：`reports/report_vision_stage4_mllm_result_zh.html`。

**② 启动 ArmA（open_clip 从头训 encoder）**：
- 用 **open_clip 协议/框架从头训练** vision encoder（🚫 不是自研 `vision/models.py` 框架），训完能被 `open_clip.create_model_and_transforms` 加载 + 直接走 open_clip/lmms-eval 评测，消除「自研架构不兼容 open_clip → 评测卡壳」的坑。
- 配置方向：open_clip 标准 ViT（推荐 **ViT-B/16 224px，86M，比自研 126.8M 更快**）+ 从头对比学习；数据复用现有图文对（GPIC/CC12M/Amshaker）；**主判据 ProtB**，对齐 ④-4ep 口径。
- 起训前回报「架构/规模 + 数据量 + 步数 + LR + ETA」；`.12` 8×H100 已空，直接起训。

**③ 纪律**：ArmA 起训前 `nvidia-smi` 确认空窗；🚫 与 data 下载错峰 IO；commit 前缀 `vision report:` / `vision armA:` · 任务书 >32KB 自滚归档。

> 📦 §运维指令 · 2026-10-16（📋 评测集缩编为 12 集）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 12/12 benchmarks 全量评测完成。需要时再读。

> 📦 §运维指令 · 2026-10-16（🔧 评测按「每卡一个 benchmark」重排）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ per-GPU eval 方案落地，13 集全量评测完成。需要时再读。

> 📦 §运维指令 · 2026-10-16（⚡ 停 batch_size=4 评测 · 加大 batch）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ batch_size 升至 32，GPU util 抬起。需要时再读。

> 📦 §运维指令 · 2026-10-16（🚀 评测直跑全量 + ArmA 转 open_clip）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 全量评测完成；ArmA 方向确认 open_clip 标准 encoder（自研 ViT 判定失败），训练已启动。需要时再读。

### 🆕 运维指令 · 2026-10-15 22:25（♻️ **别重下：先复用旧缓存** + 🧩 **ArmA 重训须实现 open_clip 协议 / LLaVA-OneVision 兼容**）· 用户直令 · 最高优先

**A. 立刻做 —— 复用旧缓存（实测省 ~20G 下载 ≈ 1 小时）**
- **实测事实**（运维 RUN_ID 105）：旧缓存 `/home/app.e0031982/.cache/huggingface/` 里**已有 6 个 lmms-lab 基准**：
  - `hub/datasets--lmms-lab--{ai2d, GQA, MMBench, MMMU, textvqa}`（约 20G 量级）
  - `datasets/lmms-lab___{ai2d, gqa, mm_bench, mmmu, real_world_qa, textvqa}`
  - （都是今天 18:27–20:48 那次**失败评测**下下来的）
- 而现在 `precache_benchmarks.py` 在新 `HF_HOME=/nas_env/...` **从零重下 GQA 等** ⇒ **白下**。
- **做法（停 → 本地拷贝 → 续跑）**：
  ```bash
  pkill -f precache_benchmarks.py; sleep 2
  cp -a "$HOME"/.cache/huggingface/hub/datasets--lmms-lab--{ai2d,GQA,MMBench,MMMU,textvqa} /nas_env/app.e0031982/hf_home/hub/
  cp -a "$HOME"/.cache/huggingface/datasets/lmms-lab___* /nas_env/app.e0031982/hf_home/datasets/
  ls -d /nas_env/app.e0031982/hf_home/hub/datasets--lmms-lab--* /nas_env/app.e0031982/hf_home/datasets/lmms-lab___*   # 核对 6 个都在
  ```
  ⚠️ 必须 `cp -a`（`/home`→`/nas_env` 跨文件系统，**不能硬链**）；🚫 **不要**把 `hub`/`datasets` 软链回 `/home`（那等于把写入引回只有 47G 余量的 `/home`，必再撑满）。
- 续跑前 `df -h /nas_env` 核余量；🚫 不要重复下载已拷过来的那 6 个。
- ⚠️ 另注：`/tmp/lmms_eval_hf_datasets_app.t0002965` 是**空的**，`/nas_train/app.e0031982/.cache/huggingface` 只有 `hub/xet`（非基准）⇒ 别处没有存量可挖；**其余 11 集（DocVQA / ChartQA / ScienceQA / SEED-Bench / POPE / VizWiz / OCRBench / MMVet / HallusionBench / VQAv2 / InfoVQA）确实从未下过**，仍要走下载。

**B. ArmA 重训（今晚评测完开工）—— open_clip 协议 + LLaVA-OneVision 兼容（用户直令）**
- **必做 ① `open_clip` 协议**：`open_clip.create_model_and_transforms('<name>', pretrained=<ckpt>)` 能加载；`encode_image(x)` / 前向返回 `[B, N, D]`（N = patch 数；**明文声明是否含 CLS / 是否 spatial-merge**）；暴露 `vision_config`（`image_size / patch_size / hidden_size / depth / width`）；预处理与现有 224 管线一致。
- **必做 ② LLaVA-OV 兼容导出**：产出可被 OV 流程消费的 HF 目录 —— `config.json`（`model_type` + `vision_config`（clip/open_clip 系）+ `text_config`（Qwen3）+ **`image_token_index`** + **`vision_feature_select_strategy`**）、`preprocessor_config.json`（image processor）、chat template。
- **验收（必须给证据）**：① `open_clip` 加载成功 + 一次前向的 shape/数值 sanity；② 该目录能被 `AutoConfig` / `AutoProcessor` 正常读；③ 用它跑 **`ai2d --limit 5`** 得到非 0 准确率（证明端到端通）。
- **先定口径并在回报里写明**（这三项决定与官方 OV 的可比性）：① **分辨率**：**224 单块（推荐先跑通）** 还是 **384 + anyres**；② `image_token_index` 取值；③ 视觉特征取**哪一层**（官方 OV = SigLIP 倒数第二层）。
- 🚫 **纪律**：报告里**必须标注与官方 LLaVA-OV 的 pipeline 差异**；**未做到 anyres 同构前，不得宣称与官方 LLaVA-OV 数字同框**。

> 📦 §运维指令 · 2026-10-15 20:0x（🔬 评测实况核查结论 + 7 项待办）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 全部 7 项已处置（提速/小样/数据/git/Stage-2/耗时归因/git push）。📌 口径：连 github 用 92.23；下 HF 数据用 92.25 直连 hf.co。需要时再读。

> 📦 §运维指令 · 2026-10-15 21:35（🔧 limit50 崩因=磁盘满 → 换盘+预建缓存+复跑）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ HF_HOME 已迁 /nas_env(9.9T)，precache_benchmarks.py 单进程预建缓存运行中(8/17 done)，磁盘检查已加入 launcher。需要时再读。

> 📦 §运维指令 · 2026-10-15（⚡ lmms-eval 提速：17 集一次跑+大 batch+多 GPU）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ run_lmms_eval.py 已实现 17 集一次命令行+batch_size 可调+8卡 multi-GPU。需要时再读。

> 📦 §运维指令 · 2026-10-15（🔧 proxy 纠正：直连 hf.co · 恢复 17 benchmark）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ hf-mirror 已移除，proxy 92.25 直连已验证，17 集评测恢复，Stage-1.5/2 已完成。需要时再读。

### 🆕 运维指令 · 2026-10-15（📚 历史实验结果全景总结 · 中文 HTML）· 用户直令

> 📦 §运维指令 · 2026-10-15（📚 历史实验结果全景总结）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ report_vision_experiments_summary_zh.html 48.5KB 交付，8 主题全覆盖。需要时再读。

> 📦 §运维指令 · 2026-10-15（🚀 放行执行 Stage(iv) MLLM 完整流程）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ Stage-1(2500步)+Stage-1.5(20000步)+Stage-2(3500步,loss=1.4853) 全部完成。lmms-eval 评测进行中(precache 8/17)。需要时再读。

### 🆕 运维指令 · 2026-10-14（🔧【放行并行】ArmC 期间先写 BaiZe ViT → HF wrapper + 自定义 LLaVA modeling（纯 CPU，不占 GPU））· 用户直令 · 最高优先（但仍低于 ArmC 训练/评测监控）

> 📦 §运维指令 · 2026-10-14（🔧 ArmC 期间先写 ViT wrapper）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ mllm_bridge/ 全套 7 文件 + 报告 20.6KB, CPU 5/5 PASSED, commit 03c36f5f。需要时再读。


> 📦 §运维指令 · 2026-10-14（📋 Stage(iv) MLLM 可行性评估）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 交付 28.5KB 中文 HTML（9节），2🔴+6🟠+7🟢，3 Stage 数据265GB全在盘，wrapper/modeling 开发纯 CPU 可并行。需要时再读。

> 📦 §运维指令 · 2026-10-14（📊 ArmC 中文状态报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ report_vision_merge3ds_armc_status_zh.html 已交付(7节+2SVG+文献表)，已多次刷新至最新训练数据。需要时再读。

> 📦 §运维指令 · 2026-10-14（✍️ 放行刷新论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ P0+P1 全部修改完成，11→12 页 0 error（commit e0f75ef5）。需要时再读。

> 📦 §运维指令 · 2026-10-14（📝 训练空窗期审视论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 交付 21.8KB HTML，2🔴+6🟠+5🟢，14/16 核验一致。需要时再读。

> 📦 §运维指令 · 2026-10-13（📐 LR 缩放规则）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 按文献定 LR ×4=2e-3（Goyal arXiv:1706.02677），3 臂扫描，报告已更新含文献表。需要时再读。

> 📦 §运维指令 · 2026-10-13（🔢 数据量口径更正）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ GPIC 快照7437tar≈94M/全量101.1M, 三集合计快照≈111M/全量118.1M, 报告已订正。需要时再读。


### 🆕 运维指令 · 2026-10-13（🚀【放行执行】外部编码器 ProtB 做完后 → 立刻跑「合并三数据集实验」：GBS/MBS ×4 · LR ×2 · 24h ≈3 epoch）· 用户直令 · 最高优先

> 📦 §运维指令 · 2026-10-13（🚀 合并三数据集实验）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ ArmC 训练完成(154500步) + eval 4/4 全提升(ProtB 68.25% Δ+1.20pp)，报告交付。需要时再读。


> 📦 §运维指令 · 2026-10-13（📄 合并三数据集实验计划 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_merge3ds_bs4_lr2_plan_zh.html（44.3KB）已交付，含 3 臂 LR 扫描 + 数据量订正 + 文献表。需要时再读。

> 📦 §运维指令 · 2026-10-13（🔬 外部编码器 ProtB 评测）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：5/5 完成（SigLIP2 87.46% / AIMv2 85.22% / OV2 84.97% / CLIP 82.66% / RICE 81.72%），report_vision_external_protb_reference_zh.html 已交付。需要时再读。
---

> 📦 §运维指令 · 2026-10-13（📄 ④-4ep 实验报告中文 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_4ep_experiment_zh.html 已交付，ProtB=67.05% MODERATE/DIMINISHING，含 MBS/GBS/LR 加速分析 + N-epoch 时间表。需要时再读。

> 📦 §运维指令 · 2026-10-11（📄 外部反馈→审视+合入论文：Muon 梯度谱解释）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：VISION_MUON_REVIEW_2026-10-11.md + paper §VI-D Muon paragraph + bib entry (arXiv:2605.19282) delivered, 11→11 pages 0err, commit 95a94d0f。需要时再读。

---

> 📦 §运维指令 · 2026-10-11（📄 Muon 坍缩根因分析报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_muon_collapse.html（33.6KB, 10节, 内联SVG）已交付，commit 6743baeb。需要时再读。

> 📦 §运维指令 · 2026-10-11（📚 文献借鉴报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lit_ideas.html（28.4KB, 25篇→TOP-5）已交付，commit 6743baeb。需要时再读。

> 📦 §运维指令 · 2026-10-12（📄 LLaVA-OV1.5 复现计划）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_llava_ov15_repro_plan.html 已交付，含 Qwen3.5-4B+OV2视觉塔+ms-swift框架+S0-S4五阶段。需要时再读。

> 📦 §运维指令 · 2026-10-12（🚀 启动 ④-4ep 续训）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：④-4ep 训练+评测全完成，ProtB=67.05±0.02%，MODERATE/DIMINISHING（<70%未达标）。需要时再读。

> 📦 §运维指令 · 2026-10-12（📄 中文版综合报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_final_20261012_zh.html 已交付，外部评审回应全链路收口。需要时再读。

> 📦 §运维指令 · 2026-10-10（🧭 外部评审回应 ③→①→②→④）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：③口径✅ ①zs✅ ②probe✅ ④2ep✅（MODERATE Δ+3.03pp）→ 全链路 DONE（10-12 13:42 收尾）。需要时再读。

> 📦 §运维指令 · 2026-10-10（🧪 变体实验：AdamW→Muon → 全量数据 → 分辨率暂缓）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：V2 Muon 全 LR 坍缩❌（lr=5e-4@step2100, lr=1e-4@step4200）；V3 全量数据 ProtB=63.52% Δ+1.18pp 不可分辨；V1 分辨率暂缓。报告 `report_vision_variants_20261011.html` 已交付。需要时再读。

> 📦 §运维征询 · 2026-10-10（下一步工作建议）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：已回答 → MEMORY_VISION.md「运维问答 · 2026-10-10」节。建议含 Stage(iv) MLLM 对齐、w384、C1-lp trade-off、336 分辨率、论文呈现等。需要时再读。

> 📦 §运维指令 · 2026-10-10（📄 Scaling fair rerun 成果报告 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：`report_vision_scaling_fair.html`（36.7KB）已交付，Δlp=+0.17pp 不可分辨，⛔ 横幅已加。需要时再读。

> 📦 §运维指令 · 2026-10-10（📄 昨夜工作汇报 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：`report_10_09_vision_overnight.html`（61.9KB）已交付，含 E1fair/E2fair 全程+最终 Δlp=+0.17pp。需要时再读。
> 📦 历史运维指令已归档 → `run/ARCHIVE_OPERATOR_VISION.md`（已执行完 / 已作废的块；需要时再读，不要读进上下文）。

> 本节由外部运维通过 git 修改。agent 禁止修改本节（只写 `MEMORY_VISION.md` / `EXPERIMENTS_VISION*` / `daily-memories-vision/` / `vision/`）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_VISION.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。

---

> 📦 §运维指令 · 2026-10-09⑨（🔁 公平性重跑）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：E1fair(62.34±0.01%) vs E2fair(62.51%)，Δlp=+0.17pp 不可分辨；旧「Bigger is WORSE −5.59pp」= schedule 伪影；`r9_train.py` cosine/min-lr 已加；两臂同一冻结快照 total_shards=10787。需要时再读。

---

> 📦 2026-10-08⑥（E2 变更：作废官方 OV2 L/14@336 → w768/d30）已归档 → `ARCHIVE_OPERATOR_VISION.md`。结论：E2(w768/d30,284.54M) 已跑完+eval；配方公平性已被 2026-10-09⑨ 定性问题。需要时再读。


> 📦 2026-10-08⑤（缩放对比实验）已归档 → `ARCHIVE_OPERATOR_VISION.md`。结论：E1(w512) vs E2(w768/d30) Δlp=−5.59pp，但建立在 `--lr 3e-3 --warmup 20`（warmup≈0%）上 ⇒ 公平性存疑，结论已作废 → 见 2026-10-09⑨ 公平重跑。需要时再读。


> 📦 §运维指令 · 2026-10-08④（📐 全量 1-epoch 耗时估算）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：已用 scaling smoke 实测回答（E1=4697 img/s → 5.66h；区间 5.2–9.1h/epoch；1 epoch 足够）。需要时再读。


### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）


- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
