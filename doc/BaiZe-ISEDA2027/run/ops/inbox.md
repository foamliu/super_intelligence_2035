# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 226 | TARGET: 29 -->
## RUN_ID 226 — pretrain 体检 v2（只读；上轮被 cline 长命令行撑爆输出，本轮全部截断）

```bash
set -u
echo "=== RUN_ID 226 | pretrain check v2 | $(date '+%F %T') | host=$(hostname) ==="
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027

echo
echo "[1] pretrain loop (bash, anchored) + 在飞的 cline 会话"
timeout 10 ps -eo pid,etime,rss,cmd --sort=-etime 2>/dev/null | grep -E '[b]aize_pretrain_loop\.sh$' | cut -c1-90 | head -3 || echo "  no loop"
echo "  cline sessions:"
timeout 10 ps -eo pid,etime,rss,cmd 2>/dev/null | grep '[.]cline_pretrain' | grep -v grep | awk '{print "    pid="$1" etime="$2" rss="$3"KB"}' | head -4 || echo "    none"

echo
echo "[2] S1 training (torchrun/launcher, truncated)"
timeout 10 ps -eo pid,etime,rss,cmd 2>/dev/null | grep -E '[p]retrain_launcher|[t]orchrun' | cut -c1-110 | head -4 || echo "  NO torchrun"

echo "[3] S1 log mtime + tail"
ls -l --time-style='+%F %T' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | awk '{print "  "$6,$7,$5"B"}'
timeout 10 tail -3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[4] GPU (.29)"
timeout 12 nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | tr '\n' ' ' | cut -c1-300

echo
echo "[5] CPU / eval procs (.29)"
echo "  nproc=$(nproc) load=$(cut -d' ' -f1-3 /proc/loadavg)"
timeout 8 vmstat 1 2 2>/dev/null | tail -1 | awk '{print "  us%="$13" sy%="$14" id%="$15}'
timeout 10 ps -eo pid,etime,%cpu,cmd 2>/dev/null | grep -E '[l]m_eval|[e]xport_hf|[p]6_lmeval|[c]onvert_mcore' | cut -c1-120 | head -5 || echo "  no eval/export proc"

echo
echo "[6] hf_iter_* (name + mtime only)"
timeout 20 find "$BASE" -maxdepth 3 -name 'hf_iter_*' -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null | sort | tail -8 | sed 's/^/    /'

echo
echo "[7] checkpoints latest 5"
timeout 12 ls -1t "$BASE/nemo_experiments/baize2b/checkpoints" 2>/dev/null | head -5 | sed 's/^/    /'

echo
echo "[8] lm_eval_results latest 5 + new json(4h) count"
timeout 12 ls -1t "$BASE/nemo_experiments/baize2b/lm_eval_results" 2>/dev/null | head -5 | sed 's/^/    /'
echo "    new_json_4h=$(timeout 20 find "$BASE/nemo_experiments/baize2b/lm_eval_results" -maxdepth 2 -name '*.json' -mmin -240 2>/dev/null | wc -l)"

echo
echo "[9] BASE 近 3h 改动文件数 + 最新 5 个"
echo "    count_3h=$(timeout 25 find "$BASE" -maxdepth 3 -type f -mmin -180 2>/dev/null | wc -l)"
timeout 25 find "$BASE" -maxdepth 3 -type f -mmin -180 -printf '%TH:%TM %p\n' 2>/dev/null | sort | tail -5 | sed 's/^/    /'

echo
echo "[10] .12 probe"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 'echo "  host=$(hostname) load=$(cut -d" " -f1-3 /proc/loadavg)"; echo "  loop=$(ps -eo cmd | grep -cE "[b]aize_pretrain_loop\.sh$")"; echo "  eval=$(ps -eo cmd | grep -cE "[l]m_eval|[e]xport_hf")"; nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null | tr "\n" " " | cut -c1-120' 2>&1 | sed 's/^/    /' || echo "    ssh .12 failed"

echo
echo "=== DONE 226 ==="
```
