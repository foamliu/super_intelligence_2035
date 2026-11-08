#!/usr/bin/env python3
"""baize_posttrain_v2_consistency_audit.py — R49: Cross-check ALL posttrain
scripts/configs for stale v1 references and v2 config consistency.

R49 (2026-11-08): R47 created v2 config fixing 5 critical bugs, and updated
rl_grpo.sh to use v2. But preflight_check.sh and day1_runbook.sh were left
referencing v1. This script scans ALL baize_posttrain_*.sh / *.py / *.yaml
files for stale v1 references and v2 config correctness.

Usage:
    python3 baize_posttrain_v2_consistency_audit.py            # Full audit
    python3 baize_posttrain_v2_consistency_audit.py --json     # JSON output
    python3 baize_posttrain_v2_consistency_audit.py --html     # HTML report
"""
from __future__ import annotations
import os, re, sys, json, yaml
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()

R47_BUGS = {
    "BUG1": {"desc": "custom_reward_function must be TOP-LEVEL",
             "check": lambda c: "custom_reward_function" in c},
    "BUG2": {"desc": "algorithm.adv_estimator must be 'grpo'",
             "check": lambda c: c.get("algorithm",{}).get("adv_estimator")=="grpo"},
    "BUG3": {"desc": "Group size must be rollout.n (not algorithm.group_size)",
             "check": lambda c: c.get("actor_rollout_ref",{}).get("rollout",{}).get("n",0)>=4},
    "BUG4": {"desc": "multi_turn must be nested dict (not bool)",
             "check": lambda c: isinstance(c.get("actor_rollout_ref",{}).get("rollout",{}).get("multi_turn"),dict)},
    "BUG5": {"desc": "tool_config must be multi_turn.tool_config_path",
             "check": lambda c: "tool_config_path" in c.get("actor_rollout_ref",{}).get("rollout",{}).get("multi_turn",{})},
}


def scan_stale_v1_refs():
    findings = []
    pattern = re.compile(r'baize_posttrain_rl_verl_config\.yaml(?!_)')
    for ext in ("*.sh", "*.py"):
        for f in SCRIPT_DIR.glob(ext):
            if not f.name.startswith("baize_posttrain_"):
                continue
            try:
                for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                    if pattern.search(line) and not (line.strip().startswith("#") and "v2" in line):
                        findings.append({"file": f.name, "line": i, "content": line.strip()})
            except Exception:
                pass
    return findings


def audit_v2_config():
    v2 = SCRIPT_DIR / "baize_posttrain_rl_verl_config_v2.yaml"
    if not v2.exists():
        return {"error": "v2 config not found"}
    try:
        cfg = yaml.safe_load(v2.read_text())
    except Exception as e:
        return {"error": str(e)}
    results = {}
    all_pass = True
    for bid, info in R47_BUGS.items():
        p = info["check"](cfg)
        results[bid] = {"desc": info["desc"], "passed": p}
        if not p: all_pass = False
    results["rollout_sglang"] = {"desc": "rollout.name=sglang (R9)",
        "passed": cfg.get("actor_rollout_ref",{}).get("rollout",{}).get("name")=="sglang"}
    results["auto_fallback"] = {"desc": "auto_fallback=true (R22)",
        "passed": cfg.get("custom_reward_function",{}).get("reward_kwargs",{}).get("auto_fallback") is True}
    results["flash_attn"] = {"desc": "attn_implementation=flash_attention_2 (R35)",
        "passed": cfg.get("actor_rollout_ref",{}).get("model",{}).get("override_config",{}).get("attn_implementation")=="flash_attention_2"}
    results["n_gpus"] = {"desc": "trainer.n_gpus_per_node=4 (R47)",
        "passed": cfg.get("trainer",{}).get("n_gpus_per_node")==4}
    results["_all_pass"] = all_pass
    return results


def scan_script_config_refs():
    refs = []
    for f in sorted(SCRIPT_DIR.glob("baize_posttrain_*.sh")):
        content = f.read_text(errors="replace")
        v2 = len(re.findall(r'baize_posttrain_rl_verl_config_v2\.yaml', content))
        v1 = len(re.findall(r'baize_posttrain_rl_verl_config\.yaml(?!_)', content))
        st = "OK" if v2 > 0 and v1 == 0 else ("MIXED" if v2 > 0 and v1 > 0 else ("V1_ONLY" if v1 > 0 else "NONE"))
        refs.append({"file": f.name, "v2_refs": v2, "v1_refs": v1, "status": st})
    return refs


def check_reward_arm():
    grpo = (SCRIPT_DIR / "baize_posttrain_rl_grpo.sh").read_text(errors="replace")
    v2 = yaml.safe_load((SCRIPT_DIR / "baize_posttrain_rl_verl_config_v2.yaml").read_text())
    arm_m = re.search(r'REWARD_ARM=(\w+)', grpo)
    script_arm = arm_m.group(1) if arm_m else "unknown"
    config_arm = v2.get("custom_reward_function",{}).get("reward_kwargs",{}).get("arm","unknown")
    return {"script_arm": script_arm, "config_arm": config_arm, "consistent": script_arm == config_arm}


def check_wrapper():
    w = SCRIPT_DIR / "baize_posttrain_verl_wrapper.py"
    if not w.exists(): return {"exists": False}
    c = w.read_text(errors="replace")
    return {"exists": True, "single_turn": "Single-turn mode" in c,
            "multi_turn_patch": "MiniCPM5XMLDetector" in c,
            "verl_import": "verl.trainer.main_ppo" in c, "lines": len(c.splitlines())}


def check_launch():
    l = SCRIPT_DIR / "baize_posttrain_launch_11_9.sh"
    if not l.exists(): return {"exists": False}
    c = l.read_text(errors="replace")
    steps = {i: f"STEP {i}:" in c for i in range(7)}
    sm = re.search(r'--smoke.*--reward-arm\s+(\w+)', c)
    fm = re.search(r'STEP 6.*--reward-arm\s+(\w+)', c, re.DOTALL)
    return {"exists": True, "all_steps": all(steps.values()),
            "smoke_arm": sm.group(1) if sm else "N/A", "full_arm": fm.group(1) if fm else "N/A"}


def run_audit():
    a = {"timestamp": datetime.now().isoformat(), "stale_v1": scan_stale_v1_refs(),
         "v2_audit": audit_v2_config(), "script_refs": scan_script_config_refs(),
         "reward_arm": check_reward_arm(), "wrapper": check_wrapper(), "launch": check_launch()}
    s = {"stale_v1_count": len(a["stale_v1"]),
         "v2_ok": a["v2_audit"].get("_all_pass", False),
         "arm_ok": a["reward_arm"]["consistent"],
         "wrapper_ok": a["wrapper"].get("exists") and a["wrapper"].get("verl_import"),
         "launch_ok": a["launch"].get("all_steps", False)}
    s["overall"] = "GO" if all([s["stale_v1_count"]==0, s["v2_ok"], s["arm_ok"], s["wrapper_ok"], s["launch_ok"]]) else "NO-GO"
    a["summary"] = s
    return a


def print_report(a):
    s = a["summary"]
    print("=" * 60)
    print(f"  R49 v2 Consistency Audit — {s['overall']}")
    print("=" * 60)
    print(f"\n1. Stale v1 refs: {s['stale_v1_count']}")
    for r in a["stale_v1"]:
        print(f"   X {r['file']}:{r['line']} — {r['content']}")
    if not a["stale_v1"]: print("   OK — no stale v1 refs")
    print(f"\n2. v2 Config R47 Fixes:")
    for k, v in a["v2_audit"].items():
        if k.startswith("_"): continue
        if isinstance(v, dict) and "passed" in v:
            print(f"   {'OK' if v['passed'] else 'FAIL'} {k}: {v['desc']}")
    print(f"\n3. Script->Config refs:")
    for r in a["script_refs"]:
        print(f"   {r['status']:8s} {r['file']}: v2={r['v2_refs']}, v1={r['v1_refs']}")
    ra = a["reward_arm"]
    print(f"\n4. Reward arm: script={ra['script_arm']}, config={ra['config_arm']}, consistent={ra['consistent']}")
    w = a["wrapper"]
    print(f"\n5. Wrapper: exists={w.get('exists')}, verl_import={w.get('verl_import')}, lines={w.get('lines')}")
    l = a["launch"]
    print(f"\n6. Launch: all_steps={l.get('all_steps')}, smoke={l.get('smoke_arm')}, full={l.get('full_arm')}")
    print(f"\n{'='*60} OVERALL: {s['overall']} {'='*60}")


def gen_html(a):
    s = a["summary"]
    oc = "#28a745" if s["overall"]=="GO" else "#dc3545"
    stale_parts = []
    for r in a["stale_v1"]:
        stale_parts.append("<tr><td>%s</td><td>%s</td><td><code>%s</code></td></tr>" % (r["file"], r["line"], r["content"]))
    stale_rows = "".join(stale_parts) or '<tr><td colspan=3 style="color:#28a745">无残留</td></tr>'
    bug_parts = []
    for k, v in a["v2_audit"].items():
        if k.startswith("_") or not isinstance(v, dict) or "passed" not in v:
            continue
        color = "#28a745" if v["passed"] else "#dc3545"
        icon = "PASS" if v["passed"] else "FAIL"
        bug_parts.append("<tr><td>%s</td><td>%s</td><td style='color:%s'>%s</td></tr>" % (k, v["desc"], color, icon))
    bug_rows = "".join(bug_parts)
    scr_parts = []
    for r in a["script_refs"]:
        scr_parts.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (r["file"], r["v2_refs"], r["v1_refs"], r["status"]))
    scr_rows = "".join(scr_parts)
    ra = a["reward_arm"]
    w = a["wrapper"]
    l = a["launch"]
    arm_icon = "YES" if ra["consistent"] else "NO"
    w_exists = "YES" if w.get("exists") else "NO"
    w_import = "YES" if w.get("verl_import") else "NO"
    l_steps = "YES" if l.get("all_steps") else "NO"
    ts = a["timestamp"]
    overall = s["overall"]
    stale_cnt = s["stale_v1_count"]
    ra_sa = ra["script_arm"]
    ra_ca = ra["config_arm"]
    w_lines = w.get("lines")
    l_sm = l.get("smoke_arm")
    l_fm = l.get("full_arm")
    return """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R49 v2 Consistency Audit</title>
<style>body{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;background:#f8f9fa}
h1{border-bottom:3px solid %s}table{border-collapse:collapse;width:100%%;background:white;margin:10px 0}
th,td{border:1px solid #dee2e6;padding:8px}th{background:#e9ecef}
.box{display:inline-block;padding:15px 30px;border-radius:8px;color:white;font-size:1.5em;font-weight:bold;background:%s;margin:10px 0}
.note{background:#d1ecf1;border-left:4px solid #17a2b8;padding:10px;margin:10px 0}</style></head>
<body><h1>R49: v2 Config Propagation Consistency Audit</h1>
<p>Time: %s</p>
<div class="box">%s</div>
<div class="note">Surrogate RL results are NOT transferable to BaiZe.</div>
<h2>1. Stale v1 References (%s found)</h2>
<table><tr><th>File</th><th>Line</th><th>Content</th></tr>%s</table>
<h2>2. v2 R47 Bug Fix Verification</h2>
<table><tr><th>Bug</th><th>Description</th><th>Status</th></tr>%s</table>
<h2>3. Script to Config References</h2>
<table><tr><th>Script</th><th>v2</th><th>v1</th><th>Status</th></tr>%s</table>
<h2>4. Reward Arm Consistency</h2>
<p>script=%s, config=%s, consistent=%s</p>
<h2>5. verl Wrapper</h2>
<p>exists=%s, verl_import=%s, lines=%s</p>
<h2>6. Launch Sequence</h2>
<p>all_steps=%s, smoke_arm=%s, full_arm=%s</p>
<h2>7. Conclusion</h2>
<div class="note"><p><b>Issue found</b>: preflight_check.sh and day1_runbook.sh referenced v1 config (5 known bugs).</p>
<p><b>Impact</b>: 11/9 preflight would validate wrong config, giving false sense of security.</p>
<p><b>Fix</b>: R49 changed both to v2, added v1 stale-ref detection + 8 R47 bug checks to day1 audit.</p></div>
<h2>8. 11/9 Operation Recommendations</h2>
<div class="note"><ol>
<li>After GPU release: run preflight, confirm "RL YAML v2"=PASS and "v1 stale ref"=PASS</li>
<li>Run day1_runbook --audit, confirm all 8 checks OK</li>
<li>Run v2_consistency_audit, confirm OVERALL=GO</li>
<li>All three green, then launch_11_9 --step 0-1</li></ol></div>
</body></html>""" % (
        oc, oc, ts, overall, stale_cnt, stale_rows, bug_rows, scr_rows,
        ra_sa, ra_ca, arm_icon,
        w_exists, w_import, w_lines,
        l_steps, l_sm, l_fm,
    )


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--html", action="store_true")
    args = p.parse_args()
    a = run_audit()
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False, default=str))
    elif args.html:
        html = gen_html(a)
        rd = SCRIPT_DIR.parent / "reports"
        rd.mkdir(exist_ok=True)
        out = rd / "report_posttrain_r49_v2_consistency_audit_zh.html"
        out.write_text(html, encoding="utf-8")
        print(f"HTML: {out} ({len(html)} bytes)")
    else:
        print_report(a)


if __name__ == "__main__":
    main()
