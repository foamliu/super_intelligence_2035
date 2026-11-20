# Deepread: vi5wa — netlist mod splice by netlist order

- **trace**: e0039602 @ hfeg0pkn002 (10.129.2.11, autofs via 10.129.8.234), session `1793069585233_vi5wa.messages.json`, mc541, 1.96MB, 345 msgs, 23 user turns
- **keywords**: verilog:1075;netlist:1049;lvs:145;systemverilog:84 → clean A-dominant digital (netlist/verilog twin-stack)
- **project**: verilog_lib_trans_v1.2 (same project family as r399/r419/r428/r436, DIFFERENT subtask/deliverable: this one = splice converted modules BACK into netlist by netlist order; r436/kdjt3 = remove a wrong catalog entry)
- **A-faithful**: U#22 (MSG 260) is a clean produce-task ("modify extract_converted_sv.py to read result_map + netlist, splice converted modules in netlist order/format, keep header/inter-module text/unconverted modules verbatim, add --only-converted mode") — user does NOT give root cause → A-faithful 合格. But deliverable = modified private `extract_converted_sv.py` at `/home/e0039602/Documents/verilog_lib_trans_v1.2/` → A-faithful INFEASIBLE (private path, report files now DELETED from .75 fs) → **B档 synthesized**

## User turn (U#22, MSG 260) — the produce-task
"修改 extract_converted_sv.py：result_map 是按 module 组织的，里面有 module 名、行号、完整原文、cell 转换。现在要按原始网表的顺序，把有转换结果的 module 替换进去，网表里其它的 module（没转换结果的）和头部、夹注都保留原样。再加一个 --only-converted 模式：只输出有转换结果的 module，但顺序还是按网表顺序，网表头部保留，不输出没转换 module 的原文。result_map 里有但网表里没有的 module（孤儿）不要写进输出。注意识别 module/endmodule 要忽略注释里的字样（// 行注释和 /* */ 块注释），别把注释里的 endmodule 当成 module 的结束。"

User does NOT state: (1) which modules are converted (that's data-driven from result_map), (2) the exact comment-trap edge cases (those are bugs the agent HIT in development), (3) error/usage behavior. Agent must infer the full spec + edge cases.

## Agent tool chain (deepseek, multi-tool, 23 user turns total but U#22 is the splice task)
1. editor: writes extract_converted_sv.py — parses result_map (celldefine blocks) + netlist (module/endmodule scan), splices in netlist order
2. run_approved_command (python-runner): runs script on real result_map_20261028_113301_cc80.txt + netlist.v
3. **BUG 1**: `re.match` for module header → misses `module` not at line start (vs `re.search`). Fixed.
4. **BUG 2**: depth counter exits on port-list close paren — naive `depth--` on `)` triggers early endmodule detection inside port list. Fixed by tracking `module` ... `endmodule` directly (not paren depth).
5. **BUG 3**: naive `text.find('endmodule')` catches `endmodule` inside `//` line comments and `/* */` block comments → splits a module mid-body. Fixed by comment-aware scan.
6. Verification: `python3 -c "compile(...)"` → SYNTAX OK; diff output vs expected → module count + order correct.

## Key reusable logic (the synthesized tool)
- Parse result_map: split on literal `# ---- module:` header; per entry extract name (token before `(`) + celldefine block (`celldefine` ... `endcelldefine`); ignore `## 完整原文` section (do NOT emit raw)
- Parse netlist: **comment-aware** module scan — strip `//` line comments and `/* */` block comments (state carried across lines) BEFORE looking for `module <NAME> (` / `endmodule`; preserve original raw lines for output
- Preserve netlist header = everything before first real module-start line
- Default mode: walk netlist modules in order; if name in result_map → emit celldefine block, else emit raw module block; inter-module text (comments/timescale/blanks) emitted verbatim
- `--only-converted` mode: only emit converted modules (in netlist order) + header; skip unconverted raw
- Orphan entries (in result_map but not netlist) → NOT emitted
- Determinism: pure function of inputs, no hash-order, no dict-order dependence (use ordered parse)

## Comment-trap (key discriminator — 3 traps)
trace hit BUG 3 (naive `find('endmodule')` catches comment endmodule). B hidden input embeds 3 comment-boundary traps:
1. **line-comment trap**: `// module FakeCMNT (Y, A);` in header comment block — naive `re.search(r'module \w+\s*\(')` would parse `FakeCMNT` as a real module
2. **block-comment trap**: `/* ... module FakeBlk (Y, A); ... endmodule ... */` — naive scan would split here too
3. **fake-endmodule trap**: `and2BBx1` body contains `// the token endmodule below is inside a line comment` AND `/* and this endmodule is inside a block comment */` — naive `find('endmodule')` splits and2BBx1 mid-body, leaking its raw `ntn/ptn` instances into the next module's region

A comment-aware scanner (strip // and /* */ before keyword match) handles all three; a naive substring/regex scanner fails. → B hidden input is structurally different from A (A has 0 comment traps).

## Cross-input guard (A vs B differ — defeats hardcoded_A / print_only)
- A netlist: 4 modules (invCS/nand2CS/aoi21DSx1/oai22LLx1), `timescale 10ps/10ps`, tRise = 20*`CDLYW
- B netlist: 5 modules (invBBx1/nand2BBx1/and2BBx1/oai22BBx1/triBBx1), `timescale 1ns/1ps`, tRise = 12*`CDLYW
- A result_map: 3 converted + 1 orphan `zzOrphanA`
- B result_map: 3 converted + 1 orphan `barOrphanB`
- check.py (o) cross-input guard: B run must have B markers (1ns/1ps, tRise=12, invBBx1) and NOT A markers; A run must have A markers and NOT B markers

## Synthesis plan → NetlistModSplice-001 (digital, L1, spec-driven, B档)
- deliverable = `netlist_mod_splice.py` (pure stdlib, CLI `<result_map> <netlist> <out> [--only-converted]`)
- A = netlist_A.v (4 modules, 0 traps) + result_map_A.txt (3 converted + 1 orphan)
- B hidden = netlist_B.v (5 modules, 3 comment traps, timescale 1ns/1ps) + result_map_B.txt (3 converted + 1 orphan barOrphanB, tRise=12*`CDLYW) + hidden_manifest.json
- check.py 17 conditions (a-q): zip-contains-script / runs-nonempty / header-verbatim / module-sequence / converted-spliced / unconverted-raw / inter-module-text / 完整原文-not-leaked / orphan-excluded / Fake-modules-not-parsed / and2BBx1-trap-single-module / only-converted-sequence / only-converted-header / only-converted-no-unconverted / cross-input-guard / determinism-3-runs / too-few-args-error
- independent oracle: **string-method line-scan** (partition/startswith/find, comment-aware via `active_lines()`) — structurally different from ref's **regex finditer** module-header parser, so a candidate sharing a bug with either implementation is caught by the other
- negatives: naive_empty (FAIL b) / naive_print hardcoded B-default (FAIL l) / naive_core_removed naive `find('endmodule')` no comment-awareness (FAIL m) / naive_hardcode_a (FAIL c)

## Determinism verified
3 runs of ref on B default → identical md5 `b68a476f481babae9a3128cd5b0797ca`. check.py (p) re-verifies at grade time.

## Verification
- ref passes check 17/17 (CHECK RESULT: True)
- 4 negatives all FAIL (NEG_RC=0): empty→(b), print→(l), core_removed→(m), hardcode_a→(c)
- embedded test (from A.jsonl `test` field, written to real file) passes on ref → jsonl entry integrity confirmed
