#!/bin/bash
# step0: environment sanity check.
set -euo pipefail
echo "[step0] PYBIN=${PYBIN:-python3}"
"${PYBIN:-python3}" --version
test -f ERC_Wesign.csv || { echo "ERC_Wesign.csv missing"; exit 1; }
echo "[step0] ok"
