# r953 deepread — qqw9t schematic schCheck/overlap audit (DEBT, ready-synth)

**Session**: 1787880772534_qqw9t.messages.json
**User/Host**: junxu @ hfeg0pjn200 (10.129.40.209) — also on hfeg0pkn005/hfeg0plg79/hfeg0plg17
**mc**: 640 (layout_virtuoso, kw: virtuoso:1446/schematic:505/dbopencellviewbytype:234/cellview:131/cadence:90/cmos:66/drc:21)
**Ledger**: C claimed r953 → parked DEBT (fresh; not in any of 4 shard ledgers; 4-shard union 4049 slugs)
**Msgs**: 342 total, **1 user message** (single-shot), 171 assistant blocks, tools: run_commands×129 / editor×24 / read_files×15 / skills×1 / search_codebase×1
**Status**: DEBT — deepread done, ready-synth, ETA 1 round

## Real task (single user msg)

> /virtuoso-cli 在 iejoad_work 里实现一个 cli_fifo2 的电路，该电路需要实现一个 8bit 4 深度的 FIFO，使用 stdcells_am 里的 cell 来实现。电压域为 vdd2c。注意器件摆放合理性，总体来说从左到右为输入到输出，器件密度均匀，不可出现大片空白区域，也不可以靠太近，不可滥用 net name stub 桥接。可以合并的 net 优先考虑 bus 总线，可以合并的 instance 优先考虑 vector instance

## Assistant work chain

1. discover virtuoso-cli skill (`/home/junxu/Agents/virtuoso-cli/scripts/virtuoso-cli.sh`), daemon ports (50063/47096/46644), cli-reference.md
2. set OA env (`OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x`, OA_HOME, OA_LIB_PATH) — RHEL 8.10 not recognized by OA
3. write `build_fifo2.py` — generates SKILL code: dbOpenCellViewByType, place 73 stdcells_am instances (DFF/MUX/INV/...), wire nets (bus DIN<7:0>, wrrow_en{i}, din_g{i}), schCheck, dbCreateProp voltageDomain=vdd2c
4. iterative editor fixes to build_fifo2.py (wiring3 data-register/read-MUX wiring, schCheck call signature `schCheck(cv)~>messages`, dbCreateProp arg order)
5. write `verify_fifo2.py` — verify schematic quality
6. final: 73 instances, 98 nets, 8 terminals; schCheck = **11 errors (wire shorting) + 5 warnings (instance overlaps)**; vdd2c property added; schematic+symbol views confirmed

## Key artifacts (for fixture)

- `build_fifo2.py` (generator): instance placement coords (X_DGT, Y_DATA[i], X_*), wiring functions (wl=wire-line), schCheck invocation, voltageDomain prop
- `verify_fifo2.py`: verification script
- schCheck result shape: `list(nErrors, nWarnings, messages_str)` — messages contain wire-short + instance-overlap diagnostics
- Final stats: 73 insts / 98 nets / 8 terms / 11 errs / 5 warns

## Cross-shard / duplicate check

- 4-shard ledger: qqw9t only C (fresh, now parked DEBT)
- Same user/project as fbz0w (r947 StdcellLibFifoSuitClassifier, junxu@hfeg0plg79 mc=1202) and sstk3 (r945 PowerMapNetExprGen, junxu@hfeg0plg79 mc=1606) — **same cli_fifo2 FIFO project, different host/session**
- BUT reframe angle is **orthogonal**:
  - fbz0w = stdcell library enumeration + FIFO-role classification (lib scan before build)
  - sstk3 = power-mapping net-expression generation (vdd2c→net expr)
  - qqw9t = **schematic schCheck error/overlap audit** (post-build placement quality check) — distinct sub-type, first of its kind

## Synth direction (reframe 档 B, offline pure-stdlib)

**Sub-type**: `schematic_schcheck_overlap_audit` (first case)
**Agent writes**: `schcheck_overlap_audit.py` (pure stdlib)
**Input fixtures**:
- `instances.tsv` — instance placement: inst_name, cell_name, x, y, orient, width, height (e.g. 73 rows for env_A)
- `schcheck.txt` — raw schCheck output: nErrors, nWarnings, message lines (wire-short lines name shorted nets; instance-overlap lines name inst pairs)
- `netlist.tsv` (optional) — net→inst-pin mapping for short detection
**Output JSON**:
```
{
  "design": "...",
  "summary": { "total_instances", "total_nets", "n_errors", "n_warnings", "n_wire_shorts", "n_overlaps", "n_other" },
  "errors": [ { "type": "wire_short"|"instance_overlap"|"other", "raw": "...", "net"|"inst_pair": [...], "severity" } ],
  "overlap_pairs": [ { "inst_a", "inst_b", "cell_a", "cell_b", "ax","ay","bx","by", "overlap_area", "manhattan_dist" } ],
  "shorted_nets": [ { "net", "driver_count", "suspect_insts" } ],
  "fix_priority": [ ... sorted by severity+area ],
  "placement_quality": { "density_uniformity", "empty_regions", "crowded_regions", "left_to_right_flow_ok" }
}
```
**check.py assertions (k≥8)**: ① py_compile ② no-arg exit0+JSON+顶层键 ③ 反硬编码 (env_B 名全现, env_A 名零泄漏) ④ summary counts correct (n_errors=env-specific, n_wire_shorts, n_overlaps) ⑤ overlap_pairs manhattan_dist computed correctly + bbox overlap area ⑥ shorted_nets driver_count logic ⑦ fix_priority sorted by severity ⑧ placement_quality density/uniformity metric ⑨ 反 delete-core (非空 errors/overlap_pairs) ⑩ 3-seed 字节级一致
**env_A**: 73 insts FIFO (from qqw9t), 11 errs/5 warns, specific net names (DIN<7:0>, wrrow_en0..3, din_g0..3)
**env_B** (hidden, inline in check.py): different design — e.g. 16bit 8depth FIFO, 120 insts, 18 errs/9 warns, different net names (DATA<15:0>, rd_sel0..7, dout_g0..7) — A/B 名/gds 全不同
**test_rationale**: `k 条断言：①…②…` (k matching assertion count)
**3 negatives**: naive_stub (empty output), hardcode_enva (env-A names leak / env-B missing), delete_core (drop overlap-pair logic)
**§4.9 three-fake**: (a) 空壳 (b) 只 print (c) 删核心 — all FAIL distinct

## Self-verify plan

ref solve.py PASS k/k + 3 neg FAIL distinct + §4.9 三假 FAIL distinct + 3-seed (PYTHONHASHSEED=1/2/3) 字节级一致 + E2E (jsonl.test 提取→check on ref submit.zip) PASS

## Next-round actions

1. `trace_ledger.py --shard C mark --session 1787880772534_qqw9t.messages.json --status claimed --force` (revive from parked DEBT)
2. Build fixtures from this deepread (instance coords + schCheck msg format are in build_fifo2.py patterns shown in MSG#304/310/318/332)
3. Synth per §Synth direction, self-verify, append C.jsonl (589), mark `case`, commit both repos
