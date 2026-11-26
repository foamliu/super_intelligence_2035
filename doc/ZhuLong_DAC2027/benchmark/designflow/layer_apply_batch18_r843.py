#!/usr/bin/env python3
"""r843 档1 layer normalize batch18 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch18 = next 12 alphabetical missing-layer cases after r842 batch17
(NetlistWLReduce was batch17 end). batch18 = O->S segment
(OdtCtrlLogicAnalyze -> SimSpecJudge), case-insensitive alphabetical.
No Q/R missing-layer cases exist (the next 12 after N fall in O, P, S).

  Methodology spot-checks (r843) — variable-blind-spot manual review (承 r841):
  The regex classifier (layer_classify_r839.py) only catches EDA binaries
  passed as *string literals* in subprocess([..]). It MISSES variable-based
  invocation `HSPICE = os.environ.get("HSPICE_BIN","hspice")` then
  `subprocess.run("{0} {1} -o {2}".format(HSPICE, ..), ..)` (discovered r841
  JitterTieRerun; r843 second hit = PlatMosThinIdsatIoffSweep).
  Manual scan of all 12 batch18 test fields for `= os.environ.get(` +
  variable-in-subprocess found **ONE** hit:

  - **PlatMosThinIdsatIoffSweep-001** (L2): test L55
      `HSPICE = os.environ.get("HSPICE_BIN", "hspice")`
      L104 `subprocess.run("{0} {1} -o {2} > /dev/null 2>&1".format(HSPICE, sp, prefix), ..)`
      condition "m" = "L2 re-verify: check.py independently re-runs HSPICE on
      B's first platform idsat deck". Classifier reported L1 (string-format
      invocation, no ["hspice",..] literal) => L2 under-count. Second
      variable-blind-spot case (after r841 JitterTieRerun) ⇒ confirms r841's
      "variable-blind-spot is systemic" concern for B-domain hspice env-var
      injection (HSPICE_BIN convention).

  EDA-binary-mention scan (broader than classifier regex) found 6 other cases
  with binary-name substrings, ALL in comments / path strings / config field
  names / produced-filename assertions (NOT subprocess invocations) => L1:
  - PlatInvsThick-001:      "run_hspice.sh" is a FILENAME the candidate must
                             produce (assert os.path.isfile) — text assertion,
                             check does not run hspice => L1
  - PrbsTmSimOptAnalysis-001: HSPICE/FineSim in config "simulator" field,
                             sim_root path, model file list, log banner TEXT
                             parsed by candidate — no subprocess => L1
  - PUvddSweep-001:          "xa" only as substring (no \bxa\b word match, no
                             subprocess) => L1
  - PwlFormatConvert-001:    "Custom WaveView PWL export file" — parsing text
                             format description, no invocation => L1
  - SimExitMatrixDiag-001:   "xrun"/"xa" inside a Chinese-prompt path string
                             /proj/.../MatrixRun_Netlist_SpfBa_... — text => L1
  - SimlibMatchAnalyze-001:  "xa" only as substring (no \bxa\b, no subprocess) => L1
  - SimSetupExplainQA-001:   finesim_chkdgt / finesim_mode / finesim_vdd are
                             CONFIG FIELD NAMES parsed from .spf files — no
                             subprocess => L1

  The remaining 4 cases (OdtCtrlLogicAnalyze / PowerNoiseInject /
  ProbeFailDiag / SimSpecJudge) have ZERO binary mentions => L1.

  All 12 batch18 cases: check() only does offline python parsing / text
  assertion / subprocess([sys.executable, script, ..]) => L1, EXCEPT
  PlatMosThinIdsatIoffSweep-001 which really invokes HSPICE => L2.

  L2 confirmed list update (承 r841 4 confirmed -> r843 5 confirmed):
  SlicerSizeOpt / Sram6tDcChar / Vcc2scActDeckGen / JitterTieRerun
  + PlatMosThinIdsatIoffSweep (r843 new). 3 in S->V segment still pending
  (batch19+); variable-blind-spot hits now 2/12 in batch16 + 1/12 in batch18
  ⇒ under-count rate ~8-12% of missing-layer cases, non-negligible.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH18 = {
    "OdtCtrlLogicAnalyze-001": "L1",
    "PlatInvsThick-001": "L1",
    "PlatMosThinIdsatIoffSweep-001": "L2",
    "PowerNoiseInject-001": "L1",
    "PrbsTmSimOptAnalysis-001": "L1",
    "ProbeFailDiag-001": "L1",
    "PUvddSweep-001": "L1",
    "PwlFormatConvert-001": "L1",
    "SimExitMatrixDiag-001": "L1",
    "SimlibMatchAnalyze-001": "L1",
    "SimSetupExplainQA-001": "L1",
    "SimSpecJudge-001": "L1",
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
    for name, layer in BATCH18.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch18:")
    ok = 0
    for name, layer in BATCH18.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "✓" if actual == layer else "✗"
        if actual == layer:
            ok += 1
        print(f"  {mark} {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH18)} correct")
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
    print(f"# remaining missing-layer (after batch18): {miss} / {len(files)}  (has layer {has})")
    print(f"# layer dist: {dict(cnt)}")


if __name__ == "__main__":
    main()
