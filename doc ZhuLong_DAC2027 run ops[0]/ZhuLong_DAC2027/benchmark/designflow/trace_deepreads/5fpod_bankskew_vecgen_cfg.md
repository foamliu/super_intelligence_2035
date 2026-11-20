# Deepread: 5fpod (tongfanl@hfeg0plg72/.75, mc134, digital) — bankskew vecgen config produce-task

**Session**: 1792222798503_5fpod, /home/tongfanl/.cline/data/sessions/1792222798503_5fpod/1792222798503_5fpod.messages.json (630KB, 56 msgs)
**User**: tongfanl | **Host**: hfeg0plg72 (session file on .75=hfhds201/10.129.32.75) | **Scan**: r292 ssh_eda_search_20261109_224902, mc134
**Keywords**: verilog:1216 analog:147 (dig-dominant, low analog) — clean digital
**Domain**: digital (DDR6 stimulus vector generation config)

## User turns (A-faithful selection)
- USER#1 (msg0): "学习一下抽激励的脚本 /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen>g runsti/gen_stimulus_chao 以及其调用的配置文件 .../runcfg/run_random_cfg" — LEARN/STUDY (analysis, NOT produce; not used as task)
- **USER#2 (msg24) [A-faithful produce-task, SELECTED]**: "依据这个之前抽出来的激励结果文件夹:/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/log_2026_Vcap/Designer/1014_bankskew 帮我配置一下抽激励的脚本和配置文件" — produce-task (configure stimulus scripts+config from a reference results folder); user gives a goal, NOT root cause or fix ✓ A-faithful
- USER#3 (msg48): "抽完了，对比一下 .../1017_bankskew/vecgen.rpt .../1014_bankskew/vecgen.rpt" — COMPARE (user RAN the configured scripts → 1017_bankskew produced → ACCEPTED the deliverable; then asked to compare 1017 vs 1014)

## Assistant produce chain (msg25-47)
1. list_allowed_files + read_files on 1014_bankskew/{sim.saved, vecgen.rpt, runCmd, .run} → reverse-engineer the original config params
2. Derived params (msg33/msg47): Pattern=Golden009_Multi4bank_bankskew, Speed=11600, Width=X2P3, Port=SC0+SC1 (each 8 cases), MR_Settings=WPre_4s4t_WPst_2p5;RPre_2s6t_RPst_0p5;RPs_0;CAParity_DIS;CMDBLK_DIS;MD_16b, Timing=tCH50, Bank=8 groups×4bank (BL0246/BL1357/BL8ace/BL9bdf/BLgikm/BLhjln/BLoqsu/BLprtv, prefix 2b16g_), Corners=TT0.92V25C;SS0.92V-40C;SS0.92V130C;FF1.23V-40C;FF1.23V130C, defines="ZERO_PAD Short_SKEW", tool=ncverilog (runCmd --tool ncverilog, NOT default xrun), log_dir_fresh=log_2026_Vcap/Designer/1017_bankskew
3. Created (editor, msg37) under /home/tongfanl/bankskew_gen/:
   - runcfg/run_bankskew_cfg (3517 chars): header + 16 rows = 2 ports × 8 bank_groups cross-product, columns PatternName/Speed/Width/Port/MR_Settings/Timing/Bank/Corner
   - runsti/gen_stimulus_bankskew (1107 chars): d6vecgen -p dscqa -v V0 -f runcfg/run_bankskew_cfg -d "ZERO_PAD Short_SKEW" -t ncverilog -l log_2026_Vcap/Designer/1017_bankskew (default fresh dir, + 2 commented alternatives: write-to-1014 / multi-thread -i 4)
   - copy_to_vecgen.py (594 chars): shutil.copyfile runcfg+runsti → vecgen_root, SKIP-if-exists, chmod 0o775
4. run_approved_command copy (msg42) → /proj/dscqa EACCES (work user lacks write). Files stay in /home/tongfanl/bankskew_gen/, user copies manually.
5. msg47 delivery summary (reverse-engineering evidence table) + file verification.

## Gold deliverable (user-accepted)
3 files under /home/tongfanl/bankskew_gen/ (readable on .75, match editor tool_use content):
- runcfg/run_bankskew_cfg | runsti/gen_stimulus_bankskew | copy_to_vecgen.py
User ACCEPTED (ran scripts → 1017_bankskew results → compared 1017 vs 1014).

## Case design
- ID: EDA-Eval-DesignFlow-BankskewVecgenCfg-001 | domain=digital | track=faithful | level=L1-static
- Pattern: spec-driven-generator (matches CkmuxXlsxExport-001/SvTbBugFix-001/DftTestmaxLaunchFlow-001; r297 blocker_resolution_note: openpyxl/infra-blocker reusable reframe)
- Deliverable: gen_bankskew_cfg.py (stdlib generator) + spec_a.json → emits 3 config files
- A=spec_a (1014_bankskew parsed params) faithful; hidden B=spec_b isomorphic (3 ports × 4 bank_groups = 12 rows vs A's 2×8=16; different pattern/speed/width/MR/timing/corners/defines/tool/log_dir)
- check.py runs gen on hidden spec_b, statically verifies 3 emitted files (16 conds a-p): zip+py_compile+3 files produced+cfg header+row count+PatternName/Speed/Width/Port cross-product/MR_Settings/Timing/Bank cross-product/Corner+script d6vecgen flags+fresh log_dir anti-overwrite+copy helper SKIP+chmod+anti-hardcode-A+3-seed determinism
- Raw 1014_bankskew ref files (sim.saved/vecgen.rpt/runCmd/.run) included as assets context (faithful to real folder user pointed at)
