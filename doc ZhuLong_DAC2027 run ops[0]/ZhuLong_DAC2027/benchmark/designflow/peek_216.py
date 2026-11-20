#!/usr/bin/env python3
"""Peek first real user text from cline messages.json - run on .75, parallel ssh."""
import json, subprocess, concurrent.futures

TARGETS = [
  ("1792827081154_d810y","jackjia","hfeg0plg78"),
  ("1788427145336_tk1gr","e0044979","hfeg0pkn001"),
  ("1793072434830_97mj2","chentong","hfeg0plg77"),
  ("1791973035805_dodbm","deniss","hfeg0plg87"),
  ("1791423204544_pewjz","johnl","hfeg0pfn119"),
  ("1791616524666_rgno0","e03179","hfeg0pkn002"),
  ("1792724728950_9z6bd","ruisongs","hfeg0pfn081"),
  ("1788249638562_0si6a","sophiaw","hfeg0plg09"),
  ("1787625155049_ovo6z","e0014566","hfeg0pkn001"),
  ("1792137927597_f4kc0","jackliu","hfhds209"),
  ("1792378687851_j8vf6","tongni","hfeg0pfn119"),
  ("1787728805982_txlfl","e0014566","hfeg0pkn001"),
  ("1786697763231_9rnwg","e0014566","hfeg0pkn001"),
  ("1789119944175_j56lm","davidwu","hfeg0pjn200"),
  ("1790078216880_4g0i9","lizwen","hfeg0pkn002"),
  ("1793002657891_l36g5","wei9liu","hfeg0plg53"),
  ("1792111736198_o3hc3","chengk","hfeg0pgn022"),
  ("1786071213100_05wcx","e0014566","hfeg0pkn001"),
  ("1783650805189_y20nc","e0014566","hfeg0pkn001"),
  ("1791463574990_um5we","xuebaok","hfhds206"),
  ("1792552457905_b4dlx","zjqiao","hfhds206"),
  ("1791858774096_1hq6h","rongjiez","hfeg0pkn002"),
]

def first_user_text(user, host, anchor):
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
        "      print(c[:600]); break\n"
    )
    py = py_template % (paths,)
    cmd = ["ssh","-o","BatchMode=yes","-o","ConnectTimeout=8","-o","StrictHostKeyChecking=no",
           host, "python3 - <<'PYEOF'\n"+py+"\nPYEOF"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        out = (r.stdout or "").strip()
        if r.returncode == 0 and out:
            return out[:600]
        return "RC=%d ERR=%s" % (r.returncode, (r.stderr or "")[:200])
    except Exception as e:
        return "EXC:" + str(e)[:200]

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    fut = {ex.submit(first_user_text, u, h, a): (a, u, h) for (a, u, h) in TARGETS}
    for f in concurrent.futures.as_completed(fut, timeout=120):
        a, u, h = fut[f]
        try:
            results[(a, u, h)] = f.result()
        except Exception as e:
            results[(a, u, h)] = "FUT_EXC:" + str(e)[:200]

for (a, u, h), txt in sorted(results.items()):
    print("### %s\t%s\t%s" % (a, u, h))
    print(txt)
    print()
