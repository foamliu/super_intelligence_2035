# Deepread note — i9qdi (BlClampRailDiagQA-001)

**Session**: `1792750940096_i9qdi.messages.json`
**User**: victorq @ hfeg0pkn001 (mc=198)
**Domain**: schematic_netlist (schematic:405 / netlist:272 / pyaether:255 — D-pure)
**Selected round**: r899 (2026-11-18)
**Case built**: `EDA-Eval-DesignFlow-BlClampRailDiagQA-001` (A档, 12 assertions a-l)
**Ledger status**: parked → force-revived (2026-11-18) → case

## Why this candidate

D-pure fresh-ish candidate with highest mc in shard D pool. Originally parked under
the old "D262-peek-unfit" rule (2026-11-05, pre-2026-11-15 reaudit). Under the new
2026-11-11 directive (mc≥10 threshold + 2026-11-15 reaudit allowing revived parked
candidates), i9qdi is the strongest D-pure pick for r899.

## Trace shape (208 msgs, 11 user turns, 1.13MB)

- **msg #0** (U#0 — selected as A档 task): user asks (verbatim)
  「网表：netlist，激励：ideal_stimulus.sp，跑出来的波形图：isotest.fsdb。波形很奇怪，我把BLSG/EQSG给了一个脉冲信号，结果BLa/b就基本被拉到vad2了，之前BLSG/EQSG都接恒定电压，就没这个问题。帮我看下我这个电路有什吗问题吗？」
  → A档: user提出需求 not giving fix, fits A档选轮规则.
- **msg #48** (agent final diagnosis, root cause):
  BLa/b 被钳到 `EQ_power = vap2 = pvblh*0.5 = 0.475V`（数值正好等于 vad2=475mV）。
  机制：感测期间 EQSG 脉冲拉高 → eqsel 均衡管导通 → BLa/b 被 EQ_power 硬钳。
  netlist 行 338: `r0 EQ_power inh_vap2 0`（0欧姆短路 EQ_power 到 inh_vap2）。
  Iso0.sp 行 25: `pvap2 = pvblh*0.5`（pvblh=0.95V → vap2=0.475V）。

## Real netlist sections extracted

- **eqsel subckt** (lines 582-601): ports incl EQSG/EQPower/LBL; NMOS gates LBL→EQPower on EQSG high.
- **blsel_withcap** (lines 914-933): bitline select with cap (BLSG gated).
- **EQ_power 0Ω short** (line 338, repeated 2586/3078/3546/4038): `r0 EQ_power inh_vap2 0`.
- **Rc_CTD_EQS** (lines 1497-1563): RC chain for EQSG pulse shaping.
- **eqsel instances** (lines 2124-2128): 8 instances in SA_unit.
- **SA_unit PreEq** (lines 11562-11563): SaBla/SaBlb also tied to inh_vad2 (secondary, not main cause).
- **Iso0.sp**: `pvap2=pvblh*0.5`, `pvad2=475mv`.
- **ideal_stimulus.sp** (lines 87-121): BLSG/EQSG stimulus — pulsed pwl vs constant.

## Hidden inputs design (B/B2/B3)

Same circuit family, varied to defeat hardcoding of A's answer:

- **B** (primary, parallel scenario): uses `eqsw` subckt instead of eqsel; clamp rail
  `inh_vap3` at 0.3V; EQSG pulsed. Root cause class: `equalizer_clamp_during_sense`.
- **B2** (robustness): keeps `eqsel` subckt but EQSG constant low → no clamp;
  `inh_vss`=0.0V; root: `no_clamp_constant_eqsg`.
- **B3** (cross-input guard): no equalizer subckt at all → root: `no_equalizer_path`.

## Deliverable contract

`outputs/submit.zip` containing:
- `diag_blclamp.py` — `python3 diag_blclamp.py --netlist <p> --stimulus <p>` → JSON stdout
  with fields equalizer_subckt / clamp_rail_net / clamp_rail_voltage_v / eqsg_pulsed /
  root_cause_class.
- `report.md` — diagnosis narrative (≤300 chars, mentions EQ_power or 均衡).

## Check design — 12 assertions (a-l)

a: zip解压含diag+report
b: B 可执行返回 JSON
c: B equalizer_subckt == eqsw
d: B clamp_rail_net == inh_vap3
e: B clamp_rail_voltage_v ~= 0.3
f: B eqsg_pulsed == true
g: B root_cause_class == equalizer_clamp_during_sense
h: B2 eqsg_pulsed == false 且 root == no_clamp_constant_eqsg
i: B2 clamp_rail_voltage_v ~= 0.0
j: B3 root_cause_class == no_equalizer_path
k: report.md 含关键词 EQ_power 或 均衡
l: B2 equalizer_subckt == eqsel

Reference check: 12/12 PASS.
Negative selftest (neg_empty / neg_hardcoded / neg_no_parse): all FAIL check
(none reaches perfect 12/12). Convention follows SpiceSim-001: a negative
FAILS check iff it does not pass ALL assertions.

## Known caveat

neg_hardcoded prints A's answer (eqsel/inh_vap2/0.475/pulsed/equalizer_clamp_during_sense).
By overlap with B (shared pulsed=True, root=equalizer_clamp_during_sense) and B2
(shared equalizer_subckt=eqsel), it coincidentally passes assertions f, g, l — total
6/12. Still classified FAIL because it does not reach 12/12. This is acceptable per
project convention; the structural assertions (a/b/k) and overlap-driven coincidental
passes (f/g/l) are unavoidable for a hardcoded-A stub, but the B-specific assertions
(c/d/e) and B2-specific (h/i) correctly reject it.
