#!/usr/bin/env python3
"""Qwen3.5-2B VQA **MCP** server (vision line · 用户令 2026-11-14 09:1x #3, task2 解阻).

Wraps the Qwen3.5-2B VQA HTTP server (`qwen35_vqa_server.py`) as an MCP
`streamableHttp` server so **cline** (running on the designflow eval machine)
can call a `vqa(image_path, query)` tool — exactly the architecture proposed by
designflow convenor shard A in `WAVEVIEW_COLLAB.md` r529.

Why MCP (not plain HTTP): cline's tool surface is MCP; its MCP client connects to
MCP servers via URL. Exposing Qwen3.5-2B as an MCP `vqa` tool lets designflow add
one entry to `cline_mcp_settings.json` and re-run the same 10 restored WAVEVIEW
cases with **唯一变量 = cline 能否调 VQA** (the #3 official comparison).

Why Qwen3.5-2B (not the existing `research.vqa` MCP): 用户令 #3/#4 explicitly
target Qwen3.5-2B, and #4 strengthens the **base model** — you cannot strengthen
`research.vqa`'s opaque backend. So the strict #3/#4 measurement must use
Qwen3.5-2B. (`research.vqa` may optionally serve as a separate upper-bound run.)

Tool:
  vqa(image_path: str, query: str, max_new_tokens: int = 512, temperature: float = 0.0) -> str
    image_path : absolute path to a PNG on the **shared NFS** (the designflow eval
                 machine `10.251.36.15` and this GPU machine `10.252.32.17` mount
                 the same NFS, so pass the NFS path directly — no base64 needed).
    query      : the visual question, e.g.
                 "How many rising edges are in the clk signal across [0,10ns]?"
    Returns the model's answer as plain text. On error returns "VQA ERROR: ...".

Run on the vision GPU machine (10.252.32.17):
  /nas_data/app.e0031982/miniforge3/envs/py310/bin/python \\
      qwen35_vqa_mcp_server.py --host 0.0.0.0 --port 30002 \\
      --vqa-server http://127.0.0.1:30001

cline MCP config (on the designflow eval machine, 10.251.36.15):
  "qwen35_vqa": {
    "url": "http://10.252.32.17:30002/mcp",
    "type": "streamableHttp",
    "timeout": 600,
    "disabled": false,
    "autoApprove": ["vqa"]
  }

Reachability: requires the eval machine (10.251.36.15) to reach
10.252.32.17:30002 over TCP. If a firewall blocks it, either (a) open the rule,
or (b) run THIS wrapper on the eval machine with `--vqa-server
http://10.252.32.17:30001` (which requires the VQA HTTP server to be rebound to
0.0.0.0:30001 — done by relaunching `qwen35_vqa_server.py --host 0.0.0.0`).
"""
import argparse
import json
import os
import urllib.request

from mcp.server.fastmcp import FastMCP

DEFAULT_VQA_SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")


def _vqa_call(vqa_server, image_path, query, max_new_tokens, temperature, timeout=300):
    """Forward one VQA request to the Qwen3.5-2B HTTP server; return answer text."""
    body = {
        "image_path": image_path,
        "question": query,
        "max_new_tokens": int(max_new_tokens),
        "temperature": float(temperature),
    }
    req = urllib.request.Request(
        vqa_server.rstrip("/") + "/vqa",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.loads(r.read())
    if not res.get("ok"):
        return f"VQA ERROR: {res.get('error')}"
    ans = res.get("answer", "")
    elapsed = res.get("elapsed_s")
    return ans if elapsed is None else f"{ans}\n[vqa elapsed_s={elapsed}]"


def make_server(vqa_server, host="0.0.0.0", port=30002):
    mcp = FastMCP(
        name="qwen35-vqa",
        instructions=(
            "Qwen3.5-2B visual question answering over waveform/EDA PNG images. "
            "Call vqa(image_path, query) with an ABSOLUTE NFS path to the image and "
            "a natural-language question; the tool returns the model's answer text. "
            "Use this to read values/shapes from waveform screenshots that a "
            "text-only model cannot see."
        ),
        host=host,
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )

    @mcp.tool()
    def vqa(
        image_path: str,
        query: str,
        max_new_tokens: int = 512,
        temperature: float = 0.0,
    ) -> str:
        """Answer a visual question about an image using Qwen3.5-2B (vision-language).

        Args:
            image_path: absolute path to the image file on the shared NFS
                (e.g. /nas_data/.../EDA-Eval-DesignFlow-WaveView-002/assets/wv_sigs_A.png).
            query: the visual question to answer (e.g. "How many rising edges in the clk signal?").
            max_new_tokens: maximum generation length (default 512).
            temperature: sampling temperature; 0.0 = greedy/deterministic (default).

        Returns:
            The model's answer as plain text. On tool/server error returns a
            string beginning with "VQA ERROR:".
        """
        try:
            return _vqa_call(
                vqa_server, image_path, query, max_new_tokens, temperature
            )
        except Exception as e:  # never raise — surface error as text to the LLM
            return f"VQA ERROR: {e}"

    return mcp


def main():
    ap = argparse.ArgumentParser(description="Qwen3.5-2B VQA MCP (streamableHttp) server")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=30002)
    ap.add_argument("--vqa-server", default=DEFAULT_VQA_SERVER,
                    help="upstream Qwen3.5-2B VQA HTTP server (default http://127.0.0.1:30001)")
    args = ap.parse_args()

    import uvicorn

    mcp = make_server(args.vqa_server, host=args.host, port=args.port)
    app = mcp.streamable_http_app()
    print(
        f"[qwen35-vqa-mcp] streamableHttp MCP on http://{args.host}:{args.port}/mcp "
        f"(stateless, json_response)  ->  upstream {args.vqa_server}/vqa",
        flush=True,
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
