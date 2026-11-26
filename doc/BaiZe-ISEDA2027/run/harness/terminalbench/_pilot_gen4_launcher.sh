#!/usr/bin/env bash
# One-shot 7x5 pilot Gen4 launcher (R448). Run on .29. NOT committed (temp).
# Fixes the two .29 issues: harbor not on non-interactive PATH, orphaned 9090.
set -euo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
# keys.txt uses FULL-WIDTH colon (：); awk -F'：' splits on it.
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[launcher] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "[launcher] FATAL: TB_API_KEY empty"; exit 1; }
cd "$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench" || { echo "[launcher] FATAL: cd failed"; exit 2; }
# Pre-check the 5 pilot task dirs + their local docker images (MITM proxy can't pull).
DS="${HOME}/terminal-bench"
for t in break-filter-js-from-html bn-fit-modify log-summary-date-ranges chess-best-move fix-git; do
  if [ -d "$DS/$t" ]; then echo "[pre] DIR OK   $t"; else echo "[pre] DIR MISS $t"; fi
  if docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1; then echo "[pre] IMG OK   $t"; else echo "[pre] IMG MISS $t"; fi
done
echo "[launcher] ports before start:"; (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -E ':9090|:9091' || echo "[launcher] 9090/9091 free"
echo "[launcher] starting pilot Gen4 at $(date '+%F %T') ..."
exec bash launch_tb_7way.sh --pilot
