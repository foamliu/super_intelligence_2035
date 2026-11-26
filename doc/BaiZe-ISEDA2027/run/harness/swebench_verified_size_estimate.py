#!/usr/bin/env python3
"""SWE-bench Verified Docker image size estimation with layer-digest dedup."""
from __future__ import annotations
import json, sys, time, shutil, subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests

PROXY = {"http": "http://172.19.92.25:13128", "https": "http://172.19.92.25:13128"}
REGISTRY = "https://registry-1.docker.io"
AUTH_URL = "https://auth.docker.io/token"
AUTH_SERVICE = "registry.docker.io"
MAX_WORKERS = 8
TIMEOUT = 60
RETRY = 3
IMAGES_FILE = "/tmp/swebench_verified_images.json"
OUTPUT_FILE = "/tmp/swebench_verified_size_report.json"
DOCKER_ROOT = "/data/docker"
ACCEPT = ("application/vnd.oci.image.index.v1+json, "
          "application/vnd.docker.distribution.manifest.list.v2+json, "
          "application/vnd.oci.image.manifest.v1+json, "
          "application/vnd.docker.distribution.manifest.v2+json")
_token_cache: dict[str, str] = {}

def get_token(repo):
    if repo in _token_cache:
        return _token_cache[repo]
    url = f"{AUTH_URL}?service={AUTH_SERVICE}&scope=repository:{repo}:pull"
    r = requests.get(url, proxies=PROXY, timeout=TIMEOUT)
    r.raise_for_status()
    tok = r.json()["token"]
    _token_cache[repo] = tok
    return tok

def fetch_manifest(repo, ref):
    token = get_token(repo)
    headers = {"Authorization": f"Bearer {token}", "Accept": ACCEPT}
    url = f"{REGISTRY}/v2/{repo}/manifests/{ref}"
    for attempt in range(1, RETRY + 1):
        try:
            r = requests.get(url, headers=headers, proxies=PROXY, timeout=TIMEOUT)
            if r.status_code == 401:
                _token_cache.pop(repo, None)
                token = get_token(repo)
                headers["Authorization"] = f"Bearer {token}"
                continue
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == RETRY:
                raise
            time.sleep(2 * attempt)

def get_amd64_layers(repo):
    ml = fetch_manifest(repo, "latest")
    if "layers" in ml:
        return ml["layers"], "latest"
    for entry in ml.get("manifests", []):
        if entry.get("platform", {}).get("architecture") == "amd64":
            digest = entry["digest"]
            m = fetch_manifest(repo, digest)
            return m.get("layers", []), digest
    raise ValueError(f"No amd64 manifest for {repo}")

def estimate_one(image_name):
    try:
        layers, m_digest = get_amd64_layers(image_name)
        total = sum(l.get("size", 0) for l in layers)
        digests = [(l["digest"], l.get("size", 0)) for l in layers]
        return {"image": image_name, "ok": True, "n_layers": len(layers),
                "total_size": total, "layers": digests, "manifest_digest": m_digest}
    except Exception as exc:
        return {"image": image_name, "ok": False, "error": str(exc)}

def check_local(images):
    try:
        r = subprocess.run(["sg", "docker", "-c",
            "docker images --format '{{.Repository}}:{{.Tag}}'"],
            capture_output=True, text=True, timeout=30)
        local = set(r.stdout.strip().splitlines())
        return {img for img in images if img in local}
    except Exception:
        return set()

def main():
    images = json.loads(Path(IMAGES_FILE).read_text())
    print(f"Total images to estimate: {len(images)}")
    print("Checking locally-present images ...")
    local = check_local(images)
    print(f"  Already local: {len(local)} / {len(images)}")
    print(f"Fetching manifests ({MAX_WORKERS} workers) ...")
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(estimate_one, img): img for img in images}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            done += 1
            if done % 50 == 0 or done == len(images):
                print(f"  {done}/{len(images)} done")
    ok_results = [r for r in results if r["ok"]]
    fail_results = [r for r in results if not r["ok"]]
    naive_sum = sum(r["total_size"] for r in ok_results)
    layer_map = {}
    for r in ok_results:
        for dg, sz in r["layers"]:
            if dg not in layer_map or layer_map[dg] < sz:
                layer_map[dg] = sz
    dedup_sum = sum(layer_map.values())
    n_unique_layers = len(layer_map)
    sizes = sorted(r["total_size"] for r in ok_results)
    median = sizes[len(sizes) // 2] if sizes else 0
    p90 = sizes[int(len(sizes) * 0.9)] if sizes else 0
    p99 = sizes[int(len(sizes) * 0.99)] if sizes else 0
    disk_total, disk_used, disk_free = shutil.disk_usage(DOCKER_ROOT)
    report = {
        "total_images": len(images), "manifests_ok": len(ok_results),
        "manifests_failed": len(fail_results),
        "failed_images": [r["image"] for r in fail_results],
        "already_local": len(local),
        "naive_sum_gb": round(naive_sum / 1e9, 2),
        "dedup_sum_gb": round(dedup_sum / 1e9, 2),
        "unique_layers": n_unique_layers,
        "avg_image_gb": round(naive_sum / max(len(ok_results),1) / 1e9, 2),
        "median_image_gb": round(median / 1e9, 2),
        "p90_image_gb": round(p90 / 1e9, 2),
        "p99_image_gb": round(p99 / 1e9, 2),
        "disk_total_gb": round(disk_total / 1e9, 1),
        "disk_used_gb": round(disk_used / 1e9, 1),
        "disk_free_gb": round(disk_free / 1e9, 1),
        "sufficient": disk_free > dedup_sum * 1.2,
    }
    Path(OUTPUT_FILE).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    detail_file = OUTPUT_FILE.replace(".json", "_detail.json")
    Path(detail_file).write_text(json.dumps([
        {"image": r["image"], "ok": r["ok"], "n_layers": r.get("n_layers",0),
         "total_size_gb": round(r.get("total_size",0)/1e9,3),
         "error": r.get("error","")}
        for r in sorted(results, key=lambda x: x["image"])
    ], indent=2))
    print("\n" + "=" * 60)
    print("SWE-bench Verified -- Docker Image Size Estimation")
    print("=" * 60)
    print(f"Total images:          {report['total_images']}")
    print(f"Manifests fetched OK:  {report['manifests_ok']}")
    print(f"Manifests failed:      {report['manifests_failed']}")
    print(f"Already local:         {report['already_local']}")
    print(f"Unique layers:         {report['unique_layers']}")
    print(f"Naive sum (500x):      {report['naive_sum_gb']} GB")
    print(f"Dedup sum (actual):    {report['dedup_sum_gb']} GB")
    print(f"Avg image size:        {report['avg_image_gb']} GB")
    print(f"Median image size:     {report['median_image_gb']} GB")
    print(f"P90 image size:        {report['p90_image_gb']} GB")
    print(f"P99 image size:        {report['p99_image_gb']} GB")
    print(f"---")
    print(f"Docker Root Dir:       {DOCKER_ROOT}")
    print(f"Disk total:            {report['disk_total_gb']} GB")
    print(f"Disk used:             {report['disk_used_gb']} GB")
    print(f"Disk free:             {report['disk_free_gb']} GB")
    print(f"Sufficient (20% pad):  {'YES' if report['sufficient'] else 'NO'}")
    if fail_results:
        print(f"Failed images:")
        for r in fail_results[:10]:
            print(f"  {r['image']}: {r['error'][:80]}")
    print("=" * 60)
    print(f"Report saved to {OUTPUT_FILE}")
    print(f"Detail saved to {detail_file}")

if __name__ == "__main__":
    main()
