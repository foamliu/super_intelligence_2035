#!/bin/bash
# Dry-run 等价验证（用户令 2026-11-20 08:4x）：复现 baize_posttrain_loop.sh 新 git_sync_and_push
# 的白名单检测逻辑，列路径不真推。证明：①不卷入别线在途 ②白名单能命中 posttrain 路径。
set -uo pipefail
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
REL="doc/BaiZe-ISEDA2027/run"
_pt_in_whitelist() {
  case "$1" in
    "$REL/MEMORY_POSTTRAIN.md"|"$REL/EXPERIMENTS_POSTTRAIN.md"|"$REL/BAIZE_POSTTRAIN_TASK.md"|"$REL/ARCHIVE_OPERATOR_POSTTRAIN.md") return 0;;
    "$REL/daily-memories-posttrain"/*) return 0;;
    "$REL/baize_posttrain_"*) return 0;;
    "$REL/bpt_"*) return 0;;
    "$REL/POSTTRAIN_"*) return 0;;
    "$REL/posttrain_"*) return 0;;
    "$REL/attribution_3615_run"*) return 0;;
    "$REL/rca_"*) return 0;;
    "$REL/reports/report_posttrain_"*) return 0;;
    "doc/BaiZe-ISEDA2027/reports/report_posttrain_"*) return 0;;
    "doc/BaiZe-ISEDA2027/reports/archive/posttrain"/*) return 0;;
    *) return 1;;
  esac
}
cd "$GIT_ROOT" || exit 1
echo "[dryrun] shared-tree changed+untracked total:"
mapfile -t CHANGED < <(git diff --name-only HEAD; git ls-files --others --exclude-standard)
echo "${#CHANGED[@]}"
PATHS=(); OTHER=0
for P in "${CHANGED[@]}"; do
  if _pt_in_whitelist "$P"; then PATHS+=("$P"); else OTHER=$((OTHER+1)); fi
done
echo "[dryrun] posttrain-whitelist matched (would stage): ${#PATHS[@]}"
printf '  %s\n' "${PATHS[@]}"
echo "[dryrun] non-posttrain (correctly excluded): $OTHER"
echo "[dryrun] sample excluded (other lines' in-flight):"
printf '  %s\n' "${CHANGED[@]}" | grep -vE 'baize_posttrain_|bpt_|POSTTRAIN_|posttrain_|attribution_3615_run|rca_|MEMORY_POSTTRAIN|EXPERIMENTS_POSTTRAIN|BAIZE_POSTTRAIN_TASK|daily-memories-posttrain|report_posttrain_' | head -8
echo "[dryrun] whitelist positive test (known tracked posttrain paths should match):"
for t in "$REL/baize_posttrain_anneal.sh" "$REL/bpt_attribution_ablation.sh" "$REL/rca_baseline_aggregate.py" "$REL/reports/report_posttrain_loop_git_diag_zh.html" "doc/BaiZe-ISEDA2027/reports/report_posttrain_loop_git_diag_zh.html" "$REL/MEMORY_POSTTRAIN.md"; do
  if _pt_in_whitelist "$t"; then echo "  MATCH  $t"; else echo "  MISS!! $t"; fi
done
echo "[dryrun] negative test (other-line paths should NOT match):"
for t in "$REL/MEMORY_DATA.md" "$REL/MEMORY_VISION.md" "$REL/harness/incr_eval_all.py" "$REL/BAIZE_HARNESS_TASK.md"; do
  if _pt_in_whitelist "$t"; then echo "  LEAK!! $t"; else echo "  reject $t"; fi
done
