# Deep-read: mn59z — finesim.prof cell-recommendation analysis

- **session**: 1793167500635_mn59z · user e03179 @ hfeg0pkn002 (IP 10.129.2.12) · mc=29
- **keywords**: netlist:223 analog:214 transistor:131 verilog:53 lvs:41 schematic:16 aether:14
- **size**: 352KB / 37 msgs / 1 user turn (single-shot produce task)
- **domain**: analog_context (analog cell modeling recommendation)
- **trace_source**: real cline session, vam-agent skill

## User intent (U#1, verbatim)
> [vam-agent] 根据这个prof文件看下哪些cell适合重新建模/proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20260907PM_DDR6TOP_Test_profile/primesim.Golden008_..._TT0.92V25C.X2P3/finesim.prof

Single-shot produce task: given a finesim.prof, analyze simulation-time breakdown and recommend which analog cells are suitable for re-modeling (Verilog-AMS behavioral modeling).

## Assistant tool chain (gold standard)
1. skills(vam-agent) → skill loaded (Scenario 1: prof → recommend analog cells)
2. list_allowed_files / search_codebase to locate skill assets
3. read_files(profile_analyzer.py) to inspect interface
4. run_approved_command(python-runner, profile_analyzer.py <prof> --simpath <simpath>) → exit 0
   - stdout: "总 subckt 数: 4718; 推荐建模: 11 (占总仿真耗时 3.09%); 排除: 数字标准单元 1967, MOS管原语 13, 数字逻辑门, ..."
5. read_files(reco_Golden008.json) to capture full recommended list
6. Final answer: markdown table of 11 recommended analog cells (sorted by solve_pct desc) + digital-block Verilog-A candidates + CRC block detection

## Gold-standard output (reco_Golden008.json structure)
- top_solving_cost: 0
- recommended[]: 11 cells, each {name, usage, eval_cost, eval_pct, solving_cost, solve_pct, has_devices, n_transistors, device_solve_cost, child_subckts[], instance_solve_cost, is_digital, is_leaf_analog, is_wrapper, cell_type, is_analog_name, solve_per_instance, eval_per_instance, device_cost_ratio, recommendation_reason}
- recommended_count, recommended_total_solve_pct
- digital_skipped_count/top, mos_skipped_count/top, trim_skipped_count/top, parasitic_skipped_count/top, digital_gate_skipped_count/top, pass_gate_skipped_count/top, wrapper_skipped_count/top, no_ports_skipped_count/top
- summary{total_subckts, recommended_count, recommended_total_solve_pct, digital_count, mos_count, trim_count, parasitic_count, no_ports_count, digital_gate_count, pass_gate_count, wrapper_count}

Top 5 recommended (by solving_cost desc):
1. rndiff_3t_ckt (41215 inst, 2.39%, 6 transistors, Analog (other), device_ratio 0.499)
2. r_lvlshftvcc2sc2vdly (512, 0.37%, 5 transistors, Analog (other), 20% device)
3. ag_vdbiasact (16, 0.08%, 5 transistors, Analog General)
4. ag_actampnmirunit (3216, 0.07%, 3 transistors, Analog General)
5. io_cabufcore (12, 0.06%, 64 transistors, IO Circuit, 3.87% eval)

## finesim.prof format (from profile_analyzer.py docstring + parse_profile_line)
```
.subckt <name> <usage_count> <eval_cost> (<eval_pct>%) <solving_cost> (<solve_pct>%)
   <inst_name> <child_subckt> <eval_cost> (<eval_pct>%) <solving_cost> (<solve_pct>%)
   <N> devices <eval_count> <eval_cost> (<eval_pct>%) <solving_cost> (<solve_pct>%)
.ends
```
- subckt header regex: `.\s*subckt\s+(\S+)\s+(\d+)\s+(\d+)\s+\(\s*([\d.]+)%\)\s+(\d+)\s+\(\s*([\d.]+)%\)`
- device line: `(\d+)\s+devices\s+(\d+)\s+(\d+)\s+\(...%\)\s+(\d+)\s+\(...%\)` (indented)
- instance line: `(\S+)\s+(\S+)\s+(\d+)\s+\(...%\)\s+(\d+)\s+\(...%\)` (indented)
- .ends closes block. .topckt directives are ignored (top_solving_cost stays 0).

## Classification logic (NO netlist → ports always []; the trace's scenario)
Order in rank_cells:
1. is_digital(name) → digital_skipped. Rules: DIGITAL_EXACT {ptn,ntn,ptn_lv,ntn_lv,ntn_m,ptn_m,nfet,pfet,rn,ntk,ptk,ntk_wl,ntk_lv,...} OR startswith DIGITAL_EXACT_PREFIXES {d_,dlybias,dlybiasn,colctrldly_,ntk_,ptk_} OR startswith/== DIGITAL_PREFIXES {inv,nand,nor,buf,aoi,oai,mx2,mxi,mx,dlyg,or2,and2,xor,xnor,passgt,switch,brknet,inviolvx,invlvx,invlvsx,invcsx,invlx,buflvx,buflvsx,buflx,buflv,bufDS,invDS,bufdsx,bufds,bufdsx4,...,rsnand,spnand,spnor,rsnor,ffrqlx,dlyrc,ffrqdsx,and2lvx,and2csx,and3gsx,invgsx,invlvs,nor2lvx,nand2lvx,nand4lx,kcellx}
2. solve_pct < 0.001 → dropped (no bucket)
3. 'trim' in name.lower() → trim_skipped
4. is_parasitic (parasitic/parasiticrc/parasiticcc/forcedummybl/d_pwdnw_ckt prefix) → parasitic_skipped
5. is_mos_primitive_by_name: startswith {ntn_,ptn_,ntnlv_,ptnlv_,ntn,ptn,ntk_,ptk_} → mos_skipped
6. (no netlist → no_ports check skipped)
7. is_digital_gate(name, []): startswith DIGITAL_GATE_NAMES {latsq,latrsq,latsqlv,latrsqlv,and3,and3lx,and3gsx,nor2,nor2lx,nor2lv,nor3,nand2,nand2lx,nand2lv,nand3,and2,and2lx,and2csx,or2,or2lx,xor,xnor,aoi21,oai21,aoi22,oai22} → digital_gate_skipped
8. is_pass_gate(name, []): 'passgt' in name.lower() → pass_gate_skipped
9. is_digital_wrapper: device_solve_cost/solving_cost*100 < 2.0 AND len(child_subckts)>5 → wrapper_skipped
10. else: if has_devices (is_leaf_analog) → recommended; else dropped (no bucket)

Derived fields per recommended cell:
- cell_type = classify_analog_type(name): ag_→"Analog General"; af_→"Analog Fuse/Aux"; io_→"IO Circuit"; ras_→"Row Address Sense"; t_+cmf/cml→"Sense Amp Latch"; t_+ras→"Row Sense Amp"; t_+cas→"Column Sense Amp"; sa_/senseamp→"Sense Amp"; cmp→"Comparator"; amp→"Amplifier"; bias→"Bias Circuit"; vref→"Reference"; clamp→"Clamp Circuit"; latch→"Latch"; else "Analog (other)"
- is_analog_name: startswith {ag_,t_,af_,io_,ras_,cml,cmf,sa_,senseamp}
- solve_per_instance = solving_cost // usage; eval_per_instance = eval_cost // usage
- device_cost_ratio = device_solve_cost / solving_cost
- recommendation_reason: cost tier (>=1%"high sim cost X%", 0.1-1%"notable cost X%", else "cost X%") + usage (>=10000"high volume", >=100 count) + per-instance (>=1e12"very expensive", >=1e9"expensive") + cell_type + device_ratio (>=0.5"transistor-dominated X%", >=0.1"mixed X% device")

## B-grade synthesized case design: FinesimProfCellReco-001
- SUT writes `prof_cell_reco.py <prof> <out_json>` (pure stdlib: re/sys/os/json/argparse; no subprocess/socket/eval/exec; no B/C literals)
- Parse finesim.prof → classify each subckt (name-based + structure-based, NO netlist) → rank analog-leaf by solving_cost desc → emit reco_report.json {total_subckts, recommended[], summary{category counts}, top_solving_cost}
- A/B/C disjoint: different cell-name prefixes + different counts/pcts. C embedded in check.py (anti-hardcode).
- check.py 14 conditions a-n: independent oracle (own parser + classifier) re-derives expected for B; compares SUT JSON field-by-field; anti-hardcode C≠B; 3-seed sha256.
- difficulty = L1 (honest: pure stdlib text parsing, no EDA tool runtime — consistent with #518-523)
- 维度正交 vs existing D cases: PwlDecodeStimGen (PWL/bit-mapping), LeakageCellPvtAudit (.mt0 PVT), SpiceUndefParamScan (undefined param), IddMeasPostProcess (idd waveform) — this is finesim.prof classification, mechanism distinct. Non-dup ✓.
