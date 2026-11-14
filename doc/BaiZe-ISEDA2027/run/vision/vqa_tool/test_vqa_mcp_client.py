#!/usr/bin/env python3
"""End-to-end smoke test for the Qwen3.5-2B VQA MCP server.

Speaks MCP streamableHttp as a real client (using the `mcp` SDK client) and calls
the `vqa` tool on a restored WAVEVIEW PNG, proving the wrapper is callable the
same way cline will call it.

  python test_vqa_mcp_client.py \
      --url http://10.252.32.17:30002/mcp \
      --image /nas_data/.../wv_sigs_A.png \
      --query "How many signals are shown in this waveform plot?"
"""
import argparse
import asyncio
import json
import sys

from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession


async def run(url, image_path, query, max_new_tokens, temperature):
    async with streamablehttp_client(url) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print("[client] initialized:", init.serverInfo.name
                  if init and init.serverInfo else "?")
            tools = await session.list_tools()
            print("[client] tools:", [t.name for t in tools.tools])
            res = await session.call_tool(
                "vqa",
                {"image_path": image_path, "query": query,
                 "max_new_tokens": max_new_tokens, "temperature": temperature},
            )
            # result.content is a list of content blocks; join text blocks
            parts = []
            for block in (res.content or []):
                txt = getattr(block, "text", None)
                if txt is not None:
                    parts.append(txt)
            print("[client] isError:", bool(res.isError))
            print("[client] answer:", "\n".join(parts))
            return ("\n".join(parts), bool(res.isError))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://10.252.32.17:30002/mcp")
    ap.add_argument("--image", required=True)
    ap.add_argument("--query", "-q", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=512)
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()
    answer, is_err = asyncio.run(
        run(args.url, args.image, args.query, args.max_new_tokens, args.temperature))
    sys.exit(1 if is_err or answer.startswith("VQA ERROR") else 0)


if __name__ == "__main__":
    main()
