# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 227 | TARGET: 29 -->
## RUN_ID 227 — S1 死亡取证（只读）：OOM? 谁杀的? 重启脚本在哪?

```bash
set -u
echo "=== RUN_ID 227 | S1 post-mortem (read-only) | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027

echo
echo "[1] 内存与 OOM 证据"
free -g | sed 's/^/    /'
echo "  dmesg OOM/kill (last 10):"
timeout 15 dmesg -T 2>/dev/null | grep -iE 'out of memory|oom-kill|killed process' | tail -10 | cut -c1-160 | sed 's/^/    /' || echo "    dmesg 不可读"
echo "  journal OOM (last 8):"
timeout 15 journalctl -k --since '2026-11-02 18:00' 2>/dev/null | grep -iE 'oom|killed process' | tail -8 | cut -c1-160 | sed 's/^/    /' || echo "    journal 不可读"

echo
echo "[2] S1 master/worker 日志尾（死亡现场）"
ls -l --time-style='+%F %T' /tmp/baize_s1_baize2b_master.log /tmp/baize_s1_baize2b_worker.log 2>/dev/null | awk '{print "    "$6,$7,$5"B",$8}'
echo "  master tail 12:"
timeout 10 tail -12 /tmp/baize_s1_baize2b_master.log 2>/dev/null | cut -c1-170 | sed 's/^/    /'
echo "  worker tail 6:"
timeout 10 tail -6 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-170 | sed 's/^/    /'

echo
echo "[3] 谁在 18:39 动过（.29 上 18:30-19:00 的用户进程线索）"
timeout 10 ls -lt --time-style='+%F %T' /tmp 2>/dev/null | grep -E '18:3[0-9]|18:4[0-9]' | head -8 | awk '{print "    "$6,$7,$5,$8}' || true

echo
echo "[4] S1 启动脚本候选（run/ 下）"
timeout 10 ls -1t "$R" 2>/dev/null | grep -iE '^s1|baize.*s1|s1.*\.sh|launch' | head -10 | sed 's/^/    /'
echo "  *.sh 列表(含 s1 关键字):"
timeout 10 ls -1 "$R"/*.sh 2>/dev/null | grep -iE 's1|launch|train' | head -10 | sed 's/^/    /'

echo
echo "[5] 该脚本尾部（看默认参数）"
for f in "$R"/s1_*.sh "$R"/baize_s1*.sh; do
  [ -f "$f" ] || continue
  echo "  ---- $f ($(stat -c %s "$f")B, mtime=$(stat -c %y "$f" | cut -c1-19)) ----"
  timeout 5 tail -12 "$f" | cut -c1-140 | sed 's/^/    /'
done

echo
echo "[6] checkpoints 最新 & 训练 sh 是否记录了 resume"
timeout 10 cat "$BASE/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt" 2>/dev/null | sed 's/^/    latest_iter=/'
timeout 10 ls -1t "$BASE/nemo_experiments/baize2b/checkpoints" 2>/dev/null | head -4 | sed 's/^/    /'

echo
echo "[7] 在飞的 cline 会话（hung 6h）是否还在耗 CPU"
timeout 10 ps -o pid,etime,pcpu,rss,stat -p 1587337 2>/dev/null | sed 's/^/    /' || echo "    pid1587337 已不在"

echo
echo "[8] loop 日志尾（是否记录卡住/重试）"
timeout 10 tail -8 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-170 | sed 's/^/    /'

echo
echo "=== DONE 227 ==="
```
