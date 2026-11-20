#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001 (shard C, physical_verify).
B-档 synthesized L1-boundary: AutoCell external DRC/LVS engine config (kit TCL variant generator).
Trace: 8ky45 (e0047434 @ hfeg0pnd002, mc=211).
"""
import os, json, zipfile, shutil, subprocess, sys, tempfile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001"
A    = os.path.join(ROOT, "assets", CID)
REF  = os.path.join(ROOT, "reference", CID)
HID  = os.path.join(A, "hidden")
NEG  = os.path.join(REF, "negative")
for d in (A, REF, HID, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- original kit TCL (A, faithful to real R_H204_000.tcl) ----------
KIT_A = """# AutoCell Layout Generator TCL, Version 1.26.7.56db6cb

source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl

option router 1
option router_method 2
option router_solver_optimize_mode 0

option lvs_check 1
option lvs_dont_compare_bulk 1

set_constraint PVS 0
set_constraint PVBS 0
set_constraint FPVB 0
set_constraint TTS 1
set_constraint VVA 1

schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}

cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin

cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device

cell ${cell_name} generate_layout

write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
"""

# hidden B kit TCLs (different content, same structure)
KIT_B1 = """# AutoCell Layout Generator TCL, Version 1.26.7.56db6cb

source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl

option router 2
option router_method 1
option router_solver_optimize_mode 1

option lvs_check 1
option lvs_dont_compare_bulk 0

set_constraint PVS 1
set_constraint PVBS 0
set_constraint FPVB 1
set_constraint TTS 0
set_constraint VVA 1

schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}

cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin

cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device

cell ${cell_name} generate_layout

write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
"""

KIT_B2 = """# AutoCell Layout Generator TCL, Version 1.26.9.91feba6

source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl

option router 1
option router_method 2
option router_solver_optimize_mode 0

option lvs_check 0
option lvs_dont_compare_bulk 1

set_constraint PVS 0
set_constraint PVBS 1
set_constraint FPVB 0
set_constraint TTS 1
set_constraint VVA 0

schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}

cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin

cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device

cell ${cell_name} generate_layout

write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
"""

KIT_B3 = """# AutoCell Layout Generator TCL, Version 1.26.9.91feba6

source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl

option router 2
option router_method 1
option router_solver_optimize_mode 1

option lvs_check 1
option lvs_dont_compare_bulk 1

set_constraint PVS 1
set_constraint PVBS 1
set_constraint FPVB 0
set_constraint TTS 1
set_constraint VVA 1

schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}

cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin

cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device

cell ${cell_name} generate_layout

write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
"""

# ---------- manifest schema ----------
# A: power_side=fs, flow=gds (faithful to trace: front-side, AutoCell GDS flow)
# B1: power_side=dbc, flow=gds (back-side, AutoCell GDS) -> tv1_dbc, *_DBC.rule
# B2: power_side=fs, flow=oa  (front-side, Virtuoso OA)  -> tv1_fs_virtuoso, *_FS.rule
# B3: power_side=dbc, flow=oa (back-side, Virtuoso OA)   -> tv1_dbc_virtuoso, *_DBC.rule
def manifest(kit_file, out_name, power_side, flow, tech="default_tech", timeout=600):
    return {
        "kit_file": kit_file,
        "output_name": out_name,
        "tech_name": tech,
        "engine_bin": "calibre",
        "power_side": power_side,            # "fs" | "dbc"
        "flow": flow,                         # "gds" (AutoCell, non-virtuoso) | "oa" (Virtuoso, _virtuoso)
        "runset_root": "/apps/imctf/cad/runset/lacaa",
        "pdk_tag": "tv1",
        "timeout_sec": timeout,
        "insertion_anchor_substring": "prepr.tcl",
        "no_comments": True,
        "preserve_original_code": True,
        "remove_header_comment": True,
    }

MAN_A  = manifest("R_H204_000.tcl", "R_H204_000_rule.tcl", "fs", "gds")
MAN_B1 = manifest("R_H204_001.tcl", "R_H204_001_rule.tcl", "dbc", "gds")
MAN_B2 = manifest("R_H204_002.tcl", "R_H204_002_rule.tcl", "fs",  "oa")
MAN_B3 = manifest("R_H204_003.tcl", "R_H204_003_rule.tcl", "dbc", "oa")

# ---------- spec doc (the "docs" the SUT reads) ----------
SPEC = """# AutoCell External DRC/LVS Engine Configuration Spec

## Command: `tech <name> set_external_engine [options]`

Configures the external physical-verification engines (DRC + LVS) that AutoCell's
`run_drc` / `run_lvs` will invoke. Settings are stored on the technology so subsequent
verification runs use them by default.

### Options used in this task
- `-bin {binary_path}`        : external tool binary (default `calibre`).
- `-drc_deck {file_path}`     : DRC rule deck file path.
- `-lvs_deck {file_path}`     : LVS rule deck file path.
- `-timeout {seconds}`        : runner timeout in seconds (default 60).

Full form (one logical command, backslash line-continuation):
```
tech <tech_name> set_external_engine \\
    -bin calibre \\
    -drc_deck <drc_deck_path> \\
    -lvs_deck <lvs_deck_path> \\
    -timeout <seconds>
```

## PDK runset path conventions (tv1 = ALS PDK, process `lacaa`)

The foundry ships four runset directories under `/apps/imctf/cad/runset/lacaa`:

| directory | power side | flow variant |
|---|---|---|
| `tv1_fs`            | front-side (fs)  | AutoCell GDS flow (non-virtuoso) |
| `tv1_dbc`           | back-side (dbc)  | AutoCell GDS flow (non-virtuoso) |
| `tv1_fs_virtuoso`   | front-side (fs)  | Virtuoso OA flow (virtuoso)      |
| `tv1_dbc_virtuoso`  | back-side (dbc)  | Virtuoso OA flow (virtuoso)      |

Each runset directory `<tag>/current/` contains calibre decks named:
- `calibre_DRC_<SIDE>.rule`  where `<SIDE>` = `FS` (front-side) or `DBC` (back-side)
- `calibre_LVS_<SIDE>.rule`

### Deck-path derivation rule
Given a manifest with `runset_root`, `pdk_tag`, `power_side` (`fs`|`dbc`), `flow` (`gds`|`oa`):
1. `SIDE` = uppercase(power_side)  -> `FS` or `DBC`
2. `flow_suffix` = `_virtuoso` if `flow == "oa"` else `""`
3. `side_dir` = `{runset_root}/{pdk_tag}_{power_side}{flow_suffix}/current`
4. `drc_deck` = `{side_dir}/calibre_DRC_{SIDE}.rule`
5. `lvs_deck` = `{side_dir}/calibre_LVS_{SIDE}.rule`

AutoCell's own `write_layout -type gds` emits GDS, so the **AutoCell flow** uses the
**non-virtuoso** runset (`flow == "gds"`). The `_virtuoso` variants are for Virtuoso OA
integration only.

## Kit TCL variant generation requirements

A "kit" TCL (e.g. `R_H204_000.tcl`) drives AutoCell layout generation. To attach an
external verification engine **without modifying the original kit**, generate a kit
**variant** `<kit_base>_rule.tcl` that:

1. **Preserves the original kit's non-comment code lines verbatim**, in their original
   relative order (zero alteration, none missing).
2. **Removes every comment line** (any line whose stripped form begins with `#`).
   Blank lines may be kept or dropped, but no `#` comment may remain.
3. **Inserts one** `tech <tech_name> set_external_engine ...` **block** (the 5-line form
   above) **immediately AFTER the line containing the insertion anchor** substring
   (default anchor: `prepr.tcl`) and before the following original code line.
4. The block must use `-bin <engine_bin>`, `-drc_deck <drc_deck>`, `-lvs_deck <lvs_deck>`,
   `-timeout <timeout_sec>` exactly as derived from the manifest.
5. The block must target the manifest's `tech_name`.
6. The output file name must equal the manifest's `output_name`.

The deliverable is a **generator script** `gen_rule_kit.py` that reads a manifest JSON
and a kit TCL file and writes the variant TCL; it must work on ANY manifest/kit pair
following this spec (the grader runs it on hidden manifests with different
power_side / flow / tech combinations).
"""

# ---------- prompt (natural language, real scenario) ----------
PROMPT = """你是 EDA 版图工程师，在用 Empyrean AutoCell 标准单元编译器（Standard Cell Compiler）为一个
N5 工艺库（autocell_n5_release_20260910/autocell_library）生成标准单元版图。AutoCell 跑完后要
用 calibre 做物理验证（DRC + LVS），需要把外部验证引擎的 rule deck 配置挂到 technology 上。

客户（fab）刚把 ALS PDK 的 calibre rule deck 路径发过来，在 /apps/imctf/cad/runset/lacaa 下分了
4 个目录：tv1_fs（正面供电）、tv1_dbc（背面供电）、tv1_fs_virtuoso、tv1_dbc_virtuoso（后两个是
Virtuoso OA flow 用的变体）。AutoCell 自己 write_layout 出的是 GDS，所以该走非 virtuoso 的那一份；
用户当前这一支是正面供电（front-side）。

你想把这套外部 DRC/LVS 引擎配置加到一个 kit TCL（如 R_H204_000.tcl）里，但不想直接改原 kit 文件
（要保持原 kit 可复用、可回退），也不想用 AutoCell GUI 的 "Rule File Settings - Technology" 对话框
（那个 GUI 不收 .rule 扩展名，只认 .drc/.lvs；文档里正式的配置入口是 TCL 命令
`tech <name> set_external_engine`）。于是决定：另起一个 kit 变体 R_H204_000_rule.tcl，在原 kit 代码
逐行保留的基础上，插一段 `tech default_tech set_external_engine -bin calibre -drc_deck ... -lvs_deck ...
-timeout 600`，并去掉所有注释行。

请交付一个**纯 Python（仅标准库）的生成器** `gen_rule_kit.py`：它读一份 manifest JSON（说明
power_side / flow / runset_root / pdk_tag / tech_name / engine_bin / timeout / 插入锚点 / kit 文件名 /
输出文件名 等参数）和一份 kit TCL 文件，按上面的约定生成对应的 `<kit_base>_rule.tcl` 变体，写到
指定输出目录。生成器必须是通用的——判分时会换不同的 manifest（不同的 power_side、flow、tech_name、
timeout 组合）和不同的 kit TCL 来跑，不能硬编码 tv1_fs / GDS 这些当前值。

manifest 字段与 deck 路径推导规则、set_external_engine 命令语法、kit 变体的逐条要求，见随附
`autocell_engine_cfg_spec.md`。当前这一份示例 manifest（`autocell_engine_cfg_manifest.json`，正面供电
+ GDS flow）和示例 kit（`R_H204_000.tcl`）只用来让你理解和自测，不是判分输入。

交付：把 `gen_rule_kit.py` 单文件打进 `outputs/submit.zip`。生成器 CLI 约定：
`python3 gen_rule_kit.py <manifest.json> <kit.tcl> <output_dir>`，在 output_dir 下写出 manifest
output_name 指定的 tcl 文件，退出码 0 表示成功。
"""

TASK_BRIEF = """交付：outputs/submit.zip 内含 gen_rule_kit.py（纯标准库）。
接口：python3 gen_rule_kit.py <manifest.json> <kit.tcl> <output_dir>，按 manifest 生成 <output_name> 指定的 kit 变体 TCL。
判分：换 hidden manifest（不同 power_side/flow/tech/timeout）+ hidden kit 跑生成器，按 autocell_engine_cfg_spec.md 逐条校验产物。
"""

# ---------- reference generator (gen_rule_kit.py) ----------
GEN_REF = r'''#!/usr/bin/env python3
"""Reference generator: AutoCell kit TCL variant with external DRC/LVS engine config.
Usage: python3 gen_rule_kit.py <manifest.json> <kit.tcl> <output_dir>
"""
import sys, os, json

def derive_decks(m):
    side = m["power_side"].upper()                      # FS | DBC
    flow_suffix = "_virtuoso" if m.get("flow") == "oa" else ""
    side_dir = "{root}/{tag}_{ps}{fsuf}/current".format(
        root=m["runset_root"], tag=m["pdk_tag"],
        ps=m["power_side"], fsuf=flow_suffix)
    drc = "{sd}/calibre_DRC_{s}.rule".format(sd=side_dir, s=side)
    lvs = "{sd}/calibre_LVS_{s}.rule".format(sd=side_dir, s=side)
    return drc, lvs

def build_variant(kit_text, m):
    drc, lvs = derive_decks(m)
    anchor = m.get("insertion_anchor_substring", "prepr.tcl")
    tech = m["tech_name"]
    bin_ = m.get("engine_bin", "calibre")
    timeout = m.get("timeout_sec", 600)
    block = [
        "tech {t} set_external_engine \\".format(t=tech),
        "    -bin {b} \\".format(b=bin_),
        "    -drc_deck {d} \\".format(d=drc),
        "    -lvs_deck {l} \\".format(l=lvs),
        "    -timeout {to}".format(to=timeout),
    ]
    out = []
    inserted = False
    for raw in kit_text.splitlines():
        s = raw.strip()
        # drop comment lines
        if s.startswith("#"):
            continue
        out.append(raw.rstrip())
        # insert engine block right after the anchor line (only code lines considered;
        # anchor line itself is a code line 'source .../prepr.tcl', not a comment)
        if (not inserted) and (anchor in raw):
            out.extend(block)
            inserted = True
    # if anchor never found, append block at end
    if not inserted:
        out.extend(block)
    return "\n".join(out) + "\n"

def main():
    if len(sys.argv) != 4:
        sys.stderr.write("usage: gen_rule_kit.py <manifest.json> <kit.tcl> <output_dir>\n")
        return 2
    mpath, kpath, odir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mpath, encoding="utf-8") as f:
        m = json.load(f)
    with open(kpath, encoding="utf-8") as f:
        kit = f.read()
    out_text = build_variant(kit, m)
    os.makedirs(odir, exist_ok=True)
    oname = m["output_name"]
    with open(os.path.join(odir, oname), "w", encoding="utf-8") as f:
        f.write(out_text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

# ---------- negatives (must all FAIL check.py) ----------
NEG_NAIVE = r'''#!/usr/bin/env python3
"""Naive negative: just copies the kit TCL verbatim (no set_external_engine block)."""
import sys, os, json, shutil
def main():
    mpath, kpath, odir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mpath, encoding="utf-8") as f: m = json.load(f)
    os.makedirs(odir, exist_ok=True)
    shutil.copyfile(kpath, os.path.join(odir, m["output_name"]))
    return 0
if __name__ == "__main__": sys.exit(main())
'''

NEG_HARDCODE = r'''#!/usr/bin/env python3
"""Hardcoded negative: always emits tv1_fs / GDS (front-side, non-virtuoso) regardless of manifest."""
import sys, os, json
def main():
    mpath, kpath, odir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mpath, encoding="utf-8") as f: m = json.load(f)
    with open(kpath, encoding="utf-8") as f: kit = f.read()
    drc = "/apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_DRC_FS.rule"
    lvs = "/apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_LVS_FS.rule"
    block = [
        "tech default_tech set_external_engine \\",
        "    -bin calibre \\",
        "    -drc_deck %s \\" % drc,
        "    -lvs_deck %s \\" % lvs,
        "    -timeout 600",
    ]
    out = []
    ins = False
    for raw in kit.splitlines():
        s = raw.strip()
        if s.startswith("#"): continue
        out.append(raw.rstrip())
        if (not ins) and "prepr.tcl" in raw:
            out.extend(block); ins = True
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, m["output_name"]), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return 0
if __name__ == "__main__": sys.exit(main())
'''

NEG_COMMENTS = r'''#!/usr/bin/env python3
"""Keep-comments negative: correct engine block but keeps all original comment lines."""
import sys, os, json
def main():
    mpath, kpath, odir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mpath, encoding="utf-8") as f: m = json.load(f)
    with open(kpath, encoding="utf-8") as f: kit = f.read()
    side = m["power_side"].upper()
    fsuf = "_virtuoso" if m.get("flow") == "oa" else ""
    sd = "{root}/{tag}_{ps}{fsuf}/current".format(root=m["runset_root"], tag=m["pdk_tag"], ps=m["power_side"], fsuf=fsuf)
    drc = "{sd}/calibre_DRC_{s}.rule".format(sd=sd, s=side)
    lvs = "{sd}/calibre_LVS_{s}.rule".format(sd=sd, s=side)
    block = [
        "tech {t} set_external_engine \\".format(t=m["tech_name"]),
        "    -bin {b} \\".format(b=m.get("engine_bin","calibre")),
        "    -drc_deck {d} \\".format(d=drc),
        "    -lvs_deck {l} \\".format(l=lvs),
        "    -timeout {to}".format(to=m.get("timeout_sec",600)),
    ]
    out = []
    ins = False
    for raw in kit.splitlines():           # keeps comment lines
        out.append(raw.rstrip())
        if (not ins) and "prepr.tcl" in raw:
            out.extend(block); ins = True
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, m["output_name"]), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return 0
if __name__ == "__main__": sys.exit(main())
'''

# ---------- check.py ----------
CHECK = r'''#!/usr/bin/env python3
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001.
Runs the submitted gen_rule_kit.py on 3 hidden manifests/kits and validates each
output kit-variant TCL against 14 conditions (a-n). 真跑候选: (j) subprocess tclsh
`info complete` syntax check.
"""
import os, sys, json, zipfile, subprocess, tempfile, shutil

HIDDEN = {
    "B1": ("manifest_B1.json", "kit_B1.tcl"),
    "B2": ("manifest_B2.json", "kit_B2.tcl"),
    "B3": ("manifest_B3.json", "kit_B3.tcl"),
}

def _fail(msg):
    raise AssertionError(msg)

def _code_lines(text):
    """non-comment, non-blank stripped lines (preserve order)."""
    out = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s: continue
        if s.startswith("#"): continue
        out.append(s)
    return out

def _derive_expected(m):
    side = m["power_side"].upper()
    fsuf = "_virtuoso" if m.get("flow") == "oa" else ""
    sd = "{root}/{tag}_{ps}{fsuf}/current".format(
        root=m["runset_root"], tag=m["pdk_tag"], ps=m["power_side"], fsuf=fsuf)
    drc = "{sd}/calibre_DRC_{s}.rule".format(sd=sd, s=side)
    lvs = "{sd}/calibre_LVS_{s}.rule".format(sd=sd, s=side)
    return drc, lvs, side, fsuf

def _tclsh_complete(text):
    """真跑候选: use tclsh `info complete` to validate TCL syntax via subprocess."""
    probe = (
        'set f [open "%s" r]; set c [read $f]; close $f; '
        'if {![info complete $c]} {puts INCOMPLETE; exit 1}; puts OK; exit 0\n'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False, encoding="utf-8") as tf:
        tf.write(text); tcl_path = tf.name
    probe_script = probe % tcl_path
    try:
        proc = subprocess.run(["tclsh"], input=probe_script,
                              capture_output=True, text=True, timeout=15)
        ok = (proc.returncode == 0) and ("OK" in proc.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # tclsh unavailable: fall back to brace/bracket/quote balance check
        depth = 0; br = 0; ok = True
        for ch in text:
            if ch == "{": depth += 1
            elif ch == "}": depth -= 1
            elif ch == "[": br += 1
            elif ch == "]": br -= 1
            if depth < 0 or br < 0: ok = False; break
        if depth != 0 or br != 0: ok = False
    finally:
        try: os.unlink(tcl_path)
        except OSError: pass
    return ok

def _run_gen(gen_py, manifest_path, kit_path, out_dir):
    proc = subprocess.run([sys.executable, gen_py, manifest_path, kit_path, out_dir],
                          capture_output=True, text=True, timeout=30)
    return proc

def check(deliverable, workdir):
    # 1. unzip deliverable into a temp dir
    tmp = tempfile.mkdtemp(prefix="autocell_extchk_")
    try:
        if not os.path.exists(deliverable):
            _fail("deliverable not found: %s" % deliverable)
        with zipfile.ZipFile(deliverable) as zf:
            zf.extractall(tmp)
        gen = os.path.join(tmp, "gen_rule_kit.py")
        # (a) gen_rule_kit.py exists + py_compile
        if not os.path.isfile(gen):
            _fail("a) submit.zip missing gen_rule_kit.py")
        try:
            subprocess.run([sys.executable, "-m", "py_compile", gen],
                           capture_output=True, timeout=30, check=True)
        except Exception:
            _fail("a) gen_rule_kit.py py_compile failed")

        # hidden assets live under workdir/hidden/ (copied by harness) — fallback to
        # the case's assets/hidden/ via known layout
        hidden_dir = os.path.join(workdir, "hidden")
        if not os.path.isdir(hidden_dir):
            # try relative to this check.py
            hidden_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hidden")
        if not os.path.isdir(hidden_dir):
            # reference/<CID>/check.py -> ../assets/<CID>/hidden (reference/ and assets/ are siblings)
            hidden_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "assets",
                                      "EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001", "hidden")
        if not os.path.isdir(hidden_dir):
            _fail("hidden dir not located")

        for tag, (mf, kf) in HIDDEN.items():
            mpath = os.path.join(hidden_dir, mf)
            kpath = os.path.join(hidden_dir, kf)
            if not (os.path.isfile(mpath) and os.path.isfile(kpath)):
                _fail("hidden %s/%s missing" % (mf, kf))
            with open(mpath, encoding="utf-8") as f: m = json.load(f)
            with open(kpath, encoding="utf-8") as f: kit_text = f.read()
            out_dir = tempfile.mkdtemp(prefix="genout_%s_" % tag)
            try:
                proc = _run_gen(gen, mpath, kpath, out_dir)
                # (b) exit 0 + output file exists with correct name
                if proc.returncode != 0:
                    _fail("b) [%s] generator exit=%d stderr=%s" % (tag, proc.returncode, proc.stderr[:200]))
                oname = m["output_name"]
                out_path = os.path.join(out_dir, oname)
                if not os.path.isfile(out_path):
                    _fail("b) [%s] output %s not produced" % (tag, oname))
                with open(out_path, encoding="utf-8") as f: out_text = f.read()

                # (c) no comment lines
                for raw in out_text.splitlines():
                    if raw.strip().startswith("#"):
                        _fail("c) [%s] comment line remains: %s" % (tag, raw.strip()[:60]))

                # (d) original non-comment code lines preserved verbatim
                orig_code = _code_lines(kit_text)
                out_code = _code_lines(out_text)
                # the only added lines should be the set_external_engine block (5 lines)
                added = [s for s in out_code if s not in orig_code]
                missing = [s for s in orig_code if s not in out_code]
                if missing:
                    _fail("d) [%s] original code lines missing: %s" % (tag, missing[:3]))

                # (e) contains set_external_engine call
                if "set_external_engine" not in out_text:
                    _fail("e) [%s] no set_external_engine call" % tag)

                # (f) -bin calibre
                if "-bin calibre" not in out_text:
                    _fail("f) [%s] missing '-bin calibre'" % tag)

                drc_exp, lvs_exp, side, fsuf = _derive_expected(m)

                # (g) -drc_deck path correct
                if drc_exp not in out_text:
                    _fail("g) [%s] drc_deck mismatch: expected %s" % (tag, drc_exp))
                # (h) -lvs_deck path correct
                if lvs_exp not in out_text:
                    _fail("h) [%s] lvs_deck mismatch: expected %s" % (tag, lvs_exp))

                # (i) set_external_engine block inserted after prepr.tcl anchor
                idx_anchor = -1; idx_engine = -1
                for i, s in enumerate(out_code):
                    if "prepr.tcl" in s and idx_anchor < 0: idx_anchor = i
                    if "set_external_engine" in s: idx_engine = i
                if idx_anchor < 0 or idx_engine < 0:
                    _fail("i) [%s] anchor or engine block not found" % tag)
                if idx_engine != idx_anchor + 1:
                    _fail("i) [%s] engine block not right after prepr.tcl (anchor=%d engine=%d)" % (tag, idx_anchor, idx_engine))

                # (j) 真跑候选: tclsh info complete
                if not _tclsh_complete(out_text):
                    _fail("j) [%s] tclsh info complete check failed" % tag)

                # (k) targets manifest tech_name
                tech = m["tech_name"]
                if ("tech %s set_external_engine" % tech) not in out_text:
                    _fail("k) [%s] tech name mismatch: expected 'tech %s ...'" % (tag, tech))

                # (l) deck path variant correct (virtuoso suffix per flow)
                if m.get("flow") == "oa":
                    if "_virtuoso" not in drc_exp or "_virtuoso" not in out_text:
                        _fail("l) [%s] flow=oa but no _virtuoso in deck path" % tag)
                else:
                    if "_virtuoso" in out_text:
                        _fail("l) [%s] flow=gds but deck path has _virtuoso" % tag)

                # (m) -timeout with manifest value
                tval = str(m.get("timeout_sec", 600))
                if ("-timeout %s" % tval) not in out_text:
                    _fail("m) [%s] -timeout %s not found" % (tag, tval))

                # (n) original header comment line absent
                for raw in kit_text.splitlines():
                    s = raw.strip()
                    if s.startswith("# AutoCell Layout Generator TCL"):
                        if s in out_text:
                            _fail("n) [%s] original header comment still present: %s" % (tag, s))
                        break
            finally:
                shutil.rmtree(out_dir, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True

if __name__ == "__main__":
    # standalone: check.py <submit.zip> <workdir_with_hidden>
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else "."
    try:
        check(d, w)
        print("PASS")
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest: every negative must FAIL check.py. All-negative must FAIL => PASS here."""
import os, sys, zipfile, tempfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
CHECK = os.path.join(HERE, "check.py")
HIDDEN = os.path.join(HERE, "hidden")
if not os.path.isdir(HIDDEN):
    HIDDEN = os.path.join(HERE, "..", "assets",
                          "EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001", "hidden")

def make_zip(py_path):
    tmp = tempfile.mkdtemp()
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as zf:
        zf.write(py_path, "gen_rule_kit.py")
    return zp, tmp

negatives = [f for f in os.listdir(NEG) if f.endswith(".py")]
if not negatives:
    print("no negatives found"); sys.exit(1)
all_failed = True
for neg in sorted(negatives):
    zp, tmp = make_zip(os.path.join(NEG, neg))
    try:
        r = subprocess.run([sys.executable, CHECK, zp, os.path.dirname(HIDDEN) or "."],
                           capture_output=True, text=True, timeout=120)
        ok = (r.returncode == 0)
        status = "PASS(should be FAIL!)" if ok else "FAIL(expected)"
        print("%s: %s" % (neg, status))
        if ok: all_failed = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
if all_failed:
    print("NEGSELFTEST PASS: all negatives failed as expected")
    sys.exit(0)
else:
    print("NEGSELFTEST FAIL: some negative passed check (should not)")
    sys.exit(1)
'''

# ===================== write files =====================
with open(os.path.join(A, "R_H204_000.tcl"), "w", encoding="utf-8") as f: f.write(KIT_A)
with open(os.path.join(A, "autocell_engine_cfg_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(MAN_A, f, indent=2, ensure_ascii=False)
with open(os.path.join(A, "autocell_engine_cfg_spec.md"), "w", encoding="utf-8") as f: f.write(SPEC)
with open(os.path.join(A, "prompt.txt"), "w", encoding="utf-8") as f: f.write(PROMPT)
with open(os.path.join(A, "task_brief.md"), "w", encoding="utf-8") as f: f.write(TASK_BRIEF)

# hidden
with open(os.path.join(HID, "kit_B1.tcl"), "w", encoding="utf-8") as f: f.write(KIT_B1)
with open(os.path.join(HID, "kit_B2.tcl"), "w", encoding="utf-8") as f: f.write(KIT_B2)
with open(os.path.join(HID, "kit_B3.tcl"), "w", encoding="utf-8") as f: f.write(KIT_B3)
with open(os.path.join(HID, "manifest_B1.json"), "w", encoding="utf-8") as f:
    json.dump(MAN_B1, f, indent=2, ensure_ascii=False)
with open(os.path.join(HID, "manifest_B2.json"), "w", encoding="utf-8") as f:
    json.dump(MAN_B2, f, indent=2, ensure_ascii=False)
with open(os.path.join(HID, "manifest_B3.json"), "w", encoding="utf-8") as f:
    json.dump(MAN_B3, f, indent=2, ensure_ascii=False)
with open(os.path.join(HID, "hidden_manifest.json"), "w", encoding="utf-8") as f:
    json.dump({"variants": ["B1", "B2", "B3"],
               "note": "check.py runs gen_rule_kit.py on each variant; deck side/flow differs"}, f, indent=2)

# reference
with open(os.path.join(REF, "gen_rule_kit.py"), "w", encoding="utf-8") as f: f.write(GEN_REF)
with open(os.path.join(REF, "check.py"), "w", encoding="utf-8") as f: f.write(CHECK)
with open(os.path.join(NEG, "naive_copy.py"), "w", encoding="utf-8") as f: f.write(NEG_NAIVE)
with open(os.path.join(NEG, "hardcoded_fs.py"), "w", encoding="utf-8") as f: f.write(NEG_HARDCODE)
with open(os.path.join(NEG, "keep_comments.py"), "w", encoding="utf-8") as f: f.write(NEG_COMMENTS)
with open(os.path.join(REF, "negative_selftest.py"), "w", encoding="utf-8") as f: f.write(NEG_SELFTEST)

os.chmod(os.path.join(REF, "gen_rule_kit.py"), 0o755)
os.chmod(os.path.join(REF, "check.py"), 0o755)
for n in os.listdir(NEG):
    os.chmod(os.path.join(NEG, n), 0o755)
os.chmod(os.path.join(REF, "negative_selftest.py"), 0o755)

print("built case files under:", A, "and", REF)
