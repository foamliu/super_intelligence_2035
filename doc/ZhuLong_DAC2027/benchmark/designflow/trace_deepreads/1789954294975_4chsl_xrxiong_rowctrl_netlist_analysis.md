# Deepread: 1789954294975_4chsl (xrxiong / hfeg0plg74 / 10.129.8.112)

> **结论：WRONG-SHARD (D 域 schematic_netlist，非 C 域 physical_verify) → parked**
> r388 选料；mc=497；本笔记记录 wrong-shard 判据，避免后续重捡。

## 会话元数据（.json）
- session_id: 1789954294975_4chsl
- title: **"分析一下row_ctrl模块的功能"**
- source: desktop, interactive
- model: glm-5.2 (provider cxmt-glm52)
- started 2026-09-21T01:31:34Z → ended 2026-09-23T03:02:15Z（跨 2 天）
- status: **failed**（exit_code=1, terminal_marker=failed_external_process_exit）
- usage: inputTokens=55,380,469 / outputTokens=134,144（input 极高 = 893KB netlist 被反复读）
- forkedFromSessionId: 1789906092725_9ld3r
- cwd: /home/xrxiong

## 用户意图（首条 user_input）
```
<user_input mode="act">分析一下row_ctrl模块的功能
--- Attached files ---
[Attached file: netlist.sv (text/x-svsrc, 893.4 KB) — saved to disk, accessible via file-reading tools]
--- End of attached files ---</user_input>
```
- 附件 `netlist.sv`：Aether schematic 导出的 Verilog netlist，top design = `dscqa_digital/R_RowCtrl/schematic`
- netlist.sv 含大量 stdcell 子模块（Spnand3GSx1 / Spnor2GSx1 / SplatrqGSx1 / Spbufx4 / SpinvGSx8 / Spaoi21GSx1 / SpffrqGSx1 / dlyg0of8GSs1...），均为 schematic-export 风格（inh_vcc/vss/vbp/vbn power pins + I0 instance）
- **任务本质：从 Verilog netlist 分析 row_ctrl 模块功能** = schematic_netlist / 网表理解（D 域）

## 关键词 false-positive 判据（重要）
summary.tsv 报 `lvs:1895; schematic:583; netlist:444; verilog:373; drc:70`，但 **4MB messages.json 实测**：
```
grep -c user_input  → 28（28 个用户轮）
grep -c lvs         → 0   ← summary 报 1895，实际 0
grep -c calibre     → 0
grep -c runlvs      → 0
grep -c row_ctrl    → 2
grep -c netlist.sv  → 395
```
⇒ summary 的 `lvs:1895` 是扫描器对 **附件 netlist.sv 文件内容**（或会话文件其他部分）的关键词计数，**不是对话中的 LVS 工具活动**。trace 内 0 个 lvs/calibre/runlvs 提及 → 无任何 LVS 工具调用 → 非 physical_verify 任务。
⇒ **shard C keyword 过滤的已知陷阱**：`lvs` 关键词可能来自附件 netlist 文件内的字符串（如模块名/注释含 "lvs" 子串），而非真实 LVS 操作。后续选料对 lvs-only（无 calibre/drc/runlvs 共现）的候选须 grep trace 验证。

## 域判定
- seed task = "分析模块功能" + 附件 = netlist.sv → **schematic_netlist (D 域)**
- 无 LVS/DRC/Calibre 工具调用 → 非 physical_verify (C 域)
- 28 个用户轮、跨 2 天、failed → 即便做 D 域 case 也需深读全部 4MB 才能定 seed turn

## 处置
`trace_ledger.py --shard C mark --status parked --note "wrong-shard: ..."`
- 不做 case（wrong-shard，红线 #1 要求真实 trace + 正确域）
- 不重捡（parked 即台账排除）

## 给后续选料的教训
1. lvs-only 关键词候选（无 calibre/drc/runlvs/.gds 共现）高风险 wrong-shard —— 优先 calibre+drc+.gds 共现的候选
2. 4MB trace 触发 §3 >2MB 例外，但 wrong-shard 例外不适用（parked 不算 deepread DEBT）
3. r387 DEBT 建议的 jason17w 簇（xm22u/le1s7，drc:2710+verilog:3947）也需同样验证 —— verilog 主导可能也是 D 域
