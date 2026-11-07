#!/usr/bin/env python3
"""Peek #369 candidates: fresh D-domain (waveform/analog_context priority), not in ledger/deepread."""
import sys, os
sys.path.insert(0, '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow')
from peek_dirbased import peek_one
import concurrent.futures

# Top fresh candidates from candidates_mc30.tsv minus ledger/deepread dedup
# Priority: waveform (lowest coverage 44), then analog_context (45)
TARGETS = [
    # waveform (waveview-heavy, low mc but focused)
    ("1792460001779_paosw", "kaixuanx", "10.129.2.10"),   # mc31 waveview:260
    ("1792212480655_m3k7v", "e0039602", "10.129.8.136"),  # mc38 waveview:124 analog:41
    ("1793100948216_wzpd1", "colinxu", "10.129.2.18"),    # mc48 cellview:311 waveview:116
    ("1790558327260_3ks9d", "rongjiez", "10.129.2.11"),   # mc36 waveview:115
    ("1791445250037_2gxuy", "e0039122", "10.129.2.12"),   # mc47 pdk:92 waveview:36 hspice:20 netlist:24
    # analog_context (high-density analog/mosfet/opamp)
    ("1792223414540_erhym", "fhwang", "10.129.2.14"),     # mc50 mosfet:405 analog:400 calibre:190
    ("1792983142511_kz3xd", "zhililu", "10.129.2.11"),    # mc40 opamp:154 transistor:34
    ("1791945162141_qo7xn", "yansonw", "10.129.33.234"),  # mc35 hspice:100 netlist:74 .spi:10
]

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:8]):
            print("  [U#%d] %s" % (i, tn[:400].replace("\n", " ")))
        print("---")
