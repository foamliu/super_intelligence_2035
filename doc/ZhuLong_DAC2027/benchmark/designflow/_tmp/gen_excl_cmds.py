sids = [l.strip() for l in open('designflow/_tmp/excl_all.txt') if l.strip()]
sids = sorted(set(sids))
print('NSIDS', len(sids))
chunk = 80
cmds = []
for i in range(0, len(sids), chunk):
    batch = sids[i:i+chunk]
    args = ' '.join(batch)
    if i == 0:
        cmd = "printf '%s\\n' " + args + " > excl.txt"
    else:
        cmd = "printf '%s\\n' " + args + " >> excl.txt"
    cmds.append(cmd)
import json
open('designflow/_tmp/excl_cmds.json', 'w').write(json.dumps(cmds))
open('designflow/_tmp/excl_cmds.txt', 'w').write('\n'.join(cmds))
print('NCMDS', len(cmds))
print('MAXLEN', max(len(c) for c in cmds))
