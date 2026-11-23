# r1127 — tji0y (alenxu@hfhds201) → McSkewDistPlotProduce-001

## 选料（r1127 选料轮，推翻 r1126「扩池无效」结论的一部分）

r1126 仅 peek 了 spice_count≥20 的 13 候选即判「扩池无效」。但 shard_mc 已降到 5，
spice_count 10–19 段有 ~22 个未 peek 候选。本轮按 stop-loss「每轮真 peek ≥10 本域 fresh」
要求，对 b_fresh_r1126_xshard_dedup.tsv 中 spice_count 10–30 的未 peek 候选批量 peek
（scp peek3.py 到各 host，解析 cline messages.json dict 格式，抓首条 user_input）。

peek 10 候选结果：
| sid | user@host | mc | spice | top_tool | U#0 意图 | 判定 |
|---|---|---|---|---|---|---|
| 4cdcu | junlingw@plg99 | 56 | 41 | .lef | NOFILE (session 已删) | skip |
| samw8 | jason1t@plg69 | 126 | 30 | netlist | 读取当前 layout 信息 | C/A 拒 |
| 827bk | carlhe@plg81 | 62 | 27 | verilog | 读 lsf 配置分析集群 | infra 拒 |
| qjt9a | e0019946@plg49 | 1 | 25 | netlist | 为什么报错 timeout | meta-Q&A 拒 |
| nakpz | yohannw@pnd001 | 59 | 18 | waveview | 梳理 get_user_info.py 逻辑 | analysis-only 拒 |
| 5qlyc | reedchen@plg93 | 41 | 17 | cmos | output.ic 是什么文件 | Q&A 拒 |
| **tji0y** | **alenxu@hfhds201** | **20** | **16** | **lvs** | **dqs2dq_path.mt0.csv 对 4 skew 列做蒙卡分布图** | **✅ B 域 spice_sim 产出** |
| rjerk | thomasz@plg92 | 19 | 16 | netlist | 看下 IR sim 怎么报错 | debug-Q&A 拒 |
| lqhs3 | mingyu1l@plg103 | 110 | 15 | netlist | 查 si.inp 怎么处理 switch | analysis-only 拒 |
| xwi92 | steveny@pnd001 | 14 | 15 | pyaether | 把该提交到 git | 非 B 拒 |

→ 10 peek 1 产出 (tji0y)。tji0y 虽 lvs keyword 排第一，但 U#0 明确是 FineSim .mt0.csv
蒙卡分布图，属 spice_sim 产出型意图，有 check 齿。

## 深读 (155 msgs / 2.84MB)

alenxu 要求读取 `/proj/drvqa/V0/workdir/alenxu/simulation/sim_dqs2dq/07_mc/result_mc/dqs2dq_path.mt0.csv`，
对 4 个 DQ skew 列 (dq_0_90_skew/dq_90_180_skew/dq_180_270_skew/dq_270_0_skew) 做蒙卡分布图。

对话流：
- U#0: 给 mt0.csv 路径 + 4 列名，要蒙卡分布图
- A#1-29: cline 读文件 → 发现 504 行(500 数据 + 4 行 avg/std/min/max 汇总尾，token 数 98≠99)
  → 写 _mc_dqs2dq_skew.py (scipy 高斯拟合 + matplotlib 直方图/箱线图)
  → scipy 加载失败(libffi.so.5 缺) → 改纯 numpy norm_pdf
  → token count mismatch (49892 not divisible by 99) → debug 发现 4 行汇总尾破坏 flatten
  → 修 parser 只接受 99-token 数值行 → n=500 成功
  → 产出 dqs2dq_skew_histograms.png (2x2 直方图+高斯拟合+mean/std/min/max 标注)
    + dqs2dq_skew_boxplot.png (4 列并排箱线图)
- U#34/37/51...: 用户多次直接粘贴 4 列数值数据(纠正列名/符号)让 cline 重新画图
  → cline 把粘贴数据落 CSV 再画图

**reframe**: 核心意图 = FineSim .mt0.csv 蒙卡测量分布分析器：解析(跳过汇总尾) + 统计
(mean/std/min/max/n) + 绘图(直方图+箱线图)。L1 纯 Python 复刻，无 EDA 依赖。

## 合成

**case = EDA-Eval-DesignFlow-McSkewDistPlotProduce-001** 落库 cases/B/。

### 设计要点
- **A (visible)**: dqs2dq_path_A.mt0.csv — 4 列 dq_0_90_skew/dq_90_180_skew/dq_180_270_skew/dq_270_0_skew,
  500 数据行(9 token), 4 行汇总尾(8 token, 首 token=avg/std/min/max 非数值), 值 N(0,~7) ps
- **hidden B (anti-hardcode 五重)**: dqs2dq_path_B.mt0.csv —
  ① 列名异 A (dq_a_b_skew/dq_b_c_skew/dq_c_d_skew/dq_d_a_skew)
  ② 行数异 A (300 vs 500)
  ③ 汇总尾 token 数异 A (6 vs 8)
  ④ 值分布异 A (mean ~[1.5,-0.8,0.6,-1.2], std ~5 vs A mean~0 std~7)
  ⑤ 数据 seed 异 A (20260808 vs 20260101)
- **交付**: mc_skew_dist.py <mt0_csv> <out_dir> <col1> <col2> <col3> <col4> → stats.json + histograms.svg + boxplot.svg
- **stdlib-only**: 不依赖 numpy/matplotlib/scipy (评测环境 matplotlib 不可用)，纯 Python 手写 SVG

### check 13 条 (k=13)
a zip+compile | b run exit0+stats.json | c 4 keys==B_COLS | d n==300(跳尾) |
e mean<1e-6 | f std(ddof=1)<1e-6 | g min<1e-9 | h max<1e-9 |
i histograms.{svg,png}>1000B | j boxplot.{svg,png}>800B |
k 反硬编码 A 列名不入 B stats | l 反硬编码 B mean|>0.3(不近似 A~0) | m 3-seed sha256

### 自验
- REF 13/13 PASS ✓
- 3 negs 全 FAIL: neg_empty(→b) / neg_print_only(→c, A 列名泄露) / neg_core_removed(→d, n=304≠300 含尾) ✓
- §4.9 三假齐 (空壳/只 print A 期望/删核心跳尾逻辑) ✓

## 指标
- 📊 trace 覆盖率: covered=589/4529=13.0% (mc>=10, +1)
- 🎯 通过率: 最近20条 20/20=100% (观察值, 不变)
- 🧾 k_rationale=13 == k_check=13 ✓
- 📦 MEMORY_B <32KB ✓
- DEBT: 0

## 下一步
r1126「扩池无效」结论被部分推翻：spice 10–19 段仍有未 peek 候选。本轮 peek 10 产出 1。
下轮继续 peek b_fresh_r1126_xshard_dedup.tsv 剩余 spice 5–14 段未 peek 候选，或等新 scan。
