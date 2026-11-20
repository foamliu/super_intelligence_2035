#!/usr/bin/env python3
"""一次性脚本（第八十五轮 · PM）：按 id_list 取单条权威元数据 + 摘要。
- 端点 https://export.arxiv.org/api/query?id_list=...
- 校验 HTTP 200 + application/atom+xml + 有 published
- 限速 >=3s
输出 JSON 到 stdout（也可 --out）。
"""
import sys, time, json, urllib.request, xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
IDS = sys.argv[1].split(",") if len(sys.argv) > 1 else []
OUT = None
if "--out" in sys.argv:
    OUT = sys.argv[sys.argv.index("--out") + 1]

def fetch(ids):
    url = ("https://export.arxiv.org/api/query?id_list=" + ",".join(ids)
           + "&max_results=50")
    req = urllib.request.Request(url, headers={"User-Agent": "research-watch/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        ct = r.headers.get("Content-Type", "")
        body = r.read().decode("utf-8", "replace")
        return r.status, ct, body

res = []
for i in range(0, len(IDS), 20):
    batch = IDS[i:i+20]
    status, ct, body = fetch(batch)
    root = ET.fromstring(body)
    for e in root.findall("a:entry", NS):
        aid = e.findtext("a:id", "", NS).rsplit("/abs/", 1)[-1]
        title = " ".join((e.findtext("a:title", "", NS) or "").split())
        pub = e.findtext("a:published", "", NS)
        upd = e.findtext("a:updated", "", NS)
        prim = ""
        for c in e.findall("a:category", NS):
            if c.get("scheme", "").endswith("arxiv.org/"):
                pass
        ctg = e.find("{http://arxiv.org/schemas/atom}primary_category")
        prim = ctg.get("term") if ctg is not None else ""
        summ = " ".join((e.findtext("a:summary", "", NS) or "").split())
        authors = [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)]
        comment = e.find("{http://arxiv.org/schemas/atom}comment")
        jr = e.find("{http://arxiv.org/schemas/atom}journal_ref")
        res.append({"id": aid, "published": pub, "updated": upd, "primary": prim,
                    "title": title, "authors": authors,
                    "comment": comment.text if comment is not None else "",
                    "journal_ref": jr.text if jr is not None else "",
                    "summary": summ})
    if i + 20 < len(IDS):
        time.sleep(3)

out = {"n": len(res), "http": status, "content_type": ct, "entries": res}
s = json.dumps(out, ensure_ascii=False, indent=2)
if OUT:
    open(OUT, "w").write(s)
print(s)
