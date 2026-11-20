#!/usr/bin/env python3
"""Find exact NaN onset threshold: test seq lengths 2,4,6,8,10,12,14,16 on iter_20000."""
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

# Use a long text and truncate to different lengths
long_text = "The quick brown fox jumps over the lazy dog. " * 10
all_ids = tok(long_text, return_tensors="pt", add_special_tokens=False)["input_ids"][0]
print(f"Total tokens available: {len(all_ids)}", flush=True)

for it in [10000, 20000]:
    print(f"\n--- iter_{it} ---", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        base + f"/hf_iter_{it}", dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()
    for n in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        ids = all_ids[:n].unsqueeze(0)
        with torch.no_grad():
            out = model(input_ids=ids)
        logits = out.logits[0, -1, :]
        nan_c = torch.isnan(logits).sum().item()
        inf_c = torch.isinf(logits).sum().item()
        status = "OK" if nan_c == 0 and inf_c == 0 else "**NaN**"
        print(f"  n={n:3d}: NaN={nan_c:6d} Inf={inf_c:6d}  {status}", flush=True)
    del model
    import gc; gc.collect()
print("\n=== DONE ===", flush=True)
