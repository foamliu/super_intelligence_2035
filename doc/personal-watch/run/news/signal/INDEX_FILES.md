# INDEX_FILES — news/signal 文件清单（第11批 · **R7** 重登记）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**（最大单文件 = `prices/JPYCNY.json` 104,684 B）。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。
> ⏱ **本次更新（R7 · 2026-10-11 早报轮）**：**38 标的十年价格再全量刷新**（`fetch_prices.py --refetch`，`ok=38 / fail=0`）⇒ §B 逐文件重登记（38 行）。
> **正式变动的范围（如实）**：**无新交易日**（10-10 周六 / 10-11 周日均无交易时段 ⇒ **只等源、不补造**）；**末日 38/38 仍 = 2026-10-09**；文件字节变化**仅 `fetched_at` 刷新**（行数据未变）。
> `lag_corr.csv` 重跑后**仍与 R1–R6 逐字节一致**（sha256 `83d3bf349be52251…`，**第 7 次可复现性通过**）。
> 🔧 **第 12 批收口产物 R7 修订（如实）**：`signal/REPORT.html` §⑤ **10 条汇率行显示层修订**（源侧 `USDCNY` 停在 2026-09-30 的显式标注）⇒ 指纹 **`29a03cd0…` → `ff695f4f0cf79060…`**（**仅展示层，非统计量**）。
> 🛡 `am_pm_check.py` 台账护栏（0 对照格时默认拒写）继续生效 ⇒ **R7 未覆盖** R3 的 63 格实核台账。
> 🔧 **勘误（如实）**：R6 轮**未重登记**本文件（其 §A `REPORT.html` 行仍记 `29a03cd0…`）⇒ 本 R7 轮**补登记**；§A 各行读数均由本脚本**当轮实测**生成（非手抄）。

## A. 代码 · 文档 · 生成物

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/fetch_prices.py`（代码） | 326 | 15008 | `af25a695577989cd` | git |
| `signal/lag_corr.py`（代码） | 577 | 27594 | `14a5d52800cdd29a` | git |
| `signal/signal_snapshot.py`（代码） | 104 | 4751 | `c82e42b942999b32` | git |
| `signal/make_findings.py`（代码） | 164 | 11701 | `3a9b1a3ddeb2aab0` | git |
| `signal/make_report_html.py`（代码 · 报告生成器） | 493 | 30335 | `5267afab883100a6` | git |
| `signal/REPORT.html`（**第11批收口报告** · 自包含单文件） | 234 | 30150 | `ff695f4f0cf79060` | git |
| `signal/block_boot.py`（代码） | 287 | 14639 | `d0ec0a0f782397cf` | git |
| `signal/am_pm_check.py`（代码 🛡护栏） | 179 | 9188 | `88b2023d1e37ce49` | git |
| `signal/PREREG.md`（**先于结果**） | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md`（源实测） | 55 | 4941 | `7c9507aba6639dec` | git |
| `signal/lag_corr.csv`（全网格 23940 格） | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/LAG_CORR.md`（**R7** 复核头） | 90 | 8056 | `dd8aaf85b959dd74` | git |
| `signal/FINDINGS.md`（结论台账） | 57 | 9605 | `6215bec577d22fa5` | git |
| `signal/BOOTSTRAP.md`（块自助 CI） | 83 | 8096 | `bed9522efd27e529` | git |
| `signal/LATEST_SIGNALS.md`（信号快照） | 118 | 5851 | `99f284f701f23b94` | git |
| `signal/AM_PM_CHECK.md`（R3 台账+R5 说明） | 113 | 7826 | `217b72f89d35f86e` | git |
| `signal/daily/2026-10-08.md`（日报 AM+PM） | 171 | 17567 | `da49cef51e192b9c` | git |
| `signal/daily/2026-10-09.md`（日报 PM · R5） | 145 | 18753 | `a5c3c956025ba237` | git |
| `signal/daily/2026-10-10.md`（日报 PM · R6） | 150 | 19388 | `39bb06f15ad896eb` | git |
| `signal/daily/2026-10-11.md`（日报 AM · R7） | 145 | 20436 | `beb93934b13f3e62` | git |

> ⚠️ 上表 `LAG_CORR.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `daily/*.md` 为**生成物或当轮产物**，
> sha 每轮会变；此处记录 **R7（2026-10-11 早报轮）** 指纹。`lag_corr.csv` 为**确定性生成物**
> ⇒ R1–R7 **七次运行**的 sha256 均为 `83d3bf349be52251…`（**逐字节一致**，可复现性证据）。
> `LATEST_SIGNALS.md` 本轮重跑 sha256 **未变**（`99f284f701f23b94…`）—— 因信号面 as-of 仍为 2026-09-30（语料冻结）。
> 🛡 **R5 台账护栏（如实记）**：`am_pm_check.py` 于 R5 复跑得 **0 对照格**（价格末日已越过 as-of 的 `k=1` 目标位）⇒
> 新增护栏**拒写**，`AM_PM_CHECK.md` **保留 R3 实核台账**并追加 `## 📌 R5 复跑说明`（**未用 null 覆盖实核**，§4-9）。
> 🔧 **R4 登记勘误（如实）**：R3 §A 曾把 `daily/2026-10-08.md` 记为 **130 行 / 11,565 B**（`501c76a7609f2663`）——
> 该读数为**登记时点早于 PM 版定稿**所致；文件**实际定稿**为 **171 行 / 17,567 B**（`da49cef51e192b9c`，与 git HEAD 一致）。
> R4 **按实际值修正**，**不改文件内容**。

## B. 价格数据（38 标的 · 逐文件登记）

> 目录级指纹（口径：**对 `prices/*.json` 逐文件 sha256（全 64 位）排序后以 `\n` 连接，再取 sha256 前 16**）＝
> `acc18b5fb54f8ce4`（38 个文件 · 合计 **2,562,208 B**，最大单文件 **104,684 B**「`JPYCNY.json`」≪ 5 MB ⇒ 全部入 git）。
> ✅ **末日一致性（R7）**：**38/38 标的末日 = 2026-10-09**（**2026-10-09（38 个）**；**A股为当日收盘价**；汇率 = 当日可得报价；大宗为当日结算/收盘口径）。
> 上市/可得日 ≠ 2016 的标的见「区间」列（**幸存者偏差**，🚫 不插值）。

| 路径 | 名称 | 类 | 行数 | 大小(B) | sha256(前16) | 存放 | 区间 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `signal/prices/AU0.json` | 沪金 | fut | 2613 | 62248 | `282d796a9b8540b0` | git | 2016-01-04~2026-10-09 |
| `signal/prices/AUDCNY.json` | 澳元 | fx | 2811 | 98076 | `16d6be5fdfcd7f79` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CADCNY.json` | 加元 | fx | 2811 | 98863 | `04bc1504b01fa6cd` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CHFCNY.json` | 瑞郎 | fx | 2809 | 98357 | `380659fb7b075130` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CU0.json` | 沪铜 | fut | 2613 | 65867 | `8b37712c2e5852d3` | git | 2016-01-04~2026-10-09 |
| `signal/prices/EURCNY.json` | 欧元 | fx | 2809 | 98540 | `391a76aec9bc3308` | git | 2016-01-01~2026-10-09 |
| `signal/prices/GBPCNY.json` | 英镑 | fx | 2811 | 98144 | `8a299fb0a1aef415` | git | 2016-01-01~2026-10-09 |
| `signal/prices/HKDCNY.json` | 港币 | fx | 2811 | 101250 | `267501981a68fdac` | git | 2016-01-01~2026-10-09 |
| `signal/prices/I0.json` | 铁矿石 | fut | 2614 | 60648 | `947b0555ebc3ed07` | git | 2016-01-04~2026-10-09 |
| `signal/prices/JPYCNY.json` | 日元 | fx | 2809 | 104684 | `f3c10fe8776937b7` | git | 2016-01-01~2026-10-09 |
| `signal/prices/M0.json` | 豆粕 | fut | 2613 | 63091 | `9d8afcaf43f4b89a` | git | 2016-01-04~2026-10-09 |
| `signal/prices/NZDCNY.json` | 新西兰元 | fx | 2811 | 98609 | `486f3daf155db6a7` | git | 2016-01-01~2026-10-09 |
| `signal/prices/RB0.json` | 螺纹钢 | fut | 2613 | 63095 | `4163f082874af893` | git | 2016-01-04~2026-10-09 |
| `signal/prices/SC0.json` | 原油(INE) | fut | 2070 | 47995 | `382782ceae1b988e` | git | 2018-03-26~2026-10-09 |
| `signal/prices/SGDCNY.json` | 新元 | fx | 2811 | 98679 | `69cacc27a7216bb7` | git | 2016-01-01~2026-10-09 |
| `signal/prices/TA0.json` | PTA | fut | 2610 | 63017 | `eced1bbdaa623eef` | git | 2016-01-04~2026-10-09 |
| `signal/prices/USDCNY.json` | 美元 | fx | 2787 | 97870 | `fbdc1c2ee0d8d9ca` | git | 2016-01-01~2026-10-09 |
| `signal/prices/sh601138.json` | 工业富联 | stock | 2021 | 47702 | `37af709412f13dc2` | git | 2018-06-08~2026-10-09 |
| `signal/prices/sh601360.json` | 三六零 | stock | 2491 | 59464 | `98a51da094fd273d` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603019.json` | 中科曙光 | stock | 2600 | 61651 | `eeee0bf61a36661f` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603986.json` | 兆易创新 | stock | 2253 | 54827 | `3f73ccc4dd15ae0f` | git | 2016-08-18~2026-10-09 |
| `signal/prices/sh688012.json` | 中微公司 | stock | 1740 | 43369 | `389b0ccd02c21fb1` | git | 2019-07-22~2026-10-09 |
| `signal/prices/sh688041.json` | 海光信息 | stock | 995 | 24896 | `26077aab90f6f8d6` | git | 2022-08-12~2026-10-09 |
| `signal/prices/sh688111.json` | 金山办公 | stock | 1670 | 42109 | `28bad11a3f1bdf23` | git | 2019-11-18~2026-10-09 |
| `signal/prices/sh688256.json` | 寒武纪 | stock | 1508 | 37809 | `e625dcd3a86aff8d` | git | 2020-07-20~2026-10-09 |
| `signal/prices/sh688981.json` | 中芯国际 | stock | 1504 | 35541 | `5d824a6b81e86234` | git | 2020-07-16~2026-10-09 |
| `signal/prices/sz000977.json` | 浪潮信息 | stock | 2600 | 62508 | `9ab96450a5671174` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002230.json` | 科大讯飞 | stock | 2565 | 61954 | `69fcd12231c0850a` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002241.json` | 歌尔股份 | stock | 2613 | 63013 | `f7a0f861bc0c8b09` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002371.json` | 北方华创 | stock | 2603 | 64714 | `c2be8733fb17d51f` | git | 2016-01-11~2026-10-09 |
| `signal/prices/sz002463.json` | 沪电股份 | stock | 2613 | 61279 | `e73e653538fae42c` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002475.json` | 立讯精密 | stock | 2612 | 62792 | `ca6a7cba481a4a15` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002594.json` | 比亚迪 | stock | 2613 | 63701 | `8095b412b4ffb2b2` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002747.json` | 埃斯顿 | stock | 2565 | 60996 | `9be69f900adcba45` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300124.json` | 汇川技术 | stock | 2602 | 62919 | `1f5614d101c6086e` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300308.json` | 中际旭创 | stock | 2469 | 59863 | `b762748cc2581876` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300502.json` | 新易盛 | stock | 2573 | 61398 | `79bea6f7b5c93a85` | git | 2016-03-03~2026-10-09 |
| `signal/prices/sz300750.json` | 宁德时代 | stock | 2020 | 50670 | `edea6d80870ce6d2` | git | 2018-06-11~2026-10-09 |

> **类目覆盖核对（第11批硬指标）**：A股 **21** ≥ 20 ✅ · 汇率 **10**（USD/AUD/CAD/CHF/EUR/GBP/HKD/JPY/NZD/SGD vs CNY）✅ · 大宗 **7**（沪金 AU / 沪铜 CU / 铁矿 I / 豆粕 M / 螺纹 RB / 原油 SC / PTA TA）✅ · **合计 38**。
> **十年覆盖核对**：全部标的区间 **≥ 6.6 年**（最短 `sh688041` 自 2022-08-12，因其 2022 上市）；**21/38 自 2016 起**（汇率 9/10、大宗 6/7、个股 6/21）。
> ⚠️ **未复权 + 主力连续**：个股为**不复权**收盘价（除权日会跳空）；大宗为**主力连续**（换月跳空可能混入）
> ⇒ `lag_corr.py` 用**对数收益**、并**剔除 |日收益| > 30%** 的异常点（见 `LAG_CORR.md` §方法）；**本表只登记数据**，不做价格修正。
