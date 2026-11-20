# deepread: yrdts — SRAM UVM code-review (审查代码找bug)

- **session**: 1792060840051_yrdts.messages.json
- **user/host**: shanliny @ 10.129.2.10 (mc=57, verification)
- **trace size**: 6.1MB / 258 msgs (129 user / 129 assistant, 115 tool_use / 115 tool_result)
- **agent**: lead (deepseek-v4-flash)
- **selected by**: parked_reaudit_A REVIVABLE_QA queue (旧筛子判 code-review Q&A weak → 11-15 新标准合法)

## 用户意图 (verbatim)

- U#0: `这是一个形似uvm的sram验证sv脚本` + 10 SV 附件 (driver.sv / env.sv / interface.sv /
  monitor.sv / package.sv / transaction_base.sv / transaction_ext.sv / strategy_base.sv /
  strategy_ext.sv / top.sv)。附件位于 `/home/shanliny/.cline/data/sessions/1791974855202_32935/uploads/`
- agent ask_question 给 6 选项, 用户选 `审查代码并找出潜在问题或bug` (msg4 tool_result)
- 这是 code-comprehension / code-review Q&A: 用户给一个类 UVM 的 SRAM 验证 SV 项目, 要 agent
  做代码审查找出 bug, 按严重程度分类。

## trace agent 行为

- msg5/msg7: read_files 读 11 个 SV 文件 (package/top/env/interface/transaction_base/
  transaction_ext/driver/monitor/strategy_base/strategy_ext + ref_model/scoreboard)
- msg9: 产出完整代码审查报告, 14 个 bug, 按严重度分 4 档 (🔴严重2 / 🔴重要3 / 🟡中等3 / 🟢轻微6):
  - Bug1 (severe) monitor.sv L278-284: `ifdef TIMING_VALIDATION 路径用 `ref_model` 但
    sram_monitor 类只有 vif/scb, 无 ref_model 成员 → 编译报错
  - Bug2 (severe) transaction_ext.sv: 多个事务类约束 `test=='1` 但 execute 驱 `test<=1'b0`
    (write_transaction/bitwrite_transaction/column_redundancy_transaction)
  - Bug3 (important) top.sv L114-116 + L150: `dut_bwen` 两个 assign (ifdef BITWRITE + 无条件)
  - Bug4 (important) transaction_base.sv L108: `virtual virtual function` 重复 virtual
  - Bug5 (important) strategy_ext.sv L49-51: random_strategy::get_data_pattern() 空函数体无 return
  - Bug6 (medium) transaction_base.sv L73: 硬编 `top_tb.target_clk_half_period_init`
  - Bug7 (medium) strategy_ext.sv: march_c_bitwrite_strategy 只测地址 0
  - Bug8 (medium) interface.sv: vec_cb/mon_cb 多 clocking block output 同信号
  - Bug9 (minor) package.sv: sram_testchip_pkg 定义但从未 import
  - Bug10 (minor) transaction_base.sv L65-66: $floor 返回 real 赋 parameter 类型不匹配
  - Bug11 (minor) strategy_base.sv L86: addr 声明 int(有符号) 与 bit 向量混用
  - Bug12 (minor) driver.sv L100: `if (op.name == "COLUMN REDUNDANCY")` 字符串名匹配
  - Bug13 (minor) ref_model.sv: sram_testmode_ref_model 未覆写 write/read
  - Bug14 (minor) strategy_base.sv L69: 硬编 `top_tb.target_clk_half_period`

- 后续 U#2 (msg10) `中等乃至以上bug，除了bug5、7、8，全部修复` → 进入修复阶段
- U#4-U#14 (msg74-238): 转 timing-validation Q_ref 半周期 (下降沿→应上升沿) + monitor
  对比相同波形报错 (流水线挪位) + driver.sv target_clk_half_period MFNF 报错调试
  → **执行子片, 本 case 取首段 code-review 子片**

## 子片选取 (11-15 双意图拆分 taxon)

- **造**: 首段 code-review (msg0-msg9) = 静态审查产出 bug 报告, 可写有牙 check
- **剔除**: 后续 timing-validation/monitor 流水线修复子片 = 需 VCD/log 运行证据, 双意图拆分

## A 档不可行性

- 原始 trace SV 文件经 read_files 工具返回, 带 ` N | content` 行号前缀, 需清洗
- 10 文件共 ~130KB, 含专有 SRAM 验证 IP (LPDDR5-style 验证环境)
- 项目原始路径 `/rundata/drgsa/...` 远程 NFS, 沙盒 ssh 走 e0031982 身份可达但文件已蒸发/巨大
- → B 档合成 mini sram_tb_proj/ (6 文件 ~80 行) 忠实还原 8 类 bug + 项目结构

## B 档合成 (sram_tb_proj/ A + sram_tb_v2/ 隐藏 B)

8 类 bug (与 trace agent 报告同类型, 不同具体值):
| # | category | A (trace-faithful) | B (hidden variant) |
|---|---|---|---|
| 1 | undefined_handle_in_ifdef | monitor.sv `ref_model` in `ifdef TIMING_VALIDATION | monitor.sv `score_ref` in `ifdef VERIFY_PATH |
| 2 | constraint_drive_mismatch | transaction.sv `test==1'b1` vs `test<=1'b0 | transaction.sv `mode==1'b1` vs `mode<=1'b0 |
| 3 | multi_driver_assign | top.sv `dut_bwen` 两 assign | top.sv `dut_cen` 两 assign |
| 4 | duplicate_virtual_keyword | transaction.sv `virtual virtual function | transaction.sv `virtual virtual task |
| 5 | empty_function_body | driver.sv get_default_data() 空 | driver.sv get_init_data() 空 |
| 6 | hardcoded_hierarchical_ref | transaction.sv `top_tb.target_clk_half_period_init | transaction.sv `tb_top.clk_period_init |
| 7 | unused_package | sram_pkg.sv sram_testchip_pkg 未 import | sram_pkg.sv sram_aux_pkg 未 import |
| 8 | string_name_match | driver.sv `op.name == "WRITE" | driver.sv `op.name == "READ" |

A vs B ≥8 维全异 (ident/信号/ifdef 宏/函数vs task/hier 名/pkg 名/字符串/文件内容) → anti-hardcode 牙齿

## 交付与判分

- 交付: sram_tb_review_report.json (含 analyze_sram_tb_fn 通用代码分析函数源码 + bugs_found_on_input)
- check 12 条 a-l: 结构+遍历+re / B 上 8-12 bug 且 8 类别全覆盖 / 字段合法 / 行号证据真实 /
  反硬编(A 标识符不字面量化) / B 分析证明(score_ref+dut_cen, 非 ref_model) / 3-seed 确定性 /
  severe+minor 分布 / bugs_found_on_input 非空 / A 上 8 类别 / 无重复三元组 / 描述非套话
- k_rationale = k_check = 12 ≥ 8
- 自验: ref 12/12 PASS + 3 neg (empty/naive-hardcoded-A/wrong-facts) 全 FAIL distinct +
  §4.9 三假 (空壳/print-only/删核心) 全 FAIL + e2e jsonl test 字段独立跑 PASS + negative_selftest PASS
