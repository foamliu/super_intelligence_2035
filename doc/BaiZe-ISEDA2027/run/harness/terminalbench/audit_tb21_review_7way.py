#!/usr/bin/env python3
"""audit_tb21_review_7way.py — TB-2.1 七路失败归因复核（merged original+rerun）

用户令 (2026-11-17 08:5x):
  「结果再复核一遍，看失败的 Case 是否均为能力不足，而非 infra 问题」

用户令 (2026-11-17 10:2x) — 纠正归因口径:
  「有 x 未真跑，那举措不应该是重跑吗？你把分直接加上去算什么？」
  → 撤回「修正后 Pass% = passed / (89 − pure_infra)」(它把未真跑题从分母剔除，
     等价于假设这些题真跑就能通过 = 凭空抬分)。未真跑题的处置只有一个正解:
     重跑拿真实结果。真正的可对外引用成绩只有 passed / 89 (分母恒 89)。
     BLOCKED(infra) 题单列, 不误算为通过, 剔除时必须显式注明原因。

扫描 original + 所有 rerun 目录，按 task_name 合并（PASS 优先），
对合并后仍失败的题做四桶归因：ability / quota / conn_refused / synthetic。
真实 Pass% = passed / 89 (分母恒 89, 唯一可对外引用口径)。
infra 桶 (quota/conn_refused/synthetic) = 待重跑, 不从分母剔除。
产物落 manifests/（已 gitignore）。
"""
from __future__ import annotations
import json, os, re, time
from pathlib import Path

JOBS = Path("/tmp/tb21_glm53_jobs")
TB_DATASET = Path(os.path.expanduser("~/terminal-bench"))
MANIFESTS = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/"
                 "BaiZe-ISEDA2027/run/harness/terminalbench/manifests")
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code",
             "pi", "hermes", "deepseek-harness"]
DISP = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
        "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
        "deepseek-harness": "deepseek"}


def _is_dated(name):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__", name))


def _iter_task_results(root: Path):
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if "/20" not in str(f).replace("\\", "/"):
            continue
        if _is_dated(f.parent.name):
            continue
        yield f


def get_all_tasks():
    if TB_DATASET.exists():
        return sorted(x.name for x in TB_DATASET.iterdir() if x.is_dir())
    return []


def scan_route_all_dirs(h):
    """扫描 original + 所有 <h>_rerun_* 目录，返回 task -> [trial dict]。"""
    task_data = {}
    scan_dirs = [JOBS / h] if (JOBS / h).exists() else []
    for rd in sorted(JOBS.glob(f"{h}_rerun_*")):
        if rd.is_dir():
            scan_dirs.append(rd)
    for sd in scan_dirs:
        for f in _iter_task_results(sd):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            vr = r.get("verifier_result") or {}
            reward = (vr.get("rewards") or {}).get("reward", 0)
            ei = r.get("exception_info") or {}
            ar = r.get("agent_result") or {}
            meta = ar.get("metadata") or {}
            stdout = meta.get("stdout", "") or ""
            tn = r.get("task_name") or str(f.parent.name).split("__")[0]
            quota = ("额度已用完" in stdout) or ("Token额度" in stdout) or \
                    ("429" in stdout and "rate" in stdout.lower())
            m = re.search(r'"iterations":(\d+)', stdout)
            # §2026-11-17 14:4x: codex 适配器盲区修复 — 检测 429/rate_limit/
            # exceeded retry (codex 把 429 事件打印到 stdout JSON, 非 stderr)。
            # 命中 = adapter/infra, 不是能力 (实测 87/88 codex 失败 = 429 infra)。
            # §2026-11-17 15:3x: 收紧 429 匹配 —— 裸 '429' 会误命中 ISO 时间戳
            # (.429Z)、会话 ID (conv_...429...)、durationMs (62429) 等。改为只在
            # HTTP 错误上下文中匹配：'429 Too Many' / 'status: 429' / 'HTTP 429'。
            # codex 真实 429 = "exceeded retry limit, last status: 429 Too Many
            # Requests" → 仍被 '429 Too Many' + 'exceeded.{0,20}retry' 命中 ✅。
            rate_limit = bool(re.search(
                r"429 Too Many|status[ _:]?\s*429|HTTP[ _]?429|"
                r"rate[ _-]?limit|Too Many Requests|"
                r"exceeded.{0,20}retry|retry.{0,20}exceeded|retries? exceeded",
                stdout + "\n" + (meta.get("stderr", "") or ""), re.I))
            exit_code = meta.get("exit_code")
            # §2026-11-17 14:5x point④: codex 适配器「掐断」检测。
            # codex.py 修复后会在 metadata 写 codex_agent_worked / codex_turn_failed。
            # 对旧 trial (无此字段) 用 stdout 事件兜底：含 turn.started /
            # agent_message / command_execution 即证明 agent 确实在跑。
            codex_agent_worked = bool(meta.get("codex_agent_worked"))
            if not codex_agent_worked and stdout:
                for _ln in stdout.splitlines():
                    _ln = _ln.strip()
                    if _ln.startswith("{") and (
                        '"turn.started"' in _ln or '"agent_message"' in _ln
                        or '"command_execution"' in _ln
                        or '"turn.completed"' in _ln):
                        codex_agent_worked = True
                        break
            codex_turn_failed = bool(meta.get("codex_turn_failed")) or \
                '"turn.failed"' in stdout
            task_data.setdefault(tn, []).append({
                "dir": str(f.parent),
                "source": "rerun" if "_rerun_" in str(sd) else "original",
                "reward": reward, "quota": quota,
                "rate_limit": rate_limit,
                "exit_code": exit_code,
                "conn_refused": "ConnectionRefused" in stdout,
                "cli_bug": ("unknown option" in stdout.lower() and
                            meta.get("exit_code") == 1 and
                            '"run_result"' not in stdout),
                "econn": "ECONNRESET" in stdout,
                "iterations": int(m.group(1)) if m else -1,
                "exc_type": ei.get("exception_type", ""),
                "exc_msg": str(ei.get("exception_message", ""))[:300],
                "exc_tb": str(ei.get("exception_traceback", ""))[:600],
                "has_run_result": '"run_result"' in stdout,
                "has_verifier": bool(vr.get("rewards")),
                "stdout_len": len(stdout),
                # §2026-11-18: clean_ability = has_verifier=True 且无 exc_type 且
                # exit_code OK (None=未记录视为OK, 或 0)。这是 layer-A「真能力」证据。
                "clean_ability": (bool(vr.get("rewards"))
                                  and not ei.get("exception_type", "")
                                  and (exit_code is None or exit_code == 0)),
                # §2026-11-17 14:5x point④: codex 适配器掐断信号
                "codex_agent_worked": codex_agent_worked,
                "codex_turn_failed": codex_turn_failed,
            })
    return task_data


# §2026-11-18 10:3x 用户令: ability 桶拆两层。
#   layer-A「真能力」: has_verifier=True + 无 exception (verifier 干净跑出 0.0)。
#   layer-B「infra 嫌疑」: 带 infra 类 exception (timeout/setup/exit≠0/RuntimeError)
#     且无任何干净 verifier trial —— 需逐题 trace 判定是真 infra 还是能力。
#   exc_type 不再无条件算「真跑证据」(旧 has_proper 的 bug)。
INFRA_EXC_TYPES = {
    "AgentTimeoutError", "AgentSetupTimeoutError", "VerifierTimeoutError",
    "NonZeroAgentExitCodeError", "RuntimeError", "CancelledError",
    "RewardFileNotFoundError",
}
INFRA_EXC_SUBTYPE = {
    "AgentTimeoutError": "timeout",
    "AgentSetupTimeoutError": "setup_fail",
    "VerifierTimeoutError": "verifier_timeout",
    "NonZeroAgentExitCodeError": "nonzero_exit",
    "RuntimeError": "runtime_error",
    "CancelledError": "other_infra",
    "RewardFileNotFoundError": "other_infra",
}
# layer-B 子桶优先级: exit≠0 / RuntimeError 可能含能力成分, timeout/setup/verifier_timeout
# 更偏 infra。分类时取「最可能含能力」的子桶 (保守: 不轻易把题标成纯 infra)。
_INFRA_PRIO = ["nonzero_exit", "runtime_error", "timeout",
               "setup_fail", "verifier_timeout", "other_infra"]


def classify_merged(task_data, all_tasks):
    """合并所有 trial 后做归因。PASS 优先。ability 拆 layer-A/B 两层。"""
    buckets = {"passed": [], "ability": [],
               "timeout": [], "setup_fail": [], "nonzero_exit": [],
               "runtime_error": [], "verifier_timeout": [], "other_infra": [],
               "quota": [], "rate_limit": [], "conn_refused": [],
               "synthetic": [], "not_evaluated": []}
    detail = {}
    for task, trials in sorted(task_data.items()):
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            buckets["passed"].append(task)
            continue
        all_quota = all(t["quota"] for t in trials)
        all_conn = all(t["conn_refused"] or t["cli_bug"] for t in trials)
        all_synthetic = all(
            (not t["has_run_result"]) and t["stdout_len"] < 50
            and not t["has_verifier"]
            for t in trials)
        # §2026-11-18 10:3x: has_proper 不再含 exc_type —— exception 是 infra 信号,
        # 不是「模型真跑」证据。econn (ECONNRESET) 同理移除。
        has_proper = any(
            t["iterations"] > 1 or t["has_run_result"]
            for t in trials)
        any_rate_limit = any(t.get("rate_limit") for t in trials)
        # §2026-11-18 10:3x: any_clean 也不认 exc_type —— 有 infra exception 的
        # trial 不是「干净跑完」。只认 exit_code==0 或 has_verifier (且 exc_type
        # 不在 infra 集) 的 trial。
        any_clean = any(
            (t.get("exit_code") == 0
             or (t.get("has_verifier") and t["exc_type"] not in INFRA_EXC_TYPES))
            and not t.get("rate_limit") for t in trials)
        any_adapter_cutoff = any(
            t.get("codex_agent_worked") and not t.get("has_verifier")
            for t in trials)
        # §2026-11-18 10:3x 用户令 核心: layer-A「真能力」。
        #   any trial: has_verifier=True (verifier 跑了给 0.0) + 无 exception
        #   = 模型在非 infra 状态下跑完且被公平判分 = 真能力失败。
        has_clean_ability = any(
            t["has_verifier"] and not t["exc_type"]
            for t in trials)
        # §2026-11-18 10:3x 用户令: layer-B「infra 嫌疑」。
        #   无干净 trial + 有 infra 类 exception → 收集子类型。
        infra_subtypes = set()
        infra_evidence = []  # (exc_type, exc_msg, exc_tb, source, dir)
        for t in trials:
            if t["exc_type"] in INFRA_EXC_TYPES:
                infra_subtypes.add(INFRA_EXC_SUBTYPE[t["exc_type"]])
                infra_evidence.append(
                    (t["exc_type"], t.get("exc_msg", ""),
                     t.get("exc_tb", ""), t["source"], t["dir"]))
            if t.get("econn"):
                infra_subtypes.add("other_infra")
        # ---- 分类 ----
        if any_rate_limit and not any_clean:
            cat = "rate_limit"
        elif any_adapter_cutoff and not any_clean:
            cat = "rate_limit"
        elif has_clean_ability:
            cat = "ability"
        elif all_conn:
            cat = "conn_refused"
        elif all_quota:
            cat = "quota"
        elif infra_subtypes:
            # layer-B: 取「最可能含能力」的子桶 (保守归因)
            for prio in _INFRA_PRIO:
                if prio in infra_subtypes:
                    cat = prio
                    break
        elif all_synthetic:
            cat = "synthetic"
        elif has_proper:
            cat = "ability"
        elif any(t.get("has_verifier") for t in trials) and not all_synthetic:
            cat = "ability"
        else:
            cat = "synthetic"
        buckets[cat].append(task)
        d = {"category": cat, "best_reward": best,
             "n_trials": len(trials),
             "sources": sorted(set(t["source"] for t in trials))}
        # layer-B: 记录 infra 证据 (exc_type + trace top3) 供逐题深挖
        if cat in _INFRA_PRIO:
            d["infra_subtypes"] = sorted(infra_subtypes)
            d["infra_evidence"] = infra_evidence[:3]
        detail[task] = d
    for t in sorted(all_tasks):
        if t not in task_data:
            buckets["not_evaluated"].append(t)
    return buckets, detail


def main():
    all_tasks = get_all_tasks()
    total = len(all_tasks) or 89
    print(f"[review] TB-2.1 total tasks: {total}")
    result = {"round": "review-tb21-failure-attribution-7way",
              "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "total_tasks": total, "harnesses": {}}
    for h in HARNESSES:
        task_data = scan_route_all_dirs(h)
        buckets, detail = classify_merged(task_data, all_tasks)
        passed = len(buckets["passed"])
        # §2026-11-18 10:3x: layer-B infra 子桶 (timeout/setup/nonzero/runtime/...)
        layer_b = sum(len(buckets[k]) for k in
                      ("timeout", "setup_fail", "nonzero_exit",
                       "runtime_error", "verifier_timeout", "other_infra"))
        pure_infra = (len(buckets["quota"]) + len(buckets["conn_refused"])
                      + len(buckets["synthetic"]) + len(buckets["rate_limit"])
                      + layer_b)
        # §2026-11-17 10:2x: 真实 Pass% = passed / 89 (分母恒 89).
        real_pct = passed / total * 100
        # §2026-11-18 10:3x: 干净 Pass% 区间。
        #   下界 = passed/89 (当前确定值)。
        #   上界 = (passed + layer_b)/89 (假设所有 infra 嫌疑题补跑后全过——
        #   极端上界, 实际不可能全过, 但给运维一个范围感)。
        upper_pct = (passed + layer_b) / total * 100
        bc = {"ability": len(buckets["ability"]),
              "timeout": len(buckets["timeout"]),
              "setup_fail": len(buckets["setup_fail"]),
              "nonzero_exit": len(buckets["nonzero_exit"]),
              "runtime_error": len(buckets["runtime_error"]),
              "verifier_timeout": len(buckets["verifier_timeout"]),
              "other_infra": len(buckets["other_infra"]),
              "quota": len(buckets["quota"]),
              "rate_limit": len(buckets["rate_limit"]),
              "conn_refused": len(buckets["conn_refused"]),
              "synthetic": len(buckets["synthetic"]),
              "not_evaluated": len(buckets["not_evaluated"])}
        result["harnesses"][h] = {
            "display": DISP[h], "evaluated": len(task_data), "passed": passed,
            "real_pass_pct": round(real_pct, 1),
            "upper_pass_pct": round(upper_pct, 1),
            "layer_b_pending": layer_b,
            "buckets": buckets, "bucket_counts": bc,
            "pending_rerun": pure_infra,
            "detail": detail}
        print(f"[review] {DISP[h]:16s}: pass={passed:2d}/{total} "
              f"({real_pct:.1f}%) | ability={bc['ability']:2d} "
              f"timeout={bc['timeout']:2d} setup={bc['setup_fail']:2d} "
              f"nonzero={bc['nonzero_exit']:2d} runtime={bc['runtime_error']:2d} "
              f"vtimeout={bc['verifier_timeout']:2d} other={bc['other_infra']:2d} "
              f"| quota={bc['quota']:2d} rate_limit={bc['rate_limit']:2d} "
              f"conn_ref={bc['conn_refused']:2d} "
              f"synthetic={bc['synthetic']:2d} not_eval={bc['not_evaluated']:2d} "
              f"| layer-B(infra嫌疑)={layer_b} "
              f"Pass%区间={real_pct:.1f}%~{upper_pct:.1f}%")
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS / f"tb21_review_7way_{time.strftime('%Y%m%d_%H%M')}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[review] written: {out} ({out.stat().st_size} bytes)")
    parts = []
    for h in HARNESSES:
        r = result["harnesses"][h]
        parts.append(f"{DISP[h]}:{r['passed']}/{total}={r['real_pass_pct']}%"
                     f"(ability={r['bucket_counts']['ability']}"
                     f"/infra嫌疑={r['layer_b_pending']}"
                     f"/Pass%区间={r['real_pass_pct']}%~{r['upper_pass_pct']}%)")
    print("[review] MEMORY line: " + " | ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
