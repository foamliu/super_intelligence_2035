# Deepread: xpfpl — eunicef@hfeg0pgn014 (10.129.35.113) — ITF brace-imbalance fix

- session: `1792637530853_xpfpl.messages.json` (99 msgs / 709KB / agent=lead / 2026-11-16)
- user: eunicef (physical-verify / PDK-LPE engineer), host hfeg0pgn014 = 10.129.35.113
- scan: mc=130, lvs:553 / calibre:141 / pdk:128 / netlist:66 / .gds:60 / gdsii:34 / aether:34 / .cdl:27 → physical_verify (Calibre PEX/ITF + LVS)
- 4-shard ledger: eunicef 仅 C 有 1 parked(5hdsl, Q&A LVS error understanding, REJECT); xpfpl 本 session 全 4 shard fresh; C.jsonl 无 eunicef → session-level fresh.

## 三段用户意图

### U#1 (idx=0) — ITF grdgenxo 报错分析与修复 [本题取材]
路径 `/home/pdk/eunicef/LPE/V2B/V2B_itf_drvqa_v0d1_Rev01_t06/tf/cxmtV2B_drvqa_1p11m1x9y1z_98C_CA_TYP.itf`，跑 `grdgenxo -viewer` 报 `ERROR: (774) ITF: ERROR: statement_name_expected at line 5 instead of }`。请给报错分析 + 修正手法。

### U#2 (idx=33) — LVS port 缺失分析
`/home/oliver1s/PDK/Star_3DIC/Buffer_cap/Buffer_top.lvs.report` 一直提示 port 缺失，版图同路径，请分析。

### U#3 (idx=88) — LVS net 数量不匹配分析
`/proj/ddgoa/V0/ver/lvs/test_3d/Buffer_top/Buffer_top.lvs.report` 一直提示 net 数量不匹配，请分析。

## U#1 深读（agent 工具链 + 关键产物）

agent(deepseek-v4-flash lead) 工具链:
1. `read_files` 读 ITF 全文（453 行 / 23411 chars）
2. `run_approved_command python-runner` 跑 `analyze_itf.py`（自写）：检 `#beginHide`/`#endHide`、首 10 行 raw repr、非打印字符、花括号平衡（逐字符 depth 追踪）
3. `analyze_itf_binary.py`：BOM/行尾(CRLF/LF)/hex dump
4. `trace_braces.py`：逐行 Old/New depth + {/} 计数表

**ITF 结构**:
```
Line 1: TECHNOLOGY = cxmtV2B_drvqa_1p11m1x9y1z_98C_CA_TYP
Line 2: GLOBAL_TEMPERATURE = 98
Line 3: HALF_NODE_SCALE_FACTOR = 1.000
Line 4: #beginHide
Line 5: $ Frontside ITF statements
Line 6+: DIELECTRIC/CONDUCTOR/VIA/TSV 块（单行 {...} 或多行 {...} 块）
Line 345: TSV ntsv\t{            ← depth 0→1
Line 346-352: TSV 参数行
Line 353:             }           ← depth 1→0 ✅ 关闭 TSV 块
Line 354: }                       ← depth 0→-1 ❌ 多余右花括号（根因）
Line 355: (空)
Line 356: $ Backside ITF statements
Line 357+: DIELECTRIC/CONDUCTOR 单行 {...}（开闭平衡，但解析器处于 -1 状态→级联报错）
Line 450: #endHide
```

**根因**: Line 354 多了一个 `}`。Line 353 已正确关闭 `TSV ntsv` 块，Line 354 的 `}` 把 depth 从 0 推到 -1，破坏解析器状态机；后续每个平衡的单行 `{...}` 块的 `}` 都在 -1 状态下再次触发"多余 }"级联报错。

**为何报"at line 5"**: `#beginHide`/`#endHide` 预处理后行号重编号，或 grdgenxo ITF 解析器行号报告有偏移；但根因是 line 354 的多余 `}`。

**次要问题**: `#beginHide`(line 4)→`#endHide`(line 450) 把几乎整份文件（所有 Frontside+Backside 层定义）包进隐藏块；若 grdgenxo 支持 `#beginHide`/`#endHide`，可见内容仅前 3 行 TECHNOLOGY/GLOBAL_TEMPERATURE/HALF_NODE_SCALE_FACTOR，无有效层定义——可能非设计本意。

**修复**: 删除 line 354 的多余 `}`（关键修复）。agent 尝试 `editor` 直接改 ITF 文件被 `policy.writableRoots` 拒（`/home/pdk/...` 不在可写根），转写 `fix_itf.py` 但 `run_approved_command` 被桌面审批拒绝（exit reject）。**最终交付以 chat-inline 文本给出分析 + 修复方案**（未落盘修正文件，但分析与修复手法完整）。

**协议指纹 / 子型**: Calibre PEX ITF `grdgenxo -viewer` (774) statement_name_expected 报错 → 花括号 depth 追踪 → 定位多余 standalone `}` → 删除修复。纯文本/几何分析，不调 EDA API。

## U#2/U#3 (略，LVS report 分析，非本题取材)

## 跨 shard 串台检查
- 4-shard ledger: xpfpl 仅 C；eunicef C 仅 1 parked(5hdsl Q&A REJECT)。
- 4-shard jsonl: 无 eunicef。
- 子型 `itf_grdgenxo_brace_imbalance_fix`(Calgrave PEX ITF 花括号 depth 追踪 + 多余 standalone `}` 定位/删除修复) **首例**，与既有 C case（LVS/DRC deck 解析、网表枚举、schematic 构建、skill 审查、GDS 操作、pyAether 环境、PEX DSPF RC 可视化、socket-bridge nav、pin 改名、M1-via DRC 协同、pcell border 修复、testmode 追踪、virtuoso-cli skill 审查、TECHLIB pwr inst 构建、SDL MOS 拆分、Aether 网表 cell 枚举、pyAether 环境审计）全正交。

## 合成方向（档 B reframe fixture-driven）
agent 写 `itf_brace_fixer.py`（纯标准库 ASCII）读 ITF 文件 → 逐行/逐字符追踪花括号 depth → 识别"多余 standalone `}`"（行非空白内容全为 `}` 且处理该行使 depth < 0）→ 贪心删除首个多余 standalone closer 并重扫迭代 → 产出 JSON 报告（analysis{technology,total_lines,beginHide_line,endHide_line,original_depth_final,original_depth_min} / redundant_closers[{line_no,content,depth_before,depth_after}] / fix{removed_lines,corrected_depth_final,corrected_depth_min,status}）。CLI `<itf_file> [--out corrected.itf]`。

- visible env_A: itf_A.itf — 仿 trace（TECHNOLOGY=drvqa_A_1p9m1y1z_25C_TT, TSV ntsv_A 块后多 1 个 `}`，Frontside+Backside, #beginHide/#endHide）
- hidden env_B: itf_B.itf — 不同 tech(pfsmr_B_2p7m2y2z_110C_FF)/不同层名/2 个多余 standalone `}`（VIA V0 后 1 个 + TSV ntsv_B 块后 1 个，不同块类型不同位置，测迭代删除 + 反 env_A 记忆）
