# Deepread: pr0tt — Calibre LVS short 报错提取 + PG short 几何定位

- **session**: `1793095792921_pr0tt.messages.json` (ziyuny / 10.129.32.190 / mc=171)
- **keywords**: cmos:992;lvs:794;calibre:198;.gds:9;.cdl:9
- **size**: 88 msgs / 991 KB / 2 user_input turns / agent cline(lead) glm-5.2
- **cwd**: /home/ziyuny
- **ledger**: claimed r385 → marked case `EDA-Eval-DesignFlow-LVSShortExtract-001` (physical_verify, L1, B-synthesized/faithful seed)

## 用户原话（逐字）

- **USER[0]**: `你知道calibre结果中，/proj/drexp/V0/ver/lvs/drexp_top/MiniCMOS_WOW_Top_1010中的short报错有哪些吗？`
- **USER[38]**: `shorts 文件（7061 行）中有 2 个真实 short：SHORT 1: vcc! - vss! 和 SHORT 2: vdd1! - vtsc!（均在顶层 MiniCMOS_WOW_Top） 对于short1，应该是一个不小的power ground short网络，你能帮我定位到具体是在版图哪个地方short吗？`

## assistant 工具链（turn 1 — short 提取 + 终态 + ext 计数）

1. 加载 `lvs-debuger` skill（深报模式：单 LVS 结果目录）。
2. `list_allowed_files` 探查 rundir → 找到 `MiniCMOS_WOW_Top.lvs.report.shorts` / `MiniCMOS_WOW_Top.lvs.report` / `runlvs.log` / `.ext`。
3. `read_files` 读 shorts 头 2000 行 + report 250 行 + log 120 行 → 看到 `SHORT 1.  vcc! - vss! in MiniCMOS_WOW_Top` + `2 Shorted texts: "vcc!" at (-238.030, 3352.080) on layer "FPA_pin"`。
4. 写 4 个只读 python 扫描脚本（`lvs_scan{,2,3,4}_MiniCMOS_WOW_Top_1010.py`，python-runner 执行）：
   - scan1: 目录结构 + shorts 全结构 + report/log 关键字
   - scan2: SHORT 2 详情 + supply error 上下文 + ext 头部
   - scan3: BY CELL 多边形归属 cell（CN 行）+ HCELL-not-located 清单
   - scan4: ext 报告精确警告计数

## 关键事实（turn 1）

- **2 个真实 short**：SHORT 1 `vcc! - vss!`（顶层 MiniCMOS_WOW_Top，65 polys / 6 layers，2 texts：vcc! @ (-238.030,3352.080) FPA_pin SN 1；vss! @ (-238.030,2506.080) FPA_pin SN 1076）；SHORT 2 `vdd1! - vtsc!`（18 polys / 4 layers，vdd1! @ (-238.030,3728.080) SN 2000；vtsc! @ (-238.030,1660.080) SN 2050）。
- **LVS 终态**：runlvs.log:64174 `ERROR: Supply error detected. ABORT ON SUPPLY ERROR is specified - aborting.` → `Exit Code: 4`；`lvs.report` = 0 字节（SVS 比对从未执行）。rule deck:30 `LVS ABORT ON SUPPLY ERROR YES`，:35 `LVS ISOLATE SHORTS YES BY LAYER ALSO BY CELL ALSO`。
- **ext 警告计数**：65 BAD DEVICE on POLY_DIFF_BAD + 5 `Short circuit - Different names on one net` + 28 `Open circuit - Same name on one net` + 8 `Unattached port` = **106 total**（精确吻合）。
- **短路点**（turn 2 几何定位）：vcc! 侧 9 形状（FPA 板 SN 4 → M6 竖条带 SN 21 CMOS_QuarterDie1），vss! 侧 56 形状；两网唯一搭接 = **V5 via SN 71 @ (-3.96, 3879.96) µm**（vcc! M6 条带 21 经此 V5 落到 vss! M5 水平轨道 72 Channel_1 y≈3879.5）。48 条桥接边构成短路链。

## shorts 文件格式（合成 case 依据）

```
<topcell> <maxshorts>
SHORT <N>.  <netA> - <netB> in <cell>
<poly_count> <poly_count> <layer_count> <timestamp>
<N> Shorted texts:
  "<name>" at (<x>, <y>) on layer "<layer>" SN <sn>
BY CELL:
  CN "<cellname>"   <n> polys
BY LAYER:
  Layer "<layer>"   <n> polygons
```
- 计数行：`<poly_count> <poly_count> <layer_count> <timestamp>`（第一、二个数都是 poly 数，第三个是 layer 数 = BY LAYER 节数）。
- 只认顶层 `SHORT N.` 头开块；BY CELL / BY LAYER 分节内的行不是新 SHORT。

## 本 case 取舍

- **取 turn-1 可交付核心**（shorts 提取 + 终态 + ext 计数）= L1 physical_verify case `EDA-Eval-DesignFlow-LVSShortExtract-001`，12 条断言 (a)-(l)，隐藏 B 结构不同（DDR5_TOP / 3 shorts / clean INCORRECT exit 0 / ext 18）。
- **turn-2 几何定位（L3）留作扩展**：需合成完整 shorts DB（main/BY CELL/BY LAYER + SN-joined 多边形 + via 连通图 + 桥接边），工作量大，本轮 40min 预算不足；下轮可做 `EDA-Eval-DesignFlow-LVSShortLocalize-001`（L3）覆盖 turn-2。

## 选料过滤 bug 修正（重要）

本轮发现 `candidates_mc10.tsv` 的 `session_file` 不带 `.messages.json` 后缀，而 `trace_ledger_C.tsv` column-0 带后缀 —— 直接字符串比对会把已 case 的 session 误判为 fresh。正确做法：比对前 `re.sub(r'\.messages\.json$','',sf)` 双向归一。本轮已据此重出 fresh 池（1151 truly fresh / 32x-OK 230）。前若干轮「fresh 池」结论若未做后缀归一，可能含此误差。
