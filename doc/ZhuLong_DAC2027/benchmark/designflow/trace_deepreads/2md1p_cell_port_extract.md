# Trace Deepread — 1794912291025_2md1p — Cell Port Extract (spice_sim)

**Session**: `1794912291025_2md1p.messages.json`
**User**: guangmingz @ hfeg0plg58 (10.129.35.82)
**mc**: 232 (spice_sim dominant; kw: netlist:1027/waveview:252/lvs:23/analog:19/schematic:10/synopsys:8/hspice:6)
**Domain**: spice_sim (B shard)
**Date**: 2026-11-15 ~ 2026-11-17 (211 msgs, 18 real user turns)
**Trace source**: real task summary = "用 python 实现 extract_cell_ports.py：输入 --cell/--netlist 从 SPICE netlist 中识别指定 cell 的端口列表，迭代细化（大小写不敏感 / list 输出 / 原始字符串显示 / help 美化 / 短选项 -c/-n / 改名）"

## User Intent (A-faithful, verbatim)

**U#0 (msg 0, ts=1794912291671)** — verbatim:
> 用python实现脚本，功能为：
> 输入参数为--cell，--netlist，从指定的netlist中识别指定cell的端口列表 参考的网表/proj/dscqa/V0/simdir/finesim/dscqaF/Netlists/Netlist_Vcap_20261031PM_DDR6TOP/netlist

**U#1~U#11** — 迭代细化（逐条 verbatim 见 trace，关键口径）：
- U#1 (1794912706118): "将脚本中的英文注释改成英文"  → 注释全英文化
- U#2 (1794913024746): "修改脚本，对指定的cell名称不区分大小写"  → case-insensitive matching
- U#3 (1794913126438): "修改脚本的输出的port为列表格式"  → ports 输出为 Python list repr `[...]`
- U#4 (1794913417088): "修改脚本的输出的cell的显示，使用从网表中找到的原始的字符串，不使用用户给的输入参数，因为用户输入的参数可能所不区分大小写"  → 输出 `cell : <原始字符串>` 而非用户输入
- U#5 (1794913515790): "修改HELP信息，增加CELL是大小写不敏感的"  → help 文本含 "case-insensitive"
- U#6 (1794913590635): "增加输入的缩写，-c和-n"  → 加短选项 `-c`/`-n`
- U#7 (1794913684702): "优化help信息，打印美观一些"  → 美化 help
- U#8 (1794913790838): 给出期望 help 排版格式（`-c CELL, --cell CELL  cell name to query (case-insensitive)` + `-n NETLIST, --netlist NETLIST`）
- U#11 (1794914354371): "改成extract_cell_ports.py"  → 文件改名

**U#12~U#15** — 切到 waveview 信号查询 tcl（不同子任务，本 case 不锚定）
**U#16~U#17** — 切到 sim corner 提取脚本（不同子任务，本 case 不锚定）

A档合规判定：✓ 真实意图（自用网表解析工具）✓ 8 条迭代细化全部可独立断言 ✓ 用户原话可作 prompt

## 真实网表 (用户实际给的，msg 13 first 80 lines + msg 198 grep)

格式（SPICE .SUBCKT）：
```
*DDR6TOP
* Tool     : AETHER-SE
* Date     : Sat Oct 31 17:44:48 2026
* User     : guangmingz
* Top Design : dscqa_top/DDR6TOP/schematic
.subckt switch_close POS NEG
r0 POS NEG r=0.001
.ends switch_close
.subckt switch_open POS NEG
.ends switch_open
.SUBCKT IO_DqLdMdl DQ inh_vss
...
.ENDS IO_DqLdMdl
.SUBCKT probeI A B
v0 A B DC=0
.ENDS probeI
***.SUBCKT AG_DelayVdbiasForSim vdbias inh_vdd1 inh_vss   ← 被 *** 注释，不应匹配
***.ENDS AG_DelayVdbiasForSim
.SUBCKT IO_DqsCmlLatch CmlDivBias CmlDivBias0 CmlDivBias1 DqsN DqsP VpwlCmlDiv inn inp outn outp inh_vss
.ENDS IO_DqsCmlLatch
.SUBCKT IO_ZQLdMdl DQ inh_vddq inh_vss
.ENDS IO_ZQLdMdl
.SUBCKT IO_DqIbDfeSlicer Corner_ctrl<2> Corner_ctrl<1> Corner_ctrl<0> Data DfeEn ... inh_vcc inh_vss inh_vssz
.ENDS IO_DqIbDfeSlicer
```
关键 trap：
- `.subckt`（小写）与 `.SUBCKT`（大写）混合，必须 keyword 大小写不敏感
- `***.SUBCKT ...` 是被注释的 cell，不应匹配（lstrip 后以 `*` 开头 → 跳过）
- `Corner_ctrl<2>` 这种 bus 端口名带 `<>`，是普通 token，split 即可
- 用户的 647124 行大网表里 cell 名 `IO_DqsCmlLatch`（混合大小写），用户查询时若输 `io_dqscmllatch`（全小写）应能命中，但若输 `IO_DQSCCMLLATCH`（多了个 C，msg 77）则不命中——这是 typo 不是 case 问题

## 真实运行结果（trace msg 60/73/79/93/104/117/135）

| 查询 cell | 网表原始名 | port count | ports |
|---|---|---|---|
| `IO_DqsCmlLatch` | `IO_DqsCmlLatch` | 11 | `['CmlDivBias','CmlDivBias0','CmlDivBias1','DqsN','DqsP','VpwlCmlDiv','inn','inp','outn','outp','inh_vss']` |
| `IO_ZQLdMdl` | `IO_ZQLdMdl` | 3 | `['DQ','inh_vddq','inh_vss']` |
| `NonexistentCell_zzz` | — | — | exit 1 + `[ERROR] .SUBCKT definition for cell 'NonexistentCell_zzz' was not found in <path>.` |
| `io_dqslmlatch` (msg 49) | — | — | exit 1 (改名前 case-sensitive 时) |
| `IO_DQSCCMLLATCH` (msg 77, typo 多 C) | — | — | exit 1 |

## 最终脚本（agent 产出, /home/guangmingz/extract_cell_ports.py, 4778B, scp 取回）

完整 verbatim 见 `reference/EDA-Eval-DesignFlow-CellPortExtract-001/extract_cell_ports_ref.py`。核心要点：
- `get_cell_ports(netlist_path, cellname)` 返回 `(ports, line_no, found_cellname)`，未找到返回 `(None, 0, None)`
- 跳过空行 + `*` 开头注释行
- `.subckt` keyword 大小写不敏感（`toks[0].lower() != ".subckt"`）
- cell 名大小写不敏感匹配（`toks[1].lower() != cellname.lower()`）
- `found_cellname = toks[1]`（保留原始字符串）
- 支持 `+` 续行：命中后遇到 `+` 开头行则 extend ports
- 输出 4 行：`cell       : <found_cellname>` / `netlist    : <path>` / `port count : <N>` / `ports      : [list repr]`
- argparse: `-c/--cell` + `-n/--netlist`，`required=True`，help 文本含 "case-insensitive"
- `_PrettyHelpFormatter` 自定义 help 对齐（max_help_position=34, width=100）
- epilog 含 Examples + "Both short (-c / -n) and long (--cell / --netlist) options are accepted."

## Case 合成计划

- **task_id**: `EDA-Eval-DesignFlow-CellPortExtract-001`
- **mode**: design_flow, entry_point: outputs/submit.zip
- **domain**: spice_sim, **track**: faithful (A档), **layer**: L1 (纯 python 无 EDA 二进制)
- **asset A** (`design_A/netlist_A.sp`): 重建用户实际网表的代表性子集（switch_close/switch_open/IO_DqLdMdl/probeI/IO_DqsCmlLatch/IO_ZQLdMdl/IO_DqIbDfeSlicer + *** 注释 cell），格式 verbatim 自 trace msg 13/198
- **hidden B** (`hidden/netlist_B.sp`): 结构性差异 — 不同 cell 名混合大小写（vco_main/PllBias/CmlDriver/Ldo_Core 带续行/EsdClkBuf/BandgapRef），不同端口数，`+` 续行 cell，*** 注释 cell trap；hidden_manifest.json 列出 6 个查询场景 + 期望输出
- **check.py**: 跑 SUT 工具在 B 上 6 个查询 + --help + 退化提交回归，14 条独立断言 (a-n)
- **reference**: agent 的最终脚本 verbatim
- **negatives**: 5 个（empty_shell / print_only / core_deleted / hardcode_a / case_sensitive_only）
- **k_check = k_rationale = 14**

## trace_source metadata

```
trace_source = {
  "user": "guangmingz",
  "host": "hfeg0plg58 (10.129.35.82)",
  "session_file": "/home/guangmingz/.cline/data/sessions/1794912291025_2md1p/1794912291025_2md1p.messages.json",
  "match_count": 232,
  "real_task_summary": "用 python 实现 extract_cell_ports.py：输入 --cell/--netlist 从 SPICE netlist 中识别指定 cell 的端口列表，迭代细化（大小写不敏感 / list 输出 / 原始字符串显示 / help 美化 / 短选项 -c/-n / 改名）"
}
```
