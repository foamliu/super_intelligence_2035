#!/usr/bin/env python3
"""Generator for EDA-Eval-DesignFlow-MBistTopAnalyze-001.

Trace-faithful (A) MBIST top hierarchical SPICE netlist from real trace
1793017339067_jhdvn (user t0002805 @ hfeg0pgn145, mc=492, characterization).
User asked agent to analyze the mBistPat / mBistTop memory-BIST circuit
netlist; agent discovered the module hierarchy (mBistCmdGen / mBistAddrGen /
mBistPat / Bistwritedata / Spare_mBist), address counters, count-clock
outputs, reset behavior (only BACntRst, no RA/CA reset), and that the
read-back compare logic lives in the upper layer (ChanMid), not in mBistTop.

This script emits:
  * A netlist (trace-faithful names) + task_spec.json  -> assets/<id>/doc, assets/<id>/
  * B netlist (cross-input, same archetype, different names/counts) + hidden_manifest.json
  * ground-truth JSONs (_gt_A.json, _gt_B.json) for the reference + check
  * reference solution, check.py, 4 negatives + selftest  -> reference/<id>/

Both A and B share the SAME structural conventions (suffix-based:
*Begin/*End = address-range ports, *CntCK = count clocks, *CntRst = resets,
internal Dec+Lat = pattern generator) so the SUT can parse generically;
names/counts differ to give the check cross-input teeth.
"""
import json, os, shutil, subprocess, sys, textwrap

CID = "EDA-Eval-DesignFlow-MBistTopAnalyze-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)

# ----------------------------------------------------------------------------
# A netlist (trace-faithful) — names/signals verbatim from the real trace
# ----------------------------------------------------------------------------
A_NETLIST = """* mBistTop thick-oxide / digital MBIST hierarchical SPICE netlist
* top integration of memory-BIST pattern generator (trace-faithful, A)
* source: /proj/ddgoa/V0 libs ddgoa_cmos_digital / mBistTop schematic
.SUBCKT mBistTop mBistCk mBistCLK Reset ResetN mBistAct1a mBistAct1b mBistCas1aRd mBistCas1aWr mBistCas1b mBistPreAlla mBistPreAllb mBistRd1a mBistRd1b mBistWrt1a mBistWrt1b mBistCS mBistWIP mBistDoneFlag mBistRABegin mBistRAEnd mBistCABegin mBistCAEnd mBistBABegin mBistBAEnd PartialArrayEn cm0_ts_BistData BACntRst CACntCK RACntCK BACntCK RASecCntCK RAMsbCntCK RARefCntCK
XI_mBistCmdGen_189 mBistCk mBistCLK mBistCAEv mBistCAOd mBistCas1aRd mBistCas1aWr mBistCmdEn mBistCmdGen
XI_mBistAddrGen_201 mBistRABegin mBistRAEnd mBistCABegin mBistCAEnd mBistBABegin mBistBAEnd PartialArrayEn RACntCK CACntCK BACntCK RASecCntCK RAMsbCntCK RARefCntCK RACntOver CACntOver BACntOver Reset mBistAddrGen
XI_mBistPat_201 mBistCk mBistCLK Reset ResetN StateBegin mBistAct1a mBistAct1b mBistCas1aRd mBistCas1aWr mBistCas1b mBistPreAlla mBistPreAllb mBistRd1a mBistRd1b mBistWrt1a mBistWrt1b mBistCS mBistWIP mBistDoneFlag CACntCK RACntCK BACntCK RASecCntCK RAMsbCntCK RARefCntCK BACntRst mBistPat
XI_bistwritedata_199 cm0_ts_BistData mBistRABegin mBistRAEnd mBistCABegin mBistCAEnd mBistBABegin mBistBAEnd mBistWrt1a mBistAct1a BistClk RN BistData Bistwritedata
XI1 Spare_mBist
.ENDS mBistTop

.SUBCKT mBistCmdGen mBistCk mBistCLK mBistCAEv mBistCAOd mBistCas1aRd mBistCas1aWr mBistCmdEn
* command / CA-parity generation only; no address range, no reset, no pattern decode
XI_cg1 mBistCk mBistCAEv invLx4
XI_cg2 mBistCk mBistCAOd invLx4
.ENDS mBistCmdGen

.SUBCKT mBistAddrGen mBistRABegin mBistRAEnd mBistCABegin mBistCAEnd mBistBABegin mBistBAEnd PartialArrayEn RACntCK CACntCK BACntCK RASecCntCK RAMsbCntCK RARefCntCK RACntOver CACntOver BACntOver Reset
* address generator: instantiates the row / col / row-msb / bank counters
XI_racnt mBistRABegin mBistRAEnd RACntCK RACntOver Reset mBistRACnt
XI_cacnt mBistCABegin mBistCAEnd CACntCK CACntOver mBistCACnt
XI_ramsbcnt RAMsbCntCK RAMsbCntOver PartialArrayEn mBistRAMsbCnt
XI_bacnt mBistBABegin mBistBAEnd BACntCK BACntOver Reset mBistBACnt_WtRdRef
.ENDS mBistAddrGen

.SUBCKT mBistPat mBistCk mBistCLK Reset ResetN StateBegin mBistAct1a mBistAct1b mBistCas1aRd mBistCas1aWr mBistCas1b mBistPreAlla mBistPreAllb mBistRd1a mBistRd1b mBistWrt1a mBistWrt1b mBistCS mBistWIP mBistDoneFlag CACntCK RACntCK BACntCK RASecCntCK RAMsbCntCK RARefCntCK BACntRst
* command state machine: emits count clocks + BACntRst; NO RACntRst / CACntRst port
XI3 invLx16 Reset ResetN
XI281 invLx2 Reset mBistStart
XI365 invLx4 net340 BACntRst
XI115 ffrqLx1 mBistCk mBistCLK BaCntRstPreN net340
XI369 nor2Lx1 net0157 net0156 BaCntRstPreN
XI208 nand2Lx1 net0145 net0144 net0157
XI210 nand2Lx1 net0146 net0143 net0156
.ENDS mBistPat

.SUBCKT Bistwritedata cm0_ts_BistData mBistRABegin mBistRAEnd mBistCABegin mBistCAEnd mBistBABegin mBistBAEnd mBistWrt1a mBistAct1a BistClk RN BistData
* write-data pattern generator: cm0_ts_BistData -> Data<7:0>; NO read-back compare input port
XI_dinv cm0_ts_BistData netd0 BistDataInv
XI_dec38 cm0_ts_BistData netdec BistDecoder38
XI_mux netdec netd0 BistClk netsel mxi3x1
XI_xor netsel RN netxor xor2x2
XI_lat0 netxor mBistWrt1a grp0 DataLat
XI_lat1 netxor mBistWrt1a grp1 DataLat
.ENDS Bistwritedata

.SUBCKT Spare_mBist
* empty placeholder (symbol-only cell)
.ENDS Spare_mBist

* ---- leaf standard cells (empty bodies) ----
.SUBCKT invLx4 a y
.ENDS invLx4
.SUBCKT invLx16 a y
.ENDS invLx16
.SUBCKT invLx2 a y
.ENDS invLx2
.SUBCKT ffrqLx1 ck ckn d q
.ENDS ffrqLx1
.SUBCKT nor2Lx1 a b y
.ENDS nor2Lx1
.SUBCKT nand2Lx1 a b y
.ENDS nand2Lx1
.SUBCKT mBistRACnt RABegin RAEnd CntCK CntOver Reset
.ENDS mBistRACnt
.SUBCKT mBistCACnt CABegin CAEnd CntCK CntOver
.ENDS mBistCACnt
.SUBCKT mBistRAMsbCnt CntCK CntOver PartialArrayEn
.ENDS mBistRAMsbCnt
.SUBCKT mBistBACnt_WtRdRef BABegin BAEnd CntCK CntOver Reset
.ENDS mBistBACnt_WtRdRef
.SUBCKT BistDataInv a y
.ENDS BistDataInv
.SUBCKT BistDecoder38 a y
.ENDS BistDecoder38
.SUBCKT DataLat d ck q
.ENDS DataLat
.SUBCKT mxi3x1 a b c s y
.ENDS mxi3x1
.SUBCKT xor2x2 a b y
.ENDS xor2x2
"""

# ----------------------------------------------------------------------------
# B netlist (cross-input: same archetype, different names + different counts)
#   - 5 count clocks (A has 6; dropped RowRef)
#   - 3 address counters (A has 4; dropped bank counter)
#   - 4 pattern components (A has 5; dropped xor)
# ----------------------------------------------------------------------------
B_NETLIST = """* MbistTopInt digital MBIST hierarchical SPICE netlist (cross-input, B)
* top integration of memory-BIST pattern generator
.SUBCKT MbistTopInt MbistClk MbistClkN Reset ResetN MbistAct1a MbistAct1b MbistCas1aRd MbistCas1aWr MbistCas1b MbistPreAlla MbistPreAllb MbistRd1a MbistRd1b MbistWrt1a MbistWrt1b MbistCS MbistWIP MbistDoneFlag MbistRowBegin MbistRowEnd MbistColBegin MbistColEnd MbistBankBegin MbistBankEnd PartArrEn cfg_BistPatData BankCntRst ColCntCK RowCntCK BankCntCK RowSecCntCK RowMsbCntCK
XI_MbistCmdPlh_072 MbistClk MbistClkN MbistColEv MbistColOd MbistCas1aRd MbistCas1aWr MbistCmdPlhEn MbistCmdPlh
XI_MbistAddrMux_081 MbistRowBegin MbistRowEnd MbistColBegin MbistColEnd MbistBankBegin MbistBankEnd PartArrEn RowCntCK ColCntCK BankCntCK RowSecCntCK RowMsbCntCK RowCntOver ColCntOver RowSecOver Reset MbistAddrMux
XI_MbistPatSm_055 MbistClk MbistClkN Reset ResetN StateBegin MbistAct1a MbistAct1b MbistCas1aRd MbistCas1aWr MbistCas1b MbistPreAlla MbistPreAllb MbistRd1a MbistRd1b MbistWrt1a MbistWrt1b MbistCS MbistWIP MbistDoneFlag ColCntCK RowCntCK BankCntCK RowSecCntCK RowMsbCntCK BankCntRst MbistPatSm
XI_BistWrDataGen_044 cfg_BistPatData MbistRowBegin MbistRowEnd MbistColBegin MbistColEnd MbistBankBegin MbistBankEnd MbistWrt1a MbistAct1a PatClk RN BistPatData BistWrDataGen
XI1 SpareRowRed
.ENDS MbistTopInt

.SUBCKT MbistCmdPlh MbistClk MbistClkN MbistColEv MbistColOd MbistCas1aRd MbistCas1aWr MbistCmdPlhEn
XI_cp1 MbistClk MbistColEv invLx4
XI_cp2 MbistClk MbistColOd invLx4
.ENDS MbistCmdPlh

.SUBCKT MbistAddrMux MbistRowBegin MbistRowEnd MbistColBegin MbistColEnd MbistBankBegin MbistBankEnd PartArrEn RowCntCK ColCntCK BankCntCK RowSecCntCK RowMsbCntCK RowCntOver ColCntOver RowSecOver Reset
XI_rowcnt MbistRowBegin MbistRowEnd RowCntCK RowCntOver Reset MbistRowCnt
XI_colcnt MbistColBegin MbistColEnd ColCntCK ColCntOver MbistColCnt
XI_rowmsbcnt RowMsbCntCK RowMsbOver PartArrEn MbistRowMsbCnt
.ENDS MbistAddrMux

.SUBCKT MbistPatSm MbistClk MbistClkN Reset ResetN StateBegin MbistAct1a MbistAct1b MbistCas1aRd MbistCas1aWr MbistCas1b MbistPreAlla MbistPreAllb MbistRd1a MbistRd1b MbistWrt1a MbistWrt1b MbistCS MbistWIP MbistDoneFlag ColCntCK RowCntCK BankCntCK RowSecCntCK RowMsbCntCK BankCntRst
XI3a invLx16 Reset ResetN
XI281a invLx2 Reset MbistStart
XI365a invLx4 netBankRst BankCntRst
XI115a ffrqLx1 MbistClk MbistClkN BankRstPreN netBankRst
XI369a nor2Lx1 net0157 net0156 BankRstPreN
.ENDS MbistPatSm

.SUBCKT BistWrDataGen cfg_BistPatData MbistRowBegin MbistRowEnd MbistColBegin MbistColEnd MbistBankBegin MbistBankEnd MbistWrt1a MbistAct1a PatClk RN BistPatData
* write-data pattern generator; NO read-back compare input port
XI_dinv cfg_BistPatData netd0 DataInvStg
XI_dec cfg_BistPatData netdec Dec38Sel
XI_mux netdec netd0 PatClk netsel Mux3x1
XI_lat0 netsel MbistWrt1a grp0 DataLatch
XI_lat1 netsel MbistWrt1a grp1 DataLatch
.ENDS BistWrDataGen

.SUBCKT SpareRowRed
.ENDS SpareRowRed

* ---- leaf standard cells ----
.SUBCKT invLx4 a y
.ENDS invLx4
.SUBCKT invLx16 a y
.ENDS invLx16
.SUBCKT invLx2 a y
.ENDS invLx2
.SUBCKT ffrqLx1 ck ckn d q
.ENDS ffrqLx1
.SUBCKT nor2Lx1 a b y
.ENDS nor2Lx1
.SUBCKT nand2Lx1 a b y
.ENDS nand2Lx1
.SUBCKT MbistRowCnt RowBegin RowEnd CntCK CntOver Reset
.ENDS MbistRowCnt
.SUBCKT MbistColCnt ColBegin ColEnd CntCK CntOver
.ENDS MbistColCnt
.SUBCKT MbistRowMsbCnt CntCK CntOver PartArrEn
.ENDS MbistRowMsbCnt
.SUBCKT DataInvStg a y
.ENDS DataInvStg
.SUBCKT Dec38Sel a y
.ENDS Dec38Sel
.SUBCKT DataLatch d ck q
.ENDS DataLatch
.SUBCKT Mux3x1 a b c s y
.ENDS Mux3x1
"""

A_GT = {
    "top_cell": "mBistTop",
    "submodule_count": 5,
    "submodules": [
        {"name": "mBistCmdGen", "instance": "XI_mBistCmdGen_189", "role": "command_generator"},
        {"name": "mBistAddrGen", "instance": "XI_mBistAddrGen_201", "role": "address_generator"},
        {"name": "mBistPat", "instance": "XI_mBistPat_201", "role": "command_state_machine"},
        {"name": "Bistwritedata", "instance": "XI_bistwritedata_199", "role": "write_data_generator"},
        {"name": "Spare_mBist", "instance": "XI1", "role": "placeholder"},
    ],
    "address_generator": "mBistAddrGen",
    "address_counters": ["mBistRACnt", "mBistCACnt", "mBistRAMsbCnt", "mBistBACnt_WtRdRef"],
    "pat_module": "mBistPat",
    "pat_count_clock_outputs": ["CACntCK", "RACntCK", "BACntCK", "RASecCntCK", "RAMsbCntCK", "RARefCntCK"],
    "pat_reset_outputs": ["BACntRst"],
    "pat_has_racnt_rst": False,
    "pat_has_cacnt_rst": False,
    "pat_has_bacnt_rst": True,
    "writedata_module": "Bistwritedata",
    "writedata_has_read_compare_input": False,
    "writedata_pattern_components": ["BistDataInv", "BistDecoder38", "mxi3x1", "xor2x2", "DataLat"],
    "compare_in_top": False,
    "mbist_flow": ["write", "read", "compare"],
}

B_GT = {
    "top_cell": "MbistTopInt",
    "submodule_count": 5,
    "submodules": [
        {"name": "MbistCmdPlh", "instance": "XI_MbistCmdPlh_072", "role": "command_generator"},
        {"name": "MbistAddrMux", "instance": "XI_MbistAddrMux_081", "role": "address_generator"},
        {"name": "MbistPatSm", "instance": "XI_MbistPatSm_055", "role": "command_state_machine"},
        {"name": "BistWrDataGen", "instance": "XI_BistWrDataGen_044", "role": "write_data_generator"},
        {"name": "SpareRowRed", "instance": "XI1", "role": "placeholder"},
    ],
    "address_generator": "MbistAddrMux",
    "address_counters": ["MbistRowCnt", "MbistColCnt", "MbistRowMsbCnt"],
    "pat_module": "MbistPatSm",
    "pat_count_clock_outputs": ["ColCntCK", "RowCntCK", "BankCntCK", "RowSecCntCK", "RowMsbCntCK"],
    "pat_reset_outputs": ["BankCntRst"],
    "pat_has_racnt_rst": False,
    "pat_has_cacnt_rst": False,
    "pat_has_bacnt_rst": True,
    "writedata_module": "BistWrDataGen",
    "writedata_has_read_compare_input": False,
    "writedata_pattern_components": ["DataInvStg", "Dec38Sel", "Mux3x1", "DataLatch"],
    "compare_in_top": False,
    "mbist_flow": ["write", "read", "compare"],
}

# A-leak tokens: A-specific names that must NOT appear in B report
A_LEAK_TOKENS = [
    "mBistTop", "mBistCmdGen", "mBistAddrGen", "mBistPat", "Bistwritedata", "Spare_mBist",
    "mBistRACnt", "mBistCACnt", "mBistRAMsbCnt", "mBistBACnt_WtRdRef",
    "CACntCK", "RACntCK", "BACntCK", "RASecCntCK", "RAMsbCntCK", "RARefCntCK", "BACntRst",
    "BistDataInv", "BistDecoder38", "DataLat", "mxi3x1", "xor2x2",
    "cm0_ts_BistData", "mBistRABegin", "mBistRAEnd", "mBistCABegin", "mBistCAEnd",
]


def write_assets():
    os.makedirs(os.path.join(ASSET, "doc"), exist_ok=True)
    os.makedirs(os.path.join(ASSET, "hidden", "doc"), exist_ok=True)
    with open(os.path.join(ASSET, "doc", "mbist_top.netlist"), "w") as f:
        f.write(A_NETLIST)
    with open(os.path.join(ASSET, "hidden", "doc", "mbist_top.netlist"), "w") as f:
        f.write(B_NETLIST)
    task_spec = {
        "task_id": CID,
        "domain": "characterization",
        "layer": "L1",
        "mode": "design_flow",
        "entry_point": "outputs/submit.zip",
        "user_prompt_verbatim": "你可以帮我分析电路吗\nvirtuoso 但是我截图不了给你啊\n这个电路图在/proj/ddgoa/V0/libs/ddgoa_cmos_digital/mBistPat下\n网表我抽了 在这个文件夹下/proj/ddgoa/V0/workdir/t0002805/simulation/ddgoa_cmos_digital_mBistPat_schematic_20260901_ALPS\n你从上往下帮我详细的说一下",
        "user_intent_summary": "用户 t0002805 把抽取好的 mBistPat / mBistTop memory-BIST 网表交给 agent，要求从上往下详细分析电路——讲清顶层实例化了哪些子模块、各子模块的职责（命令状态机/地址产生/写图案数据）、mBistPat 输出哪些计数时钟与复位信号、RA/CA 有没有独立复位、写图案数据从哪里产生、读回比对电路在哪里。这是 characterization 流程里典型的「电路/网表分析报告」Q&A 任务。",
        "scene": "你是 IC 设计师的 EDA 助手。用户在 characterization 流程中拿到一个 memory-BIST 顶层的分层 SPICE 网表(doc/mbist_top.netlist)，想快速知道这个 MBIST 顶层实例化了哪些子模块、各自职责是什么、命令状态机输出哪些计数时钟/复位、地址计数器在哪里、写测试图案的数据产生器在哪、以及读回比对电路是否在顶层。你需要写一个 Python 脚本自动解析该分层网表，产出结构化 JSON 分析报告。",
        "deliverable": {
            "script": "mbist_top_analyze.py — 命令行签名为 mbist_top_analyze.py <workdir> <out_dir>;读取 <workdir>/doc/mbist_top.netlist;写出 <out_dir>/mbist_top_report.json",
            "zip": "outputs/submit.zip 内含 mbist_top_analyze.py(可能还有辅助文件)",
        },
        "input_files": ["doc/mbist_top.netlist"],
        "netlist_format": {
            "comment": "* 行为注释",
            "subckt_header": ".SUBCKT <name> <ports...>",
            "instance": "XI<instname> <nets...> <cellname>  (子电路实例)",
            "ends": ".ENDS <name>",
            "top_cell": "未被任何其它 subckt 实例化的 subckt(且内部 XI 实例数最多)",
            "leaf_cells": "标准单元(空 body)不参与角色分类",
        },
        "output_schema": {
            "top_cell": "string — 顶层 subckt 名(未被实例化、内部 XI 实例最多者)",
            "submodule_count": "int — 顶层直接实例化的子模块数",
            "submodules": "list[{name, instance, role}] — 顶层每个 XI 子模块;role 取自 {command_generator, address_generator, command_state_machine, write_data_generator, placeholder}",
            "address_generator": "string — 角色为 address_generator 的子模块名",
            "address_counters": "list[string] — address_generator 内部实例化的计数器子模块名(按出现顺序)",
            "pat_module": "string — 角色为 command_state_machine 的子模块名",
            "pat_count_clock_outputs": "list[string] — pat 模块端口中以 CntCK 结尾的端口(按出现顺序)",
            "pat_reset_outputs": "list[string] — pat 模块端口中以 CntRst 结尾的端口",
            "pat_has_racnt_rst": "bool — pat 是否有匹配 RA.*CntRst 的端口",
            "pat_has_cacnt_rst": "bool — pat 是否有匹配 CA.*CntRst 的端口",
            "pat_has_bacnt_rst": "bool — pat 是否有匹配 BA.*CntRst 的端口",
            "writedata_module": "string — 角色为 write_data_generator 的子模块名",
            "writedata_has_read_compare_input": "bool — writedata 端口列表中是否出现 read/rd-data/cmp-data/expect 类读回比对输入端口",
            "writedata_pattern_components": "list[string] — writedata 内部实例化中名字含 Dec/Lat/Inv/Mux/Xor 的单元类型(去重,按出现顺序)",
            "compare_in_top": "bool — 顶层子模块名里是否出现 cmp/compare 类比对单元",
            "mbist_flow": "list[string] — MBIST 流程步骤(有 write_data_generator 则含 write;pat 有 Rd/Read 端口则含 read;末尾含 compare)",
        },
        "role_classification_rules": [
            "1. 端口列表含 *CntRst 结尾的端口 -> command_state_machine (pat)",
            "2. 否则 内部实例单元名同时出现 /Dec/i 与 /Lat|Latch/i -> write_data_generator",
            "3. 否则 端口列表同时出现 *Begin 与 *End 结尾的端口 -> address_generator",
            "4. 否则 body 为空(无 XI 实例) -> placeholder",
            "5. 否则 -> command_generator",
        ],
        "parsing_hints_from_trace": [
            "顶层 = 未被任何 subckt 实例化、且内部 XI 实例数最多的 subckt",
            "顶层 XI 行最后一个 token 是子模块 cell 名;倒数之外的第一个 token 是实例名(XI...)",
            "pat 的计数时钟 = pat 自身 .SUBCKT 端口列表里以 CntCK 结尾的端口(注意是端口名,不是 net)",
            "pat 的复位 = pat 端口列表里以 CntRst 结尾的端口;A/B 都只有 BA 复位,没有 RA/CA 复位",
            "writedata 内部含 Dec/Lat/Inv/Mux/Xor 类单元 = 图案产生部件;其端口列表里没有读回数据输入",
            "顶层子模块里没有 cmp/compare 命名单元 => 比对电路不在顶层(在上层 ChanMid)",
        ],
        "rules": [
            "只解析 doc/mbist_top.netlist,不得访问网络或其它路径",
            "输出 JSON 必须可被 json.loads 解析",
            "脚本须在纯 Python3 标准库下运行(不得依赖外部包)",
            "角色分类与字段提取必须基于网表结构通用推导,不得硬编码某一组网表的具体名字",
        ],
    }
    with open(os.path.join(ASSET, "task_spec.json"), "w") as f:
        json.dump(task_spec, f, ensure_ascii=False, indent=2)
    manifest = {
        "hidden_inputs": ["hidden/doc/mbist_top.netlist"],
        "top_cell": B_GT["top_cell"],
        "a_top_cell": A_GT["top_cell"],
        "a_leak_tokens": A_LEAK_TOKENS,
        "note": "B is synthesized MbistTopInt (5 count clocks, 3 address counters, 4 pattern components); A is trace-faithful mBistTop (6/4/5). check.py scores B only.",
    }
    with open(os.path.join(ASSET, "hidden", "hidden_manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    write_assets()
    # ground truth
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "_gt_A.json"), "w") as f:
        json.dump(A_GT, f, ensure_ascii=False, indent=2)
    with open(os.path.join(REF, "_gt_B.json"), "w") as f:
        json.dump(B_GT, f, ensure_ascii=False, indent=2)
    print("assets + GT written for", CID)
    print("A:", os.path.join(ASSET, "doc", "mbist_top.netlist"))
    print("B:", os.path.join(ASSET, "hidden", "doc", "mbist_top.netlist"))
