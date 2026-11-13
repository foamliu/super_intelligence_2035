# Deepread: 1794461147267_g4ixv — fan1yang PEX .meas 失败诊断

- **user/host**: fan1yang / hfeg0plg104 (10.129.8.236) / 新用户（ledger 0 条）
- **mc**: 41 · keywords: hspice:271;pex:246;.def:40;synopsys:34;netlist:16;mosfet:10;schematic:3;virtuoso:1
- **session**: 23 msgs（目录格式，scp 自 `.snapshot/daily-new.2026-11-12_2230/`，live sessions 已轮转只剩 qufjs/z5b4z），347KB
- **scan**: 1113 池（ssh_eda_search_20261113_131349），cross-shard(4 ledger + main jsonl)三式去重后 fresh

## 用户原话（msg 0）
> 检查该目录下的spf，sp和inv_03/sim_inv_Rev03.log文件，说明为什么measure不出来
> /rundata/lacaa/V0/simdir/finesim/workdir/fan1yang/7_post_sim/7_pex_evaluation/sim_inv/

## Agent 工具链
1. `list_allowed_files` 列 sim_inv 目录 → 发现 .sp / PEX_CASE_Rev03.spf_RCC / inv_03/sim_inv_Rev03.log / .swp / 0_run
2. `read_files` 读 sim_inv_Rev03.sp + PEX_CASE_Rev03.spf_RCC + log（tool_result 已被 cline 清空 msg4/16/17/19）
3. `run_approved_command` 多次失败（shell-runner 需 filePath / python-runner filePath 须 .py 后缀）→ 改用 `editor` 写 /home/fan1yang/check_meas.py（解析 SPF: .SUBCKT / *|I 实例行）
4. `run_approved_command python-runner /home/fan1yang/check_meas.py` 跑通 → SPF 36895 行，line22 `.SUBCKT PEX_CASE IN1..IN6 OUT1..OUT6 VDD VSS`，line 4357+ `*|I (XI_INV_M3_1.MIMN0:b ...)`
5. `read_files` 读 log 430-512 / 1-80 + SPF 36820-36895 + .elog + .mt0（tool_result 清空）
6. 再跑 check_meas.py 找 .SUBCKT/.ENDS → 仅 1 个 SUBCKT，无嵌套
7. msg22 输出完整中文诊断

## 诊断结论（agent msg22，证据扎实）
**根本原因**：SPF 是**扁平 DSPF 1.3** 格式，仅 1 个 `.SUBCKT PEX_CASE`（line22），DIVIDER=. DELIMITER=:，36895 行无嵌套子电路。PEX 工具(GloryEX RC)把所有层级展平，`XI_INV_M3_1.MIMN0` 只是扁平器件命名约定，**不存在 `XI_INV_M3_1` 子电路**。

`.meas` 语句用分层电流路径 `i(XTOP.XI_INV_M3_1.MIMN0:d)`，FineSim 把 `.` 当层级分隔符，找不到子电路 `XI_INV_M3_1` → 所有 6 条 `.meas` 失败，log line 454-459 `WARNING! can't compute 'i(...)'`。

**6 条 .meas**（.sp line 36-41）：
| .meas | line | 目标路径 | 失败原因 |
|---|---|---|---|
| cap_m3_long | 36 | XTOP.XI_INV_M3_1.MIMN0 | 扁平 SPF 无子电路 XI_INV_M3_1 |
| cap_m1 | 37 | XTOP.XI_INV_M1_3.MIMN0 | 无子电路 XI_INV_M1_3 |
| cap_m1_2 | 38 | XTOP.XI_INV_M1_1.MIMN0 | 无子电路 XI_INV_M1_1 |
| cap_inv | 39 | XTOP.XI_INV_C.MIMN0 | 无子电路 XI_INV_C |
| cap_nm0 | 40 | XTOP.MINM0 | SPF 无此器件 |
| cap_pm0 | 41 | XTOP.MIPM0 | SPF 无此器件 |

**次要问题 #1（表达式重复）**：line36/37 的 INTEGRAL 表达式前 5 项与后 5 项完全重复（`i(...MIMN0:d)+...@2:d+...@5:d` 出现两次），line38/39 同样 5 次重复。复制粘贴/通配符展开错误。

**次要问题 #2（器件不存在）**：line40/41 引用 `XTOP.MINM0`/`XTOP.MIPM0`，SPF 中所有 MOSFET 命名为 `XI_INV_*.MIMN0`（含 @2..@5 变体），无 MINM0/MIPM0。

**次要问题 #3**：`.option measform=2` 已设（INTEGRAL 正确），from=5n to=10n 在 tran 20ns 范围内，非失败根因（can't compute 在输出准备阶段、tran 之前出现）。

**实例部分**（SPF line 36828-36843）：器件直接列为 `XI_INV_C.MIMN0 XI_INV_C.MIMN0:d XI_INV_C.MIMN0:g XI_INV_C.MIMN0:s XI_INV_C.MIMN0:b nsvt_fs ...`，含 XI_INV_M1_1/M1_3/M3_1.MIMN0（@2..@5 变体）。

## A 档可行性
🚫 不可行：`/rundata/lacaa/V0/...` 对 e0031982 `head` 实测 Permission denied；read_files tool_result 已清空（msg4/16/17/19）。agent 诊断正文(msg22)持久化，可作合成依据。

## B 档合成方向
**任务**：SPF + .sp testbench + FineSim log 的 `.meas` 失败诊断器。给定扁平 DSPF SPF + 含分层 `.meas` INTEGRAL 的 .sp + 报 `can't compute 'i(...)'` 的 log，输出结构化 JSON 诊断：
- SPF 格式判定（flat DSPF / nested / subckt 数 / DIVIDER / DELIMITER）
- 逐条 .meas：目标路径、是否存在对应子电路层级、是否存在目标器件、失败原因分类（hierarchy_missing / device_missing / duplicate_terms / ok）
- 表达式重复检测（项数 vs 去重项数）
- log warning 计数 + 匹配的 .meas 名

**deliverable**：`spf_meas_diagnoser.py`（CLI 读 spf/sp/log → JSON）

**与既有 case 区分**：DeckConsistencyCheck-001(r482) 做 deck 静态一致性（drate/run_ref/corner 名），本 case 做 SPF 架构 vs .meas 路径匹配诊断 + 表达式重复 + 器件存在性，不同 deliverable 不同技能。SpiceMeasInjector-001(r485) 注入 .measure 语句，本 case 诊断 .measure 为何失败，相反方向。

## 资产
- 真实文件不可读（权限）→ 全合成
- 真实结构依据：agent msg22 诊断 + msg14/21 grep 输出（36895 行 / line22 SUBCKT / *|I 实例行）
