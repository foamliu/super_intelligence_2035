#!/usr/bin/env bash
# git_line_commit.sh — 多线共享工作副本时，为**单条线**安全提交/推送（worktree 隔离）。
#
# 背景与协议见 run/ops/SHARED_REPO_GIT_PROTOCOL.md（运维 2026-11-19 22:0x）。
# 核心思想：共享工作树只读只跑；提交一律在 /tmp/gitpush_<line> 的**隔离 worktree** 里做，
#           只 add 本线白名单路径 ⇒ 永不撞共享 index / 永不卷入别线在途改动。
#
# 用法
#   bash run/ops/git_line_commit.sh --line vision -m "vision wake#1700: ..." --dry-run
#   bash run/ops/git_line_commit.sh --line vision -m "vision wake#1700: ..."
#   bash run/ops/git_line_commit.sh --line vision -m "..." --paths doc/.../MEMORY_VISION.md
#   bash run/ops/git_line_commit.sh --line posttrain -m "..." --sync-shared
#
# 退出码：0=成功/无内容；2=参数或白名单错误；3=git 操作失败
set -uo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED="${SHARED:-$(git -C "$SELF_DIR/../../../.." rev-parse --show-toplevel 2>/dev/null || true)}"
LINE=""; MSG=""; DRY=0; NOPUSH=0; SYNC=0; PATHS_GIVEN=0; PATHS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --line) LINE="${2:-}"; shift 2 ;;
    -m|--message) MSG="${2:-}"; shift 2 ;;
    --paths) shift; PATHS_GIVEN=1; while [ $# -gt 0 ] && [ "${1#--}" = "$1" ]; do PATHS+=("$1"); shift; done ;;
    --dry-run) DRY=1; shift ;;
    --no-push) NOPUSH=1; shift ;;
    --sync-shared) SYNC=1; shift ;;
    --allow-empty) shift ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[err] 未知参数: $1" >&2; exit 2 ;;
  esac
done

[ -n "$SHARED" ] && [ -d "$SHARED/.git" ] || { echo "[err] 找不到共享仓库根（可用 SHARED=/path 指定）" >&2; exit 2; }
[ -n "$LINE" ] || { echo "[err] 缺 --line" >&2; exit 2; }
[ -n "$MSG" ]  || { echo "[err] 缺 -m 提交信息" >&2; exit 2; }

WT="/tmp/gitpush_${LINE}"
log() { echo "[$(date +%H:%M:%S)] $*"; }

# ── 白名单 ────────────────────────────────────────────────────────────────
allowed() {  # allowed <path>
  local p="$1"
  case "$LINE" in
    vision)    [[ "$p" == doc/BaiZe-ISEDA2027/run/vision/* || "$p" == doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/daily-memories-vision/* \
              || "$p" == doc/BaiZe-ISEDA2027/run/reports/report_vision_* \
              || "$p" == doc/BaiZe-ISEDA2027/reports/report_vision_* ]] ;;
    posttrain) [[ "$p" == doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md || "$p" == doc/BaiZe-ISEDA2027/run/BAIZE_POSTTRAIN_TASK.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/ARCHIVE_OPERATOR_POSTTRAIN.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/daily-memories-posttrain/* \
              || "$p" == doc/BaiZe-ISEDA2027/run/baize_posttrain_* \
              || "$p" == doc/BaiZe-ISEDA2027/run/attribution_3615_run* \
              || "$p" == doc/BaiZe-ISEDA2027/run/POSTTRAIN_* \
              || "$p" == doc/BaiZe-ISEDA2027/reports/report_posttrain_* ]] ;;
    pretrain)  [[ "$p" == doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/daily-memories/* \
              || "$p" == doc/BaiZe-ISEDA2027/run/reports/report_pretrain_* \
              || "$p" == doc/BaiZe-ISEDA2027/reports/report_pretrain_* ]] ;;
    harness)   [[ "$p" == doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/daily-memories-harness/* \
              || "$p" == doc/BaiZe-ISEDA2027/run/harness/* \
              || "$p" == doc/BaiZe-ISEDA2027/reports/report_harness_* ]] ;;
    data)      [[ "$p" == doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md \
              || "$p" == doc/BaiZe-ISEDA2027/run/daily-memories-data/* \
              || "$p" == doc/BaiZe-ISEDA2027/run/data* \
              || "$p" == doc/BaiZe-ISEDA2027/run/reports/report_s1s2_* ]] ;;
    *) return 1 ;;
  esac
}

# ── 0) stale 锁保护（只在无 git 进程且锁 >120s 时清） ───────────────────
if [ -f "$SHARED/.git/index.lock" ]; then
  if pgrep -x git >/dev/null 2>&1; then
    log "[wait] .git/index.lock 存在且有 git 进程在跑 → 等待最多 60s"
    for _ in $(seq 1 12); do sleep 5; [ -f "$SHARED/.git/index.lock" ] || break; done
    [ -f "$SHARED/.git/index.lock" ] && { log "[abort] 锁仍被占用，稍后重试（不删活锁）"; exit 3; }
  else
    if [ -n "$(find "$SHARED/.git/index.lock" -mmin +2 2>/dev/null)" ]; then
      log "[fix] 无 git 进程 + 锁 >120s ⇒ 清 stale 锁"
      [ "$DRY" = 1 ] || rm -f "$SHARED/.git/index.lock"
    else
      log "[abort] 锁很新（<120s），可能刚有进程退出，稍后重试"; exit 3
    fi
  fi
fi

# ── 1) fetch ─────────────────────────────────────────────────────────────
log "[1/6] fetch origin main"
git -C "$SHARED" fetch --prune origin main || { log "[abort] fetch 失败"; exit 3; }

# ── 2) 收集待提交路径（缺省按白名单从 status 自动发现） ──────────────────
if [ "$PATHS_GIVEN" = 0 ]; then
  mapfile -t PATHS < <(git -C "$SHARED" status --porcelain -uall | sed 's/^...//' | sed 's/.* -> //')
fi
KEEP=()
for p in ${PATHS[@]+"${PATHS[@]}"}; do
  [ -z "$p" ] && continue
  if allowed "$p"; then KEEP+=("$p"); else log "[skip] 非本线路径，忽略: $p"; fi
done
if [ ${#KEEP[@]} -eq 0 ]; then log "[ok] 无可提交的本线改动（0 文件）"; exit 0; fi
log "[2/6] 待提交 ${#KEEP[@]} 个文件："; printf '   %s\n' "${KEEP[@]}"

[ "$DRY" = 1 ] && { log "[dry-run] 结束（未建 worktree/未提交/未推送）"; exit 0; }

# ── 3) 建/重建隔离 worktree（独立 index/HEAD，不碰共享树） ───────────────
log "[3/6] worktree: $WT (detach origin/main)"
git -C "$SHARED" worktree remove --force "$WT" >/dev/null 2>&1 || true
rm -rf "$WT"
git -C "$SHARED" worktree add --detach "$WT" origin/main >/dev/null || { log "[abort] worktree add 失败"; exit 3; }

# ── 4) 复制本线文件进 worktree ───────────────────────────────────────────
log "[4/6] copy 本线文件 → worktree"
for p in "${KEEP[@]}"; do
  if [ -e "$SHARED/$p" ]; then
    mkdir -p "$WT/$(dirname "$p")"
    cp -a "$SHARED/$p" "$WT/$p"
  else
    rm -f "$WT/$p"   # 本线删除的文件
  fi
done

# ── 5) add + commit ─────────────────────────────────────────────────────
cd "$WT" || exit 3
git add -- "${KEEP[@]}" || { log "[abort] git add 失败"; exit 3; }
if git diff --cached --quiet; then log "[ok] 与 origin/main 无差异（可能已推过）"; exit 0; fi
git -c user.name="${LINE}-agent" -c user.email="${LINE}-agent@localhost" \
    commit -m "$MSG" >/dev/null || { log "[abort] commit 失败"; exit 3; }
log "[5/6] committed $(git rev-parse --short HEAD): $(git show --stat --oneline HEAD | tail -1)"

[ "$NOPUSH" = 1 ] && { log "[ok] --no-push：停在 $WT（可手工 push）"; exit 0; }

# ── 6) push（rejected → 本 worktree 内 rebase 后重试） ───────────────────
PUSH_OK=0
for try in 1 2 3; do
  if git push origin HEAD:main 2>"/tmp/gitpush_${LINE}.err"; then
    log "[6/6] pushed ✅ (try=$try)"; PUSH_OK=1; break
  fi
  log "[retry $try] push 被拒 → fetch+rebase 后重试"
  git fetch origin main >/dev/null 2>&1
  if ! git rebase origin/main >"/tmp/gitpush_${LINE}.rebase" 2>&1; then
    log "[abort] worktree 内 rebase 冲突（**共享树未受影响**）。冲突文件："
    git diff --name-only --diff-filter=U | sed 's/^/   /'
    log "       处理：cd $WT 手工解决 → git rebase --continue → git push origin HEAD:main"
    exit 3
  fi
  sleep $(( try * 3 ))
done
[ "$PUSH_OK" = 1 ] || { log "[abort] push 3 次失败，见 /tmp/gitpush_${LINE}.err"; exit 3; }

# ── 7) 可选：共享树干净才快进（脏则跳过，绝不 reset） ────────────────────
if [ "$SYNC" = 1 ]; then
  if [ -z "$(git -C "$SHARED" status --porcelain)" ]; then
    git -C "$SHARED" merge --ff-only origin/main >/dev/null 2>&1 \
      && log "[sync] 共享树已 ff 至 origin/main" \
      || log "[sync-skip] 共享树 ff 失败（可能已分叉），未做任何 reset"
  else
    log "[sync-skip] 共享树有未提交改动，跳过 ff（不做 reset，避免毁别线在途）"
  fi
fi

log "完成。shared HEAD=$(git -C "$SHARED" rev-parse --short HEAD)  origin=$(git -C "$SHARED" rev-parse --short origin/main)"
