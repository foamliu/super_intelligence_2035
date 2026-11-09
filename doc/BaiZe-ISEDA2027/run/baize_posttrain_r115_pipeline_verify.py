#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r115_pipeline_verify.py — Pre-launch data pipeline verification.

R115 (2026-11-09): Comprehensive end-to-end verification of the SFT + RL data
pipeline before GPU arrival. Cross-checks all config<->data references, verifies
parquet schemas against verl expectations, checks venv dependencies, and
identifies gaps that would block training launch.

Key findings from dry-run phase:
  1. RL parquet exists, 3347 rows, correct schema [PASS]
  2. SFT parquet v2 exists, 19524 rows, correct schema [PASS]
  3. SFT config references sft_blended_v1.parquet which DOES NOT EXIST [FAIL->FIXED]
  4. jsonl_to_parquet.py requires pyarrow -> only works with cu124 venv
  5. UltraData (agent+general) is megatron .bin/.idx on .29 NFS, not on .17

Usage:
  python3 baize_posttrain_r115_pipeline_verify.py
  python3 baize_posttrain_r115_pipeline_verify.py --json
  python3 baize_posttrain_r115_pipeline_verify.py --fix-config
"""
import argparse, json, os, subprocess, sys, ast, re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
VERL_VENV_PY = Path.home() / "code" / "verl_cu124_venv" / "bin" / "python"
MODEL_DIR = Path("/nas_data/app.e0031982/models/MiniCPM5-2B")
EDA_BASE = Path.home() / "code" / "eda_fastmcp"
EVAL_DS = EDA_BASE / "pyAether-eval" / "original_dataset" / "EDA-Eval-PyAether-v20260311.jsonl"
EVAL_DRV = EDA_BASE / "scripts" / "run_cline_script.sh"
EVAL_SCR = EDA_BASE / "scripts" / "run_eval.py"


def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", str(e), -1


def _human(n):
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return "%.1f%s" % (n, u)
        n /= 1024
    return "%.1fTB" % n


def check_file(label, path, required=True):
    p = Path(path)
    if p.exists():
        sz = p.stat().st_size
        return {"label": label, "path": str(p), "exists": True,
                "size_human": _human(sz), "status": "PASS" if required else "OK"}
    return {"label": label, "path": str(p), "exists": False,
            "status": "FAIL" if required else "WARN"}


def verify_parquet(path, expected_cols, label):
    result = {"label": label, "path": str(path), "expected_cols": expected_cols}
    if not path.exists():
        result["status"] = "FAIL"
        result["error"] = "File not found"
        return result
    if not VERL_VENV_PY.exists():
        result["status"] = "FAIL"
        result["error"] = "cu124 venv Python not found"
        return result
    cmd = "%s -c \"import pyarrow.parquet as pq; t=pq.read_table('%s'); print(t.num_rows, ',', t.column_names)\"" % (
        VERL_VENV_PY, path)
    out, err, rc = run_cmd(cmd, timeout=60)
    if rc != 0 or not out:
        result["status"] = "FAIL"
        result["error"] = err or "No output"
        return result
    parts = out.split(",", 1)
    try:
        rows = int(parts[0].strip())
    except (ValueError, IndexError):
        rows = -1
    cols_str = parts[1].strip() if len(parts) > 1 else ""
    try:
        cols = ast.literal_eval(cols_str)
    except (ValueError, SyntaxError):
        cols = [c.strip().strip("'\"") for c in cols_str.strip("[]").split(",")]
    result["rows"] = rows
    result["columns"] = cols
    missing = [c for c in expected_cols if c not in cols]
    if missing:
        result["status"] = "FAIL"
        result["error"] = "Missing columns: %s" % missing
    else:
        result["status"] = "PASS"
    return result


def verify_venv():
    results = []
    if not VERL_VENV_PY.exists():
        results.append({"label": "cu124 venv", "status": "FAIL",
                        "error": "Not found at %s" % VERL_VENV_PY})
        return results
    pkgs = [("pyarrow", "pyarrow.__version__"), ("verl", "'OK'"),
            ("sglang", "sglang.__version__"), ("torch", "torch.__version__"),
            ("flash_attn", "flash_attn.__version__"), ("ray", "ray.__version__")]
    for pkg, ver_expr in pkgs:
        cmd = "%s -c \"import %s; print(%s)\" 2>&1 | tail -1" % (VERL_VENV_PY, pkg, ver_expr)
        out, _, rc = run_cmd(cmd, timeout=60)
        if rc == 0 and out and "Error" not in out and "Traceback" not in out:
            results.append({"label": pkg, "status": "PASS", "version": out.strip()})
        else:
            results.append({"label": pkg, "status": "FAIL", "error": out[:80]})
    cmd = "%s -c \"import torch; print(torch.cuda.is_available())\" 2>&1 | tail -1" % VERL_VENV_PY
    out, _, rc = run_cmd(cmd, timeout=60)
    cuda_ok = rc == 0 and out.strip() == "True"
    results.append({"label": "torch.cuda", "status": "PASS" if cuda_ok else "FAIL", "value": out.strip()})
    return results


def verify_config_refs():
    results = []
    rl_cfg = SCRIPT_DIR / "baize_posttrain_rl_verl_config_v2.yaml"
    if rl_cfg.exists():
        m = re.search(r"train_files:\s*(\S+)", rl_cfg.read_text())
        if m:
            tf = m.group(1)
            exists = (SCRIPT_DIR / tf).exists()
            results.append({"label": "RL config train_files", "referenced": tf,
                            "exists": exists, "status": "PASS" if exists else "FAIL"})
    sft_cfg = SCRIPT_DIR / "baize_posttrain_sft_verl_config.yaml"
    if sft_cfg.exists():
        m = re.search(r"train_files:\s*(\S+)", sft_cfg.read_text())
        if m:
            tf = m.group(1)
            exists = (SCRIPT_DIR / tf).exists()
            r = {"label": "SFT config train_files", "referenced": tf,
                 "exists": exists, "status": "PASS" if exists else "FAIL"}
            if not exists:
                r["fix"] = "Change to sft_pyaether_corpus_v2.parquet"
            results.append(r)
    return results


def verify_bash_scripts():
    scripts = ["baize_posttrain_rl_grpo.sh", "baize_posttrain_sft.sh",
               "baize_posttrain_eval.sh", "baize_posttrain_anneal.sh",
               "baize_posttrain_launch_11_9.sh", "baize_posttrain_preflight_check.sh",
               "baize_posttrain_contamination_gate.sh", "baize_posttrain_gpu_watcher.sh",
               "baize_posttrain_minicpm5_diag.sh", "baize_posttrain_data_transfer.sh"]
    results = []
    for s in scripts:
        p = SCRIPT_DIR / s
        if not p.exists():
            results.append({"label": s, "status": "FAIL", "error": "Not found"})
            continue
        _, _, rc = run_cmd("bash -n '%s'" % p)
        results.append({"label": s, "status": "PASS" if rc == 0 else "FAIL", "rc": rc})
    return results


def verify_eval_assets():
    return [check_file("158-case dataset", EVAL_DS), check_file("Eval driver", EVAL_DRV),
            check_file("Eval scorer", EVAL_SCR), check_file("MiniCPM5-2B model", MODEL_DIR)]


def verify_gpu():
    out, _, rc = run_cmd("nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader 2>/dev/null")
    if rc != 0 or not out:
        return {"status": "WARN", "error": "nvidia-smi not available"}
    gpus, free_count = [], 0
    for line in out.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            used = int(parts[1].replace(" MiB", ""))
            total = int(parts[2].replace(" MiB", ""))
            free_mib = total - used
            if free_mib > 4000:
                free_count += 1
            gpus.append({"idx": parts[0], "free_mib": free_mib})
    return {"status": "PASS", "total": len(gpus), "free": free_count, "ready": free_count >= 4}


def fix_sft_config():
    sft_cfg = SCRIPT_DIR / "baize_posttrain_sft_verl_config.yaml"
    if not sft_cfg.exists():
        return {"status": "FAIL", "error": "Config not found"}
    content = sft_cfg.read_text()
    if "sft_blended_v1.parquet" in content:
        sft_cfg.write_text(content.replace(
            "train_files: sft_blended_v1.parquet",
            "train_files: sft_pyaether_corpus_v2.parquet  # R115 fix: was sft_blended_v1.parquet (never created)"))
        return {"status": "PASS", "action": "Replaced sft_blended_v1.parquet -> sft_pyaether_corpus_v2.parquet"}
    if "sft_pyaether_corpus_v2.parquet" in content:
        return {"status": "OK", "action": "Already references correct file"}
    return {"status": "WARN", "action": "Unexpected train_files value"}


def main():
    parser = argparse.ArgumentParser(description="R115 Pre-launch pipeline verification")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fix-config", action="store_true")
    args = parser.parse_args()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print("R115: Pre-launch Data Pipeline Verification")
    print("  Time: %s" % ts)
    print("=" * 60)
    print("\n[1] Config <-> Data References")
    cfg = verify_config_refs()
    for r in cfg:
        s = "PASS" if r["status"] == "PASS" else "FAIL"
        print("  [%s] %s: %s -> exists=%s" % (s, r["label"], r["referenced"], r["exists"]))
        if r.get("fix"):
            print("        FIX: %s" % r["fix"])
    print("\n[2] Parquet Schema Verification (via cu124 venv)")
    pq_res = [verify_parquet(SCRIPT_DIR / "rl_pyaether_synth_v2.parquet",
             ["prompt", "reward_model", "agent_name"], "RL parquet"),
             verify_parquet(SCRIPT_DIR / "sft_pyaether_corpus_v2.parquet",
             ["conversation", "pair_id", "type", "api_used", "contamination_check"], "SFT v2 parquet")]
    for r in pq_res:
        s = "PASS" if r["status"] == "PASS" else "FAIL"
        print("  [%s] %s: rows=%s cols=%s" % (s, r["label"], r.get("rows", "?"), r.get("columns", r.get("error", "?"))))
    print("\n[3] cu124 Venv Dependencies")
    venv = verify_venv()
    for r in venv:
        s = "PASS" if r["status"] == "PASS" else "FAIL"
        print("  [%s] %s: %s" % (s, r["label"], r.get("version", r.get("value", r.get("error", "?")))))
    print("\n[4] Bash Script Syntax (bash -n)")
    bash = verify_bash_scripts()
    for r in bash:
        s = "PASS" if r["status"] == "PASS" else "FAIL"
        print("  [%s] %s" % (s, r["label"]))
    print("\n[5] Evaluation Assets")
    evl = verify_eval_assets()
    for r in evl:
        s = "PASS" if r["status"] in ("PASS", "OK") else "FAIL"
        print("  [%s] %s: exists=%s (%s)" % (s, r["label"], r.get("exists"), r.get("size_human", "?")))
    print("\n[6] GPU Status")
    gpu = verify_gpu()
    print("  Free GPUs: %s/%s (need >=4)" % (gpu.get("free", "?"), gpu.get("total", "?")))
    print("  Ready for launch: %s" % gpu.get("ready", False))
    fix_r = None
    if args.fix_config:
        print("\n[7] Fix SFT Config")
        fix_r = fix_sft_config()
        s = "PASS" if fix_r["status"] in ("PASS", "OK") else "FAIL"
        print("  [%s] %s" % (s, fix_r.get("action", fix_r.get("error", "?"))))
    all_r = {"timestamp": ts, "round": "R115", "config_refs": cfg,
             "parquet_schemas": pq_res, "venv_deps": venv, "bash_scripts": bash,
             "eval_assets": evl, "gpu_status": gpu}
    if fix_r:
        all_r["config_fix"] = fix_r
    n_pass = sum(1 for r in cfg + pq_res + venv + bash + evl if r.get("status") in ("PASS", "OK"))
    n_fail = sum(1 for r in cfg + pq_res + venv + bash + evl if r.get("status") == "FAIL")
    print("\n" + "=" * 60)
    print("SUMMARY: %d PASS / %d FAIL" % (n_pass, n_fail))
    if gpu.get("ready"):
        print("GPU: READY -- launch can proceed")
    else:
        print("GPU: NOT READY (%s/8 free) -- watcher will auto-trigger" % gpu.get("free", 0))
    print("=" * 60)
    if args.json:
        print(json.dumps(all_r, indent=2, ensure_ascii=False, default=str))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
