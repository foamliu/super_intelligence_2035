#!/usr/bin/env python3
"""Append reference solution, check.py, negatives for AnalogGroupCfgMergeDummy-001."""
import os, json

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = f"{ROOT}/reference/{CASE}"
NEG_DIR = f"{REF_DIR}/negative"
os.makedirs(NEG_DIR, exist_ok=True)

# ============ REFERENCE SOLUTION ============
REF = r'''#!/usr/bin/env python3
"""gg_cfg_merge_verify.py - merge group_generator_cfg patch + audit GG dummies + verdict.

Reads base cfg JSON + patch JSON (deep leaf-merge), layout labels txt, layout & schematic
instance txts. Writes 5 files to --outdir: merged_cfg.json, merge_report.md,
dummy_audit.json, instance_diff.json, verdict.json.
"""
import argparse, json, os, sys


def deep_merge(base, patch):
    """Leaf-override deep merge: patch overrides base at leaf keys; dict nodes merged recursively."""
    if isinstance(base, dict) and isinstance(patch, dict):
        out = dict(base)
        for k, v in patch.items():
            if k in out:
                out[k] = deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    return patch


def diff_paths(base, merged, prefix=""):
    """Return list of (path, old, new) where base != merged (leaf changes only)."""
    changes = []
    if isinstance(base, dict) and isinstance(merged, dict):
        for k, v in merged.items():
            p = f"{prefix}.{k}" if prefix else k
            if k not in base:
                changes.append((p, "<ABSENT>", v))
            elif v != base[k]:
                if isinstance(base[k], dict) and isinstance(v, dict):
                    changes.extend(diff_paths(base[k], v, p))
                else:
                    changes.append((p, base[k], v))
    return changes


def parse_labels(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            t = l = x = y = None
            if line.startswith("text="):
                # text=O layer=MET1 xy=(100,400)
                rest = line
                ti = rest.find("text="); rest = rest[ti+5:]
                sp = rest.find(" layer="); t = rest[:sp]; rest = rest[sp+7:]
                lp = rest.find(" xy="); l = rest[:lp]; rest = rest[lp+4:]
                rest = rest.strip()
                if rest.startswith("(") and rest.endswith(")"):
                    xs = rest[1:-1].split(",")
                    try:
                        x = float(xs[0]); y = float(xs[1])
                    except Exception:
                        pass
            rows.append({"text": t, "layer": l, "xy": (x, y)})
    return rows


def parse_inst_xy(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # name master xy=(x,y)
            parts = line.split()
            if len(parts) < 2:
                continue
            nm = parts[0]; mst = parts[1]
            x = y = None
            if "xy=" in line:
                seg = line[line.find("xy=")+3:].strip()
                if seg.startswith("(") and seg.endswith(")"):
                    xs = seg[1:-1].split(",")
                    try:
                        x = float(xs[0]); y = float(xs[1])
                    except Exception:
                        pass
            rows.append({"name": nm, "master": mst, "xy": (x, y)})
    return rows


def parse_sch(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                rows.append({"name": parts[0], "master": parts[1]})
    return rows


def centroid_xy(insts):
    xs = [r["xy"][0] for r in insts if r["xy"][0] is not None]
    ys = [r["xy"][1] for r in insts if r["xy"][1] is not None]
    cx = sum(xs)/len(xs) if xs else 0.0
    cy = sum(ys)/len(ys) if ys else 0.0
    return cx, cy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--patch", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--layout-inst", required=True)
    ap.add_argument("--sch-inst", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    with open(args.base) as f:
        base = json.load(f)
    with open(args.patch) as f:
        patch = json.load(f)

    merged = deep_merge(base, patch)
    with open(os.path.join(args.outdir, "merged_cfg.json"), "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    changes = diff_paths(base, merged)
    # determine which PatternCfg sections changed / unchanged
    pat = merged.get("PatternCfg", {})
    changed_sections = set()
    for p, _, _ in changes:
        top = p.split(".")[0]
        if top == "PatternCfg":
            sec = p.split(".")[1] if len(p.split(".")) > 1 else ""
            changed_sections.add(sec)
    md = ["# Merge Report", ""]
    md.append("## Changed keys")
    for p, old, new in changes:
        md.append(f"- `{p}`: {json.dumps(old, ensure_ascii=False)} -> {json.dumps(new, ensure_ascii=False)}")
    md.append("")
    md.append("## PatternCfg sections")
    for sec in pat.keys():
        status = "CHANGED" if sec in changed_sections else "unchanged"
        md.append(f"- {sec}: {status}")
    md.append("")
    with open(os.path.join(args.outdir, "merge_report.md"), "w") as f:
        f.write("\n".join(md))

    labels = parse_labels(args.labels)
    o_labels = [r for r in labels if r["text"] == "O"]
    sch = parse_sch(args.sch_inst)
    sch_xy = centroid_xy(parse_inst_xy(args.sch_inst))
    cx, cy = sch_xy
    dist = {"left": 0, "right": 0, "top": 0, "bottom": 0}
    for r in o_labels:
        x, y = r["xy"]
        if x is None or y is None:
            continue
        if x < cx:
            dist["left"] += 1
        else:
            dist["right"] += 1
        if y > cy:
            dist["top"] += 1
        else:
            dist["bottom"] += 1
    audit = {
        "n_labels": len(o_labels),
        "centroid": {"x": cx, "y": cy},
        "labels": [{"text": r["text"], "layer": r["layer"], "xy": list(r["xy"])} for r in o_labels],
        "distribution": dist,
    }
    with open(os.path.join(args.outdir, "dummy_audit.json"), "w") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    lay = parse_inst_xy(args.layout_inst)
    sch_names = set(r["name"] for r in sch)
    lay_names = set(r["name"] for r in lay)
    shared = sorted(sch_names & lay_names)
    layout_only = sorted(r["name"] for r in lay if r["name"] not in sch_names)
    idiff = {
        "schematic": sorted(sch_names),
        "layout_only": layout_only,
        "shared": shared,
    }
    with open(os.path.join(args.outdir, "instance_diff.json"), "w") as f:
        json.dump(idiff, f, indent=2, ensure_ascii=False)

    # verdict
    checks = []
    checks.append({"name": "merged_cfg_valid", "pass": isinstance(merged, dict) and "PatternCfg" in merged})
    # patch applied: every leaf change in patch must equal merged value
    patch_applied = True
    def check_patch(b, p, m):
        nonlocal patch_applied
        if isinstance(p, dict):
            for k, v in p.items():
                if k in m:
                    check_patch(b.get(k, {}), v, m[k])
                else:
                    patch_applied = False
        else:
            if m != p:
                patch_applied = False
    check_patch(base, patch, merged)
    checks.append({"name": "patch_applied", "pass": patch_applied})
    # sibling keys in changed DP section unchanged (other than patched leaves)
    dp_changed = any(p.startswith("PatternCfg.DifferentPair.") for p, _, _ in changes)
    # other PatternCfg sections unchanged
    other_unchanged = True
    for sec in pat.keys():
        if sec == "DifferentPair" and dp_changed:
            continue
        if sec in changed_sections:
            other_unchanged = False
    checks.append({"name": "other_sections_unchanged", "pass": other_unchanged})
    checks.append({"name": "o_labels_found", "pass": len(o_labels) > 0})
    gg_dum = [n for n in layout_only if ("Dum" in n or n.startswith("GG_DUM"))]
    checks.append({"name": "layout_only_gg_dummies", "pass": len(layout_only) > 0 and len(gg_dum) > 0})
    all_sch_in_lay = sch_names.issubset(lay_names)
    checks.append({"name": "all_schematic_in_layout", "pass": all_sch_in_lay})
    # axis check based on patch
    dp_dummy = merged.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {})
    cm_dummy = merged.get("PatternCfg", {}).get("CurrentMirror", {}).get("Matching", {}).get("Dummy", {})
    axis_ok = True
    if str(dp_dummy.get("LeftRight")) == "1":
        axis_ok = dist["left"] > 0 and dist["right"] > 0
    if str(dp_dummy.get("TopBottom")) == "1":
        axis_ok = axis_ok and dist["top"] > 0 and dist["bottom"] > 0
    if str(cm_dummy.get("LeftRight")) == "1" and str(dp_dummy.get("LeftRight")) != "1":
        axis_ok = dist["left"] > 0 and dist["right"] > 0
    checks.append({"name": "dummy_axis_matches_patch", "pass": axis_ok})
    overall = all(c["pass"] for c in checks)
    verdict = {"overall": "PASS" if overall else "FAIL", "checks": checks}
    with open(os.path.join(args.outdir, "verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
'''
with open(f"{REF_DIR}/gg_cfg_merge_verify_ref.py", "w") as f:
    f.write(REF)

# ============ CHECK.PY ============
CHECK = r'''#!/usr/bin/env python3
"""check.py for AnalogGroupCfgMergeDummy-001 (analog_context, B-grade, L1).
check(deliverable, workdir) -> True on pass, raise on fail.
Runs the candidate on hidden B and B2, verifies 16 conditions a-p.
"""
import json, os, sys, zipfile, subprocess, shutil, hashlib, re, tempfile

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
HIDDEN_DIR = os.path.join(workdir, "assets", CASE, "hidden") if os.path.isdir(os.path.join(workdir, "assets", CASE, "hidden")) else None
# fallback: hidden may be staged next to reference
if not HIDDEN_DIR or not os.path.isdir(HIDDEN_DIR):
    # search common locations
    for cand in (os.path.join(workdir, "hidden"),
                 os.path.join(os.path.dirname(__file__), "hidden"),
                 os.path.join(os.path.dirname(__file__), "..", "assets", CASE, "hidden")):
        if os.path.isdir(cand):
            HIDDEN_DIR = cand
            break

CONDITIONS = [
    ("a", "zip no leak (no check/reference/negative/jsonl/hidden inside submit.zip)"),
    ("b", "py_compile candidate script (gg_cfg_merge_verify.py)"),
    ("c", "B-run: exit 0 + produces 5 output files"),
    ("d", "merged_cfg_B.json: valid JSON, deep-merge correct (non-overridden keys preserved)"),
    ("e", "merged_cfg_B: patch leaf overridden to patch value"),
    ("f", "merged_cfg_B: sibling keys in changed section unchanged from base"),
    ("g", "merged_cfg_B: other PatternCfg sections unchanged from base"),
    ("h", "merge_report.md: lists changed key paths + old->new + unchanged sections"),
    ("i", "dummy_audit.json: O labels count > 0, each with xy position"),
    ("j", "dummy_audit.json: distribution matches patch axis (LR->left+right>0, TB->top+bottom>0)"),
    ("k", "instance_diff.json: layout_only count > 0 and names match Dum/GG_DUM pattern"),
    ("l", "instance_diff.json: all schematic instances present in layout"),
    ("m", "verdict.json: overall PASS + all checks pass"),
    ("n", "B2 cross-input: run on B2, merged reflects B2 patch section, DP unchanged, verdict PASS"),
    ("o", "anti-hardcode: candidate source has no A-specific literals; B merged values come from B inputs"),
    ("p", "determinism: 3 B runs -> identical sha256 of all 5 output files"),
]

def fail(cond, msg):
    raise AssertionError(f"[{cond}] {msg}")

def run_case(cand_py, base, patch, labels, li, si, outdir):
    os.makedirs(outdir, exist_ok=True)
    cmd = [sys.executable, cand_py, "--base", base, "--patch", patch,
           "--labels", labels, "--layout-inst", li, "--sch-inst", si, "--outdir", outdir]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc

def deep_merge(base, patch):
    if isinstance(base, dict) and isinstance(patch, dict):
        out = dict(base)
        for k, v in patch.items():
            if k in out:
                out[k] = deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    return patch

def check(deliverable, workdir):
    # extract zip
    tmp = tempfile.mkdtemp(prefix="chk_agcm_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            # cond a: no leak
            leak_pat = re.compile(r"(^|/)(check\.py|reference|negative|\.jsonl|hidden|_reference_check)", re.I)
            leaks = [n for n in names if leak_pat.search(n)]
            if leaks:
                fail("a", f"leak files in zip: {leaks}")
            z.extractall(tmp)
        # find candidate
        cand = None
        for n in names:
            if n.endswith("gg_cfg_merge_verify.py") and "/_negatives/" not in n and "/negative/" not in n:
                cand = os.path.join(tmp, n); break
        if not cand or not os.path.isfile(cand):
            fail("b", f"gg_cfg_merge_verify.py not found in zip; names={names}")
        # cond b: py_compile
        pc = subprocess.run([sys.executable, "-m", "py_compile", cand], capture_output=True, text=True)
        if pc.returncode != 0:
            fail("b", f"py_compile failed: {pc.stderr[:300]}")

        if not HIDDEN_DIR or not os.path.isdir(HIDDEN_DIR):
            fail("c", f"hidden dir not found (looked in workdir/assets and reference/hidden)")

        def run_hidden(tag):
            base = os.path.join(HIDDEN_DIR, f"base_cfg_{tag}.json")
            patch = os.path.join(HIDDEN_DIR, f"patch_{tag}.json")
            labels = os.path.join(HIDDEN_DIR, f"labels_{tag}.txt")
            li = os.path.join(HIDDEN_DIR, f"layout_inst_{tag}.txt")
            si = os.path.join(HIDDEN_DIR, f"sch_inst_{tag}.txt")
            outdir = os.path.join(tmp, f"out_{tag}")
            proc = run_case(cand, base, patch, labels, li, si, outdir)
            return proc, outdir

        # cond c: B-run
        procB, outB = run_hidden("B")
        if procB.returncode != 0:
            fail("c", f"B-run exit={procB.returncode} stderr={procB.stderr[:300]}")
        expected_files = ["merged_cfg.json", "merge_report.md", "dummy_audit.json",
                          "instance_diff.json", "verdict.json"]
        for fn in expected_files:
            if not os.path.isfile(os.path.join(outB, fn)):
                fail("c", f"B-run missing output file: {fn}")

        with open(os.path.join(HIDDEN_DIR, "base_cfg_B.json")) as f: baseB = json.load(f)
        with open(os.path.join(HIDDEN_DIR, "patch_B.json")) as f: patchB = json.load(f)
        with open(os.path.join(outB, "merged_cfg.json")) as f: mergedB = json.load(f)
        expected_mergedB = deep_merge(baseB, patchB)
        # cond d: deep-merge correct
        if mergedB != expected_mergedB:
            fail("d", f"merged_cfg_B != deep_merge(base_B, patch_B); diff keys: " +
                 ", ".join(k for k in set(json.dumps(expected_mergedB, sort_keys=True).split()) - set(json.dumps(mergedB, sort_keys=True).split()) if k))
        # cond e: patch leaf overridden
        dp_lr = str(mergedB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("TopBottom"))
        if dp_lr != str(patchB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("TopBottom")):
            fail("e", f"patch leaf not overridden: DP.Dummy.TopBottom merged={dp_lr} patch={patchB}")
        # cond f: sibling keys unchanged (LeftRight should still be base value "0")
        if str(mergedB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("LeftRight")) != str(baseB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("LeftRight")):
            fail("f", "sibling key DP.Dummy.LeftRight changed unexpectedly")
        if mergedB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Style") != baseB.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Style"):
            fail("f", "sibling key DP.Matching.Style changed unexpectedly")
        # cond g: other sections unchanged
        if mergedB.get("PatternCfg", {}).get("CurrentMirror") != baseB.get("PatternCfg", {}).get("CurrentMirror"):
            fail("g", "CurrentMirror section changed unexpectedly")
        if mergedB.get("PatternCfg", {}).get("Cascode") != baseB.get("PatternCfg", {}).get("Cascode"):
            fail("g", "Cascode section changed unexpectedly")
        # cond h: merge_report.md content
        with open(os.path.join(outB, "merge_report.md")) as f: report = f.read()
        if "Changed keys" not in report or "TopBottom" not in report:
            fail("h", f"merge_report.md missing 'Changed keys' or 'TopBottom': {report[:200]}")
        if "unchanged" not in report.lower():
            fail("h", f"merge_report.md missing 'unchanged' section: {report[:200]}")
        # cond i: dummy_audit O labels
        with open(os.path.join(outB, "dummy_audit.json")) as f: audit = json.load(f)
        if audit.get("n_labels", 0) <= 0:
            fail("i", "dummy_audit n_labels <= 0")
        for lb in audit.get("labels", []):
            xy = lb.get("xy")
            if not isinstance(xy, list) or len(xy) != 2:
                fail("i", f"label xy malformed: {lb}")
        # cond j: distribution matches patch axis (B patch = TopBottom)
        dist = audit.get("distribution", {})
        if dist.get("top", 0) <= 0 or dist.get("bottom", 0) <= 0:
            fail("j", f"B patch TopBottom=1 but distribution top/bottom not both >0: {dist}")
        # cond k: instance_diff layout_only
        with open(os.path.join(outB, "instance_diff.json")) as f: idiff = json.load(f)
        lo = idiff.get("layout_only", [])
        if len(lo) <= 0:
            fail("k", "layout_only empty")
        if not any(("Dum" in n or n.startswith("GG_DUM")) for n in lo):
            fail("k", f"no layout_only name matches Dum/GG_DUM pattern: {lo}")
        # cond l: all schematic in layout
        sch = set(idiff.get("schematic", []))
        shared = set(idiff.get("shared", []))
        if not sch.issubset(shared | set(lo) | set(idiff.get("layout_only", []))):
            # shared should contain all schematic if all sch are in layout
            if not sch.issubset(shared):
                fail("l", f"not all schematic instances in layout: sch={sorted(sch)} shared={sorted(shared)}")
        # cond m: verdict PASS
        with open(os.path.join(outB, "verdict.json")) as f: verdict = json.load(f)
        if verdict.get("overall") != "PASS":
            fail("m", f"verdict overall != PASS: {verdict}")
        if not all(c.get("pass") for c in verdict.get("checks", [])):
            fail("m", f"not all verdict checks pass: {verdict.get('checks')}")
        # cond n: B2 cross-input
        procB2, outB2 = run_hidden("B2")
        if procB2.returncode != 0:
            fail("n", f"B2-run exit={procB2.returncode} stderr={procB2.stderr[:300]}")
        with open(os.path.join(outB2, "merged_cfg.json")) as f: mergedB2 = json.load(f)
        with open(os.path.join(HIDDEN_DIR, "base_cfg_B2.json")) as f: baseB2 = json.load(f)
        with open(os.path.join(HIDDEN_DIR, "patch_B2.json")) as f: patchB2 = json.load(f)
        expected_mergedB2 = deep_merge(baseB2, patchB2)
        if mergedB2 != expected_mergedB2:
            fail("n", "B2 merged_cfg != deep_merge(base_B2, patch_B2)")
        # B2 patch is CurrentMirror.Dummy.LeftRight=1 -> CM should change, DP unchanged
        cm_lr_b2 = str(mergedB2.get("PatternCfg", {}).get("CurrentMirror", {}).get("Matching", {}).get("Dummy", {}).get("LeftRight"))
        if cm_lr_b2 != "1":
            fail("n", f"B2 CurrentMirror.Dummy.LeftRight not overridden to 1: {cm_lr_b2}")
        dp_lr_b2 = str(mergedB2.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("LeftRight"))
        if dp_lr_b2 != str(baseB2.get("PatternCfg", {}).get("DifferentPair", {}).get("Matching", {}).get("Dummy", {}).get("LeftRight")):
            fail("n", "B2 DifferentPair.Dummy.LeftRight changed unexpectedly (should be unchanged)")
        with open(os.path.join(outB2, "verdict.json")) as f: vb2 = json.load(f)
        if vb2.get("overall") != "PASS":
            fail("n", f"B2 verdict != PASS: {vb2}")
        # cond o: anti-hardcode
        with open(cand) as f: src = f.read()
        a_literals = ["VwlpRefAmpIP", "200,400", "260,400", "100,400", "360,400",
                      "AnaWeave_demo"]
        found = [lit for lit in a_literals if lit in src]
        if found:
            fail("o", f"candidate source contains A-specific literals: {found}")
        # B merged values must come from B inputs (already verified by cond d/e/g via deep_merge == expected)
        # additionally check merge_report does not hardcode A cell name
        if "VwlpRefAmpIP" in report:
            fail("o", "B merge_report.md contains A cell name VwlpRefAmpIP (hardcoded)")
        # cond p: determinism
        sha_set = []
        for i in range(3):
            od = os.path.join(tmp, f"det_{i}")
            p = run_case(cand, os.path.join(HIDDEN_DIR, "base_cfg_B.json"),
                         os.path.join(HIDDEN_DIR, "patch_B.json"),
                         os.path.join(HIDDEN_DIR, "labels_B.txt"),
                         os.path.join(HIDDEN_DIR, "layout_inst_B.txt"),
                         os.path.join(HIDDEN_DIR, "sch_inst_B.txt"), od)
            if p.returncode != 0:
                fail("p", f"det run {i} exit!=0: {p.stderr[:200]}")
            h = hashlib.sha256()
            for fn in expected_files:
                with open(os.path.join(od, fn), "rb") as ff:
                    h.update(ff.read())
            sha_set.append(h.hexdigest())
        if len(set(sha_set)) != 1:
            fail("p", f"non-deterministic outputs: {sha_set}")
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    import sys
    deliverable = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    wd = sys.argv[2] if len(sys.argv) > 2 else "."
    ok = check(deliverable, wd)
    print("CHECK:", "PASS" if ok else "FAIL")
'''
with open(f"{REF_DIR}/check.py", "w") as f:
    f.write(CHECK)

print("reference solution + check.py written to", REF_DIR)
