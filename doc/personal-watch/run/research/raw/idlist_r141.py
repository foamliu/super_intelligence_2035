#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十一轮（本地 2026-11-09 06:00 AM「早报 3 篇」轮）：id_list 权威复核。

产出：raw/2026-11-09-am-idlist-r141<后缀>.xml + .headers
用法（在 research/ 目录）：python3 raw/idlist_r140.py <后缀> <id1> <id2> ...
"""
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HOST = "export.arxiv.org"
BASE = Path(__file__).resolve().parent.parent  # research/


def main():
    suffix = sys.argv[1]
    ids = sys.argv[2:]
    assert ids, "need at least one arXiv id"
    qs = urllib.parse.urlencode({
        "id_list": ",".join(ids),
        "max_results": str(len(ids)),
    })
    url = "https://%s/api/query?%s" % (HOST, qs)
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-watch/1.0 (mailto:foamliu@yeah.net)",
    })
    t0 = time.time()
    last = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw = resp.read()
                ctype = resp.headers.get("Content-Type")
                status = resp.status
            break
        except Exception as exc:  # noqa: BLE001
            last = exc
            print("attempt %d failed: %r" % (attempt, exc), flush=True)
            time.sleep(3.2)
    else:
        raise last
    dt = time.time() - t0
    out_xml = BASE / "raw" / ("2026-11-09-am-idlist-r141%s.xml" % suffix)
    out_hdr = BASE / "raw" / ("2026-11-09-am-idlist-r141%s.headers" % suffix)
    out_xml.write_bytes(raw)
    out_hdr.write_text(
        "url: %s\nstatus: %s\ncontent-type: %s\nbytes: %d\nelapsed: %.2fs\n"
        % (url, status, ctype, len(raw), dt),
        encoding="utf-8",
    )
    print("STATUS=%s CTYPE=%s BYTES=%d ELAPSED=%.2fs" % (status, ctype, len(raw), dt))
    print("SAVED=%s" % out_xml)


if __name__ == "__main__":
    main()
