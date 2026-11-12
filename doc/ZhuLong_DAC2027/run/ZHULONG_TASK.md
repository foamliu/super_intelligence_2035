# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

[用户令 · 2026-11-12 21:2x · 最高优先 · 新实验（压缩机制消融）]
用户原话："我想用 PyAether 158 评测 对比一下 cline 两个 压缩机制：basic vs. agentic 的效果。用中文HTML写个计划书。"

执行口径（严格按序）：
1) **计划书已交付（只读，按它执行）**：`doc/ZhuLong_DAC2027/reports/plan_zhulong_compaction_basic_vs_agentic_zh.html`（28.9KB，10 节 + 3 附录，0 外链）。先通读 §3 设计 / §4 指标 / §5 执行 / §6 分析 / §10 决策规则，再起跑。
2) **实验本质**：同一基座、同一 cline 版本、同一协议（`-p 8 -n`、`CLINE_THINKING=medium`、`LANG_HINT` 空、158 题），只切换 `cline --compaction basic` vs `--compaction agentic`；每臂 3 轮（ABBA 顺序：B→A→A→B→B→A），共 6 轮。
3) **P0 预检（必须先做，未过不许起跑）**：
   a. `cline --version` + `cline --help | grep -- --compaction` —— 现网 3.0.51 若**不支持该 flag**，升级到支持版本（4.x，记录版本号），两臂同版本，并加做 10 题校准；
   b. 检查 `EDA-Eval-Framework/scripts/run_cline_script.sh` 是否把 `CLINE_COMPACTION` 透传成 `--compaction`；无则按计划书附录 A 打 **3 行补丁**（无 flag 时保持原行为）；
   c. 两臂各 1 题 smoke：确认 `*.compaction.json` 出现且 `metadata.kind` 分别为 `compaction`（basic）/ `compaction_summary`（agentic）；
   d. 沙盒端口 8664/8665/8653/8669 全空闲 + quota probe 通过 + `pgrep -f '^bash scripts/run_cline_script'` 无输出。
4) **与 B_en_r1 重跑串行**：B_en_r1 收口（落盘+报告刷新+push）之前**不得**起本实验；两实验不并发（额度与沙盒都会互相污染）。
5) **P1 试点**：固定子集 10 题（seed=42）× 两臂各 1 轮，核对耗时/成本/压缩事件统计脚本可用 → 再开全量。
6) **P2 全量**：新建 `run/run_compaction_ablation.sh`（复制 `run_think_lang_ablation.sh`，去轴 A/B，改 6 轮 ABBA + `CLINE_COMPACTION`），每轮落 `run/ablation_compaction_results.json` 条目 + `run/cost_C_{basic,agentic}_r{1..3}.json` + trace 归档 `/nasdata/.../trace_compaction_ablation/<arm>/<batch>/`。每轮起跑前 quota probe；429 等待不降并发。
7) **P3 报告（用户点名要中文 HTML）**：`reports/report_zhulong_compaction_basic_vs_agentic_zh.html`——单文件自包含、内联 CSS、**0 外链**；8 节：摘要（三问结论）/机制口径/主结果（6 轮表+逐题配对）/亚组（是否触发压缩×轨迹长度×domain）/失败分类/成本-收益/摘要质量/结论与默认策略建议 + 附录。**主终点唯一 = 3 轮 Pass@1 均值（ITT）**；亚组只作次要终点，须报效应量+CI+n。
8) **预注册纪律**：跑前不改判据；所有轮次全入表、不剔除；单轮不下结论；差异 <3pp 就写「证据不足」，不许包装成增益。
9) **红线**：不 kill 编排器/loop；不与 designflow 并发抢沙盒；不改 benchmark/评分器；不删旧结果与 trace；不改别线文件。
10) **心跳**：每轮写清 臂/轮次/PID/etime/log 大小/batch/已评题数；实验跑中 WAITING=1；6 轮完成 + 报告刷新 + commit/push 后写 done_all + WAITING=1。


[用户令 · 2026-11-12 15:4x · 最高优先 · 覆盖 done_all 等待状态 · 基座对齐补救]
用户原话："既然你确定仅 B_en_r1 = glm-5.2，其余 14 轮（含 B_zh_r3 重跑）= deepseek-v4-pro-cloud，那就安排 zhulong agent 重新测试 B_en_r1；测完后刷新中文 HTML 报告，表格中加上 token 列。"

执行口径（严格按序，不许改序）：
1) **重跑 B_en_r1**：用与 B_en_r2/r3 完全相同的配置起新 batch 重跑 —— `thinking=medium`、`LANG_HINT="Think in English."`、**默认基座（deepseek-v4-pro-fp4/cloud，不强制 glm-5.2）**、`-p 8 -n`、158 题。目的：让轴 B 全部 15 轮基座一致（消除 wake#865 发现的基座违规），使 B 轴从「降级描述性」升级为「同基座可横比」。
2) **启动方式**（参考 B_zh_r3 重跑 PID 4037472 的成功模式）：
   ```bash
   cd /nasdata/app.e0031982/code/eda_fastmcp
   export CLI_AGENT=cline PARALLEL=8 CLINE_THINKING=medium LANG_HINT="Think in English."
   export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
   export EVAL_ROOT_DIR_OVERRIDE=/nasdata/app.e0031982/code/eda_code_eval
   export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
   export PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python
   export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
   export PATH="/home/app.e0031982/.local/node-20/bin:$PATH"
   setsid bash -c 'timeout --signal=TERM --kill-after=120 43200 bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_B_en_r1_rerun.log 2>&1' < /dev/null &
   ```
   ⚠️ 先 `pgrep -f '^bash scripts/run_cline_script'` 确认无其他评测在跑再起；沙盒端口 8664/8665/8653/8669 须全空闲（designflow 线不抢沙盒）。
3) **旧 B_en_r1 留档**（idx 15, pass=75.3%, batch 2026_1109_084446, glm-5.2）：
   - 在 `run/ablation_think_lang_results.json` 的 idx 15 summary 里加 `superseded_note` 字段，内容：`"2026-11-12 15:4x 令·基座对齐重跑·旧值 75.3% (glm-5.2) 留档不删·新 r1 完成后追加"`（参考 B_zh_r3 旧版 idx 20 的处理）。
   - `run/cost_B_en_r1.json` 改名 `run/cost_B_en_r1_old_glm52.json` 留档；新 r1 的 cost 写进新的 `run/cost_B_en_r1.json`。
4) **新 r1 落盘**（gen + score + cost 全完成后）：
   - 新 summary 追加到 `ablation_think_lang_results.json` 末尾（新 entry，tag 仍 `B_en_r1`，batch 为新 batch id，含完整 pass_rate_pct/passed/total/tokens/converged/timeout/gen_fail/success 字段）。
   - trace 存档到 `/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang/B_en_r1/<new_batch>/`（旧 batch 目录保留不删）。
5) **刷新报告**（新 r1 落盘后必做）：
   ```bash
   cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
   python3 gen_report_zhulong_ablation_think_lang_zh.py
   ```
   - 主报告 `reports/report_zhulong_ablation_thinking_language_zh.html` 已含 token 列（prompt/completion/reasoning/total tok + tok/题），刷新后 B_en 行自动用新 r1 数据。
   - **基座违规 banner 需改写**：B_en_r1 重跑后轴 B 全 15 轮基座一致（dsv4-pro-fp4），原 banner「仅 B_en_r1=glm-5.2，其余 14 轮=dsv4-pro」不再成立 → 改为「轴 B 15/15 轮 = dsv4-pro-fp4 ✅ 恒定合规（B_en_r1 已于 11-12 重跑对齐基座，旧 75.3% glm-5.2 版标 SUPERSEDED 留档）」；§⑦ 降级结论同步升级（B 轴可作同基座横比，但与基线 glm-5.2 的 Δpp 仍不可直接归因为语言效应，因基座不同）。
   - audit 报告 `reports/report_zhulong_lang_switch_audit_zh.html` §5.3 的「修正建议」同步标注「B_en_r1 已重跑对齐，剩余 14 轮本就同基座 → 基座恒定条件已满足；基础 prompt 中性化 + 语言切换验证仍需做」。
6) **B 轴独立报告** `reports/report_zhulong_ablation_axisB_language_zh.html`（11-12 15:34 生成）：
   - 由编排 agent 重新生成（用与主报告相同的 results JSON 数据源）；如无现成生成器，手动更新该 HTML 的 §2.1/§2.2 表格：① B_en r1 行替换为新 pass 率 + 新 batch + 新 tokens；② §2.1/§2.2 主表**每行加 token 列**（prompt/completion/reasoning/total tok，与主报告口径一致）；③ 顶部红色「基座违规」banner 改写为「基座已对齐」绿色 banner；④ §七 降级结论同步升级。
7) **心跳**：每轮写明 B_en_r1 重跑状态（PID / etime / log 大小 / batch / step）；WAITING=1（重跑跑中）；新 r1 落盘 + 报告刷新 + commit/push 完成后写 done_all + WAITING=1 等下一条指令。
8) **红线**：不 kill 编排器/loop；不碰 trace 原文（旧 B_en_r1 batch 目录保留）；不占沙盒（designflow 线不抢）；不改别线；不 clean/reset/stash 别线未提交改动（designflow 线 dirty tree 非本线）。

[用户令 · 2026-11-11 22:4x · 已交付 · 降级为历史参照]
用户原话："抽样的结果只做参考，跑完再说。不许因为抽检思维链漂回英文而停止评测。坚决把评测执行到底。RU之后，regrade zh r2.再之后重跑 zh r3"

执行口径（严格按顺序，不许改序）：
1) 评测不许停：B_ru_r1/r2/r3 必须全部跑完（30/30）。抽检报告只是参考；不得因 en/es/fr/ru 思维链漂回英文而 kill 编排器、暂停轮次、提前收口或改编排器；WAITING 不得因此置 1。
2) 现有编排器 PID 3675162 继续跑；B_ru 三轮完成前不做任何会打断评测的动作（不抢沙盒、不改 trace、不重跑其他臂）。
3) RU 三轮全部结束后，按此顺序执行：
   - 先 regrade B_zh_r2：用已存 completed_code_generation_2026_1110_073833.jsonl 原地补分；补分后原位替换 run/ablation_think_lang_results.json 的 B_zh_r2（旧 pass=null）；原 batch/trace/日志保留不删。
   - 再重跑 B_zh_r3：起新 batch；旧 r3（78.5%）标 SUPERSEDED 留档，不删；新 r3 完成后更新 results JSON 与 cost 字段。
4) 重跑 r3 的配置：先按与 B_zh_r1/r3 相同的现有配置跑（不改 prompt、不改基座），保证可比；"基础 prompt 强制中文 / 基座不恒定"的修法另开令，不许在本次重跑里顺手改口径。
5) 报告：30 轮 + regrade + 新 r3 全部落盘后，才按 report_zhulong_lang_switch_audit_zh.html §5.3 做降级改写；当前不动报告、不新增 divergent 产物。
6) 每轮心跳必须写明：当前轮次/30、编排器 PID、B_ru 进度、B_zh_r2 regrade 状态、B_zh_r3 重跑状态；WAITING 不得因抽检结论置 1。
7) 红线：不 kill 编排器/worker/gap-grabber（除明确的 regrade/重启流程）；不碰 trace 原文；不占沙盒；不改别线。


> 🔍 **用户令 · 2026-11-11（最高优先 · 评测期间做）：抽查 B 轴 trace，验证思维链真的换了语言**
>
> **用户原话**：「让zhulong agent在评测过程中看看 思维链语言消融（B）的现有trace，抽查一下，看看思维链是否遵循prompt改成了指定语言。」
>
> ### 0. 为什么现在必须做（现有证据链是弱的）
>
> 本任务书本来就写着两条要求，但**从未真正执行**：
> - §轴 B L98：「**抽 3~5 条 trace 核对思维链真的换了语言**。未生效 ⇒ 停下修注入」
> - §4 P3 L115：「**每语言先抽 3 条 trace 核对语言真切换**」
>
> 而 MEMORY 里一路写的「lang hint 生效 ✅」，证据只有：
> - ❌ 「log 里看到一句 `Piensa en español`」——**这只能证明 prompt 注入了，不能证明思维链是法语**
> - ❌ 「1791 行重音字符」——**数量不能证明是法语思考，可能是复述 prompt**
>
> ⇒ **B 轴（en/zh/es/fr/ru 五语言）的全部结论目前建立在这个弱证据上。若思维链其实没换语言，B 轴 15 轮的结论全部作废。**
>
> ### 1. 抽查对象：直接读已存档的 trace
>
> 路径（已由 §3 Trace 保留机制落盘）：
> ```
> /nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang/<TAG>/<batch>/
> ```
> 已有 TAG（截至 11-11 10:35）：`B_es_r1` `B_es_r2` `B_es_r3` `B_fr_r1`（跑中）· `B_zh_r1` `B_zh_r3`（`B_zh_r2` 待 regrade）· `A_*` 系列
> 每轮 trace 应 ≥158 个（与题一一对应）；cline session 在 `~/.cline/data/**`
>
> 读之前先在 .75 上 `ls -dt .../trace_ablation_think_lang/*/` 确认真实目录名与体量。
>
> ### 2. 抽查方法（**每语言至少 5 条**，不足则如实记）
>
> 对 **es / fr / zh / en** 四个已完成的语言（ru 若已跑也加上）：
>
> 1. **从 trace 里抽出模型的 reasoning / thinking 段**（不是 prompt、不是最终答案）。
>    - 若 trace 是 JSON：找 `reasoning_content` / `thinking` / `thought` 字段
>    - 若是纯文本：定位 thinking 块的起止标记
> 2. **逐条判定「思维链主体语言」**，四分类（不许只写"是/否"）：
>    - `TARGET`：**主体**是目标语言（如 es 轮的思维链主体为西班牙语）
>    - `ENGLISH`：主体是英语（**未遵循**，即使个别词是目标语言）
>    - `MIXED`：两种语言实质混用（记大致比例，如「70% es / 30% en」）
>    - `COPIED_PROMPT`：只是在复述/翻译 prompt 那句语言指令，其余思维链仍是英语
> 3. **同时核一件事**：答案/代码部分是否仍是英语（预期：**是**，因为只要求思维链换语言；若答案也变成目标语言，说明注入影响了输出，需单独记）。
>
> ### 3. 判定阈值（写进报告）
>
> - **语言真切换**：≥5 条里 **≥4 条**为 `TARGET` 或 `MIXED`（且 MIXED 必须目标语言占多数）
> - **部分生效**：≥5 条里 2–3 条 `TARGET`/`MIXED`
> - **未生效**：≥5 条里 ≥4 条为 `ENGLISH` 或 `COPIED_PROMPT`
> - ≥5 条里出现 `COPIED_PROMPT` ⇒ **必须在报告里点名**（这正是"以为生效其实没生效"的典型）
>
> ### 4. 交付
>
> **产出**：`reports/report_zhulong_lang_switch_audit_zh.html`（中文 · 单文件自包含 · 内联 CSS · 零外链）
>
> 必含 5 节：
> ① **结论一句话**（每个语言：真切换 / 部分生效 / 未生效）
> ② **抽查表**：`语言 | TAG | 样本数 | TARGET | MIXED | ENGLISH | COPIED_PROMPT | 判定 | trace 文件路径`
> ③ **原文片段**：每语言贴 **≥2 段思维链原文**（截 80–150 字，标注来自哪个 trace 文件），让人能自己判断
> ④ **答案部分核查**：答案/代码是否仍英语（避免把"输出变外语"误当"思维链变外语"）
> ⑤ **影响评估**：若某语言判为「未生效」或「部分生效」，**明确写出 B 轴对应轮次的结论是否要作废**
>
> ### 5. 边界
>
> - 🚫 **不打断在跑的评测**（`B_fr_r1` 跑中）：只读已存档 trace，**不许 kill / 不许改编排器 / 不许抢沙盒**
> - 🚫 **不改 trace 原文**，只读
> - 🚫 不改论文、不改其他线产物
> - 抽查用只读命令（`ls` / `cat` / `head` / `grep` / `python3` 读文件），**不许写 /nasdata 下的 trace 目录**
> - 若某语言 trace 已不存在（被清）⇒ 记 `BLOCKED(trace_missing)`，**不许凭 MEMORY 里的旧描述当作已验证**
>
> ### 6. 与现有最高优先令的关系
>
> 本条**不取代**「轮间空档补 `B_zh_r2` regrade」令；两者并行：
> - **regrade 优先**（有空档就跑）
> - **本文抽查**在等空档的间隙做（只读，不占沙盒，可与 eval 并发）

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认维护既有报告（原地覆盖）；用户点名或里程碑才新增，产物落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

> 🚨 **本轮最高优先（2026-11-10 21:3x 用户令，方式 A）：在「轮间空档」把 `B_zh_r2` regrade 跑掉。**
> 取代 20:46 那版"趁 r3 跑中"的令（r3 已于 20:35:26 DONE=78.5%，编排器自动起了 `B_es_r1`）。
> **不再等编排器整体退出**（那要 ~2 天），但也**不许**在轮内硬闯。
>
> **零、先算清楚可用窗口（这决定 A 成不成）**
> 编排器 `run_think_lang_ablation.sh` 每轮 = `timeout 43200 bash scripts/run_cline_script.sh -p 8 -n`
> **前台串行**；轮结束到下一轮开始之间只有：评分 grep + trace 拷贝（~430MB）+ `probe_quota`，
> **通常几十秒**（quota 耗尽时 `probe_quota` 会 `sleep 300`，那是唯一的大窗口）。
> ⇒ 所以 A 的实现必须是「**抢空档 + 一发现新轮起来就自动让路**」，不能是"排队等整轮跑完"。
>
> **一、改写手（唯一允许的改法；已有一版等编排器退出的，作废）**
> 把 `run_B_zh_r2_regrade_wait.sh` 改成 `run_B_zh_r2_regrade_gap.sh`，逻辑：
> 1. `while :; do`
> 2. **空档判定**：`! pgrep -f '^bash scripts/run_cline_script'` 且 `! pgrep -f 'run_eval.py'`
>    → 再 `sleep 20` 复验一次（20s 内没新轮才算真空档；**最多重试 3 次机会**）。
> 3. **独占启动**：`bash run_B_zh_r2_regrade.sh`（`-p 2`，别用 -p 8）后台跑，记 PID。
> 4. **避让守护**（关键）：每 60s 检查
>    `pgrep -f '^bash scripts/run_cline_script'`。一旦出现（编排器起了下一轮）
>    → **立刻 `kill -TERM <regrade_pid>`**，日志写 `ABORT: new round appeared at <ts>, gap too short`
>    → 回到步骤 1 等下一个空档（计入已用机会数）。
> 5. 3 次机会都没跑完 → **降级为 B**：改等编排器 PID 退出再跑（原 waiter 逻辑），
>    并在 MEMORY 明确写 `upgraded-to-B: 3 gaps too short`。
> 🚫 不许 `pkill -f run_cline_script`、不许 kill 编排器/worker、不许用 `exec -a` 之类
>    伪装进程名去骗编排器的互斥检查（会被它自己的兜底 `pkill` 误杀，反而更乱）。
>
> **二、跑法与闸门（沿用 20:46 那版，不变）**
> - regrade 脚本 = `run_B_zh_r2_regrade.sh`（复用 `run_A_none_r2_regrade.sh`，`GEN_FILE=completed_code_generation_2026_1110_073833.jsonl`）。
> - 三个老坑：benchmark 文件名**小写 p**（`EDA-Eval-pyAether-158.jsonl`）、`run_eval.py` 读
>   `EVAL_ROOT_DIR`（非 `_OVERRIDE`）、必须 `unset http_proxy` + 设 `NO_PROXY`。
> - **闸门**：`n_tasks` 必须 == **158**；否则 BLOCKED，不许填数。
> - 回填：`ablation_think_lang_results.json` 里 `tag=B_zh_r2` 的 null **原位替换**（`len(rounds)` 仍 20）；
>   `extract_cost.py --batch <regrade batch> --log <log> --out cost_B_zh_r2.json`。
> - 合理性：r2 应与 **r1=84.2% / r3=78.5%** 同量级；差 >15pp 先查 benchmark 选错。
>   ⚠️ 现在有了 r3=78.5%，**r1/r3 已经差 5.7pp**，报告里必须按三轮均值±std 讲，别只报 r1。
>
> **三、收尾**
> - MEMORY 进度 `21/30（r2=null 待 regrade）` → `22/30（r2 ✅ pass=X%）`，并记：用了几次空档、
>   是否降级 B、regrade 实际耗时、n_tasks。
> - commit 只含 `doc/ZhuLong_DAC2027/run`（脚本 + MEMORY + daily）；results json 被 gitignore。
> - `WAITING` 保持 `1`（es_r1 仍在跑）。
> - **本轮只做这一件**：不起新轮、不动报告生成器、不碰其他线。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准（本线消融实验的基座/题量/协议口径不受其影响）。


### 🔴 用户令 · 2026-11-07 08:3x（**两轴消融：cline `--thinking` 档位 × 思维链语言** · 测试集 **EDA-Eval-PyAether 158** · 中文 HTML 报告须含**分数 + 成本**（墙钟/token））· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「安排 zhulong agent 做如下消融实验：测试集 EDA-Eval-PyAether（158）。1. 变化 cline 的 thinking 参数：None、Low、Medium等。2. 变化 cline 思维链使用的语言：中文、英文、西班牙文、法文、俄文等，可以通过修改任务提示实现，比如：'请使用XX语言思考'。实验后生成中文 HTML 报告。包含对比表格，不光含不同变体的分数，还应包含成本，比如墙钟、token 等。」

**基座（用户 2026-11-07 明确：GLM-5.3-Flash 或 GLM-5.2，二选一）** —— ⚠️ **两轴实验内必须恒定**（否则 thinking/语言效应被基座差异污染），报告首行写明实际用的哪个。

| 选项 | `-m` | `cline auth`（key 可能过期，**开跑前先 `curl` 探针确认 HTTP 200**）| 既有同臂基线（PyAether 158） |
|:--|:--|:--|:--|
| **① GLM-5.3-Flash**（**首选**：额度新、速度稳、与 harness 线现行一致） | `glm-5.3-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f -b http://agi-gateway.cxmt.com/v1 -m glm-5.3-flash` | `B.glm-5.3-flash` = **86.8 ± 1.6%**（5/5，cline CLI）← **本实验的天然对照锚点** |
| **② GLM-5.2**（备选：①额度耗尽/不可用时改这个） | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` | `B.glm-5.2` = **83.3 ± 3.1%**（5/5，cline CLI） |

> 🚫 **不用 `deepseek-v4-pro-fp4`**（额度已耗尽）。🚫 两轴之间不得换基座。🚫 若两个 GLM 都探针失败 ⇒ **报 blocker 停工**，不许擅自换第三个模型。
> 💡 **优先选 ①**：`B.glm-5.3-flash = 86.8±1.6%` 是既有 cline×PyAether 的正式基线，跑出来的 thinking/语言变体能直接与它做 **Δpp + McNemar** 对照；选 ② 也有一致的基线可用。**选哪个都要在报告里把对应基线拉出来做差**，不能只报绝对值。

**其余口径（不可改）**：测试集 = **EDA-Eval-PyAether 158 题**（`EDA-Scripting-Bench 449` 的 PyAether 子集；🚫 不跑 SKILL/Tcl）· harness = `cline` 3.0.51（🚫 不改版本）· 协议 = Pass@1 单次无 retry `-p 8 -n`（与既有消融同口径）· 环境 = `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`，启动 `setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &`，结束判据 `pgrep -f '^bash scripts/run_cline_script'` 无输出，打分 `$BASE_DIR/venv/bin/python scripts/run_eval.py --latest 1` · 每变体 **3 轮**（成本允许则 5 轮与既有臂对齐，报告写实际 n）。


#### 1. 两轴设计 —— ⚠️ **一次只变一个轴，不做笛卡尔积**

> 5 档 × 5 语言 × 3 轮 × 158 题 ≈ 上万次推理，成本不可控。设计 = **基线 + 单轴扫描**：先固定语言=英，扫完 thinking；再固定 thinking=medium，扫语言。若要交互项只补 2~3 个关键格（如 low×中文、high×中文）。

**轴 A · thinking 档位**（`--thinking <level>`）：`A0 none`（若 cline 不接受 `none` 则**不传该 flag**）→ `A1 low` → `A2 medium`（=既有基线）→ `A3 high`（+ 若 `cline --help` 有第 4 档一并测）。
> **P0（≤15min，先做）**：`cline --help | grep -i thinking` 查**真实枚举**，🚫 不许臆造档位名。`none` 若不被接受，用「不传 flag」代表并在报告**明确标注口径差异**。

**轴 B · 思维链语言**（改 prompt 末尾追加一行，不动 harness）：基线 thinking 固定 `medium`。
| 变体 | 注入后缀 |
|:--|:--|
| `B1 en` | `Think in English.` |
| `B2 zh` | `请使用中文思考。` |
| `B3 es` | `Piensa en español.` |
| `B4 fr` | `Réfléchis en français.` |
| `B5 ru` | `Думай по-русски.` |
| （可选）`B6` 对照 | 不加任何语言指令（原样 prompt）= 真实基线 |

> **注入实现**：在送进 cline 的 prompt **末尾追加**语言指令（不删改原题）。建议给 `run_cline_script.sh` 加 `LANG_HINT` 环境变量透传。
> **⚠️ 必须核验**：①日志可见后缀确实进了 prompt ②**抽 3~5 条 trace 核对思维链真的换了语言**。未生效 ⇒ 停下修注入，🚫 别把无效变体跑满 3 轮；确属未生效则标注「该变体未生效」而非当有效数据。

#### 2. 成本指标（用户明确要求，缺一不可 · 口径照抄 `PLAN_RETEST_READBACK_COST.md` §4）

每变体每轮必报，最终给 `mean ± std`：**Pass@1(%)**（通过/158）· **墙钟·单题均值(s)**（逐题 Step3→Step6，**非** batch 总时长）· **Batch 墙钟(h)**（真实 elapsed）· **Token prompt/completion/reasoning/total**（从 cline session `~/.cline/data/**` 或 trace 聚合，给逐题均值 + 总消耗）· **Token/题**（total/158，横向比贵贱）· **¥（可选）**（有公开单价才换算，🚫 不许编造价）· **Timeout 数**（命中 2500s）· **Converged(%)** · **Gen-fail 数**。
> 判据沿用既有十三：`timeout ≤10`、`0 infra`、`0 exec_err`；Pass@1 任何值有效，**不因低分重跑**。
> **reasoning token 必须单独抽**（thinking 档位直接决定它，是解释「高分是否靠堆思考」的关键）。

#### 3. Trace 保留（硬前置 —— 上次 `(N')` 成本就因 trace 被清而丢失）

每轮结束、清理前：`DEST=/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang/<TAG>/<batch>`；`cp -a "$OUT/<batch>" "$DEST"/`（`OUT=.../EDA-Eval-Framework/output_evaluation`），cline session 一并复制。验收：trace 文件数 ≥158（与题一一对应），`du -sh` 记进报告；**不删、不 `git add`**。

#### 4. 执行顺序

1. **P0**：查 thinking 枚举 + 记录基线档；`pgrep` 确认无在跑评测（有则等，🚫 不打断）。
2. **P1 冒烟**：`A0/A2` 各跑 8 题子集（不支持子集则跳过）→ 确认 `--thinking` 真生效（trace 里 reasoning 长度差异）+ 成本抽取脚本跑通。
3. **P2 轴 A 全量**：`A0→A1→A2→A3` 逐档 3 轮，**串行**，每轮即打分 + 落 trace。
4. **P3 轴 B 全量**：固定 `medium`，`B1→B2→B3→B4→B5` 逐语言 3 轮，**每语言先抽 3 条 trace 核对语言真切换**。
5. **P4 报告**。

#### 5. 交付物

- `doc/ZhuLong_DAC2027/reports/report_zhulong_ablation_thinking_language_zh.html` —— **中文单文件自包含，0 script 0 外链**（本线 10-24 常驻规程），必含：①**轴 A 对比表** 变体×{Pass@1, 墙钟/题, Batch 墙钟, prompt/completion/reasoning/total tok, ¥, timeout, converged, gen-fail}，全 `mean±std` ②**轴 B 对比表**（同结构）③**成本-分数象限图**（找性价比最优 / 堆 token 无收益者）④**口径校验节**（thinking 是否真生效 trace 证据 + 各语言是否真切换 trace 原文片段 + `none` 实际实现）⑤**失败归因**（infra/timeout/gen-fail/能力，**infra 单列**）⑥**与既有基线对照**：拉出所选基座的 `B.glm-5.3-flash 86.8±1.6%` 或 `B.glm-5.2 83.3±3.1%`（cline CLI / PyAether 158 / 5-run）做 **Δpp + 配对 McNemar**，逐变体一张小表 ⑦**结论**（边际收益、是否值得改生产配置）。
- 生成器 `run/gen_report_zhulong_ablation_think_lang_zh.py` + 原始数据 `run/ablation_think_lang_results.json`（逐题分数+成本）+ `MEMORY_ZHULONG.md` 心跳 + `daily-memories/` 流水；完成后本行改 `✅ 已交付`。

#### 6. 护栏

🚫 一次只变一轴（两轴同变 ⇒ 效应不可归因）· 🚫 不改 cline 版本/主基座/题面语义（语言指令只追加末尾）· 🚫 不因低分重跑、不用 legacy 数字冒充、不插补缺失轮次 · 🚫 不删 trace，结果 JSON/trace 不入 git · 🚫 不打断其他线（pretrain S1 / vision / data / harness）与在跑评测 · 报告 infra 与能力**分栏**，无效变体必须标注而非丢弃。

> **完成标记**：中文 HTML 报告交付（两表 + 成本列 + 口径校验）⇒ 改 `✅ 已交付`；任一轴未跑完 ⇒ `WAITING: 0`。

---

### 🚨 用户裁定 · 2026-11-05 19:2x（**P0「双盲违规」不成立 —— 论文早已是匿名状态 · 立即闭合**）· 用户直令 · 最高优先

> 用户原话（2026-11-05 19:1x）：「zhulong P0：早已是匿名状态了」

**① 裁定**：撤销长期挂起的「P0 双盲违规仍 OPEN」，**不再等 RUN_ID 143**。运维本地核验（2026-11-05 19:1x，`doc/ZhuLong_DAC2027/ZhuLong_DAC2027/`）：
- `main.tex:1` = `\documentclass[anonymous, sigconf]{acmart}` → anonymous 模式生效（acmart 打印 “Anonymous Author(s)”，且第 54 行注释明确「双盲投稿跳过作者网格改造」）；
- `reference.bib` / `software.bib` 无 `CXMT` / `ChangXin` / `长鑫` 等机构串；无本团队自引（无 `zhulong`/`ZhuLong` 条目）；`liu2025layoutcopilot` / `liu2026agentic` 系**第三方** Liu 姓作者，不构成身份泄露；
- 全部 `.tex` 无 `acknowledg` / `\thanks{}` / `funded` / `grant` 字串。

**② 本轮必做（15 分钟内，写成 1 条心跳）**
1. 把 `MEMORY_ZHULONG.md` 里的 P0 条目改写为 **`CLOSED（2026-11-05 19:2x 用户裁定：早已匿名）`**，并删掉「待运维 RUN_ID 143」表述；§⑧ 跟踪同步改为已闭合。
2. 复核上面 3 条证据仍成立（若 bib 近期有新条目，再扫一次 `CXMT|ChangXin|长鑫|zhulong`），结论 1 行写进心跳。
3. ops inbox 若再出现关于 P0 / RUN_ID 143 的只读回执，只记「已知，已闭合」，不据此恢复阻塞。
4. 若**确实**发现新的可识别信息（作者 / 单位 / 致谢 / 第一人称自引）→ 只做匿名化修正并重编译（`pdflatex×1 + bibtex + pdflatex×2`，ERR=0 / UNDEF=0，页数不变），**不重跑评测**。

**③ 完成标记**：P0 标 CLOSED 且心跳含证据 ⇒ `WAITING: 1`（恢复空巡检）；若发现需改动且未改完 ⇒ `WAITING: 0`。


### 📦 已闭合（batch 15/16，原文见 `ZHULONG_TASK_ARCHIVE.md`）

> 🚨 11-03 21:0x llama.cpp + Qwen3.5-0.8B 安装（smoke 双过）✅ · 11-02 21:3x Tab-3 美观改进（`Tab3_改进建议.html` 已入库，`6_exp.tex` 已落地）✅ · 10-30 22:2x zhulong-full×kimi-k2.6 5-run（**85.0±2.5%**，vs cline 86.8±1.6% Δ−1.8pp）✅ · 10-29 21:5x 论文审阅（92.8KB 报告，P0=1/P1=3/P2=11）✅ · 10-26 08:1x 作废 224219+重跑 glm53-full（已被 10-27 令覆盖）。详情见 archive §batch 15/16。


### 📦 归档指针 · 2026-10-25「按外部评审意见改论文（含 57.4pp 归因硬伤）」· 已执行完毕（10-26 令并行）。要点：改稿须如实标注「待补」及补法，不得编造数字/文献。原文见 `ZHULONG_TASK_ARCHIVE.md`「归档块 · 2026-11-11」。

### 📦 已归档 batch 13 · 2026-10-27（原文见 `ZHULONG_TASK_ARCHIVE.md` §归档 batch 13）

> 以下均已闭合/已被取代，仅留 1 行指针，需要时读 archive：10-26 ops 中继修复（relay PID118463 活，.last_run_id=128）· 10-26 cimi_search/cimi_fetch 挂载（research MCP 可用）· 10-24 23:0x DAC 审稿+改稿方案（41.6KB 报告已交付）· 10-24 19:0x 论文排版（commit 3651b322）· 10-24 22:23 配置对齐（maxTokens 16384→8192，已被 10-26 令覆盖）· 10-24 22:15 已核实事实（RUN_ID 115/117）· 10-24 22:1x 停 cline-full+重跑 5-run（已被 10-26 令覆盖）· 10-24 20:2x cline vs zhulong-CLI 差异归因（25.9KB）· 10-24 15:4x 引用修正（Lemma→Claim）· 10-24 16:1x refs 单独起页 · 10-24 13:0x 执行令（commit d2d9bb7a）· 10-23 22:1x cline×deepseek-v4-pro×full 5-run（**部分活跃·r1 已硬切留证，r2-r5 待裁决**）· 10-23 09:4x 作废 r1-r3+重跑（已被 10-26 覆盖）· batch 10/11/12 更早指针见 archive。
### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
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

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
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
