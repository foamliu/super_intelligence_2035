# 深读笔记 — as67p (waveform 域, mc=786, waveform 扩量#2 → WaveView-002 L2)

**trace**: `1793147699495_as67p` · user `easont` · host `hfhds211`(10.129.32.85)/`hfhds208`/`hfhds207`/`hfeg0plg102`/`hfeg0pkn004`/`hfeg0pfn136` · 2026-10 · model deepseek-v4-pro-cloud · 496 msgs(268 user/228 assistant) · 13 substantive user msgs.

**真实任务**：easont 做 LPDDR5 DDGOA `TempHalfWL` 温度传感器混合信号 cosim（FineSim SPICE + VCS Verilog），仿真产生 `finesim.fsdb`(9131 探测信号) + `verilog.fsdb`(数字 A2D)。用自建 skill `waveview-fsdb-readerV2-2`（Synopsys WaveView ACE Tcl 后端 `wv -ace_no_gui`，比 fscript 快 ~16x）从 FSDB 按层次信号名逐个读波形 → 自动判数字/模拟 → 数字做边沿/脉冲/电平时长/上升下降沿(25↔75%)，模拟做过零+统计 → 结合 `netlist_AI` 网表说明模块功能 + 迭代优化网表（agent 反复出错，最终结论 netlist_AI 正确，仅删未用 std cell 定义）。

**13 substantive user msgs（阶段）**：
- A(msg0/8/17): 读 FSDB / 问 FSDB MCP / 用 skill 读 FSDB 说明信号功能
- B(msg63): 读 netlist_AI + FSDB 说明模块功能
- C(msg97/204/234/278): 分析/优化/迭代 netlist（agent 多次生成错误结构，用户纠正"结构参考 netlist_AI"）
- D(msg383): 对比修改后 vs 原网表生成 markdown 报告
- E(msg392/401/412): 分析 cosim 文件夹流程 / 重复分析 FSDB markdown 输出

**关键 agent 流程**：`run_approved_command`(python-runner) 调 `waveview-fsdb-readerV2-2.py <fsdb> "<signals>" <step> <t_start> <t_end>` → skill 内部生成 `wv_s_<ts>.tcl`（用 `sx_signal {v(signame)}`）→ `wv -ace_no_gui` 跑 Tcl → 导出 `wv_o_<ts>.tbl` → Python 解析 → 分析报告。

**踩坑（agent 真踩）**：
1. 信号名格式：先试 `v(top.temp<0>)` not found → 再试 `top.temp<0>` not found → 最终从 `wv_tmp/wv_s_8131.tcl` 旧文件发现 FineSim FSDB 顶层信号用**裸名** `v(temp<0>)`/`v(sel32to35)`（无 `top.` scope 前缀）才成功。
2. `sx_signal` 对不存在信号返回空句柄但不抛错；后续 `sx_wave_is_logic`/`sx_wave_to_list` 在空句柄上报 "argument type error" —— 必须先判 `string length $h == 0`。
3. `sx_signal` 多参数静默丢弃不存在的信号（底层逐个拿 handle，空 handle 跳过）。
4. bsub 队列偶尔空返回（FSDB 读取抖动）。

**WaveView ACE Tcl API（实测可用，.75 沙盒 `/apps/synopsys/SRB/wv/T-2022.06-SP1/bin/wv`）**：
- `sx_open_sim_file_read <fsdb>` 打开 FSDB
- `sx_signal <name>` 取句柄；不存在返回空字符串
- `sx_wave_is_logic <h>` → 1=数字逻辑；`sx_wave_is_analog <h>` → 1=模拟
- `sx_number_of_bits <h>` → 位宽(1 或 8)
- `sx_wave_to_list <h>` → 值序列 Tcl list（数字: `0`/`1`/`X`/`Z`/`U`；bus: 8 字符串如 `00000000`/`xxxxxxxx`，**不含时间戳**）
- `sx_dump_hier [sx_current_sim_file] <outfile>` → dump scope 树（只列 scope 不列信号）
- `sx_exit` 退出

**demo FSDB 探明（.75 上，用于 A/B）**：
- `mixed/mixed.fsdb`（system scope，22 子 scope）：`clock`(logic,1bit,297 samp,`U 0 1 0 1...`)、`reset`(logic,1bit,6 samp)、`data`(logic,**8bit** bus,118 samp,`UUUUUUUU XXXXXXXX 00000000 ZZZZZZZZ...`)、`system/i_pram/addr`(8bit,122)、`system/i_CPU/i_ALUB/i_alu/a`(8bit,109)、`system/i_CPU/i_ALUB/i_alu/b`(8bit,19)。顶层信号裸名或 `system.<sig>` 都可；`v()` 包装**不行**（Verilog FSDB 非 SPICE）。
- `power/cpf_demo/demo.fsdb`（同 system 设计，power-aware sim，**值/采样数不同**）：`clock`(247 samp,`X 0 1...`)、`reset`**MISSING**、`data`(36 samp,小写 `xxxxxxxx`)、`i_pram/addr`(37)、`i_alu/a`(42)、`i_alu/b`(14)。→ 用作隐藏 B。
- `hwsw_debug/multi_core/design.fsdb`(`execution_tb` scope，不同设计)：仅 `execution_tb.clk`(logic,1bit,134302 samp) 可访问，其余 missing。
- `dumper/modelsim_link_third_party/sample.fsdb`(`top` scope，简单)。

**WaveView ACE 稳定性坑（重要）**：`wv -ace_no_gui` 在单进程内**连续调用 ≥5 次**会 internal error S01 crash（`sx_crash.sx` saved），即使每次 fresh tmp subdir + `HOME=sub` 隔离也无效。→ check.py 设计为**3 次** wv 调用（1 固定序 + 2 随机种子打乱），且 ground truth **硬编码**（不跑 reference wv），避开崩溃阈值。

**合成 case（WaveView-002，waveform 扩量#2，L2 真跑 wv -ace_no_gui）**：
- deliverable = `outputs/submit.zip` 含一个 ASCII `.tcl`：从 `FSDB_PATH`/`SIGNALS_FILE` env 读输入，对每个信号打印 `SIG|name|type|bits|nsamples|ntransitions|histogram`。
- asset A（SUT 见）：`signals_A.txt`(mixed.fsdb 6 信号含 1 missing) + `task_brief.md`(真实场景+API+输出格式+隐藏泛化+8 错解)。
- 隐藏 B（assets/hidden/，不进 SUT）：`power/cpf_demo/demo.fsdb` + 6 信号(reset MISSING, NOPE_FAKE_X9 unknown) + 不同采样数/值/missing 集 → check.py 自包含 embeds ground truth(type/bits/nsamp/ntrans/hist 全硬编码)。
- check.py 12 条件 (a-l)：zip+ASCII / wv exit0+SIG 行 / 每信号有行 / type 分类 / bits / nsamples / ntransitions / histogram / missing 不伪造 / unknown 不崩溃 / hist 之和==nsamp / 3 序(order-invariant)逐信号一致且==ground truth。
- 自验(.75 真跑)：reference→CHECK_RESULT=True(12/12 PASS)；§4.9 三假全 FAIL(empty→a / print_expected→c 缺 NOPE / core_deleted→d reset type logic!=missing)；2 naive 全 FAIL(always_logic→d / nsamp_only→e data bits 1!=8)。
- **pi 实跑本轮预算不足未跑，pending 下轮补。**

**§5 难度**：本条 **L2**（真跑 WaveView ACE subprocess on 隐藏 FSDB B），补强 L2 占比。trace_ledger as67p→case(17 covered, waveform×2)。
