#!/usr/bin/env python
"""Export ArmB checkpoint for LLaVA-OneVision / lmms-eval.

Takes the ArmB training output (open_clip_state_dict.pt) and exports it
in a format usable by the BaiZe ViT-B/16 bridge for LLaVA-OV pipelines.

Usage:
  python export_for_llava_ov.py --ckpt /path/to/open_clip_state_dict.pt \
      --output /path/to/export_dir
"""
import argparse
import os
import sys
import json
import torch

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)

import open_clip
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768

MODEL_NAME = 'baize-vitb16-768'
IMAGE_SIZE = 224
PATCH_SIZE = 16
WIDTH = 768


def main():
    ap = argparse.ArgumentParser(description='Export ArmB ckpt for LLaVA-OV')
    ap.add_argument('--ckpt', required=True, help='path to open_clip_state_dict.pt')
    ap.add_argument('--output', required=True, help='output directory')
    ap.add_argument('--projector-dim', type=int, default=None,
                    help='LLM hidden dim for projector (e.g. 2560 for Qwen3-2B)')
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Load via bridge
    model, preprocess, _ = create_baize_vitb16_768(
        pretrained=args.ckpt, device='cpu')
    model.eval()

    # Verify encode_image output shape
    dummy = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    with torch.no_grad():
        feats = model.encode_image(dummy)
    assert feats.shape == (1, 196, WIDTH), f"encode_image {feats.shape} != (1, 196, {WIDTH})"
    print(f"[export] encode_image -> {feats.shape} (OK)")

    # Save export
    export_path = os.path.join(args.output, 'baize_vitb16_768_export.pt')
    torch.save({
        'state_dict': model.clip.state_dict(),
        'config': {
            'model_name': 'baize-vitb16-768',
            'image_size': IMAGE_SIZE,
            'patch_size': PATCH_SIZE,
            'hidden_size': WIDTH,
            'num_patches': 196,
            'spatial_merge_size': 1,
        },
    }, export_path)
    print(f"[export] saved {export_path} ({os.path.getsize(export_path)/1e6:.1f}MB)")

    # Optional projector (768 -> LLM dim)
    if args.projector_dim:
        projector = torch.nn.Linear(WIDTH, args.projector_dim)
        proj_path = os.path.join(args.output, 'projector.pt')
        torch.save(projector.state_dict(), proj_path)
        # Test projector shape
        with torch.no_grad():
            proj_out = projector(feats)
        assert proj_out.shape == (1, 196, args.projector_dim)
        print(f"[export] projector {WIDTH}->{args.projector_dim} -> {proj_out.shape} saved {proj_path}")

    # Config JSON
    with open(os.path.join(args.output, 'config.json'), 'w') as f:
        json.dump({
            'model_name': 'baize-vitb16-768',
            'image_size': IMAGE_SIZE,
            'patch_size': PATCH_SIZE,
            'hidden_size': WIDTH,
            'num_patches': 196,
            'spatial_merge_size': 1,
            'source_ckpt': args.ckpt,
            'projector_dim': args.projector_dim,
        }, f, indent=2)
    print(f"[export] config.json written")
    print("[export] DONE")


if __name__ == '__main__':
    main()
