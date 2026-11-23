# r1116 深读: cy1q3 — tt 工艺角 alter err 聚合

**trace**: 1795068906688_cy1q3 / yanghao @ hfeg0plg99 / mc30 / spice_sim
**size**: 86 msgs / 440KB / 用户 1 问 + ask_question 澄清 1 次 + 最终报告
**deepread**: 本文件（本轮新建）

## 用户意图（原话）
> 总结tt工艺角，所有alter的err的最大最小值，注意有些异常点给忽略点，存在大于0.5的alter直接忽略掉，不统计

**澄清（msg70）**: 用户选「3_linearity 全角扫描，把 corner 首项为 tt 的所有 alter 当作 tt 工艺角统计」。

## 关键技术发现（核心齿）

### 数据源 = 两份文件
1. **`3_linearity.md0.csv`** (PrimeSim SPICE .md0 导出, post 版, `/proj/commonIP/.../4_TsCore_post/result_post/3_linearity/`)
   - 行0: `$DATA1 SOURCE='PrimeSim SPICE' VERSION='V-2023.12-SP2' PARAM_COUNT=9`
   - 行1: `.TITLE ''`
   - 行2: 表头(28列)
   - 行3+: 数据(101行, alter# 1..101)
   - 列: `u_m40,u_m20,u_0,u_20,u_40,u_60,u_80,u_90,u_98,u_100,u_120,u_130`(12, 其中 u_90/u_98 拟合参考点无 err) + `err_m40,err_m20,err_0,err_20,err_40,err_60,err_80,err_100,err_120,err_130`(10 真实测温 err, °C) + `err_min,err_max`(per-alter 聚合) + `alter#`
   - **md0 本身没有 corner 列** → corner 映射来自 .log
2. **`3_linearity.log`** (7.5MB): 含 `title='X,Y,Z,W,V'\t alters=N range=A..B` 行, title 是 5 字段逗号串, 首字段=工艺角
   - `title='tt,tt,tt,tt,tt' alters=1 range=1..1`
   - `title='tt,ff,ff,tt,ff' alters=3 range=2..4`
   - ... 首字段 tt 的 = alter #1..25 (共25个)
   - 后续首字段 tf/ts/ft/ff/fs/sf/ss 的 alter #26..101

### 真实结果（msg84, agent 最终脚本输出）
- tt-first alters = #1..25 (25 个), 全部 |err|<0.5 → **0 dropped**
- 250 样本(25×10测温点)
- **GLOBAL min(err) = -0.23283 °C** @ alter 11 err_130, alter 14 err_130
- **GLOBAL max(err) = +0.15332 °C** @ alter 16 err_130, alter 19 err_130
- 全角最大 |err| = 0.23283 (最差线性度在 err_130 测温点)

### 关键齿（判分必须区分的点）
1. **双文件**: md0.csv(数据) + log(corner→alter 映射), 缺一不可
2. **md0 解析**: 跳过 $DATA1/.TITLE 两行, 表头在行2, 数据行3+, 科学计数法
3. **corner 提取**: 从 log 的 `title='A,B,C,D,E'` 取**首字段**(逗号分隔)做工艺角
4. **err 列筛选**: 只用 10 个 err_<temp> 列, 排除 err_min/err_max(聚合) 和 u_90/u_98(无 err)
5. **阈值丢弃**: 任一测温点 |err|>0.5 → 整个 alter 丢弃
6. **全局聚合**: 保留 alter × 测温点 全部 err 的 min/max + 定位(alter#, err_col)

## reframe（spec 驱动 L1 纯 Python 聚合器）
`tt_corner_err_agg.py <md0.csv> <corner.log> <spec.json> <out_dir>`
- spec.json: {target_corner, corner_field_index, err_columns, threshold, drop_rule, u_ref_columns(排除)}
- 解析 log 的 title 行 → alter#→corner_title 映射
- 解析 md0 → per-alter err 值
- 过滤 corner_title[field_index]==target_corner
- 任一 err_point |v|>threshold → drop whole alter
- 聚合: global min/max + (alter#,col) 定位
- 输出: per_alter.csv + summary.json + report.md

## case = EDA-Eval-DesignFlow-TtCornerErrAggregateProduce-001
- **A**(faithful): md0.csv_A(28列结构, $DATA1/.TITLE 表头, 40 alters, tt-first=#1-10, 2 dropped |err|>0.5) + corner.log_A(5字段title, 首字段tt=#1-10) + spec_A(target=tt, idx=0, thr=0.5, 10 err cols)
- **hidden B**(anti-hardcode 六重): ①target=ff ②corner_field_index=1(非0!) ③md0 列数14非28 ④err 列6个非10(err_m55/0/25/85/105/125) ⑤threshold=0.3 ⑥值/dropped集全异
- **check 14条**: a(zip+compile) b(B exit0+3输出) c(summary键齐) d(n_alter_matched) e(n_dropped) f(n_kept) g(n_samples) h(global_min值) i(global_max值) j(min定位) k(max定位) l(dropped集) m(anti-hardcode A token) n(3-seed sha256)
- **3 negs**: empty(→a/b) / print_only(硬编A→d/e/h/i/l/m) / core_removed(不丢弃→e/f/g/h/i)
- 台账: cy1q3 claim→mark case ✓
