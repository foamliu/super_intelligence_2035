# Deepread: uks8u — DRC Testpattern Generator (识别+富化+报告前端抽取)

- session: `1790217091100_uks8u` (148 msgs, 9 user turns)
- user/host: lizwen @ hfeg0plg89
- mc=220, tools: pyAether / pythone / aether / drc / techfile
- domain: layout_aether (DRC testpattern generation flow front-end)

## Real user intent
- 整个 session 围绕 `drc_pattern_gen.py`（544 行 pythone 调 pyAether 生成 .oa DRC 测试图形）的调试与零配置移植
- USER#7 给出 3-file fix：把 `test_deck_new` 规则清单 + `drc_rules_spec.json` 规格库 + `derived_layer_map.json` 层映射抽到独立 config 目录，实现"拷目录即可跑"的零配置移植
- 主体流程：解析 `test_deck_new`（按类别分节的规则清单文本）→ 按规则名/通配符筛规则 → 在 `drc_rules_spec.json` 里查每条规则的详细规格（rule_type/layers/region/svrf_raw/parameters/pattern_constraints）→ 调 pyAether 生成 .oa 测试图形

## Real deliverable on .75
- `/home/lizwen/.cline/scripts/data/drc_pattern_gen.py` (544 行)
- `/home/lizwen/.cline/scripts/data/sample_drc_deck/specs/test_deck_new` (49 rules, 4 categories: Width/Spacing/Extension/Enclosure)
- `/home/lizwen/.cline/scripts/data/sample_drc_deck/config/drc_rules_spec.json` (49 rules spec 库)
- `/home/lizwen/.cline/scripts/data/sample_drc_deck/config/derived_layer_map.json` (层映射)

## Case 抽取边界 (EDA-Eval-DesignFlow-DrcPatQueryEnrich-001)
本 case 只抽"识别+富化+报告"前端（不调 pyAether、不生成 .oa），因为 SUT 沙盒里没有 live Aether bridge。这样既保留了真实 trace 的核心解析逻辑（fnmatch 大小写不敏感筛规则 + 按 rule_id 在 spec 里查规格 + JSON 报告），又让 case 可在纯 stdlib 环境下被 cline 端到端跑通。

- 可见 A: `test_deck_new_A`（49 rules, 4 categories）+ `drc_rules_spec.json`，query `M1_S*` → 8 命中（全在 Spacing 类）
- 隐藏 B: `test_deck_new_B`（18 rules，类别重排 Enclosure/Width/Spacing，移除 M1_S/NCH/PC_S 系）+ 同一份 spec，query `DNW*` → 9 命中（DNW_ENC_009_00_c/p, DNW_ENC_011_00_c/p, DNW_W_000_00, DNW_W_007_00, DNW_S_001/002/003_00），与 A 的 M1_S* 集合不相交 → cross-input guard 防硬编码

## Gold SUT (drc_pat_query_enrich.py, 169 行, sha256 218fd0d4b6)
核心函数：
- `parse_test_deck(path)` — 逐行解析：类别标题行更新当前类别；列头行 `规则名` 跳过；规则数据行 `RULE_ID: description` 记录 {rule_id, category, description}
- `build_spec_index(spec_path)` — 加载 drc_rules_spec.json，按 rule_id 大写建索引
- `match_and_enrich(deck_rules, spec_index, queries)` — fnmatch 大小写不敏感匹配（rule_id 与 query 都转大写），命中规则去 spec 查规格富化，deck 有 spec 没的规则打 WARNING 且不计入命中，多 query 并集去重
- CLI: `--deck/--spec/--query(可多个)/--out/--list`；`--list` 模式按类别分组列出全部规则 + `Total: <N> rules`；无命中时非 0 退出

## check.py 14 条独立断言 (a-n)
- a: zip 合法 + 恰含 drc_pat_query_enrich.py
- b: py_compile 通过
- c: AST 用 argparse + 暴露 --deck/--spec/--query/--out/--list
- d: AST 定义 parse_test_deck + build_spec_index + match_and_enrich (≥3 核心函数，反空壳)
- e: SUT 跑 B (DNW*) 退出 0 + 写出报告文件
- f: B 报告 JSON 含 5 顶层键 query/deck_total/matched_count/categories_present/matched_rules
- g: B deck_total == 18
- h: B matched_count == 9 且 == len(matched_rules)
- i: B matched_ids == 9 条 DNW 期望集 (cross-input guard vs A)
- j: 每条 matched rule 含全部 10 必需字段
- k: B categories_present == [包围类规则 (Enclosure), 宽度类规则 (Width), 间距类规则 (Spacing)] (B 类别序 ≠ A 单一 Spacing)
- l: 9 条 B matched rules 全 has_pattern_constraints == True
- m: --list 模式跑 B 退出 0 + stdout 含 "Total: 18 rules"
- n: cross-input guard: 跑 A (M1_S*) matched_count == 8 且 ids 全 M1_S* 前缀且与 B 的 DNW* 不相交 (防 B 硬编码)

## Negatives (4 个, NEG_RC=0, distinct labels {c,d,e,h})
- empty_shell.py → FAIL [c] (无 argparse 选项)
- print_expected.py → FAIL [d] (无核心函数)
- core_deleted.py → FAIL [e] (B 跑不出报告)
- hardcode_a.py → FAIL [h] (硬编码 A 的 8 条，B 跑出 8 ≠ 9)

## 选案理由
- lizwen 在 4 shard 里仅 5 prior cases (未过度使用)
- uks8u 对 4 shard 全新鲜 (mc=220 但从未被任何 shard 用过)
- domain=layout_aether，但抽出的前端本质是 physical_verify (DRC 规则解析+富化)，归 C shard physical_verify 域，补 C shard 最弱的 pg_layout 之外的真实 DRC 覆盖
- L1 纯 stdlib，SUT 沙盒可端到端跑通（无 pyAether/.oa 依赖）
