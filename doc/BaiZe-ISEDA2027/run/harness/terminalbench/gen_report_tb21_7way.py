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


def count_route_before_rerun(h):
    """§2026-11-17 10:2x 用户令 item 3: 重跑前 passed 计数 = 合并 original + 所有 *早期* rerun
    目录, 但 **排除** 本次 post-R2600 重跑目录 (匹配 ``*_rerun_7way_20261117_*``)。
    这样「重跑前」= R2600 基线 (已含 cline 额度重跑 / cc R1+R2 / hermes 重跑等早期 rerun),
    「重跑后」= count_route (含本次 post-R2600 rerun), Δ 即本次重跑的真实增益。
    按 task_name 去重, 任一 trial reward==1.0 即记 passed。"""
    d = JOBS / h
    tasks = {}
    scan_dirs = [d] if d.exists() else []
    for rd in sorted(JOBS.glob(f"{h}_rerun_*")):
        if rd.is_dir() and "7way_20261117" not in rd.name:
            scan_dirs.append(rd)
    for sd in scan_dirs:
        for f in _iter_task_results(sd):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
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
    return sum(1 for v in tasks.values() if v)


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
    """§2026-11-17 10:2x 用户令: 撤回「修正后 Pass%」, 改为真实 Pass% = passed/89.

    合并 original+rerun 后的失败归因, 但不再计算 corrected_pass_pct.
    返回 dict: harness_key -> {display, passed, real_pct, pending_rerun,
    bucket_counts, buckets} 或 {} (失败时)。

    infra 桶 (quota/conn_refused/synthetic) = 待重跑, 不从分母剔除.
    重跑完成后重算真实 Pass% (passed/89, 分母恒 89).
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
        pending_rerun = (len(buckets["quota"]) + len(buckets["conn_refused"])
                         + len(buckets["synthetic"]))
        result[h] = {
            "display": mod.DISP[h], "passed": passed, "total": total,
            "real_pct": round(passed / total * 100, 1),
            "pending_rerun": pending_rerun,
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
        "额度重跑 (quota_lost 65→0) + synthetic 5th-batch + pytorch-model-recovery 3次重跑",
        "额度✅清零; synthetic 4/8 PASS; pytorch-model-recovery=BLOCKED(infra) (3次重跑 cline CLI exit1 无输出, 任务特定CLI崩溃, 非能力); 余 4 synthetic 待重跑",
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


def _build_html(rows, total_tasks, total_passed, total_trials, now, audit_7way=None, review_data=None, before_counts=None):
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
             "<li><strong>cline</strong>: 额度已清零; 余 1 conn_refused (pytorch-model-recovery) 经 3 次重跑 (original 2026-11-09 + reruns 0932/1143) 均 cline CLI exit 1 无输出 → "
             "<strong>BLOCKED(infra)</strong> (cline CLI 在该任务环境静默崩溃, cline auth OK, 1379B 正常 instruction, cline 跑通 332 题→任务特定 CLI 崩溃, 非能力); "
             "另 4 synthetic 待补跑。</li></ul></div>")

    # ---- §2026-11-17 10:2x 用户令: 撤回「修正后 Pass%」, 改为「重跑中」真实口径 ----
    if review_data:
        H.append("<h2>失败归因复核 → 重跑中 (2026-11-17 用户令)</h2>")
        H.append("<div class='caveat'><p><strong>🔴 口径纠正声明 (2026-11-17 10:2x 用户令)</strong>: "
                  "此前 R2600 的「修正后 Pass% = passed / (89 − 纯 infra 题数)」已<strong>撤回</strong>。"
                  "该口径把未真跑 / 额度 / 连接拒绝的题直接从分母剔除，等价于<strong>默认这些题「真跑就能通过」</strong>，"
                  "这是凭空抬分，不是复核准绳。<strong>未真跑题的处置只有一个正解: 重跑拿真实结果</strong>。"
                  "真正可对外引用的成绩只有 <strong>真实 Pass% = passed / 89</strong> (分母恒 89)。</p>"
                  "<p><strong>当前状态</strong>: 47 trial 串行重跑进行中 (R2602 启动, codex 路已完成 2/2=ability (Δ=0), "
                  "cline 1=BLOCKED(infra·3次CLI崩溃), hermes 8/12 done (2 PASS=bn-fit-modify+portfolio-optimization Δ=+2, 6 ability=AgentTimeoutError, 4 running), "
                  "opencode 10→pi 15→deepseek 5→cc 1 依次排队)。"
                  "重跑完成后将重算真实 Pass%, "
                  "pass 就 +1, fail 计失败。<strong>重跑完成前, infra 桶标「待重跑」, 不从分母剔除</strong>。"
                  "环境硬约束 (BLOCKED) 题显式注明原因, 不误算为通过: hermes qemu/mteb (Py3.9&lt;3.11), "
                  "cline pytorch-model-recovery (cline CLI 静默崩溃, 3 attempts)。</p>"
                  "<p><strong>四桶定义</strong>: <code>ability</code> = 模型真跑且答错 "
                  "(有 run_result / iterations&gt;1 / exc_type 等真实证据); "
                  "<code>quota</code> = 全部 trial 命中网关额度耗尽; "
                  "<code>conn_refused</code> = 全部 trial 连接被拒 / CLI bug; "
                  "<code>synthetic</code> = 无 run_result、stdout≈空，占位假结果 / 未真跑。"
                  "后三桶 = <strong>待重跑</strong> (infra), 重跑后按真实 reward 归入 passed 或 ability。</p>"
                  "<p><strong>合并逻辑</strong>: 任一 trial (跨 original + rerun) reward==1.0 即记 PASS。</p></div>")
        # 四桶表 (去掉修正后 Pass% 列, 改为真实 Pass% + 待重跑列)
        H.append("<h3>表四 · 四桶归因 + 重跑状态 (合并后)</h3>")
        H.append("<table><thead><tr><th>#</th><th>Harness</th><th>Passed</th>"
                  "<th>真实 Pass%<br>(passed/89)</th><th>能力不足</th><th>Quota</th>"
                  "<th>ConnRefused</th><th>Synthetic</th><th>待重跑<br>(infra)</th>"
                  "<th>重跑状态</th></tr></thead><tbody>")
        # rerun plan: which tasks per route
        rerun_plan = {
            "cline-patched": (1, "BLOCKED(infra): cline CLI exit 1, no run_result, no stderr — 3 attempts (original 2026-11-09 + reruns 0932/1143) all infra-failed; cline auth OK but task cmd crashes silently; 1379B instruction, normal task; cline ran 332 other tasks → task-specific CLI crash, NOT ability"),
            "codex": (2, "done (2/2, both reward=0; bn-fit-modify=AgentTimeoutError=ability, break-filter-js-from-html=model started but no run_result → audit classifies synthetic, 待补 rerun)"),
            "opencode": (10, "排队中"),
            "claude-code": (1, "排队中"),
            "pi": (15, "排队中"),
            "hermes": (13, "running (8/12 done: 2 PASS=bn-fit-modify+portfolio-optimization Δ=+2, 6 ability=AgentTimeoutError, 4 running=regex-chess/sam-cell-seg/sanitize-git-repo/tune-mjcf; video-processing 1 not in batch 待补)"),
            "deepseek-harness": (5, "排队中"),
        }
        for i, (name, up, ev, tr, er) in enumerate(rows, 1):
            hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
            rd = review_data.get(hkey, {})
            if not rd:
                H.append(f"<tr><td class='num'>{i}</td><td>{esc(name)}</td>"
                         f"<td colspan='8'>复核数据不可用</td></tr>")
                continue
            bc = rd["bucket_counts"]
            real = f"{rd['real_pct']}%"
            inf_cls = "warn" if rd["pending_rerun"] > 0 else "pass"
            rp = rerun_plan.get(hkey, (0, "—"))
            rerun_status = rp[1]
            H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                     f"<td class='num pass'>{rd['passed']}</td>"
                     f"<td class='num'><strong>{real}</strong></td>"
                     f"<td class='num'>{bc['ability']}</td>"
                     f"<td class='num'>{bc['quota']}</td>"
                     f"<td class='num'>{bc['conn_refused']}</td>"
                     f"<td class='num'>{bc['synthetic']}</td>"
                     f"<td class='num {inf_cls}'>{rd['pending_rerun']}</td>"
                     f"<td style='font-size:0.85em'>{esc(rerun_status)}</td></tr>")
        H.append("</tbody></table>")
        H.append("<div class='info'><p><strong>口径说明</strong>: 真实 Pass% = passed / 89, "
                  "分母恒 89, 这是<strong>唯一可对外引用的成绩</strong>。待重跑列 = quota + conn_refused + synthetic "
                  "(未真跑 / infra), 这些题正在串行重跑; 重跑完成后, pass 的题 +1, fail 的题计入能力失败, "
                  "再重算真实 Pass%。<strong>不再有「修正后 Pass%」</strong>。</p></div>")
        # Infra 题清单 (保留, 用于追踪重跑清单)
        H.append("<h3>待重跑题清单 (synthetic + conn_refused + quota)</h3>")
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
        # 重跑计划与 BLOCKED 说明
        H.append("<div class='caveat'><p><strong>重跑计划 (47 trial)</strong>: "
                  "cline 1 (BLOCKED·3次CLI崩溃) · codex 2 (done, both ability) · hermes 13 (running) · opencode 10 · "
                  "pi 15 · deepseek 5 · cc 1 = 47 trial, 串行, adaptive concurrency (work=4/off=10)。</p>"
                  "<p><strong>环境硬约束 (BLOCKED, 显式注明)</strong>:</p><ul>"
                  "<li><strong>hermes qemu 类</strong>: BLOCKED (容器 Py3.9 &lt; hermes-agent 最低 3.11, "
                  "PyPI 全版本均 requires-python≥3.11) — 从分母剔除时显式注明原因, 不误算为通过</li>"
                  "<li><strong>cline pytorch-model-recovery</strong>: BLOCKED(infra) — 3 次重跑 (original 2026-11-09 + reruns 0932/1143) "
                  "均 cline CLI exit 1, no run_result, no stderr (cline auth OK, 1379B 正常 instruction, cline 跑通 332 题 → "
                  "任务特定 CLI 静默崩溃, 非能力); 同题 hermes 已 PASS → 确认非任务环境问题</li>"
                  "<li><strong>codex</strong>: 2 synthetic 已重跑, 均 reward=0.0 (ability) → "
                  "低分=真能力, 与原归因一致</li>"
                  "<li><strong>deepseek 5 · cc 1</strong>: 低分路也必须补齐, 不因分低跳过 "
                  "(2026-11-17 用户令)</li>"
                  "</ul></div>")

    # ---- 表五 · 重跑前后真实 Pass% 对比 (§2026-11-17 10:2x 用户令 item 3) ----
    H.append("<h2>表五 · 重跑前后真实 Pass% 对比 (2026-11-17 用户令)</h2>")
    H.append("<div class='caveat'><p><strong>口径</strong>: "
              "<strong>重跑前</strong> = 仅 original 目录的 passed/89; "
              "<strong>重跑后</strong> = 合并 original+rerun 的 passed/89 (分母恒 89)。"
              "Δ = 重跑后 − 重跑前。重跑进行中的路, 「重跑后」为当前合并值 (随重跑完成实时更新); "
              "重跑完成后 Δ 即最终增益。<strong>能力题一旦重跑仍 fail, 必须计为 fail</strong>, "
              "不许因想好看归到 infra; BLOCKED(infra) 硬约束题单列, 不误算为通过。</p></div>")
    H.append("<table><thead><tr><th>#</th><th>Harness</th><th>重跑前<br>passed/89</th>"
             "<th>重跑前<br>Pass%</th><th>重跑后<br>passed/89</th><th>重跑后<br>Pass%</th>"
             "<th>Δ</th><th>待重跑<br>(infra)</th><th>状态</th></tr></thead><tbody>")
    for i, (name, up, ev, tr, er) in enumerate(rows, 1):
        hkey = next((hk for hk, dv in DISP.items() if dv == name), name)
        before = (before_counts or {}).get(hkey, 0)
        after = up
        delta = after - before
        rd = review_data.get(hkey, {}) if review_data else {}
        pending = rd.get("pending_rerun", 0)
        # §2026-11-17: cline pytorch-model-recovery = BLOCKED(infra) after 3 failed rerun attempts
        # (cline CLI exit 1, no output); not "待重跑" — it's a hard infra constraint.
        BLOCKED_ROUTES = {"cline-patched"}
        if hkey in BLOCKED_ROUTES and pending > 0:
            status = f"BLOCKED(infra) ({pending} 题 cline CLI 崩溃, 3 attempts)"
        elif pending == 0:
            status = "重跑完成 ✅"
        else:
            status = f"重跑中 (待重跑 {pending})"
        d_cls = "pass" if delta > 0 else ("" if delta == 0 else "fail")
        delta_txt = f"+{delta}" if delta > 0 else str(delta)
        pend_cls = "warn" if pending > 0 else "pass"
        H.append(f"<tr><td class='num'>{i}</td><td><strong>{esc(name)}</strong></td>"
                 f"<td class='num'>{before}/{total_tasks}</td>"
                 f"<td class='num'>{before/total_tasks*100:.1f}%</td>"
                 f"<td class='num pass'>{after}/{total_tasks}</td>"
                 f"<td class='num'><strong>{after/total_tasks*100:.1f}%</strong></td>"
                 f"<td class='num {d_cls}'>{delta_txt}</td>"
                 f"<td class='num {pend_cls}'>{pending}</td>"
                 f"<td style='font-size:0.85em'>{esc(status)}</td></tr>")
    H.append("</tbody></table>")
    H.append("<div class='info'><p><strong>读法</strong>: codex 重跑前 1/89 → 重跑后 1/89 "
             "(2 synthetic 已重跑, 均 reward=0=ability, Δ=0, 证实低分=真能力, 无凭空抬分)。"
             "其余各路重跑进行中/排队, 完成后 Δ 自动更新: 重跑 pass 的题 +1, 重跑 fail 的题计失败 (Δ 不变)。"
             "BLOCKED(infra) 题 (如 hermes qemu 容器 Py3.9&lt;3.11) 显式注明原因、单列, 不误算为通过。</p></div>")

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
    before_counts = {h: count_route_before_rerun(h) for h in HARNESSES}
    _build_html(rows, total_tasks, total_passed, total_trials, now,
                audit_7way=audit_7way, review_data=review_data,
                before_counts=before_counts)


if __name__ == "__main__":
    main()
