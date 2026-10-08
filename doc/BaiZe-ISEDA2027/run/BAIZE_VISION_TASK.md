# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_VISION.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_VISION.md` / `EXPERIMENTS_VISION*` / `daily-memories-vision/` / `vision/`）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_VISION.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。

---

### 🏆 最佳实践（BEST PRACTICES）— **2026-10-08 锁定 · 如无特殊指定，一律按此执行**

> 以下三项由 R2–R14 全线实验**预注册 + 收敛**后裁定，证据见对应报告/实验记录。
> **默认执行**：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> **不得回退**：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| **损失** | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| **文本塔** | 冻结 CLIP-ViT-L/14-336（768-d），**不**解冻 / **不**用 LoRA |
| **注意力** | **双向**（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| **证据** | R11-G：lp 7.40% → **19.76%**（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 **20.27%** |
| **否决项** | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| **报告** | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | **0.6** | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | **1.0 / 1.0**（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | **SGD + momentum 0.9 + cosine**（5-ep warmup） |
| Batch size | full-batch（49,970） | **mini-batch 1024** |
| Epochs | 100（= 100 次梯度更新） | **90**（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | **IN-1k full train = 1,281,167 张** |
| Eval 集 | 自切分 val（50/类 = 5,000） | **IN-1k 官方 validation（50k）** |
| Normalization | CLIP mean/std | **ImageNet mean/std** |
| 重复 | seed 0 单次 | **3 seeds（0,1,2）→ mean ± σ** |
| **证据** | Δlp ≈ **+10.05 pp**（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| **内部横比** | 旧实验（R2–R14）均用 Protocol A，相对排序**仍有效**（A/B 排序一致）；但**绝对数字**须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；**与 DINOv2/MAE/iBOT 等公开值可直接横比** |

> ⚠️ **Protocol A → B 迁移说明**：旧实验的**相对结论**（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，**不混表**。

---


> 📦 §运维指令 · 2026-10-08①（📝 更新论文 LaTeX）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：6_vision_encoder.tex 已更新（mask-ratio 表 + weight-ratio 表 + §VI-D AR 范式探索），main.pdf 11p 0err，commit 6f2baa2b。需要时再读。

> 📦 §运维指令 · 2026-10-08②（📄 全线总结报告 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：report_vision_encoder_final.html（28.6KB, 10 节/4SVG）+ report_vision_final_20261008.html（v2 最终版）已交付，commit 67a306f8。需要时再读。

> 📦 §运维指令 · 2026-10-07③（mask-ratio 消融报告 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_mask_ratio.html 已交付（34.3KB, 8节+2SVG, 倒U形 0.6 最优, commit ee9db3ca）。需要时再读。

> 📦 §运维指令 · 2026-10-07②（GPU12 对账簿）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：pretrain 借 GPU1–7 跑完长上下文成本矩阵后 09:44 已归还，GPU12_ALLOC.md 已建。需要时再读。

> 📦 §运维指令 · 2026-10-07（📊 昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_10_07_vision_overnight.html 已交付（自包含 27.7KB，内联 SVG，零外部依赖）。需要时再读。

### 🆕 运维指令 · 2026-10-06（✅ **批准 `VISION_AIMV2_OFFICIAL_PLAN.md`（方向⑤）** ＋ ⚠️ **开跑前必须先按下列 6 点修订方案**）· 高优先

> **用户已批准**「复现官方 AIMv2 纯 AR 范式，并与我们的 AIMv2 做量化对比」。**但要求开跑前先把下面 6 点写清/改对**（用户逐项审阅意见；**重点 = 问题 3 与问题 5**）。**这 6 点落实后即可按队列开跑，不必再等第二次批准**（前提仍是队列 ①②③ 已完成：R12b 训完 + lp 协议 A/B 跑完）。

**① §3.2 AR 前向语义 —— 必须写清「AR ≠ MAE」**
`MSE(pred[:, :-1], target[:, 1:])` 的 shift-by-1 是对的，但报告要**显式说明语义差异**：AR 是「**给定前文预测后文**」，**不是** MAE 的「给定上下文重建被遮位置」；并写明**位置 0 的输出只看到 patch 0 自身、位置 195 无 target 被 shift 掉**。否则读者会把两者混淆。

**② §3.1 text decoder 的 cross-attention 目标 —— 必须显式声明**
**必须写明「text decoder cross-attend 到 `causal` vision patches（每个 patch 只含前缀信息）」**（与官方一致）。🚫 若 attend 到**双向** patch 特征，就变成「双向 vision + causal text」，**不是**官方 AIMv2 范式 —— 请在方案里显式声明确认。

**③ §6 短 caption handicap（用户点名重点）**
官方用 **LLaMA-3 长合成 caption（~12B 样本）**，我们用**短 alt-text（CC12M / Amshaker / GPIC short）** ⇒ **text AR 的 next-token 信号天然弱**。**必须在方案与最终报告里显著标注该 handicap**，否则会把「**短 caption 不适合 text AR**」误读成「**官方 AIMv2 范式差**」。

**④ §4 吞吐预估 —— 先 smoke test，并预留更差情况**
**AR causal attention 的 FLOPs 不降**（SDPA + `attn_mask` 通常不省算力，还有 mask 开销）；text decoder 的 cross-attn 与 **`PatchPredictor` 对全部 196 位置**（vs 随机掩码 ~118 ⇒ +66%）都会增算 ⇒ **预留「实际吞吐可能只有 3500–4000 img/s」**。**必须先 smoke test**；⚠️ **若 30k 快速 A/B 的实际墙钟 >3h，需重新评估是否值得上 108k**。

**⑤ §3.3 B' 的参数量隔离（用户点名重点）—— 改成「缩宽度」而非「减深度」**
`depth=2` **隔离不干净**（浅 decoder 的表达能力本身就差 ⇒ 无法区分"参数少"还是"太浅"）⇒ **改为「保持 depth 不变、缩小 hidden dim」**使参数量对齐 Arm A；**并同时报告 B' 的 `cap_loss` 与 `pixel_loss`**（若 B' 的 cap_loss 明显更高 ⇒ 说明是 text AR 能力不足，而非参数量）。

**⑥ §5.2 判定规则 —— 补一个中间态**
加一档「**趋势性优势但不显著**」（**+0.5 < Δlp < +1.5**）⇒ 报告写「**AR 有正向趋势，但未达预注册显著性阈值，需更大规模验证**」；并写明「**Δlp 大但 C1 接近坍缩（如 C1=0.90）**」这类组合**怎么判**。

> **执行顺序**：① 先改 `VISION_AIMV2_OFFICIAL_PLAN.md` 落实上述 6 点 → 提交（版本/diff 记入 `MEMORY_VISION.md`）；② ✅ 然后按队列（**① lp 协议 A/B → ② mask-ratio → ③ 权重比 → ④ 本项**）开跑。🚫 **不打断 R12b**；每步 commit + push。


### 🆕 运维指令 · 2026-10-06（📋 **vision 后续队列裁定**：批「lp 协议 → mask-ratio + 权重比」；方向1 **不急** / 方向4 **作废**；**第三批 = 复现「官方 AIMv2」范式并做量化对比**）· 排队执行 · **不打断 R12b**

> **用户 2026-10-06 裁定（原文口径）**：
> 1. ✅ **「第二棒之后可以上 mask-ratio 消融 和 contrast : patch 权重比消融」** ⇒ **批准 `VISION_NEXT_DIRECTIONS.md` 方向 2 ＋ 方向 3**，**排在「lp 协议对齐研究」之后**，按该文件已写好的**预注册判据**执行（主指标 = IN-1k frozen-trunk lp @step30k；噪声带 ±1.5pp；**改 recipe ⇒ 单列，不并入 scaling 曲线**）。
> 2. ⏸ **方向 1（GPIC 全量 ~100M 重跑 AIMv2 scaling）＝ 不急** —— 用户原话「**首先 GPIC 还没下完**」⇒ **维持暂缓**；**等 GPIC 下载完成后先回报**（剩余量 / ETA / 唯一对估数），**再由运维定**。🚫 不要提前占卡。
> 3. 🚫 **方向 4（文本塔 full fine-tune）＝ 已作废** —— **条件不满足**：R11-L2 LoRA 实测**未翻盘**（Δlp −0.30 / −0.70 / −0.80）⇒ 按方向 4 自己写的「仅当 LoRA 有正面信号才提议」⇒ **取消**（已同步标注在 `VISION_NEXT_DIRECTIONS.md`）。
> 4. 🆕 **第三批（两个消融之后）＝ 实现「官方 AIMv2」范式，并与「我们的 AIMv2」做量化对比**（规格见下表）。⚠️ **本项比消融大 ⇒ 先交「实现方案 + 成本估算 + 预注册判据」，经运维批准再开跑。**

> **要实现什么（用户给的原表，作为规格）**：
>
> | 项 | **官方 AIMv2** | **我们（现状）** |
> |---|---|---|
> | **范式** | **纯 AR**（vision AR + text AR） | 非 AR：**双向 ViT + 随机掩码** |
> | **对比项** | ❌ **无** | ✅ **保留 InfoNCE** |
> | **掩码** | **prefix-attention（causal）** | **随机掩码**（每 patch 独立 0.6） |
> | **trunk forward** | **AR：前面可见、后面 mask token** | **全 patch 可见、无 mask token** |
> | **文本塔** | **可训 text AR decoder** | **冻结 CLIP-768** |
> | **损失** | `cap_loss + α × pixel_loss` | `1.0 × InfoNCE + 1.0 × patch_MSE` |
>
> **第三批的硬要求**：
> - 🔴 **许可证红线（先确认再动手）**：官方 `ml-aim/AIMv2` 仓库**只有模型接口、无训练/损失/数据**，**LICENSE = Apple Sample Code（research-only，🚫 不可 COPY）**（见 `VISION_OFFICIAL_REPOS_SURVEY.md`）⇒ **不得拷贝其代码**；**按论文描述自研实现**，并**标注「自研实现（非官方权重复现）」**。
> - **规模口径**：本项是**范式复现（controlled A/B）**，**不是**复刻官方 3B/12B 对；**必须与我们的 AIMv2 同塔（w512/d30/patch16/224²）、同数据、同 token 预算**，否则结论无意义。
> - **公平性**：报 **参数量（含 text decoder）+ 训练 token + 每步耗时**；不许只比 lp（沿用 `BAIZE_VISION_TASK.md §1` 公平性条款）。
> - **预注册判据**：先写清「官方式 AR 范式 vs 我们非 AR 范式」在**同规模**下的判定阈值（lp 差异 + 是否坍缩 C1–C4 + 成本比），**先定后测**。
> - **产出**：`report_vision_aimv2_official_vs_ours.html`（自包含：规格对照表 + 两臂结果 + 差异归因 + 论文 §6.3 措辞建议）。

> **执行顺序（排队）**：R12b 训完 → **① lp 协议对齐研究** → **② mask-ratio 消融（5 臂）** → **③ 权重比消融（4 臂）** → **④ 官方 AIMv2 范式复现对比（先交方案）**；**方向 1 等 GPIC 下载**。
> **纪律**：🚫 不打断 R12b / 不改正在跑的脚本 / 不下载大文件；每步 commit + push；每项带**时间盒 + 判据**，做不完**如实写卡点**。


> 📦 §运维指令 · 2026-10-06（🔬 lp 评测协议与主流对齐研究）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_lp_protocol.html 已交付（21.2KB, 2026-10-07）。需要时再读。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）**原文**搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `vision 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**24KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，**优先滚它**）。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，**data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 在改别的文件、push 得出去），**外部运维只能靠 git 判断死活** ⇒ 被**误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；loop 的兜底 push 间隔是 **5h**（本日已缩短），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底 push 一次」**不再作为交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**，**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

### 0. 🎯 当前状态速览（**每次唤醒先看这里**）

| 项 | 值（**2026-10-05 晚 运维更新**） |
|:--|:--|
| **GPU 状态** | 🚀 **R12 全量数据 AIMv2 训练中**（`.12` 8 卡，120k 步，16:43 起；吞吐随 NFS 争用波动 ~2300–5600 img/s）· **3-epoch 续跑 watcher 已就绪**（R12+eval 完自动接续）· 另有 **两份 HTML 报告**（纯 CPU/写作）待写 |
| **已完成** | ✅ R9/R10/R14/E1/R11-L 四臂/R11-L2/caption-weight/R11-E/R13（官方 OV2 **79.81%**）· ⭐ **臂⑥ AIMv2 翻盘**（lp 12.08% vs 6.08%，**+6.00 pp → 25.1% 局部推翻**）· ✅ **R11-F 五臂**（A/B/C/E/D）· ✅ **R11-G**（108k 长跑：lp@55.3M **19.76%** vs 基线 7.40%，幂律 **R²=0.91**）· ✅ **R11-H**（纯 AR **无翻盘** ⇒ 翻盘依赖对比项） |
| **🔜 下一步（✅ 已批准 · 严格按此顺序）** | 🔒 **①先「AIMv2 提速」**（归因实测 → 数据管线优化，见「运维前置」块）→ **②再用「全部现有数据」（GPIC ≈41% + CC12M + Amshaker ≈59.5M 对）跑 AIMv2**（先交**提速后**的「时长 / epoch」估算）→ **③训练稳态后自改论文 §6**（可用 `cimi_search`，仅该段解冻） |
| **可立即开跑** | ✅ **① AIMv2 提速（归因实测 + 数据管线优化）** —— `.12` 8 卡已空；**② 全量训练须待 ① 完成**（硬性前置） |
| **🚫 已裁定不做** | **臂⑤ GenLIP**（→ 用 `caption-loss-weight` 三点消融替代）· **R12 iGVLM / TuringViT**（无官方仓库，取消） |
| **⏸ 暂缓** | 无 —— 原「GPIC 到齐后重跑 scaling」已被用户**改为「用现有全部数据直接跑」**（见新块）；`R13` 已完成 |
| **叙事** | ✅ **锁定 A = 从零训练**（不改用预训练权重） |

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（**一次性质，对所有 R 生效**）


- 🚫 **不许闭门造车**：涉及"别人怎么做"（架构/loss/评测/数据）**必须去读官方仓库或论文原文**（能 clone 就 clone）—— **不得凭二手描述下结论**（本线已因此出错一次）。
- **不重跑已落盘训练**；**不改 R8/R9/R10 已落盘结论**（只在 §2 明确"修正"条目下补限定）。
- **控变量**：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- **公平性**：加 decoder 的臂**必须报「参数量 + 训练 token + 每步耗时」**，不许只比 acc。
- **预注册**：判据**先定后测**，不许事后改。
- **体积**：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` **各 ≤32KB**（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（**最高优先 · 纯 CPU · 与 R14/E1 合并做**）

| # | 修正 | 要点 |
|:--|:--|:--|
| **C1** | **数据量口径** | `r9_scaling.py:158` 的「本地 53M 上限」是 **`--local-cap-m default=53.0`＝假设、非实测**。按 DATA_RESEARCH 实测（GPIC **5 tar=53,637 图 → ~10,727/tar × 8000 ≈ 86M**）外推 → **本地全量上限 ≈103M**（GPIC 86M + CC12M 11M + Amshaker 6M）。→ 用**真实 cap 重算** R9 所有 "×N 缺口"（含 "226× the 53M cap"）；报告中**统一三类分母**：**R9 用过 18.5M / 盘上现有 ≈29M / 本地全量 ≈103M**，并标注**数据仍在下载（动态值）**。 |
| **C2** | **R8 结论加限定** | R8 的 6 架构**全是自研 from-scratch 等参改编**（`run/vision/models.py` 头行自证；R8 亦标「等参改编（非官方模型）」）→ **「SSM 坍缩」只能表述为「我们 recipe（冻结语义文本塔 + InfoNCE）下、我们自研改编版的坍缩」**，🚫 **不得**推广成「官方 MambaEye/DeepEncoderV2 会坍缩」。 |

### 3. 🔜 任务队列（**按优先级；不要跳序、并行不超过 2 项**）

| 序 | 任务 | 类型 | 前置 | 状态 |
|:--|:--|:--|:--|:--|
| **1** | **R14 官方仓库资源调研** | 调研 · 纯 CPU | — | ✅ **已完成** |
| **2** | **E1 GPIC 规模实测** + **R11-E 数据轴** | 轻(测) / **训** | 抽 tar | ✅ **E1 完成**（GPIC 全量 ≈**100.3M**）· 🟢 **R11-E 已批准 · 即刻执行**（「10.9M 同 N 两点」版，见上「运维指令 · 2026-10-04（四）」） |
| **3** | **R11-L loss 轴** | GPU | R14 完成 | ✅ **四臂全兑现、无一翻盘**（①基线 ②SigLIP ③LocalLoss ④CoCa） |
| **4** | ⭐ **R11-L2 文本塔解冻（LoRA/Adapter）** | GPU | — | 🟢 **已批准 · 下一优先级 · 立即执行**（见上「运维指令 · 2026-10-03（三）」） |
| **5** | 🆕 **`caption-loss-weight` 三点消融**（替代臂⑤ GenLIP） | GPU · 轻 | **R11-L2 之后** | 🆕 **已排期**（0.5 / 1.0 / 2.0，≈0.5–1 臂） |
| **6** | **R13 官方 vs 自研对照** | GPU · 轻 | ✅ **已批准** | ✅ **完成**（2026-10-04：官方 OV2 L/14@224 同口径 IN-1k lp=79.81% vs 自研 7.99%，补结论边界） |
| **7** | **臂⑥ AIMv2 式（patch + text 双 AR）** | GPU · 重 | **R11-L2 结果** | ⏸ **暂缓** |
| **8** | ~~**R12 iGVLM 指令条件化**~~ | — | — | ❌ **已取消**（**无官方仓库** → 不值得自研） |
| **9** | 🆕 **R11-F 数据源横向对比（含 GPIC caption 粒度轴）** | GPU | — | 🟢 **已批准 · 立即执行**（GPIC `short`/`medium`/`short+medium`(90%) vs en500k vs CC12M；见「运维指令 · 2026-10-04（六）」） |
| **10** | 🆕 **R11-G — AIMv2 长跑（108k 步）→ 重拟合 scaling 并外推** | GPU | R11-F | 🟢 **已批准**（见「运维指令 · 2026-10-04（七）」） |
| **11** | 🆕 **R11-H — 臂⑥-B 纯 AR（去对比项）** | GPU | R11-G | 🟢 **已批准**（同上） |

> **已合并（不再单列）**：**「R11-L3 读 OpenVision 官方代码」→ 并入 R14**；**「R11-D 的先验证 GPIC tar」→ 并入 E1/C1**。

---

### 5. 📚 背景参考（**输入素材，不是任务**）

- **`run/VISION_ARCH_FRONTIER_2026.md`** —— 2026 前沿架构调研（iGVLM / TuringViT / MambaEye / MoE-ViE / FastVLM）+ **与 R8 的逐项对照** + **§5 数据量口径错误更正**。
- **关键事实速查**：
  - R9 lp 渐近 **25.1%**（幂律 `acc=0.251−0.864·N^−0.090`，R²≈0.94）· 当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结 CLIP-768 文本塔 + InfoNCE**。
  - R10-② 二维拟合（3 点 M 轴）：**M 边际效应全区间为负**（≈ −2.2 lp pp/参数翻倍）→ 数据受限区间**加宽塔是负收益**。
  - `attention flash` 仅占 GPU 自耗 **0.7%**（P-4）· 分辨率 **224/16**。
- **已核实官方资源**（运维 2026-10-03）：
  - `UCSC-VLAA/OpenVision`（**Apache-2.0**；**同时支持「对比+生成」与「caption-only」两套目标**；**2026-08 已放出 decoder**；训练栈 **TPU/JAX**，PyTorch 侧基于 OpenCLIP fork）。
  - `apple-aiml-research/ml-aim`（**AIMv2-L 0.3B = 87.6% 冻结 trunk / 77.0% LiT zero-shot**；代码与权重均已发布；LICENSE 待逐字核实）。
- **数据侧硬约束（机制推断，⚠️ 须 R11 实测验证，不得当结论引用）**：我们 caption **偏短**（CC12M = alt-text 短句 / Amshaker = 中长 / GPIC short = 20 tok），官方用 **ReCap-DataComp-1B v2 的 LLaMA-3 长合成 caption** → **caption-only 生成式的监督密度会被我们的短 caption 拖累**；**AIMv2 式（含 patch 预测）不依赖 caption 丰富度**。
- **口径提醒**：R6/R7 的「**正式训练**切 GPIC `short`」是**另一条线**；**R9/R10 的 scaling 实际用的是 CC12M+Amshaker** —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ **21KB**、`MEMORY_VISION.md` ≈ **32KB（已贴上限）**。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_VISION.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的**巡检/流水条目**（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 ③ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（**为省 prompt token**）

ROUND 2–9 的完整任务原文已移至 **`run/vision/ARCHIVE_ROUNDS_2-9.md`**。

- 这些轮次**均已完成**；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- **需要查旧轮细节时**再去读归档文件；**不要**把整份归档读进上下文。
- 当前指令全部在**本文件上半部分**（运维指令区）。
