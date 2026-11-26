#!/usr/bin/env python3
"""Peek first real user text from cline messages.json - run on .75, parallel ssh.
Strips <user_input mode="act">...</user_input> wrapper + <skill_instructions> blocks.
"""
import json, subprocess, concurrent.futures, re

TARGETS = [
  ("1790660523598_1fxvk","rongtaoy","hfeg0pkn001"),
  ("1793072434830_97mj2","chentong","hfeg0plg77"),
  ("1793081107300_z1qdm","t0002224","hfeg0pkn004"),
  ("1793172510005_qa5p9","reedchen","hfeg0pkn004"),
  ("1792466303393_peuft","zxtu","hfeg0pkn002"),
  ("1792386804961_6tiy7","kaixuanx","hfeg0pkn001"),
  ("1791420858846_g3ud6","t0002801","hfeg0plg99"),
  ("1792487428780_fux9","e0029308","hfeg0pkn001"),
  ("1791858774096_1hq6h","rongjiez","hfeg0pkn002"),
  ("1790061417120_p2n1r","miccao","hfeg0plg37"),
  ("1792980238183_sh05n","shwanlai","hfeg0pgn016"),
  ("1792724728950_9z6bd","ruisongs","hfeg0pfn081"),
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
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
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
