# Deepread: r1110 ejxsv — jkxu DDR5 RHR Mirror Internal_Monitor.rpt PhWL grouping

- session: `1795352038992_ejxsv.messages.json`
- user/host: `jkxu` @ `hfeg0pkn001` (10.129.2.10)
- mc: 54 (verilog:1086; drc:915; synopsys:2; netlist:2; analog:2; rtl:1) → A-pure verification
- fetched via eda_flow: scp from `/home/jkxu/.cline/data/sessions/1795352038992_ejxsv/1795352038992_ejxsv.messages.json` (subdir path), 503KB / 65 msgs (33 user / 32 assistant)
- real `/rundata/drcpa/.../Internal_Monitor.rpt` → permission denied (e0031982 cannot read jkxu files) ⇒ B档 synthesized

## Two tasks in session

### Task 1 (msgs 0-31) — USED for case
User asks "分析当前log" on
`/rundata/drcpa/V0/simdir/verilog/jkxu/verilog.ddr5.drcpa.post_2nd_rev/RHR_MIRROR/rhr_mirror_bk=0_new.x16_9200/Internal_Monitor.rpt`
(a 536-line `[WL_MON] RHR_MIRROR_SCAN` WordLine monitor log). Assistant reads the
file in 2 chunks and produces a phased analysis:
- Phase 1 (lines 1-224, PhWL 0x00-0x5f): normal sequential ascending scan,
  2-4 records/PhWL, ADDSUB 0001/0010, Sample GrDec progressively clearing
  lowest 1-bit (...ffe→...ffd→...ffb→...ff7→...fef→...), PhDec ∈{0,1,2,4,8}.
- Phase 2 (lines 225-260, PhWL 0x373ff→0x373f0): anomalous big jump (+226720)
  then descending, GrDec all-f, PhDec 0, WL_IDX 322-335.
- Phase 3 (PhWL 0x3756f→0x37560): higher-address descending, WL_IDX ~683-703.
- Phase 4 (PhWL 0x3556f→0x35560): another high descending, WL_IDX ~1371-1391.
- Phase 5: random scattered addresses, no monotonicity.

User refines: "相同PhWL 归为一组" (group same PhWL together). Assistant writes
`group_phwl.py` — first attempt with a strict regex fails (line format has
irregular spacing around commas: ` ,Sample` no-space vs ` , Sample` space vs
` , WL_IDX` space); switches to a comma-split + " is " parser. Produces 268
unique PhWL groups from 664 lines, each group 1-4 records, then a full phased
report.

**Line format (trace-faithful):**
```
@<ts> [WL_MON] RHR_MIRROR_SCAN: PhWL is <hex> ,ADDSUB is <4bit> ,Sample GrDec is <hex> , Sample PhDec is <hex> , WL_IDX_Cal is <dec> ;
```

### Task 2 (msgs 32-64) — NOT used
User asks to kill sim jobs: under
`/rundata/.../verilog.ddr5.drcpa.cov/log.reg.cov/16Gb/PRAC`, find all dirs whose
`verilogrun` file contains `automsie` and kill the running LSF jobs. Assistant
writes kill scripts; first attempt over-matches and kills 107 jobs (too broad);
rewrites to precise-match against user-provided `bjobs` output; lists matched
jobs manually. This is a live-system-state task (hard to make a faithful
check) ⇒ not used.

## Case synthesis (B档)
- task_id: `RhrMirrorPhwlGroupAnalyzeProduce-001`, domain verification
- Visible A: `Internal_Monitor_A.rpt` (126 lines, 62 unique PhWL) — 4 phases:
  inc(32 PhWL 0x00000-0x0001f) → jump → dec(8, 0x373ff-0x373f8) → jump →
  dec(10, 0x5a5a5-0x5a59c) → jump → scatter(12, 0x0b000 cluster, deltas 50-220).
- Hidden B: `Internal_Monitor_B.rpt` (180 lines, 90 unique PhWL) — 4 phases:
  inc(40, 0x00000-0x00027) → jump → dec(16, 0x4b1ff-0x4b1f0) → jump →
  dec(18, 0x6c3d5-0x6c3c4) → jump → scatter(16, 0x13077 cluster, deltas 50-240).
- A/B discriminating tokens zero-overlap: A={373ff,5a5a5,0b000,drcpa,
  rhr_mirror_bk=0,post_2nd_rev,x16_9200}; B={4b1ff,6c3d5,13077,ddrtop,
  rfm_bk=3,rev_4b,x8_4800}.
- Deliverable: `group_phwl.py <rpt> <out.json>` — parse, group-by-PhWL
  (first-appearance order), classify phases (inc/dec/scatter separated by
  |delta|>=1000 jumps), emit JSON {rpt_path,total_records,unique_phwl,groups,
  phases,jumps,max_jump_delta}.
- check: 14 assertions (a-n), independent oracle (different comma-split parser),
  runs on hidden B, anti-hardcode (A tokens absent from B-output), determinism
  (3x md5). ref PASS 14/14; §4.9 三假 (empty/print-only/core-deleted) all FAIL;
  neg_selftest ALL_OK.
