# 8tchb — FineSim cosim pvint 未定义诊断（A-faithful deepread）

## trace
- user: easont, host: hfeg0pkn004
- session: 1793172979841_8tchb (272 msgs, 1.5MB, mtime Oct 30 16:21)
- spice keyword matches: 128 (hspice/finesim/simulator/spice)
- shard B spice_sim, hfeg0pkn004 cron 盲区 not-in-ledger 候选（11-05 重扫令持续履行）

## U#0 逐字（A-faithful 任务说明轮，提出需求，无根因/修复 → 符合 A-档选轮）
`/proj/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_RowControl_schematic_ALPS_sim/cosim_check/cosim/1067tt25/cosim.log ; debug这个仿真流程，找到Error的原因`

后续用户轮（U#19 import netlist / U#77 netlist import / U#91 measure_spf / U#106 measure_AI）为不同话题，不入 prompt。

## 金标准（assistant A#18 完整诊断报告）
仿真工具 = FineSimPro V-2023.12-1 + VCS R-2020.12 cosim；设计 = ddgoa_cmos_digital_RowControl (LPDDR5)；PVT = 1067tt25 (ptemp=45, tt corner)。

**根本原因：`pvint` 参数从未被定义。** PVT 文件 `1067tt25.sp` 第 27 行 `**.param pvint = pvdd2h` 被 `**` 注释掉（SPICE 整行注释）→ pvint 不存在。

**19 个 ERROR 全部源自 pvint 缺失的级联：**
| ERROR 位置 | 表达式 | 原因 |
|---|---|---|
| hspice0.94v.voltage:33 | .param pvbp = pvint*1.1 | pvint 未定义 |
| common_new.env:3 | .param pvccsc = pvint | pvint 未定义 |
| common_new.env:43 | vint vint! 0 dc=pvint | pvint 未定义 |
| common_new.env:61 | .param pvpgint = pvint+pvth | pvint 未定义 |
| common_new.env:62 | .param pvpgintbus = pvintbus+pvth | pvintbus 未定义 |
| common_new.env:64 | .param pvpgvblh = pvblh+pvth | pvth 作用域 |
| common_new.env:65 | .param pvpgvcsl = 0.9+pvth | pvth 作用域 |
| common_new.env:26,56,127,132,134 | vbp ... dc=pvbp | pvbp=pvint*1.1 依赖 pvint |
| common_new.env:136-147 | vintcore/vintio/vFsCompRef/... | 全部依赖 pvint |

19 ERROR 明细（log 行号 111-144）：
1. pvbp unresolved (common_new.env:26)
2. pvint undefined (common_new.env:43)
3. pvintbus undefined (common_new.env:45)
4. pvpgint unresolved (common_new.env:46)
5. pvpgintbus unresolved (common_new.env:47)
6. pvpgvblh unresolved (common_new.env:51)
7. pvbp unresolved (common_new.env:56)
8. pvbp unresolved (common_new.env:127)
9. pvbp unresolved (common_new.env:132)
10. pvbp unresolved (common_new.env:134)
11-19. pvint undefined (common_new.env:136,137,138,140,141,143,144,145,146) ×9

**关键 log 标志：**
- 行 176: `# ERRORs: 19`
- 行 188: `Time: 0 ps`（瞬态仿真从未启动）
- 行 193: `FineSim Completed with error(s)`

**次要问题：** pvth 模型参数作用域（WARNING 非 ERROR）；ptemp=45 不匹配温度分支（-40/25/130）。

**修复：** 取消注释 PVT 文件第 27 行 `**.param pvint = pvdd2h` → `.param pvint = pvdd2h`。

## 通用化（reference）
diag_cosim_param_error.py <cosim.log> <pvt.sp> -o out.json
- parse_log_errors: 正则 `ERROR!` → {kind(unresolved/undefined), param, source_file, source_line}
- parse_summary: `# ERRORs: N` / `Time: ...` / `Completed with error(s)`
- find_commented_params: 扫 pvt.sp `**` 注释行含 `.param X =` → commented[]
- root_cause = commented param X 出现在 ERROR 的 param 集合中
- cascade_params = ERROR 中 unresolved/undefined 但 != root_cause 的参数

## 合成
- A = 真实 cosim_A.log(194行原文) + pvt_A.sp(31行原文, line 27 `**.param pvint = pvdd2h`) + voltage_A.txt + env_A.txt
- hidden B = 合成不同根因: pvblh 被注释, 11 ERROR, 不同级联参数
- 判分 14 断言(a-n): 含交叉输入守卫(k: A 跑得 pvint) + A-only 泄漏闸门(l: B 不含 pvint/1067tt25) + 3次幂等(m)
