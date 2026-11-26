# r118 shard C 深读：1792488619552_mt7ua（johnl Innovus APR + LEF 后处理）

## 元数据
- session: 1792488619552_mt7ua ｜ user: johnl ｜ host: hfeg0plg99 (10.129.32.99 等多 plg)
- mc=679（真实富: innovus:872 pyAether:332 netlist:180 dbGet:47 hspice:42 schematic:33 calibre:32 synthesis:31 virtuoso:28 dbCreateRect:17）
- 591 msgs / 1.95MB / 16h42m（2026-10-20 09:30 → 10-21 02:12）/ status=failed / terminal_marker=failed_external_process_exit
- agent: cline (deepseek-v4-flash), cwd=/home/johnl, provider=johnll
- ledger: r118 claim（physical_verify 域候选；本深读为 B-档合成准备，DEBT:1 下轮合成）

## 用户轮（A-档 seed 甄别）
- **USER#0（逐字，A-档合格 seed — 提出目标未给根因）**：
  `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/out/mapped.v  请在本文件夹建立工程，使用innovus完成此电路的版图 要满足时序约束，  .param pvcc=1.1 .param pvdd1=1.8 .param pvdbias=0.9323 .param t_osc_period='1.59n' .lib ".../G5_CIP_Model_D5_v0d5_Rev03_t03.sp" TT .lib ".../incFile_G5_CIP" bjt_tt/res_tt/nicap_tt/diode_tt .TEMP 25 这是spice库 还有其他的库你可能需要找 /proj/drcoa/V0/libs/drcoa_stdcell这是aether里面的`
- USER#227/333/348/358/360：「继续/完成layout/加油加油」（nudge，非 seed）
- USER#421（**A-档禁用** — 用户已给根因+修复方向）：「不要手改原点为零、猜测 SIZE 或批量重生成来掩盖问题」
- USER#430：「我们一起重新生成lef」
- USER#456（**A-档禁用** — 详细 prBoundary 诊断步骤 4 条）
- USER#525：「好的」
- USER#579（**A-档禁用** — 显式 SIZE 3.88 BY 6.71 + origin/FOREIGN 一致性要求）
- USER#590（**A-档禁用** — 「查 GenLEF 是否支持显式边界输入」修复方向）
- **ask_question#56**：agent 问「如何处理缺失的 stdcell 物理数据（cell LEF / tech LEF）？」2 选项；用户答「第二个 我不是有综合用的db .lib吗」→ 选「自动从 OA layout 生成 LEF + 用 .db 跑 Innovus」

→ 唯一 A-档 seed = USER#0。后续用户轮多给根因/修复（prBoundary/SIZE 3.88×6.71），A-档禁用，但可作 hint 不进 prompt。

## agent 真实工具链（591 msgs / 147 editor 写文件）
1. **env probe**（msg 15-50）：probe_env.sh..probe9.sh 探查 — Innovus 23.1 @ `/apps/cdsmgr/CRB/INNOVUS231/tools/bin/innovus`（23.35 tree 模式 d--------- 不可读）；stdcells_ac OA lib @ `/proj/drcoa/V0/libs/stdcells_ac`（含 `*LVS*` comb cells 的 layout/schematic/symbol/verilog 视图）；无任何预生成 LEF/tech.lef；timing lib `SS_0p98_m40c_lvs.db`；`run_commands` 被禁 → 用 `run_approved_command`（profile=shell-runner/python-runner）
2. **list_cells.py**（msg 58-78）：解析 mapped.v → 18 个 `*LVS*` comb 单元（aoi21LVSx1/aoi22LVSx1/aoi22LVSx2/invLVSx1/invLVSx2/invLVSx4/invLVSx6/nand2LVSx1/nand2LVSx2/nand3LVSx1/nand3LVSx2/nor2LVSx1/nor2LVSx2/nor2LVSx3/oai211LVSx1/oai21LVSx1/oai21LVSx2/or2LVSx1）；top=`addr_to_rowcol_v7`（N[8:0]→row[3:0]/col[4:0]/valid，纯组合）
3. **db2lib.tcl / run_lc.sh / run_lc2.sh / run_lc3.sh**（msg 58-104）：尝试 lc_shell .db→.lib 文本转换 — **最终放弃**（此环境 lc_shell/dc_shell write_lib 只支持 .db；Innovus 可直读 .db，无需 .lib）
4. **GenLEF 流**（msg 286-445）：`genlef_all.sh` / `genlef_chunk.sh` / `config/option.conf` / `config/tech.lef` / `combine_lef.sh` / `regen_all.sh` — asOut OA→GDS（`/apps/empyrean/tools/aether_new/bin/asOut` -gds -lib stdcells_ac -cell <c> -view layout -layerMap layer.map）→ ski-genlef GDS→LEF（`/apps/empyrean/skipper/.../bin/ski-genlef`，Tcl: lefGenCellPorts/lefExtract/lefWrite）。**问题**：源 OA 无 prBoundary → 输出 LEF `SIZE 0.0001 BY 0.0001`、`CLASS BLOCK`、无 `SITE`、几何在负坐标、ORIGIN/FOREIGN 非零
5. **postprocess_lef.py**（msg 383，**★ 核心可合成 gold，2075B**）：Python 后处理 raw genlef LEF — 从 RECT/POLYGON 几何 bbox 算真实 width → round_up_grid(site_w=0.1) → 几何平移 DY=0.43（min y→0）→ `CLASS BLOCK`→`CLASS CORE` → 插入 `SITE core ;` → `SIZE <w> BY 7.57` → `ORIGIN 0 0` → `FOREIGN <cell> 0 0`
6. **gds_layers.py**（msg 334，1142B）：GDS 二进制流解析器（struct.unpack 大端，rectype 0x0D=LAYER/0x0E=DATATYPE/0x14=BOUNDARY），统计 layer:datatype 计数
7. **Innovus flow.tcl + mmmc.tcl + run.sh + README.md**（msg 202-407，**L2 真跑 Innovus，B-档不可行**）：MMMC（create_rc_corner/create_library_set/create_delay_corner/create_constraint_mode/create_analysis_view，SS LVS .db）→ init_design（LEF+netlist+top）→ floorplan → PDN → place → route → signoff → export DEF/GDS/verilog/sdc；约束 set_max_delay 0.5ns
8. **prBoundary 调查**（msg 421-590）：ae_dump_all.py / gds_dump.py / ae_pyprobe.py 探查 pyAether prBoundary；install_gdspy.sh 装 gdspy 解 GDS；最终未完成 P&R（failed_external_process_exit）

## gold 评估
- **gold = postprocess_lef.py（msg 383，2075B）★ 选定**：确定性 LEF 文本后处理，physical_layout 特定（LEF = 物理版图抽象），stdlib-only，离线可验，真实坑丰富（grid round-up / POLYGON 多点平移 / CLASS BLOCK→CORE / SITE 插入 / SIZE 从几何 bbox 重算 / ORIGIN/FOREIGN 归一化 / DY 平移）。**B-档 L1-boundary 可合成**。
- 备选 gold（本轮不合成）：gds_layers.py（GDS 解析，更偏文件解析非版图核心）、flow.tcl（需 live Innovus，B-档不可行）

## B-档合成计划（下轮 r119 第一件事，DEBT:1）
- **case_id**: EDA-Eval-DesignFlow-LefPostprocessFix-001
- **domain**: physical_verify（LEF 抽象格式校验/修复；shard C 首个 LEF 后处理子主题，正交于现有 physical_verify 的 DRC/LVS/ERC/SVRF/ViaFill 系列）
- **档位**: B-档 faithful-seed-B-synthesized（A-档 seed=USER#0 逐字；gold 依赖 live Innovus/OA/asOut/ski-genlef → A-档不可行 → B-档离线 LEF 文本后处理模拟）
- **资产 A（忠实 USER#0 + genlef 输出形态）**：2-3 个 raw genlef LEF 文件（invLVSx1/invLVSx2/nand2LVSx1），含 `MACRO <cell>` / `CLASS BLOCK` / `SIZE 0.0001 BY 0.0001` / 无 SITE / RECT+POLYGON 几何在负坐标 / `ORIGIN -0.43 -0.43` / `FOREIGN <cell> -0.43 -0.43` / PIN A/Y + vcc!/vss!；prompt = USER#0 逐字 + 沙盒注（genlef 已产 raw LEF 在 inputs/，需写 postprocess_lef.py 后处理成可用 stdcell LEF）+ 接口 + task_brief ≤3 行
- **hidden B（结构不同，杀硬编码）**：2-3 个不同 cell（nor2LVSx2/nand3LVSx2/oai21LVSx1），不同几何尺寸/坐标，不同 site_w/site_h/DY 参数（如 site_w=0.12/site_h=8.0/DY=0.5）→ 杀 A 的 0.1/7.57/0.43 与 invLVSx1/nand2LVSx1
- **ref（postprocess_lef_ref.py，通用化禁硬编码）**：argv 取 input_dir/output_dir/site_w/site_h/DY → glob *.lef → 每 cell：从 RECT+POLYGON 算 bbox max_x → round_up_grid(w, site_w) → 几何平移 +DY → CLASS BLOCK→CORE → 插 SITE <site_name> → SIZE <w> BY <site_h> → ORIGIN 0 0 → FOREIGN <cell> 0 0 → 写 output_dir
- **check.py 14+ 条独立断言（k≥8，预拟 ①-⑯）**：
  ①(a) zip 含 postprocess_lef.py + 处理后 LEF 文件齐全 ②(b) py_compile exit0 ③(c) subprocess 跑 B exit0 无 Traceback ④(d) 输出 LEF 全 `CLASS CORE` 无 `CLASS BLOCK` ⑤(e) 每个输出 LEF 含 `SITE <name>` ⑥(f) SIZE 宽度 grid 对齐（w % site_w == 0，容差 1e-3）+ 高度 == site_h ⑦(g) `ORIGIN 0 0` ⑧(h) `FOREIGN <cell> 0 0` ⑨(i) 几何 Y 坐标平移 +DY（与输入比） ⑩(j) 宽度 == 输入几何 bbox max_x round_up grid ⑪(k) 无 `SIZE 0.0001` 残留 ⑫(l) 确定性 3×md5 一致 ⑬(m) 源码无 A 专属 token（invLVSx1/nand2LVSx1/0.43/7.57/0.1） ⑭(n) 输出含 B 专属 cell（nor2LVSx2 等） ⑮(o) cross-input guard：B 输出 LEF 的 MACRO 名 == B 的 cell，不含 A 的 cell ⑯(p) POLYGON 多点全平移（不只 RECT）
- **negative（≥5，各击穿不同条件）**：fake_empty→a；fake_print_expected（写伪造 `CLASS CORE` 文本但不真处理，B 跑后 LEF 仍 BLOCK）→d；fake_core_deleted（strip CLASS CORE 逻辑）→d；naive_no_translate（skip DY 平移）→i；naive_hardcode_width（固定 w=0.6）→j on B；§4.9 三假（empty/print_expected/core_deleted）全 FAIL
- **自验**：.75 上 ref PASS 14+/14+ + 6 negative 各击穿 + §4.9 三假全 FAIL
- **断言闸门**：k_rationale == k_check ≥ 8，`16 条断言：①..⑯` 开头

## 选料注（r118）
- 按 r115 笔记改进筛选：在 .75 跑 awk（mc>=30 + tools 含 maskLayout|.gds|.lef|.def|PG|via|placement|route|floorplan|版图|pnr|innovus）→ 排除 228 台账 → 逐字读 top 候选 prompt：
  - ukkn7 e0031668 mc=1478 → 实为 ERC run_all 2.1-2.8（与 r116a ErcBatchReasonFlow-001 i41yw 同主题，topic 饱和）→ 跳过
  - awgyg hbpeng mc=445 → prompt 是 LDDB2.0_EM_File.xls Excel 解析成 Python 类（纯 L1 Python，calibre/dbCreateRect 是工作目录背景噪声）→ 假阳性跳过
  - 9knot vincelu mc=862 → netlist:4456+hspice:226 主导 = spice_sim shard B → 跳过
  - as67p easont mc=786 → netlist:2023+schematic:776 主导 = schematic_netlist shard A → 跳过
  - wb03t cwei mc=691 → 已在台账（excluded）
  - **mt7ua johnl mc=679 → prompt = Innovus APR 建工程完成版图 + 时序约束，clean A-档 seed，innovus:872 + dbCreateRect:17 强 physical_layout 信号，新用户 johnl** → 当选
- mt7ua 是 L3 多工具流（env probe + list_cells + db2lib + GenLEF + Innovus flow + prBoundary 调查，591 msgs/147 editor 文件），完整 trace B-档不可行；**分解出 postprocess_lef.py 这个离线可验的 physical_layout 子任务**作为 B-档 L1-boundary 合成目标。johnl 首个 mt7ua trace。

## 心跳口径
- r118 = 深读轮（claim + 深读 + B-档合成计划），未交付 case。DEBT:1（下轮 r119 必须先合成 LefPostprocessFix-001）。
- 非「连续两轮只深读」（r117 已交付 PinNetWiringAether-001）。
- shard C 累计 case 仍 115（r118 未新增）；trace 覆盖率 115/1369=8.4%。
