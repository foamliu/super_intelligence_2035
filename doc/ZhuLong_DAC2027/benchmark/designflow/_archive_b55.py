#!/usr/bin/env python3
# Archive oldest 4 flow lines from MEMORY_B into ARCHIVE_OPERATOR_DESIGNFLOW_B.md
import re, os

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_B.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/ARCHIVE_OPERATOR_DESIGNFLOW_B.md"

lines = open(MEM).readlines()
# find the flow section start and identify the 4 oldest dated flow lines (lines starting with "- 2026-11-05 2")
# locate "## 流水" line
flow_idx = next(i for i, l in enumerate(lines) if l.startswith("## 流水"))
# collect indices of dated flow lines (start with "- 2026-11-05 " and not "[归档]")
dated = [i for i, l in enumerate(lines) if l.startswith("- 2026-11-05 ") and "[归档]" not in l]
print("dated flow lines:", len(dated), "at idx", dated)
# archive the LAST 4 (oldest, since flow is newest-first -> oldest at bottom)
to_archive = dated[-4:]  # 21:1x, 21:0x, 20:4x, 20:3x
print("archiving idx:", to_archive, "timestamps:", [lines[i][:30] for i in to_archive])

# extract their full text (each is one long line)
archived_text = "\n".join(lines[i].rstrip("\n") for i in to_archive)

# build archive batch header
batch = """
以下 4 条流水原文（2026-11-05 20:3x / 20:4x / 21:0x / 21:1x）已闭合，从 MEMORY_B 滚入此处以控体积（MEMORY_B ≤32KB 软限）。

"""
# prepend to ARCHIVE (after any header). Just append at end with a separator.
with open(ARCH, "a") as f:
    f.write("\n" + "=" * 80 + "\n")
    f.write(batch)
    f.write(archived_text + "\n")

# now remove those lines from MEMORY and insert a single pointer line at the position of the first archived
# replace the 4 lines with one pointer
ptr = "- [归档] 2026-11-05 20:3x–21:1x 流水（4 条：RonMonoDiag-001 交付 + race-damage 回退 + DEBT 清零核验 + TbMeasCheck-001 交付）原文见 ARCHIVE_OPERATOR_DESIGNFLOW_B.md 归档批次 55\n"
# build new lines: keep order, drop the 4 archived, insert pointer where the first archived was
new_lines = []
inserted = False
for i, l in enumerate(lines):
    if i in to_archive:
        if not inserted:
            new_lines.append(ptr)
            inserted = True
        continue
    new_lines.append(l)
open(MEM, "w").writelines(new_lines)
print("MEMORY_B new size:", os.path.getsize(MEM))
print("ARCHIVE new size:", os.path.getsize(ARCH))
