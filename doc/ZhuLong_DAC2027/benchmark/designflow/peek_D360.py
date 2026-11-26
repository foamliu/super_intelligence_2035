#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow')
from peek_dirbased import peek_one
import concurrent.futures

TARGETS = [
    ("1789978168832_po6m1", "davidwu", "10.129.40.209"),    # mc204 aether/schematic/floorplan/calibre
    ("1790127432240_oh3te", "miccao", "10.129.32.47"),      # mc202 gds/netlist/calibre/cdl
    ("1791797822968_mxaca", "lizwen", "10.129.2.11"),       # mc201 aether/schematic/mixed-signal
    ("1792475021825_nn4my", "hongyuy", "10.129.8.102"),     # mc159 pdk/cmos/analog/calibre/transistor/waveview
    ("1792040490093_hi28t", "alanji", "10.129.35.244"),     # mc163 cadence/aether/netlist/analog
    ("1790151981511_hn72n", "oliverz", "10.129.40.209"),    # mc189 aether/virtuoso/pdk/techfile/netlist
]

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:7]):
            print("  [U#%d] %s" % (i, tn[:450].replace("\n", " ")))
        print("---")
