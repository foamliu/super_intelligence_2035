# INDEX_FILES — news/signal 文件清单（第11批 · **R6** 重登记）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**（最大单文件 = `prices/JPYCNY.json` 104,684 B）。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。
> ⏱ **本次更新（R6 · 2026-10-10 晚报轮）**：**38 标的十年价格再全量刷新**（`fetch_prices.py --refetch`，`ok=38 / fail=0`）⇒ §B 逐文件重登记（38 行）。
> **正式变动的范围（如实）**：**10 条汇率的末日 2026-10-08 → 2026-10-09**（R5 轮源侧当日价未发布 ⇒ **只等源、不补造**）；**A股 21 + 大宗 7 末日与 R5 相同**（均为 2026-10-09）
> ⇒ **末日一致性由 R5 的「28/38 整齐」变为 R6 的「38/38 整齐」**。
> `lag_corr.csv` 重跑后**仍与 R1/R2/R3/R4/R5 逐字节一致**（sha256 `83d3bf349be52251…`，**第 6 次可复现性通过**）。
> 🛡 `am_pm_check.py` 台账护栏（0 对照格时默认拒写）继续生效 ⇒ **R6 未覆盖** R3 的 63 格实核台账。
> 📄 **第 12 批收口产物（R6 轮复核）**：`signal/REPORT.html`（自包含单文件 · `grep -c http` = **0**，`href` 仅 7 个内部锚点）＋ 生成器 `signal/make_report_html.py`
> （**只读既有产物**：`lag_corr.csv` / `FINDINGS.md` / `BOOTSTRAP.md` / `prices/*.json`；**确定性**）。
> 🔧 **未再发生 R4/R5 式勘误**：§A 各行读数均由本脚本**当轮实测**生成（非手抄）。

## A. 代码 · 文档 · 生成物

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/fetch_prices.py`（代码） | 326 | 15008 | `af25a695577989cd` | git |
| `signal/lag_corr.py`（代码） | 574 | 27465 | `a132bba9af3daf2d` | git |
| `signal/signal_snapshot.py`（代码） | 104 | 4751 | `c82e42b942999b32` | git |
| `signal/make_findings.py`（代码） | 157 | 10745 | `e12523d47de268ff` | git |
| `signal/make_report_html.py`（代码 · 报告生成器） | 493 | 30335 | `5267afab883100a6` | git |
| `signal/REPORT.html`（**第11批收口报告** · 自包含单文件） | 234 | 30150 | `29a03cd0cd41e7ec` | git |
| `signal/block_boot.py`（代码） | 287 | 14639 | `d0ec0a0f782397cf` | git |
| `signal/am_pm_check.py`（代码 🛡护栏） | 179 | 9188 | `88b2023d1e37ce49` | git |
| `signal/PREREG.md`（**先于结果**） | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md`（源实测） | 55 | 4941 | `4367b85e123bedc0` | git |
| `signal/lag_corr.csv`（全网格 23940 格） | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/LAG_CORR.md`（**R6** 复核头） | 90 | 7975 | `5db62d0d9ac42aa8` | git |
| `signal/FINDINGS.md`（结论台账） | 56 | 8761 | `9d4fcb2fc32e92b5` | git |
| `signal/BOOTSTRAP.md`（块自助 CI） | 83 | 8096 | `bed9522efd27e529` | git |
| `signal/LATEST_SIGNALS.md`（信号快照） | 118 | 5851 | `99f284f701f23b94` | git |
| `signal/AM_PM_CHECK.md`（R3 台账+R5 说明） | 113 | 7826 | `217b72f89d35f86e` | git |
| `signal/daily/2026-10-08.md`（日报 AM+PM） | 171 | 17567 | `da49cef51e192b9c` | git |
| `signal/daily/2026-10-09.md`（日报 PM · R5） | 145 | 18753 | `a5c3c956025ba237` | git |
| `signal/daily/2026-10-10.md`（日报 PM · R6） | 150 | 19388 | `39bb06f15ad896eb` | git |

> ⚠️ 上表 `LAG_CORR.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `daily/*.md` 为**生成物或当轮产物**，
> sha 每轮会变；此处记录 **R6（2026-10-10 晚报轮）** 指纹。`lag_corr.csv` 为**确定性生成物**
> ⇒ R1 / R2 / R3 / R4 / R5 五次运行的 sha256 均为 `83d3bf349be52251…`（**逐字节一致**，可复现性证据）。
> `LATEST_SIGNALS.md` 本轮重跑 sha256 **未变**（`99f284f701f23b94…`）—— 因信号面 as-of 仍为 2026-09-30（语料冻结）。
> 🛡 **R5 台账护栏（如实记）**：`am_pm_check.py` 于 R5 复跑得 **0 对照格**（价格末日已越过 as-of 的 `k=1` 目标位）⇒
> 新增护栏**拒写**，`AM_PM_CHECK.md` **保留 R3 实核台账**并追加 `## 📌 R5 复跑说明`（**未用 null 覆盖实核**，§4-9）。
> 🔧 **R4 登记勘误（如实）**：R3 §A 曾把 `daily/2026-10-08.md` 记为 **130 行 / 11,565 B**（`501c76a7609f2663`）——
> 该读数为**登记时点早于 PM 版定稿**所致；文件**实际定稿**为 **171 行 / 17,567 B**（`da49cef51e192b9c`，与 git HEAD 一致）。
> R4 **按实际值修正**，**不改文件内容**。

## B. 价格数据（38 标的 · 逐文件登记）

> 目录级指纹（口径：**对 `prices/*.json` 逐文件 sha256（全 64 位）排序后以 `\n` 连接，再取 sha256 前 16**）＝
> `50d5ab4c3a40114c`（38 个文件 · 合计 **2,562,208 B**，最大单文件 **104,684 B**「`JPYCNY.json`」≪ 5 MB ⇒ 全部入 git）。
> ✅ **末日一致性（R6）**：**38/38 标的末日 = 2026-10-09**（A股为当日收盘价；汇率 = 当日可得报价；大宗为当日结算/收盘口径）。
> 上市/可得日 ≠ 2016 的标的见「区间」列（**幸存者偏差**，🚫 不插值）。

| 路径 | 名称 | 类 | 行数 | 大小(B) | sha256(前16) | 存放 | 区间 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `signal/prices/AU0.json` | 沪金 | fut | 2613 | 62248 | `02c609c2d96c280e` | git | 2016-01-04~2026-10-09 |
| `signal/prices/AUDCNY.json` | 澳元 | fx | 2811 | 98076 | `2b80ec1c2b41e699` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CADCNY.json` | 加元 | fx | 2811 | 98863 | `d34839eb2782a06e` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CHFCNY.json` | 瑞郎 | fx | 2809 | 98357 | `ed78d5e30c80c283` | git | 2016-01-01~2026-10-09 |
| `signal/prices/CU0.json` | 沪铜 | fut | 2613 | 65867 | `2861664b79ae7a7d` | git | 2016-01-04~2026-10-09 |
| `signal/prices/EURCNY.json` | 欧元 | fx | 2809 | 98540 | `fec5dfa291c49d79` | git | 2016-01-01~2026-10-09 |
| `signal/prices/GBPCNY.json` | 英镑 | fx | 2811 | 98144 | `a086f3e417041e15` | git | 2016-01-01~2026-10-09 |
| `signal/prices/HKDCNY.json` | 港币 | fx | 2811 | 101250 | `1cb6b2b180390504` | git | 2016-01-01~2026-10-09 |
| `signal/prices/I0.json` | 铁矿石 | fut | 2614 | 60648 | `d5a9a0beabbd820f` | git | 2016-01-04~2026-10-09 |
| `signal/prices/JPYCNY.json` | 日元 | fx | 2809 | 104684 | `6f15b9bfac9cf57c` | git | 2016-01-01~2026-10-09 |
| `signal/prices/M0.json` | 豆粕 | fut | 2613 | 63091 | `e1eb52e0f60ef452` | git | 2016-01-04~2026-10-09 |
| `signal/prices/NZDCNY.json` | 新西兰元 | fx | 2811 | 98609 | `9b7f4099df802c05` | git | 2016-01-01~2026-10-09 |
| `signal/prices/RB0.json` | 螺纹钢 | fut | 2613 | 63095 | `c536039f472becf5` | git | 2016-01-04~2026-10-09 |
| `signal/prices/SC0.json` | 原油(INE) | fut | 2070 | 47995 | `659096c9aab75d41` | git | 2018-03-26~2026-10-09 |
| `signal/prices/SGDCNY.json` | 新元 | fx | 2811 | 98679 | `e2ed126cacf8e953` | git | 2016-01-01~2026-10-09 |
| `signal/prices/TA0.json` | PTA | fut | 2610 | 63017 | `90d149006fef66b0` | git | 2016-01-04~2026-10-09 |
| `signal/prices/USDCNY.json` | 美元 | fx | 2787 | 97870 | `f96b123e16fe3e98` | git | 2016-01-01~2026-10-09 |
| `signal/prices/sh601138.json` | 工业富联 | stock | 2021 | 47702 | `24f33f0ecdbf3255` | git | 2018-06-08~2026-10-09 |
| `signal/prices/sh601360.json` | 三六零 | stock | 2491 | 59464 | `ed4edf4dd5cbc851` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603019.json` | 中科曙光 | stock | 2600 | 61651 | `3e3915afda01f21d` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603986.json` | 兆易创新 | stock | 2253 | 54827 | `5359abef4116aca0` | git | 2016-08-18~2026-10-09 |
| `signal/prices/sh688012.json` | 中微公司 | stock | 1740 | 43369 | `bfb77d116804e637` | git | 2019-07-22~2026-10-09 |
| `signal/prices/sh688041.json` | 海光信息 | stock | 995 | 24896 | `55ff3644a67eb57f` | git | 2022-08-12~2026-10-09 |
| `signal/prices/sh688111.json` | 金山办公 | stock | 1670 | 42109 | `153cb0e692a2c031` | git | 2019-11-18~2026-10-09 |
| `signal/prices/sh688256.json` | 寒武纪 | stock | 1508 | 37809 | `abeb1e90b422fca6` | git | 2020-07-20~2026-10-09 |
| `signal/prices/sh688981.json` | 中芯国际 | stock | 1504 | 35541 | `89311110267783f9` | git | 2020-07-16~2026-10-09 |
| `signal/prices/sz000977.json` | 浪潮信息 | stock | 2600 | 62508 | `ae1a98353c67c601` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002230.json` | 科大讯飞 | stock | 2565 | 61954 | `270f3ca4ca204ff0` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002241.json` | 歌尔股份 | stock | 2613 | 63013 | `06ff066c8565d7e6` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002371.json` | 北方华创 | stock | 2603 | 64714 | `0237a118923e6589` | git | 2016-01-11~2026-10-09 |
| `signal/prices/sz002463.json` | 沪电股份 | stock | 2613 | 61279 | `ba1ed751f5534406` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002475.json` | 立讯精密 | stock | 2612 | 62792 | `eaf15efdd2db7ec9` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002594.json` | 比亚迪 | stock | 2613 | 63701 | `1c6dcd61bc4a8b42` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002747.json` | 埃斯顿 | stock | 2565 | 60996 | `2b294ed144dcb109` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300124.json` | 汇川技术 | stock | 2602 | 62919 | `62b7061c8b88e439` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300308.json` | 中际旭创 | stock | 2469 | 59863 | `18457e1d1f684205` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300502.json` | 新易盛 | stock | 2573 | 61398 | `b50595a48a8e55e1` | git | 2016-03-03~2026-10-09 |
| `signal/prices/sz300750.json` | 宁德时代 | stock | 2020 | 50670 | `a4bf173bd2a478fd` | git | 2018-06-11~2026-10-09 |

> **类目覆盖核对（第11批硬指标）**：A股 **21** ≥ 20 ✅ · 汇率 **10**（USD/AUD/CAD/CHF/EUR/GBP/HKD/JPY/NZD/SGD vs CNY）✅ · 大宗 **7**（沪金 AU / 沪铜 CU / 铁矿 I / 豆粕 M / 螺纹 RB / 原油 SC / PTA TA）✅ · **合计 38**。
> **十年覆盖核对**：全部标的区间 **≥ 6.6 年**（最短 `sh688041` 自 2022-08-12，因其 2022 上市）；**21/38 自 2016 起**（汇率 9/10、大宗 6/7、个股 6/21）。
> ⚠️ **未复权 + 主力连续**：个股为**不复权**收盘价（除权日会跳空）；大宗为**主力连续**（换月跳空可能混入）
> ⇒ `lag_corr.py` 用**对数收益**、并**剔除 |日收益| > 30%** 的异常点（见 `LAG_CORR.md` §方法）；**本表只登记数据**，不做价格修正。
