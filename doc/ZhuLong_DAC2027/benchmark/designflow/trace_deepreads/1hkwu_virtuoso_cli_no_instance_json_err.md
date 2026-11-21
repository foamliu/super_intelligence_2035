# Deepread: 1hkwu — virtuoso-cli SKILL daemon no-instance structured JSON error report fix

**Session**: `1787122881271_1hkwu` (dir form, .messages.json 2.3MB / 670 msgs / 42 typed user_inputs)
**User**: junxu @ hfeg0plg79 (NFS-shared home across hfeg0plg79/17/pkn005/pjn200)
**mc**: 1956
**Keywords**: virtuoso:6610; cadence:186; synopsys:110; cellview:76; verilog:57; spectre:47; maestro:47; binary:47; netlist:44; schematic:38; dbcreaterect:34; skipper:30; analog:23; hspice:21; calibre:15; aether:10; ddgetobj:6; floorplan:5; adexl:5; techfile:3; assembler:3; .spi:2; drc:1
**Domain**: layout_virtuoso (C-dominant; virtuoso-cli SKILL daemon infra — same lineage as sjzm0/r915)
**Format**: cline messages.json (role/content blocks: text / tool_use / tool_result)

## User intent (real task)

junxu maintains a self-built `virtuoso-cli` SKILL daemon Python package at
`~/.cline/skills/virtuoso-cli/scripts/virtuoso_cli/`. The package provides a
TCP daemon that forwards SKILL expressions to a running Cadence Virtuoso
process and returns the result. Virtuoso runs on a REMOTE server (hfeg0plg17)
accessed via NFS; many users share one server and multiple Virtuoso instances
may run concurrently. The session is the original build-out of the skill
(42 typed user inputs spanning daemon launch, .cdsinit bridge, multi-instance
support, TCP-no-auth security, server auto-detect, --stdin/heredoc, docs).

## Turning point selected (U41, idx ~619–642)

User feedback (U41, idx 645): "用户反馈 --stdin 命令报错之后拿不到错误报告".

Root cause found by assistant: `_make_client(args)` in `cli.py` calls
`sys.exit(1)` when `_discover_instances` finds no reachable Virtuoso instance
(e.g. Virtuoso not started, or daemon died but `~/.virtuoso-cli/ports/*.port`
stale files remain). Because `_make_client` hard-exits, `cmd_test` /
`cmd_status` / `cmd_eval` never get a chance to emit a structured JSON error
report — the process just dies after a bare stderr line, so callers (agents /
scripts) cannot recover or parse the failure. Additionally `SkillClient`
defaults `host="127.0.0.1"` / `port=65432`, which on this NFS cluster connects
to the wrong host (Virtuoso is on hfeg0plg17, not localhost).

### Gold fix (committed, idx 619–642)

1. **`_make_client`** — replace the `sys.exit(1)` block with `return None`
   (caller decides how to handle the no-instance case).
2. **`cmd_test`** — add `if client is None:` branch printing
   `{"connected": False, "hint": "No reachable Virtuoso instance found. ..."}`
   (JSON, exit 1).
3. **`cmd_status`** — add `if client is None:` branch printing
   `{"bridge_running": False, "state": "unreachable", "errors": [...]}` (exit 1).
4. **`cmd_eval`** — add `if client is None:` branch printing
   `{"status": "error", "errors": ["No reachable Virtuoso instance found. ..."]}`
   (exit 1).
5. **`SkillClient.__init__`** — defaults `host=None, port=None` (auto-discovered),
   no `127.0.0.1`/`65432` fallback.
6. **`skill_bridge.il`** — always bind `0.0.0.0` (remote-server reachability).

## B-reframe (A infeasible)

A (live workspace) infeasible: live `~/.cline/skills/virtuoso-cli/` is READ-ONLY
to the agent and the SUT sandbox has no Virtuoso license/socket. Reframe =
fix-the-bug fixture: env_A has a self-contained buggy `cli.py` (same buggy
structure: `_make_client` sys.exit + `SkillClient` 127.0.0.1/65432 defaults +
no `client is None` branches) + spec.json. Deliverable = fixed `cli.py` +
`report.json`. check.py runs the delivered `cli.py` against env_B's ports dir
(no daemon listening on any B port) via subprocess and asserts each cmd_*
emits the structured JSON error report.

## Distinctness vs r915 (sjzm0)

r915 fixed: A4 (read total-timeout), A6 (listen backlog), nil-dict bug in
`list_instance_attributes`. This case fixes: no-instance `_make_client`
return-None + structured JSON error branches in cmd_test/status/eval +
SkillClient None/None defaults. Orthogonal bug, same skill package, same
user — no overlap.

## Anti-hardcode

env_B ports dir uses DIFFERENT port/PID values (59999/9999, 60001/8001) from
env_A (65432/12297, 52297/15229). The fix (string-replace on buggy patterns +
None-branches) is content-agnostic; check.py tooth m asserts cmd_test output
contains neither A port nor A pid; tooth i asserts SkillClient defaults
None/None (no 127.0.0.1/65432); tooth p asserts no hardcoded
`SkillClient("127.0.0.1"...)` / `SkillClient(...65432)` construction.

## Self-verification

- ref solve.py → fixed cli.py: check.py PASS 16/16 teeth (a–p).
- 4 negatives all FAIL distinct:
  - only_print (buggy cli, report lies) → tooth e (_make_client still sys.exit)
  - hardcode_A (only cmd_test None-branch) → tooth g (cmd_status missing None-branch)
  - empty_report (fixed cli + empty report) → tooth o (report.json missing)
  - delete_core (cmd_test None-branch removed) → tooth f (cmd_test missing None-branch)
- §4.9 (a) empty cli → tooth b; (b) only-print → tooth e; (c) delete-core → tooth f.
- 3-seed determinism (tooth n): cmd_test byte-identical across 3 seeds.
- roundtrip sha256: disk check.py == jsonl test field ==
  `360930331b91b9fa7e3aa14a2344eb44308a7c28e5360c6f1a208a77d3365faa`.
- k_rationale = k_check = 16 (≥8 ✓).

## Lessons

(a) **no-instance sys.exit is a clean fix-the-bug**: bug has clear behavioral
failure (caller gets bare stderr + exit, no JSON); gold fix = return None +
per-cmd JSON branches;区分齿强 (buggy sys.exit → tooth e FAIL; fixed None →
teeth j/k/l PASS on B).
(b) **anti-hardcode via B port/PID rotation**: B uses different unreachable
ports/PIDs than A; a hardcoded-A solution leaks A values into output (tooth m
FAIL) or keeps 127.0.0.1:65432 default (tooth i/p FAIL).
(c) **collision hazard**: this exact case (same ID, same fixtures, slightly
buggier check.py) was already committed by a parallel agent (paul.liu,
"shard D bench-shardD" 21:46) WITHOUT jsonl append or ledger mark. Mine is
the bug-fixed check.py (SkillClient class regex + tooth-p real assertion) and
the first jsonl append + ledger claim. Future: check `git ls-tree HEAD` for
case-ID collisions before building; claim ledger BEFORE building to avoid
duplicate work.
(d) **layout_virtuoso domain includes virtuoso-cli skill infra**: precedent
r915 (sjzm0) classified virtuoso-cli daemon work as layout_virtuoso; this case
follows that precedent (virtuoso keyword is shard C's).
