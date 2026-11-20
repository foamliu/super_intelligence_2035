# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 288 | TARGET: 12 -->
## RUN_ID 288 — **判定 `.29` 的 sshd 是「不响应」还是「拒绝认证」：keyscan + 180s 详细握手（只读 · 2026-11-20 11:3x）**

> **已排除/已确认（287）**：`.12` 上 `~/.ssh` 只有 `id_rsa`，`config` 的 `ControlMaster` 只覆盖 `10.239.2.10/11/22/24`（**不含 `.29`**）；5 种登录姿势（默认 / 禁 GSSAPI+publickey / 显式 user / 主机名 / user+主机名）**全部 rc=124 超时且零输出**。
> **284 曾看到**：`ssh -vv` 到过 `SSH2_MSG_SERVICE_ACCEPT received`，随后卡住 ⇒ sshd 至少有时能完成 KEX。
> 本轮用 **`ssh-keyscan`（只做 banner+KEX，不需要认证）** 把两种情况分开：
> - keyscan **能出 key** ⇒ sshd 活着，问题只在认证（PAM/NFS/密钥）；
> - keyscan **也超时** ⇒ sshd 根本没在 accept（机器 hung / 进程 D 状态）。
> **只读**：不 kill、不重启、不改文件、不写 known_hosts（keyscan 只打 stdout）。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
echo
echo "[1] ssh-keyscan（不需要认证；能出 key = sshd 在正常响应）"
timeout 25 ssh-keyscan -T 15 -p 22 10.239.2.29 2>&1 | head -6 | cut -c1-160 | sed "s/^/  scan| /"
echo "  keyscan_rc=$?"
echo
echo "[2] 已有的 ControlMaster socket（用户手工 ssh 过会留下）"
ls -l ~/.ssh/control-* 2>/dev/null | head -6 | sed "s/^/  /"
echo
echo "[3] 单次详细握手 180s（只看判定性 debug 行 + 末尾）"
OUT=$(timeout 180 ssh -vv -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=no -o NumberOfPasswordPrompts=0 app.e0031982@10.239.2.29 "echo SSH_LOGIN_OK; hostname; uptime" 2>&1); RC=$?
echo "  rc=$RC"
echo "$OUT" | grep -E "Connecting to|Connection established|Remote protocol version|Local version|kex: algorithm|Authentications that can continue|Next authentication method|Offering public key|Server accepts key|Authenticated to|Permission denied|No more authentication|Timed out" | head -12 | cut -c1-160 | sed "s/^/  vv| /"
echo "  --- 末尾 6 行 ---"
echo "$OUT" | tail -6 | cut -c1-160 | sed "s/^/  vv| /"
echo
if echo "$OUT" | grep -q SSH_LOGIN_OK; then
  echo "[4] 登录成功 → 采集 .29 全景"
  R2="uptime; cat /proc/loadavg; free -g | head -3; nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader; echo ---procs; ps -eo pid,ppid,etime,stat,pcpu,rss,args | grep -e baize_ -e torchrun -e pretrain_gpt -e harness | grep -v grep | cut -c1-150 | head -20; echo ---relay; ps -eo pid,etime,args | grep ops_relay | grep -v grep | cut -c1-110; tail -n 8 /tmp/baize_ops_relay.29.log 2>/dev/null; echo ---loops; ls -l /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null; tail -n 4 /tmp/baize_pretrain_loop.log 2>/dev/null; tail -n 4 /tmp/baize_harness_loop.log 2>/dev/null; echo ---Dstate; ps -eo stat= | cut -c1 | grep -c D; echo ---mount; mount | grep -e nas -e nfs | head -5; echo ---dmesg; dmesg 2>/dev/null | tail -6"
  timeout 120 ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=no app.e0031982@10.239.2.29 "$R2" 2>&1 | cut -c1-200 | sed "s/^/  .29| /"
else
  echo "[4] 未登录 → 跳过采集"
fi
echo
echo "（只读：未 kill / 未重启 / 未改文件）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 288 | $(date "+%F %T") ==="
```
