#!/usr/bin/env python3
"""MM proxy: converts markdown-embedded images to OpenAI image_url content.

Sits between cline CLI and the gateway.  cline passes the initial task as text
(including markdown image tags).  This proxy intercepts the chat completion
request, extracts image references from markdown image tags in the first user
message, and converts to multimodal format:
  [{type:text, text:...}, {type:image_url, image_url:{url:data:...}}]

Two image reference styles are supported:
  1. Inline data: URLs  — ![alt](data:image/png;base64,<b64>)
     (kept for backwards compat; not used by run_mm_2x3.py because the base64
      payload exceeds the 128 KB single-argument limit (MAX_ARG_STRLEN) when
      passed as a cline positional prompt argument.)
  2. Short proxy URLs   — ![alt](http://127.0.0.1:<port>/mm_image/<filename>)
     The proxy reads <filename> from --image-dir, base64-encodes it, and emits
     an image_url content part.  This keeps the cline command-line prompt tiny.
"""
from __future__ import annotations
import argparse, base64, http.client, json, re, sys, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Inline data: URLs (legacy / small images)
MD_DATAIMG_RE = re.compile(
    r'!\[[^\]]*\]\(data:(image/[a-z]+);base64,([A-Za-z0-9+/=]+)\)')

# Short proxy URLs: http://127.0.0.1:<port>/mm_image/<filename>
MD_PROXYIMG_RE = re.compile(
    r'!\[[^\]]*\]\(https?://127\.0\.0\.1:\d+/mm_image/([^)\s]+)\)')

# Module-level image directory (set in main(), read by convert_message_content)
IMAGE_DIR: str | None = None

_MIME_BY_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp"}


def _read_proxy_image(filename: str):
    """Read image file from IMAGE_DIR. Returns (mime, base64_str) or None."""
    if not IMAGE_DIR:
        return None
    # Sanitize: only basename, no path traversal
    safe = Path(filename).name
    p = Path(IMAGE_DIR) / safe
    if not p.is_file():
        print(f"[mm_proxy] image not found: {p}", file=sys.stderr)
        return None
    mime = _MIME_BY_EXT.get(p.suffix.lower(), "image/png")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return mime, b64


def convert_message_content(content):
    """If content is a string with markdown image tags, convert to multimodal.

    Handles both inline data: URLs and short proxy /mm_image/<file> URLs.
    """
    if not isinstance(content, str):
        return content

    # Collect all matches (data: + proxy) sorted by position
    matches = []
    for m in MD_DATAIMG_RE.finditer(content):
        matches.append((m.start(), m.end(), "data", m))
    for m in MD_PROXYIMG_RE.finditer(content):
        matches.append((m.start(), m.end(), "proxy", m))
    matches.sort(key=lambda x: x[0])
    if not matches:
        return content

    parts = []
    last_end = 0
    for start, end, kind, m in matches:
        text_before = content[last_end:start].strip()
        if text_before:
            parts.append({"type": "text", "text": text_before})
        if kind == "data":
            parts.append({"type": "image_url",
                          "image_url": {"url": f"data:{m.group(1)};base64,{m.group(2)}"}})
        else:  # proxy URL → read local file
            res = _read_proxy_image(m.group(1))
            if res:
                mime, b64 = res
                parts.append({"type": "image_url",
                              "image_url": {"url": f"data:{mime};base64,{b64}"}})
            else:
                # keep original markdown text if file unreadable
                parts.append({"type": "text", "text": content[start:end]})
        last_end = end
    text_after = content[last_end:].strip()
    if text_after:
        parts.append({"type": "text", "text": text_after})
    return parts if parts else content


def process_body(body: bytes) -> bytes:
    """Parse JSON body, convert first user message content, return modified body."""
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return body
    messages = data.get("messages", [])
    for msg in messages:
        if msg.get("role") == "user":
            converted = convert_message_content(msg.get("content"))
            if converted != msg.get("content"):
                msg["content"] = converted
            break  # only first user message
    return json.dumps(data).encode()


class MMProxyHandler(BaseHTTPRequestHandler):
    upstream_url = None
    api_key = None

    def log_message(self, fmt, *args):
        pass

    def _forward(self, method: str):
        parsed = urlparse(self.upstream_url)
        upstream_host = parsed.hostname
        upstream_port = parsed.port or 80
        # Forward self.path as-is: the upstream URL provides only host:port.
        # The API path suffix (e.g. /cloud/v1 or /v1) is baked into cline's
        # OPENAI_BASE_URL, so self.path already contains the full correct path
        # (e.g. /cloud/v1/chat/completions).  Prepending parsed.path would
        # double the /v1 segment → gateway 403 Forbidden.
        upstream_path = self.path
        print(f"[mm_proxy] {method} {upstream_path} → "
              f"{upstream_host}:{upstream_port}", file=sys.stderr)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        if "/chat/completions" in self.path and method == "POST" and body:
            body = process_body(body)
        conn = http.client.HTTPConnection(upstream_host, upstream_port, timeout=600)
        headers = dict(self.headers)
        headers["Host"] = f"{upstream_host}:{upstream_port}"
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if body:
            headers["Content-Length"] = str(len(body))
        for h in ("Transfer-Encoding", "Connection", "Keep-Alive"):
            headers.pop(h, None)
        try:
            conn.request(method, upstream_path, body=body, headers=headers)
            resp = conn.getresponse()
            resp_body = resp.read()
            if resp.status != 200:
                print(f"[mm_proxy] ← {resp.status}: {resp_body[:200]!r}",
                      file=sys.stderr)
            else:
                print(f"[mm_proxy] ← {resp.status} ({len(resp_body)}B)",
                      file=sys.stderr)
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)
            conn.close()
        except Exception as e:
            print(f"[mm_proxy] upstream error: {e}", file=sys.stderr)
            self.send_error(502, f"Upstream error: {e}")

    def do_POST(self): self._forward("POST")
    def do_GET(self): self._forward("GET")


class ThreadedHTTPServer(HTTPServer):
    def __init__(self, addr, handler, upstream_url, api_key):
        handler.upstream_url = upstream_url
        handler.api_key = api_key
        super().__init__(addr, handler)
        self.daemon_threads = True


def main():
    global IMAGE_DIR
    ap = argparse.ArgumentParser(description="MM proxy: markdown to image_url")
    ap.add_argument("--port", type=int, default=9095)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--image-dir", default=None,
                    help="Directory of cached image files for /mm_image/<file> proxy URLs")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    IMAGE_DIR = args.image_dir
    server = ThreadedHTTPServer((args.host, args.port), MMProxyHandler,
                                 args.upstream, args.api_key)
    print(f"[mm_proxy] {args.host}:{args.port} -> {args.upstream} "
          f"(image_dir={IMAGE_DIR})", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[mm_proxy] shutdown", file=sys.stderr)

if __name__ == "__main__":
    main()
