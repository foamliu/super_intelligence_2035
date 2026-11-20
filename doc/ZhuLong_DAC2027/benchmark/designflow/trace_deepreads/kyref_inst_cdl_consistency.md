# 深读笔记 — 1792297746172_kyref_inst_cdl_consistency

- **trace**: `1792297746172_kyref.messages.json` (vincelu / hfeg0plg55 / mc=476 / 351 msgs / 3.05MB)
- **host**: 10.129.35.74 = hfeg0plg55（.75 本机，/home/vincelu/.cline/data/sessions/1792297746172_kyref/）
- **tools profile**: netlist:5768 schematic:4031 pyAether:97 cellview:56 hspice:22 calibre:6 → schematic_netlist / SiliconSmart 表征流程

## 用户意图（6 substantive turns）
- **U[1]**: `stdcells_ac add new cells {coveragecap}, pls create inst` + `drgqx_cmos_digital add new cells {R_SrefRateLookUpTable42t58, R_trimand2_SanOC}, pls create inst` + `drgqx_cmos_io add new cells {DL_DFFPD_sub1, IO_VrefDqGenV3_cvps, DL_DFFPD_sub2}, pls create inst` — 为三库 6 新增 cell 创建 SiliconSmart 表征 .inst。
- **U[2]**: 查找版图中 DL_DFFPD_sub1 cell 的信息。
- **U[3]**: 在 /proj/drgqx/V0/libs/ 根据库信息查找并创建上述 cell 的 inst。
- **U[4]** ⭐: **「分析所有已有的 inst 文件是否电路中行为一致，列出差异，先不要修改」** ← 本 case 任务来源（提出需求，未给根因/方案，合规）。
- **U[5]**: 总结遇到的问题及解决方案。
- **U[6]**: 贴 emy2netlist（Empyrean emy2netlist 2025.09.sp1.hf7）导出 drgqx_cmos_analog 的报错（VCell Error: invalid bareword "50m" in "50m/0.1"）。

## 助手工具链（226 tool_use）
大量 list_allowed_files 探索 + read_files 读 .inst/.cdl + editor 写 create_inst_files.py / create_inst_symlinks.py / analyze_inst.py + run_approved_command 跑脚本。真实文件位置：
- .inst: `/rundata/drgqx/V0_20261007/simdir/verilog/workdir/vincelu/tt_25_1017/sisregular/<lib>/control/<cell>.inst`
- .cdl: `/rundata/drgqx/V0_20261007/ver/pex/vincelu/<lib>/<cell>/<cell>.cdl`（PEX 提取）

## 金标准（真实 .inst vs CDL 顶层，经 read_files 工具结果核对）
| cell | .inst 端口/功能 | CDL 顶层 .SUBCKT / .GLOBAL | 一致? |
|---|---|---|---|
| DL_DFFPD_sub1 | Ck/CkN/D/Q/QN/R/RN/S/SN, add_flop, vdpg/vss | IN1/IN2/IN3/OUT1/OUT2, .GLOBAL vdll!/vssdll!, nand SR 锁存 | **不符**（端口/电源/行为） |
| DL_DFFPD_sub2 | 同 sub1（字节相同） | IN1/IN2/IN3/OUT1/OUT2/**RST**, .GLOBAL vdll!/vssdll! | **不符** |
| IO_VrefDqGenV3_cvps | VREFDQ_TDQ -inout / VREF_DM / VREF_DQ<3:0> / cm0_io_*, add_function MUX, vcc/vddq/vss | 同端口, VREFDQ_TDQ:B, .GLOBAL vss!, 5 NMOS TG | **一致** |
| R_SrefRateLookUpTable42t58 | Ck/CkN/D<41:0>/Q<57:0>/RN, add_flop, vbp/vcc/vbn/vss | In0/In1/Rate<6:0>/SelRate<7:0>/SelRateN<7:0>, .GLOBAL vbn!/vcc!/vss!（缺 vbp）, MUX+缓冲 | **不符**（端口/电源 vbp/行为） |
| R_trimand2_SanOC | A/B/Y, add_function Y A&B, vbp/vcc/vbn/vss | In/Out/OutN/cm<3:0>, .GLOBAL vbn!/vbp!/vcc!/vdbias!/vss!, trim 延时缓冲 | **不符**（端口；电源一致） |
| coveragecap | 无端口、无功能, vbp/vcc/vbn/vss | 无 .cdl（仅 symbol 视图） | **一致**（passive） |

真值：**2 一致（IO/coveragecap）/ 4 不符**。

## 关键陷阱
助手 U[331] 报告对 DL_DFFPD_sub1 判「✅ 一致」是**口述错误**：它把 .inst 端口描述成与 CDL 相同（IN1/IN2/IN3/OUT1/OUT2），但真实 .inst 是 DFF 端口（Ck/CkN/D/Q/QN/R/RN/S/SN），与 CDL 锁存端口完全不符。本 case 以真实文件（read_files 工具结果）为金标准，SUT 必须自己解析得出真值，不能照抄 trace 报告——这天然构成防硬编码。

## 产物用于 case
- assets A：6 真实 .inst + 5 .cdl（去 read_files 行号前缀）+ example_report_A.json + task_brief.md + prompt.txt
- hidden B：6 合成 cell（3 一致 + 3 分别注入端口/方向/电源单维不符）
- reference：inst_cdl_consistency_ref.py + check.py（内嵌独立解析器，15 条件 a–o）+ 5 negatives + reference_submit.zip
- case id: EDA-Eval-DesignFlow-InstCdlConsist-001（schematic_netlist / L1 / track B）
