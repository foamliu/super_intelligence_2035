# Deepread — i8070 (cck instance-traversal Tcl debug Q&A)

**session**: 1792478844725_i8070
**user**: chengk
**host**: hfeg0plg74 (10.129.8.112)
**mc**: 31
**domain**: schematic_netlist (netlist)
**peek**: eda_flow open_session → ssh 10.129.8.112 python3 peek /home/chengk/.cline/data/sessions/1792478844725_i8070/1792478844725_i8070.messages.json (21 msgs, 2 substantive user turns)

## 用户原话（逐字，不脱敏）

**U#1** (len=6666): 粘贴完整 Tcl/cck 脚本（`ProcOneInst` + `createStdCellDict` + `ReadInstFile` + `ParseArgs` + `Opt` + `main` + runner），脚本功能：用 cck API 遍历 netlist 中的 instance，对 subcircuit 类型 instance 打印端口连接关系。末尾附"报错："+错误输出：
```
== Target inst_full path : xi_buf.xi1  type=1 ==
subHdl : _s_15
subName : inv
all ports in _e_15  ports=(a,y,inh_vbulkn,inh_vbulkp,inh_vccz,inh_vss)
ports path and net path:
allStdCell: inv {name inv input a output y}
*** 'TCL_ERROR' returned after ERROR evaluation ***
  !! failed for 'xi_buf.xi1': CCK ERROR : Input Argument with Wrong Handler Type
  !! errorCode: NONE
  !! errorInfo:
CCK ERROR : Input Argument with Wrong Handler Type
    while executing
"cckGetSubcktName $term"
    (procedure "ProcOneInst" line 44)
```

**U#2** (len=152): "Error: Voltage/Inductor/E-element/H-element loop occurs / The following elements form V-L-E-H loops: / cck报错，分析是什么原因"

## 用户真实意图

**U#1**: code-debug Q&A — 粘贴 Tcl 脚本 + 错误输出，隐含"分析为什么报错"（cckGetSubcktName $term 抛 Wrong Handler Type）。
**U#2**: netlist-topology debug Q&A — "cck报错，分析是什么原因"（V-L-E-H loop，netlist 拓扑问题）。

本 case 聚焦 **U#1 的 code-debug 意图**（Tcl/cck 脚本 bug 诊断），因：
- 源码在 message 内粘贴，立即可取（无需 ssh find）
- 套 #254 v2 code-grounded debug-diagnosis pattern（9imo1/7sgr2 同族）
- U#2 V-L-E-H loop 属 netlist-topology 知识诊断，非 code-grounded，超本 case 范围

## 脚本 bug 分析（A = 真实脚本）

### Bug A1: WRONG_HANDLER_TYPE (high severity)
- **位置**: ProcOneInst 内层循环 `set conInsName [cckGetSubcktName $term]` (line 44)
- **根因**: `$term` 来自 `cckSearchInst -adj $nodeHdl`（instance handle），但 `cckGetSubcktName` 期望 subckt handle（来自 `cckGetSubckt`）
- **对比**: 脚本上方正确写法 `set subHdl [cckGetSubckt $cur_inst]; set subName [cckGetSubcktName $subHdl]`（两步），内层循环漏了第一步
- **修复**: `cckGetSubcktName [cckGetSubckt $term]`
- **cited_identifier**: cckGetSubcktName, cckGetSubckt, cckSearchInst, term, cur_inst, subHdl

### Bug A2: DICT_GET_NO_GUARD (medium severity)
- **位置**: `set CellInfoDic [dict get $allStdCell $subName]`
- **根因**: 无 `dict exists $allStdCell $subName` 守卫，若 subName 不在 dict 中 → Tcl 抛 "key not found in dictionary"
- **当前不触发**: trace 中 subName=inv 恰在 dict（createStdCellDict 只建了 inv），但 latent bug
- **修复**: `if {[dict exists $allStdCell $subName]} { set CellInfoDic [dict get $allStdCell $subName] ... } else { continue }`
- **cited_identifier**: dict, allStdCell, subName, CellInfoDic, createStdCellDict

### Bug A3: PORT_FILTER_INCOMPLETE (low severity，本 case 不取，design choice 非 crash bug)
- `foreach p $ports` 仅处理 CellInput 端口（`if {[lsearch -exact $CellInput $p] >= 0}`），跳过 output/其他端口
- 脚本声称打印 "ports path and net path" 但仅 trace input fanout

## case 设计

套 #254 v2 code-grounded debug-diagnosis reframe（同 9imo1 LatchFFDiagnoseQA-001 / 7sgr2 WaveCmpMismatchDiagQA-001）：
- 候选写 `cck_traverse_diagnose.py`，读 Tcl 脚本 + 错误日志 + 问题 → 结构化诊断 JSON
- 3 bug types: WRONG_HANDLER_TYPE / DICT_GET_NO_GUARD / MISSING_INSTANCE_CHECK
- A: WRONG_HANDLER_TYPE + DICT_GET_NO_GUARD (真实脚本)
- B1: WRONG_HANDLER_TYPE + MISSING_INSTANCE_CHECK (合成，不同 proc 结构)
- B2: DICT_GET_NO_GUARD + MISSING_INSTANCE_CHECK (合成，不同 proc 结构)
- B3: clean (0 bug, 优雅降级)

## trace_source
- user: chengk
- host: hfeg0plg74
- session_file: 1792478844725_i8070.messages.json
- match_count: 31
- real_task_summary: cck Tcl instance-traversal 脚本报 "Wrong Handler Type" + V-L-E-H loop，用户要求分析原因
