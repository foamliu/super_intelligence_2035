# Deepread: y6liq (t0002614 @ hfeg0pkn001, mc150) — SPICE testbench structure analysis

## Trace identity
- session: 1793065763835_y6liq.messages.json (937KB, 138 msgs, 82 user / 56 assistant)
- user: t0002614 (CharlesC), host hfeg0pkn001 (10.129.2.10)
- scan kw: netlist:907; schematic:141; synopsys:112; hspice:43; transistor:40; aether:27; verilog:14; cmos:13
- domain assessment: eda_other (SPICE netlist structure analysis — generic EDA parsing, shard A owns eda_other)

## User turns (clean needs)
- USER#0: "analyze and detailed explain the structure of the netlist" + attached TPC_Case1_Group1_BL4_28_D0_SenB_toc_1n.sp  ← A-faithful task pick (clean need, rule2 OK)
- USER#5: "now you can access all files in path /rundata/sim_cloud/CRG/CharlesC/test ... try to explain the netlist again" (grants file access — premise, not A pick)
- USER#46: "how to fix the bugs in simulation?" (clean need but depends on sim errors = premise)
- USER#66: "There are still errors including some about 'pvwlp'. Fix them..." (gives root cause → rule2 弃)
- USER#105: "have you fixed the bugs" (follow-up)
- USER#137: "wave" (open waveform — final)

## Gold (self-contained, from .sp alone = ASSISTANT#4 first analysis)
ASSISTANT#4 produced a structural analysis of the top-level .sp netlist (without remote includes):
- Executive summary: DRAM sense-amplifier margin testbench, HSPICE syntax, FineSim target
- Filename decode: TPC_Case1_Group1_BL4_28_D0_SenB_toc_1n
- Block-by-block layout: *** PVT *** (7 .lib), *** ADD finesim option *** (.inc+2 .option), *** Netlist Block *** (6 .inc), *** Stimulus Block *** (.param), *** power *** (.param+vad2+.inc), *** Cell Block *** (.inc), Array Param, *** Mismatch Block *** (.inc)
- .tran sweep Optimize bisection, .MODEL OptMod, .temp, .END

## .sp file structure (demo_a.sp, 156 lines)
- 7 .lib (model corners: ss, ss_Array, bjt_tt, res_tt, nicap_tt, diode_tt, tdv)
- 12 .inc (finesim_option, netlistHeader/netlist/netlistFooter, 2 spf, tRAS_PWL, Pattern_Power, BG_ys_SLD1, G1_E_D0_TPC, ArrayRcSetting, D0_SenB)
- 16 .param (toc, pstrap, tpreeq_block, tpreeq_act, tblen_blockU, tblen_actL, pvcc, ptemp, ORG, pvblh, pvad2, c_ntsv_vss, c_ntsv, c_adjntsv, c_negntsv, VTarget)
- 2 .option (finesim_mode, finesim_bisection_output)
- 1 voltage source (vad2)
- 1 .tran sweep Optimize=Opt1 Result=MaxVout Model=OptMod
- 1 active .MEASURE (28_G1_D0_4), many commented *.MEASURE
- 1 .MODEL OptMod Opt Method=Bisection Itropt=12
- .temp -40, .END

## Case design (A-faithful, L1-static, eda_other, 15 conds a-o)
- prompt: USER#0 verbatim "analyze and detailed explain the structure of the netlist" + demo_a.sp attachment
- candidate: gen_spice_netlist_structure.py — generic SPICE netlist parser → JSON (blocks, lib, inc, params, options, v_sources, tran, measures active/commented, model, temp, end)
- hidden B (b1.sp): SRAM write-margin testbench, different banners (*** CORNER ***/*** SIMULATOR ***/*** DUT ***/*** STIMULUS ***/*** SUPPLY ***/*** PATTERN ***/*** RC ***/*** MISMATCH ***), 3 .lib, 11 .inc, 12 .param, corner ff/125°C/vdd=1.1, optimize Vcrit/Opt2/OptM2, goal 0.6, time 60n
- randomized B' (b2.sp): shuffled block order for seed test (same summary)
- check subprocess runs candidate on b1.sp, asserts 15 conditions; anti-hardcode guard l runs candidate on A (demo_a.sp) verifying A counts; m source has no A/B literal block/param names; n b2 order-independence
