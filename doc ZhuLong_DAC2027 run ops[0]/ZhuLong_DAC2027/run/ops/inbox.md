# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 147 -->
## RUN_ID 147 — **zhulong agent 怎么了？（只读诊断：进程 / 日志 / 17:09 那轮评测进度 / 工作副本）**

> 背景：`zhulong eval` 轮1（doubao-pro，batch `run_batch_20261120_170940`）**17:09 起跑**，
> 当时 ETA 2–3h；但仓库最后一次 zhulong 提交停在 **11-20 17:13**，到 22:5x 仍无回填 ⇒ 需判断
> 是「还在跑」「卡住」还是「loop/cline 掉了」。
>
> **本块只读**：不 pull、不改文件、不 kill、不重启、不碰评测目录内容。全部命令有界。

```bash
set -u
echo "=== RUN_ID 147 | zhulong agent health (READ-ONLY) | $(date '+%F %T') | host=$(hostname) ==="

echo
echo "[1] 进程总览：zhulong loop / relay / cline / node"
ps -eo pid,ppid,etime,stat,pcpu,rss,args 2>/dev/null | grep -E 'zhulong_loop|zhulong_ops_relay' | grep -v grep | cut -c1-150
echo "-- cline --"
ps -eo pid,ppid,etime,stat,pcpu,rss,args 2>/dev/null | grep -E 'bin/cline|/cline ' | grep -v grep | head -10 | cut -c1-190
echo "cline 进程数=$(pgrep -f 'bin/cline' 2>/dev/null | wc -l)  node 进程数=$(pgrep -x node 2>/dev/null | wc -l)"

echo
echo "[2] D 状态 / 卡死进程"
echo "DSTATE=$(ps -eo stat= 2>/dev/null | cut -c1 | grep -c D)"
ps -eo pid,etime,stat,pcpu,args 2>/dev/null | awk 'NR>1 && $3 ~ /^D/ {print}' | head -5 | cut -c1-160

echo
echo "[3] 日志尾"
for f in /tmp/zhulong_loop.log /tmp/zhulong_ops_relay.log; do
  echo "--- $f"
  ls -l "$f" 2>/dev/null || echo "  (无此文件)"
  timeout 10 tail -n 8 "$f" 2>/dev/null | cut -c1-200
done

echo
echo "[4] 17:09 那轮评测：目录 + 进度"
REPO=/nasdata/app.e0031982/code/EDA-Flow-Bench
if [ -d "$REPO" ]; then cd "$REPO" || true; else echo "  (无 $REPO，尝试 eda_fastmcp)"; cd /nasdata/app.e0031982/code/eda_fastmcp 2>/dev/null || true; fi
pwd
ls -d eval/run_batch_20261120_17* 2>/dev/null
for B in $(ls -d eval/run_batch_20261120_17* 2>/dev/null | head -3); do
  echo "--- $B"
  ls -l "$B" 2>/dev/null | head -6
  if [ -f "$B/status.jsonl" ]; then
    echo "  status.jsonl 行数=$(wc -l < "$B/status.jsonl")"
    echo "  末 3 行:"; timeout 10 tail -n 3 "$B/status.jsonl" | cut -c1-200
  fi
  [ -f "$B/summary.json" ] && { echo "  summary.json:"; timeout 10 head -c 600 "$B/summary.json"; echo; }
done

echo
echo "[5] 最近评测日志（在跑的那份）"
L=$(ls -t eval/run_20261120_17*.log 2>/dev/null | head -1)
if [ -n "${L:-}" ]; then
  ls -l "$L"; echo "  末 12 行:"; timeout 10 tail -n 12 "$L" | cut -c1-200
  echo "  error 关键词计数:"
  for k in cline-not-found quota 401 connection refused rate-limit fuse traceback; do
    printf '    %-16s %s\n' "$k" "$(timeout 20 grep -ic "$k" "$L" 2>/dev/null)"
  done
else
  echo "  (没找到 eval/run_20261120_17*.log)"
fi

echo
echo "[6] 机器负载 / 磁盘"
cat /proc/loadavg
df -h /nasdata /home 2>/dev/null | tail -3
free -g 2>/dev/null | head -2

echo
echo "[7] 工作副本新鲜度（zhulong 线）"
for GR in /nasdata/app.e0031982/code/super_intelligence_2035; do
  [ -d "$GR/.git" ] || { echo "  (无 $GR)"; continue; }
  cd "$GR" || continue
  echo "  HEAD=$(git log -1 --pretty='%h %ad %s' --date=format:'%F %T' | cut -c1-110)"
  echo "  vs origin: $(git rev-list --left-right --count origin/main...HEAD 2>/dev/null | awk '{print "behind="$1" ahead="$2"}')"
  echo "  TASK 最近提交: $(git log -1 --pretty='%h %ad %s' --date=format:'%F %T' -- doc/ZhuLong_DAC2027/run/ZHULONG_TASK.md | cut -c1-110)"
done

echo
echo "（只读：未 pull / 未 kill / 未改文件 / 未碰评测目录内容）"
echo "=== DONE 147 ==="
```
