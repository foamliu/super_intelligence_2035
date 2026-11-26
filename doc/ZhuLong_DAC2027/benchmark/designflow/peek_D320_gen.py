#!/usr/bin/env python3
"""Generic peek batch. Run ON .75. Reads targets from targets.tsv (sid\tuser\tip\tmc\thint).
Directory-based cline storage: /home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json
Extract user turns + assistant tool signal (editor + produce files) to triage A-faithful produce candidates.
"""
import json, subprocess, concurrent.futures, re, sys

def load_targets(path):
    out = []
    for line in open(path):
        line = line.rstrip('\n')
        if not line: continue
        parts = line.split('\t')
        if len(parts) < 4: continue
        sid, user, ip, mc = parts[0], parts[1], parts[2], parts[3]
        hint = parts[4] if len(parts) > 4 else ""
        try: mc_i = int(mc)
        except: mc_i = 0
        out.append((sid, user, ip, mc_i, hint))
    return out

TARGETS = load_targets(sys.argv[1] if len(sys.argv) > 1 else "targets.tsv")

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=6",ip,cmd],
            capture_output=True, text=True, timeout=t, stdin=subprocess.DEVNULL)
        return out.stdout, out.returncode
    except Exception:
        return "", 998

def extract_user_turns(raw):
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return []
    turns = []
    for m in msgs:
        if m.get("role") != "user":
            continue
        content = m.get("content"); texts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    texts.append(c.get("text", ""))
        elif isinstance(content, str):
            texts.append(content)
        for txt in texts:
            if txt.startswith("<user_input"):
                mm = re.search(r'<user_input mode="act">(.+?)</user_input>', txt, re.S)
                if mm: txt = mm.group(1)
            if txt.startswith("<skill_instructions>") or txt.startswith("<environment_details>") or txt.startswith("<attempt_completion"):
                continue
            s = txt.strip()
            if s and not s.startswith("<"):
                turns.append(s)
    return turns

def assistant_signal(raw):
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return 0, []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return 0, []
    nedit = 0
    produced = set()
    for m in msgs:
        if m.get("role") != "assistant":
            continue
        content = m.get("content")
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use":
                    name = c.get("name","")
                    inp = c.get("input", {})
                    if name in ("write_to_file","create_file","editor","apply_diff","insert_content","search_and_replace"):
                        nedit += 1
                        fp = inp.get("path") or inp.get("file") or inp.get("filePath") or ""
                        if fp:
                            produced.add(fp)
                    elif name in ("execute_command","run_command","run_commands","bash"):
                        cmd = inp.get("command","") or inp.get("cmd","")
                        for mm in re.finditer(r'>\s*([^\s|;&]+/\S+|[\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                        for mm in re.finditer(r'\b(?:cat|tee|cp|mv)\s+(?:>?>?\s*)?([\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                elif c.get("type") == "text":
                    txt = c.get("text","")
                    for mm in re.finditer(r'(?:write_to_file|create_file|editor).*?path[":=\s]+([^\s",}]+)', txt):
                        produced.add(mm.group(1))
    return nedit, sorted(produced)

def peek_one(t):
    sid, user, ip, mc, hint = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, mc, ["NO_FILE"], "?", 0, [])
    fpath = files[0]
    sz, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    out2, _ = sh(ip, "head -c 2000000 %s" % fpath, 90)
    turns = extract_user_turns(out2)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', out2, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    nedit, produced = assistant_signal(out2)
    return (sid, user, ip, mc, turns, sz.strip(), nedit, produced)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(peek_one, t): t for t in TARGETS}
        for fu in concurrent.futures.as_completed(futs):
            try:
                sid, user, ip, mc, turns, sz, nedit, produced = fu.result()
            except Exception as e:
                t = futs[fu]; sid, user, ip, mc, turns, sz, nedit, produced = t[0], t[1], t[2], t[3], ["EXC:"+str(e)], "?", 0, []
            print("### %s | %s@%s | mc=%s | size=%s | nturns=%d | nedit=%d | produced=%s" % (sid, user, ip, mc, sz, len(turns), nedit, produced))
            for i, tn in enumerate(turns[:6]):
                print("  [U#%d] %s" % (i, tn[:400].replace("\n", " ")))
            print("---")
