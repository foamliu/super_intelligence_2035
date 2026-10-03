# EXPERIMENTS_VISION_ROUND11.md — R11 目标函数（loss）轴：监督密度 vs 渐近上限

> 第十一轮：R9/R10 已证「瓶颈在数据量与目标函数（非架构）」。本轮**只变目标函数**，检验
> 「InfoNCE 每对只给 1 个全局标量（监督密度最低）→ 换成稠密监督（逐 patch/token）能否把 25.1% 渐近抬高」。
> **预注册**：判据先定后测，不许事后改。**控变量**：除目标函数外全部固定。

---

## 0. 定位与动机（一句话）

R9 幂律渐近 `acc=0.251−0.864·N^−0.090`（R²≈0.94）→ **25.1% 上限**是「从零 + InfoNCE」路线的如实渐近；
本轮的机制假说（⚠️ 须实测，不得当结论）：**InfoNCE 监督密度最低（1 个全局标量/对），数据越少越可能被稠密监督翻盘**。
→ 官方 AIMv2 / OpenVision2 都是**逐 patch / token 的稠密监督**。

---

## 1. ⚖️ 预注册判据（先定后测，不许改）

> 固定「同 N、同口径」：塔 w512（126.78M）· 数据 CC12M+Amshaker · 步数/样本预算 · 优化器 · 评测 IN-1k **frozen-trunk lp**（同 R9）。

- **基线**：InfoNCE（R9 阶段一 w512 = 6.08%@15.36M；阶段二 7.70%@51.2M，lp 渐近 25.1%）。
- **判据**：某臂同 N 下 **lp 比基线 > +1.5 点** → 「25.1% 是对比学习的渐近」**局部推翻** → 对该臂**重拟合 scaling 并外推**。
  - ≤ +1.5 点 → 维持「对比/稠密监督在本数据规模下不改变 25.1% 上限」。
  - ⚠️ 本线 pre-commit 口径：run variance 同 (N,M) 两 run 差 **0.5–1.1 pp**（R10 §1.5）→ +1.5 点阈值 > 噪声带上界，公平。
- **公平性铁律**：加 decoder/生成头的臂**必须报「参数量 + 训练 token + 每步耗时」**，不许只比 acc（见 §3 公平表）。

---

## 2. 臂定义（6 臂，按 R14 官方实现对齐；全部固定 w512 + 冻结 CLIP-768 文本塔 — 仅 arm ⑤⑥ 例外见备注）

> 现状代码：`r9_train.py` 用 `open_clip.loss.ClipLoss`（InfoNCE，`local_loss=False`）；`train.py` 另有 `SigLipLoss`（旧 S 系列栈，随机 text 塔，R4 用其在 ~0.5M 坍缩）。

| # | 臂 | 目标函数 | 实现来源 | 成本/风险 | 状态 |
|:--|:--|:--|:--|:--|:--|
| ① | **InfoNCE（基线）** | `open_clip.loss.ClipLoss(local_loss=False)` | 已有（R9/R10） | — | ✅ 已有 |
| ② | **SigLIP** | `open_clip.loss.SigLipLoss`（双向 sigmoid） | `train.py:110-111` 已写；R14 `sigmoid_xent`(OpenVision `losses/common.py:40`) 同源 | 低（改 1 处 loss + 保留冻结文本塔） | ⏸ 待实现 |
| ③ | **LocalLoss** | InfoNCE 的 `local_loss=True`（逐卡局部 batch，不 cross-rank gather） | `open_clip.loss.ClipLoss(local_loss=True)` | 低（改 1 参数；⚠️ 改变负样本池语义，须盯 C1–C4 不坍缩） | ⏸ 待实现 |
| ④ | **CoCa**（对比 + caption 生成） | 对比 + 自回归 caption CE（OpenVision `caption CE` + `coca_caption_loss_weight=2`） | 需**新写 caption decoder**（OpenVision2 权重 = concat/prefix-LM，**非 CoCa cross-attn**）；R14 可抄 Apache-2.0 的 caption CE 写法 | 高（新 decoder + 参数量/token 报备） | ⏸ |
| ⑤ | **GenLIP / AR（纯生成）** | caption-only 自回归（无对比项） | 需 caption decoder；⚠️ 我们 caption 偏短（CC12M=Amshaker alt-text 短句 / GPIC short=20 tok）→ 生成监督密度被短 caption 拖累（机制推断须实测） | 高 | ⏸ |
| ⑥ | **AIMv2 式（patch+text 双 AR）** | patch 预测 + text token 自回归（多模态 AR） | 官方 `ml-aim` 仅模型接口、**无 loss/训练代码 + Apple Sample Code 不可抄**；需自研 mask+双流 AR | 🔴 最贵；**条件触发**（臂②–⑤无翻盘迹象才做） | ⏸ |

- **执行顺序（成本递增）**：①（基线）→ ② SigLIP → ③ LocalLoss → ④ CoCa → ⑤ GenLIP → ⑥ AIMv2（条件）。
- **R11-L2 单独成题**（文本塔解冻 LoRA/Adapter vs 现状冻结），不在本表内，另测。

---

## 3. ⚖️ 公平表（加 decoder 的臂必填；无 decoder 臂与基线同参数量）

| 臂 | 参数量增量 | 每步额外 token | 每步耗时（相对基线） | 备注 |
|:--|:--|:--|:--|:--|
| ① InfoNCE | 0（基线） | 0 | 1.0× | w512=126.78M |
| ② SigLIP | +1（logit bias 标量） | 0 | ≈1.0× | 无 decoder |
| ③ LocalLoss | 0 | 0 | ≈1.0×（无 cross-rank gather） | 负样本池变局部 |
| ④ CoCa | +decoder（≈参考 OpenVision2 `text_decoder w768·12L`） | +caption 自回归 | 待实测 | 须报 decoder 层数/宽度 |
| ⑤ GenLIP | +decoder（同上） | +caption 自回归 | 待实测 | — |
| ⑥ AIMv2 式 | +patch head + text AR | +patch/text token | 待实测（最贵） | — |

---

## 4. 协议（控变量，全部固定）

- 塔：OpenVision2 **w512（126.78M）**，depth30 / patch16 / 224²。
- 文本塔：冻结 `clip-vit-large-patch14-336` 768 维（context 77）（臂⑤⑥ 若需改动，须在下表报备并重跑 R4 坍缩判据 C1–C4）。
- 数据：CC12M ~11M + Amshaker ~6M（R9 同源，`r9_train.py --data` 同路径）。
- 优化器/schedule：AdamW、lr 3e-3、warmup 20、cosine、seed 1234、bf16、bs64×8=512。
- **样本预算（同 N 对照）**：主锚点 **N=15.36M（30k 步，= R9 阶段一）**；胜负臂延至 108k（55.3M）复证。
- 评测：IN-1k **frozen-trunk lp**（`r8_eval_in1k.py`，同 R9/R10）+ 坍缩探针 C1–C4（同 R4）。
- 证据纪律：每条结论贴命令 + 原始输出 + 路径。

---

## 5. 状态

- 🕐 **R11-L 预注册完成（本文档）**；臂 ① 基线已有，**臂 ② SigLIP 待实现（下一唤醒）**。
- 每臂灰印培训需要 8 卡（`.12`），启动前先核 GPU 空闲（同 R10-③ 的 GPU 核验）。