#!/usr/bin/env python3
# shard D hfhds201 cron-blind-spot scan. Runs ON .75 (hfhds201) directly.
# Dumps D-domain candidate sessions (no exclusion filtering - done locally).
import os, re, json, sys, time

STRONG_D = re.compile(rb'(fsdb|waveview|verdi|wv_press|wv_set|sx_add_wave|sx_display|sx_new_wv|\.sw0|_wdf\b|subckt|\.cdl\b|\.spi\b|schEdit|geGetInstSet|abMatch|guardring|analogContext)', re.I)
SIM_KW = re.compile(rb'(\.measure|hspice|finesim|primesim|spectre|\.tran|\.dc\b|\.ac\b|\.sp\b|spice)', re.I)
WRONG = re.compile(rb'(\.v\b|verilog|systemverilog|sdc|sta\b|primetime|innovus|calibre|lvs\b|drc\b|svrf|pnr\b|floorplan|cts\b|router)', re.I)

SESS_ROOTS = []
for u in os.listdir('/home'):
    p = os.path.join('/home', u, '.cline/data/sessions')
    if os.path.isdir(p):
        SESS_ROOTS.append(p)

candidates = []
scanned = 0
for root in SESS_ROOTS:
    user = os.path.basename(os.path.dirname(os.path.dirname(root)))
    for entry in os.listdir(root):
        full = os.path.join(root, entry)
        msgfile = None
        sid = None
        if os.path.isdir(full):
            for f in os.listdir(full):
                if f.endswith('.messages.json'):
                    msgfile = os.path.join(full, f)
                    sid = f[:-len('.messages.json')]
                    break
        elif entry.endswith('.messages.json'):
            msgfile = full
            sid = entry[:-len('.messages.json')]
        if not msgfile: continue
        scanned += 1
        try:
            st = os.stat(msgfile)
            mtime = st.st_mtime
            if time.time() - mtime > 45*86400: continue
            with open(msgfile, 'rb') as fh:
                head = fh.read(8000)
            first_user = b''
            try:
                data = json.loads(head.decode('utf-8','replace'))
                msgs = data.get('messages', [])
                for m in msgs[:6]:
                    if m.get('role')=='user':
                        c = m.get('content')
                        if isinstance(c, list):
                            for blk in c:
                                if isinstance(blk,dict) and blk.get('type')=='text':
                                    first_user = blk.get('text','').encode('utf-8','replace')[:600]
                                    break
                        elif isinstance(c, str):
                            first_user = c.encode('utf-8','replace')[:600]
                        if first_user: break
            except Exception:
                first_user = head[:400]
            nstrong = len(STRONG_D.findall(head))
            nsim = len(SIM_KW.findall(head))
            nwrong = len(WRONG.findall(head))
            if nstrong > 0 or (nsim > 0 and nwrong == 0):
                candidates.append({'sid':sid,'user':user,'mtime':int(mtime),'strong':nstrong,'sim':nsim,'wrong':nwrong,'first_user':first_user.decode('utf-8','replace')[:400]})
        except Exception:
            pass

candidates.sort(key=lambda x: (x['strong'], x['sim'], -x['wrong']), reverse=True)
OUT = sys.argv[1] if len(sys.argv)>1 else 'D405_candidates.json'
json.dump({'scanned':scanned,'n_cand':len(candidates),'candidates':candidates[:60]}, open(OUT,'w'), ensure_ascii=False, indent=1)
print('scanned', scanned, 'sessions; D-domain candidates:', len(candidates), file=sys.stderr)
