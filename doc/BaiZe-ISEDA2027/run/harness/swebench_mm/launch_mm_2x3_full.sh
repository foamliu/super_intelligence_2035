#!/bin/bash
# Launch SWE-bench Multimodal 2x3 full predict (480 instances x 6 routes).
# Each route runs as an independent setsid background process with its own
# workdir (per-route) and proxy port (cline routes: 9095..9097).
# CPU-light (agents wait on API); eval phase (Docker) is launched separately
# with CPU limits (taskset 0-15 + OMP=1) to avoid sklearn-style spirals.
#
# Usage:  bash launch_mm_2x3_full.sh           # launch all 6 routes
#         bash launch_mm_2x3_full.sh status    # show progress per route
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

ROUTES=(
  cline__deepseek-v4-flash
  cline__kimi-k2.6
  cline__doubao
  opencode__deepseek-v4-flash
  opencode__kimi-k2.6
  opencode__doubao
)

if [ "${1:-}" = "status" ]; then
  for r in "${ROUTES[@]}"; do
    pf="progress_2x3/${r}.json"
    done_n=0; has=0; empty=0; infra=0; blocked=0
    if [ -f "$pf" ]; then
      read -r done_n has empty infra blocked < <(python3 -c "
import json,sys
d=json.load(open('$pf'))
h=e=im=b=0
for v in d.values():
    c=v.get('classification','')
    if c=='has_patch': h+=1
    elif c=='empty_patch': e+=1
    elif c=='infra': im+=1
    elif c=='blocked': b+=1
print(len(d),h,e,im,b)
" 2>/dev/null || echo "0 0 0 0 0")
    fi
    running=$(pgrep -f "run_mm_2x3.py predict --route $r" >/dev/null 2>&1 && echo "RUN" || echo "idle")
    printf '  %-28s %3s done | has=%3s empty=%3s infra=%3s blocked=%3s | %s\n' "$r" "$done_n" "$has" "$empty" "$infra" "$blocked" "$running"
  done
  exit 0
fi

mkdir -p logs_2x3
for r in "${ROUTES[@]}"; do
  log="logs_2x3/predict_${r}.log"
  if pgrep -f "run_mm_2x3.py predict --route $r" >/dev/null 2>&1; then
    echo "  $r already running, skip"
    continue
  fi
  echo "  launching $r -> $log"
  setsid bash -c "cd '$HERE' && python3 run_mm_2x3.py predict --route '$r' > '$log' 2>&1" \
    < /dev/null > /dev/null 2>&1 &
  sleep 2   # stagger launches to avoid a thundering herd on the gateway
done
echo "All 6 routes launched. Check: bash $0 status"
