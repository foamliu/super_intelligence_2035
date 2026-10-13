# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-13（🔢 更正 `report_vision_merge3ds_bs4_lr2_plan_zh.html` 的数据量口径 —— **GPIC 被低估**，应按快照实盘重算）· 用户直令 · 最高优先

> **用户质疑（2026-10-13）**：「三集合并 **GPIC 怎么会只有 ~80–85M 样本**呢？**应该 100M+ 样本吧**。」
> **运维核实（✓ 用户对 · 报告错）**：
> - 报告 §2 写：GPIC(7437 tar) ≈ **~80–85M**、三集合计 ≈ **95.8M**。
> - 本线自有记录相反：`EXPERIMENTS_VISION.md` **L934**「GPIC **8000×12,639 = 101.1M** + CC12M 11.0M + Amshaker 5.95M = **118.1M pairs**」；**L60**「GPIC 每 tar 实测 ≈12,495 对」。
> - **实测快照**：`run/vision/data_snapshot_20261009.txt` = **7437 行**（7437 GPIC tar，已核）；`data_snapshot_20261010_full.txt` = **8000 行**。
> ⇒ **GPIC 快照（7437 tar）≈ 93.0–94.0M 对 · GPIC 全量 = 101.1M 对**。**三集合计：快照 ≈ 110–111M · 全量 ≈ 118.1M**。
> ⇒ 报告 §2 的「GPIC ~80–85M / 合计 95.8M」= **6233-tar 时代旧值**（`EXPERIMENTS_VISION.md` L489: 6233×12639+11+5.95≈95.7M），**快照冻结到 7437 tar 后未重算** ⇒ **陈旧引用**。
> ⚠️ **自相矛盾**：报告 §2 **权重列**写 GPIC **~84%**（=94/111），**对数列**却写 ~80–85M（=0.84×95.8）—— 同表两列打架。

**① 必做（只重算数字，不改配方）**：
1. **重算 §1/§2/§3 全部数据量**：GPIC =（快照 7437 / 全量 8000）× **实测每 tar 对数**；CC12M / Amshaker 同法；给**三集合计（快照 / 全量 两栏）**。**每个数附来源**（快照 `wc -l` 行数 / per-tar 实测命令）。
2. **重算受影响的量**：**epoch 定义 + 每 epoch 步数 + 24h 内 epoch 数 + ProtB 外推**。⚠️ 基线 ④-4ep「1 epoch = 187,101 步 × 512 = 95.8M」要按**真实快照量**重判（若快照 ≈111M，则 187,101 步其实 ≈ **0.86 epoch**）。
3. **修自相矛盾的权重列**：GPIC/CC12M/Amshaker 占**三集合计**的 %（用重算后对数）。
4. 若「快照实际对数」与「187,101×512」不一致，**如实并列两种口径**（「训练实际喂入样本数」vs「数据集大小」），🚫 不许混为一谈。

**② 交付**：更新 `report_vision_merge3ds_bs4_lr2_plan_zh.html`（中文 · 自包含）+ 在 `EXPERIMENTS_VISION.md` 加一条**口径订正**（注明旧 95.8M 系 6233-tar 时代值，已被 7437-tar 快照取代）。

**③ 纪律**：🚫 **不许再复用陈旧聚合值**；✅ 每个数字**可溯源到盘点命令**（`wc -l` / `tar -tf … | grep -c`，可 CPU 抽样）；commit 前缀 `vision fix:` · 任务书 >32KB 自滚归档。


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


### 🆕 运维指令 · 2026-10-13（📄「合并三数据集 · GBS/MBS×4 · LR×2」实验计划 · 中文 HTML · 24h 预算）· 用户直令 · 最高优先

> 用户令（2026-10-13）：「vision：生成 html 实验计划（中文版），合并三数据集，GBS/MBS ×4，LR ×2，预估 N epoch 的训练时间即 ProtB 成绩。预算 24 小时。」
> 性质：只出计划（HTML），不启动训练（未获批前）；纯写作 + 估算，不占 GPU。

① 口径（先核，勿臆断）：
- 三数据集 = 本线现有全部 GPIC + CC12M + Amshaker（≈59M 对）；以 `EXPERIMENTS_VISION.md` / `r9_train.py` 实际配置为准，如实列每集对数 + 权重 + 去重。
- GBS/MBS ×4：相对当前基线（E1fair / ④-4ep）各 ×4（写「基线 X → 新 4X」），并做显存 / grad-accum 可行性校核。
- LR ×2：相对基线 ×2（写「基线 LR → 新值」，warmup 是否同比调整）。
- 预算 = 24 小时墙钟（`.12` H100×8 独占）。

② 交付：`doc/BaiZe-ISEDA2027/report_vision_merge3ds_bs4_lr2_plan_zh.html`（中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB）。必需节：① HERO+TL;DR（24h 能跑几 epoch + ProtB 预期）② 三集合并方案表 ③ 超参 before→after 表（GBS/MBS/LR/warmup/grad-accum/显存，标 ×4/×2 依据）④ 时间估算（用 ④-4ep 实测 ~2818 img/s → 单 epoch 墙钟 → 24h 内 N epoch）⑤ ProtB 预估（epoch 曲线 1ep 62.34 / 2ep 65.37 / 4ep 67.05 外推 + BS/LR 敏感性，标「外推·待验」）⑥ 风险 ⑦ 执行清单 ⑧ 诚实条款。

③ 纪律：🚫 不占 GPU、不打断在飞评测 · 🚫 不编数字（外推标「估」）· commit 前缀 `vision plan:` · 任务书 >32KB 自滚归档。


### 🆕 运维指令 · 2026-10-13（🔬 用 ProtB 评测 `/nas_train/app.e0031982/models` 下现有公众视觉编码器 · 参考值 · 最高优先）· 用户直令

> 用户令（2026-10-13）：「用 ProtB 评测现有 vision encoder（CLIP、SigLIP/SigLIP2、AIMv2、OpenVision2、RiCE-ViT 等，都在 `/nas_train/app.e0031982/models` 已下载）。」
> 性质：评测类任务（占 GPU，在 `.12`；不训练编码器，只 linear-probe）。🔥 ④-4ep 已全收尾、`.12` 8 卡空；只须注意与 data 线 NFS 下载错峰（它占 IO 不占 GPU)。

① 目标与范围（运维已实地盘点 `/nas_train/app.e0031982/models`，以下为实存编码器）：
| 模型 | 路径 | 加载方式 | 备注 |
|--|--|--|--|
| CLIP ViT-L/14 | `openai/clip-vit-large-patch14-336` | transformers `CLIPVisionModel` | 本线冻结文本塔同源，vision 侧可测 |
| SigLIP2 so400m | `google/siglip2-so400m-patch14-384`（另有 `-224`/`-16-384`/`-16-512`） | transformers `Siglip2VisionModel` | ⚠️ 无原版 SigLIP，只有 SigLIP2 |
| AIMv2-1B | `apple/aimv2-1B-patch14-336`（另有 `-448`） | HF 自定义 `modeling_aimv2.py`（就在目录内） | `model.safetensors` 4.9GB |
| OpenVision2 official | `UCSC-VLAA/openvision2-vit-large-patch14-336-vision-only` | open_clip（`open_clip_pytorch_model.bin`+`open_clip_config.json`） | R13 已跑过 Protocol A=79.81% |
| RICE-ViT-L | `DeepGlint-AI/rice-vit-large-patch14-560` | HF `config.json`+`model.safetensors` | 需核 modeling 代码来源并落地 |
| 可选加测 | `lmms-lab-encoder/onevision-encoder-large` | HF 自定义 `modeling_onevision_encoder.py` | 易加载则一并测 |

② 关键工程前提：现有 `lp_protocol_bridge.py` 只吃 BaiZe `.pt`（`load_vision`/`encode_images` 来自 `r8_eval_in1k.py`），不能加载外部模型 → 需新增「外部编码器加载层」，把每个模型统一暴露成 `encode_images(imgs) → pooled_features`（用于 probe），并按各自 native 分辨率 + native mean/std 预处理（CLIP 336/CLIP-norm · SigLIP2 384 视其 preprocessor · AIMv2 336 · OV2 336 · RICE-ViT 560）。⚠️ 统一用 pooling 输出（cls/pooled），若各模型特征维不同属预期。

③ Protocol（严格复用 ④-4ep 的 ProtB，冻结）：IN-1k 官方 val(50k) 评测 + 全量 train(1.28M) SGD+momentum0.9、cosine(5ep warmup)、90ep、bs1024、3 seeds(0/1/2) 报 mean±std；直接复用 `lp_protocol_bridge.py` 的 `linear_probe_mainstream()`。

④ 红线：
1. 🚫 公众预训练 =「参考值」，必须另起一张表，绝不与 from-scratch BaiZe（④-4ep 67.05% 等）放同一榜里排名不加区分（历史纪律：『训练过的模型』打『从零的模型』是作弊口径）。
2. 🚫 不许编数字：lp 用实测；公开论文 lp/zero-shot 只作「文献锚点 · 待核」标注，不得当本项目结论。
3. ⚠️ 分辨率/patch 各不同（224/336/384/448/560）→ 报告每行显式标注 native 分辨率，并声明「跨分辨率 lp 不可直接排高下」。

⑤ 交付：`doc/BaiZe-ISEDA2027/report_vision_external_protb_reference_zh.html`（中文 · 自包含 · 内联 CSS/SVG · 零外链）+ 在 `EXPERIMENTS_VISION.md` 新增「§外部编码器 ProtB 参考」小节。表 = 每模型一行：native 分辨率 · 特征维 · ProtB mean±std(3 seeds) ·（可选）zero-shot · 文献锚点。

⑥ 执行序（先 smoke 后全量）：① 建加载层 + 每模型 smoke（能 load/能出特征/维度对/前向不 OOM）→ ② 先报「最终模型清单 + 各 native 配置 + 全量 ETA + 占卡」再跑全量（⚠️ RICE-ViT@560 / AIMv2-1B 高分辨率重 I/O、显存大，feature extraction 可能 ~10–20h/模型，务必先给 ETA 与分批计划）→ ③ 全量 feature extraction + 3-seed probe → ④ 出表 + HTML + 提交。

⑦ 纪律：占 `.12` GPU 前 `nvidia-smi` 确认空闲 · 与 data 线下载错峰（必要时夜间跑/降 workers）· commit 前缀 `vision protb:` · 任务书 >32KB 自滚归档。

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


> 📦 §运维指令 · 2026-10-08①（📝 更新论文 LaTeX）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：6_vision_encoder.tex 已更新（mask-ratio 表 + weight-ratio 表 + §VI-D AR 范式探索），main.pdf 11p 0err，commit 6f2baa2b。需要时再读。

> 📦 §运维指令 · 2026-10-08②（📄 全线总结报告 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：report_vision_encoder_final.html（28.6KB, 10 节/4SVG）+ report_vision_final_20261008.html（v2 最终版）已交付，commit 67a306f8。需要时再读。

> 📦 §运维指令 · 2026-10-07③（mask-ratio 消融报告 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_mask_ratio.html 已交付（34.3KB, 8节+2SVG, 倒U形 0.6 最优, commit ee9db3ca）。需要时再读。

> 📦 §运维指令 · 2026-10-07②（GPU12 对账簿）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：pretrain 借 GPU1–7 跑完长上下文成本矩阵后 09:44 已归还，GPU12_ALLOC.md 已建。需要时再读。

> 📦 §运维指令 · 2026-10-07（📊 昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_10_07_vision_overnight.html 已交付（自包含 27.7KB，内联 SVG，零外部依赖）。需要时再读。

> 📦 §运维指令 · 2026-10-08③（💬 下一步工作建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：4 题已答（未验证假设/Stage iv 前置/GPU 利用/论文补充），写入 MEMORY_VISION.md「运维问答」区，commit 0bb4dc24。需要时再读。


> 📦 §运维指令 · 2026-10-06（✅ 批准 AIMv2 官方 AR 范式 + 6 点修订）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：6 点修订已落实，Arm A baseline lp=13.49% 最优 / Arm B pure AR 坍缩@step600 / Arm B-hybrid lp=1.37% Δ−12.1pp，report_vision_aimv2_official_vs_ours.html 已交付。需要时再读。


> 📦 §运维指令 · 2026-10-06（📋 vision 后续队列裁定）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：队列全部完成（① lp 协议 A/B → ② mask-ratio 5 臂 0.6 最优 → ③ weight-ratio 4 臂 1:1 最优 → ④ 官方 AIMv2 AR Arm A/B/B-hybrid）。方向 1 待 GPIC 下载；方向 4 已作废。需要时再读。


> 📦 §运维指令 · 2026-10-06（🔬 lp 评测协议与主流对齐研究）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_protocol.html 已交付（21.2KB, 2026-10-07）。需要时再读。


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

- `run/VISION_ARCH_FRONTIER_2026.md` —— 2026 前沿架构调研（iGVLM / TuringViT / MambaEye / MoE-ViE / FastVLM）+ 与 R8 的逐项对照 + §5 数据量口径错误更正。
- 关键事实速查：
  - R9 lp 渐近 25.1%（幂律 `acc=0.251−0.864·N^−0.090`，R²≈0.94）· 当前路线 = OpenVision2 w512 + CC12M+Amshaker + 冻结 CLIP-768 文本塔 + InfoNCE。
  - R10-② 二维拟合（3 点 M 轴）：M 边际效应全区间为负（≈ −2.2 lp pp/参数翻倍）→ 数据受限区间加宽塔是负收益。
  - `attention flash` 仅占 GPU 自耗 0.7%（P-4）· 分辨率 224/16。
- 已核实官方资源（运维 2026-10-03）：
  - `UCSC-VLAA/OpenVision`（Apache-2.0；同时支持「对比+生成」与「caption-only」两套目标；2026-08 已放出 decoder；训练栈 TPU/JAX，PyTorch 侧基于 OpenCLIP fork）。
  - `apple-aiml-research/ml-aim`（AIMv2-L 0.3B = 87.6% 冻结 trunk / 77.0% LiT zero-shot；代码与权重均已发布；LICENSE 待逐字核实）。
- 数据侧硬约束（机制推断，⚠️ 须 R11 实测验证，不得当结论引用）：我们 caption 偏短（CC12M = alt-text 短句 / Amshaker = 中长 / GPIC short = 20 tok），官方用 ReCap-DataComp-1B v2 的 LLaMA-3 长合成 caption → caption-only 生成式的监督密度会被我们的短 caption 拖累；AIMv2 式（含 patch 预测）不依赖 caption 丰富度。
- 口径提醒：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

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
