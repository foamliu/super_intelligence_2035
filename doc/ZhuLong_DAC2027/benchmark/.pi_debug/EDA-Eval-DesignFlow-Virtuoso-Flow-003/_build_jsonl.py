#!/usr/bin/env python3
import json, pathlib
base = pathlib.Path("/nasdata/app.e0031982/code/EDA-Flow-Bench")
dbg = base / "agent_workspace/.pi_debug/EDA-Eval-DesignFlow-Virtuoso-Flow-003"
prompt = (dbg / "prompt.txt").read_text()
test = (dbg / "checker.tcl").read_text()

entry = {
    "task_id": "EDA-Eval-DesignFlow-Virtuoso-Flow-003",
    "prompt": prompt,
    "entry_point": "vflow_runlog_audit",
    "test": test,
    "metadata": {
        "task_name": "virtuoso_flow_runlog_audit",
        "direction": "virtuoso",
        "scenario": "cadence-virtuoso-batch-skill-flow-orchestrator-runlog-audit",
        "layer": "L2",
        "topic": "flow-runlog-audit",
        "difficulty": "medium",
        "design": "DERIVED (per 2026-10-29 ephemeral-session strategy: cline sessions near-totally cleared, fresh mining dead) from known real Cadence Virtuoso batch-SKILL flow-orchestration patterns (layout_virtuoso 2496 scan hits, second-largest raw class). Virtuoso-Flow-001 distilled CONFIG CONSOLIDATION (merge two tool configs); Virtuoso-Flow-002 distilled STATIC config-DAG validation. This case distills a THIRD real recurring task the same designers face AFTER a run: parse the orchestrator RUN LOG into a structured audit -- per-step final status (LAST-WINS within a block), attempt/retry block counting (attempts = start-line count, NOT retry-line count), skip-reason coverage (ALL reasons incl. upstream-failed AND user), final-block-only duration (midnight-aware), true wall clock (flow_end - flow_start, NOT sum of per-step durations; setup gap + discarded retry time excluded), and overall verdict with priority ERROR > SKIPPED > PASS. 7 real traps: (1) retry attempts counted as retry-lines instead of start/block count; (2) LAST-WINS terminal within a block (PASS then ERROR -> ERROR); (3) skipped_steps must include ALL skip reasons not only upstream-failed; (4) total_wall = wall clock not sum of durations; (5) MIDNIGHT rollover +86400; (6) verdict priority ERROR over SKIP; (7) steps_seen de-duplicated in first-appearance order. DISTINCT from Virtuoso-Flow-001/002 (config merge / static DAG validate): dynamic run-log audit. layout_virtuoso 2496 scan hits (expansion, class was 2 cases, weakest non-blocked class).",
        "tcr_refs": [
            "flow line: '[flow] start 03:00:00'",
            "step start: '[step:rscalc] start 03:00:10'",
            "terminal: '[step:autovia] ERROR via-insertion-failed 03:00:25'",
            "skip: '[step:pe] SKIP reason=upstream-failed:rscalc 03:00:06'",
            "retry marker: '[step:autovia] retry'"
        ],
        "heavy": False,
        "wall_time_sec": 600
    },
    "mode": "design_flow",
    "runtime": {"lang": "tcl", "host": "waveview"},
    "attachments": [],
    "budget": {"max_turns": 40, "wall_time_sec": 600}
}
out = base / "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Virtuoso-Flow.jsonl"
with open(out, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", out)
# verify
for l in open(out):
    if l.strip():
        d=json.loads(l); print(" ", d["task_id"])
