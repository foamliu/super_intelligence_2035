#!/usr/bin/env python3
"""hf_api_fetch.py — Batch fetch HF dataset API info via proxy.
Usage: python3 hf_api_fetch.py <repo1> <repo2> ...
Outputs JSON lines to stdout: {"repo":..., "id":..., "gated":..., "downloads":...,
  "lastModified":..., "license":..., "size_cat":..., "tags":..., "desc":...}
Failed fetches output {"repo":..., "error":...}
"""
import sys, os, json, requests

PROXY = "http://172.19.92.25:13128"
os.environ["https_proxy"] = PROXY
os.environ["http_proxy"] = PROXY

def fetch_one(repo_id):
    url = f"https://huggingface.co/api/datasets/{repo_id}"
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return {"repo": repo_id, "error": f"HTTP {r.status_code}"}
        d = r.json()
        cd = d.get("cardData") or {}
        return {
            "repo": repo_id,
            "id": d.get("id", "?"),
            "gated": d.get("gated", False),
            "private": d.get("private", False),
            "disabled": d.get("disabled", False),
            "downloads": d.get("downloads", "?"),
            "lastModified": d.get("lastModified", "?"),
            "license": cd.get("license", "?"),
            "size_cat": cd.get("size_categories", "?"),
            "tags": [t for t in d.get("tags", []) if not t.startswith("region:")][:8],
            "desc": (cd.get("description") or cd.get("short_description") or "")[:200],
            "card_keys": list(cd.keys())[:10],
        }
    except Exception as e:
        return {"repo": repo_id, "error": str(e)[:200]}

if __name__ == "__main__":
    repos = sys.argv[1:]
    for repo in repos:
        info = fetch_one(repo)
        print(json.dumps(info, ensure_ascii=False))
        sys.stdout.flush()
