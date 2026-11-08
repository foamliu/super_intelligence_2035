# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 273 | TARGET: 12 -->
## RUN_ID 273 — **极简：各 chunk tqdm 进度 + 输出目录内容**（只读）

```bash
set -u
echo "=== RUN_ID 273 | progress | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
D=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v5_correct_binary
for c in 0 1 2 3; do
  echo "== chunk$c =="
  ls -t $D/hellaswag_chunk$c/ 2>/dev/null | head -6 | sed "s/^/  /"
  f=$(ls -t $D/hellaswag_chunk$c/*.log 2>/dev/null | head -1)
  [ -n "$f" ] && { echo "  log=$f"; grep -oE "[0-9]+/[0-9]+ \\[[^]]*\\]" "$f" | tail -1 | sed "s/^/  /"; tail -1 "$f" | cut -c1-140 | sed "s/^/  /"; }
done
echo "== piqa =="; ls -t $D/piqa/ 2>/dev/null | head -5 | sed "s/^/  /"; f=$(ls -t $D/piqa/*.log 2>/dev/null | head -1); [ -n "$f" ] && tail -1 "$f" | cut -c1-140 | sed "s/^/  /"
echo "== writer lines =="; grep -nE "json.dump|json.dumps|samples.*open|write\(" /tmp/baize_eval_v4/gguf_lmeval_run.py | cut -c1-120 | head -8'
echo
echo "=== 273 done ==="
```
