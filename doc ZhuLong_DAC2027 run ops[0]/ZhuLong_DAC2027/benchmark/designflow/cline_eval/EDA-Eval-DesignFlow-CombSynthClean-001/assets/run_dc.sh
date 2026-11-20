#!/usr/bin/env bash
# =============================================================================
# Shell wrapper for Design Compiler synthesis of addr_to_rowcol_region
# Usage:  ./run_dc.sh
#
# All key parameters can be overridden from the environment, e.g.:
#   CLOCK_PERIOD_NS=3.0 ./run_dc.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# ---------------------------------------------------------------------------
# Configuration (overridable via environment)
# ---------------------------------------------------------------------------
export TARGET_DB=${TARGET_DB:-"${SCRIPT_DIR}/lib/stdcells_ac_FF_1p3_m40c.db"}
export TOP_DESIGN=${TOP_DESIGN:-addr_to_rowcol_region}
export RTL_FILE=${RTL_FILE:-"${SCRIPT_DIR}/rtl/addr_to_rowcol_region.v"}
export SDC_FILE=${SDC_FILE:-"${SCRIPT_DIR}/addr_to_rowcol_region.sdc"}
export OUTPUT_DIR=${OUTPUT_DIR:-"${SCRIPT_DIR}/out"}
export CLOCK_PERIOD_NS=${CLOCK_PERIOD_NS:-5.0}
export SETUP_UNCERTAINTY_NS=${SETUP_UNCERTAINTY_NS:-0.20}
export HOLD_MARGIN_NS=${HOLD_MARGIN_NS:-0.10}
export INPUT_DELAY_NS=${INPUT_DELAY_NS:-0.50}
export OUTPUT_DELAY_NS=${OUTPUT_DELAY_NS:-0.50}
export INPUT_TRANSITION_NS=${INPUT_TRANSITION_NS:-0.05}
export OUTPUT_LOAD=${OUTPUT_LOAD:-0.05}
export DATA_MAX_TRANSITION_NS=${DATA_MAX_TRANSITION_NS:-0.50}

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
command -v dc_shell >/dev/null 2>&1 || {
    echo "ERROR: dc_shell is not in PATH" >&2
    exit 127
}

for f in "$TARGET_DB" "$RTL_FILE" "$SDC_FILE"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: required file not found: $f" >&2
        exit 1
    fi
done

mkdir -p "${OUTPUT_DIR}"

echo "============================================================"
echo " Design Compiler synthesis"
echo "   TOP_DESIGN : ${TOP_DESIGN}"
echo "   RTL_FILE   : ${RTL_FILE}"
echo "   SDC_FILE   : ${SDC_FILE}"
echo "   TARGET_DB  : ${TARGET_DB}"
echo "   OUTPUT_DIR : ${OUTPUT_DIR}"
echo "============================================================"

# ---------------------------------------------------------------------------
# Run DC
# ---------------------------------------------------------------------------
dc_shell -no_gui -f "${SCRIPT_DIR}/synth.tcl" \
    | tee "${OUTPUT_DIR}/dc_console.log"

# ---------------------------------------------------------------------------
# Post-synthesis checks
# ---------------------------------------------------------------------------
MAPPED_NETLIST="${OUTPUT_DIR}/${TOP_DESIGN}_mapped.v"
DDC_FILE="${OUTPUT_DIR}/${TOP_DESIGN}_mapped.ddc"

if [[ ! -s "$MAPPED_NETLIST" ]]; then
    echo "ERROR: Mapped netlist not generated: $MAPPED_NETLIST" >&2
    exit 1
fi

if [[ ! -s "$DDC_FILE" ]]; then
    echo "ERROR: DDC file not generated: $DDC_FILE" >&2
    exit 1
fi

echo "============================================================"
echo " Synthesis completed successfully."
echo "   Mapped netlist : ${MAPPED_NETLIST}"
echo "   DDC database   : ${DDC_FILE}"
echo "   Reports        : ${OUTPUT_DIR}/reports/"
echo "============================================================"
