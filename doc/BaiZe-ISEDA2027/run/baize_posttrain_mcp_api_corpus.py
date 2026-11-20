#!/usr/bin/env python3
"""baize_posttrain_mcp_api_corpus.py — Build PyAether API reference corpus via MCP SSE.

Calls the local MCP server (eda_fastmcp, port 18888, SSE transport) get_api_details
tool for a list of API names, saves full responses to a JSONL corpus file.

Usage:
    python3 baize_posttrain_mcp_api_corpus.py --api-file pyAether_eval_apis_not_found.txt \
        --output pyAether_api_ref_mcp_enriched.jsonl --batch-size 10
    python3 baize_posttrain_mcp_api_corpus.py --help

R148 (wake216): MCP get_api_details returns richer data than static JSON
(test verification, error handling, best practices). This script enriches
the base corpus (pyAether_api_ref_488.jsonl from API_INFO_MERGED_V3.json)
with MCP-sourced entries for APIs not in the static JSON.

MCP server: ~/code/eda_fastmcp/.venv/bin/python main.py (SSE on :18888)
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

MCP_SSE_URL = "http://localhost:18888/sse"
MCP_MESSAGES_BASE = "http://localhost:18888/messages/"
TIMEOUT = 120  # seconds per API batch


def _send_msg(session_id, payload):
    """POST a JSON-RPC message to the MCP messages endpoint."""
    msg_url = MCP_MESSAGES_BASE + "?session_id=" + session_id
    req = urllib.request.Request(
        msg_url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        if e.code != 202:
            raise


def _read_response(sse_resp, msg_id, timeout=120):
    """Read a JSON-RPC response with matching id from the SSE stream."""
    deadline = time.time() + timeout
    for raw_line in sse_resp:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if line.startswith("data:"):
            data_str = line[5:].strip()
            if not data_str:
                continue
            try:
                data = json.loads(data_str)
                if data.get("id") == msg_id:
                    return data
            except json.JSONDecodeError:
                continue
        if time.time() > deadline:
            break
    return {"error": "timeout"}


def get_session_id(sse_url):
    """Connect to SSE, do MCP initialize handshake, return (resp, session_id)."""
    req = urllib.request.Request(sse_url)
    resp = urllib.request.urlopen(req, timeout=30)
    session_id = None
    for raw_line in resp:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if "session_id=" in data:
                session_id = data.split("session_id=")[-1]
                break
    if not session_id:
        raise RuntimeError("No session_id received from SSE endpoint")
    # MCP initialize handshake
    _send_msg(session_id, {
        "jsonrpc": "2.0", "method": "initialize", "id": 0,
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "corpus-builder", "version": "1.0"}}})
    _read_response(resp, 0, timeout=30)
    _send_msg(session_id, {
        "jsonrpc": "2.0", "method": "notifications/initialized"})
    time.sleep(0.5)
    return resp, session_id


def call_tool(session_id, tool_name, arguments, sse_resp, timeout=120, msg_id=1):
    """Send a JSON-RPC tools/call request and read response from SSE stream."""
    _send_msg(session_id, {
        "jsonrpc": "2.0", "method": "tools/call", "id": msg_id,
        "params": {"name": tool_name, "arguments": arguments}})
    return _read_response(sse_resp, msg_id, timeout=timeout)


def parse_api_details(result):
    """Extract API detail entries from MCP tool result."""
    if "error" in result:
        return []
    content = result.get("result", {}).get("content", [])
    entries = []
    for item in content:
        if item.get("type") == "text":
            try:
                entry = json.loads(item["text"])
                entries.append(entry)
            except json.JSONDecodeError:
                pass
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Build PyAether API corpus via MCP SSE")
    parser.add_argument("--api-file", required=True,
                        help="File with API names (one per line)")
    parser.add_argument("--output", required=True, help="Output JSONL file path")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="APIs per MCP call (default 10)")
    parser.add_argument("--mcp-url", default=MCP_SSE_URL,
                        help="MCP SSE endpoint URL")
    args = parser.parse_args()

    with open(args.api_file) as f:
        apis = [l.strip().replace("pyAether.", "") for l in f if l.strip()]
    print("Loaded {} API names from {}".format(len(apis), args.api_file))

    print("Connecting to MCP SSE at {} ...".format(args.mcp_url))
    sse_resp, session_id = get_session_id(args.mcp_url)
    print("Session: {}".format(session_id))

    results = []
    failed = []
    for i in range(0, len(apis), args.batch_size):
        batch = apis[i:i + args.batch_size]
        print("  Batch {}: {} APIs ({}...)".format(
            i // args.batch_size + 1, len(batch), batch[0]))
        try:
            result = call_tool(session_id, "get_api_details",
                               {"api_list": batch}, sse_resp, timeout=TIMEOUT,
                               msg_id=i // args.batch_size + 1)
            entries = parse_api_details(result)
            if entries:
                results.extend(entries)
                print("    -> {} entries retrieved".format(len(entries)))
            else:
                print("    -> no entries (keys: {})".format(
                    list(result.keys())))
                failed.extend(batch)
        except Exception as e:
            print("    -> ERROR: {}".format(e))
            failed.extend(batch)
            try:
                sse_resp.close()
            except Exception:
                pass
            time.sleep(2)
            try:
                sse_resp, session_id = get_session_id(args.mcp_url)
                print("    reconnected, session: {}".format(session_id))
            except Exception as re_err:
                print("    reconnect failed: {}".format(re_err))
                break

    with open(args.output, "w") as f:
        for entry in results:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    total_chars = sum(len(e.get("api_descriptions", "")) for e in results)
    print("\nSaved {} entries to {}".format(len(results), args.output))
    print("File size: {} bytes".format(os.path.getsize(args.output)))
    print("Total chars: {} (~{} tokens)".format(total_chars, total_chars // 4))
    if failed:
        fail_path = args.output + ".failed.txt"
        with open(fail_path, "w") as f:
            for a in failed:
                f.write(a + "\n")
        print("Failed: {} APIs -> {}".format(len(failed), fail_path))
    try:
        sse_resp.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
