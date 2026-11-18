# trace_deepread: wi5an — Verdi FSDB "List of Signal Not Found" 诊断

## 一、trace 元数据
- session: `1794559200062_wi5an`，user `tabtao`，host `10.129.2.12`，mc6
- agent: `lead` (zhulong)，12 msgs，messages.json 66949 B（小，可单轮合成）
- keywords: rtl:35;netlist:34;verilog:9;synthesis:9;schematic:8;systemverilog:6;synopsys:5
- ssh ALIVE 确认 (r725)：`/home/tabtao/.cline/data/sessions/1794559200062_wi5an/1794559200062_wi5an.messages.json`
- 路径修正：session 是**目录**，messages.json 在目录内（与 r723 发现的 `.messages.json` 后缀 bug 同源，本次确认 `<sf>/<sf>.messages.json` 嵌套结构）

## 二、用户真实意图（逐条 user 原话）
- U#1..U#4（重复 4 次，用户重试）: `在使用verdi拉波形的时候有如下提示：` + 5 条信号路径
- U#4 带 `List of Signal Not Found:` 前缀（最清晰版本，A 档 prompt 取此）
- U#6: 贴 `$fsdbDumpvars(0, TOP,"+struct"); $fsdbDumpvars(0, TOP,"+all"); $fsdbDumpMDA();` dump 代码
- U#8: `Error-[UST] Undefined System Task Call ... '$fsdbDumpfile'` 报错
- U#10: 合并 `+all +struct` 后顶层端口 (CRESET_N/REF_CLK/HCLK_P/FP_JTAG_*/GPIO PAD/C/I) 也 dump 不到

→ **首问交付意图**（A 档取此，单条连贯）：诊断「信号找不到」——对列出的信号按插入来源分类 + 根因 + 修复。
  后续 U#6/U#8/U#10 是同一调试会话的演进（dump 代码→UST 报错→顶层端口也丢），属同主题但不入单条 produce-task。

## 三、助手流水线与分析（A 档 ground truth）
msg5 助手把 5 条信号分 3 类（关键判断 = 判分「牙」的来源）：
| 信号 | 助手判定 | 来源 |
|---|---|---|
| `.../dont_touch_clk_buf_Z_inst/uvt_pvcell_clk_mux2_clock_out/FE_OFN1451_n` | FE_OFN* = **扇出优化(fanout optimization)插入 net**；dont_touch_clk_buf = 保留时钟 buffer；uvt_pvcell_* = PV cell | 综合/物理 |
| `...GPIO_15__u_cxmt_dont_touch_GPIO_macro_pin_buf_C_BUF_i_0.I` | macro_pin_buf / `.I` = **macro 引脚 buffer cell 内部 pin** | 门级 cell 内部 pin |
| `CCOPT_INST__ccl_inv_32564.I` (x3) | **CCOPT (Clock Concurrent Optimization, CTS) 插入反相器内部 pin** | CTS |

根因：门级 post-synthesis/物理设计插入的信号不在 RTL；cell 内部 pin 需 `+struct`。
修复（msg7/9/11）：合并 `$fsdbDumpvars(0,TOP,"+all +struct")`；链接 Verdi PLI `novas.tab`+`pli.a` (`-P`，否则 UST)；核对 FSDB top scope (`fsdbDumpfile -listhier`/`fsdb2vcd`)；cell 内部 pin/插入 net 从原理图追驱动 net。

## 四、produce-task 化
`diagnose_fsdb_signal_not_found.py <signal_list_file> <output_json>`：
- 解析任意信号清单（`/` 或 `.` 分隔），按 leaf/路径模式 7 类分类
  (gate_insertion_fanout / gate_insertion_cts / pv_cell / macro_pin / preserved_buffer / cell_internal_pin / rtl_signal)
- 派生根因 (gate_level_post_synthesis_insertion / cell_internal_pin_not_dumped / fsdb_dump_scope_or_pli_misconfig)
- 给 4 条修复；输出 {signals, summary, root_causes, fixes, overall_verdict}

## 五、A / B 设计
- **A**（trace-faithful，真实 5 信号）：FE_OFN1451_n + macro_pin_buf GPIO_15 `.I` + CCOPT ccl_inv_32564 `.I` x3
  → fanout=1/macro_pin=1/cts=3，verdict=`gate_level_signals_and_cell_pins_not_in_rtl`（无 rtl_signal → 无 misconfig 分支）
- **B**（隐藏异构，14 信号，check.py 内联，永不进 SUT）：
  - 芯片名 u_chip（非 dram_tester_chip）、FE_OFN33/201、CCOPT ccl_buf/ccl_cts/ccl_inv（非只 ccl_inv）、GPIO_42
  - **故意混入** rtl_signal: data_valid / state_q / 顶层端口 CRESET_N / REF_CLK → 触发 `fsdb_dump_misconfig_with_rtl_signals_missing` 分支（A 走不到）
  - 全 7 类各覆盖：fanout=2/macro_pin=1/cts=3/rtl_signal=4/cell_internal_pin=2(.Q/.Z)/pv_cell=1/preserved_buffer=1
  - 反硬编码 A 字面量: FE_OFN1451 / ccl_inv_32564 / GPIO_15 / dram_tester_chip

## 六、check.py 15 条独立断言 (a-o)，k_check==k_rationale==15
a 脚本非空可编译 ②[b]exit0+JSON+5键 ③[b]14信号+字段 ④[b]FE_OFN→fanout ⑤[b]CCOPT→cts ⑥[b]macro_pin_buf→macro_pin ⑦[b]dont_touch buf→preserved ⑧[b]uvt_pvcell→pv_cell ⑨[b].Q/.Z→cell_internal_pin ⑩[b]顶层端口+rtl→rtl_signal ⑪[b]root_causes≥2含misconfig ⑫[b]verdict含misconfig ⑬反硬编码A(无A字面量+含GPIO_42) ⑭空输入→no_signals ⑮3-seed sha256稳定

## 七、自验结果 (r725)
- reference_submit.zip → check PASS (15/15)
- 4 negatives 全 FAIL@各自首失败断言: neg_empty→a / neg_print_expected→c(5≠14) / neg_core_deleted→d(FE_OFN漏判) / neg_no_pin_classify→i(cell_pin=0)
- §4.9 三假提交 (empty-shell / print-expected / core-deleted) 全 FAIL
- e2e (从 case JSON 提取 test 跑) ref PASS + 4 neg FAIL
- build_jsonl.py --check: cases/A 372, total 1709
