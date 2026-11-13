#!/usr/bin/env python3
"""collect_subagent_cost.py — 从 round log + batch dir 收集 subagent 消融的 cost/调用率/Pass@1.

P1 pilot 用: 采 spawn 调用率 / Pass@1 / 墙钟 / doubao 连通.
P2 主实验会扩展 token 采集 (从 cline session usage).
"""
import argparse, json, os, re, sys, glob

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arm", required=True)
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--batch-dir", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--n-tasks", type=int, default=0)
    p.add_argument("--out", required=True)
    return p.parse_args()

def main():
    a = parse_args()
    log_text = ""
    if os.path.isfile(a.log):
        with open(a.log, errors="replace") as f:
            log_text = f.read()

    # spawn 调用率: 数 [subagent_researcher] 工具调用次数 (主 agent 调 subagent)
    spawn_calls = len(re.findall(r'\[subagent_researcher\]', log_text))
    # spawn 完成: 数 SpawnAgentOutput / subagent.*complet
    spawn_completed = len(re.findall(r'(?i)subagent.{0,20}(complet|finish|return|done)', log_text))
    # subagent 内部的 search_apis / get_api_details 调用 (subagent 做了研究)
    sub_search = len(re.findall(r'\[pyAether_MCP_server__search_apis\]', log_text))
    sub_details = len(re.findall(r'\[pyAether_MCP_server__get_api_details\]', log_text))

    # Pass@1: 从 log grep 'pass (xx.x%)' 或 'PASS_RATE' 或 'passed'
    pass_rate = None
    passed = None
    total = None
    m = re.search(r'pass\s*\(([\d.]+)%\)', log_text)
    if m:
        pass_rate = float(m.group(1))
    m2 = re.search(r'(?i)passed[:\s]+(\d+)\s*/\s*(\d+)', log_text)
    if m2:
        passed = int(m2.group(1)); total = int(m2.group(2))
    # harness run_eval 输出: "通过: X/Y" 或 "pass_rate: Z%"
    m3 = re.search(r'(?i)(通过|pass_rate|PASS_RATE)[:\s]+(\d+(?:\.\d+)?)\s*%?', log_text)
    if m3 and pass_rate is None:
        pass_rate = float(m3.group(2))

    # 墙钟: 从 log 首末时间戳估算 (粗)
    wall_sec = None
    ts = re.findall(r'\[(\d{2}:\d{2}:\d{2})\]', log_text)
    if len(ts) >= 2:
        def to_s(t):
            h, mi, s = map(int, t.split(":")); return h * 3600 + mi * 60 + s
        wall_sec = to_s(ts[-1]) - to_s(ts[0])
        if wall_sec < 0: wall_sec += 86400

    # token: 从 session usage 采 (P2 扩展; P1 先扫 batch trace 里的 ui_messages.json)
    prompt_tok = 0; completion_tok = 0; reasoning_tok = 0; total_tok = 0
    batch = os.path.basename(a.batch_dir)
    trace_dir = os.path.join(a.batch_dir, "trace")
    usage_files = glob.glob(os.path.join(a.batch_dir, "**", "ui_messages.json"), recursive=True)
    for uf in usage_files:
        try:
            data = json.load(open(uf, errors="replace"))
            # ui_messages 可能含 usage 字段; 尽力采集
            if isinstance(data, list):
                for msg in data:
                    u = msg.get("usage") or msg.get("tokenUsage") if isinstance(msg, dict) else None
                    if isinstance(u, dict):
                        prompt_tok += u.get("inputTokens", u.get("prompt_tokens", 0)) or 0
                        completion_tok += u.get("outputTokens", u.get("completion_tokens", 0)) or 0
                        reasoning_tok += u.get("reasoningTokens", 0) or 0
        except Exception:
            pass
    total_tok = prompt_tok + completion_tok + reasoning_tok

    # timeout / gen_fail / converged (从 log)
    timeout_n = len(re.findall(r'(?i)timeout|超时', log_text))
    gen_fail = len(re.findall(r'(?i)(gen.?fail|生成失败|exit code: [^0])', log_text))

    cost = {
        "arm": a.arm, "round": a.round, "batch": batch,
        "n_tasks": a.n_tasks,
        "spawn_calls": spawn_calls,
        "spawn_completed": spawn_completed,
        "spawn_call_rate": round(spawn_calls / a.n_tasks, 3) if a.n_tasks else None,
        "subagent_search_apis_calls": sub_search,
        "subagent_get_api_details_calls": sub_details,
        "pass_rate_pct": pass_rate,
        "passed": passed, "total": total,
        "wall_sec": wall_sec,
        "tokens": {"prompt": prompt_tok, "completion": completion_tok,
                   "reasoning": reasoning_tok, "total": total_tok},
        "timeout": timeout_n, "gen_fail": gen_fail,
        "log": a.log,
    }
    json.dump(cost, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"cost saved: {a.out} | arm={a.arm} r={a.round} spawn={spawn_calls}/{a.n_tasks} "
          f"(rate={cost['spawn_call_rate']}) pass={pass_rate}% wall={wall_sec}s")

if __name__ == "__main__":
    main()
