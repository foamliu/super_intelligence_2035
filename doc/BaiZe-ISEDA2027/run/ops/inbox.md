# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 290 | TARGET: 12 -->
## RUN_ID 290 — **pretrain / data 静默体检（只读 · 2026-11-24 22:4x）**

> 背景：pretrain 自 **19:17**、data 自 **19:57** 起无新提交（静默 2.5–3.2h，常态 10–20min/条），
> 怀疑 ① loop 已死 ② `git push` 失败（.12 的 github 需要代理 92.23）③ `.git/index` 损坏 / `index.lock` 残留 ④ NFS D-state。
> 另：`.29` 与 `.12` 共享同一 NFS 工作副本，**命令可能落在任一台**；本块会打印 `exec_host` 并对另一台做 bounded ssh。
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
echo "=== DONE 290 | $(date '+%F %T') ==="
```
