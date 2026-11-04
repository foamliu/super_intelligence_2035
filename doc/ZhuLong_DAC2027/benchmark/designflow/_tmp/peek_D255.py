#!/usr/bin/env python3
"""Peek U#0 / first real user requirement for a list of (host, session_file) via .75 ssh.
Usage: peek_D253.py <tsv: host<TAB>session_file [host<TAB>session_file ...]>
"""
import json, subprocess, sys, os

def fetch_msgs(host, sessfile):
    # path on remote .75: /home/<user>/.cline/data/sessions/<sessfile_dir>/<sessfile>
    # sessfile like 1793081498316_qhzmr.messages.json -> dir = 1793081498316_qhzmr
    base = sessfile.replace('.messages.json','').replace('.messages.archive','.messages.json')
    # we don't know user; use ssh default identity, glob across /home/*/.cline/data/sessions/<base>/
    cmd = ['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',host,
           "for u in $(ls /home); do f=/home/$u/.cline/data/sessions/"+base+"/"+base+".messages.json; [ -f $f ] && echo $f && break; done </dev/null"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception as e:
        return None, f"ssh-err: {e}"
    path = r.stdout.strip().split('\n')[0] if r.stdout.strip() else None
    if not path:
        return None, f"no-session-file on {host}"
    # read first 200KB
    cmd2 = ['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',host,
            "head -c 200000 "+path+" </dev/null"]
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=20)
    if not r2.stdout:
        return None, f"empty-read {path}"
    try:
        d = json.loads(r2.stdout)
    except Exception as e:
        # try truncated; attempt to load just messages
        return None, f"json-parse-err {e}"
    msgs = d.get('messages', d if isinstance(d,list) else [])
    return msgs, f"ok n={len(msgs)}"

def first_real_user(msgs, n=3):
    out = []
    for m in msgs:
        if m.get('role') != 'user':
            continue
        c = m.get('content','')
        if isinstance(c, list):
            c = ' '.join(str(x.get('text','')) if isinstance(x,dict) else str(x) for x in c)
        c = str(c).strip()
        if not c:
            continue
        # skip policy-engine status / tool_result / cd / scene-launch boilerplate
        if c.startswith('{') and ('status' in c[:40] or 'tool_result' in c[:60] or 'content' in c[:40]):
            continue
        if c.startswith('<') and ('user_input' in c[:30] or 'environment' in c[:40] or 'user_profile' in c[:40]):
            # unwrap user_input
            import re
            mm = re.search(r'<user_input[^>]*>(.*?)</user_input>', c, re.S)
            if mm:
                c = mm.group(1).strip()
            else:
                continue
        if len(c) < 3:
            continue
        # skip pure command boilerplate
        low = c.lower()
        if low in ('hello','hi','hey','ok','okay','好的','嗯','在吗','你好') or low.startswith('/'):
            continue
        out.append(c[:500])
        if len(out) >= n:
            break
    return out

def main():
    args = sys.argv[1:]
    if not args:
        print("usage: peek_D253.py <tsv-file>  (cols: host<TAB>session_file)")
        sys.exit(1)
    tsv = args[0]
    with open(tsv) as f:
        rows = [l.rstrip('\n').split('\t') for l in f if l.strip()]
    for row in rows:
        host = row[0]; sess = row[1]
        mc = row[2] if len(row)>2 else ''
        msgs, st = fetch_msgs(host, sess)
        if msgs is None:
            print(f"### {sess} [{host}] mc={mc} :: {st}")
            continue
        fu = first_real_user(msgs, 2)
        print(f"### {sess} [{host}] mc={mc} :: {st}")
        for i,u in enumerate(fu):
            print(f"  U#{i}: {u}")
        print()

if __name__ == '__main__':
    main()
