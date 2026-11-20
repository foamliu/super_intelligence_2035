#!/usr/bin/env python3
"""r462 A-dominant fresh candidate filter (mc>=10, 11/09 pool, 4-shard excl)."""
import re, sys, os

DESIGN = os.path.dirname(os.path.abspath(__file__))

def norm(sf):
    sf = sf.strip()
    sf = re.sub(r'\.messages\.json$', '', sf)
    sf = re.sub(r'\.json$', '', sf)
    return sf

# 4-shard exclusion (normalized session anchors)
USED = set()
for s in ['A','B','C','D']:
    p = os.path.join(DESIGN, f'trace_ledger_{s}.tsv')
    with open(p) as f:
        next(f)  # header
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if not parts or not parts[0]: continue
            USED.add(norm(parts[0]))
print(f'[excl] 4-shard normalized anchors: {len(USED)}', file=sys.stderr)

# A-domain keywords (token set, exact)
A_KW = {'verilog','systemverilog','rtl','sdc','vcs','verdi','dc_shell','synthesis',
        'synopsys','primetime','pt_shell','innovus','formality','yosys','vivado',
        'openroad','verilint','design_compiler','tcl','rc'}
B_KW = {'hspice','spice','cmos','analog','pex','waveview','netlist','transistor',
        '.cdl','finesim','eldo','spectre','smartspice','siliconsmart'}
C_KW = {'drc','calibre','aether','virtuoso','pdk','lvs','gds','cellview','schematic',
        'pyaether','dbopencv','skipper','cadence','.def','lib.defs'}
D_KW = set()  # not used for A dominance

def kw_count(field, kwset):
    # field is semicolon-separated tokens "token:count"
    cnt = 0
    for tok in field.split(';'):
        tok = tok.strip().lower()
        if not tok: continue
        name = tok.split(':')[0].strip()
        if name in kwset:
            try: cnt += int(tok.split(':')[1])
            except: cnt += 1
    return cnt

rows = []
with open(os.path.join(DESIGN, 'summary_1109.tsv')) as f:
    next(f)
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 7: continue
        ip, host, user, sf, mc, kws, tools = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
        try: mc = int(mc)
        except: continue
        if mc < 10: continue
        anchor = norm(sf)
        if anchor in USED: continue
        # A-keyword presence required
        if not any(k in kws.lower() for k in A_KW): continue
        a = kw_count(kws, A_KW)
        b = kw_count(kws, B_KW)
        c = kw_count(kws, C_KW)
        rows.append((mc, a, b, c, anchor, user, host, kws))

# A-dominant strict: a>2c and a>2b and a>=15
strict = [r for r in rows if r[1] > 2*r[3] and r[1] > 2*r[2] and r[1] >= 15]
# relaxed: a>c and a>b and a>=10
relaxed = [r for r in rows if r[1] > r[3] and r[1] > r[2] and r[1] >= 10 and r not in strict]

strict.sort(key=lambda r: (-r[1], -r[0]))
relaxed.sort(key=lambda r: (-r[1], -r[0]))

print(f'[filter] total A-keyword fresh: {len(rows)}', file=sys.stderr)
print(f'[filter] strict (a>2c,2b,a>=15): {len(strict)}', file=sys.stderr)
print(f'[filter] relaxed (a>c,b,a>=10): {len(relaxed)}', file=sys.stderr)

print('=== STRICT (top 25) ===')
for r in strict[:25]:
    print(f'{r[1]:5d} a  mc={r[0]:5d}  {r[4]}  user={r[5]} host={r[6]}  kw={r[7][:80]}')
print('=== RELAXED (top 25) ===')
for r in relaxed[:25]:
    print(f'{r[1]:5d} a  mc={r[0]:5d}  {r[4]}  user={r[5]} host={r[6]}  kw={r[7][:80]}')
