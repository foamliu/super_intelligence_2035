# Deepread: cvo4q — ellawu LVS PC-split root-cause analyzer

**Trace**: `1794790200671_cvo4q.messages.json` · ellawu @ hfeg0plg79 (10.129.8.122)
**Scanned**: mc=68, keywords netlist:613/lvs:263/calibre:74/drc:28/.spi:10/transistor:6/pex:2/mosfet:2/gdsii:2/.gds:2
**Session size**: 603 KB, 29 messages, 2026-11-16 01:23 UTC (single-turn follow-up)
**Domain**: physical_verify (LVS deck root-cause analysis) — C-shard pure

## Real user task (verbatim)

> U#1 (act): 「这个lvs定义里面能看出来顶层ntk_sv1上的AT4的PC被切成一半的原因吗」
> Attached: `calibreLVS.rule` → `/home/ellawu/.cline/data/sessions/1794790200671_cvo4q/uploads/calibreLVS.rule`

> U#2 (act, 4 min later): 「如果是AT4导致的PC被切一半 原因是什么」

**Attachment**: `calibreLVS.rule` — cxmt10G4plus DRAM Calibre-LVS Rule File by Kobe Weng, 5001 lines, TVF syntax. Real CXMT copyright header.

## Real intent

ellawu (LVS deck author) asks the agent to **read the LVS rule file and identify the rule-level root causes** for why a PC (poly contact) geometry that physically looks continuous on top of `ntk_sv1` device's AT4 (active) layer gets **electrically split into two separate nets** during LVS extraction.

This is **debug-Q&A on LVS deck semantics** — a legitimate real intent per TASK §10 (debug-Q&A is explicitly listed as legal). No tool execution needed; the answer is purely derived from parsing the rule file's TVF/SVRF derivation chain.

## Trace gold (assistant's actual analysis, distilled)

The agent identified **6 distinct rule-level mechanisms** that can split a continuous PC into two electrical networks on NTK_SV1's AT4:

### Mechanism 1 — PCNnet vs PCNnet_MOS contact-split (THE primary cause)
```
2626: PCNnet_MOS = (((PC AND PCN) AND NDIFF) AND NDnet_GATE) NOT PG_NTAP   // gate contact
2627: PCNnet     = ((PC AND PCN) AND NDIFF) NOT PCNnet_MOS                 // S/D contact
2711: CONNECT M0net NDnet       BY PCNnet       // → NDnet (S/D)
2714: CONNECT M0net NDnet_MOS   BY PCNnet_MOS   // → NDnet_MOS (gate terminal)
```
A single PC polygon straddling the gate/diffusion boundary is split: the portion over `NDnet_GATE` (gate) → PCNnet_MOS → NDnet_MOS; the portion over pure S/D → PCNnet → NDnet. Two different electrical nets.

### Mechanism 2 — `DEVTR_mark22` punches NGATE
```
2614: NGATE = (PG_NCH AND (NDIFF NOT INTERACT PCP)) NOT DEVTR_mark22
```
`DEVTR_mark22` removes regions from NGATE. PC contact landing on the punched-out NGATE region loses its gate-side electrical classification → may force the entire PC into PCNnet (S/D) or break the PCNnet_MOS classification.

### Mechanism 3 — `DEVTR_mark37` punches NTK_SV1 recognition
```
2915: NTK_SV1 = (... AND DEVTR_mark5 AND PWnet AND DNW) NOT DEVTR_mark37
```
`DEVTR_mark37` carves a hole in the device recognition region. PC contact landing on the carved-out region is no longer recognised as part of NTK_SV1's diffusion → contact may be orphaned/split.

### Mechanism 4 — `AT4_NCH` geometry discontinuity → NDIFF break
```
2407: AT4  = OR AT4_PCH AT4_NCH
2408: AT4X = OR AT4_PCH AT4_NCH AT4_ARRAY AT4_CMP AT4_SL AT4_DUMMY2
2607: DIFF  = AT4X NOT DEVTR_mark20
2609: NDIFF = ((DIFF AND NSD) NOT PSD) NOT INTERACT DIFF_FLOAT
2627: PCNnet = ((PC AND PCN) AND NDIFF) NOT PCNnet_MOS
```
`PCNnet` depends on `NDIFF` depends on `DIFF` depends on `AT4X` depends on `AT4_NCH`. If `AT4_NCH` has a gap under the PC polygon, `NDIFF` breaks → `PCNnet` is empty in that region → PC contact has no valid diffusion anchor → split.

### Mechanism 5 — `AT4_resistance` excluded from `ND_SD`
```
2634: ND_SD = (NDIFF NOT (PG NOT DEVTR_mark22)) NOT AT4_resistance
2637: NDnet_GATE = ND_SD INTERACT NGATE
```
`AT4_resistance` (MAP 4 DATATYPE 13) is removed from `ND_SD` (electrical S/D region). If PC straddles the AT4_resistance boundary, part of PC sits on `ND_SD` (gate-eligible) and part doesn't → forces PCNnet_MOS / PCNnet split.

### Mechanism 6 — `AT4X` extended-component splicing discontinuity
```
2408: AT4X = OR AT4_PCH AT4_NCH AT4_ARRAY AT4_CMP AT4_SL AT4_DUMMY2
```
`AT4X` ORs 6 sub-layers. If `AT4_CMP`/`AT4_ARRAY`/`AT4_SL`/`AT4_DUMMY2` don't perfectly tile the complement of `AT4_PCH`+`AT4_NCH`, `AT4X` (hence `DIFF`/`NDIFF`) has internal seams → PC straddling a seam splits.

## Reframe decision (档 B, fixture-driven)

Trace gold = **rule-file derivation-chain root-cause analysis** (not tool execution). Reframe as **档 B fixture-driven analyzer**:

- **Deliverable**: `lvs_pc_split_analyzer.py` — Python script that takes `<rule_file> <device_name>` and emits a structured JSON report identifying every rule-level mechanism that can split the device's primary contact layer (PC) into multiple electrical nets.
- **env_A (visible)**: A trimmed slice of the real `calibreLVS.rule` (~140 lines) preserving real layer names (AT4/PC/PCNnet/NTK_SV1/DEVTR_mark22/DEVTR_mark37/AT4_resistance/NDnet_MOS).
- **hidden B**: A different synthesized TVF rule file (~140 lines) with **different layer names + different mark numbers + different device + different extended components** so a hardcode-on-A solution fails:
  - device `ntk_sv3` (vs ntk_sv1), recog layer `NTK_SV3`
  - active `AT5`/`AT5X` (vs AT4/AT4X)
  - contact `PC`/`PCX`/`PCXnet`/`PCXnet_MOS` (vs PC/PCN/PCNnet/PCNnet_MOS)
  - mark layers `DEVTR_mark15` (gate punch, vs mark22) + `DEVTR_mark41` (recog punch, vs mark37) + `DEVTR_mark18` (DIFF punch, vs mark20)
  - resistance `AT5_resistance` (vs AT4_resistance)
  - extended `AT5_PCH/AT5_NCH/AT5_ARRAY/AT5_FILL/AT5_EDGE/AT5_DUMMY` (vs AT4_PCH/AT4_NCH/AT4_ARRAY/AT4_CMP/AT4_SL/AT4_DUMMY2)
  - nets `NXnet`/`NXnet_MOS`/`NXnet_GATE`/`NXnet_D`/`NXnet_S` (vs NDnet...)
  - 5 dimensions of difference: device-name / active-layer-name / contact-net-name / mark-numbers / extended-component-names
- **check.py**: self-contained, embeds B fixture as string literal (no `__file__`), runs candidate script on B via subprocess, parses JSON, asserts ≥15 structural teeth.
- **Anti-hardcode teeth**: B's device name `ntk_sv3` must appear in output (not A's `ntk_sv1`); B's primary active layer `AT5` must appear (not A's `AT4`); B's split net pair `PCXnet`/`PCXnet_MOS` must appear (not A's `PCNnet`/`PCNnet_MOS`); B's mark layers `DEVTR_mark15`/`DEVTR_mark41` must appear (not A's `mark22`/`mark37`); B's resistance layer `AT5_resistance` must appear (not A's `AT4_resistance`).

## Mechanism types the analyzer must classify (independent, each FAILable)

| type | what it detects |
|---|---|
| `contact_split` | a contact net pair `<X>net` / `<X>net_MOS` where `NOT <X>net_MOS` carves the sibling; both must have CONNECT statements routing to different M0-side nets |
| `gate_punch_layer` | a `<gate>` definition containing `NOT DEVTR_mark<N>` |
| `device_recognition_exclusion` | a `<recog>` definition containing `NOT DEVTR_mark<N>` |
| `diff_punch_layer` | a `DIFF`-like definition containing `NOT DEVTR_mark<N>` |
| `resistance_exclusion` | an `ND_SD`-like definition containing `NOT <active>_resistance` |
| `active_layer_discontinuity` | `AT<N>X = OR ...` with >2 sub-layers; `DIFF = AT<N>X NOT ...` |

## Check.py assertions (≥15 teeth, each independent FAILable)

1. JSON parses + has keys {device, primary_active_layer, contact_layer, split_nets, connect_lines, mechanisms}
2. device == "ntk_sv3" (B's actual; NOT A's ntk_sv1)
3. primary_active_layer == "AT5" (B's actual; NOT A's AT4)
4. contact_layer == "PC"
5. split_nets is a 2-element list == {"PCXnet", "PCXnet_MOS"} (B's actual; NOT A's PCNnet)
6. connect_lines has ≥2 entries, each a CONNECT statement routing M0Xnet → different NXnet* via PCXnet* — verified by regex on the literal `CONNECT ... BY PCXnet` and `CONNECT ... BY PCXnet_MOS`
7. mechanisms list has ≥4 entries
8. ≥1 mechanism with type `contact_split` citing line_no + snippet containing `PCXnet_MOS`
9. ≥1 mechanism with type `gate_punch_layer` citing `DEVTR_mark15`
10. ≥1 mechanism with type `device_recognition_exclusion` citing `DEVTR_mark41`
11. ≥1 mechanism with type `resistance_exclusion` citing `AT5_resistance`
12. every mechanism has non-empty `line_no` (int) + `snippet` (str) + `causal_chain` (str)
13. anti-leakage: A-only tokens {`ntk_sv1`, `AT4`, `PCNnet`, `DEVTR_mark22`, `DEVTR_mark37`, `AT4_resistance`} appear in ZERO mechanism snippets
14. 3-seed randomization: shuffle B's rule-line order (3 seeds), re-run, frozenset of mechanism `type|layer` signatures must be identical across seeds
15. (negative-stub guard) output JSON `mechanisms` is not the empty list and not a single identical-repeat (delete-core stub must FAIL this)

## Negatives (all must FAIL check.py)

- **empty_shell.py**: emits `{"mechanisms": []}` → assertion #7 + #15 fail
- **only_print_A.py**: emits the A-answer hardcoded (device=ntk_sv1, AT4, PCNnet, mark22, mark37, AT4_resistance) → assertions #2/#3/#5/#8/#9/#10/#11/#13 all fail (B names mismatch)
- **delete_core.py**: emits 5 mechanism entries but ALL with `type="identical"`, `layer="N/A"`, `snippet=""`, `causal_chain=""` → assertions #8/#9/#10/#11/#12 fail

## Verdict

- ✅ Real trace (ellawu@hfeg0plg79, mc=68, netlist:613/lvs:263 dominant — pure physical_verify/LVS)
- ✅ Real user intent (debug-Q&A on LVS deck — explicitly legal per TASK §10)
- ✅ check() has teeth (≥15 independent assertions + 5-dimension anti-hardcode + 3-seed randomization + 3 negatives)
- ✅ Hidden B differs from A on 5 dimensions (device/active/contact/mark/resistance names) — anti-memorization
- ✅ trace_source metadata preserved (user/host/session_file/match_count/real_task_summary)
- ✅ No collision with existing ellawu case (ImplantFillDeckGen-001 was DRC deck gen, different files/domain)

Case ID: `EDA-Eval-DesignFlow-LvsPcSplitRootCauseAnalyzer-001`
