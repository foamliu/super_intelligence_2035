# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 1 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`。
> **每行一条命令**，整块会被当成一个脚本执行（可以有变量、循环、管道）。
> 危险模式（`rm -rf /` 等）会被拦截；单块总超时 600s，超长输出截断 20000 字符。

---

## RUN_ID 1 — GPU 服务器环境摸底（首次执行）

**目的**：核实数据准备方案 §1 里那些"来自仓库记录、**未经实测**"的路径与规模。

```bash
echo "=========== BASIC ==========="
hostname; date; whoami; uname -r
echo
echo "=========== CPU / MEM ==========="
lscpu 2>/dev/null | grep -E '^Model name|^CPU\(s\):|^Socket' || true
free -g
echo
echo "=========== DISK ==========="
df -h 2>/dev/null | grep -E 'Filesystem|nas_train|nas_inference|/nas|/$' || df -h
echo
echo "=========== GPU (local node) ==========="
nvidia-smi
echo
echo "=========== RUNNING PROCESSES ==========="
echo "-- loops --"
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' || echo "(no loop processes)"
echo "-- training --"
pgrep -af 'torchrun|megatron|pretrain_launcher|open_clip|train\.py' || echo "(no training processes)"
echo
echo "=========== REMOTE NODE 10.239.2.12 ==========="
ssh -o BatchMode=yes -o ConnectTimeout=8 10.239.2.12 'hostname; echo "-- gpu --"; nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader; echo "-- loops/training --"; pgrep -af "baize_.*_loop\.sh|torchrun|open_clip|train\.py" || echo "(none)"' 2>&1 | head -40
echo
echo "=========== GIT (shared working copy) ==========="
cd /nas_train/app.e0031982/code/super_intelligence_2035 && git status -sb | head -5 && git log --oneline -3
echo
echo "=========== DATA ROOTS ==========="
echo "-- /nas_inference/app.e0031982/datasets --"
ls -1 /nas_inference/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- openbmb --"
ls -1 /nas_inference/app.e0031982/datasets/openbmb 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo
echo "=========== KEY DATASET SIZES (timeout 90s each) ==========="
for d in \
  /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Code \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Math \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent \
  /nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M \
  /nas_train/app.e0031982/datasets/baize-vision ; do
  if [ -e "$d" ]; then
    echo "-- $d"
    timeout 90 du -sh "$d" 2>/dev/null || echo "   (du timed out or failed)"
    timeout 30 find "$d" -maxdepth 1 -type f 2>/dev/null | wc -l | sed 's/^/   files at depth1: /'
  else
    echo "-- $d  : MISSING"
  fi
done
echo
echo "=========== PYTHON / TORCH ==========="
P=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
[ -x "$P" ] && "$P" -c "import sys,torch;print('python',sys.version.split()[0]);print('torch',torch.__version__);print('cuda',torch.version.cuda);print('gpu_count',torch.cuda.device_count())" 2>&1 | head -10 || echo "python not found at $P"
echo
echo "=========== REPO / CODE LAYOUT ==========="
ls -1 /nas_train/app.e0031982/code 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027 --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027/data --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data 2>/dev/null | head -20
echo
echo "=========== DONE ==========="
```
