# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-15（🔧 proxy 纠正：直连 hf.co 下载 lmms-eval 基准 · 恢复 17 benchmark）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「如实使用 http://172.19.92.25:13128 这个 https_proxy，则需要直连 hf.co，不能用 https://hf-mirror.com。」

**① proxy 纠正**：
- 🚫 **去掉** `HF_ENDPOINT=https://hf-mirror.com`（及任何 hf-mirror 相关设置）。
- ✅ 设 `https_proxy=http://172.19.92.25:13128` + `http_proxy=http://172.19.92.25:13128`，**直连 hf.co** 下载 lmms-eval 17 benchmark 数据（此前用 mirror / 未带 proxy 导致「HF Hub 不可达」）。

**② 恢复 lmms-eval 评测**：
- 🚫 不要降级为「本地 instruct held-out」——用 proxy 直连 hf.co 下载 17 benchmark 数据，恢复原计划的 **lmms-eval 17 集评测**。

**③ Stage 推进（继续，勿停）**：
- Stage-1.5 已完成（step20000，ckpt `/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15/step20000/`）→ gate check 后启动 **Stage-2 instruct（~3500 步）** → lmms-eval 17 集。

**④ 纪律**：🚫 不打断 Stage 训练链；下载/评测一律带 proxy 直连 hf.co；commit 前缀 `vision mllm:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（📚 历史实验结果全景总结 · 中文 HTML）· 用户直令

> **用户令（2026-10-15）**：「vision 之前的实验结果如何，写成 html 中文报告。」

**性质**：纯写作、零 GPU。**主线仍是刚放行的 MLLM 训练**——本任务在 MLLM smoke/Stage 间空窗期做，🚫 不延迟 MLLM 训练。

**① 报告内容**：把 vision 线从架构选型到 merge3ds ArmC 的**全部关键实验结果**，按主题结构化整理成中文 HTML 报告。

**② 必须覆盖**（基于 `EXPERIMENTS_VISION.md` 台账，每主题给动机/关键数字/判定/后续影响）：
1. **架构选型（R2/R8）**：六架构四指标对比，OpenVision2 胜出（Loss@5k / img/s / 推理 ms/img）。
2. **缩放（R9/R10）**：「塔越小越高」，w512=126.8M 定位。
3. **AIMv2-style（R11）**：w512 翻盘、loss 轴主线。
4. **E1/E2 公平重跑**：Δlp **+0.17pp 不可分辨**，旧「−5.59pp」= schedule 伪影。
5. **epoch 缩放（④）**：1ep 62.34% / 2ep 65.37% / 4ep 67.05%（ProtB），递减收敛。
6. **变体**：V2 Muon 全 LR 坍缩、V3 全量数据 Null（Δ+1.18pp）。
7. **外部编码器 ProtB 参照**：5 模型 81.72~87.46 vs BaiZe 67.05。
8. **merge3ds ArmC**：GBS/MBS×4 + LR×4 结果（若 eval chain 已出）。

**③ 交付**：`reports/report_vision_experiments_summary_zh.html`（自包含中文、内联 CSS/SVG、可带 lp-epoch/scaling 曲线图）。

**④ 纪律**：数字全部与 `EXPERIMENTS_VISION.md` 一致、贴 §行号，🚫 凭印象；🚫 不延迟 MLLM 训练；commit 前缀 `vision report:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（🚀 放行执行 Stage(iv) MLLM 完整流程：smoke → Stage-1/1.5/2 → lmms-eval）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「vision 为什么停下来不做 MLLM？」—— 你**是被授权做的**（用户早已批「我同意，可以做」），wrapper 已就绪，8 GPU 已空，现在放行执行完整 Stage(iv)，不再停在 Phase0。

**① 前置已就绪（无需再确认）**：wrapper + 自定义 modeling + projector CPU 单测 **5/5 通过** ✅；**.12 8×H100 空闲** ✅；三个 Stage 数据 265GB 在盘 ✅；Qwen3-4B ✅；ms-swift 4.5.3 ✅；lmms-eval 0.7.1 ✅。

**② 执行顺序（按可行性报告 §8.3 排期 + §9.2 建议，方案 A）**：
1. **GPU smoke test**：加载 BaiZe wrapper + projector + Qwen3-4B，前向 1 batch（~1h）
2. **Stage-1 Alignment**：冻结 LLM + vision tower，只训 projector（~2500 步；LR 先 1e-4 基线，不收敛扫 {5e-5, 2e-4, 5e-4}）
3. **Stage-1.5 Mid-Training**：解冻 LLM（或 LoRA），~20000 步
4. **Stage-2 Instruct**：~3500 步
5. **lmms-eval 17 benchmarks**
- 超参参照 `train_4b.sh` 但**用 ms-swift**；`SEQ_LEN=32768` 若 OOM 降 8192/16384；Stage-1 固定 224、跳过 spatial merge、image-token 占位 196。

**③ 门控**：每 stage 完成上报一次（smoke 通过才进 Stage-1；Stage-1 通过才进 1.5，依此类推），各 stage 落 ckpt 到指定目录。

**④ 交付**：全程日志 + 各 stage ckpt + 17 benchmark 结果表 + 中文 HTML 报告（含 vs LLaVA-OV1.5 RICE ViT 基线对比，方案 B 对照）。

**⑤ 纪律**：开跑前 `nvidia-smi` 确认 .12 空窗；与 data 线下载错峰 IO；训练用 py310、评测用 ov_encoder（或 py310 装 lmms-eval）；🚫 不碰论文/其它线产物；commit 前缀 `vision mllm:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-14（🔧【放行并行】ArmC 期间先写 BaiZe ViT → HF wrapper + 自定义 LLaVA modeling（纯 CPU，不占 GPU））· 用户直令 · 最高优先（但仍低于 ArmC 训练/评测监控）

> **用户令（2026-10-14）**：「vision MLLM 桥接：**现在就在 ArmC 期间并行写 ViT wrapper**（纯 CPU 可并行）。」
> **背景**：可行性报告 `report_vision_mllm_stage4_feasibility_zh.html` §4.3/§7 已判定「视觉编码器桥接」= 🔴 R1 最大工程量（~1-2 天工程），且 §8.2/§8.3 明确 #3#4 为**纯 CPU 工作、可在 ArmC 训练期间并行完成、不占 GPU**。本令 = 批准 Phase0 并行开工（覆盖报告中 #3#4「未开始」状态）。

**① 先决纪律（不可越线）**：
- 🚫 **不打断/不延迟 ArmC 训练与 eval chain**（training PID + eval chain PID 3698490）；本任务**零 GPU**（仅 CPU 前向做 shape/数值单测）。
- 🚫 不改 ArmC 训练脚本/数据/ckpt；不改已发布报告数字。
- ⚠️ 若 CPU/IO 与 ArmC 的 NFS 读冲突（ArmC 近期已有 NFS 停顿），**主动让路**：把 CPU 密集步骤降到 nice / 串行 / 错峰。

**② 交付物（落在 repo，可复现）**：
1. **BaiZe vision tower HF wrapper**（建议 `run/vision/mllm_bridge/modeling_baize_vision.py` + `configuration_baize_vision.py`）：
   - 把 `run/vision/models.py:OpenVision2`（image_size=224 / patch_size=16 / width=1024 / depth=30 / heads=16 / mlp_dim=4096）包成 HF `PreTrainedModel` 子类（`model_type: baize_vision`），加 `config.json`（含 `spatial_merge_size=1`）。
   - **输出 patch-level features `[B,196,1024]`**：走 `forward(..., return_patch=True)` 取 `x`（`self.norm` 之后、**跳过 `ReadoutHead`**，ReadoutHead 仅对比学习用）。
   - **权重加载**：从 ④-4ep ckpt 读 `{'vision': state_dict}`（按 `run/vision/r13_eval_official.py` / `r7_eval.py` 的既有映射，含 `visual.` 前缀剥离逻辑）；映射到 wrapper 参数名；`load_state_dict(strict=True)` 并打印 matched/missing/unexpected 列表。
2. **自定义 LLaVA modeling 文件**（建议 `run/vision/mllm_bridge/modeling_llava_baize.py`，基于盘上 `modeling_llavaonevision1_5.py` 改写）：
   - vision tower 调用替换为 BaiZe wrapper；**projector = 2 层 MLP（1024→2560）**；**跳过 spatial merge**（BaiZe 196 tokens 直出 vs RICE 576/4=144）；**Stage-1 固定 224**；同步处理 image-token 占位数（196）。
3. **CPU 单测**（`run/vision/mllm_bridge/test_wrapper_cpu.py`，纯 CPU、形状/数值断言、不占 GPU）：
   - ① wrapper 载入 ④-4ep ckpt 且 `strict=True` 通过；② 随机 `[1,3,224,224]` 前向 → patch 输出恰为 `[1,196,1024]`；③ 与原始 `OpenVision2.forward(return_patch=True)` **逐元素一致**（`torch.allclose`，证明封装无损）；④ projector 前向 `[1,196,1024] → [1,196,2560]`。
4. **接口/接入说明**（`run/vision/mllm_bridge/README.md`）：目录结构、`config.json` 字段、如何被 ms-swift `swift sft/pretrain --model <baize_llava_dir> --template llava_onevision1_5` 加载、以及 GPU smoke test（100 步）的**前置清单**（GPU 空窗时才跑）。

**③ 允许并行推进（不阻塞、可选）**：#6 Stage-1 数据格式适配（ms-swift 读 WebDataset）、#7 环境统一（py310 装 lmms-eval 或导出方案）——有余力可一并做，但**以 #3#4 为主**。

**④ 交付报告**：更新/新增中文 HTML `reports/report_vision_mllm_bridge_zh.html`：wrapper 设计、**参数名映射表**、CPU 单测结果（贴原始输出）、与 RICE ViT 的差异处理（spatial_merge / 分辨率 / ReadoutHead）、GPU smoke 前置清单与剩余风险。

**⑤ 纪律**：commit 前缀 `vision mllm-bridge:`；任务书 >32KB 自滚归档；证据凭实测（贴 `python -c` 原始输出 + 文件路径），🚫 凭印象；**ArmC 监控/eval 仍是每次唤醒的第一优先动作**，本任务在空窗期推进。


> 📦 §运维指令 · 2026-10-14（📋 Stage(iv) MLLM 可行性评估）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 交付 28.5KB 中文 HTML（9节），2🔴+6🟠+7🟢，3 Stage 数据265GB全在盘，wrapper/modeling 开发纯 CPU 可并行。需要时再读。

> 📦 §运维指令 · 2026-10-14（📊 ArmC 中文状态报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ report_vision_merge3ds_armc_status_zh.html 已交付(7节+2SVG+文献表)，已多次刷新至最新训练数据。需要时再读。

> 📦 §运维指令 · 2026-10-14（✍️ 放行刷新论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ P0+P1 全部修改完成，11→12 页 0 error（commit e0f75ef5）。需要时再读。

> 📦 §运维指令 · 2026-10-14（📝 训练空窗期审视论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 交付 21.8KB HTML，2🔴+6🟠+5🟢，14/16 核验一致。需要时再读。

> 📦 §运维指令 · 2026-10-13（📐 LR 缩放规则）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ 按文献定 LR ×4=2e-3（Goyal arXiv:1706.02677），3 臂扫描，报告已更新含文献表。需要时再读。

> 📦 §运维指令 · 2026-10-13（🔢 数据量口径更正）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：✅ GPIC 快照7437tar≈94M/全量101.1M, 三集合计快照≈111M/全量118.1M, 报告已订正。需要时再读。


### 🆕 运维指令 · 2026-10-13（🚀【放行执行】外部编码器 ProtB 做完后 → 立刻跑「合并三数据集实验」：GBS/MBS ×4 · LR ×2 · 24h ≈3 epoch）· 用户直令 · 最高优先

> 用户令（2026-10-13）：「vision：外部编码器 ProtB 做完后，执行「合并三数据集实验计划」。GBS/MBS ×4 · LR ×2 · 24h → 约 3 epoch。」
> 性质：占 GPU（`.12` H100×8）。⚠️ 与前令「只出计划、不起训」不同 —— 本令 = 放行执行（覆盖前令的「不启动训练」约束）。

① 前置门控（硬）：必须先跑完外部编码器 ProtB（5/5 全出结果）并交付报告，再起本实验 —— 避免两组任务抢 `.12` GPU。路线：ProtB 全部完成 → 本实验开跑。
② 做法（按已交付计划 `report_vision_merge3ds_bs4_lr2_plan_zh.html`）：
- 数据：合并 GPIC + CC12M + Amshaker（blend，权重/去重按计划）；
- 超参：GBS ×4、MBS ×4、LR ×2（相对 E1fair/④-4ep 基线，按计划表）；预算 24h 墙钟 → 约 3 epoch。
- 流程：预注册（判据先行）→ smoke（100 步）→ 全量 → 3-seed ProtB 评测（复用 `lp_protocol_bridge.py`）。
③ 交付：训练日志 + ProtB(3 seeds mean±std) + 中文 HTML 结果报告 `report_vision_merge3ds_result_zh.html` + `EXPERIMENTS_VISION.md` 新节（含 vs 基线 Δlp）。
④ 纪律：起训前 `nvidia-smi` 确认 `.12` 空闲 · 与 data 线新下载错峰 IO · 单一变量（除 GBS/MBS/LR 外与基线逐字节一致）· commit 前缀 `vision merge3ds:` · 任务书 >32KB 自滚归档。


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
