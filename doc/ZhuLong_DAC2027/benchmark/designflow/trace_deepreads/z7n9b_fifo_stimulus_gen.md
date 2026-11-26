# trace_deepread: z7n9b — FIFO_TOP stimulus generation (curryxu@hfeg0pkn001)

- **session**: `1793690145277_z7n9b.messages.json`, user=curryxu, host=hfeg0pkn001 (10.129.2.10), 40 msgs / 277KB, mtime 2026-11-03 15:15.
- **trace_source**: cron 11-10 log diff (8 un-ledgered spice-dominated candidates from 11-10 cron vs ledger B tsv). z7n9b was top clean produce-task candidate (spice=172/total=547).
- **user rounds** (A-faithful selection):
  - **U#0** (提需求，A-faithful 合格 ✓): "用这个skill来帮我写个激励文件，/home/adaml/.cline/skills/spice_tb_stimulus，电路netlist为/proj/m2701/V0_DDR4/workdir/curryxu/simulation/FIFO_TOP/hspiceD/schematic/netlist/netlist" — 用 spice_tb_stimulus skill 为 FIFO_TOP 网表编写仿真激励文件。未给根因/修复 → A-faithful 合格。
  - U#39 (末轮，未应答): 给出 D<0> 的 pwl 波形，要求按周期 6tck 继续写 D<0>..D<24>。此轮在 trace 末尾无 assistant 应答 → 无 accepted 交付，不作金标准。
- **assistant tool chain**: skills(spice_tb_stimulus) → read_files(netlist + 5 skill 模板: template_tran_io.sp/model_libraries.md/template_measure.sp/simulator_options.md/template_analog.sp) → run_commands(grep .subckt/.ends, wc -l) → ask_question(选 finesim / 选 .tran) → editor×4 写出 FIFO_TOP_tb.sp(13-Section)/measure.sp/run_fifo.sh → read_files 验证。
- **netlist 结构** (assistant A#28 分析): FIFO_TOP 是 **flat 网表**（无 .subckt 包裹），顶层信号 = CLK_Sample, D<23:0>, Rst, Nibble_Sel0/1/2, Dout<23:0>, Dout_dly<23:12>, Sel<5:0>, SelN<5:0>, DNNOF/DNNEF/DNNOR/DNNER；全局电源 vcc!/vccz!/vss!/vbn!/vbp!/vbulkn!/vbulkp!。netlist 241 行。
- **金标准** = assistant 最终交付 (write#30, /home/curryxu/FIFO_TOP_tb.sp, 5208B) — 13-Section 结构：
  1. Simulator option (finesim 默认/hspice 注释切换, finesim_mode=spicehd)
  2. Model corner & temp (.lib model.sp top_tt + pre_simu, .temp 25)
  3. Supply voltage (.param pvcc=0.8 pvccz=0.94 pvbn/pvbp/pvbulkn/pvbulkp)
  4. Designer params (.param tr/tf=60p tCK=1.25n duty=0.5 pw_clk sim_finish=50n tRst_delay=5n tData_delay)
  5. Power sources (vvcc/vvccz/vvss/vvbulkn/vvbulkp/vvbn/vvbp 全局电源)
  6. Netlist include (.include './netlist/netlist')
  7. Input stimulus (VRst pwl 低有效 / VClk CLK_Sample pulse / VNibble_Sel0-2 / VD0/VD12/VD1/VD13 pwl)
  8. Data sweep (注释态 .data)
  9. Analysis (.tran 1p 'sim_finish')
  10. Probe (.probe v(*) + 关键信号)
  11. Measure (.inc 'measure.sp')
  12. Pattern include (注释)
  13. Corner .alter (注释) + .end
- **case 重构 (B-synthesized)**: trace 是「写一份激励文件」，本 case 把约定重构成**网表通用生成器** `gen_tb_stimulus(netlist_text)->str`，使隐藏输入 B（不同端口/位宽/结构的网表）可判分 + 反硬编码。A = FIFO_TOP trimmed netlist (.subckt + @ports_* manifest) + example_stimulus.sp(金标准作约定参考) + task_brief。B1=FIFO16 16-bit, B2=SRAM8 8-bit。check.py 16 断言驱动端口覆盖 + 结构 + 反硬编码 + 3-seed 端口乱序。
- **判分**: ref PASS 16/16, 3 neg (stub/always_example/port_ignoring) 全 FAIL NEG_RC=0, §4.9 三假(空壳/print-expected/core-deleted)全 FAIL, check_sha256=1fe9795c…
- jsonl B 219→220, ledger covered 220→221 (spice_sim 177→178).
