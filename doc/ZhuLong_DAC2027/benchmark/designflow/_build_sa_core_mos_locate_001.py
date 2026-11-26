#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build assets + reference for EDA-Eval-DesignFlow-SaCoreMosLocate-001.

Trace-faithful (A) source: yuyingc @ hfeg0pkn001, session 1793623698314_n7w6c
U#38 (verbatim): find the 4 MOS in the SA sense amplifier that determine
pull-up/down of v(blasec28<562>) in the netlist. Gold = assistant traced
hierarchy -> CXSA1x4_die2_fbcc SA, identified 4 cross-coupled core MOS:
  - 2 NMOS pull-down (XMMN0/XMMN1, NCS-enabled, cross bitline gate,
    delvto=delvtoBL<k>_NsL/NsR)
  - 2 PMOS pull-up  (XMMP7/XMMP8, PCS-enabled, cross Sa-node gate,
    delvto=delvtoBL<k>_PsL/PsR)

Generates: A netlist (visible), B netlist (hidden, structurally different:
reversed port order, different subckt/instance/model names, different bit,
2 decoy SAs vs 1), hidden_manifest.json with expected values.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE_ID = "EDA-Eval-DesignFlow-SaCoreMosLocate-001"
ASSETS = os.path.join(BENCH, 'assets', CASE_ID)
REF = os.path.join(BENCH, 'reference', CASE_ID)
HIDDEN = os.path.join(REF, 'hidden')
NEG = os.path.join(REF, 'negative')
for d in (ASSETS, REF, HIDDEN, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- A netlist (visible) ----------
# top signal Blasec28<562> -> XI_sa562 arg[1] -> port Bla<2> -> bit 2 -> delvtoBL2_*
A_NETLIST = """* SPICE PEX netlist (A) - SA sense-amp core MOS locator
* trace-faithful reconstruction: yuyingc @ hfeg0pkn001, session 1793623698314_n7w6c U#38
* top signal under test: Blasec28<562>
* hierarchy: sim_top -> XI_sa562 -> CXSA1x4_die2_fbcc (bit 2 -> delvtoBL2_*)

* ---- MOS model wrappers (PEX-style, with delvto) ----
.SUBCKT ntnlvio_sa d g s b w=0 l=0 nf=1 delvto=0
M0 d g s b nch w='w' l='l' nf=nf delvto='delvto'
.ENDS ntnlvio_sa
.SUBCKT ptnlvio_sa d g s b w=0 l=0 nf=1 delvto=0
M0 d g s b pch w='w' l='l' nf=nf delvto='delvto'
.ENDS ptnlvio_sa
.SUBCKT ntnlvio_sw d g s b w=0 l=0 nf=1
M0 d g s b nch w='w' l='l' nf=nf
.ENDS ntnlvio_sw
.SUBCKT ptnlvio_sw d g s b w=0 l=0 nf=1
M0 d g s b pch w='w' l='l' nf=nf
.ENDS ptnlvio_sw
.SUBCKT resrc p n r=1k
R0 p n r='r'
.ENDS resrc
.SUBCKT caprc p n c=1f
C0 p n c='c'
.ENDS caprc

* ---- SA subckt: 4 bits, each = 4 core MOS (delvto) + decoy precharge/iso/colsel (no delvto) ----
.SUBCKT CXSA1x4_die2_fbcc Bla<3> Bla<2> Bla<1> Bla<0> Blb<3> Blb<2> Blb<1> Blb<0> Csl Io<3> Io<2> Io<1> Io<0> Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss
* bit 0 core (delvtoBL0_*) - decoy by bit (NOT target)
XMMN0   SaBla<0>  Blb_local<0>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL0_NsL*0.5'
XMMN1   SaBlb<0>  Bla_local<0>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL0_NsR*0.5'
XMMP7   SaBla<0>  SaBlb<0>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL0_PsL*0.5'
XMMP8   SaBlb<0>  SaBla<0>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL0_PsR*0.5'
* bit 1 core (delvtoBL1_*) - decoy by bit
XMMN0_1 SaBla<1>  Blb_local<1>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL1_NsL*0.5'
XMMN1_1 SaBlb<1>  Bla_local<1>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL1_NsR*0.5'
XMMP7_1 SaBla<1>  SaBlb<1>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL1_PsL*0.5'
XMMP8_1 SaBlb<1>  SaBla<1>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL1_PsR*0.5'
* bit 2 core (delvtoBL2_*) - TARGET BIT (Blasec28<562> -> Bla<2>)
XMMN0_2 SaBla<2>  Blb_local<2>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL2_NsL*0.5'
XMMN1_2 SaBlb<2>  Bla_local<2>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL2_NsR*0.5'
XMMP7_2 SaBla<2>  SaBlb<2>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL2_PsL*0.5'
XMMP8_2 SaBlb<2>  SaBla<2>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL2_PsR*0.5'
* bit 3 core (delvtoBL3_*) - decoy by bit
XMMN0_3 SaBla<3>  Blb_local<3>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL3_NsL*0.5'
XMMN1_3 SaBlb<3>  Bla_local<3>  NCS  inh_vss  ntnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL3_NsR*0.5'
XMMP7_3 SaBla<3>  SaBlb<3>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL3_PsL*0.5'
XMMP8_3 SaBlb<3>  SaBla<3>  PCS  inh_vblhbk  ptnlvio_sa  w=228e-9 l=97e-9 nf=1 delvto='delvtoBL3_PsR*0.5'
* bit 2 decoy MOS (precharge/iso/colsel) - NO delvto, must be excluded
XMMP0_2 SaBla<2>  PreEq_a  PCS  inh_vblhbk  ptnlvio_sw  w=100e-9 l=80e-9
XMMP1_2 SaBlb<2>  PreEq_b  PCS  inh_vblhbk  ptnlvio_sw  w=100e-9 l=80e-9
XMMN2_2 SaBla<2>  Iso  NCS  inh_vss  ntnlvio_sw  w=120e-9 l=80e-9
XMMN3_2 Io<2>  Csl  SaBla<2>  inh_vss  ntnlvio_sw  w=120e-9 l=80e-9
* parasitic R/C decoys (bit 2) - not MOS
XRC0_2  SaBla<2>  inh_vss  resrc  r=50
XCC0_2  SaBla<2>  inh_vss  caprc  c=2f
.ENDS CXSA1x4_die2_fbcc

* ---- top-level subckt ----
.SUBCKT sim_top Blasec28<575> Blasec28<562> Blasec28<0> BlbTop<575> BlbTop<562> BlbTop<0> BlaDummy<9> BlbDummy<9>
* decoy SA instance (connects Dummy, NOT the target signal) - must be excluded
XI_decoySA BlaDummy<9> BlaDummy<8> BlaDummy<7> BlaDummy<6> BlbDummy<9> BlbDummy<8> BlbDummy<7> BlbDummy<6> Csl Io3 Io2 Io1 Io0 Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss CXSA1x4_die2_fbcc
* the real SA instance: Blasec28<562> -> arg[1] -> Bla<2> -> bit 2 -> delvtoBL2_*
XI_sa562 Blasec28<575> Blasec28<562> Blasec28<0> BlaDummy<9> BlbTop<575> BlbTop<562> BlbTop<0> BlbDummy<9> Csl Io3 Io2 Io1 Io0 Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss CXSA1x4_die2_fbcc
.ENDS sim_top
"""

# ---------- B netlist (hidden, structurally different) ----------
# REVERSED port order (Bla<0>..Bla<3>); Blasec28<417> -> arg[3] -> Bla<3> -> bit 3 -> delvtoBL3_*
# different subckt/instance/model names; 2 decoy SAs (scale); different w/l
B_NETLIST = """* SPICE PEX netlist (B) - SA sense-amp core MOS locator (hidden)
* structurally different from A: reversed port order, renamed subckts/instances/models,
* different target bit (3), 2 decoy SA instances.
* top signal under test: Blasec28<417> -> XI_sa417 arg[3] -> port Bla<3> -> bit 3 -> delvtoBL3_*

.SUBCKT ntnlvio_saB d g s b w=0 l=0 nf=1 delvto=0
M0 d g s b nch w='w' l='l' nf=nf delvto='delvto'
.ENDS ntnlvio_saB
.SUBCKT ptnlvio_saB d g s b w=0 l=0 nf=1 delvto=0
M0 d g s b pch w='w' l='l' nf=nf delvto='delvto'
.ENDS ptnlvio_saB
.SUBCKT ntnlvio_swB d g s b w=0 l=0 nf=1
M0 d g s b nch w='w' l='l' nf=nf
.ENDS ntnlvio_swB
.SUBCKT ptnlvio_swB d g s b w=0 l=0 nf=1
M0 d g s b pch w='w' l='l' nf=nf
.ENDS ptnlvio_swB
.SUBCKT resrcB p n r=1k
R0 p n r='r'
.ENDS resrcB
.SUBCKT caprcB p n c=1f
C0 p n c='c'
.ENDS caprcB

* ---- SA subckt B: REVERSED port order Bla<0> Bla<1> Bla<2> Bla<3> ----
.SUBCKT CXSA1x4_die2_fbccB Bla<0> Bla<1> Bla<2> Bla<3> Blb<0> Blb<1> Blb<2> Blb<3> Csl Io<0> Io<1> Io<2> Io<3> Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss
* bit 0 core (delvtoBL0_*) - decoy by bit
XN0_b0 SaBla<0> Blb_local<0> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL0_NsL*0.5'
XN1_b0 SaBlb<0> Bla_local<0> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL0_NsR*0.5'
XP0_b0 SaBla<0> SaBlb<0> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL0_PsL*0.5'
XP1_b0 SaBlb<0> SaBla<0> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL0_PsR*0.5'
* bit 1 core (delvtoBL1_*) - decoy by bit
XN0_b1 SaBla<1> Blb_local<1> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL1_NsL*0.5'
XN1_b1 SaBlb<1> Bla_local<1> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL1_NsR*0.5'
XP0_b1 SaBla<1> SaBlb<1> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL1_PsL*0.5'
XP1_b1 SaBlb<1> SaBla<1> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL1_PsR*0.5'
* bit 2 core (delvtoBL2_*) - decoy by bit
XN0_b2 SaBla<2> Blb_local<2> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL2_NsL*0.5'
XN1_b2 SaBlb<2> Bla_local<2> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL2_NsR*0.5'
XP0_b2 SaBla<2> SaBlb<2> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL2_PsL*0.5'
XP1_b2 SaBlb<2> SaBla<2> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL2_PsR*0.5'
* bit 3 core (delvtoBL3_*) - TARGET BIT (Blasec28<417> -> Bla<3>)
XN0_b3 SaBla<3> Blb_local<3> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL3_NsL*0.5'
XN1_b3 SaBlb<3> Bla_local<3> NCS inh_vss ntnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL3_NsR*0.5'
XP0_b3 SaBla<3> SaBlb<3> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL3_PsL*0.5'
XP1_b3 SaBlb<3> SaBla<3> PCS inh_vblhbk ptnlvio_saB w=300e-9 l=90e-9 nf=1 delvto='delvtoBL3_PsR*0.5'
* bit 3 decoy MOS (no delvto) - must be excluded
XMPC0_b3 SaBla<3> PreEq_a PCS inh_vblhbk ptnlvio_swB w=110e-9 l=70e-9
XMPC1_b3 SaBlb<3> PreEq_b PCS inh_vblhbk ptnlvio_swB w=110e-9 l=70e-9
XMIC0_b3 SaBla<3> Iso NCS inh_vss ntnlvio_swB w=130e-9 l=70e-9
XMIC1_b3 Io<3> Csl SaBla<3> inh_vss ntnlvio_swB w=130e-9 l=70e-9
* parasitic R/C decoys (bit 3)
XRC0_b3 SaBla<3> inh_vss resrcB r=42
XCC0_b3 SaBla<3> inh_vss caprcB c=3f
.ENDS CXSA1x4_die2_fbccB

* ---- top-level subckt B ----
.SUBCKT sim_topB Blasec28<417> Blasec28<300> Blasec28<0> BlbTopB<417> BlbTopB<300> BlbTopB<0> BlaDummyB<9> BlaDummyB<7> BlbDummyB<9>
* decoy SA instance #1 (connects DummyB, NOT the target signal) - must be excluded
XI_decoySA1 BlaDummyB<9> BlaDummyB<8> BlaDummyB<7> BlaDummyB<6> BlbDummyB<9> BlbDummyB<8> BlbDummyB<7> BlbDummyB<6> Csl Io0 Io1 Io2 Io3 Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss CXSA1x4_die2_fbccB
* decoy SA instance #2 (scale differs from A's single decoy)
XI_decoySA2 BlaDummyB<7> BlaDummyB<6> BlaDummyB<5> BlaDummyB<4> BlbDummyB<7> BlbDummyB<6> BlbDummyB<5> BlbDummyB<4> Csl Io0 Io1 Io2 Io3 Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss CXSA1x4_die2_fbccB
* the real SA: Blasec28<417> -> arg[3] -> Bla<3> -> bit 3 -> delvtoBL3_*
XI_sa417 BlaDummyB<9> BlaDummyB<8> BlaDummyB<7> Blasec28<417> BlbDummyB<9> BlbDummyB<8> BlbDummyB<7> BlbTopB<417> Csl Io0 Io1 Io2 Io3 Iso NCS OcEn PCS PreEq_a PreEq_b Sel inh_vad2 inh_vblhbk inh_vss CXSA1x4_die2_fbccB
.ENDS sim_topB
"""

with open(os.path.join(ASSETS, 'netlist'), 'w', encoding='utf-8') as f:
    f.write(A_NETLIST)
with open(os.path.join(HIDDEN, 'B_netlist'), 'w', encoding='utf-8') as f:
    f.write(B_NETLIST)

manifest = {
    "case_id": CASE_ID,
    "hidden_inputs": {
        "B_netlist": "B_netlist",
        "B_top_signal": "Blasec28<417>",
        "B_expected_bit_index": 3,
        "B_expected_sa_subckt": "CXSA1x4_die2_fbccB",
        "B_expected_sa_instance": "XI_sa417",
        "B_expected_delvto_prefix": "delvtoBL3",
        "B_expected_instances": ["XN0_b3", "XN1_b3", "XP0_b3", "XP1_b3"],
    },
    "A_visible": {
        "A_netlist": "assets/" + CASE_ID + "/netlist",
        "A_top_signal": "Blasec28<562>",
        "A_expected_bit_index": 2,
        "A_expected_sa_subckt": "CXSA1x4_die2_fbcc",
        "A_expected_sa_instance": "XI_sa562",
        "A_expected_delvto_prefix": "delvtoBL2",
        "A_expected_instances": ["XMMN0_2", "XMMN1_2", "XMMP7_2", "XMMP8_2"],
    },
    "note": "B is structurally different from A: reversed SA port order (Bla<0..3> vs Bla<3..0>), renamed SA subckt (CXSA1x4_die2_fbccB) + model wrappers (ntnlvio_saB/ptnlvio_saB) + core MOS instance names (M_sa_*_b3 vs XMMN0_2/..), different target bit (3 vs 2), 2 decoy SA instances (vs 1), different w/l. Forces structural discovery (no hardcoded port-index or instance-name). Cross-input guard runs candidate on BOTH A and B.",
}
with open(os.path.join(HIDDEN, 'hidden_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# prompt.txt (verbatim U#38, masked)
PROMPT = "帮我查看 v(blasec28<562>) 这个信号线所在的SA中决定了上拉和下拉能力的4个mos管在Netlist网表里是哪四个"
with open(os.path.join(ASSETS, 'prompt.txt'), 'w', encoding='utf-8') as f:
    f.write(PROMPT + "\n")

# task_brief.md (delivery interface + file location only, <=3 lines intent)
BRIEF = """交付：outputs/submit.zip，内含你的 python 脚本（sa_core_mos_locate.py）。
脚本用法：python3 sa_core_mos_locate.py <netlist_sp> <top_signal> -o <out.json>
输出契约：out.json 为 JSON 对象，含字段 top_signal, sa_subckt, sa_instance, bit_index(int), core_mos(数组，每元素含 instance/model/mos_type(NMOS|PMOS)/role(pull_down|pull_up)/side(L|R)/drain/gate/source/body/delvto_param)。脚本须定位顶层信号所在 SA 实例、解析该信号映射到 SA 的哪个 bit，并输出该 bit 决定上拉/下拉的 4 个核心 MOS（2 NMOS 下拉 + 2 PMOS 上拉交叉耦合，带 delvtoBL<k>_NsL/NsR/PsL/PsR 失配参数）。
可见输入：assets/EDA-Eval-DesignFlow-SaCoreMosLocate_001/netlist（A 网表，顶层信号 Blasec28<562>）。判分只跑隐藏 B。
"""
with open(os.path.join(ASSETS, 'task_brief.md'), 'w', encoding='utf-8') as f:
    f.write(BRIEF)

print("WROTE:")
print("  ", os.path.join(ASSETS, 'netlist'))
print("  ", os.path.join(ASSETS, 'prompt.txt'))
print("  ", os.path.join(ASSETS, 'task_brief.md'))
print("  ", os.path.join(HIDDEN, 'B_netlist'))
print("  ", os.path.join(HIDDEN, 'hidden_manifest.json'))
