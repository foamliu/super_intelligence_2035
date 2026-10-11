# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🆕 **2026-10-10 晚（运维直令 · 最高优先）**：外部评审质疑 E1fair ProtB=62.34% 偏低 → 运维下发 ③→①→②→④ 顺序指令。**③ 口径修订**（✅ DONE）+ **① 同模型 zero-shot eval**（✅ DONE: E1fair 34.10%, E2fair 35.45%）+ **② k-NN probe 对照**（✅ DONE: k=20→37.68%）+ **变体实验 V2(Muon)→V3(全量数据)→V1(分辨率暂缓)**。
> 🔴 **V2 Muon COLLAPSED at ALL tested LRs** (2026-10-11): lr=5e-4 collapsed@step2100 (C1→0.99), lr=1e-4 collapsed@step4200 (C1→0.9569). 14 PROBE points show monotonic C1 rise (0.18→0.96, zero reversals). Root cause: Newton-Schulz orthogonalization amplifies contrastive collapse mode. AdamW's per-parameter adaptive scaling naturally damps this. ❌ **Muon incompatible with AIMv2-style contrastive+reconstruction objective**. C2 guard bug also found & fixed (`gap<=0.005`→`abs(gap)<=0.005`, r9_train.py:909). Full collapse analysis in `EXPERIMENTS_VISION.md §9.2`.
> ✅ **V3 Full GPIC Data TRAINING HEALTHY** (02:06 Oct 11 launch): 230,598 steps (1 epoch of 118.1M pairs), AdamW, same fair recipe. Screen `v3_fulldata`. **Step ~213.0k/230.6k (~92.4%)**, loss=0.13-0.31, C1=0.54, C2_gap=+0.19, ~2000-4000 img/s (NFS varying), lr=5.65e-05 (cosine active). ETA ~12:50 Oct 11 (~1h remaining). 21 checkpoints saved (step 10k–210k). **No collapse** — C1 oscillating 0.52-0.55 (stable, no monotonic rise), loss_ema ~0.16, C4=OK all 700+ PROBE points.
> ✅ **V3 eval watcher running** (`v3_eval_watcher.sh`, PID 1928152, ~9h old): monitors training, auto-runs ProtB(3 seeds)+ProtA+zero-shot+k-NN when done. Log: `/tmp/v3_eval_watcher.log` (last: step 212610 at 11:47).
> ✅ **④ epoch scaling pre-registered** in `EXPERIMENTS_VISION.md §9.4`: 2ep(374,202 steps) first, 4ep(748,404) if 2ep≥70%. Pending V3 eval completion.
> ✅ **①② results documented** in `EXPERIMENTS_VISION.md §9.6`: ① zs pathway (ReadoutHead→768-d→cosine sim with frozen CLIP text tower), E1fair zs=34.10%, E2fair=35.45%, lp−zs=+28pp. ② k-NN k=20=37.68%. **② gap**: ×5 epochs probe + wd/LR sweep NOT yet run (GPU blocked by V3) — pending after V3 completes.
> ✅ **③ 参照系说明 section ADDED** (2026-10-11 11:14): `EXPERIMENTS_VISION.md §8.3` — BaiZe internal protocol (ProtB/ProtA) labeling rules, 不可比原因逐条 (objective/data/text-tower/protocol/scale), 可比范围表, 清理记录. Closes ③ gap (previous wake marked DONE but 参照系 section was missing).

| 字段 | 值 |
|:---|:---|
| PHASE | 🔄 **V3 full data training step ~213.0k/230.6k (~92.4%), healthy**. Chained watcher `post_v3_chain.sh` (PID 117389) running: auto-runs ② ×5 probe → ④-2ep train → ④-2ep eval after V3. V2 Muon ❌ COLLAPSED. ③ 参照系说明 added to EXPERIMENTS_VISION.md §8.3. All automation scripts verified end-to-end. **Next**: collect automated results from /tmp/post_v3_chain.log. |
| WAITING | 1（🔄 V3 training ~92.4%, ETA ~12:50 Oct 11. Chained watcher runs ② probe → ④-2ep train → eval automatically. Next wake: check /tmp/post_v3_chain.log.） |
| ERROR_COUNT | 12（①~⑨ 同前 ⑩ V2 Muon lr=5e-4 collapse ⑪ C2 guard bug ⑫ V2 Muon lr=1e-4 collapse@step4200） |
| BUDGET_USED | ~740 GPU·h (V3 ~90 GPU·h consumed so far, ④-2ep ~80 GPU·h queued) |
| 更新 | **2026-10-11 11:49（V3 health check step ~213.0k ~92.4%)**: V3 step 213040/230598 (~92.4%), loss=0.13-0.31, C1=0.5406, C2_gap=+0.1902, throughput 2000-4000 img/s (128-245 ms/iter, NFS varying), lr=5.65e-05 (cosine), no collapse. 21 checkpoints (10k-210k, 510MB each). All 8 GPUs 61-81% util, 16.5GB/81.5GB mem, temps 40-45°C. Latest PROBE step213000: C1=0.5406, C2_gap=+0.1902, loss_ema=0.1620, C4=OK. 700+ PROBE points total, all C4=OK. C1 stable 0.52-0.55 over last 10 PROBE points (no monotonic rise = no collapse). Watchers: v3_eval_watcher (PID 1928152, ~9h old, last step 212610@11:47) + post_v3_chain (PID 117389, ~6.5h old) both alive. Rate ~296 steps/min → remaining ~17.6k steps → ETA V3 ~12:50 Oct 11. Full chain ETA: V3 ~12:50 → eval ~3.5h → ② ~1h → ④-2ep ~10h → eval ~3.5h ⇒ ④-2ep results ~Oct 12 ~07:00. 📦 体积：TASK=31.6KB / MEMORY=29.4KB（均 ≤32KB ✅, 无需归档） |
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

## 🗣️ 运维问答 · 2026-10-10（下一步工作建议）

> 回应运维指令 2026-10-10「询问 vision，对于下一步工作，有什么建议」。基于当前状态：E1fair ProtB=62.34±0.01%，scaling fair Δlp=+0.17pp（不可分辨），zs=34.10%，k-NN=37.68%。按价值排序。

### 1. ④ Epoch 缩放（最有决策价值）
- **问题**：62.34% 是预算不足还是特征质量天花板？
- **依据**：E1fair 1 epoch ProtB=62.34%；R12 3-epoch→20.27%（但旧 recipe）；k-NN=37.68% vs lp=62.34%→probe 欠拟合不大；zs=34.10% < lp=62.34%→文本对齐有增益但未饱和。
- **设计**：在 E1fair 基础上补 2 epoch（374,202 步）和 4 epoch（748,404 步），同数据/目标/schedule。8 卡，2ep≈10h，4ep≈20h。
- **判据**：2ep ≥70% → 预算不足；4ep ~63% 横盘 → 特征/目标函数问题。
- **成本**：2ep ~80 GPU·h / 4ep ~160 GPU·h。
- **依赖**：V1 Muon + V2 全量数据完成后排 GPU 档期。
- **风险**：NFS 波动影响吞吐；多 epoch 可能过拟合（R12b 2ep < R11-G 1ep 先例）。

### 2. V2 全量数据（已排期 · 第二优先）
- **问题**：GPIC 全量 8000 tar（vs snapshot 7437 tar）+ CC12M + Amshaker 是否提升 lp？
- **依据**：E1fair 用 total_shards=10787（~95.8M 对）；GPIC 全量 8000 tar→100.3M 对（+4.5M）。R12b「更多 unique 数据 ≠ 更高 lp」（69.7M 2ep=18.81% < R11-G 18.5M 1ep=19.76%）。
- **设计**：1 臂，全量 GPIC 8000 tar 快照，步数按数据量计算（~230k 步），其余与 E1fair 逐字节相同。8 卡，~12h。
- **判据**：Δlp vs baseline |Δ|≥1.5pp 可分辨。
- **成本**：~96 GPU·h / ~12h 墙钟。
- **依赖**：V1 Muon 完成（共用 .12 8 卡，串行）。
- **风险**：同时变「数据量+步数」，结论只能表述为「全量配方 vs baseline」。

### 3. (a) Stage (iv) MLLM 对齐前置
- **问题**：当前最佳 ckpt（E1fair）能否直接用于 MLLM，需要哪些准备？
- **依据**：论文 §VI-C 已声明「Stage (iv) revisits visual-token count」；R11-L2 LoRA 解冻未翻盘(Δ−0.30~−0.80)。
- **设计**（纯 CPU/轻 GPU）：① projector 设计文档（linear/MLP/Q-Former 对比）；② 特征缓存管线（`extract_features_cache.py`）；③ 冻结/解冻评测框架（`eval_mllm_readiness.py`）；④ GPIC layout 标注配对脚本。
- **判据**：产出设计文档 + 可运行脚本（不占 8 卡训练）。
- **成本**：~2 天纯写作/代码，~0 GPU·h。
- **依赖**：无（可与 V1/V2 并行）。
- **风险**：低。

### 4. (e) 论文呈现（纯写作）
- **问题**：scaling 公平性翻案（Δlp=−5.59pp→+0.17pp）如何在 §VI 呈现？
- **依据**：`report_vision_scaling_fair.html`（Δlp=+0.17pp 不可分辨）；旧报告 ⛔ 横幅已加。
- **设计**：① §VI-B 加「schedule 敏感性」教训段（旧 lr=3e-3/warmup20 → 新 5e-4/warmup2000/cosine）；② 重拟合 scaling 曲线（若 ④ 有数据）；③ Limitations 加单预算点声明。
- **判据**：LaTeX 编译 0 err，数字与报告一致。
- **成本**：~0 GPU·h，~半天写作。
- **依赖**：④ epoch 缩放数据（若有）可增强结论。
- **风险**：低。

### 5. (b) w384 AIMv2-style（可选 · GPU 空窗期）
- **问题**：AIMv2-style 在更小塔（w384, 71.5M）上是否更优？
- **依据**：R10 w384 InfoNCE lp=7.99%@15.36M 全宽度最高；R11-G AIMv2 w512 翻盘→19.76%。交叉点未验证。
- **设计**：1 臂 w384 AIMv2-style，30k 步，8 卡，~2h。
- **判据**：lp@30k ≥ 15.0% → w384 更优。
- **成本**：~16 GPU·h / ~2h。
- **依赖**：GPU 空窗期（V1/V2/④ 之后）。
- **风险**：若 w384 不优于 w512 → 负结果（仍有价值）。

### 6. (d) 224→336 分辨率（暂缓 · 用户令「明天再说」）
- **问题**：336/16=576 patch 对版图 VQA 是否必要？
- **依据**：官方 OV2 用 patch14/336=576 token；我们 224/16=196。BP-3 未测高分辨率 dense。
- **设计**：1 臂 336/16 AIMv2-style，187k 步，pos-emb 重建，~2.25× 计算。8 卡，~20h。
- **判据**：Δlp vs baseline ≥1.5pp → 高分辨率有益。
- **成本**：~160 GPU·h / ~20h。
- **依赖**：用户批准（暂缓中）。
- **风险**：pos-emb 插值不稳定；计算量大。

### 7. (c) C1-lp 背离（低优先 · 可选）
- **问题**：降低 contrast weight 是否系统性提升 lp？
- **依据**：mask-ratio arm 0.3 C1↓但 lp≈；weight-ratio 0.5:1 C1 最低但 lp 最高。
- **设计**：contrast_weight {0.1,0.25,0.5} × 1 seed，30k 步。
- **判据**：lp 倒 U 峰值 = 最优 trade-off。
- **成本**：~48 GPU·h / ~6h。
- **依赖**：GPU 空窗期。
- **风险**：已有 2 点数据，趋势不明朗。

> **总结排序**：④ epoch 缩放 > V2 全量数据 > (a) MLLM 前置（CPU 并行）> (e) 论文（CPU 并行）> (b) w384 > (d) 336 > (c) C1-lp。前 4 项可并行（④/V2 占 GPU，a/e 纯 CPU）。


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

- [2026-10-09 晚 · 运维] 🔁 **scaling 公平性重跑令下发** — 已归档至 `daily-memories-vision/2026-10-09.md`。配方 `warmup=2000/lr=5e-4/cosine/min_lr=5e-5`，两臂同数据。

> 📦 R12b/scaling 早期流水(10-06~10-07)已归档 → daily-memories-vision/2026-10-{06,07}.md
> 📦 7 条 scaling 流水(10-10 00:35~05:55)已归档 → daily-memories-vision/2026-10-10.md
> 📦 10 条 scaling fair rerun 巡检/报告(10-10 07:44~20:28)已归档 → daily-memories-vision/2026-10-10.md。**结论**：E1fair ProtB=62.34%, E2fair ProtB=62.51%, Δlp=+0.17pp indistinguishable。

> 📦 4 条早期流水(10-11 00:15~03:27)已归档 → daily-memories-vision/2026-10-11.md「Archived from MEMORY_VISION.md」节
> 📦 3 条巡检流水(10-11 04:00~05:20)已归档 → daily-memories-vision/2026-10-11.md（V3 step 52.5k~84.7k health checks + automation scripts created）

> 📦 3 条 V3 巡检流水(10-11 06:25~08:14, step 46%~61%)已归档 → daily-memories-vision/2026-10-11.md。**结论**：V3 healthy, no collapse, all automation verified end-to-end.

> 📦 2 条 V3 巡检流水(10-11 07:39~08:47, step 57%~67%)已归档 → daily-memories-vision/2026-10-11.md。**结论**：V3 healthy, C1 spike@153300 recovered, all automation deep-verified.

- [09:22 Oct11] **V3 health check step ~166.5k (~72%) · NFS contention eased, throughput up**: V3 step 166530/230598 (~72%), loss=0.10-0.24, C1=0.5292, C2_gap=+0.1901, loss_ema=0.1632, no collapse. 16 checkpoints (10k-160k, 510MB each). Throughput 5100-5900 img/s (88-100 ms/iter — NFS contention eased significantly vs 08:47's 118-269 ms/iter). lr=1.32e-04 (cosine). All 8 GPUs 68-83% util, 16.5GB/81.5GB mem, temps 43-48°C. Latest PROBE step166500: C1=0.5292, C2_gap=+0.1901, C4=OK. C1 stable 0.52-0.56 across last 10 PROBE points (163800→166500), zero monotonic rise. 556+ PROBE points total, all C4=OK. Watchers: v3_eval_watcher (PID 1928152, ~6.5h old, last poll step166400 at 09:22) + post_v3_chain (PID 117389, ~4h old) both alive. Rate ~330 steps/min → remaining ~64k steps → ETA V3 ~12:35 Oct 11 (~3.2h). Full chain ETA: V3 ~12:35 → eval ~3.5h → ② ~1h → ④-2ep ~10h → eval ~3.5h ⇒ ④-2ep results ~Oct 12 ~06:30. 📦 TASK=32.4KB / MEMORY=31.9KB（均在限内）.
- [10:31 Oct11] **V3 health check step ~187.5k (~81%) · healthy, all watchers alive**: V3 step 187490/230598 (~81%), loss=0.08-0.21, C1=0.5164, C2_gap=+0.1948, loss_ema=0.1150, no collapse. 18 checkpoints (10k-180k, 510MB each). Throughput 1800-4400 img/s (117-280 ms/iter, NFS varying). lr=8.84e-05 (cosine). All 8 GPUs 67-80% util, 16.5GB/81.5GB mem. Latest PROBE step187200: C1=0.5164, C2_gap=+0.1948, C4=OK. 600+ PROBE points total, all C4=OK. C1 stable 0.49-0.52 (no monotonic rise). Watchers: v3_eval_watcher (PID 1928152, ~8.4h old, last step 186380@10:27) + post_v3_chain (PID 117389, ~5.2h old) both alive. Rate ~300 steps/min → remaining ~43k → ETA V3 ~12:55 Oct 11. Full chain ETA: V3 ~12:55 → eval ~3.5h → ② ~1h → ④-2ep ~10h → eval ~3.5h ⇒ ④-2ep results ~Oct 12 ~07:00. 📦 TASK=31.6KB / MEMORY=32.0KB（均在限内）.
- [11:49 Oct11] **V3 health check step ~213.0k (~92.4%) · healthy, ~1h to completion**: V3 step 213040/230598 (~92.4%), loss=0.13-0.31, C1=0.5406, C2_gap=+0.1902, loss_ema=0.1620, no collapse. 21 checkpoints (10k-210k, 510MB each). Throughput 2000-4000 img/s (128-245 ms/iter, NFS varying). lr=5.65e-05 (cosine). All 8 GPUs 61-81% util, 16.5GB/81.5GB mem, temps 40-45°C. Latest PROBE step213000: C1=0.5406, C2_gap=+0.1902, C4=OK. 700+ PROBE points total, all C4=OK. C1 stable 0.52-0.55 (no monotonic rise). Watchers: v3_eval_watcher (PID 1928152, ~9h old, last step 212610@11:47) + post_v3_chain (PID 117389, ~6.5h old) both alive. Rate ~296 steps/min → remaining ~17.6k → ETA V3 ~12:50 Oct 11 (~1h). Full chain ETA: V3 ~12:50 → eval ~3.5h → ② ~1h → ④-2ep ~10h → eval ~3.5h ⇒ ④-2ep results ~Oct 12 ~07:00. 📦 TASK=31.6KB / MEMORY=29.4KB（均 ≤32KB ✅）.

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
