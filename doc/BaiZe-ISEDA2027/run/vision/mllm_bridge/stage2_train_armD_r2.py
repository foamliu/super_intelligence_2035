#!/usr/bin/env python
"""Stage-2 Instruct Tuning (ArmD): continue LoRA+projector on instruction data.

ArmD variant of stage2_train.py — only the vision tower + projector width differ:
  - Vision tower: ArmD open_clip ViT-B/16 (86.2M, 768-dim patch tokens, FROZEN)
  - Projector: 2-layer MLP 768->2560 (trainable, loaded from Stage-1.5 step20000)
  - LLM: Qwen3-4B-Instruct-2507 + LoRA r=64 (trainable, loaded from Stage-1.5)

After Stage-1.5 mid-training adapted the LLM to ArmD visual features (20k steps),
Stage-2 fine-tunes on higher-quality instruction data (LLaVA-NeXT-780k) to teach
the model to follow user instructions in a chat format.

Loads from Stage-1.5 final checkpoint (step20000): both projector weights and
LoRA adapter. Vision tower stays frozen.

Hyperparameters (operator instruction 2026-10-18 P0 ④, = stage2_train.py defaults):
  - LoRA: rank=64, alpha=128, dropout=0.05 (loaded from Stage-1.5, continued)
  - LR: 1e-5 (LoRA), 5e-6 (projector), cosine decay -> 1e-7, warmup 0.01
  - Steps: 3500, GBS=8, MBS=1
  - Image: 224x224, CLIP normalization, 196 tokens, no spatial merge
  - Data: LLaVA-NeXT-780k Instruct WebDataset (same as ④-4ep)

Usage (8 GPUs):
  cd run/vision
  torchrun --nproc_per_node=8 mllm_bridge/stage2_train_armB.py
"""

import sys, os, time, json, io, math, random
import tarfile
from pathlib import Path

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import transforms as T
from PIL import Image

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

# ArmD open_clip ViT-B/16 checkpoint (clip-only, predictor stripped)
CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/armD_r2_20261020_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
STAGE15_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armD_r2_20261020/step20000"
DATA_DIR = "/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-NeXT-780k-plus-Instruct-opt47-webdataset"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armD_r2_20261020"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
VISION_HIDDEN_SIZE = 768  # ArmD open_clip ViT-B/16 patch-token dim (vs ④'s 512)
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--lr_lora', type=float, default=1e-5)
    p.add_argument('--lr_proj', type=float, default=5e-6)
    p.add_argument('--min_lr', type=float, default=1e-7)
    p.add_argument('--nsteps', type=int, default=3500)
    p.add_argument('--gbs', type=int, default=8)
    p.add_argument('--mbs', type=int, default=1)
    p.add_argument('--warmup_frac', type=float, default=0.01)
    p.add_argument('--seq_len', type=int, default=2048)
    p.add_argument('--num_workers', type=int, default=4)
    p.add_argument('--save_steps', type=int, default=500)
    p.add_argument('--log_steps', type=int, default=50)
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

# ---- data: LLaVA-NeXT-780k Instruct (chat format) ----
class LLaVANeXTInstructDataset(Dataset):
    """LLaVA-NeXT-780k instruction data in WebDataset tar format."""
    def __init__(self, data_dir, rank=0, world=1):
        self.data_dir = data_dir
        self._tar_cache = {}
        self.index = []

        if world > 1 and rank > 0:
            # Non-root ranks: wait for rank 0 to build and broadcast the index
            dist.barrier()
            recv = [None]
            dist.broadcast_object_list(recv, src=0)
            self.index = recv[0]
            tars_count = len(set(t for t, _, _ in self.index))
        else:
            # Rank 0 (or single-GPU): build the index
            tars = sorted(Path(data_dir).glob('data-*.tar'))
            for tar_path in tars:
                try:
                    with tarfile.open(str(tar_path), 'r') as tf:
                        names = tf.getnames()
                    groups = {}
                    for n in names:
                        if n.endswith('.json'):
                            prefix = n.rsplit('.json', 1)[0]
                            g = groups.setdefault(prefix, {'json': False, 'imgs': []})
                            g['json'] = True
                        elif n.endswith(('.jpg', '.png', '.jpeg')):
                            parts = n.rsplit('.', 2)
                            prefix = parts[0] if len(parts) >= 3 else n.rsplit('.', 1)[0]
                            g = groups.setdefault(prefix, {'json': False, 'imgs': []})
                            g['imgs'].append(n)
                    for prefix, info in groups.items():
                        if info['json'] and len(info['imgs']) > 0:
                            self.index.append((str(tar_path), prefix, sorted(info['imgs'])))
                except Exception as e:
                    print0(f"WARNING: failed to index {tar_path}: {e}")
            tars_count = len(tars)
            print0(f"[Rank {rank}] Dataset: {len(self.index)} samples from {tars_count} tars")

            if world > 1:
                # Broadcast index to all ranks
                dist.barrier()
                dist.broadcast_object_list([self.index], src=0)

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
            jf = tf.extractfile(f"{prefix}.json")
            meta = json.load(io.BytesIO(jf.read()))
            texts = meta.get('texts', [])
            if not texts:
                return Image.new('RGB', (224, 224), (0, 0, 0)), "What is this?\n<image>", "an image"
            user_text, assistant_text = "", ""
            for msg in texts:
                if msg['role'] == 'user':
                    user_text = msg['content']
                elif msg['role'] == 'assistant':
                    assistant_text = msg['content']
            if not user_text:
                user_text = "What is this?\n<image>"
            if not assistant_text:
                assistant_text = "an image"
            if '<image>' not in user_text:
                user_text = '<image>\n' + user_text
            img_file = tf.extractfile(img_names[0])
            image = Image.open(io.BytesIO(img_file.read())).convert('RGB')
            return image, user_text, assistant_text
        except Exception:
            return Image.new('RGB', (224, 224), (0, 0, 0)), "What is this?\n<image>", "an image"

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
    for image, user_text, assistant_text in batch:
        pixel = transform(image)
        pixel_values_list.append(pixel)
        prompt_text = user_text.replace('<image>', '<|image_pad|>')
        user_part = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
        assistant_part = f"{assistant_text}<|im_end|>"
        full_text = user_part + assistant_part
        full_ids = tokenizer(full_text, add_special_tokens=False)['input_ids']
        user_ids = tokenizer(user_part, add_special_tokens=False)['input_ids']
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
    """Load vision tower (ArmD, frozen) + projector (from Stage-1.5, trainable) + LLM (LoRA from Stage-1.5)."""
    print0("Loading vision tower (ArmD open_clip ViT-B/16, 768-dim, frozen)...")
    vision, _, _ = create_baize_vitb16_768(pretrained=CKPT, device="cpu")
    vision = vision.to(device=device, dtype=dtype)
    for p in vision.parameters():
        p.requires_grad = False
    vision.eval()
    nv = sum(p.numel() for p in vision.parameters())
    print0(f"  Vision: {nv/1e6:.2f}M params (frozen)")

    print0(f"Loading projector from Stage-1.5 ({STAGE15_DIR})...")
    projector = BaizeMultiModalProjector(VISION_HIDDEN_SIZE, LLM_HIDDEN_SIZE)
    projector = projector.to(device=device, dtype=dtype)
    ck = torch.load(os.path.join(STAGE15_DIR, 'projector.pt'), map_location="cpu", weights_only=False)
    sd = ck.get('projector', ck) if isinstance(ck, dict) else ck
    sd = {k.replace('module.', '', 1) if k.startswith('module.') else k: v for k, v in sd.items()}
    projector.load_state_dict(sd, strict=True)
    n_proj = sum(p.numel() for p in projector.parameters())
    print0(f"  Projector: {n_proj/1e6:.2f}M params (trainable, from Stage-1.5)")

    print0(f"Loading LLM (Qwen3-4B) + LoRA adapter from Stage-1.5...")
    llm = AutoModelForCausalLM.from_pretrained(
        LLM_PATH, torch_dtype=dtype, device_map={'': device}, trust_remote_code=True)
    llm = PeftModel.from_pretrained(llm, STAGE15_DIR, is_trainable=True)
    llm.print_trainable_parameters()
    return vision, projector, llm

def inject_image_features(llm, input_ids, image_features):
    """Replace IMAGE_TOKEN_ID placeholders with projected image features."""
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

def get_lr(step, nsteps, lr, min_lr, warmup_frac):
    warmup_steps = max(1, int(nsteps * warmup_frac))
    if step < warmup_steps:
        return lr * step / warmup_steps
    progress = (step - warmup_steps) / max(1, nsteps - warmup_steps)
    return min_lr + 0.5 * (lr - min_lr) * (1 + math.cos(math.pi * min(1.0, progress)))

def save_checkpoint(projector, llm, output_dir, step, rank=0):
    if rank != 0:
        return
    ckpt_dir = os.path.join(output_dir, f"step{step}")
    os.makedirs(ckpt_dir, exist_ok=True)
    proj_module = projector.module if hasattr(projector, 'module') else projector
    torch.save({'projector': proj_module.state_dict(), 'step': step},
               os.path.join(ckpt_dir, 'projector.pt'))
    llm_module = llm.module if hasattr(llm, 'module') else llm
    llm_module.save_pretrained(ckpt_dir)
    print0(f"  Saved checkpoint to {ckpt_dir}/")

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

    print0("Building instruction dataset index...")
    dataset = LLaVANeXTInstructDataset(DATA_DIR, rank=rank, world=world)
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
    print0(f"\n=== Stage-2 Instruct Tuning ===")
    print0(f"  Steps: {args.nsteps}, GBS={args.gbs}, MBS={args.mbs}")
    print0(f"  LR: LoRA={args.lr_lora} / Proj={args.lr_proj} -> {args.min_lr}")
    print0(f"  Trainable: {n_lora/1e6:.2f}M (LoRA) + {n_proj/1e6:.2f}M (Proj) = {(n_lora+n_proj)/1e6:.2f}M")
    print0(f"  Data: LLaVA-NeXT-780k Instruct ({len(dataset)} samples)")

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
    print0(f"\n=== Stage-2 Training Complete ===")
    print0(f"  Total time: {(time.time()-start_time)/60:.1f} min")
    print0(f"  Final avg loss: {total_loss/max(1,step):.4f}")
    print0(f"  Final checkpoint: {OUTPUT_DIR}/step{args.nsteps}/")
    cleanup()

if __name__ == "__main__":
    main()
