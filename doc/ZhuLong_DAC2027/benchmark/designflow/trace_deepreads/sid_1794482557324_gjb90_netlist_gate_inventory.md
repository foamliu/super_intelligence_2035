# Deepread · gjb90 · netlist gate inventory

- **trace_source**: user=hairuizh, host=10.129.2.10 (hfeg0pkn002 via /proj), session=1794482557324_gjb90, mc=95, keywords=cmos:484;netlist:325;lvs:215;schematic:136;transistor:23;hspice:...
- **domain**: schematic_netlist
- **NMSG**: 101, NTURNS(user)=1 (single clean produce-task)
- **U0 (verbatim, key part)**: 「统计网表中使用到的所有逻辑gate，@/proj/.../drvqa_cmos_core_lwdrq_msaq_schematic_ALPS/netlist，交付文件为同文件夹下的gates.csv 要求：1.只允许查看该文件夹 2.每种名称的门只统计一次，且取最小尺寸，如：invSx1 invSx2，只取invSx1 3.输出格式: 类型(inv/nand等),Cell名,lib(会写在门定义之前),MOS信息,电压域。MOS信息格式: ptn/3u/100n/1 & ntn/3u/100n/1; ptn是MOS名,3u=width,100n=length,1=nf。含>2个MOS的gate,成对记录PMOS & NMOS,中间以|隔开」
- **ask_question [40]**: 用户确认按 cell 基础名去重（同类型+家族+后缀去尺寸，如 invGSx1/2/4_CoM→invGSx1_CoM；不同家族/电压域各占一行）。

## Assistant tool chain
list_allowed_files → read netlist.presim (symlink) → analyze1-6.py (parse 159 subckts, identify GATE_LIBS=drvqa_cmos_stdcells/drvqa_cmos_digital/stdcells_ac, 45 gate cells all used) → inspect TECHLIB primitives + voltage rails → gen_gates.py/gen2.py (editor 6KB limit + line-shift corruption 多轮) → gen3.py (compact clean) → debug MOS model index (t[6]→t[5] fix) → rows=31, MOS信息 populated → gates.csv written.

## Real netlist format (exact, from trace dump)
**TECHLIB primitive** (parametrized, MOS use param refs):
```
* Library: TECHLIB
.SUBCKT invGS A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss WN=1.06u LN=156n nfN=1 WP=2.12u LP=156n nfP=1
XMM0 Y A inh_vss inh_vbulkn ntn w='WN' l='LN' nf='nfN'
XMM1 Y A inh_vcc inh_vbulkp ptn w='WP' l='LP' nf='nfP'
cg1 A 0 c='Cthin*(nfN+nfP)'
cout1 Y 0 c='CapO*(nfN+nfP)'
.ENDS invGS
```
- MOS line = `X<name> <d> <g> <s> <b> <model> w='<param>' l='<param>' nf='<param>'` (4 nodes, model at t[5], params at t[6:])
- dev() matches `^X\S+\s` lines containing `w=`; model=t[5]; w/l/nf from `^([wl]|nf)='?(.+?)'?$`

**Gate cell** (concrete, X-instance of TECHLIB primitive with scientific-notation params):
```
* Library: drvqa_cmos_stdcells
.SUBCKT invGSx1_CoM A Y inh_vbn inh_vbp inh_vcc inh_vss
XI0 A Y inh_vbn inh_vbp inh_vcc inh_vss invGS WN=150e-9 LN=46e-9 nfN=1 WP=270e-9 LP=46e-9 nfP=1
.ENDS invGSx1_CoM
```
- instance params in **scientific notation** (150e-9, 46e-9, 1) → val()=float() parses ✓
- expand(): p from instance (keys uppercased WN/LN/NFN/WP/LP/NFP); primitive MOS w='WN' → r('WN')=val(p['WN'])=float('150e-9')=1.5e-7 → fm=150n
- vdom(): scan cell body tokens for `^inh_(vcc|vwlp|vdleq|vpcsg|...)$` → inh_vcc→VCC, inh_vwlp→VWLP; inh_vbn/inh_vbp NOT in regex (excluded); multiple → sorted UPPER joined by /

**Multi-input gate (nor2GS, 4 MOS = 2 pairs)**:
```
.SUBCKT nor2GS A B Y inh_vbulkn inh_vbulkp inh_vcc inh_vss WN1=.. LN1=.. nfN1=.. WP1=.. LP1=.. nfP1=..
XMM2 Y B inh_vss inh_vbulkn ntn w='WN1' l='LN1' nf='nfN1'
XMM3 Y A inh_vss inh_vbulkn ntn w='WN1' l='LN1' nf='nfN1'
XMM0 zp1 B inh_vcc inh_vbulkp ptn w='WP1' l='LP1' nf='nfP1'
XMM1 Y A zp1 inh_vbulkp ptn w='WP1' l='LP1' nf='nfP1'
.ENDS
```
- gather() returns devices in file order; mos() splits P=[ptn,ptn] N=[ntn,ntn], pairs by index → "ptn/W/L/nf & ntn/W/L/nf | ptn/W/L/nf & ntn/W/L/nf"
- aoi21 (6 MOS=3 pairs): WP1/WP2/WP3 + WN1/WN2/WN3

**fm()** : w>=1e-6→"%gu"%(w*1e6); w>=1e-9→"%gn"%(w*1e9); else "%g". fmnf: int if integer else %g.
**Output rows=31** (real), sorted by (type, name). Header: 类型,Cell名,lib,MOS信息,电压域

## Real output sample [95]
- aoi21GSx1_CoM → 'ptn/540n/46n/1 & ntn/150n/46n/1 | ptn/540n/46n/1 & ntn/300n/46n/1 | ptn/540n/46n/1 & ntn/300n/46n/1', VCC
- invGSx1_CoM → 'ptn/270n/46n/1 & ntn/150n/46n/1', VCC
- invYLVx2_SaCtrol → 'ptk_lv/540n/124n/1 & ntk_lv/300n/151n/1', VWLP

## Synthesis plan (case_id EDA-Eval-DesignFlow-NetlistGateInventory-001)
**SUT produces**: gen_gates.py (CLI `python3 gen_gates.py <netlist> <out_csv>`) — parse SPICE netlist, identify logic-gate cells in GATE_LIBS, dedup by base-name (min size), flatten MOS via TECHLIB primitive param-override, resolve voltage domain, output CSV (类型,Cell名,lib,MOS信息,电压域).
**visible A** = sample_A.sp (TECHLIB invGS/invLVS/nand2GS/nor2GS/aoi21GS + GATE_LIBS cells with size variants x1/x2/x4 across VCC/VWLP + decoy non-gate lib + top instantiation)
**hidden B** = sample_B.sp (different families CS/LV, nand3/nor3/oai21, voltage VDLEQ, different sizes/values, anti-hardcode)
**hidden C** = sample_C.sp (different again, voltage VPCSG, mx2/nor2/aoi21, anti-hardcode)
**check.py 16 cond a-p**: zip valid+py_compile / no A-hardcode / B run exit0+csv / header / rowcount==oracle_B / (type,cell) multiset==oracle / specific gate MOS==oracle (param-override) / multi-MOS | pairing / voltage domain / dedup min-size (x1 not x2/x4) / TECHLIB excluded / non-GATE-lib excluded / C cross-input (type,cell)==oracle_C / C MOS==oracle_C / C voltage has domain not in B / robustness empty-GATE-lib 0 rows.
**negatives**: empty_shell / print_only(hardcode A rows) / hardcode_a / core_removed(no MOS flatten).
**k_rationale=k_check=16**.
**distinct subclass**: netlist-gate-inventory + MOS-flatten + base-name-dedup (vs r620 hierarchy-extract, r622 text-transform, r626 coupling-cap-extract — all orthogonal).
