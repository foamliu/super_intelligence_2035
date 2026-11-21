#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-MissingRefDiagnose-001 assets + reference + check + negatives."""
import os, sys, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-MissingRefDiagnose-001"
ASSET = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)

def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path, len(content), "bytes")

# ================= A assets (visible to SUT) =================
NETLIST_A = """\
* SPICE netlist : HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu (excerpt)
* exported from schematic view
.SUBCKT HCSP_LEAF_TIEHL_CORNER TIEH TIEL TRKWL TRKWL_BCK VDD VSS
XI_cds_thru_0 TRKWL TRKWL_BCK rm2cb_fs w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res
XI_tieh0 TIEH VDD HCSP_TIEH_CELL
XI_tiel0 TIEL VSS HCSP_TIEL_CELL
.ENDS HCSP_LEAF_TIEHL_CORNER
*
.SUBCKT HCSP_LEAF_TIEHL TIEH TIEL TRKWL TRKWL_BCK VDD VSS
XI_cds_thru_1 TRKWL TRKWL_BCK rm2cb_fs w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res
XI_tieh0 TIEH VDD HCSP_TIEH_CELL
.ENDS HCSP_LEAF_TIEHL
*
.SUBCKT HCSP_BITCELL_128X4 BL BR WL VDD VSS
M0 BL WL BR VSS nsvt_fs w=0.12u l=40n
M1 BR WL BL VDD psvt_fs w=0.18u l=40n
.ENDS HCSP_BITCELL_128X4
*
.SUBCKT HCSP_LEAF_WLBUF_DUM_L WL IN VDD VSS
XINV0 IN WL HCSP_INVX4
.ENDS HCSP_LEAF_WLBUF_DUM_L
"""

DECK_A = """\
* HSPICE deck : HCSP_AA SRAM simulation (nanospice-compatible)
.param vvdd=1.1
.temp 25
.inc './netlist_A.sp'
.lib './model.lib' tt_res_fs
.tran 1n 100n
.end
"""

ERRLOG_A = """\
nanospice(3.2.1) > reading netlist : HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu.netlist
nanospice(3.2.1) > expanding subckt HCSP_LEAF_TIEHL_CORNER
nanospice(3.2.1) > Error: no reference ckt rm2cb_fs for xi_cds_thru_0  (line 1226)
nanospice(3.2.1) >   instance params: w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res
nanospice(3.2.1) > simulation aborted : unresolved reference
"""

MODEL_LIB_A = """\
* model library switch file (35H PDK, FS corner)
.lib tt_res_fs
.lib './model_setup_fs.lib' res_default
.lib './model_setup_fs.lib' res_tt
.endl tt_res_fs
"""

MODEL_SETUP_A = """\
* resistor model setup
.lib res_default
.param rctmod_res=0
.endl res_default
.lib res_tt
.lib './res_fs.mdl' res
.endl res_tt
"""

RES_FS_MDL = """\
* resistor model definitions (35H PDK, FS corner)
.lib res
.SUBCKT rm1ca_fs n1 n2 w=0.014u l=1u mr=1
rbody n1 n2 rsh=5.7 w=w l=l m=mr
.ENDS rm1ca_fs
.SUBCKT rm1cb_fs n1 n2 w=0.014u l=1u mr=1
rbody n1 n2 rsh=5.7 w=w l=l m=mr
.ENDS rm1cb_fs
.SUBCKT rms2ca_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.3 w=w l=l m=mr
.ENDS rms2ca_fs
.SUBCKT rms2cb_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.3 w=w l=l m=mr
.ENDS rms2cb_fs
.SUBCKT rms3ca_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.3 w=w l=l m=mr
.ENDS rms3ca_fs
.SUBCKT rms3cb_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.3 w=w l=l m=mr
.ENDS rms3cb_fs
.SUBCKT rmx4ca_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.1 w=w l=l m=mr
.ENDS rmx4ca_fs
.SUBCKT rmx4cb_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.1 w=w l=l m=mr
.ENDS rmx4cb_fs
.SUBCKT rmx5ca_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.1 w=w l=l m=mr
.ENDS rmx5ca_fs
.SUBCKT rmx5cb_fs n1 n2 w=0.02u l=1u mr=1
rbody n1 n2 rsh=2.1 w=w l=l m=mr
.ENDS rmx5cb_fs
.SUBCKT rmy6_fs n1 n2 w=0.038u l=1u mr=1
rbody n1 n2 rsh=0.6 w=w l=l m=mr
.ENDS rmy6_fs
.SUBCKT rmy7_fs n1 n2 w=0.038u l=1u mr=1
rbody n1 n2 rsh=0.6 w=w l=l m=mr
.ENDS rmy7_fs
.SUBCKT rmy8_fs n1 n2 w=0.038u l=1u mr=1
rbody n1 n2 rsh=0.6 w=w l=l m=mr
.ENDS rmy8_fs
.SUBCKT rmy9_fs n1 n2 w=0.038u l=1u mr=1
rbody n1 n2 rsh=0.6 w=w l=l m=mr
.ENDS rmy9_fs
.SUBCKT rmy10_fs n1 n2 w=0.038u l=1u mr=1
rbody n1 n2 rsh=0.6 w=w l=l m=mr
.ENDS rmy10_fs
.endl res
"""

w(os.path.join(ASSET, "netlist_A.sp"), NETLIST_A)
w(os.path.join(ASSET, "deck_A.sp"), DECK_A)
w(os.path.join(ASSET, "error_log_A.txt"), ERRLOG_A)
w(os.path.join(ASSET, "model_lib_A", "model.lib"), MODEL_LIB_A)
w(os.path.join(ASSET, "model_lib_A", "model_setup_fs.lib"), MODEL_SETUP_A)
w(os.path.join(ASSET, "model_lib_A", "res_fs.mdl"), RES_FS_MDL)

# ================= Hidden B (cap family, .model format) =================
NETLIST_B = """\
* SPICE netlist : HCSP_AA decouple network (excerpt)
* exported from schematic view
.SUBCKT HCSP_LEAF_DECOUPLE VDD VSS VSSP
XCD_cpl0 VDD VSS cm2n_fs w=40n l=200n mr=1
XCD_cpl1 VDD VSSP cm2m_fs w=40n l=200n mr=1
XINV0 VDD VSSP HCSP_INVX2
.ENDS HCSP_LEAF_DECOUPLE
*
.SUBCKT HCSP_LEAF_BIAS VDD VSS VBIAS
M0 VBIAS VBIAS VSS nsvt_fs w=0.2u l=1u
.ENDS HCSP_LEAF_BIAS
"""

DECK_B = """\
* HSPICE deck : HCSP_AA decouple simulation
.param vvdd=1.1
.temp 25
.inc './netlist_B.sp'
.lib './cap.lib' tt_cap_fs
.ac dec 10 1 1g
.end
"""

ERRLOG_B = """\
hspice(2024.09) > reading netlist : HCSP_AA_decouple.netlist
hspice(2024.09) > expanding subckt HCSP_LEAF_DECOUPLE
hspice(2024.09) > Error: no reference ckt cm2n_fs for xcd_cpl0  (line 487)
hspice(2024.09) >   instance params: w=40n l=200n mr=1
hspice(2024.09) > simulation aborted : unresolved reference
"""

CAP_LIB = """\
* capacitor library switch file
.lib tt_cap_fs
.lib './cap_setup_fs.lib' cap_default
.lib './cap_setup_fs.lib' cap_tt
.endl tt_cap_fs
"""

CAP_SETUP = """\
* capacitor model setup
.lib cap_default
.param cctmod_cap=0
.endl cap_default
.lib cap_tt
.lib './cap_fs.mdl' cap
.endl cap_tt
"""

CAP_FS_MDL = """\
* capacitor model definitions (FS corner)
.lib cap
.model cm1m_fs c rsh=0.8e-3 w=0.04u
.model cm2m_fs c rsh=0.8e-3 w=0.06u
.model cm3m_fs c rsh=0.8e-3 w=0.08u
.model cm4m_fs c rsh=0.8e-3 w=0.10u
.model cm5m_fs c rsh=0.8e-3 w=0.12u
.endl cap
"""

HB = os.path.join(REF, "hidden_B")
w(os.path.join(HB, "netlist_B.sp"), NETLIST_B)
w(os.path.join(HB, "deck_B.sp"), DECK_B)
w(os.path.join(HB, "error_log_B.txt"), ERRLOG_B)
w(os.path.join(HB, "model_lib_B", "cap.lib"), CAP_LIB)
w(os.path.join(HB, "model_lib_B", "cap_setup_fs.lib"), CAP_SETUP)
w(os.path.join(HB, "model_lib_B", "cap_fs.mdl"), CAP_FS_MDL)

MANIFEST = {
    "case_id": CASE,
    "description": "Hidden B: capacitor family (.model format), typo cm2n_fs (real cm2m_fs), subckt HCSP_LEAF_DECOUPLE, instance XCD_cpl0, .lib chain cap.lib/cap_setup_fs.lib/cap_fs.mdl. Differs from A in model family/format/names/instance/nodes/params/chain.",
    "inputs": ["deck_B.sp", "netlist_B.sp", "error_log_B.txt", "model_lib_B/"],
    "expected_missing": "cm2n_fs",
    "expected_instance": "XCD_cpl0",
    "expected_best_suggestion": "cm2m_fs",
    "A_only_tokens_forbidden": ["rm2cb_fs", "rms2cb_fs", "rm1cb_fs", "HCSP_LEAF_TIEHL_CORNER", "xi_cds_thru_0", "TRKWL", "res_fs", "rctmod_res", "tt_res_fs"],
}
w(os.path.join(HB, "hidden_manifest.json"), json.dumps(MANIFEST, indent=2))

print("DONE A + hidden_B")
