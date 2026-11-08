#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-ConnChkSummaryGen-001 (shard C r258, physical_verify, B-synthesized L1)."""
import os, json, subprocess, zipfile, shutil, hashlib, sys, io

CASE = "EDA-Eval-DesignFlow-ConnChkSummaryGen-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = f"{REPO}/assets/{CASE}"
HID = f"{AST}/hidden"
REF = f"{REPO}/reference/{CASE}"
NEG = f"{REF}/negative"
for d in (AST, HID, REF, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- reference solution ----------
GOLDEN = r'''#!/usr/bin/env python3
"""Connectivity-check summary report generator.

Grounded on the drcConnect tool's connectivity_check/summary.py + graph.py:
  - normalize_connectivity: >3-layer edges [S,V,T1,T2,...] split into 3-layer
    [S,V,Ti] (one per target) and every ordered target pair (i<j) yields a
    shield "S V : Ti->Tj".
  - find_all_paths: DFS from a bottom layer; 3-layer edges [S,V,T] include the
    via V in the path (S -> V -> T), 2-layer edges [S,T] do not (S -> T); a via
    or node may not repeat in a single path.
  - format_report: 72-"=" header, per-run block, 72-"=" footer; paths and
    shields each on their own line with 17-space continuation indent; sameNet/
    diffNet verdict = "HAS ERRORS" if count>0 else "OK"; status passed through.
"""
import sys, json, argparse, os

SEP = "=" * 72


def normalize_connectivity(connectivity):
    norm_edges = []
    shields = []
    for edge in connectivity:
        if len(edge) <= 3:
            norm_edges.append(list(edge))
            continue
        s, v = edge[0], edge[1]
        targets = edge[2:]
        for t in targets:
            norm_edges.append([s, v, t])
        for i in range(len(targets)):
            for t in targets[i + 1:]:
                shields.append("%s %s : %s->%s" % (s, v, targets[i], t))
    return norm_edges, shields


def find_all_paths(connectivity, start, path=None):
    path = (path if path is not None else []) + [start]
    valid = [e for e in connectivity if e[0] == start]
    if not valid:
        return [path]
    direct = [(e[0], e[1]) for e in valid if len(e) == 2]
    indirect = [(e[0], e[1], e[2]) for e in valid if len(e) == 3]
    all_paths = []
    for _, inter, nxt in indirect:
        if inter not in path and nxt not in path:
            new_path = path + [inter]
            if new_path not in all_paths:
                all_paths.extend(find_all_paths(connectivity, nxt, new_path))
    for _, nxt in direct:
        if nxt not in path:
            new_path = path
            if new_path not in all_paths:
                all_paths.extend(find_all_paths(connectivity, nxt, new_path))
    return all_paths


def compute_paths(connectivity, bottom_layers):
    norm_edges, _ = normalize_connectivity(connectivity)
    paths = []
    seen = set()
    for start in bottom_layers:
        for p in find_all_paths(norm_edges, start):
            key = tuple(p)
            if key not in seen:
                seen.add(key)
                paths.append(p)
    return paths


def compute_shields(connectivity):
    _, shields = normalize_connectivity(connectivity)
    return shields


def mode_line(label, groups):
    verdict = "HAS ERRORS" if groups else "OK"
    return "  %s: %d data group(s)  [%s]" % (label, groups, verdict)


def format_report(config, meta):
    base_dir = config.get("base_dir", ".")
    generated = config.get("generated", "")
    blocks = config.get("blocks", [])
    lines = []
    lines.append(SEP)
    lines.append(" Connectivity Check Summary")
    lines.append(" generated : " + generated)
    lines.append(" base dir  : " + os.path.abspath(base_dir))
    lines.append(SEP)
    for i, blk in enumerate(blocks, 1):
        name = blk.get("name", "run_%d" % i)
        connectivity = blk.get("connectivity", [])
        bottom = blk.get("bottomLayer", [])
        paths = compute_paths(connectivity, bottom)
        shields = compute_shields(connectivity)
        m = meta.get(name, {})
        lines.append("")
        lines.append("[" + name + "]")
        path_lines = [" -> ".join(p) for p in paths] if paths else ["(no path resolved)"]
        lines.append("  path(s)      : " + path_lines[0])
        for extra in path_lines[1:]:
            lines.append("                 " + extra)
        if shields:
            lines.append("  shields       : " + shields[0])
            for extra in shields[1:]:
                lines.append("                 " + extra)
        lines.append(mode_line("sameNet", m.get("sameNet", 0)))
        lines.append(mode_line("diffNet", m.get("diffNet", 0)))
        lines.append("  status   : " + m.get("status", "OK"))
    lines.append("")
    lines.append(SEP)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("meta")
    ap.add_argument("-o", "--output", default="sum.rep")
    a = ap.parse_args()
    config = json.load(open(a.config))
    meta = json.load(open(a.meta))
    text = format_report(config, meta)
    with open(a.output, "w") as f:
        f.write(text + "\n")
    print("wrote %s (%d bytes, %d runs)" % (a.output, len(text) + 1, len(config.get("blocks", []))))


if __name__ == "__main__":
    main()
'''

# ---------- inputs ----------
CONFIG_A = {
    "base_dir": "/home/eval_user/drcConnect/runA",
    "generated": "2026-11-09 01:30:00",
    "blocks": [
        {"name": "run_1",
         "connectivity": [["PG", "PC", "M1"], ["M1", "V1", "M2"], ["M2", "V2", "M3"]],
         "bottomLayer": ["PG"],
         "connectOPC011": ["CONNECT OPC011 PGnet"],
         "skip_via_connect": ["CT"]},
        {"name": "run_2",
         "connectivity": [["AA", "BB", "CC", "DD", "EE"]],
         "bottomLayer": ["AA"],
         "connectOPC011": ["CONNECT OPC011 AA"]},
        {"name": "run_3",
         "connectivity": [["MT", "CT", "M0"], ["M0", "VX", "NBP"], ["M0", "VX", "TCP"], ["MT", "VY", "TOP"]],
         "bottomLayer": ["MT", "M0"],
         "connectOPC011": ["CONNECT OPC011 MT", "CONNECT OPC011 M0"]},
        {"name": "run_4",
         "connectivity": [["X", "Y"], ["Y", "Z"]],
         "bottomLayer": ["X"],
         "connectOPC011": ["CONNECT OPC011 X"]},
    ],
}
META_A = {
    "run_1": {"sameNet": 0, "diffNet": 4, "status": "OK"},
    "run_2": {"sameNet": 2, "diffNet": 0, "status": "OK"},
    "run_3": {"sameNet": 0, "diffNet": 6, "status": "OK"},
    "run_4": {"sameNet": 0, "diffNet": 3, "status": "OK"},
}

CONFIG_B = {
    "base_dir": "/home/eval_user/drcConnect/runB",
    "generated": "2026-11-09 02:10:00",
    "blocks": [
        {"name": "run_1",
         "connectivity": [["P0", "V0", "T1", "T2", "T3", "T4"]],
         "bottomLayer": ["P0"],
         "connectOPC011": ["CONNECT OPC011 P0"]},
        {"name": "run_2",
         "connectivity": [["B1", "C1", "M1"], ["B2", "C2", "M1"], ["B3", "C3", "M1"], ["M1", "C4", "TOP"]],
         "bottomLayer": ["B1", "B2", "B3"],
         "connectOPC011": ["CONNECT OPC011 B1", "CONNECT OPC011 B2", "CONNECT OPC011 B3"]},
        {"name": "run_3",
         "connectivity": [["A", "B"], ["B", "C"], ["C", "D"]],
         "bottomLayer": ["A"],
         "connectOPC011": ["CONNECT OPC011 A"]},
        {"name": "run_4",
         "connectivity": [["Q0", "QV", "Q1", "Q2"], ["Q2", "QV2", "Q3"]],
         "bottomLayer": ["Q0"],
         "connectOPC011": ["CONNECT OPC011 Q0"],
         "skip_via_connect": ["QV"]},
        {"name": "run_5",
         "connectivity": [["S1", "SV", "E1"], ["S1", "SV", "E2"]],
         "bottomLayer": ["S1"],
         "connectOPC011": ["CONNECT OPC011 S1"],
         "skip_via_connect": ["SV"]},
    ],
}
META_B = {
    "run_1": {"sameNet": 0, "diffNet": 8, "status": "OK"},
    "run_2": {"sameNet": 0, "diffNet": 0, "status": "OK"},
    "run_3": {"sameNet": 1, "diffNet": 2, "status": "OK"},
    "run_4": {"sameNet": 0, "diffNet": 5, "status": "DRC ERROR (calibre run failed - see log)"},
    "run_5": {"sameNet": 0, "diffNet": 3, "status": "OK"},
}

# B2: structurally distinct (different layer names, 3 runs, a 5-target edge, a multi-bottom chain)
CONFIG_B2 = {
    "base_dir": "/home/eval_user/drcConnect/runB2",
    "generated": "2026-11-09 03:00:00",
    "blocks": [
        {"name": "run_1",
         "connectivity": [["W0", "WV", "W1", "W2", "W3"]],
         "bottomLayer": ["W0"],
         "connectOPC011": ["CONNECT OPC011 W0"]},
        {"name": "run_2",
         "connectivity": [["K1", "KC", "KM"], ["K2", "KC2", "KM"], ["KM", "KD", "END"]],
         "bottomLayer": ["K1", "K2"],
         "connectOPC011": ["CONNECT OPC011 K1", "CONNECT OPC011 K2"]},
        {"name": "run_3",
         "connectivity": [["R", "S"], ["S", "T"]],
         "bottomLayer": ["R"],
         "connectOPC011": ["CONNECT OPC011 R"]},
    ],
}
META_B2 = {
    "run_1": {"sameNet": 0, "diffNet": 7, "status": "OK"},
    "run_2": {"sameNet": 3, "diffNet": 1, "status": "OK"},
    "run_3": {"sameNet": 0, "diffNet": 0, "status": "result file missing - run may not have completed"},
}

# ---------- write assets ----------
def wj(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

wj(f"{AST}/config_A.json", CONFIG_A)
wj(f"{AST}/runs_meta_A.json", META_A)
wj(f"{HID}/config_B.json", CONFIG_B)
wj(f"{HID}/runs_meta_B.json", META_B)
wj(f"{HID}/config_B2.json", CONFIG_B2)
wj(f"{HID}/runs_meta_B2.json", META_B2)
wj(f"{HID}/hidden_manifest.json", {"inputs": ["config_B.json", "runs_meta_B.json", "config_B2.json", "runs_meta_B2.json"],
                                   "note": "B and B2 are structurally distinct from A; check runs candidate on both"})

PROMPT = """我有一个 DRC 连通性检查工具（drcConnect），它的 config_multi 里每个 block 定义了一组 connectivity 层连接边、bottomLayer、connectOPC011（以及可选的 skip_via_connect）。工具跑完会在每个 run 目录下产 sameNet/diffNet 的 rdb 计数和一个 status。现在我需要你写一个**离线报告生成器** conn_summary.py，读 config.json（含 base_dir、generated、blocks 列表）和 runs_meta.json（每个 run 的 sameNet/diffNet 计数 + status），按工具原有的 sum.rep 格式输出报告。

要求：
1. **path 计算**：从每个 block 的 bottomLayer 出发，沿 connectivity 边做 DFS 图遍历。3 层边 [S, V, T] 路径里要包含 via V（即 S -> V -> T）；2 层边 [S, T] 路径里不含 via（即 S -> T）。同一个 path 里 via 和节点不能重复。多个 bottomLayer 的路径去重后合并。
2. **shields 计算**：connectivity 里**超过 3 层**的边 [S, V, T1, T2, ...] 要拆成若干 3 层边 [S, V, Ti]（每个目标一条），并且目标按列表顺序的每个有序对 (Ti, Tj)，i<j，产生一条 shield，格式 `S V : Ti->Tj`。≤3 层的边不产生 shield。
3. **sum.rep 格式**：每条 path 单独占一行、每条 shield 单独占一行；第一行跟在标签 `path(s)` / `shields` 后，续行用空格缩进对齐到冒号后。每个 run 块依次为 `[run_N]`、`path(s)`、`shields`（有 shields 才输出这一段）、`sameNet`、`diffNet`、`status`。sameNet/diffNet 行格式 `  sameNet: <N> data group(s)  [OK|HAS ERRORS]`，N>0 时为 HAS ERRORS 否则 OK。status 行 `  status   : <status>`，status 直接取自 runs_meta。报告开头是 72 个 `=` 的分隔行 + title + generated + base dir + 分隔行；结尾是空行 + 72 个 `=` 的分隔行。
4. connectOPC011 和 skip_via_connect 字段在 config 里存在，但**报告里不直接用到**（path/shields 只来自 connectivity 和 bottomLayer）；你的脚本要能正常解析含这些字段的 config 而不报错。
5. generated 时间戳从 config 的 `generated` 字段读取（保证可复现）。

附件 config_A.json 和 runs_meta_A.json 是一组示例（可见输入 A）。你的脚本要能处理任意同结构的 config/meta。把 conn_summary.py 打包到 outputs/submit.zip（zip 里只放 conn_summary.py 一个文件）。"""

with open(f"{AST}/prompt.txt", "w") as f:
    f.write(PROMPT)

with open(f"{AST}/task_brief.md", "w") as f:
    f.write("交付：outputs/submit.zip（仅含 conn_summary.py 一个文件）\n"
            "接口：conn_summary.py <config.json> <runs_meta.json> -o <sum.rep>\n"
            "判分：在隐藏输入 B/B2 上运行候选，校验 sum.rep 的路径/屏蔽/计数/格式是否与参考一致\n")

# ---------- reference ----------
with open(f"{REF}/golden_solution.py", "w") as f:
    f.write(GOLDEN)

# generate golden outputs by running the golden solution
import tempfile
for tag, cfg, meta in [("A", CONFIG_A, META_A), ("B", CONFIG_B, META_B), ("B2", CONFIG_B2, META_B2)]:
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "config.json"); wj(cp, cfg)
        mp = os.path.join(td, "meta.json"); wj(mp, meta)
        op = os.path.join(td, "sum.rep")
        r = subprocess.run([sys.executable, f"{REF}/golden_solution.py", cp, mp, "-o", op], capture_output=True, text=True)
        assert r.returncode == 0, f"golden {tag} failed: {r.stderr}"
        out = open(op).read()
        with open(f"{REF}/golden_{tag}.sum.rep", "w") as f:
            f.write(out)
        print(f"golden {tag}: {len(out)} bytes, runs={len(cfg['blocks'])}")

# ---------- check.py ----------
CHECK = r'''#!/usr/bin/env python3
"""Check EDA-Eval-DesignFlow-ConnChkSummaryGen-001.

16 independent conditions (a-p), each can FAIL independently. Runs the
candidate on hidden inputs B and B2 (structurally distinct from visible A).
"""
import os, sys, json, zipfile, subprocess, tempfile, re, shutil

SEP = "=" * 72
PY = sys.executable

def _extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)

def _run_cand(cand, config, meta, out):
    return subprocess.run([PY, cand, config, meta, "-o", out],
                          capture_output=True, text=True, timeout=120)

def _expected_paths_shields(config):
    """Re-derive expected paths + shields per run with the reference graph logic."""
    def normalize(connectivity):
        ne, sh = [], []
        for e in connectivity:
            if len(e) <= 3:
                ne.append(list(e)); continue
            s, v, tgt = e[0], e[1], e[2:]
            for t in tgt: ne.append([s, v, t])
            for i in range(len(tgt)):
                for t in tgt[i+1:]:
                    sh.append("%s %s : %s->%s" % (s, v, tgt[i], t))
        return ne, sh
    def find_all(connectivity, start, path=None):
        path = (path if path is not None else []) + [start]
        valid = [e for e in connectivity if e[0] == start]
        if not valid: return [path]
        direct = [(e[0], e[1]) for e in valid if len(e) == 2]
        indirect = [(e[0], e[1], e[2]) for e in valid if len(e) == 3]
        ap = []
        for _, inter, nxt in indirect:
            if inter not in path and nxt not in path:
                np_ = path + [inter]
                if np_ not in ap:
                    ap.extend(find_all(connectivity, nxt, np_))
        for _, nxt in direct:
            if nxt not in path:
                np_ = path
                if np_ not in ap:
                    ap.extend(find_all(connectivity, nxt, np_))
        return ap
    res = {}
    for blk in config["blocks"]:
        ne, sh = normalize(blk["connectivity"])
        paths, seen = [], set()
        for s in blk["bottomLayer"]:
            for p in find_all(ne, s):
                k = tuple(p)
                if k not in seen: seen.add(k); paths.append(" -> ".join(p))
        res[blk["name"]] = {"paths": paths, "shields": sh}
    return res

def _check(deliverable, workdir):
    CONDITIONS = []
    def cond(label, ok, detail=""):
        CONDITIONS.append((label, bool(ok), detail))
    tmp = tempfile.mkdtemp(prefix="connchk_")
    try:
        # a. zip valid + contains conn_summary.py
        try:
            _extract(deliverable, tmp)
            has_py = os.path.isfile(os.path.join(tmp, "conn_summary.py"))
            cond("a", has_py, "zip must contain conn_summary.py")
        except Exception as e:
            cond("a", False, "bad zip: %s" % e); return CONDITIONS
        cand = os.path.join(tmp, "conn_summary.py")
        # b. py_compile
        r = subprocess.run([PY, "-m", "py_compile", cand], capture_output=True, text=True)
        cond("b", r.returncode == 0, "py_compile failed: %s" % r.stderr[:200])
        # c. stdlib only
        src = open(cand).read()
        third = re.findall(r'^\s*(?:import|from)\s+(gdspy|calibre|numpy|pandas|sklearn|scipy|matplotlib|aether|pyAether)\b', src, re.M)
        cond("c", not third, "third-party imports: %s" % third)
        # locate hidden inputs (relative to this check.py)
        ref_dir = os.path.dirname(os.path.abspath(__file__))
        hidden = os.path.join(ref_dir, "..", "..", "assets", "EDA-Eval-DesignFlow-ConnChkSummaryGen-001", "hidden")
        cfgB = os.path.join(hidden, "config_B.json"); metaB = os.path.join(hidden, "runs_meta_B.json")
        cfgB2 = os.path.join(hidden, "config_B2.json"); metaB2 = os.path.join(hidden, "runs_meta_B2.json")
        # d. hidden B run: exit 0 + non-empty sum.rep
        outB = os.path.join(tmp, "sum_B.rep")
        rB = _run_cand(cand, cfgB, metaB, outB)
        ok_d = (rB.returncode == 0 and os.path.isfile(outB) and os.path.getsize(outB) > 0)
        cond("d", ok_d, "B run rc=%d stderr=%s" % (rB.returncode, rB.stderr[:200]))
        if not ok_d:
            return CONDITIONS
        txtB = open(outB).read()
        cfgBo = json.load(open(cfgB)); metaBo = json.load(open(metaB))
        expB = _expected_paths_shields(cfgBo)
        # e. header block (5 lines: SEP, title, generated, base dir, SEP)
        head = txtB.splitlines()[:5]
        ok_e = (len(head) == 5 and head[0] == SEP and head[1] == " Connectivity Check Summary"
                and head[2].startswith(" generated : ") and head[3].startswith(" base dir  : ")
                and head[4] == SEP and head[2].strip().endswith(cfgBo["generated"]))
        cond("e", ok_e, "header mismatch: %r" % head)
        # f. exactly N [run_X] blocks named run_1..run_N in order
        blocks = re.findall(r'^\[run_\d+\]$', txtB, re.M)
        names = [b.strip("[]") for b in blocks]
        exp_names = [b["name"] for b in cfgBo["blocks"]]
        ok_f = (names == exp_names)
        cond("f", ok_f, "block names %r != %r" % (names, exp_names))
        # split into per-run chunks
        chunks = re.split(r'^\[run_\d+\]$', txtB, flags=re.M)
        # chunks[0] = header; chunks[1..N] = per-run bodies
        # g. each run block has a "  path(s)      :" line
        ok_g = all(re.match(r'^  path\(s\)      : ', c.lstrip("\n"), re.M) or re.search(r'^  path\(s\)      : ', c, re.M) for c in chunks[1:])
        # use search to be safe
        ok_g = all(re.search(r'^  path\(s\)      : ', c, re.M) for c in chunks[1:])
        cond("g", ok_g, "missing path(s) label in some run")
        # h. paths per-line: continuation lines start with exactly 17 spaces (not comma-joined on one line)
        ok_h = True; hdetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            pm = re.search(r'^  path\(s\)      : (.*)\n((?:                 .*\n?)*)', c, re.M)
            if not pm: ok_h = False; hdetail = "no path block %s" % nm; break
            # reject comma-join of the old format: a single path line containing ", " between two paths
            first = pm.group(1)
            if " -> " in first and ", " in first:
                # could be legitimate? paths are joined by " -> "; old format joined paths by ", "
                ok_h = False; hdetail = "comma-joined paths in %s: %r" % (nm, first[:80]); break
            cont = pm.group(2)
            for ln in cont.splitlines():
                if ln and not ln.startswith("                 "):
                    ok_h = False; hdetail = "bad continuation indent %s: %r" % (nm, ln[:40]); break
            if not ok_h: break
        cond("h", ok_h, hdetail or "paths per-line OK")
        # i. paths content correct
        ok_i = True; idetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            pm = re.search(r'^  path\(s\)      : (.*)\n((?:                 .*\n?)*)', c, re.M)
            got = [pm.group(1)] if pm else []
            if pm and pm.group(2):
                for ln in pm.group(2).splitlines():
                    if ln: got.append(ln.strip())
            exp_paths = expB[nm]["paths"]
            if got != exp_paths:
                ok_i = False; idetail = "paths %s: got %r != exp %r" % (nm, got, exp_paths); break
        cond("i", ok_i, idetail or "paths content OK")
        # j. shields present only for runs with >3-layer edges; absent otherwise
        ok_j = True; jdetail = ""
        for c, blk in zip(chunks[1:], cfgBo["blocks"]):
            has_shield_label = bool(re.search(r'^  shields       : ', c, re.M))
            has_multi = any(len(e) > 3 for e in blk["connectivity"])
            if has_shield_label != has_multi:
                ok_j = False; jdetail = "shields presence %s: label=%s multi=%s" % (blk["name"], has_shield_label, has_multi); break
        cond("j", ok_j, jdetail or "shields presence OK")
        # k. shields content correct (all ordered target pairs)
        ok_k = True; kdetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            sm = re.search(r'^  shields       : (.*)\n((?:                 .*\n?)*)', c, re.M)
            if not sm:
                if expB[nm]["shields"]:
                    ok_k = False; kdetail = "missing shields %s" % nm; break
                continue
            got = [sm.group(1)] + [ln.strip() for ln in sm.group(2).splitlines() if ln]
            if got != expB[nm]["shields"]:
                ok_k = False; kdetail = "shields %s: got %r != exp %r" % (nm, got, expB[nm]["shields"]); break
        cond("k", ok_k, kdetail or "shields content OK")
        # l. shields per-line (17-space continuation, not "; "-joined)
        ok_l = True; ldetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            sm = re.search(r'^  shields       : (.*)\n((?:                 .*\n?)*)', c, re.M)
            if not sm: continue
            first = sm.group(1)
            if "; " in first:
                ok_l = False; ldetail = "semicolon-joined shields %s: %r" % (nm, first[:80]); break
            for ln in sm.group(2).splitlines():
                if ln and not ln.startswith("                 "):
                    ok_l = False; ldetail = "bad shield indent %s: %r" % (nm, ln[:40]); break
            if not ok_l: break
        cond("l", ok_l, ldetail or "shields per-line OK")
        # m. sameNet line correct
        ok_m = True; mdetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            sm = re.search(r'^  sameNet: (\d+) data group\(s\)  \[(OK|HAS ERRORS)\]$', c, re.M)
            if not sm: ok_m = False; mdetail = "no sameNet line %s" % nm; break
            n = int(sm.group(1)); verd = sm.group(2)
            exp_n = metaBo[nm]["sameNet"]; exp_v = "HAS ERRORS" if exp_n else "OK"
            if n != exp_n or verd != exp_v:
                ok_m = False; mdetail = "sameNet %s: got %d/%s exp %d/%s" % (nm, n, verd, exp_n, exp_v); break
        cond("m", ok_m, mdetail or "sameNet OK")
        # n. diffNet line correct
        ok_n = True; ndetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            sm = re.search(r'^  diffNet: (\d+) data group\(s\)  \[(OK|HAS ERRORS)\]$', c, re.M)
            if not sm: ok_n = False; ndetail = "no diffNet line %s" % nm; break
            n = int(sm.group(1)); verd = sm.group(2)
            exp_n = metaBo[nm]["diffNet"]; exp_v = "HAS ERRORS" if exp_n else "OK"
            if n != exp_n or verd != exp_v:
                ok_n = False; ndetail = "diffNet %s: got %d/%s exp %d/%s" % (nm, n, verd, exp_n, exp_v); break
        cond("n", ok_n, ndetail or "diffNet OK")
        # o. status line correct
        ok_o = True; odetail = ""
        for c, nm in zip(chunks[1:], exp_names):
            sm = re.search(r'^  status   : (.*)$', c, re.M)
            if not sm: ok_o = False; odetail = "no status line %s" % nm; break
            if sm.group(1) != metaBo[nm]["status"]:
                ok_o = False; odetail = "status %s: got %r exp %r" % (nm, sm.group(1), metaBo[nm]["status"]); break
        cond("o", ok_o, odetail or "status OK")
        # p. cross-input guard: re-run candidate on B2; assert B2 paths/shields correct (anti hardcoded A or B)
        outB2 = os.path.join(tmp, "sum_B2.rep")
        rB2 = _run_cand(cand, cfgB2, metaB2, outB2)
        ok_p = (rB2.returncode == 0 and os.path.isfile(outB2) and os.path.getsize(outB2) > 0)
        if ok_p:
            txtB2 = open(outB2).read(); cfgB2o = json.load(open(cfgB2)); expB2 = _expected_paths_shields(cfgB2o)
            chk2 = re.split(r'^\[run_\d+\]$', txtB2, flags=re.M)
            for c, nm in zip(chk2[1:], [b["name"] for b in cfgB2o["blocks"]]):
                pm = re.search(r'^  path\(s\)      : (.*)\n((?:                 .*\n?)*)', c, re.M)
                got = [pm.group(1)] if pm else []
                if pm and pm.group(2):
                    for ln in pm.group(2).splitlines():
                        if ln: got.append(ln.strip())
                if got != expB2[nm]["paths"]:
                    ok_p = False; break
                sm = re.search(r'^  shields       : (.*)\n((?:                 .*\n?)*)', c, re.M)
                gsh = ([sm.group(1)] + [ln.strip() for ln in sm.group(2).splitlines() if ln]) if sm else []
                if gsh != expB2[nm]["shields"]:
                    ok_p = False; break
        cond("p", ok_p, "B2 cross-input guard (rc=%d)" % rB2.returncode)
        return CONDITIONS
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check(deliverable, workdir):
    conds = _check(deliverable, workdir)
    passed = sum(1 for _, ok, _ in conds if ok)
    total = len(conds)
    print("ConnChkSummaryGen check: %d/%d conditions passed" % (passed, total))
    for label, ok, detail in conds:
        print("  [%s] %s %s" % ("PASS" if ok else "FAIL", label, detail))
    if passed != total:
        raise AssertionError("ConnChkSummaryGen: %d/%d conditions failed" % (total - passed, total))
    return True


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        check(sys.argv[1], sys.argv[2])
    else:
        print("usage: check.py <submit.zip> <workdir>")
        sys.exit(2)
'''
with open(f"{REF}/check.py", "w") as f:
    f.write(CHECK)

# ---------- negatives ----------
NEG_EMPTY = '# conn_summary.py - empty shell\nimport sys\nsys.exit(0)\n'
NEG_PRINT = r'''# prints a pre-baked sum.rep for A (hardcoded) -- fails cross-input (p) and content on B
import sys
out = """========================================================================
 Connectivity Check Summary
 generated : 2026-11-09 01:30:00
 base dir  : /home/eval_user/drcConnect/runA
========================================================================

[run_1]
  path(s)      : PG -> PC -> M1 -> V1 -> M2 -> V2 -> M3
  sameNet: 0 data group(s)  [OK]
  diffNet: 4 data group(s)  [HAS ERRORS]
  status   : OK

========================================================================
"""
import sys
a = sys.argv
with open(a[ a.index("-o")+1 ] if "-o" in a else "sum.rep", "w") as f:
    f.write(out + "\n")
'''
NEG_HARDcoded_A = r'''# hardcoded_A: only ever emits A's run_1 regardless of input -- fails i/k/m/n/o/p
import sys, json
out = ("========================================================================\n"
" Connectivity Check Summary\n"
" generated : 2026-11-09 01:30:00\n"
" base dir  : /home/eval_user/drcConnect/runA\n"
"========================================================================\n"
"\n"
"[run_1]\n"
"  path(s)      : PG -> PC -> M1 -> V1 -> M2 -> V2 -> M3\n"
"  sameNet: 0 data group(s)  [OK]\n"
"  diffNet: 4 data group(s)  [HAS ERRORS]\n"
"  status   : OK\n"
"\n"
"========================================================================\n")
args = sys.argv
outp = args[args.index("-o")+1] if "-o" in args else "sum.rep"
open(outp, "w").write(out + "\n")
'''
NEG_CORE_DELETED = r'''# core_deleted: emits correct headers/labels/counts but NO real path computation
# (paths replaced with a single placeholder) -- fails i (paths content)
import sys, json, argparse, os
SEP = "=" * 72
def mode_line(label, groups):
    verdict = "HAS ERRORS" if groups else "OK"
    return "  %s: %d data group(s)  [%s]" % (label, groups, verdict)
ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("meta"); ap.add_argument("-o","--output",default="sum.rep")
a = ap.parse_args()
config = json.load(open(a.config)); meta = json.load(open(a.meta))
lines = [SEP, " Connectivity Check Summary", " generated : " + config.get("generated",""), " base dir  : " + os.path.abspath(config.get("base_dir",".")), SEP]
for blk in config["blocks"]:
    nm = blk["name"]; m = meta.get(nm, {})
    lines += ["", "["+nm+"]", "  path(s)      : (placeholder)"]
    lines.append(mode_line("sameNet", m.get("sameNet",0)))
    lines.append(mode_line("diffNet", m.get("diffNet",0)))
    lines.append("  status   : " + m.get("status","OK"))
lines += ["", SEP]
open(a.output, "w").write("\n".join(lines) + "\n")
'''
NEG_STUB_NOSHEILDS = r'''# stub_no_shields: computes paths correctly but OMITS all shields -- fails j/k
import sys, json, argparse, os
SEP = "=" * 72
def normalize(connectivity):
    ne = []
    for e in connectivity:
        if len(e) <= 3: ne.append(list(e)); continue
        s, v, tgt = e[0], e[1], e[2:]
        for t in tgt: ne.append([s, v, t])
    return ne
def find_all(connectivity, start, path=None):
    path = (path if path is not None else []) + [start]
    valid = [e for e in connectivity if e[0] == start]
    if not valid: return [path]
    direct = [(e[0], e[1]) for e in valid if len(e) == 2]
    indirect = [(e[0], e[1], e[2]) for e in valid if len(e) == 3]
    ap = []
    for _, inter, nxt in indirect:
        if inter not in path and nxt not in path:
            np_ = path + [inter]
            if np_ not in ap: ap.extend(find_all(connectivity, nxt, np_))
    for _, nxt in direct:
        if nxt not in path:
            np_ = path
            if np_ not in ap: ap.extend(find_all(connectivity, nxt, np_))
    return ap
def mode_line(label, groups):
    verdict = "HAS ERRORS" if groups else "OK"
    return "  %s: %d data group(s)  [%s]" % (label, groups, verdict)
ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("meta"); ap.add_argument("-o","--output",default="sum.rep")
a = ap.parse_args()
config = json.load(open(a.config)); meta = json.load(open(a.meta))
lines = [SEP, " Connectivity Check Summary", " generated : " + config.get("generated",""), " base dir  : " + os.path.abspath(config.get("base_dir",".")), SEP]
for blk in config["blocks"]:
    nm = blk["name"]; m = meta.get(nm, {})
    ne = normalize(blk["connectivity"])
    paths, seen = [], set()
    for s in blk["bottomLayer"]:
        for p in find_all(ne, s):
            k = tuple(p)
            if k not in seen: seen.add(k); paths.append(" -> ".join(p))
    lines.append(""); lines.append("["+nm+"]")
    lines.append("  path(s)      : " + (paths[0] if paths else "(no path resolved)"))
    for extra in paths[1:]: lines.append("                 " + extra)
    # shields deliberately omitted
    lines.append(mode_line("sameNet", m.get("sameNet",0)))
    lines.append(mode_line("diffNet", m.get("diffNet",0)))
    lines.append("  status   : " + m.get("status","OK"))
lines += ["", SEP]
open(a.output, "w").write("\n".join(lines) + "\n")
'''
NEG_COMMA_JOIN = r'''# stub_comma_join: correct paths/shields content but OLD format: paths comma-joined
# on one line and shields semicolon-joined -- fails h and l
import sys, json, argparse, os
SEP = "=" * 72
def normalize(connectivity):
    ne, sh = [], []
    for e in connectivity:
        if len(e) <= 3: ne.append(list(e)); continue
        s, v, tgt = e[0], e[1], e[2:]
        for t in tgt: ne.append([s, v, t])
        for i in range(len(tgt)):
            for t in tgt[i+1:]: sh.append("%s %s : %s->%s" % (s, v, tgt[i], t))
    return ne, sh
def find_all(connectivity, start, path=None):
    path = (path if path is not None else []) + [start]
    valid = [e for e in connectivity if e[0] == start]
    if not valid: return [path]
    direct = [(e[0], e[1]) for e in valid if len(e) == 2]
    indirect = [(e[0], e[1], e[2]) for e in valid if len(e) == 3]
    ap = []
    for _, inter, nxt in indirect:
        if inter not in path and nxt not in path:
            np_ = path + [inter]
            if np_ not in ap: ap.extend(find_all(connectivity, nxt, np_))
    for _, nxt in direct:
        if nxt not in path:
            np_ = path
            if np_ not in ap: ap.extend(find_all(connectivity, nxt, np_))
    return ap
def mode_line(label, groups):
    verdict = "HAS ERRORS" if groups else "OK"
    return "  %s: %d data group(s)  [%s]" % (label, groups, verdict)
ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("meta"); ap.add_argument("-o","--output",default="sum.rep")
a = ap.parse_args()
config = json.load(open(a.config)); meta = json.load(open(a.meta))
lines = [SEP, " Connectivity Check Summary", " generated : " + config.get("generated",""), " base dir  : " + os.path.abspath(config.get("base_dir",".")), SEP]
for blk in config["blocks"]:
    nm = blk["name"]; m = meta.get(nm, {})
    ne, sh = normalize(blk["connectivity"])
    paths, seen = [], set()
    for s in blk["bottomLayer"]:
        for p in find_all(ne, s):
            k = tuple(p)
            if k not in seen: seen.add(k); paths.append(" -> ".join(p))
    lines.append(""); lines.append("["+nm+"]")
    lines.append("  path(s)      : " + ", ".join(paths))   # OLD comma-join format
    if sh:
        lines.append("  shields       : " + "; ".join(sh))  # OLD semicolon-join
    lines.append(mode_line("sameNet", m.get("sameNet",0)))
    lines.append(mode_line("diffNet", m.get("diffNet",0)))
    lines.append("  status   : " + m.get("status","OK"))
lines += ["", SEP]
open(a.output, "w").write("\n".join(lines) + "\n")
'''

for nm, code in [("empty_shell", NEG_EMPTY), ("print_expected", NEG_PRINT),
                 ("hardcoded_A", NEG_HARDcoded_A), ("core_deleted", NEG_CORE_DELETED),
                 ("stub_no_shields", NEG_STUB_NOSHEILDS), ("stub_comma_join", NEG_COMMA_JOIN)]:
    with open(f"{NEG}/{nm}.py", "w") as f:
        f.write(code)

# rename the candidate file inside each negative to conn_summary.py is NOT needed:
# negative_selftest packs each negative AS conn_summary.py into a zip and runs check.py.

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest: pack each negative as conn_summary.py in submit.zip, run check.py, expect ALL FAIL."""
import os, sys, json, zipfile, subprocess, tempfile, shutil
PY = sys.executable
REF = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(REF, "check.py")
NEG = REF
cases = ["empty_shell", "print_expected", "hardcoded_A", "core_deleted", "stub_no_shields", "stub_comma_join"]
results = {}
for c in cases:
    tmp = tempfile.mkdtemp(prefix="neg_")
    try:
        z = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(z, "w") as zf:
            zf.write(os.path.join(NEG, c + ".py"), "conn_summary.py")
        r = subprocess.run([PY, CHECK, z, tmp], capture_output=True, text=True, timeout=120)
        # expect non-zero exit (check raises AssertionError on any failure)
        results[c] = (r.returncode != 0, r.stdout[-400:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
allok = True
for c, (failed, detail) in results.items():
    status = "FAIL-as-expected" if failed else "PASS-BAD(should have failed)"
    if not failed: allok = False
    print("  %-18s %s" % (c, status))
if not allok:
    print("NEG_SELFTEST: some negative passed check (BUG)")
    sys.exit(1)
print("NEG_SELFTEST: all %d negatives correctly FAIL check.py" % len(cases))
'''
with open(f"{NEG}/negative_selftest.py", "w") as f:
    f.write(NEG_SELFTEST)

# ---------- reference_submit.zip ----------
rs = f"{REF}/reference_submit.zip"
with zipfile.ZipFile(rs, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(f"{REF}/golden_solution.py", "conn_summary.py")

# ---------- self-verify ----------
print("\n=== SELF-VERIFY ===")
# 1. golden check PASS
r = subprocess.run([sys.executable, f"{REF}/check.py", rs, REF], capture_output=True, text=True)
print("golden check rc=%d" % r.returncode)
print(r.stdout)
if r.returncode != 0:
    print("STDERR:", r.stderr); sys.exit(1)

# 2. negatives ALL FAIL
r = subprocess.run([sys.executable, f"{NEG}/negative_selftest.py"], capture_output=True, text=True)
print("negatives rc=%d" % r.returncode)
print(r.stdout)
if r.returncode != 0:
    print("STDERR:", r.stderr); sys.exit(1)

# 3. three fake submissions (empty/print-expected/core-deleted) -> already in negatives; verify individually via check
print("\n=== 4.9 three-fake check ===")
for c in ["empty_shell", "print_expected", "core_deleted"]:
    tmp = tempfile.mkdtemp(prefix="fake_")
    z = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(f"{NEG}/{c}.py", "conn_summary.py")
    r = subprocess.run([sys.executable, f"{REF}/check.py", z, tmp], capture_output=True, text=True)
    print("  %-16s rc=%d (expect !=0)" % (c, r.returncode))
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode == 0:
        print("  BAD: fake %s passed!" % c); sys.exit(1)

# 4. 3-seed sha256 stability on B output
print("\n=== 3-seed sha256 stability ===")
import hashlib
hashes = set()
for seed in range(3):
    tmp = tempfile.mkdtemp(prefix="seed_")
    cp = os.path.join(tmp, "config.json"); wj(cp, CONFIG_B)
    mp = os.path.join(tmp, "meta.json"); wj(mp, META_B)
    op = os.path.join(tmp, "sum.rep")
    r = subprocess.run([sys.executable, f"{REF}/golden_solution.py", cp, mp, "-o", op], capture_output=True, text=True)
    h = hashlib.sha256(open(op, "rb").read()).hexdigest()
    hashes.add(h)
    shutil.rmtree(tmp, ignore_errors=True)
print("distinct sha256 over 3 seeds: %d (expect 1)" % len(hashes))
if len(hashes) != 1:
    print("BAD: non-deterministic output"); sys.exit(1)

# 5. assertion gate: k_rationale == k_check >= 8
# count labels in check.py
check_src = open(f"{REF}/check.py").read()
labels = re.findall(r'cond\("([a-z])"', check_src)
k_check = len(labels)
print("\n=== assertion gate ===")
print("k_check (labels in check.py) = %d" % k_check)
print("labels:", labels)
print("GATE: k_check >= 8:", k_check >= 8)

print("\n=== ALL SELF-VERIFY PASSED ===")
