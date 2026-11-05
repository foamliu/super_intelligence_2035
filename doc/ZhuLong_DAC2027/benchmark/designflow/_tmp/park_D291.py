#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch-park the 19 unfit peeked sessions from shard D #291 peek batch."""
import subprocess, sys, os

parks = [
  ("1791958847728_7ycbz","joeyl","10.129.2.13","53","schematic_netlist","dup duty/skew avg measurement (3 dup sessions 7ycbz/4khqb/jesvi same U#0), not selected"),
  ("1791855758340_4khqb","joeyl","10.129.2.13","49","schematic_netlist","dup duty/skew (see 7ycbz), not selected"),
  ("1791867861982_jesvi","joeyl","10.129.2.13","49","schematic_netlist","dup duty/skew (see 7ycbz), not selected"),
  ("1787549214610_0muo8","sophiaw","172.16.8.175","61","analog_context","skill-scenario (启动业务场景 仿真与验证), not a produce-task"),
  ("1792478336435_qe1n4","t0002801","10.129.8.231","102","schematic_netlist","qualib TCL template gen for STD check - borderline domain (qualib not shard-D core), not selected"),
  ("1792573684287_demod","wenzhuod","10.129.34.20","102","schematic_netlist","ssh host key verification failed (NOFILE), unreachable"),
  ("1790229492123_m7hxu","cynthiaz","10.129.35.68","128","schematic_netlist","clean A-faithful produce (design double-tail slicer 2.9GHz) L2 schematic-gen, kept-note for future; not selected this round"),
  ("1788144579422_5cz37","e0014566","10.129.2.10","135","analog_context","layout autovia/powerfill cell removal - wrong domain (layout not shard-D core)"),
  ("1792045605929_rp1xk","e0029495","10.129.35.74","63","analog_context","Q&A (hspice .option for sensitive param sweep), no deliverable"),
  ("1792063193685_1vto1","e0023936","10.129.32.75","305","schematic_netlist","Q&A/inspection (who are you / current schematic), no produce-task"),
  ("1792120107352_t1b5d","wnyu","10.129.35.120","48","analog_context","context-summary continuation + user-gave-fix (减cascode级数), violates A-faithful rule"),
  ("1789870142807_4shph","yongk1li","10.129.2.12","108","schematic_netlist","software-eng (update totem_sc_signal_em Python GUI package), not EDA design flow"),
  ("1789090803347_bg5ws","oshen","10.129.32.46","41","schematic_netlist","skill-scenario (启动业务场景 DRC/LVS), not a produce-task"),
  ("1793069627641_n6ago","yanghao","10.129.2.11","46","schematic_netlist","NOFILE (session file not found on host)"),
  ("1790319450652_i4pp3","mike","10.129.32.80","107","schematic_netlist","analysis (帮我分析 ddr6_model dir) + mid-conv edits, not a clean produce-task"),
  ("1792400031626_1b13k","rongjiez","10.129.2.11","40","waveform","Q&A (how does waveview open stimulus.list), no deliverable"),
  ("1789699671032_sk6cg","joelchen","10.129.2.13","86","analog_context","DRC log analysis report (calibre_drc2.log), wrong domain (DRC not shard-D core) + analysis"),
  ("1793005134920_8bp0f","e03179","10.129.2.11","96","schematic_netlist","skill-scenario (vam-agent cosim cell recommend), not a produce-task"),
  ("1792387368762_qw7ae","tongni","10.129.33.245","69","schematic_netlist","skill-scenario (tran-sim-gen skill invoked), not a clean A-faithful task"),
]

base = [sys.executable, "designflow/trace_ledger.py", "--shard", "D", "mark",
        "--status", "parked"]
ok = 0
fail = 0
for p in parks:
    sid, user, host, mc, dom, note = p
    # ensure session is in ledger (claim first if needed) then mark parked
    cmd = base + ["--session", sid, "--note", note]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
    else:
        # session not in ledger -> claim then mark
        cc = [sys.executable, "designflow/trace_ledger.py", "--shard", "D", "claim",
              "--session", sid, "--user", user, "--host", host, "--match", mc, "--domain", dom]
        subprocess.run(cc, capture_output=True, text=True)
        r2 = subprocess.run(cmd, capture_output=True, text=True)
        if r2.returncode == 0:
            ok += 1
        else:
            fail += 1
            print("FAIL", sid, r2.stderr.strip()[:120])
print("parked ok=%d fail=%d / %d" % (ok, fail, len(parks)))
