#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Park the 19 unfit peeked candidates from shard D #292 batch (rank 124-143)."""
import subprocess
import sys

# (sid, user, host, match_count, reason)
UNFIT = [
    ("1790500569237_451ou", "cwei", "10.129.33.27", 116, "skill-scenario: SpiceAgent skill prompt load, not a clean produce-task"),
    ("1789717410805_n5r98", "miccao", "10.129.32.47", 33, "skill-scenario: AutoCell TCL flow generator slash-command; wrong domain (layout/pnr)"),
    ("1792134251943_q9r9s", "lanxinz", "10.129.2.10", 118, "conditional produce (regenerate testbench IF syntax errors) needs real .sp; root-cause-leaning, deferred"),
    ("1788699263327_huf68", "rongjiez", "10.129.2.11", 460, "analysis/explain task (@runModelQA.pl perl code walkthrough), not produce; wrong domain"),
    ("1791969171304_w3eav", "zxtu", "10.129.2.11", 168, "U#0 how-to Q&A (bash args) + U#1 si.out warning analysis; not clean produce-task"),
    ("1789717909559_1v3yt", "miccao", "10.129.32.47", 135, "skill-scenario: AutoCell TCL flow generator slash-command; wrong domain"),
    ("1789731915060_hfm2o", "davidwu", "10.129.40.209", 99, "layout placement (aeAutoPlacementFromDesign floorplan); wrong domain for shard D"),
    ("1790042849968_vzne3", "miccao", "10.129.32.47", 203, "skill-scenario: AutoCell TCL flow generator slash-command; wrong domain"),
    ("1792373056714_2enpk", "jasonw", "10.129.2.13", 145, "U#0/Q&A (accessible dirs, sim dir location) + aging sim analysis; not clean produce-task"),
    ("1785896968029_vo4gm", "e0025768", "10.129.2.10", 113, "root-cause debug (optimize flow error diagnosis); user gives error symptom, not clean produce"),
    ("1789353120542_c21e8", "rongjiez", "10.129.2.11", 206, "Qt C++ config refactor (configloader/config.json); wrong domain (software, not EDA shard D)"),
    ("1789544452184_6pzrm", "rongjiez", "10.129.2.11", 207, "dup of c21e8 Qt C++ config refactor; wrong domain"),
    ("1789544515891_af6a0", "rongjiez", "10.129.2.11", 206, "dup of c21e8 Qt C++ config refactor; wrong domain"),
    ("1789544518757_at2ga", "rongjiez", "10.129.2.11", 206, "dup of c21e8 Qt C++ config refactor; wrong domain"),
    ("1792570696255_obhqj", "ypzheng", "10.129.2.12", 32, "U#0 sp file line-by-line analysis + U#1 token-balance Q&A; not clean produce-task"),
    ("1790150039431_ojny6", "sagequan", "10.129.32.190", 863, "skill-scenario: simdiag-cli remote HTTP diagnosis skill prompt; not a clean produce-task"),
    ("1790145346740_n1crk", "miccao", "10.129.32.47", 38, "skill-scenario: AutoCell TCL flow generator slash-command; wrong domain"),
    ("1789465514819_9f0ra", "shaoyou", "10.129.2.13", 28, "vague trigger (启动业务场景:仿真与验证) -> env overview Q&A; not a produce-task"),
    ("1789555682011_6j4hl", "pjli", "172.16.8.13", 105, "mid-conv: user pastes RunTrace signal edge trace-back output to continue debug; not a clean U#0 produce-task proposal"),
]

n = 0
for sid, user, host, mc, reason in UNFIT:
    r = subprocess.run(
        ["python3", "trace_ledger.py", "--shard", "D", "mark",
         "--session", sid, "--status", "parked", "--note", reason],
        capture_output=True, text=True,
    )
    ok = r.returncode == 0
    if not ok:
        # may already be parked; re-claim then mark
        subprocess.run(["python3", "trace_ledger.py", "--shard", "D", "claim",
                        "--session", sid, "--user", user, "--host", host,
                        "--match", str(mc), "--domain", "waveform"],
                       capture_output=True, text=True)
        r = subprocess.run(
            ["python3", "trace_ledger.py", "--shard", "D", "mark",
             "--session", sid, "--status", "parked", "--note", reason],
            capture_output=True, text=True,
        )
        ok = r.returncode == 0
    n += 1 if ok else 0
    print("%s %s" % ("OK " if ok else "ERR", sid))
print("parked %d/%d" % (n, len(UNFIT)))
