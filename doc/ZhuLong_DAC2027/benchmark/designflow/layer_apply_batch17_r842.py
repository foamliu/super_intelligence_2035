#!/usr/bin/env python3
"""r842 档1 layer normalize batch17 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch17 = next 12 alphabetical missing-layer cases after r841 batch16
(FinesimLogExplainDiag..LatchSubcktLocate, F->L segment). batch17 = L->N
segment (LibCoordMapper -> NetlistWLReduce).

  Methodology spot-checks (r842) — variable-blind-spot manual review:
  The regex classifier (layer_classify_r839.py) only catches EDA binaries
  passed as *string literals* in subprocess([..]). It MISSES variable-based
  invocation `HSPICE = os.environ.get("HSPICE_BIN","hspice")` then
  `subprocess.run([HSPICE, ..])` (discovered r841 JitterTieRerun).
  Manual scan of all 12 batch17 test fields for `= os.environ.get(` +
  variable-in-subprocess found ZERO hits. The only subprocess-variable
  pattern is `PY = sys.executable or "python3"` (LvLvioSweep, MeaNetPathDiag)
  which is offline python => L1. No batch17 case has a variable-blind-spot
  L2 under-count.

  EDA-binary-mention scan (broader than classifier regex) found 4 cases with
  binary-name substrings, ALL in comments / path strings / text-content
  assertions (NOT subprocess invocations):
  - LvLvioSweep-001:    check reads run_all.sh TEXT and asserts the string
                        "finesim -i" appears in it (candidate must PRODUCE
                        that text; check does not run finesim) => L1
  - MeaNetPathDiag-001: "hspice/model.lib" is a model-lib PATH string parsed
                        from a config => L1
  - Mt0MetastabDiag-001: "HSPICE .mt0" in a COMMENT describing what to parse
                        => L1
  - Mt0ParseFix-001:    "FineSim .mt0" in a COMMENT describing what to parse
                        => L1

  All 12 batch17 cases: check() only does offline python parsing / text
  assertion / subprocess([sys.executable, script, ..]) => L1.

  L->N segment (LibCoordMapper -> NetlistWLReduce).
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH17 = {
    "LibCoordMapper-001": "L1",
    "LvLvioSweep-001": "L1",
    "MeaNetPathDiag-001": "L1",
    "ModelLibVerDiff-001": "L1",
    "MosDcGuiTool-001": "L1",
    "Mt0AggMinMax-001": "L1",
    "Mt0FolderAggStat-001": "L1",
    "Mt0MetastabDiag-001": "L1",
    "Mt0ParseFix-001": "L1",
    "NetlistDiffBankLogic-001": "L1",
    "NetlistMisModCompare-001": "L1",
    "NetlistWLReduce-001": "L1",
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
    for name, layer in BATCH17.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch17:")
    ok = 0
    for name, layer in BATCH17.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH17)} correct")
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
    print(f"# remaining missing-layer (after batch17): {miss} / {len(files)}  (has layer {has})")
    print(f"# layer dist: {dict(cnt)}")


if __name__ == "__main__":
    main()
