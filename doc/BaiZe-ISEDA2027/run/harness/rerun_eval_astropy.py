#!/usr/bin/env python3
"""Re-evaluate the 28 astropy patch-not-applied entries (P1-1).

Problem: astropy is NOT installed in the rootfs template's conda env.
  The eval.sh does `pip install -e .[test]` which builds C extensions
  (cfitsio, erfa, expat, wcslib) — this fails/times out inside the sandbox.

Fix: Pre-install astropy in the rootfs template ONCE (with a 3600s timeout),
  then re-eval the 28 instances (pip install -e . will be fast since C exts
  are already built).

Usage:
  HF_HUB_OFFLINE=1 python3 rerun_eval_astropy.py [--limit 5] [--resume] [--skip-prebuild]
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, traceback, ast
from pathlib import Path
from collections import Counter

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

HARNESS_WORK = Path("/nas_train/app.e0031982/harness_work")
ROOTFS_DIR = HARNESS_WORK / "rootfs"
LOGS_EVAL = HARNESS_WORK / "logs_eval_astropy"
RESULTS_JSON = HERE / "kimi_pilot_results.json"
OUTPUT_JSON = HERE / "kimi_pilot_results.astropy.json"
PROXY = "http://172.19.92.25:13128"

ROOTFS_TEMPLATE = ROOTFS_DIR / "astropy__astropy-12907"
TIMEOUT_PREBUILD = 3600
TIMEOUT_EVAL = 1800


def run_cmd(cmd, cwd=None, timeout=300):
    e = os.environ.copy()
    e.setdefault("https_proxy", PROXY)
    e.setdefault("http_proxy", PROXY)
    e.setdefault("no_proxy", "127.0.0.1,localhost")
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, env=e)
        return (p.stdout + p.stderr).decode(errors="replace"), p.returncode
    except subprocess.TimeoutExpired as ex:
        out = ((ex.stdout or b"") + (ex.stderr or b"")).decode(errors="replace")
        return out + "\n[TIMEOUT]", -1


def git_fetch_retry(workdir, base_commit, max_retries=3, timeout=300):
    for attempt in range(1, max_retries + 1):
        for lock in Path(workdir / ".git").glob("*.lock"):
            try: lock.unlink()
            except OSError: pass
        out, rc = run_cmd(["git", "fetch", "--depth=1", "origin", base_commit],
                         cwd=workdir, timeout=timeout)
        if rc == 0: return True, out
        if attempt < max_retries:
            print(f"    [FETCH RETRY {attempt}/{max_retries}] waiting 10s...")
            time.sleep(10)
    return False, out

def prebuild_astropy():
    """Pre-install astropy in the rootfs template using unshare sandbox."""
    print("[PREBUILD] Pre-installing astropy in rootfs template...")
    r = str(ROOTFS_TEMPLATE)
    testbed = ROOTFS_TEMPLATE / "testbed"
    print("  [1] git reset --hard HEAD...")
    run_cmd(["git", "reset", "--hard", "HEAD"], cwd=testbed, timeout=60)
    run_cmd(["git", "clean", "-fdq"], cwd=testbed, timeout=60)
    cmd = (
        f"source /opt/miniconda3/bin/activate && "
        f"conda activate testbed && "
        f"cd /testbed && "
        f"python -m pip install -e .[test] --verbose 2>&1 | tail -50"
    )
    inner = (
        f"mount --bind /usr {r}/usr || exit 11; "
        f"mount --bind {r}/.locale {r}/usr/lib/locale || exit 12; "
        f"mount -t tmpfs tmpfs {r}/tmp || exit 13; "
        f"chroot {r} /usr/bin/env HOME=/tmp TMPDIR=/tmp PIP_NO_INPUT=1 "
        f"http_proxy=http://172.19.92.25:13128 "
        f"https_proxy=http://172.19.92.25:13128 "
        f"PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ "
        f"PIP_NO_BUILD_ISOLATION=1 "
        f"/bin/bash -c {subprocess.list2cmdline([cmd])}"
    )
    argv = ["unshare", "--user", "--map-root-user", "--mount", "--fork",
            "bash", "-c", inner]
    print(f"  [2] pip install -e .[test] (timeout={TIMEOUT_PREBUILD}s)...")
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT_PREBUILD)
        out = (p.stdout + p.stderr).decode(errors="replace")
        print(f"  Done in {time.time()-t0:.0f}s, rc={p.returncode}")
        print(f"  Output tail: {out[-500:]}")
        return p.returncode == 0
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"") + (e.stderr or b"")).decode(errors="replace")
        print(f"  TIMEOUT. Output tail: {out[-500:]}")
        return False



def find_astropy_entries(orig_results):
    """Find astropy patch-not-applied entries from original results."""
    entries = []
    for r in orig_results:
        if 'astropy' not in r.get('repo', ''): continue
        if r.get('classification') != 'patch-but-failed': continue
        ev = r.get('harness_result', {}).get('eval', {})
        if ev.get('patch_applied', False): continue
        pred_file = r.get('harness_result', {}).get('predictions_file', '')
        if not pred_file or not os.path.exists(pred_file): continue
        try:
            preds = json.load(open(pred_file))
            pred = preds[0] if isinstance(preds, list) and preds else preds
            patch = pred.get('model_patch', '')
            if not patch.strip(): continue
            key = f"{r.get('harness','')}|{r.get('instance_id','')}"
            entries.append({
                'instance_id': r.get('instance_id', ''),
                'repo': r.get('repo', ''),
                'harness': r.get('harness', ''),
                'pred_file': pred_file,
                'patch_size': len(patch),
                'old_eval': ev, 'key': key,
            })
        except Exception: pass
    return entries


def setup_rootfs(instance, rootfs_path):
    """Checkout the correct base_commit in the rootfs template."""
    testbed = rootfs_path / "testbed"
    if not testbed.exists():
        return False, f"template testbed missing: {testbed}"
    base_commit = instance["base_commit"]
    run_cmd(["git", "checkout", "-f"], cwd=testbed, timeout=30)
    run_cmd(["git", "clean", "-fdq"], cwd=testbed, timeout=30)
    out, rc = run_cmd(["git", "cat-file", "-t", base_commit], cwd=testbed, timeout=10)
    if rc != 0 or "commit" not in out:
        import glob
        for tmp in glob.glob(str(testbed / ".git" / "objects" / "pack" / "tmp_*")):
            try: os.unlink(tmp)
            except OSError: pass
        for lock in (testbed / ".git").glob("*.lock"):
            try: lock.unlink()
            except OSError: pass
        ok, out = git_fetch_retry(testbed, base_commit, max_retries=3, timeout=300)
        if not ok: return False, f"base_commit fetch failed: {out[:200]}"
    out, rc = run_cmd(["git", "checkout", "-f", base_commit], cwd=testbed, timeout=30)
    if rc != 0: return False, f"git checkout failed: {out[:200]}"
    run_cmd(["git", "clean", "-fdq"], cwd=testbed, timeout=30)
    return True, f"using template {rootfs_path.name}"


def parse_report(report, instance_id):
    result = {"eval_rc": 0}
    inst_report = report.get(instance_id, report) if isinstance(report, dict) else {}
    result["resolved"] = inst_report.get("resolved", False)
    result["patch_applied"] = inst_report.get("patch_successfully_applied", False)
    ts = inst_report.get("tests_status", {})
    f2p = ts.get("FAIL_TO_PASS", {})
    p2p = ts.get("PASS_TO_PASS", {})
    result["f2p_pass"] = len(f2p.get("success", []))
    result["f2p_total"] = len(f2p.get("success", [])) + len(f2p.get("failure", []))
    result["p2p_pass"] = len(p2p.get("success", []))
    result["p2p_total"] = len(p2p.get("success", [])) + len(p2p.get("failure", []))
    return result


def run_reeval_one(instance_row, pred, rootfs_path, run_id, timeout):
    from swebench.harness.utils import make_test_spec
    from r1_eval import r1_run_instance, UnshareSandbox
    test_spec = make_test_spec(instance_row)
    model_name = pred.get("model_name_or_path", "model").replace("/", "__")
    inst_log_dir = LOGS_EVAL / run_id / model_name / test_spec.instance_id
    report = r1_run_instance(
        test_spec=test_spec, pred=pred, rootfs=Path(rootfs_path),
        sandbox_cls=UnshareSandbox, timeout=timeout,
        inst_log_dir=inst_log_dir, skip_patch=False,
        base_commit=instance_row.get("base_commit", ""),
    )
    return report, inst_log_dir


def main():
    ap = argparse.ArgumentParser(description="Re-eval astropy after pre-build fix (P1-1)")
    ap.add_argument("--limit", type=int, default=0, help="Max instances (0=all)")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--skip-prebuild", action="store_true")
    ap.add_argument("--timeout", type=int, default=TIMEOUT_EVAL)
    args = ap.parse_args()

    print("[1/5] Loading SWE-bench dataset (offline)...")
    from datasets import load_dataset
    ds = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    ds_map = {x["instance_id"]: x for x in ds}
    print(f"  Loaded {len(ds)} instances")

    print("[2/5] Pre-building astropy in rootfs template...")
    if args.skip_prebuild:
        print("  SKIPPED (--skip-prebuild)")
    else:
        ok = prebuild_astropy()
        if not ok:
            print("  WARNING: pre-build failed, continuing anyway")

    print("[3/5] Finding astropy patch-not-applied entries...")
    orig_results = json.load(open(RESULTS_JSON))
    entries = find_astropy_entries(orig_results)
    print(f"  Found {len(entries)} re-evaluable entries")

    existing = {}
    if args.resume and OUTPUT_JSON.exists():
        for r in json.load(open(OUTPUT_JSON)):
            k = r.get("key", "")
            if k: existing[k] = r
        print(f"  Resume: {len(existing)} already done")

    if args.limit > 0:
        entries = entries[:args.limit]

    print(f"[4/5] Re-evaluating {len(entries)} astropy entries...")
    results = list(existing.values())
    flipped = 0
    for i, entry in enumerate(entries):
        key = entry["key"]
        if key in existing:
            print(f"  [{i+1}/{len(entries)}] {key} -- SKIP (already done)")
            continue
        inst_id = entry["instance_id"]
        ds_row = ds_map.get(inst_id)
        if not ds_row:
            print(f"  [{i+1}/{len(entries)}] {key} -- SKIP (not in dataset)")
            continue
        print(f"  [{i+1}/{len(entries)}] {key} ({entry['patch_size']}b)...")
        ok, msg = setup_rootfs(ds_row, ROOTFS_TEMPLATE)
        if not ok:
            print(f"    setup_rootfs FAILED: {msg}")
            results.append({"key": key, "error": msg, **entry})
            continue
        try:
            preds = json.load(open(entry["pred_file"]))
            pred = preds[0] if isinstance(preds, list) and preds else preds
        except Exception as e:
            print(f"    pred load FAILED: {e}")
            results.append({"key": key, "error": str(e), **entry})
            continue
        t0 = time.time()
        try:
            report, log_dir = run_reeval_one(ds_row, pred, ROOTFS_TEMPLATE,
                                             "astropy_fix", args.timeout)
            elapsed = time.time() - t0
            new_eval = parse_report(report, inst_id)
            was_r = entry["old_eval"].get("resolved", False)
            is_r = new_eval.get("resolved", False)
            flip = " *** FLIPPED ***" if (is_r and not was_r) else ""
            print(f"    {elapsed:.0f}s, applied={new_eval.get('patch_applied')}, "
                  f"resolved={is_r}, f2p={new_eval.get('f2p_pass')}/{new_eval.get('f2p_total')}{flip}")
            if is_r and not was_r: flipped += 1
            results.append({"key": key, "instance_id": inst_id, "repo": entry["repo"],
                "harness": entry["harness"], "old_eval": entry["old_eval"],
                "new_eval": new_eval, "elapsed_s": round(elapsed, 1)})
        except Exception as e:
            print(f"    eval ERROR: {e}")
            traceback.print_exc()
            results.append({"key": key, "error": str(e), **entry})
        with open(OUTPUT_JSON, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[5/5] Summary: total={len(results)}, flipped={flipped}")
    pa = sum(1 for r in results if isinstance(r.get("new_eval"), dict) and r["new_eval"].get("patch_applied"))
    rs = sum(1 for r in results if isinstance(r.get("new_eval"), dict) and r["new_eval"].get("resolved"))
    er = sum(1 for r in results if "error" in r)
    print(f"  patch_applied={pa}, resolved={rs}, errors={er}")
    print(f"  Output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

