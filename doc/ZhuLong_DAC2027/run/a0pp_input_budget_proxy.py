#!/usr/bin/env python3
"""
a0pp_input_budget_proxy.py — Truncation proxy to enforce 8K input budget.

PROBLEM (smoke-proven 2026-11-16 wake#1011):
  cline 3.0.51 ignores models.json contextWindow/maxInputTokens for openai-compatible
  custom models. Compaction triggers at 0.9×128K=115.2K, NOT at 0.9×8K=7.2K.
  inputTokens=233K observed → maxInputTokens=8000 NOT enforced either.
  => A0'' cannot enforce 8K input budget via cline config alone.

SOLUTION:
  This proxy sits between cline and the real API. It truncates the `messages`
  array in each /v1/chat/completions request to fit within INPUT_BUDGET tokens,
  keeping the system prompt + the most recent messages (with tool_call/result
  pairs kept intact). This simulates a small context window.

USAGE:
  1. Start proxy:  python3 a0pp_input_budget_proxy.py --port 18080
  2. Point cline's baseUrl to http://localhost:18080/v1 (in providers.json)
  3. Proxy forwards to UPSTREAM_URL (default: agi-gateway.cxmt.com/cloud/v1)

TOKEN ESTIMATION:
  Simple heuristic: 1 token ≈ 4 chars (English/code). Good enough for
  truncation decisions; exact count not needed (we truncate to 90% of budget
  for safety margin).

TRUNCATION STRATEGY:
  - Always keep message[0] (system prompt).
  - Group subsequent messages: an assistant msg with tool_calls + its tool
    result msgs form an inseparable "group".
  - Keep groups from the END (most recent) until adding another would exceed
    0.9 × INPUT_BUDGET tokens. Drop older groups.
  - If a single group exceeds the budget, keep it anyway (can't split pairs).

NOTES:
  - Supports streaming (SSE) responses — just pipes bytes through.
  - Does NOT modify non-chat endpoints (e.g., /v1/models) — passes through.
  - Logs truncation events to stderr for traceability.
"""
import sys
import json
import argparse
import http.server
import socketserver
import urllib.request
import urllib.error
import ssl
from typing import List, Dict, Any, Tuple

# ThreadingHTTPServer so concurrent cline workers don't block each other
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

# ---- config ----
INPUT_BUDGET = 8000          # tokens (the 8K input budget per 09:0x order)
KEEP_RATIO = 0.9             # keep 90% of budget → truncate at 7200 tokens
CHARS_PER_TOKEN = 4          # estimation heuristic
UPSTREAM_URL = "http://agi-gateway.cxmt.com/cloud/v1"

# ---- token estimation ----
def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return len(text) // CHARS_PER_TOKEN

def msg_token_count(msg: Dict[str, Any]) -> int:
    """Estimate token count of a single message (content + tool_calls + etc)."""
    # serialize and measure — rough but sufficient
    return estimate_tokens(json.dumps(msg, ensure_ascii=False))

def total_tokens(msgs: List[Dict[str, Any]]) -> int:
    return sum(msg_token_count(m) for m in msgs)

# ---- message grouping ----
def group_messages(msgs: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Group messages keeping tool_call/result pairs together.
    Group boundaries:
      - A new group starts at each 'user' or 'assistant' message that does NOT
        have tool_calls (i.e., a new conversational turn).
      - Tool result messages (role='tool') attach to the preceding assistant group.
      - Assistant messages WITH tool_calls start a group that includes subsequent
        'tool' messages.
    """
    groups: List[List[Dict[str, Any]]] = []
    current: List[Dict[str, Any]] = []
    for m in msgs:
        role = m.get("role", "")
        has_tool_calls = bool(m.get("tool_calls"))
        if role == "tool":
            # attach to current group (the assistant that issued the tool_call)
            current.append(m)
        elif role == "assistant" and has_tool_calls:
            # start new group if current is non-empty
            if current:
                groups.append(current)
            current = [m]
        else:
            # user or plain assistant — new group
            if current:
                groups.append(current)
            current = [m]
    if current:
        groups.append(current)
    return groups

# ---- truncation ----
def truncate_messages(msgs: List[Dict[str, Any]], budget_tokens: int) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Truncate messages to fit within budget_tokens.
    Keeps message[0] (system) + most recent groups.
    Returns (truncated_msgs, original_tokens, truncated_tokens).
    """
    orig_tokens = total_tokens(msgs)
    if orig_tokens <= budget_tokens:
        return msgs, orig_tokens, orig_tokens

    if not msgs:
        return msgs, 0, 0

    # Always keep first message (system prompt)
    system = msgs[0] if msgs[0].get("role") == "system" else None
    rest = msgs[1:] if system else msgs

    system_tokens = msg_token_count(system) if system else 0
    remaining_budget = budget_tokens - system_tokens

    # Group the rest
    groups = group_messages(rest)

    # Keep groups from the END until budget exceeded
    kept: List[List[Dict[str, Any]]] = []
    used = 0
    for grp in reversed(groups):
        grp_tokens = sum(msg_token_count(m) for m in grp)
        if used + grp_tokens > remaining_budget and kept:
            # would exceed budget and we already have some groups — stop
            break
        kept.insert(0, grp)
        used += grp_tokens
        if used >= remaining_budget:
            break

    # Reassemble
    result: List[Dict[str, Any]] = []
    if system:
        result.append(system)
    for grp in kept:
        result.extend(grp)

    trunc_tokens = total_tokens(result)
    return result, orig_tokens, trunc_tokens

# ---- HTTP proxy ----
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # log to stderr
        print(f"[proxy] {self.address_string()} - {fmt % args}", file=sys.stderr)

    def _forward(self, method: str):
        # Build upstream URL
        path = self.path
        upstream = UPSTREAM_URL.rstrip("/") + path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Truncate messages if this is a chat completions request
        trunc_info = ""
        if "/chat/completions" in path and body:
            try:
                data = json.loads(body)
                msgs = data.get("messages", [])
                orig_toks = total_tokens(msgs)
                budget = int(INPUT_BUDGET * KEEP_RATIO)
                trunc_msgs, orig_t, trunc_t = truncate_messages(msgs, budget)
                data["messages"] = trunc_msgs
                body = json.dumps(data).encode("utf-8")
                if len(trunc_msgs) < len(msgs):
                    trunc_info = f"TRUNCATED {len(msgs)}→{len(trunc_msgs)} msgs, {orig_t}→{trunc_t} tokens (budget={budget})"
                    print(f"[proxy] {trunc_info}", file=sys.stderr)
                else:
                    print(f"[proxy] passthrough {len(msgs)} msgs, {orig_t} tokens (within budget={budget})", file=sys.stderr)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[proxy] WARN: could not parse body for truncation: {e}", file=sys.stderr)

        # Prepare upstream request
        req = urllib.request.Request(upstream, data=body if body else None, method=method)
        # Copy relevant headers
        for hdr in ["Content-Type", "Authorization", "Accept"]:
            val = self.headers.get(hdr)
            if val:
                req.add_header(hdr, val)
        if body:
            req.add_header("Content-Length", str(len(body)))

        # Check if streaming requested
        is_stream = False
        if body:
            try:
                is_stream = json.loads(body).get("stream", False)
            except Exception:
                pass

        try:
            resp = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
            return
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"proxy error: {e}".encode())
            return

        # Forward response
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            if k.lower() not in ("transfer-encoding", "connection"):
                self.send_header(k, v)
        self.end_headers()

        if is_stream:
            # Pipe streaming response
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        else:
            self.wfile.write(resp.read())

    def do_POST(self):
        self._forward("POST")

    def do_GET(self):
        self._forward("GET")

def main():
    global INPUT_BUDGET, UPSTREAM_URL
    parser = argparse.ArgumentParser(description="Input budget truncation proxy for A0'' ablation")
    parser.add_argument("--port", type=int, default=18080, help="Port to listen on")
    parser.add_argument("--budget", type=int, default=INPUT_BUDGET, help="Input budget in tokens")
    parser.add_argument("--upstream", type=str, default=UPSTREAM_URL, help="Upstream API URL")
    args = parser.parse_args()

    INPUT_BUDGET = args.budget
    UPSTREAM_URL = args.upstream

    server = ThreadingHTTPServer(("127.0.0.1", args.port), ProxyHandler)
    print(f"[proxy] Input budget truncation proxy", file=sys.stderr)
    print(f"[proxy] Listening on http://127.0.0.1:{args.port}", file=sys.stderr)
    print(f"[proxy] Upstream: {UPSTREAM_URL}", file=sys.stderr)
    print(f"[proxy] Input budget: {INPUT_BUDGET} tokens (truncate at {int(INPUT_BUDGET*KEEP_RATIO)})", file=sys.stderr)
    print(f"[proxy] Point cline baseUrl to: http://127.0.0.1:{args.port}/v1", file=sys.stderr)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[proxy] shutting down", file=sys.stderr)
        server.shutdown()

if __name__ == "__main__":
    main()
