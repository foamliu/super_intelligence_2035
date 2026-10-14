"""Configuration for the BaiZe vision tower (HF PretrainedConfig subclass).

The BaiZe vision tower is a from-scratch OpenVision2 ViT trained with an
AIMv2-style dense objective (InfoNCE + masked-patch-MSE).  This config mirrors
the architecture parameters stored in the training checkpoint's ``config`` dict
so that ``BaizeVisionModel`` can be constructed and weights loaded with
``strict=True``.

model_type: ``baize_vision``
"""

from __future__ import annotations

from transformers import PretrainedConfig


class BaizeVisionConfig(PretrainedConfig):
    """Configuration for :class:`BaizeVisionModel`.

    Parameters
    ----------
    image_size : int
        Input image resolution (default 224).
    patch_size : int
        ViT patch size (default 16).  ``grid = image_size // patch_size``.
    width : int
        Transformer hidden dimension (default 512, matching the ④-4ep
        checkpoint).  The OpenVision2 *class* default in ``models.py`` is 1024,
        but the actual trained model uses 512.
    depth : int
        Number of transformer blocks (default 30).
    heads : int
        Number of attention heads (default 8 = 512 // 64).
    mlp_dim : int
        SwiGLU MLP intermediate dimension (default 2048 = 4 × 512).
    spatial_merge_size : int
        Spatial merge factor — **1** for BaiZe (no merge, 196 tokens direct).
        RICE ViT uses 2 (576 / 4 = 144 tokens).  Kept in config for interface
        compatibility with LLaVA-OV1.5 code that reads this field.
    embed_dim : int
        ReadoutHead output dimension (768, aligning with frozen CLIP-L/14-336
        text tower).  **Not used** by the MLLM bridge (ReadoutHead is skipped);
        kept so that ``strict=True`` weight loading succeeds.
    """

    model_type = "baize_vision"

    def __init__(
        self,
        image_size: int = 224,
        patch_size: int = 16,
        width: int = 512,
        depth: int = 30,
        heads: int = 8,
        mlp_dim: int = 2048,
        spatial_merge_size: int = 1,
        embed_dim: int = 768,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.patch_size = patch_size
        self.width = width
        self.depth = depth
        self.heads = heads
        self.mlp_dim = mlp_dim
        self.spatial_merge_size = spatial_merge_size
        self.embed_dim = embed_dim

    @property
    def num_patches(self) -> int:
        """Number of patch tokens = (image_size / patch_size)²."""
        grid = self.image_size // self.patch_size
        return grid * grid
