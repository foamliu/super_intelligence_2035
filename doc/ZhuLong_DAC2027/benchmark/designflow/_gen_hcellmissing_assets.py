#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator for EDA-Eval-DesignFlow-HcellMissingFind-001 case assets + reference."""
import os, zipfile

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-HcellMissingFind-001"
A = os.path.join(BASE, "assets", CASE)
R = os.path.join(BASE, "reference", CASE)
for d in (A, os.path.join(A, "hidden"), R, os.path.join(R, "solution"), os.path.join(R, "negative")):
    os.makedirs(d, exist_ok=True)

# ============================================================
# A assets (visible to SUT)
# ============================================================
hcell_A = """\
IO_DqLdMdl                 IO_DqLdMdl
AG_VdivActTop              AG_VdivActTop
AG_VdivActTopSpare         AG_VdivActTopSpare
AG_PosClamp                AG_PosClamp
T_CMDq                     T_CMDq
BCenterR                   BCenterR
BCenterL                   BCenterL
AG_BCenterL_moscap         AG_BCenterL_moscap
AG_BCenterL_moscap_ntk     AG_BCenterL_moscap_ntk
AG_BCenterL_moscap_ntk_lv  AG_BCenterL_moscap_ntk_lv
AG_BCenterL_moscap_ptk     AG_BCenterL_moscap_ptk
AG_BCenterL_moscap_ptk_lv  AG_BCenterL_moscap_ptk_lv
IO_DqRcv_moscap            IO_DqRcv_moscap
AG_VblhActComC_Nicap       AG_VblhActComC_Nicap
R_GIDLPwr1                 R_GIDLPwr1
R_GIDLPwr2                 R_GIDLPwr2
R_GIDLPwr3                 R_GIDLPwr3

AG_ThinVfsYGateAmp         AG_ThinVfsYGateAmp
IO_TsacMdlRdClk            IO_TsacMdlRdClk
IO_ReadTsacMain            IO_ReadTsacMain
CDM_Diode_2                CDM_Diode_2
AG_VibCom                  AG_VibCom
T_IsmTop                   T_IsmTop
AG_AnalogEdgeLTop8G        AG_AnalogEdgeLTop8G
AG_VdivActTop              AG_VdivActTop
"""

netlist_A = """\
*WOWTOP_1C2A
****************************************
* Tool     : AETHER-SE
* Date     : Thu Oct 30 10:00:00 2026
* User     : zjqiao
* Top Design : drvqa_top/WOWTOP_1C2A/schematic
****************************************

.subckt switch_close POS NEG
r0 POS NEG r=0.001
.ends switch_close
** End of subcircuit definition.

.subckt switch_open POS NEG
.ends switch_open
** End of subcircuit definition.

* Library : drvqa_cmos_io
* Cell    : IO_DqLdMdl
* View    : schematic
****************************************

.SUBCKT IO_DqLdMdl DQ inh_vddq inh_vss
XI0_31 net11 DQ switch_open
XI0_32 net16 DQ switch_open
r6 net12 inh_vddq 240
c0 DQ inh_vss 500e-15
.ENDS IO_DqLdMdl

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_VdivActTop
* View    : schematic
****************************************

.SUBCKT AG_VdivActTop vdd vss ctrl
r1 vdd vss 1k
c1 ctrl vss 10e-15
.ENDS AG_VdivActTop

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_VdivActTopSpare_v2
* View    : schematic
****************************************

.SUBCKT AG_VdivActTopSpare_v2 vdd vss
r1 vdd vss 2k
.ENDS AG_VdivActTopSpare_v2

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_PosClamp
* View    : schematic
****************************************

.SUBCKT AG_PosClamp in out vdd
r1 in out 100
.ENDS AG_PosClamp

****************************************
* Library : drvqa_cmos_dig
* Cell    : T_CMDq
* View    : schematic
****************************************

.SUBCKT T_CMDq clk dq vdd vss
x1 clk dq vdd vss invLVS
.ENDS T_CMDq

****************************************
* Library : drvqa_cmos_analog
* Cell    : BCenterR
* View    : schematic
****************************************

.SUBCKT BCenterR bl br vdd
r1 bl br 50
.ENDS BCenterR

****************************************
* Library : drvqa_cmos_analog
* Cell    : BCenterL
* View    : schematic
****************************************

.SUBCKT BCenterL bl br vdd
r1 bl br 50
.ENDS BCenterL

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_BCenterL_moscap
* View    : schematic
****************************************

.SUBCKT AG_BCenterL_moscap a b
c1 a b 1e-12
.ENDS AG_BCenterL_moscap

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_BCenterL_moscap_ntk
* View    : schematic
****************************************

.SUBCKT AG_BCenterL_moscap_ntk a b
c1 a b 5e-13
.ENDS AG_BCenterL_moscap_ntk

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_BCenterL_moscap_ntk_lv2
* View    : schematic
****************************************

.SUBCKT AG_BCenterL_moscap_ntk_lv2 a b vdd
c1 a b 5e-13
r1 a vdd 1k
.ENDS AG_BCenterL_moscap_ntk_lv2

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_BCenterL_moscap_ptk
* View    : schematic
****************************************

.SUBCKT AG_BCenterL_moscap_ptk a b
c1 a b 7e-13
.ENDS AG_BCenterL_moscap_ptk

****************************************
* Library : drvqa_cmos_io
* Cell    : IO_DqRcv_moscap
* View    : schematic
****************************************

.SUBCKT IO_DqRcv_moscap a b
c1 a b 2e-12
.ENDS IO_DqRcv_moscap

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_VblhActComC_Nicap
* View    : schematic
****************************************

.SUBCKT AG_VblhActComC_Nicap a b
c1 a b 3e-13
.ENDS AG_VblhActComC_Nicap

****************************************
* Library : drvqa_cmos_analog
* Cell    : R_GIDLPwr1
* View    : schematic
****************************************

.SUBCKT R_GIDLPwr1 a b
r1 a b 100
.ENDS R_GIDLPwr1

****************************************
* Library : drvqa_cmos_analog
* Cell    : R_GIDLPwr2
* View    : schematic
****************************************

.subckt R_GIDLPwr2 a b
r1 a b 200
.ends R_GIDLPwr2

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_ThinVfsYGateAmp
* View    : schematic
****************************************

.SUBCKT AG_ThinVfsYGateAmp in out vdd
r1 in out 80
.ENDS AG_ThinVfsYGateAmp

****************************************
* Library : drvqa_cmos_io
* Cell    : IO_TsacMdlRdClk
* View    : schematic
****************************************

.SUBCKT IO_TsacMdlRdClk clk out vdd
r1 clk out 40
.ENDS IO_TsacMdlRdClk

****************************************
* Library : drvqa_cmos_io
* Cell    : IO_ReadTsacMain
* View    : schematic
****************************************

.SUBCKT IO_ReadTsacMain in out vdd vss
r1 in out 60
.ENDS IO_ReadTsacMain

****************************************
* Library : TECHLIB
* Cell    : CDM_Diode_2
* View    : schematic
****************************************

.SUBCKT CDM_Diode_2 a b
d1 a b diode
.ENDS CDM_Diode_2

****************************************
* Library : drvqa_cmos_analog
* Cell    : AG_VibCom
* View    : schematic
****************************************

.SUBCKT AG_VibCom_v2 in out vdd
r1 in out 90
.ENDS AG_VibCom_v2

* top-level instance referencing T_IsmTop (no .SUBCKT def, no * Cell header)
Xism_top top1 top2 T_IsmTop

* invLVS filler (referenced by T_CMDq)
.SUBCKT invLVS A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss
m1 Y A inh_vbulkn inh_vss nmos w=1u l=100n
m2 Y A inh_vbulkp inh_vcc pmos w=2u l=100n
.ENDS invLVS

.END
"""

# ============================================================
# hidden B assets (judge only)
# ============================================================
hcell_B = """\
PhyRdDqs                   PhyRdDqs
AG_PhonyAct                AG_PhonyAct
AG_PhonyActSpare           AG_PhonyActSpare
T_DDR5Cmd                  T_DDR5Cmd
BCenterPhyR                BCenterPhyR
BCenterPhyL                BCenterPhyL
AG_BCenterPhyR_moscap      AG_BCenterPhyR_moscap
AG_BCenterPhyR_moscap_ntk  AG_BCenterPhyR_moscap_ntk
AG_BCenterPhyR_moscap_ntk_lv AG_BCenterPhyR_moscap_ntk_lv
AG_BCenterPhyR_moscap_ptk  AG_BCenterPhyR_moscap_ptk
AG_BCenterPhyR_moscap_ptk_lv AG_BCenterPhyR_moscap_ptk_lv
IO_DDR5Rcv_moscap          IO_DDR5Rcv_moscap
AG_VblhPhyRd_Nicap         AG_VblhPhyRd_Nicap
R_GIDLPwrPhy1              R_GIDLPwrPhy1
R_GIDLPwrPhy2              R_GIDLPwrPhy2
R_GIDLPwrPhy3              R_GIDLPwrPhy3

AG_ThinVfsPhyAmp           AG_ThinVfsPhyAmp
IO_DDR5TsacRdClk           IO_DDR5TsacRdClk
IO_DDR5ReadTsacMain        IO_DDR5ReadTsacMain
CDM_Diode_4                CDM_Diode_4
AG_PhonyVibCom             AG_PhonyVibCom
T_DDR5IsmTop               T_DDR5IsmTop
AG_PhonyEdgeTop            AG_PhonyEdgeTop
AG_PhonyAct                AG_PhonyAct
"""

netlist_B = """\
*DDRTOP_PHY
****************************************
* Tool     : AETHER-SE
* Date     : Thu Oct 30 11:00:00 2026
* User     : zjqiao
* Top Design : ddr5_top/DDRTOP_PHY/schematic
****************************************

.subckt switch_close POS NEG
r0 POS NEG r=0.001
.ends switch_close

.subckt switch_open POS NEG
.ends switch_open

* Library : ddr5_cmos_phy
* Cell    : PhyRdDqs
* View    : schematic
****************************************

.SUBCKT PhyRdDqs dqs vdd vss
r1 dqs vss 30
.ENDS PhyRdDqs

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_PhonyAct
* View    : schematic
****************************************

.SUBCKT AG_PhonyAct vdd vss ctrl
r1 vdd vss 1.2k
c1 ctrl vss 12e-15
.ENDS AG_PhonyAct

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_PhonyActSpare_v2
* View    : schematic
****************************************

.SUBCKT AG_PhonyActSpare_v2 vdd vss
r1 vdd vss 2.5k
.ENDS AG_PhonyActSpare_v2

****************************************
* Library : ddr5_cmos_dig
* Cell    : T_DDR5Cmd
* View    : schematic
****************************************

.SUBCKT T_DDR5Cmd clk cmd vdd vss
x1 clk cmd vdd vss invLVS
.ENDS T_DDR5Cmd

****************************************
* Library : ddr5_cmos_phy
* Cell    : BCenterPhyR
* View    : schematic
****************************************

.SUBCKT BCenterPhyR bl br vdd
r1 bl br 55
.ENDS BCenterPhyR

****************************************
* Library : ddr5_cmos_phy
* Cell    : BCenterPhyL
* View    : schematic
****************************************

.SUBCKT BCenterPhyL bl br vdd
r1 bl br 55
.ENDS BCenterPhyL

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_BCenterPhyR_moscap
* View    : schematic
****************************************

.SUBCKT AG_BCenterPhyR_moscap a b
c1 a b 1.1e-12
.ENDS AG_BCenterPhyR_moscap

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_BCenterPhyR_moscap_ntk
* View    : schematic
****************************************

.SUBCKT AG_BCenterPhyR_moscap_ntk a b
c1 a b 5.5e-13
.ENDS AG_BCenterPhyR_moscap_ntk

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_BCenterPhyR_moscap_ntk_lv2
* View    : schematic
****************************************

.SUBCKT AG_BCenterPhyR_moscap_ntk_lv2 a b vdd
c1 a b 5.5e-13
r1 a vdd 1.2k
.ENDS AG_BCenterPhyR_moscap_ntk_lv2

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_BCenterPhyR_moscap_ptk
* View    : schematic
****************************************

.SUBCKT AG_BCenterPhyR_moscap_ptk a b
c1 a b 7.5e-13
.ENDS AG_BCenterPhyR_moscap_ptk

****************************************
* Library : ddr5_cmos_io
* Cell    : IO_DDR5Rcv_moscap
* View    : schematic
****************************************

.SUBCKT IO_DDR5Rcv_moscap a b
c1 a b 2.2e-12
.ENDS IO_DDR5Rcv_moscap

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_VblhPhyRd_Nicap
* View    : schematic
****************************************

.SUBCKT AG_VblhPhyRd_Nicap a b
c1 a b 3.3e-13
.ENDS AG_VblhPhyRd_Nicap

****************************************
* Library : ddr5_cmos_phy
* Cell    : R_GIDLPwrPhy1
* View    : schematic
****************************************

.SUBCKT R_GIDLPwrPhy1 a b
r1 a b 110
.ENDS R_GIDLPwrPhy1

****************************************
* Library : ddr5_cmos_phy
* Cell    : R_GIDLPwrPhy2
* View    : schematic
****************************************

.subckt R_GIDLPwrPhy2 a b
r1 a b 220
.ends R_GIDLPwrPhy2

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_ThinVfsPhyAmp
* View    : schematic
****************************************

.SUBCKT AG_ThinVfsPhyAmp in out vdd
r1 in out 85
.ENDS AG_ThinVfsPhyAmp

****************************************
* Library : ddr5_cmos_io
* Cell    : IO_DDR5TsacRdClk
* View    : schematic
****************************************

.SUBCKT IO_DDR5TsacRdClk clk out vdd
r1 clk out 45
.ENDS IO_DDR5TsacRdClk

****************************************
* Library : ddr5_cmos_io
* Cell    : IO_DDR5ReadTsacMain
* View    : schematic
****************************************

.SUBCKT IO_DDR5ReadTsacMain in out vdd vss
r1 in out 65
.ENDS IO_DDR5ReadTsacMain

****************************************
* Library : TECHLIB
* Cell    : CDM_Diode_4
* View    : schematic
****************************************

.SUBCKT CDM_Diode_4 a b
d1 a b diode
.ENDS CDM_Diode_4

****************************************
* Library : ddr5_cmos_phy
* Cell    : AG_PhonyVibCom
* View    : schematic
****************************************

.SUBCKT AG_PhonyVibCom_v2 in out vdd
r1 in out 95
.ENDS AG_PhonyVibCom_v2

* top-level instance referencing T_DDR5IsmTop (no .SUBCKT def, no * Cell header)
Xism_top top1 top2 T_DDR5IsmTop

.SUBCKT invLVS A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss
m1 Y A inh_vbulkn inh_vss nmos w=1u l=100n
m2 Y A inh_vbulkp inh_vcc pmos w=2u l=100n
.ENDS invLVS

.END
"""

# ---- write A/B assets ----
with open(os.path.join(A, "hcell_A"), "w") as f:
    f.write(hcell_A)
with open(os.path.join(A, "netlist_A"), "w") as f:
    f.write(netlist_A)
with open(os.path.join(A, "hidden", "hcell_B"), "w") as f:
    f.write(hcell_B)
with open(os.path.join(A, "hidden", "netlist_B"), "w") as f:
    f.write(netlist_B)

hidden_manifest = {
    "hidden_dir": "hidden",
    "files": ["netlist_B", "hcell_B"],
    "note": "Hidden input B — different library (ddr5_cmos_phy) + different blocks. check.py runs the SUT script on hcell_B + netlist_B and verifies the missing-block output."
}
import json
with open(os.path.join(A, "hidden_manifest.json"), "w") as f:
    json.dump(hidden_manifest, f, ensure_ascii=False, indent=2)

prompt_txt = """\
现在我需要你做一件事情，将hcell这个文件的第一列逐行在netlist这个文件中进行检索，看看有没有哪个block是在netlist中找不到（改过名字）的

[附件] hcell_A —— hcell 映射文件，每行两列，第一列为要在 netlist 中检索的 block 名。
[附件] netlist_A —— 一份 SPICE 网表（AETHER-SE 导出），subcell 以 `* Library : <lib>` / `* Cell    : <cell>` / `* View    : schematic` header 块 + `.SUBCKT <cell> <ports>` 定义，并含 `X<inst> <pins...> <subckt>` 实例引用。
判分时 hcell 与 netlist 路径由参数传入，不一定与上文路径相同。

交付：写一个 Python 脚本，读入 hcell 文件第一列 block 名，逐个在 netlist 中检索，把 netlist 中找不到的 block（缺失/改过名字）输出到指定文件。脚本调用方式（判分器将以此调用）：`python3 check_hcell_missing.py <hcell_file> <netlist_file> <output_file>`
提交：把脚本打包成 `outputs/submit.zip`（zip 根目录含 `check_hcell_missing.py`）。
"""
with open(os.path.join(A, "prompt.txt"), "w") as f:
    f.write(prompt_txt)

task_brief = """\
交付接口：写一个 Python 脚本，读入 hcell 文件第一列 block 名（去重保序、跳过空行），在 netlist 文件中检索每个 block（命中位置：`.SUBCKT`/`.subckt` 定义名、`* Cell :` header 值、`X` 实例引用末 token），将 netlist 中找不到的 block（缺失/改名）按 hcell 顺序写入输出文件，每行一个 block 名。
脚本调用方式（判分器将以此调用）：`python3 check_hcell_missing.py <hcell_file> <netlist_file> <output_file>`
提交：把脚本打包成 `outputs/submit.zip`（zip 根目录含 `check_hcell_missing.py`）。
"""
with open(os.path.join(A, "task_brief.md"), "w") as f:
    f.write(task_brief)

print("Assets written to", A)
print("hcell_A lines:", len(hcell_A.splitlines()), " netlist_A bytes:", len(netlist_A))
print("hcell_B lines:", len(hcell_B.splitlines()), " netlist_B bytes:", len(netlist_B))
