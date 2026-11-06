# Deepread: 1791602435253_66tx9 (ynbai @ hfhds201) — lib_cell.list 生成

## trace 元信息
- session: `1791602435253_66tx9` (ynbai @ hfhds201)
- 84 msgs / 1.6MB? 实际：netlist 17 hspice(低)，schematic/netlist dominated（mc=162）
- 11-05 19:28 summary.tsv 命中：mc=162，tools="2671 schematic 1047 netlist 17 hspice 3 cellview 1 virtuoso"
- scout 路径：hfhds201 not-ledger spice-tool 候选（44 个）中按 mc 排第 7（前 6 已被前轮 scout 拒: wg5u2=schematic dominated/3s3zx=trivial"你能干什么"... 实测 3s3zx trivial, 66tx9 clean）

## USER#0（逐字原文，A-档任务说明）
> 我提供cell list文件和netlist，你帮忙输出lib_cell.list文件，文件格式为Library Cell，netlist内部格式为\* Library : drvqa_cmos_io
> \* Cell    : IO_DqLdMdl
> \* View    : schematic
> ，输出文件为drvqa_cmos_io IO_DqLdMdl，生成脚本，cell list文件为/proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/netlist_lat，网表文件为/proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/Netlist_Vcap_20260918AM_Fullchip_0918DB/netlist，生成到输出到/home/ynbai/下

### 选轮判定（A-档规则）
- ✅ 「提出需求 / 表达目标」轮：用户给目标（输出 lib_cell.list）+ 输入（cell list + netlist）+ 格式（Library Cell）+ 方法（生成脚本）。
- ✅ 未给根因，未给修复方案。
- ✅ 纯需求轮，可用作 A-档任务说明（prompt）。

## assistant 工具链（关键产物）
1. read_files cell list (netlist_lat) + netlist → 发现 cell list 含 `* Cell    : latrqLx1` 行；netlist 含 `* Library : <lib>` / `* Cell    : <cell>` / `* View : schematic` header block。
2. read_files netlist.log → 含 `Exporting design "LIBRARY/CELL/view"` 行（备选 mapping 来源）。
3. 设计方案（msg 45/64）：
   - 解析 cell list → 提取 `* Cell : <name>` 行的目标 cell 列表（去重保序）
   - 解析 netlist（或 netlist.log）→ 建 cell→library map
   - 对每个目标 cell 查 library，输出 `Library Cell` 到 lib_cell.list
4. editor 写 `/home/ynbai/generate_lib_cell_list.py`（msg 64–82）→ **文件被多次 edit 损坏，trace 末尾(msg 82)仍在 rewrite**，未确认用户接受最终产物。

## 金标准（合成，基于 USER#0 spec）
trace 末尾未闭合 → 按 spec 合成金标准（参 SlicerSizeOpt/VcoKvcoChar 模式）：
- **核心规则**：解析 netlist 中 `* Library : <lib>` / `* Cell    : <cell>` header block，建 cell→library map（**首次出现 wins**）；对 cell list 中每个 cell（`* Cell : <name>` 行，去重保序），若在 map 中 → 输出 `<Library> <Cell>`；不在 → 跳过。
- **traps**：
  - cell 出现在多个 library 下 → 取首次出现的 library
  - cell list 中重复 cell → 去重（首次保序）
  - cell list 中存在但 netlist 中找不到的 cell → 跳过
  - `* View :` 行 → 忽略（不输出）
  - `* Cell :` 行出现在首个 `* Library :` 之前（cur_lib=None）→ 跳过该 cell
  - header 行空白变体（`* Cell:` / `* Cell    :` / `* Cell :`）需灵活匹配
  - 网表 body（.subckt/X inst/.ends 等）不参与 mapping

## case 合成计划
- case_id: `EDA-Eval-DesignFlow-LibCellListGen-001`
- domain: spice_sim（netlist 解析供 finesim/sim flow），track: faithful A-档，level: L1（离线 Python 网表解析）
- 交付：通用 `gen_lib_cell_list.py <cell_list> <netlist> <output>` → 输出 `lib_cell.list`（每行 `<Library> <Cell>`）
- A 资产：netlist_A（8 block，3 library，含 multi-lib/dup/not-found traps）+ cell_list_A（6 cell，含 dup/not-found）
- hidden B：netlist_B（7 block，4 library，不同 lib/cell/数量）+ cell_list_B（6 cell，含 missing/multi-lib）
- reference: gen_lib_cell_list_ref.py + check.py（k=12 断言 a-l）+ negative/(5 stub)+negative_selftest.py+reference_submit.zip
- 预期 A 输出 4 行，B 输出 5 行（A≠B 跨输入护栏）
