#!/bin/bash
# run_tokenize_sft.sh — 运维令 2026-10-27 13:3x（用户直令·最高优先）
# 分词 UltraData-SFT-2605 + UltraData-SFT-Agent-2609 → /nas_env，纳入映射镜像同等对待。
#
# Phase 1: JSONL → parquet（每文件一个；SFT-2605 12 子集 + Agent-2609 4 子集，子集并行）
# Phase 2: parquet → .bin/.idx/.json（size-balanced 分 shard，96 并发单核，resume+failed）
#          产物直写 /nas_env/app.e0031982/baize-data/full_sft_2605|full_sft_agent_2609
# Phase 3: finalize（清空未分词侧车 → build_tokenized_mirror.py → gen_data_mapping_md.py --measure
#          → gen_report_data_mapping_html.py → git add 本线文件 + commit + push）
#
# 启动：setsid bash run_tokenize_sft.sh > /tmp/tokenize_sft_$(date +%s).log 2>&1 &
# 续跑：安全——Phase 2 用 is_done 跳过已完成 shard；Phase 1 parquet 已在则跳过（幂等）。
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
PIPE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
DATA=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data
REPO=/nas_train/app.e0031982/code/super_intelligence_2035
CONVERT=$PIPE/convert_sft_jsonl_to_parquet.py
SERIAL=$PIPE/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/BaiZe-ISEDA2027/data/tokenizer_eod
BUILD_MIRROR=$DATA/build_tokenized_mirror.py
GEN_MD=$DATA/gen_data_mapping_md.py
GEN_REPORT=$DATA/gen_report_data_mapping_html.py

SFT2605_DATA=/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data
AGENT2609_DATA=/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609/data
TEXT_BASE=/nas_train/app.e0031982/datasets/baize-data/text
STAGING_BASE=$TEXT_BASE/staging_sft
SFT2605_PARQUET=$STAGING_BASE/parquet_sft_2605
AGENT2609_PARQUET=$STAGING_BASE/parquet_sft_agent_2609
SHARD_STAGE_SFT=$STAGING_BASE/shards_sft_2605
SHARD_STAGE_AG=$STAGING_BASE/shards_sft_agent_2609
NAS_ENV_BASE=/nas_env/app.e0031982/baize-data
SFT2605_OUT=$NAS_ENV_BASE/full_sft_2605
AGENT2609_OUT=$NAS_ENV_BASE/full_sft_agent_2609
LOG_DIR=$TEXT_BASE/logs/sft
MANIFEST=$TEXT_BASE/sft_manifest.tsv
FAILED=$TEXT_BASE/sft_failed_shards.txt
PLAN=$STAGING_BASE/shard_plan.tsv
LOCK=/tmp/tokenize_sft.lock

PPS_SFT=${PPS_SFT:-16}        # SFT-2605: 1504 parquet / 16 = 94 shard
PPS_AGENT=${PPS_AGENT:-4}     # Agent-2609: 50 parquet / 4 = 13 shard
MAX_CONCURRENT=${MAX_CONCURRENT:-96}
NICE=${NICE:-10}
RESCAN=${RESCAN:-60}
PROXY=${https_proxy:-http://172.19.92.25:13128}

mkdir -p "$SFT2605_PARQUET" "$AGENT2609_PARQUET" "$SHARD_STAGE_SFT" "$SHARD_STAGE_AG" \
         "$LOG_DIR" "$SFT2605_OUT" "$AGENT2609_OUT"
exec 9>"$LOCK"
if ! flock -n 9; then echo "[$(date '+%F %T')] lock $LOCK held; exit"; exit 1; fi

count_running() { pgrep -cf 'preprocess_data_cm[.]py' 2>/dev/null || echo 0; }
is_done() { local p="$1"; [ -s "${p}.bin" ] && [ -s "${p}.idx" ] && [ -s "${p}.json" ]; }
shard_tokens() { local jf="$1"; [ -s "$jf" ] || { echo 0; return; }; "$PY" -c "import json;print(int(json.load(open('$jf')).get('num_tokens',0)))" 2>/dev/null || echo 0; }

echo "============================================================"
echo "=== run_tokenize_sft.sh START $(date '+%F %T') ==="
echo "PPS_SFT=$PPS_SFT PPS_AGENT=$PPS_AGENT MAX_CONCURRENT=$MAX_CONCURRENT NICE=$NICE"
echo "============================================================"

# ===== Phase 1: JSONL → parquet（每文件一个；子集并行；幂等：parquet 已在则跳过该子集）=====
echo "=== PHASE 1: CONVERT START $(date '+%F %T') ==="
pids=()
# SFT-2605：data/{no_think,think}/{cat}
for think in no_think think; do
  for cat_dir in "$SFT2605_DATA/$think"/*/; do
    [ -d "$cat_dir" ] || continue
    cat=$(basename "$cat_dir"); prefix="sft2605_${think}_${cat}"
    # 幂等：该前缀已有 parquet 则跳过
    if ls "$SFT2605_PARQUET"/${prefix}_p*.parquet >/dev/null 2>&1; then
      echo "[convert] skip $prefix (parquet already present)"; continue
    fi
    echo "[convert] launch SFT-2605 $think/$cat -> $prefix"
    "$PY" "$CONVERT" --input-dir "$cat_dir" --output-dir "$SFT2605_PARQUET" \
        --prefix "$prefix" --kind sft2605 > "$LOG_DIR/convert_${prefix}.log" 2>&1 &
    pids+=($!)
  done
done
# Agent-2609：data/{cat}
for cat_dir in "$AGENT2609_DATA"/*/; do
  [ -d "$cat_dir" ] || continue
  cat=$(basename "$cat_dir"); prefix="sftagent2609_${cat}"
  if ls "$AGENT2609_PARQUET"/${prefix}_p*.parquet >/dev/null 2>&1; then
    echo "[convert] skip $prefix (parquet already present)"; continue
  fi
  echo "[convert] launch Agent-2609 $cat -> $prefix"
  "$PY" "$CONVERT" --input-dir "$cat_dir" --output-dir "$AGENT2609_PARQUET" \
      --prefix "$prefix" --kind agent2609 > "$LOG_DIR/convert_${prefix}.log" 2>&1 &
  pids+=($!)
done
cfail=0
for p in "${pids[@]}"; do wait "$p" || cfail=1; done
if [ "$cfail" -ne 0 ]; then echo "[$(date '+%F %T')] PHASE 1 CONVERT FAILED"; exit 1; fi
n_sft_parquet=$(ls "$SFT2605_PARQUET"/*.parquet 2>/dev/null | wc -l)
n_ag_parquet=$(ls "$AGENT2609_PARQUET"/*.parquet 2>/dev/null | wc -l)
echo "=== PHASE 1: CONVERT DONE $(date '+%F %T') sft2605_parquet=$n_sft_parquet agent2609_parquet=$n_ag_parquet ==="

# ===== Phase 2: parquet → .bin/.idx/.json（size-balanced 分 shard + 96 并发 + resume）=====
echo "=== PHASE 2: TOKENIZE START $(date '+%F %T') ==="
# 生成 shard_plan.tsv：size-balanced round-robin（按 parquet 字节降序，轮转分配到 n_shard）。
# 列：name shard_idx staging_dir output_prefix parquet_count text_column
"$PY" - "$SFT2605_PARQUET" "$AGENT2609_PARQUET" "$SHARD_STAGE_SFT" "$SHARD_STAGE_AG" \
        "$SFT2605_OUT" "$AGENT2609_OUT" "$PPS_SFT" "$PPS_AGENT" "$PLAN" <<'PYEOF'
import os, glob, sys
sft_pq, ag_pq, st_sft, st_ag, out_sft, out_ag, pps_sft, pps_ag, plan = sys.argv[1:10]
pps_sft=int(pps_sft); pps_ag=int(pps_ag)
def build(src_dir, stage_base, out_dir, pfx, pps, name):
    files=sorted(glob.glob(os.path.join(src_dir,"*.parquet")))
    if not files: return []
    n_shard=max(1,(len(files)+pps-1)//pps)
    sized=sorted(files,key=lambda f: os.path.getsize(f),reverse=True)
    buckets=[[] for _ in range(n_shard)]
    for i,f in enumerate(sized): buckets[i%n_shard].append(f)
    rows=[]
    for si,b in enumerate(buckets):
        sd=os.path.join(stage_base,f"s{si}"); os.makedirs(sd,exist_ok=True)
        for f in b:
            link=os.path.join(sd,os.path.basename(f))
            if os.path.islink(link) or os.path.exists(link):
                try: os.remove(link)
                except OSError: pass
            os.symlink(f,link)
        outp=os.path.join(out_dir,f"{pfx}_train_s{si}")
        rows.append((name,si,sd,outp,len(b),"content"))
    return rows
rows=[]
rows+=build(sft_pq,st_sft,out_sft,"sft2605",pps_sft,"sft2605")
rows+=build(ag_pq,st_ag,out_ag,"sftagent2609",pps_ag,"sftagent2609")
with open(plan,"w") as f:
    for r in rows: f.write("\t".join(str(x) for x in r)+"\n")
print(f"[plan] {len(rows)} shards (sft2605+agent2609) -> {plan}")
PYEOF
TOTAL_SHARDS=$(wc -l < "$PLAN")
echo "[plan] TOTAL_SHARDS=$TOTAL_SHARDS -> $PLAN"


rm -f "$MANIFEST" "$FAILED"; touch "$FAILED"
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
  if [ "$running_n" -eq 0 ] && [ "$pending_n" -eq 0 ]; then
    echo "=== RUN COMPLETE $(date '+%F %T') done=$done_n giveup=$giveup_n ==="; break; fi
  while IFS=$'\t' read -r name s stage outp pcnt tcol; do
    [ -z "$name" ] && continue
    is_done "$outp" && continue
    { pgrep -af 'preprocess_data_cm[.]py' 2>/dev/null || true; } | grep -qF "$outp" && continue
    attf="${stage}.attempts"; att=$(cat "$attf" 2>/dev/null || echo 0)
    if [ "$att" -ge 3 ]; then
      grep -qF "${name} s${s}" "$FAILED" 2>/dev/null || echo "[$(date '+%F %T')] GIVEUP $name s$s (attempts=$att)" >> "$FAILED"
      continue
    fi
    if [ "$(count_running)" -ge "$MAX_CONCURRENT" ]; then continue; fi
    logf="$LOG_DIR/${name}_s${s}.log"
    echo "[$(date '+%F %T')] LAUNCH $name s$s ($pcnt parquet col=$tcol att=$((att+1))) -> ${outp##*/} (running=$(count_running))"
    echo $((att+1)) > "$attf"
    nice -n "$NICE" "$PY" "$SERIAL" --input-dir "$stage" --output-prefix "$outp" \
      --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
      --mode content --text-column "$tcol" --dtype int32 --max-chars 50000 --doc-timeout 120 > "$logf" 2>&1 &
    sleep 2
  done < "$PLAN"
  sleep "$RESCAN"
done

echo "=== FINAL SUMMARY $(date '+%F %T') ==="
done_n=0; fail_n=0; total_tokens=0; total_bin_bytes=0
: > "$MANIFEST"
while IFS=$'\t' read -r name s stage outp pcnt tcol; do
  [ -z "$name" ] && continue
  if is_done "$outp"; then
    done_n=$((done_n + 1))
    tok=$(shard_tokens "${outp}.json"); bin=$(stat -c %s "${outp}.bin" 2>/dev/null || echo 0)
    total_tokens=$((total_tokens + tok)); total_bin_bytes=$((total_bin_bytes + bin))
    printf '%s\t%s\t%d\t%d\tOK\n' "$name" "${outp##*/}" "$tok" "$bin" >> "$MANIFEST"
  else
    fail_n=$((fail_n + 1))
    grep -qF "${name} s${s}" "$FAILED" 2>/dev/null || echo "[$(date '+%F %T')] INCOMPLETE $name s$s" >> "$FAILED"
    printf '%s\t%s\t%d\t%d\tFAIL\n' "$name" "${outp##*/}" 0 0 >> "$MANIFEST"
  fi
done < "$PLAN"
echo "done=$done_n/$TOTAL_SHARDS failed=$fail_n total_tokens=$total_tokens total_bin_bytes=$total_bin_bytes"
echo "failed_shards: $(grep -c '.' "$FAILED" 2>/dev/null || echo 0)"
if [ "$fail_n" -ne 0 ]; then echo "[$(date '+%F %T')] PHASE 2 had $fail_n FAILED shards; aborting finalize"; exit 1; fi
echo "=== PHASE 2: TOKENIZE DONE $(date '+%F %T') ==="


# ===== Phase 3: FINALIZE（清空未分词侧车 → build_mirror → gen_md --measure → gen_report → git）=====
echo "=== PHASE 3: FINALIZE START $(date '+%F %T') ==="
UTOK=$DATA/untokenized_sft_sources.tsv
# SFT 两源已分词入镜像 ⇒ 清空未分词侧车（保留表头），避免 gen_md 重复加「未分词」行。
echo -e "download_dir\tfiles\tbytes\tstatus\tevidence_cmd\tstructure\tnotes" > "$UTOK"
echo "[finalize] cleared untokenized sidecar (SFT-2605 + Agent-2609 now tokenized)"

# 刷新 tokenized 镜像（build_tokenized_mirror.py 已含 SFT 两源 ENTRIES → INDEX.tsv 12 行）
"$PY" "$BUILD_MIRROR" > "$LOG_DIR/build_mirror.log" 2>&1
echo "[finalize] build_tokenized_mirror.py done (see $LOG_DIR/build_mirror.log)"
tail -5 "$LOG_DIR/build_mirror.log"

# 重生成 DATA_MAPPING.md（--measure 重测下载目录 du，含新增 SFT 两源 dl_dir）
"$PY" "$GEN_MD" --measure --out "$DATA/DATA_MAPPING.md" > "$LOG_DIR/gen_md.log" 2>&1
echo "[finalize] gen_data_mapping_md.py --measure done"
tail -3 "$LOG_DIR/gen_md.log"
DMM_BYTES=$(wc -c < "$DATA/DATA_MAPPING.md")

# 重生成 report_data_mapping_zh.html
"$PY" "$GEN_REPORT" > "$LOG_DIR/gen_report.log" 2>&1
echo "[finalize] gen_report_data_mapping_html.py done"
tail -2 "$LOG_DIR/gen_report.log"
REPORT=$REPO/doc/BaiZe-ISEDA2027/reports/report_data_mapping_zh.html
REPORT_BYTES=$(wc -c < "$REPORT")

# 写 finalize 标记（供运维巡检）
cat > "$STAGING_BASE/FINALIZE_DONE.txt" <<EOF
finalize_time: $(date '+%F %T')
sft_2605_shards: $(ls "$SFT2605_OUT"/*.bin 2>/dev/null | wc -l)
agent_2609_shards: $(ls "$AGENT2609_OUT"/*.bin 2>/dev/null | wc -l)
total_tokens: $total_tokens
total_bin_bytes: $total_bin_bytes
DATA_MAPPING.md_bytes: $DMM_BYTES
report_bytes: $REPORT_BYTES
EOF
echo "[finalize] FINALIZE_DONE.txt written"

# git 提交推送（仅本线文件；先 pull --rebase --autostash 避免冲突）
cd "$REPO"
echo "[finalize] git pull --rebase --autostash ..."
https_proxy="$PROXY" http_proxy="$PROXY" git pull --rebase --autostash origin main 2>&1 | tail -3 || \
  echo "[finalize] WARN: git pull failed (continue to commit)"
git add -- \
  doc/BaiZe-ISEDA2027/run/data/DATA_MAPPING.md \
  doc/BaiZe-ISEDA2027/reports/report_data_mapping_zh.html \
  doc/BaiZe-ISEDA2027/run/data/untokenized_sft_sources.tsv \
  doc/BaiZe-ISEDA2027/run/data/build_tokenized_mirror.py \
  doc/BaiZe-ISEDA2027/run/data/gen_data_mapping_md.py \
  doc/BaiZe-ISEDA2027/run/data/gen_report_data_mapping_html.py \
  doc/BaiZe-ISEDA2027/run/data_pipeline/convert_sft_jsonl_to_parquet.py \
  doc/BaiZe-ISEDA2027/run/data_pipeline/run_tokenize_sft.sh
# INDEX.tsv 在 datasets/ 仓库外（不入 git）；MANIFEST/FAILED 同理。镜像产物在 /nas_env（不入 git）。
git commit -m "data tokenize: 分词 SFT-2605+Agent-2609 到 /nas_env 纳入映射镜像同等对待 (DMM=${DMM_BYTES}B report=${REPORT_BYTES}B shards=$(ls "$SFT2605_OUT"/*.bin 2>/dev/null|wc -l)+$(ls "$AGENT2609_OUT"/*.bin 2>/dev/null|wc -l) tokens=${total_tokens})" 2>&1 | tail -3
echo "[finalize] git push ..."
https_proxy="$PROXY" http_proxy="$PROXY" git push origin main 2>&1 | tail -3 || \
  echo "[finalize] WARN: git push failed — 留待下轮补推"
echo "=== PHASE 3: FINALIZE DONE $(date '+%F %T') ==="
echo "============================================================"
echo "=== run_tokenize_sft.sh ALL DONE $(date '+%F %T') ==="
echo "  SFT-2605  shards=$(ls "$SFT2605_OUT"/*.bin 2>/dev/null | wc -l)  tokens=$(python3 -c "print(sum(__import__('json').load(open(f)).get('num_tokens',0) for f in __import__('glob').glob('$SFT2605_OUT/*.json')))" 2>/dev/null)"
echo "  Agent-2609 shards=$(ls "$AGENT2609_OUT"/*.bin 2>/dev/null | wc -l)  tokens=$(python3 -c "print(sum(__import__('json').load(open(f)).get('num_tokens',0) for f in __import__('glob').glob('$AGENT2609_OUT/*.json')))" 2>/dev/null)"
echo "  DATA_MAPPING.md = ${DMM_BYTES} B ; report = ${REPORT_BYTES} B"
echo "============================================================"

