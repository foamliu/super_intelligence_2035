"""Custom LLaVA modeling with BaiZe vision tower.

This module provides the components needed to build a LLaVA-style multimodal
model that uses the BaiZe OpenVision2 ViT as the vision encoder instead of
the RICE ViT used in LLaVA-OneVision-1.5.

Key differences from the original LLaVA-OV1.5 (RICE ViT):
  1. **Vision tower**: BaiZe OpenVision2 (w512/d30/p16/224px) replaces RICE
     ViT (w1024/d24/p14/336px).
  2. **Patch tokens**: 196 (14x14) direct output — **no spatial merge**
     (``spatial_merge_size=1``).  RICE outputs 576/4 = 144 merged tokens.
  3. **Projector**: 2-layer MLP (width -> llm_hidden_size) as a separate
     module.  In RICE, the PatchMerger inside the vision tower acts as the
     projector; here we use an explicit ``MultiModalProjector``.
  4. **Stage-1 resolution**: fixed 224px (BaiZe's training resolution).

Design
------
The full LLaVA-OV1.5 modeling file (2144 lines) is tightly coupled with
Qwen2VL's RoPE, cache, and attention infrastructure.  Rather than copy all
of it, this module provides:

  - :class:`BaizeMultiModalProjector`: 2-layer MLP (GELU activation).
  - :class:`LlavaBaizeModel`: combines vision tower + projector + LLM,
    with ``get_image_features()`` that returns projected 196-token embeddings.
  - :class:`LlavaBaizeForConditionalGeneration`: thin wrapper for HF
    ``AutoModelForCausalLM`` compatibility (delegates to the base LLM's
    ``forward`` with image embeddings injected into ``inputs_embeds``).

Integration with ms-swift
-------------------------
ms-swift loads the model via ``AutoModelForCausalLM.from_pretrained()``
using the ``auto_map`` in ``config.json``.  The LLM (Qwen3-4B) is loaded
separately and passed as ``language_model``.  During ``swift sft/pretrain``,
ms-swift handles the data pipeline and token replacement; this modeling
file provides the ``get_image_features`` method that ms-swift's LLaVA
template calls to obtain visual embeddings.

Example
-------
>>> from mllm_bridge.modeling_baize_vision import BaizeVisionModel
>>> from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector
>>> vision = BaizeVisionModel.from_baize_checkpoint("vision.pt")
>>> projector = BaizeMultiModalProjector(vision.config.width, 2560)
>>> feats = vision(pixel_values)          # [B, 196, 512]
>>> embeds = projector(feats)             # [B, 196, 2560]
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .modeling_baize_vision import BaizeVisionModel
from .configuration_baize_vision import BaizeVisionConfig


class BaizeMultiModalProjector(nn.Module):
    """2-layer MLP projector: vision_width -> llm_hidden_size.

    Architecture (matching LLaVA convention):
        Linear(width, llm_hidden_size) -> GELU -> Linear(llm_hidden_size, llm_hidden_size)

    For BaiZe ④-4ep + Qwen3-4B: 512 -> 2560 -> 2560.

    Parameters
    ----------
    vision_hidden_size : int
        Output dimension of the BaiZe vision tower (512 for ④-4ep).
    llm_hidden_size : int
        Hidden size of the LLM (2560 for Qwen3-4B).
    """

    def __init__(self, vision_hidden_size: int, llm_hidden_size: int):
        super().__init__()
        self.fc1 = nn.Linear(vision_hidden_size, llm_hidden_size)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(llm_hidden_size, llm_hidden_size)

    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))


class LlavaBaizeModel(nn.Module):
    """LLaVA-style model: BaiZe vision tower + projector + LLM.

    This is a lightweight wrapper that provides the ``get_image_features``
    method (analogous to ``LLaVAOneVision1_5_Model.get_image_features``).
    The LLM is passed in as an existing HF model (e.g. Qwen3-4B).

    Parameters
    ----------
    vision_tower : BaizeVisionModel
        BaiZe vision encoder with loaded weights.
    llm_hidden_size : int
        Hidden size of the LLM (determines projector output dim).
    language_model : nn.Module, optional
        The LLM (e.g. ``Qwen3ForCausalLM``).  If None, only vision + projector
        are available (useful for testing).
    """

    def __init__(
        self,
        vision_tower: BaizeVisionModel,
        llm_hidden_size: int,
        language_model: nn.Module | None = None,
    ):
        super().__init__()
        self.vision_tower = vision_tower
        self.multi_modal_projector = BaizeMultiModalProjector(
            vision_tower.config.width, llm_hidden_size
        )
        self.language_model = language_model
        self.num_image_tokens = vision_tower.num_patches  # 196

    @torch.no_grad()
    def get_image_features(self, pixel_values: torch.FloatTensor) -> torch.Tensor:
        """Encode images into LLM-space embeddings.

        Parameters
        ----------
        pixel_values : Tensor[B, 3, 224, 224]
            Normalised image batch.

        Returns
        -------
        image_embeds : Tensor[B, 196, llm_hidden_size]
            Projected patch embeddings ready to be injected into ``inputs_embeds``.
        """
        # Vision tower: [B, 3, 224, 224] -> [B, 196, width]
        patch_features = self.vision_tower(pixel_values)
        # Projector: [B, 196, width] -> [B, 196, llm_hidden_size]
        image_embeds = self.multi_modal_projector(patch_features)
        return image_embeds

    def forward(
        self,
        input_ids: torch.LongTensor,
        pixel_values: torch.FloatTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        labels: torch.LongTensor | None = None,
        image_token_id: int = 151655,
        **kwargs,
    ):
        """Forward pass: inject image embeddings into LLM input embeddings.

        This follows the LLaVA pattern:
        1. Get LLM input embeddings from ``input_ids``.
        2. If ``pixel_values`` is provided, compute image embeddings and
           scatter them into the positions where ``input_ids == image_token_id``.
        3. Forward through the LLM.

        Parameters
        ----------
        input_ids : Tensor[B, seq_len]
            Token IDs.  Image positions are marked with ``image_token_id``.
        pixel_values : Tensor[B, 3, 224, 224], optional
            Images.  ``B`` must equal the number of image_token markers.
        image_token_id : int
            Token ID used as placeholder for image tokens (default 151655,
            matching LLaVA-OV1.5's ``image_token_id``).

        Returns
        -------
        output : CausalLMOutput
            The LLM's output.
        """
        if self.language_model is None:
            raise RuntimeError("language_model is not set; cannot run forward().")

        # Get base text embeddings
        inputs_embeds = self.language_model.get_input_embeddings()(input_ids)

        # Inject image embeddings if provided
        if pixel_values is not None:
            image_embeds = self.get_image_features(pixel_values)  # [num_images, 196, llm_hidden_size]
            # Flatten image_embeds to [total_image_tokens, llm_hidden_size]
            image_embeds = image_embeds.reshape(-1, image_embeds.shape[-1])

            # Scatter into input embeddings at image_token positions
            image_mask = (input_ids == image_token_id).unsqueeze(-1).expand_as(inputs_embeds)
            inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds.to(inputs_embeds.dtype))

        # Forward through LLM
        return self.language_model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            labels=labels,
            **kwargs,
        )
