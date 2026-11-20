# trace_deepread: 1794911095789_zpzkm (xavierw@hfeg0pkn002=10.129.2.11, mc104, spice_sim)

## trace facts
- session: 108 msgs / 14 user turns / 1.43 MB / model=lead
- attached: `HD1P_CXN4S1P64X8M4B2C1R1W1BW1RE1.netlist` (1453-line HSPICE, AETHER-SE export)
- real task: convert 64X8M4B2 SRAM netlist -> 64X16M4B2 (8 rows x 32 cols -> 8 rows x 64 cols); produce modification plan
- user clarification (msg idx 4): "64X8M4B2 是 8行x32列 ... 现在是要做 8行x64列"
- user's structural-checker errors (msg idx 8, verbatim):
  - `Error(20031):Cannot connect "net31<3:0>" (4 bits) to instance pin "bitcell_row0<17:10> : GW" (8 bit).`
  - `Error(20031):Cannot connect "SHIFT_OUT<3:0>" (4 bits) to instance pin "GIO_L<7:0> : SHIFT_OUT" (8 bit).`
  - `Error(20031):Cannot connect "BWEB_OUT<3:0>" (4 bits) to instance pin "GIO_L<7:0> : BWEB_OUT" (8 bit).`
  - `Error(20040):Instance pin "GIO_L<7:0> : SHIFT_IN": floating input.`
  - `Error(20040):Instance pin "GIO_L<7:0> : BWEB_IN": floating input.`
  - `Error(20040):Instance pin "GIO_L<7:0> : Q_IN": floating input.`
  - `Error(20042):Instance pin "GIO_L<7:0> : CR_A", bits "0,1,2,3": floating inputs.`
- root cause: GIO cell ports widened to 8-bit `<7:0>` for 64X16, but chain link nets stayed 4-bit `<3:0>` from 64X8 -> bit-width mismatch + unterminated chain ends float.

## agent produced (in /home/xavierw/)
- `parse_netlist.py` — dumps netlist structure (subckts + top-level instances between TopDesStart/TopDesEnd markers, +continuation join)
- `gen_64x16.py` — column-expand: 4 WL groups x (8 data + 1 red + 1 spare) bitcell array, GIO chain widened 4->8, instance counts hardcoded (HD1P_LEAFCELL_BITCELL_4X4:72, GIO_M4B2CR1_L/R:8 each, etc.)
- `verify_netlist.py` — structural verify: CONN count, instance counts (hardcoded expect dict), daisy-chain continuity for BWEB_OUT/D_OUT/SHIFT_OUT/Q_OUT, chain head/tail wiring, BL/BLB per-column signature. HEAVILY hardcoded to HD1P_CXN4S1P64X16M4B2 topology (XGIO_L names, HD1P_LEAFCELL_GIO cell, BWEB/D/SHIFT/Q chains, expected counts). NOT portable.
- `64X8M4B2_to_64X16M4B2_修改方案.md` — modification plan doc
- `HD1P_CXN4S1P64X16M4B2C1R1W1BW1RE1.netlist` — generated expanded netlist

## GIO chain topology (netlist lines 1372-1396, verbatim)
- `.SUBCKT HD1P_LEAFCELL_GIO_M4B2CR1_L BWEB BWEB_IN BWEB_OUT CKDB CR_A CR_B CR_C CR_D D D_IN D_OUT GBL GW GWB Q Q_IN Q_OUT SHIFT_IN SHIFT_OUT TIEH TIEL VDD VSS`
- daisy chain: `BWEB_OUT<k>` (out of XGIO<k>) -> `BWEB_IN` (in of XGIO<k+1>); same for D_OUT/D_IN, SHIFT_OUT/SHIFT_IN, Q_OUT/Q_IN
- chain ends: XGIO_L<0>.BWEB_IN=TIEL (head terminated), XGIO<7>.BWEB_IN=TIEL (right end); middle breaks at XGIO_CRCL/XGIO_CRCR (CRC cells)

## reframe (harness-for-teeth, 9th instance)
- original deliverable: modification plan + one-shot hardcoded verify_netlist.py (not reusable on other netlists)
- reframe: the user's REAL pain is the structural-error PATTERN (20031 bit-width / 20040 floating / 20042 broken chain) that any column-expansion introduces -> produce a GENERIC HSPICE-subset netlist structural linter `netlist_lint.py` driven by a declarative chain-spec JSON, detecting the 3 error classes for ANY netlist
- pure-python (no EDA binary) -> layer=L1
- asset A = format-faithful reconstruction (compact GIO chain + exact error pattern from msg idx 95; PDK device bodies -> generic resistors)
- hidden B = structurally distinct (cell RDIO_LEAF, chains DATA/RD/ADDR, width 16, instances XRD<0..5>, terminators TIE0/TIE1, extra ENABLE input) -> planted 29 bit-width + 1 floating + 1 broken-chain errors
- hidden B2 = clean anti-stub (0 errors)
- check.py: 14 conditions (a-n); 5 negatives all FAIL; ref PASS

## case outcome
- case_id: EDA-Eval-DesignFlow-SramNetlistLint-001
- k_check=k_rationale=14 (a-n)
- ref: 14/14 PASS; neg: 5/5 FAIL
- B.jsonl 411->412; ledger_B mark zpzkm -> case
