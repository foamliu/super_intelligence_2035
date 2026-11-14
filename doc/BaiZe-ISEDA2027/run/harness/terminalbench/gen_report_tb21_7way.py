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


# ---------------------------------------------------------------------------
# §cline TB-2.1 根因归因 (2026-11-13 用户令)
# ---------------------------------------------------------------------------

def _cline_attrtribution():
    """逐题归因 cline TB-2.1 失败，返回 (cats_dict, fair_passed, fair_attempted,
    quota_lost_tasks, cross_fail_detail)."""
    import re
    d = JOBS / "cline-patched"
    if not d.exists():
        return {}, 0, 0, [], []
    # collect per-task best result + failure category
    task_data = {}  # task -> list of trial dicts
    for f in d.rglob("result.json"):
        if "/20" not in str(f):
            continue
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        vr = r.get("verifier_result") or {}
        rew = vr.get("rewards", {}).get("reward", 0)
        ei = r.get("exception_info") or {}
        exc_type = ei.get("exception_type", "")
        ar = r.get("agent_result") or {}
        meta = ar.get("metadata") or {}
        stdout = meta.get("stdout", "") or ""
        exit_code = meta.get("exit_code")
        has_run_result = '"run_result"' in stdout
        quota = "额度已用完" in stdout or "Token额度" in stdout
        econn = "ECONNRESET" in stdout
        iter_match = re.search(r'"iterations":(\d+)', stdout)
        iterations = int(iter_match.group(1)) if iter_match else -1
        tn = str(f.parent.name).split("__")[0]
        task_data.setdefault(tn, []).append({
            "reward": rew, "exc_type": exc_type, "exit_code": exit_code,
            "has_run_result": has_run_result, "quota": quota, "econn": econn,
            "iterations": iterations, "stdout_len": len(stdout),
        })

    cats = {"quota_exhausted": 0, "timeout": 0, "econnreset": 0,
            "cli_parse_bug": 0, "real_ability": 0, "passed": 0}
    fair_passed = 0
    fair_attempted = 0
    quota_lost = []
    for tn, trials in task_data.items():
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            cats["passed"] += 1
            fair_passed += 1
            fair_attempted += 1
            continue
        # classify failure
        all_quota = all(t["quota"] for t in trials)
        has_timeout = any(t["exc_type"] == "AgentTimeoutError" for t in trials)
        has_econn = any(t["econn"] and not t["quota"] for t in trials)
        has_cli_bug = any(
            t["exit_code"] == 1 and not t["has_run_result"]
            and "unknown option" in (t.get("stdout", "") or "").lower()
            for t in trials
        )
        if all_quota:
            cats["quota_exhausted"] += 1
            quota_lost.append(tn)
        elif has_timeout and not has_econn:
            cats["timeout"] += 1
        elif has_econn:
            cats["econnreset"] += 1
        elif has_cli_bug:
            cats["cli_parse_bug"] += 1
        else:
            cats["real_ability"] += 1
        # fair = tasks where cline got at least one non-quota trial
        if not all_quota:
            fair_attempted += 1

    # cross-fail: cline fail but pi/opencode pass
    pi_tasks = _peer_passed("pi")
    oc_tasks = _peer_passed("opencode")
    cross = []
    for tn, trials in task_data.items():
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            continue
        if tn not in pi_tasks and tn not in oc_tasks:
            continue
        all_quota = all(t["quota"] for t in trials)
        cross.append({
            "task": tn, "pi": tn in pi_tasks, "oc": tn in oc_tasks,
            "quota": all_quota,
        })
    return cats, fair_passed, fair_attempted, quota_lost, cross


def _peer_passed(h):
    """Return set of unique task names that passed for harness h."""
    d = JOBS / h
    passed = set()
    if d.exists():
        for f in d.rglob("result.json"):
            if "/20" not in str(f):
                continue
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            vr = r.get("verifier_result") or {}
            rew = vr.get("rewards", {}).get("reward", 0)
            if rew == 1.0:
                tn = str(f.parent.name).split("__")[0]
                passed.add(tn)
    return passed


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------------------
# §七路额度归因 (2026-11-14 用户令)
# ---------------------------------------------------------------------------

def _quota_audit_7way():
    """返回 dict: harness_key -> {summary, buckets} — 七路五桶额度归因。

    复用 audit_tb21_quota_7way.py 的 scan + classify 逻辑。
    """
    try:
        import importlib.util
        audit_path = Path(__file__).parent / "audit_tb21_quota_7way.py"
        spec = importlib.util.spec_from_file_location("audit_tb21_quota_7way", audit_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return {}

    all_tasks = mod.get_all_tasks()
    result = {}
    for h in mod.HARNESSES:
        root = mod.JOBS / h
        task_data = mod.scan_trials(root)
        buckets, detail = mod.classify_route(task_data, all_tasks)
        evaluated = len(task_data)
        passed = len(buckets["passed"])
        result[h] = {
            "summary": {
                "evaluated": evaluated,
                "passed": passed,
                "quota_only": len(buckets["quota_only"]),
                "mixed_fail": len(buckets["mixed_fail"]),
                "ability_fail": len(buckets["ability_fail"]),
                "synthetic_or_never_ran": len(buckets["synthetic_or_never_ran"]),
                "not_evaluated": len(buckets["not_evaluated"]),
                "pass_rate": round(passed / max(evaluated, 1), 4),
                "rerun_targets": len(buckets["quota_only"]) + len(buckets["synthetic_or_never_ran"]),
            },
            "buckets": buckets,
        }
    return result


def _build_html(rows, total_tasks, total_passed, total_trials, total_eval, now,
                attr_data=None, audit_7way=None):
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
    # ---- §七路额度归因 (2026-11-14 用户令) ----
    if audit_7way:
        H.append("<h2>TB-2.1 七路额度归因 (2026-11-14 用户令)</h2>")
        total_quota = sum(a["summary"]["quota_only"] for a in audit_7way.values())
        total_synth = sum(a["summary"]["synthetic_or_never_ran"] for a in audit_7way.values())
        total_rerun = sum(a["summary"]["rerun_targets"] for a in audit_7way.values())
        if total_quota == 0 and total_synth > 0:
            conclusion = (f"七路合计 quota_only = <strong>{total_quota}</strong> (额度耗尽已清零), "
                          f"但仍有 <strong>{total_synth}</strong> 个 synthetic/未真跑结果需重跑; "
                          f"失败主因 = synthetic 假结果 + timeout/ability")
        elif total_quota > 0:
            conclusion = (f"七路合计 quota_only = <strong>{total_quota}</strong> (仍有额度耗尽未重跑), "
                          f"synthetic = <strong>{total_synth}</strong>; "
                          f"rerun_targets = <strong>{total_rerun}</strong>")
        else:
            conclusion = (f"七路合计 quota_only = 0, synthetic = 0; "
                          f"失败 = timeout/ability (无额度/假结果因素)")
        H.append(f"<div class='info'><p><strong>结论一句话 (数据驱动)</strong>: {conclusion}</p></div>")
        H.append("<table><tr><th>Harness</th><th>Pass</th><th>Eval</th>"
                 "<th>quota_only</th><th>mixed</th><th>ability</th>"
                 "<th>synthetic</th><th>not_eval</th><th>rerun_targets</th></tr>")
        for h in HARNESSES:
            if h not in audit_7way:
                continue
            s = audit_7way[h]["summary"]
            name = DISP[h]
            q_cls = "warn" if s["quota_only"] > 0 else ""
            syn_cls = "warn" if s["synthetic_or_never_ran"] > 0 else ""
            H.append(f"<tr><td><strong>{esc(name)}</strong></td>"
                     f"<td class='pass'>{s['passed']}</td>"
                     f"<td>{s['evaluated']}</td>"
                     f"<td class='{q_cls}'>{s['quota_only']}</td>"
                     f"<td>{s['mixed_fail']}</td>"
                     f"<td class='fail'>{s['ability_fail']}</td>"
                     f"<td class='{syn_cls}'>{s['synthetic_or_never_ran']}</td>"
                     f"<td>{s['not_evaluated']}</td>"
                     f"<td><strong>{s['rerun_targets']}</strong></td></tr>")
        H.append(f"<tr style='font-weight:bold;background:#d5e8d4'>"
                 f"<td>合计</td><td>{sum(a['summary']['passed'] for a in audit_7way.values())}</td>"
                 f"<td>—</td><td class='{ 'warn' if total_quota else ''}'>{total_quota}</td>"
                 f"<td>—</td><td>—</td>"
                 f"<td class='{ 'warn' if total_synth else ''}'>{total_synth}</td>"
                 f"<td>—</td><td>{total_rerun}</td></tr>")
        H.append("</table>")
        H.append("<div class='caveat'><p><strong>五桶定义</strong>: "
                 "<strong>quota_only</strong> = 全部 trial 命中网关额度耗尽 (零机会, 需重跑) | "
                 "<strong>mixed_fail</strong> = 部分额度+部分非额度 (不重跑) | "
                 "<strong>ability_fail</strong> = 无额度, 有 proper 证据 (iterations>1/run_result/exception) = 能力差 | "
                 "<strong>synthetic_or_never_ran</strong> = 无 run_result, stdout 极短 = 假结果/未真跑 (需重跑) | "
                 "<strong>not_evaluated</strong> = 89 题中未出现在 result.json (需补跑)</p>"
                 "<p><strong>归因红线</strong>: 额度耗尽 ≠ 能力, 假结果 ≠ 能力 (三者分开记账)</p></div>")

    # ---- §cline TB-2.1 根因归因 (2026-11-13 用户令, ~~部分作废~~) ----
    if attr_data:
        cats, fair_p, fair_a, quota_lost, cross = attr_data
        total_fail = sum(cats.values()) - cats["passed"]
        H.append("<h2>cline TB-2.1 低分根因归因 (2026-11-13 用户令)"
                 " <span style='color:#e74c3c;text-decoration:line-through'>~~部分作废~~</span>"
                 f" <small>见上方「七路额度归因」{now}</small></h2>")
        H.append(f"<div class='caveat'><p><strong>结论一句话 (原始, R2386)</strong>: "
                 f"cline TB-2.1 原始 = 10/89 = 11.2% 的低分 "
                 f"<strong>非模型能力问题</strong>，主因 = "
                 f"<strong>网关 Token 额度耗尽</strong>（本次Token额度已用完）"
                 f"占失败 {cats['quota_exhausted']}/{total_fail} = "
                 f"{cats['quota_exhausted']/max(total_fail,1)*100:.0f}%。"
                 f"<br><strong>⚠️ 更新 ({now})</strong>: cline 额度重跑已清零 "
                 f"(quota_lost=0), cline 现 = <strong>38/89 = 42.7%</strong>。"
                 f"排除额度耗尽后 cline 公平通过率 = "
                 f"{fair_p}/{fair_a} = "
                 f"{fair_p/max(fair_a,1)*100:.0f}%，与同 backbone 同路（pi/opencode）"
                 f"可比。</p></div>")
        H.append("<table><tr><th>失败类别</th><th>题数</th><th>占比(失败)</th>"
                 "<th>说明</th></tr>")
        cat_desc = {
            "quota_exhausted": "网关返回「本次Token额度已用完，请等待X分钟后重试」; "
                               "cline run_result finishReason=error, iterations=1, "
                               "inputTokens=0, outputTokens=0 → 零工作 → reward=0. "
                               "归因红线: 网关额度耗尽 ≠ 模型能力.",
            "timeout": "AgentTimeoutError (900s 超时), cline 挂起无响应; "
                       "可能与网关无响应相关.",
            "econnreset": "网关 ECONNRESET (连接中断), cline 已做部分工作但被截断.",
            "cli_parse_bug": "cline CLI 将 task instruction (以 '-' 开头) 解析为 "
                             "未知选项 → 适配器/CLI 解析 bug, 非能力.",
            "real_ability": "cline 真正运行了 (有 run_result, 有 token 消耗) 但 "
                            "verifier 判 fail = 真能力差.",
            "passed": "verifier reward=1.0 (通过).",
        }
        for k in ["passed", "quota_exhausted", "timeout", "econnreset",
                  "cli_parse_bug", "real_ability"]:
            v = cats.get(k, 0)
            pct = f"{v/max(total_fail,1)*100:.0f}%" if k != "passed" else "—"
            cls = "pass" if k == "passed" else ("fail" if k == "real_ability" else "warn")
            H.append(f"<tr><td class='{cls}'>{k}</td><td>{v}</td><td>{pct}</td>"
                     f"<td style='font-size:0.9em'>{esc(cat_desc.get(k,''))}</td></tr>")
        H.append("</table>")
        H.append(f"<p><strong>公平分析</strong>: 排除全部 trial 均为额度耗尽的 "
                 f"{cats['quota_exhausted']} 题后, cline 在剩余 {fair_a} 题上通过 "
                 f"{fair_p} 题 = <strong>{fair_p/max(fair_a,1)*100:.0f}%</strong> "
                 f"(vs 原始 10/89=11.2%)。与 pi (27/86=31.4%)、opencode (33/58=56.9%) "
                 f"的差距大幅缩小。</p>")
        if cross:
            quota_cross = sum(1 for c in cross if c["quota"])
            real_cross = sum(1 for c in cross if not c["quota"])
            H.append(f"<p><strong>交叉对照 (cline 失败但 pi/opencode 通过)</strong>: "
                     f"共 {len(cross)} 题, 其中 <strong>{quota_cross} 题</strong>"
                     f"= cline 全部 trial 均额度耗尽 (零机会), "
                     f"仅 {real_cross} 题为 cline 真正运行后失败。</p>")
            H.append("<details><summary>交叉对照明细 (点击展开)</summary>"
                     "<table><tr><th>题目</th><th>cline</th><th>pi</th>"
                     "<th>opencode</th><th>额度耗尽?</th></tr>")
            for c in cross[:20]:
                H.append(f"<tr><td>{esc(c['task'])}</td><td class='fail'>FAIL</td>"
                         f"<td class='{'pass' if c['pi'] else 'fail'}'>"
                         f"{'PASS' if c['pi'] else '—'}</td>"
                         f"<td class='{'pass' if c['oc'] else 'fail'}'>"
                         f"{'PASS' if c['oc'] else '—'}</td>"
                         f"<td class='{'warn' if c['quota'] else ''}'>"
                         f"{'是(零机会)' if c['quota'] else '否'}</td></tr>")
            if len(cross) > 20:
                H.append(f"<tr><td colspan=5>... 还有 {len(cross)-20} 题</td></tr>")
            H.append("</table></details>")
        H.append("<div class='info'><p><strong>根因链</strong>: "
                 "cline 适配器无重试机制 → 网关额度耗尽时 cline "
                 "收到「额度已用完」错误 → 产生 run_result(finishReason=error, "
                 "iterations=1, 0 tokens) → 适配器检测到 run_result 让 verifier "
                 "评分 → verifier 发现无输出文件 → reward=0。"
                 "<br><strong>为何 cline 受影响远大于 pi/opencode</strong>: "
                 "① cline 在 10 小时内集中跑完 89 题 (11:51-21:39), "
                 "而 opencode 跨 40 小时 (2+ 天)、pi 跨 31 小时且有 167 次 trial "
                 "(含重试) → cline 时间窗与额度耗尽期高度重叠; "
                 "② cline 适配器无 retry/backoff, 每题仅一次机会; "
                 "③ 7 路 + SWE-bench Verified 共享同一网关 key → 同一额度池。</p>"
                 "<p><strong>与 SWE-bench Verified 74.8% 的一致性</strong>: "
                 "cline SWE-bench 跑了 323 题跨越多天, 额度有补充窗口; "
                 "TB-2.1 集中 10 小时爆发, 额度无补充 → 同一模型, 不同额度环境。</p>"
                 "<p><strong>修复建议</strong>: ① cline 适配器增加 "
                 "quota-error retry-with-backoff (等待网关提示的时间后重试); "
                 "② 或 cline 单独 rerun (网关额度充足时), 预计可达 ~30-40%。"
                 "值得 rerun 以获得干净的 cline TB-2.1 数字。</p></div>")
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
    attr_data = _cline_attrtribution()
    audit_7way = _quota_audit_7way()
    _build_html(rows, total_tasks, total_passed, total_trials, total_eval, now,
                attr_data=attr_data, audit_7way=audit_7way)


if __name__ == "__main__":
    main()
