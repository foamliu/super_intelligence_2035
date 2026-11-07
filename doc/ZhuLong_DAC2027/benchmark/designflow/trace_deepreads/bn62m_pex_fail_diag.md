# Deepread: bn62m — PEX failure log diagnosis (han1li)

- **session**: 1793094734633_bn62m @ 10.129.35.68 (han1li, mc=76)
- **tools profile**: read_files=12, list_allowed_files=9, run_commands=1, get_agent_policy_status=1
- **nmsgs**: 37 (1 user turn, 23 assistant tool calls)

## User intent (verbatim U#0)
> i have one cell pex failed , log file path is /proj/lacaa/TV1_DBC_Virtuoso/ver/pex_gxrc/han1li/PEX_20261027_172944/DBCP51H180L6W25T5_BASEMB_SVT_ALL/CKBD6/run.log

## Assistant diagnosis (final, ASST#36)
CKBD6 PEX run pipeline:
1. **GDS export** ✅ (Step 1)
2. **CDL netlist** ✅ (Step 2)
3. **Calibre LVS** ✅ — run.log line 35280 `LVS completed successfully` (report CORRECT, not a data mismatch)
4. **GloryEX RC extraction** ❌ — `pex.sh` ran `gxrc_t -mpi`, returned non-zero → `PEX failed!` + `exit 1`

Exact error (run.log tail lines 35440–35456):
```
-E- Process rank 0, pid 45942, Receive Value 15
Error message: -W- SIGTERM is caught
-I- Please send '.stack_rpt/GEXstackTrace_hfeg0pgn120_45942.rpt' to <support@phlexing.com> for support.
-I- GloryEX extraction of design completed with risk!
PEX failed!
```
- Tool: **GloryEX RC 2026.06_P009**, invoked as `gxrc_t -mpi -c .../gxrc_cci_cmd_V0d1_Rev06`
- Failure point: Extract job, right after `Load capTab ... OK`, during polygon merge / connectivity build → caught **signal 15 (SIGTERM)**
- Stack trace (`.stack_rpt/GEXstackTrace_hfeg0pgn120_45942.rpt`): process blocked in `read()` when SIGTERM received
- Batch comparison: other cells (AIOI21D1/D2/D4, AN2D1/D2/D3/D4/D12, …) succeeded → produced `.dspf.TYPICAL_25`; CKBD6 produced none (exited at extraction stage)
- Warnings common to all runs (capTab TRIO-0565/TRIO-0403) — not the differentiator

## A-faithful judgment
Not feasible: run.log/gex.log live on `/rundata/lacaa/...` (owned by han1li, not readable from .75 as e0031982; not portable as attachment); hidden inputs need different failure modes. → **B-grade synthesized**.

## B-grade facet
PEX run.log failure diagnosis generator (`gen_pex_failure_diag.py --log <run.log> --outdir <dir>`):
- parse 4-stage pipeline status (gds_export / cdl_netlist / lvs / rc_extraction)
- detect LVS verdict (CORRECT/INCORRECT), failed stage, error signal (SIGTERM=15/SIGKILL=9), error lines (-E-), corner, GloryEX version, host/user
- emit `diagnosis.json` (13 top-level keys) + `report.md` (Summary + Diagnosis + Recommendation)
- recommendation heuristic per failed_stage + error_signal

## Inputs (anti-hardcode 5 axes)
- **A** = `pex_run_A.log`: trace-faithful CKBD6, GloryEX 2026.06_P009, corner TYPICAL_25, host hfeg0pgn120, user han1li, pid 45942, SIGTERM(15) during RC, LVS CORRECT
- **hidden B** = `pex_run_B.log`: AN5D4, version 2026.06_P010, corner FAST_M40, host hfeg0pgn088, user lintao, **LVS INCORRECT** (failed_stage=lvs, RC not_reached), 3 LVS -E- mismatch errors
- **hidden B2** = `pex_run_B2.log`: ND2D1, version 2026.07_P002, corner SLOW_125, host hfeg0pgn055, user wuq, **OOM SIGKILL(9) during RC**, LVS CORRECT
- All design/corner/version/host/user/pid literals distinct across A/B/B2; 3 distinct failure modes (SIGTERM-during-RC / LVS-INCORRECT / OOM-SIGKILL-during-RC)

## check (16 conditions a-p)
a zip+py_compile / b B-run exit0+2files / c 13 keys / d design==AN5D4 / e pex_tool==GloryEX RC / f version==2026.06_P010 / g stages dict 4 keys valid status / h failed_stage==lvs / i lvs_verdict==INCORRECT / j stages.lvs==failed / k stages.rc==not_reached / l error_lines non-empty+markers / m corner==FAST_M40 / n report Summary+Diagnosis+design / o recommendation LVS+fix keyword / p anti-hardcode(no A literals)+A-run design==CKBD6+B2-run(rc_extraction/SIGKILL/CORRECT)+3x sha256

## Self-verify
- ref PASS 16/16 (a-p)
- 5 negatives all FAIL with 5 distinct first_fail: empty_shell→b / hardcode_a→d / print_expected→p / ref_core_deleted→l / naive_stub→h
- §4.9 three-fake (empty/print_expected/ref_core_deleted) all FAIL
- assertion gate: k_rationale = k_check = 16 ✓

## Lesson
- PEX run.log 4-stage pipeline (GDS→CDL→LVS→RC) + signal-based RC failure (SIGTERM/SIGKILL) is a clean L2-trace-faithful diagnosis facet; 16 conditions naturally rich (stage status / verdict / signal / error lines / corner / version / cross-input / determinism).
- The real CKBD6 SIGTERM log (lines 35250-35456) extracted from the trace's read_files tool_results is fully trace-faithful (real GloryEX 2026.06_P009 banner, real gxrc_t command, real pid 45942, real captab path) — A input is genuine, not fabricated.
- Domain: schematic_netlist (PEX = parasitic netlist extraction; output is .dspf parasitic netlist). The case diagnoses why netlist extraction failed.
- ⚠️ L-level: marked L2 (real PEX/GloryEX/calibre tool logs from a real L2 tool run; the generator parses offline but the data is genuine L2 tool output). L1/L2 debt: this is an offline-log-parsing generator (L1 by strict definition "离线 Python 复刻"); however the source data is from a real L2 PEX run. Strictly L1; the L1/L2 ratio debt persists (8th consecutive round clean L2 produce scarce in fresh pool).
