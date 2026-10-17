# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🆕 **2026-10-18 05:37（🔄 ArmB 训练监控 · wake #144）**：git pull up to date, 无新运维指令（顶部 12:4x「kill .12 pretrain→起 ArmB 4epoch」已于 wake #131/#132 执行完毕；.12 上 8 GPU 进程=**ArmB 训练非 pretrain**, pgrep baize_xmodel25_decay=空, 不杀）。✅ **ArmB 4-epoch 训练健康**：step **50360/57250(88.0%)**，loss~0.20(硬分片抖动非坍缩, contr~0.19 patch~0.016)，C1 0.77–0.89（正常），lr=1.34e-04(cosine→1e-4)，**0.87 it/s**(稳态)，8×H100 100% util/50.5GB/卡(peak=50.4GB 无OOM)，t=964.7min(16.1h)。✅ ckpt@50000(@05:28)+40000+latest.pt+open_clip_state_dict(598MB)+predictor+config.json 均在；checkpoint_30000 已自动删(keep-ckpts 2)。✅ grep error/traceback/oom/nan = **NONE**(仅 pynvml FutureWarning 良性)。✅ ArmA 中文报告+附录A(兼容性)/B(概念澄清)已交付(report_vision_armA_openclip_result_zh.html, wake#133)。✅ armB_protb_eval.py+run_armB_protb_eval.sh 就绪(OMP_NUM_THREADS=8 修复过订阅, 偏好 open_clip_state_dict.pt)。**ETA**: (57250−50360)/0.87≈**2.2h → ~07:50 10-18** 训完；+ProtB(3 seeds)1–2h ⇒ **~09:00–10:00 10-18**。下一步: 监控至 57250 → `run_armB_protb_eval.sh` → armB 中文报告。📦 体积：TASK=26.2KB / MEMORY=31.9KB。
 > 📦 2026-10-18 03:12（🔄 ArmB 训练监控 · wake #143）已归档 → daily-memories-vision/2026-10-18.md；**结论**：ArmB step42420(74.1%)健康, 0.86 it/s, ckpt@40000已存, ETA~08:00 10-18。
 >
 > 📦 2026-10-18 02:02（🔄 ArmB 训练监控 · wake #142）已归档 → daily-memories-vision/2026-10-18.md；**结论**：ArmB step38580(67.4%)健康, 0.86 it/s, ckpt@30000+20000已存, 硬分片抖动非坍缩, ETA~08:00 10-18。
> 📦 2026-10-18 00:50（🔄 ArmB 训练监控 · wake #141）已归档 → daily-memories-vision/2026-10-18.md；**结论**：ArmB step35440(61.9%)健康, 0.87 it/s, ckpt@30000已存, ETA~07:50 10-18。
> 📦 2026-10-17 23:37（🔄 ArmB 训练监控 · wake #140）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step31480(55.0%)健康, 0.87 it/s, ckpt@30000已存, ETA~07:50 10-18。
> 📦 2026-10-17 22:26（🔄 ArmB 训练监控 · wake #139）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step27540(48.1%)健康, 0.86 it/s, ckpt@20000+10000已存, ETA~08:00 10-18。
> 📦 2026-10-17 21:1x（🔄 ArmB 训练监控 · wake #138）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step23680(41.4%)健康, 0.85 it/s, ckpt@20000+10000已存, ETA~08:00 10-18。
> 📦 2026-10-17 19:5x（🔄 ArmB 训练监控 + ✅ ProtB eval 脚本就绪 · wake #137）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step20520(35.8%)健康, armB_protb_eval.py+run_armB_protb_eval.sh 交付(CPU单测3/3 PASSED), 0.88 it/s, ETA~07:30 10-18。
> 📦 2026-10-17 18:39（🔄 ArmB 训练监控 · wake #136）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step15960(27.9%)健康, 0.87 it/s, ETA~10-18 08:00。
> 📦 2026-10-17 14:5x~17:27（🔄 ArmB 监控 · wake #133~#135）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step4540→12120 健康, P1 ArmA 中文报告交付(commit 2f15f88e), 0.86 it/s 稳态, checkpoint_10000 已存。
>
> 📦 2026-10-17 13:3x（🔄 ArmB 改 4 epoch 重启 · wake #132）已归档；**结论**：4-epoch run(steps=57250)由 wake #132 启动(PID 1203148)，wake #133 确认健康运行中(step 4540)。
>
> 📦 2026-10-17 09:1x~12:4x（wake #128~#131: ArmA 训练完成154500步 + ProtB lp=58.03±0.02%/5-NN=53.98% + Stage(iv)报告闭环(da8e9cd1) + ArmB 3-epoch 启动后被 #132 改 4-epoch）已归档 → daily-memories-vision/2026-10-17.md。
>
> 📦 **改动清单 + 10-14~16 全天流水**（wake #106~#128, ArmA 起训/12集 eval/Stage-1/1.5/2/open_clip wrapper）已归档 → daily-memories-vision/2026-10-{14,15,16}.md + ARCHIVE_OPERATOR_VISION.md；**结论**：✅ ArmA 全链路完成, 改动清单(LPT/workers/cudnn/fused)已落地, 配方不变。
> ✅ **④-4ep 基线（COMPLETE）**: ProtB 67.05±0.02% / ProtA 56.70% / zs 40.64%/72.64% / k-NN 42.35%. final_loss=0.0805, C1=0.5932, 748,404 steps, 60,545s. VERDICT: MODERATE, DIMINISHING. 详见 EXPERIMENTS_VISION.md §9.5/§9.7.
> 📦 ④-2ep / V2 Muon / V3 / ② probe / ④-4ep评测（2026-10-11~13）已归档 → daily-memories-vision/2026-10-14.md + ARCHIVE_OPERATOR_VISION.md；**结论**：V2 Muon 坍缩❌；V3 不可分辨；② probe=ceiling；④-2ep MODERATE；④-4ep 67.05% 递减确认。
> ✅ **③ 参照系说明** in `EXPERIMENTS_VISION.md §8.3`: BaiZe internal protocol labeling rules, 不可比原因逐条.

| 字段 | 值 |
|:---|:---|
| PHASE | 🚀 **ArmB 4-epoch 训练运行中（wake #132 重启, PID 1203161, 10-17 13:31）**：open_clip ViT-B/16 + AIMv2-style dense(InfoNCE + masked-patch MSE)。step 38580/57250(67.4%) loss~0.35(硬分片抖动), 0.86 it/s, 8×H100 100%/50.5GB, ckpt@30000+20000已存, ETA~6.0h→~08:00 10-18。✅ armB_protb_eval.py+run_armB_protb_eval.sh 就绪(CPU单测3/3 PASSED)。✅ kill/分卡已完成(.12=vision独占, pretrain在.29)。**WAITING=1**。前序 ArmA(154500步)+ProtB(58.03%)完成。 |
| ERROR_COUNT | 20（①~⑲ 同前 ⑳ gather_object 119GB OOM → `log_samples=False` 修复 + batched `generate_until` 重写） |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-18 02:02 (wake #142)**: ArmB 4-epoch 训练监控——step 38580/57250(67.4%), loss~0.35(contr 0.12→0.33 硬分片抖动, C1 0.88→0.72 反坍缩方向, patch~0.019 平稳), 0.86 it/s(稳态), ETA~6.0h→~08:00 10-18。8卡100%util, 50.5GB/卡, 无OOM。✅ checkpoint_30000(@23:09)+20000已存, 下一@40000(~02:50)。✅ armB_protb_eval.py+run_armB_protb_eval.sh 就绪(CPU单测3/3 PASSED)。P0(kill+起训)+P1(ArmA报告)均已交付。下一步: 监控→训完run_armB_protb_eval.sh→报告。📦 体积：TASK=26.2KB / MEMORY=31.0KB（均<32KB）。 |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

### 评测耗时归因（2026-10-15）

| 环节 | 耗时(估) | 说明 |
|:--|:--|:--|
| 训练链 (Stage-1/1.5/2) | ~4h | Stage-1 2500步(~1.5h) + Stage-1.5 20000步(~2h) + Stage-2 3500步(0.26h) + gate check/smoke(~0.3h) |
| adapter 适配 (lmms-eval wrapper) | ~3h | `lmms_eval_baize_llava.py` 编写+调试(generate_until/loglikelihood/multi-GPU LOCAL_RANK/batch_size) |
| 数据通道 (HF 下载) | ~1.5h | proxy 直连 hf.co；ai2d smoke 77MB OK；17 集首次下载是大头(预建缓存中) |
| 磁盘满崩溃 + 修复 | ~0.5h | limit50 8卡同时写 `/home`(47G)→崩；修复=迁 HF_HOME→/nas_env + 单进程预建缓存 |
| git 推送阻塞 | ~6h | `.12` 直连 github 不通(无 proxy)→ 6h 推不上来(运维已配 git config http.proxy=92.23 修复) |
| generate 输出 bug | ~0.5h | 早期 ai2d 输出解析调试(`HF_TOKEN=hf_dummy` + adapter 输出格式) |

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
> 📦 [06:45 Oct08] weight-ratio 消融流水已归档 → daily-memories-vision/2026-10-11.md「Archived」节。**结论**：4臂无翻盘，1:1最优，contrast过高显著有害。
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

> 📦 [04:20 Oct12] 全量 1-epoch 耗时估算 + AIMv2 提速归因实测（bs/nw 扫描）已归档 → daily-memories-vision/2026-10-12.md「Archived from MEMORY_VISION.md」节。**结论**：bs=64 下数据/IO 受限（GPU util~70%），~5000 img/s 是 NFS 架构上限；1 epoch ≈ 5.2–9.1h。需要时再读。

## 本唤醒流水

> 📦 [Oct 13~14] 本唤醒流水旧条目（Wake #45~#84, 含 ArmC 监控/MLLM bridge/报告刷新/④-4ep eval/外部编码器, ~15条）已归档 → daily-memories-vision/2026-10-{13,14}.md。**关键结论**：ArmC 154500步完成(ProtB 68.25%), ④-4ep ProtB 67.05%, MLLM bridge 5/5 PASSED, 外部编码器 SigLIP2 87.46% 最高。需要时再读。
> 📦 10-06~10-12 早期流水（R12b/scaling/fair-rerun/V3/②probe/④-2ep/④-4ep, ~40条）已归档 → daily-memories-vision/2026-10-{06..12}.md。**关键结论**：E1fair vs E2fair Δlp=+0.17pp indistinguishable; ④-4ep ProtB 67.05% MODERATE/DIMINISHING; ④-2ep ProtB 65.37%。需要时再读。
> 📦 [Oct 16] 本唤醒流水旧条目（Wake #108~#115, 含 precache 监控/Part B 验收/limit50 abort/12集 eval 完成/keepalive, 5条）已归档 → daily-memories-vision/2026-10-16.md。**关键结论**：✅ Part B 三项验收全通过(ai2d=0.60)；✅ 12/12 benchmarks 全量 eval 完成(ai2d 60.04%/mmmu 42.89%/realworldqa 43.01%)；consolidated_12benchmarks.json 交付。需要时再读。
> 📦 [Oct16 20:50~23:1x] Wake #118~#120（ArmA 监控+效率专项落地）已归档 → daily-memories-vision/2026-10-16.md；**结论**：ArmA step21940 健康；效率优化一揽子落地(修前2.40→修后3.35 it/s +40%, util 95-100%全卡, 三项验收全达标)。
- [00:30 Oct17] **Wake #121**: 🔄 **ArmA 训练健康监控 + 效率验收复核** — git pull up to date, 无新运维指令。✅ ArmA 训练健康: step 59480/154500(38.5%), 8×H100 util 95-100%/全卡(25.6GB/卡), loss 0.33-0.63 EMA, C1~0.53-0.72, lr=1.51e-3。✅ 真实吞吐复核: (59480−30000)/(146.1min×60)=**3.36 it/s**(日志显示 6.79 系旧 sps 公式膨胀值)。✅ LPT 分片 0.0% 不均(spread=0.22GB)。✅ checkpoint_40000/50000 已存。✅ 效率验收三项全达标(+40% it/s, util≥85%全卡, 方差≈0)。真实 ETA ~7.9h → ~08:20 Oct17。📦 体积：TASK=30.4KB / MEMORY=~32KB（无归档，均 <32KB）。
- [02:57 Oct17] **Wake #123**: 🔄 **ArmA 训练监控** — git pull up to date，无新运维指令。✅ ArmA 训练健康: step 88940/154500(57.6%)，8×H100 util 90-100%/全卡(25.6GB/卡)，loss 0.39-0.65 EMA 振荡(C1~0.52-0.68, shard 难度正常)，lr=9.5e-4。✅ 真实吞吐: (88940−30000)/17579s=**3.35 it/s**(日志 5.07 系旧 sps 公式膨胀值)。✅ checkpoint_80000 已存(@02:15)。✅ 效率验收三项全达标(+40% it/s, util≥85%全卡, 方差≈0)。真实 ETA ~5.4h → ~08:24 Oct17。📦 体积：TASK=30.4KB / MEMORY=29.3KB（无归档，均 <32KB）。
- [04:09 Oct17] **Wake #124**: 🔄 **ArmA 训练监控** — git pull up to date，无新运维指令。✅ ArmA 训练健康: step 103400/154500(67.0%)，8×H100 util 99-100%/全卡(25.6GB/卡)，loss 0.48 EMA(C1~0.62, shard 难度波动正常)，lr=6.9e-4。✅ 真实吞吐: (103400−30000)/21936s=**3.35 it/s**(与 wake #123 完全一致→吞吐稳定; 日志 4.71 系旧 sps 公式膨胀值)。✅ checkpoint_90000(@03:00)+checkpoint_100000(@03:49) 已存。✅ 效率验收三项全达标(+40% it/s, util≥85%全卡, 方差≈0)。真实 ETA ~4.2h → ~08:24 Oct17。📦 体积：TASK=30.4KB / MEMORY=29.9KB（无归档，均 <32KB）。
- [09:10~13:30 Oct17] **Wake #126~#132**: ArmA 训练完成(154500步,3.37it/s,~7.9h)→ProtB 评测启动→ArmB 3-epoch→改4-epoch重启(PID 1203148)。详见 daily-memories-vision/2026-10-17.md。
- [14:5x Oct17] **Wake #133**: 🔄 **ArmB 训练监控 + ✅ P1 ArmA 中文报告交付** — git pull up to date，无新运维指令。✅ **ArmB 4-epoch 训练健康**：step 4540/57250(7.9%)，loss=0.70(contr=0.656 patch=0.045)，C1~0.52(warmup后爬升)，lr=9.95e-4(peak)，0.89 it/s，8×H100 96-100% util/50.5GB/卡(peak=50.4GB **无OOM**, MBS=512确认)，t=85min。真实吞吐 0.89 it/s(稳态)。✅ **P1 ArmA 中文报告交付**(纯CPU不占GPU)：`reports/report_vision_armA_openclip_result_zh.html`(25KB, 9节)——含训练配置、ProtB结果(lp 58.03±0.02%, 5-NN 53.98%)、对比表、关键解读、附录A/B。✅ EXPERIMENTS_VISION.md 新增 §10 ArmA 完整记录。📦 体积：TASK=26.9KB / MEMORY=~32KB（均 <32KB, 无归档）。
- [17:27 Oct17] **Wake #135**: 🔄 **ArmB 训练监控** — git pull up to date，无新运维指令。✅ **ArmB 4-epoch 训练健康**：step **12120/57250(21.2%)**，loss=0.48(contr=0.45 patch=0.030)，C1~0.60–0.70(对比损失正常振荡 0.55–0.71)，lr=9.28e-4(cosine 衰减)，**0.86 it/s**(稳态锁定)，8×H100 99–100% util/全卡/50.5GB/卡(peak=50.4GB **无OOM**, MBS=512确认)，t=234min(3.9h)。✅ checkpoint_10000(@16:49,1.81GB)+latest.pt+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json。ETA (57250−12120)/0.86≈14.5h→~10-18 08:00。📦 体积：TASK=26.2KB / MEMORY=31.1KB。
- [18:39 Oct17] **Wake #136**: 🔄 **ArmB 训练监控** — step 15960/57250(27.9%), loss=0.53, 0.87 it/s, ETA~08:00 10-18。详见 daily-memories-vision/2026-10-17.md。
- [19:5x Oct17] **Wake #137**: 🔄 **ArmB 训练监控 + ✅ ProtB eval 脚本就绪** — git pull up to date，无新运维指令。✅ ArmB 4-epoch 训练健康: step **20520/57250(35.8%)**, loss=0.36(contr=0.33 patch=0.026), C1~0.72, lr=7.73e-4, **0.88 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=390min(6.5h)。✅ checkpoint_20000(@19:53)+10000+latest+open_clip_state_dict(598MB)+predictor+config。✅ **新建 `armB_protb_eval.py`(386行)+`run_armB_protb_eval.sh`** — CPU单测3/3 PASSED: open_clip_state_dict.pt(302keys)与latest.pt(308→302keys, predictor剥离)两条加载路径权重一致, visual=86.2M；复用ArmA ProtB口径(feature=projected, full IN-1k, SGD 90ep, seeds 0/1/2, 5-NN, OMP_NUM_THREADS=8修复)。ETA (57250−20520)/0.88≈**11.6h→~07:30 10-18**; +ProtB 1–2h⇒**~09:00 10-18**。下一步: 监控→训完`run_armB_protb_eval.sh`→报告。📦 体积：TASK=26.2KB / MEMORY=31.3KB。
- [21:1x Oct17] **Wake #138**: 🔄 **ArmB 训练监控** — git pull fast-forward(1 commit, personal-watch), 无新运维指令。✅ ArmB 4-epoch 训练健康: step **23680/57250(41.4%)**, loss=0.27(contr=0.245 patch=0.023), C1~0.78, lr=6.99e-4, **0.85 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=462min(7.7h)。ETA (57250−23680)/0.85≈**11.0h→~08:00 10-18**。📦 体积：TASK=26.9KB / MEMORY=30.3KB。
- [22:26 Oct17] **Wake #139**: 🔄 **ArmB 训练监控** — git pull up to date，无新运维指令。✅ ArmB 4-epoch 训练健康: step **27540/57250(48.1%)**, loss=0.32(contr=0.30 patch=0.022), C1~0.74(正常振荡 0.69–0.85), lr=6.03e-4, **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=533min(8.9h)。✅ checkpoint_10000+20000+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在。ETA (57250−27540)/0.86≈**9.6h→~08:00 10-18**; +ProtB 1–2h⇒**~09:00–10:00 10-18**。下一步: 监控→训完`run_armB_protb_eval.sh`→报告。📦 体积：TASK=26.9KB / MEMORY=30.2KB（均<32KB）。




## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- Wakes #47/#49/#50/#51（2026-10-13）已归档至 `daily-memories-vision/2026-10-13.md`（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
