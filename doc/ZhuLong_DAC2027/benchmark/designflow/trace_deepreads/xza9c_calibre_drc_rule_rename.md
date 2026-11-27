# Deepread: xza9c — Calibre DRC Rule File Transformer (jaychen)

## Trace source
- user: jaychen (FRESH USER, only 3 sessions)
- host: hfeg0pkn005 (file in /home/jaychen/.cline/data/sessions/1795572780344_xza9c/)
- session_file: 1795572780344_xza9c.messages.json (1.9MB, mc827)
- cwd: /home/jaychen/workspace/3DIC_DRC
- model: deepseek-v4-flash (cxmt-deepseek-flash)
- started 2026-11-25, status idle
- match_count: 827; keywords: drc:2078;calibre:574;cmos:97;pex:47;pdk:36;aether:9;gdsii:5;.gds:5
- domain: **physical_verify** (C-shard) — Calibre DRC rule file management

## ⚠️ PATH-FIX BREAKTHROUGH (applies to ALL shards)
cline sessions are stored in **subdirectories**: `/home/<user>/.cline/data/sessions/<epoch_id>/<epoch_id>.messages.json`, NOT flat files. r1469 (and earlier) stop-loss was based on WRONG flat path `/home/<user>/.cline/data/sessions/<epoch_id>.messages.json` → "No such file or directory". With correct subdirectory path, ALL "rotated" candidates (j7cyb/xza9c/x3t64/wf513) are fetchable. The AGENTS.md command template `head -c 4000 /home/<user>/.cline/data/sessions/<session_file>` is WRONG — must be `head -c 4000 /home/<user>/.cline/data/sessions/<epoch_id>/<epoch_id>.messages.json`.

## User intent (real task)
Transform a real DRAM Calibre DRC rule file (`calibreDRC.rule`, 36213 lines / 1.6MB) → `calibreDRC_CHENXING.rule` with a series of suffix/number transformations. Requirements evolved through ~12 user corrections:

1. **Global derived layer suffix**: Add `_CHENXING` to all global derived layer names (top-level `name = ...` at depth 0), BOTH on definition LHS and reference RHS.
2. **Rule-block local var protection**: Local variables inside `{ }` blocks (e.g. `A1 = ...` inside `PG_W_029_00 { ... }`) must NOT be modified.
3. **Case-insensitive matching**: SVRF derived layer names are case-insensitive. `M0A_incore_real` (lowercase def @L6790) must match `M0A_INCORE_REAL` (uppercase ref @L7180); both become `M0A_incore_real_CHENXING` (preserve original spelling when appending).
4. **PRIMARY keyword vs derived layer**: `PRIMARY` is both. `PRIMARY ONLY` (in `WITH TEXT ... PRIMARY ONLY`) is a keyword → NO suffix. `PRIMARY` as derived layer reference → suffix. 994 PRIMARY ONLY preserved, 29 derived refs suffixed.
5. **Local dotted-name protection**: `P_2d8v.M1` (rule-block local dotted derived layer @L28999) — embedded global short name `M1` must NOT be suffixed within dotted local names.
6. **LAYER MAP format**: For each `LAYER MAP <n1> DATATYPE <t> <n2>` / `LAYER <name> <n2>` pair: n1+=20000, n2+=20000, name+=`_CHENXING`. 2115 pairs. DATATYPE/TEXTTYPE unchanged.
7. **LAYER reference propagation**: All references to LAYER physical names elsewhere → +`_CHENXING`. 8011 replacements.
8. **RULE block names**: Rule block names (e.g. `PCM_S_002_00 {`) also get `_CHENXING` suffix → `PCM_S_002_00_CHENXING {`.
9. **Comments/#DEFINE/LAYER/VARIABLE lines**: NOT modified. is_skip logic.
10. **Syntax check**: run `rules_syntax_checker calibreDRC_CHENXING.rule` until "Success" (BLOCKED in-session: env VCO=aok vs required aoi).

## Deliverable
`calibreDRC_CHENXING.rule` — transformed rule file, 36214 lines, all transformations verified (0 missed refs, 0 double suffix, 0 residual placeholders, 0 lost `=`, 0% comment corruption).

## Case synthesis plan (NEXT ROUND)
- **task_id**: EDA-Eval-DesignFlow-CalibreRuleSuffixXform-001
- **domain**: physical_verify
- **mode**: design_flow, entry_point outputs/submit.zip
- **judge_layers**: [L0, L1] (static text transform; L2.live would need calibre rules_syntax_checker with VCO=aoi — check .75 availability, but L1 is clean)
- **assets**: Build a SELF-CONTAINED representative rule file (~250-400 lines) exercising ALL edge cases: LAYER MAP pairs, global derived layers (lowercase def + uppercase ref), PRIMARY derived + PRIMARY ONLY keyword, rule blocks with local vars (A1), local dotted names (P_2d8v.M1), RULE block names (PCM_S_002_00 {}), comments/#DEFINE. NOT the real 1.6MB file.
- **hidden B**: Different representative rule file (different layer names/numbers, different rule blocks) — not just rename.
- **reference solution**: Python script (two-phase placeholder: name→placeholder→_CHENXING; depth/brace tracking; case-insensitive norm() lookup; PRIMARY ONLY negative lookahead; local dotted protection; LAYER +20000; rule-block name suffix). Based on jaychen's gen_final0.py + gen_layer.py + fix_layer_refs.py approach.
- **check.py ≥8 assertions** (independent, each can FAIL):
  1. zip contains calibreDRC_CHENXING.rule + transformer script
  2. transformer script py_compile clean
  3. global derived layer defs have _CHENXING on LHS
  4. global derived layer refs (RHS) have _CHENXING, case-insensitive match (lowercase def → uppercase ref both suffixed)
  5. rule-block local vars (inside {}) UNCHANGED (no _CHENXING)
  6. PRIMARY ONLY keyword NOT suffixed (count preserved)
  7. PRIMARY derived layer refs suffixed
  8. LAYER MAP numbers +20000 (both n1 and n2)
  9. LAYER names +_CHENXING
  10. LAYER refs propagated
  11. local dotted names (P_2d8v.M1) NOT suffixed
  12. RULE block names (PCM_S_002_00) suffixed
  13. comments/#DEFINE lines unchanged
  14. no double _CHENXING (_CHENXING_CHENXING absent)
  15. line count preserved (A input == B output line count)
  16. cross-input guard: check runs on hidden B (different names), not just A
- **negatives** (§4.9 trio + extras):
  - empty stub → FAIL (no output)
  - print-only (echo expected) → FAIL
  - deleted-core (regex sed 's/$/_CHENXING/' naive — suffixes EVERYTHING incl comments/locals) → FAIL local-var + comment conds
  - hardcode-A (hardcode A's specific names) → FAIL cross-input B cond
- **test_rationale**: 16 条断言：①zip 结构 ②py_compile ③global LHS suffix ④case-insensitive RHS suffix ⑤local var unchanged ⑥PRIMARY ONLY preserved ⑦PRIMARY derived suffixed ⑧LAYER MAP +20000 ⑨LAYER name suffix ⑩LAYER ref propagation ⑪local dotted protected ⑫RULE block name suffix ⑬comments unchanged ⑭no double suffix ⑮line count preserved ⑯cross-input B guard

## Status
- DEBT: 1 synthesis pending (deepread complete, next round deliver EDA-Eval-DesignFlow-CalibreRuleSuffixXform-001)
- claim: 1795572780344_xza9c → ledger (covered 566→567)
