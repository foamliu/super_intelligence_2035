# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 283 | TARGET: 12 -->
## RUN_ID 283 — **`.29` 到底是死是活：可达性 + NFS 写入痕迹取证（只读 · 2026-11-20 10:4x）**

> **背景（RUN_ID 282 实测结果，不必重查）**：RUN_ID 282 由 `whag0pgpuap12` 在 10:04:22 执行、exit=0，但它内部 `ssh 10.239.2.29` **跑满 180s 超时、零输出**；`.29` 的中继游标至今仍停在 281（未执行 282）。⇒ `.12 → .29` 的 SSH 通路当前不可用，或 `.29` 主机/sshd 卡死。
> 本令**不去修 `.29`**，只用 `.12` 能看到的证据回答三件事：① `.29` 网络层是否活着；② 共享 NFS 上 `.29` 侧最近有没有写入（= 训练/loop 是否还在跑）；③ 共享副本 git 是否干净（这决定 loop 复活后能否 push）。
> **只读**：不 kill、不重启、不改 `.29` 任何东西、不动共享副本。
> 投递到 `.12`（唯一在线中继）。

```bash
set -u
BODY='
set -u
echo "host=$(hostname)  date=$(date "+%F %T")"
echo
echo "[1] .29 可达性"
ping -c 2 -W 2 10.239.2.29 2>&1 | tail -3
( timeout 3 bash -c "</dev/tcp/10.239.2.29/22" ) >/dev/null 2>&1 && echo "  tcp22=OPEN" || echo "  tcp22=CLOSED_OR_TIMEOUT"
timeout 12 ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no 10.239.2.29 "echo SSH_OK; hostname; uptime" 2>&1 | tail -3 | sed "s/^/  ssh| /"
echo
echo "[2] 共享副本 git（两机同一块 NFS）"
R=/nas_train/app.e0031982/code/super_intelligence_2035
git -C "$R" log -1 --date=iso --format="  HEAD %ad %h" 2>&1 | cut -c1-110
echo "  left-right(origin...HEAD)=$(git -C "$R" rev-list --left-right --count origin/main...HEAD 2>/dev/null | tr "\t" " ")"
echo "  staged=$(git -C "$R" diff --cached --name-only 2>/dev/null | wc -l) unstaged=$(git -C "$R" diff --name-only 2>/dev/null | wc -l) untracked=$(git -C "$R" ls-files -o --exclude-standard 2>/dev/null | wc -l)"
[ -f "$R/.git/index.lock" ] && stat -c "  LOCK %y %s %n" "$R/.git/index.lock"
git -C "$R" log -1 --date=iso --format="  last_pretrain_commit=%ad %h" -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md 2>/dev/null
git -C "$R" log -1 --date=iso --format="  last_harness_commit=%ad %h" -- doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md 2>/dev/null
echo
echo "[3] 共享副本上近 60 分钟被改动的 run/ 文件（= 是否有 agent 还在写）"
L=$(find "$R/doc/BaiZe-ISEDA2027/run" -type f -mmin -60 2>/dev/null | head -8)
if [ -n "$L" ]; then echo "$L" | sed "s/^/  /"; else echo "  无（60 分钟内 run/ 零写入）"; fi
echo
echo "[4] /nas_train 近 3 小时被写过的文件（checkpoint / 训练日志痕迹，最多 8 条）"
L=$(timeout 60 find /nas_train/app.e0031982 -maxdepth 6 -type f -mmin -180 2>/dev/null | head -8)
if [ -n "$L" ]; then echo "$L" | sed "s/^/  /"; else echo "  无（3 小时内 /nas_train 零写入 → 训练已停）"; fi
echo
echo "[5] /nas_train 近 1 小时内 >50MB 的新写入（最多 5 条，看是否还在存 ckpt）"
L=$(timeout 60 find /nas_train/app.e0031982 -maxdepth 7 -type f -size +50M -mmin -60 2>/dev/null | head -5)
if [ -n "$L" ]; then echo "$L" | sed "s/^/  /"; else echo "  无"; fi
echo
echo "[6] .12 中继自身"
ps -eo pid,etime,args | grep "[o]ps_relay" | cut -c1-110 | head -3 | sed "s/^/  /"
tail -n 4 /tmp/baize_ops_relay.12.log 2>/dev/null | cut -c1-140 | sed "s/^/  relay12| /"
echo
echo "（全部只读：未 kill / 未重启 / 未改 .29 / 未改共享副本）"
'
echo
echo "[0] 本令只投 .12（TARGET: 12）；实际执行机 = $(hostname)"
eval "$BODY"
echo
echo "=== DONE 283 | $(date "+%F %T") ==="
```
