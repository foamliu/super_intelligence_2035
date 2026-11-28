#!/usr/bin/env python3
"""Direct single-instance harness runner (replaces lost run_harness_direct.py).

Loads an SWE-bench instance from a *local JSON file* (no `datasets` network
call needed).  Runs a specified harness driver, captures the git diff as
`model_patch`, and writes a predictions.json for `r1_eval.py`.
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_harness import DRIVERS, DriverResult, _run, git_patch, DUMMY_KEY  # noqa: E402

# Token usage sidecar path (must match gw_proxy.py / gw_proxy_dsh.py)
USAGE_LOG = os.environ.get("GW_USAGE_LOG", "/tmp/gw_proxy_usage.jsonl")


def _aggregate_usage(t_start: float, t_end: float) -> dict | None:
    """Read the proxy usage sidecar JSONL and sum tokens for [t_start, t_end].

    Returns {"input_tokens": N, "output_tokens": M, "total_tokens": N+M,
             "n_api_calls": K} or None if no data.
    """
    if not os.path.exists(USAGE_LOG):
        return None
    prompt_total = 0
    completion_total = 0
    n_calls = 0
    try:
        with open(USAGE_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                ts = rec.get("ts_epoch", 0)
                if t_start <= ts <= t_end:
                    prompt_total += rec.get("prompt_tokens", 0)
                    completion_total += rec.get("completion_tokens", 0)
                    n_calls += 1
    except Exception:
        return None
    if n_calls == 0:
        return None
    return {
        "input_tokens": prompt_total,
        "output_tokens": completion_total,
        "total_tokens": prompt_total + completion_total,
        "n_api_calls": n_calls,
    }


def reset_workdir(workdir: Path, base_commit: str):
    """Hard-reset the workdir to base_commit and remove untracked files."""
    _run(["git", "reset", "--hard", base_commit], workdir, timeout=120)
    _run(["git", "clean", "-fdq"], workdir, timeout=120)


_SHARED_CLINE_DATA = "/nas_train/app.e0031982/harness_work/cline_harness_data"


def _seed_cline_data_dir(data_dir: str):
    """Seed a fresh per-instance cline --data-dir from the shared (proven) dir.

    A brand-new data-dir lacks globalState.json/settings, so cline falls back to
    platform.openai.com and fails on the dummy key (empty patch).  Copy the routing
    config so isolated per-instance dirs behave identically to the historic shared
    dir.  (2026-11-24, parallel-predict fix.)
    """
    if data_dir == _SHARED_CLINE_DATA or (Path(data_dir) / "globalState.json").exists():
        return
    src = Path(_SHARED_CLINE_DATA)
    dst = Path(data_dir)
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("globalState.json", "secrets.json"):
        if (src / name).exists():
            shutil.copy2(src / name, dst / name)
    if (src / "settings").exists() and not (dst / "settings").exists():
        shutil.copytree(src / "settings", dst / "settings")


def run_cline_patched(instance, workdir, timeout):
    """Run cline with --data-dir + -P openai (independent cline_harness_data).

    Fix #1 (2026-11-04 per trace analysis): use the original TypeScript cline
    binary (.bun/bin/cline) instead of the compiled cline-checkpoint-off ELF
    binary (.local/bin/cline).  The compiled binary has a bug where it silently
    exits (rc=0, ~2s, 0 bytes stdout) on certain prompts — root cause of 36/500
    silent-exit failures.  Also explicitly route through gw_proxy (127.0.0.1:9090).
    """
    import types
    from run_harness import CLINE_BIN, UNIFIED_MODEL, ClineDriver
    driver = ClineDriver()
    # 2026-11-24: per-instance data-dir (env CLINE_DATA_DIR) so parallel predict
    # workers don't collide on a single cline --data-dir.  Serial flow keeps the
    # historic shared dir.
    data_dir = os.environ.get(
        "CLINE_DATA_DIR", "/nas_train/app.e0031982/harness_work/cline_harness_data")
    _seed_cline_data_dir(data_dir)
    def run_patched(self, instance, workdir, timeout=3600):
        cmd = [CLINE_BIN, "-c", str(workdir), "--data-dir", data_dir,
               "-P", "openai", "-m", UNIFIED_MODEL, "-k", DUMMY_KEY,
               "--auto-approve", "true",
               "--compaction", "basic",
               "--thinking", "low",
               "--json", instance["problem_statement"]]
        r = _run(cmd, workdir, timeout, env={
            "OPENAI_API_KEY": DUMMY_KEY,
            "OPENAI_BASE_URL": f"http://127.0.0.1:{os.environ.get('GW_PROXY_PORT', '9090')}/v1",
        })
        r.harness = self.name
        r.model_patch = git_patch(workdir)  # R1744 fix: always extract patch; rc!=0 may still have real edits
        return r
    driver.run = types.MethodType(run_patched, driver)
    return driver.run(instance, workdir, timeout)


def run_zhulong(instance, workdir, timeout):
    """Zhulong CLI (Cline fork, no policy) runner.
    完全复用cline参数配置，仅替换启动命令路径。
    """
    import types
    from run_harness import UNIFIED_MODEL, ClineDriver
    driver = ClineDriver()
    # 共用cline的数据目录，配置已适配doubao-pro网关
    data_dir = os.environ.get(
        "CLINE_DATA_DIR", "/nas_train/app.e0031982/harness_work/cline_harness_data")
    _seed_cline_data_dir(data_dir)
    _bun = shutil.which("bun") or os.path.expanduser("~/.bun/bin/bun")
    ZHULONG_BIN = [_bun, "run", "/nas_train/app.e0031982/harness/eda_platform/apps/cli/src/index.ts"]
    def run_zhulong_impl(self, instance, workdir, timeout=3600):
        cmd = ZHULONG_BIN + ["-c", str(workdir), "--data-dir", data_dir,
               "-P", "openai-compatible", "-m", UNIFIED_MODEL, "-k", DUMMY_KEY,
               "--auto-approve", "true",
               "--compaction", "basic",
               "--thinking", "none",
               "--json", instance["problem_statement"]]
        r = _run(cmd, workdir, timeout, env={
            "OPENAI_API_KEY": DUMMY_KEY,
            "OPENAI_BASE_URL": f"http://127.0.0.1:{os.environ.get('GW_PROXY_PORT', '9090')}/v1",
        })
        r.harness = "zhulong"
        r.model_patch = git_patch(workdir)
        return r
    driver.run = types.MethodType(run_zhulong_impl, driver)
    return driver.run(instance, workdir, timeout)


def main():
    ap = argparse.ArgumentParser(
        description="Run a single harness on a single SWE-bench instance")
    ap.add_argument("--harness", required=True,
                    choices=list(DRIVERS.keys()) + ["cline-patched", "zhulong"])
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
    t_start = time.time()
    if harness_name == "cline-patched":
        print(f"[run_single] running cline (patched) ...")
        res = run_cline_patched(inst, workdir, args.timeout)
    elif harness_name == "zhulong":
        print(f"[run_single] running zhulong (no policy) ...")
        res = run_zhulong(inst, workdir, args.timeout)
    else:
        driver = DRIVERS[harness_name]
        if not driver.available():
            print(f"[run_single] ERROR: {harness_name} not available", file=sys.stderr)
            return 2
        print(f"[run_single] running {harness_name} ...")
        res = driver.run(inst, workdir, timeout=args.timeout)
    t_end = time.time()

    usage = _aggregate_usage(t_start, t_end)
    if usage:
        print(f"[run_single] usage: input={usage['input_tokens']} "
              f"output={usage['output_tokens']} "
              f"total={usage['total_tokens']} "
              f"api_calls={usage['n_api_calls']}")

    print(f"== harness={res.harness} rc={res.returncode} "
          f"timed_out={res.timed_out} wall={res.wall_s:.1f}s ==")
    # Fix #2 (2026-11-04 per trace analysis): print stdout tail so that cline's
    # --json error output (API errors, startup crashes) is visible to predict_one's
    # blocked/forbidden detection.  Previously only stderr was printed, so cline's
    # stdout (where --json errors go) was silently swallowed.
    if res.stdout:
        print(f"[stdout tail] ...{res.stdout[-400:]}")
    if res.stderr:
        print(f"[stderr tail] ...{res.stderr[-400:]}")

    patch = res.model_patch
    print(f"[run_single] model_patch: {len(patch)} bytes")

    if args.out_patch:
        Path(args.out_patch).write_text(patch)
        print(f"[run_single] wrote patch -> {args.out_patch}")

    if args.out_predictions:
        model_name = args.model_name or f"{res.harness}-{os.environ.get('HARNESS_MODEL', 'kimi-k2.6-cloud')}"
        pred = {"instance_id": inst["instance_id"],
                "model_name_or_path": model_name, "model_patch": patch}
        if usage:
            pred["usage"] = usage
        Path(args.out_predictions).write_text(json.dumps([pred], indent=2))
        print(f"[run_single] wrote predictions -> {args.out_predictions}")

    if base_commit:
        print(f"[run_single] cleanup: git reset --hard {base_commit}")
        reset_workdir(workdir, base_commit)

    # R1744 fix: always return 0 — patch is extracted regardless of harness rc;
    # the official SWE-bench eval will judge the patch honestly.  A non-zero
    # harness rc (API error, timeout) should not prevent the prediction from
    # being saved and evaluated.
    return 0


if __name__ == "__main__":
    sys.exit(main())
