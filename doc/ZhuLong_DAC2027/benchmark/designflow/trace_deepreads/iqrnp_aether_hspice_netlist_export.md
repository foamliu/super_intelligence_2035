# iqrnp — Aether HSPICE netlist export (deepread memo)

- **session**: `1795004858414_iqrnp` (mc=567, claimed r848)
- **user/host**: scarle @ hfhds201 (=10.129.32.75)
- **provider/model**: cxmt-deepseek-flash / deepseek-v4-flash
- **engine**: aether (pyAether)
- **cwd**: `/home/scarle/agentdir/dscqa/V0_metalDBR/`
- **started**: 2026-11-18T12:27:38Z; 298 msgs, 937KB
- **trace fork chain**: none
- **title**: masked by skill-creator preamble; real task in user msg idx 4

## Real task

抽特定电路的 HSPICE 网表，Lib/cell/viewname 作为输入。子任务 1: `stdcells_ac/Dlyrc_gut/schematic` → 输出到 `/rundata/dscqa/V0/simdir/finesim/workdir/scarle/simulation`。子任务 2 (config view DDR6TOP) 跑到 sandbox timeout，且其产出的 `DDR6TOP_config_IDD5_trans.sp` 与子任务 1 的 `Dlyrc_gut.sp` 内容完全相同（config view 回退到 schematic）。→ **取子任务 1 作为 case**。

用户原话（msg 4/6/8）：
- `stdcells_ac/Dlyrc_gut/schematic`
- `使用路径/rundata/dscqa/V0/simdir/finesim/workdir/scarle/simulation`
- `已启动`

## Agent path（143 tool_uses）

1. RAG API search（aeOpenDesign / mdeSetNetlistViewList / seGuiShowNetlist / form widgets）
2. 写 Tcl `aether_netlist_export.tcl` 直接 `source` → `invalid command name "Aether"` / `aeOpenDesign Extra arguments`
3. 切 **pyAether** Python 接口
4. 迭代调试 ExportNetlist 表单 widget：
   - `seGuiShowNetlist()` 只弹表单不写文件
   - `setFormComboBoxIndex(typeComboBox, 2)` 选 HSPICE（idx=2，非 0/1）
   - `setFormValue(outfileLineEdit, path)` 设输出路径
   - `guFormOK(form="ExportNetlist")` 提交
5. 跑通 → 产 `Dlyrc_gut.sp`（4387B / 113 行）
6. 沉淀可复用脚本 `export_hspice_netlist.py`

## Reference solution（trace-verbatim）

`/home/scarle/agentdir/dscqa/V0_metalDBR/export_hspice_netlist.py`（3644B）— 函数 `export_hspice_netlist(lib, cell, view, output_dir, output_filename=None)`：
`aeOpenDesign(lib,cell,view,"readOnly")` → `mdeSetNetlistViewList("hspice", "hspiceText hspiceD spice schematic veriloga")` → `seGuiShowNetlist()` → `setFormComboBoxIndex(typeComboBox, 2)` → `setFormValue(outfileLineEdit, path)` → `guFormOK(form="ExportNetlist")` → 验证文件存在。

## Reference netlist `Dlyrc_gut.sp`（4387B / 113 行）

来源：trace idx 182 `print_log`（agent `cat`+`print`，但 print_log 截断于 2593/4387 字节）。完整原文件在 .75 `/rundata/dscqa/V0/simdir/finesim/workdir/scarle/simulation/Dlyrc_gut.sp`，属 `scarle:dscqaw`，e0031982（guest/eda_agent）**perm-denied**，无法直读。

已 verbatim 捕获部分：
- header: `*Dlyrc_gut` / `* Type : hspice` / `* Tool : AETHER-SE` / `* Date : Wed Nov 18 20:40:59 2026` / `* User : scarle` / `* Top Design : stdcells_ac/Dlyrc_gut/schematic`
- `.subckt switch_close POS NEG` / `r0 POS NEG r=0.001` / `.ends`
- `.subckt switch_open POS NEG` / `.ends`
- `.GLOBAL vbn! vbp! vcc! vss!`
- TECHLIB `.SUBCKT nand2 A B Y vbulkn! vbulkp! vcc! vss! WP2=... ` (4 管 XMMN1/XMMN2/XMMP1/XMMP2) / `.ENDS nand2`
- TECHLIB `.SUBCKT brknet PLUS MINUS r=1m` / `.ENDS brknet`
- TECHLIB `.SUBCKT brknetM0 A B` (XRRI0) / `.ENDS brknetM0`
- TECHLIB `.SUBCKT inv A Y ... ` (XMMN0/XMMP0) / `.ENDS inv`
- stdcells_ac/Dlyrc_gut section header + `**TopDesStart` + 顶层 instance `XMMN13 vss! l422l vss! vbn! ntn_m w=1.51e-6 l=1.5e-6 nf=1` / `XMMN7 mpull out net0105 vbn! ntn_m` → **truncated**（顶层 body 余 ~1.8KB 未捕获）

**重建**：`Dlyrc_gut_ref.sp` = verbatim 捕获部分 + `.END`（顶层 body 仅 2 条 instance，标注为 print_log 截断所致）。结构水印 `XMMN13` 用于 check.py (o) 防手织。

## Case

`EDA-Eval-DesignFlow-AetherHspiceNetlistExport-001`（B.jsonl line 396, domain=spice_sim, layer=L1, k_check=15）。produce 形态：可复用脚本 + 真跑网表。check 静态校验脚本 + 结构水印校验网表。§4.9: 18 neg 全 FAIL NEG_RC=0, ref PASS。
