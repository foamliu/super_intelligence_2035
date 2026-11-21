# Deepread — 1x7j0 (rockyf, DDR5 2-step Sa schematic-hierarchy traversal)

- **session**: `1795164931087_1x7j0.messages.json` (81 msgs / 502KB / 2026-11-21)
- **user/host**: rockyf @ hfeg0plg95 (10.129.8.227)
- **match_count**: 149 (drc:380 / cellview:352 / pyaether:109 dominant)
- **shard/domain**: C / layout_aether
- **ledger**: claimed r939 → case `EDA-Eval-DesignFlow-TwoStepSaSchemTrace-001`

## Real user intent (msg 0 + 80)

User pastes a DDR5TOP schematic-hierarchy instance list and asks the agent to
"read the circuit module and analyze the working logic of the **2 step Sa
signal**" (2-step Sa = two-step sense-amplifier control, a DDR5 bank-logic
timing scheme). Msg 80 = "继续" (continue) — session ends mid-analysis of
`R_twoStepSaCtrl_LP` internals.

## Hierarchy traversed (trace msg 57)

```
DDR5TOP (drcoa_top, schematic)
  I_Channel → Channel (drcoa_top)
    I_BnkGTopX4_Top → BnkGTopX4_Top (drcoa_digital)
      I_BnkGTopX4_gut → BnkGTopX4_gut (drcoa_digital)
        I_D_BnkGTop_L → D_BnkGTop_L
          I_D_BankLogicx2 → D_BankLogicx2
            I_D_BankLogic → D_BankLogic (drcoa_digital)
              I_R_RasBnkLogic_LP0212 → R_RasBnkLogic_LP0212
              I_R_SaCntrlBnk_LP     → R_SaCntrlBnk_LP     ★ 2-step Sa cell
                I0                   → R_SensingOnCtrl_LPwr (1st-stage Sa en)
                I_R_twoStepSaCtrl    → R_twoStepSaCtrl_LP   ★ 2-step Sa core (leaf)
                  I0 → R_2StepSA_gut_LPwr (blackbox gut)
```

## pyAether API pattern (msgs 35-66)

- `dbOpenLib(lib,'r')` → emyLib
- `emyCellView.find(lib,cellName,viewName)` → cv (DM container, no getBlock)
- `emyDesign.open(libName,cellName,viewName,viewType,'r')` → design with
  `.instances` / `.nets` / `.terminals` properties
- `ns = pyScript.emyCdbaNS()` for CDBA name resolution
- `it.getTermName(ns, name)` for instTerm names (NOT `getName` on instTerm —
  that raises; `getName` works on emyTerm/emyInst)
- term direction via property `term.direction` (no `getDirection` method)
- pyAether GUI APIs (`dbGetOpenLib`, `os.walk` full-disk) TIMEOUT in sandbox;
  file-system + `emyDesign.open` paths succeed

## Gold analysis (msgs 67-77): 2-step Sa signal flow in R_SaCntrlBnk_LP

**First stage — I0 (R_SensingOnCtrl_LPwr):**
- inputs: WlOn, SaDly, PDN, RstN, RfshIP, AsyncRas (←R_CmAsyncRasGut),
  fnRasCtrl<2>, cm1_ro_WlOn2SaOn<6:0>, cm1_ro_SaNP<4:0>, SenseOffN
- outputs: SanEnint, SapEnint (N/P Sa enables), PreSaOn, SaOnN_LPwr

**Main SaOn path:**
- SaOnN_LPwr → I_R_lvlshftVdly2Vcc → I2 (invGSx2) → I1 (bufLx12) → **SaOn** (out)

**2-step Sa path:**
- I5 (and2): SanEnint & SapEnint → SaEnint
- I_R_trim2ndSaOn_1 (R_trimbuf_2ndSaOnLarge, trim=cm1_ro_2StepSaLarge<3:0>)
  → SaEnintDly (trimmable delay buffer)
- I9 (nor3): cm1_ro_2StepSaLarge<2:0> → TwoStepLargeEnN; I11 (inv) → TwoStepLargeEn
- I6 (mx2): A0=SaEnintDly, A1=SaEnint, S=TwoStepLargeEnN → SaEnintDly2
  (Large-mode enable picks delayed vs undelayed SaEnint)
- **I_R_twoStepSaCtrl (R_twoStepSaCtrl_LP)**:
  - inputs: SanEnIn=SanEnint, SapEnIn=SapEnint, SaEnInDly=SaEnintDly2,
    cm1_ro_2StepSa<3:0>, cm1_rf_Ref2StepSaDis, PulsemodeN, RefExt, ...
  - outputs: **SaOn2nd**, SanEn2, SapEn2, **Ref2StepSA**, cm1_ro_2StepSaN<3>

**2-step Sa control ports (R_SaCntrlBnk_LP / R_twoStepSaCtrl_LP):**
- `cm1_ro_2StepSa<3:0>` (input, 2-step Sa mode config)
- `cm1_ro_2StepSaLarge<3:0>` (input, large-swing config)
- `cm1_rf_Ref2StepSaDis` (input, ref 2-step disable)
- `SaOn2nd` (output, 2nd-step Sa On)
- `Ref2StepSA` (output, Ref 2-step SA)

## Reframe (case synthesis)

Fixture-driven **DDR5 schematic-hierarchy 2-step Sa signal-flow analyzer**.
Agent writes a Python script that loads a `schem_hierarchy.json` fixture
(libraries / cells / ports-by-direction / instances-with-masters / instTerms /
nets), traverses the hierarchy from `top`, identifies 2-step Sa control cells
(port-name regex `2StepSa|SaOn2nd|Ref2StepSA`), builds the subpath from top to
the innermost 2-step Sa cell, traces SaOn2nd signal flow, and emits a JSON
report. env_A = DDR5TOP hierarchy (9 levels, 11 cells, drcoa_top/drcoa_digital);
hidden B = LPDDR5X hierarchy (4 levels, 7 cells, lib_x) — same 2-step Sa
pattern, fully disjoint top/cell/lib/depth names → anti-hardcode.

## Notes

- Trace ends mid-analysis (msg 80 "继续") — no final written deliverable in
  trace; the gold answer is the in-conversation signal-flow map (msgs 67-79).
- pyAether GUI timeouts make a "live pyAether" reframe non-deterministic in the
  sandbox; reframe uses a JSON fixture (deterministic) that mimics what
  pyAether returns, preserving the hierarchy-traversal + 2-step-Sa-identification
  skill being tested.
