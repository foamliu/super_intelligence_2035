#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/archive/fetch_archive.py — N1 历史回溯**语料库**抓取器（可中断可恢复）
==========================================================================
目标：为 L1（政策信号预测）提供**长期语料** —— 只取「标题 + 日期 + 来源(channel) + 链接」，
      🚫 **不请求文章详情页、不保存正文**（见 news/archive/README.md 契约）。

源（2026-10-03 本机实测，见 PROGRESS.md 与 WATCH_NEWS_TASK.md 第7批 N1）：
  * 新华网（**主源**）：日期路径 https://www.xinhuanet.com/{politics,...}/{YYYY}-{MM}/{DD}/ → **HTTP 403**；
    so.news.cn/getNews → **HTTP 405**（WAF 页）→ 🚫 **不绕**（不代理、不伪造 UA），走兜底源。
  * 中新网（**兜底**，已实测 200 且**可逐日枚举**）：
    https://www.chinanews.com.cn/scroll-news/{YYYY}/{MMDD}/news.shtml
    页面条目结构：
      <div class="dd_lm">[频道]</div>
      <div class="dd_bt"><a href="/xx/YYYY/MM-DD/id.shtml">标题</a></div>
      <div class="dd_time">M-D HH:MM</div>

输出：news/archive/<source>-<年>.jsonl.gz   （每行**仅 5 字段**：date/source/channel/title/url；主键 url）
断点：news/archive/.progress.json           （机器可读游标；PROGRESS.md 为对应人读版）
限速：同站默认 **≥2.0s/请求**；失败重试 ≤2 次后跳过并记录（🚫 不并发）。

⚠️ 纪律：只取公开可见标题/链接；不抓正文；**源字段严格区分**（不许把兜底源标成 xinhua）；
   尊重 robots；控制频率。本脚本只写入 news/archive/ 下的本线文件。
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html as _html
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta

import requests

UA = "Mozilla/5.0 (compatible; PersonalWatch/1.0)"
HEADERS = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
TIMEOUT = 20
HERE = os.path.dirname(os.path.abspath(__file__))
PROGRESS_JSON = os.path.join(HERE, ".progress.json")
PROGRESS_MD = os.path.join(HERE, "PROGRESS.md")

# 中新网条目解析（dd_lm 频道 / dd_bt 链接+标题 / dd_time 时间）
CN_HOST = "https://www.chinanews.com.cn"
_CN_DOUBLE = CN_HOST + "//www.chinanews.com.cn"   # 历史误拼接（协议相对链接被重复加前缀）
CN_ITEM = re.compile(
    r'<div class="dd_lm">\[(?P<channel>[^\]]*)\]</div>\s*'
    r'<div class="dd_bt"><a href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a></div>\s*'
    r'<div class="dd_time">(?P<t>[^<]*)</div>',
    re.S)


def normalize_url(url: str) -> str:
    """把 href 规整为绝对 URL（处理 绝对 / 协议相对 `//` / 站内 `/` 三种）。"""
    url = (url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return CN_HOST + url
    return CN_HOST + "/" + url


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = _html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def decode_html(b: bytes) -> str:
    """按页面 meta/HTTP 声明解码头；CHARSET 缺失时 utf-8 → gbk 依次回退。

    实测：中新网**新版页面为 UTF-8**，**旧版（约 2016 前后）为 GBK**；
    HTTP 头不带 charset，故必须从 HTML 里探测，否则老页面会乱码。
    """
    m = re.search(rb'charset=["\']?\s*([\w-]+)', b[:4096], re.I)
    cands = []
    if m:
        try:
            enc = m.group(1).decode("ascii", "ignore").lower()
        except Exception:  # noqa: BLE001
            enc = ""
        cands.append({"gb2312": "gbk", "gb-2312": "gbk"}.get(enc, enc))
    cands += ["utf-8", "gbk"]
    for enc in cands:
        if not enc:
            continue
        try:
            return b.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return b.decode("utf-8", errors="replace")


def shard_path(source: str, year: int) -> str:
    return os.path.join(HERE, f"{source}-{year}.jsonl.gz")


def load_url_index(source: str) -> dict:
    """扫描全部年份 shard，建 {year: set(url)} 去重索引。"""
    idx: dict = {}
    for fn in sorted(os.listdir(HERE)):
        m = re.match(rf"^{re.escape(source)}-(\d{{4}})\.jsonl\.gz$", fn)
        if not m:
            continue
        year = int(m.group(1))
        s = set()
        with gzip.open(os.path.join(HERE, fn), "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    s.add(json.loads(line).get("url"))
                except Exception:  # noqa: BLE001
                    pass
        idx[year] = s
    return idx


class ShardWriter:
    """按年增量追写 gzip shard（多次追加 = 多个 gzip member，读取端可正常拼接）。"""

    def __init__(self, source: str):
        self.source = source
        self.buf: dict = {}

    def add(self, year: int, rec: dict) -> None:
        self.buf.setdefault(year, []).append(rec)

    def flush(self) -> int:
        n = 0
        for year, recs in self.buf.items():
            if not recs:
                continue
            with gzip.open(shard_path(self.source, year), "ab") as f:
                for r in recs:
                    f.write((json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8"))
            n += len(recs)
        self.buf.clear()
        return n


def fetch_day_cn(sess: requests.Session, y: int, m: int, d: int):
    """返回 (status, url, text)；status ∈ {'ok','empty','fail'}。"""
    url = f"https://www.chinanews.com.cn/scroll-news/{y}/{m:02d}{d:02d}/news.shtml"
    code = "?"
    for attempt in range(3):
        try:
            r = sess.get(url, headers=HEADERS, timeout=TIMEOUT)
            code = r.status_code
            if r.status_code == 200:
                return "ok", url, decode_html(r.content)
            if r.status_code == 404:
                return "empty", url, ""
        except Exception as e:  # noqa: BLE001
            code = f"EXC:{e.__class__.__name__}"
        time.sleep(1.5 * (attempt + 1))
    return "fail", url, str(code)


def parse_cn(text: str, y: int, m: int, d: int) -> list:
    iso = f"{y:04d}-{m:02d}-{d:02d}"
    out = []
    for mm in CN_ITEM.finditer(text):
        url = normalize_url(mm.group("url"))
        title = clean(mm.group("title"))
        channel = clean(mm.group("channel"))
        if not url or not title:
            continue
        out.append({"date": iso, "source": "chinanews",
                    "channel": channel, "title": title, "url": url})
    return out


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_state(source: str, start: str, end: str) -> dict:
    if os.path.exists(PROGRESS_JSON):
        with open(PROGRESS_JSON, encoding="utf-8") as f:
            st = json.load(f)
        if st.get("source") == source:
            return st
    return {"source": source, "next_day": start, "start": start, "end": end,
            "done_days": 0, "total_recs": 0, "empty_days": 0,
            "fail_days": [], "per_year": {}, "updated": ""}


def save_state(st: dict) -> None:
    st["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_JSON, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def write_index_files() -> None:
    """生成 INDEX_FILES.md：路径 · 行数 · 大小 · sha256（体积纪律对照）。"""
    rows = []
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".jsonl.gz"):
            continue
        p = os.path.join(HERE, fn)
        nline = 0
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for _ in f:
                nline += 1
        rows.append((fn, nline, os.path.getsize(p), sha256_file(p)))
    big = [r for r in rows if r[2] > 20 * 1024 * 1024]
    lines = ["# INDEX_FILES — 历史语料大文件清单\n",
             "> 由 `fetch_archive.py --index` **自动生成**。体积纪律：**单文件 >20 MB → 🚫 不入 git**",
             "> （本体移 `~/archive_data/`，本表登记路径/行数/大小/sha256）。\n",
             "| 路径 | 行数 | 大小(B) | sha256(前16) | 入 git |",
             "|:--|--:|--:|:--|:--|"]
    for fn, nline, size, sha in rows:
        ingit = "🚫 否(>20MB)" if size > 20 * 1024 * 1024 else "✅ 是"
        lines.append(f"| `news/archive/{fn}` | {nline} | {size} | `{sha}` | {ingit} |")
    if not rows:
        lines.append("| _（暂无 shard）_ | 0 | 0 | - | - |")
    if big:
        lines.append(f"\n> ⚠️ **{len(big)} 个文件 >20MB** → 需移出 git 并在 `.gitignore` 排除。")
    with open(os.path.join(HERE, "INDEX_FILES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def repair_shards(source: str) -> int:
    """一次性修复历史 shard 中被重复加前缀的 URL（幂等；顺带按 url 去重）。"""
    fixed = 0
    for fn in sorted(os.listdir(HERE)):
        if not re.match(rf"^{re.escape(source)}-(\d{{4}})\.jsonl\.gz$", fn):
            continue
        p = os.path.join(HERE, fn)
        recs, seen = [], set()
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                u = o.get("url", "")
                nu = normalize_url(u.replace(_CN_DOUBLE, CN_HOST))
                if nu != u:
                    o["url"] = nu
                    fixed += 1
                if nu in seen:
                    continue
                seen.add(nu)
                recs.append(o)
        with gzip.open(p, "wt", encoding="utf-8") as f:
            for o in recs:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return fixed


def write_progress_md(st: dict) -> None:
    lines = []
    lines.append("# PROGRESS — N1 历史回溯语料抓取 · 进度游标\n")
    lines.append("> 由 `fetch_archive.py` **自动生成**（不要手改）；机器游标见 `.progress.json`。\n")
    lines.append(f"> 更新：{st.get('updated', '-')}\n")
    lines.append("\n## 1. 源可用性结论（实测，2026-10-03）\n")
    lines.append("| 源 | 端点 | 实测 | 判定 |\n|:--|:--|:--|:--|")
    lines.append("| 新华网（主源） | `https://www.xinhuanet.com/politics/2016-01/01/` | **HTTP 403** | ❌ 日期路径不通 |")
    lines.append("| 新华网（站内搜索） | `https://so.news.cn/getNews?...` | **HTTP 405**（WAF 页） | ❌ 不通 |")
    lines.append("| **中新网（兜底）** | `https://www.chinanews.com.cn/scroll-news/{YYYY}/{MMDD}/news.shtml` | **HTTP 200** | ✅ **可逐日枚举** |")
    lines.append("")
    lines.append("> 🚫 新华网 403/405 **如实记录、不绕**（不代理、不伪造 UA）。")
    lines.append(f"> 📝 **新华网 {st.get('end', '2016')}–{st.get('start', '2026')} 未通 → 该区间由代理源 `chinanews` 覆盖**；"
                 "🚫 代理源**不冒充**新华社（`source` 字段严格为 `chinanews`）。\n")
    lines.append("\n## 2. 游标（断点续抓）\n")
    lines.append(f"- 源：`{st.get('source')}` ｜ 区间：`{st.get('start')}` ← `{st.get('next_day')}` → `{st.get('end')}`（**倒序**逐日）")
    lines.append(f"- 已完成天数：**{st.get('done_days')}** ｜ 空页(404)：{st.get('empty_days')} ｜ 失败：{len(st.get('fail_days', []))}")
    lines.append(f"- 累计条目：**{st.get('total_recs')}** ｜ 限速：同站 ≥2s/请求\n")
    lines.append("\n## 3. 分年条目数（真实计数）\n")
    lines.append("| 年 | 条数 | shard | 大小 | sha256(前16) |\n|:--|--:|:--|--:|:--|")
    for y in sorted(st.get("per_year", {}), key=lambda x: int(x)):
        cnt = st["per_year"][y]
        p = shard_path(st["source"], int(y))
        size = os.path.getsize(p) if os.path.exists(p) else 0
        sha = sha256_file(p) if os.path.exists(p) else "-"
        lines.append(f"| {y} | {cnt} | `{os.path.basename(p)}` | {size} B | `{sha}` |")
    if st.get("fail_days"):
        lines.append("\n## 4. 失败日（HTTP 非 200/404）\n")
        for dy in st["fail_days"][-40:]:
            lines.append(f"- {dy}")
    with open(PROGRESS_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="N1 历史回溯语料抓取器（中新网逐日枚举）")
    ap.add_argument("--source", default="chinanews", choices=["chinanews"])
    ap.add_argument("--start", default=None, help="起始日 YYYY-MM-DD（默认今天；仅首次生效）")
    ap.add_argument("--end", default="2016-01-01", help="终止日（含），倒序到该日停")
    ap.add_argument("--max-seconds", type=float, default=600, help="单轮最长运行秒数（默认 600）")
    ap.add_argument("--min-interval", type=float, default=2.0, help="同站最小请求间隔秒（默认 2.0）")
    ap.add_argument("--reset", action="store_true", help="重置游标（不改 shard）")
    ap.add_argument("--check", metavar="YYYY-MM-DD", help="仅解析并打印某日，不落盘")
    ap.add_argument("--stats", action="store_true", help="只统计现有 shard 并重写 PROGRESS.md")
    ap.add_argument("--index", action="store_true", help="只生成 INDEX_FILES.md 后退出")
    ap.add_argument("--repair", action="store_true", help="修复历史 shard 的 URL（幂等）后退出")
    args = ap.parse_args()

    source = args.source
    today = date.today().isoformat()
    start = args.start or today

    if args.repair:
        n = repair_shards(source)
        print(f"[repair] fixed_urls={n}")
        return 0

    if args.index:
        write_index_files()
        print("[index] wrote INDEX_FILES.md")
        return 0

    # --check：单日解析自检
    if args.check:
        y, m, d = map(int, args.check.split("-"))
        with requests.Session() as sess:
            stt, url, text = fetch_day_cn(sess, y, m, d)
        print(f"[check] {url} status={stt} bytes={len(text)}")
        recs = parse_cn(text, y, m, d) if stt == "ok" else []
        print(f"[check] parsed={len(recs)}")
        for r in recs[:5]:
            print(" -", r["date"], "|", r["channel"], "|", r["title"][:40], "|", r["url"])
        return 0

    # --stats：只统计
    if args.stats:
        idx = load_url_index(source)
        st = load_state(source, start, args.end)
        st["per_year"] = {str(y): len(s) for y, s in idx.items()}
        st["total_recs"] = sum(len(s) for s in idx.values())
        save_state(st)
        write_progress_md(st)
        print(f"[stats] years={len(idx)} total={st['total_recs']}")
        return 0

    if args.reset and os.path.exists(PROGRESS_JSON):
        os.remove(PROGRESS_JSON)

    st = load_state(source, start, args.end)
    if not st.get("start"):
        st.update({"start": start, "next_day": start, "end": args.end})
    end_d = date.fromisoformat(st["end"])
    cur = date.fromisoformat(st["next_day"])
    if cur < end_d:
        print(f"[done] cursor {cur} already past end {end_d}")
        return 0

    idx = load_url_index(source)
    writer = ShardWriter(source)
    t0 = time.time()
    last = None  # 上次请求时刻（限速用）
    print(f"[run] source={source} from {cur} back to {end_d}  max={args.max_seconds}s  >=2s/req")

    with requests.Session() as sess:
        while cur >= end_d and (time.time() - t0) < args.max_seconds:
            if last is not None:
                gap = args.min_interval - (time.time() - last)
                if gap > 0:
                    time.sleep(gap)
            last = time.time()

            stt, url, text = fetch_day_cn(sess, cur.year, cur.month, cur.day)
            if stt == "ok":
                recs = parse_cn(text, cur.year, cur.month, cur.day)
                known = idx.setdefault(cur.year, set())
                fresh = [r for r in recs if r["url"] not in known]
                for r in fresh:
                    known.add(r["url"])
                    writer.add(cur.year, r)
                st["per_year"][str(cur.year)] = len(known)
                st["total_recs"] += len(fresh)
                st["done_days"] += 1
                print(f"[ok] {cur} recs={len(recs)} fresh={len(fresh)}")
            elif stt == "empty":
                st["empty_days"] += 1
                print(f"[404] {cur}")
            else:
                st["fail_days"].append(f"{cur} ({text})")
                print(f"[FAIL] {cur} code={text}")

            cur -= timedelta(days=1)
            st["next_day"] = cur.isoformat()
            # 每 2 天落一次盘，保证可中断
            if st["done_days"] % 2 == 0:
                writer.flush()
                save_state(st)

    writer.flush()
    save_state(st)
    write_progress_md(st)
    print(f"[done] done_days={st['done_days']} total={st['total_recs']} "
          f"next={st['next_day']} elapsed={time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[interrupt] flushing ...")
        sys.exit(130)