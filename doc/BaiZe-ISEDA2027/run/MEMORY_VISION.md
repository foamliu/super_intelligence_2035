# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🔁 **2026-10-09 晚（运维直令 · 最高优先）**：scaling E1/E2 的 **schedule 公平性**被复核推翻 —— 旧两臂 `--lr 3e-3 --warmup 20` 在 **187,101 步**下 warmup 仅 **0.01%**（该配方原为 **30k 短跑**设计）⇒ **「Bigger is WORSE (Δlp=−5.59pp)」不可信、作废重做**。**新任务：`BAIZE_VISION_TASK.md` 顶部 `2026-10-09⑨`**（`warmup=2000` / `lr=5e-4` / **cosine** / `min_lr=5e-5`；两臂**必须同一冻结数据快照**；输出 `scaling_E{1,2}fair_ov2_w{512,768}_d30_p16_224` **不覆盖旧结果**；旧报告加「⛔ 结论已被取代」横幅）。
> 🔴 **注意**：~~`r9_train.py` 不支持 cosine~~ **已修复**（`lr_at` = warmup→cosine(`min_lr + 0.5*(lr-min_lr)*(1+cos(π*(s-w)/(steps-w)))`) or const）；`--scheduler {const,cosine}` + `--min-lr` 已加，lr 四点自检已打印入 train.log。smoke_cos 预检两臂 `total_shards=10787=10787` 一致✅。

| 字段 | 值 |
|:---|:---|
| PHASE | 🔁 **Scaling fair rerun: E1fair RUNNING via bothfair** (step ~73500/187101 ~39%, ~5200 img/s avg, loss~0.26, C1=0.47 C2_gap=+0.19 C4=OK, no collapse, lr=3.54e-04 cosine active decaying). **bothfair mode** (PID 2670216, etimes~10404s ~2.9h) auto-chains: E1fair→eval→E2fair→eval. ckpts saved @step10000-70000 (7 ckpts, 487MB each). ETA: E1fair done ~04:30 Oct10 → E1 eval ~3.5h → E2fair ~6h → E2 eval ~3.5h → **all done ~17:30 Oct10** |
| WAITING | 1（🔁 **E1fair running step~73500/187101 (~39%) via bothfair**. Next wake: check E1fair/E2fair progress, collect eval results, fill §8.2 in EXPERIMENTS_VISION.md, write report_vision_scaling_fair.html） |
| ERROR_COUNT | 8（①~⑤ 同前 ⑥ AIMv2.forward() return_patch修复 ⑦ E1 DataLoader bus error@step131490 ⑧ **step-count mismatch caught**: GPIC grew 6233→6754 tar between E1/E2 launches; E2 would train 6.8% longer. Fixed by explicit `--steps 187101`. Also: sympy 1.5.1 incompatible with torch 2.8.0 → fixed by copying sympy 1.14.0 from vllm conda env） |
| BUDGET_USED | R2–R12 ≈215 + R12b(106.4) + lp bridge(5.8) + mask-ratio(78.4+0.5) + weight-ratio(~65.4+0.5) + ④ AIMv2 AR Arm B(2.1) + Arm B-hybrid(~24) ≈ **累计 ~498 GPU·h** + scaling E1(~2.1h×8=~17 GPU·h) + E2(~11.4h×8=~91 GPU·h) + evals(~3h×1 GPU) ≈ **~609 GPU·h** |
| 更新 | **2026-10-10 01:20（E1fair RUNNING ~39% health check）**: ✅ E1fair at step~73500/187101 (~39%), ~5200 img/s avg (range 3411-5979, NFS fluctuation), loss~0.26 (down from ~0.45@29%), C1=0.47 C2_gap=+0.19 C4=OK no collapse, lr=3.54e-04 (cosine decaying from 5e-4 peak, correctly tracking). ckpts saved @step10000-70000 (7 ckpts, 487MB each, 3.4GB total). ✅ lr self-check verified in real run: lr@0=0, @warmup(2000)=5e-4, @50%(93550)=2.79e-4, @last(187100)=5e-5, monotonically decreasing✅. ✅ total_shards=10787 (7437 frozen GPIC snapshot + CC12M + Amshaker) — both arms byte-identical. ✅ bothfair (PID 2670216, etimes~10404s ~2.9h) running correctly, will auto-chain E1fair→eval→E2fair→eval. ✅ ⛔ banner verified on `report_vision_aimv2_scaling.html`. ✅ 245 PROBE events, ALL C4=OK, 0 fusing events. All 8 GPU 16.5GB/card, 67-89% util. ETA: E1fair done ~04:30 Oct10 → E1 eval ~3.5h → E2fair ~6h → E2 eval ~3.5h → **all done ~17:30 Oct10**. 📦 体积：TASK=32.1KB / MEMORY=26.7KB（均≤32KB ✅） |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

## 🗣️ 运维问答 · 2026-10-08③（下一步工作建议）

> 回应运维指令 2026-10-08③。纯写作，不占 GPU。每条建议附实验编号/报告/数据路径为依据。

### 1. 未验证的假设 / 遗留疑点

**1-A · AIMv2-style 在更小塔（w384）上可能更优**
- 依据：R10-③ 实测 w384(71.5M) InfoNCE lp=7.99%@15.36M **全宽度最高**（w512=6.08%），M 边际全区间为负 ≈−2.2pp/参数翻倍（`EXPERIMENTS_VISION.md §R10`，论文 §VI-B）。R11-G 证 AIMv2-style 在 w512 翻盘（7.40%→19.76%，+12.4pp，R²=0.91）（`§R11-G`，Table~XII）。**两者交叉点未验证**。
- 设计：1 臂 w384 AIMv2-style(`--loss aimv2 --mask-ratio 0.6`)，CC12M+Amshaker 18.5M，30k 步，8 卡。≈2h/~16 GPU·h。判据：lp@30k ≥ 13.49%+1.5=15.0% → w384 更优。
- 价值：若正面 → 最终编码器选 w384（更小更快，Stage iv 延迟更低），scaling 曲线需重拟合。

**1-B · C1（对比对齐）与 lp（线性可分性）的背离是系统性的**
- 依据：① mask-ratio arm 0.3（C1=0.3495 < 0.6 的 0.3810，但 lp=12.69% 接近，zs=5.25% > 4.72%）（`§mask-ratio 结论#5`）；② weight-ratio arm 0.5:1（C1_final=0.2816 **最低**，但 lp=13.80% **最高**）（`§weight-ratio 结论#7`）。→ 降低 contrast 权重 → C1↓ 但 lp↑，暗示 InfoNCE 对齐压力与 lp 特征质量有 trade-off。
- 设计：contrast_weight 精细扫描 {0.1,0.25,0.5,0.75,1.0} × 3 seeds。先跑 0.1/0.25 两点 × 1 seed = ~32 GPU·h 确认趋势。判据：lp 倒 U，峰值点 = 最优 trade-off。
- 价值：机制理解——若确认，论文可写「InfoNCE 的作用是防坍缩锚点而非 lp 最优化」。

**1-C · R12b「更多 unique 数据 ≠ 更高 lp」归因未隔离**
- 依据：R12b(69.7M,2ep) 18.81% < R11-G(18.5M,1ep) 19.76% < R12-3ep(58.8M,3ep) 20.27%。matched-N 显示 R12b 始终 ≤ R12-3ep（`EXPERIMENTS_VISION_ROUND12.md §2`）。可能原因：① GPIC short caption 9% 在 77-token 100% 截断→InfoNCE 退化；② epoch 重复=隐式增强。**两因素未隔离**。
- 设计：取 R12 58.8M 混合数据只跑 1 epoch(~136k 步)，与 R12 3-epoch 同 N 对比。≈6.5h/~52 GPU·h。判据：1-epoch lp ≈ 19.76% → epoch 有效；> 18.81% → GPIC 质量是主因。
- 价值：指导方向 1(GPIC 全量 100M)是否值得——若 epoch > unique，100M×1ep 不如 58.8M×3ep。

**1-D（低优先）· 更高分辨率的 dense 监督信号更强**
- 依据：224/16=196 patch，mask 0.6=~118 被遮。336/16=576 patch，mask 0.6=~346 → dense 密度 2.9×。S6(论文 §VI-C)只测 InfoNCE 未测 AIMv2-style。
- 设计：336/16 AIMv2 30k，对比 224/16 baseline 13.49%。≈3h/~24 GPU·h（吞吐降 ~40%）。判据：lp ≥ 13.49%+1.5 → 高分辨率有益。

### 2. Stage (iv) MLLM 对齐的前置准备（视觉编码器侧）

**2-A · Projector 设计预研**（纯 CPU，~1 天）
- 编码器输出 196 patch token(512-dim)+1 CLS。候选：① LLaVA 式 linear projection；② 2-layer MLP(LLaVA-1.5)；③ Q-Former/resampler(BLIP-2)。196 token 已较紧凑(CLIP-L/14@336=576)，linear/MLP 可能够用。→ 产出 `VISION_MLLM_PROJECTOR_DESIGN.md`。依据：论文 §VI-C 已声明「Stage~(iv) revisits the visual-token count for detail-dense layout」。

**2-B · 分辨率/patch token 消融预案**（CPU 准备 + GPU 实验）
- 224/16=196 对版图 VQA 远不够。预案：336/16=576、448/16=784、336/14=576(匹配官方 OV2)。需决定重训 vs pos-emb 插值。→ 先跑假设 1-D(336/16 AIMv2 30k)验证。依据：S6 显示 224/16 InfoNCE 最优但 dense 未测；官方 OV2 用 patch14/336（`VISION_OFFICIAL_REPOS_SURVEY.md §10.4`）。

**2-C · 视觉塔冻结 vs 解冻评测框架**（纯 CPU 代码，~2 天）
- Stage iv 需决定：① 冻结 trunk+可训 projector；② +LLM LoRA；③ 端到端微调。→ 搭 `vision/eval_mllm_readiness.py`：从最佳 ckpt 提特征→冻结/解冻开关→lp/zs 评测。依据：R11-L2 LoRA 解冻文本塔未翻盘(Δ−0.30~−0.80)（`§R11-L2`）→ 视觉塔解冻也需预验。

**2-D · 特征提取与缓存管线**（CPU+轻 GPU，~0.5 天）
- 从最佳 ckpt(R12 3-epoch 或 R11-G)提取并缓存 IN-1k/GPIC 特征到磁盘，供 Stage iv 直接读取。脚本 `vision/extract_features_cache.py`，复用已修复的 `extract_features_streaming`。依据：lp protocol bridge 已验证提取管线稳定(3 ckpt×A/B×3 seeds 无 crash)。

**2-E · 数据配对脚本**（纯 CPU，~1 天）
- GPIC 含 layout/parasitic 标注。Stage iv 需 image→script/script→image/版图 VQA。→ 检查 GPIC json 字段、编写配对脚本、统计可用量。与 data 线协调。依据：E1 实测 GPIC 每 tar ≈12,639 对（`§C1`）。

### 3. GPU 空窗期利用建议（优先级排序）

| 优先级 | 候选 | 成本 | 理由 |
|:--|:--|:--|:--|
| **P1** | AIMv2 on w384(假设 1-A) | ~16 GPU·h/~2h | 信息密度最高：1 臂回答「最优编码器是否应更小」+「AIMv2 翻盘在 w384 是否放大」。若正面→直接影响 Stage iv 选型。R10 已证 w384 InfoNCE 最优，AIMv2 交叉点未测是最大空白。 |
| **P2** | Protocol B 评测消融臂(9 ckpt) | ~6 GPU·h/~1h | 论文消融表(Table~XIII/XIV)全用 Protocol A(比主流低~10pp，`BP-3`)。对 9 臂跑 Protocol B → 补「主流协议」数字，可与 DINOv2/MAE/iBOT 横比。桥接脚本 `lp_protocol_bridge.py` 已就绪，GPU 占用极轻。 |
| **P3** | 336/16 AIMv2 test(假设 1-D) | ~24 GPU·h/~3h | 同时验证高分辨率 dense 假说 + 为 Stage iv 分辨率选型提供数据。吞吐降~40%+需 pos-emb 插值，风险高于 P1。建议 P1 有正面信号后再做。 |

> **不建议现在做**：假设 1-B(contrast 扫描 ~240 GPU·h)和 1-C(epoch vs unique ~52 GPU·h)——前者太重且已有 2 点数据，后者与方向 1(GPIC 全量)强耦合，等 GPIC 下完一起做更有意义。

### 4. 对论文的补充建议

**4-A · 缺 Limitations 段（应补）**
- 论文以 §VI-D AR 探索收尾(line 277)，无 Limitations/Future Work。建议加：① 数据规模 ~118M vs AIMv2 ~12B(102× 缺口)(`§C1`)；② 短 alt-text(~20 tok) vs LLaMA-3 长合成 caption(`VISION_AIMV2_OFFICIAL_PLAN.md §6`)；③ 单 seed(除 lp 协议 3 seeds 外消融全 seed 0)(`§mask-ratio/§weight-ratio`)；④ Protocol A 比主流低~10pp(`BP-3`)；⑤ 仅 224/16 未测高分辨率 dense；⑥ 无下游 MLLM 评测。

**4-B · 缺 Protocol B 结果+公开基准横比（应补）**
- Table~XII 仍用 Protocol A(19.76%)。已有 Protocol B：R11-G=**29.94±0.04%**、R12 1ep=**30.27±0.03%**(3 seeds σ<0.1pp)(`report_vision_lp_protocol.html`)。→ 加一列「Protocol B(mainstream)」或脚注，补与 DINOv2/MAE/iBOT 公开 lp 横比表(需 `cimi_search` 查公开数字)。

**4-C · R12b「更多 unique 数据 ≠ 更高 lp」未写入（应补）**
- 论文 §VI-C 提到 3-epoch 延伸(20.27%@176M)但未讨论 R12b(69.7M,2ep,18.81% < R11-G 19.76%)。这是 epoch vs unique 的重要发现(`§R12b`，`EXPERIMENTS_VISION_ROUND12.md §2`)，应写入 §VI-C 或 Limitations。

**4-D · C1 vs lp 背离未写入（可选补）**
- 两组消融均发现 C1↓ 但 lp↑(`§mask-ratio 结论#5/§weight-ratio 结论#7`)。建议加 1-2 句：「contrastive alignment (C₁) and linear separability (lp) can diverge: reducing contrast weight lowers C₁ but raises lp, suggesting the contrastive term's role is collapse prevention rather than lp optimization.」

**4-E · Future Work 段（应补）**
- ① 高分辨率编码器(336/448) for MLLM；② 更长 caption(LLaMA-3 式)；③ GPIC 全量 100M scaling；④ Stage (iv) MLLM 对齐评测。

## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

- 阶段一：w512/w768/w1024 lp = 6.10/3.63/1.03% → 选 **w512（126.8M）**。阶段二：w512×108k=55.3M，lp 峰值 7.70%@51.2M。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **25.1%**）；外推 20% 需 41 万亿样本 → **本地 ≈118M 上限够不到**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对 vs 我们 649× 少），非架构。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

- 2D 拟合（19 点 R²=0.980）：M 边际效应**全区间为负** ≈ −2.2 lp pp/参数翻倍 → 数据受限区间**加宽塔是负收益**。
- **w384@15.36M=7.99% 为全部宽度最高**；最优 M 仍在观测下界（71.5M）之下 → 无饱和点、更小塔持续更优。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

- CPU-only 源码普查，与 R10-③ denseM 训练并行。产物：`VISION_OFFICIAL_REPOS_SURVEY.md`（①目标②数据③config④结构差异⑤可复用资产⑥LICENSE⑦三清单）。
- ✅ 两个 ⭐⭐⭐ 仓库源码普查完成（上一 cycle）：**OpenVision**（JAX/TPU，官方 ViT-L/16 = w1024/d24/h16；文本 = BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35）；**ml-aim/AIMv2**（仅模型接口，无训练/损失/数据；LICENSE = Apple Sample Code，🔴 不可 COPY）。
- ✅ 第二阶段（本轮）全部核毕：
- [06:45] **③ weight-ratio 消融 ALL DONE + 结果记录**: ✅ **4臂全部完成 + 16ckpt IN-1k eval完成@05:27:03**. arm4 cw2_plw1(2:1) DONE@05:05: step30k, 7521s, steady_img_s=2691.8, C1_final=0.3475, C1_peak=0.4177@22500, C4=OK无坍缩, final_loss=7.0765. IN-1k lp结果: arm1(1:2)=13.13%(Δ−0.36不显著), arm2(1:0.5)=10.22%(Δ−3.27显著差), arm3(0.5:1)=13.80%(Δ+0.31不显著, 最优), arm4(2:1)=10.21%(Δ−3.28显著差). Baseline 1:1=13.49%. **结论: 无翻盘; contrast_weight过高/patch_weight过低显著有害; patch-heavy方向更宽容**. 8条结论+完整结果表已写入EXPERIMENTS_VISION.md. GPU已释放(PID 3214830已退出). **消融队列②③已全部完成 → 下一步=④ 官方AIMv2 AR范式**. 📦 体积：TASK=31.9KB / MEMORY=16.3KB（均≤32KB✅, 无需归档）.
  - **OpenVision2 权重 = ✅ 已放出且真带 caption decoder**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only`；含 `caption_decoder.safetensors` + `text_decoder_config.json`（concat/prefix-LM，非 CoCa cross-attn）。🔑 官方 = **patch14/d24**，我们 = **patch16/d30**（models.py:170）→ R13 需另建官方结构塔才能 load。
  - **FastVLM** = ✅ `apple/ml-fastvlm`（FastViTHD 1024² conv-hybrid RepMixer）；LICENSE = Apple Sample Code（research-only，不可抄）。
  - **MambaEye** = ✅ `usingcolor/MambaEye`（MIT）：纯 Mamba2、**小模型监督分类**（非对比）；**MoE-ViE** = ✅ `facebookresearch/moe_vie`（CC BY-NC 4.0）：CLIP 风格 MoE-ViT，官方权重 HF；**iGVLM(AdaLN)/TuringViT** = 🚫 **未找到官方实现**（iGVLM 同名 IG-VLM 是视频QA；TuringViT 仅项目主页）。
- 关键产出（对 R13/R12）：官方 MoE-ViE/FastVLM/MambaEye/AIMv2 权重均可作「官方 vs 自研」对照标尺；OpenVision2 官方是 patch14/d24，需建官方结构塔。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

- 抽 **8 个 tar 均匀抽样**（index 0..1212）实测：**12,537 图文对/tar**（稳定 ±2%）→ **GPIC 全量 ≈ 100.3M**（证官方 100M 卡；旧「5 tar=86M」少计 png 作废）；**已下 1213/8000 tar ≈ 15.2M**。
- `caption_type` mix：short **45.0%** / medium 45.1% / long 9.0% / tag 1.0% → **可训练 short 子类：全量 ≈45M / 已下 ≈6.8M**。
- 🔑 **C1 口径定案**：R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态、仍在下载）——与 `r9_scaling.py --local-cap-m default=118.0` 一致；R11-E「同 N」可比区间被压到 ≈6.8M（short 已下 < 18.5M），须如实说明。已回填 `VISION_ARCH_FRONTIER_2026.md §5`。

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

## ⏱️ 全量 1-epoch 耗时估算（✅ 回答运维指令 2026-10-08④，使用 scaling 实验 smoke 实测数据）

> 运维指令 2026-10-08④ 问：「现有所有数据训练 1 epoch 需要多长时间？」
> ⑤ 升级后本估算作为 ETA 报备（不再是终点）—— 实际训练已在跑。

**N（逐源）**：GPIC 6233 tar × 12,639 = 78.8M + CC12M 1100 × 10,000 = 11.0M + Amshaker 2250 × 2,646 = 5.95M ⇒ **合计 ≈ 95.7M 对**（与 ④ 的 94.9M 基本一致，差异来自 tar 计数微调）。
不含 LLaVA/CC3M/coco/vg（这些不参与当前训练）。

**img/s（实测，2026-10-08 smoke test）**：
- **(a) E1 w512 smoke**：**4697 img/s**（30 steps / 6.3s，8 卡 H100，bs64×8=512，nw=6，224/p16，AIMv2 dense objective）— **这是最真实的端到端吞吐**（含 NFS 数据加载 + AIMv2 forward/backward）。
- **(b) E1 训练实测**：稳态 ~5100 img/s（step 14k–17k，NFS 波动 2300–6300）。
- **(c) R12b 有效吞吐**（历史参考）：139.3M 图 / 106.4 GPU·h / 8 卡 = ≈2909 img/s（含更多 overhead）。

**墙钟（8 卡，1 epoch ≈ 187,101 steps）**：
- 按 smoke 4697 img/s：95.7M / 4697 = 20,373 s = **5.66 h**
- 按训练稳态 5100 img/s：95.7M / 5100 = 18,765 s = **5.21 h**
- 按 R12b 2909 img/s（保守下界）：95.7M / 2909 = 32,895 s = **9.14 h**
- ⇒ **区间 ≈ 5.2–9.1 h/epoch**（+ IN-1k 评测 ~1–2h）
- GPIC 若下满 8001 tar（N ≈ 118M）⇒ **6.6–11.3 h/epoch**

**是否 >1 epoch**：R12b 已实测「更多 unique 数据 ≠ 更高 lp」（69.7M×2ep lp=18.81% < R11-G 18.5M 的 19.76%）⇒ **1 epoch 足够**；多 epoch 是隐式增强效果（R12 3-epoch 20.27% > 1-epoch 17.57%），但边际递减。

## AIMv2 提速归因实测（✅ 完成，2026-10-06 12:33–12:44）

> 运维指令「运维前置 · AIMv2 提速」（已归档 → `ARCHIVE_OPERATOR_VISION.md`）。目的：bs 64/128/256 归因 + num_workers 扫描 → 判断瓶颈是数据/IO 还是算力。详见 `EXPERIMENTS_VISION_ROUND12.md §1`。

### batch size 扫描（nw=6 固定）

| BS | Global | steady img/s | ms/iter | Mem(GB) | GPU util |
|---:|---:|---:|---:|---:|:---|
| 64 | 512 | **4993** | ~102 | 16.5 | 62–83% (~70%) |
| 128 | 1024 | **6293** | ~134 | 26.8 | 49–95% |
| 256 | 2048 | **8314** | ~250 | 47.6 | 48–100% |

### num_workers 扫描（bs=64 固定）

| NW | steady img/s | Notes |
|---:|---:|:---|
| 6 | **4993** | baseline |
| 12 | **4262** | 更差（NFS 争用） |
| 16 | **5311** | 略好（噪声范围） |

### 诊断：**bs=64 下数据/IO 受限（非算力受限）**

1. GPU util ~70%（未饱和）→ 符合「util≲70% = 数据/IO 受限」判据
2. image/s 随 MBS 上升（4993→8314, +66%）= 每步开销摊销，**非**算力受限标志
3. ms/iter 亚线性增长（64→256 = 4×, ms/iter 2.45×）→ 混合瓶颈，以数据/IO 为主
4. 显存远未满（16.5/81.6 GB = 20%）；num_workers 无显著效果（NFS 带宽是瓶颈）
5. 无本地 NVMe；1.7 TiB RAM 但数据 ~742 GB（预热增益有限，NFS 波动仍存）

### 处方：保持 bs=64 / global 512 / nw=6

- ❌ 加 MBS → 改 recipe → 不并入 scaling 曲线
- ❌ 加 num_workers → NFS 争用（nw=12 实测更差）
- ❌ 无本地 NVMe 可用
- **当前 ~5000 img/s 是 NFS 架构下可达到吞吐率**

### 全量训练时长估算（实测 img/s）

- 总 unique pairs ≈ 58.8M；1 epoch ≈ 114,844 步
- 实测 ~5000 img/s → **1 epoch ≈ 3.3h**；保守 ~4500 img/s → **1 epoch ≈ 3.7h**
- R12 3-epoch 实测平均 4470 img/s → 1 epoch ≈ 3.7h（吻合）
- **>1 epoch？是。** 2 epoch ≈ 7.2h, 3 epoch ≈ 10.8h
- 从零 1 epoch ≈ 29.6 GPU·h；从零 3 epoch ≈ 88.8 GPU·h

### 脚本路径

- `vision/r12_throughput_bench.sh`（bs 扫描）+ `r12_throughput_bench_128_256.sh` + `r12_throughput_bench_nw.sh`
- 日志：`/tmp/bench_bs{64,128,256}.log` + `/tmp/bench_nw{12,16}.log`

## 本唤醒流水

- [2026-10-09 晚 · 运维] 🔁 **scaling 公平性重跑令下发（用户直令）**：复核 `report_vision_aimv2_scaling.html` §11 复现命令 ⇒ 两臂 `--lr 3e-3 --warmup 20` 在 **187,101 步**下 warmup = **20/187101 = 0.01%**（原为 30k 短跑配方，见 `ARCHIVE_OPERATOR_VISION.md` 2026-10-05 全量训练块）⇒ 「Bigger is WORSE (Δlp=−5.59pp)」**不能归因于规模，作废重做**。已下发 `BAIZE_VISION_TASK.md` 顶部 **2026-10-09⑨**：① 配方 `warmup=2000` / `lr=5e-4` / **cosine** / `min_lr=5e-5`，其余（bs512/seed1234/224/p16/d30/AIMv2/mratio0.6/`--steps 187101`）不动，唯一差异仍 `--width`；② **`r9_train.py` 必须新增 `--scheduler {const,cosine}` + `--min-lr`**（现 `lr_at` 是 warmup 后恒定，写 `cosine` 也是假的），并打印 lr 四点自检入 `train.log`；③ **两臂同一冻结 tar 快照**（`snapshot_gpic` → `data_snapshot_20261009.txt`，`smoke_cos` 预检 `total_shards=` 两臂相同）；④ 新输出目录 `scaling_E{1,2}fair_ov2_w{512,768}_d30_p16_224`，**旧结果原地保留不覆盖**；⑤ 旧报告顶部加「⛔ 结论已被取代」横幅；⑥ 判据沿用 ⑤（±1.5pp / 3-seed σ / 单点≠scaling law）；⑦ 体积：TASK 32,179→29,520B（先把 2026-10-08⑥ 搬入 `ARCHIVE_OPERATOR_VISION.md` 并留指针），加 ⑨ 后 37,134B **超 32KB ⇒ 本块归档后需再滚**。`GPU12_ALLOC.md` 申请区+1 行、流水+1 行。**ETA ~14–18h 墙钟（`.12` 8 卡）。** ⚠️ 本块由运维代发（agent 只做 volume 搬迁，不改指令）。

> 📦 15 条 R12b 巡检流水(10-06 12:33–23:57)已归档 → daily-memories-vision/2026-10-06.md（2026-10-07 13:00 滚动）
> 📦 5 条 R12b 巡检#17-19 + 完成 + eval(10-07 00:33–03:07)已归档 → daily-memories-vision/2026-10-07.md（2026-10-08 03:23 滚动）
- [02:23→03:07] *(R12b 训练完成 + eval完成 + lp协议A/B桥接启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp_max=18.81%, R12b<R11-G, lp bridge PID 1499158 启动）
- [03:20→23:25] *(lp bridge 完成 + mask-ratio 消融 ALL DONE + 报告HTML交付 + weight-ratio arm1 DONE + arm2 启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp bridge Δlp≈+10pp 3ckpts极稳定; mask-ratio 0.6最优13.49%倒U; report_vision_mask_ratio.html 34.3KB commit ee9db3ca; arm1 cw1_plw2 DONE C1=0.3546）
- [22:46] *(arm1✅DONE + 脚本异常退出→恢复)* — 已归档至 daily-memories-vision/2026-10-07.md（arm1 cw1_plw2 DONE@22:11, C1=0.3546, 脚本crash→恢复PID 3214830）
- [02:48→20:08] *(weight-ratio arm3巡检 → ④AIMv2 AR Arm B坍缩 → scaling E1/E2 训练+eval 全过程)* — 20条巡检流水已归档至 `daily-memories-vision/2026-10-09.md`（原文未改）。**关键结论**：E2 ProtB=23.76±0.04%, E1 ProtB=29.35%, Δlp=−5.59pp "Bigger is WORSE" —— ⚠️ **该结论已被 2026-10-09⑨ 作废（schedule 不公平），公平重跑中**
- [09:05→19:31] *(④ Arm B-hybrid巡检 → ⑥ E2变更 → scaling E1 crash/resume → E1/E2 训练eval全流程 → HTML报告)* — 全部已归档至 `daily-memories-vision/2026-10-{08,09}.md`（原文未改）。E1 crash@step131490→resume from 130k; E2 训练 11.35h; HTML report `report_vision_aimv2_scaling.html` 26KB
- [20:42] **🔬 scaling — ALL EVALS DONE, REPORT FINALIZED**: ✅ All evals completed by 20:41. **E2 ProtB=23.76±0.04%** (seeds 0/1/2: 23.74/23.82/23.73), **E2 ProtA=15.59%**, **E1 ProtA=19.70%**. **Δlp(ProtB)=23.76−29.35=−5.59pp → "Bigger is WORSE"** (Δ≤−1.5pp, σ=0.04≪|Δ|). ProtA confirms: Δ=−4.11pp same direction. ⚠️ **该结论已被 2026-10-09⑨ 作废**。✅ EXPERIMENTS_VISION.md §7 results section added. ✅ Both arms no collapse (C1<0.5, C2_gap>0, C4=OK throughout 187k steps).
- [22:19] **🔁 scaling fair rerun — CODE READY + SMOKE_COS VERIFIED → LAUNCHING FULL RUN**: ✅ `r9_train.py` cosine support: added `--scheduler {const,cosine}` (default=const) + `--min-lr` (default=5e-5); `lr_at` now: warmup→cosine(`min_lr + 0.5*(lr-min_lr)*(1+cos(π*(s-w)/(steps-w)))`) or const; `lora_lr_at` synced; lr 4-point self-check printed to train.log; `[start]` line includes `scheduler=`/`min_lr=`; ckpt config saves scheduler/min_lr. ✅ `run_scaling_experiment.sh` new modes: `snapshot_gpic`→`data_snapshot_20261009.txt` (7437 GPIC tars frozen), `smoke_cos` (30-step×2 arms, lr self-check + shard parity check), `e1fair`/`e2fair`/`bothfair` (new dirs `scaling_E{1,2}fair_*`, old dirs NOT overwritten, `--lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --steps 187101`). ✅ py_compile + bash -n both pass. ✅ **smoke_cos PASSED**: E1fair(w512,126.8M) exit 0 steady_img_s=4268, E2fair(w768,284.5M) exit 0 steady_img_s=4188. **total_shards=10787=10787** (✅ shard parity, byte-identical data). lr self-check (verified for 187101-step real run): lr@0=0, lr@warmup(2000)=5e-4, lr@50%(93550)=2.79e-4, lr@last(187100)=5e-5, monotonic✅. GPU12_ALLOC.md申请区状态更新为✅. ETA: E1fair~6.2h + E2fair~6.4h + eval~3.5h = ~16h. Next: launch `bothfair 187101` → commit+push. 📦 体积：TASK=32.1KB / MEMORY=check after edit
- [23:50] **🔁 scaling fair rerun — E1fair RUNNING ~19% + watcher conflict FIXED + ⛔ banner + pre-reg**: ✅ E1fair via `bothfair` mode (PID 2670216) at step~35400/187101 (~19%), ~4900 img/s, loss~0.27, C1=0.42 C2_gap=+0.18 C4=OK (no collapse), lr=4.66e-04 (cosine active). ckpts @step10000/20000/30000 saved. ✅ lr self-check re-verified in train.log. ✅ **KILLED redundant e2fair_watcher.sh** (PID 1652207) — `bothfair` already chains E1→eval→E2→eval; the watcher would have **double-launched E2fair** → GPU conflict (8-card collision). ✅ ⛔ banner added to `report_vision_aimv2_scaling.html` (red gradient box at top of body). ✅ EXPERIMENTS_VISION.md §8 pre-registration written (§8.1: config table + lr trajectory + [start] line + judgment criteria + schedule comparison; §8.2: results placeholder). ETA: E1fair done ~04:15 Oct10 → E2fair ~6.4h → eval ~3.5h → all done ~17:40 Oct10. 📦 体积：TASK=32.1KB / MEMORY=~26.5KB（均≤32KB ✅）
- [00:35 Oct10] **🔁 scaling fair rerun — E1fair health check ~29%**: ✅ E1fair at step~54210/187101 (~29%), ~4900 img/s, loss~0.45, C1=0.49 C2_gap=+0.19 C4=OK (no collapse), lr=4.17e-04 (cosine decaying correctly from 5e-4 peak). ckpts @step10000/20000/30000/40000/50000 saved (487MB each, 2.4GB total). ✅ lr self-check from real run: `lr@0=0, lr@warmup(2000)=5e-4, lr@50%(93550)=2.79e-4, lr@last(187100)=5e-5, monotonically decreasing OK`. ✅ total_shards=10787 in [start] line. ✅ bothfair (PID 2670216, etimes~7788s) running correctly. ✅ ⛔ banner verified on report (lines 41-44). ✅ §8.2 updated with current progress. All 8 GPU 16.5GB/card 59-93%util. ETA: E1fair done ~05:40 → E1 eval ~3.5h → E2fair ~5.2h → E2 eval ~3.5h → all done ~18:00 Oct10. 📦 体积：TASK=32.1KB / MEMORY=26.6KB（均≤32KB ✅）
- [01:20 Oct10] **🔁 scaling fair rerun — E1fair health check ~39%**: ✅ E1fair at step~73500/187101 (~39%), ~5200 img/s avg (range 3411-5979 NFS fluct), loss~0.26 (↓ from ~0.45@29%), C1=0.47 C2_gap=+0.19 C4=OK (no collapse), lr=3.54e-04 (cosine decaying correctly). ckpts @step10000-70000 saved (7 ckpts, 3.4GB total). ✅ 245 PROBE events ALL C4=OK, 0 fusing. ✅ bothfair (PID 2670216, etimes~10404s ~2.9h) running. ✅ GPIC grew 7437→7445 since snapshot → confirms snapshot was necessary. ETA: E1fair done ~04:30 → E1 eval ~3.5h → E2fair ~6h → E2 eval ~3.5h → all done ~17:30 Oct10. 📦 体积：TASK=32.1KB / MEMORY=26.7KB（均≤32KB ✅）

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
