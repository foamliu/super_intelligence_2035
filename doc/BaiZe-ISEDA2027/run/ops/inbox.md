# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 284 | TARGET: 12 -->
## RUN_ID 284 — **`.29` 到底卡在哪：SSH banner 探针 + 长超时登录 + NFS 最后写入时间（只读 · 2026-11-20 10:5x）**

> **已知（RUN_ID 282/283 实测，不必重查）**：`.29` ping 通（0% 丢包，但 rtt 最大 293ms）；`.29:22` TCP OPEN；`.12→.29` 的 ssh 在 180s 内**连 banner 都没拿到**；共享副本 `origin...HEAD = 0 0`（`.12` 拉取正常、inbox 已到 283）；`/nas_train` **近 3 小时零写入**；pretrain/harness 最后提交仍是 01:22 / 01:13。
> 本轮把「`.29` 是负载饿死、sshd 僵死，还是文件系统挂死」区分开：**只读、不 kill、不重启**。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
echo
echo "[1] SSH banner 探针（能拿到 banner = sshd 进程还在接受连接）"
B=$(timeout 12 bash -c "exec 3<>/dev/tcp/10.239.2.29/22; head -c 64 <&3" 2>/dev/null)
if [ -n "${B:-}" ]; then echo "  banner=$B"; else echo "  banner=NONE（12s 内未返回 SSH banner → sshd 未响应）"; fi
echo
echo "[2] 长超时 ssh（240s）：一次性拿 uptime/load/GPU/进程"
timeout 240 ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -o ServerAliveCountMax=4 10.239.2.29 "uptime; echo LOAD=$(cut -d\" \" -f1-3 /proc/loadavg); free -g | head -2; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader; echo ---procs---; ps -eo pid,etime,pcpu,args | grep -e baize_ -e torchrun -e pretrain | grep -v grep | cut -c1-120 | head -12" 2>&1 | tail -25 | sed "s/^/  ssh| /"
echo "  ssh_rc=$?"
echo
echo "[3] 若 [2] 失败：ssh -vv 看握手停在哪一步（最后 12 行）"
timeout 40 ssh -vv -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no 10.239.2.29 "true" 2>&1 | tail -12 | cut -c1-150 | sed "s/^/  vv| /"
echo
echo "[4] NFS 上最后的 checkpoint / 目录时间（判断训练是否停在某步）"
timeout 60 find /nas_train/app.e0031982 -maxdepth 7 -type d -name "iter_*" -printf "%TY-%Tm-%Td %TH:%TM  %p\n" 2>/dev/null | sort | tail -4 | sed "s/^/  /"
echo
echo "[5] /nas_train 近 24h / 6h / 1h 写入文件数（同一块盘，两机都能看到）"
for m in 1440 360 60; do printf "  last_%smin=%s\n" "$m" "$(timeout 60 find /nas_train/app.e0031982 -maxdepth 6 -type f -mmin -$m 2>/dev/null | wc -l)"; done
echo
echo "[6] .12 中继实例与日志尾"
ps -eo pid,etime,args | grep "[o]ps_relay" | cut -c1-110 | sed "s/^/  /"
tail -n 6 /tmp/baize_ops_relay.12.log 2>/dev/null | cut -c1-150 | sed "s/^/  relay12| /"
echo
echo "（只读：未 kill / 未重启 / 未改 .29 / 未改共享副本）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 284 | $(date "+%F %T") ==="
```
