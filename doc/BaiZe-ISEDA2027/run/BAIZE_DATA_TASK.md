# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_DATA.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_DATA.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

### 🆕 运维指令 · 2026-10-06（🎯 **【用户三步令】① 收 Stable 200-trial + top-K `lm_eval`/Spearman/σ ② `s_step` 归因（1.5 s→~30–100 ms，`D` 0.016 B→0.5–1 B）③ `.29` GPU0-1 释放后 **8 卡**搜第二轮**）· **最高优先 · 用户直令**

> **用户 2026-10-06 三步令（按此顺序）**：
> 1. **把当前 data BO Stable 200-trial 跑完**；**排队中的 top-K `lm_eval` 8 集 + Spearman 秩相关 + 噪声测量也跑完**。
> 2. **做 `s_step` 归因（最高杠杆）**，争取把 **1.5 s 压到 ~30–100 ms** ⇒ **`D` 从 0.016 B 抬到 0.5–1 B**。
> 3. **此时若 `.29` GPU0-1 已释放，就用 8 卡搜第二轮。**

> ⚙️ **运维技术修正（先读，别走错方向）—— `s_step=1.5 s` ❗不是多卡同步**：
> - `run/baize_mix_optuna.py:208` = `torchrun --nnodes=1 --nproc_per_node=1`；`:216` `--tensor-parallel 1`；`:231` `CUDA_VISIBLE_DEVICES=<单卡>` ⇒ **【每个 trial 本来就跑在单卡上】**（`--gpus 2,3,4,5,6,7` = 6 个**独立并行** trial，**无任何跨卡通信**）。
> - `s_step=1.50 s` 本身也是**单卡**实测（`daily-memories-data/2026-10-06.md` 必验#4：16 次测量 1,425–1,582 ms）。
> - ⇒ **真凶候选（都在单卡内）**：① ⭐ **`--micro-batch-size 1`（`:219`）+ `GBS=16`（`:218`）⇒ 每步 16 个 microbatch**，TP1/DP1 不可切分、只能梯度累积 ⇒ ≈**94 ms/microbatch** 的 Python/kernel-launch/DataLoader 开销 × 16 ≈ **1.5 s**；② 数据管线（NFS 小批读）；③ CE logits 4.24e9 元素（≈10–17 ms，非主因）；④ 无 CUDA graph。
> - **算力账**：`6·N·tokens = 6×18.5e6×32768 ≈ 3.6 TFLOP ≈ <10 ms` ⇒ 实测 1.5 s = 算力的 **~100×** ⇒ **纯 overhead-bound，不是算力、更不是通信**。
> - ⇒ **修法（单卡内即可，🚫 不用改多卡策略）**：**MBS 1→8/16**（microbatch 16→2/1）· 开 CUDA graph · DataLoader `num_workers`/prefetch 上调 · fused/chunked CE。判据 = 维修后 **`s_step` 中位数 ≤100 ms**（力争 ≤30 ms）。
> - ℹ️ **`MBS=1` 的由来 + `MBS↑` 的显存账（运维补 · 用户 2026-10-06 追问）**：
>   - **由来 = 沿用 2.2B 基线 recipe 未重标定**：`run/baize_p5b_train.sh`（GBS1024·MBS1·seq4094）、`baize_p2/p3_sweep.sh`、`baize_p7_remeasure.sh` 全为 MBS1；arch-search 计划原文写「`micro_batch_size=1`（**共享 GPU 下 mb2 易 OOM**）」—— 那是**为 2.2B 设的**；`baize_mix_optuna.py:219` 只是**把该值抄给了 18.5M 代理**。
>   - **显存大头不是模型，是 logits/CE**（`vocab=129,408`）：`logits = MBS×seq×vocab` ⇒ MBS=1 → 2.65e8 元素 **0.53 GB(bf16)**；**MBS=16 → 4.24e9 元素 = 8.5 GB(bf16) / 17 GB(fp32)**（含反传可至 ~17–34 GB）⇒ **80 GB H100 装得下** ⇒ **MBS 16 预期可行，直接消掉 16× 梯度累积**。
>   - ⚠️ 但**以 step ②a 实测为准**（防 CE 反传 OOM）；若 OOM ⇒ 上 **fused/chunked CE**（本就该做）。✅ **改 MBS 不改 GBS 语义（GBS 恒 16）⇒ 结果仍可比。**

> **执行（① 先收口；② 可并行、时间盒 ≤2h；③ 条件触发）**
>
> **① 收 Stable + 分析（沿用现有 GPU2-7，🚫 不改现跑脚本）**
> - 让 `mix_search_eval.db`（PID 1011682）**自然跑完 200/200（不许 kill）**；随后按既有「下一步 ②③④」执行：
>   - 重跑 **top-5（#155/149/96/125/55）+ 先验 88:8:4（#79）共 6 config 带 ckpt → `lm_eval` 8 集 → 取均分作真 objective**；
>   - **Spearman 秩相关**（代理 val-loss ↔ 均分）；
>   - **噪声测量**（top-5 各 ≥3 次，报 **σ**）。
> - 产出 `report_data_mix_eval.html`（200-trial 的 top-K/秩相关/σ）+ 更新 `DATA_MIX_RECIPE.md §6`。🚫 **不要把 200 扩成 512**（512 目标**并入第二轮**，见 ③）。
>
> **② `s_step` 归因（⭐ 最高杠杆；时间盒 ≤2h；**只占 1–2 卡**，别抢 ① 的卡）**
> - **⭐ 目标函数（用户 2026-10-06 追问：`MBS`/`GBS` 都往大试，追求「最快训完 0.5–1 B」）**：**不是最小化 `s_step`，而是最小化「训完 `D`=0.5–1 B」的总墙钟**。模型：
>   `墙钟 = (D/(GBS·seq)) × s_step`，`s_step = F(每步固定) + (GBS/MBS)·P(每 microbatch) + c·GBS(算力)`
>   ⇒ `墙钟 ∝ D/seq × [ F/GBS + P/MBS + c ]` ⇒ **两杠杆都拉满：GBS↑（压 F/GBS）× MBS↑（压 P/MBS）**，地板 = 纯算力 `c`。
> - **逐项实测（每次只改一个变量，贴原始输出）**：
>   a. ⭐ **MBS 扫描（拉满，受显存限）**：MBS ∈ **{1,4,8,16,32,64,128}**（GBS 固定 16 先测单点）→ 报 **s_step 中位数 + tok/s + 峰值显存 + OOM?**；**若 s_step 不随 microbatch 数变 ⇒ 转查数据管线**。
>      - **显存账（瓶颈 = `vocab=129,408` 的 logits）**：`logits = MBS×seq×vocab`（bf16）→ 16→**8.5 GB**、32→**17 GB**、64→**34 GB**、128→**68 GB**（+反传再翻倍）⇒ **32 稳 / 64 视情况 / 128 须先落 fused CE**。
>   b. ⭐ **先落 `fused/chunked CE`**（`--cross-entropy-loss-fusion`；TP1/DP1 无 TP 可切 ⇒ 必须）—— **落了它 MBS 才能上 128/256**（激活降到 `O(MBS·seq·d·L)` ≈ 1 GB 级）。**先做 b，再做 a 的高档位。**
>   c. ⭐ **GBS 扫描（拉满，但受「优化步数」限）**：GBS ∈ **{16,64,256,1024}**（MBS 取 a 的最大可用值）→ 报 **tok/s + 训完 D=0.5 B / 1 B 的总墙钟 + 步数**。
>      - ⚠️ **fidelity 约束（不许无视）**：`D` 固定时 **GBS↑ ⇒ 优化器更新次数↓**（`步数 = D/(GBS·seq)`；GBS1024·seq2048·D=0.5B ⇒ **仅 238 步**）⇒ **GBS 不是越大越好**；必须 **按比例同步调 LR/warmup**，并在报告里**显式标注所选 GBS 的「步数」与「是否仍是可辩护的配比排序口径」**（排序相对性最终由 ③ 的 top-K `lm_eval` 背书）。
>   d. **DataLoader**：`num_workers` / prefetch / 本地缓存 vs NFS → 报 s_step 差；
>   e. **CUDA graph**（若 launcher 暴露）/ 关 `--recompute`；
>   f. **纯前向 vs 纯数据处理分离计时**（定位到底卡在哪）。
> - **判据（必须给）**：**MBS×GBS 网格表**（`s_step` / `tok/s` / 峰值显存 / OOM / **训完 0.5B·1B 的墙钟**）+ **最优组合**；目标把「训完 0.5 B」从当前（1.50 s/步 ⇒ ≈**6.4 h/trial**）压到 **≤1–2 h**；据此定 ③ 的 `D` / `trial 数` / `T`。
> - 产出 `report_data_mix_sstep.html` + `DATA_MIX_RECIPE.md` 增节（网格原始输出 + 判据 + **GBS 的 fidelity 说明**）。
>
> **③ 第二轮搜索（**条件触发**：`.29` GPU0-1 已释放）**
> - **触发条件**：pretrain 侧 **D（P-9.11 补测）已完成并明确释放 GPU0-1**（运维会在心跳/任务书确认）。🚫 **在此之前绝不碰 GPU0-1**（pretrain A/B/D 在用）。
> - **做法**：用 **8 卡（GPU0-7）** 跑 **Stable 第二轮 BO**；`D`（token/trial）按 ② 修好的 `s_step` **反算**（目标 0.5–1 B；若 `T` 不允许则如实降档并标注），trial 数按 `T` 反算（**目标 ≥200 且尽量多**；512 若可达则取 512）。
> - 新 study 用**独立 DB**（如 `mix_search_eval_r2.db`），保留 200-trial 结果作对照；**同样跑 top-K `lm_eval` + σ**。
> - 产出 `report_data_mix_eval_r2.html`。
>
> **纪律（不变）**：🚫 **不 kill 正在跑的 BO**；🚫 **不在 pretrain 释放前碰 GPU0-1**；🚫 不改白名单 / 不重启下载；**心跳 ≤60 min** 且每步 commit + push；做不完**如实写卡点 + 需要什么 + 阻塞**；`TASK/MEMORY` 体积均 ≤32KB。

### 🆕 运维指令 · 2026-10-06（🚨 **P0 · 立即重启 base 全量下载**）· **最高优先 · 用户直令**

> **用户指令（2026-10-06）**：「**让 data 立即重启下载 base**」。
>
> **为什么急**：pretrain 侧连续多轮状态核查报 **base 下载进程 DEAD**（`PID 550476` 已死、`ps` 无活跃 `hf download`/`huggingface` 进程）：`ultrafineweb_l1_en_hq` 停在 **313G/478G（~65%，4205 parquet）**、`ultrafineweb_zh` 停在 **202G/324G（~62%，171 parquet）**；而 **base 是 P-8（Stage (i) 本体）stable 段的主力数据**，P-8 需 **~100B token**，当前已分词仅 **22.05B tok** ⇒ **这是 P-8 的硬前置，必须立刻恢复。**
>
> **按顺序做**：
> 1. **先取证**：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer' | grep -v grep`（**预期为空 = 真停**）＋ 两项的 `.incomplete` 计数 ＋ 落盘目录 mtime。
> 2. **立即重启**（✅ 只用**既有白名单**、**config 级 `--include`**）：
>    - 目标 = **`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`**（两项）；
>    - 🚫 **绝不再拉 `ultrafineweb_en_v1_4`**（6.7TB、非 P-8 必需、曾阻塞后续 —— **白名单铁律不变**）；GPIC 按原计划续下（Stage (iii) 在用）；
>    - ⚠️ **外网命令必须显式带 proxy**（`https_proxy=http://172.19.92.25:13128`；**内网 hub 不带**）—— 历史上"下载不动"多半就是这个；
>    - `nohup`/`setsid` 脱离进程组，日志落 `/tmp/hf_dl_base.log`，**把完整命令原文 + 首次输出贴进心跳**。
> 3. **保活核验**：重启后 **1–2 分钟内**确认**速率 / `.incomplete` 在增长**（防 CDN 假活）；若又停，查清原因（proxy / DNS / CDN 403 / 磁盘满）并如实记录。
> 4. **报 ETA**：按实测速率给出 `l1_en_hq`（余 ~165G）+ `zh`（余 ~122G）的下完时间，以及「**下满 → 分词到 100B token**」的预计时长。
> 5. ⚠️ **不要因下载而停掉配比 BO**（BO 在 GPU2-7、下载是 I/O，可并行）；重 I/O 会与 **vision R12b（ETA ~21:00）** 争 NFS —— **用户此前已裁定「不限速、趁假期尽快下完」**，照此执行，但要在心跳里**记录当时 vision 在跑**。
>
> **纪律不变**：🚫 不占 GPU0-1（pretrain 提速用）；🚫 不改白名单；每步 commit + push；做不完**如实写卡点 + 需要什么**。


### 🆕 运维指令 · 2026-10-06（🚨 **目标函数错了：配比搜索必须用「评测均分」，不是 val loss**）· **P0 · 立即改**

> **用户 2026-10-06 更正**：你在心跳里报的 **`best=4.6471(#64)` 是 proxy 的 `val loss`** —— **loss 排序 ≠ 能力排序** ⇒ 用 loss 当 BO 目标，会选出「loss 低但能力不高」的配比。**这是方法学错误，不是措辞问题。**
>
> **✅ 正确口径（必须照此改）**
> - **Stable 段配比搜索** → **目标函数 = 8 集常识推理评测均分**：`arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande`（**zero-shot**，**与 P-6 同口径的 lm_eval/harness**）。
> - **Decay 段配比搜索** → **目标函数 = 6 集复杂推理评测均分**：`gsm8k, math, bbh, mmlu, humaneval, mbpp`（**同一套 lm_eval 口径**）。
> - **`val loss` 降级为"诊断列"**：可继续记录，但**不作排序/选优依据**。
>
> **必须做的 6 件事**
> 1. **改评测管线**：每个 trial 训完的 ckpt → HF 转换 → 用 **`run/baize_mix_eval.sh`（已就绪）** 跑对应任务集 → **取均分**作为 BO 的 objective。（可对齐 pretrain 的 `p5b_lmeval_all.sh` / `p5b_collect_and_report.py` 口径；⚠️ **装包/起服遵守环境隔离**，不要污染共享 `py310`。）
> 2. **回算已有 trial**：至少对 **top-K + 先验点(88:8:4) + 若干随机点** 在新目标下评测 → **检验「loss 排名 vs 均分排名」的相关性（秩相关）**——若不一致，**这本身就是结论**（说明此前挑选标准是错的）。**如实报告，不许美化**。
> 3. **预注册**：先把**判定阈值**写进 `DATA_MIX_RECIPE.md`（例：「以 8 集均分为准；Δ 必须超过**评测噪声 σ** 才算真差异」）⇒ **先定后测**。
> 4. **噪声必须有数**：**同一个 ckpt 重复评测 ≥3 次**，报 **σ**；评测协议（harness 版本 / shot / 数据 bin）**全文唯一**。
> 5. **在跑的 trial**：**立即切换 objective**（后续采样不再由 loss 引导）；已完成的 **79 个保留**作对照。
> 6. **产出**：`report_data_mix_eval.html`（自包含：新目标 top-K 表 + **loss-vs-均分散点/秩相关** + 先验点位置 + best-so-far 曲线 + **噪声 σ** + 命令与原始输出）。
>
> **⏱️ 速度红线（用户 2026-10-06 追加）**：**若本安排导致整体太慢 ⇒ 立刻汇报**（🚫 不要自己硬扛、也🚫 不许静默降级）。用户给的**可行方向**（具体方案可再议）：
>   1. **减少题目数量**：每个评测集**降采样** ⇒ 必须标注「**用了几题 / 原题数**」，并**验证「降采样排名 vs 全量排名」一致性**（至少对 top-K 全量复算）。
>   2. **用「评测集语料的 val loss」代表评测集评分**：把这 **8/6 个评测集本身的文本**做成 held-out bin，算 **val loss** 作代理 ⇒ 必须 ①**语料就是评测集本身**（🚫 不是训练分布）②**在 top-K 上验证「代理 val loss ↔ 真实均分」的相关性**（给秩相关 + 散点）③**不得**与"训练分布 val loss"混为一谈。
>   3. 其他：降 trial 数 / 提高单 trial token / **仅 top-K 全评 + 其余用代理校正**。
>   **共同铁律**：任何降级都要 ①**先报**（含成本估算：**单 trial 评测耗时 × 剩余 trial 数**）②**给相关性证据**证明代理没失真 ③**报告里显著标注"代理指标"**。🚫 **绝不许"偷偷用 loss 当 objective"**（那等于没改）。
>
> **纪律不变**：🚫 **不占 GPU0-1**（pretrain 提速用）/ 只动 **GPU2-7**；🚫 不重启下载、不改白名单；每步 commit + push；做不完就**如实写卡点 + 需要什么**。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，本线心跳文件 **`run/MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 确实在改任务书/配方、也 push 得出去），**外部运维只能靠 git 看到「06:55 后零提交」⇒ 被误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；而 loop 的兜底 push 间隔是 **5h**（本日已缩短，**见下**），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底同步一次」**不再作为你的交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_DATA.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_DATA.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_DATA.md` 顶部进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-data/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**，不许攒着最后补）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md doc/BaiZe-ISEDA2027/run/DATA_LEDGER.md \
              doc/BaiZe-ISEDA2027/run/CONTAMINATION_CHECK.md doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md \
              doc/BaiZe-ISEDA2027/run/DATA_MIX_RECIPE.md doc/BaiZe-ISEDA2027/run/DISK_CLEANUP_INVENTORY.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-data doc/BaiZe-ISEDA2027/run/data_pipeline
   git commit -m "data <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已因此出过事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**（派人上机 kill / 重排卡），**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

### 🔴🔴 运维指令 · 2026-10-06（**第 5 轮 · 代理规模定案 `d=128/L=14 ≈ 18.5M` + 开工前 5 项必验**）· **P0 · 从本块开始执行**（前两块的方法学定义与改道方案**全部继续有效**；**仅「代理规模」一项被本块覆盖**）

> 📦 §第5轮块头·用户两问+裁定（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：代数求解D=1B×512×24h→d=128/L=14/N≈18.5M(定案),h=512降为备用。需要时再读。

#### A. 规模定案（🚫 **不许自行改**；若确因结构/性能改，必须在 `MEMORY_DATA.md` 写明「按 §③.6 哪一档、因何故」）

> 📦 §A 规模定案表（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：d=128/L=14/N≈18.5M(实测18.36M)、tie embed、pattern 24M:4*:28-。需要时再读。

> 📦 §B 开工前5项必验（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5项全部PASS（可分辨性Δloss/2σ=7.9×、结构合法18.36M、2B=untie系数8.32、s_step=1.50s、LR=3e-3），详见MEMORY_DATA.md。需要时再读。

#### C. 评测硬规则（**`T` 的乘数，必须按此写预算**；完整口径见 §③.9）

> 📦 §C 评测硬规则（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：eval in-process/固定held-out bin/单次≤20M tok/总评测点≤8/搜索期save_interval=0/top-K跑lm_eval。需要时再读。

#### D. 第 0 步的分工（**重要：防重复 kill**）

> 📦 §D 第0步分工（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：kill S0a=no-op(已无进程)、GPU0-7全空确认、GPU2-7归data恢复生效。需要时再读。

### 🔴🔴 运维指令 · 2026-10-06（**用户复核②：给「实验」下可检验定义 —— 单臂/单点不算实验，先验不得当结论交付**）· **P0 · 先读本块，再读下块（改道方案本身不变）**

> 📦 §用户复核②块头·原话+裁定（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：单臂/单点不算实验(方法学错),须按§B-E订正。需要时再读。

> 📦 §A 事故复盘（用户复核②块内，2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：S0a单臂98GPU·h已浪费、名实不符+结论越界已订正、改道方案已执行。需要时再读。

#### B. 「配比实验」的可检验定义（**5 条判据，缺一不算实验**）

1. **≥ 2 个不同配比被真正跑过** —— 本任务下要求 **≥ 200 个 trial**（下块②③）。**单臂 / 单点 / 单 seed = 无效实验**，成果栏只能写「未验证先验」。
2. **每个 trial 都要落盘成表**（**含 `pruned` / 失败 / 跳过的**），可由 `sqlite`/CSV 复现 —— **不是**只在正文里报「效果最好的那个」。
3. **评测协议全程唯一**：同一 held-out bin、同步数、同 GBS·seq、同 seed 规则 ⇒ 否则横向不可比（中途不许改，迫不得已改了必须重跑全部）。
4. **结果必须是「排序 + 不确定性」**：给 **best-so-far 收敛曲线** + **top-K 表（K≥3）** + **trial 空间分布**。
5. **先验点必须与搜索结果同台出现**（见 C）。

> 🚫 **违反任一条的产出，禁止出现「最优 / 胜出 / 结论 / 定稿」字样**；只能写「**未验证先验（占位，待 BO 检验）**」。

#### C. 直接回答用户的质疑（**「直觉 vs 实验」必须用数据回答，不靠嘴**）

- **硬要求**：把 **`88:8:4`（Stable）** 与 **`SFT=64%`（Decay）** 作为**强制候选点**喂进 study（`study.enqueue_trial()` 或固定候选清单），与 BO 搜出的最优点**并排对比**：
  `Δ = loss(BO 最优) − loss(先验点)`，**同 held-out bin、同步数、同 seed 规则**。
- 报告须用**一句话**回答：**「先验点排第几 / top-K 里有没有它 / 差多少」**。
- **两种结果都合格**：若 `Δ` 落在 seed 噪声内 → **如实写「先验已经很好，搜索的收益是置信度与鲁棒性」**；若明显更优 → **给出配比偏移方向与幅度**。⇒ **伪造结论不合格，如实报负结果合格。**

> 📦 §D 文档订正（用户复核②块内，2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：report_data_mix_s0a.html+DATA_MIX_RECIPE.md §3/§6运维已加订正框，§6待BO完成后用实测trial表替换。需要时再读。

#### E. 心跳纪律（**运维只有 git 通道，看不到训练机 —— 无心跳 = 视为卡死**）

- study 每推进 **≥ 20 个 trial 或 ~30–60 min** → **必须 commit 一次**：`trials_done / pruned / best-so-far loss / top-3 配比 / ETA`（**贴原始输出片段**，不许只写结论）。
- ⚠️ **超 60 min 无提交 ⇒ 运维按「卡死」处理**（会派人 kill / 重排卡），**不再等你**。
- 🚫 **「运行中 / 进度中 / 已完成标定」不是交付物**；**Day1 结束前必须给出 Stable 段搜索完成证据**：trial 数 + best-so-far 曲线 + top-K 表 + 先验点对比（Day2 同理）。
- 🔴 **第 0 步（kill）+ 释放卡的原始输出**必须在本块生效后的**第一次唤醒内**贴进 `MEMORY_DATA.md`。

> 📌 **一句话**：**先验只能当「候选之一」被实验检验，不能当「答案」交付；没有 trial 表 / 没有对照 / 没有排序，就不许说「最优」。**

---

### 🔴 运维指令 · 2026-10-06（**配比实验改道**：废弃「目标尺寸模型 + 手挑单臂」→ 改「**小代理模型 + Optuna 贝叶斯优化 + 每卡独立 trial**」；**1 天搜 Stable / 1 天搜 Decay**）· **最高优先 · 立即执行**

> 📦 §改道方案·裁定原文（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：S0a方法学错(单臂2.2B)+成本失控(312GPU·h/臂)→改道小代理+BO(§①②③已归档,§④⑤⑥见下)。需要时再读。

> 📦 §改道方案 ①②③（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md（①立即动作）+ run/ARCHIVE_DATA_SPEC_HISTORY.md（②硬约束+③标定）；**结论**：kill S0a 完成、d=128/L=14 由第5轮块定案、标定5项必验全部通过（见 MEMORY_DATA.md）。需要时再读。

#### ④ 搜索空间（Optuna `suggest_*`）

- **Day1 · Stable 段（WSD 的 stable 主体）**：`web`（base / UltraX；**UltraX 🚫 未下 → 本轴降级为「仅 base」**，沿用 §0.6-B 既有口径）· `code` · `math` **三点、`sum=1`**。
  初值域：`web ∈ [0.80, 0.95]`、`code ∈ [0.03, 0.12]`、`math = 1 − web − code`（**让 BO 自己找，别把先验钉死**）。
- **Day2 · Decay 段（带 SFT 的退火）**：**`SFT 总占比 ∈ [0.40, 0.80]`**（⚠️ Xmodel-2 最优落在 **60–69%（取 64%）**，**是文献锚点不是答案**——**让 BO 自己搜**）+ **SFT 内部 5 类**（`Mathematics` / `Code` / `Logic` / `Knowledge` / `Commonsense`，**CoT 归 Logic**）**单纯形采样**。
- 搜索空间若有物理约束（`sum=1`、非负）→ 用 **`suggest_float` + 归一化**，**不要**用会越界的独立 `suggest_float`。

#### ⑤ 目标函数（objective）与收尾

- **主 objective = 固定 held-out 验证集 loss**（⭐ **整轮固定同一个 held-out bin，防泄**；用 `suggest=` 采样出的配比去训，在**同一验证 bin** 上测）。
  → 便宜、信号密、**可早停**；**别对 300+ 个模型都跑 `lm_eval`**。
- **早停**：`MedianPruner`（如 **1/3 步处 loss 显著差于中位 → prune**）→ 同 24h 内能跑**更多** trial。
- **收尾**：取 **top-K（如 5）** 配比跑 **`lm_eval` Table 2（8 集）/ Table 3（6 集）** 复核（复用 pretrain 已打通的 `ckpt → HF → lm_eval` 管线）。
- **可复现**：每 trial 落盘 **Optuna `sqlite` storage** + **trial 配置 CSV**（`number / params / steps / loss / status / created`）。
- **依赖安装**：`optuna` **装进独立 env**（🚫 **不许污染共享 `py310`**，见上方「环境隔离纪律」）；**外网命令显式带 proxy**（见上方 proxy 口径块）。

#### ⑥ 交付 & 纪律

- **交付**：**重写 `DATA_MIX_RECIPE.md §6`** = **① Optuna study 定义（搜索空间/采样器/pruner/objective）② trial 数（实测）③ 两段各自的最优配比百分比 ④ 外推到 2.2B 的迁移性说明**（引用 `ye2024datamixinglaws`；**如实标注「代理规模 ≠ 2.2B」这一限制**）；每 trial 一行进实验记录（`MEMORY_DATA.md` / `DATA_LEDGER.md`）。
- **口径统一**：`DATA_MIX_RECIPE.md` 里 §6 的模型尺寸数字**有 2.2B / 2.47B / 3B 三种写法** → **一并订正**（以 `pretrain_launcher.py` 的 `NVIDIAMambaHybridModelProvider2B` = **2.220B** 为唯一准据）。
- **纪律（不变）**：🚫 不改 pretrain 的脚本 / 🚫 不碰 `.29` GPU0–1 / 🚫 **不 kill 对方进程** / 🚫 **全轮不出现领域化** / 重 I/O 避让（`.29` 与 `.12` 共享 `/nas_train`）。
- **回写**：`MEMORY_DATA.md` 的「进度快照」+「运维问答」须写清 **标定结果** 与 **最终两段配比**。

> ✅ **本块生效即视为已批准**，**无需再等拍板**。**这是当前 data 线唯一主攻**（白名单下载巡检照常后台低强度进行）。
> 📌 **一句话**：**用小模型跑几百次试验去拟合配比，而不是用 2.2B 跑一次；两天（Stable / Decay 各一天）出配方。**

---

> 📦 §运维指令 · 2026-10-05（HTML报告 + D-CLEAN-4 定案 + 环境隔离）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：report_data_mix_s0a.html 已产出（已废弃）、D-CLEAN-4 保留不动、环境隔离纪律见 proxy 口径块。需要时再读。


### 🆕 运维口径 · 2026-10-05（**你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测**）

> **定位（运维 2026-10-05 13:2x，跨线）**：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——**目的是给内网网关鉴权**（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ **你（agent）会话里每条命令都继承了「无代理」env。**
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 **`Network is unreachable`（Errno 101）/ http `000`** 是**预期现象**：🚫 **不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题**——**别把它写进结论**。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ **同机反证**：`run/harness/r1_eval.py:144-148` 正是**显式钉 proxy + 阿里云索引**，所以**同一台 `.29`** 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：GPU2-7 归 data、配比实验已开工。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_DATA_TASK.md` ≈ **78KB**、`MEMORY_DATA.md` ≈ **29KB**（**任务书已是记忆的 2.4×** —— 旧规程只管记忆、漏了更大的一头）。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_DATA.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_DATA_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成的**调研轮次原文** → 沿用 `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md` 等；
  ④ 较早的**唤醒流水**（保留最近 ~20 条） → `daily-memories-data/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有「见 §③.9」「上方块」这类交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 「进度快照」③ 「运维问答」（**这一区不清**，运维靠它读答复）④ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---


| 项 | 当前值 |
|:---|:---|
| **🆕 下载白名单（2026-10-03 最新 · 覆盖一切下载类指令）** | **只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族剩余）② GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（43 天 / 非必需 / 阻塞后两项）；🚫 **白名单外一律不下载、不调研、不推荐**（含 `UltraX-Preview`）→ 详见顶部「运维指令 · 2026-10-03（下载白名单锁定）」 |
| **历史指令** | 📦 D-CLEAN-4/当前指令/优先级覆盖/状态索取/暂停标志（2026-10-01~04）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：全部已闭合/被运维指令区新块取代（配比实验改道为BO搜索，见上方活跃块）。需要时再读。 |

---

## 📊 进度快照（**每次唤醒必须更新**，供远程巡检）

> 固定格式写在 **`MEMORY_DATA.md` 最顶部**，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

**运维巡检方式**：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；**不需要登录服务器**。

---

> 📦 §0「当前主攻」+ §0.6「R4阶段 P-8 数据配方」（2026-10-02）已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：R/R2 调研完成、配比实验已改道为小代理+BO（见运维指令区改道方案块）。需要时再读。
---
## 1. 任务目标

把已在盘上的原始语料，变成**训练可直接消费、配比正确、且不污染评测集**的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ **← 🚫 已取消**（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. **污染隔离白/黑名单 + 校验脚本（红线，P0）**

**上游方案文档（先读它）**：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
**时间线约束**：ISEDA 2027 投稿截止 ≈ **2027-02-01**；本任务必须在 **2026-11 底**前可交接（见方案 §6）。

> **注意本任务的定位**：瓶颈是**算力窗口**不是数据量（方案 §2.1）。
> 所以**不要**把精力花在"下载/切分更多数据"上，而要花在**质量、配比、格式可用性、隔离**上。

> 📦 §1.1「数据落盘地图」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：实测数据位置详见 DATA_LEDGER.md。需要时再读。

> 📦 §2「阶段与推荐执行顺序」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：R/phase0/phase5 完成，当前主攻=配比实验（见运维指令区）。需要时再读。

## 3. 红线：污染隔离（**违反则全部下游结论作废**）

🚨 **`EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。** 改写/paraphrase 也不洗白。

- ✅ **允许**入训练集：PyAether / SKILL 的 **API 参考文档**（它是任务的"来源材料"）
- ❌ **禁止**入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ **阈值写明可复现** ④ **SFT 语料同闸** ⑤ 独立报告
- 同一条规则适用于**多模态 held-out 评估集**（如 `eval5k`）：与训练集不同源 + 跨集去重比对

**评测集本体路径**（用于建黑名单，**只读，绝不写入任何训练集**）：
`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`

---

> 📦 §4「git 与共享工作区规则」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：git 规程见「收尾铁律」§3 + AGENTS.md §4。需要时再读。

## 5. 资源与约束
> 📦 §5「资源与约束」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；**结论**：常驻 .12、GPU2-7 归 data（见运维指令区）、重 I/O 避让。需要时再读。


## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：**顶部"进度快照"**（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| **`run/DATA_RESEARCH.md`** | 🎯 **调研报告（当前主攻）**：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | **数据清单**（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | **污染隔离报告**（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 **`DATA_RESEARCH.md`（调研报告，当前主攻）** —— **两个问题各四小项全部有结论**，每条关键结论可顺 URL 复核
2. `DATA_LEDGER.md`（数据清单，含**实测**规模与与方案文档的差异）
3. `CONTAMINATION_CHECK.md`（污染隔离规则 + 阈值 + 扫描量 + 命中 + 处置）
4. `run/data_pipeline/`（可复现脚本，至少含盘点、校验、分词打包、指纹比对）
5. 训练可消费的产物（`.bin/.idx` + webdataset），**路径与校验和写入清单**
6. `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html`（自包含，与既有 HTML 报告同风格）
7. git commit + push（只提交 doc/ 文本与 run/ 脚本）

---

## 8. 推进原则

- **无阻塞时连续推进**：把能立即做完的步骤一口气做完（可跨多个阶段），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟）。
- **有异步阻塞时**：回写记忆并把 `WAITING` 置 `1`，记录"等待什么、如何判断结束"，然后退出。
- **不确定就如实记录并上报**，不要编造数据、不要产出"看起来对"的合成语料。
