# 深读笔记 — 1790061417120_p2n1r (miccao @ hfeg0plg37 / 10.129.32.47)

- **trace**: 144 msgs / 970KB / model deepseek-v4-flash / cwd /home/miccao / status failed (title "demo") / 2026-09-22
- **match_count**: 187 (calibre:850 / netlist:169 / schematic:61 / cellview:6 / pyAether:3 / hspice:3 / virtuoso:1 / spectre:1)
- **tool freq**: read_files×28, editor×20, run_approved_command×14, list_allowed_files×11, search_codebase×3, skills×1

## USER 原话（A-档 seed，提出目标，未给根因/修复）
USER#0 (idx=0):
> [autocell-tcl-flow-generator] /home/miccao/autocell/ddcpc/cell_constraints_template.txt这是我的配置文件，运行路径是/home/miccao/autocell/demo/show，网表路径是/home/miccao/autocell/ddcpc/netlist/train_proplus_decqa_20260903/netlist_dir_20260807/xord2x2.cdl，生成的gds请放到/home/miccao/autocell/demo/show下，运行autocell请打印log.autocell用 /apps/proplus/autocell.1.2026.8。如果能调用到calibre的话，请修DRC

单轮任务（全 session 仅此一条 user 指令轮，其余为 tool_result）。

## agent 行为
- read_files×28：读 cell_constraints_template.txt + xord2x2_flat.cdl + 8 个 TCL(run/globals/layers/layer_functions/rules/viadefs/place/route) + log.autocell(820-1000 行分段读) + calibre_drc.log + calibre_drc_flat.log + autocell_stdout.log + xord2x2_placement.json
- editor×20：写辅助脚本（find_pdf/extract_mp_pdf/check_pdf_libs/find_mp_pdfs/calbr_mp_study 等，多数因 filePath not regular file 失败后改路径）+ 改 run.tcl 注释
- run_approved_command×14 (profile=python-runner)：跑 autocell 1.26.8 生成 8-file TCL 流 + xord2x2.gds + xord2x2_placement.json + log.autocell；尝试 calibre DRC（flat + hierarchical 两种 license 均不可用 → DRC 跳过）；run.tcl 把外部 DRC 引擎切到 nano_verify (nanov.drc)
- list_allowed_files×11：探路 /apps/mentor/calibre, /home/miccao, /home/miccao/autocell/demo/show

## gold（人工复核 msg#143 任务完成摘要）
AutoCell 标准单元生成流跑通：
- **工艺/库**：planar (G5 DDCPC)，cell `xord2x2` (XOR2, 2x drive)，kit `x_pin22`，layout_spec `x`，pmos `ptn` / nmos `ntn_m`
- **模式**：netlist_mode `per_cell`，placement_mode `auto`，hierarchy `-hierachy`
- **8-file TCL 流**（全部生成于 /home/miccao/autocell/demo/show/）：
  | 文件 | size | 角色 |
  |---|---|---|
  | run.tcl | 7017 | 主控：set 流程变量 + source 7 技术文件 + 建 schematic/cell + placer + router + generate_layout + write GDS |
  | globals.tcl | 382 | global-net 替换列表 (vdd/vss/vpw/vnw) |
  | layers.tcl | 78532 | technology 对象 + 物理层声明 |
  | layer_functions.tcl | 1707 | 语义层功能分配 (ndiff/pdiff) |
  | rules.tcl | 5716 | design rules (min_width) + 外部 DRC/LVS 引擎配置 |
  | viadefs.tcl | 9921 | via 定义 (cut_layer/enc) |
  | place.tcl | 23109 | placement 模板 + placer 配置 |
  | route.tcl | 14646 | routing grid map + via 实例 + pin 契约 |
- **产物**：xord2x2.gds + xord2x2_placement.json + log.autocell
- **calibre DRC**：flat + hierarchical 两 license 均不可用 → 跳过（用户原话"如果能调用到calibre的话"→ 可接受）；run.tcl 切外部引擎 nano_verify
- **配置关键字段**（cell_constraints_template.txt）：process=planar, autocell_bin=/home/miccao/autocell.1.2026.7/autocell/bin/autocell, drc_engine=calibre, design_grid=0.0005, gds_dbu=0.0001, tech_unit=0.0001, cell_height=7.38
- **网表**（xord2x2_flat.cdl）：.SUBCKT xord2x2 A AN B BN Y vbn! vbp! vcc! vss! (9 pins)，8 个 MOS（MMN1-4 ntn_m + MMP1-4 ptn）

## 为什么 B-档 synthesized（A-档 faithful 不可行）
gold 依赖 live autocell 1.26.8 二进制 + PDK tech.tcl (live /home/miccao/autocell.1.2026.7/g5_ddcpc/) + live calibre license → 不可整体 fixture 化。A-档 faithful 要复刻整条 live 工具链，离线沙箱跑不了。
→ B-档 synthesized L1-boundary：离线 bundle fixture（config + 展平 cdl + run.tcl + globals.tcl + tcl_manifest.json[8 文件清单]）→ 静态审计脚本 + flow_audit.json，stdlib-only，确定性，不硬编码单元/工艺/文件数/尺寸。

## 合成
- **资产 A**（忠实）：bundle/cell_constraints_template.txt（真实 planar/calibre/7.38 等）+ xord2x2_flat.cdl（真实 9 pins/8 MOS）+ run.tcl（真实 7K，source 7 技术文件）+ globals.tcl + tcl_manifest.json（真实 8 文件尺寸 78532 layers 最大）
- **隐藏 B**（杀硬编码）：nand2x2 / finfet / autocell 1.2026.9 / drc_engine nano_verify / cell_height 8.20 / design_grid 0.00025 / gds_dbu 0.00005 / 5 pins / 4 MOS / placement manual / 缺 viadefs.tcl → 7 文件 / layers.tcl 82100 不同尺寸
- **参考解**：audit_autocell_flow_ref.py（parse config `key: value` + parse cdl .SUBCKT/MM* + parse run.tcl `set X "Y"` + source refs + parse manifest → flow_audit.json）
- **check.py**：20 条独立断言（a–t）+ 3-seed 随机化防硬编码；ref PASS + 3 neg (naive_hardcode/print_summary_only/empty_stub) 全 FAIL ✓
