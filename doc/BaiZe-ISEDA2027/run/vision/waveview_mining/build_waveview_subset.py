#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build & maintain EDA-Eval-DesignFlow-WaveView.jsonl on 36.15.

Task book §2026-11-17 16:3x user order: autonomously scan the full
EDA-Eval-DesignFlow.jsonl (1647 lines, A/B/C/D shards merged) and produce a
maintained WaveView subset in the SAME directory on 36.15:
  /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/
      EDA-Eval-DesignFlow-WaveView.jsonl

Selection criteria (reproducible, defined here):
  A case enters the WaveView subset iff it satisfies ANY of:
    (K) strict WaveView keyword hit in task_id / prompt / metadata /
        attachments / expected_artifacts on:
        waveform | waveview | fsdb | vcd | eye[-_ ]?diagram | oscilloscope?
        | edge[-_ ]?timing | signal[-_ ]?extract | 波形 | \bwave\b
    (I) a visible (non-hidden) raster image file (png/jpg/jpeg/bmp/gif/tiff)
        exists under assets/<task_id>/ .
  (Having a check.py alone is NOT sufficient -- all 1647 cases have one.)

  image_required (bool) = a visible image file exists under assets/<task_id>/.
        Operational definition: a case requires viewing an image iff an image
        asset is actually provided for it. (Verified: the wave-named cases
        WITHOUT a png -- SimFailDiagnose/SimFailParse/TempSelInfer/
        WaveviewModuleUpdate/WaveViewPanel -- are script/tool/debug tasks
        whose original intent does NOT need reading a raster waveform image;
        their inputs are VCD text / log / Perl / env snapshots. Hence they
        are cataloged as source=text_only, image_required=false.)

  source: original_png | generated_png | text_only | no_check
  baseline_verdict / failure_mode_tier: filled from the sha256-verified
  10-case real run (run/vision/real_waveview_index.json) where available;
  otherwise not_run / unknown (never fabricated).
  failure_mode_tier mapping: designflow A->alpha, B->beta, C->gamma
    (A=did-not-engage, B=engaged-text-only, C=engaged-but-could-not-read-image).

Run ON 36.15 from the EDA-Eval-DesignFlow bench dir.
"""
import json, re, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
MERGED = os.path.join(BENCH, "EDA-Eval-DesignFlow.jsonl")
ASSETS = os.path.join(BENCH, "assets")
REFERENCE = os.path.join(BENCH, "reference")
REAL_INDEX = os.environ.get(
    "WAVEVIEW_REAL_INDEX",
    os.path.join(BENCH, "_real_waveview_index.json"))

KW_RE = re.compile(
    r"waveform|waveview|fsdb|\bvcd\b|eye[\s\-_]?diagram|oscil(?:loscope)?"
    r"|edge[\s\-_]?timing|signal[\s_\-]?extract|波形|\bwave\b", re.IGNORECASE)
IMG_EXT = ("png", "jpg", "jpeg", "bmp", "gif", "tiff", "tif")
TIER_MAP = {"A": "alpha", "B": "beta", "C": "gamma"}
EXCLUDE_NON_WAVEFORM = {
    "EDA-Eval-DesignFlow-IRReportPdf-001":
    "pg_layout IR voltage-drop report task; 14 IR heat-map PNGs but zero "
    "waveform/信号/wave keyword hit; not a waveform-viewing task -> excluded "
    "from V0/V1/V2 waveform experiment per user 'honestly exclude unrelated' "
    "clause (2026-11-17 2nd correction).",
}


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


def visible_images(task_id):
    cdir = os.path.join(ASSETS, task_id)
    out = []
    if not os.path.isdir(cdir):
        return out
    for fn in sorted(os.listdir(cdir)):
        full = os.path.join(cdir, fn)
        if os.path.isdir(full) or fn.lower().startswith("hidden"):
            continue
        if fn.lower().rsplit(".", 1)[-1] in IMG_EXT:
            out.append(os.path.relpath(full, BENCH))
    return out


def check_info(task_id):
    p = os.path.join(REFERENCE, task_id, "check.py")
    if not os.path.exists(p):
        return False, 0
    try:
        src = open(p, encoding="utf-8", errors="ignore").read()
    except Exception:
        return True, 0
    n = len(re.findall(r"^\s*assert\b", src, re.MULTILINE))
    n += len(re.findall(r"^\s*if\b", src, re.MULTILINE))
    return True, n


def real_index_map():
    try:
        idx = json.load(open(REAL_INDEX, encoding="utf-8"))
    except Exception:
        return {}
    m = {}
    for ci in idx.get("cases", []):
        cid = ci.get("case_id")
        if not cid:
            continue
        tier = ci.get("baseline", {}).get("failure_mode_tier")
        m[cid] = {"verdict": ci.get("baseline", {}).get("verdict", "FAIL"),
                  "tier": TIER_MAP.get(tier, "unknown"),
                  "tag": ci.get("id")}
    return m


def main():
    smap = shard_map()
    rmap = real_index_map()
    print(f"[shard_map] {len(smap)} task_ids; [real_index] {len(rmap)} verified cases")
    rows = []
    n_total = n_sel = n_kw = n_img = n_orig = n_text = n_nocheck = n_nonwf = 0
    with open(MERGED, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_total += 1
            try:
                d = json.loads(line)
            except Exception:
                continue
            tid = d.get("task_id") or d.get("id") or d.get("case_id") or f"line{n_total}"
            blob = text_of(d, "task_id", "prompt", "metadata", "attachments",
                           "expected_artifacts", "entry_point")
            kw = KW_RE.search(blob)
            imgs = visible_images(tid)
            has_check, k_cond = check_info(tid)
            if not (kw or imgs):
                continue
            n_sel += 1
            wf_rel = bool(kw)
            if kw:
                n_kw += 1
            if imgs:
                n_img += 1
            meta = d.get("metadata") or {}
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta.replace("'", '"'))
                except Exception:
                    meta = {}
            domain = meta.get("domain") if isinstance(meta, dict) else None
            task_name = meta.get("task_name") if isinstance(meta, dict) else None
            exclusion_reason = None
            if imgs and not wf_rel:
                source = "image_only_non_waveform"; n_nonwf += 1
                exclusion_reason = EXCLUDE_NON_WAVEFORM.get(
                    tid, "has visible image but no waveform keyword; not a "
                    "waveform-viewing task -> excluded from V0/V1/V2.")
            elif imgs:
                source = "original_png"; n_orig += 1
            elif not has_check:
                source = "no_check"; n_nocheck += 1
            else:
                source = "text_only"; n_text += 1
            real = rmap.get(tid, {})
            rows.append({
                "task_id": tid,
                "shard": smap.get(tid, "?"),
                "domain": domain,
                "task_name": task_name,
                "waveform_relevant": wf_rel,
                "image_required": bool(imgs),
                "image_path": imgs,
                "has_check": has_check,
                "k_conditions": k_cond,
                "kw_match": kw.group(0) if kw else None,
                "baseline_verdict": real.get("verdict", "not_run"),
                "failure_mode_tier": real.get("tier", "unknown"),
                "source": source,
                "exclusion_reason": exclusion_reason,
                "vqa_runnable": wf_rel and bool(imgs) and has_check,
            })
    rows.sort(key=lambda r: (not r["vqa_runnable"], r["shard"], r["task_id"]))
    out = os.path.join(BENCH, "EDA-Eval-DesignFlow-WaveView.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_run = sum(1 for r in rows if r["vqa_runnable"])
    n_wf = sum(1 for r in rows if r["waveform_relevant"])
    print(f"[scan] total={n_total} selected={n_sel} waveform_relevant={n_wf} "
          f"kw_hit={n_kw} with_image={n_img}")
    print(f"[source] original_png={n_orig} text_only={n_text} "
          f"no_check={n_nocheck} image_only_non_waveform={n_nonwf}")
    print(f"[vqa_runnable] {n_run} (waveform_relevant & image_required & has_check)")
    print(f"[wrote] {out} ({len(rows)} lines)")
    print("\n=== vqa_runnable (waveform_relevant & image_required & has_check) ===")
    for r in rows:
        if r["vqa_runnable"]:
            print(f"  [{r['shard']}] {r['task_id']}  dom={r['domain']}  "
                  f"k={r['k_conditions']}  verdict={r['baseline_verdict']}  "
                  f"tier={r['failure_mode_tier']}  img={r['image_path']}")
    print("\n=== image_only_non_waveform (excluded from V0/V1/V2) ===")
    for r in rows:
        if r["source"] == "image_only_non_waveform":
            print(f"  [{r['shard']}] {r['task_id']}  dom={r['domain']}  "
                  f"reason={r['exclusion_reason'][:80]}")


if __name__ == "__main__":
    main()
