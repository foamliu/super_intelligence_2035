#!/usr/bin/env python3
"""audit_codex_88_rebin.py — codex 88 失败题逐题翻 trace · 四桶重排

用户令 (2026-11-17 14:4x):
  「codex 1.1% 有点难以置信那」
  → 专项复查 codex 1.1%，疑为适配器假低分，非能力。

判据（codex 专属，具体到适配器层）：
  adapter/infra : return_code != 0 (RuntimeError / AgentTimeoutError / exit≠0)
                  且 stderr/stdout 含 429 / rate limit / exceeded retry /
                  responses 适配错 / 1800s 超时 → = infra，不是能力
  ability       : return_code == 0 (codex 干净跑完) 且 verifier 真给出 0.0

可检验假设：88 失败里 return_code!=0/超时/429 比例 >50% ⇒ 坐实
            「1.1% 是适配器缺陷假低分」而非真能力。
对照：codex 在它「干净跑完」的题里 Pass 率（历史约 48.8%）
      与 SWE-bench Verified 63.2% 是否自洽。

产物落 manifests/（已 gitignore）。
"""
from __future__ import annotations
import json, re, time
from pathlib import Path
import collections

JOBS = Path("/tmp/tb21_glm53_jobs")
MANIFESTS = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/"
                 "BaiZe-ISEDA2027/run/harness/terminalbench/manifests")

SCAN_DIRS = [JOBS / "codex"] if (JOBS / "codex").exists() else []
for rd in sorted(JOBS.glob("codex_rerun_*")):
    if rd.is_dir():
        SCAN_DIRS.append(rd)

INFRA_PATTERNS = [
    ("429", re.compile(r"429")),
    ("rate_limit", re.compile(r"rate[ _-]?limit|Too Many Requests", re.I)),
    ("exceeded_retry", re.compile(r"exceeded.{0,12}retry|retry.{0,12}exceeded|retries? exceeded", re.I)),
    ("responses_adapter", re.compile(r"wire_api|responses.*no longer supported|/v1/responses", re.I)),
    ("timeout_1800", re.compile(r"timed out after \d+ seconds|AgentTimeoutError|Command timed out", re.I)),
    ("ECONNRESET", re.compile(r"ECONNRESET|socket connection was closed", re.I)),
    ("config_toml", re.compile(r"config\.toml|no longer supported|model_providers\.gw_proxy", re.I)),
    ("quota", re.compile(r"额度已用完|Token额度", re.I)),
]


def _is_dated(name):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__", name))


def _iter_task_results(root: Path):
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if _is_dated(f.parent.name):
            continue
        yield f


def load_trials():
    """task_name -> list of trial dicts (original + rerun merged)."""
    task_data = {}
    for sd in SCAN_DIRS:
        for f in _iter_task_results(sd):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            vr = r.get("verifier_result") or {}
            rewards = vr.get("rewards")
            reward = (rewards or {}).get("reward", 0) if rewards else 0
            ei = r.get("exception_info") or {}
            ar = r.get("agent_result") or {}
            meta = ar.get("metadata") or {}
            stdout = meta.get("stdout", "") or ""
            stderr = meta.get("stderr", "") or ""
            tn = r.get("task_name") or str(f.parent.name).split("__")[0]
            exc_type = ei.get("exception_type", "")
            exc_msg = ei.get("exception_message", "") or ""
            exit_code = meta.get("exit_code")
            combined = stdout + "\n" + stderr + "\n" + exc_msg
            signals = []
            for name, pat in INFRA_PATTERNS:
                if pat.search(combined):
                    signals.append(name)
            task_data.setdefault(tn, []).append({
                "task": tn,
                "dir": str(f.parent),
                "source": "rerun" if "_rerun_" in str(sd) else "original",
                "reward": reward,
                "exit_code": exit_code,
                "exc_type": exc_type,
                "exc_msg_head": exc_msg[:200],
                "stdout_len": len(stdout),
                "stderr_len": len(stderr),
                "stdout_head": stdout[:400],
                "stderr_head": stderr[:400],
                "signals": signals,
                "has_verifier": bool(rewards),
            })
    return task_data


def classify(trials):
    """codex-specific rebin. PASS-first merge across trials."""
    best_reward = max(t["reward"] for t in trials)
    if best_reward == 1.0:
        return "passed", best_reward
    any_clean = any(
        (t["exit_code"] == 0 and not t["signals"]) for t in trials
    )
    any_infra_signal = any(t["signals"] for t in trials)
    any_nonzero_exit = any(
        (t["exit_code"] not in (0, None)) or t["exc_type"] for t in trials
    )
    if any_clean:
        return "ability", best_reward
    if any_infra_signal and any_nonzero_exit:
        return "adapter_infra", best_reward
    if any_nonzero_exit:
        return "adapter_infra", best_reward
    return "ability", best_reward


def main():
    td = load_trials()
    print(f"[codex-rebin] scan dirs: {[str(s) for s in SCAN_DIRS]}")
    print(f"[codex-rebin] tasks with trials: {len(td)}")
    buckets = collections.defaultdict(list)
    detail = {}
    for task, trials in sorted(td.items()):
        cat, best = classify(trials)
        buckets[cat].append(task)
        sig_tally = collections.Counter()
        for t in trials:
            for s in t["signals"]:
                sig_tally[s] += 1
        detail[task] = {
            "category": cat, "best_reward": best, "n_trials": len(trials),
            "sources": sorted(set(t["source"] for t in trials)),
            "signals": dict(sig_tally),
            "exit_codes": [t["exit_code"] for t in trials],
            "exc_types": [t["exc_type"] for t in trials],
            "has_verifier": any(t["has_verifier"] for t in trials),
        }
    total = len(td)
    passed = len(buckets["passed"])
    ability = len(buckets["ability"])
    infra = len(buckets["adapter_infra"])
    denom = passed + infra + ability
    print(f"\n[codex-rebin] codex TB-2.1 重排结果 (total={total}):")
    print(f"  passed        = {passed}  ({passed/total*100:.1f}%)")
    print(f"  adapter/infra = {infra}   ({infra/total*100:.1f}%)")
    print(f"  ability       = {ability}  ({ability/total*100:.1f}%)")
    ratio = infra / denom * 100 if denom else 0
    print(f"\n[codex-rebin] 假设验证: 失败里 infra 比例 = {infra}/{denom} = "
          f"{ratio:.1f}%  ({'坐实 (>50%)' if ratio > 50 else '未坐实'})")
    all_sig = collections.Counter()
    for t, d in detail.items():
        for s, n in d["signals"].items():
            all_sig[s] += n
    print(f"\n[codex-rebin] infra signal 频次 (跨所有 trial): {dict(all_sig)}")
    print("\n[codex-rebin] adapter/infra 桶 top3:")
    for task in list(buckets["adapter_infra"])[:3]:
        d = detail[task]
        t0 = td[task][0]
        print(f"  - {task}: signals={d['signals']} exit={d['exit_codes']} exc={d['exc_types']}")
        print(f"      stdout_head: {t0['stdout_head'][:200]!r}")
        print(f"      exc_msg_head: {t0['exc_msg_head'][:200]!r}")
    print("\n[codex-rebin] ability 桶 top3:")
    for task in list(buckets["ability"])[:3]:
        d = detail[task]
        t0 = td[task][0]
        print(f"  - {task}: signals={d['signals']} exit={d['exit_codes']} exc={d['exc_types']} has_verifier={d['has_verifier']}")
        print(f"      stdout_head: {t0['stdout_head'][:200]!r}")
    clean_trials = []
    for task, trials in td.items():
        for t in trials:
            if t["exit_code"] == 0 and not t["signals"]:
                clean_trials.append((task, t["reward"]))
                break
    if clean_trials:
        clean_pass = sum(1 for _, r in clean_trials if r == 1.0)
        cpr = round(clean_pass / len(clean_trials) * 100, 1)
        print(f"\n[codex-rebin] 干净跑完题数={len(clean_trials)} 其中 Pass={clean_pass} ({cpr}%)")
    else:
        clean_pass, cpr = 0, None
        print(f"\n[codex-rebin] 干净跑完题数=0 (codex 从未干净跑完任何一题!)")
    out = {
        "round": "codex-88-rebin-20261117-14xx",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks": total, "passed": passed,
        "adapter_infra": infra, "ability": ability,
        "infra_ratio_pct": round(ratio, 1),
        "hypothesis_confirmed": ratio > 50,
        "signal_freq": dict(all_sig),
        "clean_run_pass_rate": cpr,
        "clean_run_total": len(clean_trials),
        "buckets": dict(buckets),
        "detail": detail,
    }
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    fp = MANIFESTS / f"codex_88_rebin_{time.strftime('%Y%m%d_%H%M')}.json"
    fp.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n[codex-rebin] written: {fp} ({fp.stat().st_size} bytes)")
    print(f"\n[codex-rebin] MEMORY line: codex 88 失败重排 = adapter/infra={infra} · ability={ability} · passed={passed} · infra比例={ratio:.1f}% ({'坐实假低分' if ratio>50 else '未坐实'}) · 干净跑完Pass率={clean_pass}/{len(clean_trials)}{('='+str(cpr)+'%') if cpr else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
