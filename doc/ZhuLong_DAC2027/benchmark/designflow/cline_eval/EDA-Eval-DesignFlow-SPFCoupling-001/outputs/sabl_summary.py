#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sabl_summary.py

Parse a StarRC DSPF 1.3 SPF coupling-capacitance file and emit a CSV summary
of the SABL (sense-amplifier bitline) coupling, one row per
(Sa_BLa<idx>, Sa_BLb<idx>) pair.

Usage:
    python3 sabl_summary.py <spf_file> <out_csv>

Only the Python standard library is used (no third-party dependencies).

Data model
----------
The SPF file groups couplings per net.  For each net there is a first line

    *|NET <net_name> <total>PF

followed by coupling lines

    <coupler_id> <net_name> <coupling_object> <value>

The last coupling line of a net block uses coupling_object "0" (ground /
power).  A blank line terminates the net block.  Header lines (*|..., .SUBCKT,
+ ..., .ENDS) are skipped.

SABL net names look like

    XI_msax256_cp00 . XI_CXSA_1x4_0<0> . Sa_BLa<0>
    <--- CP --->     <----- SA ------->   <- Sa_BL<bit>->

The "practice" CPs use a slightly different SA spelling without the angle
bracket, e.g.

    XI_msax196_pracL.XI_CXSA1x4_10.Sa_BLb<0>

Column layout (23 columns, no header row):
    1  row counter
    2  CP number
    3  SA sort number
    4  Sa_BLa<idx>
    5  Sa_BLa vs PreEq0
    6  Sa_BLa vs bl
    7  Sa_BLa vs IO
    8  Sa_BLa vs ION
    9  Sa_BLa vs Cslin
    10 Sa_BLa vs non-same-name Sa_BL
    11 Sa_BLa vs power
    12 Sa_BLa total
    13 Sa_BLb<idx>
    14 Sa_BLb vs PreEq0
    15 Sa_BLb vs bl
    16 Sa_BLb vs IO
    17 Sa_BLb vs ION
    18 Sa_BLb vs Cslin
    19 Sa_BLb vs non-same-name Sa_BL
    20 Sa_BLb vs power
    21 Sa_BLb total
    22 (empty)
    23 same-name Sa_BLa<idx> <-> Sa_BLb<idx> coupling

All coupling quantities are reported in farads.  The per-net total is stored
by the file in picofarads ("...PF") and is converted to farads here so the
total is consistent with the individual coupling values (which are already in
farads).

CP ordering: XI_msax196_pracL and XI_msax196_pracR come, in that order, right
after CP07.  Every other CP is ordered by its numeric cpNN index regardless of
the msax256 / msax260 block prefix.
"""

import sys
import re
import csv
from decimal import Decimal, InvalidOperation

# A hierarchical SABL net name:  CP . SA . Sa_BL<ab><idx>
SABL_RE = re.compile(r'^([^.]+)\.([^.]+)\.Sa_BL([ab])<(\d+)>$')
# Ordinal CP index for the "ordinary" CPs: XI_msax256_cp00, XI_msax260_cp08, ...
CP_RE = re.compile(r'^XI_msax\d+_cp(\d+)$')
# Bitline coupling object: cn09bla<34>, cn09blb<35>, ...
BL_RE = re.compile(r'cn\d+bl')
# Trailing <N> (msax256 / msax260 SA spelling)
SA_ANGLE_RE = re.compile(r'<(\d+)>$')
# Trailing _N (pracL / pracR SA spelling, e.g. XI_CXSA1x4_10)
SA_USCORE_RE = re.compile(r'_(\d+)$')


def sa_sort_num(sa):
    """Extract the numeric sort key from an SA cell name."""
    m = SA_ANGLE_RE.search(sa)
    if m:
        return int(m.group(1))
    m = SA_USCORE_RE.search(sa)
    if m:
        return int(m.group(1))
    return 0


def parse_sabl(name):
    """Split a SABL net name into (cp, sa, sa_num, ab, idx) or return None."""
    m = SABL_RE.match(name)
    if not m:
        return None
    cp, sa, ab = m.group(1), m.group(2), m.group(3)
    idx = int(m.group(4))
    return cp, sa, sa_sort_num(sa), ab, idx


def cp_sort_key(cp):
    """Sorting key for a CP name (pracL/pracR sit right after CP07)."""
    m = CP_RE.match(cp)
    if m:
        return (0, float(m.group(1)), cp)
    if cp == 'XI_msax196_pracL':
        return (0, 7.2, cp)
    if cp == 'XI_msax196_pracR':
        return (0, 7.3, cp)
    # unknown CP -> after all known CPs, stable by name
    return (1, 0.0, cp)


def _num(token):
    try:
        return Decimal(token)
    except InvalidOperation:
        return Decimal(0)


def parse_total(token):
    """'0.0006263PF' (picofarad) -> farad Decimal."""
    m = re.match(r'[+-]?\d*\.?\d+(?:[eE][+-]?\d+)?', token)
    if not m:
        return Decimal(0)
    return _num(m.group(0)) * Decimal('1e-12')


def classify(obj, partner_name):
    """Bucket a coupling object for a SABL net.

    Returns one of: power, same, other_sabl, preeq, bl, cslin, ion, io, other.
    """
    if obj == '0':
        return 'power'
    if parse_sabl(obj) is not None:
        return 'same' if obj == partner_name else 'other_sabl'
    if obj == 'PreEq0' or obj.endswith('.PreEq0'):
        return 'preeq'
    if BL_RE.search(obj):
        return 'bl'
    if obj.startswith('Cslin') or '.Cslin' in obj:
        return 'cslin'
    if 'IoN' in obj:
        return 'ion'
    if 'Yio' in obj:
        return 'io'
    return 'other'


def fmt(d):
    """Decimal -> clean lowercase scientific notation."""
    if d == 0:
        return "0"
    return format(d.normalize(), 'E').replace('E', 'e')


def parse_file(text):
    nets = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            cur = None
            continue
        if line.startswith('*'):
            if line.startswith('*|NET '):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    nets[name] = {'total': parse_total(parts[2]),
                                  'couplings': []}
                    cur = name
            continue
        if line.startswith('.') or line.startswith('+'):
            continue
        if cur is not None:
            parts = line.split()
            if len(parts) >= 4:
                nets[cur]['couplings'].append((parts[2], _num(parts[3])))
    return nets


def bucket_for(net_name, partner_name, nets):
    """Accumulate that net's coupling buckets; return (total, buckets, same)."""
    total = nets[net_name]['total']
    buckets = {'preeq': Decimal(0), 'bl': Decimal(0), 'io': Decimal(0),
               'ion': Decimal(0), 'cslin': Decimal(0), 'other_sabl': Decimal(0),
               'power': Decimal(0)}
    same = None
    for obj, val in nets[net_name]['couplings']:
        c = classify(obj, partner_name)
        if c == 'same':
            same = val
        elif c in buckets:
            buckets[c] += val
    return total, buckets, same


def main(argv):
    if len(argv) < 3:
        sys.stderr.write("Usage: python3 sabl_summary.py <spf_file> <out_csv>\n")
        return 2

    with open(argv[1], 'r', encoding='utf-8') as f:
        nets = parse_file(f.read())

    pairs = {}
    for name in nets:
        p = parse_sabl(name)
        if p is None:
            continue
        cp, sa, sa_num, ab, idx = p
        key = (cp, sa, idx)
        rec = pairs.setdefault(key, {'cp': cp, 'sa': sa, 'sa_num': sa_num,
                                     'idx': idx, 'a': None, 'b': None})
        rec[ab] = name

    rows = []
    for key, rec in pairs.items():
        if rec['a'] is None or rec['b'] is None:
            continue
        a_total, ba, same_a = bucket_for(rec['a'], rec['b'], nets)
        b_total, bb, same_b = bucket_for(rec['b'], rec['a'], nets)
        if same_a is not None:
            same = same_a
        elif same_b is not None:
            same = same_b
        else:
            same = Decimal(0)
        rows.append((rec, a_total, ba, b_total, bb, same))

    rows.sort(key=lambda r: (cp_sort_key(r[0]['cp']), r[0]['sa_num'],
                             r[0]['sa'], r[0]['idx']))

    out = []
    for i, (rec, a_total, ba, b_total, bb, same) in enumerate(rows, 1):
        idx = rec['idx']
        out.append([
            str(i),                       # 1 row counter
            rec['cp'],                    # 2 CP
            str(rec['sa_num']),           # 3 SA sort
            'Sa_BLa<%d>' % idx,           # 4
            fmt(ba['preeq']),             # 5
            fmt(ba['bl']),                # 6
            fmt(ba['io']),                # 7
            fmt(ba['ion']),               # 8
            fmt(ba['cslin']),             # 9
            fmt(ba['other_sabl']),        # 10
            fmt(ba['power']),             # 11
            fmt(a_total),                 # 12
            'Sa_BLb<%d>' % idx,           # 13
            fmt(bb['preeq']),             # 14
            fmt(bb['bl']),                # 15
            fmt(bb['io']),                # 16
            fmt(bb['ion']),               # 17
            fmt(bb['cslin']),             # 18
            fmt(bb['other_sabl']),        # 19
            fmt(bb['power']),             # 20
            fmt(b_total),                 # 21
            "",                           # 22 empty
            fmt(same),                    # 23 same-name coupling
        ])

    with open(argv[2], 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, lineterminator='\n').writerows(out)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))