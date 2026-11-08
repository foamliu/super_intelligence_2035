# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 250 | TARGET: 12 -->
## RUN_ID 250 — **部署事后解析器（pre / FROZEN / post 三段 Step Time 均值）**，约 13 min 后出结果

> RUN_ID 249 已在 `.29` 启动冻结：12:23:46 起 600 s（clients=7，baseline load=98.37，srv_cpu=4665%）。
> 249 的采样脚本 `step()` 正则没吃前导空格 → 采样里 ms 为空；但训练日志保留每步时间戳，本命令部署一个 detached 解析器，`sleep 800` 后按时间桶统计。
> 只读：`grep` 日志 + `cat` 结果文件。零写训练侧。

```bash
set -u
echo "=== RUN_ID 250 | deploy post-hoc analyzer to .29 | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'cat > /tmp/baize_ab_analyze.sh' <<'EOS30'
#!/bin/bash
set -u
sleep 800
OUT=/tmp/baize_ab_analyze.txt
LOG=/tmp/baize_s1_baize2b_master.log
[ -f "$LOG" ] || LOG=/tmp/baize_s1_baize2b_worker.log
{
echo "=== analyze $(date '+%F %T') host=$(hostname) log=$LOG ==="
echo "--- freeze sampler file ---"
cat /tmp/baize_eval_freeze_ab29.txt 2>/dev/null
echo
echo "--- step-time buckets (from log) ---"
grep -E 'elapsed time per iteration' "$LOG" | tail -500 | awk '
{
  ts=$0; sub(/^[ \t]*\[/,"",ts); sub(/\].*/,"",ts);
  hh=substr(ts,12,8);
  it=""; if (match($0, /iteration +[0-9]+\//)) { it=substr($0,RSTART,RLENGTH); gsub(/[^0-9]/,"",it) }
  ms=""; if (match($0, /\(ms\): [0-9.]+/)) { ms=substr($0,RSTART+6,RLENGTH-6) }
  if (ms=="") next;
  tag="other";
  if (hh>="12:12:00" && hh<"12:23:40") tag="pre";
  else if (hh>="12:24:00" && hh<="12:33:40") tag="FROZEN";
  else if (hh>="12:34:00") tag="post";
  if (tag!="other") { n[tag]++; s[tag]+=ms; if (!(tag in mn) || ms<mn[tag]) mn[tag]=ms; if (ms>mx[tag]) mx[tag]=ms; last[tag]=ms }
}
END{
  split("pre FROZEN post",ord," ");
  for(i=1;i<=3;i++){ t=ord[i]; if(n[t]>0) printf "%-7s n=%3d mean=%.1f ms min=%.1f max=%.1f last=%.1f\n", t, n[t], s[t]/n[t], mn[t], mx[t], last[t]; else printf "%-7s n=0\n", t }
}'
echo
echo "--- last 14 step lines ---"
grep -E 'elapsed time per iteration' "$LOG" | tail -14 | sed -E 's/^[[:space:]]*\[([^]]+)\].*iteration +([0-9]+)\/.*\(ms\): ([0-9.]+).*/  t=\1 it=\2 ms=\3/'
echo "=== END ==="
} > "$OUT" 2>&1
EOS30
$SSH 10.239.2.29 'chmod +x /tmp/baize_ab_analyze.sh; rm -f /tmp/baize_ab_analyze.txt; setsid nohup bash /tmp/baize_ab_analyze.sh >/dev/null 2>&1 < /dev/null & echo analyzer_pid=$!'
echo
echo "[interim] freeze sampler tail:"
$SSH 10.239.2.29 'tail -14 /tmp/baize_eval_freeze_ab29.txt 2>/dev/null'
echo
echo "=== 250 done; result in /tmp/baize_ab_analyze.txt on .29 after ~13 min (RUN_ID 251) ==="
```
