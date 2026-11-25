#!/usr/bin/env python
"""Export BaiZe vision encoder as an LLaVA-OneVision compatible HF directory.

Per operator instruction 2026-10-15 22:25 §B-2, produces a directory that can
be consumed by the official LLaVA-OV pipeline:

  - config.json: model_type + vision_config + text_config + image_token_index
    + vision_feature_select_strategy
  - preprocessor_config.json: image processor config
  - chat_template: Jinja2 chat template (from Qwen3)
  - Model weights (vision tower only)

Architecture declaration:
  1. Resolution: 224 single block (no anyres)
  2. image_token_index: 151655
  3. vision_feature_select_strategy: "default" (last layer; BaiZe has no CLS,
     so all 196 patch tokens are used)
  4. Feature layer: last hidden (after final LayerNorm). Official LLaVA-OV
     uses SigLIP penultimate — difference MUST be noted in reports.

Usage:
    python mllm_bridge/export_llava_ov_hf.py \\
        --ckpt /path/to/vision.pt \\
        --output_dir /path/to/baize_llava_ov_hf \\
        --llm_path /path/to/Qwen3-4B-Instruct
"""

from __future__ import annotations
import os, sys, json, argparse, torch
from pathlib import Path

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

from mllm_bridge.modeling_baize_vision import BaizeVisionModel, BaizeVisionConfig

IMAGE_TOKEN_INDEX = 151655
CLIP_MEAN = [0.48145466, 0.4578275, 0.40821073]
CLIP_STD = [0.26862954, 0.26130258, 0.27577711]

def build_llava_ov_config(vision_config, llm_config):
    """Build the LLaVA-OV style config.json."""
    return {
        "model_type": "llava_onevision",
        "architectures": ["LlavaOnevisionForConditionalGeneration"],
        "image_token_index": IMAGE_TOKEN_INDEX,
        "vision_feature_select_strategy": "default",
        "vision_config": {
            "model_type": "baize_vision",
            "architectures": ["BaizeVisionModel"],
            "image_size": vision_config.image_size,
            "patch_size": vision_config.patch_size,
            "width": vision_config.width,
            "depth": vision_config.depth,
            "heads": vision_config.heads,
            "mlp_dim": vision_config.mlp_dim,
            "embed_dim": vision_config.embed_dim,
            "spatial_merge_size": 1,
            "has_cls_token": False,
            "feature_layer": "last",
            "auto_map": {
                "AutoConfig": "configuration_baize_vision.BaizeVisionConfig",
                "AutoModel": "modeling_baize_vision.BaizeVisionModel",
            },
        },
        "text_config": llm_config,
        "ignore_index": -100,
        "image_seq_length": vision_config.num_patches,
        "torch_dtype": "float32",
    }


def build_preprocessor_config(image_size=224):
    """Build preprocessor_config.json (CLIPImageProcessor style)."""
    return {
        "do_convert_rgb": True, "do_normalize": True,
        "do_resize": True, "do_center_crop": True,
        "image_mean": CLIP_MEAN, "image_std": CLIP_STD,
        "size": {"shortest_edge": int(image_size * 1.15)},
        "crop_size": {"height": image_size, "width": image_size},
        "resample": 3, "processor_type": "CLIPImageProcessor",
    }

def export_llava_ov_hf(ckpt_path, output_dir, llm_path=None):
    """Export BaiZe vision as LLaVA-OV compatible HF directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[export] Loading BaiZe checkpoint: {ckpt_path}")
    model = BaizeVisionModel.from_baize_checkpoint(ckpt_path)
    model.eval()
    vc = model.config

    llm_config = {}
    if llm_path and os.path.exists(llm_path):
        llm_cfg_path = os.path.join(llm_path, "config.json")
        if os.path.exists(llm_cfg_path):
            with open(llm_cfg_path) as f:
                llm_config = json.load(f)
            llm_config.pop("auto_map", None)
            print(f"[export] Loaded LLM config from {llm_cfg_path}")

    # 1. config.json
    config = build_llava_ov_config(vc, llm_config)
    with open(output_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"[export] Wrote config.json")

    # 2. preprocessor_config.json
    preproc = build_preprocessor_config(vc.image_size)
    with open(output_dir / "preprocessor_config.json", "w") as f:
        json.dump(preproc, f, indent=2)
    print(f"[export] Wrote preprocessor_config.json")

    # 3. Copy vision config files
    import shutil
    bridge = Path(BRIDGE_DIR)
    for fname in ["configuration_baize_vision.py", "modeling_baize_vision.py",
                  "__init__.py"]:
        src = bridge / fname
        if src.exists():
            shutil.copy2(src, output_dir / fname)
            print(f"[export] Copied {fname}")

    # 4. Save vision weights
    weights_path = output_dir / "pytorch_model.bin"
    state_dict = model.state_dict()
    torch.save(state_dict, weights_path)
    print(f"[export] Saved vision weights: {len(state_dict)} keys")

    # 5. open_clip_config.json
    open_clip_config = {
        "model_cfg": {
            "model_type": "baize_vision",
            "embed_dim": vc.embed_dim,
            "vision_cfg": {
                "image_size": vc.image_size, "patch_size": vc.patch_size,
                "width": vc.width, "layers": vc.depth, "heads": vc.heads,
                "mlp_ratio": float(vc.mlp_dim) / vc.width,
                "output_tokens": True, "pool_type": "none",
            },
            "text_cfg": {
                "context_length": 77, "vocab_size": 49408,
                "width": vc.embed_dim, "heads": 12, "layers": 12,
            },
        },
        "preprocess_cfg": {
            "mean": CLIP_MEAN, "std": CLIP_STD,
            "interpolation": "bicubic", "resize_mode": "shortest",
        },
    }
    with open(output_dir / "open_clip_config.json", "w") as f:
        json.dump(open_clip_config, f, indent=2)
    print(f"[export] Wrote open_clip_config.json")

    # 6. Chat template
    chat_template = None
    if llm_path and os.path.exists(llm_path):
        tok_cfg_path = os.path.join(llm_path, "tokenizer_config.json")
        if os.path.exists(tok_cfg_path):
            with open(tok_cfg_path) as f:
                tok_cfg = json.load(f)
            chat_template = tok_cfg.get("chat_template")
    if chat_template:
        with open(output_dir / "chat_template.json", "w") as f:
            json.dump({"chat_template": chat_template}, f, indent=2)
        print(f"[export] Wrote chat_template.json")
    else:
        print("[export] WARNING: No chat template found")

    print(f"\n[export] ✅ Export complete: {output_dir}")
    print(f"[export] Files: {sorted(os.listdir(output_dir))}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Export BaiZe vision as LLaVA-OV compatible HF directory")
    parser.add_argument("--ckpt", required=True,
                        help="Path to BaiZe vision.pt checkpoint")
    parser.add_argument("--output_dir", required=True,
                        help="Output HF directory path")
    parser.add_argument("--llm_path", default=None,
                        help="Path to LLM (Qwen3) for config extraction")
    args = parser.parse_args()
    export_llava_ov_hf(args.ckpt, args.output_dir, args.llm_path)

if __name__ == "__main__":
    main()
