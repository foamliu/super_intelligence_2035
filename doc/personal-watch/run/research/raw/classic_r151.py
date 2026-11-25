#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""classic_r151.py —— B 轨第七轮元数据核验（AlphaGo / AlphaGo Zero / Gemini / OpenVLA）

只做只读 GET；arXiv 间隔 >=3s；Crossref / OpenAlex 逐条注明查询日。
输出 JSON 到 stdout（同时落 raw/classic_r151.json）。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "research-watch/1.0 (mailto:foamliu@yeah.net)"
ARXIV = "http://export.arxiv.org/api/query?id_list="
CROSSREF = "https://api.crossref.org/works/"
OPENALEX = "https://api.openalex.org/works/https://doi.org/"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def openalex(doi):
    st, body = get(OPENALEX + doi)
    d = json.loads(body)
    inv = d.get("abstract_inverted_index") or {}
    words = []
    for w, poss in inv.items():
        for p in poss:
            words.append((p, w))
    abstract = " ".join(w for _, w in sorted(words))
    return {
        "status": st,
        "title": d.get("title"),
        "year": d.get("publication_year"),
        "cited_by_count": d.get("cited_by_count"),
        "type": d.get("type"),
        "doi": d.get("doi"),
        "venue": ((d.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "biblio": d.get("biblio"),
        "abstract": abstract,
        "authors": [a["author"]["display_name"] for a in d.get("authorships", [])][:6],
    }


def crossref(doi):
    st, body = get(CROSSREF + doi)
    d = json.loads(body)["message"]
    return {
        "status": st,
        "title": (d.get("title") or [""])[0],
        "container": (d.get("container-title") or [""])[0],
        "volume": d.get("volume"),
        "issue": d.get("issue"),
        "page": d.get("page"),
        "published": d.get("published", {}).get("date-parts"),
        "DOI": d.get("DOI"),
        "authors": ["%s %s" % (a.get("given", ""), a.get("family", ""))
                    for a in d.get("author", [])][:6],
    }


def arxiv(ids):
    st, body = get(ARXIV + ",".join(ids))
    out = {}
    for entry in re.findall(r"<entry>(.*?)</entry>", body, re.S):
        def one(tag):
            m = re.search(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), entry, re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        aid = re.search(r"<id>https?://arxiv.org/abs/([^<]+)</id>", entry)
        out[aid.group(1) if aid else "?"] = {
            "title": one("title"),
            "published": one("published"),
            "updated": one("updated"),
            "authors": re.findall(r"<name>([^<]+)</name>", entry)[:8],
            "summary": one("summary"),
            "primary": (re.search(r'<arxiv:primary_category[^>]*term="([^"]+)"', entry) or [None, ""])[1],
        }
    return {"status": st, "ctype": "atom+xml", "entries": out, "bytes": len(body)}


def main():
    res = {"queried_at": time.strftime("%Y-%m-%d %H:%M:%S"), "items": {}}

    # arXiv 两条（间隔 >=3s）
    a = arxiv(["2312.11805"])
    time.sleep(3.2)
    b = arxiv(["2406.09246"])
    res["arxiv"] = {**a["entries"], **b["entries"]}
    res["arxiv_meta"] = {"a_status": a["status"], "a_bytes": a["bytes"],
                         "b_status": b["status"], "b_bytes": b["bytes"]}

    # Nature 两条
    for key, doi in [("alphago", "10.1038/nature16961"),
                     ("alphago_zero", "10.1038/nature24270")]:
        try:
            cr = crossref(doi)
        except Exception as e:  # noqa: BLE001
            cr = {"error": str(e)}
        time.sleep(1.2)
        try:
            oa = openalex(doi)
        except Exception as e:  # noqa: BLE001
            oa = {"error": str(e)}
        res["items"][key] = {"doi": doi, "crossref": cr, "openalex": oa}
        time.sleep(1.2)

    # arXiv 两条的被引（OpenAlex arXiv DOI）
    for key, aid in [("gemini", "2312.11805"), ("openvla", "2406.09246")]:
        doi = "10.48550/arxiv." + aid
        try:
            oa = openalex(doi)
        except Exception as e:  # noqa: BLE001
            oa = {"error": str(e)}
        res["items"][key] = {"doi": doi, "openalex": oa}
        time.sleep(1.2)

    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
    with open("research/raw/classic_r151.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
