# Deepread — 1av5p (zhiguo1w @ hfeg0pjn200 / 10.129.40.209, mc=115, physical_verify)

Session: `1794828924621_1av5p.messages.json` (560951 B / 145 msgs, scp'd to .75 workdir).
Host: `hfeg0pjn200` (10.129.40.209). User: `zhiguo1w` (PDK engineer).
Domain: physical_verify (Calibre TVF Dummy rule deck).

## Real task

`zhiguo1w` maintains the **Calibre TVF Dummy** rule deck for the V1_DDGOA chip at
`/home/pdk/zhiguo1w/Dummy/working/QA/V1_DDGOA_20261110/chip/calibreDummy_chip.rule`
(14.46 MB, symlink → `/home/pdk/peiyaoz/00_Dummy/deck/V1_DDGOA/chip/V1_dummy_ddgoa_v0d5_Rev01/calibreDummy_chip.rule`).

Two user intents in the trace:

1. **Compress < 10 MB + analyze content.** gzip → 1.187 MB
   (sha256 `29fcf81f246b90f9132637e147e5ac1be46422f7b49a0a093c1f79e496089a1c`).
   The deck is a Calibre TVF (Tcl-based Verification Format) script that builds dummy-fill
   mask blocks via `DefMaskBlk` and emits GDSII output layers.
2. **"AT4/PGZ 生成只在 DGX/PDR 区域里"** — verify/constrain AT4/PGZ dummy generation to the
   DGX ∪ PDR regions.

## Key technical findings (from flow.txt)

- **Layer map** (extracted from the deck):
  - `lay_Gen2 = 20_0` → **DGX** (dummy-generation exclusion region)
  - `BORD_PDR = 117_0` → **PDR** (power-delivery region)
  - AT4 output layer = `4_8`
  - PGZ output layer = `30_8`
- **Keep-out mechanism**: each `DefMaskBlk` for AT4/PGZ carries a
  `BORD NOT ( PDR union DGX )` keep-out expression (lines L11018/13698 → L11020/13700 in
  the deck). `BORD NOT (R)` compresses the empty area to the complement-of-R, i.e. fill is
  generated only where `BORD` (chip border) is NOT outside `PDR ∪ DGX` — effectively
  constraining fill to DGX ∪ PDR.
- **Verification** done in the trace: 8 AT4 polygons extracted from the output GDS; all 8
  polygon corners checked by point-in-polygon containment against DGX ∪ PDR rectangles →
  all 8 inside. Confirms the deck already constrains AT4 to DGX ∪ PDR.
- Also explored SOH stripe fill (ARZ/WLZ/NC1/NC2 along array `1_7` etc.) and ATA
  (layer 106) BORD-minus-via/metal keep-out fill — orthogonal sub-topics, not used here.

## Reframe for the benchmark case

Reframe as a **fixture-driven 档B case**: the SUT writes a pure-stdlib
`dummy_region_contain_audit.py` that parses a *simplified* Calibre TVF dummy rule deck
(`lay_<role> = <ld>`, `Region <name> = <ref>`, `DefMaskBlk <name> { output / fill / keepout }`)
+ stream-parses a small GDSII, extracts the `BORD NOT (R1 union R2 …)` keep-out regions per
block, and audits whether every output-layer polygon's vertices fall inside the union of the
keep-out region polygons (ray-casting point-in-polygon). Emits a structured JSON verdict.

- **env_A (visible)**: synthetic small deck with DGX=20_0 / PDR=117_0 / AT4=4_8 / PGZ=30_8
  and a GDS where all 8 AT4 + 4 PGZ polys are inside DGX ∪ PDR → expected PASS.
- **env_B (hidden, inline in check.py)**: different layer numbers (DGX=25_0 / PDR=120_0 /
  AT4=7_8 / PGZ=33_8) and a GDS with **deliberate containment violations** (2 of 6 AT4 polys
  outside DGX ∪ PDR) → expected overall FAIL, AT4 block FAIL (2 violating), PGZ block PASS.

## Cross-shard / dedup check

- 4-shard ledger: `1av5p` only in C (claimed r957).
- 4-shard jsonl `trace_source`: no `1av5p`.
- Same-domain (physical_verify) already-landed cases: LvsDeckPairDiff / DummyDeckStructDiff
  / DrcQaPatternPlanGen / AuxRegionAndOrPlan / SpacePatternPlanner / IddToIpf… — none does
  "DefMaskBlk keep-out region-containment audit with GDS point-in-polygon". Sub-type
  `dummy_defmaskblk_region_contain_audit` is a first.

## Case

- `task_id`: `EDA-Eval-DesignFlow-DummyRegionContainAudit-001`
- `domain`: physical_verify
- `k`: 17
