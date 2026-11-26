#!/usr/bin/env python3
"""Peek first real user text from cline messages.json - run on .75, parallel ssh.
Strips <user_input mode="act">...</user_input> wrapper + <skill_instructions> blocks.
"""
import json, subprocess, concurrent.futures, re

TARGETS = [
  ("1791854550345_39z6e","lizwen","10.129.2.11"),
  ("1792488450622_kc85b","kevinc","10.129.2.13"),
  ("1790667716325_1f7f1","e0039503","10.129.32.83"),
  ("1791522635010_ikvky","clarawu","10.129.2.10"),
  ("1792583647014_50put","e0042337","10.129.32.190"),
  ("1789904654090_nzxx2","ziyuny","10.129.32.190"),
  ("1792983142511_kz3xd","zhililu","10.129.2.11"),
  ("1789889636409_cv1d2","ziyuny","10.129.32.190"),
  ("1788757855111_k34i5","xinqiaoz","10.129.2.13"),
  ("1790055622847_hhl2j","simplec","10.129.2.11"),
  ("1792372024585_wjj8v","ruminji","10.129.2.13"),
  ("1792023179795_wpxqf","e0042624","10.129.2.12"),
  ("1793000899273_uk649","yohannw","10.129.2.12"),
  ("1790229478830_bl77a","bensonh","10.129.8.236"),
  ("1792212480655_m3k7v","e0039602","10.129.8.136"),
  ("1790586188040_ud56w","cwei","10.129.33.27"),
  ("1783403844641_6lp9l","e0014566","10.129.2.10"),
  ("1791714944861_r8u7j","e0014566","10.129.2.10"),
  ("1791871990799_p5k61","lizwen","10.129.2.11"),
  ("1789460091466_4t4t5","sagequan","10.129.32.190"),
  ("1792049688397_r97bk","tongfanl","10.129.35.69"),
  ("1784077259904_98ha6","e0032903","10.129.8.86"),
  ("1788751406721_c385l","sophiaw","172.16.8.175"),
  ("1789106338537_v9zug","sophiaw","172.16.8.175"),
  ("1790558327260_3ks9d","rongjiez","10.129.2.11"),
  ("1789894171658_nclaf","steveny","10.129.2.11"),
  ("1790735750467_9wlpy","pdsong","10.129.8.104"),
  ("1791945162141_qo7xn","yansonw","10.129.33.234"),
  ("1789709270496_c9hdy","rongjiez","10.129.2.11"),
  ("1791442441803_cdf1w","e04201","10.129.2.13"),
  ("1792205299313_nvi22","chengk","10.129.35.121"),
  ("1792113930059_f7v4d","ruisongs","10.129.33.207"),
  ("1792497319115_a6f6r","jinsongl","10.129.33.139"),
  ("1791946116873_bs9rk","e0039503","10.129.32.83"),
  ("1791784036591_y9y0f","joeyl","10.129.2.13"),
  ("1792842218809_1yo6b","jkxu","10.129.32.83"),
  ("1791524223726_bgrlw","xrxiong","10.129.2.11"),
  ("1792113562815_feok1","adaml","10.129.2.10"),
  ("1791602750335_dtdfk","jason17w","10.129.32.190"),
  ("1790667366131_9qw70","cwei","10.129.33.27"),
  ("1784267301134_k3qx4","e0014566","10.129.2.10"),
  ("1791526393866_9n5th","devonma","10.129.32.84"),
  ("1789090361589_54h58","e0044455","10.129.2.13"),
  ("1793084065593_fg1kv","ghyang","10.129.2.12"),
  ("1793155140658_8ciyv","sherlock","10.129.2.11"),
  ("1792460001779_paosw","kaixuanx","10.129.2.10"),
  ("1791280343229_bp54q","mwxi","10.129.32.112"),
  ("1792478844725_i8070","chengk","10.129.35.121"),
  ("1790596559451_9p8g2","clwang","10.129.2.14"),
  ("1790230670440_jdjbi","sagequan","10.129.32.190"),
  ("1789979327643_ce2xm","devonma","10.129.32.84"),
  ("1790151429785_t5h84","yanxvwei","10.129.32.85"),
  ("1782784000943_pcb1x","e03179","10.129.2.11"),
  ("1793087790243_tosh6","colinxu","10.129.2.18"),
  ("1792497873290_0oabs","alanji","10.129.35.244"),
  ("1789901478183_k9dnd","kenwang","10.129.2.14"),
  ("1790039746600_vbr3y","steveny","10.129.2.11"),
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
