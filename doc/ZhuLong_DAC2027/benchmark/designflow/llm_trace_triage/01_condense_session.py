#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_condense_session.py — 把 messages.json 压成 <=N 字符的 triage 文本。

用法:
  python3 01_condense_session.py <messages.json> [--out out.txt] [--max-chars 6000]

兼容:
  - 顶层 list / {"messages": [...]} / {"conversation": [...]}
  - content 为 str 或 block list（type=text/tool_use/tool_result）
  - 工具调用字段: name/input.command、input.cmd、input.file_path、input.path、input.pattern 等

输出结构:
  SESSION
  [user] ...
  [assistant] ...
  [cmd] tool: <command or path>
  ...
"""
import argparse
import json
import os
import re
import sys

MAX_ITEM = 400


def norm(s):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s[:MAX_ITEM]


def load_messages(path):
    d = json.load(open(path, encoding="utf-8", errors="ignore"))
    if isinstance(d, list):
        return d
    if isinstance(d, dict):
        for k in ("messages", "conversation", "history", "data"):
            v = d.get(k)
            if isinstance(v, list):
                return v
        # 有些导出是 {sid: {...}}
        for v in d.values():
            if isinstance(v, dict) and isinstance(v.get("messages"), list):
                return v["messages"]
    raise SystemExit(f"无法识别的 messages 结构: {path}")


def blocks(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return [("text", c)]
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, str):
                out.append(("text", b))
            elif isinstance(b, dict):
                t = b.get("type") or ""
                if t in ("text", "input_text", "output_text"):
                    out.append(("text", b.get("text") or b.get("content") or ""))
                elif t in ("tool_use", "tool_call", "function_call"):
                    inp = b.get("input") or b.get("arguments") or {}
                    if isinstance(inp, str):
                        try:
                            inp = json.loads(inp)
                        except Exception:
                            inp = {"raw": inp}
                    out.append(("tool", inp))
                elif t in ("tool_result", "tool_response"):
                    out.append(("result", b.get("content") or b.get("output") or ""))
    return out


def tool_line(inp):
    if not isinstance(inp, dict):
        return norm(inp)
    for k in ("command", "cmd", "shell", "script"):
        if inp.get(k):
            return "cmd: " + norm(inp[k])
    for k in ("file_path", "path", "filename", "target_file"):
        if inp.get(k):
            return "file: " + norm(inp[k])
    if inp.get("pattern"):
        return "grep: " + norm(inp["pattern"])
    # 兜底：最多 3 个短字段
    parts = []
    for k, v in list(inp.items())[:3]:
        if isinstance(v, (str, int, float)):
            parts.append(f"{k}={norm(v)}")
    return "args: " + "; ".join(parts)


def condense(path, max_chars):
    msgs = load_messages(path)
    users, assists, tools, results = [], [], [], []
    for m in msgs:
        if not isinstance(m, dict):
            continue
        role = (m.get("role") or m.get("type") or "?").lower()
        for kind, val in blocks(m):
            if kind == "text":
                txt = norm(val)
                if not txt:
                    continue
                if role in ("user", "human"):
                    users.append(txt)
                elif role in ("assistant", "ai", "model"):
                    assists.append(txt)
            elif kind == "tool":
                line = tool_line(val)
                if line and line not in tools:
                    tools.append(line)
            elif kind == "result":
                results.append(norm(val))

    # 只保留代表性片段：前 6 条 user、全部命令（最多 40）、后 4 条 assistant
    parts = ["SESSION", f"msgs={len(msgs)} user={len(users)} assistant={len(assists)} tools={len(tools)}"]
    for u in users[:6]:
        parts.append("[user] " + u)
    for t in tools[:40]:
        parts.append("[cmd] " + t)
    for a in assists[-4:]:
        parts.append("[assistant] " + a)
    if results:
        parts.append("[tool_result_sample] " + results[0])

    text = "\n".join(parts)
    if len(text) > max_chars:
        text = text[: max_chars - 40] + "\n...[TRUNCATED]"
    return text, {"msgs": len(msgs), "users": len(users), "assistant": len(assists),
                  "tools": len(tools), "chars": len(text)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("messages_json")
    ap.add_argument("--out", default="")
    ap.add_argument("--max-chars", type=int, default=6000)
    args = ap.parse_args()
    text, stat = condense(args.messages_json, args.max_chars)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(json.dumps({"out": args.out, **stat}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
