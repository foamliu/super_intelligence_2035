#!/usr/bin/env python3
# P-6 对拍诊断：对比 mcore 与 HF 的逐层激活，定位第一个分歧点。
import torch

A = torch.load("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/p6_cap_mcore_v2.pt", map_location="cpu", weights_only=False)
B = torch.load("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/p6_cap_hf.pt", map_location="cpu", weights_only=False)

print("input_ids equal:", bool((A["input_ids"].long() == B["input_ids"].long()).all()),
      A["input_ids"].shape, A["input_ids"].flatten()[:10].tolist())

def to_bch(x):
    # megatron [S,B,H] -> [B,S,H]
    t = x.float()
    if t.ndim == 3:
        t = t.transpose(0, 1)
    return t

for k in ["emb", "L0", "L1", "L10", "L55", "final"]:
    a = to_bch(A["caps"][k])
    b = B["caps"][k].float()
    diff = (a - b).abs()
    # relative to magnitude
    rel = diff / (a.abs() + 1e-6)
    # cosine similarity
    cos = torch.nn.functional.cosine_similarity(a.flatten().unsqueeze(0), b.flatten().unsqueeze(0)).item() if a.shape == b.shape else float("nan")
    print(f"[{k}] shape a={tuple(a.shape)} b={tuple(b.shape)} "
          f"max_abs_diff={diff.max().item():.4e} mean_abs_diff={diff.mean().item():.4e} "
          f"a_std={a.std().item():.4f} b_std={b.std().item():.4f} cos={cos:.6f}")

# logits compare
la = A["logits"].float()  # [1,S,V]? megatron runtime_gather -> [B,S,V]
lb = B["logits"].float()
print("logits shapes", tuple(la.shape), tuple(lb.shape))
if la.shape == lb.shape:
    d = (la - lb).abs()
    print(f"[logits] max_abs_diff={d.max().item():.4e} mean={d.mean().item():.4e} "
          f"argmaxA={la[0,-1].argmax().item()} argmaxB={lb[0,-1].argmax().item()}")
else:
    # transpose megatron logits if [S,B,V]
    la2 = la.transpose(0,1) if la.ndim==3 and la.shape[0]==lb.shape[1] else la
    if la2.shape==lb.shape:
        d=(la2-lb).abs()
        print(f"[logits] max_abs_diff={d.max().item():.4e} mean={d.mean().item():.4e} "
              f"argmaxA={la2[0,-1].argmax().item()} argmaxB={lb[0,-1].argmax().item()}")