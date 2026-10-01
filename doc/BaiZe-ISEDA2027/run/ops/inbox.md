# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 2 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> **整块会被当成一个脚本执行**，可以写变量、循环、管道。
> 危险模式（`rm -rf /` 等）会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **上一批（RUN_ID 1）的教训**：`pgrep -af` 会把整条 cline 命令行（**含整份任务书**）打出来，
> 吃光 20000 字符的截断额度，导致后面的数据目录部分被截掉。
> → **本次所有可能很长的输出都加 `cut -c1-140` 截断**；用 `ps -eo pid=,comm=,args=` 代替裸 `pgrep -af`。

---

## RUN_ID 2 — 补全 RUN_ID 1 被截掉的部分

**目标**：拿回被截断的 **数据目录清单 / 数据集实测规模 / 磁盘余量 / python-torch / repo 布局**，
用于核对 `run/DATA_LEDGER.md` 的实测值。

```bash
echo "=========== LOOPS (line-truncated) ==========="
ps -eo pid=,comm=,args= 2>/dev/null | grep -E 'baize_.*_loop\.sh|ops_relay\.sh' | grep -v grep | cut -c1-140 || echo "(none)"
echo
echo "=========== TRAINING PROCESSES (line-truncated) ==========="
ps -eo pid=,comm=,args= 2>/dev/null | grep -E 'torchrun|megatron|pretrain_launcher|open_clip|train\.py' | grep -v grep | cut -c1-140 || echo "(none)"
echo
echo "=========== DATA ROOTS ==========="
echo "-- /nas_inference/app.e0031982/datasets --"
ls -1 /nas_inference/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- openbmb --"
ls -1 /nas_inference/app.e0031982/datasets/openbmb 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982 (top-level) --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo
echo "=========== KEY DATASET SIZES (du timeout 90s each) ==========="
for d in \
  /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Code \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Math \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609 \
  /nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M \
  /nas_train/app.e0031982/datasets/baize-vision ; do
  if [ -e "$d" ]; then
    printf '%-95s : ' "$d"
    timeout 90 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== DISK FREE SPACE (matters for data prep) ==========="
df -h /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== PYTHON / TORCH ==========="
P=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
if [ -x "$P" ]; then "$P" -c "import sys,torch;print('python',sys.version.split()[0]);print('torch',torch.__version__);print('cuda',torch.version.cuda);print('gpu_count',torch.cuda.device_count())" 2>&1 | head -10; else echo "python not found at $P"; fi
echo
echo "=========== REPO / CODE LAYOUT ==========="
ls -1 /nas_train/app.e0031982/code 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027 --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027 2>/dev/null | head -25
echo "-- BaiZe-ISEDA2027/data --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data 2>/dev/null | head -20
echo
echo "=========== BAZE-VISION (derived, for stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== DONE ==========="
```
