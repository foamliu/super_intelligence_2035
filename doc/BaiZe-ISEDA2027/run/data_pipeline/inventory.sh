#!/bin/bash
# inventory.sh — phase0 实测盘点（轻量版，避免重 I/O 与下载抢带宽）
# 只做 ls / find -maxdepth / wc -l / du（单目录），不做全量递归扫描。
# 结果回写 DATA_LEDGER.md（由 agent 汇总），本脚本只负责打印实测数字。
set -u

L3QA=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa
OPENBMB=/nas_inference/app.e0031982/datasets/openbmb
MM=/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M
EN500K=/nas_train/app.e0031982/datasets/baize-vision/en500k
EVAL5K=/nas_train/app.e0031982/datasets/baize-vision/eval5k
EVAL_JSONL=/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027

echo "=== 通用文本：Ultra-FineWeb-L3 qa ==="
ls "$L3QA"/*.parquet 2>/dev/null | wc -l
du -sh "$L3QA" 2>/dev/null

echo "=== 通用文本：openbmb 目录 ==="
ls -1 "$OPENBMB" 2>/dev/null

echo "=== 退火源：UltraData-Code 语言分布 ==="
find "$OPENBMB/UltraData-Code/data" -maxdepth 3 -type d 2>/dev/null | sed 's#.*/##' | sort | uniq -c | head -40

echo "=== 多模态：LLaVA-OneVision 子集结构 ==="
for s in imagenet laioncn datacomp1b coyo mint obelics; do
  echo "[$s] EN/CN parquet 计数"
  for lang in EN CN; do
    n=$(find "$MM/$s/$lang" -maxdepth 3 -name '*.parquet' 2>/dev/null | wc -l)
    echo "  $lang: $n"
  done
done

echo "=== 多模态：已派生 en500k / eval5k ==="
ls -1 "$EN500K"/*.tar 2>/dev/null | wc -l
du -sh "$EN500K" 2>/dev/null
ls -1 "$EVAL5K"/*.tar 2>/dev/null | wc -l
du -sh "$EVAL5K" 2>/dev/null

echo "=== 评测集（只读，红线）==="
wc -l "$EVAL_JSONL"

echo "=== Round 1 派生数据（复用模板）==="
for f in ultrafineweb_l3_qa ultrafineweb_l3_qa_700m anneal_code anneal_math anneal_math2; do
  ls -la "$BASE/data/$f.bin" "$BASE/data/$f.idx" "$BASE/data/$f.json" 2>/dev/null
done
ls -d "$BASE/data/tokenizer_eod" 2>/dev/null