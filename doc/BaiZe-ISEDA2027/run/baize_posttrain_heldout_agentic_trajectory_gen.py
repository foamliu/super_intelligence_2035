#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_heldout_agentic_trajectory_gen.py
Held-out (contamination-isolated) REAL agentic trajectory harvester -- secK.

CHAIN CONTEXT (secF -> secG -> secH -> secI -> secJ -> secK):
  secF root cause: A1 SFT corpus = v2 static single-turn doc->code (19524 pairs,
    0% agentic trajectories) -> covered the base healthy loop -> catastrophic
    degradation A0 43.29% -> A1 4.56% (McNemar chi2=68.01 p=0.0).
  secG: harvested 25 pass_all agentic trajectories from A0 158-eval traces as a
    BEHAVIOR TEMPLATE only (red line sec5.1: those traces contain eval
    prompt/signature/assertion -> cannot be SFT training data).
  secH: contamination-isolation audit -> 3930 available_for_sft_apis (97.71%).
  secI/secJ: TIERED doc->code corpus = 2842 pairs (held-out, form-aligned to the
    secG3 healthy template), but these are SKELETONS, not real trajectories.
  secK (THIS): the missing link -- run base+cline on the held-out task prompts
    (the 2842 TIERED prompts, which are themselves non-eval held-out tasks) to
    harvest REAL pass agentic trajectories, then MIX with the TIERED doc->code
    pairs so the formal SFT corpus has agentic share >= 30% (fixes secF 0%-agentic
    root cause). Frozen pre-registration in heldout_agentic_trajectory_prereg.json.

ZERO GPU / WRITE-ONLY STATUS:
  Structurally-complete SKELETON. The runner that drives base+cline + the EDA
  sandbox is a documented stub (raise NotImplementedError) because executing it
  needs (a) a served base/pretrain ckpt on GPU4 :8098, (b) the dual-nix-tunnel
  sandbox, (c) serial discipline vs zhulong (pgrep run_cline + ss port check),
  (d) operator/user authorization. It compiles clean; the NON-runner parts
  (task-pool loader, contamination re-check gate, behavior gate, mixer, manifest
  writer) are runnable on CPU for dry-run/validation. Does NOT touch
  protocol/task/check.py/timeout/-p and uses zero GPU.

RED LINE sec5.1: only held-out (non-eval) APIs are used; the 158 eval tasks'
prompt/signature/assertion never enter training. secH4 signature gate retained.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TIERED_CORPUS = os.path.join(HERE, "heldout_sft_corpus_tiered.jsonl")
AUDIT = os.path.join(HERE, "sft_contamination_isolation_audit.json")
PREREG_DECISION = os.path.join(HERE, "sft_isolation_prereg_decision.json")
PREREG = os.path.join(HERE, "heldout_agentic_trajectory_prereg.json")

# secF5.3 / secG3 behavior gate thresholds (vs A0 base run1 aggregate).
BEHAVIOR_GATE = {
    "search_apis_min": 1,
    "submit_and_exit_max": 3,
    "agent_loop_entry_required": True,
    "must_end_with_submit": True,
    "search_before_code": True,
}
AGENTIC_SHARE_MIN = 0.30  # secJ5.5 / secI6 pre-registered

_DEF_RE = re.compile(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)")


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def load_forbidden_sets(audit):
    """Return (forbidden_api_set, forbidden_signatures) from secH audit."""
    fa = set()
    freq = audit.get("forbidden_api_frequency") if audit else None
    if isinstance(freq, dict):
        fa = set(freq.keys())
    elif isinstance(freq, list):
        for item in freq:
            if isinstance(item, dict) and "api" in item:
                fa.add(item["api"])
            elif isinstance(item, str):
                fa.add(item)
    sigs = set()
    for t in (audit.get("per_task") if audit else None) or []:
        s = t.get("signatures") or []
        if isinstance(s, list):
            for item in s:
                if isinstance(item, dict) and "def" in item:
                    name = item["def"]
                    args = item.get("args", "")
                    sigs.add("def " + str(name) + "(" + str(args) + ")")
                elif isinstance(item, str):
                    sigs.add(item)
    return fa, sigs


def contamination_gate(traj, forbidden_apis, forbidden_signatures, excluded_helpers):
    """secH4 re-check on a harvested REAL trajectory's code surface.

    Returns (passed, reasons). Target API must be held-out; excluded HIGH-risk
    helpers (dbNewCV/dbCreateLib) must not appear in code; no eval entry-point
    signature may leak.
    """
    reasons = []
    code = traj.get("submitted_code", "") or ""
    if not traj.get("available_for_sft", True):
        reasons.append("target_api_not_heldout")
    for h in excluded_helpers or []:
        if re.search(r"\b" + re.escape(h) + r"\s*\(", code):
            reasons.append("excluded_helper_in_code:" + h)
    for sig in forbidden_signatures or []:
        m = _DEF_RE.search(sig)
        if m and re.search(r"\bdef\s+" + re.escape(m.group(1)) + r"\s*\(", code):
            reasons.append("signature_leak:" + m.group(1))
    return (len(reasons) == 0), reasons


def behavior_gate(traj, thresholds=BEHAVIOR_GATE):
    """secG3 healthy-template behavior gate on a harvested trajectory.

    metrics keys: search_apis, submit_and_exit, agent_loop_entry (bool),
    first_non_runcommand_tool, last_tool.
    """
    m = traj.get("behavior_metrics", {}) or {}
    reasons = []
    if m.get("search_apis", 0) < thresholds["search_apis_min"]:
        reasons.append("search_apis_below_min")
    if m.get("submit_and_exit", 0) > thresholds["submit_and_exit_max"]:
        reasons.append("submit_storm")
    if thresholds["agent_loop_entry_required"] and not m.get("agent_loop_entry", False):
        reasons.append("no_agent_loop_entry")
    if thresholds["must_end_with_submit"] and m.get("last_tool") != "submit_and_exit":
        reasons.append("not_ended_with_submit")
    if thresholds["search_before_code"]:
        first = m.get("first_non_runcommand_tool", "")
        if first not in ("search_apis", "get_api_details", "search_apis_by_keyword"):
            reasons.append("no_search_before_code")
    return (len(reasons) == 0), reasons


def load_task_pool(limit=None, categories=None):
    """Load held-out task prompts from the TIERED corpus (secJ8).

    Each TIERED pair already carries an `instruction` (a non-eval held-out task
    prompt) + `doctest_code` (reference example used as the pass-oracle). We do
    NOT synthesize new tasks/check.py (that is designflow's job); we reuse the
    held-out prompts that secI/secJ already produced.
    """
    pool = load_jsonl(TIERED_CORPUS)
    if categories:
        want = set(categories)
        pool = [p for p in pool if p.get("category") in want]
    if limit:
        pool = pool[:limit]
    return pool


def pass_oracle(traj, task):
    """A held-out task 'passes' if the trajectory submitted executable code whose
    behavior matches the reference doctest. Actual execution happens in the EDA
    sandbox (run_code) during the RUN; here we only return the runner-recorded
    verdict. This stub returns the runner-recorded verdict.
    """
    return bool(traj.get("pass_verdict", False))


def run_trajectory(task, endpoint, model, timeout_s=2500):
    """Drive base+cline on one held-out task prompt to harvest a REAL agentic
    trajectory. A0 口径: search_apis/get_api_details/run_code/editor/
    submit_and_exit, PreToolUse anti-cheat hook, single trace, 2500s, Pass@1.

    BLOCKED pre-requisites (do NOT run until all green):
      1. base/pretrain ckpt served OpenAI-compatible on `endpoint` (GPU4 :8098
         standby OK for base预演; pretrain ckpt ETA approx 2026-12-25);
      2. dual-nix-tunnel sandbox up (ssh -p 3333 ... -> 36.15, run_code e2e);
      3. SERIAL discipline vs zhulong: `pgrep -f run_cline_script` empty AND
         `ss -tlnp | grep -E ':(30|80)'` clear before start;
      4. operator/user authorization (this burns GPU + sandbox time).

    Returns dict: {api, task_id, session_id, trace_path, submitted_code,
    behavior_metrics, pass_verdict, generation_status, execution_status}.
    """
    raise NotImplementedError(
        "Runner needs served ckpt + sandbox + serial clearance + authorization. "
        "See secK pre-registration. This skeleton is write-only / zero-GPU.")


def mix_corpus(tiered_pairs, agentic_trajectories, agentic_share_min=AGENTIC_SHARE_MIN):
    """Formal SFT corpus = TIERED doc->code pairs + real agentic trajectories.

    Pre-registered (secJ5.5): real agentic share must be >= 30% to fix secF
    0%-agentic root cause. Returns (mixed, share, ok).
    """
    n_doc = len(tiered_pairs)
    n_ag = len(agentic_trajectories)
    total = n_doc + n_ag
    share = (n_ag / total) if total else 0.0
    mixed = []
    for p in tiered_pairs:
        mixed.append({"source": "tiered_doc_to_code", "pair": p})
    for t in agentic_trajectories:
        mixed.append({"source": "real_agentic_trajectory", "pair": t})
    ok = share >= agentic_share_min
    return mixed, share, ok


def dry_run_validate():
    """Validate the non-runner pipeline (gates + mixer) on a tiny synthetic
    fixture. Zero GPU, zero sandbox. Confirms the skeleton is wired correctly so
    that when the runner is authorized the harvest is one command.
    """
    audit = load_json(AUDIT, default={})
    fa, fs = load_forbidden_sets(audit)
    prereg = load_json(PREREG_DECISION, default={})
    excluded = prereg.get("rule", {}).get("excluded_helpers", ["dbNewCV", "dbCreateLib"])

    good = {
        "api": "CallingCounter", "available_for_sft": True,
        "submitted_code": "pyScript.CallingCounter(func)\nc = cnt.count()",
        "behavior_metrics": {"search_apis": 2, "submit_and_exit": 1,
                             "agent_loop_entry": True, "last_tool": "submit_and_exit",
                             "first_non_runcommand_tool": "search_apis"},
        "pass_verdict": True,
    }
    bad = {
        "api": "CallingCounter", "available_for_sft": True,
        "submitted_code": "dbNewCV(1,2,3)",
        "behavior_metrics": {"search_apis": 0, "submit_and_exit": 9,
                             "agent_loop_entry": True, "last_tool": "submit_and_exit",
                             "first_non_runcommand_tool": "editor"},
        "pass_verdict": False,
    }
    g_pass, g_reasons = contamination_gate(good, fa, fs, excluded)
    b_pass, b_reasons = contamination_gate(bad, fa, fs, excluded)
    bg_pass, bg_reasons = behavior_gate(good)
    bb_pass, bb_reasons = behavior_gate(bad)
    tiered = load_jsonl(TIERED_CORPUS)[:10]
    mixed, share, share_ok = mix_corpus(tiered, [good], AGENTIC_SHARE_MIN)
    return {
        "contamination_gate_good": {"pass": g_pass, "reasons": g_reasons},
        "contamination_gate_bad": {"pass": b_pass, "reasons": b_reasons},
        "behavior_gate_good": {"pass": bg_pass, "reasons": bg_reasons},
        "behavior_gate_bad": {"pass": bb_pass, "reasons": bb_reasons},
        "mix": {"n_tiered": len(tiered), "n_agentic": 1, "share": round(share, 4),
                "share_ok": share_ok, "agentic_share_min": AGENTIC_SHARE_MIN},
        "task_pool_available": os.path.exists(TIERED_CORPUS),
    }


def main():
    ap = argparse.ArgumentParser(
        description="secK held-out agentic trajectory harvester (skeleton)")
    ap.add_argument("--dry-run-validate", action="store_true",
                    help="CPU-only validation of gates + mixer (zero GPU)")
    ap.add_argument("--task-pool-size", action="store_true",
                    help="Print the held-out task pool size (TIERED corpus reuse)")
    args = ap.parse_args()

    if args.dry_run_validate:
        res = dry_run_validate()
        print(json.dumps(res, ensure_ascii=False, indent=2))
        assert res["contamination_gate_good"]["pass"] is True
        assert res["contamination_gate_bad"]["pass"] is False
        assert res["behavior_gate_good"]["pass"] is True
        assert res["behavior_gate_bad"]["pass"] is False
        print("secK dry-run validate: ALL GATES WIRED OK "
              "(skeleton is write-only, runner stub intentional)")
        return 0

    if args.task_pool_size:
        pool = load_task_pool()
        print("held-out task pool size (TIERED reuse, no new造题):", len(pool))
        return 0

    print("secK skeleton. Use --dry-run-validate or --task-pool-size. "
          "Runner is a documented stub (needs ckpt+sandbox+authorization).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

