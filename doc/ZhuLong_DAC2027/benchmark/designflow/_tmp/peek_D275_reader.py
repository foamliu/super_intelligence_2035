import sys, os, json, re
sid, user = sys.argv[1], sys.argv[2]
base = "/home/%s/.cline/data/sessions/%s/%s" % (user, sid, sid)
path = None
for cand in (base + ".messages.json", base + ".messages.archive.json", base + ".json"):
    if os.path.exists(cand):
        path = cand
        break
if not path:
    print("NOFILE")
    sys.exit(0)
is_jsonl = path.endswith(".archive.json")
msgs = []
if is_jsonl:
    with open(path, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msgs.append(json.loads(line))
            except Exception:
                pass
else:
    try:
        with open(path, "r", errors="replace") as f:
            d = json.load(f)
        if isinstance(d, dict):
            msgs = d.get("messages", [])
        elif isinstance(d, list):
            msgs = d
    except Exception as e:
        print("ERR json.load: %s" % e)
        sys.exit(0)
if not msgs:
    print("EMPTY n=0")
    sys.exit(0)
n = len(msgs)
ui_re = re.compile(r"<user_input[^>]*>(.*?)</user_input>", re.S)
def extract_text(m):
    c = m.get("content") if isinstance(m, dict) else None
    if c is None:
        return ""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for it in c:
            if isinstance(it, dict):
                if it.get("type") == "text":
                    out.append(it.get("text", ""))
                elif "text" in it:
                    out.append(str(it["text"]))
            else:
                out.append(str(it))
        return "".join(out)
    return str(c)
user_turns = []
for m in msgs:
    if not isinstance(m, dict):
        continue
    role = m.get("role", "")
    if role != "user":
        continue
    txt = extract_text(m)
    if not txt:
        continue
    # skip tool_result-only messages
    if txt.strip().startswith("<") and "tool_result" in txt[:200]:
        continue
    mm = ui_re.search(txt)
    if mm:
        txt = mm.group(1)
    txt = txt.strip()
    if not txt:
        continue
    # skip pure tool_result fragments
    if txt.startswith("[Request interrupted") or txt.startswith("Cline"):
        continue
    user_turns.append(txt)
out = ["N=%d" % n]
for i, t in enumerate(user_turns[:6]):
    t = re.sub(r"\s+", " ", t)
    if len(t) > 600:
        t = t[:600] + "..."
    out.append("U#%d: %s" % (i, t))
print("\n".join(out))
