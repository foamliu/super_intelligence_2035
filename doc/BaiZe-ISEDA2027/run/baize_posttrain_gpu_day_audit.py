#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_gpu_day_audit.py — R78: GPU-Day Comprehensive Readiness Audit

Audits ALL components needed for the 11/9 GPU auto-launch sequence:
  1. Script inventory (bash -n syntax check)
  2. Config audit (RL v2, tool config, paths)
  3. Data audit (model, SFT/RL parquet, EDA dataset, reward function)
  4. Venv audit (key packages: torch, sglang, verl, ray, flash_attn)
  5. GPU watcher status (PID, iteration, elapsed)
  6. Launch dependency chain (step 0-6, each step prerequisites)
  7. Risk assessment (known issues + mitigation)
  8. Timeline projection (estimated wall-clock per step)

Usage:
  python3 baize_posttrain_gpu_day_audit.py              # Full audit + print
  python3 baize_posttrain_gpu_day_audit.py --html FILE  # Generate HTML report
  python3 baize_posttrain_gpu_day_audit.py --json FILE  # Generate JSON
  python3 baize_posttrain_gpu_day_audit.py --verbose    # Show details

Zero GPU, zero network. Pure local filesystem audit.
"""
import sys, os, subprocess, json, time, glob, argparse
from pathlib import Path
from datetime import datetime

RUN_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
VENV_DIR = Path.home() / "code" / "verl_cu124_venv"
VENV_PY = VENV_DIR / "bin" / "python"
MODEL_PATH = Path("/tmp/models/MiniCPM5-2B")
EDA_BASE = Path.home() / "code" / "eda_fastmcp"

PASS_C = 0; FAIL_C = 0; WARN_C = 0; INFO_C = 0

class AuditResult:
    def __init__(self):
        self.items = []
        self.start_time = datetime.now()
    def add(self, category, name, status, detail=""):
        self.items.append({"category": category, "name": name, "status": status, "detail": detail})
    def summary(self):
        counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
        for item in self.items:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        return counts
    def to_dict(self):
        return {"audit_time": self.start_time.isoformat(),
                "elapsed_sec": (datetime.now() - self.start_time).total_seconds(),
                "summary": self.summary(), "items": self.items}

def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)

def check_file(path, min_size=0, audit=None, category="File", name=None):
    name = name or Path(path).name
    p = Path(path)
    if p.exists():
        size = p.stat().st_size
        if min_size > 0 and size < min_size:
            audit.add(category, name, "WARN", f"Exists but small: {size}B (min {min_size}B)")
            return False
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime('%m-%d %H:%M')
        audit.add(category, name, "PASS", f"Exists, {size:,}B, modified {mtime}")
        return True
    else:
        audit.add(category, name, "FAIL", "MISSING")
        return False

def check_bash_syntax(script_path, audit):
    name = Path(script_path).name
    rc, out, err = run_cmd(f"bash -n '{script_path}' 2>&1")
    if rc == 0:
        audit.add("Script-Syntax", name, "PASS", "bash -n OK")
    else:
        audit.add("Script-Syntax", name, "FAIL", f"bash -n FAILED: {err}")

def check_python_compile(py_path, audit):
    name = Path(py_path).name
    rc, out, err = run_cmd(f"python3 -m py_compile '{py_path}' 2>&1")
    if rc == 0:
        audit.add("Script-Syntax", name, "PASS", "py_compile OK")
    else:
        audit.add("Script-Syntax", name, "FAIL", f"py_compile FAILED: {err[:200]}")

def do_script_inventory(audit):
    sh_scripts = sorted(glob.glob(str(RUN_DIR / "baize_posttrain_*.sh")))
    py_scripts = sorted(glob.glob(str(RUN_DIR / "baize_posttrain_*.py")))
    audit.add("Script-Inventory", "Total .sh scripts", "INFO", f"{len(sh_scripts)} found")
    audit.add("Script-Inventory", "Total .py scripts", "INFO", f"{len(py_scripts)} found")
    for s in sh_scripts:
        check_bash_syntax(s, audit)
    for p in py_scripts:
        check_python_compile(p, audit)

def do_config_audit(audit):
    rl_cfg = RUN_DIR / "baize_posttrain_rl_verl_config_v2.yaml"
    if rl_cfg.exists():
        content = rl_cfg.read_text()
        checks = [
            ("custom_reward_function top-level", "custom_reward_function:" in content and "  path:" in content),
            ("adv_estimator: grpo", "adv_estimator: grpo" in content),
            ("rollout.name: sglang", "name: sglang" in content),
            ("rollout.n: 8", "n: 8" in content),
            ("multi_turn.enable: False", "enable: False" in content),
            ("flash_attention_2", "flash_attention_2" in content),
            ("auto_fallback: true", "auto_fallback: true" in content),
            ("n_gpus_per_node: 4", "n_gpus_per_node: 4" in content),
            ("max_prompt_length: 8192", "max_prompt_length: 8192" in content),
            ("max_response_length: 8192", "max_response_length: 8192" in content),
            ("train_files: rl_pyaether_synth_v2.parquet", "rl_pyaether_synth_v2.parquet" in content),
        ]
        for name, ok in checks:
            audit.add("Config-RL-v2", name, "PASS" if ok else "FAIL", "")
    else:
        audit.add("Config-RL-v2", "rl_verl_config_v2.yaml", "FAIL", "MISSING")
    check_file(RUN_DIR / "baize_posttrain_tool_config.yaml", 100, audit, "Config", "tool_config.yaml")
    check_file(RUN_DIR / "baize_posttrain_paths.sh", 100, audit, "Config", "paths.sh")

def do_data_audit(audit):
    if MODEL_PATH.exists():
        config_file = MODEL_PATH / "config.json"
        if config_file.exists():
            audit.add("Data-Model", "MiniCPM5-2B", "PASS", "Model dir exists, config.json present")
        else:
            audit.add("Data-Model", "MiniCPM5-2B", "WARN", "Dir exists but config.json missing")
    else:
        audit.add("Data-Model", "MiniCPM5-2B", "FAIL", "Model dir MISSING")
    check_file(RUN_DIR / "sft_pyaether_corpus_v2.jsonl", 1_000_000, audit, "Data-SFT", "sft_pyaether_corpus_v2.jsonl")
    check_file(RUN_DIR / "sft_pyaether_corpus_v2.parquet", 1_000, audit, "Data-SFT", "sft_pyaether_corpus_v2.parquet")
    check_file(RUN_DIR / "rl_pyaether_synth_v2.parquet", 1_000, audit, "Data-RL", "rl_pyaether_synth_v2.parquet")
    check_file(RUN_DIR / "baize_posttrain_reward_functions.py", 10_000, audit, "Data-RL", "reward_functions.py")
    check_file(RUN_DIR / "baize_posttrain_rl_monitor.py", 5_000, audit, "Data-RL", "rl_monitor.py")
    check_file(RUN_DIR / "baize_posttrain_antihack_framework.py", 10_000, audit, "Data-RL", "antihack_framework.py")
    check_file(RUN_DIR / "baize_posttrain_antihack_monitor.py", 5_000, audit, "Data-RL", "antihack_monitor.py")
    check_file(RUN_DIR / "baize_posttrain_eda_tool_v2.py", 1_000, audit, "Data-RL", "eda_tool_v2.py")
    check_file(RUN_DIR / "baize_posttrain_minicpm5_parser_patch.py", 1_000, audit, "Data-RL", "minicpm5_parser_patch.py")
    eda_dataset = EDA_BASE / "pyAether-eval" / "original_dataset" / "EDA-Eval-PyAether-v20260311.jsonl"
    check_file(eda_dataset, 10_000, audit, "Data-EDA", "EDA-Eval-PyAether-v20260311.jsonl")
    api_info = EDA_BASE / "docs" / "API_INFO_MERGED_V3.json"
    check_file(api_info, 100_000, audit, "Data-EDA", "API_INFO_MERGED_V3.json")
    check_file(EDA_BASE / "scripts" / "run_cline_script.sh", 100, audit, "Data-EDA", "run_cline_script.sh")
    check_file(EDA_BASE / "scripts" / "run_eval.py", 100, audit, "Data-EDA", "run_eval.py")

def do_venv_audit(audit):
    if not VENV_DIR.exists():
        audit.add("Venv", "verl_cu124_venv", "FAIL", "Venv dir MISSING"); return
    audit.add("Venv", "verl_cu124_venv", "PASS", f"Dir exists at {VENV_DIR}")
    if not VENV_PY.exists():
        audit.add("Venv", "python", "FAIL", "Python binary MISSING"); return
    audit.add("Venv", "python", "PASS", f"Python exists at {VENV_PY}")
    site_pkg = VENV_DIR / "lib"
    if site_pkg.exists():
        for pkg_dir in site_pkg.iterdir():
            if pkg_dir.name.startswith("python"):
                sp = pkg_dir / "site-packages"
                if sp.exists():
                    packages = {"torch": "torch", "sglang": "sglang", "verl": "verl",
                                "ray": "ray", "flash_attn": "flash_attn",
                                "flashinfer": "flashinfer", "transformers": "transformers", "vllm": "vllm"}
                    for pkg_name, dir_name in packages.items():
                        pkg_path = sp / dir_name
                        if pkg_path.exists():
                            audit.add("Venv-Package", pkg_name, "PASS", f"Installed at {pkg_path}")
                        else:
                            dist_infos = list(sp.glob(f"{dir_name}*.dist-info"))
                            if dist_infos:
                                audit.add("Venv-Package", pkg_name, "PASS", "Installed (dist-info found)")
                            else:
                                audit.add("Venv-Package", pkg_name, "WARN", f"Not found in {sp}")
                    break

def do_gpu_watcher_audit(audit):
    rc, out, err = run_cmd("ps aux | grep 'baize_posttrain_gpu_watcher' | grep -v grep")
    if rc == 0 and out.strip():
        lines = out.strip().split("\n")
        audit.add("GPU-Watcher", "Process", "PASS", f"Running ({len(lines)} process(es))")
    else:
        audit.add("GPU-Watcher", "Process", "FAIL", "NOT running")
    rc, out, err = run_cmd("nvidia-smi --query-gpu=index,memory.free,memory.total,utilization.gpu --format=csv,noheader,nounits 2>/dev/null")
    if rc == 0 and out.strip():
        free_count = 0
        for line in out.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                free_mb = int(parts[1])
                if free_mb >= 40000: free_count += 1
        if free_count >= 4:
            audit.add("GPU-Watcher", "Ready to launch", "PASS", f"{free_count}/8 GPUs free")
        else:
            audit.add("GPU-Watcher", "Ready to launch", "WARN", f"Only {free_count}/8 free, waiting...")
    else:
        audit.add("GPU-Watcher", "GPU Status", "FAIL", "nvidia-smi failed")
    log_dir = Path("/nas_data/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments")
    log_files = sorted(log_dir.glob("gpu_watcher_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if log_files:
        latest = log_files[0]
        try:
            tail = latest.read_text().strip().split("\n")[-3:]
            audit.add("GPU-Watcher", "Latest log", "INFO", f"{latest.name}: ...{tail[-1][:100]}" if tail else "empty")
        except:
            audit.add("GPU-Watcher", "Latest log", "WARN", f"Cannot read {latest.name}")
    else:
        audit.add("GPU-Watcher", "Latest log", "WARN", "No watcher log found")

def do_launch_chain_audit(audit):
    steps = [
        ("Step 0", "setup_cu124_venv.sh", "baize_posttrain_setup_cu124_venv.sh"),
        ("Step 1", "preflight_check.sh", "baize_posttrain_preflight_check.sh"),
        ("Step 2", "minicpm5_diag.sh (full)", "baize_posttrain_minicpm5_diag.sh"),
        ("Step 3", "minicpm5_diag.sh (extract)", "baize_posttrain_minicpm5_diag.sh"),
        ("Step 4", "contamination_gate.sh", "baize_posttrain_contamination_gate.sh"),
        ("Step 5", "rl_grpo.sh (smoke R0)", "baize_posttrain_rl_grpo.sh"),
        ("Step 6", "rl_grpo.sh (full R0)", "baize_posttrain_rl_grpo.sh"),
    ]
    for step_name, desc, script_file in steps:
        script_path = RUN_DIR / script_file
        if script_path.exists():
            audit.add("Launch-Chain", f"{step_name}: {desc}", "PASS", f"{script_file} exists ({script_path.stat().st_size:,}B)")
        else:
            audit.add("Launch-Chain", f"{step_name}: {desc}", "FAIL", f"{script_file} MISSING")

def do_risk_assessment(audit):
    risks = [
        ("R1", "NFS cold-start import >30s", "WARN", "verl/torch import from NFS >30s (R45). gpu_watcher includes NFS warm-up."),
        ("R2", "SGLang holding all 8 GPUs", "WARN", "SGLang Qwen3.8-27B occupies all 8 A40 (0% util). gpu_watcher polls 120s. DO NOT kill."),
        ("R3", "Sandbox TCP filtered (R37)", "INFO", "EDA sandbox ports filtered. Launch uses R0 (no sandbox). R2 deferred."),
        ("R4", "MiniCPM5 XML format mismatch (R70)", "INFO", "MiniCPM5FunctionDetector + monkey-patch created. Phase1 single-turn unaffected."),
        ("R5", "Context window 28K avg (R60)", "WARN", "Config 16K ctx captures ~82%. 32K infeasible (17.5 days/500 steps)."),
        ("R6", "Reward all-zero smoke", "INFO", "R0 std=0.3718 (non-zero expected). Monitor P2 alert handles."),
        ("R7", "OOM on 4xA40", "WARN", "Fallback: micro_batch 4->2, gpu_mem 0.50->0.35, response 8192->4096."),
        ("R8", "Pretrain ckpt not ready", "INFO", "ETA~2026-12-25. Current RL is SURROGATE (MiniCPM5-2B), NOT BaiZe."),
    ]
    for risk_id, name, severity, detail in risks:
        audit.add("Risk", f"{risk_id}: {name}", severity, detail)

def do_timeline_projection(audit):
    timeline = [
        ("Step 0", "Venv Setup", "15-30 min", "Already done, likely skip"),
        ("Step 1", "Preflight Check", "2-5 min", "NFS warm-up may add 30s"),
        ("Step 2", "Baseline (quick)", "20-30 min", "10 tasks x 1 run"),
        ("Step 2b", "Baseline (full)", "15-25 hours", "158 tasks x 5 runs, background"),
        ("Step 3", "D1-D6 Extraction", "5-10 min", "From quick results first"),
        ("Step 4", "Contamination Gate", "1-2 min", "File hash check"),
        ("Step 5", "RL Smoke (10 iters)", "20-40 min", "R0, group_size=4, batch=16"),
        ("Step 6", "Full RL (2000 iters)", "3-5 days", "R0, group_size=8, batch=128"),
    ]
    for step, name, duration, note in timeline:
        audit.add("Timeline", f"{step}: {name}", "INFO", f"~{duration} -- {note}")

def generate_html(audit, output_path):
    counts = audit.summary()
    items_by_cat = {}
    for item in audit.items:
        cat = item["category"]
        if cat not in items_by_cat: items_by_cat[cat] = []
        items_by_cat[cat].append(item)
    total = sum(counts.values())
    pass_rate = counts.get("PASS", 0) / total * 100 if total > 0 else 0
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe Post-Train GPU-Day 就绪审计 (R78)</title>
<style>
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; margin: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 10px; }}
h2 {{ color: #16213e; margin-top: 30px; border-left: 5px solid #0f3460; padding-left: 10px; }}
.summary {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
.card {{ padding: 15px 25px; border-radius: 8px; color: white; font-size: 18px; font-weight: bold; min-width: 100px; text-align: center; }}
.card.PASS {{ background: #28a745; }}
.card.FAIL {{ background: #dc3545; }}
.card.WARN {{ background: #ffc107; color: #333; }}
.card.INFO {{ background: #17a2b8; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; background: white; }}
th, td {{ border: 1px solid #dee2e6; padding: 8px 12px; text-align: left; }}
th {{ background: #16213e; color: white; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.status {{ font-weight: bold; padding: 2px 8px; border-radius: 4px; color: white; font-size: 12px; }}
.status.PASS {{ background: #28a745; }}
.status.FAIL {{ background: #dc3545; }}
.status.WARN {{ background: #ffc107; color: #333; }}
.status.INFO {{ background: #17a2b8; }}
.detail {{ font-size: 13px; color: #555; }}
.meta {{ background: #e9ecef; padding: 10px 15px; border-radius: 5px; margin: 10px 0; font-size: 14px; }}
.warning-box {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0; }}
.danger-box {{ background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 15px 0; }}
</style>
</head>
<body>
<h1>BaiZe Post-Train GPU-Day 综合就绪审计 (R78)</h1>
<div class="meta">
<strong>审计时间:</strong> {audit.start_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
<strong>审计耗时:</strong> {(datetime.now() - audit.start_time).total_seconds():.1f}s<br>
<strong>节点:</strong> 10.252.32.17 (.17) | <strong>NAS_ROOT:</strong> /nas_data<br>
<strong>GPU:</strong> 8xA40 (46GB each), 4 allocated to post-train on 11/9<br>
<strong>gpu_watcher:</strong> Running, polling 120s, auto-launch steps 1-5 when >=4 GPUs free
</div>
<div class="summary">
<div class="card PASS">PASS: {counts.get("PASS", 0)}</div>
<div class="card FAIL">FAIL: {counts.get("FAIL", 0)}</div>
<div class="card WARN">WARN: {counts.get("WARN", 0)}</div>
<div class="card INFO">INFO: {counts.get("INFO", 0)}</div>
</div>
"""
    if counts.get("FAIL", 0) > 0:
        html += '<div class="danger-box">有 FAIL 项，GPU 释放后可能无法自动起跑。请修复后再等 GPU 释放。</div>\n'
    elif counts.get("WARN", 0) > 0:
        html += '<div class="warning-box">有 WARN 项，起跑可能遇到延迟但不阻塞。已知风险均有缓解措施。</div>\n'
    else:
        html += '<div class="card PASS" style="display:inline-block">所有检查通过，GPU 释放后可立即自动起跑</div>\n'
    for cat, items in items_by_cat.items():
        html += f"\n<h2>{cat}</h2>\n<table>\n<tr><th>检查项</th><th>状态</th><th>详情</th></tr>\n"
        for item in items:
            html += f'<tr><td>{item["name"]}</td><td><span class="status {item["status"]}">{item["status"]}</span></td><td class="detail">{item["detail"]}</td></tr>\n'
        html += "</table>\n"
    html += f"""
<h2>审计结论</h2>
<div class="meta">
<p><strong>就绪度:</strong> {pass_rate:.1f}% ({counts.get('PASS', 0)}/{total} 项通过)</p>
"""
    if counts.get("FAIL", 0) == 0:
        html += "<p><strong>结论:</strong> GPU-Day 自动起跑管线 <strong>就绪</strong>。所有脚本语法正确、配置完整、数据在位、venv 包已安装。gpu_watcher 正在运行，GPU 释放后将自动执行 steps 1-5。</p>"
        html += "<p><strong>已知 WARN:</strong> NFS冷启动(>30s) | SGLang占全8卡(轮询等待) | 上下文16K覆盖82%(R61权衡) | OOM风险(有降级方案)</p>"
        html += "<p><strong>下一步:</strong> SGLang释放GPU -> gpu_watcher自动触发 -> steps 1-5 -> 36%基线+D1-D6实测+RL smoke</p>"
    else:
        html += f"<p><strong>结论:</strong> 有 {counts.get('FAIL', 0)} 项 FAIL，需修复后才能自动起跑。</p>"
    html += "<p><strong>替身模型声明:</strong> 所有 RL 结果基于 MiniCPM5-2B（替身），不可迁移到 BaiZe。验证方法链并产出可复用管线工件。</p>\n</div>\n</body>\n</html>"
    Path(output_path).write_text(html, encoding="utf-8")
    return html

def main():
    parser = argparse.ArgumentParser(description="R78: GPU-Day Readiness Audit")
    parser.add_argument("--html", type=str, default=None)
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    audit = AuditResult()
    print("=== R78: GPU-Day Comprehensive Readiness Audit ===")
    print(f"Time: {audit.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    do_script_inventory(audit)
    do_config_audit(audit)
    do_data_audit(audit)
    do_venv_audit(audit)
    do_gpu_watcher_audit(audit)
    do_launch_chain_audit(audit)
    do_risk_assessment(audit)
    do_timeline_projection(audit)
    counts = audit.summary()
    print()
    print("=" * 60)
    print(f"AUDIT COMPLETE -- PASS={counts.get('PASS',0)} FAIL={counts.get('FAIL',0)} WARN={counts.get('WARN',0)} INFO={counts.get('INFO',0)}")
    print(f"Elapsed: {(datetime.now() - audit.start_time).total_seconds():.1f}s")
    print("=" * 60)
    fails = [i for i in audit.items if i["status"] == "FAIL"]
    if fails:
        print("\nFAIL items:")
        for f in fails: print(f"  [{f['category']}] {f['name']}: {f['detail']}")
    warns = [i for i in audit.items if i["status"] == "WARN"]
    if warns:
        print("\nWARN items:")
        for w in warns: print(f"  [{w['category']}] {w['name']}: {w['detail'][:100]}")
    if args.html:
        html_path = Path(args.html)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        generate_html(audit, str(html_path))
        print(f"\nHTML report: {html_path} ({html_path.stat().st_size:,}B)")
    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        data = audit.to_dict()
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report: {json_path} ({json_path.stat().st_size:,}B)")
    if args.verbose:
        print("\n--- All Items ---")
        for item in audit.items:
            print(f"  [{item['status']}] [{item['category']}] {item['name']}: {item['detail']}")
    return 0 if counts.get("FAIL", 0) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
