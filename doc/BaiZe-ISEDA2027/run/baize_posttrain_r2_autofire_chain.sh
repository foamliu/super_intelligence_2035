#!/usr/bin/env bash
# baize_posttrain_r2_autofire_chain.sh -- Autonomous R2+sandbox-exec RL auto-fire chain.
#
# Purpose (用户令 2026-11-13 13:3x #4「换奖励/任务定义」+「追求显著提升」):
#   R0 (static string-match reward) 训练侧证据偏负（reward 平台 / mean_ratio==1.0 /
#   frac_nonzero_reward~1.0 区分度塌缩）。R2 (sandbox 执行 + 部分分) 是「追求显著提升」
#   主战场。本守护进程在 R0 的 5-run eval 完成后，**严格按预注册决策框架（§R425 C）**
#   自动分流：
#     分支1 (R0 显著优于 SFT step105 基线)  -> 不自动起 R2，留待 agent 写里程碑报告
#     分支2 (R0 无显著提升 / 退化 / eval 失败) -> 杀掉 R0 eval 在 GPU7:8095 的残留
#        vLLM serve -> 释放 GPU7 -> 自动起 R2+sandbox-exec 200 步主训（不再搁置）
#
# 决策判据（与 §R425 C 一致，先定后测，红线 §5 预注册）：
#   baseline = SFT step105 5-run mean (锁定 0.0304±0.0083)
#   分支1 = R0_mean > baseline_mean 且 (McNemar p<0.05 且 b>c  或  bootstrap ci_low>0)
#   否则   = 分支2
#   (bootstrap observed_diff = R0 - baseline；ci_low>0 即 R0 显著更好。
#    McNemar b = R0 pass&baseline fail，c = baseline pass&R0 fail；b>c 即 R0 净更好。)
#
# 并发安全：R2 用 GPU7(HF 直载 policy，无需 vLLM serve)+沙盒(隧道)；residual SFT eval 用
#   GPU4/5+providers.json，不碰 GPU7/沙盒 ⇒ 可并发，无争用。
#
# 报告口径：替身预演，收益不可迁移到 BaiZe。
# 红线：anti-cheat 全程开（grpo loop 内置 n-gram cheat 检测，cheat_rate.json 落盘）；
#   污染隔离 rl_pyaether_synth_v2.parquet 已验 0/3347（§5.1）。
#
# Usage (background, fire-and-forget after launching the R0 eval chain):
#   nohup bash baize_posttrain_r2_autofire_chain.sh \
#     --rl-eval-chain-pid 2028723 --gpu 7 --port 8095 \
#     > /tmp/posttrain_r2_autofire_chain.log 2>&1 &
#
#   bash baize_posttrain_r2_autofire_chain.sh --dry-run    # print recipe only
#   bash baize_posttrain_r2_autofire_chain.sh --status     # show wait/decision status
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GRPO_LOOP="$SCRIPT_DIR/baize_posttrain_rl_grpo_loop.py"
VENV_PY="${HOME}/code/verl_cu124_venv/bin/python"
ANALYSIS_JSON="/tmp/posttrain_5run_eval/5run_rl_analysis.json"

RL_EVAL_CHAIN_PID="2028723"
GPU="7"
PORT="8095"
BASE_MEAN="0.0304"
SFT_CKPT="$SCRIPT_DIR/sft_surrogate_runs/minicpm5_agentic_v39_pretok/global_step_105"
R2_OUTDIR="$SCRIPT_DIR/rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step"
R2_LOG="/tmp/grpo_loop_R2_sandbox_200step.log"
DRY_RUN=0; STATUS_ONLY=0
MAX_WAIT_S=$((30 * 3600))   # 30h safety cap; if R0 eval chain stuck, force-decide

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)            DRY_RUN=1 ;;
    --status)             STATUS_ONLY=1 ;;
    --rl-eval-chain-pid)  RL_EVAL_CHAIN_PID="$2"; shift ;;
    --gpu)                GPU="$2"; shift ;;
    --port)               PORT="$2"; shift ;;
    --base-mean)          BASE_MEAN="$2"; shift ;;
    --sft-ckpt)           SFT_CKPT="$2"; shift ;;
    --r2-outdir)          R2_OUTDIR="$2"; shift ;;
    *) echo "unknown: $1"; exit 1 ;;
  esac
  shift
done

# ---- helpers ---------------------------------------------------------------

# Kill any vLLM api_server serve occupying GPU<GPU> (frees the card).
kill_gpu_serve() {
  local g="$1"
  local pids
  pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits -i "$g" 2>/dev/null | tr -d ' ')
  [ -z "$pids" ] && { echo "[r2-chain] GPU${g} already free (no compute-apps)."; return 0; }
  for pid in $pids; do
    local cmd
    cmd=$(ps -o args= -p "$pid" 2>/dev/null)
    if echo "$cmd" | grep -q "vllm.entrypoints.openai.api_server"; then
      echo "[r2-chain] killing vLLM serve PID $pid on GPU${g}..."
      kill -TERM "$pid" 2>/dev/null || true; sleep 4
      kill -9 "$pid" 2>/dev/null || true
    else
      echo "[r2-chain] GPU${g} PID $pid is not vLLM serve (skip): ${cmd:0:70}"
    fi
  done
}

wait_gpu_free() {
  local g="$1" i
  for i in $(seq 1 40); do
    local used
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$g" 2>/dev/null | tr -d ' ')
    if [ -z "$used" ] || [ "$used" -lt 1000 ]; then
      echo "[r2-chain] GPU${g} free (memory.used=${used}MiB) after ${i}x6s"
      return 0
    fi
    sleep 6
  done
  echo "[r2-chain] WARN: GPU${g} still not free after 4min (will attempt launch anyway)"
  return 0
}

# A GRPO loop already running? (idempotency guard)
grpo_already_running() {
  pgrep -f "baize_posttrain_rl_grpo_loop.py" >/dev/null 2>&1 && return 0
  return 1
}

# Read the pre-registered decision from ANALYSIS_JSON.
# Prints exactly one line: "BRANCH1 ..." or "BRANCH2 ..."
# Exit code 0 = BRANCH2 (fire R2), 10 = BRANCH1 (do not fire).
decide_branch() {
  python3 - "$ANALYSIS_JSON" "$BASE_MEAN" <<'PYEOF'
import json, os, sys
path, base_default = sys.argv[1], float(sys.argv[2])
if not os.path.exists(path):
    print("BRANCH2 analysis_json_missing -> R0 eval failed/incomplete; fire R2 (不再搁置)")
    sys.exit(0)
try:
    d = json.load(open(path))
except Exception as e:
    print("BRANCH2 analysis_json_parse_error:%s -> fire R2" % e)
    sys.exit(0)
r0_label = None
for k in d:
    if k in ("comparison", "step105"):
        continue
    r0_label = k; break
if r0_label is None:
    print("BRANCH2 no_r0_label -> fire R2")
    sys.exit(0)
r0 = d.get(r0_label, {})
base = d.get("step105", {})
r0_mean = r0.get("mean")
base_mean = base.get("mean", base_default)
if r0_mean is None:
    print("BRANCH2 r0_mean_missing -> fire R2")
    sys.exit(0)
cmp = d.get("comparison", {})
mc = cmp.get("mcnemar", {})
bo = cmp.get("bootstrap", {})
mc_p = mc.get("p_value")
mc_b = mc.get("b", 0)
mc_c = mc.get("c", 0)
ci_low = bo.get("ci_low")
sig_mc = (mc_p is not None and mc_p < 0.05 and mc_b > mc_c)
sig_boot = (ci_low is not None and ci_low > 0)
better = (r0_mean > base_mean)
detail = "r0_mean=%.4f base_mean=%.4f mcnemar(b=%s c=%s p=%s) boot(ci_low=%s diff=%s)" % (
    r0_mean, base_mean, mc_b, mc_c, mc_p, ci_low, bo.get("observed_diff"))
if better and (sig_mc or sig_boot):
    print("BRANCH1 %s -> R0 significant improvement; NOT firing R2; await milestone report" % detail)
    sys.exit(10)
print("BRANCH2 %s -> R0 not significant/regression; fire R2+sandbox-exec" % detail)
sys.exit(0)
PYEOF
}

# ---- status ----------------------------------------------------------------
if [ $STATUS_ONLY -eq 1 ]; then
  echo "[status] R0 eval-chain PID=$RL_EVAL_CHAIN_PID: $(kill -0 "$RL_EVAL_CHAIN_PID" 2>/dev/null && echo RUNNING || echo DONE)"
  echo "[status] analysis json: $ANALYSIS_JSON ($(test -f "$ANALYSIS_JSON" && echo EXISTS || echo MISSING))"
  echo "[status] GPU${GPU} port ${PORT}:"
  curl -s --max-time 3 "http://localhost:${PORT}/v1/models" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  (not serving)"
  echo "[status] R2 GRPO loop running: $(pgrep -f 'baize_posttrain_rl_grpo_loop.py' >/dev/null 2>&1 && echo YES || echo NO)"
  echo "[status] decision (if json present):"
  decide_branch || true
  exit 0
fi

echo "===== R2 Auto-fire Chain Daemon @ $(date '+%F %T') ====="
echo "  rl-eval-chain-pid=$RL_EVAL_CHAIN_PID  gpu=$GPU  port=$PORT  base-mean=$BASE_MEAN"
echo "  sft-ckpt=$SFT_CKPT"
echo "  r2-outdir=$R2_OUTDIR  r2-log=$R2_LOG"
echo "  decision-framework: §R425 C (branch1=significant->wait; branch2=not/regression->fire R2)"

if [ $DRY_RUN -eq 1 ]; then
  echo "[dry-run] Would: wait R0 eval-chain PID $RL_EVAL_CHAIN_PID (<=${MAX_WAIT_S}s) ->"
  echo "[dry-run]   read $ANALYSIS_JSON -> decide branch1/branch2 (§R425 C) ->"
  echo "[dry-run]   branch2: kill GPU${GPU}:${PORT} serve -> wait GPU${GPU} free ->"
  echo "[dry-run]   fire: CUDA_VISIBLE_DEVICES=$GPU $VENV_PY $GRPO_LOOP --reward-arm R2 --sandbox-exec"
  echo "[dry-run]     --sft-ckpt $SFT_CKPT --total-steps 200 --output-dir $R2_OUTDIR"
  exit 0
fi

# ---- 1. wait for R0 eval chain to finish (or safety cap) -------------------
echo "[r2-chain] Waiting for R0 eval chain (PID $RL_EVAL_CHAIN_PID) to finish..."
elapsed=0
while kill -0 "$RL_EVAL_CHAIN_PID" 2>/dev/null; do
  if [ "$elapsed" -ge "$MAX_WAIT_S" ]; then
    echo "[r2-chain] SAFETY CAP: ${MAX_WAIT_S}s reached; R0 eval chain still alive -> force-decide"
    break
  fi
  sleep 180; elapsed=$((elapsed + 180))
  echo "[r2-chain]   R0 eval-chain still running ($(date '+%T'), ${elapsed}s)... sleeping 180s"
done
echo "[r2-chain] R0 eval chain finished (or cap hit) at $(date '+%F %T')"

# ---- 2. decide branch (pre-registered §R425 C) -----------------------------
echo "[r2-chain] === Decision gate (§R425 C) @ $(date '+%F %T') ==="
DECISION_LINE="$(decide_branch)"
RC=$?
echo "[r2-chain] $DECISION_LINE (rc=$RC)"

if [ "$RC" -eq 10 ]; then
  echo "[r2-chain] BRANCH1: R0 achieved significant improvement over SFT baseline."
  echo "[r2-chain] Per pre-registered framework (§R425 C), NOT auto-firing R2."
  echo "[r2-chain] Awaiting agent wake to write milestone report reports/report_posttrain_rl_surrogate_zh.html"
  echo "[r2-chain] (R2 may still be launched manually as an ablation arm if desired.)"
  echo "[r2-chain] === R2 auto-fire chain DONE (branch1, no R2) ==="
  exit 0
fi

# ---- 3. branch2: free GPU7, then fire R2 -----------------------------------
echo "[r2-chain] BRANCH2: R0 no significant improvement -> firing R2+sandbox-exec (追求显著提升 主战场)."

# idempotency: don't double-launch
if grpo_already_running; then
  echo "[r2-chain] A GRPO loop is already running -> skip launch (idempotency)."
  echo "[r2-chain] === R2 auto-fire chain DONE (R2 already running) ==="
  exit 0
fi

# free GPU: kill the R0 eval serve left running on GPU:PORT
echo "[r2-chain] Freeing GPU${GPU} (killing R0 eval serve on :${PORT})..."
kill_gpu_serve "$GPU"
wait_gpu_free "$GPU"

# ---- 4. launch R2+sandbox-exec 200-step main training ----------------------
mkdir -p "$R2_OUTDIR"
echo "[r2-chain] === Launching R2+sandbox-exec GRPO @ $(date '+%F %T') ==="
echo "[r2-chain]   venv=$VENV_PY  gpu=$GPU  sft-ckpt=$SFT_CKPT"
echo "[r2-chain]   outdir=$R2_OUTDIR  log=$R2_LOG"
cd "$SCRIPT_DIR"
CUDA_VISIBLE_DEVICES="$GPU" nohup "$VENV_PY" "$GRPO_LOOP" \
  --reward-arm R2 --sandbox-exec \
  --sandbox-ports 8664,8665,8653,8669 --sandbox-timeout 60 \
  --sft-ckpt "$SFT_CKPT" \
  --total-steps 200 --group-size 8 --batch-prompts 2 --save-freq 50 \
  --lr 3e-6 --kl-coef 0.02 \
  --output-dir "$R2_OUTDIR" \
  > "$R2_LOG" 2>&1 &
R2_PID=$!
echo "[r2-chain] R2 GRPO launched: PID=$R2_PID at $(date '+%F %T')"
echo "[r2-chain] Monitor: tail -f $R2_LOG"
echo "[r2-chain] Dynamics will land: $R2_OUTDIR/*training_dynamics.json + cheat_rate.json"
echo "[r2-chain] === R2 auto-fire chain DONE (R2 launched, branch2) ==="
