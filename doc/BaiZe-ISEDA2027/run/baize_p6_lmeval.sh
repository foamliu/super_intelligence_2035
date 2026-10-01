#!/usr/bin/env bash
# P-6 第 1 步：现有 20000 步 ckpt（已转 HF Nemotron-H）的 lm_eval 8 集零样本评测。
#
# 关键：用 p6_tf5（transformers 5.17.0，含 NemotronHForCausalLM）隔离装，
#       经 PYTHONPATH 前置，让 lm_eval(0.4.13) 的 HFLM 用 5.17.0 加载 nemotron_h。
# 已冒烟通过：HFLM 加载 323 权重 / 10.6s / 前向正常（见 _p6_smoke.py）。
#
# 用法:  bash baize_p6_lmeval.sh [--limit N]   (N 省略=全量)
set -euo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
# 直连 huggingface.co 的 LFS CDN (cdn-lfs.huggingface.co) 被代理 DNS 拦截，改用可达的 hf-mirror 镜像。
export HF_ENDPOINT="https://hf-mirror.com"

MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/hf_nemotron_h"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/lm_eval_results"
TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"

LIMIT=""
if [[ "${1:-}" == "--limit" ]]; then LIMIT="--limit $2"; fi

mkdir -p "$OUT"

exec python -m lm_eval \
  --model hf \
  --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
  --tasks "$TASKS" \
  --num_fewshot 0 \
  --batch_size 2 \
  --output_path "$OUT" \
  $LIMIT