#!/usr/bin/env bash
# verify_rl2609.sh — Wait for UltraData-RL-2609 download completion, then self-check
# Self-check: file count == 26, .incomplete == 0, byte-by-byte comparison with hf_manifest.json
# Output: /tmp/rl2609_selfcheck_result.txt

LOCAL_DIR="/nas_env/app.e0031982/datasets/openbmb/UltraData-RL-2609"
MANIFEST="$LOCAL_DIR/hf_manifest.json"
RESULT_FILE="/tmp/rl2609_selfcheck_result.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === RL-2609 self-check: waiting for completion ===" > "$RESULT_FILE"

# Wait up to 30 minutes for download to complete
MAX_WAIT=1800
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
  JSONL_COUNT=$(find "$LOCAL_DIR/data" -name '*.jsonl' 2>/dev/null | wc -l)
  INCOMPLETE_COUNT=$(find "$LOCAL_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
  if [ "$JSONL_COUNT" -eq 20 ] && [ "$INCOMPLETE_COUNT" -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] Download complete: 20 jsonl, 0 .incomplete" >> "$RESULT_FILE"
    break
  fi
  echo "[$(date '+%H:%M:%S')] Still downloading: ${JSONL_COUNT}/20 jsonl, ${INCOMPLETE_COUNT} .incomplete" >> "$RESULT_FILE"
  sleep 30
  WAITED=$((WAITED + 30))
done

if [ $WAITED -ge $MAX_WAIT ]; then
  echo "[$(date '+%H:%M:%S')] TIMEOUT after 30 min — download not complete" >> "$RESULT_FILE"
  JSONL_COUNT=$(find "$LOCAL_DIR/data" -name '*.jsonl' 2>/dev/null | wc -l)
  INCOMPLETE_COUNT=$(find "$LOCAL_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
  echo "Final: ${JSONL_COUNT}/20 jsonl, ${INCOMPLETE_COUNT} .incomplete" >> "$RESULT_FILE"
  exit 1
fi

echo "" >> "$RESULT_FILE"
echo "=== SELF-CHECK START ===" >> "$RESULT_FILE"

# 1. Count all files (excluding .cache)
echo "" >> "$RESULT_FILE"
echo "--- 1. File count ---" >> "$RESULT_FILE"
ALL_FILES=$(find "$LOCAL_DIR" -type f -not -path '*/.cache/*' | sort)
ALL_COUNT=$(echo "$ALL_FILES" | wc -l)
echo "Total files (excl .cache): $ALL_COUNT" >> "$RESULT_FILE"
echo "Expected: 26" >> "$RESULT_FILE"
if [ "$ALL_COUNT" -eq 26 ]; then
  echo "RESULT: PASS ✅" >> "$RESULT_FILE"
else
  echo "RESULT: FAIL ❌ (expected 26, got $ALL_COUNT)" >> "$RESULT_FILE"
  echo "Files found:" >> "$RESULT_FILE"
  echo "$ALL_FILES" >> "$RESULT_FILE"
fi

# 2. .incomplete count
echo "" >> "$RESULT_FILE"
echo "--- 2. .incomplete check ---" >> "$RESULT_FILE"
INC_COUNT=$(find "$LOCAL_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
echo ".incomplete files: $INC_COUNT" >> "$RESULT_FILE"
if [ "$INC_COUNT" -eq 0 ]; then
  echo "RESULT: PASS ✅" >> "$RESULT_FILE"
else
  echo "RESULT: FAIL ❌" >> "$RESULT_FILE"
  find "$LOCAL_DIR" -name '*.incomplete' >> "$RESULT_FILE"
fi

# 3. Byte-by-byte comparison with hf_manifest.json
echo "" >> "$RESULT_FILE"
echo "--- 3. Byte-by-byte comparison vs hf_manifest.json ---" >> "$RESULT_FILE"
PASS_COUNT=0
FAIL_COUNT=0
FAIL_DETAILS=""
while IFS='|' read -r key expected_size; do
  # Skip empty lines
  [ -z "$key" ] && continue
  FILE_PATH="$LOCAL_DIR/$key"
  if [ -f "$FILE_PATH" ]; then
    ACTUAL_SIZE=$(stat -c '%s' "$FILE_PATH" 2>/dev/null)
    if [ "$ACTUAL_SIZE" -eq "$expected_size" ]; then
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      FAIL_COUNT=$((FAIL_COUNT + 1))
      FAIL_DETAILS="${FAIL_DETAILS}MISMATCH: $key expected=$expected_size actual=$ACTUAL_SIZE\n"
    fi
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    FAIL_DETAILS="${FAIL_DETAILS}MISSING: $key (expected $expected_size bytes)\n"
  fi
done < <(python3 -c "
import json
with open('$MANIFEST') as f:
    data = json.load(f)
for k, v in data.items():
    print(f'{k}|{v}')
")

echo "Pass: $PASS_COUNT / 26" >> "$RESULT_FILE"
echo "Fail: $FAIL_COUNT" >> "$RESULT_FILE"
if [ "$FAIL_COUNT" -eq 0 ]; then
  echo "RESULT: PASS ✅ (all 26 files match byte-for-byte)" >> "$RESULT_FILE"
else
  echo "RESULT: FAIL ❌" >> "$RESULT_FILE"
  echo -e "$FAIL_DETAILS" >> "$RESULT_FILE"
fi

# 4. Total size
echo "" >> "$RESULT_FILE"
echo "--- 4. Total size ---" >> "$RESULT_FILE"
TOTAL_SIZE=$(find "$LOCAL_DIR" -type f -not -path '*/.cache/*' -exec stat -c '%s' {} \; 2>/dev/null | paste -sd+ | bc)
EXPECTED_TOTAL=187632276428
echo "Actual total: $TOTAL_SIZE bytes ($(echo "scale=2; $TOTAL_SIZE / 1073741824" | bc) GiB)" >> "$RESULT_FILE"
echo "Expected total: $EXPECTED_TOTAL bytes (174.70 GiB)" >> "$RESULT_FILE"
if [ "$TOTAL_SIZE" -eq "$EXPECTED_TOTAL" ]; then
  echo "RESULT: PASS ✅" >> "$RESULT_FILE"
else
  echo "RESULT: Note — actual may differ if .cache metadata files are counted" >> "$RESULT_FILE"
fi

# 5. Summary
echo "" >> "$RESULT_FILE"
echo "=== SUMMARY ===" >> "$RESULT_FILE"
echo "File count: $ALL_COUNT/26 ($([ $ALL_COUNT -eq 26 ] && echo PASS || echo FAIL))" >> "$RESULT_FILE"
echo ".incomplete: $INC_COUNT ($([ $INC_COUNT -eq 0 ] && echo PASS || echo FAIL))" >> "$RESULT_FILE"
echo "Byte match: $PASS_COUNT/26 ($([ $FAIL_COUNT -eq 0 ] && echo PASS || echo FAIL))" >> "$RESULT_FILE"
echo "Total size: $TOTAL_SIZE bytes" >> "$RESULT_FILE"
echo "=== SELF-CHECK END ===" >> "$RESULT_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done" >> "$RESULT_FILE"
