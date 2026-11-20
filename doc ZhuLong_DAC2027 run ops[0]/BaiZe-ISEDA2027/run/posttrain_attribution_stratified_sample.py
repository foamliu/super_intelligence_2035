#!/usr/bin/env python3
# posttrain_attribution_stratified_sample.py — Task A 40 题分层抽样 (POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §2)
#
# 规格: 40 题, 按「旧 .17 5-run 是否至少通过 1 次 × 失败类型」分层抽样, 种子固定.
# 输入: /tmp/posttrain_5run_eval/step105/run{1..5}/final_report.json (旧 .17 step105 5-run baseline=3.04%)
# 输出: attribution_stratified_40.json (40 题 task_id + 分层标注 + 可复算证据) + 打印逗号分隔 ID 串 (供 bpt_attribution_ablation.sh --tasks)
#
# 纪律: 不挑题面/不删失败样本; 抽样只决定 ablation 子集, 不改 benchmark. 种子固定 -> 可复现.
import json, os, sys, random, collections

BASE = "/tmp/posttrain_5run_eval/step105"
RUNS = ["run1", "run2", "run3", "run4", "run5"]
SEED = 20261114
N_SAMPLE = 40

def load_run(r):
    fr = os.path.join(BASE, r, "final_report.json")
    if not os.path.isfile(fr):
        return None
    d = json.load(open(fr))
    return d.get("details_per_task", {})

def main():
    runs = {}
    for r in RUNS:
        dps = load_run(r)
        if dps is None:
            print(f"[WARN] {r} 无 final_report, 跳过", file=sys.stderr)
            continue
        runs[r] = dps
    if not runs:
        print("[FATAL] 无可用 run", file=sys.stderr); sys.exit(1)
    # 全集 task_id (取首个 run 的 keys)
    all_tasks = list(next(iter(runs.values())).keys())
    # 每题: passed_at_least_once + 失败类型聚合
    per_task = {}
    for tid in all_tasks:
        passed_any = False
        fail_types = collections.Counter()
        gen_statuses = collections.Counter()
        exec_statuses = collections.Counter()
        for r, dps in runs.items():
            t = dps.get(tid, {})
            if t.get("num_correct", 0) > 0:
                passed_any = True
            for e in t.get("error_types", []):
                fail_types[e] += 1
            for g in t.get("generation_statuses", []):
                gen_statuses[g] += 1
            for x in t.get("execution_statuses", []):
                exec_statuses[x] += 1
        # 主导失败类型 (num_correct>0 的 run 不计失败)
        dom_fail = fail_types.most_common(1)[0][0] if fail_types else "none"
        dom_gen = gen_statuses.most_common(1)[0][0] if gen_statuses else "none"
        per_task[tid] = {
            "passed_any": passed_any,
            "pass_count": sum(1 for r in runs if runs[r].get(tid, {}).get("num_correct", 0) > 0),
            "dom_fail_type": dom_fail,
            "dom_gen_status": dom_gen,
            "fail_types": dict(fail_types),
            "gen_statuses": dict(gen_statuses),
            "exec_statuses": dict(exec_statuses),
        }
    # 分层: (passed_any, dom_gen_status) — gen_status 比 error_types 更稳定 (success/timeout/fail)
    strata = collections.defaultdict(list)
    for tid, info in per_task.items():
        strata[(info["passed_any"], info["dom_gen_status"])].append(tid)
    # 抽样: 按各层占比分配 40 题 (proportional), 层内 random.seed(SEED) 抽
    total = len(all_tasks)
    random.seed(SEED)
    sampled = []
    alloc = []
    for key, ids in sorted(strata.items(), key=lambda kv: (str(kv[0]), kv[1])):
        n_alloc = max(1, round(N_SAMPLE * len(ids) / total)) if ids else 0
        n_alloc = min(n_alloc, len(ids))
        chosen = random.sample(ids, n_alloc)
        sampled.extend(chosen)
        alloc.append({"stratum": {"passed_any": key[0], "dom_gen_status": key[1]},
                      "pool": len(ids), "allocated": n_alloc, "chosen": chosen})
    # 若 round 不足/超出 40, 微调
    if len(sampled) > N_SAMPLE:
        random.seed(SEED + 1)
        sampled = random.sample(sampled, N_SAMPLE)
        # rebuild alloc chosen accordingly
        chosen_set = set(sampled)
        for a in alloc:
            a["chosen"] = [c for c in a["chosen"] if c in chosen_set]
            a["allocated"] = len(a["chosen"])
    elif len(sampled) < N_SAMPLE:
        # 从剩余池补
        remain = [tid for tid in all_tasks if tid not in set(sampled)]
        random.seed(SEED + 2)
        need = N_SAMPLE - len(sampled)
        extra = random.sample(remain, need) if len(remain) >= need else remain
        sampled.extend(extra)
    # 排序保持题号顺序
    sampled = sorted(set(sampled))[:N_SAMPLE]
    # 简化 id (去掉前缀) 供 --tasks
    short_ids = [t.replace("EDA-Eval-PyAether-", "") for t in sampled]
    out = {
        "spec": "POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §2 Task A 40-question stratified sample",
        "seed": SEED,
        "source": {"baseline": "step105 (.17 5-run, mean 0.0304+/-0.0083)",
                   "runs_used": list(runs.keys()),
                   "path": BASE},
        "total_tasks": total,
        "n_sample": len(sampled),
        "strata_pool": [{"passed_any": k[0], "dom_gen_status": k[1], "pool": len(v)} for k, v in sorted(strata.items())],
        "allocation": alloc,
        "sampled_task_ids": sampled,
        "short_ids_csv": ",".join(short_ids),
        "per_task": {t: per_task[t] for t in sampled},
    }
    out_path = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/attribution_stratified_40.json"
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=2)
    print(f"[OK] {len(sampled)} 题抽样完成 -> {out_path}")
    print(f"  passed_any=True: {sum(1 for t in sampled if per_task[t]['passed_any'])}")
    print(f"  生成状态分布: {dict(collections.Counter(per_task[t]['dom_gen_status'] for t in sampled))}")
    print(f"  失败类型分布: {dict(collections.Counter(per_task[t]['dom_fail_type'] for t in sampled))}")
    print()
    print("--tasks 参数 (逗号分隔, 供 bpt_attribution_ablation.sh):")
    print(out["short_ids_csv"])

if __name__ == "__main__":
    main()
