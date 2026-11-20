# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 282 | TARGET: both -->
## RUN_ID 282 — **pretrain / harness 存活体检（只读 · 2026-11-20 10:0x）**：两线心跳自 01:13 / 01:22 起静默 ~8.5h

> **背景（运维侧已核对 origin，不必重查）**：
> `run/MEMORY_PRETRAIN_2B.md` 最后一次提交 = **#2708 @ 11-20 01:22**；`run/MEMORY_HARNESS.md` 最后一次提交 = **R2801 @ 11-20 01:13**。
> 此后 8.5 小时内这两条线**零提交**，而同期 designflow（43 次）/ zhulong（32 次）/ data（R28→R35）/ vision 都有提交 ⇒ 怀疑 `.29` 上两个 loop 已死、或 push 被卡住（与 posttrain loop 2026-11-17 14:07 静默死亡同一模式：末尾停在 cline `[abort]`）。
> `run/ops/outbox.md` 的最后一条结果是 RUN_ID 281（执行于 **2026-11-17 22:39**），之后再无输出 ⇒ **中继自身是否还活着也一并上报**。
>
> **只读**：只看进程 / 日志 / git 状态，**不 kill、不重启、不改任何文件、不删锁**。
> **投递口径**：TARGET = both —— `.29` 直接自检；`.12` 收到后用 `ssh .29` 代为采集（同样只读），两份结果都留在 outbox 里可交叉验证。
> 历史 RUN_ID ≤ 281 的命令原文已被本块覆盖，执行结果仍完整保存在 `outbox.md`。

```bash
set -u
BODY='
set -u
H=$(hostname)
echo "host=$H  date=$(date "+%F %T")"
echo "uptime: $(uptime | sed "s/^ *//")"
echo "load1/5/15: $(cut -d" " -f1-3 /proc/loadavg 2>/dev/null)"
echo
echo "[1] loop 进程（已排除 cline 误匹配：loop 把整份任务书当参数传给 cline，-f 会假阳性）"
for pat in baize_pretrain_loop.sh baize_harness_loop.sh baize_posttrain_loop.sh baize_data_loop.sh baize_vision_loop.sh; do
  L=$(ps -eo pid,ppid,etime,pcpu,stat,args | grep -F -- "$pat" | grep -v -e grep -e cline -e ops_relay -e "bash -c" | cut -c1-150)
  if [ -n "$L" ]; then echo "  [$pat] 命中:"; echo "$L" | sed "s/^/    /"; else echo "  [$pat] 无"; fi
done
echo
echo "[2] cline 进程（计数 + 明细）"
echo "  count=$(ps -eo args | grep -F -- "cline" | grep -vc -e grep -e ops_relay)"
ps -eo pid,ppid,etime,pcpu,args | grep -F -- "cline" | grep -v -e grep -e ops_relay | cut -c1-120 | head -6 | sed "s/^/  /"
echo
echo "[3] 日志 mtime / size（判定 loop 最后活动时间）"
for f in /tmp/baize_pretrain_loop.log /tmp/pretrain_loop.log /tmp/baize_harness_loop.log /tmp/harness_loop.log /tmp/baize_posttrain_loop.log /tmp/baize_ops_relay.29.log /tmp/baize_ops_relay.12.log; do
  [ -f "$f" ] && stat -c "  %y  %8s  %n" "$f"
done
ls -t /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/logs/*.log 2>/dev/null | head -4 | while read -r f; do stat -c "  %y  %8s  %n" "$f"; done
echo
echo "[4] pretrain loop 日志尾 12 行"
f=$(ls -t /tmp/baize_pretrain_loop.log /tmp/pretrain_loop*.log 2>/dev/null | head -1)
if [ -n "${f:-}" ] && [ -f "$f" ]; then
  echo "  file=$f  lines=$(wc -l < "$f")"
  tail -n 12 "$f" | sed "s/\x1b\[[0-9;]*m//g" | cut -c1-170 | sed "s/^/    | /"
else echo "  未找到 pretrain loop 日志"; fi
echo
echo "[5] harness loop 日志尾 12 行"
f=$(ls -t /tmp/baize_harness_loop.log /tmp/harness_loop*.log 2>/dev/null | head -1)
if [ -n "${f:-}" ] && [ -f "$f" ]; then
  echo "  file=$f  lines=$(wc -l < "$f")"
  tail -n 12 "$f" | sed "s/\x1b\[[0-9;]*m//g" | cut -c1-170 | sed "s/^/    | /"
else echo "  未找到 harness loop 日志"; fi
echo
echo "[6] 两条 loop 的失效模式计数 + 最后 loop/push 行"
for f in /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log; do
  [ -f "$f" ] || continue
  echo "  $f"
  for p in "push FAILED" "pull --rebase FAILED" "push deferred" "index.lock" "TASK_MD missing" "no available LLM" "abort"; do
    printf "    %-22s %s\n" "$p" "$(grep -a -c -- "$p" "$f" 2>/dev/null)"
  done
  grep -a -E "^\[loop\]|^\[push\]" "$f" | tail -3 | sed "s/\x1b\[[0-9;]*m//g" | cut -c1-165 | sed "s/^/      last| /"
done
echo
echo "[7] GPU / 训练进程（pretrain 是否还在训）"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | sed "s/^/  /"
echo "  torchrun=$(ps -eo args | grep -F torchrun | grep -vc -e grep)  pretrain_gpt=$(ps -eo args | grep -F "pretrain_gpt" | grep -vc -e grep)"
ps -eo pid,etime,pcpu,args | grep -F "pretrain_gpt" | grep -v grep | cut -c1-130 | head -2 | sed "s/^/  /"
echo
echo "[8] 系统资源 / 磁盘"
free -g 2>/dev/null | sed -n "1,2p" | sed "s/^/  /"
df -h /nas_train /nas_data 2>/dev/null | sed "s/^/  /"
echo
echo "[9] 共享副本 git（只读）"
if cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && [ -d .git ]; then
  echo "  HEAD=$(git rev-parse --short HEAD 2>/dev/null)  $(git log -1 --date=iso --format="%ad %s" 2>/dev/null | cut -c1-110)"
  echo "  left-right(origin...HEAD)=$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null | tr "\t" " ")"
  echo "  staged=$(git diff --cached --name-only 2>/dev/null | wc -l) unstaged=$(git diff --name-only 2>/dev/null | wc -l) untracked=$(git ls-files -o --exclude-standard 2>/dev/null | wc -l)"
  [ -f .git/index.lock ] && stat -c "  LOCK %y %s %n" .git/index.lock
  git log -1 --date=iso --format="  last_pretrain_commit=%ad %h" -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md 2>/dev/null
  git log -1 --date=iso --format="  last_harness_commit=%ad %h" -- doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md 2>/dev/null
else echo "  共享副本不可达"; fi
echo
echo "[10] 中继自身"
ps -eo pid,etime,args | grep "[o]ps_relay" | cut -c1-120 | head -3 | sed "s/^/  /"
tail -n 4 /tmp/baize_ops_relay.29.log 2>/dev/null | cut -c1-150 | sed "s/^/  relay29| /"
echo
echo "（以上全部只读；未 kill / 未重启 / 未改文件）"
'
TAG=$(hostname | sed -n "s/.*\([0-9][0-9]\)$/\1/p")
echo
if [ "${TAG:-}" = "29" ]; then
  echo "[0] 本机 = .29，直接体检"
  eval "$BODY"
else
  echo "[0] 本机 = ${TAG:-?}（非 .29）→ ssh 10.239.2.29 只读代采"
  echo "$BODY" | timeout 180 ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no 10.239.2.29 "bash -s" 2>&1 | sed "s/^/  /"
fi
echo
echo "=== DONE 282 | $(date "+%F %T") ==="
```
