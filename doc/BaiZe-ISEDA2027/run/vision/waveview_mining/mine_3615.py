#!/usr/bin/env python3
import json, os, hashlib, re

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
SHARDS = ["A", "B", "C", "D"]
IMG_EXT = (".png", ".jpg", ".jpeg", ".svg", ".bmp", ".gif", ".webp")
KW = ["wave", "fsdb", "vcd", "wlf", "waveform", "waveview", "\xe6\xb3\xa2\xe5\xbd\xa2",
      "eye", "transient", "sweep", "duty", "jitter"]
VB_SIGNALS = ["wv ", "wv\t", "FineSim", "finesim", "vcs ", "vcs\n", "irun",
              "xrun", "verdi", "nWave", ".fsdb", ".vcd", ".wlf", "vsim",
              "questasim", "ncsim", "simv", "run_sim", "run_vcs", "vcd2fsdb",
              "fsdbextract"]
VA_SIGNALS = ["wv_summary", ".csv", "answer", "deliverable", "oracle",
              "EXPECTED", "read_csv", "json.loads", "DictReader", "_cond("]

def sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return "ERR:%s" % e

def list_visible_images(case_id):
    adir = os.path.join(BASE, "assets", case_id)
    out = []
    if not os.path.isdir(adir):
        return out, False
    for name in sorted(os.listdir(adir)):
        full = os.path.join(adir, name)
        if os.path.isfile(full) and name.lower().endswith(IMG_EXT):
            out.append({"filename": name, "sha256": sha256_file(full),
                        "rel_path": "assets/%s/%s" % (case_id, name)})
    return out, True

def count_conds(check_src):
    n_cond_call = len(re.findall(r"_cond\s*\(", check_src)) - (1 if re.search(r"def\s+_cond\s*\(", check_src) else 0)
    n_assert = len(re.findall(r"\bassert\s+", check_src))
    n_if = len(re.findall(r"^\s*if\s+", check_src, re.M))
    k = n_cond_call if n_cond_call > 0 else (n_assert if n_assert else n_if)
    return {"n_cond_call": n_cond_call, "n_assert": n_assert, "n_if": n_if, "k_conditions": k}

def classify_vab(check_src, prompt, expected_artifacts, metadata):
    low = check_src.lower()
    arts = [str(a).lower() for a in (expected_artifacts or [])]
    vb_hits = [s.strip() for s in VB_SIGNALS if s.strip().lower() in low]
    needs_sim_artifact = any(("vcd" in a or "fsdb" in a or "wlf" in a or "wave" in a) for a in arts)
    va_hits = [s for s in VA_SIGNALS if s.lower() in low]
    has_answer_deliverable = any(("csv" in a or "answer" in a or "summary" in a or ".json" in a) for a in arts)
    entry_answer = ("submit.zip" in low and ("wv_summary" in low or "csv" in low))
    # strong V-A: restored image-required answer-validation form
    va_strong = any(t in low for t in ["answer-validation", "answer-deliverable",
                                       "deliverable is an answer", "not a parsing script",
                                       "restored form", "image-required restoration"])
    # V-B: the SUT deliverable is itself a script that must execute in an EDA sandbox
    vb_strong = any(t in low for t in ["candidate script runs", "candidate runs on hidden",
                                       "runs the candidate", "execute the candidate",
                                       "subprocess.run(.*sim", "finesim_deck", "run_vcs"])
    if va_strong and not vb_strong:
        return "A", "restored-answer-validation"
    if (needs_sim_artifact and not has_answer_deliverable) and vb_hits and not va_strong:
        return "B", "needs-sim-artifact+vbsignals(%s)" % ",".join(vb_hits[:4])
    if has_answer_deliverable or entry_answer or ("wv_summary" in low and "csv" in low):
        return "A", "answer-deliverable-validated"
    if vb_hits and not va_hits:
        return "B", "vbsignals-only(%s)" % ",".join(vb_hits[:4])
    if va_hits and not vb_hits:
        return "A", "vasignals-only(%s)" % ",".join(va_hits[:4])
    return "UNCLEAR", "ambiguous(va=%d,vb=%d)" % (len(va_hits), len(vb_hits))

def asset_fidelity(check_src, metadata, has_real_png, image_list):
    low = check_src.lower()
    md = metadata or {}
    notes = str(md.get("restoration_notes", "")) + " " + str(md.get("note", ""))
    if "image-required restoration" in low or "restored form" in low or "restoration" in notes.lower():
        if "reframe" in notes.lower() or "reframe" in low:
            return "synthesized-reframe"
        return "synthesized-image-restored"
    if has_real_png:
        return "real-private"
    return "synthesized-reframe" if image_list else "image_missing"

def main():
    results = []
    stats = {"total": 0, "per_shard": {}}
    for shard in SHARDS:
        p = os.path.join(BASE, "EDA-Eval-DesignFlow_%s.jsonl" % shard)
        n = 0
        with open(p) as f:
            for li, line in enumerate(f, 1):
                if not line.strip():
                    continue
                stats["total"] += 1
                n += 1
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                tid = d.get("task_id", "")
                md = d.get("metadata", {}) or {}
                domain = str(md.get("domain", ""))
                task_name = str(md.get("task_name", ""))
                scenario = str(md.get("scenario", ""))
                prompt = d.get("prompt", "") or ""
                test_src = d.get("test", "") or ""
                arts = d.get("expected_artifacts", []) or []
                attach_names = " ".join(str(a.get("name", "")) if isinstance(a, dict) else str(a) for a in (d.get("attachments", []) or []))
                hay = " ".join([str(tid), str(domain), str(task_name), str(scenario), str(prompt), str(test_src), str(attach_names)]).lower()
                kw_hits = [k for k in KW if k.lower() in hay]
                is_wave = (domain.lower() == "waveform") or bool(kw_hits)
                if not is_wave:
                    continue
                check_path = os.path.join(BASE, "reference", tid, "check.py")
                check_exists = os.path.isfile(check_path)
                if check_exists:
                    with open(check_path) as cf:
                        check_src_full = cf.read()
                    check_sha = sha256_file(check_path)
                else:
                    check_src_full = test_src
                    check_sha = ""
                cond = count_conds(check_src_full)
                imgs, asset_dir_exists = list_visible_images(tid)
                vtype, vreason = classify_vab(check_src_full, prompt, arts, md)
                fidelity = asset_fidelity(check_src_full, md, bool(imgs), imgs)
                results.append({
                    "case_id": tid, "source_pool": shard, "pool_line": li,
                    "shard_jsonl": "EDA-Eval-DesignFlow_%s.jsonl" % shard,
                    "domain": domain, "task_name": task_name, "scenario": scenario,
                    "difficulty": md.get("difficulty", ""),
                    "check_path_3615": check_path, "check_exists": check_exists,
                    "sha256_check": check_sha, "k_conditions": cond["k_conditions"],
                    "cond_detail": cond, "expected_artifacts": arts,
                    "image_paths": [im["filename"] for im in imgs],
                    "image_inventory": imgs, "image_count": len(imgs),
                    "image_missing": (len(imgs) == 0), "asset_fidelity": fidelity,
                    "vision_run_type": vtype, "vab_reason": vreason,
                    "keyword_hits": kw_hits,
                    "restoration_notes": md.get("restoration_notes", ""),
                    "legacy_source_file": md.get("legacy_source_file", ""),
                    "prompt_len": len(prompt),
                })
        stats["per_shard"][shard] = n
    print(json.dumps({"base_dir_3615": BASE, "stats": stats, "candidates": results}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
