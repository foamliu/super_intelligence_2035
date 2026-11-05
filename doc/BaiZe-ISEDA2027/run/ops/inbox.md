# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 243 | TARGET: 29 -->
## RUN_ID 243 — **pretrain 是否活着**（只读巡检）：loop / cline / S1 / 60k–100k 评测管线 / results 落盘

> 背景：pretrain 线自 19:49（#1418，60k eval 85.8%、ETA 20:03）后再无任何提交，已停摆 ~80 min；同期其它线正常。
> 本块**只读**：不 kill、不重启、不写工作区、不跑 GPU、不碰训练。
> `ps`/`pgrep` 输出截断到 200 字符；不 dump cline 完整 cmdline（README §8）。

```bash
set -u
echo "=== RUN_ID 243 | pretrain alive probe (read-only) | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[1] 关键进程一览（pretrain / eval / cline）"
ps -eo pid,ppid,etimes,pcpu,rss,args --no-headers 2>/dev/null \
  | grep -E 'baize_pretrain_loop|baize_eval_60k_100k|train\.sh|torchrun|llama-server|gguf_lmeval|cline' \
  | grep -v grep | cut -c1-200 | head -20
echo
echo "[2] pretrain loop"
LOOP=$(pgrep -f 'baize_pretrain_loop\.sh' | head -1)
echo "loop_pid=${LOOP:-none}"
if [ -n "${LOOP:-}" ]; then
  ps -o pid,etimes,pcpu,rss,args --no-headers -p "$LOOP" 2>/dev/null | cut -c1-160
  echo "--- children ---"
  ps -o pid,etimes,pcpu,rss,args --no-headers --ppid "$LOOP" 2>/dev/null | cut -c1-160 | head -8
fi
echo
echo "[3] cline 会话（pretrain data-dir）"
CL=$(ps -eo pid,etimes,pcpu,rss,args --no-headers 2>/dev/null \
     | grep -F 'data-dir /nas_train/app.e0031982/.cline_pretrain' | grep -v grep | awk '{print $1}' | head -1)
echo "cline_pid=${CL:-none}"
[ -n "${CL:-}" ] && ps -o pid,etimes,pcpu,rss --no-headers -p "$CL" 2>/dev/null
echo
echo "[4] S1 训练"
pgrep -af 'train\.sh s1' 2>/dev/null | head -3 | cut -c1-160
grep -aE 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-200
stat -c 'worker.log mtime=%y size=%s' /tmp/baize_s1_baize2b_worker.log 2>/dev/null
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>&1 | head -8
echo
echo "[5] 60k-100k 评测管线"
PIPE=$(pgrep -f 'baize_eval_60k_100k_pipeline' | head -1)
echo "pipeline_pid=${PIPE:-none}"
pgrep -af 'llama-server' 2>/dev/null | head -3 | cut -c1-160
pgrep -af 'gguf_lmeval_run\.py' 2>/dev/null | head -3 | cut -c1-160
echo "--- /tmp 日志 mtime（判活）---"
ls -l --time-style='+%m-%d %H:%M' /tmp/baize_eval_60k_100k*.log /tmp/baize_server_*.log /tmp/baize_pretrain_loop.log 2>/dev/null | tail -8
echo "--- 最新 server 日志尾 6 行 ---"
ls -t /tmp/baize_server_*.log 2>/dev/null | head -1 | xargs -r tail -6 2>/dev/null | cut -c1-180
echo
echo "[6] results.json 落盘（>=60k）"
R=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
for it in 60000 70000 80000 90000 100000; do
  f=$R/gguf_iter_${it}_fixed_8set/results.json
  if [ -f "$f" ]; then stat -c "iter_$it results.json mtime=%y size=%s" "$f"; else echo "iter_$it results.json MISSING"; fi
done
echo
echo "[7] GGUF / HF ckpt 最新"
ls -1dt /nas_train/app.e0031982/models/baize2b_gguf/*.gguf 2>/dev/null | head -8 | while read -r g; do ls -l --time-style='+%m-%d %H:%M' "$g" | awk '{print $5, $6, $7, $8}'; done
ls -1d /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_* 2>/dev/null | sort -V | tail -3
echo
echo "[8] .29 克隆内 pretrain 线最近提交"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && {
  git log -3 --pretty='%h %ad %s' --date=format:'%m-%d %H:%M' -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | cut -c1-160
  echo "clone_HEAD=$(git rev-parse --short HEAD)"
}
echo
echo "[9] pretrain loop 日志尾 10 行"
tail -10 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo
echo "=== DONE 243 ==="
```
