#!/usr/bin/env python3
import sys

anchors = [l.strip() for l in open('designflow/_ledgered_C_bare.txt') if l.strip()]
regex = '|'.join(anchors)

body = r'''  sub(/\.messages\.json$/,"",$4);
  if ($4 !~ /^EXCREGEX$/ && $3 != "ruifan") {
    kw=$7;
    lay=0; sim=0;
    if (kw ~ /calibre/) lay+=1;
    if (kw ~ /virtuoso/) lay+=1;
    if (kw ~ /aether/) lay+=1;
    if (kw ~ /cellview/) lay+=1;
    if (kw ~ /dbGet/) lay+=1;
    if (kw ~ /dbCreateInst/) lay+=1;
    if (kw ~ /dbCreateRect/) lay+=1;
    if (kw ~ /pcell/) lay+=1;
    if (kw ~ /layout/) lay+=1;
    if (kw ~ /innovus/) lay+=1;
    if (kw ~ /pyAether/) lay+=1;
    if (kw ~ /pex/) lay+=1;
    if (kw ~ /netlist/) sim+=1;
    if (kw ~ /hspice/) sim+=1;
    if (kw ~ /schematic/) sim+=1;
    if (kw ~ /synthesis/) sim+=1;
    if (kw ~ /spectre/) sim+=1;
    if (kw ~ /finesim/) sim+=1;
    if (kw ~ /primesim/) sim+=1;
    if (kw ~ /fsdb/) sim+=1;
    if (kw ~ /verdi/) sim+=1;
    if (kw ~ /waveview/) sim+=1;
    if (kw ~ /ncsim/) sim+=1;
    score = lay - 0.6*sim;
    if (lay>=2 && (kw ~ /calibre/ || kw ~ /virtuoso/ || kw ~ /aether/ || kw ~ /ipcustom/ || kw ~ /layout/ || kw ~ /pex/))
      printf "%d\t%d\t%s\t%s\t%s\t%s\n", score, $5, $4, $3, $2, kw;
  }
'''.replace('EXCREGEX', regex)

awk_cmd = "awk -F'\\t' 'NR>1 && $5+0>=30 {" + body + "}' /home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv | sort -rn | head -30"

with open('designflow/_scan_r296.awk.sh', 'w') as f:
    f.write(awk_cmd + '\n')

print("wrote designflow/_scan_r296.awk.sh", len(awk_cmd), "bytes")
