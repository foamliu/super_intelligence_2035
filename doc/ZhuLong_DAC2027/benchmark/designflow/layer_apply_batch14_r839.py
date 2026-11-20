#!/usr/bin/env python3
"""r839 档1 layer normalize batch14 — apply layer to 12 missing-layer B cases.

Inserts `"layer": "<L1|L2>"` as the FIRST key in the metadata block, right
after the `"metadata": {` line, via text insertion (no json round-trip, to
preserve exact formatting of prompt/test strings).

batch14 = first 12 alphabetical missing-layer cases (per r839 classifier):
  10 x L1 (offline python parsing/subprocess, no EDA binary in check)
   2 x L2 (check invokes real hspice binary): C2cRfbCmStab, CdlBulkSanitize

Methodology (r747): layer = whether check() actually runs an EDA binary.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH14 = {
    "AcSimHowtoGuide-001": "L1",
    "AgingDirSeparateTransform-001": "L1",
    "AplmmxGen025RootCause-001": "L1",
    "BlSpfCapClassify-001": "L1",
    "C2cRfbCmStab-001": "L2",
    "CTLETranDeck-001": "L1",
    "CabufPvtDatAudit-001": "L1",
    "CapCharProps-001": "L1",
    "CbrForceMechanismExplain-001": "L1",
    "CdlBulkSanitize-001": "L2",
    "ClampPwrStateExtract-001": "L1",
    "CmlBwExtensionHandbook-001": "L1",
}

ANCHOR = '"metadata": {\n'


def apply_one(name, layer):
    fn = f"EDA-Eval-DesignFlow-{name}.json"
    path = os.path.join(CASES_DIR, fn)
    txt = open(path, encoding="utf-8").read()
    # sanity: not already has layer
    c = json.loads(txt)
    if c.get("metadata", {}).get("layer") is not None:
        return ("SKIP_HAS_LAYER", layer)
    idx = txt.find(ANCHOR)
    if idx < 0:
        return ("NO_ANCHOR", layer)
    insert_at = idx + len(ANCHOR)
    insertion = f'    "layer": "{layer}",\n'
    new_txt = txt[:insert_at] + insertion + txt[insert_at:]
    # verify valid json
    try:
        json.loads(new_txt)
    except Exception as e:
        return (f"JSON_ERR:{e}", layer)
    open(path, "w", encoding="utf-8").write(new_txt)
    return ("OK", layer)


def main():
    results = []
    for name, layer in BATCH14.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    # verify
    print("\n# verify batch14:")
    ok = 0
    for name, layer in BATCH14.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH14)} correct")
    # remaining missing-layer count
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    miss = sum(
        1 for f in files
        if json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer") is None
    )
    print(f"# remaining missing-layer (after batch14): {miss} / {len(files)}")


if __name__ == "__main__":
    main()
