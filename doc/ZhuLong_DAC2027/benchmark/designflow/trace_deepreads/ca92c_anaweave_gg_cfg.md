# Deepread: ca92c — AnaWeave Group Layout cfg merge + dummy verifier

## Trace meta
- sid: `1791532940009_ca92c`
- user: ziyuny @ 10.129.32.190
- mc: 108, size 731KB, 149 msgs, 7 user turns
- tools: editor×30, run_approved_command×26, read_files×15, RAG_MCP_Server__search_apis×3, list_allowed_files×5
- domain: **analog_context** (AnaWeave Group Generator = Empyrean analog layout auto-place for diff pair / current mirror / cascode groups with dummy + guardring)

## User turns (real intent)
- U#0: Skill 写作指南 (meta-skill doc, context)
- U#1: 继续
- U#2: 对差分对，左右两端加上dummy  ← produce intent (add L/R dummy to diff pair)
- U#3: 重新生成一版版图，对差分对，左右两端加上dummy  ← refined
- U#4: 帮我重新生成版图，不额外加dummy  ← revision (remove dummy)
- U#5: 帮我重新生成版图  ← regenerate
- U#6: AnaWeave Group Layout 自动生成 skill doc (the skill being built)

## Assistant produce (key editor targets under /home/ziyuny/.cline/scripts/data/run_cfg/)
1. **train_ddgoa_test_VwlpRefAmpIP_patch.json** — partial override cfg, e.g. `{"PatternCfg":{"DifferentPair":{"Matching":{"Dummy":{"LeftRight":"0"}}}}}`
2. **verify_merged_cfg_VwlpRefAmpIP_dpDummyLR_20261009.py** — reads merged cfg + base cfg, verifies:
   - DP.Matching.Dummy.LeftRight == "1" (LR dummy patch applied)
   - DP.Matching.Dummy.TopBottom unchanged
   - DP.Matching.Style/Mode unchanged
   - CurrentMirror.Matching unchanged
3. **verify_gg_generated_dummies_VwlpRefAmpIP.py** — opens schematic + layout via pyAether, finds layout-only instances (GG-generated dummies), reports with xy
4. **scan_layout_labels_VwlpRefAmpIP.py** — scans layout labels, finds 'O' labels (GG convention: dummy device labels rewritten to 'O'), reports positions
5. **dump_cfg_dummy_sections.py** — dumps DeviceCfg/DummyCfg/LibCfg/TapCfg/PatternCfg.DifferentPair from base cfg
6. **acceptance_gg_run_*.py** — acceptance test wrappers

## cfg schema (group_generator_cfg.json)
```
LibCfg: {libName, cellName}
DeviceCfg: {nmos:{w,l}, pmos:{w,l}}
DummyCfg: {device, labelRewrite:"O"}
TapCfg: {enabled, tapCell}
PatternCfg:
  DifferentPair.Matching: {Style, Mode, Rows, Dummy:{LeftRight, TopBottom}}
  CurrentMirror.Matching: {Style, Mode, Dummy:{LeftRight, TopBottom}}
  Cascode.Matching: {Style, Mode, Dummy:{LeftRight, TopBottom}}
```

## A-faithful judgment
- U#2/U#3 produce = live AnaWeave Group Generator run on cellview (pyAether dbOpenCV, Cst Analysis, Cst Realize All, Save) → **NOT portable** (needs live Aether + cellview lock + project lib)
- Verification scripts (cfg merge verify, label scan, instance diff) are portable IF we synthesize the layout label/instance dumps as text inputs
- → **B-grade synthesized**: extract portable facet = "group_generator_cfg deep-merge + dummy audit (labels + instances) + verdict"

## Synthesis plan (AnalogGroupCfgMergeDummy-001, analog_context, B-grade, L1)
- Tool: `gg_cfg_merge_verify.py --base <base.json> --patch <patch.json> --labels <labels.txt> --layout-inst <li.txt> --sch-inst <si.txt> --outdir <dir>`
- Outputs (5): merged_cfg.json, merge_report.md, dummy_audit.json, instance_diff.json, verdict.json
- A: cell VwlpRefAmpIP, base DP.Dummy.LR=0/TB=0, patch DP.Dummy.LR=1, labels 'O' at L+R of diff pair centroid, layout has GG dummies
- hidden B: cell OtaFoldCascode, base values differ, patch DP.Dummy.TB=1, labels 'O' at top+bottom, different instance names → defeats hardcode of LR/1/cellname/coords
- hidden B2: patch CurrentMirror.Dummy.LR=1 (different section) → defeats hardcode of DifferentPair-only
- 16 conditions a-p: zip no-leak / py_compile / B-run 5 files / deep-merge correct / patch override applied / sibling unchanged / other sections unchanged / merge_report content / O labels found / distribution matches patch axis / layout-only inst > 0 Dum-pattern / all sch in layout / verdict PASS + per-check / B2 cross-input / anti-hardcode (no A literals, B values from B inputs) / determinism 3x sha256
- negatives: empty_shell / hardcode_a / no_deepmerge (shallow) / print_expected / ref_core_deleted / wrong_axis (always LR) → all FAIL
