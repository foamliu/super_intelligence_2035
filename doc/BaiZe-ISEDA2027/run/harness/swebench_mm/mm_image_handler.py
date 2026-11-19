#!/usr/bin/env python3
"""Download and cache images from GitHub user-images URLs for SWE-bench Multimodal.

Images are downloaded via HTTP proxy (external GitHub URLs need proxy on this host).
Cached to a local directory keyed by URL hash (SHA256[:16]).

Usage (programmatic):
  from mm_image_handler import ImageHandler
  h = ImageHandler(cache_dir="images", proxy="http://172.19.92.25:13128")
  local_path = h.download(url)           # → /path/to/images/abcd1234.png
  b64_url = h.to_data_url(url)           # → data:image/png;base64,iVBOR...
  info = h.get_info(url)                 # → {"path":..., "data_url":..., "mime":...}
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, sys, time
from pathlib import Path
from urllib.request import urlopen, Request, build_opener, ProxyHandler
from urllib.error import URLError, HTTPError

PROXY = os.environ.get("MM_PROXY", "http://172.19.92.25:13128")


def guess_mime(url: str) -> str:
    low = url.lower()
    if low.endswith(".png"): return "image/png"
    if low.endswith((".jpg", ".jpeg")): return "image/jpeg"
    if low.endswith(".gif"): return "image/gif"
    if low.endswith(".webp"): return "image/webp"
    return "image/png"  # GitHub user-images are typically PNG


class ImageHandler:
    """Download, cache, and convert images for SWE-bench Multimodal."""

    def __init__(self, cache_dir: str | Path = "images",
                 proxy: str = PROXY, timeout: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        self.timeout = timeout
        self.manifest_path = self.cache_dir / "manifest.json"
        self.manifest: dict = {}
        if self.manifest_path.exists():
            try: self.manifest = json.loads(self.manifest_path.read_text())
            except Exception: pass

    def _url_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _cache_path(self, url: str) -> Path:
        ext = ".png"
        low = url.lower()
        for e in (".jpg", ".jpeg", ".gif", ".webp", ".png"):
            if low.endswith(e): ext = e; break
        return self.cache_dir / f"{self._url_hash(url)}{ext}"

    def download(self, url: str, retries: int = 2) -> Path | None:
        """Download an image URL to cache. Returns local Path or None on failure."""
        cached = self._cache_path(url)
        if cached.exists() and cached.stat().st_size > 0:
            return cached

        if self.proxy:
            opener = build_opener(ProxyHandler(
                {"http": self.proxy, "https": self.proxy}))
        else:
            opener = build_opener()

        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) BaiZe-MM/1.0",
        })

        for attempt in range(retries + 1):
            try:
                resp = opener.open(req, timeout=self.timeout)
                data = resp.read()
                if len(data) == 0:
                    print(f"[img] WARNING: empty response for {url}", file=sys.stderr)
                    return None
                cached.write_bytes(data)
                self.manifest[url] = {"path": str(cached), "mime": guess_mime(url),
                                       "size": len(data), "ts": time.time()}
                self._save_manifest()
                return cached
            except (URLError, HTTPError, TimeoutError, OSError) as e:
                if attempt < retries:
                    time.sleep(2 ** attempt); continue
                print(f"[img] FAILED {url}: {e}", file=sys.stderr)
                return None
        return None

    def _save_manifest(self):
        try: self.manifest_path.write_text(json.dumps(self.manifest, indent=2))
        except Exception: pass

    def to_data_url(self, url: str) -> str | None:
        path = self.download(url)
        if path is None: return None
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{guess_mime(url)};base64,{b64}"

    def get_info(self, url: str) -> dict | None:
        path = self.download(url)
        if path is None: return None
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return {"path": str(path), "data_url": f"data:{guess_mime(url)};base64,{b64}",
                "mime": guess_mime(url), "size": path.stat().st_size}

    def download_all(self, urls: list[str]) -> dict[str, str | None]:
        results = {}
        for u in urls:
            p = self.download(u)
            results[u] = str(p) if p else None
        return results


def main():
    ap = argparse.ArgumentParser(description="Download MM images")
    ap.add_argument("--url", required=True)
    ap.add_argument("--cache-dir", default=str(Path(__file__).parent / "images"))
    ap.add_argument("--proxy", default=PROXY)
    ap.add_argument("--data-url", action="store_true")
    args = ap.parse_args()
    h = ImageHandler(cache_dir=args.cache_dir, proxy=args.proxy)
    if args.data_url:
        durl = h.to_data_url(args.url)
        if durl: print(f"OK: {durl[:80]}...(len={len(durl)})")
        else: print("FAILED", file=sys.stderr); sys.exit(1)
    else:
        p = h.download(args.url)
        if p: print(f"OK: {p} ({p.stat().st_size} bytes)")
        else: print("FAILED", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()
