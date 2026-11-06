import csv, sys

# ledger anchors
anchors = set()
with open('designflow/trace_ledger_B.tsv') as f:
    r = csv.reader(f, delimiter='\t')
    header = next(r)
    for row in r:
        if not row: continue
        s = row[0]
        for suf in ['.messages.json', '.messages.archive.json', '.json']:
            if s.endswith(suf):
                s = s[:-len(suf)]
                break
        anchors.add(s)

print(f"ledger anchors: {len(anchors)}", file=sys.stderr)

# parse candidates, dedupe by normalized session
cands_text = open('designflow/_cands_1105.tsv').read()
lines = cands_text.strip().split('\n')
seen_sess = set()
fresh = []
for line in lines[1:]:
    cols = line.split('\t')
    if len(cols) < 9: continue
    ip, host, user, session_file, mc, spice_cnt, tool_total, spice_ratio, tools = cols[:9]
    s = session_file
    for suf in ['.messages.json', '.messages.archive.json', '.json']:
        if s.endswith(suf):
            s = s[:-len(suf)]
            break
    if s in anchors or s in seen_sess:
        continue
    seen_sess.add(s)
    fresh.append((int(mc), float(spice_ratio), user, host, session_file, ip, tools, int(spice_cnt), int(tool_total)))

fresh.sort(key=lambda x: -x[0])
print(f"fresh candidates: {len(fresh)}")
print(f"{'mc':>5} {'ratio':>6} {'user':<12} {'host':<14} {'session_file':<48} {'spice/total':>11} tools")
for mc, ratio, user, host, sf, ip, tools, sc, tt in fresh[:30]:
    print(f"{mc:>5} {ratio:>6} {user:<12} {host:<14} {sf:<48} {sc:>5}/{tt:<5} {tools[:55]}")
