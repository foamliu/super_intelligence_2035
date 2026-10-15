#!/usr/bin/env bash
# Launcher: starts 3 Xmodel-2.5 evals in background on different GPUs
SCRIPT_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
EVAL_BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/xmodel_eval"
RESULTS_BASE="$EVAL_BASE/lm_eval_results"

# step_4000 on GPU 4
rm -rf "$RESULTS_BASE/xmodel25_step_4000"
nohup bash "$SCRIPT_DIR/xmodel_eval_common8_single_gpu.sh" \
    "$EVAL_BASE/xmodel25_step_4000" \
    "$RESULTS_BASE/xmodel25_step_4000" 4 true \
    > /tmp/xmodel25_step_4000_eval.log 2>&1 &
echo "step_4000 launched PID $!"

# step_8000 on GPU 7
rm -rf "$RESULTS_BASE/xmodel25_step_8000"
nohup bash "$SCRIPT_DIR/xmodel_eval_common8_single_gpu.sh" \
    "$EVAL_BASE/xmodel25_step_8000" \
    "$RESULTS_BASE/xmodel25_step_8000" 7 true \
    > /tmp/xmodel25_step_8000_eval.log 2>&1 &
echo "step_8000 launched PID $!"

echo "DONE launching"
