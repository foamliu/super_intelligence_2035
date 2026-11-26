#!/usr/bin/env bash
# Cleanup all step_532000 eval processes on .29
pkill -f 'python.*lm_eval.*step532000' 2>/dev/null || true
pkill -f 'python.*lm_eval.*step_532000' 2>/dev/null || true
sleep 3
N=$(ps -eo args= | grep lm_eval | grep -v grep | wc -l)
echo "remaining_lm_eval_procs=$N"
nvidia-smi --query-gpu=index,memory.used --format=csv
