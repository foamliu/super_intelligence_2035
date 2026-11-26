# deepread — 1794191874918_jt7be (jt7be)

- **user**: e0039602
- **host**: hfeg0pkn003 (load-balanced: 10.129.2.12 / 10.129.8.227 / 10.129.8.235)
- **session**: 1794191874918_jt7be.messages.json (1,098,223 B, 189 msgs: 101 user / 88 assistant, agent=lead)
- **mc**: 311 (verilog:987 / netlist:692 / lvs:544 / drc:28)
- **updated_at**: 2026-11-09T03:39:16Z
- **domain**: digital (A-core, strict first-keyword = verilog)
- **infra note**: r546 误判 infra-block —— 文件在 `sessions/<sid>/<sid>.messages.json` **子目录**（非 flat），r546 用 flat 路径 `sessions/<sid>.messages.json` 全 NOFILE；改 subdir 路径 + 10.129.8.227 即可 scp/读。**p0fqe-class infra-block 实为路径错误**，非 load-balancer 漂移。

## 真实意图（9 条 user_input, mode=act 全为 produce-task）
项目 `verilog_lib_trans_skill_aifree` 把 Verilog 网表标准单元按固定规则转 SystemVerilog：
1. (idx0) 改 resultmap 输出逻辑：无法固定规则转换（需大模型）的不打印，只保留成功的；跑 `final_merged_netlist_digitial.v`。
2. (idx42) 最终 SV `final_merged_netlist_digitial_converted.sv` 只写成功模块，未转换完全不写。
3. (idx58) 用 `block_name_digital.log` 作 block 清单重转（可作 runskill 命令行输入）。
4. (idx67) 跑 `final_merged_netlist_stdcells_ac.v` + log `block_name_stdcell_ac.log`。
5. (idx76) 读 `final_merged_netlist_stdcells_ac.v` 与 golden `simlib_stdcells_ac_copy.sv`，判断 `dlybias`/`dlybiasn` 能否固定逻辑转换无须大模型。
6-7. (idx98/99) 严格按 8 档插值/线性推生成延迟单元（dlyrc/dlybias/dlybiasn）：`buf #(...)` 延迟、`dlyrc_base .STEP/.TR_D`、`specparam tRise/tFall = (ps-10):ps:(ps+10)`、specify 块。
8-9. (idx136/138) Q&A：「以后遇到这类型都能写对吗」→「按现有 8 档插值/线性推，自动判断其他参数」。

## agent 工具链（92 tool_use）
list_allowed_files / read_files / editor / run_approved_command(python-runner) / run_commands / search_codebase。**纯 python，无 EDA 工具运行**（无 vcs/vsim/calibre）。

关键产物（远程 `/home/e0039602/Documents/verilog_lib_trans_skill/verilog_lib_trans_skill_aifree/`）：
- `run_skill.py` —— 改 `_write_block` / `_run_extract`：result_map 只写成功模块；`--block-list` arg。
- `extract_converted_sv.py` —— 改成只写已转换 module（`--only-converted` 默认）。
- `src/delay_cell_rules.py` (1260 行) —— **核心**：`_DELAY_RE = ^(dlyrc|dlynrc|dlybias|dlybiasn)(\d+)ps$`；`DELAY_CELL_GOLDEN` 字节固化 8 档 golden；参数化生成器 `_LEVELS=[250,500,750,1000,1250,1500,1750,2000]`，`_FAM_BUF`/`_FAM_STEP` 8 档表，`_interp`（分段线性+端斜率外推），`_timing`（dlynrc rise 固定 100:150:200），`_build`（族相关 buf/Ain_tmp/nmos-pmos 偏置栈/TR_D/FPulse/specify 块），`lookup`/`is_delay_cell`。
- outputs: `result_map_*.txt`、`final_merged_netlist_*_converted.sv`、`map_rerun_*.txt`。

## 合成决策
- **A档 INFEASIBLE**：完整产物在远端 698 机（不在 SUT 沙盒），1.1MB session + 大 netlist 无法入 assets；强引 = 超体积 + 非自包含。
- **B档合成**：聚焦最 distinctive 可测子能力 —— 延迟叶单元参数化 SV 生成 + result_map 过滤。archetype = `verilog-delay-cell-parametric-svgen`（A.jsonl 无同类，已 grep 确认）。
- reference `delay_gen.py` = trace `delay_cell_rules.py` 参数化部分的忠实移植（同 `_interp`/`_timing`/`_build` 逻辑、同 8 档表、同族规则）。
- 可见 A：4 个档上 ps (1000/500/750/750) + 2 非延迟 (bufx4/and2) 应排除。
- 隐藏 B：4 个非档 ps (325/850/1400/2200 需插值/外推) + 2 非延迟 (invx2/nand2b) 应排除 —— B 与 A 取值/规模不同。
- check 17 条独立断言（k_check=k_rationale=17≥8），覆盖：regex 过滤 / 插值数值 / 外推 / 族相关 buf/Ain_tmp 偏置栈 / TR_D-FPulse / tRise-tFall / result_map-only-success / converted_sv-only-converted / 确定性 / 非硬编码。
- 5 negative 全 FAIL（naive_empty/print_only/hardcoded_A/core_removed/regex_broken）。
- 难度 L1（trace 即纯 python 规则引擎，无 EDA 工具运行；A档 trace-faithful 优先于 L2/L3 新建倾向）。

## 自验
- reference check.py 17/17 PASS。
- negative_selftest 5/5 全 FAIL。
- reference_submit.zip 落盘。
