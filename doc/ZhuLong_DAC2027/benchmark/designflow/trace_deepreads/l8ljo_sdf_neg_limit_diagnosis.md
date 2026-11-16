# l8ljo — SDF SDFCOM_NL Negative Limit Diagnosis (deepread)

## Trace metadata
- session: 1792112971082_l8ljo.messages.json
- user: e13zhang
- host: 10.129.35.111
- match_count: 17
- domain: digital
- trace size: 43KB / 17 msgs / 1 user turn (repeated 6x + 1 license error)
- agent: lead (poor response)

## User intent (verbatim MSG 0-5, repeated 6x = retries)
```
我的后仿sdf log一直有Warning-[SDFCOM_NL] Negative Limit Not Allowed
/proj/lagat/V0_digital/workdir/tabtao/backend/sdf/func.tt0p8v.ss.cworst_m40c.setup.sdf.gz, 3481808
module: SDFCNQD1BWP40P140LVT, "instance: TOP.u_dram_tester_chip.inst_ft_loopback_rx_wdat_d1_reg_0__3__0_"
  SDF Warning: $recovery/$removal timing checks does not support negative 
  values.
  Please use $recrem timing check instead.
```

MSG 6 (secondary issue, NOT used for case): Cadence VIP license failure (MM_LPD6 checkout fail, Denali fatal).

## Agent response (poor)
- list_allowed_files on /home/e13zhang (depth 2)
- get_agent_policy_status
- search_codebase for SDFCOM_NL/Negative Limit/recrem/MM_LPD6/Denali — ALL TIMED OUT
- read_files: clean_rebuild.sh, dm_mask.py, find_rtl.py, etc. (UNRELATED formal verification scripts)
- read_files: formal_lagat_s2p_adapt/README.md, filelist.f, formal_config.tcl (UNRELATED)
- Agent never actually diagnosed the SDF warning

## Root cause (correct diagnosis)
1. SDF file func.tt0p8v.ss.cworst_m40c.setup.sdf.gz line 3481808 contains $recovery/$removal timing checks with negative values for cell SDFCNQD1BWP40P140LVT
2. At ss.cworst_m40c corner (slow-silicon, -40C, worst-case metal RC), library characterization produced negative recovery (-0.123ns) and removal (-0.045ns) for the async clear path
3. Simulator does not support negative values in $recovery/$removal checks → SDFCOM_NL warning
4. Fix: use $recrem (combined recovery-removal) check which supports negative values, OR use compile flags (+neg_tchk/-negdelay), OR re-characterize library

## Case synthesis
- case_id: EDA-Eval-DesignFlow-SdfNegLimitDiagnose-001
- type: C-A debug-Q&A / analysis-only
- domain: digital
- delivery: sdf_neg_limit_diagnosis_report.json (in outputs/submit.zip)
- A files: 3 (sdf_warning_message.txt, sdf_negative_timingcheck_snippet.txt, sdf_file_header.txt)
- B variant: SDFSEQD1BWP40P140HVT / inst_ft_loopback_tx_adapt_d2 / func.tt0p8v.ff.cbest_125c.hold.sdf.gz / line 2918402
- check: 15 conditions (a-o), k_check=k_rationale=15>=8
- self-verify: ref 15/15 ALL PASS + 5 negs ALL FAIL distinct + E2E jsonl 15/15 PASS
- ledger: l8ljo parked→case
- parked_reaudit: l8ljo→done_r649
