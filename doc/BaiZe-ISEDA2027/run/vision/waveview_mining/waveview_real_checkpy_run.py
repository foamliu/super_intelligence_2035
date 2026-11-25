#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vision WaveView REAL designflow check.py grading (task book 2026-11-17 16:3x redo).

Re-runs the THREE-ARM对照 on the 10 image-bearing (vqa_runnable) WaveView cases,
graded by designflow's ACTUAL check.py (self-contained oracle recomputed from the
embedded A_PARAMS that generated the real A-PNG) -- NOT the prior reconstruction
oracle (which was misaligned with the current A_PARAMS; e.g. WaveView-002
reconstruction had clk period 1.0 / vref 0.2-0.8 while the real A image is period 2.0
/ vref 0.0-1.0).

Arms (single variable = whether the image is seen, and via which VQA backend):
    V0  baseline = text-only (NO image). Stored text-only model answers mapped to
                   the real deliverable schema; missing -> None -> check.py FAILs.
    V1  +VQA      = base Qwen3.5-2B VQA (:30001) reads the REAL A-PNG.
    V2  +SFT/RL   = base + rft2_adapter VQA (:30003) reads the REAL A-PNG.

Grading: imports each real designflow check.py from /tmp/wv_checks/<case>__check.py
(copied verbatim from 36.15 reference/<case>/check.py). Oracles are embedded
(subprocess recompute from A_PARAMS), so check.py runs locally with no external files.
Runner never decodes the image (no PIL/opencv/OCR/base64) -> audit stays clean.
"""
import json, os, re, sys, time, urllib.request, tempfile, importlib.util, zipfile, io, csv
from math import comb, erfc, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))  # .../run
OUTD = os.path.join(HERE, "real_checkpy_runs")
os.makedirs(OUTD, exist_ok=True)
CHECKS_DIR = "/tmp/wv_checks"
IMG_BASE = os.path.join(RUN_ROOT, "vision", "real_waveview_images")
V0_STORE = os.path.join(RUN_ROOT, "vision", "vqa_tool", "waveview_selftest", "V0")
V1_SERVER = os.environ.get("QWEN35_VQA_SERVER_V1", "http://127.0.0.1:30001")
V2_SERVER = os.environ.get("QWEN35_VQA_SERVER_V2", "http://127.0.0.1:30003")
TRACE = []


def log(op):
    op["t"] = round(time.time(), 3); TRACE.append(op)


def vqa(server, image_path, question, max_new_tokens=120, timeout=180, retries=3):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(server.rstrip("/") + "/vqa",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e; time.sleep(2 + attempt * 2)
    raise last


def num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(x))
    return float(m.group()) if m else None


def _norm(s):
    return str(s or "").lower().replace("-", "").replace("_", "").replace(" ", "")


def extract_val(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.search(r"Final Answer:?\s*\*{0,2}\s*(.+)", s, re.I)
    if m:
        val = re.split(r"[.\n]", m.group(1).strip())[0].strip()
        return val if val else s
    s1 = s.splitlines()[0].strip()
    s1 = re.split(r"[.\n]", s1)[0].strip()
    return s1 if s1 else s


def zip_with_json(obj, json_name):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(json_name, json.dumps(obj, ensure_ascii=False))
    return buf.getvalue()


def zip_with_csv(header, row, csv_name="wv_summary.csv"):
    sio = io.StringIO()
    w = csv.writer(sio); w.writerow(header); w.writerow(row)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(csv_name, sio.getvalue())
    return buf.getvalue()


def write_deliverable(blob, path):
    with open(path, "wb") as f:
        f.write(blob)
    return path


def load_check(check_path):
    spec = importlib.util.spec_from_file_location("chk_" + str(abs(hash(check_path))), check_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_check(mod, deliverable_path, workdir):
    try:
        res = mod.check(str(deliverable_path), workdir)
    except AssertionError as e:
        return False, [], str(e)
    except Exception as e:
        return False, [], "RUNTIME_ERROR: %s" % str(e)[:300]
    if isinstance(res, dict):
        verdict = bool(res.get("pass"))
        conds = res.get("conditions", [])
        ff = next((c.get("detail") for c in conds if not c.get("ok")), "")
        return verdict, conds, ff
    if res is True:
        return True, [], ""
    return False, [], "check returned %r" % res


def _logic_type(v):
    n = _norm(v)
    if "analog" in n or "ramp" in n:
        return "analog"
    return "logic"


CASES = []

# ---- 1. WaveView-002 : 5 stacked signals classification (JSON signals) ----
Q = [
    ("clk_type", "Look at the TOP trace (clk). Is it a logic/digital signal or an analog signal? Answer 'logic' or 'analog'. One word.", "str"),
    ("clk_ntrans", "Look at the TOP trace (clk). How many transitions (rising+falling edges total) over the whole window? Just the integer.", "num"),
    ("clk_period", "What is the period of the clk trace in ns? Just the number.", "num"),
    ("clk_duty", "What is the duty cycle of clk (fraction of the period that is HIGH, 0 to 1)? Just the number.", "num"),
    ("clk_func", "Function of clk? One of: clock, reset, data_bus, reference_ramp, selector. One word.", "str"),
    ("rst_n_type", "2nd trace (rst_n): logic or analog? One word.", "str"),
    ("rst_n_ntrans", "2nd trace (rst_n): how many transitions total? Just the integer.", "num"),
    ("rst_n_func", "Function of rst_n? One of: clock, reset, data_bus, reference_ramp, selector. One word.", "str"),
    ("data_type", "3rd trace (data): logic or analog? One word.", "str"),
    ("data_ntrans", "3rd trace (data): how many transitions total? Just the integer.", "num"),
    ("data_nlevels", "3rd trace (data): how many distinct voltage levels does it have? Just the integer.", "num"),
    ("data_func", "Function of data? One of: clock, reset, data_bus, reference_ramp, selector. One word.", "str"),
    ("vref_type", "4th trace (vref): logic or analog? One word.", "str"),
    ("vref_vmin", "4th trace (vref): minimum voltage in Volts? Just the number.", "num"),
    ("vref_vmax", "4th trace (vref): maximum voltage in Volts? Just the number.", "num"),
    ("vref_func", "Function of vref? One of: clock, reset, data_bus, reference_ramp, selector. One word.", "str"),
    ("sel_type", "5th/bottom trace (sel): logic or analog? One word.", "str"),
    ("sel_ntrans", "5th trace (sel): how many transitions total? Just the integer.", "num"),
    ("sel_npulses", "5th trace (sel): how many pulse windows (high regions)? Just the integer.", "num"),
    ("sel_func", "Function of sel? One of: clock, reset, data_bus, reference_ramp, selector. One word.", "str"),
]
def build_wv002(ans):
    def sig(name, t, **kw):
        d = {"name": name, "type": _logic_type(ans.get(t))}; d.update(kw); return d
    sigs = [
        sig("clk", "clk_type", n_transitions=num(ans.get("clk_ntrans")), function=ans.get("clk_func"),
            period_ns=num(ans.get("clk_period")), duty=num(ans.get("clk_duty"))),
        sig("rst_n", "rst_n_type", n_transitions=num(ans.get("rst_n_ntrans")), function=ans.get("rst_n_func")),
        sig("data", "data_type", n_transitions=num(ans.get("data_ntrans")), function=ans.get("data_func"),
            n_levels=num(ans.get("data_nlevels"))),
        sig("vref", "vref_type", function=ans.get("vref_func"),
            vmin=num(ans.get("vref_vmin")), vmax=num(ans.get("vref_vmax"))),
        sig("sel", "sel_type", n_transitions=num(ans.get("sel_ntrans")), function=ans.get("sel_func"),
            n_pulses=num(ans.get("sel_npulses"))),
    ]
    return zip_with_json({"signals": sigs}, "wv_sigs_report.json")
CASES.append({"id": "EDA-Eval-DesignFlow-WaveView-002", "png": "wv_sigs_A.png",
              "check": "EDA-Eval-DesignFlow-WaveView-002__check.py", "Q": Q, "build": build_wv002,
              "v0_map": {"clk_type": "clk_type", "clk_period": "clk_period", "clk_duty": "clk_duty",
                         "rst_n_type": "rst_n_type", "data_type": "data_type", "data_n_levels": "data_nlevels",
                         "vref_type": "vref_type", "vref_vmin": "vref_vmin", "vref_vmax": "vref_vmax",
                         "sel_type": "sel_type", "sel_n_pulses": "sel_npulses"}})
# ---- 2. WaveMaxFind-001 : damped sinusoid extrema (CSV) ----
Q = [
    ("signal", "What signal name is on the y-axis label? (e.g. v(vb)). Just the label text.", "str"),
    ("max", "Maximum (peak) voltage in Volts? Just the number.", "num"),
    ("t_at_max", "Time (ns) at which the maximum occurs? Just the number.", "num"),
    ("min", "Minimum (trough) voltage in Volts? Just the number.", "num"),
    ("t_at_min", "Time (ns) at which the minimum occurs? Just the number.", "num"),
    ("peak_to_peak", "Peak-to-peak voltage (max minus min) in Volts? Just the number.", "num"),
    ("offset", "DC offset (midline) voltage in Volts? Just the number.", "num"),
    ("period", "Period of oscillation in ns? Just the number.", "num"),
]
def build_wavemax(ans):
    hdr = ["signal", "max", "t_at_max", "min", "t_at_min", "peak_to_peak", "offset", "period"]
    row = [str(ans.get("signal") or ""), str(num(ans.get("max")) or ""),
           str(num(ans.get("t_at_max")) or ""), str(num(ans.get("min")) or ""),
           str(num(ans.get("t_at_min")) or ""), str(num(ans.get("peak_to_peak")) or ""),
           str(num(ans.get("offset")) or ""), str(num(ans.get("period")) or "")]
    return zip_with_csv(hdr, row)
CASES.append({"id": "EDA-Eval-DesignFlow-WaveMaxFind-001", "png": "wave_vb_A.png",
              "check": "EDA-Eval-DesignFlow-WaveMaxFind-001__check.py", "Q": Q, "build": build_wavemax,
              "v0_map": {"signal": "signal", "max": "max", "t_at_max_ns": "t_at_max", "min": "min",
                         "t_at_min_ns": "t_at_min", "peak_to_peak": "peak_to_peak", "offset": "offset",
                         "period_ns": "period"}})
# ---- 3. TempThreshChar-001 : threshold detector (JSON) ----
Q = [
    ("detector_function", "Function of the bottom detector signal v(det)? One of: threshold_detector, schmitt_trigger, hysteresis_comparator, comparator. One word/phrase.", "str"),
    ("vmax", "TOP v(temp): peak/maximum voltage in Volts? Just the number.", "num"),
    ("vmin", "TOP v(temp): minimum/baseline voltage in Volts? Just the number.", "num"),
    ("t_at_max", "TOP v(temp): time (us) at which the peak occurs? Just the number.", "num"),
    ("ramp_slope", "Ramp up slope of v(temp) in V/us? Just the number.", "num"),
    ("vth_high", "Upper trip threshold vth_high in Volts? Just the number.", "num"),
    ("vth_low", "Lower trip threshold vth_low in Volts? Just the number.", "num"),
    ("hysteresis", "Hysteresis (vth_high minus vth_low) in Volts? Just the number.", "num"),
    ("t_cross_up", "BOTTOM v(det): time (us) it first goes HIGH? Just the number.", "num"),
    ("t_cross_down", "BOTTOM v(det): time (us) it goes back LOW? Just the number.", "num"),
    ("n_transitions", "BOTTOM v(det): how many transitions total? Just the integer.", "num"),
    ("duty", "Duty cycle of v(det) (fraction of time HIGH, 0 to 1)? Just the number.", "num"),
]
def build_ttc(ans):
    obj = {"detector_function": ans.get("detector_function"), "vmax": num(ans.get("vmax")),
           "vmin": num(ans.get("vmin")), "t_at_max_us": num(ans.get("t_at_max")),
           "ramp_slope_v_per_us": num(ans.get("ramp_slope")), "vth_high": num(ans.get("vth_high")),
           "vth_low": num(ans.get("vth_low")), "hysteresis_v": num(ans.get("hysteresis")),
           "t_cross_up_us": num(ans.get("t_cross_up")), "t_cross_down_us": num(ans.get("t_cross_down")),
           "n_transitions": num(ans.get("n_transitions")), "duty": num(ans.get("duty"))}
    return zip_with_json(obj, "thresh_report.json")
CASES.append({"id": "EDA-Eval-DesignFlow-TempThreshChar-001", "png": "thresh_char_A.png",
              "check": "EDA-Eval-DesignFlow-TempThreshChar-001__check.py", "Q": Q, "build": build_ttc,
              "v0_map": {"vth_high": "vth_high", "vth_low": "vth_low", "hysteresis": "hysteresis",
                         "t_cross_up": "t_cross_up", "t_cross_down": "t_cross_down",
                         "n_transitions": "n_transitions", "vmax": "vmax", "t_at_max": "t_at_max"}})
# ---- 4. EyeApertureSelect-001 : VREF sweep optimum (CSV) ----
Q = [
    ("name", "What name/label is associated with this sweep? (look for a name string). Just the name.", "str"),
    ("vref", "A VREF is valid only if skew<=15 AND eye_height>=100. Among VALID VREFs, which VREF (mV) has the LARGEST max_width? Just the number.", "num"),
    ("aperture", "At that optimal VREF, what is the max_width (aperture) in ps? Just the number.", "num"),
    ("skew", "At that optimal VREF, what is the skew in ps? Just the number.", "num"),
    ("height", "At that optimal VREF, what is the eye_height in mV? Just the number.", "num"),
]
def build_eye(ans):
    hdr = ["name", "corner", "aperture_ps", "vref_mV", "skew_ps", "eye_height_mV"]
    nm = str(ans.get("name") or "")
    row = [nm, nm, str(num(ans.get("aperture")) or ""), str(num(ans.get("vref")) or ""),
           str(num(ans.get("skew")) or ""), str(num(ans.get("height")) or "")]
    return zip_with_csv(hdr, row)
CASES.append({"id": "EDA-Eval-DesignFlow-EyeApertureSelect-001", "png": "eye_sweep_A.png",
              "check": "EDA-Eval-DesignFlow-EyeApertureSelect-001__check.py", "Q": Q, "build": build_eye,
              "v0_map": {"optimal_vref": "vref", "max_width_at_opt": "aperture", "skew_at_opt": "skew",
                         "height_at_opt": "height"}})
# ---- 5. RiseEdgeMarginMeas-001 : rise-edge margin (JSON) ----
Q = [
    ("ref_signal", "Which signal rises FIRST (the reference)? 'clk_a' or 'data_a'? One word.", "str"),
    ("target_signal", "Which signal rises SECOND (the target)? 'clk_a' or 'data_a'? One word.", "str"),
    ("ref_edge_time", "Time (ns) at which the FIRST-rising signal crosses 50% of its swing on the rising edge? Just the number.", "num"),
    ("target_edge_time", "Time (ns) at which the SECOND-rising signal crosses 50% of its swing on the rising edge? Just the number.", "num"),
    ("margin_ns", "Margin = target_edge_time minus ref_edge_time, in ns? Just the number.", "num"),
    ("swing", "Peak-to-peak swing (the high level reached) in Volts? Just the number.", "num"),
]
def build_rise(ans):
    obj = {"ref_signal": ans.get("ref_signal"), "target_signal": ans.get("target_signal"),
           "ref_edge_time": num(ans.get("ref_edge_time")), "target_edge_time": num(ans.get("target_edge_time")),
           "margin_ns": num(ans.get("margin_ns")), "signals": [ans.get("ref_signal"), ans.get("target_signal")],
           "annotation": {"label": "margin=%s" % (num(ans.get("margin_ns")))}}
    return zip_with_json(obj, "rise_margin_report.json")
CASES.append({"id": "EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001", "png": "rise_margin_A.png",
              "check": "EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001__check.py", "Q": Q, "build": build_rise,
              "v0_map": {"ref_signal": "ref_signal", "ref_edge_time": "ref_edge_time",
                         "target_edge_time": "target_edge_time", "margin_ns": "margin_ns", "swing": "swing"}})
# __APPEND_CASES_6__
# __APPEND_RUNNERS__
