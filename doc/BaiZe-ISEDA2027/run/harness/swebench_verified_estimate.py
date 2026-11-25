#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
swebench_verified_estimate.py — SWE-bench Verified (500) 镜像去重体积估算
仅元数据请求（KB 级），不抢 TB 评测的 layer 下载带宽。
镜像命名: swebench/sweb.eval.x86_64.<instance_id 小写, __ -> _1776_>:latest
走 92.25 代理，匿名 token 鉴权。
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

PROXY = os.environ.get("SWEBENCH_PROXY", "http://172.19.92.25:13128")
PROXIES = {"http": PROXY, "https": PROXY}
REGISTRY = "https://registry-1.docker.io"
AUTH_URL = "https://auth.docker.io/token"
NAMESPACE = "swebench"
ARCH = "x86_64"
TAG = "latest"
DATASET = "princeton-nlp/SWE-bench_Verified"
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST_CACHE = os.path.join(HERE, "swebench_verified_manifests.json")
IMAGE_LIST = os.path.join(HERE, "swebench_verified_image_list.txt")
ACCEPT_LIST = ("application/vnd.oci.image.index.v1+json, "
               "application/vnd.docker.distribution.manifest.list.v2+json")
ACCEPT_MANIFEST = ("application/vnd.oci.image.manifest.v1+json, "
                   "application/vnd.docker.distribution.manifest.v2+json")
sess = requests.Session(); sess.proxies = PROXIES
# datasets / huggingface_hub run in-process -> must set os.environ so they see the proxy
for _k in ("http_proxy","https_proxy","HTTP_PROXY","HTTPS_PROXY"):
    os.environ[_k] = PROXY

def gb(n): return n / (1024 ** 3)

def image_name(instance_id):
    key = f"sweb.eval.{ARCH}.{instance_id}:{TAG}".lower()
    return f"{NAMESPACE}/{key}".replace("__", "_1776_")

def load_instances():
    env = os.environ.copy(); env["https_proxy"]=PROXY; env["http_proxy"]=PROXY
    from datasets import load_dataset
    ds = load_dataset(DATASET, split="test")
    return [r["instance_id"] for r in ds]

def get_token(repo):
    r = sess.get(AUTH_URL, params={"service":"registry.docker.io",
                "scope":f"repository:{repo}:pull"}, timeout=30)
    r.raise_for_status(); return r.json()["token"]

def fetch_manifest(repo, ref, accept, token=None):
    if token is None: token = get_token(repo)
    url = f"{REGISTRY}/v2/{repo}/manifests/{ref}"
    for attempt in range(4):
        r = sess.get(url, headers={"Authorization":f"Bearer {token}","Accept":accept}, timeout=30)
        if r.status_code == 200: return r.json(), token
        if r.status_code == 429:
            wait = 5*(attempt+1); print(f"  [429] {repo} sleep {wait}s",flush=True)
            time.sleep(wait); token = get_token(repo); continue
        if r.status_code == 401: token = get_token(repo); continue
        r.raise_for_status()
    raise RuntimeError(f"failed {repo}@{ref} after retries")

def get_layers(repo):
    idx, _ = fetch_manifest(repo, TAG, ACCEPT_LIST)
    media = idx.get("mediaType","")
    if "manifest" in media and "index" not in media and "list" not in media:
        manifest = idx
    else:
        amd = None
        for m in idx.get("manifests",[]):
            if m.get("platform",{}).get("architecture") in ("amd64","x86_64"): amd=m; break
        if amd is None: return None, "no amd64"
        manifest, _ = fetch_manifest(repo, amd["digest"], ACCEPT_MANIFEST)
    return [(l["digest"], int(l["size"])) for l in manifest.get("layers",[])], None

def load_cache():
    if os.path.exists(MANIFEST_CACHE):
        with open(MANIFEST_CACHE) as f: return json.load(f)
    return {}
def save_cache(cache):
    with open(MANIFEST_CACHE,"w") as f: json.dump(cache, f)


def local_images():
    try:
        out = subprocess.run(["sg","docker","-c",
            'docker images --filter reference=swebench/* --format "{{.Repository}}:{{.Tag}}"'],
            capture_output=True, text=True, timeout=30).stdout
        return set(l.strip() for l in out.splitlines() if l.strip())
    except Exception as e:
        print(f"[warn] docker local check failed: {e}", file=sys.stderr); return set()

def docker_root_free():
    try:
        info = subprocess.run(["sg","docker","-c",
            "docker info --format '{{.DockerRootDir}}'"],
            capture_output=True, text=True, timeout=30).stdout.strip() or "/data/docker"
        df = subprocess.run(["df","-h",info],
            capture_output=True, text=True, timeout=15).stdout.splitlines()
        return info, df[-1] if len(df)>1 else "?"
    except Exception as e:
        return "?", f"err {e}"

def main():
    print(f"=== SWE-bench Verified 镜像去重体积估算  {time.strftime('%F %T')} ===")
    print(f"proxy = {PROXY}\ndataset = {DATASET}")
    ids = load_instances()
    print(f"实例数: {len(ids)}")
    names = {iid: image_name(iid) for iid in ids}
    with open(IMAGE_LIST,"w") as f:
        for iid in ids: f.write(f"{iid}\t{names[iid]}\n")
    print(f"镜像名清单 -> {IMAGE_LIST}")
    cache = load_cache()
    repos = {iid: names[iid].split(":")[0] for iid in ids}
    todo = [iid for iid in ids if iid not in cache]
    print(f"需抓 manifest: {len(todo)}  (缓存命中: {len(ids)-len(todo)})")
    def worker(iid):
        repo = repos[iid]
        try:
            layers, err = get_layers(repo)
            return iid, {"layers": layers, "repo": repo} if not err else {"error":err,"layers":[]}
        except Exception as e:
            return iid, {"error": repr(e)[:200], "layers": []}
    done=0; t0=time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(worker,iid):iid for iid in todo}
        for fut in as_completed(futs):
            iid,res = fut.result(); cache[iid]=res; done+=1
            if res.get("error"):
                print(f"  [{done}/{len(todo)}] {iid} ERROR: {res['error']}",flush=True)
            else:
                sz=sum(s for _,s in res["layers"]); nl=len(res["layers"])
                print(f"  [{done}/{len(todo)}] {iid} layers={nl} sum={gb(sz):.2f}GB",flush=True)
            if done%25==0:
                save_cache(cache); el=time.time()-t0
                print(f"  --- ckpt {done}/{len(todo)} elapsed={el:.0f}s rate={done/max(el,1):.2f}/s ---",flush=True)
    save_cache(cache)
    unique={}; total_raw=0; total_layers=0; ok=0; failed=[]
    for iid in ids:
        entry=cache.get(iid,{}); layers=entry.get("layers",[])
        if entry.get("error") or not layers: failed.append((iid,entry.get("error","no layers"))); continue
        ok+=1
        for dg,sz in layers: unique[dg]=sz; total_raw+=sz; total_layers+=1
    dedup=sum(unique.values()); local=local_images()
    present=sum(1 for iid in ids if names[iid] in local)
    root,dfline=docker_root_free()
    print("\n"+"="*60+"\n体积估算报告\n"+"="*60)
    print(f"总实例数            : {len(ids)}")
    print(f"manifest 抓取成功   : {ok}")
    print(f"manifest 抓取失败   : {len(failed)}")
    print(f"已存在本地镜像      : {present}")
    print(f"缺失需下载          : {len(ids)-present}")
    print(f"总 layer 数(未去重) : {total_layers}")
    print(f"去重后 unique layer : {len(unique)}")
    print(f"共享 layer 数       : {total_layers-len(unique)} ({(total_layers-len(unique))/max(total_layers,1)*100:.1f}%)")
    print(f"sum(size) 未去重    : {gb(total_raw):.1f} GB")
    print(f"去重后实际下载量    : {gb(dedup):.1f} GB")
    print(f"节省比例            : {(total_raw-dedup)/max(total_raw,1)*100:.1f}%")
    print(f"Docker Root Dir     : {root}")
    print(f"磁盘                : {dfline}")
    print(f"\n缓存 -> {MANIFEST_CACHE}\n清单 -> {IMAGE_LIST}")
    if failed:
        print(f"\n失败清单(前20):")
        for iid,err in failed[:20]: print(f"  {iid}: {err}")
    print(f"完成于 {time.strftime('%F %T')}")

if __name__ == "__main__": main()
