# 深读笔记：qky0j — R_PreDec_TB HSPICE 网表模块功能分析

## trace 来源
- user: keviny / host: hfeg0plg57 (10.129.35.77) / session: 1792834214357_qky0j / mc=324
- session_file: `/home/keviny/.cline/data/sessions/1792834214357_qky0j/1792834214357_qky0j.messages.json`（1.95MB, 122 msgs/62 user/60 asst, agent=lead）
- 工具命中：schematic:1447 / netlist:288 / hspice:2 —— 纯 schematic_netlist，无 virtuoso/calibre/layout 污染 → shard-D
- 跨 shard 去重：grep 4 shard jsonl + 主 jsonl，qky0j 未被任何 shard 用过

## 用户意图演进（提出需求轮，非根因/修复轮）
- U[0] 原话「给我分析一下这个网表，分析一下模块功能」+ attached netlist（780KB HSPICE 网表 *R_PreDec_TB）← A 档任务说明候选
- U[1]「我想梳理一下 R_RowPreDec_lv 模块的功能」
- U[2]「给我梳理一下 R_RfIPRHRadd 模块的功能」
- U[3]「我想梳理一下 Predec 模块，你觉得我怎么梳理比较好」
- U[4]「给我讲一下 fnTRFC 输入，fnTRFCD 输出的电路」
- U[5]「电路分析时，给出我信号线功能，模块功能即可」← 收紧交付要求
- U[6–9] 信号级提问：CompRa15ND / SecDis / cm0_ro_CmpGroupU<2:0> / async

## 助手工具链
- read_files ×48（分段读 780KB 网表，每 chunk ~数 KB）+ run_commands ×1 + search_codebase ×2
- 无脚本产物；交付全是散文式模块功能报告（markdown）
- A[2] 产出「网表分析报告：R_PreDec_TB」：基本信息表（HSPICE/AETHER-SE/2026-09-10/rachely/dscqa_work/R_PreDec_TB/schematic/~180-220nm）+ 层级树（R_PreDec_TB → R_RasBnkLogic(~100+ 端口) → R_RasBase_lv/R_RasRRT_lv/R_RasToSaCtrol_lv/R_RowPreDec_lv/R_SaCntrlBnk_lv/R_SaDly4tRasLock_lv/R_PreBnkCtrl_lv/R_LongtRASCnt_PRAC/R_WLdlyMdl_lv/R_PRAC_Row_Ctrl_lv/R_SCmosBnkLoc/R_TSCodeSampler/R_2StepOC/T_IsmRasNew/T_PPRbanklogic ...）
- 多轮「Let me find R_RowPreDec_lv definition」反复（网表大、定位难）

## 真实网表结构（从 attached netlist 解析）
- 14502 行 / 780KB / 552 个 .SUBCKT（大小写混合 .subckt 7 + .SUBCKT 545）
- header: `*R_PreDec_TB` + `* Type:hspice` `* Tool:AETHER-SE` `* Date:Thu Sep 10 13:04:57 2026` `* User:rachely` `* Top Design:dscqa_work/R_PreDec_TB/schematic`
- 顶层 testbench 区夹在 `**TopDesStart`(L14490) / `**TopDesEnd`(L14497) 之间：3 个 XI_switch_*→switch_close + 1 条巨型 XI72（480 token，跨 3 行 `+` 续行）→ R_RasBnkLogic
- 552 子电路分类：design_R(R_*_lv/Bnk/Ras/PreDec) 68 + design_T(T_*) 9 + RAS(RAS_CustDly_1750/2000/1000ps) 3 + switch(switch_close/open) 2 + stdcell(inv/nand/nor/invLx1/...) 379 + other(R_trimbuf_*/Sp*/Toc/...) 91
- R_RasBnkLogic（DUT）：91 端口，196 个 X 实例，top 实例化 cell = nand2Lx1×24 / invLx6×23 / invLx1×22 / switch_close×21 / nor2Lx1×12 / mx2LVx1×7 / invLVx4×6 / nand2GSx2×5
- 按 X 实例数最大子电路：R_RowPreDec_lv（249 实例，254 行）；其次 R_RHR234RateCtrlRas(235) / R_RasBnkLogic(196) / R_SpareLogicRasBnkLogic(180) / R_RHRCalCtrl_PRAC(167)
- 关键陷阱：XI72 顶层实例跨 3 行 `+` 续行，子电路名 R_RasBnkLogic 在最后一行末尾；不处理续行会取错 dut_cell

## 合成（B 档，L1 离线 Python）
- 把「读网表并结构化模块功能分析」固化为 `analyze_netlist.py`（CLI: `<netlist.sp> <report.json>`），输出 JSON：header(tb_name/tool/date/user/top_design) + summary(total_subckts/total_x_instances) + top_level(dut_instance/dut_cell/dut_token_count) + dut(name/port_count/instance_count/top_cell/top_cell_count) + largest_subckt(name/instance_count) + subckts(全名清单)
- DUT 识别规则：`**TopDesStart`..`**TopDesEnd` 区内 X 实例中连接 token 数最多者
- 资产 A = 真实网表经可达性裁剪（保留 header + 从顶层 DUT 可达的全部 552 子电路 + 顶层实例化区 + **TopDesEnd），10638 行 / 694KB（与原网表结构一致，仅去掉 Below-origin-Cell 冗余段）
- 隐藏 B = 合成 DCC_CalTB（11 子电路，DUT=DCC_MainCtrl 10 端口 36 实例 top=nand2Lx1×8，largest=DCC_MainCtrl:36），结构全异于 A 杀 A-hardcode
- 跨输入守卫 B2 = 合成 Tiny_TB（3 子电路，DUT=TinyTop 6 端口 3 实例 top=invLx1×2），极小且 top_cell=invLx1（A/B 都是 nand2Lx1）杀 B-hardcode/print_expected/nand2Lx1 硬编码
- check.py 内嵌 B/B2 + 独立 GT 常量（不 import ref），subprocess 重跑候选 on B/B2

## 难度定位
- L1（离线 Python 解析 HSPICE 网表，无 EDA 工具），domain=schematic_netlist，track=B
- 难点：续行处理（`+`）、顶层 DUT 识别（按 token 数最大）、端口数（排除 param=value）、最大子电路（按实例数）、552 子电路规模
