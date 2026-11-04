# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 242 | TARGET: 29 -->
## RUN_ID 242 — pretrain 状态刷新（只读）：S1 iter / cline 存活 / llama.cpp 工作区 diff / 残留 server

> 距 RUN_ID 241 已约 2 小时。本块只做“现在几点、到哪一步”，不 kill、不重启、不写文件、不跑 GPU。
> `pgrep -f` 结果截断；不 dump cline 的完整 cmdline（README §8）。

```bash
set -u
echo "=== RUN_ID 242 | pretrain status tick (read-only) | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[1] S1 训练心跳"
grep -aE 'iteration [0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-200
stat -c 'worker.log mtime=%y size=%s' /tmp/baize_s1_baize2b_worker.log 2>/dev/null
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>&1 | head -8
echo
echo "[2] pretrain loop / cline"
LOOP=$(pgrep -f 'baize_pretrain_loop\.sh' | head -1)
echo "loop_pid=${LOOP:-none}"
if [ -n "${LOOP:-}" ]; then
  ps -o pid,etimes,pcpu,rss,args --ppid "$LOOP" --no-headers 2>/dev/null | cut -c1-150 | head -5
fi
CL=$(ps -eo pid,etimes,pcpu,rss,args --no-headers 2>/dev/null | grep 'data-dir /nas_train/app.e0031982/.cline_pretrain' | grep -v grep | awk '{print $1}' | head -1)
echo "cline_pid=${CL:-none}"
[ -n "${CL:-}" ] && ps -o pid,etimes,pcpu,rss --no-headers -p "$CL" 2>/dev/null
echo
echo "[3] llama.cpp 工作区改动（只读）"
cd /nas_train/app.e0031982/code/llama.cpp 2>/dev/null && {
  echo "HEAD=$(git rev-parse --short HEAD) branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "--- changed files (top 15) ---"
  git status --short 2>/dev/null | head -15
  echo "--- diff stat ---"
  git diff --stat 2>/dev/null | tail -6
}
echo
echo "[4] loop 日志尾部 12 行"
tail -12 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo
echo "[5] 残留 llama-server / 最近 GGUF"
echo "server_count=$(pgrep -fc 'llama-server' 2>/dev/null || echo 0)"
ls -lt --time-style='+%m-%d %H:%M' /tmp/*.gguf 2>/dev/null | head -5
echo
echo "[6] 本线最近提交"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && git log -2 --pretty='%h %ad %s' --date=format:'%m-%d %H:%M' -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | cut -c1-160
echo
echo "=== DONE 242 ==="
```
