# BAIZE_VISION_TASK.md

### 📦 §用户令·2026-11-16 21:2x（vision 自行到 36.15 挖 waveview case · 不再等 designflow task2）✅ 已交付（wake#1461：1606 题池(A352/B390/C418/D446)→双判 273→可判分 225→带可见图 10→可跑集(带图∧V-A) 10；V-A 124/V-B 101，10 带图全 V-A；三方对账 case_id+sha256 全重合·新增 0·缺失 0·sha256 10/10 匹配。交付 vision/waveview_cases_mined.jsonl(273·A124/B101/NA48)+reports/report_vision_waveview_mining_zh.html(14547B 0外链0script)+vision/waveview_mining/(mine_3615.py 只读+raw)。§8 新增可跑=0<阈值≥3→不启动 V0/V1。全程只读未改 designflow·modified=false。commit `vision mining:`）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 wake#1462 归档）。需要时再读。


> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不编造数字/文献、负结果照写）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定技术路线、实验设计与工具选择；用证据说话，用结果说服。**

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 §用户令·2026-11-07 10:10（阶段2 放行·CPU 放开试各种 idea）✅ 已交付（wake#893：6 项授权变更 v2–v5 全试，v5 获统计显著正结果 A16%→B37%→C53% p=0.0009）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。

### 📦 §用户令·2026-11-07 09:2x（走出「干等 GPU」·用 .12/.29 CPU 设计有效 RL 证明 Qwen3.5-2B 波形理解显著提升）✅ 已交付（wake#893：数据集调研+技术栈冒烟+RL 方案+CPU 实验(含对照与显著性)+中文 HTML 报告 全部交付）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。


> 📦 已归档（2026-10-30~31，ViT-L 68.236% / MLLM 26.10% 写进论文 ch6/ch7、6_vision_encoder.tex 重写、第6章审校修订、波形图强化 RL 计划书、2B MLLM 看懂波形图能力报告）→ run/ARCHIVE_OPERATOR_VISION.md（wake#424/#435/#436/#437/#439）。需要时再读。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 📦 §用户令·2026-11-15 07:2x（解两条真阻塞：① SSH 自建 VQA 通道 ② 自行 SSH 36.15 取 WaveView 真题）✅ 已交付（wake#1288：① 反向转发 `ssh -p3333 -R 1300x`+forwarder·容器视角 10.247.64.1:3000x curl /health 三端口全 ok·MCP initialize 成功·断线 ~6s watchdog 自愈·桥接后答对真题；② 真题 10 道·check.py 原样·sha256 校验只读复制；③ 真题三段 V0=0/V1=0/V2=1/10·McNemar p=1.0(n=10 不足仅参考)·cheat=0。交付 vision_vqa_ssh_bridge.md+vision_ssh_bridge_proof.txt+vision/real_waveview_index.json+vision_real_waveview_intake.md+原地覆盖 report_vision_waveview_selftest_agent_zh.html 31875B）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 wake#1462 归档）。需要时再读。


### 📦 §用户令·2026-11-14 17:2x（为 v2 显著正结果写正式成果报告）✅ 已交付（reports/report_vision_cot_vqa_result_zh.html 23410B·中文·单文件·0外链·0script·内联SVG·7节：关键数字卡片(60→90%·McNemar b=7/c=0 p=0.0156)+预注册判据+溯源+方法+全链路对比表+3seed+技能分解+翻转7题+诚实性声明+可复现清单）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 wake#1462 归档）。需要时再读。

---

### 📦 §用户令·2026-11-14 10:3x（designflow 协作通道已建好）✅ 已交付（VQA tool 封装 + waveview 真题 + WAVEVIEW_COLLAB 交接区均落地，见 07:2x 交付）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 归档）。需要时再读。

### 📦 §用户令·2026-11-14 09:5x（designflow 不再降级多模态题·口径变更）✅ 已交付（waveview 题已恢复 answer-validation 形态，wake#1458 挖掘据此口径）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 归档）。需要时再读。

### 📦 §用户令·2026-11-14 09:1x（四件事：NeurIPS §6 / designflow 评 waveview / VQA tool 对比 / 强化识图）✅ 已交付（6_domain_rl.tex TBD=0 · VQA tool · 强化 v2 RFT 60→90% p=0.0156 · 报告齐）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 归档）。需要时再读。

### 📦 §用户令·2026-11-14 08:4x（waveview failed 分析 α/β/γ）✅ 已交付（report_vision_waveview_failed_analysis_zh.html 42530B）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-16 归档）。需要时再读。


> 📦 §用户令·2026-11-06 21:3x（advantage 方差诊断）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#838 判定 PARTIAL（std=0=78.7%/全0=0%/全同档=无信号根因），建议 group_size→8+按目标差异化+奖励连续化(需批)。需要时再读。

> 📦 §用户令·2026-11-06 18:5x（vision 先上 CPU）**✅ 已交付**（wake#827-#835：P0 冒烟 5 步 365s（73s/步）、P1 50 步 ~2min/步、4 个 eval JSON、报告 15058B、EXPERIMENTS §21；结论 post-GRPO 6.2% < post-SFT 9.2% 未提升）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### 📦 §运维令·2026-11-05 17:5x（执行波形 RL 计划：Stage-1W SFT → Stage-2W GRPO · 分阶段）· ✅ 阶段0+阶段1 已交付 → 原文见 `ARCHIVE_OPERATOR_VISION.md`

> **用户令**：「vision：执行 2026-10-31 波形 RL 计划书（`reports/report_vision_wave_rl_plan_zh.html`），让 2B MLLM 通过与 WaveView 交互学会看懂波形图。分阶段，先解锁待核项再训练。」
> **交付进展**：阶段0（WaveView/FSDB 解锁 + Gym 冒烟）✅ · 阶段1 SFT 验收 PASS（format 100%/submit 100%）✅ · Phase2 **CPU pilot 全链路 PASS**（诚实负结果 post-GRPO 6.2% < post-SFT 9.2%）✅ · advantage 诊断 gs4/gs8 双轮 ✅（PARTIAL，离散分档是全同档根因）。**阶段2 正式 GRPO 需 GPU —— 已被 2026-11-07 用户令改为「改用 CPU 重新设计」路线，见顶部新令。** 需要细节读 archive / 各阶段报告。
> 📦 已归档（2026-10-17 ~ 10-26）：ArmA/B/C/D 系列指令 + OCR 三条调研/路线令 + Milestone 报告令 + 08:2x ArmD-R2 整块→ `run/ARCHIVE_OPERATOR_VISION.md`（wake#133/#247/#250/#271/#272/#275/#279 交付）。需要时再读。
### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-17（ArmA 中文报告 + open_clip×AIMv2-style 兼容性评估）**已完成**（wake#133：数字全溯源 EXPERIMENTS §10，不得写「AIMv2好 9pp」）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> **历史配置参考**（不是禁令）：下表是已实验过的旧配置及其结果，供**知情决策**用。若你想重试，请说明「为什么这次会不同」（新数据/新方法/新预算），并把两者结果并列上报。

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

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。

> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）

- **外部证据**：涉及"别人怎么做"（架构/loss/评测/数据），优先读官方仓库或论文原文（能 clone 就 clone）；二手描述可以当线索，但结论要自己有依据（本线曾因此出错过一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂需报「参数量 + 训练 token + 每步耗时」，与 acc 并列（否则不是同一把尺子）。
- **判据先行**：判据在测之前定好，测完就按那个判；若中途发现判据本身有问题，写清「原判据 → 为何要改 → 改后的结论是否仍成立」。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
