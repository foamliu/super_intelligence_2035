#!/bin/bash
# Launch B1 extension benchmark on GPU1
cd /nas_train/app.e0031982/code/super_intelligence_2035
export PYTHONPATH=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5
exec /nas_train/app.e0031982/miniforge3/envs/py310/bin/python \
    doc/BaiZe-ISEDA2027/run/baize_b1_longctx_extend.py
