# VISION_AIMV2_OFFICIAL_PLAN.md — 官方 AIMv2 范式复现 · 实现方案 + 成本 + 预注册判据

> **状态**：✅ **已批准**（运维 2026-10-06 批准「方向⑤复现官方 AIMv2 纯 AR 范式」）。⚠️ **开跑前必须先落实下方 6 点修订**（运维逐项审阅意见，重点 = 问题 3 与问题 5）。6 点落实后即可按队列开跑，不必再等第二次批准。
> **队列位置**：④（排在 lp 协议桥接 ① → mask-ratio 消融 ② → 权重比消融 ③ 之后）
> **创建**：2026-10-06 18:10；**修订**：2026-10-06（落实运维 6 点审阅意见）
> **许可证**：🔴 **Apple Sample Code License — 不得拷贝官方代码**；本方案为**按论文描述自研实现**

---

## 1. 目标

在**同塔、同数据、同 token 预算**下，将「官方 AIMv2 纯 AR 范式」与「我们的非 AR 范式」做 **controlled A/B**，回答：**在相同规模下，AR 范式是否优于我们的非 AR + 对比范式？**

## 2. 规格对照表（用户给定）

| 项 | **官方 AIMv2（Arm B）** | **我们（Arm A，现状）** |
|---|---|---|
| **范式** | **纯 AR**（vision AR + text AR） | 非 AR：**双向 ViT + 随机掩码** |
| **对比项** | ❌ **无** | ✅ **保留 InfoNCE** |
| **掩码** | **prefix-attention（causal）** | **随机掩码**（每 patch 独立 0.6） |
| **trunk forward** | **AR：前面可见、后面 mask token** | **全 patch 可见、无 mask token** |
| **文本塔** | **可训 text AR decoder** | **冻结 CLIP-768** |
| **损失** | `cap_loss + α × pixel_loss` (α≈0.4) | `1.0 × InfoNCE + 1.0 × patch_MSE` |

## 3. 实现方案（自研，不抄 Apple 代码）

### 3.1 代码修改清单

| 文件 | 修改 | 复用 |
|:--|:--|:--|
| `vision/models.py` | ① `AttentionBlock.forward(x, attn_mask=None)` — 传递 causal mask 到 `Attention`（已有 `attn_mask` 参数，L44）<br>② `OpenVision2.forward(x, return_patch=False, causal=False)` — 当 `causal=True` 时构造下三角 mask 并传给所有 block | `Attention` 类已支持 `attn_mask`（L48） |
| `vision/models.py` | ③ 新增 `ARTextDecoder` — 基于 `CoCaDecoder` 结构（L442-475），causal self-attn + **cross-attn→**`causal`** vision patches**（每个 patch 只含前缀信息，与官方一致）+ **trainable** token embed | `CoCaDecoderBlock`（L423）已支持 causal mask |

> ⚠️ **cross-attention 目标声明（修订点②）**：text decoder **必须 cross-attend 到 `causal` vision patches**（即 `OpenVision2.forward(causal=True)` 的输出，每个 patch 只含位置 0..i 的前缀信息）。🚫 **若 attend 到双向 patch 特征**（即 `causal=False` 的全可见输出），则变成「双向 vision + causal text」——**这不是**官方 AIMv2 范式。官方 AIMv2 的 text decoder 看到的 vision 特征与 vision AR 头看到的完全一致（均为 causal 前缀），这是范式一致性的核心约束。
| `vision/models.py` | ④ `PatchPredictor`（L478）**原样复用** — AR 模式下对**所有位置**做 next-patch 预测 | `PatchPredictor` + `mae_norm_pix_target` 均已有 |
| `vision/r9_train.py` | ⑤ 新增 `--loss aimv2_ar` 分支：causal ViT → next-patch pixel_loss + text AR cap_loss；**无 InfoNCE** | `mae_norm_pix_target` / `coca_caption_loss` / `tokenize_cap` 均已有 |
| `vision/r9_train.py` | ⑥ 新增 `--alpha-pixel 0.4`（官方 α 值） | — |

### 3.2 AR 前向详解

```
Input: imgs (B,3,224,224)
  ↓ PatchEmbed → patches (B, 196, 512)
  ↓ OpenVision2.forward(causal=True)  # 下三角 mask，位置 i 只见 0..i
  ↓ ar_patches (B, 196, 512)
  ├──→ PatchPredictor(ar_patches) → pred_pixels (B, 196, 768)
  │    pixel_loss = MSE(pred[:, :-1], target[:, 1:])  # next-patch (shift by 1)
  └──→ ARTextDecoder(ids, ar_patches)
       cap_loss = CE(cap_logits[:, :-1], ids[:, 1:])  # next-token
  ↓ total_loss = cap_loss + 0.4 * pixel_loss
```

**关键**：causal mask 使位置 i 只见 0..i → 预测 i+1 的 patch 是合法自监督任务；text decoder 的 token_embed **可训**（非冻结 CLIP）。

> 📌 **AR ≠ MAE 语义说明（修订点①）**：
> - **AR（自回归）**=「**给定前文预测后文**」：位置 i 的输出**只看到 patch 0..i**，目标是预测 patch i+1。`MSE(pred[:, :-1], target[:, 1:])` 的 shift-by-1 实现是正确的。
> - **MAE（掩码自编码）**=「给定**双向上下文**重建**被遮位置**」：每个位置可看到全部未被遮的 patch，目标是重建被随机遮住的位置。
> - **两者本质不同**：AR 是因果的（单向），MAE 是双向的。不要将 `shift-by-1 MSE` 与 MAE 的重建混淆。
> - **边界细节**：位置 0 的输出**只看到 patch 0 自身**（无前文）；位置 195（最后一个 patch）**无 target**（被 shift 掉，不参与 loss）→ 实际 loss 只在位置 0..194 上计算，共 195 个预测位置。

### 3.3 参数量对比

| 组件 | Arm A (我们) | Arm B (官方 AR) |
|:--|---:|---:|
| Vision trunk (w512/d30) | 126.78M | 126.78M |
| PatchPredictor | 0.66M | 0.66M |
| Text tower/decoder | 冻结 CLIP (不计) | ARTextDecoder ~66.8M (可训, weight-tied) |
| **总可训** | **127.44M** | **~194.3M** |

> ⚠️ Arm B 多 ~67M 可训参数。**必须报告**，并补跑 Arm B' 隔离参数量影响。

> 📌 **B' 参数量隔离方案（修订点⑤）——缩宽度而非减深度**：
> - **问题**：原方案 `depth=2` 的浅 decoder **隔离不干净** —— 浅 decoder 的表达能力本身就差，无法区分「参数少导致性能差」还是「太浅导致性能差」。
> - **改为**：**保持 depth 不变（与 Arm B 同 depth）、缩小 hidden dim**，使 B' 的总可训参数量**对齐 Arm A（~127M）**。具体：decoder hidden dim 从 512 缩到 ~256（使 decoder 参数 ≈ Arm A 的 PatchPredictor + 冻结 CLIP 投影层量级），depth 保持 30（与 trunk 同）或取 CoCaDecoder 默认深度。
> - **同时报告 B' 的 `cap_loss` 与 `pixel_loss`**：若 B' 的 `cap_loss` 明显高于 Arm B（但 `pixel_loss` 相近）⇒ 说明是 **text AR 能力不足**（窄 decoder 限制了语言建模），而非参数量本身的问题；若两者都高 ⇒ 确认是参数量不足。
> - **判据**：B' lp ≈ Arm A（±1.5 pp）⇒ 参数量不是主因；B' lp 明显 < Arm B 且 ≈ Arm A ⇒ 参数量是主因。

## 4. 成本估算

| 档位 | 步数 | N (样本) | 预估墙钟 | GPU·h | 用途 |
|:--|---:|---:|---:|---:|:--|
| **快速 A/B** | 30k | 15.36M | ~1.5–2.5h | ~12–20 | 最小可行：快速看 AR 是否有信号 |
| **中规模** | 108k | 55.3M | ~6–9h | ~48–72 | 与 R11-G 同 N，可比 scaling |
| **全量** | 272k | 139.3M | ~15–22.7h | ~120–182 | 与 R12b 同 N，完整对照 |

> ⚠️ 上表墙钟区间 = 乐观 ~4500 img/s（上界）至保守 ~3500 img/s（下界）。**实际值以 smoke test 为准**。

> 吞吐预估：AR causal attention 的 **FLOPs 不降**（SDPA + `attn_mask` 通常不省算力，还有 mask 开销）；text decoder 的 cross-attn 与 **`PatchPredictor` 对全部 196 位置**（vs 随机掩码 ~118 ⇒ **+66%**）都会增算 ⇒ **预留「实际吞吐可能只有 3500–4000 img/s」**（vs R12b ~5000）。
> **必须先 smoke test**（30 步）确认实际 img/s；⚠️ **若 30k 快速 A/B 的实际墙钟 >3h，需重新评估是否值得上 108k**。
> **推荐先跑 30k 快速 A/B**，有正面信号再上 108k/272k。

## 5. 预注册判据（先定后测）

### 5.1 主指标
IN-1k frozen-trunk lp @ step30k（BaiZe 协议）。噪声带 ±1.5 pp。

### 5.2 判定规则

| 条件 | 判定 | 论文措辞 |
|:--|:--|:--|
| Arm B lp ≥ Arm A **+1.5** 且 C1-C4 OK | ✅ **AR 更优** | 「纯 AR 在同规模下优于非 AR + 对比」 |
| Arm B lp ≤ Arm A **−1.5** | ❌ **非 AR + 对比更优** | 「保留对比项 + 双向注意力是必要的」 |
| **+0.5 < Δlp < +1.5**（趋势但不显著） | 🟡 **趋势性优势** | 「AR 有正向趋势，但未达预注册显著性阈值（+1.5 pp），需更大规模验证」 |
| \|Δlp\| ≤ 0.5 | ⚪ **范式等价** | 「范式选择在此规模不敏感」 |
| Arm B **坍缩** (C1>0.95) | 🔴 **AR 无对比项坍缩** | 「与 R11-H 一致，翻盘依赖对比项」 |

> 📌 **组合判定（修订点⑥）**：
> - **Δlp 大但 C1 接近坍缩（如 C1=0.90）**：判定为 **⚠️ 「AR 有效果但表征退化」** —— lp 的提升可能来自 decoder 的额外监督信号而非更好的 trunk 表征。论文措辞：「AR 范式在 lp 上有提升，但 C1 指标接近坍缩表明 trunk 表征质量退化，lp 提升更可能来自 decoder 的辅助监督而非 trunk 本身」。
> - **C1 在 0.85–0.92 区间 + Δlp > +1.5**：判定为 🟡 **「有信号但需警惕」** —— 报告必须同时报 C1 与 lp，不允许只报 lp。
> - **C1 < 0.80 + Δlp > +1.5**：判定为 ✅ **「AR 更优」**（正常通过）。

### 5.3 公平性报告（必须全部报告）
参数量（含 decoder）× 2 臂 · 训练 token × 2 · 每步耗时 × 2 · 稳态 img/s × 2 · C1/C2/C4 × 2

### 5.4 对照臂

| 臂 | 范式 | 损失 | 文本 | 掩码 |
|:--|:--|:--|:--|:--|
| **A** (基线) | 双向 + InfoNCE | `1.0×InfoNCE + 1.0×patch_MSE` | 冻结 CLIP-768 | 随机 0.6 |
| **B** (官方 AR) | 纯 AR (causal) | `cap + 0.4×pixel` | 可训 ARTextDecoder | causal mask |
| *(可选) B'* | 纯 AR (causal) | `cap + 0.4×pixel` | 可训 decoder (**缩宽度**, hidden~256) | causal mask |

> Arm A 基线 = R11-G arm⑥-A（已有 lp@30k=12.08%，不必重跑）。B' 隔离参数量影响。

## 6. 风险与边界

| 风险 | 缓解 |
|:--|:--|
| C2 限定：自研实现，非官方复现 | 报告标注「自研实现（非官方权重复现）」 |
| 坍缩风险 | C1-C4 探针监控（R11-H 实际未坍缩 C1=0.43）；组合判定见 §5.2 |
| caption 短 → cap_loss 信号弱 | ⭐ **必须在方案与最终报告里显著标注该 handicap**（修订点③）：官方用 **LLaMA-3 长合成 caption（~12B 样本）**，我们用**短 alt-text**（CC12M / Amshaker / GPIC short）⇒ **text AR 的 next-token 信号天然弱**。否则会把「**短 caption 不适合 text AR**」误读成「**官方 AIMv2 范式差**」。同数据公平比较；标注 handicap |
| causal attention 可能更慢 | smoke test 确认；预留 3500–4000 img/s；若 30k >3h 需重新评估 |
| 参数量不对等（B 多 ~67M） | 补跑 B'（**缩宽度**而非减深度，修订点⑤）；同时报 cap_loss + pixel_loss 隔离原因 |

## 7. 产出

- `report_vision_aimv2_official_vs_ours.html`（自包含：规格表 + 两臂结果 + 差异归因 + 论文 §6.3 措辞建议）
- `EXPERIMENTS_VISION_ROUND13.md`：预注册判据 + 结果 + 公平性表
- 代码：`models.py` `ARTextDecoder` + `OpenVision2.forward(causal=True)`；`r9_train.py` `--loss aimv2_ar`

## 8. 执行计划（批准后）

1. **实现 + smoke**（~2h）：修改代码，30 步 smoke 验证 **+ 吞吐实测**（确认实际 img/s，更新成本表）
2. **30k 快速 A/B**（~12–20 GPU·h）：Arm B 跑 30k，Arm A 复用已有；⚠️ **若墙钟 >3h 需重新评估是否上 108k**
3. **判据评估**：有信号 → 上 108k；否则 → 报告负结果
4. **（条件）108k/272k**：有信号才跑
5. **写报告 + 回填论文**（报告须标注短 caption handicap）

## 9. 许可证合规

- 🔴 **不得拷贝** `ml-aim/AIMv2` 任何代码（Apple Sample Code License）
- ✅ **可参考论文描述**（arXiv 2411.14444）自研实现
- ✅ **可复用** 本仓库已有代码（`CoCaDecoder` / `PatchPredictor`，均自研或 Apache-2.0 参考）
- 报告标注：「自研实现（非官方权重复现），基于 AIMv2 论文描述」

