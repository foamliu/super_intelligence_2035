#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第八十九轮：按 MEMORY_RESEARCH.md §3 把最旧的流水条目（第八十七轮）滚动归档到
daily-memories-research/2026-10-11.md，并更新归档指针行。"""
import io, re

MEM = "MEMORY_RESEARCH.md"
DAY = "daily-memories-research/2026-10-11.md"

mem = io.open(MEM, encoding="utf-8").read()

# 1) 抽取第八十七轮流水条目（从 '- **2026-10-11（本地 18:00 时窗）**' 到其后首个空行）
start = mem.index("- **2026-10-11（本地 18:00 时窗）**")
end = mem.index("\n\n", start)
entry = mem[start:end]
assert "第八十七轮" in entry, "wrong entry captured"

# 2) 从 MEMORY 中删除该条目（连同其后的一个空行）
mem2 = mem[:start] + mem[end + 2:]  # 删掉条目 + 一个换行（保留一个空行分隔）

# 3) 更新归档指针行
mem2 = mem2.replace("第四十七 ~ 第八十六轮", "第四十七 ~ 第八十七轮")
mem2 = mem2.replace(
    "`2026-10-11.md`（含第八十六轮条目，2026-10-12 滚动）",
    "`2026-10-11.md`（含第八十六 / 八十七轮条目，2026-10-12 滚动）")

io.open(MEM, "w", encoding="utf-8").write(mem2)

# 4) 追加到当日文件归档小节
day = io.open(DAY, encoding="utf-8").read()
if "归档 · MEMORY 滚动（2026-10-12 第八十九轮唤醒时执行）" not in day:
    block = ("\n## 归档 · MEMORY 滚动（2026-10-12 第八十九轮唤醒时执行）\n\n"
             "> 承接上节：本节的第八十七轮流水条目于 **第八十九轮唤醒** 时自 `MEMORY_RESEARCH.md` 滚动至此。\n\n"
             + entry + "\n")
    day = day.rstrip("\n") + "\n" + block
io.open(DAY, "w", encoding="utf-8").write(day)

print("MEM bytes:", len(mem2.encode("utf-8")))
