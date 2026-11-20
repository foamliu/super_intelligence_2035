# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 287 | TARGET: 12 -->
## RUN_ID 287 — **由 `.12` SSH 进 `.29`：服务器状态 + `.29` ops 中继 + pretrain/harness 两个 loop（只读 · 2026-11-20 11:2x）**

> **背景**：`.12→.29` 之前用默认参数 ssh 会卡在认证（284/286 实测），但用户确认 **`.12` 是可以 SSH 到 `.29` 的** —— 说明是**参数/密钥/主机名姿势**问题，不是通路断。
> 本令：先**逐种姿势**试登录（每种 30s 上限，成功即停），登录成功后**一次性**采集：
> ① 服务器状态（uptime / loadavg / 内存 / 磁盘 / GPU / NFS 挂载 / dmesg 尾 / D 状态进程数）
> ② `.29` 的 ops 中继进程与日志
> ③ pretrain / harness 两个 agent loop 进程与日志
> **只读**：不 kill、不重启、不改任何文件、不装东西。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
echo
echo "[0] .12 侧 ssh 配置（判断该用哪把钥匙 / 有没有 host 别名）"
ls -l ~/.ssh 2>/dev/null | head -8 | sed "s/^/  /"
grep -v -e "^#" -e "^$" ~/.ssh/config 2>/dev/null | head -12 | sed "s/^/  cfg| /"
echo
REMOTE="uptime; cat /proc/loadavg; free -g | head -3; nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader; echo ---procs; ps -eo pid,ppid,etime,stat,pcpu,rss,args | grep -e baize_ -e torchrun -e pretrain_gpt -e harness | grep -v grep | cut -c1-150 | head -20; echo ---relay; ps -eo pid,etime,args | grep ops_relay | grep -v grep | cut -c1-110; tail -n 8 /tmp/baize_ops_relay.29.log 2>/dev/null; echo ---loops; ls -l /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null; tail -n 4 /tmp/baize_pretrain_loop.log 2>/dev/null; tail -n 4 /tmp/baize_harness_loop.log 2>/dev/null; echo ---Dstate; ps -eo stat= | cut -c1 | grep -c D; echo ---mount; mount | grep -e nas -e nfs | head -5; echo ---dmesg; dmesg 2>/dev/null | tail -6"
SSHOK=""
for v in 1 2 3 4 5; do
  case $v in
    1) OPTS="-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no"; TGT="10.239.2.29" ;;
    2) OPTS="-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no -o GSSAPIAuthentication=no -o PreferredAuthentications=publickey -o NumberOfPasswordPrompts=0"; TGT="10.239.2.29" ;;
    3) OPTS="-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no -o IPQoS=throughput -o Compression=no"; TGT="app.e0031982@10.239.2.29" ;;
    4) OPTS="-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no"; TGT="whag0pgpuap29" ;;
    5) OPTS="-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no"; TGT="app.e0031982@whag0pgpuap29" ;;
  esac
  echo "  try#$v target=$TGT"
  OUT=$(timeout 30 ssh $OPTS "$TGT" "echo SSH_LOGIN_OK; hostname" 2>&1); RC=$?
  echo "    rc=$RC  out=$(echo "$OUT" | tail -2 | tr "\n" " " | cut -c1-150)"
  if echo "$OUT" | grep -q SSH_LOGIN_OK; then SSHOK="$OPTS $TGT"; echo "    ==> 登录成功 (try#$v)"; break; fi
done
echo
if [ -n "${SSHOK:-}" ]; then
  echo "======== .29 实测采集（ssh $SSHOK）========"
  timeout 150 ssh $SSHOK "$REMOTE" 2>&1 | cut -c1-200 | sed "s/^/  /"
  echo "  ssh_collect_rc=$?"
else
  echo "  !! 5 种姿势全部未登录成功 —— 与用户所述不一致，需人工确认账号/密钥"
fi
echo
echo "（只读：未 kill / 未重启 / 未改文件）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 287 | $(date "+%F %T") ==="
```
