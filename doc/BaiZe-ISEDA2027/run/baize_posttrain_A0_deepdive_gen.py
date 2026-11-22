#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A0 capability deep-dive report generator (三条令 §三 核心交付).
Computes ALL numbers itself from落盘 JSON (不抄代拟稿). Zero script/外链 in output HTML.
"""
import json, os, statistics, collections, html

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
REP_DIR = os.path.join(RUN_DIR, "reports")
os.makedirs(REP_DIR, exist_ok=True)
OUT = os.path.join(REP_DIR, "report_posttrain_A0_capability_deepdive_zh.html")

def L(name):
    p = os.path.join(RUN_DIR, name)
    return json.load(open(p)) if os.path.exists(p) else None

a0_runs = [L("baseline_A0_base_run%d_pertask.json" % i) for i in range(1, 6)]
a0_runs = [r for r in a0_runs if r]
a0_5run = L("baseline_A0_base_5run_summary.json")
a1_5run = L("baseline_A1_sft_5run_summary.json")
paired = L("baseline_A0_vs_A1_paired_compare.json")
r83 = L("r83_difficulty_analysis.json")

task_ids = list(a0_runs[0]["per_task"].keys())
per_task = {}
TOOL_KEYS = ["search_apis", "get_api_details", "search_apis_by_keyword", "run_code",
             "run_commands", "read_files", "editor", "submit_and_exit"]
for tid in task_ids:
    pc = []; fm = []; et = []; tc = []; it = []; ot = []
    sc = []; rc = []; ec = []; rmc = []; al = []; rq = []; breadth = []
    for r in a0_runs:
        t = r["per_task"].get(tid)
        if not t:
            continue
        pc.append(t.get("pass_count", 0))
        if t.get("outcome") == "fail":
            fm.append(t.get("fail_mode"))
        et.extend(t.get("error_types") or [])
        tc.append(t.get("tool_call_count", 0))
        it.append(t.get("input_tokens", 0))
        ot.append(t.get("output_tokens", 0))
        sc.append(t.get("search_calls", 0))
        rc.append(t.get("run_code_calls", 0))
        ec.append(t.get("editor_calls", 0))
        rmc.append(t.get("run_commands_calls", 0))
        al.append(1 if t.get("agent_loop_entry") else 0)
        rq.append(1 if t.get("rag_queried") else 0)
        tcalls = t.get("tool_calls") or {}
        breadth.append(sum(1 for k in TOOL_KEYS if tcalls.get(k, 0) > 0))
    per_task[tid] = dict(
        pass_counts=pc, sum_pass=sum(pc),
        dom_fm=(collections.Counter(fm).most_common(1)[0][0] if fm else "none"),
        error_types=et,
        m_tc=statistics.mean(tc) if tc else 0,
        m_it=statistics.mean(it) if it else 0,
        m_ot=statistics.mean(ot) if ot else 0,
        m_sc=statistics.mean(sc) if sc else 0,
        m_rc=statistics.mean(rc) if rc else 0,
        m_ec=statistics.mean(ec) if ec else 0,
        m_rmc=statistics.mean(rmc) if rmc else 0,
        al_rate=statistics.mean(al) if al else 0,
        rq_rate=statistics.mean(rq) if rq else 0,
        m_breadth=statistics.mean(breadth) if breadth else 0,
    )

# categories
cats = {"pass_all": 0, "fail_all": 0, "partial": 0}
for tid, d in per_task.items():
    s = d["sum_pass"]; n = len(d["pass_counts"])
    if s >= n: cats["pass_all"] += 1
    elif s == 0: cats["fail_all"] += 1
    else: cats["partial"] += 1

# dominant fail_mode over failing tasks (by dom_fm)
fm_dist = collections.Counter(d["dom_fm"] for d in per_task.values() if d["dom_fm"] != "none")
# error_types dist (aggregate over all task-runs)
et_dist = collections.Counter()
for d in per_task.values():
    for e in d["error_types"]:
        et_dist[e] += 1

# PASS group (sum_pass>=3 majority) vs FAIL group (<3)
def grp(pred):
    ds = [d for d in per_task.values() if pred(d)]
    if not ds: return None
    return dict(
        n=len(ds),
        m_tc=statistics.mean(d["m_tc"] for d in ds),
        m_it=statistics.mean(d["m_it"] for d in ds),
        m_ot=statistics.mean(d["m_ot"] for d in ds),
        m_sc=statistics.mean(d["m_sc"] for d in ds),
        m_rc=statistics.mean(d["m_rc"] for d in ds),
        m_ec=statistics.mean(d["m_ec"] for d in ds),
        m_rmc=statistics.mean(d["m_rmc"] for d in ds),
        al_rate=statistics.mean(d["al_rate"] for d in ds),
        rq_rate=statistics.mean(d["rq_rate"] for d in ds),
        m_breadth=statistics.mean(d["m_breadth"] for d in ds),
    )
pass_g = grp(lambda d: d["sum_pass"] >= 3)
fail_g = grp(lambda d: d["sum_pass"] < 3)

# tool breadth dist
breadth_dist = collections.Counter(int(round(d["m_breadth"])) for d in per_task.values())

# aggregate tool calls run1 (口径 evidence)
agg_tc = a0_runs[0].get("aggregate_tool_calls", {})
fm_legend = a0_runs[0].get("fail_mode_legend", {})

# 4run interim for cross-run stability
a0_4run = L("baseline_A0_base_4run_interim_summary.json")

print("cats", cats)
print("fm_dist", dict(fm_dist))
print("et_dist", dict(et_dist.most_common(12)))
print("pass_g", pass_g)
print("fail_g", fail_g)
print("breadth_dist", dict(breadth_dist))
print("agg_tc", agg_tc)

# stash for html stage
import pickle
pickle.dump(dict(per_task=per_task, cats=cats, fm_dist=fm_dist, et_dist=et_dist,
                 pass_g=pass_g, fail_g=fail_g, breadth_dist=breadth_dist,
                 agg_tc=agg_tc, fm_legend=fm_legend, a0_5run=a0_5run, a1_5run=a1_5run,
                 paired=paired, r83=r83, a0_4run=a0_4run),
            open("/tmp/a0_deepdive.pkl", "wb"))
print("STAGE1_OK")
