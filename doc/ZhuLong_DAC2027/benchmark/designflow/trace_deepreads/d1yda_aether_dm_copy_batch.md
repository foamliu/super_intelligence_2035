# Deepread · d1yda · Aether Design Manager 批量 copy cell howto

- **session**: `1793782993086_d1yda` (e0044131@hfeg0pkn003, 10.129.2.12)
- **match_count**: 28 (aether:353 / verilog:73 / schematic:61 / netlist:59 / cellview:49 / virtuoso:20 / floorplan:12 / mixed-signal:9)
- **size**: 173,865 B / 18 msgs (轻量 Q&A 单轮)
- **path-bug revival**: r270 flat-path peek_D270 parked「unfit (Q&A/doc/...NOFILE)」；2026-11-15 用户令后 Q&A/doc-search 复活为可造；r977 subdir 路径 ALIVE 确认（与 fz05e/3rdqj 同形态 path-bug revival 第 8 例）
- **trace_source**: 真实 trace，user/host/session_file 全保留

## 用户意图（逐字）

- **U#0**（唯一提问轮）: `华大aether如何批量copy cell到目标文件夹`
- **U#16**（版本补充，非提问轮）: `SOS 7.05.p4 virtuoso wei 23.1` —— ⚠️ 注意：这是用户在**另一个**会话（1mndt）的版本补充，d1yda 本会话只有 U#0 一个提问轮，无后续追问。agent 单轮作答。
- **金标准** = msg[17] agent 末答：基于 Aether Design Manager 手册 `part_I_Design_Manager.md` Chapter 3 Edit → `3.1 Copy`（Copy Cell 3.1.2）+ `3.2 Copy Wizard` 给出批量复制流程，Copy Wizard 为批量入口（Show Copy List 表格勾选 + Cell 通配符过滤 + Update Instances New Copied/All）。

## agent 工具链

1. `skills(aether-tool-qa)` —— 调 Aether 知识库 skill
2. `search_codebase([copy cell / copyCell / batch copy / 复制 cell])` + `read_files(part_I_Design_Manager.md, aether_tool_qa.md)`
3. `run_commands(grep -ni copy ...)` —— 手册内搜 copy
4. `read_files(part_I_Design_Manager.md, start=291 end=700)` —— 读 Design Manager 手册
5. `editor(grep_copy.py)` + `run_approved_command` —— 跨手册文件 grep copy 相关行
6. `read_files(part_I_Design_Manager.md, start=769 end=865)` —— 读 Copy Wizard 章节
7. msg[17] 文字作答（Copy Wizard 批量 + Copy Cell 单个）

**关键产物**：无脚本交付，纯文字 howto 答。手册章节为 ground truth（`part_I_Design_Manager.md` lines 769-865 = Chapter 3 Edit §3.1 Copy + §3.2 Copy Wizard）。

## reframe 决策

- **形态**：manual-grounded howto Q&A → produce-parser reframe（承 r972 DbcoaZqCalCircuitExplainQA-001 范式 + r974 Ddr5WriteTaskParamExplainQA-001 verilog-source-as-fixture 子型续）
- **A 档 trace-faithful**：task prompt = U#0 逐字原文
- **判分牙**：SUT 产 `aether_dm_proc_extract.py` 解析器，读 Aether DM 手册 markdown fixture + query，输出结构化 procedure JSON；check() 只跑隐藏 B 手册（同操作 batch-copy-cell，不同术语/字段名/菜单路径），断言解析器是 manual-driven 非 hardcoded
- **asset A** = 真实手册 §3.1-3.2（Copy + Copy Wizard，逐字自 .75 trace GOLD，lines 769-865）
- **隐藏 B** = 同操作 batch-copy-cell 的重写手册（Edit → Batch Copy，字段名全置换：From Library→Source Library / To Library→Target Library / Cell→Cell Pattern / View Name→View Filter / Update Instances→Hierarchy Update / New Copied→Self Only / All→Entire Hierarchy / Add To Category→Target Category / Show Copy List→Copy Selection Grid），token 与 A 完全不相交
- **anti-hardcode**：A-only 字段 token 在 B 输出出现 ≤1；B 字段名 ≥4 命中；menu_path 匹配 B 非 A
- **domain**: analog_context（Aether Design Manager cell/schematic 库操作，D 域 schematic/cellview 邻域）

## 资产清单

- `assets/EDA-Eval-DesignFlow-AetherDmBatchCopyExplainQA-001/dm_manual_A.md` —— 真实 Aether DM 手册 Copy+Copy Wizard 章节（trace GOLD，lines 769-865，ligature 清理 ﬁ→fi ﬂ→fl）
- `assets/.../hidden/dm_manual_B.md` —— 重写 B 手册（同操作，置换术语）
- `assets/.../hidden/hidden_manifest.json`
- `assets/.../task_brief.md` —— U#0 verbatim + ≤3 行交付接口
- `assets/.../context_A.md` —— trace 上下文（agent 真实答 + 手册来源）
- `reference/.../check.py` —— 12 断言 a-l
- `reference/.../aether_dm_proc_extract.py` —— 参考解
- `reference/.../negative/{empty_shell,print_expected,delcore}.py + negative_selftest.py`
