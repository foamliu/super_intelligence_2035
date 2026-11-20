#!/usr/bin/env python3
"""r846 档1 layer normalize batch21 — apply layer to 7 remaining missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

Three-mode manual review (承 r841/r843/r844) on top of classifier
layer_classify_r839.py:

  Mode 1 (variable-blind-spot): HSPICE=os.environ.get(...) + subprocess.run([HSPICE,...])
    HITS:
      - VwlpPumpReport-001: `HSPICE = os.environ.get("HSPICE_BIN","hspice")` +
        `subprocess.run([HSPICE,"-i",dp,"-o",...])` + cond m "L2 independent hspice
        re-run" ⇒ L2 (classifier missed: var name "HSPICE" not literal binary name;
        VAR_ASSIGN_RE in classifier does not catch `os.environ.get` default fallback)
      - VwlpRefDeckSet-001: `HSPICE = os.environ.get("HSPICE","hspice")` +
        `subprocess.run([HSPICE, base, "-o", label], ...)` + cond h/i/j/k/l
        "deck did not conclude in HSPICE" ⇒ L2

  Mode 2 (function-call-blind-spot): def fn() returns binary, subprocess.run([fn(),...])
    HITS:
      - VwlpRefDeckSet-001: `def run_hspice(deck, workdir, label, ...)` wraps
        `subprocess.run([HSPICE, base, "-o", label], ...)` ⇒ L2 (same case as Mode 1,
       双重命中: variable + function-call wrapper; classifier regex does not follow
        function definitions)

  Mode 3 (candidate-internal-blind-spot): check only runs [sys.executable, script, ...]
    but candidate script internally spawns EDA binary per prompt
    NO HITS in batch21:
      - VsimFinesimAdapt-001: prompt = refactor Perl vsim script for FineSim TB
        generation; candidate outputs adapted Perl script, no sim run; check parses
        Perl (subprocess [perl, "-c", path]) + runs candidate generator → L1
      - VthOverrideHowtoGuide-001: prompt = write Python how-to guide for redefining
        vth0 in .sp; candidate outputs structured guide JSON; no sim run → L1
      - XaLogCompare-001: prompt = write Python tool to compare two xa.log files;
        candidate parses logs → L1
      - XmelabCuvpomPortDiag-001: prompt = parse xmelab log, produce structured
        diagnostic; candidate parses log → L1
      - WvModalPopupTclFix-001: prompt = fix Tcl script for WaveView modal popup;
        0 EDA binary in test (only tclsh + sys.executable) → L1

Final batch21 layer dist: 5 L1 + 2 L2 (VwlpPumpReport / VwlpRefDeckSet)
After batch21: has_layer 388 → 395 / 395 = 100% (miss 7 → 0, 全量收口)
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

# (case_id, layer, reason)
BATCH21 = [
    ("VsimFinesimAdapt-001", "L1",
     "offline python/perl parsing: check runs [sys.executable, script, ...] + "
     "[perl, '-c', path]; candidate = Perl vsim refactor for FineSim TB gen, no sim"),
    ("VthOverrideHowtoGuide-001", "L1",
     "offline python: check runs [sys.executable, script_path, ...]; candidate = "
     "vth0-override how-to guide generator (BSIM4 .sp structured guide), no sim"),
    ("VwlpPumpReport-001", "L2",
     "L2 variable-blind-spot: HSPICE=os.environ.get('HSPICE_BIN','hspice') + "
     "subprocess.run([HSPICE,'-i',dp,'-o',...]) + cond m 'L2 independent hspice "
     "re-run' on B first-corner deck (classifier missed: var name not literal bin)"),
    ("VwlpRefDeckSet-001", "L2",
     "L2 variable-blind-spot + function-call-blind-spot: HSPICE=os.environ.get("
     "'HSPICE','hspice') + def run_hspice wraps subprocess.run([HSPICE, base, "
     "'-o', label]) + cond h/i/j/k/l 'deck did not conclude in HSPICE' (tran/dc/"
     "psrr/ac + B tran re-run)"),
    ("WvModalPopupTclFix-001", "L1",
     "offline python+tclsh: check runs [tclsh] + [sys.executable, '-c', ...]; "
     "0 EDA binary in test (WaveView Tcl modal-popup fix)"),
    ("XaLogCompare-001", "L1",
     "offline python: check runs [sys.executable, tool_path, ref_log, cmp_log, "
     "out_json]; candidate = FineSim XA log diff tool, parses logs only, no sim"),
    ("XmelabCuvpomPortDiag-001", "L1",
     "offline python: check runs [sys.executable, script, log, '-o', out_path]; "
     "candidate = xmelab CUVPOM port diagnostic, parses log only, no sim"),
]

def main():
    applied = 0
    skipped = 0
    for cid, layer, reason in BATCH21:
        fpath = os.path.join(CASES_DIR, f"EDA-Eval-DesignFlow-{cid}.json")
        if not os.path.exists(fpath):
            print(f"MISS: {fpath}", file=sys.stderr)
            continue
        with open(fpath) as f:
            c = json.load(f)
        md = c.get("metadata", {})
        if md.get("layer"):
            print(f"SKIP (already {md['layer']}): {cid}")
            skipped += 1
            continue
        md["layer"] = layer
        # keep layer_evidence/layer_method absent (consistent with prior batches:
        # only layer field is set; evidence recorded in this script's docstring +
        # MEMORY流水)
        c["metadata"] = md
        with open(fpath, 'w') as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f"APPLY {layer}: {cid}  [{reason[:80]}]")
        applied += 1
    print(f"\n# batch21 applied: {applied}, skipped: {skipped}")
    # verify
    miss = 0
    total = 0
    from collections import Counter
    cnt = Counter()
    for fname in sorted(os.listdir(CASES_DIR)):
        if not fname.endswith('.json'):
            continue
        total += 1
        c = json.load(open(os.path.join(CASES_DIR, fname)))
        l = c.get("metadata", {}).get("layer")
        cnt[l] += 1
        if not l:
            miss += 1
    print(f"# verify: total={total}, missing_layer={miss}, layer_dist={dict(cnt)}")


if __name__ == "__main__":
    main()
