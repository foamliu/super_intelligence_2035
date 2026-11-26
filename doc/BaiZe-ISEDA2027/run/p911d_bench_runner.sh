#!/bin/bash
# D bench runner — launched via nohup to survive SSH disconnect
export no_proxy=localhost,127.0.0.1
export NO_PROXY=localhost,127.0.0.1
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python p911d_sglang_vram_bench.py \
    --base-url http://127.0.0.1:30001 \
    --model-name default \
    --model-path /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000 \
    --gpu-id 0 \
    --output /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/p911d_hybrid_vram_results.json \
    --contexts 4096 16384 65536 131072 \
    --batches 1 8 \
    --gen-len 64 \
    > /tmp/p911d_bench3.log 2>&1
echo "BENCH DONE rc=$?" >> /tmp/p911d_bench3.log