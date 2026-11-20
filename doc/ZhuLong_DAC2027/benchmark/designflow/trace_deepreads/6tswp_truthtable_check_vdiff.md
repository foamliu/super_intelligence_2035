# Deepread: 6tswp — verilog_lib_trans v1.4.1 vs v1.4 真值表检查 version-diff

**session**: `1793343472817_6tswp` (messages.json, 682969 B / 51 msgs)
**user/host**: e0039602 @ hfeg0plg95 (DRAM drcoa 团队) — A-domain **digital**
**scan mc**: 119 (summary_1115_081559.tsv; keywords verilog:587/netlist:366/drc:30/transistor:20)
**trace fetched**: r679 via eda_flow SSH (.75→hfeg0plg95, SSH **restored** this round — 见 MEMORY r678 infra-block 已解除)
**agent**: lead (cline), policy-engine enforcing, run_approved_command (python-runner profile)
**status**: failed (agent 自清理临时脚本后给结论, 但 session 标 failed)
**ledger**: r679 mark → deepread (synth DEBT 下轮兑现)

## 用户意图（原话, 2 turn, 均无附件, 纯项目内文件 Q&A）

- **U#0 (msg[0])**: `<user_input mode="act">请你阅读这个项目，你当前的版本应该是1.4.1，然后告诉我这个项目里真值表检查的原理，并和1.4版本当中的对比，告诉我这两者的这部分有什么区别，1.4在documents目录下</user_input>`
  → 读 verilog_lib_trans_v1.4.1 项目, 讲真值表检查原理, 与 v1.4 (在 Documents 目录下) 对比差异.
- **U#37 (msg[37])**: `<user_input mode="act">请你解释一下当前版本的整体工作原理</user_input>`
  → 解释 v1.4.1 整体工作原理.

**任务形态**: version-diff + code-comprehension Q&A (analysis-Q&A). 真实交付 = 一份对比报告 + 一份整体原理说明. 合法任务 (11-15 新标准: analysis-Q&A/doc-search/code-comprehension 全合法).

## 项目结构（trace 实读, agent list_allowed_files + read_files 还原）

```
/home/e0039602/Documents/
├── verilog_lib_trans_v1.4/          # 旧版
│   ├── _verify_models.py
│   ├── src/{__init__.py, logic_check.py(17876B), run.py, parallel_worker.py, rules_engine.py, ...}
│   └── test/_del.py                 # 标记 logic_check "废弃待删"
└── verilog_lib_trans_v1.4.1/        # 当前版
    ├── README.md, config.yaml, run.py
    ├── _verify_models.py
    ├── src/{__init__.py, logic_check.py(17876B, 与1.4逐字节相同), expr_check.py(新增),
    │        parallel_worker.py, rules_engine.py, rules_prompt.py, rules_prompt02.py,
    │        agent_client.py, output_validator.py, port_check.py, xrun_check.py,
    │        netlist_parser.py, simlib_lookup.py, simlib_ref_db.py, llm_parser.py,
    │        report_writer.py, logging_util.py}
    └── docs/{adjustment_netlist_to_sv.md, ...}
```

## agent 工具链

list_allowed_files (depth 3) → list_allowed_files docs/src/./父目录 → read_files README.md → search_codebase (truth.?table|真值表|func_truth|truthtable) → list_allowed_files v1.4 → read_files 两版 logic_check.py + run.py → search_codebase (logic_check|check_conversion|expr_check) → editor 创建 _compare_versions.py → run_approved_command (diff: logic_check.py identical? YES, 两版均 17876B) → read_files parallel_worker.py 两版 + expr_check.py 中段 → read_files expr_check.py 178-245 (compare_pair/_independent_set) + logic_check.py eval_direct → 清理临时脚本 → 结论. Turn2: read_files run.py(全)+config.yaml+rules_engine+agent_client+output_validator+port_check+xrun_check+rules_prompt*+simlib_* → 整体原理.

## 真实根因 / 事实结论（深读复核, 与 agent 结论一致）

**核心事实**: `src/logic_check.py` 在 1.4 与 1.4.1 **字节级完全一致 (均 17876 B)**. 真正区别 = **校验策略被换掉**:

| 维度 | 1.4 (logic_check 真值表自仿真) | 1.4.1 (expr_check 布尔表达式对拍) |
|---|---|---|
| 代码文件 | src/logic_check.py (1.4.1 同名文件仍在但**不被主流程使用**) | src/expr_check.py (新增) |
| 是否用 LLM | **否**, 纯 Python 确定性网表仿真器 | **是**, LLM 逐个读原/转网表各输出布尔表达式 (每 module 2 次) |
| ground truth | 直接仿真**原始晶体管网表本身** (管子按导通并节点, 电源钉死) | 大模型对原网表的**布尔表达式理解** |
| 运行时机 | 转换**过程中**每个 module 转完立刻内联校验 (parallel_worker.run_module) | **所有转换完成后**独立批量后置 (run.py:655, report 落盘后, 批量 xrun 前) |
| 适用门槛 | 仅单输出; 输入 1~8; 纯组合 (关键词扫描) | 多输出也行; 独立变量 ≤10; 任一侧不 SKIP |
| 互补输入(S/SN) | 不特殊处理, 所有输入脚当独立变量枚举 | INDEP/DERIVED 显式区分, 只对 INDEP 全枚举, DERIVED 回填, 杜绝非法组合 |
| 时序/三态跳过 | 关键词扫描放行 | LLM 输出 SKIP 放行 |
| 不一致修复 | 复用 C6 修复回路重生成 (≤2 轮) | 专门修复回路, 逐输入差异表回喂 LLM (≤2 轮) |
| 旧 logic_check 状态 | 主流程正式组件 | 留在仓库但废弃, 移出主流程 (parallel_worker 不再 import; test/_del.py 删它) |

**1.4 logic_check.check_conversion 机制**: module_io 只处理单输出+1≤输入≤8 纯组合; combinational() 关键词扫描 (trireg/notif/weak1/pull) 含三态/锁存放行; itertools.product([0,1]) 穷举; 每组合对原/转网表各跑 eval_direct; eval_direct = 最多 40 次迭代定点仿真器, 内建门(_pval) + 子模块递归 + 晶体管级 cell(ntn/ntk/nmos/ptn/ptk/pmos) eval_transistors 理想开关+并查集合并 D/S 节点+vcc/vss 钉死; 任一侧 None→放行不误杀; ov≠cv→(False, msg) 进 C6 修复. **零 LLM 纯确定性**.

**1.4.1 expr_check.run_batch_expression_check 机制**: 每 module 拆 2 个独立 LLM 表达式任务 (原网表/转网表各一); LLM 按固定格式 INDEP/DERIVED/EXPR 输出; parse_expr_output 纯解析不 exec; compare_pair: _independent_set 合并两侧 INDEP 剔除 DERIVED 左边+电源常量→独立主变量集; 独立变量>max_indep(10)→too_many_inputs 跳过; 任一侧 SKIP→放行; 全枚举+eval_bool 递归下降按 DERIVED 回填→收集 mismatch→修复回路. **设计思想: 把"读懂的难度"外包给大模型, 把"穷举比对"交给确定的 Python**.

**v1.4.1 整体工作原理 (turn2)**: 网表 cell 转换器, 把物理库不存在的缺失 cell 经机械规则+LLM 转成 simlib_base.sv 已有标准单元. run.py main: 解析参数/config→load_prompt_module (rules_prompt/rules_prompt02 可热插拔)→known_modules+SimlibRefDB 建索引→extract_missing (netlist_parser 字符级扫描, 失败降级 llm_parser)→block_list 过滤→module_blocks 分组→parallel_worker.run_module 8 线程: _build_prompt(静态 RULES+18 积木源码入 system role 命中 KV cache; 动态 module原文+参考示例+缺失cell JSON)→rules_engine.try_convert 机械快路径(inv*→inv_base, nand/nor/aoi/oai→表达式合并, 电源脚改名; cell-only 模式且全可机械→ok-mechanical 零LLM)→_generate_candidates 三候选并行→_judge_best 评审选最佳→_validate_all(_extract_approach 剥//LLM-APPROACH; normalize_declarations 网类型去重; validate module/endmodule配平+markdown围栏检测+vssz回归; port_check 端口名/方向)→C6 修复回路≤2轮→后置①expr_check 布尔对拍→后置②xrun_check 批量编译(ncvlog L1, 缺工具降级跳过)→result_map 报告+低置信度表.

## B 档合成计划（下轮兑现, case_id = TruthTblCheckVerDiff-001）

**为何 A 档不可行**: 项目在远程 hfeg0plg95:/home/e0039602/Documents/verilog_lib_trans_v1.4{,.1}/, 含完整 LLM 转换管线 + simlib 私有库, 不可在 .75 沙盒整体复现; 但可检测结构可 mini 还原.

**B 档 mini 项目** `verilog_lib_trans_proj/` (两子树 v14/ + v141/, 忠实还原可检测结构):
- `v14/src/logic_check.py` (mini: check_conversion + eval_direct + eval_transistors + _pval + combinational 关键词扫描 + module_io 单输出≤8输入门; 含 ntn/ptn 晶体管开关+并查集 _merge)
- `v14/src/parallel_worker.py` (mini: run_module 中 `import logic_check` + `_validate_all(..., cells)` 调 `logic_check.check_conversion(orig, conv, cells)` 内联)
- `v14/src/run.py` (mini: 不调 expr_check)
- `v14/test/_del.py` (无, 或不标废弃)
- `v141/src/logic_check.py` (与 v14 **逐字节相同** — 关键事实)
- `v141/src/expr_check.py` (mini: run_batch_expression_check + compare_pair + _independent_set + parse_expr_output + eval_bool; INDEP/DERIVED/EXPR 格式)
- `v141/src/parallel_worker.py` (mini: init_worker 注释"逻辑校验已改为布尔表达式对拍(expr_check), logic_check 已移除"; _validate_all 只做结构/端口校验, **不 import logic_check**)
- `v141/src/run.py` (mini: 转换后调 `expr_check.run_batch_expression_check(...)`, config expr_check.enabled)
- `v141/test/_del.py` (标记 logic_check "废弃待删")
- `v141/config.yaml` (expr_check.enabled: true, max_indep: 10)

**B 隐藏变体** `verilog_lib_trans_proj_B/` (base64 内联 check.py, 同结构但 ≥10 维全异, 保留"两版 logic_check 逐字节相同 + 1.4 内联自仿真 / 1.4.1 后置 expr_check + 互补输入 INDEP/DERIVED" 这 3 个可判事实):
- 项目名 verilog_lib_trans → netlist2sv_trans / 版本 v1.4/v1.4.1 → v2.0/v2.1 / logic_check → gate_sim / expr_check → bool_equiv / check_conversion → verify_gate / eval_direct → sim_gate / eval_transistors → sim_xstr / _pval → _gate_val / combinational → is_purecomb / parallel_worker → conv_worker / run_module → process_mod / _validate_all → _struct_check / run_batch_expression_check → run_bool_equiv_batch / compare_pair → cmp_pair / _independent_set → _free_vars / parse_expr_output → parse_bool / eval_bool → eval_expr / INDEP/DERIVED/EXPR → VARS/DERIVED/FORMULA / max_indep → max_free / ntn/ptn/nmos/pmos → NCH/PCH / vcc/vss → VDD/GND / 关键词 trireg/notif → latch/tribuf / C6 修复 → R1 修复 / ok-mechanical → ok-rule / _judge_best → _pick_best / _generate_candidates → _gen_candidates / timestamps+具体行号全异.

**交付**: `analyze_truthtable_check_diff(proj_dir)` 通用函数 — os.walk 两子树, 检测:
1. 两版 logic_check 等价文件 (按名找, byte-compare 或 normalized compare) 是否**逐字节相同** (hashlib.md5)
2. v14 parallel_worker 是否 import logic_check (re `import\s+logic_check`/`from.*logic_check`)
3. v14 _validate_all/run_module 是否**内联调** logic_check.check_conversion (re `logic_check\.check_conversion`/`check_conversion\(`)
4. v141 parallel_worker 是否**不** import logic_check (断言 not found)
5. v141 是否有 expr_check.py 且 run.py 调 run_batch_expression_check (re `expr_check\.run_batch`)
6. v141 test/_del.py 是否标记 logic_check 废弃/待删 (re `废弃|待删|delete|deprecated|logic_check`)
7. v141 config expr_check.enabled (yaml/正则)
8. v14 无 expr_check.py 或 run.py 不调 expr_check (断言旧版无新机制)
9. 机制判定: v14 mechanism = "self-sim/truth-table", v141 mechanism = "bool-expr/expr_check" (从命名+调用事实推断)
10. 互补输入处理: v141 expr_check 含 INDEP/DERIVED 区分 (re `INDEP|DERIVED` 或 _independent_set/_free_vars 函数)
→ 输出 `truthtable_check_diff_report.json` (含两版 mechanism/文件hash/import事实/调用事实/废弃标记/互补处理/anti-hardcode 证明字段).

**check ≥12 条** (a-l): (a) report 结构+函数执行返回 dict (b) 两版 logic_check hash 相等 (c) v14 import logic_check True (d) v14 内联 check_conversion 调用 True (e) v141 import logic_check False (f) v141 有 expr_check.py (g) v141 run.py 调 expr_check.run_batch (h) v141 _del.py 废弃标记 (i) v141 config expr_check.enabled (j) v14 无 expr_check 机制 (k) 互补输入 INDEP/DERIVED 在 v141 expr_check (l) anti-hardcode (B≠A ≥10 标识符) + 3-seed 确定性. k_check=k_rationale=12.

**negatives** (≥2): naive_hardcoded_A (直接 return 写死 A 的字符串, B 上 hash 相等等断言全错) / empty_stub (return {}) / wrong_facts (v141 import logic_check=True 等颠倒) → 全 FAIL. §4.9 三假 (empty-shell/print-expect/deleted-core) 全 FAIL. negative_selftest.

**自验**: ref 12/12 PASS + 3neg FAIL + §4.9 FAIL + e2e jsonl test-field 提取 PASS.

**trace_source metadata**: {user:"e0039602", host:"hfeg0plg95", session_file:"1793343472817_6tswp.messages.json", match_count:119, real_task_summary:"读 verilog_lib_trans v1.4.1, 讲真值表检查原理, 与 v1.4 对比差异; 再解释 v1.4.1 整体工作原理"}.

**预计下轮工作量**: ~25 min (B 档 mini 两子树 ~12 文件 + 隐藏变体 base64 + check 12 条 + negs + §4.9 + ref + e2e + 双仓提交). 单轮闭环可行.
