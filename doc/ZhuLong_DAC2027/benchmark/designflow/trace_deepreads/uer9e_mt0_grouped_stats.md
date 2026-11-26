# 深读笔记: 1794450135994_uer9e (declanzh / 10.129.2.11)

**日期**: 2026-11-13 r479
**session**: 1794450135994_uer9e.messages.json (1.39MB, 512 msgs, 258 user msgs)
**用户**: declanzh
**主机**: 10.129.2.11 (hfeg0pkn002)
**match_count**: 489 (hspice:489)
**domain**: spice_sim
**agent**: lead (cline)

## 用户意图

declanzh 在多个 HSpice 仿真目录下处理 `.mt0` 测量数据文件，核心需求：
1. **汇总 .mt0 文件数据**：读取文件夹下所有 `.mt0` 文件，提取测量参数，给出每个参数的最大/最小值
2. **按 pvref 分组统计**：按 pvref 值分组，每组内计算各测量参数的绝对值 min/max
3. **单位换算**：A→mA(×1000)、ohm→Mohm(/1e6)、原始值→%(×100)
4. **标注极值条件**：min/max 对应的 alter# 和温度(temper)
5. **格式化输出**：输出汇总文档到文件

涉及多个仿真目录：
- `a51_VfsblnPumpCore_SIM/spf_result/core1103` — 电流参数(i_vfsbln/i_vwlp_fsbln/ieff)
- `a8_Vfsrdb_and_FsLatch_SIM` — res_r1/v_faout_sum 单位换算
- `a23_AG_FsAryLvlVwlp2Vfsblwn_SIM` — delay_fall_ns/delay_rise_ns 按 alter# 分组
- `a7_ThinFsComp_SIM` — voffset_vout_d_mv/voffset_vout_u_mv 按 pvref 分组

## Agent 工具链

1. list_allowed_files (3) — 探索仿真目录
2. read_files (60) — 读取 .mt0 文件、已有脚本
3. editor (114) — 编写/迭代 mt0 汇总脚本（多版本：a51_mt0_summary.py → mt0_summary_v2.py → vth_minmax.py → vth_grouped.py）
4. run_approved_command (58) — 执行 Python 脚本验证输出
5. run_commands (3) — 尝试 shell 命令（被拒绝，改用 run_approved_command）

## 关键产物

- **a51_mt0_summary.py**: 读 .mt0 文件 → 解析 i_vfsbln/i_vwlp_fsbln/ieff + temper + alter# → A→mA 换算 → 绝对值 min/max → 写汇总文档
- **vth_minmax.py / vth_grouped.py**: 读 .mt0 → 按 pvref 分组 → 计算每组 |voffset_vout_d_mv|/|voffset_vout_u_mv| 的 min/max → 标注 alter#/temper → 写分组报告
- **.mt0 格式**: 行以 `$`/`.` 开头为注释，列名行以 `pvref` 开头，数据行空格分隔数值

## .mt0 文件格式（实例）

```
$ HSPICE measurement data - monte carlo sweep
.measuremt0_file
pvref  voffset_vout_d_mv  voffset_vout_u_mv  temper  alter#
0.15  -0.2525  -0.2519  130  80
0.15  -0.7422  -0.7444  130  52
...
0.35  -0.5956  -0.5965  130  80
...
```

输出格式（agent 产出的真实输出）：
```
pvref 取值: [0.15, 0.35, 0.55]
pvref = 0.1500 V  (91 条数据)
  |voffset_vout_d_mv| :  min = 0.2525 mV,  max = 0.7422 mV
  |voffset_vout_u_mv| :  min = 0.2519 mV,  max = 0.7444 mV
    voffset_vout_d_mv  min时原始值 = -0.2525 mV  (alter#80, temper=130C)
    voffset_vout_d_mv  max时原始值 = -0.7422 mV  (alter#52, temper=130C)
```

## Case 化决策

- **case_id**: EDA-Eval-DesignFlow-Mt0GroupedStatsGen-001
- **A 档 trace-faithful**: 是（用 declanzh 原始需求作 prompt，保留真实 .mt0 格式和 pvref 分组统计场景）
- **domain**: spice_sim
- **layer**: L2（subprocess 真跑候选脚本在 hidden B 上，断言输出结构）
- **Input A**: measurement.mt0 (3 pvref 组 × 10 行) + spec.json (列定义/分组/输出格式)
- **Hidden B**: measurement_B.mt0 (4 pvref 组 × 8 行，不同值) + spec_B.json
- **check.py**: 10 断言 (k_check==k_rationale==10≥8):
  ① zip 含 mt0_grouped_stats.py
  ② subprocess 在 B 上真跑无错
  ③ 输出 JSON 有 groups 顶层键
  ④ 组数 = 4 (B 的 pvref 去重数)
  ⑤ 每组 row_count = 8
  ⑥ group "0.20" voffset_vout_d_mv abs_min/abs_max 正确
  ⑦ group "0.80" voffset_vout_u_mv abs_min/abs_max 正确
  ⑧ group "0.40" voffset_vout_d_mv abs_max 的 alter#/temper 正确
  ⑨ abs_min 基于绝对值(非 raw min): group "0.60" abs_min ≠ abs(raw_min)
  ⑩ groups 按 pvref 升序排列
- **自验**: check.py 10/10 PASS + 3 naive negatives 全 FAIL + 3 §4.9 fakes 全 FAIL
