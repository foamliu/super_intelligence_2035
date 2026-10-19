#!/bin/bash
# ==============================================================================
# run_armD_launch_when_ready.sh — top-level ArmD auto-launch watcher.
#
# Waits for the two prep_data_armD conversions (webmix38m + wit_base) to finish,
# builds the 6-source snapshot, counts pairs, computes 3-epoch steps, runs a CPU
# decode smoke test on 3 random shards, then launches:
#   1. run_armD_openclip.sh   (training, with ARMD_STEPS exported)
#   2. run_armD_full_chain.sh (waits for training, then ProtB->MLLM->12bench)
#
# All on .12, setsid so it survives shell exit. Logs to /tmp/armD_launch.log.
#
# Launch (on .12, in a login shell so PATH has cline/conda):
#   setsid bash -lc 'exec bash /nas_train/.../vision/run_armD_launch_when_ready.sh' \
#       > /tmp/armD_launch.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
cd "$VISION_DIR"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/armD_launch.log
echo "===== ArmD launch-when-ready START $(date '+%F %T') =====" | tee "$LOG"
# ============================================================
# STEP 1: wait for conversions to finish
# ============================================================
echo "[$(date '+%H:%M:%S')] Waiting for prep_data_armD conversions to finish..." | tee -a "$LOG"
while pgrep -f 'prep_data_armD' >/dev/null 2>&1; do
    W=$(tail -1 /tmp/armD_convert_webmix.log 2>/dev/null | tr -d '\r')
    T=$(tail -1 /tmp/armD_convert_wit.log 2>/dev/null | tr -d '\r')
    echo "[$(date '+%H:%M:%S')] still converting. webmix: $W | wit: $T" | tee -a "$LOG"
    sleep 120
done
echo "[$(date '+%H:%M:%S')] All prep_data_armD processes exited." | tee -a "$LOG"
# sanity: check conversion logs for errors / completion
echo "[$(date '+%H:%M:%S')] webmix convert tail:" | tee -a "$LOG"; tail -3 /tmp/armD_convert_webmix.log 2>&1 | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] wit convert tail:" | tee -a "$LOG"; tail -3 /tmp/armD_convert_wit.log 2>&1 | tee -a "$LOG"
# ============================================================
# STEP 2: build snapshot + count pairs + compute steps
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] Building ArmD 6-source snapshot..." | tee -a "$LOG"
bash build_armD_snapshot.sh 2>&1 | tee -a "$LOG"
if [ ! -f armD_steps.txt ] || [ ! -f data_snapshot_20261019_armD.txt ]; then
    echo "[$(date '+%H:%M:%S')] ERROR: snapshot/steps not produced. Aborting." | tee -a "$LOG"; exit 1
fi
ARMD_STEPS=$(cat armD_steps.txt)
TOTAL_PAIRS=$(cat armD_pair_count.txt)
echo "[$(date '+%H:%M:%S')] ARMD_STEPS=$ARMD_STEPS  TOTAL_PAIRS=$TOTAL_PAIRS" | tee -a "$LOG"
# ============================================================
# STEP 3: CPU decode smoke test on 3 random shards from the snapshot
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] CPU decode smoke test (3 random shards)..." | tee -a "$LOG"
"$PY" - <<'PYEOF' 2>&1 | tee -a "$LOG"
import random, sys, tarfile, io
from PIL import Image
snap="data_snapshot_20261019_armD.txt"
paths=[l.strip() for l in open(snap) if l.strip()]
random.seed(1234); picks=random.sample(paths, 3)
ok=True
for p in picks:
    try:
        tf=tarfile.open(p, 'r')
        names=tf.getnames()
        txts=[n for n in names if n.endswith('.txt')]
        imgs=[n for n in names if n.endswith(('.jpg','.png','.img','.jpeg'))]
        # decode first image + first caption
        if imgs and txts:
            im=Image.open(io.BytesIO(tf.extractfile(imgs[0]).read())).convert('RGB')
            cap=tf.extractfile(txts[0]).read().decode('utf-8','ignore')[:80]
            print(f"OK {p.split('/')[-1]}: {len(names)} members, {len(txts)} txt, {len(imgs)} img, img={im.size}, cap='{cap}'")
        else:
            print(f"WARN {p}: txts={len(txts)} imgs={len(imgs)}"); ok=False
        tf.close()
    except Exception as e:
        print(f"FAIL {p}: {e}"); ok=False
sys.exit(0 if ok else 1)
PYEOF
if [ $? -ne 0 ]; then echo "[$(date '+%H:%M:%S')] ERROR: smoke test failed. NOT launching training." | tee -a "$LOG"; exit 1; fi
echo "[$(date '+%H:%M:%S')] Smoke test passed." | tee -a "$LOG"
# ============================================================
# STEP 4: launch training (ARMD_STEPS exported)
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] Launching run_armD_openclip.sh (ARMD_STEPS=$ARMD_STEPS)..." | tee -a "$LOG"
export ARMD_STEPS
setsid bash run_armD_openclip.sh > /tmp/armD_openclip_train.log 2>&1 < /dev/null &
TRAIN_PID=$!
echo "[$(date '+%H:%M:%S')] training launched PID=$TRAIN_PID" | tee -a "$LOG"
# wait for training to actually start (log grows / process alive / Step appears)
sleep 90
echo "[$(date '+%H:%M:%S')] training log head after 90s:" | tee -a "$LOG"; head -20 /tmp/armD_openclip_train.log 2>&1 | tee -a "$LOG"
if ! pgrep -f 'armB_aimv2_openclip.py.*armD_20261019' >/dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] WARNING: training process not detected after 90s. Check /tmp/armD_openclip_train.log" | tee -a "$LOG"
fi
# ============================================================
# STEP 5: launch full chain (it waits for training internally)
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] Launching run_armD_full_chain.sh (waits for training, then ProtB->MLLM->12bench)..." | tee -a "$LOG"
setsid bash run_armD_full_chain.sh > /tmp/armD_full_chain.log 2>&1 < /dev/null &
CHAIN_PID=$!
echo "[$(date '+%H:%M:%S')] full chain launched PID=$CHAIN_PID" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "===== ArmD launch-when-ready DISPATCHED $(date '+%F %T') =====" | tee -a "$LOG"
echo "  training PID : $TRAIN_PID  -> /tmp/armD_openclip_train.log" | tee -a "$LOG"
echo "  chain    PID : $CHAIN_PID  -> /tmp/armD_full_chain.log" | tee -a "$LOG"
echo "  ARMD_STEPS=$ARMD_STEPS  TOTAL_PAIRS=$TOTAL_PAIRS  (3 epochs, GBS=8192)" | tee -a "$LOG"
echo "  Variables: data 3src->6src + epoch 4->3 + lr 1e-3->2e-3 + min_lr 1e-5->2e-5 (FOUR vars)" | tee -a "$LOG"
echo "  Next (agent): report <=30min after training start; later wake does report+EXPERIMENTS+MEMORY." | tee -a "$LOG"
exit 0
