# deepread — 62why (hktklin@hfeg0plg87, mc=111) → TapPcellBot-001

**session**: `1795069253162_62why.messages.json` (502KB, 98 msgs, 2 user turns)
**host**: hfeg0plg87, **user**: hktklin
**domain**: layout_virtuoso (SKILL pcell generation)
**keyword profile**: virtuoso:1072;cellview:307;dbcreaterect:233;dbcreatelabel:50;dbcreatepolygon:37;ddgetobj:32;pyaether:29
**shard**: C — claimed r861, case EDA-Eval-DesignFlow-TapPcellBot-001

## Real user intent (trace-faithful)
Turn 1 (brief): "对lacaa_common库的common_tap_L6_H_pcell_bot进行PCELL 化生成SKILL"
Turn 2 (spec): "对lacaa_common库的common_tap_L6_H_pcell_bot进行PCELL 化生成SKILL文件。具体方案是分别设置点选开关选项 ntap_svt,ntap_lvt,ntap_ulvt,ptap_svt,ptap_lvt,ptap_ulvt, ntap_svt开关是要选中NW,NSR,VT PS这三层，ntap_lvt开关要选中NW,NSR,VT PL这三层"

→ PCELL-ize the tap cell `lacaa_common/common_tap_L6_H_pcell_bot` into a SKILL file with 6 boolean point-select switches; each switch, when on, draws a specific set of layers via dbCreateRect inside a pcDefinePCell body.

## Explicit (trace-stated) vs inferred (pattern)
- EXPLICIT: ntap_svt → {NW, NSR, VT PS}; ntap_lvt → {NW, NSR, VT PL}
- INFERRED (clear N/P + VT pattern): ntap_ulvt → {NW, NSR, VT PUL}; ptap_* → {PW, PSP, VT <purpose>}; svt→PS, lvt→PL, ulvt→PUL.
- The assistant's deliverable (common_tap_L6_H_pcell_bot.il, written at trace IDX 74, 11006 chars) confirms this exact mapping.

## Assistant deliverable
- `/ai_sandbox/lacaa/TV1_FS_Virtuoso/agentdir/hktklin/common_tap_L6_H_pcell_bot.il` (pcDefinePCell, 6 boolean params, when(<switch>) branches, dbCreateRect on NW/NSR/VT(PS|PL|PUL)/AA for ntap, PW/PSP/VT/AA for ptap, PRBoundary, labels, +Recreate/Register helpers).
- Supporting explore scripts: explore_lacaa.py, check_cad.py, find_pcell_examples.py (used to discover the pcell API + existing examples).
- Could NOT scp the on-disk .il (permission denied on agentdir); reconstructed the reference from the trace editor write (IDX 74 new_text), which is complete and self-consistent.

## Reframe (why this is a clean produce-task)
- Deliverable = a single SKILL `.il` file (pcell source). No live Virtuoso needed to judge.
- check.py is STATIC source analysis (SKILL can't run without a Virtuoso license in the test env): parses the .il for pcDefinePCell, the 6 boolean switch declarations, and each switch's conditional branch drawing the required layer set.
- 14 teeth (a..n): zip/size/utf8; pcDefinePCell; cell name; library; 6 switch decls; 6 per-switch layer sets; conditional gating; drawing API; N/P polarity asymmetry.
- hidden B = the exact per-switch layer mapping (2 explicit + 4 pattern-inferred), embedded in check.py SWITCH_LAYERS.

## Self-verify
- reference_submit.zip (common_tap_pcell_ref.il) → PASS (all 14 teeth).
- 4 negatives: empty_shell→fail(b), no_ptap→fail(e ptap missing), unconditional→fail(e switches missing), wrong_vt_polarity→fail(f ntap_svt wrong VT) → all FAIL.
- negative_selftest OK.
- End-to-end: jsonl-embedded check.py string run against ref + negatives → ALL GOOD.

## Coverage
- C.jsonl 542→543. This is the first hktklin/tap-pcell case in shard C (no near-dup).
- Note: the jzeng/IMCleAutoVia V4 cluster (00p77=shard A claimed AutoViaV4Diagnose-001, zd8b7/huu52 parked) was investigated first but rejected — 00p77 already claimed in shard A; jx42b (sierraw LPE trend, mc=376) rejected — rich trace but deliverable not extractable (editor new_text not captured for that session's lpe_trend.py + /proj permission denied).
