# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 251 | TARGET: 12 -->
## RUN_ID 251 — **取回 A/B 三段 Step Time 统计 + 恢复后状态**

> 冻结窗口：12:23:46–12:33:46（clients SIGSTOP 600 s，`trap` 自动恢复）。
> 解析器 `/tmp/baize_ab_analyze.txt` 在 12:39:18 生成（`sleep 800` + 按时间桶统计 log）。
> 本命令 ssh 到 `.29`，最多等 500 s（仍在 relay 600 s 上限内），随后 `cat` 结果 + 复核 client 状态与评测日志是否继续增长。

```bash
set -u
echo "=== RUN_ID 251 | fetch A/B analysis | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'for i in $(seq 1 50); do if [ -f /tmp/baize_ab_analyze.txt ] && grep -q "=== END ===" /tmp/baize_ab_analyze.txt 2>/dev/null; then break; fi; sleep 10; done; echo "-- waited_iter=$i (~${i}0 s) --"; cat /tmp/baize_ab_analyze.txt 2>/dev/null; echo; echo "-- live now --"; uptime; echo "-- clients --"; ps -eo pid=,stat=,etimes=,args= | awk "/[g]guf_lmeval_run\\.py/ && !/cline/ {print \"  \" \$1 \" \" \$2 \" etimes=\" \$3}" ; echo "-- eval chunk logs (size) --"; ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v4/hellaswag_chunk*.log 2>/dev/null | awk "{print \"  \" \$5 \" \" \$9}"'
echo
echo "=== 251 done ==="
```
