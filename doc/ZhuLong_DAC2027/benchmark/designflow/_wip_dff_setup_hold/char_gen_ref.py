#!/usr/bin/env python3
# -*- coding: ascii -*-
"""char_gen_ref.py -- DFF setup/hold/tCQ timing characterization.

Usage: char_gen.py <dff_netlist> <params.json> <out_dir>

Generates a setup-time sweep (D-to-CLK lead time) and a hold-time sweep
(D return after CLK) plus a tCQ measurement, runs HSPICE .tran per sweep
point, parses .measure results (with SI suffix awareness), and writes
result.json: {tSU, tH, tCQ, hspice_ran, vq_setup_critical,
vq_hold_critical, n_setup_pts, n_hold_pts}.

Two independent sweep variables (tsu_lead for setup, th_lag for hold) are
used -- NOT a single tskew that would seesaw setup and hold boundaries.
The hold observation window is set to (t_clk4 + tclk/2 - 50p), i.e. inside
the CLK=1 transparent phase and strictly before the next CLK edge, so that
a real hold violation (Q flipping) is observable rather than masked.
"""
import subprocess, os, sys, re, json

SI = {'t':1e12, 'g':1e9, 'meg':1e6, 'k':1e3, 'm':1e-3,
      'u':1e-6, 'n':1e-9, 'p':1e-12, 'f':1e-15, 'a':1e-18}


def parse_num(s):
    if s is None:
        return None
    s = s.strip().lower()
    if s in ('failed', 'fail', 'error', 'nan', 'inf', '-failed', '+failed', ''):
        return None
    m = re.match(r'^([+-]?[0-9]*\.?[0-9]+(?:e[+-]?[0-9]+)?)([a-z]*)$', s)
    if not m:
        return None
    val = float(m.group(1))
    suf = m.group(2)
    if suf == '':
        return val
    if suf in SI:
        return val * SI[suf]
    for k, v in SI.items():
        if suf.startswith(k):
            return val * v
    return None


def run_hspice(deck_path, cwd):
    try:
        r = subprocess.run(['hspice', '-i', os.path.abspath(deck_path), '-o', os.path.join(cwd, 'out')],
                           capture_output=True, text=True, timeout=120, cwd=cwd)
        return r
    except Exception:
        return None


def parse_meas(lis_path, names):
    out = {}
    if not os.path.exists(lis_path):
        return out
    txt = open(lis_path, errors='ignore').read()
    for n in names:
        m = re.search(r'^\s*' + n + r'\s*=\s*(\S+)', txt, re.M)
        if m:
            out[n] = parse_num(m.group(1))
            out[n + '_raw'] = m.group(1)
    return out


def hspice_ran(lis_path):
    if not os.path.exists(lis_path):
        return False
    t = open(lis_path, errors='ignore').read().lower()
    return 'job concluded' in t


def build_setup_tb(netlist, params, tsu_lead):
    vdd = params['vdd']
    tclk = params['tclk']
    t_clk4 = 4.0 * tclk
    t_d_rise = t_clk4 - tsu_lead
    obs = t_clk4 + params['obs_setup_offset']
    tstop = t_clk4 + tclk
    # .ic breaks SR-latch DC metastability (slave holds at t=0 -> bistable)
    ic = (f".ic v(xdff.qm)=0 v(xdff.qmb)={vdd} "
          f"v(xdff.q)=0 v(xdff.qsb)={vdd} v(xdff.clk_b)={vdd}")
    return f"""* setup_tb tsu_lead={tsu_lead}
.inc '{netlist}'
VVDD vdd 0 {vdd}
VCLK CLK 0 PULSE(0 {vdd} {tclk} 5p 5p {tclk/2.0} {tclk})
VDIN D 0 PULSE(0 {vdd} {t_d_rise} 5p 5p {tstop} {2*tstop})
XDFF D CLK Q Qb vdd 0 dff
CL Q 0 {params['cl']}
.tran 1p {tstop} uic
{ic}
.meas tran vq_setup find v(Q) at={obs}
.meas tran tCQ trig v(CLK) val={vdd/2.0} rise=4 targ v(Q) val={vdd/2.0} rise=1
.end
"""


def build_hold_tb(netlist, params, th_lag):
    vdd = params['vdd']
    tclk = params['tclk']
    t_clk4 = 4.0 * tclk
    tsu_nom = params['tsu_nominal']
    t_d_rise = t_clk4 - tsu_nom
    pw = tsu_nom + th_lag
    obs = t_clk4 + params['obs_hold_offset']
    tstop = t_clk4 + tclk
    ic = (f".ic v(xdff.qm)=0 v(xdff.qmb)={vdd} "
          f"v(xdff.q)=0 v(xdff.qsb)={vdd} v(xdff.clk_b)={vdd}")
    return f"""* hold_tb th_lag={th_lag}
.inc '{netlist}'
VVDD vdd 0 {vdd}
VCLK CLK 0 PULSE(0 {vdd} {tclk} 5p 5p {tclk/2.0} {tclk})
VDIN D 0 PULSE(0 {vdd} {t_d_rise} 5p 5p {pw} {2*tstop})
XDFF D CLK Q Qb vdd 0 dff
CL Q 0 {params['cl']}
.tran 1p {tstop} uic
{ic}
.meas tran vq_hold find v(Q) at={obs}
.end
"""


def characterize(netlist, params, outdir):
    os.makedirs(outdir, exist_ok=True)
    ran = False
    vdd = params['vdd']
    vthr = vdd * params['vq_threshold_frac']

    # ---- setup sweep: find min tsu_lead where Q captured (vq_setup > vthr) ----
    setup_pts = []
    tcq_val = None
    for tsu in params['tsu_sweep']:
        sub = os.path.join(outdir, f"setup_{int(tsu*1e12)}")
        os.makedirs(sub, exist_ok=True)
        deck = os.path.join(sub, "tb.sp")
        open(deck, 'w').write(build_setup_tb(netlist, params, tsu))
        run_hspice(deck, sub)
        lis = os.path.join(sub, "out.lis")
        if hspice_ran(lis):
            ran = True
        meas = parse_meas(lis, ['vq_setup', 'tCQ'])
        vq = meas.get('vq_setup')
        setup_pts.append((tsu, vq))
        if vq is not None and vq > vthr and tcq_val is None:
            tcq_val = meas.get('tCQ')

    tSU = None
    vq_setup_critical = None
    for tsu, vq in setup_pts:
        if vq is not None and vq > vthr:
            tSU = tsu
            vq_setup_critical = vq
            break

    # ---- hold sweep: find min th_lag where Q held (vq_hold > vthr) ----
    hold_pts = []
    for th in params['th_sweep']:
        sub = os.path.join(outdir, f"hold_{int(th*1e12)}")
        os.makedirs(sub, exist_ok=True)
        deck = os.path.join(sub, "tb.sp")
        open(deck, 'w').write(build_hold_tb(netlist, params, th))
        run_hspice(deck, sub)
        lis = os.path.join(sub, "out.lis")
        if hspice_ran(lis):
            ran = True
        meas = parse_meas(lis, ['vq_hold'])
        hold_pts.append((th, meas.get('vq_hold')))

    tH = None
    vq_hold_critical = None
    for th, vq in hold_pts:
        if vq is not None and vq > vthr:
            tH = th
            vq_hold_critical = vq
            break

    result = {
        "tSU": tSU,
        "tH": tH,
        "tCQ": tcq_val,
        "hspice_ran": ran,
        "vq_setup_critical": vq_setup_critical,
        "vq_hold_critical": vq_hold_critical,
        "n_setup_pts": len(setup_pts),
        "n_hold_pts": len(hold_pts),
        "setup_pts": [{"tsu_lead": t, "vq": v} for t, v in setup_pts],
        "hold_pts": [{"th_lag": t, "vq": v} for t, v in hold_pts],
    }
    with open(os.path.join(outdir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result


def main():
    if len(sys.argv) != 4:
        print("usage: char_gen.py <dff_netlist> <params.json> <out_dir>", file=sys.stderr)
        sys.exit(2)
    netlist = os.path.abspath(sys.argv[1])
    params = json.load(open(sys.argv[2]))
    outdir = os.path.abspath(sys.argv[3])
    res = characterize(netlist, params, outdir)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
