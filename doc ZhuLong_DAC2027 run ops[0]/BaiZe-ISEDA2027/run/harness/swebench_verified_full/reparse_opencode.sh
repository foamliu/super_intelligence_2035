#!/bin/bash
# Watcher: wait for opencode eval to finish, then re-parse with fixed EVAL_LOG_ROOT
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
MARKER=reports/.opencode_reparse_done
while [ ! -f "$MARKER" ]; do
  # Check if opencode eval process is still running
  if ! pgrep -f 'run_verified_full.py eval --harness opencode' > /dev/null 2>&1; then
    # opencode eval finished — re-parse
    echo "$(date '+%H:%M:%S') opencode eval done, re-parsing..."
    python3 -c "
import json
from run_verified_full import parse_eval
ids = ['django__django-10097','scikit-learn__scikit-learn-10297','pydata__xarray-2905','pytest-dev__pytest-10051','pylint-dev__pylint-4970','psf__requests-1142','astropy__astropy-12907','sympy__sympy-11618','sphinx-doc__sphinx-10323']
result = parse_eval('verified_full_opencode', ids, 'opencode')
print('opencode:', result)
" 2>&1
    touch "$MARKER"
    echo "$(date '+%H:%M:%S') opencode re-parse done"
    break
  fi
  sleep 15
done
