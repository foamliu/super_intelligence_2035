# Deep-read: a6f6r (jinsongl@hfeg0pkn005, mc=204) — NmosBulkVoltCheck-001

## Trace source
- session: `1792497319115_a6f6r.messages.json` (dir-based: `/home/jinsongl/.cline/data/sessions/1792497319115_a6f6r/1792497319115_a6f6r.messages.json`)
- user: jinsongl, host: hfeg0pkn005 (10.129.2.14), match_count: 204
- size: 218187 bytes, 3 user turns (after stripping skill/env wrappers)
- domain keywords: netlist:160; pyaether:20; hspice:18; transistor:8; dbget:8; spectre:6; rtl:4; drc:2

## User intent (verbatim, A-faithful candidate)
- U#0 (msg#0): "chkCellPinTieSpecialPower_v2.tcl 这个脚本是我用tcl写的，借用 CCK 的 API 对电路进行检查的脚本 说明逻辑" — Q&A: explain existing CCK TCL script.
- **U#1 (msg#12) [produce, A-faithful task statement]**: "仿照上述写法，为我写一个新的脚本 逻辑是：检查电路里面所有的 nmos，如果 bulk 端的电压最小值小于等于 -0.2v，就进行输出，输出 nmos 的长宽、类型和电压最大最小值"
  - 提需求 + 给出完整 spec (目标 NMOS、判定阈值 -0.2V、输出字段 L/W/type/Vmax/Vmin)，**未指根因** → A 档任务说明可用原文。
- U#2 (msg#33): 用户粘贴一段 ChkMosBulkVolt namespace proc 代码骨架，要求封装成可调用 module style（仿 2.1_ChkMosVgs/4.1_ChkMosBulk）—— 这是 refinement/封装要求（gives a code template，不是根因）。

## Agent tool chain (msg#1-40)
1. msg#1-11: 读 `/home/jinsongl/chkCellPinTieSpecialPower_v2.tcl` + RAG 搜 CCK API（cckSearchInst/cckGetInstTerminalNode/cckSearchNode/cckGetSubcktPortNames）→ 解释原脚本逻辑（检查 subcircuit 引脚是否接到指定 power rail，支持 switch_close/brknet 跨接、通配符电源名）。
2. msg#13-28: 接 U#1 需求，RAG 搜 NMOS 遍历/节点电压/器件 L/W API（pyAether 语料不覆盖 CCK TCL）→ 转而浏览 `/home/jinsongl/work/script/cck/cckScript/` 目录，读真实参考脚本 `4.1_ChkMosBulk.tcl`、`2.1_ChkMosVgs_v2p0.tcl`、`2.8_ChkMosVsb_v2p0.tcl`、`2.3_ChkMosVds_v2p0.tcl`，提取真实 CCK TCL API 用法：
   - 遍历所有 MOS: `cckSearchInst -type MOS -proc <回调>`
   - 判 NMOS/PMOS: `cckIsPmos $instHdl` (1=PMOS, 0=NMOS)
   - 取 bulk 节点: `cckGetInstTerminalNode $instHdl $::CCK_BULK`
   - 取节点电压 max/min: `xplGetNodeProp $B "vmax"`/`"vmin"`
   - 取器件 W/L/finger: `cckGetInstProp $instHdl "w"/"l"/"nf"`，`LE=$length*1e6/$shrinkFactor`
   - 取类型(model): `cckGetInstModel $instHdl`
   - 输出: `util::Report::RptDump -attr -status_str -type dev -rpthdl -err`
3. msg#28: 写 `/home/jinsongl/chkMosBulkNeg_v1p0.tcl` — 仿 chkCellPinTieSpecialPower_v2 框架（exec cck 头、package require、argvParser -proj、main 读网表/GenDeck/SelectRailTbl/开报告、cckSearchInst 回调 ChkInst、报告输出）。核心 ChkInst: cckIsPmos=1 跳过 → 取 bulk 节点 vmax/vmin → 空则跳过 → Vbmin<=bulkVoltThr(-0.2) → RptDump 输出 model+L+W+nf+Vbmax+Vbmin。
4. msg#33-40: 接 U#2 封装要求，读 `2.1_ChkMosVgs_v2p1.tcl` + pkgIndex.tcl 确认标准封装 style（namespace eval + ChkInst proc + 入口 proc with -o/-ver + package provide），shrink 因子取 `$::ERC::shrinkFactor`。重写为 `/home/jinsongl/chkMosBulkVolt.tcl`（tclPackage 之外的可调用 module）。

## 金标准 (agent 实际产物)
- `chkMosBulkNeg_v1p0.tcl` (独立脚本) + `chkMosBulkVolt.tcl` (可调用 module) — CCK TCL，依赖 CCK runtime + 私有电路网表/节点电压库，沙盒不可复刻。

## A-faithful 不可复刻判定
- 真实任务依赖 CCK TCL 运行时（`exec cck`、`cckSearchInst`、`xplGetNodeProp` 实时查询网表节点电压数据库）+ 用户私有电路工程（`-proj`）。沙盒无 CCK 运行时、无私有电路 → A-faithful 不可复刻 → **B-grade synthesized**。

## B-grade synthesized 抽象
保留核心逻辑（遍历 NMOS、bulk 节点 Vmin<=阈值 判定、输出 L/W/model/Vmax/Vmin），把 CCK 运行时查询抽成自包含文件解析任务：
- 输入: (1) SPICE 网表（M-card MOS 实例：name/d/g/s/bulk/model/L/W），(2) DC operating-point 节点电压报告（node vmin vmax）
- 候选 `nmos_bulk_check.py <netlist.sp> <voltage.rpt> <out.json> [--threshold V]`:
  解析 M-card → 按模型名首字母 'p' 判 PMOS 跳过 → 查 bulk 节点 vmin/vmax → Vmin<=阈值 (-0.2) 判违规 → 输出 JSON{threshold, summary{total_mos,total_nmos,flagged_count,by_model}, flagged[], all_nmos[]}
- 可见 A: netlist_A.sp (7 MOS: 5 NMOS + 2 PMOS) + voltage_A.rpt → flagged {Mn2(vmin=-0.35), Mn4(vmin=-0.50)}
- 隐藏 B: netlist_B.sp (9 MOS: 7 NMOS + 2 PMOS, LV+HV 混合, 边界 case) + voltage_B.rpt → flagged {Mn_lv1(-0.25), Mn_lv3(-0.80), Mn_hv1(-0.21)}; Mn_hv2(-0.19) clean 边界; Mn_lv5 缺电压 skip; PMOS Mp_lv1(vmin=-0.40) skip
- 反硬编码: A/B 模型名/实例名/拓扑/电压全不同; 跨阈值 --threshold -0.5 → B flagged {Mn_lv3} (与默认 3 不同); A-only 名不泄入 B
