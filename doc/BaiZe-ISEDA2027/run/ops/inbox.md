# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 241 | TARGET: 29 -->
## RUN_ID 241 — pretrain 细查（只读）：loop 日志尾部 / cline 会话 / 子进程树 / 残留 llama-server

> RUN_ID 240 已确认：S1 iter 82320 健康（6.88s/step、GPU 97–100%）、`baize_pretrain_loop.sh` alive（etimes≈554k）、`.12` torchrun alive；但本线自 14:03 起无提交。**本块只查「loop 在干什么」**。
> 只读；不 kill、不重启、不写文件；`cline` 命令行一律截断（README §8）。

```bash
set -u
echo "=== RUN_ID 241 | pretrain loop forensics (read-only) | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[1] pretrain loop 日志尾部（最近 30 行）"
tail -30 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-240
echo
echo "[2] loop 进程与其子进程"
LOOP=$(pgrep -f 'baize_pretrain_loop\.sh' | head -1)
echo "loop_pid=${LOOP:-none}"
if [ -n "${LOOP:-}" ]; then
  ps -o pid,ppid,etimes,pcpu,rss,args --ppid "$LOOP" --no-headers 2>/dev/null | cut -c1-180 | head -10
  echo "--- grandchildren ---"
  for p in $(pgrep -P "$LOOP" 2>/dev/null); do
    ps -o pid,ppid,etimes,pcpu,args --ppid "$p" --no-headers 2>/dev/null | cut -c1-160 | head -5
  done
fi
echo
echo "[3] 本线 cline / 调试子进程（截断 160 字符）"
ps -eo pid,etimes,pcpu,rss,args --sort=-etimes --no-headers 2>/dev/null | grep -E 'cline|gdb|convert_hf_to_gguf|llama-cli' | grep -v -E 'grep -E|RUN_ID 241' | cut -c1-160 | head -8
echo
echo "[4] 最近 20 分钟内被写过的 baize 日志"
find /tmp -maxdepth 1 -name 'baize_*.log*' -mmin -20 -printf '%TY-%Tm-%Td %TH:%TM %10s %p\n' 2>/dev/null | sort | tail -12
echo
echo "[5] 本线最近提交（MEMORY/llamacpp 视角）"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && git log -4 --pretty='%h %ad %s' --date=format:'%m-%d %H:%M' -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/llamacpp.txt | cut -c1-160
echo
echo "[6] 残留 llama-server（只读，不 kill）"
echo "count=$(pgrep -fc 'llama-server' 2>/dev/null || echo 0)"
pgrep -af 'llama-server' 2>/dev/null | cut -c1-120 | head -10
echo
echo "=== DONE 241 ==="
```
