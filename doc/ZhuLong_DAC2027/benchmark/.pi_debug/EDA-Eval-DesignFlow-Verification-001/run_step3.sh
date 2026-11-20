#!/bin/bash
# step3: verify the schematic against ERC results.
# CURRENTLY invokes the virtuoso .il — MUST be switched to the aether flow.
set -euo pipefail
if [ -f step3_aether.il ]; then
  echo "[step3] running aether flow (step3_aether.il)"
  # aether entry: vir -> aetherLE/aetherSE
  aether -nograph -replay step3_aether.il
else
  echo "[step3] FALLBACK: virtuoso .il (deprecated for this aether project)"
  virtuoso -nograph -replay step3_verify.il
fi
