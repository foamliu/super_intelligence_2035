#!/usr/bin/env python
"""Stage-1.5 Mid-Training (ArmD): unfreeze LLM via LoRA, continue training projector.

ArmD variant of stage15_train.py — only the vision tower + projector width differ:
  - Vision tower: ArmD open_clip ViT-B/16 (86.2M, 768-dim patch tokens, FROZEN)
  - Projector: 2-layer MLP 768->2560 (trainable, loaded from Stage-1 step2500)
  - LLM: Qwen3-4B-Instruct-2507 + LoRA r=64 (trainable)

After Stage-1 aligned the projector, Stage-1.5 adapts the LLM to the ArmD visual
features using LoRA. The vision tower stays frozen; the projector continues
training (loaded from Stage-1 step2500 checkpoint).

Hyperparameters (operator instruction 2026-10-18 P0 ④, = stage15_train.py defaults):
  - LoRA: rank=64, alpha=128, dropout=0.05, targets=all linear
  - LR: 2e-5 (LoRA), 1e-5 (projector), cosine decay, warmup 0.002
  - Steps: 20000, GBS=8, MBS=1
  - Image: 224x224, CLIP normalization, 196 tokens, no spatial merge
  - Data: LLaVA-558K WebDataset (same as Stage-1 / ④-4ep)

Usage (8 GPUs):
  cd run/vision
  torchrun --nproc_per_node=8 mllm_bridge/stage15_train_armB.py

Usage (1 GPU):
  CUDA_VISIBLE_DEVICES=0 python mllm_bridge/stage15_train.py
"""

import sys, os, time, json, io, math, random, traceback
import tarfile
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import transforms as T
from PIL import Image

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

# ArmD open_clip ViT-B/16 checkpoint (clip-only, predictor stripped)
CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/armD_r2_20261020_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
DATA_DIR = "/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-558K-Webdataset"
PROJECTOR_CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage1_armD_r2_20261020/step2500/projector.pt"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armD_r2_20261020"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
VISION_HIDDEN_SIZE = 768  # ArmD open_clip ViT-B/16 patch-token dim (vs ④'s 512)
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--lr_lora', type=float, default=2e-5)
    p.add_argument('--lr_proj', type=float, default=1e-5)
    p.add_argument('--min_lr', type=float, default=1e-6)
    p.add_argument('--nsteps', type=int, default=20000)
    p.add_argument('--gbs', type=int, default=8)
    p.add_argument('--mbs', type=int, default=1)
    p.add_argument('--warmup_frac', type=float, default=0.002)
    p.add_argument('--seq_len', type=int, default=2048)
    p.add_argument('--num_workers', type=int, default=4)
    p.add_argument('--save_steps', type=int, default=2000)
    p.add_argument('--log_steps', type=int, default=50)
    p.add_argument('--lora_r', type=int, default=64)
    p.add_argument('--lora_alpha', type=int, default=128)
    p.add_argument('--lora_dropout', type=float, default=0.05)
    p.add_argument('--max_images_per_sample', type=int, default=1)
    return p.parse_args()

def setup_ddp():
    if 'RANK' in os.environ:
        rank = int(os.environ['RANK'])
        world = int(os.environ['WORLD_SIZE'])
        local = int(os.environ.get('LOCAL_RANK', 0))
        dist.init_process_group(backend='nccl')
        torch.cuda.set_device(local)
    else:
        rank, world, local = 0, 1, 0
        torch.cuda.set_device(0)
    return rank, world, local

def is_main():
    return dist.get_rank() == 0 if dist.is_initialized() else True

def cleanup():
    if dist.is_initialized():
        dist.destroy_process_group()

def print0(*args, **kw):
    if is_main():
        print(*args, **kw, flush=True)

# ---- data (same as stage1_train.py) ----
class LLaVA558KDataset(Dataset):
    def __init__(self, data_dir, rank=0, world=1, max_images_per_sample=1):
        self.data_dir = data_dir
        self.max_images = max_images_per_sample
        self._tar_cache = {}
        self.index = []
        tars = sorted(Path(data_dir).glob('pretrain-*.tar'))
        for tar_path in tars:
            try:
                with tarfile.open(str(tar_path), 'r') as tf:
                    names = tf.getnames()
                groups = {}
                for n in names:
                    if '.img' in n:
                        prefix = n.rsplit('.img', 1)[0]
                    elif n.endswith('.json'):
                        prefix = n.rsplit('.json', 1)[0]
                    else:
                        continue
                    groups.setdefault(prefix, {'imgs': [], 'json': False})
                    if n.endswith('.jpg'):
                        groups[prefix]['imgs'].append(n)
                    elif n.endswith('.json'):
                        groups[prefix]['json'] = True
                for prefix, info in groups.items():
                    if info['json'] and len(info['imgs']) > 0:
                        self.index.append((str(tar_path), prefix, sorted(info['imgs'])))
            except Exception as e:
                print0(f"WARNING: failed to index {tar_path}: {e}")
        print0(f"[Rank {rank}] Dataset: {len(self.index)} samples from {len(tars)} tars")

    def _get_tar(self, tar_path):
        if tar_path not in self._tar_cache:
            tf = tarfile.open(tar_path, 'r')
            self._tar_cache[tar_path] = (tf, set(tf.getnames()))
        return self._tar_cache[tar_path]

    def __len__(self):
        return len(self.index)

    def __getitem__(self, idx):
        tar_path, prefix, img_names = self.index[idx]
        try:
            tf, all_names = self._get_tar(tar_path)
            json_name = f"{prefix}.json"
            jf = tf.extractfile(json_name)
            meta = json.load(io.BytesIO(jf.read()))
            prompts = meta.get('prompts', ['What is this?\n<image>'])
            captions = meta.get('captions', ['a photo'])
            choice = random.randint(0, len(prompts) - 1)
            prompt = prompts[choice]
            caption = captions[choice] if choice < len(captions) else captions[0]
            img_name = img_names[0]
            img_file = tf.extractfile(img_name)
            image = Image.open(io.BytesIO(img_file.read())).convert('RGB')
            return image, prompt, caption
        except Exception:
            image = Image.new('RGB', (224, 224), (0, 0, 0))
            return image, "What is this?\n<image>", "an image"

def expand_image_tokens(ids, num_expansion=NUM_IMAGE_TOKENS):
    result = []
    for tid in ids:
        if tid == IMAGE_TOKEN_ID:
            result.extend([IMAGE_TOKEN_ID] * num_expansion)
        else:
            result.append(tid)
    return result

def collate_fn(batch, tokenizer, transform, seq_len):
    input_ids_list, labels_list, pixel_values_list = [], [], []
    for image, prompt, caption in batch:
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
    padded_ids = torch.full((len(batch), max_len), tokenizer.pad_token_id, dtype=torch.long)
    padded_labels = torch.full((len(batch), max_len), -100, dtype=torch.long)
    attention_mask = torch.zeros((len(batch), max_len), dtype=torch.long)
    for i, (ids, labels) in enumerate(zip(input_ids_list, labels_list)):
        L = ids.shape[0]
        padded_ids[i, :L] = ids
        padded_labels[i, :L] = labels
        attention_mask[i, :L] = 1
    pixel_values = torch.stack(pixel_values_list)
    return {'input_ids': padded_ids, 'attention_mask': attention_mask,
            'labels': padded_labels, 'pixel_values': pixel_values}

# ---- model setup ----
def build_model(device, dtype, args):
    """Load vision tower (frozen) + projector (from Stage-1, trainable) + LLM (LoRA)."""
    print0("Loading vision tower (ArmD open_clip ViT-B/16, 768-dim, frozen)...")
    vision, _, _ = create_baize_vitb16_768(pretrained=CKPT, device="cpu")
    vision = vision.to(device=device, dtype=dtype)
    for p in vision.parameters():
        p.requires_grad = False
    vision.eval()
    nv = sum(p.numel() for p in vision.parameters())
    print0(f"  Vision: {nv/1e6:.2f}M params (frozen)")

    print0("Loading projector from Stage-1 step2500...")
    projector = BaizeMultiModalProjector(VISION_HIDDEN_SIZE, LLM_HIDDEN_SIZE)
    projector = projector.to(device=device, dtype=dtype)
    ck = torch.load(PROJECTOR_CKPT, map_location="cpu", weights_only=False)
    sd = ck.get('projector', ck) if isinstance(ck, dict) else ck
    sd = {k.replace('module.', '', 1) if k.startswith('module.') else k: v for k, v in sd.items()}
    result = projector.load_state_dict(sd, strict=True)
    print0(f"  Projector loaded: matched={len(sd)-len(result.missing_keys)-len(result.unexpected_keys)}/{len(sd)}")
    n_proj = sum(p.numel() for p in projector.parameters())
    print0(f"  Projector: {n_proj/1e6:.2f}M params (trainable, from Stage-1)")

    print0("Loading LLM (Qwen3-4B) + applying LoRA...")
    llm = AutoModelForCausalLM.from_pretrained(
        LLM_PATH, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    for p in llm.parameters():
        p.requires_grad = False

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    llm = get_peft_model(llm, lora_config)
    llm.print_trainable_parameters()
    n_lora = sum(p.numel() for p in llm.parameters() if p.requires_grad)
    print0(f"  LoRA trainable: {n_lora/1e6:.2f}M params")

    return vision, projector, llm

def inject_image_features(llm, input_ids, image_features):
    """Replace IMAGE_TOKEN_ID placeholders with projected image features."""
    # Unwrap DDP to access get_input_embeddings (DDP only exposes forward())
    llm_raw = llm.module if hasattr(llm, 'module') else llm
    embed_tokens = llm_raw.get_input_embeddings()
    inputs_embeds = embed_tokens(input_ids)
    B, S, H = inputs_embeds.shape
    for b in range(B):
        img_mask = (input_ids[b] == IMAGE_TOKEN_ID)
        n_img = img_mask.sum().item()
        if n_img == 0:
            continue
        n_feat = image_features.shape[1]
        if n_img == n_feat:
            inputs_embeds[b, img_mask] = image_features[b]
        elif n_img > n_feat:
            inputs_embeds[b, img_mask][:n_feat] = image_features[b]
        else:
            inputs_embeds[b, img_mask] = image_features[b, :n_img]
    return inputs_embeds

# ---- LR schedule ----
def get_lr(step, nsteps, lr, min_lr, warmup_frac):
    warmup_steps = max(1, int(nsteps * warmup_frac))
    if step < warmup_steps:
        return lr * step / warmup_steps
    progress = (step - warmup_steps) / max(1, nsteps - warmup_steps)
    return min_lr + 0.5 * (lr - min_lr) * (1 + math.cos(math.pi * min(1.0, progress)))

def save_checkpoint(projector, llm, output_dir, step, rank=0):
    """Save projector weights + LoRA adapter."""
    if rank != 0:
        return
    ckpt_dir = os.path.join(output_dir, f"step{step}")
    os.makedirs(ckpt_dir, exist_ok=True)
    proj_module = projector.module if hasattr(projector, 'module') else projector
    torch.save({'projector': proj_module.state_dict(), 'step': step},
               os.path.join(ckpt_dir, 'projector.pt'))
    llm_module = llm.module if hasattr(llm, 'module') else llm
    llm_module.save_pretrained(ckpt_dir)
    print0(f"  Saved checkpoint to {ckpt_dir}/ (projector.pt + LoRA adapter)")

def main():
    args = parse_args()
    rank, world, local = setup_ddp()
    device = torch.device(f'cuda:{local}')
    dtype = torch.bfloat16
    if is_main():
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    print0("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    transform = T.Compose([
        T.Resize(int(224 * 1.15)), T.CenterCrop(224), T.ToTensor(),
        T.Normalize(CLIP_MEAN, CLIP_STD),
    ])

    print0("Building dataset index...")
    dataset = LLaVA558KDataset(DATA_DIR, rank=rank, world=world,
                               max_images_per_sample=args.max_images_per_sample)
    sampler = DistributedSampler(dataset, shuffle=True, drop_last=True) if world > 1 else None
    loader = DataLoader(dataset, batch_size=args.mbs, shuffle=(sampler is None),
                        sampler=sampler, num_workers=args.num_workers, pin_memory=True,
                        drop_last=True,
                        collate_fn=lambda b: collate_fn(b, tokenizer, transform, args.seq_len))

    vision, projector, llm = build_model(device, dtype, args)
    if world > 1:
        projector = nn.parallel.DistributedDataParallel(projector, device_ids=[local], output_device=local)
        llm = nn.parallel.DistributedDataParallel(llm, device_ids=[local], output_device=local,
                                                   find_unused_parameters=True)

    lora_params = [p for p in llm.parameters() if p.requires_grad]
    proj_params = [p for p in projector.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam([
        {'params': lora_params, 'lr': args.lr_lora},
        {'params': proj_params, 'lr': args.lr_proj},
    ], betas=(0.9, 0.99), eps=1e-5)

    n_lora = sum(p.numel() for p in lora_params)
    n_proj = sum(p.numel() for p in proj_params)
    print0(f"\n=== Stage-1.5 Mid-Training (LoRA) ===")
    print0(f"  Steps: {args.nsteps}, GBS={args.gbs}, MBS={args.mbs}")
    print0(f"  LoRA: r={args.lora_r}, alpha={args.lora_alpha}")
    print0(f"  LR: LoRA={args.lr_lora} / Proj={args.lr_proj} -> {args.min_lr}")
    print0(f"  Trainable: {n_lora/1e6:.2f}M (LoRA) + {n_proj/1e6:.2f}M (Proj) = {(n_lora+n_proj)/1e6:.2f}M")

    accum_steps = max(1, args.gbs // (args.mbs * world))
    step = 0
    accum_count = 0
    total_loss = 0.0
    log_loss = 0.0
    log_count = 0
    start_time = time.time()
    epoch = 0
    if sampler is not None:
        sampler.set_epoch(epoch)
    data_iter = iter(loader)

    while step < args.nsteps:
        try:
            batch = next(data_iter)
        except StopIteration:
            epoch += 1
            if sampler is not None:
                sampler.set_epoch(epoch)
            data_iter = iter(loader)
            batch = next(data_iter)

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        pixel_values = batch['pixel_values'].to(device=device, dtype=dtype)

        with torch.no_grad():
            vis_feat = vision(pixel_values)
        proj_feat = projector(vis_feat)
        inputs_embeds = inject_image_features(llm, input_ids, proj_feat)
        outputs = llm(inputs_embeds=inputs_embeds, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss / accum_steps

        loss.backward()
        total_loss += loss.item() * accum_steps
        log_loss += loss.item() * accum_steps
        log_count += 1

        accum_count += 1
        if accum_count >= accum_steps:
            lr_lora = get_lr(step, args.nsteps, args.lr_lora, args.min_lr, args.warmup_frac)
            lr_proj = get_lr(step, args.nsteps, args.lr_proj, args.min_lr, args.warmup_frac)
            optimizer.param_groups[0]['lr'] = lr_lora
            optimizer.param_groups[1]['lr'] = lr_proj
            torch.nn.utils.clip_grad_norm_(lora_params + proj_params, max_norm=1.0)
            optimizer.step()
            optimizer.zero_grad()
            accum_count = 0
            step += 1

            if step % args.log_steps == 0:
                avg_loss = log_loss / log_count
                elapsed = time.time() - start_time
                sps = step / elapsed
                eta = (args.nsteps - step) / max(1e-6, sps)
                mem_gb = torch.cuda.max_memory_allocated(device) / 1e9
                print0(f"  Step {step:>5}/{args.nsteps} | loss={avg_loss:.4f} | "
                       f"lr_lora={lr_lora:.2e} lr_proj={lr_proj:.2e} | "
                       f"{sps:.2f} steps/s | ETA={eta/60:.1f}min | GPU={mem_gb:.1f}GB")
                log_loss = 0.0
                log_count = 0

            if step % args.save_steps == 0:
                save_checkpoint(projector, llm, OUTPUT_DIR, step, rank)

    save_checkpoint(projector, llm, OUTPUT_DIR, args.nsteps, rank)
    print0(f"\n=== Stage-1.5 Training Complete ===")
    print0(f"  Total time: {(time.time()-start_time)/60:.1f} min")
    print0(f"  Final avg loss: {total_loss/max(1,step):.4f}")
    print0(f"  Final checkpoint: {OUTPUT_DIR}/step{args.nsteps}/")
    cleanup()

if __name__ == "__main__":
    main()

