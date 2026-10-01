# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 3 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> 危险模式会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **两条纪律**（前两批的教训）：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② **绝不整树 `du`** —— `/nas_train` 有 175 TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`（每条带 `timeout`）**。

---

## RUN_ID 3 — 磁盘空间与占用分布

**目标**：确认 `df -h` 实况；定位 `/nas_train` 175 TB 被什么占用；核对数据准备所需空间与剩余空间。

```bash
echo "=========== DF -H (ALL MOUNTS) ==========="
df -h
echo
echo "=========== DF -H (NAS + ROOT, explicit) ==========="
df -h /nas_train /nas_inference /nas_user /nas_env / 2>/dev/null
echo
echo "=========== DF -I (INODES — large-corpus trap) ==========="
df -i /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== TARGETED DU (bounded, timeout 150s each) ==========="
for d in \
  /nas_train/app.e0031982/datasets/baize-vision \
  /nas_train/app.e0031982/datasets/baize-data \
  /nas_train/app.e0031982/datasets/mvp-lab \
  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data \
  /nas_train/app.e0031982/models \
  /nas_inference/app.e0031982/datasets/openbmb ; do
  if [ -e "$d" ]; then
    printf '%-58s : ' "$d"
    timeout 150 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout/fail)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== TOP-LEVEL LISTING (no du, just names) ==========="
echo "-- /nas_train/app.e0031982 --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null | head -40
echo "-- /nas_user/app.e0031982/datasets --"
ls -1 /nas_user/app.e0031982/datasets 2>/dev/null | head -40
echo
echo "=========== BAZE-VISION DETAIL (stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
timeout 60 du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== ANY IN-PROGRESS DOWNLOAD? ==========="
ps -eo pid=,etime=,comm=,args= 2>/dev/null | grep -E 'wget|curl|hf_transfer|datasets|nohup' | grep -v grep | cut -c1-140 | head -10 || echo "(none)"
echo "-- nohup.out tail (if a download is logging) --"
for f in /nas_inference/app.e0031982/datasets/nohup.out /nas_train/app.e0031982/datasets/nohup.out; do
  [ -f "$f" ] && { echo "== $f"; tail -5 "$f" | cut -c1-140; }
done
echo
echo "=========== DONE ==========="
```
