# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 245 | TARGET: 29 -->
## RUN_ID 245 — **杀掉卡死的 pretrain cline 会话**（用户直令 · 仅 kill 该进程，不动 loop/评测/训练）

> 用户原话（2026-11-05 22:4x）：「pretrain 那个 cline 会话 杀掉吧，时间太久不正常」
> 依据：PID 3640274 已连续运行 **~2h53m**（21:13/22:09 两次探针均为 99.9% CPU、97 线程），日志认知停在「5/10、60k in progress」，实际已 8/10。
> **护栏**：只按 `--data-dir /nas_train/app.e0031982/.cline_pretrain` 精确定位；先 `TERM`，4 s 不退再 `KILL`；🚫 不碰 loop(3165013) / pipeline(3543961) / llama-server / torchrun / S1。

```bash
set -u
echo "=== RUN_ID 245 | kill wedged pretrain cline | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[1] 定位目标（只认 .cline_pretrain data-dir）"
CL=$(ps -eo pid,etimes,pcpu,rss,args --no-headers 2>/dev/null \
     | grep -F 'data-dir /nas_train/app.e0031982/.cline_pretrain' | grep -v grep | awk '{print $1}' | head -1)
echo "target_cline_pid=${CL:-none}"
if [ -z "${CL:-}" ]; then
  echo "NOT_FOUND: 目标已不在（可能已自行退出）——不执行 kill"
else
  ps -o pid,etimes,pcpu,rss,nlwp,args --no-headers -p "$CL" 2>/dev/null | cut -c1-220
  echo "--- TERM ---"
  kill -TERM "$CL" 2>&1 || echo "TERM_FAILED(rc=$?)"
  sleep 4
  if kill -0 "$CL" 2>/dev/null; then
    echo "still alive after TERM -> KILL"
    kill -KILL "$CL" 2>&1 || echo "KILL_FAILED(rc=$?)"
    sleep 3
  fi
  if kill -0 "$CL" 2>/dev/null; then echo "RESULT=STILL_ALIVE"; else echo "RESULT=KILLED_OK"; fi
fi
echo
echo "[2] 复核：cline_pretrain 是否已无残留"
pgrep -af 'data-dir /nas_train/app.e0031982/.cline_pretrain' 2>/dev/null | cut -c1-180 || echo "(none)"
echo
echo "[3] 护栏：loop / pipeline / llama-server / torchrun 必须仍在"
echo "loop:";     pgrep -af 'baize_pretrain_loop\.sh' 2>/dev/null | head -2 | cut -c1-120
echo "pipeline:"; pgrep -af 'baize_eval_60k_100k_pipeline' 2>/dev/null | head -1 | cut -c1-120
echo "server:";   pgrep -af 'llama-server' 2>/dev/null | head -2 | cut -c1-150
echo "train:";    pgrep -af 'scripts/train\.sh s1' 2>/dev/null | head -1 | cut -c1-120
echo
echo "[4] 杀掉后 10 s：loop 是否已继续（会提交/或重开会话）"
sleep 10
tail -12 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-180
echo "--- cline_pretrain now ---"
pgrep -af 'data-dir /nas_train/app.e0031982/.cline_pretrain' 2>/dev/null | cut -c1-120 || echo "(none: 等 loop 下一轮唤醒)"
echo
echo "[5] 当前评测进度快照（确认 kill 未影响落盘）"
R=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
for it in 60000 70000 80000 90000; do
  f=$R/gguf_iter_${it}_fixed_8set/results.json
  if [ -f "$f" ]; then stat -c "iter_$it results.json mtime=%y" "$f"; else echo "iter_$it results.json MISSING"; fi
done
pgrep -af 'llama-server' 2>/dev/null | head -1 | grep -o 'bz2b-[0-9]*-f16.gguf' || true
echo
echo "=== DONE 245 ==="
```
