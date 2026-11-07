# htwv2 深读笔记 — cxmt10G4plus DRAM Calibre LVS 规则文件分模块拆解

- **trace**: `1791456748770_htwv2` (yzwang @ hfeg0plg55 / 10.129.2.10, mc=76, 3 user turns, keywords netlist:223/calibre:128/pdk:53/.spi:11)
- **domain**: schematic_netlist (Calibre LVS SVRF 规则文件结构审计)
- **shard**: D
- **深读日期**: 2026-11-07
- **状态**: 已合成 case EDA-Eval-DesignFlow-LvsRuleAudit-001（schematic_netlist, B 档 synthesized, L1, 16 条件 a-p, k_rationale=k_check=16 ✓）

## 真实用户意图（逐字）

U#0: "加载一下： /home/cwei/Spice_Agent 中的skill" —（无关探索轮，cwei 路径误入；非本 session 主题）
U#1（核心需求轮，A 档合规候选）逐字：「我在当前路径放置了一个 `calibreLVS.rule` 的文件，请将该文件分模块拆解，并告诉我每个模块写的是什么。」+ U#1 后续「我在/home/pdk/yzwang/06_AI_workspace/test3放置了一个calibreLVS.rule的文件，请将该文件分模块拆解，并告诉我每个模块写的是什么。」+ U#2「分析4056行到4062行的意思。」
- A 档选轮判定：U#1 = 纯需求（分模块拆解 + 说明），未给根因/修复 → A 档合规 ✓。

## 真实文件（.75 ssh 取证）

`/home/pdk/yzwang/06_AI_workspace/test3/calibreLVS.rule`：228271 bytes / 5253 行，`#! tvf` + `tvf::VERBATIM { ... }` 包裹的 Calibre LVS SVRF + TVF 规则文件（cxmt10G4plus DRAM, Author Qianxue Shi）。
真实结构（节标题注释）：
- `// INPUT & OUTPUT FILE //`（LAYOUT PATH/PRIMARY/SYSTEM GDSII, SOURCE PATH/PRIMARY/SYSTEM SPICE, LVS REPORT, MASK RESULTS DATABASE, #DEFINE LVS_CHECK/SOFT_CHECK/TOP_METAL_IS_M8, LVS PUSH DEVICES, MASK SVDB DIRECTORY, ERC RESULTS/SUMMARY）
- `// LVS OPTIPON SETTING //`（LVS REPORT OPTION A B C D G N S V, LVS EXACT SUBTYPES, LVS EXECUTE ERC, LAYOUT DEPTH ALL, VIRTUAL CONNECT REPORT, LVS POWER NAME POWER_NAME, LVS GROUND NAME GROUND_NAME, LVS IGNORE PORTS, LVS CHECK PORT NAMES, LVS RECOGNIZE GATES）
- `// Include File //`（INCLUDE "calibre.layer" — DYT3E DRAM 层文件，~3000 行 LAYER MAP）
- calibreLVS.extract 块（`//////// Device List ////////` MOSFET ntn/ptn/ntn_lv/.../ptk, Resistor rndiff_3t_ckt/rnpo_2t_ckt/rm0_2t_ckt, Diode d_npw_ckt/d_pwdnw_ckt, CAP nicap_2t；`//////// LVS Options ////////` SOURCE/LAYOUT CASE；`//////// RC BLOCKING SETTING ////////` LAYOUT CELL LIST pcells "dcscr*"；`//////// Pins ////////` TEXT LAYER M0C_pin..M8_pin, PORT LAYER TEXT；`//////// Power & Ground ////////` VARIABLE POWER_NAME "vdd1!" "vcc!" "vwlp!" "vblh!" ... / VARIABLE GROUND_NAME "vss!" "vssbtc!" "vkb!"；`//////// Connectivity ////////` ATTACH M*_pin M*net, CONNECT M1 M2 BY VIA1；`//////// LVS Filter ////////` LVS FILTER R rnc_ckt OPEN, LVS REDUCE SERIES/PARALLEL）
- 顶层 SVRF 命令 3582 条（grep 统计），#DEFINE 3 个。

## A-faithful 判定

真实文件 5253 行含 foundry 工艺层名（DYT3E DRAM, cxmt10G4plus）不可公开进 assets；真实 produce = 模块拆解说明文（agent 输出 markdown 解释）+ L2 live calibre 跑比对验证 → A-faithful 不可移植。→ **B 档 synthesized**：取便携 facet = LVS 规则模块结构审计器。

## 合成 plan（已落地）

**gen_lvs_rule_audit.py --rule <deck> --outdir <dir>**：
- 节标题检测：`// NAME //`（前后被纯 `/` 分隔线夹住的单行横幅）+ `//////// NAME ////////`；排除版权/作者框（含 COPYRIGHT/AUTHOR/CHANGXIN/DEMO/Qianxue 等词或 name>40 字符）；首节标题前的内容为 `header` 模块。
- 每模块：name/line_start/line_end(1-based)/type(12 值枚举)/n_commands/command_breakdown(按 SVRF 动词)/key_directives(LAYOUT PATH/PRIMARY/SYSTEM/SOURCE PATH/PRIMARY/SYSTEM/LVS REPORT/LVS POWER NAME/LVS GROUND NAME/MASK SVDB DIRECTORY/INCLUDE/VARIABLE POWER_NAME|GROUND_NAME|PWR|GND)/summary。
- 顶层键 8 个：deck_name(=LAYOUT PRIMARY 去引号)/n_modules/modules/n_sections/n_commands/total_lines(到 tvf close 行)/defines/command_breakdown。
- 输出 modules.json + report.md（每模块 `## <name>` 节 + `## Summary` 表）。

**A=calibreLVS_A.rule**（trace-faithful cxmt10G4plus DRAM 代表 deck, 123 行, deck=layout_top, 12 模块/90 命令/defines LVS_CHECK+SOFT_CHECK+TOP_METAL_IS_M8, VARIABLE POWER_NAME vdd1!/vblh!）。
**hidden B=calibreLVS_B.rule**（SRAM deck, 77 行, deck=sram_top, 10 模块/59 命令/defines LVS_CHECK+NF_OFF_OP, VARIABLE PWR/GND VDD!/VSS!, LAYER 12）。
**hidden B2=calibreLVS_B2.rule**（analog opamp deck, 38 行, deck=amp_top, 7 模块/26 命令/defines LVS_CHECK, 无 Power/Ground/Filter 节）。
A/B/B2 deck 名/层名/电源名/节结构全不相交。

## check.py 16 条件 a-p

a(zip+py_compile) b(B-run exit0+2文件) c(8 顶层键) d(deck==sram_top) e(n_modules==10) f(n_commands==59) g(total_lines==77) h(defines==[LVS_CHECK,NF_OFF_OP]) i(每模块 8 字段) j(type∈12 枚举) k(io 模块 LAYOUT PATH+PRIMARY) l(power_ground 模块含 VARIABLE PWR+GND) m(layer_map LAYER==12) n(report 每模块 ## 节+Summary) o(反硬编码无 A 字面量+A-run deck==layout_top) p(跨输入 B2 n_modules==7+deck==amp_top+defines==[LVS_CHECK]+3x sha256)。

## 自验

- ref PASS 16/16（reference_submit.zip 跑 check.py 全 PASS）
- 5 negatives 全 FAIL（empty_shell→b / hardcode_a→d / print_expected→m / ref_core_deleted→f / naive_stub→d，first_fail 集合 {b,d,f,m} ≥2 distinct）
- §4.9 三假（empty_shell/print_expected/ref_core_deleted）全 FAIL ✓
- 断言闸门 k_rationale=k_check=16 ✓

## 教训

1. **Calibre LVS SVRF 节标题检测的坑**：`// NAME //` 形式的版权框行（如 `//  Copyright(C) ChangXin ... //`）也会匹配 `^//\s+(\S.*?)\s*//\s*$`，必须用「前后被纯 `/` 分隔线夹住」+「name<=40 字符」+「排除 COPYRIGHT/AUTHOR/CHANGXIN/DEMO 等词」三重过滤才不误判。
2. **classify 的子串匹配坑**：`'IO' in 'LVS OPTION SETTING'` → True（OPTION 里的 I-O 相邻），把 options 误判成 input_output。必须用 `\bIO\b` 词边界正则。
3. **check.py 路径**：check.py 在 `reference/<CID>/`，assets 在 `../../assets/<CID>/`（上两级，非一级）。
4. **A/B/B2 跨输入守卫**：用 deck_name + n_modules + defines 三轴全异 + 反硬编码字面量集，naive_stub/hardcode_a 全在 d/p 失败。
