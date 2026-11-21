# Deepread: 1795055039874_siev4 (lorikx @ hfeg0plg15, mc=123)

**Session**: `1795055039874_siev4.messages.json` (subdir path: `1795055039874_siev4/`)
**User**: lorikx @ hfeg0plg15 (10.129.32.75 / 172.16.8.191)
**Size**: 785 KB / 75 messages
**Scan keywords**: rtl:583;verilog:87;synopsys:19;binary:8;netlist:6;synthesis:2 (A-pure, no C-domain lvs/drc/calibre/virtuoso)
**Tool histogram**: list_allowed_files, read_files, editor, run_approved_command
**Domain**: verification (A shard) — VCS + Verdi makefile produce + sim diagnosis

## Workdir
`/home/lorikx/MY_SANDBOX/6in1_sel10_dft_rtl/` — 6in1 SRAM test chip 2P channel ch378 RTL sim verification

## User intent (4 typed turns, verbatim)

- **U#0**: 「请帮我检查testbench，然后写个makefile用于编译仿真并打开verdi」
- **U#21**: 报告 OK=63 ERR=1, ERR 378L_7/S_7 addr=7 Q=xxx, 问「我发现例化为7的基本都有x，是因为什么原因呢，都是贴近仿真结束的」
- **U#65**: 「请将问题的原因讲解清楚，并把需要修改的地方列出来，都输出到文件里」
- **U#73**: 「可以在Makefile里面把有问题的版本留一个用来运行，正确版本也留一个命令用来运行，最后是有两个fsdb方便握紧行对比」

## Trace gold

### Makefile (A#8 editor → A#14 readback)
- FILELIST=sram2p_verify_top.f, TB_FILE=WR_turn_tb.v, TOP=TB (all `=` overridable)
- VCS_OPTS: -full64 -kdb -sverilog +v2k -error=noMPD +vcs+lic+wait +nospecify +notimingcheck +define+MEM_CHECK_OFF -debug_access+all
- targets: compile (vcs -f FILELIST TB_FILE -top TOP -l COMPILE_LOG), sim (./simv -ucli -do UCLI_DO -l SIM_LOG), verdi (verdi -f FILELIST TB_FILE -ssf FSDB &), clean (rm -rf simv csrc fsdb logs), help
- FSDB: dut_000.fsdb, UCLI_DO: fsdb.dump.do

### Root cause (A#26, A#39)
- DUT top `CXTV1_DBC_6in1TC_top.v`: `assign WEB_top_sel[i] = (i_macro_inst_num_sel == i[4:0]) ? 1'b0 : 1'b1;` — pure address decode, GPIO_WEB not connected for 2P channel (ch378/420)
- 1P channel (ch210/336) uses `.WEB(i_web)` (GPIO_WEB controlled), but 2P uses `.WEB(WEB_top_sel[i])` (address-only)
- After write loop, gpio_a stays at (7,7) → WEB_top_sel[7]=0 → ch378L[7]/ch378S[7] write port active entire read phase
- CLKW/CLKR same phase → last read (7,7) = same addr + same time + read+write both active → SRAM model rule "Read-write conflict → Q=X, mem=D"
- Other 63 reads: different addr ≠ (7,7), 2P SRAM supports concurrent diff-addr R/W → OK

### TB fix (A#29, A#39)
- After write loop: `gpio_a[18:14] = 5'h1f;` (decode to non-existent wrap → all write ports inactive)
- Regression: `done OK=64 ERR=0`

### DUT fix (A#64)
- `assign WEB_top_sel[i] = ((i_macro_inst_num_sel == i[4:0]) && !i_web) ? 1'b0 : 1'b1;`
- Patch file: `dut_top_2p_web_fix.patch`

### TB residual fixes (A#64)
- pad_clkw/pad_clkr: declared + driven (was implicit wire = Z)
- Read port idled during write phase: gpio_a_read = {5'h1f, 14'd0}
- Dead code removed: read378 `(2'b10<<19)` truncation

## Case synthesis (r951)
- Case ID: EDA-Eval-DesignFlow-VcsMkfileSimDiagnoseProduce-001
- Tier: A (trace-faithful) — produce+analysis hybrid
- k=14/14 assertions, §4.9 3-neg all FAIL
- check.py uses `make -n` dry-run on hidden B (TB_HEX/DUALPORT_RF_TOP) to verify Makefile parameterization
