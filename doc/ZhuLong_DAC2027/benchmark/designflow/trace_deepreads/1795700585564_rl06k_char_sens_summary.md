# Deepread: 1795700585564_rl06k — MOS Characterization Summary with Sensitivity

**Session**: 1795700585564_rl06k  
**User**: ericwang @ hfeg0plg53  
**Agent**: lead (440 msgs, 28 real user inputs)  
**Keywords**: hspice:1506, pdk:571, mosfet:174, netlist:43, lvs:28, pex:18, synopsys:114  
**Date**: 2026-11-27 21:34 ~ 2026-11-28 22:35  

## User Intent

ericwang is a PDK characterization engineer running MOS transistor characterization
for foundry processes (HL22 = HLMC 22nm, V2B = another process). The session is a
continuation of prior work ("继续执行"). The core workflow:

1. User has reference HSPICE .sp deck files in `/home/ericwang/Desktop/Zhulong_1128_MOS/Ref/`
2. User wants to simulate MOS devices (nrvt/prvt/nhvt/phvt/nlvt/plvt/nuhvt/puhvt/nehvt/pehvt/nulvt/pulvt for HL22; ntk/ntk_lv/ptk_lv/ntk_s/ptk_s/ntk_sv3/ntk_sv4/ptk_sv for V2B) across corners (TT/SS/FF/FS/SF) and temperatures (-40/25/98/110/130°C), with specific W/L sizes
3. Extract characterization metrics: Vtgm (Vth from gm), Vtlin (Vth linear), Vtsat (Vth saturation), Idlin (Ids linear), Idsat (Ids saturation), Ioff (off current), DIBL
4. Compute Sensitivity (SS corner deviation from TT, normalized)
5. Output a Summary table with specific columns

## Key Deliverables (assistant produced)

- `gen_batch1.py` — HSPICE deck generator for batch1 devices
- `run_batch1_all.py` — batch runner: generates decks, runs HSPICE, parses .mt0/.lis, extracts metrics
- `gen_hl22_full_summary.py` — the final summary generator (most-edited, msg 296-362): reads pre-computed batch data CSV, generates summary CSV with DIBL + sensitivity
- `compare_ref.py` — compares output against reference CSV

## Core Gotcha (user-caught bug, msg #24 + msg #362)

**Id sensitivity is a RATIO (%, normalized by TT), Vt sensitivity is ABSOLUTE (V).**

User msg #24: "Id相关的还需要处以TT corner下的本身，是算比例"  
(Id-related needs to be divided by TT corner itself, it's a ratio)

User msg #22: "sensitivity仅仅需填写在TT corner所在的行（只用计算SS相比TT的变化），其他corner不用填写"  
(Sensitivity only filled in TT corner rows, only compute SS vs TT change, other corners don't fill)

The assistant initially computed Id sensitivity as absolute (like Vt): `(SS - TT) / sigma`.
The user corrected: Id sensitivity should be `((SS - TT) / TT) / sigma × 100` (ratio in %).
The msg #362 edit changed Idlin_S/Idsat_S/Ioff_S column units from (uA/um) to (%/sig).

## Other Key Details

1. **Physical vs Drawing size**: HL22 thin V0d12 needs drawing × 0.855 = physical (shrink factor). Id normalized by physical W. (msg #26: "HL22 thin V0d12 中，你写的都是drawing size, physical需要乘以0.855")
2. **Sigma per model**: HL22 SS = 3-sigma (msg #22: "HL这个model ss 是3sigma"). V2B might use 2.2.
3. **DIBL** = Vtlin - Vtsat (drain-induced barrier lowering, linear Vth minus saturation Vth)
4. **Sensitivity reference temp**: Uses a fixed reference temperature (98°C for HL22), not the current row's temp
5. **Sensitivity only in TT rows**: SS/FF/FS/SF rows leave sensitivity blank
6. **Sigma per corner**: SS=+sigma, FF=-sigma, TT=0

## Portability Assessment

**Original deliverable** depends on:
- HSPICE simulator (real .sp decks + .mt0/.lis parsing)
- Project-specific PDK models (HL22 at /apps/imctf/extpdk/HL22/..., V2B)
- Reference .sp files (user-private)
- Pre-computed batch data CSV (from HSPICE runs)

**Portable abstraction** = pure-Python summary generator:
- Input: pre-computed batch_data.csv (raw metrics per device/corner/temp/size) + spec.json (config)
- Output: summary.csv (31 columns: physical W/L + DIBL + Vt sens absolute + Id sens ratio) + report.json
- No HSPICE/PDK/display dependency
- The core algorithm (sensitivity computation with ratio/absolute distinction) is the judgeable "有牙" part

## Case Design

**Case**: EDA-Eval-DesignFlow-CharSensSummaryGen-001 (characterization, L1 judge-run, LIVE-NA)

**Candidate**: `char_summary.py <batch_data.csv> <spec.json> <out_dir>`
- Reads batch_data.csv + spec.json
- Computes: physical W/L = drawn × shrink, DIBL = Vtlin - Vtsat
- Sensitivity (only TT rows): Vt sens = (SS-TT)/sigma (absolute V), Id sens = ((SS-TT)/TT)/sigma×100 (ratio %/sig)
- Outputs: summary.csv (31 cols) + report.json

**A/B inputs (token-structurally disjoint)**:
- A: ProcA v1.0, na_rvt/pa_rvt, vdd=0.8, shrink=0.855, sigma=3, ref_temp=98.0, 3 sizes, 3 corners, 3 temps (54 rows)
- B: ProcB v2.0, nb_tk/pb_tk, vdd=1.2, shrink=1.0, sigma=2.2, ref_temp=25.0, 2 sizes, 3 corners, 3 temps (36 rows)

**15 assertions (a,b,sa static + c..n L1)**:
- a: zip top-level char_summary.py
- b: py_compile
- sa: source has csv.DictReader + json.load + sensitivity markers
- c: B runs, produces summary.csv + report.json
- d: B header 31 columns
- e: B total_rows == 36
- f: B DIBL == Vtlin - Vtsat
- g: B sensitivity only TT rows (SS/FF blank)
- h: B Vt sensitivity absolute (V) [GOTCHA]
- i: B Id sensitivity ratio (%/sig) [GOTCHA, neg]
- j: B physical W/L == drawn × shrink
- k: B sigma per corner (SS=2.2, FF=-2.2, TT=0)
- l: cross-input A (54 rows + sigma=3) [neg]
- m: determinism (B2 md5 match)
- n: anti-hardcode (no A-only literals) [neg]

**§4.9 negatives 4 (first-fail distinct)**:
- naive_empty (syntax error) → b
- naive_print_expected (canned output, no real sens) → h
- naive_id_absolute (Id sens absolute instead of ratio — THE GOTCHA) → i
- naive_hardcode_a (hardcoded A values) → sa

**Self-verify**: ref 15/15 PASS; negative_selftest ALL_FAIL + TRIO_DISTINCT (b/h/i) + HARDCODE_FAIL; SKIP_RUN framework accepts (B.jsonl 611 case, infra_fail=0, workdir clean, no-leak).

**judge_layers**: [L0, L1] (LIVE-NA — pure Python data transformation, no EDA simulator dependency)
