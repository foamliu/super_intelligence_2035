#!/bin/bash
# summarize_meas.sh - summarize IsmOscTestSweep measurement results per corner.
#
# Usage: bash summarize_meas.sh [BASE_DIR]
#   BASE_DIR defaults to the script's own directory.
#   BASE_DIR must contain: meas_result_by_corner_1021/cornerN/*.mt0
#
# Produces:
#   <BASE_DIR>/meas_summary/cornerN.csv           per-corner measurement table
#   <BASE_DIR>/all_corners_summary.csv            combined table (all corners)
# Exit status: 0 if all samples PASS; 2 if any sample FAIL (summary still written);
#              non-zero (find/set -e) if a corner result dir is missing (BUG).
set -eu
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="${1:-$SCRIPT_DIR}"
SWEEP=1021
RESULT_ROOT="$BASE/meas_result_by_corner_${SWEEP}"
SUMMARY_ROOT="$BASE/meas_summary"
ALL_CSV="$BASE/all_corners_summary.csv"

mkdir -p "$SUMMARY_ROOT"

sort_by_sample_number() {
  # read mt0 paths from stdin, sort by the numeric <N> in IsmOscTestSweep_s<N>.mt0
  while IFS= read -r line; do
    b="$(basename "$line" .mt0)"        # IsmOscTestSweep_s12
    n="${b##*_s}"                        # 12
    printf '%s\t%s\n' "$n" "$line"
  done | sort -k1,1n | cut -f2-
}

CORNERS="corner0 corner1 corner2 corner3"

overall_fail=0
for corner in $CORNERS; do
  result_dir="$RESULT_ROOT/$corner"
  input_list="$SUMMARY_ROOT/${corner}_input.list"
  # (original) list mt0 files for this corner
  find "$result_dir" -maxdepth 1 -type f -name '*.mt0' | sort_by_sample_number > "$input_list"
  corner_csv="$SUMMARY_ROOT/${corner}.csv"
  : > "$corner_csv"
  while IFS= read -r mt0; do
    [ -z "$mt0" ] && continue
    sample="$(basename "$mt0" .mt0 | sed 's/IsmOscTestSweep_//')"
    pass_flag="$(grep -E '^[[:space:]]*pass_flag=' "$mt0" | tail -1 | sed 's/.*pass_flag=[[:space:]]*//')"
    last_pls="$(grep -E '^[[:space:]]*last_pls_pre0=' "$mt0" | tail -1 | sed 's/.*last_pls_pre0=[[:space:]]*//')"
    if [ "$pass_flag" = "1.000000e+00" ]; then
      status=PASS
    else
      status=FAIL; overall_fail=1
      echo "[ALARM] $corner sample=$sample pass_flag=$pass_flag file=$mt0"
    fi
    echo "$corner,$sample,$pass_flag,$last_pls,$status" >> "$corner_csv"
  done < "$input_list"
done

# combined summary (written AFTER all corners processed)
echo "corner,sample,pass_flag,last_pls_pre0,status" > "$ALL_CSV"
for corner in $CORNERS; do
  corner_csv="$SUMMARY_ROOT/${corner}.csv"
  [ -f "$corner_csv" ] && grep -v '^$' "$corner_csv" >> "$ALL_CSV"
done
echo "Wrote $ALL_CSV"

if [ "$overall_fail" = "1" ]; then exit 2; fi
