# cyua2 — WTM001 dangling-else mre0 expdata=0 diagnosis

## Trace
- session: `1792993730194_cyua2` (tongfanl@hfhds201, 80 msgs, 688KB, 2026-10-26)
- source: hfhds201 cron blind spot (not in 11-05 summary's hfhds201 entries; found in 11-05 summary on pkn004 with mc=103 but local copy is the cron blind spot)
- spice keywords: 98 (but actual spice tool count low: 1 hspice; dominant: verilog/aether/netlist)
- domain: spice_sim / sim_vector / stimulus extraction

## Conversation flow
- msg#0 U: 「你知道抽激励吗」(Do you know stimulus extraction?) — setup
- msg#20 U: 「看下 tongfanl_workflow.md，重新回答」— context-setting
- **msg#26 U (task turn, A-faithful)**: 「/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/log/stimulus_tongfanl/WTM_fsm_1023/WTM001_normal_check_SC0_WPre_4s4t_WPst_4p5_RPre_2s6t_RPst_4p5_MD_OFF_tCH50_2b16g_BL02_12800_SS_DQSELH.X2P3_12800 帮我看下这个文件夹下抽出的激励，明明xrun.log中gen_wtm_write_data中的dq0 UI1和UI2都有错，为啥mre0的expdata是全0？」
  - User provides specific stimulus folder path
  - States symptom: dq0 UI1/UI2 have errors in xrun.log
  - Asks: why is mre0's expdata all 0?
  - NO root cause given → A-faithful eligible
- msg#27-42: assistant investigates (list_allowed_files, read_files, run_approved_command with python script)
- **msg#42 A (gold standard)**: Complete diagnosis with 6-point evidence chain:
  1. Case runs 2-phase mode (is4phase=0), 4-phase `case(m%4)` code not executed
  2. 2-phase path has **dangling-else** at lines 525-526:
     ```verilog
     if(m % 2 == 0) if(n <= 2) mrdf[n] = 1'b1;  // even UI
     else if(m % 2 == 1)           if(n <= 2) mre0[n] = 1'b1;  // odd UI
     ```
  3. `else if(m%2==1)` binds to inner `if(n<=2)` not outer `if(m%2==0)` → odd-UI mre0 assignment is dead code
  4. xrun.log Write 9: `Error UI mask: 0x899d6e, Error DQ mask: 0x15` (DQ[0] at UI[1], UI[2])
  5. Odd UIs {1,3,5,11,15,19,23} → should set mre0; Even UIs {2,6,8,10,12,16} → should set mrdf
  6. mre0 stays at initial value 0 → expdata all 0 → MRR E0 comparison fails
- msg#43 U: follow-up about framework understanding
- msg#48 U: 「我改过了，你再帮我检查下」— verification after user fix (separate task)

## Gold standard
- Root cause: **dangling-else** in X2P3/DQSELH/SC0 2-phase branch (lines 525-526)
- `else if(m%2==1)` binds to inner `if(n<=2)` instead of outer `if(m%2==0)`
- In 2-phase mode (is4phase=0), odd-UI mre0 assignment becomes dead code
- mre0 stays 0 → expdata all 0

## Case design
- **A (input)**: A_wtm001_normal_check.v (faithful X2P3/DQSELH/SC0 2-phase branch with dangling-else) + A_xrun.log (is4phase=0, Write 9 error injection UI mask 0x899d6e DQ mask 0x15)
- **Hidden B**: B_wtm001_normal_check.v (FIXED: proper begin...end, no dangling-else; X1P6/SC1 macro) + B_xrun.log (different error injection UI mask 0x42468e DQ mask 0x2a)
- **Script**: `diag_wtm_dangling_else.py <wtm.v> <xrun.log> -o out.json`
  - Detects dangling-else pattern (if(outer) if(inner) stmt; else if(...) without begin)
  - Parses is4phase, error UI mask, DQ mask from xrun.log
  - Computes affected UIs, classifies odd/even
  - Determines if mre0 would be all 0 (dangling-else + 2-phase → dead code)
- **Check**: 14 assertions (a-n), including cross-input guard (B → no dangling-else, mre0 not all 0) + A-only leak guard + 3x idempotency
- **Level**: L1 (offline Python analysis of pattern source + log)
