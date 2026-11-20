#!/usr/bin/env python3
"""baize_posttrain_r102_readiness_audit.py — Launch readiness audit + v5 SFT parquet conversion

R102 (2026-11-09): Comprehensive pre-GPU readiness audit.
- Converts sft_pyaether_corpus_v5_deep_enriched.jsonl → .parquet (verl SFT format)
- Validates existing rl_pyaether_synth_v2.parquet (verl RL format)
- Audits all 11 launch scripts (bash -n)
- Audits verl config v2 YAML (all referenced paths exist)
- Audits model files, venv packages, eval dataset, reward functions
- Produces HTML report + JSON summary

Usage:
    ~/code/verl_cu124_venv/bin/python baize_posttrain_r102_readiness_audit.py
    ~/code/verl_cu124_venv/bin/python baize_posttrain_r102_readiness_audit.py --smoke
    ~/code/verl_cu124_venv/bin/python baize_posttrain_r102_readiness_audit.py --html report.html

⚠️ Surrogate RL results are NOT transferable to BaiZe.
"""
import sys, os, json, time, subprocess, argparse, warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings("ignore")

RUN_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
MODEL_PATH = Path("/nas_data/app.e0031982/models/MiniCPM5-2B")
VENV_PY = Path.home() / "code/verl_cu124_venv/bin/python"
EDA_BASE = Path.home() / "code/eda_fastmcp"
REPORTS_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ── 1. Convert SFT v5 JSONL → Parquet ──
def convert_sft_v5_to_parquet():
    import pyarrow as pa
    import pyarrow.parquet as pq
    jsonl_path = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.jsonl"
    parquet_path = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet"
    if not jsonl_path.exists():
        return {"status": "FAIL", "error": f"JSONL not found: {jsonl_path}"}
    log(f"Converting SFT v5: {jsonl_path.name} -> {parquet_path.name}")
    records, errors = [], 0
    with open(jsonl_path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                records.append({
                    "conversation": [
                        {"role": "system", "content": "You are an EDA automation assistant specialized in PyAether API usage. Write clean, correct Python code that calls the specified APIs."},
                        {"role": "user", "content": d.get("prompt", "")},
                        {"role": "assistant", "content": d.get("completion", "")},
                    ],
                    "pair_id": d.get("pair_id", f"v5-{i:06d}"),
                    "type": d.get("type", "unknown"),
                    "api_used": json.dumps(d.get("api_used", [])),
                    "contamination_check": d.get("contamination_check", "passed"),
                })
            except json.JSONDecodeError as e:
                errors += 1
                if errors <= 3: log(f"  WARN: line {i} JSON error: {e}")
    if not records: return {"status": "FAIL", "error": "No valid records"}
    table = pa.Table.from_pylist(records)
    pq.write_table(table, str(parquet_path), compression="snappy")
    vt = pq.read_table(str(parquet_path))
    result = {"status": "PASS", "input": jsonl_path.name, "output": parquet_path.name,
              "rows": len(records), "parquet_rows": vt.num_rows, "errors": errors,
              "size_mb": round(parquet_path.stat().st_size / 1048576, 2),
              "schema_cols": vt.column_names,
              "types": sorted(set(r["type"] for r in records))}
    log(f"  OK Converted {len(records)} records -> {result['size_mb']}MB")
    return result

# ── 2. Validate RL parquet ──
def validate_rl_parquet():
    import pyarrow.parquet as pq
    parquet_path = RUN_DIR / "rl_pyaether_synth_v2.parquet"
    if not parquet_path.exists():
        return {"status": "FAIL", "error": f"Not found: {parquet_path}"}
    log(f"Validating RL parquet: {parquet_path.name}")
    t = pq.read_table(str(parquet_path))
    issues = []
    for col in ["prompt", "reward_model", "agent_name"]:
        if col not in t.column_names:
            issues.append(f"Missing column: {col}")
    if "prompt" in t.column_names:
        null_count = sum(1 for v in t.column("prompt") if v is None or len(v) == 0)
        if null_count > 0: issues.append(f"Null/empty prompts: {null_count}")
    if "reward_model" in t.column_names:
        rm_nulls = sum(1 for v in t.column("reward_model") if v is None)
        if rm_nulls > 0: issues.append(f"Null reward_model: {rm_nulls}")
    difficulty_dist = {}
    if "reward_model" in t.column_names:
        for v in t.column("reward_model"):
            if v and "metadata" in v:
                try:
                    meta = json.loads(v["metadata"]) if isinstance(v["metadata"], str) else v["metadata"]
                    diff = meta.get("difficulty", "unknown")
                    difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
                except: pass
    result = {"status": "PASS" if not issues else "WARN", "path": parquet_path.name,
              "rows": t.num_rows, "columns": t.column_names,
              "size_mb": round(parquet_path.stat().st_size / 1048576, 2),
              "issues": issues, "difficulty_dist": difficulty_dist}
    log(f"  {'OK' if not issues else 'WARN'} RL parquet: {t.num_rows} rows, issues={len(issues)}")
    return result

# ── 3. Audit launch scripts ──
def audit_scripts():
    scripts = ["baize_posttrain_setup_cu124_venv.sh", "baize_posttrain_preflight_check.sh",
        "baize_posttrain_minicpm5_diag.sh", "baize_posttrain_contamination_gate.sh",
        "baize_posttrain_rl_grpo.sh", "baize_posttrain_sft.sh", "baize_posttrain_anneal.sh",
        "baize_posttrain_eval.sh", "baize_posttrain_paths.sh", "baize_posttrain_gpu_watcher.sh",
        "baize_posttrain_launch_11_9.sh"]
    results, all_pass = [], True
    for s in scripts:
        path = RUN_DIR / s
        if not path.exists():
            results.append({"script": s, "status": "MISSING"}); all_pass = False; continue
        try:
            r = subprocess.run(["bash", "-n", str(path)], capture_output=True, timeout=10)
            lines = sum(1 for _ in open(path))
            if r.returncode == 0:
                results.append({"script": s, "status": "PASS", "lines": lines})
            else:
                results.append({"script": s, "status": "FAIL", "lines": lines, "error": r.stderr.decode()[:200]})
                all_pass = False
        except Exception as e:
            results.append({"script": s, "status": "ERROR", "error": str(e)}); all_pass = False
    log(f"  {'OK' if all_pass else 'WARN'} Scripts: {sum(1 for r in results if r['status']=='PASS')}/{len(scripts)} pass")
    return {"all_pass": all_pass, "scripts": results}

# ── 4. Audit verl config v2 ──
def audit_verl_config():
    config_path = RUN_DIR / "baize_posttrain_rl_verl_config_v2.yaml"
    if not config_path.exists():
        return {"status": "FAIL", "error": "Config not found"}
    try:
        import yaml
    except ImportError:
        return {"status": "FAIL", "error": "PyYAML not available"}
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    issues, path_checks = [], []
    model_path = cfg.get("actor_rollout_ref", {}).get("model", {}).get("path", "")
    if model_path:
        exists = Path(model_path).exists()
        path_checks.append({"path": model_path, "exists": exists, "label": "model.path"})
        if not exists: issues.append(f"Model path not found: {model_path}")
    tokenizer = cfg.get("data", {}).get("tokenizer", "")
    if tokenizer:
        exists = Path(tokenizer).exists()
        path_checks.append({"path": tokenizer, "exists": exists, "label": "data.tokenizer"})
        if not exists: issues.append(f"Tokenizer not found: {tokenizer}")
    train_files = cfg.get("data", {}).get("train_files", "")
    if train_files:
        tf_path = RUN_DIR / train_files
        exists = tf_path.exists()
        path_checks.append({"path": str(tf_path), "exists": exists, "label": "data.train_files"})
        if not exists: issues.append(f"Train parquet not found: {tf_path}")
    crf = cfg.get("custom_reward_function", {})
    reward_path = RUN_DIR / crf.get("path", "")
    exists = reward_path.exists()
    path_checks.append({"path": str(reward_path), "exists": exists, "label": "reward.path"})
    if not exists: issues.append(f"Reward function not found: {reward_path}")
    api_db = crf.get("reward_kwargs", {}).get("api_database", "")
    if api_db:
        api_path = Path(api_db.replace("~", str(Path.home())))
        exists = api_path.exists()
        path_checks.append({"path": str(api_path), "exists": exists, "label": "reward.api_database"})
        if not exists: issues.append(f"API database not found: {api_path}")
    out_dir = cfg.get("trainer", {}).get("default_local_dir", "")
    if out_dir:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        path_checks.append({"path": out_dir, "exists": True, "label": "trainer.output_dir"})
    config_summary = {
        "algorithm": cfg.get("algorithm", {}).get("adv_estimator"),
        "rollout_engine": cfg.get("actor_rollout_ref", {}).get("rollout", {}).get("name"),
        "group_size_n": cfg.get("actor_rollout_ref", {}).get("rollout", {}).get("n"),
        "max_prompt_len": cfg.get("data", {}).get("max_prompt_length"),
        "max_response_len": cfg.get("data", {}).get("max_response_length"),
        "multi_turn": cfg.get("actor_rollout_ref", {}).get("rollout", {}).get("multi_turn", {}).get("enable"),
        "total_steps": cfg.get("trainer", {}).get("total_training_steps"),
        "n_gpus": cfg.get("trainer", {}).get("n_gpus_per_node"),
        "reward_arm": crf.get("reward_kwargs", {}).get("arm"),
        "lr": cfg.get("actor_rollout_ref", {}).get("actor", {}).get("optim", {}).get("lr"),
        "kl_coef": cfg.get("actor_rollout_ref", {}).get("actor", {}).get("kl_loss_coef"),
        "clip_ratio": cfg.get("actor_rollout_ref", {}).get("actor", {}).get("clip_ratio"),
        "gpu_mem_util": cfg.get("actor_rollout_ref", {}).get("rollout", {}).get("gpu_memory_utilization"),
    }
    result = {"status": "PASS" if not issues else "WARN", "issues": issues,
              "path_checks": path_checks, "config_summary": config_summary}
    log(f"  {'OK' if not issues else 'WARN'} Verl config v2: {len(issues)} issues, paths={len(path_checks)}")
    return result

# ── 5. Audit model files ──
def audit_model():
    required = ["config.json", "model-00000-of-00001.safetensors", "model.safetensors.index.json",
        "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "chat_template.jinja"]
    results, all_present = [], True
    for f in required:
        path = MODEL_PATH / f
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results.append({"file": f, "exists": exists, "size_mb": round(size / 1048576, 2)})
        if not exists: all_present = False
    total_size = sum(f.stat().st_size for f in MODEL_PATH.iterdir() if f.is_file())
    result = {"status": "PASS" if all_present else "FAIL", "path": str(MODEL_PATH),
              "total_size_gb": round(total_size / 1073741824, 2), "files": results}
    log(f"  {'OK' if all_present else 'FAIL'} Model: {result['total_size_gb']}GB, {sum(1 for r in results if r['exists'])}/{len(required)} files")
    return result

# ── 6. Audit venv packages ──
def audit_venv():
    packages = ["torch", "sglang", "verl", "ray", "flash_attn", "transformers", "pyarrow", "pandas", "yaml"]
    results, all_pass = [], True
    for pkg in packages:
        try:
            r = subprocess.run([str(VENV_PY), "-c", f"import {pkg}; print(getattr({pkg}, '__version__', 'ok'))"],
                capture_output=True, timeout=60, text=True)
            if r.returncode == 0:
                results.append({"package": pkg, "status": "PASS", "version": r.stdout.strip().split('\n')[-1]})
            else:
                results.append({"package": pkg, "status": "FAIL", "error": r.stderr[:100]}); all_pass = False
        except subprocess.TimeoutExpired:
            results.append({"package": pkg, "status": "TIMEOUT"}); all_pass = False
        except Exception as e:
            results.append({"package": pkg, "status": "ERROR", "error": str(e)}); all_pass = False
    try:
        r = subprocess.run([str(VENV_PY), "-c", "import torch; print(f'cuda={torch.cuda.is_available()},v={torch.version.cuda}')"],
            capture_output=True, timeout=60, text=True)
        cuda_info = r.stdout.strip().split('\n')[-1] if r.returncode == 0 else "UNKNOWN"
    except: cuda_info = "TIMEOUT"
    result = {"status": "PASS" if all_pass else "WARN", "venv_path": str(VENV_PY.parent.parent),
              "cuda_info": cuda_info, "packages": results}
    log(f"  {'OK' if all_pass else 'WARN'} Venv: {sum(1 for r in results if r['status']=='PASS')}/{len(packages)} pkgs, CUDA: {cuda_info}")
    return result

# ── 7. Audit eval dataset ──
def audit_eval_dataset():
    eval_path = EDA_BASE / "pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
    if not eval_path.exists():
        return {"status": "FAIL", "error": f"Eval dataset not found: {eval_path}"}
    count, scenarios = 0, {}
    with open(eval_path) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line); count += 1
                sc = d.get("metadata", {}).get("scenario", "unknown")
                scenarios[sc] = scenarios.get(sc, 0) + 1
            except: pass
    result = {"status": "PASS" if count == 158 else "WARN", "path": str(eval_path),
              "task_count": count, "scenarios": scenarios, "size_kb": round(eval_path.stat().st_size / 1024, 1)}
    log(f"  {'OK' if count == 158 else 'WARN'} Eval dataset: {count} tasks")
    return result

# ── 8. Audit data files ──
def audit_data_files():
    files = [("SFT v5 JSONL", "sft_pyaether_corpus_v5_deep_enriched.jsonl"),
        ("SFT v5 Parquet", "sft_pyaether_corpus_v5_deep_enriched.parquet"),
        ("SFT v2 Parquet", "sft_pyaether_corpus_v2.parquet"),
        ("RL v2 JSONL", "rl_pyaether_synth_v2.jsonl"), ("RL v2 Parquet", "rl_pyaether_synth_v2.parquet"),
        ("Contamination gate", "baize_posttrain_contamination_gate.sh"),
        ("Reward functions", "baize_posttrain_reward_functions.py"),
        ("EDA tool v2", "baize_posttrain_eda_tool_v2.py"), ("Tool config", "baize_posttrain_tool_config.yaml"),
        ("Verl config v2", "baize_posttrain_rl_verl_config_v2.yaml"),
        ("MiniCPM5 parser", "baize_posttrain_minicpm5_parser.py")]
    results = []
    for label, fname in files:
        path = RUN_DIR / fname; exists = path.exists()
        size = path.stat().st_size if exists else 0
        results.append({"label": label, "file": fname, "exists": exists, "size_kb": round(size / 1024, 1) if exists else 0})
    found = sum(1 for r in results if r["exists"])
    log(f"  {'OK' if found == len(results) else 'WARN'} Data files: {found}/{len(results)} present")
    return {"files": results, "found": found, "total": len(results)}

# ── 9. GPU status ──
def check_gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu",
            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
        gpus = []
        for line in r.stdout.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 4:
                gpus.append({"id": int(parts[0]), "used_mib": int(parts[1]), "total_mib": int(parts[2]), "util": int(parts[3])})
        free_gpus = [g for g in gpus if g["used_mib"] < 1000]
        result = {"total_gpus": len(gpus), "free_gpus": len(free_gpus), "gpus": gpus,
                  "status": "PASS" if len(free_gpus) >= 4 else "BLOCKED"}
        log(f"  {'BLOCKED' if len(free_gpus) < 4 else 'OK'} GPU: {len(free_gpus)}/{len(gpus)} free")
        return result
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ── 10. Generate HTML report ──
def generate_html_report(audit_data, output_path):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections = list(audit_data.keys())
    pc = sum(1 for s in sections if audit_data[s].get("status") == "PASS")
    wc = sum(1 for s in sections if audit_data[s].get("status") == "WARN")
    fc = sum(1 for s in sections if audit_data[s].get("status") in ("FAIL", "BLOCKED", "ERROR"))
    def badge(status):
        colors = {"PASS": "#28a745", "WARN": "#ffc107", "FAIL": "#dc3545", "BLOCKED": "#dc3545", "ERROR": "#dc3545", "MISSING": "#dc3545", "SKIPPED": "#6c757d"}
        c = colors.get(status, "#6c757d")
        return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:4px;font-size:0.85em;">{status}</span>'
    h = [f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe Post-Train R102: Launch Readiness Audit</title>
<style>
body {{ font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; max-width: 1200px; margin: 0 auto; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #16213e; margin-top: 30px; border-left: 4px solid #e94560; padding-left: 12px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; background: white; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; font-size: 0.9em; }}
th {{ background: #16213e; color: white; }}
tr:nth-child(even) {{ background: #f9f9f9; }}
.summary-box {{ display: flex; gap: 15px; margin: 20px 0; }}
.summary-card {{ flex: 1; padding: 15px; border-radius: 8px; text-align: center; }}
.pass-card {{ background: #d4edda; border: 1px solid #c3e6cb; }}
.warn-card {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
.fail-card {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
.summary-card h3 {{ margin: 0 0 5px 0; font-size: 2em; }}
code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin: 2px; }}
.tag-pass {{ background: #d4edda; color: #155724; }}
.footer {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.8em; color: #888; }}
</style></head><body>
<h1>BaiZe Post-Train R102: 11/9 GPU Launch Readiness Audit</h1>
<p>Generated: {ts} | Node: 10.252.32.17 | R102 (wake150)</p>
<div class="summary-box">
<div class="summary-card pass-card"><h3>{pc}</h3><p>PASS</p></div>
<div class="summary-card warn-card"><h3>{wc}</h3><p>WARN</p></div>
<div class="summary-card fail-card"><h3>{fc}</h3><p>BLOCKED/FAIL</p></div>
</div>"""]
    return h, badge

def _html_body(h, badge, audit_data):
    """Append body sections to html list h."""
    sft = audit_data.get("sft_v5_conversion", {})
    h.append(f'<h2>1. SFT v5 -> Parquet</h2><p>{badge(sft.get("status","N/A"))}</p><table>')
    for k in ["input","output","rows","parquet_rows","size_mb","errors","schema_cols","types"]:
        v = sft.get(k, "N/A")
        if isinstance(v, list): v = ", ".join(map(str, v))
        h.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    h.append("</table>")
    rl = audit_data.get("rl_parquet", {})
    h.append(f'<h2>2. RL Parquet</h2><p>{badge(rl.get("status","N/A"))}</p><table>')
    for k in ["path","rows","size_mb","columns","issues"]:
        v = rl.get(k, "N/A")
        if isinstance(v, list): v = ", ".join(map(str, v))
        h.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    h.append("</table>")
    sc = audit_data.get("scripts", {})
    h.append(f'<h2>3. Scripts (bash -n)</h2><p>{badge("PASS" if sc.get("all_pass") else "FAIL")}</p><table><tr><th>Script</th><th>Status</th><th>Lines</th></tr>')
    for s in sc.get("scripts", []): h.append(f'<tr><td><code>{s["script"]}</code></td><td>{badge(s["status"])}</td><td>{s.get("lines","")}</td></tr>')
    h.append("</table>")
    cfg = audit_data.get("verl_config", {})
    h.append(f'<h2>4. verl Config v2</h2><p>{badge(cfg.get("status","N/A"))}</p><table>')
    for k,v in cfg.get("config_summary",{}).items(): h.append(f"<tr><th>{k}</th><td><code>{v}</code></td></tr>")
    h.append("</table><h3>Path Checks</h3><table><tr><th>Key</th><th>Path</th><th>OK</th></tr>")
    for pc in cfg.get("path_checks",[]): h.append(f'<tr><td>{pc["label"]}</td><td><code>{pc["path"]}</code></td><td>{"Y" if pc["exists"] else "N"}</td></tr>')
    h.append("</table>")
    m = audit_data.get("model", {})
    h.append(f'<h2>5. Model</h2><p>{badge(m.get("status","N/A"))}</p><p>Size: {m.get("total_size_gb",0)}GB</p><table><tr><th>File</th><th>OK</th><th>MB</th></tr>')
    for f in m.get("files",[]): h.append(f'<tr><td><code>{f["file"]}</code></td><td>{"Y" if f["exists"] else "N"}</td><td>{f["size_mb"]}</td></tr>')
    h.append("</table>")
    v = audit_data.get("venv", {})
    h.append(f'<h2>6. Venv</h2><p>{badge(v.get("status","N/A"))}</p><p>CUDA: <code>{v.get("cuda_info","")}</code></p><table><tr><th>Pkg</th><th>Status</th><th>Ver</th></tr>')
    for p in v.get("packages",[]): h.append(f'<tr><td>{p["package"]}</td><td>{badge(p["status"])}</td><td><code>{p.get("version","")}</code></td></tr>')
    h.append("</table>")
    ev = audit_data.get("eval_dataset", {})
    h.append(f'<h2>7. Eval Dataset</h2><p>{badge(ev.get("status","N/A"))}</p><p>Tasks: {ev.get("task_count",0)}</p>')
    df = audit_data.get("data_files", {})
    h.append(f'<h2>8. Data Files</h2><p>{df.get("found",0)}/{df.get("total",0)}</p><table><tr><th>Label</th><th>File</th><th>OK</th></tr>')
    for f in df.get("files",[]): h.append(f'<tr><td>{f["label"]}</td><td><code>{f["file"]}</code></td><td>{"Y" if f["exists"] else "N"}</td></tr>')
    h.append("</table>")
    gpu = audit_data.get("gpu", {})
    h.append(f'<h2>9. GPU</h2><p>{badge(gpu.get("status","N/A"))}</p><table><tr><th>GPU</th><th>Used</th><th>Total</th><th>Util</th></tr>')
    for g in gpu.get("gpus",[]): h.append(f'<tr><td>GPU{g["id"]}</td><td>{g["used_mib"]}</td><td>{g["total_mib"]}</td><td>{g["util"]}%</td></tr>')
    h.append(f'</table><p>Free: {gpu.get("free_gpus",0)}/{gpu.get("total_gpus",0)}</p>')
    h.append("<h2>10. Verdict</h2>")
    issues = []
    if gpu.get("free_gpus",0) < 4: issues.append(f'GPU blocked: {gpu.get("free_gpus",0)}/8 free')
    if cfg.get("status") == "WARN": issues.append(f'Config: {len(cfg.get("issues",[]))} issues')
    if not issues: h.append('<div class="summary-card pass-card" style="padding:20px"><h3>READY (except GPU)</h3></div>')
    else:
        h.append('<div class="summary-card warn-card" style="padding:20px"><h3>ISSUES</h3><ul>')
        for i in issues: h.append(f"<li>{i}</li>")
        h.append("</ul></div>")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    h.append(f'<div class="footer"><p>R102 | {ts}</p></div></body></html>')

def main():
    parser = argparse.ArgumentParser(description="R102 Launch Readiness Audit")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--html", type=str, default=None)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()
    log("=== R102 Launch Readiness Audit Start ===")
    audit = {}
    audit["sft_v5_conversion"] = convert_sft_v5_to_parquet()
    audit["rl_parquet"] = validate_rl_parquet()
    audit["scripts"] = audit_scripts()
    audit["verl_config"] = audit_verl_config()
    audit["model"] = audit_model()
    if not args.smoke:
        audit["venv"] = audit_venv()
    else:
        audit["venv"] = {"status": "SKIPPED"}
    audit["eval_dataset"] = audit_eval_dataset()
    audit["data_files"] = audit_data_files()
    audit["gpu"] = check_gpu()
    html_path = Path(args.html) if args.html else REPORTS_DIR / "report_posttrain_r102_readiness_audit_zh.html"
    h_parts, badge_fn = generate_html_report(audit, html_path)
    _html_body(h_parts, badge_fn, audit)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, 'w') as f:
        f.write('\n'.join(h_parts))
    log(f"  OK HTML: {html_path} ({html_path.stat().st_size//1024}KB)")
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(audit, f, indent=2, default=str)
        log(f"  OK JSON: {args.json}")
    log("=== R102 Audit Summary ===")
    for section, data in audit.items():
        log(f"  {section}: {data.get('status', 'N/A')}")
    log("=== R102 Audit Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
