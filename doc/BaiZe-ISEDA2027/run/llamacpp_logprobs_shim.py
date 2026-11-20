#!/usr/bin/env python3
"""Lightweight HTTP proxy that converts llama-server's new OpenAI logprobs format
to the old format expected by lm_eval's GGUFLM model.

llama-server (build 149f5641b) returns:
  choices[0].logprobs = {"content": [{"token": " the", "logprob": -4.2, "top_logprobs": [...]}]}

lm_eval GGUFLM (0.4.13) expects:
  choices[0].logprobs = {"text_offset": [0, 4, ...], "tokens": ["The", " capital", ...],
                          "token_logprobs": [-0.1, -4.2, ...],
                          "top_logprobs": [{"The": -0.1, ...}, ...]}

Usage:
  python llamacpp_logprobs_shim.py --listen 30013 --upstream http://127.0.0.1:30012
  # Then point lm_eval at: --model_args base_url=http://127.0.0.1:30013/v1
"""
import sys, os, json, argparse, time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

UPSTREAM = "http://127.0.0.1:30012"

def convert_logprobs(new_lp):
    """Convert new OpenAI logprobs format to old format."""
    if new_lp is None:
        return None
    content = new_lp.get("content")
    if content is None:
        return new_lp  # already old format or unknown

    tokens = []
    token_logprobs = []
    top_logprobs = []
    text_offset = []
    pos = 0
    for item in content:
        tok_str = item.get("token", "")
        logprob = item.get("logprob", 0.0)
        tokens.append(tok_str)
        token_logprobs.append(logprob)
        text_offset.append(pos)
        pos += len(tok_str)
        # Convert top_logprobs from array-of-objects to dict {token: logprob}
        tp_dict = {}
        for tp in item.get("top_logprobs", []):
            tp_dict[tp.get("token", "")] = tp.get("logprob", 0.0)
        top_logprobs.append(tp_dict)

    return {
        "text_offset": text_offset,
        "tokens": tokens,
        "token_logprobs": token_logprobs,
        "top_logprobs": top_logprobs,
    }


class ShimHandler(BaseHTTPRequestHandler):
    def _proxy(self, method):
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Build upstream request
        url = UPSTREAM + self.path
        req = urllib.request.Request(url, data=body if body else None, method=method)
        for h in ["Content-Type", "Authorization"]:
            v = self.headers.get(h)
            if v:
                req.add_header(h, v)

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp_body = resp.read()
                resp_type = resp.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
            return
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # For /v1/completions responses, convert logprobs
        if "/v1/completions" in self.path and resp_type.startswith("application/json"):
            try:
                data = json.loads(resp_body)
                for choice in data.get("choices", []):
                    if "logprobs" in choice and choice["logprobs"] is not None:
                        choice["logprobs"] = convert_logprobs(choice["logprobs"])
                resp_body = json.dumps(data).encode()
            except (json.JSONDecodeError, KeyError) as e:
                sys.stderr.write(f"[shim] WARNING: failed to convert logprobs: {e}\n")

        self.send_response(200)
        self.send_header("Content-Type", resp_type)
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)

    def do_POST(self):
        self._proxy("POST")

    def do_GET(self):
        self._proxy("GET")

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[shim] {self.address_string()} {fmt % args}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", type=int, default=30013)
    parser.add_argument("--upstream", default="http://127.0.0.1:30012")
    args = parser.parse_args()
    global UPSTREAM
    UPSTREAM = args.upstream.rstrip("/")
    server = HTTPServer(("0.0.0.0", args.listen), ShimHandler)
    sys.stderr.write(f"[shim] listening on :{args.listen} → upstream {UPSTREAM}\n")
    sys.stderr.flush()
    server.serve_forever()


if __name__ == "__main__":
    main()
