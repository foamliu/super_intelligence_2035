#!/usr/bin/env python3
"""Re-evaluate the 65 fix1 STILL_NOT_APPLIED entries with C build deps fix (fix3).

Fixes applied (P0 completion, 2026-10-13):
  1. matplotlib (30 entries): testbed_py39 (Python 3.9.20) with qhull+freetype+libpng
  2. scikit-learn (27 entries): testbed_py38 (Python 3.8.20) with numpy+scipy+Cython
  3. sphinx-doc/sphinx (8 entries): force git checkout to correct base_commit

Usage:
  HF_HUB_OFFLINE=1 python3 rerun_eval_fix3.py [--repo matplotlib/matplotlib] [--limit 10] [--resume]
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
LOGS_EVAL = HARNESS_WORK / "logs_eval_fix3"
FIX1_JSON = HERE / "kimi_pilot_results.fix1.json"
FIX2_JSON = HERE / "kimi_pilot_results.fix2.json"
RESULTS_JSON = HERE / "kimi_pilot_results.json"
OUTPUT_JSON = HERE / "kimi_pilot_results.fix3.json"
PROXY = "http://172.19.92.25:13128"

ROOTFS_TEMPLATES = {
    "matplotlib/matplotlib": ROOTFS_DIR / "matplotlib__matplotlib-18869",
    "scikit-learn/scikit-learn": ROOTFS_DIR / "scikit-learn__scikit-learn-10297",
    "sphinx-doc/sphinx": ROOTFS_DIR / "sphinx-doc__sphinx-10325",
}

FIX3_CONFIG = {
    "matplotlib/matplotlib":     {"env_override": "testbed_py39", "extra_pip": "", "no_build_isolation": False},
    "scikit-learn/scikit-learn": {"env_override": "testbed_py38", "extra_pip": "", "no_build_isolation": False},
    "sphinx-doc/sphinx":         {"env_override": "", "extra_pip": "", "no_build_isolation": False},
}

TARGET_REPOS = set(FIX3_CONFIG.keys())
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


def setup_rootfs(instance, rootfs_path):
    """fix3: force git checkout -f to clear dirty state (sphinx fix)."""
    repo = instance["repo"]
    template = ROOTFS_TEMPLATES.get(repo)
    if not template or not Path(template).exists():
        return False, f"no rootfs template for {repo}"
    testbed = template / "testbed"
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
    return True, f"using template {template.name}"


def find_fix3_entries(fix1_results, fix2_results, orig_results, target_repos=None):
    """Find not-applied entries from fix1, excluding fix2 entries."""
    fix2_keys = set()
    for r in fix2_results:
        if "error" in r: continue
        key = r.get("key", "")
        if key: fix2_keys.add(key)
    orig_map = {}
    for x in orig_results:
        key = f"{x.get('harness','')}|{x.get('instance_id','')}"
        orig_map[key] = x
    entries = []
    for r in fix1_results:
        if "error" in r: continue
        ne = r.get("new_eval", {})
        if isinstance(ne, str): ne = ast.literal_eval(ne)
        if ne.get("patch_applied") or ne.get("resolved"): continue
        repo = r.get("repo", "")
        if target_repos and repo not in target_repos: continue
        key = r.get("key", "")
        if key in fix2_keys: continue
        inst_id = r.get("instance_id", "")
        harness = r.get("harness", "")
        orig = orig_map.get(key, {})
        hr = orig.get("harness_result", {})
        if isinstance(hr, str): hr = ast.literal_eval(hr)
        pred_file = hr.get("predictions_file", "")
        if not pred_file or not os.path.exists(pred_file): continue
        try:
            preds = json.load(open(pred_file))
            pred = preds[0] if isinstance(preds, list) and preds else preds
            patch = pred.get("model_patch", "")
            if patch.strip():
                entries.append({
                    "instance_id": inst_id, "repo": repo, "harness": harness,
                    "pred_file": pred_file, "patch_size": len(patch),
                    "old_eval": r.get("old_eval", {}), "fix1_eval": ne, "key": key,
                })
        except Exception: pass
    return entries


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


def run_reeval_one(instance_row, pred, rootfs_path, run_id, timeout,
                   env_override="", extra_pip="", no_build_isolation=False):
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
        env_override=env_override, extra_pip=extra_pip,
        no_build_isolation=no_build_isolation,
    )
    return report, inst_log_dir


def main():
    ap = argparse.ArgumentParser(description="Re-eval after fix3 C build deps fix")
    ap.add_argument("--repo", default=None, help="Limit to a specific repo")
    ap.add_argument("--limit", type=int, default=0, help="Max instances (0=all)")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--timeout", type=int, default=TIMEOUT_EVAL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("[1/4] Loading SWE-bench dataset (offline)...")
    from datasets import load_dataset
    ds = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    ds_map = {x["instance_id"]: x for x in ds}
    print(f"  Loaded {len(ds)} instances")

    print("[2/4] Finding re-evaluable entries from fix1 (excluding fix2)...")
    fix1_results = json.load(open(FIX1_JSON))
    fix2_results = json.load(open(FIX2_JSON)) if FIX2_JSON.exists() else []
    orig_results = json.load(open(RESULTS_JSON))
    target_repos = {args.repo} if args.repo else TARGET_REPOS
    entries = find_fix3_entries(fix1_results, fix2_results, orig_results, target_repos)
    print(f"  Found {len(entries)} re-evaluable entries")
    for repo, cnt in Counter(e["repo"] for e in entries).most_common():
        print(f"    {repo}: {cnt}")

    if args.dry_run:
        for e in entries[:20]:
            print(f"  {e['instance_id']} ({e['harness']}) patch={e['patch_size']}B")
        return

    existing = {}
    if args.resume and OUTPUT_JSON.exists():
        existing = {x["key"]: x for x in json.load(open(OUTPUT_JSON))}
        print(f"  [RESUME] {len(existing)} already-completed entries loaded")

    print("[3/4] Setting up rootfs templates...")
    for repo in target_repos:
        template = ROOTFS_TEMPLATES.get(repo)
        print(f"  {repo}: {template.name} {'OK' if template and template.exists() else 'MISSING'}")

    print(f"[4/4] Re-evaluating {len(entries)} entries (timeout={args.timeout}s)...")
    new_results = []
    done = skipped = failed = resolved_new = flipped_new = 0
    t_start = time.time()

    for i, entry in enumerate(entries):
        if args.limit and done + skipped >= args.limit:
            print(f"  --limit {args.limit} reached, stopping.")
            break
        key = entry["key"]
        if key in existing:
            skipped += 1
            if existing[key].get("new_eval", {}).get("resolved"): resolved_new += 1
            continue

        inst_id = entry["instance_id"]
        repo = entry["repo"]
        harness = entry["harness"]
        if inst_id not in ds_map:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} — not in dataset")
            continue
        instance_row = ds_map[inst_id]
        template = ROOTFS_TEMPLATES.get(repo)
        if not template or not template.exists():
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} — no rootfs template")
            failed += 1
            continue

        ok, msg = setup_rootfs(instance_row, template)
        if not ok:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} — rootfs setup failed: {msg}")
            failed += 1
            continue

        try:
            preds = json.load(open(entry["pred_file"]))
            pred = preds[0] if isinstance(preds, list) else preds
        except Exception as e:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} — pred load failed: {e}")
            failed += 1
            continue

        patch_size = len(pred.get("model_patch", ""))
        if patch_size == 0:
            skipped += 1
            continue

        cfg = FIX3_CONFIG.get(repo, {"env_override": "", "extra_pip": "", "no_build_isolation": False})
        elapsed = time.time() - t_start
        eta = (elapsed / max(done, 1)) * (len(entries) - done - skipped) if done > 0 else 0
        print(f"  [{i+1}/{len(entries)}] {inst_id} ({harness}) patch={patch_size}B "
              f"env={cfg['env_override'] or 'testbed'} elapsed={elapsed:.0f}s eta={eta:.0f}s", flush=True)

        try:
            report, log_dir = run_reeval_one(
                instance_row, pred, template, "FIX3", timeout=args.timeout,
                env_override=cfg["env_override"], extra_pip=cfg["extra_pip"],
                no_build_isolation=cfg["no_build_isolation"],
            )
            new_eval = parse_report(report, inst_id)
            old_eval = entry["old_eval"]
            if isinstance(old_eval, str): old_eval = ast.literal_eval(old_eval)
            flipped = "FLIPPED!" if new_eval["resolved"] and not old_eval.get("resolved") else ""
            if new_eval["resolved"]:
                resolved_new += 1
                if flipped: flipped_new += 1
            result = {
                "key": key, "instance_id": inst_id, "repo": repo, "harness": harness,
                "old_eval": old_eval, "fix1_eval": entry["fix1_eval"],
                "new_eval": new_eval, "flipped": flipped, "log_dir": str(log_dir),
            }
            new_results.append(result)
            done += 1
            status = "RESOLVED" if new_eval["resolved"] else ("APPLIED" if new_eval["patch_applied"] else "NOT_APPLIED")
            print(f"    -> {status} {flipped}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            traceback.print_exc()
            failed += 1
            result = {"key": key, "instance_id": inst_id, "repo": repo, "harness": harness, "error": str(e)}
            new_results.append(result)

        all_results = list(existing.values()) + new_results
        with open(OUTPUT_JSON, "w") as f:
            json.dump(all_results, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\n=== FIX3 COMPLETE ===")
    print(f"  Done: {done}, Skipped: {skipped}, Failed: {failed}")
    print(f"  Resolved (new): {resolved_new}, Flipped: {flipped_new}")
    print(f"  Total time: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"  Results: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
