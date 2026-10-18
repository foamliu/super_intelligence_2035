#!/usr/bin/env python
"""CPU smoke test for ArmB -> MLLM Stage-2 pipeline (no GPU, no full LLM load).

Verifies the ArmB-specific pieces of stage2_train_armB.build_model that differ
from the proven ④ stage2_train.py:
  1. ArmB open_clip_state_dict.pt loads via create_baize_vitb16_768 (strict).
  2. encode_image([1,3,224,224]) -> [1,196,768] patch tokens.
  3. Projector 768->2560 loads from Stage-1.5 step20000 ckpt with strict=True
     (the key new risk: Stage-1.5 ckpt must match the 768-dim projector exactly,
      and Stage-1.5 must have actually finished).
  4. End-to-end vision + projector [1,3,224,224] -> [1,196,2560].
  5. Stage-1.5 LoRA adapter directory exists (PeftModel.from_pretrained target).
     (Full LoRA-on-Qwen3-4B load is already proven by ④ stage2_train.py, which
      ran 3500 steps exit 0; we only validate the adapter dir presence here to
      avoid loading the 4B LLM on CPU.)

Run (AFTER Stage-1.5 step20000 is written):
  cd run/vision
  python mllm_bridge/test_stage2_armB_smoke.py
"""
import sys, os

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/armB_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
STAGE15_FINAL = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armB/step20000"
PROJECTOR_CKPT = os.path.join(STAGE15_FINAL, "projector.pt")
VISION_DIM = 768
LLM_DIM = 2560


def main():
    print("=" * 60)
    print("ArmB -> MLLM Stage-2 CPU smoke test")
    print(f"Vision ckpt:       {CKPT}")
    print(f"Stage-1.5 final:   {STAGE15_FINAL}")
    print("=" * 60)

    # Gate: Stage-1.5 must have finished.
    if not os.path.isfile(PROJECTOR_CKPT):
        print(f"\n[!] Stage-1.5 final projector NOT found: {PROJECTOR_CKPT}")
        print("    Stage-1.5 has not finished yet. Run this smoke test AFTER step20000 is written.")
        sys.exit(2)

    print("\n[1] Load ArmB vision tower (strict)...")
    model, _, _ = create_baize_vitb16_768(pretrained=CKPT, device='cpu')
    model.eval()
    print("    strict load OK")

    print("\n[2] encode_image shape check...")
    with torch.no_grad():
        x = torch.randn(1, 3, 224, 224)
        feats = model.encode_image(x)
    print(f"    encode_image: {tuple(x.shape)} -> {tuple(feats.shape)} (expect (1, 196, {VISION_DIM}))")
    assert feats.shape == (1, 196, VISION_DIM), f"SHAPE MISMATCH: {feats.shape}"
    print("    PASSED")

    print("\n[3] Load projector 768->2560 from Stage-1.5 step20000 (strict=True)...")
    projector = BaizeMultiModalProjector(VISION_DIM, LLM_DIM)
    ck = torch.load(PROJECTOR_CKPT, map_location="cpu", weights_only=False)
    sd = ck.get('projector', ck) if isinstance(ck, dict) else ck
    sd = {k.replace('module.', '', 1) if k.startswith('module.') else k: v for k, v in sd.items()}
    result = projector.load_state_dict(sd, strict=True)
    n_proj = sum(p.numel() for p in projector.parameters())
    print(f"    projector params: {n_proj / 1e6:.2f}M")
    print(f"    keys loaded: {len(sd)}  missing={len(result.missing_keys)} unexpected={len(result.unexpected_keys)}")
    assert len(result.missing_keys) == 0, f"MISSING KEYS: {result.missing_keys}"
    assert len(result.unexpected_keys) == 0, f"UNEXPECTED KEYS: {result.unexpected_keys}"
    assert sd['fc1.weight'].shape == (LLM_DIM, VISION_DIM), \
        f"fc1.weight shape {sd['fc1.weight'].shape} != ({LLM_DIM},{VISION_DIM})"
    print(f"    fc1.weight={tuple(sd['fc1.weight'].shape)} (confirm 768->2560 input width)")
    print("    PASSED (Stage-1.5 projector loads strict into 768-dim Stage-2 projector)")

    print("\n[4] End-to-end [1,3,224,224] -> [1,196,2560] (frozen vision + loaded projector)...")
    with torch.no_grad():
        patch = model(x)
        embeds = projector(patch)
    print(f"    image {tuple(x.shape)} -> patch {tuple(patch.shape)} -> embeds {tuple(embeds.shape)}")
    assert patch.shape == (1, 196, VISION_DIM)
    assert embeds.shape == (1, 196, LLM_DIM)
    print("    PASSED")

    print("\n[5] Stage-1.5 LoRA adapter dir present (PeftModel.from_pretrained target)...")
    adapter_file = os.path.join(STAGE15_FINAL, "adapter_config.json")
    if os.path.isfile(adapter_file):
        print(f"    adapter_config.json FOUND at {STAGE15_FINAL}")
        print("    PASSED (full LoRA load on Qwen3-4B already validated by ④ stage2_train.py)")
    else:
        print(f"    [!] adapter_config.json NOT found at {adapter_file}")
        print("    Stage-1.5 save_checkpoint may not have written the PEFT adapter dir.")
        sys.exit(3)

    print("\n" + "=" * 60)
    print("ALL STAGE-2 SMOKE TESTS PASSED  (ArmB 768 tower + Stage-1.5 projector + LoRA dir OK)")
    print("=" * 60)


if __name__ == '__main__':
    main()
