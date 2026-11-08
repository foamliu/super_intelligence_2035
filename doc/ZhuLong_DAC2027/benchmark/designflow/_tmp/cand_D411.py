import sys
EXCL=set()
with open('all_shard_sids_r411.txt') as f:
    for line in f:
        s=line.strip()
        if s: EXCL.add(s)
# D-domain keywords (shard D = netlist_wave: analog_context/schematic_netlist/waveform)
DKW=set('waveview cosmos skill netlist spiros spectrum analog schematic transistor mosfet spice hspice finesim primo xyce silver aether virtuoso calibre lvs drc erc cdl spf verilogA verilog-a sdt schmatic schematic'.split())
def parse_kw(s):
    d={}
    for pair in s.split(';'):
        if not pair.strip(): continue
        if ':' not in pair: continue
        k,v=pair.rsplit(':',1)
        k=k.strip().lower()
        try: c=int(v)
        except: continue
        if k: d[k]=d.get(k,0)+c
    return d
rows=[]
seen=set()
with open('/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv') as f:
    f.readline()
    for line in f:
        p=line.rstrip('\n').split('\t')
        if len(p)<7: continue
        mc=p[4]; session=p[3].replace('.messages.json','').replace('.messages.archive.json',''); user=p[2]; host=p[1]; kw6=p[5]; tools=p[6]
        try: mcn=int(mc)
        except: continue
        if mcn<15: continue
        if session in EXCL: continue
        if session in seen: continue
        seen.add(session)
        d=parse_kw(kw6)
        polluted = d.get('systemverilog',0)>=1000
        if polluted:
            d.pop('systemverilog',None)
            if d.get('verilog',0)>=150: d.pop('verilog',None)
        if not d: continue
        total=sum(d.values())
        if total==0: continue
        d_total=sum(c for k,c in d.items() if k in DKW)
        d_share=d_total/total
        top_kw=max(d.items(),key=lambda x:x[1])[0]
        # D-domain: top keyword in DKW OR D-share >= 0.4
        if top_kw not in DKW and d_share<0.4: continue
        rows.append((mcn,session,user,host,kw6,tools,d_share,top_kw))
rows.sort(key=lambda x:-x[0])
print('TOTAL_FRESH_D',len(rows))
for r in rows[:20]:
    print('%d\t%s\t%s\t%s\td_share=%.2f top=%s | kw6=%s'%(r[0],r[1],r[2],r[3],r[6],r[7],r[4][:100]))
