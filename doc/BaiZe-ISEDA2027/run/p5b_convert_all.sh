#!/usr/bin/env bash
# No set -e: we want to continue even if grep finds no matches
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

# Milestone iterations as actual numbers (checkpoint dir = iter_%07d)
for iter_num in 624 1248 2496 4771; do
  ckpt_dir=$(printf "iter_%07d" "$iter_num")
  out_tag=$(printf "%04d" "$iter_num")
  echo "=== Converting ${ckpt_dir} -> hf_iter_${out_tag} ==="
  PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 \
  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python baize_p6_ckpt_to_hf.py \
    --ckpt "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/checkpoints/${ckpt_dir}" \
    --tokenizer /nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/tokenizer_eod \
    --out "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_${out_tag}" \
    2>&1 | tail -5
  echo "--- done ${ckpt_dir} ---"
done
echo "ALL_DONE"

