#!/usr/bin/env bash
# ============================================================
# baize-llm · 开跑前自检（只读，不改任何状态）
# 覆盖：路径 / launcher 特性 / 数据 blend / 节点与 GPU / 磁盘 / 端口 / 依赖
# 退出码：0=全部硬项 PASS；1=有 FAIL
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"
# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"

FAIL=0
ok()  { pass "$*"; }
bad() { err  "$*"; FAIL=$((FAIL + 1)); }

echo "===== baize-llm preflight @ $(ts) · host=$(hostname) ====="
echo "  BAIZE_LLM_HOME   = $BAIZE_LLM_HOME"
echo "  BAIZE_TRAIN_CODE = $BAIZE_TRAIN_CODE"
echo "  TOK_ROOT         = $TOK_ROOT"
echo "  name/seq/nodes   = $NAME / $SEQ / ${NNODES}x${NPROC_PER_NODE} (TP$TP CP$CP DP$DP)"

echo
echo "--- [1] 路径 ---"
[ -f "$BAIZE_TRAIN_CODE/pretrain_launcher.py" ] \
  && ok "pretrain_launcher.py 存在" || bad "缺 $BAIZE_TRAIN_CODE/pretrain_launcher.py"
[ -f "$TOKENIZER/tokenizer.json" ] \
  && ok "tokenizer 存在（$TOKENIZER）" || bad "缺 tokenizer：$TOKENIZER/tokenizer.json"
[ -d "$TOK_ROOT" ] && ok "TOK_ROOT 存在" || bad "缺 TOK_ROOT：$TOK_ROOT"
for f in "$PY/python" "$PY/torchrun"; do
  [ -x "$f" ] && ok "$f 可执行" || bad "缺 $f"
done
"$PY/python" - <<'EOF' 2>/dev/null && ok "python 可 import torch" || bad "python 无法 import torch"
import torch; print(f"torch {torch.__version__} cuda {torch.version.cuda} dev {torch.cuda.device_count()}")
EOF
[ -x "$PY/tensorboard" ] && ok "tensorboard 可执行（$PY/tensorboard）" || bad "缺 tensorboard（$PY/tensorboard）"

echo
echo "--- [2] launcher 特性（--help 探测）---"
H="$(launcher_help)"
[ -s "$H" ] && ok "已缓存 --help → $H" || bad "pretrain_launcher.py --help 失败（见 $H）"
for f in --optimizer --lr-decay-style --lr-warmup-iters --lr-decay-iters --min-lr \
         --global-batch-size --micro-batch-size --seq-length --context-parallel \
         --fp8-recipe --enable-cuda-graph; do
  has_flag "$f" && ok "支持 $f" || bad "launcher 不支持 $f"
done
if has_flag --lr-decay-shape; then
  ok "支持 --lr-decay-shape（D 段 exponential 可直接用）"
else
  bad "不支持 --lr-decay-shape ⇒ Decay 无法用指数衰减；按 docs/LAUNCHER_PATCH_EXP_DECAY.md 打补丁"
fi
has_flag --weight-decay && ok "支持 --weight-decay（可在 configs 设 0.1）" \
                        || warn "--weight-decay 未探测到，WEIGHT_DECAY 留空即可"

echo
echo "--- [3] 数据 blend（逐阶段）---"
for st in s1 s2 decay; do
  ( set +u
    source "$BAIZE_LLM_HOME/configs/common.env"
    # shellcheck disable=SC1090
    source "$BAIZE_LLM_HOME/configs/$st.env"
    TOTAL=$(( (ITERS - START_ITER) * GBS * SEQ ))
    "$PY/python" "$BAIZE_LLM_HOME/scripts/gen_blend.py" \
        --tsv "$BLEND_TSV" --tok-root "$TOK_ROOT" --verify --total-tokens "$TOTAL" >/dev/null
  )
  rc=$?
  case $rc in
    0) ok "blend $st 可构建" ;;
    2) bad "blend $st 数据缺失（阻塞：先补分词，见 run/data/DATA_MAPPING.md）" ;;
    *) bad "blend $st 生成失败（rc=$rc）" ;;
  esac
done

echo
echo "--- [4] 节点 / GPU ---"
gpus_free_local && ok "$(hostname) 8 卡空闲" \
  || bad "$(hostname) GPU 非空闲：$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"
if [ "$NNODES" -gt 1 ]; then
  if ssh_ok; then
    ok "ssh $MASTER_IP 可连"
    gpus_free_remote && ok "$MASTER_IP 空闲" \
      || bad "$MASTER_IP GPU 非空闲（vision 在用？train.sh 会 SKIP）"
  else
    bad "ssh $MASTER_IP 不可达（16 卡需它做 rank0；否则改 NNODES=1 单机 8 卡）"
  fi
fi

echo
echo "--- [5] 磁盘 / 端口 ---"
AVAIL=$(df -Pk /tmp | awk 'NR==2{print $4}')
[ "${AVAIL:-0}" -ge "$TMP_MIN_KB" ] && ok "/tmp 可用 $((AVAIL / 1024 / 1024))GB" \
  || bad "/tmp 可用 $((AVAIL / 1024 / 1024))GB < 5GB"
df -h /nas_train /nas_env 2>/dev/null | sed 's/^/      /'
used_port "$MASTER_PORT" && bad "MASTER_PORT=$MASTER_PORT 已被占用" || ok "MASTER_PORT=$MASTER_PORT 空闲"
used_port "$TB_PORT" && warn "TB_PORT=$TB_PORT 已被占用（若已是 tensorboard 则正常）" \
                     || ok "TB_PORT=$TB_PORT 空闲"

echo
echo "===== 结论：FAIL=$FAIL ====="
if [ "$FAIL" -eq 0 ]; then
  echo "✅ 硬项全通过 ⇒ 可跑 bash scripts/train.sh s1 --smoke 20"
else
  echo "❌ 有 $FAIL 个硬项未过 ⇒ 先修再开跑（不要带着 FAIL 起训练）"
  exit 1
fi
