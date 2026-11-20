#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001 (shard D, schematic_netlist).

A-faithful seed: cr42l (johnl@hfeg0pkn001, mc=43). USER#0 verbatim:
  "/home/johnl/.cline/scripts/data/primelib/primelib_char_all_comb  帮我看下这里的k库流程是怎样的"

A assets = real primelib_char_all_comb project (fetched from .75).
Hidden B  = synthesized iolib_io project (different library/corner/cells/config, same 5-step flow).
Ref       = analyze_flow.py (general parser, reads any such project -> structured JSON).
check.py  = 16 conditions (a-p), runs ref on hidden B, verifies JSON structure+values.
"""
import json, os, sys, hashlib, zipfile, io, shutil, subprocess, tempfile
from pathlib import Path

BENCH = Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
CASE = "EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001"
AST = BENCH / "assets" / CASE
REF = BENCH / "reference" / CASE

# ---------- Hidden B project (iolib_io) ----------
B_CELLS = [
    "iobufLx1", "iobufLx2", "iobufLx4", "iobufLx8",
    "iobufLVx1", "iobufLVx2", "iotriLx1", "iotriLx2",
    "pdLx1", "pdLx2", "puLx1", "puLx2",
    "esdLx1", "esdLx2", "esdLx4",
]

B_PROJECT_JSON = json.dumps({
    "library": "iolib_io",
    "source_netlist": "../netlist.io.sp",
    "corner": "TT_1p1_25c",
    "process_section": "TT",
    "model": {
        "main_file": "/apps/imctf/models/V3A/model_local/V3A_IO_Model_v0d2/V3A_IO_Model_v0d2.sp",
        "include_file": "/apps/imctf/models/V3A/model_local/V3A_IO_Model_v0d2/incFile_V3A_IO",
        "include_sections": ["bjt_tt", "res_tt", "nicap_tt", "diode_tt"],
        "nmos_names": ["ion", "ion_lv", "ion_lv_pc60"],
        "pmos_names": ["iop", "iop_lv", "iop_lv_pc60"],
    },
    "voltage": {"vcc": 1.1, "vss": 0.0, "vbn": 0.0, "vbp": 1.1},
    "temperature_c": 25.0,
    "grid": {
        "rise_slew_ns": [0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30, 0.50, 0.80, 1.20],
        "fall_slew_ns": [0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30, 0.50, 0.80, 1.20],
        "load_pf": [0.001, 0.005, 0.010, 0.020, 0.040, 0.080, 0.120, 0.200, 0.350, 0.500],
    },
    "threshold_pct": {"input": 50.0, "output": 50.0, "slew_lower": 20.0, "slew_upper": 80.0},
    "spice": {
        "parameter_lines": ["Ithin=0.5f Ithick=0.3f IapO=0.5f Igatein=0.5f"],
        "external_x_targets": ["riodiff_3t_ckt"],
    },
}, indent=2)

B_PROJECT_JSON_ALT = json.dumps({
    "library": "iolib_io",
    "source_netlist": "../netlist.io.sp",
    "corner": "FF_1p2_m40c",
    "process_section": "FF",
    "model": {
        "main_file": "/apps/imctf/models/V3A/model_local/V3A_IO_Model_v0d2/V3A_IO_Model_v0d2.sp",
        "include_file": "/apps/imctf/models/V3A/model_local/V3A_IO_Model_v0d2/incFile_V3A_IO",
        "include_sections": ["bjt_ff", "res_ff", "nicap_ff", "diode_ff"],
        "nmos_names": ["ion", "ion_lv", "ion_lv_pc60"],
        "pmos_names": ["iop", "iop_lv", "iop_lv_pc60"],
    },
    "voltage": {"vcc": 1.2, "vss": 0.0, "vbn": 0.0, "vbp": 1.2},
    "temperature_c": -40.0,
    "grid": {
        "rise_slew_ns": [0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30, 0.50, 0.80, 1.20],
        "fall_slew_ns": [0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30, 0.50, 0.80, 1.20],
        "load_pf": [0.001, 0.005, 0.010, 0.020, 0.040, 0.080, 0.120, 0.200, 0.350, 0.500],
    },
    "threshold_pct": {"input": 50.0, "output": 50.0, "slew_lower": 20.0, "slew_upper": 80.0},
    "spice": {
        "parameter_lines": ["Ithin=0.5f Ithick=0.3f IapO=0.5f Igatein=0.5f"],
        "external_x_targets": ["riodiff_3t_ckt"],
    },
}, indent=2)

B_CELLS_TXT = "\n".join(B_CELLS) + "\n"

B_README = """# iolib_io IO-combo PrimeLib project

This project characterizes IO-buffer combinational cells with PrimeLib.

## Input

Source netlist configured in the selected corner JSON's `source_netlist`:

```json
"source_netlist": "../netlist.io.sp"
```

## Step 1: inventory and closure

```sh
./scripts/run_prepare.sh
```

Generates config/cells.txt, reports/io_comb_pins.tsv,
netlists/iolib_io_all_comb_closure.sp, work/char_config.tcl,
work/liberty_header.lib, and work/PREPARE.PASS gate.

## Step 2: remote PrimeLib

```sh
./scripts/bsub_run_all.sh
```

Default queue: ioqueue2; module: tsa/primelib_2024.01-SP1; corner: TT_1p1_25c.

Switch corner:

```sh
PROJECT_CONFIG=config/project.FF_1p2_m40c.json ./scripts/bsub_run_all.sh
```

Output: output/iolib_io_all_comb_TT_1p1_25c.lib

## Step 3: strict validation

validate_lib.py checks exact cell inventory, no ff/latch state groups,
slew/load grid match, and 8 threshold attributes.

## Step 4: LC to DB (optional)

```sh
./scripts/run_lc_lib_to_db.sh
```
"""

B_CHAR_TCL = """# PrimeLib timing/power characterization for iolib_io IO combinational cells.
foreach required_env {
  ALL_COMB_CONFIG_TCL ALL_COMB_HEADER_FILE ALL_COMB_CELL_FILE
  ALL_COMB_NETLIST_FILE ALL_COMB_OUTPUT_LIB
} {
  if {![info exists env($required_env)]} { error "Set environment variable $required_env" }
}
proc read_cell_list {path} {
  set fp [open $path r]; set cells {}
  while {[gets $fp line] >= 0} { regsub {#.*$} $line {} line; set cell [string trim $line]; if {$cell ne ""} { lappend cells $cell } }
  close $fp; return $cells
}
source $env(ALL_COMB_CONFIG_TCL)
set CELLS [read_cell_list $env(ALL_COMB_CELL_FILE)]
if {[llength $CELLS] == 0} { error "No IO combinational cells selected" }
if {$CELLS ne $CONFIG_CELLS} { error "Prepared Tcl cell list does not match config/cells.txt" }
set PROJECT_ROOT [file normalize [pwd]]
set CHAR_DIR [file join $PROJECT_ROOT work primelib_char_$CONFIG_CORNER]
file delete -force $CHAR_DIR; file mkdir $CHAR_DIR
puts "IO combinational cell count: [llength $CELLS]"
create $CHAR_DIR; set_location $CHAR_DIR
set_parameter active_pvts [list $CONFIG_CORNER]
set_parameter nmos_model_names $CONFIG_NMOS_MODELS
set_parameter pmos_model_names $CONFIG_PMOS_MODELS
set_parameter power_meas_supplies {iovcc}
set_parameter power_meas_grounds {iovss}
create_operating_condition $CONFIG_CORNER
set_opc_process $CONFIG_CORNER $CONFIG_MODEL_PROCESS
add_opc_supplies $CONFIG_CORNER iovcc $CONFIG_VCC iovbp $CONFIG_VBP VDD $CONFIG_VCC
add_opc_grounds $CONFIG_CORNER iovss $CONFIG_VSS iovbn $CONFIG_VBN VSS $CONFIG_VSS
set_opc_temperature $CONFIG_CORNER $CONFIG_TEMPERATURE
import -netlist_dir [file join $PROJECT_ROOT work import_netlists_$CONFIG_CORNER] -extension .sp -recognize -flatten -overwrite -powers {iovcc iovbp} -grounds {iovss iovbn} $CELLS
set_config_opt -cell $CELLS -from_direction LH explicit_points_slew $CONFIG_TR_SECONDS
set_config_opt -cell $CELLS -from_direction HL explicit_points_slew $CONFIG_TF_SECONDS
set_config_opt -cell $CELLS explicit_points_load $CONFIG_CAP_FARADS
configure -timing -power $CELLS
characterize $CELLS
model -timing -power -liberty -create_new_model -operating_condition $CONFIG_CORNER -library_type best -header_file $env(ALL_COMB_HEADER_FILE) -filename $env(ALL_COMB_OUTPUT_LIB) $CELLS
puts "PrimeLib IO-comb characterization done"
exit 0
"""

B_BSUB = """#!/usr/bin/env bash
set -euo pipefail
QUEUE="${LSF_QUEUE:-ioqueue2_io}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODULE_CMD="${PRIMELIB_MODULE_CMD:-module load tsa/primelib_2024.01-SP1}"
PROJECT_CONFIG="${PROJECT_CONFIG:-config/project.json}"
if [[ "$PROJECT_CONFIG" != /* ]]; then PROJECT_CONFIG="$PROJECT_DIR/$PROJECT_CONFIG"; fi
if [[ ! -f "$PROJECT_CONFIG" ]]; then printf 'Error: project config not found: %s\\n' "$PROJECT_CONFIG" >&2; exit 2; fi
if ! python3 -m json.tool "$PROJECT_CONFIG" >/dev/null; then printf 'Error: invalid JSON: %s\\n' "$PROJECT_CONFIG" >&2; exit 2; fi
configured_paths_output="$(python3 -c 'import json, sys; c=json.load(open(sys.argv[1])); m=c["model"]; print(c["source_netlist"]); print(m["main_file"]); print(m["include_file"])' "$PROJECT_CONFIG")" || exit 2
mapfile -t CONFIGURED_PATHS <<< "$configured_paths_output"
CONFIGURED_SOURCE="${CONFIGURED_PATHS[0]}"
if [[ "$CONFIGURED_SOURCE" != /* ]]; then CONFIGURED_SOURCE="$PROJECT_DIR/$CONFIGURED_SOURCE"; fi
if [[ ! -f "$CONFIGURED_SOURCE" ]]; then printf 'Error: source netlist not found: %s\\n' "$CONFIGURED_SOURCE" >&2; exit 2; fi
printf 'Source netlist: %s\\n' "$CONFIGURED_SOURCE"
bsub -I -q "$QUEUE" /usr/bin/env "PROJECT_CONFIG=$PROJECT_CONFIG" "PRIMELIB_MODULE_CMD=$MODULE_CMD" /bin/bash "$PROJECT_DIR/scripts/run_compute.sh"
"""

B_RUN_COMPUTE = """#!/usr/bin/env bash
set -eo pipefail
printf 'JOB_STAGE compute_start host=%s\\n' "$(hostname)"
job_stage="module_init"
if [[ ! -r /apps/cad/Modules/init/bash ]]; then printf 'JOB_ERROR stage=%s\\n' "$job_stage" >&2; exit 10; fi
set +u; source /apps/cad/Modules/init/bash; set -u
job_stage="module_load"
module_command="${PRIMELIB_MODULE_CMD:-module load tsa/primelib_2024.01-SP1}"
eval "$module_command"
job_stage="project_setup"
project_dir="$(cd "$(dirname "$0")/.." && pwd)"; cd "$project_dir"
export PRIMELIB_BIN="${PRIMELIB_BIN:-primelib}"
: "${PROJECT_CONFIG:?PROJECT_CONFIG is required}"
job_stage="run_all"
./scripts/run_all.sh
"""

B_RUN_ALL = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PROJECT_CONFIG="${PROJECT_CONFIG:-config/project.json}"
./scripts/run_prepare.sh
./scripts/run_primelib.sh
"""

B_RUN_PREPARE = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT_CONFIG="${PROJECT_CONFIG:-config/project.json}"
python3 scripts/prepare_project.py --project-root "$PWD" --config "$PROJECT_CONFIG"
"""

B_RUN_PRIMELIB = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${PRIMELIB_BIN:=primelib}"
PROJECT_CONFIG="${PROJECT_CONFIG:-config/project.json}"
CORNER="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["corner"])' "$PROJECT_CONFIG")"
CONFIG_TCL="$PWD/work/char_config.tcl"
HEADER_FILE="$PWD/work/liberty_header.lib"
CELL_FILE="$PWD/config/cells.txt"
NETLIST_FILE="$PWD/netlists/iolib_io_all_comb_closure.sp"
PREPARE_SENTINEL="$PWD/work/PREPARE.PASS"
OUTPUT_LIB="$PWD/output/iolib_io_all_comb_${CORNER}.lib"
LOG="$PWD/logs/primelib_all_comb_${CORNER}.log"
for required_file in "$CONFIG_TCL" "$HEADER_FILE" "$CELL_FILE" "$NETLIST_FILE" "$PREPARE_SENTINEL"; do
    if [[ ! -s "$required_file" ]]; then printf 'Error: missing prepared input: %s\\n' "$required_file" >&2; exit 2; fi
done
mkdir -p logs output work
export ALL_COMB_CONFIG_TCL="$CONFIG_TCL" ALL_COMB_HEADER_FILE="$HEADER_FILE" ALL_COMB_CELL_FILE="$CELL_FILE" ALL_COMB_NETLIST_FILE="$NETLIST_FILE" ALL_COMB_OUTPUT_LIB="$OUTPUT_LIB"
"$PRIMELIB_BIN" -x "source primelib/char_io_comb.tcl" 2>&1 | tee "$LOG"
python3 scripts/validate_lib.py "$OUTPUT_LIB" --cell-file "$CELL_FILE" --config "$PROJECT_CONFIG"
printf 'ALL IO COMB CHARACTERIZATION PASS: %s\\n' "$OUTPUT_LIB"
"""

B_RUN_LC = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs output
: "${LC_BIN:=lc_shell}"
CORNER="${1:-TT_1p1_25c}"
SOURCE_LIB="${2:-output/iolib_io_all_comb_${CORNER}_lc.lib}"
DB_FILE="${3:-output/iolib_io_all_comb_${CORNER}.db}"
if [[ ! -s "$SOURCE_LIB" ]]; then printf 'Error: missing Liberty: %s\\n' "$SOURCE_LIB" >&2; exit 2; fi
LC_LIBRARY_NAME="$(sed -nE 's/^[[:space:]]*library[[:space:]]*\\([[:space:]]*([^[:space:])]+).*/\\1/p' "$SOURCE_LIB" | head -n1)"
LC_EXPECTED_CELLS="$(awk 'NF && $1 !~ /^#/ {count++} END {print count+0}' config/cells.txt)"
export LC_INPUT_LIB="$SOURCE_LIB" LC_OUTPUT_DB="$DB_FILE" LC_LIBRARY_NAME LC_EXPECTED_CELLS
"${LC_BIN}" -f scripts/lib_to_db.tcl 2>&1 | tee "logs/lc_lib_to_db_${CORNER}.log"
"""

B_LIB_TO_DB = """proc finalize_library {} {
  global env
  foreach required_var {LC_INPUT_LIB LC_OUTPUT_DB LC_LIBRARY_NAME LC_EXPECTED_CELLS} {
    if {![info exists env($required_var)]} { error "Set environment variable $required_var" }
  }
  set lib_file $env(LC_INPUT_LIB); set db_file $env(LC_OUTPUT_DB)
  set lib_name $env(LC_LIBRARY_NAME); set expected_cells $env(LC_EXPECTED_CELLS)
  if {![file exists $lib_file]} { error "Missing input Liberty $lib_file" }
  read_lib $lib_file
  set loaded_cells [get_lib_cells -quiet ${lib_name}/*]
  set cell_count [sizeof_collection $loaded_cells]
  if {$cell_count != $expected_cells} { error "Loaded $cell_count cells; expected $expected_cells" }
  write_lib $lib_name -format db -output $db_file
  puts "LC conversion passed: $cell_count cells"
}
if {[catch {finalize_library} message]} { puts stderr "Error: $message"; exit 1 }
exit 0
"""

B_PREPARE_PY = """#!/usr/bin/env python3
\"\"\"Prepare iolib_io IO-combinational PrimeLib project.\"\"\"
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

def read_subckts(netlist: str) -> dict[str, list[str]]:
    subckts = {}
    for m in re.finditer(r'\\.SUBCKT\\s+(\\S+)([^\\n]*)', netlist):
        name, pins = m.group(1), m.group(2).split()
        subckts[name] = pins
    return subckts

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root
    config = json.loads(args.config.read_text(encoding="utf-8"))
    library = config["library"]
    src = config["source_netlist"]
    src_path = src if src.startswith("/") else root / src
    netlist = src_path.read_text(encoding="utf-8", errors="replace")
    subckts = read_subckts(netlist)
    cells_path = root / "cells.txt"
    cells = [l.split("#",1)[0].strip() for l in cells_path.read_text().splitlines() if l.split("#",1)[0].strip()]
    missing = [c for c in cells if c not in subckts]
    if missing:
        (root/"reports").mkdir(exist_ok=True)
        (root/"reports"/"missing_selected_subckts.tsv").write_text("\\n".join(missing)+"\\n")
        print(f"FAIL: missing {len(missing)} cells", file=sys.stderr); return 1
    (root/"work").mkdir(exist_ok=True)
    (root/"work"/"PREPARE.PASS").write_text("ok\\n")
    print(f"PREPARE PASS: {len(cells)} IO comb cells for {library}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""

B_VALIDATE_PY = """#!/usr/bin/env python3
\"\"\"Validate exact cell inventory and shared lookup-table settings for iolib_io.\"\"\"
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

def read_cells(path: Path) -> list[str]:
    return [l.split("#",1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines() if l.split("#",1)[0].strip()]

def axes(text: str, n: int) -> list[list[float]]:
    return [[float(v.strip()) for v in vals.split(",")] for vals in re.findall(rf'\\bindex_{n}\\s*\\(\\s*"([^"]+)"\\s*\\)', text, re.IGNORECASE)]

def close(a: list[float], b: list[float]) -> bool:
    return len(a)==len(b) and all(abs(x-y)<=max(1e-9,abs(y)*1e-6) for x,y in zip(a,b))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("liberty", type=Path)
    ap.add_argument("--cell-file", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True)
    args = ap.parse_args()
    expected = read_cells(args.cell_file)
    text = args.liberty.read_text(encoding="utf-8")
    actual = re.findall(r"^\\s*cell\\s*\\(\\s*([^\\s)]+)\\s*\\)", text, re.MULTILINE)
    if set(actual) != set(expected) or len(actual) != len(expected):
        raise ValueError(f"inventory mismatch: expected={len(expected)} actual={len(actual)}")
    if re.search(r"^\\s*(?:ff|latch)\\s*\\(", text, re.MULTILINE|re.IGNORECASE):
        raise ValueError("sequential ff/latch state group found")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    grid = config["grid"]
    for key in ("rise_slew_ns","fall_slew_ns"):
        exp_axis = [float(v) for v in grid[key]]
        if not any(close(a, exp_axis) for a in axes(text,1)): raise ValueError(f"{key} grid not found")
    load = [float(v) for v in grid["load_pf"]]
    if not any(close(a, load) for a in axes(text,2)): raise ValueError("load_pf grid not found")
    th = config["threshold_pct"]
    for attr, want in {"input_threshold_pct_rise":th["input"],"output_threshold_pct_fall":th["output"],"slew_lower_threshold_pct_rise":th["slew_lower"],"slew_upper_threshold_pct_rise":th["slew_upper"]}.items():
        m = re.search(rf"\\b{attr}\\s*:\\s*([-+0-9.eE]+)\\s*;", text)
        if not m or abs(float(m.group(1))-float(want))>1e-9: raise ValueError(f"missing {attr}")
    print(f"PASS: {len(actual)} IO combinational cells: {args.liberty}")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except (OSError,KeyError,TypeError,ValueError,json.JSONDecodeError) as e:
        print(f"FAIL: {e}", file=sys.stderr); raise SystemExit(1)
"""

B_PATCH_PY = """#!/usr/bin/env python3
\"\"\"Patch iolib_io Liberty for LC compatibility (add delay_model, areas, clear_preset).\"\"\"
from __future__ import annotations
import re, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {Path(sys.argv[0]).name} input.lib output.lib", file=sys.stderr); return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    text = src.read_text()
    if "delay_model" not in text:
        text = re.sub(r"(library\\s*\\([^)]*\\)\\s*\\{\\s*)", r"\\1\\n  delay_model : table_lookup; ", text, count=1)
    dst.write_text(text)
    print(f"Wrote LC-compatible Liberty: {dst}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""

B_NETLISTS_README = "# Generated netlists\n\nrun_prepare.sh generates recursive closure here.\n"

B_FILES = {
    "README.md": B_README,
    "cells.txt": B_CELLS_TXT,
    "config/project.json": B_PROJECT_JSON,
    "config/project.FF_1p2_m40c.json": B_PROJECT_JSON_ALT,
    "config/cells.txt": B_CELLS_TXT,
    "primelib/char_io_comb.tcl": B_CHAR_TCL,
    "scripts/bsub_run_all.sh": B_BSUB,
    "scripts/run_compute.sh": B_RUN_COMPUTE,
    "scripts/run_all.sh": B_RUN_ALL,
    "scripts/run_prepare.sh": B_RUN_PREPARE,
    "scripts/run_primelib.sh": B_RUN_PRIMELIB,
    "scripts/run_lc_lib_to_db.sh": B_RUN_LC,
    "scripts/lib_to_db.tcl": B_LIB_TO_DB,
    "scripts/prepare_project.py": B_PREPARE_PY,
    "scripts/validate_lib.py": B_VALIDATE_PY,
    "scripts/patch_lib_for_lc.py": B_PATCH_PY,
    "netlists/README.md": B_NETLISTS_README,
}

# ---------- Reference solution: analyze_flow.py ----------
ANALYZE_FLOW_PY = '''#!/usr/bin/env python3
"""Analyze a PrimeLib characterization project directory and emit structured JSON.

Usage: python3 analyze_flow.py <project_dir> [-o out.json]
Parses config/project.json, cells.txt, scripts/, primelib/*.tcl to describe
the K-library characterization flow (library, corner, steps, gate, tools,
validation checks, corner-switching mechanism).
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def _read_cells(path: Path) -> list[str]:
    return [l.split("#", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines()
            if l.split("#", 1)[0].strip()]


def _load_config(project: Path) -> dict:
    cfg_path = project / "config" / "project.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"config/project.json not found in {project}")
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _detect_steps(project: Path) -> list[dict]:
    scripts = project / "scripts"
    steps = []
    mapping = [
        ("prepare", "run_prepare.sh", "inventory + classification + SPICE closure + PREPARE.PASS gate"),
        ("bsub_submit", "bsub_run_all.sh", "LSF submission: validate config, check source/model, bsub run_compute"),
        ("compute", "run_compute.sh", "module init/load + project setup + run_all"),
        ("run_all", "run_all.sh", "orchestrate prepare + primelib"),
        ("primelib_char", "run_primelib.sh", "check prepare sentinel, run primelib char, validate output"),
        ("validate", "validate_lib.py", "strict cell inventory + no ff/latch + grid match + thresholds"),
        ("lc_to_db", "run_lc_lib_to_db.sh", "patch lib for LC + lc_shell read_lib/write_lib db"),
    ]
    for step, script, desc in mapping:
        if (scripts / script).exists():
            steps.append({"step": step, "script": script, "description": desc})
    return steps


def _detect_gate(project: Path) -> str:
    rp = project / "scripts" / "run_primelib.sh"
    if rp.exists():
        txt = rp.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'PREPARE[_A-Z]*.*?SENTINEL.*?"([^"]+)"', txt, re.I)
        if m:
            return m.group(1)
        m2 = re.search(r'(work/[A-Z.]*PASS[A-Z.]*)', txt)
        if m2:
            return m2.group(1)
    return "work/PREPARE.PASS"


def _detect_tools(project: Path) -> list[str]:
    tools = []
    rp = project / "scripts" / "run_primelib.sh"
    if rp.exists():
        txt = rp.read_text(encoding="utf-8", errors="replace")
        if "primelib" in txt.lower():
            tools.append("primelib")
    rlc = project / "scripts" / "run_lc_lib_to_db.sh"
    if rlc.exists():
        txt = rlc.read_text(encoding="utf-8", errors="replace")
        if "lc_shell" in txt:
            tools.append("lc_shell")
    return tools


def _detect_validation_checks(project: Path) -> list[str]:
    checks = []
    vp = project / "scripts" / "validate_lib.py"
    if vp.exists():
        txt = vp.read_text(encoding="utf-8", errors="replace")
        if "inventory" in txt.lower() or "set(actual)" in txt:
            checks.append("exact cell inventory matches cells.txt (no missing/unexpected/duplicate)")
        if "ff" in txt and "latch" in txt:
            checks.append("no sequential ff/latch state groups in ordinary-comb Liberty")
        if "rise_slew_ns" in txt or "index_1" in txt:
            checks.append("slew/load grid matches config (index_1/index_2 axes)")
        if "threshold_pct" in txt or "input_threshold_pct" in txt:
            checks.append("8 threshold attributes (input/output 50%, slew lower/upper) correct")
    return checks


def _detect_corner_mechanism(project: Path) -> str:
    bs = project / "scripts" / "bsub_run_all.sh"
    if bs.exists():
        txt = bs.read_text(encoding="utf-8", errors="replace")
        if "PROJECT_CONFIG" in txt:
            return "PROJECT_CONFIG env var selects corner JSON (e.g. config/project.FF_1p2_m40c.json)"
    return "config/project.json default corner"


def _detect_char_tcl(project: Path) -> str | None:
    pdir = project / "primelib"
    if pdir.exists():
        tcls = sorted(pdir.glob("*.tcl"))
        if tcls:
            return tcls[0].name
    return None


def analyze(project: Path) -> dict:
    project = Path(project)
    config = _load_config(project)
    cells_path = project / "cells.txt"
    cells = _read_cells(cells_path) if cells_path.exists() else []
    return {
        "library": config.get("library"),
        "corner": config.get("corner"),
        "process_section": config.get("process_section"),
        "source_netlist": config.get("source_netlist"),
        "cell_list_source": "cells.txt",
        "cell_count": len(cells),
        "cells": cells,
        "voltage": config.get("voltage"),
        "temperature_c": config.get("temperature_c"),
        "grid": config.get("grid"),
        "threshold_pct": config.get("threshold_pct"),
        "flow_steps": _detect_steps(project),
        "gate": _detect_gate(project),
        "tools": _detect_tools(project),
        "validation_checks": _detect_validation_checks(project),
        "corner_mechanism": _detect_corner_mechanism(project),
        "char_tcl": _detect_char_tcl(project),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("-o", "--output", default="flow_analysis.json")
    args = ap.parse_args()
    result = analyze(args.project_dir)
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

# ---------- check.py (16 conditions a-p) ----------
CHECK_PY = '''#!/usr/bin/env python3
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001.

Runs the submitted analyze_flow.py on the HIDDEN B project (iolib_io),
verifies 16 independent conditions on the output JSON, plus an anti-hardcode
guard (run on A project -> different library) and 3-seed determinism.
"""
import json, os, re, subprocess, sys, zipfile, tempfile, shutil, hashlib
from pathlib import Path

CONDITIONS = [
    ("a", "submit.zip valid zip containing analyze_flow.py"),
    ("b", "analyze_flow.py runs on hidden B project, exit 0"),
    ("c", 'output library == "iolib_io"'),
    ("d", 'output corner == "TT_1p1_25c"'),
    ("e", 'output source_netlist == "../netlist.io.sp"'),
    ("f", 'output cell_list_source == "cells.txt"'),
    ("g", "output cell_count == 15 (B cell count)"),
    ("h", "flow_steps has >=5 steps incl prepare/primelib_char/validate/lc_to_db"),
    ("i", 'gate mentions "PREPARE.PASS"'),
    ("j", 'tools contains "primelib"'),
    ("k", "validation_checks non-empty list mentioning cell inventory"),
    ("l", 'corner_mechanism mentions "PROJECT_CONFIG"'),
    ("m", "voltage.vcc == 1.1 and voltage.vbp == 1.1"),
    ("n", "temperature_c == 25.0"),
    ("o", "anti-hardcode: run on A project -> library == stdcells_ac (different from B)"),
    ("p", "3-seed determinism: 3 runs produce identical output"),
]


def _run_analyze(script: Path, project: Path, out: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(script), str(project), "-o", str(out)],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"analyze_flow.py exit {proc.returncode}: {proc.stderr[:500]}")
    return json.loads(out.read_text(encoding="utf-8"))


def check(deliverable, workdir) -> bool:
    workdir = Path(workdir)
    fails = []

    # a: zip valid + contains analyze_flow.py
    script = None
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        try:
            with zipfile.ZipFile(deliverable) as zf:
                names = zf.namelist()
                if "analyze_flow.py" not in names:
                    fails.append("a")
                else:
                    zf.extract("analyze_flow.py", td)
                    script = td / "analyze_flow.py"
        except Exception:
            fails.append("a")
            raise AssertionError("a: invalid zip or missing analyze_flow.py: " + str(fails))

        if script is None:
            raise AssertionError("a: analyze_flow.py not found in zip")

        b_project = workdir / "hidden" / "iolib_io_project"
        a_project = workdir / "hidden" / "primelib_char_all_comb"
        out = td / "out.json"

        # b: run on B
        try:
            res = _run_analyze(script, b_project, out)
        except Exception as ex:
            fails.append("b")
            raise AssertionError("b: " + str(ex))

        # c: library
        if res.get("library") != "iolib_io": fails.append("c")
        # d: corner
        if res.get("corner") != "TT_1p1_25c": fails.append("d")
        # e: source_netlist
        if res.get("source_netlist") != "../netlist.io.sp": fails.append("e")
        # f: cell_list_source
        if res.get("cell_list_source") != "cells.txt": fails.append("f")
        # g: cell_count
        if res.get("cell_count") != 15: fails.append("g")
        # h: flow_steps
        steps = res.get("flow_steps", [])
        step_names = {s.get("step") for s in steps} if isinstance(steps, list) else set()
        if len(steps) < 5 or not {"prepare", "primelib_char", "validate", "lc_to_db"}.issubset(step_names):
            fails.append("h")
        # i: gate
        if "PREPARE.PASS" not in str(res.get("gate", "")): fails.append("i")
        # j: tools
        if "primelib" not in res.get("tools", []): fails.append("j")
        # k: validation_checks
        vc = res.get("validation_checks", [])
        if not vc or not any("inventory" in str(c).lower() for c in vc): fails.append("k")
        # l: corner_mechanism
        if "PROJECT_CONFIG" not in str(res.get("corner_mechanism", "")): fails.append("l")
        # m: voltage
        v = res.get("voltage", {})
        if v.get("vcc") != 1.1 or v.get("vbp") != 1.1: fails.append("m")
        # n: temperature
        if res.get("temperature_c") != 25.0: fails.append("n")

        # o: anti-hardcode (run on A -> stdcells_ac)
        try:
            out_a = td / "out_a.json"
            res_a = _run_analyze(script, a_project, out_a)
            if res_a.get("library") != "stdcells_ac":
                fails.append("o")
        except Exception:
            fails.append("o")

        # p: 3-seed determinism
        try:
            outs = []
            for s in range(3):
                o = td / f"det_{s}.json"
                _run_analyze(script, b_project, o)
                outs.append(o.read_bytes())
            if not (outs[0] == outs[1] == outs[2]):
                fails.append("p")
        except Exception:
            fails.append("p")

    if fails:
        raise AssertionError("FAIL conditions: " + ",".join(fails))
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        ok = check(sys.argv[1], sys.argv[2])
        print("PASS" if ok else "FAIL")
    else:
        print("usage: check.py <deliverable.zip> <workdir>", file=sys.stderr)
        sys.exit(2)
'''

# ---------- Negatives ----------
NEG_EMPTY = '''#!/usr/bin/env python3
import sys, json
# empty shell: does nothing, produces no output
'''
NEG_PRINT = '''#!/usr/bin/env python3
import sys, json, os
# prints expected B values hardcoded, no parsing
out = {"library":"iolib_io","corner":"TT_1p1_25c","source_netlist":"../netlist.io.sp",
       "cell_list_source":"cells.txt","cell_count":15,"cells":[],
       "voltage":{"vcc":1.1,"vss":0.0,"vbn":0.0,"vbp":1.1},"temperature_c":25.0,
       "grid":{},"threshold_pct":{},
       "flow_steps":[{"step":"prepare"},{"step":"primelib_char"},{"step":"validate"},{"step":"lc_to_db"},{"step":"bsub_submit"}],
       "gate":"work/PREPARE.PASS","tools":["primelib"],"validation_checks":["cell inventory"],
       "corner_mechanism":"PROJECT_CONFIG env var","char_tcl":"char_io_comb.tcl"}
o = sys.argv[sys.argv.index("-o")+1] if "-o" in sys.argv else "flow_analysis.json"
open(o,"w").write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
'''
NEG_CORE_DEL = '''#!/usr/bin/env python3
# core logic deleted: only reads config, no steps/gate/tools/validation detection
import sys, json
from pathlib import Path
ap = sys.argv
project = Path(ap[1])
cfg = json.loads((project/"config"/"project.json").read_text())
out = {"library": cfg.get("library"), "corner": cfg.get("corner"),
       "source_netlist": cfg.get("source_netlist"), "cell_list_source": "cells.txt"}
cells = [l.strip() for l in (project/"cells.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
out["cell_count"] = len(cells)
o = ap[ap.index("-o")+1] if "-o" in ap else "flow_analysis.json"
open(o,"w").write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
'''
NEG_WRONG_LIB = '''#!/usr/bin/env python3
# hardcodes wrong library (A value) -> fails c, and o (B run gives stdcells_ac)
import sys, json
out = {"library":"stdcells_ac","corner":"TT_1p1_25c","source_netlist":"../netlist.io.sp",
       "cell_list_source":"cells.txt","cell_count":15,"cells":[],
       "voltage":{"vcc":1.1,"vss":0.0,"vbn":0.0,"vbp":1.1},"temperature_c":25.0,
       "grid":{},"threshold_pct":{},
       "flow_steps":[{"step":"prepare"},{"step":"primelib_char"},{"step":"validate"},{"step":"lc_to_db"},{"step":"bsub_submit"}],
       "gate":"work/PREPARE.PASS","tools":["primelib"],"validation_checks":["cell inventory"],
       "corner_mechanism":"PROJECT_CONFIG env var","char_tcl":"char_io_comb.tcl"}
o = sys.argv[sys.argv.index("-o")+1] if "-o" in sys.argv else "flow_analysis.json"
open(o,"w").write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
'''

NEGATIVES = {
    "naive_empty.py": NEG_EMPTY,
    "naive_print_expected.py": NEG_PRINT,
    "naive_core_deleted.py": NEG_CORE_DEL,
    "naive_wrong_lib.py": NEG_WRONG_LIB,
}

NEG_SELFTEST = '''#!/usr/bin/env python3
import json, subprocess, sys, tempfile, zipfile
from pathlib import Path
REF = Path(__file__).parent
check = REF / "check.py"
submit_zip = REF / "reference_submit.zip"
negs = ["naive_empty.py","naive_print_expected.py","naive_core_deleted.py","naive_wrong_lib.py"]
rc = 0
for neg in negs:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        zpath = td / "submit.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.write(REF / "negative" / neg, "analyze_flow.py")
        proc = subprocess.run([sys.executable, str(check), str(zpath), str(REF / "hidden_workdir")],
                              capture_output=True, text=True, timeout=120)
        status = "FAIL" if proc.returncode != 0 else "PASS"
        first_fail = ""
        if proc.returncode == 0:
            first_fail = "UNEXPECTED_PASS"
        else:
            import re as _re
            m = _re.search(r"FAIL conditions: ([a-z,]+)", proc.stderr + proc.stdout)
            first_fail = m.group(1) if m else proc.stderr[:80]
        print(f"{neg}: {status} (first_fail={first_fail})")
        if proc.returncode == 0: rc = 1
print("NEG_RC=%d" % rc)
sys.exit(rc)
'''

# ---------- Build ----------
def build():
    # A assets (real primelib_char_all_comb) — populated by transfer step
    a_dir = AST / "primelib_char_all_comb"
    # Hidden B
    b_dir = AST / "hidden" / "iolib_io_project"
    if b_dir.exists(): shutil.rmtree(b_dir)
    for rel, content in B_FILES.items():
        fp = b_dir / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
    # Reference
    if REF.exists(): shutil.rmtree(REF)
    REF.mkdir(parents=True)
    (REF / "analyze_flow.py").write_text(ANALYZE_FLOW_PY, encoding="utf-8")
    (REF / "check.py").write_text(CHECK_PY, encoding="utf-8")
    (REF / "negative").mkdir()
    for n, c in NEGATIVES.items():
        (REF / "negative" / n).write_text(c, encoding="utf-8")
    (REF / "negative_selftest.py").write_text(NEG_SELFTEST, encoding="utf-8")
    print("Built B project, reference, negatives.")
    print(f"A assets dir: {a_dir} (exists={a_dir.exists()})")

if __name__ == "__main__":
    build()
