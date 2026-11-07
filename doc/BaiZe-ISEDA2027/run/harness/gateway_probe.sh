#!/usr/bin/env bash
# gateway_probe.sh — Proper gateway health check (corrects the /models-only false positive).
#
# 2026-11-07 audit finding: `curl /v1/models` returns HTTP 200 even when the
# token quota is exhausted — it only lists available models, no quota check.
# The REAL test is a /v1/chat/completions call, which returns a Chinese error
# string "本次Token额度已用完" (or HTTP 429) when quota is used up.
#
# Usage:
#   ./gateway_probe.sh            # exit 0 = gateway fully usable, exit 1 = not
#   ./gateway_probe.sh --verbose  # print details
#
# This replaces the naive `curl -s -o /dev/null -w '%{http_code}' /v1/models`
# probe that R1736 used (and got a false "200 = recovered").
set -euo pipefail

KEY="02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
GW="http://agi-gateway.cxmt.com/v1"
VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

# Step 1: /models endpoint (quick liveness check)
models_rc=$(curl -s -o /dev/null -w '%{http_code}' -m 8 \
  "$GW/models" -H "Authorization: Bearer $KEY" 2>/dev/null || echo "000")

if [[ "$VERBOSE" == "1" ]]; then
  echo "[probe] /v1/models → HTTP $models_rc"
fi

if [[ "$models_rc" != "200" ]]; then
  echo "GATEWAY_DOWN: /v1/models returned $models_rc"
  exit 1
fi

# Step 2: /chat/completions (the REAL quota check — this is what R1736 missed)
resp=$(curl -s -m 15 "$GW/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY" \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  2>/dev/null || echo "CURL_FAILED")

if [[ "$VERBOSE" == "1" ]]; then
  echo "[probe] /v1/chat/completions → $(echo "$resp" | head -c 200)"
fi

# Check for quota exhaustion (Chinese error string or 429 in response)
if echo "$resp" | grep -qE '额度已用完|429|rate.limit|Rate.Limit|Too Many|CURL_FAILED'; then
  # Extract wait time if present
  wait_time=$(echo "$resp" | grep -oP '等待\K[0-9]+分钟[0-9]+秒' || echo "unknown")
  echo "GATEWAY_QUOTA_EXHAUSTED: chat completions blocked. Wait: ${wait_time}"
  exit 1
fi

# Check for valid JSON response with choices
if echo "$resp" | grep -q '"choices"'; then
  echo "GATEWAY_OK: chat completions working"
  exit 0
fi

echo "GATEWAY_UNKNOWN: unexpected response: $(echo "$resp" | head -c 200)"
exit 1
