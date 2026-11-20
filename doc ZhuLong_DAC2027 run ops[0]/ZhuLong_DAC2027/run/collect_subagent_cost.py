#!/usr/bin/env python3
"""collect_subagent_cost.py — collect subagent-ablation cost / spawn-rate / Pass@1 / tokens.

Scans a finished batch dir produced by run_cline_script.sh. Supports two layouts:
  (A) legacy: <batch>/cli_data/worker_*/data/sessions/*/*.messages.json
  (B) unified-data-dir (CLINE_UNIFIED_DATA_DIR=1): <batch>/code/<task>/ws/sessions/*/*.messages.json

Each session .messages.json has an `agent` field: "lead" (main agent) or "subagent".
  - Main sessions: count `spawn_agent` tool_use blocks (spawn calls) + main-agent tokens (assistant metrics).
  - Subagent sessions (filename starts with `agent_` or agent=="subagent"): collect sub tokens + tools used.

Subagent sessions are created by cline's spawn_agent tool; their tokens are reported separately.
Outputs one JSON per (arm, round) with: spawn_calls, spawn_call_rate, pass_rate, tokens{main,sub}, wall.
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
    """Return dict for one cline session messages.json."""
    try:
        d = json.load(open(path, errors="replace"))
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    msgs = d.get("messages")
    if not isinstance(msgs, list):
        return None
    agent_kind = d.get("agent", "")  # "lead" or "subagent"
    fname = os.path.basename(path)
    is_subagent = (agent_kind == "subagent") or fname.startswith("agent_")
    spawn = 0
    tool_hist = {}
    in_tok = out_tok = cache_r = cache_w = 0
    n_assistant = 0
    finish_reasons = {}
    for m in msgs:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        if role == "assistant":
            n_assistant += 1
            mt = m.get("metrics") or {}
            in_tok += int(mt.get("inputTokens", 0) or 0)
            out_tok += int(mt.get("outputTokens", 0) or 0)
            cache_r += int(mt.get("cacheReadTokens", 0) or 0)
            cache_w += int(mt.get("cacheWriteTokens", 0) or 0)
        # tool_use blocks
        c = m.get("content")
        if isinstance(c, list):
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "tool_use":
                    name = blk.get("name", "")
                    tool_hist[name] = tool_hist.get(name, 0) + 1
                    if name == "spawn_agent":
                        spawn += 1
        # finishReason
        fr = m.get("finishReason")
        if fr:
            finish_reasons[fr] = finish_reasons.get(fr, 0) + 1
    return {
        "is_subagent": is_subagent,
        "agent_kind": agent_kind,
        "spawn_calls": spawn,
        "n_assistant_msgs": n_assistant,
        "n_msgs": len(msgs),
        "tokens": {"input": in_tok, "output": out_tok, "cacheRead": cache_r, "cacheWrite": cache_w,
                    "total": in_tok + out_tok},
        "tool_hist": tool_hist,
        "finish_reasons": finish_reasons,
        "session_file": path,
    }


def find_sessions(batch_dir):
    """Find all .messages.json under both legacy and unified layouts."""
    patterns = [
        os.path.join(batch_dir, "cli_data", "worker_*", "data", "sessions", "*", "*.messages.json"),
        os.path.join(batch_dir, "code", "*", "ws", "sessions", "*", "*.messages.json"),
    ]
    found = []
    for pat in patterns:
        found.extend(sorted(glob.glob(pat)))
    return found


def main():
    a = parse_args()
    log_text = open(a.log, errors="replace").read() if os.path.isfile(a.log) else ""
    batch = os.path.basename(a.batch_dir)

    session_files = find_sessions(a.batch_dir)
    sessions = []
    for mf in session_files:
        s = scan_session(mf)
        if s:
            sessions.append(s)

    main_sessions = [s for s in sessions if not s["is_subagent"]]
    sub_sessions = [s for s in sessions if s["is_subagent"]]

    # spawn call rate: main sessions (tasks) with >=1 spawn_agent / n_tasks
    n_spawn_sessions = sum(1 for s in main_sessions if s["spawn_calls"] > 0)
    total_spawn = sum(s["spawn_calls"] for s in main_sessions)
    n_tasks = a.n_tasks or len(main_sessions)
    spawn_call_rate = round(n_spawn_sessions / n_tasks, 4) if n_tasks else None

    # main-agent tokens
    main_in = sum(s["tokens"]["input"] for s in main_sessions)
    main_out = sum(s["tokens"]["output"] for s in main_sessions)
    main_cache_r = sum(s["tokens"]["cacheRead"] for s in main_sessions)
    main_cache_w = sum(s["tokens"]["cacheWrite"] for s in main_sessions)

    # subagent tokens
    sub_in = sum(s["tokens"]["input"] for s in sub_sessions)
    sub_out = sum(s["tokens"]["output"] for s in sub_sessions)

    # subagent execution rate: sub sessions with n_msgs > 0 / total sub sessions
    sub_executed = sum(1 for s in sub_sessions if s["n_msgs"] > 2)  # >2 means real conversation
    sub_execution_rate = round(sub_executed / len(sub_sessions), 4) if sub_sessions else None

    # subagent tools used (aggregate)
    sub_tools = {}
    for s in sub_sessions:
        for k, v in s["tool_hist"].items():
            sub_tools[k] = sub_tools.get(k, 0) + v
    sub_has_mcp = any("pyAether_MCP_server" in k or k in ("search_apis", "get_api_details") for k in sub_tools)
    # Note: search_apis in sub_tools may be FAILED attempts (NoSuchToolError); check tool_results
    sub_mcp_rejected = log_text.count("AI_NoSuchToolError")

    # tool histogram aggregate (main sessions)
    agg_hist = {}
    for s in main_sessions:
        for k, v in s["tool_hist"].items():
            agg_hist[k] = agg_hist.get(k, 0) + v

    # Pass@1: parse the pyAether_aether runtime line
    pass_rate = None
    passed = None
    total = None
    m = re.search(r'运行时 pyAether_aether[^:]*: 任务=(\d+) 样本=(\d+) 正确=(\d+)', log_text)
    if m:
        total = int(m.group(1))
        passed = int(m.group(3))
        if total:
            pass_rate = round(100.0 * passed / total, 2)
    if pass_rate is None:
        m2 = re.search(r'pyAether_aether\s*\(.*?\)\s*:\s*PASS_RATE=([\d.]+)', log_text)
        if m2:
            pass_rate = round(float(m2.group(1)) * 100, 2)

    # completion from stats/
    succ = read_int(os.path.join(a.batch_dir, "stats", "success")) or 0
    fail = read_int(os.path.join(a.batch_dir, "stats", "failure")) or 0
    tmo = read_int(os.path.join(a.batch_dir, "stats", "timeout")) or 0
    total_done = succ + fail + tmo
    completion_rate = round(100.0 * (succ + fail) / total_done, 2) if total_done else None

    # wall
    wall = read_int(os.path.join(a.batch_dir, "stats", "total_time"))
    if wall is None:
        ts = re.findall(r'\[(\d{2}:\d{2}:\d{2})\]', log_text)
        if len(ts) >= 2:
            def to_s(t):
                h, mi, s = map(int, t.split(":")); return h * 3600 + mi * 60 + s
            wall = to_s(ts[-1]) - to_s(ts[0])
            if wall < 0: wall += 86400

    cost = {
        "arm": a.arm, "round": a.round, "batch": batch, "n_tasks": n_tasks,
        "spawn_calls_total": total_spawn,
        "spawn_sessions": n_spawn_sessions,
        "spawn_call_rate": spawn_call_rate,
        "subagent_sessions_total": len(sub_sessions),
        "subagent_executed": sub_executed,
        "subagent_execution_rate": sub_execution_rate,
        "subagent_has_mcp_tools": sub_has_mcp,
        "subagent_mcp_rejected_count": sub_mcp_rejected,
        "subagent_tools_histogram": sub_tools,
        "pass_rate_pct": pass_rate,
        "passed": passed, "total_eval": total,
        "cline_success": succ, "cline_failed": fail, "timed_out": tmo, "total_done": total_done,
        "completion_rate_pct": completion_rate,
        "wall_sec": wall,
        "tokens_main": {"input": main_in, "output": main_out, "cacheRead": main_cache_r, "cacheWrite": main_cache_w,
                        "total": main_in + main_out},
        "tokens_sub": {"input": sub_in, "output": sub_out, "total": sub_in + sub_out},
        "tokens_grand_total": main_in + main_out + sub_in + sub_out,
        "tool_histogram_main": agg_hist,
        "n_sessions_scanned": len(sessions),
        "n_main_sessions": len(main_sessions),
        "n_subagent_sessions": len(sub_sessions),
        "per_main_session": [{"spawn_calls": s["spawn_calls"],
                              "n_msgs": s["n_msgs"],
                              "main_in_tok": s["tokens"]["input"], "main_out_tok": s["tokens"]["output"],
                              "n_assistant": s["n_assistant_msgs"]} for s in main_sessions],
        "per_subagent_session": [{"n_msgs": s["n_msgs"],
                                  "sub_in_tok": s["tokens"]["input"], "sub_out_tok": s["tokens"]["output"],
                                  "finish_reasons": s["finish_reasons"],
                                  "tools": s["tool_hist"]} for s in sub_sessions],
        "log": a.log,
    }
    json.dump(cost, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"cost saved: {a.out} | arm={a.arm} r={a.round} "
          f"spawn={total_spawn} calls in {n_spawn_sessions}/{n_tasks} tasks (rate={spawn_call_rate}) "
          f"sub_sessions={len(sub_sessions)} executed={sub_executed} (exec_rate={sub_execution_rate}) "
          f"Pass@1={pass_rate}% ({passed}/{total}) cline_ok={succ}/{total_done} wall={wall}s "
          f"main_tok={main_in+main_out} sub_tok={sub_in+sub_out}")


if __name__ == "__main__":
    main()
