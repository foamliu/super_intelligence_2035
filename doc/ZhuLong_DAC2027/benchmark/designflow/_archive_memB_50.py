#!/usr/bin/env python3
"""Archive the 2 oldest流水 lines from MEMORY_B to ARCHIVE, replace with 1-line pointer."""
import os
PATH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark"
MEM = PATH + "/MEMORY_DESIGNFLOW_B.md"
ARCH = PATH + "/ARCHIVE_OPERATOR_DESIGNFLOW_B.md"
mem = open(MEM).read()
lines = mem.split("\n")
idxs = [i for i,l in enumerate(lines) if l.startswith("- 2026-11-05 11:")]
toArchive = idxs[-2:]  # last two = oldest
archived = [lines[i] for i in toArchive]
# append原文 to ARCHIVE
block = "\n\n## 归档批次 50 (2026-11-05 15:4x) — MEMORY_B 流水原文搬迁\n" + "\n".join(archived) + "\n"
open(ARCH, "a").write(block)
# replace in MEM
pointer = "- [归档] 2026-11-05 11:0x–11:2x 流水（PostsimToggleDiag-001 交付 + 11:2x 收尾校验/scouting）原文见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md 归档批次 50"
firstIdx = toArchive[0]
# remove higher idx first
del lines[toArchive[1]]
del lines[toArchive[0]]
lines.insert(firstIdx, pointer)
mem = "\n".join(lines)
open(MEM, "w").write(mem)
sz = len(mem.encode("utf-8"))
print(f"archived {len(archived)} lines; MEMORY_B now {sz} bytes = {sz/1024:.1f}KB")
