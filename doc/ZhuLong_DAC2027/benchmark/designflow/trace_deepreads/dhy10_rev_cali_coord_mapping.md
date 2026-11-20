# dhy10 — rev_cali 后端 (i_slew, c_slew, q_load) ↔ template_table 映射分析

## Trace 元数据
- session: `1794187969151_dhy10`
- user: `e0046686` @ `hfeg0pkn001`
- match_count: 8 / domain: spice_sim (characterization 边界)
- agent: lead / 335 msgs (175 user / 160 assistant) / 1.3MB / 305 substantive turns
- 工具调用: read_files×28, editor×92, run_approved_command×33, list_allowed_files×9, run_commands×1, search_codebase×1, SandBox_MCP×1
- 旧判 parked "rev_cali analysis-only no-produce 305msg" → **r707 reaudit 复活**（按 11-15 令 analysis-Q&A→produce 合法）

## 用户原始意图（verbatim，msg[0] + msg[148] + msg[165]）
- msg[0]: 「阅读并理解 TASK_REV_CALI_BACKEND.md 和 /home/e0046686/需求文档_rev_cali_backend.md，按需执行」
- msg[148]/msg[165]（实质任务，msg[165] 为完整版）:
  > 「反标的后端脚本中：lib_timing_tools 抽 timing 需要按照（i_slew，c_slew，q_load）的三维坐标形式传递，再去匹配 template table，然后抽值；传递索引和传递值均可，传递值的时候需要做插值，当前优先用索引传递，值传递时先保持精确匹配，插值算法后续再做；
  > 需要先做下 i，c，q 与 table 的关系梳理；一个三维坐标对应到某个 template table 时，只需要取三维坐标中的两个或者其中一个，且不同 template table 取的坐标或者坐标对可能不同；
  > 先梳理这个关系，再看怎么开发；参考 lib：/home/e0046686/new/tmp_scan_data/lib；/home/e0046686/new/ 下的同名工程 np/autosim_script 及 zk/cx_cm 工程，也有参考价值；」

**意图**：梳理 (i_slew, c_slew, q_load) 三维坐标到 liberty template_table 的映射关系——每类 table 取三维中的哪几个、变量顺序如何——产出结构化映射，为后续 extract_timing 的索引/值传递开发铺路。这是「analysis-Q&A → produce」型：产出结构化映射报告 + 解析器。

## Agent 关键分析发现（trace msg[172]-[294]，verbatim 摘录）
1. **msg[172]**: 「参考 lib 中 CONSTRAINT 模板是 `variable_1 = related_pin_transition`（CLK slew）、`variable_2 = constrained_pin_transition`（数据脚 slew）——与直觉顺序相反」
2. **msg[186]**: 「4 个 lib 的 template 全景已拿到，**关键发现**：模板库与 k 库的 CONSTRAINT 变量顺序**相反**（模板库 v1=related_pin_transition，k 库 v1=constrained_pin_transition），且存在使用 q_load 的表（CELL_DELAY/TRAN）」
3. **msg[202]**: 「k 库结构确认：约束表内联网格两维相同（1~500ps），Q 延迟表 index_2 是负载网格（0.001~80，需确认电容单位）」
4. **msg[208]**: 「当前 `select_value` 是**纯位置式**（coord[0]→index_1，coord[1]→index_2），无变量名感知——这正是两种 lib 风格坐标含义不一致的根源」
5. **msg[234]**: 「CLK_TRAN 内联 index_1 = constrained_pin_transition = **c_slew**；且 `compiler_config.py` 有 `get_i_c_slews_loads`（i/c slew 与 load 网格的权威定义）」
6. **msg[250]**: 「权威网格确认（cxn4s1p，ns）：i_slews=[0.05..0.35]、c_slews=[0.01..0.07]、loads=[0.02..0.14]，与 lib 模板 index 完全对应」
7. **msg[258]**: 「np 工程的 lib_timing_tools 与我们的一致（无 lib2parm，已被 V2 取代）。潜在存量 bug：真实 k 库的 `mpw_template_7x0` 模板声明了 index_2（占位 0..6），而表块只有内联 index_1——`extract_table` 会把模板占位 index_2 合并进来导致 1D 表被误判为 2D」
8. **msg[270]**: 「模板库 (3,3) 实测：clkh=values[3]（c_slew 网格第 3 点）、tcsr=values[3*7+3]（行=c_slew，列=i_slew）——**模板库 CONSTRAINT 是 (c,i) 顺序**」
9. **msg[294]**（关键实证完成）:
   - 「k 库 mpw 表无 2D 误判（build_lu_templates 用 match_brace 取真实块体，dim=1）」
   - 「k 库 (3,3)：clkh=values[3]（1D，c_slew 网格）、tcsr=values[3×7+3]（**k 库 CONSTRAINT = (i,c) 顺序**）」
   - 「模板库 (3,3)：tcsr=values[3×7+3]（**模板库 CONSTRAINT = (c,i) 顺序**）——同一坐标在两种风格下含义相反」

## 映射关系总结（agent 产出的核心知识）
| table 类型 | coord 子集 | dim | 模板库 var 顺序 | k 库 var 顺序 |
|---|---|---|---|---|
| CONSTRAINT (clkh/tcsr/tchr) | {i_slew, c_slew} | 2D | v1=c_slew, v2=i_slew | v1=i_slew, v2=c_slew |
| CELL_DELAY / TRAN (q-delay) | {q_load} | 1D (index_2) | — | — |
| CLK_TRAN | {c_slew} | 1D | — | v1=c_slew |
| mpw_template_7x0 | {c_slew} | 1D（占位 index_2 → 误判风险） | — | — |

权威网格（cxn4s1p, ns）：i_slews=[0.05..0.35] (7 点), c_slews=[0.01..0.07] (7 点), loads=[0.02..0.14] (7 点)。

## Agent 最终交付（msg[334] 总结）
- `rev_cali.py` (635 行) + `test_rev_cali.py` (9 用例) + README.md + 部署到 `autosim_script/rev_cali_tools/` (19 文件)
- 复用 `lib_timing_tools.extract_timing()` 零改动
- 单测 9/9 + 部署一致性 + UI 对接 (`Scripts.revCaliGenerator`)
- 红线遵守：`1p_timing_stress_link`、`lib_timing_tools`、`SRAMAutoSim` UI 零改动

## 造题 reframe（r697 methodology: analysis-Q&A → produce）
**case_id**: `EDA-Eval-DesignFlow-LibCoordMapper-001`
**形态**: spice_sim characterization · analysis-Q&A→produce · A 档 trace-faithful
**任务**: 写 `lib_coord_mapper.py(workdir, out_dir)` 解析提供的 liberty 文件，产出 `coord_mapping.json`——结构化 (i_slew, c_slew, q_load) ↔ template_table 映射 + 变量顺序检测 + 维度分类 + 占位 index 误判告警。
**判分重点**:
- 变量顺序检测必须 data-driven（读 variable_1/variable_2），不能硬编码 → **hidden B 用相反 var 顺序（k 库风格）**作 cross-input guard
- coord_subset 归类（1D/2D/3D，取哪些坐标）
- q_load 表识别（CELL_DELAY/TRAN）
- mpw_template 占位 index_2 误判告警
- 权威网格提取（i/c/loads 三数组）
- A-leak + B-grounding + 确定性 + 4 假提交
