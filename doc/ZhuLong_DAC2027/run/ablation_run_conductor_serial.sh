#!/bin/bash
# 十一假期串行执行总控脚本（单机版）
# 按 README §8 建议顺序：S1 保真度 → 组件消融 → S2 Φ → 模型消融
# 每个阶段串行，阶段内 loop 自驱 8 并发。
#
# ⚡ 关于「沙箱阻断」的预期行为：
#    loop 每 30min 唤醒 agent → agent 执行 pgrep 检查：
#      - eval cline 活跃 → pgrep 有输出 → 反作弊 PreToolUse 拦截 run_commands（ACCESS RESTRICTED）
#        → agent 判定「还在跑」，什么都不做退出。这是正确的，不是故障。
#      - eval 结束 → pgrep 无输出 → 工具恢复可用 → agent 打分、推进。
#    所以「run_commands 被禁」恰恰说明 eval 进程正常运作中，无需任何人工干预。
#
# 启动方式（脱离进程组）:
#   setsid bash /nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_conductor_serial.sh > /tmp/ablation_conductor.log 2>&1 < /dev/null &
set -euo pipefail

BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run"
CONDUCTOR_LOG="/tmp/ablation_conductor.log"

log() {
    echo "[conductor] $(date '+%F %T') $*"
}

require() {
    local f="$1"
    if [[ ! -f "$BASE/$f" ]]; then
        log "❌ 缺失依赖文件: $BASE/$f —— 已停止(不空跑)。"
        exit 1
    fi
}

log "========== 十一假期串行执行开始 =========="
log "机器: 10.251.36.15"
log "预计总耗时: ~10-11 天（75 轮 × ~3.5h/轮，含 30min 轮询粒度；模型阶段可节后续跑）"
log ""

# 启动前预检：所有 loop / task book 必须就绪，缺失即停（不空跑）。
require "ablation_run_loop_s1_full.sh";           require "ablation_run_task_s1_full.md"
require "ablation_run_loop_component_s2_full.sh"; require "ablation_run_task_component_s2_full.md"
require "ablation_run_loop_model_full.sh";        require "ablation_run_task_model_full.md"
log "预检通过：所有 loop / task book 就绪。"
log ""

# ────────────────────────────────────────────
# 阶段 1: S1 保真度消融（流 A）
#   omega_low ×5 → readback_binary ×5 → readback_none ×5 = 15 轮
#   MEMORY: MEMORY_s1_full.md
#   ~2 天
# ────────────────────────────────────────────
log "=== 阶段 1/4: S1 保真度消融（omega_low → binary → none）==="
log "启动 loop: $BASE/ablation_run_loop_s1_full.sh"
bash "$BASE/ablation_run_loop_s1_full.sh"
log "=== 阶段 1/4 完成 ==="
log ""

# ────────────────────────────────────────────
# 阶段 2: 组件消融（流 C Phase 1，含 full 锚点）
#   pure_llm ×5 → rag ×5 → wo_retrieval ×5 → full ×5 = 20 轮
#   MEMORY: MEMORY_component_full.md
#   ~2.5 天（full 是锚点，喂 5 张表的锚点行）
# ────────────────────────────────────────────
log "=== 阶段 2/4: 组件消融（pure_llm → rag → wo_retrieval → full 锚点）==="
log "启动 loop: $BASE/ablation_run_loop_component_s2_full.sh"
log "（此 loop 含 Phase 1 组件 + Phase 2 S2 Φ，自动切换）"
bash "$BASE/ablation_run_loop_component_s2_full.sh"
log "=== 阶段 2/4 完成 ==="
log ""

# ────────────────────────────────────────────
# 阶段 3: S2 Φ 轴（流 C Phase 2 — 已在阶段 2 的 loop 中自动衔接）
#   说明：component_s2_full 的 loop 会先从 Phase 1 组件消融开始，
#   完成后自动切到 Phase 2（phi_k10 → k3 → k1 → lagged），
#   所以阶段 2 的 loop 退出时，组件+S2 全部完成。
# ────────────────────────────────────────────
log "组件+S2 已在阶段 2 完成 ✓（component_s2_full loop 自驱 Phase 1→Phase 2 过渡）"
log ""

# ────────────────────────────────────────────
# 阶段 4: 模型消融（流 B）
#   glm-5.2 ×5 → ds-v4-flash ×5 → kimi ×5 → doubao ×5 = 20 轮
#   MEMORY: MEMORY_model_full.md
#   ~2.5 天
# ────────────────────────────────────────────
log "=== 阶段 4/4: 模型消融（glm → flash → kimi → doubao）==="
log "启动 loop: $BASE/ablation_run_loop_model_full.sh"
bash "$BASE/ablation_run_loop_model_full.sh"
log "=== 阶段 4/4 完成 ==="
log ""

# ────────────────────────────────────────────
log "========== 全部试验完成 $(date '+%F %T') =========="
log "检查各 MEMORY 文件确认成绩："
for f in MEMORY_s1_full.md MEMORY_component_full.md MEMORY_model_full.md; do
    if [[ -f "$BASE/$f" ]]; then
        log "  ✅ $f 存在"
    else
        log "  ⚠️  $f 不存在"
    fi
done
log "详情见 daily-memories/ 目录"
log "========== END =========="
