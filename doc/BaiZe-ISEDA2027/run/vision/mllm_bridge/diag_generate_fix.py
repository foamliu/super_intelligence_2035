#!/usr/bin/env python
"""Diagnostic: verify merge_and_unload() fix for degenerate "A" output.

Tests three configs on a single image+question:
  A) PeftModel + generate(inputs_embeds=...)     [original broken path]
  B) Merged model + generate(inputs_embeds=...)  [fixed path]
  C) Merged model + generate(input_ids=...) [no image] [text-only baseline]

If B produces meaningful output (not just "A"), the fix works.
"""
import os, sys, io, tarfile, json, random
import torch
from pathlib import Path
from torchvision import transforms as T
from PIL import Image

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
STAGE2_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2/step3500"
DATA_DIR = "/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-NeXT-780k-plus-Instruct-opt47-webdataset"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

transform = T.Compose([
    T.Resize(int(224 * 1.15)), T.CenterCrop(224), T.ToTensor(),
    T.Normalize(CLIP_MEAN, CLIP_STD),
])


def load_image_and_question():
    tars = sorted(Path(DATA_DIR).glob("data-*.tar"))
    tars = [t for t in tars if t.exists()]  # filter broken symlinks
    if not tars:
        raise FileNotFoundError(f"No valid tar files in {DATA_DIR}")
    tf = tarfile.open(str(tars[0]), "r")  # use first valid tar
    names = tf.getnames()
    groups = {}
    for n in names:
        if n.endswith(".json"):
            prefix = n.rsplit(".json", 1)[0]
            groups.setdefault(prefix, {"json": False, "imgs": []})["json"] = True
        elif n.endswith((".jpg", ".png", ".jpeg")):
            parts = n.rsplit(".", 2)
            prefix = parts[0] if len(parts) >= 3 else n.rsplit(".", 1)[0]
            groups.setdefault(prefix, {"json": False, "imgs": []})["imgs"].append(n)
    samples = [(p, i) for p, i in groups.items() if i["json"] and i["imgs"]]
    random.seed(42)
    random.shuffle(samples)
    for prefix, info in samples[:10]:
        try:
            jf = tf.extractfile(f"{prefix}.json")
            meta = json.load(io.BytesIO(jf.read()))
            texts = meta.get("texts", [])
            user_text, gt = "", ""
            for msg in texts:
                if msg["role"] == "user": user_text = msg["content"]
                elif msg["role"] == "assistant": gt = msg["content"]
            if not user_text or not gt: continue
            if "<image>" not in user_text: user_text = "<image>\n" + user_text
            img_file = tf.extractfile(info["imgs"][0])
            image = Image.open(io.BytesIO(img_file.read())).convert("RGB")
            return image, user_text, gt
        except Exception:
            continue
    raise RuntimeError("No valid sample found")


def inject_image_features(llm, input_ids, image_features):
    embed_tokens = llm.get_input_embeddings()
    inputs_embeds = embed_tokens(input_ids)
    img_mask = (input_ids[0] == IMAGE_TOKEN_ID)
    n_img = img_mask.sum().item()
    if n_img == NUM_IMAGE_TOKENS:
        inputs_embeds[0, img_mask] = image_features[0]
    elif n_img > 0:
        inputs_embeds[0, img_mask][:NUM_IMAGE_TOKENS] = image_features[0, :min(n_img, NUM_IMAGE_TOKENS)]
    return inputs_embeds


def expand_image_tokens(ids):
    result = []
    for tid in ids:
        if tid == IMAGE_TOKEN_ID: result.extend([IMAGE_TOKEN_ID] * NUM_IMAGE_TOKENS)
        else: result.append(tid)
    return result


def build_prompt(user_text):
    prompt_text = user_text.replace("<image>", "<|image_pad|>")
    return f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"


def run_test(label, llm, tokenizer, input_ids, inputs_embeds, device):
    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    if im_end_id is None or im_end_id == tokenizer.unk_token_id:
        im_end_id = 151645
    with torch.no_grad():
        if inputs_embeds is not None:
            attn = torch.ones((1, inputs_embeds.shape[1]), dtype=torch.long, device=device)
            output = llm.generate(
                inputs_embeds=inputs_embeds, attention_mask=attn,
                max_new_tokens=128, do_sample=False, temperature=1.0, top_p=1.0,
                num_beams=1, pad_token_id=tokenizer.pad_token_id,
                eos_token_id=im_end_id)
            dbg = llm(inputs_embeds=inputs_embeds, attention_mask=attn)
            dbg_logits = dbg.logits[0, -1]
            top5 = dbg_logits.topk(5)
            top5_str = [(tokenizer.decode([idx.item()]), f"{val.item():.2f}")
                        for val, idx in zip(top5.values, top5.indices)]
        else:
            attn = torch.ones_like(input_ids)
            output = llm.generate(
                input_ids=input_ids, attention_mask=attn,
                max_new_tokens=128, do_sample=False, temperature=1.0, top_p=1.0,
                num_beams=1, pad_token_id=tokenizer.pad_token_id,
                eos_token_id=im_end_id)
            top5_str = "(no image, no debug)"
    if inputs_embeds is not None:
        input_len = inputs_embeds.shape[1]
        if output.shape[1] > input_len:
            new_tokens = output[0][input_len:]
        else:
            new_tokens = output[0]
    else:
        new_tokens = output[0][input_ids.shape[1]:]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    print(f"\n{'='*60}")
    print(f"  Test {label}")
    print(f"  Output shape: {output.shape}")
    print(f"  New tokens:   {new_tokens[:10].tolist()}")
    print(f"  Top-5 logits: {top5_str}")
    print(f"  Generated:    '{text[:200]}'")
    print(f"{'='*60}")
    return text


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16
    print(f"Device: {device}, dtype: {dtype}")
    print("\nLoading vision tower...")
    vision = BaizeVisionModel.from_baize_checkpoint(CKPT).to(device=device, dtype=dtype).eval()
    for p in vision.parameters(): p.requires_grad = False
    print("Loading projector...")
    projector = BaizeMultiModalProjector(vision.config.width, LLM_HIDDEN_SIZE).to(device=device, dtype=dtype)
    ck = torch.load(os.path.join(STAGE2_DIR, "projector.pt"), map_location="cpu", weights_only=False)
    sd = ck.get("projector", ck) if isinstance(ck, dict) else ck
    sd = {k.replace("module.", "", 1) if k.startswith("module.") else k: v for k, v in sd.items()}
    projector.load_state_dict(sd, strict=True)
    projector.eval()
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    print("Loading image+question...")
    image, user_text, gt_answer = load_image_and_question()
    print(f"  Question: {user_text[:150]}")
    print(f"  GT answer: {gt_answer[:150]}")
    pixel = transform(image).unsqueeze(0).to(device=device, dtype=dtype)
    with torch.no_grad():
        vis_feat = vision(pixel)
        image_features = projector(vis_feat)
    print(f"  Image features: {image_features.shape}, min={image_features.min():.3f}, max={image_features.max():.3f}")
    prompt = build_prompt(user_text)
    input_ids = tokenizer(prompt, add_special_tokens=False, return_tensors="pt")["input_ids"].to(device)
    expanded = expand_image_tokens(input_ids[0].tolist())
    input_ids = torch.tensor([expanded], dtype=torch.long, device=device)
    n_img = (input_ids[0] == IMAGE_TOKEN_ID).sum().item()
    print(f"  Input shape: {input_ids.shape}, img_tokens: {n_img}")

    # Test A: PeftModel (original, potentially broken)
    print("\n" + "#"*60)
    print("# Test A: PeftModel + generate(inputs_embeds)")
    print("#"*60)
    llm_a = AutoModelForCausalLM.from_pretrained(LLM_PATH, torch_dtype=dtype, device_map={"": device}, trust_remote_code=True)
    llm_a = PeftModel.from_pretrained(llm_a, STAGE2_DIR, is_trainable=False)
    llm_a.eval()
    inputs_embeds_a = inject_image_features(llm_a, input_ids, image_features)
    text_a = run_test("A (PeftModel)", llm_a, tokenizer, input_ids, inputs_embeds_a, device)
    del llm_a
    torch.cuda.empty_cache()

    # Test B: Merged model + generate(inputs_embeds) [THE FIX]
    print("\n" + "#"*60)
    print("# Test B: Merged model + generate(inputs_embeds) [FIX]")
    print("#"*60)
    llm_b = AutoModelForCausalLM.from_pretrained(LLM_PATH, torch_dtype=dtype, device_map={"": device}, trust_remote_code=True)
    llm_b = PeftModel.from_pretrained(llm_b, STAGE2_DIR, is_trainable=False)
    llm_b = llm_b.merge_and_unload()
    llm_b.eval()
    print(f"  Model type after merge: {type(llm_b).__name__}")
    inputs_embeds_b = inject_image_features(llm_b, input_ids, image_features)
    text_b = run_test("B (Merged)", llm_b, tokenizer, input_ids, inputs_embeds_b, device)

    # Test C: Merged model + generate(input_ids) [text-only baseline]
    print("\n" + "#"*60)
    print("# Test C: Merged model + generate(input_ids) [no image]")
    print("#"*60)
    text_prompt = build_prompt(user_text.replace("<image>", ""))
    text_ids = tokenizer(text_prompt, add_special_tokens=False, return_tensors="pt")["input_ids"].to(device)
    text_c = run_test("C (text-only)", llm_b, tokenizer, text_ids, None, device)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  GT answer:     '{gt_answer[:100]}'")
    print(f"  A (PeftModel): '{text_a[:100]}'")
    print(f"  B (Merged):    '{text_b[:100]}'")
    print(f"  C (text-only): '{text_c[:100]}'")
    print()
    if text_b.strip() != "A" and len(text_b.strip()) > 1:
        print("  RESULT: FIX WORKS - Merged model generates meaningful output with images!")
    elif text_b.strip() == text_a.strip():
        print("  RESULT: SAME OUTPUT - merge_and_unload() did not change the result.")
        print("         The issue may be elsewhere (projector, vision tower, or prompt format).")
    else:
        print("  RESULT: Still degenerate output. Need further investigation.")
    print("="*60)


if __name__ == "__main__":
    main()
