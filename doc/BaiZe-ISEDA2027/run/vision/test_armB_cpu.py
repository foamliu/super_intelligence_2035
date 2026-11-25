#!/usr/bin/env python
"""CPU unit tests for ArmB (open_clip ViT-B/16 + AIMv2-style).

Tests (all CPU, no GPU):
  1. Model creation + predictor attachment
  2. Forward hook captures patch tokens [B, 196, 768]
  3. PatchPredictor forward shape [M, 768]
  4. mae_norm_pix_target shape [B, 196, 768]
  5. Save open_clip_state_dict.pt -> strict load passes
  6. AIMv2-style loss computation

Run: python test_armB_cpu.py
"""
import os, sys, tempfile
import torch
import torch.nn as nn

VISION_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)

import open_clip
from armB_aimv2_openclip import (
    ArmBModel, PatchPredictor, mae_norm_pix_target,
    MODEL_NAME, PATCH_SIZE, IMAGE_SIZE, N_PATCHES, PATCH_DIM, WIDTH)


def test_1_model_creation():
    print("=" * 60)
    print("Test 1: Model creation + predictor")
    clip_model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=None)
    n_visual = sum(p.numel() for p in clip_model.visual.parameters())
    n_total = sum(p.numel() for p in clip_model.parameters())
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    n_pred = sum(p.numel() for p in predictor.parameters())
    assert n_visual == 86192640, f"visual {n_visual} != 86192640"
    assert n_total == 149620737, f"total {n_total} != 149620737"
    print(f"  visual={n_visual/1e6:.1f}M total={n_total/1e6:.1f}M predictor={n_pred/1e6:.2f}M")
    print("  PASSED")


def test_2_forward_hook():
    print("=" * 60)
    print("Test 2: Forward hook patch token extraction")
    clip_model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=None)
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    model = ArmBModel(clip_model, predictor)
    model.eval()
    imgs = torch.randn(2, 3, IMAGE_SIZE, IMAGE_SIZE)
    texts = open_clip.get_tokenizer(MODEL_NAME)(["a cat", "a dog"])
    with torch.no_grad():
        img_feat, txt_feat, logit_scale, patch_tokens = model(imgs, texts)
    assert img_feat.shape == (2, 512), f"img_feat {img_feat.shape}"
    assert patch_tokens.shape == (2, N_PATCHES, WIDTH), f"patch {patch_tokens.shape}"
    print(f"  img_feat={img_feat.shape} patch_tokens={patch_tokens.shape}")
    print("  PASSED")


def test_3_predictor():
    print("=" * 60)
    print("Test 3: PatchPredictor forward")
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    x = torch.randn(100, WIDTH)
    out = predictor(x)
    assert out.shape == (100, PATCH_DIM), f"out {out.shape} != (100, {PATCH_DIM})"
    n_pred = sum(p.numel() for p in predictor.parameters())
    print(f"  input=(100,{WIDTH}) -> output={out.shape} params={n_pred/1e6:.2f}M")
    print("  PASSED")


def test_4_mae_target():
    print("=" * 60)
    print("Test 4: mae_norm_pix_target")
    imgs = torch.randn(4, 3, IMAGE_SIZE, IMAGE_SIZE)
    target = mae_norm_pix_target(imgs, PATCH_SIZE)
    assert target.shape == (4, N_PATCHES, PATCH_DIM), f"target {target.shape}"
    mean_pp = target.mean(dim=-1)
    std_pp = target.std(dim=-1)
    assert mean_pp.abs().max() < 1e-5, f"mean {mean_pp.abs().max()}"
    assert (std_pp - 1.0).abs().max() < 1e-4, f"std {(std_pp-1.0).abs().max()}"
    print(f"  target={target.shape} per-patch mean~{mean_pp.abs().max():.2e}")
    print("  PASSED")


def test_5_strict_load():
    print("=" * 60)
    print("Test 5: open_clip strict load (strip predictor)")
    clip_model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=None)
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    wrapper = ArmBModel(clip_model, predictor)
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = os.path.join(tmpdir, 'open_clip_state_dict.pt')
        torch.save(wrapper.clip.state_dict(), ckpt_path)
        fresh, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=None)
        sd = torch.load(ckpt_path, map_location='cpu')
        result = fresh.load_state_dict(sd, strict=True)
        assert not result.missing_keys, f"missing: {result.missing_keys}"
        assert not result.unexpected_keys, f"unexpected: {result.unexpected_keys}"
        print(f"  saved {os.path.getsize(ckpt_path)/1e6:.1f}MB, strict load: 0 missing/unexpected")
        print("  PASSED")


def test_6_mask_loss():
    print("=" * 60)
    print("Test 6: AIMv2-style loss computation")
    clip_model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=None)
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    model = ArmBModel(clip_model, predictor)
    model.eval()
    imgs = torch.randn(2, 3, IMAGE_SIZE, IMAGE_SIZE)
    texts = open_clip.get_tokenizer(MODEL_NAME)(["a cat", "a dog"])
    with torch.no_grad():
        img_feat, txt_feat, logit_scale, patch_tokens = model(imgs, texts)
        img_n = torch.nn.functional.normalize(img_feat, dim=-1)
        txt_n = torch.nn.functional.normalize(txt_feat, dim=-1)
        contrastive = torch.nn.functional.cross_entropy(
            logit_scale * img_n @ txt_n.T, torch.arange(2))
        target = mae_norm_pix_target(imgs, PATCH_SIZE)
        mrand = torch.rand(2, N_PATCHES) < 0.6
        pred = predictor(patch_tokens[mrand])
        patch_loss = torch.mean((pred.float() - target[mrand].float()) ** 2)
        loss = contrastive + patch_loss
    assert loss.item() > 0
    print(f"  contrastive={contrastive.item():.4f} patch={patch_loss.item():.4f} "
          f"total={loss.item():.4f} masked={mrand.sum().item()}/{2*N_PATCHES}")
    print("  PASSED")


if __name__ == '__main__':
    test_1_model_creation()
    test_2_forward_hook()
    test_3_predictor()
    test_4_mae_target()
    test_5_strict_load()
    test_6_mask_loss()
    print("=" * 60)
    print("ALL CPU TESTS PASSED")
