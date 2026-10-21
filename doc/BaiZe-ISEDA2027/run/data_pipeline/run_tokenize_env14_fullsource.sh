#!/bin/bash
# run_tokenize_env14_fullsource.sh
# Full-source tokenization of en_v1_4: tokenize EVERY CC-MAIN-* snapshot (110),
# not a 500B/1.5T token-budget slice.
# Policy (2026-10-18 user): "if we tokenize, tokenize a whole data source".
# Launch:
#   setsid -f nohup bash run_tokenize_env14_fullsource.sh \
#     > /tmp/run_tokenize_env14_fullsource.log 2>&1 &
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
EN_V14_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs
MANIFEST="$OUT_DIR/env14_fullsource_manifest.tsv"
SUMMARY="$OUT_DIR/env14_fullsource_summary.json"

EXPECTED_SHARDS=110
# 2026-10-18 user: tokenization may use 32 or 64 cores.
# Default 32; override with MAX_CONCURRENT=64 after checking RAM/NFS headroom.
MAX_CONCURRENT=${MAX_CONCURRENT:-32}
NICE=19
RESCAN=600

mkdir -p "$OUT_DIR" "$LOG_DIR"

exec 9>/tmp/env14_fullsource.lock
if ! flock -n 9; then
  echo "another run_tokenize_env14_fullsource.sh instance holds the lock; exit"
  exit 1
fi

# NOTE: anchor on '^bash ' so we only match an actual bash launcher of the
# resume script, NOT this agent's own cline process (whose cmdline contains
# the task-book text mentioning 'run_tokenize_env14_resume.sh').
while pgrep -f '^bash .*run_tokenize_env14_resume[.]sh' >/dev/null 2>&1; do
  echo "[$(date '+%F %T')] waiting for run_tokenize_env14_resume.sh ..."
  sleep 60
done

count_running() {
  # Anchor on the python interpreter path to avoid matching cline's cmdline
  # (which embeds the task-book text containing 'preprocess_data_cm.py').
  # FIX 2026-10-22: pgrep -c prints "0" AND exits 1 on no-match; `|| echo 0`
  # then prints a second "0" → "0\n0" → `[ -ge ]` integer error.
  # Fix: capture in var, default to 0 on failure.
  local n
  n=$(pgrep -cf 'miniforge3/envs/py310/bin/python3.10.*preprocess_data_cm' 2>/dev/null) || n=0
  echo "$n"
}

is_running() {
  local shard="$1"
  # FIX 2026-10-22: grep -q exits early on match → pgrep gets SIGPIPE (exit 141).
  # With `set -o pipefail`, the pipeline returns 141 (non-zero = "not running"),
  # causing the script to launch DUPLICATE processes for the same shard.
  # Fix: wrap pgrep in `{ ... || true; }` so pipefail only sees grep's exit code.
  { pgrep -af 'preprocess_data_cm[.]py' 2>/dev/null || true; } | grep -qF "$shard"
}

is_done() {
  local shard="$1"
  local p="$OUT_DIR/env14_${shard}"
  [ -s "${p}.bin" ] && [ -s "${p}.idx" ] && [ -s "${p}.json" ]
}

is_complete_shard() {
  local shard="$1"
  local d="$EN_V14_DIR/$shard"
  [ -d "$d" ] || return 1
  local n_par n_inc
  n_par=$(find "$d" -maxdepth 1 -name '*.parquet' 2>/dev/null | wc -l)
  [ "$n_par" -ge 512 ] || return 1
  n_inc=$(find "$d" -maxdepth 1 -name '*.incomplete' 2>/dev/null | wc -l)
  [ "$n_inc" -eq 0 ] || return 1
  return 0
}

shard_tokens() {
  local shard="$1"
  local jf="$OUT_DIR/env14_${shard}.json"
  [ -s "$jf" ] || { echo 0; return; }
  "$PY" - "$jf" <<'PY' 2>/dev/null || echo 0
import json, sys
try:
    print(int(json.load(open(sys.argv[1])).get("num_tokens", 0)))
except Exception:
    print(0)
PY
}

echo "=== en_v1_4 FULL-SOURCE tokenization START $(date '+%F %T') ==="
echo "expected=$EXPECTED_SHARDS max_concurrent=$MAX_CONCURRENT nice=$NICE rescan=${RESCAN}s"

while true; do
  tmp="$MANIFEST.tmp"
  : > "$tmp"
  done_n=0
  available_n=0
  pending_download_n=0
  running_n=0
  total_tokens=0
  total_bin_bytes=0

  for d in "$EN_V14_DIR"/CC-MAIN-*; do
    [ -d "$d" ] || continue
    shard=$(basename "$d")
    if is_complete_shard "$shard"; then
      available_n=$((available_n + 1))
      if is_done "$shard"; then
        done_n=$((done_n + 1))
        tok=$(shard_tokens "$shard")
        bin="$OUT_DIR/env14_${shard}.bin"
        bytes=$(stat -c %s "$bin" 2>/dev/null || echo 0)
        total_tokens=$((total_tokens + tok))
        total_bin_bytes=$((total_bin_bytes + bytes))
        printf '%s\tDONE\t%s\t%s\n' "$shard" "$tok" "$bytes" >> "$tmp"
      elif is_running "$shard"; then
        running_n=$((running_n + 1))
        printf '%s\tRUNNING\t-\t-\n' "$shard" >> "$tmp"
      else
        printf '%s\tPENDING\t-\t-\n' "$shard" >> "$tmp"
      fi
    else
      pending_download_n=$((pending_download_n + 1))
      printf '%s\tPENDING_DOWNLOAD\t-\t-\n' "$shard" >> "$tmp"
    fi
  done
  mv "$tmp" "$MANIFEST"

  echo "[$(date '+%F %T')] done=$done_n/$EXPECTED_SHARDS available=$available_n running=$running_n pending_download=$pending_download_n tokens=$total_tokens bin_bytes=$total_bin_bytes"

  if [ "$done_n" -ge "$EXPECTED_SHARDS" ]; then
    "$PY" - "$MANIFEST" "$SUMMARY" "$EXPECTED_SHARDS" "$total_tokens" "$total_bin_bytes" <<'PY'
import json, sys, datetime
manifest, out, expected, total_tokens, total_bin_bytes = sys.argv[1:6]
rows = []
for line in open(manifest, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) == 4:
        rows.append({'shard': parts[0], 'status': parts[1], 'tokens': parts[2], 'bin_bytes': parts[3]})
data = {
    'source': 'openbmb/Ultra-FineWeb data/ultrafineweb_en_v1_4',
    'expected_shards': int(expected),
    'done_shards': sum(1 for r in rows if r['status'] == 'DONE'),
    'total_tokens': int(total_tokens),
    'total_bin_bytes': int(total_bin_bytes),
    'finished_at': datetime.datetime.now().isoformat(timespec='seconds'),
    'shards': rows,
}
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('wrote', out)
PY
    echo "=== en_v1_4 FULL-SOURCE tokenization COMPLETE $(date '+%F %T') ==="
    exit 0
  fi

  for d in "$EN_V14_DIR"/CC-MAIN-*; do
    [ -d "$d" ] || continue
    shard=$(basename "$d")
    is_complete_shard "$shard" || continue
    is_done "$shard" && continue
    is_running "$shard" && continue
    while [ "$(count_running)" -ge "$MAX_CONCURRENT" ]; do
      echo "[$(date '+%F %T')] throttle: running=$(count_running) >= $MAX_CONCURRENT; wait ${RESCAN}s"
      sleep "$RESCAN"
    done
    out_prefix="$OUT_DIR/env14_${shard}"
    echo "[$(date '+%F %T')] LAUNCH $shard (running=$(count_running))"
    nice -n "$NICE" "$PY" "$SCRIPT" \
      --input-dir "$d" \
      --output-prefix "$out_prefix" \
      --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
      --mode content --text-column content --dtype int32 \
      > "$LOG_DIR/env14_${shard}.log" 2>&1 &
    sleep 5
  done

  sleep "$RESCAN"
done

