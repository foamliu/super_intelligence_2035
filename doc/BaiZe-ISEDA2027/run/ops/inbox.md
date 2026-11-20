# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 286 | TARGET: 12 -->
## RUN_ID 286 — **从 `.12` 侧看 `.29` 的三条线：pretrain / harness / ops 中继（只读 · 2026-11-20 11:1x）**

> **已知**（282/283/284/285 实测）：`.29` ping 通、`:22` 通、KEX 完成但**卡在用户认证**；`.29` 中继游标停在 281；共享副本 `origin...HEAD = 0 0`（`.12` 正常）。
> **关键约束**：`.29` 的 `/tmp` 日志 `.12` 看不到；但 **`/nas_train` 与 `$HOME` 是两机共享的 NFS**，所以 `.29` 侧三条线的**落盘痕迹在 `.12` 全可见**。
> 本轮就按「pretrain / harness / ops 中继」三块，逐个查 `.29` 留下的最后写入时间 + 再试一次连通性。
> **只读**：不 kill、不重启、不改任何文件。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
BASE=/nas_train/app.e0031982
CK=$BASE/code/BaiZe-ISEDA2027/nemo_experiments
R=$BASE/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo
echo "=========== A. pretrain（.29 独有）==========="
echo "[A1] 训练产出目录（ckpt 目录最后写入时间 = 训练最后一刻）"
ls -lt --time-style=+%m-%d_%H:%M "$CK/baize2b/checkpoints" 2>/dev/null | sed -n "1,6p" | sed "s/^/  /"
echo "[A2] 训练目录里的最新日志"
ls -lt --time-style=+%m-%d_%H:%M "$CK/baize2b" 2>/dev/null | sed -n "1,6p" | sed "s/^/  /"
echo "[A3] 最新日志尾部 3 行（含 iter/step）"
L=$(ls -t "$CK"/baize2b/*.log "$CK"/baize2b/logs/*.log 2>/dev/null | head -1)
if [ -n "${L:-}" ]; then echo "  file=$L  mtime=$(stat -c %y "$L")"; tail -n 3 "$L" | cut -c1-160 | sed "s/^/    | /"; else echo "  未找到 log"; fi
echo "[A4] pretrain agent 会话目录（最后活动时间）"
ls -lt --time-style=+%m-%d_%H:%M "$BASE/.cline_pretrain/sessions" 2>/dev/null | sed -n "1,4p" | sed "s/^/  /"
echo
echo "=========== B. harness（.29 独有）==========="
echo "[B1] harness 工作目录"
ls -lt --time-style=+%m-%d_%H:%M "$BASE/harness" 2>/dev/null | sed -n "1,6p" | sed "s/^/  /"
echo "[B2] harness agent 会话/日志目录（$HOME 下 .cline* 逐个列 mtime）"
for d in "$BASE"/.cline_harness "$BASE"/.cline_harness_eval "$HOME"/.cline_harness*; do
  [ -d "$d" ] && ls -ld --time-style=+%m-%d_%H:%M "$d" | sed "s/^/  dir /"
done
ls -lt --time-style=+%m-%d_%H:%M "$BASE/.cline_harness/sessions" 2>/dev/null | sed -n "1,4p" | sed "s/^/  /"
echo
echo "=========== C. ops 中继（.29 那只）==========="
echo "[C1] .29 中继游标文件的 mtime（= 最后一次执行命令的时刻）"
stat -c "  %y  %s  %n" "$R/ops/.last_run_id.29" 2>/dev/null
echo "[C2] outbox 里 .29 主机执行过的最后 3 条"
grep -nF "host=whag0pgpuap29" "$R/ops/outbox.md" 2>/dev/null | tail -3 | cut -c1-120 | sed "s/^/  /"
echo "[C3] 共享树里 .29 侧最后写过的 5 个文件（按 mtime，排除 .12 自己的明显产物）"
find "$R" -maxdepth 2 -type f -mmin -900 2>/dev/null | head -5 | sed "s/^/  /"
echo
echo "=========== D. 再试一次连 .29（换姿势，全部 2>&1）==========="
echo "[D1] 裸读 SSH banner（dd 逐字节，最多 5s）"
timeout 5 bash -c "exec 3<>/dev/tcp/10.239.2.29/22; dd bs=1 count=40 <&3 2>/dev/null" 2>&1 | head -2 | sed "s/^/  banner| /"
echo "[D2] ssh 公钥认证 45s（只看结果）"
timeout 45 ssh -o BatchMode=yes -o ConnectTimeout=10 -o PreferredAuthentications=publickey -o NumberOfPasswordPrompts=0 10.239.2.29 "echo SSH_LOGIN_OK; hostname; uptime" 2>&1 | tail -3 | sed "s/^/  ssh| /"
echo "[D3] .29 的 22 端口当前连接数（从 .12 看）"
timeout 5 bash -c "exec 3<>/dev/tcp/10.239.2.29/22" 2>&1 && echo "  connect=OK" || echo "  connect=FAIL"
echo
echo "（只读：未 kill / 未重启 / 未改文件）"
'
echo
echo "[0] TARGET: 12；执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 286 | $(date "+%F %T") ==="
```
