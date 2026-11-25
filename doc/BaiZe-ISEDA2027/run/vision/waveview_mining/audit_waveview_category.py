#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the 192 eval_included WaveView cases: classify by (a) genuine waveform
relevance and (b) what check.py validates (image-reading vs code-gen vs other).

Goal: separate cases where a VQA tool (reading a waveform image) can plausibly
raise the pass rate (V0 < V1/V2) from cases where it cannot.
"""
import json, re, os
from collections import Counter

SRC = "/tmp/EDA-Eval-DesignFlow.jsonl"
WV = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/EDA-Eval-DesignFlow-WaveView.jsonl"

# load source records by task_id
src = {}
for l in open(SRC, encoding="utf-8", errors="replace"):
    d = json.loads(l)
    src[d["task_id"]] = d

# load waveview subset eval_included
wv = []
for l in open(WV, encoding="utf-8", errors="replace"):
    d = json.loads(l)
    if d.get("eval_included"):
        wv.append(d)

print("eval_included", len(wv))

# Classification heuristics
IMG_READ_SIGNALS = [
    "vmax", "vmin", "peak_to_peak", "peak-to-peak", "period_ns", "duty",
    "n_transitions", "vth_high", "vth_low", "hysteresis", "t_cross_up",
    "t_cross_down", "eye_height", "aperture", "skew", "vref", "margin_ns",
    "rise_edge", "fall_edge", "amplitude", "frequency", "rise_time",
    "fall_time", "overshoot", "undershoot", "settling", "jitter",
    "t_at_max", "t_at_min", "ramp_slope", "swing", "n_levels", "n_pulses",
]

CODE_SIGNALS = [
    "submit.zip", ".v", ".sv", "verilog", "systemverilog", "rtl", "testbench",
    "makefile", "make run", "python script", "analyze_code", "def check",
    "spice netlist", ".sp", "rtl template", "module(", "always @", "assign ",
    "run_sim", "vcs ", "iverilog",
]

# keyword false-positive detectors: tasks clearly unrelated to waveforms
NONWAVE_TOPICS = [
    "analyze your own code structure", "code structure", "software install",
    "安装指南", "analyze_code.py", "mcp_settings", "system_config",
]


def classify(rec, wrec):
    tid = rec["task_id"]
    prompt = (rec.get("prompt") or "")
    test = (rec.get("test") or "")
    blob = (prompt + "\n" + test).lower()
    kw = wrec.get("kw_match", "")
    # 1. false-positive: non-waveform topic dominates
    has_img = bool(wrec.get("image_path"))
    # image-reading: check.py validates numeric readings likely from a graph
    img_hits = sum(1 for s in IMG_READ_SIGNALS if s in blob)
    code_hits = sum(1 for s in CODE_SIGNALS if s in blob)
    # Does check.py embed A_PARAMS / signal reconstruction (image oracle)?
    has_oracle = any(k in test for k in ["A_PARAMS", "reconstruct", "recompute",
                                          "regenerate", "matplotlib", "plt.",
                                          "savefig", ".png"])
    # Does check.py expect a JSON/CSV of readings (image-reading deliverable)?
    expects_readings = bool(re.search(r"(signals|readings|measurements|report)\.json|"
                                       r"\.csv|vmax|vmin|peak_to_peak|aperture_ps|"
                                       r"vref_mV|eye_height", test))
    # code deliverable: expects .v/.sv/.py/zip with code
    expects_code = bool(re.search(r"submit\.zip|\.v\b|\.sv\b|\.py\b|Makefile|module\s*\(",
                                   test + " " + (rec.get("entry_point") or "")))

    if has_img:
        cat = "image_reading"
    elif img_hits >= 3 and expects_readings and not expects_code:
        cat = "text_image_reading_candidate"  # could generate image
    elif expects_code and code_hits >= 2:
        cat = "code_gen"
    elif img_hits >= 2:
        cat = "waveform_signal_text"
    else:
        cat = "weak_or_falsepos"
    return {
        "task_id": tid,
        "shard": wrec.get("shard"),
        "kw_match": kw,
        "has_image": has_img,
        "k_conditions": wrec.get("k_conditions"),
        "img_hits": img_hits,
        "code_hits": code_hits,
        "has_oracle": has_oracle,
        "expects_readings": expects_readings,
        "expects_code": expects_code,
        "category": cat,
        "prompt_head": prompt[:160].replace("\n", " "),
        "test_head": test[:160].replace("\n", " "),
    }


rows = [classify(src[r["task_id"]], r) for r in wv if r["task_id"] in src]
cats = Counter(r["category"] for r in rows)
print("categories", dict(cats))
for cat in cats:
    print("\n==== %s (n=%d) ====" % (cat, cats[cat]))
    for r in rows:
        if r["category"] == cat:
            print("  %s | kw=%s k=%s img=%s oracle=%s read=%s code=%s | %s"
                  % (r["task_id"][:48], r["kw_match"], r["k_conditions"],
                     r["has_image"], r["has_oracle"], r["expects_readings"],
                     r["expects_code"], r["prompt_head"][:90]))

json.dump(rows, open("/tmp/waveview_audit.json", "w"), ensure_ascii=False, indent=1)
print("\nSaved /tmp/waveview_audit.json")
