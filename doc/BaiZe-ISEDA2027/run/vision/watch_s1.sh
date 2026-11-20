#!/bin/bash
# Background watcher: poll S1 until all 4 architectures finish, then emit a summary.
OUT=/nas_train/app.e0031982/datasets/baize-vision/out
SUMR=/tmp/s1_summary.txt
while true; do
    done_cnt=$(grep -c 'done (exit' /tmp/s1_main.log 2>/dev/null)
    if [ "$done_cnt" -ge 4 ]; then
        : > "$SUMR"
        for t in openvision2 mambaeye moevie deepencoder_v2; do
            lg="$OUT/S1_$t/train.log"
            if [ -f "$lg" ]; then
                last=$(grep 'step 1000/1000' "$lg" | tail -1)
                done_line=$(grep '^\[done\]' "$lg" | tail -1)
                echo "$t | $last | $done_line" >> "$SUMR"
            fi
        done
        echo "ALL_DONE" >> "$SUMR"
        exit 0
    fi
    sleep 30
done