#!/usr/bin/env bash
# download_longctx_gated.sh — BaiZe 长上下文(A类) gated 数据下载
# 运维令 2026-11-04 09:2x：yuyijiong/LongData-Corpus (36G, gated:auto, 用户 token 授权)
# 纪律：在 .29 上跑（real token 在 .29 ~/.cache/huggingface/token）；setsid 后台 + /tmp 日志；
#        🚫 不占 GPU；nice -n 10；并发 ≤4；HF_HUB_ENABLE_HF_TRANSFER=0（给训练留带宽）；断点续传。
# 幂等：可重复运行；已下完的会被跳过。
set -uo pipefail

PROXY="http://172.19.92.25:13128"
export https_proxy="$PROXY" http_proxy="$PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0
NICE="nice -n 10"
MAX_WORKERS=4
BASE="/nas_inference/app.e0031982/datasets"
STATUS_TSV="/tmp/data_download_lc_gated_status.tsv"
RUN_TS="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="/tmp/data_download_lc_gated_${RUN_TS}.log"

REPO="yuyijiong/LongData-Corpus"
ORG="yuyijiong"
NAME="LongData-Corpus"
LDIR="$BASE/$ORG/$NAME"

echo "==== gated longctx download start $RUN_TS ====" | tee -a "$MASTER_LOG"
echo "proxy=$PROXY  hf_transfer=0  max_workers=$MAX_WORKERS  repo=$REPO  ldir=$LDIR" | tee -a "$MASTER_LOG"
echo -e "repo_id\tlocal_dir\tstatus\tfiles\tbytes\tattempts\tts" > "$STATUS_TSV"

mkdir -p "$LDIR"
attempt=0 ok=0 status="FAIL"
for attempt in 1 2 3; do
  echo "[attempt $attempt] hf download $REPO --repo-type dataset --local-dir $LDIR --max-workers $MAX_WORKERS" | tee -a "$MASTER_LOG"
  if $NICE hf download "$REPO" --repo-type dataset --local-dir "$LDIR" --max-workers "$MAX_WORKERS" >> "$MASTER_LOG" 2>&1; then
    ok=1; status="OK"; break
  else
    echo "[attempt $attempt] FAILED (tail):" | tee -a "$MASTER_LOG"; tail -5 "$MASTER_LOG" | tee -a "$MASTER_LOG"
    sleep 10
  fi
done

files="$(find "$LDIR" -type f ! -name '.gitattributes' 2>/dev/null | wc -l)"
bytes="$(find "$LDIR" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END{print s+0}')"
inc="$(find "$LDIR" -name '*.incomplete' 2>/dev/null | wc -l)"
[ "$inc" -gt 0 ] && status="INCOMPLETE($inc)"
gb="$(awk "BEGIN{printf \"%.2f\", $bytes/1073741824}")"
echo "[$REPO] status=$status files=$files bytes=$bytes(${gb}GiB) incomplete=$inc attempts=$attempt" | tee -a "$MASTER_LOG"
echo -e "$REPO\t$LDIR\t$status\t$files\t$bytes\t$attempt\t$(date +%s)" >> "$STATUS_TSV"
echo "==== gated longctx download FINISH $(date +%H:%M:%S) ====" | tee -a "$MASTER_LOG"
echo "MASTER_LOG=$MASTER_LOG  STATUS=$STATUS_TSV" | tee -a "$MASTER_LOG"
