#!/usr/bin/env python3
"""Batch pilot runner — expand SWE-bench-Lite evaluation to 20-30 instances.

For each instance:
  1. Create a workdir (git clone repo @ base_commit) — needs GitHub.
  2. Create/reuse a rootfs (conda env + repo at base_commit) — needs PyPI.
  3. Run 4 harnesses (cline-patched, codex, opencode, claude-code).
  4. Evaluate each with r1_eval.py (unshare sandbox).
  5. Save results incrementally (per harness, per instance).

Usage:
  python3 run_pilot_batch.py --instances django__django-10924 django__django-11001
  python3 run_pilot_batch.py --all-prepared          # run all in instances/
  python3 run_pilot_batch.py --setup-only django__django-10924  # just workdir+rootfs

Honesty: blocked when GitHub/PyPI unreachable. Reports blocker, skips instance.
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_WORK = Path("/nas_train/app.e0031982/harness_work")
INSTANCES_DIR = HARNESS_WORK / "instances"
WORKDIRS = HARNESS_WORK / "workdirs"
ROOTFS_DIR = HARNESS_WORK / "rootfs"
LOGS_EVAL = HARNESS_WORK / "logs_eval"

ROOTFS_TEMPLATES = {
    "django/django": {"3.0": ROOTFS_DIR / "django__django-10914"},
    "sympy/sympy": {"1.1": ROOTFS_DIR / "sympy__sympy-11400"},
}
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code"]
TIMEOUT_RUN = 1800
TIMEOUT_EVAL = 1800


def run(cmd, cwd=None, timeout=300, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, env=e)
        return (p.stdout + p.stderr).decode(errors="replace"), p.returncode
    except subprocess.TimeoutExpired as ex:
        out = ((ex.stdout or b"") + (ex.stderr or b"")).decode(errors="replace")
        return out + "\n[TIMEOUT]", -1


def git_clone_or_fetch(repo, base_commit, workdir):
    workdir = Path(workdir)
    if workdir.exists() and (workdir / ".git").exists():
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=workdir, timeout=120)
        if rc != 0:
            out2, rc2 = run(["git", "fetch", "--unshallow"], cwd=workdir, timeout=300)
            if rc2 != 0:
                return False, f"git fetch failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "existing workdir updated"
    else:
        workdir.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://github.com/{repo}"
        out, rc = run(["git", "clone", "--no-checkout", url, str(workdir)], timeout=300)
        if rc != 0:
            return False, f"git clone failed: {out[:200]}"
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=workdir, timeout=120)
        if rc != 0:
            return False, f"git fetch base_commit failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "cloned fresh"


def setup_rootfs(instance, rootfs_path):
    rootfs_path = Path(rootfs_path)
    if rootfs_path.exists() and (rootfs_path / "testbed").exists():
        return True, "rootfs already exists"
    repo = instance["repo"]
    version = instance.get("version", "")
    template = ROOTFS_TEMPLATES.get(repo, {}).get(version)
    if not template or not Path(template).exists():
        return False, f"no rootfs template for {repo} v{version}"
    print(f"  [rootfs] copying template {template.name} -> {rootfs_path.name} ...")
    out, rc = run(["cp", "-a", str(template), str(rootfs_path)], timeout=600)
    if rc != 0:
        return False, f"cp -a failed: {out[:200]}"
    testbed = rootfs_path / "testbed"
    base_commit = instance["base_commit"]
    out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=testbed, timeout=120)
    if rc != 0:
        out2, rc2 = run(["git", "fetch", "--unshallow"], cwd=testbed, timeout=300)
        if rc2 != 0:
            return False, f"rootfs git fetch failed: {out[:200]}"
    out, rc = run(["git", "checkout", base_commit], cwd=testbed, timeout=60)
    if rc != 0:
        return False, f"rootfs git checkout failed: {out[:200]}"
    out, rc = run(["pip", "install", "-e", ".", "--no-deps", "-q"], cwd=testbed, timeout=300)
    return True, f"rootfs created from template, pip install rc={rc}"


def run_harness(harness, instance_json, workdir, predictions_out):
    cmd = [sys.executable, str(HERE / "run_single.py"),
           "--harness", harness, "--instance-json", str(instance_json),
           "--workdir", str(workdir), "--timeout", str(TIMEOUT_RUN),
           "--out-predictions", str(predictions_out)]
    t0 = time.time()
    out, rc = run(cmd, timeout=TIMEOUT_RUN + 120)
    wall = time.time() - t0
    return rc == 0, {"harness": harness, "returncode": rc, "wall_s": round(wall, 1),
                     "predictions_file": str(predictions_out), "stdout_tail": out[-500:]}


def eval_instance(instance_id, predictions_file, rootfs_path, run_id):
    cmd = [sys.executable, str(HERE / "r1_eval.py"),
           "--instance", instance_id, "--predictions", str(predictions_file),
           "--rootfs", str(rootfs_path), "--run-id", run_id,
           "--log-dir", str(LOGS_EVAL), "--sandbox", "unshare", "--timeout", str(TIMEOUT_EVAL)]
    out, rc = run(cmd, timeout=TIMEOUT_EVAL + 120)
    (LOGS_EVAL / f"eval_{run_id}.log").write_text(out)
    result = {"eval_rc": rc}
    report_dir = LOGS_EVAL / run_id
    report_jsons = list(report_dir.rglob("report.json"))
    if report_jsons:
        try:
            report = json.loads(report_jsons[0].read_text())
            result.update(resolved=report.get("resolved", False),
                          f2p=report.get("fail_to_pass", {}),
                          p2p=report.get("pass_to_pass", {}))
        except Exception as e:
            result["report_error"] = str(e)
    return rc == 0, result


def process_instance(instance_id, do_setup=True, do_run=True, do_eval=True):
    inst_json = INSTANCES_DIR / f"{instance_id}.json"
    if not inst_json.exists():
        return {"instance_id": instance_id, "error": "instance JSON not found"}
    instance = json.loads(inst_json.read_text())
    results = {"instance_id": instance_id, "repo": instance["repo"], "version": instance.get("version", "")}
    workdir = WORKDIRS / instance_id
    if do_setup:
        print(f"\n{'='*60}\n[SETUP] {instance_id}")
        ok, msg = git_clone_or_fetch(instance["repo"], instance["base_commit"], workdir)
        results["workdir_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = msg
            return results
        rootfs_path = ROOTFS_DIR / instance_id
        ok, msg = setup_rootfs(instance, rootfs_path)
        results["rootfs_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = f"rootfs: {msg}"
            return results
    if do_run:
        harness_results = {}
        for harness in HARNESSES:
            print(f"\n[RUN] {harness} on {instance_id} ...")
            pred_file = WORKDIRS / f"predictions_{harness.replace('-', '_')}_{instance_id}.json"
            ok, hres = run_harness(harness, inst_json, workdir, pred_file)
            if do_eval and ok:
                run_id = f"R1_PILOT_{harness.replace('-', '_').upper()}_{instance_id.replace('-', '_')}"
                eok, eres = eval_instance(instance_id, pred_file, ROOTFS_DIR / instance_id, run_id)
                hres["eval"] = eres
            harness_results[harness] = hres
        results["harnesses"] = harness_results
    return results


def main():
    ap = argparse.ArgumentParser(description="Batch pilot runner for SWE-bench Lite")
    ap.add_argument("--instances", nargs="+")
    ap.add_argument("--all-prepared", action="store_true")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--run-only", action="store_true")
    ap.add_argument("--out-summary", default=None)
    args = ap.parse_args()
    if args.all_prepared:
        instance_ids = [f.stem for f in sorted(INSTANCES_DIR.glob("*.json"))]
    elif args.instances:
        instance_ids = args.instances
    else:
        ap.error("Must specify --instances or --all-prepared")
    do_setup = not args.run_only
    do_run = not args.setup_only
    do_eval = not args.setup_only
    print(f"Pilot batch: {len(instance_ids)} instances, setup={do_setup}, run={do_run}")
    all_results = []
    for iid in instance_ids:
        res = process_instance(iid, do_setup, do_run, do_eval)
        all_results.append(res)
        summary_path = Path(args.out_summary or HARNESS_WORK / "pilot_results.json")
        summary_path.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\n{'='*80}\nPILOT SUMMARY\n{'='*80}")
    for res in all_results:
        iid = res["instance_id"]
        if "blocked" in res:
            print(f"  {iid}: BLOCKED - {res['blocked'][:60]}")
            continue
        for h, hres in res.get("harnesses", {}).items():
            resolved = hres.get("eval", {}).get("resolved", "N/A")
            print(f"  {iid} | {h} | resolved={resolved} | wall={hres.get('wall_s', '?')}s")
    return 0

if __name__ == "__main__":
    sys.exit(main())
