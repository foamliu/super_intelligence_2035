import json, sys, re
PATH = "/home/yuyingc/.cline/data/sessions/1793623698314_n7w6c/1793623698314_n7w6c.messages.archive.json"
raw = open(PATH, encoding='utf-8', errors='replace').read()
data = json.loads(raw)
msgs = data.get("messages") if isinstance(data, dict) else data
def get_texts(m):
    content = m.get("content"); texts = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text": texts.append(("TEXT", c.get("text", "")))
                elif c.get("type") == "tool_use":
                    name = c.get("name", "?"); inp = c.get("input", {})
                    inp_str = json.dumps(inp, ensure_ascii=False)[:500]
                    texts.append(("TOOL_USE", "[" + name + "] " + inp_str))
                elif c.get("type") == "tool_result":
                    c2 = c.get("content")
                    if isinstance(c2, list):
                        for cc in c2:
                            if isinstance(cc, dict) and cc.get("type") == "text":
                                texts.append(("TOOL_RES", cc.get("text", "")[:1500]))
                    elif isinstance(c2, str):
                        texts.append(("TOOL_RES", c2[:1500]))
    elif isinstance(content, str): texts.append(("TEXT", content))
    return texts
# Print msgs 369 to 410 (around U#38 msg#371 and U#39 msg#391, U#42 msg#409)
for i in range(369, 412):
    if i >= len(msgs): break
    m = msgs[i]; role = m.get("role", "?")
    texts = get_texts(m)
    for kind, t in texts:
        t = re.sub(r'(sk-[A-Za-z0-9]{6})[A-Za-z0-9_-]+', r'\1***', t)
        if len(t) > 1800: t = t[:1800] + "...[TRUNC]"
        print("=== msg#" + str(i) + " " + role + " " + kind + " ===")
        print(t)
        print()
