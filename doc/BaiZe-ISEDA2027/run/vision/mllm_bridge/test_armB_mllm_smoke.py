#!/usr/bin/env python
"""CPU smoke test for ArmB -> MLLM Stage-1 pipeline (no GPU needed).

Verifies (operator instruction 2026-10-18 P0 ③-3):
  1. ArmB open_clip_state_dict.pt loads via create_baize_vitb16_768 (strict).
  2. encode_image([1,3,224,224]) -> [1,196,768] patch tokens.
  3. BaizeMultiModalProjector(768, 2560) forward [1,196,768] -> [1,196,2560].
  4. End-to-end vision + projector [1,3,224,224] -> [1,196,2560].

Run:
  cd run/vision
  python mllm_bridge/test_armB_mllm_smoke.py
"""
import sys, os

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/armB_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
VISION_DIM = 768
LLM_DIM = 2560


def main():
    print("=" * 60)
    print("ArmB -> MLLM Stage-1 CPU smoke test")
    print(f"Checkpoint: {CKPT}")
    print("=" * 60)

    print("\n[1] Load ArmB vision tower (strict)...")
    model, _, _ = create_baize_vitb16_768(pretrained=CKPT, device='cpu')
    model.eval()
    print("    strict load OK (create_baize_vitb16_768 uses strict=True)")

    print("\n[2] encode_image shape check...")
    with torch.no_grad():
        x = torch.randn(1, 3, 224, 224)
        feats = model.encode_image(x)
    print(f"    encode_image: {tuple(x.shape)} -> {tuple(feats.shape)} (expect (1, 196, {VISION_DIM}))")
    assert feats.shape == (1, 196, VISION_DIM), f"SHAPE MISMATCH: {feats.shape}"
    print("    PASSED")

    print("\n[3] Projector 768->2560 shape check...")
    projector = BaizeMultiModalProjector(VISION_DIM, LLM_DIM)
    with torch.no_grad():
        proj_out = projector(feats)
    print(f"    projector: {tuple(feats.shape)} -> {tuple(proj_out.shape)} (expect (1, 196, {LLM_DIM}))")
    assert proj_out.shape == (1, 196, LLM_DIM), f"SHAPE MISMATCH: {proj_out.shape}"
    n_proj = sum(p.numel() for p in projector.parameters())
    expected = VISION_DIM * LLM_DIM + LLM_DIM + LLM_DIM * LLM_DIM + LLM_DIM
    print(f"    projector params: {n_proj / 1e6:.2f}M (expected {expected / 1e6:.2f}M)")
    assert n_proj == expected, f"proj param count mismatch: {n_proj} != {expected}"
    print("    PASSED")

    print("\n[4] End-to-end [1,3,224,224] -> [1,196,2560]...")
    with torch.no_grad():
        x2 = torch.randn(1, 3, 224, 224)
        patch = model(x2)            # forward -> encode_image -> [1,196,768]
        embeds = projector(patch)    # -> [1,196,2560]
    print(f"    image {tuple(x2.shape)} -> patch {tuple(patch.shape)} -> embeds {tuple(embeds.shape)}")
    assert patch.shape == (1, 196, VISION_DIM)
    assert embeds.shape == (1, 196, LLM_DIM)
    print("    PASSED")

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED  (ArmB 768 -> projector 2560 pipeline OK)")
    print("=" * 60)


if __name__ == '__main__':
    main()
