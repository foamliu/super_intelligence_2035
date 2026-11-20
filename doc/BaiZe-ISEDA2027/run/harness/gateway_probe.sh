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
# R2072 fix: capture HTTP status code separately — bare grep '429' on the body
# false-matches JSON response IDs that happen to contain "429" as a substring
# (e.g. "b75b614022284291a9cdcc3296307115").  Now we check the *HTTP status*
# for 429, and only grep the body for explicit error strings.
resp_with_rc=$(curl -s -m 15 -w '\n%{http_code}' "$GW/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY" \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  2>/dev/null || echo -e "CURL_FAILED\n000")

# Split body and HTTP status code (last line)
chat_rc=$(echo "$resp_with_rc" | tail -1)
resp=$(echo "$resp_with_rc" | sed '$d')

if [[ "$VERBOSE" == "1" ]]; then
  echo "[probe] /v1/chat/completions → HTTP $chat_rc, body: $(echo "$resp" | head -c 200)"
fi

# Check for CURL failure
if [[ "$resp" == "CURL_FAILED" || "$chat_rc" == "000" ]]; then
  echo "GATEWAY_DOWN: chat completions curl failed (rc=$chat_rc)"
  exit 1
fi

# Check for quota exhaustion: HTTP 429 status OR explicit error strings in body
if [[ "$chat_rc" == "429" ]] || echo "$resp" | grep -qE '额度已用完|rate.limit|Rate.Limit|Too Many|quota'; then
  # Extract wait time if present
  wait_time=$(echo "$resp" | grep -oP '等待\K[0-9]+分钟[0-9]+秒' || echo "unknown")
  echo "GATEWAY_QUOTA_EXHAUSTED: chat completions blocked (HTTP $chat_rc). Wait: ${wait_time}"
  exit 1
fi

# Check for auth failure
if [[ "$chat_rc" == "401" || "$chat_rc" == "403" ]]; then
  echo "GATEWAY_AUTH_FAIL: chat completions returned HTTP $chat_rc"
  exit 1
fi

# Check for valid JSON response with choices (HTTP 200)
if [[ "$chat_rc" == "200" ]] && echo "$resp" | grep -q '"choices"'; then
  echo "GATEWAY_OK: chat completions working (HTTP 200)"
  exit 0
fi

echo "GATEWAY_UNKNOWN: unexpected response (HTTP $chat_rc): $(echo "$resp" | head -c 200)"
exit 1
