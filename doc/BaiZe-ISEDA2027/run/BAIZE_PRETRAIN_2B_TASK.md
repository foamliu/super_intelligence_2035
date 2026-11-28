# BAIZE_PRETRAIN_2B_TASK.md
> ## 🔴 常驻职责 · 2026-11-28 19:2x 用户令 · **pretrain 为预训练的健康负责**
>
> **用户原话**（逐字）：「加一条 pretrain 的职责：监控 S2 的训练，如果崩溃需要跟 data 协调后把训练修好。总之：pretrain 为预训练的健康负责！」
>
> **修正（2026-11-28 19:3x 用户令）**：「让它自己解决，遇到问题可以读取 data 记忆作为参考。」
>
> **一句话：pretrain 为预训练的健康负责。**
> - **监控 S2**：step / loss / NaN·skip / GPU 利用率 / iter 推进，异常第一时间发现。
> - **崩溃处置**：**自己定位、自己修、自己拉起**（数据配比 / shard / DataLoader / OOM / 内存侧都在你的范围）；需要时读 data 线的 `MEMORY_DATA.md` 与 `run/data/blendswitch/` 作参考，**不用等 data、不用协商**。直到恢复健康推进。
> - **收口记录**：MEMORY 记「崩溃时刻 · 根因 · 参考来源（可含 data MEMORY / blendswitch 文档）· 修复项 · 重启命令 · 验收五项（iter 续上 / step ≤7.4s / loss 正常 / 0 NaN / 0 skip）」。
> - **例外（2026-11-28 20:0x 用户令）**：S2 的内存实验与重启**当前由 data 执行**；pretrain 只做只读监控、不重复启停，data 达标交付后交接回 pretrain 长跑。
> - **现状（20:0x）**：`code/baize-llm/configs/common.env` 已被改为 `nw=2 + no_mmap=1`（commit `c423bcb9cc`，19:59），属**未验证的降速路径**；S2 实际启动配置以 data 20:0x 令的实验结论为准（硬指标 step ≤7.4s，`nw=0` 一律否决）。




> ## 🔴 2026-11-28 19:0x 用户令 · **查两机内存占用 + 做清理（最高优先）**
>
> **用户原话**（逐字）：「让 pretrain 看看两台机器的内存占用 做清理」
>
> **背景**：S2 已于 **18:09:11 崩溃** —— `.29` rank13 的 DataLoader worker（pid 3983423）被 **SIGKILL**，报 `is killed by signal: Killed`；本线 2026-10-27 #801/#802 对同签名事故的定论是 **worker RSS 累积 → swap 耗尽 → 内核 OOM-kill**。当前配置 `code/baize-llm/configs/common.env:72-79` = `BAIZE_NUM_WORKERS=8` / `fork`（START_METHOD 空）/ `PERSISTENT_WORKERS=0` / `mmap enabled`。
>
> **你要做的**：
>
> **1. 两节点各采一次内存全景**（`.29` 本机 + `ssh .12`）：
> ```bash
> free -g
> grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree|SReclaimable|Slab|Mapped|Dirty|Writeback' /proc/meminfo
> vmstat 1 5
> ps -eo pid,ppid,user,rss,pmem,etime,args --sort=-rss | head -25
> cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.events 2>/dev/null
> cat /proc/sys/vm/swappiness /proc/sys/vm/overcommit_memory
> ```
> 两机分别记：RAM used/avail、**swap used/free**、page cache、Slab、cgroup `memory.events` 里的 **`oom_kill` 计数**。
>
> **2. 顺手取 18:09 崩溃的铁证**：
> ```bash
> dmesg -T | grep -iE 'killed process|Out of memory|oom-kill' | tail -30
> journalctl -k --since '2026-11-28 17:50' --until '2026-11-28 18:15' | grep -iE 'oom|killed process'
> ```
> 命中 `Killed process 3983423 (python)` ⇒ 把**该行原文**写进 MEMORY，#3582 的「OOM 嫌疑」正式定性；没命中 ⇒ 如实写「dmesg 无 OOM 记录，转查 audit/hub 登录与 kill 记录」。
>
> **3. 做清理**（只清「确认无主 / 已退出 / 本线自产」的）：
> - ✅ 可清：本线 `/tmp` 旧日志与 core dump（`/tmp/baize_*` ≥3 天、`core.*`）、已结束的 torchrun/eval 残留进程、**经 `lsof` 确认无主**的 stale shm（`/dev/shm/torch_*`）、本线临时产物（`.bak`、临时 HF/GGUF 转换目录）。
> - 🚫 禁清：**任何 ckpt**、别线进程与文件（posttrain / vision / harness / data）、root 进程（GPU0-3 sglang 等）、`/nas_*` 上非本线内容；**🚫 不 `drop_caches`**（要做得单独报批）。
> - 每条清理动作记：`PID 或路径 · 大小 · 判无主的依据 · 是否可回滚`。
>
> **4. 前后对比**：清理前后各记一次 `free -g` + `ps` top-RSS，给出**释放量（GiB）**。
>
> **5. 交付**：`MEMORY_PRETRAIN_2B.md` 顶部一条（前后数字 + 清理清单 + OOM 定性结论 + 证据行原文）+ `run/reports/report_pretrain_memory_cleanup_zh.html`（两机内存/swap/top-RSS 表 + 清理项 + 释放量 + 残余风险）。
>
> 做完即止。



> ## 🔴🔴 2026-11-28 09:2x 用户令 · **立刻把 S1 训练停下**
>
> **用户原话**（逐字）：「让 pretrain 立刻把 S1 训练停下」
>
> **要求**：**立刻停止当前 S1 训练**。不要等 360k ckpt、不要等当前 step 跑完、不要先做一轮监控再动手。
> - 两节点（`.29` + `.12`）的 S1 训练进程全部停掉（`train.sh s1` / `pretrain_launcher` / `torchrun`）。
> - 停之前先确认最新 ckpt 已落盘安全。
> - 停完记录：停的时间、杀掉的 PID（两节点）、停止前 iter / loss、最新可用 ckpt。
>
> 完成即止，不必附带其他巡检。



> ## 🔴 2026-11-28 08:1x 用户令（最高优先 · 覆盖此前所有 S2 切换相关约定）· **S2 切换：GPU 非空闲就杀死占用 GPU 的进程，坚决启动 S2**
>
> **用户原话**（逐字）：
> 1. 「安排 pretrain 修复 S2 切换过程中遇到的一些困难，坚决完成 S2 切换，绝不退回到 S1。」
> 2. 「如果 GPU 非空闲，那就杀死占用 GPU 的进程，坚决启动 S2。不要给自己找借口。」
>
> **要求**：
> - S2 切换必须完成，**不退回 S1**。
> - GPU 非空闲时，**直接杀死占用 GPU 的进程**，然后启动 S2。
> - 遇到的问题自己修，**不要给自己找借口**。
>
> **交付**：执行完在 `MEMORY_PRETRAIN_2B.md` 置顶记一条（改动 / 杀了哪些进程 / S2 起跑证据 / 验收五项）。



> ## 🔴 2026-11-26 20:3x 用户令 · **L1 评测节奏 2k → 每 1 万步一次** · 覆盖 11-21 放行令的 2k 口径
>
> **用户原话**：「pretrain：没有必要每个检查点都评测，每 1w 步评测一次即可」
> **动因**：现行每 **2k** 一点（已 56 点）；19:58 的 330k eval 正是 eval 负载把 step avg10 从 7.39s 顶到 8.0s+ 超 7.4s gate 被杀（MEMORY #3417）。10k 节奏可砍 eval 负载约 **80%**。
>
> 1. **只评 `iter % 10000 == 0`**：10k,20k,…,700k（共 70 点）。**下一个 = 340k**；**330k 本身在边界上，FAILED 补评照做**（属新口径，非例外）。
> 2. **不回溯删结果**：已评 56 点（2k 密度）保留，报告照常包含，但说明里加一句「**≤328k 为历史 2k 密度，≥330k 起为 10k 密度**」，防论文/读者误读曲线密度。
> 3. **口径不变**：harness_avg（`acc_norm`×6+`acc`×2）、llama.cpp GGUF、同版本/同 `-t4`。🚫 不许借减频换量尺。
> 4. **实现**：`baize_l1_autoqueue_continuous.sh` 的 ckpt 过滤改 `iter % 10000 == 0`（**保留** step<7.4s gate、HF/GGUF skip-if-exist、串行）；🚫 删盘上 2k ckpt。
> 5. **红线**：10k 点漏评 ⇒ **必须从已落盘 ckpt 补评，不许跳**；前后各记 step time + 两机 load；心跳加 `eval_next=<下一个 10k 边界>`。若 330k 补评后 step 仍长期 >7.4s ⇒ 照旧记 `⚠️ 待运维处理`，不得硬顶。

> ## 🔴 2026-11-21 17:0x 用户令 · **放行 autoqueue —— 270k / 272k 及后续万整数 ckpt 立即补评** · 覆盖「维护态保守 hold」

> **用户原话**：「pretrain：放行 autoqueue」

**背景**：此前在维护态下**保守 hold 了 eval**，导致 **270k（iter_0270000）与 272k（iter_0272000）两个万整数评测点积压未评**（L1 仍停在 260k=59.00%，26/27 完成）。

**一、授权范围（仅限 eval，不涉训练）**
- ✅ **放行 autoqueue**：对所有**已落盘的万整数 ckpt**（270k / 272k，以及此后每新落盘的 274k / 276k …）**立即启动 L1 评测并刷新报告**。
- ✅ 按 TASK 既有口径执行（L146 条款）：新 ckpt 出现即评一次、刷新 `report_pretrain_llamacpp_scaling_zh.html`。

**二、执行要求**
1. **一次把积压清掉**：先补评 270k、272k（若新 ckpt 已落盘一并纳入），跑完在 MEMORY 写出每个 ckpt 的 L1 分数。
2. **监控负载**：eval 会占 CPU（`llama-server`）。跑前记录两机 load，跑后再记一次；若 step time 因此从 ~7.17s 明显上抬（>7.4s 持续）⇒ **立即暂停 eval 并记 `⚠️ 待运维处理`**（11-18 MegaMath CPU 争抢事故的教训）。
3. **每次 eval 前后各测一次 step time**，把「有无 eval 负载」写进心跳，便于日后归因。
4. **evidence 三件套**照旧：ckpt 路径 + eval JSON/日志路径 + 复现命令。数字取不到就写 `TODO(BLOCKED: 原因)`，🚫 不估不猜。

**三、顺带**：`WAITING` 仍按实际状态维持 0；eval 串行跑时可在心跳记 `eval_running=<ckpt>`。

---

> ✅ **用户令 · 2026-11-18 — 训练 resume 后吞吐减半，排查原因（已完成）** — 根因=`.12` CPU 争抢(data 线 MegaMath 分词 8925% CPU)；运维直接干预重启自 iter_244000，CPU 释放后 step time 回落 ~7.0s；2026-11-19 06:36 训练健康 iter=252000。详见 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-19」节。

> ✅ **用户令 · 2026-11-17 — Stable 段 S1/S2 等分可行性报告（已完成）** — 报告已交付 `run/reports/report_s1s2_split_pretrain.md`(36.7KB)。

> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不估不编、评测数字口径真实）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权判断什么最值得做、并主动追异常。**

> ✅ **用户令 · 2026-11-12（L1/L2 评测脚本入库 + L4 移交）· 用户直令 · 已完成（commit ed6ea54e4 · 12 脚本 + README §4.6 · L4→HANDOFF→post-train）**
>
> **用户原话**：「Pretrain：把修好的 L1/L2 评测脚本提交到 baize-llm 仓库，相应刷新 README。」「既然后训练说『隧道第 4 次复验 OK』，那么 Pretrain 说的 L4 BLOCKED 就不成立了。这件事 Pretrain 不要管，由 Post-Train 负责。」
>
> **① L1/L2 评测脚本入库（已完成，需你确认可用并接手维护）**
> - 已落 `code/baize-llm/scripts/eval/`：`baize_l1_autoqueue_170k.sh`、`baize_l1_autoqueue_180k.sh`、`baize_l2_hf_humaneval.sh`、`baize_l2_hf_humaneval_direct.sh/.py`、`baize_l2_hf_humaneval_py310.py`、`baize_l2_hf_gsm8k_direct.py`、`baize_l2_hf_mbpp_direct.py`、`baize_l2_hf_bbh_direct.py`、`baize_l2_hf_math_direct.py`。
> - `code/baize-llm/README.md` 已新增 **§4.6 能力评测（L1/L2）**：口径（L1 走 GGUF+loglikelihood、L2 必须 HF 直跑，禁用 llama.cpp 生成判据）、用法、依赖、已知坑。
> - 你的职责：训练机上以 `scripts/eval/` 为**唯一启动入口**跑评测；如脚本再修，直接改这里，不要再散落回 `run/`。
>
> **② L4 移交 Post-Train（即刻生效）**
> - **L4（zhulong 消融评测 + designflow / EDA-Flow-Bench）不再由 pretrain 负责**，由 post-train 主责（其隧道已 4 次复验 OK、run_code 端到端 PASS）。
> - 你从本轮起：**L4 状态统一写「HANDOFF→post-train」，不写 BLOCKED、不再做 L4 资源调查、不再尝试 .15/.17 直连**。
> - 四层口径调整为：L1 / L2 / L3 由你负责；L4 只做**只读引用**（post-train 出数后引用）。
>

> 🎯 **用户令 · 2026-11-11（关注点：如何拿到更好的结果，不是打磨论文）· 用户直令 · 最高优先**
>
> **用户原话（两次）**：
> ①「pretrain：这些预训练主要看结果，这些前期消融根本就不应该进入论文。你可以参考其他预训练论文，比如MiniCPM、DeepSeek、Kimi，绝对没有人在论文中写这么细的消融。我们的论文中这些内容都需要删掉。我让agent做了实验，却不是想把所有实验经过和结果都写入论文。」
> ②「它需要考虑的是如何拿到更好的结果。这些结果在常识推理8集、复杂推理6集、agentic能力（比如SWE-bench、Terminal-bench以及Kimi DeepSeek在意的其他评测），最后是领域能力，也就是zhulong/designflow评测的能力。」
>
> #### 0. 定位修正（先读，之前"读论文提建议"的方向是错的）
>
> - ❌ **错的**：把超参搜索每一步、每个消融数字写进论文；或"补更多消融让论文更扎实"。
> - ✅ **对的**：**只关心四层能力评测能不能拿到更好的数**。消融是内部过程，不进论文。
> - 参考 MiniCPM / DeepSeek / Kimi：**正文只报最终配方 + 最终结果**；消融最多一句 "we tuned X on a 5k-step proxy"，或进附录。
>
> #### 1. 四层评测目标（你的主战场）
>
> | 层 | 评测 | 现状 | 目标 |
> |:--|:--|:--|:--|
> | **L1 常识推理（8 集）** | ARC-e/ARC-c/BoolQ/HellaSwag/OBQA/PiQA/SciQ/Winogrande | ✅ 已有（160k: Avg 58.13%） | 继续推高 |
> | **L2 复杂推理（6 集）** | GSM8K / MATH / MMLU / BBH / HumanEval / MBPP | ✅ 已有，但 **GSM8K 1.52% / MMLU 23.79% / BBH 14.04% 明显偏低** | **重点补** |
> | **L3 Agentic** | **SWE-bench（verified）/ Terminal-bench** + Kimi/DeepSeek 在意的其他（τ-bench / WebArena / GAIA） | ❌ **完全空白** | **从 0 建立** |
> | **L4 领域能力** | **zhulong 消融评测 + designflow（EDA-Flow-Bench）** | ❌ **未接**（两个 bench 都有成品可跑） | **接上并跑** |
>
> #### 2. 每轮该做什么（按优先级）
>
> **P0 — 补 L3/L4 缺口（当前最大空洞）**
> - **先查 L2 异常**：GSM8K 1.52% 对 2B 模型**不正常**（正常应 >5%）⇒ 先判定是评测配置问题（0-shot / extract 方式 / stop token）还是真能力问题。
> - **L3 agentic**：先选 1–2 个能跑起来的（Terminal-bench 比 SWE-bench 轻），建立最小可跑 pipeline；**不必一步到位全上**。
> - **L4**：zhulong 与 designflow 都已有评测脚本和 jsonl，**去对接**，先跑一个 ckpt 出基线数。
>
> **P1 — 四层定期复跑**
> - 每跨 20k ckpt 跑一次四层全量，记进 `EXPERIMENTS_PRETRAIN_2B.md`（**不进论文**）。
> - 维护 `reports/report_pretrain_eval_4tier_zh.html`（中文 · 四层能力趋势）。
>
> **P2 — 结果驱动的配方调整**
> - 某层明显落后 ⇒ 分析是数据配比（如 code 占比对 SWE 的影响）、训练阶段（early vs decay）、还是评测口径问题。
> - 建议必须**指向具体动作**（加多少 code / 何时开长上下文 / 是否提前进 decay），不是"再做一轮消融"。
>
> #### 3. 论文怎么写（用户已明确）
>
> - **`4_llm_pretrain.tex` 应大幅瘦身**：删 Search Protocol 小节、删 `tab:configs`（S1–S5 逐条结果）、删 dense/hybrid 那 6 行对比表。
> - **保留**：架构选型一句话 + 最终配方 + 数据配比 + 生产 run 状态 + 长上下文能力。
> - 消融细节移到附录或直接不写；正文不出现 5000 步/20000 步的搜索过程。
> - ⚠️ 改稿是例行轮的活，但**判断"哪些该删"由本节的评测视角决定**。
>
> #### 4. 红线不变
>
> - 🚫 **评测数字不进论文正文**（2026-11-10 令仍有效）；评测是**监控与决策依据**，落 `EXPERIMENTS` / `MEMORY` / `reports`。
> - ✅ 但**评测结果决定你接下来做什么** —— 这是本节的核心。
>
> #### 5. 交付
>
> - 每轮 MEMORY 记一行：`#<轮次> 四层评测 · L1=<avg> L2=<key> L3=<status> L4=<status> · 本轮动作：<一句话>`
> - 新建/维护 `reports/report_pretrain_eval_4tier_zh.html`（中文 · 单文件自包含）—— **这是评测报告，不是论文建议**。
> - 发现某层需配方调整 ⇒ 写进 MEMORY「待决策」区并给出你的建议方案（含预期收益与风险）；生产配置由用户拍板后改。


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

> 📦 §运维令·2026-11-10（刷新 ISEDA2027 论文预训练章节 · 详细指令）已归档 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-15」节。
> **仍有效**：① §4.6 进度句需更新为实测 iter/tok·s⁻¹/loss（论文根目录 `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/`，只改 `ISEDA2027/4_llm_pretrain.tex`）；② 🚫 评测数字不进论文正文（21:2x 更正，§4.7 已撤回）；③ 11-11 起关注点转向四层评测拿结果，非打磨论文。
> 📦 §运维令·2026-11-08 15:3x（全量eval均值37.40%异常调查）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-09」节；**结论**：✅ 报告report_pretrain_eval_avg7_anomaly_zh.html(50KB)已交付,结论A(口径差异):stale results.json缺piqa致低估,补全后Avg7=55.96%与历史56.71%仅差-0.75pp。需要时再读。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

> 📦 §运维令·2026-11-07 15:2x（全量eval提速）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-09」节；**结论**：✅ 报告report_pretrain_cpu_eval_speedup_zh.html(17KB)已交付,llama.cpp 7×提速已用于万整数ckpt评测。需要时再读。


> 📦 §运维令·2026-11-07 09:1x（11w 检查点 8 集评测：去 `--limit 100` 改全量 + 扫线程/batch）**✅ 已交付 #1570**；§2026-10-30 22:2x（1M 长上下文 + 95% 大海捞针报告，`report_pretrain_1m_needle_zh.html` 33.7KB）**✅ 已交付 #983** → 两者原文归档 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。**结论**：① 探测矩阵 8/8 完成，**16 线程饱和（SSM 顺序扫描不可并行）、80 线程 bs1 反变慢、80×bs2 最优 1.36x** → `report_pretrain_cpu_eval_thread_scaling_zh.html`；② 全量 eval 已启动（16 线程 bs1 无 limit）。需要时再读。




## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### ✅ 用户令 · 2026-11-27 08:3x（**S2 切换准备：350k 时执行 blend hot-switch，由你操作**）· 用户直令 · 最高优先 · 已完成（运维直接执行）

**背景（必读）**：
- 训练当前 iter ≈ 340k/700k，**350k 切换点 ETA ≈ 11-28 06:00**（约 18h 后）
- data 线已完成 **Plan F 自定义改造**：`blend_switcher.py`（416 行）+ `blend_hotswitch.patch`，实现了 S1→S2 权重热更新 + per-source 游标映射 + 零重叠
- 验证状态：standalone 8/8 PASS + Megatron integration 7/7 PASS，zero_overlap=0，flag-off 与 stock 逐字节等价
- **你的职责**：在 350k ckpt 保存后，应用 patch + 切换 S2 blend → 重启训练 → 继续监控

**切换前准备（现在就做，不等 350k）**：

1. **阅读 data 交付物**（理解 patch 原理和操作步骤）：
   - `run/data/blendswitch/README_PATCH.md`：patch 说明 + 安装步骤 + 验证结果
   - `run/data/blendswitch/blend_hotswitch.patch`：patch 本体（新增 `blend_switcher.py` + 修改 `blended_dataset.py` / `samplers.py` / `loaders.py`）
   - `run/data/blendswitch/blend_switcher.py`：核心逻辑（权重热更新 + 游标映射）
   - `run/data/blendswitch/s2_blend_switch_config.json`：S2 切换配置（source keys + weights）
   - `run/data/blendswitch/test_blend_switch.py`：验证脚本（8 项测试）
   - `run/data/blendswitch/verify_results.json`：验证结果（8/8 PASS）
   - `run/data/blendswitch/verify_results_integration.json`：集成验证结果（7/7 PASS）

2. **理解关键参数**：
   - patch 的开关是 `--blend-hot-switch`（默认关闭，关闭时与 stock 逐字节等价）
   - S2 blend 配置：`blend_s2_preblend.tsv`（已在 `code/baize-llm/configs/` 中，10 源 web40/code40/math20）
   - 切换时机：350k ckpt 保存后（save-interval=2000，所以 350k 会自然落盘）
   - 切换后训练参数不变（LR、warmup、seq-length 等全保持，只换 blend）

3. **制定切换 runbook**（写进 MEMORY，不等 350k）：
   - 步骤 1：等 350k ckpt 落盘确认（`ls checkpoints/iter_0350000`）
   - 步骤 2：kill 当前训练进程（两个节点的 torchrun + pretrain_launcher）
   - 步骤 3：应用 patch 到训练代码（`cd code/baize-llm && git apply run/data/blendswitch/blend_hotswitch.patch`，或手动 cp `blend_switcher.py`）
   - 步骤 4：修改 `s1.env` 或启动参数，加入 `--blend-hot-switch` + S2 blend TSV 路径
   - 步骤 5：从 350k ckpt resume 启动训练（`bash scripts/train.sh s1`，配置已含 S2 blend）
   - 步骤 6：验证切换成功（step time 正常 ~7s、loss 无异常突跳、前 100 步 ratio 偏差 ≤1pp）
   - 步骤 7：继续监控 + L1 评测 350k（S1 最后一个点）

4. **向 data 确认疑问**：如果阅读 patch 后有不确定的操作步骤，在自己的 MEMORY 记一行「待 data 确认：<具体问题>」，data 下轮唤醒会看到并回答。

**执行切换（350k 时）**：
- 在 350k 时执行 kill 训练 + 应用 patch + 重启
- 切换后恢复维护态（不再自行重启）
- 切换前先 commit 记录现场（当前 ckpt / step time / loss / 进程 PID）

**纪律**：
- 切换前后的 step time / loss / GPU 状态必须记录
- 如果 patch 应用失败或切换后训练异常（loss spike / NaN / step time >>7.4s），**排查修好再起**；🚫 不回退 S1（2026-11-28 用户令：绝不退回 S1）
- S2 blend 的 zero_overlap 已由 data 验证（8/8 + 7/7 PASS），你不需要重验，但切换后前 100 步要观察 loss 是否有异常突跳

---

> 📦 §2026-11-25 13:1x（daemon print 口径修复 acc_only→harness_avg · #3365 已完成）→ `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-25」节。

---

> 📦 §2026-11-25 10:2x（L1 评测持续下降排查 · NOT 真下降 · #3349 已完成）→ `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-25」节。

---

> 📦 **2026-11-19 13:2x 改论文第二轮**（贡献点重写/§5改Domain Adaptation）**✅ 已完成**（commit 53985409e · 2026-11-19 14:12）→ 原文归档 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-19 论文改进第二轮」节。**结论**：① 删重复引述句+中文注释；② 贡献点3项重写(2B Mamba2-hybrid+1M ctx / curriculum learning / domain adaptation)；③ §5标题改Domain Adaptation(label不变)+ACI段落；④ pipeline表改"Domain adaptation (anneal, SFT, RLVR)"；⑤ latexmk 0err 5pp 0undefined。已push。

> 📦 **2026-11-19 08:3x 论文改进令**（精简摘要/贡献点拆解3项/backbone TikZ图fig:backbone）**✅ 已完成**（commit 23068482d · 2026-11-19 10:01）→ 原文归档 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-19 论文改进」节。**结论**：0_abstract删volatile快照句(169130/591K/loss≈2.04)、1_intro贡献点拆解3项(cost-privacy子agent/Mamba2-hybrid结构成本/budget recipe+449eval)、3_architecture加TikZ Mamba2-hybrid层结构图(fig:backbone,4/56层session-growing state)、latexmk编译0err5页0undefined。已push到origin/main。需要时再读。

> 📦 **2026-11-18 吞吐诊断四令**（14:2x 告知重启 / 13:1x 立即重启 / 11:1x 授权重启 / 10:5x 排查吞吐腰斩）**✅ 均已完成** → 原文归档 `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-19」节。**结论**：根因=`.12` CPU 争抢（data 线 MegaMath 分词 `pc2_fast.py` 8925% CPU 占 89 核）；运维直接干预重启训练自 iter_244000；data 线释放 CPU 后 step time 从 ~13.3s 回落至 ~7.0s，吞吐闭环。截至 2026-11-19 06:36 训练健康 iter=252000/700000 step~7.0s/1030TFLOP/0NaN/0skip。需要时再读。

---

### [运维令] 2026-11-09 10:0x（**每满万整数 ckpt 做 8 集常识评测（limit=100）持续刷新同一报告 · 不得影响训练吞吐**）· 用户直令 · 最高优先

> 用户原话（2026-11-09）四点：①已认识到全量评测 8 集会影响吞吐 ②评测回退到每集 limit 100 ③每满万整数检查点做 8 集常识推理评测（每集 limit 100）④结果刷新同一个中文 HTML 报告（表格+折线图）。⑤评测仍保持 CPU+llamacpp(server) 维持 7× 提速。

**① 铁律（最高优先，先于评测本身）**：🚫 **评测不得拖训练吞吐**。训练 S1 当前 ~584–600K tok/s（16 卡满载），任何评测进程若把 step time 拉高（>7.4s/step）即视为越界：llama-server 用低线程（`-t 4` 或更低）+ `nice -n 19`，且**每次只跑 1 个 ckpt**（单 server + 单 client，串行），🚫 禁止像 11-09 那样 7 个 llama-server 并行（那就是吞吐 613K→560K 的根因）。每轮唤醒先看训练日志 step time，若 >7.4s 立即降载/暂停评测。

**② 评测口径（与历史基线完全一致，勿改）**：8 集 / zero-shot / **`limit=100`** / GGUF F16 / 修复后二进制（build 5dc38db00 或 PR 合并后的 master）。任务集 = `arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande`。后端 = `llama-server` + lm_eval `local-completions`/`gguf`（`-t 4`、`nice 19`、串行单 ckpt）。

**③ 待评测点**：**所有满万整数 ckpt**。已评完成 1w–10w（`gguf_iter_{10k..100k}_fixed_8set` 10/10 在）。**本轮补齐 11w/12w/13w**（iter_110000/120000/130000，均已在盘），之后每逢新的万整数 ckpt 落盘即补评（14w/15w/… 自动跟进，每新 ckpt 出现就评一次并刷新报告）。

**④ 评测流程（每 ckpt）**：export_hf（若该 iter 无 HF 导出）→ 转 GGUF F16 → `llama-server` 起服 → lm_eval 8 集 limit=100 → results.json 落 `gguf_iter_<iter>_fixed_8set/` → 杀 server（歇 CPU）。

**⑤ 报告刷新（同一文件，增量追加）**：结果并入 `reports/report_pretrain_llamacpp_scaling_zh.html`（或 60k_100k 版同文件，二选一固定），含：① 全 ckpt × 8 集表格（新增行）② Avg + 逐集折线图（x=iter，log 轴，叠加 700k 外推 + Xmodel-2 参照）③ 700k 对数拟合预测（R² 随点增多重算）。

**⑥ 纪律**：不碰 GPU（`CUDA_VISIBLE_DEVICES=""`）；🚫 禁止 `pkill python`/宽泛 kill（杀 server 只用 `kill <PID>`）；不碰 vision/data/harness；commit `pretrain eval:`；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到本轮 11w/12w/13w 三 ckpt 补评+报告刷新完成。

> 📦 **历史基线（§0 与 §1⑥ 的对照源）** —— 2026-11-05/06 llama.cpp 8 集能力曲线两批已合并归档 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`「归档 2026-11-06 第一批」+「2026-11-05 第七批」。**结论**：① 10/10 ckpt(10k–100k) 全评测，10 点 harness Avg `51.50→52.00→53.00→55.12→54.25→54.25→56.00→57.00→57.88→57.75%`；② 100k 双口径 **harness 57.75% / raw 54.75%**；③ 700k 对数拟合 **62.8% / R²=0.860**（幂律发散 pred 161% 已判退化）；④ `sciq` 全恢复非 NaN（证实 sciq=0 系 HF/bf16 路径问题，非 ckpt 权重）；⑤ **口径 = 8 集 / zero-shot / `limit=100` / GGUF F16 / `-t 8`**；⑥ 结果落盘 `gguf_iter_{10k..100k}_fixed_8set/results.json` 10/10 全在；生成器 `gen_llamacpp_scaling_report.py`（TARGET_ITERS=10 动态）。**⚠️ 本轮 37.40% 必须与此表同口径比对。**


> 📦 §运维令 2026-11-04 22:1x（llama.cpp 调试每环节落盘 + 清理残留）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ A-E 检查点全有结论(A/B/D=PASS, C=FAIL dt-clamp 影响小 1/64 head), 残留已清(llama-server 11→0, GGUF 34G→13G), 根因已定位。需要时再读。

> 📦 §运维令 2026-11-04 14:0x（定位 llama.cpp 映射 bug + 修复 + PR）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ 根因=GGUF converter 全权重逐张量对照发现混合架构权重错位→级联放大 3.6 nats; Mamba2 层 A/B/D PASS; 修复后 logits Δmax=0.006; PR #31703 已提交 https://github.com/ggml-org/llama.cpp/pull/31703; dt-clamp follow-up 待单独 PR。需要时再读。


> 📦 §运维令 2026-11-04 13:2x（logits 逐 token 对齐定案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ 1-token 即偏 3.6 nats，定案=映射/计算错误（非精度累积），llamacpp.txt §6+§7 已更新，commit eca8b7f49。需要时再读。

> 📦 §运维令 2026-11-04 09:3x（llama.cpp 提速 pilot）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ llh 打分打通、5/5 eval 完成（10K/30K 有效 Avg=50.00%/50.25%；20K/40K/50K 因权重 NaN 无效）；llama.cpp 精度不可用，保留 HF float32。需要时再读。

> 📦 §运维令 2026-10-29 14:1x（整理并提交 baize-llm 独立仓库）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：✅ commit e1c6be4 pushed to origin/master，28 files（README 19.6KB + configs/9 + scripts/18 + docs/2 + .gitignore），symlink 已删除+纳入 .gitignore，ls-remote 匹配。需要时再读。

> 📦 §运维令 2026-11-02 11:1x（CPU 评测 5 ckpt 8 集）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ 5/5 CPU HF float32 eval 完成, 报告 report_pretrain_cpu_eval_8sets_zh.html(44KB)已交付, 被 11-05 llama.cpp 修复管线取代。需要时再读。


> 📦 **2026-10-24 ~ 2026-10-28 运维令已全部归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`。涵盖：10-28 计划定稿(GBS=256/700k)/613K锁定/baize-llm入库/blend报告；10-27 spawn/OOM/MCP工具；10-26 S1落地/RoPE θ=1e6/吞吐对齐613K；10-25 通宵攻坚(CUDA Graph修复)/16卡吞吐；10-24 双机调通(606K tok/s)/305K最佳实践。**仍有效**：① 启动口径 `bash .../baize-llm/scripts/train.sh <stage>`；② 613K 配方(16K/CP1/DP16/FP8/graph-OFF)；③ RoPE check_rope.py 需 ckpt 验证、lr-decay-shape exponential Decay 前验证。需要时按日期查阅归档。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

> 📦 **2026-10-16 ~ 2026-10-17 运维令已全部归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md` + `daily-memories/2026-10-17.md`。涵盖：#548 误判更正(NFS旧日志)、P0 resume闭环(长期授权训练挂了自行重启)、中继抢修(PID2706247健康)、`_orig_mod`崩溃修复(断点续跑至6890/19980无崩)。需要时按日期查阅。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）
> 📦 已归档（R3配比 / LaTeX / R2收官 / T3）→ `ARCHIVE_OPERATOR_PRETRAIN.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）原文搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `pretrain 归档: …` 前缀。
> 本轮动作：本任务书已归档瘦身（2026-11-15：11-10论文刷新详细指令→归档，2026-10-xx 📦指针→合并）。体积自检见心跳。


## ⚠️ git 同步规则（必读，2026-10-01 新增，每次唤醒都要走）

