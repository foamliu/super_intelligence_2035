#!/usr/bin/env bash
# baize_posttrain_contamination_gate.sh — BaiZe Stage(ii) 污染隔离闸门（红线 P1-e）
#
# 用途：在任何 post-train 合成数据（SFT synth / RL synth / PyAether 退火语料）投料或训练前，
#       用 EDA-Eval 评测黑名单逐条扫描，命中即剔除并阻断训练（总纲 §5.1 红线：158 任务禁入训练集）。
#
# 机制（复用 data 线已验证的 check_contamination.py + build_blacklist.py；累计 220,000 docs 0 命中）：
#   - 黑名单来源：6 个评测快照并集 536 任务（含 v20260311 的 158 任务）的 13-gram FNV-1a 64-bit 哈希集
#     + 短文本 8-gram 兜底 + entry_point sha256 + MinHash(k=128) 溯源签名。
#   - 命中判定：13-gram 重合率 ≥ 0.80，或短 8-gram 兜底重合数 ≥ 1（覆盖中文短 prompt / 嵌在长文档里的短串）。
#   - 命中文档必须剔除（改写不洗白）；任一输入命中数 > 0 ⇒ 闸门 FAIL（exit 2），阻断训练。
#
# 规则（CONTAMINATION_CHECK.md §1，post-train 专用复述）：
#   - ✅ 允许入训练：PyAether / SKILL 的 API 参考文档（函数签名 / 参数说明 / 示例）——任务的"来源材料"。
#   - ❌ 禁止入训练：评测任务的 prompt / entry_point / canonical_solution / test 断言，及其改写版。
#   - 合成训练对（SFT/RL）时：从 API 文档合成允许，但合成产物必须过本闸；任何与 158 任务指纹重合的
#     合成对一律剔除。RL 的 rl_pyaether_synth_tasks.jsonl 同闸，🚫 禁用 158 评测题原题。
#
# 用法：
#   bash baize_posttrain_contamination_gate.sh --dry-run
#   bash baize_posttrain_contamination_gate.sh --dry-run --sft-synth /p/sft.jsonl --rl-synth /p/rl.jsonl
#   bash baize_posttrain_contamination_gate.sh --sft-synth <j> --rl-synth <j> --anneal-corpus <d|j> --out /tmp/r.md
#   bash baize_posttrain_contamination_gate.sh --build-blacklist --eval-jsonl <v20260311.jsonl> [其它快照...]
#
# 退出码：0 = 通过(0 命中,可投料)；2 = 失败(有命中,阻断训练)；3 = 闸门自身不可用(fail-safe)。
set -uo pipefail

# Auto-detect NFS root (.17 → /nas_data, .29/.12 → /nas_train)
if [ -d "/nas_data/app.e0031982/code/super_intelligence_2035" ] && [ ! -d "/nas_train/app.e0031982/code/super_intelligence_2035" ]; then
    RUN_DIR=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
elif [ -d "/nas_train/app.e0031982/code/super_intelligence_2035" ]; then
    RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
else
    RUN_DIR=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
fi
BLACKLIST_DIR="${BLACKLIST_DIR:-$RUN_DIR/data_pipeline/blacklist}"
CHECK_PY="$RUN_DIR/data_pipeline/check_contamination.py"
BUILD_PY="$RUN_DIR/data_pipeline/build_blacklist.py"

NGRAM=13; SHORT_NGRAM=8; THRESHOLD=0.8; MINHASH_K=128
OUT="${OUT:-/tmp/baize_posttrain_contam_gate_$(date +%s).md}"
DRY_RUN=0; BUILD_ONLY=0

declare -a IN_PATHS=() IN_LABELS=()
declare -a EVAL_JSONLS=()
add_input() { IN_PATHS+=("$2"); IN_LABELS+=("$1"); }
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --build-blacklist) BUILD_ONLY=1 ;;
    --sft-synth)      add_input "sft-synth"      "$2"; shift ;;
    --rl-synth)       add_input "rl-synth"       "$2"; shift ;;
    --anneal-corpus)  add_input "anneal-corpus"  "$2"; shift ;;
    --input)          add_input "input"          "$2"; shift ;;
    --blacklist-dir)  BLACKLIST_DIR="$2"; shift ;;
    --ngram)          NGRAM="$2"; shift ;;
    --threshold)      THRESHOLD="$2"; shift ;;
    --out)            OUT="$2"; shift ;;
    --eval-jsonl)     EVAL_JSONLS+=("$2"); shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

# ---------- --build-blacklist：从评测 jsonl（可多个，并集）重建黑名单 ----------
if [ "$BUILD_ONLY" -eq 1 ]; then
  if [ "${#EVAL_JSONLS[@]}" -eq 0 ]; then echo "[gate] --build-blacklist 需要至少一个 --eval-jsonl" >&2; exit 3; fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[DRY-RUN] 将重建黑名单 → $BLACKLIST_DIR ；eval-jsonl=${EVAL_JSONLS[*]} ；ngram=$NGRAM short=$SHORT_NGRAM minhash_k=$MINHASH_K"; exit 0
  fi
  if [ ! -f "$BUILD_PY" ]; then echo "[gate] 缺 build_blacklist.py: $BUILD_PY" >&2; exit 3; fi
  echo "[gate] 重建黑名单 → $BLACKLIST_DIR"
  python3 "$BUILD_PY" --eval-jsonl "${EVAL_JSONLS[@]}" --out-dir "$BLACKLIST_DIR" \
    --ngram "$NGRAM" --short-ngram "$SHORT_NGRAM" --minhash-k "$MINHASH_K" || exit 3
  echo "[gate] 黑名单已重建：$BLACKLIST_DIR"; exit 0
fi
# ---------- 闸门主流程 ----------
cat <<EOF
===== BaiZe Stage(ii) 污染隔离闸门 @ $(date '+%F %T') =====
  blacklist_dir   : ${BLACKLIST_DIR}  (6 快照并集 / 536 任务 / 含 v20260311 的 158)
  checker         : ${CHECK_PY}
  命中判定        : 13-gram 重合率 ≥ ${THRESHOLD}  或  短 ${SHORT_NGRAM}-gram 兜底重合 ≥ 1
  输入数          : ${#IN_PATHS[@]}
  报告            : ${OUT}
  红线            : 158 任务(prompt/entry_point/test/断言)禁入训练集；改写不洗白；命中即剔除+阻断训练
EOF
if [ "${#IN_PATHS[@]}" -eq 0 ]; then echo "  (无 --sft-synth/--rl-synth/--anneal-corpus/--input 输入 ⇒ 仅打印配方)"; fi

if [ "$DRY_RUN" -eq 1 ]; then
  for i in "${!IN_PATHS[@]}"; do echo "  · [${IN_LABELS[$i]}] 将扫描: ${IN_PATHS[$i]}"; done
  echo "===== DRY-RUN：不扫描、不读写黑名单、exit 0 ====="; exit 0
fi

# 真跑前置：黑名单 + checker 必须在位（fail-safe）
if [ ! -f "$CHECK_PY" ]; then echo "[gate][FAIL-SAFE] 缺 check_contamination.py: $CHECK_PY" >&2; exit 3; fi
if [ ! -d "$BLACKLIST_DIR" ] || [ ! -f "$BLACKLIST_DIR/meta.json" ]; then
  echo "[gate][FAIL-SAFE] 黑名单不可用: $BLACKLIST_DIR/meta.json 缺失（先用 --build-blacklist 生成）" >&2; exit 3
fi

mkdir -p "$(dirname "$OUT")"; : > "$OUT"
{ echo "# BaiZe Stage(ii) 污染隔离闸门报告（自动生成）"; echo ""
  echo "- 黑名单：${BLACKLIST_DIR}（6 快照并集 536 任务，含 v20260311 的 158）"
  echo "- 命中判定：13-gram 重合率 ≥ ${THRESHOLD} 或短 ${SHORT_NGRAM}-gram 兜底重合 ≥ 1"
  echo "- 时间：$(date '+%F %T')"; echo ""
  echo "| 标签 | 输入 | 扫描文档数 | 命中(污染)数 | 状态 |"; echo "|:--|:--|--:|--:|:--|"; } >> "$OUT"

TOTAL_FLAGGED=0; TOTAL_SCANNED=0; FAIL=0
for i in "${!IN_PATHS[@]}"; do
  label="${IN_LABELS[$i]}"; inp="${IN_PATHS[$i]}"; rep="/tmp/pt_contam_${label}_$$.md"
  echo "[gate] 扫描 [${label}] ${inp} ..."
  if ! python3 "$CHECK_PY" --blacklist-dir "$BLACKLIST_DIR" --input "$inp" \
        --ngram "$NGRAM" --threshold "$THRESHOLD" --out "$rep" >/tmp/pt_contam_stdout_$$.log 2>&1; then
    echo "[gate][FAIL-SAFE] check_contamination.py 执行失败（见 /tmp/pt_contam_stdout_$$.log）" >&2
    { echo "| ${label} | ${inp} | ERR | ERR | ❌ checker 失败(阻断) |"; } >> "$OUT"; FAIL=1; continue
  fi
  scanned=$(grep -oE '扫描文档数：[0-9]+' "$rep" | head -1 | grep -oE '[0-9]+$')
  flagged=$(grep -oE '命中（污染）文档数：[0-9]+' "$rep" | head -1 | grep -oE '[0-9]+$')
  scanned="${scanned:-0}"; flagged="${flagged:-0}"
  TOTAL_SCANNED=$((TOTAL_SCANNED + scanned)); TOTAL_FLAGGED=$((TOTAL_FLAGGED + flagged))
  st="✅ 通过"; [ "$flagged" -gt 0 ] && { st="❌ 命中(阻断)"; FAIL=1; }
  { echo "| ${label} | ${inp} | ${scanned} | ${flagged} | ${st} |"; } >> "$OUT"
  echo "[gate]   扫描 ${scanned} / 命中 ${flagged} → ${st}"
  [ -f "$rep" ] && cat "$rep" >> "$OUT"; rm -f "$rep"
done
rm -f /tmp/pt_contam_stdout_$$.log

{ echo ""; echo "## 汇总"; echo "- 总扫描文档数：${TOTAL_SCANNED}"
  echo "- **总命中（污染）文档数：${TOTAL_FLAGGED}**"
  if [ "$TOTAL_FLAGGED" -gt 0 ]; then
    echo "- ⚠️ 闸门 **FAIL**：检测到 ${TOTAL_FLAGGED} 个污染文档，必须剔除后再投料；改写不洗白。"
  else
    echo "- ✅ 闸门 **PASS**：0 命中，合成数据与 158 评测任务不同源，可投料。"
  fi; } >> "$OUT"
echo "[gate] 报告 → ${OUT}"
if [ "$FAIL" -eq 1 ]; then echo "[gate] 闸门 FAIL（有命中或 checker 失败）→ 阻断训练" >&2; exit 2; fi
echo "[gate] 闸门 PASS（0 命中）→ 可投料"; exit 0

