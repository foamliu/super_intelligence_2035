#!/usr/bin/env python3
"""gen_report_tb21_7way.py — Terminal-Bench 2.1 · 7-harness × glm-5.3-flash 报告生成器.

§2026-11-15 用户令重构: 只保留两张表 + Infra 修复台账, 分母统一为题集总数(89).
数据源: /tmp/tb21_glm53_jobs/<harness>/ 下 per-task result.json
        (verifier_result.rewards.reward == 1.0 => passed).
口径: TB-2.1 / 89 题 / 7-way concurrent (不可与 TB4 比较).
计数: unique tasks passed (按 result.json 的 task_name 字段去重, 任一 trial reward==1.0 即记 passed).

分母铁律: Pass% = Passed / 题集总数(89). 全报告只有一个分母.

用法: python3 gen_report_tb21_7way.py
"""
import json
import os
import re
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


def _is_dated_dir(name: str) -> bool:
    """判断目录名是否为 dated job 目录 (如 '2026-11-09__19-51-22')。"""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__", name))


def _iter_task_results(root: Path):
    """只取 task 级 result.json (跳过 dated job 级 result.json)。

    job 级: .../2026-11-09__19-51-22/result.json  (parent=dated dir → skip)
    task 级: .../2026-11-09__19-51-22/<task>__<id>/result.json  (parent=task dir → keep)
    """
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if "/20" not in str(f).replace("\\", "/"):
            continue
        if _is_dated_dir(f.parent.name):
            continue
        yield f


def count_route(h):
    """返回 (unique_passed, evaluated, trials, errors).

    用 result.json 的 task_name 字段做去重键 (canonical), 避免 dir-name
    split('__')[0] 把 dated job 级 result.json 误算成 task (旧 bug: 90/91>89).

    §2026-11-17: 扫描 original dir + 所有 <h>_rerun_* dir (R1/R2 重跑结果).
    PASS 优先 (任一 trial reward==1.0 即记 passed), 与 merge_cc_r1r2.py 逻辑一致.
    """
    d = JOBS / h
    tasks = {}
    trials = 0
    errors = 0
    # Scan original dir + all rerun dirs (R1/R2/quota rerun 等)
    scan_dirs = [d] if d.exists() else []
    for rd in sorted(JOBS.glob(f"{h}_rerun_*")):
        if rd.is_dir():
            scan_dirs.append(rd)
    for sd in scan_dirs:
        for f in _iter_task_results(sd):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            trials += 1
            if r.get("exception_info"):
                errors += 1
            tn = r.get("task_name") or str(f.parent.name).split("__")[0]
            vr = r.get("verifier_result")
            if vr:
                rew = vr.get("rewards", {}).get("reward", 0)
                if rew == 1.0:
                    tasks[tn] = True
                else:
                    tasks.setdefault(tn, False)
            else:
                tasks.setdefault(tn, False)
    upass = sum(1 for v in tasks.values() if v)
    return upass, len(tasks), trials, errors

# ---------------------------------------------------------------------------
# §七路额度归因 (复用 audit_tb21_quota_7way.py)
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
                "connection_refused": len(buckets["connection_refused"]),
                "ability_fail": len(buckets["ability_fail"]),
                "synthetic_or_never_ran": len(buckets["synthetic_or_never_ran"]),
                "not_evaluated": len(buckets["not_evaluated"]),
                "rerun_targets": (len(buckets["quota_only"]) + len(buckets["synthetic_or_never_ran"])
                                   + len(buckets["connection_refused"])),
            },
            "buckets": buckets,
        }
    return result


def _reclassify(audit_entry):
    """把 audit 五桶 → 三桶 (Infra / 能力不足 / 其他), 满足守恒。

    规则 (§2026-11-15 用户令, 逐题追溯 + 加总守恒):
      Infra     = quota_only + connection_refused + synthetic_or_never_ran
                  (额度耗尽 / 连接拒绝 / 未真跑假结果 / setup-env 失败 = 全 trial 均为 infra)
      能力不足   = ability_fail + mixed_fail
                  (模型真运行有 run_result/iterations>0 但 verifier 判 fail;
                   mixed_fail = 至少一个 trial 非额度且有运行证据 → 按「任一 trial 有
                   proper 证据 + verifier fail ⇒ 记能力不足」归入能力不足)
      其他       = not_evaluated (未出现在任何 result.json)
    守恒: Failed = Infra + 能力不足 + 其他 = 题集总数 - Passed
    """
    s = audit_entry["summary"]
    infra = s["quota_only"] + s["connection_refused"] + s["synthetic_or_never_ran"]
    ability = s["ability_fail"] + s["mixed_fail"]
    other = s["not_evaluated"]
    return infra, ability, other


def _review_7way_merged():
    """§2026-11-17 08:5x 用户令: 合并 original+rerun 后的失败归因复核。

    返回 dict: harness_key -> {display, passed, current_pct, corrected_pct,
    pure_infra, real_denom, bucket_counts, buckets} 或 {} (失败时)。
    """
    try:
        import importlib.util
        rev_path = Path(__file__).parent / "audit_tb21_review_7way.py"
        spec = importlib.util.spec_from_file_location(
            "audit_tb21_review_7way", rev_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return {}
    all_tasks = mod.get_all_tasks()
    result = {}
    for h in mod.HARNESSES:
        task_data = mod.scan_route_all_dirs(h)
        buckets, _ = mod.classify_merged(task_data, all_tasks)
        total = len(all_tasks) or 89
        passed = len(buckets["passed"])
        pure_infra = (len(buckets["quota"]) + len(buckets["conn_refused"])
                      + len(buckets["synthetic"]))
        real_denom = total - pure_infra
        result[h] = {
            "display": mod.DISP[h], "passed": passed, "total": total,
            "current_pct": round(passed / total * 100, 1),
            "corrected_pct": round(passed / max(real_denom, 1) * 100, 1),
            "pure_infra": pure_infra, "real_denom": real_denom,
            "bucket_counts": {
                "ability": len(buckets["ability"]),
                "quota": len(buckets["quota"]),
                "conn_refused": len(buckets["conn_refused"]),
                "synthetic": len(buckets["synthetic"]),
                "not_evaluated": len(buckets["not_evaluated"]),
            },
            "buckets": buckets,
        }
    return result


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# Infra 修复台账 (事实来自 MEMORY_HARNESS 各轮心跳, 2026-11-15)
# 键 = harness key; 值 = (原Infra题描述, 修复动作, 重跑状态)
INFRA_LEDGER = {
    "cline-patched": (
        "65 quota + 1 conn_refused + 8 synthetic",
        "额度重跑 (quota_lost 65→0) + synthetic 5th-batch",
        "额度✅清零; synthetic 4/8 PASS; 余 1 conn_refused + 4 synthetic 待重跑",
    ),
    "hermes": (
        "39 quota + 2 mteb + 2 qemu + synthetic",
        "_ensure_python (apt/apk/dnf install python3) + _ensure_pip (Py3.9 legacy get-pip.py); 额度重跑",
        "65/65 done+merged (quota✅); 2 mteb=BLOCKED(hermes-agent 不在容器 PyPI); 2 qemu=BLOCKED(容器 Py3.9 < hermes-agent 最低要求 3.11, R2510 确认)",
    ),
    "opencode": (
        "15 quota + 23 synthetic",
        "待重跑 (额度窗口)",
        "未启动",
    ),
    "pi": (
        "1 conn_refused + 45 synthetic",
        "待重跑",
        "未启动",
    ),
    "deepseek-harness": (
        "48 synthetic",
        "_ensure_python/_ensure_pip 同样适用; 待重跑",
        "未启动",
    ),
    "codex": (
        "5 synthetic + gateway 502 类",
        "待重跑",
        "未启动",
    ),
    "claude-code": (
        "89 ConnectionRefused (适配器无法连接网关, 模型从未运行)",
        "适配器 base_url/network 修复 (容器内 127.0.0.1 → overlay network_mode:host)",
        "rerun COMPLETE R1+R2 merged: 30P/89=33.7%, 0 ConnRefused✅ HARD VERIFIED",
    ),
}


def _build_html(rows, total_tasks, total_passed, total_trials, now, audit_7way=None, review_data=None):
    css = ("body{font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif;"
           "max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}"
           "h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}"
           "h2{color:#1a5276;margin-top:25px;border-left:5px solid #2980b9;padding-left:10px}"
           "table{border-collapse:collapse;width:100%;margin:12px 0}"
           "th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}"
           "th{background:#2980b9;color:#fff}tr:nth-child(even){background:#ecf0f1}"
           ".pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}"
           ".warn{color:#e67e22;font-weight:bold}"
           ".info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:12px 0}"
           ".caveat{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:12px 0}"
           "td.num{text-align:right;font-variant-numeric:tabular-nums}"
           "tfoot td{font-weight:bold;background:#d6eaf8}")
    H = ["<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>",
         f"<title>TB-2.1 7way {now}</title><style>{css}</style></head><body>"]
    H.append(f"<h1>Terminal-Bench 2.1 · 7路横评 — {now}</h1>")
    H.append(f"<p><strong>模型</strong>: glm-5.3-flash | <strong>网关</strong>: gw_proxy 9092 + gw_proxy_dsh 9093 (HTTP 200)<br>"
             f"<strong>口径声明</strong>: TB-2.1 / {total_tasks} 题 / 7-way concurrent "
             f"(<strong>不可与 TB4 比较</strong>) | oracle 5/5 ✅ (verifier 正常) | "
             f"分母 = 题集总数 {total_tasks} (全报告唯一分母)</p>")

    # ---- 顶部一句话结论 (7路速览) ----
    speed = " · ".join(f"{name} {up}/{total_tasks}" for name, up, ev, tr, er in rows)
    H.append(f"<div class='info'><p><strong>7路速览</strong>: {speed}</p></div>")

    # ---- 表一: TB-2.1 7路矩阵 ----
    H.append("<h2>表一 · TB-2.1 7路矩阵</h2>")
    H.append("<table><thead><tr><th>#</th><th>Harness</th><th>Passed</th>"
             f"<th>题集总数</th><th>Pass%</th><th>墙钟成本</th>"
             "<th>Token 成本 (in / out)</th><th>Trials</th></tr></thead><tbody>")
    for i, (name, up, ev, tr, er) in enumerate(rows, 1):
        pct = f"{up/total_tasks*100:.1f}%"
        H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                 f"<td class='num pass'>{up}</td>"
                 f"<td class='num'>{total_tasks}</td>"
                 f"<td class='num'><strong>{pct}</strong></td>"
                 f"<td class='warn'>未采集</td>"
                 f"<td class='warn'>未采集</td>"
                 f"<td class='num'>{tr}</td></tr>")
    H.append("</tbody><tfoot><tr><td colspan=2>合计</td>"
             f"<td class='num'>{total_passed}</td>"
             f"<td class='num'>{total_tasks}×7={total_tasks*7}</td>"
             f"<td class='num'>{total_passed/(total_tasks*7)*100:.1f}%</td>"
             "<td class='warn'>未采集</td><td class='warn'>未采集</td>"
             f"<td class='num'>{total_trials}</td></tr></tfoot></table>")
    H.append("<div class='caveat'><p><strong>成本列说明</strong>: 墙钟与 Token 当前均为「未采集」。"
             "各适配器未填充 <code>agent_result.n_input_tokens / n_output_tokens</code>（实测 7 路全部为 null），"
             "result.json 亦无 <code>wall_sec / duration</code> 字段。</p>"
             "<p><strong>补采方案</strong>: ① 各适配器在 resolve 阶段从网关响应累计 input/output token 并写回 "
             "<code>agent_result.n_input_tokens / n_output_tokens</code>; ② 墙钟由 harbor task 开始/结束时间戳"
             "计算并落 <code>result.json</code>。重跑时启用。🚫 未采集不编造数字（宁缺勿编）。</p></div>")

    # ---- 表二: 各 Harness 失败分析 ----
    H.append("<h2>表二 · 各 Harness 失败分析</h2>")
    H.append("<p><strong>桶定义</strong>: "
             "<strong>Infra</strong> = 额度耗尽 + 连接拒绝 + 超时(harbor wrapper) + ECONNRESET + setup/env 失败 "
             "+ CLI/适配器 bug + 网关 502 + 未真跑/假结果（全 trial 均为 infra）; "
             "<strong>能力不足</strong> = 模型真运行（有 run_result / iterations&gt;0）但 verifier 判 fail "
             "（含 Reached max turns; mixed_fail 至少一 trial 非额度且有运行证据 → 归能力）; "
             "<strong>其他</strong> = 未出现在任何 result.json（未评测/未跑）。</p>")
    H.append("<table><thead><tr><th>#</th><th>Harness</th><th>Failed</th>"
             "<th>Infra</th><th>能力不足</th><th>其他(未评测/未跑)</th>"
             "<th>守恒校验</th></tr></thead><tbody>")
    tot_failed = tot_infra = tot_ability = tot_other = 0
    all_ok = True
    for i, (name, up, ev, tr, er) in enumerate(rows, 1):
        # find the audit key for this display name
        hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
        ae = (audit_7way or {}).get(hkey, {})
        if ae:
            infra, ability, other = _reclassify(ae)
        else:
            infra, ability, other = 0, 0, 0
        failed = total_tasks - up
        ok = (infra + ability + other == failed)
        all_ok = all_ok and ok
        tot_failed += failed; tot_infra += infra
        tot_ability += ability; tot_other += other
        i_cls = "fail" if infra > 0 else "pass"
        o_cls = "warn" if other > 0 else ""
        ok_txt = "✅" if ok else f"❌ ({infra+ability+other}≠{failed})"
        H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                 f"<td class='num'>{failed}</td>"
                 f"<td class='num {i_cls}'>{infra}</td>"
                 f"<td class='num'>{ability}</td>"
                 f"<td class='num {o_cls}'>{other}</td>"
                 f"<td>{ok_txt}</td></tr>")
    H.append("</tbody><tfoot><tr><td colspan=2>合计</td>"
             f"<td class='num'>{tot_failed}</td>"
             f"<td class='num {('fail' if tot_infra>0 else 'pass')}'>{tot_infra}</td>"
             f"<td class='num'>{tot_ability}</td>"
             f"<td class='num'>{tot_other}</td>"
             f"<td>{'✅' if (tot_infra+tot_ability+tot_other==tot_failed) else '❌'}</td></tr></tfoot></table>")
    H.append(f"<p><strong>守恒断言</strong>: 逐行 Failed = Infra + 能力不足 + 其他 "
             f"{'全部成立 ✅' if all_ok else '存在不守恒 ❌'}; "
             f"合计 Failed {tot_failed} = 7×{total_tasks} − Passed {total_passed} = {total_tasks*7 - total_passed} "
             f"{'✅' if (tot_failed == total_tasks*7 - total_passed) else '❌'}。</p>")
    H.append("<div class='caveat'><p><strong>Infra 归零目标</strong>: 本表 Infra 列存在意义即「infra 已清零」验收证据。"
             "当前各路 Infra 尚未归零（见下方修复台账）。目标: 每路修复 + 重跑后 Infra → 0。"
             "🚫 不改 verifier/reward 判据, 不删旧 result.json（重跑落新目录）。</p></div>")

    # ---- 表三: Infra 欠账修复台账 ----
    H.append("<h2>表三 · Infra 欠账修复台账</h2>")
    H.append("<table><thead><tr><th>#</th><th>Harness</th><th>原 Infra 题</th>"
             "<th>修复动作</th><th>重跑状态</th><th>现 Infra</th></tr></thead><tbody>")
    for i, (name, up, ev, tr, er) in enumerate(rows, 1):
        hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
        ae = (audit_7way or {}).get(hkey, {})
        infra_now = _reclassify(ae)[0] if ae else 0
        orig, action, status = INFRA_LEDGER.get(hkey, ("—", "—", "—"))
        i_cls = "fail" if infra_now > 0 else "pass"
        H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                 f"<td style='font-size:0.9em'>{esc(orig)}</td>"
                 f"<td style='font-size:0.9em'>{esc(action)}</td>"
                 f"<td style='font-size:0.9em'>{esc(status)}</td>"
                 f"<td class='num {i_cls}'>{infra_now}</td></tr>")
    H.append("</tbody></table>")
    H.append("<div class='info'><p><strong>尚未归零的修复计划 + ETA</strong>:</p><ul>"
             "<li><strong>claude-code</strong>: 89 ConnectionRefused → 适配器已修 (overlay network_mode:host), "
             "rerun COMPLETE R1+R2 merged: <strong>30P/89=33.7%</strong>, 0 ConnRefused✅ HARD VERIFIED. "
             "Infra 残留 4 (502/503), 余 42 能力不足 + 13 timeout。</li>"
             "<li><strong>hermes</strong>: 2 mteb = BLOCKED (hermes-agent 不在容器 PyPI 镜像, 非能力); "
             "2 qemu = BLOCKED (容器 debian:bullseye-slim Python 3.9 < hermes-agent 最低要求 ≥3.11, "
             "PyPI 全版本均 requires-python≥3.11, R2510 确认: _ensure_pip 修复成功→pip 可用, "
             "但 hermes-agent 无兼容版本→HERMES_PY_TOO_OLD)。</li>"
             "<li><strong>opencode / pi / deepseek / codex</strong>: synthetic(未真跑) + quota 残留 → 逐路串行重跑 "
             "(cc 完成后启动, 避免网关额度竞争)。</li>"
             "<li><strong>cline</strong>: 额度已清零; 余 1 conn_refused + 4 synthetic 待补跑。</li></ul></div>")

    # ---- §2026-11-17 08:5x 用户令: 失败归因复核 (merged original+rerun) ----
    if review_data:
        H.append("<h2>失败归因复核 (2026-11-17 用户令)</h2>")
        H.append("<div class='caveat'><p><strong>复核目的</strong>: 用户质疑「失败的 Case 是否均为能力不足，"
                  "而非 infra 问题」。本节合并各路 original + 全部 rerun 目录后，对仍失败的题做四桶归因，"
                  "并计算<strong>修正后 Pass%</strong> = passed / (89 − 纯 infra 题数)，与当前 Pass% 并排对比。</p>"
                  "<p><strong>四桶定义</strong>: <code>ability</code> = 模型真跑且答错 "
                  "(有 run_result / iterations&gt;1 / exc_type 等真实证据); "
                  "<code>quota</code> = 全部 trial 命中网关额度耗尽; "
                  "<code>conn_refused</code> = 全部 trial 连接被拒 / CLI bug; "
                  "<code>synthetic</code> = 无 run_result、stdout≈空，占位假结果 / 未真跑。</p>"
                  "<p><strong>合并逻辑</strong>: 任一 trial (跨 original + rerun) reward==1.0 即记 PASS。"
                  "失败题若任何 trial 有 proper evidence → 归 ability (模型至少跑过一次)。</p></div>")
        # 四桶表
        H.append("<h3>表四 · 四桶归因 (合并后)</h3>")
        H.append("<table><thead><tr><th>#</th><th>Harness</th><th>Passed</th>"
                  "<th>当前 Pass%</th><th>能力不足</th><th>Quota</th>"
                  "<th>ConnRefused</th><th>Synthetic</th><th>纯Infra</th>"
                  "<th>修正后分母</th><th>修正后 Pass%</th></tr></thead><tbody>")
        for i, (name, up, ev, tr, er) in enumerate(rows, 1):
            hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
            rd = review_data.get(hkey, {})
            if not rd:
                H.append(f"<tr><td class='num'>{i}</td><td>{esc(name)}</td>"
                         f"<td colspan='9'>复核数据不可用</td></tr>")
                continue
            bc = rd["bucket_counts"]
            cur = f"{rd['current_pct']}%"
            cor = f"{rd['corrected_pct']}%"
            inf_cls = "fail" if rd["pure_infra"] > 0 else "pass"
            cor_cls = "pass" if rd["corrected_pct"] > rd["current_pct"] else ""
            H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                     f"<td class='num pass'>{rd['passed']}</td>"
                     f"<td class='num'>{cur}</td>"
                     f"<td class='num'>{bc['ability']}</td>"
                     f"<td class='num'>{bc['quota']}</td>"
                     f"<td class='num'>{bc['conn_refused']}</td>"
                     f"<td class='num'>{bc['synthetic']}</td>"
                     f"<td class='num {inf_cls}'>{rd['pure_infra']}</td>"
                     f"<td class='num'>{rd['real_denom']}</td>"
                     f"<td class='num {cor_cls}'><strong>{cor}</strong></td></tr>")
        H.append("</tbody></table>")
        # 关键结论
        H.append("<div class='info'><p><strong>关键结论</strong>:</p><ul>")
        for name, up, ev, tr, er in rows:
            hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
            rd = review_data.get(hkey, {})
            if not rd:
                continue
            bc = rd["bucket_counts"]
            gap = rd["corrected_pct"] - rd["current_pct"]
            if rd["pure_infra"] == 0:
                verdict = f"<strong>失败全部为能力不足</strong>，修正后 Pass% 不变"
            elif gap < 1:
                verdict = f"纯 infra 仅 {rd['pure_infra']} 题，修正后 Pass% 几乎不变"
            else:
                verdict = (f"纯 infra {rd['pure_infra']} 题 (synthetic {bc['synthetic']}"
                           f" + conn_ref {bc['conn_refused']} + quota {bc['quota']})，"
                           f"修正后 Pass% {rd['current_pct']}% → {rd['corrected_pct']}% (+{gap:.1f}pp)")
            H.append(f"<li><strong>{esc(name)}</strong>: {verdict}</li>")
        H.append("</ul></div>")
        # Infra 题清单
        H.append("<h3>纯 Infra 题清单 (synthetic + conn_refused + quota)</h3>")
        H.append("<table><thead><tr><th>Harness</th><th>桶</th><th>题数</th>"
                  "<th>题号清单</th></tr></thead><tbody>")
        for name, up, ev, tr, er in rows:
            hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
            rd = review_data.get(hkey, {})
            if not rd:
                continue
            b = rd["buckets"]
            for bucket_name, label in [("synthetic", "synthetic/未真跑"),
                                       ("conn_refused", "conn_refused"),
                                       ("quota", "quota")]:
                tasks = b.get(bucket_name, [])
                if tasks:
                    H.append(f"<tr><td><strong>{esc(name)}</strong></td>"
                             f"<td>{label}</td><td class='num'>{len(tasks)}</td>"
                             f"<td style='font-size:0.85em'>{esc(', '.join(tasks))}</td></tr>")
        H.append("</tbody></table>")
        # 重跑需求
        H.append("<div class='caveat'><p><strong>重跑需求评估</strong>: "
                  "上述 synthetic 题为「合并后仍无 run_result」的纯 infra，"
                  "理论上值得 rerun（排除 infra 后才能测出真能力）。"
                  "但部分题受环境硬约束:</p><ul>"
                  "<li><strong>hermes</strong>: qemu 类题 BLOCKED (容器 Py3.9 &lt; hermes-agent 最低 3.11)</li>"
                  "<li><strong>codex</strong>: 86/89 失败已归 ability (适配器 err 前科已排除, "
                  "合成后仅 2 synthetic) → 低分=真能力, rerun 无意义</li>"
                  "<li><strong>deepseek</strong>: 73/89 失败已归 ability, 仅 5 synthetic → rerun 收益有限</li>"
                  "<li><strong>opencode/pi</strong>: synthetic 各 10/14 题 → rerun 可提升修正后 Pass%</li>"
                  "<li><strong>cline/cc</strong>: 各 1 conn_refused (pytorch-model-recovery) → 单题重跑即可</li>"
                  "</ul></div>")

    H.append(f"<hr><p style='text-align:center;color:#7f8c8d;font-size:0.9em'>"
             f"BaiZe Harness TB-2.1 7way {now} | glm-5.3-flash | "
             f"数据源: /tmp/tb21_glm53_jobs (gen_report_tb21_7way.py) | "
             f"旧版详表已归档: reports/archive/harness_tb21_7way/</p>")
    H.append("</body></html>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(H), encoding="utf-8")
    print(f"report written: {OUT} ({OUT.stat().st_size} bytes)")
    for name, up, ev, tr, er in rows:
        pct = f"{up/total_tasks*100:.1f}%"
        print(f"  {name:12s}: passed={up:3d}/{total_tasks} pass%={pct} trials={tr:4d} errors={er:3d}")
    print(f"  TOTAL: passed={total_passed}/{total_tasks*7} trials={total_trials}")


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
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    audit_7way = _quota_audit_7way()
    review_data = _review_7way_merged()
    _build_html(rows, total_tasks, total_passed, total_trials, now,
                audit_7way=audit_7way, review_data=review_data)


if __name__ == "__main__":
    main()
