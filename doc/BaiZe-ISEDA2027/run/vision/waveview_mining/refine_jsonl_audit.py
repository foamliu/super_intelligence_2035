#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refine EDA-Eval-DesignFlow-WaveView.jsonl: add audit_category + vqa_mechanism
based on what each case's check.py actually grades.

audit_category:
  image_reading  : deliverable = measurements read from a waveform PNG (VQA-receptive)
  code_gen       : deliverable = code/script; check.py validates code (VQA-as-MCP-tool
                   mechanism: agent MAY call Qwen3.5-2B VQA to ask waveform details;
                   whether it helps is empirical -- let V0 vs V1/V2 speak)
  no_check       : no check.py -> cannot be graded -> excluded
  excluded_nonwaveform : image-bearing but not a waveform task (IRReportPdf)

vqa_mechanism: short honest note on how VQA can/cannot affect this case.

Keeps all 192 eval_included in the cohort (does NOT pre-judge exclusion of code_gen).
"""
import json, re, os

WV = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/EDA-Eval-DesignFlow-WaveView.jsonl"
AUDIT = "/tmp/waveview_audit.json"
SRC = "/tmp/EDA-Eval-DesignFlow.jsonl"

audit = {r["task_id"]: r for r in json.load(open(AUDIT))}
src = {}
for l in open(SRC, encoding="utf-8", errors="replace"):
    d = json.loads(l); src[d["task_id"]] = d

IMG_READ_SIGNALS = ["vmax","vmin","peak_to_peak","peak-to-peak","period_ns","duty",
    "n_transitions","vth_high","vth_low","hysteresis","t_cross_up","t_cross_down",
    "eye_height","aperture","skew","vref","margin_ns","rise_edge","fall_edge",
    "amplitude","frequency","rise_time","fall_time","overshoot","jitter",
    "t_at_max","t_at_min","ramp_slope","swing","n_levels","n_pulses"]

out = []
for l in open(WV, encoding="utf-8", errors="replace"):
    d = json.loads(l)
    tid = d["task_id"]
    if not d.get("eval_included"):
        # excluded
        if d.get("source") == "no_check":
            d["audit_category"] = "no_check"
            d["vqa_mechanism"] = "no check.py -> cannot grade whole-case pass; excluded from V0/V1/V2."
        else:
            d["audit_category"] = "excluded_nonwaveform"
            d["vqa_mechanism"] = "image-bearing but not a waveform task; honestly excluded."
        out.append(d); continue
    a = audit.get(tid)
    rec = src.get(tid, {})
    test = (rec.get("test") or "")
    prompt = (rec.get("prompt") or "")
    blob = (prompt + "\n" + test).lower()
    if d.get("vqa_runnable") or d.get("image_path"):
        d["audit_category"] = "image_reading"
        d["vqa_mechanism"] = ("Deliverable = measurements read from a real waveform PNG. "
            "V0=text-only(no image); V1=+Qwen3.5-2B base VQA reads PNG; "
            "V2=+Qwen3.5-2B rft2 VQA reads PNG. VQA directly produces the graded readings.")
    else:
        d["audit_category"] = "code_gen"
        d["vqa_mechanism"] = ("Deliverable = code/script (check.py validates code, not image readings). "
            "V0=text agent writes code (no VQA tool); V1/V2=agent + Qwen3.5-2B VQA available as MCP tool "
            "(:30001/:30003) to ask waveform-detail questions. Whether VQA raises pass rate is empirical "
            "-- not pre-judged; let V0 vs V1/V2 speak. Requires the EDA-Eval harness (deepseek agent + sandbox).")
    out.append(d)

with open(WV, "w", encoding="utf-8") as f:
    for d in out:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

from collections import Counter
c = Counter(d["audit_category"] for d in out)
print("refined total", len(out), "categories", dict(c))
ev = [d for d in out if d.get("eval_included")]
print("eval_included", len(ev), "of which image_reading",
      sum(1 for d in ev if d["audit_category"]=="image_reading"),
      "code_gen", sum(1 for d in ev if d["audit_category"]=="code_gen"))
import hashlib
print("sha256", hashlib.sha256(open(WV,'rb').read()).hexdigest())
