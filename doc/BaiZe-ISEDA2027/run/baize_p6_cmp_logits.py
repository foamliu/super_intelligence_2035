#!/usr/bin/env python3
# P-6 第1步：最终 logits 对拍（mcore 已正确加载 checkpoint 后）。
import torch

A = torch.load("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/p6_cap_mcore_v2.pt", map_location="cpu", weights_only=False)
B = torch.load("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/p6_cap_hf.pt", map_location="cpu", weights_only=False)

la = A["logits"].float()   # [1,1,V] last token
lb = B["logits"].float()   # [1,S,V]
ref = la[0, 0]             # last token logits
hf = lb[0, -1]

print("ref shape", tuple(la.shape), "hf shape", tuple(lb.shape))
d = (hf - ref).abs()
print(f"ref_argmax={ref.argmax().item()} hf_argmax={hf.argmax().item()} match={ref.argmax().item()==hf.argmax().item()}")
print(f"max_abs_diff={d.max().item():.4e} mean_abs_diff={d.mean().item():.4e}")
print(f"ref_std={ref.std().item():.4f} hf_std={hf.std().item():.4f}")
for k in (1, 5, 10, 50, 100):
    a = set(torch.topk(ref, k).indices.tolist())
    b = set(torch.topk(hf, k).indices.tolist())
    print(f"top{k} overlap={len(a & b)}/{k}")
# 相关系数
corr = torch.corrcoef(torch.stack([ref, hf]))[0,1].item()
print(f"pearson_corr={corr:.6f}")