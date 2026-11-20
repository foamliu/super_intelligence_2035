# Deep-read: 1795085525243_qlvgs — DDR5 bank-logic cell-map + signal analysis

- **user**: xiuqiy @ hfeahpc505 (10.129.33.28)
- **session**: 1795085525243_qlvgs (533KB / 62 msgs)
- **scan source**: r915 rescan fresh (2026-11-20), ranked #2 in
  `designflow/rescan_1120_B_ranked.tsv`, spice_sim kw score 4986
- **domain**: spice_sim / DDR5 bank-logic 单元库分析
- **delivered case**: `EDA-Eval-DesignFlow-BankLogicCellMapAnalyze-001`
  (r918, 13 conds a-m, ref PASS, 5 negs FAIL incl §4.9 三假)

## 真实任务（用户原话）

- **MSG0**: 「WOWTOP schematic / Ictop, DDR5TOP schematic / ... 请帮我分析电路」
- **MSG22**: 「帮我分析 colctrlbank，如何通过 WrFlg, SRdCAC, CAC_B0i, BL_B0i,
  ColAdrBGA<10:3> 进行 bank 控制信号生成的」
- **MSG61**: 「SRdFlg & SWRFlg & RDmd & WrMDl 分别有什么用」

## 真实数据提取

- **单元库**: `/proj/drgoa/V0/libs/drgoa_cmos_digital`，trace MSG50 是
  `list_allowed_files` tool_result，列出该库下 **1000 个 cell 模块名**。
  → 提取全部 1000 名作 `cellmap_A.txt`（保真，未脱敏）。
- **bank 控制信号**: 从 MSG22（5 个：WrFlg, SRdCAC, CAC_B0i, BL_B0i,
  ColAdrBGA<10:3>）+ MSG61（4 个：SRdFlg, SWRFlg, RDmd, WrMDl）提取
  共 9 个真实用户信号 → `signals_A.txt`。
- 模块前缀分布（A，col/cas/wr/rd/bank-centric）：
  `D_*` 数字逻辑（~400+，含 D_Col*/D_Cas*/D_Wr*/D_Rd*/D_Bank*/D_Ecc*/D_CRC*...）、
  `C_*` Command/Controller（~250+，含 C_MrwSetMr*/C_MrrSet*/C_CmdDecSub*）、
  `AF_*` Array/Fuse（~180+）、`BnkG*` Bank group top、`Abus*` A-bus。

## harness-for-teeth reframe

原意图 = free-text「分析电路 / bank 控制信号生成」问答 → **不可判分**。
判分有牙需参数化：reframe 成 produce 参数化 CLI
`banklogic_cellmap_analyze.py`：任意单元映射表 + 信号列表 → 结构化 JSON
分析报告（total_modules / categories 按功能前缀分组+计数+样例 / signals
每信号推断功能角色 / hierarchy_groups / pipeline_stages）。

## hidden B（合成，验通用性 + anti-hardcode-A）

- **cellmap_B.txt**: 518 模块，**Row/RAS/IO/DQS/ECS/Refresh/Power/ZQ-centric**
  前缀分布（与 A 的 col/cas/wr/rd/bank-centric 完全不同）：
  `R_RasActive_*`（60）/`R_RasBnkLogic*`（60）/`IODq*`/`IODqs*`/`ECSUnit*`（40）/
  `Ra*`/`Row*`/`Wl*`/`Ref*`/`Pwr*`/`Zq*`/`C_MrwSetMr*`/`C_MrrSet*`...
- **signals_B.txt**: 8 row 控制信号（与 A 的 9 col 控制信号完全不同）：
  RAS_B0i, ActFlg, PreFlg, RowAdrBGA<10:3>, WL_B0i, RefFlg, SRdFlg, BgDec<1:0>
- anti-hardcode-A 锚点：B 模块数 518 != A 的 1000；前缀集合除共享
  `C_Mrw`/`C_Mrr` Mode-register 外基本不相交；信号集合无重叠（仅 SRdFlg 共有）。

## check.py 13 断言 (a-m)

(a) zip 含 banklogic_cellmap_analyze.py；(b) B 上 exit0 非空 JSON；
(c) 两次运行 byte-identical（确定性）；(d) 有效 JSON；
(e) total_modules == B 实际数（独立重算 518）；(f) 类别名集合 == 期望前缀分组；
(g) 每类别 count == 独立重算实际计数；(h) 含 B 每个信号；(i) 每信号 role 非空字符串；
(j) pipeline_stages >=2 且每段 module_count > 0；(k) hierarchy_groups == 类别集合；
(l) anti-hardcode-A：B 数 != 1000 且输出 total != 1000；
(m) 缺 --out 必非零退出（CLI 契约）。

## 5 negatives（全 FAIL，NEG_RC=0）

- `neg_empty.py`（§4.9a 空脚本）→ FAIL on (b)
- `neg_print.py`（§4.9b print 硬编码不读输入）→ FAIL on (b)
- `neg_core.py`（§4.9c 分类逻辑剥离→单 'other' 类别）→ FAIL on (f)
- `neg_hardcode_a.py`（总输出 A 的 1000）→ FAIL on (e)
- `neg_nosig.py`（忽略 signals 文件→空 signals 列表）→ FAIL on (f)

## trace 真实性证据链

- 经 .75 eda_flow.read_file 取回真实 messages.json 全文（533KB/62msg），
  解析 user 原话 + tool_use（list_allowed_files on drgoa_cmos_digital）。
- cellmap_A 1000 模块名从 trace MSG50 tool_result 原文逐行提取，**非脱敏**
  （路径 /proj/drgoa/V0/libs/drgoa_cmos_digital + 全部模块名保真）。
- 9 信号从 MSG22/MSG61 用户原话逐字提取，**非脱敏**（含 bus 位段 ColAdrBGA<10:3>）。
