# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 249 | TARGET: 12 -->
## RUN_ID 249 — **经 `.12` ssh 到 `.29` 启动 eval-freeze A/B**（RUN_ID 248 未被 `.29` relay 执行：游标仍 247）

> 现象：`.last_run_id.29` 一直停在 247，248（TARGET 29）5 分钟未执行 ⇒ `.29` 的 `ops_relay_v2` 可能已退出/卡住。
> 改法：用 `.12` 的 relay（存活）ssh 到 `.29`，把 A/B 脚本传过去并 `setsid` 后台启动；冻结逻辑不变：**只 SIGSTOP 7 个 `gguf_lmeval_run.py` 600 s**，`trap` 兜底 SIGCONT，不动 llama-server / torchrun / watcher / ckpt。
> 结果文件：`.29:/tmp/baize_eval_freeze_ab29.txt`（约 18 min 后取，见下一 RUN_ID）。

```bash
set -u
echo "=== RUN_ID 249 | dispatch A/B to .29 via ssh from .12 | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
if $SSH 10.239.2.29 'hostname' >/dev/null 2>&1; then
  echo "[ssh .29] OK"
  $SSH 10.239.2.29 'hostname; echo "-- relay proc --"; pgrep -af "ops_relay_v2.sh" | cut -c1-140; echo "-- relay log tail --"; tail -6 /tmp/baize_ops_relay.29.log 2>/dev/null; echo "-- state --"; cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29 2>/dev/null'
  echo
  echo "[deploy freeze script to .29]"
  $SSH 10.239.2.29 'cat > /tmp/baize_eval_freeze_ab29.sh' <<'EOS29'
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
  echo "--- servers alive ---"
  ps -eo pid=,stat=,pcpu= -C llama-server 2>/dev/null | sed 's/^/  /'
  echo "=== DONE $(date '+%F %T') ==="
} >>"$OUT"
EOS29
  $SSH 10.239.2.29 'chmod +x /tmp/baize_eval_freeze_ab29.sh; rm -f /tmp/baize_eval_freeze_ab29.txt; setsid nohup bash /tmp/baize_eval_freeze_ab29.sh >/tmp/baize_eval_freeze_ab29.run.log 2>&1 < /dev/null & echo detached_pid=$!; sleep 8; echo "-- early --"; head -30 /tmp/baize_eval_freeze_ab29.txt 2>/dev/null'
else
  echo "[ssh .29] FAILED (BatchMode/ConnectTimeout)"
  echo "-- .12 relay alive? --"; pgrep -af "ops_relay_v2.sh" | cut -c1-140
fi
echo
echo "=== 249 done; full result ~18 min later in /tmp/baize_eval_freeze_ab29.txt on .29 ==="
```
