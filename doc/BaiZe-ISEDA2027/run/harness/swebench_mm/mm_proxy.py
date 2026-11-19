#!/usr/bin/env python3
"""MM proxy: converts markdown-embedded base64 images to OpenAI image_url content.

Sits between cline CLI and the gateway.  cline passes the initial task as text
(including markdown image tags with data: URLs).  This proxy intercepts the
chat completion request, extracts data: URLs from markdown image tags in the
first user message, and converts to multimodal format:
  [{type:text, text:...}, {type:image_url, image_url:{url:data:...}}]
"""
from __future__ import annotations
import argparse, http.client, json, re, sys, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

MD_IMG_RE = re.compile(
    r'!\[[^\]]*\]\(data:(image/[a-z]+);base64,([A-Za-z0-9+/=]+)\)')


def convert_message_content(content):
    """If content is a string with markdown data:image tags, convert to multimodal."""
    if not isinstance(content, str):
        return content
    matches = list(MD_IMG_RE.finditer(content))
    if not matches:
        return content
    parts = []
    last_end = 0
    for m in matches:
        text_before = content[last_end:m.start()].strip()
        if text_before:
            parts.append({"type": "text", "text": text_before})
        parts.append({"type": "image_url",
                       "image_url": {"url": f"data:{m.group(1)};base64,{m.group(2)}"}})
        last_end = m.end()
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
        upstream_path = parsed.path.rstrip("/") + self.path
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
    ap = argparse.ArgumentParser(description="MM proxy: markdown to image_url")
    ap.add_argument("--port", type=int, default=9095)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadedHTTPServer((args.host, args.port), MMProxyHandler,
                                 args.upstream, args.api_key)
    print(f"[mm_proxy] {args.host}:{args.port} -> {args.upstream}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[mm_proxy] shutdown", file=sys.stderr)

if __name__ == "__main__":
    main()
