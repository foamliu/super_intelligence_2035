# Deepread: 1793674800055_2xkge — cla_top DC-synth-flow SDC generation (digital, A档 faithful)

## Trace
- session: `1793674800055_2xkge.messages.json` (871 KB, 151 msgs)
- user/host: e0046913 @ hfeg0pkn003 (10.129.2.12)
- markers: 89 synthesis + 77 netlist + 7 schematic (pure digital DC-synth flow)
- fresh: 11/03 session (not in any prior ledger)

## A档 turn selection (rule ②)
- User turn #0: "针对cla_top这个design跑综合流程，我首先需要准备哪些输入件、进行哪些配置？" — 咨询性（问需要什么），偏弱。
- User turn #43: "我想完全依据cla_top的lint flow设置来运行cla_top的综合…" — 目标表达，但偏"如何做"的引导。
- **User turn #75 (选用)**: 「如何生成一份带真实时钟/IO 占位的 data/cla_top.sdc（告诉我 cla_top 的主时钟名和周期）？帮我生成一份」
  - clean 提需求（生成一份带真实时钟+IO占位的 SDC，并告知主时钟名/周期），未给根因/未给修复 → **A档规则②合格 → A档 faithful**。
- 排除的轮：#128/#130/#132（用户已指出根因 RTL_SOURCE_FORMAT verilog→sverilog，给出修复方案）→ 禁用 A档②。

## 真实资产（助手 read_files 读取，已逐字提取）
cla_top RTL（5 文件，`/rundata/lacaa/TV1_digital/simdir/yutingq/CXDP/cla_top/src_rtl/`）：
- `cla_top.v`: 顶层 16-bit CLA，parameterized WIDTH=16。端口 `input [WIDTH-1:0] a,b` / `input cin` / `output [WIDTH-1:0] sum` / `output cout`。**无任何 clk 端口**（纯组合）。例化 `cla_recursive #(.WIDTH(WIDTH)) u`。
- `cla_recursive.v`: 递归 CLA（WIDTH=1→full_adder / =2→cla2 / =4→cla4 / else 4-way 递归），含 generate + `.*`、`+:` 部分选择。
- `cla4.v`: 4-bit CLA（assign 链）。
- `cla2.v`: 2-bit CLA。
- `full_adder.v`: 1-bit 全加器。

## 金标准（助手 msg A80/A82，用户接受）
助手读 RTL 后发现 **cla_top 是纯组合逻辑、没有时钟端口**，于是：
- **不**用 `create_clock [get_ports clk]`（会因找不到脚位报错）；
- 改用**虚拟时钟** `create_clock -name vclk -period <period_ns>`；
- `set_input_delay -clock vclk -max <input_delay_ns> [get_ports [list a b cin]]`；
- `set_output_delay -clock vclk -max <output_delay_ns> [get_ports [list sum cout]]`；
- `set_input_transition 0.1 [all_inputs]` / `set_load 0.02 [all_outputs]`；
- 保留 3 个占位 `<period_ns>`/`<input_delay_ns>`/`<output_delay_ns>`（用户要求"IO 占位"）；
- 注释里给出"若加真实时钟脚位则改写"与 `set_max_delay` 备选。
- 用户 #83 即转向下一子任务（dont_use tcl），未否定 SDC ⇒ **隐含接受**。

## Case scope（verb: `rtl-derived-sdc-gen`）
通用 SDC 生成器：读 RTL 目录 → 解析 top 模块端口 → 检测有无真实时钟端口（1-bit input + clk/clock 命名启发式）→
- 有真实时钟：`create_clock -name <clk> -period <P> [get_ports <clk>]`；
- 无时钟（组合）：`create_clock -name vclk -period <P>`（虚拟时钟）；
- 生成 set_input_delay/set_output_delay 绑定该时钟 + IO 占位 token。
与所有已有 shard-A verb 互斥（sta-flow-scaffold=构建 flow 树 / netlist-port-connectivity-extract / lib-to-parm / synth-upf-diagnose / apr-stamp-fix / flat-net / apr-setup-audit / apr-log-audit / vcs-equiv / vcs-makefile / itf-compare / calibre-pdf2md）。

## A/B 输入（cross-input guard 击破硬编）
- **A 可见** = cla_top 5 RTL 文件（真实，纯组合，无 clk）→ 期望虚拟时钟 SDC。
- **B 隐藏** = `clk_div8.v`（合成，时序电路，真实 `input clk` + rst_n/en + cnt[7:0]/tick）→ 期望 `create_clock [get_ports clk]`。
- 击破：只生成虚拟时钟的硬编 → B FAIL；只绑定 clk 端口的硬编 → A FAIL；hardcode cla_top 输出 → B run 崩溃。

## 判分（check.py 14 条 a–n，纯 stdlib + subprocess 跑候选于 A+B）
a zip2件 / b py_compile / c 候选跑 A exit0 / d A 虚拟 vclk / e A 不绑定端口 / f A set_input_delay vclk + a,b,cin / g A set_output_delay vclk + sum,cout / h A 占位 token / i 候选跑 B exit0 / j B [get_ports clk] / k B 非裸 vclk / l B 端口名=clk / m gen_sdc.py 含 CLI / n 跨输入结构差异(A虚拟/B端口)。

## 自验
- ref `gen_sdc.py` + `cla_top.sdc` → check.py **PASS 14/14 (a-n)**。
- 5 negatives 全 FAIL（NEG_RC=0）：fake_empty→c / fake_print_expected→j / fake_core_deleted→j / naive_always_virtual→j / naive_hardcode_cla_top→i。
- §4.9 (a)(b)(c) 三假全 FAIL ✓。
- 判分纯 stdlib python3（无 DC/VCS/PT license 依赖），本地 PASS == 判分环境等价。
- 🧾 断言: k_rationale=k_check=14 ≥8 ✓ GATE PASS。
