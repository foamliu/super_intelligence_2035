#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_cost.py — ZhuLong think×lang 消融 · 单轮成本抽取

从一轮 batch 目录的 cline sessions 中抽取逐题 + 汇总成本指标：
  - Pass@1（从 log grep，可选）
  - 墙钟·单题均值(s) / Batch 墙钟(h)
  - Token prompt / completion / reasoning(est) / total
  - Token/题
  - Timeout 数 / Gen-fail 数 / Converged(%)

用法:
  python3 extract_cost.py --batch <batch_dir> [--log <run_log>] [--out <cost.json>]
"""
import argparse, json, os, sys, re, glob
from datetime import datetime
from pathlib import Path


def iso_to_epoch(s):
    if not s:
        return None
    try:
        s2 = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s2).timestamp()
    except Exception:
        return None


def find_sessions(batch_dir):
    """并行模式: <batch>/cli_data/worker_*/data/sessions/*；串行: ~/.cline/data/sessions/* (按 mtime 近 batch)。
    返回 [(sid_dir, sid), ...]"""
    out = []
    for p in glob.glob(os.path.join(batch_dir, "cli_data", "worker_*", "data", "sessions", "*")):
        if os.path.isdir(p):
            out.append((p, os.path.basename(p)))
    if out:
        return out
    # 串行回退：共享 ~/.cline/data/sessions
    home_sessions = os.path.expanduser("~/.cline/data/sessions")
    if os.path.isdir(home_sessions):
        for p in glob.glob(os.path.join(home_sessions, "*")):
            if os.path.isdir(p):
                out.append((p, os.path.basename(p)))
    return out


def parse_session(sid_dir, sid):
    meta_path = os.path.join(sid_dir, f"{sid}.json")
    msg_path = os.path.join(sid_dir, f"{sid}.messages.json")
    if not os.path.exists(meta_path):
        return None
    try:
        md = json.load(open(meta_path))
    except Exception:
        return None
    m = md.get("metadata", {}) or {}
    usage = m.get("usage", {}) or {}
    cwd = md.get("cwd", "") or ""
    # task_name = basename(dirname(cwd))  e.g. .../code/EDA-Eval-PyAether-001/ws -> EDA-Eval-PyAether-001
    task_name = ""
    if cwd:
        parent = os.path.dirname(os.path.normpath(cwd))
        task_name = os.path.basename(parent)
    started = md.get("started_at")
    ended = md.get("ended_at")
    se, ee = iso_to_epoch(started), iso_to_epoch(ended)
    wall = (ee - se) if (se and ee) else None
    status = md.get("status", "")
    model = md.get("model", "")
    # 逐 assistant 聚合
    n_assist = 0
    in_tok = out_tok = 0
    think_chars = 0
    n_think = 0
    if os.path.exists(msg_path):
        try:
            mm = json.load(open(msg_path))
            msgs = mm.get("messages", []) if isinstance(mm, dict) else (mm if isinstance(mm, list) else [])
        except Exception:
            msgs = []
        for x in msgs:
            if not isinstance(x, dict):
                continue
            if x.get("role") == "assistant":
                n_assist += 1
                mt = x.get("metrics", {}) or {}
                in_tok += int(mt.get("inputTokens", 0) or 0)
                out_tok += int(mt.get("outputTokens", 0) or 0)
                c = x.get("content")
                if isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "thinking":
                            n_think += 1
                            t = b.get("thinking", "") or ""
                            think_chars += len(t)
    # 优先用 agg usage；回退逐 msg
    agg_in = int(usage.get("inputTokens", 0) or 0) or in_tok
    agg_out = int(usage.get("outputTokens", 0) or 0) or out_tok
    return {
        "sid": sid,
        "task": task_name,
        "model": model,
        "status": status,
        "converged": 1 if status == "completed" else 0,
        "started_at": started,
        "ended_at": ended,
        "wall_sec": round(wall, 1) if wall is not None else None,
        "prompt_tokens": agg_in,
        "completion_tokens": agg_out,
        "reasoning_chars": think_chars,
        "reasoning_tokens_est": think_chars // 4,  # 粗估：4 char/token
        "n_thinking_blocks": n_think,
        "n_assistant_msgs": n_assist,
        "total_tokens": agg_in + agg_out,
    }


def grep_pass_rate(log_path):
    if not log_path or not os.path.exists(log_path):
        return None, (None, None)
    txt = open(log_path, errors="ignore").read()
    # 形如 "pass (xx.x%)" 或 "PASS_RATE=0.xxxx"
    m = re.findall(r"pass\s*\(([0-9.]+)%\)", txt)
    pr = float(m[-1]) if m else None
    m2 = re.search(r"PASS_RATE\s*[:=]\s*([0-9.]+)", txt)
    pr2 = float(m2.group(1)) if m2 else None
    rate = pr if pr is not None else (pr2 * 100 if pr2 is not None else None)
    # pass 计数
    mc = re.findall(r"pass\s*\(\s*[0-9.]+%\s*\D*(\d+)\s*/\s*(\d+)", txt)
    passed = total = None
    if mc:
        passed, total = int(mc[-1][0]), int(mc[-1][1])
    return rate, (passed, total)


def read_stats(batch_dir):
    stats = {}
    sd = os.path.join(batch_dir, "stats")
    for k in ("success", "failure", "timeout", "total_time"):
        p = os.path.join(sd, k)
        try:
            stats[k] = int(open(p).read().strip() or 0)
        except Exception:
            stats[k] = None
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True, help="batch 目录 (含 cli_data/)")
    ap.add_argument("--log", default=None, help="run_cline_script.sh 的 stdout log（用于 grep pass rate）")
    ap.add_argument("--out", default=None, help="输出 JSON 路径（默认 stdout）")
    ap.add_argument("--tag", default=None, help="变体标签 (如 A_none_r1)")
    args = ap.parse_args()

    sessions = find_sessions(args.batch)
    tasks = []
    for sid_dir, sid in sessions:
        r = parse_session(sid_dir, sid)
        if r:
            tasks.append(r)

    # 排除空 task（如本 opencode agent 自身 session）——只保留 EDA-Eval-PyAether-NNN
    tasks = [t for t in tasks if re.search(r"EDA-Eval-PyAether-\d+", t["task"])]
    # 去重：同一 task 多 session 取最完整（total_tokens 最大）
    by_task = {}
    for t in tasks:
        k = t["task"]
        if k not in by_task or t["total_tokens"] > by_task[k]["total_tokens"]:
            by_task[k] = t
    tasks = sorted(by_task.values(), key=lambda x: x["task"])

    n = len(tasks)
    walls = [t["wall_sec"] for t in tasks if t["wall_sec"] is not None]
    conv = sum(t["converged"] for t in tasks)
    tot_in = sum(t["prompt_tokens"] for t in tasks)
    tot_out = sum(t["completion_tokens"] for t in tasks)
    tot_reason_chars = sum(t["reasoning_chars"] for t in tasks)
    tot_tok = sum(t["total_tokens"] for t in tasks)
    stats = read_stats(args.batch)
    rate, (passed, total) = grep_pass_rate(args.log)

    batch_start = min((t["started_at"] for t in tasks if t["started_at"]), default=None)
    batch_end = max((t["ended_at"] for t in tasks if t["ended_at"]), default=None)
    bse, bee = iso_to_epoch(batch_start), iso_to_epoch(batch_end)
    batch_wall_h = round((bee - bse) / 3600.0, 2) if (bse and bee) else None

    def mean(xs):
        return round(sum(xs) / len(xs), 2) if xs else None

    summary = {
        "tag": args.tag,
        "batch": os.path.basename(args.batch.rstrip("/")),
        "n_tasks": n,
        "pass_rate_pct": rate,
        "passed": passed,
        "total": total,
        "wall_sec_per_task_mean": mean(walls),
        "batch_wall_h": batch_wall_h,
        "prompt_tokens_total": tot_in,
        "completion_tokens_total": tot_out,
        "reasoning_chars_total": tot_reason_chars,
        "reasoning_tokens_est_total": tot_reason_chars // 4,
        "total_tokens": tot_tok,
        "tokens_per_task_mean": round(tot_tok / n, 1) if n else None,
        "prompt_tokens_per_task_mean": round(tot_in / n, 1) if n else None,
        "completion_tokens_per_task_mean": round(tot_out / n, 1) if n else None,
        "reasoning_chars_per_task_mean": round(tot_reason_chars / n, 1) if n else None,
        "converged_pct": round(conv / n * 100, 1) if n else None,
        "timeout": stats.get("timeout"),
        "gen_fail": stats.get("failure"),
        "success": stats.get("success"),
    }
    result = {"summary": summary, "tasks": tasks}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        open(args.out, "w").write(out)
        print(f"[extract_cost] wrote {args.out}: n={n} pass={rate}%", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
