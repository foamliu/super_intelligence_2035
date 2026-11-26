#!/usr/bin/env python3
"""r840 档1 layer normalize batch15 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch15 = next 12 alphabetical missing-layer cases after r839 batch14
(AcSimHowtoGuide..CmlBwExtensionHandbook). Per layer_classify_r839.py all 12
are L1 (offline python parsing/subprocess; no EDA binary in check):

  Methodology spot-checks (r840):
  - CmlSweepHeadroomDiag-001: check subprocess only py_compile (python) -> L1
  - FineSimCoreCounter-001:   check imports subprocess but never calls it;
                              "finesim" only in test-data CSV -> L1
  - CosineWaveAnalyze-001:    check runs `tclsh` (generic TCL shell, not an
                              EDA binary) -> L1

  C->F segment (CmlSweepHeadroomDiag -> FineSimDatacardDiag).
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH15 = {
    "CmlSweepHeadroomDiag-001": "L1",
    "CmpStg1CapAdd-001": "L1",
    "Coord3DProj-001": "L1",
    "CosimPvintUndefDiag-001": "L1",
    "CosineWaveAnalyze-001": "L1",
    "DffSeqTestPipelineExplain-001": "L1",
    "DsaEvalExplainQA-001": "L1",
    "DspfCapExtractValidate-001": "L1",
    "DspfPerfMultiProcDiag-001": "L1",
    "DupSubcktDefDiag-001": "L1",
    "FineSimCoreCounter-001": "L1",
    "FineSimDatacardDiag-001": "L1",
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
    for name, layer in BATCH15.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch15:")
    ok = 0
    for name, layer in BATCH15.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH15)} correct")
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    miss = sum(
        1 for f in files
        if json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer") is None
    )
    has = len(files) - miss
    print(f"# remaining missing-layer (after batch15): {miss} / {len(files)}  (has layer {has})")


if __name__ == "__main__":
    main()
