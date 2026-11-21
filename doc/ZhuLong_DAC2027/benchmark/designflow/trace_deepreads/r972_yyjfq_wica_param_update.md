# r972 deepread: yyjfq — WICA MR15 WPre Parameter Update Script

**Session**: 1794997341095_yyjfq (devonma @ hfeg0pkn004, mc54)
**Trace size**: 606KB / 82 msgs
**Scan source**: ssh_eda_search_20261121_151844/summary.tsv (r940 POOL_SWITCH)
**Domain**: digital (verilog:164 dominant; analog:94 from analogsim paths, not analog design)

## User Intents (4 distinct in session)

| msg# | Intent | Type |
|------|--------|------|
| #0 | Expand sim.saved.shmoov — shmoo V 0.92→1.23V step 0.06V, keep PVT PT fixed | produce-task (shmoov expansion) |
| **#1** | **Write script to update AddressParameter.v.bk lines 144-212 from wica_spf.txt** (TT/SS→0.92V, FF→1.23V, WPre_4s2t→WPre6, WPre_4s4t→WPre8) | **produce-task (script gen) ← SELECTED** |
| #32 | Add 4800 speed parameter (follow-up to #1) | follow-up |
| #44-46 | Wrap `bmatrix -np 128 -r | grep | bkill` into standalone script with user keyword + OR logic | produce-task (shell script) |
| #60 | Optimize kill script — sim status change causes premature exit | debug/fix |
| #76 | Change all Chinese to English in kill script | refactor |

## Selected: msg#1 — AddressParameter.v.bk Update Script

**User verbatim**:
> "写个脚本，按照/home/devonma/coverage/DDR6/DSCQA/sim_setup/Normalsim/wica_spf.txt中的值更新/home/devonma/coverage/DDR6/DSCQA/analogsim/Include/AddressParameter.v.bk第144到212行对应speed和WPre的值，其中TT/SS取0.92v，FF取1.23V的值，WPre_4s2t对应WPre6 ，WPre_4s4t对应WPre8"

## Data Structures

### wica_spf.txt (CSV, 2 sections)
- Section 1 header: `WPre_4s2t,TM,Comp,400,800,1067,1600,2133,2666,2750,3200,3750,4267,4800,5500,6400,7500,8000,9600,10400,10667,11600,12800,14400`
- 23 speed columns (400-14400)
- PVT rows: TT/TF/TS/FT/FF/FS/SS/SF × voltages (0.9V-1.45V)
- Blank separator rows between sections
- Section 2 header: `WPre_4s4t,TM,Comp,...` (same speeds, different values)

### AddressParameter.v.bk lines 144-212 (60 params)
- 10 speed groups: 19200, 16400, 14400, 12800, 11600, 10400, 9600, 9200, 8000, 6400
- Each group: 6 params (WPre6_FF/TT/SS + WPre8_FF/TT/SS)
- Format: `parameter bit[7:0] WICA_MR15_<SPEED>_WPre<P>_<CORNER> = 8'b0000_0000;`
- All initialized to zero; need updating from wica_spf.txt

## Transformation Rule (from user intent)

1. **Section mapping**: WPre6 → WPre_4s2t section, WPre8 → WPre_4s4t section
2. **Corner → row**: FF → FF1.23V, TT → TT0.92V, SS → SS0.92V
3. **Speed → column**: exact match if in wica; else nearest by absolute difference
   - Trace examples: 19200→14400 (not in wica), 16400→14400, 9200→9600
4. **Value → binary**: integer → `8'b<high_nibble>_<low_nibble>` (e.g., 11→8'b0000_1011)

## Assistant's Solution (trace msg#6)

- Created `expand_shmoov_and_update_wica.py` (handled both U#0 shmoov + U#1 wica update)
- Parsed wica_spf.txt into two sections
- Regex matched WICA_MR15 param lines, extracted SPEED/WPre/CORNER
- Mapped to section + row + column, converted value to binary
- **Bug found & fixed**: `8'b8'b` duplication (regex captured `= 8'b` in prefix, then value_to_binstr also added `8'b`)
- Iterated through msg#6-#31 to verify correctness
- U#32 follow-up: added 4800 speed params manually

## Case Design

- **A fixture** (visible, trace-faithful): wica_spf_A.txt (full PVT table from trace) + AddressParameter_A.v (10 speed groups, 60 params, all zeros)
- **Hidden B** (structurally different): wica_spf_B.txt (15 speeds 500-14000, different PVT values) + AddressParameter_B.v (8 speed groups: 14000/12000/10000/8200/7000/5300/4200/3000, 48 params)
  - 3 speeds test nearest-match: 8200→8000, 5300→5000, 4200→4000
  - 5 speeds exact: 14000, 12000, 10000, 7000, 3000
- **Reference**: update_wica_params_ref.py (regex-based, 3-arg CLI)
- **check.py**: 18 independent assertions (a-r)
- **Negatives**: empty shell, print-only (hardcoded A values), core-deleted (verbatim copy)

## Self-Verification Results

- ref on A: Updated 60 parameters ✓
- ref on B: Updated 48 parameters ✓
- check.py on ref: ALL CHECKS PASSED (18/18) ✓
- negative_selftest: ref PASS + 3/3 negatives FAIL ✓
