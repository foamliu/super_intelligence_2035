#!/bin/bash
# Pre-clone 5 high-freq repos for P1-2 rerun (reduces git fetch 503 risk)
set -e
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

for repo in "${REPOS[@]}"; do
    name=$(basename "$repo")
    dir="$DEST/$name"
    if [ -d "$dir/.git" ]; then
        echo "[preclone] $name already exists, updating..."
        cd "$dir"
        git fetch --all --quiet 2>&1 || echo "  fetch failed (ok, existing commits available)"
    else
        echo "[preclone] cloning $repo -> $dir ..."
        git clone --bare "https://github.com/$repo" "$dir" 2>&1 | tail -3
    fi
    echo "[preclone] $name: $(cd "$dir" && git rev-list --count --all 2>/dev/null || echo '?') commits"
done

echo "[preclone] DONE"
