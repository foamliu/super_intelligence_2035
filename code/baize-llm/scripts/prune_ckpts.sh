#!/usr/bin/env bash
# ============================================================
# checkpoint 保留策略清理（默认 dry-run，不动盘）
#   策略 = 最近 N 个 + 每 M 步的里程碑 + 训练将续跑的 latest + 显式 protect
# 用法:
#   bash scripts/prune_ckpts.sh                 # dry-run，打印将删/将留
#   bash scripts/prune_ckpts.sh --apply         # 真删
#   bash scripts/prune_ckpts.sh --keep-last 2 --milestone-every 50000 --apply
#   bash scripts/prune_ckpts.sh --dir /path/checkpoints --apply
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"
# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"

DIR=""
KEEP_LAST=3
MILE=25000
APPLY=0
PROTECT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) DIR="${2:-}"; shift 2 ;;
    --keep-last) KEEP_LAST="${2:-3}"; shift 2 ;;
    --milestone-every) MILE="${2:-25000}"; shift 2 ;;
    --protect) PROTECT="${2:-}"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "未知参数：$1" ;;
  esac
done
[ -n "$DIR" ] || DIR="$EXP_ROOT/$NAME/checkpoints"
[ -d "$DIR" ] || die "目录不存在：$DIR"

iter_of() { basename "$1" | sed 's/^iter_0*//'; }

mapfile -t ALL < <(find "$DIR" -maxdepth 1 -type d -name 'iter_*' | sort -t_ -k2 -n)
[ "${#ALL[@]}" -gt 0 ] || { log "没有 iter_* 目录"; exit 0; }

ITERS=(); for d in "${ALL[@]}"; do ITERS+=("$(iter_of "$d")"); done
MAXIT="${ITERS[${#ITERS[@]}-1]}"

# 训练将续跑的 latest（必须保）
LATEST_FILE="$DIR/latest_checkpointed_iteration.txt"
LATEST_TRAIN=""
[ -f "$LATEST_FILE" ] && LATEST_TRAIN="$(tr -dc '0-9' < "$LATEST_FILE")"

KEEP=(); DELETE=()
idx=0
TOTAL=${#ALL[@]}
for d in "${ALL[@]}"; do
  it="${ITERS[$idx]}"; idx=$((idx + 1))
  n=$((10#$it))
  keep=0
  # 最近 KEEP_LAST 个（按排序位置，不按数值阈值——间隔可能不均）
  if [ $(( TOTAL - idx + 1 )) -le "$KEEP_LAST" ]; then keep=1; fi
  # 里程碑
  if [ "$MILE" -gt 0 ] && [ $(( n % MILE )) -eq 0 ]; then keep=1; fi
  # latest_checkpointed_iteration
  if [ -n "$LATEST_TRAIN" ] && [ "$((10#$LATEST_TRAIN))" -eq "$n" ]; then keep=1; fi
  # 显式 protect（空格/逗号分隔，可写 iter_0009441 或 9441）
  for p in ${PROTECT//,/ }; do
    pn="$(echo "$p" | sed 's/^iter_0*//; s/^iter_//')"
    [ -n "$pn" ] && [ "$((10#$pn))" -eq "$n" ] 2>/dev/null && keep=1
  done
  if [ "$keep" -eq 1 ]; then KEEP+=("$d"); else DELETE+=("$d"); fi
done

echo "===== prune_ckpts @ $(ts) ====="
echo "  dir=$DIR"
echo "  策略: keep-last=$KEEP_LAST  milestone-every=$MILE  latest_train=${LATEST_TRAIN:-<none>}  protect='${PROTECT}'"
echo "  总数=${#ALL[@]}  保留=${#KEEP[@]}  待删=${#DELETE[@]}"

sz() { du -sm "$1" 2>/dev/null | awk '{print $1}'; }
KEEP_MB=0; for d in "${KEEP[@]}"; do KEEP_MB=$((KEEP_MB + $(sz "$d"))); done
DEL_MB=0
echo
echo "  ——— 保留 ———"
for d in "${KEEP[@]}"; do printf "    keep   %-22s %6s MB\n" "$(basename "$d")" "$(sz "$d")"; done
echo "  ——— 待删 ———"
for d in "${DELETE[@]}"; do m=$(sz "$d"); DEL_MB=$((DEL_MB + m)); printf "    delete %-22s %6s MB\n" "$(basename "$d")" "$m"; done
echo
echo "  保留合计 ${KEEP_MB} MB (≈$((KEEP_MB / 1024)) GB)  /  待删 ${DEL_MB} MB (≈$((DEL_MB / 1024)) GB)"
echo "  df: $(df -h "$DIR" | tail -1)"

if [ "$APPLY" -ne 1 ]; then
  echo
  log "dry-run：未删除任何目录。确认后加 --apply 执行。"
  exit 0
fi
[ "${#DELETE[@]}" -gt 0 ] || { log "无需删除"; exit 0; }
for d in "${DELETE[@]}"; do
  log "rm -rf $d"
  rm -rf -- "$d" || warn "删除失败：$d"
done
echo
log "完成：删除 ${#DELETE[@]} 个，释放 ≈$((DEL_MB / 1024)) GB；剩余 $(find "$DIR" -maxdepth 1 -type d -name 'iter_*' | wc -l) 个"
