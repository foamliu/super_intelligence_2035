#!/usr/bin/env python
"""Extract the text-only backbone from Qwen3-VL-2B-Instruct as a standalone
Qwen3ForCausalLM checkpoint.

WHY
---
The operator task (2026-11-05) specifies a **2B MLLM** for the wave RL pipeline.
The natural candidate is Qwen3-VL-2B-Instruct, but its architecture
(``qwen3_vl``) is NOT recognised by transformers 4.56.1 -- upgrading
transformers risks breaking the existing MLLM training infrastructure
(Stage-1/1.5/2 for ArmE-R2 etc.).

This script sidesteps the problem: the VL model's *text backbone* is a plain
Qwen3 decoder (``text_config.model_type == "qwen3_vl_text"``, architecture
identical to ``Qwen3ForCausalLM``).  We remap the config to ``model_type=qwen3``
and copy only the ``model.language_model.*`` tensors (310 of 625; the other 315
are the vision tower), stripping the ``model.language_model.`` prefix.

The result is a standard Qwen3-2B text checkpoint loadable by transformers
4.56.1 **without any upgrade** -- usable directly for Phase-1 SFT (text-only
tool-use).  The LoRA adapter trained on it will transfer to the full
Qwen3-VL-2B in Phase 2 (same text-backbone weights) once transformers is
upgraded for the multimodal RL stage.

RoPE note
---------
The VL text backbone uses mRoPE (``rope_scaling.mrope_section=[24,20,20]``).
transformers 4.56.1's Qwen3 implementation does NOT understand mrope_section
and silently falls back to standard RoPE.  Empirically the extracted 2B model
generates coherent text with standard RoPE (verified: "What is 2+3?" -> "5"),
so for short text-only SFT trajectories this is safe.

Usage
-----
    python extract_qwen3vl_2b_text.py
    python extract_qwen3vl_2b_text.py --verify          # also load + generate
    python extract_qwen3vl_2b_text.py --src <vl_path> --out <out_dir>

Author: vision wake#620.  License: project-internal.
"""
import argparse, json, os, shutil, torch

from safetensors import safe_open
from safetensors.torch import save_file

SRC_DEFAULT = "/nas_train/app.e0031982/models/Qwen/Qwen3-VL-2B-Instruct"
OUT_DEFAULT = ("/nas_train/app.e0031982/datasets/baize-vision/out/"
               "wave_sft_stage1w/qwen3vl_2b_text_extracted")
PREFIX_TEXT = "model.language_model."   # text-backbone tensor prefix
PREFIX_VIS  = "model.visual."           # vision-tower tensor prefix (skipped)


def build_remapped_config(src_dir, out_dir):
    """Write a qwen3 config derived from the VL model's text_config."""
    cfg_full = json.load(open(os.path.join(src_dir, "config.json")))
    tc = dict(cfg_full["text_config"])
    tc["model_type"] = "qwen3"
    tc["architectures"] = ["Qwen3ForCausalLM"]
    # Drop mRoPE scaling -- tf 4.56.1 Qwen3 ignores these keys anyway;
    # setting None makes the intent explicit (standard RoPE for text-only use).
    tc["rope_scaling"] = None
    os.makedirs(out_dir, exist_ok=True)
    json.dump(tc, open(os.path.join(out_dir, "config.json"), "w"), indent=2)
    print(f"[config] model_type=qwen3  hidden={tc['hidden_size']}  "
          f"layers={tc['num_hidden_layers']}  heads={tc['num_attention_heads']}  "
          f"kv_heads={tc['num_key_value_heads']}  tie_emb={tc['tie_word_embeddings']}")
    return tc


def extract_weights(src_dir, out_dir):
    """Copy model.language_model.* tensors, stripping the prefix -> model.*."""
    src_st = os.path.join(src_dir, "model.safetensors")
    state = {}
    n_vis = 0
    with safe_open(src_st, "pt") as f:
        for k in f.keys():
            if k.startswith(PREFIX_TEXT):
                state[k[len(PREFIX_TEXT):]] = f.get_tensor(k)
            elif k.startswith(PREFIX_VIS):
                n_vis += 1
    save_file(state, os.path.join(out_dir, "model.safetensors"),
              metadata={"format": "pt"})
    print(f"[weights] extracted {len(state)} text tensors "
          f"(skipped {n_vis} vision tensors)")
    return len(state)


def copy_tokenizer(src_dir, out_dir):
    """Copy tokenizer + chat-template files (identical vocab for Qwen3 family)."""
    copied = []
    for fn in ["tokenizer.json", "tokenizer_config.json", "vocab.json",
               "merges.txt", "chat_template.json"]:
        src = os.path.join(src_dir, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out_dir, fn))
            copied.append(fn)
    print(f"[tokenizer] copied {len(copied)} files: {', '.join(copied)}")
    return copied


def verify(out_dir):
    """Load the extracted model on CPU and run a generation sanity check."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(out_dir, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        out_dir, dtype=torch.float32, trust_remote_code=True)
    model.eval()
    nparams = sum(p.numel() for p in model.parameters()) / 1e9
    print(f"[verify] loaded {type(model).__name__}  params={nparams:.2f}B")
    prompt = ("<|im_start|>user\nWhat is 2+3? Answer briefly.<|im_end|>\n"
              "<|im_start|>assistant\n")
    ids = tok(prompt, return_tensors="pt").input_ids
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=20, do_sample=False)
    text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    print(f"[verify] generation: {text!r}")
    ok = bool(text.strip())
    print(f"[verify] {'PASS' if ok else 'FAIL -- empty generation'}")
    return ok


def main():
    ap = argparse.ArgumentParser(
        description="Extract Qwen3-VL-2B text backbone as standalone Qwen3ForCausalLM")
    ap.add_argument("--src", default=SRC_DEFAULT,
                    help="source Qwen3-VL-2B-Instruct dir")
    ap.add_argument("--out", default=OUT_DEFAULT,
                    help="output dir for extracted text-only checkpoint")
    ap.add_argument("--verify", action="store_true",
                    help="load the extracted model + run a generation sanity check")
    args = ap.parse_args()

    print(f"=== extract_qwen3vl_2b_text: {args.src} -> {args.out} ===")
    build_remapped_config(args.src, args.out)
    extract_weights(args.src, args.out)
    copy_tokenizer(args.src, args.out)
    if args.verify:
        ok = verify(args.out)
        if not ok:
            raise SystemExit("Verification FAILED")
    print("=== DONE ===")


if __name__ == "__main__":
    main()
