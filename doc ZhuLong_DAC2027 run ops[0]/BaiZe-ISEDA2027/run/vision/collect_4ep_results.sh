#!/bin/bash
# ==============================================================================
# collect_4ep_results.sh — Parse ④-4ep eval results and update lp-epoch curve
#
# Run AFTER post_4ep_chain.sh has completed (i.e., /tmp/e4_4ep_eval.log has
# '④-4ep EVAL DONE').
#
# Outputs:
#   1. Parsed results to stdout + /tmp/4ep_parsed_results.txt
#   2. Updated lp-epoch curve PNG
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
EVAL_LOG=/tmp/e4_4ep_eval.log
TRAIN_LOG=/tmp/e4_4ep_train.log
PARSED=/tmp/4ep_parsed_results.txt
E4_4EP_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224

echo "=== ④-4ep Results Collection ($(date '+%F %T')) ===" | tee "$PARSED"

# 1. Training final stats
echo "" | tee -a "$PARSED"
echo "=== TRAINING FINAL STATS ===" | tee -a "$PARSED"
grep '④-4ep done' "$TRAIN_LOG" 2>/dev/null | tee -a "$PARSED"
grep '\[done\]' "$TRAIN_LOG" 2>/dev/null | tail -1 | tee -a "$PARSED"
echo "Final checkpoint:" | tee -a "$PARSED"
ls -la "$E4_4EP_OUT/vision.pt" 2>/dev/null | tee -a "$PARSED"
echo "Total checkpoints: $(ls "$E4_4EP_OUT"/vision_step*.pt 2>/dev/null | wc -l)" | tee -a "$PARSED"

# 2. Parse eval results
echo "" | tee -a "$PARSED"
echo "=== EVAL LOG (full) ===" | tee -a "$PARSED"
cat "$EVAL_LOG" 2>/dev/null | tee -a "$PARSED"

# 3. Extract key metrics using Python
echo "" | tee -a "$PARSED"
echo "=== PARSED KEY METRICS ===" | tee -a "$PARSED"
"$PY" -c "
import re, sys

with open('$EVAL_LOG', 'r') as f:
    log = f.read()

# Protocol B results — ONLY match [BRIDGE] B seed=X: lp_top1=0.XXXX (XX.XX%)
# (the mean line has ± in the percentage so it won't match this regex)
protb_results = []
for m in re.finditer(r'\[BRIDGE\]\s+B seed=\d+.*?lp_top1=([0-9.]+)\s*\(([0-9.]+)%\)', log):
    protb_results.append(float(m.group(2)))

# Protocol A results — ONLY match [BRIDGE] A: lp_top1=0.XXXX (XX.XX%)
protA_results = []
for m in re.finditer(r'\[BRIDGE\]\s+A:.*?lp_top1=([0-9.]+)\s*\(([0-9.]+)%\)', log):
    protA_results.append(float(m.group(2)))

# Zero-shot results — match 'top1=XX.XX% top5=XX.XX%'
zs_results = []
for m in re.finditer(r'top1=([0-9.]+)%.*?top5=([0-9.]+)%', log):
    zs_results.append((float(m.group(1)), float(m.group(2))))

# k-NN results — match '[probe] k-NN k=XX: top1=XX.XX%'
knn_results = []
for m in re.finditer(r'k-NN\s+k=(\d+).*?top1=([0-9.]+)%', log):
    knn_results.append((int(m.group(1)), float(m.group(2))))

print('--- Protocol B (3 seeds) ---')
if protb_results:
    for i, v in enumerate(protb_results):
        print(f'  Seed {i}: {v:.2f}%')
    avg = sum(protb_results) / len(protb_results)
    if len(protb_results) > 1:
        import statistics
        std = statistics.stdev(protb_results)
        print(f'  Mean ± σ: {avg:.2f} ± {std:.2f}%')
    else:
        print(f'  Mean: {avg:.2f}%')
else:
    print('  NOT FOUND in eval log')

print('--- Protocol A ---')
if protA_results:
    for v in protA_results:
        print(f'  {v:.2f}%')
else:
    print('  NOT FOUND')

print('--- Zero-shot ---')
if zs_results:
    for top1, top5 in zs_results:
        print(f'  top-1: {top1:.2f}%, top-5: {top5:.2f}%')
else:
    print('  NOT FOUND')

print('--- k-NN ---')
if knn_results:
    for k, acc in knn_results:
        print(f'  k={k}: {acc:.2f}%')
else:
    print('  NOT FOUND')
" 2>&1 | tee -a "$PARSED"

# 4. Update lp-epoch curve
echo "" | tee -a "$PARSED"
echo "=== UPDATING LP-EPOCH CURVE ===" | tee -a "$PARSED"

# Extract ProtB mean for curve — ONLY match per-seed lines (not the mean line with ±)
PROTB_MEAN=$("$PY" -c "
import re
with open('$EVAL_LOG', 'r') as f:
    log = f.read()
protb = []
for m in re.finditer(r'\[BRIDGE\]\s+B seed=\d+.*?lp_top1=([0-9.]+)\s*\(([0-9.]+)%\)', log):
    protb.append(float(m.group(2)))
if protb:
    avg = sum(protb) / len(protb)
    print(f'{avg:.2f}')
else:
    print('NONE')
" 2>/dev/null)

if [ "$PROTB_MEAN" != "NONE" ] && [ -n "$PROTB_MEAN" ]; then
    echo "ProtB mean = $PROTB_MEAN% → updating lp-epoch curve" | tee -a "$PARSED"
    "$PY" plot_lp_epoch_curve.py \
        --e1fair 62.34 --e1fair-err 0.01 \
        --e2ep 65.37 --e2ep-err 0.01 \
        --e4ep "$PROTB_MEAN" --e4ep-err 0.01 \
        --png lp_epoch_curve.png 2>&1 | tee -a "$PARSED"
    echo "lp-epoch curve updated: vision/lp_epoch_curve.png" | tee -a "$PARSED"
else
    echo "⚠️ Could not extract ProtB mean from eval log — curve NOT updated" | tee -a "$PARSED"
fi

echo "" | tee -a "$PARSED"
echo "=== COLLECTION COMPLETE ===" | tee -a "$PARSED"
echo "Results file: $PARSED" | tee -a "$PARSED"
echo "Curve: vision/lp_epoch_curve.png (if updated)" | tee -a "$PARSED"
