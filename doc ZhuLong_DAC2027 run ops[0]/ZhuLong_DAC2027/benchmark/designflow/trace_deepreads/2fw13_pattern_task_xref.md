# 2fw13 — Pattern-Task Cross-Reference Analyzer (deepread)

- **session**: `1792654323443_2fw13.messages.json`
- **user / host**: graywang / hfeg0pjn140 (10.129.40.149)  [also on hfeg0plg108]
- **mc / kw**: mc51 · `verilog:3981;netlist:26;analog:24;.def:16;pex:6;lib.defs:4;aether:4;drc:2`
- **size / msgs**: 720958 B / 28 msgs (15 user / 13 asst) · single-turn · 2026-10-22
- **agent**: lead / deepseek-v4-flash
- **file location**: live rotated to `.snapshot/hourly-new.2026-11-12_0000/.cline/data/sessions/1792654323443_2fw13/1792654323443_2fw13.messages.json`

## User intent (original, A-faithful)

> 帮我分析这个这个主目录 `/proj/drgqx/V0/simdir/verilog/graywang/verilog.ddr5.drgqx.move_testn/` 下的子目录 `patterns/cmds_mrs` 中的文件在其子目录 `Regressions/` 中文件的哪些文件中有出现

即：`patterns/cmds_mrs/` 下的 verilog 文件定义了若干 SystemVerilog `task`，`Regressions/` 下的 `.run`/`.inc` 文件会调用这些 task。用户要的是一份「cmds_mrs 文件 → Regressions 文件」的交叉引用报告（哪些 cmds_mrs 文件的 task 被 Regressions 引用、被哪些引用）。

## Agent 工具链（13 asst turns）

1. `list_allowed_files` cmds_mrs → 14 entries (symlinks → `/proj/drgqx/V0/sim/verilog/sos_manage/ddr5/drgqx/ddr5_tb/patterns/cmds_mrs`)
2. `list_allowed_files` patterns → 找 Regressions 子目录
3. `run_commands` readlink/ls 解 symlink
4. `run_approved_command` (shell-runner) readlink
5. `list_allowed_files` ddr5_tb + simdir
6. `list_allowed_files` `/rundata/...` cmds_mrs + Regressions （改用 /rundata 路径）
7. `read_files` mrs_fsm.run / mrr.run — 看 .run 文件如何引用 task（`taskname()` 调用）
8. `read_files` cmds_mrs/*.v — 提取每个 .v 定义的 task 名
9. `search_codebase` 12 个 task 名 — **超时**（目录太大）
10. `run_approved_command` (python-runner) `/home/graywang/analyze_cmds_mrs_refs.py` — 文件不存在
11. `editor` 新建 `analyze_cmds_mrs_refs.py`（核心 deliverable）
12. `run_approved_command` (python-runner) 跑脚本 → exitCode 0
13. final text：整理成中文报告（task 表 + 引用表 + 未引用 task + 文件对应表）

## Deliverable: `analyze_cmds_mrs_refs.py`（核心，纯 stdlib）

行为：
1. `cmds_mrs_files = sorted(os.listdir(alt_cmds_mrs))`，过滤 `.v`/`.sv`/`.inc`
2. 对每个文件 `re.findall(r'\btask\s+(\w+)\s*[\(;]', content)` 提取 task 定义 → `file_to_tasks[fname]` / `task_to_file[task]`
3. `task_names_sorted` 按 len 降序（避免短名贪婪吃掉长名），构造 `re.compile(r'\b(' + '|'.join(re.escape(t)) + r')\s*\(')`
4. 扫 `Regressions/` 每个文件，`task_pattern.finditer` → `task_refs[task] = set(reg files)`
5. 输出 3 段：Step1 task 列表 / Step2 每文件引用 / Step3 summary（file→refs + per-task refs + unreferenced）

关键不变量：
- **task 提取正则** `\btask\s+(\w+)\s*[\(;]` — 匹配 `task foo(` 或 `task foo();`
- **引用匹配正则** `\b<name>\s*\(` — 词边界 + 可选空白 + `(`，避免 `mrr` 误匹 `mrr_default(`（`_` 是 word char，`\bmrr\b` 后跟 `_` 不满足 `\b`… 实测 `\bmrr\s*\(` 不匹 `mrr_default(`，因 `mrr` 后是 `_` 不是 `(` 或空白）
- **长名优先** alternation 顺序：`mrr` 与 `mrr_default` 同存时，`mrr_default(` 先匹长名（虽然 `\s*\(` 锚点已足够，但保留 faithful）
- **latin-1 解码** `encoding='latin-1', errors='ignore'` 防中文/特殊字符崩溃
- **只扫普通文件** `os.path.isfile` 跳过子目录/symlink 目录

## 真实结果（脚本输出，摘要）

cmds_mrs 14 entries，9 个有 task 定义：
- `mrs_fsm.v`: mrs_fsm, act_writeap_mrr, act_readap_mrr, act_write_pre_mrr, act_read_pre_mrr, pd_mrr, mpc_mrr, ref_mrr, mrr
- `mrr_default.v`: mrr_default
- `mrw_mrr.v`: mrw_mrr
- `mrr_dfe.v`: mrr_dfe
- `mrr_dfe_unused.v`: mrr_dfe_unused
- `mrr_new.v`: mrr_new_regs
- `mrr_3deep.v`: 140+ 个 SRE*/MRR* task
- `mrr_three_deep.v`: 220+ 个 task
- `mrr_3deep.inc.v`: random_addr, tpd_extend, random_insert

引用：mrs_fsm→mrs_fsm.run/mrs_fsm.inc · mrr_default→mrr.run/mrr_default.run · mrw_mrr→mrr.run/mrw_mrr.run · mrr_dfe→mrr.run · mrr_dfe_unused→mrr.run · mrr_new_regs→mrr_new.run · mrr_3deep*→mrr_3deep.run · mrr_three_deep→mrr_three_deep.run

未引用：mrs_fsm.v 的 act_*/pd_mrr/mpc_mrr/ref_mrr/mrr（内部子 task）· mrr_3deep.inc.v 的 random_addr/tpd_extend/random_insert · mrr_three_deep.v 的 basic_write/basic_rdback

## A-faithful 判定

- 用户**未给根因**（不是 bug-fix 题），是「新需求 produce-task」→ A-faithful 合格（符合 §4.6 A 档：用真实需求，agent 自主实现）
- 单轮闭环、纯 stdlib、offline-verifiable → **L1 log-parser/cross-check archetype**
- 不依赖 /proj 路径可达（脚本本身纯 stdlib，只要给 base dir 即可）→ 沙盒友好

## B 档合成 plan（PatternTaskXref-001, digital L1）

**deliverable**: `pattern_task_xref.py`（纯 stdlib）
- `--base <dir>`（含 `patterns/cmds_mrs/` + `Regressions/`）、`--out <report.json>`
- 提取 cmds_mrs 中 `.v`/`.sv`/`.inc` 文件的 task 定义（`\btask\s+(\w+)\s*[\(;]`）
- 扫 Regressions 所有普通文件，词边界 + `\s*\(` 匹配 task 引用
- 输出 JSON：cmds_mrs_files（含 tasks）/ regressions_files / task_to_file / task_refs / file_refs / unreferenced_tasks / summary

**A（visible）**: 4 cmds_mrs .v + 4 Regressions .run（小规模，mrs_fsm/mrr_default/mrw_mrr/mrr_dfe 系列）
**B（hidden）**: 5 cmds_mrs .v + 5 Regressions .run（不同 task 名/文件名/引用模式，含 1 个未引用 task、1 个名字互为前缀的 task 对验证词边界）

**check.py 独立条件（k≥10）**：
1. exit 0 + JSON 可解析
2. 顶层 keys 齐全
3. cmds_mrs_files 数 = B 实际 .v/.sv/.inc 数
4. regressions_files 数 = B 实际文件数
5. task_to_file 含所有期望 task 且映射正确
6. 某具体 task 的 file_refs 正确
7. task_refs 对被引用 task 非空且正确
8. unreferenced_tasks 含期望未引用 task
9. summary.total_tasks = referenced + unreferenced
10. **词边界**：短名 task（`mrr`）不误匹长名（`mrr_default`）的引用文件
11. .inc（无 task 定义）文件出现在 cmds_mrs_files 但 tasks 为空列表
12. file_refs 对一个被多 reg 引用的 cmds_mrs 文件返回所有 reg 文件

**negatives**: naive_empty（空 JSON）/ print_only（打印期望串不分析）/ core_removed（删 task 提取，task_to_file 空）/ substring_match（用 `in` 子串匹配而非词边界，误匹）→ 全 FAIL

**§4.9**: (a) 空壳 (b) print 期望串 (c) 删核心 → 全 FAIL
