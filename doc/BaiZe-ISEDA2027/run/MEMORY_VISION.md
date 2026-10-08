# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🟧 **🔬 Scaling 对比实验进行中（⑥修订E2→w768）** — 运维指令 2026-10-08⑤→⑥(用户裁定): E1(OV2 w512/d30,126.78M,224/p16) vs **E2改为同族OV2 w768/d30(284.54M,224/p16)** — 旧E2(官方304M/336/p14)作废(4变量同变). 同AIMv2/数据94.9M/1epoch/bs512. ✅ E1训练中(step~14k/187k,~5100img/s,loss↓,无坍缩). ✅ 脚本已修(run_e2→w768/d30/p16/224). ✅ 预注册已更新(⑥). ✅ e2_watcher.sh已启动(E1完后自动跑E2 smoke+训练). |
| WAITING | 1（🔬 scaling 实验在跑 — E1训练中(~5h剩余) → E2 smoke+训练(~5.6h) → Protocol B eval 3 seeds → HTML报告. ETA total ~11h+eval. |
| ERROR_COUNT | 6（①~⑤ 同前 ⑥ AIMv2.forward() 不支持 return_patch → 已加 return_patch+causal 参数修复） |
| BUDGET_USED | R2–R12 ≈215 + R12b(106.4) + lp bridge(5.8) + mask-ratio(78.4+0.5) + weight-ratio(~65.4+0.5) + ④ AIMv2 AR Arm B(2.1) + Arm B-hybrid(~24) ≈ **累计 ~498 GPU·h** + scaling E1(~8 GPU·h so far) |
| 更新 | **2026-10-08 20:14（⑥ E2变更执行完毕+push✅）**: ✅ 读到运维指令⑥(E2作废官方304M→改同族w768/d30/284.54M,只差宽度). ✅ E1训练中(step~18k/187k,~5100img/s,loss 2.6,无坍缩)→不动. ✅ run_scaling_experiment.sh已修: run_e2()改为--tower openvision2 --width 768 --depth 30 --resolution 224 --patch 16. ✅ 预注册EXPERIMENTS_VISION.md已更新(⑥修订,保留历史). ✅ e2_watcher.sh启动(PID 161134,等E1完后自动跑E2 smoke→训练). ✅ ④估算已答(MEMORY新增⏱️节,smoke实测5.2-9.1h/epoch)+④块归档→ARCHIVE. ✅ commit ee1a2bfd push✅. 📦 体积：TASK=31.2KB / MEMORY=31.3KB（均≤32KB✅, 归档④~1.9KB→ARCHIVE_OPERATOR_VISION.md）· *[更早见 daily-memories-vision/2026-10-08.md]* |
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

> 📦 15 条 R12b 巡检流水(10-06 12:33–23:57)已归档 → daily-memories-vision/2026-10-06.md（2026-10-07 13:00 滚动）
> 📦 5 条 R12b 巡检#17-19 + 完成 + eval(10-07 00:33–03:07)已归档 → daily-memories-vision/2026-10-07.md（2026-10-08 03:23 滚动）
- [02:23→03:07] *(R12b 训练完成 + eval完成 + lp协议A/B桥接启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp_max=18.81%, R12b<R11-G, lp bridge PID 1499158 启动）
- [03:20→23:25] *(lp bridge 完成 + mask-ratio 消融 ALL DONE + 报告HTML交付 + weight-ratio arm1 DONE + arm2 启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp bridge Δlp≈+10pp 3ckpts极稳定; mask-ratio 0.6最优13.49%倒U; report_vision_mask_ratio.html 34.3KB commit ee9db3ca; arm1 cw1_plw2 DONE C1=0.3546）
- [22:46] *(arm1✅DONE + 脚本异常退出→恢复)* — 已归档至 daily-memories-vision/2026-10-07.md（arm1 cw1_plw2 DONE@22:11, C1=0.3546, 脚本crash→恢复PID 3214830）
- [02:48] **③ weight-ratio arm3巡检#2（CPU-only, 不打断训练）**: PID 3214830健康(ppid=1, etimes~14548s~4h). 🚀 **arm3 cw0p5_plw1(0.5:1) RUNNING step~27300/30k~91%**: loss~1.5-1.8, contrast~2.8-3.2, patch_mse~0.17-0.19, C1 probes: 0.3856@26400→0.3650@26700→0.3367@27000→0.3510@27300(无坍缩, C2_gap~+0.12, C4=OK). **C1 从 11700 低谷(0.2924) 回升到 26400(0.3856) 再回落到 27300(0.3510) → 非单调但稳定, C4=OK 无坍缩**. 2ckpts✅(step10k@01:33+step20k@02:16). img/s~2100-2600(NFS波动, ms/iter~210-240), 8GPU 16.5GB/卡 0-100%util. arm3 ETA~02:55(剩~2700步), arm4(2:1) pending, all+eval ETA~05:10. ⚠️ **git fetch FAILED: Network unreachable(github.com:443)** — repo synced(HEAD=origin/main=5a5ac6c0), push将重试. 📦 体积：TASK=31.2KB / MEMORY=~31.2KB（均≤32KB✅, 无需归档）.

- [07:53] **④ 官方 AIMv2 AR 范式 Arm B 开跑**: ②③消融全部完成, 8GPU全空闲(nvidia-smi 4MiB/卡). 代码已就绪(models.py: OpenVision2.forward(causal=True)+ARTextDecoder(weight-tied,trainable embed)+PatchPredictor; r9_train.py: --loss aimv2_ar 分支实现 causal ViT→next-patch pixel_loss(shift-by-1)+text AR cap_loss(cross-attn→causal patches)+total=cap+0.4*pixel, 无InfoNCE). 脚本 run_aimv2_ar.sh 已就绪(smoke→30k→eval). 🚀 **smoke test✅**(30步/9.1s/exit0): steady_img_s=2069.5, loss=7.14→6.66(cap=6.77→6.29,pixel=0.94→0.92), 无坍缩(fused=False). Arm B params~203.7M(trunk126.8M+ARdec76.2M+pred0.66M) vs Arm A~127.4M(+67M). 🚀 **30k full run START**@07:58: step100/30000, loss=5.94(cap=5.63,pixel=0.76), ~2185 img/s, 8GPU 22.5GB/卡 48-85%util. 30k ETA~2.1h(~10:00), <3h✅. 脚本自动: 30k→save-every 10000(3ckpts)→IN-1k eval(r8_eval_in1k.py). ⚠️ git fetch FAILED(Network unreachable), repo synced(HEAD=origin/main), push将重试. 📦 体积：TASK=31.9KB / MEMORY=17.2KB（均≤32KB✅, 无需归档）.
- [08:10] **🔴 ④ Arm B 坍缩@step600 + 🟢 hybrid 追加实验 RUNNING**: 🔴 **Arm B (pure AR 无 InfoNCE) 坍缩**: C1=0.8649@300→0.9731@600, fused=True, loss在降(cap 6.77→5.08, pixel~0.73, C4=OK)但特征坍缩. 预注册判据命中"AR无对比项坍缩". **DDP死锁bug**: rank0 fuse→break, 其他rank仍在forward→NCCL hang(216s+), 已kill. **bug修复**: r9_train.py 加 `dist.broadcast(fused_flag, src=0)` 让所有rank同步退出. **关键对比**: R11-H(双向+无InfoNCE)C1=0.43✅不坍缩 vs Arm B(因果+无InfoNCE)C1=0.97🔴坍缩 → **causal比bidirectional更易坍缩**. 🟢 **Arm B-hybrid (AR+InfoNCE) RUNNING@08:13**: 代码改动 r9_train.py aimv2_ar 分支新增 `--contrast-weight` 支持(用causal pooled算InfoNCE). 新脚本 run_aimv2_ar_hybrid.sh(`--contrast-weight 1.0 --c2-collapse-guard 1`). smoke✅(30步, contrast=6.10, exit0). **step300探针: C1=0.2480(健康!), C2_gap=+0.096, C4=OK, contrast=5.10(cap=5.04,pixel=0.73)**. 4臂对比表已写入EXPERIMENTS_VISION.md. 30k ETA~10:45. 📦 体积：TASK=31.9KB / MEMORY=~18KB（均≤32KB✅）.
- [00:01] **③ weight-ratio arm2巡检#2**: PID 3214830健康(ppid=1, etimes~4490s~75min). **arm 2/4 cw1_plw0p5(contrast=1,patch=0.5) 运行中** step 18450/30000 ~61.5%: loss~3.1-3.8, contrast~2.9-3.7, patch_mse~0.28-0.36, C1 probes: 0.3755@17700→0.4043@18000→0.3934@18300(无坍缩, C2_gap~+0.11, C4=OK). step10k ckpt✅(vision_step10000.pt, 510MB, saved 23:25). img/s 2000-5100(NFS波动, ms/iter 100-248), 8GPU 16.5GB/卡, util 44-77%. arm2 remaining ~11550步 ETA~00:47, 2 arms remaining(0.5:1→2:1), all+eval ETA~04:30-05:15. ✅ git synced(fetch✅with proxy, HEAD=origin/main=dd8874ad, 0新vision提交, 无新运维指令). 训练健康, 无需干预. 📦 体积：TASK=31.2KB / MEMORY=30.5KB（均≤32KB✅, 无需归档）.
- [09:05] **④ Arm B-hybrid 巡检#1 + mask-ratio报告验证 + TASK归档（CPU-only, 不打断训练）**: 🟢 **Arm B-hybrid RUNNING step 9350/30000 ~31%**: PID 2382170健康(ppid=1, 8 ranks alive). C1 probes: 0.4863@8100→0.4796@8400→0.5464@8700→0.5089@9000→0.4287@9300. **C1 振荡 0.43–0.55, 高于 Arm A 基线~0.33 但 C4=OK C2_gap~+0.045 无坍缩** — causal+InfoNCE 的对比对齐度比 bidirectional+InfoNCE 更强, 但仍稳定. loss~10.7(contrast~5.78 cap~4.5 pixel~0.87, 降中). img/s~2330(ms/iter~215), 8GPU 22-45GB/卡 64-100%util. step10k ckpt 即将落盘(save-every 10000). ETA~09:45(剩~20650步~1.3h). ✅ **mask-ratio报告验证**: report_vision_mask_ratio.html 34.3KB, 8节+2SVG, commit ee9db3ca, 已在origin/main — 运维指令2026-10-07③已交付. ✅ **TASK.md归档**: 2个已闭合块(2026-10-07③+②)原文搬入ARCHIVE_OPERATOR_VISION.md+留指针, 34872→31766B(≤32KB✅). ✅ git fetch✅with proxy, repo synced(HEAD=origin/main). 无新运维指令(2026-10-08全线总结报告块=等hybrid完成后再写). 📦 体积：TASK=31.8KB / MEMORY=~19KB（均≤32KB✅, 归档~3KB→ARCHIVE）.
- [09:44] **④ Arm B-hybrid 巡检#2 + TASK.md归档(lp协议块) + 论文数据准备（CPU-only, 不打断训练）**: 🟢 **Arm B-hybrid RUNNING step 19200/30000 ~64%**: C1 probes: 0.4076@18000→0.4021@18600→0.4993@18900→0.5087@19200, 振荡0.38-0.57, C4=OK C2_gap~+0.05 无坍缩. loss~10.3(contrast~5.56 cap~3.6-4.7 pixel~0.81, 降中), ~2300 img/s. step10k ckpt✅(vision_step10000.pt 814MB). step20k ckpt即将落盘. ETA~10:24 + IN-1k eval ~60-80min. ✅ **TASK.md归档**: lp协议块(2026-10-06, 已闭合: report_vision_lp_protocol.html已交付21.2KB)原文搬入ARCHIVE_OPERATOR_VISION.md+留1行指针, 34435→30325B(≤32KB✅). ✅ **论文数据准备**: 已读6_vision_encoder.tex(183行)结构+EXPERIMENTS_VISION.md关键段. 已识别需补充论文内容: ①mask-ratio消融(倒U形0.6最优) ②weight-ratio消融(无翻盘,patch-heavy更宽容) ③InfoNCE防AR坍缩(④待完成) ④R13官方OV2 79.81% ⑤更新结论段. ✅ git fetch✅with proxy, repo synced. 📦 体积：TASK=30.3KB / MEMORY=~20KB（均≤32KB✅, 归档~4KB→ARCHIVE）.
- [12:34] **全线收敛确认 · 收尾巡检（CPU-only, 无训练在跑）**: ✅ **所有任务已完成**: R2–R14 全部 closed. ④ Arm B-hybrid=lp@30k 1.37% (Δ−12.1pp vs baseline 13.49%), InfoNCE 防 AR 坍缩验证✅. 论文 6_vision_encoder.tex + main.pdf (11p 0err) 已 commit (6f2baa2b). 全线总结报告 report_vision_encoder_final.html (10节/4SVG/28.6KB) 已 commit (67a306f8). ✅ **git synced**: fetch✅(w/proxy), HEAD=origin/main=1ca21758, 0 ahead/0 behind. ✅ **GPU**: 8×H100 全部 idle (4MiB/卡, 0% util). ✅ **5份报告均在盘+tracked**: report_vision_encoder_final.html(28.6KB)+mask_ratio(34.3KB)+lp_protocol(21.2KB)+lp_eval(27KB)+aimv2_impl(30.8KB). 无新运维指令（2026-10-08 两块=论文更新+全线总结报告，均已交付）. **视觉编码器线全线收敛，待运维审阅+派新任务**. 📦 体积：TASK=30.3KB / MEMORY=~21KB（均≤32KB✅）.
- [13:09] **唤醒巡检 · 全线仍收敛（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), HEAD=origin/main=088442ca, 0 ahead/0 behind — **无新运维指令**. ✅ GPU 8×H100 全 idle (4MiB/卡). ✅ 交付物均完好: main.pdf(358KB)+6_vision_encoder.tex+report_vision_encoder_final.html(28.6KB)+4份专项报告. ✅ 体积: TASK=30.3KB / MEMORY=~21KB（均≤32KB✅）. **视觉编码器线 R2–R14 全线收敛，WAITING=1 待运维派新任务**.
- [13:43] **唤醒巡检 · 全线仍收敛（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind — **无新运维指令**. ✅ GPU 8×H100 全 idle. ✅ 交付物完好: main.pdf(358KB)+6_vision_encoder.tex+report_vision_encoder_final.html(28.6KB)+4份专项报告. ✅ 体积: TASK=30.3KB / MEMORY=22.2KB（均≤32KB✅）. **视觉编码器线 R2–R14 全线收敛，WAITING=1 待运维派新任务**.
- [14:16] **唤醒巡检 · 提交未归档的归档变更 + 心跳同步（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind — **无新运维指令**. ⚠️ 发现工作区有未提交的归档变更: BAIZE_VISION_TASK.md（+Best Practices三节 BP-1/2/3 + 归档 2026-10-08①②块→指针, 34KB→28.9KB）+ ARCHIVE_OPERATOR_VISION.md（+67行接收归档块）— 均为上一轮 agent 归档工作未提交. ✅ GPU 8×H100 全 idle. ✅ 体积: TASK=28.9KB / MEMORY=22.6KB（均≤32KB✅）. **视觉编码器线 R2–R14 全线收敛，WAITING=1 待运维派新任务**. 📦 体积：TASK=28.9KB / MEMORY=22.6KB（均≤32KB✅）.
- [01:39] **③ weight-ratio arm2✅DONE + arm3巡检#1**: ✅ **arm2 cw1_plw0p5(1:0.5) DONE@00:48**: step30k, total=7383s, steady_img_s=2443.8, final_loss=3.5013, C1_final=0.3517, C1_peak=0.4176@19200, C2_gap=+0.1131, C4=OK(无坍缩), 4ckpts✅. arm2结果已写入EXPERIMENTS_VISION.md. 🚀 **arm3 cw0p5_plw1(0.5:1) RUNNING**: PID 3214830健康(ppid=1,~2.9h), step~11650/30k~39%, C1_peak=0.4304@2100(早现), C1_latest=0.2924@11700(下降趋势但C4=OK), C2_gap~+0.133, loss~1.7-1.8, img/s~2200-2700, 8GPU 16.5GB/卡 55-67%util, step10k ckpt✅. arm3 ETA~02:40, 1 arm remaining(2:1), all+eval ETA~05:10. ⚠️ **git fetch FAILED: Network unreachable(github.com:443)** — HEAD=origin/main=1a36624d(synced), push将重试. 📦 体积：TASK=31.2KB / MEMORY=31.0KB（均≤32KB✅, 无需归档）.
- [15:10→16:10] *(AIMv2 专项报告补交付 + 补推确认 + 2 次巡检)* — 已归档至 `daily-memories-vision/2026-10-08.md`（report_vision_aimv2_official_vs_ours.html 23.2KB 交付 + git 补推确认 + 交付物完好）
- [16:44] **唤醒巡检 · 全线仍收敛（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind. ✅ GPU 8×H100 全 idle. ✅ 交付物完好: main.pdf+6_vision_encoder.tex+6份HTML报告均在盘. ✅ 体积: TASK=28.9KB / MEMORY=25.6KB（均≤32KB✅）. **视觉编码器线 R2–R14 全线收敛, WAITING=1 待运维派新任务**.
- [17:20] **回答运维 2026-10-08③ · 下一步工作建议（CPU-only, 纯写作）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind. ✅ **运维指令 2026-10-08③ 已执行**：在 MEMORY_VISION.md 状态头下方新增「🗣️ 运维问答 · 2026-10-08③（下一步工作建议）」区（4 题 × 逐条回答 + 每条附实验依据）：① 未验证假设 4 条（w384 AIMv2 / C1-lp 背离 / R12b epoch-vs-unique / 高分辨率 dense）；② Stage iv 前置 5 项（projector/分辨率/冻结vs解冻/特征缓存/数据配对）；③ GPU 利用 3 候选（P1=w384 AIMv2 ~16h / P2=Protocol B 消融臂 ~6h / P3=336/16 ~24h）；④ 论文补充 5 项（Limitations/Protocol B 横比/R12b 发现/C1-lp 背离/Future Work）。✅ 纯写作不占 GPU。✅ GPU 8×H100 全 idle。📦 体积：TASK=30.8KB / MEMORY=31.5KB（均≤32KB✅, 归档 3 条旧流水→daily）.
- [18:00] **唤醒巡检 · 全线仍收敛（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind — **无新运维指令**. ✅ 运维 2026-10-08③ 已于 17:20 完成(commit 0bb4dc24). ✅ GPU 8×H100 全 idle (4MiB/卡, 0% util). ✅ 交付物完好: main.pdf+6_vision_encoder.tex+6份HTML报告均在盘. ✅ 体积: TASK=31.5KB / MEMORY=31.5KB（均≤32KB✅）. **视觉编码器线 R2–R14 全线收敛, WAITING=1 待运维派新任务**.
- [18:39] **唤醒巡检 + TASK 归档（CPU-only, 无训练）**: ✅ git fetch✅(w/proxy), 0 ahead/0 behind — **无新运维指令**. ✅ **3 个已闭合运维指令块原文归档→ARCHIVE_OPERATOR_VISION.md**（① 2026-10-08③ Q&A 下一步建议 → ② 2026-10-06 批准 AIMv2 官方 AR 范式+6点修订 → ③ 2026-10-06 队列裁定）, 各留 1 行指针. TASK 31.5KB→22.2KB(−9.3KB). ✅ GPU 8×H100 全 idle. ✅ 交付物完好: main.pdf+6_vision_encoder.tex+6份HTML报告. 📦 体积：TASK=22.2KB / MEMORY=31.6KB（均≤32KB✅, 归档~9KB→ARCHIVE_OPERATOR_VISION.md）.

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
