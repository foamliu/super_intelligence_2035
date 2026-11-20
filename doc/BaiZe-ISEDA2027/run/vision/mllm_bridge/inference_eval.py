#!/usr/bin/env python
"""BaiZe-LLaVA Inference & Evaluation Script.

Loads trained BaiZe vision tower + projector + Qwen3-4B (LoRA) and runs
inference on VQA-style image+question pairs.

Usage:
  cd run/vision
  CUDA_VISIBLE_DEVICES=0 python mllm_bridge/inference_eval.py
"""

import sys, os, time, json, io, random, argparse
import tarfile
from pathlib import Path

import torch
import torch.nn as nn
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
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

transform = T.Compose([
    T.Resize(int(224 * 1.15)), T.CenterCrop(224), T.ToTensor(),
    T.Normalize(CLIP_MEAN, CLIP_STD),
])


def load_model(stage2_dir, device='cuda'):
    """Load vision tower + projector + LLM (with LoRA) from checkpoint."""
    dtype = torch.bfloat16
    print("Loading vision tower...")
    vision = BaizeVisionModel.from_baize_checkpoint(CKPT)
    vision = vision.to(device=device, dtype=dtype)
    vision.eval()
    for p in vision.parameters():
        p.requires_grad = False

    print("Loading projector...")
    projector = BaizeMultiModalProjector(vision.config.width, LLM_HIDDEN_SIZE)
    projector = projector.to(device=device, dtype=dtype)
    ck = torch.load(os.path.join(stage2_dir, 'projector.pt'), map_location="cpu", weights_only=False)
    sd = ck.get('projector', ck) if isinstance(ck, dict) else ck
    sd = {k.replace('module.', '', 1) if k.startswith('module.') else k: v for k, v in sd.items()}
    projector.load_state_dict(sd, strict=True)
    projector.eval()
    for p in projector.parameters():
        p.requires_grad = False

    print("Loading LLM + LoRA adapter...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    llm = AutoModelForCausalLM.from_pretrained(
        LLM_PATH, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    llm = PeftModel.from_pretrained(llm, stage2_dir, is_trainable=False)
    llm.eval()
    for p in llm.parameters():
        p.requires_grad = False

    print("Model loaded successfully!")
    return vision, projector, llm, tokenizer


def generate_response(vision, projector, llm, tokenizer, image, question, device='cuda',
                      max_new_tokens=128):
    """Generate a response for a single image+question pair."""
    dtype = torch.bfloat16
    pixel = transform(image).unsqueeze(0).to(device=device, dtype=dtype)

    with torch.no_grad():
        vis_feat = vision(pixel)
        proj_feat = projector(vis_feat)

    prompt_text = question.replace('<image>', '<|image_pad|>')
    user_text = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
    input_ids = tokenizer(user_text, add_special_tokens=False, return_tensors='pt')['input_ids'].to(device)

    expanded = []
    for tid in input_ids[0].tolist():
        if tid == IMAGE_TOKEN_ID:
            expanded.extend([IMAGE_TOKEN_ID] * NUM_IMAGE_TOKENS)
        else:
            expanded.append(tid)
    input_ids = torch.tensor([expanded], dtype=torch.long, device=device)

    embed_tokens = llm.get_input_embeddings()
    inputs_embeds = embed_tokens(input_ids)
    img_mask = (input_ids[0] == IMAGE_TOKEN_ID)
    n_img = img_mask.sum().item()
    if n_img == NUM_IMAGE_TOKENS:
        inputs_embeds[0, img_mask] = proj_feat[0]
    elif n_img > 0:
        inputs_embeds[0, img_mask][:NUM_IMAGE_TOKENS] = proj_feat[0, :min(n_img, NUM_IMAGE_TOKENS)]

    with torch.no_grad():
        outputs = llm.generate(
            inputs_embeds=inputs_embeds,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "<|im_start|>assistant\n" in response:
        response = response.split("<|im_start|>assistant\n")[-1]
    if "<|im_end|>" in response:
        response = response.split("<|im_end|>")[0]
    return response.strip()


def eval_on_instruct_data(vision, projector, llm, tokenizer, data_dir, n_samples=50, device='cuda'):
    """Evaluate on held-out LLaVA-NeXT instruct samples."""
    tars = sorted(Path(data_dir).glob('data-*.tar'))
    tar_path = str(tars[-1])
    tf = tarfile.open(tar_path, 'r')
    names = tf.getnames()

    groups = {}
    for n in names:
        if n.endswith('.json'):
            prefix = n.rsplit('.json', 1)[0]
            groups.setdefault(prefix, {'json': True, 'imgs': []})
        elif n.endswith(('.jpg', '.png', '.jpeg')):
            parts = n.rsplit('.', 2)
            prefix = parts[0] if len(parts) >= 3 else n.rsplit('.', 1)[0]
            groups.setdefault(prefix, {'json': False, 'imgs': []})
            groups[prefix]['imgs'].append(n)

    samples = [(prefix, info) for prefix, info in groups.items() if info['json'] and info['imgs']]
    random.shuffle(samples)
    samples = samples[:n_samples]

    results = []
    correct = 0
    total = 0

    for prefix, info in samples:
        try:
            jf = tf.extractfile(f"{prefix}.json")
            meta = json.load(io.BytesIO(jf.read()))
            texts = meta.get('texts', [])
            user_text, gt_answer = "", ""
            for msg in texts:
                if msg['role'] == 'user':
                    user_text = msg['content']
                elif msg['role'] == 'assistant':
                    gt_answer = msg['content']
            if not user_text or not gt_answer:
                continue
            if '<image>' not in user_text:
                user_text = '<image>\n' + user_text

            img_file = tf.extractfile(info['imgs'][0])
            image = Image.open(io.BytesIO(img_file.read())).convert('RGB')
            pred = generate_response(vision, projector, llm, tokenizer, image, user_text, device)

            pred_lower = pred.lower().strip()
            gt_lower = gt_answer.lower().strip()
            is_correct = (gt_lower in pred_lower) or (pred_lower in gt_lower)
            if len(gt_lower) <= 3:
                is_correct = gt_lower == pred_lower[:len(gt_lower)]

            results.append({'question': user_text[:200], 'gt': gt_answer[:200],
                            'pred': pred[:200], 'correct': is_correct})
            correct += int(is_correct)
            total += 1

            if total % 10 == 0:
                print(f"  [{total}/{n_samples}] acc={correct/total:.1%} | GT: {gt_answer[:50]} | Pred: {pred[:50]}")
        except Exception as e:
            print(f"  SKIP {prefix}: {e}")
            continue

    acc = correct / max(1, total)
    print(f"\n=== Evaluation Results ===")
    print(f"  Samples: {total}/{n_samples}")
    print(f"  Accuracy: {acc:.1%} ({correct}/{total})")
    return acc, results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage2_dir', type=str,
                        default="/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2/step3500")
    parser.add_argument('--data_dir', type=str,
                        default="/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-NeXT-780k-plus-Instruct-opt47-webdataset")
    parser.add_argument('--n_samples', type=int, default=50)
    parser.add_argument('--output_json', type=str, default="/tmp/baize_mllm_eval_results.json")
    args = parser.parse_args()

    device = 'cuda'
    vision, projector, llm, tokenizer = load_model(args.stage2_dir, device)

    print(f"\nEvaluating on {args.n_samples} held-out instruct samples...")
    acc, results = eval_on_instruct_data(vision, projector, llm, tokenizer,
                                          args.data_dir, args.n_samples, device)

    with open(args.output_json, 'w') as f:
        json.dump({'accuracy': acc, 'n_samples': len(results), 'results': results}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {args.output_json}")


if __name__ == "__main__":
    main()
