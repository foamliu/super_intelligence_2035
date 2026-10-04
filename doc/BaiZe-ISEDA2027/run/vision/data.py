"""Data loading: WebDataset shards -> (image, tokenized-caption) batches for SigLIP/CLIP training."""
import io
import os
import random

import torch
import torchvision.transforms as T
import webdataset as wds

MEAN = (0.48145466, 0.4578275, 0.40821073)
STD = (0.26862954, 0.26130258, 0.27577711)


def get_train_transform(size: int = 224):
    return T.Compose([
        T.RandomResizedCrop(size, scale=(0.5, 1.0)),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize(MEAN, STD),
    ])


def get_val_transform(size: int = 224):
    return T.Compose([
        T.Resize(int(size * 1.15)),
        T.CenterCrop(size),
        T.ToTensor(),
        T.Normalize(MEAN, STD),
    ])


def _no_split(src, group=None):
    """Identity nodesplitter: shard partitioning is done by the caller (rank-sliced list)."""
    yield from src


def build_loader(shard_list, batch_size: int, tokenizer, size: int = 224,
                 num_workers: int = 6, shuffle: bool = True, train: bool = True,
                 drop_last: bool = True):
    """`shard_list` is an explicit list of tar paths (already rank-sliced)."""
    tf = get_train_transform(size) if train else get_val_transform(size)
    dataset = (
        wds.WebDataset(shard_list, nodesplitter=_no_split,
                       shardshuffle=(200 if shuffle else 0))
        .shuffle(2000 if shuffle else 0)
        .decode('pil', handler=wds.ignore_and_continue)
        .to_tuple('png;jpg;img', 'txt')
        .map(lambda s: (tf(s[0]), s[1]), handler=wds.ignore_and_continue)
    )

    def collate(batch):
        imgs = torch.stack([b[0] for b in batch])
        caps = [b[1] for b in batch]
        texts = tokenizer(caps)
        return imgs, texts

    loader = wds.WebLoader(dataset, batch_size=batch_size, num_workers=num_workers,
                           collate_fn=collate, drop_last=drop_last)
    return loader


def build_gpic_loader(shard_list, batch_size: int, tokenizer, size: int = 224,
                      num_workers: int = 6, shuffle: bool = True, train: bool = True,
                      drop_last: bool = True, caption_type='short'):
    """GPIC loader (no re-packing). Reads GPIC tar = `{key}.json` (caption/caption_type)
    + `{key}.jpg|png`, keeps only pairs whose caption_type matches `caption_type`
    ('short' / 'medium' / 'short+medium'; 'long' NOT supported — 100% 77-truncation).

    R11-F (2026-10-04): caption_type param added so GPIC arms A/B/C can select
    short / medium / short+medium from the SAME frozen tar snapshot."""
    import json as _json
    from PIL import Image as _Image
    from webdataset import ignore_and_continue

    tf = get_train_transform(size) if train else get_val_transform(size)

    def gpic_decode(sample):
        try:
            meta = _json.loads(sample.get('json') or b'{}')
        except Exception:
            return None
        _ct = meta.get('caption_type')
        if caption_type == 'short+medium':
            if _ct not in ('short', 'medium'):
                return None
        elif _ct != caption_type:
            return None
        cap = (meta.get('caption') or '').strip()
        raw = sample.get('jpg') or sample.get('png') or sample.get('img')
        if not raw or not cap:
            return None
        try:
            img = _Image.open(io.BytesIO(raw)).convert('RGB')
        except Exception:
            return None
        return tf(img), cap

    dataset = (
        wds.WebDataset(shard_list, nodesplitter=_no_split,
                       shardshuffle=(200 if shuffle else 0),
                       handler=ignore_and_continue)
        .shuffle(2000 if shuffle else 0)
        .map(gpic_decode)
        .select(lambda s: s is not None)
    )

    def collate(batch):
        imgs = torch.stack([b[0] for b in batch])
        caps = [b[1] for b in batch]
        texts = tokenizer(caps)
        return imgs, texts

    loader = wds.WebLoader(dataset, batch_size=batch_size, num_workers=num_workers,
                           collate_fn=collate, drop_last=drop_last)
    return loader