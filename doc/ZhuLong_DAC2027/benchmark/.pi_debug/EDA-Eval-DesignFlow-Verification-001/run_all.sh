#!/bin/bash
# ERC_AI_CHECK pipeline (synthetic, derived from real trace ukkn7 — desensitized).
# Orchestrates step0..step3 over the drcpa/ ERC data.
set -euo pipefail
cd "$(dirname "$0")"

# Default: only ERC sub-sections 2.1..2.8 (the user's real ask).
export ERC_SECTION="${ERC_SECTION:-2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8}"
export PYBIN="${PYBIN:-python3}"

echo "[run_all] step0: env check"
./run_step0.sh
echo "[run_all] step1: prepare_new_netlist.py (filter ERC by section)"
./run_step1.sh
echo "[run_all] step2: analyze_errors_v1.py"
./run_step2.sh
echo "[run_all] step3: verify (aether flow via step3_aether.il)"
./run_step3.sh
echo "[run_all] done"
