#!/usr/bin/env python3
"""r493 v2: A-domain-PRIMARY fresh candidates (A-tools dominate, not C/D/B).

Counts keyword hits per domain and requires A > C, A > D, A > B (like r490
cand_query2.py logic) to exclude C-domain drc/pdk/calibre bleed-through.
"""
import re, sys, os

BENCH = os.path.dirname(os.path.abspath(__file__))

A_KW = {'verdi','vcs','dc_shell','verilint','formality','innovus','primetime',
        'design_compiler','rc','pt_shell','synthesis','synopsys','tcl','verilog',
        'systemverilog','rtl','sdc','vivado','yosys','openroad'}
B_KW = {'hspice','finesim','siliconsmart','spectre','ngspice','simulator','spice','custom_sim'}
C_KW = {'calibre','virtuoso','aether','ipcustom','layout','lvs','drc','pexivirtuoso',
        'pdk','pex','gdsii','.gds','.def','techfile','dbcreaterect','dbcreatepolygon',
        'dbcreatepath','dbopencellviewbytype','dbopencv','dbget','ddgetobj','cellview',
        'schematic','floorplan','lib.defs'}
D_KW = {'waveview','cosmos','skill','netlist','spiros','spectrum','analog','schematic',
        '.cdl','cmos','transistor','opamp'}

def count_domain(kw_field, domain_set):
    cnt = 0
    for part in kw_field.split(';'):
        part = part.strip().rstrip(':')
        if not part: continue
        name = part.split(':')[0].strip().lstrip('.')
        if name in domain_set:
            try: cnt += int(part.split(':')[1])
            except: pass
    return cnt

def short_sid(sf):
    s = re.sub(r'\.messages\.json$','',sf)
    s = re.sub(r'\.json$','',s)
    m = re.match(r'^\d+_([a-z0-9]+)$', s)
    return m.group(1) if m else s

# exclusion from 4 shard ledgers (full sid + short)
excl_full, excl_short = set(), set()
for sh in ['A','B','C','D']:
    p = os.path.join(BENCH, f'trace_ledger_{sh}.tsv')
    if not os.path.exists(p): continue
    with open(p) as f:
        for line in f:
            line = line.rstrip('\n')
            if not line: continue
            sid = line.split('\t')[0]
            excl_full.add(sid)
            excl_short.add(short_sid(sid))
sys.stderr.write(f"exclusion: full={len(excl_full)} short={len(excl_short)}\n")

summary = os.path.join(BENCH, 'summary_1113.tsv')
rows, seen = [], set()
with open(summary) as f:
    f.readline()
    for line in f:
        line = line.rstrip('\n')
        if not line: continue
        c = line.split('\t')
        if len(c) < 6: continue
        ip, host, user, sf, mc, kw = c[0],c[1],c[2],c[3],c[4],c[5]
        try: mcn = int(mc)
        except: continue
        if mcn < 10: continue
        sid = re.sub(r'\.messages\.json$','',sf); sid = re.sub(r'\.json$','',sid)
        if sid in seen: continue
        seen.add(sid)
        if sid in excl_full or short_sid(sid) in excl_short: continue
        a = count_domain(kw, A_KW)
        b = count_domain(kw, B_KW)
        cc = count_domain(kw, C_KW)
        d = count_domain(kw, D_KW)
        total = a+b+cc+d
        if total == 0: continue
        # A-domain-primary: A dominant over each of C, D, B
        if not (a > cc and a > d and a > b): continue
        if a < 50: continue  # need meaningful A presence
        rows.append((mcn, sid, user, host, a, cc, d, b, kw))

rows.sort(key=lambda r:-r[0])
sys.stderr.write(f"A-domain-primary mc>=10 a>=50 fresh: {len(rows)}\n")
print("# r493 v2: A-domain-PRIMARY fresh (a>cc, a>d, a>b, a>=50), not in 4-shard ledger")
print("# mc<TAB>sid<TAB>user<TAB>host<TAB>A<TAB>C<TAB>D<TAB>B<TAB>keywords")
for r in rows:
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}\t{r[6]}\t{r[7]}\t{r[8]}")
