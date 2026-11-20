# Deepread: 1782871301636_zy2q7 — Level Shifter SPICE Spec Compliance

## Trace metadata
- **session**: 1782871301636_zy2q7
- **user**: e0025730 @ hfeg0plg49 (10.129.8.86)
- **mc**: 29 (netlist:237; schematic:75; analog:8; hspice:5)
- **date**: 2026-07-01
- **agent**: deepseek-v4-flash
- **msgs**: 72, 303KB

## User intent
`启动业务场景: 模拟电路生成` — Start business scenario: analog circuit generation.
The user triggers the **lvlshft** (Level Shifter) circuit design optimization toolchain.

## Toolchain (lvlshft)
Full flow: **SOA selection → SPICE template fill → L/W/S parameter optimization → PVT verification**

### Key files (on .75, 2026-07-01, since cleaned up — reconstructed from trace)
- `lvlshft.py` — main CLI: `list`, `status`, `run`, `result`
- `soa_selector.py` — SOA (Safe Operating Area) transistor selection
- `run_test_only.py` — verification-only (skip optimization, inject params + run SPICE)
- SP templates: `2_delay.sp`, `2_funtrip_.sp`, `2_Ioff.sp`, `2_speed_delay.sp`, `tck50n_delay_aging.sp`
- `result_summary.txt` — verification report
- `final_result.txt` — optimal parameters

### Circuit: Case 3 — Vss2VkbVcc (negative voltage level shifter)
- Input: Vss(0V) → actual input Vcc(1.05V)
- Output: VkbVcc(-0.7V) → actual output Vkb
- Topology: input_p (ptn/600e-9) + protect_p (ptn_lv/300e-9) + feedforward_n + pulldown_n + inv_n + inv_p
- Voltages: pvnn=1.05, pvpp=-0.7, pvppmax=-1.175

### Specification (from `lvlshft.py status`)
| Metric | Spec |
|--------|------|
| Rise delay | ≤ 6.94e-10 s (0.694 ns) |
| Fall delay | ≤ 3.1e-10 s (0.31 ns) |
| Duty cycle | 0.4 ~ 0.6 |
| Ioff | ≤ 5e-9 A (5 nA) |
| Aging degradation | < 20% |

### Optimal parameters & verification results (result_summary.txt)
| Parameter | Value |
|-----------|-------|
| beta1 | 70 |
| S | 0.05 |
| L | 1.30 um |
| W | 1.00 |

| Metric | typ | PVT | Spec | PASS? |
|--------|-----|-----|------|-------|
| Rise Delay | 0.446 ns | **0.573 ns** | ≤0.694 ns | ✅ |
| Fall Delay | 0.149 ns | **0.304 ns** | ≤0.31 ns | ✅ |
| Duty cycle | 44.4%~47.9%@tck=7ns, 49.2%~49.7%@tck=50ns | — | 0.4~0.6 | ✅ |
| Ioff | 0.058 nA | **1.588 nA** | ≤5 nA | ✅ |
| Funtrip | 0.77V | — | — | — |
| Aging max degr | 7.42% (H2H_HV Rise Delay) | — | <20% | ✅ |

### Aging degradation entries (11 patterns × 2 metrics)
Rise Delay: B2B_HV=6.57%, B2B_LV=3.43%, H2H_HV=7.42%, H2H_LV=2.48%, H2L_HV=6.38%, H2L_LV=1.73%, L2H_HV=2.85%, L2H_LV=1.50%, L2L_HV=2.86%, L2L_LV=1.26%, T2T_NV=4.92%
Duty cycle: B2B_HV=0.04%, ..., T2T_NV=0.10%

### SP param injection (run_test_only.py)
`.param s=0.05 W=1.00 L=1.30um beta1=70` injected into all 5 SP files.

## Case design plan
**ID**: EDA-Eval-DesignFlow-LvlShftSpecCompliance-001
**Domain**: spice_sim (L2)
**Task**: Write a compliance checker that parses result_summary.txt, checks each metric vs spec, injects params into SP templates, outputs JSON report.
**Input A**: real result_summary.txt (all PASS) + spec.json + SP templates
**Hidden B**: modified result_summary.txt (Ioff FAIL, aging FAIL, rise_delay FAIL) + different params
**Deliverable**: submit.zip {compliance_checker.py, compliance_report.json, injected_2_delay.sp}
**check.py**: 12 assertions — parse correctness, spec compliance A (all PASS), spec compliance B (specific FAILs), SP injection, output structure.
