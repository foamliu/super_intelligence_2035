#!/usr/bin/env bash
# One-shot 7x5 pilot Gen7 launcher (R467). Run on .29.
# Gen7 = Gen5 + R466 fixes: codex + claude-code pre-mounted fast path
#   (NFS npm packages mounted via overlay, avoiding in-container npm install
#   timeout that caused 4/5 and 3/5 infra errors in Gen5).
#   Also wraps with `sg docker` for Docker daemon access (R461 fix: user is in
#   docker group but current shell hasn't activated it).
# Verifies ALL 7 harnesses work in-container, especially the new codex +
# claude-code fast paths.
set -euo pipefail
export PATH="/home/app.e0031982/.local/bin:${PATH}"
REPO="/nas_train/app.e0031982/code/super_intelligence_2035"
# keys.txt uses FULL-WIDTH colon (：); awk -F'：' splits on it.
export TB_API_KEY="$(grep -A2 'kimi-k2.6-cloud' "$REPO/doc/keys.txt" | grep 'API Key' | awk -F'：' '{print $2}' | tr -d '[:space:]')"
echo "[gen7] HOST=$(hostname) TB_API_KEY_len=${#TB_API_KEY} harbor=$(command -v harbor || echo MISSING)"
[[ -n "${TB_API_KEY:-}" ]] || { echo "[gen7] FATAL: TB_API_KEY empty"; exit 1; }
cd "$REPO/doc/BaiZe-ISEDA2027/run/harness/terminalbench" || { echo "[gen7] FATAL: cd failed"; exit 2; }

# Pre-check the 5 pilot task dirs + their local docker images (MITM proxy can't pull).
DS="${HOME}/terminal-bench"
for t in break-filter-js-from-html bn-fit-modify log-summary-date-ranges chess-best-move fix-git; do
  if [ -d "$DS/$t" ]; then echo "[pre] DIR OK   $t"; else echo "[pre] DIR MISS $t"; fi
done
sg docker -c 'for t in break-filter-js-from-html bn-fit-modify log-summary-date-ranges chess-best-move fix-git; do
  if docker image inspect "alexgshaw/$t:20251031" >/dev/null 2>&1; then echo "[pre] IMG OK   $t"; else echo "[pre] IMG MISS $t"; fi
done'

# Pre-check NFS mounts for codex + claude-code fast path (R466).
echo "[pre] codex fast path:"; ls -la /nas_train/app.e0031982/download/codex-npm/@openai/codex/bin/codex.js 2>&1
echo "[pre] claude fast path:"; ls -la /nas_train/app.e0031982/download/claude-code-npm/@anthropic-ai/claude-code/bin/claude.exe 2>&1

echo "[gen7] ports before start:"; (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -E ':9090|:9091' || echo "[gen7] 9090/9091 free"
echo "[gen7] starting pilot Gen7 at $(date '+%F %T') ..."
echo "[gen7] logging to /tmp/tb_gen7_pilot.log"
# Wrap with sg docker so harbor run + docker info succeed inside launch_tb_7way.sh.
exec sg docker -c 'export TB_API_KEY="'"$TB_API_KEY"'" PATH="/home/app.e0031982/.local/bin:$PATH"; bash launch_tb_7way.sh --pilot'
