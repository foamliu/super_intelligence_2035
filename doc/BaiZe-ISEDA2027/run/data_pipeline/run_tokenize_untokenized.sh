#!/bin/bash
# run_tokenize_untokenized.sh — 2026-10-25 运维令 §②
# tokenize 4 untokenized sources (ufw_en / l1_en_hq / ufw_zh / UltraX-AICC).
# Phase A: 4-tier calibration (64/96/128/192 CONCURRENT serial shards),
#          throughput = .bin-size growth (tokens = bytes/4, int32).
#          (parallel --num-workers unstable at high W here; serial+concurrent
#           is the proven env14/fullsource model.)
# Phase B: serial + MAX_CONCURRENT=knee, ~64 parquet/shard, symlink staging,
#          resume + failed_shards.txt + manifest + periodic report. 224核 nice=10.
# Launch: setsid bash <this> > /tmp/tokenize_untokenized_$(date +%s).log 2>&1 &
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SERIAL=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
STAGING_BASE=$OUT_DIR/staging_untokenized
CALIB_OUT=$OUT_DIR/calib
LOG_DIR=$OUT_DIR/logs/untokenized
MANIFEST=$OUT_DIR/untokenized_manifest.tsv
FAILED=$OUT_DIR/untokenized_failed_shards.txt
NICE=10
PARQUET_PER_SHARD=${PARQUET_PER_SHARD:-64}
TIERS=${TIERS:-"64 96 128 192"}
RESCAN=${RESCAN:-120}

EN_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en
L1_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq
ZH_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_zh
AICC_DIR=/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/UltraX-AICC
SOURCES=(
  "ufw_en|${EN_DIR}|ufw_en_train_s|content"
  "ufw_l1_en_hq|${L1_DIR}|ufw_l1_en_hq_train_s|content"
  "ufw_zh|${ZH_DIR}|ufw_zh_train_s|content"
  "ultrax_aicc|${AICC_DIR}|ultrax_aicc_train_s|cleaned_content"
)
mkdir -p "$OUT_DIR" "$LOG_DIR" "$STAGING_BASE" "$CALIB_OUT"
exec 9>/tmp/tokenize_untokenized.lock
if ! flock -n 9; then echo "[$(date '+%F %T')] lock held; exit"; exit 1; fi
count_running() { pgrep -cf 'preprocess_data_cm[.]py' 2>/dev/null || echo 0; }
is_done() { local p="$1"; [ -s "${p}.bin" ] && [ -s "${p}.idx" ] && [ -s "${p}.json" ]; }
shard_tokens() { local jf="$1"; [ -s "$jf" ] || { echo 0; return; }; "$PY" -c "import json;print(int(json.load(open('$jf')).get('num_tokens',0)))" 2>/dev/null || echo 0; }
kill_pat() { ps -eo pid,comm,args 2>/dev/null | awk -v p="$1" '$2=="python3.10" && $0 ~ p {print $1}' | xargs -r kill -9 2>/dev/null; }

# ===== Phase A: calibration (serial + concurrent shards, .bin-growth) =====
if [ -z "${KNEE:-}" ]; then
echo "=== PHASE A: CALIBRATION START $(date '+%F %T') ==="
echo "tiers=$TIERS nice=$NICE nproc=$(nproc) model=serial+concurrent measure=.bin-growth"
rm -rf "$STAGING_BASE"/calib_s* 2>/dev/null
mapfile -t CALIB_FILES < <(find "$EN_DIR" -maxdepth 1 -name '*.parquet' 2>/dev/null | sort | head -256)
NCALIB=${#CALIB_FILES[@]}
echo "calib single-parquet shard dirs: $NCALIB"
for ((i=0; i<NCALIB; i++)); do
  sd="$STAGING_BASE/calib_s${i}"; rm -rf "$sd"; mkdir -p "$sd"
  ln -sf "${CALIB_FILES[$i]}" "$sd/$(basename "${CALIB_FILES[$i]}")"
done
CALIB_TBL="$LOG_DIR/calib_table.tsv"
printf 'W\ttokens_per_s\tcpu_pct\tgain_pct\n' > "$CALIB_TBL"
prev_tps=0
for W in $TIERS; do
  if [ "$W" -gt "$NCALIB" ]; then echo "[$(date '+%F %T')] TIER W=$W skipped (only $NCALIB shards)"; continue; fi
  kill_pat "calib_w${W}" 2>/dev/null
  rm -f "$CALIB_OUT"/calib_w${W}_s*.bin "$CALIB_OUT"/calib_w${W}_s*.idx "$CALIB_OUT"/calib_w${W}_s*.json 2>/dev/null
  rm -rf /tmp/calib_tok_w${W}_s* 2>/dev/null
  echo "[$(date '+%F %T')] TIER W=$W launching $W serial shard procs (nice -n $NICE) ..."
  for ((i=0; i<W; i++)); do
    sd="$STAGING_BASE/calib_s${i}"; outp="$CALIB_OUT/calib_w${W}_s${i}"
    tokout="/tmp/calib_tok_w${W}_s${i}"; logf="$LOG_DIR/calib_w${W}_s${i}.log"; : > "$logf"
    nice -n "$NICE" "$PY" "$SERIAL" --input-dir "$sd" --output-prefix "$outp" \
      --tokenizer "$TOKENIZER" --tokenizer-output-dir "$tokout" \
      --mode content --text-column content --dtype int32 --max-chars 50000 > "$logf" 2>&1 &
  done
  sleep 45
  S1=0; for ((i=0; i<W; i++)); do b=$(stat -c %s "$CALIB_OUT/calib_w${W}_s${i}.bin" 2>/dev/null || echo 0); S1=$((S1+b)); done
  sleep 30
  S2=0; for ((i=0; i<W; i++)); do b=$(stat -c %s "$CALIB_OUT/calib_w${W}_s${i}.bin" 2>/dev/null || echo 0); S2=$((S2+b)); done
  cpu=$(ps -eo pcpu,args 2>/dev/null | awk -v p="calib_w${W}" '$0 ~ p {s+=$1} END{print int(s+0)}')
  kill_pat "calib_w${W}"; sleep 3
  db=$((S2 - S1)); [ "$db" -lt 0 ] && db=0
  tps=$(( db / 4 / 30 ))
  if [ "$prev_tps" -gt 0 ] && [ "$tps" -gt 0 ]; then gain=$(awk -v c="$tps" -v p="$prev_tps" 'BEGIN{printf "%.0f",(c-p)*100/p}'); else gain="na"; fi
  echo "[$(date '+%F %T')] TIER W=$W: tokens/s=$tps (delta=$db B/30s) cpu=${cpu}% gain=${gain}%"
  printf '%s\t%s\t%s\t%s\n' "$W" "$tps" "$cpu" "$gain" >> "$CALIB_TBL"
  prev_tps=$tps
  rm -f "$CALIB_OUT"/calib_w${W}_s*.bin "$CALIB_OUT"/calib_w${W}_s*.idx "$CALIB_OUT"/calib_w${W}_s*.json 2>/dev/null
  rm -rf /tmp/calib_tok_w${W}_s* 2>/dev/null
  sleep 5
done
echo "=== CALIBRATION TABLE ==="; cat "$CALIB_TBL"
knee=$("$PY" - "$CALIB_TBL" <<'PY'
import sys
rows=[]
for line in open(sys.argv[1]):
    line=line.strip()
    if not line or line.startswith('W'): continue
    w,tps,cpu,gain=line.split('\t'); rows.append((int(w),int(tps),int(cpu),gain))
if not rows: print(96); sys.exit()
knee=rows[0][0]
for i in range(1,len(rows)):
    g=rows[i][3]
    try: gv=int(g)
    except: gv=0
    if gv>15: knee=rows[i][0]
    else: break
print(knee)
PY
)
echo "[$(date '+%F %T')] KNEE (chosen MAX_CONCURRENT) = $knee"
echo "=== PHASE A: CALIBRATION END $(date '+%F %T') ==="
else
  knee=$KNEE
  echo "[$(date '+%F %T')] KNEE preset via env (skip calibration): $knee"
fi

# ===== Phase B: real run (serial + MAX_CONCURRENT=knee concurrent shards) =====
MAX_CONCURRENT=${MAX_CONCURRENT:-$knee}
echo ""
echo "=== PHASE B: REAL TOKENIZATION START $(date '+%F %T') ==="
echo "MAX_CONCURRENT=$MAX_CONCURRENT parquet_per_shard=$PARQUET_PER_SHARD nice=$NICE"
[ -f "$MANIFEST" ] || printf '#source\tshard\ttokens\tbin_bytes\tstatus\n' > "$MANIFEST"
: > "$FAILED"
PLAN=$STAGING_BASE/plan.tsv; : > "$PLAN"
for src in "${SOURCES[@]}"; do
  IFS='|' read -r name input_dir prefix tcol <<< "$src"
  all_parquet=$(find "$input_dir" -type f -name '*.parquet' 2>/dev/null | sort)
  total=$(echo "$all_parquet" | grep -c '.')
  [ "$total" -eq 0 ] && { echo "[$name] WARN: no parquet in $input_dir; skip"; continue; }
  nshards=$(( (total + PARQUET_PER_SHARD - 1) / PARQUET_PER_SHARD ))
  mapfile -t files <<< "$all_parquet"
  echo "[$name] $total parquet -> $nshards shards (~$PARQUET_PER_SHARD/shard), prefix=$prefix"
  for ((s=0; s<nshards; s++)); do
    start=$((s * PARQUET_PER_SHARD)); end=$((start + PARQUET_PER_SHARD))
    [ "$end" -gt "$total" ] && end=$total
    [ "$start" -ge "$total" ] && continue
    stage="${STAGING_BASE}/${name}_s${s}"; outp="${OUT_DIR}/${prefix}${s}"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$s" "$stage" "$outp" "$((end-start))" "$tcol" >> "$PLAN"
    rm -rf "$stage"; mkdir -p "$stage"
    for ((i=start; i<end; i++)); do ln -sf "${files[$i]}" "$stage/$(basename "${files[$i]}")"; done
  done
done
TOTAL_SHARDS=$(grep -c '.' "$PLAN")
echo "[$(date '+%F %T')] total shards planned: $TOTAL_SHARDS"

run_start=$(date +%s)
while true; do
  done_n=0; running_n=0; pending_n=0; giveup_n=0; total_tokens=0; total_bin_bytes=0
  while IFS=$'\t' read -r name s stage outp pcnt tcol; do
    [ -z "$name" ] && continue
    if is_done "$outp"; then
      done_n=$((done_n + 1))
      tok=$(shard_tokens "${outp}.json"); bin=$(stat -c %s "${outp}.bin" 2>/dev/null || echo 0)
      total_tokens=$((total_tokens + tok)); total_bin_bytes=$((total_bin_bytes + bin))
    elif { pgrep -af 'preprocess_data_cm[.]py' 2>/dev/null || true; } | grep -qF "$outp"; then
      running_n=$((running_n + 1))
    else
      att=$(cat "${stage}.attempts" 2>/dev/null || echo 0)
      if [ "$att" -ge 3 ]; then giveup_n=$((giveup_n + 1)); else pending_n=$((pending_n + 1)); fi
    fi
  done < "$PLAN"
  elapsed=$(( $(date +%s) - run_start ))
  cpu_now=$(ps -eo pcpu,args 2>/dev/null | awk '/preprocess_data_cm[.]py/ && !/awk/ {s+=$1} END{print int(s+0)}')
  if [ "$done_n" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
    tps=$(( total_tokens / elapsed )); remain=$(( TOTAL_SHARDS - done_n )); eta_s=$(( remain * elapsed / done_n ))
  else tps=0; eta_s=0; fi
  echo "[$(date '+%F %T')] done=$done_n/$TOTAL_SHARDS running=$running_n pending=$pending_n giveup=$giveup_n tokens=$total_tokens bin_bytes=$total_bin_bytes | tokens/s=$tps cpu=${cpu_now}% ETA=${eta_s}s"
  if [ "$running_n" -eq 0 ] && [ "$pending_n" -eq 0 ]; then echo "=== RUN COMPLETE $(date '+%F %T') done=$done_n giveup=$giveup_n ==="; break; fi
  while IFS=$'\t' read -r name s stage outp pcnt tcol; do
    [ -z "$name" ] && continue
    is_done "$outp" && continue
    { pgrep -af 'preprocess_data_cm[.]py' 2>/dev/null || true; } | grep -qF "$outp" && continue
    attf="${stage}.attempts"; att=$(cat "$attf" 2>/dev/null || echo 0)
    if [ "$att" -ge 3 ]; then
      grep -qF "${name} s${s}" "$FAILED" 2>/dev/null || echo "[$(date '+%F %T')] GIVEUP $name s$s (attempts=$att, bad shard)" >> "$FAILED"
      continue
    fi
    if [ "$(count_running)" -ge "$MAX_CONCURRENT" ]; then continue; fi
    logf="$LOG_DIR/${name}_s${s}.log"
    echo "[$(date '+%F %T')] LAUNCH $name s$s ($pcnt parquet col=$tcol att=$((att+1))) -> ${outp##*/} (running=$(count_running))"
    echo $((att+1)) > "$attf"
    nice -n "$NICE" "$PY" "$SERIAL" --input-dir "$stage" --output-prefix "$outp" \
      --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
      --mode content --text-column "$tcol" --dtype int32 --max-chars 50000 > "$logf" 2>&1 &
    sleep 2
  done < "$PLAN"
  sleep "$RESCAN"
done

echo "=== FINAL SUMMARY $(date '+%F %T') ==="
done_n=0; fail_n=0; total_tokens=0; total_bin_bytes=0
while IFS=$'\t' read -r name s stage outp pcnt tcol; do
  [ -z "$name" ] && continue
  if is_done "$outp"; then
    done_n=$((done_n + 1))
    tok=$(shard_tokens "${outp}.json"); bin=$(stat -c %s "${outp}.bin" 2>/dev/null || echo 0)
    total_tokens=$((total_tokens + tok)); total_bin_bytes=$((total_bin_bytes + bin))
    printf '%s\t%s\t%d\t%d\tOK\n' "$name" "${outp##*/}" "$tok" "$bin" >> "$MANIFEST"
  else
    fail_n=$((fail_n + 1))
    grep -qF "${name} s${s}" "$FAILED" 2>/dev/null || echo "[$(date '+%F %T')] INCOMPLETE $name s$s (not is_done at end)" >> "$FAILED"
    printf '%s\t%s\t%d\t%d\tFAIL\n' "$name" "${outp##*/}" 0 0 >> "$MANIFEST"
  fi
done < "$PLAN"
echo "done=$done_n/$TOTAL_SHARDS failed=$fail_n total_tokens=$total_tokens total_bin_bytes=$total_bin_bytes"
echo "failed_shards: $(grep -c '.' "$FAILED" 2>/dev/null || echo 0)"
echo "manifest: $MANIFEST"; echo "failed: $FAILED"
echo "=== PHASE B: REAL TOKENIZATION END $(date '+%F %T') ==="
