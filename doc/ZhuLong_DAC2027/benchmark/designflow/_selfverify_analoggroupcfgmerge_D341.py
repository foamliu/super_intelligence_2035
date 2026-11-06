#!/usr/bin/env python3
"""Self-verify AnalogGroupCfgMergeDummy-001:
1. Build ref submit.zip (run ref on B, zip script + 5 outputs)
2. Run check.py on ref submit -> expect PASS (16/16)
3. Run negative_selftest -> expect all 6 FAIL
4. Run §4.9 three false submits (empty/print_expected/ref_core_deleted) -> expect all FAIL
"""
import os, sys, json, zipfile, subprocess, tempfile, shutil

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = f"{ROOT}/reference/{CASE}"
A_DIR = f"{ROOT}/assets/{CASE}"
HID_DIR = f"{A_DIR}/hidden"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.get("timeout", 180), cwd=kw.get("cwd"))

def build_ref_submit(tmp):
    """Run ref on B inputs, zip script + 5 outputs as submit.zip."""
    ref_py = f"{REF_DIR}/gg_cfg_merge_verify_ref.py"
    outdir = os.path.join(tmp, "ref_out")
    os.makedirs(outdir, exist_ok=True)
    p = run([sys.executable, ref_py,
             "--base", f"{HID_DIR}/base_cfg_B.json",
             "--patch", f"{HID_DIR}/patch_B.json",
             "--labels", f"{HID_DIR}/labels_B.txt",
             "--layout-inst", f"{HID_DIR}/layout_inst_B.txt",
             "--sch-inst", f"{HID_DIR}/sch_inst_B.txt",
             "--outdir", outdir])
    assert p.returncode == 0, f"ref B-run failed: {p.stderr}"
    # zip: script as gg_cfg_merge_verify.py + 5 outputs
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.write(ref_py, "gg_cfg_merge_verify.py")
        for fn in ["merged_cfg.json","merge_report.md","dummy_audit.json","instance_diff.json","verdict.json"]:
            z.write(os.path.join(outdir, fn), fn)
    return zp

def stage_workdir(tmp):
    """Create a workdir with assets/CASE/hidden so check.py finds hidden."""
    wd = os.path.join(tmp, "workdir")
    assets_hidden = os.path.join(wd, "assets", CASE, "hidden")
    os.makedirs(assets_hidden, exist_ok=True)
    for fn in os.listdir(HID_DIR):
        shutil.copy(os.path.join(HID_DIR, fn), os.path.join(assets_hidden, fn))
    return wd

def run_check(submit_zip, workdir):
    check_py = f"{REF_DIR}/check.py"
    p = run([sys.executable, check_py, submit_zip, workdir], timeout=300)
    return p

def main():
    tmp = tempfile.mkdtemp(prefix="selfverify_agcm_")
    try:
        # 1. ref submit
        ref_zip = build_ref_submit(tmp)
        print("[1] ref submit.zip built:", os.path.getsize(ref_zip), "bytes")
        # 2. check.py on ref -> expect PASS
        wd = stage_workdir(tmp)
        p = run_check(ref_zip, wd)
        print("[2] check on ref: rc=%d" % p.returncode)
        print("    stdout:", p.stdout[-400:])
        if p.returncode != 0:
            print("    stderr:", p.stderr[-500:])
            print("FAIL: ref check did not PASS")
            return 1
        print("    -> ref PASS OK")

        # 3. negative_selftest
        ns = f"{REF_DIR}/negative_selftest.py"
        pn = run([sys.executable, ns], timeout=400)
        print("[3] negative_selftest: rc=%d" % pn.returncode)
        print("    stdout:", pn.stdout[-800:])
        if pn.returncode != 0:
            print("FAIL: negative_selftest did not PASS (some negative passed check)")
            return 1
        print("    -> all negatives FAIL OK")

        # 4. §4.9 three false submits (already covered by negatives: empty_shell, print_expected, ref_core_deleted)
        #    Re-run explicitly to confirm
        false_subs = ["empty_shell.py", "print_expected.py", "ref_core_deleted.py"]
        for fs in false_subs:
            fs_zip = os.path.join(tmp, f"false_{fs}.zip")
            with zipfile.ZipFile(fs_zip, "w") as z:
                z.write(f"{REF_DIR}/negative/{fs}", "gg_cfg_merge_verify.py")
            pf = run_check(fs_zip, wd)
            status = "FAIL (expected)" if pf.returncode != 0 else "PASS (BAD)"
            print(f"[4] §4.9 false submit {fs}: rc={pf.returncode} -> {status}")
            if pf.returncode == 0:
                print(f"FAIL: false submit {fs} passed check")
                return 1
        print("    -> all 3 false submits FAIL OK")
        print("\n=== SELF-VERIFY PASS ===")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
