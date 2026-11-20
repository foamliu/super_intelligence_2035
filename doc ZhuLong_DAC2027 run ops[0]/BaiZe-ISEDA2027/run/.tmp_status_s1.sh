#!/bin/bash
# Diagnostic: check S1-01 training status on 10.239.2.29
echo "=== date ==="
date '+%F %T'
echo "=== s1_01 log tail (loss/iter) ==="
ssh 10.239.2.29 'tail -n 60 /tmp/baize_s1_01.log 2>/dev/null | grep -E "iteration|loss|consumed|ETA|lm loss|grad norm" | tail -n 20'
echo "=== s1_01 log bottom 8 lines ==="
ssh 10.239.2.29 'tail -n 8 /tmp/baize_s1_01.log 2>/dev/null'
echo "=== nvidia-smi compute apps ==="
ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null'
echo "=== pgrep pretrain/torchrun ==="
ssh 10.239.2.29 'pgrep -af "pretrain_launcher|torchrun" 2>/dev/null'