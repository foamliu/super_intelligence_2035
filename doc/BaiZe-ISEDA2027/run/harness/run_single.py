#!/usr/bin/env python3
"""Direct single-instance harness runner (replaces lost run_harness_direct.py).

Loads an SWE-bench instance from a *local JSON file* (no `datasets` network
call needed).  Runs a specified harness driver, captures the git diff as
`model_patch`, and writes a predictions.json for `r1_eval.py`.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_harness import DRIVERS, DriverResult, _run, git_patch, DUMMY_KEY  # noqa: E402


def reset_workdir(workdir: Path, base_commit: str):
    """Hard-reset the workdir to base_commit and remove untracked files."""
    _run(["git", "reset", "--hard", base_commit], workdir, timeout=120)
    _run(["git", "clean", "-fdq"], workdir, timeout=120)


def run_cline_patched(instance, workdir, timeout):
    """Run cline with --data-dir + -P openai (independent cline_harness_data)."""
    import types
    from run_harness import CLINE_BIN, UNIFIED_MODEL, ClineDriver
    driver = ClineDriver()
    data_dir = "/nas_train/app.e0031982/harness_work/cline_harness_data"
    def run_patched(self, instance, workdir, timeout=3600):
        cmd = [CLINE_BIN, "-c", str(workdir), "--data-dir", data_dir,
               "-P", "openai", "-m", UNIFIED_MODEL, "-k", self.api_key,
               "--auto-approve", "true", "--json", instance["problem_statement"]]
        r = _run(cmd, workdir, timeout)
        r.harness = self.name
        r.model_patch = git_patch(workdir) if r.returncode == 0 else ""
        return r
    driver.run = types.MethodType(run_patched, driver)
    return driver.run(instance, workdir, timeout)


def main():
    ap = argparse.ArgumentParser(
        description="Run a single harness on a single SWE-bench instance")
    ap.add_argument("--harness", required=True,
                    choices=list(DRIVERS.keys()) + ["cline-patched"])
    ap.add_argument("--instance-json", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--base-commit", default="")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--out-patch", default=None)
    ap.add_argument("--out-predictions", default=None)
    ap.add_argument("--model-name", default=None)
    args = ap.parse_args()

    inst = json.loads(Path(args.instance_json).read_text())
    print(f"[run_single] instance_id={inst['instance_id']}")
    print(f"[run_single] base_commit={inst.get('base_commit', 'N/A')}")
    print(f"[run_single] ps_len={len(inst.get('problem_statement', ''))}")

    workdir = Path(args.workdir)
    base_commit = args.base_commit or inst.get("base_commit", "")

    if base_commit:
        print(f"[run_single] git reset --hard {base_commit}")
        reset_workdir(workdir, base_commit)

    harness_name = args.harness
    if harness_name == "cline-patched":
        print(f"[run_single] running cline (patched) ...")
        res = run_cline_patched(inst, workdir, args.timeout)
    else:
        driver = DRIVERS[harness_name]
        if not driver.available():
            print(f"[run_single] ERROR: {harness_name} not available", file=sys.stderr)
            return 2
        print(f"[run_single] running {harness_name} ...")
        res = driver.run(inst, workdir, timeout=args.timeout)

    print(f"== harness={res.harness} rc={res.returncode} "
          f"timed_out={res.timed_out} wall={res.wall_s:.1f}s ==")
    if res.stderr:
        print(f"[stderr tail] ...{res.stderr[-400:]}")

    patch = res.model_patch
    print(f"[run_single] model_patch: {len(patch)} bytes")

    if args.out_patch:
        Path(args.out_patch).write_text(patch)
        print(f"[run_single] wrote patch -> {args.out_patch}")

    if args.out_predictions:
        model_name = args.model_name or f"{res.harness}-deepseek-v4-flash"
        pred = {"instance_id": inst["instance_id"],
                "model_name_or_path": model_name, "model_patch": patch}
        Path(args.out_predictions).write_text(json.dumps([pred], indent=2))
        print(f"[run_single] wrote predictions -> {args.out_predictions}")

    if base_commit:
        print(f"[run_single] cleanup: git reset --hard {base_commit}")
        reset_workdir(workdir, base_commit)

    return 0 if res.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
