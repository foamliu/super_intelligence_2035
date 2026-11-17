# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 279 | TARGET: 29 -->
## RUN_ID 279 — **处置：杀掉卡死的 pretrain cline（用户直令·第一步）**

> 依据 RUN_ID 278：`.29` 上 `baize_pretrain_loop.sh`(3165013) 活着，其子进程
> `cline --data-dir .cline_pretrain`(2054633) 已 `R` 状态 100% CPU 空转 9h+、sessions 自 12:57 零写入。
> 本块动作（用户已批准）：
> ① 前置核对：cmdline 必含 `.cline_pretrain`、ppid 必为 3165013、loop 必活 —— **任一不满足即 ABORT，不 kill**；
> ② 抢救 loop 日志（fd1 指向已删除的 `/tmp/baize_pretrain_loop.log`）；
> ③ `kill -TERM` → 等 10s → 仍活则 `kill -KILL`（**只此一个 PID**）；
> ④ 校验 loop 未受影响；等 ≤120s 观察 loop 是否自动起新 cline；
> ⑤ 抽查训练（GPU / torchrun worker 数）未受影响。
> 🚫 不碰 3165013 / 3165005 / 训练 torchrun / 其他线 cline。

```bash
set -u
echo "=== RUN_ID 279 | pretrain hung-cline kill (AUTHORIZED) | $(date '+%F %T') | host=$(hostname) ==="
LPID=3165013
CPID=2054633
LOGDIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/logs

echo
echo "[0] 前置核对（任一不满足 → ABORT，不做任何 kill）"
cmd="$(tr '\0' ' ' < /proc/$CPID/cmdline 2>/dev/null || true)"
ppid="$(ps -o ppid= -p $CPID 2>/dev/null | tr -d ' ')"
echo "  cpid=$CPID ppid=${ppid:-none}"
echo "  cmdline=${cmd:0:220}"
ok=1
case "$cmd" in *'.cline_pretrain'*) ;; *) echo "  ABORT: cmdline 不含 .cline_pretrain"; ok=0;; esac
[ "${ppid:-0}" = "$LPID" ] || { echo "  ABORT: ppid=${ppid:-none} != loop $LPID"; ok=0; }
kill -0 $LPID 2>/dev/null || { echo "  ABORT: loop $LPID 不在"; ok=0; }
[ "$ok" = "1" ] || { echo "=== ABORTED (no kill) 279 ==="; exit 0; }

echo
echo "[1] kill 前证据"
ps -o pid,ppid,etime,stat,pcpu,rss,args -p $CPID | cut -c1-150
awk '{print "  utime_ticks=" $14 " stime_ticks=" $15 " state=" $3}' /proc/$CPID/stat 2>/dev/null
stat -c '  .cline_pretrain/sessions mtime=%y' /nas_train/app.e0031982/.cline_pretrain/sessions 2>/dev/null || true

echo
echo "[2] 抢救 loop 日志（fd 指向已删除文件）"
mkdir -p "$LOGDIR"
SALV="$LOGDIR/pretrain_loop_salvage_$(date '+%Y%m%d_%H%M%S').log"
if [ -r /proc/$LPID/fd/1 ]; then
  timeout 20 cat /proc/$LPID/fd/1 > "$SALV" 2>/dev/null; rc=$?
  echo "  salvage rc=$rc size=$(stat -c %s "$SALV" 2>/dev/null || echo 0)"
  echo "  path=$SALV"
  tail -n 12 "$SALV" 2>/dev/null | cut -c1-170 | sed 's/^/  | /'
else
  echo "  /proc/$LPID/fd/1 不可读，跳过抢救"
fi

echo
echo "[3] kill：TERM → 10s → KILL"
kill -TERM $CPID 2>/dev/null && echo "  TERM sent @ $(date '+%T')" || echo "  TERM failed"
gone=0
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if ! kill -0 $CPID 2>/dev/null; then echo "  已退出（TERM 生效，用时 ${i}s）"; gone=1; break; fi
done
if [ "$gone" = "0" ]; then
  echo "  10s 未退 → KILL"
  kill -KILL $CPID 2>/dev/null
  sleep 2
  if kill -0 $CPID 2>/dev/null; then echo "  ⚠️ STILL ALIVE（需人工）"; else echo "  已退出（KILL 生效）"; fi
fi

echo
echo "[4] 校验 loop 未受影响"
ps -o pid,ppid,etime,stat,args -p $LPID | cut -c1-140
echo "  loop_alive=$(kill -0 $LPID 2>/dev/null && echo yes || echo no)"

echo
echo "[5] 等 loop 下一轮（push + sleep 60s + 新 cline），最多 120s"
NEW=""
for i in $(seq 1 24); do
  sleep 5
  NEW="$(ps -eo pid,ppid,etime,args 2>/dev/null | grep -F '.cline_pretrain' | grep -v grep | grep -vE "^ *${CPID} " | head -2 | cut -c1-140)"
  if [ -n "$NEW" ]; then echo "  @+$((i*5))s 检测到新 cline:"; echo "$NEW" | sed 's/^/    /'; break; fi
done
[ -z "$NEW" ] && echo "  120s 内未见新 cline（loop 可能仍在 push/sleep，稍后自然恢复；不影响训练）"

echo
echo "[6] 当前 .cline_pretrain 下的 cline"
ps -eo pid,ppid,etime,stat,pcpu,args 2>/dev/null | grep -F '.cline_pretrain' | grep -v grep | cut -c1-150

echo
echo "[7] 训练未受影响抽查"
nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader 2>/dev/null | head -8 | sed 's/^/  /'
echo "  torchrun(4177347) workers=$(ps -eo ppid= 2>/dev/null | awk '$1==4177347' | wc -l)"
echo
echo "=== DONE 279 ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 278 | TARGET: 29 -->
## RUN_ID 278 — **pretrain loop / cline 深探（只读）**：fd 实指日志、进程状态、会话写入、训练进度

> 承 RUN_ID 277（结论：`.29` 上 loop PID 3165013 与训练 torchrun 都活着，GPU 8×100%；
> 但 `cline --data-dir .cline_pretrain` PID 2054633 已跑 **9h07m / 100% CPU** ⇒ 疑似卡死）。
> 本块只读：不 kill、不重启；读 `/proc` 与文件 mtime，确定 **loop 日志真实路径** 与 **cline 是否在空转**。

```bash
set -u
echo "=== RUN_ID 278 | pretrain loop/cline deep probe (READ-ONLY) | $(date '+%F %T') | host=$(hostname) ==="
hostname -I 2>/dev/null | awk '{print "  local IPs: "$0}'
LPID=3165013
CPID=2054633

echo
echo "[1] loop 进程与 fd（日志真实去向）"
ps -o pid,ppid,etime,stat,pcpu,args -p $LPID 2>/dev/null | cut -c1-200
echo "  fd1 -> $(readlink /proc/$LPID/fd/1 2>/dev/null || echo '?')"
echo "  fd2 -> $(readlink /proc/$LPID/fd/2 2>/dev/null || echo '?')"

echo
echo "[2] 相关进程（loop / 其父 / cline）"
ps -eo pid,ppid,etime,stat,pcpu,rss,args 2>/dev/null | grep -E "^ *(3165013|3165004|3165005|$CPID) " | cut -c1-200

echo
echo "[3] cline $CPID 状态"
awk '{print "  state=" $3 "  utime_ticks=" $14 "  stime_ticks=" $15 "  threads=" $20}' /proc/$CPID/stat 2>/dev/null || echo "  (no /proc/$CPID/stat)"
echo "  wchan=$(cat /proc/$CPID/wchan 2>/dev/null)"
grep -E '^(State|Threads|VmRSS|voluntary_ctxt_switches|nonvoluntary_ctxt_switches)' /proc/$CPID/status 2>/dev/null | sed 's/^/  /'

echo
echo "[4] loop 日志尾部（按 fd 实指路径）"
for f in "$(readlink /proc/$LPID/fd/1 2>/dev/null)" "$(readlink /proc/$LPID/fd/2 2>/dev/null)"; do
  case "$f" in
    /*) if [ -f "$f" ]; then
          stat -c '  mtime=%y size=%s path=%n' "$f"
          echo "  silence_sec=$(( $(date +%s) - $(stat -c %Y "$f") ))"
          tail -n 25 "$f" | cut -c1-180 | sed 's/^/  | /'
        else echo "  $f 不存在（fd 指向已删除文件？）"; fi ;;
  esac
done

echo
echo "[5] cline 会话目录最新写入（判断是否真的在产出）"
ls -lt /nas_train/app.e0031982/.cline_pretrain 2>/dev/null | head -6 | cut -c1-160
echo "  -- 最近 3h 内有写入的文件（最多 8 条）--"
find /nas_train/app.e0031982/.cline_pretrain -maxdepth 3 -type f -mmin -180 2>/dev/null | head -8

echo
echo "[6] 训练侧进度取样"
ls -dt /nas_train/app.e0031982/*/checkpoints/iter_* 2>/dev/null | head -3
ls -dt /nas_train/app.e0031982/*/*/checkpoints/iter_* 2>/dev/null | head -3
echo "  -- torchrun 子进程数（8 worker 应在）--"
ps -eo ppid=,pid=,etime=,args= 2>/dev/null | awk '$1==4177347' | wc -l

echo
echo "[7] 判活汇总"
echo "  loop_alive=$(kill -0 $LPID 2>/dev/null && echo yes || echo no)  cline_alive=$(kill -0 $CPID 2>/dev/null && echo yes || echo no)"
echo "=== DONE 278 ==="
```


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
