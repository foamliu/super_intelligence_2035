# BAIZE_VISION_TASK.md

### 🔴 用户令 · 2026-11-24 08:5x（放行下一步：GRPO 改进 + 真题复测）

> **Option B 已验收**（SFT 3-seed 74.4% / RFT2 90% / GRPO 86.7% 负结果如实记录）。现在放行 vision agent 自己提出的 4 条改进建议（来自 GRPO 报告 §5.5），按以下优先级执行：
>
> **P1 — GRPO 改进训练（GPU 6-7）**：
> 1. **从 SFT 冷启动**（而非已 0.90 的 RFT2），留出 headroom 让 GRPO 有学习空间。
> 2. **奖励分解**：把 reward 从「全对=1 / 全错=0」改为「区间内 vs 越界」分段奖励，β>α（越界惩罚大于区间内奖励），减少全对饱和（189/224 步 reward=1.0 的根因）。
> 3. **更难/长尾训练题**：增加噪声、多通道、非整数周期等难例，提高 group 内奖励方差（当前仅 2/224 步有梯度）。
> 4. **跑 ≥500 步**，报 reward 曲线 + cheat rate + 配对检验（与冷启动对比，McNemar / paired bootstrap）。
>
> **P2 — 真题 benchmark 复测**：
> 1. 把 post-GRPO adapter 装入 `:30003`，**在 EDA-Eval-DesignFlow-WaveView 全队列（182 case）重跑 V2 臂**。
> 2. 与现有 V2=17.6% 基线做配对检验，看改进后的 adapter 是否在真题上也有提升。
> 3. 如果新 GRPO 跑出了比 rft2_adapter_seed11 更好的 adapter，用新 adapter 重跑；否则用现有 rft2 adapter 复测确认 baseline 可复现。
>
> **P3 — 交付**：
> 1. 更新 `report_vision_wave_grpo_mllm_result_zh.html`：新增 GRPOv2 结果节（改进点 + 数字 + 对比表 + 负结果照写）。
> 2. 更新 `report_vision_waveview_selftest_agent_zh.html` §0.6：如果真题复测有新数字，追加一行。
> 3. 心跳 + daily 照常。
>
> **约束**：
> - 预注册：开跑前先在 MEMORY 写明臂设计 + 判据，跑完不许改判据。
> - 反作弊常开，报 cheat rate。
> - GPU 6-7 可用（:30001/:30003 服务不停）；SSH 桥到 36.15 保持。
> - 负结果照写，不许粉饰。
> - WAITING=0（无阻塞，连续推进）。

### 📦 §用户令·2026-11-20 16:2x（写 vision 工作总报告）✅ 已交付（wake#1708+：`report_vision_overall_work_zh.html` 38460B 已 ON origin，`git cat-file -e` OK）。需要时再读。

### 📦 §用户令·2026-11-20 08:4x（诊断 posttrain loop 存活性 + 修 git 推送）✅ 已交付（wake#1702/1703/1704：posttrain loop **DEAD** 确认·`baize_posttrain_loop.sh` worktree 隔离 `git_sync_and_push()` 改造 + 13 段白名单 + `bash -n` PASS·报告 `run/reports/report_posttrain_loop_git_diag_zh.html` 19002B·5 交付文件全 ON origin `f831265a9`（`merge-base --is-ancestor` EXIT0）·未重启/未 kill/未 reset --hard/未声称一次过 push·待运维带正确 PATH 重启 loop）→ 详见报告 + `MEMORY_VISION.md` wake#1702/1703/1704；原文指令见 git history commit `f831265a9`。需要时再读。

### 📦 §用户令·2026-11-16 21:2x（vision 自行到 36.15 挖 waveview case）✅ 已交付（wake#1461：273 双判→225 可判分→10 带图可跑；交付 waveview_cases_mined.jsonl + report_vision_waveview_mining_zh.html + mine_3615.py）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`「归档 · 2026-11-19 §A」。需要时再读。



> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不编造数字/文献、负结果照写）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定技术路线、实验设计与工具选择；用证据说话，用结果说服。**

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：默认只写本线文件与目录。但**你有权自主 SSH 到用户放行的远程机器**（如 36.15）读取、检索、复制数据，不必等别线供给。跨线需要**修改**别线文件时先在 MEMORY 记一行，但**只读操作（grep/ls/cat/ssh 检索）不受此限**。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 §用户令·2026-11-07 两条（10:10 阶段2 放行·CPU 试各种 idea；09:2x 走出「干等 GPU」用 .12/.29 CPU 做 RL）✅ 均已交付（wake#893：v2–v5 全试，v5 统计显著正结果 A16%→B37%→C53% p=0.0009；含数据集调研/技术栈冒烟/RL 方案/CPU 实验/中文 HTML 报告）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（wake#1212 归档）。需要时再读。



> 📦 已归档（2026-10-30~31，ViT-L 68.236% / MLLM 26.10% 写进论文 ch6/ch7、6_vision_encoder.tex 重写、第6章审校修订、波形图强化 RL 计划书、2B MLLM 看懂波形图能力报告）→ run/ARCHIVE_OPERATOR_VISION.md（wake#424/#435/#436/#437/#439）。需要时再读。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 用户令 · 2026-11-19 22:1x（**排障：你与 post-train 共用 .17 同一份仓库目录 → 冲突 / 它的记忆推不上来**）

> **用户原话**：「vision 和 post-train 在一台服务器，共享仓库目录。之前 post-train 总是抱怨跟 vision 有冲突，最新的记忆推不上来。**请 vision 看一下这个情况**。」
> ⇒ 这条令的**执行人是 vision 线**，不是运维。运维只给线索与参考实现，取证/整改/验收由你完成。

**一、要你查清的事（带证据，不许只写结论）**
1. 共享工作副本当前状态：`git -C <共享根> status --porcelain`、`stash list`（历史上有 **stash `d5427b789`** 卡在 `MEMORY_VISION.md` / `daily-memories-vision` 上，posttrain 2026-11-16 记录「autostash 冲突系 vision 文件，非本线，留 stash 不动」——**这个 stash 该由你判读后处理**）、`rebase-merge/` 残留、`.git/index.lock` 争用事件。
2. 共享 HEAD 与 `origin/main` 的分叉：你在 wake#1686 自记「共享 HEAD=`2749fa3ca` 8 ahead（内容已在 origin）」，现在还是不是？分叉是什么造成的？
3. 你历史上的 `git add -A` 提交里混入了哪些别线文件（列 commit + 路径）——这是 posttrain rebase 必冲突的根因之一。
4. posttrain 侧症状对照：它在 daily 记的 `Unable to create index.lock`、`autostash 冲突`、`rejected (fetch first)` 各出现在哪几轮。

**二、要你落地的整改（这是重点）**
1. **推送改为 worktree 隔离**（你 wake#1686 已自证可行）：共享工作树只读只跑，提交一律在 `/tmp/gitpush_vision` 之类的 **detached worktree** 里做，只 `git add` 本线路径。**固化为默认做法**，写进你的 MEMORY 常驻段。
2. 共享树**清理到可用态**：处理掉卡住的 stash（判读后：属你线的就 pop/落盘，不属你线的**保留并写明**，禁止删别线 stash）；若共享 HEAD 与 origin 分叉且工作树干净，用 `merge --ff-only` 对齐；**任何情况下不得 `reset --hard` / `clean -xfd`**（会毁别线在途）。
3. 产出一页 **RCA**（症状→根因→证据→修法→回滚），并把「共享副本 git 协议」写成 **posttrain 能照抄的命令块**（它下一轮唤醒要直接用）。落点：本线报告或 `run/vision/` 下 md，同时在 MEMORY 记一行指针。
4. 参考（可选，**必须自己核验后才可用**）：运维已放 `run/ops/SHARED_REPO_GIT_PROTOCOL.md`（根因/协议/红线）+ `run/ops/git_line_commit.sh`（worktree 封装，白名单/锁检测/--dry-run）。它**没有在 .17 上跑过**，你要么验证它可用并采用，要么指出问题并给替代——不许照抄不验。

**三、验收判据（你自己跑出来给我看）**
- posttrain 下一次唤醒能 **pull → 改 MEMORY → commit → push 一次过，0 冲突、不等锁**（把它那轮的 git 日志摘要贴出来）；
- 连续 3 轮多线并发提交无 `index.lock` 事故；
- 本线 commit 的 `--stat` 里**不含别线路径**；
- 共享树每轮结束时 `status --porcelain` 为空（或只剩本线 `.gitignore` 覆盖物）。

**四、边界**
- 只动本线文件 + 共享树**只读检查**；需要改 posttrain 文件时先在 MEMORY 记一行并说明原因（不许悄悄改它的 MEMORY/TASK）。
- 不杀别线进程；不碰 `attribution_3615_run*`。
- 本轮**不得以「已上报」收尾**：要么整改完成并给出验收证据，要么写清卡在哪一步、需要谁配合。


### 🔴 用户令 · 2026-11-19 20:0x（**定版：.12→.17 无网，SFT 产物在 .17 就地重生成**）· 细化并取代本文件「2026-11-19 11:12 GPU 分配令」第 2 条

> **用户原话（2026-11-19）**：「.12 到 .17 无网，在 .17 重生成 SFT 产物。」
> 这是对 wake#1681 / wake#1682 里「② GRPO 仍 BLOCKED，等运维 staging 或 Option B 拍板」的**正式答复**。

**一、先钉死前提（不要再当待确认项复述）**
1. `.12 ↔ .17` **无网络**：`rsync` / `scp` / 自取 checkpoint 一律不可行。**Option A（运维拷贝/迁移）作废**，不得再出现在心跳、报告或"下一步"里。
2. `.17` 上 `/nas_train` 不可用（挂成 `/H100_train` 且无 app 数据），`/nas_data/.../out/` 只有空 `wave_grpo_stage2w/`。⇒ **不存在"等产物到位"这条路**。
3. `.12` / `.29` SSH 超时是既定事实。**不必每轮再探测、不要再因它判 BLOCKED**（省 token，也免误判）。

**二、本轮唯一目标：在 .17 从零把 Stage-1W SFT 产物做出来，再用 GPU6-7 把 SFT → GRPO 跑通**
按 11-19 11:12 令第 2 条 a)–d) 执行，**baseline = 完整 Qwen3.5-2B MLLM + LoRA（不剥视觉塔）**：
- **a) 数据**：波形图 + 问答对（`image, question → answer`）。来源三选一或混用：10 道带 PNG 的旧题 / 按 case 公开参数重建波形图 / EDA-Eval-DesignFlow 波形 case 提取。**必须落盘并报路径 + 条数 + 1 条样例**（禁止只报"已准备"）。
- **b) SFT**：GPU6-7，LoRA，~3000 步，产出 `step{N}/adapter_*`，并同时产出**可判定指标**（VQA 通过率 或 format/submit 口径，二选一，**写明分母**）。
- **c) GRPO**：SFT 验收通过后 500 步，可验证奖励（check.py 或等效判分）。奖励设计纳入 research 日报 2026-11-19 建议：拆「区间内 vs 越界」β>α、判分档位边界 ±2% 重判一致性。
- **d) 评测**：pre-SFT / post-SFT / post-GRPO 三段对比，题集写明（WaveQA-RL 或 EDA-Eval-DesignFlow-WaveView 子集），**每个数字要能追到落盘文件**。

**三、硬性要求**
1. **本轮不得以 BLOCKED 收尾**。缺什么自己造（数据自己合成、backbone 自己确认、依赖自己解决）。某一步真做不成，必须写清「试了什么 / 报什么错 / 替代方案 / 下一步可执行动作」，**不许写"等运维"**。
2. **架构兼容性自行解决**：`qwen3_5` 若当前 transformers 不支持直接 LoRA，自选路径（升级 transformers / `trust_remote_code` / 调 peft `target_modules` / 必要时先回退纯文本骨干跑通闭环再补视觉），并在报告里写清取舍理由。
3. **本地权重优先**：先在 `.17` 找现成可用的 Qwen3.5 / Qwen3-VL 权重，不要再尝试跨机取。
4. **兜底工具（本轮已交付并自测）**：`run/vision/wave_rl/probe_backbone.py`。若最终需要纯文本骨干：
   `python probe_backbone.py --scan --roots <...>`（只读探测，输出 DIRECT / STRIP_LLM / STRIP_LM / SKIP 判定）
   `python probe_backbone.py --autoprepare --out <dir> --roots <...>`（就地抽取，支持分片 safetensors、`model.language_model.` 前缀剥离、视觉塔丢弃）
   已过离线功能自检（4 场景：纯文本 DIRECT / 分片+前缀剥离 / autoprepare / SKIP 分支）。**它只是兜底，不改变"主目标是完整 MLLM"这一条**。
5. **旧守卫必须改造**：`run_grpo_wave_gpu67.sh` 里「缺 SFT 产物 → `[EXIT 0] BLOCKED`」不再是正常出口——改为在缺失时**自动进入自生成链路**（或直接调用自生成脚本）；BLOCKED 只允许用于「GPU6-7 被他线真占用」这类外部事实。
6. **边界不变**：只动 GPU6-7；不杀别线进程（posttrain serve / VQA serve / pretrain）；不碰 `attribution_3615_run*`；`git add` 只加本线文件（不用 `-A`）。

**四、交付物清单（缺一项即本轮不算完成）**

| # | 交付物 | 落点 / 要求 |
|:--|:--|:--|
| 1 | 波形 QA 训练集 | `.jsonl` 落盘 + 条数 + 样例 1 条 + 生成脚本 |
| 2 | SFT 产物 | `step{N}/adapter_config.json` + `adapter_model.safetensors` |
| 3 | SFT 验收结果 | `eval_results.json`（含分母、阈值、pass 字段） |
| 4 | GRPO 产物 | `step{N}` ckpt + 训练日志（reward 曲线） |
| 5 | 三段对比表 | pre/post-SFT/post-GRPO 通过率 + 配对检验（n 与 p 值） |
| 6 | 报告 | 原地更新本线固定报告（不新开文件） |
| 7 | 心跳 | `MEMORY_VISION.md` 一行 + 当日 daily 一行 |
| 8 | 提交 | `git add <本线文件>` + `commit + push`，`git status -sb` 干净 |

**五、验收判据（预注册，先写后跑，跑完按此判）**
- SFT 至少产出 1 个 `step*` 且验收指标落盘（**分母必须写明**）；
- **post-SFT > pre-SFT** 才判 SFT 有效；
- **post-GRPO vs post-SFT** 做同题配对检验（McNemar），报到 **n10/n01/n 与 p 值**；不显著就照写「不显著」，不许粉饰；
- 所有数字给可复算命令（脚本 + 参数）。

> ⚠️ 若 GPU6-7 实际被他线占用（如 VQA serve 仍在 GPU6），先报占用实况（`nvidia-smi` 输出摘要 + 进程），再决定是等释放还是先把数据/训练链路准备好——**但"先准备链路"不等于可以停摆**。

### 📦 用户令 · 2026-11-19 11:12（**GPU 分配 + 训练迁回 GPU**）· 第 2 条已被上方 20:0x 令细化，原文保留对照



> **.17 GPU 分配**：GPU 4-5 → posttrain，**GPU 6-7 → vision**。
>
> **背景**：vision 以前在 .12 用 CPU 跑 RL，是因为 .12 的 GPU 腾给了 pretrain。现在 vision 已迁到 .17，后四卡中的 GPU 6-7 可以用起来。
>
> **你要做的**：
> 1. **VQA 服务迁移**：当前 VQA 服务（Qwen3.5-2B `:30001` + rft2 适配器 `:30003`）跑在 GPU 5。把 `--gpu` 参数从 5 改到 **6**，重启服务。这会释放 GPU 5 给 posttrain。✅ 已完成（wake#1680）
> 2. **训练迁回 GPU — 走 Option B（在 .17 上重新生成）**：之前因 GPU 不足改用 CPU 的波形 RL 训练（Stage-1W SFT + Stage-2W GRPO），现在用 **GPU 6-7** 迁回 GPU 训练。**.17 与 .12/.29 网络不通**，旧的 SFT checkpoint / 训练数据都在 .12 上拿不到。**因此走 Option B：在 .17 上从零重新生成全部前置产物**。
>
>    **核心目标**：以 **Qwen3.5-2B（MLLM）为 baseline**，通过 SFT + GRPO 强化它**读懂波形图**的能力。Qwen3.5-2B 本身就是个蛮强的多模态模型（VQA 服务已在用它看图答题），不需要剥离视觉塔——直接对完整 MLLM 做 LoRA 微调。
>
>    - **a) 准备训练数据**：合成或收集**波形图 + 问答对**（image + question → answer）。数据源：已有 10 道带 PNG 的波形题、用公开参数重建合成波形图、或从 EDA-Eval-DesignFlow 的波形 case 中提取。参照 .12 上的合成方法（`vision/wave_rl/` 下的脚本逻辑），在 .17 上重新生成。
>    - **b) GPU SFT 训练**：用 GPU 6-7 跑 Stage-1W SFT——直接对 **Qwen3.5-2B 完整 MLLM** 做 LoRA 微调（不是文本骨干，是完整多模态模型），训练它看波形图回答问题。3000 步左右，GPU 上应远快于 CPU。
>    - **c) GPU GRPO 训练**：SFT 验收通过后，跑 Stage-2W GRPO——用可验证奖励（check.py 或等效判分）强化 MLLM 的波形图理解。500 步，GPU 6-7，bf16 并行 rollout。
>    - **d) 评测**：对比 pre-SFT / post-SFT / post-GRPO 的波形图理解通过率。可用 WaveQA-RL 评测集或 EDA-Eval-DesignFlow-WaveView 子集。
>    - **注意**：之前 .12 上的做法是剥离视觉塔用纯文本骨干（因为 transformers 不支持 qwen3_vl 架构）。现在 Qwen3.5-2B 是不同的模型，需确认其架构在当前 transformers 版本下可被 LoRA 微调（含视觉塔）。如遇兼容性问题，自行解决（升级 transformers / 用 peft / 调整加载方式）。
> 3. **WaveView 评测不受影响**：36.15 上的 V0/V1/V2 全量对照继续跑，这是推理任务不占本地 GPU。
> 4. **已完成项**：① VQA→GPU 6 ✅（wake#1680）。② GRPO 训练当前 BLOCKED——走 Option B 解除阻塞。

### 🔴 用户令 · 2026-11-17 16:3x（**自主构建 EDA-Eval-DesignFlow-WaveView 子集**）· ✅ 重做已交付 (wake#1663) · 待用户验收

> **wake#1663 重做交付（2026-11-19 00:25:35 全队列 runner done）**：用户两轮修正后已重做，原「还差什么」三项全部落地——
> 1. ✅ **jsonl 分类改判**：废除旧「214 道 text_only 标 `image_required=False` + 排除在 V0/V1/V2 外」口径。新口径 `eval_included = 波形相关 ∧ 有 check.py = 192` 全部纳入评测队列（`cohort=full_eval`）；182 道 text_only 不再排除，由 agent 尝试、真实 check.py 判分（不预设「需不需要看图」，让实验说话）。新增 `audit_category`（image_reading/code_gen）字段。33 道（32 no_check + 1 非波形 IRReportPdf）诚实排除并写明理由。子集 `vision/EDA-Eval-DesignFlow-WaveView.jsonl` 225 行，36.15 与本地 sha256 一致。
> 2. ✅ **V0/V1/V2 全队列对照跑完**：36.15 `run_codegen_full.py` 跑完全队列 **546 行/546 = 182 case × 3 臂三臂齐全**。V0 20/182(11.0%) · V1 28/182(15.4%) · V2 32/182(17.6%)。**McNemar：V0 vs V1 b=11 c=3 p=0.057(边缘) · V0 vs V2 b=15 c=3 p=0.008(显著 p<0.05) · V1 vs V2 b=8 c=4 p=0.388**。17 例 VQA 翻转（15 例 V0→V2 PASS / 3 例反向）。**结论：MLLM-as-VQA 价值 = V2 适配器 vs 无 VQA 整题通过率 +6.6pp(11.0%→17.6%)，p=0.008 显著**。本地快照 `vision/waveview_mining/codegen_full_results_snapshot.json`(546 行)。
> 3. ✅ **报告已更新**：`reports/report_vision_waveview_selftest_agent_zh.html` §0.6 已改写为最终全队列结果（废除 interim 措辞），数字可复算。
>
> **状态**：重做已交付并 commit（`vision wake#1663`），**WAITING: 0**。原 wake#1525 否决记录与三项「还差什么」原文保留于下，供用户验收对照；用户验收通过后归档至 `ARCHIVE_OPERATOR_VISION.md`。

> 📦 **wake#1525 否决记录 / 原「还差什么」三项 / 用户原话** 已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「归档 · 2026-11-19 §B」。**现行结论**：wake#1663 重做已交付（546 行全队列 · V0 20/182(11.0%) / V1 28/182(15.4%) / V2 32/182(17.6%) · McNemar V0vsV2 p=0.008 显著 · MLLM-as-VQA 价值 +6.6pp），待用户验收。需要对照旧口径时再读归档。

**一、核心任务：自主构建 WaveView 评测子集**

你已有 `.17 → 36.15` 的 SSH 隧道（`ssh -p 3333 app.e0031982@localhost`）。36.15 上的 EDA-Flow-Bench 全量数据在：
`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`

**你要做的事**：

1. **全量扫描 `EDA-Eval-DesignFlow.jsonl`（1647 行，含 A/B/C/D 四 shard 合并）**，筛选所有 WaveView 相关 case。筛选口径由你自主定义，但必须覆盖：
   - task_id / prompt / metadata 中含 waveform / wave / fsdb / vcd / waveview / eye diagram / oscil / edge timing / signal extract 等关键词的 case
   - assets 目录下有可见图像文件（PNG/JPG）的 case
   - 有 `check.py` 的 case
   - **不要只挑已有 PNG 的 10 道**——对没有 PNG 但原意图需看图的 case，你有权**自行生成波形图**（用 case 定义中的公开参数重建），纳入子集

   > ⚠️ **2026-11-17 用户修正（第二条）：不要把 MLLM 价值矮化为 OCR 或 pattern recognition**
   >
   > 上一条修正举了 pattern recognition 的例子，但**那只是个例子，不是新的狭义定义**。MLLM 在 WaveView 子集上的价值是**任何一个维度**的：
   >
   > - 读数（从坐标轴读值）
   > - pattern 识别（眼图形态、毛刺、违例区间）
   > - agent 调 VQA 问细节问题，得到回答后通过率上升
   > - 以前解决不了的问题，加上 VQA 后能解决了
   > - **任何**有 VQA 工具 vs 无 VQA 工具导致通过率提升的机制
   >
   > **唯一的度量标准**：WaveView 子集上，**有 VQA（V1/V2）vs 无 VQA（V0）的通过率差异 = MLLM 的价值**。不需要分类"这种帮助算数、那种不算"。
   >
   > **因此**：WaveView 子集应包含**所有与波形相关的 case**。只要这道题跟波形/信号/波形查看工具有关，就纳入子集。V0 跑一遍、V1/V2 跑一遍，**通过率有没有变就是答案**。不需要预先判断"这道题需不需要看图"——让实验说话，让数据说话。

2. **在 36.15 同目录下生成并维护 `EDA-Eval-DesignFlow-WaveView.jsonl`**：
   - 路径：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-WaveView.jsonl`
   - 格式：与原 jsonl 相同的 JSON Lines，每行一个 case
   - 每条记录至少含：`task_id`（或 `id`/`case_id`，沿用原字段名）、`shard`、`domain`、`image_required`（bool）、`image_path`（如有）、`has_check`（bool）、`k_conditions`（check.py 条件数）、`baseline_verdict`、`failure_mode_tier`（α/β/γ）、`source`（"original_png" / "generated_png" / "text_only" / "no_check"）
   - **你负责维护这个文件**：后续新 case 恢复、新图生成、基线更新都要同步到这里

3. **跑基线（V0 = 无 VQA）和加 VQA 后（V1/V2）的对照**：
   - V0：纯文本 agent，不看图（正确基线，预期大量 fail）
   - V1：加 Qwen3.5-2B 基模 VQA
   - V2：加 SFT/RL 适配器 VQA
   - 同口径、同题、同 check.py，报告整题通过率 + 每量准确率 + McNemar

4. **交付**：
   - `EDA-Eval-DesignFlow-WaveView.jsonl`（在 36.15 上，同时 ssh 复制一份到本地 `vision/` 下）
   - 更新 `reports/report_vision_waveview_selftest_agent_zh.html`（原地覆盖，用扩大的题集重跑）
   - MEMORY 心跳一行

**二、自主性授权**

- **你有权自行 SSH 到 36.15**，读取、检索、复制 EDA-Flow-Bench 的任何数据（只读）
- **你有权自行生成波形图**（对没有 PNG 但需看图的 case，用公开参数重建）
- **你有权自行定义筛选口径**（但口径要写清，数字要可复算）
- **不必等 designflow**——这是你自己的工作项，不是别线的供给任务
- **你可以写入 36.15 上的 `EDA-Eval-DesignFlow-WaveView.jsonl`**——这是你负责维护的文件

**三、判据**
- WaveView 子集应包含**所有与波形/信号/波形查看工具相关的 case**——不预设"这道题需不需要看图"，让 V0 vs V1/V2 的实验结果说话
- 基线 V0 + V1/V2 对照跑完，**通过率差异 = MLLM 价值**
- 报告更新，数字可复算
- 如果某 case 确实与波形完全无关（纯文本 Q&A / 软件安装指南等），诚实排除并写明理由

---
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
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不绕过验证/实名/风控。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。
- **自主性**：你有权自主 SSH 到用户放行的机器、自主检索全量数据、自主决定技术路线。不要因为「这是别线的数据」就干等——只读不改是你的权利。

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
| 注意力 | 双向（bidirectional）—— causal AR 已证明坍缩或 lp 极低，不推荐；若有新证据可重新评估 |
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

### 🧭 运维规程 · 2026-10-06（agent 自滚 MEMORY + 任务书）· 常驻 → **现行条款已并入上文「工作约定」第 2 条（各 ≤32KB、超限原文搬 ARCHIVE 留 1 行指针）**；原文见 `run/ARCHIVE_OPERATOR_VISION.md`。
### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览 + §运维指令 2026-10-05（深夜2 两份 HTML 报告 / 深夜 R12→3epoch+方向建议 / 晚 全量 AIMv2 训练+论文 §6 改写+proxy 口径）**均已归档** → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）

- **外部证据**：涉及"别人怎么做"（架构/loss/评测/数据），优先读官方仓库或论文原文（能 clone 就 clone）；二手描述可以当线索，但结论要自己有依据（本线曾因此出错过一次）。
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
