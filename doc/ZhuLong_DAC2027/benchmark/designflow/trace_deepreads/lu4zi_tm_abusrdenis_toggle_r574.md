# trace_deepreads/lu4zi_tm_abusrdenis_toggle.md — TM ABusRdEnDis bus-driver toggle analysis

## meta
- session: 1793861526761_lu4zi (directory-form: /home/daiweilu/.cline/data/sessions/1793861526761_lu4zi/)
- user/host: daiweilu / hfeg0pfn090 (10.129.32.x)
- mc=120 ; domain: verification (LPDDR5 test mode debug)
- trace: 844KB, 179 msgs, 10 user turns, 81 tool_use (run_commands 191 / editor 30 / read_files 2)
- model: deepseek (cline)

## user 意图 (逐字选轮)
- USER#0: "我运行TM_AbusRdEnDis.run时有报错ncvlog: *E,UNDIDN 'OP_ABUSRDENDISUP': undeclared identifier. 帮我检查一下"
- USER#1: "我修改创建了一个新的TM_AbusRdEnDis1.v,然后报错ncelab: *E,CUVUNF Hierarchical name component lookup failed at 'TM_AbusRdEnDis1'"
- USER#2: "这个tm的要求是 TM_ABUSRDENDISUP=00 全常开 / =10 上拉常开下拉toggle / =01 下拉常开上拉toggle / =11 全部toggle采样. 这是我的网表,帮我看下如何验证"
- USER#3-5: "cm1_cl_AbusRdEnDisUp在网表的层级是什么", "应该toggle的信号是哪个?", "我要AbusUp的路径"

## assistant 工具链与关键发现
1. **Error #1 诊断**: OP_ABUSRDENDISUP 未在 TM_parameters.v 定义 (只有 OP_ABUSRDENDISUP0/UP1)
2. **Error #2 诊断**: TM_AbusRdEnDis1.v 仍声明 task TM_AbusRdEnDis (未改名为 TM_AbusRdEnDis1)
3. **Truth table decode**: TM_ABUSRDENDISUP[1:0] → 00=both-on, 01=up-toggle, 10=down-toggle, 11=both-toggle
4. **Netlist mapping**: cm1_cl_AbusRdEnDisUp[1:0] (2-bit) + cm1_cl_AbusRdEnDisDn (1-bit) → AbusNNWPDrv_ddgoa_0820 cells with .PupN()/.Pdn() ports → AbusUp/AbusDn rails
5. **Hierarchy**: CMAryA module produces cm1_cl_AbusRdEnDisUp, 8 instances per bank group; AbusUp in RWAbusTN_NN_new_ddgoa_0915, 288 instances
6. **RdDrvEnN**: read-enable pulse (not constant-low), one pulse per read
7. **TM actually PASSES**: A_Summary.rpt shows TM_AbusRdEnDis DQ_Err:0 (PASS)

## 落地 case
EDA-Eval-DesignFlow-TmBusToggleAnalyze-001 (verification, B档 synthesized, L1-static, 16 conds ①-⑯)
- prompt = synthesized (引用真实 scenario: daiweilu/LPDDR5/TM_AbusRdEnDis/bus-driver toggle/truth table)
- assets A: tm_spec_A.md(2-bit OP truth table) + pattern_A.v(Load_TestMode OP=11+01) + netlist_A.v(AbusPupDrv/PdnDrv cells, cm1_cl signals) + task_brief.md + prompt.txt
- hidden B: tm_spec_B.md(1-bit pulldown-only TM_ABUSRDENDISDN) + pattern_B.v(OP=1+0) + netlist_B.v(WlPupDrv/PdnDrv cells, different rails)
- reference: tm_toggle_analyzer_ref.py + check.py(16 conds: zip存在/无错产JSON/tm_name/op_bits/truth_table keys/modes/pulldown-only/op_values_loaded/driver_cells count/cell_type/cm_signals/toggle_signals/determinism/anti-hardcode) + 4 neg + negative_selftest
- 自验: ref selftest 16 PASS + 4/4 neg FAIL (③/⑯/⑨/③) + §4.9 三假 FAIL distinct{③/⑯/⑨}
- r574 fresh-deepread (scp trace 844KB to .75, parse 179 msgs)
