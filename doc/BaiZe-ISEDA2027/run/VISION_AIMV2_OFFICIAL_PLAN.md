# VISION_AIMV2_OFFICIAL_PLAN.md — 官方 AIMv2 范式复现 · 实现方案 + 成本 + 预注册判据

> **状态**：⏸ **方案待运维批准**（运维指令 2026-10-06：「先交方案 + 成本 + 预注册判据，经运维批准再开跑」）
> **队列位置**：④（排在 lp 协议桥接 ① → mask-ratio 消融 ② → 权重比消融 ③ 之后）
> **创建**：2026-10-06 18:10（R12b 训练中 step~108k/272k，CPU-only 准备工作）
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
| `vision/models.py` | ③ 新增 `ARTextDecoder` — 基于 `CoCaDecoder` 结构（L442-475），causal self-attn + cross-attn→vision patches + **trainable** token embed | `CoCaDecoderBlock`（L423）已支持 causal mask |
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

### 3.3 参数量对比

| 组件 | Arm A (我们) | Arm B (官方 AR) |
|:--|---:|---:|
| Vision trunk (w512/d30) | 126.78M | 126.78M |
| PatchPredictor | 0.66M | 0.66M |
| Text tower/decoder | 冻结 CLIP (不计) | ARTextDecoder ~66.8M (可训, weight-tied) |
| **总可训** | **127.44M** | **~194.3M** |

> ⚠️ Arm B 多 ~67M 可训参数。**必须报告**，并补跑 Arm B'（depth=2, ~33.4M）隔离参数量影响。

## 4. 成本估算

| 档位 | 步数 | N (样本) | 预估墙钟 | GPU·h | 用途 |
|:--|---:|---:|---:|---:|:--|
| **快速 A/B** | 30k | 15.36M | ~2.5h | ~20 | 最小可行：快速看 AR 是否有信号 |
| **中规模** | 108k | 55.3M | ~9.0h | ~72 | 与 R11-G 同 N，可比 scaling |
| **全量** | 272k | 139.3M | ~22.7h | ~182 | 与 R12b 同 N，完整对照 |

> 吞吐预估：AR causal attention FLOPs = 双向（同 QKV）；text decoder +10-15% → ~4500 img/s（vs R12b ~5000）。**需 smoke test 确认。**
> **推荐先跑 30k 快速 A/B**，有正面信号再上 108k/272k。

## 5. 预注册判据（先定后测）

### 5.1 主指标
IN-1k frozen-trunk lp @ step30k（BaiZe 协议）。噪声带 ±1.5 pp。

### 5.2 判定规则

| 条件 | 判定 | 论文措辞 |
|:--|:--|:--|
| Arm B lp ≥ Arm A **+1.5** 且 C1-C4 OK | ✅ **AR 更优** | 「纯 AR 在同规模下优于非 AR + 对比」 |
| Arm B lp ≤ Arm A **−1.5** | ❌ **非 AR + 对比更优** | 「保留对比项 + 双向注意力是必要的」 |
| \|Δlp\| < 1.5 | ⚪ **范式等价** | 「范式选择在此规模不敏感」 |
| Arm B **坍缩** (C1>0.95) | 🔴 **AR 无对比项坍缩** | 「与 R11-H 一致，翻盘依赖对比项」 |

### 5.3 公平性报告（必须全部报告）
参数量（含 decoder）× 2 臂 · 训练 token × 2 · 每步耗时 × 2 · 稳态 img/s × 2 · C1/C2/C4 × 2

### 5.4 对照臂

| 臂 | 范式 | 损失 | 文本 | 掩码 |
|:--|:--|:--|:--|:--|
| **A** (基线) | 双向 + InfoNCE | `1.0×InfoNCE + 1.0×patch_MSE` | 冻结 CLIP-768 | 随机 0.6 |
| **B** (官方 AR) | 纯 AR (causal) | `cap + 0.4×pixel` | 可训 ARTextDecoder | causal mask |
| *(可选) B'* | 纯 AR (causal) | `cap + 0.4×pixel` | 可训 decoder (depth=2) | causal mask |

> Arm A 基线 = R11-G arm⑥-A（已有 lp@30k=12.08%，不必重跑）。B' 隔离参数量影响。

## 6. 风险与边界

| 风险 | 缓解 |
|:--|:--|
| C2 限定：自研实现，非官方复现 | 报告标注「自研实现（非官方权重复现）」 |
| 参数量不对等（B 多 ~67M） | 补跑 B'（浅 decoder）隔离 |
| caption 短 → cap_loss 信号弱 | 同数据公平比较；标注 handicap |
| causal attention 可能更慢 | smoke test 确认 |
| 坍缩风险 | C1-C4 探针监控（R11-H 实际未坍缩 C1=0.43） |

## 7. 产出

- `report_vision_aimv2_official_vs_ours.html`（自包含：规格表 + 两臂结果 + 差异归因 + 论文 §6.3 措辞建议）
- `EXPERIMENTS_VISION_ROUND13.md`：预注册判据 + 结果 + 公平性表
- 代码：`models.py` `ARTextDecoder` + `OpenVision2.forward(causal=True)`；`r9_train.py` `--loss aimv2_ar`

## 8. 执行计划（批准后）

1. **实现 + smoke**（~2h）：修改代码，30 步 smoke 验证
2. **30k 快速 A/B**（~20 GPU·h）：Arm B 跑 30k，Arm A 复用已有
3. **判据评估**：有信号 → 上 108k；否则 → 报告负结果
4. **（条件）108k/272k**：有信号才跑
5. **写报告 + 回填论文**

## 9. 许可证合规

- 🔴 **不得拷贝** `ml-aim/AIMv2` 任何代码（Apple Sample Code License）
- ✅ **可参考论文描述**（arXiv 2411.14444）自研实现
- ✅ **可复用** 本仓库已有代码（`CoCaDecoder` / `PatchPredictor`，均自研或 Apache-2.0 参考）
- 报告标注：「自研实现（非官方权重复现），基于 AIMv2 论文描述」

