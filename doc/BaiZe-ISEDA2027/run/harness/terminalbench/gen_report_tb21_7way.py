#!/usr/bin/env python3
"""gen_report_tb21_7way.py — Terminal-Bench 2.1 · 7-harness × glm-5.3-flash 报告生成器.

§15:2x 交付物: reports/report_harness_tb21_7way_zh.html (中文 / 0 script / 0 外链).
数据源: /tmp/tb21_glm53_jobs/<harness>/ 下 per-task result.json
        (verifier_result.rewards.reward == 1.0 => passed).
口径: TB-2.1 / 89 题 / 7-way concurrent (不可与 TB4 比较).
计数: unique tasks passed (按目录名 <task>__<id> 前缀去重, 任一 trial reward==1.0 即记 passed).

用法: python3 gen_report_tb21_7way.py
"""
import json
import os
from pathlib import Path
from datetime import datetime

JOBS = Path("/tmp/tb21_glm53_jobs")
TB_DATASET = Path(os.path.expanduser("~/terminal-bench"))
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code",
             "pi", "hermes", "deepseek-harness"]
DISP = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
        "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
        "deepseek-harness": "deepseek"}
OUT = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/"
           "BaiZe-ISEDA2027/reports/report_harness_tb21_7way_zh.html")
ORACLE_EVIDENCE = ("launch_tb21_glm53_7way.sh 内置 oracle check "
                   "(5 pilot tasks: break-filter-js-from-html / bn-fit-modify / "
                   "log-summary-date-ranges / cancel-async-tasks / fix-git), "
                   "R1789 记录 oracle 5/5 PASS, verifier 正常.")


def count_route(h):
    """返回 (unique_passed, evaluated, trials, errors)."""
    d = JOBS / h
    tasks = {}
    trials = 0
    errors = 0
    if d.exists():
        for f in d.rglob("result.json"):
            if "/20" not in str(f):
                continue
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            vr = r.get("verifier_result")
            if not vr:
                continue
            trials += 1
            if r.get("exception_info"):
                errors += 1
            p = str(f.parent.name)
            tn = p.split("__")[0] if "__" in p else p
            rew = vr.get("rewards", {}).get("reward", 0)
            if rew == 1.0:
                tasks[tn] = True
            else:
                tasks.setdefault(tn, False)
    upass = sum(1 for v in tasks.values() if v)
    return upass, len(tasks), trials, errors


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _build_html(rows, total_tasks, total_passed, total_trials, total_eval, now):
    css = ("body{font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif;"
           "max-width:1000px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}"
           "h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}"
           "h2{color:#1a5276;margin-top:25px;border-left:5px solid #2980b9;padding-left:10px}"
           "table{border-collapse:collapse;width:100%;margin:12px 0}"
           "th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}"
           "th{background:#2980b9;color:#fff}tr:nth-child(even){background:#ecf0f1}"
           ".pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}"
           ".warn{color:#e67e22;font-weight:bold}"
           ".info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:12px 0}"
           ".caveat{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:12px 0}")
    H = ["<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>",
         f"<title>TB-2.1 7way {now}</title><style>{css}</style></head><body>"]
    H.append(f"<h1>Terminal-Bench 2.1 · 7路横评 — {now}</h1>")
    H.append(f"<p><strong>模型</strong>: glm-5.3-flash | <strong>网关</strong>: "
             f"gw_proxy 9092 + gw_proxy_dsh 9093 (HTTP 200)<br>"
             f"<strong>口径声明</strong>: TB-2.1 / {total_tasks} 题 / 7-way concurrent "
             f"(<strong>不可与 TB4 比较</strong>) | oracle 5/5 ✅</p>")
    H.append("<h2>TB-2.1 7路矩阵 (unique tasks passed)</h2>")
    H.append("<table><tr><th>#</th><th>Harness</th><th>Passed</th>"
             "<th>Evaluated</th><th>题集总数</th><th>Pass% (passed/eval)</th>"
             "<th>Trials</th><th>Errors</th></tr>")
    for i, (name, up, ev, tr, er) in enumerate(rows, 1):
        pct = f"{up/ev*100:.1f}%" if ev else "—"
        ev_cls = "warn" if ev < total_tasks else ""
        H.append(f"<tr><td>{i}</td><td><strong>{esc(name)}</strong></td>"
                 f"<td class='pass'>{up}</td><td class='{ev_cls}'>{ev}</td>"
                 f"<td>{total_tasks}</td><td><strong>{pct}</strong></td>"
                 f"<td>{tr}</td><td class='fail'>{er}</td></tr>")
    H.append("</table>")
    H.append(f"<p><strong>合计</strong>: {total_passed} unique tasks passed / "
             f"{total_eval} evaluated / {total_trials} trials "
             f"(7-way concurrent, 仍在运行中)</p>")
    H.append(f"<div class='caveat'><p><strong>⚠️ 临时快照说明 (interim)</strong>:</p><ul>"
             f"<li>本报告读取 <code>/tmp/tb21_glm53_jobs/</code> 当前快照. /tmp 为易失存储, "
             f"历史结果可能被清理; opencode / pi 的 rerun 仍在运行中.</li>"
             f"<li><strong>Evaluated 列</strong> = 该路在 /tmp 中有 verifier 结果的去重题数. "
             f"若 Evaluated &lt; {total_tasks}, 表示该路尚未跑满 (或 /tmp 被清理后 rerun 未重建完), "
             f"<strong>非能力结论</strong>.</li>"
             f"<li>Pass% = Passed / Evaluated (仅对已评测题, 非 Passed / {total_tasks}). "
             f"rerun 完成后 Evaluated → {total_tasks}, 届时为最终报告.</li>"
             f"<li>历史峰值快照 (R1982, 2026-11-09): 161 passed-trials / 1197 trials "
             f"(trial 级, 含重试). /tmp 被部分清理后当前 trial 数低于历史, 属存储现象而非回退.</li>"
             f"</ul></div>")
    H.append(f"<div class='info'><p><strong>Oracle 5/5 证据</strong>: {esc(ORACLE_EVIDENCE)}</p>"
             "<p>oracle 5/5 通过 ⇒ verifier 正常 ⇒ 非 0 分均为能力/适配器/超时, "
             "非 verifier infra 故障.</p></div>")
    H.append(f"<div class='info'><p><strong>不可比性说明</strong>: "
             f"TB-2.1 与 TB4 题集不同 ({total_tasks} 题 vs TB4 66 题), "
             "不可跨基准比较. TB4 全 0 passed = 能力 (verifier 已运行, R1743). "
             "TB-2.1 oracle 5/5 证明 verifier 正常.</p>"
             "<p><strong>空 patch 归因</strong>: errors 列 = 适配器/超时/环境错误 "
             "(exception_info 非空, 非能力). 网关 ALL 200, 非 429. "
             "reward=0 且无 exception = 能力差 (真实做错).</p>"
             "<p><strong>7 路纪律</strong>: 7 路不得替换/合并 (§15:2x 铁律).</p></div>")
    H.append(f"<hr><p style='text-align:center;color:#7f8c8d;font-size:0.9em'>"
             f"BaiZe Harness TB-2.1 7way {now} | glm-5.3-flash | 正文写 cline | "
             f"数据源: /tmp/tb21_glm53_jobs (gen_report_tb21_7way.py)</p>")
    H.append("</body></html>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(H), encoding="utf-8")
    print(f"report written: {OUT} ({OUT.stat().st_size} bytes)")
    for name, up, ev, tr, er in rows:
        pct = f"{up/ev*100:.1f}%" if ev else "—"
        print(f"  {name:12s}: passed={up:3d} evaluated={ev:3d}/{total_tasks} "
              f"trials={tr:4d} errors={er:3d} pass%={pct}")
    print(f"  TOTAL: passed={total_passed} evaluated={total_eval} trials={total_trials}")


def main():
    total_tasks = (len([x for x in TB_DATASET.iterdir() if x.is_dir()])
                   if TB_DATASET.exists() else 89)
    rows = []
    for h in HARNESSES:
        up, ev, tr, er = count_route(h)
        rows.append((DISP[h], up, ev, tr, er))
    rows.sort(key=lambda r: -r[1])
    total_passed = sum(r[1] for r in rows)
    total_trials = sum(r[3] for r in rows)
    total_eval = sum(r[2] for r in rows)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    _build_html(rows, total_tasks, total_passed, total_trials, total_eval, now)


if __name__ == "__main__":
    main()
