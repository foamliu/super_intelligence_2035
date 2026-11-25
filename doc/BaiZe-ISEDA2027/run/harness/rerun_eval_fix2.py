#!/usr/bin/env python3
"""Re-evaluate the 97 fix1 STILL_NOT_APPLIED entries with per-repo env fixes (fix2).

Fixes applied (P1-1b, 2026-10-13):
  1. matplotlib (30 entries): use testbed_py39 conda env (Python 3.9.20) instead
     of testbed (Python 3.8.20). matplotlib 3.8+ requires Python 3.9.
  2. scikit-learn (21 entries): use testbed_py38 conda env (Python 3.8.20) instead
     of testbed (Python 3.6.13). sklearn needs Python 3.8+ for importlib.resources.
  3. pallets/flask (14 entries): install werkzeug<2.3 in testbed env.
  4. pytest-dev/pytest (15 entries): downgrade setuptools to <70 in testbed env.
  5. sphinx-doc/sphinx (8 entries): included for re-eval.
  6. other (11 entries): included for re-eval with env fixes applied.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, traceback
from pathlib import Path
from collections import Counter

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

HARNESS_WORK = Path("/nas_train/app.e0031982/harness_work")
ROOTFS_DIR = HARNESS_WORK / "rootfs"
LOGS_EVAL = HARNESS_WORK / "logs_eval_fix2"
FIX1_JSON = HERE / "kimi_pilot_results.fix1.json"
RESULTS_JSON = HERE / "kimi_pilot_results.json"
OUTPUT_JSON = HERE / "kimi_pilot_results.fix2.json"
PROXY = "http://172.19.92.25:13128"

ROOTFS_TEMPLATES = {
    "django/django": ROOTFS_DIR / "django__django-10914",
    "sympy/sympy": ROOTFS_DIR / "sympy__sympy-11400",
    "matplotlib/matplotlib": ROOTFS_DIR / "matplotlib__matplotlib-18869",
    "scikit-learn/scikit-learn": ROOTFS_DIR / "scikit-learn__scikit-learn-10297",
    "pytest-dev/pytest": ROOTFS_DIR / "pytest-dev__pytest-11143",
    "sphinx-doc/sphinx": ROOTFS_DIR / "sphinx-doc__sphinx-10325",
    "astropy/astropy": ROOTFS_DIR / "astropy__astropy-12907",
    "psf/requests": ROOTFS_DIR / "psf__requests-1963",
    "pylint-dev/pylint": ROOTFS_DIR / "pylint-dev__pylint-5859",
    "pydata/xarray": ROOTFS_DIR / "pydata__xarray-3364",
    "mwaskom/seaborn": ROOTFS_DIR / "mwaskom__seaborn-2848",
    "pallets/flask": ROOTFS_DIR / "pallets__flask-4045",
}

# fix2 per-repo configuration
FIX2_CONFIG = {
    "matplotlib/matplotlib":     {"env_override": "testbed_py39", "extra_pip": "", "no_build_isolation": False},
    "scikit-learn/scikit-learn": {"env_override": "testbed_py38", "extra_pip": "", "no_build_isolation": False},
    "pallets/flask":             {"env_override": "", "extra_pip": "'werkzeug<2.3'", "no_build_isolation": False},
    "pytest-dev/pytest":         {"env_override": "", "extra_pip": "'setuptools<70'", "no_build_isolation": False},
    "sphinx-doc/sphinx":         {"env_override": "", "extra_pip": "", "no_build_isolation": False},
}

TARGET_REPOS = set(FIX2_CONFIG.keys())
TIMEOUT_EVAL = 1200


def run_cmd(cmd, cwd=None, timeout=300):
    """Run a command with proxy env vars."""
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
    """Git fetch with retry."""
    for attempt in range(1, max_retries + 1):
        for lock in Path(workdir / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        out, rc = run_cmd(["git", "fetch", "--depth=1", "origin", base_commit],
                         cwd=workdir, timeout=timeout)
        if rc == 0:
            return True, out
        if attempt < max_retries:
            print(f"    [FETCH RETRY {attempt}/{max_retries}] waiting 10s...")
            time.sleep(10)
    return False, out


def setup_rootfs(instance, rootfs_path):
    """Ensure the base_commit is available in the rootfs testbed git repo."""
    repo = instance["repo"]
    template = ROOTFS_TEMPLATES.get(repo)
    if not template or not Path(template).exists():
        return False, f"no rootfs template for {repo}"
    testbed = template / "testbed"
    if not testbed.exists():
        return False, f"template testbed missing: {testbed}"
    base_commit = instance["base_commit"]
    out, rc = run_cmd(["git", "cat-file", "-t", base_commit], cwd=testbed, timeout=10)
    if rc != 0 or "commit" not in out:
        import glob
        for tmp in glob.glob(str(testbed / ".git" / "objects" / "pack" / "tmp_*")):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        for lock in (testbed / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        ok, out = git_fetch_retry(testbed, base_commit, max_retries=3, timeout=300)
        if not ok:
            return False, f"base_commit fetch failed: {out[:200]}"
    return True, f"using template {template.name}"


def find_fix2_entries(fix1_results, orig_results, target_repos=None):
    """Find not-applied entries from fix1 that have non-empty patches."""
    orig_map = {}
    for x in orig_results:
        key = f"{x.get('harness','')}|{x.get('instance_id','')}"
        orig_map[key] = x

    entries = []
    for r in fix1_results:
        if "error" in r:
            continue
        ne = r.get("new_eval", {})
        if ne.get("patch_applied") or ne.get("resolved"):
            continue
        repo = r.get("repo", "")
        if target_repos and repo not in target_repos:
            continue
        key = r.get("key", "")
        inst_id = r.get("instance_id", "")
        harness = r.get("harness", "")
        orig = orig_map.get(key, {})
        hr = orig.get("harness_result", {})
        pred_file = hr.get("predictions_file", "")
        if not pred_file or not os.path.exists(pred_file):
            continue
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
        except Exception:
            pass
    return entries


def parse_report(report, instance_id):
    """Extract eval metrics from the report dict."""
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
    """Run a single re-eval instance with fix2 env overrides."""
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
    ap = argparse.ArgumentParser(description="Re-eval after fix2 env fixes")
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

    print("[2/4] Finding fix2 re-evaluable entries (from fix1 not-applied)...")
    fix1 = json.load(open(FIX1_JSON))
    orig = json.load(open(RESULTS_JSON))
    target_repos = {args.repo} if args.repo else TARGET_REPOS
    entries = find_fix2_entries(fix1, orig, target_repos)
    print(f"  Found {len(entries)} fix2 re-evaluable entries")
    for repo, cnt in Counter(e["repo"] for e in entries).most_common():
        cfg = FIX2_CONFIG.get(repo, {})
        env = cfg.get("env_override", "testbed")
        pip = cfg.get("extra_pip", "")
        print(f"    {repo}: {cnt} (env={env}" + (f", pip={pip}" if pip else "") + ")")

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
        if template and template.exists():
            print(f"  {repo}: {template.name} OK")
        else:
            print(f"  {repo}: MISSING")

    print(f"[4/4] Re-evaluating {len(entries)} entries (timeout={args.timeout}s)...")
    new_results = []
    done = 0; skipped = 0; failed = 0; resolved_new = 0; patch_improved = 0
    t_start = time.time()

    for i, entry in enumerate(entries):
        if args.limit and done + skipped >= args.limit:
            print(f"  --limit {args.limit} reached, stopping.")
            break
        key = entry["key"]
        if key in existing:
            skipped += 1
            if existing[key].get("new_eval", {}).get("resolved"):
                resolved_new += 1
            continue

        inst_id = entry["instance_id"]; repo = entry["repo"]; harness = entry["harness"]
        if inst_id not in ds_map:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} ({harness}) - not in dataset")
            continue
        instance_row = ds_map[inst_id]
        template = ROOTFS_TEMPLATES.get(repo)
        if not template:
            continue
        ok, msg = setup_rootfs(instance_row, template)
        if not ok:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} ({harness}) - rootfs setup failed: {msg}")
            failed += 1; continue

        cfg = FIX2_CONFIG.get(repo, {})
        env_override = cfg.get("env_override", "")
        extra_pip = cfg.get("extra_pip", "")
        no_build_isolation = cfg.get("no_build_isolation", False)

        try:
            preds = json.load(open(entry["pred_file"]))
            pred = preds[0] if isinstance(preds, list) and preds else preds
        except Exception as e:
            print(f"  [{i+1}/{len(entries)}] SKIP {inst_id} ({harness}) - pred load failed: {e}")
            failed += 1; continue

        patch_size = len(pred.get("model_patch", ""))
        if patch_size == 0:
            skipped += 1; continue

        elapsed = time.time() - t_start
        eta = (elapsed / max(done, 1)) * (len(entries) - done - skipped) if done > 0 else 0
        env_label = f" env={env_override}" if env_override else ""
        pip_label = f" pip+{extra_pip}" if extra_pip else ""
        print(f"  [{i+1}/{len(entries)}] {inst_id} ({harness}) patch={patch_size}B{env_label}{pip_label} "
              f"elapsed={elapsed:.0f}s eta={eta:.0f}s", flush=True)

        try:
            report, log_dir = run_reeval_one(
                instance_row, pred, template, "FIX2", timeout=args.timeout,
                env_override=env_override, extra_pip=extra_pip,
                no_build_isolation=no_build_isolation,
            )
            new_eval = parse_report(report, inst_id)
            old_eval = entry["old_eval"]; fix1_eval = entry["fix1_eval"]
            flipped = "RESOLVED->" if new_eval["resolved"] and not old_eval.get("resolved") else ""

            result = {
                "key": key, "instance_id": inst_id, "repo": repo, "harness": harness,
                "old_eval": old_eval, "fix1_eval": fix1_eval, "new_eval": new_eval,
                "flipped": flipped, "log_dir": str(log_dir),
                "fix2_config": {"env_override": env_override, "extra_pip": extra_pip},
            }
            new_results.append(result); done += 1
            if new_eval["resolved"] and not old_eval.get("resolved"):
                resolved_new += 1
                print(f"    FLIPPED: {inst_id} ({harness}) -> RESOLVED!")
            elif new_eval["patch_applied"] and not fix1_eval.get("patch_applied"):
                patch_improved += 1
                print(f"    IMPROVED: patch now applied (f2p={new_eval['f2p_pass']}/{new_eval['f2p_total']})")
            else:
                print(f"    -> resolved={new_eval['resolved']} patch_applied={new_eval['patch_applied']} "
                      f"f2p={new_eval['f2p_pass']}/{new_eval['f2p_total']}")
        except Exception as e:
            failed += 1; print(f"    ERROR: {e}"); traceback.print_exc()
            new_results.append({"key": key, "instance_id": inst_id, "repo": repo,
                                "harness": harness, "error": str(e)})

        all_results = list(existing.values()) + new_results
        with open(OUTPUT_JSON, "w") as f:
            json.dump(all_results, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"fix2 Re-eval complete: {done} done, {skipped} skipped, {failed} failed, "
          f"{resolved_new} newly resolved")
    print(f"Patch improved (fix1 not-applied -> fix2 applied): {patch_improved}")
    print(f"Elapsed: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"Results saved to: {OUTPUT_JSON}")

    print(f"\nPer-repo summary (newly resolved / total re-evaluated):")
    repo_stats = Counter()
    for r in new_results:
        if "new_eval" in r:
            repo_stats[r["repo"]] += 1
            if r["new_eval"].get("resolved"):
                repo_stats[r["repo"] + "_resolved"] += 1
            if r["new_eval"].get("patch_applied"):
                repo_stats[r["repo"] + "_applied"] += 1
    for repo in sorted(target_repos):
        total = repo_stats.get(repo, 0)
        res = repo_stats.get(repo + "_resolved", 0)
        appl = repo_stats.get(repo + "_applied", 0)
        print(f"  {repo}: {res}/{total} resolved, {appl}/{total} patch-applied")


if __name__ == "__main__":
    main()
