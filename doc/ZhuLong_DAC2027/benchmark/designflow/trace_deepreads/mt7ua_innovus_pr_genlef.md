# trace_deepreads — mt7ua (johnl / hfeg0plg49) — Innovus P&R + GenLEF LEF-generation flow

- **session**: `1792488619552_mt7ua.messages.json` (johnl, host hfeg0plg49 等 11 台镜像)
- **match_count**: 679 · **size**: 2.04 MB · **msgs**: 591 (user 320 / assistant 271) · **tool_use**: 308 (editor 147 / run_approved_command 100 / read_files 26 / list_allowed_files 18 / RAG search 9)
- **keywords**: innovus:1767 · aether:831 · skipper:696 · .lef:398 · pyaether:359 · netlist:223 · synopsys:181 · .gds:169 · synthesis:31
- **domain (台账)**: pnr_signoff · **真实主线**: Cadence Innovus 数字 P&R + 单元 LEF 抽象生成（GenLEF/prBoundary 调试）
- **ledger 状态**: parked（见下「.75 沙盒可行性结论」）

## 用户意图（12 条 substantive user msg）

1. **idx 0（主任务）**：`/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/out/mapped.v` 在本文件夹建工程，用 **innovus** 完成版图，满足时序约束；附 spice 库（`.lib .../G5_CIP_Model_D5_v0d5_Rev03_t03.sp TT` + bjt_tt/res_tt/nicap_tt/diode_tt，`.TEMP 25`，pvcc=1.1/pvdd1=1.8/pvdbias=0.9323）+ `/proj/drcoa/V0/libs/drcoa_stdcell`（aether 内）。
2. idx 227/333/348/358/360：继续 / 完成layout / 加油（催进度）。
3. **idx 421**：只读对比 `nand3LVSx1` 的源 OA 边界、GDS、GenLEF 配置和日志，定位边界丢失环节；追踪 Y 方向来自哪个定义文件；不要手改原点为零/猜测 SIZE/批量重生成掩盖问题。
4. idx 430：一起重新生成 lef。
5. **idx 456**：①确认同路径/同库/同 cell/view ②用专用 prBoundary 查询接口（`emyPRBoundary.find(topBlock)`），接口报错≠对象不存在 ③对象存在查 asOut 为何没导出；不存在再找可靠边界源，不拿图形 bbox 代替 ④暂不改源库、不跑 P&R。
6. idx 525：好的。
7. **idx 579**：①独立 GDS 副本传入真实 prBoundary、正确处理单位；不改源库/原始 GDS ②重跑 GenLEF，确认 SIZE **3.88 BY 6.71**、原点/FOREIGN 与源坐标一致、不再出现整数极值 ③确认引脚/OBS/供电图形坐标一致，Y 仍为 OUTPUT ④通过后记录"边界传递与单元 LEF 转换已验证"，暂不跑 P&R。
8. **idx 590**：查 GenLEF 是否支持显式边界输入，再评估派生 LEF 或隔离 OA 副本路径，只完成 nand3LVSx1 转换与一致性验证，暂不跑 P&R。

## 两阶段主线

### Phase A（idx 0–360）：Innovus 数字 P&R 工程搭建
- **探明环境**：Innovus **23.35** 在 `module load innovus/23.35`（CDS_LIC_FILE=5980@hl06），但 `/apps/cdsmgr/cadence_tools/innovus/INNOVUS-23.35` 对 agent 不可执行（Permission denied）；可用的为 `/apps/cdsmgr/CRB/INNOVUS231`(23.1) 与 `INNOVUS2231`(22.31)。`LD_PRELOAD` 的 agent `libstdc++`/`libgcc` 是毒，须 unset 后用 wrapper。
- **设计输入**：`out/mapped.v`（module `addr_to_rowcol_v7`，纯组合逻辑）+ `out/mapped.sdc`（input→output max delay **0.5 ns**、input slew 20 ps、max transition 100 ps、output load 5 fF）。
- **时序库**：DC 用 `/proj/.../output/stdcells_ac_all_comb_SS_0p98_m40c_lvs.db`（LVS comb cells）。**无匹配 Innovus .lib/.db**；FF `.lib` `stdcells_ac_FF_1p3_m40c.lib` 用 **`Lx` 命名**（`invLx4`/`nand3Lx1`…），与网表的 `*LVS*` cell 不一致 → 只有 SS LVS-comb `.db` 含网表所需 cell。
- **物理视图阻塞**：stdcell（`stdcells_ac`，如 `and2LVSx1` 有 layout/schematic/verilog view）存为 **Empyrean Aether/OpenAccess layout**；`/proj/drcoa` **无预生成 cell LEF/FRAM**，G5_CIP techlib **无 tech LEF**（仅 `techfile.tf`）→ Innovus 无法 `init_design`。
- **18 个 unique gate cell**：aoi21/22、inv、nand2/3、nor2、oai21/211、or2（LVS 变体）。
- **关键验证（idx 184–202， Innovus 23.1）**：`create_library_set -name <n> -timing <.db>` **成功**——Innovus 可直接读 Synopsys `.db` 时序库（无需 .lib 转换）；`report_lib_cells` 内省偶发 segfault 但读库本身 OK。三电源 PDN（pvcc/pvdd1/pvdbias）+ MMMC（SS=setup/FF=hold）。
- **db→lib 转换失败**：`lc_shell write_lib` 与 DC `write_lib` 在该环境**只支持 .db**，无法导出文本 .lib（`-format lib`/`-format text` 均无效）。
- **GenLEF 路径**：`ski-genlef` 需完整 Aether/Tcl 环境；`cxmt_autoGenLefFlow.py` 是 **PyQt5 GUI**（非 headless）→ 无法可靠 headless 自动生成 cell LEF。
- **交付**：完整可运行的 Innovus 工程脚本 `innovus/run.sh` + `tcl/flow.tcl`（floorplan/place/CTS/route/timing/export）+ `stage2.sh` + `README.md` + 18-cell manifest + MMMC setup，**待 LEF 提供后即可执行**；并附精确 LEF 生成指引（团队 GenLEF flow）。

### Phase B（idx 421–590）：nand3LVSx1 LEF 生成 / prBoundary 调试
- 症状：GenLEF 产出的 LEF **SIZE 出现整数极值**、原点/FOREIGN 与源坐标不一致、Y 方向边界丢失。
- 根因：**prBoundary 未正确传入** GenLEF（OA 的 prBoundary 对象未被 asOut 导出 / GenLEF 未读 prBoundary 而用图形 bbox 代替，导致边界错误）。
- 目标规格：`SIZE 3.88 BY 6.71`、FOREIGN 与源坐标一致、Y 为 OUTPUT、引脚/OBS/供电图形坐标保持一致。
- 调试手段：pyAether `emyPRBoundary.find(topBlock)` 查 prBoundary 对象；独立 GDS 副本传入真实 prBoundary（正确单位），不改源库/原始 GDS；重跑 GenLEF 一致性验证。
- 状态：trace 末段仍在"查 GenLEF 是否支持显式边界输入 / 评估派生 LEF 或隔离 OA 副本"，**未最终闭环**到 P&R。

## .75 沙盒可行性结论（本轮实地探明，**关键**）

经 `eda_flow run_code host=innovus` 实测（.75 = hfhds201，Innovus **22.31-s119_1**，license `invs 22.1` checkout OK）：

1. **`report_library_sets` SEGFAULT**：`report_library_sets -library_set LS1 -library_details` 触发 `tsPrintLibrarySets` 段错误（Qt5 AAE crash）→ 该命令不可用于 grader。
2. **`create_library_set -name LS1 -timing <abs>.lib` 成功**（无 TCLCMD-995），但 **`get_libs`/`get_lib_cells MINLIB_SS/*` 全空**（"Cannot find 'libraries'"）——library set 是 MMMC 构造，lib cells **仅在 `init_design` 后**才可查询；无 design top 时 `dbGet top.lib.name` 也无对象。
3. **`read_lef` = invalid command name**（22.31 无此独立命令；LEF 经 init_design/tech LEF 流程载入）。
4. **根本阻塞 = trace 自身的阻塞**：Innovus headless 需 tech LEF + cell LEF + netlist 才能 `init_design` 查询任何库/宏，而 .75 上 `/proj/drcoa/V0/libs/` 为空（trace 的 stdcell `.db`/`.lib`/OA layout 均在 johnl 机、不在 .75），tech LEF 亦无 → **无法构造自包含 L2 grader**。
5. GenLEF/ski-genlef 为 PyQt5/Aether-GUI，**非 headless**，不可 grader-subprocess（与 aether -nographic X11 阻塞同类）。

→ **mt7ua 不适合作为 .75 L2 case**。若要做此 trace，唯一可行口径为 **L1-structural**（离线解析 Innovus flow.tcl / LEF 文本 / .db cell 列表），但 §5 要求新建 case 只做 L2/L3，故**本轮不合成 case，台账 parked**。

## 可复用要点（供后续 case 借鉴）
- Innovus 批处理：`innovus -files <script.tcl>`（**非** `-no_init`，该 flag 无效）；`-files` 正确。
- Innovus **可直接读 Synopsys `.db`** 作时序库（`create_library_set -timing <.db>`），无需 .lib 转换——这是 trace 最有价值的可验证技术结论。
- Innovus headless 须 `unset LD_PRELOAD`（agent 注入的 libstdc++/libgcc 会毒杀 Innovus runtime）。
- LEF 抽象生成的正确口径：从 OA **prBoundary**（非图形 bbox）取单元边界 → GenLEF → 校验 SIZE/FOREIGN/原点/引脚方向/OBS/供电图形。
- **.75 上 Innovus 22.31 不适合做 grader**（无 PDK、report 库命令段错误）——后续选 trace 应避开纯 Innovus-PnR 域，优先 skipper/finesim/hspice/wv/calibre（已验证稳定）。
