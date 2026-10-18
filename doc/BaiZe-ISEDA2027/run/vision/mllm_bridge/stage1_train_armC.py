#!/usr/bin/env python
"""Stage-1 Alignment Training: freeze vision+LLM, train projector only.

Trains the 2-layer MLP projector (768->2560) to align ArmC (open_clip ViT-B/16) vision features
with Qwen3-4B's embedding space using the LLaVA-558K pretraining dataset.
  ArmC: open_clip ViT-B/16 224px, 86.2M visual, 768-dim patch tokens, 196 tokens.

Hyperparameters (from train_4b.sh / stage_1_alignment_llava_ov_4b.sh):
  - LR: 1e-4, cosine decay, min_lr=1e-6, warmup 0.002 fraction
  - Optimizer: Adam (beta1=0.9, beta2=0.99, eps=1e-5)
  - Steps: 2500, GBS=8, MBS=1
  - Image: 224x224, CLIP normalization
  - Image tokens: 196 (14x14), no spatial merge

Usage (8 GPUs):
  cd run/vision
  torchrun --nproc_per_node=8 mllm_bridge/stage1_train.py

Usage (1 GPU):
  CUDA_VISIBLE_DEVICES=0 python mllm_bridge/stage1_train.py
"""

import sys, os, time, json, io, math, random, traceback
import tarfile
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T
from PIL import Image

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoModelForCausalLM, AutoTokenizer
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector

# ---- constants ----
CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
DATA_DIR = "/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-558K-Webdataset"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage1_armC_20261018"
IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
VISION_HIDDEN_SIZE = 768  # ArmC open_clip ViT-B/16 patch-token dim
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

# ---- arg parsing ----
def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--lr', type=float, default=1e-4)
    p.add_argument('--min_lr', type=float, default=1e-6)
    p.add_argument('--nsteps', type=int, default=2500)
    p.add_argument('--gbs', type=int, default=8)
    p.add_argument('--mbs', type=int, default=1)
    p.add_argument('--warmup_frac', type=float, default=0.002)
    p.add_argument('--seq_len', type=int, default=2048)
    p.add_argument('--num_workers', type=int, default=4)
    p.add_argument('--save_steps', type=int, default=500)
    p.add_argument('--log_steps', type=int, default=10)
    p.add_argument('--max_images_per_sample', type=int, default=1)
    return p.parse_args()


# ---- DDP helpers ----
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


# ---- data ----
class LLaVA558KDataset(Dataset):
    """Reads LLaVA-558K WebDataset tars, yields (image, prompt, caption) pairs.

    Each tar has samples like:
      ps_XXXXX.img0.jpg, ps_XXXXX.img1.jpg, ..., ps_XXXXX.json
    The JSON has keys: prompts (list), captions (list), images (list).
    For Stage-1, we use max_images_per_sample (default 1) images per example.
    """
    def __init__(self, data_dir, rank=0, world=1, max_images_per_sample=1):
        self.data_dir = data_dir
        self.max_images = max_images_per_sample
        self._tar_cache = {}  # tar_path -> (tarfile, set_of_names)
        # Build index: all ranks index all tars (sharding done by DistributedSampler)
        self.index = []
        tars = sorted(Path(data_dir).glob('pretrain-*.tar'))
        for tar_path in tars:
            try:
                with tarfile.open(str(tar_path), 'r') as tf:
                    names = tf.getnames()
                # Group by prefix (everything before .imgN.jpg or .json)
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
        """Cache open tarfile objects per worker."""
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
            # Read JSON
            json_name = f"{prefix}.json"
            jf = tf.extractfile(json_name)
            meta = json.load(io.BytesIO(jf.read()))
            prompts = meta.get('prompts', ['What is this?\n<image>'])
            captions = meta.get('captions', ['a photo'])
            # Pick one prompt-caption pair
            choice = random.randint(0, len(prompts) - 1)
            prompt = prompts[choice]
            caption = captions[choice] if choice < len(captions) else captions[0]
            # Read first image
            img_name = img_names[0]
            img_file = tf.extractfile(img_name)
            image = Image.open(io.BytesIO(img_file.read())).convert('RGB')
            return image, prompt, caption
        except Exception as e:
            # Return a blank sample on error
            image = Image.new('RGB', (224, 224), (0, 0, 0))
            return image, "What is this?\n<image>", "an image"



def expand_image_tokens(ids, num_expansion=NUM_IMAGE_TOKENS):
    """Replace each IMAGE_TOKEN_ID (151655) with num_expansion copies."""
    result = []
    for tid in ids:
        if tid == IMAGE_TOKEN_ID:
            result.extend([IMAGE_TOKEN_ID] * num_expansion)
        else:
            result.append(tid)
    return result


def collate_fn(batch, tokenizer, transform, seq_len):
    """Collate (image, prompt, caption) -> (input_ids, labels, pixel_values).

    Replaces <image> with <|image_pad|>, tokenizes, then expands each
    image_pad token to NUM_IMAGE_TOKENS (196) copies.
    Builds labels that mask the prompt (only compute loss on the caption).
    """
    input_ids_list = []
    labels_list = []
    pixel_values_list = []

    for image, prompt, caption in batch:
        # Preprocess image
        pixel = transform(image)  # (3, 224, 224)
        pixel_values_list.append(pixel)

        # Build chat text manually (no jinja2 needed)
        prompt_text = prompt.replace('<image>', '<|image_pad|>')
        # User part (everything up to and including "<|im_start|>assistant\n")
        user_text = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
        # Assistant part (caption + <|im_end|>)
        assistant_text = f"{caption}<|im_end|>"
        full_text = user_text + assistant_text

        # Tokenize
        full_ids = tokenizer(full_text, add_special_tokens=False)['input_ids']
        user_ids = tokenizer(user_text, add_special_tokens=False)['input_ids']

        # Expand image tokens: 1 -> 196
        full_ids_exp = expand_image_tokens(full_ids, NUM_IMAGE_TOKENS)
        user_ids_exp = expand_image_tokens(user_ids, NUM_IMAGE_TOKENS)
        user_len = len(user_ids_exp)

        # Truncate if too long
        if len(full_ids_exp) > seq_len:
            full_ids_exp = full_ids_exp[:seq_len]
        if user_len > len(full_ids_exp):
            user_len = len(full_ids_exp)

        ids = torch.tensor(full_ids_exp, dtype=torch.long)
        # Labels: mask everything before assistant response
        labels = ids.clone()
        labels[:user_len] = -100

        input_ids_list.append(ids)
        labels_list.append(labels)

    # Pad to same length
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

    return {
        'input_ids': padded_ids,
        'attention_mask': attention_mask,
        'labels': padded_labels,
        'pixel_values': pixel_values,
    }



# ---- model setup ----
def build_model(device, dtype=torch.bfloat16):
    """Load vision tower (frozen) + projector (trainable) + LLM (frozen)."""
    print0("Loading vision tower (ArmC open_clip ViT-B/16, 768-dim)...")
    vision, _, _ = create_baize_vitb16_768(pretrained=CKPT, device="cpu")
    vision = vision.to(device=device, dtype=dtype)
    for p in vision.parameters():
        p.requires_grad = False
    vision.eval()
    print0(f"  Vision: {sum(p.numel() for p in vision.parameters())/1e6:.2f}M params (frozen)")

    print0("Loading projector...")
    projector = BaizeMultiModalProjector(VISION_HIDDEN_SIZE, LLM_HIDDEN_SIZE)
    projector = projector.to(device=device, dtype=dtype)
    n_proj = sum(p.numel() for p in projector.parameters() if p.requires_grad)
    print0(f"  Projector: {n_proj/1e6:.2f}M params (trainable)")

    print0("Loading LLM (Qwen3-4B)...")
    llm = AutoModelForCausalLM.from_pretrained(
        LLM_PATH, torch_dtype=dtype, device_map={'':device},
        trust_remote_code=True
    )
    for p in llm.parameters():
        p.requires_grad = False
    llm.eval()
    n_llm = sum(p.numel() for p in llm.parameters())
    print0(f"  LLM: {n_llm/1e9:.2f}B params (frozen)")

    return vision, projector, llm


def inject_image_features(llm, input_ids, image_features):
    """Replace IMAGE_TOKEN_ID placeholders with projected image features.

    image_features: (B, N_img, hidden) - already projected to LLM dim
    Returns: inputs_embeds (B, seq_len, hidden)
    """
    embed_tokens = llm.get_input_embeddings()
    inputs_embeds = embed_tokens(input_ids)  # (B, seq, hidden)

    B, S, H = inputs_embeds.shape
    for b in range(B):
        img_mask = (input_ids[b] == IMAGE_TOKEN_ID)  # (S,)
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

def save_checkpoint(projector, output_dir, step, rank=0):
    """Save projector weights."""
    if rank != 0:
        return
    ckpt_dir = os.path.join(output_dir, f"step{step}")
    os.makedirs(ckpt_dir, exist_ok=True)
    torch.save({
        'projector': projector.state_dict(),
        'step': step,
    }, os.path.join(ckpt_dir, 'projector.pt'))
    print0(f"  Saved checkpoint to {ckpt_dir}/projector.pt")


def main():
    args = parse_args()
    rank, world, local = setup_ddp()
    device = torch.device(f'cuda:{local}')
    dtype = torch.bfloat16

    if is_main():
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load tokenizer
    print0("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Image transform (val transform: deterministic resize + center crop)
    transform = T.Compose([
        T.Resize(int(224 * 1.15)),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(CLIP_MEAN, CLIP_STD),
    ])

    # Build dataset
    print0("Building dataset index...")
    dataset = LLaVA558KDataset(DATA_DIR, rank=rank, world=world,
                                max_images_per_sample=args.max_images_per_sample)

    # DataLoader with DistributedSampler
    from torch.utils.data.distributed import DistributedSampler
    sampler = DistributedSampler(dataset, shuffle=True, drop_last=True) if world > 1 else None
    loader = DataLoader(
        dataset,
        batch_size=args.mbs,
        shuffle=(sampler is None),
        sampler=sampler,
        num_workers=args.num_workers,
        pin_memory=True,
        drop_last=True,
        collate_fn=lambda batch: collate_fn(batch, tokenizer, transform, args.seq_len),
    )

    # Build model
    vision, projector, llm = build_model(device, dtype)

    # DDP wrap projector (the only trainable part)
    if world > 1:
        projector = nn.parallel.DistributedDataParallel(
            projector, device_ids=[local], output_device=local
        )

    # Optimizer: only projector params
    proj_params = [p for p in projector.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(proj_params, lr=args.lr,
                                  betas=(0.9, 0.99), eps=1e-5)

    print0(f"\n=== Stage-1 Alignment Training ===")
    print0(f"  World size: {world}")
    print0(f"  Steps: {args.nsteps}")
    print0(f"  GBS: {args.gbs}, MBS: {args.mbs}")
    print0(f"  Accum steps: {args.gbs // (args.mbs * world)}")
    print0(f"  LR: {args.lr} -> {args.min_lr} (cosine, warmup {args.warmup_frac})")
    print0(f"  Seq len: {args.seq_len}")
    print0(f"  Trainable params: {sum(p.numel() for p in proj_params)/1e6:.2f}M")
    print0()

    accum_steps = args.gbs // (args.mbs * world)
    if accum_steps < 1:
        accum_steps = 1

    # Training loop
    step = 0
    accum_count = 0
    total_loss = 0.0
    total_count = 0
    log_loss = 0.0
    log_count = 0
    start_time = time.time()

    # Use infinite iterator with epoch tracking
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
        pixel_values = batch['pixel_values'].to(device=device, dtype=dtype)  # (B, 3, 224, 224)

        # Forward: vision -> projector -> inject -> LLM
        with torch.no_grad():
            vis_feat = vision(pixel_values)  # (B, 196, 768)  ArmC open_clip bridge

        proj_feat = projector(vis_feat)  # (B, 196, 2560)

        inputs_embeds = inject_image_features(llm, input_ids, proj_feat)

        # LLM forward (frozen, but need gradients to flow to projector via inputs_embeds)
        outputs = llm(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            labels=labels,
        )
        loss = outputs.loss / accum_steps

        loss.backward()
        total_loss += loss.item() * accum_steps
        total_count += 1
        log_loss += loss.item() * accum_steps
        log_count += 1

        accum_count += 1
        if accum_count >= accum_steps:
            # LR step
            lr_now = get_lr(step, args.nsteps, args.lr, args.min_lr, args.warmup_frac)
            for pg in optimizer.param_groups:
                pg['lr'] = lr_now

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(proj_params, max_norm=1.0)

            optimizer.step()
            optimizer.zero_grad()
            accum_count = 0
            step += 1

            # Logging
            if step % args.log_steps == 0:
                avg_loss = log_loss / log_count
                elapsed = time.time() - start_time
                steps_per_sec = step / elapsed
                eta = (args.nsteps - step) / max(1e-6, steps_per_sec)
                mem_gb = torch.cuda.max_memory_allocated(device) / 1e9
                print0(f"  Step {step:>5}/{args.nsteps} | loss={avg_loss:.4f} | lr={lr_now:.2e} | "
                       f"{steps_per_sec:.2f} steps/s | ETA={eta/60:.1f}min | GPU mem={mem_gb:.1f}GB")
                log_loss = 0.0
                log_count = 0

            # Save checkpoint
            if step % args.save_steps == 0:
                proj_module = projector.module if hasattr(projector, 'module') else projector
                save_checkpoint(proj_module, OUTPUT_DIR, step, rank)

    # Final checkpoint
    proj_module = projector.module if hasattr(projector, 'module') else projector
    save_checkpoint(proj_module, OUTPUT_DIR, args.nsteps, rank)

    print0(f"\n=== Training Complete ===")
    print0(f"  Total time: {(time.time()-start_time)/60:.1f} min")
    print0(f"  Final avg loss: {total_loss/max(1,total_count):.4f}")
    print0(f"  Final checkpoint: {os.path.join(OUTPUT_DIR, f'step{args.nsteps}')}/projector.pt")

    cleanup()


if __name__ == '__main__':
    main()


