# trace deepread — 1789520291803_uhir2 (kenwang @ hfeg0plg16)

- shard: C · domain: physical_verify (Calibre DRC) · round: 329
- match_count: 312 · status: completed (real cline trace)
- case_id: EDA-Eval-DesignFlow-DrcMetalOptGen-001
- track: A-faithful · level: L1 · k_check = k_rationale = 12 (a-l)
- ledger: claimed → marked case (2026-11-10)

## 用户真实意图 (U#0 逐字原文)

> /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/test/ 在当前路径下面有2个文件 drc_auto.py ts_auto.sh ,这是一个拆分metal option的脚本,可以根据 不同的metal option 分配 x或者 y，或者yy 等 字母对用的metal 层, 现在我遇到一个问题，当我有一条 rule ，他是包含所有的metal 层的时候，但是每一个metal option对应的又不是同样多的metal 数量，我如何修改这个脚本，可以让它在不同的metal option 中通用呢，你有不理解的可以先反问我，

## 真实场景

用户 `kenwang` 在 `metalOption/test/` 下有一套按 metal option（13M/15M/17M，每个 option 对应不同 metal 层数量）拆分生成 Calibre DRC rule deck 的 `drc_auto.py`。脚本通过命令行变量（`xa_start`/`xa_end`/`x_start`/`x_end`/`y_start`/`y_end`/`z_start`/`z_end`/`mtsk=...` 等）描述每个 option 的层范围，模板支持指令 `#output_path` / `#filename` / `#var` / `#loop` / `#end_loop` 与占位符 `$<var>`（变量替换）、`$`（=top_metal）、`#`（=当前 loop 索引）、`#-n`/`#+n`（索引算术）。

核心问题："包含所有 metal 层"的 rule 在不同 metal option 下 metal 数量不同（13M=11 层、15M=13 层、17M=15 层），需要脚本通用化而非为每个 option 硬编码。

## 真实 assistant 行为

- 对 `drc_auto.py` 做了大量分块编辑（chunked editor edits），替换 `build_opt_map` / loop 展开 / 变量替换逻辑。
- 附件包括多个真实 DRC rule deck 模板：`4_5_54_My.rules`（808 行可见，trace pager 截断自 2913 行）、`4_5_51_Vxa.rules`、`4_5_55_Vz.rules`、`4_5_56_Mz.rules` 等。
- 因 chunked edit 出现 IndentationError —— 真实 gold 不可直接用。

## case 改造（A-faithful）

- 真实 gold 不可用（chunked edit buggy）→ 重新撰写 clean self-contained `drc_auto.py` gold：
  - 支持 `#output_path` / `#filename` / `#var` / `#loop` / `#end_loop` 指令
  - 支持 `$<var>` 变量替换、`$`（=top_metal）、`#`（=loop 索引）、`#-n`/`#+n` 算术
  - `build_opt_map_from_vars`：从 `*_start`/`*_end` 变量对自动派生 metal→option 映射
- A 输入（可见）：`4_5_54_My.rules`（808 行真实 DRC deck 模板）+ `ts_auto.sh` + `readme` + `prompt.txt`（U#0 逐字）+ `task_brief.md`
- **B 输入（hidden，结构不同于 A）**：合成 `B_template.rules`，单层循环——all-metal loop `xa_start..z_end` step 1 + y-loop step 2
- 三组配置 metal 数量各异（反硬编码）：B13=11 metals / B17=15 / B15=13

## check.py 12 条件 (a-l)

| 条件 | 断言 |
|---|---|
| a | submit.zip 合法且含 drc_auto.py |
| b | drc_auto.py 语法合法 (py_compile) |
| c | 三组配置 (B13/B17/B15) exit 0 并生成 out/B_metalopt.rules |
| d | B13 all-metal SP 计数=11 (M3_SP..M13_SP)，不含 M2/M14 |
| e | `#-1` 算术：ENC VIA2 M3 (n=3→#-1=2) .. ENC VIA12 M13 (n=13→#-1=12)，无越界 |
| f | y-loop step 2 → M7_Y/M9_Y/M11_Y (3 条) |
| g | `$<var>` 替换 → WIDTH > 2 (pad=2) |
| h | `$` = top_metal：B13 含 M13_SP 不含 M14_SP；B17 含 M17_SP |
| i | 非硬编码：三组 SP 计数 11/15/13 互不相同 |
| j | 只读守卫：运行后隐藏模板 MD5 不变 |
| k | B17 SP 计数=15，不含 M18_SP |
| l | B15 SP 计数=13，不含 M16_SP |

## negatives (6 + §4.9 三假)

| negative | 命中失败条件 |
|---|---|
| naive_hardcode_15 | 硬编码 M3..M15 → d/i/k (B13=13≠11) |
| print_only | 只打印不写文件 → c |
| fixed_no_loop | 静态 deck 忽略 loop → d |
| no_var_subst | 不替换 $<var> → d |
| crash_on_var | 遇 var 崩溃 → c |
| modify_input | 正确 deck 但改写输入模板 → **j** |
| empty_shell (fake) | 空壳 → c |
| print_expected (fake) | 打印期望串无生成 → c |
| name_only (fake) | 仅文件名注释 → c |

## 自验证

- .75 沙盒：ref PASS，9 negatives 全 FAIL ✓
- 本地（EDA-Flow-Bench repo）：ref PASS，negative_selftest ALL OK ✓
- hidden B_template.rules md5 = `f4625cb93dfb77239c65ececd2322caf`（local 与 .75 一致）
- check_sha256 = `68f80d4cf4c85955b40eb364a4e1e4b482ab218f949f02eac674902b12996833`，size=6589

## 关键

- 真实 gold 因 chunked edit 不可用 → 必须重写 clean gold，但仍忠实于真实指令格式（#loop/$<var>/$/#-arith）。
- B 结构与 A 不同（单层循环 vs A 的多层嵌套），三配置 metal 数量 11/15/13 各异是反硬编码核心。
- `#-1` 算术 + `$<var>` 替换 + `$`=top_metal 三者联合区分真模板引擎与硬编码/静态输出。
- 只读守卫 (j) 专门由 modify_input negative 命中。
