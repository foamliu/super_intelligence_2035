# Deepread: 1792461332006_3mgw6 (shanliny @ 10.129.2.10, mc11, verification)

## Session
- 14 msgs, 4 user turns, 13 attached SV files (~11K lines: tb_sp_sram.v 3930, CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS.v 3578, ref_model.sv 795, strategy_ext.sv 857, monitor.sv 301, interface.sv 318, transaction_ext.sv 510, ...)
- domain: verification (SystemVerilog UVM-style SRAM verification env)

## User turns
- U#0 (1584ch): "这是一个SRAM的sv验证程序，里面的monitor在random策略下有流水线挪位的问题，但在其他策略下就没有，帮我检查下问题出在哪" + 13 attached SV files
- U#1/U#2: "你要修改的东西注明文件，行号" (annotate file/line for changes)
- U#3: "你这改动里面用了好些没被定义过的变量，注意文件之间的调用关系，最后注明你修改的文件、行号" (you used undefined variables, check file call relationships, annotate)

## A-faithful assessment
- U#0 gives SYMPTOM ("流水线挪位") but NOT root cause → A-faithful合格 (agent must diagnose)
- deliverable = modified monitor.sv (added read-addr tracking queue) → real /home/shanliny private path → INFEASIBLE for sandbox → B档合成

## Root cause (agent diagnosed)
strategy_base.sv `execute()` two-stage pipeline ( SAME function call = SAME clock cycle):
  step1: `next_execute(prev_tx)` → drives rdata_valid=1, rdata_expected=REF  (RESPONSE of PREV)
  step2: `execute(curr_tx)`    → drives addr=A_new, ce_n, we_n               (REQUEST of CURRENT)
Both driven via clocking block `output #0ns` (Re-NBA region). Monitor samples in Observed region → sees rdata_valid=1 with addr=A_new (wrong: should be the addr that initiated the read).
- Random strategy: addr sequence unpredictable → mismatch → ERROR
- March C / deterministic: sequential addrs → misaligned addr happens to point to same expected → no error (latent bug)

## Agent fix (monitor.sv lines 218-301)
Added `read_addr_queue[$]`:
  1. On read request (ce_n=0 && we_n=1): `read_addr_queue.push_back(vif.mon_cb.addr)`
  2. On rdata_valid=1: `tracked_addr = read_addr_queue.pop_front()`, use tracked_addr (not sampled addr) for `scb.check_data`
  3. Write recording (ce_n=0 && we_n=0) judged before rdata_valid branch to avoid masking

## Case design: EDA-Eval-DesignFlow-SramPipelineMisalignDiag-001
- domain: verification, L1 (static SV analysis), B档 synthesized
- archetype: sv-pipeline-misalign-detector (NEW)
- deliverable: pipeline_misalign_diag.py (stdlib) — scans SV strategy files, detects two-stage pipeline addr/rdata_valid misalignment (response+request driven in same function call via independent if-blocks vs if/else exclusive)
- A (visible): strategy_buggy_A.sv (sram_strategy_random, execute, independent ifs, rdata_valid/addr) + strategy_clean_A.sv (sram_strategy_march, execute, if/else) + monitor_A.sv (samples, skipped)
- B (hidden): strategy_buggy_B.sv (ddr_strategy_random, drive_cycle, resp_valid/req_addr) + strategy_clean_B.sv (ddr_strategy_seq, if/else) + monitor_B.sv
- core trap: B uses different signal names (resp_valid/req_addr/chip_en/wr_en) + different function name (drive_cycle) vs A (rdata_valid/addr/ce_n/we_n/execute) → defeats hardcoded_A
- detection: response signal (rdata_*/resp_*/_valid/_expected) + request signal (addr/ce_n/we_n/chip_en/wr_en/req_*) both assigned to dotted (vif.cb.X) LHS in same function; control_flow = sequential_if (misaligned) vs if_else_exclusive (aligned)
