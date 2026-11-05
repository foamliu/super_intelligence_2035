# 4a8f9 — port_catch (schematic_netlist) deepread

- sid: 1792136569651_4a8f9.messages.json · user chengk · host 10.129.35.121 · mc130 · n_msgs=176
- path: /home/chengk/.cline/data/sessions/1792136569651_4a8f9/1792136569651_4a8f9.messages.json (1.1MB)
- sample netlist: /home/chengk/work/code/wv_trig/port_catch/data/nand2_CPSel.netlist (1454B, real attachment, fetched)

## U#0 (verbatim, A-faithful prompt)
> 参考路径/home/chengk/work/code/wv_trig/port_catch/code/下的代码，希望实现以下功能，输入网表中的一个实例化的层级结构，能够用cck的api实现抓取这个实例化的所有端口和连接的连线，通过连线关系得到这个实例的输入和输出端口链接到的实例，示例网表的位置在/home/chengk/work/code/wv_trig/port_catch/data/nand2_CPSel.netlist

纯提需求 / 未给根因 / 未给修复 → A 档合格。

## trace 演化
- agent list_allowed_files → 探索 /home/chengk/work/code/wv_trig/port_catch/{code,data}
- search_apis (cck 相关: leGuiCrtPinByInstance / emyNetGetMemNets / dbCrtInstTermByName …)
- read 参考代码 ChkFO_v1p3.tcl / dspfParser.tcl (后查已不存在，code/ 已重组为 cck_tcl_packages + task3_src)
- editor write grep_cck.py / grep_cck_ctx.py / grep_port_map.py → 在 IddFlowCode/cck_tcl_packages 里 grep cck::getMasterInst / cckGetSubckt 等用法
- editor write PortCatch.tcl (9815B 超 6000 限制 → split insert) — Tcl 用 cck API 抓 inst ports + nets + neighbors
- editor write verify_portcatch.py (Python netlist parser 校验 Tcl 输出) → 调 regex 解 XI1/XI0
- U#118/U#119: 用户贴 CCK banner + `cck PortCatch.tcl -netlist data/nand2_CPSel.netlist -top nand2_CPSel -inst XI1,XI0 -o portCatch.rep` → **Segmentation fault** (debug 轮，A 档禁用作 prompt)
- U#138: 用户**重贴 U#0 原话**（任务重申）→ agent 重构 PortCatch.tcl + README_PortCatch.md
- U#154: 用户再贴 cck 命令输出（debug）
- 注: agent 最终产物 PortCatch.tcl / verify_portcatch.py / portCatch.rep **已被清理**（code/ 重组），无 final deliverable 可直接复用

## 真实附件 nand2_CPSel.netlist 结构
- 2 空 subckt: switch_close / switch_open
- nand2LV: 7 ports (A:I B:I Y:O vbulkn!:B vbulkp!:B vcc!:B vss!:B), 4 MOS (2 PMOS ptn_lv / 2 NMOS ntn_lv)
- nand2_CPSel (top): 7 ports (A:I B:I Y:O vbn!:B vbp!:B vcc!:B vss!:B), 2 instances of nand2LV:
  - XI1 A B Y vbn! vbp! vcc! vss! / nand2LV (params)
  - XI0 B A Y vbn! vbp! vcc! vss! / nand2LV (params)  ← A/B 交叉
- 连接: XI1.A↔net A↔XI0.B；XI1.B↔net B↔XI0.A；XI1.Y↔net Y↔XI0.Y；bulks→top pins

## 任务意图（用于 B-grade 合成金标）
给定 netlist + top + instance：解析出该 instance 的所有端口 + 每端口连接的 net + 通过 net 关系得到该 instance 输入/输出端口连接到的其它 instance（含对端端口名 + 方向）。真 cck 工具不可附加（segfault / 商业 license）→ B-grade synthesized：金标为纯 Python netlist 解析器，输出结构化 JSON。

## 合成方案
- A（可见）= 真实 nand2_CPSel.netlist + prompt.txt(U#0 逐字) + task_brief.md(≤3 行接口)
- hidden B = norf_chain.netlist（结构反转：A=并行 2-inst 交叉，B=串联 3-inst 链 XI0→XI1→XI2；不同 top/subckt/实例名/连接；query XI1）
- 金标 port_catch_ref.py: parse subckt/.PININFO/X-instance → map nets→ports (positional, handle `/` + params) → for each port {name, direction, net, connected:[{instance,port,direction}], top_pin} + summary
- check.py ≥14 条件 a-n：含 (k) 跨输入反硬编码（A 重跑验 XI1.Y↔XI0.Y）+ (l) B 输出无 A-only token + (m) 源码无 /home//proj 硬编码 + (n) 确定性 sha256
