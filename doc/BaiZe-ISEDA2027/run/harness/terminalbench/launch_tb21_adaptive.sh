#!/usr/bin/env bash
# launch_tb21_adaptive.sh — TB-2.1 重跑「自适应并发」封装（2026-11-15 用户令）
#
# 用户令：周末并发开高一些；评测要有放量/回退——
#   长鑫工作时间 08:30-17:30 内遇 429 就减并发；工作时间之外一段时间没有 429 就加并发。
#
# 用法：
#   bash launch_tb21_adaptive.sh --harness opencode --task-list manifests/tb21_7way_rerun_opencode_xxx.txt
#   HARNESS_CHUNK_SIZE=8 bash launch_tb21_adaptive.sh --harness pi --task-list ...
#
# 说明：
#   * 并发由 run/harness/adaptive_concurrency.py 计算（work 上限 4 / off 上限 10）
#   * 每块跑完扫日志中的 429/quota，自动记录并按策略升降，下一块生效
#   * 纯查看当前建议并发：python3 ../adaptive_concurrency.py status
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHUNK="${HARNESS_CHUNK_SIZE:-12}"

echo "[adaptive-launch] chunk=$CHUNK  (状态: python3 ${HERE}/../adaptive_concurrency.py status)"
exec python3 "${HERE}/rerun_tb21_cline_quota.py" \
    --launch --n-concurrent auto --chunk-size "${CHUNK}" "$@"
