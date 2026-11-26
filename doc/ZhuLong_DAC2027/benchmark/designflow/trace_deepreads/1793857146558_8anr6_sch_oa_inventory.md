# Deepread: 1793857146558_8anr6 — SchOaInventoryExtract (layout_aether)

**Trace**: `1793857146558_8anr6.messages.json` — haoliu @ hfeg0pkn003, mc=87
**Agent**: lead (glm-5.3-flash, cxmt-glm), 70 messages, 2026-11-05
**Domain**: layout_aether (Aether OA schematic analysis)
**Library dir**: `/proj/drgqa/V0/workdir/haoliu/drgqa_work_haol/` (DDR4 DQ/DQS receiver DTCO project)

## User intent (verbatim)
- msg#0: `请分析当前电路` (analyze current circuit)
- msg#7: `你是否可以查看virtuoso` (can you view Virtuoso)
- msg#20: `jixu` (continue)

## Assistant tool chain (key steps)
1. `list_allowed_files` — workspace `/ai_sandbox/m2701/V0_DDR4/agentdir/haoliu` empty
2. `SandBox_MCP_Server__run_code` (SKILL) — Virtuoso bridge test → connection refused (172.16.8.12:25069)
3. `run_approved_command` (python-runner) — probe Virtuoso env: no Virtuoso process, no ip_port.json
4. Discovered environment is **Empyrean Aether** (`/apps/empyrean/aether/`), not Cadence Virtuoso
5. Found haoliu's Aether workdir `/proj/drgqa/V0/workdir/haoliu` with `cds.lib` + design dirs (IO_hao, drgqa_work_haol, IO_DQRCV_PC60)
6. Identified "current circuit" = `drgqa_work_haol/WRDQS_Full_path` (schematic, last edited 2026-10-29 11:03; Aether session 2026-10-28)
7. `dump_sch_strings.py` — extracted 469 unique clean strings from `sch.oa` binary (103012 bytes) via strings-filtering
8. Read `CXMT_zhulong_EDAAgent.py` — understood bridge mechanism: UID-based deterministic ports (pyAether=20000+(UID×10008)%45533, skill=×10009), bridge runs inside EDA tool, MCP connects to ip_port.json (currently points to desktop 172.16.8.12, not LSF node 10.129.2.13)
9. Delivered: circuit analysis (WRDQS_Full_path component inventory) + bridge diagnosis + one-click bridge start script `start_bridge_in_aether.py`

## Real artifact: sch.oa strings dump (469 strings)
**Top cell**: `WRDQS_Full_path` (DDR4 Write DQS full path top-level integration schematic)
**Subckt instances** (I_ prefix): `I_IO_DqsRcvTop`, `I_IO_TrnLoopbackDqs`, `I_IO_DqsM4RcModel`, `I_IO_DqRcv`, `I_IO_DqsDmRedundancy_477`, `I_D_WrDqsDly_0`, `I_D_WrDqsDly_drgpx_0` (+ numeric I30/I248/I301/I256/I422/I273/I299/I274/I276/I275/I302/I1348/I1349)
**Signal nets**: DQS_P/N, DQS_buf_R0/R1/F0/F1, DQS_IN/OUT, DQS_I/IB/Q/QB, DQS_0/90/180/270 (+D delayed), DQS_Far/P/N, WR_DQS0–7, WR_DQSDM, WR_DQS3<0:4>, DATA_I/IB/Q/QB, DATA_*_OUT_T, DoutI/IB/Q/QB, VREFDQ, PHASE_A/B/C/D_EN, LoopBack_EnB/EnN/Mode_Sel, DmRedundancy<0:4>, EnPh0–7_ODrv/EDrv, Dqs_Out, DQSI_Out, ScmosDQSIB, Dmwr
**Pins**: PIN0–PIN258 (259 total)
**Techlib refs**: TECHLIB.vss.symbol, TECHLIB.switch.symbol, TECHLIB.MarkSN.symbol, basic.in.symbol, basic.out.symbol
**Module refs**: IO_DqsRcvTop, IO_TMF_WLDQSB, IO_DqsDmRedundancy, IO_DqsM4RcModelV2, IO_TrnLoopbackDqs, IO_DqRcv, IO_NBTI_WDQS, IO_NBTI_NORMALen, IO_MRDfeGain, IO_MRDFEgain, D_WrDqsDly, TMF_IO_DqVga1stI, TMF_IO_Rx_DqSummer, TMF_IO_DqSummerNCE, TMF_IO_DQR1/R2, TMF_IO_DfeBiasI, TMF_IO_DqBiasI, TMF_IO_DqVgaNCE, TMF_IO_DqOffsetT, TMF_IO_RX_DQSummerI, TMF_IO_DFEGAIN, TMF_IO_DQC/DQC1/DQC2, TMF_IO_DQBIASI, TMF_IO_1stCTLEen, TMF_IO_2ndCTLEdis
**Mode register bits**: MR_BC8OTF, MR2_OP1, MR2_OP7, MR3In, MR3InN, MR3_SETT, MR3_SETB, MR53_OP6B, MR53_OP6B_PHASE, MRS_SETB, MRS_SETT, WPRE2, WPRE3, WPRE4, BC8_Opt, BC8_CN_EDrv, BC8_CN_ODrv, BC8_DQS3p5_EDrv, BC8_DQS3p5_ODrv, Gap0, Gap1, Gap2, Gap3, Gap4, CRC_WR
**Shielding**: m1_shielding, m2_shielding, m3_shielding
**Layout notes**: "Layout notes: WR DQS tree, need match and add shielding", "20240326_redundancy match for DQS tree"
**Version**: Aether 2.2-p001 or above, build 22.60.047, platform linux_rhel60_64 gcc_6.3.0
**Noise strings** (OA binary fragments): gE#, b( b(, 0dK, Pd0, Jfgh, zzzzzzzxxtvvtt,nnnmmm, BBB, ppp, etc.

## Circuit function (from msg#69 final analysis)
DDR4 Write DQS (Write DQS) full path top-level integration:
- Digital delay line `D_WrDqsDly` → 4-phase DQS generation (DQS_0/90/180/270 + delayed DQS_xD) → 8 byte-lane write DQS tree WR_DQS0–7 + DM lane WR_DQSDM → M4 routing RC model IO_DqsM4RcModelV2 → DQS receiver IO_DqsRcvTop (input buffer + CTLE cm1_io_DqsIbCtleC + offset/DCA calibration)
- Training loopback IO_TrnLoopbackDqs, write leveling IO_TMF_WLDQSB, DQS/DM redundancy IO_DqsDmRedundancy, NBTI stress IO_NBTI_WDQS, DFE gain IO_MRDfeGain
- DQ RX test controls: IO_DqRcv + TMF_IO_DqVga1stI / Rx_DqSummer / DqVgaNCE / DqOffsetT / DfeBiasI, DFE_TAP1_ENT

## Bridge diagnosis (harness, NOT used in case)
Aether bridge service down: pyAether 172.16.8.12:58537 + SKILL 172.16.8.12:25069 connection refused. ip_port.json points to desktop 172.16.8.12 (user's Aether machine), not LSF node 10.129.2.13. Aether session 2026-10-28 09:54 (2025.06.sp3.hf1), DM license valid to 2026-10-31. Fix: set CXMT_START_EDA_AGENT_SERVER=1 before launching Aether, or run start_bridge_in_aether.py in Aether CIW.

## Case synthesis decision
- **B-档 synthesized** (trace has no single clean accepted artifact; user ended after receiving analysis text)
- Grounded on real sch.oa strings dump (469 strings, verbatim from trace msg#57 tool_result)
- SUT writes `sch_inventory_extract.py`: CLI 1 arg <strings_file>, stdlib-only, parses noisy OA binary strings → structured JSON inventory (top_cell / instances / signal_nets / pin_count / techlib_refs / module_refs / mode_register_bits / shielding_nets / version_info / circuit_function / layout_notes)
- A = real WRDQS_Full_path strings (DDR4 write DQS, top_cell=WRDQS_Full_path, 259 pins, DQS nets, dqs_write_path)
- Hidden B = synthesized RDDQ_Full_path strings (DDR4 read DQ, top_cell=RDDQ_Full_path, 157 pins, DQ/RD_DQ nets, dq_read_path, +I_IO_DqVga/Slicer/Summer/Preamp/BiasGen/DqDfe instances) — fully reparameterized
- Hidden B_broken = no top_cell, no I_IO_* instances → sentinel for empty handling
- DISTINCT from r214 YamlToGds / r213 InvLayoutGen (layout_aether GDS/YAML generation) — this is OA-binary-strings parsing + circuit inventory classification, not layout generation
