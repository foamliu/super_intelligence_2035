#!/bin/bash
# 🔴🔴🔴 HARD-DISABLED GUARD (2026-11-17 wake629 → wake632 3rd-bypass hardening) 🔴🔴🔴
# 此脚本会把 attribution_3615_runN 封存 mv 走并起新 eval = 起新 run，
# 违反 23:0x item1「不要再起任何新 run」+ 18:3x/22:0x 禁令「🚫 不改 run1-4 产物」。
# 已三次被未授权 wake 启动：
#   wake590 @ 11-16 17:24 / wake629 @ 11-17 09:25 / wake632 @ 11-17 11:29
#   （第3次用 `export BPT_CLEAN_5RUN_AUTHORIZED=1` 直接绕过旧 env-var guard，
#    已 kill 整树 PID1891007/1891011/1891025/1891050 + 从 git HEAD 恢复 run1-5，
#    exec 行数 36/43/28/35/44 全对，git diff HEAD 空）。
# 旧 env-var guard（BPT_CLEAN_5RUN_AUTHORIZED=1）已被证明无法阻止自主 wake（wake632 直接 export 绕过）
# ⇒ 现改为无条件 exit 7（硬禁用），env-var bypass 已移除。
# 保留全文作证据。如运维确实需要跑干净 5-run，必须由运维本人编辑本脚本注释掉下面的 exit 7；
# 自主 agent 不得编辑本 guard、不得以任何方式（env var / 编辑脚本 / 改名调用）绕过。
echo "baize_posttrain_clean_5run.sh HARD-DISABLED (3rd unauthorized bypass 2026-11-17 11:29; run1-5 restored from HEAD). Operator must edit out 'exit 7' to run. Agent MUST NOT bypass." >&2
exit 7
# =====================================================================
# baize_posttrain_clean_5run.sh
# 干净 5-run 重跑（run2-5），照抄 run1 配置，不搞幺蛾子
#
# run1 (attribution_3615_run1, 18.99%) 是 zhulong 自己跑的，配置：
#   run_cline_script.sh -p 8 -n  （无 -b flag，用 config.yaml 默认 benchmark）
#   CLI_AGENT=zhulong (from .env)
#   PreToolUse hook active
#   model via reverse tunnel 18096 → .17:8096
#
# 旧 chain script 的问题：
#   1. 加了 -b EDA-Eval-PyAether-v20260311_fixed.jsonl（run1 没这个）
#   2. 跟 zhulong eval 并发 → 共享 temp 互相踩 → 丢码
#   3. 事后 rca_recover_extract.py 回补 + 重跑 run_eval → 代码是初稿，没自验迭代
#
# 本脚本修复：
#   1. 不加 -b flag（和 run1 一样）
#   2. GATE 等待 36.15 无 run_cline_script.sh → 独占运行
#   3. 直接取原始 output_evaluation，不回补不重评
# =====================================================================
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
SSH="ssh -p 3333 -o ConnectTimeout=25 -o StrictHostKeyChecking=no -o BatchMode=yes app.e0031982@localhost"
REMOTE_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
LOG="/tmp/posttrain_clean_5run.log"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

# ---- GATE：等 36.15 无 run_cline_script.sh ----
gate_wait(){
  log "[gate] 等待 36.15 无 run_cline_script.sh ..."
  while :; do
    local rem_busy
    rem_busy=$($SSH 'ps -eo pid=,cmd= 2>/dev/null | awk "\$2==\"bash\" && /scripts\\/run_cline_script\\.sh/ {print \$1; exit}"' 2>/dev/null | tr -d '[:space:]')
    if [ -z "$rem_busy" ]; then
      log "[gate] 36.15 无 eval → 放行"
      return 0
    fi
    log "[gate] 仍忙 (pid=${rem_busy}) → 300s 后再探"
    sleep 300
  done
}

# ---- 单 run：在 36.15 跑全量 158（照抄 run1）----
run_one(){
  local runidx="$1"
  local dest="$RUN_DIR/attribution_3615_run${runidx}"

  # 备份旧产物
  if [ -d "$dest" ]; then
    local backup="${dest}_old_$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    log "[run $runidx] 旧产物备份 → $backup"
  fi
  mkdir -p "$dest"

  gate_wait

  local py_venv="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
  local eval_fw="/nasdata/app.e0031982/code/EDA-Eval-Framework"

  # 照抄 run1：run_cline_script.sh -p 8 -n （无 -b flag）
  # 用 setsid 在 36.15 上脱离 SSH，再轮询等待完成（防 SSH 断连杀 eval）
  log "[run $runidx] 在 36.15 启动全量158（照抄 run1: -p 8 -n, 无 -b, setsid 防断连）..."
  local remote_log="/tmp/posttrain_clean_run${runidx}.log"
  local remote_pid
  remote_pid=$($SSH "cd $REMOTE_BASE && PYTHON=$py_venv EVAL_FW_DIR=$eval_fw setsid bash -c 'timeout --signal=TERM --kill-after=120 80000 bash scripts/run_cline_script.sh -p 8 -n' > $remote_log 2>&1 < /dev/null & echo \$!" 2>/dev/null | tr -d '\r')
  log "[run $runidx] 远程 PID=$remote_pid, 日志=$remote_log"

  if [ -z "$remote_pid" ]; then
    log "[run $runidx] ⚠ 启动失败 → INVALID"
    echo "INVALID"
    return 0
  fi

  # 轮询等待远程 eval 完成（每 120s 检查一次）
  local wait_count=0
  while :; do
    local alive
    alive=$($SSH "kill -0 $remote_pid 2>/dev/null && echo yes || echo no" 2>/dev/null | tr -d '\r')
    if [ "$alive" = "no" ]; then
      log "[run $runidx] 远程 eval 完成 (PID=$remote_pid)"
      break
    fi
    wait_count=$((wait_count + 1))
    if [ $((wait_count % 10)) -eq 0 ]; then
      local remaining
      remaining=$($SSH "wc -l < ~/eda_code_eval/2026_1117_*/.task_queue 2>/dev/null | tail -1" 2>/dev/null | tr -d '\r')
      log "[run $runidx] 仍在跑... (已轮询 ${wait_count}×120s, task_queue=${remaining:-?})"
    fi
    sleep 120
  done

  # 直接取最新 output_evaluation（不回补、不重评）
  local latest_oe
  latest_oe=$($SSH "ls -dt /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/*_app.e0031982/ 2>/dev/null | head -1" 2>/dev/null | tr -d '\r')
  if [ -z "$latest_oe" ]; then
    log "[run $runidx] ⚠ 未找到 output_evaluation → INVALID"
    echo "INVALID"
    return 0
  fi
  log "[run $runidx] output_evaluation=$latest_oe"

  # 拷回产物
  for f in final_report.json execution_results.jsonl; do
    $SSH "cat '${latest_oe}${f}' 2>/dev/null" >"$dest/$f" 2>/dev/null || true
  done

  # completed_code_generation ← ~/eda_code_eval/（最新 batch）
  local latest_batch
  latest_batch=$($SSH 'ls -dt ~/eda_code_eval/*/ 2>/dev/null | head -1' 2>/dev/null | tr -d '\r')
  if [ -n "$latest_batch" ]; then
    local batch_id
    batch_id=$(basename "${latest_batch%/}")
    $SSH "cat ~/eda_code_eval/completed_code_generation_${batch_id}.jsonl 2>/dev/null" >"$dest/completed_code_generation.jsonl" 2>/dev/null || true
    # 也拷回 codegen_rejection_stats.json（如果存在）
    $SSH "find '$latest_batch' -maxdepth 3 -name 'codegen_rejection_stats.json' 2>/dev/null | head -1 | xargs -r cat 2>/dev/null" >"$dest/codegen_rejection_stats.json" 2>/dev/null || true
  fi

  local pr
  pr=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate', d.get('pass_rate','NA')))" 2>/dev/null || echo NA)
  log "[run $runidx] Pass@1=$pr （产物→ $dest）"

  # 验证：gen_success 和 pass count
  local gen_ok pass_count
  gen_ok=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));s=d.get('summary',{}).get('generation_statistics',{});print(s.get('success',0))" 2>/dev/null || echo "?")
  pass_count=$(python3 -c "import json;d=json.load(open('$dest/final_report.json'));print(d.get('summary',{}).get('total_correct_completions',0))" 2>/dev/null || echo "?")
  log "[run $runidx] gen_success=$gen_ok, correct=$pass_count"

  echo "$pr"
}

# ---- 主流程 ----
log "===== 干净 5-run 重跑 START (run2-5, 照抄 run1) ====="

declare -a PASS_RATES=()

# run1 已存在，直接读
pr1=$(python3 -c "import json;d=json.load(open('$RUN_DIR/attribution_3615_run1/final_report.json'));m=d.get('metrics',{});print(m.get('pass_rate', d.get('pass_rate','NA')))" 2>/dev/null || echo NA)
log "[run 1] 既有 Pass@1=$pr1 (attribution_3615_run1)"
PASS_RATES+=("$pr1")

for i in 2 3 4 5; do
  pr=$(run_one "$i")
  PASS_RATES+=("$pr")
done

log "5-run Pass@1 序列: ${PASS_RATES[*]}"

# ---- 简单统计 ----
python3 -c "
import json, sys
rates = []
for i, pr in enumerate(${PASS_RATES[@]@Q}, 1):
    try:
        rates.append(float(pr))
    except:
        rates.append(None)
valid = [r for r in rates if r is not None]
n = len(valid)
if n > 0:
    mean = sum(valid) / n
    if n > 1:
        var = sum((r - mean)**2 for r in valid) / (n - 1)
        std = var ** 0.5
    else:
        std = 0.0
    print(f'5-run mean = {mean*100:.2f}% ± {std*100:.2f}% (n={n})')
    print(f'per-run: {[\"{:.2f}%\".format(r*100) if r is not None else \"NA\" for r in rates]}')
else:
    print('No valid runs')
" >>"$LOG" 2>&1 || true

log "===== 干净 5-run 重跑 END ====="
