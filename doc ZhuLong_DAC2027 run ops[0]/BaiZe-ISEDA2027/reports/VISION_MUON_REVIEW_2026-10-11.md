# VISION_MUON_REVIEW_2026-10-11.md — Muon 坍缩「梯度谱」解释：外部反馈审视报告

> **性质**：评审 + 写作（零 GPU）· 线：vision · 日期：2026-10-11
> **任务来源**：运维指令 2026-10-11（用户直令）—— 朋友的意见支持 vision 的实验，请审视并简单合入论文。
> **关联文件**：`EXPERIMENTS_VISION.md §9.2` · `report_vision_muon_collapse.html` · `6_vision_encoder.tex`

---

## 0. 文献核验（铁律：不许猜 / 不许闭门造车）

对方称有「2026 年论文『Pion: high-pass replacement for Muon』」，但未给 arXiv ID。经联网核验：

| 字段 | 核验结果 |
|:--|:--|
| **标题** | Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR |
| **作者** | Chongyu Fan, Gaowen Liu, Mingyi Hong, Ramana Rao Kompella, Sijia Liu |
| **年份** | 2026 |
| **arXiv ID** | **2605.19282** |
| **提交日期** | 2026-05-19 |
| **链接** | https://arxiv.org/abs/2605.19282 |
| **核验状态** | ✅ **已核验**（arXiv 页面原文确认） |

**对方称「Pion: high-pass replacement for Muon」**——核验后确认：论文**确实提出了 Pion**（a drop-in replacement for Muon），但**论文标题不是「Pion: high-pass replacement for Muon」**，而是上述完整标题。「Pion」是方法名，不是论文标题。对方系**转述/简称**，非精确引用。

**论文摘要原文要点（arXiv 页面确认，非伪引）**：
> "Muon is a matrix-aware optimizer that leverages Newton-Schulz (NS) iterations to enforce spectral gradient orthogonalization by driving all singular values of the momentum matrix toward 1. While this uniform spectral whitening enhances exploration and outperforms AdamW in LLM pretraining, we show it could lead to fundamental limitations beyond pretraining in two regimes: (i) cross-modality vision-language-action (VLA) training, where inherently **low-rank action-module gradients cause amplification of noisy tail directions**, and (ii) reinforcement learning with verifiable rewards (RLVR), where **low-SNR gradients** ... make whitening unstable."

**核验结论**：对方转述的**核心机制**（均匀谱白化在低秩/低 SNR 梯度上失效、Pion 用高通替代）与 arXiv 原文一致。但对方未给 arXiv ID、且将论文标题简称为「Pion: high-pass replacement for Muon」——**我们在论文中引用时必须用真实标题 + arXiv ID，不得用对方的简称**。

---

## 1. 逐条审视（对方 7 条主张 vs 我方实测证据）

> **三分法标注**：🔵 我方实测 · 🟡 我方推断 · ⚪ 外部结论

### 第 1 条：坍缩不是调参失败，而是 Muon 核心机制的结构性不兼容 — ✅ 支持

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `EXPERIMENTS_VISION.md §9.2:922` | 🔵 我方实测 | "5× lower LR delays but does not prevent collapse (2,100→4,200 steps, same endpoint)" |
| `EXPERIMENTS_VISION.md §9.2:922` | 🔵 我方实测 | "C1 rise is monotonic and accelerating (0.18→0.96 in 3,900 steps). Loss IS decreasing (7.39→7.30)" |
| `report_vision_muon_collapse.html §3` | 🔵 我方实测 | C1 轨迹图：lr=1e-4 的 14 个 PROBE 点零回退，单调加速上升 |
| `EXPERIMENTS_VISION.md §9.2:922` | 🟡 我方推断 | "Root cause: Newton-Schulz orthogonalization forces unit-norm gradients, amplifying the dominant collapse direction" |

**说明**：5× 降 LR 仅将坍缩步数从 2,100 延缓到 4,200，终点相同（C1→0.95+）。坍缩时 loss 仍在下降（7.39→7.30），排除了优化失败（梯度爆炸/NaN），指向表示坍缩。

### 第 2 条：均匀谱白化在全秩/高 SNR 梯度上是优势，在低秩/低 SNR 上失效 — ✅ 支持（外部结论，已核验）

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| arXiv:2605.19282 摘要 | ⚪ 外部结论 | "low-rank action-module gradients cause amplification of noisy tail directions" |
| arXiv:2605.19282 摘要 | ⚪ 外部结论 | "low-SNR gradients ... make whitening unstable" |

**说明**：外部文献结论，我方未独立验证其 VLA/RLVR 实验。但 arXiv 原文确认该主张。

### 第 3 条：Muon pretrain 好 / VLA-RLVR 坍缩，与我方 pretrain 成功 / vision 失败同构 — ✅ 支持

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`「dist_muon」节 | 🔵 我方实测 | pretrain dist_muon 成功（loss 3.11 vs AdamW 4.00） |
| `report_pretrain_muon_vs_adamw.html §8` | 🔵 我方实测 | pretrain Muon 不坍缩 |
| `EXPERIMENTS_VISION.md §9.2:909` | 🔵 我方实测 | vision Muon 所有测试 LR 下坍缩 |
| arXiv:2605.19282 摘要 | ⚪ 外部结论 | "outperforms AdamW in LLM pretraining" + "Muon collapses to zero" (RLVR) |

**说明**：同一项目内直接平行证据——pretrain 纯 CE 成功 / vision InfoNCE+MSE 坍缩，与外部模式同构。

### 第 4 条：InfoNCE 偏好低秩；AdamW 逐参自适应对谱不敏感，Muon 是矩阵级谱约束 — ⚠️ 部分

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `EXPERIMENTS_VISION.md §9.2:922` | 🟡 我方推断 | "AdamW's per-parameter adaptive scaling naturally damps this" |
| `EXPERIMENTS_VISION.md §9.6` | 🔵 我方实测 | AdamW 基线 C1 稳定 0.10–0.55（187k 步无坍缩） |
| — | ❓ 无法判定 | **我们未测过 InfoNCE 梯度矩阵的秩/有效秩** — 「InfoNCE 偏好低秩」是外部推断，我方无直接证据 |

**说明**：AdamW vs Muon「作用维度不同」有间接支持（AdamW 不坍缩），但「InfoNCE 偏好低秩」我方未验证。

### 第 5 条：降 LR 只延缓不阻止（纯 GD vs Muon 设定） — ⚠️ 部分（须严格区分设定）

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `EXPERIMENTS_VISION.md §9.2:922` | 🔵 我方实测 | "5× lower LR delays but does not prevent collapse (2,100→4,200 steps, same endpoint)" |
| 对方第 5 条 | ⚪ 外部结论 | 纯 GD 下 lr=0.01 不坍缩 / lr=1 强坍缩 |
| 对方第 5 条 | ⚪ 外部推断 | "Muon 改方向结构而非缩放 ⇒ lr 只改到达时间" |

**⚠️ 关键区分**：对方引述的 lr 实验是**纯 GD 设定**，与我们的 **Muon 设定不同**，**不得混为一谈**。我们的结论是「降 LR 只延缓不阻止」——这是 **Muon 设定下的实测**。「Muon 改方向结构而非缩放」是对方的推断，我方未独立验证。

### 第 6 条：适用边界由梯度谱形状决定，而非损失函数类型 — ✅ 支持（非我方已证明）

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `EXPERIMENTS_VISION.md §9.2` | 🔵 我方实测 | Muon 在 InfoNCE+MSE 坍缩，AdamW 不 |
| `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` | 🔵 我方实测 | Muon 在纯 CE 预训练成功 |
| arXiv:2605.19282 | ⚪ 外部结论 | 均匀谱白化在低秩/低 SNR 梯度上失效 |

**说明**：我方数据与该结论方向一致，但**未直接测量梯度谱形状**，**不能写成「我们已证明」**。正确表述：「外部文献的解释 + 我们的现象与之相符」。

### 第 7 条：奇异值谱验证 — ❓ 无法判定（未验证，列为后续）

| 证据来源 | 类别 | 内容 |
|:--|:--|:--|
| `report_vision_muon_collapse.html §10` | 🔵 我方实测（缺口） | "无逐层梯度统计：训练日志仅输出全局聚合指标" |

**说明**：**我们没测过奇异值谱**。训练日志未记录 per-module 动量矩阵奇异值分布。坍缩实验的 optimizer state（含动量矩阵）未单独保存——ckpt 仅保存模型权重。**无法从已有产物补出**，列为后续工作。

---

## 2. 总结表

| # | 对方主张 | 判定 | 我方证据 | 外部证据 |
|:--|:--|:--|:--|:--|
| 1 | 坍缩不是调参失败，是结构性不兼容 | ✅ 支持 | 🔵 5×降LR仅延缓不阻止 | — |
| 2 | 均匀谱白化在低秩/低SNR梯度上失效 | ✅ 支持 | — | ⚪ arXiv:2605.19282 |
| 3 | Muon pretrain好/VLA-RLVR坍缩 与我方同构 | ✅ 支持 | 🔵 pretrain成功/vision坍缩 | ⚪ 论文确认同模式 |
| 4 | InfoNCE偏好低秩；AdamW对谱不敏感 | ⚠️ 部分 | 🟡 AdamW不坍缩（间接） | ❓ InfoNCE低秩未验证 |
| 5 | 降LR只延缓不阻止（纯GD vs Muon） | ⚠️ 部分 | 🔵 Muon设定下确实只延缓 | ⚠️ 纯GD≠我方设定 |
| 6 | 适用边界由梯度谱形状决定 | ✅ 支持（非已证明） | 🔵 现象方向一致 | ⚪ 外部解释 |
| 7 | 奇异值谱验证 | ❓ 无法判定 | ❓ 未测过，无optimizer state | — |

---

## 3. 我方能证明什么 / 不能证明什么

### ✅ 我方已证明（实测）
1. **Muon 在 AIMv2-style 联合目标下，于所有测试 LR 均引发对比坍缩**（C1→0.95+），AdamW 同配置不坍缩。
2. **降 LR 只延缓不阻止坍缩**（5e-4@step2100 → 1e-4@step4200，终点相同）。
3. **坍缩时 loss 仍在下降**（7.39→7.30），是表示坍缩而非优化失败。
4. **Muon 在纯 CE LLM 预训练下成功**（pretrain 线 dist_muon，loss 3.11 < AdamW 4.00）。

### 🟡 我方推断（未独立验证）
1. 根因是 Newton-Schulz 正交化放大了主导坍缩方向。
2. AdamW 的逐参自适应缩放天然抑制了坍缩方向。

### ❓ 我方未验证（列为后续）
1. **InfoNCE 梯度矩阵的有效秩**（是否真的「低秩」）。
2. **Muon vs AdamW 的动量矩阵奇异值分布**（对方建议的第 7 条验证）。
3. **Muon 更新方向的几何分析**（是否真的「改方向结构而非缩放」）。

### ⚠️ 须严格区分
- 对方第 5 条的 lr 实验是**纯 GD 设定**，与我们的 **Muon 设定不同**，不得混为一谈。

---

## 4. 论文合入说明（Part B）

### 落点
`6_vision_encoder.tex` §VI-D 末尾，新增 `\paragraph{Optimizer ablation: Muon.}`（约 114 词）

### 合入内容
1. **现象**（一句）：Muon 在 AIMv2-style 联合目标下所有测试 LR 均坍缩，AdamW 不。
2. **外部对照**（一句）：引 arXiv:2605.19282（已核验），均匀谱白化在低秩/低 SNR 梯度上失效。
3. **结论**（一句）：适用边界由梯度谱形状决定——**明确写成「外部文献的解释 + 我们的现象与之相符」**，🚫 不写成「我们已证明」。

### bib 条目
`reference.bib` 新增 `@misc{fan2026pion, ...}`（arXiv:2605.19282）

### 页数控制
- ISEDA Regular Full Paper 限制 = **4-6 页**（IEEE double-column，ISEDA 2026 CFP 确认）。
- **改前**：11 页 / 358,430 bytes（Oct 8 11:13）
- **改后**：11 页 / 358,753 bytes（Oct 11 22:57）
- **页数变化：11 → 11（净增 = 0 页）** ✅
- 压缩了 §VI-D Evaluation 段（retrieval proxy 描述）和 Interpretation 段（冗余措辞），约节省 ~60 词；新增 Muon 段 ~114 词 + bib 1 条。

### 编译验收
- `pdflatex ×1 + bibtex + pdflatex ×2` → **0 error**，0 undefined citation/reference（仅预存在的 font shape warning）。
- `fan2026pion` 已在 `main.bbl` 中解析为 `\bibitem{fan2026pion}`（参考文献第 19 条）。

---

## 5. Part C：奇异值谱验证（未做，如实记录）

**对方建议**：坍缩前记录各层动量矩阵的奇异值分布，与 AdamW 对比。

**执行情况**：**未验证，列为后续**。

**原因**：
1. 训练日志未记录 per-module 动量矩阵奇异值分布（`report_vision_muon_collapse.html §10` 已记录此缺口）。
2. 坍缩实验的 **optimizer state（含动量矩阵）未单独保存**——ckpt 仅保存模型权重。
3. 从已有 ckpt 无法重建动量矩阵（动量是训练过程中梯度 EMA，非权重属性）。
4. 要做此验证需重新跑训练或添加 spectral norm 日志，但**不得占用 `.12` GPU**（在飞的 ④-2ep 优先）。

---

## 6. 诚实条款

| 类别 | 内容 |
|:--|:--|
| 🔵 我方实测 | C1/C2_gap/loss 轨迹；坍缩步数与终值；AdamW 不坍缩；lr 延缓规律；pretrain Muon 成功 |
| 🟡 我方推断 | 根因假设（正交化放大坍缩方向）；AdamW 逐参自适应抑制 |
| ⚪ 外部结论（已核验） | arXiv:2605.19282：均匀谱白化在低秩/低 SNR 梯度上失效 |
| ❓ 未验证 | InfoNCE 梯度有效秩；Muon vs AdamW 动量奇异值分布；更新方向几何 |
| ⚠️ 须区分 | 对方第 5 条 lr 实验是纯 GD ≠ 我方 Muon 设定 |

---

> **报告信息**：BaiZe Vision Muon 审视报告 · 2026-10-11 · 线：vision · 提交前缀：`vision muon-review:`
> **关联文件**：`EXPERIMENTS_VISION.md §9.2` · `report_vision_muon_collapse.html` · `6_vision_encoder.tex` · `reference.bib`
