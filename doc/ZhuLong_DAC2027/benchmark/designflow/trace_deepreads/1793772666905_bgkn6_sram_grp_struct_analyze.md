# Deepread: 1793772666905_bgkn6 (lorikx @ hfeg0pkn001, mc54)

- **agent**: lead (zhulong), model deepseek-v4-flash, 83 msgs, 565KB
- **user**: lorikx — heavy digital/SRAM-synthesis user (prior cases: CrEdgeAlignFix r182, etc.)
- **session path**: /home/lorikx/.cline/data/sessions/1793772666905_bgkn6/1793772666905_bgkn6.messages.json

## USER#0 (verbatim, A-faithful-eligible need-stating turn)
> 请模仿对话(1793618006543_5qlqi)的内容，整理该路径下的SramEDABistGrp2

- Not a rootcause/fix turn → valid A-faithful candidate. (本 case 实做 B档 synthesized, 因 hidden-B 结构差异在 A-faithful 下偏弱；A 档留作未来候选。)

## Real task flow (assistant)
1. Read prior conversation 5qlqi (the template) — 5qlqi organized SramNoBistGrp3 (Grp3): structure.md + SVG + _draw_structure.py.
2. Read target SramEDABistGrp2_modified.v (1179 lines, 27 SRAM macro instances) + Grp3 reference files (structure.md / _draw_structure.py / SVG) as format template.
3. Extracted 27 instances, selection logic decomposition: `decoder #(.WIDTH(5)) Inst_slect` → `sel_iN = inst_selection[N]` (one-hot) → `en_iN = SELALL | (sel_iN & sel_g2)` (enable gating) → `vmuxNNto16 wsel_mux_iN` (word select) → `wsmux27to1` (top mux).
4. Produced _draw_structure.py → SramEDABistGrp2_structure.svg (10673 bytes) + SramEDABistGrp2_structure.md.
5. Second phase: compared SramEDABistGrp2.v (original) vs rtl/SramEDABistGrp2_DFT.v → SramEDABistGrp2_DFT_diff.md. Final conclusion (msg82): "DFT 版 = 原始版 + 每实例独立的 BIST 写时钟通路; 新增 mbist_mode 和 27 个时钟口 CLKA_00~26; 27 个 CKMUX 2选1 时钟切换; 45 个差异块, +139/-58 行 (1179→1260)."

## Real artifacts (on hfeg0pkn001:/home/lorikx/MY_SANDBOX/TV1_top/)
- SramEDABistGrp2/SramEDABistGrp2_modified.v (61809B, 1179 lines) — A target
- SramEDABistGrp2/rtl/SramEDABistGrp2.v + SramEDABistGrp2_DFT.v (65260B each) — original + DFT pair
- SramEDABistGrp2/SramEDABistGrp2_structure.md + .svg + _draw_structure.py + SramEDABistGrp2_DFT_diff.md — agent products (gold)
- SramNoBistGrp3/SramNoBistGrp3_modified.v (61265B, 1157 lines) — Grp3 (template module; reused as hidden B for this case)

## Case built: SramGrpStructAnalyze-001 (B档 synthesized, L1-static, digital)
- **A (SUT sees)**: SramEDABistGrp2_modified.v + synthesized prompt (analyze SRAM group RTL structure → submit analyze_sram_grp.py + structure.json/md). SUT does NOT see Grp3 or the 5qlqi template.
- **Hidden B (check runs on, SUT doesn't see)**: SramNoBistGrp3_modified.v — structurally different (NoBist: no JTAG/BIST ports, 28 vs 44 ports, sel_g3 vs sel_g2, 1158 vs 1180 lines, module name SramNoBistGrp3 vs SramEDABistGrp2). Instance count same (27) but value-discriminators differ strongly.
- **Deliverable**: submit.zip/analyze_sram_grp.py (generic Verilog structure extractor) + structure.json + structure.md.
- **check.py**: 18 conditions (a-p2,q); subprocess runs candidate on B; validates structure.json facts re-derived from B; anti-hardcode guard runs candidate on A and verifies A-facts match A-gold (SramEDABistGrp2/sel_g2/44/jtag=true) — proves candidate is generic, not hardcoded. Self-contained (A/B base64-embedded).
- **Self-verify**: ref PASS (18/18); 5 negatives (naive_empty/hardcoded_A/hardcoded_B/print_expected/core_deleted) all FAIL; §4.9 (a)(b)(c) three-fake all FAIL; negative_selftest PASS.
- **k_check = k_rationale = 18** (≥8 gate PASS).

## Why B档 not A档
A-faithful would use verbatim USER#0 ("请模仿对话(5qlqi)...整理SramEDABistGrp2") + bundle 5qlqi/Grp3 template as asset. But Grp2 and Grp3 share identical instance count (27) and selection cells; the structural difference is only in ports/module-name/line-count (NoBist vs EDABist). For A-faithful the SUT would see Grp3 (as the mimic template), leaving no unseen hidden B with a different instance count. B档 synthesized lets the SUT see only Grp2 and keeps Grp3 fully unseen as hidden B, with the value-discriminators (module_name/group_select/port_count/jtag/line_count) providing strong anti-hardcode signal.
