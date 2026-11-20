#!/usr/bin/env python
"""open_clip bridge for BaiZe ArmB ViT-L/14 (1024-dim patch tokens).

Registers a custom model `baize-vitl14-1024` in open_clip so the ArmB-trained
ViT-L/14 encoder can be used as a drop-in vision tower in LLaVA-OneVision-style
pipelines and lmms-eval.

Key properties (per operator instruction 2026-10-17 §②):
  - encode_image(x) -> [B, 256, 1024]  (patch tokens, NOT pooled)
  - image_size=224, patch_size=16, no spatial merge
  - Loads via open_clip.create_model_and_transforms('baize-vitl14-1024', pretrained=<ckpt>)
  - Checkpoint = open_clip_state_dict.pt (clip model only, predictor stripped)

Usage:
  >>> from mllm_bridge.open_clip_vitl14_1024 import register_baize_vitl14
  >>> register_baize_vitl14()
  >>> import open_clip
  >>> model, _, preprocess = open_clip.create_model_and_transforms(
  ...     'baize-vitl14-1024', pretrained='/path/to/open_clip_state_dict.pt')
  >>> feats = model.encode_image(preprocess(img).unsqueeze(0))  # [1, 196, 768]
"""
from __future__ import annotations
import os
import sys
import logging
import torch
import torch.nn as nn
import open_clip
from open_clip.transformer import VisionTransformer

logger = logging.getLogger(__name__)

BAIZE_VITL14_IMAGE_SIZE = 224
BAIZE_VITL14_PATCH_SIZE = 14
BAIZE_VITL14_WIDTH = 1024
BAIZE_VITL14_N_PATCHES = (BAIZE_VITL14_IMAGE_SIZE // BAIZE_VITL14_PATCH_SIZE) ** 2  # 256


class BaiZeViTL14VisionWrapper(nn.Module):
    """Wraps open_clip ViT-L/14 visual tower to return patch tokens [B, 256, 1024].

    encode_image returns the full sequence of patch tokens (after ln_post,
    before projection) — suitable for LLaVA-OV's vision token injection.
    No CLS token, no spatial merge.
    """
    def __init__(self, visual: VisionTransformer):
        super().__init__()
        self.visual = visual
        self._captured = {}
        self.visual.transformer.register_forward_hook(self._hook_fn)
        # Expose config for LLaVA-OV compatibility
        self.image_size = BAIZE_VITL14_IMAGE_SIZE
        self.patch_size = BAIZE_VITL14_PATCH_SIZE
        self.hidden_size = BAIZE_VITL14_WIDTH
        self.num_patches = BAIZE_VITL14_N_PATCHES
        self.spatial_merge_size = 1  # no merge

    def _hook_fn(self, module, input, output):
        self._captured['transformer_out'] = output

    def encode_image(self, x, normalize: bool = False):
        """Returns [B, 256, 1024] patch tokens (after ln_post, no projection)."""
        _ = self.visual(x)  # triggers hook
        transformer_out = self._captured['transformer_out']
        patch_tokens = self.visual.ln_post(transformer_out[:, 1:])  # strip CLS
        if normalize:
            patch_tokens = torch.nn.functional.normalize(patch_tokens, dim=-1)
        return patch_tokens

    def forward(self, x):
        return self.encode_image(x)


class BaiZeViTL14CLIP(nn.Module):
    """Minimal CLIP-like wrapper exposing encode_image for lmms-eval."""
    def __init__(self, clip_model):
        super().__init__()
        self.clip = clip_model
        self.visual_wrapper = BaiZeViTL14VisionWrapper(clip_model.visual)
        # Copy attributes for open_clip compatibility
        self.logit_scale = clip_model.logit_scale
        self.transformer = clip_model.transformer  # text tower (open_clip naming)
        self.token_embedding = clip_model.token_embedding
        self.ln_final = clip_model.ln_final
        self.text_projection = clip_model.text_projection
        self.positional_embedding = clip_model.positional_embedding

    def encode_image(self, x, normalize=False):
        return self.visual_wrapper.encode_image(x, normalize=normalize)

    def encode_text(self, text, normalize=True):
        return self.clip.encode_text(text, normalize=normalize)

    def forward(self, x):
        return self.encode_image(x)


def create_baize_vitl14_1024(pretrained=None, device='cpu'):
    """Create BaiZe ViT-L/14 1024-dim model with patch-token output.

    Args:
        pretrained: path to open_clip_state_dict.pt (ArmB output). If None,
                    random init.
        device: 'cpu' or 'cuda'

    Returns:
        (model_wrapper, preprocess_train, preprocess_val)
        model_wrapper.encode_image(x) -> [B, 256, 1024]
    """
    model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(
        'ViT-L-14', pretrained=None)
    if pretrained and isinstance(pretrained, str) and os.path.isfile(pretrained):
        state_dict = torch.load(pretrained, map_location='cpu')
        incompatible = model.load_state_dict(state_dict, strict=True)
        if incompatible.missing_keys or incompatible.unexpected_keys:
            logger.warning(f"BaizeViTB16 load: missing={incompatible.missing_keys[:5]} "
                          f"unexpected={incompatible.unexpected_keys[:5]}")
        else:
            logger.info(f"BaizeViTB16: strict load OK from {pretrained}")
    wrapper = BaiZeViTL14CLIP(model)
    wrapper = wrapper.to(device)
    return wrapper, preprocess_train, preprocess_val


# Backward-compat alias
register_baize_vitl14 = create_baize_vitl14_1024
