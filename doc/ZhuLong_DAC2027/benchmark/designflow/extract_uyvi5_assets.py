import json, os, re

SESS = "/home/e0046913/.cline/data/sessions/1794790395375_uyvi5/1794790395375_uyvi5.messages.json"
OUT_ROOT = "/tmp/uyvi5_A_assets"
os.makedirs(OUT_ROOT, exist_ok=True)

m = json.load(open(SESS))["messages"]

# Map tool_use_id -> (tool_name, input)
tool_map = {}
for i, x in enumerate(m[:33]):
    if x.get("role") == "assistant":
        for c in x.get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                tool_map[c.get("id")] = (c.get("name"), c.get("input", {}))

LINE_PREFIX_RE = re.compile(r"^ *\d+ \| ")

def strip_line_prefix(line):
    # "  12 | content" -> "content"
    return LINE_PREFIX_RE.sub("", line, count=1)

def safe_rel(path):
    # /proj/lacaa/TV1_digital/simdir/yutingq/CxDP/cla_top_DS/sta/run/Makefile
    # -> sta/run/Makefile  (keep sta/... tree)
    # /proj/lacaa/.../1103_clatop_syn/flow_cla_top/results/cla_top.mapped.v -> 1103_clatop_syn/flow_cla_top/results/cla_top.mapped.v
    p = path
    for prefix in ["/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/", "/rundata/lacaa/TV1_digital/simdir/yutingq/CxDP/"]:
        if p.startswith(prefix):
            return p[len(prefix):]
    return p.lstrip("/")

# Collect: rel_path -> {start_line, content_lines dict}
files = {}
for i, x in enumerate(m[:33]):
    if x.get("role") != "user":
        continue
    for c in x.get("content", []):
        if not isinstance(c, dict) or c.get("type") != "tool_result":
            continue
        tid = c.get("tool_use_id")
        tname, tinput = tool_map.get(tid, ("?", {}))
        if tname != "read_files":
            continue
        content = c.get("content", "")
        if not isinstance(content, list):
            continue
        # input files list (to map query->start_line/end_line)
        in_files = tinput.get("files", [])
        query_to_range = {}
        for f in in_files:
            query_to_range[f.get("path", "")] = (f.get("start_line"), f.get("end_line"))
        for item in content:
            q = item.get("query", "")
            res = item.get("result", "")
            rel = safe_rel(q)
            start, end = query_to_range.get(q, (None, None))
            if rel not in files:
                files[rel] = {"ranges": [], "lines": {}}
            files[rel]["ranges"].append((start, end, len(res)))
            # parse lines
            for ln in res.split("\n"):
                m2 = re.match(r"^ *(\d+) \| (.*)$", ln)
                if m2:
                    lineno = int(m2.group(1))
                    text = m2.group(2)
                    files[rel]["lines"][lineno] = text
                else:
                    # line without prefix (continuation or non-numbered); append to last
                    pass

# Write merged files
written = []
for rel, data in sorted(files.items()):
    out_path = os.path.join(OUT_ROOT, rel)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    lines = data["lines"]
    if not lines:
        # no numbered lines, write raw concatenation
        with open(out_path, "w") as f:
            f.write("")
        written.append((rel, 0, data["ranges"]))
        continue
    max_ln = max(lines.keys())
    # write 1..max_ln, missing lines = ""
    with open(out_path, "w") as f:
        for ln in range(1, max_ln + 1):
            f.write(lines.get(ln, "") + "\n")
    written.append((rel, max_ln, data["ranges"]))

print("Wrote", len(written), "files to", OUT_ROOT)
for rel, max_ln, ranges in written:
    print(f"  {rel}: {max_ln} lines, ranges={ranges}")
