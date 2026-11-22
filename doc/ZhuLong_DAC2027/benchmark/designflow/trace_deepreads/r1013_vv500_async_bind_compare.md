# r1013 deepread — vv500 async_module_bind compare produce-task

**trace**: `1795158759743_vv500.messages.json`
**user**: max7c @ hfeg0pkn005 (mc6, verilog:16 A-pure verification)
**scan**: reused ssh_eda_search_20261122_172249 (r995 rescan); digA A-domain filter; fresh-diff vs 4-shard ledger; vv500 fresh + alive (ssh verified)
**case**: EDA-Eval-DesignFlow-AsyncBindCompareProduce-001 (verification, A档 trace-faithful produce-task + hidden-B)

## Trace anatomy

- **Single-turn act-mode produce-task**. 4 messages total (1 user + 1 assistant + tool-use bookends).
- **U#0 (verbatim)**: 「比较一下 /rundata/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.20260410/proj_monitor/async_module_bind.sv 和 /rundata/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.Nov17/proj_monitor/async_module_bind.sv」
- No vague preamble, no env-config, no follow-up turns. Pure single-intent diff/compare request.
- Assistant read both .sv files via tool calls and produced a structured comparison report (added/removed/common with per-field match flags).

## Files (both fetchable from the trace host, scp'd to .75 sandbox)

- **bind_A_old.sv** = `verilog.lpddr5.ddjoc.20260410/proj_monitor/async_module_bind.sv` — 48 binds, **compact single-line** form, grouped under `//rsnor` / `//rsnand` comment headers. Each bind: `bind <mod> async_checker #(.INPUT_PIN_NUM(2), .PIN_NAMES({"A","B"}), .RS_TYPE("<mod>")) <inst> ( .in({B,A}) );` on consecutive lines.
- **bind_A_new.sv** = `verilog.lpddr5.ddjoc.Nov17/proj_monitor/async_module_bind.sv` — 52 binds, **expanded multi-line** form, with a `// deploy-bind-src-sha256=...` header, `// Generated: 2026-11-17 20:25:08`, and a `// Total RS latch types scanned: 52` tail. Each bind spans 7+ lines with each parameter on its own line.

## Trace gold comparison (A pair, verified on .75 sandbox)

- total_a = 48, total_b = 52
- **added (5)**: `RS_XdecGapDrv` (pin5 A,B,C,D,Out), `RS_tRasLock_New` (pin4 Out,RN,Rst,SN), `rsnand22GSx1` (pin2 A,B), `rsoai122PFx2ClkSyncEn` (pin2 A,B), `rsoai212Pre` (pin2 A,B)
- **removed (1)**: `rsnand22KFx1` (pin2 A,B)
- **common (47)**: all params + port_order identical between the two files

## Case abstraction

Generalized the single-shot A comparison into `compare_async_binds.py <file_a.sv> <file_b.sv> <output.json>`:
- Regex parses `bind <mod> async_checker #(...) <inst> (.in({...}));` with `re.DOTALL` so both compact single-line and expanded multi-line forms match.
- Extracts per-module: `INPUT_PIN_NUM` (int), `PIN_NAMES` (list), `RS_TYPE` (str), `port_order` (list from `.in({...})`).
- Emits JSON: `file_a`, `file_b` (basenames), `total_a`, `total_b`, `added[]` (module + fields), `removed[]`, `common[]` (module + 5 boolean match flags: pin_num/pin_names/rs_type/port_order/params_match).
- Sorted by module name; no hardcoded names or counts.

## Hidden B construction (anti-hardcode)

- **Suffix rename**: every module name, RS_TYPE string, and instance name in A_old/A_new gets a `_B` suffix. Same bind structure, same regex parseability, but all module names are different.
- **Vary totals**: drop the last 2 binds from B_old (48 → 46) and add 3 fresh `RS_FreshHidden*` binds to B_new (52 → 55). This shifts added/removed/common counts away from A's 48/52/5/1/47.
- Resulting B: total_a=46, total_b=55, **added=10** (5 original-suffixed + 2 dropped-from-B_old become added + 3 fresh), **removed=1** (`rsnand22KFx1_B`), **common=45** (all params_match + port_order_match True).
- `hidden_manifest.json` records expected counts + the list of A-specific unsuffixed names that must NOT leak into a correct B output.

## check.py (14 assertions, k≥8)

Embedded **independent reference parser** (`_ref_parse` / `_ref_compare`) re-parses B_old/B_new and computes the expected totals/added/removed/common, then compares against the SUT's output. Assertions:
- a: hidden/ + manifest + B fixtures present
- b: submit.zip contains compare_async_binds.py
- c: py_compile passes
- d: SUT runs on hidden B, exit 0, produces output.json
- e: total_a == 46 (B_old count, NOT A's 48)
- f: total_b == 55 (B_new count, NOT A's 52)
- g: added set == B reference (10 _B-suffixed modules, exact match)
- h: removed set == B reference (1 module: rsnand22KFx1_B)
- i: common count == 45 + every common entry params_match==True AND port_order_match==True
- j: anti-hardcode A — output.json must NOT contain A-specific unsuffixed names (word-boundary regex check)
- k: anti-hardcode numbers — totals must NOT be A's 48/52
- l: determinism — 3 runs produce byte-identical output.json (md5 match)
- m / m2: file_a basename == bind_B_old.sv AND file_b basename == bind_B_new.sv (proves SUT used CLI args, not hardcoded paths)

## §4.9 three-fake FAIL (negative_selftest)

- `fake_print_expected.py`: hardcodes A's output (totals 48/52, A's unsuffixed added/removed) → FAIL at (e) total_a=48≠46
- `fake_hardcode_a_added.py`: parses B for totals but hardcodes A's added/removed lists → FAIL at (g) added set mismatch
- `fake_buggy_parser.py`: regex without re.DOTALL, misses all multi-line binds → FAIL at (f) total_b=0≠55

REF `compare_async_binds.py` (the reference solution) PASSes all 14. negative_selftest OK: ref PASS + 3 neg FAIL.

## Verdict

Clean single-turn produce-task, trace-faithful, A-档 self-contained, hidden-B anti-hardcode (suffix rename + total shift), 14 independent assertions ≥ 8, three-fake FAIL verified. Suitable for design_flow eval.
