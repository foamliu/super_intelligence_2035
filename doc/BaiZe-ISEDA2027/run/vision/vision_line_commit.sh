#!/bin/bash
# vision_line_commit.sh — worktree-isolated commit + push for the vision line on the SHARED .17 repo.
#
# WHY THIS EXISTS (RCA: run/vision/SHARED_REPO_GIT_PROTOCOL_RCA.md):
#   vision & posttrain share ONE working copy + ONE .git on .17.  vision's old loop did
#   `git add -A` + `git commit` + `git push origin main` directly in the shared tree.  Because
#   other lines (and vision's own manual worktree pushes) advance origin/main, that push was
#   rejected (non-fast-forward), so vision auto-commits piled up on the shared HEAD ("N ahead").
#   When posttrain then ran `git pull --rebase --autostash`, it replayed those diverged vision
#   commits onto an origin that ALREADY contained vision's worktree-pushed files -> conflicts on
#   MEMORY_VISION.md / daily-memories-vision; autostash also grabbed both lines' uncommitted
#   MEMORY edits -> pop conflicts; and concurrent `git` ops tripped `index.lock` contention.
#
# WHAT THIS HELPER DOES (keeps the shared tree READ-ONLY for git writes):
#   1. fetch origin/main
#   2. create a DETACHED worktree at origin/main (own index, does not touch shared HEAD/index/WT)
#   3. copy ONLY vision-whitelist paths from the shared working tree into the worktree
#   4. `git add` ONLY those paths (no `-A`; .gitignore still honored -> regenerable binaries skipped)
#   5. commit + `push HEAD:main` (fast-forward)
#   6. VERIFY the commit really landed on origin/main (merge-base --is-ancestor) -- never trust
#      the push exit code alone (a rejected non-ff push exits non-zero but stderr is easy to miss)
#   7. realign the shared HEAD to origin/main with `git reset --mixed` (keeps working tree,
#      resets index+HEAD) so posttrain's next `git pull --ff-only` succeeds with 0 conflict
#
# USAGE:
#   vision_line_commit.sh "commit message" [file1 file2 ...]
#     - files given: only those vision-territory paths are shipped (preferred, explicit).
#     - no files:    auto-detect changed+untracked paths intersected with the vision whitelist.
#
# RED LINES:
#   - never `git add -A` across the whole repo; never `reset --hard`; never `clean -xfd`
#   - never stage a path outside the vision whitelist
#   - never delete another line's stash
#   - refuse to `reset --mixed` while an index.lock is held by another process

set -uo pipefail

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /nas_data/app.e0031982/code/super_intelligence_2035)"
MSG="${1:-}"
if [ -z "$MSG" ]; then
  echo "usage: $0 \"commit message\" [file1 file2 ...]" >&2
  exit 2
fi
shift || true

VISION_WHITELIST=(
  doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md
  doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md
  doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md
  doc/BaiZe-ISEDA2027/run/daily-memories-vision
  doc/BaiZe-ISEDA2027/run/vision
  doc/BaiZe-ISEDA2027/run/baize_vision_loop.sh
  doc/BaiZe-ISEDA2027/run/GPU29_ALLOC.md
)

in_whitelist() {
  local p="$1" w
  for w in "${VISION_WHITELIST[@]}"; do
  case "$p" in
    "$w"|"$w"/*) return 0;;
  esac
  done
  return 1
}

cd "$GIT_ROOT" || { echo "cannot cd $GIT_ROOT" >&2; exit 1; }
git fetch origin main >/dev/null 2>&1 || { echo "fetch failed" >&2; exit 1; }

# Determine vision paths to ship.
PATHS=()
if [ "$#" -gt 0 ]; then
  for p in "$@"; do
  if in_whitelist "$p"; then PATHS+=("$p"); else echo "[vision_line_commit] SKIP non-vision: $p" >&2; fi
  done
else
  mapfile -t CHANGED < <(git diff --name-only HEAD; git ls-files --others --exclude-standard)
  for c in "${CHANGED[@]}"; do
  if in_whitelist "$c"; then PATHS+=("$c"); fi
  done
fi

if [ "${#PATHS[@]}" -eq 0 ]; then
  echo "[vision_line_commit] nothing to commit (vision territory clean vs HEAD)."
  # still realign in case shared HEAD drifted but WT has no vision diffs
  if [ -f "$GIT_ROOT/.git/index.lock" ]; then
  echo "[vision_line_commit] index.lock held -- skip realign (another git op in progress)." >&2
  else
  git reset --mixed origin/main >/dev/null 2>&1 || true
  fi
  exit 0
fi

WT="$(mktemp -d /tmp/gitpush_vision.XXXXXX)"
echo "[vision_line_commit] shipping ${#PATHS[@]} path(s) via worktree $WT"
git worktree add --detach "$WT" origin/main >/dev/null 2>&1 || { echo "worktree add failed" >&2; rm -rf "$WT"; exit 1; }
trap 'git worktree remove --force "$WT" 2>/dev/null || true; rm -rf "$WT"' EXIT

# Copy changed vision files from the shared working tree into the worktree (preserve rel paths).
for p in "${PATHS[@]}"; do
  if [ -e "$p" ]; then
  mkdir -p "$WT/$(dirname "$p")"
  cp -a -- "$p" "$WT/$p"
  fi
done

# Stage ONLY these vision paths (no -A). .gitignore is honored -> regenerable binaries skipped.
git -C "$WT" add -- "${PATHS[@]}" 2>/dev/null || true

if git -C "$WT" diff --cached --quiet 2>/dev/null; then
  echo "[vision_line_commit] nothing staged (content identical to origin)."
else
  git -C "$WT" commit -m "$MSG" >/dev/null 2>&1 || { echo "commit failed" >&2; exit 1; }
  NEWC="$(git -C "$WT" rev-parse HEAD)"
  pushed=0
  for attempt in 1 2 3 4 5; do
    git -C "$WT" fetch origin main >/dev/null 2>&1 || true
    # replay our commit onto the latest origin/main (detached HEAD rebase is fine)
    git -C "$WT" rebase origin/main >/dev/null 2>&1 || { git -C "$WT" rebase --abort 2>/dev/null || true; }
    NEWC="$(git -C "$WT" rev-parse HEAD)"
    if git -C "$WT" push origin HEAD:main 2>&1; then
      pushed=1; break
    fi
    echo "[vision_line_commit] push attempt $attempt rejected (origin advancing); retrying after re-fetch+rebase ..." >&2
    sleep 3
  done
  if [ "$pushed" = 1 ]; then
  echo "[vision_line_commit] pushed $NEWC"
  else
  echo "[vision_line_commit] push FAILED after retries (origin advancing too fast); aborting realign." >&2
  exit 1
  fi
  git fetch origin main >/dev/null 2>&1 || true
  if git merge-base --is-ancestor "$NEWC" origin/main 2>/dev/null; then
  echo "[vision_line_commit] VERIFIED on origin/main: $NEWC"
  else
  echo "[vision_line_commit] WARNING: $NEWC NOT on origin/main after push -- DO NOT realign." >&2
  exit 1
  fi
fi

# Realign shared HEAD to origin/main (mixed: keep working tree, reset index+HEAD).
if [ -f "$GIT_ROOT/.git/index.lock" ]; then
  echo "[vision_line_commit] index.lock held by another process -- skip realign (safe; will align next call)." >&2
else
  git reset --mixed origin/main >/dev/null 2>&1 || echo "[vision_line_commit] reset --mixed failed (non-fatal)" >&2
  echo "[vision_line_commit] shared HEAD realigned to origin/main: $(git rev-parse --short HEAD)"
fi
echo "[vision_line_commit] DONE"
