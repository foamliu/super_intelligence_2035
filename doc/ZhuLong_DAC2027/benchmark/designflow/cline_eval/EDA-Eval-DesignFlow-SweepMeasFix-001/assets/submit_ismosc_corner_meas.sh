#!/bin/bash
# submit_ismosc_corner_meas.sh - submit IsmOscTestSweep corner measurements.
# (on-disk version: already fixed for single-sweep datasets)
#
# The 20261021 sweep dir currently holds only the base (corner0) FSDBs, so
# corners 1-3 are skipped (no #N corner replicas in this dataset). Runs fscript
# directly (no interactive LSF) for the present corners.
set -eu
BASE="$(cd "$(dirname "$0")" && pwd)"
SWEEP_DIR="$BASE/superon_sweep_20261021_133105"
RESULT_ROOT="$BASE/meas_result_by_corner_1021"
LOG_ROOT="$BASE/meas_log_by_corner_1021"

gen_corner() {
  local corner="$1"
  local fsdb_glob="$2"
  local meas_sp="$BASE/IsmOscTestSweep_meas_${corner#corner}.sp"
  local outdir="$RESULT_ROOT/$corner"
  local logdir="$LOG_ROOT/$corner"
  mkdir -p "$outdir" "$logdir"
  local n
  n=$(ls $fsdb_glob 2>/dev/null | wc -l)
  if [ "$n" -eq 0 ]; then
    echo "WARNING: no FSDB matched for $corner; skipping"
    return 0
  fi
  : > "$BASE/fsdb_measure_${corner}.sp"
  for fsdb in $fsdb_glob; do
    local b=$(basename "$fsdb" .fsdb)
    echo "meas $meas_sp -i $fsdb -o $outdir/${b}.mt0 -l $logdir/${b}.log" >> "$BASE/fsdb_measure_${corner}.sp"
  done
  echo "Running fscript directly (no interactive LSF) for $corner ($n samples)"
  fscript "$BASE/fsdb_measure_${corner}.sp"
}

gen_corner corner0 "$SWEEP_DIR/IsmOscTestSweep_s*.fsdb"
gen_corner corner1 "$SWEEP_DIR/IsmOscTestSweep_s*_1.fsdb"
gen_corner corner2 "$SWEEP_DIR/IsmOscTestSweep_s*_2.fsdb"
gen_corner corner3 "$SWEEP_DIR/IsmOscTestSweep_s*_3.fsdb"
echo "submit done"
