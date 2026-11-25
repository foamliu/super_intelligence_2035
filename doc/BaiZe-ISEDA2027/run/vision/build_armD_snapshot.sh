#!/bin/bash
# ==============================================================================
# build_armD_snapshot.sh — build ArmD 6-source training snapshot + pair/steps counts
#
# ArmD = ArmC's 3 sources (GPIC8000 + CC12M + Amshaker) + WebMix-38M + wit_base
#        + InternVL-SA1B.  The snapshot is a plain text file: one absolute tar
#        path per line (same format as ArmC's data_snapshot_20261017_gpic8000.txt),
#        consumed by armB_aimv2_openclip.py --data <file> --data-source mixed.
#
# Outputs (in $VISION_DIR):
#   data_snapshot_20261019_armD.txt   — the snapshot (shard list)
#   armD_pair_count.txt               — total image-text pairs (single integer)
#   armD_steps.txt                    — ceil(3 * total_pairs / 8192)  (3-epoch steps)
#
# Pair counting: ArmC's 3-source count is fixed at 117,305,600 (derived exactly
# from ArmC STEPS=57250 * GBS=8192 / 4 epochs).  InternVL + WebMix + wit pairs
# are COUNTED by streaming `tar -tf | grep -c '\.txt$'` in parallel (each wds
# tar holds one .txt per sample).  This avoids decoding any image.
#
# Precondition: both conversions (webmix38m, wit_base) must be COMPLETE.
#   pgrep -f 'prep_data_armD' should return nothing.
#
# Launch:
#   bash build_armD_snapshot.sh
# ==============================================================================
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
cd "$VISION_DIR"

ARMC_SNAP="data_snapshot_20261017_gpic8000.txt"
ARMD_SNAP="data_snapshot_20261019_armD.txt"
PAIR_FILE="armD_pair_count.txt"
STEPS_FILE="armD_steps.txt"

CONV_ROOT=/nas_user/app.e0031982/datasets/baize-vision/converted_armD
WEBMIX_DIR="$CONV_ROOT/webmix38m"
WIT_DIR="$CONV_ROOT/wit_base"
INTERNVL_DIR=/nas_user/app.e0031982/datasets/hanlincs/InternVL-SA1B-Caption-WebDataset/webdataset

GBS=8192
EPOCHS=3
# ArmC 3-source pairs: STEPS(57250) * GBS(8192) / 4 epochs = 117,305,600 (exact)
ARMC_PAIRS=117305600

echo "===== build_armD_snapshot START $(date '+%F %T') ====="
echo "[armD-snap] ArmC snapshot base: $ARMC_SNAP"

# ---- guard: conversions must be done ----
if pgrep -f 'prep_data_armD' >/dev/null 2>&1; then
    echo "[armD-snap] ERROR: prep_data_armD still running — conversions not done. Aborting."
    exit 1
fi

# ---- 1. ArmC base (11350 shards) ----
if [ ! -f "$ARMC_SNAP" ]; then
    echo "[armD-snap] ERROR: ArmC snapshot $ARMC_SNAP missing."; exit 1
fi
N_ARMC=$(wc -l < "$ARMC_SNAP")
echo "[armD-snap] ArmC shards: $N_ARMC"

# ---- 2. InternVL-SA1B webdataset tars ----
INTERNVL_TARS=$(find "$INTERNVL_DIR" -maxdepth 1 -name 'sa_*.tar' 2>/dev/null | sort)
N_INTERNVL=$(echo "$INTERNVL_TARS" | grep -c . )
echo "[armD-snap] InternVL shards: $N_INTERNVL"
if [ "$N_INTERNVL" -eq 0 ]; then echo "[armD-snap] ERROR: no InternVL tars."; exit 1; fi

# ---- 3. converted WebMix-38M ----
WEBMIX_TARS=$(find "$WEBMIX_DIR" -name 'shard-*.tar' 2>/dev/null | sort)
N_WEBMIX=$(echo "$WEBMIX_TARS" | grep -c . )
echo "[armD-snap] WebMix shards: $N_WEBMIX"
if [ "$N_WEBMIX" -eq 0 ]; then echo "[armD-snap] ERROR: no WebMix converted tars."; exit 1; fi

# ---- 4. converted wit_base ----
WIT_TARS=$(find "$WIT_DIR" -name 'shard-*.tar' 2>/dev/null | sort)
N_WIT=$(echo "$WIT_TARS" | grep -c . )
echo "[armD-snap] wit_base shards: $N_WIT"
if [ "$N_WIT" -eq 0 ]; then echo "[armD-snap] ERROR: no wit converted tars."; exit 1; fi

# ---- 5. assemble snapshot ----
echo "[armD-snap] assembling $ARMD_SNAP ..."
cat "$ARMC_SNAP" > "$ARMD_SNAP"
echo "$INTERNVL_TARS" >> "$ARMD_SNAP"
echo "$WEBMIX_TARS"   >> "$ARMD_SNAP"
echo "$WIT_TARS"      >> "$ARMD_SNAP"
N_TOTAL=$(wc -l < "$ARMD_SNAP")
echo "[armD-snap] total shards: $N_TOTAL  ->  $ARMD_SNAP"

# ---- 6. count pairs (InternVL + WebMix + wit) via parallel tar -tf ----
echo "[armD-snap] counting pairs (InternVL + WebMix + wit) via tar -tf ..."
count_pairs() {
    # $1 = file of tar paths, one per line; prints total .txt member count
    local list="$1"
    # xargs: -P 16 parallel, -n 1 one tar per proc; grep -c per tar; awk sums
    cat "$list" | xargs -P 16 -n 1 -I{} sh -c 'tar -tf "{}" 2>/dev/null | grep -c "\.txt$"' \
        | awk '{s+=$1} END{print s+0}'
}

TMP_LIST=$(mktemp)
{ echo "$INTERNVL_TARS"; echo "$WEBMIX_TARS"; echo "$WIT_TARS"; } > "$TMP_LIST"
COUNTED_PAIRS=$(count_pairs "$TMP_LIST")
rm -f "$TMP_LIST"
echo "[armD-snap] counted InternVL+WebMix+wit pairs: $COUNTED_PAIRS"

TOTAL_PAIRS=$((ARMC_PAIRS + COUNTED_PAIRS))
STEPS=$(awk -v t="$TOTAL_PAIRS" -v g="$GBS" -v e="$EPOCHS" \
    'BEGIN{c = (t*e)/g; print (c==int(c))? int(c) : int(c)+1}')

echo "$TOTAL_PAIRS" > "$PAIR_FILE"
echo "$STEPS"       > "$STEPS_FILE"

echo ""
echo "===== build_armD_snapshot DONE $(date '+%F %T') ====="
echo "  snapshot : $ARMD_SNAP  ($N_TOTAL shards)"
echo "  ArmC pairs (fixed) : $ARMC_PAIRS"
echo "  counted pairs      : $COUNTED_PAIRS   (InternVL $N_INTERNVL + WebMix $N_WEBMIX + wit $N_WIT shards)"
echo "  TOTAL pairs        : $TOTAL_PAIRS"
echo "  epochs             : $EPOCHS"
echo "  GBS                : $GBS"
echo "  STEPS (3-epoch)    : $STEPS   -> written to $STEPS_FILE"
echo "  Next: export ARMD_STEPS=$STEPS; setsid bash run_armD_openclip.sh ..."
