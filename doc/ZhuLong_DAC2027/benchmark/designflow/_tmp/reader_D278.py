import sys, os, json, glob

def find_session(sid, user):
    base = "/home/%s/.cline/data/sessions" % user
    cands = []
    if os.path.isdir(base):
        for d in os.listdir(base):
            dp = os.path.join(base, d)
            if sid in d and os.path.isdir(dp):
                for f in os.listdir(dp):
                    if f.endswith(".json") or f.endswith("archive.json"):
                        cands.append(os.path.join(dp, f))
    # also direct
    cands += glob.glob("/home/%s/.cline/data/sessions/*%s*/*.json" % (user, sid))
    cands = list(set(cands))
    # prefer .messages.json over archive
    cands.sort(key=lambda p: (0 if "messages.json" in p and "archive" not in p else 1, -os.path.getsize(p)))
    return cands

def extract_user_turns(path, max_turns=6, max_chars=600):
    turns = []
    try:
        with open(path, "r", errors="replace") as f:
            data = json.load(f)
    except Exception:
        # try line-delimited json
        try:
            with open(path, "r", errors="replace") as f:
                lines = [ln for ln in f if ln.strip()]
            data = lines
        except Exception as e:
            return [("ERR", "parse-fail: %s" % e)]
    items = data if isinstance(data, list) else data.get("messages", data.get("history", []))
    for m in items:
        if not isinstance(m, dict):
            continue
        role = m.get("role") or m.get("type") or ""
        if role != "user":
            continue
        msg = m.get("message") if isinstance(m.get("message"), str) else m
        # extract text
        text = ""
        content = m.get("content") or msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            parts = []
            for c in content:
                if isinstance(c, dict):
                    parts.append(c.get("text") or c.get("content") or "")
                else:
                    parts.append(str(c))
            text = " ".join(str(p) for p in parts if p)
        elif isinstance(content, str):
            text = content
        text = (text or "").strip()
        # skip tool_result-only turns
        if not text:
            continue
        if text.startswith("<tool_") or text.startswith("[Request interrupted"):
            continue
        turns.append(text[:max_chars])
        if len(turns) >= max_turns:
            break
    return turns

def main():
    sid, user = sys.argv[1], sys.argv[2]
    sid_base = sid
    for suf in [".messages.json", ".messages.archive.json", ".json"]:
        if sid_base.endswith(suf):
            sid_base = sid_base[:-len(suf)]
    cands = find_session(sid_base, user)
    if not cands:
        print("NOFILE")
        return
    path = cands[0]
    print("FILE:", path)
    print("SIZE:", os.path.getsize(path))
    turns = extract_user_turns(path)
    for i, t in enumerate(turns):
        print("===U#%d===\n%s" % (i, t))

main()
