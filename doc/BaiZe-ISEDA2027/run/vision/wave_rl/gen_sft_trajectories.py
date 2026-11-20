#!/usr/bin/env python3
"""gen_sft_trajectories.py - Phase 1 Stage-1W SFT data pipeline.

Generates multi-turn dialog trajectories for teaching a 2B MLLM to "read"
waveforms via tool calls (open -> get_signal -> get_values -> submit).

Backed by ngspice .raw + Python (no Synopsys/FSDB/wv needed).
Reuses circuit generators + measurement functions from waveview_gym.py.

Trajectory types:
  - normal:         clean path  open -> get_signal -> get_values -> submit
  - error_recovery: wrong signal name -> dump_hier -> find correct -> retry

Output: JSONL (one trajectory per line) + stats summary.

Author: vision wake#610.  License: project-internal.
"""
from __future__ import annotations
import argparse, json, os, random, sys, tempfile, time, traceback, shutil
from typing import Any, Dict, List, Optional

import numpy as np

# --- reuse waveview_gym infrastructure ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from waveview_gym import (  # noqa: E402
    CircuitSpec, generate_circuit, run_ngspice, parse_ngspice_raw,
    detect_signal_type, measure_period, measure_amplitude,
    measure_rise_time, measure_duty_cycle, _CIRCUIT_GENS,
)

# ---------------------------------------------------------------------------
# 1. Extra circuit generator: differential pair (plan mentions 差分对)
# ---------------------------------------------------------------------------
def _gen_diffpair(rng, wd):
    Vdd = float(rng.uniform(3, 5))
    Iss = float(rng.uniform(50e-6, 200e-6))
    Wn  = float(rng.uniform(2e-6, 10e-6)); L = 1e-6
    per = float(rng.uniform(2e-6, 10e-6))
    Vin_diff = float(rng.uniform(0.1, 0.5))
    rp = os.path.join(wd, "diffpair.raw")
    Vcm = Vdd / 2.0
    nl = (
        f"DIFFPAIR\n"
        f"Vdd vdd 0 {Vdd}\n"
        f"Iss src 0 {Iss}\n"
        f"Vp in_p 0 SINE({Vcm} {Vin_diff} {1.0/per})\n"
        f"Vn in_n 0 SINE({Vcm} {Vin_diff} {1.0/per} 0 0 180)\n"
        f"M1 out_p in_p src 0 nmos W={Wn:.3e} L={L:.3e}\n"
        f"M2 out_n in_n src 0 nmos W={Wn:.3e} L={L:.3e}\n"
        f"R1 vdd out_p {float(rng.uniform(5e3,20e3)):.3e}\n"
        f"R2 vdd out_n {float(rng.uniform(5e3,20e3)):.3e}\n"
        f".model nmos nmos kp=50u vto=0.7\n"
        f".tran {per/200:.3e} {per*5:.3e}\n"
        f".control\nrun\nwrite {rp} v(in_p) v(in_n) v(out_p) v(out_n)\nquit\n.endc\n"
    )
    gt = {"period": per, "amplitude": Vin_diff * 2.0, "vdd": Vdd, "tail_current": Iss}
    params = {"V_dd": Vdd, "Iss": Iss, "Wn": Wn, "L": L, "period": per, "Vin_diff": Vin_diff, "Vcm": Vcm}
    return CircuitSpec("diffpair", nl, rp,
        ["time","v(in_p)","v(in_n)","v(out_p)","v(out_n)"], gt, params)

_CIRCUIT_GENS["diffpair"] = _gen_diffpair

# ---------------------------------------------------------------------------
# 2. Digital circuit generators (ngspice behavioral — no Verilator needed)
# ---------------------------------------------------------------------------

def _gen_ring_osc(rng, wd):
    """3-stage ring oscillator using behavioral comparators + RC delay.

    Produces a full rail-to-rail oscillating digital waveform.
    Period ≈ 2 * n_stages * R * C.
    """
    Vdd = float(rng.uniform(3, 5))
    R_val = float(rng.uniform(500, 3000))
    C_val = float(rng.uniform(0.5e-12, 3e-12))
    n_stages = int(rng.choice([3, 5]))
    rp = os.path.join(wd, "ringosc.raw")
    thresh = Vdd / 2.0
    # Build stages: each stage = behavioral inverter + RC delay
    # The behavioral comparator: V = Vdd if v(input) < thresh else 0
    lines = ["RINGOSC", f"Vdd vdd 0 {Vdd}"]
    sig_vars = []
    prev = "out"
    for i in range(n_stages):
        out_node = "out" if i == n_stages - 1 else f"d{i}"
        n_node = f"n{i}"  # behavioral source always drives intermediate node
        expr = f"{Vdd}*(v({prev}) < {thresh})"
        lines.append(f"B{i+1} {n_node} 0 V={{{expr}}}")
        lines.append(f"R{i+1} {n_node} {out_node} {R_val:.4e}")
        lines.append(f"C{i+1} {out_node} 0 {C_val:.4e}")
        sig_vars.append(f"v({out_node})")
        prev = out_node
    # Initial conditions to break symmetry
    ic_parts = ["v(out)=0"]
    for i in range(n_stages - 1):
        ic_parts.append(f"v(d{i})={Vdd if i % 2 == 0 else 0}")
    lines.append(f".ic {' '.join(ic_parts)}")
    period_est = 2 * n_stages * R_val * C_val
    tstep = period_est / 200
    tstop = period_est * 40
    lines.append(f".tran {tstep:.3e} {tstop:.3e}")
    lines.append(".control")
    lines.append("run")
    lines.append(f"write {rp} {' '.join(sig_vars)}")
    lines.append("quit")
    lines.append(".endc")
    lines.append(".end")
    nl = "\n".join(lines) + "\n"
    gt = {"vdd": Vdd, "n_stages": n_stages, "R": R_val, "C": C_val}
    params = {"Vdd": Vdd, "R": R_val, "C": C_val, "n_stages": n_stages}
    return CircuitSpec("ring_osc", nl, rp,
        ["time"] + sig_vars, gt, params)


def _gen_lc_tank(rng, wd):
    """LC tank circuit with pulse excitation — damped oscillation.

    Produces a decaying sinusoidal waveform with measurable period
    (natural resonant frequency) and amplitude.
    """
    L_val = float(rng.uniform(1e-6, 100e-6))
    C_val = float(rng.uniform(1e-9, 100e-9))
    # Q factor: R = Q * sqrt(L/C).  Q in [5, 50] for visible oscillation.
    Q = float(rng.uniform(5, 50))
    import math
    R_val = Q * math.sqrt(L_val / C_val)
    Vpulse = float(rng.uniform(1, 5))
    rp = os.path.join(wd, "lctank.raw")
    # Resonant frequency
    f0 = 1.0 / (2 * math.pi * math.sqrt(L_val * C_val))
    period0 = 1.0 / f0
    # Pulse: short kick to excite the tank
    pw = period0 * 0.5
    per = period0 * 10
    tstop = period0 * 50
    tstep = period0 / 100
    nl = (
        f"LCTANK\n"
        f"Vin in 0 PULSE(0 {Vpulse} 0 {tstep*5:.3e} {tstep*5:.3e} {pw:.3e} {per:.3e})\n"
        f"L1 in out {L_val:.4e}\n"
        f"C1 out 0 {C_val:.4e}\n"
        f"R1 out 0 {R_val:.4e}\n"
        f".tran {tstep:.3e} {tstop:.3e}\n"
        f".control\nrun\nwrite {rp} v(in) v(out)\nquit\n.endc\n.end\n"
    )
    gt = {"L": L_val, "C": C_val, "R": R_val, "Q": Q, "f0": f0}
    params = {"L": L_val, "C": C_val, "R": R_val, "Q": Q, "Vpulse": Vpulse}
    return CircuitSpec("lc_tank", nl, rp,
        ["time", "v(in)", "v(out)"], gt, params)


_CIRCUIT_GENS["ring_osc"] = _gen_ring_osc
_CIRCUIT_GENS["lc_tank"] = _gen_lc_tank

MEASURE_TARGETS = ["period", "amplitude", "rise_time", "duty_cycle"]

def _pick_signal(spec, target):
    out_candidates = [s for s in spec.signals if "out" in s and s != "time"]
    if out_candidates:
        return out_candidates[0]
    inp = [s for s in spec.signals if s != "time"]
    return inp[0] if inp else "v(in)"

def oracle_measure(raw_parsed, signal_name):
    vns = raw_parsed["var_names"]
    if signal_name not in vns:
        return {}
    idx = vns.index(signal_name)
    t = raw_parsed["data"][:, 0]
    v = raw_parsed["data"][:, idx]
    return {"period": measure_period(t, v), "amplitude": measure_amplitude(v),
            "rise_time": measure_rise_time(t, v), "duty_cycle": measure_duty_cycle(t, v),
            "signal_type": detect_signal_type(v), "n_samples": int(len(v))}

def _fmt_val(v):
    if v is None: return "None"
    if abs(v) < 1e-3 or abs(v) >= 1e6: return f"{v:.6e}"
    return f"{v:.6f}"

SYSTEM_PROMPT = (
    "You are a waveform analysis agent. You interact with a simulation file "
    "via tool calls to measure waveform properties. Available actions:\n"
    "  open(<file>)            - open a simulation .raw file\n"
    "  get_signal(<name>)      - load a signal by name\n"
    "  get_values(<name>)      - retrieve time-value pairs for a signal\n"
    "  dump_hier()             - list all available signals in the file\n"
    "  submit(<type>, <value>) - submit your measurement answer\n"
    "Measure targets: period, amplitude, rise_time, duty_cycle.\n"
    "Be precise. Use the tools step by step."
)

def _clean_dict(d):
    out = {}
    for k, v in d.items():
        if v is None: out[k] = None
        elif isinstance(v, (int, float)): out[k] = float(v)
        else: out[k] = v
    return out

def build_normal_trajectory(spec, raw_parsed, target, traj_id):
    sig = _pick_signal(spec, target)
    oracle = oracle_measure(raw_parsed, sig)
    gt_val = oracle.get(target)
    if gt_val is None or gt_val == 0: return None
    fname = os.path.basename(spec.raw_path)
    n_sig = len(raw_parsed["var_names"]) - 1
    n_pts = raw_parsed["npts"]
    sig_type = oracle.get("signal_type", "analog")
    n_samples = oracle.get("n_samples", n_pts)
    conv = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Open the simulation file {fname} and measure the {target} of signal {sig}."},
        {"role": "assistant", "content": f"open({fname})"},
        {"role": "tool", "content": f"Opened {fname}: {n_pts} time points, {n_sig} signals available."},
        {"role": "assistant", "content": f"get_signal({sig})"},
        {"role": "tool", "content": f"Signal {sig}: type={sig_type}, {n_samples} samples loaded."},
        {"role": "assistant", "content": f"get_values({sig})"},
        {"role": "tool", "content": f"Retrieved {n_samples} time-value pairs for {sig}. t_range=[{_fmt_val(raw_parsed['data'][0,0])}, {_fmt_val(raw_parsed['data'][-1,0])}]."},
        {"role": "assistant", "content": f"submit({target}, {_fmt_val(gt_val)})"},
        {"role": "tool", "content": f"Submitted {target}={_fmt_val(gt_val)}. Relative error: 0.000%. PASS."},
    ]
    return {"id": traj_id, "circuit_type": spec.circuit_type, "measure_target": target,
            "trajectory_type": "normal", "signal": sig, "params": _clean_dict(spec.params),
            "gt": _clean_dict(spec.gt), "oracle": _clean_dict(oracle),
            "submitted_value": float(gt_val), "gt_value": float(gt_val),
            "rel_err": 0.0, "pass": True, "conversation": conv}

def build_error_recovery_trajectory(spec, raw_parsed, target, traj_id):
    sig = _pick_signal(spec, target)
    oracle = oracle_measure(raw_parsed, sig)
    gt_val = oracle.get(target)
    if gt_val is None or gt_val == 0: return None
    fname = os.path.basename(spec.raw_path)
    n_sig = len(raw_parsed["var_names"]) - 1
    n_pts = raw_parsed["npts"]
    sig_type = oracle.get("signal_type", "analog")
    n_samples = oracle.get("n_samples", n_pts)
    available = [n for n in raw_parsed["var_names"] if n != "time"]
    wrong_name = f"v({spec.circuit_type}.clk)"
    if wrong_name == sig: wrong_name = "v(top.clock)"
    conv = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Open the simulation file {fname} and measure the {target} of the clock signal."},
        {"role": "assistant", "content": f"open({fname})"},
        {"role": "tool", "content": f"Opened {fname}: {n_pts} time points, {n_sig} signals available."},
        {"role": "assistant", "content": f"get_signal({wrong_name})"},
        {"role": "tool", "content": f"Error: signal {wrong_name} not found. Use dump_hier() to list available signals."},
        {"role": "assistant", "content": "dump_hier()"},
        {"role": "tool", "content": f"Available signals: {', '.join(available)}"},
        {"role": "assistant", "content": f"get_signal({sig})"},
        {"role": "tool", "content": f"Signal {sig}: type={sig_type}, {n_samples} samples loaded."},
        {"role": "assistant", "content": f"get_values({sig})"},
        {"role": "tool", "content": f"Retrieved {n_samples} time-value pairs for {sig}. t_range=[{_fmt_val(raw_parsed['data'][0,0])}, {_fmt_val(raw_parsed['data'][-1,0])}]."},
        {"role": "assistant", "content": f"submit({target}, {_fmt_val(gt_val)})"},
        {"role": "tool", "content": f"Submitted {target}={_fmt_val(gt_val)}. Relative error: 0.000%. PASS."},
    ]
    return {"id": traj_id, "circuit_type": spec.circuit_type, "measure_target": target,
            "trajectory_type": "error_recovery", "signal": sig, "wrong_signal_attempted": wrong_name,
            "params": _clean_dict(spec.params), "gt": _clean_dict(spec.gt), "oracle": _clean_dict(oracle),
            "submitted_value": float(gt_val), "gt_value": float(gt_val),
            "rel_err": 0.0, "pass": True, "conversation": conv}

def generate_dataset(n_trajectories, seed, output_path, workdir, error_ratio=0.2, verbose=False, circuit_types_filter=None):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    os.makedirs(workdir, exist_ok=True)
    all_types = list(_CIRCUIT_GENS.keys())
    if circuit_types_filter:
        circuit_types = [ct.strip() for ct in circuit_types_filter.split(",") if ct.strip() in all_types]
        if not circuit_types:
            print(f"ERROR: no valid circuit types in filter '{circuit_types_filter}'. Available: {all_types}")
            sys.exit(1)
    else:
        circuit_types = all_types
    results = []
    stats = {"total": 0, "ok": 0, "fail": 0, "by_type": {}, "by_circuit": {},
             "by_target": {}, "ngspice_fail": 0, "measure_skip": 0}
    for i in range(n_trajectories):
        ct = rng.choice(circuit_types)
        target = rng.choice(MEASURE_TARGETS)
        is_error = rng.random() < error_ratio
        traj_id = f"traj_{i:06d}"
        ep_wd = os.path.join(workdir, f"ep_{i:06d}")
        os.makedirs(ep_wd, exist_ok=True)
        try:
            spec = generate_circuit(np_rng, ep_wd, ct)
            ok, log = run_ngspice(spec.netlist)
            if not ok or not os.path.exists(spec.raw_path):
                stats["ngspice_fail"] += 1; stats["fail"] += 1
                if verbose: print(f"  [FAIL] {traj_id} ngspice: {log[:120]}")
                continue
            raw_parsed = parse_ngspice_raw(spec.raw_path)
            if is_error:
                traj = build_error_recovery_trajectory(spec, raw_parsed, target, traj_id)
            else:
                traj = build_normal_trajectory(spec, raw_parsed, target, traj_id)
            if traj is None:
                stats["measure_skip"] += 1; stats["fail"] += 1
                continue
            results.append(traj); stats["ok"] += 1
            tt = traj["trajectory_type"]
            stats["by_type"][tt] = stats["by_type"].get(tt, 0) + 1
            stats["by_circuit"][ct] = stats["by_circuit"].get(ct, 0) + 1
            stats["by_target"][target] = stats["by_target"].get(target, 0) + 1
        except Exception as e:
            stats["fail"] += 1
            if verbose: print(f"  [EXC] {traj_id}: {e}"); traceback.print_exc()
        finally:
            try:
                if os.path.exists(ep_wd): shutil.rmtree(ep_wd, ignore_errors=True)
            except Exception: pass
        stats["total"] = i + 1
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for traj in results:
            f.write(json.dumps(traj, ensure_ascii=False, default=str) + "\n")
    stats["output_path"] = output_path
    stats["output_bytes"] = os.path.getsize(output_path)
    return stats, results

def validate_trajectories(results, n_check=20):
    sample = random.Random(42).sample(results, min(n_check, len(results)))
    checks = {"checked": len(sample), "format_ok": 0, "measure_ok": 0, "errors": []}
    for traj in sample:
        conv = traj.get("conversation", [])
        roles = [m["role"] for m in conv]
        has_system = roles[0] == "system" if roles else False
        has_user = "user" in roles
        has_submit = any("submit(" in m.get("content", "") for m in conv if m["role"] == "assistant")
        if has_system and has_user and has_submit: checks["format_ok"] += 1
        else: checks["errors"].append(f"{traj['id']}: format bad roles={roles}")
        sv = traj.get("submitted_value"); gv = traj.get("gt_value")
        if sv is not None and gv is not None and gv != 0:
            re_ = abs(sv - gv) / abs(gv)
            if re_ < 1e-6: checks["measure_ok"] += 1
            else: checks["errors"].append(f"{traj['id']}: rel_err={re_:.6e}")
        else: checks["measure_ok"] += 1
    return checks

def main():
    p = argparse.ArgumentParser(description="Phase 1 Stage-1W SFT trajectory generator (ngspice-backed)")
    p.add_argument("--n", type=int, default=100)
    p.add_argument("--seed", type=int, default=20261105)
    p.add_argument("--output", type=str, default=None)
    p.add_argument("--workdir", type=str, default=None)
    p.add_argument("--error_ratio", type=float, default=0.2)
    p.add_argument("--circuit_types", type=str, default=None,
                   help="Comma-separated circuit types to generate (default: all). e.g. 'ring_osc,lc_tank'")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    output = args.output or os.path.join(here, "sft_trajectories.jsonl")
    workdir = args.workdir or "/tmp/wave_rl_sft"
    print(f"=== Stage-1W SFT trajectory generator ===")
    print(f"  n_trajectories = {args.n}")
    print(f"  seed           = {args.seed}")
    print(f"  error_ratio    = {args.error_ratio}")
    print(f"  output         = {output}")
    print(f"  workdir        = {workdir}")
    print(f"  circuit_types  = {list(_CIRCUIT_GENS.keys())}")
    print(f"  measure_targets= {MEASURE_TARGETS}")
    t0 = time.time()
    stats, results = generate_dataset(args.n, args.seed, output, workdir, error_ratio=args.error_ratio, verbose=args.verbose, circuit_types_filter=args.circuit_types)
    elapsed = time.time() - t0
    stats["elapsed_s"] = round(elapsed, 2)
    print(f"\n=== Generation complete ({elapsed:.1f}s) ===")
    print(f"  total attempted : {stats['total']}")
    print(f"  ok              : {stats['ok']}")
    print(f"  fail            : {stats['fail']}")
    print(f"    ngspice_fail  : {stats['ngspice_fail']}")
    print(f"    measure_skip  : {stats['measure_skip']}")
    print(f"  by_type         : {stats['by_type']}")
    print(f"  by_circuit      : {stats['by_circuit']}")
    print(f"  by_target       : {stats['by_target']}")
    print(f"  output_bytes    : {stats['output_bytes']}")
    print(f"  throughput      : {stats['ok']/max(elapsed,0.01):.1f} traj/s")
    if args.validate and results:
        v = validate_trajectories(results)
        print(f"\n=== Validation ({v['checked']} sampled) ===")
        print(f"  format_ok  : {v['format_ok']}/{v['checked']}")
        print(f"  measure_ok : {v['measure_ok']}/{v['checked']}")
        if v["errors"]:
            print(f"  errors ({len(v['errors'])}):")
            for e in v["errors"][:10]: print(f"    {e}")
        else: print(f"  All checks PASS.")
    stats_path = output.replace(".jsonl", "_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  stats saved to {stats_path}")
    sys.exit(0 if stats["ok"] > 0 else 1)

if __name__ == "__main__":
    main()
