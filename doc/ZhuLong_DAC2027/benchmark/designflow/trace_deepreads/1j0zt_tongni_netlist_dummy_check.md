# 1j0zt deepread — tongni@hfeg0pkn004 (schematic_netlist, D-pure) — r1123

> Deep-read of `1794798805818_1j0zt.messages.json` (606KB, 111 msgs). Claimed r1123.
> **Synthesis plan ready — ETA r1124.** All materials identified + fetched.

## trace identity
- session: `1794798805818_1j0zt.messages.json` (+ 6.08MB `.messages.archive.json` not fetched)
- host: hfeg0pkn004 = 10.129.2.13
- user: tongni
- live path (verified): `/home/tongni/.cline/data/sessions/1794798805818_1j0zt/1794798805818_1j0zt.messages.json`
- keyword profile: netlist:97 / spice:51 / sta:55 / hspice:41 / .subckt:17 / subckt:27 / pin:31 / instance:18 / schematic:16
- ledger: `trace_ledger_D.tsv` status=claimed (r1123, mc=215)

## real user task (1j0zt live part, 111 msgs)
User (tongni) is fixing `r6_amp_dummy_check.py` — a Python script in the `sim-sp-gen` SKILL that analyzes SPICE netlists to identify amplifier matching groups (diff pairs, current mirrors, symmetric loads) and check dummy counts.

**Specific bug this session**: `AG_VnocVdleqVtscRefAmpCore` amplifier has XMM2 (gate=GlbRef10, source=n1, 16f) and XMM3 (gate=GlbRef10, source=nCom, 16f) — a cross-source symmetric load (SL) pair (NMOS cascode loads, same bias but different source nodes). The buggy `fm()` function splits by source (`by_ss`), so each sub-group has only 1 base inst name → filtered by `len(unames)>=2` → SL missed. User said: **"M2和M3 也是需要匹配的"** (idx=77).

**Fix applied (idx=85)**: After per-source SL grouping, add cross-source SL merge — for remaining same-gate unused devices across different sources, if combined ≥2 base inst names + ≥2 sources → merge as cross-source SL (`src=n1+nCom`).

## before/after R6 report (the deliverable signal)
**BEFORE (buggy, idx=37)** — 3 groups, cross-source SL MISSING:
```
AG_VnocVdleqVtscRefAmpCore:
  [DF] diffpair src=ntail: Neg:16f; Pos:16f          members: XMMN4, XMMN5
  [CM] curmirror gate=pmirror src=inh_vdd1+n2+pCom    members: XMM4, XMM5, XMMP1, XMMP2
AG_VtscRefAnalog:
  [SL] symload gate=net036 src=inh_vdd1               members: XMM0, XMMP0   SHORT dum=0
R6: 3 matched structures
```
**AFTER (fixed, idx=87/109)** — 4 groups, cross-source SL present:
```
AG_VnocVdleqVtscRefAmpCore:
  [DF] diffpair src=ntail: Neg:16f; Pos:16f          members: XMMN4, XMMN5      PASS dum=4
  [SL] symload gate=GlbRef10 src=n1+nCom             members: XMM2, XMM3        PASS dum=4
  [CM] curmirror gate=pmirror src=inh_vdd1+n2+pCom    members: XMM4, XMM5, XMMP1, XMMP2  PASS dum=8
AG_VtscRefAnalog:
  [SL] symload gate=net036 src=inh_vdd1               members: XMM0, XMMP0       SHORT dum=0
R6: 4 matched structures, 1 shortfalls
```

## materials (all fetched to .75 workdir, re-fetchable)
1. **FIXED r6_amp_dummy_check.py** (371 lines) — fetched from `tongni@hfeg0pkn004:/home/tongni/.cline/skills/sim-sp-gen/scripts/r6_amp_dummy_check.py` → use as **reference solution**. Re-fetch: `scp 10.129.2.13:/home/tongni/.cline/skills/sim-sp-gen/scripts/r6_amp_dummy_check.py .`
2. **netlist_AG_VnocVdleqVtscRefAmpCore.sp** (157 lines captured from trace idx=47/49 stdout; full subcircuit is 237 lines — the trace excerpt is truncated but contains the critical XMM2/XMM3 cross-source SL pattern + diff pair + CM). Header: `.SUBCKT AG_VnocVdleqVtscRefAmpCore BiasN EnVV GlbRef10 HbiasV Neg Out Pos nCom pCom inh_vdd1 inh_vss`
3. **netlist_AG_VtscRefAnalog.sp** (15 lines captured from trace; full is 42 lines — simple SL pattern XMM0/XMMP0 same source inh_vdd1)
4. **The actual fix diff** (idx=85 editor call) — cross-source SL merge logic added at lines 247-255 of `fm()`:
```python
# Cross-source SL: same gate-bias pair split across different source nets
# e.g. NMOS cascode loads with same bias (GlbRef10) but different sources (n1 vs nCom)
# Each source sub-group alone has only 1 base inst name → filtered out above.
# Merge across sources: treat as one matched load pair.
cross_sgg = [d for d in g if id(d) not in used and is_matching_gate(d["gr"], d["sr"])]
if len(cross_sgg) >= 2:
    unames = set(d["b"] for d in cross_sgg)
    if len(unames) >= 2:
        # ... merge as cross-source SL
```
5. **The SKILL.md acceptance items** (R6 section, idx=7 editor diff) — defines the 4-segment output structure: ① power-transistor exclusion list → ② matching-group summary (type + topology + members) → ③ Pull switch dummy check (1:1) → ④ Dummy per-item check (PASS/SHORT + dummy count).

## case synthesis plan (ETA r1124)
**Case ID**: `EDA-Eval-DesignFlow-D-012` (next D id — verify against D.jsonl tail)
**Domain**: schematic_netlist
**Task reframing** (per r1083 pattern — reframe Q&A/fix to script-deliverable):
> 用户有一个 SPICE netlist 分析脚本 `r6_amp_dummy_check.py`，用于识别放大器子电路中的匹配组（差分对/电流镜/对称负载）并检查 dummy 数量。当前脚本在处理 `AG_VnocVdleqVtscRefAmpCore` 放大器时漏检了 XMM2/XMM3 跨源对称负载对（同 gate GlbRef10、不同 source n1/nCom）。请修复脚本的 `fm()` 函数，增加跨源 SL 合并逻辑，使 R6 报告正确输出 4 个匹配组（差分对 + 跨源 SL + 电流镜 + 另一放大器的 SL）。交付 `outputs/submit.zip`（含修复后的 `r6_amp_dummy_check.py`）。

**Input A (visible to SUT)**:
- `r6_amp_dummy_check_BUGGY.py` — the FIXED script with the idx=85 cross-source SL merge REMOVED (reconstruct by reversing the diff)
- `netlist_A.vtscRef.sp` — the VtscRef netlist (AG_VnocVdleqVtscRefAmpCore + AG_VtscRefAnalog subcircuits, from trace idx=47/49)
- `expected_report_A.txt` — the BEFORE report (3 groups, to show the bug)

**Hidden B (SUT-invisible)**:
- `netlist_B.vtscRef.sp` — a variant with DIFFERENT instance names / sources / gate names but SAME cross-source SL topology (e.g. XMM20/XMM30, gate=GlbRef20, sources nA/nB, different W/L). Must be structurally non-identical (not just rename).
- `expected_report_B.txt` — the correct 4-group report for netlist B

**check() assertions (k≥8)**:
1. zip 内含 `r6_amp_dummy_check.py`
2. 脚本可执行（python3 r6_amp_dummy_check.py netlist_B.sp 无 ERROR）
3. 报告识别出 2 个放大器（AG_VnocVdleqVtscRefAmpCore 变体 + AG_VtscRefAnalog 变体）
4. AG_VnocVdleqVtscRefAmpCore 变体报告 3 个匹配组（DF + cross-source SL + CM）
5. 跨源 SL 组存在且 src 显示为合并形式（如 `src=nA+nB`）
6. 跨源 SL 组 members 包含 2 个不同 base inst name（如 XMM20, XMM30）
7. 差分对组 members 为 2 个不同 base inst name
8. 电流镜组 members ≥3 个不同 base inst name
9. dummy 数量检查：DF dum≥4 PASS、cross-source SL dum≥4 PASS、CM dum≥4 PASS
10. AG_VtscRefAnalog 变体报告 1 个 SL 组（SHORT dum=0）
11. 总匹配结构数 = 4
12. 报告格式为四段结构（功率管排除 → 匹配组汇总 → Pull 开关 → Dummy 逐项）

**Negative samples (≥2)**:
- `neg_print_only.py` — 只打印 expected_report_B.txt 内容，不跑分析 → FAIL (assertion 2,3,5,7,8,9,10,11)
- `neg_core_deleted.py` — 删除 `fm()` 的跨源 SL 合并逻辑 → FAIL (assertion 4,5,6,9,11)
- `neg_hardcode_a.py` — 把 netlist A 的期望输出硬编码 → FAIL on B (assertion 3,4,5,6,7,8,10,11 — A vs B 结构不同)

**§4.9 three-fake**:
- (a) 空壳 → FAIL
- (b) 只 print 期望串 → FAIL (assertion 2 + content mismatch on B)
- (c) 删核心逻辑 → FAIL (assertion 5,6,11)

**test_rationale** (k=12 条断言):
`12 条断言：① zip 含 r6_amp_dummy_check.py ② 脚本可执行无 ERROR ③ 报告识别 2 个放大器 ④ AmpCore 变体报告 3 匹配组(DF+SL+CM) ⑤ 跨源 SL 组 src 为合并形式 ⑥ 跨源 SL 组 2 个不同 base inst ⑦ DF 组 2 个不同 base inst ⑧ CM 组 ≥3 个不同 base inst ⑨ 3 组 dummy≥4 PASS ⑩ VtscRefAnalog 变体 1 个 SL 组 SHORT ⑪ 总匹配结构数=4 ⑫ 报告四段结构`

## feasibility — GO
- All materials re-fetchable: script from tongni home (readable), netlist from trace tool_results (idx=47/49)
- Reference solution = the FIXED script (371 lines) — runs correctly, produces 4-group report
- Hidden B creation = rename instances/sources/gates in netlist_A (mechanical transform, preserves topology)
- No eda_flow/pyAether dependency for check() — pure Python subprocess on netlist file (L1/L2)
- Risk: the 371-line script is complex (parsing, union-find, switch_close resolution); SUT may struggle. But that's the real task difficulty — measure honestly.

## connectivity (19th confirm, this round r1123)
eda_flow MCP OK = .75 reachable (19th confirm r1105-r1123).
This session (GLM-5.2/opencode): open_session 25ms / run_commands 6/6 exit0 hostname=hfhds201 whoami=e0031982 date 2026-11-22 16:02 CST / list_files OK / write_file 70B + read_file round-trip 一致 / declare_done declared=true + close_session cleaned=true / trace summary.tsv 24086 行 + eda_trace_20261122.log 可读 / ssh 10.129.2.13 scp OK (tongni home readable, /proj/dscqa permission-denied = 权限层非不可达).
