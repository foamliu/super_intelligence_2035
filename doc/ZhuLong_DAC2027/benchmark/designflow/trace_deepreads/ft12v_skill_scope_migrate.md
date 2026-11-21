# ft12v — Skill Scope Migrate (Cline-fork SKILL dirs → project-local)

- **trace**: `1794788771330_ft12v.messages.json`
- **user**: xxchen @ hfeg0plg06 (10.x)
- **session mc**: 167 (DRC:1016 dominant, also LVS/PEX hints)
- **case-id**: `SkillScopeMigrate-001` (shard C, physical_verify domain)
- **track**: B · tier L2-boundary · A-tier self-contained
- **claimed**: r913 backup → r914 synth
- **status**: case (synth complete, 2026-11-21)

## Real task (xxchen)

xxchen maintains a Cline-fork with global SKILL directories under `~/.cline/skills/`.
Two skills (`QA_pattern_debug`, `create_QA_pattern_function`) lived globally but are
project-specific to `~/workspace/DRC_pattern_tool/0.5/device_rule1/`. He wanted to
relocate them to `<project>/.cline/skills/` so they:

1. stop polluting every other Cline project's skill namespace,
2. become versionable with the DRC tool repo,
3. still load via SKILL.md discovery.

The concrete flow (155 msgs) was:
1. inspect `~/.cline/skills/` listing → identify the 2 dirs
2. `mkdir -p <project>/.cline/skills/` and `cp -a` byte-faithful
3. `rm -rf` the global copies (after verifying copy success via `diff -r`)
4. rewrite `SKILL.md` internal path references from `~/.cline/skills/<skill>/...`
   to relative `<project>/.cline/skills/<skill>/...`
5. prepend an entry to `<project>/.cline/skills/update_history.md`
6. append `<project>/.cline/skills/` rule to `<project>/.gitignore`

Why this is a clean physical_verify / project-hygiene case (not pure SRE):
the skills drive DRC pattern debug + QA pattern function generation; relocating
them without breaking SKILL.md discovery is the project-scope analog of
"verify layout skill integrity after a layout-flow SKILL move". The verify
weight is on byte-faithfulness + path-ref correctness + history trail, which
is exactly the L2-boundary check pattern we want shard C to exercise.

## A-tier reframe (synthetic fixtures)

The real project files are READ-ONLY (xxchen's live workspace). To keep the
case self-contained and reproducible without depending on xxchen's machine,
we built deterministic synthetic fixtures:

- `env_A.tar.gz` (visible assets): fake project `proj_alpha/` with 2 fake
  skills under `~/.cline/skills/` (`skill_drc_audit`, `skill_lvs_helper`),
  each with SKILL.md + 2 helper .py files. SKILL.md contains absolute
  `~/.cline/skills/<skill>/...` references that the SUT must rewrite.
- `env_B.tar.gz` (hidden B): alternative project `proj_beta/` with 3 skills
  (`skill_pex_view`, `skill_drc_audit`, `skill_lvs_helper`) — different skill
  count + names to defeat hardcoded-A solutions.
- `env_B2.tar.gz` (hidden B2): yet another `proj_gamma/` with 1 skill only
  (`skill_drc_audit`) — minimum-N edge.
- `migrate_spec.json`: project/skill-agnostic contract the SUT must read;
  names the source dir, dest project path, skills list, and expected
  `update_history.md` / `.gitignore` mutations.

The reference `solve.py` reads `migrate_spec.json` and is fully project/skill
agnostic — passes 16/16 on env_A and (by construction) on env_B / env_B2.

## check.py — 16 teeth (a–p)

| tooth | assertion |
|---|---|
| a | exactly one `<dest>/.cline/skills/` tree exists, no leftover global copies |
| b | each migrated skill dir exists under dest with all original files |
| c | byte-faithful: `diff -r` source-vs-dest empty for every skill |
| d | core skill payload file (the `.py` impl) present under dest (§4.9 fakes FAIL here) |
| e | global `<src>/<skill>/` removed for every migrated skill |
| f | non-migrated global skills (if any) untouched |
| g | SKILL.md exists under each dest skill |
| h | SKILL.md no longer contains absolute `~/.cline/skills/<skill>/` self-ref |
| i | SKILL.md rewritten to project-relative form |
| j | `update_history.md` exists at `<dest>/.cline/skills/update_history.md` |
| k | `update_history.md` prepended (new entry above old top line) |
| l | `update_history.md` entry mentions the migrate action + timestamp |
| m | `<project>/.gitignore` exists |
| n | `.gitignore` has a line covering `.cline/skills/` (exact or pattern) |
| o | `.gitignore` append did not duplicate a pre-existing identical line |
| p | no extra unrelated files written under dest (no junk) |

## Negatives (4, all FAIL distinct teeth)

| negative | fails tooth | why |
|---|---|---|
| `only_print` | a, b, c… | just prints "done", no FS mutation |
| `hardcode_A` | h, i, n | hardcodes env_A names; breaks on hidden B/B2 (caught even on A by tooth n) |
| `delete_all` | b, c, d, f | `rm -rf` global src without copying — destroys payload |
| `copy_only` | e, h, i, j, k | copies but skips global removal + SKILL.md rewrite + history |

## §4.9 three-fake

| fake | fails tooth | why |
|---|---|---|
| `empty_shell` | d | check.py framework with no assertions — tooth d (core payload check) catches |
| `only_print_expected` | d | "expected" stub that only prints expected outputs — tooth d catches |
| `ref_delete_core` | d | ref check.py with the payload-presence tooth deleted — tooth d (now a no-op) still d-tagged FAIL via self-consistency |

## Roundtrip verification

- check.py on disk sha256: `1cd9ad3ef982c683333c5c1d63883beac3a1a0d1371acced6bb2270b72d7966a`
- check.py extracted from C.jsonl test.check_code sha256: same → MATCH
- k_check (teeth in check.py): 16 (a–p)
- k_rationale (marks in test_rationale): 16 — both ≥ 8 ✓
- ref solve.py: PASS 16/16 on env_A
- 4 negatives + 3 §4.9 fakes: all FAIL (distinct / tooth d)

## Trace sourcing

- `metadata.trace_source.host`: hfeg0plg06
- `metadata.trace_source.user`: xxchen (real username, not hashed)
- `metadata.trace_source.session_file`: 1794788771330_ft12v.messages.json
- `metadata.trace_source.session_msgs`: 155
- `metadata.trace_source.real_task_summary`: relocated 2 globally-placed
  Cline-fork SKILL dirs from `~/.cline/skills/` to project-local
  `<project>/.cline/skills/` with byte-faithful copy + global removal +
  SKILL.md path-ref rewrite + update_history.md prepend + .gitignore append.
- Keys/tokens/passwords masked; no other PII.

## Lessons (carried forward)

1. **tooth-a basename filter**: exclude `check.py` and `negative_selftest.py`
   by *basename*, not by `"solve"` substring — otherwise ref `solve.py` is
   mis-excluded and tooth-a false-fails.
2. **negative_selftest runner**: must use multi-line heredoc-style runner
   script, not single-line `python -c` with embedded newlines (breaks).
3. **fixture determinism**: build tars from a Python script with fixed mtime
   (`tarfile` + `time.time()` override) so roundtrip sha256 is stable across
   re-runs.
4. **A-tier agnostic solution**: putting the contract in `migrate_spec.json`
   and making `solve.py` read it is what enables hidden B/B2 to use the same
   check.py — defeats hardcoded-A negatives cleanly.
