#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""x_fetch.py —— B 轨「X 只读抓取」（登录前 profile 页内嵌 JSON 解析）

用途：给 `research/classic/AUTHORS.md` 的作者跟踪提供一手言论（`voice_ready`）证据。
边界（硬）：
  - 🚫 只做 GET 只读；不登录、不注册、不使用任何凭据、不执行 follow/like/发帖。
  - ⏱ 串行请求，间隔 ≥3s（与 arXiv 同口径）。
  - ❌ 抓不到就写空结果，🚫 不猜、不补。

依赖：仅标准库（urllib / json / re）+ 本机代理（默认 http://127.0.0.1:7897）。
用法：
  python3 x_fetch.py _jasonwei tri_dao          # 默认 6 个 handle 上限
  python3 x_fetch.py --outdir /tmp/x _jasonwei
输出：<outdir>/<handle>.json  {"handle","bio","tweets":[{"id","created_at","text","url","handle_guess"}]}
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "x")
PROXY = os.environ.get("X_PROXY", "http://127.0.0.1:7897")


def _opener():
    if not PROXY:
        return urllib.request.build_opener()
    handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    return urllib.request.build_opener(handler)


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    })
    with _opener().open(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def _unescape(raw):
    try:
        return json.loads('"' + raw + '"')
    except Exception:
        return raw.replace('\\"', '"').replace("\\n", "\n").replace("\\/", "/")


def parse_profile(html, handle):
    bio = ""
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    if m:
        bio = m.group(1)
    name = ""
    m = re.search(r"<title>([^<]*)</title>", html)
    if m:
        name = m.group(1).strip()

    # 登录前页面把 timeline JSON 以 \" 转义后内嵌在 <script> 里 ⇒ 先整体去转义再切块解析。
    # ⚠️ 去转义后正文内的 \\" 也会变成 " ⇒ 正文可能被截断；**引用前必须回推文页复核**（见 --verify 用法说明）。
    flat = html.replace('\\"', '"').replace("\\/", "/").replace("\\n", "\n")

    tweets, seen = [], set()
    for chunk in flat.split('"created_at_ms":')[1:]:
        m = re.match(r"(\d+)", chunk)
        if not m:
            continue
        ms = int(m.group(1))
        mt = re.search(r'"full_text":"([^"]*)"', chunk[:6000])
        mid = re.search(r'"edit_tweet_ids":\["(\d+)"\]', chunk[:6000]) or \
            re.search(r'"rest_id":"(\d+)"', chunk[:6000])
        if not mt or not mid:
            continue
        tid = mid.group(1)
        text = _unescape(mt.group(1))
        if not text or tid in seen:
            continue
        seen.add(tid)
        # 该条推文的作者（就近向前找 screen_name；仅作候选，最终仍以推文页复核为准）
        idx = flat.index('"created_at_ms":' + str(ms))
        head = flat[max(0, idx - 6000):idx]
        sn = re.findall(r'"screen_name":"([A-Za-z0-9_]{1,20})"', head)
        tweets.append({
            "id": tid,
            "created_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(ms / 1000)),
            "created_at_ms": ms,
            "text": text,
            "url": "https://x.com/%s/status/%s" % (handle, tid),
            "handle_guess": sn[-1] if sn else "",
        })
    tweets.sort(key=lambda t: t["created_at_ms"], reverse=True)
    return {"handle": handle, "name": name, "bio": bio, "tweets": tweets}


def verify_tweet(url):
    """回推文页复核：返回 (og_title, 页面字数)；og_title 形如 `Jason Wei (@_jasonwei) on X`。"""
    code, html = fetch(url)
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    return code, (m.group(1) if m else ""), len(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handles", nargs="*")
    ap.add_argument("--verify", nargs="*", default=[], help="推文 URL 列表：只复核作者/正文")
    ap.add_argument("--outdir", default=DEFAULT_OUT)
    ap.add_argument("--sleep", type=float, default=3.0)
    ap.add_argument("--max", type=int, default=6, help="单轮最多抓几个 handle")
    args = ap.parse_args()

    if args.verify:
        for i, u in enumerate(args.verify):
            if i:
                time.sleep(args.sleep)
            try:
                code, title, n = verify_tweet(u)
                print("VERIFY %s -> %s  title=%r  html=%d B" % (u, code, title, n))
            except Exception as e:  # noqa: BLE001
                print("VERIFY %s -> ERR %s" % (u, e), file=sys.stderr)
        if not args.handles:
            return 0

    if len(args.handles) > args.max:
        print("refuse: %d handles > --max %d（限速纪律）" % (len(args.handles), args.max),
              file=sys.stderr)
        return 2
    os.makedirs(args.outdir, exist_ok=True)
    for i, h in enumerate(args.handles):
        h = h.lstrip("@")
        if i:
            time.sleep(args.sleep)
        url = "https://x.com/" + h
        try:
            code, html = fetch(url)
        except Exception as e:  # noqa: BLE001
            print("%-18s ERR %s" % (h, e), file=sys.stderr)
            continue
        data = parse_profile(html, h)
        data["http_status"] = code
        data["fetched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(args.outdir, h + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("%-18s %s  bio=%r  tweets=%d  -> %s"
              % (h, code, data["bio"][:60], len(data["tweets"]), path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
