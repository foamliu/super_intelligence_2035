# INDEX_FILES — news/signal 文件清单（第11批 · **R5** 重登记）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**（最大单文件 = `prices/JPYCNY.json` 104,647 B）。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。
> ⏱ **本次更新（R5 · 2026-10-09 晚报轮）**：**38 标的十年价格再全量刷新**（`fetch_prices.py --refetch`，`ok=38 / fail=0`）⇒ §B 逐文件重登记（38 行）。
> **正式变动的范围（如实）**：**A股 21 + 大宗 7 = 28 个标的末日 2026-10-08 → 2026-10-09**；
> **汇率 10/10 末日仍为 2026-10-08**（**源侧当日价尚未发布** ⇒ 如实停在上日，🚫 不补造、只等源）。
> `lag_corr.csv` 重跑后**仍与 R1/R2/R3/R4 逐字节一致**（sha256 `83d3bf349be52251…`，**第 5 次可复现性通过**）。
> 🛡 `am_pm_check.py` R5 新增**台账护栏**（0 对照格时默认拒写）⇒ 复跑**未覆盖** R3 的 63 格实核台账。

## A. 代码 · 文档 · 生成物

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/fetch_prices.py`（代码） | 326 | 15008 | `af25a695577989cd` | git |
| `signal/lag_corr.py`（代码） | 574 | 27381 | `06c0d60bafba2e92` | git |
| `signal/signal_snapshot.py`（代码） | 104 | 4751 | `c82e42b942999b32` | git |
| `signal/make_findings.py`（代码） | 148 | 9528 | `398048e02ec4a2ad` | git |
| `signal/block_boot.py`（代码） | 287 | 14639 | `d0ec0a0f782397cf` | git |
| `signal/am_pm_check.py`（代码 🛡R5护栏） | 179 | 9188 | `88b2023d1e37ce49` | git |
| `signal/PREREG.md`（**先于结果**） | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md`（源实测） | 55 | 4941 | `450129125902a833` | git |
| `signal/lag_corr.csv`（全网格 23940 格） | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/LAG_CORR.md`（**R5** 复核头） | 90 | 7891 | `663036b88f23e120` | git |
| `signal/FINDINGS.md`（结论台账） | 55 | 7688 | `830c2b2be7932426` | git |
| `signal/BOOTSTRAP.md`（块自助 CI） | 83 | 8096 | `bed9522efd27e529` | git |
| `signal/LATEST_SIGNALS.md`（信号快照） | 118 | 5851 | `99f284f701f23b94` | git |
| `signal/AM_PM_CHECK.md`（R3 台账+R5 说明） | 113 | 7826 | `217b72f89d35f86e` | git |
| `signal/daily/2026-10-08.md`（日报 AM+PM） | 171 | 17567 | `da49cef51e192b9c` | git |
| `signal/daily/2026-10-09.md`（日报 PM · R5） | 145 | 18753 | `a5c3c956025ba237` | git |

> ⚠️ 上表 `LAG_CORR.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `daily/*.md` 为**生成物或当轮产物**，
> sha 每轮会变；此处记录 **R5（2026-10-09 晚报轮）** 指纹。`lag_corr.csv` 为**确定性生成物**
> ⇒ R1 / R2 / R3 / R4 / R5 五次运行的 sha256 均为 `83d3bf349be52251…`（**逐字节一致**，可复现性证据）。
> `LATEST_SIGNALS.md` 本轮重跑 sha256 **未变**（`99f284f701f23b94…`）—— 因信号面 as-of 仍为 2026-09-30（语料冻结）。
> 🛡 **R5 台账护栏（如实记）**：`am_pm_check.py` 于 R5 复跑得 **0 对照格**（价格末日已越过 as-of 的 `k=1` 目标位）⇒
> 新增护栏**拒写**，`AM_PM_CHECK.md` **保留 R3 实核台账**并追加 `## 📌 R5 复跑说明`（**未用 null 覆盖实核**，§4-9）。
> 🔧 **R4 登记勘误（如实）**：R3 §A 曾把 `daily/2026-10-08.md` 记为 **130 行 / 11,565 B**（`501c76a7609f2663`）——
> 该读数为**登记时点早于 PM 版定稿**所致；文件**实际定稿**为 **171 行 / 17,567 B**（`da49cef51e192b9c`，与 git HEAD 一致）。
> R4 **按实际值修正**，**不改文件内容**。

## B. 价格数据（38 标的 · 逐文件登记）

> 目录级指纹（口径：**对 `prices/*.json` 逐文件 sha256（全 64 位）排序后以 `\n` 连接，再取 sha256 前 16**）＝
> `0928c6631ed5b343`（38 个文件 · 合计 **2,561,853 B**，最大单文件 104,647 B ≪ 5 MB ⇒ 全部入 git）。
> ✅ **末日一致性（R5 起）**：**A股 21 + 大宗 7 = 28/38 末日 = 2026-10-09**；**汇率 10/38 末日 = 2026-10-08**（**源侧当日价尚未发布** ⇒ 如实停在上日，🚫 不补造）。
> 上市/可得日 ≠ 2016 的标的见「区间」列（**幸存者偏差**，🚫 不插值）。

| 路径 | 名称 | 类 | 行数 | 大小(B) | sha256(前16) | 存放 | 区间 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `signal/prices/AU0.json` | 沪金 | fut | 2613 | 62248 | `59a42d737ad6ef74` | git | 2016-01-04~2026-10-09 |
| `signal/prices/AUDCNY.json` | 澳元 | fx | 2810 | 98041 | `f5863044f2697a6d` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CADCNY.json` | 加元 | fx | 2810 | 98828 | `f97235b6cafde7bd` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CHFCNY.json` | 瑞郎 | fx | 2808 | 98322 | `8ad9df202dbbb0e0` | git | 2016-01-01~2026-10-08 |
| `signal/prices/CU0.json` | 沪铜 | fut | 2613 | 65867 | `19111aa1c5cd7e42` | git | 2016-01-04~2026-10-09 |
| `signal/prices/EURCNY.json` | 欧元 | fx | 2808 | 98505 | `8b16b6c35408fb57` | git | 2016-01-01~2026-10-08 |
| `signal/prices/GBPCNY.json` | 英镑 | fx | 2810 | 98109 | `02c410cade23c2f7` | git | 2016-01-01~2026-10-08 |
| `signal/prices/HKDCNY.json` | 港币 | fx | 2810 | 101214 | `f96187b7b6e75ad0` | git | 2016-01-01~2026-10-08 |
| `signal/prices/I0.json` | 铁矿石 | fut | 2614 | 60648 | `8723c066aa114076` | git | 2016-01-04~2026-10-09 |
| `signal/prices/JPYCNY.json` | 日元 | fx | 2808 | 104647 | `cd9b642ad08a0614` | git | 2016-01-01~2026-10-08 |
| `signal/prices/M0.json` | 豆粕 | fut | 2613 | 63091 | `9e135f8852641955` | git | 2016-01-04~2026-10-09 |
| `signal/prices/NZDCNY.json` | 新西兰元 | fx | 2810 | 98573 | `2b87d12a509e1d33` | git | 2016-01-01~2026-10-08 |
| `signal/prices/RB0.json` | 螺纹钢 | fut | 2613 | 63095 | `cba15aaa09a6696f` | git | 2016-01-04~2026-10-09 |
| `signal/prices/SC0.json` | 原油(INE) | fut | 2070 | 47995 | `6e5594376aad80be` | git | 2018-03-26~2026-10-09 |
| `signal/prices/SGDCNY.json` | 新元 | fx | 2810 | 98643 | `6c26323439bdfa0f` | git | 2016-01-01~2026-10-08 |
| `signal/prices/TA0.json` | PTA | fut | 2610 | 63017 | `50a2214adff92470` | git | 2016-01-04~2026-10-09 |
| `signal/prices/USDCNY.json` | 美元 | fx | 2786 | 97835 | `09eda7af0220ccad` | git | 2016-01-01~2026-10-08 |
| `signal/prices/sh601138.json` | 工业富联 | stock | 2021 | 47702 | `04b5a341b31615c8` | git | 2018-06-08~2026-10-09 |
| `signal/prices/sh601360.json` | 三六零 | stock | 2491 | 59464 | `14ffa601938119ae` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603019.json` | 中科曙光 | stock | 2600 | 61651 | `f3ee92c8f31f0892` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sh603986.json` | 兆易创新 | stock | 2253 | 54827 | `a01d2a9e94b3c047` | git | 2016-08-18~2026-10-09 |
| `signal/prices/sh688012.json` | 中微公司 | stock | 1740 | 43369 | `d33b8336c45a90f2` | git | 2019-07-22~2026-10-09 |
| `signal/prices/sh688041.json` | 海光信息 | stock | 995 | 24896 | `16ebd5abceaec806` | git | 2022-08-12~2026-10-09 |
| `signal/prices/sh688111.json` | 金山办公 | stock | 1670 | 42109 | `e1db90e21422a8f6` | git | 2019-11-18~2026-10-09 |
| `signal/prices/sh688256.json` | 寒武纪 | stock | 1508 | 37809 | `354d7ddc6227a106` | git | 2020-07-20~2026-10-09 |
| `signal/prices/sh688981.json` | 中芯国际 | stock | 1504 | 35541 | `98e25cb94ceae49a` | git | 2020-07-16~2026-10-09 |
| `signal/prices/sz000977.json` | 浪潮信息 | stock | 2600 | 62508 | `f8d1393ba42319e4` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002230.json` | 科大讯飞 | stock | 2565 | 61954 | `652b469acc586928` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002241.json` | 歌尔股份 | stock | 2613 | 63013 | `c5de29933c30bec4` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002371.json` | 北方华创 | stock | 2603 | 64714 | `2985fc2641fe0f41` | git | 2016-01-11~2026-10-09 |
| `signal/prices/sz002463.json` | 沪电股份 | stock | 2613 | 61279 | `2dff725b07f55138` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002475.json` | 立讯精密 | stock | 2612 | 62792 | `59f933f9c78147eb` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002594.json` | 比亚迪 | stock | 2613 | 63701 | `578003f2325b68d5` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz002747.json` | 埃斯顿 | stock | 2565 | 60996 | `7dd830fcc6a204f8` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300124.json` | 汇川技术 | stock | 2602 | 62919 | `e05b44f2ddbddf3e` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300308.json` | 中际旭创 | stock | 2469 | 59863 | `a728b9648c259ca2` | git | 2016-01-04~2026-10-09 |
| `signal/prices/sz300502.json` | 新易盛 | stock | 2573 | 61398 | `14e829b9dc6ecc51` | git | 2016-03-03~2026-10-09 |
| `signal/prices/sz300750.json` | 宁德时代 | stock | 2020 | 50670 | `21e0403aeea64077` | git | 2018-06-11~2026-10-09 |

> **类目覆盖核对（第11批硬指标）**：A股 **21** ≥ 20 ✅ · 汇率 **10**（USD/AUD/CAD/CHF/EUR/GBP/HKD/JPY/NZD/SGD vs CNY）✅ · 大宗 **7**（沪金 AU / 沪铜 CU / 铁矿 I / 豆粕 M / 螺纹 RB / 原油 SC / PTA TA）✅ · **合计 38**。
> **十年覆盖核对**：全部标的区间 **≥ 6.6 年**（最短 `sh688041` 自 2022-08-12，因其 2022 上市）；**21/38 自 2016 起**（汇率 9/10、大宗 6/7、个股 6/21）。
> ⚠️ **未复权 + 主力连续**：个股为**不复权**收盘价（除权日会跳空）；大宗为**主力连续**（换月跳空可能混入）
> ⇒ `lag_corr.py` 用**对数收益**、并**剔除 |日收益| > 30%** 的异常点（见 `LAG_CORR.md` §方法）；**本表只登记数据**，不做价格修正。
