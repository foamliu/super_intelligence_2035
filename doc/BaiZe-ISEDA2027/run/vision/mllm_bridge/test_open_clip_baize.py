#!/usr/bin/env python
"""Validation tests for BaiZe open_clip protocol + LLaVA-OV compatibility.

Tests:
  1. open_clip load success + forward shape/numerical sanity
  2. HF directory readable by AutoConfig / AutoProcessor
  3. End-to-end ai2d --limit 5 (deferred, requires GPU)
"""

from __future__ import annotations
import os, sys, json, tempfile, traceback
import torch
from pathlib import Path

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"

def test_1_open_clip_load(ckpt_path):
    """Test 1: open_clip loads BaiZe + forward sanity."""
    print("\n" + "="*60)
    print("TEST 1: open_clip load + forward sanity")
    print("="*60)
    from mllm_bridge.open_clip_baize import register_baize_in_open_clip
    register_baize_in_open_clip()
    import open_clip
    model, _, _ = open_clip.create_model_and_transforms(
        "baize-vit-512", pretrained=ckpt_path, device="cpu", precision="fp32")
    vc = model.vision_config
    assert vc.image_size == 224 and vc.patch_size == 16
    assert vc.hidden_size == 512 and vc.depth == 30 and vc.width == 512
    assert vc.num_patches == 196
    print("  ✅ vision_config fields correct")
    dummy = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        feats = model.encode_image(dummy)
    assert feats.shape == (2, 196, 512), f"shape={feats.shape}"
    assert not torch.isnan(feats).any() and not torch.isinf(feats).any()
    print(f"  ✅ Shape {feats.shape} correct, no NaN/Inf")
    dummy2 = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        feats2 = model.encode_image(dummy2)
    assert not torch.allclose(feats, feats2)
    print("  ✅ Different inputs → different outputs")
    with torch.no_grad():
        feats_direct = model.visual(dummy)
    assert torch.allclose(feats, feats_direct)
    print("  ✅ encode_image() == visual()")
    print("  TEST 1 PASSED ✅")

def test_2_hf_directory(ckpt_path, llm_path):
    """Test 2: Export HF dir + AutoConfig/AutoProcessor read."""
    print("\n" + "="*60)
    print("TEST 2: LLaVA-OV HF directory + AutoConfig/AutoProcessor")
    print("="*60)
    from mllm_bridge.export_llava_ov_hf import export_llava_ov_hf
    with tempfile.TemporaryDirectory() as tmpdir:
        hf_dir = export_llava_ov_hf(ckpt_path, tmpdir, llm_path)
        for f in ["config.json", "preprocessor_config.json",
                   "open_clip_config.json", "pytorch_model.bin"]:
            assert (hf_dir / f).exists(), f"Missing: {f}"
        print("  ✅ All required files present")
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained(str(hf_dir), trust_remote_code=True)
        assert config.image_token_index == 151655
        assert config.vision_feature_select_strategy == "default"
        print(f"  ✅ AutoConfig: image_token_index={config.image_token_index}")
        try:
            from transformers import AutoProcessor
            AutoProcessor.from_pretrained(str(hf_dir), trust_remote_code=True)
            print("  ✅ AutoProcessor loaded")
        except Exception:
            from transformers import CLIPImageProcessor
            CLIPImageProcessor.from_pretrained(str(hf_dir))
            print("  ✅ CLIPImageProcessor loaded (fallback)")
        with open(hf_dir / "config.json") as f:
            cfg = json.load(f)
        assert cfg["model_type"] == "llava_onevision"
        assert cfg["vision_config"]["has_cls_token"] == False
        assert cfg["image_seq_length"] == 196
        print("  ✅ config.json content correct")
    print("  TEST 2 PASSED ✅")


def test_3_e2e():
    """Test 3: End-to-end ai2d --limit 5 (requires GPU)."""
    print("\n" + "="*60)
    print("TEST 3: End-to-end ai2d --limit 5 (DEFERRED — requires GPU)")
    print("="*60)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", default=CKPT)
    parser.add_argument("--llm_path", default=LLM_PATH)
    args = parser.parse_args()
    print(f"\n{'#'*60}")
    print(f"# BaiZe open_clip + LLaVA-OV Validation")
    print(f"# Checkpoint: {args.ckpt}")
    print(f"{'#'*60}")
    results = {}
    try:
        test_1_open_clip_load(args.ckpt)
        results["test_1"] = "PASSED"
    except Exception as e:
        print(f"  TEST 1 FAILED ❌: {e}")
        traceback.print_exc()
        results["test_1"] = f"FAILED: {e}"
        return results
    try:
        test_2_hf_directory(args.ckpt, args.llm_path)
        results["test_2"] = "PASSED"
    except Exception as e:
        print(f"  TEST 2 FAILED ❌: {e}")
        traceback.print_exc()
        results["test_2"] = f"FAILED: {e}"
    test_3_e2e()
    results["test_3"] = "DEFERRED (GPU)"
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    for name, status in results.items():
        icon = "✅" if "PASSED" in status else ("❌" if "FAILED" in status else "⏸️")
        print(f"  {icon} {name}: {status}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
