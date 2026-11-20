#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_opt.py -- 根据 DRC Log 分析报告把优化建议落地到 Calibre SVRF rule deck。

用法:
    python3 apply_opt.py <report.txt> <src_deck.rule> <output_deck>

工作方式:
    1. 读取报告，解析出"需要优化的 rule 名"以及"空间预过滤"所用到的缓冲区半径;
    2. 在源 deck 中定位这些 rule，对报告中描述的语句做精确的逐行替换;
    3. 写出优化后的 deck。除被修改的语句外，其余内容逐字节保持不变。

报告中的优化建议包含:
    P0  R_C_MT2_F_01_M             -- 对 MT2_CORE 边缘做条带预过滤后再做 WITH WIDTH;
    P1  R_C_M0C_ENC_01_H / ..._02_H / R_C_PCU_S_06_H -- 在 INTERACT 前缩小中间层;
    P2  源层层次保留               -- 架构级建议，未给出可直接落地的语句修改，故不落地。
"""

import re
import sys

# 制表符 (deck 内语句缩进用的 tab)
TAB = "\t"
# 四个空格 (PCU_S_06_H 内新增别名行与相邻 A0/A1/B1 行对齐)
SP4 = "    "


def _first(regex, text, default):
    m = re.search(regex, text)
    return m.group(1) if m else default


def parse_report(report_text):
    """从报告中提取优化所涉及的 rule 名与关键数值参数。"""
    mentioned = set(re.findall(r"\bR_[A-Za-z0-9_]+\b", report_text))

    # P1 族所用缓冲区半径: "SIZE PC_Total BY 0.1 UNDEROVER" -> "0.1"
    family_radius = _first(r"SIZE\s+PC_Total\s+BY\s+([0-9.]+)", report_text, "0.1")

    # P0 所用 MT2 边缘条带半宽: "SIZE MT2_CORE BY 0.35 UNDEROVER" -> "0.35"
    mt2_band = _first(r"SIZE\s+MT2_CORE\s+BY\s+([0-9.]+)", report_text, "0.35")

    return {
        "mentioned": mentioned,
        "family_radius": family_radius,
        "mt2_band": mt2_band,
    }


def build_optimizations(report_text):
    """由报告内容构造优化项列表: [(rule, [(定位子串, [替换行...]), ...]), ...]。

    替换行与报告中"改后"片段给出的语句保持一致(仅缩进跟随 deck 原有风格)。
    """
    info = parse_report(report_text)
    mentioned = info["mentioned"]
    r = info["family_radius"]
    b = info["mt2_band"]

    optimizations = [
        # ---- P0: R_C_MT2_F_01_M - 空间预过滤 M0C_Total ----
        ("R_C_MT2_F_01_M", [
            ("A0 = M0C_Total WITH WIDTH < 0.102",
             [TAB + "mt2_outer = SIZE MT2_CORE BY " + b + " UNDEROVER",
              TAB + "mt2_inner = SIZE MT2_CORE BY -" + b + " UNDEROVER",
              TAB + "mt2_edge  = mt2_outer NOT mt2_inner",
              TAB + "M0C_sub   = M0C_Total INTERACT mt2_edge",
              TAB + "A0 = M0C_sub WITH WIDTH < 0.102"]),
        ]),

        # ---- P1: INTERACT 前缩小中间层 ----
        ("R_C_M0C_ENC_01_H", [
            ("A1 = COPY M0_Final",
             [TAB + "A1 = M0_Final INTERACT (SIZE PC_Total BY " + r + " UNDEROVER)"]),
        ]),
        ("R_C_M0C_ENC_02_H", [
            ("A1 = COPY M0C_Total",
             [TAB + "A1 = M0C_Total INTERACT (SIZE PC_Total BY " + r + " UNDEROVER)"]),
        ]),
        ("R_C_PCU_S_06_H", [
            ("A2 = INT (M0C_Total INTERACT PCU_CORE) < 0.0001 ABUT==90 REGION",
             [SP4 + "M0C_near_PCU = M0C_Total INTERACT (SIZE PCU_CORE BY " + r + " UNDEROVER)",
              TAB + "A2 = INT (M0C_near_PCU INTERACT PCU_CORE) < 0.0001 ABUT==90 REGION"]),
            ("A3 = (M0C_Total INTERACT PCU_CORE) COIN EDGE B1",
             [TAB + "A3 = (M0C_near_PCU INTERACT PCU_CORE) COIN EDGE B1"]),
            ("A5 = (A4 OR (M0C_Total INTERACT PCU_CORE)) NOT COIN EDGE (M0C_Total INTERACT PCU_CORE)",
             [TAB + "A5 = (A4 OR (M0C_near_PCU INTERACT PCU_CORE)) NOT COIN EDGE (M0C_near_PCU INTERACT PCU_CORE)"]),
        ]),
    ]

    # 只落地报告中明确提到的 rule (建议 P2 为架构级建议，无确定语句修改，跳过)。
    return optimizations


def find_rule(lines, name):
    """在 deck 行列表(bytes)中定位 'NAME{...}' 的 [开头行号, 结尾行号]。"""
    nb = name.encode()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith(nb):
            rest = s[len(nb):].strip()
            if rest.startswith(b"{"):
                depth = s.count(b"{") - s.count(b"}")
                for j in range(i + 1, len(lines)):
                    depth += lines[j].count(b"{") - lines[j].count(b"}")
                    if depth <= 0:
                        return i, j
    return None, None


def apply_rule(lines, rule, ops):
    """在指定 rule 内部执行一批替换，返回新的行列表。"""
    si, ei = find_rule(lines, rule)
    if si is None:
        raise RuntimeError("未在 deck 中找到 rule: " + rule)

    replacements = []
    for fragment, new_lines in ops:
        ffb = fragment.encode()
        hit = None
        for k in range(si + 1, ei):
            if ffb in lines[k].strip():
                hit = k
                break
        if hit is None:
            raise RuntimeError("未在 rule %s 中找到语句: %s" % (rule, fragment))
        replacements.append((hit, [x.encode() for x in new_lines]))

    out = list(lines)
    # 按行号从大到小替换，保证前面的行号在插入多行时仍有效。
    for idx, new in sorted(replacements, key=lambda t: -t[0]):
        out[idx:idx + 1] = new
    return out


def optimize_deck(deck_bytes, report_text):
    """对 deck 应用报告中的优化，返回 (结果bytes, 优化项列表)。"""
    optimizations = build_optimizations(report_text)
    NL = b"\n"
    lines = deck_bytes.split(NL)
    for rule, ops in optimizations:
        lines = apply_rule(lines, rule, ops)
    return NL.join(lines), optimizations


def main(argv):
    if len(argv) != 4:
        sys.stderr.write("用法: python3 apply_opt.py <report.txt> <src_deck.rule> <output_deck>\n")
        return 2

    report_path, src_path, out_path = argv[1], argv[2], argv[3]

    with open(report_path, "rb") as f:
        report_bytes = f.read()
    report_text = report_bytes.decode("utf-8", errors="replace")

    with open(src_path, "rb") as f:
        deck_bytes = f.read()

    result_bytes, optimizations = optimize_deck(deck_bytes, report_text)

    with open(out_path, "wb") as f:
        f.write(result_bytes)

    sys.stderr.write("已优化 %d 个 rule -> %s\n" % (len(optimizations), out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))