# Deepread: 4kbqy (nevinrao@hfeg0pkn001 mc55) — testmode merge verification

**Session**: 1794293977226_4kbqy.messages.json (1057798 B, 117 msgs / 63 user) @ 10.129.2.10
**Date**: 2026-11-19 r905 triage (revival candidate, parked D 2026-11-14 "testmode merge verification Q&A")
**Verdict**: ❌ NOT造-able as quality k≥8 case — borderline domain + huge real assets + no clean gold deliverable

## Trace flow
- **U1 (real request)**: testmode merge verification spec:
  "1、先单个testmode分别开启，所有六个档位互相切换，覆盖所有的切换场景，查看对应的sel档位是否merge正确；
   2、多个testmode开启，所有六个档位互相切换，覆盖所有的切换场景，查看对应的档位是否正确merge到对应的档位；
   结果确认是否merge正确：被merge的档位和merge到的档位分别开启时，只会出现merge到的档位被拉高的情况，其他未merge的档位正常拉高拉低；
   cm信号解释：cm1_ag_Ldosel0merge1：将s..."
- **U2-U63**: agent tool results — explored `/proj/ddgoa/.../cmds_testmode/` dir, read `TM_1600En.v` / `TM_AbusLatOpen.v` / `tm_config.v` / `allCMAdr_MAandOP.csv` (8000+ rows CM address mapping) / `TM_parameters.v` (7000+ lines) / `TM_parameters_MultiAddr.v`; searched "Ldosel0merge" (all timed out 30s); **U58: write `TM_LdoSelMerge.v` BLOCKED by policy** (writableRoots).
- No clean verification script/report produced; session ended with agent still investigating.

## Domain judgment
- Keywords: analog:1146 / cmos:148 / verilog:89 / drc:32 / netlist:30 / pex:18 / schematic:10 / rtl:10
- `cm1_ag_Ldosel` = analog (ag) category LDO-select merge signal → analog_context flavor
- BUT actual work = reading/writing Verilog test patterns (TM_*.v tasks) for DDR5 testmode switching → verification-pattern work, borderline A-domain (digital/DFT verification) / D-domain (analog signal context)
- Ledger domain was mislabeled `waveform` (no waveview/waveform kw in scan) — real domain = analog_context/verification-pattern

## Why not造-able (this round)
1. **Huge real assets**: allCMAdr_MAandOP.csv (8000+ rows), TM_parameters.v (7000+ lines), multiple TM_*.v — synthesizing a faithful-but-small asset A would lose the merge-verification substance; using real assets = multi-MB (violates trace-faithful A档 asset scope)
2. **No clean gold deliverable**: agent's write was policy-blocked (U58); trace ended mid-investigation; no user-accepted verification script/report to use as gold standard (violates 红线#1 gold-anchoring)
3. **Borderline domain**: Verilog test-pattern verification of analog-merge signals — neither cleanly D (analog circuit) nor cleanly A (digital verification); D-purity low
4. **Budget**: synthesizing a faithful merge-config + verifier + 3 hidden B variants + ≥8-assertion check + negatives in remaining ~12 min infeasible without rushing (rushed case risks k<8 hardgate → incomplete)

## Disposition
- `mark --status parked --force` with deepread note (already D-parked 2026-11-14, note updated r905)
- Not revived. Candidate remains in pool but low priority (would need: small synthesized merge-config + scoping to "produce verifier for N-position merge per spec" C-第三范式, domain re-tag analog_context).
