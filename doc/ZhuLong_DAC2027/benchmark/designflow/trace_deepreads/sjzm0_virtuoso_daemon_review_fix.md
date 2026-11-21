# Deepread: sjzm0 — virtuoso-cli SKILL daemon review-driven bug fix

**Session**: `1787743463896_sjzm0.messages.json` (kanban jsonl, 7.1MB / 49215 lines)
**User**: junxu @ hfeg0pkn005 (10.129.2.14)
**mc**: 2287
**Keywords**: virtuoso:6175; schematic:3040; cellview:1004; dbopencellviewbytype:312; ddgetobj:221; cadence:87; netlist:83; dbget:39; analog:30; binary:22; adexl:20; opamp:15; dbcreaterect:11; verilog:8; maestro:8; techfile:3; pex:3; transistor:2; cmos:2; vhdl:1; spectre:1; rtl:1; pdk:1; lib.defs:1; dbcreatepolygon:1; dbcreatepath:1; dbcreateinst:1; aether:1
**Domain**: layout_virtuoso (C-dominant: c=6183, b=1, a=9)
**Format**: cline kanban streaming jsonl (chat_text / chat_reasoning / chat_tool_call_start / chat_done / chat_queued_prompt_start)

## User intent (real task)

junxu maintains a self-built `virtuoso-cli` SKILL daemon Python package at
`~/.cline/skills/virtuoso-cli/scripts/virtuoso_cli/`. The package provides a
single-threaded socket daemon that forwards SKILL expressions to a running
Cadence Virtuoso process and returns the result. junxu asks the agent to
look at HANDOFF.md critically and apply review items from REVIEW.md.

Concrete deliverable (accepted git commit):
`A4+A6: daemon total-timeout + listen(5); fix nil-dict bug in list_instance_attributes`

3 gold fixes (all static-source-checkable offline):

1. **A6 — socket backlog** (`daemon.py`):
   `s.listen(1)` → `s.listen(5)  # allow pending connections to queue while busy`
   (single pending connection was too small; long SKILL expressions caused
   second client to get ECONNREFUSED.)

2. **A4 — read total-timeout** (`daemon.py`):
   `result = _read_until_delimiter()` →
   `result = _read_until_delimiter(total_timeout=timeout_seconds + 5)`
   (watchdog SIGINT may fail on long schCheck/ocean/stuck IPC; the read loop
   must have a hard deadline slightly beyond the watchdog so the daemon can
   always accept new connections.)

3. **nil-dict bug** (`schematic.py`, `SchematicMixin.list_instance_attributes`):
   `if not isinstance(row, list) or len(row) < 8:`
   → `if not isinstance(row, list) or len(row) < 8 or row[0] is None:`
   (Virtuoso returns `row[0] is None` for a deleted/invalid instance; the
   method used to build `{"name": None, ...}` and callers crashed treating
   a non-empty dict as "instance exists". Now returns `{}`.)

## Iteration history (rich multi-turn)

- iter 1 (msg #2129–#3704): agent added `_busy` flag + busy guard + listen(5)
  + finally reorder + nil-dict fix.
- iter 2 (msg #6973–#7814): junxu pushed back ("可我看到代码里有一行 break",
  "bus 线通常需要配合 vector instance", "如果有一个很高但很窄的器件…pin
  在右边…算法是不是会朝上下 stub"). Agent REVERTED the `_busy` guard
  (removed `_busy` global, removed busy guard block, removed `_busy = False`
  from finally) but KEPT listen(5), total_timeout, and the nil-dict fix.
- commit at msg #8124: `A4+A6: daemon total-timeout + listen(5); fix nil-dict
  bug in list_instance_attributes`.
- later (msg #9053–#9388): separate fix for `check()` method — switch
  schCheck capture from hardcoded `/tmp/_schcheck_capture.txt` to
  `tempfile.mkstemp(prefix="schcheck_")` + add `import os` (concurrent
  schCheck capture file collisions). NOT part of the A4+A6 commit —
  excluded from this case to keep scope tight.

## User prompts (decoded from chat_queued_prompt_start)

1. "你应该以批判性的眼光来看待 handoff，要有自己的判断，不该全盘接受"
2. "bus 线通常需要配合 vcector instance，例如 Iinv<3:0>，当前 api 能够实现吗"
3. "可我看到代码里有一行 break，这真的不会影响执行 skill 吗"
4. "如果有一个很高但很窄的器件，它的 pin 在右边，理论上应该往右边 stub，但这个算法是不是会朝上下 stub"
5. "能直接根据 pin 的坐标判断出是在四条边的哪条边吗？我在 GUI 界面上是能很清晰地看出来在哪条边上的"
6. "这个方法不行，你无法确保 25% 这个是安全的。我在 GUI 中确实能看到一个边框，这个边框连接了所有 pin 的中心点"
7. "当我在 GUI 中选中一个器件时，这个器件会高亮一个蓝色边框，所有的 pin 都在这个边框上"

## Why this trace is a good reframe candidate

- **Real user intent**: junxu is doing real dev work on a Virtuoso SKILL
  wrapper package — clean, accepted git commit as gold.
- **Teeth-checkable offline**: all 3 fixes are static source-code checks
  (regex on daemon.py/schematic.py) + functional test of the nil-dict
  guard with a mock `_exec`. No need for a live Virtuoso or socket daemon.
- **Anti-hardcode**: env_B uses `listen_bad=3` (not 1) and `row_min=10`
  (not 8) so a solver that hardcodes env_A's literal `s/\.listen(1)/` or
  `len(row) < 8` fails on B; must read spec.json for parameter values.
- **Distinct from existing C cases**: not a migration (SkillScopeMigrate),
  not a shell env init fix (VirEnvCancelInitFix), not a doc generator
  (PyLibApiDocGen). New archetype: review-driven Python bug-fix of a
  Virtuoso SKILL daemon package.

## Case produced

`EDA-Eval-DesignFlow-VirtuosoDaemonReviewFix-001` (shard C, layout_virtuoso,
track B, tier L1). 17 teeth (a-q), k_rationale = k_check = 17 (≥8). ref
solve.py PASS on env_A AND env_B; 5 negatives (only_print / hardcode_A /
delete_all / copy_only / skip_nildict) all FAIL distinctly; §4.9(a)(b)(c)
three fakes all FAIL; 3-seed randomization tooth q; roundtrip sha256
997f750a596a1d88a1b84f621c717bc6aca4d6542163f5471257e07102d210a1.
C.jsonl 569 → 570. ledger sjzm0 → case.
