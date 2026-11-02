# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 236 | TARGET: 29 -->
## RUN_ID 236 — 杀掉卡了 6h+ 的 pretrain cline 会话（用户直令），并确保 loop 与 S1 不受影响

> 用户直令：「6h 会话杀掉吧，必然不健康」。只杀该 cline 会话及其子进程，**绝不碰 S1 训练 / loop 本体**。

```bash
set -u
echo "=== RUN_ID 236 | kill stale cline session | $(date '+%F %T') | host=$(hostname) ==="
PID=1587337

echo
echo "[0] 目标确认（必须先核对 cmdline 含 .cline_pretrain）"
CMD=$(ps -o cmd= -p "$PID" 2>/dev/null | cut -c1-120)
echo "    pid=$PID  etime=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')  cmd=$CMD"
case "$CMD" in
  *cline*) ;;
  *) echo "    ❌ cmdline 不像 cline，安全中止，不做任何 kill"; exit 0 ;;
esac

echo
echo "[1] 子进程树（先看会连带杀谁）"
for c in $(timeout 8 ps -eo pid,ppid 2>/dev/null | awk -v p="$PID" '$2==p{print $1}'); do
  echo "    child $c: $(ps -o etime=,cmd= -p $c 2>/dev/null | cut -c1-110)"
done

echo
echo "[2] SIGTERM 该会话 + 子进程"
for c in $(timeout 8 ps -eo pid,ppid 2>/dev/null | awk -v p="$PID" '$2==p{print $1}'); do kill -TERM "$c" 2>/dev/null || true; done
kill -TERM "$PID" 2>/dev/null || true
sleep 6

echo
echo "[3] 残留检查 → SIGKILL 兜底"
if ps -p "$PID" >/dev/null 2>&1; then
  echo "    仍存活，SIGKILL"
  for c in $(timeout 8 ps -eo pid,ppid 2>/dev/null | awk -v p="$PID" '$2==p{print $1}'); do kill -KILL "$c" 2>/dev/null || true; done
  kill -KILL "$PID" 2>/dev/null || true
  sleep 2
fi
echo "    pid $PID 状态: $(ps -p "$PID" >/dev/null 2>&1 && echo '仍存在 ❌' || echo '已退出 ✅')"
echo "    仍指向 .cline_pretrain 的 cline 进程数=$(ps -eo cmd 2>/dev/null | grep -c '[.]cline_pretrain')"

echo
echo "[4] loop 本体必须还活着"
echo "    loop: $(timeout 8 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[b]aize_pretrain_loop\.sh$' | cut -c1-100)"
echo "    loop log 尾 5:"
timeout 8 tail -5 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[5] S1 训练必须不受影响"
echo "    train.sh: $(timeout 8 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]rain\.sh s1' | cut -c1-100)"
timeout 10 grep -E 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-170 | sed 's/^/    /'
echo "    .29 GPU: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr '\n' ' ')"

echo
echo "[6] 收尾：确认没有遗留 python 冒烟"
timeout 10 ps -eo pid,etime,pcpu,cmd 2>/dev/null | grep -E 'python[^ ]* .*(lm_eval|cpu_smoke|test_lmeval)' | grep -v grep | cut -c1-110 | sed 's/^/    /' || true

echo "=== DONE 236 ==="
```
