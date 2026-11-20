# 深读笔记 · plwnn · LVS svdb .rep 目录分析

## trace_source
- session: 1793012120155_plwnn.messages.json
- user: pdsong @ hfeg0pgn024 (10.129.35.123)
- mc: 81, kw: lvs:221 / calibre:87 / netlist:12 (C 域 physical_verify, LVS)
- 文件: 43 msgs / 502KB / 2 真实 user_input (msg0 "hello", msg2 分析请求)
- ledger host 字段历史口径: hfeg0pgn024 (nofile revival 误记 hfeg0pgn024，本线实测 autofs /home/pdsong 可达)

## 用户真实意图 (msg2 原文)
> 帮我分析下 /rundata/drjqa/V0/simdir/finesim/workdir/pdsong/simulation/PDN_sim/Vtb1_powerCap_split1_261022_PCPN_test/lvsSvdb/test/tt/ 下的文件

= 分析一个 Calibre LVS svdb 查询结果目录下的一批 `.rep` 文件（每个文件是某个宏单元某条电源/地 net 的 NET SHAPES 响应）。

## 助手 gold 链
1. list_allowed_files 探目录 → read_files 看 `.rep` 头部 → run_approved_command `wc`/`grep`/`ls`
2. editor 写 `analyze_tt_dir.py`（4 次精化 msg16/20/22/24）：扫 `*.rep`，每文件输出 bytes/lines/polygons，末尾汇总 total_polygons / total_bytes。polygon 计数用 `grep -c "^ *p [0-9]"`（匹配 `p <序号> <顶点数>` 行）。
3. editor 写 `sum_tt.sh`（msg30）：md5sum + 几个 vss 文件 head 6 行（验证多份 vss 文件内容是否相同）
4. editor 写 `inspect_poly.py`（msg38）：首多边形前 11 行 + 小文件 bbox
5. 末尾长文分析报告：解释文件机制（`grepPCPNLoc.py` → `calibre -query` → Multiple_Response_File）、关键发现（4 份 `_vss.rep` 全局地 net 图形数完全相同 13,162,529 / vddq 同理 / 局部 net 才小 / `instHierPinLoc.txt` 空说明后续解析被注释）、磁盘成本建议。

## .rep 文件格式（Calibre Multiple_Response_File）
```
Multiple_Response_File <精度>
File: grepPortsLoc_<macro>_<net>.rep
Timestamp: ...
Layer: PCPnet_MOS / PCNnet_MOS
Count: <N>
p <序号> <顶点数>
x y
x y
...
p <序号> <顶点数>
...
```
polygon = 形如 `^\s*p\s+\d+\s+\d+` 的行（每个 `p` 一个多边形）。

## 档 B reframe（grounding，非加难）
- A 档 gold = 真实 `analyze_tt_dir.py` 跑 4.6GB / 11 文件的真实 tt/ 目录（不可复现：数据巨大 + Calibre 专有 svdb）。
- reframe = fixture 驱动的参数化 `.rep` 目录统计器：候选交付 `analyze_rep_dir.py <dir> [-o out.json]`，扫 `*.rep`，输出 JSON `{dir, files:[{name,bytes,lines,polygons}], total_files, total_polygons, total_bytes}`。polygon 计数 = 匹配 `^\s*p\s+\d+\s+\d+` 的行数。
- visible A fixture = 小合成 tt/ 目录（2 个 .rep，合 7 polygons）；hidden B fixture = 另一合成目录（4 个 .rep，含一对重复内容，合 13 polygons）。A/B 文件名/坐标/polygon 数全异 → 硬编 A fail B，硬编 B fail A。
- reframe 忠实保留用户意图（"分析目录下的 .rep 文件"→ 统计每文件 bytes/lines/polygons + 汇总），未引入用户未要求的内容；把"4.6GB 真实数据"沉淀为"小合成 fixture + JSON 结构化输出"，离线化。
- 用户分析报告里的"重复 vss 全局地"洞察由 check.py 在 B fixture 中以"一对内容相同文件 → 相同 bytes/lines/polygons"自然体现（check 验统计正确即捕获），不强制候选做重复检测（gold 脚本本身只统计，重复检测是助手人工洞察）。

## 意图审计
keep — pdsong 真实意图（分析 LVS svdb 查询结果目录的 .rep 文件）完整保留，reframe 是 grounding（4.6GB 真实数据 → 小合成 fixture + JSON 输出），非加难。2026-11-15 reaudit 后 debug-Q&A/analysis 类合法。
