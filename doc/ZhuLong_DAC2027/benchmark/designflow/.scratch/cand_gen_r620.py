#!/usr/bin/env python3
# Generate D-domain candidates (mc>=10, D-keywords) sorted by mc desc, no exclusion.
import re
SUMMARY = "/home/t0002965/log/ssh_eda_search_20261113_131349/summary.tsv"
D_KW = re.compile(r'waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic', re.I)
def norm(s):
    s = re.sub(r'\.messages\.json$','',s)
    s = re.sub(r'\.messages\.archive$','',s)
    s = re.sub(r'\.json$','',s)
    return s
cands=[]
with open(SUMMARY) as f:
    f.readline()
    for line in f:
        parts=line.rstrip('\n').split('\t')
        if len(parts)<7: continue
        ip,host,user,session_file,match_count,keywords,tools=parts[:7]
        try: mc=int(match_count)
        except: continue
        if mc<10: continue
        if not D_KW.search(keywords): continue
        kw_tokens=[t for t in keywords.split(';') if t.strip()]
        d_mc=0; total_mc=0
        for t in kw_tokens:
            m=re.match(r'([a-zA-Z_]+):(\d+)',t)
            if m:
                total_mc+=int(m.group(2))
                if D_KW.search(m.group(1)): d_mc+=int(m.group(2))
        d_ratio=d_mc/total_mc if total_mc else 0
        cands.append((mc,d_ratio,norm(session_file),session_file,user,host,keywords))
cands.sort(key=lambda x:-x[0])
with open("cand_raw_D_r620.tsv","w") as out:
    out.write("mc\td_ratio\tanchor\tsession_file\tuser\thost\tkeywords\n")
    for c in cands:
        out.write("%d\t%.2f\t%s\t%s\t%s\t%s\t%s\n"%c)
print("total D mc>=10:",len(cands),"-> wrote cand_raw_D_r620.tsv")
