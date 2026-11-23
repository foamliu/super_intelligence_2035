# Trace Deepread — qs9e9 (eva1li / hfeg0pkn003) — r1050

- session: `1794902668080_qs9e9.messages.json` (141632 B, alive on 10.129.2.12)
- user: eva1li ; host: hfeg0pkn003 ; mc=47 ; domain verdict: **digital** (ac=219: verilog:167+rtl:28+synopsys:24 >> cc=5(aether:5) >> bc=90(cadence:66=vendor not C-tool))
- sourced from: ledger_A line 836 (r1021 parked, r1049 domain-corrected cross_domain→digital)

## 对话流（20 msgs, 2 用户问题）

- **U#0** (Q&A): `simvision怎么在design browser框里搜索一个rtl的例化名` → agent 查 AskEDA 知识库，给 SimVision Design Browser 搜索栏 + Find 菜单两种方法（解释性回答，无脚本/文件）。
- **U#6** (本 case 取材): `catch the top signal from @/proj/decqa/V0/simdir/verilog/eva1li/1103_lp6tb/link_ecc_log/link_ecc.link_ecc.x24/ncsim.shm` → agent 依次 list_allowed_files / read_files 读 `top.sv` + `probe.tcl` + `irun.log` + `verilog.rc` + `.out` + `A_Summary.rpt`，发现：
  - 顶层模块 `TOP`，例化 `Chip`(PROJECTNAME) + `A_pattern_gen`/`B_pattern_gen` 等
  - `probe.tcl`：`database -open -shm ncsim -incsize 5G` + 27 条 active `probe -create TOP[.A_pattern_gen|B_pattern_gen|in_powerdown|reset_req].* -depth all|to_cells [-packed N]` + 注释行 + `run`/`drivers -active`/`exit`
  - 仿真在 12233ps 时 segfault 崩掉（ncsim 内部异常）
  - agent 给解释性回答：说明 ncsim.shm 是 Cadence 二进制快照、要用 Cadence SimVision 打开、列了顶层 TOP 模块与 probe 层次。**没产脚本/文件**。

## reframe（按 11-15 令）

trace U#6 真实意图 = 「抓顶层信号层次」。agent 给了解释但没产可复用产物。reframe 成 produce-task：写通用 Python 脚本 `parse_probe_tcl.py`，把任意 probe.tcl 解析成结构化 JSON（database 名 / probe 层次 / depth / packed / flags / top-level groups / non-probe commands）。这把「解释性 Q&A」升级成「可复用交付物」，同时保留用户原始意图（理解一次仿真 dump 了哪些顶层信号层次）。

## 产物

- visible A = 真实 probe.tcl（LPDDR6 testbench，44 行，27 active probes，db=ncsim）— 原值保留
- hidden B = 构造的 SerDes/PCIe testbench probe.tcl（不同 db 名 serdes_wv、不同层次 tb_top.xmit_lane0/1|recv_lane0/1、18 probes、4 packed、5 comments）— 与 A 规模/取值/结构均不同
- reference: `parse_probe_tcl.py`（通用解析器）
- check: 20 条独立断言（k_check=k_rationale=20 ≥ 8），含反硬编码A / 确定性 / 反空壳 / 反print-only / 反core-deleted
- negatives: naive(硬编码A-shaped) + always_stub(硬编码B-shaped但comment_count故意错)

## 自验

- reference PASS check ✓
- 空壳 FAIL（size<200B）✓
- print-only FAIL（无 output json）✓
- core-deleted FAIL（unique_signal_paths length 0!=18）✓
- 2 negatives 全 FAIL（negative_selftest rc=0）✓

## case_id

`EDA-Eval-DesignFlow-ProbeTclSignalHierarchyExtractProduce-001` → `cases/A/EDA-Eval-DesignFlow-ProbeTclSignalHierarchyExtractProduce-001.json`
