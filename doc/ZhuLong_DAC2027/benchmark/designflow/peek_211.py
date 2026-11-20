#!/usr/bin/env python3
"""Peek first real user text from cline messages.json - run on .75, parallel ssh to target hosts."""
import sys, json, subprocess, concurrent.futures

# targets: anchor<TAB>user<TAB>host
TARGETS = sys.argv[1]

def first_user_text(user, host, anchor):
    # Try subdirectory layout first: sessions/<anchor>/<anchor>.messages.json
    # then flat: sessions/<anchor>.messages.json
    paths = [
        "/home/%s/.cline/data/sessions/%s/%s.messages.json" % (user, anchor, anchor),
        "/home/%s/.cline/data/sessions/%s.messages.json" % (user, anchor),
    ]
    py_template = (
        "import json,sys\n"
        "paths=%r\n"
        "data=None;err=''\n"
        "for p in paths:\n"
        "  try:\n"
        "    f=open(p);data=json.load(f);f.close();break\n"
        "  except Exception as e:\n"
        "    err+=p+':'+str(e)+'; '\n"
        "if data is None:\n"
        "  print('NOFILE:'+err); sys.exit()\n"
        "for m in data:\n"
        "  if m.get('role')=='user' or m.get('type')=='user':\n"
        "    c=m.get('content','') or m.get('text','')\n"
        "    if isinstance(c,list):\n"
        "      c=' '.join(str(x.get('text','') if isinstance(x,dict) else x) for x in c)\n"
        "    c=str(c).strip()\n"
        "    if c and not c.startswith('<') and len(c)>5:\n"
        "      print(c[:800]); break\n"
    )
    py = py_template % (paths,)
    # write py to a temp file on target to avoid quoting hell
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "StrictHostKeyChecking=no",
           host, "python3 - <<'PYEOF'\n" + py + "\nPYEOF"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        out = (r.stdout or "").strip()
        if r.returncode == 0 and out:
            return out[:800]
        return "RC=%d ERR=%s" % (r.returncode, (r.stderr or "")[:200])
    except Exception as e:
        return "EXC:" + str(e)[:200]

jobs = []
with open(TARGETS) as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) < 3:
            continue
        anchor, user, host = parts[0], parts[1], parts[2]
        jobs.append((anchor, user, host))

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    fut = {ex.submit(first_user_text, u, h, a): (a, u, h) for (a, u, h) in jobs}
    for f in concurrent.futures.as_completed(fut, timeout=90):
        a, u, h = fut[f]
        try:
            results[(a, u, h)] = f.result()
        except Exception as e:
            results[(a, u, h)] = "FUT_EXC:" + str(e)[:200]

for (a, u, h), txt in sorted(results.items()):
    print("### %s\t%s\t%s" % (a, u, h))
    print(txt)
    print()
