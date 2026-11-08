# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 248 | TARGET: 29 -->
## RUN_ID 248 — **S1 变慢根因 A/B：`.29` 上冻结 7 个 eval client 10 分钟**（用户直令 2026-11-08 12:2x）

> RUN_ID 247 实测：eval 全在 `.29`（7×llama-server ~670% CPU + 7×gguf_lmeval_run.py），`.29` load 83–95/224；`.12` load 26 且无 eval。
> `Step Time`：12:15 7965.9 ms → 12:16 8154.8 → 12:18 **8804.2 ms**（同时段 load 94→84）。
> 做法：只对 `.29` 的 7 个 `gguf_lmeval_run.py` 发 SIGSTOP（**不 kill、不动 llama-server / torchrun / watcher / ckpt**），600 s 后自动 SIGCONT；`trap` 兜底。
> 若假设成立：client 停 → server 无请求 → ~46 核让出 → Step Time 应明显回落；恢复后再次上升。
> 只读采样：master/worker log 的 `elapsed time per iteration` + `loadavg` + llama-server CPU 总和。零写训练侧。

```bash
set -u
echo "=== RUN_ID 248 | eval-freeze A/B on .29 | $(date '+%F %T') | host=$(hostname) ==="
cat > /tmp/baize_eval_freeze_ab29.sh <<'EOS'
#!/bin/bash
set -u
OUT=/tmp/baize_eval_freeze_ab29.txt
LOG=/tmp/baize_s1_baize2b_master.log
[ -f "$LOG" ] || LOG=/tmp/baize_s1_baize2b_worker.log
step(){ grep -E 'elapsed time per iteration' "$LOG" 2>/dev/null | tail -1 | sed -E 's/^\[([^]]+)\].*iteration +([0-9]+)\/.*\(ms\): ([0-9.]+).*/t=\1 it=\2 ms=\3/'; }
srv_cpu(){ ps -eo pcpu=,args= | awk '/[l]lama-server/ && !/cline/ {s+=$1;n++} END{printf "srv_n=%d srv_cpu=%.0f%%",n,s}'; }
ld(){ cut -d' ' -f1-3 /proc/loadavg; }

CLI=$(ps -eo pid=,args= | awk '/[g]guf_lmeval_run\.py/ && !/awk/ && !/cline/ && !/bun/ {print $1}')
N=$(echo $CLI | wc -w)
echo "clients=$N pids=[$(echo $CLI)] log=$LOG" >>"$OUT"
if [ "$N" -eq 0 ]; then echo "NO_CLIENTS -> abort" >>"$OUT"; exit 0; fi

resume(){ for p in $CLI; do kill -CONT "$p" 2>/dev/null; done; }
trap resume EXIT INT TERM

{
  echo "=== start $(date '+%F %T') host=$(hostname) ==="
  echo "[baseline] $(step)"
  echo "[baseline] load=$(ld) $(srv_cpu)"
  echo "--- last 8 step lines ---"
  grep -E 'elapsed time per iteration' "$LOG" | tail -8 | sed -E 's/^\[([^]]+)\].*iteration +([0-9]+)\/.*\(ms\): ([0-9.]+).*/  t=\1 it=\2 ms=\3/'
  echo "--- client stdout (size before) ---"
  for p in $CLI; do f=$(readlink /proc/$p/fd/1 2>/dev/null); [ -n "$f" ] && echo "  $p -> $f size=$(stat -c %s "$f" 2>/dev/null)"; done
} >>"$OUT"

for p in $CLI; do kill -STOP "$p" 2>/dev/null; done
sleep 20

{
  echo "=== FROZEN $(date '+%F %T') (clients SIGSTOP only) ==="
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
  for p in $CLI; do f=$(readlink /proc/$p/fd/1 2>/dev/null); [ -n "$f" ] && echo "  $p -> $f size=$(stat -c %s "$f" 2>/dev/null)"; done
  echo "--- client state (expect S, not T) ---"
  for p in $CLI; do ps -o pid=,stat=,pcpu=,etimes= -p "$p" 2>/dev/null | sed 's/^/  /'; done
  echo "--- servers still alive ---"
  ps -eo pid=,stat=,pcpu= -C llama-server 2>/dev/null | sed 's/^/  /'
  echo "=== DONE $(date '+%F %T') ==="
} >>"$OUT"
EOS
chmod +x /tmp/baize_eval_freeze_ab29.sh
rm -f /tmp/baize_eval_freeze_ab29.txt
setsid nohup bash /tmp/baize_eval_freeze_ab29.sh >/tmp/baize_eval_freeze_ab29.run.log 2>&1 < /dev/null &
echo "detached_pid=$!"
sleep 8
echo "--- early result ---"
head -40 /tmp/baize_eval_freeze_ab29.txt 2>/dev/null
echo
echo "=== 248 dispatched; full result ~18 min later (RUN_ID 249) ==="
```
