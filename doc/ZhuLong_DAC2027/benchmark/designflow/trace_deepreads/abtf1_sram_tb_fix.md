# Deepread: 1793241722276_abtf1 (lorikx @ hfeg0pkn004, mc=132)

> Round r299 (2026-11-10): claim + preliminary peek. Full deepread + case build deferred to r300.

## Trace metadata
- session: 1793241722276_abtf1
- user: lorikx  host: hfeg0pkn004 (10.129.2.13-area)
- match_count: 132  (dig=1054, wrong=2 — very clean digital)
- keywords: rtl:611 verilog:427 synopsys:255 systemverilog:16 vhdl:2 lvs:2
- total msgs: 136  real_user turns: 21
- domain: verification (SRAM testbench sim/fix)
- scan source: ssh_eda_search_20261109_224902 (r292 full rescan)

## User turns (first 6, peek)
- U#0: `sim下的仿真 最新一次有10个error，请检查并修改代码`
- U#1: (paste of tb_sram_sp.sv v7.0 header — Testbench for High Density One Port Register File, covers Read/Write/BitWrite/Timing/ColumnRedundancy/TESTMode; Test 15 added)
- U#2-U#5: `继续` (continue nudges)

## A-faithful assessment
- U#0 = **clean produce-task** (提出需求 "fix 10 sim errors" 未给根因 ✓).
- Same SRAM-redundancy project as jzlbn (FsdbVerdiInteg-001, already a case) / im5c1 / xalsb / 9uwcw / 5jgp2 / c6xow / gu1m2 / 6yrpu — lorikx has MANY sessions on this project. abtf1 is a DISTINCT task (TB sim-error fix, not fsdb/verdi integration), so not a duplicate of FsdbVerdiInteg-001. Must confirm during full deepread that the accepted gold differs from existing cases.

## Candidate-pool context (r299)
- This round's filter (mc>=15, dig>wrong, dig>=50, exclude all-4-shard ledger suffixes) → 274 truly-fresh candidates.
- Top fresh: tsn3o/hzyu6 (fernandoy, parked-too-big), r2yjr/pzo6g/rv1g2 (e0039602, netlist/LVS borderline-C), abtf1 (this, claimed), c4vkj (parked, code-merge).
- Confirms r295/r296 finding: shard A clean digital A-faithful produce-tasks are SCARCE — strong-digital marker noisy (verilog keyword often from sim-log content not RTL produce).

## Next round (r300) plan
1. Full deepread: scp full messages.json (136 msgs), parse assistant tool chain + accepted final artifacts (modified tb_sram_sp.sv / sim log showing 0 errors).
2. Decide case design: if gold = modified TB that passes sim → spec-driven-generator pattern (gen_sram_tb_fix.py + spec_a, check.py runs generator on hidden spec_b then statically verifies TB structure + fix sites + anti-hardcode). Match SvTbBugFix-001 pattern (verification TB bugfix).
3. Self-verify: ref PASS + 8+ assertions (k_check>=8, k_rationale==k_check) + negatives + §4.9 fakes.
4. Append A.jsonl, mark abtf1→case, daily report, commit.

## Ledger status
- claimed in trace_ledger_A.tsv at r299 (status=claimed, domain=verification).

## r300 case build (DONE 2026-11-10)
- Full deepread of 136 msgs: USER#1 (idx=0) 逐字「sim下的仿真 最新一次有10个error，请检查并修改代码」= clean A-faithful produce-task (提出需求未给根因 ✓). USER#25 = paste of tb_sram_sp.sv v7.0 header (file context, not a demand). 其余 user turns = "继续" nudges.
- Root cause (assistant tool chain): VCS 默认 V2001 parser 对 sp_sram.v 的 10 个 `output realtime dbg_*` ANSI 端口报 `Error-[IPD] Identifier previously declared` (IPD); 经 /tmp/vcs_ipd_test 最小复现确认 `output realtime`/`output real` 触发 IPD, `output integer`/`output reg` 不触发.
- Fix (3 edits): ① sim/Makefile + inst_sim/Makefile 的 VCS_FLAGS 与 CR_ABSORB_VCS_FLAGS 加 `-sverilog` (切 SV parser 清 10 IPD 错误); ② FAULT_ARGS 由 `+defect_bit` 改 `+defect_bit_left` (默认 + 6 个 fi/cm1 target 调用), 与 RTL defect_bit_left 实现对齐; ③ rtl/sp_sram.v 行 1019-1025 加注释说明 IPD bug + -sverilog fix. 验证: cm1_all 全回归 PASS (compile rc=0, 0 errors).
- Case design (spec-driven-generator, matching SvTbBugFix-001 pattern): **EDA-Eval-DesignFlow-VcsIpdSverilogFix-001** (verification, A-faithful, L1-static, k=14). Generator gen_vcs_ipd_fix.py 按 spec 产 fixed Makefile + ipd_fix_notes.md: 两个编译变量块都插 flag_to_add, FAULT_ARGS 默认+各 fi/cm1 target 都用 fault_args_new, 头注释含 IPD/ipd_error_count/dbg_port_prefix/dbg_port_total. A=spec_a faithful (lorikx/CXMT_SPSRAM_1028_v21/-sverilog/10 IPD/dbg_/30 ports/+defect_bit→+defect_bit_left/6 fi targets); hidden B=spec_b isomorphic (w0047129/CXMT_SPSRAM_2048_v33/14 IPD/tdbg_/42 ports/+defect_bit→+defect_bit_right/cm1_all_64x16).
- check.py 14 条断言 a-n; 自验: gold PASS 14/14 + 4 negatives (noop/hardcode_a/stub/keep_bug) 全 FAIL + §4.9 (a空壳 b print-only c core-deleted) 全 FAIL. 断言闸门 k_rationale=k_check=14≥8 ✓. test_sha8=bcfba184 test==disk check.py ✓.
- 追加 EDA-Eval-DesignFlow_A.jsonl (191→192); ledger mark abtf1→case (case_id=VcsIpdSverilogFix-001). 泄漏隔离 OK (assets 无 check.py/reference/jsonl/test).
