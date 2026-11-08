# Deep-read: 1793945103405_x8v81 (dsgao @ hfeg0pkn001)

**Completed 2026-11-08 (shard D #408)**

## Trace meta
- session: 1793945103405_x8v81.messages.json (directory-form: /home/dsgao/.cline/data/sessions/1793945103405_x8v81/)
- user: dsgao
- host: hfeg0pkn001
- domain: schematic_netlist (shard D)
- status: case (ledger_D, 2026-11-08, case-id EDA-Eval-DesignFlow-TrimMuxInvDiff-001)
- 82 messages total

## User turns (full deep-read)
- **U0 (idx=0)**: "@/proj/drcpa/.../drcpa_digital_R_trimEqOff_schematic.netlist 和 /proj/drcoa/.../drcoa_digital_R_trimEqOff_schematic.netlist 有区别吗，为什么后仿真 delay 有差异"
  - A-grade seed ✓ (表达目标：对比两 netlist + 解释 delay 差异；未给根因/修复)
  - **被采纳为本 case 任务说明**（prompt.txt 逐字原文）
- **U#26 (idx=26)**: "fngidl 要恒为vwlp" — 修改 GidlAryCtrl testbench（另一独立任务链，未采纳）
- **U#45 (idx=45)**: "fngidlmode 前半程 vwlp 后半程 vss + 步长 10p" — 续 testbench 任务链
- **U#69 (idx=69)**: 对比 R_tOCTrim netlist pair（delay 差异）— A-grade seed，**被采纳为隐藏 B 对**
- 其余为 plugin/state 块（agent-policy-engine）+ assistant 工具调用结果

## Assistant 工具链与关键产物（U0 链）
1. list_allowed_files → 列出 /rundata/drcpa_sim/.../ 与 /rundata/drcoa/.../ 仿真目录
2. read_files → 读两 netlist 首 60 行（发现 header Date/TopDesign 不同，正文开头一致）
3. editor → 写 /home/dsgao/Desktop/diff_netlists.py（difflib.unified_diff）
4. run_approved_command python-runner → 跑 diff，得 drcpa 459 行 / drcoa 462 行，diff @@ -377,46 处 XI_switch 新增 +3 条
5. read_files 360-459 → 读 invGSx2/mx2LVSx2 子电路定义 + 顶层 R_trimEqOff
6. search_codebase "mx2LVSx2"/"invDS" → 确认 mx2LVSx2 = 2:1 mux (A0 A1 S SN Y)
7. **结论（idx=25）**：两 netlist 共享全部 stdcell；顶层 R_trimEqOff 的 trim 选择通路 drcoa 多 1 级 invDSx1（XI13：trimN→trim），drcpa 仅 XI7（cm1_ro_EqOffWlOn→cm1_ro_EqOffWlOnN）；mux 选通信号 drcpa 用 cm1_ro_EqOffWlOn/...N，drcoa 用 trim/trimN → **delay 差异来源 = 多 1 级反相器**

## R_tOCTrim 链（U#69 → 隐藏 B）
- drcpa R_tOCTrim: XI18=dlyg2of8LVSs1, XI25=dlyg4of8LVSs1, XI30=dlyg4of8Ls1, trim 1 级
- drcoa R_tOCTrim: XI18=dlyg0of8LVSs1(-2), XI25=dlyg6of8LVSs1(+2), XI30=dlyg6of8Ls1(+2), trim 2 级(+XI29)
- 结构差异模式与 R_trimEqOff 不同（延时抽头单元变更 + 额外反相器），适合做隐藏 B

## 资产获取限制
- /rundata/drcpa_sim、/rundata/drcoa 归属 cadmin:drcpa，e0031982 无读权限且无 sudo
- 无法获取真实 netlist 文件 → 采 B-grade synthesized：trace_source 真实(x8v81)，assets 合成但忠实复刻 trace 中的结构差异模式（trim mux XI13 额外反相器 + R_tOCTrim 延时抽头变更）

## 交付
- case-id: EDA-Eval-DesignFlow-TrimMuxInvDiff-001
- grade: B (synthesized from real trace)
- level: L1 (offline Python 结构分析)
- domain: schematic_netlist
- 16 条件 a-p（zip+py_compile+B-run+7键+行数+Date+TopDesign+shared+left/right_only+XI29+XI25+XI30+XI18+finding+3-seed+反硬编码A≠B）
- 自验: ref PASS 16/16 + 4 neg FAIL distinct{c,d,h,p} NEG_RC=0 + §4.9 三假 distinct{d,c,h}
- byte-sync sha 41d51c79d9965a0c size 11178
- D.jsonl 427→428
