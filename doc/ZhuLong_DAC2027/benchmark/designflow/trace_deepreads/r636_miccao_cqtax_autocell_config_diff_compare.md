# r636 deepread — miccao @ hfeg0plg37, session 1789697772892_cqtax (mc36, physical_verify)

## trace 来源
- user: miccao, host: hfeg0plg37 (IP 10.129.32.47), session: 1789697772892_cqtax.messages.json (subdir layout)
- mc=36, keywords: schematic:60; drc:58; lvs:50; .gds:48; netlist:22; calibre:20
- 选取：`_fresh_mc10_C_r626.tsv` mc 30-55 段 unpeeked 非-known-cluster 筛，r636 第 4 peek 命中
- miccao 为已知 C 作者（r624 9pcjd AutoCellParamSecurityAudit / r628 yavow reject / r630 j2was LvsHcellFailReportExtract），cqtax 与既有 case distinct（config-diff vs security-audit / report-extract）

## 真实用户意图（逐字）
U#1 原话：「/home/miccao/autocell.1.2026.7/g5_ddcpc和/home/miccao/autocell.1.2026.7/g5_decoa里面的配置文件有什么差异，我要你把所有tcl里每一个参数都比一遍」
- 单轮、干净 produce-task（无 debug/无 handoff/无 skill-orch）
- 交付形态：两目录所有 TCL 配置文件的逐参数差异比对报告
- miccao 维护 AutoCell (Primarius std cell compiler) 的两套 G5 工艺配置（g5_ddcpc 与 g5_decoa），想确认两者参数是否一致

## assistant 工具链与 gold
- 工具：list_allowed_files（两目录 + configuration/layout_gen/layout_spec/pcell 子目录）+ read_files（逐批读 TCL 对比）。run_commands 被 sandbox 禁用。
- gold 结论（ASST 末尾结构化 markdown 报告）：**两目录所有 33 个 TCL 配置文件完全一致，无任何参数差异**。分 5 个目录层级列表（根 tech.tcl 1319 行 / configuration 10 文件 / layout_spec / layout_gen / pcell），每文件标 ✅ 完全一致。
- 关键：gold = "all identical"。但真实工具需能检测差异（若两目录确有不同）——故 case 用隐藏 B/B2 注入不相交参数差异，迫使 SUT 工具真解析 set 参数而非总答 identical。

## case 合成（B档 mock-behavioral config-diff-tool reframe）
- deliverable = `autocell_config_diff.py <dir_a> <dir_b> <output.json>`：递归遍历两目录 .tcl → 解析 `set <name> <value>` 参数（跳过 # 注释）→ 逐文件逐参数比对 → 结构化 JSON {files_compared/identical_files/different_files/differences/verdict/total_files/total_diffs}，缺失文件/缺失参数用 __missing__ 标记，sort_keys 确定性输出
- asset A = `dir_a_a/` + `dir_b_a/`（6 tcl 文件，全部一致，mirrors trace gold；tech/common/boundary/vias/grid/pin 各 3-4 set 参数）
- 隐藏 B = `dir_a_b/` vs `dir_b_b/`（tech.tcl MINW 0.12→0.15 + SPACING 0.18→0.20，boundary.tcl PITCH 0.40→0.44；3 diffs / 2 files；4 identical）
- 隐藏 B2 = `dir_a_b2/` vs `dir_b_b2/`（common.tcl LAYER M1→M2，grid.tcl XPITCH 0.50→0.55；2 diffs / 2 files，与 B 不相交 → 反硬编；tech.tcl 参数级一致）
- 隐藏 A = `dir_a_a/` vs `dir_b_a/`（全一致，断言 verdict==identical 反 always-different）
- 19 条 a-s：结构2(a:zip含py / b:py_compile) + B运行1(c) + schema1(d:7键) + B判定3(e:verdict different / f:total_files 6 / g:total_diffs 3) + B文件集2(h:different{tech,boundary} / i:identical{common,vias,grid,pin}) + B参数grounding3(j:tech MINW / k:tech SPACING / l:boundary PITCH) + A守卫2(m:verdict identical / n:total_diffs 0) + B2反硬编4(o:verdict different / p:total_diffs 2 / q:different{common,grid}与B不相交 / r:common LAYER) + 确定性1(s:重跑字节一致)
- 自验：ref 19/19 PASS ✓；3 neg(naive_empty/print_expected_A/deleted_core)全FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓；§4.9(a)(b)(c)三假全FAIL ✓；embedded test==disk check.py byte-equal ✓；bool(check)=True ✓；k_rationale==k_check==19≥8 ✓
- C.jsonl 395→396；mark case ✓（pv 174→175, ledger_C case 396→397, covered 396→397/943=42.1%）
- same_trace_group `cqtax-autocell-config-diff-compare`（cap-1）；与 r624 AutoCellParamSecurityAudit distinct：输入=两配置目录 vs DRAM示例+TECHLIB；输出=diff 报告 vs leakage 安全报告；判定=差异列表 vs 泄露计数

## 意义
- 新标准下 config-diff Q&A（「两个目录配置有什么差异，每个参数比一遍」）经 config-diff-tool reframe 可造出有牙 case——deliverable 不是"读文件回答"而是"产出递归比对+参数解析+结构化差异报告的通用工具"
- fresh-pool mid-mc(30-55) 段经 reframe 仍可造有牙 case（承 r625/r627/r631-r635 连续命中）；cqtax 是 miccao 已知作者的新 session（非已知 cluster 重复），证明已知作者的 fresh session 仍有 distinct produce-task
- 与 r624 AutoCellParamSecurityAudit 互补：同 AutoCell 配置域，r624 检"泄露"(值相等=unsafe)，r636 检"差异"(值不等=different)，正反两面覆盖 AutoCell 配置比对任务族
