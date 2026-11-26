# sbaad — signal→pattern→inc cross-ref (zmzhang, hfeg0plg98, mc122, digital)

**session**: `1793967043660_sbaad.messages.json` (zmzhang @ hfeg0plg98, 11/09 scan, mc122)
**keywords**: `verilog:1762;analog:92;pex:8;netlist:4;.def:4;pyaether:2` — verilog-dominant, A-domain (digital/DDR5 pattern testmode xref)
**NMSG**: 253, NUSTR: 129 (but **2 real user turns**, rest empty/tool_result)

## 用户意图（原话）

**U#0**: 「我给你一个文件 `/proj/drgqx/.../cmname`，里面有很多信号名，你帮我在路径 `.../patterns/cmds_testmode/` 下的文件和文件夹中的文件里去找包含这些信号名的文件，然后去路径 `.../Regressions/` 下以 `.inc` 结尾的文件中去找到有包含这些文件名的文件，并记录信号名和文件名的对应关系给我」

**U#241**（cmname 更新后重跑，扩 scope）: 同上 + 「同时在路径 `.../Regression`（不带 s）下的文件里去找包含这些信号的文件，并记录信号名和文件名的对应关系给我」

→ **单轮闭环 produce-task**（2 user turn，第 2 turn 是更新+扩 scope，同任务）。用户**未给根因**（不是"为什么失败"，是"找对应关系"）→ A-faithful 合格。deliverable = 脚本 + 映射报告（结构化 signal→file→inc 对应）。

## agent 工具链

1. `read_files` cmname → 读信号名清单
2. `list_allowed_files` patterns/cmds_testmode/ + Regressions/ → 发现是 symlink，需 `readlink -f`
3. `run_commands` ls/readlink → 确认目录结构
4. `editor` ×~20 编辑 `/home/zmzhang/search_signals.py`（Step1 读 cmname / Step2 os.walk patterns 找信号→文件 / Step3 搜 .inc 找文件名 / Step4 输出映射）
5. `run_approved_command` python-runner 跑脚本 → 2698 mappings，输出过长
6. `editor` 精炼：过滤 swap/backup 文件，聚焦 .v/.sv pattern 文件
7. cmname 更新（95→119 信号）→ 改 `build_report.py` 重跑 → `signal_pattern_inc_mapping.txt`
8. `read_files` 报告关键段 → 给出 SECTION A（signal→pattern→inc）+ SECTION B（signal→regression 直接匹配）+ stats

## 关键产物 / 输出结构

`signal_pattern_inc_mapping.txt`：
- **stats**: cmname 信号总数 119 / patterns 中找到 101 / Regression 直接找到 26 / 同时两处 24 / 仅 patterns 77 / 仅 regression 2 / 两处都未找到 16
- **SECTION A**（signal→pattern 文件→.inc 文件，20 信号）: 例 `cm1_io_Tccdl → cmds_dll/TM_NBTI.v → tm_NBTI.inc, tm_dll.inc, tm_dll_NBTI.inc, tm_dll_clkmon.inc, tm_dll_connection.inc`（5 inc）；`cm1_io_DLLCDLGateSEL → TM_inc.v → 28 个 .inc` + `→ tm_sweep.v → tm_sweep.inc`（同信号 2 个 pattern 文件）
- **SECTION B**（signal→Regression 文件直接匹配，30 信号）: 例 `testmode_weki.run` 含 9 信号

## A-faithful 判定

- 用户给 produce-task **未给根因** → A-faithful 合格
- 但真实 cmname / patterns / Regressions / Regression 在 `/proj/drgqx/V0/simdir/...`（私有 /proj，沙盒不可达）→ A-faithful（真实文件做 merged-file check）**INFEASIBLE** → **B 档 synthesized**
- B 档：构造自包含 cmname_A/B + patterns_A/B + Regressions_A/B + Regression_A/B（不带 s），deliverable = `signal_file_xref.py` 纯 stdlib CLI

## 合成方向（B 档）

- archetype: **2-layer cross-ref**（signal→pattern.v→Regressions.inc）+ **direct branch**（signal→Regression 文件）— 与 r426 TmPatternXref-001（testmode→pattern xref）同构但多一层 inc 引用 + 直接 regression 分支
- 匹配规则：整词（word boundary，非子串）→ 子串陷阱；跳过 backup（~/.swp/.bak/.tmp）→ backup 陷阱
- 输出 JSON: stats(7 计数) + section_a(signal→pattern_file→inc_files) + section_b(signal→regression_files) + unmatched
- A: 12 信号 / 5 子目录 pattern / 9 inc / 4 regression file
- B: 15 信号 / 不同子目录(cmds_top/phy/pll/fuse/io) / multi_ref.inc 引用 2 pattern / top_only.v 无 inc / 2 unmatched / 子串+backup 陷阱
- k 目标 17，L1 stdlib，判分用独立 token-oracle（非正则）
