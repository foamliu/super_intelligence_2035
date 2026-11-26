#!/usr/bin/env python3
"""Archive r148 entry to MEMORY_C_archive (batch 154) to bring MEMORY_C under 32KB."""
import os

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_C.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/MEMORY_C_archive.md"

lines = open(MEM).read().splitlines()
idx = None
for i, ln in enumerate(lines):
    if ln.startswith("- **轮(148)"):
        idx = i; break
assert idx is not None
r148_text = lines[idx]

arch = open(ARCH).read()
arch += "\n\n## 归档批次 154b (r154 轮追加归档 r148)\n\n" + r148_text + "\n"
open(ARCH, "w").write(arch)

lines[idx] = "- 轮(148) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SvrfHandbookPaginate-001, physical_verify；归档批次 154b；详细见归档）"
out = "\n".join(lines) + "\n"
open(MEM, "w").write(out)
print("MEMORY_C bytes:", len(out.encode()))
