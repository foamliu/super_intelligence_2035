#!/bin/bash
# =====================================================================
# bpt_rca_recover_reeval.sh — RCA 丢码回补后的「干净重评测」(2026-11-16)
#
# 背景：run2/3/4 的 completed_code_generation jsonl 被共享 temp race 踩成 0~1 行
#   真码，但 code/<task>/pyAether_code/ 里的真实 .py 完整存活（per-batch 隔离）。
#   rca_recover_extract.py 已把存活 .py 回补进 jsonl（run2=42/run3=27/run4=32
#   真码行，原件 .rca_orig_bak.jsonl 备份保留）。本脚本对**回补后的 jsonl**重跑
#   run_eval.py → 产出干净的 execution_results + final_report（真实 Pass@1）。
#
# 关键安全设计（不踩同样的坑）：
#   - GATE：等 36.15 上无 run_cline_script.sh / run_eval.py 运行 → 避让共享
#     config.yaml(git checkout 互踩) + 共享 assemble 输出(generated_solutions)。
#     这正是 run2/3/4 坍塌的同类根因，必须避让。
#   - 三个 batch **串行**跑（各自 assemble→sandbox→calculate，共享输出目录）。
#   - run_eval.py 自恢复（restore_config git checkout config.yaml），加 --benchmark
#     强制 pyAether-158（小写 pyAether），与 run1 同口径。
#   - 不改 eda_fastmcp 代码，只复用 run_eval.py 入口（08:1x 纪律）。
#
# 产物 → attribution_3615_run{2,3,4}/final_report.json + execution_results.jsonl
#        （干净版；原坍塌版保留为 final_report_collapsed.jsonl 不动）
# 汇总 → rca_recover_reeval_summary.json
# =====================================================================
set -uo pipefail

# flock 防并发（避免两实例抢共享 generated_solutions/output_evaluation，即 run2/3/4 坍塌同类根因）
exec 9>/tmp/posttrain_rca_recover_reeval.lock
if ! flock -n 9; then echo "[rca_reeval] 另一实例已在跑 → 退出" | tee -a /tmp/posttrain_rca_recover_reeval.log; exit 0; fi

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
SSH="ssh -p 3333 -o ConnectTimeout=25 -o StrictHostKeyChecking=no -o BatchMode=yes app.e0031982@localhost"
REMOTE_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
VENV_PY="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
EVAL_FW="/nasdata/app.e0031982/code/EDA-Eval-Framework"
BENCH="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"   # 小写 pyAether, 158 行(run1 同口径)
LOG="/tmp/posttrain_rca_recover_reeval.log"
SUMMARY="$RUN_DIR/rca_recover_reeval_summary.json"
GATE_MAX_WAIT="${GATE_MAX_WAIT:-21600}"   # 最长等 6h 等 zhulong eval 释放沙盒

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

declare -A BATCH_OF=( [2]=2026_1115_110506 [3]=2026_1115_144001 [4]=2026_1115_183438 )

gate_wait(){
  log "[gate] 等 36.15 无 run_cline_script.sh / run_eval.py (最长 ${GATE_MAX_WAIT}s) ..."
  local waited=0
  while [ "$waited" -lt "$GATE_MAX_WAIT" ]; do
    local busy
    busy=$($SSH 'ps -eo pid=,cmd= 2>/dev/null | grep -E "[r]un_cline_script.sh|[r]un_eval.py" | head -1' 2>/dev/null | awk '{print $1}' | tr -d '[:space:]')
    if [ -z "$busy" ]; then log "[gate] 空闲 → 放行"; return 0; fi
    log "[gate] 仍忙 (pid=$busy) → 300s 后再探 (已等 ${waited}s)"; sleep 300; waited=$((waited+300))
  done
  log "[gate] ⚠ 超时仍未放行 → 本轮放弃(不强行抢沙盒)"; return 1
}

reeval_one(){
  local runidx="$1" batch="$2"
  local dest="$RUN_DIR/attribution_3615_run${runidx}"
  local gen_jsonl="completed_code_generation_${batch}.jsonl"
  log "[run $runidx] 重评测 batch=$batch gen=$gen_jsonl"
  local marker="/tmp/.rca_reeval_marker_run${runidx}_${batch}"
  $SSH "touch $marker" 2>/dev/null
  local cmd="cd $REMOTE_BASE && PYTHON=$VENV_PY EVAL_FW_DIR=$EVAL_FW timeout --signal=TERM --kill-after=120 14400 $VENV_PY scripts/run_eval.py -g $gen_jsonl --benchmark $BENCH"
  local rc=0
  $SSH "$cmd" >>"$LOG" 2>&1 || rc=$?
  log "[run $runidx] run_eval 退出 rc=$rc"
  local oe_dir
  oe_dir=$($SSH "MARKER='$marker' python3 - <<'PYEOF'
import os, glob
mk=os.environ['MARKER']; mt=os.path.getmtime(mk); hit=''
for d in glob.glob('$EVAL_FW/output_evaluation/*_app.e0031982/'):
    fr=os.path.join(d,'final_report.json')
    if os.path.isfile(fr) and os.path.getmtime(fr)>=mt: hit=d; break
print(hit)
PYEOF" 2>/dev/null | tr -d '\r')
  if [ -z "$oe_dir" ]; then log "[run $runidx] ⚠ 无新 output_evaluation → INVALID-noeval"; echo "INVALID-noeval"; return 0; fi
  log "[run $runidx] 匹配 output_evaluation=$oe_dir"
  [ -f "$dest/final_report.json" ] && [ ! -f "$dest/final_report_collapsed.jsonl" ] && cp "$dest/final_report.json" "$dest/final_report_collapsed.jsonl" 2>/dev/null || true
  $SSH "cat '${oe_dir}final_report.json' 2>/dev/null" >"$dest/final_report.json" 2>/dev/null || true
  $SSH "cat '${oe_dir}execution_results.jsonl' 2>/dev/null" >"$dest/execution_results.jsonl" 2>/dev/null || true
  $SSH "cat ~/eda_code_eval/${gen_jsonl} 2>/dev/null" >"$dest/completed_code_generation_recovered.jsonl" 2>/dev/null || true
  local pr nexec
  pr=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));print(d.get('metrics',{}).get('pass_rate','NA'))" 2>/dev/null || echo NA)
  nexec=$(wc -l < "$dest/execution_results.jsonl" 2>/dev/null | tr -d '[:space:]')
  log "[run $runidx] 干净 Pass@1=$pr  execution_results 行数=$nexec (产物→ $dest)"
  echo "${pr}|${nexec}"
}

log "===== RCA 丢码回补·干净重评测 START ====="
log "BENCH=$BENCH  GATE_MAX_WAIT=$GATE_MAX_WAIT"
if ! gate_wait; then log "GATE 超时 → 退出(下次唤醒再试)"; exit 0; fi

declare -a RESULTS=()
for i in 2 3 4; do res=$(reeval_one "$i" "${BATCH_OF[$i]}"); RESULTS+=("$i:$res"); done
log "结果: ${RESULTS[*]}"

python3 - "$SUMMARY" "${RESULTS[@]}" <<'PYEOF' || log "⚠ 汇总生成失败"
import json, sys
out=sys.argv[1]; rows={}
for arg in sys.argv[2:]:
    runidx, rest = arg.split(":",1)
    pr, nexec = (rest.split("|")+["NA","NA"])[:2]
    rows[f"run{runidx}"] = {"pass_rate": pr, "execution_results_lines": nexec}
doc={"generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
  "purpose": "RCA 丢码回补后干净重评测(run2/3/4 code/<task>/pyAether_code 存活 .py → rca_recover_extract.py 回补 → run_eval 重评)",
  "method": "gated run_eval.py -g <recovered jsonl> --benchmark EDA-Eval-pyAether-158.jsonl (run1 同口径, run_eval 自恢复 config)",
  "runs": rows,
  "note": "run1=18.99%(30/158)未受 race; 本表为 run2/3/4 回补后真实 Pass@1。原坍塌 0.0% 系共享 temp race, 非模型 collapse。"}
json.dump(doc, open(out,"w"), ensure_ascii=False, indent=2); print("summary ->", out)
PYEOF
log "===== RCA 丢码回补·干净重评测 END ====="

