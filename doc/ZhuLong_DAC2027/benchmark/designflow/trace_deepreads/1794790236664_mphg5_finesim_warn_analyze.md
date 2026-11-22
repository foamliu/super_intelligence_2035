# Deepread — 1794790236664_mphg5 (FineSim output.log WARNING 分析)

- session_file: `1794790236664_mphg5.messages.json`
- user / host: reedchen @ hfeg0pkn002
- match_count: 26 (hspice:22 + finesim)
- domain: spice_sim / characterization
- 决策: ACCEPT → 合成 case `EDA-Eval-DesignFlow-FinesimWarnAnalyzeProduce-001`

## 真实任务
reedchen 让 agent 看一块 FineSim 仿真的 output.log 报告里"值得注意的 warning"。仿真目录：
`/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ddgoa_cmos_top_ChannelLeft_sim/sim_smoke/`

agent 读 `./output/output.log`（FineSim Extended Log，V-2023.12-1）。日志 486 行，停在
`Starting DC Initialization ...`，**没有任何收尾汇总**（无 "Total WARNINGs"、无
"Number of WARNINGs not printed"、无 "FineSim Simulation Finished"）—— run 在 DC 初始化
阶段就被中断/终止了。

## 日志里出现的 WARNING! 类别（trace 实测）
1. `WARNING! '-i' is an obsolete option. Please use '-istop' for interactive mode.`（命令行选项过时，1 条）
2. `WARNING! duplicated model param 'wdvtp0' (/apps/imctf/models/.../incFile_V1_HKMG:277124)`（模型参数重复定义）
3. `WARNING! duplicated param 'pvss' (.../hspice0.94v.voltage:9)` 等：pvss/pvbn/pvbp/pvdbias/pvblh/pviso/pvwlp/pvap2（.param 重复定义）
4. `WARNING! subckt nor2gfx1_..._schematic_ddgoa_cdnflib and ..._0 (two definitions with the same name)`（subckt 重名，nor2gfx1/invpfx2/invpfx4/invgfx2/invpfx8/nor2pfx1）
5. `WARNING! Could not find subckt 'ChanLeft' for spf file '...ChanLeft.spf.TYP_98_RCC'. Using top-level subckt.`
6. `WARNING! ChanLeft.spf.TYP_98_RCC:58249050: Element 'XI_DQByteLo.XI_WCKTop.XI_DOutCtrl.XDDD0@21' is a finger of a an element that does not exist in the netlist and will be ignored.`（注意原文 "a an" 拼写）
7. `WARNING! SPF device pin '...:gate' in net '...' is not a port (ChanLeft.spf...)`
8. `WARNING! node "0" is part of a self-consistent voltage loop.`（terminal 1 of vvss）
9. `WARNING! node ':tdq1asyncin' has only 1 connection to an SPF resistor.`（:tdq1asyncin/:vblhsfrr/:vcslrefr...）

FineSim 限流：`WARNINGs will not be printed. Number of WARNINGs not printed = 45.`

## agent 的产出
- `analyze_warn.py`：按 WARNING 行前 90 字符归类计数（粗糙分类）。
- `check_sim.py`：看文件 mtime / 进程是否还在跑（判断 run 是否被中断）。

## reframe（L1 纯 Python，可移植化）
e0031982 在沙盒里没有 /proj PDK 读权限 → 不能真跑 FineSim → L1 reframe：把"看 warning"重构成
一个**参数化的 FineSim output.log WARNING 分类汇总工具** `finesim_warn_analyzer.py`，纯 Python
标准库，对任意 output.log 解析 9 类 WARNING!、计总数、解析版本号、抑制计数、去重 param 名、
判断 run 完整性（有无 "FineSim Simulation Finished"），产出 JSON 报告。

## 有牙设计（hidden B，与 A 结构性不同）
- A（公开样本）：不完整 run，停在 `Starting DC Initialization`，44 条 WARNING!，suppressed=45，
  run_complete=false，param 名 pvss/pvbn/pvbp/pvdbias/pvblh/pviso/pvwlp/pvap2，SPF subckt ChanLeft，
  element 前缀 XI_DQByteLo/XDDD0，node "0"/:tdq1asyncin。
- B（隐藏判分）：**完整 run**（有 "Total WARNINGs: 43" + "FineSim Simulation Finished"），43 条 WARNING!，
  suppressed=0，run_complete=true，param 名 pvdd/pvssq/pvbn2/pvbp2/pviso2/pvwln/pvap3，SPF subckt PhyTop，
  element 前缀 XI_DQBus/XQQ0，node "vssx"/:dqs0pad。类别计数全部不同（1/2/7/4/1/15/6/4/3 vs 1/1/8/6/1/10/3/9/5）。
- anti-hardcode：A 专属值（pvdbias/ChanLeft/XI_DQByteLo/wdvtp0/tdq1asyncin/pvblh/pvwlp/58249050/hspice0.94v）
  不得泄漏进 B 报告。

## check.py 12 条断言（k=12）
zip+py_compile+size ② B exit0+合法JSON ③ total==43 ④ by_class==oracle 9 类 ⑤ run_complete==True
⑥ suppressed==0 ⑦ distinct_duplicated_params==oracle 7 集 ⑧ finesim_version ⑨ anti-hardcode
⑩ 3-seed 确定性 ⑪ A 上也 exit0 且 run_complete==False ⑫ A total==44。

## 3 个 negative（均须 FAIL）
- neg_empty：空 stub，不写 JSON → 失败 ②
- neg_print_only：硬编码 A 的报告 → 失败 ③/④/⑤/⑥/⑦ + ⑨ anti-hardcode（A 值泄漏）
- neg_core_removed：只计 total 不分类（by_class 全 0）→ 失败 ④

## 自验
- ref PASS 12/12；3 negative 全 FAIL；3-seed 报告 sha256 一致。
