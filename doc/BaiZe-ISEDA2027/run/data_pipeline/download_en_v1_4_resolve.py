#!/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
"""download_en_v1_4_resolve.py — Download Ultra-FineWeb en_v1_4 via hf-mirror RESOLVE endpoint.

WHY THIS SCRIPT (2026-10-18):
  huggingface_hub's hf_hub_download resolves xet-backed files to `us.aws.cdn.hf.co`,
  which the .23 proxy CANNOT reach (SSL EOF). But hf-mirror's `/resolve` endpoint
  returns 302 -> `cas-bridge.xethub.hf.co`, which .23 CAN reach. So we bypass
  huggingface_hub entirely:
    1. List snapshot dirs  via hf-mirror API   (/api/datasets/.../tree/main/...)
    2. List files per snap  via hf-mirror API   (path + size metadata)
    3. Download each file   via hf-mirror RESOLVE (requests follows 302 -> cas-bridge)
  Already-complete files (exists + size matches API) are SKIPped.

Proxy / endpoint (read from env, same convention as download_en_v1_4.sh/.py):
  .23 + hf-mirror : HF_PROXY=http://172.19.92.23:13128 HF_ENDPOINT=https://hf-mirror.com
  .25 direct hf.co : HF_PROXY=http://172.19.92.25:13128  + unset HF_ENDPOINT

Launch:
  export HF_PROXY=http://172.19.92.23:13128 HF_ENDPOINT=https://hf-mirror.com
  export https_proxy=$HF_PROXY http_proxy=$HF_PROXY
  setsid -f nohup python3 download_en_v1_4_resolve.py > /tmp/en_v1_4_dl_dot23.log 2>&1 &
"""
import os, sys, time, json, logging, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

REPO_ID = "openbmb/Ultra-FineWeb"
LOCAL_DIR = "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb"
BASE_PATH = "data/ultrafineweb_en_v1_4"
MAX_RETRIES = 5
RETRY_SLEEP = 15
MAX_WORKERS = int(os.environ.get("DL_WORKERS", "12"))
CHUNK = 1024 * 1024  # 1 MB stream chunk
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 300

_HF_PROXY = os.environ.get("HF_PROXY", "http://172.19.92.23:13128")
_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
os.environ["https_proxy"] = _HF_PROXY
os.environ["http_proxy"] = _HF_PROXY

PROXIES = {"http": _HF_PROXY, "https": _HF_PROXY}
HEADERS = {"User-Agent": "baize-data-dl/resolve/1.0"}

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S", stream=sys.stdout)
log = logging.getLogger("en_v1_4_resolve")
_print_lock = threading.Lock()
_tls = threading.local()


def session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.proxies = PROXIES
        s.headers.update(HEADERS)
        _tls.s = s
    return s


def api_tree(path_in_repo, recursive=False):
    """List entries under path_in_repo via hf-mirror API. Returns list of dicts."""
    url = f"{_ENDPOINT}/api/datasets/{REPO_ID}/tree/main/{path_in_repo}"
    params = {"recursive": "true" if recursive else "false"}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session().get(url, params=params, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            log.warning(f"api_tree retry {attempt}/{MAX_RETRIES} for {path_in_repo}: {e}")
            time.sleep(RETRY_SLEEP)


def list_snapshot_dirs():
    entries = api_tree(BASE_PATH, recursive=False)
    return sorted([e["path"].split("/")[-1] for e in entries
                   if e.get("type") == "directory" and "path" in e])


def list_files_in_dir(snap):
    entries = api_tree(f"{BASE_PATH}/{snap}", recursive=False)
    return [(e["path"], int(e.get("size", 0)))
            for e in entries if e.get("type") == "file" and "path" in e]


def local_path_for(repo_path):
    return os.path.join(LOCAL_DIR, repo_path)


def is_complete(repo_path, expected_size):
    lp = local_path_for(repo_path)
    return os.path.isfile(lp) and (expected_size == 0 or os.path.getsize(lp) == expected_size)


def download_one(repo_path, expected_size, max_retries=MAX_RETRIES):
    lp = local_path_for(repo_path)
    if is_complete(repo_path, expected_size):
        return ("skip", 0)
    tmp = lp + ".partial"
    url = f"{_ENDPOINT}/datasets/{REPO_ID}/resolve/main/{repo_path}"
    for attempt in range(1, max_retries + 1):
        try:
            existing = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            hdrs = dict(HEADERS)
            if existing > 0:
                hdrs["Range"] = f"bytes={existing}-"
            r = session().get(url, headers=hdrs, stream=True, allow_redirects=True,
                              timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            if r.status_code == 416:
                r.close()
                if expected_size and os.path.getsize(tmp) == expected_size:
                    os.rename(tmp, lp)
                    return ("done", expected_size)
                os.remove(tmp)
                raise IOError("416 range not satisfiable")
            r.raise_for_status()
            mode = "ab" if (existing > 0 and r.status_code == 206) else "wb"
            if mode == "wb":
                existing = 0
            written = existing
            with open(tmp, mode) as f:
                for chunk in r.iter_content(chunk_size=CHUNK):
                    if chunk:
                        f.write(chunk)
                        written += len(chunk)
            r.close()
            if expected_size and written != expected_size:
                raise IOError(f"size mismatch: got {written}, expected {expected_size}")
            os.rename(tmp, lp)
            return ("done", written)
        except Exception as e:
            if attempt == max_retries:
                with _print_lock:
                    log.error(f"  FAIL: {repo_path} after {max_retries} retries: {e}")
                return ("fail", 0)
            time.sleep(RETRY_SLEEP * attempt)
    return ("fail", 0)


def download_snapshot(snap, files):
    to_dl = [(p, s) for p, s in files if not is_complete(p, s)]
    skip = len(files) - len(to_dl)
    if not to_dl:
        return (0, skip, 0, 0)
    done = fail = bytes_dl = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(download_one, p, s): (p, s) for p, s in to_dl}
        for fut in as_completed(futs):
            status, nbytes = fut.result()
            if status == "done":
                done += 1
                bytes_dl += nbytes
            elif status == "fail":
                fail += 1
            total = done + fail + skip
            if total % 50 == 0:
                with _print_lock:
                    log.info(f"    {snap}: {done} done, {fail} fail, {skip} skip / {len(files)}")
    return (done, skip, fail, bytes_dl)


def main():
    log.info(f"=== en_v1_4 resolve-download START (workers={MAX_WORKERS}, "
             f"proxy={_HF_PROXY}, endpoint={_ENDPOINT}) ===")
    log.info("Fetching snapshot list from hf-mirror API...")
    snapshots = list_snapshot_dirs()
    log.info(f"Found {len(snapshots)} snapshots")
    t_total = time.time()
    t_done = t_skip = t_fail = s_done = s_skip = s_fail = 0
    total_bytes = 0
    for idx, snap in enumerate(snapshots, 1):
        try:
            files = list_files_in_dir(snap)
        except Exception as e:
            log.error(f"[{idx}/{len(snapshots)}] {snap}: FAIL to list files: {e}")
            s_fail += 1
            continue
        if not files:
            log.warning(f"[{idx}/{len(snapshots)}] {snap}: no files")
            s_fail += 1
            continue
        if all(is_complete(p, s) for p, s in files):
            log.info(f"[{idx}/{len(snapshots)}] {snap}: SKIP ({len(files)} files complete)")
            t_skip += len(files)
            s_skip += 1
            continue
        log.info(f"[{idx}/{len(snapshots)}] {snap}: {len(files)} files, downloading "
                 f"(parallel {MAX_WORKERS})...")
        t0 = time.time()
        sd, ss, sf, sb = download_snapshot(snap, files)
        elapsed = time.time() - t0
        t_done += sd; t_skip += ss; t_fail += sf; total_bytes += sb
        rate = sb / elapsed / 1e6 if elapsed > 0 else 0
        if sf == 0:
            log.info(f"[{idx}/{len(snapshots)}] {snap}: DONE (+{sd} new, {ss} skip, "
                     f"{sb/1e9:.2f} GB, {elapsed:.0f}s, {rate:.1f} MB/s)")
            s_done += 1
        else:
            log.error(f"[{idx}/{len(snapshots)}] {snap}: PARTIAL (+{sd}, {ss} skip, "
                      f"{sf} fail, {elapsed:.0f}s)")
            s_fail += 1
        if idx % 5 == 0:
            el = time.time() - t_total
            log.info(f"--- Progress: {idx}/{len(snapshots)} snapshots, +{t_done} new, "
                     f"{t_skip} skip, {t_fail} fail, {total_bytes/1e9:.2f} GB, {el:.0f}s ---")
    total_elapsed = time.time() - t_total
    log.info(f"=== en_v1_4 resolve-download END ({total_elapsed:.0f}s) ===")
    log.info(f"Snapshots: {s_done} done, {s_skip} skip, {s_fail} fail / {len(snapshots)}")
    log.info(f"Files: +{t_done} new, {t_skip} skip, {t_fail} fail, {total_bytes/1e9:.2f} GB")
    import subprocess
    base = os.path.join(LOCAL_DIR, BASE_PATH)
    pq = len(subprocess.run(["find", base, "-name", "*.parquet"],
               capture_output=True, text=True).stdout.strip().split("\n")) if True else 0
    inc = len(subprocess.run(["find", base, "-name", "*.incomplete"],
               capture_output=True, text=True).stdout.strip().split("\n")) if True else 0
    part = len(subprocess.run(["find", base, "-name", "*.partial"],
               capture_output=True, text=True).stdout.strip().split("\n")) if True else 0
    log.info(f"FINAL: {pq} parquet, {inc} .incomplete, {part} .partial")


if __name__ == "__main__":
    main()
