# BAIZE_PRETRAIN_2B_TASK.md

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
> | **L4 领域能力** | **zhulong 消融评测 + designflow（EDA-LiveFlow-Bench）** | ❌ **未接**（两个 bench 都有成品可跑） | **接上并跑** |
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
> - 发现某层需配方调整 ⇒ 写进 MEMORY「待决策」区等用户拍板，🚫 不自行改生产配置。


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

> 🚨 **本轮最高优先（2026-11-10 用户直令 · 优先于一切状态确认 / 评测排期 / 归档）**：
> **刷新 ISEDA2027 论文的预训练章节。**
>
> ⛔️ **2026-11-10 21:2x 用户更正（效力高于下面全部内容，务必先读）**：
> **「评测结果不用写在论文里。评测是为了监控，训练还处于早期。」**
> → 即：**8 集 zero-shot / 任何 benchmark 数字都不许进 `main.tex` 体系**。这些数只用于
> 训练监控，落在 `EXPERIMENTS_PRETRAIN_2B.md`、`MEMORY_PRETRAIN_2B.md`、`reports/*.html`。
> → 原 §4.7 `Checkpoint Scaling on General Benchmarks` + `tab:ckpt-scaling` **已由主 agent 撤回**
> （2026-11-10 21:2x，commit 见 git log）；论文只保留 §4.6 的**训练状态句**（iter / tok·s⁻¹ / loss）。
> → 本轮及以后：**不要再把评测表/评测曲线加回论文**，直到用户明确要求（例如正式训练结束后写
> camera-ready 结果）。若你认为该加，先在 MEMORY 提建议，**不要直接改 tex**。
> → 若发现论文里还有残留的 benchmark 数字（包括摘要），同样视为 bug，删掉并在 MEMORY 记一行。
> 论文根目录：`doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/`（`main.tex` + `ISEDA2027/4_llm_pretrain.tex` + `main.pdf`）
>
> **一、现状（主 agent 实测，勿再核对，直接改）**
> 1. §4.6 `sec:llm-results` 的进度句仍是 **"At the time of writing, the run has passed
>    iteration 30,660 of 700,000 at ≈598K tok/s, training loss 2.151"**，而实际已到 **iter ≈154k**；
>    `tab:prod-budget` 的 Status 仍写 `30.7k done`。
> 2. **全文没有任何基准评测结果**（grep 过 ARC/HellaSwag/PIQA 均 0 命中）：15 个 ckpt（10k–150k）
>    已在 8 个 zero-shot 集上评完（Avg(harness) 51.50% → 58.00%），论文完全没收录。
>    → 这是审稿人必问的"你这个 2.2B 到底什么水平"，缺它就是硬伤。
>
> **二、任务（只动 §4.6 + 新增 §4.7 + main.pdf）**
> 1. **§4.6 进度句**：改成实测值（iteration / tok/s / loss / 0 NaN / `as of <日期>`），
>    同步 `tab:prod-budget` 的 Status（`30.7k done` → `Xk done`）与 wall-clock 估算
>    （用实测 tok/s 重算 `700k×4{,}194{,}304 / tok_s`，别照抄 56 d）。
>    **取数必须落盘可查**：`.29` 训练日志（`tail /tmp/baize_xmodel25_decay_v2_train.log`
>    或 `/proc/<pid>/fd/1`）+ `nvidia-smi`；**把实际执行的命令原样贴进 MEMORY**。
>    注意：主训练跑在 **.29**、watcher 在 **.12**，判活必须 `ssh 10.239.2.29` 后再查（老坑）。
> 2. **新增 §4.7 `\subsection{Checkpoint Scaling on General Benchmarks}\label{sec:ckpt-scaling}`**
>    （位置：§4.6 之后、§4.8 长上下文之前）：
>    - 口径：8 个 zero-shot 集（ARC-Challenge / ARC-Easy / BoolQ / HellaSwag / OpenBookQA /
>      PIQA / SciQ / Winogrande），`limit=100`，llama.cpp F16 GGUF CPU 推理（与线上一致）；
>    - **一张 booktabs 表**：`iter`（抽 6 行：10k/30k/50k/80k/110k/150k）× `已训 token`
>      （iter×4,194,304）× `Avg(harness)`；**不要 15 行塞满**；
>    - 正文 2–3 句：51.50%(10k) → 58.00%(110k/130k 峰值) → 57.12%(150k)；**必须写明**
>      `limit=100` 的抽样波动（acc_stderr ≈ ±4.5%）与"这是 harness 均值口径、非官方全量"；
>      160k–200k 尚在评（写清 `pending`，别写成结果）；
>    - 可选图：本模板**只有 tikz，没有 pgfplots**，要画就用纯 `\draw` 折线；画不好就只留表，
>      **不要为了图牺牲编译**。
> 3. **编译并提交 PDF**：`cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027 && latexmk -pdf -interaction=nonstopmode main.tex`
>    → **必须 0 error**（无 latexmk 则 `pdflatex main && bibtex main && pdflatex main && pdflatex main`），
>    然后 `git add main.pdf`。本机确实没有 LaTeX 时记 `PAPER_SKIP(no latexmk)`、只交 .tex。
>
> **三、数据来源（唯一可信，按优先级）**
> 1. `doc/BaiZe-ISEDA2027/reports/report_pretrain_llamacpp_scaling_zh.html`（15 ckpt 汇总表）；
> 2. 底层结果：`.29:nemo_experiments/baize2b/lm_eval_results/gguf_iter_*_fixed_8set/`；
> 3. **若 1 与 2 冲突 → 以 2 为准**，并在 MEMORY 记一行差异（我们要的是可复核，不是好看）。
>
> **四、护栏**
> - 只改 `ISEDA2027/4_llm_pretrain.tex` 与 `main.pdf`；**不碰** abstract / intro / 2_related_work /
>   3_architecture / 5_llm_posttrain / 9_conclusion / 参考文献；不碰其它线（designflow/harness/...）的文件。
> - 数字**不许估、不许外推**；取不到就写 `\todo{...}` 并在 MEMORY 标 `BLOCKED: <原因>`。
> - 收尾：`EXPERIMENTS_PRETRAIN_2B.md` 加一节记录（iter/表格数据/命令/编译结果），
>   MEMORY 首行写 `paper: ISEDA2027 §4.6 refreshed (iter=X) + §4.7 scaling table (6 rows) added, pdf=Yp, ERR=0`。
> - 本轮**不要**顺带做其它评测/运维令；做完这一件就回到训练监控（`WAITING: 1`）。
> 📦 §运维令·2026-11-08 15:3x（全量eval均值37.40%异常调查）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-09」节；**结论**：✅ 报告report_pretrain_eval_avg7_anomaly_zh.html(50KB)已交付,结论A(口径差异):stale results.json缺piqa致低估,补全后Avg7=55.96%与历史56.71%仅差-0.75pp。需要时再读。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

> 📦 §运维令·2026-11-07 15:2x（全量eval提速）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-09」节；**结论**：✅ 报告report_pretrain_cpu_eval_speedup_zh.html(17KB)已交付,llama.cpp 7×提速已用于万整数ckpt评测。需要时再读。


> 📦 §运维令·2026-11-07 09:1x（11w 检查点 8 集评测：去 `--limit 100` 改全量 + 扫线程/batch）**✅ 已交付 #1570**；§2026-10-30 22:2x（1M 长上下文 + 95% 大海捞针报告，`report_pretrain_1m_needle_zh.html` 33.7KB）**✅ 已交付 #983** → 两者原文归档 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。**结论**：① 探测矩阵 8/8 完成，**16 线程饱和（SSM 顺序扫描不可并行）、80 线程 bs1 反变慢、80×bs2 最优 1.36x** → `report_pretrain_cpu_eval_thread_scaling_zh.html`；② 全量 eval 已启动（16 线程 bs1 无 limit）。需要时再读。




## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

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


> 📦 §运维令 2026-11-04 22:1x（llama.cpp 调试每环节落盘 + 清理残留）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ A-E 检查点全有结论(A/B/D=PASS, C=FAIL dt-clamp 影响小 1/64 head), 残留已清(llama-server 11→0, GGUF 34G→13G), 根因已定位。需要时再读。



> 📦 §运维令 2026-11-04 14:0x（定位 llama.cpp 映射 bug + 修复 + PR）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ 根因=GGUF converter 全权重逐张量对照发现混合架构权重错位→级联放大 3.6 nats; Mamba2 层 A/B/D PASS; 修复后 logits Δmax=0.006; PR #31703 已提交 https://github.com/ggml-org/llama.cpp/pull/31703; dt-clamp follow-up 待单独 PR。需要时再读。


> 📦 §运维令 2026-11-04 13:2x（logits 逐 token 对齐定案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ 1-token 即偏 3.6 nats，定案=映射/计算错误（非精度累积），llamacpp.txt §6+§7 已更新，commit eca8b7f49。需要时再读。

> 📦 §运维令 2026-11-04 09:3x（llama.cpp 提速 pilot）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第五批」节；**结论**：✅ llh 打分打通、5/5 eval 完成（10K/30K 有效 Avg=50.00%/50.25%；20K/40K/50K 因权重 NaN 无效）；llama.cpp 精度不可用，保留 HF float32。需要时再读。

> 📦 §运维令 2026-10-29 14:1x（整理并提交 baize-llm 独立仓库）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：✅ commit e1c6be4 pushed to origin/master，28 files（README 19.6KB + configs/9 + scripts/18 + docs/2 + .gitignore），symlink 已删除+纳入 .gitignore，ls-remote 匹配。需要时再读。

> 📦 §运维令 2026-11-02 11:1x（CPU 评测 5 ckpt 8 集）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-05 第六批」节；**结论**：✅ 5/5 CPU HF float32 eval 完成, 报告 report_pretrain_cpu_eval_8sets_zh.html(44KB)已交付, 被 11-05 llama.cpp 修复管线取代。需要时再读。


> 📦 §运维令 2026-10-28 17:0x（预训练项目目录定位）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-11-04 第四批」节；**结论**：✅ 脚本&文档落 baize-llm/baize-llm，commit e1c6be4 pushed 28 files；启动口径 `bash .../baize-llm/scripts/train.sh <stage>` 仍有效。需要时再读。

> 📦 §运维令 2026-10-28 11:5x（blend 逻辑中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：报告已交付 `reports/report_pretrain_blend_logic_zh.html`（11KB, commit aa6d3eddf），澄清训练时不会串行出不同源（索引层交错）。需要时再读。

> 📦 §运维令 2026-10-28 10:0x（预训练计划定稿）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：计划已定稿并执行，GBS=256/2.94T/700k运行中，pre-blend完成/nw=8恢复/613K，Decay后置待data线。需要时再读。

> 📦 §运维令 2026-10-28 09:3x（锁定 613K 配置 + spawn 调优）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：613K 配方已冻结（16K/CP1/DP16/FP8/graph-OFF），根因=数据加载串行化(nw=0)，spawn 路径被 10:0x pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 15:2x（cimi MCP web search 已配好）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：MCP 工具就绪（cimi_search/cimi_fetch/vqa/text_to_image），授权永久有效。需要时再读。

> 📦 §运维令 2026-10-27 13:1x（杀掉 S1 + spawn smoke）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：S1 已杀，spawn 方案被 2026-10-28 10:0x pre-blend 取代。需要时再读。
> 📦 §运维令 2026-10-27 10:4x（不放弃：spawn 验证 + web 调研）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：spawn 被 pre-blend 取代；web 调研授权仍有效（见 15:2x）。需要时再读。
> 📦 §运维提示 2026-10-27 09:2x（DataLoader OOM fork-COW 根因 + spawn 方案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：fork-COW 是 RSS 累积根因，spawn 方案被 pre-blend 取代。需要时再读。

> 📦 §运维提示 2026-10-27 08:4x（内存使用率>95%触发告警）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：内存纪律已纳入日常监控，调试时盯内存+swap，逼近95%先降载。需要时再读。

> 📦 §运维令 2026-10-26 22:0x（S1 吞吐对齐 613,992：归因 + 方案 A/B/C）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#798 归因=gbs128 固定开销摊薄不足；吞吐目标 ≥600K 由后续 10:4x/13:1x 令推进（spawn 验证中）。参数口径 2.220B 仍有效。需要时再读。


> 📦 §运维令 2026-10-26 21:3x（RoPE θ 未生效：评估 + 方案 + 重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：θ=1e6 实现路径(ii) `--rotary-base` CLI + recipe 透传，commit ae3a093，三重验证 PASS；#799 运行时确认 θ=1e6 + 0崩；rank15 崩因=DDP DETAIL wrapper（非θ）；--dir 修正已落地。**仍有效红线**：check_rope.py PASS 需 ckpt（待 S1 重启）；lr-decay-shape exponential Decay 前验证。需要时再读。


> 📦 §运维令 2026-10-26 19:2x（预训练正式落地并开跑）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md「归档 2026-10-31」节；**结论**：全10步已完成，S1运行中(iter30660/700k,loss2.151,~598K tok/s)，TB6006常驻，RoPE PASS，Decay阻塞待data线。需要时再读。

> 📦 §运维令 15:3x（预训练构想报告 + ETA）**已完成**（#794：`report_pretrain_baize2b_pretrain_plan_zh.html` 22.5KB；§五执行口径已补）→ 原文归档 run/ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 14:3x（补写 #792 双机实测进吞吐报告）**已完成**（#793：报告 14,208→20,888B）→ 原文同上归档。
> 📦 §运维令 13:2x（FP8 真实数据 16K/32K 实测）**已完成**（#792：16K=613,992 / 32K CP2=351,526）→ 原文同上归档。
> 📦 §运维令 11:1x（双机 16 卡调优 seq16K/32K）**已完成**（#791 8卡首跑 + #792 双机实测覆盖）→ 原文同上归档。
> 📦 §运维令 09:1x（优化 16K/32K 吞吐至 600K+）**已完成**（#791 8卡 + #792 双机 16K=613,992 ≥600K）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 08:2x（写最近工作报告 · 中文 HTML）**已完成**（#790，report_pretrain_recent_work_zh.html 20KB）→ 原文同上归档。
> 📦 §运维令 2026-10-25 23:0x（通宵攻坚：tokens/microbatch 悬崖）**已完成**（#784–#789：真因=CUDA Graph 顶格停滞·关 graph 修复·16K 双机 613,992 达标；根因报告 + seqlen rev3）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 2026-10-25 20:2x（seq 掉速排查初版）已并入 23:0x 通宵令 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-25 17:5x（seq×tok/step 16卡网格）已完成（cfg1-4 OK）→ ARCHIVE_OPERATOR_PRETRAIN.md；注意「seq≥8192 崩 5x」已被 cfg0a 证伪。需要时再读。
> 📦 §运维令 2026-10-25 07:4x（双机 16 卡吞吐报告）已完成（#770-#776）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-24 23:5x（双机调通→吞吐优化）已完成（606,300 tok/s）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维指令 2026-10-24 16:0x（305K 最佳实践+longctx 报告）已完成 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

> 📦 §2026-10-16:4x（#548 误判更正）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#548 误判根因=NFS 旧日志，判活规则已修正。需要时再读。

> 📦 §2026-10-16:2x（P0 resume + 长期授权）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 resume 闭环，长期授权训练挂了自行重启。需要时再读。


> 📦 §2026-10-17 两块（P0 中继抢修 / `_orig_mod` 崩溃修复）均已闭合 → 原文已在 `daily-memories/2026-10-17.md`；结论：中继 PID2706247 健康（RUN_ID118-122 exit=0）；`_orig_mod` 修复验证通过，断点续跑至 6890/19980 无崩。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）
> 📦 已归档（R3配比 / LaTeX / R2收官 / T3）→ `ARCHIVE_OPERATOR_PRETRAIN.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）原文搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `pretrain 归档: …` 前缀。
> 本轮动作：本任务书现 ≈40KB（已过 40KB 红线）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


## ⚠️ git 同步规则（必读，2026-10-01 新增，每次唤醒都要走）

