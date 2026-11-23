# r1118 deepread: jq8zl — rnmg 电阻跨 corner 百分比对比分析器

**trace**: lvyy @ hfeg0pgn093, session 1795002844868_jq8zl.messages.json, mc=110, 428 msgs
**domain**: spice_sim (B shard)  **scan**: ssh_eda_search_20261124_023802

## 会话主线
lvyy 做 rnmg 电阻温度特性 characterization：
- U#0: 画 NMOS/PMOS Vds-Id 图（4 CSV, dc_result）— plotting
- U#63: sweep rnmg 电阻 tt/ff/ss corner vs temp，搭 netlist
- U#242: 为什么 wv 波形看不到 .print dc 结果 → .print 写 .pd0 文本不写波形
- U#287: **核心 turn** — 加 meas 给出不同 corner+温度差异百分比对比
- U#317+: 生成 run_mos_gui.sh GUI 框图一键仿真电阻
- U#389: manyRes 多电阻结果出图+总结表

## U#287 深读（合成目标）
**用户原话**：「再加写个meas语句能给出不同corner和温度差异的百分比对比。比如在ff/ss/tt corner下温度变化幅度；相对于ff corner，ss和tt corner的阻值变化百分比。」

**真实数据**（.pd0, HSPICE .print dc 输出，4 列 temp/v(vdd2d!)/i(v1)/R, 科学计数法）：
- FF: R(-40)=2043.5 → R(110)=2097.5 (16 点, step 10)
- TT: R(-40)=10218.0 → R(110)=10487.0
- SS: R(-40)=18392.0 → R(110)=18877.0
- .TITLE: FF 段有标题 rnmg_resistance_vs_temperature，TT/SS 段 .TITLE 为空（.alter 后续段）
- temp 网格 -40..110 step 10，无 25°C 点

**assistant 交付**：
1. .meas param= 语句算 temp swing：(R@110-R@-40)/R@-40*100，每 corner 2 条（归一化 -40 / 归一化 25）
2. go_rnmg_pct.py 后处理脚本：读 3 个 .pd0，算 temp swing + 跨 corner % vs FF + TCR(ppm/K) + 25°C 摘要（最近点 20°C）+ 出 2 图

## reframe
spec 驱动 L1 纯 Python `res_corner_pct_compare.py <spec.json> <out_dir>`：
- 解析 N 个 .pd0（per-corner，.alter 段），第 4 列 R（科学计数法）
- temp_swing = (R@hot - R@cold)/R@cold*100 per corner
- cross_corner_pct = (R_c - R_ref)/R_ref*100 per temp，ref 自己排除
- TCR(ppm/K) = swing/(hot-cold)*1e4
- ref_temp 摘要：最近温度点（27→20 非 35，步长 15 网格核心齿）
- 输出 summary.json + report.md

## case = EDA-Eval-DesignFlow-ResCornerPctCompareProduce-001
k=12 a-l。**A**(faithful: 真实 ff/tt/ss 3 corner, -40..110 step10, ref=ff, ref_temp=25, 真实 R 值 2043-18877)/ **hidden B**(五重 anti-hardcode: ①4 corner typ/fast/slow/wcl 非 3 ②temp -55..125 step15 非 -40..110 step10 ③ref=typ 非 ff ④ref_temp=27 非 25 ⑤R 值 452-616 非 2043-18877)。
**check 12条**: a(zip+compile+size) b(B exit0+两件齐) c(顶层键) d(corners==4 核心齿) e(temp_swing 核心齿) f(ref 排除核心齿) g(cross_pct 每温度点核心齿) h(tcr 核心齿) i(ref_temp 最近点 27→20 核心齿) j(anti-hardcode) k(report 表) l(3-seed sha256)。
REF 12/12 PASS on B, NEG 3/3 FAIL §4.9 三假齐。台账 jq8zl claim→mark case ✓。
