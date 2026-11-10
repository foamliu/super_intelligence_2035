# zxb65 — MBIST repair re-injection diagnosis (thomas1w@hfeg0pjn100, mc=133, verification)

## Trace
- session: `/home/thomas1w/.cline/data/sessions/1793972832447_zxb65/1793972832447_zxb65.messages.json` (975KB, 177 msgs)
- user turns (7): USER#1/#2 = syntax-error locate (irun.log → find语法错); USER#3 = **clean A-faithful diagnosis**; USER#4/#5 = write fix to separate file + diff; USER#6/#7 = root-cause mechanism deep-dive.

## USER#3 verbatim (the diagnosis task)
> /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/patterns/proj_function/cmds_ppr/mbistmppr.v，我在测试的时候，加上了宏DOUBLE_REPAIR，我的本意是想使用相同的错误地址，运行两次mbist和mppr，但是现在的代码，在运行第二次的mbist的时候没有注错了，麻烦看下为什么

User describes intended behavior (run mbist+mppr twice with same error address via DOUBLE_REPAIR macro) vs actual (2nd mbist has no fault injection), asks why — does NOT name the root cause. ✓ A-faithful diagnosis.

## Agent's root cause (idx 140)
- `errforcebit` is the injection-enable control var (consumed in `proj_special_modify.sv:692-693`): `errforcebit == -1` (also -2005/-1002) → `errforceiocnt=0` → no injection; any other value (e.g. -100) → injection enabled (random single-bit error).
- `A_Pattern_Sim.v:35` sets `errforcebit = -100` (enabled) before the first mbist → 1st mbist injects correctly.
- After 1st mbist completes (`mBistDoneFlag` raised), `mbistmppr.v:482` sets `errforcebit = -1` (to allow clean MR112-115 error-count reads without injected data interfering).
- `DOUBLE_REPAIR` macro only changes `repeat_num = 2`, making `repeat(repeat_num) begin` loop run twice. After line 482 sets `errforcebit=-1`, NOTHING re-enables it before the 2nd iteration's mbist → 2nd mbist sees `errforcebit=-1` (disabled) → no injection.
- **Root cause class**: `injection_not_re_armed_between_loop_iterations`.

## Gold fix (idx 140/154)
- Insert `\`TOPHIENAME.A_proj_monitors_if.tbctrlmonitors.errforcebit = -100;` right after `repeat(repeat_num) begin` (before the mbist `Load_Mode` at line 465), so each iteration re-enables injection.
- KEEP line 482's `errforcebit = -1` (needed for clean MR112-115 reads).
- Agent wrote `mbistmppr_fixed.v` + `mbistmppr_fixed.diff` to `/home/thomas1w/` (source `/proj/...` read-only).

## USER#6/#7 follow-up
- USER#6: "之前为啥不注错，为啥加了 errforcebit=-100 就可以注错了" → agent explained the errforcebit sentinel semantics (idx 156).
- USER#7: challenged — "mbist是否注错不是靠 hdl_mbist_Ca_QForce 这段代码么" → agent (idx 158) refined: precise injection IS dynamically controlled by `hdl_mbist_Ca_QForce` address-match logic, not just static -100. But the core re-arm diagnosis stands (the disable/enable lifecycle is the bug).

## Case design (diagnosis-generator reframe, matches SvHierRefDiag-001/RhrQueueBoundsDiag-001)
- deliverable = `gen_mbist_repair_diag.py` (stdlib generator) + `spec_a.json`
- generator emits `diag_mbist_repair.py` which reads spec.json + structured codebase (injection_control_vars / injection_enable_points / run_loops / injection_disable_points / read_clean_points / macro_guards / re_enable_scan / user_constraints) and STATICALLY DERIVES:
  1. injection control var (name) + disable sentinels + enable value example (from consumption)
  2. run loop (repeat construct) + iteration count (macro_guard → loop_var value)
  3. disable point (after done-flag, sets var to disable sentinel) + reason (clean MR reads)
  4. re-enable scan (found=False; no assignment between disable point and next iteration)
  5. root-cause class: `injection_not_re_armed_between_loop_iterations`
  6. fix: `re_enable_injection_at_loop_body_start` + target (loop body start) + fix_code (re-assign var to enable value) + keep_disable_rationale + why_no_re_enable
  7. user constraints recognized
  → outputs `root_cause.json` (30 fields) + `diag_report.md`
- A=spec_a faithful (thomas1w/mbistmppr.v/DOUBLE_REPAIR/errforcebit/-1/-100/repeat_num=2/line482/A_Pattern_Sim.v:35/proj_special_modify.sv:692-693/mBistDoneFlag/MR112-115)
- hidden B=spec_b isomorphic (inj_enable/bist_repair_pair.v/REPAIR_TWICE/bistDoneFlag/tb_monitors.sv:510-511/B_Pattern_Sim.v:42/-999/-50/loop_count=2/line512/MR224-227)
- check.py 16 conds a-p (independent recompute). Self-verify: gold PASS 16/16 + 6 negatives (noop/fake_print_a/fake_core/hardcode_a/stub_unclassified/core_deleted) ALL FAIL NEG_RC=0. §4.9 (a)(b)(c) covered.
- k_rationale = k_check = 16 ≥ 8 ✓. test_sha8 = 6284d9b5. A.jsonl 199→200. ledger zxb65→case (verification 46→47).
