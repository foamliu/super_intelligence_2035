# h3vpf — joeyl@hfeg0pkn004 — CML ÷2 divider swing-variation sizing-guidance

- session: `1794481033621_h3vpf.messages.json` (203 msgs: 108 user / 95 assistant)
- user/host/ip: joeyl / hfeg0pkn004 / 10.129.2.13
- domain: analog_context (shard D)
- match_count: 39
- ledger status: **case** → `EDA-Eval-DesignFlow-CmlDivSwingVarSizingQA-001` (r755, 2026-11-16)
- case tier: **A-tier** (verbatim user prompt)

## Real task (U#1 verbatim)

> 请看handoff：/ai_sandbox/m2701/V0_DDR4/agentdir/joeyl/HANDOFF_CML_divider_v2.md目前已经可以在5corner下稳定起振，但swing varation特别大，你觉得有办法细调管子的尺寸以减小swing varation吗？

Attached (read from trace tool_result blocks, source .md files on .75 not directly readable):
- `HANDOFF_CML_divider_v2.md` — CML ÷2 divider 全速率 8.8GHz 调参 handoff (v2, 159 lines, 7820 chars)
- `5corner_swing.txt` — 5-corner (TT_45 / FF_-40 / FF_130 / SS_-40 / SS_130) 摆幅/quad 实测表

= **analog-context sizing-guidance produce-task**: 读 handoff.md + 5corner_swing.txt → 结构化 swing-variation 分析 + 晶体管尺寸调整建议 JSON，数据驱动可泛化到 B 变换输入。

## Handoff v2 key contents (A)

- §0 TL;DR: 147~311mV core swing, 5-corner 全锁 (÷2)
- §2.1 finger 调参矩阵: base / t8 / i4 / t8_i4 (4 configs)
- §3.4 5-corner 全锁表: TT_45 258mV / FF_-40 311mV / FF_130 199mV / SS_-40 231mV / SS_130 147mV
- §4.1 推荐配置: `ResCtr0=0` + `nl_tail8` (尾 finger=8, 输入/锁存/选通 finger=8)
- §4.2-4.4 tradeoffs: 尾管 finger 8 → 尾电流翻倍 200→400µA; 静态核心摆幅下降需后级 CML→CMOS buffer; 尾管 DC 静态点仍 Linear
- §5 各管子 W/L: XNM10/XNM11 尾管 width_bias*8=19.2µ nf=8; XNM0/XNM1 输入对 width_input*8=16µ; XNM2/XNM3 锁存对; XNM4/XNM5 时钟选通; XPM0/XPM1 上拉 PMOS 24µ
- §7 未做/下一步: tail4 + ResCtr0=0 + input8 (省功耗); 加 CML→CMOS 输出 buffer

## B transformation (hidden, systematic)

- version: v2 → v3, filename HANDOFF_CML_divider_v2.md → HANDOFF_CML_divider_v3.md
- finger numbers +2 each: base tail4/input8 → tail6/input10; t8 → t10; i4 → i5; t8_i4 → t10_i5
- netlist names: nl_tail8 → nl_tail10, nl_i4 → nl_i5, nl_t8_i4 → nl_t10_i5
- corner swing +14mV each: 258/311/199/231/147 → 272/325/213/245/161 (max 325, min 161, range 164, mean 243.2)
- lo/hi +0.014V, sw37 +1, netab +0.006
- device W/L scaled: width_input 2u→2.5u, width_bias 2.4u→3.0u, finger 8→10; XPM0/XPM1 24µ→30µ
- tail current tradeoff: 200→400µA → 250→500µA
- recommended config: nl_tail8 → nl_tail10, tail_finger 8→10, input_finger 8→10

## Case artifacts

- assets (visible to SUT): `assets/EDA-Eval-DesignFlow-CmlDivSwingVarSizingQA-001/{prompt.txt, task_brief.md, HANDOFF_CML_divider_v2.md, 5corner_swing.txt}`
- hidden (judge workdir only): `assets/.../hidden/{HANDOFF_CML_divider_v3.md, 5corner_swing.txt, hidden_manifest.json}`
- reference: `reference/EDA-Eval-DesignFlow-CmlDivSwingVarSizingQA-001/{swing_sizing_guide.py (data-driven, parses handoff+swing→structured JSON), check.py (16 conditions a..p), negative/{empty.py, hardcode_a.py, always_ok.py}, negative_selftest.py}`

## Verification (r755, 2026-11-16)

- reference solution runs on A: exit 0, parses 5 corners + 5 device_wl rows (incl. XPM0/XPM1 PMOS load) + 4 finger_configs + recommended nl_tail8 + tradeoffs 200→400µA
- reference solution runs on B: exit 0, all B-transformed values (swings 272/325/213/245/161, nl_tail10, tail_finger 10, tradeoff 250→500µA, evidence_chain HANDOFF_CML_divider_v3.md)
- check.py on reference submit.zip: **PASS** (16/16 conditions)
- negative_selftest: all 3 negatives (empty/hardcode_a/always_ok) **FAIL** ✓
- 3 degraded submissions (empty_shell/only_print/deleted_core) all **FAIL** ✓
- anti-hardcode vs A: feeding A inputs as hidden/ → fails cond e (swing 258 ≠ B 272) ✓
- determinism: cond p 3x re-run identical ✓
- k_rationale == k_check == 16 ≥ 8 ✓

## Follow-up turns (NOT used in case, noted for context)

- U#26/U#27: user later asked about skew and swing/Vref sweeps — these are follow-up turns; the primary task for the case is U#1's sizing-guidance Q&A.
