# trace_deepread: 1794445729302_9kc99 — VerilibEquiAnalyze-001

- **session**: `1794445729302_9kc99.messages.json`
- **user / host**: e0039602 @ hfeg0pkn003 (10.129.2.12)
- **match_count**: 77 (verilog:672;drc:222;netlist:209;lvs:42;systemverilog:10;schematic:5;aether:5;transistor:4)
- **NMSG**: 27 (lead agent), updated_at 2026-11-12T02:22:47Z, file 680KB (alive Nov 13 mtime, confirmed 11-18)
- **ledger**: was parked r503 (2026-11-14) as "阅读目录告诉我项目在做什么/TB怎么构建 pure analysis Q&A"; under 11-15 new intent standard analysis-Q&A is legitimate → revived + marked case r713 (EDA-Eval-DesignFlow-VerilibEquiAnalyze-001)

## 用户真实意图（原话）

- **U#0**: `/home/wellesc/VerilogLibVerifiy  请你仔细阅读这个目录下的所有内容，告诉我这个项目在做什么`
- **U#20**: `TB是怎么构建的呢，如何做到这个TB能同时运行网表和sv文件？`

真实交付意图 = 阅读 DRCOA 标准单元库 Verilog 网表功能等价性验证项目，理解 (a) 项目做什么 (b) TB 如何在单次 xrun 中同时编译 .v 网表与 .sv。

## 项目实际是什么（从真实文件确认）

DRCOA 标准单元库 Verilog 网表 **功能等价性验证项目**：
- **方法**：同名 golden-镜像对比（golden vs DUT 逐拍仿真比较）
- **三库**：`01_veriloglib_golden/` 下 `00_drcoa_stdcell_dut` (1529 cells) / `01_drcoa_digital_dut` (623) / `02_drcoa_stdcell_ac_dut` (1982) = **4133 cells**
- **仿真器**：Cadence Xcelium 23.09 `xrun`，路径 `/apps/cdsmgr/CRB/XCELIUM2309/tools/xcelium/bin/xrun`
- **xrun 编译选项**：`-64bit -sv +access+rwc +define+LocalPower +define+CDLYW=1 -ALLOWREDEFINITION -nospecify`
- **调度**：LSF 集群，队列 `verilog`，全库 4133 cell 并行回归
- **TB 同时跑 .v + .sv 的机制**（用户问的核心）：不是"链接两个文件"，而是靠 xrun 单次统一编译把 .v 与 .sv 混进同一 worklib，TB 顶层 `tb_<cell>` 对同一份信号网实例化两个同名 cell——golden 由 `make_golden_alias.py` 改名为 `module <cell>__gld`，DUT 保持 `module <cell>`，两侧输入接同一激励网、输出接不同网，逐拍比 `out_g !== out_d`，`err>0` 即 FAIL。
- **结果判读**：`RESULT cell=.. lib=.. K=.. W=.. checks=.. err=.. xmatch=.. PASS/FAIL`，`err=0` 即 PASS；`TIMEOUT-FAIL` 超时；`*E,*C,*F` 编译错 → NODUT。
- **.clinerules**：规则1 使用中文回复（lang=zh）。

## agent 流水线（trace 实际发生）

list_allowed_files 浏览目录(3层) → read_files 读 `.clinerules`/`b_random_TB/handoff.md`/`simulation_guide.md`/`c_VeriligLibVerifier/non_pass_classes.md` → read_files 读 `lsf_verify.py`/`make_report.py`/`verify_cell.py`/`result_all.csv`/`under_test_dut_report.md` → 产出结构化中文分析报告（项目一句话概括 + 目录结构 + TB 构建原理 + xrun 编译列表）。

## produce-task 化（交付件）

`analyze_verilib_verify.py <project_dir>` 通用解析任意"同形 golden-vs-DUT 单元库等价性验证"项目树 → JSON：
`{project_type, golden_root_dir, libs[name,golden_sv,cell_count], simulator, simulator_version_path, simulator_flags, scheduler, queue, golden_rename_suffix, compare_method, tb_top_pattern, result_columns, pass_criterion, total_cells, clinerules_lang}`。

## 判分设计

- **A（可见）** = 真实 DRCOA 项目树精简版（真实文件内容：.clinerules zh / run_cell.sh XCELIUM2309 +define+LocalPower +define+CDLYW=1 / simulation_guide.md / result_all.csv K/W/err/verdict / 三库 simlib_*.sv / under_test_dut_report.md），供 SUT 开发自验。
- **B（隐藏）** = 同形 SKY130 变体（不同取值）：三库 00_sky_stdcell_dut/01_sky_digital_dut/02_sky_stdcell_ac_dut (880/412/1156=2448) / xrun XCELIUM2409 / +define+PWR_GATE +define+SDF_DEL=0 / queue=stdcell_q / 后缀 __gold / .clinerules en / result csv (lib,cell,vectors,checks,mismatch,xmatch,status)。
- **check.py** 21 条独立断言（k=21）：在隐藏 B 上跑候选脚本，断言 B-specific 值 + 反硬编码 A（A-only 的 +define+LocalPower / queue=verilog / __gld / 4133 / zh / XCELIUM2309 / K,W,err,verdict 列 / 1529,623,1982 必须不出现或取 B 值）。
- **§4.9 三假提交**：neg_empty（空壳）/ neg_print_expected（硬编码 A 值）/ neg_core_deleted（删核心解析）全部 FAIL。

## 自验结果（r713）

- reference_submit.zip → check.py 21/21 PASS
- negative_selftest：3 neg 全 FAIL-as-expected，ref PASS-as-expected，OVERALL PASS
- k_check == k_rationale == 21（①-㉑ 完整）
- A.jsonl 364 → 365

## 备注

- 真实项目树 100MB（含 4577 .sv sim dump + xcelium.d 仿真产物），ssh 自 .75 遍历多次 timeout；最终用 ssh cat 单文件抓取核心文档/脚本的真实内容，A 档附件用"真实文件内容精简版"（保留全部判分相关事实，drop 100MB 仿真产物与 merged 网表），与 r708 FineSim 案"真实但精简"做法一致。
- 9kc99 是 r711 §II 候选池重审里"被旧 analysis-only=weak 筛子误杀"的典型，按 11-15 任务初衷复活。
