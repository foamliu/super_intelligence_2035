# mejpi — Formal Lagat S2P Bind Adaptation

**session**: 1791961260627_mejpi.messages.json
**user/host**: e13zhang / hfeg0pkn002 (10.129.2.11)
**mc**: 207 (rtl:1188; synopsys:122; analog:60; verilog:28; systemverilog:17; netlist:10)
**domain**: verification
**msgs**: 316 / 1.6MB / 20 user turns
**case**: EDA-Eval-DesignFlow-FormalBindS2pAdapt-001 (A.jsonl 349→350)

## User Intent (trace-faithful)

- **U#0**: "帮我分析一下sim/base_fun中的RTL代码，结合环境中的check和assert分析一下是否有需要补充的检查"
- **U#43**: "这个DUT因为涉及很多个时钟，以及串转并和并转串有没有需要特别增加的点"
- **U#53**: "我新建了一个formal_lagat_s2p 帮我把里面需要适配的 都适配一下"
- **U#165**: "这两个增补完以后还有明显的缺陷和漏洞吗？"

## Key Findings (assistant A#25/A#30/A#32/A#37)

1. `sim/base_fun` = VCS compiled simvdir (`+define+DDR6_MODE +define+ONEP6`), top: `dram_tester_chip.sv`
2. **Write mask NOT a gap** — implemented at top level (interrupt mask, RX lane/bank/channel mask, txfifo intr mask)
3. **rx_fifo_s2p overflow risk**: `wfull=1'b0`, `wr_en=1'b1`, depth 8 — no write flow control
4. **Uncovered async FIFOs**: `rx_fifo_s2p`, `txfifo_async_fifo`, `sync_fifo_9to18` — no formal bind
5. Formal env covers rxfifo/txfifo/slice_txfifo but NOT rx_fifo_s2p/sync_fifo_9to18

## Deliverable (assistant A#65)

Created `formal_lagat_s2p_adapt/` with 4 adapted files:
- `filelist.f`: slice_txfifo.v → sig_sync.sv + sync_fifo_9to18.v + rx_fifo_s2p.v
- `formal_config.tcl`: top=rx_fifo_s2p; 3 clocks (wr_clk/rd_clk/rd_clk_1p25g); 3 resets
- `lagat_s2p_bind.sv`: 10 assertions + 8 covers (overflow, gray-code, no-read-when-empty, data integrity, occupancy bound, CDC reset value)
- `run_vcf`: batch run script

## Case Construction (B-档 mini)

- **A_files**: mini rx_fifo_s2p.v (DATA_WIDTH=9, DEPTH=8, wfull=0, wr_en=1) + sync_fifo_9to18.v + sig_sync.sv + original formal_config_orig.tcl (slice_txfifo) + lagat_tc_formal_bind_orig.sv (txfifo template) + filelist_orig.f
- **B variant** (hidden): tx_fifo_async_B.v (DATA_WIDTH=18, DEPTH=16, sub-modules u_cdc_sync/u_sync_fifo_32to64) — structurally different module/params/sub-module names
- **check()**: 16 conditions (a-p), static regex analysis of bind .sv file + cross-input guard against B variant
- **ref**: lagat_s2p_bind_ref.sv (from actual trace deliverable) → 16/16 PASS
- **negatives**: 4 (empty, print-expected, core-deleted, wrong-module) → all FAIL

## Trace Source
- `trace_source.user` = e13zhang (real username, not hashed)
- `trace_source.host` = hfeg0pkn002
- `trace_source.session_file` = 1791961260627_mejpi.messages.json
- `trace_source.match_count` = 207
- Adapted files fetched from `/home/e13zhang/formal_lagat_s2p_adapt/` on 10.129.2.11
