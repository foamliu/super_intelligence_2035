#!/usr/bin/env bash
# ============================================================
# 长上下文扩展阶梯（ABF）：32K → 64K → 128K，逐级升 seq、保持 tok/mb/GPU=16,384
#   bash scripts/longctx_ladder.sh [--dry-run] [--from 1] [--ladder configs/longctx_ladder.tsv]
# 前置：S2 已跑完（累计 1,050,000 步）；theta=1e6（common.env）；Decay 尚未开始。
# 每级：跑完 → 校验（0 NaN / 吞吐≥门限）→ 通过才进下一级；任一级失败即停。
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"
# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"

LADDER="$BAIZE_LLM_HOME/configs/longctx_ladder.tsv"
DRY=0
FROM=1
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --from) FROM="${2:-1}"; shift 2 ;;
    --ladder) LADDER="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "未知参数：$1" ;;
  esac
done
[ -f "$LADDER" ] || die "找不到阶梯表：$LADDER"

START=1050000          # S2 末（累计口径）
OUT="/tmp/baize_longctx_ladder_$(date +%m%d_%H%M).tsv"
{
  printf "# longctx ladder @ %s\n" "$(ts)"
  printf "rung\tseq\tcp\tgbs\ttokens\tsteps\tstart_iter\tend_iter\tpretrain_tok_s\tstatus\n"
} > "$OUT"
log "阶梯表=$LADDER  起始累计步=$START  台账=$OUT  dry_run=$DRY"

while IFS=$'\t' read -r rung seq tokens cp gbs note; do
  case "$rung" in ''|'#'*) continue ;; esac
  [ "$rung" -lt "$FROM" ] && continue
  # 校验：seq/CP 必须 = 16384；gbs 必须能被 DP 整除且 accum=16
  dp=$(( 16 / cp ))
  [ "$dp" -ge 1 ] || die "rung$rung: CP=$cp ⇒ DP=$dp <1，16 卡跑不了"
  [ $(( seq / cp )) -eq 16384 ] || die "rung$rung: seq/CP=$(( seq / cp )) != 16384（显存顶格线）"
  [ $(( gbs % (1 * dp) )) -eq 0 ] || die "rung$rung: gbs=$gbs 不是 DP=$dp 的整数倍"
  accum=$(( gbs / dp ))
  [ "$accum" -eq 16 ] || warn "rung$rung: accum=$accum（期望 16；tok/step 会变）"
  tps=$(( gbs * seq ))
  steps=$(( (tokens + tps - 1) / tps ))
  END=$(( START + steps ))
  log "rung$rung: seq=$seq CP=$cp DP=$dp gbs=$gbs accum=$accum tok/step=$tps tokens=$tokens steps=$steps 区间=[$START,$END)"
  if [ "$DRY" = "1" ]; then
    printf "  SEQ=%s CP=%s GBS=%s ITERS=%s START_ITER=%s bash scripts/train.sh longctx\n" \
      "$seq" "$cp" "$gbs" "$END" "$START"
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t-\tDRY\n" \
      "$rung" "$seq" "$cp" "$gbs" "$tokens" "$steps" "$START" "$END" >> "$OUT"
    START="$END"
    continue
  fi

  SEQ="$seq" CP="$cp" GBS="$gbs" ITERS="$END" START_ITER="$START" \
    bash "$HERE/train.sh" longctx
  rc=$?
  LOG_W="/tmp/baize_longctx_${NAME}_worker.log"
  nan=$(grep -ci 'nan' "$LOG_W" 2>/dev/null || echo 0)
  lastit=$(grep -oE 'iteration +[0-9]+' "$LOG_W" 2>/dev/null | tail -1 | grep -oE '[0-9]+' || echo 0)
  if [ "$rc" -ne 0 ] || [ "$nan" -gt 0 ]; then
    warn "rung$rung FAIL（rc=$rc nan_hits=$nan last_iter=$lastit）⇒ 停止阶梯"
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t-\tFAIL(rc=%s,nan=%s)\n" \
      "$rung" "$seq" "$cp" "$gbs" "$tokens" "$steps" "$START" "$END" "$rc" "$nan" >> "$OUT"
    exit 1
  fi
  log "rung$rung 通过（last_iter=$lastit, 0 NaN）"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t-\tOK\n" \
    "$rung" "$seq" "$cp" "$gbs" "$tokens" "$steps" "$START" "$END" >> "$OUT"
  START="$END"
done < "$LADDER"

log "阶梯结束。台账：$OUT"
log "下一步：① 跑长上下文评测（PPL/passkey，见 docs/LONGCTX_ABF_PLAN.md §4）② 达标后才开 Decay（train.sh decay，其 ITERS 需按扩展总量顺延）"
