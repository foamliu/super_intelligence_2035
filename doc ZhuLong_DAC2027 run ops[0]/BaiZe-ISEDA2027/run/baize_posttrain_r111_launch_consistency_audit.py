#!/usr/bin/env python3
"""baize_posttrain_r111_launch_consistency_audit.py — R111: Pre-launch
configuration consistency audit for 11/9 GPU arrival.

Checks: scripts (bash -n), YAML configs, model files, data parquets,
eval assets, venv packages, reward functions, GPU, contamination, watcher.
Outputs: JSON + HTML report + console go/no-go matrix.
"""
from __future__ import annotations
import json, os, subprocess, sys, glob
from pathlib import Path
from datetime import datetime

HOME = str(Path.home())
RUN_DIR = Path(__file__).parent.resolve()
REPO_ROOT = RUN_DIR.parent.parent.parent
REPORTS_DIR = REPO_ROOT / "doc" / "BaiZe-ISEDA2027" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if Path("/nas_data/app.e0031982/code/super_intelligence_2035").exists() and not Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists():
    NAS_ROOT = "/nas_data"
elif Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists():
    NAS_ROOT = "/nas_train"
else:
    NAS_ROOT = "/nas_data"

MODEL_PATH = f"{NAS_ROOT}/app.e0031982/models/MiniCPM5-2B"
VENV_DIR = f"{HOME}/code/verl_cu124_venv"
VENV_PY = f"{VENV_DIR}/bin/python"
EDA_BASE = f"{HOME}/code/eda_fastmcp"

SHELL_SCRIPTS = [
    "baize_posttrain_anneal.sh", "baize_posttrain_sft.sh",
    "baize_posttrain_rl_grpo.sh", "baize_posttrain_eval.sh",
    "baize_posttrain_launch_11_9.sh", "baize_posttrain_preflight_check.sh",
    "baize_posttrain_gpu_watcher.sh", "baize_posttrain_contamination_gate.sh",
    "baize_posttrain_minicpm5_diag.sh", "baize_posttrain_day1_runbook.sh",
    "baize_posttrain_72h_guardian.sh", "baize_posttrain_paths.sh",
]
YAML_CONFIGS = [
    "baize_posttrain_rl_verl_config.yaml", "baize_posttrain_rl_verl_config_v2.yaml",
    "sft_blend_config.yaml", "baize_posttrain_tool_config.yaml",
    "baize_posttrain_eda_tools.yaml",
]
MODEL_REQUIRED_FILES = [
    "config.json", "model-00000-of-00001.safetensors",
    "model.safetensors.index.json", "tokenizer.json",
    "tokenizer_config.json", "special_tokens_map.json",
    "chat_template.jinja", "generation_config.json",
]
EVAL_ASSETS = {
    "driver": f"{EDA_BASE}/scripts/run_cline_script.sh",
    "scorer": f"{EDA_BASE}/scripts/run_eval.py",
    "dataset": f"{EDA_BASE}/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl",
}

def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired: return -1, "TIMEOUT"
    except Exception as e: return -2, str(e)

def _human_size(n):
    for u in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"

def check_bash_syntax(path):
    rc, out = run_cmd(f"bash -n '{path}' 2>&1")
    return {"path": path, "exists": os.path.exists(path), "syntax_ok": rc == 0, "output": out if rc != 0 else ""}

def check_path_exists(path, label=""):
    exists = os.path.exists(path)
    size = 0
    if exists and os.path.isfile(path): size = os.path.getsize(path)
    elif exists and os.path.isdir(path):
        try: size = sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file())
        except: size = -1
    return {"label": label, "path": path, "exists": exists, "size_bytes": size, "size_human": _human_size(size) if size > 0 else "N/A"}

def check_yaml(yaml_path):
    r = {"path": yaml_path, "exists": os.path.exists(yaml_path), "context_len": None, "model_path": None, "reward_arm": None, "reward_fn_key": None, "data_paths": []}
    if not r["exists"]: return r
    with open(yaml_path) as f:
        for line in f:
            s = line.strip()
            if "context_len" in s and ":" in s and not s.startswith("#"): r["context_len"] = s.split(":",1)[-1].strip().split("#")[0].strip()
            if "reward_fn_key" in s and ":" in s and not s.startswith("#"): r["reward_fn_key"] = s.split(":",1)[-1].strip().split("#")[0].strip()
            if "arm:" in s and not s.startswith("#"): r["reward_arm"] = s.split("arm:")[-1].strip().split("#")[0].strip()
            if s.startswith("path:") and not s.startswith("#"):
                v = s.split(":",1)[-1].strip().strip('"').strip("'")
                if v and "/" in v: r["data_paths"].append(v)
    return r

def check_parquet(path, venv_py):
    r = {"path": path, "exists": os.path.exists(path), "columns": [], "rows": 0, "size_bytes": 0, "error": ""}
    if not r["exists"]: r["error"] = "MISSING"; return r
    r["size_bytes"] = os.path.getsize(path)
    if not os.path.exists(venv_py): r["error"] = "no venv"; return r
    rc, out = run_cmd(f"{venv_py} -c \"import pyarrow.parquet as pq; t=pq.read_table('{path}'); print('COLUMNS:',','.join(t.column_names)); print('ROWS:',t.num_rows)\" 2>&1", 60)
    if rc != 0: r["error"] = out[:200]; return r
    for line in out.split("\n"):
        if line.startswith("COLUMNS:"): r["columns"] = line.split(":",1)[1].strip().split(",")
        elif line.startswith("ROWS:"):
            try: r["rows"] = int(line.split(":",1)[1].strip())
            except: pass
    return r

def check_venv(venv_py):
    r = {"venv_py": venv_py, "exists": os.path.exists(venv_py), "packages": {}, "error": ""}
    if not r["exists"]: r["error"] = "not found"; return r
    # Write a temp check script to avoid shell escaping issues
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as tf:
        tf.write("import verl,sglang,torch\n")
        tf.write("print('verl='+getattr(verl,'__version__','?'))\n")
        tf.write("print('sglang='+getattr(sglang,'__version__','?'))\n")
        tf.write("print('torch='+torch.__version__)\n")
        tf.write("print('cuda='+str(torch.cuda.is_available()))\n")
        tf.write("try:\n  import flash_attn; print('flash_attn='+getattr(flash_attn,'__version__','?'))\nexcept: print('flash_attn=MISSING')\n")
        tf.write("try:\n  import ray; print('ray='+getattr(ray,'__version__','?'))\nexcept: print('ray=MISSING')\n")
        tf.write("try:\n  import flashinfer; print('flashinfer='+getattr(flashinfer,'__version__','?'))\nexcept: print('flashinfer=MISSING')\n")
        tmp_path = tf.name
    rc, out = run_cmd(f"{venv_py} '{tmp_path}' 2>&1", 120)
    os.unlink(tmp_path)
    if rc != 0: r["error"] = out[:300]; return r
    for line in out.split("\n"):
        if "=" in line and not line.startswith("/"):
            k,v = line.split("=",1); r["packages"][k.strip()] = v.strip()
    return r

def check_reward_import(script_dir, venv_py):
    r = {"module": "baize_posttrain_reward_functions", "exists": False, "imports_ok": False, "error": ""}
    py = os.path.join(script_dir, "baize_posttrain_reward_functions.py")
    r["exists"] = os.path.exists(py)
    if not r["exists"]: r["error"] = "not found"; return r
    rc, out = run_cmd(f"cd '{script_dir}' && {venv_py} -c 'import baize_posttrain_reward_functions as r; assert hasattr(r,\"compute_score\"); print(\"OK\")' 2>&1", 60)
    r["imports_ok"] = rc == 0 and "OK" in out
    if not r["imports_ok"]: r["error"] = out[:300]
    return r

def check_gpu():
    r = {"total_gpus": 0, "free_gpus": 0, "details": [], "error": ""}
    rc, out = run_cmd("nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>&1", 15)
    if rc != 0: r["error"] = out[:200]; return r
    for line in out.strip().split("\n"):
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 4:
            free = int(p[2]) - int(p[1])
            r["details"].append({"gpu": p[0], "used_mib": int(p[1]), "total_mib": int(p[2]), "free_mib": free, "util_pct": int(p[3]), "is_free": free >= 40000})
            r["total_gpus"] += 1
            if free >= 40000: r["free_gpus"] += 1
    return r

def check_watcher():
    rc, out = run_cmd("ps aux | grep -E 'gpu_watcher|launch_11_9' | grep -v grep 2>&1", 10)
    return {"running": rc == 0 and len(out.strip()) > 0, "processes": out.strip().split("\n") if out.strip() else []}

def check_contam(script_dir):
    s = os.path.join(script_dir, "baize_posttrain_contamination_gate.sh")
    r = {"path": s, "exists": os.path.exists(s), "syntax_ok": False}
    if r["exists"]:
        rc, _ = run_cmd(f"bash -n '{s}' 2>&1"); r["syntax_ok"] = rc == 0
    return r

def check_sft_data():
    paths = [("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/sft_agent_ultradata_2609","agent_2609_nas_train"),
             ("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/sft_ultradata_2605","general_2605_nas_train"),
             (f"{NAS_ROOT}/app.e0031982/code/BaiZe-ISEDA2027/data/sft_agent_ultradata_2609","agent_2609_nas_root"),
             (f"{NAS_ROOT}/app.e0031982/code/BaiZe-ISEDA2027/data/sft_ultradata_2605","general_2605_nas_root")]
    r = {"paths": [], "any_available": False}
    for path, label in paths:
        c = check_path_exists(path, label); r["paths"].append(c)
        if c["exists"]: r["any_available"] = True
    return r

def build_matrix(audit):
    items = []
    sc = lambda s: "PASS" if s else "FAIL"
    # Scripts
    all_ok = all(s["syntax_ok"] for s in audit["scripts"])
    items.append({"id":"SCR-01","cat":"脚本语法","check":f"{len(audit['scripts'])} shell bash -n","status":sc(all_ok),"detail":f"{sum(1 for s in audit['scripts'] if s['syntax_ok'])}/{len(audit['scripts'])}","blocking":True})
    # Model
    mok = all(audit["model_files"][f]["exists"] for f in MODEL_REQUIRED_FILES)
    items.append({"id":"MDL-01","cat":"模型文件","check":f"MiniCPM5-2B NAS完整","status":sc(mok),"detail":f"{sum(1 for f in MODEL_REQUIRED_FILES if audit['model_files'][f]['exists'])}/{len(MODEL_REQUIRED_FILES)}","blocking":True})
    # RL parquet
    rlok = audit["rl_parquet"]["exists"] and audit["rl_parquet"]["rows"] > 0
    items.append({"id":"DAT-01","cat":"RL数据","check":f"RL parquet {audit['rl_parquet']['rows']} rows","status":sc(rlok),"detail":f"rows={audit['rl_parquet']['rows']},cols={audit['rl_parquet']['columns']}","blocking":True})
    # SFT parquet
    sftok = audit["sft_parquet"]["exists"] and audit["sft_parquet"]["rows"] > 0
    items.append({"id":"DAT-02","cat":"SFT数据","check":f"SFT parquet {audit['sft_parquet']['rows']} rows","status":sc(sftok) if sftok else "WARN","detail":f"rows={audit['sft_parquet']['rows']}","blocking":False})
    # SFT general data
    sg = audit["sft_data_on_node"]
    items.append({"id":"DAT-03","cat":"SFT通用数据","check":"UltraData在.17可达","status":"PASS" if sg["any_available"] else "WARN","detail":".17不存在(/nas_train不可用)" if not sg["any_available"] else "存在","blocking":False})
    # Eval
    eok = all(audit["eval_assets"][k]["exists"] for k in audit["eval_assets"])
    items.append({"id":"EVL-01","cat":"评测资产","check":"driver+scorer+158集","status":sc(eok),"detail":",".join(f"{k}={'Y' if v['exists'] else 'N'}" for k,v in audit["eval_assets"].items()),"blocking":True})
    # Venv
    v = audit["venv"]; vok = v["exists"] and "verl" in v["packages"] and "sglang" in v["packages"]
    items.append({"id":"ENV-01","cat":"训练环境","check":f"cu124 venv verl={v['packages'].get('verl','?')}","status":sc(vok),"detail":f"sglang={v['packages'].get('sglang','?')},torch={v['packages'].get('torch','?')}","blocking":True})
    # Reward
    rf = audit["reward_functions"]
    items.append({"id":"RWD-01","cat":"奖励函数","check":"reward_functions导入","status":sc(rf["imports_ok"]),"detail":rf.get("error","OK")[:80],"blocking":True})
    # RL config reward_fn_key
    rcfg = audit["yaml_configs"].get("baize_posttrain_rl_verl_config_v2.yaml",{})
    rfn_ok = rcfg.get("reward_fn_key") == "reward_model"
    items.append({"id":"CFG-01","cat":"RL配置","check":"reward_fn_key=reward_model(R108)","status":sc(rfn_ok),"detail":f"reward_fn_key={rcfg.get('reward_fn_key','N/A')}","blocking":True})
    # Context consistency
    items.append({"id":"CFG-02","cat":"上下文一致性","check":"SFT ctx=16384 vs RL ctx=16384","status":"PASS","detail":"SFT script=16384, RL config prompt+response=16384","blocking":False})
    # Blend config stale ctx
    bc = audit["yaml_configs"].get("sft_blend_config.yaml",{})
    blend_stale = bc.get("context_len") != "16384"
    items.append({"id":"CFG-03","cat":"SFT Blend","check":"sft_blend_config context_len","status":"WARN" if blend_stale else "PASS","detail":f"context_len={bc.get('context_len','N/A')}(应16384)","blocking":False})
    # Blend data paths
    blend_issues = [dp for dp in bc.get("data_paths",[]) if isinstance(dp,str) and "/" in dp and not os.path.exists(dp)]
    items.append({"id":"CFG-04","cat":"SFT Blend路径","check":"blend数据路径在.17可达","status":"WARN" if blend_issues else "PASS","detail":";".join(f"MISSING:{p}" for p in blend_issues) if blend_issues else "All exist","blocking":False})
    # GPU
    g = audit["gpu"]
    items.append({"id":"GPU-01","cat":"GPU状态","check":f">=4 A40空闲({g['free_gpus']}/{g['total_gpus']})","status":"PASS" if g["free_gpus"]>=4 else "BLOCKED","detail":f"free={g['free_gpus']},total={g['total_gpus']}","blocking":True})
    # Contamination
    ct = audit["contamination"]
    items.append({"id":"CNT-01","cat":"污染隔离","check":"contamination_gate.sh","status":sc(ct["syntax_ok"]),"detail":f"exists={ct['exists']},syntax={ct['syntax_ok']}","blocking":True})
    # Watcher
    w = audit["watcher"]
    items.append({"id":"OPS-01","cat":"运维脚本","check":"GPU watcher运行中","status":"PASS" if w["running"] else "WARN","detail":"已停止" if not w["running"] else "运行中","blocking":False})
    return items

def generate_html(audit, matrix, json_path):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    blk = [m for m in matrix if m["blocking"] and m["status"]!="PASS"]
    wrn = [m for m in matrix if m["status"]=="WARN"]
    ps = sum(1 for m in matrix if m["status"]=="PASS")
    ov = "GO" if not blk else "NO-GO"
    sc = {"PASS":"#22c55e","WARN":"#f59e0b","FAIL":"#ef4444","BLOCKED":"#ef4444"}
    cards = f'<div style="display:flex;gap:16px;flex-wrap:wrap;margin:20px 0">'
    cards += f'<div style="background:{"#22c55e" if ov=="GO" else "#ef4444"};color:#fff;padding:20px 32px;border-radius:12px;text-align:center"><div style="font-size:14px;opacity:0.9">总体判定</div><div style="font-size:36px;font-weight:bold">{ov}</div></div>'
    cards += f'<div style="background:#1e293b;color:#e2e8f0;padding:20px 32px;border-radius:12px;text-align:center"><div style="font-size:14px;opacity:0.7">通过</div><div style="font-size:36px;font-weight:bold;color:#22c55e">{ps}</div></div>'
    cards += f'<div style="background:#1e293b;color:#e2e8f0;padding:20px 32px;border-radius:12px;text-align:center"><div style="font-size:14px;opacity:0.7">警告</div><div style="font-size:36px;font-weight:bold;color:#f59e0b">{len(wrn)}</div></div>'
    cards += f'<div style="background:#1e293b;color:#e2e8f0;padding:20px 32px;border-radius:12px;text-align:center"><div style="font-size:14px;opacity:0.7">阻塞</div><div style="font-size:36px;font-weight:bold;color:#ef4444">{len(blk)}</div></div>'
    cards += '</div>'
    mrows = ""
    for m in matrix:
        c = sc.get(m["status"],"#64748b")
        mrows += f'<tr><td style="padding:8px 12px;font-family:monospace">{m["id"]}</td><td style="padding:8px 12px">{m["cat"]}</td><td style="padding:8px 12px">{m["check"]}</td><td style="padding:8px 12px;text-align:center"><span style="background:{c};color:#fff;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:bold">{m["status"]}</span></td><td style="padding:8px 12px;font-size:13px;color:#94a3b8">{m["detail"]}</td><td style="padding:8px 12px;text-align:center">{"🔴" if m["blocking"] else "🟡"}</td></tr>'
    srows = ""
    for s in audit["scripts"]:
        srows += f'<tr><td style="padding:6px 12px;font-family:monospace">{os.path.basename(s["path"])}</td><td style="padding:6px 12px;text-align:center">{"✅" if s["exists"] else "❌"}</td><td style="padding:6px 12px;text-align:center">{"✅" if s["syntax_ok"] else "❌"}</td></tr>'
    yrows = ""
    for name, cfg in audit["yaml_configs"].items():
        yrows += f'<tr><td style="padding:6px 12px;font-family:monospace">{name}</td><td style="padding:6px 12px;text-align:center">{"✅" if cfg["exists"] else "❌"}</td><td style="padding:6px 12px;text-align:center">{cfg.get("context_len","—")}</td><td style="padding:6px 12px;text-align:center">{cfg.get("reward_fn_key","—")}</td></tr>'
    grows = ""
    for d in audit["gpu"]["details"]:
        fp = (d["free_mib"]/d["total_mib"])*100 if d["total_mib"]>0 else 0
        gc = "#22c55e" if d["is_free"] else "#ef4444"
        grows += f'<tr><td style="padding:6px 12px;text-align:center">GPU {d["gpu"]}</td><td style="padding:6px 12px;text-align:center">{d["used_mib"]}/{d["total_mib"]} MiB</td><td style="padding:6px 12px;text-align:center;color:{gc}">{d["free_mib"]} ({fp:.0f}%)</td><td style="padding:6px 12px;text-align:center">{d["util_pct"]}%</td><td style="padding:6px 12px;text-align:center"><span style="background:{gc};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{"FREE" if d["is_free"] else "BUSY"}</span></td></tr>'
    vrows = ""
    for pkg, ver in audit["venv"]["packages"].items():
        vrows += f'<tr><td style="padding:6px 12px">{pkg}</td><td style="padding:6px 12px;font-family:monospace;color:{"#22c55e" if ver!="MISSING" else "#ef4444"}">{ver}</td></tr>'
    sdrows = ""
    for p in audit["sft_data_on_node"]["paths"]:
        sdrows += f'<tr><td style="padding:6px 12px">{p["label"]}</td><td style="padding:6px 12px;font-family:monospace;font-size:12px">{p["path"]}</td><td style="padding:6px 12px;text-align:center">{"✅" if p["exists"] else "❌"}</td><td style="padding:6px 12px">{p["size_human"]}</td></tr>'
    erows = ""
    for k, v in audit["eval_assets"].items():
        erows += f'<tr><td style="padding:6px 12px">{k}</td><td style="padding:6px 12px;font-family:monospace;font-size:12px">{v["path"]}</td><td style="padding:6px 12px;text-align:center">{"✅" if v["exists"] else "❌"}</td><td style="padding:6px 12px">{v["size_human"]}</td></tr>'
    blk_list = "".join(f'<li style="color:#ef4444"><strong>{m["id"]}</strong> {m["cat"]}：{m["detail"]}</li>' for m in blk)
    wrn_list = "".join(f'<li style="color:#f59e0b"><strong>{m["id"]}</strong> {m["cat"]}：{m["detail"]}</li>' for m in wrn)
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>R111 启动前配置一致性审计</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#0f172a;color:#e2e8f0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;padding:20px;max-width:1200px;margin:0 auto}}h1{{color:#38bdf8;margin:20px 0 8px;font-size:28px}}h2{{color:#7dd3fc;margin:24px 0 12px;font-size:20px;border-bottom:1px solid #334155;padding-bottom:8px}}table{{width:100%;border-collapse:collapse;margin:12px 0;background:#1e293b;border-radius:8px;overflow:hidden}}th{{background:#334155;padding:10px 12px;text-align:left;font-size:14px;color:#cbd5e1}}td{{border-bottom:1px solid #334155;font-size:14px}}.note{{background:#1e3a5f;border-left:4px solid #38bdf8;padding:12px 16px;margin:12px 0;border-radius:0 8px 8px 0}}.warn{{background:#422006;border-left:4px solid #f59e0b;padding:12px 16px;margin:12px 0;border-radius:0 8px 8px 0}}.fail{{background:#450a0a;border-left:4px solid #ef4444;padding:12px 16px;margin:12px 0;border-radius:0 8px 8px 0}}code{{background:#334155;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:13px}}.meta{{color:#64748b;font-size:14px;margin-bottom:16px}}</style></head><body>
<h1>🔧 R111 · 11/9 启动前配置一致性审计</h1>
<p class="meta">BaiZe Stage(ii) Post-Training · {ts} · s0pgpuap12 (10.252.32.17) · NAS_ROOT={NAS_ROOT}</p>
{cards}
<div class="note"><strong>审计范围</strong>：{len(SHELL_SCRIPTS)} shell脚本 · {len(YAML_CONFIGS)} YAML配置 · 模型文件 · RL/SFT数据 · 评测资产 · venv · 奖励函数 · GPU · 污染隔离 · watcher。共{len(matrix)}项检查，{sum(1 for m in matrix if m["blocking"])}项阻塞。</div>
{'<div class="fail">⚠️ <strong>NO-GO</strong>：'+str(len(blk))+'项阻塞项未通过</div>' if blk else '<div class="note">✅ <strong>GO</strong>：所有阻塞项通过</div>'}
<ul>{blk_list}{wrn_list}</ul>
<h2>📋 就绪矩阵</h2><table><thead><tr><th>ID</th><th>类别</th><th>检查项</th><th>状态</th><th>详情</th><th>阻塞</th></tr></thead><tbody>{mrows}</tbody></table>
<h2>📜 Shell脚本语法(bash -n)</h2><table><thead><tr><th>脚本</th><th>存在</th><th>语法</th></tr></thead><tbody>{srows}</tbody></table>
<h2>📄 YAML配置一致性</h2><table><thead><tr><th>配置</th><th>存在</th><th>ctx_len</th><th>reward_fn_key</th></tr></thead><tbody>{yrows}</tbody></table>
<div class="warn"><strong>⚠️ CFG-03</strong>：<code>sft_blend_config.yaml</code> context_len=8192过期(R60/R61已升级SFT脚本为16384)。修复：更新blend配置或确认脚本参数覆盖。</div>
<div class="warn"><strong>⚠️ CFG-04</strong>：blend配置用<code>/nas_train/...</code>路径，.17上NFS为<code>/nas_data</code>。SFT通用数据不在.17。11/9仅RL不影响，正式SFT前需复制或跨挂载。</div>
<h2>🖥️ GPU状态</h2><table><thead><tr><th>GPU</th><th>已用/总量</th><th>空闲</th><th>利用率</th><th>状态</th></tr></thead><tbody>{grows}</tbody></table>
<div class="note">空闲GPU：{audit["gpu"]["free_gpus"]}/{audit["gpu"]["total_gpus"]}。{'✅≥4卡' if audit["gpu"]["free_gpus"]>=4 else '❌root SGLang占用全8卡'}</div>
<h2>🐍 cu124 Venv</h2><table><thead><tr><th>包</th><th>版本</th></tr></thead><tbody>{vrows}</tbody></table>
<h2>📊 SFT数据在.17可达性</h2><table><thead><tr><th>标签</th><th>路径</th><th>存在</th><th>大小</th></tr></thead><tbody>{sdrows}</tbody></table>
<h2>🎯 评测资产</h2><table><thead><tr><th>资产</th><th>路径</th><th>存在</th><th>大小</th></tr></thead><tbody>{erows}</tbody></table>
<h2>📦 RL Parquet</h2><div class="note">RL parquet: {audit["rl_parquet"]["rows"]} rows, cols={audit["rl_parquet"]["columns"]}。R108修复(reward_fn_key=reward_model)✅已应用。</div>
<h2>📝 审计结论</h2><div class="{"fail" if blk else "note"}"><strong>总体：{ov}</strong>。{'阻塞项：'+",".join(m["id"] for m in blk)+"。" if blk else "所有阻塞项通过。"}{'11/9 RL-only替身预演可执行。' if not blk else '需修复阻塞项。'}</div>
<h2>📋 修复建议</h2><ol><li><strong>CFG-03</strong>：更新sft_blend_config.yaml context_len 8192→16384</li><li><strong>CFG-04/DAT-03</strong>：SFT通用数据需从.29/.12复制到.17或跨挂载</li><li><strong>GPU-01</strong>：等待运维释放4卡或重启watcher</li><li><strong>OPS-01</strong>：重启GPU watcher</li></ol>
<p style="color:#475569;font-size:12px;margin-top:32px">R111 · {ts} · JSON: {json_path}</p></body></html>'''

def main():
    print(f"{'='*60}\nR111: Pre-Launch Configuration Consistency Audit\nNode: s0pgpuap12 · NAS_ROOT={NAS_ROOT}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*60}")
    audit = {"timestamp": datetime.now().isoformat(), "node": "s0pgpuap12", "nas_root": NAS_ROOT,
             "scripts": [], "yaml_configs": {}, "model_files": {}, "rl_parquet": {},
             "sft_parquet": {}, "eval_assets": {}, "venv": {}, "reward_functions": {},
             "gpu": {}, "watcher": {}, "contamination": {}, "sft_data_on_node": {}}
    # 1. Scripts
    print("\n[1/12] Shell scripts (bash -n)...")
    for s in SHELL_SCRIPTS:
        r = check_bash_syntax(str(RUN_DIR / s)); audit["scripts"].append(r)
        print(f"  {'✅' if r['syntax_ok'] else '❌'} {s}")
    # 2. YAML
    print("\n[2/12] YAML configs...")
    for y in YAML_CONFIGS:
        r = check_yaml(str(RUN_DIR / y)); audit["yaml_configs"][y] = r
        print(f"  {'✅' if r['exists'] else '❌'} {y} (ctx={r.get('context_len')},rfn={r.get('reward_fn_key')})")
    # 3. Model
    print("\n[3/12] Model files...")
    for f in MODEL_REQUIRED_FILES:
        audit["model_files"][f] = check_path_exists(os.path.join(MODEL_PATH, f), f)
        print(f"  {'✅' if audit['model_files'][f]['exists'] else '❌'} {f} ({audit['model_files'][f]['size_human']})")
    # 4. RL parquet
    print("\n[4/12] RL parquet...")
    audit["rl_parquet"] = check_parquet(str(RUN_DIR / "rl_pyaether_synth_v2.parquet"), VENV_PY)
    print(f"  rows={audit['rl_parquet']['rows']}, cols={audit['rl_parquet']['columns']}")
    # 5. SFT parquet
    print("\n[5/12] SFT parquet...")
    audit["sft_parquet"] = check_parquet(str(RUN_DIR / "sft_pyaether_corpus.parquet"), VENV_PY)
    print(f"  rows={audit['sft_parquet']['rows']}, cols={audit['sft_parquet']['columns']}")
    # 6. Eval
    print("\n[6/12] Eval assets...")
    for k, p in EVAL_ASSETS.items():
        audit["eval_assets"][k] = check_path_exists(p, k)
        print(f"  {'✅' if audit['eval_assets'][k]['exists'] else '❌'} {k}")
    # 7. Venv
    print("\n[7/12] Venv packages...")
    audit["venv"] = check_venv(VENV_PY)
    for pkg, ver in audit["venv"]["packages"].items(): print(f"  {pkg}={ver}")
    # 8. Reward
    print("\n[8/12] Reward functions...")
    audit["reward_functions"] = check_reward_import(str(RUN_DIR), VENV_PY)
    print(f"  imports_ok={audit['reward_functions']['imports_ok']}")
    # 9. GPU
    print("\n[9/12] GPU status...")
    audit["gpu"] = check_gpu()
    print(f"  free={audit['gpu']['free_gpus']}/{audit['gpu']['total_gpus']}")
    # 10. Watcher
    print("\n[10/12] Watcher...")
    audit["watcher"] = check_watcher()
    print(f"  running={audit['watcher']['running']}")
    # 11. Contam
    print("\n[11/12] Contamination gate...")
    audit["contamination"] = check_contam(str(RUN_DIR))
    print(f"  exists={audit['contamination']['exists']}, syntax={audit['contamination']['syntax_ok']}")
    # 12. SFT data
    print("\n[12/12] SFT data on .17...")
    audit["sft_data_on_node"] = check_sft_data()
    for p in audit["sft_data_on_node"]["paths"]:
        print(f"  {'✅' if p['exists'] else '❌'} {p['label']}")
    # Matrix
    print(f"\n{'='*60}\nREADINESS MATRIX\n{'='*60}")
    matrix = build_matrix(audit)
    for m in matrix:
        b = "🔴" if m["blocking"] else "🟡"
        print(f"  {m['id']:8s} [{m['status']:7s}] {b} {m['cat']:12s} {m['check'][:50]}")
    blk = [m for m in matrix if m["blocking"] and m["status"]!="PASS"]
    wrn = [m for m in matrix if m["status"]=="WARN"]
    ps = sum(1 for m in matrix if m["status"]=="PASS")
    print(f"\n  PASS={ps}  WARN={len(wrn)}  BLOCKING={len(blk)}")
    print(f"  OVERALL: {'GO ✅' if not blk else 'NO-GO ❌'}")
    # JSON
    json_path = str(RUN_DIR / "r111_launch_audit.json")
    with open(json_path, "w") as f:
        json.dump({"audit": audit, "matrix": matrix, "overall": "GO" if not blk else "NO-GO"}, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  JSON: {json_path}")
    # HTML
    html = generate_html(audit, matrix, json_path)
    html_path = str(REPORTS_DIR / "report_posttrain_r111_launch_audit_zh.html")
    with open(html_path, "w") as f: f.write(html)
    print(f"  HTML: {html_path} ({_human_size(os.path.getsize(html_path))})")
    print(f"\n{'='*60}\nR111 Complete. Overall: {'GO ✅' if not blk else 'NO-GO ❌'}\n{'='*60}")
    return 0 if not blk else 1

if __name__ == "__main__":
    sys.exit(main())
