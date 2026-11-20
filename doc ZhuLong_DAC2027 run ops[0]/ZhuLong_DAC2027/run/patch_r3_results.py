#!/usr/bin/env python3
"""patch_r3_results.py — Fix C_agentic_r3 in ablation_compaction_results.json:
  - correct pass_rate_pct from 15.2 (158-denom) to 60.0 (40-subset)
  - populate per-task pass field (currently all None) from final_report.json details_per_task
  - set pass_denominator='subset_40'
"""
import json, os
RUN = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
RESULTS = os.path.join(RUN, "ablation_compaction_results.json")
EVAL_DIR = "/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/20261113_1226_app.e0031982"

subset = [l.strip() for l in open(os.path.join(RUN, "compaction_subset_40.txt")) if l.strip()]
fr = json.load(open(os.path.join(EVAL_DIR, "final_report.json")))
details = fr.get("details_per_task", {})
task_pass = {t: int(details.get(t, {}).get("num_correct", 0)) for t in subset}
n_pass = sum(task_pass.values())

results = json.load(open(RESULTS))
for r in results.get("rounds", []):
    s = r.get("summary", {})
    if s.get("tag") == "C_agentic_r3":
        s["pass_rate_pct"] = round(n_pass / 40 * 100, 1)
        s["passed"] = n_pass
        s["total"] = 40
        s["pass_denominator"] = "subset_40"
        s["eval_note"] = "re-scored from final_report.json details_per_task num_correct (orchestrator used 158-denom)"
        print(f"patched summary: pass_rate_pct={s['pass_rate_pct']} passed={n_pass}/40")
        # patch tasks
        for t in r.get("tasks", []):
            tid = t.get("task")
            t["pass"] = task_pass.get(tid, 0)
        n_patched = sum(1 for t in r["tasks"] if t.get("pass") is not None)
        print(f"patched {n_patched}/40 tasks with pass field")
        break

with open(RESULTS, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"-> {RESULTS}")
