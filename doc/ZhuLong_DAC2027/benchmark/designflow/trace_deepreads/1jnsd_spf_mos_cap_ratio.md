# Deepread: 1jnsd — SPF/DSPF Net-Cap vs MOS Gate-Cap Ratio with cox.csv Calibration

## Trace
- session: `1793780117036_1jnsd`, user `stephens`, host `hfeg0pkn002` (10.129.2.11), mc=14
- 123 msgs / 2 user turns, single-produce (clean)
- keyword profile: cmos:105;transistor:82;synopsys:6;calibre:6;mosfet:2;hspice:2;netlist:1
- cox.csv (2279 B, 18 rows) attached in turn 2

## Task (verbatim user turns)
- **U#0**: "如果给你一个spf文件，你能将其中所有的net电容和mos管的电容分别抓出来，各自加在一起，并计算二者的比例吗?"
- **U#9**: "比如这个路径下的spf文件：/proj/ddgoa/V0/simdir/finesim/workdir/stephens/RWAbus288DnW_NNDriver_ddgoa_split_newprc2_0820.spf.TYP_98_RCC"
- **U#120** (with cox.csv): "这个列表为ntn_lvio和ptn_lvio在不同width length 温度 vgs条件下的栅级电容拆解...将所有的N管都按照这里的ntn_lvio的类型进行处理，P管按照ptn_lvio的类型处理，如果出现表中没有的width length则按照0.32/42n的行的size等比计算，其中Cggi这一列为你之前公式中提到的Cox，按照这个表重新计算MOS管电容，并和之前的走线电容做比"

## DSPF format (DSPF 1.3, StarRC)
- Header: `*|DSPF 1.3`, `*|DESIGN <name>`, `*|DIVIDER .`, `*|DELIMITER :`, `**FORMAT SPF`
- Net caps: `*|NET <name> <value>PF` (e.g. `*|NET ECCbnk23_b0<3> 0.00611725PF`)
- MOS device lines (plain SPICE, before `.ENDS`): `<inst> <drain>:DRN <gate>:GATE <src>:SRC <bulk> <model> L=<l>u W=<w>u`
  - e.g. `XI_...XMMP1@10 XI_...XMMP1@10:DRN XI_...XMMP1@10:GATE XI_...XMMP1@10:SRC vbp! ptn L=0.05u W=0.54u`
  - model `ntn`=NMOS, `ptn`=PMOS

## Real file scale
- 344.5 MB / 5,139,242 lines, 12,555 nets, 55,662 MOS (16,618 NMOS / 39,044 PMOS)
- Agent first-pass (default Cox=8.0 fF/μm², Cgg=Cox×W×L×nf): net_cap=39.9078 pF, mos_cap=8.1268 pF, ratio=4.9106

## cox.csv structure (tab-separated, 18 rows)
- Columns: Corner, vgs, temp, w, l, freq, Vg, Cg, Cd, Cb, Technode, Model Version, **(empty)**, Polarity, Device type, Cch, Cgd0, **Cggi**
- NOTE: header has 16 col names but data has 18 fields (extra empty tab between "Model Version" and "Polarity") — column misalignment, must parse robustly
- 9 N rows (ntnlvio): w∈{0.32,0.64,0.96}u × l∈{0.036,0.042,0.048}u
- 9 P rows (ptnlvio): w∈{0.8,1.2,1.6}u × l∈{0.036,0.042,0.048}u
- Cggi = per-(W,L) total gate cap at nf=1 (Farads), e.g. N(0.32u,0.042u)=3.86E-16 F
- Fallback base row: l=0.042u, smallest w → N:(0.32u,0.042u,3.86E-16), P:(0.8u,0.042u,9.44E-16)

## Gold mechanism
1. Parse `*|NET <name> <cap>PF` → net caps (sum = net_total_cap)
2. Parse MOS device lines → (model, W, L, nf); polarity = N if model[0]=='n' else P
3. Cggi lookup: exact (polarity,W,L) in cox table → cap=Cggi×nf; else fallback Cggi_base×(W×L)/(W_base×L_base)×nf
4. mos_total_cap = sum of all device caps; ratio = net_total_cap / mos_total_cap

## B-grade synthesis design (EDA-Eval-DesignFlow-SpfMosCapRatio-001, L2, k=13)
- **Visible A** (`RWAbus_A_drv`): 12 nets + 8 MOS (4N/4P), all W/L exact-match in cox_A.csv
- **Hidden B** (`RWAbus_B_drv`): 15 nets + 14 MOS (7N/7P), 6 off-table W/L fallback cases (W=0.48/0.16/2.4, L=0.084 etc.)
- **Anti-hardcode C** (`RWAbus_C_drv`): 3 nets + 4 MOS (2 fallback), embedded in check.py, never seen by SUT
- A/B/C net names (netA/netB/netC), instance names (XA/XB/XC), design names completely disjoint
- cox_A vs cox_B: different Cggi values (B scaled ~1.3x)
- check.py 13 conditions a-m: forbidden-import/eval/B-literal, py_compile, B-JSON-keys, net_count+per-net-cap, net_total_cap, mos_count+N/P-split, per-device polarity/w/l/nf, **per-device cggi (exact+fallback)**, per-device cap, mos_total_cap, ratio, anti-hardcode C, 3-seed determinism
- Independent oracle: regex-findall (nets) + csv.reader/list-scan (cox) — structurally different from ref's line-iterator+dict

## Dup-check (§5 task-family)
- stephens IS in D.jsonl: VmMhlAlterStats-001 (line 102, FineSim MC VMHL/VMLH min/max CSV stats) — DIFFERENT mechanism (no SPF, no MOS cap, no cox calibration)
- No existing case does net-cap/MOS-gate-cap ratio with cox.csv Cggi lookup + area-scaled fallback
- SpfCapResAnomaly-001 (#509): SPF net cap + resistor segment — different (no MOS cap, no cox)
- NOT a dup ✓

## Self-verify
- ref PASS 13/13 (check.py self-test)
- negative_selftest: ref PASS + 3 neg (empty/print/hardcode_a) all FAIL ✓
- §4.9 three-fake-submit: empty_zip/wrong_name/non_zip all REJECTED ✓
- D.jsonl 319→320, ledger_D 1jnsd claimed→case
