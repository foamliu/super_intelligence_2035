# PAPER_STALENESS_AUDIT.md — BaiZe 论文「陈旧性审计」

> 审计时间：2026-10-03 · 审计人：运维 · 对象：`BaiZe-ISEDA2027/ISEDA2027/*.tex`
> **依据（只引权威源，不凭印象）**：`run/EXPERIMENTS_VISION_ROUND{4,5,8,9,10}.md` · `README.md` · `run/MEMORY_VISION.md` · 本项目 2026-10-03 的各项更正。
> **一句话结论**：**§6 视觉节整节停留在 R1/R2「坍缩期」，与 R4–R10 的实际结论完全脱节**（这是最严重的问题，比任何叙事问题都严重）；另有 2 处**同文档自相矛盾**、1 处**口径不一致**。

---

## 0. 速览（结论先行）

| # | 位置 | 问题 | 严重度 | 本轮处置 |
|:-:|:--|:--|:--:|:--|
| 1 | `6_vision_encoder.tex` **全节** | **整节停留在 R1/R2 坍缩期**：**4 架构**（R8 起为 **6**）· recipe 写 **SigLIP + width-512 文本塔**（R4 已弃）· 指标是 **loss≈4.456**（= 坍缩平台读数）· 还断言「**本阶段没有可用的下游指标**」 | 🔴🔴🔴 | ✅ **已改述**（§1）；⚠️ **四张表待整表替换**（§2） |
| 2 | `6_vision_encoder.tex:121` vs `:106` | CLIP InfoNCE loss **`2.894`** vs **`3.2704`** —— **同一文档自相矛盾** | 🔴🔴 | ✅ **已修 → `3.2704`** |
| 3 | `3_architecture.tex:30` | `Sequence length & 4096`，但 §4 报告的是 **`8×4094`** —— **口径打架** | 🔴 | ✅ **已修 → `4094`** |
| 4 | `3_architecture.tex:40` · `6_vision_encoder.tex:7` | 「**four** iso-parameter candidates」→ R8 起为 **six** | 🟡 | ✅ **已修 → `six`** |
| 5 | `6_vision_encoder.tex:8,22` | recipe 描述为 **"SigLIP sigmoid-contrastive + frozen text tower (12L, width 512, 8 heads)"** | 🔴🔴 | ✅ **已修 → 冻结 CLIP-ViT-L/14-336(768-d) + CLIP InfoNCE** |
| 6 | `6_vision_encoder.tex:115–117` | 断言「**this stage therefore has no working downstream metric**」 | 🔴🔴🔴 | ✅ **已改 → IN-1k**（R8 已用 IN-1k 替换退化的 R@1） |
| 7 | `6_vision_encoder.tex` 的 **tab:visarch / visarch_res / visres / visobj** | **四张表的数字全是 R1/R2 坍缩读数**（4.456x） | 🔴🔴🔴 | ✅ **已处理三张**：`tab:visarch` 换 R8 六架构表 · `tab:visarch_res` **删除**（坍缩伪影）· `tab:visres` 换 R5 P1；⚠️ **`tab:visobj` 未动**（其结论仍成立） |
| 9 | `6_vision_encoder.tex` 缺 **scaling 结果** | 论文**没有** R9/R10 的 scaling / 外推 | 🔴🔴 | ✅ **已新增** `\subsection{Scaling Behaviour}` + `tab:visscale`（3 塔 + 11 点 + 渐近 25.1% + w384 无饱和） |
| 10 | `7_mllm.tex:17` | 「architectural study **found resolution immaterial**」= 坍缩期读数 | 🟡 | ✅ **已改** → 「selected 224/16；能否迁移到细节密集视图正是 (iv) 要测的」 |
| 8 | `0_abstract.tex` / `5/7/8/9` | 4 处 `[TBD]`；abstract 的 `n=3` 已被 R2 扩到 `n=5` | 🟡 | 见 §3（未动，属"等结果"而非"陈旧"） |

---

## 1. §6 本轮已做的修补（逐条给证据）

### 1.1 recipe 修正（`6_vision_encoder.tex:8`）
- **原文**：`... a frozen shared text tower (12 layers, width~512, 8 heads, one BPE for all towers), the SigLIP sigmoid-contrastive objective, and a unified 500K subset of LLaVA-OneVision-1.5 ... lr 1e-3 ...`
- **问题**：这是 **R1/R2 的配方**。R4 已定位坍缩并改为 **冻结 CLIP 文本塔 + CLIP InfoNCE**；R8 的六架构对比明确用 **InfoNCE + 冻结 CLIP-768（77 硬约束）**，数据 = **Stanford GPIC `short`（~2.77M 对）**，lr **3e-3** / warmup **20** / bs64×8。
- **证据**：`ROUND8 §0`（架构 6 个 · 数据 GPIC short · InfoNCE · 冻结 CLIP-768 · lr 3e-3/warmup 20）；`ROUND9` 头部「recipe/文本塔/目标函数一律不变（R8 已验证：**冻结 CLIP-768 text + InfoNCE + lr 3e-3 / warmup 20 / bs64×8=512 负样本 / @224/16**）」。
- ✅ **已改**。

### 1.2 架构数 4 → 6（`6:7`、`3:40`）
- R8 把候选从 4 扩到 **6**：新增 **AIMv2** 与 **FastViTHD**（`ROUND8 §0`）。
- ✅ **已改**（`3_architecture.tex:40` 同步）。
- ⚠️ **待补**：R8 明确要求这两个标注为「**等参 500–600M from-scratch 改编（非官方模型）**」（`BAIZE_VISION_ENCODER_RESULT_ROUND8.html` 回填建议）→ 见 §2.1。

### 1.3 删掉「没有可用下游指标」的过时断言（`6:115–117`）
- **原文**：`... a zero-shot text↔image retrieval proxy (R@1/5/10 ...)` + `That proxy is degenerate: R@1=0.0002 ...` + `we note that this stage therefore has **no** working downstream metric---the main limitation of the comparison.`
- **问题**：R8 已**成功用 ImageNet-1k（zero-shot + linear-probe，frozen trunk）替换退化的 R@1**（`ROUND8 §0` 新指标 + `README` 三结论之③）。
- ✅ **已改**：保留"R@1 退化"作**方法论警示**（有价值），但把"no working downstream metric"改为「**we therefore replaced it with ImageNet-1k zero-shot and linear-probe on the frozen trunk**」并给出 R8 headline。

### 1.4 CLIP InfoNCE loss `2.894` → `3.2704`（`6:121`）
- 同文档 `tab:visobj`（第 106 行）已写 `3.2704`，正文第 121 行仍写 `2.894` → **自相矛盾**。
- `EXPERIMENTS_VISION_ROUND2`/`README`：**旧表写的 2.8941 是 lr=1e-3 下的值，实测应为 3.2704**。
- ✅ **已改**。

### 1.5 序列长度 4096 → 4094（`3_architecture.tex:30`）
- §4 明确报 **`8×4094≈32.7K tokens/step`**（`4_llm_pretrain.tex:40`），架构表却写 4096 → **报告口径应取实际跑的值 4094**。
- ✅ **已改**（并记录：2026-10-03 起**新实验**统一 4096，但**论文报的是历史运行，用 4094 才自洽**）。


---

## 2. ✅ 四张视觉表 —— **本轮已处理白三张，一张保留**

> 这四张表原本的数字**全是 R1/R2 坍缩期读数**（loss ≈ **4.456 / 4.466 / 4.470**；4.456 ≈ 坍缩均衡的算术值）。**继续留在论文里 = 用已被自己推翻的实验数据支撑 §6。** 本轮已按下列方案处理。

### 2.1 `tab:visarch` ✅ **已替换为 R8 六架构表**
（数据来自 `ROUND8 §4`；均 500–600M / GPIC short / InfoNCE / 3000 步 / lr 3e-3 / bs64×8）：

| Arch. | Params | loss@3k | img/s | zs t1/t5 | lp t1 |
|:--|--:|--:|--:|--:|--:|
| **OpenVision2** | 505.2M | **4.865** | 3052 | **0.95/3.64** | **1.14%** |
| MambaEye† | 535.2M | 6.251 | 950 | 0.10/0.50 | 0.10% |
| MoE-ViE | 505.5M | 5.558 | 1226 | 0.35/1.53 | 0.28% |
| DeepEncoderV2† | 517.2M | 6.251 | 1865 | 0.10/0.50 | 0.10% |
| AIMv2（adapt.） | 505.5M | 5.637 | **3393** | 0.38/1.61 | 0.25% |
| FastViTHD（adapt.） | 507.8M | 5.668 | 2097 | 0.39/1.57 | 0.27% |

> † = 坍缩熔断。另**已写入**「AIMv2 / FastViTHD 是我们的**等参改编**、非官方模型」这一限定。

### 2.2 `tab:visarch_res`（token 预算 × 4 架构）✅ **已删除**
- 四个格子都是 **4.456x**（坍缩读数），caption 自己写「within 0.0025 of each other」——**这正是 R3 判定「架构在 loss 上不可区分 = 坍缩伪影」的东西**。
- 其唯一 `\ref` 在旧的「architecture-invariant」结论句里，而该结论**已被同一编辑删除** → 无悬挂引用（编译已验证：0 undefined reference）。

### 2.3 `tab:visres`（分辨率/patch）✅ **已替换为 R5 P1**
- 旧表同为 4.456x 坍缩读数；新表 = **224/16 → 3.0977 / 336/14 → 3.1909 / 448/14 → 3.2711**（R5 P1 的干净结论）。
- caption 已注明**数据臂差异**（R5 用 LLaVA `imagenet/EN` 500K、`tab:visarch` 用 GPIC），避免读者误比 loss 量纲。

### 2.4 `tab:visobj`（目标函数 × lr）⚠️ **保留未动**
- 该表**基本正确**（SigLIP vs CLIP InfoNCE；lr 1e-3 坍缩 vs 3e-3 选中），已含修正后的 `3.2704`。
- 建议（未做）**补一行说明**：lr 1e-3 的坍缩是 **schedule collapse**，与 §2.1 的 **SSM 坍缩是两回事**（前者被 lr 修复，后者不是）。→ **留给下一轮或你定稿时**。

### 2.5 🆕 **已新增：R9/R10 的 scaling 结果**（论文原本**完全没有**）
新增 `\subsection{Scaling Behaviour}\label{sec:vis-scaling}` + `\begin{table}…\label{tab:visscale}`：

| 内容 | 数字（来源） |
|:--|:--|
| 缩塔先导（同数据同步数，只变塔宽） | w512 126.8M → **lp 6.10%** ／ w768 284.5M → 3.63% ／ w1024 505M → **1.03%**（`ROUND9 §3`） |
| 长训练（w512 × 108k 步 = 55.3M 样本） | lp 由 3.96%@5.1M 升至峰值 **7.70%**@51.2M（`tab:visscale`；`ROUND9 §4`） |
| scaling 拟合（11 点，R²≈0.94） | 幂律 `acc = 0.251 − 0.864·N^−0.090` → **渐近 25.1%**；斜率 **+4 lp 点 / 10× 数据** |
| 外推 | 20% 需 **6×10¹⁰**（对数线性）vs 本地 **≈1.2×10⁸** 上限 → **够不到**（**诚实的负结果**） |
| M 轴（R10，5 点） | **w384(71.5M) lp@15.4M = 7.99%（全部宽度最高）**；边际 **−2.2~−2.4 lp/参数翻倍**；**无饱和点** |

→ 结论句：**「瓶颈是数据量与目标函数，不是架构」**。


---

## 3. 其他（本轮**未动**，因为它们不是「陈旧」，而是「等结果」）

- **4 处 `[TBD]`**：`5_llm_posttrain:47` · `7_mllm:21` · `8_domain_rl:18` · `9_conclusion:5` —— 属 (ii)–(v) 阶段结果，**要等 P-8 + EDA-Eval**。
- **`0_abstract.tex`**：只写 Stage (i)，**没有任何视觉/scaling 结果** → 若采纳 §2.5，abstract 可补一句。
- **abstract 的 `three seeds`**：R2 的 P-2 已把 seed 扩到 **n=5（2.673386 ± 0.0349）**（`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`）；README 目前仍记 n=3 → **要不要改用 n=5 待你定**（属口径选择，不是错误）。
- **README §9 的论文层 TODO**（仍未做）：补 **Limitations** 节 · **§2 相关工作缺视觉编码器一线** · 去重 §3.1 与 §4.1(iii) · **页数上限确认**（当前 7 页）。

---

## 4. 引用的权威来源（便于复核）

- `run/EXPERIMENTS_VISION_ROUND8.md` §0/§3/§4/§7/§8 —— 六架构、SSM 熔断、IN-1k
- `run/EXPERIMENTS_VISION_ROUND9.md` §3/§4/§5 —— 缩塔先导、长训练、scaling 拟合与外推
- `run/EXPERIMENTS_VISION_ROUND{2,5}.md` —— lr 坍缩根因、R5 P1 分辨率
- `run/MEMORY_VISION.md` —— R10③ 5 点 M 重拟合、w384 7.99%
- `README.md` §1.1 —— Stage (i) 关键数字（2.220B / 2.2054 / 2.6739±0.0469）

---

## 5. 本轮**已改**的 `.tex` 清单（便于 `git diff` 复核）

| 文件 | 改动 |
|:--|:--|
| `1_intro.tex` | 第 3 段后**补 2 句**「为什么小」= **本地性**（专有设计产物不能出域）+ **长上下文服务成本**（仅 4 层 attention 随会话增长）—— **复用 §8 既有论证，不引入新框架** |
| `3_architecture.tex` | ① `Sequence length & 4096` → **`4094`**（与 §4 的 `8×4094` 对齐）② `four` → **`six`** candidates |
| `6_vision_encoder.tex` | ① 候选 **4 → 6**（+AIMv2/FastViTHD，并标明**等参改编、非官方模型**）② recipe → **冻结 CLIP-ViT-L/14-336(768-d) + CLIP InfoNCE + GPIC `short` + lr 3e-3 / warmup 20** ③ **`tab:visarch` 整表替换**为 R8 六架构表（含 **IN-1k zs/lp**）④ **删除** `tab:visarch_res`（坍缩伪影）⑤ `tab:visres` 换 **R5 P1** ⑥ **删掉被推翻的「architecture-invariant」结论** → 改为 **OpenVision2 四指标第一 + SSM 特异坍缩** ⑦ **新增 `\subsection{Scaling Behaviour}`**（R9 3 塔 + 11 点 + 渐近 25.1% + R10 w384 无饱和）⑧ 尾部「**no working downstream metric**」→ **IN-1k**，并去掉过时的 `2.894` 与旧分辨率/dummy-lr 论述 |
| `7_mllm.tex` | 「found **image resolution immaterial**」→ 「**selected 224/16**；能否迁移到细节密集视图正是 (iv) 要测的」 |
| `main.pdf` | **已重建**（**7 页**，与改前同页数） |

> ⚠️ **仍未动**：`tab:visobj`（§2.4：建议下一轮补一句「lr-坍缩 vs SSM-坍缩」的区分）· 4 处 `[TBD]` · abstract · §2 相关工作 · README §9 其余 TODO。
>
> **✅ 编译验证**：本机 MiKTeX（`pdflatex` 25.12.0）→ `pdflatex`×2 + `bibtex` + `pdflatex`×2 →
> **0 error · 0 undefined reference · 0 overfull hbox · `main.pdf` 7 页**。

