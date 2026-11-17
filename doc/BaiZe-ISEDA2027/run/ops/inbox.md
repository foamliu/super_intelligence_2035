# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 277 | TARGET: both -->
## RUN_ID 277 — **pretrain agent loop 存活体检（只读）**：loop 进程 / 日志静默 / cline 卡死 / 训练与 GPU

> 背景：`MEMORY_PRETRAIN_2B.md` 心跳停在 11-17 10:06（#2428），此后 ~12h 无 `pretrain:` 提交，
> 而该 loop 正常节律是 `WAITING:0` → 60s 一轮。需要判定是 **loop 真死** / **cline 卡死** / **训练挂了**。
> 本块**只读**：不 kill、不重启、不起跑、不改任何文件；只有 /tmp 下写一个临时探测脚本并删除。
> 判据（人工据此下结论）：
> ① `.29` 上 `baize_xmodel25_decay_v2`/torchrun 还在、GPU 有占用、train.log 仍在增长 ⇒ 训练没死，只是 agent 不推进；
> ② `.12` 上 `baize_pretrain_loop.sh` 不在 ⇒ **loop 进程已死**（10-23 曾出现 29h 同款停摆）；
> ③ loop 在、但 `silence_sec` 很大且日志尾部停在 `invoking cline` ⇒ **cline 单轮卡死**（超 25min 上限仍不返回）。

```bash
set -u
echo "=== RUN_ID 277 | pretrain loop liveness (READ-ONLY) | $(date '+%F %T') | host=$(hostname) ==="
hostname -I 2>/dev/null | sed 's/^/  local IPs: /'

GR=/nas_train/app.e0031982/code/super_intelligence_2035
[ -d "$GR/.git" ] || GR="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
echo
echo "[A] 共享仓库侧最后活动"
git -C "$GR" log -5 --date=format:'%F %T' --pretty='  %ad %h %s' -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md 2>/dev/null | cut -c1-150
stat -c '  MEMORY mtime=%y size=%s' "$GR/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md" 2>/dev/null || true
echo "  now=$(date '+%F %T')"

cat > /tmp/pretrain_probe_$$.sh <<'EOS'
#!/bin/bash
set -u
echo "  host=$(hostname) ip=$(hostname -I 2>/dev/null | awk '{print $1}') now=$(date '+%F %T')"
echo "  --- [1] pretrain watchdog loop ---"
ps -eo pid,ppid,etime,pcpu,args 2>/dev/null | grep -F 'baize_pretrain_loop.sh' | grep -v grep | grep -viE 'cline|bun|node' | cut -c1-180
echo "  --- [2] loop log ---"
if [ -f /tmp/baize_pretrain_loop.log ]; then
  stat -c '      mtime=%y size=%s' /tmp/baize_pretrain_loop.log
  echo "      silence_sec=$(( $(date +%s) - $(stat -c %Y /tmp/baize_pretrain_loop.log) ))"
  tail -n 8 /tmp/baize_pretrain_loop.log | cut -c1-170 | sed 's/^/      | /'
else echo "      (no /tmp/baize_pretrain_loop.log)"; fi
echo "  --- [3] cline/bun ---"
ps -eo pid,etime,pcpu,args 2>/dev/null | grep -E 'cline|bun' | grep -v grep | cut -c1-140 | head -5
echo "  --- [4] train proc ---"
ps -eo pid,etime,pcpu,args 2>/dev/null | grep -E 'baize_xmodel25_decay_v2|torchrun' | grep -v grep | cut -c1-180 | head -6
echo "  --- [5] train log ---"
if [ -f /tmp/baize_xmodel25_decay_v2_train.log ]; then
  stat -c '      mtime=%y size=%s' /tmp/baize_xmodel25_decay_v2_train.log
  echo "      silence_sec=$(( $(date +%s) - $(stat -c %Y /tmp/baize_xmodel25_decay_v2_train.log) ))"
  tail -n 4 /tmp/baize_xmodel25_decay_v2_train.log | cut -c1-170 | sed 's/^/      | /'
else echo "      (no train log)"; fi
echo "  --- [6] GPU ---"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader 2>/dev/null | sed 's/^/      /'
echo "  --- [7] local relays / loops ---"
ps -eo pid,etime,args 2>/dev/null | grep -E 'ops_relay|baize_(pretrain|vision|data|harness|posttrain)_loop\.sh|watch_.*_loop\.sh' | grep -v grep | grep -viE 'cline|bun' | cut -c1-150 | head -10
EOS
P=/tmp/pretrain_probe_$$.sh

echo
echo "[B] 本机"
bash "$P"
for H in 10.239.2.29 10.239.2.12; do
  echo
  echo "[C] ssh $H"
  timeout 25 ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$H" 'bash -s' < "$P" 2>&1 | sed 's/^/  /'
  echo "  (ssh exit=${PIPESTATUS[0]})"
done
rm -f "$P"
echo
echo "=== DONE 277 ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 276 | TARGET: 12 -->
## RUN_ID 276 — **取 chunk2/3 当前已评估计数与速率**（只读）

```bash
set -u
echo "=== RUN_ID 276 | c2/c3 progress | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
for n in chunk2_restart chunk3_numa_fix; do
  f=/tmp/baize_eval_v5/logs/client_hellaswag_${n}.log
  echo "== $n =="
  [ -f "$f" ] && tr "\r" "\n" < "$f" | grep -E "^gguf-ll:" | tail -2 | cut -c1-120 | sed "s/^/  /"
  stat -c "  mtime=%y size=%s" "$f" 2>/dev/null
done
echo "-- etimes --"; ps -o pid=,etimes=,pcpu= -p 2097234,2097251 2>/dev/null
echo "-- c2/c3 server cpu --"; ps -o pid=,pcpu=,psr= -p 2083722,2083724 2>/dev/null'
echo
echo "=== 276 done ==="
```
