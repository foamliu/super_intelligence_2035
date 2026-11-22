# Deepread: oj780 — reedchen SPF prune for Dbus post-sim speedup

**Session**: 1795002534044_oj780.messages.json  
**User**: reedchen @ hfeg0pkn002 (also seen on hfeg0pkn001, hfeg0pfn136)  
**Match count**: 185 (cmos:755;netlist:599;schematic:300;pyaether:63;lvs:54;aether:49;analog:32;synopsys:31)  
**Messages**: 120, 893KB  
**Date**: 2026-11-19  
**Domain**: schematic_netlist (netlist/SPF processing)  

## User intent (msg#0, verbatim)
> /proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_top_ChannelLeft_sim/sim_smoke/
> 我现在在这个目录下对整个Channel Left模块执行带RCC寄生信息的后仿，我发现我每次仿真需要4-5小时，非常不利于迭代，请你探索整个环境，给出一些建议能让我优化仿真速度
> 我的仿真目标是对这个Channel的Dbus部分进行仿真，主要的关键子模块的DPhalf DQByte,主要的关键最小子模块的Dbus driver和Dbus Recevier，请你充分探索环境

## Real task
Post-layout (RCC) simulation of ChannelLeft module takes 4-5 hours. User wants to reduce sim time by pruning the 8.1GB StarRC SPF parasitic netlist to only Dbus-related instance prefixes (XI_DPHalf., XI_DQByteLo., XI_DbusPrc., XI7.), keeping RC values verbatim, re-grounding coupling caps with one dropped end.

## Agent deliverable (msg#67-117)
Built `prune_spf.py` (v2, casing-fixed) + `reduce_netlist.py` + `template_ai.sp` + `README.md`:
- **prune_spf.py**: reads StarRC DSPF/SPF, keeps C/R elements whose nets are under retained prefixes, re-grounds coupling caps (one retained + one dropped → far terminal = 0), keeps R-to-ground with retained end, drops everything else, preserves values verbatim, auto-creates output dir
- v1 had a case-sensitivity bug: `n.upper()` vs mixed-case PREFIXES → always False → dropped everything. Fixed in v2 with `PREF_UP = [p.upper() for p in PREFIXES]`
- User iterated: ran script, got FileNotFoundError (output dir missing) → agent added `os.makedirs(..., exist_ok=True)`
- Verified on real 8.1GB SPF: XI_DQByteLo.net305<0>, XI_DPHalf.net309, XI_DPHalf.XI_DPCtrl.XI53.net15 all retained after fix

## Tool chain
- SandBox_MCP_Server__run_code ×26 (Python sandbox)
- list_allowed_files ×14, read_files ×11
- editor ×3, apply_patch ×1, run_approved_command ×1
- RAG_MCP_Server__search_apis ×1, get_api_details ×1

## Synthesis decision
- **Task form**: produce (script deliverable) — agent built a real, checkable Python script
- **Domain**: schematic_netlist (SPF/netlist processing, not layout editing)
- **Reframe**: none needed — the deliverable is already a concrete script with checkable behavior
- **Assets**: synthetic but structurally faithful SPF files (small, ~30 lines) preserving the real DSPF structure (header/*|I/*|NET/.SUBCKT/C/R elements/.ENDS)
- **Hidden B**: different prefixes (XI_Topo./XI_ClkDiv./XI_BiasGen./XI9.), different net names/values
- **Hidden A-prime**: same filenames as B, different content (anti-hardcode cross-check)
- **check.py**: 13 assertions (k=13), runtime on hidden B + A-prime cross-check
- **§4.9 三假**: fake_print_only (no file written) → FAIL ③; fake_core_deleted (keeps all, no pruning) → FAIL ⑦⑩; fake_hardcode_b (hardcodes B output) → FAIL ⑬ (A-prime cross-check)

## Case
**EDA-Eval-DesignFlow-SpfPruneProduce-001** (schematic_netlist, L1, k=13)  
Appended to EDA-Eval-DesignFlow_D.jsonl line 559.  
Self-verified: reference PASS (13/13), negative_selftest 3/3 FAIL.
