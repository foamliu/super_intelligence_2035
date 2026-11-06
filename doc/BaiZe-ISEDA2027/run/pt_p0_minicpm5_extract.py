#!/usr/bin/env python3
"""
pt_p0_minicpm5_extract.py — MiniCPM5-2B D1-D6 诊断指标提取脚本

从 ~/eda_code_eval/ 下 MiniCPM5-2B 评测轨迹提取 D1-D6 六项诊断指标。
基于 DeepSeek 侧提取逻辑（/tmp/pt_p0_analyze.py），适配 MiniCPM5-2B 轨迹路径。

用法:
  python pt_p0_minicpm5_extract.py --eval-dir ~/eda_code_eval --dataset <jsonl> --trace-reader <path> --eda-base <path>
  python pt_p0_minicpm5_extract.py --dry-run  # 仅打印将扫描的路径
"""
import json, os, sys, argparse, importlib.util, statistics
from collections import Counter, defaultdict
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description="MiniCPM5-2B D1-D6 提取")
    ap.add_argument("--eval-dir", default=os.path.expanduser("~/eda_code_eval"), help="评测输出根目录")
    ap.add_argument("--dataset", required=True, help="158-case JSONL 数据集路径")
    ap.add_argument("--trace-reader", required=True, help="trace_reader.py 路径")
    ap.add_argument("--eda-base", required=True, help="eda_fastmcp 根目录")
    ap.add_argument("--output", default=None, help="输出 JSON 路径")
    ap.add_argument("--dry-run", action="store_true", help="仅打印路径")
    args = ap.parse_args()

    EDA = args.eda_base
    EVAL_DIR = args.eval_dir
    DATASET = args.dataset

    # 加载 trace_parser
    tp_path = os.path.join(EDA, "memory_bank", "trace_parser.py")
    if not os.path.isfile(tp_path):
        print(f"❌ trace_parser.py 不存在: {tp_path}", file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("tp", tp_path)
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)

    # 加载 trace_reader
    tr_path = args.trace_reader
    sys.path.insert(0, os.path.dirname(tr_path))
    from trace_reader import load_trace

    # 加载数据集元数据
    dataset = {}
    scenario_count = Counter()
    with open(DATASET) as f:
        for line in f:
            d = json.loads(line)
            tid = d["task_id"]
            m = d.get("metadata", {})
            dataset[tid] = m
            scenario_count[m.get("scenario", "Unknown")] += 1

    # 发现评测运行目录
    run_dirs = []
    if os.path.isdir(EVAL_DIR):
        for d in sorted(os.listdir(EVAL_DIR)):
            full = os.path.join(EVAL_DIR, d)
            if os.path.isdir(full) and "minicpm5" in d.lower():
                run_dirs.append(full)

    if args.dry_run:
        print(f"[dry-run] eval_dir: {EVAL_DIR}")
        print(f"[dry-run] dataset: {DATASET} ({len(dataset)} tasks)")
        print(f"[dry-run] run_dirs found: {len(run_dirs)}")
        for rd in run_dirs:
            print(f"  {rd}")
        return

    if not run_dirs:
        print(f"⚠️ 未在 {EVAL_DIR} 下找到 minicpm5 相关运行目录", file=sys.stderr)
        print(f"   将扫描所有子目录...", file=sys.stderr)
        if os.path.isdir(EVAL_DIR):
            for d in sorted(os.listdir(EVAL_DIR)):
                full = os.path.join(EVAL_DIR, d)
                if os.path.isdir(full):
                    run_dirs.append(full)

    all_results = []

    for run_dir in run_dirs:
        # 查找 trace 目录
        trace_dir = None
        for candidate in ["trace", "cline_trace", "traces"]:
            p = os.path.join(run_dir, candidate)
            if os.path.isdir(p):
                trace_dir = p
                break
        if trace_dir is None:
            # 查找嵌套的 trace 目录
            for root, dirs, files in os.walk(run_dir):
                if "api_conversation_history.json" in files or any(f.endswith(".messages.json") for f in files):
                    trace_dir = root
                    break
                for d in dirs:
                    if "trace" in d.lower():
                        trace_dir = os.path.join(root, d)
                        break
                if trace_dir:
                    break

        if trace_dir is None:
            print(f"  ⚠️ {run_dir}: 未找到 trace 目录，跳过")
            continue

        trace_subdirs = [d for d in sorted(os.listdir(trace_dir)) if os.path.isdir(os.path.join(trace_dir, d))]
        if not trace_subdirs:
            trace_subdirs = [""]  # trace_dir 本身可能包含 trace 文件

        all_tool_calls = 0
        all_tool_results = 0
        tool_name_counter = Counter()
        err_type_counter = Counter()
        n_code_exec_per_task = []
        n_tool_calls_per_task = []
        n_msgs_per_task = []
        n_errors_per_task = []
        has_timeout = 0
        has_assertion_err = 0
        has_exec_err = 0
        n_traces_ok = 0
        assistant_turns = 0
        n_total = len(trace_subdirs)
        per_scenario_pass = defaultdict(lambda: [0, 0])

        for td in trace_subdirs:
            tpath = os.path.join(trace_dir, td) if td else trace_dir
            if not os.path.isdir(tpath):
                continue
            try:
                tr = load_trace(tpath)
            except Exception:
                continue

            tcs = tp.extract_tool_calls_from_trace(tr)
            trs = tp.extract_tool_results_from_trace(tr)
            n_traces_ok += 1

            all_tool_calls += len(tcs)
            all_tool_results += len(trs)
            for c in tcs:
                tool_name_counter[c.get("tool", "?")] += 1
            n_tool_calls_per_task.append(len(tcs))
            n_msgs_per_task.append(len(tr))

            for m in tr:
                if isinstance(m, dict) and m.get("role") == "assistant":
                    assistant_turns += 1

            errs = [r for r in trs if r.get("has_error") in (True, "True", "true")]
            n_errors_per_task.append(len(errs))

            n_exec = 0
            for c in tcs:
                if c.get("tool") in ("run_pyAether_code_tool", "run_code", "probe_pyAether_code"):
                    n_exec += 1
            n_code_exec_per_task.append(n_exec)

            for r in errs:
                ec = r.get("error_code", "UNKNOWN")
                err_type_counter[ec] += 1
                if ec == "ASSERTION_ERROR":
                    has_assertion_err += 1
                elif ec in ("SANDBOX_TIMEOUT", "TIMEOUT", "TIME_OUT"):
                    has_timeout += 1
                else:
                    has_exec_err += 1

        # 查找 final_report.json
        final_report = None
        for root, dirs, files in os.walk(run_dir):
            if "final_report.json" in files:
                rp = os.path.join(root, "final_report.json")
                try:
                    final_report = json.load(open(rp))
                except Exception:
                    pass
                break

        # D5 per-scenario pass rate
        if final_report:
            det = final_report.get("details_per_task", {})
            for tid, v in det.items():
                meta = dataset.get(tid, {})
                sc = meta.get("scenario", "Unknown")
                correct = v.get("num_correct", 0)
                total = v.get("num_samples", 1)
                per_scenario_pass[sc][0] += correct
                per_scenario_pass[sc][1] += total

        spr = {}
        for sc, (c, t) in sorted(per_scenario_pass.items()):
            spr[sc] = {"pass": c, "total": t, "rate": round(c / t, 4) if t else 0}

        d1 = (all_tool_calls / assistant_turns) if assistant_turns else 0
        d2 = (all_tool_calls / n_traces_ok) if n_traces_ok else 0
        d3r = (has_timeout / n_traces_ok) if n_traces_ok else 0

        result = {
            "run_dir": run_dir,
            "trace_dir": trace_dir,
            "n_trace_dirs": n_total,
            "n_traces_parsed": n_traces_ok,
            "D1_legality_proxy": round(d1, 4),
            "D2_freq_per_task": round(d2, 2),
            "D2_tool_breakdown": dict(tool_name_counter.most_common()),
            "D3_timeout_tasks": has_timeout,
            "D3_timeout_ratio": round(d3r, 4),
            "D4_error_breakdown": dict(err_type_counter.most_common()),
            "D4_assertion_err_tasks": has_assertion_err,
            "D4_exec_err_tasks": has_exec_err,
            "D5_per_scenario": spr,
            "D6_exec_per_task_mean": round(statistics.mean(n_code_exec_per_task), 2) if n_code_exec_per_task else 0,
            "D6_exec_per_task_median": statistics.median(n_code_exec_per_task) if n_code_exec_per_task else 0,
            "D6_exec_per_task_dist": dict(Counter(n_code_exec_per_task).most_common()),
            "avg_msgs_per_task": round(statistics.mean(n_msgs_per_task), 1) if n_msgs_per_task else 0,
            "avg_tool_calls_per_task": round(statistics.mean(n_tool_calls_per_task), 2) if n_tool_calls_per_task else 0,
            "avg_errors_per_task": round(statistics.mean(n_errors_per_task), 2) if n_errors_per_task else 0,
            "final_report_pass_rate": final_report.get("metrics", {}).get("pass_rate") if final_report else None,
        }
        all_results.append(result)

    summary = {
        "model": "MiniCPM5-2B",
        "generated_on": os.uname().nodename + " (" + os.popen("date '+%F %T'").read().strip() + ")",
        "dataset": {"n_tasks": len(dataset), "scenario_dist": dict(scenario_count.most_common())},
        "runs": all_results,
    }

    if all_results:
        # 跨 run 汇总
        d1s = [r["D1_legality_proxy"] for r in all_results if r["n_traces_parsed"] > 0]
        d2s = [r["D2_freq_per_task"] for r in all_results if r["n_traces_parsed"] > 0]
        d6s = [r["D6_exec_per_task_mean"] for r in all_results if r["n_traces_parsed"] > 0]
        pass_rates = [r["final_report_pass_rate"] for r in all_results if r["final_report_pass_rate"] is not None]
        summary["aggregate"] = {
            "n_runs": len(all_results),
            "D1_mean": round(statistics.mean(d1s), 4) if d1s else None,
            "D1_std": round(statistics.pstdev(d1s), 4) if len(d1s) > 1 else 0,
            "D2_mean": round(statistics.mean(d2s), 2) if d2s else None,
            "D2_std": round(statistics.pstdev(d2s), 2) if len(d2s) > 1 else 0,
            "D6_mean": round(statistics.mean(d6s), 2) if d6s else None,
            "D6_std": round(statistics.pstdev(d6s), 2) if len(d6s) > 1 else 0,
            "pass_rate_mean": round(statistics.mean(pass_rates), 4) if pass_rates else None,
            "pass_rate_std": round(statistics.pstdev(pass_rates), 4) if len(pass_rates) > 1 else 0,
        }

    out_path = args.output or os.path.join(EVAL_DIR, "minicpm5_d1d6_results.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"WROTE {out_path}")
    print(json.dumps(summary.get("aggregate", {}), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
