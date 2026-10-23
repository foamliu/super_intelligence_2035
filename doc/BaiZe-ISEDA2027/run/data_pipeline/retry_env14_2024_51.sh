#!/bin/bash
# retry_env14_2024_51.sh — Supplementary retry for 61 failed files in CC-MAIN-2024-51
# resolve.py moved on after 60 files failed with read timeout; this script retries them.
# Launch: setsid -f nohup bash retry_env14_2024_51.sh > /tmp/retry_2024_51.log 2>&1 &
set -euo pipefail

SHARD_DIR="/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4/CC-MAIN-2024-51"
MISSING_FILE="/tmp/env14_2024_51_missing.txt"
HF_PROXY="http://172.19.92.23:13128"
HF_ENDPOINT="https://hf-mirror.com"
REPO_ID="openbmb/Ultra-FineWeb"
REPO_PATH_PREFIX="data/ultrafineweb_en_v1_4/CC-MAIN-2024-51"
PARALLEL=6
MAX_RETRIES=10
NICE_VAL=10

export https_proxy="$HF_PROXY" http_proxy="$HF_PROXY" HF_ENDPOINT="$HF_ENDPOINT"

echo "[$(date '+%F %T')] === retry CC-MAIN-2024-51 START (parallel=$PARALLEL, retries=$MAX_RETRIES) ==="

if [ ! -f "$MISSING_FILE" ]; then
  echo "[$(date '+%F %T')] ERROR: $MISSING_FILE not found. Regenerating..."
  python3 - "$SHARD_DIR" "$MISSING_FILE" <<'PY'
import os, sys
d, out = sys.argv[1], sys.argv[2]
have = set(f for f in os.listdir(d) if f.endswith('.parquet') and not f.endswith('.partial'))
missing = []
for i in range(512):
    fn = f'ultrafineweb-en-CC-MAIN-2024-51-part-{i:04d}-of-512.parquet'
    if fn not in have:
        missing.append(fn)
with open(out, 'w') as f:
    for fn in missing:
        f.write(fn + '\n')
print(f'Regenerated: {len(missing)} missing files')
PY
fi

TOTAL=$(wc -l < "$MISSING_FILE")
echo "[$(date '+%F %T')] Missing files to download: $TOTAL"

# Download using Python with ThreadPoolExecutor
nice -n "$NICE_VAL" python3 - "$MISSING_FILE" "$SHARD_DIR" "$REPO_ID" "$REPO_PATH_PREFIX" "$HF_ENDPOINT" "$PARALLEL" "$MAX_RETRIES" <<'PYEOF'
import os, sys, time, requests, logging
from concurrent.futures import ThreadPoolExecutor, as_completed

missing_file, shard_dir, repo_id, repo_path_prefix, endpoint, parallel, max_retries = sys.argv[1:8]
parallel = int(parallel)
max_retries = int(max_retries)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%F %T')
log = logging.getLogger()

with open(missing_file) as f:
    files_to_download = [line.strip() for line in f if line.strip()]

log.info(f"Downloading {len(files_to_download)} files to {shard_dir}")

session = requests.Session()
session.headers.update({"User-Agent": "baize-data-retry/1.0"})

def download_one(filename):
    repo_path = f"{repo_path_prefix}/{filename}"
    local_path = os.path.join(shard_dir, filename)
    url = f"{endpoint}/datasets/{repo_id}/resolve/main/{repo_path}"
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(url, timeout=60, stream=True, allow_redirects=True)
            r.raise_for_status()
            tmp_path = local_path + ".partial"
            with open(tmp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            os.rename(tmp_path, local_path)
            size = os.path.getsize(local_path)
            return (filename, True, size, attempt)
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                return (filename, False, 0, attempt)
    return (filename, False, 0, max_retries)

done = fail = 0
total_bytes = 0
t0 = time.time()
with ThreadPoolExecutor(max_workers=parallel) as pool:
    futures = {pool.submit(download_one, fn): fn for fn in files_to_download}
    for fut in as_completed(futures):
        fn, ok, size, attempts = fut.result()
        if ok:
            done += 1
            total_bytes += size
            log.info(f"  OK: {fn} ({size/1e6:.1f} MB, {attempts} tries)")
        else:
            fail += 1
            log.error(f"  FAIL: {fn} (after {attempts} retries)")

elapsed = time.time() - t0
log.info(f"=== retry CC-MAIN-2024-51 END: {done} done, {fail} fail, "
         f"{total_bytes/1e9:.2f} GB, {elapsed:.0f}s ===")

# Verify final parquet count
final_count = len([f for f in os.listdir(shard_dir) if f.endswith('.parquet') and not f.endswith('.partial')])
log.info(f"Final parquet count in CC-MAIN-2024-51: {final_count}/512")
PYEOF

echo "[$(date '+%F %T')] retry script finished"
