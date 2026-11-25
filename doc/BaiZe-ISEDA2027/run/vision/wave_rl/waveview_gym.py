#!/usr/bin/env python3
"""waveview_gym.py - Gym-style deterministic env for waveform RL (Phase 0).
Backed by ngspice .raw + numpy (no Synopsys/FSDB/wv). Author: vision wake#609."""
from __future__ import annotations
import argparse, json, os, re, struct, subprocess, sys, tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# --- 1. ngspice binary .raw parser ---
def parse_ngspice_raw(path):
    with open(path, "rb") as f: raw = f.read()
    bm = raw.find(b"Binary:")
    if bm < 0: raise ValueError(f"No Binary marker in {path}")
    header = raw[:bm].decode("ascii", errors="replace")
    bd = raw[bm+8:]
    nv = int(re.search(r"No\. Variables:\s+(\d+)", header).group(1))
    np_ = int(re.search(r"No\. Points:\s+(\d+)", header).group(1))
    vn, vt = [], []
    for m in re.finditer(r"\t(\d+)\t(\S+)\t(\S+)", header):
        i = int(m.group(1))
        while len(vn) <= i: vn.append(""); vt.append("")
        vn[i] = m.group(2); vt[i] = m.group(3)
    ed, ef = np_*nv*8, np_*nv*4
    if len(bd) >= ed: vals = struct.unpack(f"<{np_*nv}d", bd[:ed])
    elif len(bd) >= ef: vals = struct.unpack(f"<{np_*nv}f", bd[:ef])
    else: raise ValueError(f"Binary too short: {len(bd)}")
    return {"nvars": nv, "npts": np_, "var_names": vn, "var_types": vt,
            "data": np.array(vals, dtype=np.float64).reshape(np_, nv)}

# --- 2. Circuit generators ---
@dataclass
class CircuitSpec:
    circuit_type: str; netlist: str; raw_path: str
    signals: List[str]; gt: Dict[str, float]; params: Dict[str, float]

def _gen_rc(rng, wd):
    R=float(rng.uniform(500,5000)); C=float(rng.uniform(1e-9,10e-9))
    Vh=float(rng.uniform(3,5)); per=float(rng.uniform(5e-6,20e-6))
    rp=os.path.join(wd,"rc.raw")
    nl=f"RC\nV1 in 0 PULSE(0 {Vh} 0 {per*0.01:.3e} {per*0.01:.3e} {per*0.5:.3e} {per:.3e})\nR1 in out {R}\nC1 out 0 {C}\n.tran {per/100:.3e} {per*5:.3e}\n.control\nrun\nwrite {rp} v(in) v(out)\nquit\n.endc\n"
    return CircuitSpec("rc",nl,rp,["time","v(in)","v(out)"],{"period":per,"amplitude":Vh,"time_constant":R*C,"rise_time_10_90":2.2*R*C},{"R":R,"C":C,"V_hi":Vh,"period":per})

def _gen_rc_pulse(rng, wd):
    R=float(rng.uniform(1e3,5e3)); C=float(rng.uniform(0.5e-9,5e-9))
    Vh=float(rng.uniform(2.5,5)); per=float(rng.uniform(2e-6,10e-6)); duty=float(rng.uniform(0.3,0.7))
    rp=os.path.join(wd,"rcp.raw")
    nl=f"RCP\nV1 in 0 PULSE(0 {Vh} 0 {per*0.005:.3e} {per*0.005:.3e} {per*duty:.3e} {per:.3e})\nR1 in out {R}\nC1 out 0 {C}\n.tran {per/200:.3e} {per*10:.3e}\n.control\nrun\nwrite {rp} v(in) v(out)\nquit\n.endc\n"
    return CircuitSpec("rc_pulse",nl,rp,["time","v(in)","v(out)"],{"period":per,"amplitude":Vh,"duty_cycle":duty,"time_constant":R*C},{"R":R,"C":C,"V_hi":Vh,"period":per,"duty":duty})

def _gen_inverter(rng, wd):
    Vdd=float(rng.uniform(3,5)); Wn=float(rng.uniform(1e-6,5e-6)); Wp=2.5*Wn; L=1e-6
    per=float(rng.uniform(1e-6,5e-6)); rp=os.path.join(wd,"inv.raw")
    nl=f"INV\nVdd vdd 0 {Vdd}\nVin in 0 PULSE(0 {Vdd} 0 {per*0.001:.3e} {per*0.001:.3e} {per*0.5:.3e} {per:.3e})\nMn out in 0 0 nmos W={Wn:.3e} L={L:.3e}\nMp out in vdd vdd pmos W={Wp:.3e} L={L:.3e}\n.model nmos nmos kp=50u vto=0.7\n.model pmos pmos kp=20u vto=-0.7\n.tran {per/500:.3e} {per*6:.3e}\n.control\nrun\nwrite {rp} v(in) v(out)\nquit\n.endc\n"
    return CircuitSpec("inverter",nl,rp,["time","v(in)","v(out)"],{"period":per,"amplitude":Vdd,"vdd":Vdd},{"V_dd":Vdd,"Wn":Wn,"Wp":Wp,"L":L,"period":per})

def _gen_rl(rng, wd):
    R=float(rng.uniform(100,1e3)); L=float(rng.uniform(1e-6,10e-6)); Vh=float(rng.uniform(3,5))
    per=float(rng.uniform(10e-6,40e-6)); rp=os.path.join(wd,"rl.raw")
    nl=f"RL\nV1 in 0 PULSE(0 {Vh} 0 {per*0.01:.3e} {per*0.01:.3e} {per*0.5:.3e} {per:.3e})\nR1 in out {R}\nL1 out 0 {L}\n.tran {per/100:.3e} {per*5:.3e}\n.control\nrun\nwrite {rp} v(in) v(out) i(l1)\nquit\n.endc\n"
    return CircuitSpec("rl",nl,rp,["time","v(in)","v(out)","i(l1)"],{"period":per,"amplitude":Vh,"time_constant":L/R},{"R":R,"L":L,"V_hi":Vh,"period":per})

_CIRCUIT_GENS = {"rc":_gen_rc,"rc_pulse":_gen_rc_pulse,"inverter":_gen_inverter,"rl":_gen_rl}

def generate_circuit(rng, wd, ct=None):
    if ct is None: ct = str(rng.choice(list(_CIRCUIT_GENS.keys())))
    return _CIRCUIT_GENS[ct](rng, wd)

def run_ngspice(netlist, timeout=30):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".cir",delete=False,dir="/tmp") as f:
        f.write(netlist); p = f.name
    try:
        r = subprocess.run(["ngspice","-b",p],capture_output=True,text=True,timeout=timeout)
        return r.returncode == 0, r.stdout + r.stderr
    except subprocess.TimeoutExpired: return False, "TIMEOUT"
    finally: os.unlink(p)

# --- 3. Signal analysis (Python replacements for WaveView Tcl APIs) ---
def detect_signal_type(values, threshold=0.25):
    if len(values) == 0: return "analog"
    vr = float(values.max() - values.min())
    if vr < 1e-12: return "analog"
    norm = (values - values.min()) / max(vr, 1e-12)
    return "digital" if float(norm.std()) < threshold else "analog"

def measure_period(time, signal):
    if len(signal) < 4: return None
    vm = (signal.max() + signal.min()) / 2.0
    above = signal > vm
    rising = np.where((~above[:-1]) & (above[1:]))[0]
    if len(rising) < 2: return None
    periods = np.diff(time[rising + 1])
    return float(np.median(periods)) if len(periods) > 0 else None

def measure_amplitude(signal):
    return float(signal.max() - signal.min())

def measure_rise_time(time, signal):
    vmin, vmax = float(signal.min()), float(signal.max())
    vr = vmax - vmin
    if vr < 1e-9: return None
    v10, v90 = vmin + 0.1*vr, vmin + 0.9*vr
    t10i = np.where(signal > v10)[0]
    if len(t10i) == 0: return None
    t10 = time[t10i[0]]
    t90i = np.where((time > t10) & (signal > v90))[0]
    if len(t90i) == 0: return None
    return float(time[t90i[0]] - t10)

def measure_duty_cycle(time, signal):
    if len(signal) < 4: return None
    vm = (signal.max() + signal.min()) / 2.0
    return float(np.sum(signal > vm)) / len(signal)


# --- 4. Gym environment ---
@dataclass
class EpisodeState:
    raw_parsed: Optional[Dict] = None; opened: bool = False
    opened_signals: Dict[str, Dict] = field(default_factory=dict)
    wv_calls: int = 0; steps: int = 0; submitted: bool = False
    submit_value: Optional[float] = None; submit_measure_type: Optional[str] = None
    submit_signal: Optional[str] = None; history: List[Dict] = field(default_factory=list)

class WaveformGymEnv:
    """Gym-style env: ngspice .raw + Python. 7 actions A1-A7. MAX_WV=3."""
    MAX_WV_CALLS = 3; MAX_STEPS = 15
    ACTION_NAMES = ["open","get_signal","get_type","get_bits","get_values","dump_hier","submit"]

    def __init__(self, circuit_type=None, seed=None, workdir=None, measure_target="period"):
        self.circuit_type = circuit_type
        self.rng = np.random.default_rng(seed)
        self.workdir = workdir or tempfile.mkdtemp(prefix="wave_rl_", dir="/tmp")
        os.makedirs(self.workdir, exist_ok=True)
        self.measure_target = measure_target
        self.spec = None; self.state = None

    def reset(self):
        self.spec = generate_circuit(self.rng, self.workdir, self.circuit_type)
        ok, log = run_ngspice(self.spec.netlist)
        if not ok or not os.path.exists(self.spec.raw_path):
            raise RuntimeError(f"ngspice failed: {log[:200]}")
        self.state = EpisodeState(); return self._get_obs()

    def step(self, action, **kw):
        if self.state is None: raise RuntimeError("Call reset() first")
        self.state.steps += 1
        info = {"action": action, "step": self.state.steps, "wv_calls": self.state.wv_calls}
        reward = 0.0; done = False
        if action == "open":
            if self.state.opened: info["result"] = "already_open"
            elif self.state.wv_calls >= self.MAX_WV_CALLS: info["result"]="budget_exhausted"; done=True; reward=-0.1
            else:
                self.state.wv_calls += 1
                self.state.raw_parsed = parse_ngspice_raw(self.spec.raw_path)
                self.state.opened = True; info["result"] = "ok"
                info["n_signals"] = len(self.state.raw_parsed["var_names"]) - 1
                info["n_points"] = self.state.raw_parsed["npts"]
        elif action == "get_signal":
            sn = kw.get("signal_name","")
            if not self.state.opened: info["result"]="file_not_open"; reward=-0.05
            elif self.state.wv_calls >= self.MAX_WV_CALLS: info["result"]="budget_exhausted"; done=True; reward=-0.1
            else:
                self.state.wv_calls += 1; vns = self.state.raw_parsed["var_names"]
                if sn in vns:
                    idx=vns.index(sn); vals=self.state.raw_parsed["data"][:,idx]; st=detect_signal_type(vals)
                    self.state.opened_signals[sn]={"handle":idx,"values":vals,"type":st,"bits":1 if st=="digital" else 0,"nsamples":len(vals)}
                    info["result"]="ok"; info["type"]=st; info["nsamples"]=len(vals)
                else: info["result"]="signal_not_found"; info["available"]=[n for n in vns if n!="time"]; reward=-0.02
        elif action == "get_type":
            sn=kw.get("signal_name","")
            if sn in self.state.opened_signals: info["result"]="ok"; info["type"]=self.state.opened_signals[sn]["type"]
            else: info["result"]="signal_not_opened"; reward=-0.01
        elif action == "get_bits":
            sn=kw.get("signal_name","")
            if sn in self.state.opened_signals: info["result"]="ok"; info["bits"]=self.state.opened_signals[sn]["bits"]
            else: info["result"]="signal_not_opened"; reward=-0.01
        elif action == "get_values":
            sn=kw.get("signal_name","")
            if not self.state.opened: info["result"]="file_not_open"; reward=-0.05
            elif self.state.wv_calls >= self.MAX_WV_CALLS: info["result"]="budget_exhausted"; done=True; reward=-0.1
            else:
                self.state.wv_calls += 1
                if sn in self.state.opened_signals:
                    sig=self.state.opened_signals[sn]; vals=sig["values"]; tc=self.state.raw_parsed["data"][:,0]
                    info["result"]="ok"; info["n_samples"]=len(vals)
                    info["value_range"]=[float(vals.min()),float(vals.max())]
                    info["time_range"]=[float(tc.min()),float(tc.max())]; sig["time"]=tc
                else: info["result"]="signal_not_opened"; reward=-0.02
        elif action == "dump_hier":
            if not self.state.opened: info["result"]="file_not_open"; reward=-0.02
            else:
                vns=self.state.raw_parsed["var_names"]; info["result"]="ok"; info["signals"]=[n for n in vns if n!="time"]
        elif action == "submit":
            val=kw.get("value",None); mt=kw.get("measure_type",self.measure_target); sn=kw.get("signal_name","")
            self.state.submitted=True; self.state.submit_value=val
            self.state.submit_measure_type=mt; self.state.submit_signal=sn
            done=True; reward=self._compute_reward(val,mt,sn)
            info["reward"]=reward; info["gt"]=self.spec.gt.get(mt); info["submitted_value"]=val
        else: info["result"]="invalid_action"; reward=-0.05
        if not done and self.state.steps >= self.MAX_STEPS: done=True; reward=-0.1; info["result"]="step_limit"
        self.state.history.append({"action":action,"info":info,"reward":reward})
        return self._get_obs(), reward, done, info


    def _get_obs(self):
        s = self.state; obs = {"opened": s.opened,
            "wv_calls_remaining": max(0, self.MAX_WV_CALLS - s.wv_calls),
            "steps_remaining": max(0, self.MAX_STEPS - s.steps),
            "opened_signals": list(s.opened_signals.keys()),
            "measure_target": self.measure_target,
            "circuit_type": self.spec.circuit_type if self.spec else None,
            "submitted": s.submitted}
        if s.opened and s.raw_parsed:
            obs["n_signals"] = len(s.raw_parsed["var_names"]) - 1
            obs["n_points"] = s.raw_parsed["npts"]
        return obs

    def _compute_reward(self, value, measure_type, signal_name):
        if value is None: return -0.5
        gt = self.spec.gt.get(measure_type)
        if gt is None or gt == 0: return -0.5
        try: value = float(value)
        except (TypeError, ValueError): return -0.5
        rel_err = abs(value - gt) / abs(gt)
        r_main = 1.0 if rel_err<=0.01 else 0.7 if rel_err<=0.05 else 0.4 if rel_err<=0.10 else 0.1 if rel_err<=0.25 else 0.0
        r_ev = 0.3 if (self.state.opened and len(self.state.opened_signals) > 0) else 0.0
        r_bud = 0.1 * (1.0 - self.state.wv_calls / self.MAX_WV_CALLS)
        r_den = min(sum(0.02 for h in self.state.history if h["info"].get("result")=="ok" and h["action"]!="submit"), 0.2)
        r_anti = -2.0 if (not self.state.opened and value is not None) else 0.0
        return r_main + r_ev + r_bud + r_den + r_anti

    def get_ground_truth(self):
        return self.spec.gt if self.spec else {}

    def oracle_measure(self):
        if not self.state or not self.state.opened or not self.state.raw_parsed: return {}
        data = self.state.raw_parsed["data"]; time = data[:, 0]; res = {}
        for i, name in enumerate(self.state.raw_parsed["var_names"]):
            if name == "time": continue
            vals = data[:, i]
            res[name] = {"type": detect_signal_type(vals), "amplitude": measure_amplitude(vals),
                "period": measure_period(time, vals), "rise_time": measure_rise_time(time, vals),
                "duty_cycle": measure_duty_cycle(time, vals)}
        return res

# --- 5. Smoke test ---
def smoke_test(n_episodes=1, seed=42):
    results = []
    for ep in range(n_episodes):
        env = WaveformGymEnv(seed=seed+ep, measure_target="period")
        try:
            obs = env.reset()
            r = {"episode": ep, "circuit_type": env.spec.circuit_type, "reset_ok": True, "actions": []}
            for act, kw in [("open",{}),("get_signal",{"signal_name":"v(in)"}),("get_values",{"signal_name":"v(in)"})]:
                obs, reward, done, info = env.step(act, **kw)
                r["actions"].append({"action":act,"reward":reward,"done":done,"result":info.get("result"),"wv_calls":info.get("wv_calls")})
                if done: break
            if "v(in)" in env.state.opened_signals:
                sig = env.state.opened_signals["v(in)"]
                tc = sig.get("time", env.state.raw_parsed["data"][:,0])
                period = measure_period(tc, sig["values"])
                if period is not None:
                    obs, reward, done, info = env.step("submit", value=period, measure_type="period", signal_name="v(in)")
                    r["actions"].append({"action":"submit","reward":reward,"done":done,"result":info.get("result"),"submitted_value":info.get("submitted_value"),"gt":info.get("gt")})
                    r["total_reward"] = sum(a["reward"] for a in r["actions"])
                    r["submitted_value"] = period; r["gt_period"] = env.spec.gt["period"]
                    r["rel_err"] = abs(period - env.spec.gt["period"]) / env.spec.gt["period"]
                    r["pass"] = r["rel_err"] <= 0.05
                else: r["error"] = "measure_period=None"; r["pass"] = False
            else: r["error"] = "v(in) not opened"; r["pass"] = False
            r["oracle"] = env.oracle_measure()
            results.append(r)
        except Exception as e:
            results.append({"episode": ep, "error": str(e), "pass": False})
    return {"n_episodes": n_episodes,
            "n_pass": sum(1 for r in results if r.get("pass")),
            "n_fail": sum(1 for r in results if not r.get("pass")),
            "results": results}

def main():
    p = argparse.ArgumentParser(description="WaveformGymEnv smoke test")
    p.add_argument("--smoke", action="store_true"); p.add_argument("--n", type=int, default=1)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    if a.smoke:
        print(f"=== WaveformGymEnv smoke test ({a.n} episodes) ===")
        s = smoke_test(n_episodes=a.n, seed=a.seed)
        print(json.dumps(s, indent=2, default=str))
        print(f"\n=== {s['n_pass']}/{s['n_episodes']} PASS ===")
        sys.exit(0 if s["n_pass"] > 0 else 1)
    else: p.print_help()

if __name__ == "__main__":
    main()

