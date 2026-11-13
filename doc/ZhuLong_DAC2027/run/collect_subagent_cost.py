#!/usr/bin/env python3
"""collect_subagent_cost.py — collect subagent-ablation cost / spawn-rate / Pass@1 / tokens.

Scans a finished batch dir produced by run_cline_script.sh:
  <batch>/cli_data/worker_*/data/sessions/*/*.messages.json   <- cline session traces
  <batch>/stats/{success,failure,timeout,total_time}           <- harness counters
  <batch>/logs/batch_cline.log                                 <- worker->task map + wall

For each worker session it counts:
  - subagent_researcher tool_use blocks  (spawn calls by main agent)
  - assistant message metrics.{input,output,cacheRead,cacheWrite}Tokens  (main-agent tokens)
  - tool_result of subagent_researcher may carry subagent usage (best-effort)

Outputs one JSON per (arm, round) with: spawn_calls, spawn_call_rate (tasks-with-spawn / n_tasks),
pass_rate_pct, passed/total, wall_sec, tokens{main,sub,total}, timeout, completion_rate.
"""
import argparse, json, os, re, glob


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arm", required=True)
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--batch-dir", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--n-tasks", type=int, default=0)
    p.add_argument("--out", required=True)
    return p.parse_args()


def read_int(path):
    try:
        return int(open(path).read().strip())
    except Exception:
        return None


def scan_session(path):
    """Return dict for one cline session messages.json: spawn_calls, tokens, tool histogram."""
    try:
        d = json.load(open(path, errors="replace"))
    except Exception:
        return None
    msgs = d.get("messages") if isinstance(d, dict) else None
    if not isinstance(msgs, list):
        return None
    spawn = 0
    tool_hist = {}
    in_tok = out_tok = cache_r = cache_w = 0
    sub_in = sub_out = 0
    n_assistant = 0
    for m in msgs:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        # assistant metrics -> main-agent tokens
        if role == "assistant":
            n_assistant += 1
            mt = m.get("metrics") or {}
            in_tok += int(mt.get("inputTokens", 0) or 0)
            out_tok += int(mt.get("outputTokens", 0) or 0)
            cache_r += int(mt.get("cacheReadTokens", 0) or 0)
            cache_w += int(mt.get("cacheWriteTokens", 0) or 0)
        # tool_use blocks (assistant content is a list of blocks)
        c = m.get("content")
        if isinstance(c, list):
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "tool_use":
                    name = blk.get("name", "")
                    tool_hist[name] = tool_hist.get(name, 0) + 1
                    if name == "subagent_researcher":
                        spawn += 1
        # tool_result blocks may contain subagent usage (best-effort parse)
        if isinstance(c, list):
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "tool_result":
                    cont = blk.get("content")
                    s = cont if isinstance(cont, str) else json.dumps(cont, ensure_ascii=False)
                    um = re.search(r'"?usage"?\s*:\s*\{[^}]*"inputTokens"\s*:\s*(\d+)[^}]*"outputTokens"\s*:\s*(\d+)', s)
                    if um and "subagent" in s.lower():
                        sub_in += int(um.group(1)); sub_out += int(um.group(2))
    return {
        "spawn_calls": spawn,
        "n_assistant_msgs": n_assistant,
        "tokens_main": {"input": in_tok, "output": out_tok, "cacheRead": cache_r, "cacheWrite": cache_w},
        "tokens_sub": {"input": sub_in, "output": sub_out},
        "tool_hist": tool_hist,
    }


def worker_task_map(log_text):
    """From batch_cline.log build worker -> [task_id, ...] in start order."""
    wm = {}
    for m in re.finditer(r'\[worker-(\d+)\]\s*开始任务\s+(\S+)', log_text):
        w, t = m.group(1), m.group(2)
        wm.setdefault(w, []).append(t)
    return wm


def main():
    a = parse_args()
    log_text = open(a.log, errors="replace").read() if os.path.isfile(a.log) else ""
    batch = os.path.basename(a.batch_dir)

    # scan all session messages.json under cli_data/
    sessions = []
    for mf in sorted(glob.glob(os.path.join(a.batch_dir, "cli_data", "worker_*", "data", "sessions", "*", "*.messages.json"))):
        # worker id from path
        wm = re.search(r'worker_(\d+)', mf)
        worker = wm.group(1) if wm else "?"
        s = scan_session(mf)
        if s:
            s["worker"] = worker
            s["session_file"] = mf
            sessions.append(s)

    # spawn call rate: tasks (sessions) with >=1 spawn / n_tasks
    n_spawn_sessions = sum(1 for s in sessions if s["spawn_calls"] > 0)
    total_spawn = sum(s["spawn_calls"] for s in sessions)
    n_tasks = a.n_tasks or len(sessions)
    spawn_call_rate = round(n_spawn_sessions / n_tasks, 4) if n_tasks else None

    # tokens aggregate (main + sub)
    main_in = sum(s["tokens_main"]["input"] for s in sessions)
    main_out = sum(s["tokens_main"]["output"] for s in sessions)
    main_cache_r = sum(s["tokens_main"]["cacheRead"] for s in sessions)
    main_cache_w = sum(s["tokens_main"]["cacheWrite"] for s in sessions)
    sub_in = sum(s["tokens_sub"]["input"] for s in sessions)
    sub_out = sum(s["tokens_sub"]["output"] for s in sessions)

    # tool histogram aggregate
    agg_hist = {}
    for s in sessions:
        for k, v in s["tool_hist"].items():
            agg_hist[k] = agg_hist.get(k, 0) + v

    # Pass@1 / completion from stats/
    succ = read_int(os.path.join(a.batch_dir, "stats", "success")) or 0
    fail = read_int(os.path.join(a.batch_dir, "stats", "failure")) or 0
    tmo = read_int(os.path.join(a.batch_dir, "stats", "timeout")) or 0
    total_done = succ + fail + tmo
    pass_rate = round(100.0 * succ / total_done, 2) if total_done else None
    completion_rate = round(100.0 * (succ + fail) / total_done, 2) if total_done else None  # exclude timeout

    # wall from stats/total_time (sec) — fallback to log timestamp delta
    wall = read_int(os.path.join(a.batch_dir, "stats", "total_time"))
    if wall is None:
        ts = re.findall(r'\[(\d{2}:\d{2}:\d{2})\]', log_text)
        if len(ts) >= 2:
            def to_s(t):
                h, mi, s = map(int, t.split(":")); return h * 3600 + mi * 60 + s
            wall = to_s(ts[-1]) - to_s(ts[0])
            if wall < 0: wall += 86400

    # doubao connectivity: count HTTP 200 / errors in log
    http_200 = len(re.findall(r'200', log_text))
    http_err = len(re.findall(r'(?i)(http (4\d\d|5\d\d)|ECONNREFUSED|ETIMEDOUT|doubao.*error)', log_text))

    cost = {
        "arm": a.arm, "round": a.round, "batch": batch, "n_tasks": n_tasks,
        "spawn_calls_total": total_spawn,
        "spawn_sessions": n_spawn_sessions,
        "spawn_call_rate": spawn_call_rate,
        "pass_rate_pct": pass_rate,
        "passed": succ, "failed": fail, "timed_out": tmo, "total_done": total_done,
        "completion_rate_pct": completion_rate,
        "wall_sec": wall,
        "tokens_main": {"input": main_in, "output": main_out, "cacheRead": main_cache_r, "cacheWrite": main_cache_w,
                        "total": main_in + main_out},
        "tokens_sub": {"input": sub_in, "output": sub_out, "total": sub_in + sub_out},
        "tokens_grand_total": main_in + main_out + sub_in + sub_out,
        "tool_histogram": agg_hist,
        "n_sessions_scanned": len(sessions),
        "doubao_http_200_hits": http_200, "doubao_http_err_hits": http_err,
        "per_session": [{"worker": s["worker"], "spawn_calls": s["spawn_calls"],
                         "main_in_tok": s["tokens_main"]["input"], "main_out_tok": s["tokens_main"]["output"],
                         "n_assistant": s["n_assistant_msgs"]} for s in sessions],
        "log": a.log,
    }
    json.dump(cost, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"cost saved: {a.out} | arm={a.arm} r={a.round} "
          f"spawn={total_spawn} calls in {n_spawn_sessions}/{n_tasks} sessions (rate={spawn_call_rate}) "
          f"pass={pass_rate}% ({succ}/{total_done}) wall={wall}s main_tok={main_in+main_out}")


if __name__ == "__main__":
    main()
