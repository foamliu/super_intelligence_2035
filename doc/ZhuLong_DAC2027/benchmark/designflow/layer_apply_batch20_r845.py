#!/usr/bin/env python3
"""r845 档1 layer normalize batch20 — apply layer to 12 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
- L3: multi-tool chain + fix + regression

batch20 = next 12 alphabetical missing-layer cases after r844 batch19
(SrefOscTranFlowAnalyze was batch19 end). batch20 = Ssh -> Verdi segment
(case-insensitive alphabetical), 19 -> 7 remaining after this batch.

  Methodology spot-checks (r845) — three blind-spot patterns,承 r841/r843/r844:

  **variable-blind-spot (os.environ.get + variable in subprocess)** —
  classifier (layer_classify_r839.py) misses because subprocess first-arg is a
  VARIABLE, not a string literal; os.environ.get default not scanned either:
  - **StrongarmFomSweep-001** (L2): test has
        HSPICE = os.environ.get("HSPICE_BIN", "hspice")
        subprocess.run([HSPICE, "-i", dp, "-o", os.path.join(run_dir, tag)], ...)
      + check.py independently re-runs HSPICE on B's first sizing point
      (cond m "L2 re-verify: check.py 用自带 hspice runner 在 B 第一个 sizing
      点上独立重跑 HSPICE"). => L2. **4th variable-blind-spot hit** (承 r841
      JitterTieRerun + r843 PlatMosThinIdsatIoffSweep + r844 Sram6tDcChar).
  - **TaperBufOpt-001** (L2): test has
        HSPICE = os.environ.get("HSPICE", "hspice")
        run_hspice(deck, run_dir, 9999, hspice=HSPICE) ->
          subprocess.run([hspice, base + ".sp", "-o", base], ...)
      + check.py independently runs HSPICE on REF design (cond h "check.py
      independently runs HSPICE (subprocess) on the REF design"). => L2.
      **5th variable-blind-spot hit** (variable passed through function
      parameter — deeper nesting than r841/r843/r844 direct-variable form).

  **function-call-blind-spot (function returns binary, called in subprocess)** —
  classifier catches this one via HARDCODED_PATH_RE (the function body has
  hardcoded /apps/.../hspice paths):
  - **Vcc2scActDeckGen-001** (L2): test has
        def _hspice_bin():
            for b in ["hspice", "hspice"]: ...      # shutil.which
            for p in ["/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice",
                      "/apps/synopsys/hspice/bin/hspice"]: ...
            return "hspice"
        subprocess.run([_hspice_bin(), "deck_%s.sp" % tag, "-o", "out_%s" % tag], ...)
      + cond j "L2 hspice parse B tran deck (no syntax error)". => L2.
      Classifier caught via HARDCODED_PATH_RE (r844 flagged this as pending
      batch20 L2; now confirmed).

  **candidate-internal-blind-spot (NEW pattern, first confirmed hit)** —
  check.py itself only spawns python (sys.executable), but the CANDIDATE
  internally invokes a real EDA binary; detected via prompt scan per r839
  classifier comment "candidate script ... itself invokes the binary (we rely
  on ... a scan of the prompt + reference for binary-mention when check only
  runs python)":
  - **VcoKvcoChar-001** (L2): check.py runs candidate via
        subprocess.run([sys.executable, script, params, model, out_dir], ...)
      then checks candidate's self-reported `hspice_ran` flag (cond d/i) +
      ref-value tolerance (cond l: B kvco within REF_B_KVCO +/-30%) +
      anti-fabrication (cond n: A fosc[0] within REF_A_FOSC_0 +/-25%) +
      cross-input guard (cond m: B fosc[0] differs from A by >10%). The
      CANDIDATE internally runs HSPICE (prompt: "自动生成 HSPICE 网表、运行
      HSPICE 仿真、解析振荡频率 fosc"). Per r747 "candidate-internal call"
      => L2. This is the **first confirmed candidate-internal-blind-spot hit**
      (承 r839 classifier comment; classifier regex only scans check.py test
      field, not candidate-internal calls => under-counts this pattern).
      Teeth: a stub setting hspice_ran=True must also match ref fosc/kvco
      within tolerance AND pass cross-input guard — possible but requires
      fabricating matching ref values, so the check has partial teeth (weaker
      than StrongarmFomSweep/TaperBufOpt/Vcc2scActDeckGen where check.py itself
      spawns hspice).

  **EDA-binary-mention scan (broader than classifier regex)** — cases with
  binary-name mentions in test field that are NOT subprocess invocations =>
  L1:
  - TwoStageLogExplainQA-001: "hspice" appears as B_ORACLE dict values
    ("stage1_tool": "hspice", "stage2_tool": "hspice"), config key name
    "HSPICE_BIN", and text assertion `config_vars.get("HSPICE_BIN") in
    ("hspice", "${HSPICE_BIN:-hspice}")` (checking candidate extracted config
    value from shell script) — candidate parses shell script + logs to JSON,
    NO binary spawn => L1.
  - TranStimSync-001: "finesim" appears in path strings ("finesim_A",
    "finesim_B", "hidden/finesim_B") and comments — candidate parses finesim
    si.inp text and edits .tran line; os.environ.get(env_key, "") is for
    _locate_dir (directory path lookup), NOT a binary => L1.
  - VerdiFsdbLoadDiagnose-001: 0 subprocess calls; "verdi" in text only
    (diagnosis/explain task) => L1.
  - TrimMarginSpec-001: "hspice" only in prompt (context: "HSPICE `.measure`
    的结果"); candidate parses existing .lis file (simulation already ran),
    no binary spawn => L1.
  - Vcc2scVarJudge-001: "finesim"/"hspice" only in prompt (user's bsub command
    context); candidate parses existing .mt0 measure file, no binary spawn
    => L1.

  **Zero binary mention** (no EDA binary in test or prompt subprocess path)
  => L1:
  - SshHostAlgDiag-001 / SvUsedModelExtract-001 / TbSpiceMeasureAudit-001:
    check.py only uses sys.executable subprocess (py_compile + run candidate
    python script) => L1.

  All 12 batch20 cases: check.py only does offline python parsing / text
  assertion / subprocess([sys.executable, script, ..]) => L1, EXCEPT:
    - StrongarmFomSweep-001 (variable-blind-spot hspice) => L2
    - TaperBufOpt-001 (variable-through-function-blind-spot hspice) => L2
    - Vcc2scActDeckGen-001 (function-call hspice, classifier caught) => L2
    - VcoKvcoChar-001 (candidate-internal hspice, NEW blind-spot) => L2

  L2 confirmed list update (承 r844 7 confirmed -> r845 11 confirmed):
  r844 had: SlicerSizeOpt / Sram6tDcChar / Vcc2scActDeckGen / JitterTieRerun
            / PlatMosThinIdsatIoffSweep (5)
  r845 batch20 adds 4 NEW: StrongarmFomSweep / TaperBufOpt / VcoKvcoChar
            + Vcc2scActDeckGen (re-confirmed, was pending batch20).
  Total L2 confirmed list (11): SlicerSizeOpt / Sram6tDcChar /
            Vcc2scActDeckGen / JitterTieRerun / PlatMosThinIdsatIoffSweep /
            StrongarmFomSweep / TaperBufOpt / VcoKvcoChar + (3 from earlier
            batches if any — recompute below).

  Variable-blind-spot hits now: r841 JitterTieRerun (1) + r843
  PlatMosThinIdsatIoffSweep (1) + r844 Sram6tDcChar (1) + r845
  StrongarmFomSweep (1) + r845 TaperBufOpt (1) = 5 total across
  batch16-20. Under-count rate ~5/~48 missing-layer cases reviewed ≈ 10%.
  NEW: candidate-internal-blind-spot first hit (VcoKvcoChar-001) — classifier
  regex scans only check.py test field, not candidate-internal calls => this
  pattern is structurally under-counted; future batches must scan prompt for
  "run HSPICE/sim" verbs when check.py only runs python.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH20 = {
    "SshHostAlgDiag-001": "L1",
    "StrongarmFomSweep-001": "L2",
    "SvUsedModelExtract-001": "L1",
    "TaperBufOpt-001": "L2",
    "TbSpiceMeasureAudit-001": "L1",
    "TranStimSync-001": "L1",
    "TrimMarginSpec-001": "L1",
    "TwoStageLogExplainQA-001": "L1",
    "Vcc2scActDeckGen-001": "L2",
    "Vcc2scVarJudge-001": "L1",
    "VcoKvcoChar-001": "L2",
    "VerdiFsdbLoadDiagnose-001": "L1",
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
    for name, layer in BATCH20.items():
        status, lyr = apply_one(name, layer)
        results.append((name, lyr, status))
        print(f"  {name:45s} -> {lyr}  [{status}]")
    print("\n# verify batch20:")
    ok = 0
    for name, layer in BATCH20.items():
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        actual = c["metadata"].get("layer")
        mark = "v" if actual == layer else "X"
        if actual == layer:
            ok += 1
        print(f"  [{mark}] {name:45s} layer={actual} (expect {layer})")
    print(f"\n# applied: {ok}/{len(BATCH20)} correct")
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
    print(f"# remaining missing-layer (after batch20): {miss} / {len(files)}  (has layer {has})")
    print(f"# layer dist: {dict(cnt)}")


if __name__ == "__main__":
    main()
