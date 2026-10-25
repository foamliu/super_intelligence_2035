# BAIZE_VISION_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 📄 运维指令 · 2026-10-24 16:1x（**写"下一步如何提升 ProtB 与 MLLM 成绩"报告**）· 用户直令 · 最高优先

> 用户原话：「vision：**下一步如何提升 ProtB 和 MLLM 成绩，写个报告。**」

> ✅ **DONE (wake #250, 2026-10-24 16:57)**：报告已交付 `reports/report_vision_next_steps_protb_mllm_zh.html`（21.1KB, 8 节, 0 script/0 外链, 生成器 `vision/generate_next_steps_protb_mllm_report.py`）。核心结论：12 集已饱和（4 臂 ProtB 跨度 6.15pp 但 MLLM 跨度 0.34pp，逐集最大跨度 1.66pp，多数 <1σ）→ 单一建议 = 先做 B4（MMBench/MMVet/MathVista + 336anyres 在已有 ArmB/ArmE-R2 ckpt 重测, ~0 GPU·h）判定「评测盲区 vs 真失效」；顺带 A3（ckpt_60000 跑 ProtB, ~0.3 GPU·h）。ProtB 仍有 ~14–19pp 理论空间（vs CLIP@336 82.66%）但主因是预训练。本轮未启动训练/未动产物。**WAITING: 0**。

**① 交付物**：`reports/report_vision_next_steps_protb_mllm_zh.html`（自包含单文件中文 HTML）

**② 先摆清现状（这是分析的起点，必须写准）**

| 阶段 | 结果 | 对比 |
|---|---|---|
| **ProtB（编码器）** | **ArmE-R2 lp 68.236±0.0182 / 5-NN 58.904** | 🏆 全实验最高（vs ArmD-R2 **Δlp+3.899 / Δ5-NN+2.948**）|
| **MLLM（12 集）** | **ArmE-R2 avg 26.10%** | vs ArmD-R2 26.12%（**−0.02pp**）/ vs ArmC 25.78%（+0.32）/ vs ArmB 26.10%（0.00）|
| **裁定** | **不可分辨（边界值）** | 落在 22–26.5% 带 |

**核心矛盾（报告必须先讲透）**：
> **编码器涨了 +3.9pp，MLLM 下游却 −0.02pp** → **ProtB→MLLM 传递性再次证伪**（ArmD-R2 时已证伪一次，ArmE-R2 用更大的 ViT-L/14 再次印证）。
> **ViT-L/14（304M）比 B/16（86M）大 3.5×，MLLM 12 集仍持平 → 容量不是 MLLM 下游瓶颈。**

**③ 报告必须回答两条主线**

**A. 如何继续提升 ProtB（编码器）** —— 给 3-5 个**具体可执行**的方向，每条给证据：
- 现有 best 是 **lp 68.236**，参考系：CLIP ViT-L/14@336 自测 82.66%、文献 ~88.1% → **还有 ~14-20pp 空间**
- 候选方向（你有权增删，但每条要给出**预期增益 + 成本 + 判据**）：
  - 分辨率（224 → 336）：ViT-L/14 在 336 下的已知增益
  - 训练时长/epoch（当前 3 epoch）
  - 数据质量/配比（6 源是否最优）
  - 损失权重（contrast:patch = 1:1 是否最优，历史 R11 曾测过）
  - **末段抖动问题**：MEMORY 提到"ProtB 用 s63400 末段抖动态，final lp 可能低于 best 段" → **取 best 段 ckpt 是否会直接提升 1-2pp？**
  - 更大模型（ViT-H/14？代价？）

**B. 如何让 MLLM 下游真正提升** —— 这是**更关键**的问题，因为编码器涨了 MLLM 不涨：
- **必须回答：为什么传递性失效？** 给出假设并设计**可判定的实验**
  - 假设 1：Stage-2 数据（LLaVA-NeXT-780k 原版 quick-start 子集，738K 样本）太弱/太小 → 是否该上完整 780K 或用 opt47？
  - 假设 2：连接层（projector）训练不足 → 是否该加长 Stage-1 / 提高 projector lr？
  - 假设 3：LoRA 容量不足（Stage-1.5 20000 步）→ 是否该全参微调或加秩？
  - 假设 4：**12 集 benchmark 本身饱和在 26% 带**（ArmB/ArmC/ArmD-R2/ArmE-R2 全在 25.78–26.12%，跨度仅 0.34pp）→ **benchmark 是否已到分辨率上限，测不出差异？** 这条必须严肃评估：如果是，说明**当前评测集对编码器差异不敏感**，需要换/扩评测集（如 MMStar、MMBench、RealWorldQA 等更难集）
  - 假设 5：视觉 token 数（256 for ViT-L/14 vs 196 for B/16）对 LLM 上下文的影响

**④ 对每条方向必须给出（表格化）**
`方向 | 预期增益 | 成本(GPU·h) | 风险 | 可判定判据 | 优先级`
**判据必须是可证伪的**（如"若假设 4 成立，则换 MMStar 后 ArmB vs ArmE-R2 的 Δ 应 > 2pp"）。

**⑤ 最后给结论**
- **下一步最该做的一件事**（单一建议，不要摊大饼）
- 若判断"当前 12 集测不出编码器差异"，**要明确说出来并给出替代评测集方案** —— 这比继续堆实验更有价值

**⑥ 纪律**
- ✅ 所有数字必须能溯源到 `EXPERIMENTS_VISION.md` / MEMORY / 报告文件
- 🚫 不启动新训练（**本轮只出方案报告**，等用户批准）
- 🚫 不动 ArmB/C/D/E 产物
- ⚠️ 若某项是"推测"，**必须标注"推测·未验证"**，不许混进结论


> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

### 📄 运维指令 · 2026-10-24 10:3x（**ArmE-R2 完整实验 → 中文 HTML 报告**）· 用户直令 · 最高优先

> 用户原话：「让 vision 写上一份实验的 HTML 中文报告。」

> ✅ **DONE (wake #247, 2026-10-24 12:57)**：完整 7 节中文 HTML 报告已交付 `reports/report_vision_armE_r2_20261024_zh.html`（26522B / 7 节：①摘要 ②配置与口径 ③训练 ④ProtB ⑤MLLM三阶段 ⑥12集 ⑦结论+复现命令 / 0 `<script>` / 0 外链 / 标签配平）；`EXPERIMENTS_VISION.md §15` 已链接；旧版 17KB（`report_vision_armE_r2_20261022_mllm_stage4_zh.html`）保留备查；生成器 `vision/generate_armE_r2_full_report.py`；commit e8dc74489 全闭合。**wake #267 复核：报告在位 ✅、7 节齐全 ✅（grep 逐节确认），未重做。**

**① 现状（先看清差什么）**
- 已有 `run/reports/report_vision_armE_r2_20261022_mllm_stage4_zh.html`（17,136B）只含 **摘要 / 配置 / ProtB / 12 集 / 结论 / 文件路径** 六节 —— **缺 ①训练段、③MLLM 三阶段**，且不在主报告目录。
- 本轮 = **补齐 + 归位**，不是重写另一个版本。

**② 交付**：`reports/report_vision_armE_r2_20261024_zh.html`（**单文件自包含**，无外链 CDN、无 `<script>`，标签配平）。必含 7 节：
1. **摘要**（≤6 条）：ProtB **68.236% 🏆 全实验最高** · 12 集 **26.10%** · vs ArmD-R2 **−0.02pp 不可分辨** · 容量≠MLLM 下游瓶颈 · ProtB→MLLM 传递性证伪 · eval bridge 修复
2. **配置与口径**：ArmE-R2 vs ArmD-R2 = **三变量**（塔 B/16→L/14 + LR 1e-3→5e-4 + warmup 2000→3000，**不得单归因**）；vs ArmC/ArmB 的对照边界；数据 6 源 173.1M 对 / GBS 8192 / 63,400 步 / seed 1234
3. **① 训练（新增）**：T0 与总耗时（≈37.2h）、0.47–0.48 it/s、loss/contr/patch/C1 的 8–10 个里程碑点、**spike 统计**（次数/峰值/谷底/恢复步数，与 ArmE 发散对比）、ckpt 落盘清单、**0 nan/0 oom 的 grep 原文行**
4. **② ProtB**：lp **68.236±0.0182** / 5-NN **58.904**，逐 seed（68.212/68.256/68.240），四臂对比表 + Δpp
5. **③ MLLM 三阶段（新增）**：Stage-1 2500 步 / Stage-1.5 LoRA 20000 步 / Stage-2 3500 步的 loss 与耗时；**eval bridge bug**（196→256 patch tokens）根因、现象（8 卡全崩）、修法（3 处动态计算）
6. **④ 12 集逐集表**：12 行 × [ArmE-R2 / ArmD-R2 / Δ]，avg(除 MME) **26.10 vs 26.12 = −0.02pp**；注明 22–26.5% 不可分辨带
7. **结论与局限** + **复现命令**（训练 / ProtB / 12 集 三条）

**③ 数据纪律**：每个数字必须能追到文件 —— `run/vision/armE_r2_20261022_protb_vitl14_224_results.json`、`run/vision/results/` 下 12 集 json、训练 log、`run/EXPERIMENTS_VISION.md §15`。🚫 不许估算/编造；取不到就写 `N/A` + 原因。

**④ 收尾**：`run/EXPERIMENTS_VISION.md §15` 链到新报告（旧 17KB 版保留，标注"旧版"）；**本轮先归档任务书**（现 31.5KB，加本块会越 32KB ⇒ 按体积规程把已闭合的 ArmE/ArmD 旧块搬 `run/ARCHIVE_OPERATOR_VISION.md`，留 1 行指针，降到 ≤32KB）；commit `vision report:`；push 后 `git status -sb` 无 ahead/behind。

> **已归档**（2026-10-24 11:43）：🔴 运维指令 · 2026-10-22 14:2x（**停止 ArmE → 降 LR 重跑 ArmE-R2：5e-4 + warmup 3000**）· 用户直令 · 最高优先 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


> **已归档**（2026-10-24 11:43）：🚀 运维指令 · 2026-10-21 20:4x（**启动 ArmE：唯一变量 = 视觉塔换 open_clip ViT-L/14-224 (430M)**）· 用户直令 · 最高优先 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


> **已归档**（2026-10-24 11:43）：🔓 运维指令 · 2026-10-21（**Stage-2 改用原版 LLaVA-NeXT-780k 数据**）· 已闭环 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 📦 运维指令 · 2026-10-20 08:2x（**ArmD-R2：LR 1e-3 / min_LR 1e-5 / 数据不变**）· 用户直令 · 最高优先 — 已归档

> **已闭合**（ArmD-R2 全链路 DONE 2026-10-21：①训练✅63400步 / ②ProtB✅lp64.3373·5-NN55.956 / ③MLLM三阶段✅Stage-2原版数据 / ④12集✅avg26.12% / ⑤报告✅）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-21 归档）。**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp/Δ5-NN+1.238pp 双双正向；MLLM下游几乎持平→ProtB→MLLM传递性再次证伪。ArmD-R2 是 ArmE 的对照基线（口径值见上方 ArmE 块口径表）。需要时再读。
> **已归档**（2026-10-24 11:43）：🔥 运维令 · 2026-10-19 22:5x（**立即启动 ArmD，不要再 idle**）· 用户直令「vision：尽快启动」 — 原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 📦 已归档（08:2x）：ArmD 原始块（2026-10-19 21:2x）

> 已被 **08:2x「ArmD-R2」块**取代（LR 2e-3→1e-3，数据不变）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🆕 运维指令 · 2026-10-17（📄 ArmA 结果中文报告 + 归档 · 🔌 open_clip × AIMv2-style 兼容性工程评估）· 用户直令 · 最高优先

> **用户令（2026-10-17）**：「vision：把 ArmA 结果写成中文报告并归档。问题：open_clip 接口和AIMv2-style不能兼容吗？」

**① 报告（先做，纯写作零 GPU）**：`reports/report_vision_armA_openclip_result_zh.html`，中文自包含，必须含：
- **协议**：ProtB（full IN-1k 1.28M train + 50k val，SGD 90 epochs，seeds 0/1/2），`feature=projected`，ckpt=`latest.pt`；数字取 `run/vision/armA_protb_vitb16_224_results.json`（lp 58.02/58.07/58.02 → **58.03±0.02%**；5-NN **53.98%**）。
- **训练口径**：open_clip **ViT-B/16 224**（visual 86.2M / total 149.6M，双塔随机初始化）、**ClipLoss InfoNCE**、GBS 2048（MBS 256×8）、LR 2e-3→2e-4（warmup 8000）、**154,500 步**、数据 GPIC(7437)+CC12M(1100)+Amshaker(2250)=10,787 shards ≈118M 对；证据 `run_armA_openclip.sh:13-15,45-52` + `armA_openclip_train.py:169-187,256-316`。
- **对比表**（同表列：协议/塔/参数量/目标/步数/数据/ProtB lp/5-NN）：ArmA vs **④-4ep（67.05±0.02 / 42.35）**、④-2ep、V3、R11-G 等，数值以 `EXPERIMENTS_VISION.md` 既有记录为准。
- **关键解读（必须写）**：ArmA = **lp −9.02pp / 5-NN +11.63pp** ⇒ 检索型表征强、线性可分性弱，与「C1/lp 背离」假设一致；⚠️ **不是单变量对照**（塔 86.2M vs 126.8M、目标 InfoNCE vs AIMv2-style dense、步数/样本不同）⇒ **不得写成「AIMv2 目标比 InfoNCE 好 9pp」**。
- **诚实条款**：内部 ProtB 口径、非官方榜；单 backbone/单预算点；5-NN 与 lp 口径不同；仅评测 3 seeds（训练单 seed）。
- **归档**：报告 + 结果 JSON + 训练/评测日志路径写入 `MEMORY_VISION.md` 与 `EXPERIMENTS_VISION.md` 新 §「ArmA（open_clip ViT-B/16, 2026-10-17）」；commit `vision armA:`。

**② 回答问题（报告附录 A，必须给结论 + 代码行号）**：
- **结论：分两层 —— 模型/推理接口兼容；open_clip 自带「训练损失/循环」不兼容（需自定义，不是不能做）。**
- **兼容证据**：ArmA 用的就是 open_clip 模型，`model(imgs, texts) → (img_feat, txt_feat, logit_scale)` + `ClipLoss`（`armA_openclip_train.py:286-287`）；导出侧只需 `encode_image` 的 pooled/patch 输出（`mllm_bridge/open_clip_baize.py:8-16,26-34`）。predictor 是训练期辅助头，**不进入推理图** ⇒ 不影响 open_clip 加载/评测。
- **不兼容点**：open_clip 的 loss 家族（Clip/SigLIP/CoCa/GenLIP…）**没有 patch 级重建目标**；其训练循环只吃 `(image,text)`，不提供 mask 采样/patch 目标。我们这套 AIMv2-style 是**自研训练环**：`loss = contrast_weight×InfoNCE + patch_loss_weight×MSE(predictor(patches[mask]), target[mask])`，`mask_ratio=0.6`（`r9_train.py:782-807`；实现说明 `reports/report_vision_aimv2_impl.html`）。
- **做「open_clip 模型 + AIMv2-style」需要 4 件事（≈1–2 人日，纯 CPU）**：
  1. 在 open_clip ViT 上挂 `PatchPredictor`（≈0.66M）；
  2. 取 patch tokens（按 open_clip 版本用 `visual.forward_features` / `visual.trunk.patch_embed` / `forward_intermediates` 之一，或用 forward hook **复用同一次前向**，避免二次算力；实现前先 `python -c` 打印 `type(model.visual)` 与可用方法并截图/日志存证）；
  3. 自定义 loss + 训练步（照 ArmA 循环改 ≈50 行）；
  4. ckpt 存 predictor；**导出 open_clip 权重时必须剥离 predictor**（或单独存 `predictor.pt`），否则 `load_state_dict(strict=True)` 会报 unexpected keys；若 `contrast_weight=0`（纯 AR）→ `find_unused_parameters=True` 或冻结文本塔（ArmA 现为 `False`）。
- **概念澄清**：官方 AIMv2 = 多模态自回归（图文 token + decoder，弃用对比），open_clip 的对比接口无法表达；本仓 `r9_train.py` 的 `aimv2_ar` + `decoder_depth` 才是那一支。报告须分开写，避免混淆。

**③ ArmB**：配方/起训/排队**已被 2026-10-17 12:0x 顶部指令取代**（open_clip ViT-B/16 + AIMv2-style，全量 8000 GPIC，3 epoch）；本条只保留 **① 报告** 与 **② 兼容性附录**。预注册判据仍有效：lp ≥58.03% 不倒退；≥61.0% 且 5-NN ≥48.98% → 接受混合；否则写负面结论。

**④ 纪律**：不占 GPU（除放行）；每个数字可溯源到 `文件:行`/原始日志；不改已发布数值；与 pretrain 线 IO 错峰。


> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
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


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


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

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

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
