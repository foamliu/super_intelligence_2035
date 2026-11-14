# BAIZE_HARNESS_TASK.md

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_harness_glm53_7way_swebench_tb_zh.html`、`reports/report_harness_cline_special_zh.html`、`run/harness/gen_report_glm53_7way.py`、`run/harness/gen_cline_special.py`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
   **🔴 `reports/` 只放人读 HTML（2026-11-14 用户令）**：机器逐轮中间产物（`*_<YYYYMMDD>_<HHMM>.json/.log/.txt` 快照、逐题证据、harbor 原始日志）**一律写 `run/harness/terminalbench/manifests/` 与 `traces/`，两处均已 .gitignore**。
   事故复盘：`tb21_cline_quota_rerun_<tag>.json` 曾逐轮写进 `reports/`，随自动提交累积 **27 个 × 1.3k 行**（首犯 `c63912b22` R2391 2026-11-13 19:13），2026-11-14 已 `git rm` 全清。
   提交前自查：`git status --porcelain` 里**不许出现** `reports/` 下的 .json/.log/.txt；`git check-ignore -v <file>` 应命中。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

> 📦 §运维令·2026-11-07 15:2x（TB4 换 TB-2.1 的时限与路径）**✅ 已交付（R1770）** → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：TB4 截止 2026-11-07 未达成「≥1题×≥1路reward非0」(661结果全reward=0=能力·R1743)→16:04 **切换 TB-2.1**→oracle 5/5 PASS✅(break-filter/bn-fit/log-summary/cancel-async/fix-git全reward=1)+7路全量启动(89题×7·/tmp·口径=TB-2.1/89题/7way不可比TB4)+报告 `reports/report_harness_tb21_7way_zh.html` 已交付(含oracle证据/7路矩阵/空patch归因/不可比性说明)。需要时再读。



> 📦 §运维令·2026-10-30 22:2x（把恒为 0 分的 harness 调试跑通）**✅ R988** → `run/ARCHIVE_OPERATOR_HARNESS.md`；hermes 根因=PYTHONPATH 中毒、deepseek 根因=网关 SSE 非标字段+超时 patch 丢弃，均已修复（verify5b 4/5、3/5）。

### 🧷 📛 命名与归档纪律（常驻）
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区，自上而下找第一条「未完成」的指令执行

### ✅ 用户令 · 2026-11-14 08:4x（**解释审计结果的「自相矛盾」**：claude-code Q0/S0 却 0 passed）· ✅ 已交付（R2462）

> **用户原话**：「把【你观察到的『自相矛盾』的审计结果】也派发给 harness，让它给出解释。」

- **要你解释的现象（用你自己的 R2461 审计数据）**：
  | 路 | 额度失败 Q | 假结果 S | Evaluated | TB-2.1 passed |
  |:--|:--:|:--:|:--:|:--:|
  | **claude-code** | **0** | **0** | 89 | **0** |
  | codex | 0 | 5 | 89 | 1 |
  | cline | 0 | 8 | 89 | 38 |
  | opencode | 15 | 23 | 89 | 33 |
  | pi | 0 | 45 | 89 | 27 |
  | hermes | 39 | 43 | 89 | 7 |
  | deepseek | 0 | 48 | 89 | 11 |
- **矛盾点**：claude-code = **0 额度失败 + 0 假结果 + 89 已评测**，却 **0 passed**。按你审计的口径，这 89 题的失败**既不能归因额度、也不能归因假结果**，那么它们**必须**落到"真跑过但失败"或"从未启动但被记成已评测"之一。**这两者含义完全不同，报告至今没有区分，也没有任何一处解释。**
- **对照放大**：同样 S=0 的只有 claude-code 一路；pi（S45）、deepseek（S48）虽有大量假结果，仍有 27/11 passed。**唯一"干净却全零"的样本就是 claude-code —— 这本身是强异常信号，不该被一句「cc 0p 待分析」带过。**
- **要交付（本轮必须出结论，不许留白）**：
  1. **逐题 89 行明细**（可折叠表格）：`task | reward | exception_type | iterations | input/output tokens | stdout 前 80 字 | 归因类别`；
  2. **归因分类饼图/堆叠表**，至少分：①docker/镜像未起 ②适配器异常（鉴权/CLI 解析/SSE）③AgentTimeoutError ④模型有输出但 verifier 判错（真能力）⑤其他；
  3. **一句话结论**：这 89 题里**真正"模型跑过且答错"有几题**？——只有这个数才是 claude-code 的能力结论，其余一律是 infra；
  4. 若判定为 infra，**先重跑再用重跑结果更新报告**；重跑不了就写清 `BLOCKED` 原因与所需资源。
- **同时修正**：`report_harness_tb21_7way_zh.html` 与 `report_harness_cline_special_zh.html` 里所有「cc 0p 待分析」「claude-code 0p」措辞，替换为上面的归因结论 + 证据路径；并在 7 路归因表里给 claude-code 补一列「失败构成」。
- **红线**：🚫 不许写「claude-code 能力差」除非给出 iterations>1 且 token>0 的证据；🚫 不许再出现"待分析"。

---

### ✅ 用户令 · 2026-11-14 08:2x（**报告 `report_harness_glm53_7way_swebench_tb_zh.html` 整改** · 用户判定「不合格」）· ✅ 已交付（R2462）

> **用户原话（逐字转述，共 4 条）**：
>
> 「harness 呈现的报告：`report_harness_glm53_7way_swebench_tb_zh.html` 不合格
> 1.【3. 与 kimi-k2.6-cloud 对照】表格为什么 kimi 的分母是 500，而 glm-5.3 的分母千奇百怪？
> 2.【TB4 — 已闭合】为什么还放在报告里？
> 3.【TB-2.1 — 进行中】这是最新的结果吗？claude-code 只有零分，难道 harness 自己对此完全没有疑问吗？为什么不排查？
> 4.【1. SWE-bench Verified · 7 路 Predict】&【2. SWE-bench Verified · 7 路 Eval 矩阵】为什么把 predict 和 eval 分开，这对于报告的阅读者有任何意义吗？」

> ⚠️ **交接边界（用户 2026-11-14 明确要求）**：下发方（运维/Windows 侧）**没有 tb21 jobs、predictions、eval 的原始数据**，无法复核任何一个数字，**禁止**由下发方推断结论。以下只转述问题；**所有事实核对、口径决定、数字复算，必须由 harness 自己在服务器上用原始数据完成**，并把证据（路径/命令/行号）写进报告与 MEMORY。

- **涉及文件**：`reports/report_harness_glm53_7way_swebench_tb_zh.html`；生成器 `run/harness/gen_report_glm53_7way.py`（模板 L246+、kimi 行 L215-220、`KIMI` 常量 L189、§1/§2/§4 结构 L260-286）。
- **纪律**：🚫 手改 HTML；🚫 拿「中间值/进行中」搪塞；改动须可复算。

**问题 1 · kimi 对照表分母不一致**

- 用户质疑：kimi 分母恒 500，glm-5.3 一路一个分母（"千奇百怪"）。
- 现状（L215-220）：`k_rate=k_resolved/500` vs `g_rate=resolved/n`（n=该路已评题数）。
- 落地其一：a) 统一同分母并写清定义；b) 拆成「已评 N 题 pass%」与「按 500 折算」两列各自标注；c) 确不可比则不做除法比较，并列陈述+说明。
- 自查 `KIMI={...}`（L189）是**硬编码**：核实来源/时点/口径并注明，否则是拿两个基准做除法。
- 交付：表头写清两边分母 + 复算命令 + 一句话结论（该表能否跨行比大小）。

**问题 2 · 已闭合的 TB4 仍在正文**

- TB4 从正文移附录或删，仅留 1 行历史指针（如「R1770 被 TB-2.1 取代，66×7=462 全 reward=0，详见 `run/ARCHIVE_OPERATOR_HARNESS.md`」）。
- 判据：正文 Terminal-Bench 章不再有 TB4 独立小节。

**问题 3 · TB-2.1 是否最新 + claude-code 全零为何不排查**

- 用户对工作态度的直接批评：**0 分不是"已知结论"，是必须归因的异常**。
- ① 复核各路 completed/passed/errored/remaining 是否最新（数据时点、扫描命令、`/tmp` 是否被清理）；② **专查 claude-code**：`/tmp/tb21_glm53_jobs/claude-code/` 逐 trial 看 `result.json`/`exception_info`/`agent_result.metadata`（`run_result`、`iterations`、`stdout`），按 ①从未启动(docker/镜像) ②适配器 bug ③429 ④超时 ⑤真能力差 逐题归类，**每类给证据**；③ infra 判定则**必须重跑并并回**，能力判定则给 iterations/token 证据；④ 一并体检 codex（报告自称 err=适配器）与 hermes（7/53）。
- 判据：该节必须有「claude-code = 0p 归因=<类别> + 证据 <路径>」一行 + MEMORY 心跳；🚫 不许留「0p 待分析」。
- 同时修措辞矛盾：§4.2「claude-code 0p待分析」、§5/§6「已恢复 HTTP 200」与「网关429(历史)」并存。

**问题 4 · predict 与 eval 分作两节，对读者无意义**

- **合并成一节「SWE-bench Verified · 7 路结果」**，列：`Harness | Predict(attempt/500) | Real | Empty | Eval N | Resolved | Pass%(resolved/N) | 状态`；中间态用一行注释，不单开节。
- 顺带清理暴露的矛盾/冗余：§2「各路predict推进中(网关429 blocking)」与页首「网关 HTTP 200」冲突；§8 research 日报输入、§7 硬盘体检是否该留在正式报告（用户未点名，同属"读者无意义"，请判断并给取舍理由）。

**统一交付（4 条一次 REGEN）**

1. 改生成器 → REGEN → 体积/0外链/0script 自检；2. 每条结论可追到原始文件（路径+复算命令）；3. MEMORY 心跳一行：`报告整改 R2462: ①kimi分母=X ②TB4降附录 ③cc0p归因=Y(证据Z)+重跑N ④§1§2合并`；4. 做不到就写 `BLOCKED: <原因> + 需求`，🚫 不许糊。
5. **体积**：本轮先按 §工作约定 把已闭合的 §运维令/流水块 fold 进 `run/ARCHIVE_OPERATOR_HARNESS.md`，再做整改。

---


### 🟡 用户令 · 2026-11-14 08:0x（**TB-2.1 七路「网关 Token 额度耗尽」诊断 + 按需重跑（含 other-6 路与 synthetic 假结果）**）· A+C ✅ / B 脚本就绪待跑

> **R2461 进度**：**A ✅ DONE**（`audit_tb21_quota_7way.py` 创建+运行→7路五桶落盘 `reports/tb21_quota_audit_7way_20261114_0802.json`：cline=Q0/S8·codex=Q0/S5·opencode=Q15/S23·cc=Q0/S0·pi=Q0/S45·hermes=Q39/S43·deepseek=Q0/S48·rerun_targets=226）·**C ✅ DONE**（`gen_report_tb21_7way.py` 增 7路归因表+旧 cline 结论作废戳+38/89 现口径·双报告 REGEN✅）·**B 脚本就绪**（`rerun_tb21_7way_quota.py` 编排器 dry-run OK·226 targets·等 train-fasttext + 5th-batch 跑完启动）。

> **用户原话**：「安排 harness 查一下，cline 和其他 harness 是否仍然有（网关 token 额度耗尽）导致失败的 Case，有则重跑。现在是周末。」

- **下发时的现状（08:0x 复核，勿重复劳动）**：cline 侧 `quota_lost` 已 = **0**（R2460：main+2nd+3rd+4th-batch ALL MERGED，cline=38/90=42.2%）；R2460 另发现 **8 个 synthetic placeholder**（2nd-batch 来源 `rerun_2nd_batch_synthetic`、`has_run_result=false`、`stdout=0` ⇒ **agent 从未真跑**）已起 5th-batch。**⇒ cline 的「额度」问题已闭环，本令剩余价值只在两处：① 其他 6 路从未做过额度口径归因；② 用同一口径复核「假结果/未真跑」是否也存在于其他路。**
- **范围（勿扩大）**：只做 **TB-2.1 / 89 题 / 7 路**。**SWE-bench 侧不查不跑**（cline 专项 C2 已证：网关额度 429 = 0 题 0.0%，66 个失败 100% 能力）。

**A. 诊断（必做，只读）— 覆盖全部 7 路，而不是只有 cline**

1. 新建 `run/harness/terminalbench/audit_tb21_quota_7way.py`：对 **7 路**逐路扫 `/tmp/tb21_glm53_jobs/<harness>/` 的 dated 子目录 `result.json`（过滤口径同 `gen_report_tb21_7way.py::count_route`：`"/20" in str(f)`）。
2. 判定口径**逐字复用** `rerun_tb21_cline_quota.py::classify` 与 `gen_report_tb21_7way.py::_cline_attrtribution`：stdout 含 `额度已用完` 或 `Token额度` ⇒ quota trial；**task 级 `best_reward<1.0` 且全部 trial 均 quota ⇒ `quota_only`**。
3. 关键新增（R2460 教训）：额外标出 **`synthetic_or_never_ran`** —— `agent_result.metadata` 无 `run_result`（或 `stdout` 长度=0 / `"run_result"` 不在 stdout）且 reward<1.0 的 trial → 这**不是能力，也不能算额度**，是「**假结果/未真跑**」，需单列并进重跑队列。
4. 每路四桶 + 一标记，落 `run/reports/tb21_quota_audit_7way_<tag>.json`：`quota_only_tasks` / `mixed_fail_tasks`（不重跑）/ `ability_fail_tasks` / `synthetic_or_never_ran` / `not_evaluated`（89−evaluated，**先补跑非重跑**）。
5. MEMORY 心跳写一行汇总：`7路 quota_only: cline=0 · pi=? · opencode=? · deepseek=? · hermes=? · codex=? · cc=? | synthetic: <各数> | evaluated: <各值>/89`。

**B. 重跑（只跑 A 里非空的桶；空的就记「0」不跑）**

1. 前置：`curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9092/v1/models` = 200；确认**无 SWE-bench predict 抢同一额度池**（周末窗口独占）；S1 训练（10.239.2.29 pretrain）不挤；`df`/`nvidia-smi` 自检照常。
2. 排队顺序：**5th-batch（8 synthetic）先跑完** → 再跑本次审计新增的 `quota_only`/`synthetic` 题；**逐路串行，一路 merge 完再起下一路**（避免 R2454 踩过的 cline-hub 冲突）。
3. cline 路：沿用 `rerun_tb21_cline_quota.py --launch`（判定口径不许改）。
4. 其他路：把 `rerun_tb21_cline_quota.py::launch()` 的 `HARNESS`/`AGENT` **参数化**（新增 `--harness <name>`，或另建 `rerun_tb21_quota_7way.py`，**沿用其 judge/merge/落盘逻辑**），agent 映射照抄 `launch_tb21_glm53_7way.sh:67-73`：`codex=terminalbench.agents.codex:CodexTB` · `hermes=…hermes:HermesTB` · `opencode=…opencode:OpenCodeTB` · `claude-code=…claude_code:ClaudeCodeTB` · `deepseek-harness=…deepseek_harness:DeepseekHarnessTB` · `pi=…pi:PiTB`。
5. 参数不得放宽：`-k 1`、`--n-concurrent 1`、`nice -n 19`、`TB_AGENT_TIMEOUT=3600`、`sg docker` 兜底、jobs-dir=/tmp。
6. 跑完：`--merge /tmp/tb21_glm53_jobs/<harness>_rerun_<tag>` → `gen_report_tb21_7way.py` + `../gen_cline_special.py` REGEN → commit（`harness:` 前缀，只 add 本线路径）。

**C. 报告口径修正（本轮必做）**

- `gen_report_tb21_7way.py`：① 额度归因从 cline 单路扩为 **7 路表**；② 顶部「结论一句话」改**数据驱动**（合计 0 时写「无额度失败；失败=timeout/ability/假结果」）；③ 旧文字「主因=额度耗尽…原始 10/89=11.2%…公平 40%」加「~~作废~~ 见 R<本轮>」时点戳，并补 R2460 后的 38/90=42.2% 现口径。
- `report_harness_cline_special_zh.html` 的 TB-2.1 段（仍写「65 题 81%…公平 40%」）同步改「已清 0 + 现 38/90」。
- 🚫 不手改 HTML，改生成器后 REGEN。

**D. 判据**：重跑前后 `quota_lost` 与 `synthetic` 题数、各路 passed/fair-pass **同框**写进心跳；重跑后仍 0 分的题必须给**非额度证据**（iterations/exception_info/finishReason），否则不得下能力结论；`synthetic` 重跑后若仍无 run_result ⇒ 报 infra bug，禁写「模型不会」。

**E. 红线**：🚫 不改 SWE-bench 口径/数字；🚫 额度失败≠能力、假结果≠能力（三者必须分开记账）；🚫 同题多 trial 只按 unique task 计一次；🚫 不放宽 timeout/并发刷分；🚫 无实测 `http_code`+trial 证据不得断言「额度已恢复」。

**F. 落盘**：`run/reports/tb21_quota_audit_7way_<tag>.json` + `run/reports/tb21_quota_rerun_7way_<tag>.json` + `run/harness/terminalbench/traces/tb21_quota_rerun_7way_<tag>.log` + MEMORY 心跳 + 双报告。

**G. 节奏**：本轮先做 **A+C**（诊断+口径，纯只读/生成器），把 7 路清单落盘；**同轮内网关 200 且无 predict 竞争就顺势进 B**（周末额度补充窗口，别拖到工作日）。不能跑就写 `BLOCKED: <原因> + 清单已落盘`，不许空转。
**H. 体积提示**：本令下发时 `MEMORY_HARNESS.md` 已 31.4KB（贴 32KB 上限）⇒ 本轮先按 §工作约定 把已闭合的 R24xx 流水 fold 到 `daily-memories-harness/`，再写心跳。

---

### ✅ 用户令 · 2026-11-13 18:2x（**TB-2.1 cline「网关 Token 额度耗尽」失败重跑**）· ✅ 已交付（R2460）

> **结论**：cline TB-2.1 额度重跑已完成——main+2nd+3rd+4th-batch ALL MERGED·quota_lost=65→**0**✅·cline=**38/89=42.7%**（原始 10/89=11.2%→公平 10/25=40%→现 38/89=42.7%）。8 synthetic placeholder tasks 已起 5th-batch（chained after train-fasttext）。**已被 11-14 08:0x 七路令取代**（A+C 已扩为 7 路口径）。

> **用户原话**：「harness：回顾一下 cline 失败的 case，如果是【网关 Token 额度耗尽】就重跑。」

- **范围（已核对，勿扩大）**：SWE-bench 侧 cline 295/295 real、0 empty，C2 66 个失败 **100% 能力**（R2300 报告）⇒ **无额度失败可重跑**；重跑只针对 **TB-2.1**：R2386 已结案 10/89=11.2%，80 个失败 trial 里 **65 个（81%）** 是网关额度耗尽（stdout「本次Token额度已用完」/iterations=1），公平通过率 10/25=40%。
- **工具**：`run/harness/terminalbench/rerun_tb21_cline_quota.py`（判定口径与 `gen_report_tb21_7way.py::_cline_attrtribution` 完全一致：best_reward<1.0 且**全部** trial 命中额度 ⇒ 重跑；有任一非额度 trial 的题不动）。
- **执行**：
  1. `cd run/harness/terminalbench && python3 rerun_tb21_cline_quota.py`（dry-run，落 `run/reports/tb21_cline_quota_rerun_ids.txt` + `run/reports/tb21_cline_quota_rerun_<tag>.json`）
  2. 确认网关 200（`curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9092/v1/models` = 200）后：`python3 rerun_tb21_cline_quota.py --launch`
  3. 跑完：`python3 rerun_tb21_cline_quota.py --merge /tmp/tb21_glm53_jobs/cline-patched_rerun_<tag>` → `python3 gen_report_tb21_7way.py` + `python3 ../gen_cline_special.py` 双报告重生成。
- **判据**：重跑前后 `quota_lost` 题数、cline TB-2.1 passed（基线 10/89）与 fair pass（40%）同框写进 MEMORY 心跳一行；重跑后仍 0 分的题必须给**非额度证据**（iterations/exception_info），否则不得下能力结论。
- **红线**：🚫 不得改 SWE-bench 口径/数字；🚫 不得把额度失败记成能力；🚫 同一题多 trial 只按 unique task 计一次。
- **落盘**：`run/reports/tb21_cline_quota_rerun_<tag>.json` + `run/harness/terminalbench/traces/tb21_cline_quota_rerun_<tag>.log` + MEMORY + 双报告。

---

### ✅ §用户令 · 2026-11-13 15:5x（**排查 TB-2.1 cline 低分根因**）· ✅ 已交付（R2386）

> **根因结论**：cline TB-2.1 = 10/89 = 11.2% 低分 **非模型能力**。主因 = **网关 Token 额度耗尽**（「本次Token额度已用完，请等待X分钟后重试」）占 80 失败中 **65 题 (81%)**，cline run_result finishReason=error / iterations=1 / tokens=0 → 零工作 → reward=0。**cline 适配器无 retry/backoff**（rerun factor=1.0x），而 pi=2.0x（每题重跑）、opencode=1.3x（部分重跑）→ 额度恢复后重跑成功。公平通过率 10/25=40%。修复建议：① 适配器加 quota-error retry-with-backoff；② 额度充足时单独 rerun（预计 ~30-40%）。**值得 rerun**。
> **证据**：`/tmp/tb21_glm53_jobs/cline-patched/` 下 90 个 result.json 逐题分析；trace 含「本次Token额度已用完」原文；rerun factor 对照 pi/opencode。双报告已增补 TB-2.1 归因小节（含 rerun factor 对比表）。

---

### ✅ §用户令 · 2026-11-12 16:3x（**给两个基准的 ETA**）· ✅ 已交付（R2279）

> **ETA结论**：① **TB-2.1 = 已交付**（100p/750t, 7路≥89tasks, 全部done）；② **SWE-bench Verified = ~15天**（瓶颈=codex 374剩余@25/天, 预计 2026-11-27）。
> **复算方法**：ETA=剩余题数÷3日平均速率(由 predictions_glm53/ 文件mtime统计)。各路拆分：cline 213剩余@49/天≈4天·codex 374剩余@25/天≈15天(瓶颈)·opencode 5剩余≈0天·cc 224剩余@49/天≈5天·pi 249剩余@51/天≈5天·hermes 51剩余@44/天≈1天·deepseek DONE(500attempted,325empty=能力,今日0产出)。eval已追上(incr_eval,0 true backlog)。网关200(curl实测)·429风险仍存(历史反复)。
> **落盘**：MEMORY心跳第一行含两ETA数字 + 双报告新增§9 ETA节(`reports/report_harness_glm53_7way_swebench_tb_zh.html` + `reports/report_harness_cline_special_zh.html`) + 生成器脚本已更新(gen_report_glm53_7way.py + gen_cline_special.py)。

---

### 🔴 用户令 · 2026-11-07 10:10（**按早晨令继续评测；cline 专项加盯**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「harness：按早晨的用户令评测，同时多关注一点 cline。」

#### 1. 主线不变（照 08:1x 令执行，不另起炉灶）

1. 代际审计令（Kimi -> GLM-5.3-Flash、SWE-bench Lite -> Verified、TB2 -> TB4）：代际矩阵表 + 可继承/可修改/应废弃逐项落地；
2. 目标：**消灭 TB4 全 0 passed**（先 1 题 x 1 路验 verifier 非结构性 0，再 oracle 必须 1.0）；
3. §22:4x 两基准 7 路全交付；SWE-bench Verified full500 每路推进到 500；
4. 已知硬故障 `deepseek` `gw_proxy_dsh:9093`（1.1s 空 patch）：继续诊断，修好后重启该路。

#### 2. cline 专项（本轮新增重点，独立考核）

| 序号 | 要求 | 判据 |
|:--|:--|:--|
| C1 | **独立统计** cline 的 real patch / empty patch / 每题耗时分布 | 数字可从 trace 复算，给出复算命令 |
| C2 | **失败原因分类**（适配器 / 网关额度 429 / 上游 5xx / 能力 / 超时 / 格式不可解析 / 环境依赖），逐条可追溯到 trace 文件 | 分类占比之和 = 100%，留 top3 样本原文 |
| C3 | 确认 R1733 定位的 resume 判定问题修复后，**cline 空 patch 是否归零** | 未归零必须给根因证据（trace + 日志行） |
| C4 | 每轮心跳含**一行 cline 专项小结**（real/empty/失败 top1） | 缺该行视为未执行本令 |
| C5 | cline 专题 HTML 报告：固定文件 `reports/report_harness_cline_special_zh.html` **原地覆盖**（🚫 禁止 `_rXXXX` 新文件），写清与 hermes/opencode 的差距来源 | 报告在 `reports/`，自包含、0 外链 |

> 📛 命名纪律照旧：报告正文一律写 `cline`，禁止任何 `cline-patched` 变体。

#### 3. 归因红线

- 网关额度耗尽 / 上游 429 **不得**写成"模型能力"结论；
- 能力差（真实做错）也**不得**用"基础设施问题"掩盖；两者必须用 oracle + trace 证据区分。
- cline 若 REAL patch 明显低于其他路，必须给出**可检验假设 + 下一步实验**，而不是只报数字。

---


### ✅ §用户令·2026-11-07 08:1x（评测脚本代际审计）· ✅ 已交付（R1739）

> 📦 §用户令·2026-11-07 08:1x（评测脚本代际审计：Kimi→GLM-5.3-Flash · Lite/TB2→Verified/TB4）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：代际矩阵报告已交付(17.8KB)·oracle=1.0×3(verifier正常)·TB4全0=429+合理失败(运维预判overlay根因=错误)·resume bug已修(size>50B→model_patch非空)·空patch 51.5%→6.9%。需要时再读。

---

### 🔴 §用户令·2026-11-06 22:4x（glm-5.3-flash 重测：SWE-bench Verified + Terminal Bench 4.0 × 7 路）· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「harness：用 glm-5.3-flash 重新测试 (SWE-bench Verified + Terminal Bench 4.0) x7」
>
> **口径（不可改）**：backbone 统一 **glm-5.3-flash**（gateway `http://agi-gateway.cxmt.com/v1`，key 用 `launch_glm53_7x300.sh` 里的 `GLM53_KEY`；开跑前先 curl 探针确认 HTTP 200，非 200 不许开跑）；7 路 = cline / codex / opencode / claude-code / pi / hermes / deepseek-harness；**两个基准都要跑满 7 路**。
>
> **基准 A · SWE-bench Verified（500 题，非 Lite）**
> - 复用既有 full500 链路（`run/harness/swebench_verified_full/run_verified_full.py` + `jobs_*/`），只把模型注入切到 glm53：cline 直连 gateway；codex / opencode / claude-code / pi / hermes 走 gw_proxy **9092**；deepseek-harness 走 gw_proxy_dsh **9093**（**照抄** `launch_glm53_7x300.sh` 的 Step1–Step2 配置块，不要重新发明）。
> - 7 路**限并发/串行**（沿用 chain 脚本的 CPU 护栏），每路跑完即 eval；进度按 **100 / 300 / 500** 三段汇报。
> - 结果落 `swebench_verified_full/reports/eval_glm53_<harness>_*.json`；🚫 结果 JSON 不入库（硬约束③）。
>
> **基准 B · Terminal Bench 4.0**（✅ 已核实可得：`~/terminal-bench-4.0` **66 题**，镜像已齐，7 路 smoke 全通——见 §08:1x 令）
> - 走 `terminalbench/launch_tb4_glm53_full.sh`，7 路全量。⚠️ **但当前全 0 passed 是 verifier infra 问题，非模型问题**，先按 §08:1x 令 P0 修 verifier 再跑全量。
> - 若 verifier 修不动 ⇒ **如实上报 RED**，并仍交付 2.0 × 7 路作对照基线，报告**必须显著标注「版本=2.0」**，🚫 不得把 2.0 写成 4.0。
>
> **交付物**：`reports/report_harness_glm53_7way_swebench_tb_zh.html`（中文单文件、0 script 0 外链；含 ①7×SWE-bench Verified 矩阵 ②7×TB 矩阵 ③与 kimi-k2.6-cloud 历史结果同口径对照 ④TB 版本核实结论与分母口径 ⑤失败归因，infra 单列）+ 生成器脚本 + 本线记录（`MEMORY_HARNESS.md` 心跳 + `run/harness/` 下的进度日志）。
>
> **护栏**：CPU 单进程 >80 核立杀（eval 题重跑）、内存同 10-30/11-02 令；🚫 结果 JSON 入库；报告里写 `cline` 不写 `cline-patched`；每路跑完即 commit（`harness glm53:` 前缀）；TASK/MEMORY ≤32KB。
>
> **带件（用户 22:5x）· 硬盘体检**：开工前先 `df -h /data /` + `docker system df`，算清 **TB 4.0 / SWE-bench 镜像预估占用 vs /data 余量**，写进报告一节；不足则给**清理候选清单**（🚫 不得擅自删他人数据 / 他线镜像）。
> **完成标记**：两基准 7 路全交付后本行改 `✅ 已交付`；未交付 ⇒ `WAITING: 0`。

> 📦 历史已闭合指针（原文见 ARCHIVE）：10-28 19:1x+20:0x（结果 JSON 不入库 → R584 `git rm --cached` 15 个；**③ 硬约束仍生效**）· 10-28 12:0x（TB 7way 整改）· 11-04 13:5x（修适配器 → cline **356/500=71.3%**）· 11-04 13:1x（cline 326 vs opencode 401）· 11-06 17:1x（差距 86% 为能力差，p=6.27e-08）。
### 🚀 运维令 · 2026-11-02 11:2x（**自检同时盯 CPU：本线评测进程 CPU 不许失控，容器内失控用 sudo/docker kill**）· 用户直令 · 最高优先

> 用户原话（2026-11-02 11:2x）：「让 harness 持续关注自己的评测进程，不光内存，CPU 也不能超过 80%。」

**① 背景（运维已核）**：11-02 harness **eval 阶段**失控——sklearn 一个 pytest 吃掉 **185 核**（`%cpu=18500%`），整机 load 顶到 234/224，抢 S1 训练 CPU。**两个新事实**：① 是 **CPU 失控**（n_jobs 失控拉起全 224 核）而非内存；② 跑在 **eval 容器内**（`containerd-shim-runc-v2` + `/opt/miniconda3/envs/testbed`）⇒ 普通 `kill -9` 杀不掉（EPERM），必须 `sudo kill -9` 或 `docker kill <容器id>`。

**② CPU 硬判据（每次唤醒自检，与内存并列，先于一切业务）**：
- `ps -eo pid=,ppid=,pcpu=,rss=,args=` 检查**本线**评测进程（predict 的 7 路 agent + eval 容器进程）CPU。
- **单进程 `%cpu` 持续 > 8000%（=80 核）→ 立即 kill**；或**整机 CPU busy 被本线评测顶到 >80%**（≈179/224 核，`top` 的 %Cpu 判断）→ 定位最高 CPU 的本线进程 kill。
- **杀法**：宿主机进程用 `kill -9`；**容器内进程（父链含 containerd-shim/runc 或路径含 `/opt/miniconda3/envs/testbed`）必须 `sudo -S kill -9` 或 `docker kill <id>`**（运维已留 sudo 密码）。

**③ 杀掉后果处理**：eval 题 → **该题重新 eval**（predict 结果不丢）；predict 题 → **重新 predict**；每次 kill 记录 `harness 内存/CPU:` 心跳 + 题目即时重跑。

**④ 纪律**：只清本线，🚫 不碰 S1 训练 / vision / data / zhulong；心跳写 `未完成指令：有` ⇒ `WAITING: 0`；commit `harness 内存:`。

### 🚀 运维令 · 2026-10-30 11:1x（**唤醒后首事：自检本线评测进程内存，失控先杀再重测**）· 用户直令 · 最高优先

> 用户原话（2026-10-30 11:1x）：「这些 agent 不是应该在容器中运行吗？内存过高可否限制？…harness 唤醒后先看看自己的评测是否占用过多内存，如果是，先杀掉，再想办法重测。」

**① 背景（运维已核）**：10-29 cline 路在 `.29` **宿主机**上跑 SWE-bench sympy 时失控——`list(partitions(200))` + `pytest test_fancysets.py` 吃掉 **~1.2TB** 内存，威胁 S1 训练（运维已 kill）。**predict 阶段跑在宿主机（非容器），不受内存限制**＝根因。

**② 硬要求（每次唤醒第一件事，先于一切业务）**：
- `ps -eo pid=,ppid=,rss=,args=` 检查**本线**评测相关进程（predict 的 cline/codex/opencode/pi/claude-code/hermes/deepseek 及其子 bash/python/pytest 子树）内存。
- 判据：任何**本线**进程（或同 bash 进程树）RSS 异常高（单进程 >50GB，或多棵进程树累计吃掉宿主机 available 的显著份额）→ **先 kill -9 整棵失控进程树**（含父 bash），再记录。
- 特别警惕缩放型失控 cmdline：`partitions(`、`list(...)`、无界 `pytest`（内存爆炸测试）等。

**③ kill 掉的是正在跑的预测子任务** → **该题重新 predict**（不丢题、不重复 eval）；并评估加内存护栏（cgroup / ulimit / 改评测触发方式）后再重测。

**④ 纪律**：只清本线，🚫 不碰 S1 训练 / vision / data / zhulong 进程；心跳写 `未完成指令：有` ⇒ `WAITING: 0`；commit `harness 内存:`。

**⑤ loop 已改（运维改好了，无需你动）**：`SLEEP_WAIT`/`PUSH_INTERVAL` 30→15min。

> 📦 §运维令·2026-10-28 07:1x（SWE-bench Verified 全量 500 题）**✅ 已完成** → ARCHIVE；7 路全量完成：**cline356 / opencode401 / pi333 / codex291 / claude-code273 / deepseek212 / hermes184**。
> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。
### 📦 历史已闭合指针 · 2026-10-17 ~ 10-24（原文见 `run/ARCHIVE_OPERATOR_HARNESS.md`）

> 均已闭合/交付（原文见 ARCHIVE）：10-24 16:3x（TB7并发+Verified镜像，**Verified=500 非 Lite**）· 10-24 09:2x（92.25 配 dockerd，TB 镜像齐）· 10-24 09:0x（7 并发）· 10-23 22:1x（npm -g，Gate 7/7 R466）· 10-23（落盘写报告 / 上下文压缩 7 路报告）· 10-19 23:1x（kill .12 双 loop + R457 hermes fix）· 10-18 10:2x（ops 中继已修）。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 📦 历史已闭合指针 · 2026-10-16 ~ 10-17（详情见 `daily-memories-harness/` 对应日期 + ARCHIVE）

> 全部已闭合/交付：10-17 20:0x（oracle **5/5**，中继已恢复）· 10-17（TB2 · 7×89 · kimi；**结论**：TB2=89 tasks、oracle 须 5/5、7 路不得替换/合并）· 10-16（补完 188 条 → glm53 **2100/2100**）· 10-16（`report_harness_glm53_7x300_zh.html` 已交付）。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_HARNESS.md` / `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）/ `daily-memories-harness/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `harness 归档: …` 前缀。
> 本轮动作：本任务书现 ≈32KB（已贴上限）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。

### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 定位（2026-10-05，跨线）：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（目的是给内网网关鉴权：不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ 你（agent）会话里每条命令都继承了「无代理」env。
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 `Network is unreachable`（Errno 101）/ http `000` 是预期现象：🚫 不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题——别把它写进结论。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ 同机反证：`run/harness/r1_eval.py:144-148` 显式钉 proxy + 阿里云索引，pip 一直成功；relay 侧 git 同理（内网网关两种都 200）。
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 10-05「换冷门模型+严格串行」已归档 → 被 10-07 7-way 取代。

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_HARNESS.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_HARNESS.md` 的顶部单独一行
（`baize_harness_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行 —— 否则会误触发 30 分钟长睡。

运维巡检方式：外部运维 `git pull` 读 `MEMORY_HARNESS.md` 顶部 + `harness/` 下的报告即可，不需要登录服务器。

---

## 0. 任务概述

目的：横向理解「agent harness」这一类系统 —— 它们的工程实现差异，以及它们在真实软件工程任务上的能力差异。

| 线 | 内容 | 产出 |
|:--|:--|:--|
| H-B | 源码分析（从 cline 开始） | `harness/<name>_SOURCE_ANALYSIS.html`（自包含） |
| H-A | SWE-bench 横评（cline / opencode / deepseek harness 等） | `harness/SWEBENCH_COMPARE.html` + 结果表 |

代码位置：`/nas_train/app.e0031982/harness/`

> ## 🔍 既有同类研究线（2026-10-02 勘察，已闭合 → 详见 `run/ARCHIVE_OPERATOR_HARNESS.md`）
>
> `/nas_train/app.e0031982/harness/` 下另有一条 9 月创建的同类线（5 个 harness 源码 + `loop.sh` + `MEMORY.md` + `evidence/` + `mechanisms/` + `analyze_harness_sources.md` 11.8KB + `report.html` 24.6KB）。
> 运维 2026-10-02 确认：其 `loop.sh` **早已停掉**，⚠️ **不要重启它**；指示「可以合并」——其产物作**纯输入**复用，结论按我方主线重新审视。
> 纪律：① 只读不改它的目录 ② 产出统一落我方 `run/harness/` ③ 🚫 不启动它的 `loop.sh`（避免两个同类 loop 抢 token）。

---

## 1. H-A —— SWE-bench 横评

### 1.1 🔴 第 0 步（必做，先做）：可行性核查

在跑任何评测之前，逐条查清并报给运维：

| # | 查什么 | 怎么查 |
|:--|:--|:--|
| 1 | `harness/` 下有哪些 harness、各自版本 / 形态（CLI？插件？）| `ls -la` + 各自 `README` / `package.json` / `pyproject.toml` |
| 2 | 每个 harness 怎么启动、接什么模型（是否要 API key、能否接本地模型）| 读文档 + 试 `--help` |
| 3 | 模型可用性：本机能调哪些模型？（DeepSeek API？本地 vLLM？）| 实测一次最小调用 |
| 4 | SWE-bench 数据集：能否取到？取哪个子集？ | ⚠️ **现行口径 = SWE-bench Verified 500 题（不是 Lite 300）**；见 §用户令·2026-11-06 22:4x |
| 5 | 评测容器 / 沙箱：见下方「§1.1-bis 无 Docker 路线」 | `docker info`；不可用就按 §1.1-bis 改道 |
| 6 | 磁盘/时长预估：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 第 0 步没通过之前，不许"假装跑了"或"用其他指标冒充 SWE-bench" —— 如实报告阻塞。

> 📦 §1.1-bis 无 Docker 路线 + 连通性测试 + sb-cli 合规 + 路线优先级 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：R1 unshare 沙箱路线已选定并实现，2100 条评测已完成，pypi/内网镜像可用，docker 不可用。需要时再读。

### 1.2 评测设计（核查通过后）

