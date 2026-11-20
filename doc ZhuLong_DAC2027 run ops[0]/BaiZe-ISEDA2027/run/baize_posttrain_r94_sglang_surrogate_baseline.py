#!/usr/bin/env python3
"""
R94: SGLang Qwen3.8-27B Surrogate Code-Generation Baseline + GPU Day Readiness Audit

Context:
  - 2026-11-09: GPU Day. 4xA40 were supposed to be allocated to post-train.
  - Reality: All 8 A40s still occupied by root's SGLang Qwen3.8-27B (ports 8098+8099).
  - gpu_watcher (PID 2022305) is running, polling every 120s, will auto-trigger
    launch_11_9.sh when >=4 GPUs free up.
  - This script uses the EXISTING SGLang Qwen3.8-27B endpoint as a SURROGATE
    to validate the EDA-Eval code-generation pipeline end-to-end.

WARNING: Surrogate results (Qwen3.8-27B) are NOT transferable to BaiZe.
    BaiZe will use MiniCPM5-2B as base, not Qwen3.8-27B.

Usage:
  python3 baize_posttrain_r94_sglang_surrogate_baseline.py                    # Full run
  python3 baize_posttrain_r94_sglang_surrogate_baseline.py --smoke            # 3 tasks only
  python3 baize_posttrain_r94_sglang_surrogate_baseline.py --audit-only       # Skip API calls
  python3 baize_posttrain_r94_sglang_surrogate_baseline.py --html             # Generate HTML report
  python3 baize_posttrain_r94_sglang_surrogate_baseline.py --json             # Output JSON
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

# Constants
DEFAULT_ENDPOINT = "http://127.0.0.1:8099/v1"
DEFAULT_MODEL = "qwen3.8-27b"
DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_DIR = os.path.expanduser(
    "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
EXP_DIR = os.path.expanduser(
    "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
NAS_MODEL_PATH = "/nas_data/app.e0031982/models/MiniCPM5-2B"
TMP_MODEL_PATH = "/tmp/models/MiniCPM5-2B"
VERL_VENV = os.path.expanduser("~/code/verl_cu124_venv")
VLLM_VENV = os.path.expanduser("~/code/vllm_venv")
EDA_BASE = os.path.expanduser("~/code/eda_fastmcp")
GPU_WATCHER_LOG = "/nas_data/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/gpu_watcher_11_9.log"


def log(msg, verbose=False):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def read_jsonl(path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def call_sglang(endpoint, model, messages, max_tokens=2048, timeout=120):
    """Call SGLang OpenAI-compatible endpoint."""
    url = f"{endpoint}/chat/completions"
    payload = {
        "model": model, "messages": messages,
        "max_tokens": max_tokens, "temperature": 0.7, "top_p": 0.95,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return None, f"HTTP {e.code}: {body[:500]}"
    except Exception as e:
        return None, str(e)


def extract_code_from_response(text):
    """Extract Python code from model response."""
    matches = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    lines = text.split("\n")
    code_lines, in_func = [], False
    for line in lines:
        if line.strip().startswith(("def ", "import ")) or in_func:
            in_func = True
            code_lines.append(line)
        elif in_func and not line.strip():
            code_lines.append(line)
        elif in_func and not line.startswith((" ", "\t")) and line.strip():
            break
    return "\n".join(code_lines).strip() if code_lines else text.strip()


def check_syntax(code):
    try:
        compile(code, "<gen>", "exec")
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"


def extract_api_names(code):
    return sorted(set(re.findall(r"(?:pyScript|pyAether)\.(\w+)", code)))


def extract_api_names_from_prompt(prompt):
    return sorted(set(re.findall(r"(?:pyScript|pyAether)\.(\w+)", prompt)))


def analyze_code_quality(task, generated_code):
    prompt = task.get("prompt", "")
    metadata = task.get("metadata", {})
    expected_apis = metadata.get("apis_used", [])
    canonical = task.get("canonical_solution", "")
    entry_point = task.get("entry_point", "")

    syntax_ok, syntax_err = check_syntax(generated_code)
    gen_apis = extract_api_names(generated_code)
    prompt_apis = extract_api_names_from_prompt(prompt)
    gen_set, prompt_set = set(gen_apis), set(prompt_apis)
    matched, missing, extra = prompt_set & gen_set, prompt_set - gen_set, gen_set - prompt_set

    loc = len([l for l in generated_code.split("\n") if l.strip() and not l.strip().startswith("#")])
    canon_loc = len([l for l in canonical.split("\n") if l.strip()])

    return {
        "syntax_ok": syntax_ok, "syntax_error": syntax_err,
        "generated_apis": gen_apis, "prompt_apis": prompt_apis,
        "apis_matched": sorted(matched), "apis_missing": sorted(missing), "apis_extra": sorted(extra),
        "api_coverage": len(matched) / max(len(prompt_set), 1),
        "has_entry_point": f"def {entry_point}" in generated_code,
        "has_return": "return " in generated_code,
        "generated_loc": loc, "canonical_loc": canon_loc,
        "loc_ratio": loc / max(canon_loc, 1),
    }


def run_code_gen_baseline(tasks, endpoint, model, num_tasks=5, timeout=120):
    """Run code generation baseline on N tasks."""
    results = []
    log(f"Starting code-gen baseline: {num_tasks} tasks, model={model}")
    for i, task in enumerate(tasks[:num_tasks]):
        task_id = task.get("task_id", f"task_{i}")
        prompt = task.get("prompt", "")
        metadata = task.get("metadata", {})
        scenario = metadata.get("scenario", "?")
        category = metadata.get("category", "?")
        log(f"  [{i+1}/{num_tasks}] {task_id} ({scenario}/{category})")
        messages = [
            {"role": "system", "content": (
                "You are an expert EDA Python programmer. "
                "Complete the function according to the prompt. "
                "Only output the Python code, no explanations.")},
            {"role": "user", "content": prompt},
        ]
        t0 = time.time()
        response, error = call_sglang(endpoint, model, messages, max_tokens=2048, timeout=timeout)
        elapsed = time.time() - t0
        if error:
            log(f"    ERROR: {error[:100]}")
            results.append({"task_id": task_id, "scenario": scenario, "category": category,
                            "success": False, "error": error, "elapsed_s": round(elapsed, 1),
                            "generated_code": "", "analysis": None})
            continue
        choice = response.get("choices", [{}])[0]
        msg = choice.get("message", {})
        content = msg.get("content", "")
        usage = response.get("usage", {})
        generated_code = extract_code_from_response(content)
        analysis = analyze_code_quality(task, generated_code)
        log(f"    {'OK' if analysis['syntax_ok'] else 'FAIL'} syntax={analysis['syntax_ok']} "
            f"api_cov={analysis['api_coverage']:.0%} loc={analysis['generated_loc']}/{analysis['canonical_loc']} "
            f"elapsed={elapsed:.1f}s tokens={usage.get('completion_tokens', '?')}")
        results.append({
            "task_id": task_id, "scenario": scenario, "category": category,
            "success": True, "elapsed_s": round(elapsed, 1),
            "finish_reason": choice.get("finish_reason", "?"),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "reasoning_tokens": usage.get("reasoning_tokens", 0),
            "generated_code": generated_code, "raw_content_length": len(content),
            "analysis": analysis,
        })
    return results


def audit_gpu_status():
    """Audit GPU availability."""
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,memory.free,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"], timeout=10).decode("utf-8").strip()
    except Exception as e:
        return {"status": "error", "error": str(e), "free_gpus": 0}
    gpus, free_count = [], 0
    for line in output.split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4:
            idx, free_mib, total_mib, util = parts
            free_mib, total_mib = int(free_mib), int(total_mib)
            is_free = free_mib >= 40000
            if is_free:
                free_count += 1
            gpus.append({"id": int(idx), "free_mib": free_mib, "total_mib": total_mib,
                         "util_pct": int(util), "is_free": is_free})
    return {"status": "ok", "total_gpus": len(gpus), "free_gpus": free_count,
            "gpus": gpus, "sglang_occupying": sum(1 for g in gpus if not g["is_free"])}


def audit_sglang_endpoints():
    """Audit existing SGLang endpoints."""
    endpoints = []
    for port in [8098, 8099]:
        url = f"http://127.0.0.1:{port}/v1/models"
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("data", [])
                endpoints.append({"port": port, "status": "alive",
                    "model": models[0]["id"] if models else "?",
                    "max_model_len": models[0].get("max_model_len", "?") if models else "?",
                    "url": f"http://127.0.0.1:{port}/v1"})
        except Exception as e:
            endpoints.append({"port": port, "status": "down", "error": str(e)[:100]})
    return endpoints


def audit_prerequisites():
    """Audit all GPU Day prerequisites."""
    checks = []
    for path, label in [(NAS_MODEL_PATH, "NAS"), (TMP_MODEL_PATH, "/tmp")]:
        exists = os.path.isdir(path)
        has_w = os.path.isfile(os.path.join(path, "model-00000-of-00001.safetensors")) if exists else False
        checks.append({"item": f"MiniCPM5-2B model ({label})", "path": path,
            "status": "[OK]" if has_w else ("[WARN] dir only" if exists else "[FAIL] missing")})
    for vp, lb in [(VERL_VENV, "verl cu124"), (VLLM_VENV, "vllm")]:
        py = os.path.join(vp, "bin", "python")
        checks.append({"item": f"venv ({lb})", "path": vp,
            "status": "[OK]" if os.path.isfile(py) else "[FAIL] missing"})
    checks.append({"item": "EDA-Eval dataset (158 tasks)", "path": DATASET_PATH,
        "status": "[OK]" if os.path.isfile(DATASET_PATH) else "[FAIL] missing"})
    for s in ["run_cline_script.sh", "run_cline_cli.sh", "config.yaml"]:
        p = os.path.join(EDA_BASE, "pyAether-eval", s)
        checks.append({"item": f"Eval: {s}", "path": p,
            "status": "[OK]" if os.path.isfile(p) else "[FAIL] missing"})
    for s in ["baize_posttrain_launch_11_9.sh", "baize_posttrain_gpu_watcher.sh",
        "baize_posttrain_minicpm5_diag.sh", "baize_posttrain_rl_grpo.sh",
        "baize_posttrain_sft.sh", "baize_posttrain_eval.sh", "baize_posttrain_paths.sh",
        "baize_posttrain_contamination_gate.sh"]:
        p = os.path.join(EXP_DIR, s)
        ex = os.path.isfile(p)
        syn = False
        if ex:
            try:
                subprocess.run(["bash", "-n", p], check=True, timeout=5, capture_output=True)
                syn = True
            except Exception:
                pass
        checks.append({"item": f"Script: {s}", "path": p,
            "status": "[OK]" if ex and syn else ("[WARN] syntax" if ex else "[FAIL] missing")})
    # DeepSeek traces
    trace_dir = os.path.join(EDA_BASE, "pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace")
    tc = len(os.listdir(trace_dir)) if os.path.isdir(trace_dir) else 0
    checks.append({"item": "DeepSeek traces", "path": trace_dir,
        "status": f"[OK] ({tc} traces)" if tc > 0 else "[FAIL] missing"})
    # pyAether
    pya_found = False
    for pc in ["python3", os.path.join(EDA_BASE, ".venv/bin/python3")]:
        try:
            r = subprocess.run([pc, "-c", "import pyAether"], capture_output=True, timeout=5)
            if r.returncode == 0:
                pya_found = True
                break
        except Exception:
            pass
    checks.append({"item": "pyAether library", "status": "[OK]" if pya_found else "[FAIL] not installed"})
    # MCP server
    mcp_ok = False
    try:
        with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8090/health"), timeout=3) as r:
            mcp_ok = r.status == 200
    except Exception:
        pass
    checks.append({"item": "pyAether MCP server (port 8090)",
        "status": "[OK] running" if mcp_ok else "[FAIL] not running (port 8090=MRT tool)"})
    # gpu_watcher
    wr = False
    try:
        r = subprocess.run(["pgrep", "-f", "gpu_watcher"], capture_output=True, timeout=5)
        wr = r.returncode == 0
    except Exception:
        pass
    checks.append({"item": "gpu_watcher", "status": "[OK] running" if wr else "[FAIL] not running"})
    # Disk
    try:
        st = os.statvfs("/nas_data")
        fg = (st.f_bavail * st.f_frsize) / (1024**3)
        checks.append({"item": "Disk space (/nas_data)",
            "status": f"[OK] {fg:.0f}GB free" if fg > 100 else f"[WARN] {fg:.0f}GB"})
    except Exception:
        checks.append({"item": "Disk space", "status": "[FAIL]"})
    return checks


def compute_summary(cg_results, audit_checks, gpu_status, sglang_eps):
    total = len(cg_results)
    succ = sum(1 for r in cg_results if r.get("success"))
    syn_ok = sum(1 for r in cg_results if r.get("analysis") and r["analysis"]["syntax_ok"])
    avg_cov = 0
    if succ > 0:
        covs = [r["analysis"]["api_coverage"] for r in cg_results if r.get("analysis")]
        avg_cov = sum(covs) / len(covs) if covs else 0
    avg_t = 0
    if succ > 0:
        ts = [r["elapsed_s"] for r in cg_results if r.get("success")]
        avg_t = sum(ts) / len(ts) if ts else 0
    a_ok = sum(1 for c in audit_checks if "[OK]" in c.get("status", ""))
    a_wn = sum(1 for c in audit_checks if "[WARN]" in c.get("status", ""))
    a_fl = sum(1 for c in audit_checks if "[FAIL]" in c.get("status", ""))
    blk = [c["item"] for c in audit_checks if "[FAIL]" in c.get("status", "")]
    gpu_blk = gpu_status.get("free_gpus", 0) < 4
    return {
        "codegen": {"total": total, "success": succ, "syntax_valid": syn_ok,
            "syntax_rate": round(syn_ok / max(total, 1), 4),
            "avg_api_coverage": round(avg_cov, 4), "avg_elapsed_s": round(avg_t, 1)},
        "audit": {"total": len(audit_checks), "ok": a_ok, "warn": a_wn, "fail": a_fl,
            "blocking": blk},
        "gpu": gpu_status, "sglang": sglang_eps,
        "gpu_day_ready": not gpu_blk and len(blk) == 0,
        "gpu_blocked_by": "GPU not free" if gpu_blk else None,
    }


def generate_html(summary, cg_results, audit_checks, output_path):
    """Generate self-contained HTML report."""
    gf = summary["gpu"].get("free_gpus", 0)
    sa = sum(1 for e in summary["sglang"] if e["status"] == "alive")
    cg = summary["codegen"]
    h = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R94: SGLang Qwen3.8-27B 替身基线 + GPU Day 审计</title>
<style>
body {{ font-family: sans-serif; margin: 2rem; background: #f5f5f5; color: #333; max-width: 1200px; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: .5rem; }}
h2 {{ color: #2c3e50; margin-top: 2rem; border-left: 4px solid #3498db; padding-left: .5rem; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; background: white; }}
th, td {{ border: 1px solid #ddd; padding: .5rem; text-align: left; font-size: .9rem; }}
th {{ background: #2c3e50; color: white; }}
.ok {{ color: #27ae60; font-weight: bold; }}
.fail {{ color: #e74c3c; font-weight: bold; }}
.warn {{ color: #e67e22; font-weight: bold; }}
pre {{ background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 5px; overflow-x: auto; }}
.warning {{ background: #fdedec; border-left: 4px solid #e74c3c; padding: .5rem 1rem; margin: 1rem 0; }}
.note {{ background: #fef9e7; border-left: 4px solid #f39c12; padding: .5rem 1rem; margin: 1rem 0; }}
.box {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
.card {{ background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); min-width: 130px; }}
.card h3 {{ margin: 0 0 .5rem; font-size: .8rem; color: #7f8c8d; }}
.card .v {{ font-size: 1.5rem; font-weight: bold; }}
</style></head><body>
<h1>R94: SGLang Qwen3.8-27B 替身基线 + GPU Day 审计</h1>
<p>2026-11-09 | 10.252.32.17 | GPU Day (4xA40 未释放)</p>
<div class="warning"><b>替身声明</b>: Qwen3.8-27B 结果<b>不可迁移到 BaiZe</b>。仅验证管线可用性。</div>
<h2>1. 摘要</h2>
<div class="box">
<div class="card"><h3>GPU 空闲</h3><div class="v">{gf}/8</div></div>
<div class="card"><h3>SGLang</h3><div class="v">{sa}/2</div></div>
<div class="card"><h3>就绪</h3><div class="v">{summary['audit']['ok']}/{summary['audit']['total']}</div></div>
<div class="card"><h3>阻塞</h3><div class="v fail">{len(summary['audit']['blocking'])}</div></div>
<div class="card"><h3>可启动</h3><div class="v">{'YES' if summary['gpu_day_ready'] else 'NO'}</div></div>
</div>
<h2>2. GPU 现状</h2><table><tr><th>GPU</th><th>空闲</th><th>总</th><th>利用率</th><th>状态</th></tr>
"""
    for g in summary["gpu"].get("gpus", []):
        cls = "ok" if g["is_free"] else "fail"
        h += f'<tr><td>GPU {g["id"]}</td><td>{g["free_mib"]}MiB</td><td>{g["total_mib"]}MiB</td><td>{g["util_pct"]}%</td><td class="{cls}">{"空闲" if g["is_free"] else "占用"}</td></tr>\n'
    h += "</table>\n"
    return _html_part2(h, summary, cg_results, audit_checks, cg, output_path)


def _html_part2(h, summary, cg_results, audit_checks, cg, output_path):
    h += "<h2>3. SGLang 端点</h2><table><tr><th>端口</th><th>状态</th><th>模型</th></tr>\n"
    for e in summary["sglang"]:
        cls = "ok" if e["status"] == "alive" else "fail"
        h += f'<tr><td>{e["port"]}</td><td class="{cls}">{e["status"]}</td><td>{e.get("model","—")}</td></tr>\n'
    h += "</table>\n"
    if cg_results:
        h += f"""<h2>4. 替身代码生成基线</h2>
<div class="box">
<div class="card"><h3>任务</h3><div class="v">{cg['total']}</div></div>
<div class="card"><h3>API OK</h3><div class="v">{cg['success']}/{cg['total']}</div></div>
<div class="card"><h3>语法率</h3><div class="v">{cg['syntax_rate']:.0%}</div></div>
<div class="card"><h3>API 覆盖</h3><div class="v">{cg['avg_api_coverage']:.0%}</div></div>
</div>
<table><tr><th>Task</th><th>场景</th><th>语法</th><th>API覆盖</th><th>LOC</th><th>耗时</th><th>Tokens</th></tr>
"""
        for r in cg_results:
            if r.get("analysis"):
                a = r["analysis"]
                sc = "ok" if a["syntax_ok"] else "fail"
                h += f'<tr><td>{r["task_id"]}</td><td>{r["scenario"]}</td><td class="{sc}">{"OK" if a["syntax_ok"] else "FAIL"}</td><td>{a["api_coverage"]:.0%}</td><td>{a["generated_loc"]}/{a["canonical_loc"]}</td><td>{r["elapsed_s"]}s</td><td>{r.get("completion_tokens",0)}</td></tr>\n'
            else:
                h += f'<tr><td>{r["task_id"]}</td><td>{r.get("scenario","")}</td><td class="fail">ERR</td><td>—</td><td>—</td><td>{r.get("elapsed_s",0)}s</td><td>—</td></tr>\n'
        h += "</table>\n"
        if cg_results and cg_results[0].get("generated_code"):
            h += f'<h3>4.1 代码示例</h3><pre>{cg_results[0]["generated_code"][:1200]}</pre>\n'
        h += f"""<div class="note"><b>解读</b>: Qwen3.8-27B 纯代码生成语法率 {cg['syntax_rate']:.0%}, API覆盖 {cg['avg_api_coverage']:.0%}。
非 full harness 口径。Full harness 需 MCP server。</div>\n"""
    else:
        h += "<h2>4. 替身代码生成</h2><p>(audit-only)</p>\n"
    return _html_part3(h, summary, audit_checks, output_path)


def _html_part3(h, summary, audit_checks, output_path):
    h += '<h2>5. GPU Day 就绪审计</h2><table><tr><th>检查项</th><th>路径</th><th>状态</th></tr>\n'
    for c in audit_checks:
        st = c.get("status", "—")
        cls = "ok" if "[OK]" in st else ("warn" if "[WARN]" in st else "fail")
        h += f'<tr><td>{c["item"]}</td><td><code>{c.get("path","")}</code></td><td class="{cls}">{st}</td></tr>\n'
    h += """</table>
<h2>6. 阻塞项与修复</h2>
<table><tr><th>阻塞</th><th>影响</th><th>修复</th></tr>
<tr><td class="fail">GPU 0/8</td><td>无法服务 MiniCPM5-2B</td><td>需 root 释放>=4卡</td></tr>
<tr><td class="fail">pyAether 未装</td><td>无法执行测试</td><td>启动 MCP server</td></tr>
<tr><td class="fail">MCP 未运行</td><td>cline 无法用工具</td><td>端口8090被MRT占,换端口</td></tr>
</table>
<h2>7. GPU 释放后执行序列</h2>
<pre>
GPU释放 -> gpu_watcher检测 -> NFS warm-up
Step0: 验证cu124 venv | Step1: Preflight
Step2: SGLang serve MiniCPM5-2B -> 复测36%(5-run)
Step3: 提取D1-D6(R93管线) | Step4: 污染隔离
Step5: RL smoke(GRPO R0,10iters) | Step6: Full RL
</pre>
<h2>8. 结论</h2>
<ol>
<li>GPU 11/9既定到位但未释放, root SGLang占全8卡, gpu_watcher轮询中</li>
<li>现有SGLang Qwen3.8-27B可作替身推理后端, 不能用于verl RL</li>
<li>Qwen3.8-27B纯代码生成提供"强模型无工具"参考点</li>
<li>三阻塞: GPU+pyAether+MCP. GPU需root, 其余可并行处理</li>
<li>管线除3项外全部就绪, GPU释放后~30min可起Step2</li>
</ol>
<p style="color:#7f8c8d;font-size:.8rem;">R94 | 2026-11-09 | BaiZe Post-Train</p>
</body></html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(h)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="R94: SGLang surrogate baseline + GPU Day audit")
    parser.add_argument("--smoke", action="store_true", help="3 tasks only")
    parser.add_argument("--audit-only", action="store_true", help="Skip API calls")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--num-tasks", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    num_tasks = 3 if args.smoke else args.num_tasks

    log("=" * 60)
    log("R94: SGLang Qwen3.8-27B Surrogate Baseline + GPU Day Audit")
    log(f"Endpoint: {args.endpoint} | Model: {args.model} | Tasks: {num_tasks}")
    log("=" * 60)

    log("Step 1: GPU audit...")
    gpu_status = audit_gpu_status()
    log(f"  Free: {gpu_status.get('free_gpus',0)}/{gpu_status.get('total_gpus',0)}")

    log("Step 2: SGLang audit...")
    sglang_eps = audit_sglang_endpoints()
    for e in sglang_eps:
        log(f"  Port {e['port']}: {e['status']}")

    log("Step 3: Prerequisites audit...")
    audit_checks = audit_prerequisites()
    for c in audit_checks:
        log(f"  {c['status']} {c['item']}")

    cg_results = []
    if not args.audit_only:
        log("Step 4: Code generation baseline...")
        if os.path.isfile(DATASET_PATH):
            tasks = read_jsonl(DATASET_PATH)
            log(f"  Loaded {len(tasks)} tasks")
            cg_results = run_code_gen_baseline(tasks, args.endpoint, args.model, num_tasks, args.timeout)
        else:
            log(f"  Dataset not found: {DATASET_PATH}")

    log("Step 5: Summary...")
    summary = compute_summary(cg_results, audit_checks, gpu_status, sglang_eps)
    log(f"\nGPU: {summary['gpu'].get('free_gpus',0)}/8 free")
    log(f"SGLang: {sum(1 for e in summary['sglang'] if e['status']=='alive')}/2 alive")
    log(f"Audit: {summary['audit']['ok']}OK {summary['audit']['warn']}WARN {summary['audit']['fail']}FAIL")
    if cg_results:
        log(f"Code-gen: syntax={summary['codegen']['syntax_rate']:.0%} api_cov={summary['codegen']['avg_api_coverage']:.0%}")
    log(f"GPU Day ready: {'YES' if summary['gpu_day_ready'] else 'NO'}")
    if summary["audit"]["blocking"]:
        log(f"Blocking: {', '.join(summary['audit']['blocking'])}")

    if args.json:
        out = {"r94": "sglang_surrogate", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
               "summary": summary, "codegen": cg_results, "audit": audit_checks}
        jp = os.path.join(EXP_DIR, "r94_surrogate_baseline.json")
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        log(f"JSON: {jp}")

    if args.html:
        hp = os.path.join(REPORT_DIR, "report_posttrain_r94_sglang_surrogate_zh.html")
        os.makedirs(REPORT_DIR, exist_ok=True)
        generate_html(summary, cg_results, audit_checks, hp)
        log(f"HTML: {hp}")

    print("\n--- BLOCKING ---")
    if summary.get("gpu_blocked_by"):
        print(f"1. {summary['gpu_blocked_by']}")
    for item in summary["audit"]["blocking"]:
        print(f"- {item}")
    print("--- END ---")
    return 0 if summary["gpu_day_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
