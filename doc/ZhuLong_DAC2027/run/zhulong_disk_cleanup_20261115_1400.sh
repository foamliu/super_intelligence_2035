#!/usr/bin/env bash
# ZhuLong disk cleanup script - 2026-11-15 14:00
# Guardrails: explicit paths only; no rm -rf /home/* or ~/* wildcards;
# never touch running eval (batch 2026_1115_110506), git repos, source,
# .ssh, tokens, conda/venv in use, designflow ledger/trace, cline session dirs.
set -u
RUN_DIR="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
TSV="$RUN_DIR/zhulong_disk_cleanup_20261115_1400.tsv"
EVID="$RUN_DIR/zhulong_disk_cleanup_20261115_1400_evidence.log"
printf 'path\tbytes\thuman\treason\n' > "$TSV"
: > "$EVID"

# helper: record evidence (du + ls -lt), delete, log to TSV
del_dir() {
  local path="$1" reason="$2"
  if [ ! -e "$path" ]; then echo "[skip not-found] $path" >> "$EVID"; return; fi
  local human bytes
  human=$(timeout 60 du -sh "$path" 2>/dev/null | awk '{print $1}')
  bytes=$(timeout 60 du -sb "$path" 2>/dev/null | awk '{print $1}')
  echo "=== EVIDENCE: $path ($human) — $reason ===" >> "$EVID"
  timeout 60 ls -lt "$path" 2>/dev/null | head -8 >> "$EVID"
  rm -rf -- "$path"
  local rc=$?
  printf '%s\t%s\t%s\t%s\n' "$path" "${bytes:-0}" "${human:-?}" "$reason" >> "$TSV"
  echo "[del rc=$rc] $path ($human) — $reason"
}

del_files() {
  # delete a list of explicit files; log each
  local reason="$1"; shift
  for f in "$@"; do
    if [ -f "$f" ]; then
      local human bytes
      human=$(du -sh "$f" 2>/dev/null | awk '{print $1}')
      bytes=$(stat -c%s "$f" 2>/dev/null)
      echo "=== EVIDENCE(file): $f ($human) — $reason ===" >> "$EVID"
      rm -f -- "$f"
      printf '%s\t%s\t%s\t%s\n' "$f" "${bytes:-0}" "${human:-?}" "$reason" >> "$TSV"
      echo "[del-file] $f ($human) — $reason"
    fi
  done
}

EDIR="/nasdata/app.e0031982/eda_code_eval"
CEDIR="/nasdata/app.e0031982/code/eda_code_eval"
CACHE="/nasdata/app.e0031982/.cache"
LOCAL="/nasdata/app.e0031982/.local"

echo "########## (a) CACHES ##########"
del_dir "$CACHE/cline_eval"           "cache: DesignFlow per-task eval cache (not running PyAether eval; no writes >2h; regenerable)"
del_dir "$CACHE/cline_eval_C"         "cache: DesignFlow eval cache_C (stale, mtime Nov 2)"
del_dir "$LOCAL/share/uv"             "cache: uv python download cache (regenerable; rule a)"
# small backup/scratch caches under .cache
del_dir "$CACHE/discfix_inline_run"   "cache/scratch: discfix inline run temp"
del_dir "$CACHE/d_r614"               "cache/scratch: d_r614 temp"
del_dir "$CACHE/d_r612"               "cache/scratch: d_r612 temp"
del_dir "$CACHE/tmp_candidates_D.txt" "cache/scratch: tmp candidates (single file temp)"
del_dir "$CACHE/scratch_r446"         "cache/scratch: scratch_r446 temp"
del_dir "$CACHE/df_shard_D"           "cache/scratch: df_shard_D temp"
del_files "cache backup" \
  "$CACHE/EDA-Eval-DesignFlow_C.jsonl.bak.r338"
# judge_* scratch dirs (cache, regenerable)
for j in "$CACHE"/judge_EDA-Eval-DesignFlow-*; do
  [ -d "$j" ] && del_dir "$j" "cache/scratch: judge temp dir (regenerable)"
done

echo "########## (b) LOGS / TEMP ##########"
del_files "log: old rotated app.log (Nov 9-12, >3d; app.log current kept)" \
  "/nasdata/app.e0031982/code/logs/app.log.2" \
  "/nasdata/app.e0031982/code/logs/app.log.3" \
  "/nasdata/app.e0031982/code/logs/app.log.4"
del_dir "/nasdata/app.e0031982/miniforge3/install_tmp" "temp: miniforge3 install temp (leftover from conda install)"

echo "########## (c) BACKUPS / INTERMEDIATES ##########"
del_files "backup: zhulong cli sourcemap (.map, not needed at runtime)" \
  "$LOCAL/share/zhulong/cli.mjs.map"

echo "########## (d) OLD PRODUCTS (superseded; result .jsonl summaries preserved) ##########"
# eda_code_eval: October batches (mtime Oct, >3d, superseded)
for d in \
  2026_1019_005631 2026_1019_005714 2026_1019_035502 2026_1019_071104 \
  2026_1019_145634 2026_1019_145634_BACKUP_223148 2026_1019_235040 \
  2026_1020_045902 2026_1020_050005 2026_1020_063134 2026_1020_090900 \
  2026_1020_161451 2026_1020_215918 2026_1021_104432 2026_1022_105416 \
  2026_1023_002456 2026_1023_052506 2026_1023_072528 2026_1023_093614 \
  2026_1023_093805 2026_1023_093847 2026_1023_093924 2026_1023_093948 \
  2026_1023_094528 2026_1023_103036 2026_1023_125220 2026_1023_155612 \
  2026_1023_183402 2026_1023_203835 2026_1023_231253 2026_1024_141148 \
  2026_1024_222540 2026_1024_222846 2026_1024_223138 2026_1024_224219 \
  2026_1026_082858 2026_1026_083652 2026_1026_112623 2026_1026_125254 \
  2026_1026_154647 2026_1026_160802 2026_1026_190240 2026_1027_083127 \
  2026_1027_123502 2026_1028_150556 2026_1028_151059 2026_1028_231232 \
  2026_1029_041540 2026_1030_231313 2026_1031_044456 2026_1031_103027 \
  2026_1031_164422 2026_1031_230700 ; do
  del_dir "$EDIR/$d" "old product: Oct eda_code_eval batch (superseded, mtime>3d)"
done
# eda_code_eval: Nov 13-15 superseded posttrain-baseline attempts (result .jsonl summaries preserved in parent; running batch 2026_1115_110506 kept)
for d in \
  2026_1113_173444 2026_1113_173557 2026_1113_173818 2026_1113_174204 \
  2026_1113_214819 2026_1113_215002 \
  2026_1114_160431 2026_1114_161225 2026_1114_204151 2026_1114_204159 \
  2026_1114_204934 2026_1114_233006 2026_1114_294494 2026_1114_294497 \
  2026_1115_004854 2026_1115_015649 2026_1115_025255 2026_1115_025541 \
  2026_1115_035637 2026_1115_051404 2026_1115_073454 ; do
  del_dir "$EDIR/$d" "old product: superseded posttrain-baseline batch (result .jsonl summary preserved; running 110506 kept)"
done
# code/eda_code_eval: Nov 12 batches (archived per task book 2026-11-12, commits e09c7e238/a909fe482)
for d in \
  2026_1112_220400 2026_1112_221008 2026_1112_221520 2026_1112_222504 \
  2026_1112_222702 2026_1112_161042 2026_1112_085105 ; do
  del_dir "$CEDIR/$d" "old product: Nov12 eda_code_eval batch (archived per task book commits e09c7e238/a909fe482)"
done
del_files "old product: Nov12 code/eda_code_eval result summary (archived)" \
  "$CEDIR/completed_code_generation_2026_1112_220400.jsonl" \
  "$CEDIR/code_generation_2026_1112_220400.jsonl" \
  "$CEDIR/completed_code_generation_2026_1112_161042.jsonl" \
  "$CEDIR/code_generation_2026_1112_161042.jsonl" \
  "$CEDIR/completed_code_generation_2026_1112_085105.jsonl" \
  "$CEDIR/code_generation_2026_1112_085105.jsonl" \
  "$CEDIR/completed_code_generation_2026_1112_044128.jsonl"

echo "########## (e) opencode old session caches ##########"
# opencode/snapshot: 6 dirs all from Oct 12-28 (old sessions; current session not present here)
for s in "$LOCAL/share/opencode/snapshot"/* ; do
  [ -d "$s" ] && del_dir "$s" "cache: old opencode session snapshot (Oct, not current session)"
done
# opencode/tool-output: files older than 2 days (old session tool caches; today's kept)
while IFS= read -r f; do
  [ -f "$f" ] && del_files "cache: old opencode tool-output (>2d, old session)" "$f"
done < <(find "$LOCAL/share/opencode/tool-output" -type f -mtime +2 2>/dev/null)
# tool-output __pycache__
del_dir "$LOCAL/share/opencode/tool-output/__pycache__" "cache: opencode tool-output __pycache__"

echo "########## (extra) stale vscode-server install (no active VS Code session for app.e0031982) ##########"
del_dir "/nasdata/app.e0031982/.vscode-server/cli/servers" "stale install: vscode-server cli/servers (no active VS Code session for my user; re-downloads on reconnect)"

echo "########## DONE ##########"
echo "=== AFTER ==="
df -h /home /nasdata
echo "=== TSV summary ==="
awk -F'\t' 'NR>1{s+=$2} END{printf "total_bytes=%d total_human_approx=%.2fGB rows=%d\n", s, s/1073741824, NR-1}' "$TSV"
