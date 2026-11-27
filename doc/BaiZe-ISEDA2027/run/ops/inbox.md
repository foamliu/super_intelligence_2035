# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 292 -->
## RUN_ID 292 — **🔴 立刻停止 S1 训练（2026-11-28 09:3x · 用户令）**

> **用户原话**：「让 pretrain 立刻把 S1 训练停下」
> **目标**：`.29` + `.12` 两节点的 S1 训练全部停下，**不要重启 S1**。
> **顺序**：先确认 ckpt 安全 → 记录停止前状态 → 停 daemon（避免 restart）→ 停训练 → 记录杀掉的 PID。
> **注意**：`.29` 与 `.12` 共享 NFS 工作副本，本命令**在任一中继执行**，会对另一节点做 bounded ssh。
> **不要动**：别的线进程、GPU0-3 上的 root 服务、文件。

```bash
set -u
R=/nas_train/app.e0031982/code/super_intelligence_2035
H=$(hostname)
echo "[0] exec_host=$H  date=$(date '+%F %T')"
echo

echo "== A. 停止前：真实训练进度与 ckpt 安全 =="
tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-210
CK=$(cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)
echo "latest_ckpt_iter=$CK"
ls -d /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0${CK} 2>/dev/null && echo "ckpt_dir_exists=YES"
echo "ckpt_disk=$(du -sh /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0${CK} 2>/dev/null | awk '{print $1}')"
echo "ckpt_mtime=$(stat -c '%y' /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)"
echo

echo "== B. 停止前：训练进程清单（两节点）=="
echo "-- .29 --"
ps -eo pid,etime,args | grep -E '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun' | cut -c1-160
echo "-- .12 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "ps -eo pid,etime,args | grep -E '[p]retrain_launcher|[t]orchrun' | cut -c1-160" 2>&1 | sed 's/^/  .12| /'
echo

echo "== C. 先杀 eval daemon（防止它把训练重新拉起）=="
for p in $(ps -eo pid,args= | grep 'baize_l1_autoqueue_continuous' | grep -v grep | awk '{print $1}'); do
  echo "  kill daemon PID=$p"; kill "$p" 2>/dev/null; sleep 2; kill -9 "$p" 2>/dev/null
done
pgrep -f 'llama-server' 2>/dev/null | xargs -r kill 2>/dev/null
echo "  daemon cleaned"
echo

echo "== D. 停 .29 训练 =="
for p in $(ps -eo pid,args= | grep -E 'train\.sh s1' | grep -v grep | awk '{print $1}'); do
  echo "  kill train.sh PID=$p"; kill "$p" 2>/dev/null
done
sleep 6
for p in $(ps -eo pid,args= | grep -E 'train\.sh s1' | grep -v grep | awk '{print $1}'); do
  echo "  kill -9 train.sh PID=$p"; kill -9 "$p" 2>/dev/null
done
sleep 4
for p in $(ps -eo pid,args= | grep -E '[p]retrain_launcher\.py|[t]orchrun' | grep -v grep | awk '{print $1}'); do
  echo "  kill -9 local PID=$p"; kill -9 "$p" 2>/dev/null
done
echo

echo "== E. 停 .12 训练 =="
timeout 90 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 '
  for p in $(ps -eo pid,args= | grep -E "[p]retrain_launcher|[t]orchrun" | awk "{print \$1}"); do
    echo "  .12 kill -9 PID=$p"; kill -9 "$p" 2>/dev/null
  done
  sleep 3
  echo "  .12 remaining=$(ps -eo args= | grep -cE "[p]retrain_launcher|[t]orchrun")"
' 2>&1 | sed 's/^/  .12| /'
echo

echo "== F. 停止后核验 =="
sleep 8
echo "-- .29 残留进程 --"
ps -eo pid,etime,args | grep -E '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun' | cut -c1-160 || echo "  (none)"
echo "  .29_still_running=$(ps -eo args= | grep -cE '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun')"
echo "-- .12 残留进程 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "ps -eo args= | grep -cE '[p]retrain_launcher|[t]orchrun'" 2>&1 | sed 's/^/  .12_count=/'
echo
echo "-- GPU（确认已释放，给 S2 切换让路）--"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null
echo "-- .12 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "nvidia-smi --query-gpu=index,memory.used --format=csv,noheader" 2>&1 | sed 's/^/  .12| /'
echo

echo "== G. 确认没有 self-restart =="
sleep 10
echo "  .29_after10s=$(ps -eo args= | grep -cE '[t]rain\.sh s1|[p]retrain_launcher')"
echo "  (0 = 已停稳，未被自动拉起)"
echo
echo "（未重启 S1 · 未动别线 · 未改配置）"
echo "=== DONE 292 | $(date '+%F %T') ==="
```

## RUN_ID 291 — **pretrain / data 静默体检（只读 · 2026-11-24 22:4x）**

> 背景：pretrain 自 **19:17**、data 自 **19:57** 起无新提交（静默 2.5–3.2h，常态 10–20min/条），
> 怀疑 ① loop 已死 ② `git push` 失败（.12 的 github 需要代理 92.23）③ `.git/index` 损坏 / `index.lock` 残留 ④ NFS D-state。
> 另：`.29` 与 `.12` 共享同一 NFS 工作副本，**本令不设 TARGET（任一中继可执行）；命令可能落在任一台**；本块会打印 `exec_host` 并对另一台做 bounded ssh。
> **只读**：不 kill / 不重启 / 不改配置 / 不删文件。

```bash
set -u
echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo
echo "== A. 本机基础 =="
uptime
free -g | awk '/Mem:/{print "mem_used="$3"G / "$2"G"}'
df -h /home /nas_train 2>/dev/null | tail -3
echo "DSTATE=$(ps -eo stat= | cut -c1 | grep -c D)"
echo
echo "== B. 进程（pretrain / data / relay / loop）=="
ps -eo pid,ppid,etime,stat,pcpu,rss,args | grep -E 'baize_|torchrun|pretrain_gpt|megatron|blend|data_loop|ops_relay|watch_.*_loop' | grep -v grep | cut -c1-170 | head -25
echo
echo "== C. GPU（若有）=="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null | head -8 || echo "  no nvidia-smi"
echo
echo "== D. 关键日志尾部（含 push 错误）=="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_data_loop.log /tmp/baize_ops_relay.29.log /tmp/baize_ops_relay.12.log; do
  if [ -f "$f" ]; then
    echo "--- $f  [$(stat -c '%y  %s B' "$f")]"
    tail -n 6 "$f" | cut -c1-200
  fi
done
echo "-- 最近 push/git 错误 --"
grep -hE 'push FAILED|rejected|Network is unreachable|index\.lock|smaller than expected|fatal:' \
  /tmp/baize_pretrain_loop.log /tmp/baize_data_loop.log 2>/dev/null | tail -8 | cut -c1-200
echo
echo "== E. 共享仓状态 =="
R=/nas_train/app.e0031982/code/super_intelligence_2035
ls -l "$R/.git/index" "$R/.git/index.lock" 2>/dev/null
if [ -d "$R/.git/rebase-merge" ]; then echo "WARN rebase-merge 残留"; else echo "no rebase-merge"; fi
cd "$R" 2>/dev/null && {
  git log -1 --format='HEAD %h %ad %s' --date=iso
  echo "dirty=$(git status --porcelain | wc -l)  ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
  git status -sb | head -3
}
echo "-- 本线关键文件 mtime --"
ls -l --time-style=+%F_%T "$R/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md" \
                        "$R/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md" \
                        "$R/doc/BaiZe-ISEDA2027/run/reports/report_pretrain_llamacpp_scaling_zh.html" 2>/dev/null \
  | awk '{print $6, $7}'
echo
echo "== F. pretrain 训练实况 =="
H=$(hostname)
if echo "$H" | grep -q '29$'; then
  echo "  (local on .29)"
  tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200
  ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt' | cut -c1-140 | head -5
else
  timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.29 \
    "tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200; ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt' | cut -c1-140 | head -5" 2>&1 \
    | sed 's/^/  .29| /' | head -12
  echo "  .29_ssh_rc=$?"
fi
echo
echo "== G. data 线实况 =="
if echo "$H" | grep -q '12$' && ! echo "$H" | grep -q 's0pgpuap12'; then
  echo "  (local on .12)"
  tail -n 6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-200
  ps -eo pid,etime,args | grep -E '[d]ata_loop|[b]lend' | cut -c1-140 | head -5
else
  timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
    "tail -n 6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-200; ps -eo pid,etime,args | grep -E '[d]ata_loop|[b]lend' | cut -c1-140 | head -5" 2>&1 \
    | sed 's/^/  .12| /' | head -12
  echo "  .12_ssh_rc=$?"
fi
echo
echo "== H. github 连通性（.12 需要代理 92.23）=="
timeout 15 curl -sS -o /dev/null -w "github=%{http_code}\n" https://github.com 2>&1 | tail -1
echo
echo "（只读：未 kill / 未重启 / 未改配置）"
echo "=== DONE 291 | $(date '+%F %T') ==="
```
