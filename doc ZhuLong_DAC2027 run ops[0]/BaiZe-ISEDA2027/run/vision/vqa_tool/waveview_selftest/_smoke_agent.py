#!/usr/bin/env python3
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_agent_run as A
import waveview_selftest_cases as C
tag = sys.argv[1] if len(sys.argv) > 1 else "β9"
arm = sys.argv[2] if len(sys.argv) > 2 else "G1"
server = {"G0": None, "G1": A.BASE_SERVER, "G2": A.ADAPTER_SERVER}[arm]
cases = C.get_cases()
for c in cases:
    c["_png"] = c["gen"]()
c = [c for c in cases if c["tag"] == tag][0]
r = A.run_agent_case(arm, server, c)
print("VERDICT", r["verdict"], "k", r["k_pass"], "/", r["k_total"],
      "vqa", r["vqa_calls_per_task"], "reask", r["reask_count"],
      "selfcheck", len(r["agent_selfcheck"]), "turns", r["n_turns"], "dur", r["duration_s"])
print("ANSWER", json.dumps(r["answer"], ensure_ascii=False))
sc = r["agent_selfcheck"] or ["(none)"]
print("SELFCHECK0:", sc[0][:500])
