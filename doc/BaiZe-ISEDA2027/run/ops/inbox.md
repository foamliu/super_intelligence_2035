# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 229 | TARGET: 29 -->
## RUN_ID 229 — 定位 S1 重启命令 + 看 pretrain agent 现在在干什么（只读）

```bash
set -u
echo "=== RUN_ID 229 | find S1 launch recipe | $(date '+%F %T') | host=$(hostname) ==="
LLM=/nas_train/app.e0031982/code/baize-llm
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo
echo "[1] baize-llm/scripts 列表"
timeout 10 ls -1t "$LLM/scripts" 2>/dev/null | head -20 | sed 's/^/    /'
timeout 10 ls -1t "$LLM" 2>/dev/null | head -12 | sed 's/^/    /'

echo
echo "[2] 谁引用了 worker 日志名（找启动包装脚本）"
timeout 25 grep -rl 'baize_s1_baize2b' "$LLM" "$R" 2>/dev/null | head -8 | sed 's/^/    /'

echo
echo "[3] 找 s1 启动脚本（可能名）"
timeout 20 ls -1 "$LLM"/scripts/*.sh 2>/dev/null | head -20 | sed 's/^/    /'

echo
echo "[4] train.sh 头部（默认参数/用法）"
if [ -f "$LLM/scripts/train.sh" ]; then
  echo "    ---- head 40 ----"
  timeout 8 sed -n '1,40p' "$LLM/scripts/train.sh" | cut -c1-150 | sed 's/^/    /'
  echo "    ---- 关键行 ----"
  timeout 8 grep -nE 'ITER|ITERS|CONFIG|resume|save|seq|mbs|gbs|GPUS|NODES|master_port' "$LLM/scripts/train.sh" 2>/dev/null | head -18 | cut -c1-140 | sed 's/^/    /'
fi

echo
echo "[5] pretrain agent 此刻在跑什么（CPU smoke / lm_eval）"
timeout 10 ls -lt --time-style='+%F %T' /tmp 2>/dev/null | grep -iE 'cpu_smoke|lmeval' | head -6 | awk '{print "    "$6,$7,$5"B",$8}'
echo "  cpu_smoke_v2.log 尾 8:"
timeout 8 tail -8 /tmp/cpu_smoke_v2.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'
echo "  当前 python 进程（>50% CPU）:"
timeout 10 ps -eo pid,etime,pcpu,rss,cmd --sort=-pcpu 2>/dev/null | awk '$3>50' | head -4 | cut -c1-130 | sed 's/^/    /'

echo
echo "[6] 确认 16 卡仍空（再采一次）"
echo "  .29: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
timeout 15 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=6 10.239.2.12 'echo "  .12: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr "\n" " ")"; echo "  .12 torch=$(ps -eo cmd | grep -cE "[t]orchrun|[p]retrain_launcher")"' 2>&1 | sed 's/^/  /'

echo
echo "=== DONE 229 ==="
```
