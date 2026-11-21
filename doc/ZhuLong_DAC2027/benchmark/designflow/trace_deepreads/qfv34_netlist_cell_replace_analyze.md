# Deepread: qfv34 — 整芯片网表 cell 替换 diff/分析（sijialv）

- session: `1795142640082_qfv34.messages.json` · user `sijialv` · host `hfeg0plg05` · mc=79 · domain **physical_verify** (LVS netlist)
- 67 msgs, 444KB, agent=lead. FRESH (4-shard ledger 0 hit, 4-shard jsonl 0 hit, no prior deepread).

## 真实意图（msg 0）
`/proj/drvqa/V0/simdir/verilog/lvsijia/netlistai` 下两个网表：`netlistfullchip`（整芯片，720839 行，3864 module，顶层 `WOWTOP_1C2A`）+ `netlistblock`（新修改 cell 重新抽取，2032 行，14 module，顶层 `C_WrApShiftsubNew`，Last Time Saved 2026-11-18）。**把 block 中新修改的 cell 替换/合入 fullchip**。

## Agent 完成的 gold 分析（msgs 1-45）
1. list 文件 → 读两个网表头。python-runner 损坏（`No module named 'encodings'`）→ 改 shell-runner（只收 .sh）。
2. `analyze_netlists.sh`：grep module 定义。block 14 module，fullchip 3864 module。
3. `locate_modules.sh`：在 fullchip 定位 14 个 block module → **`C_WrApWRshift_edit` NOT FOUND in fullchip**（需 INSERT）。
4. `diff_modules.sh`：逐 module diff（awk 提取 module body 到 /tmp，diff）。四类结论：
   - 11 个 delay cell（dlyg*）：**IDENTICAL**，不动。
   - `C_WrApWRshift_edit`：**NOT IN FULLCHIP**（817 行）→ INSERT。
   - `C_WrAp64TCounter_edit`：**DIFFERENT**（block=100/fullchip=100，6 diff 行）→ REPLACE。diff 细节：port 顺序差异（`inh_vss, inh_vbn, inh_vcc, inh_vbp` vs `inh_vss, inh_vcc, inh_vbn, inh_vbp`）+ `inout inh_vbn;` 位置变。**端口集合相同，仅顺序变**（假差异 / port-reorder）。
   - `C_WrApShiftsubNew`：**DIFFERENT**（block=648/fullchip=706，382 diff 行）→ REPLACE。**新增 `WRAP_O`（output）+ `MR70OP1`（input）端口**。
5. `check_mr70op1.sh`：fullchip 搜 `MR70OP1` → 在 `Controller`（line 429709 `wire MR70OP1;`）中。`C_WrApShift`（fullchip 420422）实例化 `C_WrApShiftsubNew`（420939/420955 两处）。
6. `find_parent.sh` + `check_capctrl.sh`：父模块链 **`C_WrApShiftsubNew` → `C_WrApShift`(420422) → `C_APCtrl`(422482) → ... → `Controller`(427953)**。
   - `WRAP_O`：父 `C_WrApShift`/祖父 `C_APCtrl` 均**无**；fullchip 仅 `C_ClkGating`(318278) 与自身有 → **不能直接用**（output 悬空 .WRAP_O()）。
   - `MR70OP1`：父 `C_WrApShift`/祖父 `C_APCtrl` 均**无**；仅更上层 `Controller` 有 → **无法直接连**（input 悬空会导致移位链功能错误）。
7. `ask_question`（msg 45）让用户决策 MR70OP1 连法（悬空/逐级穿线/连等价信号/只换定义）。→ 任务停在此决策点（替换未实际执行）。

## 用户 pivot（msg 46-66）
msg 46「复盘刚才任务执行的全流程，生成一个 Skill」。agent 用 skill-creator 建 `/home/sijialv/.cline/skills/netlist-cell-replace/`（SKILL.md 122 行 + references/pitfalls.md 115 行 P1-P11 + case-netlistai-2026-11.md 61 行），verify 通过。

## 跨 shard 串台检查
- 4-shard ledger：qfv34 仅 C（本轮 claim）。4-shard jsonl trace_source：0 hit。
- 同 domain 已落库 case（grep C.jsonl）：网表/diff/analyze 主题——LvsPinCaseMismatchDiag/LvsSvdbRepDirStat/VdlyVccCrossDomainAudit/NetlistCellXxx 均无「block→fullchip cell 替换 diff 分析器」子型。**首例**：netlist_cell_replace_diff_analyzer。

## Reframe 决策（档 B fixture-driven）
真实**已完成**的 gold = diff/分析（四分类 + 端口变更 + 父链 + 新端口可用性），不是替换本身（停在决策点）。故 reframe 为 **fixture-driven「整芯片网表 cell 替换 diff 分析器」**：agent 写 `netlist_cell_replace_analyzer.py`，读 block+fullchip Verilog 网表，emit JSON 报告（block module 清单 + 四分类 IDENTICAL/INSERT/REPLACE + diff 行数 + 端口 add/remove + 父模块链 + 新端口在父/祖父可用性）。A/B 两套合成 Verilog fixture（结构同真实：identical/insert/port-reorder/new-port+parent-chain），B 与 A 规模/名称/端口名/父链深度均异。check() 在 B 上跑候选脚本 + 3-seed 顺序随机 + 反硬编码 + 三假 FAIL。

## 真实参数（A fixture 泛化来源）
block 14 module：11 identical(dlyg*) + 1 INSERT(C_WrApWRshift_edit,817 行) + 1 REPLACE-port-reorder(C_WrAp64TCounter_edit,6 diff) + 1 REPLACE-new-ports(C_WrApShiftsubNew,+WRAP_O out/+MR70OP1 in,382 diff)。fullchip 3864 module，顶层 WOWTOP_1C2A。父链 C_WrApShiftsubNew→C_WrApShift→C_APCtrl→Controller。MR70OP1 在 Controller(wire)，WRAP_O 在 C_ClkGating + 自身。
