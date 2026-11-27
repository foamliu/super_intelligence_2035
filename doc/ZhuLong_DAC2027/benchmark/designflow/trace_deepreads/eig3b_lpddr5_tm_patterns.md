# Deep-read: 1794798158521_eig3b — LPDDR5 test-mode calibration pattern authoring

## Trace provenance
- session: `1794798158521_eig3b` (nevinrao @ hfeg0plg103, mc=49, domain=analog_context)
- 337 msgs, 1.7MB; claimed r1614 (shard D, 2026-11-27)
- trace file retrieved from `.snapshot/daily-new.2026-11-26_2230/.cline/data/sessions/1794798158521_eig3b/1794798158521_eig3b.messages.json` (live path moved into per-session subdir; flat path from scan summary no longer exists — known cline format change)
- tools used: editor(61) / read_files(50) / run_approved_command(37) / list_allowed_files(4)

## User real intent (17 user turns)
User (DRAM test engineer) wants verilog **test patterns** for 3 LPDDR5 test-mode calibration registers, written to follow their existing pattern template framework at
`/proj/ddgoa/V0/workdir/qi3wang/sos_manage_lpddr5/lpddr5/ddgoa/patterns/proj_function/cmds_testmode/cmds_datapathtiming/`.

Three sub-tasks (sequential in trace):
1. **TM_CaIbSw** (cm1_io_CaIbSw, C2C switch): default 0. Sw=0 → C2C off when rate<1600Mbps, on when >1600Mbps; Sw=1 → off when <800Mbps, on when >800Mbps. Pattern must verify both switch settings × both rate regimes. User clarified the C2C switch signal is `CaIbsw-CTRL` and `ba =$urandom_range(3)` is acceptable (vs `random_bk()`).
2. **TM_BoostPlusHigh** (cm1_io_BoostPlusHigh<1:0>): boost pulse width adjust. TX=2'b11 → widest; TX=2'b01 → narrowest. Pattern must sweep the 4 TX codes and check pulse-width ordering.
3. **TM_2StepSenseAdj** (cm1_ro_2StepSa): 8-bit sapen. User explicitly: first set `<3>` (cm1_ro_2StepSa bit3), then load TM_2StepSenseAdj; because 8-bit, must set high nibble and low nibble each to 0000–1111 (16 sweeps each) and verify sapen signals map correctly — user checks in waveform, pattern must guarantee the nibble sweeps.

## Deliverable (what user accepted)
Three verilog pattern files written to `/home/nevinrao/`:
- `TM_CaIbSw.v` (5902 chars, final @ msg67) — `task TM_CaIbSw(integer entry_mode=0, integer nnop=0);` with rate-threshold branching + bg/ba/row/col/dq randomization, C2C on/off via CaIbsw-CTRL writes
- `TM_BoostPlusHigh.v` (3318 chars, final @ msg178) — `task TM_BoostPlusHigh(...)`, sweeps TX<1:0> 4 codes, boost pulse-width ordering
- `TM_2StepSenseAdj.v` (1715 chars, final @ msg322) — `task TM_2StepSenseAdj(...)`, sets cm1_ro_2StepSa bit3, then high/low nibble 0000–1111 sweeps on sapen

Assistant's process: wrote helper `search_*.py` scripts (search_c2c / search_boostplus / search_preem / search_cmarya / search_2stepsense) to grep existing pattern corpus for signal/register references → read template patterns → wrote .v files → iterated with user on signal specifics.

## Case synthesis plan (next round)
- **task_id**: `EDA-Eval-DesignFlow-Lpddr5TmPatternProduce-001` (shard D, analog_context)
- **deliverable**: `outputs/submit.zip` containing 3 verilog pattern files (TM_CaIbSw.v / TM_BoostPlusHigh.v / TM_2StepSenseAdj.v)
- **A (visible)**: prompt with real user intent + a small excerpt of the template framework (task signature conventions, register write macros, rate variable) + the 3 register functional descriptions (CaIbSw rate thresholds, BoostPlusHigh TX codes, 2StepSa 8-bit nibble sweep)
- **hidden B**: different rate thresholds (e.g. 1200/600 Mbps) + different TX code→width mapping + different target bit (bit5 instead of bit3) and different nibble width — token-structurally different from A
- **check.py (≥8 conds, only-add)**:
  1. zip has exactly 3 files with expected names
  2. each .v defines `task TM_<Name>(integer entry_mode=0, integer nnop=0);` signature
  3. TM_CaIbSw writes the C2C switch control signal for both Sw=0/Sw=1
  4. TM_CaIbSw has rate-threshold branching matching B's thresholds (anti-hardcode: must use B's numbers not A's)
  5. TM_BoostPlusHigh sweeps all 4 TX<1:0> codes
  6. TM_BoostPlusHigh pulse-width ordering: TX=11 widest, TX=01 narrowest (per B's mapping)
  7. TM_2StepSenseAdj sets the target bit (B's bit, e.g. bit5) before load
  8. TM_2StepSenseAdj sweeps high nibble 0000–1111 AND low nibble 0000–1111 (16 each)
  9. anti-hardcode: A-specific tokens (1600/800, bit3) must NOT appear in B-graded submission
- **真跑候选**: deliverable is verilog pattern source (text), judged by structural parse — no real EDA tool product dependency ⇒ **LIVE-NA** (judge_layers=[L0,L1]); no check_live needed
- **negatives**: empty_shell / print_expected / hardcode_a (A's thresholds) / wrong_order (boost width reversed) / drop_nibble_sweep — all must FAIL distinct conds
- **trace_source**: {user:nevinrao, host:hfeg0plg103, session_file:1794798158521_eig3b, match_count:49, real_task_summary:"写 LPDDR5 test-mode 校准寄存器(CaIbSw C2C / BoostPlusHigh / 2StepSa)的 verilog pattern，按 cmds_datapathtiming 模板框架交付 3 个 .v 文件"}

## Status
- **DEBT: 1 deepread 未合成** — deepread complete r1614, case synthesis deferred to next round (40-min budget exhausted by candidate mining + trace retrieval friction).
- Next round: build assets/hidden/check.py/negative per plan above, self-verify, pi run, mark ledger case.
