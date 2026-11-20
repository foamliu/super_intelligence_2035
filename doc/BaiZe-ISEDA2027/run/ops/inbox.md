# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 285 | TARGET: 12 -->
## RUN_ID 285 — **修正取样口径：`.29` 最后一次可见写入 + SSH 认证阶段诊断（只读 · 2026-11-20 10:5x）**

> **上一轮（284）的两处口径缺陷，本轮修正**：
> ① `find -maxdepth 6/7` **太浅**——仓库文件在 depth 9+、ckpt 在 depth 8+，所以 `[4]/[5]` 的「0 写入」不能采信；
> ② `[2]` 里 `cut -d\" \"` 被外层引号吞掉，`uptime/load` 没取到。
> **已知**：`.29` ping 通、`:22` TCP OPEN、`ssh -vv` **已完成 KEX 并收到 `SSH2_MSG_SERVICE_ACCEPT`，随后卡在用户认证**；`.12` 中继正常（已执行 282/283/284）。
> **只读**：不 kill、不重启、不改任何文件。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
R=/nas_train/app.e0031982/code/super_intelligence_2035
echo
echo "[1] 精确目录的最近写入（mtime 排序，各取前 4）"
for d in "$R/doc/BaiZe-ISEDA2027/run/logs" "$R/doc/BaiZe-ISEDA2027/run/daily-memories" "$R/doc/BaiZe-ISEDA2027/run/daily-memories-harness" "$R/doc/BaiZe-ISEDA2027/run/reports"; do
  echo "  [$d]"
  ls -lt --time-style=+%m-%d_%H:%M "$d" 2>/dev/null | sed -n "2,5p" | sed "s/^/    /"
done
echo
echo "[2] git 侧写入时间（.29 若还在提交，这些会变新）"
ls -lt --time-style=+%m-%d_%H:%M "$R/.git" 2>/dev/null | sed -n "1,6p" | sed "s/^/  /"
ls -lt --time-style=+%m-%d_%H:%M "$R/.git/refs/heads" 2>/dev/null | sed -n "1,3p" | sed "s/^/  refs| /"
echo
echo "[3] 训练产物：latest_checkpointed_iteration / iter_02x 目录（深度放到 9）"
timeout 90 find /nas_train/app.e0031982 -maxdepth 9 \( -name "latest_checkpointed_iteration.txt" -o -type d -name "iter_02*" \) -printf "%TY-%Tm-%Td %TH:%TM  %p\n" 2>/dev/null | sort | tail -6 | sed "s/^/  /"
echo
echo "[4] /nas_train 近 4 小时被写过的文件（深度 8，按时间取最后 5 条）"
timeout 90 find /nas_train/app.e0031982 -maxdepth 8 -type f -mmin -240 -printf "%TY-%Tm-%Td %TH:%TM  %p\n" 2>/dev/null | sort | tail -5 | sed "s/^/  /"
echo
echo "[5] SSH 认证阶段（只要结果，60s）"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o PreferredAuthentications=publickey -o NumberOfPasswordPrompts=0 10.239.2.29 "uptime" 2>&1 | tail -4 | sed "s/^/  auth| /"
echo
echo "[6] 中继实例（是否被反复重启）"
ps -eo pid,etime,args | grep "[o]ps_relay" | cut -c1-120 | sed "s/^/  /"
tail -n 3 /tmp/baize_ops_relay.12.log 2>/dev/null | cut -c1-150 | sed "s/^/  relay12| /"
echo
echo "（只读：未 kill / 未重启 / 未改文件）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 285 | $(date "+%F %T") ==="
```
