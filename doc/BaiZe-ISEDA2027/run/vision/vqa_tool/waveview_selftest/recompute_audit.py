#!/usr/bin/env python3
"""Recompute the cheat audit from the saved trace with the corrected static
scan (excludes audit()'s own forbidden-pattern definition lines so the regex
strings don't self-match). Updates audit.json + summary.json['audit'] in place.
No model calls, no image reads -- pure audit recompute on already-saved trace."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
summ = json.load(open(os.path.join(HERE, "summary.json")))
trace = summ.get("trace", [])
forbidden = [r"PIL\.(Image|Image open)", r"cv2\.imread", r"pytesseract", r"tesseract",
             r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)"]
findings = []
for op in trace:
    if op.get("arm") == "V0" and op.get("op") in ("vqa_call", "image_read"):
        findings.append({"severity": "cheat", "op": op, "why": "V0 arm touched image/vqa"})
src = open(os.path.join(HERE, "waveview_selftest_run.py")).read()
_fstart = src.find("forbidden = [")
_fend = src.find("]", _fstart) + 1
src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
for pat in forbidden:
    if re.search(pat, src_scan):
        findings.append({"severity": "review", "pattern": pat,
                         "why": "forbidden image-bypass token present in runner source"})
cheat = any(f["severity"] == "cheat" for f in findings)
aud = {"cheat": cheat,
        "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
        "findings": findings,
        "v0_vqa_calls": sum(1 for o in trace if o.get("arm") == "V0" and o.get("op") == "vqa_call"),
        "v1_vqa_calls": sum(1 for o in trace if o.get("arm") == "V1" and o.get("op") == "vqa_call"),
        "v0_image_reads": sum(1 for o in trace if o.get("arm") == "V0" and o.get("op") == "image_read")}
json.dump(aud, open(os.path.join(HERE, "audit.json"), "w"), ensure_ascii=False, indent=1)
summ["audit"] = aud
json.dump(summ, open(os.path.join(HERE, "summary.json"), "w"), ensure_ascii=False, indent=1)
print("recomputed audit:", json.dumps(aud, ensure_ascii=False))
