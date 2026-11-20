#!/usr/bin/env python3
"""baize_posttrain_r126_deepseek_trajectory_analysis.py — DeepSeek Golden Trajectory Analysis.

R126 (2026-11-10 wake173): Deep analysis of 103 DeepSeek full-harness EDA-Eval
traces to extract tool-use patterns, error recovery strategies, API usage
distributions, and conversation structure.

All CPU, zero GPU. Surrogate analysis results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import json, os, sys, re, time, logging
from typing import Any, Dict, List, Optional
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)
TRACE_DIR = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace")
DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")

TOOL_CALL_RE = re.compile(
    r'<use_mcp_tool>\s*<server_name>([^<]+)</server_name>\s*'
    r'<tool_name>([^<]+)</tool_name>\s*<arguments>(.*?)</arguments>', re.DOTALL)
THINKING_RE = re.compile(r'<thinking>(.*?)</thinking>', re.DOTALL)
CODE_BLOCK_RE = re.compile(r'```python\s*(.*?)```', re.DOTALL)
MCP_RESULT_RE = re.compile(
    r"\[use_mcp_tool for '([^']+)'\] Result:\s*(.*?)(?=\[use_mcp_tool|\[attempt_completion|<environment_details>|\Z)", re.DOTALL)
ATTEMPT_COMPLETION_RE = re.compile(
    r'<attempt_completion>.*?<command>(.*?)</command>.*?</attempt_completion>', re.DOTALL)
ERROR_INDICATORS = ["error", "Error", "Traceback", "Exception", "failed",
    "Failed", "TypeError", "AttributeError", "ImportError", "SyntaxError",
    "KeyError", "ValueError", "NameError", "IndexError"]

class TrajectoryAnalyzer:
    """Analyze a single DeepSeek trajectory (conversation history)."""
    def __init__(self, task_id, messages):
        self.task_id = task_id
        self.messages = messages

    def extract_tool_calls(self):
        calls = []
        for i, msg in enumerate(self.messages):
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                text = block.get("text", "")
                for m in TOOL_CALL_RE.finditer(text):
                    server, tool, args = m.group(1), m.group(2), m.group(3)
                    try:
                        args_dict = json.loads(args.strip())
                    except (json.JSONDecodeError, ValueError):
                        args_dict = {"raw": args.strip()[:200]}
                    calls.append({"msg_idx": i, "server": server.strip(),
                        "tool": tool.strip(), "args": args_dict})
        return calls

    def extract_tool_results(self):
        results = []
        for i, msg in enumerate(self.messages):
            if msg.get("role") != "user":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                text = block.get("text", "")
                for m in MCP_RESULT_RE.finditer(text):
                    server = m.group(1)
                    result_text = m.group(2).strip()
                    has_error = any(e in result_text for e in ERROR_INDICATORS)
                    results.append({"msg_idx": i, "server": server.strip(),
                        "result_length": len(result_text),
                        "has_error": has_error, "preview": result_text[:200]})
        return results

    def extract_code_blocks(self):
        blocks = []
        for msg in self.messages:
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                for m in CODE_BLOCK_RE.finditer(block.get("text", "")):
                    blocks.append(m.group(1).strip())
        return blocks

    def extract_thinking(self):
        thoughts = []
        for msg in self.messages:
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                for m in THINKING_RE.finditer(block.get("text", "")):
                    thoughts.append(m.group(1).strip())
        return thoughts

    def get_api_names_from_tool_calls(self):
        api_names = []
        for call in self.extract_tool_calls():
            tool = call["tool"]
            args = call.get("args", {})
            if tool == "search_apis":
                q = args.get("query", "")
                if q:
                    api_names.append("search:" + q)
            elif tool == "get_api_details":
                names = args.get("api_names", args.get("api_list", []))
                if isinstance(names, str):
                    names = [names]
                if isinstance(names, list):
                    for n in names:
                        api_names.append("detail:" + str(n))
            elif tool == "run_pyAether_code_tool":
                code = args.get("code", "")
                for m in re.finditer(r'pyScript\.([a-zA-Z_][a-zA-Z0-9_.]*)', code):
                    api_names.append("use:" + m.group(1))
        return api_names

    def get_error_recovery_events(self):
        events = []
        tool_results = self.extract_tool_results()
        tool_calls = self.extract_tool_calls()
        for tr in tool_results:
            if not tr["has_error"]:
                continue
            next_calls = [c for c in tool_calls if c["msg_idx"] > tr["msg_idx"]][:1]
            events.append({"error_msg_idx": tr["msg_idx"],
                "error_preview": tr["preview"],
                "recovery_tool": next_calls[0]["tool"] if next_calls else None,
                "recovery_args": next_calls[0]["args"] if next_calls else None})
        return events

    def get_completion_command(self):
        for msg in reversed(self.messages):
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                m = ATTEMPT_COMPLETION_RE.search(block.get("text", ""))
                if m:
                    return m.group(1).strip()
        return None

    def analyze(self):
        tool_calls = self.extract_tool_calls()
        tool_results = self.extract_tool_results()
        code_blocks = self.extract_code_blocks()
        thinking = self.extract_thinking()
        errors = self.get_error_recovery_events()
        api_names = self.get_api_names_from_tool_calls()
        tool_seq = [c["tool"] for c in tool_calls]
        compressed_seq = []
        for t in tool_seq:
            if not compressed_seq or compressed_seq[-1] != t:
                compressed_seq.append(t)
        used_apis = [n.split(":", 1)[1] for n in api_names if n.startswith("use:")]
        searched_apis = [n.split(":", 1)[1] for n in api_names if n.startswith("search:")]
        detailed_apis = [n.split(":", 1)[1] for n in api_names if n.startswith("detail:")]
        final_code = code_blocks[-1] if code_blocks else None
        has_import = bool(final_code and "import pyAether" in final_code)
        has_entry = bool(final_code and re.search(r"def\s+\w+\s*\(", final_code))
        loc = final_code.count("\n") + 1 if final_code else 0
        return {
            "task_id": self.task_id,
            "n_messages": len(self.messages),
            "n_assistant_turns": sum(1 for m in self.messages if m.get("role") == "assistant"),
            "n_tool_calls": len(tool_calls),
            "n_tool_results": len(tool_results),
            "n_error_results": sum(1 for tr in tool_results if tr["has_error"]),
            "n_code_blocks": len(code_blocks),
            "n_thinking_blocks": len(thinking),
            "tool_sequence": tool_seq,
            "compressed_sequence": compressed_seq,
            "tool_frequency": dict(Counter(tool_seq)),
            "searched_queries": searched_apis,
            "detailed_apis": detailed_apis,
            "used_apis_in_code": list(set(used_apis)),
            "n_unique_apis_used": len(set(used_apis)),
            "n_error_recoveries": len(errors),
            "error_recovery_events": errors[:5],
            "final_code_loc": loc,
            "final_code_has_import": has_import,
            "final_code_has_entry_point": has_entry,
            "completion_command": self.get_completion_command(),
            "thinking_total_chars": sum(len(t) for t in thinking),
        }

class BatchAnalyzer:
    """Analyze all 103 DeepSeek trajectories and aggregate statistics."""
    def __init__(self, trace_dir=TRACE_DIR):
        self.trace_dir = trace_dir
        self.task_ids = []
        self.results = []
        self._dataset = {}

    def _load_dataset(self):
        if not os.path.exists(DATASET_PATH):
            logger.warning("Dataset not found: %s", DATASET_PATH)
            return
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                task = json.loads(line)
                tid = task.get("task_id", task.get("id", ""))
                if tid:
                    self._dataset[tid] = task

    def run(self):
        self._load_dataset()
        if not os.path.isdir(self.trace_dir):
            return {"error": "Trace dir not found: " + self.trace_dir}
        self.task_ids = sorted(os.listdir(self.trace_dir))
        logger.info("Found %d task traces", len(self.task_ids))
        t0 = time.time()
        for tid in self.task_ids:
            hist_path = os.path.join(self.trace_dir, tid, "api_conversation_history.json")
            if not os.path.exists(hist_path):
                continue
            try:
                with open(hist_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                analyzer = TrajectoryAnalyzer(tid, messages)
                result = analyzer.analyze()
                ds = self._dataset.get(tid, {})
                meta = ds.get("metadata", {})
                result["scenario"] = meta.get("scenario", "unknown")
                result["category"] = meta.get("category", "unknown")
                result["n_unique_apis_metadata"] = meta.get("num_unique_apis", 0)
                result["techlib_dependency"] = meta.get("techlib_dependency", False)
                self.results.append(result)
            except Exception as e:
                logger.error("Failed to analyze %s: %s", tid, e)
                self.results.append({"task_id": tid, "error": str(e)})
        elapsed = time.time() - t0
        logger.info("Analyzed %d trajectories in %.2fs", len(self.results), elapsed)
        return self._aggregate(elapsed)

    def _aggregate(self, elapsed):
        valid = [r for r in self.results if "error" not in r]
        n = len(valid)
        if n == 0:
            return {"error": "No valid trajectories", "elapsed": elapsed}
        msg_counts = [r["n_messages"] for r in valid]
        assistant_turns = [r["n_assistant_turns"] for r in valid]
        tool_call_counts = [r["n_tool_calls"] for r in valid]
        code_block_counts = [r["n_code_blocks"] for r in valid]
        thinking_counts = [r["n_thinking_blocks"] for r in valid]
        thinking_chars = [r["thinking_total_chars"] for r in valid]
        all_tools = Counter()
        for r in valid:
            all_tools.update(r["tool_frequency"])
        seq_patterns = Counter()
        for r in valid:
            seq_patterns[tuple(r["compressed_sequence"])] += 1
        error_counts = [r["n_error_results"] for r in valid]
        recovery_counts = [r["n_error_recoveries"] for r in valid]
        recovery_tools = Counter()
        for r in valid:
            for ev in r.get("error_recovery_events", []):
                if ev.get("recovery_tool"):
                    recovery_tools[ev["recovery_tool"]] += 1
        all_used_apis = Counter()
        all_searched = Counter()
        all_detailed = Counter()
        for r in valid:
            all_used_apis.update(r["used_apis_in_code"])
            all_searched.update(r["searched_queries"])
            all_detailed.update(r["detailed_apis"])
        locs = [r["final_code_loc"] for r in valid]
        has_import = sum(1 for r in valid if r["final_code_has_import"])
        has_entry = sum(1 for r in valid if r["final_code_has_entry_point"])
        scenario_stats = defaultdict(lambda: {
            "count": 0, "msg_sum": 0, "tool_sum": 0, "error_sum": 0,
            "recovery_sum": 0, "loc_sum": 0, "unique_apis_sum": 0})
        for r in valid:
            s = r["scenario"]
            scenario_stats[s]["count"] += 1
            scenario_stats[s]["msg_sum"] += r["n_messages"]
            scenario_stats[s]["tool_sum"] += r["n_tool_calls"]
            scenario_stats[s]["error_sum"] += r["n_error_results"]
            scenario_stats[s]["recovery_sum"] += r["n_error_recoveries"]
            scenario_stats[s]["loc_sum"] += r["final_code_loc"]
            scenario_stats[s]["unique_apis_sum"] += r["n_unique_apis_used"]
        scenario_summary = {}
        for s, v in scenario_stats.items():
            c = v["count"]
            scenario_summary[s] = {
                "count": c, "avg_messages": round(v["msg_sum"] / c, 1),
                "avg_tool_calls": round(v["tool_sum"] / c, 1),
                "avg_errors": round(v["error_sum"] / c, 1),
                "avg_recoveries": round(v["recovery_sum"] / c, 1),
                "avg_loc": round(v["loc_sum"] / c, 1),
                "avg_unique_apis": round(v["unique_apis_sum"] / c, 1)}
        est_tokens_per_msg = 125
        est_context = [mc * est_tokens_per_msg for mc in msg_counts]
        def stats(lst):
            if not lst:
                return {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0}
            s = sorted(lst)
            n2 = len(s)
            mean = sum(s) / n2
            median = s[n2 // 2]
            var = sum((x - mean) ** 2 for x in s) / n2
            return {"mean": round(mean, 2), "median": median,
                "min": s[0], "max": s[-1], "std": round(var ** 0.5, 2)}
        return {
            "meta": {"n_traces_found": len(self.task_ids),
                "n_traces_valid": n, "elapsed_s": round(elapsed, 2)},
            "1_conversation_structure": {
                "messages_per_task": stats(msg_counts),
                "assistant_turns_per_task": stats(assistant_turns),
                "tool_calls_per_task": stats(tool_call_counts),
                "code_blocks_per_task": stats(code_block_counts),
                "thinking_blocks_per_task": stats(thinking_counts),
                "thinking_chars_per_task": stats(thinking_chars),
                "est_context_tokens_per_task": stats(est_context),
            },
            "2_tool_usage_frequency": {
                "total_tool_calls": sum(tool_call_counts),
                "per_tool_count": dict(all_tools.most_common(20)),
                "per_tool_avg": {t: round(all_tools[t] / n, 2)
                    for t in [x[0] for x in all_tools.most_common(10)]},
            },
            "3_tool_sequence_patterns": {
                "unique_patterns": len(seq_patterns),
                "top_10_patterns": [
                    {"pattern": list(p), "count": c, "pct": round(c / n * 100, 1)}
                    for p, c in seq_patterns.most_common(10)],
            },
            "4_error_recovery": {
                "error_results_per_task": stats(error_counts),
                "recovery_events_per_task": stats(recovery_counts),
                "tasks_with_errors": sum(1 for e in error_counts if e > 0),
                "tasks_with_errors_pct": round(
                    sum(1 for e in error_counts if e > 0) / n * 100, 1),
                "recovery_tool_distribution": dict(recovery_tools.most_common(10)),
            },
            "5_api_usage": {
                "unique_apis_used_in_code": len(all_used_apis),
                "top_20_used_apis": all_used_apis.most_common(20),
                "top_20_searched_queries": all_searched.most_common(20),
                "top_20_detailed_apis": all_detailed.most_common(20),
                "avg_unique_apis_per_task": stats(
                    [r["n_unique_apis_used"] for r in valid]),
            },
            "6_code_structure": {
                "loc_stats": stats(locs),
                "has_import_pct": round(has_import / n * 100, 1),
                "has_entry_point_pct": round(has_entry / n * 100, 1),
            },
            "7_per_scenario": scenario_summary,
            "8_implications": self._derive_implications(
                n, msg_counts, tool_call_counts, error_counts,
                recovery_counts, est_context, all_tools, seq_patterns,
                all_used_apis, locs),
            "per_task_details": self.results[:20],
        }

    def _derive_implications(self, n, msg_counts, tool_counts, error_counts,
            recovery_counts, est_context, all_tools, seq_patterns,
            all_used_apis, locs):
        avg_tools = sum(tool_counts) / n
        avg_msgs = sum(msg_counts) / n
        avg_errors = sum(error_counts) / n
        avg_ctx = sum(est_context) / n
        p90_ctx = sorted(est_context)[int(n * 0.9)] if n > 5 else max(est_context)
        max_ctx = max(est_context) if est_context else 0
        if p90_ctx < 4096:
            ctx_rec = "4096"
        elif p90_ctx < 8192:
            ctx_rec = "8192"
        elif p90_ctx < 16384:
            ctx_rec = "16384"
        else:
            ctx_rec = "32768"
        top_seq = seq_patterns.most_common(1)[0] if seq_patterns else ((), 0)
        return {
            "sft_context_length": {
                "recommended": ctx_rec,
                "p50_tokens": int(avg_ctx),
                "p90_tokens": int(p90_ctx),
                "max_tokens": int(max_ctx),
                "rationale": "90th percentile ≈" + str(int(p90_ctx)) + " tokens; recommend " + ctx_rec,
            },
            "sft_data_quality": {
                "avg_tool_calls_per_task": round(avg_tools, 1),
                "avg_messages_per_task": round(avg_msgs, 1),
                "golden_pattern": list(top_seq[0]) if top_seq[0] else [],
                "golden_pattern_pct": round(top_seq[1] / n * 100, 1) if top_seq[1] else 0,
                "implication": "SFT trajectories should follow search->detail->run pattern",
            },
            "rl_reward_design": {
                "avg_errors_per_task": round(avg_errors, 1),
                "tasks_with_errors_pct": round(
                    sum(1 for e in error_counts if e > 0) / n * 100, 1),
                "avg_recoveries_per_task": round(sum(recovery_counts) / n, 1),
                "implication": "Error recovery is common -> RL should reward successful recovery",
            },
            "api_diversity": {
                "unique_apis_in_traces": len(all_used_apis),
                "top_5": all_used_apis.most_common(5),
                "implication": str(len(all_used_apis)) + " unique APIs used across " + str(n) + " tasks",
            },
            "code_complexity": {
                "avg_loc": round(sum(locs) / n, 1),
                "max_loc": max(locs) if locs else 0,
                "implication": "Average solution is short; focus reward on correctness",
            },
        }


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print("=" * 72)
    print("R126: DeepSeek Golden Trajectory Analysis (103 traces)")
    print("=" * 72)
    analyzer = BatchAnalyzer()
    results = analyzer.run()
    if "error" in results:
        print("ERROR: " + results["error"])
        sys.exit(1)
    print("\n[Meta] Traces found:", results["meta"]["n_traces_found"],
          "valid:", results["meta"]["n_traces_valid"],
          "elapsed:", results["meta"]["elapsed_s"], "s")
    s1 = results["1_conversation_structure"]
    print("\n[1. Conversation Structure]")
    for k, v in s1.items():
        print("  " + k + ": mean=" + str(v["mean"]) + " median=" + str(v["median"]) +
              " min=" + str(v["min"]) + " max=" + str(v["max"]) + " std=" + str(v["std"]))
    s2 = results["2_tool_usage_frequency"]
    print("\n[2. Tool Usage] Total calls:", s2["total_tool_calls"])
    for tool, cnt in s2["per_tool_count"].items():
        print("  " + tool + ": " + str(cnt) + " (avg " + str(s2["per_tool_avg"].get(tool, 0)) + "/task)")
    s3 = results["3_tool_sequence_patterns"]
    print("\n[3. Tool Sequences]", s3["unique_patterns"], "unique patterns")
    for p in s3["top_10_patterns"]:
        print("  " + " -> ".join(p["pattern"]) + ": " + str(p["count"]) + " (" + str(p["pct"]) + "%)")
    s4 = results["4_error_recovery"]
    print("\n[4. Error Recovery]")
    print("  Errors/task: mean=" + str(s4["error_results_per_task"]["mean"]))
    print("  Tasks with errors:", str(s4["tasks_with_errors_pct"]) + "%")
    print("  Recovery tools:", s4["recovery_tool_distribution"])
    s5 = results["5_api_usage"]
    print("\n[5. API Usage]", s5["unique_apis_used_in_code"], "unique APIs")
    print("  Top 5 used:", s5["top_20_used_apis"][:5])
    print("  Avg unique APIs/task:", s5["avg_unique_apis_per_task"]["mean"])
    s6 = results["6_code_structure"]
    print("\n[6. Code Structure] LOC mean=" + str(s6["loc_stats"]["mean"]) +
          " max=" + str(s6["loc_stats"]["max"]))
    print("  Has import:", str(s6["has_import_pct"]) + "%",
          "Has entry point:", str(s6["has_entry_point_pct"]) + "%")
    s7 = results["7_per_scenario"]
    print("\n[7. Per-Scenario]")
    for s, v in s7.items():
        print("  " + s + ": count=" + str(v["count"]) + " avg_msgs=" + str(v["avg_messages"]) +
              " avg_tools=" + str(v["avg_tool_calls"]) + " avg_errors=" + str(v["avg_errors"]))
    s8 = results["8_implications"]
    print("\n[8. Implications for SFT/RL Design]")
    print("  SFT context length:", s8["sft_context_length"]["recommended"],
          "(p90≈" + str(s8["sft_context_length"]["p90_tokens"]) + " tok)")
    print("  Golden pattern:", " -> ".join(s8["sft_data_quality"]["golden_pattern"]),
          "(" + str(s8["sft_data_quality"]["golden_pattern_pct"]) + "%)")
    print("  Error recovery:", str(s8["rl_reward_design"]["tasks_with_errors_pct"]) + "% tasks have errors")
    print("  API diversity:", s8["api_diversity"]["unique_apis_in_traces"], "unique APIs")
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "r126_trajectory_analysis_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n[Saved]", out_path, "(" + str(os.path.getsize(out_path)) + " bytes)")
    print("\n✅ R126 analysis complete.")

if __name__ == "__main__":
    main()
