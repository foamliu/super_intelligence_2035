#!/bin/bash
# step1: prepare netlist from ERC CSV, filtered by ERC_SECTION.
set -euo pipefail
"${PYBIN:-python3}" prepare_new_netlist.py \
  --csv ERC_Wesign.csv \
  --erc-section "${ERC_SECTION:-2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8}" \
  --out erc_report_2_1_to_2_8.csv
echo "[step1] wrote erc_report_2_1_to_2_8.csv"
