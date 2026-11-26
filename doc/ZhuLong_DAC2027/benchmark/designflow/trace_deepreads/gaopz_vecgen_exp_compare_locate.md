# Deepread: gaopz — vecgen_drexp exp值 compare 定位 (C-A code-search/analysis-Q&A, digital)

**Session**: 1794446207194_gaopz · user=ericw · host=hfhds201 (10.129.32.75, .75 本机可读)
**mc**: 90 · domain: digital · agent: lead · msgs: 41 · size: 526KB
**Trace source**: real cline session, A-domain (digital/verification SV testbench comprehension)
**旧判定**: r503 parked "single Q&A analysis" (旧 weak 筛子) → **11-15 新标准: analysis-Q&A 合法, 复活**
**r683 状态**: claimed (reaudit revive), DEBT 1 合成未交付 (时间预算耗尽), 下轮 r684 合成

## 用户原话 (trace-verbatim)

- **U#0**: `/proj/drexp/V0/setup/sim/sim_vector/verilog.ddr5.drexp.0716/vecgen_drexp` 这里面有关与激励 exp值 compare相关的东西吗
- (全程仅此 1 条实质 user turn; 后续无追加)

## 核心意图

用户指着 `vecgen_drexp` 这个路径, 问里面有没有跟"激励 exp 值 compare (期望值比较)"相关的东西。
这是一个 **code-search / analysis-Q&A**: 在 DDR5 DRExp 仿真向量生成项目目录里, 定位 exp (期望值) 比较逻辑的位置与机制。

## 核心事实 (agent msg#40 最终回答, trace-verbatim 引用真实代码)

### 1. vecgen_drexp 是什么
- `vecgen_drexp` 是一个 **Perl 脚本** (可执行文件), **不是目录**; 是 dr_exp 项目的激励向量生成工具, 读 `.cfg` 配置文件生成仿真向量。
- **vecgen_drexp 本身与 exp 值比较逻辑无关** — 只负责调度仿真任务、生成 regression 运行文件和矢量文件, 不做信号级 exp 期望值比较。

### 2. exp 值 compare 逻辑在哪 — SystemVerilog 仿真代码

#### 2a. exp_TDQ / exp_configout 信号定义与赋值 — `ddr5_test.sv`
- 信号定义 (第 37-38 行):
  ```systemverilog
  wire[TDQ_NUM-1:0] exp_TDQ;
  wire exp_configout;
  ```
- 连续赋值 (第 264-265 行):
  ```systemverilog
  assign exp_TDQ = drexp_exp_tmp;
  assign exp_configout = configout_exp_tmp;
  ```
- `drexp_exp_tmp` 生成逻辑 — Read 任务 (第 750 行起): 从 `drexp_mem_arr[current_row]` 反向取数据, 带延迟赋值生成期望值; 支持 FOURBG (12-bit TDQ) 与标准 3-bit TDQ; 支持 ADDX 编译选项 (有效数据前加 'x)。
- `configout_exp_tmp` 生成 — 三个 FIFO 任务:
  - `FIFO_IN_RA` (第 354 行): 写 Row Address 时回放 RA FIFO → ConfigOut 期望值
  - `FIFO_IN_DATA` (第 479 行): 写 Data 时回放数据 FIFO → ConfigOut 期望值
  - `FIFO_IN_MR` (第 583 行): 写 Mode Register 时回放 MR FIFO → ConfigOut 期望值
  - FIFO 流水线: `fifo_*_q_2 → _q_3 → _q_1 → _q_0`, 带延迟参数 + ADDX 支持

#### 2b. compare_tasks.sv — 真正的 compare 核心
- `tdq_genexp` 赋值 (第 234-249 行):
  ```systemverilog
  assign tdq_genexp[0] = (tdq_compare_en) ? exp_TDQ[0] : 1'bz;
  // ... TDQ_NUM 个 bit
  assign config_genexp = (config_compare_en) ? exp_configout : 1'bz;
  ```
- buf 比较器 (第 267-292 行): `buf #(tdq_compare.tolerance)` 延迟比较 `tdq_genexp` vs `dut_compare_data` (来自 PDRIVER.TDQ) → `tdq_err[]`; 同时比较 `config_genexp` vs `dut_compare_config` → `config_err`
  ```systemverilog
  buf #(tdq_compare.tolerance) (tdq_err[0], (tdq_genexp[0] === 'z)? 1'b0 :
       (((tdq_genexp[0]===dut_compare_data[0])?1'b0:1'b1) & tdq_compare.compareflag & tdq_compare_en));
  ```
- 错误报告 (第 303-319 行): `always @(tdq_err)` / `always @(config_err)` 打印 DUT vs Exp 差异, 累加 `err_cnt`
- compare 控制任务 (第 1-120 行): `compare_set_default` / `compare_set_ignorebit` / `compare_set_ignoreval` / `compare_set_tolerance` / `compare_enable` / `compare_disable`
- Pattern 结果统计 (第 122-161 行): 据 err_cnt 判断 pattern pass/fail

#### 2c. ddr5_genvector.sv — 模拟向量生成
- `analogvec_gen` 任务: `exp_TDQ[2:0]` 和 `exp_configout` 列为 stimulus.vec / vec.text / stimulus.list 输出信号
- 信号列表索引: 9-11 = `exp_TDQ<2:0>`, 12 = `exp_configout`
- 仿真时 `$fmonitor` 将 exp 信号值写入向量文件, 供 FineSim 后处理比较

### 3. 总结表
| 组件 | 位置 | 作用 |
|---|---|---|
| vecgen_drexp (Perl) | 根目录 | 调度仿真任务、生成回归, **不做 exp 比较** |
| exp_TDQ / exp_configout 生成 | ddr5_test.sv Read + 3 FIFO 任务 | 据写入数据/地址/MR 生成期望输出值 |
| compare 比较逻辑 | compare_tasks.sv | `buf #tolerance` 延迟比较 exp vs DUT, 累加错误 |
| 模拟向量输出 | ddr5_genvector.sv | exp 信号输出到 .vec 文件供 FineSim |

**结论**: vecgen_drexp 本身不涉及 exp 值 compare, 但全套 exp 值比较逻辑存在于同目录下 ddr5_test.sv + compare_tasks.sv 中; vecgen_drexp 调 vsim 跑仿真, 仿真过程执行这些 compare 逻辑。

## 关键文件清单 (A档 assets 候选, 从 trace read_files 结果抽取)
- `vecgen_drexp` — Perl 脚本 (向量生成调度, 非 compare)
- `compare_tasks.sv` — compare 核心 (tdq_genexp/buf 比较器/err_cnt/控制任务/pattern 统计)
- `ddr5_test.sv` — exp_TDQ/exp_configout 定义+赋值+Read/FIFO 任务生成期望值
- `ddr5_genvector.sv` — analogvec_gen exp 信号向量输出
- `ddr5_tasks.sv`, `proj_special.sv`, `ddr5_package.sv`, `ddr5_specdef.sv`, `ddr5_interface.sv` — 配套
- `config`, `vec_perbank_100.cfg`, `vec_perbank_100.cfg_Q2` — 配置

## 合成计划 (r684 兑现)

**Case ID**: VecgenExpCompareLocate-001
**Mode**: C-A code-search/analysis-Q&A (digital)
**用户原话**: trace-faithful A 档 (U#0 原文)
**交付**: `analyze_vecgen_exp_compare(proj_root)` → JSON report
**A档 assets**: mini 项目 (vecgen_drexp Perl + compare_tasks.sv + ddr5_test_exp_excerpt.sv + ddr5_genvector_vec_excerpt.sv + config), trace-quoted 代码
**B隐藏变体**: ≥10 维全异 (exp_TDQ→exp_DQX, drexp_exp_tmp→drexp_dqx_tmp, compare_tasks→chk_tasks, tdq_genexp→dqx_genexp, buf 比较器→delay 比较器, FIFO_IN_RA→FIFO_IN_ROWADDR, tolerance→margin, err_cnt→mis_cnt, FOURBG→BGX4, vec 索引 9-11→7-9 等)
**check**: ≥10 条 a-j
  - a: vecgen_drexp 识别为 Perl 脚本 (非 compare 逻辑)
  - b: exp 期望值信号名正确 (B: exp_DQX/exp_cfgout)
  - c: exp 信号定义文件定位 (B: ddr5_test.sv → tb_top.sv)
  - d: 连续赋值 exp <- *_tmp 寄存器
  - e: compare 核心文件定位 (B: compare_tasks.sv → chk_tasks.sv)
  - f: buf/delay 比较器机制 (tolerance/margin 延迟比较 exp vs dut)
  - g: 3 个 FIFO 任务生成 configout 期望值
  - h: 错误累加机制 (err_cnt/mis_cnt)
  - i: 向量输出索引 (B: 9-11 → 7-9)
  - j: B-judge-selfcheck (隐藏 B 内嵌 _parse, 命名全异 anti-hardcode)
  + evidence-verification + 3-seed
**negatives**: neg_naive (空 report), neg_wrong (硬编码 A 命名, B 拦截), neg_stub (长度不足) — 全 FAIL
**§4.9 三假**: empty_shell / print_expected / core_deleted — 全 FAIL (anti-hardcode B 命名拦截)

## 备注
- 项目目录 /proj/drexp/... 在 .75 上 ericw 可读, e0031982 不可读 (PermissionError) → A档 assets 须从 trace tool_result 抽取 (read_files 结果), 不能直接 cp。
- read_files tool_result 结构: user msg 内 tool_result block, content 为 str, 需按 tool_use_id 配对 (msg14 read_files compare_tasks.sv 的 result 在后续 user msg)。
- r683 未完成抽取 (tool_use_id 配对脚本未跑通 + 时间预算耗尽), r684 需先修抽取脚本拿到 compare_tasks.sv / vecgen_drexp / ddr5_test.sv 真实内容再合成。
