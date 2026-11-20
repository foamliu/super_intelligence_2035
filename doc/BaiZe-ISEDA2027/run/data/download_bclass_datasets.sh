#!/usr/bin/env bash
# download_bclass_datasets.sh — BaiZe B类 agentic 数据下载
# 运维令 2026-11-04 13:2x（用户直令 · 最高优先）：放行 B 类 agentic 数据下载，落盘 /nas_inference
# 纪律：setsid 后台 + /tmp 日志；🚫 不占 GPU；nice -n 10；并发 ≤4（--max-workers 4）；
#        限带宽（HF_HUB_ENABLE_HF_TRANSFER=0）；断点续传（hf download 自动跳过已存在文件）。
# 幂等：可重复运行；已下完的会被跳过。
set -uo pipefail

PROXY="http://172.19.92.25:13128"
export https_proxy="$PROXY" http_proxy="$PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0
NICE="nice -n 10"
MAX_WORKERS=4
BASE="/nas_inference/app.e0031982/datasets"
STATUS_TSV="/tmp/data_download_bclass_status.tsv"
LOG_DIR="/tmp"
RUN_TS="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="${LOG_DIR}/data_download_bclass_${RUN_TS}.log"

# repo_id|note  （local-dir = $BASE/<org>/<name>）
# P0-P3 per 运维令 13:2x; zhangdw/to-tool-call-datasets 已在盘(2.2G/37f/0inc) 仍列以校验
TARGETS=(
  "SWE-bench/SWE-smith|P0 SWE-smith MIT"
  "nvidia/Nemotron-Terminal-Corpus|P0 Nemotron-Terminal CC BY 4.0"
  "nebius/SWE-rebench|P0 SWE-rebench"
  "zhangdw/to-tool-call-datasets|P1 to-tool-call(已在盘校验)"
  "tuandunghcmut/toolbench-v1|P1 toolbench-v1 Apache-2.0"
  "open-thoughts/AgentTrove|P2 AgentTrove"
  "microsoft/Orchard|P2 Orchard MIT"
  "nvidia/Nemotron-Cascade-RL-SWE|P2 Nemotron-Cascade-RL-SWE"
  "nvidia/Nemotron-Cascade-SFT-SWE|P2 Nemotron-Cascade-SFT-SWE CC BY 4.0"
  "SWE-bench/SWE-smith-trajectories|P2 SWE-smith-trajectories"
  "mshojaei77/terminal-command-execution-sft|P3 terminal-cmd-exec-sft"
  "ia03/terminal-bench|P3 terminal-bench 评测集仅去污染"
)

echo "==== bclass download start $RUN_TS ====" | tee -a "$MASTER_LOG"
echo "proxy=$PROXY  hf_transfer=0  max_workers=$MAX_WORKERS  base=$BASE" | tee -a "$MASTER_LOG"
echo -e "repo_id\tlocal_dir\tnote\tstatus\tfiles\tbytes\tattempts\tts" > "$STATUS_TSV"

download_one() {
  local entry="$1"
  local repo="${entry%%|*}"
  local note="${entry##*|}"
  local org="${repo%%/*}"
  local name="${repo#*/}"
  local ldir="$BASE/$org/$name"
  local perlog="${LOG_DIR}/data_download_bclass_${org}__${name}_${RUN_TS}.log"
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

echo "==== bclass download FINISH $(date +%H:%M:%S) ====" | tee -a "$MASTER_LOG"
echo "--- status summary ---" | tee -a "$MASTER_LOG"
column -t -s $'\t' "$STATUS_TSV" | tee -a "$MASTER_LOG"
echo "MASTER_LOG=$MASTER_LOG  STATUS=$STATUS_TSV" | tee -a "$MASTER_LOG"
