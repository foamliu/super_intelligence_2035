# r998 deepread — 7j1bw async-fifo trace collision + fresh-diff bug

## Round outcome
**0-case round.** Built a complete async-FIFO produce-task case on trace 7j1bw, then
discovered 7j1bw is **already a shard-D case (EDA-Eval-DesignFlow-AsyncFifoSim-001,
commit 3e9a310)** and explicitly abandoned in shard-A ledger (L: "cross-shard collision:
AsyncFifoSim-001 is shard D case; shard A abandons"). Reverted the case before commit;
A.jsonl back to 456 (matches HEAD), no AsyncFifoTemplate entry in any jsonl.

## Root cause 1 — fresh-diff short-sid extraction bug
`a_pure_short_sids.txt` was built with `n=split($3,a,"_"); print a[n]` → for sid
`1791962616204_7j1bw` yields `7j1bw`. Ledger short-sid was built the same way on col1,
but ledger col1 = `1791962616204_7j1bw.messages.json` → last `_`-token =
`7j1bw.messages.json`, NOT `7j1bw`. So the two sets never matched on `.messages.json`
suffixed sids → 7j1bw (and every ledgered `.messages.json` row) appeared "fresh".

**Fix (applied this round):** strip leading `^[0-9]+_` AND trailing
`.messages.json` / `.messages.archive.json` / `.json` from BOTH sides before comm.
Recomputed fresh = **30** (was 96 with the bug). 7j1bw correctly drops out; mejpi
correctly drops out (was falsely "fresh" in the buggy 96-list).

## Root cause 2 — 7j1bw is a D-shard case
7j1bw (caozhang, async FIFO RTL template + TB + run script) is:
- in trace_ledger_A.tsv: parked, note "cross-shard collision: AsyncFifoSim-001 is
  shard D case (commit 3e9a310); shard A abandons" (r663-era).
- in trace_ledger_B.tsv: parked, spice_sim (wrong-shard).
- in trace_ledger_D.tsv: the actual case AsyncFifoSim-001.
- in HEAD: `benchmarks/.../EDA-Eval-DesignFlow-AsyncFifoSim-001/` (C-shard commit
  97d8ca2ba swept the in-flight files; B-shard commit c08da7927 cleaned them).

So 7j1bw is a hard "一 trace 一 case" violation if shard A reuses it. **Do not pick.**

## Other fresh candidates considered (30 fresh, correct diff)
Top by mc from a_pure_all_r998.tsv (col1 = match_count):
- **kjrai** (t0002470@hfeg0pkn001, mc87, verilog:997) — deep-read: user asks
  "参考这个readme去分析内容" + provides VCD / coverage HTML report / sim log paths,
  wants root-cause for PRE_PB_WO_AS covergroup all-zero bins. Assistant writes
  Python analysis scripts (analyze_cov_pre_pb_wo_as.py, find_timing_logic.py) that
  PARSE proprietary lpddr5 coverage JSON / VCD. This is an **analysis/debug task**,
  not a clean produce-task with a self-contained checkable deliverable (would need
  the huge proprietary coverage data bundled). Skipped.
- **dkeeq** (xuebaok@hfhds206, mc47, analog:121;verilog:64;cadence:43) — analog
  dominant → B/D-leaning, weak A-pure.
- **vjetl** (tongfanl@hfhdspkn002, mc38, netlist:422;synopsys:10) — netlist dominant
  → B/D.
- **m2iag / le2ke / 60khu / 5d3vo / 1862w** (guomings@hfeg0plg54, mc34 each,
  rtl:41;verilog:3;analog:1 — 5 sessions, IDENTICAL keyword profile = same user
  same task repeated) — rtl dominant = A-pure, but low mc (34) and likely a small
  repeat task; not yet deep-read.
- rest (czfpa, vv500, r8b4l, ts189, x5h2n, ...) — low mc, mixed.

## State
- EDA-Flow-Bench repo: **clean** (git status empty), A.jsonl 456 == HEAD, no
  AsyncFifoTemplate in any jsonl, AsyncFifoSim-001 (C-shard) intact in HEAD.
- super_intelligence_2035: ledger untouched (7j1bw claim REFUSED — already in B
  ledger; mark REFUSED — cross-shard mutex). Only this deepread + MEMORY update.
- eda_flow session: to declare_done + close.

## Recommendation for next round
1. Use the **corrected** fresh-diff (strip `.messages.json` suffix). 30 fresh
   available; the guomings rtl:41 cluster (m2iag/le2ke/60khu/5d3vo/1862w) is the
   most promising un-read A-pure produce candidate — deep-read one next.
2. Before building, always `grep <sid> trace_ledger_*.tsv` to confirm not in ANY
   shard (the mutex is cross-shard).
3. The 30 fresh list is saved at /tmp/fresh_a_pure2.txt (local); a_pure_all_r998.tsv
   + a_pure_short_sids.txt are on the .75 sandbox workdir.
