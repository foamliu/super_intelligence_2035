# Deepread: 1789713289092_h01fd (shanliny / hfeg0pkn005 / 10.129.2.14)

> **结论：可造（debug-Q&A, 11-15 令复活）· DEBT: 合成未完成 → r785 清**
> r784 选料（pool_reaudit_D 复活候选，旧判 "analysis-only 不可造" → 新标准可造）；
> trace 8MB >2MB ⇒ §3 大 trace 例外：本轮只深读，下一轮合成 case。
> ssh 通（hfeg0pkn005 免密），素材全取（1prf.py 68KB + lvs.rep 1.2MB + 附件 6 文件）。

## 会话元数据
- session_id: 1789713289092_h01fd
- user: shanliny, host: hfeg0pkn005 (10.129.2.14)
- trace_source: session_file=1789713289092_h01fd.messages.json, match_count=15
- title: "参考lvs.rep告诉我1prf.py拼接的逻辑哪里出了问题"
- 10 msgs (5 user + 5 assistant), 8.16MB, status=completed
- model: deepseek-v4-flash, cwd=/home/shanliny
- keywords: schematic:132, netlist:27

## 用户意图（A 档 verbatim, 纯需求轮）
```
参考lvs.rep告诉我1prf.py拼接的逻辑哪里出了问题
```
附件（全在 msg#0 content，可直接恢复，不需 ssh 源）：
- 1prf.py (68.5 KB) — SRAM generator 脚本，1538 行，class SRAMGenerator
- netlist_interface.py (35.8 KB) — NetTiler 库
- HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.cdl (2.6 MB) — CDL source netlist
- 0_run (0.2 KB) — `python 1prf.py --nw 2048 --nb 144 --cd 1 --cm 4 --bk 2 --re 1 --wa 1 --ra 1 --bw 1 --netlist ...`
- CX2048X144M4B2C1.netlist (3.9 MB) — layout netlist
- lvs.rep (1.2 MB) — Calibre LVS report, INCORRECT

**real_task_summary**: 用户跑 1prf.py 生成 SRAM tiling netlist，LVS 报 INCORRECT，要求 agent 参考 lvs.rep 定位 1prf.py 拼接逻辑的错误（不改代码，只诊断）。

## 金标准（agent 诊断的 3 处 bug，逐字从 msg#9）

### Bug 1: build_row() 第 143-144 行 — IC_RE2 的 BL/BLB 误接
- **函数**: `build_row(self, iops, name)` (第 90 行起)
- **问题行**: 第 143-144 行
```python
self.nt.rename_inst_ports(inst_name,f"BLB",f"BLB_RED<{self.CM}>")  # CM=1 → BLB_RED<1>
self.nt.rename_inst_ports(inst_name,f"BL",f"BL_RED<{self.CM}>")    # CM=1 → BL_RED<1>
```
- IC_RE2 (第 136 行 inst_name="IC_RE2") 的 BL/BLB 应接 `BL_RED<0>`/`BLB_RED<0>`（和 IC_RE1 共享同一根冗余位线），而非 `BL_RED<1>`/`BLB_RED<1>`
- **lvs.rep 证据**: VSS 网上 253 个多余 bitcell 实例 (`BKB/BK_R/ARRAY/IR63/IC_RE/Ibitcell_4x1[...]`)，drain 连 `BL_RED_R_D[0]` 但 source 连 `net170[0]`
- **修复**: 第 143-144 行 `BL_RED<{self.CM}>` → `BL_RED<0>`, `BLB_RED<{self.CM}>` → `BLB_RED<0>`

### Bug 2: build_top() 第 1364-1368 行 — VDDWL 漏做 _U/_D 改名
- **函数**: `build_top(self)` (第 1198 行起), bank 循环 (第 1346 行起)
- **问题位置**: 第 1364-1368 行，bank 循环对 BL/BLB/FCKB/XB/XC 做了 `_U/_D` 改名，漏掉 VDDWL
```python
1364| self.nt.rename_inst_ports(bank_name,f"BL<...>",f"BL_{up_or_down}<...>")
1365| self.nt.rename_inst_ports(bank_name,f"BLB<...>",f"BLB_{up_or_down}<...>")
1366| self.nt.rename_inst_ports(bank_name,f"FCKB<7:0>",f"FCKB_{up_or_down}<7:0>")
1367| self.nt.rename_inst_ports(bank_name,"XB<7:0>",f"XB_{up_or_down}<7:0>")
1368| self.nt.rename_inst_ports(bank_name,"XC<7:0>",f"XC_{up_or_down}<7:0>")
# ❌ 缺少 VDDWL 改名
```
- **lvs.rep 证据**: `BKT/BK_L/WLBUF/BUF0/MVDDWL_HEADER d: BKT/VDDWL ** VDDWL_U **`
- **修复**: 第 1368 行后加 `self.nt.rename_inst_ports(bank_name,"VDDWL",f"VDDWL_{up_or_down}")`

### Bug 3: build_top() 第 1364-1368 行 — WL_IN 漏做 _U/_D 改名
- 同 Bug 2 位置，漏掉 WL_IN
- **lvs.rep 证据**: `BKT/BK_L/WL[232] ** BKB/BK_L/WL[169]` (上下 bank WL 短接)
- **修复**: 加 `self.nt.rename_inst_ports(bank_name,f"WL_IN<{self.rpb-1}:0>",f"WL_IN_{up_or_down}<{self.rpb-1}:0>")`

## 1prf.py 关键结构（check.py 合成用）
- 1538 行, class SRAMGenerator, 16 个 def
- `def build_row(self,iops,name)` — 第 90 行，IC_RE1(128-135)/IC_RE2(136-144) 冗余列 bitcell
- `def build_top(self)` — 第 1198 行，bank 循环 1346-1394，_U/_D 改名 1364-1368
- 465 处 `rename_inst_ports` 调用
- Bug 1 精确行: 143 (`BLB_RED<{self.CM}>`) + 144 (`BL_RED<{self.CM}>`)
- Bug 2/3 精确行: 1364-1368 (5 行改名，缺 VDDWL + WL_IN)

## lvs.rep 关键证据（excerpt 已取，270 行）
- 第 32 行: `INCORRECT`
- 第 37-39 行: `Different numbers of nets / instances / Connectivity errors`
- 第 93 行起: `INCORRECT NETS` — VSS net 253 个 unmatched IC_RE bitcell
- `BL_RED_R_D[0] ** net170[0]` — BL_RED 误连证据
- `BKB/BK_R/WL[253] ** net6[253]` — WL 误连证据
- `BKT/BK_L/WL[232] ** BKB/BK_L/WL[169]` — 上下 bank WL 短接证据

## 拟造任务形态（套 #254 v2 code-grounded debug-diagnosis pattern）
- **A 档 verbatim**: "参考lvs.rep告诉我1prf.py拼接的逻辑哪里出了问题"
- **交付**: diagnose.py（读 1prf.py + lvs_rep_excerpt.txt → 输出 diagnosis.json 结构化诊断）+ diagnosis.json
- **check.py** (≥12 条件 a-l):
  - (a) zip 含 diagnose.py + diagnosis.json
  - (b) diagnosis.json 合法 JSON, 含 bugs 数组
  - (c) 每个 bug 有 function/line_range/bug_desc/fix_location 字段
  - (d) ≥1 bug cites build_row (存在于 1prf.py)
  - (e) ≥1 bug cites build_top (存在于 1prf.py)
  - (f) bug cites 真实行号 (在 1prf.py 1-1538 范围内)
  - (g) ≥1 bug cites BL_RED 或 BLB_RED (bug 1 信号)
  - (h) ≥1 bug cites VDDWL 或 WL_IN (bug 2/3 信号)
  - (i) diagnosis 引用 lvs.rep 证据 (VSS/253/INCORRECT/BL_RED_R_D)
  - (j) subprocess: check.py 运行 diagnose.py 于 hidden B，断言输出结构
  - (k) anti-hardcode: B 诊断 ≠ A (B bug 不同: GBL_RED<0> vs <1>)
  - (l) 3-run 确定性
- **hidden B**: 1prf_B.py — bug1 修复(143-144→BL_RED<0>) + 新 bug@140-141 (IC_RE2 GBL_RED<0> 应为 <1>) + lvs_rep_B_excerpt (GBL_RED 短接症状)
- **reference**: diagnose_ref.py — 解析 1prf.py rename_inst_ports 调用 + 匹配 lvs.rep 证据 → JSON
- **negatives**: empty / print_only / deleted_core / naive_wrong_func

## 素材可达性
- ssh hfeg0pkn005 免密 ✓ (r784 验证)
- 1prf.py / lvs.rep / 全附件在 msg#0 content 内联 ✓ (不需 /rundata)
- 已 scp 到 .75 workdir: `sessions/shardD_20261116-designflow-D_D-r784-9z6bd_0/`
- 下一轮可直接从 deepread 恢复素材（或重 ssh fetch）

## DEBT
- 合成未完成 → r785 第一件事：建 assets/reference/hidden/negative + check.py 12 条件 + 自验 + 落 D.jsonl
