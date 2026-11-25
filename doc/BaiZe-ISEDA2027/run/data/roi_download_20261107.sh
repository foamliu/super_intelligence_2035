#!/usr/bin/env bash
# roi_download_20261107.sh — 2026-11-07 运维令：代码语料放行 + ROI 自排优先级下载
# 落盘 /nas_inference/app.e0031982/datasets/<repo原名>/
# 纪律：setsid 后台 / nice / --max-workers 4 / 走代理 / 断点续传
set -euo pipefail

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export HTTPS_PROXY="http://172.19.92.25:13128"
export https_proxy="$HTTPS_PROXY"
export HTTP_PROXY="$HTTPS_PROXY"
export http_proxy="$HTTPS_PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0

BASE="/nas_inference/app.e0031982/datasets"
LOG="/tmp/data_download_roi_20261107.log"
STATUS_TSV="/tmp/data_download_roi_status.tsv"

echo "==== ROI download start $(date '+%Y%m%d_%H%M%S') ====" | tee "$LOG"
echo -e "repo_id\tstatus\tfiles\tbytes\tincomplete\tattempts" > "$STATUS_TSV"

# 下载函数：$1=repo_id $2=local_subdir $3=note
dl() {
    local repo="$1" subdir="$2" note="$3" attempts=1
    local dest="$BASE/$subdir"
    echo "[dl] $repo -> $dest ($note)" | tee -a "$LOG"
    mkdir -p "$dest"
    while true; do
        if nice -n 10 hf download "$repo" \
            --repo-type dataset \
            --local-dir "$dest" \
            --max-workers 4 \
            >> "$LOG" 2>&1 ; then
            local nfiles incs bytes
            nfiles=$(find "$dest" -type f ! -path '*/.cache/*' | wc -l)
            incs=$(find "$dest" -name '*.incomplete' | wc -l)
            bytes=$(du -sb "$dest" 2>/dev/null | cut -f1)
            echo -e "${repo}\tOK\t${nfiles}\t${bytes}\t${incs}\t${attempts}" >> "$STATUS_TSV"
            echo "[dl] $repo OK files=$nfiles bytes=$bytes incs=$incs" | tee -a "$LOG"
            break
        else
            attempts=$((attempts+1))
            if [ $attempts -le 3 ]; then
                echo "[dl] $repo FAILED attempt=$((attempts-1)), retry $attempts/3..." | tee -a "$LOG"
                sleep 10
            else
                echo -e "${repo}\tFAIL\t0\t0\t-1\t${attempts}" >> "$STATUS_TSV"
                echo "[dl] $repo FAILED after 3 attempts" | tee -a "$LOG"
                break
            fi
        fi
    done
}

# === ROI 高→低 排序下载 ===

# T1: utter-project/LongBlocks (9.57 GB) — 多语言长上下文 QA + 教师蒸馏
dl "utter-project/LongBlocks" "utter-project/LongBlocks" "长上下文QA 194K 20语言含中文"

# T1: nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1 (5.10 GB) — agentic SWE step-level RL
dl "nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1" "nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1" "agentic SWE RL step-level reward 33.8K rows"

# T1: caskcsg/NExtLong-Instruct-Magpie-Llama-3 (2.89 GB) — 合成长上下文训练集 100%≥64K
dl "caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1" "caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1" "合成长上下文 1M样本 64K/128K/256K/512K子集"

# T2: common-pile/arxiv_papers_filtered (6.04 GB) — 版权干净论文全文
dl "common-pile/arxiv_papers_filtered" "common-pile/arxiv_papers_filtered" "arxiv论文全文 CC BY/SA/CC0"

# T2: THUDM/LongWriter-6k (0.15 GB) — 长输出生成 SFT
dl "THUDM/LongWriter-6k" "THUDM/LongWriter-6k" "长输出生成SFT 6K样本 2K-20K words"

# T2: NovaSky-AI/SkyRL-v0-293-data (0.002 GB) — RL pipeline 验证
dl "NovaSky-AI/SkyRL-v0-293-data" "NovaSky-AI/SkyRL-v0-293-data" "RL验证 293 train tasks SWE-Gym"

# T3: Nethraaaaa81/swev-trm-trajectories-25models (0.93 GB) — TRM分析（高污染风险）
dl "Nethraaaaa81/swev-trm-trajectories-25models" "Nethraaaaa81/swev-trm-trajectories-25models" "SWE轨迹TRM训练 25模型 高污染"

# T3: zai-org/LongBench-v2 (0.47 GB) — ⚠️评测集 仅去污染 禁入训练
dl "zai-org/LongBench-v2" "zai-org/LongBench-v2" "⚠️评测集 503 MCQ 仅去污染禁入训练"

echo "==== ROI download FINISH $(date '+%Y%m%d_%H%M%S') ====" | tee -a "$LOG"
echo "Status TSV: $STATUS_TSV" | tee -a "$LOG"
cat "$STATUS_TSV" | tee -a "$LOG"
