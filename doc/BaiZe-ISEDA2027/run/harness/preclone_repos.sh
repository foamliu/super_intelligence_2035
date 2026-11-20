#!/bin/bash
# Pre-clone 5 high-freq repos for P1-2 rerun (reduces git fetch 503 risk)
# fix: use --filter=blob:none (partial clone) to avoid "early EOF" on large repos
#      + retry with exponential backoff + --depth 1 fallback
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
DEST=/dev/shm/repos
mkdir -p "$DEST"

REPOS=(
    "matplotlib/matplotlib"
    "django/django"
    "sympy/sympy"
    "scikit-learn/scikit-learn"
    "pytest-dev/pytest"
)

clone_repo() {
    local repo="$1" dir="$2"
    # Try 1: partial clone (blob:none) — small initial download, blobs fetched on demand
    echo "[preclone] cloning $repo (partial) -> $dir ..."
    if git clone --bare --filter=blob:none "https://github.com/$repo" "$dir" 2>&1 | tail -5; then
        return 0
    fi
    rm -rf "$dir"
    echo "[preclone] partial clone failed, retry 1/3 with depth=1..."
    sleep 5
    # Try 2: shallow clone
    if git clone --bare --depth=1 "https://github.com/$repo" "$dir" 2>&1 | tail -5; then
        return 0
    fi
    rm -rf "$dir"
    echo "[preclone] shallow clone failed, retry 2/3..."
    sleep 15
    # Try 3: full clone with longer buffer
    if GIT_HTTP_LOW_SPEED_LIMIT=0 GIT_HTTP_LOW_SPEED_TIME=300 git clone --bare "https://github.com/$repo" "$dir" 2>&1 | tail -5; then
        return 0
    fi
    rm -rf "$dir"
    return 1
}

for repo in "${REPOS[@]}"; do
    name=$(basename "$repo")
    dir="$DEST/$name"
    if [ -d "$dir/objects" ] && [ -f "$dir/HEAD" ]; then
        echo "[preclone] $name already exists, fetching..."
        cd "$dir" && git fetch --all --quiet 2>&1 || echo "  fetch failed (ok, existing commits available)"
    else
        clone_repo "$repo" "$dir" || echo "[preclone] FAILED to clone $name (will retry next run)"
    fi
    if [ -d "$dir" ]; then
        echo "[preclone] $name: $(cd "$dir" && git rev-list --count --all 2>/dev/null || echo '?') commits"
    fi
done

echo "[preclone] DONE"
