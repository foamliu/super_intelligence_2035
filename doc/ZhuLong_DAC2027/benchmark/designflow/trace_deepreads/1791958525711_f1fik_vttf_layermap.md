# 深读笔记 — 1791958525711_f1fik (chengleiy / hfeg0plg07, mc=504)

- session: /home/chengleiy/.cline/data/sessions/1791958525711_f1fik/{.json,.messages.json}
- meta: 543 msgs / 80 user turns, cwd /home/chengleiy/testTool/zl, model glm-5.3-flash, status failed (long iterative enhancement session)
- tools: virtuoso 525 + calibre 92 + dbCreateRect 23 + netlist 64 + spectre 33 — layout_virtuoso/physical_verify signal (PDK techfile QA flow)
- domain: physical_verify (PDK techfile / layer.map generation+validation)

## 用户意图（A-档 seed 判定）
- U[0] 逐字原文：「这个路径下是我的全部脚本  请你阅读所有的脚本，理解每个脚本的功能，以及每个脚本之间的关系，路径如下   /home/chengleiy/scripts」 — 脚本理解委托轮，**非 design_flow 交付需求**，不构成 A-档 seed。
- U[41] read the prompt_flow.md and do the job... + 5 个英文报告 — 引用 prompt_flow.md 的复合需求，偏 rscalc flow（near-dup e0014566 ResFlow）。
- U[87] 列 5 条对 genLayermap_definition.py 的验证增强要求（同名同号一致性 / 产物行数==输入有效行数 / round-trip 回读 / 反向孤儿 packet / packet 引用完整性）— **增强/fix 性质**，按 A-档规则 ② 不作 seed。
- 会话整体=脚本理解→测试→增强迭代长 saga，无单一干净「提出需求做 X 交付」轮 → **本 case 取 B 档 synthesized**。

## 金标（人工复核）
- gold = /home/chengleiy/scripts/application/vttf/vttf2/genLayermap_definition.py (7752B / 197 行, Oct 15, VTTF 流水线 layer-table→layer.map 生成器)
- 功能映射 U[87] 要求：
  1. 同名同号一致性（双向）：layer number→name / layer name→number / purpose number→name / purpose name→number 四类 conflict 检测 ✓
  2. 产物行数 == 输入有效行数：round-trip 重读 layer.map 计 written_rows，断言 written_rows==expected 且 valid_rows==written+duplicates ✓
  3. round-trip 回读校验 ✓
  4. skipped（comment/empty/bad-format）+ duplicate（首次保留，余者报告）✓
  5. 输出按 (layerNumber, dataType) 数值排序，N/A 行（3 字段）追加末尾 ✓
  6. 输出 header 注释：#date/#author/#source_file/#source_total_lines(empty)/#source_valid_rows/#skipped_lines/#duplicate_rows/#output_rows + 逐条 skipped/duplicate/conflict 行 + 列头 `#layerName #purposeName #layerNumber #dataType`，格式 `{:<25}{:<25}{:<15}{:<15}` ✓
  7. 终端打印 source/output 统计 + 逐条 SKIPPED/DUPLICATE/CONFLICT，row-count check CONSISTENT，exit 0 / 1 ✓
- 验证：gold 跑真实 lay (1042 行) exit 0 输出 1042 行排序正确；跑合成 lay_B (20 行: 2 注释+1 空+1 bad-format+2 重复+layer conflict 400→METAL3/METAL4+purpose conflict 0→drawing/net & net→0/999+N/A 行) exit 0 输出 14 行，全部冲突/重复/跳过正确报告。

## 资产
- A = inputs/lay_A.tsv（真实 lay，1042 行，chengleiy 真实层表，verbatim 真实附件）+ task_brief.md（交付接口 ≤3 行）+ prompt.txt（合成自然语言场景，真实用户/路径/工具）
- B = hidden/lay_B.tsv（合成层表，结构≠A：不同层名/编号 + 注入 comment/empty/bad-format/duplicate/layer-conflict/purpose-conflict/N/A 行）+ hidden_manifest.json
- reference = check.py (14 条断言 a-n，subprocess 真跑候选脚本 on lay_B + 结构化解析输出/终端校验 + 行序无关性随机化) + reference_submit.zip(gold genLayermap_definition.py) + negative/{naive_hardcode,only_print_expected,empty_shell,ref_deleted_core} + negative_selftest.py

## L 层
- L1（offline Python 复刻）：layer-table→layer.map 是纯文本处理，无需 live EDA 工具；check.py subprocess 真跑候选脚本 on B。physical_verify 域 PDK-techfile 变体补牙（域内 9→10，新增 VTTF/layer.map 主题，与 xinqiaoz PDK QA dummy/DRC deck 主题不同）。
