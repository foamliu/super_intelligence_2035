# Deepread: sid_1793254473946_hjok0 — Pin Access Config Manifest

## Trace
- session: 1793254473946_hjok0.messages.json
- user: e0047434 @ hfeg0pkn002, match_count=89
- domain: layout_aether
- real task: 分析 std-cell pin 可访问性评估脚本（SKILL config_access.il + check_access.il）

## Real scripts (from .75 host hfeg0pkn002:/home/e0047434/work/std_cell/data/Pin_access/)

### config_access.il (68 lines)
SKILL config table `gAccessConfig`:
- tolerance = 0.001
- M1Size = 0.014 (M1 pin square edge)
- M1 = list(yCenterBase=0.046, yPitch=0.028, lPitch=0.204, mMax=4)
- V0D = list(v0dCenterBase=0.0255, v0dPitch=0.051, v0gCenterBase=0.051)
- CM1 = list(width=0.018)
- M2 = list(width=0.031)
- skipPin = list("VPP" "VSS" "VDD" "VBB")

### check_access.il (288 lines)
23 procedures:
- loadAccessConfig / cfgGetA / getToleranceA — config access helpers
- getM1YConfig / getV0DConfig / getCM1Config / getM2Config / getSkipPin — config getters
- buildPinRefTableA — pin reference table (foreach: 82 input / 20 output / 4 inputOutput)
- lookupExpectedA — pin name → expected direction with suffix stripping (_M2/_M3/!)
- shouldSkipPinA / isM2PinA / isM3PinA / isM1PinA — pin classification
- coordInListA / m2Covers / v1Blocks — geometry helpers
- classifyM1PinX — V0D vs V0G grid classification
- v0dPosToIndex / isV0DPos — grid index helpers
- getAccessibleV0DPositions — left/right search with CM1-cut stop, M2-cover skip, V1-block skip
- removeEdgePos — edge position removal
- posWeight — shareCount → weight cond: 1→1.0, 2→0.8, 3→0.4, 4→0.3, 5+→0.2

## Case extraction
Extracted a deterministic **config/metric manifest parser** — parse config table assignments + procedure signatures + weight tiers + pin ref table → JSON manifest. Hidden B uses a variant 28nm HP config with different numbers, extra skip prefix (VNN), different weight tiers, and different pin ref table.

## Deliverable
- `pin_access_manifest.py` (pure stdlib; CLI --config/--check-script/--out)
- `check.py` (14 conditions a–n, self-contained with embedded A/B SKILL text)
- `negative/negative_selftest.py` (5 negatives: empty/only_print/core_deleted/naive_stub/wrong_weights)

## Self-verify
- ref PASS 14/14
- NEG_RC=5/5 all FAIL
- §4.9 three fakes all FAIL
- sha256 deterministic
- check_sha256_prefix: 70bb2b0890de
