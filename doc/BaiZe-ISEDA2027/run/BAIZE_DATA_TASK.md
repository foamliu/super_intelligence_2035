# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_DATA.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_DATA.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

> 📦 §运维指令·昨夜汇报HTML（2026-10-07）已执行完毕 → report_10_07_data_overnight.html 已交付；详细指令已归档 → run/ARCHIVE_OPERATOR_DATA.md。需要时再读。

### 🚨 运维指令 · 2026-10-07（**P0 · 两条下载线（base + GPIC）继续 / 立即重启 —— 正文口径统一为「数据下载失败需主动重启」**）· **最高优先 · 用户直令**

> **用户 2026-10-07 直令**：**data 的两条数据下载线必须继续跑** —— **base 死了 / 僵死就重启**，**从来没有过「拖着不动」的指令**（用户原话逐字见 `run/ARCHIVE_OPERATOR_DATA.md`「2026-10-07 口径修正」块）。
> ⇒ ① **两条下载线必须持续在跑**：**base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）+ **GPIC**；② **从来没有过「base 死了就拖着不动」的指令** —— 你心跳里连写的 `Base 下载: 进程已死（按指令保持不动）` 属**误读**，**立即废止该口径**。

> 🔍 **误读溯源（运维自查，如实说）**：旧第 36 行那句 `🚫 不改白名单 / 不动下载`，本是 **2026-10-03 白名单锁定时的巡检纪律**，原意 =「**不要擅自改白名单、不要乱动［健康的］下载**」，**不是**「下载失败也不许重启」。2026-10-06 15:1x **用户已直令重启 base**，那个 **P0 块**处置完后被归档进 `ARCHIVE_OPERATOR_DATA.md`（唤醒 167）⇒ **正文只剩「不动」半句，重启授权随归档一并消失**。**表述缺陷在运维，不在你。** 完整溯源（含用户原话 + 被替换掉的旧字句原文）见归档「口径修正 · 2026-10-07」块。
> ✅ **永久口径（即刻生效，覆盖旧表述）**：**数据下载失败需主动重启** —— **白名单内任一下载「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 `kill`（若还在）+ 重启**（沿用既有 retry-loop 规程），报告里标「**已重启**」+ 新 PID；**不再需要等运维点名**。
> 🚫 该条纪律**今后只剩一种含义**：**不改白名单、不起白名单外的新下载**；**白名单内下载失败 ⇒ 按「数据下载失败需主动重启」处理，不许再写「保持不动」**。

> **本轮唤醒内做完（不许拖到下轮）**：
> 1. **取证**：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer|download_it_pairs'`（留原文）+ 两目录 `.incomplete` 计数 + 最新 mtime。
> 2. **重启 base**（`l1_en_hq` 停在 **5476/6006 ≈91%**、`zh` **✅ 256/256 已满**）：
>    - `--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*'`（**config 级**）；🚫 **绝不拉 `en_v1_4`**；
>    - **retry-loop 包裹**（失败 `sleep 30` 自愈 —— 你 2026-10-04 唤醒 85 用过、有效）+ `setsid nohup`（`ppid=1`）+ log `Ultra-FineWeb/download_l1_zh.log`；
>    - ⚠️ 外网命令**显式带 proxy**（`.12` 用你 `~/.bashrc` 里的那个值）；
>    - **命令原文 + 首次输出（起步 part 号）贴心跳**。
> 3. **GPIC 判活**（PID / `gpic_train_XXXX.tar` mtime / 24h 新增 tar 数）→ **死即重启**（父 `download_it_pairs.sh` 一并核）；目标 **8001 tar** + test 128 ✓。
> 4. **心跳格式（本轮起固定写一行）**：`下载线：base l1_en_hq <n>/6006（+Δ, 活/已重启 PID, ETA）· zh ✅256/256 | GPIC <n>/8001（+Δ, 活/已重启 PID, ETA）`。
> 5. **P-8 关联（为什么急）**：base = **P-8（Stage (i) 本体）硬前置**（已分词仅 **22.05B tok**，P-8 需 ~100B）⇒ **base 下满即解锁 P-8 备料**；`l1_en_hq` + `zh` 双满 ⇒ **报运维「MiniCPM5 base 族就绪」**。

> **纪律（不变）**：🚫 不 kill 正在跑的 BO；🚫 不在 pretrain 释放前碰 GPU0-1；🚫 重 I/O 与 `.29` 抢 `/nas_train`；心跳 ≤60 min 且每步 commit + push；`TASK/MEMORY` ≤32KB。

---

### 📎 运维转发 · 2026-10-07（**R1 top-K `lm_eval` 结论更正**：名次方向 + ρ 符号 + 表格错字）· **参考/更正，非新任务**

> **优先级低于上方 P0 块**：不新增任务、不变节奏（BO 照跑、下载线照重启）。
> **来源**：对 `run/topk_lmeval_results.json`（**机器可读权威源**）+ `run/analyze_lmeval.py` 的**独立复算**（数值已对所有 8 集逐项复现）。**请把下列更正落到你自己的产出**：`report_data_mix_eval.html` / `DATA_MIX_RECIPE.md §9.2.1` / `MEMORY_DATA.md`；**旧措辞「ρ=−0.43 ⇒ 负相关 / 完全反向 / loss 排序错误」请删除**，它由下面 2 个 bug 产生。

> **① 名次方向 bug（`analyze_lmeval.py` L35）**：`np.argsort(np.argsort(avgs))` 把**均分最小**排成 rank 1，但 `accuracy` **越大越好** ⇒ 报告 `lm rk` 列**整体倒序**。补丁：`lm_ranks = np.argsort(np.argsort(-np.asarray(avgs))) + 1`（R2 收尾报告别让同一 bug 复发）。
> 　正确名次（均分降序）：**#182 0.3373 → rank 1（最好）** / #96 0.3354 → 2 / #198 0.3353 → 3 / #149 0.3338 → 4 / #79 0.3337 → 5 / #155 0.3320 → 6。⇒ **「BO rank1 → lm rank6，完全反向」不成立**：#182 两边都是第 1。

> **② ρ 符号被读反**：`spearmanr(loss, avg) = −0.43 (p=0.40, n=6)` 的含义是「**loss 越低 → 均分越高**」= **代理方向正确**，不是"反相关"。
> 　逐任务（与报告表数值一致）：`arc_ch −0.83 / hella −0.71 / wino −0.49 / sciq −0.43 / piqa −0.20` = **5 个方向有利**；`obqa +0.64 / boolq +0.78 / arc_ea +0.18` = 3 个反向（p≥0.07 全不显著）⇒ **「6/8 集呈负相关」应为 5/8**。
> 　⇒ 严谨表述 =「**证据不足**（n=6、p=0.40，无功效）」；唯一显著的 `arc_challenge`(p=0.04) 恰在**支持**代理一侧，且 8 任务出 1 个 p≈0.04 属多重比较正常波动。

> **③ `DATA_MIX_RECIPE.md §9.2.1` 表格是转位错字 + 重复名次，须从 JSON 重生成**：#155 真值 **0.3320**（文中 0.3420）/ #149 **0.3338**（0.3387）/ #79 **0.3337**（0.3387）/ #96 **0.3354**（0.3343）/ #198 **0.3353**（0.3350）；现表**两行同为 5/6**。

> **④ 真正站得住的结论（替换「loss≠能力」）**：6 配置 8 集均分 **0.3320–0.3373**，而 8 集随机基线均值 = **0.34375**；除 `boolq`（0.381 vs 0.50，**低 11.9pp** = 常数输出坍塌）外 7 集全在 **±3.3pp** 内 ⇒ **18.36M/0.016B 代理对这 8 集无能力**。全量 8 集单次评测 **SE≈0.44pp**（逐任务 0.43–1.97pp，二项近似），而配置极差仅 **0.53pp ≈ 1.2×SE** ⇒ **`σ=0` 只表示"重跑确定"，不代表配置差异可信**。**R2 改 objective 的决定不变、仍正确**，理由改为「**代理无分辨力 + 证据不足**」。

> **⑤ R2 操作提醒（同源，收尾时用）**：`--limit 500/task` 单 trial 评测 **SE≈0.73pp**；R2 `σ_obs` 0.92–0.98pp ⇒ 扣噪后**真实效应仅 0.56–0.66pp** ⇒ **每 trial SNR≈0.8（<1）**；`best=0.4155` 高出均值 **2.60pp**，而 ~50 次抽样的**选择膨胀期望 ≈2.80σ = 2.58pp** ⇒ **"best" 与纯噪声极值不可区分**。
> 　⇒ ① 收尾 **top-K 全量 `lm_eval` 是定案环节（准入条件，必须做）**；② **不要中途把 `EVAL_LIMIT` 500 调大**（trial 间评测子集不同 ⇒ 分数不可比 ⇒ 污染 GP 代理）；③ R1（全量集）与 R2（limit 500）**只比轮内排序，别比水平**。

> （更正落地后本块可归档：按「体积维护规程」搬入 `run/ARCHIVE_OPERATOR_DATA.md` 并留 1 行指针。）


### 🆕 运维指令 · 2026-10-06（🎯 **【用户三步令】① 收 Stable 200-trial + top-K `lm_eval`/Spearman/σ ② `s_step` 归因（1.5 s→~30–100 ms，`D` 0.016 B→0.5–1 B）③ `.29` GPU0-1 释放后 **8 卡**搜第二轮**）· **最高优先 · 用户直令**

> **用户 2026-10-06 三步令（按此顺序）**：
> 1. **把当前 data BO Stable 200-trial 跑完**；**排队中的 top-K `lm_eval` 8 集 + Spearman 秩相关 + 噪声测量也跑完**。
> 2. **做 `s_step` 归因（最高杠杆）**，争取把 **1.5 s 压到 ~30–100 ms** ⇒ **`D` 从 0.016 B 抬到 0.5–1 B**。
> 3. **此时若 `.29` GPU0-1 已释放，就用 8 卡搜第二轮。**

> 📦 §三步令①②详细执行计划（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：①200trial+top-K lm_eval+Spearman ρ=−0.43+σ=0 ✅；②MBS16→s_step 166ms(8.6×)→D=0.5B/trial ✅。需要时再读。

> **③ 第二轮搜索（**条件触发**：`.29` GPU0-1 已释放）**
> - **触发条件**：pretrain 侧 **D（P-9.11 补测）已完成并明确释放 GPU0-1**（运维会在心跳/任务书确认）。🚫 **在此之前绝不碰 GPU0-1**（pretrain A/B/D 在用）。
> - **做法**：用 **8 卡（GPU0-7）** 跑 **Stable 第二轮 BO**；`D`（token/trial）按 ② 修好的 `s_step` **反算**（目标 0.5–1 B；若 `T` 不允许则如实降档并标注），trial 数按 `T` 反算（**目标 ≥200 且尽量多**；512 若可达则取 512）。
> - 新 study 用**独立 DB**（如 `mix_search_eval_r2.db`）；**与 200-trial 的对照 = 只比「最优配比 + 排序结论」，不比 loss 绝对值**（`D`/GBS 不同，loss 尺度不同）；**同样跑 top-K `lm_eval` + σ**。
> - 产出 `report_data_mix_eval_r2.html`。
>
> **纪律（不变）**：🚫 **不 kill 正在跑的 BO**；🚫 **不在 pretrain 释放前碰 GPU0-1**；🚫 **不改白名单 / 不起白名单外的下载**（⚠️ **数据下载失败需主动重启**：白名单内任一进程「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 kill+重启，见顶部「运维指令 · 2026-10-07」P0 块）；**心跳 ≤60 min** 且每步 commit + push；做不完**如实写卡点 + 需要什么 + 阻塞**；`TASK/MEMORY` 体积均 ≤32KB。

> 📦 §P0 base下载重启（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：base下载已重启(PID 3520692,l1_en_hq 89%+zh✅256/256),proxy=172.19.92.25:13128,白名单不变。需要时再读。


> 📦 §目标函数错了（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：6项全执行✅(Round2用lm_eval 8集均分作objective, Spearman ρ=−0.43证实loss≠能力)。需要时再读。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> 📦 §收尾铁律·事故背景（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：心跳2h未更新致误判卡死→立「每轮必commit+push」硬约束。需要时再读。

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

> 📦 §第5轮·代理规模定案 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：d=128/L=14/N≈18.5M定案+5项必验全PASS+评测硬规则+第0步分工,详见各子指针。需要时再读。

> 📦 §用户复核② 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：5条判据(BO 200/200已满足)+先验88:8:4对照(进行中,见三步令①)+心跳纪律(已由收尾铁律覆盖)。需要时再读。

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

> 📦 §proxy口径·定位与反证段（2026-10-05）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：loop剥代理致外网不可达是预期→外网命令显式带proxy(见下方用法)。需要时再读。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：GPU2-7 归 data、配比实验已开工。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 📦 §体积维护规程·理由段（2026-10-03~06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：TASK/MEMORY每次唤醒全文读入→越大约烧token→≤32KB硬约束。需要时再读。
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
