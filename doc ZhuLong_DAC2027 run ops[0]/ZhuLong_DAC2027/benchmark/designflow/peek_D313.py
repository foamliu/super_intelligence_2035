#!/usr/bin/env python3
"""Peek first real user text from cline messages.json - run on .75, parallel ssh.
Strips <user_input mode="act">...</user_input> wrapper + <skill_instructions> blocks.
"""
import json, subprocess, concurrent.futures, re

TARGETS = [
  ("1790490968281_6vy3t","mike","10.129.32.80"),
  ("1792223414540_erhym","fhwang","10.129.2.14"),
  ("1790314530475_4auih","pjli","172.16.8.13"),
  ("1790061769435_epctt","e0042337","10.129.32.190"),
  ("1792386923801_1lote","hongyuy","10.129.8.102"),
  ("1790578411744_brrc3","e0039602","10.129.8.136"),
  ("1792138312431_6i68m","e0042624","10.129.2.12"),
  ("1789708302199_on45q","bensonh","10.129.8.236"),
  ("1792981065381_vg3v4","yunfat","10.129.2.13"),
  ("1791354199272_3kgd5","rongjiez","10.129.2.11"),
  ("1793100948216_wzpd1","colinxu","10.129.2.18"),
  ("1793077423218_8nqgg","e03179","10.129.2.11"),
  ("1792380521540_xyw6o","hongyuy","10.129.8.102"),
  ("1788831007337_cmr7h","sagequan","10.129.32.190"),
  ("1792743512849_1nuuf","victorq","10.129.2.11"),
  ("1791782242441_8rxb1","steveny","10.129.2.11"),
  ("1791445250037_2gxuy","e0039122","10.129.2.12"),
  ("1790733563737_3qe6x","e0039602","10.129.8.136"),
  ("1790578434343_y6ito","binwenh","10.129.33.28"),
  ("1789647055494_9imo1","rongjiez","10.129.2.11"),
]

def first_user_text(user, host, anchor):
    paths = [
        "/home/%s/.cline/data/sessions/%s/%s.messages.json" % (user, anchor, anchor),
        "/home/%s/.cline/data/sessions/%s.messages.json" % (user, anchor),
    ]
    py_template = (
        "import json,sys,re\n"
        "paths=%r\n"
        "data=None;err=''\n"
        "for p in paths:\n"
        "  try:\n"
        "    f=open(p);data=json.load(f);f.close();break\n"
        "  except Exception as e:\n"
        "    err+=p+':'+str(e)+'; '\n"
        "if data is None:\n"
        "  print('NOFILE:'+err); sys.exit()\n"
        "msgs = data if isinstance(data,list) else data.get('messages', data if isinstance(data,dict) else [])\n"
        "if isinstance(msgs,dict): msgs=msgs.get('messages',[])\n"
        "for m in msgs:\n"
        "  if not isinstance(m,dict): continue\n"
        "  role=m.get('role') or m.get('type') or ''\n"
        "  if role not in ('user','user'): continue\n"
        "  c=m.get('content','') or m.get('text','')\n"
        "  if isinstance(c,list):\n"
        "    parts=[]\n"
        "    for x in c:\n"
        "      if isinstance(x,dict):\n"
        "        parts.append(str(x.get('text','') or x.get('content','') or ''))\n"
        "      else:\n"
        "        parts.append(str(x))\n"
        "    c=' '.join(parts)\n"
        "  c=str(c).strip()\n"
        "  # strip <skill_instructions>...</skill_instructions> blocks\n"
        "  c=re.sub(r'<skill_instructions>.*?</skill_instructions>','',c,flags=re.S)\n"
        "  # strip <user_input ...>...</user_input> wrapper, keep inner\n"
        "  m2=re.search(r'<user_input[^>]*>(.*?)</user_input>',c,flags=re.S)\n"
        "  if m2: c=m2.group(1).strip()\n"
        "  # strip remaining xml-ish tags\n"
        "  c=re.sub(r'<[^>]+>','',c).strip()\n"
        "  if c and len(c)>5 and not c.startswith('Cline tried to') and not c.startswith('[\') :#'):\n"
        "    print(c[:700]); break\n"
    )
    py = py_template % (paths,)
    cmd = ["ssh","-o","BatchMode=yes","-o","ConnectTimeout=8","-o","StrictHostKeyChecking=no",
           host, "python3 - <<'PYEOF'\n"+py+"\nPYEOF"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25, stdin=subprocess.DEVNULL)
        out = (r.stdout or "").strip()
        if r.returncode == 0 and out:
            return out[:700]
        return "RC=%d ERR=%s" % (r.returncode, (r.stderr or "")[:200])
    except Exception as e:
        return "EXC:" + str(e)[:200]

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
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
