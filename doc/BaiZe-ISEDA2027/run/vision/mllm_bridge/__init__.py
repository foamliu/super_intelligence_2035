"""BaiZe MLLM Bridge — HF wrapper for BaiZe vision tower + custom LLaVA modeling.

This package provides:
  - BaizeVisionConfig / BaizeVisionModel: HuggingFace-compatible wrapper around
    the BaiZe OpenVision2 ViT (from-scratch, AIMv2-style trained).
  - LlavaBaizeForConditionalGeneration: custom LLaVA modeling that replaces the
    RICE vision tower with BaiZe's and adds a 2-layer MLP projector.

Usage:
  from mllm_bridge.configuration_baize_vision import BaizeVisionConfig
  from mllm_bridge.modeling_baize_vision import BaizeVisionModel
"""

from .configuration_baize_vision import BaizeVisionConfig
from .modeling_baize_vision import BaizeVisionModel

__all__ = ["BaizeVisionConfig", "BaizeVisionModel"]
