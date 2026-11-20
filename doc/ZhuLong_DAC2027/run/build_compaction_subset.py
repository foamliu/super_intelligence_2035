#!/usr/bin/env python3
"""build_compaction_subset.py — 为压缩机制消融构建 40 题「长轨迹倾向」子集。

口径（plan §11.2 / ZHULONG_TASK §11 step3）：
  从 think_lang 消融历史 trace（30 轮、~4700 session）按
    ① 上下文峰值（content 字符数代理）
    ② tool_calls 数（tool_use block 计数）
    ③ 是否曾触发压缩（messages 中出现 "Context summary:"）
  排序，取 Top-40，按 metadata.category 分层，seed=42 决定平局打破。

两臂同一清单；输出 run/compaction_subset_40.txt（每行一个 task_id）。
"""
import argparse, json, os, random, sys
from collections import defaultdict

TRACE_BASE_DEFAULT = "/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang"
BENCH_DEFAULT = "/nasdata/app.e0031982/code/EDA-Eval-Framework/benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"


def iter_task_messages(trace_root):
    """yield (task_id, messages_json_path) for every archived session."""
    for tag in sorted(os.listdir(trace_root)):
        tag_dir = os.path.join(trace_root, tag)
        if not os.path.isdir(tag_dir):
            continue
        for batch in sorted(os.listdir(tag_dir)):
            trace_dir = os.path.join(tag_dir, batch, "trace")
            if not os.path.isdir(trace_dir):
                continue
            for tid in sorted(os.listdir(trace_dir)):
                tdir = os.path.join(trace_dir, tid)
                if not os.path.isdir(tdir):
                    continue
                # 优先 messages.json，回退 api_conversation_history.json
                mj = os.path.join(tdir, "messages.json")
                if not os.path.exists(mj):
                    mj = os.path.join(tdir, "api_conversation_history.json")
                if os.path.exists(mj):
                    yield tid, mj


def analyze_messages(path):
    """返回 (tool_calls, msg_count, content_len, compacted)。
    compacted = messages 中是否出现 agentic 摘要头 "Context summary:"。"""
    try:
        d = json.load(open(path))
    except Exception:
        return None
    msgs = d if isinstance(d, list) else d.get("messages", [])
    if not isinstance(msgs, list):
        return None
    tool_calls = 0
    content_len = 0
    compacted = False
    for m in msgs:
        if not isinstance(m, dict):
            continue
        c = m.get("content", "")
        if isinstance(c, list):
            for blk in c:
                if not isinstance(blk, dict):
                    continue
                t = blk.get("type", "")
                if t == "tool_use":
                    tool_calls += 1
                txt = blk.get("text", "")
                if isinstance(txt, str):
                    content_len += len(txt)
                    if "Context summary:" in txt:
                        compacted = True
        elif isinstance(c, str):
            content_len += len(c)
            if "Context summary:" in c:
                compacted = True
    return tool_calls, len(msgs), content_len, compacted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default=TRACE_BASE_DEFAULT)
    ap.add_argument("--tasks", default=BENCH_DEFAULT)
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="compaction_subset_40.txt")
    args = ap.parse_args()

    random.seed(args.seed)

    # 1) 聚合每 task 的 max 指标（跨所有轮次）
    agg = defaultdict(lambda: {"max_tools": 0, "max_msgs": 0, "max_len": 0, "compact": False, "n_sessions": 0})
    n_files = 0
    for tid, path in iter_task_messages(args.traces):
        r = analyze_messages(path)
        if r is None:
            continue
        tools, nmsgs, clen, comp = r
        a = agg[tid]
        a["max_tools"] = max(a["max_tools"], tools)
        a["max_msgs"] = max(a["max_msgs"], nmsgs)
        a["max_len"] = max(a["max_len"], clen)
        a["compact"] = a["compact"] or comp
        a["n_sessions"] += 1
        n_files += 1

    # 2) benchmark: task_id -> category
    cat = {}
    all_tasks = []
    for line in open(args.tasks):
        d = json.loads(line)
        tid = d["task_id"]
        c = d.get("metadata", {}).get("category", "Unknown")
        cat[tid] = c
        all_tasks.append(tid)

    # 3) 评分：z-score 归一 max_tools / max_len + 压缩 bonus
    tasks = [t for t in agg.keys() if t in cat]
    if not tasks:
        print("ERROR: no overlapping tasks between traces and benchmark", file=sys.stderr)
        sys.exit(1)
    import statistics
    def zscore(vals):
        mu = statistics.mean(vals) if vals else 0
        sd = statistics.pstdev(vals) if len(vals) > 1 else 1
        return {v: (0.0 if sd == 0 else (v - mu) / sd) for v in vals}
    zt = zscore([agg[t]["max_tools"] for t in tasks])
    zl = zscore([agg[t]["max_len"] for t in tasks])
    # 压缩 bonus: 0.6 sigma
    score = {}
    for t in tasks:
        s = zt[agg[t]["max_tools"]] + 0.5 * zl[agg[t]["max_len"]]
        if agg[t]["compact"]:
            s += 0.6
        score[t] = s

    # 4) 分层 Top-40：按 category 配额 + 按 score 降序填充
    cat_counts = defaultdict(int)
    for t in all_tasks:
        cat_counts[cat[t]] += 1
    total = len(all_tasks)
    # 每类配额 = round(top * cat/total)，至少 2
    quota = {c: max(2, round(args.top * cat_counts[c] / total)) for c in cat_counts}
    # 配额总和可能 != top；先按配额取，再补足/截断
    chosen = []
    chosen_cat = defaultdict(int)
    # 第一遍：按 score 降序，每类填到配额
    order = sorted(tasks, key=lambda t: (-score[t], t))
    for t in order:
        if chosen_cat[cat[t]] < quota[cat[t]]:
            chosen.append(t)
            chosen_cat[cat[t]] += 1
        if len(chosen) >= args.top:
            break
    # 第二遍：若不足 top，从剩余按 score 降序补足（不限配额）
    if len(chosen) < args.top:
        rest = [t for t in order if t not in set(chosen)]
        for t in rest:
            chosen.append(t)
            if len(chosen) >= args.top:
                break
    # 截断到 top
    chosen = chosen[:args.top]
    chosen.sort()

    # 5) 输出
    with open(args.out, "w") as f:
        for t in chosen:
            f.write(t + "\n")

    # 报告
    print(f"scanned sessions: {n_files}; unique tasks: {len(agg)}; chosen: {len(chosen)}")
    cc = defaultdict(int)
    for t in chosen:
        cc[cat[t]] += 1
    print("category distribution (chosen):", dict(cc))
    print("compact-flag count (chosen):",
          sum(1 for t in chosen if agg[t]["compact"]))
    print(f"median max_tools (chosen): {statistics.median([agg[t]['max_tools'] for t in chosen])}")
    print(f"median max_len   (chosen): {statistics.median([agg[t]['max_len'] for t in chosen])}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
