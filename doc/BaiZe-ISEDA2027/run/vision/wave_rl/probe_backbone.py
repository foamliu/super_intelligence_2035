#!/usr/bin/env python
"""probe_backbone.py — 定位 / 抽取纯文本 Qwen3 系 backbone（.17 就地重生成 Stage-1W 专用）。

背景（用户令 2026-11-19，Option B）
----------------------------------
vision 线 Stage-1W SFT 需要一个 **纯文本 Qwen3 系 backbone**（~1.7–2B）。历史产物在
``/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted``，
但 **.12 → .17 无网络**、.17 上 ``/nas_train`` 不可用 ⇒ 无法 rsync，只能在 .17 就地重生成。

``extract_qwen3vl_2b_text.py``（wake#620）只认单文件 ``model.safetensors`` 且写死
``model.language_model.`` 前缀，覆盖不了 .17 上可能存在的其他布局（分片权重、
``language_model.*``、纯文本 Qwen3 / Qwen3.5）。本脚本是它的**超集**：

  * ``--scan``    只读探测若干根目录，判定每个 HF 模型目录属于哪一类，给出该走哪条路；
  * ``--prepare`` 按判定结果就地生成纯文本 checkpoint（config 重映射 + 权重抽前缀 +
                  tokenizer 拷贝），**支持单文件与 sharded safetensors**。

判定规则（保守，不猜）
--------------------
1. 权重带 ``model.language_model.`` 前缀           → ``STRIP_LLM``（复制时去该前缀）
2. 权重带 ``language_model.`` 前缀                 → ``STRIP_LM``
3. 权重含视觉张量（``visual.`` / ``vision_tower.``）且无 language_model 前缀
                                                   → ``SKIP``（不支持，宁可 BLOCKED 不编造）
4. 其余（纯文本 CausalLM 权重）                     → ``DIRECT``（只做 config 重映射）

输出
----
人类可读日志 + 可选 ``--json-out``；``--prepare/--autoprepare`` 末尾恒打印一行
``READY <path>`` 或 ``BLOCKED <reason>``，**退出码恒 0**（与项目 BLOCKED-guard 约定一致）。

用法
----
    python probe_backbone.py --scan --roots /nas_data/app.e0031982 /H100_train/app.e0031982
    python probe_backbone.py --prepare --src <model_dir> --out <out_dir> [--verify]
    python probe_backbone.py --autoprepare --out <out_dir> --roots <r1> <r2> ...

作者：vision wake#1683（2026-11-19，Option B 落地）。License: project-internal.
"""
import argparse
import glob
import json
import os
import shutil
import sys

TOKENIZER_FILES = [
    "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
    "special_tokens_map.json", "added_tokens.json", "chat_template.json",
    "chat_template.jinja", "generation_config.json",
]
PREFIX_LLM = "model.language_model."
PREFIX_LM = "language_model."
VISION_MARKERS = ("visual.", "vision_tower.", "model.visual.", "model.vision_tower.")
CONFIG_DROP = (
    "vision_config", "image_token_id", "video_token_id",
    "vision_start_token_id", "vision_end_token_id",
)


# --------------------------------------------------------------------------
# 权重文件 / key 探测
# --------------------------------------------------------------------------
def weight_files(model_dir):
    """返回该目录的权重文件列表（优先读 index json 的 weight_map）。"""
    idx = os.path.join(model_dir, "model.safetensors.index.json")
    if os.path.isfile(idx):
        try:
            with open(idx) as f:
                wm = json.load(f).get("weight_map", {})
            files = sorted({os.path.join(model_dir, v) for v in wm.values()})
            files = [f for f in files if os.path.isfile(f)]
            if files:
                return files
        except Exception as e:                                     # noqa: BLE001
            print(f"  [warn] index json 解析失败({e})，回退 glob")
    return sorted(f for f in glob.glob(os.path.join(model_dir, "*.safetensors"))
                  if os.path.isfile(f))


def sample_keys(files, limit=20000):
    """从权重文件抽样 key（只读 header，不加载张量）。"""
    try:
        from safetensors import safe_open
    except ImportError:                                            # pragma: no cover
        return [], "safetensors 未安装"
    keys = []
    for path in files:
        try:
            with safe_open(path, "pt") as f:
                for k in f.keys():
                    keys.append(k)
                    if len(keys) >= limit:
                        return keys, None
        except Exception as e:                                     # noqa: BLE001
            return keys, f"读取 {path} 失败: {e}"
    return keys, None


def classify(keys, cfg):
    """按 key 前缀判定抽取方式，返回 (method, prefix, reason)。"""
    if not keys:
        return "SKIP", None, "读不到任何权重 key（safetensors 缺失或损坏）"

    def _starts(pref):
        return any(k.startswith(pref) for k in keys)

    if _starts(PREFIX_LLM):
        return "STRIP_LLM", PREFIX_LLM, "权重带 model.language_model. 前缀"
    if _starts(PREFIX_LM):
        return "STRIP_LM", PREFIX_LM, "权重带 language_model. 前缀"
    if any(_starts(v) for v in VISION_MARKERS):
        return "SKIP", None, "权重含视觉张量且无 language_model 前缀（架构不支持抽取）"
    if "text_config" in cfg:
        return "DIRECT", None, "config 含 text_config 但权重已是纯文本"
    return "DIRECT", None, "纯文本权重"


def inspect(model_dir):
    """探测单个目录，返回结构化结论（不写任何文件）。"""
    cfg_path = os.path.join(model_dir, "config.json")
    info = {"path": os.path.abspath(model_dir), "ok": False}
    if not os.path.isfile(cfg_path):
        info["reason"] = "无 config.json"
        return info
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except Exception as e:                                         # noqa: BLE001
        info["reason"] = f"config.json 解析失败: {e}"
        return info

    wf = weight_files(model_dir)
    keys, perr = sample_keys(wf)
    method, prefix, reason = classify(keys, cfg)
    tc = cfg.get("text_config") or {}

    info.update({
        "ok": method != "SKIP" and bool(wf) and perr is None,
        "reason": perr or reason,
        "method": method,
        "prefix": prefix,
        "model_type": cfg.get("model_type"),
        "text_model_type": tc.get("model_type"),
        "architectures": cfg.get("architectures"),
        "multimodal": bool("vision_config" in cfg or tc),
        "hidden_size": tc.get("hidden_size") or cfg.get("hidden_size"),
        "num_hidden_layers": tc.get("num_hidden_layers") or cfg.get("num_hidden_layers"),
        "n_weight_files": len(wf),
        "n_keys_sampled": len(keys),
        "has_tokenizer": os.path.isfile(os.path.join(model_dir, "tokenizer.json")),
        "size_gb": round(sum(os.path.getsize(f) for f in wf) / 1e9, 2) if wf else 0.0,
    })
    return info


def scan(roots, max_depth=4, max_dirs=600):
    """在 roots 下广度受限地找 HF 模型目录（含 config.json）。"""
    found, seen = [], 0
    for root in roots:
        root = os.path.expanduser(root)
        if not os.path.isdir(root):
            print(f"  [skip] 不存在: {root}")
            continue
        base_depth = root.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root):
            seen += 1
            if seen > max_dirs:
                print(f"  [warn] 目录数超过 {max_dirs}，停止扫描 {root}")
                break
            if (dirpath.count(os.sep) - base_depth) >= max_depth:
                dirnames[:] = []
            # 跳过大体积非模型目录，避免 NFS 上无意义遍历
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", "blobs")
                           and not d.startswith(".cache")]
            if "config.json" in filenames:
                found.append(dirpath)
    return found


# --------------------------------------------------------------------------
# 抽取 / 重映射
# --------------------------------------------------------------------------
def build_config(src_cfg, method, out_dir):
    """写出纯文本 config：优先 text_config；去掉视觉相关键；规范化 model_type。"""
    if "text_config" in src_cfg:
        base = dict(src_cfg["text_config"])
        archs = base.get("architectures") or src_cfg.get("architectures")
    else:
        base = dict(src_cfg)
        archs = src_cfg.get("architectures")

    for k in CONFIG_DROP:
        base.pop(k, None)

    mt = base.get("model_type") or ""
    if mt.endswith("_text"):          # qwen3_vl_text -> qwen3_vl
        mt = mt[: -len("_text")]
    if mt.endswith("_vl"):            # qwen3_vl -> qwen3（纯文本实现）
        mt = mt[: -len("_vl")]
    base["model_type"] = mt

    if method.startswith("STRIP"):
        t = base.get("model_type") or ""
        if t.startswith("qwen3"):
            base["architectures"] = ["Qwen3ForCausalLM"]
        elif archs:
            base["architectures"] = archs
    elif archs:
        base["architectures"] = archs

    # VL 侧的 mRoPE 在纯文本 transformers 实现里不可用，显式置空（部分版本会报错）
    rs = base.get("rope_scaling") or {}
    if isinstance(rs, dict) and rs.get("mrope_section"):
        base["rope_scaling"] = None
        base["_rope_scaling_note"] = (
            "mrope_section dropped: text-only load falls back to standard RoPE")

    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump(base, f, indent=2)
    return base


def extract_weights(src_dir, out_dir, prefix):
    """按前缀抽权重并落成单个 model.safetensors。"""
    from safetensors import safe_open
    from safetensors.torch import save_file

    state, n_skip = {}, 0
    for path in weight_files(src_dir):
        with safe_open(path, "pt") as f:
            for k in f.keys():
                if any(v in k for v in ("visual.", "vision_tower.")):
                    n_skip += 1
                    continue
                if prefix:
                    if not k.startswith(prefix):
                        n_skip += 1
                        continue
                    name = k[len(prefix):]
                else:
                    name = k
                state[name] = f.get_tensor(k)
    tmp = os.path.join(out_dir, "model.safetensors")
    save_file(state, tmp, metadata={"format": "pt"})
    print(f"[weights] 写入 {len(state)} 个张量（跳过 {n_skip} 个）-> {tmp}")
    return len(state)


def copy_tokenizer(src_dir, out_dir):
    """拷贝 tokenizer 相关文件（Qwen 家族词表一致）。"""
    copied = []
    for fn in TOKENIZER_FILES:
        src = os.path.join(src_dir, fn)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(out_dir, fn))
            copied.append(fn)
    if not copied:
        print("[tokenizer] ⚠️ 源目录没有任何 tokenizer 文件（下游 load 会失败）")
    else:
        print(f"[tokenizer] 拷贝 {len(copied)} 个文件: {', '.join(copied)}")
    return copied


def verify_load(out_dir):
    """载入抽取结果并生成一句话，确认可被 transformers 正常读取。"""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:                                        # pragma: no cover
        print(f"  [verify] 跳过（缺依赖: {e}）")
        return True
    try:
        tok = AutoTokenizer.from_pretrained(out_dir, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            out_dir, dtype=torch.float32, trust_remote_code=True)
        model.eval()
        nparams = sum(p.numel() for p in model.parameters()) / 1e9
        prompt = ("<|im_start|>user\nWhat is 2+3? Answer briefly.<|im_end|>\n"
                  "<|im_start|>assistant\n")
        ids = tok(prompt, return_tensors="pt").input_ids
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=16, do_sample=False)
        text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        print(f"  [verify] {type(model).__name__} params={nparams:.2f}B gen={text!r}")
        return bool(text.strip())
    except Exception as e:                                          # noqa: BLE001
        print(f"  [verify] 失败: {type(e).__name__}: {e}")
        return False


def prepare(src_dir, out_dir, verify=False):
    """按探测结论把 src_dir 落成纯文本 backbone；成功打印 READY 并返回 True。"""
    info = inspect(src_dir)
    print(f"=== prepare: {info['path']} -> {out_dir} ===")
    print(f"  method={info['method']}  model_type={info['model_type']}  "
          f"text_type={info['text_model_type']}  files={info['n_weight_files']}  "
          f"size={info['size_gb']}GB  reason={info['reason']}")
    if info.get("method") == "SKIP" or not info.get("n_weight_files"):
        print(f"BLOCKED {info['reason']}")
        return False

    with open(os.path.join(src_dir, "config.json")) as f:
        src_cfg = json.load(f)
    os.makedirs(out_dir, exist_ok=True)
    cfg = build_config(src_cfg, info["method"], out_dir)
    print(f"[config] -> {out_dir}/config.json  model_type={cfg.get('model_type')}  "
          f"architectures={cfg.get('architectures')}")
    n = extract_weights(src_dir, out_dir, info["prefix"])
    if n == 0:
        print("BLOCKED 抽取后张量为 0（前缀判定可能有误）")
        return False
    copy_tokenizer(src_dir, out_dir)
    with open(os.path.join(out_dir, "SOURCE.json"), "w") as f:
        json.dump({"source": info["path"], "method": info["method"],
                   "prefix": info["prefix"], "n_tensors": n,
                   "generated_by": "probe_backbone.py (vision wake#1683)"}, f, indent=2)
    if verify and not verify_load(out_dir):
        print("BLOCKED 载入自检失败（详见上方 [verify] 输出）")
        return False
    print(f"READY {os.path.abspath(out_dir)}")
    return True


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="定位/抽取纯文本 Qwen3 系 backbone（.17 就地重生成 Stage-1W 专用）")
    ap.add_argument("--scan", action="store_true", help="只读扫描 roots 并打印判定")
    ap.add_argument("--prepare", action="store_true", help="抽取指定 --src 到 --out")
    ap.add_argument("--autoprepare", action="store_true",
                    help="扫描 roots，自动选一个可用源并抽取到 --out")
    ap.add_argument("--src", default=None, help="多模态/分片模型目录（--prepare 用）")
    ap.add_argument("--out", default=None, help="纯文本 backbone 输出目录")
    ap.add_argument("--roots", nargs="*", default=[], help="扫描根目录（可多个）")
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--max-dirs", type=int, default=600)
    ap.add_argument("--verify", action="store_true", help="抽取后载入并生成自检")
    ap.add_argument("--json-out", default=None, help="把结论写成 JSON")
    args = ap.parse_args()

    if not (args.scan or args.prepare or args.autoprepare):
        ap.print_help()
        return 0

    report = {"roots": args.roots, "candidates": []}
    if args.scan or args.autoprepare:
        print(f"=== scan {len(args.roots)} 个根目录（depth<={args.max_depth}, "
              f"max_dirs={args.max_dirs}）===")
        for d in scan(args.roots, args.max_depth, args.max_dirs):
            info = inspect(d)
            report["candidates"].append(info)
            flag = "OK  " if info.get("ok") else "SKIP"
            print(f"  [{flag}] {info.get('method', '?'):9s} {d}")
            print(f"         {info.get('reason')}  size={info.get('size_gb')}GB  "
                  f"hidden={info.get('hidden_size')} layers={info.get('num_hidden_layers')}")

    if args.prepare or args.autoprepare:
        src = args.src
        if args.autoprepare and not src:
            ok = [c for c in report["candidates"] if c.get("ok")]
            if not ok:
                print("BLOCKED 扫描未找到可用的 backbone 源")
                if args.json_out:
                    with open(args.json_out, "w") as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                return 0
            # 小体积优先：2B 级 backbone 足够，避免误抓巨型 VL 全量权重
            ok.sort(key=lambda c: c.get("size_gb") or 1e9)
            src = ok[0]["path"]
            print(f"[autoprepare] 选中: {src}")
        if not src or not args.out:
            print("BLOCKED --prepare 需要 --src 与 --out")
            return 0
        ok = prepare(src, args.out, verify=args.verify)
        report["prepared"] = {"src": src, "out": args.out, "ok": ok}
        if not ok:
            print("BLOCKED 抽取失败")

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[json] {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
