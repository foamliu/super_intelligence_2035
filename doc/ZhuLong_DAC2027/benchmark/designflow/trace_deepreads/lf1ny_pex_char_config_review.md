# r700 deepread — lf1ny (PEX char config review)

## Trace
- session: `1792828059985_lf1ny`
- user: `jkxu` @ `10.129.32.80` (`hfhds206`), mc=27
- domain: physical_verify (PEX/LVS char)
- keywords: drc:1125; lvs:424; analog:262; verilog:26; netlist:6; aether:5; pex:4

## User turns (verbatim)
- U#0: `/rundata/drcpa/V0/simdir/verilog/char/qiangw/spf_gen/261019/BCenter_ok4_spf reivew 下这个目录`
- U#8: `lpe 是什么意思`

## Directory contents (real, from trace read_files tool result)
3 files at `/rundata/drcpa/V0/simdir/verilog/char/qiangw/spf_gen/261019/BCenter_ok4_spf/`:
1. **lpe.config_CVPS** (67 lines, 21 keys): SPF Extraction config. `key = value` format, `***` comment lines. project=drcpa, version=V0_20261019, platform=aether, core_num=16, CORNER=TYP, netlist_format=SPEF, top_cell=BCenter, extract_cdlgds=ALL, etc.
2. **hcell.cvps** (520 cells, 7 categories): RC extraction skip-cell list. Format `cellname  //category k-cell, MUST one-to-one map in hcell`. Categories: drcpa_digital(213), drcpa_io(153), stdcells_ac(87), drcpa_analog(27), commonIP_G5CIPanalog(21), drcpa_stdcells(14), drcpa_array(5).
3. **hcells_merge_CVPS** (889 pairs, 1 comment): CCI-LVS hcell mapping. Format `source  target` per line, `//` comment header. 888 identity (source==target), 1 non-identity.

## Assistant behavior
- Listed directory (list_allowed_files), read 3 files (read_files), gave verbal review.
- U#8 asked "lpe 是什么意思" → assistant explained LPE (Layout Parasitic Extraction).

## Reframe (mock-behavioral, per r645-r699 family)
- **New sub-type**: `pex-char-config-review-extract` — structured review extractor for PEX char config directory.
- Real deliverable = verbal review; reframe = pure stdlib `pex_char_config_review.py` producing structured JSON review report.
- Parses lpe.config (key=value), hcell.cvps (cell+category), hcells_merge (source→target pairs), cross-check overlap, stats.
- Output: 6 top-level keys (file_inventory, lpe_config, skip_cells, hcell_merge, cross_check, stats), sort_keys=True, indent=2, deterministic.
- **Distinct vs** r699 PgPlacementPlan=PG device list+placement plan / r698 ErcRulecheckStatsScan=batch erc.rep tree scan+stats / r697 PgDummyFillFlowOrganize=TVF deck structural extract / r695 RsCalcFlowCompare=multi-file .rvn compare+decision = **本例 PEX char 3-file config parse + category aggregate + pair/identity parse + cross-check overlap**.

## Asset A (visible, real files)
- A/lpe.config_CVPS (real, 21 keys, project=drcpa)
- A/hcell.cvps (real, 520 cells, 7 drcpa_* categories)
- A/hcells_merge_CVPS (real, 889 pairs, 888 identity)
- prompt.md + task_brief.md

## Hidden B (anti-hardcode, fully disjoint from A)
- B/lpe.config_CVPS: project=drcoh, platform=virtuoso, core_num=8, CORNER=CMAX CMIN, netlist_format=DSPF (21 keys, all values ≠ A)
- B/hcell.cvps: 40 cells, 5 categories (drcoh_digital:18, drcoh_io:10, drcoh_analog:7, drcoh_array:3, commonIP_G7CIPanalog:2) — names ∩ A = ∅
- B/hcells_merge_CVPS: 50 pairs, 45 identity, 12 overlap with skip_cells

## Hidden B2 (anti-hardcode-B, fully disjoint from B)
- B2/lpe.config_CVPS: project=drphx, platform=aether, core_num=24, CORNER=RCMIN, netlist_format=SPEF
- B2/hcell.cvps: 25 cells, 3 categories (drphx_digital:15, drphx_io:7, drphx_analog:3)
- B2/hcells_merge_CVPS: 30 pairs, 20 identity, 8 overlap
- Defeats neg4 always-pass stub (hardcodes B's drcoh/40/50 → fails B2's drphx/25/30)

## check.py — 19 conditions (a-s)
- a: zip contains script at root
- b: py_compile
- c: B run exit 0 + valid JSON
- d: 6 top-level keys
- e-i: lpe_config B values (project=drcoh, platform=virtuoso, core_num=8, CORNER=CMAX CMIN, netlist_format=DSPF)
- j: skip_cells.total=40
- k: skip_cells.categories (5 drcoh_* cats with exact counts)
- l: hcell_merge.pair_count=50
- m: hcell_merge.identity_count=45
- n: cross_check.overlap_count=12
- o: stats consistency
- p: determinism (2 runs byte-identical)
- q: B2 run exit 0 + valid JSON + 6 keys
- r: B2 project=drphx (≠B drcoh)
- s: B2 skip_total=25 + pair_count=30 (≠B 40/50)

## Self-verify
- gold ref on B: 19/19 PASS ✓
- gold ref on A: works (21 keys, 520 cells, 889 pairs, project=drcpa) ✓
- determinism: 2 runs md5 identical (bea12dde67ff1340cf723fbb6be1a4d2) ✓
- negative_selftest: gold PASS + 4 negs FAIL (c/e/e/r) + 3 distinct first_fail ✓
- §4.9 three fakes: 空壳→c FAIL / 只print A→e FAIL / 删核心→e FAIL ✓
- jsonl round-trip: extract test field → check.py → run on reference_submit.zip → CHECK PASS ✓
- k_rationale = k_check = 19 ≥ 8 GATE PASS ✓
- A∩B∩B2 disjoint: project(drcpa/drcoh/drphx), platform(aether/virtuoso/aether), cells, categories all disjoint ✓
