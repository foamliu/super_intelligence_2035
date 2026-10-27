#!/usr/bin/env python3
"""SWE-bench Verified 20-instance pilot orchestrator (R528, 2026-10-27).

Operator directive (2026-10-27 08:3x): "SWE-bench Verified 20条试点启动".
Per R518 readiness report plan: smoke 1 (cline+hermes) -> 20 each -> report.

Two phases, both reusing PROVEN infrastructure:
  * PREDICT: reuse harness/run_single.py (the SWE-bench Lite 7x300 prediction
    driver, 2100 runs proven).  Each instance: git clone repo@base_commit into a
    workdir -> run harness CLI agent with problem_statement -> capture git diff
    as model_patch -> write a per-instance predictions JSON.
  * EVAL: reuse the official swebench v5.0.2 docker harness
    (swebench.harness.run_evaluation) on the pre-pulled sweb.eval images
    (500/500, via `sg docker`).  The Verified HF dataset lacks the
    image/eval_script/log_parser/eval_type fields that make_test_spec needs, so
    we feed an ENRICHED local JSON (Verified curated F2P/P2P/test_patch + full
    SWE-bench infra fields) as --dataset_name.

Unified caliber (task §1.2): same instance set / same model (kimi-k2.6-cloud
via gw_proxy 9090 for hermes, cline secrets.json for cline) / same timeout
1800s / same eval script (official docker harness) / same 20 instances.

Report: three columns resolved / failed / infra-or-quota + conclusion, for ops
scale-up decision.  STRICTLY stop at 20 (do NOT run full 500).
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
RUN_SINGLE = HARNESS_DIR / "run_single.py"
ENRICHED = HERE / "enriched_20.json"
IDS_FILE = HERE / "verified_20_ids.txt"
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
WORKDIRS = Path("/dev/shm/harness_verified/workdirs")
PROXY = "http://172.19.92.25:13128"
TIMEOUT_RUN = 1800
TIMEOUT_EVAL = 1800
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
HARNESS_CHOICES = ["cline-patched", "hermes"]


def log(msg: str):
    print(f"[verified-pilot {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_ids(smoke: bool, max_n: int | None) -> list[str]:
    ids = IDS_FILE.read_text().split()
    if smoke:
        return ids[:1]
    if max_n:
        ids = ids[:max_n]
    return ids


def load_instances() -> dict[str, dict]:
    rows = json.loads(ENRICHED.read_text())
    return {r["instance_id"]: r for r in rows}


def run(cmd, cwd=None, timeout=300, with_proxy=True):
    """Run a subprocess.

    with_proxy=True  -> ensure external proxy set (git fetch to github etc.).
    with_proxy=False -> ACTIVELY strip all proxy env. Harness agent CLIs
      (cline/hermes) talk to the LOCAL gateway (127.0.0.1:9092 / :9090).
      cline's bun ai-sdk HTTP client ignores no_proxy for HTTP and would
      tunnel the localhost request through the external Squid proxy ->
      ERR_ACCESS_DENIED (R529, 2026-10-27). Mirrors run_serial_kimi
      skip_proxy=True (codex Rust client, same class of bug, 2026-10-14).
    NOTE: the old impl only *added* proxy when True and did nothing when False,
      so a parent shell that exported http_proxy (for git) leaked into the
      agent subprocess and broke cline. Now False actively removes it.
    """
    e = os.environ.copy()
    if with_proxy:
        e.setdefault("https_proxy", PROXY)
        e.setdefault("http_proxy", PROXY)
        e.setdefault("no_proxy", "127.0.0.1,localhost")
    else:
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                  "all_proxy", "ALL_PROXY"):
            e.pop(k, None)
        e["no_proxy"] = "*"
        e["NO_PROXY"] = "*"
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       timeout=timeout, env=e)
    return p.stdout, p.stderr, p.returncode


def git_clone_or_fetch(repo: str, base_commit: str, workdir: Path) -> tuple[bool, str]:
    url = f"https://github.com/{repo}.git"
    if (workdir / ".git").exists():
        run(["git", "fetch", "--all", "--tags"], workdir, timeout=600)
        out2, _, rc2 = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
        return rc2 == 0, "existing workdir updated"
    workdir.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], workdir, timeout=30, with_proxy=False)
    run(["git", "remote", "add", "origin", url], workdir, timeout=30, with_proxy=False)
    _, _, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], workdir, timeout=600)
    if rc != 0:
        run(["git", "fetch", "origin"], workdir, timeout=900)
    _, _, rc = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
    return rc == 0, f"init+fetch (checkout rc={rc})"


def predict_one(harness: str, inst: dict, workdir: Path) -> dict:
    iid = inst["instance_id"]
    bc = inst["base_commit"]
    ok, msg = git_clone_or_fetch(inst["repo"], bc, workdir)
    if not ok:
        return {"instance_id": iid, "harness": harness, "blocked": msg,
                "classification": "blocked", "model_patch_len": 0}
    inst_json = HERE / "instances" / f"{iid}.json"
    pred_out = PRED_DIR / f"{harness}__{iid}.json"
    cmd = [sys.executable, str(RUN_SINGLE), "--harness", harness,
           "--instance-json", str(inst_json), "--workdir", str(workdir),
           "--base-commit", bc, "--timeout", str(TIMEOUT_RUN),
           "--out-predictions", str(pred_out),
           "--model-name", f"{harness}-kimi-k2.6-cloud"]
    t0 = time.time()
    out, err, rc = run(cmd, workdir, timeout=TIMEOUT_RUN + 120, with_proxy=False)
    wall = time.time() - t0
    patch_len = 0
    if pred_out.exists():
        try:
            preds = json.loads(pred_out.read_text())
            if preds:
                patch_len = len(preds[0].get("model_patch", ""))
        except Exception:
            pass
    blocked = ("quota" in out.lower() or "429" in out or "forbidden" in out.lower())
    return {"instance_id": iid, "harness": harness, "returncode": rc,
            "wall_s": round(wall, 1), "model_patch_len": patch_len,
            "quota_blocked": blocked, "stdout_tail": out[-400:],
            "predictions_file": str(pred_out)}


def merge_predictions(harness: str, ids: list[str]) -> Path:
    merged = PRED_DIR / f"predictions_{harness}.json"
    all_preds = []
    for iid in ids:
        f = PRED_DIR / f"{harness}__{iid}.json"
        if f.exists() and f.stat().st_size > 30:
            try:
                preds = json.loads(f.read_text())
                preds = [p for p in preds if p.get("model_patch", "").strip()]
                all_preds.extend(preds)
            except Exception:
                pass
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)}/{len(ids)} predictions -> {merged}")
    return merged


def phase_predict(harness: str, smoke: bool, max_n: int | None) -> list[dict]:
    ids = load_ids(smoke, max_n)
    insts = load_instances()
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for iid in ids:
        inst = insts[iid]
        workdir = WORKDIRS / harness / inst["repo"].replace("/", "_")
        log(f"PREDICT {harness} on {iid} (workdir={workdir})")
        r = predict_one(harness, inst, workdir)
        cls = ("no-patch" if r["model_patch_len"] == 0
               else "quota-blocked" if r.get("quota_blocked")
               else "patch-produced")
        r["classification"] = cls
        log(f"  -> {cls} (patch={r['model_patch_len']}B wall={r.get('wall_s')}s)")
        results.append(r)
    (REPORT_DIR / f"predict_{harness}.json").write_text(json.dumps(results, indent=2))
    merge_predictions(harness, ids)
    return results


# --- EVAL --------------------------------------------------------------------
def phase_eval(harness: str, smoke: bool, max_n: int | None) -> dict:
    ids = load_ids(smoke, max_n)
    merged = PRED_DIR / f"predictions_{harness}.json"
    if not merged.exists():
        log(f"no merged predictions for {harness}; run predict first")
        return {"error": "no predictions"}
    preds = json.loads(merged.read_text())
    pred_ids = [p["instance_id"] for p in preds if p.get("model_patch", "").strip()]
    eval_ids = [i for i in ids if i in pred_ids]
    if not eval_ids:
        log(f"no patches to eval for {harness} (all 0-length?)")
        return {"error": "no patches", "eval_ids": []}
    run_id = f"verified_pilot_{harness}" + ("_smoke" if smoke else "")
    cmd = (f"PYTHONPATH=/tmp/swebench_repo python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers 4 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {harness} on {len(eval_ids)} instances (run_id={run_id})")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    logf = LOG_DIR / f"eval_{run_id}.log"
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    return parse_eval(run_id, eval_ids, harness)


def parse_eval(run_id: str, eval_ids: list[str], harness: str) -> dict:
    model = f"{harness}-kimi-k2.6-cloud"
    summary = {"harness": harness, "run_id": run_id, "n": len(eval_ids),
               "resolved": [], "failed": [], "infra_or_quota": []}
    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            summary["infra_or_quota"].append(iid)
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
    (REPORT_DIR / f"eval_{harness}.json").write_text(json.dumps(summary, indent=2))
    log(f"  resolved={len(summary['resolved'])} failed={len(summary['failed'])} "
        f"infra_or_quota={len(summary['infra_or_quota'])}")
    return summary


# --- REPORT ------------------------------------------------------------------
def phase_report(harness: str) -> str:
    pj = REPORT_DIR / f"predict_{harness}.json"
    ej = REPORT_DIR / f"eval_{harness}.json"
    pred = json.loads(pj.read_text()) if pj.exists() else []
    ev = json.loads(ej.read_text()) if ej.exists() else {}
    lines = [f"# SWE-bench Verified pilot - {harness}",
             f"predict: {len(pred)} attempted  eval: {ev.get('n', 0)} evaluated",
             f"resolved={len(ev.get('resolved', []))} "
             f"failed={len(ev.get('failed', []))} "
             f"infra_or_quota={len(ev.get('infra_or_quota', []))}"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="SWE-bench Verified 20-instance pilot")
    ap.add_argument("phase", choices=["predict", "eval", "report", "all"])
    ap.add_argument("--harness", required=True, choices=HARNESS_CHOICES)
    ap.add_argument("--smoke", action="store_true", help="single instance")
    ap.add_argument("--max", type=int, default=None, help="cap #instances")
    args = ap.parse_args()
    if args.phase == "predict":
        phase_predict(args.harness, args.smoke, args.max)
    elif args.phase == "eval":
        phase_eval(args.harness, args.smoke, args.max)
    elif args.phase == "report":
        print(phase_report(args.harness))
    elif args.phase == "all":
        phase_predict(args.harness, args.smoke, args.max)
        phase_eval(args.harness, args.smoke, args.max)
        print(phase_report(args.harness))


if __name__ == "__main__":
    main()

