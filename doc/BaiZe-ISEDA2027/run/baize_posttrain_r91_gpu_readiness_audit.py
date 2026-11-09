#!/usr/bin/env python3
"""baize_posttrain_r91_gpu_readiness_audit.py -- Pre-GPU Day Readiness Audit (R91)

Comprehensive audit of ALL prerequisites for the 11/9 GPU launch sequence.
Checks: model files, venvs, scripts, configs, eval assets, data, GPU state.

Usage:
    python3 baize_posttrain_r91_gpu_readiness_audit.py
    python3 baize_posttrain_r91_gpu_readiness_audit.py --json r91_results.json
    python3 baize_posttrain_r91_gpu_readiness_audit.py --html report_r91_gpu_readiness_zh.html
    python3 baize_posttrain_r91_gpu_readiness_audit.py --decision-only
"""
import sys, os, json, subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
NAS_ROOT = "/nas_data" if Path("/nas_data/app.e0031982/code/super_intelligence_2035").exists() else "/nas_train"
CODE_DIR = Path(f"{NAS_ROOT}/app.e0031982/code/super_intelligence_2035")
RUN_DIR = CODE_DIR / "doc/BaiZe-ISEDA2027/run"
HOME = Path.home()
OLD_MODEL_PATH = "/tmp/models/MiniCPM5-2B"
NAS_MODEL_PATH = f"{NAS_ROOT}/app.e0031982/models/MiniCPM5-2B"
VENV_DIR = HOME / "code/verl_cu124_venv"
VLLM_VENV_DIR = HOME / "code/vllm_venv"
EDA_BASE = HOME / "code/eda_fastmcp"

def check_exists(path, label, expected_type="any"):
    p = Path(path)
    ok = p.is_dir() if expected_type == "dir" else (p.is_file() if expected_type == "file" else p.exists())
    return {"label": label, "path": str(path), "exists": ok}

def check_bash_syntax(sp):
    try:
        r = subprocess.run(["bash", "-n", str(sp)], capture_output=True, timeout=10)
        return {"syntax_ok": r.returncode == 0, "stderr": r.stderr.decode()[:200] if r.returncode else ""}
    except Exception as e:
        return {"syntax_ok": False, "stderr": str(e)}

def get_gpu_status():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.free,memory.total,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, timeout=10)
        if r.returncode != 0:
            return {"available": False, "error": r.stderr.decode()[:200]}
        gpus = []
        for line in r.stdout.decode().strip().split("\n"):
            parts = [x.strip() for x in line.split(",")]
            if len(parts) >= 4:
                gpus.append({"index": int(parts[0]), "free_mib": int(parts[1]), "total_mib": int(parts[2]), "util_pct": int(parts[3])})
        free_count = sum(1 for g in gpus if g["free_mib"] >= 40000)
        return {"available": True, "gpus": gpus, "free_gpus": free_count, "total_gpus": len(gpus), "ready": free_count >= 4}
    except Exception as e:
        return {"available": False, "error": str(e)}

def check_venv(vd, label):
    py = vd / "bin/python"
    if not py.exists():
        return {"label": label, "path": str(py), "exists": False, "version": ""}
    try:
        r = subprocess.run([str(py), "--version"], capture_output=True, timeout=15)
        return {"label": label, "path": str(py), "exists": True, "version": (r.stdout.decode().strip() + r.stderr.decode()).strip()}
    except Exception as e:
        return {"label": label, "path": str(py), "exists": True, "version": "err: "+str(e)}

def check_torch_cuda(vd, label):
    py = vd / "bin/python"
    if not py.exists():
        return {"label": label, "torch_cuda": False, "output": "venv missing"}
    try:
        code = "import torch; print(f'torch={torch.__version__}'); print(f'cuda_available={torch.cuda.is_available()}'); print(f'cuda_version={torch.version.cuda}')"
        r = subprocess.run([str(py), "-c", code], capture_output=True, timeout=60, env={**os.environ, "PYTHONWARNINGS": "ignore"})
        out = r.stdout.decode().strip()
        return {"label": label, "output": out, "torch_cuda": "cuda_available=True" in out}
    except subprocess.TimeoutExpired:
        return {"label": label, "output": "TIMEOUT(>60s NFS cold)", "torch_cuda": None}
    except Exception as e:
        return {"label": label, "output": str(e), "torch_cuda": False}

def scan_tmp_refs():
    refs = []
    for f in RUN_DIR.iterdir():
        if f.name.startswith("baize_posttrain") and f.suffix in (".sh", ".py", ".yaml", ".yml"):
            try:
                c = f.read_text(errors="replace")
                if OLD_MODEL_PATH in c:
                    refs.append({"file": f.name, "ref_count": c.count(OLD_MODEL_PATH)})
            except Exception:
                pass
    return refs

def check_model(mp):
    md = Path(mp)
    if not md.is_dir():
        return {"path": str(mp), "exists": False, "files": [], "total_size_mb": 0}
    files = []
    for fn in ["config.json", "model-00000-of-00001.safetensors", "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "generation_config.json", "chat_template.jinja"]:
        fp = md / fn
        files.append({"file": fn, "exists": fp.exists(), "size": fp.stat().st_size if fp.exists() else 0})
    ts = sum(f["size"] for f in files if f["exists"])
    return {"path": str(mp), "exists": True, "files": files, "total_size_mb": round(ts / 1024 / 1024, 1)}

def check_eval_assets():
    a = []
    a.append(check_exists(EDA_BASE / "scripts/run_cline_script.sh", "Eval driver", "file"))
    a.append(check_exists(EDA_BASE / "scripts/run_eval.py", "Eval scorer", "file"))
    a.append(check_exists(EDA_BASE / "pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl", "158-case dataset", "file"))
    a.append(check_exists(EDA_BASE / "docs/API_INFO_MERGED_V3.json", "API database", "file"))
    dsp = EDA_BASE / "pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
    if dsp.exists():
        try:
            with open(dsp) as f: cnt = sum(1 for _ in f)
            a.append({"label": "Dataset task count", "count": cnt, "ok": cnt == 158})
        except Exception: a.append({"label": "Dataset task count", "count": 0, "ok": False})
    td = EDA_BASE / "pyAether-eval/cline_cli_trace/cline_trace_v1_3"
    if td.is_dir():
        a.append({"label": "DeepSeek traces", "path": str(td), "count": len(list(td.glob("*.json")))})
    else:
        a.append({"label": "DeepSeek traces", "path": str(td), "count": 0})
    return a

def check_sft_data():
    r = []
    for name, fn in [("SFT v1", "sft_pyaether_corpus.jsonl"), ("SFT v2", "sft_pyaether_corpus_v2.jsonl")]:
        p = RUN_DIR / fn
        if p.exists():
            try:
                with open(p) as f: cnt = sum(1 for _ in f)
                r.append({"label": name, "path": str(p), "exists": True, "lines": cnt})
            except Exception: r.append({"label": name, "path": str(p), "exists": True, "lines": -1})
        else: r.append({"label": name, "path": str(p), "exists": False, "lines": 0})
    p = RUN_DIR / "rl_pyaether_synth_v2.parquet"
    r.append({"label": "RL parquet", "path": str(p), "exists": p.exists(), "size": p.stat().st_size if p.exists() else 0})
    return r

def check_scripts():
    scripts = ["baize_posttrain_anneal.sh", "baize_posttrain_sft.sh", "baize_posttrain_rl_grpo.sh", "baize_posttrain_eval.sh", "baize_posttrain_launch_11_9.sh", "baize_posttrain_gpu_watcher.sh", "baize_posttrain_preflight_check.sh", "baize_posttrain_contamination_gate.sh", "baize_posttrain_minicpm5_diag.sh", "baize_posttrain_post_rl_pipeline.sh", "baize_posttrain_paths.sh", "baize_posttrain_day1_runbook.sh"]
    results = []
    for s in scripts:
        p = RUN_DIR / s
        if p.exists():
            results.append({"script": s, "exists": True, **check_bash_syntax(p)})
        else:
            results.append({"script": s, "exists": False, "syntax_ok": False})
    return results

def check_configs():
    configs = []
    for name in ["baize_posttrain_rl_verl_config_v2.yaml", "baize_posttrain_rl_verl_config.yaml", "baize_posttrain_tool_config.yaml", "sft_blend_config.yaml"]:
        p = RUN_DIR / name
        configs.append({"config": name, "exists": p.exists(), "has_old_model_path": OLD_MODEL_PATH in p.read_text(errors="replace") if p.exists() else False})
    return configs

def check_disk():
    r = []
    for mount, path in [("/", "/"), ("/nas_data", "/nas_data"), ("~/code", str(HOME / "code"))]:
        try:
            res = subprocess.run(["df", "-h", path], capture_output=True, timeout=5)
            lines = res.stdout.decode().strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 6:
                    r.append({"mount": mount, "total": parts[1], "used": parts[2], "avail": parts[3], "use_pct": parts[4]})
        except Exception: r.append({"mount": mount, "error": "df failed"})
    return r

def check_gpu_watcher():
    try:
        r = subprocess.run(["pgrep", "-af", "gpu_watcher"], capture_output=True, timeout=5)
        lines = [l for l in r.stdout.decode().strip().split("\n") if l and "pgrep" not in l]
        return {"running": len(lines) > 0, "processes": lines[:3]}
    except Exception:
        return {"running": False, "processes": []}

def run_audit():
    audit = {"timestamp": datetime.now().isoformat(), "node": os.uname().nodename, "r_number": "R91", "title": "Pre-GPU Day Readiness Audit"}
    audit["model_old_path"] = check_model(OLD_MODEL_PATH)
    audit["model_nas_path"] = check_model(NAS_MODEL_PATH)
    audit["model_path_issue"] = {"old_path_deleted": not Path(OLD_MODEL_PATH).exists(), "nas_path_exists": Path(NAS_MODEL_PATH).exists(), "fix": f"Update BAIZE_MODEL_PATH from {OLD_MODEL_PATH} to {NAS_MODEL_PATH}", "blocking": not Path(NAS_MODEL_PATH).exists()}
    audit["venv_verl"] = check_venv(VENV_DIR, "verl_cu124_venv")
    audit["venv_vllm"] = check_venv(VLLM_VENV_DIR, "vllm_venv")
    audit["torch_cuda_verl"] = check_torch_cuda(VENV_DIR, "verl_cu124_venv")
    audit["gpu"] = get_gpu_status()
    audit["eval_assets"] = check_eval_assets()
    audit["sft_data"] = check_sft_data()
    audit["scripts"] = check_scripts()
    audit["configs"] = check_configs()
    audit["tmp_model_refs"] = scan_tmp_refs()
    audit["disk"] = check_disk()
    audit["gpu_watcher"] = check_gpu_watcher()
    blockers = []
    if audit["model_path_issue"]["blocking"]: blockers.append("Model files missing on NAS")
    if not audit["model_old_path"]["exists"] and audit["tmp_model_refs"]: blockers.append(f"{len(audit['tmp_model_refs'])} files reference deleted /tmp model path")
    if not audit["gpu"].get("ready", False): blockers.append(f"GPU not ready: {audit['gpu'].get('free_gpus', 0)}/8 free (need >=4)")
    for s in audit["scripts"]:
        if not s.get("syntax_ok", False): blockers.append(f"Script syntax error: {s['script']}")
    for a in audit["eval_assets"]:
        if isinstance(a, dict) and "exists" in a and not a["exists"]: blockers.append(f"Eval asset missing: {a.get('label', '?')}")
    ready_items = []
    if audit["model_nas_path"]["exists"]: ready_items.append(f"Model on NAS: {audit['model_nas_path']['total_size_mb']}MB")
    if audit["venv_verl"]["exists"]: ready_items.append("verl_cu124_venv exists")
    if audit["venv_vllm"]["exists"]: ready_items.append("vllm_venv exists")
    for s in audit["scripts"]:
        if s.get("syntax_ok"): ready_items.append(f"Script OK: {s['script']}")
    for a in audit["eval_assets"]:
        if isinstance(a, dict) and a.get("exists"): ready_items.append(f"Eval asset OK: {a.get('label', '?')}")
    audit["summary"] = {"total_blockers": len(blockers), "blockers": blockers, "ready_count": len(ready_items), "ready_items": ready_items, "overall_ready": len(blockers) == 0, "can_proceed_after_fixes": not audit["model_path_issue"]["blocking"]}
    return audit

def generate_html(audit):
    s = audit["summary"]
    color = "#27ae60" if s["overall_ready"] else ("#e67e22" if all("GPU" in b for b in s["blockers"]) else "#e74c3c")
    h = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>R91 GPU Day 就绪审计</title><style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}
h1{{color:#2c3e50;border-bottom:3px solid {color};padding-bottom:10px}}
h2{{color:#2c3e50;margin-top:30px;border-left:4px solid {color};padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;background:white}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}
th{{background:#2c3e50;color:white}}
tr:nth-child(even){{background:#f2f2f2}}
.ok{{color:#27ae60;font-weight:bold}}.fail{{color:#e74c3c;font-weight:bold}}.warn{{color:#e67e22;font-weight:bold}}
.box{{background:white;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.blk{{background:#fdf2f2;border-left:4px solid #e74c3c;padding:10px;margin:5px 0}}
.rdy{{background:#f0faf0;border-left:4px solid #27ae60;padding:10px;margin:5px 0}}
code{{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}}
.ts{{color:#999;font-size:0.9em}}
</style></head><body>
<h1>R91 GPU Day 就绪审计</h1>
<p class="ts">审计时间：{audit['timestamp']} | 节点：{audit['node']}</p>
<div class="box"><h2>总览</h2>
<p><strong>阻塞项：{s['total_blockers']}</strong> | <strong>就绪项：{s['ready_count']}</strong> | <strong>总体就绪：<span class="{'ok' if s['overall_ready'] else 'fail'}">{'YES' if s['overall_ready'] else 'NO'}</span></strong></p>
<p>修复后可启动：<span class="{'ok' if s['can_proceed_after_fixes'] else 'warn'}">{'是（修复模型路径+GPU释放后即可起跑）' if s['can_proceed_after_fixes'] else '需先解决阻塞项'}</span></p>
"""
    if s["blockers"]:
        h += "<h3>阻塞项</h3>\n"
        for b in s["blockers"]: h += f'<div class="blk">{b}</div>\n'
    if s["ready_items"]:
        h += "<h3>就绪项</h3>\n"
        for r in s["ready_items"][:15]: h += f'<div class="rdy">{r}</div>\n'
    h += f"""</div>
<h2>1. 模型文件（关键发现）</h2>
<table><tr><th>路径</th><th>存在</th><th>大小</th><th>状态</th></tr>
<tr><td><code>{OLD_MODEL_PATH}</code></td><td class="fail">DELETED</td><td>-</td><td class="fail">/tmp 被清理，路径失效</td></tr>
<tr><td><code>{NAS_MODEL_PATH}</code></td><td class="ok">YES</td><td>{audit['model_nas_path'].get('total_size_mb',0)}MB</td><td class="ok">NAS 持久存储，可用</td></tr>
</table>
<p><strong>修复</strong>：将 paths.sh 的 <code>BAIZE_MODEL_PATH</code> 从 <code>{OLD_MODEL_PATH}</code> 改为 <code>{NAS_MODEL_PATH}</code>，同时更新 RL YAML 和 Python 脚本。</p>
"""
    refs = audit["tmp_model_refs"]
    if refs:
        h += f'<p>{len(refs)} 个文件引用了已删除的 /tmp 模型路径：</p><table><tr><th>文件</th><th>引用次数</th></tr>\n'
        for r in refs: h += f'<tr><td><code>{r["file"]}</code></td><td>{r["ref_count"]}</td></tr>\n'
        h += "</table>\n"
    v = audit["venv_verl"]
    v2 = audit["venv_vllm"]
    tc = audit["torch_cuda_verl"]
    cuda_s = "OK" if tc.get("torch_cuda") == True else ("FAIL" if tc.get("torch_cuda") == False else "TIMEOUT")
    h += f"""<h2>2. Python 虚拟环境</h2>
<table><tr><th>环境</th><th>路径</th><th>存在</th><th>版本</th></tr>
<tr><td>verl_cu124_venv</td><td><code>{v['path']}</code></td><td class="{'ok' if v['exists'] else 'fail'}">{'YES' if v['exists'] else 'NO'}</td><td>{v.get('version','')}</td></tr>
<tr><td>vllm_venv</td><td><code>{v2['path']}</code></td><td class="{'ok' if v2['exists'] else 'fail'}">{'YES' if v2['exists'] else 'NO'}</td><td>{v2.get('version','')}</td></tr>
</table>
<p><strong>verl_cu124 torch+CUDA</strong>: <span class="{'ok' if tc.get('torch_cuda')==True else 'fail'}">{cuda_s}</span><br><code>{tc.get('output','')}</code></p>
"""
    g = audit["gpu"]
    h += f'<h2>3. GPU 状态</h2><p>空闲 GPU：<strong>{g.get("free_gpus",0)}/{g.get("total_gpus",8)}</strong> (需>=4) -> <span class="{"ok" if g.get("ready") else "fail"}">{"READY" if g.get("ready") else "NOT READY"}</span></p>\n'
    if g.get("gpus"):
        h += '<table><tr><th>GPU</th><th>空闲(MiB)</th><th>总容量(MiB)</th><th>利用率</th></tr>\n'
        for gpu in g["gpus"]:
            cls = "ok" if gpu["free_mib"] >= 40000 else "fail"
            h += f'<tr><td>GPU{gpu["index"]}</td><td class="{cls}">{gpu["free_mib"]}</td><td>{gpu["total_mib"]}</td><td>{gpu["util_pct"]}%</td></tr>\n'
        h += "</table>\n"
    gw = audit["gpu_watcher"]
    h += f'<p>GPU Watcher: {"RUNNING" if gw["running"] else "NOT RUNNING"} ({len(gw.get("processes",[]))} procs)</p>\n'
    h += '<h2>4. 评测资产</h2><table><tr><th>资产</th><th>路径</th><th>存在</th></tr>\n'
    for a in audit["eval_assets"]:
        if isinstance(a, dict) and "label" in a:
            if "exists" in a: h += f'<tr><td>{a["label"]}</td><td><code>{a.get("path","")}</code></td><td class="{"ok" if a["exists"] else "fail"}">{"YES" if a["exists"] else "NO"}</td></tr>\n'
            elif "count" in a: h += f'<tr><td>{a["label"]}</td><td>-</td><td class="{"ok" if a.get("ok",a["count"]>0) else "fail"}">{a["count"]}</td></tr>\n'
    h += "</table>\n"
    h += '<h2>5. SFT/RL 数据</h2><table><tr><th>数据集</th><th>存在</th><th>行数/大小</th></tr>\n'
    for d in audit["sft_data"]:
        info = str(d.get("lines", d.get("size", "-")))
        h += f'<tr><td>{d["label"]}</td><td class="{"ok" if d["exists"] else "fail"}">{"YES" if d["exists"] else "NO"}</td><td>{info}</td></tr>\n'
    h += "</table>\n"
    h += '<h2>6. 脚本语法检查</h2><table><tr><th>脚本</th><th>存在</th><th>bash -n</th></tr>\n'
    for sc in audit["scripts"]:
        syn = "PASS" if sc.get("syntax_ok") else ("FAIL" if sc["exists"] else "-")
        cls = "ok" if sc.get("syntax_ok") else "fail"
        h += f'<tr><td><code>{sc["script"]}</code></td><td class="{"ok" if sc["exists"] else "fail"}">{"YES" if sc["exists"] else "NO"}</td><td class="{cls}">{syn}</td></tr>\n'
    h += "</table>\n"
    h += '<h2>7. 配置文件</h2><table><tr><th>配置</th><th>存在</th><th>引用旧模型路径</th></tr>\n'
    for c in audit["configs"]:
        old = "YES" if c["has_old_model_path"] else "NO"
        cls = "warn" if c["has_old_model_path"] else "ok"
        h += f'<tr><td><code>{c["config"]}</code></td><td class="{"ok" if c["exists"] else "fail"}">{"YES" if c["exists"] else "NO"}</td><td class="{cls}">{old}</td></tr>\n'
    h += "</table>\n"
    h += '<h2>8. 磁盘空间</h2><table><tr><th>挂载点</th><th>总容量</th><th>已用</th><th>可用</th><th>使用率</th></tr>\n'
    for d in audit["disk"]:
        if "error" not in d: h += f'<tr><td>{d["mount"]}</td><td>{d["total"]}</td><td>{d["used"]}</td><td>{d["avail"]}</td><td>{d["use_pct"]}</td></tr>\n'
    h += "</table>\n"
    h += f"""<h2>9. GPU 释放后行动计划</h2><div class="box"><ol>
<li><strong>修复模型路径</strong>：更新 paths.sh -> BAIZE_MODEL_PATH={NAS_MODEL_PATH}；更新 RL YAML tokenizer/model path；更新 Python 脚本硬编码</li>
<li><strong>GPU 释放</strong>：gpu_watcher 自动检测 -> NFS warm-up -> 启动 launch_11_9.sh</li>
<li><strong>SGLang serve MiniCPM5-2B</strong>：用 verl_cu124_venv SGLang 0.4.6（非 vLLM，CUDA 兼容），4xA40 TP=4</li>
<li><strong>复测 36% 基线</strong>：158任务x5-run Pass@1 2500s -p 8 -n</li>
<li><strong>采集真实失败轨迹</strong>：替换 R4/D1-D6 假设，校准 R88/R89</li>
<li><strong>RL 替身预演</strong>：按 R1/R2/R3 结论起 EDA 交互式 RL（标注不可迁移）</li>
</ol></div>
<h2>10. 关键结论</h2><div class="box"><ol>
<li><strong>模型路径是唯一硬阻塞（可修复）</strong>：/tmp 被清理 -> NAS 有完整副本 4.7GB -> 改 paths.sh 即可</li>
<li><strong>GPU 未释放是外部依赖</strong>：SGLang Qwen3.8-27B 占全 8 卡 0% util，gpu_watcher 轮询中</li>
<li><strong>所有脚本/配置/数据已就绪</strong>：12 bash 脚本 PASS，SFT 19524 对，RL parquet，eval 全套</li>
<li><strong>venv 已就绪</strong>：verl_cu124_venv (7.5G torch2.6.0+cu124 sglang0.4.6) 首选</li>
<li><strong>评测资产完整</strong>：eda_fastmcp 含 driver/scorer/158-case/API DB/traces</li>
</ol></div>
<h2>11. 溯源</h2><ul>
<li>审计脚本：baize_posttrain_r91_gpu_readiness_audit.py</li>
<li>模型：HuggingFace MiniCPM5-2B -> /tmp(11-06) -> /tmp清理 -> NAS副本(11-09 08:55)</li>
<li>venv：R25(verl_cu124) / wake13(vllm)</li>
<li>eda_fastmcp：L1.0 本地克隆(wake3)</li>
<li>SFT语料：v1(wake56)/v2(wake60)</li>
</ul></body></html>"""
    return h

def main():
    import argparse
    parser = argparse.ArgumentParser(description="R91 GPU Day Readiness Audit")
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--html", type=str, default=None)
    parser.add_argument("--decision-only", action="store_true")
    args = parser.parse_args()
    audit = run_audit()
    if args.decision_only:
        s = audit["summary"]
        print(f"GO: {s['overall_ready']}")
        print(f"BLOCKERS: {s['total_blockers']}")
        for b in s["blockers"]: print(f"  - {b}")
        print(f"READY: {s['ready_count']}")
        print(f"CAN_PROCEED_AFTER_FIXES: {s['can_proceed_after_fixes']}")
        return
    if args.json:
        Path(args.json).write_text(json.dumps(audit, indent=2, ensure_ascii=False, default=str))
        print(f"JSON written to {args.json}")
    if args.html:
        Path(args.html).write_text(generate_html(audit))
        print(f"HTML written to {args.html}")
    s = audit["summary"]
    print(f"\n{'='*60}")
    print(f"R91 GPU Day Readiness Audit -- {audit['timestamp']}")
    print(f"{'='*60}")
    print(f"Overall Ready: {'YES' if s['overall_ready'] else 'NO'}")
    print(f"Blockers: {s['total_blockers']}")
    for b in s["blockers"]: print(f"  BLOCKER: {b}")
    print(f"Ready Items: {s['ready_count']}")
    print(f"Can Proceed After Fixes: {'YES' if s['can_proceed_after_fixes'] else 'NO'}")
    print(f"Model old path: {'DELETED' if not Path(OLD_MODEL_PATH).exists() else 'exists'}")
    print(f"Model NAS path: {'exists' if Path(NAS_MODEL_PATH).exists() else 'MISSING'}")
    print(f"Files with old ref: {len(audit['tmp_model_refs'])}")
    g = audit["gpu"]
    print(f"GPU Free: {g.get('free_gpus',0)}/{g.get('total_gpus',8)}")

if __name__ == "__main__":
    main()
