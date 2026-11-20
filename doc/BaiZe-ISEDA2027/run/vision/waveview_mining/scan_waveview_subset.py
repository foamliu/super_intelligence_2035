#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan EDA-Eval-DesignFlow.jsonl (1647 lines, A/B/C/D shards merged) on 36.15
and filter WaveView-related cases (task book §2026-11-17 16:3x user order).
Run ON 36.15 from the EDA-Eval-DesignFlow bench dir."""
import json, re, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
MERGED = os.path.join(BENCH, "EDA-Eval-DesignFlow.jsonl")
ASSETS = os.path.join(BENCH, "assets")

KW_RE = re.compile(
    r"waveform|waveview|fsdb|\bvcd\b|eye[\s\-_]?diagram|oscil(?:loscope)?"
    r"|edge[\s\-_]?timing|signal[\s_\-]?extract|\bwave\b", re.IGNORECASE)
IMG_RE = re.compile(r"\.(png|jpe?g|bmp|gif|tiff?|svg)$", re.IGNORECASE)


def shard_map():
    m = {}
    for s in "ABCD":
        p = os.path.join(BENCH, f"EDA-Eval-DesignFlow_{s}.jsonl")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                tid = d.get("task_id") or d.get("id") or d.get("case_id")
                if tid:
                    m[tid] = s
    return m


def attachments_images(att):
    imgs = []
    if not att:
        return imgs
    a = att
    if isinstance(a, str):
        try:
            a = json.loads(a.replace("'", '"'))
        except Exception:
            a = [a]
    for x in a:
        if isinstance(x, dict):
            name = x.get("name") or x.get("source") or x.get("path") or ""
            if name and IMG_RE.search(name):
                imgs.append(name)
        elif isinstance(x, str) and IMG_RE.search(x):
            imgs.append(x)
    return imgs


def has_image_on_disk(task_id, imgs):
    found = []
    for name in imgs:
        cands = [os.path.join(ASSETS, name),
                 os.path.join(ASSETS, task_id, name),
                 os.path.join(ASSETS, task_id.replace("/", "_"), name)]
        for c in cands:
            if os.path.exists(c):
                found.append(c)
                break
    return found


def count_conditions(test_src):
    if not test_src:
        return 0
    if not isinstance(test_src, str):
        test_src = str(test_src)
    n = len(re.findall(r"^\s*assert\b", test_src, re.MULTILINE))
    n += len(re.findall(r"^\s*if\b", test_src, re.MULTILINE))
    return n


def text_of(d, *keys):
    parts = []
    for k in keys:
        v = d.get(k)
        if v is None:
            continue
        if isinstance(v, (dict, list)):
            try:
                parts.append(json.dumps(v, ensure_ascii=False))
            except Exception:
                parts.append(str(v))
        else:
            parts.append(str(v))
    return "\n".join(parts)


def main():
    smap = shard_map()
    print(f"[shard_map] {len(smap)} task_ids mapped to A/B/C/D")
    rows = []
    n_total = 0
    n_kw = 0
    with open(MERGED, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_total += 1
            try:
                d = json.loads(line)
            except Exception as e:
                print(f"[warn] line {n_total} parse fail: {e}")
                continue
            tid = d.get("task_id") or d.get("id") or d.get("case_id") or f"line{n_total}"
            blob = text_of(d, "task_id", "prompt", "metadata", "attachments",
                           "expected_artifacts", "entry_point")
            kw_hit = KW_RE.search(blob)
            imgs = attachments_images(d.get("attachments"))
            img_on_disk = has_image_on_disk(tid, imgs)
            has_check = bool(d.get("test"))
            k_cond = count_conditions(d.get("test"))
            shard = smap.get(tid, "?")
            meta = d.get("metadata") or {}
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta.replace("'", '"'))
                except Exception:
                    meta = {}
            domain = meta.get("domain") if isinstance(meta, dict) else None
            task_name = meta.get("task_name") if isinstance(meta, dict) else None
            row = {"task_id": tid, "shard": shard, "domain": domain,
                   "task_name": task_name, "kw_hit": bool(kw_hit),
                   "kw_match": kw_hit.group(0) if kw_hit else None,
                   "image_required": bool(imgs) or bool(kw_hit),
                   "image_names": imgs,
                   "image_on_disk": [os.path.relpath(p, BENCH) for p in img_on_disk],
                   "has_png": bool(img_on_disk), "has_check": has_check,
                   "k_conditions": k_cond}
            rows.append(row)
            if kw_hit:
                n_kw += 1
    n_img = sum(1 for r in rows if r["has_png"])
    n_check = sum(1 for r in rows if r["has_check"])
    n_kw_check = sum(1 for r in rows if r["kw_hit"] and r["has_check"])
    n_kw_img = sum(1 for r in rows if r["kw_hit"] and r["has_png"])
    n_kw_img_check = sum(1 for r in rows if r["kw_hit"] and r["has_png"] and r["has_check"])
    print(f"[scan] total={n_total} kw_hit={n_kw} has_png={n_img} has_check={n_check}")
    print(f"[scan] kw&check={n_kw_check} kw&png={n_kw_img} kw&png&check={n_kw_img_check}")
    out = os.path.join(BENCH, "waveview_scan_candidates.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"total": n_total, "kw_hit": n_kw, "rows": rows}, f, ensure_ascii=False, indent=1)
    print(f"[wrote] {out}")
    print("\n=== candidates (kw_hit & has_check) ===")
    cands = [r for r in rows if r["kw_hit"] and r["has_check"]]
    cands.sort(key=lambda r: (not r["has_png"], r["shard"], r["task_id"]))
    for r in cands:
        png = "PNG" if r["has_png"] else "noPng"
        print(f"  [{r['shard']}] {r['task_id']}  kw={r['kw_match']!r}  {png}  k={r['k_conditions']}  dom={r['domain']}  name={(r['task_name'] or '')[:50]}")


if __name__ == "__main__":
    main()
