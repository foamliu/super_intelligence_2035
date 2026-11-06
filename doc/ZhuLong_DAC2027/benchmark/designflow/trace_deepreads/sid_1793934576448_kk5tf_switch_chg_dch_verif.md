# Deepread: sid_1793934576448_kk5tf (dsgao@hfeg0pkn001) — switch charge/discharge verification

## Trace meta
- session: 1793934576448_kk5tf.messages.json (97 msgs, 479KB, mtime 2026-11-06, NEW via fresh rescan >10:30)
- user: dsgao, host: hfeg0pkn001
- domain: spice_sim (FineSim transient verification of DRAM row-decode power switch)
- tool chain: read_files / list_allowed_files / editor / run_approved_command (python-runner) / search_codebase
- 52 tool calls; run_approved_command drives FineSim V-2023.12-1 via python-runner profile

## User turns (verbatim, A-档 clean needs)
- USER#0: "@/proj/drcpa/V0/workdir/dsgao/R_GidlAryCtrl_switch.netlist 验证一下功能，看一下 GRDecN 的 充放电过程"
  (pure need ✓: gives netlist, asks verify function + observe charge/discharge; no root-cause/fix)
- USER#89: "print 所有节点电压"
  (pure need ✓: asks all node voltages; no root-cause/fix)

## Assistant tool chain (key steps)
1. list_allowed_files / read_files → read R_GidlAryCtrl_switch.netlist (7-transistor switch cell, GrDecPwr output)
2. search_codebase GRDecN/GrDecPwr → found GrDecPwr refs (user said "GRDecN", netlist has "GrDecPwr")
3. read existing testbench (R_GidlAryCtrl_switch_sim_tb.sp), launch_sim.py, parse_single.py, prior sim run (gidlary_sim.pt0/log)
4. read ALPS top-level netlist + GrDecPQ_org_sim.netlist → context (simplified switch vs expanded _sim version)
5. confirm toolchain: finesim V-2023.12-1, model G5_CIP_Model_D5_v0d5_Rev01, calibre runset cxmtG5_CIP
6. **editor → R_GidlAryCtrl_switch_verify_tb.sp** (self-contained TB: charge phase cm1sw=0/cm1_sw_total=0, discharge phase)
7. **editor → run_verify.py** (runner: finesim -i tb -o prefix)
8. run finesim → model-not-found (ptk/ntk unresolved with M-device style)
9. debug: read empty_device.spi, grep models → **root cause: PDK resolves analog primitives as X-subckt-macros, M-device style fails**
10. **editor → R_GidlAryCtrl_switch_x.netlist** (X-device style) → finesim SUCCEEDS
11. read gidl_verify.pt0 → GrDecPwr starts at charged DC ~2.73V, barely moves (can't see charge rise)
12. add .ic v(GrDecPwr)=0 + clean PWL control (charge 0-15n / hold 15-50n / discharge 50-120n / recharge 120-160n) + .probe internal nodes
13. rerun finesim → full charge/discharge waveform captured
14. **editor → analyze_verify.py** → parse pt0, event table + plot (grdecpwr_charge_discharge.png)
15. **A#88 final analysis**: "该电路是一个预充/充电开关: 充电 cm1sw=0/cm1_sw_total=0 → GrDecPwr 上充; 放电 cm1_sw_total=高 → 弱钳位(仅 nA 经二极管链)"
16. **editor → print_all_nodes.py** → print all node voltages at charge state (t=30ns) and discharge-hold state (t=60.7ns)

## Golden result (user-accepted, A#96 node voltage table)
### 充电态 (t=30ns, cm1_sw_total=0)
| node | V | note |
|---|---|---|
| vss! | 0.0000 | gnd |
| vwlp! | 3.4000 | pull-up rail |
| cm1sw | 0.0000 | low=charge enable |
| net5 | 2.1106 | diode MMP0 clamp source ≈ vwlp−\|Vtp\| |
| net0 | 2.0947 | after MMP1 pass |
| **GrDecPwr** | **2.0786** | output cap node, charging (→2.73V asymptote) |
| net2 | −0.202 | MMN0 (discharge) off, floating, slightly neg |
| net3 | 1.1215 | discharge chain mid |
| net9 | 0.8680 | discharge chain bottom |

### 放电保持态 (t=60.7ns, cm1_sw_total=3.40)
| node | V | note |
|---|---|---|
| net0/net5 | 2.4722 | disconnected from GrDecPwr (MMP2 off), floating hold |
| **GrDecPwr** | **2.0824** | stopped charging, clamped, not hard-discharged |
| net2 | 2.0824 | = GrDecPwr (MMN0 Vds≈0) |
| net3 | 1.4478 | discharge chain mid |
| net9 | 0.9344 | discharge chain bottom |

**Key finding**: simplified switch only charges / weakly clamps; does NOT actively discharge to 0 (discharge current only nA through diode chain).

## Case synthesis plan
- **case_id**: EDA-Eval-DesignFlow-SwitchChgDchVerif-001
- **domain**: spice_sim, A-faithful L2
- **prompt**: USER#0 verbatim + USER#89 verbatim ("print 所有节点电压")
- **deliverable**: `switch_chg_dch_verif.py <netlist.sp> <verify_config.json> <out_dir>` — build testbench (.ic from 0 + multi-phase PWL charge/hold/discharge/recharge + .probe + .measure FIND v(node) AT=steady_t for all observe nodes + rise/fall time), run hspice, parse .lis measures, report JSON {method, hspice_ran, charge_state:{node:v}, discharge_state:{node:v}, grdecpwr_charge_v, grdecpwr_discharge_v, charge_rise_time, discharge_fall_time, verdict}
- **portable netlist**: self-contained level-1 MOS switch (charge path PMOS diode+pass, discharge path NMOS switch), NOT the G5_CIP PDK version
- **A/B split**: A = 2-PMOS charge + 1-NMOS discharge, VDD=1.8, phases 0-15n/15-50n/50-120n/120-160n; hidden B = 3-PMOS charge chain + 2-NMOS discharge, VDD=1.2, different sizing/phases/nodes
- **distinct from GrDecPwrVerifTb-001** (a75vy): that case = testbench GENERATOR (secHV ACT/PRE stimulus → deck); this case = functional VERIFICATION + all-node-voltage reporting harness (.ic from 0 + multi-phase + measure FIND AT=steady_t for all nodes). Different session, different user text, different deliverable focus.
- **k assertions** (≥8): zip/py_compile/--help/A run valid/A hspice_ran/A charge nodes present/A charge_v>0.5vdd/A discharge_v<charge/A rise_time>0/B run valid/B hspice_ran/B charge nodes/B charge_v>0.5vdd/cross-input A≠B
