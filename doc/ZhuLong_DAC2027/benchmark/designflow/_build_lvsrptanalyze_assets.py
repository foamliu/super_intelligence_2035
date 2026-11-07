#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-LvsRptAnalyze-001 case assets, reference, check, negatives.

Case: LVS report analyzer — parse Calibre LVS report + .ext + .erc.summary,
categorize errors, generate structured Markdown analysis report + error_summary.json.
Trace: erhym/fhwang/10.129.2.14/mc50 (schematic_netlist, B-grade synthesized L1).
"""
import json, os, shutil, subprocess, sys, zipfile, hashlib

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-LvsRptAnalyze-001"
REF = os.path.join(REPO, "reference", CID)
AST = os.path.join(REPO, "assets", CID)
for d in [REF, AST, os.path.join(AST, "hidden"), os.path.join(REF, "negative")]:
    os.makedirs(d, exist_ok=True)

# ───────────────────────── A input (visible to SUT) ─────────────────────────
# Mimics real erhym trace: Array3G_TOP_L, INCORRECT, Calibre v2020.1, 1224 smashed,
# Property W 2.717u vs 1.476u, .ext warnings SecEnGapN/vap2!/viso!

LVS_REPORT_A = """# Calibre v2020.1_36.18 LVS run
# Cell: Array3G_TOP_L
# Layout: Array3G_TOP_L.gds
# Source: Array3G_TOP_L.cdl
# LVS rule: INCLUDE /apps/imctf/cad/runset/drcpa/v0/current/calibreLVS.rule
#
# LVS RECOGNIZE GATES = NONE
# LVS FILTER UNUSED OPTION = NONE SOURCE LAYOUT
# LVS ISOLATE SHORTS = YES BY LAYER ALSO BY CELL ALSO CELL PRIMARY && NAME "?"
# VIRTUAL CONNECT COLON = NO
# VIRTUAL CONNECT REPORT = YES UNSATISFIED
# LVS EXECUTE ERC = YES
# LVS SPICE ALLOW FLOATING PINS = YES
#
# CPU time: 264s   Elapsed: 287s
# Total lines in report: 1986972

=========================================
LVS COMPARISON RESULTS
=========================================
Overall LVS Result: INCORRECT

Connectivity errors: YES
Property errors: YES
Unbalanced smashed mosfets matched: YES

SUMMARY OF TOTAL RESULTS
Total cells compared: 4521
Correct cells: 4515
Incorrect cells: 6

CELL COMPARISON RESULTS
Cell: Array3G_TOP_L  Result: INCORRECT

INCORRECT OBJECTS
Layout: X2/X0/X160/X0/X23/XI28  Source: XI_Array768Meg_Top_L_2/XI_AG_AnalogFar_Top_L_76/XI_AG_FarSubL_12
  Property: W does not match
  Device: MP(ptn)

Property Error #22: Layout W = 2.717u  Source W = 1.476u  diff = 84.1%  Device: MP(ptn)
Property Error #23: Layout W = 1.476u  Source W = 2.717u  diff = 45.7%  Device: MP(ptn)
Property Error #24: Layout W = 2.717u  Source W = 1.476u  diff = 84.1%  Device: MP(ptn)

Connectivity error: drain of X2/X0/X160/X0/X23/XI28 has no similar net in source
  Layout net: VblhActBank_0
  Source net: <none>
Connectivity error: source of X0/X73/X142/X0/X23/XI19 has no similar net in source
  Layout net: VwlpDetectF
  Source net: <none>

MISSING SMASHED MOSFET
missing smashed mosfet: 1224 occurrences
Unbalanced smashed mosfets were matched: 1224

SHORT/OPEN SCAN
Short circuits found: 0
Open circuits detected: 2

ERC SUMMARY
ERC errors: 0
ERC warnings: 18

END OF LVS REPORT
"""

LVS_EXT_A = """# Extraction warnings for Array3G_TOP_L
# Calibre v2020.1_36.18

Open circuit - Same name on different nets
  cell "R_GrDecX174G0":
    Name: "SecEnGapN"
    (1) at (60.892,96.168) on M2_pin, net id 201
    (2) at (62.602,114.968) on M2_pin, net id 204
Open circuit - Same name on different nets
  cell "Array768Meg_Top_L":
    Name: "vap2!"
    (1) at (-57.394,-1.04) on M4_pin, net id 311
    (2) at (57.056,-1.04) on M4_pin, net id 11

Unattached label
  cell "R_PhDecX4_UV": "viso!" at (43.0285,25.958) on M1_pin
Unattached label
  cell "R_Eqio_SaCtrol_drv_UV_inv": "VncsgnEn" at (23.707,-8.886) on M0U_pin
Unattached label
  cell "R_NegPowerGate_IDD3N_OcEn": "vncsgn!" at (-6.2991,1.756) on PW_pin
Unattached label
  cell "R_SaCtrol_IsoOcEn_Burnin_top_base": "vncsgn!" at (-102.4151,-616.93) on PW_pin
Unattached label
  cell "R_SaCtrol_IsoOcEn_Burnin_top_base": "vncsgn!" at (-102.4151,-606.21) on PW_pin

Unattached port
  cell "R_PhDecX4_UV": port "viso!" unattached
Unattached port
  cell "R_Eqio_SaCtrol_drv_UV_inv": port "VncsgnEn" unattached
Unattached port
  cell "R_NegPowerGate_IDD3N_OcEn": port "vncsgn!" unattached
Unattached port
  cell "R_SaCtrol_IsoOcEn_Burnin_top_base": port "vncsgn!" unattached
Unattached port
  cell "R_GrDecX174G0": port "SecEnGapN" unattached
Unattached port
  cell "Array768Meg_Top_L": port "vap2!" unattached

Virtually connected label
  cell "Array3G_TOP_L": "vap2!" at (-606.4716,1581.056) and (-606.4716,1466.606) on M4_pin
Virtually connected label
  cell "Array3G_TOP_L": "vmwln!" at (-597.9326,10440.177) on M4_pin
Virtually connected label
  cell "Array3G_TOP_L": "vmwln!" at (-597.9326,7463.177) on M4_pin
Virtually connected label
  cell "Array3G_TOP_L": "vmwln!" at (-597.9326,4486.177) on M4_pin

Stamping conflict
  SCONNECT stamping conflict on net "vss!": 19470 nets rejected
"""

ERC_SUMMARY_A = """# ERC summary for Array3G_TOP_L
ERC errors: 0
ERC warnings: 18
  - Virtually connected labels: 4
  - Unattached labels: 5
  - Open circuit (same name diff nets): 2
  - Stamping conflict: 1
  - Soft check warnings: 6
"""

# ───────────────────────── hidden B (different design, INCORRECT) ─────────────
# DDR5_PHY_TOP, Calibre v2022.4, 856 smashed, W 0.840u vs 0.420u, vcore!/vref!

LVS_REPORT_B = """# Calibre v2022.4_12.3 LVS run
# Cell: DDR5_PHY_TOP
# Layout: DDR5_PHY_TOP.gds
# Source: DDR5_PHY_TOP.cdl
# LVS rule: INCLUDE /apps/imctf/cad/runset/phy/v0/current/calibreLVS.rule
#
# LVS RECOGNIZE GATES = ALL
# LVS FILTER UNUSED OPTION = SOME SOURCE LAYOUT
# LVS ISOLATE SHORTS = YES BY LAYER
# VIRTUAL CONNECT COLON = YES
# VIRTUAL CONNECT REPORT = YES ALL
# LVS EXECUTE ERC = YES
# LVS SPICE ALLOW FLOATING PINS = NO
#
# CPU time: 412s   Elapsed: 445s
# Total lines in report: 456789

=========================================
LVS COMPARISON RESULTS
=========================================
Overall LVS Result: INCORRECT

Connectivity errors: YES
Property errors: YES
Unbalanced smashed mosfets matched: YES

SUMMARY OF TOTAL RESULTS
Total cells compared: 3210
Correct cells: 3202
Incorrect cells: 8

CELL COMPARISON RESULTS
Cell: DDR5_PHY_TOP  Result: INCORRECT

INCORRECT OBJECTS
Layout: X5/X1/X80/X3/XI12  Source: XI_DDR5_PHY_Array/XI_AG_Core_Top_L_31/XI_AG_SubL_8
  Property: W does not match
  Device: MP(ptn)

Property Error #5: Layout W = 0.840u  Source W = 0.420u  diff = 100.0%  Device: MP(ptn)
Property Error #6: Layout W = 0.420u  Source W = 0.840u  diff = 50.0%  Device: MP(ptn)
Property Error #7: Layout W = 1.200u  Source W = 0.600u  diff = 100.0%  Device: MN(ntn)

Connectivity error: drain of X5/X1/X80/X3/XI12 has no similar net in source
  Layout net: vcore!
  Source net: <none>
Connectivity error: source of X9/X22/X140/X3/XI07 has no similar net in source
  Layout net: vref!
  Source net: <none>

MISSING SMASHED MOSFET
missing smashed mosfet: 856 occurrences
Unbalanced smashed mosfets were matched: 856

SHORT/OPEN SCAN
Short circuits found: 0
Open circuits detected: 7

ERC SUMMARY
ERC errors: 0
ERC warnings: 29

END OF LVS REPORT
"""

LVS_EXT_B = """# Extraction warnings for DDR5_PHY_TOP
# Calibre v2022.4_12.3

Open circuit - Same name on different nets
  cell "R_PhyDecX8_UV":
    Name: "vcore!"
    (1) at (12.40,55.71) on M3_pin, net id 502
    (2) at (88.10,55.71) on M3_pin, net id 88
Open circuit - Same name on different nets
  cell "R_CtlDecoder_UV":
    Name: "vref!"
    (1) at (-3.21,17.04) on M4_pin, net id 711
    (2) at (44.99,17.04) on M4_pin, net id 45
Open circuit - Same name on different nets
  cell "R_PhyClkTree_UV":
    Name: "vcore!"
    (1) at (5.50,99.30) on M3_pin, net id 230
    (2) at (5.50,12.00) on M3_pin, net id 731
Open circuit - Same name on different nets
  cell "R_PhyBias_UV":
    Name: "vbias!"
    (1) at (0.00,1.00) on M2_pin, net id 9
    (2) at (0.00,88.00) on M2_pin, net id 604
Open circuit - Same name on different nets
  cell "R_PhyIoTop_UV":
    Name: "vcore!"
    (1) at (15.0,77.0) on M3_pin, net id 333
    (2) at (15.0,3.0) on M3_pin, net id 102
Open circuit - Same name on different nets
  cell "R_PhyEqTop_UV":
    Name: "vref!"
    (1) at (22.0,44.0) on M4_pin, net id 718
    (2) at (22.0,1.0) on M4_pin, net id 55
Open circuit - Same name on different nets
  cell "R_PhyTop_UV":
    Name: "vbias!"
    (1) at (7.0,7.0) on M2_pin, net id 12
    (2) at (7.0,77.0) on M2_pin, net id 700

Unattached label
  cell "R_PhyDecX8_UV": "vcore!" at (12.40,55.71) on M3_pin
Unattached label
  cell "R_CtlDecoder_UV": "vref!" at (-3.21,17.04) on M4_pin
Unattached label
  cell "R_PhyBias_UV": "vbias!" at (0.00,1.00) on M2_pin
Unattached label
  cell "R_PhyClkTree_UV": "vcore!" at (5.50,99.30) on M3_pin
Unattached label
  cell "R_PhyIoTop_UV": "vcore!" at (15.0,77.0) on M3_pin
Unattached label
  cell "R_PhyEqTop_UV": "vref!" at (22.0,44.0) on M4_pin
Unattached label
  cell "R_PhyTop_UV": "vbias!" at (7.0,7.0) on M2_pin
Unattached label
  cell "R_PhyDqTop_UV": "vddq!" at (3.0,3.0) on M5_pin
Unattached label
  cell "R_PhyDqsTop_UV": "vddq!" at (4.0,4.0) on M5_pin
Unattached label
  cell "R_PhyCaTop_UV": "vssx!" at (2.0,2.0) on M1_pin
Unattached label
  cell "R_PhyZqTop_UV": "vssx!" at (8.0,8.0) on M1_pin
Unattached label
  cell "R_PhyAddrTop_UV": "vssx!" at (9.0,9.0) on M1_pin

Unattached port
  cell "R_PhyDecX8_UV": port "vcore!" unattached
Unattached port
  cell "R_CtlDecoder_UV": port "vref!" unattached
Unattached port
  cell "R_PhyBias_UV": port "vbias!" unattached

Virtually connected label
  cell "DDR5_PHY_TOP": "vcore!" at (0.0,0.0) and (99.0,99.0) on M3_pin
Virtually connected label
  cell "DDR5_PHY_TOP": "vref!" at (1.0,1.0) and (98.0,98.0) on M4_pin
Virtually connected label
  cell "DDR5_PHY_TOP": "vbias!" at (2.0,2.0) and (97.0,97.0) on M2_pin
Virtually connected label
  cell "DDR5_PHY_TOP": "vddq!" at (3.0,3.0) and (96.0,96.0) on M5_pin
Virtually connected label
  cell "DDR5_PHY_TOP": "vssx!" at (4.0,4.0) and (95.0,95.0) on M1_pin

Stamping conflict
  SCONNECT stamping conflict on net "vss!": 8842 nets rejected
Stamping conflict
  SCONNECT stamping conflict on net "vdd!": 3110 nets rejected
"""

ERC_SUMMARY_B = """# ERC summary for DDR5_PHY_TOP
ERC errors: 0
ERC warnings: 29
  - Virtually connected labels: 5
  - Unattached labels: 12
  - Open circuit (same name diff nets): 7
  - Stamping conflict: 2
  - Soft check warnings: 3
"""

# ───────────────────────── hidden B2 (CORRECT case — pass) ─────────────────
# AES_CORE, CORRECT, no errors

LVS_REPORT_B2 = """# Calibre v2022.4_12.3 LVS run
# Cell: AES_CORE
# Layout: AES_CORE.gds
# Source: AES_CORE.cdl
# LVS rule: INCLUDE /apps/imctf/cad/runset/aes/v0/current/calibreLVS.rule
#
# LVS RECOGNIZE GATES = ALL
# LVS FILTER UNUSED OPTION = SOME SOURCE LAYOUT
# LVS ISOLATE SHORTS = YES BY LAYER
# VIRTUAL CONNECT COLON = YES
# VIRTUAL CONNECT REPORT = YES ALL
# LVS EXECUTE ERC = YES
# LVS SPICE ALLOW FLOATING PINS = NO
#
# CPU time: 38s   Elapsed: 41s
# Total lines in report: 12450

=========================================
LVS COMPARISON RESULTS
=========================================
Overall LVS Result: CORRECT

Connectivity errors: NO
Property errors: NO
Unbalanced smashed mosfets matched: NO

SUMMARY OF TOTAL RESULTS
Total cells compared: 890
Correct cells: 890
Incorrect cells: 0

CELL COMPARISON RESULTS
Cell: AES_CORE  Result: CORRECT

No INCORRECT OBJECTS found.

MISSING SMASHED MOSFET
missing smashed mosfet: 0 occurrences
Unbalanced smashed mosfets were matched: 0

SHORT/OPEN SCAN
Short circuits found: 0
Open circuits detected: 0

ERC SUMMARY
ERC errors: 0
ERC warnings: 0

END OF LVS REPORT
"""

LVS_EXT_B2 = """# Extraction warnings for AES_CORE
# Calibre v2022.4_12.3
# No extraction warnings.
"""

ERC_SUMMARY_B2 = """# ERC summary for AES_CORE
ERC errors: 0
ERC warnings: 0
"""

# ───────────────────────── write assets ─────────────────────────
with open(os.path.join(AST, "lvs_report_A.txt"), "w") as f: f.write(LVS_REPORT_A)
with open(os.path.join(AST, "lvs_report_A.txt.ext"), "w") as f: f.write(LVS_EXT_A)
with open(os.path.join(AST, "erc_summary_A.txt"), "w") as f: f.write(ERC_SUMMARY_A)

HID = os.path.join(AST, "hidden")
with open(os.path.join(HID, "lvs_report_B.txt"), "w") as f: f.write(LVS_REPORT_B)
with open(os.path.join(HID, "lvs_report_B.txt.ext"), "w") as f: f.write(LVS_EXT_B)
with open(os.path.join(HID, "erc_summary_B.txt"), "w") as f: f.write(ERC_SUMMARY_B)
with open(os.path.join(HID, "lvs_report_B2.txt"), "w") as f: f.write(LVS_REPORT_B2)
with open(os.path.join(HID, "lvs_report_B2.txt.ext"), "w") as f: f.write(LVS_EXT_B2)
with open(os.path.join(HID, "erc_summary_B2.txt"), "w") as f: f.write(ERC_SUMMARY_B2)

manifest = {
    "hidden_inputs": [
        {"id": "B",  "report": "lvs_report_B.txt",  "ext": "lvs_report_B.txt.ext",  "erc": "erc_summary_B.txt",  "top_cell": "DDR5_PHY_TOP", "lvs_result": "INCORRECT"},
        {"id": "B2", "report": "lvs_report_B2.txt", "ext": "lvs_report_B2.txt.ext", "erc": "erc_summary_B2.txt", "top_cell": "AES_CORE",    "lvs_result": "CORRECT"},
    ],
    "note": "B is a different design (DDR5_PHY_TOP) with different errors; B2 is a CORRECT (pass) case to test the analyzer handles no-error reports."
}
with open(os.path.join(HID, "hidden_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

print("assets written to", AST)
print("hidden written to", HID)
