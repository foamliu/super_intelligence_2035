# Deepread: tadah (jackliu) — netlist fighting / x-state analysis

- **session**: `1792137924614_tadah.messages.json` (jackliu @ 10.129.32.83, mc=87, 206 msgs)
- **domain tags**: netlist:118 / synopsys:359 / cadence:116 / skipper:88 / hspice
- **peek**: nturns=4 user, nedit=45 (editor), 38 produced files (check_*.py / try_*.py / read_*.py / dump_*.tcl — all exploratory debug scripts for reading ncsim.shm/.trn via simvision+xvfb)

## Verbatim user turns
- U#0 (msg#0): 「你可以读取verilog波形文件吗，比如/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpdddr5.ddgoa.new/log/log.regression_20261016_093556/scan_allspeed.x16/ncsim.shm/ncsim.trn」
- U#1 (msg#30): 「以后都说中文」
- U#2 (msg#58): 「刚才的波形文件你有读吗，你会发现里面的inh_vblh都是x态」
- U#3 (msg#205, **produce-demand**): 「如果你可以读到波形内的信号数据，请根据网表分析一下vblh是x的原因，可能哪里存在fighting，你可能需要网表 /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct15.193816/netlist」

## Assistant behaviour
- 106 tool_uses, almost entirely attempts to read the binary `.trn` waveform via `simvision` under `xvfb` (run_simvision_xvfb*.py, check_simvision*.py, try_simv_*.py, dump_inh_vblh.tcl). Persistent environment/tooling struggle (simvision license, xvfb display, SHM db open).
- The session **never reached a clean netlist-fighting analysis produce** — agent stayed stuck on waveform value extraction. No user-accepted netlist-analysis artifact.
- Real `/rundata/.../netlist/` is a large flat verilog gate-level netlist (V0_WOWTOP_2026Oct15) — live, not attachable.

## User's real goal (U#3)
Given a verilog netlist, analyze **why a signal (inh_vblh) is x-state** by finding **driver fighting** — nets driven by more than one source (multiple instance outputs, output+assign, inout contention, tri-state enable overlap). This is the classic static cause of x in gate-level netlist.

## Synthesis decision (B-grade synthesized)
- Real netlist is live + huge → cannot attach verbatim. Real produce is exploratory debug, not a clean deliverable.
- **B-grade synthesized**: keep the user's real goal (static netlist fighting/x-state analysis) and synthesize a clean offline-verifiable deliverable: a Python **netlist driver-fighting analyzer** that parses a verilog netlist, builds a per-net driver map (bit-aware), and reports nets with >1 driver (fighting) classified by driver kind (instance output / continuous assign / primitive / inout port / tri-state), plus x-state risk.
- Asset A = small synthesized verilog netlist with deliberate fighting patterns (multi-driver, assign+output conflict, inout contention, tri-state enable overlap, bus bit conflicts, clean single-driver nets, hierarchy).
- hidden B = different module/cell/net names + different fighting topology (more nested, different conflict kinds) + cross-input guard.
- L1 offline: candidate run via `python3 subprocess` on hidden B; structural JSON assertions.
- 反硬编码三轴: A/B names fully disjoint + B contains conflict kinds A lacks + cross-input guard (re-run on A must equal goldA; no B literals in source).

## Conditions target: 16 (a–p)
