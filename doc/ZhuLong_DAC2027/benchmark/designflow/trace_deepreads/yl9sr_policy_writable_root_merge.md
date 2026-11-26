# Deepread: 1792999100763_yl9sr — PDK QA Policy writableRoots Merge

## Trace metadata
- **session**: 1792999100763_yl9sr.messages.json
- **user**: xinqiaoz @ 10.129.2.11 (hfeg0plg46 inferred)
- **mc**: 76 (pdk / drc / calibre / qa domain keywords dominate → physical_verify C)
- **date**: 2026-11-18
- **msgs**: single clean user turn + assistant tool_use sequence
- **agent**: cline (Empyrean Aether SKILL/pyAether host)

## User intent (verbatim)
> 当前 generate_policy.py 生成的 policy 文件的 writableRoots 只有 /home/xinqiaoz/，
> 现在我想增加一个 /home/pdk/xinqiaoz/ 目录。

i.e. modify `generate_policy.py` so the generated `agent-policy.json`'s `writableRoots`
adds `/home/pdk/xinqiaoz/` on top of the existing `/home/xinqiaoz/` (and `/home/xinqiaoz`)
roots.

## Real artifacts recovered from trace (tool_result messages)
- **`generate_policy.py`** (165 lines, pre-modification): reads existing
  `agent-policy.json`, computes SHA-256 of each profile script, writes a new
  `agent-policy.json` with the pdkQaSystem profiles (git_status/log/diff/add/commit,
  run_all_tests, run_single_test, run_drcqa, py_compile, git_checkout, git_generic,
  python_generic, shell_generic, ssh_test, hello_world — 15 profiles). The
  writableRoots in the generated policy was hard-coded to `['/home/xinqiaoz/', '/home/xinqiaoz']`.
- **`agent-policy.json`** (real, 15 profiles, 11367 B): top-level keys
  `version / allowedTools / allowedScriptRoots / readableRoots / writableRoots /
  profiles / audit / runCodeGuard`. Real `writableRoots = ['/home/xinqiaoz/', '/home/xinqiaoz']`.
  (assets/PolicyWritableRootMerge-001/existing_policy_A.json is this file verbatim.)
- **assistant's actual modification**: added a constant
  `ADDITIONAL_WRITABLE_ROOTS = ['/home/pdk/xinqiaoz/']` and a "step 2.5" in `main()`
  that does dedup-append of these extra roots into `policy["writableRoots"]`
  (preserving original order, skipping duplicates). Verification output:
  `Writable roots: ['/home/xinqiaoz/', '/home/xinqiaoz', '/home/pdk/xinqiaoz/']`.

## Why physical_verify (not pg_layout)
The trace's keyword mass is pdk-qa / drc / calibre / qa-policy generation in the
PDK QA DRC-QA workflow (the agent-policy.json governs which scripts/roots the
cline agent may use when running DRC QA checks). It is **not** a power-ground
layout task. → domain = `physical_verify` (C-shard), track = `mock-behavioral`.

## Reframe: mock-behavioral `policy-writable-root-merge`
Real `generate_policy.py` is path-dependent on the live PDK_QA tree (computes
live SHA-256s, regenerates the whole policy). To make a self-contained,
deterministic, hidden-B-gradable case, the case strips the SHA-256 recomputation
and reframes the user's *core ask* — "merge extra writable roots into an existing
policy, dedup, append-after, leave everything else alone" — as a pure-stdlib
merge script:

```
python <script> <existing_policy.json> <extra_roots.txt> <output_policy.json>
```

- Read existing policy JSON (preserve dict insertion order, Python 3.7+).
- Read `extra_roots.txt`: strip each line; skip blank lines and `#`-comment lines;
  each remaining line is an extra writable root (kept as-is, NO trailing-slash
  normalization).
- Merge: keep `policy["writableRoots"]` original order; for each extra root,
  if it already exists (exact string equality) skip, else append to end.
- All other top-level fields preserved unchanged (no reordering, no re-hash,
  no profile mutation).
- Write `output_policy.json`: `json.dump(out, indent=2, ensure_ascii=False)` +
  trailing newline; key order = input dict order (deterministic).

### Behavior traps encoded in check()
1. **trailing-slash NOT normalized**: `/home/pdk/xinqiaoz/` ≠ `/home/pdk/xinqiaoz`
   (both kept as distinct strings).
2. **dedup when extra root already in writableRoots** → skip (don't double-append).
3. **append-after**: extra roots must come AFTER original roots (never prepend/interleave).
4. **profiles / allowedScriptRoots / audit / runCodeGuard / version / readableRoots**
   must be deep-equal preserved.
5. **deterministic**: byte-identical output on rerun.

## Hidden inputs
- **B** (`existing_policy_B.json` + `extra_roots_B.txt`): 3 profiles, version 2,
  original `writableRoots = ['/data/userB/work', '/data/userB/work/']`; extras
  include a duplicate of `/data/userB/work` (dedup trap), a new `/home/pdk/userB/`
  (trailing slash), and a new `/tmp/userB` (no trailing slash — slash-normalization
  trap). Expected: `['/data/userB/work', '/data/userB/work/', '/home/pdk/userB/', '/tmp/userB']`.
- **B2** (`existing_policy_B2.json` + `extra_roots_B2.txt`): 2 profiles, version 3,
  original `writableRoots = ['/var/b2/']`; extras include `/var/b2` (differs from
  existing `/var/b2/` by trailing slash → both kept), `/var/b2/` (duplicate → skip),
  `/opt/b2/dir/` (new). Expected: `['/var/b2/', '/var/b2', '/opt/b2/dir/']`.
  B2 length (3) ≠ B length (4) → defeats single-hardcoded-list anti-hardcode.

## check.py — 16 conditions a-p
a zip-py · b py_compile · c run-B-exit0 · d toplevel-keys-preserved ·
e new-roots-present · f dedup-existing-root · g append-after-order ·
h trailing-slash-not-normalized · i profiles-preserved ·
j allowedScriptRoots-unchanged · k version-unchanged · l audit-unchanged ·
m runCodeGuard-unchanged · n readableRoots-unchanged · o B2-antihardcode ·
p determinism-byte-identical.

## Self-verification (local Python 3.12)
- ref solution: **PASS 16/16** on B + B2.
- negatives: naive_empty **FAIL 2/16**, print_expected (hardcoded B) **FAIL 15/16** (only cond o B2-antihardcode fails),
  core_deleted (writableRoots gutted to []) **FAIL 11/16**. `NEGATIVE_SELFTEST_ALL_FAIL = True`.
- determinism: 3 reruns of ref on B → byte-identical.
- embedded `test` field round-trip (extracted from jsonl) vs ref-submit → **PASS 16/16**.

## Delivery
- case_id (ledger): `EDA-Eval-DesignFlow-PolicyWritableRootMerge-001`
- appended to: `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl` (row 461)
- assets: `assets/PolicyWritableRootMerge-001/{existing_policy_A.json, extra_roots_A.txt, generate_policy_original.py.txt, input_spec.json, task_brief.md, hidden/}`
- reference: `reference/PolicyWritableRootMerge-001/{check.py, policy_writable_root_merge_ref.py, negative/}`
- ledger row marked: `1792999100763_yl9sr → case (EDA-Eval-DesignFlow-PolicyWritableRootMerge-001)`
- round: r739
