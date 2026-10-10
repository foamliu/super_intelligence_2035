#!/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
"""download_en_v1_4.py — Download Ultra-FineWeb en_v1_4 per-file.

Bypasses snapshot_download timeout (list_repo_tree recursive fails for 64K+ files).
Instead: list each CC-MAIN dir non-recursively, then hf_hub_download per file.

Launch: setsid -f nohup python3 download_en_v1_4.py > /tmp/en_v1_4_dl.log 2>&1 &
"""
import os, sys, time, logging, subprocess
from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "openbmb/Ultra-FineWeb"
REPO_TYPE = "dataset"
LOCAL_DIR = "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb"
BASE_PATH = "data/ultrafineweb_en_v1_4"
MAX_RETRIES = 5
RETRY_SLEEP = 30

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S", stream=sys.stdout)
log = logging.getLogger("en_v1_4_dl")

os.environ["https_proxy"] = "http://172.19.92.25:13128"
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"

api = HfApi()

def list_snapshot_dirs():
    """List all CC-MAIN-XXXX dirs under en_v1_4 (non-recursive, fast)."""
    entries = list(api.list_repo_tree(
        REPO_ID, repo_type=REPO_TYPE, path_in_repo=BASE_PATH, recursive=False))
    return sorted([e.path.split("/")[-1] for e in entries if hasattr(e, "path")])

def list_files_in_dir(snap):
    """List files in a CC-MAIN-XXXX dir (non-recursive)."""
    path_in_repo = f"{BASE_PATH}/{snap}"
    entries = list(api.list_repo_tree(
        REPO_ID, repo_type=REPO_TYPE, path_in_repo=path_in_repo, recursive=False))
    return [e.path for e in entries if hasattr(e, "path") and not hasattr(e, "children")]

def is_complete(local_path):
    """Check if file exists and has no .incomplete sibling."""
    return os.path.isfile(local_path) and not os.path.exists(local_path + ".incomplete")

def download_one(repo_path, max_retries=MAX_RETRIES):
    """Download a single file with retry."""
    for attempt in range(1, max_retries + 1):
        try:
            hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE,
                            filename=repo_path, local_dir=LOCAL_DIR)
            return True
        except Exception as e:
            log.warning(f"  FAIL: {repo_path} (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(RETRY_SLEEP)
    return False

def main():
    log.info("=== en_v1_4 download START ===")
    log.info("Fetching snapshot list from HF API...")
    snapshots = list_snapshot_dirs()
    log.info(f"Found {len(snapshots)} snapshots")

    t_done = t_skip = t_fail = 0
    s_done = s_skip = s_fail = 0

    for idx, snap in enumerate(snapshots, 1):
        try:
            files = list_files_in_dir(snap)
        except Exception as e:
            log.error(f"[{idx}/{len(snapshots)}] {snap}: FAIL to list: {e}")
            s_fail += 1
            continue

        if not files:
            log.warning(f"[{idx}/{len(snapshots)}] {snap}: No files found")
            s_fail += 1
            continue

        # Check if all complete
        if all(is_complete(os.path.join(LOCAL_DIR, f)) for f in files):
            log.info(f"[{idx}/{len(snapshots)}] {snap}: SKIP ({len(files)} files complete)")
            t_skip += len(files)
            s_skip += 1
            continue

        log.info(f"[{idx}/{len(snapshots)}] {snap}: {len(files)} files, downloading...")
        sd = ss = sf = 0

        for fp in files:
            local_full = os.path.join(LOCAL_DIR, fp)
            if is_complete(local_full):
                ss += 1
                continue
            if download_one(fp):
                sd += 1
            else:
                sf += 1

        t_done += sd
        t_skip += ss
        t_fail += sf

        if sf == 0:
            log.info(f"[{idx}/{len(snapshots)}] {snap}: DONE (+{sd} new, {ss} skip)")
            s_done += 1
        else:
            log.error(f"[{idx}/{len(snapshots)}] {snap}: PARTIAL (+{sd}, {ss} skip, {sf} fail)")
            s_fail += 1

        # Disk check
        try:
            st = os.statvfs("/nas_train")
            free_gb = (st.f_bavail * st.f_frsize) / (1024 ** 3)
            if free_gb < 500:
                log.error(f"DISK LOW: {free_gb:.0f} GB free! Stopping.")
                break
        except Exception:
            pass

    log.info(f"=== en_v1_4 download END ===")
    log.info(f"Snapshots: {s_done} done, {s_skip} skip, {s_fail} fail / {len(snapshots)}")
    log.info(f"Files: +{t_done} new, {t_skip} skip, {t_fail} fail")

    r1 = subprocess.run(["find", os.path.join(LOCAL_DIR, BASE_PATH),
                         "-name", "*.parquet"], capture_output=True, text=True)
    pq = len(r1.stdout.strip().split("\n")) if r1.stdout.strip() else 0
    r2 = subprocess.run(["find", os.path.join(LOCAL_DIR, BASE_PATH),
                         "-name", "*.incomplete"], capture_output=True, text=True)
    inc = len(r2.stdout.strip().split("\n")) if r2.stdout.strip() else 0
    log.info(f"FINAL: {pq} parquet, {inc} .incomplete")

if __name__ == "__main__":
    main()

