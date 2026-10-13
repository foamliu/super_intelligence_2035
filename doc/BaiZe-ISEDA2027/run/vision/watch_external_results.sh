#!/bin/bash
# Wait for all 5 external_protb_results_*.json files, then generate report
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
MODELS="clip-vitl14-336 siglip2-so400m-384 aimv2-1B-336 openvision2-vitl14-336 rice-vitl14-560"
LOG=/tmp/external_protb_watcher.log
echo "[$(date '+%H:%M:%S')] Watcher started, waiting for results..." > $LOG
while true; do
    COUNT=0
    for m in $MODELS; do
        if [ -f "external_protb_results_${m}.json" ]; then
            COUNT=$((COUNT+1))
        fi
    done
    echo "[$(date '+%H:%M:%S')] Found $COUNT/5 result files" >> $LOG
    if [ "$COUNT" -eq 5 ]; then
        echo "[$(date '+%H:%M:%S')] All 5 results found! Generating report..." >> $LOG
        export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
        python generate_external_protb_report.py >> $LOG 2>&1
        echo "[$(date '+%H:%M:%S')] Report generation done." >> $LOG
        break
    fi
    sleep 60
done
