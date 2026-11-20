#!/usr/bin/env python3
# r860: scan latest .75 scan summary for fresh (not-ledgered) mc>=10 C-domain candidates.
# Usage on .75: python3 _fresh_mc10_scan_C_r860.py [summary.tsv] [ledger_sids.txt]
# ledger_sids.txt = all 4-shard ledger session bases (one per line) to exclude.
# If ledger_sids.txt not given, just prints top dedup C cands (no exclusion).
import re, sys
SUM = sys.argv[1] if len(sys.argv) > 1 else "/home/t0002965/log/ssh_eda_search_20261120_145529/summary.tsv"
LEDGER = sys.argv[2] if len(sys.argv) > 2 else None
cre = re.compile(r'(calibre|drc|lvs|aether|layout|virtuoso|pex|gdsii|skill|pyaether)', re.I)
TAB = chr(9)
ledger = set()
if LEDGER:
    for L in open(LEDGER):
        s = L.strip()
        if s:
            ledger.add(re.sub(r'[.]messages.*$', '', s))
seen = set(); cands = []
for L in open(SUM):
    parts = L.rstrip(chr(10)).split(TAB)
    if len(parts) < 6 or parts[0] == 'ip':
        continue
    ip, host, user, sess, mc, kw = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
    try:
        mci = int(mc)
    except Exception:
        continue
    if mci < 10:
        continue
    if not cre.search(kw):
        continue
    base = re.sub(r'[.]messages.*$', '', sess)
    if base in seen:
        continue
    seen.add(base)
    if base in ledger:
        continue
    kws = {}
    for tok in kw.split(';'):
        tok = tok.strip()
        if not tok:
            continue
        m = re.match(r'(.*?):([0-9]+)', tok)
        if m:
            kws[m.group(1)] = int(m.group(2))
    verilog = kws.get('verilog', 0) + kws.get('rtl', 0) + kws.get('systemverilog', 0)
    ccore = (kws.get('drc', 0) + kws.get('calibre', 0) + kws.get('lvs', 0) + kws.get('aether', 0)
             + kws.get('virtuoso', 0) + kws.get('pex', 0) + kws.get('pyaether', 0)
             + kws.get('layout', 0) + kws.get('gdsii', 0))
    if ccore < verilog:
        continue
    cands.append((mci, ccore, verilog, user, host, ip, base, kw))
cands.sort(reverse=True)
print("FRESH_C_CANDS", len(cands), "(ledger_excluded=" + str(len(ledger)) + ")")
for c in cands[:50]:
    print(chr(9).join([c[6], c[3], c[4], c[5], str(c[0]), str(c[2]), c[7][:120]]))
