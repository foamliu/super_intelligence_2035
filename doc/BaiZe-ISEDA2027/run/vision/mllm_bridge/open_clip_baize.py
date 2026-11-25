#!/usr/bin/env python
"""open_clip protocol wrapper for the BaiZe vision encoder.

This module makes the BaiZe OpenVision2 ViT loadable via the **open_clip**
API so it can be used as a drop-in vision tower in LLaVA-OneVision-style
pipelines and other open_clip consumers.

Requirements satisfied (per operator instruction 2026-10-15 22:25 §B-1):
  - open_clip.create_model_and_transforms('baize-vit-512', pretrained=<ckpt>)
    loads the model and returns (model, preprocess_train, preprocess_val).
  - model.encode_image(x) / model.visual(x) returns [B, N, D] where
    N = 196 patch tokens, D = 512.  No CLS token (BaiZe has none).
    No spatial-merge (spatial_merge_size=1).
  - model.vision_config exposes image_size / patch_size / hidden_size /
    depth / width.
  - Preprocessing matches the existing 224 pipeline (CLIP mean/std, bicubic).

Architecture declaration:
  1. Resolution: 224 single block (no anyres).  Matches BaiZe training.
  2. image_token_index: 151655 (Qwen3 / LLaVA-OV convention).
  3. Feature layer: last hidden layer (after final LayerNorm, before
     ReadoutHead).  Official LLaVA-OV uses SigLIP penultimate layer.

Usage
-----
>>> from mllm_bridge.open_clip_baize import register_baize_in_open_clip
>>> register_baize_in_open_clip()
>>> import open_clip
>>> model, _, preprocess = open_clip.create_model_and_transforms(
...     'baize-vit-512',
...     pretrained='/path/to/vision.pt',
... )
>>> feats = model.encode_image(preprocess(image).unsqueeze(0))
>>> feats.shape  # torch.Size([1, 196, 512])
"""

from __future__ import annotations

import os
import sys
import json
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Callable
from pathlib import Path

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

from mllm_bridge.modeling_baize_vision import BaizeVisionModel, BaizeVisionConfig

logger = logging.getLogger(__name__)

# ---- BaiZe architecture constants ----
BAIZE_IMAGE_SIZE = 224
BAIZE_PATCH_SIZE = 16
BAIZE_WIDTH = 512
BAIZE_DEPTH = 30
BAIZE_HEADS = 8  # 512 // 64 = 8 (matches config default & checkpoint)
BAIZE_MLP_DIM = 2048
BAIZE_EMBED_DIM = 768  # ReadoutHead output dim (checkpoint head.proj is [768, 512])
BAIZE_NUM_PATCHES = (BAIZE_IMAGE_SIZE // BAIZE_PATCH_SIZE) ** 2  # 196
BAIZE_VIT_NAME = "baize-vit-512"

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

_REGISTERED = False


class BaizeVisionConfigOC:
    """Lightweight vision config exposed on the open_clip model.

    Provides: image_size / patch_size / hidden_size / depth / width.
    """

    def __init__(
        self,
        image_size=BAIZE_IMAGE_SIZE,
        patch_size=BAIZE_PATCH_SIZE,
        hidden_size=BAIZE_WIDTH,
        depth=BAIZE_DEPTH,
        width=BAIZE_WIDTH,
        heads=BAIZE_HEADS,
        mlp_dim=BAIZE_MLP_DIM,
        embed_dim=BAIZE_EMBED_DIM,
        num_patches=BAIZE_NUM_PATCHES,
        spatial_merge_size=1,
        feature_layer="last",
    ):
        self.image_size = image_size
        self.patch_size = patch_size
        self.hidden_size = hidden_size
        self.depth = depth
        self.width = width
        self.heads = heads
        self.mlp_dim = mlp_dim
        self.embed_dim = embed_dim
        self.num_patches = num_patches
        self.spatial_merge_size = spatial_merge_size
        self.feature_layer = feature_layer
        self.layers = depth
        self.output_dim = embed_dim

    def to_dict(self):
        return {
            "image_size": self.image_size, "patch_size": self.patch_size,
            "hidden_size": self.hidden_size, "depth": self.depth,
            "width": self.width, "heads": self.heads,
            "mlp_dim": self.mlp_dim, "embed_dim": self.embed_dim,
            "num_patches": self.num_patches,
            "spatial_merge_size": self.spatial_merge_size,
            "feature_layer": self.feature_layer,
            "has_cls_token": False, "spatial_merge": False,
        }

    def __repr__(self):
        return (
            f"BaizeVisionConfigOC(image_size={self.image_size}, "
            f"patch_size={self.patch_size}, hidden_size={self.hidden_size}, "
            f"depth={self.depth}, width={self.width}, heads={self.heads}, "
            f"num_patches={self.num_patches}, has_cls=False, "
            f"spatial_merge=False, feature_layer={self.feature_layer})"
        )


class DummyTextTower(nn.Module):
    """Placeholder text tower — BaiZe is vision-only."""

    def __init__(self, output_dim=BAIZE_EMBED_DIM):
        super().__init__()
        self.output_dim = output_dim
        self._dummy_param = nn.Parameter(torch.zeros(1))

    def forward(self, text):
        batch = text.shape[0] if isinstance(text, torch.Tensor) else 1
        return torch.zeros(batch, self.output_dim, device=self._dummy_param.device)

    def encode_text(self, text, normalize=False):
        out = self.forward(text)
        return F.normalize(out, dim=-1) if normalize else out


class BaizeOpenCLIP(nn.Module):
    """open_clip-compatible model wrapping the BaiZe vision encoder.

    visual : BaizeVisionModel — visual(x) returns [B, 196, 512] patch features.
    text : DummyTextTower — placeholder (BaiZe is vision-only).
    vision_config : BaizeVisionConfigOC — architecture metadata.

    encode_image(x) returns patch-level [B, N, D], NOT pooled.
    No CLS token. No spatial merge. Feature layer = last hidden.
    """

    def __init__(
        self,
        ckpt_path=None,
        image_size=BAIZE_IMAGE_SIZE,
        patch_size=BAIZE_PATCH_SIZE,
        width=BAIZE_WIDTH,
        depth=BAIZE_DEPTH,
        heads=BAIZE_HEADS,
        mlp_dim=BAIZE_MLP_DIM,
        embed_dim=BAIZE_EMBED_DIM,
        **kwargs,
    ):
        super().__init__()
        hf_config = BaizeVisionConfig(
            image_size=image_size, patch_size=patch_size, width=width,
            depth=depth, heads=heads, mlp_dim=mlp_dim,
            spatial_merge_size=1, embed_dim=embed_dim,
        )
        if ckpt_path and os.path.exists(ckpt_path):
            logger.info(f"[BaizeOpenCLIP] Loading checkpoint: {ckpt_path}")
            self.visual = BaizeVisionModel.from_baize_checkpoint(ckpt_path, hf_config)
        else:
            logger.info("[BaizeOpenCLIP] No checkpoint — random init")
            self.visual = BaizeVisionModel(hf_config)

        self.vision_config = BaizeVisionConfigOC(
            image_size=image_size, patch_size=patch_size, hidden_size=width,
            depth=depth, width=width, heads=heads, mlp_dim=mlp_dim,
            embed_dim=embed_dim, num_patches=(image_size // patch_size) ** 2,
        )
        self.text = DummyTextTower(embed_dim)
        self.logit_scale = nn.Parameter(torch.ones([]) * 2.659)

    @property
    def dtype(self):
        return next(self.visual.parameters()).dtype

    @property
    def device(self):
        return next(self.visual.parameters()).device

    def encode_image(self, image, normalize=False):
        """Returns [B, 196, 512] patch features (no CLS, no pool, no merge)."""
        features = self.visual(image)
        if normalize:
            features = F.normalize(features, dim=-1)
        return features

    def encode_text(self, text, normalize=False):
        return self.text.encode_text(text, normalize=normalize)

    def forward(self, image, text=None):
        """Forward: encode_image + optional encode_text for CLIP-style loss."""
        image_features = self.encode_image(image, normalize=True)
        if text is not None:
            text_features = self.encode_text(text, normalize=True)
            return image_features, text_features, None
        return image_features


def get_baize_transforms(
    image_size=BAIZE_IMAGE_SIZE,
    mean=CLIP_MEAN,
    std=CLIP_STD,
):
    """Return (preprocess_train, preprocess_val) matching the 224 pipeline."""
    from torchvision import transforms as T
    preprocess_val = T.Compose([
        T.Resize(int(image_size * 1.15)),
        T.CenterCrop(image_size),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])
    preprocess_train = T.Compose([
        T.RandomResizedCrop(
            image_size, scale=(0.9, 1.0),
            interpolation=T.InterpolationMode.BICUBIC,
        ),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])
    return preprocess_train, preprocess_val
_REGISTERED = False

def register_baize_in_open_clip():
    """Register 'baize-vit-512' in open_clip's model registry.

    After calling this, you can use:
        open_clip.create_model_and_transforms('baize-vit-512', pretrained=<ckpt>)
    """
    global _REGISTERED
    if _REGISTERED:
        return

    import open_clip
    import open_clip.factory as factory

    baize_config = {
        "embed_dim": BAIZE_EMBED_DIM,
        "vision_cfg": {
            "image_size": BAIZE_IMAGE_SIZE, "patch_size": BAIZE_PATCH_SIZE,
            "width": BAIZE_WIDTH, "layers": BAIZE_DEPTH, "heads": BAIZE_HEADS,
            "mlp_ratio": float(BAIZE_MLP_DIM) / BAIZE_WIDTH,
            "output_tokens": True, "pool_type": "none",
        },
        "text_cfg": {
            "context_length": 77, "vocab_size": 49408,
            "width": BAIZE_EMBED_DIM, "heads": 12, "layers": 12,
        },
        "preprocess_cfg": {
            "mean": list(CLIP_MEAN), "std": list(CLIP_STD),
            "interpolation": "bicubic", "resize_mode": "shortest",
        },
    }

    # Register config
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({BAIZE_VIT_NAME: baize_config}, f)
        config_path = f.name
    try:
        open_clip.add_model_config(config_path)
    except Exception as e:
        if "already" not in str(e).lower():
            raise
    finally:
        os.unlink(config_path)

    # Monkey-patch create_model to intercept 'baize-vit-512'
    _original_create_model = factory.create_model

    def _build_baize(model_name, pretrained, precision, device, **kw):
        ckpt_path = pretrained
        if model_name.startswith("local-dir:") and ckpt_path is None:
            local_path = Path(model_name[len("local-dir:"):])
            for wname in ["pytorch_model.bin", "model.safetensors",
                          "open_clip_pytorch_model.pt", "vision.pt"]:
                wpath = local_path / wname
                if wpath.exists():
                    ckpt_path = str(wpath)
                    break
        model = BaizeOpenCLIP(ckpt_path=ckpt_path)
        if precision == "fp16":
            model = model.half()
        elif precision == "bf16":
            model = model.bfloat16()
        model = model.to(device)
        preprocess_train, preprocess_val = get_baize_transforms()
        return model, preprocess_train, preprocess_val

    def _patched_create_model(model_name, pretrained=None, precision="fp32",
                              device="cpu", **kwargs):
        clean_name = model_name
        if model_name.startswith("local-dir:"):
            local_path = Path(model_name[len("local-dir:"):])
            cfg_file = local_path / "open_clip_config.json"
            if cfg_file.exists():
                with open(cfg_file) as f:
                    cfg = json.load(f)
                if cfg.get("model_cfg", {}).get("model_type") == "baize_vision":
                    clean_name = BAIZE_VIT_NAME
                    if pretrained is None:
                        for wname in ["pytorch_model.bin", "model.safetensors",
                                      "open_clip_pytorch_model.pt", "vision.pt"]:
                            wpath = local_path / wname
                            if wpath.exists():
                                pretrained = str(wpath)
                                break
        if clean_name == BAIZE_VIT_NAME:
            logger.info(f"[open_clip_baize] Intercepted '{model_name}'")
            return _build_baize(model_name, pretrained, precision, device, **kwargs)
        return _original_create_model(
            model_name=model_name, pretrained=pretrained, precision=precision,
            device=device, **kwargs)

    factory.create_model = _patched_create_model
    open_clip.create_model = _patched_create_model

    _original_cm_and_t = factory.create_model_and_transforms

    def _patched_cm_and_t(model_name, pretrained=None, **kwargs):
        clean_name = model_name
        if model_name.startswith("local-dir:"):
            local_path = Path(model_name[len("local-dir:"):])
            cfg_file = local_path / "open_clip_config.json"
            if cfg_file.exists():
                with open(cfg_file) as f:
                    cfg = json.load(f)
                if cfg.get("model_cfg", {}).get("model_type") == "baize_vision":
                    clean_name = BAIZE_VIT_NAME
                    if pretrained is None:
                        for wname in ["pytorch_model.bin", "model.safetensors",
                                      "open_clip_pytorch_model.pt", "vision.pt"]:
                            wpath = local_path / wname
                            if wpath.exists():
                                pretrained = str(wpath)
                                break
        if clean_name == BAIZE_VIT_NAME:
            return _patched_create_model(
                model_name, pretrained=pretrained, **kwargs)
        return _original_cm_and_t(model_name, pretrained=pretrained, **kwargs)

    factory.create_model_and_transforms = _patched_cm_and_t
    open_clip.create_model_and_transforms = _patched_cm_and_t

    _REGISTERED = True
    logger.info(
        f"[open_clip_baize] Registration complete. "
        f"Use: open_clip.create_model_and_transforms('{BAIZE_VIT_NAME}', pretrained=<ckpt>)")


# Auto-register on import
register_baize_in_open_clip()
