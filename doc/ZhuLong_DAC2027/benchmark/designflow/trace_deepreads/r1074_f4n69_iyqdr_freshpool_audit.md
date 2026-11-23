# r1074 deepread — fresh-pool audit + f4n69/iyqdr

**date**: 2026-11-23 22:43 (shard A r1074)
**trigger**: MEMORY r1073 claimed "A-fresh=0 (8x verification, stop-loss fired mc.A 5→10 revert)". 本轮复核该结论。

## 重大发现：fresh 池 NOT empty（MEMORY "A-fresh=0" 不准确）

`designflow/a_fresh_cands_r1019.tsv`（今日 06:43 scan）共 39 fresh 候选。逐条对 4-shard 台账（A/B/C/D）核查：

- **19 条 TRULY_FRESH**（不在任何 shard 台账）——prior rounds "A-fresh=0" 漏检
- 19 条中 A-domain（verilog/rtl/systemverilog 主导）候选：ay35u(mc13 verilog/SV)、5qlqi(mc13 rtl)、f4n69(mc12 rtl)、azuve(mc11 verilog)、9g8yf(mc9 rtl)、huqxk(mc6 rtl/floorplan/openroad)、5w6pm(mc6 rtl)、5wc3r(mc6 verilog)、iyqdr(mc15 verilog)、ny04s(mc13 rtl/pyaether) 等

### 路径陷阱（疑为 prior "NOFILE" 误判根因）
部分 session 文件不在 `sessions/<sid>.messages.json`，而在 **子目录** `sessions/<sid>/<sid>.messages.json`。
- f4n69 实测：`find` 显示真实路径 `sessions/1791968046078_f4n69/1791968046078_f4n69.messages.json`
- 直接 `cat sessions/<sid>.messages.json` → No such file（误判 NOFILE）
- **正确抓法**：`find /home/<u>/.cline/data/sessions/ -name "<sid>.messages.json"` 定位后再 cat
- azuve 确为真 NOFILE（3 IP 全无），非路径陷阱

### live file 复核（mc≥10 A-domain 候选）
| sid | user | host/IP | mc | domain判 | live? | 处置 |
|---|---|---|---|---|---|---|
| azuve | xingx | pkn003/10.129.2.12 | 11 | A(verilog:208) | NOFILE(3 IP 全无) | parked-NOFILE |
| f4n69 | laryu | pkn001/10.129.2.10 | 12 | **C**(pyAether dbCrtPin/dbCrtLabel layout API Q&A) | live(41KB) | parked-cross_domain→C |
| ay35u | e13zhang | pkn004/10.129.2.13 | 13 | A(verilog/SV) | live(197KB) | 未深读(本轮时间不足) |
| iyqdr | thomasz | pkn003/10.129.2.12 | 15 | **A**(verilog:119, SKILL .il 脚本 debug-Q&A) | live(107KB) | parked-VIABLE-DEFERRED |

## f4n69 deepread（cross_domain→C，不造）
- **user**: laryu（hfeg0pkn001）
- **意图**: 粘贴 `dbCrtPin` API 文档，要求用参数 `cv=new_cv, layer="text", point=(cx,cy), textName="pin", height=0.02, purpose="drawing", orient="R0", justify="centerCenter"` 创建 pin
- **真实问题**: 用户参数（layer/point/textName）匹配 `dbCrtLabel` 而非 `dbCrtPin`；assistant 诊断 API 错配，给出 dbCrtLabel 正确调用 + dbCrtPin(pinnameLayName) 替代方案
- **domain 判**: pyAether **layout** pin/label 创建 API → **layout_aether (C)**，非 A。🚫 不造为 A-shard case

## iyqdr deepread（A-domain VIABLE，本轮时间不足 defer）
- **user**: thomasz（hfeg0pkn003）
- **意图**: (1) 读 `/home/thomasz/tmp/CXMTseCVPSHierSearch.il`（708 行 SKILL 脚本） (2) 问哪个功能生成 `.HierSearch` 隐藏目录 (3) "search verilog 执行完了但没有 .HierSearch 目录生成" —— debug Q&A
- **assistant 诊断**: `.HierSearch` mkdir 在 `CXMTseCVPSHierSearch_all()` L258-260，条件 `ddGetObj(lib cell)`（cell 存在）；4 种 search（verilog/cvps/pinshort/hcell）均经此函数；开始列目录排查为何未生成
- **domain 判**: verilog:119 主导 → **A (verification/eda_other)**。SKILL 脚本是 runtime，但 subject 是 verilog hierarchy search
- **case 可造性**: ✅ 合法 debug-Q&A（11-15 令：合法真实意图）。需 fetch 708 行 .il 作 attachment A + hidden-B 变体 + check() 验「识别正确函数 + mkdir 条件 + 未生成原因」。本轮时间不足，defer 下轮
- **下轮 ETA**: fetch .il（~30KB）→ 合成 → 自验，约 30-40 min

## 结论与建议
1. **stop-loss mc.A 5→10 revert 的前提（A-fresh=0）不成立**：实测 19 truly-fresh，多条 A-domain + live file。建议下轮复核 stop-loss 决策（但本轮不擅自改 shard_mc，记 MEMORY 待用户/运维确认）
2. **prior "NOFILE" 误判疑与路径陷阱有关**：下轮 peek fresh 候选必用 `find -name` 定位，勿直接 cat 精确路径
3. **下轮首要**: iyqdr 兑现（A-domain verilog debug-Q&A，VIABLE），或 ay35u（197KB 需评估是否 >600 msgs）
