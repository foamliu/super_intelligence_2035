import re
REACHABLE = {"10.129.32.47","10.129.32.75","10.129.32.189","10.129.32.190","10.129.32.204","10.129.32.46","10.129.32.100","10.129.32.112","10.129.32.114","10.129.32.234","10.129.33.234"}
ledger_sids = set()
with open("designflow/trace_ledger_D.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if not parts: continue
        sid = re.sub(r'\.messages\.json$','',parts[0])
        sid = re.sub(r'\.messages\.archive\.json$','',sid)
        sid = re.sub(r'\.json$','',sid)
        ledger_sids.add(sid)
cands = {}
with open("designflow/_tmp/candidates_D_all2.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5: continue
        mc = int(parts[0]); sid = parts[1]; user = parts[2]; host = parts[3]; ip = parts[4]
        sid_clean = re.sub(r'\.messages\.json$','',sid)
        sid_clean = re.sub(r'\.messages\.archive\.json$','',sid_clean)
        sid_clean = re.sub(r'\.json$','',sid_clean)
        if sid_clean in ledger_sids: continue
        if sid_clean in cands: continue
        cands[sid_clean] = (mc, user, host, ip, parts[5] if len(parts)>5 else "")
reach = [(sid,)+v for sid,v in cands.items() if v[3] in REACHABLE]
reach.sort(key=lambda x:-x[1])
print("=== fresh on REACHABLE hosts:", len(reach), "===")
for sid,mc,user,host,ip,tools in reach[:60]:
    print(f"{mc}\t{sid}\t{user}\t{host}\t{ip}\t{tools[:80]}")
