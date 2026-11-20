#!/usr/bin/env python3
"""R60: Context Window Budget Analyzer for Multi-Turn EDA RL.

Analyzes DeepSeek full-harness traces (103 tasks) to measure real token
consumption, projects context window budgets for MiniCPM5-2B on 4xA40,
estimates KV-cache memory, and designs truncation / context management
strategy for RL training.

Usage:
  python3 baize_posttrain_ctx_budget_analyzer.py [--json OUT] [--html OUT]
  python3 baize_posttrain_ctx_budget_analyzer.py --dry-run   # quick stats only

Dependencies: Python 3.8+, zero external packages.
Data source: ~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/
"""
import json, os, sys, math, argparse, html as html_mod
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────
TRACE_DIR = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace/"
)
CHAR_PER_TOK = 3.8  # mixed English+code; Chinese~2.5, code~3.5, English~4.5
SYS_PROMPT_TOK = 500
TASK_PROMPT_TOK = 200

# MiniCPM5-2B architecture (from config.json)
MODEL_CONFIG = {
    "max_position_embeddings": 131072,
    "hidden_size": 2048,
    "num_hidden_layers": 42,
    "num_attention_heads": 16,
    "num_key_value_heads": 2,  # GQA
    "head_dim": 2048 // 16,    # 128
    "vocab_size": 130560,
    "torch_dtype": "bfloat16",
}

# A40 specs
A40_MEM_GB = 46.0
A40_MEM_USABLE_GB = 44.0  # reserve ~2GB for CUDA context
N_GPUS = 4

# Context windows to evaluate
CTX_WINDOWS = [4096, 8192, 16384, 32768, 65536]


def char_to_tok(n):
    return n / CHAR_PER_TOK


def analyze_trace(conv_path):
    """Analyze one api_conversation_history.json."""
    with open(conv_path) as f:
        conv = json.load(f)
    if not isinstance(conv, list):
        return None
    turns = []
    total_chars = 0
    roles = {}
    for msg in conv:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if isinstance(content, list):
            chars = sum(len(str(p)) for p in content)
        elif isinstance(content, str):
            chars = len(content)
        else:
            chars = len(str(content))
        total_chars += chars
        roles[role] = roles.get(role, 0) + chars
        turns.append({"role": role, "chars": chars, "tokens": char_to_tok(chars)})
    return {"n_messages": len(conv), "total_chars": total_chars,
            "total_tokens_est": char_to_tok(total_chars),
            "roles": roles, "turns": turns}


def analyze_ui_messages(ui_path):
    """Analyze ui_messages.json for tool call patterns."""
    with open(ui_path) as f:
        ui = json.load(f)
    if not isinstance(ui, list):
        return None
    say_types = {}
    for m in ui:
        if not isinstance(m, dict):
            continue
        say = m.get("say", "?")
        say_types[say] = say_types.get(say, 0) + 1
    tool_calls = say_types.get("use_mcp_server", 0)
    tool_responses = say_types.get("mcp_server_response", 0)
    api_requests = say_types.get("api_req_started", 0)
    return {"say_types": say_types, "tool_calls": tool_calls,
            "tool_responses": tool_responses, "api_requests": api_requests,
            "n_ui_messages": len(ui)}


def compute_stats(arr):
    """Compute percentile stats for an array."""
    if not arr:
        return {}
    arr_s = sorted(arr)
    n = len(arr_s)
    mean = sum(arr_s) / n
    def pct(p):
        idx = min(int(n * p), n - 1)
        return arr_s[idx]
    return {"mean": round(mean, 1), "median": arr_s[n // 2],
            "p25": pct(0.25), "p75": pct(0.75),
            "p90": pct(0.90), "p95": pct(0.95), "p99": pct(0.99),
            "min": arr_s[0], "max": arr_s[-1], "n": n}


def kv_cache_mem_gb(ctx_len, batch_size=1):
    """Estimate KV cache memory for MiniCPM5-2B at given context length.

    KV cache = 2 (K+V) * n_layers * n_kv_heads * head_dim * ctx_len * batch * 2 bytes (bf16)
    """
    cfg = MODEL_CONFIG
    # Per-token KV cache: 2 * n_layers * n_kv_heads * head_dim * 2 bytes
    per_token_bytes = (2 * cfg["num_hidden_layers"] * cfg["num_key_value_heads"]
                       * cfg["head_dim"] * 2)  # bf16=2 bytes
    per_token_gb = per_token_bytes / (1024**3)
    total_gb = per_token_gb * ctx_len * batch_size
    return {"per_token_bytes": per_token_bytes, "per_token_gb": per_token_gb,
            "total_gb": total_gb, "ctx_len": ctx_len, "batch_size": batch_size}


def model_weights_gb():
    """2B params in bf16 = 2B * 2 bytes / 1024^3."""
    return 2.0e9 * 2 / (1024**3)  # ~3.73 GB


def run_analysis():
    """Main analysis: returns dict with all results."""
    if not os.path.isdir(TRACE_DIR):
        return {"error": f"trace dir not found: {TRACE_DIR}"}
    
    task_dirs = sorted([d for d in os.listdir(TRACE_DIR)
                        if os.path.isdir(os.path.join(TRACE_DIR, d))])
    
    trace_results = []
    ui_results = []
    
    for td in task_dirs:
        conv_path = os.path.join(TRACE_DIR, td, "api_conversation_history.json")
        ui_path = os.path.join(TRACE_DIR, td, "ui_messages.json")
        if os.path.exists(conv_path):
            try:
                r = analyze_trace(conv_path)
                if r:
                    r["task_id"] = td
                    trace_results.append(r)
            except Exception:
                pass
        if os.path.exists(ui_path):
            try:
                u = analyze_ui_messages(ui_path)
                if u:
                    u["task_id"] = td
                    ui_results.append(u)
            except Exception:
                pass
    
    n_traces = len(trace_results)
    if n_traces == 0:
        return {"error": "no traces analyzed"}
    
    # Token stats
    n_msgs = [r["n_messages"] for r in trace_results]
    total_toks = [r["total_tokens_est"] for r in trace_results]
    all_turn_toks = [t["tokens"] for r in trace_results for t in r["turns"]]
    
    # Tool call stats from ui_messages
    tool_calls_arr = [u["tool_calls"] for u in ui_results] if ui_results else []
    api_reqs_arr = [u["api_requests"] for u in ui_results] if ui_results else []
    
    # Role breakdown
    role_chars = {}
    for r in trace_results:
        for role, chars in r["roles"].items():
            role_chars[role] = role_chars.get(role, 0) + chars
    
    # Context window projections
    ctx_projections = {}
    for ctx in CTX_WINDOWS:
        usable = ctx - SYS_PROMPT_TOK - TASK_PROMPT_TOK
        fits = sum(1 for t in total_toks if t <= usable)
        truncated = n_traces - fits
        # Simulate truncation: count how many turns/tool_calls are lost
        lost_turns = 0
        total_turns = sum(r["n_messages"] for r in trace_results)
        for r in trace_results:
            if r["total_tokens_est"] > usable:
                remaining = usable
                turns_in = 0
                for t in r["turns"]:
                    if remaining <= 0:
                        break
                    if t["tokens"] <= remaining:
                        remaining -= t["tokens"]
                        turns_in += 1
                    else:
                        remaining = 0
                lost_turns += (r["n_messages"] - turns_in)
        ctx_projections[str(ctx)] = {
            "ctx_len": ctx, "usable": usable,
            "tasks_fitting": fits, "tasks_total": n_traces,
            "fit_pct": round(fits / n_traces * 100, 1),
            "truncated": truncated,
            "trunc_pct": round(truncated / n_traces * 100, 1),
            "turns_lost": lost_turns,
            "turns_total": total_turns,
            "turn_loss_pct": round(lost_turns / max(1, total_turns) * 100, 1),
        }
    
    # KV cache memory estimates
    weights_gb = model_weights_gb()
    kv_estimates = {}
    for ctx in CTX_WINDOWS:
        # For RL rollout: batch_size = max_num_seqs
        for bs in [1, 4, 8, 12]:
            kv = kv_cache_mem_gb(ctx, bs)
            # Total per-GPU memory: weights (sharded across 4 GPUs) + KV + activations
            weights_per_gpu = weights_gb / N_GPUS
            # Rough activation estimate: ~0.5x KV for backward
            activation_est = kv["total_gb"] * 0.3
            total_per_gpu = weights_per_gpu + kv["total_gb"] + activation_est
            key = f"ctx{ctx}_bs{bs}"
            kv_estimates[key] = {
                "ctx_len": ctx, "batch_size": bs,
                "kv_cache_gb": round(kv["total_gb"], 3),
                "weights_per_gpu_gb": round(weights_per_gpu, 3),
                "activation_est_gb": round(activation_est, 3),
                "total_per_gpu_gb": round(total_per_gpu, 3),
                "fits_in_a40": total_per_gpu <= A40_MEM_USABLE_GB,
                "remaining_gb": round(A40_MEM_USABLE_GB - total_per_gpu, 3),
            }
    
    return {
        "n_traces": n_traces,
        "n_ui_traces": len(ui_results),
        "messages_stats": compute_stats(n_msgs),
        "total_tokens_stats": compute_stats(total_toks),
        "turn_tokens_stats": compute_stats(all_turn_toks),
        "tool_calls_stats": compute_stats(tool_calls_arr) if tool_calls_arr else {},
        "api_requests_stats": compute_stats(api_reqs_arr) if api_reqs_arr else {},
        "role_breakup_toks": {k: round(char_to_tok(v)) for k, v in role_chars.items()},
        "char_per_tok": CHAR_PER_TOK,
        "model_config": MODEL_CONFIG,
        "model_weights_gb": round(weights_gb, 2),
        "a40_mem_gb": A40_MEM_GB,
        "a40_usable_gb": A40_MEM_USABLE_GB,
        "n_gpus": N_GPUS,
        "ctx_projections": ctx_projections,
        "kv_estimates": kv_estimates,
        "analysis_time": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="R60: Context Window Budget Analyzer for Multi-Turn EDA RL")
    parser.add_argument("--json", default=None, help="Output JSON path")
    parser.add_argument("--html", default=None, help="Output HTML report path")
    parser.add_argument("--dry-run", action="store_true", help="Quick stats only")
    args = parser.parse_args()

    data = run_analysis()
    if "error" in data:
        print(f"ERROR: {data['error']}")
        sys.exit(1)

    if args.dry_run:
        ts = data["total_tokens_stats"]
        ms = data["messages_stats"]
        print(f"Traces: {data['n_traces']}")
        print(f"Messages/task: median={ms['median']} mean={ms['mean']}")
        print(f"Tokens/task: median={ts['median']:.0f} mean={ts['mean']:.0f}")
        for ctx_str, p in data["ctx_projections"].items():
            print(f"  ctx={p['ctx_len']}: fit={p['fit_pct']}% trunc={p['trunc_pct']}%")
        return

    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON saved to {args.json}")

    if args.html:
        ok = generate_html(data, args.html)
        if ok:
            print(f"HTML saved to {args.html}")
        else:
            print(f"HTML generation failed")

    # Always print summary
    ts = data["total_tokens_stats"]
    ms = data["messages_stats"]
    print(f"\n{'='*60}")
    print(f"R60 Context Window Budget Analysis")
    print(f"{'='*60}")
    print(f"Traces analyzed: {data['n_traces']}")
    print(f"Messages/task: median={ms['median']} mean={ms['mean']}")
    print(f"Tokens/task: median={ts['median']:.0f} mean={ts['mean']:.0f}")
    print(f"\nContext window fit rates:")
    for ctx_str, p in data["ctx_projections"].items():
        print(f"  ctx={p['ctx_len']:>6}: fit={p['fit_pct']:>5}%  trunc={p['trunc_pct']:>5}%  turn_loss={p['turn_loss_pct']:>5}%")
    print(f"\nKV cache (ctx=32768, bs=8): {data['kv_estimates']['ctx32768_bs8']['kv_cache_gb']:.2f}GB, total={data['kv_estimates']['ctx32768_bs8']['total_per_gpu_gb']:.2f}GB/GPU, fits={data['kv_estimates']['ctx32768_bs8']['fits_in_a40']}")


if __name__ == "__main__":
    main()
