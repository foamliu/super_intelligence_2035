# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 246 | TARGET: 12 -->
## RUN_ID 246 — **训练变慢根因 A/B：冻结 eval client 10 分钟**（用户直令 2026-11-08 12:0x）

> 背景：S1 `Step Time` 从 6.93–7.04 s（11-06，eval 未启动）升到 7.9 s（11-08 11:42，eval 7 server+7 client 运行中）。
> 假设：CPU eval 与训练 node_rank=0 共置 `.12`，同步 DP 被最慢 rank 拖住。
> 做法：**只 SIGSTOP 7 个 `gguf_lmeval_run.py` 客户端**（不 kill、不动 llama-server / torchrun / watcher / ckpt），冻结 **600 s** 后自动 SIGCONT；脚本带 `trap`，异常退出也必恢复。
> 预期：client 停 → server 无请求 → 机器 CPU/内存带宽让出 → `Step Time` 回到 ~7.0 s；恢复后回到 7.9 s。
> 护栏：只匹配 `gguf_lmeval_run.py` 且排除 `cline|bun`（见 ops/README §8 硬教训 1）；不写任何训练侧文件。

```bash
set -u
echo "=== RUN_ID 246 | eval-freeze A/B | $(date '+%F %T') | host=$(hostname) ==="
cat > /tmp/baize_eval_freeze_ab.sh <<'EOS'
#!/bin/bash
set -u
OUT=/tmp/baize_eval_freeze_ab.txt
LOG=""
for f in /tmp/baize_s1_baize2b_master.log /tmp/baize_s1_baize2b_worker.log; do
  if [ -f "$f" ]; then LOG="$f"; break; fi
done
step(){ grep -E 'elapsed time per iteration' "$LOG" 2>/dev/null | tail -1 | sed 's/^ *//'; }
srv_cpu(){ ps -eo pcpu=,args= | awk '/[l]lama-server/ && !/cline/ {s+=$1;n++} END{printf "srv_n=%d srv_cpu=%.0f%%",n,s}'; }
ld(){ cut -d' ' -f1-3 /proc/loadavg; }

CLI=$(ps -eo pid=,args= | awk '/gguf_lmeval_run\.py/ && !/awk/ && !/cline/ && !/bun/ {print $1}')
echo "clients=$(echo $CLI | wc -w) pids=[$(echo $CLI)]" >>"$OUT"

resume(){ for p in $CLI; do kill -CONT "$p" 2>/dev/null; done; }
trap resume EXIT INT TERM

{
  echo "=== start $(date '+%F %T') host=$(hostname) log=$LOG ==="
  echo "[baseline] $(step)"
  echo "[baseline] load=$(ld) $(srv_cpu)"
  echo "--- last 8 step lines ---"
  grep -E 'elapsed time per iteration' "$LOG" | tail -8 | sed 's/^ *//'
  echo "--- client stdout (size before) ---"
  for p in $CLI; do f=$(readlink /proc/$p/fd/1 2>/dev/null); [ -n "$f" ] && echo "$p -> $f size=$(stat -c %s "$f" 2>/dev/null)"; done
} >>"$OUT"

for p in $CLI; do kill -STOP "$p" 2>/dev/null; done
sleep 20

{
  echo "=== FROZEN $(date '+%F %T') (clients SIGSTOP only; servers/training untouched) ==="
  for i in 0 1 2 3 4 5 6 7 8 9 10; do
    echo "[f${i} $(date '+%H:%M:%S')] $(step) | load=$(ld) | $(srv_cpu)"
    [ "$i" -lt 10 ] && sleep 60
  done
} >>"$OUT"

resume
trap - EXIT INT TERM
sleep 5

{
  echo "=== RESUMED $(date '+%F %T') ==="
  for i in 0 1 2 3 4 5; do
    echo "[r${i} $(date '+%H:%M:%S')] $(step) | load=$(ld) | $(srv_cpu)"
    [ "$i" -lt 5 ] && sleep 60
  done
  echo "--- client stdout (size after) ---"
  for p in $CLI; do f=$(readlink /proc/$p/fd/1 2>/dev/null); [ -n "$f" ] && echo "$p -> $f size=$(stat -c %s "$f" 2>/dev/null)"; done
  echo "--- client state (expect S/R, not T) ---"
  for p in $CLI; do ps -o pid=,stat=,pcpu=,etimes= -p "$p" 2>/dev/null; done
  echo "=== DONE $(date '+%F %T') ==="
} >>"$OUT"
EOS
chmod +x /tmp/baize_eval_freeze_ab.sh
rm -f /tmp/baize_eval_freeze_ab.txt
setsid nohup bash /tmp/baize_eval_freeze_ab.sh >/tmp/baize_eval_freeze_ab.run.log 2>&1 < /dev/null &
echo "detached_pid=$!"
sleep 8
echo "--- early result ---"
head -40 /tmp/baize_eval_freeze_ab.txt 2>/dev/null
echo
echo "=== 246 dispatched; result completes ~17 min later (see RUN_ID 247) ==="
```
