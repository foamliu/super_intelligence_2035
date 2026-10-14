#!/usr/bin/env python
"""CPU unit tests for the BaiZe vision tower HF wrapper.

All tests run on CPU only -- no GPU required.  Run with:

    cd run/vision
    python mllm_bridge/test_wrapper_cpu.py

Tests
-----
1. Wrapper loads ④-4ep checkpoint with strict=True (no missing/unexpected keys).
2. Random [1,3,224,224] forward -> patch output is [1,196,512].
3. Wrapper output matches original OpenVision2.forward(return_patch=True)
   element-wise (torch.allclose) -- proves the wrapper is lossless.
4. Projector forward [1,196,512] -> [1,196,2560].
5. End-to-end vision + projector [1,3,224,224] -> [1,196,2560].
"""

import sys
import os

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"


def test_1_checkpoint_loading():
    """Test 1: Wrapper loads ckpt with strict=True."""
    print("=" * 60)
    print("Test 1: Checkpoint loading (strict=True)")
    print("=" * 60)
    model = BaizeVisionModel.from_baize_checkpoint(CKPT)
    model.eval()
    cfg = model.config
    print(f"  Config: w={cfg.width} d={cfg.depth} h={cfg.heads} m={cfg.mlp_dim}")
    assert cfg.width == 512
    assert cfg.depth == 30
    assert cfg.num_patches == 196
    n = sum(p.numel() for p in model.parameters())
    print(f"  Total params: {n / 1e6:.2f}M")
    print("  PASSED\n")
    return model


def test_2_forward_shape(model):
    """Test 2: Forward [1,3,224,224] -> [1,196,512]."""
    print("=" * 60)
    print("Test 2: Forward shape")
    print("=" * 60)
    with torch.no_grad():
        x = torch.randn(1, 3, 224, 224)
        out = model(x)
    print(f"  Input:  {tuple(x.shape)} -> Output: {tuple(out.shape)}")
    assert out.shape == (1, 196, 512)
    print("  PASSED\n")


def test_3_equivalence(model):
    """Test 3: Wrapper == original OpenVision2.forward(return_patch=True)."""
    print("=" * 60)
    print("Test 3: Equivalence with original OpenVision2")
    print("=" * 60)
    import models
    from models import get_vision_tower, ReadoutHead

    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    orig = get_vision_tower("openvision2", width=cfg.get("width"),
                            depth=cfg.get("depth"), heads=cfg.get("heads"),
                            mlp_dim=cfg.get("mlp_dim"))
    orig.head = ReadoutHead(orig.head.proj.in_features, embed_dim=cfg.get("embed_dim", 768))
    orig.load_state_dict(ck["vision"])
    orig.eval()

    torch.manual_seed(42)
    x = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        _, patch_orig = orig(x, return_patch=True)
        patch_wrap = model(x)

    diff = (patch_orig - patch_wrap).abs()
    print(f"  Max abs diff: {diff.max().item():.2e}")
    assert torch.allclose(patch_orig, patch_wrap, atol=1e-6, rtol=1e-5)
    print("  PASSED (torch.allclose, atol=1e-6)\n")


def test_4_projector():
    """Test 4: Projector [1,196,512] -> [1,196,2560]."""
    print("=" * 60)
    print("Test 4: Projector [1,196,512] -> [1,196,2560]")
    print("=" * 60)
    proj = BaizeMultiModalProjector(512, 2560)
    x = torch.randn(1, 196, 512)
    with torch.no_grad():
        out = proj(x)
    print(f"  Input: {tuple(x.shape)} -> Output: {tuple(out.shape)}")
    assert out.shape == (1, 196, 2560)
    n = sum(p.numel() for p in proj.parameters())
    print(f"  Projector params: {n / 1e6:.2f}M")
    expected = 512 * 2560 + 2560 + 2560 * 2560 + 2560
    assert n == expected, f"Expected {expected}, got {n}"
    print("  PASSED\n")


def test_5_e2e(model):
    """Test 5: End-to-end vision + projector [1,3,224,224] -> [1,196,2560]."""
    print("=" * 60)
    print("Test 5: End-to-end vision + projector")
    print("=" * 60)
    proj = BaizeMultiModalProjector(512, 2560)
    with torch.no_grad():
        x = torch.randn(1, 3, 224, 224)
        patch = model(x)
        embeds = proj(patch)
    print(f"  Image: {tuple(x.shape)} -> Patch: {tuple(patch.shape)} -> Embeds: {tuple(embeds.shape)}")
    assert embeds.shape == (1, 196, 2560)
    print("  PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BaiZe Vision Tower HF Wrapper -- CPU Unit Tests")
    print(f"Checkpoint: {CKPT}")
    print("=" * 60 + "\n")

    model = test_1_checkpoint_loading()
    test_2_forward_shape(model)
    test_3_equivalence(model)
    test_4_projector()
    test_5_e2e(model)

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
