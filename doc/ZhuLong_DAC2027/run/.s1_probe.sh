#!/bin/bash
echo "PROBE_OK date=$(date +%F_%T)"
pgrep -f '^bash scripts/run_cline_script' && echo "PGREP_FOUND" || echo "PGREP_NONE"