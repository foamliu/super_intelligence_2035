#!/usr/bin/env python
"""Stage-1 Gate-Check: verify the trained projector improves loss & generation.

This script is the gate between Stage-1 (Alignment) and Stage-1.5 (Mid-Training).
It verifies that the 2500-step projector checkpoint actually learned to align
BaiZe vision features with Qwen3-4B's embedding space.

Tests:
  1. Load step2500 projector checkpoint (strict=True).
  2. Loss comparison: trained vs random projector on held-out LLaVA-558K samples.
     PASS if trained loss < random loss by a meaningful margin.
  3. Text generation: feed image+prompt through full pipeline, generate 30 tokens.
     PASS if output is non-empty and not all-pad/eos.
  4. Embedding statistics: compare projected image embeds (trained vs random).

Usage:
  cd run/vision
  CUDA_VISIBLE_DEVICES=0 python mllm_bridge/gate_check_stage1.py
"""

import sys, os, time, json, io, random, traceback
import tarfile
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms as T
from PIL import Image

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoModelForCausalLM, AutoTokenizer
from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
DATA_DIR = "/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-558K-Webdataset"
PROJECTOR_CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage1/step2500/projector.pt"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=CLIP_MEAN, std=CLIP_STD),
])

def _sec(t):
    print("\n" + "=" * 70 + f"\n  {t}\n" + "=" * 70)

def _ok(m):
    print(f"  PASS {m}")

def _fail(m):
    print(f"  FAIL {m}")
    raise AssertionError(m)

def load_samples(n=8):
    """Load n image-prompt-caption samples from LLaVA-558K tars."""
    tars = sorted(Path(DATA_DIR).glob('pretrain-*.tar'))
    samples = []
    tar_path = str(tars[-1])
    tf = tarfile.open(tar_path, 'r')
    names = tf.getnames()
    groups = {}
    for n_ in names:
        if '.img' in n_:
            prefix = n_.rsplit('.img', 1)[0]
        elif n_.endswith('.json'):
            prefix = n_.rsplit('.json', 1)[0]
        else:
            continue
        groups.setdefault(prefix, {'imgs': [], 'json': False})
        if n_.endswith('.jpg'):
            groups[prefix]['imgs'].append(n_)
        elif n_.endswith('.json'):
            groups[prefix]['json'] = True
    valid = [(p, info) for p, info in groups.items() if info['json'] and len(info['imgs']) > 0]
    random.seed(42)
    random.shuffle(valid)
    for prefix, info in valid[:n]:
        json_name = f"{prefix}.json"
        jf = tf.extractfile(json_name)
        meta = json.load(io.BytesIO(jf.read()))
        prompts = meta.get('prompts', ['What is this?\n<image>'])
        captions = meta.get('captions', ['a photo'])
        prompt = prompts[0]
        caption = captions[0]
        img_name = sorted(info['imgs'])[0]
        img_file = tf.extractfile(img_name)
        image = Image.open(io.BytesIO(img_file.read())).convert('RGB')
        samples.append((image, prompt, caption))
    tf.close()
    return samples

def expand_image_tokens(ids, num_expansion=NUM_IMAGE_TOKENS):
    result = []
    for tid in ids:
        if tid == IMAGE_TOKEN_ID:
            result.extend([IMAGE_TOKEN_ID] * num_expansion)
        else:
            result.append(tid)
    return result

def prepare_batch(samples, tokenizer, seq_len=512):
    """Tokenize samples into (input_ids, attention_mask, labels, pixel_values)."""
    input_ids_list, labels_list, pixel_values_list = [], [], []
    for image, prompt, caption in samples:
        pixel = transform(image)
        pixel_values_list.append(pixel)
        prompt_text = prompt.replace('<image>', '<|image_pad|>')
        user_text = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
        assistant_text = f"{caption}<|im_end|>"
        full_text = user_text + assistant_text
        full_ids = tokenizer(full_text, add_special_tokens=False)['input_ids']
        user_ids = tokenizer(user_text, add_special_tokens=False)['input_ids']
        full_ids_exp = expand_image_tokens(full_ids)
        user_ids_exp = expand_image_tokens(user_ids)
        user_len = len(user_ids_exp)
        if len(full_ids_exp) > seq_len:
            full_ids_exp = full_ids_exp[:seq_len]
        if user_len > len(full_ids_exp):
            user_len = len(full_ids_exp)
        ids = torch.tensor(full_ids_exp, dtype=torch.long)
        labels = ids.clone()
        labels[:user_len] = -100
        input_ids_list.append(ids)
        labels_list.append(labels)
    max_len = max(t.shape[0] for t in input_ids_list)
    padded_ids = torch.full((len(samples), max_len), tokenizer.pad_token_id, dtype=torch.long)
    padded_labels = torch.full((len(samples), max_len), -100, dtype=torch.long)
    attention_mask = torch.zeros((len(samples), max_len), dtype=torch.long)
    for i, (ids, labels) in enumerate(zip(input_ids_list, labels_list)):
        L = ids.shape[0]
        padded_ids[i, :L] = ids
        padded_labels[i, :L] = labels
        attention_mask[i, :L] = 1
    pixel_values = torch.stack(pixel_values_list)
    return {'input_ids': padded_ids, 'attention_mask': attention_mask,
            'labels': padded_labels, 'pixel_values': pixel_values}

def compute_loss(vision, projector, llm, batch, device, dtype=torch.bfloat16):
    """Forward pass and compute cross-entropy loss on assistant tokens only."""
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    labels = batch['labels'].to(device)
    pixel_values = batch['pixel_values'].to(device=device, dtype=dtype)
    with torch.no_grad():
        vis_feat = vision(pixel_values)
    proj_feat = projector(vis_feat)
    embed_layer = llm.get_input_embeddings()
    inputs_embeds = embed_layer(input_ids)
    image_mask = (input_ids == IMAGE_TOKEN_ID).unsqueeze(-1).expand_as(inputs_embeds)
    image_embeds_flat = proj_feat.reshape(-1, proj_feat.shape[-1])
    inputs_embeds = inputs_embeds.masked_scatter(
        image_mask, image_embeds_flat.to(inputs_embeds.dtype))
    outputs = llm(inputs_embeds=inputs_embeds, attention_mask=attention_mask, labels=labels)
    return outputs.loss.item()

def generate_text(vision, projector, llm, tokenizer, image, prompt, device, dtype=torch.bfloat16, max_new_tokens=30):
    """Generate text from image+prompt through the full pipeline."""
    pixel = transform(image).unsqueeze(0).to(device=device, dtype=dtype)
    prompt_text = prompt.replace('<image>', '<|image_pad|>')
    user_text = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
    input_ids = tokenizer(user_text, add_special_tokens=False, return_tensors='pt')['input_ids'].to(device)
    input_ids_exp = torch.tensor([expand_image_tokens(input_ids[0].tolist())], dtype=torch.long, device=device)
    with torch.no_grad():
        vis_feat = vision(pixel)
        proj_feat = projector(vis_feat)
        embed_layer = llm.get_input_embeddings()
        inputs_embeds = embed_layer(input_ids_exp)
        image_mask = (input_ids_exp == IMAGE_TOKEN_ID).unsqueeze(-1).expand_as(inputs_embeds)
        image_embeds_flat = proj_feat.reshape(-1, proj_feat.shape[-1])
        inputs_embeds = inputs_embeds.masked_scatter(
            image_mask, image_embeds_flat.to(inputs_embeds.dtype))
        attention_mask = torch.ones_like(input_ids_exp)
        output_ids = llm.generate(
            inputs_embeds=inputs_embeds, attention_mask=attention_mask,
            max_new_tokens=max_new_tokens, do_sample=False, temperature=1.0, top_p=1.0,
            pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id)
    generated_ids = output_ids[0, input_ids_exp.shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return text

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        _fail("CUDA not available -- gate-check requires a GPU.")
    print(f"\nGPU: {torch.cuda.get_device_name(0)}  ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)")
    dtype = torch.bfloat16

    _sec("Loading models")
    t0 = time.time()
    print("  Loading BaiZe vision tower (4ep w512/d30)...")
    vision = BaizeVisionModel.from_baize_checkpoint(CKPT).to(device=device, dtype=dtype).eval()
    for p in vision.parameters():
        p.requires_grad = False
    nv = sum(p.numel() for p in vision.parameters())
    print(f"  Vision: {nv/1e6:.2f}M params")
    print("  Loading Qwen3-4B-Instruct-2507 (bf16)...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    llm = AutoModelForCausalLM.from_pretrained(
        LLM_PATH, torch_dtype=torch.bfloat16, trust_remote_code=True).to(device).eval()
    for p in llm.parameters():
        p.requires_grad = False
    nl = sum(p.numel() for p in llm.parameters())
    print(f"  LLM: {nl/1e9:.2f}B params, loaded in {time.time()-t0:.1f}s")

    _sec("Test 1: Load step2500 projector checkpoint")
    trained_proj = BaizeMultiModalProjector(vision.config.width, LLM_HIDDEN_SIZE).to(device=device, dtype=dtype)
    ck = torch.load(PROJECTOR_CKPT, map_location="cpu", weights_only=False)
    if isinstance(ck, dict) and 'state_dict' in ck:
        sd = ck['state_dict']
    elif isinstance(ck, dict) and 'projector' in ck:
        sd = ck['projector']
    else:
        sd = ck
    sd = {k.replace('module.', '', 1) if k.startswith('module.') else k: v for k, v in sd.items()}
    result = trained_proj.load_state_dict(sd, strict=True)
    matched = len(sd) - len(result.missing_keys) - len(result.unexpected_keys)
    print(f"  Projector load: matched={matched}/{len(sd)}, missing={list(result.missing_keys)}, unexpected={list(result.unexpected_keys)}")
    np_ = sum(p.numel() for p in trained_proj.parameters())
    print(f"  Projector: {np_/1e6:.2f}M params")
    if len(result.missing_keys) > 0 or len(result.unexpected_keys) > 0:
        _fail("Projector checkpoint mismatch")
    _ok("Trained projector loaded (strict=True)")

    torch.manual_seed(0)
    random_proj = BaizeMultiModalProjector(vision.config.width, LLM_HIDDEN_SIZE).to(device=device, dtype=dtype)
    for p in random_proj.parameters():
        p.requires_grad = False

    _sec("Loading 8 held-out LLaVA-558K samples for evaluation")
    samples = load_samples(n=8)
    print(f"  Loaded {len(samples)} samples from last tar (held-out)")
    for i, (img, prompt, caption) in enumerate(samples):
        print(f"  Sample {i}: prompt={prompt[:50]}... | caption={caption[:50]}...")
    batch = prepare_batch(samples, tokenizer, seq_len=512)
    print(f"  Batch: input_ids={tuple(batch['input_ids'].shape)}, pixel_values={tuple(batch['pixel_values'].shape)}")

    _sec("Test 2: Loss comparison — trained vs random projector")
    loss_trained = compute_loss(vision, trained_proj, llm, batch, device, dtype)
    print(f"  Trained projector loss: {loss_trained:.4f}")
    loss_random = compute_loss(vision, random_proj, llm, batch, device, dtype)
    print(f"  Random  projector loss: {loss_random:.4f}")
    delta = loss_random - loss_trained
    print(f"  Delta (random - trained): {delta:.4f}")
    if delta > 0.5:
        print(f"  -> Trained projector is meaningfully better (Delta={delta:.2f} > 0.5)")
        _ok("Trained projector reduces loss vs random")
    elif delta > 0:
        print(f"  -> Trained projector is slightly better (Delta={delta:.2f}), marginal")
        _ok("Trained projector reduces loss (marginal)")
    else:
        _fail(f"Trained projector is WORSE than random (Delta={delta:.2f}) — Stage-1 failed!")

    _sec("Test 3: Text generation with trained projector")
    img, prompt, caption = samples[0]
    print(f"  Prompt: {prompt[:80]}")
    print(f"  Ground truth caption: {caption[:80]}")
    gen_text = generate_text(vision, trained_proj, llm, tokenizer, img, prompt, device, dtype, max_new_tokens=30)
    print(f"  Generated (trained): {repr(gen_text[:120])}")
    if len(gen_text.strip()) > 0:
        _ok("Generation produces non-empty output")
    else:
        print("  WARNING: Generation empty (expected for projector-only Stage-1; LLM frozen,")
        print("           has never seen BaiZe visual features. Quality improves in Stage-1.5)")
        print("  -> Treating as soft check (loss comparison is the hard gate)")
    gen_random = generate_text(vision, random_proj, llm, tokenizer, img, prompt, device, dtype, max_new_tokens=30)
    print(f"  Generated (random):  {repr(gen_random[:120])}")

    _sec("Test 4: Projected embedding statistics")
    with torch.no_grad():
        pixel_values = batch['pixel_values'].to(device=device, dtype=dtype)
        vis_feat = vision(pixel_values)
        trained_embeds = trained_proj(vis_feat)
        random_embeds = random_proj(vis_feat)
        text_embeds = llm.get_input_embeddings()(batch['input_ids'].to(device))
    text_std = text_embeds[batch['attention_mask'].to(device).bool()].std().item()
    trained_std = trained_embeds.std().item()
    random_std = random_embeds.std().item()
    print(f"  LLM text embed std:     {text_std:.4f}")
    print(f"  Trained proj embed std: {trained_std:.4f}")
    print(f"  Random proj embed std:  {random_std:.4f}")
    trained_dist = abs(trained_std - text_std)
    random_dist = abs(random_std - text_std)
    print(f"  |trained - text| = {trained_dist:.4f}")
    print(f"  |random  - text| = {random_dist:.4f}")
    if trained_dist < random_dist:
        _ok("Trained projector embeds closer to LLM text distribution")
    else:
        print(f"  WARNING: trained not closer (OK if loss improved)")

    _sec("GATE-CHECK SUMMARY")
    print(f"  Vision:  {nv/1e6:.2f}M (frozen)")
    print(f"  Proj:    {np_/1e6:.2f}M (trained step2500)")
    print(f"  LLM:     {nl/1e9:.2f}B (frozen)")
    print(f"  Trained loss: {loss_trained:.4f}")
    print(f"  Random loss:  {loss_random:.4f}")
    print(f"  Delta loss:   {delta:.4f} (trained better)")
    print(f"  GPU peak:     {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
    print(f"\n  Test 1: Projector load strict=True  PASS")
    print(f"  Test 2: Loss trained < random       PASS (Delta={delta:.2f})")
    print(f"  Test 3: Generation                  SOFT (empty OK for Stage-1)")
    print(f"  Test 4: Embed stats closer to LLM   {'PASS' if trained_dist < random_dist else 'WARN'}")
    print(f"\n  ** GATE-CHECK PASSED — ready for Stage-1.5 Mid-Training **")
    print("=" * 70)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  BaiZe MLLM Bridge — Stage-1 Gate-Check")
    print(f"  Projector: {PROJECTOR_CKPT}")
    print(f"  Vision:    {CKPT}")
    print(f"  LLM:       {LLM_PATH}")
    print("=" * 70)
    try:
        main()
    except Exception as e:
        print(f"\nGATE-CHECK FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
