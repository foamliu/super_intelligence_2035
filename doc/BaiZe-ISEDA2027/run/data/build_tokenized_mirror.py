#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_tokenized_mirror.py — 把已分词产物整理成「镜像下载目录」的布局（零拷贝）.

运维令 2026-10-25 12:5x ①：新根
  /nas_train/app.e0031982/datasets/baize-data/tokenized/
路径镜像 HF 下载目录。只许 hardlink（同盘）/ symlink（跨盘），禁 cp/mv/rm。

规则（仲裁表 2026-10-25 13:3x）：
  - env14_* 与 ufw_*_train_s* 在 /nas_train（与 tokenized/ 同盘）⇒ hardlink
  - full_* 真身在 /nas_env（跨盘）⇒ symlink（指向 /nas_env 上的绝对路径）
  - 正在写入的 shard：仅当 .bin/.idx/.json 三件套齐全才链接（.json 最后写）

产出：每目录 MANIFEST.json + 顶层 INDEX.tsv + 终端校验结果。
幂等：已存在的同名链接（hardlink 同 inode / symlink 同 target）跳过。
"""
import os, sys, json, datetime

ROOT = "/nas_train/app.e0031982/datasets/baize-data/tokenized"
TEXT_DIR = "/nas_train/app.e0031982/datasets/baize-data/text"
TOKENIZER = "DeepSeek-V4.1-Flash int32 (tokenizer_eod, vocab=129281, pad=129408)"
EXTS = (".bin", ".idx", ".json")

ENTRIES = [
    {"tok_subdir": "Ultra-FineWeb/ultrafineweb_en_v1_4", "src_dir": TEXT_DIR, "glob_pfx": "env14_", "dl_dir": "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4", "hf_repo": "openbmb/Ultra-FineWeb", "subdir": "ultrafineweb_en_v1_4", "storage": "hardlink"},
    {"tok_subdir": "Ultra-FineWeb-L3/ultrafineweb_en_l3/qa", "src_dir": "/nas_env/app.e0031982/baize-data/full_ufw_l3", "glob_pfx": "ufw_l3_train_s", "dl_dir": "/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa", "hf_repo": "openbmb/Ultra-FineWeb-L3", "subdir": "ultrafineweb_en_l3/qa", "storage": "symlink"},
    {"tok_subdir": "UltraData-Code/UltraData-Code-L2", "src_dir": "/nas_env/app.e0031982/baize-data/full_ultradata_code_l2", "glob_pfx": "", "dl_dir": "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L2", "hf_repo": "openbmb/UltraData-Code", "subdir": "UltraData-Code-L2", "storage": "symlink"},
    {"tok_subdir": "UltraData-Code/UltraData-Code-L3", "src_dir": "/nas_env/app.e0031982/baize-data/full_ultradata_code_l3", "glob_pfx": "", "dl_dir": "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3", "hf_repo": "openbmb/UltraData-Code", "subdir": "UltraData-Code-L3", "storage": "symlink"},
    {"tok_subdir": "UltraData-Math/UltraData-Math-L1", "src_dir": "/nas_env/app.e0031982/baize-data/full_ultradata_math_l1", "glob_pfx": "", "dl_dir": "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L1", "hf_repo": "openbmb/UltraData-Math", "subdir": "UltraData-Math-L1", "storage": "symlink"},
    {"tok_subdir": "UltraData-Math/UltraData-Math-L3", "src_dir": "/nas_env/app.e0031982/baize-data/full_ultradata_math_l3", "glob_pfx": "", "dl_dir": "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L3", "hf_repo": "openbmb/UltraData-Math", "subdir": "UltraData-Math-L3", "storage": "symlink"},
    {"tok_subdir": "Ultra-FineWeb/ultrafineweb_en", "src_dir": TEXT_DIR, "glob_pfx": "ufw_en_train_s", "dl_dir": "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en", "hf_repo": "openbmb/Ultra-FineWeb", "subdir": "ultrafineweb_en", "storage": "hardlink"},
    {"tok_subdir": "Ultra-FineWeb/ultrafineweb_l1_en_hq", "src_dir": "/nas_env/app.e0031982/baize-data/full_ufw_l1_en_hq", "glob_pfx": "ufw_l1_en_hq_train_s", "dl_dir": "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq", "hf_repo": "openbmb/Ultra-FineWeb", "subdir": "ultrafineweb_l1_en_hq", "storage": "symlink"},
    {"tok_subdir": "Ultra-FineWeb/ultrafineweb_zh", "src_dir": "/nas_env/app.e0031982/baize-data/full_ufw_zh", "glob_pfx": "ufw_zh_train_s", "dl_dir": "/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_zh", "hf_repo": "openbmb/Ultra-FineWeb", "subdir": "ultrafineweb_zh", "storage": "symlink"},
    {"tok_subdir": "UltraX-Preview/UltraX-AICC", "src_dir": "/nas_env/app.e0031982/baize-data/full_ultrax_aicc", "glob_pfx": "ultrax_aicc_train_s", "dl_dir": "/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/UltraX-AICC", "hf_repo": "openbmb/UltraX-Preview", "subdir": "UltraX-AICC", "storage": "symlink"},
]

def err(m): print("  [ERR] "+m, file=sys.stderr)

def list_shards(src_dir, glob_pfx):
    bases=[]
    try: names=os.listdir(src_dir)
    except OSError as e: err("listdir %s: %s"%(src_dir,e)); return bases
    for n in names:
        if n.endswith(".bin") and n.startswith(glob_pfx): bases.append(n[:-4])
    return sorted(bases)

def read_num_tokens(p):
    try:
        with open(p) as f: d=json.load(f)
        return int(d.get("num_tokens",0))
    except Exception as e: err("num_tokens %s: %s"%(p,e)); return None

def make_hardlink(src,dst):
    if os.path.exists(dst) or os.path.islink(dst):
        try:
            if os.stat(src).st_ino==os.stat(dst).st_ino: return "skip"
        except OSError: pass
        err("hardlink dst diff inode: %s"%dst); return "fail"
    try: os.link(src,dst); return "ok"
    except OSError as e: err("hardlink %s: %s"%(dst,e)); return "fail"

def make_symlink(target,dst):
    if os.path.islink(dst):
        if os.readlink(dst)==target: return "skip"
        err("symlink dst diff target: %s"%dst); return "fail"
    if os.path.exists(dst): err("symlink dst exists: %s"%dst); return "fail"
    try: os.symlink(target,dst); return "ok"
    except OSError as e: err("symlink %s: %s"%(dst,e)); return "fail"

def process_entry(e):
    tok_dir=os.path.join(ROOT,e["tok_subdir"])
    os.makedirs(tok_dir,exist_ok=True)
    src_dir=e["src_dir"]; storage=e["storage"]
    bases=list_shards(src_dir,e["glob_pfx"])
    linked=skipped=failed=bad=0
    shards_info=[]; tokens_total=0; bytes_total=0
    for base in bases:
        if not all(os.path.exists(os.path.join(src_dir,base+x)) for x in EXTS): continue
        nt=read_num_tokens(os.path.join(src_dir,base+".json"))
        if nt is None: bad+=1; continue
        sb=0
        for ext in EXTS:
            sp=os.path.join(src_dir,base+ext); dp=os.path.join(tok_dir,base+ext)
            if storage=="hardlink": r=make_hardlink(sp,dp)
            else: r=make_symlink(os.path.realpath(sp),dp)
            if r=="fail": failed+=1
            elif r=="skip": skipped+=1
            else: linked+=1
            try: sb+=os.path.getsize(sp)
            except OSError: pass
        shards_info.append({"name":base,"tokens":nt,"bytes":sb})
        tokens_total+=nt; bytes_total+=sb
    _ls=os.listdir(tok_dir)
    nb=len([f for f in _ls if f.endswith(".bin")])
    ni=len([f for f in _ls if f.endswith(".idx")])
    nj=len([f for f in _ls if f.endswith(".json") and f!="MANIFEST.json"])
    tri="OK" if nb==ni==nj else "MISMATCH(bin=%d idx=%d json=%d)"%(nb,ni,nj)
    iok=ibad=0
    for si in shards_info:
        base=si["name"]
        try:
            if storage=="hardlink":
                if os.stat(os.path.join(src_dir,base+".bin")).st_ino==os.stat(os.path.join(tok_dir,base+".bin")).st_ino: iok+=1
                else: ibad+=1
            else:
                if os.path.realpath(os.path.join(src_dir,base+".bin"))==os.readlink(os.path.join(tok_dir,base+".bin")): iok+=1
                else: ibad+=1
        except OSError as ex: ibad+=1; err("verify %s: %s"%(base,ex))
    manifest={"tokenized_dir":tok_dir,"download_dir":e["dl_dir"],"hf_repo":e["hf_repo"],"subdir":e["subdir"],"shards":shards_info,"shards_count":len(shards_info),"tokens_total":tokens_total,"bytes_total":bytes_total,"tokenizer":TOKENIZER,"storage":storage,"created":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"verify":{"triplet":tri,"link_integrity_ok":iok,"link_integrity_bad":ibad,"num_tokens_unparseable":bad}}
    with open(os.path.join(tok_dir,"MANIFEST.json"),"w",encoding="utf-8") as f: json.dump(manifest,f,ensure_ascii=False,indent=2)
    print("[%s] shards=%d linked=%d skipped=%d failed=%d bad=%d | tok=%.4fB %.2fGB | tri=%s iok=%d/%d"%(e["tok_subdir"],len(shards_info),linked,skipped,failed,bad,tokens_total/1e9,bytes_total/1e9,tri,iok,iok+ibad))
    return {"tokenized_dir":tok_dir,"download_dir":e["dl_dir"],"shards":len(shards_info),"tokens":tokens_total,"bytes":bytes_total,"tokenizer":TOKENIZER,"storage":storage,"triplet":tri,"inode_ok":iok,"inode_bad":ibad}

def main():
    os.makedirs(ROOT,exist_ok=True)
    print("== build_tokenized_mirror.py ROOT=%s =="%ROOT)
    res=[process_entry(e) for e in ENTRIES]
    idx=os.path.join(ROOT,"INDEX.tsv")
    with open(idx,"w",encoding="utf-8",newline="\n") as f:
        f.write("tokenized_dir\tdownload_dir\tshards\ttokens\tbytes\ttokenizer\tstorage\ttriplet\tinode_ok\tinode_bad\n")
        ts=tt=tb=0
        for r in res:
            f.write("\t".join(str(x) for x in [r["tokenized_dir"],r["download_dir"],r["shards"],r["tokens"],r["bytes"],r["tokenizer"],r["storage"],r["triplet"],r["inode_ok"],r["inode_bad"]])+"\n")
            ts+=r["shards"]; tt+=r["tokens"]; tb+=r["bytes"]
        f.write("\t".join(["TOTAL","",str(ts),str(tt),str(tb),"","","","",""])+"\n")
    print("\n== INDEX.tsv: %s =="%idx)
    print("TOTAL shards=%d tokens=%.4fB bytes=%.2fGB"%(ts,tt/1e9,tb/1e9))
    print("VERIFY tri:%s inode:%s"%("ALL OK" if all(r["triplet"]=="OK" for r in res) else "MISMATCH","ALL OK" if all(r["inode_bad"]==0 for r in res) else "BAD"))
    print("\n== find tokenized -maxdepth 3 -type d ==")
    for dp,dns,_ in os.walk(ROOT):
        if dp[len(ROOT):].count(os.sep)<=3: print(dp)

if __name__=="__main__": main()
