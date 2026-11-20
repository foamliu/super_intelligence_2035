# Deepread: 1793611777735_q9ulk — xrun TYPEERR bit-select string-index diagnose

## trace source
- session: `1793611777735_q9ulk`
- user: `ruisongs` @ `hfeg0pfn087` (10.129.33.213)
- domain: verification (xrun elaboration debug-Q&A)
- mc=31; 35 msgs; messages.json 159KB
- parked r506 (旧判 analysis-Q&A REJECT) → 11-15 §II 复活（debug-Q&A 真实用户意图）

## 用户真实意图（U#0 原话）
```
<user_input mode="act">/proj/drvqa/V0/simdir/verilog/ruisongs/array_test/verilog.ddr5.drvqa.test/build_file/noregression.x8,看下xrun。log的err</user_input>
```
→ 用户要 agent 看 noregression.x8/xrun.log 的 error，找出根因。

## agent 工具链（trace 真实路径）
1. `get_agent_policy_status` → policy enforcing
2. `list_allowed_files` noregression.x8 → 列出 build dir 文件
3. `read_files` xrun.log → 50K+ 行，截断
4. `read_files` agent-policy.json → 看 allowedScriptRoots
5. `editor` 写 `/home/ruisongs/grep_xrun2.py`（grep error 模式 + tail）
6. `run_approved_command` python-runner grep_xrun2.py → 拿到 TYPEERR 列表
7. `read_files` xrun.log 95295-95345 → 错误上下文（csl 信号 bit-select）
8. `run_approved_command` find_sv.py（递归找 simlib_drvqa_array.sv，超时 SIGKILL）
9. `list_allowed_files` test dir → 发现 `libs/simlib_drvqa_array.sv`
10. `read_files` simlib_drvqa_array.sv 6100-6306 → 看 module `array12Meg_E_UW_dwl`
11. `read_files` simlib_drvqa_array.sv 6196-6260 + 6420-6575 → 看 csl 用法
12. `search_codebase` tbctrlmonitors / csl / csl_key / array_piece

## 根因（trace 确证）
- xrun.log: 103374 行；**24 条 `*E,TYPEERR`**，全在 `./libs/simlib_drvqa_array.sv`
- 错误信息: `[] (bit select) index expression type illegal.`
- 两块：block1 = log 行 95307-95340（.sv 行 6450-6567，12 条）；block2 = log 行 96315-96348（.sv 行 6187-6303，12 条）
- 收尾: `*E,ELBERR`（elaboration status 1）+ `*E,RUNERR`（xrun status 1）
- 信号: `TOP.A_proj_monitors_if.tbctrlmonitors.csl`
- .sv 源（6148）: `function int pcs_idx(input bit [1:0] piece, input bit [1:0] csl);` ← csl 是 2-bit 标量
- .sv 源（6136）: `string my_key;` ← my_key 是 string
- .sv 源（6194）: `pcs = pcs_idx(...tbctrlmonitors.csl);` 调用 OK
- .sv 源（6198/6209/...）: `(TOP.A_proj_monitors_if.tbctrlmonitors.csl[my_key] == 2'b01)` ← **bit-select 用 string 索引 my_key → TYPEERR**
- 根因一句话: `tbctrlmonitors.csl` 是 2-bit 标量信号，被 `csl[my_key]` 用 string 类型变量做 bit-select 索引，索引表达式类型非法 → 24 处 TYPEERR → ELBERR → RUNERR，elaboration 失败退出。

## 可判分要点（checkable deliverable）
SUT 交付 `analyze_xrun_typeerr.py`，接受 build_dir（含 xrun.log + libs/*.sv），输出 JSON 诊断报告，字段：
- total_log_lines / failing_step(xmelab) / primary_error_code(TYPEERR)
- typeerr_count (B 实际值) / source_file (B 实际值)
- offending_signal (B 实际值) / index_variable (B 实际值)
- index_variable_type (string) / bit_select_is_illegal (True)
- elaboration_error_code(ELBERR) / run_error_code(RUNERR)
- root_cause 文本（含 B 信号名 + string-index 诊断）
- anti-hardcode: B 值 ≠ A 值（信号/文件/行号/计数/索引变量全异）

## B 隐藏变体设计（≥8 维全异于 A）
A (trace-faithful):
- source_file = simlib_drvqa_array.sv
- offending_signal = csl
- index_variable = my_key
- typeerr_count = 24
- sv error lines = 6187-6303 + 6450-6567
- log error lines = 95307-95340 + 96315-96348
- elaboration exit = ELBERR + RUNERR
- module = array12Meg_E_UW_dwl

B (synthesized):
- source_file = simlib_drvqa_monitor.sv
- offending_signal = pcs_en
- index_variable = key_str
- typeerr_count = 18
- sv error lines = 4210-4326 (one block, 18 errors)
- log error lines = 88450-88471 (one block)
- elaboration exit = ELBERR + RUNERR (same code, different status msg)
- module = monitor_drvqa_xcheck
所有数值/名称/行号/计数 B ≠ A，证明脚本非硬编码。
