# BAIZE_DESIGNFLOW_BENCH_TASK.md — 设计流 Benchmark 任务书（2026-10-30 重构版）

> ## 🎯 任务初衷（最高优先级 · 一切规则与之冲突时以本段为准）
>
> **基于真实 trace 创建评测用例，评价 agent 解决用户真实任务并交付结果的能力。**
>
> 由此推出的三条铁律：
>
> 1. **任务形态 = 用户意图**。真实用户在 trace 里想干什么，就造什么样的任务——查文档就造查文档，跑 DRC 就造跑 DRC，写脚本就造写脚本。**没有任何预设的题型清单、难度配比或层级配额可以否决一个真实用户意图。**
> 2. **交付结果 = 判分对象**。每道 case 的 `check()` 必须能区分「真的交付了用户要的东西」和「没交付」：断言独立可失败、退化提交（空壳/只打印期望/删核心逻辑）必须 FAIL、隐藏输入 B 防背题。
> 3. **真实性 = 唯一来源**。每条 case 必须能溯源到真实 trace（`metadata.trace_source{user, host, session_file, match_count, real_task_summary}`）；没有真实 trace 的 case 没有资格入库。
>
> **难度分布是观察对象，不是生产指标。** L1/L2/L3 只用于事后统计当前题库覆盖了什么，**不得用于限制新建 case**。**通过率同样是观察值**——由用户任务的真实难度与 agent 真实能力共同决定，如实测量即可，不为凑数字而挑题、改题、加难或降难。

> ## 🔍 2026-11-15 用户令 · 用新标准重审「已造的题」与「候选池」· 最高优先 · 全部 4 shard

> **用户原话**：「安排4线重新审视自己已经造的题和候选池，如果跟任务初衷有违背可以重做」

**为什么现在要重审**

任务初衷已置顶（见本文件开头），但**你现有的题和候选池，是在旧规则下筛出来的**——旧规则里有 `L1≤30%/L2≥50%/L3≥20%` 的难度配额、有"只做 L2/L3"的准入限制、有"analysis-only 判为 weak"的筛子、还有"通过率必须落 20–30%"的调难度要求。**这些规则今天全部作废。**因此旧题里可能混进了两类问题：

- **A 类（该删/该重做）**：为了满足配额或通过率区间而**人为加难、改题、硬凑工具链路**的题——它们不是用户真实想干的事。
- **B 类（被误杀，该复活）**：当年因为"归为 analysis / doc-search / Q&A / env-config"被判 weak 而**没造的候选**——按新标准这些都是合法任务。

**一、重审「已造的题」（本 shard 全部 jsonl）**

逐题过一遍，用这三个问题判定：

1. **这条题问的，是 trace 里用户真实想干的事吗？**
   - 是 → 保留
   - 否（为了凑 L2/L3 配额硬加的步骤、为过题而人为改造的任务、把用户没要求的东西塞进判分） → 标 **`off_intent`**，进重做队列
2. **如果 `check()` 判分要求的东西，超出了用户原始意图**（例如用户只要"看到结果"，判分却要求特定文件结构/特定实现路径） → 标 **`over_constrained`**，把判分收敛回用户真实交付物
3. **有没有因为旧配额规则，把用户真实任务"降级/裁剪"后才入库的？** → 标 **`downgraded`**，考虑恢复原形态

**产出**：`designflow/intent_audit_<shard>.tsv`，列固定：
```
case_id | user_intent_from_trace | 判定(keep/off_intent/over_constrained/downgraded) | 理由 | 处置(保留/重做/下线)
```
并在 MEMORY 写一行：`🔍 意图审计: N 题, keep=x / off_intent=y / over_constrained=z / downgraded=w`

**二、重审「候选池」**

旧筛子把大量真实用户意图判成了"不可造"。逐项重判：

- **旧判为 weak / analysis-only / 不可造的候选**：`analysis-Q&A`、`doc-search`、`debug-Q&A`、`env-config`、`flow-driving`、`setup 类`、`retrieval 类`、`explain 类` —— **按任务初衷，这些都是真实用户意图，全部恢复为可造**。
- 唯一保留的排除标准只有两条：
  1. **没有真实 trace**（无 `trace_source` 可溯源）→ 不可造
  2. **写不出能区分真假交付的 `check()`**（判分没有"牙"）→ 不可造
- 其余一律视为**有资格造题**。

**产出**：`designflow/pool_reaudit_<shard>.tsv`，列：
```
session | user | host | mc | domain | 旧判定 | 新判定(可造/不可造) | 拟造任务形态
```
并在 MEMORY 写：`🔍 候选重审: 旧可造=x → 新可造=y（新增 z 条被旧规则误杀）`

**三、重做的方式（重要）**

- **重做不是删了重来**：保留原 case 及其 `check()`（作历史对照），新建修正版（case_id 加 `-v2` 后缀或独立新 id），并在 MEMORY 说明「v2 相对 v1 改了什么、为什么」。
- 🚫 **不删旧 case、不删 jsonl 行**——旧题是"旧规则下的产物"的证据，留着才能说明口径变迁。
- ✅ 允许**下线**：标 `retired` + 理由，从通过率分母中剔除（但 jsonl 行保留）。
- **工作量提示**：1366 条全审不是一轮能干完的（A=293 / B=319 / C=358 / D=396）。**分批做**：每轮审 N 条（自己定），把进度写进 MEMORY（`审计进度 x/N`），审完再回到正常造题。

**四、顺序建议**

1. 先审**最近 50 条**（最近的最可能带旧配额痕迹）
2. 再审 `rewrite_queue.tsv` 里挂着的那批
3. 最后扫历史存量
4. **候选池重审优先于继续造题**——池里被误杀的候选可能比你现在能挖到的更多

**五、纪律**

- 🚫 不改别人 shard 的 jsonl / MEMORY
- 🚫 不删数据（重做 = 新增版本 + 标状态）
- ✅ 审计结论要能逐题追溯到 trace 原文（`user` / `session_file` / 用户原话）



> 🔴 **2026-11-15 用户令 · shard A：mc 阈值降到 5（选料枯竭 → 扩池）· 最高优先 · 未完成**

> **用户原话**：「既然 designflow shard A 选料枯竭，那就把 mc 阈值降到 5」

**一、配置已由运维改好（不是待办，直接生效）**

- `designflow/summary_stats.json` → `shard_mc = {"A": 5, "B": 10, "C": 10, "D": 10}`（**只有 A 降到 5**，B/C/D 维持 10）
- `target_mc` 仍为 10（全局覆盖率分母口径不变）
- `trace_ledger.py` 读取逻辑：`--shard A` 时取 `shard_mc["A"]=5`（已核对代码 L320-324）
- 复算命令（`--thresholds` 默认就含 5，无需改代码）：
  ```
  python3 designflow/trace_ledger.py --shard A mc-matrix --thresholds 5,10,15,20,30
  python3 designflow/trace_ledger.py --shard A mc-matrix --emit-candidates-mc 5
  ```

**二、你要做的事**

1. **用最新扫描快照重算 A 的 mc≥5 池**（`scan_path` 现指向 `ssh_eda_search_20261115_013654/summary.tsv`，11-15 01:36，39263 行 / 6959 dedup）。
   ⚠️ **不要引用 r382 那份「降到 mc≥5 没用」的结论**——它基于 **11-05 的 `summary_1105.tsv`（2560 dedup）**，而现在是 **6959 dedup，数据量翻了近 3 倍**，旧结论可能已过期。**必须用新快照重新算一遍再说。**
2. **按 mc≥5 选料造题**，沿用既有全部质检（k≥8、3 neg FAIL、hidden B、A 档自包含、真实 trace 溯源——**这些门禁一条都不放松**）。
3. **每轮心跳必须报三个数**（不然无法判断降阈值是否有效）：
   - mc≥5 的 `pool / touched / fresh`
   - 本轮 peek 的候选里 **A 域 vs 跨域（C/D）的比例**
   - 本轮产出 case 数
4. **自动止损（写进你的判断逻辑，不用问我）**：若连续 **3 轮** mc≥5 下仍 0 case，把 `shard_mc.A` 改回 10，在 MEMORY 记录「mc≥5 扩池实测无效 + 数据依据」，然后转向别的产出（详见下条）。

   ⚠️ **注意止损的判据变了**：此前判「枯竭」用的是「strict-clean produce-task 有没有」——那套筛选把 analysis-Q&A / doc-search / debug-Q&A / env-config / flow-driving **全判为 weak**，而按顶部「任务初衷」，**这些正是真实用户意图，都该造**。所以现在止损的唯一判据是：**mc≥5 的候选里，有没有能忠实还原用户意图、且能写出可判分 `check()` 的任务**。若这类候选也真的耗尽，才算枯竭。

**三、并行任务：把 `waveview_real_cases.jsonl` 做出来**

你已连续 0-case 空转多轮，这段产能不要浪费。**在跑 mc≥5 选料的同时（或空转时）**，优先完成：

- 产出 `designflow/waveview_real_cases.jsonl` + `waveview_real_cases.README.md`
- 规格见 `designflow/WAVEVIEW_COLLAB.md` §零（字段、验收硬指标、纪律都在里面）
- 这条已经挂了 1 小时，vision 侧在等（虽然它也自己开了 SSH 通道，但你的 jsonl 是它的主路径）

**四、纪律**
- 🚫 不改题/图/check；🚫 不混 text-only 替身
- ✅ 「枯竭」照实说，但**要换成 mc≥5 口径重新举证**，不能拿 mc≥10 的旧证据说 mc≥5 也枯竭


> 🟢 **运维令 · 2026-11-14 18:0x（用户直令）· A 可主动全量扫描 698 机 —— 覆盖 §9「默认否，只被动只读发现」**
>
> **用户原话**：「designflow A 要开新全量扫描就开吧，随他。」
>
> **授权**：A 可**自行发起主动全量 `ssh_eda_search`（698 机）**，不必再逐次请示；§9 该条已同步标注「已确认」。**「随他」指节奏自主，不是无约束**，四条护栏同时生效：
> 1. **频率**：全量**每日 ≤1 次**（确需补扫 ≤2，须在心跳写明理由）；扫前先 `ls -dt /home/t0002965/log/ssh_eda_search_*` 记录上次数与 mtime —— **同池不重复扫**。
> 2. **只读 + 低影响**：仅 `ls/stat/head/grep` 级元数据；🚫 不写远端、不 chmod、不删文件、不跑长命令；并发与 `nice/ionice` 沿用既有脚本默认（若要提高并发，先在心跳记录改动与理由）。
> 3. **扫完必须闭环**（r528 教训：扫了不换池 = 白扫）：新 `summary_<MMDD>.tsv` → 刷新 `mc_matrix.src` / `summary_stats.json` → 按 r462/r501 的 **POOL_SWITCH** 流程落盘（旧快照留 `_hist`）→ 同轮在 MEMORY 写 **scan 目录名 / 行数 / mtime / 耗时**。
> 4. **异常即停**：Permission denied / 超时 / 主机不可达 比例异常（>20%）⇒ 停手报运维，不硬刚。
>
> **本轮目标**：把 r528 查到的 95 条 fresh（14/14 抽查 NOFILE = 文件已被 rotation 蒸发）变成**可 peek 的活会话**，并回答「A-core 到底还剩多少可做」；扫完前两轮不要再用「枯竭」措辞。

> 🆕 **用户令 · WAVEVIEW 协作 · 2026-11-14（vision ↔ designflow 协作 · 空闲时认领）**
>
> **用户原话**：「请你帮助 vision 完成跟 designflow 的工作协调（#3 / #4）」
>
> **要你做什么**：vision 需要 designflow 帮忙跑 waveview 用例的**真实基线**，才能度量多模态增益。
> 详细交接 → **`benchmark/designflow/WAVEVIEW_COLLAB.md`**（含输入清单、两步任务、交付落点）。
>
> **一句话**：把「原意图需看图」的 11 题（α4+β7，清单在 `doc/BaiZe-ISEDA2027/run/reports/waveview_need_image_handoff.md`）**恢复成需要看图的原始形态**并跑出基线通过率；无多模态能力者 fail 是正确结果，**不许降级成文本替身**。
>
> **认领规则**：任一**空闲** shard 在 `WAVEVIEW_COLLAB.md` 的「认领记录」写一行即可开始；**同一任务只由一个 shard 做**；本 shard 若有 case 可造，**造题优先**，协作让给空闲 shard。
>
> **完成**：在 `WAVEVIEW_COLLAB.md` 的「交付记录」写一行 + 本线 MEMORY 记一行。
>
> ---
>
> 🔁 **换池职责变更 · 2026-11-12 用户令**：候选池 11/05 → 11/09 的切换**改由 B 执行**（见 `BAIZE_DESIGNFLOW_BENCH_TASK_B.md` 顶部令）。**A 不再执行 A1–A6 换池步骤**，也不再重复生成 `summary_1109.tsv`；A 继续负责 `board.md` 维护与选料，等 B 落盘 `summary_stats.json.mc_matrix.src=summary_1109.tsv` 后**直接使用新池**（不得再用 1105 的 fresh 数字做选料结论）。
>
> ---
>

> 💬 **2026-11-11 用户令（第 2 版）：讨论区 `benchmark/designflow/discuss/`**
>
> 用户原话：「各线designflow在没有case可做时，阅读论文，在这个文件中阅读他人的看法，发表自己的意见。」
>
> #### 触发（配额制 · 取代第 1 版「0-case 才进」）
> 第 1 版写「本轮 0 case 才进 + 有 case 则造题优先」⇒ **零发言**（0-case 是瞬时状态，且没配额跳过零成本）。
>
> | 何时必须发言 | 说明 |
> |:--|:--|
> | **每 4 个造题轮 ⇒ 1 次** | 看 `discuss/A.md` 最近发言轮次，与本轮相差 ≥4 即欠一条 |
> | **`board.md` 有 OPEN 议题点 `@A`** | 当轮必须表态，不受配额限制 |
>
> 🚫 不许以「本轮有 case」跳过 —— 发言仅 15–20 分钟，不占造题时间。
> **豁免**：BLOCKED/事故轮；或无 OPEN 议题且未欠配额。连续两轮欠配额须在 MEMORY 写原因。
>
> #### 4 步（15–20 min）
> ① 读：`board.md` OPEN 议题 → 其他 3 shard 的 `.md`（尤其 `回应 @A`）→ `rounds/` → 论文 section
> ② 想：用 **digital / verification / pnr_signoff / eda_other** 域视角；**引你造过的 case** 作依据最有价值
> ③ 写：append 到 `discuss/A.md`（格式照 `discuss/README.md §3`）
> ④ 提交：`git add benchmark/designflow/discuss/A.md`
>
> #### 最低有效标准（达不到 = 没发言，下轮重写）
> 🚫「我同意」「+1」不算；✅ 必须表态明确（同意/反对/补充）+ 本域依据（case id / 实测数字 / `sections/X.tex`+行号）。
>
> #### 边界
> 🚫 禁改 `README.md` / `board.md` / 其他 shard 的 `.md`；🚫 `git add -A`
> 召集人 = **shard A**（board 只由 A 写；A 也要发言）。讨论产出是**建议**不是结论。论文目录只读。



> ### ⚠️ 同步纪律（共享工作副本 · 2026-11-11 补 · 源自两次真实事故）
>
> 4 个 shard + 其他线**共用一个 git 工作区**。文件系统不会写坏文件，**但 git 合并会丢内容**：
> - **事故 1（2026-11-02 本仓 shard C）**：`rebase clobbered rounds 3-6` —— 台账 4 轮记录被 rebase 覆盖（commit `5883d4d43`）。
> - **事故 2（2026-10-07 兄弟仓）**：历史 autostash 一 `pop` 就冲突 ⇒ 弄脏共享工作区 ⇒ **阻塞所有线 pull，停摆 5 小时**。
>
> **每轮收尾「同步三连」，缺一不可**：
> ```bash
> git status --porcelain                                 # ① 干净（只应有你本轮的文件）
> git stash list                                         # ② 空
> git rev-list --left-right --count origin/main...HEAD   # ③ "0 0"
> ```
> 1. 🚫 不 clean / reset / stash 别人的改动（陌生未提交文件是别线在途）。
> 2. 🚫 禁止 `git stash pop` 去"恢复"残留 —— 会阻塞全部线。
> 3. ✅ 冲突解不掉就**停手报 blocker**，🚫 别靠 rebase 硬推（丢的是别人的数据）。
>



> 🔴 **2026-11-11 用户令（最高优先 · 覆盖上面所有旧令）：mc 阈值全线 30 → 10**
>
> **用户原话**：「那就继续全面调低 mc 值，比如调到 mc>=10」。
>
> **配置已由运维落地**（本机可直接验证，不是待办）：
> - `designflow/trace_ledger.py`：`SHARD_MC = {"A":10,"B":10,"C":10,"D":10}`，新增 `DEFAULT_MC=10`；
> - `designflow/summary_stats.json`：`target_mc=10`、`shard_mc` 全 10、新增 `mc10/mc15/mc20` 与 `mc_matrix`；
> - `designflow/candidates_mc10.tsv`：**已生成 1929 行（mc≥10）**，比旧 `candidates_mc30.tsv`（1369 行）多 560 行；
> - `designflow/trace_ledger.py mc-matrix`：本机复算池/已动过/未动过，`gen_daily_report.py` 已改为一页一个分母。
>
> **各 shard 每轮必须执行**：
> 1. **选料改用 mc≥10**：`python3 designflow/trace_ledger.py --shard <X> mc-matrix --src designflow/summary_1105.tsv --thresholds 10,15,30` 核对池；取候选时 `awk '$5+0>=10'`，**禁止再出现 `>=30` / `>=15` 字面量**（含注释与 MEMORY 里的口径描述）。
> 2. **候选池用 mc≥10 口径**：建议用 `candidates_mc10.tsv`（或用 `mc-matrix --emit-candidates-mc 10` 按 shard 过滤重出）；`candidates_mc30.tsv` 是旧口径，用它会让「池多少」失真。
> 3. **说「池已枯竭」要有依据**：同轮贴出 `mc-matrix` 输出证明 `fresh=0`。此前 `C` 线「池确证枯竭」是在 mc≥30 口径下说的，mc≥10 下尚未验证。（不是禁止你说，是要你说得能被复核。）
> 4. **覆盖率报数必须与 `summary_stats.json.target_mc` 同口径**（现在是 `mc10`，分母 1929），并注明是哪份扫描快照（`mc_matrix.src`），不得混用 `mc30=2247`。
>
> **实测依据（11/05 全量扫描，5822 数据行 → 2560 去重 session）**：
>
> | 阈值 | 池总量 | 已动过 | 未动过（可做） |
> |:--|--:|--:|--:|
> | mc≥30（旧） | 1,511 | 1,392 | **119** |
> | mc≥20 | 1,681 | 1,465 | 216 |
> | mc≥15（A 旧） | 1,795 | 1,504 | 291 |
> | **mc≥10（新）** | **1,929** | **1,548** | **381** |
> | mc≥5 | 2,114 | 1,582 | 532 |
>
> 分 shard 未动过（mc≥30 → mc≥10）：**A 109→318 · B 5→39 · C 102→332 · D 70→252**。
>
> ⚠️ **shard A 补充**：工具健康令（2026-11-10 22:2x）的硬约束"`trace_ledger next/claim` 跳过 + A.jsonl 保持 203"**与令同日失效**——本条用户令要求恢复造题。工具健康深挖已 DONE（r325 交付 + r334 修正），请把令归档进 `ARCHIVE_OPERATOR_DESIGNFLOW.md`，勿再以 holding 空转（已连 35 轮 r327-r361）。

> 🚨 **本轮这一条 case 不是造题，是「工具健康深挖」（2026-11-10 22:2x 用户令 · 仅 shard A）**
>
> 循环任务卡会说「本轮只做 1 条 case：trace_ledger next → 深读 → 合成 → 追加 jsonl」。
> **本轮把这 1 条 case 直接替换成本任务**：`trace_ledger next / claim` 跳过，
> `EDA-Eval-DesignFlow_A.jsonl` 保持 203 不变。
> （沿用上一轮成功的经验：把令写成卡片语言，比在顶部挂"最高优先"更有效。）
>
> **问题（用户原话）**：「再深入看看 trace，有没有异常。比如 finesim、asc 这些 EDA 工具是否正常执行？
> 有哪些重复出现的失败模式？**写个中文 HTML 报告**。」
>
> **一、数据在手，别重新跑评测**
> `designflow/eval_triage/results/run_batch_20261109_171201/triage_summary.json` 里每个 case 都带
> status/class/evidence 路径；据此定位每条的 agent session 与 judge log。
> 690/696 有判分证据，6 个 ABSENT。
>
> **二、写 `07_tool_health.py`（stdlib only，放进 `eval_triage/`）**
> 逐 run 抽取并聚合：
> 1. **执行过的命令**：从 session 的 tool 调用里取 `run_commands` / `eda_flow__run_commands` 的输入；
> 2. **工具识别**：正则命中清单（大小写不敏感、按"词边界+可执行名"匹配）：
>    `finesim` `hspice` `spectre` `eldo` `smartspice` `asc` `aether` `schematic` `calibre` `pvx`
>    `innovus` `icc2` `pt_shell` `primetime` `dc_shell` `design_compiler` `verdi` `vcs` `xrun`
>    `spyglass` `star-rc` `redhawk` `totem` `siliconsmart` `pyAether`
>    —— 每个工具报：**调用次数 / 有正常输出 / 报错退出 / 调了但无产物 / 从未调用**（四态分开，
>    **"从未调用"绝不算工具失败**）；
> 3. **失败签名归一化**：从工具输出/退出码里抽 stderr 首行，去掉路径/时间/编号后聚类
>    （例：`command not found`、`licence`/`license`、`No such file`、`Permission denied`、
>    `MCP ... refused`、`timeout`、`syntax error`、`undefined net`、`SPICE convergence`）。
>    每类报：出现 run 数 / 出现次数 / **3 个 example task_id** / **1 行原文证据（≤200 字符）**；
> 4. **交叉分析**：签名 × domain、签名 × 失败类别（NO_SUBMIT/RT/SEM/UNKNOWN）、finesim/asc 专项小节。
>
> **三、产出（本轮交付物）**
> 1. `eval_triage/results/run_batch_20261109_171201/tool_health.json`（机器可读，带 evidence 路径）；
> 2. **中文 HTML 报告**：`doc/ZhuLong_DAC2027/reports/report_designflow_tool_health_20261110_zh.html`
>    —— 自包含（内联 CSS + 内联 SVG 条形图，**不引 CDN、不依赖 JS**），结构：
>    ① 一句话结论 ② 工具健康矩阵表 ③ **finesim / asc 专项**（是否正常执行、典型失败）
>    ④ Top-15 重复失败模式（含 example + 原文）⑤ 按 domain / 失败类别的交叉表 ⑥ 方法与被排除项
>    （例如"从未调用"、"无判分证据"的计数）+ 复现命令。
> 3. MEMORY 一行：`tool-health: <工具数> tools seen, finesim=ok/fail/not-invoked, top pattern=<签名> <n>runs, html=<path>`；
> 4. commit 脚本 + json + html + MEMORY + daily；**原始 session/trace 不入库**。
>
> **四、判据**
> - 工具四态必须能自证（贴 2 个 case 的解析前后对照到 MEMORY）；
> - "asc" 若在本数据里其实是别的含义（如 Aether 的 asc 子命令或某个 shell 别名），
>   **在报告里如实写清你核到的含义**，不要硬凑成工具；
> - 若某工具的全部调用都失败，单独点名（这正是用户要的"异常"）。
> - 数字不许估：取不到写 `n/a` 并说明原因。

> 📦 **归档指针 · 2026-11-09「全量 trace 重扫 + mc 阈值下调评估」**（已执行完毕）：现行做法 = 定期全量 `ssh_eda_search` 重扫 → 更新 `summary_stats.json.scansync` + `threshold_table`；阈值评估**只看"能忠实还原用户意图的候选有多少"**，不再产出"最低可用阈值"这类向上论证。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW.md`。


> ⛳ **每轮收尾必做（2026-11-09 运维令 · 论文维护）**
> 1) 编译回归（≤2 min）：`cd doc/ZhuLong_DAC2027/EDA-LiveFlow-Bench_ICML2027 && latexmk -pdf -interaction=nonstopmode main.tex` → 必须 **0 error**；本机无 latexmk 则记录 `PAPER_SKIP(no latexmk)` 后继续。
> 2) 数字同步：任务总数唯一事实源 = `main.tex` 的 `\newcommand{\Ntasks}{931}`（当前 **931 = A185 + B211 + C271 + D264**）。若本轮 A/B/C/D 任一 jsonl 有增减：改 `\Ntasks` 一行 + 文末 App A 的分项，然后重新生成并提交 `main.pdf`。
> 3) 记录：在 MEMORY/daily 写 `paper: compile OK, N=931, pdf=10p` 或 `PAPER_SKIP(no latexmk)`。
> 基线提交：`4b7ed6331`（结构/接口已修好；**不要重写结构**，只做回归与数字同步）。


### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow（含本 benchmark 的造题/保真度/判分）。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「designflow 建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 归档指针 · 2026-11-06「shard A 双重职责 + 放宽候选池」· 现行口径：A 仍承担每日管理任务（`scansync` + 刷新 `summary_stats.json`）；候选池阈值已改 mc≥10（见顶部令）。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档块 · 2026-11-11」
---

### 📦 归档指针 · 2026-11-02「被测换 cline + PreToolUse 防泄题 hook」· 现行口径：被测 = cline（`--auto-approve true --json`）；hook ⇒ agent 只能看 workspace 内文件，判分器在 workspace 外跑。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档块 · 2026-11-11」

### 📦 归档指针 · 2026-10-31 21:5x「k 条断言硬闸门」· 现行口径已并入 **§4.3（≥8 独立条件）+ §4.6（test_rationale 逐条断言清单）**：`k_rationale == k_check 且 k_check ≥ 8`，不过则标 `incomplete` + 进 `rewrite_queue.tsv`，不许落 jsonl、不计通过率。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW.md`。


### 📦 归档指针 · 2026-10-31「A/B 双档 casemaking」· 现行要点：A 档 = trace-faithful（用真实 trace 用户原话作任务说明，不改写），B 档 = synthesized；A 档优先，B 档须说明 A 为何不可行。原文见 `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档块 · 2026-11-11」。

## 0. 目标（一句话）

用 `.75` 内网 **698 台机 / 2,850 用户 / 52,698 会话（24,085 条 IC-EDA 命中）** 的真实 cline 轨迹，构建「设计流编排」评测集——**用户真实在做什么，就造什么样的题**，通过率如实测量、不设目标区间（见顶部「任务初衷」）。

## 1. 红线（不可协商）

1. **真实 trace 才有资格**：每条 case 必带 `metadata.trace_source{user, host, session_file, match_count, real_task_summary}`。没有真实 trace 的 case 一律删除，🚫 不许改个名字保留。
2. **不脱敏（全产物）**：`user` / `host` / `session_file` / `/home/<user>` 路径 / `prompt` / `attachments` / 深读笔记 / MEMORY **一律保留原值**；只有 **key / token / 密码** 需掩码。🚫 prompt 里出现"脱敏""不要出现真实用户名"字样视为违规。
3. **单一 jsonl**：只往 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl` 追加；🚫 新建 jsonl（>500 条才按 `metadata.domain` 拆 4 个）。
4. **只读纪律**：对 698 机只 `find`/`ls`/`cat`/`head -c`/`awk`/`python3` 只读；🚫 写目标机、🚫 `rm`/`tee`/`>`；🚫 本机自扫；🚫 lineage 自审计 / §X 递归。
5. **git 双仓**：workspace → `super_intelligence_2035` **main**；用例产物 → `EDA-Flow-Bench` **master**；🚫 `git add -A`。
6. **体积**：本 TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限按 §8 归档（原文搬 ARCHIVE，留 1 行指针）。

## 2. 环境速查

| 项 | 值 |
|:--|:--|
| workspace | `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/` |
| 用例仓库 | `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（jsonl / assets / reference） |
| 历史快照 | `EDA-Flow-Bench/agent_workspace/designflow/`（bench_v0.1~v0.50，只读，不迁） |
| 运行时 cwd | `/nasdata/app.e0031982/code/EDA-Flow-Bench/` |
| 沙盒入口 | `eda_flow` MCP `http://127.0.0.1:18891/mcp` → `.75`（`hfhds201` / `10.129.32.75`）`run_commands`·`run_code`·`read_file`·`write_file` |
| 扫描结果 | `.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`（列：`ip host user session_file match_count keywords tools`） |
| 评测框架 | `./RUN_EVAL.sh --design-flow` / `--design-flow-agent`；`scripts/run_design_flow_batch.py`；`config.yaml`；`docs/design_flow_session_backend.md`（§3 接口 / §9 判分两步）；`docs/设计流Benchmark-{测试用例编写指南,框架改进设计文档}.html` |
| pi（被测） | `pi` 1.4.0，provider `cxmt` / `deepseek-v4-pro-cloud`，已配 `eda_flow` MCP。调用：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`（Node 22 需在 PATH：`export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH`） |

**命令模板（只读抓 trace）**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "ls /home/*/.cline/data/sessions/*.messages.json | head -20"
```
> `.75` 已对 **697/698** 台免密（`e0031982` 身份）。**分批 5–10 台/次**，别一次扫 698 台（会超时）。

**三个已知坑（别再踩）**
1. **GitHub 假阴性**：`curl https://github.com` 在剥掉 proxy 的环境里返回 `000`，但 `git push` 走 `git config --global http.proxy` 仍可通。**判据用 `git ls-remote origin HEAD`，不要用 curl**。（确需代理：`git config --global http.proxy http://172.19.92.23:13128`）
2. **`write_file(content_base64=...)` 会腐蚀内容**（`$dA` → `$d\x01`）：一律用 plain `content` 字符串，或 `run_commands` 里 `base64 -d` 在本机解码。
3. **`ssh` 在 eda_flow 里会 hang**：命令前加 `</dev/null`（`-n` 反而会断 stdin pipe）。

## 3. 用例契约（proper `design_flow`）

```text
mode:        "design_flow"
entry_point: "outputs/submit.zip"
test:        "def check(deliverable, workdir): ..."   # 双参，返回通过 / 抛异常失败
prompt:      自然语言，写真实场景（真实用户名/路径/工具/指标），不是函数签名题
attachments: [assets/<task_id>/...]                    # 真实输入文件
metadata:    { trace_source{...}, domain, test_rationale }
```
🚫 不带 `lang` / `host` / `runtime`；🚫 不写"实现 `xxx(args)->dict`"这类抽象题。

**单轮闭环 + 交付定义（DoD）**

一轮 = 一条 case 从选料到落库，**建议不要拆成两轮**（拆开会拉长交付周期）：

- **深读是硬闸门，但不是独立的一轮**：必须先解析完整对话流（`scp` `messages.json` → user 意图 / assistant 工具链 / 关键产物 → `designflow/trace_deepreads/<sid>_<主题>.md`）才允许合成；已有笔记可直接复用，不重复深读。
- **DoD（交付定义）**：1 条 case 通过自验并写进 `EDA-Eval-DesignFlow.jsonl` 才算交付；**深读笔记是中间产物，不算交付**。
- **每轮做多少条由你判断**：只要上下文不失控、每条都过质检，一轮做 1 条或 3 条都可以。**硬要求是质量不是数量**：未过闸门的 case 一律标 `incomplete`，不进 jsonl、不计通过率。
- **单条 trace 过大时**（>2MB 或 >600 msgs）可以本轮只深读，心跳记 `DEBT: 1 deepread 未合成`，下一轮交付 case。连续多轮只深读会让产出滞后——如果确实需要（例如在追一个大线索），说明理由并给出交付 ETA。
- **选 trace 走台账（去重与进度的事实源）**：`python3 designflow/trace_ledger.py next --n 5` → 在 `.75` 上取候选 → 选第一条 → `claim` 落台账。
  - 出完 case：`mark --session <s> --status case --case-id <EDA-Eval-DesignFlow-XXX>`（覆盖率的唯一分子）；
  - 暂缓：`mark --session <s> --status parked --note "<原因>"`（如 aether 超时），**不重复捡**。
  - 台账是**去重与进度的记录**，不是选题的紧箍咒：如果你从别的途径（深读、domain 关键词、其他 shard 线索）发现了一个值得做的 session，**只要先 `claim` 登记**就可以做。跳过 claim 才会让去重失真，所以登记就行。
- 选料偏好：`match_count` 高 + **该 domain 尚无 case**（domain 覆盖优先于纯命中数）——这是偏好，不是硬性规则，遇到更好的题可以覆盖。

## 4. 判分质量（"有牙"，缺一不可）

1. **隐藏输入 B**：A 给 SUT 看，B 放 `assets/<id>/hidden/` + `hidden_manifest.json`，**不进 SUT 沙箱**；`check()` **只跑 B**，B 与 A 在规模/取值/结构上必须不同（不是换文件名）。
2. **真跑候选**：≥1 个条件用 `subprocess` 在 B 上执行候选脚本，断言**输出结构**（解析成字段/拓扑/计数再比较），不是文本相似。
3. **≥8 个独立条件**，每个单独可 FAIL；🚫 "仅成员名 / 仅子串出现"式断言。
4. **负样本入库**：`reference/<id>/negative/` ≥2 个错解（naive / always-XXX stub）+ `negative_selftest.py`，一次跑完必须**全 FAIL**；每轮抽查 1 条重跑。
5. **随机化**：在 B 上随机抽子集（net / signal / 行），3 个随机种子跑 3 次结论一致；🚫 把期望值硬编码成固定串。
6. **`metadata.test_rationale` = 逐条断言清单（不是摘要）**：格式固定 `k 条断言：①<验什么> ②<验什么> …`，**一条对应 `check()` 里一个可独立失败的条件**，写清"对象 + 判定"。
   - ✅ `7 条断言：① zip 内 5 个文件齐全 ② mac4.v 有 module mac4 且端口 clk/rst_n/acc0 齐全 ③ 累加为 32-bit 有符号饱和（边界 0x7fffffff/0x80000000） ④ sim_mac4.log 含 MAC4_SIM_PASS 且无 MAC4_SIM_FAIL ⑤ …`
   - 🚫 废话：`解 zip 校验 3 文件`、`校验交付件完整性`、`断言内容达标`
   - 🚫 实现细节：`raise AssertionError(...)`、`zipfile.ZipFile(...)`、`z.read(...).decode(...)`
   - 自检：`k` 必须等于 §4.3 要求的独立条件数（≥8）；两者对不上 = 未完成。⇒ 按顶部令 21:5x 执行：标 `incomplete`、进 `designflow/rewrite_queue.tsv`、🚫 不许落 jsonl、🚫 不许计入通过率。
7. `check()` 在**独立临时目录**解 zip；🚫 在 SUT workdir 留 `__chk`。
8. **泄漏隔离**：SUT 沙箱不得包含 `benchmarks/EDA-Eval-DesignFlow/`（`reference/`、jsonl、`test` 字段）；结论写 MEMORY 一行。
9. **退化提交回归**：每条 case 必须让 (a) 空壳 (b) 只 print 期望串 (c) 参考解删核心 三种假提交**全部 FAIL**；任一 PASS ⇒ 该 case 判分不合格，限期整改或下线。

## 5. 难度分布（观察指标 · 不是生产配额）

| 层 | 定义 | 当前占比（事后统计） |
|:--|:--|--:|
| L1 | 离线 Python 复刻（读附件写脚本） | 观察值 |
| L2 | 真跑沙盒工具（calibre LVS/DRC、Virtuoso、PrimeTime、VCS，经 eda_flow / .75） | 观察值 |
| L3 | 多工具链路 + 修复 + 回归（DRC 179→0、LVS 干净 CORRECT、ERC 全清） | 观察值 |

- 🎯 **层级不是造题的准入门槛**：trace 里用户实际在做什么，就造什么难度的题（见顶部「任务初衷」第 1 条）。此表只用于**事后统计题库覆盖了哪些难度**，供判断题库是否偏科，**不得用于否决任何真实用户意图**。
- 若观察发现某一层长期为 0（例如 L2 一直没题），说明**选料没覆盖到这类 trace**，应去扩大选料面，而不是禁止其他层造题。
- 总样本 **<30 条前不报通过率**，只写"已跑 n 条中 x PASS"（6 条算百分比没有统计意义）。
- 🎯 **通过率是观察指标，不是造题目标**：真实用户的任务有的容易、有的很难，题库本来就该长这样。**不得为了让数字落进某个区间而挑题、改题、加难或降难。**
- 实际含义：通过率由“用户任务的真实难度分布 + agent 的真实能力”共同决定，我们只负责如实测量，不负责塑造。总样本 **<30 条前不报通过率**，只写“已跑 n 条中 x PASS”。
- 心跳每轮写一行：`🎯 通过率: 最近20条 x/20 = y%（观察值）`。
- 若某条 case 长期 0 PASS，**先查 `check()` 是否误判**（参考解能不能 PASS），再判断是题难还是判分错——**不要为了好看向下调难度**。

## 6. 每轮流程

1. `trace_ledger.py next --n 5` 取候选 → `claim` → 深读（有笔记就复用）→ 合成（`assets/` `reference/` `hidden/` `negative/`）。
2. 自验：`reference/` 参考解跑 `check()` 必 PASS；§4.9 (a)(b)(c) 三假提交必 FAIL；`negative_selftest.py` 全 FAIL。
3. pi 实跑：`designflow/pi_debug_status.jsonl` 追加一行，记 `pi_model / pi_thinking / pi_dur_sec / pi_verdict / ref_check`。
6. 收尾：`WAITING: 0`（下一轮 60s 后立即开下一条 case）；仅真外部阻塞（pi 异步未回 / 推送失败 / 等人工）才写 `WAITING: 1`。

## 7. 当前基线（每轮只更新这一行，不堆历史）

`11 条 proper（10 域）· 已跑 6 条 = 6 PASS · 6 trace_deepreads · test_rationale 断言清单 0/30（硬闸门见顶部令 21:5x）· 目标通过率（B 档）20–30%`
`📊 trace 覆盖率：见 designflow/trace_ledger.py stats（covered / mc≥10 候选池，target_mc=10）`
> 现存 11 条的 `test_rationale` 本轮内全部改写成 `k 条断言：①…`（k = 该 case `check()` 的独立条件数）。

## 8. 收尾（轻量结账，不是每轮做全套）

> 收尾是"结账"：**一轮 = 1 条 case = 1 次结账**。别把结账做成产出，也别攒着不提交。

0. **体积自检**：TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限先把已闭合块**原文**搬 `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针），搬前 `git pull --rebase --autostash`，🚫 不改小节编号/标题。数字抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB`。
1. **心跳（轻）**：`MEMORY_DESIGNFLOW.md` 顶部快照**只改变化的几行** + **追加 1 行流水**（三口径 + `🎯 通过率` + `📊 trace 覆盖率 x/y=z%` + `DEBT`）；🚫 每轮重写整份快照。
   - 顺带刷新候选池（**2026-11-11 令：mc≥10 口径，`target_mc` 必须 10**）：在 `.75` 上跑一次 `awk` 统计 `sessions / mc10 / mc20 / mc30 / mc100`，然后
     `python3 designflow/trace_ledger.py refresh --json '{"sessions":N,"mc10":N10,"mc30":N30,"mc100":N100,"target_mc":10,"shard_mc":{"A":10,"B":10,"C":10,"D":10}}'`
     ⚠️ **禁止**写 `"target_mc":30` 或 `shard_mc` 里出现 15/30（会把分母与选料阈值脱钩）。
     （进度条的分母与"新增 traces"都来自这里；换池时按顶部 A1–A6 走。）
2. **日记忆**：`daily-memories-designflow/<YYYY-MM-DD>.md` **当天首轮创建，之后只追加**。
3. **提交**：**每轮（1 条 case）结束即提交**（loop 另有每 30 分钟兜底）；🚫 把工作留在工作树过夜。双仓命令：
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/designflow \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
           doc/ZhuLong_DAC2027/reports
git commit -m "designflow #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow
git commit -m "designflow #<轮次>: <一句话>" && git push origin master
```
4. **闭环自检**：`git status -sb` 无 ahead/behind；push 失败重试 1 次并记报错原文。

> ⏱ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

## 9. 待确认（未确认前按默认走）

- Benchmark 是否对外（默认：先内部）
- ~~是否允许主动扫描 698 机~~ ⇒ **已确认：允许（2026-11-14 用户令「放宽，随他」）**，口径见本文件顶部 🟢 运维令；四条护栏同时生效

---

> ⚠️ 本文件为**只读指令文件**，agent 禁止修改；有异议写进 MEMORY 并存疑执行。



## 🔀 SHARD 配置（本 shard 专用 · 覆盖主 TASK 中的通用描述）

**你是 shard A（digital_front + 管理员）**。负责以下 domain：digital, eda_other, pnr_signoff, verification。**额外承担全 4 shard 的每日 scansync 管理任务**（见顶部 11/06 运维令）。

### 你的文件（不要碰别的 shard 的文件）
- **jsonl**：`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl`（只往这个文件追加 case）
- **台账**：`designflow/trace_ledger_A.tsv`（通过 `trace_ledger.py --shard A` 自动使用）
- **心跳**：`MEMORY_DESIGNFLOW_A.md`（只写这个文件，含每日 scansync 报告）
- **日记忆**：`daily-memories-designflow/daily_A_*.md`
- **全 shard 共享配置**（shard A 负责维护，其他 shard 只读）：`designflow/summary_stats.json`

### 选 trace 命令（**2026-11-11 令：mc≥10，候选池 = 11/09 快照**）
```bash
# 候选池：mc>=10 + 放宽过滤词 (+synthesis/synopsys/tcl/verilog/rtl/sdc/vivado/yosys/openroad)
# 扫描源：summary_stats.json.scan_path（11/09 = ssh_eda_search_20261109_224902）
# 候选清单：designflow/candidates_mc10.tsv（candidates_mc30.tsv 已冻结）
python3 designflow/trace_ledger.py --shard A next --n 5
python3 designflow/trace_ledger.py --shard A claim --session <s> --user <u> --host <h> --match <m> --domain <d>
python3 designflow/trace_ledger.py --shard A mark --session <s> --status case --case-id <id>
```

### 管理任务命令（每轮开工前先做，5 分钟）
```bash
# 1. 跑 scansync 拿最新扫描口径 (输出 ready-to-run 命令块，含 mc10/mc15/mc20)
python3 designflow/trace_ledger.py --shard A scansync
# 2. 经 eda_flow run_commands 在 .75 上执行 scansync 输出的命令
# 3. 用拿到的数字更新 summary_stats.json（mc≥10 口径，禁止 target_mc=30）:
python3 designflow/trace_ledger.py refresh --json '{"scan_path":"<最新>","mc10":N10,"mc20":N20,"mc30":N30,"users_mc10":NU,"target_mc":10,"shard_mc":{"A":10,"B":10,"C":10,"D":10},"scansync":{...},"updated_at":"<now>"}'
# 4. 在 MEMORY_DESIGNFLOW_A.md 写今日新增 trace 报告
```
⚠️ 老模板里的 `"shard_mc":{"A":15,"B":30,"C":30,"D":30}` 与 `"target_mc":30` **已作废**，勿再复制。

### 合并
- **不要碰主 jsonl**（`EDA-Eval-DesignFlow.jsonl`），它由 merge 脚本自动合并 4 个 shard 生成
- 你的 case 只追加到 `EDA-Eval-DesignFlow_A.jsonl`

### 收尾提交（只提交自己 shard 的文件 + 全 shard 共享的 summary_stats.json）
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_A.md \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_A.tsv \
           doc/ZhuLong_DAC2027/benchmark/designflow/summary_stats.json \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger.py \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow/daily_A_*
git commit -m "designflow shard A #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl \
           benchmarks/EDA-Eval-DesignFlow/assets benchmarks/EDA-Eval-DesignFlow/reference
git commit -m "designflow shard A #<轮次>: <一句话>" && git push origin master
```

---

## 附加职责（2026-11-09 运维令）：ICML 2027 论文维护

路径：`doc/ZhuLong_DAC2027/EDA-LiveFlow-Bench_ICML2027/`

### A. 编译（每轮必过）

```bash
cd doc/ZhuLong_DAC2027/EDA-LiveFlow-Bench_ICML2027
latexmk -pdf -interaction=nonstopmode main.tex   # 必须 0 error；当前 10 页
```

- ICML 2027 Author Kit 未发布，暂用仓库自带 `icml2026.sty/.bst`；拿到 2027 kit 后替换文件并改 `\usepackage{icml2026}` / `\bibliographystyle{icml2026}`。
- `main.tex` 必须用 **ICML 2026+ 接口**：`\twocolumn[... \icmltitle / icmlauthorlist / icmlaffiliation / icmlkeywords ...]` + `\printAffiliationsAndNotice{}`；禁止旧接口 `\icmlrunning` / `\maketitle`。
- **正文禁止非 ASCII**（中文 / em dash / 箭头等）：pdflatex 无 CJK 字体，会 fatal；注释也建议写英文。
- 若报 `pcrr7t.tfm not found`：`tlmgr install courier`。
- 生成物：`main.pdf` 随提交；aux/log/bbl 已在 `.gitignore`。

### B. 内容刷新（每轮或 case 有增减时）

- 任务总数 = A+B+C+D：**2026-11-09 = A:184 B:210 C:271 D:263 = 928**。
- 生产扫描口径（**11/05 快照，历史值**）：42 hosts / 5,822 行 / dedup 2,560（mc≥1）/ mc10 = **1,929** / mc30 = 1,511。**11/09 换池后以 `summary_stats.json.mc10` 为准。**
- 资产规模（survey）：**698 workstations / 2,850 users / 52,698 session files / 24,085 IC-EDA matched**。
- 领域数：**13**（论文口径；survey 的 11 类是更粗分类）。
- 评测样本：**48 cases / 4 domains**（`benchmark/designflow/cline_eval/`），最终扩到全量。
- 同步位置：摘要、§1 Intro、§2 Benchmark、§4 Experiments、§7 Conclusion、§9 Reproducibility、App A/B/C、README。
- 数字来源优先级：`benchmark/designflow/summary_stats.json`（scan/users/mc30）> 各 shard MEMORY 的 ledger 计数 > 论文旧值（禁止沿用旧值）。

### C. 交付

- `main.pdf` 必须重新生成并随提交（10 页；0 undefined citation）。
- 提交信息：`paper: refresh stats (<date>, N=<total>)`。
- 若 case 计数未变，只做编译回归，不必改数字。

