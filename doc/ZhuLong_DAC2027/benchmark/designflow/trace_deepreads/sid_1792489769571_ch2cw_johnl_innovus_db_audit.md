# Deepread: sid 1792489769571_ch2cw — Innovus 数字后端能力审计 (pg_layout)

- **trace**: johnl @ hfeg0pfn119 (10.129.x), mc=255, keywords innovus:645; schematic:233; netlist:145; calibre:66; hspice:36; synthesis:27
- **tools**: run_approved_command:32, editor:33, read_files:13, list_allowed_files:7, run_commands:2, search_codebase:1, get_agent_policy_status:1
- **size**: 158 msgs / 0.95 MB (cline v3 nested sessions/<sid>/<sid>.messages.json)
- **agent**: zhulong (lead), 2026-09-20

## USER 意图（逐字）

- **USER#0（A-档 seed，提出目标，未给根因/修复）**：「全定制环境下 Innovus 完整数字后端能力审计——从当前已有、实际使用的全定制流程出发，调查能否用 Innovus 完成指定电路的完整数字后端流程，并定位可复用的数据、工具和真实缺项。本轮只调查现状和可行性，不进行任何正式实现。审计时必须区分三类：必须具备的信息或能力、满足触发条件才需要的项目、不是硬性前提的文件格式或工具。」
  - 网表：`/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/out/mapped.v`
  - 库入口：`/proj/drcoa/V0/libs/drcoa_stdcell`（实际 `drcoa_stdcells`，带 s）、`/proj/drcoa/V0/ver/pex/johnl/T_BistCtrlNew`（RCC 提取工程）
  - 目标 SPICE：pvcc=1.1 / pvdd1=1.8 / pvdbias=0.9323 / T=25°C / TT
  - §4.1 给出"必须项表"（可链接设计/单元物理/工艺规则/时序模型/约束/供电/Innovus 可用/寄生/物理实现+DRC-LVS/功能一致）
- **USER#135**：「继续」（无信息）

## assistant 工具链（只读调查）

read_files + run_approved_command（沿调用链：lib.defs → emy2netlist cdlOut / asOut → StarRC lpe_RCC / starrc_mapping / ITF nxtgrd → Calibre runset cxmtG5_CIP → TECHLIB tech.db / gds.map → Innovus modulefile / INNOVUS231）+ editor（在 `innovus_audit/` 写审计脚本 inspect_e / find_inno / phys_lib / proj_lib / check_map / lib_phys / cell_phys / tech_inno / innovus_s / cell_cove）+ run_commands（env -i 启动 Innovus 验证版本 banner）。

## 关键发现（gold 事实）

1. **电路**：mapped.v = 纯组合，顶层 `addr_to_rowcol_v7`，端口 N[8:0]→row[3:0]/col[4:0]/valid，18 个 `*LVSx*` master，107 实例，**无触发器** → CTS/setup/hold 不适用。
2. **综合**：synth.tcl + rtl/addr_to_rowcol_region_v7.v + run_dc.sh + command.log（DC O-2018.06-SP5）。约束 set_max_delay 0.5ns / input_trans 20ps / max_trans 100ps / load 5fF。**1.59ns 是无关振荡周期，未作约束**。
3. **时序库**：`stdcells_ac_all_comb_SS_0p98_m40c_lvs.db`（SS/0.98V/-40°C，PrimeLib 2023.12，18/18 覆盖）= mapped.v 综合用库。目标 SPICE pvcc=1.1/25°C → **PVT mismatch**（voltage/temp/process 三项）。
4. **物理数据**：stdcells_ac 每单元有真实 OA `layout` view，**无现成 LEF/FEF**，无 abstract。TECHLIB = G5_CIP drcoa v0d5 Rev14，tech.db 是 OA/Aether 技术库（非 DC .db），无 .tf/tLEF。
5. **工具**：Innovus 23.1 已装（INNOVUS231 v23.32-s091_1，license invs 5980@ts51，startup_verified，含 NanoRoute/IQuantus/TQuantus 23.1.1/OA 22.61/STYLUS 23.10）；Quantus 23.11；StarRC；Calibre；Empyrean Argus；**genlef 可用**（/apps/cad/bin/genlef → cxmt_autoGenLefFlow.py，skipper ski-genlef）。沙盒 LD_PRELOAD 注入旧 libstdc++ 致启动受阻，env -i + Cadence cdnslibssl.so.1.0.2k 后启动成功——属沙盒限制非真实环境。
6. **RC 提取**：全定制 CalibreLPE + StarRC（lpe_RCC.rule / star_cmd_RCC / mode RCC / corner TYP_25），ITF/nxtgrd G5CIP_itf_PF，starrc_mapping（M0-M5+RDL/POLY/NDIFF，1.9p×9m）。
7. **DRC/LVS**：Calibre runset cxmtG5_CIP（G5_CIP_drc / G5_CIP_lvs / lpe_star）+ Empyrean Argus，scripts_exist + historically_run + currently_verified。
8. **用户 Innovus 工程**：data/mapped.v + data/mapped.sdc + data/lib/SS_0p98_m40c_lvs.db + data/lef/cell_list.txt（18 单元）+ tcl/flow.tcl（read_lib/read_lef/floorplan/power_grid VDD/VSS M3/M4/placeDesign/routeDesign/timing OCV_CPPR/export DEF verilog sdc），CTS 标不适用，**唯一缺口 = tech.lef + stdcells_ac_comb.lef 未生成**。
9. **供电**：pvcc→VDD core；pvdd1/pvdbias 本块不路由。

## 最终审计结论（assistant ASST#134/152/156）

- blocking_gaps = [LEF]（唯一）；final_verdict = feasible_pending_lef。
- CTS = non_must（纯组合）；timing_opt = satisfied（覆盖 full + SDC）但 PVT mismatch 须列；placement = conditional（OA layout + genlef 可生成 LEF）；Innovus = installed + license + startup_verified。

## 案件化（B-档 synthesized L1-boundary）

gold 依赖 live Innovus + live drcoa OA 库（/proj/drcoa/V0 内网）→ .75 沙盒不可达 → **A-档 disqualified（tooling）** → **B-档 synthesized L1-boundary**（纯离线 manifest → audit 分类器生成）。

- **合成**：`audit_classifier.py`（标准库，确定性）读 `flow_audit_manifest.json` → 产 `audit_report.json`：circuit 类型判定 / PVT 校核（mismatch 列每项）/ cell 覆盖 / 9 阶段分类（must/conditional/non_must × satisfied/conditional/missing/n_a + reusable_data/missing_items/verdict）/ innovus 可用性 / blocking_gaps / final_verdict。
- **资产 A 忠实**（johnl drcoa：addr_to_rowcol_v7 组合 / SS_0p98_m40c_lvs / pvcc 1.1 / OA layout 无 LEF / Innovus 231 装且可启 / CalibreLPE+StarRC / Calibre runset+Argus / genlef 可用 / flow.tcl 缺 LEF）。
- **hidden B**（fs_h204 时序电路：12 master 含 4 flop / LEF 已就绪 / CTS must / gaps 空 / feasible_with_conditions）。
- **B2**（组合+LEF 缺：CTS non_must + placement conditional + gaps=[LEF]，击穿 always-must-cts/always-satisfied）。
- **B3**（组合+LEF 有+PVT 匹配：placement satisfied + pvt match + timing_opt satisfied，击穿 always-mismatch/always-conditional）。
- **B4**（Innovus 未装：gaps 含 Innovus + infeasible_innovus_missing，击穿 always-feasible）。

## check.py 16 条断言 (a)-(p)

a zip+py_compile / b 跑 B exit0+JSON+9 顶层键 / c circuit 判定与 B 一致(type/has_flop/n_masters/n_instances/flop_masters) / d CTS: B 含 flop→must 且≠n_a / e PVT mismatch: B verdict=mismatch 含 temperature / f cell 覆盖 B 12/12 full / g placement: B 有 LEF→satisfied / h timing_opt: B full+SDC+PVT mismatch→satisfied_with_pvt_mismatch / i innovus: B installed+license+startup / j parasitic: B StarRC+ITF→satisfied / k blocking_gaps: B LEF 就绪→[] / l B2 组合+LEF 缺→CTS non_must + placement conditional + gaps=[LEF] / m B3 组合+LEF 有+PVT 匹配→placement satisfied + pvt match + timing_opt satisfied / n B4 Innovus 未装→gaps 含 Innovus + infeasible / o 确定性 3×md5 / p A↔B guard(A combinational+CTS non_must+gaps=[LEF]+feasible_pending_lef, A≠B n_masters/gaps, osc_period≠max_delay)。

自验：ref PASS 16/16 ✓；5 neg（fake_empty→a / fake_print_expected→l / core_deleted→e / naive_cts_always_must→l / naive_placement_always_satisfied→l）全 FAIL NEG_RC=0 ✓；§4.9(a)(b)(c) 全 FAIL ✓；test==disk roundtrip ✓；jsonl_C 95→96；pg_layout 13→14；断言 96/96 ✓（k=16=k_check≥8 GATE PASS）。

## 正交性

与 r83 PwrGlobalsGen（PG 全局网生成）/ r82 PGReproGuide（PG 复现指南）/ r77 RsCalcCkPtAudit（电阻 checkpoint 审计）正交——本案是 **read-only 数字后端能力审计分类**（每阶段 must/conditional/non_must + PVT/覆盖/缺口 + final_verdict），不生成 PG 实现代码、不做电阻分析，是可行性判定类。
