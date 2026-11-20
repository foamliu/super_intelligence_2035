#!/usr/bin/env python3
"""Quick forward pass test: check if iter_20000 (degraded) produces NaN logits.
Uses same setup as cpu_lmeval_run.py (block mamba_ssm/causal_conv1d)."""
import sys, os, types, warnings
warnings.filterwarnings("ignore")
for mod_name in ["mamba_ssm", "causal_conv1d"]:
    fake = types.ModuleType(mod_name)
    fake.__file__ = f"<blocked:{mod_name}>"
    fake.__path__ = []
    sys.modules[mod_name] = fake
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch
torch.set_num_threads(8)
from transformers import AutoModelForCausalLM, AutoTokenizer

base = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
tok = AutoTokenizer.from_pretrained(base + "/hf_iter_10000")

for it in [10000, 20000, 30000, 40000]:
    print(f"--- iter_{it} ---", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        base + f"/hf_iter_{it}", dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()
    ids = tok("Hello world", return_tensors="pt")
    with torch.no_grad():
        out = model(**ids)
    logits = out.logits[0, -1, :]
    nan_c = torch.isnan(logits).sum().item()
    inf_c = torch.isinf(logits).sum().item()
    print(f"  logits: NaN={nan_c} Inf={inf_c} min={logits.min():.4f} max={logits.max():.4f} std={logits.std():.4f}", flush=True)
    if nan_c == 0 and inf_c == 0 and logits.std() > 0.001:
        top5 = torch.topk(logits, 5)
        print(f"  top5 ids={top5.indices.tolist()} vals={[round(v,3) for v in top5.values.tolist()]}", flush=True)
    else:
        print("  OUTPUT CORRUPT (NaN/Inf in logits)", flush=True)
    del model
    import gc; gc.collect()
print("=== DONE ===", flush=True)
