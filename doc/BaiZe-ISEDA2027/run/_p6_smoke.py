#!/usr/bin/env python3
# P-6 smoke test: can lm_eval (0.4.13) HFLM load NemotronH via transformers 5.17.0 (p6_tf5)?
# 只做最小验证：加载模型 + 3 条 loglikelihood，不跑全量任务。
import sys, os, time
sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

t0 = time.time()
import torch  # noqa
print("[smoke] transformers =", __import__("transformers").__version__, flush=True)

from lm_eval.models.huggingface import HFLM  # noqa
from lm_eval.api.instance import Instance  # noqa

MODEL = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/hf_nemotron_h"

m = HFLM(pretrained=MODEL, batch_size=1, dtype="bfloat16", device="cuda")
print(f"[smoke] model loaded in {time.time()-t0:.1f}s", flush=True)

# 三条简单 loglikelihood 请求（模拟 multiple-choice 打分）
reqs = [
    ("The capital of France is", {"Paris": 0, "London": 0}),
    ("Mitochondria are the", {"powerhouse": 0, "garbage": 0}),
]
out = m.loglikelihood(reqs)
for (ctx, conts), r in zip(reqs, out):
    print(f"[smoke] ctx={ctx!r} -> {[(c, round(float(v),3)) for c,v in zip(conts.keys(), r)]}", flush=True)

print("[smoke] DONE", flush=True)