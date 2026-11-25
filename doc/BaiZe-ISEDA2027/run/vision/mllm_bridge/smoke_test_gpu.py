#!/usr/bin/env python
"""GPU smoke test for BaiZe MLLM bridge: vision tower + projector + Qwen3-4B.

Tests:
  1. BaiZe vision tower loads from ④-4ep checkpoint onto GPU.
  2. Projector (2-layer MLP 512->2560) initialises on GPU.
  3. Qwen3-4B-Instruct-2507 loads onto GPU in bf16.
  4. Full forward: image -> vision -> projector -> inject into LLM -> logits.
  5. Loss computation (cross-entropy with dummy labels).
  6. Backward through projector (gradient flow verification).

Usage:
  cd run/vision
  python mllm_bridge/smoke_test_gpu.py
  CUDA_VISIBLE_DEVICES=2 python mllm_bridge/smoke_test_gpu.py
"""

import sys, os, time, traceback

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560


def _sec(t):
    print("\n" + "=" * 70 + f"\n  {t}\n" + "=" * 70)

def _ok(m):
    print(f"  PASS {m}")

def _fail(m):
    print(f"  FAIL {m}")
    raise AssertionError(m)

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        _fail("CUDA not available -- this test requires a GPU.")
    print(f"\nGPU: {torch.cuda.get_device_name(0)}  ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)")

    # --- Test 1: Vision tower ---
    _sec("Test 1: Load BaiZe vision tower (4ep) onto GPU")
    t0 = time.time()
    vision = BaizeVisionModel.from_baize_checkpoint(CKPT).to(device).eval()
    t1 = time.time()
    nv = sum(p.numel() for p in vision.parameters())
    print(f"  Params: {nv/1e6:.2f}M  Load: {t1-t0:.1f}s  Device: {next(vision.parameters()).device}")
    _ok("Vision tower loaded")

    # --- Test 2: Projector ---
    _sec("Test 2: Projector (2-layer MLP 512->2560) on GPU")
    projector = BaizeMultiModalProjector(vision.config.width, LLM_HIDDEN_SIZE).to(device)
    np_ = sum(p.numel() for p in projector.parameters())
    print(f"  Params: {np_/1e6:.2f}M  Linear({vision.config.width}->{LLM_HIDDEN_SIZE})->GELU->Linear({LLM_HIDDEN_SIZE}->{LLM_HIDDEN_SIZE})")
    _ok("Projector on GPU")

    # --- Test 3: Qwen3-4B ---
    _sec("Test 3: Load Qwen3-4B-Instruct-2507 (bf16)")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    llm = AutoModelForCausalLM.from_pretrained(LLM_PATH, torch_dtype=torch.bfloat16, trust_remote_code=True).to(device)
    t1 = time.time()
    nl = sum(p.numel() for p in llm.parameters())
    print(f"  Params: {nl/1e9:.2f}B  Load: {t1-t0:.1f}s  Vocab: {llm.config.vocab_size}  Hidden: {llm.config.hidden_size}")
    _ok("Qwen3-4B loaded in bf16")

    # --- Test 4: Vision + Projector forward ---
    _sec("Test 4: Vision tower + Projector forward on GPU")
    bs = 2
    dummy_images = torch.randn(bs, 3, 224, 224, device=device)
    with torch.no_grad():
        patch_feats = vision(dummy_images)
        print(f"  Vision: {tuple(patch_feats.shape)}  (expected: ({bs}, 196, 512))")
        assert patch_feats.shape == (bs, 196, 512), f"Got {tuple(patch_feats.shape)}"
        image_embeds = projector(patch_feats)
        print(f"  Projector: {tuple(image_embeds.shape)}  (expected: ({bs}, 196, 2560))")
        assert image_embeds.shape == (bs, 196, 2560), f"Got {tuple(image_embeds.shape)}"
    _ok("Vision + Projector forward shapes correct")

    # --- Test 5: Full forward (inject image embeds into LLM) ---
    _sec("Test 5: Full forward (vision -> projector -> LLM)")
    text = "Describe this image."
    text_ids = tokenizer.encode(text, add_special_tokens=False)
    ids_list = [IMAGE_TOKEN_ID] * NUM_IMAGE_TOKENS + text_ids
    if tokenizer.bos_token_id is not None:
        ids_list = [tokenizer.bos_token_id] + ids_list
    input_ids = torch.tensor([ids_list] * bs, dtype=torch.long, device=device)
    attn_mask = torch.ones_like(input_ids)
    print(f"  Seq len: {input_ids.shape[1]}  Image tokens: {NUM_IMAGE_TOKENS}  Text tokens: {len(text_ids)}")

    llm.eval()
    with torch.no_grad():
        embed_layer = llm.get_input_embeddings()
        inputs_embeds = embed_layer(input_ids)
        print(f"  LLM embeds (before injection): {tuple(inputs_embeds.shape)}")
        image_mask = (input_ids == IMAGE_TOKEN_ID).unsqueeze(-1).expand_as(inputs_embeds)
        print(f"  Image positions: {image_mask[0].any(dim=-1).sum().item()} per sample")
        image_embeds_flat = image_embeds.reshape(-1, image_embeds.shape[-1])
        inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds_flat.to(inputs_embeds.dtype))
        outputs = llm(inputs_embeds=inputs_embeds, attention_mask=attn_mask)
        logits = outputs.logits
        print(f"  Logits: {tuple(logits.shape)}  (expected: ({bs}, {input_ids.shape[1]}, {llm.config.vocab_size}))")
        assert logits.shape == (bs, input_ids.shape[1], llm.config.vocab_size)
    _ok("Full forward pass -- logits shape correct")

    # --- Test 6: Loss computation ---
    _sec("Test 6: Cross-entropy loss computation")
    with torch.no_grad():
        labels = input_ids.clone()
        labels[labels == IMAGE_TOKEN_ID] = -100
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        loss_fct = torch.nn.CrossEntropyLoss()
        loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        print(f"  Loss: {loss.item():.4f}  finite: {torch.isfinite(loss)}")
        assert torch.isfinite(loss)
    _ok("Loss computation works (finite value)")

    # --- Test 7: Backward through projector ---
    _sec("Test 7: Backward pass -- gradient flows to projector")
    projector.train()
    for p in llm.parameters():
        p.requires_grad = False
    for p in vision.parameters():
        p.requires_grad = False
    for p in projector.parameters():
        p.requires_grad = True

    patch_feats = vision(dummy_images)
    image_embeds = projector(patch_feats)
    inputs_embeds = embed_layer(input_ids).detach()
    image_mask = (input_ids == IMAGE_TOKEN_ID).unsqueeze(-1).expand_as(inputs_embeds)
    image_embeds_flat = image_embeds.reshape(-1, image_embeds.shape[-1])
    inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds_flat.to(inputs_embeds.dtype))
    outputs = llm(inputs_embeds=inputs_embeds, attention_mask=attn_mask)
    logits = outputs.logits
    shift_logits = logits[..., :-1, :].contiguous()
    labels_g = input_ids.clone()
    labels_g[labels_g == IMAGE_TOKEN_ID] = -100
    shift_labels = labels_g[..., 1:].contiguous()
    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
    loss.backward()
    grad_ok = all(p.grad is not None and p.grad.abs().sum() > 0 for p in projector.parameters())
    print(f"  Loss (grad): {loss.item():.4f}")
    print(f"  fc1 grad norm: {projector.fc1.weight.grad.norm().item():.6f}")
    print(f"  fc2 grad norm: {projector.fc2.weight.grad.norm().item():.6f}")
    if not grad_ok:
        _fail("Projector gradients are zero/None -- gradient flow broken!")
    _ok("Gradient flows to projector parameters")

    # --- Summary ---
    _sec("SMOKE TEST SUMMARY")
    print(f"  Vision tower:  {nv/1e6:.2f}M params (4ep w512/d30)")
    print(f"  Projector:     {np_/1e6:.2f}M params (2-layer MLP 512->2560)")
    print(f"  LLM:           {nl/1e9:.2f}B params (Qwen3-4B-Instruct-2507)")
    print(f"  Total:         {(nv+np_+nl)/1e9:.2f}B params")
    print(f"  GPU peak mem:  {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
    print("\n  All 7 tests PASSED")
    print("  -> GPU smoke test successful -- ready for Stage-1 alignment training.")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  BaiZe MLLM Bridge -- GPU Smoke Test")
    print(f"  Checkpoint: {CKPT}")
    print(f"  LLM:        {LLM_PATH}")
    print("=" * 70)
    try:
        main()
    except Exception as e:
        print(f"\nSMOKE TEST FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)

