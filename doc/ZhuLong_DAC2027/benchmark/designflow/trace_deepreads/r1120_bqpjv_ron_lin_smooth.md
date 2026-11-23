# r1120 bqpjv 深读 — clarawu Ron 线性度/光滑度/单调性 .md0 分析

**session**: 1794905973396_bqpjv (clarawu@hfhds201, mc39, netlist:144 hspice:144 schematic:144)
**结果**: REJECT near-dup of RonCurveSmoothness-001

## 用户意图（msg 0, 13, 23, 44）

clarawu 跑 DDR4 FinalDrv Ron characterization，FineSim/HSPICE 输出 `.md0` 测量文件（Ron.md0, Ron#1.md0），含 rpu_50/rpd_50 vs zqdec 扫描数据（64 点, zqdec 0..63, 22 列）。

要求写 Python 脚本:
1. **线性度** = Ron 随 zqdec 一阶差分；msg 23 精化为 `max|d1|`（绝对值最大）
2. **光滑度** = 二阶差分；msg 23 精化为 `max|d2|`
3. **单调性** (msg 23 新增): 所有一阶差分为负 → 单调
4. merge 进 `extract_all.py`；msg 44 去掉 direction 列、值保留 2 位小数；复制回 /proj 工作目录

## assistant 方案

### ron_linearity_smoothness.py (msg 6, 独立脚本)
- `parse_md0(path)`: 跳 `$`/`.` 注释行，header = first non-numeric line，parse 数值行
- `analyze(vals_by_zq)`: 按 zqdec 升序排序，d1[i]=y[i+1]-y[i]，d2[i]=y[i+2]-2y[i+1]+y[i]
- 每 signal 输出: d1_min/d1_max/d1_max_abs, d2_min/d2_max/d2_max_abs, per-step 表
- 默认分析 2 个 .md0 文件，SIGNALS=["rpu_50","rpd_50"]

### ron_lin_smooth_stats() + task_ron_lin_smooth() (msg 35, merge 进 extract_all.py)
- `linearity = max(|d1|)`, `smoothness = max(|d2|)`, `monotonic = all(d1<0)`
- `direction`: 'mono-dec' (all d1<0) / 'mono-inc' (all d1>0) / 'non-monotonic'
- `d1@zqdec` = "a->b" (|d1| 最大处的 zqdec 对), `d2@zqdec` = "c" (|d2| 最大处中心 zqdec)
- 输出对齐表: file | signal | linearity max|d1| | d1@zqdec | smoothness max|d2| | d2@zqdec | monotonic | direction

## 真实数据重建（从 msg 9 stdout 提取，64 点/信号 × 2 文件 × 2 信号）

从 msg 9 per-step 表重建 (zqdec, ron) 对，验证 summary 与 trace 报告(msg 21)完全一致:

| 文件 | 信号 | n | linearity=max|d1| | d1@zqdec | smoothness=max|d2| | d2@zqdec | direction |
|---|---|---|---|---|---|---|---|
| Ron.md0 | rpu_50 | 64 | 8.5600 | 1->2 | 5.1500 | 2 | mono-dec |
| Ron.md0 | rpd_50 | 64 | 7.9200 | 1->2 | 4.2500 | 32 | mono-dec |
| Ron#1.md0 | rpu_50 | 64 | 12.6300 | 1->2 | 8.0600 | 32 | mono-dec |
| Ron#1.md0 | rpd_50 | 64 | 14.0300 | 15->16 | 10.7600 | 32 | mono-dec |

全部 mono-dec（所有 d1<0）。msg 21 报告值完全匹配。

## REJECT 理由

台账 r913 已 parked: "near-dup of clarawu RonDvqSlopeExtract-001 + r958-parked bqpjv(RonSmoothnessGen/RonCurveSmoothness dup)"。

核对 `cases/B/EDA-Eval-DesignFlow-RonCurveSmoothness-001.json`:
- trace: 1794465241456_ua9tu (clarawu)
- prompt: FineSim/HSPICE `.md0` 测量文件，Ron (rpu_50/rpd_50) vs zqdec，linearity/smoothness/monotonic

核心 .md0 parse + d1/d2 + monotonic 完全重叠。bqpjv 增量:
1. d1@zqdec / d2@zqdec location 报告（worst step/curvature 位置）
2. 3-way direction 分类（mono-dec/mono-inc/non-monotonic）

增量不足以脱离 near-dup（核心 produce 逻辑 = .md0 parse + d1/d2/linearity/smoothness/monotonic 已被 RonCurveSmoothness-001 覆盖）。parking 正确，不推翻。

## 附: .md0 格式（供未来 Ron 类 case 参考）

- 注释行: `$...` 和 `.TITLE ...`
- header 行: 首个 token 非数字的行（22 列: zqdec, rpu_50, rpu_lin20, rpu_lin50, rpu_lin75, rpd_50, rpd_lin20, rpd_lin50, rpd_lin75, ... ）
- 数据行: 空白分隔的浮点数，64 行（zqdec 0..63）
- parse 关键: 跳注释 → 找 header(first non-numeric) → float() 数据行；用 `.split()` 而非 regex `\s`（ASCII env 下 `\s`/`\S` 类失效，已知坑）
