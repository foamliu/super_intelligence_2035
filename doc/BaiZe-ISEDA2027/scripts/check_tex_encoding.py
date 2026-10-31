#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TeX 源文件编码自检（2026-10-31）。

背景：中文 Windows 编辑器（记事本 / 老版 IDE）在没有 BOM 时会按 GBK 解码 UTF-8，
把 `% 中文：...` 双语注释显示成乱码。项目约定：**BaiZe 论文的所有 .tex 必须
UTF-8-with-BOM + LF/CRLF 一致 + 无替换字符**。

用法（在 doc/BaiZe-ISEDA2027 下）：
    python scripts/check_tex_encoding.py [--fix]

退出码：0 = 全部合规；1 = 有问题（--fix 可自动补 BOM）。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "BaiZe-ISEDA2027"
BOM = b"\xef\xbb\xbf"


def check(path: Path, fix: bool):
    raw = path.read_bytes()
    problems = []
    has_bom = raw.startswith(BOM)
    if not has_bom:
        problems.append("no BOM")
        if fix:
            path.write_bytes(BOM + raw)
            raw = BOM + raw
            has_bom = True
    body = raw[3:] if has_bom else raw
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        problems.append(f"invalid UTF-8 ({exc.start})")
        return problems
    if "\ufffd" in text:
        problems.append(f"U+FFFD x{text.count(chr(0xFFFD))}")
    if "\r" in text.replace("\r\n", ""):
        problems.append("lone CR")
    if not text.endswith("\n"):
        problems.append("no trailing newline")
        if fix:
            with path.open("ab") as fh:
                fh.write(b"\n")
    return problems


def main():
    fix = "--fix" in sys.argv
    files = sorted({p.resolve() for p in list(ROOT.rglob("*.tex")) + [ROOT / "main.tex"]})
    bad = 0
    for f in files:
        if not f.exists():
            continue
        problems = check(f, fix)
        if problems:
            bad += 1
            print(f"[FAIL] {f.relative_to(ROOT.parent)}: {', '.join(problems)}")
        else:
            print(f"[ OK ] {f.relative_to(ROOT.parent)}")
    print(f"\n{len(files)} files checked, {bad} problem(s)"
          + (" (BOM auto-fixed where missing)" if fix else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
