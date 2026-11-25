#!/usr/bin/env bash
# download_longctx_datasets.sh — BaiZe 长上下文(A类)数据下载
# 运维令 2026-11-04 09:2x（用户直令 · 最高优先）：批准下载长上下文数据，落盘 /nas_inference
# 纪律：setsid 后台 + /tmp 日志；🚫 不占 GPU；nice -n 10；并发 ≤4（--max-workers 4）；
#        限带宽（HF_HUB_ENABLE_HF_TRANSFER=0，避免 hf_transfer 激进多分片）；断点续传（hf download 自动跳过已存在文件）。
# 幂等：可重复运行；已下完的会被跳过。
set -uo pipefail

PROXY="http://172.19.92.25:13128"
export https_proxy="$PROXY" http_proxy="$PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0   # 关闭激进传输，给训练留带宽
NICE="nice -n 10"
MAX_WORKERS=4
BASE="/nas_inference/app.e0031982/datasets"
STATUS_TSV="/tmp/data_download_lc_status.tsv"
LOG_DIR="/tmp"
RUN_TS="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="${LOG_DIR}/data_download_lc_${RUN_TS}.log"

# repo_id|note  （local-dir = $BASE/<org>/<name>）
TARGETS=(
  "ysngkil/whole-books|书籍长文"
  "princeton-nlp/prolong-data-512K|prolong 512K 训练数据"
  "openbmb/InfLLM-V2-data-5B|InfLLM-V2 5B 训练数据"
  "self-long/RULER-llama3-1M|RULER 1M 评测/合成 haystack"
  "caskcsg/NExtLong-128K-dataset|NExtLong 128K（原 id caskcsg/NExtLong 401 私有，改用公开 128K 变体）"
  "THUDM/LongAlign-10k|LongAlign 10k 长对齐"
  "birgermoell/oellm-longctx-tokenized-natural-128k-256k-pilot-v1|oellm 长上下文 pilot-v1"
  "deepmind/pg19|PG-19 古登堡长文"
  "ghostcc3/mix-context-post-training-128k|mix-context 128k 后训练"
)

echo "==== longctx download start $RUN_TS ====" | tee -a "$MASTER_LOG"
echo "proxy=$PROXY  hf_transfer=0  max_workers=$MAX_WORKERS  base=$BASE" | tee -a "$MASTER_LOG"
echo -e "repo_id\tlocal_dir\tnote\tstatus\tfiles\tbytes\tattempts\tts" > "$STATUS_TSV"

download_one() {
  local entry="$1"
  local repo="${entry%%|*}"
  local note="${entry##*|}"
  local org="${repo%%/*}"
  local name="${repo#*/}"
  local ldir="$BASE/$org/$name"
  local perlog="${LOG_DIR}/data_download_${org}__${name}_${RUN_TS}.log"
  mkdir -p "$ldir"
  echo "---- [$repo] -> $ldir  ($note) ----" | tee -a "$MASTER_LOG"
  local attempt=0 ok=0 status="FAIL"
  for attempt in 1 2 3; do
    echo "[attempt $attempt] hf download $repo --repo-type dataset --local-dir $ldir --max-workers $MAX_WORKERS" | tee -a "$MASTER_LOG"
    if $NICE hf download "$repo" --repo-type dataset --local-dir "$ldir" --max-workers "$MAX_WORKERS" >> "$perlog" 2>&1; then
      ok=1; status="OK"; break
    else
      echo "[attempt $attempt] FAILED (see $perlog tail):" | tee -a "$MASTER_LOG"; tail -3 "$perlog" | tee -a "$MASTER_LOG"
      sleep 10
    fi
  done
  # 校验：统计文件数 + 字节 + 残留 .incomplete
  local files bytes inc
  files="$(find "$ldir" -type f ! -name '.gitattributes' 2>/dev/null | wc -l)"
  bytes="$(find "$ldir" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END{print s+0}')"
  inc="$(find "$ldir" -name '*.incomplete' 2>/dev/null | wc -l)"
  [ "$inc" -gt 0 ] && status="INCOMPLETE($inc)"
  local gb; gb="$(awk "BEGIN{printf \"%.2f\", $bytes/1073741824}")"
  echo "[$repo] status=$status files=$files bytes=$bytes(${gb}GiB) incomplete=$inc attempts=$attempt" | tee -a "$MASTER_LOG"
  echo -e "$repo\t$ldir\t$note\t$status\t$files\t$bytes\t$attempt\t$(date +%s)" >> "$STATUS_TSV"
}

for t in "${TARGETS[@]}"; do
  download_one "$t"
done

echo "==== longctx download FINISH $(date +%H:%M:%S) ====" | tee -a "$MASTER_LOG"
echo "--- status summary ---" | tee -a "$MASTER_LOG"
column -t -s $'\t' "$STATUS_TSV" | tee -a "$MASTER_LOG"
echo "MASTER_LOG=$MASTER_LOG  STATUS=$STATUS_TSV" | tee -a "$MASTER_LOG"
