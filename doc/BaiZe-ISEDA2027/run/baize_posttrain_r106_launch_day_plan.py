#!/usr/bin/env python3
"""R106: Launch-Day Execution Plan & Final Config Freeze.

Consolidates 105 prior research rounds (R1-R105) into a single actionable
document for the 11/9 GPU arrival. Produces:
  1. A go/no-go checklist (all prerequisites verified)
  2. A concrete 72h timeline with milestones and decision gates
  3. Final frozen configs (SFT recipe, RL GRPO params, eval protocol)
  4. Real-time monitoring specification (metrics, alerts, thresholds)
  5. Rollback / failure recovery decision tree

Usage:
  python3 baize_posttrain_r106_launch_day_plan.py [--html] [--json] [--smoke]

Zero GPU. Pure computation + file system checks.
"""

import json, os, sys, time, subprocess
from pathlib import Path
from datetime import datetime, timedelta

RUN_DIR = Path(__file__).parent.resolve()
CODE_DIR = RUN_DIR.parent.parent.parent
REPORT_DIR = CODE_DIR / "doc" / "BaiZe-ISEDA2027" / "reports"
EXP_FILE = RUN_DIR / "EXPERIMENTS_POSTTRAIN.md"

if (Path("/nas_data/app.e0031982/code/super_intelligence_2035").exists()
        and not Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists()):
    NAS_ROOT = "/nas_data"
elif Path("/nas_train/app.e0031982/code/super_intelligence_2035").exists():
    NAS_ROOT = "/nas_train"
else:
    NAS_ROOT = "/nas_data"

MODEL_PATH = f"{NAS_ROOT}/app.e0031982/models/MiniCPM5-2B"
EDA_BASE = os.path.expanduser("~/code/eda_fastmcp")
VENV_DIR = os.path.expanduser("~/code/verl_cu124_venv")
VENV_PY = os.path.join(VENV_DIR, "bin", "python")


def _human_size(n):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"


def check_file(path, label, min_size=0):
    p = Path(path)
    if p.exists():
        if p.is_file():
            sz = p.stat().st_size
            return {"label": label, "path": str(path), "exists": True,
                    "size_bytes": sz, "size_human": _human_size(sz), "ok": sz >= min_size}
        else:
            return {"label": label, "path": str(path), "exists": True, "is_dir": True, "ok": True}
    return {"label": label, "path": str(path), "exists": False, "ok": False}


def check_script_syntax(script_path):
    try:
        r = subprocess.run(["bash", "-n", script_path], capture_output=True, timeout=10)
        return {"path": script_path, "ok": r.returncode == 0, "error": r.stderr.decode().strip() if r.returncode else ""}
    except Exception as e:
        return {"path": script_path, "ok": False, "error": str(e)}


def check_gpu():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, timeout=15)
        if r.returncode != 0:
            return {"available": False, "error": r.stderr.decode().strip()}
        gpus = []
        for line in r.stdout.decode().strip().split("\n"):
            parts = [x.strip() for x in line.split(",")]
            if len(parts) >= 3:
                idx, used, total = parts[0], int(parts[1]), int(parts[2])
                util = int(parts[3]) if len(parts) > 3 else 0
                free = total - used
                gpus.append({"id": idx, "used_mib": used, "total_mib": total,
                             "free_mib": free, "util_pct": util, "free": free >= 40000})
        free_count = sum(1 for g in gpus if g["free"])
        return {"available": free_count >= 4, "free_count": free_count, "total": len(gpus), "gpus": gpus}
    except Exception as e:
        return {"available": False, "error": str(e)}


# === 1. GO/NO-GO CHECKLIST ===
def build_checklist():
    checks = []
    checks.append({"category": "Model", **check_file(MODEL_PATH, "MiniCPM5-2B model", 1_000_000)})
    if Path(MODEL_PATH).exists():
        for f in ["config.json", "tokenizer.json", "tokenizer_config.json",
                   "model.safetensors.index.json", "chat_template.jinja"]:
            checks.append({"category": "Model", **check_file(os.path.join(MODEL_PATH, f), f"  {f}")})
    checks.append({"category": "EDA Env", **check_file(EDA_BASE, "eda_fastmcp clone")})
    checks.append({"category": "EDA Env", **check_file(
        os.path.join(EDA_BASE, "pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"), "158-case dataset")})
    checks.append({"category": "EDA Env", **check_file(os.path.join(EDA_BASE, "scripts/run_eval.py"), "Eval script")})
    checks.append({"category": "EDA Env", **check_file(os.path.join(EDA_BASE, "scripts/run_cline_script.sh"), "Driver script")})
    checks.append({"category": "EDA Env", **check_file(os.path.join(EDA_BASE, "docs/API_INFO_MERGED_V3.json"), "API database (8463 APIs)")})
    checks.append({"category": "Venv", **check_file(VENV_PY, "verl cu124 venv python")})
    checks.append({"category": "Venv", **check_file(os.path.join(VENV_DIR, "lib"), "venv lib dir")})
    checks.append({"category": "Data", **check_file(
        str(RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet"), "SFT PyAether v5 parquet", 100_000)})
    checks.append({"category": "Data", **check_file(
        str(RUN_DIR / "rl_pyaether_synth_tasks.jsonl"), "RL synth tasks (500)", 100_000)})
    checks.append({"category": "Data", **check_file(
        str(RUN_DIR / "sft_pyaether_corpus_v2.parquet"), "SFT PyAether v2 parquet (fallback)", 1_000_000)})
    checks.append({"category": "Config", **check_file(str(RUN_DIR / "baize_posttrain_rl_verl_config_v2.yaml"), "RL verl config v2")})
    checks.append({"category": "Config", **check_file(str(RUN_DIR / "sft_blend_config.yaml"), "SFT blend config")})
    checks.append({"category": "Config", **check_file(str(RUN_DIR / "baize_posttrain_tool_config.yaml"), "Tool config")})
    scripts = ["baize_posttrain_launch_11_9.sh", "baize_posttrain_setup_cu124_venv.sh",
               "baize_posttrain_preflight_check.sh", "baize_posttrain_minicpm5_diag.sh",
               "baize_posttrain_contamination_gate.sh", "baize_posttrain_rl_grpo.sh",
               "baize_posttrain_sft.sh", "baize_posttrain_anneal.sh", "baize_posttrain_eval.sh",
               "baize_posttrain_gpu_watcher.sh", "baize_posttrain_paths.sh"]
    for s in scripts:
        p = str(RUN_DIR / s)
        if Path(p).exists():
            checks.append({"category": "Script", "name": s, **check_script_syntax(p)})
        else:
            checks.append({"category": "Script", "name": s, "path": p, "exists": False, "ok": False})
    gpu_info = check_gpu()
    checks.append({"category": "GPU", "name": "GPU availability", "ok": gpu_info["available"],
                    "detail": f"{gpu_info.get('free_count', 0)}/{gpu_info.get('total', 0)} free"})
    try:
        r = subprocess.run(["pgrep", "-f", "baize_posttrain_gpu_watcher"], capture_output=True, timeout=5)
        watcher_alive = r.returncode == 0
    except:
        watcher_alive = False
    checks.append({"category": "Watcher", "name": "gpu_watcher process", "ok": watcher_alive,
                    "detail": "alive" if watcher_alive else "NOT running"})
    return checks, gpu_info


# === 2. 72H TIMELINE ===
def build_timeline(gpu_info):
    now = datetime.now()
    t0 = now
    fc = gpu_info.get('free_count', 0)
    tot = gpu_info.get('total', 0)
    gpu_status = f"GPU {'AVAILABLE' if gpu_info['available'] else f'NOT YET FREE ({fc}/{tot})'} — watcher polling"
    phases = [
        {"phase": "P0-Setup", "duration_h": 0.5,
         "steps": ["Step 0: Setup cu124 venv", "Step 1: Preflight check"],
         "gates": ["All preflight pass", "Venv has torch+sglang+verl"],
         "decision": "If preflight fails → fix before proceeding"},
        {"phase": "P1-Baseline", "duration_h": 2.0,
         "steps": ["Step 2: SGLang serve MiniCPM5-2B 4xA40", "Baseline eval: 158 tasks 5-run Pass@1 2500s",
                   "Step 3: Extract D1-D6"],
         "gates": ["SGLang responds", "Pass@1 in [30%,42%]", "D1-D6 saved"],
         "decision": "If baseline <30% or >42% → investigate",
         "milestone": "M0: Baseline ~36%"},
        {"phase": "P2-Contamination", "duration_h": 0.5,
         "steps": ["Step 4: Contamination gate"],
         "gates": ["0 contamination hits"],
         "decision": "If contamination → STOP"},
        {"phase": "P3-RL-Smoke", "duration_h": 1.0,
         "steps": ["Step 5: RL smoke (GRPO R0, 10 iters)"],
         "gates": ["10 iters complete", "Reward > 0", "Loss finite", "GPU stable"],
         "decision": "If smoke fails → debug",
         "milestone": "Smoke PASS"},
        {"phase": "P4-RL-Full", "duration_h": 48.0,
         "steps": ["Step 6: Full RL (GRPO R0, 2000 steps)", "P1 medium(144,0-500)", "P2 +high(68,500-1000)",
                   "P3 +low(252,1000-2000)", "Checkpoint every 200"],
         "gates": ["Reward >base+0.1 by 500", "KL<1.0", "Entropy>0.01", "Cheat<5%"],
         "decision": "If stagnant → adjust LR/curriculum",
         "milestone": "M1-smoke: RL complete"},
        {"phase": "P5-Eval", "duration_h": 8.0,
         "steps": ["Eval RL ckpt 158 tasks 5-run", "Paired McNemar vs baseline"],
         "gates": ["5-run mean±std", "p-value computed"],
         "milestone": "M1-surrogate: Eval done"},
        {"phase": "P6-Analysis", "duration_h": 2.0,
         "steps": ["Aggregate", "D1-D6 before/after", "Failure mode shifts", "Final report"],
         "gates": ["Report complete"],
         "milestone": "Campaign complete"},
    ]
    t = t0
    tlp = []
    th = 0
    for ph in phases:
        s, e = t, t + timedelta(hours=ph["duration_h"])
        t = e
        th += ph["duration_h"]
        tlp.append({**ph, "start": s.strftime("%m-%d %H:%M"), "end": e.strftime("%m-%d %H:%M"), "cumulative_h": th})
    return {"gpu_status": gpu_status, "t0": t0.strftime("%Y-%m-%d %H:%M"), "total_duration_h": th, "phases": tlp}


# === 3. FROZEN CONFIGS ===
def build_frozen_configs():
    return {
        "sft_recipe": {
            "name": "BaiZe SFT v1.0 (frozen 2026-11-09)",
            "data_mixture": {"agent": {"source": "UltraData-SFT-Agent-2609", "weight_pct": 50, "tokens": "~5.97B"},
                             "general": {"source": "UltraData-SFT-2605", "weight_pct": 30, "tokens": "~18.89B"},
                             "pyaether": {"source": "sft_pyaether_v5.parquet", "weight_pct": 20, "tokens": "~0.5M"}},
            "hyperparams": {"context_len": 16384, "gbs": 128, "mbs": 1, "iters": 3000, "warmup": 100,
                            "decay": 300, "lr": "2e-5", "min_lr": "1e-6", "save_interval": 300, "ft_mode": "full", "tool_traces": True},
            "rationale": {"context_len": "R60: 16K captures 82%; R61: 32K infeasible", "data_mix": "R79: MC 18000 trials optimal",
                          "lr": "Standard SFT LR for 2B", "iters": "3000x128=384K samples"},
            "gates": {"pre": "Contamination pass + ckpt available", "mid": "Loss down at 300; no NaN at 600",
                      "post": "Eval >=45%", "ckpt": "R87: best eval not last"}},
        "rl_recipe": {
            "name": "BaiZe RL GRPO v1.0 (frozen 2026-11-09)",
            "hyperparams": {"group_size": 8, "ppo_mini_batch": 32, "ppo_micro": 4, "ppo_epochs": 2, "clip": 0.2,
                            "kl_coef": 0.02, "entropy": 0.001, "lr": "3e-6", "total_steps": 2000, "save_freq": 200,
                            "max_prompt": 8192, "max_response": 8192, "gpu_mem_util": 0.50, "n_gpus": 4},
            "reward_arms": {"R0": {"name": "Skeleton", "active": True, "desc": "API match + syntax, no exec"},
                            "R1": {"name": "Binary", "active": False, "desc": "Execute, pass/fail"},
                            "R2": {"name": "Partial", "active": False, "desc": "Partial credit"},
                            "R3": {"name": "R2+penalty", "active": False, "desc": "R2 + tool call penalty"},
                            "R4": {"name": "R3+legality", "active": False, "desc": "R3 + API legality bonus"}},
            "curriculum": {"phase1": {"steps": "0-500", "tasks": "medium(144)", "solvable": "96%"},
                           "phase2": {"steps": "500-1000", "tasks": "+high(68)", "solvable": "97.1%"},
                           "phase3": {"steps": "1000-2000", "tasks": "+low(252)", "solvable": "90%"}},
            "anti_cheat": {"vectors": ["partial_gaming(25)", "api_memorize(med)", "empty(low)", "syntax_only(low)"], "threshold": "<5%"},
            "rationale": {"group_size": "R92: G=8", "kl": "R18: 0.02; R80: >1.0 collapse", "clip": "R73: [0.1,0.3]",
                          "lr": "R92: 3e-6 DS stats", "curriculum": "R105: med->high->low"},
            "gates": {"pre": "SFT ckpt + contamination + sandbox", "mid500": "Reward>base+0.1; KL<1.0; cheat<5%", "post": "Eval 158; McNemar"}},
        "eval_protocol": {
            "name": "EDA-Eval-PyAether Frozen v1.0", "dataset": "158 tasks", "metric": "Pass@1", "runs": 5,
            "timeout": 2500, "parallel": "-p 8 -n", "single_trace": True, "stats": "mean±std; McNemar/bootstrap",
            "red_lines": ["158/Pass@1/2500s/single-trace/5-run/-p8-n FROZEN", "Contamination before every eval", "Report cheat_rate"]},
        "success_ladder": {
            "M0": {"pass1": "36%", "desc": "Baseline", "status": "measured"},
            "M1": {"pass1": "50%", "desc": "Tool protocol fixed", "status": "target_surrogate"},
            "M2": {"pass1": "65%", "desc": "+Domain+SFT", "status": "target_real"},
            "M3": {"pass1": "75%", "desc": "+RL", "status": "target_real"},
            "M4": {"pass1": "85%+", "desc": "Approaching DS", "status": "stretch"}},
    }


# === 4. MONITORING ===
def build_monitoring_spec():
    return {
        "metrics": [
            {"name": "reward_mean", "freq": "step", "alert": "flatline>50", "threshold": ">base+0.1 by 500"},
            {"name": "reward_std", "freq": "step", "alert": "->0", "threshold": ">0.01"},
            {"name": "kl_divergence", "freq": "step", "alert": ">1.0", "threshold": "<1.0"},
            {"name": "entropy", "freq": "step", "alert": "<0.001", "threshold": ">0.01"},
            {"name": "loss", "freq": "step", "alert": "NaN/Inf", "threshold": "finite"},
            {"name": "grad_norm", "freq": "step", "alert": ">10", "threshold": "<10"},
            {"name": "cheat_rate", "freq": "200 steps", "alert": ">5%", "threshold": "<5%"},
            {"name": "gpu_memory", "freq": "100 steps", "alert": "OOM", "threshold": "<46GB"},
            {"name": "step_time", "freq": "step", "alert": ">180s", "threshold": "<120s"},
            {"name": "crash_count", "freq": "continuous", "alert": ">3/200", "threshold": "0"},
        ],
        "alert_actions": {"reward_flatline": "Check curriculum; LR warmup restart", "kl_collapse": "kl_coef->0.05; LR->1e-6",
                          "entropy_degenerate": "entropy->0.01; temp->0.9", "cheat_high": "Switch to R3",
                          "grad_explosion": "LR-=50%", "oom": "micro_batch->2; seqs->12", "crash": "R82 auto-recovery"},
    }


# === 5. RECOVERY ===
def build_recovery_tree():
    return {"scenarios": [
        {"scenario": "SGLang won't start", "symptoms": "Port not responding",
         "fix": ["Kill stale procs", "Use cu124 venv", "gpu_mem_util=0.35"], "escalate": "Manual --debug launch"},
        {"scenario": "Baseline eval crashes", "symptoms": "Eval exits non-zero",
         "fix": ["-p 4", "timeout 3600s", "Single task first"], "escalate": "Check pyAether import"},
        {"scenario": "GRPO OOM", "symptoms": "CUDA OOM",
         "fix": ["micro_batch->2", "seqs->8", "ctx->8192", "grad_checkpointing"], "escalate": "Use LoRA"},
        {"scenario": "Reward all-zero", "symptoms": "reward_mean=0 >20 steps",
         "fix": ["Verify R70 parser", "Check entry_point", "R0 verbose"], "escalate": "Debug single sample"},
        {"scenario": "Training diverges", "symptoms": "Loss NaN/Inf",
         "fix": ["Resume last good ckpt", "LR-=50%", "grad_clip->2.0"], "escalate": "If 3x → stop, investigate data"},
        {"scenario": "72h exceeded", "symptoms": "Not converged",
         "fix": ["Stop at best ckpt", "Partial results", "Document lessons"], "escalate": "Report to operator"},
    ]}


# === EXPERIMENTS SECTION ===
def generate_experiments_section(checks, gpu_info, timeline, configs):
    total = len(checks)
    passed = sum(1 for c in checks if c.get("ok"))
    failed = total - passed
    failures = [c for c in checks if not c.get("ok")]
    fail_s = "; ".join(f"{c.get('label') or c.get('name','')}({c.get('category','')})" for c in failures) if failures else "无"
    go = "🟢 GO" if failed == 0 else "🟡 CONDITIONAL GO (仅GPU待释放)" if all(c.get("category") == "GPU" for c in failures) else "🔴 NO-GO"
    tl_rows = "".join(f"| {ph['phase']} | {ph['duration_h']}h | {ph['cumulative_h']:.1f}h | {ph.get('milestone', '-')} |\n" for ph in timeline["phases"])
    return f"""

## §R106: 启动日执行计划与配置冻结（2026-11-09 wake153 · 零 GPU · 纯计算+文件检查）

> **目标**：将 R1-R105 共 105 轮调研整合为可执行的启动日计划：go/no-go 检查、72h 时间线、冻结配置、监控规范、故障恢复决策树。

### 1. Go/No-Go 检查清单
- 检查总数：{total}，通过：{passed}（{passed/total*100:.0f}%），失败：{failed}
- 失败项：{fail_s}
- GPU：{gpu_info.get('free_count', 0)}/{gpu_info.get('total', 0)} free
- 判定：{go}

### 2. 72h 时间线
| 阶段 | 时长 | 累计 | 里程碑 |
|:--|--:|--:|:--|
{tl_rows}
总时长：{timeline['total_duration_h']:.1f}h（~3天）

### 3. 冻结配置摘要
**SFT v1.0**：Agent50/General30/PyAether20（R79），ctx=16384（R60），LR=2e-5，3000步全参。
**RL GRPO v1.0**：G=8, KL=0.02, clip=0.2, LR=3e-6, 2000步, R0→R2, 课程中→高→低（R105）。
**评测 v1.0**：158任务/Pass@1/5-run/2500s/-p8-n/单trace/McNemar。

### 4. 监控规范
10项指标（reward/kl/entropy/loss/grad/cheat/gpu/step_time/crash），7种告警动作。

### 5. 故障恢复
6种场景：SGLang启动/基线评测/GRPO OOM/奖励全零/训练发散/72h超限。

### 6. 研究溯源
SFT: R56/R79/R87/R89/R99-R101/R60-R61 | RL: R18/R47/R73/R92/R74/R83/R105/R13/R22/R85 | 反作弊: R75/R76 | 恢复: R80/R82/R81 | 评测: R72/R83/R84 | 工具: R69/R70/R71 | 就绪: R66/R78/R91-R96/R102 | 可解性: R97/R103/R104

### 7. 交付物
- `baize_posttrain_r106_launch_day_plan.py`（本脚本）
- `reports/report_posttrain_r106_launch_day_plan_zh.html`
- `r106_launch_day_plan.json`
- 本节（EXPERIMENTS §R106）
"""


def generate_html(checks, gpu_info, timeline, configs, monitoring, recovery):
    total = len(checks)
    passed = sum(1 for c in checks if c.get("ok"))
    failed = total - passed
    pass_rate = passed / total * 100 if total else 0
    cl, cc = "", ""
    for c in checks:
        cat = c.get("category", "")
        if cat != cc:
            cc = cat
            cl += f'<tr><td colspan="4" class="cat-h">{cat}</td></tr>\n'
        ok = c.get("ok", False)
        name = c.get("label") or c.get("name", "")
        detail = c.get("size_human", "") or c.get("detail", "") or c.get("error", "")
        cl += f'<tr class="{"ok" if ok else "fail"}"><td>{"✅" if ok else "❌"}</td><td>{name}</td><td><code>{c.get("path","")}</code></td><td>{detail}</td></tr>\n'
    tl = ""
    for ph in timeline["phases"]:
        ms = f'<span class="ms">🎯 {ph["milestone"]}</span>' if ph.get("milestone") else ""
        steps = "".join(f"<li>{s}</li>" for s in ph["steps"])
        gates = "".join(f"<li>{g}</li>" for g in ph["gates"])
        tl += f'<div class="phase"><h3>{ph["phase"]}({ph["duration_h"]}h)</h3><p>{ph["start"]}-{ph["end"]}({ph["cumulative_h"]:.1f}h)</p>{ms}<div class="cols"><div><ul>{steps}</ul></div><div><ul>{gates}</ul></div></div><p>{ph.get("decision","")}</p></div>'
    mh = "".join(f'<tr><td><code>{m["name"]}</code></td><td>{m["freq"]}</td><td>{m["alert"]}</td><td><code>{m["threshold"]}</code></td></tr>' for m in monitoring["metrics"])
    rh = "".join(f'<div class="scen"><h3>⚠️{s["scenario"]}</h3><p>{s["symptoms"]}</p><ul>{"".join(f"<li>{f}</li>" for f in s["fix"])}</ul><p>🔼{s["escalate"]}</p></div>' for s in recovery["scenarios"])
    sft, rl, ev = configs["sft_recipe"], configs["rl_recipe"], configs["eval_protocol"]
    go = "🟢 GO" if failed == 0 else ("🟡 CONDITIONAL GO (GPU pending)" if all(not c.get("ok") and c.get("category") == "GPU" for c in checks if not c.get("ok")) else "🔴 NO-GO")
    go_cls = "go" if failed == 0 else ("cond" if "CONDITIONAL" in go else "nogo")
    arms = ''.join(f'<tr><td><code>{k}</code></td><td>{v["name"]}</td><td>{"✅" if v["active"] else "⬜"}</td><td>{v["desc"]}</td></tr>' for k, v in rl['reward_arms'].items())
    curr = ''.join(f'<tr><td><strong>{k}</strong></td><td>{v["steps"]}</td><td>{v["tasks"]}</td><td>{v["solvable"]}</td></tr>' for k, v in rl['curriculum'].items())
    lad = ''.join(f'<tr><td><strong>{k}</strong></td><td><code>{v["pass1"]}</code></td><td>{v["desc"]}</td><td>{v["status"]}</td></tr>' for k, v in configs['success_ladder'].items())
    aa = ''.join(f'<li><strong>{k}：</strong>{v}</li>' for k, v in monitoring['alert_actions'].items())
    rlines = ''.join(f'<li>{r}</li>' for r in ev['red_lines'])
    ac = ''.join(f'<li>{v}</li>' for v in rl['anti_cheat']['vectors'])
    return _build_html_body(go, go_cls, passed, failed, pass_rate, timeline, cl, tl, sft, rl, ev, arms, curr, lad, aa, rlines, ac, mh, rh)


def _build_html_body(go, go_cls, passed, failed, pr, tl_info, cl, tl, sft, rl, ev, arms, curr, lad, aa, rlines, ac, mh, rh):
    css = "body{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}h2{color:#1a1a2e;margin-top:40px;border-left:4px solid #e94560;padding-left:12px}table{width:100%;border-collapse:collapse;margin:15px 0;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1)}th{background:#16213e;color:#fff;padding:10px;text-align:left}td{padding:8px;border-bottom:1px solid #e0e0e0;font-size:13px}tr.ok{background:#e8f5e9}tr.fail{background:#ffebee}.cat-h{background:#e0e0e0!important;font-weight:bold}.go-nogo{font-size:28px;font-weight:bold;text-align:center;padding:20px;border-radius:10px;margin:20px 0}.go{background:#c8e6c9;color:#2e7d32}.cond{background:#fff9c4;color:#f57f17}.nogo{background:#ffcdd2;color:#c62828}.phase{background:#fff;border-radius:8px;padding:15px;margin:15px 0;box-shadow:0 1px 3px rgba(0,0,0,.1);border-left:4px solid #0f3460}.ms{display:inline-block;background:#e94560;color:#fff;padding:3px 12px;border-radius:12px;font-size:13px}.cols{display:flex;gap:30px}.cols>div{flex:1}.scen{background:#fff;border-radius:8px;padding:15px;margin:15px 0;border-left:4px solid #ff9800}code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:12px}.summary{display:flex;gap:20px;margin:20px 0}.card{flex:1;background:#fff;border-radius:8px;padding:15px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.1)}.card .num{font-size:36px;font-weight:bold}.rl{background:#fff3e0;border:1px solid #ff9800;border-radius:8px;padding:15px;margin:15px 0}.rl h3{color:#e65100}ul{padding-left:20px}li{margin:3px;font-size:13px}.ft{text-align:center;color:#999;margin-top:40px;font-size:12px}"
    return f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R106</title><style>{css}</style></head><body><h1>R106: BaiZe Post-Train 启动日执行计划与配置冻结</h1><p>生成：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · 节点：{os.uname().nodename}</p><div class="go-nogo {go_cls}">{go}</div><div class="summary"><div class="card"><div class="num" style="color:#2e7d32">{passed}</div><div>通过</div></div><div class="card"><div class="num" style="color:#c62828">{failed}</div><div>失败</div></div><div class="card"><div class="num" style="color:#1565c0">{pr:.0f}%</div><div>通过率</div></div><div class="card"><div class="num" style="color:#7b1fa2">{tl_info["total_duration_h"]:.0f}h</div><div>总时长</div></div></div><p>GPU：{tl_info["gpu_status"]}</p><h2>1. Go/No-Go 检查清单</h2><table><tr><th>状态</th><th>项目</th><th>路径</th><th>详情</th></tr>{cl}</table><h2>2. 72h 时间线</h2><p>起点：{tl_info["t0"]} · 总时长：{tl_info["total_duration_h"]:.1f}h</p>{tl}<h2>3. SFT 冻结配置</h2><div class="phase"><h3>{sft["name"]}</h3><table><tr><th>参数</th><th>值</th><th>依据</th></tr><tr><td>数据配比</td><td>Agent50/Gen30/PA20</td><td>{sft["rationale"]["data_mix"]}</td></tr><tr><td>上下文</td><td><code>{sft["hyperparams"]["context_len"]}</code></td><td>{sft["rationale"]["context_len"]}</td></tr><tr><td>LR</td><td><code>{sft["hyperparams"]["lr"]}</code></td><td>{sft["rationale"]["lr"]}</td></tr><tr><td>迭代</td><td><code>{sft["hyperparams"]["iters"]}</code></td><td>{sft["rationale"]["iters"]}</td></tr></table><h4>门控</h4><ul><li>前：{sft["gates"]["pre"]}</li><li>中：{sft["gates"]["mid"]}</li><li>后：{sft["gates"]["post"]}</li></ul></div><h2>4. RL GRPO 冻结配置</h2><div class="phase"><h3>{rl["name"]}</h3><table><tr><th>参数</th><th>值</th><th>依据</th></tr><tr><td>G</td><td><code>{rl["hyperparams"]["group_size"]}</code></td><td>{rl["rationale"]["group_size"]}</td></tr><tr><td>KL</td><td><code>{rl["hyperparams"]["kl_coef"]}</code></td><td>{rl["rationale"]["kl"]}</td></tr><tr><td>Clip</td><td><code>{rl["hyperparams"]["clip"]}</code></td><td>{rl["rationale"]["clip"]}</td></tr><tr><td>LR</td><td><code>{rl["hyperparams"]["lr"]}</code></td><td>{rl["rationale"]["lr"]}</td></tr><tr><td>步数</td><td><code>{rl["hyperparams"]["total_steps"]}</code></td><td>256K samples</td></tr></table><h4>奖励臂</h4><table><tr><th>臂</th><th>名称</th><th>状态</th><th>描述</th></tr>{arms}</table><h4>课程</h4><table><tr><th>阶段</th><th>步数</th><th>任务</th><th>可解率</th></tr>{curr}</table><h4>反作弊</h4><ul>{ac}<li>阈值：{rl["anti_cheat"]["threshold"]}</li></ul></div><h2>5. 评测协议</h2><div class="phase"><table><tr><th>参数</th><th>值</th></tr><tr><td>数据集</td><td><code>{ev["dataset"]}</code></td></tr><tr><td>指标</td><td><code>{ev["metric"]}</code></td></tr><tr><td>运行</td><td><code>{ev["runs"]}-run</code></td></tr><tr><td>超时</td><td><code>{ev["timeout"]}s</code></td></tr><tr><td>统计</td><td>{ev["stats"]}</td></tr></table></div><div class="rl"><h3>🚨 红线</h3><ul>{rlines}</ul></div><h2>6. 成功阶梯</h2><table><tr><th>里程碑</th><th>Pass@1</th><th>含义</th><th>状态</th></tr>{lad}</table><h2>7. 实时监控</h2><table><tr><th>指标</th><th>频率</th><th>告警</th><th>阈值</th></tr>{mh}</table><ul>{aa}</ul><h2>8. 故障恢复</h2>{rh}<h2>9. 研究溯源</h2><table><tr><th>组件</th><th>来源</th></tr><tr><td>SFT</td><td>R56/R79/R87/R99-R101/R60-R61</td></tr><tr><td>RL</td><td>R18/R47/R73/R92/R105</td></tr><tr><td>反作弊</td><td>R75/R76</td></tr><tr><td>恢复</td><td>R80/R82/R81</td></tr><tr><td>评测</td><td>R72/R83/R84</td></tr><tr><td>就绪</td><td>R66/R78/R91-R96/R102</td></tr><tr><td>可解性</td><td>R97/R103/R104</td></tr></table><div class="ft">R106 · {datetime.now().strftime("%Y-%m-%d %H:%M")} · ⚠️替身RL不可迁移到白泽</div></body></html>'


def main():
    import argparse
    parser = argparse.ArgumentParser(description="R106: Launch-Day Execution Plan")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    print("=" * 60)
    print("R106: Launch-Day Execution Plan & Final Config Freeze")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Node: {os.uname().nodename}")
    print("=" * 60)
    print("\n[1/5] Go/No-Go checklist...")
    checks, gpu_info = build_checklist()
    total = len(checks)
    passed = sum(1 for c in checks if c.get("ok"))
    print(f"  Total: {total}, Passed: {passed}, Failed: {total - passed}")
    print(f"  GPU: {gpu_info.get('free_count', 0)}/{gpu_info.get('total', 0)} free")
    print("\n[2/5] 72h timeline...")
    timeline = build_timeline(gpu_info)
    print(f"  Total: {timeline['total_duration_h']:.1f}h")
    print("\n[3/5] Frozen configs...")
    configs = build_frozen_configs()
    print(f"  SFT: {configs['sft_recipe']['hyperparams']['iters']} iters")
    print(f"  RL: G={configs['rl_recipe']['hyperparams']['group_size']}, {configs['rl_recipe']['hyperparams']['total_steps']} steps")
    print("\n[4/5] Monitoring spec...")
    monitoring = build_monitoring_spec()
    print(f"  Metrics: {len(monitoring['metrics'])}")
    print("\n[5/5] Recovery tree...")
    recovery = build_recovery_tree()
    print(f"  Scenarios: {len(recovery['scenarios'])}")
    if args.html:
        print("\n[HTML] Generating report...")
        html = generate_html(checks, gpu_info, timeline, configs, monitoring, recovery)
        html_path = REPORT_DIR / "report_posttrain_r106_launch_day_plan_zh.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        print(f"  Written: {html_path} ({_human_size(html_path.stat().st_size)})")
    if args.json:
        print("\n[JSON] Generating JSON...")
        data = {"r106": {"timestamp": datetime.now().isoformat(), "checks": checks,
                         "gpu_info": gpu_info, "timeline": timeline, "configs": configs,
                         "monitoring": monitoring, "recovery": recovery}}
        json_path = RUN_DIR / "r106_launch_day_plan.json"
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"  Written: {json_path} ({_human_size(json_path.stat().st_size)})")
    print("\n[EXP] Appending EXPERIMENTS section...")
    section = generate_experiments_section(checks, gpu_info, timeline, configs)
    with open(EXP_FILE, "a", encoding="utf-8") as f:
        f.write(section)
    print(f"  Appended to {EXP_FILE}")
    print("\n" + "=" * 60)
    print(f"R106 COMPLETE: {passed}/{total} checks passed, GPU {gpu_info.get('free_count', 0)}/{gpu_info.get('total', 0)} free")
    print("=" * 60)


if __name__ == "__main__":
    main()
