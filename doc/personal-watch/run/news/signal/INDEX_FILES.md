# INDEX_FILES — news/signal 文件清单（第11批 · **R4** 重登记）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**（最大单文件 = `prices/JPYCNY.json` 104,647 B）。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。
> ⏱ **本次更新（R4 · 2026-10-09 早报轮）**：**38 标的十年价格再全量刷新**（`fetch_prices.py`，`ok=38 / fail=0`）⇒
> §B 逐文件重登记（38 行）。**正式变动的范围（如实）**：**仅 10 条汇率的末日由 2026-10-07（`USDCNY` 为 2026-09-30）推进到 2026-10-08**；
> 其余 **28 个价格文件的行数据（`rows`/`sha16`）与 R3 完全相同**，文件字节差异仅来自每次抓取必写的 `fetched_at` 时间戳。
> `lag_corr.csv` 重跑后**仍与 R1/R2/R3 逐字节一致**（sha256 `83d3bf349be52251…`，**第 4 次可复现性通过**）。

## A. 代码 · 文档 · 生成物

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/fetch_prices.py` | 326 | 14993 | `bb89bc45b29288be` | git |
| `signal/lag_corr.py` | 575 | 27435 | `57fd8aadbc8c6ddd` | git |
| `signal/signal_snapshot.py` | 104 | 4751 | `c82e42b942999b32` | git |
| `signal/make_findings.py` | 141 | 8603 | `76473d71d5f92eae` | git |
| `signal/block_boot.py` | 287 | 14639 | `d0ec0a0f782397cf` | git |
| `signal/am_pm_check.py` | 161 | 7739 | `0211a563969378a3` | git |
| `signal/PREREG.md`（**先于结果**） | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md`（源实测） | 55 | 4941 | `cc2d7d3b48ef851e` | git |
| `signal/lag_corr.csv`（全网格 23940 格） | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/LAG_CORR.md`（R4 复核头） | 90 | 7929 | `3bcb268b4b574917` | git |
| `signal/FINDINGS.md`（结论台账） | 54 | 6875 | `065e06bc168b526b` | git |
| `signal/BOOTSTRAP.md`（块自助 CI） | 83 | 8096 | `bed9522efd27e529` | git |
| `signal/LATEST_SIGNALS.md`（信号快照） | 118 | 5851 | `99f284f701f23b94` | git |
| `signal/AM_PM_CHECK.md`（早报→晚报复核） | 96 | 6076 | `f217c73f8097551d` | git |
| `signal/daily/2026-10-08.md`（日报 AM+PM） | 171 | 17567 | `da49cef51e192b9c` | git |
| `signal/daily/2026-10-09.md`（日报 AM · R4） | 134 | 14711 | `0fb7e0345e04723d` | git |

> ⚠️ 上表 `LAG_CORR.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `daily/*.md` 为**生成物或当轮产物**，
> sha 每轮会变；此处记录 **R4（2026-10-09 早报轮）** 指纹。`lag_corr.csv` 为**确定性生成物**
> ⇒ R1 / R2 / R3 / R4 四次运行的 sha256 均为 `83d3bf349be52251…`（**逐字节一致**，可复现性证据）。
> `LATEST_SIGNALS.md` 本轮重跑 sha256 **未变**（`99f284f701f23b94…`）—— 因信号面 as-of 仍为 2026-09-30（语料冻结）。
> 🔧 **R4 登记勘误（如实）**：R3 §A 曾把 `daily/2026-10-08.md` 记为 **130 行 / 11,565 B**（`501c76a7609f2663`）——
> 该读数为**登记时点早于 PM 版定稿**所致；文件**实际定稿**为 **171 行 / 17,567 B**（`da49cef51e192b9c`，与 git HEAD 一致）。
> R4 **按实际值修正**，**不改文件内容**。

## B. 价格数据（38 标的 · 逐文件登记）

> 目录级指纹（口径：**对 `prices/*.json` 逐文件 sha256（全 64 位）排序后以 `\n` 连接，再取 sha256 前 16**）＝
> `8699b2b2b16407cf`（38 个文件 · 合计 **2,561,195 B**，最大单文件 104,647 B ≪ 5 MB ⇒ 全部入 git）。
> ✅ **末日一致性（R4 起全部整齐）**：**38/38 标的末日均为 2026-10-08** —— 相对 R3 的变化仅 10 条汇率
>（2026-10-07 → 2026-10-08；`USDCNY` 2026-09-30 → 2026-10-08）；其余 28 个文件末日未变、行数据逐字节相同。
> 上市/可得日 ≠ 2016 的标的见「区间」列（**幸存者偏差**，🚫 不插值）。

| 路径 | 名称 | 类 | 行数 | 大小(B) | sha256(前16) | 存放 | 区间 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `signal/prices/AU0.json` | 沪金 | fut | 2612 | 62224 | `9879d102aab8c7ba` | git | 2016-01-04~2026-10-08 |
| `signal/prices/AUDCNY.json` | 澳元 | fx | 2810 | 98041 | `20c3b6ea495735be` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CADCNY.json` | 加元 | fx | 2810 | 98828 | `fba38a1571563ccf` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CHFCNY.json` | 瑞郎 | fx | 2808 | 98322 | `672cff9dcd0bc5d0` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CU0.json` | 沪铜 | fut | 2612 | 65841 | `4420055d808691ec` | git | 2016-01-04~2026-10-08 |
| `signal/prices/EURCNY.json` | 欧元 | fx | 2808 | 98505 | `ce699fc5a442480d` | git | 2016-01-01~2026-10-08 |
| `signal/prices/GBPCNY.json` | 英镑 | fx | 2810 | 98109 | `12154728cc16700c` | git | 2016-01-01~2026-10-08 |
| `signal/prices/HKDCNY.json` | 港币 | fx | 2810 | 101214 | `c28ffd409a2003f0` | git | 2016-01-01~2026-10-08 |
| `signal/prices/I0.json` | 铁矿石 | fut | 2613 | 60625 | `4cffb10153637ba2` | git | 2016-01-04~2026-10-08 |
| `signal/prices/JPYCNY.json` | 日元 | fx | 2808 | 104647 | `b4273b9e9ed55e77` | git | 2016-01-01~2026-10-08 |
| `signal/prices/M0.json` | 豆粕 | fut | 2612 | 63067 | `db38e3b393572da2` | git | 2016-01-04~2026-10-08 |
| `signal/prices/NZDCNY.json` | 新西兰元 | fx | 2810 | 98573 | `b70cad98d38e2b9c` | git | 2016-01-01~2026-10-08 |
| `signal/prices/RB0.json` | 螺纹钢 | fut | 2612 | 63071 | `f679073009dad19c` | git | 2016-01-04~2026-10-08 |
| `signal/prices/SC0.json` | 原油(INE) | fut | 2069 | 47972 | `c940cac1c6e7cd75` | git | 2018-03-26~2026-10-08 |
| `signal/prices/SGDCNY.json` | 新元 | fx | 2810 | 98643 | `db8a7a7e376c548a` | git | 2016-01-01~2026-10-08 |
| `signal/prices/TA0.json` | PTA | fut | 2609 | 62993 | `3f4bc2b71f0bd295` | git | 2016-01-04~2026-10-08 |
| `signal/prices/USDCNY.json` | 美元 | fx | 2786 | 97835 | `fb28b1007cf4155d` | git | 2016-01-01~2026-10-08 |
| `signal/prices/sh601138.json` | 工业富联 | stock | 2020 | 47679 | `cbc6fe0ae4dc484d` | git | 2018-06-08~2026-10-08 |
| `signal/prices/sh601360.json` | 三六零 | stock | 2490 | 59442 | `b489a8ff92771996` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sh603019.json` | 中科曙光 | stock | 2599 | 61628 | `9c015f7f7cd48c24` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sh603986.json` | 兆易创新 | stock | 2252 | 54803 | `5f0d9c84aac0e41c` | git | 2016-08-18~2026-10-08 |
| `signal/prices/sh688012.json` | 中微公司 | stock | 1739 | 43346 | `fc5caba9d4b6c22e` | git | 2019-07-22~2026-10-08 |
| `signal/prices/sh688041.json` | 海光信息 | stock | 994 | 24872 | `933273cdb5665c30` | git | 2022-08-12~2026-10-08 |
| `signal/prices/sh688111.json` | 金山办公 | stock | 1669 | 42085 | `b6061f2a1e14a21a` | git | 2019-11-18~2026-10-08 |
| `signal/prices/sh688256.json` | 寒武纪 | stock | 1507 | 37785 | `5dcf49d88daa6072` | git | 2020-07-20~2026-10-08 |
| `signal/prices/sh688981.json` | 中芯国际 | stock | 1503 | 35517 | `b452aa5dccb09268` | git | 2020-07-16~2026-10-08 |
| `signal/prices/sz000977.json` | 浪潮信息 | stock | 2599 | 62485 | `f28a24ba5eeb9a03` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002230.json` | 科大讯飞 | stock | 2564 | 61932 | `659cc00759913265` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002241.json` | 歌尔股份 | stock | 2612 | 62990 | `101d6b3d77b559f8` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002371.json` | 北方华创 | stock | 2602 | 64690 | `c7281f2a7b122480` | git | 2016-01-11~2026-10-08 |
| `signal/prices/sz002463.json` | 沪电股份 | stock | 2612 | 61255 | `8276b1598b3b3f2d` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002475.json` | 立讯精密 | stock | 2611 | 62769 | `64fed571302798e9` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002594.json` | 比亚迪 | stock | 2612 | 63678 | `dbb0ac312f64e445` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002747.json` | 埃斯顿 | stock | 2564 | 60973 | `465f7425b05eaf97` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300124.json` | 汇川技术 | stock | 2601 | 62896 | `7a92992baab90b58` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300308.json` | 中际旭创 | stock | 2468 | 59839 | `6b59fb943478d376` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300502.json` | 新易盛 | stock | 2572 | 61375 | `a21e3fd39b007c26` | git | 2016-03-03~2026-10-08 |
| `signal/prices/sz300750.json` | 宁德时代 | stock | 2019 | 50646 | `1690b3ef599faadf` | git | 2018-06-11~2026-10-08 |

> **类目覆盖核对（第11批硬指标）**：A股 **21** ≥ 20 ✅ · 汇率 **10**（USD/AUD/CAD/CHF/EUR/GBP/HKD/JPY/NZD/SGD vs CNY）✅ · 大宗 **7**（沪金 AU / 沪铜 CU / 铁矿 I / 豆粕 M / 螺纹 RB / 原油 SC / PTA TA）✅ · **合计 38**。
> **十年覆盖核对**：全部标的区间 **≥ 6.6 年**（最短 `sh688041` 自 2022-08-12，因其 2022 上市）；**21/38 自 2016 起**（汇率 9/10、大宗 6/7、个股 6/21）。
> ⚠️ **未复权 + 主力连续**：个股为**不复权**收盘价（除权日会跳空）；大宗为**主力连续**（换月跳空可能混入）
> ⇒ `lag_corr.py` 用**对数收益**、并**剔除 |日收益| > 30%** 的异常点（见 `LAG_CORR.md` §方法）；**本表只登记数据**，不做价格修正。
