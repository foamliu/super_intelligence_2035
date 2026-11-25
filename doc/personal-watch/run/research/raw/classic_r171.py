#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""classic_r171.py —— B 轨第二十七轮元数据核验（Latent Diffusion / MuZero / AutoDMP / DREAM-GAN）

只做只读 GET；arXiv 间隔 >=3s；Crossref / OpenAlex 逐条注明查询日。
输出 JSON 到 stdout（同时落 raw/classic_r171.json）。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "research-watch/1.0 (mailto:foamliu@yeah.net)"
ARXIV = "http://export.arxiv.org/api/query?%s"
CROSSREF = "https://api.crossref.org/works/"
OPENALEX = "https://api.openalex.org/works/https://doi.org/"


def get(url, timeout=40, tries=4):
    """只读 GET；429 / 5xx 退避重试（本轮实测 arXiv 在候选池抓取后立刻 429）。"""
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:  # noqa: PERF203
            last = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
            wait = 20 * (i + 1)
            print("  HTTP %s on %s -> sleep %ds" % (e.code, url[:90], wait), flush=True)
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(10 * (i + 1))
    raise last


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
        "authors": [a["author"]["display_name"] for a in d.get("authorships", [])][:8],
        "institutions": [[i.get("display_name") for i in a.get("institutions", [])]
                         for a in d.get("authorships", [])][:8],
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
                    for a in d.get("author", [])][:8],
    }


def arxiv(ids):
    url = ARXIV % urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": len(ids)})
    st, body = get(url)
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
            "comment": one("arxiv:comment"),
            "primary": (re.search(r'<arxiv:primary_category[^>]*term="([^"]+)"', entry) or [None, ""])[1],
        }
    return {"status": st, "entries": out, "bytes": len(body),
            "content_type": "application/atom+xml" if "<feed" in body[:400] else "?"}


def arxiv_search(term):
    url = ARXIV % urllib.parse.urlencode({
        "search_query": term, "start": 0, "max_results": 5,
        "sortBy": "relevance", "sortOrder": "descending"})
    st, body = get(url)
    tr = re.search(r"<opensearch:totalResults[^>]*>(\d+)<", body)
    titles = [re.sub(r"\s+", " ", t).strip()
              for t in re.findall(r"<title>(.*?)</title>", body, re.S)][1:]
    return {"status": st, "total": int(tr.group(1)) if tr else None, "titles": titles}


def main():
    res = {"queried_at": time.strftime("%Y-%m-%d %H:%M:%S"), "items": {}}

    a = arxiv(["2207.11240"])
    time.sleep(3.2)
    b = arxiv(["1911.08265"])
    res["arxiv"] = {**a["entries"], **b["entries"]}
    res["arxiv_meta"] = {"a_status": a["status"], "a_bytes": a["bytes"], "a_ct": a["content_type"],
                         "b_status": b["status"], "b_bytes": b["bytes"], "b_ct": b["content_type"]}

    time.sleep(3.2)
    res["no_arxiv_autodmp"] = arxiv_search('ti:"AutoDMP"')
    time.sleep(3.2)
    res["no_arxiv_dreamgan"] = arxiv_search('ti:"DREAM-GAN"')

    for key, doi in [("latent_diffusion", "10.48550/arxiv.2207.11240"),
                     ("muzero", "10.48550/arxiv.1911.08265"),
                     ("autodmp", "10.1145/3569052.3578923"),
                     ("dreamgan", "10.1145/3569052.3572993")]:
        try:
            oa = openalex(doi)
        except Exception as e:  # noqa: BLE001
            oa = {"error": repr(e)}
        res["items"][key] = {"doi": doi, "openalex": oa}
        time.sleep(1.2)

    for key, doi in [("autodmp", "10.1145/3569052.3578923"),
                     ("dreamgan", "10.1145/3569052.3572993")]:
        try:
            cr = crossref(doi)
        except Exception as e:  # noqa: BLE001
            cr = {"error": repr(e)}
        res["items"][key]["crossref"] = cr
        time.sleep(1.2)

    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
    with open("research/raw/classic_r171.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
