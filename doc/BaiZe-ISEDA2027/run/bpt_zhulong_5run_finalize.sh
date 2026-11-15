#!/bin/bash
# =====================================================================
# bpt_zhulong_5run_finalize.sh
# zhulong 口径 5-run 基线复测链完成后的「一键收口」脚本
# 2026-11-15 用户令：158 评测改用 zhulong 方式（36.15 eda_fastmcp）
#
# 用途：当 baize_posttrain_zhulong_baseline_5run_chain.sh 跑完 5 run 后，
#       本脚本一次性产出两份交付物：
#   ① 5run_zhulong_baseline_analysis.json   (mean±std + vs 旧 .17 step105 配对检验)
#   ② attribution_zhulong_5run_attribution.json (Q1-Q4 跨 5 run 聚合，run_commands 排除)
#
# 设计原则（与 08:1x 令一致）：
#   - 不改 eda_fastmcp 代码，只读 run/ 下本线产物
#   - run_commands 拒绝计入 hook 设计行为，不计入真 MCP 拒绝率
#   - 旧 .17 5-run 基线数据在 /tmp/posttrain_5run_eval/step105/run{1..5}
#   - robust to missing runs（只聚合存在的 run 产物）
#
# 用法：
#   bash bpt_zhulong_5run_finalize.sh [--num-runs 5]
# =====================================================================
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
NUM_RUNS="${1:-5}"
if [ "$1" = "--num-runs" ]; then NUM_RUNS="${2:-5}"; fi

cd "$RUN_DIR" || { echo "FATAL: cannot cd $RUN_DIR"; exit 2; }

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*"; }

BASE_PY="bpt_zhulong_baseline_5run_analysis.py"
ATTR_PY="bpt_zhulong_5run_attribution_aggregate.py"
BASE_OUT="5run_zhulong_baseline_analysis.json"
ATTR_OUT="attribution_zhulong_5run_attribution.json"
OLD_DIR="/tmp/posttrain_5run_eval/step105"

log "===== zhulong 口径 5-run 收口 START (num-runs=$NUM_RUNS) ====="

# ---- 前置：统计已有 run 产物 ----
present=0
for i in $(seq 1 "$NUM_RUNS"); do
  if [ -f "attribution_3615_run${i}/final_report.json" ]; then present=$((present+1)); fi
done
log "已有 final_report.json 的 run 数 = $present / $NUM_RUNS"
if [ "$present" -lt "$NUM_RUNS" ]; then
  log "⚠ 仍有 run 未完成（$present/$NUM_RUNS）——本脚本仍对已存在的 run 聚合（robust-to-missing）"
fi

# ---- ① 5-run 基线分析（mean±std + 配对检验 vs 旧 .17 step105）----
if [ -f "$BASE_PY" ]; then
  log "运行 ① $BASE_PY --num-runs $NUM_RUNS --out $BASE_OUT --old-dir $OLD_DIR"
  python3 "$BASE_PY" --run-dir "$RUN_DIR" --num-runs "$NUM_RUNS" --out "$BASE_OUT" --old-dir "$OLD_DIR" \
    > /tmp/bpt_zhulong_finalize_base.log 2>&1 || log "⚠ $BASE_PY 退出非0（见 /tmp/bpt_zhulong_finalize_base.log）"
  if [ -f "$BASE_OUT" ]; then
    delta=$(python3 -c "import json;d=json.load(open('$BASE_OUT'));print('delta_pp=',d.get('delta_pp'),'new_mean=',d.get('new_zhulong_baseline',{}).get('mean'),'old_mean=',d.get('old_17_baseline',{}).get('mean'))" 2>/dev/null || echo "parse-fail")
    log "① 产物 → $BASE_OUT  $delta"
  fi
else
  log "⚠ 缺 $BASE_PY"
fi

# ---- ② 5-run 归因聚合（Q1-Q4，run_commands 排除）----
if [ -f "$ATTR_PY" ]; then
  log "运行 ② $ATTR_PY --num-runs $NUM_RUNS --out $ATTR_OUT"
  python3 "$ATTR_PY" --run-dir "$RUN_DIR" --num-runs "$NUM_RUNS" --out "$ATTR_OUT" \
    > /tmp/bpt_zhulong_finalize_attr.log 2>&1 || log "⚠ $ATTR_PY 退出非0（见 /tmp/bpt_zhulong_finalize_attr.log）"
  if [ -f "$ATTR_OUT" ]; then
    q1=$(python3 -c "import json;d=json.load(open('$ATTR_OUT'));q=d.get('Q1_real_mcp_rejection_rate_exclude_run_commands',{});print('Q1_overall=',q.get('overall_real_mcp_rejection_rate'),'aggregate_over_n=',d.get('aggregate_over_n_runs_present'))" 2>/dev/null || echo "parse-fail")
    log "② 产物 → $ATTR_OUT  $q1"
  fi
else
  log "⚠ 缺 $ATTR_PY"
fi

# ---- 收口摘要（新旧基线同表）----
log "===== 新旧基线同表并列 ====="
python3 - "$BASE_OUT" "$ATTR_OUT" "$OLD_DIR" "$NUM_RUNS" <<'PYEOF' 2>/dev/null || log "摘要生成失败"
import json,sys,statistics,glob,os
base_out,attr_out,old_dir,num=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
def pr(path):
    try:
        d=json.load(open(path)); m=d.get('metrics',{})
        return m.get('pass_rate') if isinstance(m,dict) else None
    except Exception: return None
old_prs=[pr(f) for f in sorted(glob.glob(os.path.join(old_dir,'run*','final_report.json')))]
old_prs=[x for x in old_prs if x is not None]
new_prs=[]
for i in range(1,num+1):
    p=os.path.join(os.path.dirname(base_out) or '.',f'attribution_3615_run{i}','final_report.json')
    v=pr(p)
    if v is not None: new_prs.append(v)
def ms(xs):
    if not xs: return 'n=0'
    m=statistics.fmean(xs); s=statistics.pstdev(xs) if len(xs)>1 else 0.0
    return f'n={len(xs)} mean={m*100:.2f}% std={s*100:.2f}% vals={[round(x*100,2) for x in xs]}'
print(f"| 口径 | n | Pass@1 mean±std | 序列(%) |")
print(f"|---|---|---|---|")
print(f"| 旧=.17 非zhulong(无RAG/无沙盒,run_commands启用) | {ms(old_prs).split()[0].split('=')[1]} | {ms(old_prs).split('mean=')[1].split(' std')[0]}±{ms(old_prs).split('std=')[1].split(' vals')[0]} | {ms(old_prs).split('vals=')[1]} |")
print(f"| 新=36.15 zhulong口徑(PreToolUse hook,RAG+沙盒,run_commands禁用) | {ms(new_prs).split()[0].split('=')[1]} | {ms(new_prs).split('mean=')[1].split(' std')[0]}±{ms(new_prs).split('std=')[1].split(' vals')[0]} | {ms(new_prs).split('vals=')[1]} |")
if old_prs and new_prs:
    print(f"| Δ(new−old) | | {round((statistics.fmean(new_prs)-statistics.fmean(old_prs))*100,2)}pp | |")
PYEOF

log "===== zhulong 口径 5-run 收口 END ====="
log "交付物：$RUN_DIR/$BASE_OUT  +  $RUN_DIR/$ATTR_OUT"
log "下一步：把上表并入报告 §10（report_posttrain_zhulong_reattribution_zh.html）"
