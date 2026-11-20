# 深读 1793256477242_dlrpg — e0039602 @ hfeg0plg103 (mc=194)

- session: `1793256477242_dlrpg.messages.json` (lead agent, 167 msgs / ~970KB)
- 项目: `verilog_lib_trans` 网表→行为级 Verilog 转换项目, `/home/e0039602/Documents/verilog_lib_trans_v1.3/`
- 工具关键词: verilog:424 / netlist:242 / drc:16 / pyaether:8（首条 user msg 上下文）；session 偏网表/Verilog 转换 + 功能校验脚本开发
- 用户首轮: 「请阅读这个目录下的项目，他主要是做一个网表转换为仿真可以看懂的行为级模型的任务，现在我想知道他每次生成完代码之后，有哪些检查措施辅助检查防止出错」
- 性质: **clean single-produce**（U#30 起明确要求把真值表自仿真 logic_check 换成「大模型写布尔表达式 + Python 全枚举对拍」），核心产物 = 新建 `src/expr_check.py`（13 段 editor 编辑，从 0 到 16KB）
- 核心产物 `expr_check.py` 关键组件（replay msg#45-#62,111 重构验证 13/13 单测过）：
  - **安全布尔求值器**（无 eval）：`_tokenize`（id/num/`1'b0`/`&|^~()`）+ 递归下降 `_parse_or>_parse_xor>_parse_and>_parse_unary>_parse_primary`，优先级 `~>&>^>|`；`eval_bool(expr, ctx, derived)` 入口
  - **`_idval`**：标识符取值，ctx 命中→取，否则按 DERIVED 递归代入（msg#111 修 `_eval_expr`→`eval_bool` 笔误）
  - **`parse_expr_output`**：解析 LLM 固定格式输出 `INDEP:/DERIVED:/EXPR <out>=.../SKIP` → dict；缺 EXPR / 缺 INDEP+DERIVED → ok=False
  - **`_independent_set(orig, conv)`**：两侧 INDEP 并集 − DERIVED 的 LHS − 电源常量(`_POWER_CTX` vcc/vss/vdd/gnd/vbn/vbp/inh_*) → 排序后的真正独立变量 + merged derived map
  - **`compare_pair(orig, conv, max_indep=10)`**：全枚举对拍核心；`itertools.product([0,1], repeat=len(indep))`，每赋值 ctx=电源常量∪赋值，求两侧共同输出(`set & set`)的 0/1，收集 mismatch；>max_indep → `too_many_inputs` 跳过；任一侧 SKIP → 跳过；None 行跳过
  - **`build_orig/conv/repair_prompt`** + `generate_expression` + `run_batch_expression_check`：LLM 驱动 + 不一致回喂修复（这部分依赖大模型 API，不进 synthesized case）
- 关键正确点（用户在 U#30 反复强调）：
  1. **互补对处理**：S/SN 且 SN=~S → 只枚举 S，SN 按 DERIVED 回填，绝不把 S、SN 都当独立变量同时赋不同值（msg#55 误删 `build_conv_expr_prompt`，msg#57-#60 read_files 查看 + 重插恢复）
  2. **Z/X 不在输出侧跳过，而在输入侧消除**：靠 INDEP/DERIVED 保证喂进去的都是合法输入，输出应是确定 0/1，无需「跳过 Z/X 行」
  3. **独立变量 > 上限跳过**（默认 10），不比对
  4. **只比对两侧共同输出名**（`set(orig.exprs) & set(conv.exprs)`）
  5. **时序/三态 module → 整模块 SKIP**，不写表达式
- 集成编辑（msg#63-#73+）：parallel_worker.py 删 `logic_check` import + 删 cell-def 库构建 + 改 `_validate_all` 签名 + 改 3 处 caller；test/test_expr_check.py 13 单测覆盖 eval_bool/parse/compare_pair 互补对/SKIP/too_many/prompt
- 环境踩坑：editor 单次 new_text 6000 字符上限（msg#45 12479 chars FAIL → msg#47 分段创建 2092 chars）；msg#53 6833 chars FAIL → msg#55 分两次
- 取用: **B-grade synthesized** — 取其「安全布尔求值 + INDEP/DERIVED 全枚举对拍」确定性核心，剥离 LLM 驱动/EDA 运行时依赖，合成 spec-driven **布尔逻辑等价对拍 CLI** case（EDA-Eval-DesignFlow-ExprLogicCheck-001，schematic_netlist，L2，k=13）。SUT 产 `expr_logic_check.py`：读两份 MODULE/INDEP/DERIVED/EXPR 描述 → 排序全枚举 + DERIVED 递归代入 → 字节固定 MISMATCH/MATCH/SKIP 报告。可见 A(2:1 mux mx2cs_a1mux, SEL/SELN 互补, 两侧等价→MATCH) vs 隐藏 B(AND-OR-Invert aoi2_b7gate, PB/QB/RB+QBN=~QB, 转换 zout_a 用 qbn_sig 替 qb_in 致极性 bug→MISMATCH 2 行) — A/B 模块/信号/输出名完全不相交反硬编码。check.py 内嵌**独立 oracle**(shunting-yard RPN 求值器，与 reference 递归下降结构不同)重推导 B 不一致集 + 逐行复核每条 mismatch 真实性 + 13 条件 a-m + 6 negative(empty/header_only/hardcode_A/hardcode_B/ignore_derived/uses_eval)全 FAIL。
- 选取原因: mc≥30 fresh D-pool 已耗尽，降到 mc≥10 + 宽 D 关键词(netlist/schematic/analog/waveview/hspice/spectre/cdl/pex/synopsys/verilog/spice) → 799 cand → 31 fresh after 4-shard ledger 排除；dlrpg(mc=194, verilog:424/netlist:242, 干净 single-produce 布尔对拍器, 低 drc:16)为最强 D-domain produce 候选。reject 2izm6(doc/report 写作) + xinm9(只读 sim-log 分析, 无 produce)。
