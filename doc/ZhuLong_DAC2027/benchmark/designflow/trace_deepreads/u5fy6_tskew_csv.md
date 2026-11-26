# Deep-read: u5fy6 — Tskew CSV 分析脚本

## Trace
- session: `1792134701239_u5fy6` (reedchen / hfeg0pkn004 / mc=174)
- 800 msgs, 2.45 MB, 22 real user turns
- domain: **waveform** (finesim .mt0.csv 仿真后处理)

## 用户意图流（U#1 = 提需求，A-faithful 任务说明）
- **U#1 (idx 0)**「请你用脚本帮我处理一下这个csv文件，这个文件有 PP 和 WP 两组数据，每组数据又分为 Tr 和 Tf 两份，先将所有数据向 1.5ns 取余，然后你需要找到 Tr 和 Tf 各自的最大值和最小值，然后用公式 Tskew = max(tf_slow,tr_slow) - min(tf_fast,tr_fast) 得到 PP 和 WP 两组数据的 Tskew」→ **干净提出需求轮 ✓**
- U#2 (idx 45)「WP 和 PP 是两种情况，应该得到两种 Skew」(修正理解)
- U#3 (idx 65)「注释换英文 + 递归分析目录 + 从文件名拿 PVT + 结果存 log 文件」(需求扩展)
- U#4 (idx 223)「CSV 多了三倍数据 L1/L2/L3，各算 WP/PP skew 取最小」
- U#6 (idx 330)「summary table 不含 TrTf 列 + 电压显示修正(74V=0.74V, 9V=0.9V) + 支持多行 CSV 横向对比」
- U#9 (idx 416)「支持 error 数据跳过」
- U#11 (idx 458)「取余后 tr/tf=0 或 1.5n 则忽略」
- U#13 (idx 530) 起：任务转向 GenSignalTrTf.py / GenSP.py（测量脚本生成，非本 case）

## Agent 工具链
- `read_files` 79 次（读 CSV / 脚本 / skill）
- `editor` 128 次（写脚本：analyze_mt0.py → tskew_calc.py → tskew_batch.py → tskew_batch_v2.py）
- `run_approved_command` 157 次（跑脚本验证）
- `list_allowed_files` 18 次
- 工作目录：`/home/reedchen/` → 最终脚本 `tskew_batch_v2.py`（14.8KB，含 L1/L2/L3 多 level + PVT + log + 递归）

## 金标准（从 trace 重建）
- 主脚本 `tskew_batch_v2.py`（idx=224 editor full write, 14836 bytes）
  - COL_RE: `^(epp|ewp)(L[123])?\d+_(r|f)\d+$`
  - PVT_RE: `output_([A-Z]+)_([0-9]+)V([-0-9]+)C\.mt0\.csv$`
  - Tskew = max(Tf_max, Tr_max) - min(Tf_min, Tr_min) per group per level
  - 跨 level 取 min
  - 递归 os.walk，写 log + summary table
- 磁盘 `/home/reedchen/tskew_batch_v2.py` ssh cat 超时（路径已不可达或 find 过慢）→ 走 trace 重建

## 合成决策
- **A 档 trace-faithful**：prompt = U#1 原话（逐字，含真实路径）；config.json 作为结构化接口资产（指定 period/groups/ignore_zero/skip_error/voltage_rule）补全 U#1 未提及的参数化细节
- 资产 A = config.json + data/output_SS_9V-40C.mt0.csv（样例，SS/0.9V/-40C，8 列单行）
- 隐藏 B = hidden/config_B.json + data_B/output_FF_74V125C.mt0.csv（结构不同：FF/0.74V/125C、11 列、含 2.9e-9 包绕值、含 0 值列、含 error 列）
- gold = 参数化 `gen_tskew.py`（逻辑取自 trace tskew_batch_v2.py，去除 L1/L2/L3 多 level 以聚焦核心 Tskew + 取余 + 忽略零 + 跳过 error + PVT 电压规则）
- 13 条件 a-m，ref PASS 13/13 · 5 negatives ALL-FAIL distinct
