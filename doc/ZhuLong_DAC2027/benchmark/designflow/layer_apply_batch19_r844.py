#!/usr/bin/env python3
"""r844 档1 layer normalize batch19 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch19 = next 12 alphabetical missing-layer cases after r843 batch18
(SimSpecJudge was batch18 end). batch19 = S segment first 12
(SiOutWarnDiag -> SrefOscTranFlowAnalyze), case-insensitive alphabetical.

  Methodology spot-checks (r844) — variable-blind-spot manual review (承 r841/r843):
  Scan all 12 batch19 test fields for `= os.environ.get(` + variable-in-subprocess.

  - **SlicerSizeOpt-001** (L2): test has
      `pr = subprocess.run(["hspice", os.path.basename(dp)], cwd=run_dir, ...)`
      direct string-literal hspice invocation (classifier catches this) ⇒ L2.
  - **Sram6tDcChar-001** (L2): test has
      `HSPICE = os.environ.get("HSPICE", "hspice")` then
      `subprocess.run([HSPICE, os.path.basename(deck), "-o", "jcheck"], ...)`
      variable-blind-spot pattern (classifier misses, manual catches) ⇒ L2.
      This is the THIRD variable-blind-spot hit (承 r841 JitterTieRerun +
      r843 PlatMosThinIdsatIoffSweep ⇒ 3rd hit, systemic confirmation).

  EDA-binary-mention scan (broader than classifier regex) found 4 other cases
  with binary-name mentions, ALL in prompt text / parsed config field values /
  file path strings / parsed simulator-field assertions (NOT subprocess
  invocations) => L1:
  - SioutMemRootcauseDiag-001: "FineSim si.out" in PROMPT text (task
                             description) — candidate parses si.out text => L1
  - SpTemplateOpt-001:         "FineSim template" in PROMPT text — candidate
                             parses template file => L1
  - SpiceCfgDirMerge-001:      "hspice.sim.template" appears as a FILE PATH
                             string the candidate merges/copies (no spawn) => L1
  - SrefOscTranFlowAnalyze-001: "HSPICE"/"Finesim" appear as PARSED simulator
                             field values in B_EXPECT dict (text assertion on
                             parsed JSON config, no spawn) => L1

  The remaining 6 cases (SiOutWarnDiag / SimStatusMonitor /
  SisInstGenSupplyGlobal / SpfNtsvMissingDiag / SpiceDeckPairDiff /
  SramPortExplainQA) have ZERO binary mentions => L1.

  All 12 batch19 cases: check() only does offline python parsing / text
  assertion / subprocess([sys.executable, script, ..]) => L1, EXCEPT
  SlicerSizeOpt-001 (direct hspice subprocess) and Sram6tDcChar-001
  (variable-blind-spot hspice) => L2.

  L2 confirmed list update (承 r843 5 confirmed -> r844 7 confirmed):
  SlicerSizeOpt / Sram6tDcChar + (r841 JitterTieRerun + r843
  PlatMosThinIdsatIoffSweep + r841 SlicerSizeOpt/Sram6tDcChar/Vcc2scActDeckGen
  confirmed list overlap reconciliation: r843 listed 5 = SlicerSizeOpt +
  Sram6tDcChar + Vcc2scActDeckGen + JitterTieRerun + PlatMosThinIdsatIoffSweep;
  r844 batch19 confirms SlicerSizeOpt + Sram6tDcChar (re-verify, both still L2).
  Vcc2scActDeckGen remains pending batch20 (V segment)).
  Variable-blind-spot hits now: r841 JitterTieRerun (1) + r843
  PlatMosThinIdsatIoffSweep (1) + r844 Sram6tDcChar (1) = 3 total across
  batch16/18/19 ⇒ under-count rate ~3/~36 missing-layer cases reviewed ≈ 8%,
  consistent with r843 estimate.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH19 = {
    "SiOutWarnDiag-001": "L1",
    "SimStatusMonitor-001": "L1",
    "SioutMemRootcauseDiag-001": "L1",
    "SisInstGenSupplyGlobal-001": "L1",
    "SlicerSizeOpt-001": "L2",
    "SpTemplateOpt-001": "L1",
    "SpfNtsvMissingDiag-001": "L1",
    "SpiceCfgDirMerge-001": "L1",
    "SpiceDeckPairDiff-001": "L1",
    "Sram6tDcChar-001": "L2",
    "SramPortExplainQA-001": "L1",
    "SrefOscTranFlowAnalyze-001": "L1",
}

ANCHOR = '"metadata": {\n'


def apply_one(name, layer):
    fn = f"EDA-Eval-DesignFlow-{name}.json"
    path = os.path.join(CASES_DIR, fn)
    txt = open(path, encoding="utf-8").read()
    c = json.loads(txt)
    if c.get("metadata", {}).get("layer") is not None:
        return ("SKIP_HAS_LAYER", layer)
    idx = txt.find(ANCHOR)
    if idx < 0:
        return ("NO_ANCHOR", layer)
    insert_at = idx + len(ANCHOR)
    insertion = f'    "layer": "{layer}",\n'
    new_txt = txt[:insert_at] + insertion + txt[insert_at:]
    try:
        json.loads(new_txt)
    except Exception as e:
        return (f"JSON_ERR:{e}", layer)
    open(path, "w", encoding="utf-8").write(new_txt)
    return ("OK", layer)


def main():
    results = []
    for name, layer in BATCH19.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch19:")
    ok = 0
    for name, layer in BATCH19.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH19)} correct")
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    miss = sum(
        1 for f in files
        if json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer") is None
    )
    has = len(files) - miss
    from collections import Counter
    cnt = Counter()
    for f in files:
        ly = json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer")
        cnt[ly] += 1
    print(f"# remaining missing-layer (after batch19): {miss} / {len(files)}  (has layer {has})")
    print(f"# layer dist: {dict(cnt)}")


if __name__ == "__main__":
    main()
