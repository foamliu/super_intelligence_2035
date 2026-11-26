# 87wu6 — WTM is4phase Misuse Check (deepread)

## Trace metadata
- session: 1792654922770_87wu6
- user: tongfanl
- host: 10.129.2.13
- match_count: 28
- domain: verification (shard A)
- trace size: 247KB / 17 msgs / 3 user-text turns
- trace path: /home/tongfanl/.cline/data/sessions/1792654922770_87wu6/1792654922770_87wu6.messages.json
- agent: failed (user said "retry" / "？", agent never delivered diagnosis)

## User intent (verbatim MSG 0)
「帮我检查下/home/tongfanl/DDR6/DSCQA/analogsim/WTM中的124三个pattern，其中is4phase有没有用错或者其它问题。抽激励的环境在：/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen」

= 检查型 analysis-Q&A: verify is4phase usage correctness in WTM patterns 1,2,4 (WTM001/002/004).

## Files examined (from 10.129.2.13 via ssh, e0031982 identity)
- WTM001_normal_check.v (786 lines) — normal check pattern
- WTM002_normal_check.v (812 lines) — normal check, LFSR->Userdefine, 4-phase header
- WTM004_block_check.v (780 lines) — block check pattern
- vecgen env (/proj/dscqa/...): Permission denied (not accessible, but not needed for diagnosis)

## Root cause (correct diagnosis, determined from pattern files)
**is4phase inversion bug in Load_Mode op[1]**: All 3 patterns use `!is4phase` for the phase-select bit (op[1]) in the active Load_Mode call, while the downstream stimulus generation uses `if(is4phase)` directly (not inverted).

- is4phase semantics: 0=2-phase, 1=4-phase (per $display L258/L284/L252)
- op[1] semantics: 0=even/odd (2-phase), 1=4-phase (per WTM002 L69 comment: "op[1]=0:even/odd;op[1]=1:4-phase")
- Active Load_Mode: op[1] = !is4phase → INVERTED
- Stimulus generation: if(is4phase) → direct (NOT inverted)
- Result: DUT configured for OPPOSITE phase to stimulus
  - is4phase=1 (4-phase) → op[1]=0 → DUT 2-phase, stimulus 4-phase → MISMATCH
  - is4phase=0 (2-phase) → op[1]=1 → DUT 4-phase, stimulus 2-phase → MISMATCH
- Commented-out old code uses `is4phase` (correct, no inversion): WTM001 L75/L79, WTM002 L75, WTM004 L66
- Fix: change `!is4phase` to `is4phase` in Load_Mode op[1]

Evidence lines:
- WTM001: active L71 `!is4phase`, commented L75/L79 `is4phase`, stimulus L129 `if(is4phase)`
- WTM002: active L69-70 `!is4phase` (2 calls), commented L75 `is4phase`, stimulus L126 `if(is4phase)`
- WTM004: active L62 `!is4phase`, commented L66 `is4phase`, stimulus L123 `if(is4phase)`

## Case synthesis
- case_id: EDA-Eval-DesignFlow-WtmIs4PhaseMisuseCheck-001
- type: C-A analysis-Q&A / 检查型 (check/audit)
- domain: verification
- delivery: wtm_is4phase_check_report.json (in outputs/submit.zip)
- A files: 3 (WTM001/002/004 key is4phase regions, line-numbered, asset_fidelity=original)
- B variant: is_4ph / 8'hDD / op[2] / WTM101/103/105 / default 1'b0 / different line numbers (8 anti-hardcode dims)
- check: 15 conditions (a-o), k_check=k_rationale=15>=8
- self-verify: ref 15/15 ALL PASS + 5 negs ALL FAIL distinct + 3 §4.9 fakes ALL FAIL
- ledger: 87wu6 parked→case
- parked_reaudit: 87wu6→done_r650

## Note on infra
- eda_flow open_session works with dummy task_id/eval_id (e0031982 on hfhds201=.75)
- ssh免密 to remote hosts works from .75 (e0031982 identity)
- All 10 "11 可造" candidates from r648 reaudit have EXISTING traces (dir format: <id>/<id>.messages.json), not NOFILE — r648's "NOFILE" was a path error (checked flat instead of dir format)
- k7668 (FfModReplace-001, r572), mt7ua (GenLefConsistAudit-001, r564), l8ljo (SdfNegLimitDiagnose-001, r649) already landed — r648 reaudit was stale (didn't check ledger)
