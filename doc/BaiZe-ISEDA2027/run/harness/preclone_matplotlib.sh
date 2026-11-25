#!/bin/bash
# Preclone matplotlib: fetch all 23 base_commits with --depth=1 into bare repo
# Uses proxy (github not directly reachable from this machine)
set -u
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128

BARE=/dev/shm/repos/matplotlib
LOG=/tmp/matplotlib_preclone2.log

echo "[$(date)] Starting matplotlib preclone (targeted fetch)" > "$LOG"

# Ensure bare repo exists
if [ ! -d "$BARE/objects" ]; then
  mkdir -p "$BARE"
  cd "$BARE"
  git init --bare -q
  git remote add origin https://github.com/matplotlib/matplotlib.git
fi

cd "$BARE"

# All 23 base_commits from SWE-bench Lite matplotlib instances
COMMITS=(
  b7d05919865fc0c37a0164cf467d5d5513bd0ede
  f670fe78795b18eb1118707721852209cd77ad51
  c33557d120eefe3148ebfcf2e758ff2357966000
  3eadeacc06c9f2ddcdac6ae39819faa9fbee9e39
  97fc1154992f64cfb2f86321155a7404efeb2d8a
  33a0599711d26dc2b79f851c6daed4947df7c167
  29a86636a9c45ab5ac4d80ac76eaee497f460dce
  149a0398b391cfc4eddb5e659f50b3c66f32ea65
  5c4595267ccd3daf78f5fd05693b7ecbcd575c1e
  269c0b94b4fcf8b1135011c1556eac29dc09de15
  e98d8d085e8f53ec0467422b326f7738a2dd695e
  af39f1edffcd828f05cfdd04f2e59506bb4a27bc
  e148998d9bed9d1b53a91587ad48f9bb43c7737f
  332937997d03e0c173be6d9fc1841e9186e857df
  a3011dfd1aaa2487cce8aa7369475533133ef777
  66f7956984cbfc3647e867c6e5fde889a89c64ef
  430fb1db88843300fb4baae3edc499bbfe073b0c
  66ba515e671638971bd11a34cff12c107a437e0b
  7eafdd8af3c523c1c77b027d378fb337dd489f18
  73394f2b11321e03a5df199ec0196f27a728b0b0
  78bf53caacbb5ce0dc7aa73f07a74c99f1ed919b
  00afcc0c6d4d2e4390338127f05b8f4fdb4e7087
  f6a781f77f5ddf1204c60ca7c544809407d4a807
)

SUCCESS=0
FAIL=0
for i in "${!COMMITS[@]}"; do
  c="${COMMITS[$i]}"
  # Check if already fetched
  if git cat-file -e "$c^{commit}" 2>/dev/null; then
    echo "[$(date)] [$((i+1))/${#COMMITS[@]}] $c already exists, skip" >> "$LOG"
    SUCCESS=$((SUCCESS+1))
    continue
  fi
  echo "[$(date)] [$((i+1))/${#COMMITS[@]}] Fetching $c ..." >> "$LOG"
  if timeout 180 git fetch origin --depth=1 "$c" 2>> "$LOG"; then
    echo "[$(date)]   SUCCESS" >> "$LOG"
    SUCCESS=$((SUCCESS+1))
  else
    echo "[$(date)]   FAILED (exit=$?)" >> "$LOG"
    FAIL=$((FAIL+1))
    # Retry once after 5s
    sleep 5
    if timeout 180 git fetch origin --depth=1 "$c" 2>> "$LOG"; then
      echo "[$(date)]   SUCCESS (retry)" >> "$LOG"
      SUCCESS=$((SUCCESS+1))
      FAIL=$((FAIL-1))
    else
      echo "[$(date)]   FAILED (retry also failed)" >> "$LOG"
    fi
  fi
done

echo "[$(date)] DONE: success=$SUCCESS fail=$FAIL" >> "$LOG"
echo "[$(date)] Bare repo size: $(du -sh "$BARE" | cut -f1)" >> "$LOG"
