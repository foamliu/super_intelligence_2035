# r1018 — digA2 fresh A-domain pool genuine exhaustion (0-case round)

**选料**: 复用 .75 scan ssh_eda_search_20261122_172249, 同款 digA2 narrow-C_KW filter
(ac>cc && ac>bc && ac>=5 && mc>=5, sum-of-nums 计数法, A_KW=verdi/vcs/synopsys/tcl/verilog/rtl/xrun/dc_shell/innovus/primetime/design_compiler/pt_shell/synthesis/formality/verilint/sdc/vivado/yosys/openroad, C_KW=virtuoso/aether/layout/lvs/drc/pex/gds/calibre/skipper/pdk/lef/def, BD_KW=hspice/spice/netlist/schematic/analog/waveview/cmos/pyaether/spectre/finesim)
→ 1595 cands → 622 dedup → 4-shard ledger diff (4226 normalized sids) → **13 fresh**

**13 fresh 归因** (r1017 已归因 8 个 cross-domain + 本轮 peek 4 个 low-mc + t61yg r1017 已用):
- wcio5(ericw mc125 ac476/cc59/bc273 mixed B/D-heavy) skip — r1010 已 parked
- dxxm5(qiangw mc106 ac2217/cc1712/bc623 C-dominant drc:1599) skip
- 77z85(cliu mc89 ac761/cc445/bc284 C-dominant lvs/drc) skip
- g2oge(rayfeng mc74 ac190/cc1/bc101 TCAD/sprocess C-leaning) skip — r1008 已 parked
- qs9e9(eva1li mc47 ac219/cc5/bc24 mixed) skip — r1006 已 parked
- yl0mz(e0040367 mc29 ac43/cc26/bc30 very mixed) skip
- v2zbq(ruisongs mc15 ac442/cc436/bc6 C-dominant drc) skip
- mg83q(e0045142 mc6 ac28/cc17/bc4 mixed C) skip
- b74x3(jianilu mc6 ac8/cc0/bc2 low-ac sparse) skip
- **本轮 peek 4 low-mc fresh**:
  - 3n34y(e0035227@hfeg0plg54 mc7 ac14/cc0/bc1): kw=rtl:14;dbopencellviewbytype:9;dbcreateinst:8;cellview:8;ddgetobj:3;pyaether:1 → **pyAether/Aether layout APIs 主导 (dbopencellviewbytype/dbcreateinst/cellview/ddgetobj)**, rtl 仅来自路径名; 实为 C-domain layout creation mis-filtered by rtl count → park (C-domain)
  - e0x94(e0041392@hfeg0pkn002 mc6 ac15/cc0/bc0): kw=rtl:15 only (sparse). scp 完整 trace 141KB/45msgs. U#0 逐字「帮我生成十大经典排序算法的python实现，然后输出一份对比文档，每个算法用一个.py文件」→ **generic Python 编程任务 (冒泡/选择/插入/希尔/归并/快排/堆/计数/桶/基数排序)**, 非 EDA design-flow, rtl 关键词来自工作目录 desktop-app 路径名 → park (not design-flow)
  - wg5qc(e0048255@hfeg0pkn004 mc6 ac17/cc0/bc0): kw=rtl:10;.spi:7;verilog:6;synopsys:1. scp 完整 trace 91KB/13msgs. U#0「请问我这个脚本的输入是什么？输出是什么？ .../gen_tb.py」+ U#1「...tb_io_top_par_wrap.v 这个是靠哪个脚本产生？」→ **explain-Q&A (脚本 I/O 分析 + 文件 provenance 追溯)**, 需 proprietary gen_tb.py + 相关脚本 fixture (在 /proj/lacaa 用户路径, 无法 bundle), deliverable=prose 难写有牙 check → park (explain-Q&A needs proprietary fixture)
  - w7f26(zoeyr@hfeg0pkn003 mc7 ac19/cc13/bc14): kw=synopsys:19;netlist:9;drc:7;pex:5;waveview:4;lvs:1;hspice:1 → **mixed C/B/D (drc/pex/lvs/hspice/waveview 主导)**, synopsys:19 拉高 ac 但实为跨域 → park (cross-domain)

**结论**: digA2 sum-filter fresh A-domain pool 真实耗尽 — 13 fresh 全部归因完毕 (8 cross-domain r1017 已归因 + 4 本轮 peek low-mc/sparse/C-domain/not-design-flow + t61yg r1017 已用). 无 clean single-round A-domain produce-task 候选.

**心跳三数**: mc≥5 pool 622 (digA2 sum dedup) / fresh 13 (4-shard ledger diff 4226 sids) / 本轮 peek 4 A-fresh(3n34y/e0x94/wg5qc/w7f26 全 parked: 1 C-domain + 1 not-design-flow + 1 explain-Q&A + 1 cross-domain) / 产出 0 case

**stop-loss**: auto_stop consecutive_zero_case_rounds: r1017产case→0; r1018首0-case→counter=1; stop-loss 1/3 NOT triggered

**下轮首要**: digA2 fresh 已耗尽 ⇒ 应跑新全量698-host scan (15:1x 令授权, daily quota 可用, 上次 11-22 17:22 ~40h ago) → POOL_SWITCH → recompute fresh → peek top fresh → 造题; 若新 scan 仍 0 fresh A-pure 则 counter=2/3, 再一轮触发 revert shard_mc.A=10 + pivot non-candidate output (§4.9 anti-hardcode 普查 / test_rationale 补断言 / ledger 治理)

**eda_flow session r1018**: declare_done + close
