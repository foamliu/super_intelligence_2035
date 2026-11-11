# deepread: 1789892513893_qopwl (lorikx @ hfeg0pkn001, mc30)

- **user**: lorikx  **host**: hfeg0pkn001  **session**: 1789892513893_qopwl.messages.json
- **match_count**: 30  **nmsgs**: 49  **keywords**: rtl:153; verilog:117; netlist:13; systemverilog:3 (clean A-domain, C=0 B=0)
- **domain**: digital

## 真实任务（U#0 原话）
> 帮我把top.sv内部修改一下，我需要生成fsdb文件，需要verdi来打开

## 对话脉络
- **U#0**: 改 top.sv 以生成 fsdb 供 Verdi 打开（produce-task 意图明确：VCD→FSDB dump 转换）。
- **agent**: 用 `list_allowed_files` / `read_files` 在 `/home/lorikx` 下广泛搜索字面名为 `top.sv` 的文件，未果。找到的候选：
  - `/home/lorikx/projects/tb_test/testbench/top_th.v`
  - `/home/lorikx/Work/tc_reg_con_v2/sim/tb_top.sv`、`/home/lorikx/Work/tc_reg_con_v3/sim/tb_top.sv`
  - `/home/lorikx/Work/tc_reg_con/sim/tb_jtag_pll1_mem_ctrl.sv`
- **agent 关键观察**: 部分 TB 用 `$dumpfile`/`$dumpvars`（VCD），需改 `$fsdbDumpfile`/`$fsdbDumpvars`（FSDB）才能给 Verdi 用 —— 这正是转换的核心。
- **U#48（最后）**: agent `ask_question` 让用户确认是哪个项目的 top.sv，**300s 超时、用户未答**。
- **结果**: agent **未修改任何文件**，无交付件。session 在 ask 超时处结束。

## A-faithful 判定
**不合格** —— 无完成的 agent 执行、无交付件可faithful复刻。用户也未给根因（没回答哪个文件）。但任务意图（VCD→FSDB dump 转换）清晰、是真实常见 EDA 操作。

## B档 合成方案
把「VCD dump → FSDB dump 转换」提炼成 **spec-driven generator** archetype（同族：VerdiFilelistGen-001 / ConCsvSliceOrderGen-001 / FilelistFlattenGen-001）：
- **deliverable**: `gen_fsdb_dump.py`，用法 `python3 gen_fsdb_dump.py <base_dir> <out_dir>`，读 `<base_dir>/top_tb.sv`，把 `$dumpfile("X.vcd")`→`$fsdbDumpfile("X.fsdb")`、`$dumpvars(d,s)`→`$fsdbDumpvars(d,s)`、加 `$fsdbDumpMDA()`，写 `<out_dir>/top_tb.sv`。
- **A/B 差异**: A=module top_tb / sim.vcd / depth 0 / scope top_tb / DUT u_dut；B=module regress_tb / regress.vcd / depth 2 / scope regress_tb.dut_inst / DUT dut_inst。硬编码 A 的解在 B 上必败（条件 f/g/h）。
- **判分**: 11 条独立断言 a-k，subprocess 在 B 上跑候选脚本（§4.2），3-seed shuffled-order 一致（§4.5）。

## 选料方法学发现（本轮副产品，重要）
r374-r396 的「strong A-tool as TOP」过滤（top 工具必须是 vcs/verdi/dc_shell/innovus 等 EDA 二进制）**漏掉了纯 RTL 编辑类 session**（top 关键词是 verilog/rtl/systemverilog 这些语言词，不是 EDA 二进制）。本轮用「clean A-domain (A>0, C≤5, B≤5)」过滤在 11/05 summary 上找到 **38 条 fresh**，其中 6/7 抽样首问为 analysis-only/Q&A（weak），但 **qopwl 是真 produce-task**。结论：strong-tool 过滤对纯代码编辑 session 有盲区，clean-domain 过滤能补；但补出来的多数仍是 weak，produce-task 命中率低（~1/7）。PIVOT 待用户裁决（自 r381）。
