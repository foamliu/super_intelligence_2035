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
set -u

BASE="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run"
CONDUCTOR_LOG="/tmp/ablation_conductor.log"

log() {
    echo "[conductor] $(date '+%F %T') $*"
}

log "========== 十一假期串行执行开始 =========="
log "机器: 10.251.36.15"
log "预计总耗时: ~7-8 天（假期 9/30-10/7 全覆盖）"
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
# 阶段 2: 组件消融（流 C Phase 1）
#   pure_llm ×5 → rag ×5 → wo_retrieval ×5 = 15 轮
#   MEMORY: MEMORY_component_full.md
#   ~2 天
# ────────────────────────────────────────────
log "=== 阶段 2/4: 组件消融（pure_llm → rag → wo_retrieval）==="
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
#   ~3 天
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
