#!/usr/bin/env python3
"""r841 档1 layer normalize batch16 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch16 = next 12 alphabetical missing-layer cases after r840 batch15
(CmlSweepHeadroomDiag..FineSimDatacardDiag). F->L segment.

  Methodology spot-checks (r841) — classifier variable-blind-spot discovery:
  The regex classifier (layer_classify_r839.py) only catches EDA binaries
  passed as *string literals* in subprocess([..]). It MISSES variable-based
  invocation `HSPICE = os.environ.get("HSPICE_BIN","hspice")` then
  `subprocess.run([HSPICE, ..])`. Manual scan of all 12 batch16 test fields
  for `= os.environ.get(` + variable-in-subprocess found exactly one:

  - JitterTieRerun-001: check.py line 44 `HSPICE = os.environ.get("HSPICE_BIN",
    "hspice")`, line 201 `subprocess.run([HSPICE, os.path.basename(dp), "-o",
    "./"], ..)` — condition "l" is an L2 independent HSPICE re-run on B first
    corner (proves non-forged sim). => L2 (NOT L1 as classifier reported).

  The r840 L2 list (SlicerSizeOpt/Sram6tDcChar/Vcc2scActDeckGen) was therefore
  INCOMPLETE; JitterTieRerun is a 4th L2 case the classifier under-counted.
  Other 11 batch16 cases verified: subprocess.run([sys.executable, script, ..])
  offline python => L1.

  - G5TbGen-001:           _run(cmd,..) helper, all callers pass
                          [sys.executable, script_path, ..] -> L1
  - GvimCjkConfigGen-001:  inline test field, offline python parsing -> L1
  - IoBufParamTune-001:    inline test field, offline python parsing -> L1

  F->L segment (FinesimLogExplainDiag -> LatchSubcktLocate).
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH16 = {
    "FinesimLogExplainDiag-001": "L1",
    "FsdbScopeSignalLocate-001": "L1",
    "G5TbGen-001": "L1",
    "GmidLutRunSelect-001": "L1",
    "GmidSizingSearch-001": "L1",
    "GvimCjkConfigGen-001": "L1",
    "HspiceAcMergeDiag-001": "L1",
    "HspiceMeasProbeGuide-001": "L1",
    "IddStimHowtoGuide-001": "L1",
    "IoBufParamTune-001": "L1",
    "JitterTieRerun-001": "L2",   # check invokes HSPICE binary (variable-blind-spot)
    "LatchSubcktLocate-001": "L1",
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
    for name, layer in BATCH16.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch16:")
    ok = 0
    for name, layer in BATCH16.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH16)} correct")
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    miss = sum(
        1 for f in files
        if json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer") is None
    )
    has = len(files) - miss
    # layer distribution
    from collections import Counter
    cnt = Counter()
    for f in files:
        ly = json.load(open(os.path.join(CASES_DIR, f))).get("metadata", {}).get("layer")
        cnt[ly] += 1
    print(f"# remaining missing-layer (after batch16): {miss} / {len(files)}  (has layer {has})")
    print(f"# layer dist: {dict(cnt)}")


if __name__ == "__main__":
    main()
