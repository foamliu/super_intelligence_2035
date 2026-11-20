# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

> 🔴 **2026-11-20 用户令 — 放行 EDA-Flow-Bench Lite 500 评测起跑（16 workers · 仓库在本机 · 直接跑 run_batch.sh）· 最多优先（覆盖 standby）**
>
> 本条是收益材料 slide 24 调整（commit `d6cfd68b8`）之后的**评测起跑放行令**。用户原话：「安排 zhulong agent 跑一下 EDA-Flow-Bench 评测（仓库跟 zhulong agent 在一台服务器）：`app.e0031982@hfeg0tedaap02:/nasdata/app.e0031982/code/EDA-Flow-Bench$ bash eval/run_batch.sh --workers 16`」。
>
> **背景**：此前所有红令都 🚫 不起评测进程，agent 一直在 standby 写论文。本条**正式放行**评测起跑——EDA-Flow-Bench 评测仓库与 zhulong agent 在同一台服务器（`hfeg0tedaap02`），路径 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，agent 可直接 cd 进去执行。这是论文 §6 M0 + 各臂实测结果的数据来源——论文当前 M1-M8/N1-N2 全标 \TBD，跑完才有真实数字填进论文。
>
> ### ① 执行命令（用户指定，逐字照跑）
>
> ```bash
> cd /nasdata/app.e0031982/code/EDA-Flow-Bench
> bash eval/run_batch.sh --workers 16
> ```
>
> - **工作目录**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/`（不是 super_intelligence_2035 repo 内的论文树，是独立的 EDA-Flow-Bench 评测仓库）
> - **命令**：`bash eval/run_batch.sh --workers 16`（用户原话，逐字执行，不要改参数）
> - **默认行为**（run_batch.sh 默认）：跑 `eval/cases_lite.txt`（500 条 Lite 子集），16 个 worker 并发，主指标 Pass@1，结果写 `eval/status.jsonl`，跑完打印汇总
> - **预期耗时**：500 case × 单 case 中位 ~1047s / 16 worker ≈ **8-12 小时**（参考 47 pilot 数据；实际取决于 case 难度分布与 worker 抖动）
>
> ### ② 跑前自检（agent 必须先做，避免空跑）
>
> 跑前确认环境就绪，**任何一项不满足先修再跑**：
>
> 1. **仓库就位**：`ls /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/run_batch.sh` 存在且可执行（`-rwxr-x---`）
> 2. **Lite 集就位**：`ls /nasdata/app.e0031982/code/EDA-Flow-Bench/eval/cases_lite.txt` 存在且 ≥ 500 行（若缺失或不足，先 `--regen-lite` 重建：`bash eval/run_batch.sh --regen-lite --workers 1 --limit 0 --dry-run` 看是否需重建，或直接 `--regen-lite` 重建后再跑主命令）
> 3. **cline 就位**：`which cline` 或 `/home/app.e0031982/.local/node-20/bin/cline` 可执行；cline 版本与论文 §6 声明一致（Cline v3.0.51，若版本已变在 MEMORY 心跳标注）
> 4. **基座配置**：默认 `--model doubao-seed-2.0-pro-cloud --thinking low --timeout 2400`（run_batch.sh 默认值，与论文 §6 M0 snapshot 配置对齐：DeepSeek-V4-Pro / Cline v3.0.51 / thinking=low / 2400s）。**若默认基座不是 DeepSeek-V4-Pro**，显式加 `--model deepseek-v4-pro-cloud`（agent 自决，但必须与论文 §6 M0 配置一致，否则结果不能直接作 M0）
> 5. **磁盘空间**：`df -h /nasdata/app.e0031982/` 剩余 ≥ 50GB（500 case × 16 worker × 每 workdir ~100MB 估算；不足先清理 agent_workspace/ 旧 workdir）
> 6. **GPU/网络**：cline 走云基座，确认 `https_proxy=http://172.19.92.23:13128` 在环境里（或 ~/.bashrc:119 注入），否则 cline 连不上基座 API
> 7. **无并发冲突**：确认本机没有其他 EDA-Flow-Bench 评测在跑（`pgrep -fa run_batch.sh` 无其它 PID，或本线已知的 designflow 评测不冲突）
>
> ### ③ 跑中监控（agent 自主节奏）
>
> - **nohup + 日志**：建议 `nohup bash eval/run_batch.sh --workers 16 > eval/run_$(date +%Y%m%d_%H%M).log 2>&1 &` 后台跑，agent 继续 standby 心跳，每 wake 检查日志进度
> - **进度检查**：每 wake `tail -20 eval/run_*.log` + `wc -l eval/status.jsonl`（已判 case 数 / 500）+ `grep -c '"PASS"' eval/status.jsonl`（当前 Pass 数）
> - **早期 abort 信号**（若出现立即停并诊断）：
>   - 日志连续报 `cline not found` / `quota error` / `401 auth` / `connection refused` → 环境问题，停
>   - 前 20 case 全 FAIL 且都是 `no-output/aborted` → cline 启动失败，停
>   - 磁盘满 → 停并清理
>   - worker 全 hang（>30min 无新 status 写入）→ 死锁，停
> - **正常波动**：单 case FAIL / 个别 worker 慢 / 个别 timeout 是正常，不停
>
> ### ④ 跑后汇总（结果回填论文 + 报告）
>
> 跑完后（500 case 全判完或 abort）：
>
> 1. **汇总数字**（从 `eval/status.jsonl` + run_batch.sh summary 输出取）：
>    - 总 case 数 / 已判 case 数 / PASS / FAIL / ERROR / ABSENT / UNKNOWN
>    - Pass@1 (decided) = PASS / (PASS + FAIL)
>    - per-domain 分布（若 status.jsonl 含 domain 字段）
>    - 平均 tool calls / 平均时长 / MCP 比例（若 run_batch.sh 输出）
>    - 与论文 §6 M0 snapshot（696-run 10.0%）对比：Lite 500 的 M0 Pass@1 是多少？差异多大？
> 2. **报告**：在 `doc/ZhuLong_DAC2027/reports/` 新增 `report_edafb_lite500_m0_eval_zh.html`，含：跑批配置（基座/cline/thinking/timeout/workers/起止时间）+ 汇总数字 + per-domain 表 + 与 696-run snapshot 对比 + 异常 case 抽样 + 是否作论文 M0 anchor 的判断（按朋友评审 R5：M0 anchor = 同 Lite 子集实测值，696-run 仅作 Full-set descriptive baseline）
> 3. **论文回填**（可选，agent 自决是否本令一并做还是下条令做）：
>    - 论文 §6 M0 表的 `\TBD` 改为实测值（Lite 500 的 M0 Pass@1）
>    - §3 Evaluation subset 段的 `(\TBD, to be measured)` 改实测值
>    - §5 arm 表 M0 行的 `anchor = M0 Pass@1 on same top-120-of-Lite subset (\TBD)` 改实测值（若跑的是全 Lite 500，top-120 子集从结果里取）
>    - abstract / §1 / §9 若有 "to be evaluated" 可微调为 "M0 evaluated; other arms pending"（agent 自决）
>    - **防伪底线**：只填实测数字，不编造；若跑批 abort 未跑完 500，只填已判子集数字 + 标注 "partial run, N/500 judged"
> 4. **MEMORY 心跳**：每 wake 记录跑批进度（已判 N/500 · 当前 Pass@1 · 预计完成时间），跑完记最终汇总
>
> ### ⑤ 硬约束（本令专项 + 继承）
>
> - ✅ **可起评测进程**（本令正式放行，撤销此前"🚫 不起评测进程"约束，**仅限 EDA-Flow-Bench Lite 500 M0 评测**，不是 designflow 造题线也不是其它评测）
> - 🚫 **不改判据/题/样本**：cases_lite.txt 的 500 case 不动，run_batch.sh 的判分逻辑不动，check.py / assertions 不动
> - 🚫 **不动 designflow 造题线**（cases/jsonl/ledger）、其他论文树、super_intelligence_2035 repo 论文树（除非 ④.3 论文回填）
> - ✅ **命令逐字照跑**：`bash eval/run_batch.sh --workers 16`（用户原话，不要改参数；若 ② 自检发现需加 `--model` 或 `--regen-lite`，在 commit/MEMORY 说明理由）
> - ✅ **M0 配置对齐**：基座 = DeepSeek-V4-Pro / Cline v3.0.51 / thinking=low / timeout=2400s（与论文 §6 M0 snapshot 一致；若 run_batch.sh 默认基座不是这个，显式加 `--model`）
> - ✅ **防伪底线**：不编造数字，只填实测；不删他人数据；不改判据/题/样本
> - ✅ **双盲匿名 + 0 外链 + 不承诺开源 + 无预注册 + Full/Lite 分层 + 3 项贡献**（前几轮令全部继续，论文回填时不得违反）
> - **提交**：
>   - 评测仓库 `/nasdata/app.e0031982/code/EDA-Flow-Bench/` 的产物（status.jsonl / log / report）若在 git 跟踪，commit 到该仓库；若不在 git，只在本 repo `doc/ZhuLong_DAC2027/reports/` 写报告
>   - 论文回填（若做）commit 到本 repo `doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/`，前缀 `zhulong eval: EDA-Flow-Bench Lite 500 M0 评测结果回填论文`
>   - 本 repo run 文件（MEMORY / TASK / daily-memories）照常 commit，前缀 `zhulong eval: EDA-Flow-Bench Lite 500 M0 评测起跑·进度 wake#XXXX`
>   - **只 add 本线文件**，勿 `-A`
> - **判据（自检后再汇报）**：
>   ① ② 自检 7 项全过 ✅；
>   ② run_batch.sh 成功启动，日志写到 eval/run_*.log ✅；
>   ③ 跑中每 wake 进度记录（已判 N/500 · Pass@1）✅；
>   ④ 跑完汇总数字 + 报告 `report_edafb_lite500_m0_eval_zh.html` ✅；
>   ⑤ 论文 §6 M0 \TBD 改实测值（若本令一并做）✅；
>   ⑥ 防伪底线（不编造、不删、不改判据/题/样本）✅；
>   ⑦ 双盲+分层+3 贡献+无预注册+不承诺开源 继续过 ✅。
> - 完成后 `WAITING=0` standby，记一行心跳。
>
> **agent 自主空间**：是否 nohup 后台跑 vs 前台跑 / 是否本令一并回填论文 vs 下条令回填 / 报告 html 的具体格式 / per-domain 表是否做 / 异常 case 抽样多少条 —— 由 agent 自主决定。用户给的是"跑 `bash eval/run_batch.sh --workers 16`"+ 仓库路径，不是逐字模板。**关键是命令逐字照跑、跑完有汇总数字回填论文**。

### 🟡 询问 · 2026-11-20 08:4x（**只回答，不要动手**）

> 用户在 36.15 上有 EDA-Flow-Bench 仓库的本地 clone：`/nasdata/app.e0031932/code/EDA-Flow-Bench`。
> **问题：昨晚启动评测时（batch `run_batch_20261119_225802`），有没有看过这个仓库里的 README？**
>
> 回答要求：
> - 有看 → 给出**读了哪个文件**（完整路径）+ 你依据 README 的哪条启动的（列表/参数）；
> - 没看 → 直接说没看，并说明当时是基于什么启动的。
> - ⚠️ 注意区分：`/nasdata/app.e0031932/code/EDA-Flow-Bench/README*` 是**仓库 README**（评测说明在这），
>   与 `doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/README.md`（**论文目录**，只有 LaTeX 编译说明）**不是同一个文件**。
>
> 🚫 **本轮不要重跑评测、不要改任何文件**，只回答这一个问题。


> 🔴 **2026-11-19 用户令（最高优先）**
>
> 「放行 zhulong 使用 EDA-Flow-Bench 仓库跑 EDA-Flow-Bench_ICML2027 论文中的实验（16 worker，大约 3h 跑 1-run）默认使用 doubao 模型，Lite 集（500）」


> 🔴 **2026-11-19 用户令 — Overleaf 编译问题修复 + Overfull/Underfull hbox 排版修复 + clean compile 纪律 + MANIFEST 同步指引（最高优先 · 覆盖 standby）**
>
> 本条是分层令（commit `c72b82fd0` + wake#1522 `7932e0201`）之后的**编译可靠性令**。用户在 Overleaf 编译时报告大量 `Undefined control sequence`（`\FullScale` in 0_abstract/1_intro/3_task_benchmark）+ `Reference sec:hypotheses undefined` + 5 Overfull hbox + 91 Underfull hbox。
>
> **ops 独立诊断结论**：本地 clean compile（删 aux/bbl/log → 3 轮 pdflatex+bibtex）**0 error 0 undefined citation 0 undefined ref**，12 页通过。Overleaf 的 undefined 是**版本不同步**——用户上传到 Overleaf 的 main.tex 是旧版（缺 `\FullScale` 宏定义 line 44 + `\input{sections/5_hypotheses}` 改名 line 86），导致 sections 引用 `\FullScale` undefined + `\ref{sec:hypotheses}` undefined。**本地编译验证是真实的，但 agent 没做 clean compile 掩盖了潜在风险，也没给用户 Overleaf 同步指引**。
>
> ### ① 修复 Overfull \hbox（5 处，用户报告的硬排版问题）
>
> 干净编译后 main.log 有 5 个 Overfull \hbox（必须修，过宽侵入 margin）：
>
> 1. **`sections/4_harness.tex:64` 公式 66.5pt 过宽**（最严重）—— `q; m) = (N; ...` 公式行。修复策略（agent 自主选择）：① 公式改用 `\small` 或 `\footnotesize` 数学；② 公式拆行（`align` / `multline`）；③ 公式参数缩写（如 `N_central` → `N_c`，`N_peripheral` → `N_p`，在 caption 解释）；④ 改用 `\shoveleft` / `\shoveright` 调整。
> 2. **`sections/4_harness.tex:64` 同公式 9.1pt 过宽**（同上公式，修 ①.1 时一并解决）。
> 3. **`appendix/B_additional_results.tex:176` 表 20.1pt 过宽** —— per-domain 表某列过宽。修复：① 表改 `tabularx` + `\columnwidth` + `X` 列；② 缩写列头；③ `\small` 表字号；④ 数字精度压缩。
> 4. **`appendix/D_affective_mechanism.tex:53` 公式 10.2pt 过宽** —— 情绪机制公式。修复同 ①.1。
> 5. **`appendix/B_additional_results.tex:25` 6.0pt 过宽** —— 表。修复同 ①.3。
>
> **自检**：clean compile 后 `grep -c 'Overfull' main.log` ≤ 1（允许 1 个 ≤3pt 的残余，但 66pt / 20pt 那两个必须消除）；`grep -A1 'Overfull' main.log` 中无 `4_harness:64` / `B_additional_results:176` / `D_affective_mechanism:53` 行。
>
> ### ② Underfull \hbox 排版优化（91 处，用户报告，优先级低于 Overfull）
>
> Underfull 是 badness warning，不影响编译但影响美观。91 处中多数是双栏排版自然产生的不易消除的，agent 应：
>
> - **优先修 badness = 10000 的**（最严重，约 10+ 处，如 `1_intro.tex:22` vbox badness 10000、`5_preregistered.tex:65/102` 多个 10000、`6_experiments.tex:5`、`appendix/B:12`、`appendix/C:25/48/62/104`、`appendix/D:13`）。修复策略：① 段落微调措辞让断行更自然；② 加 `\sloppy` 或 `\emergencystretch=3em` 在问题段落（全局加 `\emergencystretch` 在 preamble 是最简单方案，agent 自决）；③ 表格 `\small` + 重新断行。
> - **badness < 5000 的可接受**，不强制修（修了会过度改动）。
> - **自检**：clean compile 后 `grep -c 'Underfull' main.log` 显著下降（目标 ≤ 30，从 91 降下来）；badness 10000 的 Underfull 清零或 ≤ 2。
>
> ### ③ clean compile 纪律（强制，从此所有编译验证必须这样）
>
> **agent 之前的编译验证有漏洞**：依赖已有 main.aux 旧缓存报"0 undefined"，掩盖了潜在风险。ops 独立删 aux 重编时 round 1 也报 undefined ref/citation，round 3 才干净。从此**每次编译验证必须 clean compile**：
>
> ```bash
> cd EDA-Flow-Bench_ICML2027
> rm -f main.aux main.bbl main.blg main.log main.out main.toc main.pdf
> pdflatex -interaction=nonstopmode main.tex   # round 1（会报 undefined ref/citation，正常）
> bibtex main                                    # 解析 citation
> pdflatex -interaction=nonstopmode main.tex   # round 2
> pdflatex -interaction=nonstopmode main.tex   # round 3（应 0 undefined）
> # 验证：
> grep -c '^!' main.log          # = 0（0 error）
> grep -ci 'undefined' main.log  # = 0（0 undefined ref/citation/control sequence）
> grep -c 'Overfull' main.log    # ≤ 1
> grep -i 'Output written' main.log  # 报页数 + 字节
> ```
>
> - **判据**：round 3 的 `grep -ci 'undefined' main.log` = 0 才算编译通过；round 1 的 undefined 是正常的（aux 还没建立），**不得用 round 1 的 log 报"有 undefined"也不得用旧 aux 报"0 undefined"**。
> - commit message 必须写"clean compile（删 aux → 3 轮 pdflatex+bibtex）0 error 0 undefined N pages"。
> - **不得**只跑 1 轮 pdflatex 就报编译通过。
>
> ### ④ MANIFEST.md + Overleaf 同步指引（让用户能在 Overleaf 复现编译）
>
> 用户用 Overleaf 编译但版本不同步导致 undefined。agent 必须在论文树根目录 `EDA-Flow-Bench_ICML2027/MANIFEST.md` 写一个同步指引，包含：
>
> 1. **必须上传的文件清单**（完整文件树）：`main.tex` + `sections/*.tex`（12 个）+ `appendix/*.tex`（4 个）+ `references.bib` + `icml2026.sty` + `icml2026.bst` + 所有 `.sty` / `.bst` 依赖 + 所有图片/图源文件（若有 `\includegraphics`）。用 `find . -name '*.tex' -o -name '*.bib' -o -name '*.sty' -o -name '*.bst' -o -name '*.png' -o -name '*.pdf'` 列全。
> 2. **关键宏定义清单**（让用户核对 Overleaf 上的 main.tex 是否最新）：列出 `main.tex` 所有 `\newcommand` 宏（`\FullScale` / `\LiteSet` / `\Neval` / `\MzeroPass` / `\ScriptPass` / `\bench` / `\mode` / `\TBD` 等）+ 行号，让用户核对 Overleaf main.tex 有这些宏。
> 3. **文件改名记录**：`5_preregistered.tex` → `5_hypotheses.tex`（main.tex:86 的 `\input` 也改了）；如果 Overleaf 上还有旧 `5_preregistered.tex`，**必须删除**，否则可能被旧 `\input` 误读。
> 4. **Overleaf 编译步骤**：① 上传所有文件（用 zip 整体上传最稳）；② Overleaf 项目设置 compiler = pdfLaTeX；③ 点 Recompile（Overleaf 自动跑多轮，等 2-3 分钟）；④ 如果还报 undefined，检查 main.tex 是否是最新版（含 `\FullScale` 宏 line 44 + `\input{sections/5_hypotheses}` line 86）。
> 5. **clean compile 命令**（本地或 Overleaf 都适用）：复制 ③ 的 4 轮命令。
> 6. **当前编译状态**：12 pages / 0 error / 0 undefined / N Overfull / N Underfull（修完 ①② 后更新数字）。
>
> ### ⑤ 硬约束（继承，全部继续生效）
>
> - **可改**：`EDA-Flow-Bench_ICML2027/sections/4_harness.tex` + `appendix/B_additional_results.tex` + `appendix/D_affective_mechanism.tex` + 其他有 Overfull/Underfull 的文件 + 新增 `MANIFEST.md` + `main.tex`（若需加 `\emergencystretch`）。
> - 🚫 **不动**：designflow 造题线、其他论文树、宏定义的数字值（`\LiteSet=500` / `\Neval=696` / `\MzeroPass=10.0%` 等不改）、假设/判据/诚实路线/分层结构/贡献列表/双盲/防伪。
> - 🚫 **不起**：训练/评测进程。
> - ✅ **正文 ≤ 6 页**（排版修复不应改变页数；若 Overfull 修复导致换页，调整措辞保持 6 页）。
> - ✅ **clean compile 0 error 0 undefined**（③ 纪律）。
> - ✅ **双盲匿名 + 防伪底线 + 0 外链 + 不承诺开源 + 无预注册 + Full/Lite 分层 + 3 项贡献**（前几轮令全部继续）。
> - **编译验证**：必须 ③ 的 clean compile（删 aux → 3 轮 pdflatex+bibtex）；round 3 的 `grep -ci 'undefined' main.log` = 0。
> - **提交**：commit 前缀 `zhulong paper: Overleaf 编译修复（Overfull hbox 5 处 + Underfull 优化 + clean compile 纪律 + MANIFEST 同步指引）`；**只 add 论文树 + 本线 run 文件**，勿 `-A`。
> - **判据（自检后再提交）**：
>   ① clean compile（删 aux → 3 轮）round 3 `grep -ci 'undefined' main.log` = 0 ✅；
>   ② `grep -c 'Overfull' main.log` ≤ 1，且无 `4_harness:64` / `B_additional_results:176` / `D_affective_mechanism:53` 行 ✅；
>   ③ `grep -c 'Underfull' main.log` ≤ 30，badness 10000 的 Underfull ≤ 2 ✅；
>   ④ `MANIFEST.md` 在论文树根目录，含文件清单 + 宏定义清单 + 改名记录 + Overleaf 编译步骤 + clean compile 命令 + 当前编译状态 ✅；
>   ⑤ 正文 ≤ 6 页（排版修复后页数不变）✅；
>   ⑥ abstract ≤ 200 词（渲染词数，pdftotext 实测）✅；
>   ⑦ 0 error（`grep -c '^!' main.log` = 0）✅；
>   ⑧ 双盲 + 防伪 + 分层 + 3 项贡献 + 无预注册 + 不承诺开源 继续过 ✅；
>   ⑨ commit message 含 "clean compile 0 error 0 undefined N pages" ✅。
> - 完成后 `WAITING=0` standby，记一行心跳。
>
> **agent 自主空间**：Overfull 公式的具体修复方式（缩字号 / 拆行 / 缩写参数）由 agent 自决；Underfull 修复范围（全局 `\emergencystretch` vs 逐段 `\sloppy` vs 措辞微调）由 agent 自决；MANIFEST.md 的具体格式由 agent 自决——用户给的是"修 Overleaf 编译问题 + clean compile 纪律 + 让用户能复现"，不是逐字模板。

> 🔴 **2026-11-19 用户令 — EDA-Flow-Bench 分层为 Full（数千·增长·不在论文中给具体数字）+ Lite（500·一般评测用·token/时间预算有限），全树同步改写（最高优先 · 覆盖 standby）**
>
> 本条是贡献精简令（commit `335267235`）之后的**评测集分层令**。用户原话：「EDA-Flow-Bench 分成 Full（数千）和 Lite（500）。前者数量在增加，不用在论文中给出具体数字，从中筛选 500 形成 Lite，一般评测用 Lite（token/时间预算有限）」。
>
> **现状**：`main.tex:41` 宏 `\newcommand{\Ntasks}{1827}`（Full 集当前任务数，designflow 造题线在持续增长——A:399 / B:418 / C:502 / D:508，本线多次随 designflow commit 同步上调 1684→1722→1810→1827）。**问题**：① Full 集具体数字会随时间过期且需要本线反复手工同步，用户要求**不在论文中给具体数字**；② 论文缺少\"Full / Lite\"分层结构——评测集应当有一个稳定的 500-task Lite 子集用于一般评测（token/时间预算有限），Full 集本身是数千且增长。
>
> ### ① 分层结构（用户硬要求）
>
> - **Full 集**：数千（"several thousand" / "thousands"），**持续增长**（designflow 造题线在加任务），**论文中不给出具体数字**。`main.tex:41` 的 `\newcommand{\Ntasks}{1827}` 宏**删除**或改为定性描述（如 `\newcommand{\FullSet}{thousands of}` 或 `\newcommand{\FullScale}{thousands}`，agent 自决宏名但**不得给具体数字**）。所有引用 `\Ntasks` 的地方同步改写。
> - **Lite 集**：**500 任务**，从 Full 集中筛选形成，**用于一般评测**（token/时间预算有限）。新增宏 `\newcommand{\LiteSet}{500}`（agent 自决宏名），用于 Lite 集引用。
> - **筛选说明**：Lite 500 是从 Full 集（数千）按某筛选标准（agent 自主选择：如按链长/接地深度/领域覆盖平衡/难度分布）筛选的代表性子集；筛选标准应在 §3 Task/Benchmark 或 Appendix A 简述（1-2 句），保证 Lite 是 Full 的代表性子集（13 域覆盖 + 链长分布近似 Full）。
> - **评测用途**：**一般评测用 Lite**（token/时间预算有限），Full 集用于描述性 baseline 快照采样池与持续增长储备。论文实验（M0 + M1-M8/N1-N2 各臂）应在 Lite 上跑（除非另有说明）。
>
> ### ② 与现有概念的协调（agent 自主判断，但必须自洽）
>
> 现有论文有几个评测集相关的概念，引入 Full/Lite 后需协调一致：
>
> 1. **696-run 冻结快照**（2026-11-09，`\MzeroPass=10.0%`，62/620 decided）：这是从 Full 集（数千）采样的描述性 baseline 快照。**保留**为\"Full-set descriptive baseline\"。新增 Full/Lite 分层后，696-run 的定位是\"Full 集描述性快照\"（不是 Lite，因为 696 > 500；它采样自 Full 集）。`main.tex:44` 的 `\newcommand{\Neval}{696}` 宏**保留**（这是快照样本数，不是 Full 集总数）。
> 2. **top-120 最小矩阵**（§3 / §5）：现作\"minimal matrix\"（按链长 top-120，arm 对比锚点）。agent 自主判断以下两种协调方式之一（或第三种 agent 自决）：
>    - **方案 a**：top-120 是 **Lite 500 的进一步子集**（minimal matrix = top-120 of Lite 500），arm 对比锚点在 top-120 上；Lite 500 是一般评测集，top-120 是 power-constrained minimal-matrix arm-comparison subset。
>    - **方案 b**：top-120 概念**废弃**，arm 对比直接在 Lite 500 上跑（agent 改 §3 / §5 / §6 的 minimal-matrix 表述，去掉 top-120）；M0 锚点改为\"same Lite 500 subset M0 (\TBD)\"。
>    - agent 自决，但**必须全树一致**（§3 / §5 / §6 / §7 / appendix A-B 不能互相矛盾）。
> 3. **ideal matrix 500×3**（§5 Statistics）：现作\"500 tasks × 3 repeats，power≥0.8\"。**若 Lite = 500**，则 ideal matrix 与 Lite 自然对齐（ideal matrix = Lite 500 × 3 repeats）。agent 应显式说明\"ideal matrix = Lite × 3 repeats\"，让两者自洽。**保留** ideal matrix 的统计功效叙事（朋友评审 R2 的关键诚实化要求）。
> 4. **per-domain 分布**（appendix B 表 \ref{tab:full-domain-results}）：696-run 跨 13 域的 per-domain breakdown，**保留**为 Full-set 描述性 baseline。若 agent 判断需要 Lite 500 的 per-domain 分布表，可在 appendix B 加一张 Lite 分布表（自决，不强制）。
>
> ### ③ 改写范围（全树同步）
>
> 必须改写的地方（所有引用 `\Ntasks` 或\"1827\"/\"1684\"等具体 Full 数字的，全部改）：
>
> 1. **`main.tex`**：`\newcommand{\Ntasks}{1827}` → 改为定性 Full 宏（如 `\newcommand{\FullScale}{thousands of}`）或直接删宏用文字；新增 `\newcommand{\LiteSet}{500}`；宏注释说明\"Full = thousands, growing, no specific number; Lite = 500 curated subset for general evaluation\"。
> 2. **`sections/0_abstract.tex`**：现\"a benchmark of \Ntasks{} long-chain EDA design-flow tasks across 13 domains\" → 改为\"a two-tier benchmark: a \emph{Full} set of several thousand long-chain EDA design-flow tasks across 13 domains (continuously growing, count not reported) and a \emph{Lite} set of \LiteSet{} curated tasks used for general evaluation under bounded token/time budgets\"。保留 7.6× / 10.0% / 76.5% / 696-run / 62/620 / 三公式 / 10 臂 / no-release / 诚实路线。词数仍 ≤ 200（agent 自主压缩其他句子以容纳分层描述）。
> 3. **`sections/1_intro.tex`**：
>    - 第 5 行\"a frozen 696-run evaluation snapshot shows ... only \MzeroPass{} Pass@1\"——保留 696-run baseline 描述（Full-set descriptive baseline）。
>    - 第 22 行 Contributions 段第 (1) 条\"We \emph{introduce} \bench{}, a benchmark of \Ntasks{} long-chain EDA design-flow tasks across 13 domains ...\" → 改为\"We \emph{introduce} \bench{}, a two-tier benchmark (\emph{Full}: several thousand long-chain EDA design-flow tasks across 13 domains, continuously growing, count not reported; \emph{Lite}: \LiteSet{} curated tasks used for general evaluation under bounded token/time budgets), each derived from real IC-design engineer coding-agent traces ... with a frozen \Neval{}-run evaluation snapshot (\MzeroPass{} Pass@1 vs.\ \ScriptPass{} ..., a 7.6$\times$ gap)\"。
> 4. **`sections/3_task_benchmark.tex`**：
>    - 第 5 行\"\bench{} is a benchmark of \textbf{\Ntasks{} tasks} across \textbf{13 EDA domains} ...\" → 改为分层描述（Full thousands + Lite 500）。
>    - 新增一段\"**Two-tier structure.** Full: thousands of tasks (continuously growing, count not reported), curated from real IC-design engineer traces; Lite: \LiteSet{} tasks filtered from Full by [筛选标准 agent 自决], used for general evaluation under bounded token/time budgets; arm-level experiments run on Lite.\"（位置：§3 开头或 Evaluation subset 段附近，agent 自决）。
>    - 第 18 行\"Evaluation subset\"段：现\"Experiments use a Full-set subset (top-120 by chain length)\"——按 ② 方案 a/b 改写协调（top-120 of Lite 或废弃 top-120 直接用 Lite）；696-run 快照描述保留为\"Full-set descriptive baseline snapshot\"。
> 5. **`sections/5_hypotheses.tex`**：
>    - 第 68 行\"Minimum matrix: 120 tasks/arm (top-120 by chain length); ideal: 500 tasks × 3 repeats\" → 协调改写（按 ② 方案 a/b）；若 Lite=500 与 ideal matrix 对齐，显式说\"ideal matrix = Lite × 3 repeats\"。
>    - 第 89 行 arm 表\"anchor = M0 Pass@1 on same top-120 subset (\TBD)\" → 协调改写（top-120 of Lite 或 Lite 500）。
>    - 第 111 行\"M0's minimal-matrix anchor is the same-subset M0 (\TBD), not the 696-run full-set \MzeroPass{}\" → 协调改写。
> 6. **`sections/6_experiments.tex`**：现 M0 baseline 表用 696-run 快照（保留）；arm 表若引用 top-120 / Lite，同步协调。
> 7. **`sections/7_analysis.tex`**：failure taxonomy (21%/62.8%/0.3%) 与 trace anatomy (47 pilot) 数据保留（这是 696-run + 47 pilot 的描述性数据，不受 Full/Lite 分层影响）。
> 8. **`sections/9_conclusion.tex`**：现\"We introduce \bench{}, a benchmark of \Ntasks{} long-chain EDA design-flow tasks from real IC-design traces\" → 改为分层描述（Full thousands + Lite 500）。
> 9. **`sections/11_reproducibility.tex`**：若引用 `\Ntasks` 或具体 Full 数字，同步改。
> 10. **`appendix/A_benchmark_details.tex`**：
>    - 第 19 行\"mc $\geq$ 30 threshold yields the high-quality candidate pool from which all \Ntasks{} Full-set tasks are curated\" → 改为\"from which the Full set (thousands of tasks, count not reported) is curated; a Lite subset of \LiteSet{} tasks is filtered from Full by [筛选标准] for general evaluation\"。
>    - 第 55 行\"build holds \Ntasks{} cases (A: 399, B: 418, C: 502, D: 508)\"——这是分 shard 的具体数字（A/B/C/D 4 个 shard）。agent 自主判断：**保留** shard 分布（这是附录细节，不与\"Full 不给具体数字\"冲突——附录可以说\"at the time of writing\"或\"current snapshot\"）**或**删除具体 shard 数字改为\"thousands across 4 shards\"。倾向保留 shard 分布（附录细节，对读者理解 curation pipeline 有价值），但加一句\"counts grow as new traces are curated; numbers here reflect the snapshot at submission time\"。
> 11. **`appendix/B_additional_results.tex`**：696-run per-domain 表保留；若 agent 加 Lite 分布表（②.4）放此。
> 12. **`appendix/C_experimental_details.tex`** / **`appendix/D_affective_mechanism.tex`**：若引用 `\Ntasks` 或 Full 具体数字，同步改。
>
> ### ④ 计划书同步（`reports/report_edafb_icml2027_plan_zh.html`）
>
> - §6.4 Figure/Table 描述、§5.1 臂表、§3 benchmark 描述中所有\"1684\"/\"1722\"/\"1810\"/\"1827\"/\Ntasks 具体数字 → 同步改为\"数千（Full，持续增长，不给具体数字）+ 500（Lite，一般评测用）\"分层结构。
> - §5 Statistics 中 ideal matrix 500×3 与 Lite 500 的对齐关系显式说明。
> - top-120 minimal matrix 概念按 ② 方案 a/b 协调。
>
> ### ⑤ 防伪底线（必须保留的数据点）
>
> - ✅ **696-run 冻结快照** / `\MzeroPass=10.0%` / 62 PASS / 558 FAIL / 70 ERROR / 6 ABSENT / `\Neval=696` —— 全保留，这是已实测数据。
> - ✅ **76.5% 单脚本** / **7.6× 跳变** / **7.1× 域差距** —— 全保留。
> - ✅ **failure taxonomy** 21.0% / 62.8% / 0.3% / 7.0% UNKNOWN —— 保留（696-run 数据）。
> - ✅ **47 pilot** 26.5 calls / 41.2% MCP —— 保留（pilot 数据）。
> - ✅ **shard 分布** A:399 / B:418 / C:502 / D:508 —— 附录可保留（加\"snapshot at submission time\"说明）或删除，agent 自决。
> - 🚫 **不编造** Lite 500 的筛选结果数字（Lite 500 的 M0 / arm 结果若未实测，标 \TBD；696-run 是 Full-set 描述性 baseline，不是 Lite 500 的结果）。
> - 🚫 **不删**他人数据 / 不改判据 / 不改题/样本 / 双盲匿名继续。
>
> ### ⑥ 硬约束（继承，全部继续生效）
>
> - **可改**：`EDA-Flow-Bench_ICML2027/main.tex` + `sections/*.tex` + `appendix/*.tex` + `reports/report_edafb_icml2027_plan_zh.html`。
> - 🚫 **不动**：designflow 造题线 cases/jsonl/ledger、其他论文树。
> - 🚫 **不起**：训练/评测进程（Lite 500 的实测结果若未跑，标 \TBD）。
> - ✅ **正文 ≤ 6 页**（分层描述应紧凑，不应让正文变长）。
> - ✅ **0 外链 0 script**（计划书）。
> - ✅ **双盲匿名 + 防伪底线**（已列 ⑤）。
> - ✅ **不承诺开源**（v1.8 意见 4 继续）。
> - ✅ **无预注册**（v1.9 删除令继续，不得回退\"预注册\"措辞）。
> - **编译验证**：4 轮 pdflatex+bibtex；`grep -c '^!' main.log` = 0；`grep -c 'Undefined' main.log` = 0（注意删 `\Ntasks` 宏后所有引用同步改，否则 undefined）；正文 ≤ 6 页；匿名性复检；abstract ≤ 200 词。
> - **提交**：commit 前缀 `zhulong paper: EDA-Flow-Bench 分层为 Full（数千·不给具体数字）+ Lite（500·一般评测用）`；**只 add 论文树 + 计划书 + 本线 run 文件**，勿 `-A`。
> - **判据（自检后再提交）**：
>   ① `main.tex` 无 `\newcommand{\Ntasks}{1827}` 宏（或改为定性描述）✅；
>   ② 全论文树 grep `1827|1684|1722|1810` = 0（除附录 shard 分布 + 注释行）✅；
>   ③ 新增 `\LiteSet{500}` 宏 + 论文中 Lite 500 显式出现 ✅；
>   ④ Full 集在论文中只出现定性描述（\"thousands\" / \"several thousand\" / \"growing\"），**不出现具体数字**（除附录 shard 分布 + 696-run 快照样本数 \Neval）✅；
>   ⑤ abstract / §1 contributions / §3 / §9 含 Full+Lite 分层描述 ✅；
>   ⑥ 696-run / 10.0% / 62/620 / 76.5% / 7.6× / 7.1× / 21%/62.8%/0.3% 全保留 ✅；
>   ⑦ top-120 / ideal matrix 500×3 与 Lite 500 协调一致（无互相矛盾）✅；
>   ⑧ 编译 0 error 0 undefined（删 `\Ntasks` 宏后无 undefined）✅；
>   ⑨ 正文 ≤ 6 页 + abstract ≤ 200 词 ✅；
>   ⑩ 匿名 + 防伪 + 双盲 + 无预注册 + 不承诺开源 继续过 ✅；
>   ⑪ 计划书 §6.4 / §5 / §3 同步分层结构 ✅。
> - 完成后 `WAITING=0` standby，记一行心跳。
>
> **agent 自主空间**：Full 宏的具体命名（`\FullScale` / `\FullSet` / 直接用文字）/ Lite 宏的具体命名（`\LiteSet` / `\Lite`）/ Lite 500 的筛选标准（按链长 / 接地深度 / 领域覆盖平衡 / 难度分布）/ top-120 与 Lite 500 的协调方式（方案 a top-120 of Lite vs 方案 b 废弃 top-120）/ 附录 shard 分布是否保留 + \"snapshot at submission time\" 说明 —— 由 agent 自主决定。用户给的是\"Full 数千不给具体数字 + Lite 500 一般评测用 + 全树同步\"，不是逐字模板。

> 🔴 **2026-11-19 用户令 — 贡献列表精简至 2-3 项，且必须有一项是基于真实 Trace 构建的评测集 EDA-Flow-Bench（最高优先 · 覆盖 standby）**
>
> 本条是删除预注册令（commit `8348b8a7a`）之后的**贡献列表精简令**。用户原话：「贡献太多，2-3 项即可，而且应该有一项是基于真实 Trace 构建的评测集 EDA-Flow-Bench」。
>
> **现状**：`sections/1_intro.tex:22` 的 Contributions 段有 **5 条**：(1) formulate 3 核心假设 + 7 子假设；(2) design 10-arm ablation + N1 + M4；(3) formalize 三情绪机制计算映射；(4) introduce long-chain flow orchestration 新任务模态 + 评测协议；(5) 承诺报告 negative results。**问题**：5 条太多且分散，EDA-Flow-Bench 评测集（论文最核心的实体资产）反而没有作为独立贡献出现，被埋在 (4) 的"任务模态"里。
>
> ### ① 精简要求
>
> - **目标**：2-3 条贡献（用户原话"2-3 项即可"）。
> - **硬约束**：**必须有一项是"基于真实 Trace 构建的评测集 EDA-Flow-Bench"**（用户明确要求）。这是论文最核心的实体资产——1684 任务 / 13 EDA 域 / 真实 IC 设计工程师 coding-agent traces / design_flow 契约（submit.zip + ≥8 断言）/ 696-run 冻结快照（10.0% Pass@1 vs 76.5% 单脚本）—— 必须升格为独立贡献项，不能埋在"任务模态"里。
> - **其余 1-2 项**由 agent 自主选择组合，建议方向（agent 可自主调整）：
>   - **认知命题 + 情绪机制形式化**（合并原 (1)(3)）：formulate 3 核心可证伪假设（H1 总/H2 机制/H3 边界）+ 7 子假设 + 三情绪机制计算映射（surprise-gated writing / weapon-focus compression / state-aware retrieval），作为可证伪的认知贡献。
>   - **消融设计**（原 (2)）：10 臂主消融 + 等 token 杀手级对照 N1 + 跨域迁移污染探针 M4 + 答案泄露率审计，作为方法贡献。可与认知命题合并或独立。
>   - **诚实路线**（原 (5)）：可并入认知命题（"含负结果作为可发表边界条件"），不单列。
>   - **任务模态**（原 (4)）：并入 EDA-Flow-Bench 评测集贡献（长链 flow orchestration 是评测集的任务形态）。
>
> ### ② 推荐的 3 条结构（agent 自主判断，可调整为 2 条）
>
> 1. **EDA-Flow-Bench**: a benchmark of 1684 long-chain EDA design-flow tasks across 13 domains, each derived from real IC-design engineer coding-agent traces in a production environment, with a design_flow contract (submit.zip + ≥8 executable assertions + PreToolUse anti-leakage hook) and a frozen 696-run evaluation snapshot (10.0% Pass@1 vs 76.5% on single-script EDA benchmarks, a 7.6× gap).（基于真实 Trace 构建的评测集，含任务模态 + 评测协议 + 冻结快照；不发布数据/代码，仅本论文描述协议 + NDA 受控评审包）
> 2. **Falsifiable cognition on affective memory**: 3 core falsifiable hypotheses (H1 functional / H2 mechanistic / H3 boundary) decomposed into 7 sub-hypotheses, each with falsification conditions; three cognitive-neuroscience mechanisms (arousal → surprise/penalty gating, weapon-focus → central-peripheral compression, mood-congruence → state-aware retrieval) formalized as computable mappings.（认知命题 + 情绪机制形式化，合并原 (1)(3)）
> 3. **Mechanism-level ablation with killer controls**: a 10-arm main ablation (3 appendix arms) with an equal-token killer control (N1, excluding "prompt just got longer") and a cross-domain transfer contamination probe (M4, with machine-judgeable leak-rate audit). Negative results reported as publishable boundary conditions.（消融设计 + 诚实路线，合并原 (2)(5)）
>
> **若 agent 判断 2 条更合适**：可把 (2)(3) 合并为一条"可证伪认知命题 + 机制级消融"（含假设 + 情绪机制公式 + 消融设计 + 诚实路线），保留 EDA-Flow-Bench 独立。agent 自决，但**总数 ≤ 3**。
>
> ### ③ 同步修改
>
> - **Abstract**（`sections/0_abstract.tex`）：现 abstract 强调"3 核心假设 + 10 臂 + 三公式"，需调整叙事权重——**EDA-Flow-Bench 评测集应占更显著位置**（它是第一贡献项），认知命题 + 情绪机制作为第二贡献。agent 自主调整 abstract 句序与权重，但保留核心数字（7.6× / 1684 / 10.0% / 76.5% / 696）+ 三公式 + 诚实路线 + no-release。词数仍 ≤ 200（v1.8 摘要判据继续）。
> - **§1 Intro Contributions 段**（`sections/1_intro.tex:22`）：5 条 → 2-3 条（按 ② 推荐）。
> - **计划书**（`reports/report_edafb_icml2027_plan_zh.html`）§6.2 贡献列表：同步精简至 2-3 条（与论文一致）；注意 v1.6 计划书原是 5 条贡献，v1.7 论文沿用，现在统一改。
> - **不强制改其他章节**：§5 假设表 / §6 实验 / §9 结论等不动（它们是内容展开，不是贡献列表）；但若 §9 Conclusion 的"we formulate 3 core hypotheses ..."句与新的 2-3 条贡献叙事冲突，agent 可微调（自决）。
>
> ### ④ 硬约束（继承，全部继续生效）
>
> - **可改**：`EDA-Flow-Bench_ICML2027/sections/1_intro.tex` + `0_abstract.tex` + `9_conclusion.tex`（可选微调）+ `reports/report_edafb_icml2027_plan_zh.html`。
> - 🚫 **不动**：其他 sections / appendix / main.tex 宏定义 / designflow 造题线 / 其他论文树。
> - 🚫 **不起**：训练/评测进程。
> - ✅ **正文 ≤ 6 页**（精简贡献应让正文更短或持平）。
> - ✅ **双盲匿名 + 防伪底线 + 0 外链**（计划书）。
> - ✅ **EDA-Flow-Bench 必须作为独立贡献项**（用户硬要求）。
> - **编译验证**：4 轮 pdflatex+bibtex；0 error 0 undefined；正文 ≤ 6 页；匿名性复检；abstract 词数 ≤ 200。
> - **提交**：commit 前缀 `zhulong paper: 贡献列表精简至 2-3 项（EDA-Flow-Bench 评测集升格为独立贡献 + 认知命题/消融合并）`；**只 add 论文树 + 计划书 + 本线 run 文件**，勿 `-A`。
> - **判据（自检后再提交）**：
>   ① Contributions 段 2-3 条（grep `We \\emph{` 命中数 = 2 或 3）✅；
>   ② 其中一条显式是 EDA-Flow-Bench 评测集（含 "real ... traces" / "1684" / "13 domains" / "design_flow contract" 关键词）✅；
>   ③ Abstract 叙事权重调整（EDA-Flow-Bench 占更显著位置）✅；
>   ④ Abstract 词数 ≤ 200 ✅；
>   ⑤ 计划书 §6.2 同步精简 ✅；
>   ⑥ 编译 0 error 0 undefined ✅；
>   ⑦ 正文 ≤ 6 页 ✅；
>   ⑧ 匿名 + 防伪 + 双盲继续过 ✅。
> - 完成后 `WAITING=0` standby，记一行心跳。
>
> **agent 自主空间**：2 条还是 3 条 / 具体措辞 / abstract 句序调整 / §9 是否微调 由 agent 自主决定——用户给的是"2-3 项 + EDA-Flow-Bench 必须独立"，不是逐字模板。

> 🔴 **2026-11-19 用户令 — 删除全部"预注册"相关内容（预注册日 / 预注册声明 / `\PreregDate` 宏 / "pre-register"措辞 / 预注册纪律段），保留假设/判据/诚实路线本身（最高优先 · 覆盖 standby）**
>
> 本条是 v1.8（5 条修订，commit `e31a8048d`）之后的**删除令**。用户原话：「不需要预注册 计划也没法排的这么严格 都删掉」。
>
> **背景**：v1.4 计划书里 agent 自己设了"预注册日 2026-11-22"并写进论文 `\PreregDate` 宏 + §6 预注册声明 + 多处"pre-registered"措辞。用户从未确认这个日期，也不需要预注册纪律——计划无法排得这么严格。**全部删除**，但**保留**假设/判据/诚实路线本身（这些是论文内容，不是预注册纪律）。
>
> ### ① 删除范围（全论文树 + 计划书）
>
> **必须删除/改写的内容**：
> 1. **`main.tex` 第 45-46 行 `\newcommand{\PreregDate}{2026-11-22}` 宏定义** —— 删除宏定义；所有引用 `\PreregDate` 的地方同步改写（见下）。
> 2. **`sections/1_intro.tex:32` "Pre-registration" 段** —— 整段删除（"All hypotheses, arms, and criteria are pre-registered before data collection on \PreregDate. The M0 baseline ... are to be evaluated post pre-registration."）；可保留一句中性的实验状态说明如"M0 baseline is available from a frozen 696-run snapshot; other arms are to be evaluated."
> 3. **`sections/6_experiments.tex:5` "Pre-registration statement" 段** —— 整段删除或改写为中性"Experimental status"段（去掉"pre-register"/"pre-registration"措辞 + `\PreregDate`，保留 M0 锚点 + 其他臂 TBD 的事实）。
> 4. **`sections/0_abstract.tex`** —— "We pre-register 3 core falsifiable hypotheses" → 改为 "We formulate 3 core falsifiable hypotheses"；"all other arms are evaluated after the pre-registration date (\PreregDate)" → 改为 "all other arms are to be evaluated"（去预注册日）。
> 5. **`sections/5_preregistered.tex`** —— 文件名/节名 `\section{Pre-Registered Hypotheses and Ablation Design}` → 改为 `\section{Falsifiable Hypotheses and Ablation Design}`（去 "Pre-Registered"）；`\label{sec:preregistered}` 可保留（避免大规模 \ref 改动）或改为 `sec:hypotheses`（agent 自决，但必须全树 \ref 同步）；正文 "We pre-register 3 core hypotheses ... frozen before data collection on \PreregDate" → 改为 "We formulate 3 core falsifiable hypotheses ... each with falsification conditions"（去预注册 + 去冻结日）。
> 6. **`sections/9_conclusion.tex:5,10`** —— "We pre-registered 3 core hypotheses ... evaluated after \PreregDate" → 改为 "We formulate 3 core falsifiable hypotheses ... other arms are to be evaluated"；"first pre-registered evidence" → 改为 "first falsifiable evidence" 或 "first mechanistic evidence"。
> 7. **`sections/10_ethics.tex:5`** —— "Pre-registration discipline (\PreregDate) ensures hypotheses and criteria cannot be retroactively adjusted" 整句删除（预注册纪律段）；保留前面的脱敏说明 + 后面的 negative-results 报告声明。
> 8. **`sections/3_task_benchmark.tex:18,24`** —— "measured post pre-registration" → 改为 "to be measured"；"预注册后与各臂一同测量" → 改为 "与各臂一同测量"。
> 9. **`sections/6_experiments.tex:45,47,49,53,79,83`** —— "pre-registered threshold" → 改为 "falsification threshold" 或 "pre-specified threshold"（"pre-specified" 不是预注册，是假设判据的事前说明，OK）；"post pre-registration" / "pre-registration" 全部改为 "to be evaluated" 或 "pending evaluation"；Table caption "Pre-registered criteria check (results \TBD{} post pre-registration)" → 改为 "Criteria check (results \TBD{})"；"No new evaluation runs before \PreregDate" → 改为 "No new evaluation runs are reported in this paper" 或直接删除该句。
> 10. **`sections/7_analysis.tex:22,24,28`** —— "placeholder, post pre-registration" → 改为 "placeholder, pending evaluation"；"待预注册后评测" → 改为 "待评测"。
> 11. **`sections/8_related.tex:13,17,18,21,26`** —— "pre-registered falsification" → 改为 "falsifiable test" 或 "mechanism-level falsification"；"this paper pre-registers" → 改为 "this paper tests"；"本文预注册的经验问题" → 改为 "本文检验的经验问题"。
> 12. **`appendix/D_affective_mechanism.tex:65,66,75,77,80,81,93,94`** —— "pre-registered falsification" → "falsifiable test"；"first pre-registered, falsifiable test" → "first falsifiable test"；"post pre-registration" → "pending evaluation"；"占位图（预注册后）" → "占位图（待评测）"。
> 13. **`sections/11_reproducibility.tex`** —— 若有"pre-registration"措辞一并删除（grep 确认）；保留附录政策说明段。
> 14. **`main.tex:7` 注释** "v1.7 重写：从'卖 bench'重定位为'认知命题 + 情绪机制 + 预注册可证伪'" → 改为 "v1.7 重写：从'卖 bench'重定位为'认知命题 + 情绪机制 + 可证伪假设'"（去"预注册"）。
>
> **计划书同步**（`reports/report_edafb_icml2027_plan_zh.html`）：
> - 若计划书中有"预注册日 2026-11-22" / "pre-registration" / "预注册" 措辞，同步删除或改为"可证伪假设" / "falsifiable hypotheses"（agent 自主判断改动范围，但必须与论文一致）。
> - §7.2 时间线节点"预注册日 2026-11-22"删除，其他时间线节点（数据冻结日/最小矩阵跑完/ICML 截稿）可保留或一并删（用户说"计划也没法排的这么严格"，倾向删除整个严格时间线，保留 ICML 截稿日作为外部硬约束）。
>
> ### ② 保留的内容（不要误删）
>
> - ✅ **3 核心假设 + 7 子假设**（H1/H2/H3 + H1a/b/c · H2a/b/c · H3）—— 假设本身保留，只去"预注册"措辞。
> - ✅ **每条假设的证伪条件**（falsification conditions）—— 保留，这是可证伪性，不是预注册。
> - ✅ **诚实路线**（"若 H1/H2 被证伪，写成边界条件，本身可发表"）—— 保留。
> - ✅ **M0 锚点 10.0% + 696-run 快照** —— 保留（这是已有数据，不是预注册纪律）。
> - ✅ **M1-M8/N1-N2 结果 TBD** —— 保留"待评测"事实，只去"预注册后评测"的措辞。
> - ✅ **判据阈值 / 统计方法**（McNemar / paired bootstrap / α=0.05）—— 保留（这是事前说明的判据，不是预注册纪律；"pre-specified threshold" OK，"pre-registered threshold" 改）。
> - ✅ **附录政策说明**（§11 ICML appendix policy 段）—— 保留。
> - ✅ **双盲匿名 / 防伪底线** —— 保留。
>
> ### ③ 硬约束（继承 v1.8，全部继续生效）
>
> - **可改**：`EDA-Flow-Bench_ICML2027/main.tex` + `sections/*.tex` + `appendix/*.tex` + `reports/report_edafb_icml2027_plan_zh.html`。
> - 🚫 **不动**：designflow 造题线 cases/jsonl/ledger、其他论文树。
> - 🚫 **不起**：训练/评测进程。
> - ✅ **正文 ≤ 6 页**（删除内容应让正文更短或持平，不应变长）。
> - ✅ **0 外链 0 script**（论文树无 HTML，此条对计划书 HTML 继续生效）。
> - ✅ **双盲匿名** + **防伪底线**（不编造数字/文献，不改判据/题/样本，不删他人数据）。
> - **编译验证**：4 轮 pdflatex+bibtex；`grep -c '^!' main.log` = 0；`grep -c 'Undefined' main.log` = 0（注意删除 `\PreregDate` 宏后，所有引用该宏的地方必须同步改，否则会 undefined）；正文页数 ≤ 6；匿名性复检。
> - **提交**：commit 前缀 `zhulong paper: 删除全部预注册相关内容（预注册日/声明/宏/措辞），保留假设/判据/诚实路线`；**只 add 论文树 + 计划书 + 本线 run 文件**，勿 `-A`。
> - **判据（自检后再提交）**：
>   ① 全论文树 grep `\\PreregDate` = 0（宏定义 + 所有引用全删）✅；
>   ② 全论文树 grep -niE 'pre-regist|preregist|预注册' = 0（除注释行 + 计划书同步）✅；
>   ③ `main.tex` 无 `\newcommand{\PreregDate}` 宏定义 ✅；
>   ④ §1 / §6 的"Pre-registration"段删除或改写为中性"Experimental status" ✅；
>   ⑤ 假设/证伪条件/诚实路线/M0 锚点/TBD 保留（grep `falsif|H1|H2|H3|MzeroPass|TBD` 命中数不降）✅；
>   ⑥ 编译 0 error 0 undefined（删宏后无 `\PreregDate` undefined 报错）✅；
>   ⑦ 正文 ≤ 6 页 ✅；
>   ⑧ 匿名性 + 防伪底线 + 双盲继续过 ✅；
>   ⑨ 计划书同步（§7.2 预注册日删除 + "预注册"措辞改"可证伪假设"）✅。
> - 完成后 `WAITING=0` standby，记一行心跳（wake# 续编）。
>
> **agent 自主空间**：`\label{sec:preregistered}` 是否改名为 `sec:hypotheses`（需同步全树 \ref）由 agent 自决；§6 "Pre-registration statement" 段是整段删还是改写为中性"Experimental status"由 agent 自决；计划书时间线节点保留哪些由 agent 自决——用户给的是"删预注册 + 保留假设/判据/诚实路线"，不是逐字模板。

> 🔴 **2026-11-19 用户令 — 论文双盲 + 排版 + 开源承诺 + 附录政策 5 条修订意见（最高优先 · 覆盖 standby）**
>
> 本条是 v1.7 论文重写 + 朋友评审处置（commit `cfb185159`·12p/0err/0undef）之后的**5 条修订意见**，全部针对 `EDA-Flow-Bench_ICML2027/` 正文与排版。subagent 消融线仍保持 `done_all` 结案，**不起任何新臂**。
>
> **用户原话（逐条对齐）**：
> 1. 「由于要双盲投稿，"Our prior work" 这样的措辞需要处理」
> 2. 「这张表【5.1. Three-Layer Structure】对于双栏过宽，已经侵入 margin 了」
> 3. 「摘要是否太长，ICML 一般摘要多少字（word）？」
> 4. 「任何数据、代码都不承诺开源」
> 5. 「提交论文给 ICML 时需要附录吗，reviewer 会看吗？」
>
> ### ① 意见 1：双盲匿名 — "Our prior work" 措辞处理
>
> - **问题定位**：`sections/2_background.tex:14` 有 "Our prior work on script-layer EDA (DATE27, \cite{...}; ZhuLong-DAC, \cite{...}) showed memory + RSI gains on short-chain tasks" —— 这是**自指暴露**，"Our prior work" 直接告诉审稿人 DATE27 / ZhuLong-DAC 是作者自己的工作，违反双盲。
> - **排查范围**：全论文树 grep `Our prior work|Our earlier|Our previous|Our own|We previously|in our prior|in our earlier|in our previous`，所有命中都要改。
> - **改写策略**（agent 自主选择，但必须双盲合规）：
>   - 改为第三方引用：`Prior work on script-layer EDA (DATE27, \cite{...}; ZhuLong-DAC, \cite{...}) showed ...` —— 去掉 "Our"，把 DATE27/DAC 当作"已有工作"引用。
>   - 或匿名引用：`Building on script-layer EDA memory + RSI work (DATE27, \cite{...}; ZhuLong-DAC, \cite{...}), this paper tests whether ...` —— 不声明归属。
>   - **DATE27 占位引用 `\cite{PLACEHOLDER_DATE27_ZHULONG}` 保留**（预印版 12 月上线后回填，现在双盲下占位 OK）。
> - **自检**：`grep -nE 'Our prior|Our earlier|Our previous|Our own|We previously' sections/*.tex main.tex` = 0 命中（除注释行）。
> - **匿名性复检**：`pdftotext main.pdf - | grep -iE 'Yang Liu|Hongwen|cxmt|ChangXin|Our prior|Our earlier|Our previous'` = 0。
>
> ### ② 意见 2：§5.1 Three-Layer Structure 表过宽侵入 margin
>
> - **问题定位**：`sections/5_preregistered.tex:16` 的 `\begin{tabular}{@{}lll@{}}` 三列表（Layer / Core Hyp. / Sub-Hypotheses）在 ICML 双栏 `\columnwidth` 下过宽，侵入 margin（用户实测）。
> - **修复策略**（agent 自主选择，但必须不侵入 margin）：
>   - 改用 `tabularx` + `\columnwidth` + `X` 列（自动换行）：`\begin{tabularx}{\columnwidth}{@{}lXX@{}}` 或 `@{}llX@{}`；
>   - 或缩写列头（Layer / Core / Sub）+ 内容紧凑化（如 "L1 Total (functional)" → "L1 Total"）；
>   - 或改为列表/段落形式（不用表格）：`L1 Total: H1 ... (H1a, H1b, H1c)` 三行列表；
>   - 或用 `\small` / `\footnotesize` 缩字号（但 ICML 不鼓励正文表格用 footnotesize）。
> - **自检**：编译后 `pdftotext -layout main.pdf -` 检查 §5.1 表格不越 margin；或看 main.log 的 `Overfull \hbox` 警告中该表所在行不出现。
> - **顺带排查**：其他表格（§5 子假设表、§6 实验矩阵、§3 delta 表等）也 grep `Overfull \hbox` 看是否有同类问题，一并修。
>
> ### ③ 意见 3：摘要长度 — ICML 惯例与压缩
>
> - **现状**：abstract 现 **215 词**（英文，不含中文注释）。
> - **ICML 惯例**：ICML 官方 author kit 通常**不设硬限**但惯例 **150-250 词**，多数录用论文在 **180-230 词**。215 词在惯例范围内**不算过长**，但偏长；考虑到用户主动询问，倾向压缩。
> - **处理要求**（agent 自主判断，但必须给数据支撑）：
>   - 在 `sections/0_abstract.tex` 顶部加一行注释 `% abstract word count: N (ICML convention 150-250)`，标注当前词数；
>   - 若 agent 判断 215 词合理（在惯例范围内），可保留但**给理由**（如"含三公式 + 预注册声明 + 开源边界，信息密度高"）；
>   - 若 agent 判断可压缩，目标压缩到 **~180-200 词**：可压缩处——开源边界细节（"protocol white-paper + NDA review package, without releasing executable Lite-set assets" 可缩短）、三公式可只提"three computable mechanisms"不列公式（公式在 §4 有）、negative-results 声明可缩短；
>   - **保留**：7.6× 跳变 / 3 核心假设 / 10 臂 + N1 + M4 / 预注册日 / 诚实路线（这些是核心叙事）。
> - **自检**：编译后 `sed -n '/\\begin{abstract}/,/\\end{abstract}/p' sections/0_abstract.tex | grep -v '^%' | wc -w` 报告最终词数，在 commit message 标注。
>
> ### ④ 意见 4：任何数据、代码都不承诺开源
>
> - **问题定位**：v1.4 把开源边界从"Lite 500 + mock-EDA"收缩到"协议白皮书级开源（harness 协议 + 判据 + 脱敏任务规格开源）"，但**用户现在要求更进一步：任何数据、代码都不承诺开源**。
> - **排查范围**：全论文树 grep `release|released|open.?source|open.?sourced|publicly available|will be made available|code is available|data is available|repository|github|huggingface|we open|we release|we share|we publish`（不区分大小写），所有"承诺开源"的措辞都要改。
> - **改写策略**（agent 自主选择，但必须完全不承诺开源）：
>   - 删除所有"we release / we open-source / will be made available"承诺；
>   - 改为"due to the production-origin of the traces (real IC design engineer sessions on commercial EDA tools), **no data, code, or executable assets can be released**; reproducibility is supported via a **detailed protocol description** (this paper) + **NDA-gated controlled review package** for qualified reviewers"；
>   - §11 Reproducibility 改为"reproducibility via protocol description + NDA review package only; no public release of data/code/assets"；
>   - Abstract 的 "We release a protocol white-paper ..." 句**删除**或改为 "No data or code is released; reproducibility is supported via a detailed protocol description and an NDA-gated review package."
>   - §3 Task Modality 的"协议白皮书级开源"措辞改为"协议描述（本论文）+ NDA 受控评审包"；
>   - Appendix D / A / B / C 中若有"will release"措辞一并改。
> - **自检**：`grep -niE 'we release|we open|will be made available|publicly available|github|huggingface|we share|we publish.*code|we publish.*data|open-source' sections/*.tex appendix/*.tex main.tex` = 0 命中（除纯描述性"open-source EDA tools"如 Yosys/OpenROAD 上下文，那些是引用别人的开源工具不是承诺自己开源，保留）。
> - **诚实性**：不承诺开源是真实情况（trace 源自公司生产资产，确实不能开），不是虚假声称。
>
> ### ⑤ 意见 5：ICML 附录政策 — 需要附录吗？reviewer 会看吗？
>
> - **ICML 政策（agent 必须在回复中给数据支撑，不能凭印象）**：
>   - **需要附录吗**：ICML **不强制**附录，但**强烈建议**有附录放补充材料（proofs / detailed experimental setup / additional results / dataset details）。ICML 2024/2025 author kit 明确："Appendices are allowed and do not count toward the page limit; however, reviewers are not obligated to read appendices, and the main paper should be self-contained."
>   - **reviewer 会看吗**：reviewer **不强制**读附录，主审通常读正文 + 抽查附录关键部分（如 proof of main theorem / detailed setup for reproducibility）。附录是"必要时可查的补充"，不是"必须读完的内容"。**关键结论必须在正文**，附录只能放支撑细节。
>   - **页数**：附录**不计入正文页数**（正文 ≤ 9 页 ICML 2027，用户自我加压 ≤ 6 页；附录无上限但建议 ≤ 20 页，超长附录可能被审稿人吐槽）。
> - **对本论文的具体建议**（agent 写进论文 §11 Reproducibility 或 README，并回应用户）：
>   - **保留附录**：Appendix A (benchmark details) / B (additional results) / C (experimental details) / D (affective mechanism design details) 都有补充价值，保留；
>   - **正文必须 self-contained**：§5 假设 + §6 实验框架 + §7 分析的**核心结论与判据**必须在正文能读懂，不依赖附录；
>   - **附录定位**：在 §11 Reproducibility 或正文首次引用附录处加一句"see Appendix X for details"明确指针，但不把关键判据只放附录；
>   - **附录长度**：agent 自检附录页数（编译后 main.pdf 的 appendix 部分），若 > 15 页考虑压缩（朋友评审 P1 已把 M1/M8 移 appendix，注意不要 appendix 臃肿）；
>   - **回应用户**：在 commit message 或 MEMORY 心跳明确写"ICML 附录政策：不强制但建议；reviewer 不强制读；附录不计入正文页数；本论文保留 Appendix A-D 作支撑细节，关键结论在正文"。
>
> ### ⑥ 硬约束（继承 v1.7，全部继续生效）
>
> - **可改**：`EDA-Flow-Bench_ICML2027/main.tex` + `sections/*.tex` + `appendix/*.tex` + `main.bbl`。
> - 🚫 **不动**：designflow 造题线 cases/jsonl/ledger、其他论文树（DATE27/DAC/ASPDAC）。
> - 🚫 **不起**：训练/评测进程。
> - ✅ **正文 ≤ 6 页**（v1.7 硬限继续；当前 7 页，本次修订若加内容需同步压缩，目标压到 ≤ 6 页）。
> - ✅ **0 外链 0 CDN 0 `<script>`** 纪律（论文树无 HTML，此条对 HTML 报告继续生效）。
> - ✅ **双盲匿名**：`\documentclass[submitted]` 或 icml2026 [submitted] 选项保留；pdftotext 无作者/机构/自指泄漏。
> - ✅ **防伪底线**：不编造数字 / 不编造文献 / 不改判据/题/样本 / 不删他人数据。
> - ✅ **预注册纪律**：§6 预注册日 2026-11-22 声明保留。
> - **编译验证**（必须自检后提交）：4 轮 pdflatex+bibtex；`grep -c '^!' main.log` = 0；`grep -c 'Undefined' main.log` = 0；正文页数 ≤ 6；匿名性复检；`Overfull \hbox` 警告中 §5.1 表格不出现。
> - **提交**：commit 前缀 `zhulong paper: EDA-Flow-Bench ICML2027 双盲+排版+开源+附录 5 条修订（"Our prior work"匿名化 / §5.1 表过宽 / 摘要长度 / 不承诺开源 / 附录政策说明）`；**只 add 论文树 + 本线 run 文件**，勿 `-A`。
> - **判据（自检后再提交）**：
>   ① 全论文树 0 处 "Our prior/earlier/previous/own" 自指（grep=0，除注释）✅；
>   ② §5.1 Three-Layer Structure 表不侵入 margin（Overfull \hbox 警告中无该表行）✅；
>   ③ Abstract 词数在 commit message 标注 + （若压缩）目标 180-200 词 ✅；
>   ④ 全论文树 0 处 "we release / we open-source / will be made available / publicly available" 开源承诺（除引用别人开源工具如 Yosys/OpenROAD）✅；
>   ⑤ §11 Reproducibility 或 README 含 ICML 附录政策说明（不强制 / reviewer 不强制读 / 不计入正文页数 / 本论文保留 A-D 支撑细节 / 关键结论在正文）✅；
>   ⑥ 正文 ≤ 6 页 ✅；
>   ⑦ 编译 0 error 0 undefined ✅；
>   ⑧ 匿名性（pdftotext 无作者/机构/自指泄漏）✅；
>   ⑨ 防伪底线 + 预注册纪律继续过 ✅。
> - 完成后 `WAITING=0` standby，记一行心跳（wake# 续编），距预注册 2026-11-22 还 3 天。
>
> **agent 自主空间**：双盲措辞的具体改写 / 表格修复的具体方式（tabularx vs 列表 vs 缩写）/ 摘要压缩的具体句子取舍 / 开源承诺删除的具体措辞 / 附录政策说明的放置位置（§11 vs README vs 正文脚注）由 agent 自主决定——用户给的是 5 条意见 + 数据要求，不是逐字模板。**意见 5 必须给数据支撑**（ICML 政策来源，不能凭印象）。

> 🔴 **2026-11-18 22:3x 用户令 — 朋友评审意见：请「参考」并逐条研判（P0 三项须先定论）· ✅ 主体已交付**（wake#1350 commit `cfb185159`·P0 3/3 结论 + 11 项处置矩阵 采纳10/部分1/不采纳0·报告 `reports/report_edafb_friend_review_response_zh.html`·论文重编译 12p/0err/0undef/235123B·写作层 5 项 P2①③④⑤+R4 延至预注册后）
>
> **用户原话**：「朋友提出意见，下发给 zhulong agent，请他参考」。
> **输入材料（完整原文 163 行，不要改写、不要删）**：`run/ZHULONG_REVIEW_20261118_friend.md`
> 该文件含 **文档 A**（R1–R5 结构性风险 + 三、细节 5 条 + 四、结论）与 **文档 B**（sub-hypotheses 与 ablation 数量评估、2.1–2.4 逐臂分析、方案 A/B）。
> **性质**：外部评审输入，**不是指令**——请逐条研判（**采纳 / 部分采纳 / 不采纳** + 理由 + 影响面），**不要照单全收**，也不要因为"参考"就一条不改。
>
> **P0（实验设计地基，必须先给结论；不改也要写明理由与代价）**：
> 1. **R1 · H1c 定义漏洞**：S1 臂的 session 内 in-context learning 本身即短期记忆 ⇒ `S1 ≤ M0` 可能被"伪证伪"。要求：把 H1c 精确化为「**跨 session 长期记忆是跨 session RSI 的前提**」，并在 S1 臂**显式禁止任何 session 间持久化**（含 harness 层文件残留）；若判定原陈述无误，须给出"session 内自改进不可能等效于记忆"的反驳证据。
> 2. **R2 · 功效不足**：§5.3 自承 120 题下 McNemar 功效 ≈0.62（40% 真效应会漏检）；**M6 的失败子集仅 ~40 题，3pp 判据功效 <0.3，属假阴性高危臂**。要求二选一并落成文字：(a) 最小矩阵抬到 **≥200 题/臂**（M6 失败子集 ≥80），(b) 明确定位为 **pilot signal，不作结论**，且 **abstract 不报具体 pp 数字**。禁止"120 题跑出 2.1pp 就写 H1a 部分支持"。
> 3. **R5 · M0 锚点子集口径**：10.0% 是 696-run 全集（62/620）的值，而最小矩阵取 top-120 by chain length ⇒ 子集 M0 很可能只有 4–6%。要求：**M0 锚点必须用同子集实测值**（重跑或明确声明），同步改 §5.4「M0 引用快照」行。
>
> **P1（臂表收敛，需给明确结论）**：参照文档 B 的**方案 A**（13 → **10 臂主表 + 3 臂附录**：主表 `M0·M3·S1·M3+S1·N1·N2·M4·M5·M6·M7`；M1 移附录；M2 仅作 M5/M7 对照、**撤掉 M2≥M0+2pp 与 M3≥M2+1pp 两条判据**；M8 移附录）。若采纳，须同步：§5.1 臂表 / §5.2 假设映射 / §5.3 功效与题量 / §5.4 时间线 / §6 判据编号 / 论文 §5 与 §6 对应段落。若不采纳，逐臂说明保留理由与功效依据。
>
> **P2（写作与口径，逐条给结论）**：① abstract 里 "7.6× drop" 与 "7.1× domain gap" 并置需半句区分（跨任务难度 vs flow 内域间差异）；② H2b 联合判据的**中间地带**（记忆 0.6–0.8×、Pass@1 持平）需定义「弱支持」；③ 表 5 的 UNK **119** 与正文 **49** 口径不一致，须加脚注；④ **DATE27 的 PLACEHOLDER 引用**必须在截稿前落实（否则 Related Work「继承 DATE27 骨架」缺支撑）；⑤ B.2「five machine-days」与 §5.4「28 天」量级差异 ⇒ 拆成「多骨干扫描」与「全臂理想矩阵」两个里程碑。
> **R3/R4 也要给结论**：R3 = M4 泄露审计需**机器可判代理指标**（记忆条目与目标域 prompt/文件名/断言字面量的 n-gram 重叠率，人工只审 borderline）；R4 = 论文 **§4.5.1 公式旁补「与最近邻方法的计算差异」**（surprise 用 KL(posterior∥prior) 而非 embedding 距离；penalty 是 sunk-cost 而非固定权重），并说明 M5 的 α/β 扫描考的是「机制贡献」还是「超参」。
>
> **纪律**：
> - 逐条处置矩阵必须写明 **采纳/部分/不采纳 + 理由 + 影响面（改哪些文件/哪些臂/要不要重跑）**；不采纳项要给"不改的代价"判断。
> - **不改任何既有实测数字**（696-run / 10.0% / 62·558·70·6 / 2.9% physical_verify 等），不编造新数字；不改题、图、check、他线文件。
> - **⚠️ 预注册日 2026-11-22 只剩 3 天**：优先级 = 保证"预注册材料可冻结"。请明确划分：哪些进 **plan v1.8**（设计层）、哪些进**预注册文档**（判据层，冻结后不可改）、哪些只改**论文正文**（写作层）。若 3 天内做不完，先交 P0 + 处置矩阵，其余排到预注册后。
>
> **验收**：① P0 三项均有明确结论；② 处置矩阵覆盖 R1–R5 + P2 五项 + 臂表收敛；③ 若动臂表/假设 ⇒ 四处编号（§5.1/§5.2/§5.3/§6）与论文对应章节同步且自查一致；④ 论文若改，重新编译 `pdflatex→bibtex→pdflatex×2` 记页数/0 err/0 undef（页数变化须说明原因）；⑤ 交付中文 HTML 报告 `run/reports/report_edafb_friend_review_response_zh.html`（与本线 `report_edafb_zh_translation_zh.html` 同目录，单文件自包含无外链：逐条处置矩阵 + P0 改前/改后对照 + 臂表 diff + 待决项）；⑥ MEMORY/daily 一行 `[friend-review] P0 3/3 结论 · 采纳 n / 部分 m / 不采纳 k · plan vX · commit <sha>`。
> **提交**：前缀 `zhulong review:`，只 `git add -- doc/ZhuLong_DAC2027/**`（含本次评审输入文件与报告）。

> 📦 已归档 · 2026-11-18 20:5x zh-cn 令（论文全文加中文对照·注释态）· ✅ 已交付 round1 `abf24281f`+round2 `28e77662f`·编译 11p/0err/230611B 同字节·报告 `reports/report_edafb_zh_translation_zh.html`·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 20:5x zh-cn」。



> 📦 已归档 · 2026-11-18 v1.7 令（放行直接改论文正文：按 v1.6 计划书重写 `EDA-Flow-Bench_ICML2027/` 正文 main.tex + sections/*.tex + appendix/*.tex + main.bbl·正文 ≤ 6 页·10 判据全通过）· ✅ 已交付·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.7」。

> 📦 已归档 · 2026-11-18 v1.6 令（假设内聚化重组：7 条并列假设 → 3 条核心假设 + 7 条子假设·总-机制-边界三层 + §5.1 臂表对应假设列 + §6 编号同步）· ✅ 已交付·报告 122386B·8 判据全通过·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.6」。

> 📦 已归档 · 2026-11-18 v1.5 增量令（§6 同步至 v1.4 口径：标题/贡献/章节/图表 4 处）· ✅ 已交付 commit `e810dc502`·报告 119150B·7 判据全通过·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.5」。

> 📦 已归档 · 2026-11-18 v1.4 令（核心认知升级情绪×长期记忆 + Full→Lite 迁移 + 开源边界收缩 + cimi_search 调研 + 合并 v1.3 预印本引用子任务④）· ✅ 已交付 commit `2c4ed787d`·v1.4·111269B·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.4」。

> 📦 已归档 · 2026-11-18 v1.3 令（补两篇 zhulong 预印本 BibTeX 引用）· ⚠️ 已被 v1.4 令合并为子任务 ④，不单独出 v1.3·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-18 v1.3」。

> 📦 已归档 · 2026-11-17 22:5x 新任务令（EDA-Flow-Bench 论文重定位 + 消融设计 + 计划书 v1）· ✅ 已交付 commit `87cdb56f8`（v1 计划书）·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-17 22:5x v1」。



> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不改题/图/check、不编造数字、不删他人数据）。判断标准只有一条：**这条约束是为了「防止说谎/防止破坏」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主设计消融臂、判据与实验路线；A3/A4/… 的 idea 由你提，不要等我给。**

> 📦 已归档 · 2026-11-17 09:3x 结案令（停止 subagent 消融评测·覆盖一切前令）· ✅ 已执行（A0pp eval killed by ops）·两条认知结论（单 agent > 多 agent；自主 spawn > 用户定制）已入 MEMORY·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-17 09:3x 结案」。

> 📦 已归档 · 2026-11-16 09:0x（用户令：修正 A0′/A3 实验设计 · 限制 input 而非 output）· ⚠️ 被 2026-11-17 09:3x 结案令覆盖（subagent 消融线结案，不再追加新臂）

> 📦 已归档 · 2026-11-15 20:5x 用户令（放行 A3–A6）· ⚠️ 被 2026-11-17 09:3x 结案令覆盖（subagent 消融线结案，不再追加新臂）·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 20:5x 用户令」。

> 📦 已归档 · 2026-11-15 20:5x 运维令（放行 A3–A6·允许起实验）· ⚠️ A0′/A3 预算维度被 2026-11-16 令修正 + 整体被 2026-11-17 结案令覆盖·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 20:5x 运维令」。


> 📦 已归档 · 2026-11-15 15:0x（用户令：出「A3–A6 是什么」中文 HTML 报告 · 纯文档不跑实验）· ✅ done_all commit `afc4c83a9`·报告 `reports/report_zhulong_a3a6_arms_zh.html`（8 节齐全 + 互链✅·wake#972 核验）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 15:0x」。


> 📦 已归档 · 2026-11-15 12:5x（清盘令）· ✅ done_all（wake#975 第三轮双达标·`/home` 5.8G✅ / `/nasdata` 33G✅·三轮 wake#967/968/975·报告 `reports/report_zhulong_disk_cleanup_zh.html` + TSV `zhulong_disk_cleanup_20261115_*.tsv`）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 12:5x」。


### 📦 已归档 · 2026-11-15 07:2x 用户裁令（⛔ 停止 H2 · 写 A0/A1/A2 trace 报告 · 提出 A3/A4… idea · 采纳「独立上下文 + 固定小 token 预算」思路）· ✅ 已完成 wake#957 commit `a6f78b8bc`·原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15 07:2x」。


> 📦 已归档 · 2026-11-14 23:4x（清盘 + 隧道复盘）· ✅ done_all commit 03bc3224d · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-14 18:3x（A1 提示改验证 agent → A2 新臂）· ✅ A2 三轮全完 53.3±3.8% · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-14 17:0x（H2 恢复：改 cline 源码 + wrapper v3.0.74）· ✅ commit 39ccd44cc + 三 smoke 全过（H2 后被 11-15 07:2x 叫停）· 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。
> 📦 已归档 · 2026-11-13 21:2x（启动 subagent 消融）· ✅ A0/A1/A2 全完 + P4 报告 commit 9b0737fe4/a6f78b8bc · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-15」。

> 📦 已归档 · 2026-11-12 21:2x 压缩机制消融（basic vs agentic）·✅ 已交付 commit e09c7e238 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-12 15:4x B_en_r1 基座对齐重跑·✅ done_all commit a909fe482 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-11 22:4x RU+regrade+r3重跑 + 11-11 lang-audit·✅ 已交付 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准（本线消融实验的基座/题量/协议口径不受其影响）。



> 📦 已归档 · 2026-11-07 08:3x 两轴消融 thinking×lang·✅ 30/30 已交付 · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。
> 📦 已归档 · 2026-11-05 19:2x P0 双盲裁定·✅ CLOSED · 原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-14 05:04」。

### 📦 已闭合（batch 15/16，原文见 `ZHULONG_TASK_ARCHIVE.md`）

> 🚨 11-03 21:0x llama.cpp + Qwen3.5-0.8B 安装（smoke 双过）✅ · 11-02 21:3x Tab-3 美观改进（`Tab3_改进建议.html` 已入库，`6_exp.tex` 已落地）✅ · 10-30 22:2x zhulong-full×kimi-k2.6 5-run（**85.0±2.5%**，vs cline 86.8±1.6% Δ−1.8pp）✅ · 10-29 21:5x 论文审阅（92.8KB 报告，P0=1/P1=3/P2=11）✅ · 10-26 08:1x 作废 224219+重跑 glm53-full（已被 10-27 令覆盖）。详情见 archive §batch 15/16。


### 📦 归档指针 · 2026-10-25「按外部评审意见改论文（含 57.4pp 归因硬伤）」· 已执行完毕（10-26 令并行）。要点：改稿须如实标注「待补」及补法，不得编造数字/文献。原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-11」。

### 📦 已归档 batch 13 · 2026-10-27（*pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（硬上限 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
