import sys
ledger=set()
with open('designflow/_b_ledger_sids_tmp.txt') as f:
    for line in f:
        s=line.strip()
        if s: ledger.add(s)
print(f'ledger sids: {len(ledger)}')
cands=[]
with open('designflow/_b_cand_1120_strict.tsv') as f:
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        c=line.split('\t')
        if len(c)<7: continue
        mc,user,host,sf = int(c[0]),c[1],c[2],c[3]
        sid=sf
        for suf in ('.messages.json','.messages.archive','.json'):
            if sid.endswith(suf): sid=sid[:-len(suf)]
        cands.append((mc,user,host,sf,sid,c[4],c[5]))
print(f'candidates: {len(cands)}')
fresh=[c for c in cands if c[4] not in ledger]
taken=[c for c in cands if c[4] in ledger]
print(f'fresh={len(fresh)} taken={len(taken)}')
print('=== FRESH top 50 (mc desc) ===')
for mc,user,host,sf,sid,ss,ts in sorted(fresh,key=lambda x:-x[0])[:50]:
    print(f'{mc}\t{user}\t{host}\t{sid}\tspice={ss}/tot={ts}')
