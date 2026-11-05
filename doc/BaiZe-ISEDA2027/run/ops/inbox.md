# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 244 | TARGET: 29 -->
## RUN_ID 244 — pretrain「80k 结果 + 会话是否绕圈」只读复查（60k/70k 逐项分数一并取）

> 距 RUN_ID 243 约 1 小时。pretrain 线自 19:49 `#1418` 起 **2h20m 无提交**，80k eval 已过 ETA(21:58)；同时 loop 的 cline 会话已连续运行 **~137 min**（21:13 时 99.6% CPU）。
> 本块**只读**：不 kill、不重启、不写工作区、不碰训练。命令总耗时应 < 60 s。

```bash
set -u
echo "=== RUN_ID 244 | pretrain 80k & session-loop probe (read-only) | $(date '+%F %T') | host=$(hostname) ==="
echo
echo "[1] 机器负载 / 核数"
nproc; uptime
echo
echo "[2] cline 会话（pretrain）"
CL=$(ps -eo pid,etimes,pcpu,rss,args --no-headers 2>/dev/null | grep -F 'data-dir /nas_train/app.e0031982/.cline_pretrain' | grep -v grep | awk '{print $1}' | head -1)
echo "cline_pid=${CL:-none}"
[ -n "${CL:-}" ] && ps -o pid,etimes,pcpu,pmem,rss,nlwp --no-headers -p "$CL" 2>/dev/null
[ -n "${CL:-}" ] && echo "--- children ---" && ps -o pid,etimes,pcpu,args --no-headers --ppid "$CL" 2>/dev/null | cut -c1-160 | head -6
echo
echo "[3] loop 日志：最近 30 行 + 工具调用计数（判是否绕圈）"
tail -30 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-180
echo "--- 近 2000 行内工具调用计数 ---"
tail -2000 /tmp/baize_pretrain_loop.log 2>/dev/null | grep -c 'search_codebase' | sed 's/^/search_codebase=/'
tail -2000 /tmp/baize_pretrain_loop.log 2>/dev/null | grep -c 'run_commands' | sed 's/^/run_commands=/'
tail -2000 /tmp/baize_pretrain_loop.log 2>/dev/null | grep -c 'read_files' | sed 's/^/read_files=/'
echo
echo "[4] 评测管线 / 当前 server"
PIPE=$(pgrep -f 'baize_eval_60k_100k_pipeline' | head -1); echo "pipeline_pid=${PIPE:-none}"
[ -n "${PIPE:-}" ] && ps -o pid,etimes,pcpu,args --no-headers -p "$PIPE" | cut -c1-160
pgrep -af 'llama-server' 2>/dev/null | head -2 | cut -c1-220
echo "--- eval 日志尾 8 行 ---"
tail -8 /tmp/baize_eval_60k_100k.log 2>/dev/null | cut -c1-180
echo
echo "[5] results.json 落盘 + 60k/70k 逐项分数"
R=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
for it in 60000 70000 80000 90000; do
  f=$R/gguf_iter_${it}_fixed_8set/results.json
  if [ -f "$f" ]; then stat -c "iter_$it results.json mtime=%y size=%s" "$f"; else echo "iter_$it results.json MISSING"; fi
done
/nas_train/app.e0031982/miniforge3/envs/py310/bin/python - <<'PY' 2>/dev/null || echo "(python parse skipped)"
import json, os
R="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results"
TASKS=["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]
for it in (60000,70000,80000):
    p=os.path.join(R,f"gguf_iter_{it}_fixed_8set","results.json")
    if not os.path.exists(p): print(f"iter_{it}: MISSING"); continue
    d=json.load(open(p)).get("results",{})
    vals=[]
    for t in TASKS:
        v=d.get(t,{})
        a=v.get("acc,none", v.get("acc", None))
        if a is None:
            a=v.get("acc_norm,none", v.get("acc_norm", None))
        vals.append((t,a))
    ok=[a for _,a in vals if isinstance(a,(int,float))]
    avg=sum(ok)/len(ok) if ok else float("nan")
    print(f"iter_{it}: " + " ".join(f"{t}={a*100:.1f}" if isinstance(a,(int,float)) else f"{t}=NA" for t,a in vals) + f" | AVG={avg*100:.2f}")
PY
echo
echo "[6] S1 训练最新 iter"
grep -aE 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-200
echo
echo "[7] .29 克隆内 pretrain 线最近提交 / HEAD"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && {
  git log -2 --pretty='%h %ad %s' --date=format:'%m-%d %H:%M' -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | cut -c1-140
  echo "clone_HEAD=$(git rev-parse --short HEAD) behind=$(git rev-list --count HEAD..origin/main 2>/dev/null)"
}
echo
echo "=== DONE 244 ==="
```
