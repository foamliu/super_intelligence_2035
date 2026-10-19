#!/usr/bin/env bash
# One-shot 7x5 pilot Gen5 launcher (R453). Run on .29. NOT committed (temp).
# Gen5 = Gen4 + fixes: pi models.json schema (baseUrl+apiKey+models array,
#   matching proven host ~/.pi/agent/models.json) + claude-code non-root user
#   (useradd agent + environment.exec(user="agent") + chown workdir).
#   deepseek was already fixed in R452. hermes deferred (needs py3.14 in
#   container; container has 3.12, 3.14 not installable — honest blocker).
# Reuses the Gen4 launcher pattern (PATH + TB_API_KEY + precheck + exec).
set -euo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
# keys.txt uses FULL-WIDTH colon (：); awk -F'：' splits on it.
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[gen5] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "[gen5] FATAL: TB_API_KEY empty"; exit 1; }
cd "$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench" || { echo "[gen5] FATAL: cd failed"; exit 2; }
# Pre-check the 5 pilot task dirs + their local docker images (MITM proxy can't pull).
DS="${HOME}/terminal-bench"
for t in break-filter-js-from-html bn-fit-modify log-summary-date-ranges chess-best-move fix-git; do
  if [ -d "$DS/$t" ]; then echo "[pre] DIR OK   $t"; else echo "[pre] DIR MISS $t"; fi
  if docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1; then echo "[pre] IMG OK   $t"; else echo "[pre] IMG MISS $t"; fi
done
echo "[gen5] ports before start:"; (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -E ':9090|:9091' || echo "[gen5] 9090/9091 free"
echo "[gen5] starting pilot Gen5 at $(date '+%F %T') ..."
exec bash launch_tb_7way.sh --pilot
