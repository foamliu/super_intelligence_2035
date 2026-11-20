# 2g3in — FSDB 波形信号脉冲宽度/tr/tf 筛选

**trace**: `1794398756746_2g3in.messages.json` (1.35MB, 281 条消息, 142 条用户消息)
**user**: kejunw @ hfeg0pkn002
**match_count**: 866
**domain**: spice_sim
**audit verdict**: 旧判 "consultation Q&A reject" → reaudit 可造 (analysis Q&A, 真实算法可提取)
**变现**: EDA-Eval-DesignFlow-FsdbPulseFilter-001 (L1 便携分析, 13 断言)

## 真实用户意图 (3 个真实用户轮)

1. "你可以直接分析分析fsdb波形吗" — 用户想直接分析 FSDB 波形文件
2. 贴出 FSDB 文件路径
3. "请分析如下path的所有信号，筛选出脉冲宽度小于300ps，tr和tf大于600ps的信号"
   path = `xi_c_top.xi_array16gtop.xi_spinetop.xi_banktopx2b23.xi24`

用户要的是：对 DDR SPICE 仿真 path 下所有信号做波形质量筛选，三个筛选条件：
- 脉冲宽度 < 300ps
- 上升时间 tr > 600ps
- 下降时间 tf > 600ps

## trace 助手工具链

1. `fscript` 把 FSDB 选定 path 的信号 dump 成文本表 `clean_out2.tbl`
   - 格式: `TIME v(sig1) v(sig2) ...` 表头 + 每行一个时间点
   - 12 个信号: `v(dmi<0>) v(dmi<1>) v(dq<0>) v(dq<1>) v(dq<2>) v(dq<3>) v(rdqs_c<0>) v(rdqs_c<1>) v(rdqs_t<0>) v(rdqs_t<1>) v(vdbias!) v(vintcore!)`
   - 900–999ns, 步长 1ns, 100 个时间点
   - SI 后缀: n/u/m/p
2. `compare.rep` 中间报告
3. `final_report.py` — 核心算法 (本 case 参考解的基础):
   - 50% 阈值 `(vmin+vmax)/2` 处上升/下降穿越 → 脉冲宽度 (high-pulse 最小值)
   - 25%→75% 摆幅上升穿越 → 上升时间 (最大值)
   - 75%→25% 摆幅下降穿越 → 下降时间 (最大值)
   - 常量信号 (摆幅 <50mV) 标记 const, 不算指标
   - 线性插值求穿越时刻

## trace 真实筛选结果

| 信号 | min_pw (ps) | max_tr (ps) | max_tf (ps) | triggers |
|---|---|---|---|---|
| v(dq<0>) | 36104 | 1010 | 69397 | rise_time_gt_600ps + fall_time_gt_600ps |
| v(dq<1>) | 36500 | 500 | 35500 | fall_time_gt_600ps |
| v(dq<2>) | 37000 | 500 | 36000 | fall_time_gt_600ps |
| v(dq<3>) | 37500 | 500 | 36500 | fall_time_gt_600ps |
| v(rdqs_c<0>) | 2150 | 500 | 650 | fall_time_gt_600ps (边界) |
| v(rdqs_c<1>) | 2150 | 500 | 650 | fall_time_gt_600ps (边界) |
| v(dmi<0>/<1>) | 15000 | 500 | 500 | (未触发) |
| v(rdqs_t<0>/<1>) | 15000 | 500 | 500 | (未触发) |
| v(vdbias!) | const (899.72m) | — | — | (常量) |
| v(vintcore!) | const (680m) | — | — | (常量) |

共 6 个信号被筛选 (dq<0-3> + rdqs_c<0-1>), 12 个信号总数。

## case 设计

**任务**: 给定 `waveform.tbl` (fscript dump 格式), 编写 `filter_pulse_signals.py(workdir, out_json)`
计算脉冲宽度/上升时间/下降时间并按三条件筛选, 输出 JSON 报告。

**L1 便携**: 纯 Python, 无 EDA 工具依赖, 波形数据是合成的但格式/信号名/算法与真实 trace 完全一致。

**A 输入 (可见)**: 12 信号, 6 个被筛选 (dq<0-3> + rdqs_c<0-1>), 与 trace 真实结果一致。
**隐藏 B 输入 (跨输入守卫)**: 信号名偏移 (dq<4-7>/dmi<2-3>/rdqs_c<2-3>/rdqs_t<2-3>/vss!/vddq!),
不同时序值, **只有 dq<4-7> 触发 tf, rdqs_c<2-3> 不触发** (tf=500ps < 600ps), 4 个被筛选。
→ A=6/B=4, filtered_signals 完全不同, 证非硬编码 A。

**check.py 13 断言**: a(zip结构) b(JSON合法+5顶层键) c(A重跑复现, 证非手写)
d(n_total==12) e(n_filt==6) f(filtered==dq<0-3>+rdqs_c<0-1>)
g(dq<0>双触发rise+fall) h(dq<1>仅fall) i(rdqs_c<0>边界fall)
j(vdbias!/vintcore! const) k(criteria==300/600/600)
l(B==oracle_B, 4个筛选) m(A!=B filtered, 跨输入守卫)

**4 个负样本**: naive_hardcode_a (硬编码A的6信号, B上失败), always_empty (全null, b失败),
print_only (只打印, b失败), core_deleted (只解析表头不算指标, e/f失败)。
全部 FAIL, 参考 PASS, negative_selftest GREEN。

## 备注

波形数据是合成的 (无法从 .75 直接 ssh 拉真实 FSDB 到本地 NAS), 但:
- 格式与真实 clean_out2.tbl 完全一致 (TIME 表头 + v(sig) 列 + SI 后缀)
- A 的信号名与真实 trace 一致 (dmi<0-1>/dq<0-3>/rdqs_c<0-1>/rdqs_t<0-1>/vdbias!/vintcore!)
- A 的触发模式与真实 trace 最终筛选结果一致 (dq<0>双触发, dq<1-3> tf, rdqs_c<0-1> 边界)
- 算法 (25-75% rise / 75-25% fall / 50% pulse width / const<50mV) 完全来自 trace final_report.py
