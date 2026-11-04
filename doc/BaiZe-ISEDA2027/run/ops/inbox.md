# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 240 | TARGET: 29 -->
## RUN_ID 240 — pretrain 健康状况巡检（只读）：S1 训练 / pretrain loop / CPU 评测 / llama.cpp 调试痕迹

> 背景：11-04 13:2x 之后 pretrain 线在 git 上无任何提交，14:03 的「继续调 llama.cpp + 准备 PR」令未见执行痕迹；需确认是「长时间调试中」还是「loop/训练已停」。
> **硬约束：整块只读**——不 kill、不重启、不 SIGSTOP、不写 ckpt、不跑 GPU 任务；`pgrep -f` 结果一律过滤 `cline|bun` 并截断（ops README §8 教训）。

```bash
set -u
echo "=== RUN_ID 240 | pretrain health probe (read-only) | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[0] load / mem"
uptime
free -g | head -3
echo
echo "[1] top CPU 进程（排除 cline/bun，截断 180 字符）"
ps -eo pid,etimes,pcpu,rss,args --sort=-pcpu --no-headers 2>/dev/null | grep -v -E 'cline|bun' | head -12 | cut -c1-180
echo
echo "[2] S1 训练：专用进程 + 日志心跳"
pgrep -af 'pretrain_launcher|baize_s1_baize2b|train\.sh s1' 2>/dev/null | grep -v -E 'cline|bun' | cut -c1-160 | head -12
for f in /tmp/baize_s1_baize2b_worker.log /tmp/baize_s1_baize2b_master.log; do
  if [ -f "$f" ]; then
    echo "--- $f | mtime=$(stat -c '%y' "$f") | size=$(stat -c '%s' "$f")"
    grep -aE 'iteration [0-9]+/' "$f" | tail -2
    tail -4 "$f" | cut -c1-200
  else
    echo "--- $f 不存在"
  fi
done
echo
echo "[3] GPU 实况（只读，不分配）"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu --format=csv,noheader 2>&1 | head -10
echo
echo "[4] pretrain loop / CPU 评测 / llama.cpp 调试痕迹"
ps -eo pid,etimes,pcpu,args --sort=-pcpu --no-headers 2>/dev/null | grep -E 'baize_pretrain_loop|cpu_lmeval|gguf_lmeval|llama-server|llama-cli|convert_hf|gdb' | grep -v -E 'cline|bun' | cut -c1-180 | head -12
echo
echo "[5] /tmp 下 baize_* 日志最新 10 个（看活跃度）"
ls -lt --time-style='+%m-%d %H:%M' /tmp/baize_*.log 2>/dev/null | head -10
echo
echo "[6] 评测结果 / ckpt 目录最新条目"
ls -lt --time-style='+%m-%d %H:%M' /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results 2>/dev/null | head -8
ls -lt --time-style='+%m-%d %H:%M' /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b 2>/dev/null | head -8
echo
echo "[7] 远端 .12 快查（只读，12s 超时）"
timeout 12 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 10.239.2.12 'echo "host=$(hostname)"; uptime; ps -eo pid,etimes,pcpu,args --sort=-pcpu --no-headers | grep -E "torchrun|cpu_lmeval|baize_pretrain_loop" | grep -v -E "cline|bun" | cut -c1-150 | head -6' 2>&1 | head -20 || echo "  [.12] ssh 失败或超时"
echo
echo "[8] 仓库 / 本线记忆文件状态"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && {
  echo "HEAD=$(git rev-parse --short HEAD) branch=$(git rev-parse --abbrev-ref HEAD)"
  git log -3 --pretty='%h %ad %s' --date=format:'%m-%d %H:%M' -- doc/BaiZe-ISEDA2027/run
  stat -c '%y %n' doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/llamacpp.txt 2>/dev/null
}
echo
echo "=== DONE 240 ==="
```
