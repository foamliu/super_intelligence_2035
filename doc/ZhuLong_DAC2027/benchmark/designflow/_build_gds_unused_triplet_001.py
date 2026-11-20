#!/usr/bin/env python3
"""Build fixtures for EDA-Eval-DesignFlow-GdsUnusedTripletAnalyze-001.

Generates a minimal valid GDSII binary (proper record structure) with the
given cell names, plus a drcWithPattern-style report whose tail has an
unusedCell section. Used to create:
  - visible A fixtures (assets/...)
  - hidden B fixtures (embedded as strings into check.py via repr)

The candidate's parser scans GDS for STRNAME records (rtype=0x06, dtype=0x06),
so the writer must produce a well-formed even-aligned GDS so the linear scan
walks records correctly.
"""
import struct, sys, os

# GDSII record (rectype, datatype, payload) -> bytes
def rec(rectype, datatype, payload=b""):
    plen = len(payload)
    rlen = 4 + plen
    if rlen % 2 == 1:
        payload += b"\x00"
        rlen += 1
    return struct.pack(">H", rlen) + bytes([rectype, datatype]) + payload

def s2b(s):
    """ASCII string payload, null-padded to even length."""
    b = s.encode("ascii")
    if len(b) % 2 == 1:
        b += b"\x00"
    return b

def i2(v):
    return struct.pack(">h", v)

def gds_double(v):
    # GDS 8-byte float (IEEE 754 double, big-endian) — UNITS only
    return struct.pack(">d", v)

def build_gds(cells, libname="PDK_QA_LIB"):
    out = b""
    # HEADER: version 600
    out += rec(0x00, 0x01, i2(600))
    # BGNLIB: 12 int2 (mod Y/M/D/h/m/s + access Y/M/D/h/m/s)
    dates = i2(2026)+i2(11)+i2(20)+i2(10)+i2(0)+i2(0) + i2(2026)+i2(11)+i2(20)+i2(10)+i2(0)+i2(0)
    out += rec(0x01, 0x02, dates)
    # LIBNAME
    out += rec(0x02, 0x06, s2b(libname))
    # UNITS: 2 doubles (user unit per db unit, db unit per meter)
    out += rec(0x03, 0x05, gds_double(1e-3) + gds_double(1e-9))
    for c in cells:
        # BGNSTR
        out += rec(0x05, 0x02, dates)
        # STRNAME
        out += rec(0x06, 0x06, s2b(c))
        # ENDSTR
        out += rec(0x07, 0x00)
    # ENDLIB
    out += rec(0x04, 0x00)
    return out

def build_report(unused_cells, total_unused_count=None, header="G5_CIP"):
    if total_unused_count is None:
        total_unused_count = len(unused_cells)
    lines = []
    lines.append("# drcWithPattern report (synthetic fixture)")
    lines.append(f"deck: {header}")
    lines.append(f"totalCells scanned: 401")
    lines.append("... rule match summary elided ...")
    lines.append("")
    # tail section: unusedCell block
    lines.append(f"unusedCellCount({total_unused_count}):")
    for c in unused_cells:
        lines.append(c)
    # next Count block to terminate parsing
    lines.append("patternNotFoundCount(0):")
    lines.append("duplicateCellCount(0):")
    return "\n".join(lines) + "\n"

# ---- Fixture A (visible) ----
A_TRIPLETS_MAIN_UNUSED = ["ENC_A_001", "ENC_A_002", "ENC_A_003"]
A_TRIPLET_USED = "USED_A_010"          # main NOT in unusedCell (used by a rule)
A_HALF_MAIN = "ENC_A_004"              # half variant: only _P
A_HALF_VARIANT = "_P"
A_STANDALONE = ["LONE_A_020", "LONE_A_030"]

A_CELLS = []
for m in A_TRIPLETS_MAIN_UNUSED:
    A_CELLS += [m, m + "_F", m + "_P"]
A_CELLS += [A_TRIPLET_USED, A_TRIPLET_USED + "_F", A_TRIPLET_USED + "_P"]
A_CELLS += [A_HALF_MAIN, A_HALF_MAIN + A_HALF_VARIANT]
A_CELLS += A_STANDALONE

A_UNUSED = sorted(A_TRIPLETS_MAIN_UNUSED + [A_HALF_MAIN] + A_STANDALONE)

# ---- Fixture B (hidden) ----
B_TRIPLETS_MAIN_UNUSED = ["ENC_B_110", "ENC_B_120"]
B_TRIPLET_USED = "USED_B_130"
B_HALF_MAIN = "ENC_B_140"              # half variant: only _F (structure-flipped vs A)
B_HALF_VARIANT = "_F"
B_STANDALONE = ["LONE_B_150", "LONE_B_160", "LONE_B_170"]

B_CELLS = []
for m in B_TRIPLETS_MAIN_UNUSED:
    B_CELLS += [m, m + "_F", m + "_P"]
B_CELLS += [B_TRIPLET_USED, B_TRIPLET_USED + "_F", B_TRIPLET_USED + "_P"]
B_CELLS += [B_HALF_MAIN, B_HALF_MAIN + B_HALF_VARIANT]
B_CELLS += B_STANDALONE

B_UNUSED = sorted(B_TRIPLETS_MAIN_UNUSED + [B_HALF_MAIN] + B_STANDALONE)

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    # A
    with open(os.path.join(out_dir, "task.gds"), "wb") as f:
        f.write(build_gds(A_CELLS, libname="PDK_QA_A"))
    with open(os.path.join(out_dir, "task.report_drcWithPattern"), "w") as f:
        f.write(build_report(A_UNUSED))
    # B
    with open(os.path.join(out_dir, "B.gds"), "wb") as f:
        f.write(build_gds(B_CELLS, libname="PDK_QA_B"))
    with open(os.path.join(out_dir, "B.report_drcWithPattern"), "w") as f:
        f.write(build_report(B_UNUSED))
    # stats
    print("A cells:", len(A_CELLS), "triplets:", len(A_TRIPLETS_MAIN_UNUSED)+1,
          "unused:", len(A_UNUSED), "orphan_main:", len(A_TRIPLETS_MAIN_UNUSED),
          "half:", A_HALF_MAIN + A_HALF_VARIANT)
    print("B cells:", len(B_CELLS), "triplets:", len(B_TRIPLETS_MAIN_UNUSED)+1,
          "unused:", len(B_UNUSED), "orphan_main:", len(B_TRIPLETS_MAIN_UNUSED),
          "half:", B_HALF_MAIN + B_HALF_VARIANT)
    # also emit python-literal forms of B for embedding in check.py
    print("---B_GDS_B64---")
    import base64
    b_gds = build_gds(B_CELLS, libname="PDK_QA_B")
    print(base64.b64encode(b_gds).decode())
    print("---B_REP---")
    print(repr(build_report(B_UNUSED)))
