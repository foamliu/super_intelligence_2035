# INDEX_FILES — news/signal 文件清单（第11批 · **R3** 重登记）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**（最大单文件 = `prices/JPYCNY.json` 104,609 B）。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。
> ⏱ **本次更新（R3 · 2026-10-08 晚报轮）**：**38 标的十年价格全量刷新完成**（`ok=38 / fail=0`）⇒
> §A 全部重登记 + §B **逐文件**重登记（38 行）；`lag_corr.csv` 重跑后**与 R2 逐字节一致**（sha 未变）。

## A. 代码 · 文档 · 生成物

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/fetch_prices.py` | 326 | 14993 | `bb89bc45b29288be` | git |
| `signal/lag_corr.py` | 573 | 27044 | `e783e99c984cb729` | git |
| `signal/signal_snapshot.py` | 104 | 4751 | `c82e42b942999b32` | git |
| `signal/make_findings.py` | 133 | 7583 | `f72834e9a8274267` | git |
| `signal/block_boot.py` | 287 | 14639 | `d0ec0a0f782397cf` | git |
| 🆕 `signal/am_pm_check.py` | 161 | 7739 | `0211a563969378a3` | git |
| `signal/PREREG.md`（**先于结果**） | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md`（源实测） | 55 | 4941 | `831394faa87d39e3` | git |
| `signal/lag_corr.csv`（全网格 23940 格） | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/LAG_CORR.md`（R3 复核头） | 90 | 7570 | `958d28065b1d6f16` | git |
| `signal/FINDINGS.md`（结论台账） | 52 | 5272 | `e23f0c4d6c18fe36` | git |
| `signal/BOOTSTRAP.md`（块自助 CI） | 83 | 8096 | `bed9522efd27e529` | git |
| `signal/LATEST_SIGNALS.md`（信号快照） | 118 | 5851 | `99f284f701f23b94` | git |
| 🆕 `signal/AM_PM_CHECK.md`（早报→晚报复核） | 96 | 6076 | `f217c73f8097551d` | git |
| 🆕 `signal/daily/2026-10-08.md`（日报 AM+PM） | 130 | 11565 | `501c76a7609f2663` | git |

> ⚠️ 上表 `LAG_CORR.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `daily/*.md` 为**生成物或当轮产物**，
> sha 每轮会变；此处记录 **R3（2026-10-08 晚报轮）** 指纹。`lag_corr.csv` 为**确定性生成物**
> ⇒ R1 / R2 / R3 三次运行的 sha256 均为 `83d3bf349be52251…`（**逐字节一致**，可复现性证据）。

## B. 价格数据（38 标的 · 逐文件登记）

> 目录级指纹（口径：**对 `prices/*.json` 逐文件 sha256（全 64 位）排序后以 `\n` 连接，再取 sha256 前 16**）＝
> `a43d193489766782`（38 个文件 · 合计 **2,560,840 B**，最大单文件 104,609 B ≪ 5 MB ⇒ 全部入 git）。
> ⚠️ **末日不一致（如实标注）**：A股个股 21 + 大宗 7 = **2026-10-08**；汇率除 `USDCNY` 外 = **2026-10-07**；
> **`USDCNY` = 2026-09-30**（新浪该源当日无更新，**未补造**）。上市/可得日 ≠ 2016 的标的见「区间」列（**幸存者偏差**，🚫 不插值）。

| 路径 | 名称 | 类 | 行数 | 大小(B) | sha256(前16) | 存放 | 区间 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `signal/prices/AU0.json` | 沪金 | fut | 2612 | 62224 | `729f0accb7aa9824` | git | 2016-01-04~2026-10-08 |
| `signal/prices/AUDCNY.json` | 澳元 | fx | 2809 | 98006 | `2cd04ba8a3f4fb9b` | git | 2016-01-01~2026-10-07 |
| `signal/prices/CADCNY.json` | 加元 | fx | 2809 | 98794 | `aa63cfc276d24278` | git | 2016-01-01~2026-10-07 |
| `signal/prices/CHFCNY.json` | 瑞郎 | fx | 2807 | 98287 | `af3247e7a4bcbc87` | git | 2016-01-01~2026-10-07 |
| `signal/prices/CU0.json` | 沪铜 | fut | 2612 | 65841 | `5b13585c93b2bd2b` | git | 2016-01-04~2026-10-08 |
| `signal/prices/EURCNY.json` | 欧元 | fx | 2807 | 98469 | `f50e2f1a6c5ea7ed` | git | 2016-01-01~2026-10-07 |
| `signal/prices/GBPCNY.json` | 英镑 | fx | 2809 | 98075 | `b3daba8237998e24` | git | 2016-01-01~2026-10-07 |
| `signal/prices/HKDCNY.json` | 港币 | fx | 2809 | 101178 | `0ab656f1674c9484` | git | 2016-01-01~2026-10-07 |
| `signal/prices/I0.json` | 铁矿石 | fut | 2613 | 60625 | `fc67f88b2592a003` | git | 2016-01-04~2026-10-08 |
| `signal/prices/JPYCNY.json` | 日元 | fx | 2807 | 104609 | `884e6987e420988e` | git | 2016-01-01~2026-10-07 |
| `signal/prices/M0.json` | 豆粕 | fut | 2612 | 63067 | `cda495b0a229c518` | git | 2016-01-04~2026-10-08 |
| `signal/prices/NZDCNY.json` | 新西兰元 | fx | 2809 | 98537 | `b26a53357769d2e9` | git | 2016-01-01~2026-10-07 |
| `signal/prices/RB0.json` | 螺纹钢 | fut | 2612 | 63071 | `f2258832c8ebfd42` | git | 2016-01-04~2026-10-08 |
| `signal/prices/SC0.json` | 原油(INE) | fut | 2069 | 47972 | `a841903ff4d6f504` | git | 2018-03-26~2026-10-08 |
| `signal/prices/SGDCNY.json` | 新元 | fx | 2809 | 98607 | `c2ca2977b68777fa` | git | 2016-01-01~2026-10-07 |
| `signal/prices/TA0.json` | PTA | fut | 2609 | 62993 | `01a51ab907e3dfa0` | git | 2016-01-04~2026-10-08 |
| `signal/prices/USDCNY.json` | 美元 | fx | 2785 | 97800 | `cd4d03b714dfa89b` | git | 2016-01-01~**2026-09-30** |
| `signal/prices/sh601138.json` | 工业富联 | stock | 2020 | 47679 | `065f1007eab1259f` | git | 2018-06-08~2026-10-08 |
| `signal/prices/sh601360.json` | 三六零 | stock | 2490 | 59442 | `23617e7e6a5ef9f7` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sh603019.json` | 中科曙光 | stock | 2599 | 61628 | `af2c46a84dc58099` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sh603986.json` | 兆易创新 | stock | 2252 | 54803 | `2c54e36d738a5d76` | git | 2016-08-18~2026-10-08 |
| `signal/prices/sh688012.json` | 中微公司 | stock | 1739 | 43346 | `6d9e43829921cb62` | git | 2019-07-22~2026-10-08 |
| `signal/prices/sh688041.json` | 海光信息 | stock | 994 | 24872 | `aca30d24db799219` | git | 2022-08-12~2026-10-08 |
| `signal/prices/sh688111.json` | 金山办公 | stock | 1669 | 42085 | `d169d31f587778da` | git | 2019-11-18~2026-10-08 |
| `signal/prices/sh688256.json` | 寒武纪 | stock | 1507 | 37785 | `057677ca7722be86` | git | 2020-07-20~2026-10-08 |
| `signal/prices/sh688981.json` | 中芯国际 | stock | 1503 | 35517 | `3c24b355ecb50517` | git | 2020-07-16~2026-10-08 |
| `signal/prices/sz000977.json` | 浪潮信息 | stock | 2599 | 62485 | `3b2c4af5b480ac12` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002230.json` | 科大讯飞 | stock | 2564 | 61932 | `2bdc2419d8d82470` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002241.json` | 歌尔股份 | stock | 2612 | 62990 | `d80093b6f4eff445` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002371.json` | 北方华创 | stock | 2602 | 64690 | `6c27b0837226d4c1` | git | 2016-01-11~2026-10-08 |
| `signal/prices/sz002463.json` | 沪电股份 | stock | 2612 | 61255 | `2b908e3f0811be5e` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002475.json` | 立讯精密 | stock | 2611 | 62769 | `5ac52b719de27f30` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002594.json` | 比亚迪 | stock | 2612 | 63678 | `a6e2adc38f9c6daf` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz002747.json` | 埃斯顿 | stock | 2564 | 60973 | `3b3516ce8f219032` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300124.json` | 汇川技术 | stock | 2601 | 62896 | `00132ef4e6a62e8c` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300308.json` | 中际旭创 | stock | 2468 | 59839 | `f78e113c3369444e` | git | 2016-01-04~2026-10-08 |
| `signal/prices/sz300502.json` | 新易盛 | stock | 2572 | 61375 | `d9ce2238c7f147da` | git | 2016-03-03~2026-10-08 |
| `signal/prices/sz300750.json` | 宁德时代 | stock | 2019 | 50646 | `ca2c588a2a5c9a4f` | git | 2018-06-11~2026-10-08 |

> **类目覆盖核对（第11批硬指标）**：A股 **21** ≥ 20 ✅ · 汇率 **10**（USD/AUD/CAD/CHF/EUR/GBP/HKD/JPY/NZD/SGD vs CNY）✅ · 大宗 **7**（沪金 AU / 沪铜 CU / 铁矿 I / 豆粕 M / 螺纹 RB / 原油 SC / PTA TA）✅ · **合计 38**。
> **十年覆盖核对**：全部标的区间 **≥ 6.6 年**（最短 `sh688041` 自 2022-08-12，因其 2022 上市）；**21/38 自 2016 起**（汇率 9/10、大宗 6/7、个股 6/21）。
> ⚠️ **未复权 + 主力连续**：个股为**不复权**收盘价（除权日会跳空）；大宗为**主力连续**（换月跳空可能混入）
> ⇒ `lag_corr.py` 用**对数收益**、并**剔除 |日收益| > 30%** 的异常点（见 `LAG_CORR.md` §方法）；**本表只登记数据**，不做价格修正。

