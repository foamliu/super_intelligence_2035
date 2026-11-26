# trace_deepread: 1793607569089_mmwky (rose3wang @ hfeg0pkn003, mc=17)

- **session**: `/home/rose3wang/.cline/data/sessions/1793607569089_mmwky/1793607569089_mmwky.messages.json` (112 KB, 34 msgs)
- **user**: rose3wang (已有 2 case: r160 PdkMutateVerify / r161 TclAreaUpdate，本 session 第 3 个)
- **keywords**: `dbGet`(4) + `innovus`(2) — 真·Innovus TCL scripting session (psensor + eFuse pre_floorplan)
- **domain fit**: pnr_signoff (Innovus pre_floorplan 物理设计初始化脚本)

## 对话流 (34 msgs)
- **USER#0 (idx0)** = `/proj/lacaa/V0/workdir/brettzhu/EfuseGrp/run/rev20261026_wodft_1026_try1/insert_script/pre_floorplan.tcl\n解释一下这个脚本` — **clean 需求**(提出目标, 无根因/无修复方案) → **A-faithful 合格**
  - assistant (idx1) `read_files` 读真实 /proj/.../pre_floorplan.tcl → (idx3) 10-段详解 audit
- **USER#4 (idx4)** = `layout里面的blockage的作用？` — 概念问答 (blockage 用途)
- **USER#6 (idx6)** = `"ONE TEAM"概念...共创"ONE ALS"专属Logo 输出个logo` — 创意任务 (与 EDA 无关, 生成 SVG logo via matplotlib/PIL, 多次 editor 失败后直接写 SVG)
- **USER#30 (idx30)** = `/proj/lacaa/V0/workdir/rose3wang/PR/psensor/run/rev20261103_wodft_TV1_try1/insert_script/pre_floorplan.tcl\n解释一下` — 第二个脚本 (psensor, 与 eFuse 同族但规模/命令不同)
  - assistant (idx33) psensor 详解 + 与 eFuse 对比表

## 真实脚本内容 (从 tool_result 完整恢复)
### eFuse pre_floorplan.tcl (asset A, 49 lines)
- `set site_x 0.051 / site_y 0.180`
- `set x [expr $site_x * 107463]` → core_x ≈ 5480.613 µm
- `set y [expr $site_y * 12222]` → core_y ≈ 2199.96 µm (大设计 ~5.48mm × 2.20mm)
- `floorPlan -site core -d $x $y 1.02 1.08 1.02 1.08 -noSnapToGrid -flip f`
- `snapFPlan -block`
- `add_tracks` m1 pitch 0.034 + 4×0.028 + 0.034, mask_pattern 1 2 1 2 1 2, m2 vert 0.0255
- **clock_ports** via `dbget [dbGet top.terms.net.isClock 1 -p].name` (自动识别)
- input_ports **排除** clock (foreach + lsearch -exact)
- `editPin` I/O layer 5 pinWidth 0.02 offsetStart y/2; clock layer 7 pinWidth 0.02 offsetStart y/2
- `source fp.tcl` (macro 摆放)
- `deleteHaloFromBlock -allBlock` + `addHaloToBlock 5 5 5 5 -snapToSite` (halo)
- `source edit_internal_ports_efuse.tcl`
- `specifyCellPad XOR2D1DBCP51H180L6W*T5*VT -left 1 -right 1`
- `source add_boundary_cell.tcl` / `power_dbc.tcl`
- `clearGlobalNets` + `globalNetConnect VDD/VSS -type pgpin`

### psensor pre_floorplan.tcl (hidden B, 57 lines) — 与 A 关键差异
- core 394×113 sites → ~20.094 × 20.34 µm (极小硬宏, ~273× 小于 A)
- floorPlan margins **1.08 1.08 1.08 1.08** (均匀, vs A 的 1.02/1.08)
- **`createRow -site bcore`** (A 无, 特殊行类型)
- clock_ports = **`"CLK CLK_OSC*"`** (literal 硬编码, vs A 的 dbget isClock 自动)
- input_ports **不排除** clock
- editPin I/O offsetStart **`y/2 -2`** (A 是 y/2); clock pinWidth **0.038** (A 是 0.02, 更宽)
- **`foreach clk $clock_ports { dbset ...pStatus unplaced }`** (A 无, 跨行)
- **`snapFPlan -pin`** (A 无)
- **`editDelete -nets {VDD VSS} -shape {STRIPE FOLLOWPIN}`** (A 无, 删 followpin)
- **`setViaGenMode -ignore_DRC true`** (A 无)
- 无 halo / 无 specifyCellPad (A 有)

## 金标准 = assistant 实际产出的 audit explanation
- eFuse 10 段: Die 尺寸计算 / Tracks / Port 分类 / Pin Placement / Macro 摆放 / Halo / 内部端口 / Cell Padding / 边界单元 / Power
- psensor: 同结构 + vs-eFuse 对比表 (规模/Row/时钟识别/Pin宽度/Followpin/ViaGenMode/snapFPlan/Macro)

## case 合成 (FloorplanTclAudit-001, pnr_signoff, A档, L2-static)
- **交付**: `audit_pre_floorplan.py` (Python3 CLI `<tcl> [-o out.json]`) 静态解析 Innovus pre_floorplan.tcl → JSON 审计报告 + 对附件的 audit.json
- **资产 A**: eFuse pre_floorplan.tcl (49 lines, 真实)
- **隐藏 B**: psensor pre_floorplan.tcl (inline 于 check.py, 与 A 同族但 7+ 字段不同)
- **边界 C**: 极简 TCL (仅 floorPlan + globalNetConnect, 测不崩溃)
- **reference audit_pre_floorplan.py**: 两遍解析 (line-continuation join + comment detect) + regex 提取 25 字段 + editPin 分类 (clock vs io by pin_target) + 跨行 foreach_clk_unplaced (fulltext 检测)
- **check.py 15 conds (a-o)**: (a)zip 含 .py (b)compile (c)B 跑出 JSON (d)B core_x≈20.094 (e)B core_y≈20.34 (f)B margins 全 1.08 (g)B createRow+bcore (h)B clock literal+CLK/CLK_OSC (i)B input_excludes_clock=False (j)B editPin_io offset y/2-2 (k)B editPin_clock pinWidth 0.038+layer7 (l)B foreach_clk_unplaced (m)B snapFPlan -pin (n)B editDelete_followpin+setViaGenMode (o)反硬编码(A≥4字段不同+A core≈5480.6+A halo+cellPad)+3-seed稳定+边界C不崩+源码无def check/无硬编/有regex
- **自验**: reference_submit.zip PASS(15/15) + 3 negatives(naive_noop/print_only/ref_delete_core)全 FAIL + §4.9(a)(b)(c)全 FAIL; 断言闸门 k_rationale=k_check=15≥8 PASS; jsonl test==disk check.py (sha 02f8a5f9fe47)
- **L2 = subprocess 跑候选于 B/A/C(纯 Python 静态 TCL 解析, 无 EDA 二进制, judge 本地跑)**

## BLOCKER 状态
- BLOCKER ③ 再确认: 严格 digital-tool 关键词集 (verdi/vcs/dc_shell/.../pt_shell) fresh 仅 13 个, 且多 analog-mixed; 放宽集 (含 synthesis/tcl/verilog) 多为 netlist/schematic analog (easont as67p/okq91/t0aom) 或 waveform (shaoyou elali/80yiq/cch2o). 本 session mmwky 是稀缺真·Innovus-pnr-flavored (dbGet+innovus 实证).
