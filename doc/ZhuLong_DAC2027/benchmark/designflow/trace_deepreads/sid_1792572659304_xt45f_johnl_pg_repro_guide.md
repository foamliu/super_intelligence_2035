# Deepread — sid 1792572659304_xt45f (johnl @ hfeg0plg99) — PGReproGuide

## trace metadata
- session: `1792572659304_xt45f` (269 msgs, 1.43 MB), agent=lead, zhulong/cline
- user: johnl, host: hfeg0plg99, match_count=183 (tools: 1391 innovus + 147 netlist + 20 synthesis + 11 schematic + 2 pyAether + 2 hspice + 1 dbGet + 1 calibre)
- real working dir of the *recovered* flow: `/home/johnl/innovus_verify/` (design `addr_to_rowcol_v7`, cxmtG5_CIP DRAM process)

## real user intent (逐字)
- USER#0: `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_regi  帮我总结下这个对话的到进展 并做一个指导我复现的pdf 工具如何启动啊 关键到文件在哪里啊这些`
- USER#24 (correction): `不对是另一个正在运行的会话 你要恢复里面的历史消息 然后做我上面的指令`
- A-档 seed rule check: USER#0/#24 提出目标 (summarize + repro guide PDF: tool startup + key files), does NOT give root cause or fix → A-档 eligible.
- USER#76/165/245/248/251/254 = "继续" (continue). USER#216 = "有很多空行啊 算了给网页html吧" (formatting nit, not root cause).

## what the assistant actually did
1. Resolved typo `dc_addr_to_regi` → `dc_addr_to_region` (a Design Compiler synthesis project).
2. Per USER#24, scanned `~/.cline/data/sessions/` to find the *live, running* session → `1792493511731_624js` (632 msgs, mtime updating in real time). Dumped its full history to `/home/johnl/live_session_dump.txt` (497 KB) just before that session was auto-compressed (632→75 msgs).
3. The recovered 624js session = a real **Innovus PR → StarRC SPEF extraction → SPEF back-annotation → PrimeTime STA** flow for `addr_to_rowcol_v7` (107 cells / 116 nets). Innovus PR itself was done in an earlier session `mt7ua` (10-20 09:30, "使用innovus完成此电路的版图").
4. Read the key artifacts: `tcl/pr2.tcl`, `tcl/pr_starrc.tcl`, `tcl/pt_sta.tcl`, `data/starrc.final.cmd`/`starrc.f12.cmd`, `data/mmmc_pr.tcl`, `data/mapped.sdc`, `run_innovus_pr2.sh`, `run_starrc_final5.sh`, `run_pt.sh`, `data/pt_timing.rpt`, `data/addr_to_rowcol_v7.star_sum`, `data/pt_viol.rpt`, `data/sxf12.log`, `pt_shell_command.log`, `parasitics_command.log`.
5. Built a multi-page CJK reproduction-guide PDF via matplotlib + DroidSansFallback font (`/home/johnl/addr_to_rowcol_v7_repro_guide.pdf`): cover, conversation-progress timeline, tool-chain startup, key-file map, etc.

## real flow facts (extracted from the artifacts; baked into synthesized asset A)
- design: `addr_to_rowcol_v7`; process: `setDesignMode -process 10`
- toolchain: Innovus (Cadence INNOVUS231), StarRC (Synopsys W-2024.09, StarXtract), PrimeTime (U-2022.12-SP5, pt_shell)
- stage order: PR (Innovus: init_design→floorPlan→addRing vcc!/vss!→placeDesign→routeDesign -globalDetail→writeNetlist postroute.v→defOut routed.def→saveDesign .enc) → StarRC (StarXtract starrc.f12.cmd, EXTRACTION RC, NETLIST_FORMAT SPEF → routed.spef) → SPEF back-annotate (PT read_parasitics -format spef) → PT STA (read_db/read_verilog/current_design/read_sdc/report_timing/report_constraint)
- timing: WNS = -0.04 ns (VIOLATED), TNS = -0.17 ns, 6 violated endpoints (row[1] -0.04, col[2] -0.03, col[4] -0.03, row[0] -0.03, col[3] -0.02, col[0] -0.02); critical path N[4](in)→row[1](out), arrival 0.54 ns, required 0.50 ns, 13 logic levels
- SPEF back-annotation: 116 nets annotated, 1993 capacitances, 1928 resistances (coverage 116/116 = 100%)

## why A-档 disqualified → B-档 synthesized L1-boundary
- A-档 gold = the actual PDF + the live `innovus_verify/` tree, both on intranet hfeg0plg99. `.75` sandbox cannot reach them; live Innovus/StarRC/PrimeTime cannot be re-run there with the real design data.
- → B-档 synthesized: assets faithfully mimic the real flow's structure & numbers (A = addr_to_rowcol_v7 / WNS -0.04 / 116 nets); hidden B/B2/B3 use different design names, process nodes, timing numbers, and stage compositions (B2 drops StarRC entirely; B3 is a clean/no-violation flow) to beat hardcoding.

## case design (EDA-Eval-DesignFlow-PGReproGuide-001, domain pg_layout)
- candidate: `repro_guide_gen.py --indir <dir> --out repro_guide.json` — generic offline parser of scripts+Tcl+reports+transcript → structured repro guide JSON.
- check.py: 14 independent assertions [a]–[n] (k_check=14), runs candidate on hidden B/B2/B3 + visible A, re-derives every fact independently from each hidden input's source files. Covers: zip/compile, JSON shape, stage ordering & field completeness, tool/binary matching, timing re-parse (wns/tns/arrival/required/levels/violators), SPEF coverage re-parse, design-name consistency across 3 files, missing-stage handling (B2), clean-flow handling (B3), A↔B structural guard (anti-fake_print_expected), determinism, process_node, file_map completeness, tool_versions.
- self-verify: ref PASS 14/14 ✓; 4 negatives (fake_empty / fake_print_expected / naive_always_4stages / naive_ignore_spef) all FAIL ✓ (NEG_RC=4); §4.9 (a)(b)(c) all FAIL ✓.

## orthogonality vs prior shard-C pg_layout cases
- AutoCellClassify / PFMergeAudit / PFMergeDupAudit / RNodeCovAudit / RsCalcCkPtAudit = PG cell-merge / node-coverage / resistance-calc audit tasks.本案 = **digital backend flow reproduction-guide synthesis** (Innovus+StarRC+PT orchestration), a distinct pg_layout sub-topic (flow reproduction / handoff documentation), fresh user johnl, fresh trace xt45f.
