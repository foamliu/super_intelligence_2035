#!/usr/bin/env python3
import json, re, sys, os
EXCL = set(json.load(open(os.path.join(os.path.dirname(__file__), '_exclude_A_list.json'))))

# Real digital-front-end tools (in $7 tools column) - strong signal
REAL_DIGITAL_TOOLS = re.compile(r'vcs|verdi|dc_shell|formality|verilint|innovus|primetime|pt_shell|design_compiler|vivado|yosys|openroad|verdi|irun|xrun|ncsim|questasim|vcs_sim')
# Digital keywords (in $6 keywords column) - medium signal
DIGITAL_KW = re.compile(r'systemverilog|verilog|sdc|rtl|upf|tcl|synopsys|formality|verilint|dc_shell|vcs|verdi|primetime|pt_shell|innovus|design_compiler|vivado|yosys|openroad|uvm|svtest|sva|assertion|dft|sta|cppm|rcmax|cdc|rdc')
# Analog/spice keywords - negative signal (these mean analog schematic, not digital)
ANALOG_KW = re.compile(r'hspice|spectre|calibre|virtuoso|schematic|layout|spice|cdl|lvs|drc|erc|pex|rcx|aether|pyAether|cellview|pdk|gm|idl|mosaic|oi|op|pvt')

rows = []
with open('/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv') as f:
    next(f)
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 7: continue
        mc, sess, user, host, kw, tools = parts[4], parts[3].replace('.messages.json',''), parts[2], parts[1], parts[5], parts[6]
        try: mcn = int(mc)
        except: continue
        if mcn < 15: continue
        if sess in EXCL: continue
        # parse keyword counts from $6: "systemverilog:1776;verilog:166;..."
        dig_count = 0
        ana_count = 0
        for token in kw.split(';'):
            token = token.strip()
            if not token: continue
            name = token.split(':')[0].strip().lower()
            cnt = 0
            try: cnt = int(token.split(':')[1])
            except: pass
            if DIGITAL_KW.search(name): dig_count += cnt
            if ANALOG_KW.search(name): ana_count += cnt
        has_real_digital = bool(REAL_DIGITAL_TOOLS.search(tools.lower()))
        # Score: must have some digital keyword presence; prefer real digital tools + digital dominance
        if dig_count == 0 and not has_real_digital: continue
        # Require digital dominance OR real digital tool
        total = dig_count + ana_count
        if total > 0:
            dig_ratio = dig_count / total
        else:
            dig_ratio = 0
        if not has_real_digital and dig_ratio < 0.5: continue
        # score: real digital tool gives boost, then mc, then dig_ratio
        score = (10000 if has_real_digital else 0) + mcn + int(dig_ratio * 100)
        rows.append((score, mcn, sess, user, host, has_real_digital, dig_count, ana_count, kw[:80], tools[:80]))

rows.sort(key=lambda r: -r[0])
print(f"# total digital-leaning candidates: {len(rows)}")
for r in rows[:15]:
    print('\t'.join(str(x) for x in r))
