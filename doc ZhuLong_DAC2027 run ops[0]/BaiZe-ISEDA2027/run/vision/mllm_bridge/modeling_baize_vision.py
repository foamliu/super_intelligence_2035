"""BaiZe vision tower — HuggingFace ``PreTrainedModel`` wrapper.

This module re-implements the BaiZe OpenVision2 ViT architecture (from
``run/vision/models.py``) as a self-contained HF model so it can be loaded
via ``AutoModel`` / ``from_pretrained`` without depending on the training
codebase.

The architecture is a pure-attention ViT:
  PatchEmbed (Conv2d + learned positional embedding)
  -> N x AttentionBlock (pre-norm, SwiGLU MLP, SDPA attention)
  -> final LayerNorm
  -> ReadoutHead (mean-pool + Linear -- used only for contrastive learning)

For the MLLM bridge, ``forward()`` returns **patch-level features** ``[B, 196, width]``
(after the final LayerNorm, **skipping** the ReadoutHead).  The ReadoutHead
weights are still loaded (``strict=True``) but not used in the forward pass.

Checkpoint format
-----------------
The ④-4ep checkpoint (``vision.pt``) is a dict with key ``'vision'`` whose
value is a ``state_dict`` with keys::

    embed.pos, embed.conv.weight,
    blocks.{0..29}.norm1.{weight,bias},
    blocks.{0..29}.attn.qkv.weight, blocks.{0..29}.attn.proj.weight,
    blocks.{0..29}.norm2.{weight,bias},
    blocks.{0..29}.mlp.{gate,up,down}.weight,
    norm.{weight,bias},
    head.norm.{weight,bias}, head.proj.weight

No prefix stripping is needed for BaiZe's own checkpoints (unlike the
official OpenVision2 ``visual.`` prefix handled in ``r13_eval_official.py``).
The ``from_baize_checkpoint`` classmethod handles both cases.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel

from .configuration_baize_vision import BaizeVisionConfig


# ---------------------------------------------------------------------------
# Architecture components (mirrors run/vision/models.py -- same param names)
# ---------------------------------------------------------------------------
class LayerNorm(nn.LayerNorm):
    """LayerNorm with explicit forward (matches models.py)."""

    def forward(self, x):
        return F.layer_norm(x, self.normalized_shape, self.weight, self.bias, self.eps)


class SwiGLU(nn.Module):
    def __init__(self, dim: int, hidden: int):
        super().__init__()
        self.gate = nn.Linear(dim, hidden, bias=False)
        self.up = nn.Linear(dim, hidden, bias=False)
        self.down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        return self.down(F.silu(self.gate(x)) * self.up(x))


class Attention(nn.Module):
    def __init__(self, dim: int, heads: int, qkv_bias: bool = False):
        super().__init__()
        assert dim % heads == 0
        self.heads = heads
        self.head_dim = dim // heads
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim, bias=False)

    def forward(self, x, attn_mask=None):
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask)
        out = out.transpose(1, 2).reshape(B, N, C)
        return self.proj(out)


class AttentionBlock(nn.Module):
    def __init__(self, dim: int, heads: int, mlp_dim: int):
        super().__init__()
        self.norm1 = LayerNorm(dim)
        self.attn = Attention(dim, heads)
        self.norm2 = LayerNorm(dim)
        self.mlp = SwiGLU(dim, mlp_dim)

    def forward(self, x, attn_mask=None):
        x = x + self.attn(self.norm1(x), attn_mask=attn_mask)
        x = x + self.mlp(self.norm2(x))
        return x


class PatchEmbed(nn.Module):
    def __init__(self, image_size: int, patch_size: int, width: int):
        super().__init__()
        self.grid = image_size // patch_size
        self.conv = nn.Conv2d(3, width, patch_size, patch_size, bias=False)
        self.pos = nn.Parameter(torch.randn(self.grid * self.grid, width) * (width ** -0.5))

    def forward(self, x):
        x = self.conv(x).flatten(2).transpose(1, 2)
        return x + self.pos


class ReadoutHead(nn.Module):
    """Mean-pool + projection head (contrastive learning only).

    **Not used** in the MLLM bridge forward path; weights are loaded only so
    that ``strict=True`` succeeds.
    """

    def __init__(self, width: int, embed_dim: int = 768):
        super().__init__()
        self.norm = LayerNorm(width)
        self.proj = nn.Linear(width, embed_dim, bias=False)

    def forward(self, x):
        x = x.mean(dim=1)
        return self.proj(self.norm(x))


# ---------------------------------------------------------------------------
# HF PreTrainedModel wrapper
# ---------------------------------------------------------------------------
class BaizeVisionPreTrainedModel(PreTrainedModel):
    """Base class for BaiZe vision models -- handles config & weight init."""

    config_class = BaizeVisionConfig
    base_model_prefix = "baize_vision"
    main_input_name = "pixel_values"
    _no_split_modules = ["AttentionBlock"]

    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)


class BaizeVisionModel(BaizeVisionPreTrainedModel):
    """BaiZe OpenVision2 ViT as an HF model.

    Forward returns patch-level features ``[B, num_patches, width]`` by default
    (after final LayerNorm, **skipping** ReadoutHead).  Pass ``return_pooled=True``
    to also get the pooled ReadoutHead output.
    """

    def __init__(self, config: BaizeVisionConfig):
        super().__init__(config)
        self.config = config
        w, d, h, m = config.width, config.depth, config.heads, config.mlp_dim
        self.embed = PatchEmbed(config.image_size, config.patch_size, w)
        self.blocks = nn.ModuleList([AttentionBlock(w, h, m) for _ in range(d)])
        self.norm = LayerNorm(w)
        self.head = ReadoutHead(w, embed_dim=config.embed_dim)
        self.num_patches = config.num_patches  # 196 for 224/16

    @property
    def dtype(self) -> torch.dtype:
        return self.blocks[0].mlp.down.weight.dtype

    def forward(
        self,
        pixel_values: torch.FloatTensor,
        return_pooled: bool = False,
        output_hidden_states: bool = False,
    ):
        """Forward pass.

        Parameters
        ----------
        pixel_values : Tensor[B, 3, image_size, image_size]
            Normalised image tensor.
        return_pooled : bool
            If True, also return the ReadoutHead pooled output [B, embed_dim].
        output_hidden_states : bool
            If True, return per-layer hidden states.

        Returns
        -------
        patch_features : Tensor[B, num_patches, width]
            Patch-level features after final LayerNorm (ReadoutHead skipped).
        pooled : Tensor[B, embed_dim], optional
            ReadoutHead output (only if ``return_pooled=True``).
        """
        x = self.embed(pixel_values)
        all_hidden = () if output_hidden_states else None
        for block in self.blocks:
            x = block(x)
            if output_hidden_states:
                all_hidden += (x,)
        x = self.norm(x)
        if return_pooled:
            pooled = self.head(x)
            if output_hidden_states:
                return x, pooled, all_hidden
            return x, pooled
        if output_hidden_states:
            return x, all_hidden
        return x

    @classmethod
    def from_baize_checkpoint(
        cls,
        ckpt_path: str,
        config: BaizeVisionConfig | None = None,
        **kwargs,
    ) -> "BaizeVisionModel":
        """Load from a BaiZe training checkpoint (``vision.pt``).

        The checkpoint is a dict with key ``'vision'`` containing the
        OpenVision2 state_dict, plus a ``'config'`` dict with architecture
        parameters.  If ``config`` is None, it is auto-derived from the
        checkpoint's config dict.

        Parameters
        ----------
        ckpt_path : str
            Path to ``vision.pt``.
        config : BaizeVisionConfig, optional
            Override config.  If None, built from checkpoint's ``config`` dict.

        Returns
        -------
        model : BaizeVisionModel
            Model with weights loaded (``strict=True``).
        """
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        sd = ck["vision"]

        # Auto-derive config from checkpoint if not provided
        if config is None:
            cfg = ck.get("config", {})
            w = cfg.get("width", 512)
            d = cfg.get("depth", 30)
            h = cfg.get("heads") or max(1, w // 64)
            m = cfg.get("mlp_dim") or (4 * w)
            embed = cfg.get("embed_dim", 768)
            config = BaizeVisionConfig(
                image_size=cfg.get("resolution", 224),
                patch_size=cfg.get("patch", 16),
                width=w,
                depth=d,
                heads=h,
                mlp_dim=m,
                embed_dim=embed,
                spatial_merge_size=1,
            )

        model = cls(config)

        # Strip common prefixeses if present (visual., module.)
        # BaiZe's own checkpoints have no prefix; official OV2 uses "visual."
        if any(k.startswith("visual.") for k in sd):
            sd = {k.replace("visual.", "", 1): v
                  for k, v in sd.items() if k.startswith("visual.")}
        if any(k.startswith("module.") for k in sd):
            sd = {k.replace("module.", "", 1): v for k, v in sd.items()}

        # Load with strict=True and report match status
        result = model.load_state_dict(sd, strict=True)
        matched = len(sd) - len(result.missing_keys) - len(result.unexpected_keys)
        print(f"[BaizeVision] load_state_dict(strict=True): "
              f"matched={matched}/{len(sd)}, "
              f"missing={list(result.missing_keys)}, "
              f"unexpected={list(result.unexpected_keys)}")
        return model

