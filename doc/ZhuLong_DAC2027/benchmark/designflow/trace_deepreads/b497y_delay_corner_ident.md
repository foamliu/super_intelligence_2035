# Deepread: 1794450128835_b497y (declanzh / 10.129.2.11 / hfeg0pkn002)

- **slug**: 1794450128835_b497y · **user**: declanzh · **host**: 10.129.2.11 · **mc**: 462 (hspice:462)
- **size**: 1.35MB / 484 msgs (244 user / 240 assistant)
- **tools**: list_allowed_files(2) · run_commands(3) · run_approved_command(49) · read_files(55) · editor(116)
- **domain verdict**: spice_sim (B) ✓ — real HSpice .mt0 processing with run_approved_command execution

## 用户意图（trace-faithful）
declanzh 在多个 HSpice 仿真目录处理 .mt0 测量文件，核心任务序列：
1. [msg 2] core1103 目录 77 个 .mt0 → 汇总 i_vfsbln/i_vwlp_fsbln/ieff 的 min/max
2. [msg 24] 按绝对值、换算 mA 单位
3. [msg 66] ieff 除以 100 显示百分比，文件列只保留 #数字
4. [msg 122] 保留小数点后 2 位，单位单独列，去掉温度列
5. **[msg 210] a23_AG_FsAryLvlVwlp2Vfsblwn_rerun.mt0 → 找 delay_fall_ns 和 delay_rise_ns 的最大/最小值** ← 本 case 选用
6. [msg 220] a7_ThinFsComp_rerun.mt0 → 按 pvref 分组，voffset_vout_d_mv/u_mv 绝对值 max/min
7. [msg 379] 为什么 min@130°C / max@-40°C（物理分析）
8. [msg 450] 将处理流程总结为 FuseSense skill

## msg 210-219 详情（本 case 源）
- 文件: `a23_AG_FsAryLvlVwlp2Vfsblwn_rerun.mt0`，228 行 = 19 alter# × 12 index
- 列: index(0) pvwlp(1) ?(2) pvfsbln(3) delay_fall_ns(4) ?(5) delay_rise_ns(6) ?(7) temper(8) alter#(9)
- 结果: delay_fall_ns min=0.4665ns(alter#3,-40°C) max=641.29ns(alter#10,-40°C,极端慢角)
        delay_rise_ns min=0.191ns(alter#17,130°C) max=876.34ns(alter#10,-40°C)
- agent 写 delay_minmax.py → run_approved_command 真跑 → 按 alter# 分组报告每角 min/max

## 与 uer9e (Mt0GroupedStatsGen-001) 的区分
- uer9e: voffset 电压信号 · 按 pvref 分组 · 绝对值 min/max · JSON 输出
- b497y (本 case): delay 延迟信号 · 按 alter#(工艺角) 分组 · 原始值 min/max · 文本报告输出 · 最差工艺角识别
- 核心技能不同：uer9e=跨参考电压统计聚合；本 case=跨工艺角最差情况识别（timing signoff 视角）

## case 化
- **task_id**: EDA-Eval-DesignFlow-DelayCornerIdent-001
- **deliverable**: submit.zip{delay_corner_checker.py}
- **Input A**: measurement.mt0 (5 alter# × 4 index = 20 行) + spec.json
- **hidden B**: measurement_B.mt0 (6 alter# × 5 index = 30 行, scale=1.5, 不同值/温度) + spec_B.json
- **check.py**: 12 断言 (k_check==k_rationale==12≥8), subprocess 在 B 真跑, 独立复算 ground truth 后逐值匹配文本报告
- **自验**: ref 12/12 PASS + 3 §4.9 fakes(empty/print/core_removed)全FAIL + 2 negatives(hardcoded_A/always_pass)全FAIL
