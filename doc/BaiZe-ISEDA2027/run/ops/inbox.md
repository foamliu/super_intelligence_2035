# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 289 | TARGET: 12 -->
## RUN_ID 289 — **`.29` 认证已通过但会话通道不开：长超时再试 + 无会话隧道验证（只读 · 2026-11-20 11:4x）**

> **288 结论（不必重查）**：`ssh-keyscan` 正常返回 `SSH-2.0-OpenSSH_8.9p1`；`ssh -vv` 走到
> `Authenticated to 10.239.2.29 … using publickey` → `Entering interactive session` → `channel 0: send open` → **服务端再无响应**，180s 被 kill。
> ⇒ **认证通、会话通道建不起来**（= sshd 主进程正常，但它 fork 出来的 session 子进程起不来 / 卡住）。
> 本轮两件事：
> ① 用 **`SessionType=none` 只搭隧道**（不需要 session 通道）验证「非会话路径」是否正常；
> ② 用 **420s 超时** 跑一条极简远程命令，判断到底是「永久卡死」还是「只是极慢」。
> **只读**：不 kill、不重启、不改文件。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
echo
echo "[1] SessionType=none 隧道测试（10s 内不退出 = 认证+通道建立正常，只是 session 起不来）"
timeout 12 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no -o SessionType=none -N -L 127.0.0.1:18922:127.0.0.1:22 app.e0031982@10.239.2.29 2>&1 | tail -3 | sed "s/^/  tun| /"
echo "  tun_rc=$?  (124 = 12s 内隧道一直活着 = 好迹象)"
echo
echo "[2] 420s 长超时 + 极简命令（若只是慢，这里能拿到数据）"
OUT=$(timeout 420 ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=no app.e0031982@10.239.2.29 "cat /proc/loadavg; uptime; echo DSTATE=$(ps -eo stat= | cut -c1 | grep -c D); nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader | head -8" 2>&1); RC=$?
echo "  rc=$RC"
echo "$OUT" | head -16 | cut -c1-180 | sed "s/^/  .29| /"
echo
echo "[3] 若 [2] 成功，再采三条线状态（60s）"
if echo "$OUT" | grep -q "load average"; then
  R3="ps -eo pid,ppid,etime,stat,pcpu,rss,args | grep -e baize_ -e torchrun -e pretrain_gpt -e harness | grep -v grep | cut -c1-150 | head -20; echo ---relay; ps -eo pid,etime,args | grep ops_relay | grep -v grep | cut -c1-110; tail -n 8 /tmp/baize_ops_relay.29.log 2>/dev/null; echo ---loops; ls -l /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null; tail -n 4 /tmp/baize_pretrain_loop.log 2>/dev/null; tail -n 4 /tmp/baize_harness_loop.log 2>/dev/null; echo ---mount; mount | grep -e nas -e nfs | head -5; echo ---dmesg; dmesg 2>/dev/null | tail -6"
  timeout 90 ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=no app.e0031982@10.239.2.29 "$R3" 2>&1 | cut -c1-190 | sed "s/^/  .29| /"
else
  echo "  [2] 未成功 → 跳过"
fi
echo
echo "（只读：未 kill / 未重启 / 未改文件）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 289 | $(date "+%F %T") ==="
```
