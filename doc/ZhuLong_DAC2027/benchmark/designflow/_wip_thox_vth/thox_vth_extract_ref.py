#!/usr/bin/env python3
"""thox_vth_extract.py -- Thick-oxide MOS Vth extractor + accept-check.

Reads a device-under-test netlist (dut.sp: a .model + .subckt dut d g s b) and a
spec (spec.json: sweep range, vds_lin, vds_sat, iref_per_wl, spec window), builds
two Id-VG testbenches (linear @ Vds=Vds_lin and saturation @ Vds=Vds_sat), runs
HSPICE, parses the .dc sweep tables, extracts Vth by two independent methods:

  vth_elr : linear extrapolation at peak gm in the linear-region curve, with the
            classic Vds/2 correction  (Vth = Vgs@maxgm - Id@maxgm/gm_max - Vds_lin/2)
  vth_cc  : constant-current interpolation in the saturation-region curve
            (Vgs at which Id_sat = iref_per_wl * (W/L))

Then compares both against the spec window and writes vth_report.json:
  { device, vth_elr, vth_cc, gm_max, id_at_vth_cc, accept (bool),
    accept_reasons (list of pass/fail strings), sweep, hspice_log_excerpt }

Usage: thox_vth_extract.py <dut.sp> <spec.json> <out_dir>
"""
import sys, os, re, json, subprocess, math

HSPICE = "hspice"

# ---- HSPICE .lis .dc table parsing -----------------------------------------
# Lines look like:
#   0.8000     0.800      7.179e-06
# (sweep_volt  v(g)   i(m1))  -- 3 float columns, 3rd in scientific notation
ROW_RE = re.compile(r'^\s*\d+\.\d+\s+\d+\.\d+\s+([0-9]\.\d+e[+-]\d+|[-+]?\d*\.?\d+[afpnumkg]?)\s*$')

def parse_num(s):
    s = s.strip()
    suf = {'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'k':1e3,'meg':1e6,'g':1e9,'t':1e12}
    m = re.match(r'^([+-]?[\d.]+)([afpnumkgt]*)$', s, re.I)
    if not m:
        return float(s)  # already scientific
    v = float(m.group(1)); u = m.group(2).lower()
    return v * suf.get(u, 1.0)

def parse_dc_table(lis_path):
    """Return list of (vgs, id) floats from the .dc transfer-curve block."""
    pairs = []
    in_block = False
    with open(lis_path, errors='ignore') as f:
        for line in f:
            if 'dc transfer curves' in line:
                in_block = True
                continue
            if in_block:
                if 'job concluded' in line or line.strip() == 'y':
                    break
                tok = line.split()
                # data rows have exactly 3 numeric tokens; first two are voltages, third is current
                if len(tok) == 3 and re.match(r'^[+-]?\d', tok[0]) and re.match(r'^[+-]?\d', tok[1]):
                    try:
                        vgs = float(tok[1]); idd = -parse_num(tok[2])  # i(vprobe)=-Id, negate to get +Id (NMOS)
                        pairs.append((vgs, idd))
                    except ValueError:
                        pass
    return pairs

# ---- Testbench generation ---------------------------------------------------
def read_dut(dut_sp):
    txt = open(dut_sp).read()
    # extract .model name + subckt pins + W/L
    m_model = re.search(r'\.model\s+(\S+)\s+(nmos|pmos)', txt, re.I)
    m_sub = re.search(r'\.subckt\s+dut\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$', txt, re.I | re.M)
    m_inst = re.search(r'(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+W\s*=\s*(\S+)\s+L\s*=\s*(\S+)', txt, re.I)
    if not (m_model and m_sub and m_inst):
        raise RuntimeError("cannot parse dut.sp: need .model <name> (n|p)mos, .subckt dut d g s b, and instance with W= L=")
    devtype = m_model.group(2).lower()
    pol = 1.0 if devtype == 'nmos' else -1.0
    return {
        'model_name': m_model.group(1),
        'pins': m_sub.groups(),
        'inst_model': m_inst.group(2),
        'W': m_inst.group(3),
        'L': m_inst.group(4),
        'raw': txt,
        'pol': pol,
    }

def wl_num(s):
    return float(re.sub(r'[uunp]', '', s, flags=re.I)) * {'u':1e-6,'n':1e-9,'p':1e-12}.get(re.search(r'([unp])',s,re.I).group(1).lower(),1.0) if re.search(r'([unp])', s, re.I) else float(s)

def build_tb(dut, spec, vds, tag):
    """Generate an Id-VG testbench netlist string."""
    vgs_start = spec['vgs_start']; vgs_stop = spec['vgs_stop']; vgs_step = spec['vgs_step']
    pol = dut['pol']
    # NMOS: drain at +Vds, sweep Vg 0->vdd. PMOS: drain at -Vds, sweep Vg 0->-vdd.
    vds_val = pol * vds
    vgs0 = 0.0
    sweep_stop = pol * vgs_stop
    sweep_start = pol * vgs_start
    # current probe: 0V vdc ammeter in drain path (i(vprobe) = -Id for NMOS)
    netlist = dut['raw'].rstrip() + "\n"
    netlist += f"* --- Id-VG testbench ({tag}) ---\n"
    netlist += "xdut d_int g 0 b dut\n"
    netlist += "vprobe d_int d 0\n"
    netlist += f"vdut d 0 {vds_val}\n"
    netlist += f"vg  g 0 {vgs0}\n"
    netlist += f"vb  b 0 0\n"
    netlist += f".dc vg {sweep_start} {sweep_stop} {vgs_step}\n"
    netlist += ".print dc v(g) i(vprobe)\n"
    netlist += f".option ingold=1 nomod post=0\n"
    netlist += f".end\n"
    return netlist

# ---- Vth extraction methods -------------------------------------------------
def extract_vth_elr(pairs, vds_lin, pol):
    """Linear extrapolation at peak gm with Vds/2 correction.
    pairs: (vgs, id) in linear region. Returns vth_elr (signed by pol)."""
    if len(pairs) < 4:
        return None
    # sort by vgs
    pairs = sorted(pairs, key=lambda p: p[0])
    vgs = [p[0]*pol for p in pairs]
    idd = [p[1]*pol for p in pairs]
    # numerical derivative gm = dId/dVgs
    gm = []
    for i in range(len(idd)):
        if i == 0:
            gm.append((idd[1]-idd[0])/(vgs[1]-vgs[0]))
        elif i == len(idd)-1:
            gm.append((idd[-1]-idd[-2])/(vgs[-1]-vgs[-2]))
        else:
            gm.append((idd[i+1]-idd[i-1])/(vgs[i+1]-vgs[i-1]))
    # find max gm index (skip points where gm<=0)
    max_i = -1; max_gm = -1.0
    for i,g in enumerate(gm):
        if g > max_gm:
            max_gm = g; max_i = i
    if max_i < 0 or max_gm <= 0:
        return None
    vgs_pk = vgs[max_i]; id_pk = idd[max_i]
    vth_raw = vgs_pk - id_pk/max_gm
    vth_elr = vth_raw - abs(vds_lin)/2.0   # classic linear-region ELR Vds/2 correction
    return vth_elr * pol

def extract_vth_cc(pairs, iref_total, pol):
    """Constant-current: Vgs at which Id = iref_total (interpolation)."""
    pairs = sorted(pairs, key=lambda p: p[0]*pol)
    vgs = [p[0]*pol for p in pairs]
    idd = [p[1]*pol for p in pairs]
    # find first crossing of iref_total
    for i in range(1, len(idd)):
        if (idd[i-1] - iref_total) * (idd[i] - iref_total) <= 0 and idd[i] != idd[i-1]:
            # linear interpolation
            frac = (iref_total - idd[i-1]) / (idd[i] - idd[i-1])
            vth_cc = vgs[i-1] + frac*(vgs[i]-vgs[i-1])
            return vth_cc * pol
    return None

# ---- main -------------------------------------------------------------------
def main():
    if len(sys.argv) != 4:
        print("usage: thox_vth_extract.py <dut.sp> <spec.json> <out_dir>", file=sys.stderr)
        sys.exit(2)
    dut_sp, spec_json, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    spec = json.load(open(spec_json))
    dut = read_dut(dut_sp)
    W = wl_num(dut['W']); L = wl_num(dut['L'])
    iref_total = spec['iref_per_wl'] * (W/L)
    report = {
        'device': dut['model_name'],
        'device_type': 'nmos' if dut['pol'] > 0 else 'pmos',
        'W': dut['W'], 'L': dut['L'],
        'wl_ratio': W/L,
        'iref_total': iref_total,
        'sweep': {k: spec[k] for k in ('vgs_start','vgs_stop','vgs_step','vds_lin','vds_sat','vdd')},
        'vth_elr': None, 'vth_cc': None, 'gm_max': None, 'id_at_vth_cc': None,
        'accept': False, 'accept_reasons': [],
        'hspice_log_excerpt': '',
    }
    # --- build & run linear TB ---
    tb_lin = build_tb(dut, spec, spec['vds_lin'], 'lin')
    sp_lin = os.path.abspath(os.path.join(out_dir, 'tb_lin.sp'))
    open(sp_lin, 'w').write(tb_lin)
    r1 = subprocess.run([HSPICE, '-i', sp_lin, '-o', os.path.abspath(os.path.join(out_dir,'tb_lin'))],
                        cwd=out_dir, capture_output=True, text=True, timeout=120)
    lis_lin = os.path.join(out_dir, 'tb_lin.lis')
    log = (r1.stdout + r1.stderr)[-800:]
    pairs_lin = parse_dc_table(lis_lin) if os.path.exists(lis_lin) else []
    report['hspice_log_excerpt'] = log[:600]
    # --- build & run saturation TB ---
    tb_sat = build_tb(dut, spec, spec['vds_sat'], 'sat')
    sp_sat = os.path.abspath(os.path.join(out_dir, 'tb_sat.sp'))
    open(sp_sat, 'w').write(tb_sat)
    r2 = subprocess.run([HSPICE, '-i', sp_sat, '-o', os.path.abspath(os.path.join(out_dir,'tb_sat'))],
                        cwd=out_dir, capture_output=True, text=True, timeout=120)
    lis_sat = os.path.join(out_dir, 'tb_sat.lis')
    pairs_sat = parse_dc_table(lis_sat) if os.path.exists(lis_sat) else []
    # --- extract ---
    vth_elr = extract_vth_elr(pairs_lin, spec['vds_lin'], dut['pol'])
    vth_cc  = extract_vth_cc(pairs_sat, iref_total, dut['pol'])
    # gm_max from linear curve
    gm_max = None
    if len(pairs_lin) >= 4:
        pp = sorted(pairs_lin, key=lambda p: p[0]*dut['pol'])
        vv = [p[0]*dut['pol'] for p in pp]; ii = [p[1]*dut['pol'] for p in pp]
        gms = [(ii[i+1]-ii[i])/(vv[i+1]-vv[i]) for i in range(len(ii)-1)]
        gms = [g for g in gms if g == g and g > 0]
        if gms: gm_max = max(gms)
    report['vth_elr'] = vth_elr
    report['vth_cc'] = vth_cc
    report['gm_max'] = gm_max
    # id at vth_cc (interpolate from sat curve)
    if vth_cc is not None and pairs_sat:
        pp = sorted(pairs_sat, key=lambda p: p[0]*dut['pol'])
        vv = [p[0]*dut['pol'] for p in pp]; ii = [p[1]*dut['pol'] for p in pp]
        tgt = vth_cc*dut['pol']
        for i in range(1,len(vv)):
            if (vv[i-1]-tgt)*(vv[i]-tgt) <= 0 and vv[i]!=vv[i-1]:
                frac=(tgt-vv[i-1])/(vv[i]-vv[i-1])
                report['id_at_vth_cc'] = (ii[i-1]+frac*(ii[i]-ii[i-1]))*dut['pol']
                break
    # --- accept check against spec window (signed, pol-aware) ---
    sw = spec['spec']
    reasons = []
    ok = True
    def in_window(val, lo, hi, name):
        nonlocal ok
        if val is None:
            reasons.append(f"{name}: NOT_EXTRACTED -> FAIL"); ok=False; return
        lo_s, hi_s = lo*dut['pol'], hi*dut['pol']   # spec given as magnitudes for NMOS/PMOS
        # treat spec window as |Vth| range; compare signed val against signed window
        if dut['pol'] > 0:
            lo_s, hi_s = lo, hi
        else:
            lo_s, hi_s = -hi, -lo
        if lo_s <= val <= hi_s:
            reasons.append(f"{name}: {val:.4f} in [{lo_s:.4f},{hi_s:.4f}] -> PASS")
        else:
            reasons.append(f"{name}: {val:.4f} NOT in [{lo_s:.4f},{hi_s:.4f}] -> FAIL"); ok=False
    in_window(vth_elr, sw['vth_elr_min'], sw['vth_elr_max'], 'vth_elr')
    in_window(vth_cc,  sw['vth_cc_min'],  sw['vth_cc_max'],  'vth_cc')
    # additional sanity: gm_max > 0 (device actually turned on)
    if gm_max is None or gm_max <= 0:
        reasons.append("gm_max: non-positive -> FAIL"); ok=False
    else:
        reasons.append(f"gm_max: {gm_max:.3e} > 0 -> PASS")
    report['accept'] = bool(ok)
    report['accept_reasons'] = reasons
    with open(os.path.join(out_dir, 'vth_report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
