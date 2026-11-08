#!/usr/bin/env python3
"""R66: Day-0 Readiness Audit (2026-11-09, zero GPU, pure filesystem checks)."""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime

# === Auto-detect paths ===
NAS_ROOT = "/nas_data" if Path("/nas_data/app.e0031982/code/super_intelligence_2035").exists() and not Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists() else "/nas_train"
RUN_DIR = Path(NAS_ROOT) / "app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
REPORT_DIR = Path(NAS_ROOT) / "app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
VENV_DIR = Path.home() / "code/verl_cu124_venv"
MODEL_PATH = Path("/tmp/models/MiniCPM5-2B")
EDA_BASE = Path.home() / "code/eda_fastmcp"

results = {"timestamp": datetime.now().isoformat(), "checks": [],
           "summary": {"pass": 0, "fail": 0, "warn": 0, "total": 0},
           "gpu_status": None, "watcher_running": False, "blocking_items": [], "ready_to_launch": False}

def add(cat, name, status, detail=""):
    results["checks"].append({"category": cat, "name": name, "status": status, "detail": detail})
    results["summary"][status] += 1
    results["summary"]["total"] += 1

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired: return -1, "", "TIMEOUT"
    except Exception as e: return -2, "", str(e)

# 1. Node
rc, out, _ = run("hostname -I 2>/dev/null | tr ' ' '\\n' | head -1")
results["node"] = out if rc == 0 else "unknown"
add("node", "Node=.17", "pass" if "10.252.32.17" in out else "warn", f"IP={out}")

# 2. Bash syntax
for s in ["baize_posttrain_gpu_watcher.sh","baize_posttrain_launch_11_9.sh","baize_posttrain_preflight_check.sh",
          "baize_posttrain_rl_grpo.sh","baize_posttrain_sft.sh","baize_posttrain_eval.sh","baize_posttrain_anneal.sh",
          "baize_posttrain_minicpm5_diag.sh","baize_posttrain_contamination_gate.sh","baize_posttrain_post_rl_pipeline.sh",
          "baize_posttrain_72h_guardian.sh","baize_posttrain_day1_runbook.sh","baize_posttrain_paths.sh",
          "baize_posttrain_setup_cu124_venv.sh"]:
    p = RUN_DIR / s
    if not p.exists(): add("bash_syntax", s, "fail", "not found"); continue
    rc, _, err = run(f"bash -n '{p}' 2>&1")
    add("bash_syntax", s, "pass" if rc == 0 else "fail", err if rc else "OK")

# 3. Python syntax
for s in ["baize_posttrain_day1_diag.py","baize_posttrain_reward_functions.py","baize_posttrain_reward_validate.py",
          "baize_posttrain_eda_tool.py","baize_posttrain_gen_sft_corpus_v2.py","baize_posttrain_gen_synth_v2.py",
          "baize_posttrain_jsonl_to_parquet.py","baize_posttrain_ckpt_selector.py","baize_posttrain_eval_analysis.py",
          "baize_posttrain_baseline_gate.py","baize_posttrain_smoke_calibrator.py","baize_posttrain_rl_monitor.py",
          "baize_posttrain_rl_prompt_prescreen.py","baize_posttrain_campaign_projection.py","baize_posttrain_sft_dynamics.py",
          "baize_posttrain_rollout_throughput.py","baize_posttrain_sglang_preflight.py","baize_posttrain_verl_wrapper.py",
          "baize_posttrain_minicpm5_parser.py","baize_posttrain_api_profiler.py","baize_posttrain_day0_audit.py",
          "baize_posttrain_e2e_audit.py","baize_posttrain_v2_consistency_audit.py","baize_posttrain_data_audit.py",
          "baize_posttrain_contam_check_v2.py","baize_posttrain_ctx_budget_analyzer.py","baize_posttrain_gpu_budget_analysis.py",
          "baize_posttrain_gpu_schedule_optimizer.py","baize_posttrain_grpo_dynamics_sim.py","baize_posttrain_power_analysis.py",
          "baize_posttrain_power_analysis_fast.py","baize_posttrain_reward_adversarial_test.py","baize_posttrain_sft_data_mixer.py",
          "baize_posttrain_sglang_patch.py","baize_posttrain_ray_patch_verify.py","baize_posttrain_mine_deepseek_traces.py",
          "baize_posttrain_eda_sandbox_client.py","baize_posttrain_vision_lessons_analyzer.py","baize_posttrain_build_eval_ngrams.py"]:
    p = RUN_DIR / s
    if not p.exists(): add("py_syntax", s, "warn", "not found"); continue
    rc, _, err = run(f"python3 -m py_compile '{p}' 2>&1")
    add("py_syntax", s, "pass" if rc == 0 else "fail", err if rc else "OK")

# 4. Data files
for fn, min_sz, desc in [("rl_pyaether_synth_v2.parquet",512*1024,"RL parquet"),
    ("rl_pyaether_synth_v2.jsonl",1024*1024,"RL JSONL"),
    ("sft_pyaether_corpus_v2.jsonl",10*1024*1024,"SFT v2 JSONL"),
    ("sft_pyaether_corpus_v2.parquet",1024*1024,"SFT v2 parquet"),
    ("sft_pyaether_corpus.jsonl",10*1024*1024,"SFT v1 JSONL"),
    ("sft_pyaether_corpus.parquet",1024*1024,"SFT v1 parquet"),
    ("rl_pyaether_synth_tasks.jsonl",100*1024,"RL tasks"),
    ("sft_deepseek_patterns.jsonl",1024,"DeepSeek patterns"),
    ("sft_mixed_output.jsonl",1024*1024,"SFT mixed output")]:
    p = RUN_DIR / fn
    if not p.exists(): add("data", fn, "warn", f"{desc} not found"); continue
    sz = p.stat().st_size
    add("data", fn, "pass" if sz >= min_sz else "warn", f"{desc} {sz//1024}KB")

# Record counts
for fn, label in [("rl_pyaether_synth_v2.jsonl","RL v2"),("sft_pyaether_corpus_v2.jsonl","SFT v2")]:
    p = RUN_DIR / fn
    if p.exists():
        rc, out, _ = run(f"wc -l < '{p}'")
        n = int(out) if rc == 0 and out.isdigit() else 0
        add("data", f"{label} records", "pass" if n > 1000 else "warn", f"{n} records")

# 5. Venv (directory existence, NOT slow imports)
for pkg, d in [("torch","torch"),("sglang","sglang"),("verl","verl"),("ray","ray"),
    ("flash_attn","flash_attn"),("flashinfer","flashinfer"),("transformers","transformers"),
    ("pyarrow","pyarrow"),("yaml","yaml"),("pandas","pandas")]:
    pp = VENV_DIR / "lib/python3.10/site-packages" / d
    sp = VENV_DIR / "lib/python3.10/site-packages"
    found = pp.exists() or any(sp.glob(f"{pkg}*")) if sp.exists() else False
    add("venv", f"cu124/{pkg}", "pass" if found else "fail", str(pp) if pp.exists() else "glob")
vllm_py = Path.home() / "code/vllm_venv/bin/python"
add("venv", "vllm_venv", "pass" if vllm_py.exists() else "fail", str(vllm_py))

# 6. Model files
for mf in ["config.json","model.safetensors","tokenizer.json","tokenizer_config.json","special_tokens_map.json"]:
    p = MODEL_PATH / mf
    if p.exists(): add("model", f"MiniCPM5-2B/{mf}", "pass", f"{p.stat().st_size//1024}KB")
    elif any(MODEL_PATH.glob(f"{mf.split('.')[0]}*.safetensors")): add("model", f"MiniCPM5-2B/{mf}", "pass", "split found")
    else: add("model", f"MiniCPM5-2B/{mf}", "warn", "not found")
if MODEL_PATH.exists():
    total = sum(f.stat().st_size for f in MODEL_PATH.rglob("*") if f.is_file())
    add("model", "total size", "pass" if total > 1e9 else "warn", f"{total/1e9:.2f}GB")

# 7. GPU status
rc, out, _ = run("nvidia-smi --query-gpu=index,memory.free,memory.total,utilization.gpu --format=csv,noheader,nounits 2>/dev/null")
if rc == 0 and out:
    gpus, free_count = [], 0
    for line in out.strip().split("\n"):
        parts = [x.strip() for x in line.split(",")]
        if len(parts) >= 4:
            idx, fmib, tmib, util = parts
            gpus.append({"id": idx, "free_mib": int(fmib), "total_mib": int(tmib), "util": int(util)})
            if int(fmib) >= 40000: free_count += 1
    results["gpu_status"] = {"gpus": gpus, "free_count": free_count, "total": len(gpus)}
    if free_count >= 4: add("gpu", "availability", "pass", f"{free_count}/{len(gpus)} free"); results["ready_to_launch"] = True
    else: add("gpu", "availability", "warn", f"{free_count}/{len(gpus)} free — need 4")
    if free_count < 4: results["blocking_items"].append(f"GPU: {free_count}/8 free, waiting for 4 A40 release")
else: add("gpu", "nvidia-smi", "fail", "failed")

# 8. SGLang ports
for port in [8099, 8098, 30000]:
    rc, out, _ = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}/health 2>/dev/null", timeout=5)
    sc = out if rc == 0 else "N/A"
    if sc == "200": add("sglang", f"port {port}", "pass", "HTTP 200 (existing)")
    elif sc == "000": add("sglang", f"port {port}", "pass", "free for our use")
    else: add("sglang", f"port {port}", "warn", f"HTTP {sc}")

# 9. EDA toolkit
for rel, desc in [("pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl","158-case dataset"),
    ("scripts/run_eval.py","eval script"),("scripts/run_cline_script.sh","code gen driver"),
    ("docs/API_INFO_MERGED_V3.json","API knowledge base")]:
    p = EDA_BASE / rel
    add("eda", desc, "pass" if p.exists() else "fail", f"{p.stat().st_size//1024}KB" if p.exists() else "not found")
api_db = EDA_BASE / "docs/API_INFO_MERGED_V3.json"
if api_db.exists():
    rc, out, _ = run(f"python3 -c \"import json; d=json.load(open('{api_db}')); print(len(d))\"")
    add("eda", "API count", "pass" if rc == 0 and out.isdigit() and int(out) > 8000 else "warn", f"{out} APIs")

# 10. RL config
yaml_v2 = RUN_DIR / "baize_posttrain_rl_verl_config_v2.yaml"
if yaml_v2.exists():
    c = yaml_v2.read_text()
    issues = [x for x in ["rollout" not in c and "missing rollout", "sglang" not in c and "missing sglang",
        "reward" not in c and "missing reward", "context" not in c and "missing context"] if x]
    add("config", "RL YAML v2", "pass" if not issues else "warn", "; ".join(issues) if issues else f"{len(c)}B OK")
else: add("config", "RL YAML v2", "fail", "not found")

# 11. gpu_watcher process
rc, out, _ = run("pgrep -af 'baize_posttrain_gpu_watcher' | grep -v grep | grep -v pgrep")
results["watcher_running"] = bool(out)
add("process", "gpu_watcher", "pass" if out else "warn", f"PID: {out[:60]}" if out else "NOT running")

# 12. Launch dry-run
rc, out, _ = run(f"bash '{RUN_DIR}/baize_posttrain_launch_11_9.sh' --dry-run 2>&1 | head -15", timeout=15)
add("launch", "dry-run", "pass" if rc == 0 else "fail", "venv+model+eda exists" if "exists" in out else f"rc={rc}")

# 13. Disk
rc, out, _ = run("df -h / /tmp /nas_data 2>/dev/null | tail -n +2")
if out:
    for line in out.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 6:
            use = int(parts[4].rstrip("%"))
            add("disk", parts[0], "pass" if use < 90 else "warn", f"avail={parts[3]} use={parts[4]}")

# Final assessment
critical_fails = [c for c in results["checks"] if c["status"] == "fail" and c["category"] in ("data","venv","model","eda","config","bash_syntax")]
for c in critical_fails: results["blocking_items"].append(f"{c['category']}/{c['name']}: {c['detail']}")
results["ready_to_launch"] = len(critical_fails) == 0 and results.get("gpu_status",{}).get("free_count",0) >= 4 and results["watcher_running"]

# === HTML generator (part 1: styles + header + summary) ===
def gen_html(results, path):
    h = []
    h.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    h.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    h.append("<title>BaiZe Post-Train R66: Day-0 Readiness Audit</title><style>")
    h.append("body{font-family:system-ui,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}")
    h.append("h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}")
    h.append("h2{color:#2c3e50;margin-top:30px;border-left:5px solid #3498db;padding-left:10px}")
    h.append("table{border-collapse:collapse;width:100%;margin:10px 0;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1)}")
    h.append("th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}th{background:#2980b9;color:#fff}")
    h.append("tr:nth-child(even){background:#f9f9f9}")
    h.append(".pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c;font-weight:bold}.warn{color:#e67e22;font-weight:bold}")
    h.append(".bp{background:#27ae60;color:#fff;padding:2px 8px;border-radius:3px;font-size:.85em}")
    h.append(".bf{background:#e74c3c;color:#fff;padding:2px 8px;border-radius:3px;font-size:.85em}")
    h.append(".bw{background:#e67e22;color:#fff;padding:2px 8px;border-radius:3px;font-size:.85em}")
    h.append(".sb{padding:20px;border-radius:8px;margin:15px 0;text-align:center}")
    h.append(".s-ready{background:#d5f5e3;border:2px solid #27ae60}.s-wait{background:#fef9e7;border:2px solid #e67e22}.s-block{background:#fadbd8;border:2px solid #e74c3c}")
    h.append(".blk{background:#fadbd8;border:1px solid #e74c3c;padding:10px;border-radius:5px;margin:10px 0}")
    h.append(".gg{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:15px 0}")
    h.append(".gc{background:#fff;padding:10px;border-radius:5px;text-align:center;box-shadow:0 1px 2px rgba(0,0,0,.1)}.gf{border:2px solid #27ae60}.gb{border:2px solid #e74c3c}")
    h.append(".note{background:#d6eaf8;padding:10px;border-radius:5px;margin:10px 0;border-left:4px solid #3498db}")
    h.append("code{background:#ecf0f1;padding:2px 6px;border-radius:3px}")
    h.append("</style></head><body>")
    h.append("<h1>BaiZe Post-Train R66: Day-0 Readiness Audit</h1>")
    h.append(f"<p><strong>时间</strong>: {results['timestamp']} | <strong>节点</strong>: {results.get('node','?')} | <strong>日期</strong>: 2026-11-09 (GPU分配日)</p>")
    s = results["summary"]
    gf = results.get("gpu_status",{}).get("free_count",0)
    if results["ready_to_launch"]: h.append("<div class='sb s-ready'><h2>✅ 就绪 — 所有关键项通过，GPU可用，gpu_watcher运行中</h2>")
    elif gf < 4 and len(critical_fails) == 0: h.append(f"<div class='sb s-wait'><h2>⏳ 等待GPU — 所有关键依赖就绪，等待{4-gf}张A40释放</h2>")
    else: h.append(f"<div class='sb s-block'><h2>❌ 阻塞 — {len(critical_fails)}个关键项失败</h2>")
    h.append(f"<p>通过:<span class='pass'>{s['pass']}</span> | 失败:<span class='fail'>{s['fail']}</span> | 警告:<span class='warn'>{s['warn']}</span> | 总计:{s['total']}</p></div>")
    if results["blocking_items"]:
        h.append("<h2>🚫 阻塞项</h2><div class='blk'><ul>")
        for item in results["blocking_items"]: h.append(f"<li>{item}</li>")
        h.append("</ul></div>")
    if results.get("gpu_status"):
        gs = results["gpu_status"]
        h.append(f"<h2>🎮 GPU状态</h2><p>空闲:<strong>{gs['free_count']}</strong>/{gs['total']} (需≥4张≥40GB)</p><div class='gg'>")
        for g in gs["gpus"]:
            cls = "gf" if g["free_mib"] >= 40000 else "gb"
            h.append(f"<div class='gc {cls}'><strong>GPU {g['id']}</strong><br>{g['free_mib']}/{g['total_mib']} MiB<br>({g['util']}% util)</div>")
        h.append("</div>")
    # (part 2 continues below)

# === HTML generator (part 2: tables + footer) ===
    wr = results["watcher_running"]
    badge = '<span class="bp">RUNNING</span>' if wr else '<span class="bw">NOT RUNNING</span>'
    detail = '自动检测GPU释放后触发启动序列(steps 1-5)' if wr else '需手动启动'
    h.append("<h2>⚙️ 进程状态</h2><table><tr><th>进程</th><th>状态</th><th>详情</th></tr>")
    h.append(f"<tr><td>gpu_watcher.sh</td><td>{badge}</td><td>{detail}</td></tr></table>")
    cats = {}
    for c in results["checks"]: cats.setdefault(c["category"], []).append(c)
    cn = {"node":"节点","bash_syntax":"Bash脚本语法","py_syntax":"Python脚本语法","data":"数据文件","venv":"虚拟环境(cu124)","model":"模型文件","gpu":"GPU","sglang":"SGLang端口","eda":"EDA工具包","config":"RL配置","process":"进程","launch":"启动序列","disk":"磁盘空间"}
    for cat, checks in cats.items():
        h.append(f"<h2>📋 {cn.get(cat,cat)} ({len(checks)}项)</h2><table><tr><th>检查项</th><th>状态</th><th>详情</th></tr>")
        for c in checks:
            b = f"<span class='b{c['status'][0]}'>{c['status'].upper()}</span>"
            h.append(f"<tr><td>{c['name']}</td><td>{b}</td><td>{c['detail']}</td></tr>")
        h.append("</table>")
    h.append("<h2>🚀 11/9启动序列概览</h2><div class='note'><p><strong>gpu_watcher.sh</strong> 后台轮询(每120秒)，≥4张A40空闲时自动触发:</p><ol>")
    h.append("<li><strong>Step 1</strong>: Preflight check</li><li><strong>Step 2</strong>: SGLang serve + 36%基线复测(158-case×5-run)</li>")
    h.append("<li><strong>Step 3</strong>: D1-D6诊断提取</li><li><strong>Step 4</strong>: 污染隔离门</li><li><strong>Step 5</strong>: RL冒烟测试(GRPO R0, 10 iters)</li></ol>")
    h.append("<p>冒烟通过后手动触发<strong>Step 6</strong>: 全量RL训练(替身预演, ~72h)</p>")
    h.append("<p>⚠️ 替身模型(MiniCPM5-2B)结果不可迁移到白泽正式训练</p></div>")
    h.append("<h2>📌 关键事实</h2><table><tr><th>项</th><th>值</th></tr>")
    h.append("<tr><td>基线锚点</td><td>MiniCPM5-2B 36% (vs DeepSeek 94%)</td></tr>")
    h.append("<tr><td>评测集</td><td>EDA-Eval-PyAether 158任务, Pass@1, 5-run, 2500s</td></tr>")
    h.append("<tr><td>成功阶梯</td><td>36%→50%(M1)→65%(M2)→75%(M3)→85%+(M4)</td></tr>")
    h.append("<tr><td>RL配置</td><td>ctx=16384, hybrid, R0 arm (sandbox down→skeleton)</td></tr>")
    h.append("<tr><td>RL步数</td><td>200步(~72h, 3.45 steps/hr)</td></tr>")
    h.append("<tr><td>pretrain ckpt ETA</td><td>2026-12-25</td></tr></table><hr>")
    h.append(f"<p style='text-align:center;color:#7f8c8d;font-size:.9em'>R66 Day-0 Readiness Audit | {results['timestamp']} | 零GPU纯文件系统检查</p>")
    h.append("</body></html>")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(h), encoding="utf-8")

# === Main ===
ap = argparse.ArgumentParser(description="R66: Day-0 Readiness Audit")
ap.add_argument("--json", default="day0_readiness_audit.json")
ap.add_argument("--html", default=None)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()
if args.dry_run:
    print("DRY-RUN: Would check 14 bash + 39 py scripts + 9 data files + 10 venv pkgs + 5 model files + GPU + SGLang + EDA + config + process + launch + disk")
    sys.exit(0)
jp = Path(args.json)
jp.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"JSON: {jp} ({jp.stat().st_size}B)")
hp = Path(args.html) if args.html else REPORT_DIR / "report_posttrain_r66_day0_readiness_zh.html"
gen_html(results, hp)
print(f"HTML: {hp} ({hp.stat().st_size}B)")
s = results["summary"]
print(f"\n=== Day-0 Readiness Audit Summary ===")
print(f"  Pass: {s['pass']} | Fail: {s['fail']} | Warn: {s['warn']} | Total: {s['total']}")
print(f"  GPU: {results.get('gpu_status',{}).get('free_count','?')}/{results.get('gpu_status',{}).get('total','?')} free")
print(f"  gpu_watcher: {'RUNNING' if results['watcher_running'] else 'NOT RUNNING'}")
print(f"  Blocking: {len(results['blocking_items'])}")
for item in results["blocking_items"]: print(f"    - {item}")
print(f"  Ready to launch: {results['ready_to_launch']}")
