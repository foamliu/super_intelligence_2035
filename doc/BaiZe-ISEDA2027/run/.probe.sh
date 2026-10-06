#!/bin/bash
echo "=== date ==="
date '+%F %T'
echo "=== local procs ==="
pgrep -af 'megatron|torchrun|pretrain_launcher|baize_s5' | head -40
echo "=== remote 29 gpu ==="
ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader' 2>&1 | head -40
echo "=== remote 29 smi ==="
ssh 10.239.2.29 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader' 2>&1 | head -20