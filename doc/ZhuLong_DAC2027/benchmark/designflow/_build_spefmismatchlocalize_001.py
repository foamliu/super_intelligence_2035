#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder for EDA-Eval-DesignFlow-SpefMismatchModuleLocalize-001.
A档 faithful case from trace fdnle (haoyut@hfeg0pkn003, mc305, 751 msgs).
USER#57 (逐字): "需要你进行一些分析 看是哪一些模块的问题较多 并且尽可能的精准一点而不是共同的上层模块"
Gold methodology = haoyut's spef_analysis_v2/analyze.py v4 (deepest non-analog cell,
NF/NM/HM classification, common-parent stripping, analog filter).

Generates:
  assets/<id>/prompt.txt, task_brief.md, mismatch_log_A.txt, hidden_manifest.json
  assets/<id>/hidden/mismatch_log_B.txt, mismatch_log_B_prime.txt
  reference/<id>/spef_module_localize_ref.py, check.py, reference_submit.zip
  reference/<id>/negative/{fake_empty.py, fake_print_expected.py, fake_core_deleted.py,
    naive_no_analog_filter.py, naive_hardcode_a.py}, negative_selftest.py
"""
import os, sys, json, random, zipfile, shutil, io, hashlib, tempfile, subprocess

random.seed(20261108)

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SpefMismatchModuleLocalize-001"
ADIR = os.path.join(ROOT, "assets", CID)
RDIR = os.path.join(ROOT, "reference", CID)
HDIR = os.path.join(ADIR, "hidden")
NEGDIR = os.path.join(RDIR, "negative")
for d in (ADIR, RDIR, HDIR, NEGDIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Log generator
# ---------------------------------------------------------------------------
# Real log format (from haoyut's spef_check_release/logs/batch_*.log):
#   ======================================================================
#     Compare #<seq>  Net: <full_netpath>
#   ======================================================================
#     NL: <a> drives, <b> loads  |  SP: <c> drives, <d> loads
#     ===========================================================
#     NETLIST
#     ===========================================================
#     Driver: <path>  (<celltype>)
#     Net: <path>
#     Load:  <path>  (<celltype>)
#     ===========================================================
#     SPEF
#     ===========================================================
#     Driver: <path>  (<celltype>)
#     Net: <path>
#     Load:  <path>  (<celltype>)
#     ===========================================================
#     COMPARISON
#     ===========================================================
#     >> <MARKER1> <<
#        Netlist: <path>
#        SPEF   : <path>
#     ... (more markers)
#   ======================================================================
#     Done.
#   ======================================================================
#
# Markers: OK | NET NAME MISMATCH | HIERARCHY MISMATCH | SPEF_NOT_FOUND
# Net path: <top>/<chan>/<side>/<common_parent>/<module>/<submod>/<leafinst>/<netname>

HEADER = "Batch #1-#%d\n2026-10-27 18:08:37.261728\nRange: #1-#%d (%d entries)\n" + "="*70 + "\n\n"

def make_block(seq, netpath, markers, nl_driver, sp_driver, sp_net, celltype_nl="invLx8", celltype_sp="invLx8"):
    lines = []
    lines.append("="*70)
    lines.append("  Compare #%d  Net: %s" % (seq, netpath))
    lines.append("="*70)
    lines.append("")
    lines.append("  NL: 1 drives, 1 loads  |  SP: 1 drives, 1 loads")
    lines.append("")
    lines.append("  " + "="*58)
    lines.append("  NETLIST")
    lines.append("  " + "="*58)
    lines.append("  Driver: %s  (%s)" % (nl_driver, celltype_nl))
    lines.append("  Net: %s" % netpath)
    load_inst = netpath.rsplit("/", 1)[0] + "/I%d/A" % random.randint(1, 20)
    lines.append("  Load:  %s  (%s)" % (load_inst, celltype_nl))
    lines.append("")
    lines.append("  " + "="*58)
    lines.append("  SPEF")
    lines.append("  " + "="*58)
    lines.append("  Driver: %s  (%s)" % (sp_driver, celltype_sp))
    lines.append("  Net: %s" % sp_net)
    lines.append("  Load:  %s  (%s, input)" % (load_inst, load_inst.rsplit("/", 1)[0].rsplit("/", 1)[-1]))
    lines.append("")
    lines.append("  " + "="*58)
    lines.append("  COMPARISON")
    lines.append("  " + "="*58)
    for mk in markers:
        lines.append("  >> %s <<" % mk)
        if mk != "OK":
            lines.append("     Netlist: %s" % netpath)
            lines.append("     SPEF   : %s" % sp_net)
    lines.append("="*70)
    lines.append("  Done.")
    lines.append("="*70)
    lines.append("")
    return "\n".join(lines)

# A hierarchy: real BnkGTop DRAM sense-amp / row-redundancy structure (from trace).
A_TOPLVL = ["Ictop", "I_Channel"]
A_SIDE = ["I_BnkGTopX4_Top", "I_BnkGTopX4_Bot"]
A_COMMON_PARENT = "I_BnkGTopX4_gut"   # the common parent that must be stripped
A_BANKS = ["I_BnkGTop_GE", "I_BnkGTop_HF", "I_BnkGTop_AC", "I_BnkGTop_BD"]
A_NONANALOG_MODS = [
    "I_D_BankLogicx2L", "I_T_CMAry_1", "I_T_CmFsLatchX6L_o476", "I_R_RowRed1024",
    "I_R_RowRed128", "I_R_RowRed32", "I_R_NcCtrl", "I_R_trimEqOff",
    "I_D_BnkGTopBGRptPrcTop", "I_BCenterL", "I_BCenterR", "I_BCenterDQ",
]
A_ANALOG_MODS = [
    "I_AG_NewBLSA_VblenActLDOCtrl", "I_AG_NewBLSA_VblhmActLDOCtrl",
    "I_AG_DigGenMPE", "I_AG_DigGenCompLogic", "I_RefGen",
]

# B hierarchy: DDR PHY (structurally different from A).
B_TOPLVL = ["DdrTop", "DfiChan0"]
B_SIDE = ["I_PhyTopX4_A", "I_PhyTopX4_B"]
B_COMMON_PARENT = "I_PhyPipe_gut"   # B's common parent to strip
B_NONANALOG_MODS = [
    "I_DqCtrl8L_o32", "I_DqsGateDeskew", "I_WriteLevelCtrl",
    "I_ReadCapture8L", "I_CmdDeskew", "I_ZqCalCtrl",
    "I_PhyBistCtrl", "I_DqDeskew4L", "I_PhyTopStatus",
]
B_ANALOG_MODS = [
    "I_AG_VrefLdo", "I_AG_PllBias", "I_RefGenCore",
    "I_VgClampCtrl", "I_AG_XtlOsc",
]

def gen_log(toplvl, side, common_parent, nonanalog_mods, analog_mods, n_blocks, analog_frac=0.35, name="A"):
    """Generate a mismatch log with the given hierarchy.
    Marker distribution per module is deterministic per module index to ensure
    check.py can independently verify counts.
    """
    out = []
    out.append(HEADER % (n_blocks, n_blocks, n_blocks))
    seq = 1
    # Distribute blocks: each non-analog module gets a FIXED count with a FIXED marker mix.
    # This makes check.py's independent verification exact.
    # Plan: nonanalog mods get the bulk; analog mods get analog_frac * n_blocks.
    n_analog_total = int(n_blocks * analog_frac)
    n_nonanalog_total = n_blocks - n_analog_total
    # per-nonanalog-module block counts (deterministic)
    nn_counts = [max(10, n_nonanalog_total // len(nonanalog_mods) + (i if i < n_nonanalog_total % len(nonanalog_mods) else 0)) for i in range(len(nonanalog_mods))]
    # adjust to sum
    while sum(nn_counts) < n_nonanalog_total:
        nn_counts[0] += 1
    while sum(nn_counts) > n_nonanalog_total:
        nn_counts[-1] -= 1
    # per-analog-module block counts
    na_counts = [max(5, n_analog_total // len(analog_mods) + (i if i < n_analog_total % len(analog_mods) else 0)) for i in range(len(analog_mods))]
    while sum(na_counts) < n_analog_total:
        na_counts[0] += 1
    while sum(na_counts) > n_analog_total:
        na_counts[-1] -= 1

    # Marker mix per non-analog module (deterministic, varies by module):
    # mod 0: mostly NM (rename)    -> category rename
    # mod 1: mostly NF (missing)   -> category missing
    # mod 2: mixed NM+HM           -> category mixed
    # mod 3: mostly HM              -> category hierarchy
    # mod 4: NF + NM both           -> category missing
    # mod 5: mostly NM              -> category rename
    # mod 6: OK (these become non-problem, but counted in total)
    # mod 7: NM dominant            -> rename
    # mod 8: NF dominant            -> missing
    def marker_mix(mod_idx, j, total):
        if mod_idx == 6:
            return ["OK"]   # this whole module is OK -> not a problem block
        r = (j * 7 + mod_idx * 13) % 100
        if mod_idx == 0:
            return ["NET NAME MISMATCH"] if r < 90 else ["SPEF_NOT_FOUND"]
        if mod_idx == 1:
            return ["SPEF_NOT_FOUND"] if r < 85 else ["NET NAME MISMATCH"]
        if mod_idx == 2:
            if r < 45: return ["NET NAME MISMATCH"]
            if r < 90: return ["HIERARCHY MISMATCH"]
            return ["NET NAME MISMATCH", "HIERARCHY MISMATCH"]
        if mod_idx == 3:
            return ["HIERARCHY MISMATCH"] if r < 88 else ["NET NAME MISMATCH"]
        if mod_idx == 4:
            if r < 50: return ["SPEF_NOT_FOUND"]
            return ["NET NAME MISMATCH"]
        if mod_idx == 5:
            return ["NET NAME MISMATCH"] if r < 92 else ["HIERARCHY MISMATCH"]
        if mod_idx == 7:
            return ["NET NAME MISMATCH"] if r < 80 else ["SPEF_NOT_FOUND"]
        if mod_idx == 8:
            return ["SPEF_NOT_FOUND"] if r < 78 else ["NET NAME MISMATCH"]
        return ["NET NAME MISMATCH"]

    def make_netpath(side_i, common_p, mod, submod, leaf, netname):
        return "/".join([toplvl[0], toplvl[1], side[side_i], common_p, mod, submod, leaf, netname])

    # Non-analog blocks
    for mi, mod in enumerate(nonanalog_mods):
        cnt = nn_counts[mi]
        # one submodule per module to keep aggregation clean
        submod = mod.replace("I_", "") + "_sub"
        for j in range(cnt):
            side_i = (mi + j) % 2
            leaf = "I%d" % random.randint(1, 999) if (j % 3 == 0) else mod.replace("I_", "I_") + "Unit_%d_" % (j % 8 + 1)
            # make leaf a real leaf-inst sometimes (I\d+), sometimes a named unit
            if j % 2 == 0:
                leaf = "I%d" % random.randint(100, 999)
            else:
                leaf = mod.replace("I_", "I_") + "Unit_%d_" % (j % 6 + 1)
            netname = "net%d" % j if (mi % 2) else "sig%d_%s" % (j, "x")
            netpath = make_netpath(side_i, common_p=common_parent, mod=mod, submod=submod, leaf=leaf, netname=netname)
            mks = marker_mix(mi, j, cnt)
            # SPEF net: if NF, SPEF net is absent; if NM, SPEF net renamed (net2/net29 style); if HM, hierarchy differs
            if "SPEF_NOT_FOUND" in mks:
                sp_net = "(not found in SPEF)"
                sp_driver = "(not found)"
            elif "NET NAME MISMATCH" in mks:
                sp_net = netpath.rsplit("/", 1)[0] + "/net%d" % random.randint(1, 99)
                sp_driver = netpath.rsplit("/", 1)[0] + "/I%d/Y" % random.randint(1, 50)
            else:
                sp_net = netpath  # HM: same net, diff hierarchy
                sp_driver = netpath.rsplit("/", 1)[0] + "/I%d/Y" % random.randint(1, 50)
            nl_driver = netpath.rsplit("/", 1)[0] + "/I%d/Y" % random.randint(1, 50)
            out.append(make_block(seq, netpath, mks, nl_driver, sp_driver, sp_net))
            seq += 1
    # Analog blocks (to be filtered)
    for mi, mod in enumerate(analog_mods):
        cnt = na_counts[mi]
        submod = mod.replace("I_", "") + "_inner"
        for j in range(cnt):
            side_i = (mi + j) % 2
            leaf = "I%d" % random.randint(1, 999)
            netname = "trim_%d" % j
            netpath = make_netpath(side_i, common_p=common_parent, mod=mod, submod=submod, leaf=leaf, netname=netname)
            mks = ["SPEF_NOT_FOUND"] if (j % 2 == 0) else ["NET NAME MISMATCH"]
            sp_net = "(not found in SPEF)" if "SPEF_NOT_FOUND" in mks else netpath.rsplit("/", 1)[0] + "/net%d" % random.randint(1, 99)
            nl_driver = netpath.rsplit("/", 1)[0] + "/I%d/Y" % random.randint(1, 50)
            sp_driver = "(not found)" if "SPEF_NOT_FOUND" in mks else netpath.rsplit("/", 1)[0] + "/I%d/Y" % random.randint(1, 50)
            out.append(make_block(seq, netpath, mks, nl_driver, sp_driver, sp_net))
            seq += 1
    return "\n".join(out), seq - 1

# Generate A log (visible, real BnkGTop hierarchy, ~180 blocks)
A_LOG, A_N = gen_log(A_TOPLVL, A_SIDE, A_COMMON_PARENT, A_NONANALOG_MODS, A_ANALOG_MODS, 180, analog_frac=0.30, name="A")
with open(os.path.join(ADIR, "mismatch_log_A.txt"), "w", encoding="utf-8") as f:
    f.write(A_LOG)
print("A log: %d blocks, %d bytes" % (A_N, len(A_LOG)))

# Generate B log (hidden, DDR PHY hierarchy, ~220 blocks, different counts)
B_LOG, B_N = gen_log(B_TOPLVL, B_SIDE, B_COMMON_PARENT, B_NONANALOG_MODS, B_ANALOG_MODS, 220, analog_frac=0.32, name="B")
with open(os.path.join(HDIR, "mismatch_log_B.txt"), "w", encoding="utf-8") as f:
    f.write(B_LOG)
print("B log: %d blocks, %d bytes" % (B_N, len(B_LOG)))

# Generate B' log (B with renamed top hierarchy + shuffled module order, for cross-input guard)
# Same structure but different top names so common_parent label changes and a hardcoded candidate fails.
BP_TOPLVL = ["SerDesTop", "LaneGrp0"]
BP_SIDE = ["I_X4Top_A", "I_X4Top_B"]
BP_COMMON_PARENT = "I_X4Pipe_gut"
BP_NONANALOG_MODS = [
    "I_LanePcs4L", "I_LanePma4L", "I_TxDeskew", "I_RxCdr",
    "I_EqCtrl", "I_PllCtrl", "I_LaneBist", "I_GearBox4L",
    "I_LaneStatus",
]
BP_ANALOG_MODS = [
    "I_AG_LdoCore", "I_AG_BiasGen", "I_RefGenPll", "I_VgClampLane",
]
BP_LOG, BP_N = gen_log(BP_TOPLVL, BP_SIDE, BP_COMMON_PARENT, BP_NONANALOG_MODS, BP_ANALOG_MODS, 200, analog_frac=0.30, name="B'")
with open(os.path.join(HDIR, "mismatch_log_B_prime.txt"), "w", encoding="utf-8") as f:
    f.write(BP_LOG)
print("B' log: %d blocks, %d bytes" % (BP_N, len(BP_LOG)))

# hidden_manifest.json
manifest = {
    "case_id": CID,
    "hidden_inputs": [
        {"name": "mismatch_log_B.txt", "purpose": "primary hidden test input (DDR PHY hierarchy, structurally different from A)", "blocks": B_N},
        {"name": "mismatch_log_B_prime.txt", "purpose": "cross-input guard (SerDes hierarchy, renamed top, defeats hardcoding)", "blocks": BP_N},
    ],
    "note": "check.py runs the candidate script on mismatch_log_B.txt as mismatch_log.txt in a temp dir, and re-runs on B_prime for the cross-input guard. A-specific tokens (BnkGTop/CmFsLatch/etc.) must NOT appear in the candidate.",
}
with open(os.path.join(ADIR, "hidden_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# prompt.txt (USER#57 verbatim) + task_brief.md (<=3 lines, only delivery interface)
# ---------------------------------------------------------------------------
PROMPT = '<user_input mode="act">需要你进行一些分析 看是哪一些模块的问题较多 并且尽可能的精准一点而不是共同的上层模块</user_input>'
with open(os.path.join(ADIR, "prompt.txt"), "w", encoding="utf-8") as f:
    f.write(PROMPT + "\n")

# task_brief: ONLY delivery interface + file location, NOT what to do.
TASK_BRIEF = (
    "交付：outputs/submit.zip，内含 spef_module_localize.py（读 mismatch_log.txt，输出 module_localization.json）。\n"
    "判分：check(deliverable, workdir) 在独立临时目录解 zip，对隐藏输入 B 真跑候选脚本。\n"
    "输入文件 mismatch_log.txt 位于 cwd；脚本须输出 module_localization.json 到 cwd。\n"
)
with open(os.path.join(ADIR, "task_brief.md"), "w", encoding="utf-8") as f:
    f.write(TASK_BRIEF)

# ---------------------------------------------------------------------------
# Reference solution (gold) — generalized from haoyut's analyze.py v4
# ---------------------------------------------------------------------------
REF_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spef_module_localize.py — SPEF/netlist mismatch module-level localization.

Reads mismatch_log.txt (Compare # blocks with Net + >> markers <<) and emits
module_localization.json: per-deepest-functional-cell counts of
SPEF_NOT_FOUND (NF) / NET NAME MISMATCH (NM) / HIERARCHY MISMATCH (HM) /
mixed (NM+HM), after (a) stripping the common parent prefix shared by all
nets, (b) filtering analog modules, (c) reducing each net to its deepest
functional owning cell (strip I_ prefix + trailing numeric/array suffixes,
strip leaf I\\d+ instances).

Methodology generalized from real SPEF-check analysis flow.
"""
import re, json, os
from collections import Counter, defaultdict

LOG_PATH = os.environ.get("MISMATCH_LOG", "mismatch_log.txt")
OUT_PATH = os.environ.get("MODULE_LOC_OUT", "module_localization.json")

ANALOG_KW = ["AG_", "NEWBLSA_", "VBL", "LDO", "REFGEN", "REFLOGIC",
             "TMSLP", "ITEMP", "VGCLAMP", "DIGGEN", "VREF", "PLLBIAS",
             "BIASGEN", "XTLOSC", "VGCLAMP"]

def parse_blocks(path):
    with open(path, errors="replace") as f:
        lines = f.read().split("\n")
    n = len(lines); blocks = []; i = 0
    while i < n:
        m = re.search(r"^\s*Compare #(\d+)\s+Net:\s+(\S+)", lines[i])
        if m:
            seq = int(m.group(1)); nl = m.group(2); mks = []; i += 1
            while i < n and "Compare #" not in lines[i]:
                for mm in re.finditer(r">>\s*([^<]+?)\s*<<", lines[i]):
                    mks.append(mm.group(1).strip())
                i += 1
            blocks.append({"seq": seq, "nl": nl, "mks": mks})
        else:
            i += 1
    return blocks

def is_leaf_inst(name):
    return bool(re.match(r"^I\d+", name))

def seg_to_cell(seg):
    s = seg[2:] if seg.startswith("I_") else seg
    s = re.sub(r"(_?[A-Za-z]?\d+)+_?$", "", s)
    return s

def common_prefix(nets):
    """Longest shared hierarchical prefix (list of segments) across all nets."""
    if not nets: return []
    split = [n.split("/") for n in nets]
    pre = []
    for k in range(min(len(s) for s in split)):
        seg = split[0][k]
        if all(s[k] == seg for s in split):
            pre.append(seg)
        else:
            break
    return pre

def get_cell_path(nl, cprefix_len):
    parts = nl.split("/")
    # Skip the common prefix; the segment right after it is the common parent — skip it too.
    # User goal: "not common upper module" -> strip the common parent layer.
    start = cprefix_len  # top + channel + side + common_parent (if all shared)
    # The common parent is the first segment after the shared top; drop it.
    rel = parts[start:-1]  # exclude the net name (last) and the shared top prefix
    if not rel:
        return parts[start] if start < len(parts) else nl, parts[start] if start < len(parts) else nl
    # strip trailing leaf insts
    while rel and is_leaf_inst(rel[-1]):
        rel = rel[:-1]
    if not rel:
        return parts[start], parts[start]
    cells = [seg_to_cell(s) for s in rel]
    dedup = []
    for c in cells:
        if dedup and c == dedup[-1]:
            continue
        dedup.append(c)
    full = "|".join(dedup).strip("|")
    if not full:
        return parts[start], parts[start]
    return full, dedup[-1]

def is_analog(cell):
    c = cell.upper()
    for kw in ANALOG_KW:
        if kw in c:
            return True
    return False

def get_context(full):
    parts = full.split("|")
    return " > ".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else "")

def classify(mks):
    if "SPEF_NOT_FOUND" in mks:
        return "NF"
    if "NET NAME MISMATCH" in mks and "HIERARCHY MISMATCH" in mks:
        return "NM+HM"
    if "NET NAME MISMATCH" in mks:
        return "NM"
    if "HIERARCHY MISMATCH" in mks:
        return "HM"
    return "?"

def categorize(nf, nm, hm, both, total):
    if total == 0:
        return "none"
    nf_pct = nf / total * 100
    if nf_pct > 50:
        return "missing"
    if nm / total > 0.8:
        return "rename"
    if hm / total > 0.8:
        return "hierarchy"
    if nm / total > 0.4:
        return "rename+hierarchy"
    if nf_pct > 10:
        return "missing-mixed"
    return "mixed"

def main():
    blocks = parse_blocks(LOG_PATH)
    total = len(blocks)
    problem = [b for b in blocks if b["mks"] and b["mks"] != ["OK"]]
    all_nets = [b["nl"] for b in problem]
    cpre = common_prefix(all_nets)
    cpre_len = len(cpre)
    common_parent_seg = cpre[-1] if cpre else ""
    na = []
    analog_count = 0
    for b in problem:
        full, deepest = get_cell_path(b["nl"], cpre_len)
        if is_analog(full):
            analog_count += 1
            continue
        na.append((b, full, deepest))
    stats = defaultdict(Counter)
    totals = Counter()
    contexts = defaultdict(set)
    samples = defaultdict(list)
    for b, full, deepest in na:
        p = classify(b["mks"])
        stats[deepest][p] += 1
        totals[deepest] += 1
        contexts[deepest].add(get_context(full))
        if len(samples[deepest]) < 1:
            samples[deepest].append(full)
    modules = []
    for ct, total_c in totals.items():
        s = stats[ct]
        nf = s.get("NF", 0); nm = s.get("NM", 0); hm = s.get("HM", 0); both = s.get("NM+HM", 0)
        nf_pct = round(nf / total_c * 100, 1) if total_c else 0.0
        cat = categorize(nf, nm, hm, both, total_c)
        modules.append({
            "cell": ct,
            "total": total_c,
            "NF": nf, "NM": nm, "HM": hm, "both": both,
            "nf_pct": nf_pct,
            "context": " | ".join(sorted(contexts[ct])[:2]),
            "category": cat,
            "sample_path": samples[ct][0] if samples[ct] else "",
        })
    # sort: by NF desc, then total desc
    modules.sort(key=lambda m: (-m["NF"], -m["total"]))
    out = {
        "total_blocks": total,
        "problem_blocks": len(problem),
        "non_analog_blocks": len(na),
        "analog_blocks_filtered": analog_count,
        "common_parent": common_parent_seg,
        "modules": modules,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("total=%d problem=%d non_analog=%d analog_filtered=%d modules=%d" %
          (total, len(problem), len(na), analog_count, len(modules)))

if __name__ == "__main__":
    main()
'''
with open(os.path.join(RDIR, "spef_module_localize_ref.py"), "w", encoding="utf-8") as f:
    f.write(REF_SRC)

# ---------------------------------------------------------------------------
# check.py — 14 conditions (a-n), each independently FAILable
# ---------------------------------------------------------------------------
CHECK_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-SpefMismatchModuleLocalize-001.
14 条断言 (a-n). Runs candidate on hidden B (and B' for cross-input guard)
in an independent temp dir. Reference check.py — NEVER placed in SUT workdir.
"""
import os, sys, json, zipfile, subprocess, tempfile, shutil, re, io

# A-specific tokens that must NOT appear in a generalized candidate source.
A_TOKENS = ["BnkGTop", "CmFsLatch", "BankLogic", "R_NcCtrl", "AG_NewBLSA",
            "Ictop", "I_Channel", "R_RowRed", "trimEqOff", "BGRptPrcTop",
            "BnkGTopX4_gut"]

CASE_ASSETS = os.path.join(os.path.dirname(__file__), "..", "..", "assets",
                           "EDA-Eval-DesignFlow-SpefMismatchModuleLocalize-001")
HIDDEN_DIR = os.path.join(CASE_ASSETS, "hidden")

COND_LABELS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n"]
CONDITIONS = [(lbl, desc) for lbl, desc in zip(COND_LABELS, [
    "submit.zip valid + contains spef_module_localize.py + module_localization.json",
    "spef_module_localize.py compiles (py_compile)",
    "module_localization.json valid JSON with top-level keys total_blocks/problem_blocks/non_analog_blocks/modules",
    "[B subprocess] candidate runs on hidden mismatch_log_B.txt as mismatch_log.txt -> exit 0 + valid JSON",
    "[B] total_blocks == independent count of 'Compare #N Net:' blocks in B log",
    "[B] problem_blocks == total_blocks - count(OK-only blocks) [independent recount]",
    "[B] non_analog_blocks < problem_blocks (analog filter applied; B has analog blocks)",
    "[B] modules non-empty + each entry has keys cell/total/NF/NM/HM/both/nf_pct/context/category/sample_path",
    "[B] anti-common-parent: top-5 modules by total do not equal B's common parent segment",
    "[B] deepest-cell logic: a known B net's expected deepest cell appears in modules",
    "[B] category classification: a >80% NM module -> category contains 'rename'; a >50% NF module -> contains 'missing'",
    "[B' cross-input guard] re-run on B_prime -> common_parent changes, top module names differ from B, structure consistent",
    "anti-hardcoding: candidate source contains 0 A-specific tokens",
    "[B] sort order: first module has max NF (or max total if no NF) among all modules",
])]

def _fail(cond, msg):
    raise AssertionError("[cond %s FAIL] %s" % (cond, msg))

def _parse_blocks_indep(path):
    """Independent re-implementation of block parsing for verification."""
    blocks = []
    with open(path, errors="replace") as f:
        lines = f.read().split("\n")
    i = 0; n = len(lines)
    while i < n:
        m = re.search(r"^\s*Compare #(\d+)\s+Net:\s+(\S+)", lines[i])
        if m:
            seq = int(m.group(1)); nl = m.group(2); mks = []; i += 1
            while i < n and "Compare #" not in lines[i]:
                for mm in re.finditer(r">>\s*([^<]+?)\s*<<", lines[i]):
                    mks.append(mm.group(1).strip())
                i += 1
            blocks.append({"seq": seq, "nl": nl, "mks": mks})
        else:
            i += 1
    return blocks

def _seg_to_cell(seg):
    s = seg[2:] if seg.startswith("I_") else seg
    s = re.sub(r"(_?[A-Za-z]?\d+)+_?$", "", s)
    return s

def _is_leaf(name):
    return bool(re.match(r"^I\d+", name))

def _expected_deepest(netpath, common_parent_seg):
    parts = netpath.split("/")
    # find the common parent index and skip it
    try:
        cp_idx = parts.index(common_parent_seg)
    except ValueError:
        cp_idx = 2
    rel = parts[cp_idx+1:-1]
    while rel and _is_leaf(rel[-1]):
        rel = rel[:-1]
    if not rel:
        return parts[cp_idx+1] if cp_idx+1 < len(parts) else netpath
    cells = [_seg_to_cell(s) for s in rel]
    dedup = []
    for c in cells:
        if dedup and c == dedup[-1]:
            continue
        dedup.append(c)
    return dedup[-1] if dedup else cells[-1]

def check(deliverable, workdir):
    # deliverable: path to submit.zip; workdir: not used (we run in temp dirs)
    if not os.path.isfile(deliverable):
        _fail("a", "submit.zip not found at %s" % deliverable)
    tmp = tempfile.mkdtemp(prefix="chk_spefmm_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
        # (a) zip contents
        has_py = any(n == "spef_module_localize.py" or n.endswith("/spef_module_localize.py") for n in names)
        has_json = any(n == "module_localization.json" or n.endswith("/module_localization.json") for n in names)
        if not (has_py and has_json):
            _fail("a", "zip missing spef_module_localize.py (%s) or module_localization.json (%s); names=%s" % (has_py, has_json, names))
        py_path = os.path.join(tmp, "spef_module_localize.py")
        json_path = os.path.join(tmp, "module_localization.json")
        if not os.path.isfile(py_path):
            for n in names:
                if n.endswith("/spef_module_localize.py"):
                    py_path = os.path.join(tmp, n); break
        if not os.path.isfile(json_path):
            for n in names:
                if n.endswith("/module_localization.json"):
                    json_path = os.path.join(tmp, n); break
        # (b) py_compile
        r = subprocess.run([sys.executable, "-m", "py_compile", py_path], capture_output=True, text=True)
        if r.returncode != 0:
            _fail("b", "py_compile failed: %s" % r.stderr[:300])
        # (c) submitted JSON valid + keys
        try:
            submitted = json.load(open(json_path, encoding="utf-8"))
        except Exception as e:
            _fail("c", "module_localization.json not valid JSON: %s" % e)
        for k in ("total_blocks", "problem_blocks", "non_analog_blocks", "modules"):
            if k not in submitted:
                _fail("c", "submitted JSON missing top-level key: %s" % k)
        # (m) anti-hardcoding: scan candidate source for A-specific tokens
        src = open(py_path, encoding="utf-8", errors="replace").read()
        hits = [t for t in A_TOKENS if t in src]
        if hits:
            _fail("m", "candidate source contains A-specific tokens: %s" % hits)

        # --- Run candidate on hidden B in a fresh temp dir ---
        b_log = os.path.join(HIDDEN_DIR, "mismatch_log_B.txt")
        if not os.path.isfile(b_log):
            _fail("d", "hidden B log not found at %s" % b_log)
        btmp = tempfile.mkdtemp(prefix="chk_spefmm_B_")
        shutil.copy(py_path, os.path.join(btmp, "spef_module_localize.py"))
        shutil.copy(b_log, os.path.join(btmp, "mismatch_log.txt"))
        r = subprocess.run([sys.executable, "spef_module_localize.py"], cwd=btmp,
                           capture_output=True, text=True, timeout=120)
        # (d) B run exit 0 + valid JSON
        if r.returncode != 0:
            _fail("d", "candidate failed on B: exit=%d stderr=%s" % (r.returncode, r.stderr[:300]))
        bout_json = os.path.join(btmp, "module_localization.json")
        if not os.path.isfile(bout_json):
            _fail("d", "candidate did not produce module_localization.json on B")
        try:
            B = json.load(open(bout_json, encoding="utf-8"))
        except Exception as e:
            _fail("d", "B output JSON invalid: %s" % e)
        for k in ("total_blocks", "problem_blocks", "non_analog_blocks", "modules"):
            if k not in B:
                _fail("d", "B output missing key: %s" % k)

        # Independent recount of B
        b_blocks = _parse_blocks_indep(b_log)
        b_total = len(b_blocks)
        b_ok_only = sum(1 for b in b_blocks if b["mks"] == ["OK"])
        b_problem = b_total - b_ok_only
        # (e) total_blocks
        if B["total_blocks"] != b_total:
            _fail("e", "B total_blocks=%d but independent count=%d" % (B["total_blocks"], b_total))
        # (f) problem_blocks
        if B["problem_blocks"] != b_problem:
            _fail("f", "B problem_blocks=%d but independent count=%d (total=%d ok_only=%d)" %
                  (B["problem_blocks"], b_problem, b_total, b_ok_only))
        # (g) analog filter applied
        if not (B["non_analog_blocks"] < B["problem_blocks"]):
            _fail("g", "B non_analog_blocks=%d NOT < problem_blocks=%d (analog filter not applied)" %
                  (B["non_analog_blocks"], B["problem_blocks"]))
        # (h) modules entries have required keys
        mods = B.get("modules", [])
        if not mods:
            _fail("h", "B modules list empty")
        REQ_KEYS = {"cell","total","NF","NM","HM","both","nf_pct","context","category","sample_path"}
        for m in mods:
            missing = REQ_KEYS - set(m.keys())
            if missing:
                _fail("h", "B module entry %s missing keys: %s" % (m.get("cell","?"), missing))
        # (i) anti-common-parent: B's common parent (computed independently) not in top-5 by total
        # B's common parent = the segment after the longest shared prefix of all problem nets.
        pnets = [b["nl"] for b in b_blocks if b["mks"] != ["OK"]]
        def _common_prefix(nets):
            if not nets: return []
            sp = [n.split("/") for n in nets]
            pre = []
            for k in range(min(len(s) for s in sp)):
                seg = sp[0][k]
                if all(s[k] == seg for s in sp):
                    pre.append(seg)
                else:
                    break
            return pre
        cpre = _common_prefix(pnets)
        b_common_parent = cpre[-1] if cpre else ""
        top5 = sorted(mods, key=lambda m: -m["total"])[:5]
        if any(m["cell"] == b_common_parent for m in top5):
            _fail("i", "B common parent '%s' appears in top-5 modules (anti-common-parent violated): %s" %
                  (b_common_parent, [m["cell"] for m in top5]))
        # (j) deepest-cell logic: pick a known B non-analog problem net, compute expected deepest cell, assert it appears
        # Find a non-analog net (not containing AG_/LDO/etc) with a known module.
        ANALOG_KW = ["AG_", "NEWBLSA_", "VBL", "LDO", "REFGEN", "REFLOGIC", "TMSLP", "ITEMP", "VGCLAMP", "DIGGEN", "VREF", "PLLBIAS", "BIASGEN", "XTLOSC", "VGCLAMP"]
        def _is_analog(s):
            u = s.upper()
            return any(k in u for k in ANALOG_KW)
        probe = None
        for b in b_blocks:
            if b["mks"] != ["OK"] and not _is_analog(b["nl"]):
                probe = b["nl"]; break
        if probe is None:
            _fail("j", "no non-analog problem net found in B for deepest-cell probe")
        exp_deepest = _expected_deepest(probe, b_common_parent)
        if not any(m["cell"] == exp_deepest for m in mods):
            _fail("j", "expected deepest cell '%s' for probe net '%s' not in B modules: %s" %
                  (exp_deepest, probe, [m["cell"] for m in mods]))
        # (k) category classification
        # find a >80% NM module and a >50% NF module (B's marker mix guarantees both)
        found_rename = False; found_missing = False
        for m in mods:
            if m["total"] > 0 and m["NM"]/m["total"] > 0.8 and "rename" in m["category"]:
                found_rename = True
            if m["total"] > 0 and m["NF"]/m["total"] > 0.5 and "missing" in m["category"]:
                found_missing = True
        if not found_rename:
            _fail("k", "no module with >80%% NM and category containing 'rename': %s" %
                  [(m["cell"], m["NM"], m["total"], m["category"]) for m in mods])
        if not found_missing:
            _fail("k", "no module with >50%% NF and category containing 'missing': %s" %
                  [(m["cell"], m["NF"], m["total"], m["category"]) for m in mods])
        # (n) sort order: first module has max NF (or max total if all NF=0)
        max_nf = max(m["NF"] for m in mods)
        if max_nf > 0:
            if mods[0]["NF"] != max_nf:
                _fail("n", "first module NF=%d but max NF=%d (sort order wrong): %s" %
                      (mods[0]["NF"], max_nf, [(m["cell"], m["NF"]) for m in mods[:5]]))
        else:
            max_tot = max(m["total"] for m in mods)
            if mods[0]["total"] != max_tot:
                _fail("n", "no NF; first module total=%d but max=%d" % (mods[0]["total"], max_tot))

        # (l) B' cross-input guard: re-run on B_prime
        bp_log = os.path.join(HIDDEN_DIR, "mismatch_log_B_prime.txt")
        if not os.path.isfile(bp_log):
            _fail("l", "hidden B_prime log not found")
        bptmp = tempfile.mkdtemp(prefix="chk_spefmm_BP_")
        shutil.copy(py_path, os.path.join(bptmp, "spef_module_localize.py"))
        shutil.copy(bp_log, os.path.join(bptmp, "mismatch_log.txt"))
        r = subprocess.run([sys.executable, "spef_module_localize.py"], cwd=bptmp,
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            _fail("l", "candidate failed on B_prime: exit=%d stderr=%s" % (r.returncode, r.stderr[:300]))
        bp_out = os.path.join(bptmp, "module_localization.json")
        if not os.path.isfile(bp_out):
            _fail("l", "candidate did not produce module_localization.json on B_prime")
        BP = json.load(open(bp_out, encoding="utf-8"))
        if BP.get("common_parent", "") == B.get("common_parent", ""):
            _fail("l", "B' common_parent='%s' equals B common_parent='%s' (cross-input guard: top hierarchy should differ)" %
                  (BP.get("common_parent"), B.get("common_parent")))
        bp_cells = {m["cell"] for m in BP.get("modules", [])}
        b_cells = {m["cell"] for m in mods}
        if bp_cells == b_cells:
            _fail("l", "B' module cells identical to B (hardcoded?): %s" % sorted(bp_cells)[:5])
        if not bp_cells:
            _fail("l", "B' modules empty")
        shutil.rmtree(bptmp, ignore_errors=True)
        shutil.rmtree(btmp, ignore_errors=True)
        return {"passed": COND_LABELS, "n_conds": len(COND_LABELS)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    # standalone self-test: run check on reference_submit.zip
    ref_zip = os.path.join(os.path.dirname(__file__), "reference_submit.zip")
    if os.path.isfile(ref_zip):
        try:
            res = check(ref_zip, os.path.dirname(__file__))
            print("CHECK PASS", res)
        except AssertionError as e:
            print("CHECK FAIL", e); sys.exit(1)
    else:
        print("no reference_submit.zip found for self-test")
'''
with open(os.path.join(RDIR, "check.py"), "w", encoding="utf-8") as f:
    f.write(CHECK_SRC)

# ---------------------------------------------------------------------------
# negatives
# ---------------------------------------------------------------------------
# fake_empty: produces empty json -> fails (a/h)
fake_empty = '''#!/usr/bin/env python3
import json, sys
open("module_localization.json","w").write("{}")
print("empty")
'''
with open(os.path.join(NEGDIR, "fake_empty.py"), "w") as f:
    f.write(fake_empty)

# fake_print_expected: hardcodes A's expected output structure with A-specific tokens -> fails (m/i/l)
fake_print_expected = '''#!/usr/bin/env python3
# Hardcodes A's expected result (BnkGTop/CmFsLatch etc.) -> fails anti-hardcoding (m)
# and anti-common-parent (i) on B.
import json
out = {
  "total_blocks": 180,
  "problem_blocks": 126,
  "non_analog_blocks": 72,
  "analog_blocks_filtered": 54,
  "common_parent": "I_BnkGTopX4_gut",
  "modules": [
    {"cell": "T_CmFsLatchX6L", "total": 20, "NF": 17, "NM": 3, "HM": 0, "both": 0, "nf_pct": 85.0,
     "context": "BnkGTop_AC > D_BankLogicx2L", "category": "missing", "sample_path": "BnkGTop_AC|D_BankLogicx2L|T_CmFsLatchX6L"},
    {"cell": "R_NcCtrl", "total": 18, "NF": 15, "NM": 3, "HM": 0, "both": 0, "nf_pct": 83.3,
     "context": "BnkGTop_GE > R_NcCtrl", "category": "missing", "sample_path": "BnkGTop_GE|R_NcCtrl"},
  ]
}
json.dump(out, open("module_localization.json","w"), ensure_ascii=False, indent=2)
print("hardcoded A output")
'''
with open(os.path.join(NEGDIR, "fake_print_expected.py"), "w") as f:
    f.write(fake_print_expected)

# fake_core_deleted: parses blocks but skips common-parent stripping + analog filter -> fails (g/i)
fake_core_deleted = '''#!/usr/bin/env python3
import re, json
from collections import Counter, defaultdict
blocks = []
with open("mismatch_log.txt", errors="replace") as f:
    lines = f.read().split("\\n")
i=0; n=len(lines)
while i < n:
    m = re.search(r"^\\s*Compare #(\\d+)\\s+Net:\\s+(\\S+)", lines[i])
    if m:
        nl = m.group(2); mks=[]; i+=1
        while i < n and "Compare #" not in lines[i]:
            for mm in re.finditer(r">>\\s*([^<]+?)\\s*<<", lines[i]):
                mks.append(mm.group(1).strip())
            i+=1
        blocks.append({"nl": nl, "mks": mks})
    else:
        i+=1
# NO analog filter, NO common-parent stripping -> common parent appears as a module
stats = defaultdict(Counter); totals = Counter()
for b in blocks:
    if b["mks"] == ["OK"]: continue
    parts = b["nl"].split("/")
    cell = parts[3] if len(parts)>3 else b["nl"]  # common parent as cell!
    p = "NF" if "SPEF_NOT_FOUND" in b["mks"] else ("NM" if "NET NAME MISMATCH" in b["mks"] else "HM")
    stats[cell][p]+=1; totals[cell]+=1
mods=[]
for ct,tot in totals.items():
    s=stats[ct]
    mods.append({"cell":ct,"total":tot,"NF":s.get("NF",0),"NM":s.get("NM",0),"HM":s.get("HM",0),"both":0,
                 "nf_pct":round(s.get("NF",0)/tot*100,1) if tot else 0.0,"context":"","category":"mixed","sample_path":""})
mods.sort(key=lambda m:(-m["NF"],-m["total"]))
out={"total_blocks":len(blocks),"problem_blocks":len(blocks)-sum(1 for b in blocks if b["mks"]==["OK"]),
     "non_analog_blocks":len(blocks)-sum(1 for b in blocks if b["mks"]==["OK"]),
     "analog_blocks_filtered":0,"common_parent":"","modules":mods}
json.dump(out, open("module_localization.json","w"), ensure_ascii=False, indent=2)
print("core deleted: no analog filter, no common-parent strip")
'''
with open(os.path.join(NEGDIR, "fake_core_deleted.py"), "w") as f:
    f.write(fake_core_deleted)

# naive_no_analog_filter: parses + strips common parent but does NOT filter analog -> fails (g)
naive_no_analog = '''#!/usr/bin/env python3
import re, json
from collections import Counter, defaultdict
blocks = []
with open("mismatch_log.txt", errors="replace") as f:
    lines = f.read().split("\\n")
i=0; n=len(lines)
while i < n:
    m = re.search(r"^\\s*Compare #(\\d+)\\s+Net:\\s+(\\S+)", lines[i])
    if m:
        nl = m.group(2); mks=[]; i+=1
        while i < n and "Compare #" not in lines[i]:
            for mm in re.finditer(r">>\\s*([^<]+?)\\s*<<", lines[i]):
                mks.append(mm.group(1).strip())
            i+=1
        blocks.append({"nl": nl, "mks": mks})
    else:
        i+=1
problem=[b for b in blocks if b["mks"]!=["OK"]]
nets=[b["nl"] for b in problem]
# common prefix
sp=[n.split("/") for n in nets]; cpre=[]
for k in range(min(len(s) for s in sp)):
    seg=sp[0][k]
    if all(s[k]==seg for s in sp): cpre.append(seg)
    else: break
cpl=len(cpre)
def seg2cell(s):
    s=s[2:] if s.startswith("I_") else s
    return re.sub(r"(_?[A-Za-z]?\\d+)+_?$","",s)
def is_leaf(s): return bool(re.match(r"^I\\d+",s))
# NO analog filter
stats=defaultdict(Counter); totals=Counter(); ctx=defaultdict(set); samp=defaultdict(list)
for b in problem:
    parts=b["nl"].split("/"); rel=parts[cpl:-1]
    while rel and is_leaf(rel[-1]): rel=rel[:-1]
    if not rel: continue
    cells=[seg2cell(s) for s in rel]; dd=[]
    for c in cells:
        if dd and c==dd[-1]: continue
        dd.append(c)
    deepest=dd[-1] if dd else cells[-1]
    p="NF" if "SPEF_NOT_FOUND" in b["mks"] else ("NM" if "NET NAME MISMATCH" in b["mks"] else "HM")
    stats[deepest][p]+=1; totals[deepest]+=1
    ctx[deepest].add(" > ".join(dd[:2]))
    if len(samp[deepest])<1: samp[deepest].append("|".join(dd))
mods=[]
for ct,tot in totals.items():
    s=stats[ct]; nf=s.get("NF",0);nm=s.get("NM",0);hm=s.get("HM",0)
    cat="missing" if nf/tot>0.5 else ("rename" if nm/tot>0.8 else "mixed")
    mods.append({"cell":ct,"total":tot,"NF":nf,"NM":nm,"HM":hm,"both":0,"nf_pct":round(nf/tot*100,1) if tot else 0.0,
                 "context":" | ".join(sorted(ctx[ct])[:2]),"category":cat,"sample_path":samp[ct][0] if samp[ct] else ""})
mods.sort(key=lambda m:(-m["NF"],-m["total"]))
out={"total_blocks":len(blocks),"problem_blocks":len(problem),"non_analog_blocks":len(problem),
     "analog_blocks_filtered":0,"common_parent":cpre[-1] if cpre else "","modules":mods}
json.dump(out, open("module_localization.json","w"), ensure_ascii=False, indent=2)
print("naive: no analog filter")
'''
with open(os.path.join(NEGDIR, "naive_no_analog_filter.py"), "w") as f:
    f.write(naive_no_analog)

# naive_hardcode_a: hardcodes A's hierarchy skip (BnkGTopX4_gut) -> fails on B (j/i)
naive_hardcode_a = '''#!/usr/bin/env python3
import re, json
from collections import Counter, defaultdict
ANALOG_KW=["AG_","NEWBLSA_","VBL","LDO","REFGEN","REFLOGIC","TMSLP","ITEMP","VGCLAMP","DIGGEN","VREF","PLLBIAS","BIASGEN","XTLOSC"]
blocks=[]
with open("mismatch_log.txt", errors="replace") as f:
    lines=f.read().split("\\n")
i=0;n=len(lines)
while i<n:
    m=re.search(r"^\\s*Compare #(\\d+)\\s+Net:\\s+(\\S+)", lines[i])
    if m:
        nl=m.group(2);mks=[];i+=1
        while i<n and "Compare #" not in lines[i]:
            for mm in re.finditer(r">>\\s*([^<]+?)\\s*<<",lines[i]): mks.append(mm.group(1).strip())
            i+=1
        blocks.append({"nl":nl,"mks":mks})
    else: i+=1
problem=[b for b in blocks if b["mks"]!=["OK"]]
def seg2cell(s):
    s=s[2:] if s.startswith("I_") else s
    return re.sub(r"(_?[A-Za-z]?\\d+)+_?$","",s)
def is_leaf(s): return bool(re.match(r"^I\\d+",s))
def is_analog(s):
    u=s.upper()
    return any(k in u for k in ANALOG_KW)
# HARDCODED A-specific common parent skip
stats=defaultdict(Counter);totals=Counter();ctx=defaultdict(set);samp=defaultdict(list);analog=0
for b in problem:
    parts=b["nl"].split("/")
    # hardcoded: skip BnkGTopX4_gut (A-specific!) -> fails on B
    rel=[p for p in parts[3:-1] if p!="I_BnkGTopX4_gut"]
    while rel and is_leaf(rel[-1]): rel=rel[:-1]
    if not rel: continue
    cells=[seg2cell(s) for s in rel];dd=[]
    for c in cells:
        if dd and c==dd[-1]:continue
        dd.append(c)
    full="|".join(dd);deepest=dd[-1] if dd else cells[-1]
    if is_analog(full): analog+=1; continue
    p="NF" if "SPEF_NOT_FOUND" in b["mks"] else ("NM" if "NET NAME MISMATCH" in b["mks"] else "HM")
    stats[deepest][p]+=1;totals[deepest]+=1;ctx[deepest].add(" > ".join(dd[:2]))
    if len(samp[deepest])<1: samp[deepest].append(full)
mods=[]
for ct,tot in totals.items():
    s=stats[ct];nf=s.get("NF",0);nm=s.get("NM",0);hm=s.get("HM",0)
    cat="missing" if nf/tot>0.5 else ("rename" if nm/tot>0.8 else "mixed")
    mods.append({"cell":ct,"total":tot,"NF":nf,"NM":nm,"HM":hm,"both":0,"nf_pct":round(nf/tot*100,1) if tot else 0.0,
                 "context":" | ".join(sorted(ctx[ct])[:2]),"category":cat,"sample_path":samp[ct][0] if samp[ct] else ""})
mods.sort(key=lambda m:(-m["NF"],-m["total"]))
out={"total_blocks":len(blocks),"problem_blocks":len(problem),"non_analog_blocks":len(problem)-analog,
     "analog_blocks_filtered":analog,"common_parent":"I_BnkGTopX4_gut","modules":mods}
json.dump(out, open("module_localization.json","w"), ensure_ascii=False, indent=2)
print("naive: hardcode A common parent")
'''
with open(os.path.join(NEGDIR, "naive_hardcode_a.py"), "w") as f:
    f.write(naive_hardcode_a)

# ---------------------------------------------------------------------------
# negative_selftest.py — pack each fake into submit.zip, run check, expect FAIL,
# collect which cond each fake trips (must be DISTINCT to prove independence).
# ---------------------------------------------------------------------------
NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest: pack each fake as submit.zip, run check(), expect FAIL,
collect first-failed cond label. Pass iff all fakes FAIL and >=2 distinct
cond labels are tripped (proving the conditions are independent).
"""
import os, sys, json, zipfile, tempfile, shutil, re, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
CHK = os.path.join(HERE, "check.py")
sys.path.insert(0, HERE)
import check as CHKMOD

FAKES = [
    ("fake_empty", "fake_empty.py"),
    ("fake_print_expected", "fake_print_expected.py"),
    ("fake_core_deleted", "fake_core_deleted.py"),
    ("naive_no_analog_filter", "naive_no_analog_filter.py"),
    ("naive_hardcode_a", "naive_hardcode_a.py"),
]

def first_fail_cond(submit_zip):
    try:
        CHKMOD.check(submit_zip, HERE)
    except AssertionError as e:
        m = re.search(r"\[cond\s+([a-n])\s+FAIL\]", str(e))
        return (m.group(1) if m else "?", str(e)[:200])
    except Exception as e:
        m = re.search(r"\[cond\s+([a-n])\s+FAIL\]", str(e))
        return (m.group(1) if m else "X", "EXC: %s" % str(e)[:200])
    return (None, "PASS (unexpected!)")

results = {}
for name, fname in FAKES:
    src = os.path.join(NEG, fname)
    if not os.path.isfile(src):
        results[name] = ("MISSING", "fake file not found"); continue
    tmp = tempfile.mkdtemp(prefix="negst_")
    try:
        shutil.copy(src, os.path.join(tmp, "spef_module_localize.py"))
        # provide the VISIBLE A log so the fake produces a "submitted" JSON
        a_log = os.path.join(CHKMOD.CASE_ASSETS, "mismatch_log_A.txt")
        if os.path.isfile(a_log):
            shutil.copy(a_log, os.path.join(tmp, "mismatch_log.txt"))
        # run the fake to produce module_localization.json (the "submitted" artifact)
        import subprocess
        r = subprocess.run([sys.executable, "spef_module_localize.py"], cwd=tmp,
                           capture_output=True, text=True, timeout=60)
        # build submit.zip
        zip_path = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            z.write(os.path.join(tmp, "spef_module_localize.py"), "spef_module_localize.py")
            jout = os.path.join(tmp, "module_localization.json")
            if os.path.isfile(jout):
                z.write(jout, "module_localization.json")
            else:
                # write an empty one so (a) doesn't trip for json-missing fakes
                z.writestr("module_localization.json", "{}")
        cond, msg = first_fail_cond(zip_path)
        results[name] = (cond, msg)
    except Exception as e:
        results[name] = ("EXC", str(e)[:200])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

print("=== negative_selftest results ===")
distinct = set()
all_fail = True
for name, (cond, msg) in results.items():
    print("%s -> cond=%s  %s" % (name, cond, msg))
    if cond is None:
        all_fail = False
    if cond and cond not in ("X", "?", "MISSING", "EXC"):
        distinct.add(cond)
print("\nall_fail=%s  distinct_conds=%d  distinct=%s" % (all_fail, len(distinct), sorted(distinct)))
ok = all_fail and len(distinct) >= 2
print("NEG_RC=%d  RESULT=%s" % (0 if ok else 1, "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
'''
with open(os.path.join(RDIR, "negative_selftest.py"), "w", encoding="utf-8") as f:
    f.write(NEG_SELFTEST)

# ---------------------------------------------------------------------------
# reference_submit.zip — pack the ref script + run it on A to produce JSON
# ---------------------------------------------------------------------------
# Run ref on A to produce module_localization.json (A's output, for the submitted json)
tmp = tempfile.mkdtemp(prefix="refbuild_")
shutil.copy(os.path.join(RDIR, "spef_module_localize_ref.py"), os.path.join(tmp, "spef_module_localize.py"))
shutil.copy(os.path.join(ADIR, "mismatch_log_A.txt"), os.path.join(tmp, "mismatch_log.txt"))
r = subprocess.run([sys.executable, "spef_module_localize.py"], cwd=tmp, capture_output=True, text=True, timeout=60)
print("REF on A: exit=%d out=%s err=%s" % (r.returncode, r.stdout[:200], r.stderr[:200]))
ref_zip = os.path.join(RDIR, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(tmp, "spef_module_localize.py"), "spef_module_localize.py")
    z.write(os.path.join(tmp, "module_localization.json"), "module_localization.json")
shutil.rmtree(tmp, ignore_errors=True)

print("\n=== Build complete ===")
print("assets dir: %s" % ADIR)
print("reference dir: %s" % RDIR)
for fn in sorted(os.listdir(ADIR)):
    p = os.path.join(ADIR, fn)
    sz = os.path.getsize(p) if os.path.isfile(p) else 0
    print("  A/%s  %s" % (fn, ("%d bytes" % sz) if os.path.isfile(p) else "<dir>"))
for fn in sorted(os.listdir(HDIR)):
    p = os.path.join(HDIR, fn)
    print("  A/hidden/%s  %d bytes" % (fn, os.path.getsize(p)))
for fn in sorted(os.listdir(RDIR)):
    p = os.path.join(RDIR, fn)
    sz = os.path.getsize(p) if os.path.isfile(p) else 0
    print("  R/%s  %s" % (fn, ("%d bytes" % sz) if os.path.isfile(p) else "<dir>"))
for fn in sorted(os.listdir(NEGDIR)):
    p = os.path.join(NEGDIR, fn)
    print("  R/negative/%s  %d bytes" % (fn, os.path.getsize(p)))
