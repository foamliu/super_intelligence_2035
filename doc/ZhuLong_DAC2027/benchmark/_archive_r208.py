#!/usr/bin/env python3
"""Archive r207 + r206 流水 lines from MEMORY_DESIGNFLOW_A.md to keep <32KB."""
import os, re

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_A.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_A_archive.md"

with open(MEM) as f:
    lines = f.readlines()

# find r207 and r206 流水 lines (start with "> 轮 r207 流水" / "> 轮 r206 流水")
to_archive = {}
new_lines = []
for ln in lines:
    stripped = ln.lstrip("> ").strip()
    if stripped.startswith("轮 r207 流水"):
        to_archive["r207"] = ln
        new_lines.append("> 轮 r207 流水已归档至 MEMORY_A_archive.md（归档批次 111，2026-11-07 轮 r208 体积维护）。摘要：r207 EDA-Eval-DesignFlow-DcUpfPgDiagnose-001 · 1 case · 无 cline 实跑 · covered 125→126 · WAITING:0\n")
    elif stripped.startswith("轮 r206 流水"):
        to_archive["r206"] = ln
        new_lines.append("> 轮 r206 流水已归档至 MEMORY_A_archive.md（归档批次 111，2026-11-07 轮 r208 体积维护）。摘要：r206 scansync 到期(数字一致无新扫描) + gs5dr A档 faithful 合成交付 RtlSimfixVerdict-001 · 1 case · 无 cline 实跑 · covered 123→124 · WAITING:0\n")
    else:
        new_lines.append(ln)

# append archived lines to archive file
with open(ARCH, "a") as f:
    f.write("\n\n## 归档批次 111（2026-11-07 轮 r208 体积维护）\n")
    for key in ["r207", "r206"]:
        if key in to_archive:
            f.write("\n" + to_archive[key].rstrip("\n") + "\n")

with open(MEM, "w") as f:
    f.writelines(new_lines)

print("archived:", list(to_archive.keys()))
print("MEMORY new size:", os.path.getsize(MEM), "bytes")
