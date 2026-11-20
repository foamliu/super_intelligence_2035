#!/usr/bin/env python3
"""Archive r885 + r886 from MEMORY_DESIGNFLOW_C.md to MEMORY_C_archive.md (batch r887)."""
import re, pathlib, sys

MEM = pathlib.Path("MEMORY_DESIGNFLOW_C.md")
ARC = pathlib.Path("MEMORY_C_archive.md")

text = MEM.read_text(encoding="utf-8")
lines = text.split("\n")

def find_entry(prefix, lineno_pat):
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            return i, ln
    return -1, None

i885, e885 = find_entry("> **轮(885)", None)
i886, e886 = find_entry("> **轮(886)", None)
assert i885 >= 0 and i886 >= 0, f"i885={i885} i886={i886}"

# Build archive block
arc_block = []
arc_block.append("\n## 归档批次 r887（2026-11-21，第二轮：r885 + r886 移入）\n")
arc_block.append(f"_{e885}\n")
arc_block.append("")
arc_block.append(f"_{e886}\n")
arc_block.append("")

with ARC.open("a", encoding="utf-8") as f:
    f.write("\n".join(arc_block))

# Replace entries in MEMORY_C with 1-line pointers
ptr885 = "> 轮(885) 已归档至 MEMORY_C_archive.md（归档批次 r887 第二轮，2026-11-21）。[摘要: 1 new case c9l2c · pg_layout + 档 B reframe dont_touch cell audit 静态解析器 DontTouchCellAudit-001 落库 · k=15 · ref PASS + 3 neg FAIL distinct · roundtrip sha256 39ba238e ✓ · C 域 pg_layout dont_touch 路径审计 reframe 子型首例]"
ptr886 = "> 轮(886) 已归档至 MEMORY_C_archive.md（归档批次 r887 第二轮，2026-11-21）。[摘要: 0-case · 🚨 cross-shard collision blocker (33zw1 已被 shard D 建为 NetPathHL-001) → 全量回滚 C.jsonl 562→561；fresh C-domain triage 7ypz6/0dml6/1s79t/6f9zc 均非 C-domain；discuss mandatory r886 顺延 r887；33zw1 collision 教训：选料前必先 `grep <sid> trace_ledger_{A,B,C,D}.tsv` 跨 shard 去重]"

lines[i885] = ptr885
lines[i886] = ptr886

new_text = "\n".join(lines)
MEM.write_text(new_text, encoding="utf-8")

# verify size
size = MEM.stat().st_size
print(f"MEMORY_C size after archive: {size} bytes", file=sys.stderr)
print(f"under 32KB red line: {size < 32768}", file=sys.stderr)
assert size < 32768, f"MEMORY_C still {size} bytes > 32KB"
print("done", file=sys.stderr)
