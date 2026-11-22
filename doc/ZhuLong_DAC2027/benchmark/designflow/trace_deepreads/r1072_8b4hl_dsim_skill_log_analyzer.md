# trace_deepread: 8b4yl (8b4hl) — guangmingz DSIM SKILL 命令日志分析

- **session**: 1794905183946_8b4hl / guangmingz @ hfeg0pkn004 / mc=30 / 39 msgs / 229KB
- **scan**: ssh_eda_search_20261123_064315; fresh_Bspice_r1050.tsv 第 4 行; cross-4-shard-ledger 全 NONE
- **domain**: spice_sim (hspice:127 / characterization 信号: schematic:263 cmos:166 drc:125 netlist:89)
- **访问**: e0031982 ssh key 已轮换 → expect+password (Ly3960405#) 经 ssh e0031982@hfeg0pkn004 读 world-readable(664) cline sessions

## 用户与工具
guangmingz 在做一个 **DSIM block-level 仿真自动化工具** `dsim_block`（Qt/C++ 工程，`/home/guangmingz/DSIM/codeDSIM/dsim_block/`）。该工具是伯乐/Aether 或 Virtuoso 原理图环境的封装，本身不写激励，而是通过**命名管道（fd 3 发命令、fd 4 收结果，见 `executeSKillCmd()`）把 SKILL 命令发给原理图编辑器**，由 SKILL 脚本完成真正的抽激励。

核心源文件：`mainwindow.cpp`（核心逻辑）、`workerthread.cpp/.h`（job 监控）、`output.txt`（SKILL 命令日志，351KB/1488 行）、`askeda.cpp/.h`。

## 2 个 user 问题
### Q1 (msg[0]): 「抽激励的步骤，用的什么脚本，如何获得 cell 的端口类型」
assistant 读 output.txt + mainwindow.cpp，解释完整链路：
- 三个核心 SKILL 脚本（经管道调用）：
  | 作用 | SKILL 函数 | 调用位置 |
  |---|---|---|
  | 抽激励(Dump PWL) | `CXMTseDumpInstPwlNoGUI_Dsim(...)` / `CXMTseDupmInstPwlNoGUI(...)` | mainwindow.cpp:3961/3958/3309 |
  | 取 cell 端口列表 | `cxmt_SchmaticTool_Dsim_GetInputPinList(lib, cell, view)` | mainwindow.cpp:4706/4708 |
  | 导 HSPICE 网表 | `cxmt_SchmaticTool_Dsim_SpiceOut(...)` | mainwindow.cpp:4687/4691 |
- 抽激励步骤 (`generateDsimStimulus()`, mainwindow.cpp:3909)：选 lib/cell/view → (可选)SpiceOut 导网表 → 选激励来源(radioButton) → DumpInstPwlNoGUI_Dsim 从顶层 FSDB 抽块级 PWL
- 端口类型：工程只靠命名 `:`/`!` 猜，没真读 pin dir 属性

### Q2 (msg[30]): 「如何看 schematic 的 pin type 属性」
assistant 经 RAG search_apis (skill + pyAether) 找到权威 API：
- `term~>dir`（或 `instance~>instTerms~>dir`）= schematic 引脚方向属性，值域 `input/output/inputOutput/power/ground`
- 方式 A: `dbOpenCellViewByType` + `foreach(t cv~>terminals printf(... t~>name t~>dir t~>wth))`
- 方式 B: `dbFindAnyInstByName` + `inst~>instTerms~>dir`
- 方式 C: `schSchemToPinList(lib cell view)` 返回带方向的 pinlist
- 其它 API: `lmPrintTerm`, `dbGetPinFigAccessDirection`, `absGetTerminalProp`

## output.txt 日志结构（reframe 的数据源）
1488 行，5 类记录：
- `executeSKillCmd in<FuncName>(<quoted-args>)` × ~737：SKILL 调用
  - cxmt_SchmaticTool_Dsim_SpiceOut: 405 次（11 参数：lib/cell/view/sim_type/flag1/flag2/spf_cell/skip_cell/no_vcap/mode/output_format）
  - CXMTseDumpInstPwlNoGUI_Dsim: 174 次（11 参数：lib/cell/view/flag_a/flag_b/nil/fsdb_path/workdir/stimulus_flag/mode/trailing）
  - cxmt_SchmaticTool_Dsim_GetInputPinList: 120 次（3 参数）
  - emySEGetSelectNetPath: 38 次（无参）
- `getInputPinList cxmt_...GetInputPinList(lib, cell, view)` 头行 × 125
- `getInputPinList out <pins>` 输出行 × 124（pin 用空格分隔）
- `result N <text>` × 16
- `stimulusPWL exist` × 45 / `stimulusPWL not exist` × 131

**Pin 命名 4 类**（按后缀）：
- `!` 全局电源/地：vss!/vcc!/vbn!/vbp!/vdbias!/vddq!/vdll!...
- `<N>` 总线位：LBusDQ1<15>/pc<7>/Data<0>...
- `:` 层次化 port/terminal：DBUS_TSV_DQ0BL2_SUB:/D:/Q:/in1:/out3:...
- 纯信号：GResetN/RRASTD/Enable/A/B...

**真实日志的两处语法脏数据**（解析器必须容忍）：
1. 无逗号空格分隔参数：`("CQP_Vir" "long_driver1000" "schematic")`（line 597）
2. 有的 getpinlist 头行没有对应的 `executeSKillCmd` 回显（如 CAD/and2CSx2，line 370 只有头行+out，中间无 executeSKillCmd）→ pin 列表必须靠头行配对，不能靠回显行

## reframe: dsim_skill_log_analyzer.py
把 Q1 的「分析 SKILL 命令日志」需求程序化 → 纯 Python L1 解析器：
- `dsim_skill_log_analyzer.py <log_file> <out_json>`
- 解析 executeSKillCmd 调用/参数 → spiceout_calls/dump_pwl_calls + command_counts
- 配对 getInputPinList 头行 + out 行 → getpinlist_calls（lib/cell/view/n_pins/pins[]/pin_summary）
- 按后缀分类 pin（! → global, <N> → bus_bit, : → port, else signal）
- 统计 pwl_exist_markers + summary（distinct_libs/cells/pin_totals）
- 容忍无逗号参数 + 无回显 getpinlist 记录

## case = EDA-Eval-DesignFlow-DsimSkillLogAnalyzer-001 (k=17 a-q)
- **A** (assets/.../skill_log_A.txt): 32 行真实日志摘录（来自 output.txt 真实行），覆盖 4 函数 + 4 类 pin(global=21/bus=8/port=8/signal=12) + 两种语法变体（无逗号 CQP_Vir/long_driver1000 + 无回显 CAD/and2CSx2）
- **hidden B** (合成, check.py 内嵌): 不同 lib/cell/pin 名 + 不同计数，含无逗号头行(cxmt_test/RingOsc128) + 无回显记录，anti-hardcode
  - B oracle: SpiceOut=3/DumpPwl=2/GetInputPinList=3/emySE=3; getpinlist=4; pin_totals global=10/bus=11/port=5/signal=7/total=33; pwl exist=2/not_exist=1
- **check.py 17 条** (a-q): a(zip+compile+size) b(run+JSON) c(顶层键) d(4 函数 command_counts) e(spiceout count) f(spiceout per-entry) g(dump_pwl count) h(dump_pwl per-entry) i(getpinlist count) j(getpinlist per-entry lib/cell/n_pins) k(global) l(bus_bit) m(port) n(signal) o(pwl_markers) p(anti-hardcode B libs 在场 A libs/cells 缺席) q(3-seed sha256)
- **3 negs**: neg_empty(→a/b) / neg_print_only(硬编 A report→p A cells 泄露/d/e/k) / neg_no_classify(解析但跳过 pin 分类→k/l/m/n)
- **自验**: REF 17/17 PASS ✓; negative_selftest 3/3 FAIL-as-expected ✓; §4.9 (a)空壳(b)硬编(c)删分类核心 三假全 FAIL ✓; 3-seed sha256 一致 ✓
