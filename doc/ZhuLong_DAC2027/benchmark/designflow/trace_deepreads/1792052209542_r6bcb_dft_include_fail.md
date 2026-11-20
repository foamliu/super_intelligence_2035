# Deepread: 1792052209542_r6bcb — dft_table.v include failure (DDR6 vecgen)

- **session**: 1792052209542_r6bcb
- **user**: tongfanl  | **host**: hfhds201 (= .75, readable directly)  | **mc**: 60
- **domain**: digital / verification (verilog:560 dominant; xrun/xmvlog compile)
- **scan**: ssh_eda_search_20261120_145529/summary.tsv
- **trace file**: /home/tongfanl/.cline/data/sessions/1792052209542_r6bcb/1792052209542_r6bcb.messages.json (268 KB, 29 msgs)
- **fresh**: NOT in trace_ledger_A.tsv (checked against 696 touched sids) — eligible to claim
- **deepread by**: shard A r876 (2026-11-21), under BLOCKER round (see bottom)

## User real intent (msg #0, user_input mode=act)
User pasted terminal output from running `./runsti/gen_stimulus_ltf` in
`/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local`.
3 xrun/vector-gen jobs were submitted; 2 passed, 1 failed. The failure is a
Verilog compile error:
```
xmvlog: *E,COFILX (dft_tasks.sv,1363|74): cannot open include file
        '/proj/dscqa/V0/sim/verilog/ddr6_tb/dscqa/Project/dft_table.v'
```
Intent = diagnose why one vecgen run failed (missing dft_table.v include) and fix it.

## Assistant tool chain (29 msgs, ends mid-diagnosis)
1. get_agent_policy_status + list_allowed_files — policy engine "enforcing"
   (this is a cline + agent-policy-plugin session, zhulong-style; NOT the
   designflow SUT agent. Note for case design: the trace shows a POLICY-CONstrained
   agent, but the BENCHMARK case should be agent-agnostic — frame as a plain task.)
2. Read `dft_tasks.sv` L1340–1390: L1363 `` `else `` branch hard-codes
   `/proj/dscqa/V0/sim/verilog/ddr6_tb/dscqa/Project/dft_table.v`.
3. SOS-managed `Project/` has `dft_table_0630.v` but NO `dft_table.v`.
4. Local `vecgen_local/Project/dft_table.v` is a symlink → resolves to a valid
   `TYPE_DFT_INFO dft_table[$]` table (newer per-op style). `dft_tasks.sv` there
   is a symlink owned by uid 202338 (a colleague's WIP), not the SOS root uid 14283.
5. vecgen.rpt confirms failing case = `WTM004_block_check_SC1...CRC_11...` (ERROR L14).
6. Compared WTM004 (fail) vs WTM001 (pass): IDENTICAL `+define+` lists (only SC0 vs
   SC1 differ); neither defines `LOAD_P1CM/P2P3CM/P4CM` → both should take the
   `` `else `` branch with the broken include, yet WTM001 passed. Hypothesis: the
   `dft_tasks.sv` symlink target was modified mid-run between the two jobs.
7. Wrote read-only diagnostic `/home/tongfanl/dft_diag.py` (sections: symlink
   status+mtimes, include-target existence, xrun.log grep for COFILX/dft_table/
   VLGERR, find TB that includes dft_tasks.sv). Ran via `run_approved_command`
   profile "python-runner" → exitCode 0, structured stdout (truncated in trace).

## Where the trace ends
Msg #28 = diagnostic script output (truncated). NO final fix applied, NO user
acceptance. The session cuts off mid-diagnosis (user said "continue" at #24).
⇒ There is NO clean "user-accepted gold result" to mirror verbatim.

## Case-framing options (for the round that builds it)
- **(A) diagnostic-script L1/L2** (recommended, matches real intent): deliverable
  = a read-only diagnostic script that, given a vecgen_local-style project layout
  (files + symlinks + xrun logs), emits a structured report (sections: symlink
  target resolution + mtime, include-target existence per `ifdef branch, xrun.log
  error grep counts, TB-includer of dft_tasks.sv). Reference solution ≈ the
  `dft_diag.py` the assistant wrote (READ IT from .75:
  `/home/tongfanl/dft_diag.py`). Hidden B = a synthesized smaller project tree
  with controlled symlinks/files/logs so ≥8 structural facts can be asserted.
  check.py runs candidate script on hidden B, parses stdout sections, asserts.
  ⚠️ Effort: building a realistic hidden-B filesystem layout is the heavy part.
- **(B) include-fix L2/L3**: deliverable = patch (symlink dft_table.v→dft_table_0630.v
  in SOS Project, or fix include path in dft_tasks.sv) + re-run. Heavy (needs real
  xrun tools), hard to self-verify without the toolchain. Not preferred.

## Data the builder needs to fetch from .75
- `/home/tongfanl/dft_diag.py` (reference diagnostic script)
- `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/Project/`
  (dft_tasks.sv symlink, dft_table.v symlink) — for asset A
- `.../log/stimulus_tongfanl/WTM_fsm_1013_try/WTM004.../xrun.log` + WTM001 log
  (pass vs fail) — for asset A / hidden B
- `/proj/dscqa/V0/sim/verilog/ddr6_tb/dscqa/Project/` (SOS-managed, missing
  dft_table.v, has dft_table_0630.v)

## Verdict
Real, fresh, A-domain, small (268 KB). Legitimate debug/diagnosis intent (per
2026-11-15 order, debug-Q&A is allowed). Best framing = diagnostic-script (A).
Not built this round because: (1) super_intelligence_2035 workspace corrupted by
a concurrent `git pull --rebase --autostash` collision (shard C) — 11000 deleted
tracked files, index/HEAD inconsistency, 30 stashes — could NOT safely commit
deepread/ledger/MEMORY; (2) hidden-B filesystem synthesis + check.py + self-verify
exceeds the remaining time budget. Next round: `claim` r6bcb, fetch dft_diag.py,
build framing (A).

---
## ⛔ BLOCKER note — shard A r876 (2026-11-21)
This round produced 0 cases. Root cause = shared-workspace hazard, NOT pool
exhaustion or capability:
- `super_intelligence_2035` (workspace repo) was mid-`git pull --rebase --autostash`
  by **shard C** (PID 869413 / git rebase PID 957364) when shard A woke. Shard C
  later ran `git rebase --abort`. Net state observed: HEAD = shard A's own r875
  commit (008a9adf1, 2 ahead / 1 behind origin), but the **working tree is
  massively corrupted** — 11000 tracked files deleted from disk yet present in
  index/HEAD (including ALL designflow/ scripts, trace_ledger_A.tsv, every
  daily-memory). 30 autostashes accumulated. 2 B/D files show in-transit `M`
  modifications.
- Per AGENTS.md sync discipline (🚫 don't clean/reset/stash others' changes;
  🚫 don't `git stash pop`; ✅ stop & report blocker on unresolvable conflict),
  shard A did NOT pull/push/repair super_intelligence_2035 this round.
- EDA-Flow-Bench (case-artifact repo) is CLEAN (HEAD=origin/master, 0/0, no
  rebase, no stash) — shard A's prior r875 case (CompressBasicRunbookQA-001) is
  already committed+pushed there.
- Shard A recovered trace_ledger.py + trace_ledger_A.tsv + candidates from HEAD
  via read-only `git show` to a scratch dir and ran `next` against the latest
  scan (20261120_145529) on .75 → r6bcb selected + deepread (this file).

**Recommendation to operator**: repair super_intelligence_2035 working tree
(restore the 11000 deleted tracked files without discarding the 2 B/D in-transit
`M` modifications — e.g. `git checkout -- <only deleted paths>` or re-clone to a
side dir); clear the 30 autostashes in a dedicated maintenance window; remind all
shards to NOT run `git pull --rebase --autostash` concurrently in the shared
working copy (this is the 3rd documented autostash accident). mc≥5 pool for A is
NOT exhausted — fresh A-domain candidates exist (r6bcb, pmnfz, x88fx verified
fresh against the 696-sid ledger).
