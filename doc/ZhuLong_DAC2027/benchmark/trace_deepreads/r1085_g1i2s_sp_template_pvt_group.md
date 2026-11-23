# Deepread — g1i2s (shanliny @ hfeg0plg107, mc=176)

**Session**: `1795165640416_g1i2s.messages.json` (nested under `sessions/1795165640416_g1i2s/`), 221 msgs (111 user / 110 assistant), 833 KB. Retrieved via `scp e0031982@hfeg0plg107:.../1795165640416_g1i2s/1795165640416_g1i2s.messages.json`.

**User**: shanliny. Same user/codebase as y9ed4 (r1069 MosComparaReportGen-001) — but **different topic**: y9ed4 was the *report* side (ΔIdsat/ΔIoff/ΔVth columns), g1i2s is the *deck-generation / PVT-orchestration* side (SP template + netlist grouping). Near-dup checked: distinct deliverable.

**6 user requests in the session** (non-empty user msgs):

1. **[msg 0]** Context summary — continue hardening `mos_compara.py` (fix `round(None)`, out_dir `.resolve()`, Sheet3 large-diff, xlsx/txt format, `--pvt-config` multi-corner batch, `--ncore`/`--nthread`/`--queue`). Big state dump, not a single new request.
2. **[msg 1]** "统一收集+分析大可不必，某个corner仿真完了就先收集+分析就好，收集+分析这一步的log做的简单一点" — per-corner collect+analyze (don't wait for all corners), simplify the analyze-step log. (Assistant: changed Phase B/C to poll each corner's job and analyze on completion; omitted Step C~G verbose headers under `_analyze_only`.)
3. **[msg 37]** **← SELECTED** — "把sp文件也作为一个模板，我在pvt里随时能新建一个新的xxx变量去替代sp文件中的<<xxx>>变量...网表这一项变量作为一个组，组内的网表统一按相同的工艺角、温度进行仿真，但我也可以在pvt中建立多个组，不同组按不同规则仿真". SP template + netlist grouping.
4. **[msg 155]** "你的样本配置文件怎么能失败呢？给我完成更新" — fix sample PVT config.
5. **[msg 195]** "你现在的内建sp模板倒是也给我生成一份到/proj给我看看呀" — dump built-in SP template to /proj.
6. **[msg 199]** "你的pvt模板很好，但你没有在注释里写明在多corner、多dspf条件下的pvt模板该怎么写" — document multi-corner/multi-dspf usage in the template comments.

**Why msg 37 selected**: clean, self-contained, programmable deliverable with a crisp spec (assistant's design in msg 58 / 72). Distinct from y9ed4. Distinct from existing B PVT cases (PvtConfigDeckGen / PvtCornerDeckGen / PvtDeckGen / PvtSimDriverGen / SpDeckPvtMigrate / MultiPvtSpGenBuild — those are about *generating* a deck or migrating corners; this one is specifically about **template `<<var>>` rendering + INI group config + backward-compat TSV**).

**Assistant design (msg 58 / 72)**:
- INI-style `[group_name]` sections; `temp`, `lib_section`, custom `key=value`, multiple `dspf = ` entries.
- `write_sp_file()` rewritten to render from a template with `<<xxx>>` placeholders, taking a `sp_vars` dict.
- `--sp-template` CLI for external template file.
- Old TSV auto-detected → each line = one independent group (backward compat).
- Directory: `results/<group_name>/<dspf_stem>/`.

**Reframe** (case = `EDA-Eval-DesignFlow-SpTemplatePvtGroupRender-001`): standalone Python script `sp_template_pvt_group_render.py <config.ini> <template.sp> <out_dir>` that (a) parses INI-style group PVT config with auto-detected legacy-TSV fallback, (b) renders `<<var>>` SP template per (group, dspf) with built-ins `group_name`/`dspf_stem`/`temp`/`lib_section` + section custom vars, leaving unresolved placeholders verbatim, (c) writes `<out_dir>/<group>/<dspf_stem>.sp` + `manifest.json` with exact top-level keys `{groups, n_groups, n_renders, unresolved_placeholders}`. L1, stdlib only.

**Anti-hardcode hidden B** (5-axis distinct from A): ① 3 groups (rx_loop_lvt / vco_osc / clk_tree_tt) vs A's 2; ② group rx_loop_lvt has 3 dspf (multi-dspf-per-group) vs A's max 2; ③ B-unique custom vars `corner_label`, `osc_trim` vs A's `vdd`/`tran_stop`; ④ temps -55/110/27 vs A's -40/125; ⑤ B template has `<<corner_label>>` / `<<osc_trim>>` / `<<debug_pin>>` placeholders (debug_pin globally unresolved, osc_trim unresolved in 2 of 3 groups, corner_label unresolved in 1 of 3 groups → exercises "unresolved-in-any-group → listed" semantics).

**Self-verify**: REF 14/14 PASS (teeth a–n); 3 negatives each FAIL on a **different** tooth — neg_empty→(a) size stub, neg_print_only→(d) n_groups hardcoded to A's 2 vs B's 3, neg_core_removed→(g) bound `<<group_name>>` left unresolved. 3-seed sha256 deterministic (tooth m). Legacy TSV backward-compat tooth (n) exercised.

**Ledger**: `trace_ledger_B.tsv` claim g1i2s → mark case `EDA-Eval-DesignFlow-SpTemplatePvtGroupRender-001`.
