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
            rate_limit = bool(re.search(
                r"429|rate[ _-]?limit|Too Many Requests|"
                r"exceeded.{0,12}retry|retry.{0,12}exceeded|retries? exceeded",
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
                "has_run_result": '"run_result"' in stdout,
                "has_verifier": bool(vr.get("rewards")),
                "stdout_len": len(stdout),
                # §2026-11-17 14:5x point④: codex 适配器掐断信号
                "codex_agent_worked": codex_agent_worked,
                "codex_turn_failed": codex_turn_failed,
            })
    return task_data


def classify_merged(task_data, all_tasks):
    """合并所有 trial 后做四桶归因。PASS 优先。"""
    buckets = {"passed": [], "ability": [], "quota": [],
               "rate_limit": [], "conn_refused": [], "synthetic": [],
               "not_evaluated": []}
    detail = {}
    for task, trials in sorted(task_data.items()):
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            buckets["passed"].append(task)
            continue
        all_quota = all(t["quota"] for t in trials)
        all_conn = all(t["conn_refused"] or t["cli_bug"] for t in trials)
        all_synthetic = all(
            (not t["has_run_result"]) and t["stdout_len"] < 50 for t in trials)
        has_proper = any(
            t["iterations"] > 1 or t["has_run_result"] or
            t["exc_type"] or t["econn"] for t in trials)
        # §2026-11-17 14:4x: codex 适配器盲区修复。
        # codex 因 429/rate_limit/exceeded retry 产生的「假 0 分」会被 has_proper
        # (exc_type=RuntimeError) 误判成 ability。修复：若有 rate_limit 信号且
        # 无任何「干净跑完」trial (exit_code==0 且无 rate_limit 信号)，归 infra。
        any_rate_limit = any(t.get("rate_limit") for t in trials)
        any_clean = any(
            t.get("exit_code") == 0 and not t.get("rate_limit") for t in trials)
        # §2026-11-17 14:5x point④: codex 适配器「掐断」检测。
        # stdout 有 agent 事件 (agent 确实在跑) 但 verifier 没跑 (has_verifier=False)
        # = 适配器把「单命令非 0 退出」误当「整个 agent 失败」→ raise RuntimeError
        # → verifier 根本没跑 → 假低分。这是 infra (adapter缺陷)，不是 ability。
        any_adapter_cutoff = any(
            t.get("codex_agent_worked") and not t.get("has_verifier")
            for t in trials)
        if any_rate_limit and not any_clean:
            cat = "rate_limit"
        elif any_adapter_cutoff and not any_clean:
            # agent 跑了但 verifier 没跑 = 适配器掐断 (infra)，不是能力不足
            cat = "rate_limit"
        elif has_proper and not all_conn:
            cat = "ability"
        elif all_conn:
            cat = "conn_refused"
        elif all_synthetic:
            cat = "synthetic"
        elif all_quota:
            cat = "quota"
        elif has_proper:
            cat = "ability"
        elif any(t.get("has_verifier") for t in trials) and not all_synthetic:
            # verifier ran (gave a real score) AND agent produced output
            # (not all_synthetic => some trial has stdout_len>=50) => real
            # ability failure, not 未真跑/synthetic
            cat = "ability"
        else:
            cat = "synthetic"
        buckets[cat].append(task)
        detail[task] = {"category": cat, "best_reward": best,
                        "n_trials": len(trials),
                        "sources": sorted(set(t["source"] for t in trials))}
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
        pure_infra = (len(buckets["quota"]) + len(buckets["conn_refused"])
                      + len(buckets["synthetic"]) + len(buckets["rate_limit"]))
        # §2026-11-17 10:2x: 真实 Pass% = passed / 89 (分母恒 89).
        # 不再计算 corrected_pass_pct = passed/(89-pure_infra) — 那是凭空抬分.
        # infra 桶 (quota/conn_refused/synthetic/rate_limit) = 待重跑, 重跑后 pass 就 +1, fail 计失败.
        real_pct = passed / total * 100
        bc = {"ability": len(buckets["ability"]), "quota": len(buckets["quota"]),
              "rate_limit": len(buckets["rate_limit"]),
              "conn_refused": len(buckets["conn_refused"]),
              "synthetic": len(buckets["synthetic"]),
              "not_evaluated": len(buckets["not_evaluated"])}
        result["harnesses"][h] = {
            "display": DISP[h], "evaluated": len(task_data), "passed": passed,
            "real_pass_pct": round(real_pct, 1), "buckets": buckets,
            "bucket_counts": bc, "pending_rerun": pure_infra,
            "detail": detail}
        print(f"[review] {DISP[h]:16s}: pass={passed:2d}/{total} "
              f"({real_pct:.1f}%) | ability={bc['ability']:2d} "
              f"quota={bc['quota']:2d} rate_limit={bc['rate_limit']:2d} "
              f"conn_ref={bc['conn_refused']:2d} "
              f"synthetic={bc['synthetic']:2d} not_eval={bc['not_evaluated']:2d} "
              f"| 待重跑(infra)={pure_infra} (重跑完成后重算真实 Pass%)")
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS / f"tb21_review_7way_{time.strftime('%Y%m%d_%H%M')}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[review] written: {out} ({out.stat().st_size} bytes)")
    parts = []
    for h in HARNESSES:
        r = result["harnesses"][h]
        parts.append(f"{DISP[h]}:{r['passed']}/{total}={r['real_pass_pct']}%"
                     f"(待重跑={r['pending_rerun']})")
    print("[review] MEMORY line: " + " | ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
